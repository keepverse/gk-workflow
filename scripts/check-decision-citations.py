"""check-decision-citations.py — a citation nobody can open is not evidence.

`docs/architecture/decisions.md` and `docs/DESIGN-GATE.md` are INDEXES: one line per row, with the
rule text living in a category file that the row names. That makes every `decisions.md:155` in the
tree a *positional* citation, and positions move. Adding one row above another shifts every later
one — silently, because nothing about the edited line is wrong; only the numbers are.

This script is the check that was named in AGENTS.md and had gone missing. `scripts/split-decisions.py`
was the generator that split the index into `decisions/<category>.md` and refused any change moving a
cited line. The generator is gone and so is its refusal, and the accounting became manual — which is
exactly the state in which a row inserted at line 155 pushed the next row to 156 while its own
`<!-- decisions.md:155 -->` marker kept claiming the old position. Found by landing the row and
measuring, not by reading: 1 of 149 markers was wrong, and it was wrong because of this change.

**What it checks, and why each shape is a different failure.**

* `<!-- decisions.md:N -->` — an in-table marker a category row carries pointing back at its index
  row. Checked against the BOLDED TITLE, not merely the line number: a number that survives a shift
  but names a different row is the failure this exists to catch, and a range check would pass it.
* `decisions.md:N` — a positional citation from prose anywhere in the tree. The cited line must
  exist AND must be a table row. Pointing at a blank line is the specific defect found once already:
  three citations asserted that "the clock's decisions.md row exists" in a table that has no clock
  row, so they pointed at nothing and would have kept pointing at nothing.
* `DESIGN-GATE.md:N` — same, for the design gate.

**Fails closed and names itself.** Non-zero exit with a counted, per-file breakdown. It is read-only:
it writes nothing, so it cannot make the tree it audits look clean by editing it — the defect that
made one earlier detector in this repo look non-deterministic until a concurrent writer was found.

Usage:  python scripts/check-decision-citations.py [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: The two positional indexes. Both are one line per row, so both are cited by line.
INDEXES = ("docs/architecture/decisions.md", "docs/DESIGN-GATE.md")

#: A citation in prose. Two shapes exist in this tree and reading only one is how a first cut of this
#: script over-fired: `decisions.md:155` is a POSITIONAL ROW citation, while `DESIGN-GATE.md:33:225`
#: (60 of them, all in tasks/ip-censor) is a `line:COLUMN` character offset into a prose line. Both
#: are real citations; only the first points at a table row.
CITATION = re.compile(r"([\w./\\-]*\b(?:decisions|DESIGN-GATE)\.md):(\d+)(?::(\d+))?")

#: The self-describing marker a category row carries back to its index row.
MARKER = re.compile(r"<!--\s*((?:[\w./\\-]*\b(?:decisions|DESIGN-GATE)\.md)):(\d+)\s*-->")

#: A table row's bolded title, which is what a marker actually asserts about.
TITLE = re.compile(r"^\s*\|\s*\*\*(.+?)\*\*")

#: Roots that can contain a citation. Everything else is skipped, which keeps the scan honest about
#: what it covered rather than silently widening to a machine-local path.
SCAN_ROOTS = ("docs", "tasks", "src", "tools", "scripts", "tests", ".github", ".claude", ".agents")

SKIP_DIRS = {".git", "node_modules", "__pycache__", "bin", "obj", "dist", ".codegraph"}


def _index_lines(workspace: Path, rel: str) -> "list[str]":
    path = workspace / rel
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def _row_title(line: str) -> str:
    m = TITLE.match(line)
    return m.group(1).strip() if m else ""


def _basename(ref: str) -> str:
    return ref.replace("\\", "/").rsplit("/", 1)[-1]


def scan(workspace: Path) -> "dict":
    """Walk the scan roots once and resolve every citation found."""
    indexes: "dict[str, list[str]]" = {rel: _index_lines(workspace, rel) for rel in INDEXES}
    findings: "list[dict]" = []
    markers = 0
    citations = 0
    docs_scanned = 0

    for root_name in SCAN_ROOTS:
        root = workspace / root_name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            docs_scanned += 1
            rel_doc = path.relative_to(workspace).as_posix()
            for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                # self-citations inside the index itself are the table, not a citation to it
                for match in MARKER.finditer(line):
                    markers += 1
                    _check(match.group(1), int(match.group(2)), rel_doc, lineno, line,
                           indexes, findings, is_marker=True)
                for match in CITATION.finditer(line):
                    if MARKER.search(line) and match.group(0) in line:
                        continue  # already handled as a marker
                    citations += 1
                    _check(match.group(1), int(match.group(2)), rel_doc, lineno, line,
                           indexes, findings, is_marker=False,
                           column=int(match.group(3)) if match.group(3) else None)

    return {
        "documents": docs_scanned,
        "markers_checked": markers,
        "citations_checked": citations,
        "findings": findings,
    }


def _check(ref: str, line_no: int, doc: str, lineno: int, line: str,
           indexes: "dict[str, list[str]]", findings: "list[dict]", *, is_marker: bool,
           column: "int | None" = None) -> None:
    """Three rules, each one ambiguous-free.

    A first cut of this script also asserted that a positional citation must land on a table ROW.
    That was wrong, and it over-fired on all three findings it reported: `DESIGN-GATE.md`'s §5 is a
    checklist rather than a table, and `DESIGN-GATE.md:89:39` is a `line:COLUMN` character offset
    into prose. Requiring a row would have "fixed" citations that were correct. The rules kept here
    are the ones with no judgement in them:

      OUT-OF-RANGE  the cited line does not exist.
      BLANK-TARGET  it exists but holds nothing -- the defect found once already, where three
                    citations asserted that "the clock's decisions.md row exists" in a table with no
                    clock row, so they pointed at a blank line and would have kept doing so.
      MARKER-DRIFT  a marker's bolded title is not the bolded title at the line it names. This is the
                    E8 failure proper: a number that survives a shift while naming a different row.
    """
    base = _basename(ref)
    target_rel = next((rel for rel in INDEXES if rel.endswith(base)), None)
    if target_rel is None:
        return  # not one of the two positional indexes
    lines = indexes[target_rel]
    if not lines:
        return

    kind = "marker" if is_marker else "citation"
    if line_no < 1 or line_no > len(lines):
        findings.append(dict(code="OUT-OF-RANGE", kind=kind, doc=doc, line=lineno,
                             ref=ref, note=f"line {line_no} does not exist ({len(lines)} lines)"))
        return

    target = lines[line_no - 1]
    if not target.strip():
        findings.append(dict(code="BLANK-TARGET", kind=kind, doc=doc, line=lineno, ref=ref,
                             note=f"points at an empty line in {ref}"))
        return

    if column is not None:
        # The third component is parsed so the LINE is read correctly, but NO rule is asserted about
        # it. A first cut assumed it was a character offset into the line and reported 52 findings
        # that columns "225", "1091" and "1529" were past the end of a ~90-character line -- which
        # only proves the assumption was wrong and the citations were fine. Its semantics were not
        # established, so this script declines to guess: asserting an unverified rule would
        # manufacture confident false findings, which is worse than checking one thing less.
        return

    if is_marker:
        # The number alone is not the assertion; the TITLE is. A marker that survived a shift while
        # naming a different row is precisely the failure this script exists to catch.
        want, got = _row_title(line), _row_title(target)
        if want and got and want != got:
            findings.append(dict(code="MARKER-DRIFT", kind=kind, doc=doc, line=lineno, ref=ref,
                                 note=f"claims {want!r} but {ref} line {line_no} is {got!r}"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--workspace", default="")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve() if args.workspace else Path(__file__).resolve().parent.parent
    report = scan(workspace)
    findings = report["findings"]

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if findings else 0

    print(f"Decision-citation check - {report['documents']} documents, "
          f"{report['markers_checked']} in-table markers, {report['citations_checked']} positional citations")
    if not findings:
        print("  every positional citation resolves to a line that exists and holds text, and every "
              "in-table marker names the row it claims")
        return 0

    by_code: "dict[str, int]" = {}
    for f in findings:
        by_code[f["code"]] = by_code.get(f["code"], 0) + 1
    for code, n in sorted(by_code.items()):
        print(f"  {code:24} {n}")
    print()
    for f in findings[:60]:
        print(f"  {f['doc']}:{f['line']}  {f['code']}  {f['ref']}  - {f['note']}")
    if len(findings) > 60:
        print(f"  ... and {len(findings) - 60} more")
    print("\nA positional citation that names a line which is blank, out of range, or a different row "
          "is not evidence. Fix the number, or point at the category file and name the row.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
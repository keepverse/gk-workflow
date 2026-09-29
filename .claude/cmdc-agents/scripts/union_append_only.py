#!/usr/bin/env python3
"""Union two sides of a conflicted APPEND-ONLY file (ledgers, task lists, jsonl).

Append-only files conflict on every merge because two lanes each appended rows. The rule that has held
every time: keep BOTH sides, dedup identical lines, and for jsonl re-sort by `ts` so the ledger reads in
time order. This is that rule, once, in code -- instead of hand-resolving the same five files at every
merge and hoping the ledger's integrity check still passes.

It never guesses, and it fails CLOSED on anything it cannot handle (added 2026-09-26):

  * A line union is only correct when a LINE is the unit of meaning. Handed a block-structured file it
    is not merely lossy, it is destructive: the dedup collapses the repeated structural lines (`{`,
    `},`, `],`), so every comma and brace position moves. Measured on the actor-hud merge: two
    182 KB sides of `gk-core/scripts/verification-boundaries.v1.json` produced a 96 KB output that is not
    valid JSON, and the tool exited 0. A resolver that reports success while destroying a verification
    registry is worse than no resolver, because the next agent trusts it. So the shape is decided
    BEFORE anything is written, and a shape this tool does not own is refused by name.
  * The output is written to a sibling staged file, re-read and re-validated THERE, and only then
    `os.replace`d onto the destination. A refusal therefore leaves the destination byte-identical --
    the difference between "a corrupt file sitting in the tree, reported as success" and a refusal.

Refusals (all non-zero, all named, all on stderr; `--json` puts the same refusal in the envelope):

  exit 1  INPUT-UNREADABLE         an input could not be read
  exit 1  INPUT-ROW-NOT-JSON       a `.jsonl` line is not JSON (pre-existing refusal, message kept)
  exit 2  INPUT-SHAPE-UNSUPPORTED  the input is a block-structured format, not an append-only ledger
  exit 3  OUTPUT-ROUNDTRIP-FAILED  the written file did not survive the re-read; destination untouched
  exit 4  OUTPUT-UNWRITABLE        the staged file could not be created or moved onto the destination
  exit 4  OUTPUT-STAGED-LEFT-BEHIND a refusal happened and the staged file could not be removed

Shape vocabulary (closed; the code owns it and a human widens it):

  lines      markdown / text / log -- a line is the unit of meaning. THIS TOOL'S CLASS.
  jsonl      `.jsonl` / `.ndjson` -- one record per line, merged, and re-sorted by `ts`.
  structured anything whose meaning depends on structure rather than lines. REFUSED.

  Refused by DECLARED SUFFIX: .json .yaml .yml .toml .xml .ini .cfg .conf
  Refused by CONTENT: the text parses as ONE json document. The two signals are independent and either
  alone is enough, because the only caller (the now-RETIRED `resolve-append-only.ps1:38-39`) renames both sides to
  `ours.txt` / `theirs.txt` while `--out` keeps the real name -- a suffix rule alone would miss a
  registry merged to a `.txt`, and a content rule alone would miss a mislabelled file. The content
  probe runs on each conflict-free REGION as well as on the whole file, so a conflicted working file
  (two documents separated by `=======`) is recognised as the two documents it is; the
  marker-stripped whole text of such a file parses as nothing at all.

Deliberately NOT refused, with the reason:

  * `.csv` / `.tsv` -- a row-per-line table is a legitimate line union, so refusing it would block a
    valid use. The one hazard is real and is NOT caught here: a quoted field containing a newline
    makes a record span physical lines, and the dedup can then drop a line that repeats. This tool
    has never been handed such a file; if one shows up, the honest fix is a csv-aware reader, not a
    suffix ban that would also block the well-formed case.
  * `.jsonl` whose rows lack `ts` -- still merged, still exit 0, still reported `sorted_by_ts=False`.
    That is the pre-existing contract and it is unchanged; the only addition is the row count in the
    NOTE line, so an operator can see WHY the sort was skipped.
  * a one-line file whose content parses as a json document, under a name that is not `.jsonl` -- it
    IS refused. A minified structured file is the likelier reading, and a one-line append-only ledger
    cannot conflict in the first place (there is nothing to append). The message names the reason.

There is no `--allow-structured`. An override is how the destructive path gets reopened by the next
agent in a hurry; a named refusal with a named remedy is the cheaper answer.

usage: python union_append_only.py --ours <side2> --theirs <side3> --out <path> [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from typing import Callable, Sequence

SCHEMA = "union-append-only/2"
TOOL = "union_append_only.py"

EXIT_OK = 0
EXIT_INPUT_UNREADABLE = 1
EXIT_INPUT_SHAPE = 2
EXIT_ROUNDTRIP = 3
EXIT_OUTPUT = 4

#: One record per line. Merged, and re-sorted by `ts`.
JSONL_SUFFIXES = frozenset({".jsonl", ".ndjson"})

#: Block-structured: a line is not the unit of meaning, so a line union rewrites structure instead of
#: appending to it. `.json` is MEASURED (2026-09-26, the 182 KB -> 96 KB incident); the rest are the
#: same class by construction and are refused on the declared suffix with the same remedy.
STRUCTURED_SUFFIXES = frozenset({".json", ".yaml", ".yml", ".toml", ".xml", ".ini", ".cfg", ".conf"})

#: What to run instead. A pointer, not an implementation: boundary-union logic already exists in the
#: manager plane under two DIFFERENT rules, so choosing one here would be a second thing to keep in
#: sync -- and a second JSON merge implementation is the drift risk this refusal exists to avoid.
ADVICE_JSON_REGISTRY = (
    "for a verification-boundaries registry: python .claude/cmdc-agents/scripts/union-registry-sides.py "
    "--ours <side2> --theirs <side3> --out <path>   (ours wins; differences are reported and exit 3 "
    "is how you say you read them)"
)
ADVICE_MISLABELLED = (
    "if this really is a JSONL ledger its name is lying -- use a .jsonl path. If it really is a "
    "structured document, run the boundary-union tool above."
)


class Refusal(Exception):
    """A named, non-zero refusal. `name` is the machine key; `detail` says what was seen."""

    def __init__(self, name: str, detail: str, exit_code: int) -> None:
        super().__init__(f"{name}: {detail}")
        self.name = name
        self.detail = detail
        self.exit_code = exit_code


def read_text(path: str, *, role: str = "input") -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        raise Refusal("INPUT-UNREADABLE", f"{role} {path}: {exc}", EXIT_INPUT_UNREADABLE) from exc
    except UnicodeDecodeError as exc:
        raise Refusal("INPUT-UNREADABLE", f"{role} {path}: not utf-8 ({exc})", EXIT_INPUT_UNREADABLE) from exc


def split_lines(raw: str) -> list[str]:
    """The one line model this tool has. Unchanged since 2026-09-21 -- append-only parity depends on
    it, down to dropping blank lines and stripping a conflict marker wherever it appears."""
    out = []
    for line in raw.split("\n"):
        s = line.rstrip("\r")
        if not s.strip():
            continue
        if is_conflict_marker(s):
            continue  # a marker must never reach the result
        out.append(s)
    return out


def is_conflict_marker(line: str) -> bool:
    return line.lstrip().startswith(("<<<<<<<", "=======", ">>>>>>>"))


def marker_regions(raw: str) -> list[str]:
    """The maximal marker-free blocks of a file, in order.

    A conflicted working file is `<<<<<<< ours ... ======= ... >>>>>>> theirs`, so its
    marker-stripped WHOLE text is two documents concatenated -- which parses as nothing. Probing each
    region separately is what lets the shape gate see through a conflicted registry instead of only
    through a clean side. With no markers this yields exactly one region: the whole file.
    """
    regions, current = [], []
    for line in raw.split("\n"):
        if is_conflict_marker(line.rstrip("\r")):
            if current:
                regions.append("\n".join(current))
                current = []
            continue
        current.append(line)
    if current:
        regions.append("\n".join(current))
    return regions


def parses_as_document(lines: Sequence[str]) -> bool:
    """True when the text is ONE json document, i.e. structure carries the meaning.

    The first-character prefilter is exact, not a heuristic: a json document begins with `{` or `[`
    after whitespace, so the parse is only reached by text that could plausibly be one -- which keeps
    a 1.2 MB markdown ledger off the expensive path entirely.
    """
    if not lines:
        return False
    head = lines[0].lstrip()
    if not head or head[0] not in "{[":
        return False
    try:
        json.loads("\n".join(lines))
    except ValueError:
        return False
    return True


def document_shaped(raw: str, lines: Sequence[str]) -> bool:
    """Document-shaped if the file is one document, OR if any conflict region inside it is one."""
    if parses_as_document(lines):
        return True
    return any(parses_as_document(split_lines(region)) for region in marker_regions(raw))


@dataclass(frozen=True)
class Shape:
    """What one file IS, as far as this tool is concerned. Reported on every run, pass or fail."""

    role: str
    path: str
    suffix: str
    kind: str
    reason: str
    lines: int
    markers: int
    document: bool

    def as_dict(self) -> dict:
        return {
            "role": self.role,
            "path": self.path,
            "suffix": self.suffix,
            "shape": self.kind,
            "reason": self.reason,
            "lines": self.lines,
            "conflictMarkers": self.markers,
            "parsesAsJsonDocument": self.document,
        }

    def describe(self) -> str:
        return f"shape={self.kind} ({self.reason})"

    @classmethod
    def from_dict(cls, d: dict) -> "Shape":
        return cls(d["role"], d["path"], d["suffix"], d["shape"], d["reason"], d["lines"],
                   d["conflictMarkers"], d["parsesAsJsonDocument"])


def classify(role: str, path: str, raw: str) -> Shape:
    lines = split_lines(raw)
    markers = sum(1 for line in raw.split("\n") if is_conflict_marker(line.rstrip("\r")))
    suffix = os.path.splitext(path)[1].lower()
    document = document_shaped(raw, lines)

    if suffix in JSONL_SUFFIXES:
        kind, reason = "jsonl", f"declared suffix {suffix!r} is one record per line"
    elif suffix in STRUCTURED_SUFFIXES:
        kind, reason = "structured", f"declared suffix {suffix!r} is block-structured, not append-only text"
    elif document:
        kind, reason = "structured", f"content parses as ONE json document over {len(lines)} lines"
    else:
        kind, reason = "lines", "a line is the unit of meaning (append-only text)"

    return Shape(role, path, suffix, kind, reason, len(lines), markers, document)


def refuse_unsupported(shapes: Sequence[Shape]) -> None:
    """The measured defect, made unreachable: nothing is written when the shape is not ours."""
    offenders = [s for s in shapes if s.kind == "structured"]
    if not offenders:
        return
    detail = "; ".join(f"{s.role} {s.path}: {s.reason}" for s in offenders)
    raise Refusal(
        "INPUT-SHAPE-UNSUPPORTED",
        f"{detail} -- a line union rewrites structure instead of appending to it, and the dedup drops "
        f"the repeated structural lines, which is how a registry becomes invalid JSON with exit 0",
        EXIT_INPUT_SHAPE,
    )


def union(ours: Sequence[str], theirs: Sequence[str]) -> tuple[list[str], int]:
    """ours in order, then the lines only theirs has. Unchanged since 2026-09-21."""
    seen, result = set(), []
    for line in ours:
        if line not in seen:
            seen.add(line)
            result.append(line)
    theirs_only = 0
    for line in theirs:
        if line not in seen:
            seen.add(line)
            result.append(line)
            theirs_only += 1
    return result, theirs_only


def sort_jsonl_by_ts(result: Sequence[str]) -> tuple[list[str], bool, int]:
    """Re-sort a jsonl union by `ts`. Unchanged since 2026-09-21, including the soft case: a row that
    is not an object, or carries no `ts`, skips the sort rather than refusing. Such rows are counted
    and reported so the shape is legible instead of merely absent from the summary."""
    rows, sortable, unsortable = [], True, 0
    for line in result:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Refusal("INPUT-ROW-NOT-JSON", f"not json ({exc}): {line[:120]}", EXIT_INPUT_UNREADABLE)
        if not isinstance(obj, dict) or "ts" not in obj:
            sortable = False
            unsortable += 1
            continue
        rows.append((str(obj["ts"]), line))
    if not sortable:
        return list(result), False, unsortable
    rows.sort(key=lambda r: r[0])
    return [r[1] for r in rows], True, 0


def verify_round_trip(staged: str, expected: Sequence[str], jsonl: bool) -> None:
    """Refuse a file that did not survive the trip to disk and back. Runs on the STAGED file, so a
    refusal here never reaches the destination."""
    try:
        reread = split_lines(read_text(staged, role="staged output"))
    except Refusal as refusal:
        raise Refusal("OUTPUT-ROUNDTRIP-FAILED", refusal.detail, EXIT_ROUNDTRIP) from refusal

    if reread != list(expected):
        detail = f"wrote {len(expected)} lines, read back {len(reread)}"
        if sorted(reread) == sorted(expected):
            detail += " (the same lines in a different order -- the file on disk is NOT the union built)"
        raise Refusal("OUTPUT-ROUNDTRIP-FAILED", detail, EXIT_ROUNDTRIP)

    if jsonl:
        for line in reread:
            try:
                json.loads(line)
            except ValueError as exc:
                raise Refusal(
                    "OUTPUT-ROUNDTRIP-FAILED",
                    f"a written .jsonl row does not parse ({exc}): {line[:120]}",
                    EXIT_ROUNDTRIP,
                ) from exc


def atomic_write_validated(dest: str, text: str, validator: Callable[[str], None]) -> str:
    """Write `text` beside `dest`, validate it there, then replace `dest` with it.

    The destination is only ever touched by an `os.replace` of an already-validated file, so a refusal
    cannot leave a corrupt file behind. A cleanup that fails is itself a refusal, never a swallowed
    delete (docs/contributing/testing-standard.md R3).
    """
    directory = os.path.dirname(os.path.abspath(dest)) or "."
    staged = None
    try:
        try:
            handle, staged = tempfile.mkstemp(
                prefix=os.path.basename(dest) + ".staged-", suffix=".tmp", dir=directory
            )
        except OSError as exc:
            raise Refusal("OUTPUT-UNWRITABLE", f"{dest}: {exc}", EXIT_OUTPUT) from exc
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        except OSError as exc:
            raise Refusal("OUTPUT-UNWRITABLE", f"{staged}: {exc}", EXIT_OUTPUT) from exc
        validator(staged)
        try:
            os.replace(staged, dest)
        except OSError as exc:
            raise Refusal("OUTPUT-UNWRITABLE", f"{dest}: {exc}", EXIT_OUTPUT) from exc
        staged = None
        return dest
    finally:
        if staged is not None and os.path.exists(staged):
            try:
                os.unlink(staged)
            except OSError as exc:
                raise Refusal(
                    "OUTPUT-STAGED-LEFT-BEHIND",
                    f"a refusal happened and the staged file could not be removed: {staged} ({exc})",
                    EXIT_OUTPUT,
                ) from exc


def build_parser() -> argparse.ArgumentParser:
    """The CLI vocabulary, in one place, so a test can assert which options EXIST rather than grep
    the source for a string. There is deliberately no way to force a structured merge through."""
    ap = argparse.ArgumentParser(description="Union two sides of a conflicted append-only file.")
    ap.add_argument("--ours", required=True, help="merge side 2")
    ap.add_argument("--theirs", required=True, help="merge side 3")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="machine-readable envelope on stdout (the human summary moves to stderr)")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    a = build_parser().parse_args(argv)

    envelope: dict = {
        "schema": SCHEMA, "tool": TOOL, "ok": False, "stage": "read-input", "refusal": None,
        "inputs": {}, "out": None,
        "counts": {"ours": 0, "theirs": 0, "theirsOnly": 0, "result": 0},
        "sortedByTs": False, "rowsWithoutTs": 0, "exitCode": EXIT_OK,
    }
    # With --json the envelope owns stdout, so a caller parsing stdout never has to skip prose.
    human = sys.stderr if a.as_json else sys.stdout

    def emit() -> None:
        if a.as_json:
            print(json.dumps(envelope, indent=2))

    try:
        ours_raw, theirs_raw = read_text(a.ours, role="ours"), read_text(a.theirs, role="theirs")
        ours_shape, theirs_shape = classify("ours", a.ours, ours_raw), classify("theirs", a.theirs, theirs_raw)
        # The destination's NAME is a signal in its own right: the retired resolve-append-only.ps1
# passed --out as
        # the real repo-relative path, so a registry merge is refused before a byte is built.
        out_name = Shape("out", a.out, os.path.splitext(a.out)[1].lower(), "pending",
                         "not built yet", 0, 0, False)
        envelope["inputs"] = {"ours": ours_shape.as_dict(), "theirs": theirs_shape.as_dict(),
                              "out": out_name.as_dict()}
        envelope["stage"] = "classify-input"
        refuse_unsupported([ours_shape, theirs_shape, out_name])

        envelope["stage"] = "merge"
        ours, theirs = split_lines(ours_raw), split_lines(theirs_raw)
        result, theirs_only = union(ours, theirs)
        envelope["counts"] = {"ours": len(ours), "theirs": len(theirs), "theirsOnly": theirs_only,
                              "result": len(result)}
        sorted_by_ts, unsortable = False, 0
        if a.out.endswith(".jsonl"):
            result, sorted_by_ts, unsortable = sort_jsonl_by_ts(result)
        envelope["sortedByTs"], envelope["rowsWithoutTs"] = sorted_by_ts, unsortable

        envelope["stage"] = "verify-output"
        document = parses_as_document(result)
        built = Shape("out", a.out, out_name.suffix,
                      "structured" if document else ("jsonl" if a.out.endswith(".jsonl") else "lines"),
                      "the union this tool built", len(result), 0, document)
        envelope["inputs"]["out"] = built.as_dict()
        # Defence in depth behind the input refusal: if a built union ever came out as a document, the
        # union was wrong even though both sides looked like text.
        refuse_unsupported([built])

        atomic_write_validated(
            a.out, "\n".join(result) + "\n",
            lambda staged: verify_round_trip(staged, result, a.out.endswith(".jsonl")),
        )

        written = read_text(a.out, role="written output")
        payload = written.encode("utf-8")
        envelope.update(ok=True, stage="done", exitCode=EXIT_OK,
                        out={"path": a.out, "bytes": len(payload), "lines": len(result),
                             "sha256": hashlib.sha256(payload).hexdigest(), "shape": built.kind})
        emit()
        print(f"{a.out}: ours={len(ours)} theirs={len(theirs)} theirs_only={theirs_only} "
              f"result={len(result)} sorted_by_ts={sorted_by_ts} shape={built.kind} roundtrip=ok",
              file=human)
        if unsortable:
            print(f"  NOTE: {unsortable} row(s) carry no 'ts' -- the union is written UNSORTED", file=human)
        return EXIT_OK

    except Refusal as refusal:
        envelope["ok"], envelope["exitCode"] = False, refusal.exit_code
        envelope["refusal"] = {"name": refusal.name, "detail": refusal.detail, "exitCode": refusal.exit_code}
        emit()
        print(f"UNION-APPEND-ONLY REFUSED [{envelope['stage']}] {refusal.name}: {refusal.detail}",
              file=sys.stderr)
        if refusal.name == "INPUT-SHAPE-UNSUPPORTED":
            offenders = [Shape.from_dict(s) for s in envelope["inputs"].values()
                         if s.get("shape") == "structured"]
            for shape in offenders:
                print(f"  {shape.role:<6} {shape.path}", file=sys.stderr)
                print(f"         {shape.describe()} lines={shape.lines} conflictMarkers={shape.markers}",
                      file=sys.stderr)
            print("  nothing written; the destination is untouched.", file=sys.stderr)
            print("  " + (ADVICE_JSON_REGISTRY if offenders[0].suffix == ".json" else ADVICE_MISLABELLED),
                  file=sys.stderr)
        return refusal.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

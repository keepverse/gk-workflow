#!/usr/bin/env python3
"""convergence-census -- the measurement behind goal mud0d8iv-rxh38v task `t1-convergence`.

Contract (verbatim):

    Per-program open task-block counts (headings + block rows, checkpoints excluded)
    driven to zero with evidence.

This file exists because two hand-run sweeps of the same tree produced two different
numbers (64/257/742 and 79/339/2067). A contract measured by a script that lives in a
shell history is not a contract: nobody reading the completion claim can reproduce it.
So the definition lives here, is executable, and prints both what it counts and what it
deliberately does not count.

DEFINITION

  A **block** is one open row a person can see and tick: a line matching `- [ ]` at
  column 0. A heading contributes its rows; a heading with no rows of its own
  contributes nothing, because it is a container (a wave, a phase), never a unit of
  work. Nested rows (indented `- [ ]`) are reported separately as `nested_open` -- they
  are sub-steps of a block, not blocks.

  `- [~]` is **in progress**, not open and not closed; it is reported separately so a
  half-done block cannot hide as either.

  Three exclusions, each reported so it is auditable rather than silent:

    * `checkpoint` sections -- the contract names them: a checkpoint's rows are a
      gate's acceptance list, not work.
    * a block whose own text or whose heading carries a done marker
      (DONE / BUILT / VERIFIED / CLOSED / SHIPPED / COMPLETE / U+2705). AGENTS.md names
      this pattern: "a shipped task can carry 6-10 permanently-unchecked acceptance
      boxes", so those boxes are residue, not work -- counted as `residue`, never as
      open.
    * a program whose header declares its boxes closed. Counted as `closed_by_header`
      and contributing 0, with the declaring line quoted in the JSON so the claim is
      checkable by eye.

  Scope: `tasks/*-todo.md`. `tasks/backlog-clean-up-todo.md` is task `t2-backlog`'s own
  contract and is reported as its own row, never folded into t1's number.

USAGE

    python .claude/cmdc-agents/scripts/convergence-census.py             # human table
    python .claude/cmdc-agents/scripts/convergence-census.py --json PATH # machine record
    python .claude/cmdc-agents/scripts/convergence-census.py --program item
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

#: scripts -> cmdc-agents -> .claude -> repo root
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

#: Targets with their own contract; reported but not summed into t1.
OTHER_TARGETS = {"backlog-clean-up-todo": "t2-backlog"}

DONE_MARKER = re.compile(
    r"(\u2705|\bDONE\b|\bBUILT\b|\bVERIFIED\b|\bCLOSED\b|\bSHIPPED\b|\bCOMPLETE\b)", re.I
)
CHECKPOINT = re.compile(r"checkpoint", re.I)
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
OPEN_ROW = re.compile(r"^- \[ \]")
DONE_ROW = re.compile(r"^- \[[xX]\]")
WIP_ROW = re.compile(r"^- \[~\]")
NESTED_OPEN = re.compile(r"^\s+- \[ \]")
FENCE = re.compile(r"^\s*```")
CLOSED_BY_HEADER = re.compile(
    r"(closed\s+by\s+a\s+header"
    r"|boxes?\s+(?:are\s+)?(?:declared\s+)?closed"
    r"|all\s+rows\s+(?:are\s+)?closed"
    r"|no\s+open\s+work"
    r"|not\s+a\s+unit\s+of\s+work"
    r"|boxes\s+below\s+are\s+closed)",
    re.I,
)


def parse(path: str) -> dict:
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")

    # A fenced code block may quote `- [ ]` without being a row.
    in_fence, kept = False, []
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            kept.append("")
            continue
        kept.append("" if in_fence else line)
    lines = kept

    declared = next(
        ((i, l.strip()) for i, l in enumerate(lines[:160]) if CLOSED_BY_HEADER.search(l)),
        None,
    )

    open_blocks: list[str] = []
    residue: list[str] = []
    wip: list[str] = []
    nested = 0
    closed_rows = 0
    heading = ""
    heading_excluded = False  # inside a checkpoint section

    for line in lines:
        m = HEADING.match(line)
        if m:
            heading = m.group(1).strip()
            heading_excluded = bool(CHECKPOINT.search(heading))
            continue
        if NESTED_OPEN.match(line):
            if not heading_excluded and not DONE_MARKER.search(heading):
                nested += 1
            continue
        if WIP_ROW.match(line):
            if not heading_excluded:
                wip.append(line.strip()[:160])
            continue
        if DONE_ROW.match(line):
            closed_rows += 1
            continue
        if not OPEN_ROW.match(line):
            continue
        if heading_excluded:
            continue
        if DONE_MARKER.search(heading) or DONE_MARKER.search(line):
            residue.append(line.strip()[:160])
            continue
        open_blocks.append(line.strip()[:160])

    name = os.path.basename(path)[: -len("-todo.md")]
    return {
        "program": name,
        "file": os.path.relpath(path, REPO).replace("\\", "/"),
        "blocks": len(open_blocks) if not declared else 0,
        "blocks_unfiltered": len(open_blocks),
        "residue": len(residue),
        "wip": len(wip),
        "nested_open": nested,
        "closed_rows": closed_rows,
        "closed_by_header": None if not declared else {"line": declared[0] + 1, "text": declared[1][:200]},
        "other_target": OTHER_TARGETS.get(name),
        "sample": open_blocks[:3],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--program", help="print one program's blocks verbatim")
    args = ap.parse_args()

    rows = [parse(p) for p in sorted(glob.glob(os.path.join(REPO, "tasks", "*-todo.md")))]

    if args.program:
        want = args.program if args.program.endswith("-todo") else args.program + "-todo"
        for r in rows:
            if r["program"] == want:
                print(json.dumps(r, indent=2))
                return 0
        print(f"no such program: {args.program}", file=sys.stderr)
        return 2

    t1 = [r for r in rows if not r["other_target"]]
    other = [r for r in rows if r["other_target"]]
    live = [r for r in t1 if r["blocks"]]

    print("t1-convergence -- per-program open task blocks")
    print("  (a block = one column-0 `- [ ]` row; checkpoints, done-titled blocks and")
    print("   header-closed programs excluded -- see this file's docstring)")
    print()
    print(f"  programs scanned            {len(t1)}")
    print(f"  programs with open blocks   {len(live)}")
    print(f"  TOTAL open blocks           {sum(r['blocks'] for r in live)}")
    print(f"    of which residue          {sum(r['residue'] for r in t1)}")
    print(f"    in progress (- [~])       {sum(r['wip'] for r in t1)}")
    print(f"    nested sub-steps          {sum(r['nested_open'] for r in t1)}")
    print(f"  programs closed by header   {sum(1 for r in t1 if r['closed_by_header'])}")
    print()
    for r in other:
        print(f"  [{r['other_target']}] {r['program']}: {r['blocks']} open blocks (own contract)")
    print()
    if live:
        print(f"  {'program':34s} {'blocks':>6s} {'wip':>4s} {'residue':>7s} {'nested':>6s}")
        for r in sorted(live, key=lambda r: -r["blocks"]):
            print(f"  {r['program']:34s} {r['blocks']:>6d} {r['wip']:>4d} {r['residue']:>7d} {r['nested_open']:>6d}")
    print()
    print("  header-closed programs (0 by construction, declaration quoted in --json):")
    for r in t1:
        if r["closed_by_header"]:
            print(f"    {r['program']:32s} L{r['closed_by_header']['line']:<5d} {r['closed_by_header']['text'][:88]}")

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        payload = {
            "contract": "t1-convergence: per-program open task-block counts driven to zero",
            "totals": {
                "programs": len(t1),
                "programs_with_open_blocks": len(live),
                "open_blocks": sum(r["blocks"] for r in live),
                "residue": sum(r["residue"] for r in t1),
                "wip": sum(r["wip"] for r in t1),
                "nested_open": sum(r["nested_open"] for r in t1),
                "closed_by_header_programs": sum(1 for r in t1 if r["closed_by_header"]),
            },
            "other_targets": {r["program"]: r["blocks"] for r in other},
            "programs": sorted(t1, key=lambda r: -r["blocks"]),
        }
        with open(args.json, "w", encoding="utf-8", newline="") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

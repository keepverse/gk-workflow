#!/usr/bin/env python3
"""Union `gk-core/scripts/verification-boundaries.v1.json` from a merge's TWO SIDES, then validate.

Why this exists next to `union-verification-registry.py`: that tool reads the conflicted *working
file*, which after a failed union still contains `<<<<<<<` markers, so it parses an invalid document and
refuses -- correct behaviour, unhelpful timing, and the reason a refused union got committed once
(2026-09-23, recorded on the board). This tool never touches the working file: it reads `:2:` and `:3:`
(the merge sides) out of git, so both inputs are always well-formed documents.

The union rule, stated so it is auditable rather than silent:

  * **base** = ours (the integration head). The head is the newer lineage: a branch that has not merged
    the head since another lane's registry edit lands always looks *older* for that entry.
  * a boundary id present only in theirs -> appended verbatim (that is the branch's own contribution).
  * a boundary id present only in ours   -> kept.
  * a boundary id in BOTH but differing  -> ours wins, and the difference is REPORTED (never silently
    dropped: if the branch's version was the newer one, a human reads the report and fixes it).
  * projects: same rule per key.

Exit codes: 0 = union written and valid; 1 = an input did not parse; 2 = the union would not parse
(nothing written); 3 = written, but differences were reported (`--accept-ours` is how you say you read
them).

    python .claude/cmdc-agents/scripts/union-registry-sides.py \
        --ours D:/tmp/registry-repair/ours.json \
        --theirs D:/tmp/registry-repair/theirs.json \
        --out gk-core/scripts/verification-boundaries.v1.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def load(path: str, label: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
        print(f"  {label} did not parse: {exc}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", required=True, help="merge side 2 (`git show :2:<path>`)")
    ap.add_argument("--theirs", required=True, help="merge side 3 (`git show :3:<path>`)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--accept-ours", action="store_true", help="acknowledge the reported differences")
    args = ap.parse_args()

    ours = load(args.ours, "ours")
    theirs = load(args.theirs, "theirs")

    ob = {b["id"]: b for b in ours.get("boundaries", [])}
    tb = {b["id"]: b for b in theirs.get("boundaries", [])}

    added = sorted(set(tb) - set(ob))
    only_ours = sorted(set(ob) - set(tb))
    differing = sorted(i for i in set(ob) & set(tb) if ob[i] != tb[i])

    merged = json.loads(json.dumps(ours))  # deep copy of the base
    merged["boundaries"] = list(ours.get("boundaries", []))
    for i in added:
        merged["boundaries"].append(tb[i])

    proj_added = sorted(set(theirs.get("projects", {})) - set(ours.get("projects", {})))
    proj_diff = sorted(
        k for k in set(ours.get("projects", {})) & set(theirs.get("projects", {}))
        if ours["projects"][k] != theirs["projects"][k]
    )
    for k in proj_added:
        merged.setdefault("projects", {})[k] = theirs["projects"][k]

    print(f"  base (ours):   {len(ob)} boundaries / {len(ours.get('projects', {}))} projects")
    print(f"  theirs:        {len(tb)} boundaries / {len(theirs.get('projects', {}))} projects")
    print(f"  added from theirs:   {added or '(none)'}")
    print(f"  only in ours:        {only_ours or '(none)'}")
    print(f"  projects added:      {proj_added or '(none)'}")
    if differing:
        print(f"  DIFFERING (ours wins, read these): {differing}")
    if proj_diff:
        print(f"  DIFFERING projects (ours wins): {proj_diff}")

    try:
        text = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
        json.loads(text)
    except Exception as exc:  # noqa: BLE001
        print(f"  union would not parse: {exc} -- nothing written", file=sys.stderr)
        return 2

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(f"  wrote {args.out}: {len(merged['boundaries'])} boundaries / {len(merged.get('projects', {}))} projects")

    if (differing or proj_diff) and not args.accept_ours:
        print("  differences reported -- re-run with --accept-ours once read", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

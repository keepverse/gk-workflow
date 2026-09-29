#!/usr/bin/env python3
"""BCU2.10's model-free reading for the action-corpus round run (T4.6).

Why this exists: BCU2.10's acceptance wants *"accepted size / thinCell shortfall delta / `quotaDrift`
clean"* **recorded**, and a delta needs a recorded BEFORE. The 2026-09-21 attempt
(`710390b56`) recorded none and landed no pipeline outputs — see
[tasks/reports/bcu2-10-closeout.md](../reports/bcu2-10-closeout.md). BCU2.10's run itself is a
manager-run detached job (`tasks/run-board-20260920.md`, 2026-09-23): this script reads the committed
round-1 corpus through seedsmith's own coverage tool in its `--dry-run` path, which computes in memory
and **writes nothing** (verified: `git status --short` is unchanged after a run).

    # baseline (before the run) and delta (after it) are the same command
    PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-10-readings.py
    PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-10-readings.py --out tasks/reports/bcu2-10-readings.json

Zero model calls: every number is arithmetic over committed files. `thinCellShortfall` is summed here
from the tool's own canonical doc (the tool reports the cell entries, not the sum) — so the *count* and
*quota* fields are the tool's, and only the addition is this script's.

Exit codes: 0 always (a reading, never a gate); 2 when the imports/tool are unavailable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "seedsmith"))

try:
    from seedsmith.adapters.actions import generate_coverage_report as gcr
    from seedsmith.adapters.actions.coverage_report import derive as cr
except ImportError as exc:  # pragma: no cover - environment, not logic
    print(f"cannot import seedsmith's coverage tool: {exc}", file=sys.stderr)
    raise SystemExit(2)

ACTIONS_ROOT = REPO_ROOT / "data" / "seed" / "actions"


def read_round(round_no: int) -> dict:
    """The tool's canonical doc for `round_no`, captured without writing a file."""
    captured: dict = {}
    original = cr.canonical_dump
    cr.canonical_dump = lambda doc: (captured.__setitem__("doc", doc), original(doc))[1]
    try:
        summary = gcr.regenerate(round_no=round_no, write=False)
    finally:
        cr.canonical_dump = original
    return {"summary": summary, "doc": captured["doc"]}


def cell_readings(doc: dict) -> dict:
    cells = [entry for entry in doc["entries"] if entry.get("kindOfEntry") == "cell"]
    thin = [entry for entry in cells if entry.get("thin")]
    return {
        "cellCount": len(cells),
        "thinCellCount": len(thin),
        "thinCellShortfall": sum(max(0, entry["quota"] - entry["count"]) for entry in thin),
    }


def committed_readings(round_no: int) -> dict:
    """What the committed report says, so a stale on-disk report is visible, not assumed."""
    path = ACTIONS_ROOT / "_reports" / f"coverage-round-{round_no}.json"
    if not path.is_file():
        return {"path": path.relative_to(REPO_ROOT).as_posix(), "present": False}
    raw = path.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "present": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "acceptedCorpusSize": doc["_meta"].get("acceptedCorpusSize"),
        "corpusHash": doc["_meta"].get("corpusHash"),
        **cell_readings(doc),
    }


def build(round_no: int) -> dict:
    run = read_round(round_no)
    summary, doc = run["summary"], run["doc"]
    gap = list(summary["gapMetrics"])
    return {
        "reading": f"BCU2.10 T4.6 round-{round_no} action corpus, model-free (no writes)",
        "repoHead": _head(),
        "round": round_no,
        "acceptedCorpusSize": summary["acceptedCorpusSize"],
        "corpusHash": doc["_meta"]["corpusHash"],
        "tuningVersion": doc["_meta"]["tuningVersion"],
        "mode": doc["_meta"]["mode"],
        "roster": doc["_meta"]["roster"],
        "verdict": summary["verdict"],
        "reviewQueueCount": summary["reviewQueueCount"],
        "quotaDriftClean": "action.corpus.quotaDrift" not in gap,
        "gapMetrics": gap,
        "nextTargetCount": summary["nextTargetCount"],
        "docHash": summary["docHash"],
        **cell_readings(doc),
        "committedReport": committed_readings(round_no),
    }


def _head() -> str:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - environment, not logic
        return "unknown"


def run(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", type=int, default=1, dest="round_no")
    ap.add_argument("--out", type=Path, default=None,
                    help="write the JSON here (default: stdout, nothing written)")
    args = ap.parse_args(argv)

    reading = build(args.round_no)
    dump = json.dumps(reading, indent=1, sort_keys=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(dump, end="")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""BCU2.12 / J10 — exercise the `sheetRead` census gate (H7) on all four paths, model-free.

J10's own Verification line is *"the census refuses any lot with no `sheetRead` row (H7)"*, and the gate's
docstring names both refusal reasons ("a census against a missing row and against a stale row both
refuse"). This probe runs the CLI surface the Verify line names against throwaway `--sheet-dir` /
`--review-dir` overrides, so all four outcomes are observed rather than inferred:

    python tasks/reports/bcu2-12-j10-review-gate-probe.py

  A. no sheet rendered            -> EXIT_CANNOT_RUN (`SheetNotRendered`)
  B. sheet, no sheetRead row      -> EXIT_REFUSED (`CensusRefused`: missing row)
  C. sheet, stale sheetRead row   -> EXIT_REFUSED (`CensusRefused`: stale row)
  D. sheet, current sheetRead row -> exit 0, gate cleared

Nothing under the repository is written: the probe works in one temp directory and deletes it with a
throwing delete (docs/contributing/testing-standard.md R3 — a failed cleanup is a failure, never swallowed).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOT = "probe-lot"


def run_cli(sheet_dir: Path, review_dir: Path, lot: str = LOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "seedsmith", "trees", "review", "--lot", lot, "--census",
         "--sheet-dir", str(sheet_dir), "--review-dir", str(review_dir)],
        cwd=REPO_ROOT / "tools" / "seedsmith", capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "."},
    )


def write_sheet(sheet_dir: Path, revision: str) -> None:
    path = sheet_dir / LOT / "sheet.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"lot": LOT, "sheetRevision": revision}), encoding="utf-8")


def write_queue(review_dir: Path, revision: str) -> None:
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / f"{LOT}.json").write_text(
        json.dumps({"lot": LOT, "entries": [],
                    "sheetReads": [{"lot": LOT, "sheetRevision": revision, "by": "probe",
                                    "utc": "2026-09-23T00:00:00Z"}]}),
        encoding="utf-8")


def build() -> dict:
    results: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="bcu2-12-j10-probe-"))
    try:
        sheet_dir = tmp / "sheet"
        review_dir = tmp / "review"

        # A — no sheet rendered at all.
        out = run_cli(sheet_dir, review_dir)
        results.append({"case": "no sheet rendered", "exit": out.returncode,
                        "reason": (out.stderr or out.stdout).strip().splitlines()[-1][:160]})

        # B — sheet present, queue holds no sheetRead row.
        write_sheet(sheet_dir, "rev-A")
        out = run_cli(sheet_dir, review_dir)
        results.append({"case": "sheet, no sheetRead row", "exit": out.returncode,
                        "reason": (out.stderr or out.stdout).strip().splitlines()[-1][:160]})

        # C — sheet present, sheetRead row names a different revision.
        write_queue(review_dir, "rev-OLD")
        out = run_cli(sheet_dir, review_dir)
        results.append({"case": "sheet, stale sheetRead row", "exit": out.returncode,
                        "reason": (out.stderr or out.stdout).strip().splitlines()[-1][:160]})

        # D — sheet present, sheetRead row names the current revision.
        write_queue(review_dir, "rev-A")
        out = run_cli(sheet_dir, review_dir)
        results.append({"case": "sheet, current sheetRead row", "exit": out.returncode,
                        "reason": (out.stdout or out.stderr).strip().splitlines()[-1][:160],
                        "cleared": out.returncode == 0})

        # The committed review dirs themselves: what a real lot would see today.
        committed_sheet = REPO_ROOT / "docs" / "research" / "passive-tree" / "_review"
        committed_review = REPO_ROOT / "data" / "seed" / "passive-tree" / "_review"
        out = run_cli(committed_sheet, committed_review, lot="any-lot")
        results.append({"case": "committed dirs, lot 'any-lot'", "exit": out.returncode,
                        "reason": (out.stderr or out.stdout).strip().splitlines()[-1][:160]})
        committed_state = {
            "sheetDirExists": committed_sheet.is_dir(),
            "reviewDirExists": committed_review.is_dir(),
            "sheetLots": sorted(p.name for p in committed_sheet.iterdir()) if committed_sheet.is_dir() else [],
            "reviewLots": sorted(p.name for p in committed_review.iterdir()) if committed_review.is_dir() else [],
        }
    finally:
        shutil.rmtree(tmp)  # throws on failure — never swallowed

    return {
        "reading": "BCU2.12/J10 — the sheetRead census gate, four paths (model-free)",
        "repoHead": _head(),
        "cases": results,
        "committedReviewState": committed_state,
        "tempRemoved": not tmp.exists(),
    }


def _head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - environment, not logic
        return "unknown"


def main() -> int:
    print(json.dumps(build(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

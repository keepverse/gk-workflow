#!/usr/bin/env python3
"""BCU2.12 -- passive-tree J9/J10 support: the species-tree full run, as a detached job with a report
artefact.

Release: BCU2.12 (passive-tree J9 / J10 / J13). J9 = the per-species production run through the
caller J8 already built and tested (`adapters/trees/species/generate_tree.run_species_tree`), driven
over a roster by `gk-forge/tools/seedsmith/_j9_batch_run.py` (the harness the J9 de-risking pass wrote;
task 4 of this brief). J10 = the census/health check over the committed corpus. J13 (the 42 shared
trees) is NOT here -- it carries its own owner go/no-go and the manager holds it.

Rules obeyed, modelled on the BCU2.11 pair (`bcu211-full-run.ps1`, since deleted, /
`bcu211-report.py`, which remains):
  * "Bound the first live run": a 2-species smoke precedes the unbounded one, so a bad prompt or a
    dead model fails in minutes, not days.
  * Resume safety is the SHARED ledger, not a flag: `run_language_stage` never regenerates a subject
    already recorded in `data/seed-tree/_runs/tree-language.ledger.json`, so an interrupt costs the
    in-flight species' unfinished nodes and nothing else. The resume pass below re-invokes the
    identical command and proves it.
  * Readings are recorded, never asserted.

Replaces `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`.

WHY THE POWERSHELL FORM WAS RETIRED
-----------------------------------
* **NO SUBPROCESS CALL WAS BOUNDED.** The roster count, the smoke run, the full run, the resume
  pass, the census and the report all ran with no timeout. A hung model call or a dead worktree
  holds the detached job open forever, and a detached job has no operator to notice. Every call now
  carries a timeout; the full-run and resume bounds are generous (7 days) because a corpus run is
  measured in hours, but they are finite -- an unbounded subprocess is a job that never ends.

* **`$LASTEXITCODE` IS A MUTABLE GLOBAL.** The original read it immediately after each command,
  before any output normalization, "or any later command can run" first. Python's `subprocess.run`
  returns `(returncode, stdout, stderr)` together, so the exit code and the output cannot drift
  apart -- the defect the original's comment warns about is structurally impossible.

* **THE ROSTER COUNT'S FOUR FAILURE MODES WERE STRINGLY-TYPED.** Empty, non-integer, non-positive
  and command-nonzero each had their own `ABORTED=roster_count_failed` / `ROSTER_FAILURE=` pair.
  They are now a pure validation function with each mode pinned by a test.

* **THE STALE-FILE CLEANUP WAS SILENT.** `Remove-Item -Force` on a missing file is a no-op in
  PowerShell; `Path.unlink(missing_ok=True)` says the same thing in Python, and the deletion is
  reported so a run says what it cleared.

DELIBERATELY UNCHANGED
----------------------
Same worktree default, same smoke-first bound, same resume-only-on-success rule, same
census/report tail, same output lines (`HEAD=`, `roster_species=`, `smoke_exit=`, `full_exit=`,
`resume_exit=`, `check_exit=`, `report_exit=`, `ABORTED=`, `FINISHED=` / `=== VERDICT JOB END ===`),
same exit contract: 1 on a roster or smoke failure or any nonzero tail, 0 on success.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_ID = "bcu212-full-run"

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_REFUSED = 64

DEFAULT_SMOKE = 2
DEFAULT_PYTHON = "python"
DEFAULT_WORKTREE = (".claude", "worktrees", "corpus-bcu212")

# The roster count is a fast, local read. The smoke is bounded. The census and report are
# model-free. The full run and the resume pass are measured in HOURS -- the 7-day bound is a safety
# net against a hung process, not an expectation, and it is finite because the port standard
# forbids an unbounded subprocess.
TIMEOUT_ROSTER_SEC = 120
TIMEOUT_GIT_SEC = 60
TIMEOUT_SMOKE_SEC = 3600
TIMEOUT_FULL_SEC = 604800
TIMEOUT_CHECK_SEC = 3600
TIMEOUT_REPORT_SEC = 3600

ROSTER_CODE = ("from seedsmith.adapters.trees.species.roster import load_roster; "
               "print(len(load_roster().species_ids))")
BATCH_RUN = ("tools", "seedsmith", "_j9_batch_run.py")
CENSUS = ("-m", "seedsmith", "check", "--family", "PassiveTree")

REFUSAL_REASONS = {
    "INVALID-SMOKE", "COMMAND-TIMED-OUT", "RUNNER-CRASHED", "ROSTER-COUNT-FAILED",
}

# THE SEAM THE SUITE NEEDS, bound once to a module-private name. `subprocess` is a process-wide
# module: a test that patches it reaches every other test in this project.
_RUN = subprocess.run


class Refusal(Exception):
    """A named precondition or transport failure. Never exits 0 having not asked."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


def run_command(cmd: list[str], cwd: Path, env: dict, timeout: int, what: str) -> tuple[int, str, str]:
    """One bounded subprocess call. Returns (returncode, stdout, stderr) together, so the exit code
    and the output cannot drift apart -- the defect PowerShell's mutable `$LASTEXITCODE` allowed."""
    try:
        proc = _RUN(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(cwd), env=env)
    except subprocess.TimeoutExpired as expired:
        raise Refusal("COMMAND-TIMED-OUT",
                      f"{what} did not finish within {timeout}s: {' '.join(cmd[:3])}") from expired
    except OSError as error:
        raise Refusal("RUNNER-CRASHED", f"could not start {what}: {error}") from error
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def validate_roster_output(text: str) -> int:
    """The roster count, with the original's four failure modes as named refusals.

    The run's population is the ROSTER's own length, NEVER a literal: a hardcoded count would
    silently under-run the corpus the moment the roster grows.
    """
    stripped = text.strip()
    if not stripped:
        raise Refusal("ROSTER-COUNT-FAILED", "roster_count_empty: the roster command printed nothing")
    try:
        count = int(stripped)
    except ValueError:
        raise Refusal("ROSTER-COUNT-FAILED",
                      f"roster_count_not_integer: the roster command printed {stripped!r}")
    if count <= 0:
        raise Refusal("ROSTER-COUNT-FAILED",
                      f"roster_count_non_positive: the roster holds {count} species")
    return count


def run_job(worktree: Path, smoke: int, python_cmd: str, repo: Path) -> dict:
    """The whole detached job. Returns the readings; raises Refusal on a transport failure.

    The output lines are the original's, printed as the job progresses so a detached log shows
    the same shape it always did.
    """
    env = dict(os.environ, PYTHONPATH="tools/seedsmith")
    readings: dict = {"worktree": str(worktree)}

    # A new attempt must never leave an older final report or batch-results file looking current.
    # The batch driver checkpoints its completed prefix after every species; if this process is
    # killed, that current partial file remains while no stale final report does.
    for stale in (worktree.joinpath(*("tools", "seedsmith", "_j9_batch_run_results.json")),
                  worktree.joinpath(*("tasks", "reports", "BCU2.12-full-run.json"))):
        if stale.is_file():
            stale.unlink()
            print(f"cleared stale {stale}")

    head_code, head_out, _ = run_command(["git", "rev-parse", "--short", "HEAD"], worktree, env,
                                         TIMEOUT_GIT_SEC, "git rev-parse --short HEAD")
    branch_code, branch_out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], worktree,
                                             env, TIMEOUT_GIT_SEC, "git rev-parse --abbrev-ref HEAD")
    readings["head"] = head_out.strip()
    readings["branch"] = branch_out.strip()
    readings["head_code"] = head_code
    readings["branch_code"] = branch_code
    print(f"HEAD={head_out.strip()}  branch={branch_out.strip()}")
    print(f"WORKTREE={worktree}")
    print(f"STARTED={datetime.now(timezone.utc).isoformat()}")

    # The roster count. A bad roster command is a hard stop; never let its output become the
    # full-run count by accident.
    roster_code, roster_out, roster_err = run_command(
        [python_cmd, "-c", ROSTER_CODE], worktree, env, TIMEOUT_ROSTER_SEC, "the roster count")
    roster_text = roster_out.strip()
    print(f"roster_output={roster_text}")
    if roster_code != 0:
        print("ABORTED=roster_count_failed")
        print(f"ROSTER_FAILURE=roster_count_command_nonzero exit={roster_code}")
        readings["aborted"] = "roster_count_failed"
        readings["exitCode"] = EXIT_FAILED
        return readings
    try:
        roster_count = validate_roster_output(roster_text)
    except Refusal as refusal:
        print("ABORTED=roster_count_failed")
        print(f"ROSTER_FAILURE={refusal.detail}")
        readings["aborted"] = "roster_count_failed"
        readings["exitCode"] = EXIT_FAILED
        return readings
    readings["roster_count"] = roster_count
    print(f"roster_species={roster_count}")

    print(f"=== smoke: bounded first live run ({smoke} species) ===")
    smoke_code, _, _ = run_command([python_cmd, *BATCH_RUN, str(smoke)], worktree, env,
                                   TIMEOUT_SMOKE_SEC, "the smoke run")
    print(f"smoke_exit={smoke_code}")
    readings["smoke_exit"] = smoke_code
    if smoke_code != 0:
        print("ABORTED=smoke_failed")
        readings["aborted"] = "smoke_failed"
        readings["exitCode"] = smoke_code
        return readings

    print("=== full run (resume-safe; re-invoke on interrupt) ===")
    full_code, _, _ = run_command([python_cmd, *BATCH_RUN, str(roster_count)], worktree, env,
                                  TIMEOUT_FULL_SEC, "the full run")
    print(f"full_exit={full_code}")
    readings["full_exit"] = full_code

    resume_code = 0
    if full_code == 0:
        print("=== resume pass (must regenerate nothing already in the shared ledger) ===")
        resume_code, _, _ = run_command([python_cmd, *BATCH_RUN, str(roster_count)], worktree, env,
                                        TIMEOUT_FULL_SEC, "the resume pass")
        print(f"resume_exit={resume_code}")
    else:
        print("resume_exit=skipped_after_failed_full_run")
    readings["resume_exit"] = resume_code

    # Even a failed full pass gets a fresh census/report from the incrementally checkpointed prefix;
    # the process still exits non-zero below. This preserves the evidence without allowing a later
    # green line to turn the detached job into a false success.
    print("=== census / health check (model-free) ===")
    check_code, _, _ = run_command([python_cmd, *CENSUS], worktree, env, TIMEOUT_CHECK_SEC,
                                   "the census")
    print(f"check_exit={check_code}")
    readings["check_exit"] = check_code

    print("=== report artefact ===")
    report_script = Path(__file__).resolve().parent / "bcu212-report.py"
    report_code, _, _ = run_command([python_cmd, str(report_script), "--python", python_cmd],
                                    worktree, env, TIMEOUT_REPORT_SEC, "the report")
    print(f"report_exit={report_code}")
    readings["report_exit"] = report_code

    if full_code != 0 or resume_code != 0 or check_code != 0 or report_code != 0:
        print(f"FAILED={datetime.now(timezone.utc).isoformat()}")
        print("=== VERDICT JOB FAILED ===")
        readings["exitCode"] = EXIT_FAILED
        return readings

    print(f"FINISHED={datetime.now(timezone.utc).isoformat()}")
    print("=== VERDICT JOB END ===")
    readings["exitCode"] = EXIT_OK
    return readings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bcu212-full-run",
        description="BCU2.12 passive-tree J9/J10: the species-tree full run as a detached job "
                    "(replaces bcu212-full-run.ps1).")
    parser.add_argument("--worktree", default="",
                        help="the worktree to run in (default: the corpus-bcu212 worktree)")
    parser.add_argument("--smoke", type=int, default=DEFAULT_SMOKE,
                        help=f"species in the bounded first live run (default {DEFAULT_SMOKE})")
    parser.add_argument("--python", default=DEFAULT_PYTHON,
                        help=f"the python command to drive (default {DEFAULT_PYTHON!r})")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.smoke <= 0:
        return _refuse("INVALID-SMOKE", f"--smoke {args.smoke} runs no species", args.json)
    python_cmd = args.python.strip() or DEFAULT_PYTHON

    repo = Path(__file__).resolve().parents[3]
    worktree = Path(args.worktree).expanduser() if args.worktree else repo.joinpath(*DEFAULT_WORKTREE)
    if not worktree.is_absolute():
        worktree = Path.cwd() / worktree
    worktree = worktree.resolve()

    try:
        readings = run_job(worktree, args.smoke, python_cmd, repo)
    except Refusal as refusal:
        return _refuse(refusal.reason, refusal.detail, args.json)

    if args.json:
        print(json.dumps({"tool": TOOL_ID, **readings}, indent=2, default=str))
    return readings["exitCode"]


def _refuse(reason: str, detail: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"tool": TOOL_ID, "verdict": "REFUSED", "reason": reason, "detail": detail,
                          "exitCode": EXIT_REFUSED}, indent=2))
    else:
        print(f"[{TOOL_ID}] REFUSED: {reason}", file=sys.stderr)
        print(f"  {detail}", file=sys.stderr)
    return EXIT_REFUSED


if __name__ == "__main__":
    sys.exit(main())

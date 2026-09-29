# Phase 0 acceptance plan — fail-closed merge plane

**Lane:** `resume-00a-fail-closed-recovery-20260925` (recovery of the abandoned `resume-00-fail-closed-merge` draft)
**Purpose:** prevent false-green merged-head, acceptance, and merge consumption before P1 implementation.

## Review identity

- Base SHA: `61750b5`
- Reviewed SHA: read from the recovery lane's final report; never substitute a moving branch tip.
- The abandoned first worker made no accepted claim; its dirty four-file draft was copied into the recovery worktree as an unreviewed starting point.
- Review checkout: clean detached checkout at the reviewed SHA.
- Allowed paths:
  - `.claude/cmdc-agents/scripts/post_merge_check.py`
  - `.claude/cmdc-agents/scripts/accept-lane.ps1`
  - `.claude/cmdc-agents/scripts/merge-lanes.py`
  - `.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`

## Required manager checks

1. Confirm the lane's final SHA is a descendant of `e7a86491e` and the diff contains no path outside the fence.
2. Run `git diff --check e7a86491e..<reviewed-sha>` in the clean checkout.
3. Run the focused regression script and capture its complete output and exit code.
4. Reproduce a failing merged-head condition and assert the PowerShell process exit is nonzero, not merely that the text says `VERDICT: RED`.
5. Exercise acceptance with an empty check set, missing expected SHA, stale artifact, malformed artifact, and mismatched SHA; every case must fail closed with a reason.
6. Exercise merge consumption with missing, malformed, stale, and mismatched acceptance evidence; no merge may proceed.
7. Run the repository verification planner for every changed path with the lane session id. A missing path mapping is a boundary defect, not a reason to run the full suite.
8. Inspect the worker's own report/session text, not only `status.json`; record open questions and untested claims.
9. Write the manager acceptance artifact as `.claude/cmdc-agents/acceptance/resume-00a-fail-closed-recovery-<8-char-sha>.json` with the full reviewed SHA, non-empty checks, attribution, and verdict.
10. Merge only that exact reviewed SHA, then run the merged-head check again from the integration branch.

## Acceptance rule

A worker self-report, a printed `RED`, or a zero exit from a wrapper that swallowed `$LASTEXITCODE` is not acceptance. The only acceptable result is a clean, exact-SHA review with a non-empty machine-readable check record and a nonzero process reproduction for every fail-closed case.

Until all items are evidenced, P1 implementation lanes remain staged but unspawned.

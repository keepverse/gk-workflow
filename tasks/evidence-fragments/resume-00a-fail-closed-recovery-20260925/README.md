# Superseded: this rescue is discharged, and applying it is now wrong

`post-merge-check-positive-test-count.patch` was rescued out of the de-registered worktree
`opencode-resume-00a-fail-closed-recovery-20260925` on 2026-09-25, at a time when it verified to apply
**and** reverse. **That is no longer true, and this file is why.**

## What the rescue carried

A fail-closed fix for the merged-head acceptance gate: `post-merge-check.ps1` read `Total` as evidence
that tests executed, and because VSTest's `Total` counts **skipped** tests, an all-skipped run
satisfied it and the gate returned GREEN for a run in which nothing executed. The patch carried the
`.ps1` fix plus `test_skipped_only_test_count_is_red` in `test_fail_closed_pipeline.py`.

## Why it cannot be applied any more

    git apply --check  ->  .claude/cmdc-agents/scripts/post-merge-check.ps1: No such file or directory
                          .claude/cmdc-agents/scripts/accept-lane.ps1: No such file or directory

Both `.ps1` targets were **retired** by `caa9fb275` — *"Repoints test_fail_closed_pipeline.py at the
Python twins, which retires accept-lane.ps1 and post-merge-check.ps1"*. The two `.py` hunks still
apply, with offsets; the two `.ps1` hunks have no target. `test_skipped_only_test_count_is_red` is
**absent** from today's `test_fail_closed_pipeline.py`, so the test this rescue carried never landed
and is not coming back through this patch.

## What happened to the defect instead

The `.ps1` -> `.py` port reproduced the defect faithfully — which is exactly what a port does, and why
a faithful port is not a fix. The hole then lived on in the successor file, unfixed, in the harness
that decides whether a lane is accepted. It is now **fixed in place**:

    .claude/cmdc-agents/scripts/post_merge_check.py
        POSITIVE_COUNT_RE  was  r"\b(?:Total|Passed):\s*(\d+)"
                        now  r"\bPassed:\s*(\d+)"
    .claude/cmdc-agents/scripts/test_post_merge_check.py
        SummaryTests.test_a_skipped_run_is_not_a_positive_test_count

Measured before the change, against the module's own predicates: the all-skipped line
`Skipped!  - Failed: 0, Passed: 0, Skipped: 38, Total: 38` yielded `findall == ['0', '38']` and a
**GREEN** verdict, while `No test matches the given testcase filter` and a genuine `Failed!` both
correctly returned RED — so the hole was the `Total` alternative alone, not a permissive gate. The
regression test is load-bearing: it fails against the old pattern and passes against the new.

## So do not apply this patch

Applying the surviving `.py` hunks would duplicate a fix that is already in the tree, and the two dead
`.ps1` hunks would fail outright. The finding this rescue recorded is **closed in the successor file**,
which is a better outcome than the rescue: a patch is a proposal, a landed fix with a load-bearing
regression test makes the defect un-recurrable.

Kept tracked because it is the provenance of the defect and of the `.ps1`-era fix, not because it is
pending work. See `tasks/backlog-clean-up-todo.md` CB8 (corrected) and CB14.

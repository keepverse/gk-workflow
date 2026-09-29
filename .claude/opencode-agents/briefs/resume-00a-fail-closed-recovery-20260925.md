# Phase 0A recovery — fail-closed merge/acceptance plane

## Goal

Recover and independently finish the manager-owned fail-closed merge, lane-acceptance, and merged-head verification work. The first worker made uncommitted progress but its OpenCode session terminated when a read tool failed; this lane starts with those four files copied into its own worktree. Treat them as an unreviewed draft, not as accepted code.

No product lane may be accepted until this plane has a real process-level fail-closed proof and manager review.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/contributing/agent-git.md`
- `docs/contributing/session-boundary.md`
- `tasks/reports/mega-merge-deep-audit-20260924.md` (verification/release findings)
- the current four allowed scripts and all their callers/tests

## Starting draft

The setup copies these unreviewed files from the abandoned `opencode-resume-00-fail-closed-merge` worktree into this worktree before you start:

- `.claude/cmdc-agents/scripts/post-merge-check.ps1`
- `.claude/cmdc-agents/scripts/accept-lane.ps1`
- `.claude/cmdc-agents/scripts/merge-lanes.py`
- `.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`

They are dirty starting evidence. Do not assume they are correct. Preserve useful tests, repair defects, and leave the final worktree dirty for manager harvest. Do not commit, push, or merge.

## Allowed paths

Only the four copied script/test paths above and `tasks/reports/resume-00a-fail-closed-recovery-20260925.md`.

## Required behavior

1. `post-merge-check.ps1` must return a nonzero process status for build, guard, test, missing-summary, malformed-evidence, and other RED conditions. A printed `RED` is not success. Legal-game/interops limitations must be explicit blocked evidence, never green.
2. The merged-head check must cover the declared post-split project surface and reject an empty or silently substituted check set. Do not broaden scope to unrelated product work.
3. `accept-lane.ps1` must require a full expected SHA and at least one schema-valid verdict/check artifact. Empty, malformed, stale, or mismatched evidence must fail closed.
4. `merge-lanes.py` must consume machine-readable acceptance evidence for the exact reviewed SHA before merging a mutable lane branch. Missing/stale/mismatched evidence must refuse with a reason and nonzero status.
5. Regression tests must exercise real PowerShell/Python entry points in isolated temporary fixtures and prove process-level nonzero/zero behavior for: RED exit, empty checks, missing SHA, mismatched SHA, stale artifact, and refusal without evidence. Do not weaken an existing guard to make a test pass.
6. Preserve no-push/no-direct-merge rules for worker lanes. Do not invent acceptance from a report or a status label; verify the actual artifact and checkout SHA.

## Required investigation and report

- Record the starting diff and why the first worker failed.
- Run the focused regression suite before and after repairs.
- Add a report at `tasks/reports/resume-00a-fail-closed-recovery-20260925.md` with exact commands, outputs, changed files, full worktree SHA, known limitations, open questions, and next steps.
- If the draft is already correct, say so with reproductions; do not make cosmetic changes.
- If a required fix is outside the four-file fence, report the exact blocker and do not widen the lane.

## Verification

```powershell
python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py
pwsh -NoProfile -File .claude/cmdc-agents/scripts/post-merge-check.ps1 -?
git diff --check
git status --porcelain
git rev-parse HEAD
```

Run additional focused tests for any changed behavior. Do not run an unfiltered full suite.

End with exactly:

```text
<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>
```

`done` means the scoped fail-closed plane is implemented and evidenced, not that the whole program is complete.

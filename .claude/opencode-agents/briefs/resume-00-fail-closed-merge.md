# Resume task 00 — fail-closed merge and acceptance plane

## Goal

Repair the manager-owned merge/acceptance scripts so a red merged-head result, missing proof, stale/mismatched SHA, or empty check set cannot be reported or consumed as success. This is the first implementation gate for the resumed program; product lanes wait for its acceptance.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/contributing/agent-git.md`
- `docs/contributing/session-boundary.md`
- `tasks/reports/mega-merge-deep-audit-20260924.md` (verification section)
- the current scripts named below and their existing callers/tests

## Allowed paths

- `.claude/cmdc-agents/scripts/post_merge_check.py`
- `.claude/cmdc-agents/scripts/accept_lane.py`
- `.claude/cmdc-agents/scripts/merge-lanes.py`
- `.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`

## Required behavior

1. `post-merge-check.ps1` must return a nonzero process status for build, guard, test, missing-summary, or other RED conditions; a printed RED is not enough.
2. The merged-head check must cover the declared post-split project surface, not silently use a stale two-project default. Preserve legal-game/interops limitations as explicit blocked evidence rather than green.
3. `accept-lane.ps1` must require a full expected SHA and at least one schema-valid check/verdict; empty, malformed, stale, or mismatched evidence must fail closed.
4. `merge-lanes.py` must consume machine-readable acceptance evidence for the exact reviewed SHA before merging a mutable lane branch. It must refuse missing/stale/mismatched evidence and print the reason.
5. Add focused regression coverage for: RED process exit, empty checks, missing SHA, mismatched SHA, stale acceptance artifact, and refusal to merge without evidence. Tests must use the repository's real PowerShell/Python behavior and temporary isolated fixtures; do not weaken an existing guard to make a test pass.
6. Preserve the repository's no-push/no-direct-merge rules for worker lanes. Leave the worktree dirty for manager harvest; do not commit or push.

## Evidence/report contract

Run focused tests and exact reproductions. Report the full SHA, changed files, every command with its result, what remains untested, open questions, and a next plan. Do not claim a gate is fixed without a process-level nonzero/zero reproduction.

## Verification

- `python .claude/cmdc-agents/scripts/test_fail_closed_pipeline.py`
- `pwsh -NoProfile -File .claude/cmdc-agents/scripts/post-merge-check.ps1 -?`
- `git status --porcelain`
- `git rev-parse --short HEAD`

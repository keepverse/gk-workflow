# Resume 25 — strain-splice-host dependency triage

## Task

Read the strain-splice-host map/specs and the current todo, including routed findings. Identify the
next bounded deterministic slice that does not require a live save or a tuning publish. Verify
current reader/writer contracts rather than trusting stale row prose.

## Boundary

- Edit only `tasks/reports/resume-25-strain-splice-triage-20260925.md`.
- No product, generated corpus, tuning, CI, or ledger edits.
- Do not run a model call or publish a new data revision.
- Keep live-only findings live-only.

## Required report

Name the recommended row, exact source/test paths, focused verification command, stop condition,
and any H7/publish/owner dependency. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

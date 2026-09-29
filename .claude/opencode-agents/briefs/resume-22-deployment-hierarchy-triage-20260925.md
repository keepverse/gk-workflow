# Resume 22 — deployment-hierarchy dependency triage

## Task

Read the deployment-hierarchy map/specs and `tasks/deployment-hierarchy-todo.md`. Select the first
bounded row that is genuinely buildable at the current head, distinguishing carry-in, injury, and
durability work. Verify the claimed prerequisites against code and tests; do not treat a partially
built row as unimplemented or a planned row as permission to design it.

## Boundary

- Edit only `tasks/reports/resume-22-deployment-hierarchy-triage-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not absorb the open Delve/CAI3.5 automation seam.
- Record any cross-program dependency instead of widening the fence.

## Required report

Give the recommended next row, rejected alternatives, exact path fence, focused verification
boundary, H1/H2/H7 implications, and unresolved owner questions. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

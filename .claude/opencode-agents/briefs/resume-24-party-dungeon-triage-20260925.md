# Resume 24 — party-dungeon dependency triage

## Task

Read the party-dungeon map/specs and `tasks/party-dungeon-todo.md` around the current open rows.
Find the next bounded task after the accepted persisted-steering row, without absorbing CAI3.5 or
`RpgHub.Resume`. Separate real live-only proof from deterministic implementation work.

## Boundary

- Edit only `tasks/reports/resume-24-party-dungeon-triage-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not reopen D2.16a or rewrite accepted steering evidence.
- Do not call a browser/live absence a code defect.

## Required report

Return a dependency-ordered shortlist with exact fences, focused verification, hard edges, and
owner/live blockers. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

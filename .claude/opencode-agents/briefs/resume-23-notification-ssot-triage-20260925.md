# Resume 23 — notification-ssot dependency triage

## Task

Read the notification-ssot map/specs, `tasks/notification-ssot-todo.md`, and the recorded
coordination asks. Separate rows that are genuinely buildable now from rows gated by a real
world-creation path, owner piece review, or live probe. Do not implement UI or world behavior.

## Boundary

- Edit only `tasks/reports/resume-23-notification-ssot-triage-20260925.md`.
- No product, FE, generated-data, tuning, CI, or ledger edits.
- Do not convert a blocked live proof into a debug-fabricated proof.
- Keep owner-gated rows explicitly owner-gated.

## Required report

List the next buildable row(s), their exact files and tests, the smallest safe fanout slice, and
the owner questions that remain. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

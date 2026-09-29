# Resume 21 — effect-pipeline dependency triage

## Task

Read the effect-pipeline capability map/specs and `tasks/effect-pipeline-todo.md`. Identify the
first dependency-ready bounded implementation row after the current head, its exact producer/consumer
paths, hard edges, verification boundary, and any owner question that must remain open. Do not
implement or regenerate anything.

## Boundary

- Edit only `tasks/reports/resume-21-effect-pipeline-triage-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not infer readiness from an unchecked box; read the row and the owning specs.
- Prefer one next task over a broad program plan.

## Required report

Return a compact table of candidate rows with dependency status, exact path fence, focused
verification command, stop condition, and whether an owner decision is required. Name stale or
contradictory rows separately. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

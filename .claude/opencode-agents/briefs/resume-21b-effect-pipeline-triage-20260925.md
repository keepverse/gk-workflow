# Resume 21b — effect-pipeline dependency triage (worktree-local recovery)

## Task

Read the effect-pipeline capability map/specs and `tasks/effect-pipeline-todo.md` **inside this
worktree only**. Identify the first dependency-ready bounded implementation row after the current
head, its exact producer/consumer paths, hard edges, verification boundary, and any owner question
that must remain open. Do not implement or regenerate anything.

## Recovery rule

The predecessor failed because it requested absolute paths outside its worktree. Every path in this
brief is relative to the current worktree. Never read another worktree, the main checkout, or an
absolute path. If a required file is absent here, report the missing file instead of reaching outside.

## Boundary

- Edit only `tasks/reports/resume-21b-effect-pipeline-triage-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not infer readiness from an unchecked box; read the row and the owning specs.
- Prefer one next task over a broad program plan.

## Required report

Return a compact table of candidate rows with dependency status, exact relative path fence, focused
verification command, stop condition, and whether an owner decision is required. Name stale or
contradictory rows separately. End with the runner report block.

## Verification

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

`git diff --check`

# Resume 26 — merged-head gate and release preparation

## Task

Read the repaired `post-merge-check.ps1`, the Phase 0B acceptance report, the legal interop preflight,
and the current manager handoff. Produce a read-only release/gate readiness report: exact environment
variables, clean-branch requirements, expected verdict semantics, known blockers, and the evidence
paths a future manager run must record. Do not run the full gate and do not edit code.

## Boundary

- Edit only `tasks/reports/resume-26-gate-release-prep-20260925.md`.
- No product, test, generated-data, tuning, CI, workflow, or ledger edits.
- Do not claim the current head is green.
- Do not put machine-local paths in the report; use environment-variable names and placeholders.

## Required report

Include the exact command shape, required legal-source variables, profile selection, the branch/clean
preconditions, GREEN/RED/BLOCKED interpretation, and the release smoke/packaging evidence still
missing. End with the runner report block.

## Verification

`git diff --check`

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

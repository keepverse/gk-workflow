# Resume 27 — browser/live proof preparation

## Task

Read the partial `resume-15` browser report, the live-probe standard, the debug-scope guard spec,
and the current handoff. Produce a read-only proof checklist for the next real connected-injector
run: slot/server isolation, real active-match entry, normal-path read-back, browser recovery and
cross-match isolation, cleanup, and evidence hashes. Do not start a game, server, or browser.

## Boundary

- Edit only `tasks/reports/resume-27-browser-live-prep-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not fabricate an active match or treat a response body as persistence proof.
- Keep Game Injector Debug and RPG Server Debug scopes separate.

## Required report

Give the exact prerequisites, command sequence shape, evidence files to retain, and the conditions
that remain blocked without a real injector/live game. End with the runner report block.

## Verification

`git diff --check`

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

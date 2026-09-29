# Resume 27b — browser/live proof preparation (worktree-local recovery)

## Task

Read `docs/contributing/live-probe-standard.md`, `docs/architecture/live-probe/spec-debug-scope-guard.md`,
`docs/DESIGN-Gate.md` if present (otherwise `docs/DESIGN-GATE.md`), and
`tasks/reports/mega-merge-program-resume-20260925.md` **inside this worktree only**. Produce a
read-only proof checklist for the next real connected-injector run: slot/server isolation, real
active-match entry, normal-path read-back, browser recovery and cross-match isolation, cleanup, and
evidence hashes. Do not start a game, server, or browser.

## Recovery rule

The predecessor failed because it tried to read the separate `resume-15` worktree. Never read another
worktree, the main checkout, or an absolute path. The current handoff report already records the
partial browser boundary; use that report and the repository standards in this worktree. If a file is
missing, report it instead of reaching outside.

## Boundary

- Edit only `tasks/reports/resume-27b-browser-live-prep-20260925.md`.
- No product, test, generated-data, tuning, CI, or ledger edits.
- Do not fabricate an active match or treat a response body as persistence proof.
- Keep Game Injector Debug and RPG Server Debug scopes separate.

## Required report

Give the exact prerequisites, command sequence shape, evidence files to retain, and the conditions
that remain blocked without a real injector/live game. End with the runner report block.

## Verification

`git diff --check`

`python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`

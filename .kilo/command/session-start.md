---
description: "Establish and record this session's boundary (mode, branch, one problem, owned paths) before editing; check other sessions for crossing."
---

Establish the boundary for this session before the first edit, then record it. Policy:
`docs/contributing/session-boundary.md`. Read it first, then do exactly this.

## 1. Read the current state

- Every `tasks/sessions/*.json` (skip `_template.json`).
- `git branch --show-current`, `git worktree list`, `git status --porcelain`.
- `python scripts/session-boundary-check.py` — a clean run is the precondition for editing. Report any
  drift it finds; do not work around it.

## 2. Check for crossing

For each other **active** record, compare its `paths` and `branch` with what this session is about to
touch. If any overlaps in `direct` mode, or two records claim the same branch without a worktree,
**stop and tell the owner** before editing. Options: narrow this session's `paths`, or take a
worktree.

## 3. Ask the owner (use the `question` tool)

Ask these and record the answers verbatim:

1. **Problem** — the one problem this session solves (a session is one problem, not one program).
2. **Mode** — `direct` (default) or `worktree`. Recommend `direct` unless the session is long, risky,
   or overlaps another active session.
3. **Branch** — default: the current branch (one shared integration branch). Offer a per-session
   branch when the session should not land until reviewed.
4. **Paths** — the exact path globs this session owns and may commit. Propose them from the problem
   and show the owner the list. This is the load-bearing field.

Do not invent an answer to any of these. If the owner is unavailable, default mode to `direct`,
scope to the files already named by the task, and say in the record that it was inferred.

## 4. Write the record

Create `tasks/sessions/<session>.json` from `tasks/sessions/_template.json`. `session` is
`<program>-<yyyymmdd>-<4hex>`. Commit it with the session's first change, with `git commit` with
explicit `paths`. Keep churning runtime detail (current task, next task, pending command) in
`.kilo/sessions/<session>.json` (gitignored), never in the tracked record.

## 5. Then work

- Edit and commit only inside `paths`. `git status` will show other sessions' dirty files — leave
  them alone. Never `git stash`/`checkout`/`reset` around another session's work.
- Never `git add -A` / `git commit -a`.
- On close, set `status` to `merged` or `abandoned` in a new commit (never amend).

Report at the end: the session id, mode, branch, the owned `paths`, and the drift-check result.

# Worktree cleanup ownership finding — unowned `.commandcode` paths

**Date:** 2026-09-25
**Status:** **OPEN OWNER ROUTING BLOCKER**

## Finding

The main checkout has nine dirty paths, but they are not all owned by
`worktree-cleanup-20260925`.

The cleanup session record claims these six paths:

- `tasks/sessions/worktree-cleanup-20260925.json` (**new** in the current cleanup lane; not yet committed)
- `gk-core/scripts/worktree_cleanup_core.py` (**new** in the current cleanup lane; not yet committed)
- `gk-core/scripts/mark-worktree-cleanup.py` (**new** in the current cleanup lane; not yet committed)
- `gk-core/scripts/cleanup-worktrees.py` (**new** in the current cleanup lane; not yet committed)
- `gk-core/scripts/test_worktree_cleanup.py` (**new** in the current cleanup lane; not yet committed)
- `docs/contributing/worktree-cleanup.md` (**new** in the current cleanup lane; not yet committed)

The checkout also has these three dirty paths, and a scan of all 221 tracked session JSON records
found no active or historical session fence that claims them:

- `.commandcode/settings.json` — untracked;
- `.commandcode/taste/taste/taste.md` — modified;
- `.commandcode/taste/workflow/taste.md` — untracked.

The `.commandcode` tree is not ignored. The modified taste file contains owner-preference additions;
the other two files are local configuration/workflow artifacts. Their origin is not established by
any current session record.

## Consequence

`worktree-cleanup-20260925` cannot truthfully be described as owning the whole dirty checkout. The
manager cannot run a clean merge or `post_merge_check.py` while these paths remain unresolved, and
must not solve the ambiguity with `git stash`, `git reset`, `git clean`, or a broad delete.

## Required owner routing

The owner must identify whether the three `.commandcode` paths are:

1. intentional local configuration that should remain outside version control and be ignored by a
   narrowly approved rule; or
2. a tracked assistant/tooling change that belongs to a named session and must be reviewed/committed
   through its own fence; or
3. disposable local artifacts that may be removed under an explicit owner instruction.

Until that decision is recorded, the paths remain untouched and the integration gate remains
`BLOCKED` independently of the cleanup tool lane. The cleanup session may finish its own six-path
work, but its completion does not authorize a merge while these three paths remain unowned.

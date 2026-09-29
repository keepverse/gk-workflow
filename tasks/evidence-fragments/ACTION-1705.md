# Housekeeping: action-todo.md's stale A8-reaction-lane line

**Already closed — no edit made.** `tasks/action-todo.md` has grown since `backlog-clear-plan.md` was
written (2026-08-31), so the line-1705 citation is stale by line number, but the underlying content is
independently confirmed already fixed:

- Grepped the current file for the exact stale text (`"reaction lane"`, `"waits on timeline B6"`): the
  only surviving hit (`:1291`) is a summary list item naming A8 as one of several *closed* blockers, not
  the original open claim.
- `tasks/action-todo.md:2947` already carries `- [x] **A8's reaction lane** — **CLOSED 2026-08-31 by its
  own evidence...** it ended up **not** needing this lane at all; it ships as a stance with
  riposte-on-release, not a reaction` — the exact correction `backlog-clear-plan.md` asked for, dated
  the same day the plan itself was written.

**No edit made.** `tasks/action-todo.md` is also fenced by the active `summoner-convergence-lane-a2-20260919`
session (its own worktree) — moot regardless, since there is nothing left to change.

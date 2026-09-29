# BCU4.5 — file `roster-balance`'s handed-off species findings in `creature-seed`

The `cmdc/lane-c` fence had gone **stale**, not active — the same class of premise the P11 gate carried.
Checked rather than assumed, then filed the findings as a real task instead of dropping them.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The fence is clear | `git merge-base --is-ancestor cmdc/lane-c HEAD` | exit 0 — lane-c is an ancestor of HEAD (came through the orchestrator's `features/mega-merge` merge) | — |
| No other session holds a dirty copy | `git -C <each worktree> status --short -- tasks/creature-seed-todo.md` | every worktree reports clean | — |
| Findings filed as a real task, not dropped | `git diff tasks/creature-seed-todo.md` | new **RB-H1** row with acceptance, verify, owner and scope | `tasks/creature-seed-todo.md` |
| The sharper half recorded first | `rg -n "VOTED_FIELDS\|PostureBalanceMetric" tasks/creature-seed-todo.md` | the metric-blindness finding (`posture: "unresolved"` invisible to both metrics) is stated as the reason the axis readings are currently unfalsifiable | same file |
| Source citations resolve | `python scripts/audit-doc-citations.py --strict --scope tasks/creature-seed-todo.md` | 0 HIGH | — |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('tasks/creature-seed-todo.md','tasks/backlog-clean-up-todo.md') -Session bcu8"` | see commit body | — |

No code changed: the deliverable is the filed task. Counts (65/252, 257‰, 973‰, 12 rows, 19 GAP rows)
are readings from `roster-balance`'s one real run and are quoted as such; RB-H1 explicitly requires
re-measuring and dispositioning each axis rather than treating them as constants or defects.

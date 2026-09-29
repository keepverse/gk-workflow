# BCU8.9 — one linked finding: the missing-reader channel families

Wrote the merged write-up into **both** programs' todos, each pointing at the other, so neither
re-discovers the list as its own new gap. The two audits already agreed; the task was to make that
agreement visible in one place each.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One finding, recorded in both programs | `git diff tasks/battle-derived-wire-todo.md tasks/class-system-todo.md` | new "Cross-program finding — the missing-reader families (W16, R1–R4)" section + a linked "External" row, same channel list, mutual pointers | those two files |
| Both readings cited, not restated from memory | `rg -n "W16" docs/research/battle-derived-wire-audit-2026-09-16.md`; `rg -n "6 of 48" tasks/class-system-todo.md` | audit `:433,440-443`; P9.0 live *6 of 48 aptitude-fed families, 18 of 486 edges, 3.7%* (`:665`) | audit doc; class-system todo |
| Cause read from code, not inferred | `rg -n "Explicit non-goals" tasks/battle-derived-wire-plan.md` | `:62` — building the reader here is refused by that plan, which is why the inventory and the reader live in different programs | `battle-derived-wire-plan.md` |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('tasks/battle-derived-wire-todo.md','tasks/class-system-todo.md') -Session bcu8"` | see below | — |

No code changed: the deliverable is the finding. `resource.efficiency` was the one family W16 and
P9.0 spelled differently (`resource.efficiency.*` vs `resource.efficiency`); the write-up uses P9.0's
census spelling and names the family, not a count.

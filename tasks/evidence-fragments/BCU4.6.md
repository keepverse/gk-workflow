# BCU4.6 — F4/F5 re-checked, F1 routed (all three clauses met)

Was "2 of 3 done"; the third clause was blocked on the `cmdc/lane-c` fence on
`tasks/creature-seed-todo.md`, which had gone **stale** — checked, then filed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| F4 re-confirmed against shipped DTOs | `rg -n "class CreatureMintSpec" -A 12 gk-core/src/FusionRpg.Contracts/CreatureDtos.cs` | no `Level` property among its 10 — the 2026-09-07 finding holds | `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs:58-70` |
| F5 re-confirmed | `rg -n "public .*Roll\(" -A 3 gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs` | `(SummonBannerDef banner, ElementTypeId? focusElement, int count, PityState pity, SeededRng rng)` — no `poolFilter` | `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs:61-62` |
| The F1 fence is stale, not active | `git merge-base --is-ancestor cmdc/lane-c HEAD` | exit 0; every worktree clean for that file | — |
| F1 routed as a real task with owners | `rg -n "TB-H1" tasks/creature-seed-todo.md` | module 4 `threat-band` + module 7 `classify-pipelines`, live `721 of 906` reading, acceptance requiring a real six-domain run to close party-dungeon F1 | `tasks/creature-seed-todo.md` |
| It is not over-claimed | `rg -n "thetaOffset" tasks/creature-seed-todo.md` | the row says explicitly that filling `threatBand` does **not** make `thetaOffset` live (zero `src/` consumers) | same file |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('tasks/creature-seed-todo.md','tasks/backlog-clean-up-todo.md') -Session bcu8"` | see commit body | — |

No code changed: F4/F5 are re-confirmations and F1's deliverable is the routed row. Counts
(`721 of 906`, `10 properties`) are readings, quoted as such and not pinned.

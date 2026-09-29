# Evidence — rpg-simulator RS-F1 (the sanctioned award step, written where the wrong sentence lived)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS-F1, acceptance's FIRST branch: *"either the simulator's own spec names
`/api/test/seed-souls-demo` as the sanctioned award step (an erratum on `rpg-simulator-idea.md` §5.3) …"*.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The wrong sentence is corrected where it lived, not only in a todo | `grep -n -A3 "Scenario \`first-session-forward\`" docs/architecture/rpg-simulator-idea.md` | §5.3's step now reads *"award souls through the sanctioned seeding surface `POST /api/test/seed-souls-demo`"*, and the paragraph beneath it (which already named that route) is consistent with the step instead of contradicting it | `docs/architecture/rpg-simulator-idea.md` §5.3 |
| The erratum carries the cause, read from the code | `grep -n "MapSouls\|never generic" gk-core/src/FusionRpg.Server/SoulEndpoints.cs` | `MapSouls` (`:9`) maps exactly two GETs; `:6` says *"Spends are feature-owned (summoning etc.), never generic"*; the award write is the SIM surface at `:29` | `gk-core/src/FusionRpg.Server/SoulEndpoints.cs` |
| Every citation in the erratum resolves | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**, `D1 file does not exist 683 (0 HIGH)`, `D3 ambiguous basename 56 (0 HIGH)` — no HIGH at all on this head | — |
| The residue is carried, not dropped | read: the new **RS-F25** row | whether the soul economy should grow a *player-facing* award route is filed with its owner (the soul-economy program / the resource registry) and its acceptance | `tasks/rpg-simulator-todo.md` |

**What the erratum says, in one line:** souls are earned by gameplay (`SoulEarnPolicy.Reasons`) and spent by
feature-owned routes; the scenario's sanctioned award step is the SIM seeding surface, which performs the **real**
`RpgStore.AwardSouls` write with reason `seed` — the reason the RS4 honesty guard allowlists it by name. Owner
ruling D3 (b) stands: an unreachable condition is the finding, not a licence for a new route.

**What is NOT closed by this row:** a player-facing award route. It would be a new economy faucet, so it is a
resource-registry decision (`docs/architecture/empire-resource-ssot.md` §3), and RS-F1's erratum deliberately
answers only the simulator's half. Carried as RS-F25.

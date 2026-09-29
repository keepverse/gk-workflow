# EP4.16 - `ActorIndexFor(SaveId, EmpireId)`: Zomboss's Theta through the existing composer

`ServerPowerIndexProvider.ActorIndexFor(save, empire)` reads that empire's own commander level
(`RpgStore.CommanderLevelOf`, SP7.3's one seam), builds `ActorLadderSnapshot(level, 0, 0)` and composes it
through the SAME `PowerIndexComposer.ActorExplain` the player's Theta uses. A wiring gap closed: no new
`f(level)`, no new curve. Commit `@EP4.16` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The read composes `ActorLadderSnapshot(CommanderLevelOf(save, empire), 0, 0)` through `ActorExplain` | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PowerIndexProvider"` | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3` - `ActorIndexFor_composes_the_empires_own_commander_level_through_the_one_ladder` asserts the composer's own answer at level 12 and that it exceeds level 1 | `gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs`, `gk-core/tests/FusionRpg.Server.Tests/PowerIndexProviderTests.cs` (new) |
| The existing `ActorIndex(player)` result is byte-identical | same | `Passed: 3` - `ActorIndexFor_the_human_empire_is_the_existing_player_read_unchanged` (same `kind='player', type_id=0` row: `ActorIndexFor(save, Dave) == ActorIndex(ctx{PlayerId=save})`, both > 0) | same |
| A reflection/grep test finds no new `f(level)` | same | `Passed: 3` - `ActorIndexFor_introduces_no_private_curve` scans the method body for `_store.CommanderLevelOf`, `ActorLadderSnapshot(`, `PowerIndexComposer.ActorExplain(` and asserts no `Math.` and no `*`/`^` in it | same |
| `guard-power` is green | `python gk-core/scripts/guard-power.py` | `POWER GUARD OK — one ladder, pin holds, no private f(level)` (exit 0) | - |
| Scoped verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs','gk-core/tests/FusionRpg.Server.Tests/PowerIndexProviderTests.cs' -Session empire-progression-4"` | `EXIT=0` - dal guard OK, server `Passed! - Failed: 0, Passed: 793, Skipped: 0, Total: 793` | - |

**NOT proved:** Zomboss's budget is not yet READ by anything — EP4.17 lands the pool read and EP4.18 the
wire that spends it. The interface (`IPowerIndexProvider`) is unchanged: the method is on the Server
provider, the only implementation that can answer it, so no stub is forced to fabricate an answer.

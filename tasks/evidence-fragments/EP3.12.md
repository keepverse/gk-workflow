# EP3.12 — Casualty: a fallen commander member is detached and set `Recovering`

Commit `@EP3.12` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-legion-commander.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A commander member at zero hp is detached, and its specimen is set `Recovering` (test 6) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCasualty"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (`ApplyCommanderCasualtiesUnlocked` + its call site in `CommitWorldTurn`), `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCasualtyTests.cs` (new) |
| The same read through the normal paths, not the pass's return value | same | `GetUniqueActor(...).Phase == "Recovering"` and `LoadWorldState(...)` has no `Commander` member — both read back from the store | same |
| The rule fires in a REAL siege, and only there | same | `A_commander_member_that_dies_in_a_siege_...` runs a committed `assault` into a Zomboss-held district through `CommitWorldTurn`; `A_commander_member_that_survives_the_siege_is_left_alone` is the same scenario with a surviving commander and moves nothing | same |
| A comment names `injury-tiers` as the replacement | `rg -n "injury-tiers" gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | 1 hit, in `ApplyCommanderCasualtiesUnlocked`'s own doc comment, naming `deployment-hierarchy`'s `injury-tiers` as the program that owns wound/kill semantics | — |
| Row Verify line | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"` | `Passed! - Failed: 0, Passed: 25, Skipped: 0, Total: 25` | — |
| No golden moved (H1) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldWaveOne"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` — the 20-turn scenario builds no `Commander` member, so the pass returns its input world unchanged (`casualties.Count == 0`), leaving the diff and the stored hash byte-identical | — |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','gk-core/tests/FusionRpg.Data.Tests/WorldTurnCasualtyTests.cs') -Session empire-progression-3` | guards `dal` OK + `test-substrate` OK; the Data half runs through the sharded runner, which printed `444 + 40 + 83 + 1145` tests with **no failure line** and then exited 1 with an **empty** exit code — the known TVB-F6 misreport, whose trx directory the runner deletes. Re-run as the union filter the four shards partition (below) | — |
| The Data half of that boundary, re-run because the sharded runner's exit code is empty | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 1737, Skipped: 0, Total: 1737, Duration: 11 m 18 s`, exit 0 (1733 before this row's 4 new tests) | — |

**Design, and the one consequence a later reader needs.** The pass runs INSIDE `CommitWorldTurn`'s transaction, after `TurnEngine.Step`
and **before** the world diff and the state hash, so the detached member is gone from both the persisted graph and the hash the log
stores. It takes two worlds on purpose: a death has two shapes and only the pair sees both — `BuildSideOutcome` REMOVES a member
whose new wounds reach its `Hp` (the ordinary path), while a member that entered already at zero effective HP is kept and never
fielded. Only a `Commander` member with a non-blank `InstanceId` is considered, so a `Fighter` (already handled by the survivor
list) and a `Bearer` (cargo, not a specimen) are untouched. It writes the **phase only** — never a `rpg_unique_actor_recovery`
row — because a wound count is bookkeeping `injury-tiers` owns. **Consequence, named rather than discovered later:** a siege
casualty is therefore `Recovering` with no recovery row, so `PerformRitual` refuses it as `recovery.missing` until `injury-tiers`
lands. That is the interim rule's honest shape, not a bug to patch here.

**Not proved** (out of fence / other owners):
- `injury-tiers`' real wound/kill semantics, and any recovery count or timer: `deployment-hierarchy`'s.
- Whether a `Recovering` (no recovery row) specimen renders correctly on the FE: `web/**` is outside this lane's fence.
- A casualty in a non-siege battle: no other battle kind damages members today (`DistrictAssaultResolver` refuses every
  non-district kind), so there is nothing else to cover yet.
- A zombie-side (Zomboss) commander casualty: nothing creates a Zomboss specimen here, so the same rule is untested for that side
  even though it is written side-agnostically.

**Finding routed with this row (for the next siege reader).** Committing a district assault through `RpgStore` was not
exercised by ANY Data test before this one: `RpgStore.WorldTurnHubInputsForUnlocked` reads `AptitudeTuningHub.Tuning`, which
`gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs` does not configure, so the first Data-level siege throws
`AptitudeTuningHub` unconfigured until the test configures it itself. `WorldTurnHubInputsForTests` had the same need and solved
it locally, so the assembly's bootstrap still has the gap. Filed as **TVB-F16** in `tasks/test-verification-boundary-todo.md`
(the test substrate's owning program) in this same commit, with the one-line remedy; this test keeps its local configuration
until that lands.

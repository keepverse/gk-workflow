# EP4.15 - the Empty guards become level reads; the empire rides the species broadcast

`RpgStore.Aptitudes.cs`: both `empire != Dave -> Empty` branches are gone; each ask reads the asker's own
level through `SpeciesLevelOf`/`SpeciesLevelOfUnlocked` (EP4.13's one reader). `AptitudesUpdatedDto` gains
the additive `empire` field and `EventIngest.BroadcastProgressionAsync` fills it from the dirty. Committed
with EP4.14. Commit `@EP4.14,EP4.15` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `RpgStore.Aptitudes.cs:229-233` and `:258-267` read `SpeciesLevelOf` | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore"` | `Passed! - Failed: 0, Passed: 19, Skipped: 0, Total: 19` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs` |
| test 3: a never-credited AI species resolves Empty | same | `Passed: 19` - `A_Zomboss_empire_ask_never_reads_the_players_species_level_baseline` (Dave 21 > 0, Zomboss 0, and `SpeciesLevelOf(zomboss) == 1`), plus `The_baseline_call_itself_honours_the_empire_it_accepts` | same |
| test 4: an AI species above level 1 resolves its plan's distribution at that level | same | `Passed: 19` - `An_AI_empires_species_above_level_one_resolves_its_own_levels_distribution`: the same species at 21/4 in opposite empires of two saves; each ask follows its OWN row | same |
| `AptitudesUpdatedDto` gains the additive `empire` field | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionPowerIndexReload"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` - `A_zomboss_species_level_change_names_the_empire_it_credited` reads `empire == "zomboss"` off the wire; `A_human_species_level_change_leaves_the_empire_field_null` proves the pre-R1 senders are byte-unchanged in meaning | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/src/FusionRpg.Server/EventIngest.cs` |
| T1-T4 each have a test; T4 is order-independent against a match edge | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesAllocationCacheTrigger"` | `Passed! - Failed: 0, Passed: 10, Skipped: 0, Total: 10` - T1 session start, T2 reconnect, T3 the `AptitudesUpdated` broadcast (now the empire-carrying one), T4 the key-set edge + the match-edge exception | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs` |
| Scoped verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs','gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs','gk-core/src/FusionRpg.Server/EventIngest.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs','gk-core/tests/FusionRpg.Data.Tests/SpeciesProgressionTests.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs','gk-core/tests/FusionRpg.Data.Tests/AllocationStoreTests.cs','gk-core/tests/FusionRpg.Server.Tests/ProgressionPowerIndexReloadTests.cs' -Session empire-progression-4"` (pwsh) | `EXIT=0` - dal + test-substrate OK; data 4 shards / 1747 tests / no overlap; server `Passed: 790` | - |

**NOT proved:** the injector's own handling of the new `empire` field beyond `scope` — `RpgClient`'s
`AptitudesUpdatedScopeDto` reads only `scope` today and needs no change (additive field), so no injector
edit was made. The FE consumers of `AptitudesUpdated` were not read this session.

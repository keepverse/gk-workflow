# EP4.14 (R1) - both species XP paths credit the side's empire

`RpgStore.Progression.cs`: a species award now resolves its owner from the side it was fielded on
(`KillAttribution.EmpireOf(SpeciesSideOf/`FactSideOf`)`) — a zombie species credits
`(SaveId, EmpireId.Zomboss)`, a plant species the human empire, and an empire the save does not carry
credits nothing rather than minting a row (`SpeciesOwnerForSideUnlocked` returns null → skip). Committed
with EP4.15. Commit `@EP4.14,EP4.15` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| test 8: a zombie spawn AND a zombie run completion each grow Zomboss's row and never the human's; a plant grows the human's; the human's old zombie rows are never rewritten | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` - `A_zombie_spawn_and_a_zombie_run_completion_credit_Zomboss_while_the_humans_rows_stay_history` seeds a level-5 human zombie row, plays both paths, asserts Zomboss >= 2, the human zombie row still level 5 / 0 xp, the human plant >= 2, Zomboss has no plant row | `gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs` |
| test 5: a replayed completion credits once | same | `Passed: 7` - `A_replayed_completion_credits_Zomboss_species_once` asserts level, xp and revision identical after the identical `MatchEnded` fact replayed | same |
| test 9: a run with no resolvable save credits nothing and is reported | same | `Passed: 7` - `A_zombie_fact_for_an_unresolvable_run_credits_nothing`: the append returns `Progression` empty (the caller's own report, SE4.21's shape) and no Zomboss row exists | same |
| The pre-existing zombie-species test follows R1 | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesProgression"` | `Passed! - Failed: 0, Passed: 17, Skipped: 0, Total: 17` - `ZombieSpawned_levels_Zomboss_empires_species_row_not_the_humans`; the human's row is asserted NULL | `gk-core/tests/FusionRpg.Data.Tests/SpeciesProgressionTests.cs` |
| Empire-side rule still holds, now with Zomboss crediting | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11` - `A_human_owned_zombie_species_never_moves_the_humans_empire` asserts NO human empire row and Zomboss's own empire level > 1 | `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` |
| Scoped verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs','gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs','gk-core/src/FusionRpg.Server/EventIngest.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs','gk-core/tests/FusionRpg.Data.Tests/SpeciesProgressionTests.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs','gk-core/tests/FusionRpg.Data.Tests/AllocationStoreTests.cs','gk-core/tests/FusionRpg.Server.Tests/ProgressionPowerIndexReloadTests.cs' -Session empire-progression-4"` (pwsh) | `EXIT=0` - dal + test-substrate OK; data `TEST-SHARDED OK: 4 shards, 1747 tests, no overlap`; server `Passed: 790` | - |

**NOT proved:** the live lawn/injector path (a real zombie spawn crediting Zomboss end to end) is a live
probe, out of this lane's scope. **Fixtures note:** the new reads go through the store's wide empire read,
since the public `GetRpgActor` resolves only the human empire.

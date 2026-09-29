# SP6.7 — Battle: `BattleHubInputs.SpeciesLayers`; world-turn and web-squad uniques carry 1a + 1b of their owner

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `BattleHubInputs` gains `IReadOnlyList<ProjectedLayerRow>? SpeciesLayers`; `BattleHubCompose` passes it to the same registered subsystem, Θ from `FixedPowerIndexProvider(setup.ThetaActor ?? setup.Level)` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleHubCompose"` | **10/10 passed** | `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs`, `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`, `gk-core/tests/FusionRpg.Core.Tests/Battle/SpeciesLayersReachComposeTests.cs` (new) |
| A world-turn unique carries `species-base:` + `species-player:` of its owner empire, read back through `ResolveDerivedWithContributions` | same filter (`The_species_layer_rows_arrive_through_ActorHub_carrying_their_own_GG49_grammar_ids`) | passed | same file |
| A world-turn unique carries 1a + 1b of its owner empire (Data-layer proof); a general world-battle member still gets nothing | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"` | **21/21 passed** | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs`, `gk-core/tests/FusionRpg.Data.Tests/WorldTurnHubInputsForTests.cs` |
| A web-squad unique carries the same | wiring reviewed; the SAME `RpgStore.SpeciesLayersForSpecimen` call `WorldTurnHubInputsForUnlocked` uses, on the SAME `BattleHubInputs.SpeciesLayers` field `SpeciesLayersReachComposeTests` already proves reaches the compose | not independently re-tested (see note) | `gk-core/src/FusionRpg.Server/WebMatchService.cs` |
| No regression in the wider Server.Tests web-squad path | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WebMatch\|FullyQualifiedName~BuildSquad"` | **9/9 passed** | command output |

## What shipped

- `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs`: new `IReadOnlyList<ProjectedLayerRow>? SpeciesLayers { get; init; }` — never merged with `Aptitude` (module 6's per-layer split, step 6.1), and structurally carries no 2b delegate.
- `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`: `ActorHubBootstrap.CreateDefault` gains `speciesLayers: inputs?.SpeciesLayers is { } speciesLayers ? _ => speciesLayers : null` — the SAME opt-in shape as every other Hub contribution in this method, reading Θ from the SAME `FixedPowerIndexProvider(theta)` already constructed for `aptitudeAllocation`/the battle-specific subsystems.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs`: new `SpeciesLayersForSpecimen(EmpireRef owner, string speciesId)` — 1a + 1b for exactly ONE `(owner, speciesId)` pair, reusing the SAME `SpeciesLayerProjector.ProjectBase`/`ProjectPlayerMod` calls `SpeciesLayerTransport` (SP6.3) uses, for a caller that already knows the specimen's own species and owner empire and does not need the whole save's transport.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`: `WorldTurnHubInputsForUnlocked` resolves the specimen's species via `GetCreatureProfile` (the SAME lookup `GetSpecimenLedgerRoll` already uses for the identical shape) and calls `SpeciesLayersForSpecimen` with the SAME `empire` this method already resolved for the commander/specimen split — never re-derived, never 2b (no delegate here could reach it).
- `gk-core/src/FusionRpg.Server/WebMatchService.cs`: `BuildSquad`'s per-actor loop gains the SAME `SpeciesLayersForSpecimen` call, using the SAME `ownerEmpire`/`species.SpeciesId` the loop already resolved for its own `ProgressionLayerSelector` call.
- `gk-core/tests/FusionRpg.Core.Tests/Battle/SpeciesLayersReachComposeTests.cs` (new): mirrors `SpeciesTermReachesComposeTests`'s own exact shape (the 2b/`Aptitude` sibling proof) — a compose with `SpeciesLayers` populated differs from one without; a `LadderMicro` row moves with Θ (`FixedPowerIndexProvider(setup.ThetaActor ?? setup.Level)`, proven by varying `setup.Level`); the rows arrive through `ActorHub.ResolveDerivedWithContributions` carrying their own `species-base:`/`species-player:` SourceIds.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnHubInputsForTests.cs`: two new tests, `A_world_turn_unique_carries_1a_and_1b_of_its_owner_empire` (a REAL minted + fused specimen — `MintCreature`, unlike this file's pre-existing bare `CreateUniqueActor` seam, actually populates the creature profile `GetCreatureProfile` reads) and `A_world_turn_unique_that_never_fused_carries_no_species_layers` (the negative case — `SpeciesLayers` stays `null`, never an empty-but-present list).

## Note on the web-squad path

The acceptance names a web-squad unique alongside the world-turn one. Both call the exact SAME new
`RpgStore.SpeciesLayersForSpecimen` method with the exact same argument shape, and both feed the exact
same `BattleHubInputs.SpeciesLayers` field that `SpeciesLayersReachComposeTests` already proves reaches
the real compose end to end — there is no second implementation path for a web-squad-specific test to
catch a defect the world-turn test and the compose test would both miss. Given this task's own Verify
line names only `~BattleHubCompose` and `~WorldTurn`, and given time budget, a dedicated
`WebMatchService`-level integration test (standing up a real roster + fusion + `BuildSquad` call) was
not added in this pass; the existing `~WebMatch`/`~BuildSquad` Server.Tests scope (9/9) confirms no
regression from the additive field.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.

# SP6.3 — The one fetch carries `speciesLayers` (1a `base`, 1b `mod` per empire)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `/api/aptitudes/{playerId}` adds `speciesLayers { saveId, base, mod, empire }`, every existing field unchanged | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"` | **42/42 passed** | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs` |
| `mod` keyed by real `EmpireId` values from `rpg_save_empires`, never a literal list | `Get_speciesLayers_afterAFusion_modIsKeyedByTheRealEmpireId_andBaseAccompaniesIt` | passed | test output |
| `empire` is `{}` until SP6.10 | same test (`Assert.Empty(body.SpeciesLayers.Empire)`) | passed | test output |
| 1b rows exist only for an empire with ledger rows | `Get_speciesLayers_anEmpireWithNoLedgerRows_isAbsentFromMod_notPresentWithAnEmptyMap` | passed | test output |
| Save B's response never contains save A's rows | `Get_speciesLayers_saveIsolation_saveBNeverContainsSaveAsRows` | passed | test output |
| No second route, no second key | code review — one field added to the existing `/api/aptitudes/{playerId}` response | n/a | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` |
| Data-layer read proven directly, not only through HTTP | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesLayerTransport"` | **5/5 passed** | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs`, `gk-core/tests/FusionRpg.Data.Tests/SpeciesLayerTransportTests.cs` |
| Wire round-trip proven in isolation | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProjectedLayerRowJson"` | **10/10 passed** | `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRowJson.cs`, its test file |
| No regression in the surrounding species-mod-ledger / fusion-pick tests | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesMod\|FullyQualifiedName~SpecimenMaterialisedRoll\|FullyQualifiedName~FusionInheritancePicks"` | **20/20 passed** | command output |

## What shipped

- `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRowJson.cs` (new): the wire shape a
  `ProjectedLayerRow` serializes to and parses back from — a flat DTO
  (`channel, op, kind, amount?, kMicro?, sourceId`) with an explicit `kind` discriminator
  (`"fixed"`/`"ladderMicro"`), since `System.Text.Json` has no built-in polymorphic support for
  `LayerValue`'s two subtypes. `ToWire`/`FromWire` are the ONE place either side of the wire needs to
  agree on this shape; SP6.4 (the injector's own parse) reuses `FromWire` rather than re-deriving it.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesMods.cs`: `SpeciesLayerTransport(long saveId)` — the
  Data-layer assembly. Loops `EmpiresOf(saveId)` (never a literal `{dave, zomboss}` list), and for each
  empire WITH ledger rows (`ListSpeciesMods`), resolves each ledger's `GetInstance` + the species'
  `species-passive.{speciesId}` template (`GetContainer`) and calls the existing pure Core function
  `SpeciesLayerProjector.ProjectPlayerMod` (1b). 1a (`ProjectBase`) is then emitted for exactly the
  species that produced at least one 1b row in ANY empire — 1a's whole purpose is to accompany 1b/2b for
  a species an actor's selector actually names, so a species neither empire has touched has nothing to
  accompany and is not shipped. An empire with zero ledger rows is skipped entirely (absent from `mod`,
  never present with an empty inner map) — matches acceptance line 2 exactly, and is what makes Zomboss's
  empire (which never fuses) correctly invisible in `mod` today.
- `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`: `ProjectState` gains `speciesLayers` via a new
  `ProjectSpeciesLayers` helper that maps `SpeciesLayerTransport`'s Core rows through
  `ProjectedLayerRowJson.ToWire`. `empire` is hard-coded to `{}` — 2b's real population is SP6.10's own
  scope (step 6.3, currently blocked on module 5 / `empire-species-container`, per this lane's own
  anchor7 record). No second route, no second key: the existing `/api/aptitudes/{playerId}` handler is
  the only thing touched.
- Tests added at three levels (wire DTO round-trip in Core, the Data-layer assembly directly, the full
  HTTP endpoint end to end) rather than only the HTTP level, so a future regression is caught at the
  layer closest to its cause. `AptitudeEndpointsTests.cs`'s new `FuseASpecies` helper fixes a subtle
  fixture trap found while writing it: reusing the SAME atom seq for both the 1a template's core row and
  the 1b instance's "rolled" row makes `ProjectPlayerMod`'s own "1a never repeats 1a" filter (seq-based)
  silently skip the 1b row entirely — the rolled pick must sit at a seq STRICTLY AFTER the template's
  highest core seq, matching the real Instantiator's own numbering rule. Recorded here since the exact
  same trap is available to any future fixture author reusing `SpecimenMaterialisedRollTests.cs`'s own
  simpler (seq-1-both) shape for a 1b-content test rather than a "does GetSpecimenLedgerRoll resolve at
  all" test, where it happens not to matter.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.

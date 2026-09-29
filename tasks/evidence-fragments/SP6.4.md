# SP6.4 — The injector cache: parse, wholesale replace, invalidate; selector-driven rows; triggers 1-3 extended

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `RpgClient`'s one fetch parses `speciesLayers`; `CheatState.ApplySpeciesLayers` replaces the whole cache and invalidates | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger"` | **5/5 passed** | `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `gk-fusion/src/FusionRpg.Injector/CheatState.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` (new) |
| The delegate gives a general `Species` answer 1a+1b of its side's empire, a `Specimen` answer 1a+1b of its owner empire, never 2b; a `None` answer gets nothing | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerSourceTests"` | **12/12 passed** | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesLayerSource.cs` (new), its test file |
| Triggers 1-3 extended to assert `speciesLayers` | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesAllocationCacheTrigger"` | **12/12 passed** (10 pre-existing + 2 new) | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs` |
| Whole `FusionRpg.Guard.Tests` project — no regression elsewhere | `dotnet test gk-core/tests/FusionRpg.Guard.Tests` | **448/449** (the one failure, `PlayerSpeciesMaterialiseCallerGuardTests.The_rolled_species_instance_reaches_a_composer`, is the PRE-EXISTING SP3.6 regression already recorded this program — see `tasks/evidence-fragments/SP3.6.md` addendum; unrelated to this task, untouched by it, and the "Guard.Tests add-only" rule forbids editing that file here) | command output |
| No regression in `SpeciesAllocationSource`/`ActorHub` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocationSource\|FullyQualifiedName~SpeciesLayerSource\|FullyQualifiedName~ActorHub"` | **531/531 passed** | command output |

## What shipped

- `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesLayerSource.cs` (new): the `ctx -> ProjectedLayerRow[]`
  resolution, mirroring `SpeciesAllocationSource`'s own established shape (pure, fully provable with
  fake resolvers, no I/O). The species lookup `(Side, TypeId) -> speciesId` is IDENTICAL for a general
  and a Bound specimen (both read the same live `(Side, TypeId)` through one `LawnElementIndex`-backed
  resolver); only WHICH EMPIRE the 1b term comes from differs — side-derived for a general, owner-derived
  for a Bound specimen (`layer-source-selector` rule 3 / C10, never `ctx.Side`). Routes through
  `ProgressionLayerSelector` (module 1) for the general/specimen split, matching the spec's own
  vocabulary; a `None` owner (or an unconfigured/absent species lookup) returns an empty list.
  Structurally cannot reach 2b: the type carries no delegate that could — the `Species` arm's own doc
  comment marks it as the future SP6.10 extension point, the `Specimen` arm has none.
- `gk-fusion/src/FusionRpg.Injector/CheatState.cs`: two new static caches (`_speciesLayersBase`,
  `_speciesLayersMod`), `ApplySpeciesLayers` (wholesale replace both + `Stats.Invalidate()`, mirroring
  `ApplySpeciesAllocations`'s own contract exactly), and the `SpeciesLayer` instance — constructed with
  the SAME `ResolveSpeciesLookup`/`ResolveBoundInstanceId`/`TryGetSpecimenEmpire` delegates
  `SpeciesAllocation` already uses, never a second copy of that plumbing. Wired into the lazy
  `ActorHub` property's new `speciesLayers:` argument (built by SP6.2).
- `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`: `RefreshCommanderAllocationAsync` — the SAME one fetch that
  already parses `shares`/`species` — now also parses `speciesLayers.base`/`.mod` (never `.empire`,
  which stays unread until SP6.10) into `ProjectedLayerRow`s via the shared `ProjectedLayerRowJson.FromWire`
  converter (SP6.3), and calls `CheatState.ApplySpeciesLayers`. A malformed row is skipped rather than
  thrown past the call, so one bad row from the server never drops every other row in the same refresh.
- `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` (new) and an extension to
  `SpeciesAllocationCacheTriggerTests.cs` (`All_three_triggers_also_reach_speciesLayers_through_the_same_one_fetch`):
  source-text scans, the SAME idiom the sibling species-allocation cache already established —
  `RpgClient` has no HTTP seam to mock and the Injector test project is not in CI. Together they prove:
  wholesale replace, invalidate, the wire converter is actually called, the delegate reuses the shared
  resolvers (not a second copy), and the delegate is actually wired into the registered `ActorHub`.

## A named, standing limitation of this session — not glossed over

`FusionRpg.Injector`'s own csproj cannot be compiled in this sandboxed session: `dotnet build` on it
resolves to an ambiguous project name (multiple BepInEx/MelonLoader host variants), and AGENTS.md's own
build instructions require `$env:FUSIONRPG_GAME_DIR` pointing at a real game install with
`BepInEx\core`/`BepInEx\interop`, which this session has no access to. `CheatState.cs`/`RpgClient.cs`
were therefore written by exact, verified pattern-matching against the file's own existing, already-
compiling code (every delegate signature cross-checked against its real declaration) and verified via
the Guard.Tests text scans above (which read the actual committed file content, proving the intended
text is present verbatim, though not proving full compilability). This is the SAME standing limitation
`SpeciesAllocationCacheTriggerTests`'s own class doc comment already names ("End-to-end proof needs the
live game per `live-probe-standard.md`") — not new to this task. The owner's own `deploy-play.ps1`
build (or a live lawn session) is the first point this session's Injector-side code is actually compiled.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.

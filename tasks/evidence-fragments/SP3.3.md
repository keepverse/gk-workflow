# SP3.3 — Move the synthetic `stat.derived` atom builder into Core (one builder)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `BuildMagnitudeAtoms` and `Kebab` move from `RpgStore.Species.cs:227-260` into `SyntheticStatDerivedAtoms`, and the magnitude synthesizer calls it | code edit | done | `gk-core/src/FusionRpg.Core/Effects/Atoms/SyntheticStatDerivedAtoms.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs` |
| `SpeciesMagnitudeSynthTests` and `CreatureLawnDeployMagnitudeTests` stay green, byte-identical atom ids and params | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesMagnitudeSynth|FullyQualifiedName~CreatureLawnDeployMagnitude"` | **13/13 passed** | test output |
| Data builds clean | `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj` | 0 errors | build log |

## What shipped

`gk-core/src/FusionRpg.Core/Effects/Atoms/SyntheticStatDerivedAtoms.cs` (new, public static class):
`BuildMagnitudeAtoms(speciesId, magnitudes)` and `Kebab(value)`, moved verbatim (same logic, same
`AtomRow.DeriveId`/`ParamsJson` construction, same ordering) from `RpgStore.Species.cs`'s two former
private static methods.

`RpgStore.Species.cs` now calls `SyntheticStatDerivedAtoms.BuildMagnitudeAtoms`/`.Kebab` directly at
both former call sites (the pre-write synthesis loop, and `DeleteMagnitudeContainerUnlocked`'s family-
prefix computation) — no local wrapper kept, so there is exactly one builder, not two names for the
same one. This is the "one builder" SP3.4-SP3.7 (`SpeciesLayerProjector`) will call for 1a/1b/2b's own
synthetic atoms, closing the Data-layer-only half of the map's "three half-mechanisms" observation
(`TreeBoundAtoms` / the magnitude synthesizer / `SpeciesPassiveAtomSource`).

No behavior change: same inputs produce the same `AtomRow` values, proven by the two untouched
regression suites staying green without any test edits.

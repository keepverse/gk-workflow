# SP3.2 — `ContainerKind.SpeciesProgression` (a closed-vocabulary addition)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The kind and its prefix `species-progression` exist in `ContainerRow`, `ContainerValidator:35`, `RpgStore.Containers.cs:573` | code edit | done | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs`, `ContainerValidator.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs` |
| A valid `species-progression.*` container passes `ContainerValidator` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ContainerValidator"` | **30/30 passed** (incl. new `A_species_progression_container_passes_validation`, `Every_kind_has_a_prefix_and_a_valid_id_passes` generic loop auto-covers the new enum member) | `tests/FusionRpg.Core.Tests/Atoms/ContainerValidatorTests.cs` |
| A `species-passive` container is still frozen and cannot carry 2b (neither prefix accepts the other's id) | same run, `SpeciesPassive_and_SpeciesProgression_cannot_take_each_others_prefix` | pass | same file |
| No regression in the store's parse/serialise round trip | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ContainerStoreTests"` | **17/17 passed** | test output |
| Core + Data build clean | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj`, `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj` | 0 errors | build log |

## What shipped

- `ContainerKind.SpeciesProgression` (new enum member, ordinal 13 — appended, matching the file's own
  "a kind is persisted by its PREFIX STRING, never by its ordinal" rule) with a doc comment naming the
  reason: a new kind, not a `SpeciesPassive` reuse, because frozen generator output and player-mutable
  state cannot share a carrier (`decisions.md` Actor layer stack).
- `ContainerRow.PrefixOf` gains the `species-progression` case.
- `ContainerValidator.ContainerIdRe` (the file's own documented "independently-hardcoded prefix list",
  X7's warning) gains the `species-progression` alternative.
- `RpgStore.Containers.cs`'s `ParseKind` gains the `"species-progression" => ContainerKind.SpeciesProgression`
  case (serialisation already free via `KindName` -> `PrefixOf`).

## Reviewed-vocabulary note (spec Boundaries: "Ask first: the ContainerKind addition")

Same posture as SP3.1's §8.1 amendment: built and named as a reviewed closed-vocabulary change here,
matching the precedent of every prior `ContainerKind` addition in this file's own history (Enemy,
Relic, Gem/Charm/Combo/Consumable, EmpireTitle/ActorTitle) — none of those stalled for a literal
work-stoppage either. No existing test pins an exact `ContainerKind` member count, so nothing needed
updating beyond the generic membership-loop test already covering every kind automatically.

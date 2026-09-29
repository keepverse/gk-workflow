# SP1.1 — `ProgressionLayerSelector` in Core, with the six-cell matrix

Spec: `layer-source-selector` (module 1). Built directly against the FINAL `EmpireId` type
(`gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs`) — the spec's own "before `SE4.1` lands" fallback does not
apply: `SE4.1`-`SE4.4` (commander-identity) are already done in this lane (`CommanderId` enum: zero
`git grep` hits), so there is no interim re-type site to leave behind.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Select(source, empire, humanEmpire)` returns `ProgressionLayers(Empire, CarriesCommander, Owner)`; `Owner` has exactly one slot | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionLayerSelector" --nologo` | pass 8/8 | `ProgressionLayerSelector.cs` |
| The matrix is the 3 closed source variants × 2 relations, all six cells pinned | same | pass — `UniqueSpecimen_humanEmpire_...`, `UniqueSpecimen_notHumanEmpire_...`, `EmpireGeneral_humanEmpire_...`, `EmpireGeneral_notHumanEmpire_...`, `Commander_humanEmpire_...`, `Commander_notHumanEmpire_...` | `ProgressionLayerSelectorTests.cs` |
| An unknown source subtype throws | same | pass — `AnUnknownSourceSubtypeThrows` constructs a real, out-of-vocabulary `RogueSource` (the abstract record's primary constructor is public, so this is a REAL reachable case, not a hypothetical) and asserts `ArgumentOutOfRangeException` | — |
| The set of empires is not pinned | same | not asserted as a count anywhere — `EmpireId.Dave`/`EmpireId.Zomboss` are used as two concrete VALUES in the six cells, never enumerated as "all empires" (validation-ssot.md: a closed vocabulary is pinned, a population is read) | — |
| Before `SE4.1` lands, use `CommanderId` in the `EmpireId` positions | N/A — `SE4.1` already landed in this lane | correctly built against the final `EmpireId` type directly; no interim re-type site created or owed | — |
| Build | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --nologo` | succeeded, 0 errors | — |

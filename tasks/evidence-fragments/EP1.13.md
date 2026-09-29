# EP1.13 — `EffectiveUniqueAllocation(Unlocked)`: explicit wins wholesale, else the ladder's default

Spec: docs/architecture/empire-progression/spec-default-build.md

| Criterion | Command | Result |
|---|---|---|
| A specimen above level 1 with no explicit allocation resolves its species' plan distribution, points summing to its budget, asserted as a relation never a literal (test 1) | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EffectiveUnique"` | pass (5/5) — `A_levelled_specimen_with_no_explicit_allocation_resolves_the_species_favour_distribution_notZero` asserts `Might > Vigor > Fortitude` (fumeshroom's own plan order) and `total == budget`, never a point literal |
| One explicit point replaces the whole default (D2, test 2) | same run — `One_explicit_point_replaces_the_whole_default` | pass — the default's own `Vigor` points are gone after one explicit `Might` point, not left over from a top-up |
| A level-1 specimen resolves Empty with `IsDefault = true` (test 3) | same run — `A_freshLevelOne_specimen_resolves_empty_withIsDefaultTrue` | pass |
| A resolved allocation carries no `CreatureType`-scope points, both the default and explicit case (test 6) | same run — 2 tests | pass |
| `guard-dal.ps1` | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |
| Determinism (Extra Rigor — shared static state) | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EffectiveUnique\|FullyQualifiedName~AllocationStoreTests"`, run twice | pass both times, 23/23 |

## Notes

- **Shared-static-catalog hazard found and fixed.** `SpeciesBuildPlanCatalog` is a global, unscoped
  singleton (its own doc comment: "no test-scoping mechanism"). `AllocationStoreTests.cs` already
  configured it in a static ctor with a comment claiming to be "the only file in the assembly that
  touches it" — this task's new test file needed the identical species ("fumeshroom") to assert the
  real distribution order, which would have made that claim false and reintroduced the exact race the
  comment warned about (two static ctors racing under xUnit's cross-class parallelism). Fixed per the
  Extra Rigor rule (a test touching process-wide static state stays out of it or shares one serialized
  xUnit `[Collection]`): both `AllocationStoreTests.cs` and the new `EffectiveUniqueAllocationTests.cs`
  now carry `[Collection("SpeciesBuildPlanCatalogGlobal")]`, and both configure the IDENTICAL
  dictionary, so the collection removes the race and the identical content makes whichever ctor runs
  last harmless regardless. Proven deterministic by running both classes together twice (23/23 both
  runs).
- `EffectiveUniqueAllocationUnlocked`'s three private helpers (`UniqueAssignContextUnlocked`,
  `MaterializePresetRowsAtUniqueBudget`, `ToPermilleDictionary`) mirror
  `AptitudePresetEndpoints.BuildAssignContext`'s "unique" branch (Server layer) and the preset
  activation path's own materialize-at-budget math, read here against the Data layer's own connection
  so the resolver never opens a second one — matching the spec's "identical in shape to the species
  path" instruction.
- `MintForEmpire` (the real creature-minting path, unlike the bare `EnsureUniqueActorForAudit` test
  fixture) writes a real `rpg_creature_profiles` row with the passed `speciesId`, which
  `ReadCreatureProfileUnlocked` then resolves inside the context builder — confirmed by reading
  `RpgStore.Creatures.cs`'s `MintCreatureForEmpire` before relying on it, not assumed.
- No production caller reads this resolver yet (that is EP1.14's own job, and its own golden-move
  commit) — this task's only callers are its own tests, so nothing else in the suite is affected.

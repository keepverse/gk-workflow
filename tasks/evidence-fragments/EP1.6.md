# EP1.6 — `RespecPolicy`: `RespecPriceTuning`, re-typed `PriceOf`, `Quote`, `IsRespec`

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| `IsRespec` true exactly when some aptitude decreases (property + 4 named cases) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy"` | pass — `IsRespec_additions_only_is_false`, `IsRespec_a_single_decrease_is_true`, `IsRespec_empty_to_anything_is_false_a_first_allocation_is_free`, `IsRespec_nonEmpty_to_empty_is_true_clearing_is_a_respec`, `IsRespec_property_true_exactly_when_some_aptitude_decreases` (theory, 4 cases), `IsRespec_only_looks_at_the_given_scope` |
| `PriceOf(RespecPriceTuning, count)` and `Quote(tuning, count, freeStock)` exist | same run | pass — `Quote_wraps_PriceOf_and_carries_the_free_stock_it_was_given`, `Quote_zero_free_stock_reads_FreeAvailable_false`, `Quote_negative_free_stock_throws` |
| `SpeciesBuildTuning.SpeciesRespec` is the species view; every existing `SpeciesRespecTests` case passes unedited (test 7) | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec"` | pass (8/8), no test file edited |
| The species spend and `/respec-price` preview both pass `tuning.SpeciesRespec`; no second price formula | `grep -rn "RespecPolicy.PriceOf" src` | two call sites, `RpgStore.SpeciesRespec.cs:217` and `SpeciesBuildEndpoints.cs:88`, both `tuning.SpeciesRespec` |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs,gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs,gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs,tests/FusionRpg.Core.Tests/Stats/Aptitudes/RespecPolicyTests.cs -Session empire-progression-20260920` | Core 14710/14711 (same named pre-existing `ExpeditionResolverTests` drift, identical hash); Data 8/8 and Server 10/10 confirmed separately (the scoped script stops at the first project failure) |

## Notes

- `RespecPriceTuning`/`RespecQuote` live in `RespecPolicy.cs` beside the policy that reads them, matching
  `AssignLadderTuning`'s own precedent of a small tuning-shaped record living beside its consumer rather
  than in the loader file (the loader for the two new `uniqueRespec*` keys arrives in EP1.7).
- `IsRespec` reads only the named `scope` — a decrease in a different scope is never mistaken for this
  one's respec (`IsRespec_only_looks_at_the_given_scope`), which matters once a creature commander's own
  `UniqueCreature` points and the empire's `Commander` pool are priced by two separate counters (EP1.8).

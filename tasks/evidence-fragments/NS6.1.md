# NS6.1 — Two read methods on `RpgStore.CacheDecay.cs` (ask A5)

| Criterion | Command | Result |
|---|---|---|
| `ListCacheClocksStarted(owner, from, to)` and `ListCacheDecayTicks(owner, from, to)`, read-only, inclusive range, in the owning partial; no schema change, no change to the tick | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~CacheDecayReadTests"` | `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4` |
| ticks at 4, 5, 6 with range `[5, 6]` return exactly those for that owner and none of another's; destroyed/remaining reconcile with `outcomes_json`; deployment-hierarchy's existing `CacheDecay` tests stay green | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~CacheDecay"` | `Passed! - Failed: 0, Passed: 19, Skipped: 0, Total: 19` (15 pre-existing + 4 new) |
| `guard-dal.ps1` | | `DAL GUARD OK` |

`ListCacheDecayTicks` reduces `outcomes_json` to `DestroyedCount`/`SurvivedCount` once, inside the
read method, reusing the existing `DecayOutcomeDestroyed`/`DecayOutcomeSurvived` closed vocabulary
— no consumer (NS6.2) ever parses the raw JSON itself. The reconciliation test independently
re-parses `outcomes_json` via a raw SQL read and asserts the counts match, rather than assuming a
roll outcome, so it is correct regardless of the seeded RNG's actual split that run.

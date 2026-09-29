# TVB-F16 — the Data bootstrap configures `AptitudeTuningHub` once

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the defect | read the two test files | `WorldTurnCasualtyTests` and `WorldTurnHubInputsForTests` each carried a private `AptitudeTuningHub.Configure(...)` + a private `FindShippedAptitudesTuningPath()` walk; `ContractTuningTestBootstrap` named ~20 hubs and not this one | this fragment |
| the fix | one configure in `ContractTuningTestBootstrap.Init()` + a `FindShippedAptitudesTuning()` helper on `FindRepoRoot()` | the hub is configured once for the whole assembly; both private copies deleted | `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs` |
| the row's own Verify | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~WorldTurnCasualty\|FullyQualifiedName~WorldTurnHubInputs"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11, Duration: 862 ms` — with both local calls gone | — |
| the module boundary | `verify-change.ps1 -Paths @(the three files) -Session tvb58` | `data-tests-fallback (module)` → `test: data (sharded runner)`; `TEST-SHARDED OK: 4 shards, 1741 tests, no overlap`, every shard exit 0; `EXIT=0` | — |
| the loader is a reading | the helper | highest `data/tuning/aptitudes.v<n>.json` by version, never a pinned literal — so a publish cannot break it | — |

The row's cause is the one it named: `RpgStore.WorldTurnHubInputsForUnlocked` reads
`AptitudeTuningHub.Tuning`, and no Data test had ever committed a district assault through the store, so
each file that did configured the hub locally. Nothing is lost by removing those copies — the assembly's
own `[ModuleInitializer]` now runs the same configure with the same loader for every Data test.

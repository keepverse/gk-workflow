| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| No `ScaledAmount` left in src/tests/tools | repo-wide grep | 0 hits in src/tests/tools (remaining hits are docs/tasks prose + CostLedger history references) | — |
| Targeted suites green | `dotnet test --filter ActionCatalog\|PoiseLedger\|CostLedger\|ActionCostsCooldownsAdoption` | Passed 71/71 | — |
| No golden moved | `dotnet test --filter BattleGolden` | Passed 5/5 | — |
| verify-change (incl. guard fix) | `verify-change.ps1 -Paths <8 files> -Session summoner-convergence-impl-20260918` | exit 0; battle-responsibility OK; funnel-delta OK; core 14133/14133 incl. SpecChannelClaim 2/2 | — |
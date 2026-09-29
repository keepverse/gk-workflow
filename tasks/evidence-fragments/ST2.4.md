| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Window bounds rung (spec tests 1, 2) | `dotnet test --filter UnlockLadder\|RungSemantics` | 32/32 incl. `WindowCeilingBoundsTheRung`, `NullWindowMatchesTheTwoArgumentForm` | — |
| Floor never raises (spec test 3) | same | `WindowFloorNeverRaisesTheResult` green | — |
| No golden moved (acceptance canary) | `dotnet test --filter HolderRungPricing\|BattleGolden` | 7/7 — production passes no band yet, bound is inert there | — |
| Trailing `RungBand = null` keeps all 16 positional call sites compiling | `dotnet build FusionRpg.Core.Tests` | 0 errors (one positional test fixture needed named args) | — |
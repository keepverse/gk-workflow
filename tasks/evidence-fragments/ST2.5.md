| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Band on compiled action, copied by compiler | `dotnet test --filter HolderRungPricing` | 3/3 incl. band-survives-compile assert | — |
| One instance resolver shared by ledger + hit | code: `CostLedger` takes `rungOf: EffectiveRungOf` method group; AE1.2 adds only its fallback line | no second resolver exists | — |
| Held action pays at min(earnCount, ceiling) through real Resolve (spec test 4) | same | bound(9→2, window [1,2]) attacks less than unbound(1); only earnCount varies | — |
| RungSemantics guard-reads-authored unchanged; StructureBudgetGuard untouched | `dotnet test --filter HolderRungPricing\|RungSemantics\|BattleGolden` | 16/16 | — |
| BattleGolden no change | same | 5/5 golden tests inside the 16, unmoved | — |
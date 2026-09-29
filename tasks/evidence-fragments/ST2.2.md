| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Compile carries authored amount (spec test 8) | `dotnet test --filter HolderRungPricing` | 2/2 incl. `CompileCarriesTheAuthoredAmountUnscaled` | — |
| Non-held pays base×costMulti once (spec test 5) + planted violation | same + falsifier run (pre-scale restored) | green; falsifier red 2/2 (Expected 10, Actual 20), restored → green | — |
| ActionCostsCooldownsAdoption unchanged (spec test 6) | `dotnet test --filter CostLedger\|ActionCostsCooldownsAdoption\|ActionCatalog\|HolderRungPricing` | 60/60 | — |
| Golden movement recorded, no re-bless | `dotnet test --filter BattleGolden` | 5/5 — no golden moved | — |
| Overflow clean | `python gk-core/scripts/audit-overflow.py --targets A3` | no output (clean) | — |
# ST4.1 — one pricing helper shared by the catalog check and the report

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| The atom fetch + `ActorPowerCache.Compose` block is one private helper | code read + build | **Done.** `RpgStore.PriceContainer(ContainerRow?)` is the one place a container is priced; `BuildActionCatalog` now calls it and keeps the atoms it returns for scope validation and the timing derivation, so no second fetch of the same rows. | gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs |
| `ListActionPricing` returns every containered action, **including** ones the budget rejects | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCatalog\|FullyQualifiedName~ActionPricing"` | **18/18 pass.** `The_containered_action_is_priced_including_the_one_the_budget_rejects` seeds an overspent rung-1 action and a thrifty rung-10 one: `BuildActionCatalog` keeps only the thrifty one, while `ListActionPricing` returns both, with the rejected row carrying its authored rung. | gk-core/tests/FusionRpg.Data.Tests/Actions/ActionPricingTests.cs |
| **Planted violation:** a second pricing function fails the agreement test | same filter, with `PriceContainer` temporarily returning `Compose(...).Total + 1` | **2 failed / 2 passed**, exactly the two guards: `The_report_prices_exactly_as_an_independent_second_pricing_does` and `The_report_and_the_catalog_check_agree_on_where_the_budget_line_is`. Restored immediately; the filter is 18/18 again. Proof the test measures the pricing path rather than re-deriving it. | gk-core/tests/FusionRpg.Data.Tests/Actions/ActionPricingTests.cs |
| The report and the check agree on the budget line | same filter | **Passes.** For the same two actions, `ListActionPricing`'s figure equals an independently composed one, the kept action prices at or under rung 10's `powerBudgetMilli`, and the rejected one prices above rung 1's — so the number the report calibrates is the number the check enforces. | gk-core/tests/FusionRpg.Data.Tests/Actions/ActionPricingTests.cs |
| Boundary | `.\scripts\verify-change.ps1 -Paths … -Session summoner-convergence-impl-20260918` | `dal` OK · `test-substrate` OK · core **14180 passed / 1 failed**, the one red the documented CRLF worktree artifact (`DungeonLootTableSeedFileTests`). The script stops at the first red module, so the data module was run directly — the 18/18 above — plus `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`, both OK. | tasks/summoner-convergence-ledger.jsonl |

## Two deviations, both declared

1. **`gk-core/src/FusionRpg.Core/Actions/Rungs/PricedAction.cs` (new) is not in this task's Files line.** The
   spec's contract 2 types the report's input as `IReadOnlyList<PricedAction>` in Core, and this task is
   what first produces one; declaring the DTO here rather than in ST4.2's `BudgetCalibration.cs` keeps
   ST4.1 compiling on its own (ST4.2 depends on nothing). ST4.2 adds `BudgetCalibration.Read` over it.
2. **The session record's `paths` gained that file** — the fence was true for the task's two listed
   files but not for the DTO, and the repo's rule is to repair the map rather than drop the path.

## A judgement call, recorded

`ListActionPricing` prices every action with a container regardless of `Enabled`. Contract 3 says
"every action with a container is read", and the disabled flag is the importer's own "this brief no
longer composes" mark (ST1) — not a budget question. A row the owner disabled is still content that
exists and would be budget-checked if it were served, so excluding it would understate the calibration
rather than protect it. The alternative reading (enabled rows only) is a one-line change if the report's
first reading argues for it.

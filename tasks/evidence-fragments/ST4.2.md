# ST4.2 — pure `BudgetCalibration.Read` and `recommendedReferencePower`

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| An action priced exactly on budget at `REF` reads `REF` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BudgetCalibration"` | **8/8 pass.** The fixture is built so the inversion divides exactly (`poolRolls 2 × qPowerMilli 1323 × REF 500 / 1000 = 1323`, the published budget; `1323 × 1000 / 2646 = 500` back) — a floor division only proves the inversion when the fixture is exact, so an inexact one would have proved the rounding instead. | gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs, tests/…/Rungs/BudgetCalibrationTests.cs |
| Σ per-rung `n` equals the number of priced actions; each id appears once | same command | **Passes.** Four actions across three rungs: `PricedActionCount == Σ rung.Count`, and the union of the per-rung above-scalar id lists has no duplicates. Reconciliation, not a count. | tests/…/Rungs/BudgetCalibrationTests.cs |
| `min ≤ p50 ≤ p90 ≤ max`; a rung with `n = 0` reports no percentiles | same command | **Passes.** Rung 1 carries three readings and is ordered end to end; rung 2 carries none and reports `null` for all four rather than four zeros (four zeros would read as "every action here needs a scalar of 0"). | tests/…/Rungs/BudgetCalibrationTests.cs |
| An action the budget rejects is still named by the report | same command | **Passes.** With a `powerBudgetMilli` column, the one action above the loaded table's own implied scalar is named; with a pre-A-G1 table (no column) nothing is above it — the column's absence is a skip, never a guess. | tests/…/Rungs/BudgetCalibrationTests.cs |
| Arithmetic throws on overflow and refuses a zero divisor | same command | **Passes.** `long.MaxValue / 2` as a realized power throws `OverflowException` (widening is not enough at that magnitude); a row with `poolRolls = 0` throws `InvalidOperationException` naming **rung 1**, not a divide-by-zero. | gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs |
| Repricing at the recommendation rejects none; one below rejects the max | same command | **Passes**, as a property: at `recommendedReferencePower` every action's repriced budget (the published derivation, mirrored in the test) covers its realized power, and at that value − 1 the action that set the max is below its own budget. The test also asserts the recommendation IS the max of the per-action ceilings, so it cannot drift from contract 6. | tests/…/Rungs/BudgetCalibrationTests.cs |
| No test pins a percentile or a `referencePower` | test read | **Holds.** The only literal scalars are the fixtures' own inputs, each chosen to make the derivation exact and stated as such; every expectation is either the derivation recomputed in the test or a property. | tests/…/Rungs/BudgetCalibrationTests.cs |
| Overflow audit | `python scripts\audit-overflow.py --targets A3` | **Exit 0, no findings.** The arithmetic is `checked` `long`, widened before multiplying, one division last and exactly once (A3's rule). | gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs |
| Boundary | `.\scripts\verify-change.ps1 -Paths … -Session summoner-convergence-impl-20260918` | Both new paths resolve (`core-fallback`, `core-tests-fallback`); core **14188 passed / 1 failed**, the one red the documented CRLF worktree artifact — and the total moved from 14181 to 14189, the 8 new tests. | tasks/summoner-convergence-ledger.jsonl |

## One design point worth naming

The two roundings differ on purpose, and the code says so where it matters:
`impliedReferencePower` is the spec's own FLOOR division (its Code-style sample is
`realizedPowerMilli * PowerMath.One / (poolRolls * qPowerMilli)`), because it is the honest inverse of
the published floor-derived budget; `recommendedReferencePower` is CEILING (contract 6), because the
recommendation must be safe — a scalar one short would reject content the owner already accepted. They
differ by at most one, and the test asserts the recommendation equals the max of the per-action
ceilings rather than comparing the two directly.

`Read` walks `table.Rows`, so the report is a complete per-rung picture including the rungs with no
content; an action whose authored rung the loaded table does not carry is refused **by name** rather
than silently dropped — the budget check reads the authored rung, so a table without it cannot be
calibrated against.

# ST4.5f — `recommendedBy`: the report names the actions that SET the scalar

**Status: done.** Manager, on ST4.5b: *"correct to the letter, but it misses the contract's INTENT on
this corpus. With nearest-rank p90, every rung with n<10 has an empty aboveP90 by construction, and 18
actions over 10 rungs means almost all do -- including rung 4 (n=3), whose max 1511 is the one action
that SETS recommendedReferencePower=1512. The intent is 'an outlier that drags the scalar up is
visible, not silent'. Add to the report the id(s) of the action(s) that set recommendedReferencePower
(recommendedBy: the argmax of the ceiling), with a test that it names the setter on a fixture."*

## What changed

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs` | `BudgetCalibrationResult` gains `RecommendedBy`; `Read` keeps the argmax of `CeilingReferencePower` instead of only its value |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` | `recommendedBy = report.RecommendedBy` on `GET /api/debug/action-budget-report` |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/Rungs/BudgetCalibrationTests.cs` | 2 tests — the argmax naming the setter (with a tie kept whole), and the property that every named id is a priced action whose ceiling IS the recommendation; the empty-catalog test now asserts the list is empty too |
| `gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs` | the endpoint's `recommendedBy` is always non-empty when a scalar is recommended, and every id is a priced action |

**The argmax, and a tie is kept whole.** Two actions that need the same scalar both set it, so naming
one of them would hide the other. Ordered ordinal, so the list is stable across runs.

This is what `aboveP90` could not carry: on the real corpus rung 4 has n=3, so `ceil(0.9 × 3) = 3`,
p90 IS max, and `actionsAboveP90` is empty by construction — exactly where the scalar-setting action
lives. `recommendedBy` names it there and on every other rung, and it is non-empty whenever
`recommendedReferencePower` is not null.

## Verification

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~BudgetCalibration"` | **14/14** (12 before + 2 new) |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~ActionBudgetReport"` | **1/1** |
| `dotnet test tests\FusionRpg.Server.Tests -c Release --verbosity minimal` | **552/552, 0 failed** — the assembly's own boundary, now green after AE2.2's escape was fixed, and unchanged by this field |

Both read-only and through the same helper: `RecommendedBy` is derived inside `BudgetCalibration.Read`
from the same `ceiling` the recommendation itself is, so the list and the number cannot disagree about
which action set it — the discipline `ActionsAboveP90` and `ActionsAboveLoadedScalar` already follow.
No percentile, no count and no scalar is pinned by any test.

# CAI-tests-1 — the wave-4 Core tests moved to the project their rows name

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row was filed as *"BLOCKED on this lane's fence:
`gk-core/tests/FusionRpg.Core.Match.Tests/**`"* — but that is lane `cai4`'s fence, not this one's, which is
`tests/**` broadly. So the move was executable here rather than waiting for a widening.

| Criterion | Command | Result |
|---|---|---|
| The ten files moved, namespaces with them | `git mv` per file; namespace rewritten per file | `tests/FusionRpg.Core.Balance.Tests/CombatAi/` **no longer exists**; `gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/` holds the ten plus the four that already lived there |
| Nothing outside them referenced the old namespace | `grep -rln "Core.Tests.CombatAi" tests/ src/` | only the moved files themselves (plus a stale `bin/` DLL) |
| The target project runs them | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests` | **182 passed / 0 failed** |
| The source project still builds without them | `dotnet build gk-core/tests/FusionRpg.Core.Balance.Tests` | `Build succeeded` |
| Reason (a): those runs stop paying the whole `core` group | `verify-change.ps1 -PlanOnly -AllowUnscoped -Paths @('gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/LawnOrderQueueTests.cs')` | `-> core-match (module)` — the focused boundary, no `VERIFICATION BOUNDARY MISSING` |

## The row said seven files; there are ten

`CombatAi/` held ten when this ran (the row was written when it held seven), and the row's intent is the
DIRECTORY rather than a count, so all ten moved: `DirectOrderAdmissionTests`, `LawnCastPlanTests`,
`LawnCastTokenPoolTests`, `LawnCoreContractScanTests`, `LawnDecisionBudgetTests`, `LawnDecisionLoopTests`,
`LawnDecisionLoopViewTests`, `LawnDecisionTriggerTests`, `LawnHeldActionSetsTests`, `LawnOrderQueueTests`.

## Reason (b) is the follow-up, and it is not this lane's

The row also notes that `gk-core/src/FusionRpg.Core/Match/**` still resolves through `core-fallback` to the whole
group (39 projects, ~15.7k tests, ~4 min per edit), and that adding the source-side row becomes cheap once
the tests are in the focused project. That registry edit belongs to `test-verification-boundary`, and this
row names it as the follow-up rather than doing it here.

## History, deliberately not rewritten

Twelve mentions of `tests/FusionRpg.Core.Balance.Tests/CombatAi/` remain elsewhere in the todo. They record
where those tests lived when their rows landed — rewriting them would falsify that record — so the current
home is stated here instead.

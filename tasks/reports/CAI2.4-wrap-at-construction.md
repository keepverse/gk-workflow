# `CAI2.4` — the per-arm wrap belongs at construction, not in the one factory

Lane `cai3` (session `combat-ai-3`), 2026-09-23. A small correction to the mechanism this lane's earlier
increment extended.

## The asymmetry, measured rather than reasoned

`AiDecisionRecordingSource` wrapped the policy, the fallback and the steered source inside
`IntentRouter.Compose` — the factory. `IntentRouter`'s **constructor** is public and its own doc says
`Compose` is the one entry point production must use, but nothing enforced that: a caller using the
constructor directly with a sink got the **ORDER** arm recorded (that arm records from `Resolve`) and the
**three source arms silent**.

Measured by planting the pre-move shape back (wrap in `Compose`, none in the constructor) and running the
suite:

```
Failed!  - Failed: 1, Passed: 24, Total: 25
  A_directly_constructed_router_records_its_source_arms_too  [FAIL]
```

Every pre-existing test passed; only the new one failed. That is the asymmetry, and the new test pins
exactly it.

## What landed

The wrap moved into the **constructor**, so "every arm records" holds for **every construction path** and
`Compose` stays an ordering helper (it still hands the policy to `steeredSourceFor` **unwrapped**, which is
what that parameter's own doc requires). One place wraps; the factory no longer does.

| Criterion | Command | Result |
|---|---|---|
| Every arm records, and a directly-constructed router records too | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouterTests\|FullyQualifiedName~DecisionInspectorTests" --nologo --verbosity quiet` | **34 passed / 0 failed** (25 `IntentRouterTests`, 9 `DecisionInspectorTests`) |
| The new case is load-bearing (planted pre-move shape) | same command with the wrap back in `Compose` only | **1 failed** — exactly `A_directly_constructed_router_records_its_source_arms_too`; every other test passed; reverted green |
| The whole Core project | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **9720 passed / 0 failed** (was 9719) |
| No golden moved | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --nologo --verbosity quiet` | **210 passed / 0 failed** |
| The lawn/match surface | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests --nologo --verbosity quiet` | **182 passed / 0 failed** |
| The delve/Server surface | `dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --verbosity quiet` | **858 passed / 0 failed** |
| The program's guards | `guard-actor-hub`, `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-battle-responsibility`, `guard-secondary-no-unity` | all **exit 0** |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

## NOT proved

- **No live probe.** The property is asserted at the router; the production wire's own proof (a real battle
  reaching the sink) is `DecisionInspectorTests.A_real_battle_reaches_the_routers_sink`, from the previous
  increment.
- **`Compose`'s "never a second one" doc is still prose, not enforcement.** Nothing stops a future caller
  from using the constructor directly — it just records correctly now, which is the point.

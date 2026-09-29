# CAI4.6 — `lawn-cast-activation`: the ordered cast plan (Core half)

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Row: `tasks/combat-ai-todo.md` CAI4.6.
Spec: `docs/architecture/combat-ai/spec-lawn-cast-activation.md`.

`gk-core/src/FusionRpg.Core/Match/Ai/LawnCastPlan.cs` + 7 tests in
`tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs`. This is the row's **pure** half —
the half the routing block names explicitly ("`Match/Ai/LawnCastPlan.cs` (CAI4.6 — the *pure* half, not
just the injector half)").

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 1. Pure and ordered **pay → cooldown → event**; `InsufficientFunds` starts no cooldown and produces no event | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnCastPlan"` | 7 passed / 0 failed | `An_insufficient_funds_outcome_starts_no_cooldown_and_produces_no_event` (real `CostLedger` over real pools; asserts the cooldown is unarmed AND `ReadyAt == 0`) |
| 1. **Planted violation:** emitting the event / arming the cooldown before paying fails | planted cooldown-before-pay, run, reverted | **1 red** (that same test); 7/7 green after revert | see commit body |
| 1. A paid cast charges exactly once at commit | same | 7 passed / 0 failed | `A_paid_cast_charges_exactly_once_at_commit` (100 stamina, an 80 cost: the second cast is refused) |
| 2. The built event has `Trigger == EffectTriggers.OnActivate`, `HitCount == 1` and the post-decision target | same | 7 passed / 0 failed | `A_paid_cast_starts_the_cooldown_and_builds_the_activation_event` |
| The plan reads no clock of its own | same | 7 passed / 0 failed | `The_plan_reads_no_clock_of_its_own` (the tick is supplied; two ticks differ only in `Event.Tick`) |
| Declaring nothing is `None`, never a throw | same | 7 passed / 0 failed | `Declaring_nothing_yields_None_rather_than_throwing` |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | 5 passed / 0 failed | no battle/siege/delve file touched |
| Row Verify line: `verify-change` | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/LawnCastPlan.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs') -Session combat-ai-4` | exit 0, **15672 passed / 0 failed** across 35 project runs (which includes the whole `FusionRpg.Core.Effects.Tests` contract suite — the row's effects-contract clause) | `core-fallback` + `core-balance` |
| `guard-funnel-delta`, `guard-single-writer`, `guard-actor-hub`, `audit-overflow --targets A3`; Balance project | see commit body | all exit 0; 277/0 (was 270) | — |

**Owed, and every one of them outside this lane's fence — the row stays open:**

1. **Row 3 — the record-kind discriminator.** `EffectEventDto.CastOrigin` is an additive
   default-`false` field on `gk-core/src/FusionRpg.Contracts/EffectDtos.cs`, and its two consumers are the
   injector's basic-attack charge (`ShouldApplyRider`'s early return) and module 19's swing counter. The
   plan states its side of the contract in its own doc comment — **every event it returns IS a cast**, so
   the fire site stamps the flag — and the Core half cannot add the field.
2. **Rows 4 and 5 — `Fire`'s depth-0 refusal and the fail-closed liveness re-check**, plus
   `FoundationContractVersion.Current`'s non-movement: all `gk-fusion/src/FusionRpg.Injector/**`.
3. **The fire site itself** (`LawnCastActivation`) — without it nothing calls the plan, so this is a Core
   half with no production host, exactly as CAI4.2/CAI4.7/CAI4.9 are.
4. **No tuning publish**, correctly: the cost is the action's own cost rows, the cooldown is its envelope,
   and `HitCount` is 1 — the module introduces no number a balance pass would touch.

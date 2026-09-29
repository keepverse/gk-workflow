# CAI2.6 — the reserve floor's rule: RULED and implemented

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The orchestrator asked for the rule to be DECIDED from
the documents rather than from whichever code was read first, and the deciding document named. It is
**`docs/architecture/combat-ai-ideal.md:318`** — the ideal's §6.1 step 3:

> "- the **reserve floor**: a pool may not drop below a fraction of its max **after paying**;"

`docs/architecture/combat-ai/spec-action-schedule-twin.md` §2 quotes that line verbatim, so both authority
documents agree and the shipped seam was the defective side. The twin was left alone.

## The rule as landed

`ReserveFloorAffordability.Check` now refuses when the POST-PAYMENT balance would fall below the floor:

```csharp
if (_currentBalanceOf(resourceId) - cost < floor)
    return UsabilityResult.Refuse(UsabilityReason.CannotAfford, resourceId);
```

Two consequences, both intended and both asserted: equal to the floor is ADMITTED (the pool does not drop
*below* it), and a zero-cost action at the floor is admitted, which is what ends the idling the old
pre-condition reading caused. The cost arrives through a new trailing-optional delegate
`ActionCostOf(actorKey, actionId, resourceId)` — a READ the composer supplies from the same
`CostLedger`-shaped authority the decorator wraps, so this class still computes no cost of its own
(ideal §3 principle 6, its own doc's rule). The `poise` reaction boost is unchanged and now protects the
reaction spend properly: the floor must REMAIN after paying, which is the whole point of it.

| Criterion | Command | Result |
|---|---|---|
| The witness is now a PARITY assertion, not a divergence | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests"` | **3 passed / 0 failed** — `The_reserve_floor_rule_agrees_between_the_twin_and_the_shipped_seam` asserts `Assert.Equal(twin, real)` with both `[act.skill, act.pass, act.pass, act.pass]`. It previously asserted the seam's `{ act.skill, act.skill, null, null }` — `null` being `ActionIntent.None`, the actor idling |
| The seam's own boundary cases are flipped to the ruled rule | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionStageTests"` | **16 passed / 0 failed** — `The_floor_admits_landing_on_it_and_refuses_dropping_below_it` (land ON the floor = admitted; one below = refused) and `A_zero_cost_action_is_admitted_at_the_floor_so_the_actor_never_idles` |
| Golden: byte-identical, and that is MEASURED | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed / 0 failed** |
| The wider balance surface | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests` | **301 passed / 0 failed** |
| Guards | `guard-actor-hub`, `guard-battle-responsibility`, `guard-single-writer`, `guard-dal` | all **exit 0** |

## The predicted-delta note, which is a NO-MOVE note

The old row said the first ruling is *"explicitly NOT byte-identical"*. Measured today it IS
byte-identical, and the reason is checkable: `new ReserveFloorAffordability(...)` still appears **nowhere
in `src/`** (only in `ActionStageTests` and `ActionScheduleMatchesCorePolicyTests`), and both shipped
profiles author `reserves: []`, so `floor <= 0` skips every resource. No battle can observe this change.
**The golden move belongs to the commit that wires the decorator (CAI3.6) and authors a non-zero floor**,
and that commit owns the predicted-delta note. This is stated because a silent "no goldens moved" would
otherwise read as luck rather than as a measured fact.

## The residual edge, named rather than smoothed over

A pool ALREADY below the floor still refuses a zero-cost non-Basic action, because `10 - 0 >= 50` is
false. That is the same shape as the divergence CAI2.6 was opened for, at the one point where "may not
drop below" is read strictly. The actor is not idle — `ActionKind.Basic` is structurally exempt, which is
this seam's form of the twin's deliberately unfloored free fallback, and the test says so on the line.
Recorded here rather than fixed, because changing it would be a SECOND ruling (whether a floor may refuse
an action that cannot possibly breach it) and the ruled rule is what the ideal's sentence states.

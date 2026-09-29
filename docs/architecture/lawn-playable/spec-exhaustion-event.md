# Spec: `exhaustion-event` (lawn-playable module 6)

**Program:** [lawn-playable](../lawn-playable-map.md) · **Depends on:** nothing structural ·
**Pairs with:** `lawn-tuning-profile`'s `lawn-resource-scale` (which makes exhaustion reachable at every
build) · **Sharpens:** `lawn-scale-live-proof` / proof 5's own instrument
**Status:** spec, 2026-09-16. Not built.

## Objective

Make exhaustion something that **happens to an actor**, observably, instead of a number that increments
somewhere.

Today, on the lawn, the entire consequence of running out of stamina is one line:

```csharp
if (afforded) LawnCombatObserver.RecordStaminaSpent(_costAmount);
else LawnCombatObserver.RecordExhaustion();          // LawnBasicAttackCostCharger.cs:164
```

and `RecordExhaustion` is `_exhaustionEvents++` — a process-wide counter with **no actor, no resource
id, no tick, no transition**. Nothing is emitted, nothing is stored, nothing is shown. A player whose
plant just stopped applying riders sees a plant that still shoots and has no idea why.

### Three specific defects, all measured

| # | Defect | Evidence |
|---|---|---|
| E1 | The counter counts **refusals, not transitions** — it cannot tell "entered exhaustion" from "was still exhausted on the next swing" | `_lawn-combat-proof4-exhaustion-clean-player.json`: `ExhaustionEvents` **591** over `totalHits` **551**. More events than hits is only possible if every refused swing counts. |
| E2 | Exhaustion has **no actor identity** on the wire | `LawnCombatObserverBridge.cs:131` publishes one board-wide `exhaustionEvents` number; per-ptr rhythm was only recoverable by hand-reading per-hit rows |
| E3 | `ExhaustionPolicy` — the status, its debuff payload, its host-and-resource-scoped grant id, and its "an exhaustion debuff must never touch a channel feeding its own resource's regen" validation — **exists in Core with zero lawn callers.** Only the pure `IsExhausted` predicate is used, by `PoiseLedger` and `NerveLadder`. | `gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionPolicy.cs`, grep for callers |

E3 is the shape this repo keeps hitting: **the machinery is built and inert.** This module is wiring,
not construction — `lawn-combat-wire`'s ideal lists *"resource exhaustion as a real status/debuff (D6)"*
as deferred on the status resolver, and the resolver it was waiting for is the `StatusRuntime` that
`ExhaustionPolicy` already composes against.

## What this module wires, and what stays deferred

| | |
|---|---|
| **Wires now** | The transition event, per actor, per resource, both edges. The status's **lifecycle** through the already-built `ExhaustionPolicy.Sync`. The observer's counter becoming per-actor and edge-triggered. |
| **Stays deferred** | The debuff **content** — which channels an exhaustion status actually weakens, and by how much. That is authored balance and belongs to `lawn-tuning-profile`. This module ships the status with an **empty** stat-mod list, which is a legal, validated payload and changes no number. |

Shipping the lifecycle with an empty payload is the point: it makes exhaustion **visible and bindable**
without making a balance decision nobody measured.

## The shape

### 1. One edge-triggered event, both directions

```
actor.exhausted   { ptr, side, resourceId, tick, poolValue, matchKey }
actor.recovered   { ptr, side, resourceId, tick, poolValue, matchKey, exhaustedForMs }
```

- **Edge-triggered, never per refusal.** The event fires when `IsExhausted` *changes* for that
  `(ptr, resourceId)`. E1 is fixed by construction: a hundred refused swings inside one exhausted
  window produce exactly one `actor.exhausted` and one `actor.recovered`.
- Emitted through the **existing** event pipeline (the drain that already carries `zombie.die`,
  `combat.hit`, `plant.place`) — no second transport, no new SignalR channel.
- `exhaustedForMs` on the recovery edge is what makes "is this a rhythm or an annoyance" a readable
  number instead of an opinion.

### 2. The status lifecycle, through the class that already exists

`ExhaustionPolicy.Sync` is called on the same edge, so `exhaustion.stamina` is applied and withdrawn on
the actor with its host-and-resource-scoped grant id. Nothing about the policy changes — it is
constructed with an empty `debuffsByResourceId` payload for the lawn, and its own constructor
validation (no self-regen spiral) still runs.

That gives **VFX and the HUD a status to bind to**, which is the repo's own rule: the VFX is already
built and tested, this program wires it and never rebuilds it (owner ruling 2026-09-16).

### 3. The observer becomes an instrument, not a tally

`LawnCombatObserver` keeps a counter for continuity, and gains per-actor transition rows:
`(ptr, resourceId, enteredTick, recoveredTick)`. That is exactly what proof 5 reads — *"an exhausted
actor recovered on the same ptr, never a respawn"* — so this module turns a by-hand read of per-hit
rows into a first-class reading for `lawn-scale-live-proof`.

## Tunables

One, and it is a debounce, not a balance number:

`data/tuning/mode-profiles.v{n}.json`, lawn row:

| Key | Meaning | v1 |
|---|---|---|
| `modes.lawn.exhaustion.minEdgeIntervalMs` | floor between two edges for one `(ptr, resourceId)`, so a pool hovering at zero cannot emit a burst | `UNMEASURED` |

The debuff payload is **absent on purpose** (see "stays deferred"). When `lawn-tuning-profile` authors
it, it lands as that program's tuning, read by the same `ExhaustionPolicy`.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Exhaustion|CostLedger|LawnCombatObserver"
dotnet test gk-fusion/tools/LawnCombatObserver.Tests
python gk-fusion/scripts/guard-funnel-delta.py ; python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Project structure

| What | Where |
|---|---|
| Edge detection | `gk-core/src/FusionRpg.Core/Actions/Cost/` beside `ExhaustionPolicy` — pure, Unity-free |
| Emission | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs` (the one place that already knows the charge outcome) |
| Status sync | `ExhaustionPolicy.Sync`, called from the same edge |
| Observer rows | `gk-core/src/FusionRpg.Core/Combat/Observability/LawnCombatObserver.cs` |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/ExhaustionEdgeTests.cs`, `gk-fusion/tools/LawnCombatObserver.Tests` |

## Testing strategy

- ✅ **The edge property**: N consecutive refused swings inside one exhausted window produce exactly one
  `actor.exhausted`; the next afforded swing produces exactly one `actor.recovered`. This is E1's fix
  asserted directly — the test that would have caught 591 > 551.
- ✅ Each event carries a real actor identity and resource id; an event with an empty ptr is never
  emitted (fail closed, like the charger already does).
- ✅ The status is applied on the entering edge and withdrawn on the recovering edge, by grant id, for
  that actor and that resource only — never a sibling resource, never another actor.
- ✅ Address reuse: a pointer re-used by a new entity starts with no exhaustion state
  (`lawn-combat-wire` L-N27 measured 46 zombie and 55 plant reused addresses in one run).
- ✅ Kill switch off ⇒ byte-identical to today, including the counter's value.
- ❌ Never assert how many exhaustion events a run produces, or how long a window lasts. Both are
  readings — `lawn-scale-live-proof` owns them.

**Mutants to kill:** emit per refusal instead of per edge; skip the withdraw; key the state by ptr
alone (ignoring resource id); keep state across a match edge.

## Boundaries

- **Always:** emit through the existing drain; use `ExhaustionPolicy` for the status — never a second
  exhaustion notion; clear all state at match end.
- **Ask first:** nothing. The debuff payload is the only balance question and it is deliberately out of
  scope.
- **Never:** make exhaustion degrade the actor's own stats in this module (proof 5's whole claim is that
  it does **not** — an empty payload keeps that true, and any future payload must be measured against
  proof 5's own reading rather than shipped beside it); let an exhaustion debuff touch a channel feeding
  its own resource's regen (`ExhaustionPolicy` already rejects this at construction — do not route
  around it); build a new status system.

## Numeric types

Ticks and durations are `long` (100 ms kernel grid). Pool values are `long` at the
`ResourceChannelReader` boundary, already `checked`. No `P(Θ)`-scaled magnitude is introduced.

## ActorHub gate

Consumes Hub output (`resource.max.*` / `resource.regen.*` through the existing pools) and contributes
the status through `StatusRuntime`, which is a registered path. No new composer, no new fold.

## Success criteria

1. One entering edge and one recovering edge per exhausted window, per actor, per resource — proven by
   test, then read live.
2. `actor.exhausted` / `actor.recovered` visible on the wire with a real ptr, joinable to the run's
   other events by `matchKey`.
3. `exhaustion.stamina` applied and withdrawn on the real actor, with an empty payload, so a HUD or VFX
   binding has something real to bind to.
4. The observer reports per-actor transition rows, and `lawn-scale-live-proof` reads proof 5's
   "recovered on the same ptr" from those rows rather than by hand.
5. With the feature switch off, every number is byte-identical to today.

## Open questions

None. The debuff payload is named as deferred, with the program that owns it.

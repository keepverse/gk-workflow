# spec — `battle-effect-math`

**Module 6 of `solid-remediation`.** Register entry: **D1**. Depends on `battle-responsibility-guard`.

## Objective

Battle's `EffectBag` carries a real `CombatMath`, so **effect-driven** hits in a battle resolve through
the shared resolver instead of applying their authored number verbatim.

The highest single value in the program: one property on an already-constructed object, and twenty
registered channel families start mattering in battle. **The first module that changes what a player
sees.**

## The defect (D1)

> Battle's `EffectBag` never sets `CombatMath`, so `CombatDamageDispatcher` falls back to
> `PassThroughCombatMath`, whose `Finalize` returns the amount unchanged.

Battle's **basic attack** uses the resolver. Every **effect-driven** hit in a battle — DoT tick, on-hit
rider, atom damage — applies its authored number with **no hit roll, crit, element matchup, penetration,
parry or block**.

Evidence:

| Claim | Where |
|---|---|
| Battle's bag never sets it | `BattleEffects.cs:55-64` |
| The fallback | `CombatDamageDispatcher.cs:28` |
| Pass-through returns the amount unchanged | `ICombatMath.cs:15-16` |
| The only production setter is injector-side | `EffectRuntime.cs:539` |

This is rule 2 — battle logic with no resolver at all on that path.

## Shape

**Wire, do not build.** The resolver exists, is correct, and is already used by the lawn and by battle's
own basic attack. The module sets the property battle's bag never sets, using the components already
constructed.

The ideal doc's classification: this is one of the **eleven wires** — the code is correct and unreached.
Nothing here needs a new mechanism, and writing one would be the defect.

## Measured 2026-09-17 — the wiring is small, the effect is unproven

A blast-radius probe was applied and reverted: `Host.Bag.ActorResolve` and `Host.Bag.CombatMath` set in
`BattleRunState`, using `OverlayCombatMath.Create`.

**Good news on size.** The resolve function D1 needs **already exists**, five lines above a line that
already sets a property on the same object:

```csharp
ShieldGate = new ShieldGate(Shields, (ptr, attackerLess) =>
    attackerLess || ptr == null || !ByKey.TryGetValue(ptr, out var a)
        ? CombatActorSnapshot.AttackerLess()
        : new CombatActorSnapshot(a.Derived, a.ElementTypes));
...
Host.Bag.ShieldGate = ShieldGate;        // BattleRunState.cs:332-341
```

That `ShieldGate` wiring carries a comment recording the **identical defect** — *"which neither
`BattleEffectHost` nor `SimEffectHost` ever set… wired here"* — already fixed once, for shields. D1 is
the same fix for the same reason on the same object. `OverlayCombatMath` is Core-side, so battle can
construct it; the injector's version differs only by its Unity-side resolve and breakdown emitter.

**⚠️ The probe moved nothing. 13940/13943 before, 13940/13943 after — not one golden.** Two readings, and
only one of them is comfortable:

- the change is safe, or
- **nothing in 13,943 tests observes effect-driven battle damage at all.**

The second is the likely one, and there is a mechanism for it. `OverlayCombatMath.Finalize` opens with:

```csharp
if (packet.ElementPayload == null || packet.ElementPayload.Count == 0)
    return signedAmount;
```

It returns the amount **unchanged** when the packet carries no element payload — behaving exactly like
`PassThroughCombatMath`. And battle's own damage entry defaults the payload to empty:
`components ?? Array.Empty<ElementPayloadComponent>()` (`BattleRunState.cs:873`).

**So this module must prove the payload reaches the packet, or the fix is inert.** Setting `CombatMath`
and declaring victory would produce a green build, a passing suite, and no behaviour change — the exact
shape of a fix that looks landed and is not. Battle already has the machinery (`HybridPayload.Build`), so
this is still wiring, not new mechanism.

**First task of this module: establish whether effect-driven battle damage reaches
`CombatDamageDispatcher` at all, and with what payload.** Everything below depends on that answer, and it
is not yet known.

## What this changes in play

Effect damage in battle begins rolling to hit, critting, and reading element matchups, penetration, parry
and block. **Numbers will move**, and that is the fix landing, not a regression.

This module owes a **before/after measurement**, not a re-tune. Any re-tune the measurement justifies
belongs to `lawn-tuning-profile` or the owning feature — **this program introduces no tunables**. A
remediation pass that starts changing balance numbers has stopped being a remediation pass.

## ActorHub

**Consumes** Hub output. It introduces no compose and no private fold, and adds no
`ContributionSourceIds` grammar id. If the implementation finds itself folding actor combat numbers
locally, that is the wrong shape — stop and re-read `actor-hub-ssot.md`.

## Numeric

Damage is an integer magnitude that `P(Θ)` grows, so it is `long`, widened before multiplying, with
integer overflow throwing rather than wrapping. `int` per-mille passes its range at Θ=3,213 and `int`
whole units at Θ=103,557 — both reachable. Where a value narrows to a Unity `int` field, that narrowing
is checked and reported (`EntityStatWriter.ClampToInt32Reporting`), never silent.

## Tests to rewrite

Any test asserting that a battle effect's damage equals its authored amount is **pinning this defect**.
Restate to the contract — the amount resolves through `CombatMath` — never re-point it at a new number.
If a test cannot be restated as a contract, that is a signal the change is wrong, not that the test is in
the way.

New tests assert the **contract**: an effect-driven hit in battle goes through the same resolver a basic
attack does, and a pass-through result is refused rather than silently accepted.

## Boundaries

- **Always:** use the constructed resolver; measure before and after
- **Ask first:** any tuning publish the measurement seems to justify
- **Never:** a second `CombatMath`, or a battle-local damage fold

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs <tests> -Session solid-remediation-<date>
```

- [ ] Battle's bag sets `CombatMath`; `PassThroughCombatMath` is no longer reached in battle
- [ ] `battle-responsibility-guard` green
- [ ] Before/after measurement recorded in the module's commit
- [ ] Goldens that move are explained as this fix, each one named

## Success criteria

This module's claim is also the program's **live proof** (see the map): on a live lawn at the 300-zombie
tier, an effect-driven hit resolves through `CombatMath`. Before this module that is false by
construction.

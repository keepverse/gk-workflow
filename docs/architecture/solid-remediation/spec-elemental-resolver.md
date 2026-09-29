# spec — `elemental-resolver`

**Module 6 of `solid-remediation`.** Register entry: **D14**. Depends on `battle-responsibility-guard`.

Replaces the retired `dead-vocabulary` module. Owner ruling 2026-09-17 turned D14 from a delete into a
fix, so the program now contains exactly one delete (X5's copy, in `estimator-parity`).

## Objective

The battle engine gains its **elemental sub-module**: every contest — attack, dodge, block, parry,
absorb, reflect, status apply — resolves from the element matrix with **omni as the additive base**.

Owner, 2026-09-17:

> *"Action have elementals (they will build become a matrix) then resolve the stats base on the matrix…
> when we resolve attack dodge, block, parry, absorb, reflect they basicly resolve from elemental matrix
> with omni is the base. So elemental resolver should be a sub module of battle engine and it play almost
> role in the damage calculation and shield mechanism."*

## What D14 actually is

D14 was filed as *"72 per-element parry/block/reflect channels have no reader in any mode"* and read as
dead vocabulary. It is not. Those slots are the **element half of a rule the codebase already follows
everywhere else**.

`CombatDerivedReader` resolves nine families as `omni + element`:

```csharp
snap.Get(CombatPowerOmni)        + snap.Get(PowerChannel(element))
snap.Get(CombatDefenseOmni)      + snap.Get(DefenseChannel(element))
snap.Get(CombatAccuracyOmni)     + snap.Get(AccuracyChannel(element))
snap.Get(CombatDodgeOmni)        + snap.Get(DodgeChannel(element))
…crit rate, crit resist, crit damage, crit-resist damage, penetration, absorption, amplification, reduction
```

and three families as **omni only**:

```csharp
ParryRate/ParryBreak/ParryStrength/ParryShred      → …Omni
BlockRate/BlockBreak/BlockStrength/BlockShred      → …Omni
ReflectRate/ReflectResistRate/ReflectDamage/…      → …Omni
```

The code comment calls that deliberate and cites `spec-evasion-chain.md` §3/§7. **The spec was read and
does not support it**: it contains no reference to "omni" at all, and §7's ban is narrower — *"Never … Let
`block.*` read `ShieldElementMatrix` — block is not a shield."* That forbids block reading the **shield**
matrix; it says nothing about per-element block channels. *"The spec never describes a per-component
breakdown"* is an argument from absence.

So the 72 channels are not dead: **three families are missing the element term the other nine have.**

## The formula — transferred, not invented

From `chaos-backend-service/docs/element-core` (owner: *"just copy elemental formula from it"*), which
this repo's stack was already built on:

**1. Omni is additive-only.** Never multiplied.

```
total_attacker = attacker_omni + attacker_element
total_defender = defender_omni + defender_element
```

> *"Omni stats chỉ cộng, không nhân"* — multiplying snowballs one-trick builds, and the additive rule is
> **anti-one-trick baseline protection**: every actor keeps a floor of capability in every element.

**2. The contest is a sigmoid on the difference.**

```
p = sigmoid((total_attacker − total_defender) / scalingFactor, steepness)
```

⚠️ **This bound is mathematical, not a gameplay cap.** The source is explicit: probability stays in [0,1]
*"do sử dụng sigmoid (ràng buộc toán học, không phải cap gameplay)"*. That distinction is load-bearing
here, because this repo bans hard progression ceilings — a sigmoid is not one, and must be commented as
such so a later audit does not "free" it.

**3. The interaction matrix stays intransitive** — no element dominates all. `ElementRingMatrix` and
`ElementMatchupRelation` already implement this; the module consumes them rather than re-deriving.

**Scope discipline:** copy the **formula** only. The wider chaos-backend-service ideas (status intensity
ODEs, refractory damping, resource distribution) are a future conversation the owner named as *"the
future"* — importing them here would be a feature pass wearing a remediation badge.

## What already exists — this is wiring, not building

| Piece | Where | State |
|---|---|---|
| Element ring matrix, matchup relations | `gk-core/src/FusionRpg.Core/Combat/Element/ElementRingMatrix.cs`, `ElementMatchupRelation.cs` | built |
| Element hub + payload | `ElementHub.cs`, `ElementPayload.cs`, `ElementPayloadComponent.cs` | built |
| `omni + element` reader rule | `CombatDerivedReader.cs` — nine families | built |
| Per-element parry/block/reflect channels | registered by the H.1 generator | built, **unread** |
| The contest helper | `ClampedContest` (per `spec-evasion-chain.md` §7 *"reuse ClampedContest"*) | built |

## Shape

1. **One resolver**, owned by the battle engine, that every contest calls. Not a helper each caller
   copies — D8 is in this program precisely because a copied formula passes a presence check.
2. **Extend `omni + element` to parry, block and reflect**, reusing `ClampedContest` as §7 requires.
3. **Feed the element payload into the packet** so the matrix is reachable — see below.
4. **Shield mechanism reads the same resolver.** The owner named shields explicitly. `block.*` still must
   not read `ShieldElementMatrix` (§7) — block resolving `omni + element` from the **combat** channels is
   a different thing from block reading the shield matrix, and the spec's ban is on the latter.

## Why this module precedes `battle-effect-math`

Measured 2026-09-17: wiring `CombatMath` onto battle's bag moved **zero** of 13,943 tests, because

```csharp
if (packet.ElementPayload == null || packet.ElementPayload.Count == 0)
    return signedAmount;                    // OverlayCombatMath.Finalize
```

and battle defaults the payload to empty (`components ?? Array.Empty<ElementPayloadComponent>()`,
`BattleRunState.cs:873`). **Without the element payload reaching the packet, D1's fix is inert.** This
module owns that seam, so it runs first and `battle-effect-math` depends on it.

## ActorHub

**Consumes** Hub output — it reads registered derived channels and contributes none. No new compose, no
private fold, no `ContributionSourceIds` grammar id.

## Numeric

- `omni + element` is an **addition of two magnitudes**: `long`, widen before multiplying, overflow throws.
- The sigmoid is a **ratio in [0,1]** — floating point is correct here, and precision is not overflow.
  Bounded ratios are the documented PS-8 exemption; comment each one with its class.
- In integer per-mille maths, divide by 1000 **last**.

## Tests to rewrite

Any test asserting parry/block/reflect ignore element is pinning D14 — restate to the contract: every
contest reads `omni + element`.

Assert the **rule**, not the numbers:

- omni-only and element-only actors with equal totals resolve identically (the additive rule)
- doubling omni never multiplies the element term (the anti-snowball rule, stated as an inequality)
- the matrix is **intransitive** — no element beats all others
- probability stays in [0,1] for extreme inputs, because the sigmoid bounds it mathematically

The channel-family count is a **closed vocabulary**: pin it, and say why.

## Boundaries

- **Always:** additive omni; reuse `ClampedContest`; comment the sigmoid bound as mathematical, not a cap
- **Ask first:** importing anything from chaos-backend-service beyond the formula — the rest is a later
  conversation the owner deferred
- **Never:** multiply omni by element. Never let `block.*` read `ShieldElementMatrix`. Never a second
  contest implementation

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Combat/** <tests> -Session solid-remediation-<date>
```

- [ ] Parry, block and reflect read `omni + element`
- [ ] One resolver; `battle-responsibility-guard` refuses a second contest implementation
- [ ] The element payload reaches battle's damage packets — proven, since D1 depends on it
- [ ] Shield resolution goes through the same resolver
- [ ] Additive, anti-snowball, intransitivity and [0,1] all asserted as rules
- [ ] No registered per-element channel is unread

## Success criteria

The registered vocabulary and the implemented vocabulary are the same set — reached by **implementing the
reading**, not by deleting the channels. D14 closes as a fix.

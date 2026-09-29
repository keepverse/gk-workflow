# Spec: `stack-combatant`

**Status: written against shipped code 2026-09-19.** Module id `stack-combatant`, row 4 of the
[legion-build map](../legion-build-map.md) (wave 2; depends on `member-stack`, `role-aware-placement`).
**Owner decision Q1 (2026-09-19):** *one combatant per stack, with HP and damage scaled by how many units
are alive (the Heroes 3 model), through a reviewed change to the battle engine's responsibility
register.* Law: [battle-engine-ssot.md](../battle-engine-ssot.md).

## Objective

A stack of *N* units enters `BattleEngine.Resolve` as **one** combatant. Its HP is the stack's pool, its
damage scales with how many units are still alive, damage that kills the top unit carries into the next,
and the battle reports how many units are left. This changes what damage and death **mean** for a
combatant, so by `battle-engine-ssot.md` §1 rule 3 it is an extension of the engine, registered in its
closed responsibility register — never a world-side trick.

Success looks like: every existing battle, delve, siege and expedition golden is byte-identical (no
setup today carries a count); a stack of 40 at 25% HP deals 10 units' worth of damage and comes back as
10 units; the answer is the same in every mode that ever fields a stack, because there is one function.

## Scope and non-goals

- **In:** a unit count on `BattleActorSetup`; one engine module (`StackBody`) that owns living units,
  outgoing scaling, overflow and the no-resurrection bound; `UnitsRemaining` on `BattleActorResult`; the
  register amendment; the world side passing the count in and reading it back.
- **Out:**
  - Statuses, riders and atom effects a stack applies apply **once** per application, not once per unit —
    the HoMM3 rule for creature abilities, and the reason the scale sits on the hit, not on the bag.
    Effect-driven damage stays on its own path (`battle-engine-ssot.md` §4 D1, `solid-remediation`
    `battle-effect-math`).
  - Initiative, targeting, movement and board footprint: a stack is one actor on one cell with one
    initiative, exactly like any combatant (responsibilities 5, 12, 14 unchanged).
  - Resurrection. No mechanism revives units; a heal restores the top unit only (§Design 4).

## §5 answers (battle-engine-ssot.md)

| Question | Answer |
|---|---|
| Which responsibility | **New register row 21, "Stack body"** — reviewed change (§Design 5) |
| Decide or resolve | Resolve. No choice is made; the count is input data and the arithmetic is deterministic |
| Mechanism or loop | Mechanism: what a hit does and when a combatant is dead |
| Which implementation it extends | `StackArithmetic` (from `member-stack`), the one `DispatchHit` site, the one death-cleanup site |
| Every mode | Yes — any setup with a count gets it in battle, delve, siege, expedition and web match alike; only the world produces counts today |
| Deterministic and seeded | Integer arithmetic, no RNG, no clock |

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | One HP seat per actor: `Hp = setup.CurrentHp ?? setup.MaxHp` | `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:33-37` |
| Built | Setup: `MaxHp`, `Atk`, `Defense` `long`; `CurrentHp` optional; optional fields serialize absent so goldens hold | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:42-44,169`; the absent-not-empty rule at `:601-611` |
| Built | Every basic hit reaches its target through one method, from both loops | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:1308` (`DispatchHit`), called at `BattleEngine.cs:651` and `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs:276` |
| Built | The hit is resolved once by the calculator | `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:388` (`calculator.Compute`) |
| Built | The damage pipeline and shield already take a `hitCount` | `gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs:63-66`; `gk-core/src/FusionRpg.Core/Combat/Shield/ShieldGate.cs:51` |
| Built | Death cleanup is inline, one site | `BattleEngine.cs:670-680` |
| Built | Result: `HpRemaining`, `Survived`, … | `BattleModels.cs:596-599` |
| Built | World: one setup per member row, pool as `MaxHp` | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:415-462` |
| Real gap | No count anywhere in battle; one setup is one body | `BattleModels.cs:7-217` |

## Design

### 1. Setup and result

```csharp
// BattleActorSetup (BattleModels.cs)
/// Units in this stack. Null = an ordinary single combatant (every setup that exists today).
/// Serialized ABSENT when null, so no golden moves.
public long? UnitCount { get; init; }
/// HP of one unit. Required when UnitCount is set; MaxHp must equal UnitCount × UnitHp.
public long? UnitHp { get; init; }

// BattleActorResult — appended, default null, serialized absent when null
long? UnitsRemaining = null
```

Validation at setup load: `UnitCount ≥ 1`, `UnitHp ≥ 1`, `MaxHp == UnitCount × UnitHp` (checked),
`CurrentHp ≤ MaxHp`. A violation throws — a malformed stack is a caller bug, not a combatant.

### 2. `StackBody` — the register's SSOT

`src/FusionRpg.Core/Battle/StackBody.cs` (new; the file does not exist yet), built on `member-stack`'s
`StackArithmetic`:

```csharp
public static class StackBody
{
    // 1 for any actor without a count. ceil(Hp / UnitHp) otherwise, via StackArithmetic.FromPool.
    public static long LivingUnits(ActorState a);

    // The one outgoing scale: signedDelta × LivingUnits, checked. Identity when UnitCount is null.
    public static long ScaleOutgoing(ActorState attacker, long signedDelta);

    // The one heal bound: a positive delta never lifts Hp above LivingUnits × UnitHp (no resurrection).
    // Structural limit, commented as such — it is not a progression ceiling.
    public static long BoundHeal(ActorState target, long positiveDelta);
}
```

### 3. Where it is called — three sites, each already the only site of its kind

1. **Outgoing.** `BattleRunState.DispatchHit` (`:1308`) scales `signedDelta` by
   `StackBody.ScaleOutgoing(attacker, …)` before the pipeline, and passes `LivingUnits(attacker)` as the
   pipeline's `hitCount`, which this module widens to `long` (Numeric types). So a shield sees *N* hits, which is the behaviour the parameter already exists for. The
   `OnDamageDealt` event's `HitCount` (`BasicAttack.cs:425`) carries the same number.
2. **Incoming damage.** Unchanged: the pipeline subtracts from the one HP seat. Overflow down the stack is
   **implicit** — the pool is HP, and `LivingUnits` is derived from it — so whole units die before the next
   is wounded without any per-unit loop.
3. **Heal.** Wherever a positive delta is written to `ActorState.Hp` (the pipeline's heal branch and the
   soul-eater path at `BattleRunState.cs:1370`), `StackBody.BoundHeal` bounds it.

Death stays the `Hp <= 0` gate at `BattleEngine.cs:670-680`: a stack dies when its last unit dies.

### 4. Reporting

`UnitsRemaining = LivingUnits(actor)` when `UnitCount` is set, else null. `HpRemaining` keeps its meaning
(the pool). `UnitsRemaining ≤ UnitCount` always (asserted).

### 5. The register amendment (reviewed change, Q1)

Added to `battle-engine-ssot.md` §3b in the same commit (a requirement of this module; the text is fixed
here so the review is of this spec):

| # | Responsibility | SSOT |
|---|---|---|
| 21 | **Stack body — a combatant made of N identical units** | `StackBody` over `StackArithmetic`: living units from the HP pool, outgoing damage × living units at the one dispatch site, overflow by construction, heal bounded to living units. Every mode; null count is the identity |

Why a new row and not a clause of #1 or #15: #1's calculator resolves **one** hit and must stay pure and
per-hit (its two call sites are its conformance evidence); #15 is death and body state after HP reaches
zero. The stack rule spans both, and a register row per responsibility is the §6 membership test's unit.

### 6. The world side

`DistrictAssaultResolver.BuildAnimateSetups` (`:415-462`) sets, for a row with `Count > 1`:
`UnitCount = Count`, `UnitHp = Hp`, `MaxHp = Count × Hp`, `CurrentHp = EffectivePool(Count, Hp, Wounds)`.
A row with `Count = 1` is built exactly as today (no `UnitCount`), which is what keeps every golden still.
`BuildSideOutcome` reads `UnitsRemaining` when present and derives top-unit wounds with
`StackArithmetic.FromPool(HpRemaining, Hp)` — the same function, so the world and the engine cannot
disagree about how many units a pool holds.

## Tunables

None. The count is state, the unit HP is the species'/raise's, and the scale is structural (a stack of
*N* is *N* units — not a balance number). Any future "stack fatigue" or diminishing return would be a new
tunable and a new register review; this module adds none.

## Numeric types

`UnitCount`, `UnitHp`, pools and scaled damage are `long`, `checked`, widened before multiplying.
**`hitCount` widens to `long` (corrected by the 2026-09-20 audit).** The first draft narrowed
`LivingUnits` into the pipeline's `int hitCount` (`gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs:66`;
`ShieldGate.AbsorbFinalized`, `gk-core/src/FusionRpg.Core/Combat/Shield/ShieldGate.cs:51`) with a checked
conversion. `Count` is unbounded by design (no cap, `raise-choice`), so a checked narrowing would throw
mid-battle for a large enough stack — an arithmetic ceiling on army size that the no-hard-ceiling rule
forbids when a wider type exists. Both parameters widen to `long` in this change; every existing caller
passes an `int`, which widens implicitly, so no existing behaviour or golden moves. Nothing here is `int`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault"
python gk-core/scripts/guard-actor-hub.py
```

## Structure

```
gk-core/src/FusionRpg.Core/Battle/BattleModels.cs          MODIFIED  UnitCount, UnitHp, UnitsRemaining (absent when null)
src/FusionRpg.Core/Battle/StackBody.cs             NEW       §2
gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs        MODIFIED  DispatchHit scale; heal bound
gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs          MODIFIED  setup validation; report UnitsRemaining
gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs, Combat/Shield/ShieldGate.cs  MODIFIED  hitCount int → long (audit 2026-09-20)
gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs MODIFIED pass count; read it back
docs/architecture/battle-engine-ssot.md            MODIFIED  register row 21 (required by this module)
```

## Testing strategy

- **Byte identity.** Every battle golden, the delve/siege/web goldens and the expedition hashes are
  unchanged with no setup carrying a count. Run, not argued.
- **Scaling.** Same attacker as one unit and as a stack of *N* at full HP: stack damage per hit is exactly
  *N* × the single-unit damage for the same RNG draw.
- **Overflow.** A hit larger than the top unit's remaining HP kills whole units first; `UnitsRemaining`
  equals `ceil(HpRemaining / UnitHp)`; never exceeds the entering count.
- **Heal bound.** A heal on a stack at 3 units + wounded top unit restores the top unit only; `LivingUnits`
  never rises.
- **Shield.** A stack's hit reaches the shield with `hitCount = LivingUnits`.
- **Mode conformance.** One test drives a stacked setup through battle, siege and delve profiles and gets
  the same `UnitsRemaining` for the same seed (rule 4 of the law).
- **Replay.** A recorded intent trace replays a stacked battle byte-identically (`battle-engine-ssot.md`
  §3c's replay test).
- **Register membership.** The §6 responsibility-registry test (when it exists) lists row 21; until then a
  source scan asserts `ScaleOutgoing` has one production call site.

## Boundaries

- **Always:** scale at `DispatchHit` only; convert pools through `StackArithmetic` only.
- **Ask first:** scaling statuses or riders by count; any diminishing return; resurrection.
- **Never:** expand a stack into *N* actors (Q1 option b, rejected); scale inside `OverlayCombatCalculator`;
  compute living units anywhere but `StackBody`; let a world resolver pre-multiply `Atk`.

## Success criteria

1. All existing goldens byte-identical.
2. Scaling, overflow and heal bound behave as tested, identically in every mode.
3. Register row 21 lands in `battle-engine-ssot.md` §3b in the same change.
4. The world round-trips `Count` through a battle with no second arithmetic.

## Interface exposed to dependents

`BattleActorSetup.UnitCount/UnitHp`, `BattleActorResult.UnitsRemaining`, `StackBody.LivingUnits` —
consumed by `field-battle-kinds`, `legion-equipment` (casualties), `raise-choice` (lifts its `Count > 1`
gate).

## Hard edges

- **Register amendment** (closed vocabulary; Q1 approves the shape, the text above is the review).
- **Ruleset stamp:** no `BattleRuleset.RulesetVersion` bump — null count is the identity, so no stored
  battle changes.
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 2** and grants a player-facing feature (a stack fighting
  as one combatant), so it rides **wave 2's single world bump**; the old claim of no world bump is withdrawn.
  Nothing hashed moves while no row has `Count > 1`, which is why no golden moves — the bump is what stops a
  world stamped before wave 2 resolving its battles the new way mid-life.
- **Golden re-bless:** none expected; any moved golden is a defect in the identity path.
- **Lifts the `Count > 1` gate** from `member-stack`: this module flips `StackCombatantLanded` to `true`
  in the commit that proves the scaling tests.

## Dependencies

`member-stack` (`StackArithmetic`, `Count`), `role-aware-placement` (only fighting rows become setups).

## Design-gate checklist

```
[x] Subsystems: battle engine (new mechanism, register row), world battle join.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: battle-engine-ssot.md (whole), DESIGN-GATE.md, PRINCIPLES.md §3-§13, the map and
    ideal. NOT read: battle-timeline-map.md, battle-turn-ideal.md (the Battle/turns row's documents);
    combat-damage-ssot.md. The dispatch and death sites were read in code instead.
[x] decisions.md checked: Battle engine is the SSOT row; Deployment hierarchy SSOT (HoMM3 top-unit).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: HP seat, DispatchHit and its two callers, Compute, hitCount, death cleanup,
    result record, the absent-when-null serialization rule.
[x] Read the surrounding section of every rule quoted (register §3a/§3b, §3c, §5).
[~] "Goldens byte-identical" is an acceptance test to run, not measured here.
[x] No §2 invariant contradicted: one engine, deterministic, no mode-owned mechanism.
[~] Corrections propagated: the register row is a requirement of this module, listed, not made now.
[x] No population count pinned.
[x] No event-refreshed cache.
[x] No ordering assumption (overflow is order-free by construction: the pool is one number).
[x] Actor magnitudes: consumes Hub output only (Derived snapshot unchanged); no private fold.
[x] No parallel path: one StackBody, one dispatch site, one arithmetic.
[ ] Enforcement-registry row owed: "stack scaling only in StackBody" — the one-call-site scan is the guard.
```

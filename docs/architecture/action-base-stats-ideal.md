# Action base stats — the ideal

**Status:** idea phase, 2026-09-18. Not a spec. No build authorized. Owned by
[`solid-enforcement`](solid-enforcement-map.md) as its wave 5, because it completes the owner's `atk`
retirement.

> **Narrowed 2026-09-18 by [action-enrich-ideal.md](action-enrich-ideal.md), on the owner's
> correction.** The change is only this: the hit's base moves from the actor's `atk` to the action
> (`BasePowerMilli × P(Θ)`, derived from the rung; the basic attack from tuning). The formula, the hybrid
> element split and the effect chain are already built and unchanged. `HitCount` is dropped from scope.
> Question 2 below is answered by the owner's earlier ruling (a deterministic function: the rung's
> `qPowerMilli`); question 1 carries over.

**Where it came from.** Answering `solid-enforcement`'s open question 1 (*"is the creature's authored
base attack also 'atk'?"*), the owner, 2026-09-18:

> *"use action base stats instead of atk. Each action have base stats, check attack action and
> extend it idea if missing, this idea usually use in almost rpg"*

## Step 0 — the principles, restated because they constrain every choice below

1. **Every RPG feature lives in the RPG layer.** PvZ is observed; the RPG contributes deltas and never
   depends on PvZ representing a concept. Where the lawn's damage number comes from is therefore an RPG
   decision, not a PvZ one.
2. **One ActorHub compose.** The actor's numbers (`combat.power.*`, defense, crit) compose once in the
   Hub. This idea adds nothing to the actor. It moves a number *off* the actor.
3. **One power ladder.** Contests read `Θ`, magnitudes read `P(Θ)`. A damage base that grows with
   level must come from `P(Θ)`, never from a new `f(level)`.
4. **The balance surface is data.** Every coefficient here lives in `gk-core/data/tuning/`.
5. **SOLID.** Today *how hard a hit lands* has two owners: the creature's `atk` and the action's own
   power budget. This idea gives it one.

## Which loop this extends

**Spine A — Level up and power** (`the-loops.md`): a creature's damage now grows through one path,
`Θ` reading the action's base, instead of two. **Combat depth** (`the-loops.md`, "hangs on places"):
moves differ from each other, which is the thing the genre uses to make a roster feel distinct. It
touches every place that fights: the lawn, battle, the Delve, siege.

## What this is, in the player's language

A creature hits hard because of **what it does**, not because of a hidden attack number. A Peashooter's
shot, a Chomper's bite and a Cherry Bomb's blast each have their own strength. The creature's growth
(level, aptitudes, gear, passives) multiplies whatever move it uses. Two creatures using the same move
at the same power deal the same damage, and a creature learning a stronger move gets stronger in a way
the player can see.

## What already exists — three buckets

### Built

| What | Where | Why it matters |
|---|---|---|
| The resolver already has a **"base × effectiveness"** slot | `OverlayCombatCalculator.cs:99`: `effectiveBaseDamage = request.BaseOverlayDamage * request.EffectivenessMultiplier` | The damage equation needs no new term. Only what *feeds* `BaseOverlayDamage` changes |
| **Skill effectiveness per category**, the genre's "damage effectiveness" | `skill.effectiveness.{category}` read in `BasicAttack.cs:377-378` | Path of Exile's mechanic already exists here |
| **An action power unit and a rung power curve** | `gk-core/data/tuning/action-rungs.v2.json`: `referencePower = PowerMath.One` (*"one reference action is worth one unit of power"*), `qPowerMilli` 1000 → 1323 → … (`qPower(r) = 1.75^((r-1)/2)`), `powerBudgetMilli` per rung | An action's worth is already a first-class, tuned number for skills |
| **A magnitude on the one ladder** | `AtomJson.cs:54-89`: `{"powerLadder": true, "kMilli": N}` resolves to `N × P(Θ)` | The level-invariant coefficient an action base needs is already a legal value shape |
| **One shared basic attack row** | `act.attack`; `BasicAttackFactory.cs:39-57` builds its `CompiledAction` | There is a single place to give the basic attack a base |

### Wiring gap

| What is inert | Where | What it means |
|---|---|---|
| **The basic attack's damage reads the creature, not the action** | `BasicAttack.cs:369` `BaseOverlayDamage = attacker.LiveAtk(state.Ledger)`, which is `Setup.Atk` via `BattleEngine.cs:101` | A creature attribute stands in for what should be an action property |
| **Action power is read for timing and budget, never for damage** | `ActionTimingTuning.WindupPerPowerMilli`; rung `powerBudgetMilli` prices what a skill's container may carry | The number exists; the damage path doesn't read it |

### Real gap

| What doesn't exist | Evidence | What would have to be built |
|---|---|---|
| **An action has no base-stats block** | `ActionRow.cs:15-60`: identity, grant, effects, timing, targeting, usability, eligibility, corpus metadata. No base power, no hit count | A small `ActionBaseStats` record on `ActionRow` / `CompiledAction` |
| **The basic attack is exempt from power** | `ActionTimingDerivation.cs:63-64`: *"it has no rung and no seeded power"*; `BasicAttackFactory.cs:42` `Rung: 0` | A base for the basic attack, authored in tuning |
| **The lawn's damage base is PvZ's number** | `OverlayCombatMath.cs:49` `baseDamage = Math.Abs(signedAmount)`: the vanilla hit amount | A decision on which number the lawn resolves from (open question 1) |

## Prior art — what the genre does, with numbers

**The pattern is near-universal: the move carries a level-invariant base, and the actor's stats scale
it.**

| Game | The move's base | What scales it | Documented lesson |
|---|---|---|---|
| **Pokémon** | Move **Power**, typically 40–150 | `Damage = ((2·Level/5 + 2) · Power · A/D / 50 + 2) · STAB · type · random` | Level and stats are the actor's; Power is the move's. Two moves on one creature differ only by Power, type and effect |
| **Final Fantasy XIV** | **Potency** per ability (auto-attack ~100, openers ~200, finishers ~500) | `Damage ≈ Potency · f(AP) · f(DET) · f(WD) / …` | *"Potency … does not increase or fluctuate as you level up"*: all level scaling lives in the actor. The failure mode was potency *inflation*, fixed by periodic normalisation passes |
| **Path of Exile** | Skill base damage (per gem level) plus **damage effectiveness** | Added and increased damage multiply the base | Effectiveness exists because added flat damage double-dipped on multi-hit skills. Low effectiveness is how multi-hit moves stay balanced |

**What this repo should take:**

1. **FFXIV's split is exactly the one power ladder.** A level-invariant coefficient on the action and
   all level scaling through the actor's `Θ` is `{"powerLadder": true, "kMilli": N}`, which already
   exists. No new curve is needed.
2. **PoE's warning applies to multi-hit.** A Gatling Pea firing four shots must not deal four times a
   one-shot base. Hit count divides the base, or effectiveness scales it down. It is never free.
3. **FFXIV's failure mode is inflation.** Keep every action's base as a coefficient against *one*
   reference action (`referencePower`), so a normalisation pass is one scalar, not an edit of every row.

Sources: [Bulbapedia — Damage](https://bulbapedia.bulbagarden.net/wiki/Damage) ·
[Smogon — the complete damage formula](https://www.smogon.com/dp/articles/damage_formula) ·
[FandomSpot — FFXIV potency](https://www.fandomspot.com/ffxiv-potency/) ·
[AkhMorning — FFXIV damage and healing](https://www.akhmorning.com/allagan-studies/how-to-be-a-math-wizard/shadowbringers/damage-and-healing/) ·
[PoE Wiki — Damage effectiveness](https://pathofexile.fandom.com/wiki/Damage_effectiveness) ·
[Maxroll — PoE damage for beginners](https://maxroll.gg/poe/getting-started/damage-for-beginners)

## The shape

### `ActionBaseStats` — what an action owns

```csharp
public sealed record ActionBaseStats(
    long BasePowerMilli,   // level-invariant coefficient; 1000 = one reference action (PowerMath.One)
    int  HitCount);        // ≥ 1; the base is SPLIT across hits, never multiplied (PoE's lesson)
```

**The base damage of one hit:**

```
basePerHit = BasePowerMilli × P(Θ_attacker) / 1000 / HitCount
```

This is the existing `powerLadder` value shape with the hit split applied. `BaseOverlayDamage` receives
`basePerHit`, and everything after it is unchanged: effectiveness, element matchup, `combat.power.*`
against defense, crit, the min-chip floor. **The creature's `combat.power.*` stays exactly what it is
today**, the actor's multiplier (FFXIV's AP), composed once in the Hub.

### Where each action's base comes from

| Action | Source of `BasePowerMilli` | Why |
|---|---|---|
| **Skills** (rung ≥ 1) | the rung's `qPowerMilli` by default (`action-rungs.v2.json`), optionally overridden per action | Skills already carry exactly this number as their power budget. Reading it for damage uses the value the budget was designed around, with no second curve |
| **Basic attack** (`act.attack`, rung 0) | `gk-core/data/tuning/action-base.v1.json` (new) `basicAttack.basePowerMilli` | It is exempt from rungs, so it needs an authored base. One row, one number |
| **Innate actions** | authored per action in the action corpus, as a coefficient | They are a species' signature move, which is where species differ |

### What happens to the creature's attack number

- **Battle:** `BattleActorSetup.Atk` and `LiveAtk` stop feeding damage. `BasicAttack.cs:369` reads
  the action's `basePerHit`.
- **Species `attackBase`** (captured from PvZ) stops being a runtime damage input. It stays a
  **seed-time signal**: `threatBand`'s `damageMilli` still reads it to classify how dangerous a
  species is, and it can inform which innate action a species gets and at what coefficient. That is
  classification, not a second runtime number.
- **Species with no attack** (`attackBase` 0: the hp-300/attack-0 group alone is 154 species, walls
  and producers) get **no damaging basic attack**. `DefaultAttackEligible` is derived from that at
  generation time, deterministically. With an action base they would otherwise fire a basic attack at
  the action's base, and even at a base of 0 the battle min-chip floor makes every landed hit deal at
  least 1 (`OverlayCombatCalculator.cs:371-372`: `Math.Max(1.0, Math.Ceiling(base × share))`).
- **`StatChannels.Atk`** (the legacy PvZ sheet channel, cheats' `P-ATK`/`Z-ATK`) is observation of
  PvZ's own field, and is unaffected.

### How species still differ

A Peashooter and a Gatling Pea both use `act.attack`. They differ, as in every RPG, by:

- **tempo**: attack interval, already classified per species (`SpeciesTempoProjection`),
- **hit count** on their innate actions,
- **element**, via `AttackComponents`,
- **`combat.power.*`**, from their build,
- and **their innate actions**, which is where the real identity lives.

### Alternatives rejected

| Alternative | Why not |
|---|---|
| Keep the creature's `atk` and add an action multiplier on top | That is the two-owner shape this idea removes. Two numbers answer "how hard", and a balance pass has to move both |
| A new per-level curve for action damage | Private `f(level)`; forbidden by the one-ladder rule. `P(Θ)` already is the curve |
| Multiply the base by hit count | PoE's documented double-dip. Multi-hit moves become strictly better |

## Tunables

| Number | File | Unit | Notes |
|---|---|---|---|
| `basicAttack.basePowerMilli` | `gk-core/data/tuning/action-base.v1.json` (new) | per-mille of `PowerMath.One` | the one authored base; **unmeasured at first** and marked so |
| per-innate `basePowerMilli` | action corpus (`gk-data/packs/fusion/data/seed/actions/**`, generated) | per-mille | emitted by the action generator from the species' seed-time signal (`attackBase`, tempo), never hand-edited |
| skills: `qPowerMilli` per rung | `gk-core/data/tuning/action-rungs.v2.json` (existing) | per-mille | reused, unchanged |
| `referencePower` | `gk-core/data/tuning/action-rungs.v2.json` (existing) | per-mille | the single normalisation scalar (FFXIV's lesson) |

Integer width: `BasePowerMilli × P(Θ)` is a magnitude, so it is **`long`**, widened before multiplying,
with the division by 1000 last (`CLAUDE.md` numeric rules). `P(Θ)` passes `int`'s range as a per-mille
product at `Θ` 3,213.

## What this deliberately does not decide

- **The numbers.** `basicAttack.basePowerMilli` and innate coefficients belong to a balance pass
  against a real corpus.
- **Changes to combat math.** `OverlayCombatCalculator` is untouched; only its input changes.
- **Goldens.** Battle goldens will move, because every basic attack's base changes. That is expected,
  and the spec will triage it in a single re-bless with the reason written down.
- **What an innate action is.** That belongs to the action corpus program; this idea only gives it a
  base.

## Open questions — owner decisions, each with a recommendation

1. **On the lawn, which number does a hit resolve from?** Today it is PvZ's vanilla hit amount
   (`OverlayCombatMath.cs:49`), and overlay math already *replaces* vanilla's computation per hit
   rather than adding to it (traced 2026-08-27 and recorded in `tasks/class-system-plan.md`
   decision 12: *"overlay mode strictly replaces vanilla's computation per hit, never adds to it"*). **Recommendation: the action's base.** The vanilla hit becomes a trigger
   only ("a hit happened, from this actor"), and the RPG owns the number end to end. That is the
   RPG-layer rule in its purest form, and it means the lawn and battle resolve the same move to the
   same damage. The cost is lawn feel: it changes, and `lawn-tuning-profile` owns tuning it.
2. **Skills: rung default, or authored per skill?** **Recommendation: rung default, with an authored
   override allowed.** Most skills then need no new data, and the override covers the signature moves.

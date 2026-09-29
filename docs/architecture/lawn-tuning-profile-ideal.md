# Lawn tuning profile — the ideal

**Status:** idea phase, 2026-09-16. Not a spec. No build authorized. **All three owner questions ruled 2026-09-16** —

> **Updated 2026-09-17.** Gains **M6** (overlay damage bypassed both armour layers — found and fixed the same day) and a correction to **M5** (the zombie side now has real data: `summonLevel`, 10 designer-authored rungs across all 227 zombies).
see "Owner rulings"; ready for `/spec`.
**Program id:** `lawn-tuning-profile`. **Found by:** `lawn-combat-wire` L-N2 (proof 5 blocked) and L-N38.
**Owner prompt (2026-09-15):** *"totally bug for lawn game, did we have tuning profile for each game feature, the lawn
run maybe need specific stats running and buff for both plant and zombie side"*. **Owner order:** measure on a clean
player first (done, below), then open this idea with those numbers.

---

## Which loop this extends

- **Place 1 — Lawn (first core)** (`docs/guide/the-loops.md`). The lawn is the first thing a player plays and it feeds
  souls, XP, almanac and deploy. Today its numbers stop reading as Plants vs. Zombies after three aptitude points.
- **Spine A — Level up and power.** Dave's level and free-build aptitudes are supposed to *show* on the lawn
  (`aura-skill/spec-commander-lawn-bridge.md` §1: *"their level and primary stats distribution will vibe in pvz lawn
  run like HoMM3 heroes"*). Today they show so strongly that vanilla values stop mattering.
- **Combat depth** hangs on both: the lawn basic-attack rider, its stamina cost and its hit roll are the combat
  language the lawn speaks.

This idea adds no loop, no stock, no player class, and no stamina gate. "No stamina gate" in `the-loops.md` means the
player's wallet. This doc is about an **actor's** combat stamina pool, which `resource-hub-ssot.md` already owns.

## What this is

A lawn match should look like Plants vs. Zombies with an RPG layer on top: a Peashooter's pea still matters, a zombie
still takes a recognisable number of peas to fall, and a stronger commander build makes the lawn *noticeably* better
rather than making vanilla numbers noise. Battle, delve and siege keep their own numbers.

The ask is **per-mode tuning**: one ActorHub, one combat formula set, one power ladder — and a small, versioned data
profile that tells the Hub how a lawn actor's RPG magnitudes relate to its vanilla base, on both sides of the board.

---

## Principles this must keep (stated here, not linked)

1. **Every RPG feature lives in the RPG layer; it is never built by changing what PvZ is.** Vanilla fields are the
   foundation. The RPG contributes signed deltas. A profile changes RPG numbers, never PvZ's.
2. **One ActorHub compose / one read.** Lawn, sheet, battle, delve, siege and sim compose actor combat numbers once, in
   `ActorHub`, and contribute through `IActorStatSubsystem`. A `LawnStatComposer`, a private fold, or a lawn copy of
   the aptitude resolver is a defect. `BattleStatComposer` is grandfathered debt, not a template.
3. **SOLID is binding.** Extend by feeding data into the existing subsystems (O), not by forking a lawn path.
4. **One power ladder.** Contests read `Θ`; magnitudes read `P(Θ)`. A profile may choose *which* `Θ` an actor reads
   and *what share* of `P(Θ)` a family takes. It may not add an `f(level)`.
5. **One combat formula set** (`decisions.md` "Combat resolution SSOT"). The overlay calculator and apply pipeline are
   the same everywhere. The only per-host knob today is `CombatProfile` (the chip floor). A profile changes inputs,
   never formulas.
6. **The balance surface is data** (`tunables-ssot.md` T1–T7): `gk-core/data/tuning/<domain>.v{n}.json`, versioned, never
   hand-edited, every number with its unit, a missing key is a load rejection, and a tuning change must not be able to
   hide a code regression. A profile holds **multipliers and selections**, never a copy of another file's numbers.
7. **No hard progression ceilings.** A profile may scale a share down; it may not cap a magnitude.
8. **Standalone-first is capability, not pitch.** The lawn profile only applies where the lawn runs. Every web mode
   keeps its current numbers and stays playable with Fusion closed.
9. **Record-then-drain, deltas not absolutes.** Nothing here moves work onto the hit path.

---

## What the lawn numbers are today — measured

All live, real Adventure 2, MelonLoader 3.9, allocations made through `POST /api/aptitudes/allocate` unless marked.

| Case | Θ read by the actor | Plant attack (vanilla 20) | Plant max HP (vanilla 300) | Stamina max | Stamina regen per 100 ms tick | Exhausts? |
|---|---|---|---|---|---|---|
| Player 1 — tainted (1,440 points spent vs budget 135) | 0 (L-N38) | — | — | 1,009 | 17.2 | never (3 runs) |
| Player 6 — no allocation | 0 (L-N38) | 20 | 300 | 53 | 0.2 | yes (proof 4 closed) |
| Player 6 — Might 2, Vigor 1 (3 points), before L-N38 fix | 0 | 554 | 620 | 1,706 | 29.2 | never |
| Player 6 — same allocation, after L-N38 fix (`e689c277`) | 6 | **1,641** | **1,271** | **5,142** | **87.6** | not measured; spend is ≤ ~65 per second |
| NormalZombie on that board, after the fix (vanilla atk 50, HP 270) | 6 | **574** | **1,915** | — | — | — |

Evidence: `docs/research/perf/_lawn-theta-hydration-live.json`, `_lawn-combat-proof4-exhaustion-clean-player.json`,
and the L-N2 notes in `tasks/lawn-combat-wire-todo.md`.

Every "after" number matches the arithmetic below to the unit, so the table is the formula working as written — not
noise. With three points the pea is 82× vanilla. At the pin (Θ = 20, `P` = 680) the same build would give +4,536
attack.

---

## What already exists

### Built

| What | Where | Proof |
|---|---|---|
| One lawn Hub | `CheatState.cs:49` → `ActorHubBootstrap.CreateDefault` (`ActorHub.cs:150-176`): `ResourceBaselineSubsystem` (order 90), `RpgProgressionSubsystem`, `AptitudeSubsystem`, `AtomDerivedSubsystem`, `StatusDerivedSubsystem` | live trace `subsystems` field |
| Lawn base is the vanilla field | `EntityApply.cs:43-47` (`MaxHp = p.thePlantMaxHealth`, `Atk = p.attackDamage`) | live `primaryAtk 20` |
| RPG bonus stacks on the vanilla base | `ActorHub.MergeAppliedCombat` (`ActorHub.cs:89-104`): `Atk = primary.Atk + bonusAtk`, `MaxHp = primary.MaxHp + bonusMaxHp` | live `appliedAtk 1641` |
| Aptitude magnitude read | `AptitudeReadFunctions.cs:52-65`: `kMilli × share^γ × P(Θ) / 10⁶`; `aptitudes.v8.json` `read.magnitude` | trace arithmetic matches |
| Family-scoped coefficient dials | `AptitudeResolver.EffectiveKMilli` (`AptitudeResolver.cs:92-104`): `recovery.scaleMilli` 374 on `resource.regen`/`combat.shield.regen`, `mitigation.scaleMilli` 300 on six defence families | `aptitudes.v8.json` `recovery`, `mitigation` |
| Resource pools on the ladder | `ResourceBaselineSubsystem.cs:31-36` (`Θ = max(1, ActorIndex)`); `BattleModels.cs:400` pool `BaseHp(Θ) × poolShareMilli / 1000`; `:452` regen `pool × regenShare / 1000 / 10` per tick | player 6 no allocation: 53 / 0.2 |
| Θ reaches every lawn actor | `HydratedPowerIndexProvider.Key` = player id (`IPowerIndexProvider.cs`, fixed `e689c277`, L-N38) | live Θ 6 on GatlingPea and zombies |
| Battle combat baseline | `BattleBaselineSubsystem` (registered `BattleHubCompose.cs:42`) seeds `combat.defense/accuracy/dodge/crit.rate/crit.resist` from `BattleRuleset.BaseAccuracy(Θ)` etc. (`BattleModels.cs:358-359`) | battle parity P(hit) 0.90 (`decisions.md` Combat resolution SSOT) |
| Battle enemies scale as content | waves `MaxHp = BaseHp(Θ)`, `Atk = BaseAtk(Θ)` (`WaveCatalog.cs:176-177`); Zomboss build applied at the content level (`WebMatchService.ApplyZombossPattern`, `:481-505`) | shipped web matches |
| Per-host combat knob | `CombatProfile(MinChipShareKPm)` (`CombatProfiles.cs:9-15`): Overlay 0, BattleSim 50; lawn default at `OverlayCombatCalculator.cs:60`, battle at `BasicAttack.cs:379` | shipped |
| Fixed-Θ provider | `FixedPowerIndexProvider` (`IPowerIndexProvider.cs:30-37`) | used by battle setups |
| Ladder ratio function | `ContentScale.Milli(Θ) = P(Θ) × 1000 / pinValue` (`ContentScale.cs:15-20`) | items |

### Wiring gap — machinery exists, inert for this use

| What | Inert line | Why it matters here |
|---|---|---|
| Explicit resource tuning per Hub | `ResourceBaselineSubsystem(…, BattleResourceTuning? tuning = null)` (`ResourceBaselineSubsystem.cs:22`); every production caller passes null (`ActorHub.cs:155`) | a lawn Hub could read a lawn resource row without touching battle |
| Explicit aptitude tuning per Hub | `ActorHubBootstrap.CreateDefault(aptitudeTuning:)`; every caller passes `AptitudeTuningHub.Tuning` (`CheatState.cs:50`) | the resolver already takes its tuning as a parameter |
| Combat baseline on the lawn | `BattleBaselineSubsystem` exists; `CreateDefault` never registers it | lawn actors sit at accuracy 0 vs dodge 0, so `pHit = Sigmoid(0)` = 0.5 and untuned riders miss half the time (L-N7, measured 3 misses of 13) |
| Lawn content Θ | `IPowerIndexProvider.ContentIndex` has no lawn caller; `SoulSinkPolicy.VanillaPvzTheta = 20` is the documented placeholder for "the vanilla-PvZ Θ signal", a named unbuilt follow-up (`decisions.md` row "Caps"; `RpgStore.Souls.cs`) | a lawn zombie has no content Θ to read |
| Zomboss as the lawn's army | `EnsureZombossPlayer` / `MintForZomboss` (`RpgStore.ZombossDeploy.cs:25,42`); `MatchHost.cs:310` says a vanilla zombie *is* Zomboss's army; the `zomboss:{playerId}` scope key has no lawn consumer | the lawn could give zombies Zomboss's build instead of the player's |
| `CombatProfile` in data | hardcoded record (`CombatProfiles.cs:12,15`) | the only per-host knob is not tunable |

### Real gap — nothing exists

- **No mode selector.** No file, loader, or Hub input says "this actor is on the lawn". Every stat hub (`AptitudeTuningHub`,
  `PowerTuningHub`, `StatsTuningHub`, `BattleRuleset.ConfigureResources`) is one static instance, and the injector and
  server load the same files (`RpgHost.cs:130,161,166,195`; `Program.cs:84,179,209,215`).
- **No base-relative magnitude read.** Both read modes (`contest`, `magnitude`) ignore the actor's own base. There is no
  read that says "this bonus is a share of *this actor's* attack".
- **No lawn calibration target.** `spec-lawn-combat-calibration.md` lists the vanilla anchors (pea 20, 1.5 s interval,
  NormalZombie 270 HP, ~20 s to kill) beside the ladder pins, and converts neither into the other.

---

## Why the numbers blow up — five mismatches, each traced

> ⚠️ **A sixth was found on 2026-09-17 and is already fixed** — overlay damage bypassed both armour
> layers entirely. See **M6** in the enrichment below, which also records that **M5's missing zombie-side
> model now has real data behind it** (`summonLevel`, 10 designer-authored rungs across all 227 zombies).


**⛔ M1's ATTACK half is fixed at the source, 2026-09-16 — do not re-solve it here.** Owner ruling:
*"Write attack damage is a bug … we already have battle engine and damage calculator in our rpg, so if
we give in game damage it cause our battle engine abundant."* Both attack writes are commented out in
`EntityStatWriter` (`WritePlant`'s `p.attackDamage`, `WriteZombie`'s `z.theAttackDamage`) with the reason
recorded inline. A Peashooter's `attackDamage` stays vanilla 20; RPG damage arrives through the engine
and its lawn rider, which is where it was always resolved. **What remains of M1 is the hp/armour half** —
`p.thePlantMaxHealth` and the zombie armour fields are still assigned composed absolutes, so a
ladder-sized `progression.bonus.maxHp` still lands on a vanilla 300. That is this module's remaining
scope, and it shrinks again if the transport becomes a delta (`species-hub-wire-ideal.md`).

**M1. A ladder-sized flat bonus lands on a vanilla base.** `progression.bonus.{maxHp,atk,defense,arm1,arm2}` read
`k × share × P(Θ)`, where `P` is the HP ladder (680 at the pin). Might → attack is `kMilli` 10000, so a full Might share
is +10 × `P(Θ)`. Share is the *proportion* of spent points, not their count (`aptitudes.v8.json` `read._note`), so three
points all in Might buy the same bonus as 135. The only consumer of these five families is `MergeAppliedCombat`, read by
the lawn writer (`EntityApply`), `SimEngine` and `UniqueBoundLoadout`. Battle never reads them: `BattleEngine.LiveAtk`
recomposes `Setup.Atk = BaseAtk(level)`. So the family's one real consumer lives in vanilla units (pea 20), and its
coefficient is sized in ladder units. This is the documented failure in prior art (flat bonuses at progression scale on
a small base — WoW downranking, PoE's damage effectiveness).

**M2. Aptitude resource edges dwarf the baseline pool.** The baseline stamina pool is 0.5 × `P(Θ)`
(`poolShareMilli` 500). Every one of the 12 aptitudes feeds `resource.max.stamina` at 8 to 26 × `P(Θ)` at full share
(`kMilli` 8000 for seven aptitudes, up to Might 18000 and Vigor 26000), and all 12 also feed `resource.regen.stamina`.
Since shares sum to 1, **any** allocation adds at least 8 × `P(Θ)` to a 0.5 × `P(Θ)` pool. Any allocation makes the baseline a
rounding error, which is why exhaustion disappears the moment a player spends a point (L-N2).

**M3. The regen edge unit is unverified.** The runtime `resource.regen.*` channel is per 100 ms tick
(`BattleModels.cs:452`, `spec-resource-subtick.md`). The aptitude regen coefficients were ported on 2026-08-26 from the
CombatSim POC (`aptitudes.v8.json` `_meta.status`), whose pool accrues `regen × rounds` (`gk-core/tools/CombatSim/ActionEconomy.cs`
`ActorPools.Tick`), and a battle round is 1,000 ms (`battle.v5.json` `roundDurationMs`). If the edges were authored per
round, they read 10× too strong on the runtime clock, in battle as well as on the lawn. **Unverified:** the recovery
dial (`recovery._scaleWhy`) was solved against peer damage, and whether that measurement used the same time base has
not been traced. This is a task for the spec, not an owner question.

**M4. The stamina cost is flat while the pool and regen scale.** `basic.baseAmountAtRung1` 25 is emitted as a constant
(`ActionCorpusComposer.cs:173`, `ValueSpec.Of(...)`), derived at the pin only (`action-corpus-cost-templates.v2.json`
`_meta.kindsNote`: sustainable 17 × 1.5 s = 25.5 at Θ = 20). Below the pin the actor starves (player 6 no allocation:
regen 2 per second against a cost of 25 per shot); above it the cost vanishes (Θ = 100: regen ≈ 117 per second). The
calibration spec's own boundary says magnitude stays `anchor(Θ) × q(rung)`, so this is a defect against an existing
spec rule, not a design question.

**M5. The zombie side has no model of its own.** On the lawn a zombie reads the **player's** Θ (L-N38, per
`spec-commander-lawn-bridge.md` §1) and the **player's commander allocation** merged with its species allocation
(`CheatState.cs:186`: `resolveCommanderAllocation: _ => CommanderAllocation.Resolve(...)` ignores side). So the player's
Might makes enemy zombies hit harder. In web battle, enemies read the **content** level and **Zomboss's** build
(`WaveCatalog.cs:176-177`, `ApplyZombossPattern`). The lawn and battle disagree on who owns the enemy's power.

The combat rider also reads Hub power on top of the vanilla hit (`L-N3` note: a Conehead bite, vanilla 50, crit −264 at
Hub power 42), so `combat.power.*` carries M1's shape too, through the overlay calculator rather than a Unity field.

---

## ⚡ Enrichment 2026-09-17 — armour is a live damage layer, and the zombie side now has a model

Idea phase. Records measurements and one shipped fix. No build authorized by this section.

Two things changed on 2026-09-17 that this document was written without, and both land on defects it
already names.

### M6 (new). Armour was a live damage layer that overlay damage bypassed entirely — **fixed**

This document does not mention armour anywhere, which was correct when it was written: nothing in the
lawn tuning path touched it. That was itself the defect.

`EntityStatWriter.AddZombieHp` handed a negative FA10 delta straight to `ResourceDeltaMath.Apply`, which
only knows about health. So **every overlay damage source bypassed both armour layers** — a Buckethead
bled health with its bucket at full. Armour was read (dumps, stat writes, base-stat capture) and written
(`WriteZombie`'s `arm1`/`arm2`), but never *spent*.

**This contradicted a ruling already written into the writer itself**, a hundred lines above the bug:

> *"What the lawn receives instead is a DELTA over the fields PvZ actually has — **hp, armor1, armor2**
> (owner, same ruling)"*

Two of those three fields were never debited.

**Fixed 2026-09-17** (`ArmorCascade`, Core): damage now spends `armor2 → armor1 → hp`, and only what
survives both layers reaches health. Healing stays health-only and deliberately does not refill armour —
restoring armour is a separate feature with its own design, and inventing it inside a damage fix would
have been a silent behaviour change.

**Why this belongs in a tuning-profile document rather than only in a changelog:** armour is now a real
term in the lawn's damage equation, so it is part of the lawn's numbers. Measured across the 911-row
capture: **75 zombies carry `armorMaxBase`**, taking 22 distinct values from **20 to 32,000**.

> ⚠️ **Corrected 2026-09-18 — "75" undercounts the surface this fix touches.** A further **23
> zombies carry `armor2MaxBase`** (200 → 30,000), and **95 carry at least one layer**. That matters
> here specifically, because `ArmorCascade` spends **`armor2` → `armor1` → `hp`** — the second layer is
> spent *first*. So the 20 zombies that carry only `armor2MaxBase` are exactly the ones whose very
> first point of mitigation the original sentence omitted. A profile that tunes lawn damage while
> treating armour as absent is tuning the wrong equation for **95** types, not 75.

**What this fix is, and what it is not — settled by R-LT1 below.** The cascade is a **foundation
spend-order correction**: overlay damage was reaching `theHealth` while two vanilla fields PvZ owns sat
untouched, and it restores the order PvZ itself implies. It is **not** the RPG modelling armour, and it
never becomes that. Armour stays PvZ's; the RPG's one mitigation mechanic is **shield**, which already
works on every actor. Flat is not a placeholder here — it is the correct and final shape for a field we
observe rather than own.

### M5 — the zombie side now HAS a model of its own, and it is the game's

M5 says the zombie side has no model: on the lawn a zombie reads the **player's** `Θ` and the player's
commander allocation, so *"the player's Might makes enemy zombies hit harder."*

The diagnosis stands. What changed is that **the raw material for a zombie-side model now exists and is
the game's own**, rather than needing to be invented:

> ⚠️ **Re-measured 2026-09-18 after an audit.** The first version of this table mixed two frames:
> it counted distinct values **including 0** while quoting a range that **excluded** it, so three rows
> read as if no zombie had a zero. The corrected table separates the two, because for a tuning profile
> the zero is the interesting part — it is the population a per-field model has nothing to say about.
> `summonLevel` is also **10 distinct values, not 10 rungs**: they are `{0,1,2,3,4,5,6,7,10,15}`, so a
> spec that maps "rung" onto Θ by index will mis-map. `VoodooDollZombie` sits at 0.

| Field | Coverage | Distinct (incl. 0) | Range over nonzero | Zeros |
|---|---|---|---|---|
| `summonLevel` | 227 zombies | **10 values** `{0,1,2,3,4,5,6,7,10,15}` | 1 → 15 | 1 |
| `summonWeight` | 227 zombies | 11 | 300 → 4,000 | yes |
| `hpBase` | 227 zombies | 38 | 1 → 300,000 | none |
| `attackBase` | 227 zombies | 14 | 50 → 7,200 | yes |
| `armorMaxBase` | **75** zombies | 22 | 20 → 32,000 | 152 |
| `armor2MaxBase` | **23** zombies | — | 200 → 30,000 | 204 |

`summonLevel` is a **difficulty tier the game's own designers authored** — which wave tier may summon a
zombie — and `summonWeight` is how often. That is precisely the signal M5 says is missing: a zombie's
strength as a property of the zombie, not of the player who is fighting it.

**It does not close M5 on its own**, and the distinction matters. M5 is an *ownership* defect —
`CheatState.cs:186`'s `resolveCommanderAllocation: _ => ...` ignores side, so the player's allocation
reaches the enemy. New data does not fix a resolver that ignores its argument. What the data does is
remove the excuse: the shape of the fix ("read the zombie's own tier") now has a real table behind it
instead of a number someone would have had to invent.

### What this adds to the three buckets

**Built.** `ArmorCascade` and its wiring in `EntityStatWriter.AddZombieHp` (damage spends armour before
health, `armor2 → armor1 → hp`). `type_base_stats`, 911 rows including `summonLevel`, `summonWeight` and
both armour maxima.

**Wiring gap.** Nothing in the lawn tuning path reads `summonLevel` or `summonWeight` yet — the table is
populated and unconsumed. And `CheatState.cs:186` still resolves commander allocation without regard to
side, which is M5's actual mechanism and is one argument, not a missing system.

**Real gap.** No decision on whether armour participates in RPG mitigation or stays a flat buffer. No
zombie-side `Θ` source — reading `summonLevel` as a tier is a proposal here, not a built path, and it
would have to land on the one power ladder rather than as a private curve.

### Open questions this adds — owner decisions only

1. ✅ **RULED 2026-09-18 — armour stays PvZ's; the RPG's mitigation is SHIELD (R-LT1).** Do not import
   the PvZ mechanic. Shield is the one mitigation system and already works on every actor.
   Original: **Does armour participate in RPG mitigation, or stay a flat pre-health buffer?** Today it is flat:
   `ArmorCascade` subtracts and nothing reduces the incoming amount. Making `combat.defense.omni`,
   shields or penetration apply to armour is defensible and is also how a Buckethead stops being a fixed
   150-point delay and starts being a defensive *stat*. Flat is the honest minimum that ships; the
   question is whether it is the design.
2. ✅ **RULED 2026-09-18 — yes, mapped onto the one ladder, never a private `f(summonLevel)` (R-LT2).**
   Original: **Should `summonLevel` be the zombie side's `Θ` source?** It is a designer-authored 10-rung tier with
   full coverage, which is exactly the shape `threat-band` already uses for creatures. If yes, it must
   map onto the existing ladder (`Θ` contests, `P(Θ)` magnitudes) — **never a private `f(summonLevel)`**,
   which is the defect `ssot-power-scale.md` §10 exists to prevent. If no, M5 needs a different answer,
   because today's answer is "the player's own Θ", which the document already calls a defect.

---

### R-LT1 — armour stays PvZ's; the RPG's mitigation is SHIELD, and it already covers every actor

**Ruled (corrected 2026-09-18):** *"do not copy the pvz mechanism to my game. i only have shield
mechanism and it work in all actor."*

> ⚠️ **An earlier version of this ruling said armour should "participate in RPG mitigation". That was
> wrong and is retracted.** It proposed importing a PvZ foundation field into the RPG stack — designing
> `combat.armor.*`-shaped behaviour, typed-armour interactions, and an armour-broken event for the RPG
> layer to consume. That is the repo's own hard rule violated in the less obvious direction: the rule is
> usually quoted as *"an RPG feature is never built by changing what PvZ is"*, and its mirror is just as
> binding — **a PvZ mechanic never becomes an RPG concept either.** The layers stay separate in both
> directions.

**The division, stated so it is not blurred again:**

| | Owns | In our stack |
|---|---|---|
| **PvZ foundation** | `theFirstArmor`/`theSecondArmor` — two typed, breakable casings on zombies | **Nothing.** We observe the fields and contribute signed deltas; we never model them |
| **The RPG layer** | **Shield** — the one mitigation mechanic, elemental, with capacity, toughness, regen and penetration | Everything. It is ours, and it is the answer to "how does an actor resist damage" |

**Shield already works on every actor, which is why no second mechanic is needed.** Verified:
`ShieldGate` is constructed with a `CombatActorResolve` (`ShieldGate.cs:15-27`) and has no plant/zombie
branch anywhere in its contract, and the shield channels appear on **both sides of the species corpus** —
`combat.shield.capacity.omni` and `combat.shield.toughness.omni` on 161 species, `combat.shield.pen.omni`
on 82, spanning plants and zombies alike. It is one mechanism over all actors, exactly as the owner
states.

**So `ArmorCascade` is a foundation spend-order correction and nothing more.** It exists for one reason:
overlay damage was reaching `theHealth` while two vanilla fields the foundation owns sat untouched. It
restores the order PvZ itself implies (`armor2 → armor1 → hp`) and stops there. It is **not** the RPG
modelling armour, and it must not grow into that.

**What this forecloses, deliberately:**

- **No `combat.armor.*` channels.** The 261+ registered channels gain nothing here.
- **No armour entry in the actor layer stack.** That vocabulary is closed, and armour is not a layer.
- **No typed-armour RPG interaction.** `theFirstArmorType` is PvZ's business; a cone and a bucket differ
  to PvZ, and to us they are both "a vanilla field that absorbs before health".
- **No armour-broken event for the RPG to consume — and this is the strongest of the four.** Owner:
  *"armor break is redundant because we already have item durability, shield have durability and break,
  so we do not double mechanism."*

  **The RPG already has two break/wear systems, and armour-break would be the third.** Verified:
  `ShieldEvents.cs:9` declares `shield.broken`, and item durability has its own spec
  (`deployment-hierarchy/spec-item-durability-repair.md`) carrying wear, repair and the craft-wear
  formula ruled in `gear-climb` R-G1. A third would be a parallel mechanic answering a question two
  systems already answer, which is the SOLID defect this repo overturned for `BattleStatComposer` —
  **two engines, same question**.

  So a "defence stripped" moment is **`shield.broken`**, and a "this gear is wearing out" moment is
  **item durability**. `theFirstArmorBroken` stays what it is: a vanilla flag on PvZ's own casing, which
  the foundation owns and we observe.

**The balance question this leaves is a genuinely different one**, and smaller: whether the *lawn tuning
profile* wants a zombie's vanilla armour to be worth more or less relative to RPG-side shield — which is a
question about **numbers on two separate systems**, not about merging them.

### R-LT2 — `summonLevel` is the zombie side's `Θ` source, mapped onto the existing ladder

**Ruled: yes.** A designer-authored **10-rung** tier with **complete coverage** across all 227 zombies is
exactly the shape `threat-band` already uses for creatures.

**This is the fix for M5's actual defect**, which is an ownership error rather than a missing number:
today a lawn zombie reads the **player's** `Θ` and the **player's** commander allocation
(`CheatState.cs:186` — `resolveCommanderAllocation` ignores side), so *the player's own Might makes enemy
zombies hit harder*. Reading the zombie's own authored tier replaces a borrowed number with an owned one.

> ⚠️ **Hard requirement, not a preference.** It maps onto the **one power ladder** — contests read `Θ`,
> magnitudes read `P(Θ)` — and **never a private `f(summonLevel)`**. `ssot-power-scale.md` §10 is a closed
> inventory, and a fresh level-derived curve in a subsystem is the exact defect that let three
> incompatible curves ship at once. `summonLevel` supplies a **rung**; the ladder supplies the magnitude.

---

## Prior art

Tags: **[V]** read on the linked page · **[S]** search snippet or secondary source · **[calc]** computed here.

**Mode-normalised stats — the character is kept, the mode overrides how it counts.**
- **ESO Battle Leveling [V]:** Cyrodiil and Imperial City scale max resources, regen, armour and ability costs to
  "average CP 160" while reading the player's own attribute allocation; crit is not scaled; set bonuses and enchants
  leak through. <https://help.elderscrollsonline.com/app/answers/detail/a_id/31249>
- **WoW Legion PvP templates [V]:** in PvP instances stats are replaced by a per-spec template (ilvl 850 budget) plus
  per-spec multipliers (e.g. caster primary ×1.55, healers −25% damage to players). Removed in BfA because templates
  "may have given up too much in terms of PvP dynamics and customization".
  <https://www.bluetracker.gg/wow/topic/us-en/20747314610-pvp-stat-templates-and-spell-multipliers-july-15th-2016/>
- **FFXIV level sync / Destiny 2 power delta [S]:** content syncs you *down* to the activity (item-level cap; Grandmaster
  Nightfalls hold you 25 below enemies; raids −10). Normalisation relative to the activity, not a fixed template.
- **Genshin [S]:** no normalisation; level is a difference term in the defence multiplier —
  `(Lc+100) / ((Lc+100) + (Le+100))` = 0.500 at parity, 0.487 at 90 vs 100 **[calc]**, about 2.6% per 10 levels.
  <https://library.keqingmains.com/combat-mechanics/damage/damage-formula>

**Per-mode multiplier tables.**
- **LoL ARAM [V]:** per-champion mode tuning — +20% energy regen for four champions, +20% tenacity for 16, damage from
  beyond 1,000 units −15% rising to −30%. <https://www.leagueoflegends.com/en-gb/news/game-updates/aram-2023-preview/>
- **WoW BfA Azerite [S]:** every item-level-scaled part of a trait set to 50% in PvP; non-scaling parts untouched.
- **ESO Battle Spirit [S]:** −50% damage taken, −55% healing received, +5,000 max health in PvP zones.

**Tower defence and meta-progression — progression as a percentage of base, small.**
- **PvZ2 plant levels [V]:** +1% damage per level (to 200%), +10 flat toughness per level; **Vasebreaker forces every
  plant to level 1** — PvZ itself has a per-mode override. <https://plantsvszombies.wiki.gg/wiki/Plant_upgrade_system>
- **Kingdom Rush [S]:** upgrades +10–15% damage, +5–10% range, +30% barracks HP, bounded by 3 stars per stage.
- **BTD6 Monkey Knowledge [S]:** small conditional bonuses (e.g. +10% attack speed), toggleable, disabled on some
  competitive tiles. **Legion TD 2 [S]:** no persistent stats at all, for fairness.

**Documented failure modes.**
- **Flat bonus on a small base:** WoW vanilla downranking — flat +healing applied in full to cheap low ranks; TBC fix
  scales the bonus by `(spell level + 6) / player level` **[V]**. PoE needs a per-skill "damage effectiveness" on flat
  added damage for the same reason **[S]**.
- **Normaliser blind spots:** what escapes a mode normaliser is the flat or conditional part it did not see (ESO set
  bonuses, GW2 downscaled trait bonuses, WoW Midnight's flat-value potions after the squish) **[V]/[S]**.
- **A squish does not stop compounding:** Diablo 4 Season 6 rescaled numbers but stacked multipliers still reached
  quintillions **[S]**. Rescaling a mismatch is not fixing its unit.

**What transfers:** keep one character and one formula set; let the **mode** decide (a) which level the actor reads and
(b) how much of each progression family counts, as a small multiplier table; express TD progression as a share of the
unit's own base.

---

## The shape

### Proposed — one mode profile, fed into the existing Hub subsystems

```text
data/tuning/mode-profiles.v1.json          (one domain: how a mode reads the shared tuning)
  modes.battle   = identity                (every multiplier 1000, every selector = today's battle behaviour)
  modes.lawn     = { theta, allocation, familyRead, familyScaleMilli, combatBaseline, combatProfile }

host (injector)  loads modes.lawn  ─►  ActorHubBootstrap.CreateDefault(..., modeProfile)
host (server)    loads modes.battle ─►  BattleHubCompose / UniqueActorHubCompose (identity: goldens unchanged)

ActorHub (one compose)
  ResourceBaselineSubsystem   reads modeProfile.familyScaleMilli for resource.*      (uses its inert tuning seam)
  AptitudeSubsystem           reads modeProfile.familyRead + familyScaleMilli        (EffectiveKMilli already scales by family)
  BattleBaselineSubsystem     registered when modeProfile.combatBaseline             (exists; lawn gets P(hit) at parity)
  IPowerIndexProvider         chosen per side from modeProfile.theta                 (player / content + offset / fixed)
  SpeciesAllocationSource     commander delegate chosen per side from modeProfile.allocation
```

Five pieces, each an existing seam:

1. **`theta` per side** — `player` (today), `content` (a lawn content Θ plus a tunable `thetaOffset`, the delve and
   threat-rung precedent), or `fixed` (`FixedPowerIndexProvider`, ESO-style sync). No new curve: every option is a `Θ`
   fed into the one ladder.
2. **`allocation` per side** — `commander` (today), `zombossCommander` (the web-battle enemy model), or `none`.
3. **`familyRead` override** — a third named read function beside `contest` and `magnitude`: **`baseRelative`**,
   `value = kMilli/1000 × share^γ × actorBase × P(Θ)/P(referenceΘ)`. It reads the same ladder through the ratio
   `ContentScale` already computes, so at the reference Θ a full share is `k` × the actor's own vanilla value. The lawn
   row sets `progression.bonus.*` (and, if M1 holds for the rider, `combat.power.*`) to `baseRelative`. This is the
   WoW-TBC / PoE fix in this repo's vocabulary.
4. **`familyScaleMilli`** — per-family multipliers, the same mechanism as `recovery.scaleMilli` and
   `mitigation.scaleMilli`, scoped to a mode. This is where the lawn says "resource pools count at 1/20" without copying
   `battle-resources` numbers (principle 6).
5. **`combatBaseline` and `combatProfile`** — register the existing `BattleBaselineSubsystem` on the lawn Hub, and move
   `CombatProfile`'s chip floor into data.
6. **Species flavour from the seed (ruling 2)** — the build favour keeps flowing through `SpeciesAllocationSource`
   (lookup moved onto the `EmpireGeneral` claim, zombie budget from Zomboss's row). The baked species values reach the
   lawn through one registered species contributor (its own `ContributionSourceIds` id) on the same Hub, read as a
   share of `P` at the species' Θ and re-read through the lawn row — covering the RPG-only channels vanilla has no field
   for (resource pools, `combat.power.*`), in place of the uniform `poolShareMilli`. The profile scales these by family;
   it never stores a species number.

**Separate defects the spec owns regardless of shape:** M3 (trace and, if confirmed, fix the regen unit through
`publish.py`, never a hand-edit) and M4 (emit the stamina cost as `anchor(Θ) × q(rung)`, as the calibration spec's own
boundary already requires).

### Rejected

| Alternative | Why not |
|---|---|
| A `LawnStatComposer` or lawn-only aptitude resolver | Second compose of the same numbers — principles 2 and 3. The exact dual-compose defect (`BattleStatComposer`) this repo is already paying to fuse |
| A second full `aptitudes-lawn.v1.json` (hypothetical — never created; 526 edges copied, then edited) | Two copies of one balance surface drift; a rebalance must be done twice; T7 attribution breaks |
| Rescale vanilla fields up to the ladder (make a pea hit `atk(Θ)`) | Changes what PvZ is (principle 1); every vanilla interaction (instakill thresholds, armour HP, wall-nut damage states) moves |
| Global coefficient cut in `aptitudes.v8.json` | Fixes the lawn by breaking battle, whose parity was measured against these coefficients |
| Hard clamp of lawn bonuses (e.g. `min(bonus, 2 × base)`) | A progression ceiling (principle 7); hides the unit mismatch instead of fixing it |
| ESO-style full sync of the lawn to one Θ, both sides | Erases Spine A on the lawn (level stops mattering); kept only as the `fixed` selector an owner can choose |

### Why this is the SOLID shape

- **S:** the Hub still composes; the profile only supplies inputs. **O:** new behaviour is new data rows and one named read
  function in the existing `read` block. **L:** the battle row is the identity, so every current caller keeps its contract
  and its goldens. **I:** hosts pass one small profile object, not a fat per-mode API. **D:** subsystems depend on the
  profile abstraction, not on "am I on the lawn".

---

## Tunables

All in `data/tuning/mode-profiles.v1.json` (new) unless named. Values below are the **proposal's starting points, UNMEASURED**;
the spec derives them from anchors the way `spec-lawn-combat-calibration.md` does.

| Key | Unit | Battle row | Lawn row (starting point) | Derivation anchor |
|---|---|---|---|---|
| `modes.<m>.theta.plant.source` | enum `player`/`content`/`fixed` | `player` | `player` | Spine A must show |
| `modes.<m>.theta.zombie.source` | enum | `content` | `player` (ruling 1) | — |
| `modes.<m>.theta.zombie.thetaOffset` | Θ | 0 | 0 to start, UNMEASURED (ruling 1; the later Zomboss "reflection" feature adjusts here) | delve `θ_enemy = Θ_room + thetaOffset`; threat rung row 18 |
| `modes.<m>.allocation.{plant,zombie}` | enum `commander`/`zombossCommander`/`none` | `commander` / `zombossCommander` | `commander` / `zombossCommander` (ruling 1) | — |
| `modes.<m>.familyRead.<family>` | enum `contest`/`magnitude`/`baseRelative` | absent (= `aptitudes.v8` `familyRead`) | `progression.bonus.*`: `baseRelative` | M1 |
| `read.baseRelative.referenceTheta` | Θ | — | 20 (the pin; same value as `SoulSinkPolicy.VanillaPvzTheta`, read from one place) | `power-scale.v2.json` `pinIndex` |
| `modes.<m>.familyScaleMilli.<family>` | Milli | absent (= 1000) | `resource.max`, `resource.regen`: derived so an allocated lawn plant still reaches burst deficit (proof 4 stays runnable) | `spec-lawn-combat-calibration.md` Method 2–3 |
| `modes.<m>.combatBaseline` | bool | true (today, via `BattleHubCompose`) | true | L-N7: 50% miss with no baseline |
| `modes.<m>.combatProfile.minChipShareKPm` | KPm | 50 | 0 (today's overlay) | `decisions.md` Combat resolution SSOT (enabling on the lawn is ask-first) |
| `progression.bonus.*` `kMilli` under `baseRelative` | Milli of the actor's base at the reference Θ | — | from owner question 2 | PvZ2 +1% per level; Kingdom Rush +10–30% |
| `basic.baseAmountAtRung1` (existing file `action-corpus-cost-templates`) | stamina at the pin, scaled by the ladder | 25 | 25 | M4 — unit change, not a value change |

Every row carries its unit in the key or `_meta` (T6). The battle row being the identity is the T7 guarantee: a lawn
retune cannot move a battle golden.

---

## What this deliberately does not decide

- **Balance.** No win-rate sweeps; the spec only derives defensible starting values, as `spec-lawn-combat-calibration.md`
  does, and marks them UNMEASURED.
- **Battle's own numbers.** M1's coefficients are a lawn problem because battle does not read `progression.bonus.*`.
  Whether battle's other families are well sized is the class-system residual-fit's job. M3 may touch battle; if so, it
  lands as its own versioned `publish.py` change with its own measurement, never bundled with the lawn profile.
- **Fusing `BattleStatComposer`.** `FUSE-battle-hub` owns that. The profile must not add a dependency on it; the battle row
  is consumed by whichever compose battle runs at the time.
- **The vanilla-PvZ content Θ signal.** Not needed: ruling 1 has lawn zombies track the player's Θ plus an offset.
  The signal stays its own named follow-up.
- **Zomboss "reflection"** — a difficulty adjustment that reacts to the player. Named later feature (ruling 1).
- **IZombie and other zombie-controlled lawn modes**, and hypno-zombie allies. They are a side-to-owner mapping the spec
  names; this doc does not design them.
- **The elemental rider amount** (`lawn-combat-rider-amount`, still open from T11).

---

## Owner rulings — 2026-09-16

The three questions below were answered on 2026-09-16. The original options stay for the reasoning trail.

1. **Whose power do lawn zombies carry? — RULED (b), "for now".**
   - (a) **The player's** Θ and commander build — today's behaviour since L-N38, per `spec-commander-lawn-bridge.md` §1.
     The lawn stays equally hard as you level; your Might also buffs the enemy.
   - (b) **Zomboss's** build at a lawn content Θ = player Θ + `thetaOffset` — the web-battle model. The lawn tracks your
     level but the enemy's build is Zomboss's, not yours.
   - (c) **Vanilla** — zombies get no RPG scaling; only deployed specimens do. The lawn gets easier as you level.

   **Ruling:** (b). Lawn zombies read `Θ_player + thetaOffset` and `ZombossCommanderAllocation`, never the player's
   commander allocation. Owner: *"we will add difficulty adjust for zomboss base on player (reflection feature later)"* —
   a Zomboss difficulty adjustment that reacts to the player is a **named later feature**, outside this program; the
   profile only has to leave room for it (the `thetaOffset` and the allocation selector are where it would plug in).
   Because the zombie Θ tracks the player, the vanilla-PvZ content Θ signal is **not** a dependency of this program.
   `spec-commander-lawn-bridge.md` §1 carries the amendment.

2. **How much should a build show on a lawn plant?** Under `baseRelative`, pick the target at the reference Θ for a
   full-share build: e.g. a full Might commander at Θ 20 makes a Peashooter's pea **2×** vanilla (+100%), rising with Θ
   on the ladder ratio (at Θ 40 the bonus is ≈ 2.1× larger [calc: `P(40)/P(20)` = 1,440 / 680]). *Recommendation: +100% at the pin.*
   It is visible (a pea kill drops from ~14 peas to ~7), leaves vanilla meaningful, and sits near PvZ2's own +1% per
   level ceiling of 200%.

   **Ruling:** *"keep the specie favour in specie seed, seem like it never wire"*. How a build shows on a lawn actor is
   shaped **per species, by what the species seed authors** — the build favour the owner asked for in
   `species-build-ideal.md` (*"i want creature have build favour so it will auto distribute the bonus primary stats …
   the zomboss will do the same"*) and the species' baked values. The lawn profile holds **mode-level dials only** and
   never flattens or copies per-species numbers. The +100% figure is not adopted as a ruling; it stays an UNMEASURED
   calibration default for the mode-level `baseRelative` coefficient, which the species favour then distributes.

   **"Never wired" — checked 2026-09-16, and it is half right.**

   | Species seed flavour | Status on the lawn | Evidence |
   |---|---|---|
   | **Build favour** (`gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, e.g. GatlingPea Onslaught 350 / Agility 163 / Might 163 / Ferocity 162 / Fortitude 162; generator `gk-forge/tools/CreatureBuildPlanGen`) | **Built, live, gated by species level.** Server baseline `RpgStore.Aptitudes.cs:208-210` (`SpeciesBuildPlanCatalog.SharesFor`) → `AptitudeEndpoints.cs:154-158` (levelled species only) → `RpgClient.cs:514-520` → `CheatState.SpeciesAllocation` → `SpeciesAllocationSource.cs:117` (`commander + species`). Points are `(speciesLevel − 1) × 4` (`PointBudget.cs:40`, `aptitudes.v8.json` `creatureType` 4), so level 1 gives nothing. | Live read 2026-09-16, `GET /api/aptitudes/6`: `normalzombie` Vigor 24, Might 4, Composure 4, Precision 4, Ferocity 4 — levelled by natural waves; this is why the L-N38 probe's NormalZombie reached max HP 1,915. No plant species had points: every probe plant was debug-spawned, and only `start`/`initHealth` spawns carry the `EmpireGeneral` claim that earns species XP (`EntityApply.cs:290-301`, `RpgXpAwardMap.cs:92-112`). |
   | **Species lookup** | **Wiring gap / spec deviation.** The lawn composes the species allocation by type id (`CheatState.cs:155` `index.TryGet(sideText, typeId, …)`); `creatures/spec-general-empire-fallback.md` eligibility rule forbids replacing the `EmpireGeneral` claim with type-id inference. | `CheatState.cs:145-158` |
   | **Baked species values** (`gk-data/packs/fusion/data/generated/creatures/<Species>.json` `magnitudes`, `theta`, `pTheta`; e.g. GatlingPea `resource.max.stamina` 6,328, `combat.power.omni` 362 at species Θ 13, `P` 452) | **Real gap for vanilla actors** — nothing reads `magnitudes` at runtime except an import round-trip and a count check (`RpgStore.Species.cs:156,328`; `RpgStore.UniqueActors.cs:1603`). **Wiring gap for deployed specimens** — the binding path exists but no `trait.species-magnitude-*` container is seeded (`RpgStore.UniqueActors.cs:1620`: `if (container is null) return;`). **Stale bake:** `gk-forge/tools/CreatureSpeciesGen/Program.cs:70` reads `aptitudes.v2.json`; both hosts load v8. Baked in ladder units at the species' own Θ, so wiring them raw repeats M1. | agent trace + code reads, this session |
   | `rangeCells` | **Real gap** — stored (`RpgStore.Species.cs:145`), never mapped onto `CreatureSpeciesDef` (`ConcreteSpeciesSeedReader.cs:82-109`), never read. | — |
   | `traitPool` | **Real gap on the lawn** — read by web-battle waves (`WaveCatalog.cs:175`) and specimen minting, never by the lawn Hub. | — |
   | `attackIntervalMs` | Deliberately not on the lawn — the lawn keeps the vanilla interval (`EntityApply.cs:50`); web-battle waves read it (`WaveCatalog.cs:179`). | principle 1 |

   **What the ruling adds to the shape** (piece 6 below): species identity reaches a lawn actor through the seed, in two
   channels — the build favour (already flowing; the spec fixes the lookup and decides whether unlevelled species show a
   seed-shaped favour at all) and the baked values (a registered species contributor on the lawn Hub, read through the
   lawn row, after the bake moves to the shipped aptitude tuning).

   **Interplay with ruling 1, settled by that ruling:** lawn zombies are Zomboss's army, so a zombie's species favour is
   budgeted from **Zomboss's** species levels (his player row, `EnsureZombossPlayer`), not the player's — today it comes
   from the player's own zombie species progression. The favour *shape* is the same seed plan either way.
   `species-build-ideal.md` decision 4 (Zomboss rotates on level-up and counter-builds on a lose streak) is the
   "reflection" feature ruling 1 defers.

3. **Do deployed specimens (Bound uniques) follow the lawn row or keep full ladder magnitudes? — RULED: lawn row.**
   `the-lawn.md` calls them "empowered uniques"; `UniqueBoundLoadout` grants the same `progression.bonus.*` families.
   *Recommendation was: they follow the lawn row with their own higher share (`uniqueCreature` already has the largest
   point rate, 6 vs commander 3 in `aptitudes.v8.json` `pointEconomy`)*, so "empowered" comes from the existing scope
   ladder, not from escaping the profile.

   **Ruling:** yes — *"use lawn setting for lawn balance"*. Everything on the lawn, deployed specimens included, reads
   the lawn row; `UniqueBoundLoadout`'s grants go through the same profile.

---

## DESIGN-GATE §5 checklist

```
[x] Subsystems: Stats/ActorHub, aptitudes, power ladder, resource hub, combat resolution, lawn injector apply, lawn-deploy.
[x] Session boundary: solid-run-20260912-eb53 (paths include docs/architecture/**, gk-core/src/FusionRpg.Core/**, Injector/**).
[x] Read this session: the-game.md, the-loops.md, the-lawn.md, DESIGN-GATE §1/§5, resource-hub-ssot.md §8–§11,
    tunables-ssot.md, ssot-power-scale.md (Θ_actor, §10 rows 1/18/21/32), spec-power-index.md §2.2,
    spec-lawn-combat-calibration.md, spec-commander-lawn-bridge.md §1, aptitudes.v8.json read/recovery/mitigation/familyRead.
    Not read in full: spec-magnitude-and-units.md (outline only) and spec-content-scale.md §2.2 — the spec must read both
    before adopting the baseRelative read (ContentScale's doc says it is applied once, inside Instantiator, and power-guard
    scans for a second multiplication).
[x] decisions.md: Combat resolution SSOT, ActorHub sole compose gate, Caps, Standalone-first, Product vision — no lock on
    per-mode stat profiles; nothing here contradicts them.
[x] Claims cite file:line; the lawn numbers are live measurements with committed evidence.
[x] Verified against code: Θ key (fixed and live-proven), MergeAppliedCombat, allocation delegate, battle LiveAtk,
    cost ValueSpec, regen per tick.
[x] Surrounding sections read for every quoted rule.
[x] Tested, not assumed: L-N38 (falsifying test + live), exhaustion on a clean player, the post-fix magnitudes.
    M3 (regen unit) is explicitly unverified.
[x] No §2 invariant contradicted: one Hub, one formula set, one ladder, data-owned tunables.
[x] Corrections propagated: spec-commander-lawn-bridge.md §1 amended for the zombie side (ruling 1, 2026-09-16).
[x] No pinned population counts.
[x] No event-refreshed cache introduced.
[x] No order-dependent acceptance criterion.
[x] Contributes via ActorHub subsystems only; no private fold.
[x] No SOLID-violating parallel path; BattleStatComposer untouched and not depended on.
```

**Next step:** all three questions are ruled (2026-09-16). `/spec lawn-tuning-profile` — capability map + module specs:
regen unit trace (M3, first), mode-profile loader, `baseRelative` read, zombie power source (Zomboss build + Θ offset),
species flavour (claim-based lookup, species bake on shipped tuning, lawn species contributor), lawn resource scale,
stamina cost scaling (M4).

# Capability map: `lawn-tuning-profile`

**Ideal:** [lawn-tuning-profile-ideal.md](lawn-tuning-profile-ideal.md) (idea phase closed 2026-09-16, three owner
rulings in) · **Plan:** [tasks/lawn-plan.md](../../tasks/lawn-plan.md) · **Tasks:** [tasks/lawn-todo.md](../../tasks/lawn-todo.md)
(one plan over `lawn-playable` + `lawn-tuning-profile`, written 2026-09-20 by `backlog-clean-up`
`orphan-plan-authoring` BCU2.4 — the per-module plan/todo pair this line originally promised was
never written and is superseded by the shared `lawn` plan above).
**Status:** capability map 2026-09-16, and specced from the top of the build order on the owner's own instruction
(*"you need to start now"*). Written so far: the two modules with no dependencies
([`regen-unit-trace`](lawn-tuning-profile/spec-regen-unit-trace.md),
[`mode-profile`](lawn-tuning-profile/spec-mode-profile.md)) and the whole chain that unblocks
`lawn-combat-wire` proof 5 / L-N2
([`base-relative-read`](lawn-tuning-profile/spec-base-relative-read.md),
[`lawn-resource-scale`](lawn-tuning-profile/spec-lawn-resource-scale.md),
[`basic-attack-cost-scale`](lawn-tuning-profile/spec-basic-attack-cost-scale.md),
[`lawn-scale-live-proof`](lawn-tuning-profile/spec-lawn-scale-live-proof.md)). Also written: [`species-flavour-lawn`](lawn-tuning-profile/spec-species-flavour-lawn.md).
**[`lawn-combat-baseline`](lawn-tuning-profile/spec-lawn-combat-baseline.md) and
[`zombie-power-source`](lawn-tuning-profile/spec-zombie-power-source.md) written 2026-09-20**
(`backlog-clean-up` `orphan-plan-authoring` BCU2.3, narrowed to wiring per the map's own ruling 1) —
all 7 modules now specced. None built yet; scheduled once in the backlog-clean-up **lawn plan** (BCU2.4).

---

## What this program is for

A lawn match must read as Plants vs. Zombies with an RPG layer on top. Today three aptitude points make a
Peashooter's pea 82× its vanilla number, no allocated actor can ever run out of stamina, and the zombie side has no
model of its own. The cause is not one bad number: the lawn and the web battle share one tuning set, and every RPG
magnitude is sized in ladder units while the lawn's base values are vanilla PvZ's.

This program adds **one versioned per-mode profile, fed into the one ActorHub through seams that already exist**. It
does not add a second composer, a second combat formula, or a private curve.

**It unblocks `lawn-combat-wire` proof 5** (`L-N2`): an exhausted actor whose Hub-composed `attackDamage`/`maxHp`
stay intact cannot exist while any allocation makes the pool unemptiable.

## Rulings carried in (owner, 2026-09-16, second round)

4. **The aptitude bonus scales each actor's own vanilla base**, not one shared reference base — so the
   vanilla roster's own ordering survives investment.
5. **A fully-invested actor still exhausts**, in a longer rhythm. Investment buys cadence, never
   immunity.

Raised with ruling 4, and answered by measurement: *"check specie seed, did they support and we wire
correctly?"* The species seed is the right long-term home and **cannot carry it today** — 730 of 904
species share `theta 13`, only 50% carry `combat.power.omni`, 450 share `resource.max.hp 2712`, and
Peashooter and GatlingPea bake identically. `species-flavour-lawn` now owns fixing that generator, and
`base-relative-read` anchors on the actor's own vanilla value until it is fixed.

## Rulings carried in (owner, 2026-09-16)

1. **Lawn zombies carry Zomboss's build** at the player's Θ plus a tunable offset. A player-reactive Zomboss
   ("reflection") is a later feature — `species-build-ideal.md` decision 4 already designs it.
   ⭐ **Sharpened 2026-09-16 (owner, `actor-layer-compose-ideal.md`): "Zomboss's build" is his EMPIRE
   SPECIES PROGRESSION, not his commander build.** A lawn zombie reads the empire that owns the species —
   Zomboss, `players` id 3 — through the same `AllocationScope.CreatureType` layer a plant reads from the
   player's empire. His commander build stays a commander aura, a different layer. This also removes the
   reason for `zombie-power-source` to invent a zombie-side model of its own: the model is the same layer,
   read from the other empire. What is left for that module is the **balance** question — an empire that
   levels from every wave the game spawns grows on a clock the player does not control, and whether that
   is difficulty scaling with play or an escalation nobody asked for is its first question.
2. **Species flavour stays authored in the species seed.** The lawn profile holds mode-level dials only and never
   per-species numbers.
3. **Deployed specimens use the lawn row** — everything on the lawn is balanced by one set of rules.

## The five measured defects this program owns

| # | Defect | Evidence |
|---|---|---|
| M1 | `progression.bonus.*` reads `k × share × P(Θ)` (ladder units) and lands on a vanilla base (pea 20) — **the attack half is fixed at the source 2026-09-16** (owner: writing `attackDamage` is a bug; both writes removed from `EntityStatWriter`, RPG damage is the battle engine's). **The hp/armour half stands**: composed absolutes still overwrite a vanilla 300. | live: attack 20 → 1641 at Θ 6; hp 300 → 3972 |
| M2 | Every aptitude adds 8–26 × `P(Θ)` to a stamina pool whose base is 0.5 × `P(Θ)` | live: max 53 → 5142, regen 0.2 → 87.6 per tick |
| M3 | The `resource.regen.*` edge unit is unverified — the POC ticked per 1,000 ms round, the runtime per 100 ms tick | `gk-core/tools/CombatSim/ActionEconomy.cs` vs `BattleModels.cs:452` |
| M4 | The basic attack's stamina cost is a flat 25 while pool and regen scale with `P(Θ)` | `ActionCorpusComposer.cs:173` |
| M5 | Lawn zombies read the player's Θ and the player's commander build; web battle enemies read content Θ and Zomboss's | `CheatState.cs:186`, `WaveCatalog.cs:176-177` |

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| [`regen-unit-trace`](lawn-tuning-profile/spec-regen-unit-trace.md) | Settle what unit the aptitude `resource.regen.*` coefficients were authored in, and reconcile them with the runtime's per-tick channel. Trace first; a value change publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`. Touches battle, so it lands alone and measured. | — |
| [`mode-profile`](lawn-tuning-profile/spec-mode-profile.md) | The profile itself: `data/tuning/mode-profiles.v1.json`, a Core parser (no I/O — hosts inject, tunables-ssot §7.2), and the Hub plumbing that carries a mode row into `ActorHubBootstrap.CreateDefault`. The battle row is the identity, so every current caller and golden is byte-identical. | — |
| [`base-relative-read`](lawn-tuning-profile/spec-base-relative-read.md) | A third PS-3 read function beside `contest` and `magnitude`: `baseRelative`, `k × share^γ × actorBase × P(Θ)/P(refΘ)`, selected per mode per family. Fixes M1 for `progression.bonus.*`. Must not become a second `contentScale` multiplication (`spec-content-scale.md` §2.2, `guard-power`). | `mode-profile` |
| `lawn-combat-baseline` | Register the shipped `BattleBaselineSubsystem` on the lawn Hub through the profile, so lawn actors get accuracy/dodge/crit from Θ instead of sitting at the sigmoid's 0.5 coin-flip (measured: 3 misses in 13 rider records). | `mode-profile` |
| `zombie-power-source` | Per-side Θ source and allocation selector: lawn zombies read `Θ_player + thetaOffset` and `ZombossCommanderAllocation`, never the player's commander build. Fixes M5, ruling 1. | `mode-profile` |
| [`lawn-resource-scale`](lawn-tuning-profile/spec-lawn-resource-scale.md) | The lawn row's family scales for `resource.max.*` / `resource.regen.*`, sized so exhaustion is reachable and recoverable at every build, not only at zero allocation. Fixes M2. | `mode-profile`, `regen-unit-trace` |
| [`basic-attack-cost-scale`](lawn-tuning-profile/spec-basic-attack-cost-scale.md) | The basic attack's stamina cost becomes `anchor(Θ) × q(rung)` instead of a flat 25, which is what `spec-lawn-combat-calibration.md`'s own boundary already requires. Fixes M4. | `lawn-resource-scale` |
| [`species-flavour-lawn`](lawn-tuning-profile/spec-species-flavour-lawn.md) | Ruling 2's wiring — **and, found 2026-09-16, the generator fix that must come first**: the bake is a constant wearing a species' name (730 of 904 at `theta 13`, 50% with no `combat.power.omni`, Peashooter and GatlingPea identical), so Θ must become a species property and attack coverage a closed join before any of it is worth carrying. Then: the species lookup moves onto the `EmpireGeneral` claim (type-id inference is forbidden), the bake re-runs against the shipped aptitude tuning (it reads `aptitudes.v2.json` while hosts load v8), and one registered contributor carries the baked values into the lawn Hub for the RPG-only channels vanilla has no field for. | `mode-profile`, `base-relative-read` |
| [`lawn-scale-live-proof`](lawn-tuning-profile/spec-lawn-scale-live-proof.md) | The live proof on a real board and a clean player: the profile's own numbers, and `lawn-combat-wire` proof 5 — an exhausted actor whose `attackDamage`/`maxHp` still equal the Hub snapshot. | every module above |

**Build order**

```
regen-unit-trace ─┐
mode-profile ─────┼─► base-relative-read ───┐
                  ├─► lawn-combat-baseline  ├─► species-flavour-lawn ─┐
                  ├─► zombie-power-source ──┘                          ├─► lawn-scale-live-proof
                  └─► lawn-resource-scale ──► basic-attack-cost-scale ─┘
```

`regen-unit-trace` and `mode-profile` are independent and can run in parallel. `lawn-resource-scale` waits for the
unit answer, because sizing a pool against a rate whose unit is unsettled is how M2 happened.

## Sibling program

`lawn-tuning-profile` fixes the **scale**. It does not make the lawn affordable — that half is
[`lawn-playable`](lawn-playable-map.md)'s program, and it is done: `LawnBasicAttackFeature.DefaultEnabled`
has read `true` since `9f985313` (2026-09-16), and a follow-up perf pass brought the cost to 3.46% of
wall, under the 6% ceiling (corrected 2026-09-20 — this line used to read "ships defaulted off … 26.7–37%
of the pipeline", which was the pre-fix measurement). What still has not run is the **scale** gate this
program owns (`lawn-scale-live-proof`, M2 stamina) — a cheap loop is not yet a tuned one. Both halves
land under the one `tasks/lawn-plan.md` (`backlog-clean-up` `orphan-plan-authoring`).

## What this program does not own

- **Balance.** Starting values are derived from named anchors and marked `UNMEASURED`, as
  `spec-lawn-combat-calibration.md` does. Win-rate sweeps stay with the balance program.
- **Battle's own numbers**, except where `regen-unit-trace` proves a unit error that touches both; that lands as its
  own measured change.
- **The Zomboss "reflection" feature** (ruling 1) and the **elemental rider amount** (`lawn-combat-rider-amount`).
- **A second composer, a second combat formula set, or a private `f(level)`.** Every module contributes to
  `ActorHub` or consumes its output.

## Open questions

None. The three that existed were ruled on 2026-09-16; they are recorded in the ideal doc.

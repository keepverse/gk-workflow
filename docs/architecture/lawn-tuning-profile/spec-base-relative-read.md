# Spec: `base-relative-read` (lawn-tuning-profile module 3)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) · **Depends on:** `mode-profile` ·
**Unblocks:** `species-flavour-lawn`, `lawn-scale-live-proof` · **Fixes:** defect M1
**Status:** spec, 2026-09-16. Not built.

## Objective

Stop landing a ladder-sized number on a vanilla-sized base.

⛔ **Scope narrowed 2026-09-16 — the attack half is gone.** The owner ruled that writing `attackDamage`
into PvZ at all is a bug (*"we already have battle engine and damage calculator in our rpg"*), and both
writes are now commented out in `EntityStatWriter` with the reason recorded inline. So the 20 → 1,641
reading below is **historical**: a Peashooter's `attackDamage` is vanilla again, and nothing needs a new
read function to make it so. **This module's remaining scope is `maxHp`, `defense`, `arm1`, `arm2`** —
`p.thePlantMaxHealth` and the zombie armour fields are still assigned composed absolutes, so a
ladder-sized bonus still lands on a vanilla 300 there (live: hp 300 → 3972). If the lawn transport
becomes a delta over hp/armor1/armor2 (`species-hub-wire-ideal.md`), this module may shrink to nothing —
check that before building it.

`progression.bonus.*` is composed by the aptitude subsystem through PS-3's `magnitude` read —
`k × share^γ × P(Θ)` — which is sized against the ladder's own baseline (`BattleRuleset.BaseHp`, about
1,000 hp at Θ=20). On the lawn it is added to vanilla PvZ's numbers, where a Peashooter's pea is **20**.

Measured live:

| Θ | vanilla base | live `attack` after the bonus |
|---|---|---|
| 6 | 20 | 1,641 |
| 57 | 20 | 2,939 |
| 57 | 20 (+ specimen's own 12 points) | 3,116 |

82× at Θ=6. The pea is not a pea. Nothing about this is a *balance* number — no value of `kMilli`
fixes a unit mismatch between "ladder units" and "the host game's own scale".

## The shape

A **third read function** beside `contest` and `magnitude`, selected per mode per family through the
mode profile:

```
baseRelative(share, Θ, actorBase) = k × share^γ × actorBase × P(Θ) / P(refΘ)
```

- `actorBase` is the actor's **own vanilla value** for that channel (the pea's 20, the wall-nut's hp) —
  the number the injector already reports as `primaryAtk` / `primaryMaxHp` in `debug.aptitude-trace`.
  **Owner ruling 2026-09-16: each actor's own base, not one shared reference base** — investment scales
  what a plant already is, so the vanilla roster's own ordering survives.
- `P(Θ)/P(refΘ)` keeps the ladder's shape: growth still tracks `P(Θ)`, but as a **ratio against a
  reference rung**, so at `Θ = refΘ` a fully-invested actor is a stated multiple of its own base rather
  than a four-digit constant.
- `contest` and `magnitude` are untouched. Battle keeps reading `magnitude`; the lawn row selects
  `baseRelative` for the `progression.bonus.*` family and nothing else changes.

## Where `actorBase` comes from — and why not the species seed (measured 2026-09-16)

The owner's question on ruling this: *"check specie seed, did they support and we wire correctly? The
specie seed have power ladder and generate base on almanac in game, maybe inconsistent some where but in
principle should correct."*

The principle is right and the seed is the correct long-term home. **It cannot carry this today**, and
the corpus says so — all 904 files under `gk-data/packs/fusion/data/generated/creatures/`:

| Reading | Value | What it means for `actorBase` |
|---|---|---|
| Distinct `theta` | **730 of 904 are `13`**, 136 are `0`, the rest scattered | Θ is effectively a corpus constant, not a species property — so `P(Θ)` from the seed differentiates nothing |
| `combat.power.omni` present | **457 of 904 (50%)** | Half the corpus has no attack identity at all; SunFlower, WallNut, KelpPuff, Threepeater all read `None` |
| Distinct `resource.max.hp` | 42 values, but **450 of 904 are exactly `2712`** and 95 are `14464` | A coarse tier, not a per-species base |
| Peashooter vs GatlingPea | identical `hp 2712` **and** identical `power 362` | The two plants vanilla separates most are indistinguishable in the bake |
| Scale | Peashooter `resource.max.hp 2712` against vanilla's 300 | Seed magnitudes are **ladder-sized**; anchoring on them re-creates defect M1, the exact thing this module exists to remove |

What the bake *does* carry per species and carries well: `rangeCells` (3 values), `attackIntervalMs`
(5 values, Gatling 500 ms vs Peashooter 1500 ms), rarity, elements and traits.

So: **`actorBase` reads the actor's own vanilla value**, which exists per species, is the right scale, and
is already on `StatContext`. The read function takes a base as an argument and does not care where it
came from — when `species-flavour-lawn` fixes the bake (per-species Θ, power coverage past 50%), moving
the base to the seed is a one-line change to the caller, not a redesign here. That module now owns the
generator defect this table found.

⚠️ **This must not become a second `contentScale` multiplication.** `spec-content-scale.md` §2.2 and
`guard-power` exist because a magnitude multiplied twice by the same ladder term is the defect that let
three curves ship. `baseRelative` replaces the `P(Θ)` term with a ratio — it never multiplies on top of
one already applied.

## Tunables

In `data/tuning/mode-profiles.v{n}.json`, under the lawn row (the file `mode-profile` ships):

| Key | Meaning | v1 |
|---|---|---|
| `modes.lawn.families.progression.bonus.read` | `baseRelative` | — |
| `modes.lawn.families.progression.bonus.refTheta` | the rung the ratio is anchored at | `UNMEASURED` |
| `modes.lawn.families.progression.bonus.k` | multiple of own base at full investment at `refΘ` | `UNMEASURED` |
| `modes.battle.families.progression.bonus.read` | `magnitude` | unchanged — battle is the identity |

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeRead|BaseRelative|PowerLadder"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Power|Golden"
python gk-core/scripts/guard-actor-hub.py ; python gk-core/scripts/audit-overflow.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Project structure

| What | Where |
|---|---|
| The read function | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeReadFunctions.cs` (beside the two that exist) |
| Selection | the mode profile row, read by `AptitudeSubsystem` |
| Base input | the actor's `EntityBaseline` already on `StatContext` |
| Tests | `tests/FusionRpg.Core.Tests/Stats/BaseRelativeReadTests.cs` |

## Testing strategy

- ✅ At `Θ = refΘ` with full investment, the bonus equals `k × actorBase` — the function's defining
  property, asserted symbolically, not against a shipped `k`.
- ✅ Share still cancels at parity (`ssot-power-scale.md` §2): two actors with the same share and the
  same Θ get the same ratio regardless of level.
- ✅ Battle is untouched: every golden byte-identical, and the battle row still selects `magnitude`.
- ✅ `actorBase = 0` yields 0, never NaN or a divide-by-zero — a plant with no attack stays a plant with
  no attack.
- ✅ The result is not multiplied by `contentScale` a second time (the `guard-power` property).
- ❌ Never assert a shipped `k`, `refTheta`, or a live attack number. Readings.

## Boundaries

- **Always:** keep the two existing read functions unchanged; select per mode through the profile.
- **Ask first:** nothing — the shape is forced by the arithmetic.
- **Never:** write a new `f(level)` (`ssot-power-scale.md` §10 is closed — this is a new *read* of the
  existing ladder, and it belongs in that inventory as one); scale the vanilla base itself (that would
  be changing what PvZ is); apply `baseRelative` in battle.

## Numeric types

`actorBase` is `long` (Unity's `int` fields are clamped at the writer via
`EntityStatWriter.ClampToInt32Reporting`, which stays the only narrowing point). The ratio is `double`;
widen before multiplying (`(long)a * b`), divide last, `checked`.

## ActorHub gate

**Contributes through the existing aptitude subsystem** — one more read mode inside the same fold, no
new subsystem and no second composer.

## Success criteria

1. At the shipped lawn row, a Peashooter's live `attack` is a stated multiple of 20, not 1,641.
2. Battle goldens byte-identical.
3. `ssot-power-scale.md` §10's inventory names `baseRelative`.
4. `audit-overflow.py` clean on the new arithmetic.

## Open questions

None. `refTheta` and `k` are `UNMEASURED` starting values, sized by `lawn-scale-live-proof`.

# Spec: Wild species spawn (`wild-species-spawn`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `wild-species-spawn`
**Owning programs:** `loam` (the spawner) + `world-map-runtime` (the sector context)
**Depends on:** `species-magnitude-synth` — ⭐ **added 2026-09-13 (owner decision, Open question 2
below)**: wild members take their species' own derived `P(Θ)`, not the flat `UnmadeMemberHp`
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized.

> **Build state (strengthen pass 2026-09-18): SHIPPED — T5 (`cb43a004`), T7 (`d2361c76`), T18b (`ee09f9d7`, member HP from species `P(Θ)`).** The Status line above is the spec's 2026-09-13 state — the plan was approved and built. § What exists today / Real gap below are the **pre-build record** — kept for their reasoning, not as a description of current code; a `file:line` there points at where the code *was* when the spec was written. Current locations, re-verified against code this pass:
>
> - `SpawnTheUnmade` is `LoamPhases.cs:295-310`: `:296` calls `WildSpawnRoller.Roll(...)`, `:307` maps `p.SpeciesId` / `p.Hp`; the `"normalzombie"` literal is gone; `:271-283` is the caller's neglect/occupancy guard
> - `LoamPolicy.cs`: `UnmadeSpawnAfterTurns` `:213`, `UnmadeMemberHp` (`long`) `:219`, `UnmadeMemberCount` `:222`
> - ⚠ `CreatureAdmission.ForWildMap` still admits the 12 `speciesKind: "excluded"` rows — no C# reader of the mark exists (`creature-seed` map ask 4)
**Source ideal:** [species-selection-ideal.md](../species-selection-ideal.md) § The shape 3, § Wild map admission

> **Amended 2026-09-18 for owner rulings R-SS1 and R-SS2 (2026-09-17)** — Open question 1 and a note
> on coverage. **Build state, from git:** shipped as T7 (`d2361c761`, 2026-09-15) with its own table,
> `gk-core/data/tuning/world-spawn.v1.json` — the shape R-SS1 then ruled. T18b (`ee09f9d7a`) wired the members'
> species `P(Θ)`.

---

## Objective

**Put varied creatures on the world map by replacing one string literal with a weighted roll.**

> **Owner, 2026-09-13:** *"the creature will spawn on the map, we will extend world stage later to
> hunt them."*

This is the decided shape and it is **cheaper than the quest-board alternative an earlier draft
proposed**, because the spawner already exists, already places `Wild`-owned warbands at real sectors,
already guards occupancy, and already reports the event. The change is the species it puts in them.

**Why the map is the right targeting surface, not merely the cheap one:**

- **The map already answers "where."** A creature on a sector *is* a target with a location, and fog,
  lanes, march and claim are verbs the player already has for reaching one. A quest board would
  invent an abstraction beside a spatial system that already exists.
- **It is the Guiding Lands shape** — the genre's own answer to roster surfacing: a gated, stochastic
  pool distributed across regions.
- **Sector context is a natural weighting axis.** Climate already selects species elsewhere.
- **It needs no new vocabulary** — no `SpeciesKind`, no quest schema, no second targeting surface.

---

## What exists today — verified against code, not comments

### Built

- **`SpawnTheUnmade` (`World/Loam/LoamPhases.cs:271-282`)** constructs a complete `WorldEntity`:
  `Kind = Warband`, `OwnerFactionId` = the wild faction, `AtSectorId`, `Stance = Hold`, and
  `LoamPolicy.UnmadeMemberCount` members. The caller (`:260-262`) already guards occupancy, resets
  the neglect countdown and emits `unmade.spawned:<sectorId>` to the turn report.
- **Its cadence and size are already tunable** — `UnmadeSpawnAfterTurns`, `UnmadeMemberCount`,
  `UnmadeMemberHp`, all read from `Tuning.Texture` (`LoamPolicy.cs:199-208`). **Nothing about the
  spawn rhythm needs authoring.**
- **`WorldFactionKind.Wild` + `WorldEntity` already model a neutral, non-player force**, and
  `WorldEntityMember.InstanceId` is documented as *"null for non-player forces."*
- **`CreatureAcquisition`** is a closed flags enum (`Summonable = 1, CaptureOnly = 2, EventOnly = 4`).
  Measured over the 904 generated species: `Summonable` 869, `Summonable, CaptureOnly` 2,
  `CaptureOnly` 29, `EventOnly` 4.

### Wiring gap — one literal

`LoamPhases.cs:280`:

```csharp
.Select(_ => new WorldEntityMember { SpeciesId = "normalzombie", Level = 1, Hp = LoamPolicy.UnmadeMemberHp })
```

**Every wild warband on the map, on every sector, forever, is `normalzombie`.** One species.

### ⭐ Real gap found this session — the same defect in a second place

`World/Growth/RaiseResolver.cs:157-170 SpeciesFor(climate)` picks *"the zombie-side species whose
primary element matches, lowest by `SpeciesId` ordinal"* — its own comment says **"Deterministic, not
rolled."**

That is the *identical* shape as `WaveCatalog`'s `pool[i % pool.Count]`: a stable sort standing in for
a selection rule. With six elements, **the entire recruit path reaches at most six species.**

⚠ **This was not in the ideal and it changes the module's scope claim.** The map has *two* species
selection sites, not one. The literal at `:280` is the one the owner's direction names; `SpeciesFor`
is the one a player would notice next. **Open question 3 puts the scoping call to the owner rather
than absorbing it silently.**

⚠ **`SpeciesFor`'s determinism is load-bearing and must be preserved if it is changed.** Its comment
states the reason explicitly: *"pure, so a replay never disagrees with itself."* Any roll introduced
there must be seeded from replay-stable inputs, not from ambient state.

---

## The decided admission rule — per flag, not a blanket filter

`CreatureAcquisition` is read **per flag**, because the flags mean different things on a map than in a
wave:

| Flag | Wild map | Wave | Why |
|---|---|---|---|
| `Summonable` (869 + 2) | admit | admit | the ordinary roster |
| `CaptureOnly` (29 + 2) | ⭐ **admit** | refuse | **the wild *is* its acquisition route** — encountering it is how you capture it. Refusing it on the map strands 29 species entirely |
| `EventOnly` (4) | **refuse** | refuse | events own their own gating; a wild spawn would bypass it |

⛔ **This is deliberately NOT the rule `wave-species-roll` uses.** `WaveCatalog.Band` has no
acquisition filter at all today (`WaveCatalog.cs:153-154`) — a bug there, and it would be a different
bug here if copied blindly.

### ⭐ One declaring site, not two prose copies — a SOLID requirement, not a tidiness one

An earlier draft offered *"two rules, one enum, stated in both specs"* as the consistency mechanism.
**Prose duplication across two files is not an SSOT**, and this repo's binding SOLID rule (`S` and
`D`) says so: the same spec's Boundaries already forbid *"copying `Band`'s missing acquisition filter
into a new call site", while the draft hand-rolled a second predicate in a second file.

**So the admission rule gets one declaring site in Core** — a `CreatureAdmission` policy type with a
named member per context:

```csharp
/// <summary>Which species a context admits, read PER FLAG. One declaring site: a fourth context is
/// a new member here, never a re-derivation in a fourth file. EventOnly is refused first and
/// unconditionally in every context -- events own their own gating.</summary>
public static class CreatureAdmission
{
    public static bool ForWave(CreatureSpeciesDef s) => !Is(s, EventOnly) && Is(s, Summonable);
    public static bool ForWildMap(CreatureSpeciesDef s) => !Is(s, EventOnly) && (Is(s, Summonable) || Is(s, CaptureOnly));
    public static bool ForDelve(CreatureSpeciesDef s) => ForWildMap(s);   // decided: matches the map
}
```

**`wave-species-roll` and `delve-species-wiring` call the same type.** Whichever of the three modules
ships first creates it; the others add their member.

---

## Tech stack

C# .NET 8 (`FusionRpg.Core`, Unity-free), xUnit. No new dependency. No FE surface.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Loam"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurn"
dotnet test gk-core/tests/FusionRpg.Guard.Tests
dotnet test gk-core/tests/FusionRpg.Data.Tests
```

## Seedsmith / generator

**No generator involved today.** `gk-core/data/tuning/world-spawn.v1.json` is authored runtime tuning; its
`members` lists ship empty (the file's own `sourceRef`: *"the shape is the deliverable, the content is
the void-raid program's"*). Per R-SS2, generated spawn content — a seedsmith biome / world-event
design with its own chance and condition per species — belongs to **its own future program**, not
this module; when one exists it writes this table's `members` through a generator and the no-hand-edit
rule then applies to them.

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:271-282` | `SpawnTheUnmade` — the roll replaces the literal |
| `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs` | Existing cadence tunables — read, not changed |
| `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:157` | The second selection site (Open question 3) |
| `gk-core/data/tuning/` — a new world-spawn domain file, or `loam*.json` | The per-sector weight table |
| `gk-core/tests/FusionRpg.Core.Tests/World/` | Determinism, admission, climate-weighting tests |

## Code style

The roll is seeded from replay-stable inputs and the admission rule is named, not inlined:

```csharp
/// <summary>Which species a wild warband is made of. Seeded from (worldSeed, sectorId, turn) so a
/// replay never disagrees with itself — the same determinism guarantee RaiseResolver.SpeciesFor
/// documents. CaptureOnly is ADMITTED here and refused in waves: the wild IS its acquisition route
/// (species-selection-ideal.md § Wild map admission), so refusing it strands the species entirely.</summary>
static bool AdmittedOnWildMap(CreatureSpeciesDef s) =>
    !s.Acquisition.HasFlag(CreatureAcquisition.EventOnly)
    && (s.Acquisition.HasFlag(CreatureAcquisition.Summonable)
        || s.Acquisition.HasFlag(CreatureAcquisition.CaptureOnly));
```

⚠ Note the order: `EventOnly` is refused **first and unconditionally**. A species carrying both
`Summonable` and `EventOnly` must be refused, and a plain `||` chain would admit it.

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| Per-sector species weight table (`weightPerMille`) | What replaces the `"normalzombie"` literal. Same slot-table **shape** as `wave-species-roll`, keyed on sector instead of wave | New world-spawn domain file in `gk-core/data/tuning/`, beside the loam texture keys |
| `offClimateMilli` | How much an off-climate species is down-weighted (on 1000 / off `offClimateMilli`) | Same file — ⚠ **the Delve selector already ships this key**; reuse the name |
| Rarity window admissible per sector, and how it widens with progression | The Guiding-Lands gate: not every sector shows every rung | Same file |
| `UnmadeSpawnAfterTurns`, `UnmadeMemberCount`, `UnmadeMemberHp` | Cadence and pack size — **already shipped**, read not authored | `Tuning.Texture` (existing loam tuning) |

**Structural (stays `const`, with a comment saying why):** the seeded-RNG stream derivation and the
draw rule — determinism guarantees, not balance.

## Numeric types

Weights are `int` per-mille — a **bounded ratio**, exempt and commented as such.
`UnmadeMemberHp` is already `long` (`LoamPolicy.cs:205`) and stays `long`: it is an hp magnitude, and
`P(Θ)` is quadratic, so its range must hold the value at reachable `Θ` (`CLAUDE.md` "Numeric types").
**This module must not narrow it** when the per-member hp starts varying by species.

## ActorHub gate

**N/A and checked.** Choosing which species fills a wild warband produces no actor combat / derived /
AppliedCombat number. When such a warband enters battle its members compose through the existing
`ActorHub` path. **No private fold is introduced.**

⚠ One consequence to state rather than discover: today every Unmade member takes the flat
`LoamPolicy.UnmadeMemberHp`. Once members are real species, whether their hp comes from that flat
value or from the species' own `P(Θ)` is a **real design question** — see Open question 2. Answering
it with a private hp calculation would be exactly the defect the Hub rule exists to prevent.

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit | **Determinism** — the same `(worldSeed, sectorId, turn)` yields the same warband composition, twice, and across a shuffled catalog order |
| Unit | **`EventOnly` is refused**, including a species carrying `EventOnly` *and* `Summonable` |
| Unit | **`CaptureOnly` is admitted** — the rule that differs from waves, asserted explicitly so a later session cannot "unify" the two filters |
| Unit | A `Summonable, CaptureOnly` species is admitted (the flags enum is a bitfield; 2 species carry both) |
| Unit | Climate weighting biases toward the sector's climate without excluding off-climate species |
| Unit | A sector whose admissible pool is empty **does not throw** — it falls back to a named, documented species rather than crashing a turn |
| Unit | Occupancy guarding and the `unmade.spawned` report are unchanged |
| Contract | Every species id in the weight table resolves in `CreatureSpeciesCatalog` |
| Report | Distinct species reachable across a simulated N-turn world — **a reading, printed, never asserted** |

⛔ **No test asserts how many species a player meets.** That is a reading.

## Boundaries

**Always**
- Seed the roll from replay-stable inputs. `RaiseResolver`'s comment is the standard to match:
  *"pure, so a replay never disagrees with itself."*
- Keep the existing occupancy guard and turn-report event.
- Leave room in the spawn table for a **non-recruitable** wild creature (below).
- Commit with plain `git` (explicit paths).

**Ask first**
- Fixing `RaiseResolver.SpeciesFor` in the same change (Open question 3).
- Per-species hp replacing the flat `UnmadeMemberHp` (Open question 2).
- Any change to spawn cadence — that is shipped, tuned loam behaviour.

**Never**
- Copy the wave's acquisition rule here. `CaptureOnly` is **admitted** on the map.
- Assume every wild creature is recruitable (below).
- Introduce an unseeded roll on a replayed path.
- Design the hunt interaction. This module stops at *creatures are there and are varied.*
- Assert a population count.

---

## ⛔ The guard this module's successor must ship with, not after

**No single species' rewards may strictly dominate.**

The Wilds/Arkveld case is the documented evidence: once a hunt verb exists, monoculture follows
**reward dominance, not the UI**. A map full of creatures whose drops are strictly ordered will be
farmed at exactly one sector, and the variety this module creates evaporates.

This is `roster-metrics` (creature-seed module 14) pointed at encounters instead of anchors. It is a
**report, never a test assertion** — roster coverage is a reading. It lands **with** the hunt
interaction, which is deferred to the world stage; this spec records the obligation so it is not
discovered afterwards.

## Introduced, not designed — a third creature category

**Owner, 2026-09-13:** *"we will introduce some neutral unit that never become a legion troop — like
demon from the hell (new empire that need serious huge program) and void beast (non empire, empty,
that come from the void). I just introduce them here."*

| Concept | What it is | Status |
|---|---|---|
| **Demon** | A creature of a **new empire** — a faction in its own right, with its own territory logic | **Named only.** *"Needs a serious huge program."* |
| **Void beast** | **Non-empire** — belongs to no faction, holds no ground, arrives *from the void* | **Named only.** |
| **Void raid** | The void deploying beasts to **siege a player-held sector** | **Named only.** Its own future program |

⭐ **The one property both carry, and it is a real constraint on this spec:** they are **neutral units
that never become a legion troop.** Today a creature is either a **general creature** (engine-spawned,
troop-stack shaped, recruitable) or a **unique creature** (a `UniqueActor` specimen).
`creature-system-map.md`'s Vocabulary has no row for a permanently non-recruitable neutral.

**So the spawn-table shape must not assume every wild creature is recruitable.** That is the only
requirement this places on the module — nothing else here depends on them, and **nothing in this
document designs them.**

For whoever opens the void-raid program: the machinery is largely built. `docs/architecture/base-defense/`
carries a dozen-plus siege specs and `SiegeObjective.Evaluate` (`Battle/Siege/SiegeObjective.cs:36`)
already resolves `CoreTaken` / `AssaultBroken`; and ⭐ `DistrictAssaultResolver` reads
`request.AttackerEntityId` (`:59`) — **an entity, not a faction — so an attacker with no empire is
already expressible.**

## Success criteria

1. A wild warband's members are rolled from a weighted, sector-keyed table; the `"normalzombie"`
   literal is gone.
2. The roll is seeded and replay-stable, proven twice and across a shuffled catalog order.
3. `EventOnly` refused and `CaptureOnly` admitted, each with a test that names the rule.
4. Climate weighting is live and tunable; `offClimateMilli` reuses the shipped key name.
5. Spawn cadence, occupancy guarding and the turn-report event are unchanged.
6. The weight table is data; no species id and no weight is a `const` in C#.
7. Core, Guard and Data test suites green.
8. The spawn table can express a non-recruitable wild creature, even though none is authored.

## Open questions

1. ✅ **RULED 2026-09-17 (R-SS1) — its own table**, matching the recommendation, and **already built
   that way**: `gk-core/data/tuning/world-spawn.v1.json` (loaded by `WorldSpawnTuning.cs`, rolled by
   `WildSpawnRoller.cs`), separate from `waves.v1.json`. The accepted cost is a second table to author
   and keep covered. Original: *"Does the map spawn table share the wave slot table, or is it its
   own?"*

   **R-SS2 (2026-09-17), recorded here because this table is where it would otherwise leak in:**
   roster **coverage** is not this program's question. Which species reach the map, and how often, is
   the business of spawn surfaces that are each **their own program** — biome, delve, world assault,
   world event, summon, gacha — each with its own chance and condition. So this table carries **no
   coverage target**, and no test here asserts how many species it can reach. The measurement gap is
   real and owed to a **distribution statistic engine** the owner scoped out as its own program; this
   module's successor guard (§ The guard this module's successor must ship with) stays a report.
   ⚠ One consequence found while verifying, owned elsewhere: R-SS2's 2026-09-18 correction names 12
   `speciesKind: "excluded"` rows that must never spawn, but `CreatureAdmission.ForWildMap`
   (`CreatureAdmission.cs:19-21`) reads only `Acquisition`, and the runtime corpus carries those rows
   as `Summonable` (`creature-seed-ideal.md` header). The C# mirror of `speciesKind` is
   `creature-seed`'s open work; when it lands, the refusal belongs in `CreatureAdmission` — **one
   declaring site** — never in this roller.
2. ⭐ **DECIDED 2026-09-13 (owner): species `P(Θ)` via `species-magnitude-synth`**, not the flat
   `UnmadeMemberHp`. The flat value is a placeholder for one species and becomes a lie at 900 — see
   the header's new `Depends on` line. Members' magnitudes compose through the existing container
   path this initiative already builds; no second stat mechanism.
3. **Does `RaiseResolver.SpeciesFor` get fixed here or filed separately?** It is the same defect
   (deterministic first-by-ordinal, ~6 species reachable) in the recruit path rather than the wild
   path. **Recommendation: file it as its own small task** — it changes what a player's *own* legions
   are made of, which is a different blast radius and deserves its own review.

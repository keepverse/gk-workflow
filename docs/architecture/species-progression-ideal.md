# Species progression — the ideal

**Status:** idea phase, 2026-09-16. **Not a spec. No build authorized.**

> **Updated 2026-09-17.** **4 owner rulings landed 2026-09-17** (R-S1–R-S4). **R-S1 closes `solid-remediation`’s S7**: a species level grants **allocation**.
> **Specced 2026-09-18:** capability map and module specs at [species-progression-map.md](species-progression-map.md). Its three OWNER questions were answered the same day by [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) R1–R3, and R16 extended R2 to layer 2a. **Where this ideal and the rulings disagree, the rulings win**; the stale lines below carry a dated note rather than being rewritten.

Scope: **layer 1b** (player-modified species) and **layer 2b** (empire species progression) of the actor
layer stack. Layer 2a (specimen progression) is already correct in code and is described here only where
2b has to stay exclusive of it. *(Superseded in part 2026-09-18 by R16: 2a's points today share the
commander's denominator on every path, and R16 rules that they resolve alone; the one change is
`species-layer-delivery` step 6.1.)* Battle-engine reconcile — reflect being lawn-only, 11 of 13 atom triggers
never firing in battle, the per-mode subsystem split — is **deliberately not in this doc**; the owner
deferred it to its own pass, and two audits are running against it.

Supersedes nothing. Extends [actor-layer-compose-ideal.md](actor-layer-compose-ideal.md), which ruled the
layer stack this doc builds two layers of.

---

## Step 0 — the principles, in my own words, before anything else

These are restated here rather than linked, because a downstream session reads this doc, not its links.

1. **Every RPG feature lives in the RPG layer. It is never built by changing what PvZ is.** PvZ owns the
   board, vanilla damage, spawn/die and the sun bank. We *observe* its events and contribute *signed
   deltas* back. We never read its current state, never rewrite it, and never make a feature depend on
   it representing a concept. A species level is an RPG concept; PvZ will never have a field for it, and
   that is not a constraint on this feature. The question "does the lawn support X" is almost always the
   wrong question — the right one is "does the RPG layer express X, and is that path wired."
2. **The PvZ write surface constrains exactly one thing:** what a *persistent vanilla stat change* may
   touch. As of 2026-09-16 it is narrower still — **no term of the damage equation is written into PvZ
   at all** (attack, plant shield, armor, take-damage multiplier are all retired), and the lawn transport
   is a **delta over `hp` / `armor1` / `armor2`**. Everything else resolves in the RPG layer.
3. **One ActorHub compose, one read.** Actor combat derived numbers compose exactly once, in `ActorHub`.
   A layer is a **source** of `DerivedModifier`s into that one fold — never a stacking tier, and never a
   second composer. The per-channel `DerivedComposeKind` owns how contributions combine. `BattleStatComposer`
   was a dual-compose defect, overturned and deleted; it is an incident, never a precedent.
4. **Two async systems, deltas not absolutes, record-then-drain.** Delay is the designed degradation mode.
5. **One power ladder.** Contests read `Θ` (linear, difference-based); magnitudes read `P(Θ)`. A private
   `f(level)` in a subsystem is the exact defect that let three incompatible curves ship at once. A
   species level must reach a magnitude *through* the ladder, not beside it.
6. **The balance surface is data.** Any number a balance pass would touch lives in
   `gk-core/data/tuning/<domain>.v{n}.json`, not a `const`.
7. **No hard progression ceilings.** Endless grind is the SSOT other systems reconcile *to*. A cap on a
   magnitude is a progression ceiling until proven otherwise; structural limits and bounded ratios are
   exempt and must say so in a comment.
8. **Gameless-first is a capability, not the pitch.** Whatever species progression becomes, it must stay
   playable with Fusion closed once unlocked. The injector may enrich it; it may never permanently gate it.
9. **Seed → concrete.** The seed is generator input, shared and deterministic; the concrete is per-player
   and produced by a real in-game event. This is the law for items, actions and creatures alike
   (`creature-seed-map.md` §1), and layer 1a/1b is where it lands for base stats.

---

## Which loop this extends

From [the-loops.md](../guide/the-loops.md):

- **Spine A — "Level up and power".** Its own status line already says *"species builds and meters **WIP**"*
  and its body already promises *"Specimens, species, and types also level from work they did."* Layer 2b
  is that sentence made true for a general creature. This is the primary loop.
- **Spine B — "Creature summon and fusion".** Layer 1b is where a fusion pick finally means something:
  today a pick is recorded and reaches no stat.
- **Vision hole — "Enemy counter-development"** (hangs on farm/hunt/defend · world events · Zomboss).
  Zomboss's own empire species progression *is* that hole, approached from the stat side.

No new loop is proposed. The lawn does not become the whole game: species progression is empire-scoped
and follows the actor into siege, world map and delve, because the empire is what owns it.

---

## What this is

**Two layers that answer two different questions about the same creature.**

> **1b — "what did *my* fusion lab make of this species?"**
> Per `(player, species)`, append-only, written only when a real mechanism modifies the species. Most
> players have no row for most species. Fusion picks are the one writer today.
>
> *(Superseded 2026-09-18 by R3 → `save-identity` G3: 1b is keyed by the **empire of the save** that paid
> for the pick, `(SaveId, EmpireId, species)`, never by the person.)*

> **2b — "what has my empire *learned* about fielding this species?"**
> Per `(empire, species)`, earned from work the species did, applied to **every general actor of that
> species in that empire**. A lawn plant reads the player's empire; a lawn zombie should read
> **Zomboss's** — a `players` row found-or-created by name (`RpgStore.ZombossDeploy.cs:25-29`), never by a
> fixed id.
>
> *(Superseded 2026-09-18 by R3: Zomboss is no longer a player row. A Save owns its empires, keyed
> `(SaveId, EmpireId)`; a lawn zombie reads Zomboss's empire **of the run's save**. R1: zombie species XP
> credits that empire.)*

The owner's framing, which is the acceptance test for this whole doc:

> *"The plant/zombie in lawn run that spawned will get their empire's specie progression, the final stats
> will be base specie stats (from species seed) + progression stats. So the general actor will work same
> way as unique actor, only difference progression module."*

and the failure it names:

> *"Our test in the live run yesterday not work on real game because species and empire progression system
> never made — the current progression for plant/zombie type only have level, so if player play the game,
> the general species spawn in game never earn progression or buff."*

**The second sentence needs correcting in both directions, and the correction is the most useful thing in
this doc.**

- Species progression **is** earned today, in volume, and on the lawn a species level **does** already
  become a stat: `SpeciesBaselineAllocation` reads `GetRpgActor(playerId, Species, creatureTypeId)?.Level`
  (`RpgStore.Aptitudes.cs:208`) and turns it into an `AptitudeAllocation`, which `AptitudeSubsystem` folds
  into `progression.bonus.*`. That path runs for a general lawn actor. So "never made" is too harsh.
- But it is credited to **the wrong empire**, absent in **battle**, and Zomboss **earns nothing at all**.
  So "the general species spawn in game never earn progression or buff" is right about the *outcome* on
  the zombie side, for a different reason than the one named.

What is actually missing is narrower and more fixable than "a system": **an empire dimension on a cache
key, a species term in the battle compose, and an XP writer that credits Zomboss.**

---

## What already exists

Three buckets, the repo's own words. `file:line` for every claim. Everything below was verified against
code in this session — by me directly, or by a read-only inventory pass whose load-bearing claims I then
re-verified myself. **Three claims inherited from [actor-layer-compose-ideal.md](actor-layer-compose-ideal.md)
turned out to be wrong, and one of my own did; they are corrected in place and called out, because a wrong
finding that survives into a spec is worse than no finding.**

### Built

| What | Where | What proves it |
|---|---|---|
| **The `(player, species)` progression row** | `RpgStore.cs:495-508` — `rpg_actor_progression`, `PRIMARY KEY (player_id, kind, type_id)`, carrying `level`, `xp`, `highest_level`, `demotion_count`, `revision` | The grain exists. Kinds are a closed set — `player`, `plant`, `zombie`, `species`, `specimen` (`RpgProgression.cs:3-26`) |
| **Species level to a real stat, on the lawn** | `RpgStore.Aptitudes.cs:200-211` `SpeciesBaselineAllocation` reads `GetRpgActor(playerId, Species, creatureTypeId)?.Level` then `SpeciesAllocation.Baseline(shares, level, tuning)`; `AptitudeSubsystem` folds it into `progression.bonus.*` | **The finding that reframes the program.** The 2b pipeline is not missing; it runs, for general lawn actors, today |
| **Species XP, both faucets, live** | placement `RpgXpAwardMap.cs:92-114`; run-completion `RpgStore.Progression.cs:79-123`, deduped `run-complete:{runId}:{speciesId}` (`:115`) | Observed live: `{zombie_spawn: 47985, species_run_complete: 8484, plant_place: 1030}` — a reading taken 2026-09-16, not a constant |
| **The progression-source claim grammar** | `CreatureProgressionSource.cs:8-75` — closed, versioned (`creature.progression.v1`): `general:{speciesId}`, `unique:{instanceId}:{occurrenceId}`, `commander:{commanderId}` | *"The source is explicit data, never inferred from a PvZ type id"* — its own doc comment. Enforced at `RpgXpAwardMap.cs:116-131`; stamped injector-side at `EntityApply.cs:289-295` |
| **2a/2b exclusivity** | `SpeciesAllocationSource.Resolve` (`:92`) — Bound-unique branch returns early (`:98-102`), species branch otherwise (`:105-117`), never both | Pinned by `SpeciesAllocationSourceTests.cs:163-183`, all four cells |
| **Fusion picks, end to end through the browser** | FE `FusionPage.tsx:230-256` to `FusionEndpoints.cs:247` to `RpgStore.Fusion.cs:229-284` (validate, nine named refusals) to `:365-377` (write) | A real feature with a real refusal vocabulary, rarity-slot-capped by `FusionRoller.SlotsFor` (`:240-241`) |
| **The `species-passive` container kind** | enum `ContainerRow.cs:30`, prefix `:186`, parse `RpgStore.Containers.cs:570`, validation `ContainerValidator.cs:28,49-56` | The id grammar *structurally* pairs kind and prefix — `species-passive.*` to `ContainerKind.SpeciesPassive`, not a convention |
| **The `(player, X)` append-only table idiom** | `player_species` (`RpgStore.PlayerSpecies.cs:45-54`), `rpg_species_respec` (`RpgStore.SpeciesRespec.cs:32-42`), `rpg_material_spend_log` (`RpgStore.Materials.cs:60-72`), `effect_instance_op` (`RpgStore.InstanceOps.cs:46-66`) | 1b has four precedents. The last two carry **provenance** (`recipe_id`/`correlation_id`, `op_kind`/`op_seed`/`catalog_revision`) — exactly what `player_species` lacks |
| **Layer 3/4/6/7** | equip, tree, aura, status | All reach the fold; 1b and 2b are the holes in an otherwise-wired stack |

### Wiring gap

**W1 — the lawn's species-allocation transport has no empire dimension, so a zombie is credited to the
human player.** The sharpest finding in this doc, and the mechanical form of the owner's complaint.

`SpeciesAllocationSource.Resolve` (`:117`) calls `_resolveSpeciesAllocation(lookup.SpeciesId)` — a
`Func<string, AptitudeAllocation>` (`:35`): **speciesId in, allocation out, no empire, no player.**
`ctx.PlayerId` is never consulted on that branch. In production:

```csharp
// CheatState.cs:176-177
resolveSpeciesAllocation: speciesId => _speciesAllocations.TryGetValue(speciesId, out var a)
    ? a : AptitudeAllocation.Empty,
```

`_speciesAllocations` is filled by `ApplySpeciesAllocations` (`CheatState.cs:190`) from `RpgClient.cs:520`,
whose data comes from `GET /api/aptitudes/{playerId}` (`RpgClient.cs:484-490`) where `playerId` is
`/api/players/current` — **the human**. Server side, `AptitudeEndpoints.cs:161-167` builds it from
`ListLevelledSpeciesIds(playerId)` plus `EffectiveSpeciesAllocation(playerId, speciesId, ...)`.

The lookup *is* side-aware (`ResolveSpeciesLookup(ctx.Side, ctx.TypeId)`; the class notes
`polevaulterzombie`/`wallnut` share a `GameTypeId` but never a `Side`), so a lawn zombie resolves a real
`speciesId` — and then reads **the human's allocation for it**. The injector holds exactly one species
dictionary, fetched for one player id. **The cache key is one dimension short.**

**W2 — battle receives no species allocation at all.** `WebMatchService.cs:602-603`:

```csharp
Aptitude = commanderAllocation + _store.LoadAllocation(
    AllocationScope.UniqueCreature, s.Profile.InstanceId),
```

No CreatureType/species term — despite a comment four lines above (`:558-561`) claiming *"the species read
stays per-actor"*. Corroborated: `EffectiveSpeciesAllocation` has exactly **two** production callers in
`src/`, both in `AptitudeEndpoints.cs` (`:164`, `:184`), neither on a battle or sheet compose path.

The deeper reason is that the two compose paths do not share registration. `BattleHubCompose.Compose`
(`BattleHubCompose.cs:41-64`) builds `new ActorHub(...)` directly and deliberately does **not** use
`ActorHubBootstrap.CreateDefault` (`:15-17`) — so it registers neither `RpgProgressionSubsystem` nor
`StatusDerivedSubsystem`. A general lawn actor goes through `CreateDefault` and gets a species term (from
the wrong empire); a battle actor goes through `BattleHubCompose` and gets none.

**W3 — nothing credits progression to Zomboss's player row.** Every species and type XP write goes to the
`playerId` on the capture (`RpgStore.Progression.cs:46-48`, `:116-119`; `RpgStore.cs:1889-1898`), and that
is the human. Zomboss's own id is never passed to `ApplyRpgProgressionFromActivityUnlocked`.
`MatchHost.cs:306-310` documents the inference used instead — *"any registered owner that is NOT this
player is, by elimination, Zomboss's own"* — and `:322-324` states that an ambient vanilla zombie is
explicitly **not** one of Zomboss's registered units. **The general horde has no owner row at all.**

So the 47,985 `zombie_spawn` XP is not Zomboss levelling up. It is the human player levelling a zombie
species, on their own row, which their own lawn plants never benefit from and which Zomboss's zombies then
read as if it were theirs.

**W4 — fusion picks are recorded and reach no stat.** The pick lands in an `effect_instance` referenced
only by `player_species` (`RpgStore.Fusion.cs:334-377`), and nothing binds that table:
`MaterialisePlayerSpecies` writes `effect_instance` plus `effect_instance_atom` plus `player_species` and
**never writes `effect_binding`** (`RpgStore.PlayerSpecies.cs:98-126`, retired by SP0.4/SP0.6 — the
method is gone; this whole W4 defect is the one `species-mod-ledger` fixed). The stat fold reads bindings by
owner scope only (`EquippedBoundAtoms.cs:23-25`), and a `player_species` instance has no owner scope.
`player_species` is a closed loop: fusion reads what fusion wrote.

**W5 — the picks feature is dark in production, for a reason nobody intended.**
`picks.source-not-materialised` (`RpgStore.Fusion.cs:266`) fires whenever the sacrifice's species has no
`player_species` row. And **`MaterialisePlayerSpecies` has no production caller** — verified 2026-09-16:
`grep -rn MaterialisePlayerSpecies src/ web/ tools/ scripts/` returns the definition (`:63`), one doc
comment (`:137`), one comment in `RpgStore.Fusion.cs:314`, and compiled DLLs. Every real call site is in
`tests/`. Its only other writer is the debug route `POST /api/debug/reforge-world`
(`DebugEndpoints.cs:1233`).

So a player who has never triggered a debug reforge has **no pickable atoms at all** —
`FusionEndpoints.cs:194` silently yields an empty `pickableAtoms` and the FE panel never renders
(`FusionPage.tsx:230`). A shipped, validated, nine-refusal feature is unreachable because one upstream
writer lost its caller.

**W6 — the Bound-unique Hot path still resolves the empire fallback.** `decisions.md`'s own 2026-09-12
amendment: the Injector Bound Hot path resolves `commander + CreatureType` for a Bound unique while the
sheet Hub uses `UniqueCreature`. That **violates the ownership row** — a unique must never receive the
empire species fallback. Tracked as **HF-lawn**.

### Real gap

**R1 — `plant`/`zombie` type level reaches no channel.** `RpgProgressionSubsystem.ContributeDerived`
(`RpgProgressionSubsystem.cs:42-54`) adds exactly two modifiers — `progression.power` and a
`progression.realm` stub — and I read the whole body: there is no third `mods.Add`. Of every reader of a
`rpg_actor_progression` row, the `plant`/`zombie` kinds reach **display counts, buckets and almanac name
promotion only** (`RpgStore.Progression.cs:354-365`, `:886-935`). **A plant type at level 4 composes
exactly as one at level 1.** The kinds that do reach a channel are `species` (via
`RpgStore.Aptitudes.cs:208`) and `player` (via Theta).

**R2 — layer 1 binds nothing to anything, and there are two dark carriers, not one.**

| | `species-passive.{id}` | `trait.species-magnitude-{id}` |
|---|---|---|
| Kind | `SpeciesPassive` | `Trait` (deliberately — `RpgStore.UniqueActors.cs:1555-1567`) |
| Shape | rolled: fixed core atoms plus affix pool | flat, pre-computed |
| Authored today | **3** (`peashooter`, `sunflower`, `conezombie`) | **0** |
| Bound to an actor | never — no `effect_binding` is ever written | only `OwnerKind.UniqueActor`, and inert |
| Per-player instance | yes, `player_species` | no |

The binder (`ReconcileCreatureMagnitudeBindingsUnlocked`, `:1588`) is complete, revision-aware and fails
closed — and returns early on **every** deploy at `:1615`, because `CreatureSpeciesDef.Magnitudes` is empty
for every species; even if it were not, `:1620` would fail closed because 0 such containers are authored.
**And no binding is ever created for a plant- or zombie-scoped owner anywhere:** a grep for
`OwnerKind.Plant` / `OwnerKind.Zombie` across `gk-core/src/FusionRpg.Data/` and `gk-core/src/FusionRpg.Server/` returns
zero hits.

> WARNING — correction to [actor-layer-compose-ideal.md](actor-layer-compose-ideal.md): its layer table
> records layer 1a as *"0 authored"*. That is the **magnitude** container count. `species-passive` has
> **3** authored entries. The two carriers were conflated.

**R3 — no container anywhere is re-projected when a level changes.** The mechanism exists in two halves
that have never been joined:

- `TreeBoundAtoms` (`TreeBoundAtoms.cs:33-85`) projects from numeric state (owned nodes, gate points,
  Theta) and invalidates correctly (`TreeBoundAtomsCache.Apply` then `CheatState.Stats.Invalidate()`) —
  **but emits atoms, not a `ContainerRow`.**
- The species-magnitude binder (`RpgStore.UniqueActors.cs:1588-1628`) is container-shaped and
  revision-driven — **but has no generator behind it.**

The only code paths that persist a *generated* `ContainerRow` are debug-only
(`CreatureEndpoints.cs:230-235`, `DerivedAuditActor.cs:152-159`). This is the one genuinely new mechanism
the program needs.

**R4 — there is no species level-to-magnitude rule.** No curve, no policy, no tuning key says what level 7
of a species is worth beyond the generic aptitude baseline. This is the content question.

**R5 — species XP is lawn-general-only.** `RpgXpReasons.SpeciesExpedition` (`RpgProgression.cs:44`) has
**zero writers** — measured 2026-09-16; `SpeciesExpeditionTests.cs:44-66` in fact pins the opposite, that
an expedition win levels the specimen and leaves the species row null.

**R6 — the species bake carries no identity.** 730 of 904 share `theta 13`, 450 share
`resource.max.hp 2712`, Peashooter and GatlingPea bake identically. Owned by `lawn-tuning-profile`'s
`species-flavour-lawn`. Named here because **2b can be built correctly and still change nothing a player
can see.** *(Counts are the prior doc's readings; not re-measured — no RPG database exists in the working
tree.)*

### Four claims that turned out to be wrong

Recorded rather than quietly dropped, because two of them are the premise of an owner ruling.

**1. The cross-player fusion leak does not exist.** `actor-layer-compose-ideal.md` treats
`RpgStore.Fusion.cs:243` as fusion *writing* into the shared `species-passive` container, and builds a
three-option hazard on it (*"player A's picks would define the species for player B"*). The line, verified:

```csharp
outputSpeciesContainer = GetContainer("species-passive." + output.SpeciesId);   // :243 - a READ
```

It is fetched as the **compose template** and handed to `InstanceProducer.Compose(..., forcedPicks)`. The
write is `INSERT INTO player_species` (`:365-377`). **Fusion never writes `effect_container`** — the only
writers are the seed importer and two debug routes. The guard is per-player (`:237`), the roll seed is
per-player (`:322`), and `effect_container` has no `player_id` because nothing player-facing writes it.

**What this means for the owner's ruling.** *"We need new table to store player roll by fusion... explicit
boundary between base species and player modified species"* was reasoning from a leak that is not there —
but the ruling survives on a different and better justification: `player_species` has **no provenance
column** (`RpgStore.PlayerSpecies.cs:45-54`), so a fusion-written row and a debug-reforge-written row are
byte-indistinguishable, and a second 1b mechanism would be indistinguishable from both. That is the real
argument for 1b's own table, and `rpg_material_spend_log` / `effect_instance_op` already show the shape.

**2. The eager roll does not happen.** The prior doc says `SpeciesMaterialiser` *"rolls every species for a
player eagerly, at first contact"*. The Core-side loop does exist (`SpeciesMaterialiser.cs:49-52`), but the
DAL method that drives it has no production caller (W5). **"Delay the roll" is already the de-facto
state** — so completely that it has broken fusion picks. The owner's instinct was right; the problem turned
out to be the opposite of the one diagnosed.

**3. My own claim that a species level reaches no stat was wrong.** I reasoned from
`RpgProgressionSubsystem` adding only two modifiers. That subsystem is not the path:
`SpeciesBaselineAllocation` then `AptitudeSubsystem` is, and it works. The claim is true of
**`plant`/`zombie` type** levels (R1), not of **species** levels.

**4. "Zomboss is `players` id 3" is a doc claim, not a code fact.** `RpgStore.ZombossDeploy.cs:10-13`
states explicitly that `players.id` carries no schema meaning, and `EnsureZombossPlayer` (`:25-29`)
find-or-creates by the **name** `"Zomboss"`. The id-3 figure comes from `creature-scope-ideal.md:67`. Any
design that keys on the literal 3 is keying on one database's accident.

---

## The question this all reduces to

[actor-layer-compose-ideal.md](actor-layer-compose-ideal.md) cut every finding against one question:

> *"Does the one compose have all its layers — **present**, **fresh**, **affordable**, and **reaching
> combat**?"*

**Two of those four closed on 2026-09-16, which is why this program is worth starting now:**

| Part | Then | Now |
|---|---|---|
| **Affordable** | `hub.resolveDerived` 1,624 µs avg; RPG capture pipeline 28.06% of wall at 19.8 fps | 823–895 µs avg; pipeline **3.46% of wall at 59.7 fps**, under the 6% ceiling (`_baseline-lcw-300z-hud-resync-b60.json`) |
| **Reaching combat** | rider `DefaultEnabled = false` after the frame-budget breach | **default ON** (`LawnBasicAttackFeature.DefaultEnabled = true`), on that measurement |
| **Fresh** | Θ frozen, player switch never reaches the injector, post-deploy allocation does not reach Bound | unchanged — still open |
| **Present** | layers 1b and 2b missing | unchanged — **this doc** |

So the compose is now cheap enough to run and its output now reaches a real hit. **What it composes is
the remaining problem**, and 1b and 2b are two of the three pieces missing from it.

---

## Prior art, with numbers

Four systems solved exactly this split. The numbers matter more than the descriptions.

### Pokémon — the cleanest 1a / 1b / 2a separation in the genre

Three independent stat sources per creature, and the separation is almost exactly the layer stack:

| Pokémon term | Scope | Range | Our layer |
|---|---|---|---|
| **Base stats** | the species — identical for every individual | 1–255 per stat | **1a** |
| **IVs** (individual values) | one creature, fixed at capture | 0–31 per stat | *(no equivalent — see below)* |
| **EVs** (effort values) | one creature, **earned by fighting** | ≤252 per stat, **510 total**; every **4 EVs = +1 stat point** at level 100 | **2a** |

Formula: `Stat = (((2 × Base + IV + EV/4) × Level / 100) + 5) × Nature`.

**What to take.** The species term and the earned term are *separate addends inside one formula* — never a
multiplier of each other, and never a second stat block. That is the same "every layer contributes into the
one fold" rule this repo already has. **252 EVs buys about +63 to a stat** against base stats that run to
255: the earned term is deliberately worth *less* than species identity. A Snorlax that trains Speed never
outruns a Garchomp.

**What to reject.** Pokémon has no 1b — no mechanism lets a player permanently redefine a species. That is
the thing fusion gives us that the prior art does not have, so nothing here constrains 1b's design.

Sources: [Bulbapedia — Effort values](https://bulbapedia.bulbagarden.net/wiki/Effort_values) ·
[VGC guide — base stats](https://www.vgcguide.com/base-stats) ·
[Pokémon IVs & EVs explained](https://pokedaily.net/iv-ev/)

### Age of Empires II vs Total War — the 2b / 2a split, shipped twice

The owner's ruling (*"specimen level up by themselves, empire species level up general actor"*) is the
difference between two shipped genres:

| | **Age of Empires II blacksmith** | **Total War chevrons** |
|---|---|---|
| Scope | **faction-wide**, by unit class | **per individual unit** |
| Earned by | researching a technology | that unit's own kills |
| Magnitude | Forging **+1**, Iron Casting **+1**, Blast Furnace **+2** — **+4 melee attack across the entire game** | **+1 melee attack and +1 defence per chevron**, to a maximum of **nine** |
| Applies to | every existing *and future* unit of that class, immediately | only that unit; dies with it |
| Our layer | **2b** | **2a** |

**The number worth staring at is +4.** Age of Empires lets a faction-wide upgrade move melee attack by four
points *across an entire match*, on units whose base attack is roughly 4–13. That is not timidity — it is
the correct discipline for an empire-wide bonus, because **it multiplies across every unit on the board at
once**. A per-unit bonus is paid once; an empire-wide one is paid N times.

Set that against our own species bake carrying `resource.max.hp 2712` where vanilla is 300, and the shape of
the mistake this program could make is already visible. Total War's per-unit ceiling (nine chevrons, +9/+9)
is *larger* than AoE's faction-wide one, and that ordering is not an accident.

**What to take.** An empire-wide per-species bonus should be **small, bounded and legible** — and it should
apply to units already on the board, not only to future spawns, because a player researching an upgrade
mid-fight expects to see it.

Sources: [AoE2 Blacksmith](https://aoe2.guide/the-blacksmith/) ·
[Forging — Liquipedia](https://liquipedia.net/ageofempires/Forging) ·
[Effects of Experience — Empire: Total War Heaven](https://etw.heavengames.com/articles/strategy/campaign/effects-of-experience/)

### Skyrim races — layer 1a as a differential, not a stat block

Every race starts from the *same* pool: **360 points across Health/Magicka/Stamina**, every skill at base
**15**. The race adds a small fixed differential: **+10 to one skill, +5 to five others**, plus one racial
perk (High Elf **+50 maximum Magicka**, Breton **+25% magic resist**) and one power. A High Elf's Archery
starts at 15, not at a separate elven number, and the race never changes again.

**What to take.** Layer 1a contributes *how this species differs from the shared base* — it is not the
actor's whole stat block. This is what resolves the `2712`-vs-`300` contradiction without a rescale: read as
an absolute it is wrong, read as a differential it is simply the wrong unit for the job.

### RimWorld wealth scaling — the documented failure mode for W3

RimWorld scales raid strength off colony wealth. The documented failure: **everything a player does outside
research raises the threat**, including upgrading pawn skills and equipment, and raw materials contribute
*more* threat than the walls and floors built from them — so building up your base can paradoxically make
you weaker. Ludeon's own remedy is instructive: the game now ships a **"wealth-independent progress mode"**
storyteller setting where threat instead **increases linearly over time**.

**What to take, and it is a warning, not a pattern.** If Zomboss's species progression is driven by the
player's own power, the player is punished for progressing, and the lawn stops rewarding investment. The
shipped counter-example — decouple the enemy clock from player wealth and let it run on its own — is
directly applicable to Open question 2.

Sources: [RimWorld Wiki — Raid points](https://rimworldwiki.com/wiki/Raid_points) ·
[RimWorld Wiki — Wealth](https://rimworldwiki.com/wiki/Wealth) ·
[RimWorld Wiki — Wealth management](https://rimworldwiki.com/wiki/Wealth_management)

---

## The shape

### What each layer is, in the stack's own five questions

[actor-layer-compose-ideal.md](actor-layer-compose-ideal.md) says any feature that changes what an actor's
numbers are must answer five questions before it is built. Answering them here is most of the design.

| | **1b — player-modified species** | **2b — empire species progression** |
|---|---|---|
| **1. Which layer** | 1b — already in the closed list | 2b — already in the closed list |
| **2. Scope** | per `(player, species)` — *superseded by R3/G3: `(SaveId, EmpireId, species)`* | per `(empire, species)`; empire is the `players` row, so `(player_id, species)` — resolve Zomboss's by name, never by a literal id — *superseded by R3: `(SaveId, EmpireId, species)`, Zomboss is an empire of the save, never a player row* |
| **3. Lifetime** | **append-only**, grows as the player plays; most players have no row for most species | mutable level/XP, monotonic except for the existing demotion path |
| **4. Carrier** | a container, bound at deploy (owner: *"container, our repo standard"*) | a container per `(empire, species)`, **re-projected on level-up** |
| **5. Provenance** | a GG-49 SourceId — e.g. `species.player.{speciesId}` (*specced as `species-player:{speciesId}:{mechanism}`, map §4*) | e.g. `species.empire.{empireId}.{speciesId}` — the empire must be *in* the id, because two empires level the same species independently (*specced as `species-empire:{empireId}:{speciesId}:{aptitudeId}`, map §4*) |

Both contribute `DerivedModifier`s into the one fold. Neither decides a number itself.

### Why 2b is a projection, not a subsystem

Progression reaches the compose today as aptitude *allocation math* through `AptitudeSubsystem` — it works,
but it is the one layer outside the container model, and the model is what makes the other layers
inspectable, revisable and bindable. The owner ruled every layer is a container.

So the shape is: **`(empire, species)` level → a projector → a container → the existing binder → the one
fold.** Every piece of that except the projector already exists, and the binder
(`RpgStore.UniqueActors.cs:1588`) is complete, revision-aware and fails closed. `revision` is already a
column on `rpg_actor_progression` (`RpgStore.cs:503`), which is exactly the invalidation signal a
re-projection needs.

**This is the same shape as 1a's missing generator stage (R1).** Both are "numeric state that exists →
container that does not". Building one projector mechanism that serves both is the obvious economy, and is
the strongest argument for doing 1a and 2b in one program rather than two.

### The one precision that keeps this from forking the composer

A layer is a **source**, never a stacking tier. "Base species stats + progression stats" — the owner's own
phrasing — means both emit `DerivedModifier`s naming the same channels, and the channel's own
`DerivedComposeKind` decides how they combine. It does **not** mean 2b multiplies 1a, and it does not mean
2b reads 1a's output. If 2b ever needs to know 1a's value to compute its own, that is a second composer
wearing a new word.

### Where the numbers must not go

Two bans already apply and constrain the design before anything is written:

- **`actor-hub-ssot.md` §8:** *"Progression combat flats use `progression.bonus.*` only — not primary
  hp/atk channels."* 2b contributes to `progression.bonus.*`, not to `resource.max.hp`.
- **`actor-hub-ssot.md` §8:** *"Do not wire level→damage silently; `progression.power` is catalog derived
  only."* A species level may not become damage by a private curve. It goes through the ladder.

### What reaches the lawn

Nothing in either layer needs a new PvZ field. Both resolve in the RPG layer and arrive at the lawn the way
everything else does: composed into the Hub snapshot, then transported as a **delta over `hp` / `armor1` /
`armor2`**, with every channel PvZ has no field for staying in the RPG layer and resolving through the
RPG's own damage path. A species that levels into more crit, more elemental defence or more shield capacity
changes real outcomes on a real lawn without PvZ ever hearing about it.

---

## Tunables

Every number this introduces, and the file that owns it. None of these is a `const`.

| Number | Where it belongs | Why it is tunable |
|---|---|---|
| XP required per species level | `data/tuning/species-progression.v{n}.json` | The pacing dial; a balance pass changes it constantly |
| What one species level is worth (the allocation or magnitude rule) | same | **The** balance number of this program |
| Per-species-level cap, if any | same | Must be a **soft, configurable** cap or none at all — PS-8: a cap on a magnitude is a progression ceiling until proven otherwise |
| The plant/zombie XP award asymmetry | same | Today ~47:1 by event count; whether that is intended is Open question 2 |
| Zomboss's progression clock | same | Whatever drives W3 — time, sector, authored ladder — is a dial, not a constant |
| 1b slot count per species | `gk-core/data/tuning/` (fusion's existing domain) | `FusionRoller.SlotsFor` already rarity-caps picks; 1b inherits that rather than inventing a second cap |

A `SpeciesProgressionTuningHub` already exists and is consulted (`RpgXpAwardMap.cs:100`,
`SpeciesProgressionTuningHub.Tuning.PlacementAward`), so this is an extension of a live tuning surface, not
a new one.

---

## What this deliberately does not decide

- **The battle-engine reconcile.** Audited separately on 2026-09-16
  ([battle-derived-wire-audit](../research/battle-derived-wire-audit-2026-09-16.md)); 2b must eventually
  reach both compose paths, but *how the two paths reconcile* is that program's call, not this one's.
  One finding from it does constrain 2b's design and belongs here: **battle's `EffectBag` never sets
  `CombatMath`** (`BattleEffects.cs:55-64`), so `CombatDamageDispatcher` falls back to
  `PassThroughCombatMath` (`:28`), whose `Finalize` returns the amount unchanged (`ICombatMath.cs:15-16`).
  Battle's *basic attack* does go through the resolver, but every effect-driven hit in a battle — DoT tick,
  on-hit rider, atom damage — applies its authored amount verbatim, with no hit roll, crit, element
  matchup, penetration, parry or block. **So a 2b bonus on any of those ~20 channel families would compose
  correctly in battle and still change nothing**, exactly as R6 warns for the lawn.
- **Species flavour** — R6. Whether a Peashooter and a GatlingPea bake differently is
  `lawn-tuning-profile`'s `species-flavour-lawn`. This doc only records that 2b is worth less without it.
- **Layer 1a's container contents** — R2. What each of the 904 containers holds is a design question this
  doc frames but does not answer.
- **Θ freshness** — the "fresh" half of the spine question. Still open, still not this program.
- **The passive tree for general creatures.** `creature-system-map.md` mentions "the general passive tree"
  as part of a general creature's stats. Whether 2b *is* that tree or is separate from it is a real
  question and is not answered here.

---

## Owner rulings — 2026-09-17

All four open questions ruled. One of them (R-S1) closes `solid-remediation`'s **S7** and therefore
unblocks `empire-progression`'s own first open question.

### R-S1 — a species level grants allocation, like a specimen; the "risk" was the design

**Ruled: option (a), allocation.** And the doc's stated objection to it is retired rather than accepted,
because the owner's reasoning removes its premise:

> *"the advanced of unique unit is equipment system, title system and maybe some special mechanism add
> later (more layer), basically **if unique unit have no equipment, is literally a general unit with same
> level and same stats/passive skill distribution**."*

This question was written with a risk attached — *"it makes a general creature's progression identical in
kind to a specimen's, which weakens the 2a/2b distinction the owner asked for."* **That is not a risk.
It is the intended design, and the question mis-stated what 2a/2b are for.**

**2a and 2b differ in SCOPE, never in KIND.** Both grant the same thing — aptitude-shaped points over the
same share weights, through `SpeciesAllocationSource`. What differs is **whose row owns them**: a
specimen's points are its own (2a), a species' points are the empire's and apply to every general
creature of that species (2b). One creature, one kind of progression, two ownership scopes.

**What actually separates a unique creature from a general one, in the owner's own order:**

1. **Equipment** — the primary and, today, the only shipped differentiator.
2. **Title** — `achievement-title`'s surface.
3. **Later layers** — *"maybe some special mechanism add later (more layer)"*.

Strip equipment from a unique and you have a general creature at the same level with the same stats and
the same passive distribution. **That is the test to apply when someone proposes a fourth difference:**
if it is not a layer above the shared progression, it does not belong.

**This is the cheapest of the three options and now also the correct one** — it reuses
`SpeciesAllocationSource` wholesale and introduces no second progression kind. Option (b)'s bounded
differential and option (c)'s unlocks are not rejected as *future layers*; they are rejected as the
*thing a species level is*.

**What this closes upstream.** `solid-remediation`'s **S7** — *"a plant type at level 4 composes exactly
as one at level 1"* — was blocked on deciding what a species level grants. It grants allocation, and
allocation already composes. `empire-progression-ideal.md`'s first open question (*"Does a species level
feed `Θ`, or a channel, or neither?"*) is answered by the same ruling: it feeds **allocation**, which the
existing fold already reads.

### R-S2 — Zomboss levels from lawn-run play; rubber-banding is a different program

**Ruled**, and in two parts that must not be collapsed into one.

**Part 1 — what ships now.** *"for now, only lawn run can ship, so in lawn run, the zomboss commander
(current is him) will level up by play the game, we already define player win/lose the run, number of
run."*

**Verified — this is already in the power ladder, exactly as the owner recalled** (`ssot-power-scale.md`
§5):

```text
Θ_actor   = Wd·daveLevel    + Wa·realmsAdvanced + Wr·runTerm(pvzRuns)
Θ_content = Wz·zombossLevel + Wm·mapLevel(M)    + Ww·worldTier + Wf·realmsAdvanced
```

| Axis | Status |
|---|---|
| `zombossLevel` | already an axis of `Θ_content` — *"The antagonist ladder — the difficulty side of the contest"* |
| `pvzRuns` | already an **uncapped** axis of `Θ_actor`, weight `Wr` = **250** (0.25), *"~100 lawn runs ≈ one world retirement"* |
| Rule **PS-6** | *"`Wr` is set so that PvZ runs are never the fastest source of `Θ`"* |

So there is **no new curve to invent** — the run term and the antagonist ladder both already exist on the
one power ladder, and PS-6 already bounds the run term so grinding the lawn cannot outpace the other
axes. This program wires Zomboss's commander level to the run outcome; it does not author a scale.

**Part 2 — the "cheat", explicitly deferred to its own program.** *"zomboss play like another empire but
it have some cheat, the cheat should be build in other program to reflect player progression, so when
player become stronger, enemy stronger too, this feature usually use in rpg, but **we are strategy +
rpg, so we avoid to exploit that lazy mechanism, we still use it some case with control**, that need a
individual program."*

Recorded with its reasoning because the reasoning is the load-bearing part: **rubber-banding is
deliberately rationed, not banned.** The objection is that scaling the enemy to the player is the lazy
RPG default, and a strategy game's difficulty should mostly come from *where you chose to go* and *what
you chose to build*. So it stays available, under control, in a program of its own — never as an ambient
rule this program bakes in.

**Both options the question offered are therefore superseded.** Option (a) (credit his zombies' work) is
not ruled out forever, but it is blocked behind **W3** — an ambient vanilla zombie is explicitly not one
of Zomboss's registered units (`MatchHost.cs:322-324`), so there is no row to credit. Option (b)
(a depth clock) is the shape the deferred rubber-band program will argue about, not this one's.

**One asymmetry this ruling does *not* fix, and it stays open elsewhere:** `zombie_spawn` XP still
credits the human's row today. *(Ruled 2026-09-18 by R1: zombie species XP goes to Zomboss's empire, on
**both** paths — the per-placement award and run completion — built by `empire-progression`
`ai-empire-species`. The code still credits the human's row until that module lands; the open question
this paragraph names is closed.)*

> ⚠️ **Corrected 2026-09-18, twice over.** This sentence read *"47,985 `zombie_spawn` awards"*. That is
> a **unit error** — 47,985 was an **XP total**, not a count of awards, as this document's own line 126
> says. And it is no longer the reading: the live store has been reset since 2026-09-16, and
> `rpg_xp_ledger` now holds `zombie_spawn` **26,424 XP over 6,606 rows**, `species_run_complete` 7,500,
> `plant_place` 824 — so the skew is **32×**, not 47×. Line 126 labels its figures honestly as *"a
> reading taken 2026-09-16, not a constant"*; this line restated the same number in the present tense,
> which is how a dated reading turns into a false claim. **The asymmetry itself is unaffected** — the
> ratio moved, the mis-attribution did not. Levelling Zomboss's commander from run outcomes does not retire
that mis-attribution — it is the same shape as the `SR-18` ruling and remains
`empire-progression-ideal.md`'s open question 2.

### R-S3 — 1b and 2b ship together, in one program

**Ruled: both together.** One projector mechanism serving 1a, 1b and 2b, rather than two passes over the
same machinery.

The recommendation in the question was (b), 2b first — on the grounds that the fusion-picks feature being
dark is *"a one-caller bug, not a layer."*

> ⚠️ **Corrected 2026-09-18. This ruling's premise was stale when it was typed, and the correction
> changes the diagnosis, not the ruling.** The text here read *"that remains true and is not overturned:
> `MaterialisePlayerSpecies` losing its only caller is still a small fix, not a program."* It never lost
> a caller. `gk-core/src/FusionRpg.Server/Program.cs:702-722` shipped the production call at **2026-09-17 10:49**
> (`aca8679a`), twelve and a half hours **before** this ruling was written, and its own comment settles
> the history: *"`git log -S` over the whole history shows every call site ever written lives in tests/,
> and the commit that introduced the method introduced no production call at all. It was never wired,
> which is a dark feature rather than a regression."* A never-wired seam is worse than a lost caller,
> because there is no earlier call site to restore — the seam has to be chosen from the spec. The
> packaging ruling below is unaffected; what is void is the reason given for it being safe.

This ruling's **other** premise stands and was re-verified: `player_species` is
`(player_id, species_id, instance_id, materialised_utc, catalog_revision)` and still cannot distinguish a
fusion pick from a debug reforge. What the ruling changes is the **packaging** —
the projector is built once, for all three, instead of being built for 2b and then revisited.

The risk to watch, stated so a spec inherits it rather than discovers it: a single program covering three
layers has the largest review surface of the three options, and 1b's own table needs provenance
(`player_species` cannot currently distinguish a fusion pick from a debug reforge) that 2b does not.
Those are separate acceptance criteria inside one program, not one criterion.

### R-S4 — do not split general and unique progression; build layers above the one hub

**Ruled**, and it is an architecture statement rather than a scope one:

> *"general unit and unique unit basically same, only different is equipment. my design actor hub is all
> in one use, **we don't need to split them, only build new layer above them for each special gameplay
> instead**."*

This is the actor-layer-compose model restated by its author: **one hub, one fold, and special gameplay
arrives as a layer above it — never as a parallel progression object underneath.** It is the same rule
`CLAUDE.md` states as *"One ActorHub compose / one read"* and that `decisions.md` enforces after the
`BattleStatComposer` dual-compose defect.

**So question 4's framing was wrong in both directions.** It asked whether empire species progression
*is* the general passive tree or is *separate from* it. The answer is that there is one progression and
one passive distribution shared by general and unique creatures, and a tree is a **layer over** that, not
a second progression belonging to one class of creature.

**The amendment this owes `creature-system-map.md`:** it describes a general creature's stats as
*"Empire-wide, per-player, per-species progression fallback (primary stats, the general passive tree)"*.
The phrase reads as though general creatures have their own progression *object* with a tree bolted
inside it. Per R-S1 and R-S4 they do not — they share the progression and differ by equipment. That
sentence needs correcting, and no general-creature tree binding exists in code to justify the current
reading.

---

## What a downstream session must not do

- Do not let 2b read 1a's composed value to compute its own. That is a second composer.
- Do not write a species level into a primary channel (`resource.max.hp`, attack). Progression flats use
  `progression.bonus.*`.
- Do not invent an `f(speciesLevel)` curve. Magnitudes read `P(Θ)`; contests read `Θ`.
- Do not give a Bound unique the empire species fallback. It is banned by `decisions.md`'s ownership row,
  already pinned by a test, and already leaking once (W5).
- Do not cap a species level without a verdict in `ssot-power-scale.md` §11.
- Do not add a PvZ field, and do not conclude the lawn "cannot support" a species stat. It resolves in the
  RPG layer.

---

## Hand-off

Next step is `/spec` — a capability map at `docs/architecture/species-progression-map.md`, then module
specs under `docs/architecture/species-progression/`, once open questions 1–4 are answered. **This doc is
where the idea phase stops:** no spec, no plan, no code here.

---

## ⏸️ Deferred sub-program: species level-up grants (owner, 2026-09-17)

**Status: TRACKED AND DEFERRED. Not built, not specced, no build authorized.** The owner's words:
*"The build is complete so we need a sub program later, track it and defer."* This section exists so the
requirement is not re-derived, and so `solid-remediation`'s **S7** has somewhere to land.

### Why this is recorded here rather than anywhere else

`solid-remediation` T4.4 proved that S7 — *"a plant type at level 4 composes exactly as one at level 1"* —
**cannot be closed by wiring**. `AptitudeResolver` reads `allocation.Share(edge.Source)`, a **share**, not
a point count, and the magnitude comes from `pTheta = ladder.Value(theta)` where theta is the **member's**
level, never the species level. So routing the species allocation into the compose (which T4.4 did, closing
S2) leaves S7 untouched. Closing S7 requires deciding **what a species level grants** — which is exactly
what the owner has now described. S7 is that decision's first consumer.

### What the owner specified

1. **Species level-up mirrors unique-actor level-up.** A species level grants the **12 primary stats**
   (the aptitude roster), **auto-assigned** — not player-allocated — from two inputs:
   - the **species favour**, and
   - the **species build preset**.

2. **Seedsmith's deterministic engine is extended** to resolve the **primary-stat distribution matrix**
   for a build favour. Deterministic resolution, the same discipline the existing generators use — seed
   in, matrix out, no model call.

3. **A species level also unlocks actions and passive points.** Named explicitly:
   - a **signature action**,
   - a **family action**,
   - **passive skill points**, assigned onto a **family/species tree** *or* a **build-favour tree**,
   - and those trees include an **element tree** and a **status tree**.

### What this deliberately does not decide

Nothing about magnitudes, curves, per-level point counts, matrix weights, tree shapes, or how a build
favour is authored. The owner described the **shape**; the numbers and the tree topology are that
sub-program's own work, and inventing them here would be the "balance decision with no design input" this
repo's tunables rule exists to prevent.

### Constraints it already inherits (so they are not re-litigated)

- **One power ladder.** Anything level-derived reads `Θ` / `P(Θ)` — a private `f(level)` is the defect that
  let three incompatible curves ship (`ssot-power-scale.md` §10 is a closed inventory).
- **Every number is a tunable**, in `gk-core/data/tuning/<domain>.v{n}.json`, with its unit in its name.
- **One ActorHub compose.** A species term contributes through `IActorStatSubsystem` / a registered atom
  reader with a GG-49 `ContributionSourceIds` grammar id — never a private fold. T4.6 already established
  the seam: `species-passive:{speciesId}`.
- **Closed vocabularies stay closed.** 12 aptitudes, 6 elements, 3 status categories — pin the count, and
  a change is a reviewed change.
- **Seedsmith emits seeds; the runtime generates concretes.** The distribution matrix is seed-side; a
  player's realised allocation is runtime-side.


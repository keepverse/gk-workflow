# `actor-layer-compose` — the ideal

**Status:** idea phase, 2026-09-16. Not a spec. No build authorized.
**Supersedes:** [`species-hub-wire-ideal.md`](species-hub-wire-ideal.md) — same findings, wrong frame. That
doc treated the species seed as a feature to wire. It is one layer of one compose, and the compose is the
subject.
**Sibling of:** [`actor-hub-and-combat-power-solid-fixing`](actor-hub-and-combat-power-solid-fixing-map.md)
— this idea is that program's unfinished half, restated as layers rather than as defects.

---

## Step 0 — the principles, in my own words, before anything else

1. **Every RPG feature lives in the RPG layer, and is never built by changing what PvZ is.** An actor's
   numbers are composed on our side. PvZ receives a signed delta for the two or three fields it actually
   has, and is never asked to hold an RPG concept.
2. **One `ActorHub` compose, one read.** Lawn, sheet, battle, delve, siege and sim contribute through
   `IActorStatSubsystem` / registered atom readers, or consume Hub output. Anything else that decides the
   same number is a second compose — and dual compose was an ADR defect, overturned 2026-09-12 and
   deleted 2026-09-13. **A second decision site is the defect whatever language it is written in**,
   including a Unity field.
3. **Two async systems, deltas not absolutes, record-then-drain.** Delay is the designed degradation.
4. **One power ladder.** Contests read `Θ`; magnitudes read `P(Θ)`. `ssot-power-scale.md` §10 is closed —
   a new `f(level)` is the defect it exists to end.
5. **The balance surface is data** (`gk-core/data/tuning/<domain>.v{n}.json`, published as `v{n+1}`), never a
   `const`.
6. **No hard progression ceilings.** Caps are soft and configurable; absolute bounds throw.
7. **Gameless-first is capability.** Every layer here composes with Fusion closed; the injector enriches
   a fielded actor, never gates the bookkeeping.
8. **Generated seed data is never hand-edited** — fix the generator and regenerate.
9. **A guardrail validates the contract and the closed enums, never a population count.** "904 species"
   is a reading.

**DESIGN-GATE §1 rows read this session:** Product vision (`the-game.md`, `the-loops.md`) · Stats
(`actor-hub-ssot.md`, `combat-power-number-ideal.md`) · Power ladder · Creature species generation
(`creature-seed-map.md`) · General vs unique creature (`creature-scope-ideal.md`) · Resources · Effect
pipeline / containers · Live-probe standard · plus `deployment-hierarchy-ideal.md` in the
`empire-development` worktree. **Box I cannot tick:** I have not read `effect-pipeline-ideal.md` §5 in
full this session — only the container/validator code it governs. Anything below about how a container
*rolls* is therefore code-verified, not spec-verified.

---

## Which loop this extends

[`the-loops.md`](../guide/the-loops.md) **Spine A — Level up and power**, whose status line already reads
*"species builds and meters WIP"*, and whose promise is the subject of this doc:

> *"Dave's level is the main line. **Specimens, species, and types also level from work they did.**"*

Also **Place — Lawn** (a Bound or general actor must feed the same compose as the sheet) and **Place —
Sanctum / ActorSheet** (the number shown must be the number composed). No new loop.

---

## What this is

**The ultimate purpose of the program this belongs to:** *one `ActorHub` composes every actor's combat
numbers once, for every mode, from every contributing layer — and the result is honest enough to answer
the player's question "how strong is this creature?"*

That question's answer is the **combat power number**: a matrix price over ~196 combat-affecting derived
channels. Not specimen level. Not `Θ`. Not `combat.power.omni` alone. An actor with 100,000 evasion and
100 omni attack is still very strong, and magic-find never raises the number.

**What this idea adds:** the compose is fed by a **stack of layers**, each an atom effect container bound
to the actor, and today **two of the layers do not arrive at all** while a third arrived twice. Stated as
the owner stated it:

> *"Specie seed carry base species stats, this is first derived stats container (atom effect container).
> The progression is second derived stats container. Item equipment, passive tree, title system, aura,
> buff, and more. They are multiple layer and sum together. So when a actor deploy, they need to resolve
> in actor hub."*

### The one precision that keeps this from forking the composer

**A layer is a source of contributions. It is never a stacking tier.**

The fold is already defined per *channel*, not per layer: `DerivedStatDef.Compose` picks `FlatSum`,
`FlatReplace`, `SumIncreased` or `MaxPriorityFlag`, and modifiers carry `Flat` / `Increased` / `Replace` /
`Flag` (`DerivedComposer.cs:38-48`, `DerivedModifier.cs:10-16`). So "layers sum together" means *every
layer emits `DerivedModifier`s into the same fold* — **not** that layer 2 multiplies layer 1. Giving a
layer its own stacking rule would be a second composer wearing a new word, which is the exact defect this
program exists to end.

---

## What already exists

### Built

| What | Where | What proves it |
|---|---|---|
| The one compose, op-aware, per channel | `DerivedComposer.cs:38-48`; `ActorHub.ResolveDerived` | Four compose kinds, four ops; `guard-actor-hub.py` green |
| Layer 3 — item equipment | `equip-assign` bindings → `EquippedBoundAtoms.cs:47` | Live: equip → `atoms-preview` 1 accepted, 0 refused → grant pushed to the bound ptr |
| Layer 4 — passive tree | `TreeBoundAtomsCache.For` via `CheatState.cs:66-69` | Registered on the injector Hub beside the grant reader |
| Layer 6 — aura / patron | `patron.aura` container | Shipped; applies from the next match by design |
| Layer 7 — buff / status | `StatusDerivedMods.For` via `CheatState.cs:74` | The registration that makes a status's `stat.combat.*` reach the composed value |
| The layer-1 **binder** | `RpgStore.UniqueActors.cs:1588` `ReconcileCreatureMagnitudeBindingsUnlocked` | Complete: binds at every deploy to `OwnerKind.UniqueActor`, withdraws stale, revision-aware, fails closed, double-grant invariant |
| The species corpus behind layer 1 | `SpeciesExpander`, `RpgStore.Species.cs:156` | **904** species, **11,724** rows in `creature_species_magnitude` |
| Species XP, both sides, both terms | `RpgXpAwardMap.cs:92`, `RpgStore.Progression.cs:79` | Live: `{zombie_spawn: 47985, species_run_complete: 8484, plant_place: 1030}` |
| The deployment tree that decides when layers resolve | `deployment-hierarchy-ideal.md` (empire-development worktree) | parent → child, snapshot inherit, exactly-once settle, *"no child invents a composer"* |

### Wiring gap

**L1 — layer 1 never arrives. The container the binder looks for does not exist, for any species.**
`SpeciesMagnitudeContainerId` (`RpgStore.UniqueActors.cs:1569`) returns
`trait.species-magnitude-{speciesId}`; the store holds **0** such containers, `gk-data/packs/fusion/data/seed/**` mentions the
id **0** times, and `effect_binding` carries **0** rows with source `creature-magnitude` (live sources:
`debug`, `demon-trait`, `derived-audit`, `equip-assign`). The binder has never fired. **Inert content, not
an architectural limit.**

**L2 — layers 2a and 2b are not container-shaped.** Progression reaches the compose as aptitude
*allocation math* through `AptitudeSubsystem`, not as a bound container. It works — a plain zombie carried
`aptitude.Ferocity:Flat:80` live — but it is the one layer outside the model, and the model is what makes
the others inspectable, revisable and bindable.

*Not* a gap, and worth saying so plainly: **the 2a/2b split the owner ruled on 2026-09-16 is already
correct in code.** `SpeciesAllocationSource.Resolve` returns early on the unique branch (`:98-103`) or
falls to the species branch (`:105-117`), never both, and
`SpeciesAllocationSourceTests.Bound_unique_sharing_a_species_id_with_a_general_never_inherits_empire_shares`
pins all four cells. Only the carrier question is open.

**L3 — the layer-1 carrier was pointed at the wrong namespace, and the alternative is stale.**
`species-passive.{speciesId}` exists as a validated container kind with 3 authored pilot entries and a
per-player materialiser (`SpeciesMaterialiser.cs:51`) — built for an idea the owner has now withdrawn
(*"my first idea is make species random stats each game but i wrong"*). Measured: **nothing binds a
`player_species` instance to any actor**; its only readers are fusion's own already-materialised guard
(`RpgStore.Fusion.cs:237`) and fusion's picks write (`:311-369`). So a player's **fusion picks are
recorded and never reach a stat.**

**L4 — a second decision site for the same number existed in PvZ's own memory.**
`EntityStatWriter` assigned the composed `y.Atk` into `p.attackDamage` / `z.theAttackDamage`. That is a
second place the actor's damage was decided, outside the compose — the dual-compose defect expressed in a
Unity field. **Fixed 2026-09-16** (owner ruling; both writes commented out with the reason inline). It is
listed here because it is the clearest example of what this idea is about, and because the rest of the
writer still has the same shape: 12 plant and 11 zombie fields are still assigned as composed absolutes
(`EntityStatWriter.cs:88-122`, `:143-162`) where the ruling is a **delta** over `hp`/`armor1`/`armor2`.

**L5 — the compose reads stale inputs.** `Θ` never moves after the injector connects (live: server
`theta 7`, injector `theta 1`); a player switch never reaches the injector (`ctxPlayerId 1` while the
server said 6); a post-deploy unique allocation does not reach a Bound entity. *(The commander half of
that last one is **by design** — `MatchCommanderSnapshotHolder.ResolveAllocation` freezes the commander
build for the match.)*

**L6 — the compose is too expensive to run, which is what tempts every shortcut.**
`ActorHub.ResolveDerived` is documented *"fresh per call in v1"* (`ActorHub.cs:52`) and the lawn rider
calls it per hit: **286 calls, 464 ms, avg 1624 µs** in one 4 s window at 300 zombies.

**L7 — the compose's output does not reach combat.** The lawn rider ships defaulted off
(`LawnBasicAttackFeature.DefaultEnabled = false`) because it costs 26.7–37% of the pipeline against a 6%
ceiling. So today the composed numbers change almost nothing a player feels.

### Real gap

**R1 — no generator stage emits layer-1 containers.** The generator writes magnitudes into
`gk-data/packs/fusion/data/generated/creatures/*.json`; the importer writes them into `creature_species_magnitude`; nothing
projects them into atom containers. That middle step has never existed.

**R2 — the layer-1 corpus is a projection nobody has decided the shape of.** 904 containers derived from
data already committed — deterministic, shared, regenerable. What each one *contains* (which channels, at
what op) is unwritten.

**R3 — plant/zombie type progression reaches no layer.** `RpgProgressionSubsystem.ContributeDerived`
(`RpgProgressionSubsystem.cs:43-54`) adds exactly `progression.power` (Θ, from Dave's level) and a
`progression.realm` stub. Nothing under `Core/Stats/**` or the injector reads a `rpg_actor_progression`
row of kind `plant`/`zombie`; the only consumers are display summaries. A plant type at level 4 composes
exactly as one at level 1.

**R4 — the species bake cannot yet carry identity even once layer 1 binds.** Owned by
`lawn-tuning-profile`'s `species-flavour-lawn`; named here because layer 1 binding a constant is a
successful wire around an empty pipe.

> **Re-measured 2026-09-17 — two of this finding's original numbers are stale, and the corpus has been
> regenerated since they were taken.** They are corrected in place rather than deleted, because a
> downstream session sizing a fix needs the current scale, not the one this finding was written against.
>
> | As originally written | Measured 2026-09-17, all 904 files in `gk-data/packs/fusion/data/generated/creatures/` |
> |---|---|
> | 730 share `theta 13` | **Stale.** `theta 13` holds **81**. All ten threat rungs are occupied; nine sit in a 55–101 band, and the largest is `theta 0` at **224 (24.8%)** |
> | 450 share `resource.max.hp 2712` | **Stale.** `2712` holds **44**. **88 distinct** hp values; the most common is 480 at 159 species |
> | only 457 (50%) carry `combat.power.omni` | **Still exactly true — 457 of 904** |
> | Peashooter and GatlingPea bake identically | **Still true** — identical `magnitudes` and `pTheta 452`; they differ only in `attackIntervalMs` and `elementSecondary` |
>
> **The finding stands, at a smaller scale.** The bake is no longer near-constant — **189 distinct
> magnitude vectors** across 904 species, the largest shared by 70 — but it still does not separate two
> plants that should obviously differ, which is what R4 claims. Size the fix against these numbers.

---

## Every open finding, re-cut as one question

*"Does the one compose have all its layers — present, fresh, affordable, and reaching combat?"*

| Finding | Which part of the question |
|---|---|
| Species base 0 of 904 containers (L1, R1, R2) | **Present** — a layer that never binds |
| Progression is allocation math, not a container (L2) | **Present** — a layer outside the model |
| Type level feeds nothing (R3) | **Present** — XP that reaches no layer |
| `attackDamage` write *(fixed)* | **Present** — a *second* place the number was decided |
| hp/armour still absolute (12+11 fields) | **Present** — the same shape, not yet corrected |
| Θ frozen · player switch · post-deploy allocation (L5) | **Fresh** — the compose reading stale inputs |
| `hub.resolveDerived` 1624 µs (L6) | **Affordable** — the one compose too expensive to run |
| `effect.onCapture` 4214 µs, drain carried 5320 (L6) | **Affordable** |
| Rider defaulted off (L7) | **Reaching combat** |
| Species XP 47× zombie-skewed | **Present, but pointed at the enemy** — the layer arrives for the wrong side |
| Species bake is a constant (R4) | **Present, but empty** — the layer would carry nothing |

Eleven findings, one spine. Not eleven programs.

---

## Prior art, with numbers

**Path of Exile** is the closest shipped system to "many layers, one fold", and this repo already borrowed
its vocabulary — `Flat` / `Increased` map to PoE's *added* / *increased*:

- PoE folds **flat** first, then sums all **increased/reduced** into one multiplier, then applies each
  **more/less** multiplicatively in turn. The canonical worked example: `(50 base + 10 flat + 0.2 × 50
  increased) × 1.1 more = 77`.
- The rule that matters for us: **the stacking behaviour belongs to the stat and the modifier word, not to
  where the modifier came from.** A ring, a passive and a buff granting *increased* all land in the same
  sum. That is exactly "a layer is a source, not a tier".

**Documented failure modes worth pricing in now:**

- **Percent stacking ambiguity.** Two sources of 30% and 20% resist are either 50% (additive) or 56%
  damage taken (multiplicative) — genuinely different games. Every percent-resist system has to pick, and
  ours should state it per channel rather than per layer.
- **The hard-ceiling problem.** Percent resists that can reach 100% stop damage entirely and break
  encounters; shipped games cap at **75–80%**. Our no-hard-ceilings rule exempts bounded ratios — this is
  exactly that case, and the cap must be a stated, tunable soft cap rather than an accident.
- **Additive dilution.** Going from +500% to +550% barely moves output, so the more a player stacks one
  category the less each upgrade feels — the reason a layer stack needs *different* categories, not more
  of the same one.

**Pokémon** for the base-vs-earned split, which is what layers 1 and 2 are: a stat is
`((2 × Base + IV + EV/4) × Level / 100 + 5) × Nature`. **Base is species identity — not earned, not
grindable.** The earned layers are hard-bounded (IV 0–31; EV ≤252 per stat and ≤510 total, 4 EV = +1 at
L100) and Nature, the whole flavour multiplier, is **±10%**. Ours has no bound on species level today,
which is what makes the 47× faucet skew compound instead of converge.

Sources: [PoE Wiki — Stat](https://pathofexile.fandom.com/wiki/Stat) ·
[Toolhub — RPG damage formulas](https://toolhub.software/articles/rpg-damage-formulas/) ·
[meredoth/Stat-System](https://github.com/meredoth/Stat-System) ·
[Bulbapedia — Effort values](https://bulbapedia.bulbagarden.net/wiki/Effort_values) ·
[Smogon — EVs and IVs Through the Ages](https://www.smogon.com/smog/issue28/evs_ivs)

---

## The shape

### The layer stack

| # | Layer | Carrier | Scope | State |
|---|---|---|---|---|
| 1a | **Base species** — the race | `species-passive.{speciesId}` *(owner ruling: reuse this id)* | global, shared, **frozen**; a player action never rewrites it | 0 authored |
| 1b | **Player-modified species** | ⛔ **a new table** — see the 1a/1b split below | per `(player, species)`, written only when a mechanism modifies it; most players have none | fusion picks write into the shared container today, which is the leak |
| 2a | **Specimen progression** | a per-specimen container, re-projected on level-up | one unique specimen, earned by that individual | allocation math today; **ruled to become a container** |
| 2b | **Empire species progression** | a per-`(empire, species)` container, re-projected on level-up | per **owning empire** per species, applied to general actors: plants read the player's, zombies read Zomboss's (`players` id 3) | allocation math today, and credited to the wrong empire |
| 3 | Item equipment | `equip-assign` → `EquippedBoundAtoms` | per actor | works |
| 4 | Passive tree | `TreeBoundAtomsCache` | per player | works |
| 5a | Actor title | `actor-title.{id}` container | one actor | **in build** in `achievement-title`; carrier already added |
| 5b | Empire title | `empire-title.{id}` container | **every actor of that empire** | **in build**; the first empire-scope layer in the model |
| 6 | Aura / patron | `patron.aura` | per side per match | works |
| 7 | Buff / status | `StatusDerivedMods` | per actor, live | works |

All contribute `DerivedModifier`s into the one fold. The channel's own `DerivedComposeKind` decides how
they combine — **no layer carries its own stacking rule.**

#### Layer 1 is the species definition — the race, not a buff (owner ruling 2026-09-16)

> *"Make it become layer 1 — this is layer where specie define, they base stats before any progression
> (same as race system in some rpg like skyrim)."*

Layer 1 answers **"what is this creature, before anything happened to it?"** It is the species' own base
stats, applied before any progression, identical for every actor of that species — exactly what a race
does in an Elder Scrolls game.

**The prior art is precise and worth borrowing whole.** In Skyrim every race starts from the *same* pool
— **360 points across Health / Magicka / Stamina**, every skill at a base of **15** — and the race adds a
small, fixed, legible differential on top: **+10 to one skill, +5 to five others**, a racial perk (High
Elf **+50 maximum Magicka**, Breton **+25% magic resist**) and one power. A High Elf's Archery starts at
15, not at some separate elven number. **The race is a differential over a shared base, not a separate
stat block** — and it never changes again for the rest of the game.

That is the shape layer 1 should take here, and it settles a question the seed's own numbers would
otherwise force: the species bake carries `resource.max.hp 2712` for a Peashooter against a vanilla 300.
Read as an absolute stat block, that is a contradiction to resolve. Read as a **race differential**, it is
simply the wrong unit for the job — layer 1 contributes *how this species differs*, and the shared base
stays the shared base.

**Fusion picks are how a player defines a new race** — owner ruling, closing open question 3.

And the repoint is almost nothing, because the code already points at the right container. A
`FusionPick(SourceInstanceId, AtomId)` inherits one rolled atom from one sacrifice into the output
species, slot-capped by the output's rarity (`FusionRoller.SlotsFor`), honoured only on the first fusion
of that species — and it writes into **`GetContainer("species-passive." + output.SpeciesId)`**
(`RpgStore.Fusion.cs:243`), which is the very container layer 1 now uses. Nothing has to be re-aimed.
What changes is the container's *meaning* and its *lifecycle*:

| | Before | After |
|---|---|---|
| What the container is | a per-player roll, materialised into `player_species` | the **species' definition** — its race |
| Who reads it | nothing binds a `player_species` instance to any actor | the layer-1 binder, at every deploy |
| What a fusion pick means | a choice recorded in a roll nobody reads | **the player authoring their own race** |

So the pick stops being an orphan and becomes the most interesting thing on the page: a fused species is
a race the player made, and the atoms they chose are what that race *is*.

⚠️ **This hazard was answered the same day by the 1a/1b split below — read that section, not the three
options here, which are kept only as the reasoning that produced the split.** A fused species id
is **global** — `output.SpeciesId` comes from the recipe, and only the *roll* was ever per-player
(`WorldSeed.DeriveRollSeed(player.WorldSeed, "species", output.SpeciesId)`, `RpgStore.Fusion.cs:322`).
The materialise-once guard is per player (`:237`) but the container is not. With the roll retired and
layer 1 shared, **player A's picks would define the species for player B.** Three ways out, and this is
an owner call, not an implementation detail:

- **(a) First fuser names the race.** Global, dramatic, and almost certainly wrong for a single-player
  game with multiple save slots.
- **(b) A fused species id becomes player-scoped** — each player's fusion creates their own race.
  **Recommended:** it is the only reading where "the player defines a race" survives contact with a
  second player, and it matches the fiction (your lab made this thing).
- **(c) Picks stop defining the species and attach to the specimen instead** — but that contradicts the
  ruling above, and puts a player's authored choice back into a layer that the specimen's own progression
  already owns.

#### Layer 1 splits: base species (shared, frozen) and player-modified species (per player, delayed)

Owner refinement 2026-09-16, and it dissolves the hazard above rather than choosing between its three
bad options:

> *"Don't make roll gone but delay it, the first seed will not change, we need new table to store player
> roll by fusion and some other mechanism layer, that explicit boundary between base species and player
> modified species."*

| | **1a — base species** | **1b — player-modified species** |
|---|---|---|
| What it is | what the species *is*, from the seed | what **this player's** version of it became |
| Scope | global, shared by every player | per `(player, species)` |
| Lifetime | **frozen** — a player action never rewrites it | append-only, grows as the player plays |
| Written by | the generator, and only the generator | a real mechanism: fusion picks today, others later |
| Storage | the `species-passive.{speciesId}` container | **a new table** — `player_species` is not it (see below) |
| Default | every species has one | **most players have none, for most species** |

**This is the repo's own `seed → concrete` law, applied to a species instead of an item.** The container
is the seed — authored, deterministic, diffable, shared. The player's modification row is the concrete —
per player, produced by a real in-game event. The owner chose that architecture for creatures already
(`creature-seed-map.md` §1: *"Seedsmith generate seed, rpg server generate concrete version that use in
game, same as item seed and concrete item principle"*). Layer 1 is where it lands for base stats.

**"Delay the roll" is the load-bearing word.** Today `SpeciesMaterialiser` rolls **every** species for a
player eagerly, at first contact, into `player_species` — which is why 3 rows exist for player 1 and why
they are stale at `catalog_revision 8`. Under this refinement nothing is rolled until a mechanism
actually modifies that species for that player. A player who has never fused composes **1a alone**, with
no row anywhere, and that is the normal case rather than an empty-state to handle.

**The hazard from the previous section is gone, and no species id has to become player-scoped.** The
shared container stays shared and stays the recipe's; player A's picks live in player A's rows. The three
options I listed last turn — first-fuser-names-the-race, player-scoped ids, or picks-on-the-specimen —
were all answers to a problem this split does not have.

⚠️ **This corrects what I recorded one turn earlier.** I wrote that fusion picks "already write into the
right container", because `RpgStore.Fusion.cs:243` targets `GetContainer("species-passive." +
output.SpeciesId)`. Under this model that is the **wrong** target: writing a player's picks into the
shared container is precisely the cross-player leak. The repoint is real work, not a no-op — picks move
from the shared container into the new per-player table.

**What the new table has to carry** (shape, not schema — a spec decides the columns):

1. `(playerId, speciesId)` as the key, append-only, so a second mechanism never overwrites the first.
2. **Provenance per row** — which mechanism added it (`fusion-pick` today), and its correlation, so a
   modification can be explained, audited and if necessary withdrawn. The repo already refuses
   progression sources that cannot name themselves (`CreatureProgressionSource`, the `creature.
   progression.v1` grammar); this is the same discipline one layer over.
3. **The atom payload**, in the same shape the container carries, so layer 1a and 1b fold identically —
   one binder, two sources, no second code path.
4. `catalogRevision`, for the same reason every other rolled row carries it.

**What this retires:** `SpeciesMaterialiser`'s eager per-player roll and the `player_species` table it
writes. Not the *concept* of a player-modified species — that is being promoted, not deleted — only the
eager materialisation of every species for every player, which produced rows nothing reads.

**What layer 1 composes, after the split:**

```text
layer 1a  species-passive.{speciesId}        shared, frozen, every actor of that species
    +
layer 1b  player-species-mod (playerId, speciesId)   only if this player modified it
    =
"what this creature is, before anything happened to it"
```

Both bind through the same binder at deploy; both emit `DerivedModifier`s into the same fold. **A layer
is a source, not a stacking tier** — that rule holds across the 1a/1b split too.

#### Layers 2a and 2b are mutually exclusive per actor — owner ruling 2026-09-16

> *"Make them individually, specimen level up by themselves, empire species level up general actor."*

A **unique specimen** carries **2a only**: it levels by its own work, and it never inherits what the
player's empire taught that species. A **general actor** carries **2b only**: it is rank-and-file, and
what it knows is what the empire knows. An actor never carries both.

**This is already shipped and already pinned**, which is the cheapest possible state for a ruling to be
in. `SpeciesAllocationSource.Resolve` takes the unique branch at `:98-103` and returns early, or falls to
the species branch at `:105-117` — never both. The regression test is
`SpeciesAllocationSourceTests.Bound_unique_sharing_a_species_id_with_a_general_never_inherits_empire_shares`,
which asserts all four cells: a Bound unique reads `UniqueCreature 10` / `CreatureType 0`, and a general
at the same `(Side, TypeId)` reads `CreatureType 999` / `UniqueCreature 0`.

So the ruling costs nothing to honour and the model gains a real property:

| | Layer 1 species base | Layer 2a specimen | Layer 2b empire species |
|---|---|---|---|
| Unique specimen | ✅ what the species **is** | ✅ what **this individual** earned | ❌ never |
| General actor | ✅ what the species **is** | ❌ never | ✅ what the **empire** taught it |

Which is a clean reading of the fiction as well as the code: a named demon grows through its own deeds; a
legion of the same species grows because the empire trained the species, not the soldier.

⚠️ **One consequence to carry forward:** a unique specimen therefore gets its species identity from
**layer 1 alone**. That makes layer 1 the only thing distinguishing a freshly summoned Peashooter from a
freshly summoned BigGloom — and layer 1 is the layer that currently binds nothing (L1). The ruling raises
layer 1 from "missing content" to "the only species identity a unique has".

#### Layer 2b belongs to the OWNING empire — owner ruling 2026-09-16

> *"Zombie in zomboss empire, we need build up zomboss empire specie progression."*

The model is symmetric. **Each side has an empire, and each empire levels its own species.** A plant on
the lawn is the player's; a zombie is Zomboss's. So layer 2b resolves against *the empire that owns the
species*, never against "whoever is watching".

| Actor | Layer 2b reads |
|---|---|
| Lawn plant (general) | the **player's** empire species progression |
| Lawn zombie (general) | **Zomboss's** empire species progression |
| Any unique specimen | nothing — 2a only |

**This closes a question that was open between two programs**, and it closes it better than either
answer on offer. `lawn-tuning-profile` ruling 1 had lawn zombies carrying *Zomboss's commander build* at
`Θ_player + offset`; this doc had them carrying *the player's* empire species progression. The right
answer is neither: they carry **Zomboss's empire species progression**, which is the same layer the
player's plants use, read from the other empire. Zomboss's *commander* build stays what it is — a
commander aura, layer 6, orthogonal to this.

**And it reframes the 47× skew from a tuning problem into an ownership bug.** Measured across the whole
store, species XP by reason is `{zombie_spawn: 47,985, species_run_complete: 8,484, plant_place: 1,030}`,
and the zombie half of it is **credited to the human player's own rows**: player 1 holds `normalzombie`
at **level 52**, player 6 at 15, player 7 at 6. The player is levelling Zomboss's species on their own
sheet. Once every zombie award lands on Zomboss's empire instead, a player's species rows contain only
plant species — and the 47× ratio stops existing rather than being capped. **A cap would have been
treating the symptom.**

**The carrier already exists, with zero schema change.** `players` row **id 3, name `Zomboss`**, created
2026-09-06 — the dedicated row `demon-lawn-deploy` Phase 3 introduced. `rpg_actor_progression` is keyed
by `player_id`, so Zomboss's empire species progression is the same table, the same shape and the same
code path as the player's, under a different id. Today player 3 holds **zero** progression rows of any
kind: his empire has never earned anything.

What this needs, stated as the shape and not as a plan:

1. **The award's owner is resolved from the species' side, not from the current player.** A
   `ZombieSpawned` fact credits Zomboss's empire; a `PlantPlaced` fact credits the player's. The
   `EmpireGeneral` provenance claim already carries the species id (`EntityApply.cs:289` stamps
   `general:{speciesId}`) — the side is one lookup away through `LawnElementIndex`.
2. **Zomboss's empire needs its own point budget and its own allocation**, read at
   `AllocationScope.CreatureType` keyed by `(player 3, speciesId)` — the identical mechanism, no new
   scope.
3. **A zombie actor's layer 2b resolves against player 3**, not against `ctx.PlayerId`.
   `SpeciesAllocationSource.Resolve` currently resolves commander and species against the watching
   player; the species half must resolve against the owning empire instead.

⚠️ **Two things this must not become.** It is not a new `AllocationScope` — `CreatureType` already means
"per-empire, per-species". And it is not a second progression engine: Zomboss's empire levels through
the *same* `RpgXpAwardMap` and the *same* `rpg_actor_progression` rows, or it is a fork by another name.

⚠️ **One open consequence worth stating rather than deciding here:** if Zomboss's empire levels from
every zombie the game spawns, his species grow on a clock the player does not control — which is the
same unbounded faucet, pointed at the enemy on purpose. Whether that is *difficulty that scales with how
long you play* or an escalation nobody asked for is a balance question, and it is the first question
`zombie-power-source` should answer now that it has a real progression to scale.

### Where the layers resolve — the deployment scope

From `deployment-hierarchy-ideal.md` (empire-development worktree), which already settles this:

- **parent** = where a force lives (home roster · legion in a sector · garrison · delve party ·
  expedition muster). **child** = where it deploys (lawn Bound · siege combatant · delve slot ·
  expedition seat).
- A child **inherits a snapshot** at deploy: the six pool values, status *specs* (re-applied at the
  child's first tick, never pre-applied), and sticky flags (`Downed`/`DownedOnce`, `NerveStacks`,
  `Wounds`, phase — `Roster` required; `ActiveBound`/`Recovering` refuse).
- **Does not cross:** live `StatusRuntime` instances, Unity `ptr`s (rebound per child), the match-scoped
  sun bank, the three stocks.
- **Settle** is exactly-once per `(parentId, childId)` — lawn die / board end writes `ActiveBound →
  Roster` plus XP and wounds, the path `lawn-combat-wire` L-N40 repaired.
- Its binding rule, verbatim: *"Every combat read goes through ActorHub. Children contribute … or consume
  Hub output. **No child invents a composer.**"*

**So a general spawn and a unique specimen resolve identically** — same Hub, same stack. They differ only
in which parent they deploy from and which container fills layer 2. Troops stay troop-stack counts and
never become N `UniqueActor` rows.

### Where the numbers stop

```text
RPG layer — layers 1..7 compose once in ActorHub, and RPG combat reads the result
        |
        |  a DELTA, for the fields PvZ actually has
        v
PvZ — hp · armor1 · armor2, otherwise untouched
```

Everything PvZ has no field for — crit, dodge, elements, stamina, resistances, the rest of the ~261
registered channels — never crosses. That is the boundary working, not a lawn limitation. The attack
write is already gone; the remaining absolutes are the rest of the same correction.

### Layer 1's own shape, and why reuse beats a new id

Reuse `species-passive.{speciesId}` and keep the binder:

1. It is the correctly-named kind (`ContainerKind.SpeciesPassive`, a validated prefix in
   `ContainerValidator.cs:28`). The current `trait.species-magnitude-{id}` squats in the **trait**
   namespace, which a *sibling* reconciler already owns for a species' real `TraitIds`.
2. `ReconcileCreatureMagnitudeBindingsUnlocked` stays untouched — repointing is one line in
   `SpeciesMagnitudeContainerId`.
3. Author the 904 containers from the generator (R1) — deterministic and shared.
4. Retire `SpeciesMaterialiser`, `player_species`, and the fusion picks write. ⚠️ Fusion picks are a
   shipped, player-facing choice; retiring the table silently deletes the only record of them. This is a
   named dependency, not a footnote.

---

## Tunables

| Number | File | Today |
|---|---|---|
| `awards.placement` / `awards.runCompletion` | `gk-core/data/tuning/species-progression.v1.json` | 4 / 100 |
| a per-run placement cap (new) | same, `v2` | — |
| any per-mode layer scale | `mode-profiles.v{n}.json` (`lawn-tuning-profile`) | — |
| any bounded-ratio soft cap (the 75–80% lesson) | the channel's own `DerivedStatDef` cap, stated | per channel |

No per-species number is ever authored in `gk-core/data/tuning` — species identity lives in the species seed
(owner ruling 2026-09-16).

---

## What this deliberately does not decide

- **Balance.** Every number here is a faucet rate, a budget or a scale.
- **The species bake's quality** (R4) — `lawn-tuning-profile`'s `species-flavour-lawn` owns the generator
  defect.
- **The perf chain** (L6) and **the switch flip** (L7) — `lawn-playable` owns both, and they are
  independent of whether the layers exist.
- **The `species-build` program's ten modules.** ⚠️ Its map still says *"no build authorized"* while
  module 6's transport is demonstrably shipped and registered at `CheatState.cs:55` — that staleness
  should be corrected wherever it is next read.
- **World / siege / delve layer sources.** The stack is the same everywhere; this idea does not spec
  their parents.

---

#### Layer 5 is in build in another program, and it has to merge here — owner, 2026-09-16

> *"Layer 5 in build need another program to merge with us."*

Checked on `worktree-achievement-title-20260915-7f3a` before recording, and the news is better than
"a planned layer": **the title program has already built the carrier, and it built two of them.**
`ContainerRow.cs` adds `ContainerKind.EmpireTitle` and `ContainerKind.ActorTitle`, and
`ContainerValidator.cs:29` already accepts `empire-title.*` and `actor-title.*` alongside the nine kinds
this model's other layers use. So layer 5 arrives container-shaped, through the same carrier as layers 1,
3, 4 and 6 — it satisfies gate question 4 without being asked.

**And it splits, for the same reason layers 1 and 2 did:**

| | **5a — actor title** | **5b — empire title** |
|---|---|---|
| Carrier | `actor-title.{id}` | `empire-title.{id}` |
| Scope | one actor | **every actor of that empire** |
| Earned by | that actor's own achievements | the empire's achievements |

⭐ **5b is the first genuine empire-scope layer in this model, and it is the carrier this doc said did not
exist.** The earlier finding stands — `AllocationScope` has four values and none of them is an empire,
`world-map-scope` is Draft and `ContainerKind.WorldBuff` has never had a row authored. `empire-title.*`
is a *fifth* answer to the same need, and it is being built right now by someone else. **Two programs
are one step from independently inventing the empire axis**, which is precisely the failure the owner
described: features extending without checking impact.

**What "merge with us" has to mean, concretely:**

1. **5a and 5b register as layers in the closed list** (open question 0) rather than as a private path —
   the title program's contributions reach the compose the same way every other layer's do.
2. **5b decides the empire-scope question for the whole model, or explicitly defers to whatever does.**
   It cannot quietly become a second empire mechanism beside `world-buff` and `world-map-scope`. One of
   the three becomes the empire carrier; the other two are retired or given a stated, different job.
3. **The title program owes the five gate answers**, same as any feature: which layer, what scope, what
   lifetime (a title is presumably frozen once earned — append-only, like 1b), what carrier (answered
   already), and how it names itself in the SourceId grammar.
4. **This program owes them a stable target.** The layer list, the binder contract and the provenance
   grammar have to be settled enough that the title program can land against them rather than around
   them.

**The coordination idiom already exists in this repo** and should be used rather than reinvented:
`CrossProgramLandedFlags` (`gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs`) is a `const bool` per
cross-program prerequisite, flipped *by whoever lands the real feature*, at the same moment the tests
stop observing absence and start requiring behaviour. Its own doc comment states the discipline: *"a
landed flag is deliberately a `const bool`, not a runtime check: flipping it is a reviewed code change."*
A `TitleLayerLanded` flag of that shape lets this model assert "layer 5 contributes nothing yet" today
and "layer 5 contributes through the registered binder" the day it lands, without either program
blocking on the other.

⚠️ **The merge direction matters and should be stated now rather than discovered.** The title program
owns *what a title is* — how it is earned, displayed, and named. This program owns *how any layer reaches
an actor's numbers*. Neither absorbs the other: titles land **through** this model, and this model does
not acquire an achievement system.

## What a new feature owes this stack

Owner, 2026-09-16: *"Our development is so random, when we extend new feature we never careful check the
impact — and this program use to wire them together."*

That is the honest diagnosis, and this doc was not yet an answer to it. Recording measurements stops a
session repeating a mistake; it does not stop the **next** feature inventing its own path to an actor's
numbers. The stack only stays one compose if there is something a feature has to satisfy before it
becomes a layer. So, modelled on `the-loops.md`'s own *"What a feature owes this page"*:

**If your feature changes what an actor's numbers are, it is a layer. Answer these five before you build
it — in the feature's own spec, not here:**

| | Question | Why it exists |
|---|---|---|
| 1 | **Which layer is it, or is it a new one?** | If it is new, the layer list is a **closed vocabulary** and adding to it is a reviewed change — the same rule this repo already applies to `ActionCategory`, `AtomKind` and every other closed set |
| 2 | **What is its scope?** — global, per empire, per player, per species, per specimen, per match | Scope is what decides where the row lives and who it leaks to. Getting it wrong is how a player's fusion picks nearly ended up defining a species for everyone |
| 3 | **What is its lifetime?** — frozen, append-only, per-match, live | Frozen and per-player-mutable cannot share a table. 1a/1b exists because those two were the same row |
| 4 | **What carries it?** — an atom effect container bound at deploy, or a registered `IActorStatSubsystem` | Two carriers exist and both are legitimate. A *third* one invented per feature is the defect |
| 5 | **How does it name itself?** — provenance, so a contribution can be explained and withdrawn | The repo already refuses a progression source that cannot name itself (`creature.progression.v1`). A stat contribution that cannot is no better |

**And one rule that is not a question:** whatever the answers, the feature **contributes
`DerivedModifier`s into the one fold, or consumes Hub output.** It never decides the number itself. The
`attackDamage` write is what that looks like when it goes wrong — a second decision site, in a Unity
field, that nobody called a composer because it was not written in C# as one.

### What would actually enforce it

This section is prose, and prose does not stop anything. Two mechanical follow-ups belong in the spec
phase, both cheap and both in this repo's existing idiom:

- **A closed layer registry** — the layer list as a real enum/registry with a pinned membership test, so
  a new layer fails a test until someone reviews it. `guard-actor-hub.py` already refuses a second
  composer; this refuses a second *unregistered* source into the first one.
- **A contribution-provenance assertion** — every `DerivedModifier` reaching the fold carries a
  `SourceId` in the GG-49 grammar already (`ContributionSourceIds`). Assert that every registered
  subsystem's contributions resolve to a **named layer**, so an unowned contribution is a test failure
  rather than a number nobody can explain on a sheet.

### ⚠️ Two things this doc has been carrying as assumptions, now named

- ~~**Layer 5 (title system) is unverified.**~~ **Resolved the same day** — the owner named it as in
  build, and checking `worktree-achievement-title-20260915-7f3a` found the carrier already added:
  `ContainerKind.EmpireTitle` / `ActorTitle` and the `empire-title.*` / `actor-title.*` prefixes in
  `ContainerValidator.cs:29`. Layer 5 is **two** layers (5a actor, 5b empire), in build in another
  program, and it has to merge through this model rather than beside it. See "Layer 5 is in build in
  another program" above. On *this* branch nothing under `FusionRpg.Core/Stats/**` or
  `FusionRpg.Injector/Stats/**` mentions a title — which is correct, because the work is not merged yet.
- **The layer list is not closed yet.** The owner's own statement ended *"and more"*. Until someone
  writes the closing list, question 1 above has no answer to check against — which is precisely the gap
  that makes development feel random. **Closing that list is the single highest-value thing this program
  can do next**, and it is an owner decision, not a research task.

## Open questions — owner decisions only

0. ~~Is the layer list closed, and what closes it?~~ **RULED 2026-09-16** — owner: *"Layer will be
   extended for more mechanism but almost close, so i dont think we need any big refactor."*
   **The list is open to EXTENSION and closed to INVENTION.** A new mechanism may become a new layer; it
   may not reach an actor's numbers by a path of its own. Adding one is a reviewed registry entry that
   answers the five questions above — the same shape this repo already uses for every other closed
   vocabulary, none of which is frozen: `ActionTag` went 8 → 9 when base-defense added `Construct`, and
   the atom kinds went 17 → 18. **Closed here has always meant "a human changes it, and the change is
   reviewed" — never "it can never grow."**
   **And no refactor is implied, which the code agrees with:** five of the nine layers already reach the
   compose through the two existing carriers (3 equipment, 4 tree, 6 aura, 7 status, plus layer 1's
   binder, which is complete and merely unfed). What is left is content (layer 1's containers), one
   repoint (fusion picks → the new per-player table), one ownership correction (2b reads the owning
   empire), and one narrowing (the writer's remaining absolutes → a delta). None of those touches
   `ActorHub`, `DerivedComposer`, or the fold.
1. ~~What carries layers 2a and 2b?~~ **RULED 2026-09-16: a container — *"our repo standard"*.** My own
   recommendation was the opposite (state an exception, keep the allocation path) and the owner overruled
   it, correctly: an exception is a second way to reach the fold, and the whole point of this model is
   that there is one. **Every layer is a container. No layer is special.**
   What that means, and the cost I flagged being accepted rather than argued away:
   - **2a** is a per-specimen container, re-projected when that specimen levels. **2b** is a
     per-`(empire, species)` container, re-projected when that species levels — for the player's empire
     and for Zomboss's alike.
   - The aptitude allocation stops being the *runtime contributor* and becomes the **projector**: level ×
     budget × allocation produces the container's atoms, and the container is what binds. The math does
     not change; where it runs does.
   - **The cost is real and is the module's own work:** a level-up must re-project, so the write path
     needs the same care `ApplyEquipProjection` already takes — diff against stored, withdraw what is no
     longer backed, never double-grant. That is why this is a module and not a batch.
   - **What it buys** is what the exception would have cost: a progression contribution becomes
     inspectable, revisable and withdrawable like every other layer, one binder serves all nine, and
     `atoms-preview` can explain a number on a sheet without a special case for "except progression,
     which is computed".
2. ~~Who owns the zombie side?~~ **RULED 2026-09-16: Zomboss's empire owns it** — see "Layer 2b belongs
   to the OWNING empire" above. A zombie reads Zomboss's empire species progression, the same layer a
   plant reads from the player's. What remains is a balance question for `zombie-power-source`, not an
   ownership one: whether an empire that levels from every wave the game spawns is difficulty that scales
   with play, or an escalation nobody asked for.
3. ~~What happens to fusion picks when `player_species` retires?~~ **RULED 2026-09-16: repoint them into
   layer 1** — a fused species is a race the player authored, and the picks are what that race is. See
   "Layer 1 is the species definition" above. ~~The code already writes them into the right container.~~
   **Corrected the same day:** it writes them into the *shared* container, which is the cross-player leak
   — under the 1a/1b split they move to the new per-player table, so the repoint is real work.
   ~~A new question falls out of it: a fused species id is global while the picks are one player's
   choice.~~ **Answered by the owner the same day** — layer 1 splits into 1a (base species, shared and
   frozen) and 1b (player-modified species, a new per-player table written only when a mechanism actually
   modifies it). The shared id stays shared; no species id has to become player-scoped.

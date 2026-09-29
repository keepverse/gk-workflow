# Empire content seeds — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current.** It says *"idea phase ... Not a spec. No build
> authorized."* Measured today: [empire-seed-map.md](empire-seed-map.md) reads **"APPROVED
> 2026-09-19"** — the owner approved module boundaries, dependency direction and build order — with
> **15** module specs written at `docs/architecture/empire-seed/spec-<module-id>.md`. The map's own
> text still gates the *build* ("no build is authorized until each spec is approved"); no
> `tasks/empire-seed-todo.md` exists in this tree yet.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the capability map, the module specs, and the code.

**Status:** idea phase, 2026-09-19. Not a spec. No build authorized. **Program id:** `empire-seed`.

**Owner request (2026-09-19):** *"Deploy agents to enrich the seedsmith generator. We have kinds of
object that need a generator, like trading buildings, logistics buildings, logistics units, warehouse
buildings, resource usage, events, cargo management, trading stuff. This game has an item system,
empire resources and creatures; we lack empire general stuff for legion building. Anything can be
generated — that is why we need seedsmith."*

**What it serves:** the [trade-network](trade-network-ideal.md) umbrella program first, then every
world and empire system that needs a catalog of things: structures and — once its mechanics exist — legion content.

**Evidence base:** three read-only surveys (seedsmith architecture, world/empire content, generation
rules), one prior-art research pass on generated empire content, and an adversarial review of the
trade program, all 2026-09-19. Repo claims carry `file:line`; the load-bearing ones were re-read
against the code.

---

## 1. Which loop this extends

From `docs/guide/the-loops.md`: **Place 5 — World stage** (buildings are what you build
there), **Place 4 — World map** (legions and their standards on lanes), **Place 3 — Farm, hunt, defend**
(yield, storage, defence structures), and **Place 7 — Quests and events** (trade storylets). Content
generation serves those loops; it adds none of its own.

## 2. What this is

One seedsmith feature that fills the world and empire with **catalogs of things** the same way it
already fills items, creatures and actions: a deterministic planner decides what is missing, a model
names and describes each entry after its enums are already drawn, deterministic tables turn every band
into a number, and the game reads the result. Nothing a model writes is ever a number.

What it does **not** do: invent mechanics. A catalog for a mechanic that does not exist is content
nobody reads. Each family below names the mechanic it waits on.

## 3. The laws, restated inline

A downstream session reads this document, not its links.

1. **Seed → concrete → per-player. Three layers, and the middle one rolls.** Seedsmith emits seeds
   offline — enums only, committed and diffable. The game runtime rolls concrete objects per player
   through the shared SDK `Instantiator.TryInstantiate`
   (`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:92`). `ActionSeeder` already reuses
   `Instantiator.Draw` (`gk-core/src/FusionRpg.Core/Actions/Seeding/ActionSeeder.cs:19,45`). **Never design a
   second roll.** Deterministic stats are shared across players (as species stats are); only effects
   roll.
2. **The LLM writes identity; deterministic code writes magnitude.** *"A model has no calibrated sense
   of scale, so a number it picks is a plausible-looking guess that survives review because nothing
   looks wrong with it"* (`docs/architecture/seedsmith-map.md:38-44`). Enforced by schema audit, never by
   review. An author may write a count, a reference, an enum or a band — *"Never a magnitude, never a
   weight, never a probability, never a quantity"* (`docs/architecture/item/seed-contract.md:90`).
3. **Four ownership levels; a field with none is a contract defect** (`seed-contract.md:52-58`):
   `AUTHORED` (the author chooses), `DERIVED` (the importer computes), `GENERATED` (a generator emits
   rows), `VALIDATED` (the author names it; a frozen registry owns it).
4. **Generated data is never hand-edited.** Fix the generator, its tuning or its registry, regenerate,
   commit the diff. Hand-author only registries, exemplars and hand-authored kinds.
5. **The plan is deterministic** (P4). No model decides what work to do. A **deterministic planner
   stage runs before any model call** (base-defense decision 33), fixing which kinds, which bands and
   which slots.
6. **A metric without a declared target is an opinion** (P2); **every metric declares closed or open
   loop** (P3). An open-loop metric (flavour quality, distinctness) produces a review queue and **never
   gates** (`docs/architecture/seedsmith/spec-metrics.md:22-38`).
7. **A guardrail validates the contract, never a population.** Assert envelope, closed-enum
   membership, joins, uniqueness, reconciliation and determinism. Never pin how many buildings, standards
   or storylets exist, and never assert generated text (`docs/architecture/validation-ssot.md:81-89`).
8. **AI-native contract rules** (`docs/research/ai-native-generation/README.md`): permute every enum,
   seeded from `(entity_id, field, sample_index)`; majority-vote only load-bearing fields;
   **1-1-1 → `unresolved`**, never the first option; every attribute description carries a
   **negative clause**; `none` is a value and a missing key is a defect; prove constrained decoding is
   on with one real call before a run; transient and quality retries are separate paths, quality
   retries bounded at two; tests never call a model.
9. **One power ladder; the balance surface is data; no hard ceilings.** Bands resolve to numbers
   through `gk-core/data/tuning/`, reading `P(Θ)` where a magnitude scales. Floating point is allowed (owner
   ruling 2026-09-15); integer magnitudes are `long`.
10. **Rarity buys breadth and ceiling, never power; tier is not a distinctness axis.** *"A stronger
    version is not a different unit"* — a bigger warehouse is still a warehouse. A tier chain is a
    `variants` list, not four rows.
11. **Every actor number composes in `ActorHub`.** Any content that changes a creature's numbers
    (a legion standard, a tradition) contributes through a registered subsystem or atom reader — never
    a legion-local composer.
12. **SOLID and one mechanism.** One structure corpus, one seed reader shape, one storylet engine, one
    relation ladder. A new family extends the existing one; it never forks it.

## 4. What already exists

### Built

| What | Where | Proof |
|---|---|---|
| Seedsmith core: corpus, numerics, budget, metrics, report, planner, briefkit, pipeline | `docs/architecture/seedsmith-map.md:70-83`; `gk-forge/tools/seedsmith/seedsmith/` | Features 1–3 built (`seedsmith-map.md:3-10`) |
| The adapter protocol | `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:95-100` (`SeedAdapter`: `kinds`, `dimensions`, `legal_combinations`, `registries`, `channels`); `KindSpec` (`gk-forge/tools/seedsmith/seedsmith/adapters/base.py:24`) | Adapters registered in `ADAPTERS` get budget, coverage and distribution checks for free |
| Registered adapters | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18` — `stub`, `items`, `creatures`, `actions`, `dungeon` | Generic `check`/`metrics` CLI |
| Generation runtime | LangGraph workflow, SQLite checkpoints, constrained decoding (`seedsmith-map.md:337-347`) | Local Gemma-26B, no hosted tier |
| Structure corpus | `gk-data/packs/fusion/data/seed/structures/<role>/` — roles `bank`, `defend`, `deny`, `enable`, `extract`, `move`, `multiply`, `refine`, `see`, `store`, plus `wonder`; 28 anchors, all hand-authored (`_provenance.source = AUTHORED`) | Read by `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs` into `StructureCatalog` |
| Structure anchor schema | `docs/architecture/structure-seed-ideal.md` §5 — `structureId`, `role`/`roleSecondary`, `requiredSlotKind`, element, `strengthBand`, `costProfile`, `footprint`, `coverTier`, `rarity`, `traits`, `variants`, `acquisitionPaths`; every field an enum, ordinal, registry id or free text | Example: `gk-data/packs/fusion/data/seed/structures/store/coffer.json` |
| Structure generation code | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/` — `generate_anchor.py`, `generate_corpus.py`, `planner.py`, `metrics.py`, `anchor/schema.py`, `anchor/audit.py`; CLI `gk-forge/tools/seedsmith/seedsmith/report/cli.py:2973` | Hand-wired subcommand |
| Storylet-shaped event machinery | `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs` — weighted archetype draw, choices, pity; 56 seeded event files under `gk-data/packs/fusion/data/seed/dungeon/events` | `npc-story-events` re-seams it into the one storylet engine (`docs/architecture/npc-story-events-ideal.md` §6.2) |
| Container kind for a world-scoped granted effect | `world-buff` is in the closed container grammar (`docs/architecture/effect-atom/definitions.md:41`) | Binds through the existing attach points |
| Per-save relation ladder | Four bands, eager / open / wary / hostile, `disposition.v1.json` (`npc-story-events-ideal.md:389,411-420`) | Consumed, never duplicated |

### Wiring gap

| What is inert | Where | What closes it |
|---|---|---|
| **The `structures` adapter bypasses the protocol.** `adapters/structures/__init__.py` is empty and not in `ADAPTERS`; the same holds for `effects` and `trees` (CLI `cli.py:2935,2963`) | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12` | Implement `SeedAdapter` for structures and register it, so budget, coverage and distribution checks run on the structure corpus |
| **Identity-only structure rows.** A row is playable only with a `magnitudes` block (`StructureCorpus.cs:65`); `convoy-depot`, `causeway`, `coffer`, `stockyard`, `district-charter` have none | `gk-data/packs/fusion/data/seed/structures/move/`, `store/`, `enable/` | Band resolution (below) — they become playable without anyone typing a number |
| **Magnitudes live in the seed.** Playable rows carry an authored `magnitudes` block (cost, yield, build turns, capacity) inside the seed file, while `structure-seed-ideal.md` §7 says *"None is a `const`, and none is in a seed file"* and plans `data/tuning/structure-seed.v{n}.json` bands | `StructureCorpus.cs:13-18`; `gk-data/packs/fusion/data/seed/structures/**` | Move every magnitude to tuning bands resolved at load |
| **Structure cost has two sources.** `LoamPolicy` exposes structure costs from `data/tuning/loam.v{n}.json` that nothing calls; `BuildResolver` reads the corpus row | `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs`; `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs` | One SSOT — the band table |
| **`demons` adapter is orphaned** (legacy name; `creature` is current) | `tools/seedsmith/seedsmith/adapters/demons/` — no `__init__.py`, no importer | Delete or fold into `creatures`; not this program's to do, named so no one builds on it |

### Real gap

| What | Why it matters |
|---|---|
| **One shared seed-plus-bands reader.** Every family hand-rolls its own C# reader (`StructureCorpus.cs`; `gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSeedReader.cs`) | A new family (haulers) would add a third. SOLID says one reader and one band resolver |
| **World-family exemplars** — exemplars exist for items only (`gk-data/packs/fusion/data/seed/items/_exemplars/`) | Invention needs a hand-authored distribution for the model to extend (`structure-seed-ideal.md` §6) |
| **A trade role and legion content** | The content trade-network and legion-build need |
| **A world or empire attach point** — none exists; owner-key scopes include `sector` and `slot` but no `world`/`empire` (`definitions.md` §6) | An empire-persistent effect follows the declare-and-read pattern of `world-map-scope` instead (`docs/architecture/buff-debuff-scope/spec-world-map-scope.md:159-161`); never assume an atom hook |
| **Legion-building mechanics** — a legion member is species, level, hp, wounds, role; nothing for equipment, standards, formations or upgrades (`gk-core/src/FusionRpg.Core/World/WorldState.cs:265-326`); raising founds one Fighter of a climate-picked species (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs`) | The legion family (§6.4) cannot ship before its mechanics |

## 5. Prior art

From one research pass, 2026-09-19, which read `docs/research/game-design/06-unsourced.md` first and did
not repeat its dead searches. "Computed" means tallied from primary data files. Numbers marked
*unverified* could not be confirmed.

### 5.1 Building catalogs

| Game | Scale | Structure |
|---|---|---|
| **Anno 1800** (computed, [datamined data](https://github.com/NiHoel/Anno1800Calculator)) | 219 production buildings, 267 goods | **Every production building makes exactly one good; none takes more than three inputs.** Chains are 1–5 deep; 67 goods are one step, 2 are five steps |
| **Against the Storm** (computed, [cheatsheet data](https://github.com/FrankRuis/ats_cheatsheet)) | 56 workshops, 69 goods, 107 recipes | Three recipes per workshop (50 of 56); **76% of goods have two or more producers**; buildings are drafted pick-1-of-2–3 because *"simply randomizing building choices would cause a lot of problems with longer production chains"* |
| **Civilization VI** (computed, [game XML](https://github.com/Swiftwork/civ6-explorer)) | 47 buildings, 21 districts | The district is the placement puzzle; **36 of 47 buildings are flat-yield increases** — the "oatmeal" risk |
| **Anno 117** ([dev blog](https://www.anno-union.com/devblog-attributes-buff-buildings/)) | 174 buildings (*unverified*) | Eight attributes; a building gives a radius **buff and a debuff** (bakery: +2 income, −2 fire safety) |
| **Endless Legend 2** ([dev diary](https://community.amplitude-studios.com/amplitude-studios/endless-legend-2/blogs/967-economy-dev-diary-1)) | — | *"We reduced the number of Improvements per district to one"* |
| **OpenTTD** (computed, [engines.h](https://github.com/OpenTTD/OpenTTD/blob/master/src/table/engines.h)) | 88 road vehicles | A strict **cargo × generation grid**: 25 of 27 cargos have exactly three trucks |
| **Factorio** ([item weight](https://lua-api.factorio.com/latest/auxiliary/item-weight.html)) | — | Cargo weight is **derived from the recipe graph**, not authored — a logistics magnitude computed from structure |

**Failure modes.** *"30+ of them are just similar tier 2+ buildings … a lot of deckbuilding oatmeal"*
(Robert Yang on Against the Storm, [review](https://www.blog.radiator.debacle.us/2023/06/design-review-of-against-storm-by.html)).
*"Games provide too many"* units (Soren Johnson, [2013](https://www.gamedeveloper.com/business/seven-deadly-sins-of-strategy-game-design)).
Anno 1800's Docklands let players skip whole chains and was contested for removing the challenge; Anno
117 has no plans for one (search extract).

### 5.2 Events

| System | Numbers |
|---|---|
| **Stellaris 3.6.1** (computed, [game files](https://gitlab.com/stellaris/game)) | 5,307 events; **92% fired by something else**, 4.9% MTTH-polled; of 4,103 visible events **67% are single-option notices** |
| Stellaris modding wiki ([page](https://stellaris.paradoxwikis.com/Event_modding)) | *"Due to poor performance, using MTTH has fallen out of favor"* |
| **EU4** ([modding wiki](https://eu4.paradoxwikis.com/Event_modding)) | A size-scaling flag exists against *"event spam that province events tend to cause in huge countries"* |
| **CK3** ([modding wiki](https://ck3.paradoxwikis.com/Event_modding)) | Weighted pulses with a **"no event" weight** and per-event cooldowns; patch 1.9.1 cut frequencies; **a trigger that could never fire shipped** (stress above −65 when the minimum is 0) |
| **FTL** (computed, [XML](https://github.com/hahn-kev/ftl-xml-extension)) | 439 named events; 18.7% of 1,174 choices are "blue" options gated on crew or gear; per-sector **min/max quotas** |
| **RimWorld** ([raid points](https://rimworldwiki.com/wiki/Raid_points)) | Threat budget from wealth and colonists, clamped 35–10,000; players suppress it by burning wealth ([wealth management](https://rimworldwiki.com/wiki/Wealth_management)) |

### 5.3 Unit and army templating

**Hearts of Iron IV:** combat width *"remained at 80 for almost all terrain types"*, so only 20- and
40-width divisions were competitive; patch 1.11 set widths from 75 (mountains) to 96 (urban)
([Wargamer](https://www.wargamer.com/hearts-of-iron-4/update-combat-width)), after which the developer
said the optimum depends on opponent and location. **One global constant produced one template.**
**Total War Rome II:** army traditions outlive the troops and can pass to a new army (search extract).

### 5.4 Generated content

**Sameness is measured.** A current model given 100 identical prompts named a developer "Marcus Chen"
100 times out of 100 ([seehuhn, 2026](https://www.seehuhn.de/blog/ai-names/)); LLM stories reuse the
same plot elements across generations ([PNAS 2025, arXiv](https://arxiv.org/abs/2501.00273)).
**Freeze the output:** Infinite Craft sends only never-seen combinations to the model and caches the
answer so *"the same pairing will give the same result every time, for every player"*
([O'Dwyer](https://quuxplusone.github.io/blog/2024/02/08/infinite-craft/)). **Generation is decorative
unless correlated with gameplay** (Emily Short, [2016](https://emshort.blog/2016/09/21/bowls-of-oatmeal-and-text-generation/)).
**Never let the model judge outcomes:** players talked Where Winds Meet's LLM NPCs into completing
quests ([GosuGamers](https://www.gosugamers.net/entertainment/news/77655-where-winds-meet-players-outsmart-ai-npcs-to-easily-get-sidequest-rewards)).

### 5.5 Lessons

1. **A trade-off, not a bigger number, gives a building its identity** (Anno 117 buff-and-debuff;
   Civ VI's 36 flat-yield buildings are the counter-example).
2. **Every good has two or more producers; a processor takes at most three inputs** — checkable as a
   contract (Against the Storm, Anno).
3. **No universal substitute** — no building or doctrine replaces a whole chain (Docklands).
4. **Events react to facts and carry their rate limits in data** — cooldown, "no event" weight,
   per-host quotas, frequency independent of empire size (Stellaris, CK3, EU4, FTL).
5. **Test every trigger can fire** (CK3's dead trigger).
6. **Composition matters only when the best answer depends on context** (HOI4).
7. **The model names and describes only after the enums are drawn**; every call runs against a global
   dedup list and a blocklist; output is frozen once accepted (Marcus Chen, Infinite Craft).

## 6. The families

Each family states its anchor, the cheap axis (the one with the fewest downstream dependencies), its
grid density, where its numbers come from, what reads it, and what it waits on.

The density bands are the repo's own (`docs/research/game-design/03-roster-scale.md`): **~1–3.6
entries per cell is where rosters stay clean; ~12.6 is the documented failure zone.**

### 6.1 Structures — extend the one corpus

Trade and logistics buildings are **rows in the existing structure corpus**, not a new family. The
existing roles already cover most of what trade needs:

| Trade need | Role | Existing rows |
|---|---|---|
| Warehouse | `store` | `coffer`, `granary`, `relic-vault`, `stockyard` |
| Depot, waystation, road | `move` | ~~`convoy-depot`~~ `caravan-yard` (round 5 X12: the row; `convoy-depot` is its tier-2 variant), `causeway`, `waystation` |
| Bank point | `bank` | `reliquary`, `soul-conduit` *(superseded: the bank point is the Counting House building — `counting-house`, `Bank` role, `featureUnlock = banking` — round 4 §B; every seat starts with one, round 5 A1)* |
| Processing | `refine` | `refinery` |
| Trade center | **none fits** | — |

**One widening:** a trade center clears exchanges, which no current role does. Adding an `exchange`
role widens a closed vocabulary — a reviewed change (§9 D-E1). The alternative, reusing `enable`
(`district-charter` sits on the Market slot), would make one role mean two things.

- **Anchor:** the shipped structure schema, unchanged (`structure-seed-ideal.md` §5).
- **Cheap axis:** `role`. Element is the honest second axis where a structure is attuned; tier is not
  an axis (law 10).
- **Density:** 11 roles; base-defense estimates 24–40 types and targets ~36, and trade adds roughly
  8–12 rows. ~44–48 over 11 roles is **~4.0–4.4 per cell** — just above the clean band, well below the
  failure zone. The planner's per-role budget holds it there.
- **Numbers:** `strengthBand`, `costProfile`, `footprint` and the new capacity and clearing bands
  resolve through `gk-core/data/tuning/structure-seed.v1.json` (it exists, created by base-defense; this corrects the previous draft), as
  `structure-seed-ideal.md` §7 already plans.
- **Reader:** `StructureCorpus` → `StructureCatalog`, through the shared seed-plus-bands reader (§7).
- **Waits on:** nothing for identity; `trade-network` `sector-yield` and `exchange` for behaviour.

### 6.2 ~~Hauler kinds~~ — withdrawn in round 3

Owner ruling (2026-09-19): *"A caravan is an automatic legion, with or without a commander … extend
its architecture."* Transport is a legion's bearers on a trade standing order, so there is **no hauler
catalog**. What a transport legion needs from content is covered by the legion family (§6.4): a
logistics-leaning **doctrine** (for example, more cargo and less combat) is a doctrine seed like any
other.

### 6.3 Trade storylets — rows for the `narrative` adapter, not a second generator

`docs/architecture/narrative-seed-ideal.md` already rules out *"a second storylet generator beside the dungeon one"*:
storylets are emitted by the **`narrative` adapter**. Trade storylets are therefore rows that adapter
emits, in the one storylet shape (the existing `EventRow`: id, kind, theme, eligibility predicate, two
to four outcomes with an ordinal, effects by atom family and power band, a drop band, a repeat scope,
a `chainRef`; `npc-story-events-ideal.md:329-331`). This program contributes no generator here — only
the **facts and hosts** trade adds, each a closed-vocabulary addition reviewed through
`npc-story-events`:

- **Hosts:** a trade hub, a depot, a lane with flow on it, the turn report.
- **Predicate leaves:** warehouse full, delivery wasted, lane cut with goods stranded, caravan legion
  lost or intercepted, price spike or crash at a hub, treaty signed, broken or embargoed, clan request
  open, relation band with a faction.
- **Rate limits in data** (that program's tuning): cooldowns, a "no event" weight, per-host quotas,
  frequency independent of empire size (EU4). **Every trigger is tested reachable** (CK3's dead
  trigger).

### 6.4 Legion content — for `legion-build`

`legion-build` is now its own sub-program with an ideal ([legion-build-ideal.md](legion-build-ideal.md)),
and its catalog is generated here once its layer-5c mechanics exist:

| Seed | Anchor fields | Level |
|---|---|---|
| **Standard** | `name`, `flavor` (AUTHORED); `elementAffinity` (VALIDATED); `atomFamilies[]` from the closed catalog (VALIDATED); `carrierRequirement` ∈ any / fighter / commander (VALIDATED); `forgeGoods[]` from the goods registry (VALIDATED) | seed only |
| **Tradition** | `triggerKind` from a closed list of world facts (VALIDATED); `atomFamily` (VALIDATED); `rankNames[]` (AUTHORED) | seed only |
| **Doctrine** | `combatFamilies[]` (VALIDATED); `worldTradeoffKind` ∈ march / burn / sight / cargo (VALIDATED); `name`, `flavor` (AUTHORED) | seed only |

- **Cheap axis:** element × doctrine trade-off = 6 × 4 = **24 cells**; 24–48 seeds is 1–2 per cell,
  inside the clean band.
- **Numbers:** tier and rank magnitudes read `P(Θ)` through ~~`data/tuning/legion.v1.json`~~ `data/tuning/legion-seed.v1.json` *(round 4 Q12: seed magnitudes are empire-seed's file; `legion.v1.json` holds legion-build's mechanics only)* (proposed; the file does not exist yet);
  nothing in a seed is a number.
- **Contributions** compose in `ActorHub` through the layer-5c atom reader — never a legion-local fold.
- **Owner ruling:** standards and traditions reset when a legion disbands or routs, so seeds never carry
  inheritance rules.

**Legion equipment** (owner, 2026-09-19; `legion-build-ideal.md` §6.7) is the fourth legion seed:

| Field | Level | Notes |
|---|---|---|
| `pieceId`, `name`, `flavor` | AUTHORED | identity |
| `slot` | VALIDATED | a closed legion-slot vocabulary, separate from the unique-item equip slots |
| `tier` | VALIDATED | the piece's tier ordinal — its fixed stats resolve from this and the tuning bands |
| `atomFamilies[]` | VALIDATED | from the closed atom catalog |
| `recipeGoods[]` | VALIDATED | goods-registry ids — *which* inputs, never how many |
| ~~`producedBy`~~ | ~~VALIDATED~~ | ~~the structure role that makes it~~ *(removed in round 4: the producer is the Workshop → Armory → Foundry chain, `featureUnlock = legion-equipment`, read through `sector-features`; the chain's tier bounds the piece tier — `spec-legion-bands.md` §3 item 3)* |

- **Fixed, not rolled.** The deterministic layer resolves each piece's stats **once**, from `tier` and
  ~~`data/tuning/legion.v1.json`~~ `data/tuning/legion-seed.v1.json` *(round 4 Q12)* (proposed; the file does not exist yet) bands, at a share of the unique-item budget below 1. Every
  player sees the same piece. No `Instantiator` roll, no affix pool, no sockets, **no sets** (sets
  stay with unique-creature items, owner amendment 2026-09-19) — the unique-item generator never touches
  this family.
- **Cheap axis:** slot × tier; element is a second axis only where a piece is attuned.


### 6.5 What is deliberately not a generated family

| Asked for | Why it is not generated | Who owns it |
|---|---|---|
| **Trade goods** | v1 trades the existing closed material vocabulary (`gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:68`); new goods need P4, P6 and a registry row (trade-network D4) | `empire-resource-ssot.md` |
| **Resource usage** | Not a family — it is the `costProfile` and `upkeepProfile` ordinals on every structure and doctrine, resolved to amounts by tuning | Each family's band table |
| **Cargo management** | A mechanic and a surface, not content | `scoped-inventory`, `trade-surface` |
| **Clan trade personalities** | Computed from climate and species, never authored per clan (`world-graph-ideal.md` §8.2) — a model picking a clan's prices would be a model picking magnitudes | `trade-network` `counterparties` |
| **Named traders and clan elders** | Characters are `npc-story-events`' family (role `trader`, `clan elder`, `npc-story-events-ideal.md:387`) | `npc-story-events` |

## 7. The pipeline shape

1. **Invention, not classification.** A structure or standard corpus has no almanac to classify;
   *"there is no almanac of trenches"* (`structure-seed-ideal.md` §3). The failure mode is mode collapse
   and generic flavour, which a vote does not catch.
2. **Hand-authored exemplars first.** Each family gets a small authored distribution the model extends
   (the 28 structure anchors are that distribution for structures).
3. **Deterministic planner before any call.** It fixes which role, lane affinity, archetype and slot
   each new entry fills, against the per-family budget (P2). No model decides what to make.
4. **Enums drawn, then named.** The model receives an entry whose enums are already decided and writes
   only name, flavour and `reason`, against a **global dedup list and a blocklist** built from every
   existing name in every corpus.
5. **Load-bearing enums are voted only where the model chooses them**; for invented entries most enums
   come from the planner and need no vote.
6. **Freeze on accept.** An accepted entry is committed and never regenerated unless its inputs change
   (provenance plus `stale_ids()`).
7. **Metrics.** Closed-loop: every field populated, every enum in its registry, every band resolves,
   every storylet trigger reachable, every good with two or more producers once goods chains exist.
   Open-loop: flavour distinctness and near-duplicate prose — a review queue, never a pass.
8. **Call budget, computed before the run.** Roughly 15 structure rows and 20–40 legion seeds (standards, traditions, doctrines), one naming call each plus two retries at most: **~100–400 calls** on the local model.
   An estimate; the planner's own dry run prints the real number.

### Infrastructure first — model-free, zero tokens

| # | Module | What it does | Gap it closes |
|---|---|---|---|
| I1 | `structures-adapter` | Implement `SeedAdapter` for structures and register it in `ADAPTERS` | Wiring gap (§4) |
| I2 | `band-reader` | One C# seed-plus-bands reader and band resolver shared by every world family | Real gap (§4); SOLID |
| I3 | `structure-bands` | Move every structure magnitude from seed `magnitudes` blocks into `structure-seed.v{n}.json` bands; delete `LoamPolicy`'s unread costs | Wiring gap (§4); one SSOT |
| I4 | `world-exemplars` | Authored exemplars for structures (trade roles) and legion seeds, plus the **tone brief**: generic strategy-genre vocabulary, no named characters, no IP words (owner, round 3) | Real gap (§4) |
| I5 | `world-budgets` | Per-family budget targets: per role, per element × doctrine trade-off. The structure corpus's density band moves from a test literal to a tuning value — `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:192-195` asserts 2.4–4.0 per role, and the trade rows land at ~4.0–4.4 | P2; validation-ssot |

I3 is a data migration that must regenerate the structure corpus through its generator, never by hand
(law 4), and it must not change any playable row's resolved number — a byte-identical catalog before
and after is its acceptance test.

## 8. Tunables

| Block | File | Rows |
|---|---|---|
| Structure bands | `gk-core/data/tuning/structure-seed.v1.json`, next version | `strengthBand`, `costProfile`, `footprint`, `coverTier`, plus the new capacity and clearing bands → numbers |
| Legion seed bands | ~~`data/tuning/legion.v1.json`~~ `data/tuning/legion-seed.v1.json` *(round 4 Q12: seed magnitudes here; mechanics such as the rank thresholds stay in `legion-build`'s `legion.v1.json`)* (proposed; the file does not exist yet) | standard tier, tradition rank tier multiplier, doctrine combat band, equipment tier ladder and weaker share → numbers |
| Budgets | the same file, `budget` block | per-family target counts for the skew guard |
| Storylet rate limits | `npc-story-events`' tuning | cooldowns, "no event" weight, quotas |

## 9. Owner decisions — closed 2026-09-19

| # | Question | Decision |
|---|---|---|
| D-E1 | A new `exchange` structure role? | **Yes** — one reviewed widening of the closed role list, so `enable` keeps one meaning |
| D-E2 | Who owns the structure corpus? | **`empire-seed` owns every world and empire content family, the structure corpus included**; base-defense and trade-network both consume it. This revises base-defense decision 45's program boundary, not its content — `decisions.md` and `base-defense-map.md` carry the revision when the map for this program is approved |

Legion content follows trade-network §14 D-B: `legion-build` is a sub-program of the trade umbrella,
and its catalog is generated here once its mechanics exist.

## 10. What this deliberately does not decide

Band intervals and budget counts (a tuning pass); names and flavour (the pipeline's output); the
storylet engine's selection rules (`npc-story-events`); legion mechanics (`legion-build`); whether a
standard ever carries a rolled quirk.

## 11. Stale items found

- `.claude/skills/seedsmith-design/SKILL.md` Law 5 still says "never `float`"; floating point is
  allowed (owner ruling 2026-09-15). The skill's other laws hold.
- `docs/architecture/seedsmith-map.md:585` says nothing exists on disk for the dungeon corpus; committed
  files exist under `gk-data/packs/fusion/data/seed/dungeon/` (stale).
- `docs/architecture/effect-atom/atom-catalog-ssot.md:82` says eight attach points while its own prose lists nine (stale).

## 12. Next step

The model-free infrastructure needs no decision: `/spec empire-seed` for I1–I5, starting with
`structures-adapter` and `band-reader`. The trade structure rows and the legion family follow once
trade-network's `sector-yield` and `fleet` specs exist.

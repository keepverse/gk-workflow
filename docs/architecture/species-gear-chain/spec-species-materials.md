# Spec: Species materials (`species-materials`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `species-materials`
**Owning programs:** `item` module 14 (`salvage-craft`) + `creature-seed`
**Depends on:** `species-cost-shaping`, `creature-drop-tables`
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized. ⚠ *2026-09-18: approved through `tasks/species-gear-chain-plan.md`; build state — unbuilt (T33–T34).*
**Source ideal:** [species-craft-ideal.md](../species-craft-ideal.md) § The shape 3 — and [tier-system-ideal.md](../tier-system-ideal.md) D2 / E3b

> ⛔ **Amended 2026-09-18 for owner ruling R-SC1 (2026-09-17)** — `species-craft-ideal.md` § R-SC1:
> *"2 for each spec, 4 for each family and general, make it parameters in seedsmith, so deterministic
> engine can make correct distribution plan."* **This reverses three things the 2026-09-13 draft
> carried, and each is struck where it stood rather than silently rewritten:**
>
> | 2026-09-13 draft | R-SC1 |
> |---|---|
> | Family layer **withdrawn** | **Reinstated** — 4 per family (**8 since R9**, next note), on the consolidated family key, which is **not** the D7 lineage key that measurement disproved (§ Design 1) |
> | Species layer **1–2**, recommended **1 for unique / 0 for general creatures** | **2 per species**, and general creatures are **not** zeroed (R-S1: a general and a unique of one species leave the same remains) |
> | Counts in `creature-yield.v1.json` as runtime tuning | Counts are **seedsmith generation parameters** feeding a **deterministic distribution plan** (§ Design 4) — the ids are generated output, never authored rows |
>
> Open question 1 is closed. The R-SC2 prior-art correction (MH materials are **source-bound**, not
> a price) is carried in § Design 3. **Build state:** unbuilt (T33/T34, Phase 5).

> ⛔ **Amended again 2026-09-18 for owner ruling R9** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
> **general = 0, family raised to 8, species stays 2.** The owner: *"we shouldn't have general drop for
> all species… we already have soul and essence"* — a material every creature drops has no role that
> souls and essence do not already fill. **The general layer is removed entirely**: no `trophy.general.*`
> ids, no general drop leg, no general branch in the planner, and no `perGeneral` parameter (removed,
> not kept at 0 — § Design 4 says why). The scope vocabulary is now **two** values. This also closes the
> former Open question 5 (*what is the "general"?*) — the question is moot, not answered.
>
> ⛔ **Amended 2026-09-18 for owner ruling R22** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
> *"Rolled per kill, equal odds, among its families; the species counts as a member of **every** listed family for recipes, so it can supply any of them."*
> § Design 5.2 is rewritten to the rule (drop side), and the cost side (former Open question 6, map O1)
> is closed: a multi-family species' family-scope cost leg accepts a trophy of **any** listed family.
> The strengthen pass's *"first family on both sides"* recommendation is **not** adopted.
>
> ⚠ **"General scope" is not "general creature".** R9 removes the species-agnostic trophy *layer*. It
> does **not** touch R-S1: a general creature of a species still yields that species' and family's
> trophies exactly as a unique one does.

---

## Objective

**⭐ DECIDED — a species-bound set piece is enhanced with its own species' material.**

This is the last module in the initiative and the reason the other fourteen are worth building.
844 set entries are themed on a creature; `set-species-binding` makes that queryable and
`species-cost-shaping` makes it legible. **This slice makes it *earned*.**

> An earlier draft demoted this to optional, on the grounds that a declared species field delivers
> *"the same legibility"* more cheaply. **It does not:** a field makes the binding *queryable*, while
> the material is what makes it *earned*. Slice 1 is the prerequisite, not the substitute.

---

## ⛔ The ask-first boundary, and the exact test the repo already states

`MaterialClass` is **closed at five**, and `MaterialCatalog.cs:6-9` states the criterion for a sixth
verbatim:

> *"Closed: a sixth is an **ask-first** boundary, and the question a lane must answer to earn one is
> **'which of these five questions is unanswerable for my spend?'** — not 'I want another currency'."*

The five questions, from the enum's own doc comments:

| Class | The question it answers | Ids |
|---|---|---|
| `Souls` | *"May I act at all?"* — the flat fee | 0 (a ledger balance, *"which is why `All` is 27 and not 28"*) |
| `Shard` | *"How good may it be?"* — the rarity ceiling | `shard.{rung}` — **10** |
| `Substrate` | *"What is it made of?"* — **frame-locked**, graded by item level | `substrate.{frame}.{grade}` — 2 × 4 = **8** |
| `Essence` | *"What flavour?"* — element direction, **no magnitude** | `essence.{element}` — **6** |
| `Catalyst` | *"What am I doing to it?"* | `catalyst.{verb}` — **3** |

**10 + 8 + 6 + 3 = 27.** Verified by counting.

### The answer this module must give

**The species material answers *"what did this come from?"* — and none of the five asks that.**

- Not `Shard`: that is a rarity ceiling, and the species' rung already rides it via
  `species-cost-shaping`.
- Not `Essence`: element direction carries **no magnitude** and no provenance.
- Not `Catalyst`: that is the verb, not the source.
- ⚠ **Closest is `Substrate`** — *"what is it made of?"* — and this is the one that needs arguing
  rather than asserting. **It fails on granularity:** `Substrate` is `{frame}.{grade}` over exactly
  two frames and four grades, deliberately 8 ids, and its cost `variable` is `grade`. A species is
  neither a frame nor a grade. Folding species into it would mean `substrate.{species}.{grade}` —
  **904 × 4 = 3,616 ids**, which is precisely MH's documented `itemData` sprawl (IDs 0–2315) and the
  thing the closed vocabulary exists to prevent.

⭐ **So a sixth class — provenance — earns its place by the repo's own stated test.** This is an
**ask-first change** against `ssot-materials-crafting.md` §3.1, and it must be filed and answered
before any code.

---

## ⛔ And the ban this must not trip

`ssot-materials-crafting.md` §3.4 **bans source-tagged ids** — the *"every recipe becomes a travel
itinerary"* failure it refused for zone-keyed materials.

⚠ **§3.4 carries TWO refusals and an earlier draft answered only one.** Both are owed:

**(a) The zone refusal** — answered below (gating + the family layer + the five species-agnostic
classes beneath both).

**(b) ⭐ The ROLE-axis refusal** — `ssot-materials-crafting.md:160` refuses a **role** axis:
*"Twelve roles × anything is the scavenger hunt."* **This proposes a SPECIES axis at 904 — two orders
of magnitude past the twelve that were refused.** `tier-system-ideal.md:990-992` calls this *"a
deliberate reversal of sealed reasoning"* that **must say so**, because *"a reversal that is not named
reads as a defect to the next reviewer."*

**Naming it: the reversal is sound because the two axes fail differently.** A role axis multiplies
**every** recipe by twelve — every craft becomes a scavenger hunt, at every rung. A species axis
multiplies only the **gated top** of a tree (the `species-cost-shaping` threshold, one default plus
R-SC2's per-verb override), and is carried by the family layer and the five shipped species-agnostic
classes (souls, shards, substrate, essence, catalyst) beneath it. The refused shape had no gate and no
floor; this one has both.

⚠ *An earlier draft also leaned on "settable to 0 for general creatures" here. R-SC1 removed that
dial; the gate and the lower layers carry the argument without it.*

**(c) The SOURCE refusal** — `MaterialCatalog.cs:117-120` restates it in code (*"a source-tagged id
such as `essence.fire.pvz`"*). ⚠ **The SC8 mode-gate clearance is owed and is NOT free here:** a
species is reachable from expedition, delve and wild map — several modes, none required — **but only
if more than one of those selection modules ships.** If the gating species is reachable from exactly
one mode, that *is* a mode gate. **This module must name which selection modules must have landed
before its gated tier is legal.**

**Named, 2026-09-18 — and all three have landed:** `wave-species-roll` (T6, `63b9e8eb9`),
`wild-species-spawn` (T7, `d2361c761`) and `delve-species-wiring` (T20, `50a054c1e`). Admission is one
declaring site: `CreatureAdmission.ForWildMap` and `ForDelve` admit the same set
(`CreatureAdmission.cs:19-24`) and `ForWave` admits the `Summonable` subset (`:14-15`), so every
admitted species is reachable from at least two modes. What remains per species is **content** — its
rung must sit inside some table's window — and that is a report, not a gate on this module.

**Why a species material is not that, stated rather than assumed:**

1. **It is gated above a threshold rung** (`species-cost-shaping`). Early crafting stays generic, so
   no recipe becomes an errand until the player is deliberately chasing a top-tier piece.
2. **The family layer carries the trophy volume.** The species layer is a fixed, small number
   of ids per species (R-SC1/R9: 2), generated rather than authored — the id count is bounded by two
   generation parameters, not by zeroing a creature class.
3. **MH's `Monster Solidbone` proves the generic layer must survive beside it either way**, and it
   does here — as the five shipped species-agnostic classes, not as a trophy scope. R9: a
   species-agnostic trophy would duplicate what souls and essence already are.

This is the MH shape: **the rare per-monster part gates the top of a tree while common and generic
parts carry the early steps** — which is exactly what keeps low-tier creatures relevant.

---

## What exists today — verified

### Built

- **`MaterialCatalog.All` builds 27 ids from three id-shape tables** — `SubstrateFrames`
  (`humanoid`, `plant`), `SubstrateGrades` (`crude`, `sound`, `fine`, `prime`), `CatalystVerbs`
  (`forge`, `temper`, `flux`) — plus the ten rungs and six elements. **The catalog is generated from
  shape, not hand-listed**, so a new class with a declared shape extends it cleanly.
- **`MaterialCatalog.ClassOf` throws outside the closed set**, by design
  (`MaterialVocabularyRejection`).
- **`CostClassMatrix.Allows(op, cls)` throws `ArgumentOutOfRangeException` on an unrecognised class**
  — so a sixth class without an arm is a **hard failure, not a silent pass.** That is the correct
  posture and must be preserved.
- **A refusal rides one existing code.** `CostClassForbiddenRule = "material.cost-class-forbidden"`,
  *"raised as the one `ContentRuleViolated` code — **never a new member of the closed 33-code
  list**."* ⭐ **So this module adds no error code.** *(The "33" is the count of specific codes;
  `ContentRuleViolated` is the 34th and last by design, and with `None` the enum has 35 members —
  `AtomRejection.cs:118-128`, pinned as a closed vocabulary at `SocketOperationsTests.cs:61`. The
  `DropTableValidator.cs:28` "34th" and this spec's "closed at 33" describe the same enum; there is no
  conflict to resolve.)*
- `shard.{rarity}` is minted per rung; `species-cost-shaping` already keys cost on a species' rung.

### Real gap

| Gap | What must be built |
|---|---|
| The sixth `MaterialClass` + its id shape | ⛔ **Ask-first** against §3.1 |
| An arm in `CostClassMatrix.Allows` | Which verbs may spend it. Without one, it throws |
| ~~`gk-core/data/tuning/creature-yield.v1.json`~~ | ⛔ **Not this module's (strengthen pass 2026-09-18).** "Shared, whoever creates it first" was two owners for one file. `creature-drop-tables` owns it alone (it lands two layers earlier, and E3a is its only reader); this module reads nothing from it — its counts live in `species-material-run.v1.json`, its per-leg chances in the loot corpus |
| Generation of the layers | The family layer and the thin species layer, through seedsmith (R9: no general layer) |

---

## Design

### 1. Two layers — R-SC1 (owner, 2026-09-17) as revised by R9 (2026-09-18)

| Scope | Ids per scope member | Keyed on | Parameter |
|---|---|---|---|
| **Species** | **2** (R-SC1, unchanged by R9) | The species (`speciesId`) | `perSpecies` |
| **Family** | **8** (R9; was 4 under R-SC1) | A consolidated family id | `perFamily` |
| ~~**General**~~ | ~~4~~ → **removed (R9)** | — | none — no parameter, no ids, no drop leg |

**Why no general layer (R9).** A trophy every creature drops answers *"what did this come from?"*
with *"anything"* — which is no provenance at all, the one question § The answer this module must give
says the class exists for. The species-agnostic spend is already served by the five shipped classes
(the owner: *"we already have soul and essence"*).

**The family key is the consolidated family, not lineage — measured 2026-09-18, not assumed.**
The 2026-09-13 draft said *"⛔ The family layer is withdrawn … D7 (lineage as the family key) was
disproven by measurement"* (median 2, 49 singletons, cyclic, 80% multi-root). That stays correct
**about lineage**: lineage is not a family. R-SC1's family is a **different, existing key** — the
consolidated family map the action corpus already plans against,
`gk-data/packs/fusion/data/seed/actions/_generated/family-map.json`, written by
`adapters/actions/generate_characteristic_pool.py:160` and read by `adapters/actions/vocab.py:168`.
Read 2026-09-18 (a **reading**, printed here, never asserted): every species key carries a non-empty
family list — 626 species in one family, 277 in two, 1 in three — over 227 distinct families and
1,183 memberships; `decisions.md` — 'Action eligibility axis (2026-09-03)' records the same figures. ⚠ Do **not** join against
`gk-data/packs/fusion/data/seed/creatures/_generated/family-assignments.json`: it is the legacy 53-row, 19-family
projection of the 84-species catalog, and joining against it would orphan most of the roster.

**General creatures are not zeroed.** R-S1 (`species-progression-ideal.md`): a general and a unique
creature of one species differ only in equipment, so they leave the same remains. Species- and
family-scope materials therefore drop from **any** creature of the species, general or unique — the
lawn, which is overwhelmingly general creatures, stays inside the crafting economy.

### 2. Scope discipline — the ids are a reading, the parameters are the contract

> MH affords ~10 materials per monster at ~100 monsters. **At 904 species that ratio is impossible.**

MH's `itemData` sprawl (IDs 0–2315) is the failure the 2026-09-13 draft bounded by *thinning* the
species layer. R-SC1 bounds it differently and more durably: **two parameters (R9), one deterministic
planner, zero authored rows.** At today's corpus the plan comes to roughly
`species × 2 + families × 8` ids — printed by the planner's report, **never pinned** — and it
moves whenever a species ships, which is exactly why it is a reading (`validation-ssot.md`). What the
repo controls is the two parameters; what it asserts is the reconciliation (§ Testing strategy).

### 3. The escape valve, and the one that does not work

**Prior art settles both:**

- ⭐ **R-SC2 (2026-09-18) corrected how this repo read MH:** its materials are **source-bound** — the
  right monster must be hunted, with no substitute — which is a **content gate, not a price**. A
  source-bound threshold is not a ceiling because the content is always there to attempt. Its failure
  mode is *a wall when the source is content nobody wants to fight*; the mitigation is making the
  source worth engaging — **never a fallback currency**, which would re-make it a price.
- ✅ **MH's documented fix** for species-bound gear whose species is unavailable was to **make the
  species farmable** — never to invent a substitute. That is why this module follows the selection
  modules, and it is the whole reason the initiative is ordered the way it is.
- ✅ **Terraria's boss gear works because the encounter is the renewable resource.**
- ❌ **A trade-in shop does not solve the first-copy problem.** MH's own Elder Melder **requires you
  to already own one.**
- ✅ **If the tail still bites, the documented safety valve is the Artian shape** — a
  species-agnostic parallel path to an equivalent item. ⛔ **Never a wildcard material that quietly
  dissolves the binding.**

### 4. The distribution plan — deterministic, generated, append-only (R-SC1's load-bearing half)

> *"make it parameters in seedsmith, so deterministic engine can make correct distribution plan."*

**(new)** A **deterministic** seedsmith planner — no model call — emits the trophy id registry from
three inputs: the species corpus, the consolidated family map, and the two scope parameters. It is
the same discipline `SpeciesBuildPlanner` and the action `distribution_planner` already prove:
parameters plus a deterministic pass, never a hand-authored corpus.

| Input | Source |
|---|---|
| Species ids | The species seed tree, **skipping `speciesKind: "excluded"`** — R-CS3/R-CS4 rule those rows *"not a creature … never count as roster"*, so they leave no remains. The C# runtime mirror of `speciesKind` is unbuilt (`creature-seed-ideal.md` header); the planner reads the seed tree, where the mark does exist |
| Family membership | `gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` (§ Design 1) |
| `perSpecies` / `perFamily` | **(new)** `gk-core/data/tuning/species-material-run.v1.json` — a generation-run file read by seedsmith, the `action-corpus-run.v1.json` precedent (`adapters/actions/distribution_planner/tuning.py:28`). Not `creature-yield.v1.json`: that file's reader is the C# host at runtime, and these numbers decide *which ids exist* — a generation-time question with a different consumer |

**`perGeneral` is removed, not kept at 0 (R9).** A parameter fixed at 0 is a dial that invites being
turned back up — and turning it up would re-open a layer the owner ruled has no role. Removing it
also removes the planner branch, the `general` scope word and the `null` scope key with it. The strict
loader's *unknown key* refusal then rejects a stale `perGeneral` in the tuning file by name, rather
than silently ignoring it. Re-introducing a general layer is a **reviewed scope-vocabulary change**,
not a tuning edit.

**Id grammar — structural, stays in code:** `trophy.species.{speciesId}.{slot}`,
`trophy.family.{familyId}.{slot}`, with `slot` in `1..count` for that scope. The scope word is a
**closed two-value vocabulary** (species / family, R9) — pinning its size is correct; the ids under
it are a population.

**Append-only, because issued ids are player inventory.** Raising a parameter appends new slots;
**lowering one never deletes an issued id** — the registry is append-only exactly as
`themes.v1.json` is (`ladder-consistency-repair`'s lesson: re-planning after ids are held is a
migration, not a regeneration). A lowered parameter retires slots from **future drops** only.

**Who owns what, so no generator is edited against its stated scope:**

- The planner mints **ids**. `materialgen` authors **name / flavor / tags** for them — its
  `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/__init__.py:1-10` scope (*"never a new material id"*) is honoured, not widened, because id
  minting lives in a planner rather than in `materialgen`. Both belong to `item-seedgen` module 3
  (`materials-gen`); filing the planner there is a cross-program ask (§ Boundaries).
- **Core never reads a file** (T7.2): the host loads the generated trophy registry and injects it;
  `MaterialCatalog.ClassOf` resolves a `trophy.*` id only if the injected registry holds it, and still
  **throws** on anything else. The five shipped classes stay generated from their shape tables.

### 5. What one kill yields — the shape R-SC1 left to the spec

R-SC1 names two shape questions it does not answer (*"whether a family material is drawn instead of
or in addition to the species material on a given kill, and what a creature belonging to no family
drops"*). Both are answered here; neither changes a ruled number.

1. **In addition, not instead of.** A kill resolves two **independent** legs — species and family
   (R9 removed the general leg) — each an **independent draw group** in the creature's rung table
   (`DropTableGroupRow`, `DropTableModel.cs:76-85`: *"an independent draw unit"*), its chance being the
   trophy entry's weight against a `Nothing` entry in the same group. The weights live in the loot
   corpus (`gk-data/packs/fusion/data/seed/loot/**`, item module 11's), **not** in `creature-yield.v1.json` — one owner per
   number. Independent legs are one weight each and couple to nothing; an *instead of* rule would make
   the family rate a function of the species rate, and every balance pass would have to move both.
2. **A species in several families (R22)** resolves the family leg **once per kill**, picking one of
   its families with **equal odds** — so belonging to two families never doubles family volume.
   - **The draw:** `index = rng.NextInt(families.Count)` over the species' family list **in
     `family-map.json` order** (`gk-data/packs/fusion/data/seed/actions/_generated/family-map.json`; e.g. `bigpumpkin` →
     `["flora", "gourd"]`), on a new named stream `LootStreams.TrophyFamily(tableId, groupKey)` =
     `item.trophy-family.{tableId}.{groupKey}`, derived from the kill's sealed `lootSeed`
     (`LootPipeline.cs:233`, `LootStreams.LootSeed(correlationId)` at `LootStreams.cs:18`). Built in
     `LootStreams` and nowhere else, per that class's own rule (`LootStreams.cs:12-13`);
     `SeededRng.NextInt` (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:55`) is the uniform draw.
   - **Deterministic and replay-safe:** the stream is a pure function of `(SourceSeed, correlationId,
     tableId, groupKey)`, so the same kill always picks the same family; a replayed kill hits
     `PersistLootUnlocked`'s `(player_id, correlation_id)` early return (`RpgStore.Loot.cs:580-584`) and
     credits once. Its own name means adding it shifts no existing draw — the property
     `the_volume_stream_shifts_no_other_stream` already proves for step 5a (`LootStreams.cs:8-10`).
   - **Single-family species** skip the draw entirely (no stream consumed), so their rolls are
     byte-identical with or without this rule.
   - **Membership for recipes:** the species counts as a member of **every** listed family, so its
     family drops can supply a recipe of any of them (§ Strengthen pass item 4).
3. **A creature in no family** gets **no family leg** — never a fabricated filler family, and
   (R9) **no general leg as a fallback** either: such a kill yields its **species leg only**. The
   planner mints its `perSpecies` ids and no family ids; the drop resolver skips the family group
   for it; the planner's report lists every such species by id (a gap to report, never a filler to
   invent). None exist today — re-read 2026-09-18, every one of the 904 keys in `family-map.json`
   carries a non-empty family list (a reading); the rule is the contract, the same *"report the gap,
   never fabricate a filler"* posture R-SS2 cites from `threat-band`'s `UnoccupiedRung` guard. With
   the general layer gone this case matters more than it did: it is the only shape in which a kill
   yields a single trophy leg, so it is tested with a synthetic fixture, not left to the corpus.

How a per-rung drop table names *the killed species'* trophy without 904 tables is
`creature-drop-tables`' concern — see its Open question 3 (a scope-parametric entry resolved against
the killed species at mint time).

### 6. Orthogonality still binds

**Upgrade level and set membership stay independent.** No craft verb may break a set bonus, because
the bonus counts **membership**, not upgrade state.

---

## Tech stack

C# .NET 8 (`FusionRpg.Core/Items/Materials`), Python 3 (seedsmith generation), xUnit + pytest.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostClass"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"
dotnet run --project gk-forge/tools/ItemSeedValidator
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k material
python gk-core/scripts/audit-overflow.py
```

## ⛔ Three live `27` pins that BREAK THE BUILD, not a test

`MaterialCatalog.All` widening is not caught by a red test — **two of the three pins are module-level
`assert`s that hard-crash seedsmith on import:**

| Pin | Effect when the vocabulary widens |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py:120` — `assert len(ISSUABLE) == 27` | ⛔ **ImportError-time crash** |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py:124` — `assert len(ISSUABLE_BY_ID) == 27` | ⛔ **ImportError-time crash** |
| `gk-forge/tools/seedsmith/tests/test_recipes_gen.py:193` — `assert len(pool) == 27` | red test |

⭐ **All three must be replaced IN THE SAME CHANGE**, with a **reconciliation canary** rather than a
new literal — `len(ISSUABLE) == len(MaterialCatalog.All)` — because under this module the id count
**grows with content**, and pinning it would convert a closed-vocabulary assertion into a pin on a
derived population (`validation-ssot.md`).

⚠ An earlier draft pinned 27 on the **C# side only** and named `gk-forge/tools/seedsmith/**` merely as
*"layer generation."*

### ⚠ And `materialgen` structurally refuses this ask today

`materialgen/__init__.py:1-10`, in its own words: it authors *"`name` / `flavor` / `tags` for a
material id — **never a new material id**."* And ownership is not seedsmith's to assume:
`materialgen` and `droptablegen` are owned by **`item-seedgen`** (module 3 `materials-gen`,
`item-seedgen-map.md:90`; module 10 `drop-tables-gen`, `:98`). **Both facts belong in the ask.**

---

## Seedsmith / generator

**Generator involved: yes — this module's central deliverable is generated content.** P1 holds
throughout: the planner is deterministic and emits ids and joins only; the model authors
identity (name / flavor / tags) and never a number (`seedsmith-map.md` P1, enforced by
`pipeline/model.py:113` `audit_schema`).

| Stage | Adapter (path) | Change | Parameter / tuning file | New seed fields |
|---|---|---|---|---|
| Plan trophy ids — **deterministic, no model** | **(new)** `gk-forge/tools/seedsmith/seedsmith/adapters/items/trophyplan/` (`item-seedgen` module 3's territory — filed as an ask) | Reads the species seed tree (skipping `speciesKind: "excluded"`), `gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` (⛔ **do not reuse** `load_family_map_keys()` at `adapters/actions/vocab.py:159-186`: it returns only the family-id **values**, not the species → families mapping the planner needs; it returns an **empty set** when the file is absent; and it **unions** the legacy `gk-data/packs/fusion/data/seed/creatures/_registry/families.v1.json` ids into the result, which would mint trophies for families no species belongs to. The planner gets its own loader returning the full mapping, which **refuses** an absent or unparsable file by name, and **refuses** any non-excluded species absent from the map's key set — a species that shipped after `family-map.json` was last regenerated — distinct from a species present with an empty list, which is § Design 5.3's no-family case. Both conditions are tested), and the two parameters; emits the append-only trophy registry + a report of per-scope totals and of species with no family (both printed, never asserted). **No general branch (R9)** | **(new)** `gk-core/data/tuning/species-material-run.v1.json` — `perSpecies` 2, `perFamily` 8 (R9), `schemaVersion` + `version`, strict loader in the `distribution_planner/tuning.py` shape (refuses float / bool-as-int / numeric string / unknown key — so a stale `perGeneral` is refused by name) | Registry row: `materialId`, `scope` (closed enum: `species`/`family`, R9), `scopeKey` (an **index** — a `speciesId` or `familyId`, never `null`), `slot` (an ordinal index, never a magnitude). **No numeric field a model writes**; `slot` is emitted by code |
| Name / flavor / tags | `adapters/items/materialgen/` — `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py:117` (the mirror + the two module-level `27` asserts), `schema.py` (the answer schema) | The mirror stops asserting `27` and reconciles `len(ISSUABLE) == len(MaterialCatalog.All)` for the **five closed classes**, then extends the issuable set with the planner's registry. `schema.py` stays name/flavor/tags only — `audit_schema` must stay clean for it | none new | none — materialgen's row shape is unchanged; it gains ids, not fields |
| Recipes that spend a trophy | `adapters/items/recipegen/` (imports `materialgen.vocab` at `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/brief.py:31`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/emit.py:29`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/run.py:60`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/schema.py:20`) | Recipe legs may name a trophy **scope + slot**, resolved against the bound piece's species at cost time — never a literal per-species id in 904 recipes | the current `materials.v{n}.json` `operations` (which verbs demand which layer), revised by a `v{n+1}` publish | none |

**Regenerate** (both have `--dry-run`; the committed diff must be a pure regeneration — `AGENTS.md`
*"generated seed data is never hand-edited"*):

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith items generate --kind material --dry-run
python -m seedsmith items generate --kind material --write
python -m seedsmith items generate --kind recipe --dry-run
cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
```

The planner's own CLI verb is **(new)** and follows the `items generate --kind <x>` passthrough
(`report/cli.py:962-971`) rather than inventing a second entry point.

**pytest:** `gk-forge/tools/seedsmith/tests/test_materials_gen.py`, `gk-forge/tools/seedsmith/tests/test_recipes_gen.py`
(`:193` pin replaced), and **(new)** `gk-forge/tools/seedsmith/tests/test_trophy_plan.py` — reconciliation,
excluded-species skip, append-only re-plan, determinism (byte-identical second run), and
`audit_schema` over every schema the stage hands a model.

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs` | The sixth class + its id shape |
| `gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs` | The `Allows` arm |
| the current `data/tuning/materials.v{n}.json` | `operations` rows for trophy legs (the D5 exchange price is deferred, R25) — one `v{n+1}` publish (map § Tuning revisions) |
| `gk-data/packs/fusion/data/seed/loot/**` | The two trophy draw groups (species, family — R9) per creature rung table — their weights are the per-leg chances |
| `gk-core/data/tuning/species-material-run.v1.json` | **(new)** The two generation parameters (`perSpecies` 2, `perFamily` 8 — R-SC1 as revised by R9) — read by seedsmith only |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/trophyplan/` | **(new)** The deterministic trophy planner |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/` | Name/flavor/tags for trophy ids; the `27` pins replaced |
| `docs/architecture/item/ssot-materials-crafting.md` §3.1 | The reviewed amendment |

## Code style

The sixth class carries its question in its doc comment, exactly as the five do — that comment *is*
the test it had to pass:

```csharp
/// <summary>"What did this come from?" — provenance. NONE of the other five asks this: Shard is a
/// rarity ceiling, Essence is element direction with no magnitude, Catalyst is the verb, and
/// Substrate is {frame}.{grade} at 8 ids — folding species into it would multiply a graded axis by
/// the whole corpus. Ids are trophy.{species|family}..., minted by a deterministic planner
/// from two seedsmith parameters (R-SC1, R9) and injected by the host — never listed here.</summary>
Trophy,
```

And the `Allows` arm must be **narrow**, not permissive:

```csharp
// Only the verbs that IMPROVE a bound piece may spend a trophy, and only above the threshold rung
// (species-cost-shaping). A permissive arm here would reopen the "every recipe is a travel
// itinerary" failure §3.4 already refused.
MaterialClass.Trophy => op is CraftOperation.Elevate or CraftOperation.Temper,
```

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| ~~Species material count per species (1–2), settable to 0 for general creatures~~ | **Superseded by R-SC1** — the rows below | — |
| `perSpecies` (R-SC1/R9: **2**) | Trophy ids per species | **(new)** `gk-core/data/tuning/species-material-run.v1.json` — a **generation** input read by seedsmith, never by Core |
| `perFamily` (R9: **8**; R-SC1 had 4) | Trophy ids per consolidated family | Same file |
| ~~`perGeneral` (R-SC1: 4)~~ | **Removed by R9** — no general layer; not a row, not a 0 (§ Design 4) | — |
| Per-leg drop chance — species / family | § Design 5's two independent legs — a trophy entry's weight against `Nothing` in its own draw group | `gk-data/packs/fusion/data/seed/loot/**` creature rung tables (item module 11's corpus) — **not** `creature-yield.v1.json`, so the chance has one owner |
| ~~Species-tier → material grade/rung map~~ | Not a number this module reads — it is E3a's shard map | `creature-yield.v1.json`, **owned by `creature-drop-tables` alone** (strengthen pass 2026-09-18) |
| Which craft verbs demand a species material, and at what share of the cost | Whether the species leg is required on every enhance or only above a rung | the current `data/tuning/materials.v{n}.json` `operations` — revised by publishing `v{n+1}` (map § Tuning revisions) |
| Deterministic-exchange price — `exchangePriceSouls`, `exchangeTokensPerGrant` (whole units) | **D5**, which rides with this module. Variance insurance priced at ≈ the EV of the random path (PoE: 1/1500 vs flat 1500) | same `materials.v{n+1}.json` publish as the row above — **one publish for this module, not two** |

⚠ **`species-material-run.v1.json` and every `materials.v{n}.json` are tuning files — `gk-core/data/tuning/**` is
authored, never hand-edited in place** (T4: a change publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`,
which refuses to invent a key, so this module's new `operations` rows need the tool extended first —
`tunables-ssot.md` §7.1's "the domain builds the path it needs"). **Core never reads a file** (T7.2): the
host loads and injects.

⚠ **If the exchange price is derived from `P(Θ)` / `contentScale` rather than flat, it is a cost
ladder and owes its own `ssot-power-scale.md` §10 row.**

**Structural (stays `const`, with a comment saying why):** the material class vocabulary itself.
Widening it is a **reviewed change** against §3.1, **not a tunable** — which is exactly why this
module's central act is an ask, not an edit.

## Numeric types

- Material quantities and costs are **`long`** — magnitudes on an endless-progression axis.
- **Widen before multiplying; divide by 1000 last, exactly once; overflow throws, never wraps.**
- **Floating-point is allowed** (owner ruling 2026-09-15) — a `float` not being integer-exact past 2^24 is precision, not overflow.
- The two scope parameters (`perSpecies`, `perFamily`) are small `int`s — a **content cardinality**, not a magnitude.
- ⛔ **The id count is bounded by two parameters (R9), not by a cap on what a player may earn.** They
  bound how many *ids exist*; nothing bounds how many a player may hold. **No hard progression
  ceiling.**
- Per-leg chances are integer draw-group weights, validated by `DropTableValidator` (the draw
  already throws rather than wraps on an out-of-range total, `DropTableModel.cs:234`).

## ActorHub gate

**N/A and checked.** A material is an economy item. Spending one changes an item's affixes, which
compose through the existing equipment path into `ActorHub`. **Nothing here composes, contributes, or
folds.** `guard-actor-hub.py` stays green.

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit | ⭐ **The five shipped classes still generate 27 ids from their shape tables** — a **closed vocabulary**, so pinning 27 **for those five** is correct and the test says so. Trophy ids are a **population** and are never pinned |
| pytest | ⭐ **Reconciliation, not a count (R-SC1/R9):** every non-excluded species resolves to exactly `perSpecies` ids; every family in the map to exactly `perFamily`; every id's scope key joins back to a species or family that exists; no orphan id; ids unique; **no id carries a scope outside `{species, family}`** (no `trophy.general.*`). Totals are **printed**, never asserted |
| pytest | ⭐ **The scope vocabulary is exactly two** (`species`, `family`) — a **closed vocabulary**, pinned, and the test says so (R9 removed `general`; a third scope is a reviewed change) |
| pytest | The tuning loader **refuses** a `perGeneral` key by name (unknown key), and refuses a missing `perSpecies`/`perFamily` |
| pytest | A species with **no family** (synthetic fixture) mints exactly `perSpecies` ids, no family id, and appears by id in the planner's no-family report |
| pytest | Excluded species (`speciesKind: "excluded"`) mint no trophy id |
| pytest | ⭐ **Append-only:** re-planning with a **lowered** parameter keeps every previously issued id; with a raised one, appends slots and renumbers nothing |
| Unit | Per-kill yield: two independent legs (species, family); a multi-family species rolls the family leg once; a no-family species (synthetic fixture) yields its species leg only — no family leg, no fabricated family, and no general fallback (R9) |
| Unit | ⭐ **R22 single-family:** a one-family species' family leg always resolves to that family and consumes no `item.trophy-family.*` draw — its manifest is byte-identical to the pre-R22 resolver's |
| Unit | ⭐ **R22 multi-family distribution by seed:** over a fixed, enumerated seed set (not a random sample), a two-family fixture species resolves to each family; the same `(SourceSeed, correlationId)` always yields the same family; the index is `NextInt(count)` on `item.trophy-family.{tableId}.{groupKey}`. The per-family split is **printed**, never asserted as a rate |
| Unit | ⭐ **R22 replay:** replaying one kill's correlation id credits once and names the same family |
| Unit | ⭐ **R22 recipe acceptance:** for a piece bound to a multi-family species, a family-scope cost leg is satisfied by a trophy of **each** listed family (one case per family) and refused by name for a family the species does not list; preview and spend resolve the same concrete id |
| Unit | `ClassOf` still **throws** outside the closed set |
| Unit | ⭐ **`CostClassMatrix.Allows` has an arm for the sixth class** — proven by asserting it does not throw, for every operation |
| Unit | The arm is **narrow**: verbs outside the improve set refuse a trophy line |
| Unit | A refusal rides `material.cost-class-forbidden` — ⭐ **no new error code**, and the closed 33-code list is unchanged |
| Unit | A species-bound piece at or above the threshold rung **requires** its own species' material |
| Unit | Below the threshold, and for species-less pieces, no trophy is required |
| Unit | ~~Setting the per-species count to 0 for general creatures yields no ids~~ — struck by R-SC1. Instead: a **general** creature of a species yields that species' trophy legs exactly as a unique one does (R-S1) |
| Unit | ⭐ **Orthogonality** — spending a trophy never changes set bonus evaluation |
| pytest | Generation is deterministic and idempotent; a second run is byte-identical |
| Contract | `ItemSeedValidator` green; every trophy id resolves; no id is source-tagged by **zone** |
| Report | Total id count by layer — **a reading, printed, never asserted** |

⛔ **No test asserts the total material id count as a growth target.** The 27 is a closed vocabulary
and is pinned; the *species layer's* size is a reading bounded by a tunable.

## Boundaries

**Always**
- **Fix the generator and regenerate.** Layer content is seedsmith output.
- Keep `ClassOf`'s and `Allows`' throwing behaviour.
- Keep the `Allows` arm narrow.
- Bound volume with the two generation parameters, not with a cap on the player.
- Mint trophy ids with the deterministic planner; let `materialgen` author only name/flavor/tags.
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **The sixth `MaterialClass`.** This is the module's central act and it is ask-first against
  `ssot-materials-crafting.md` §3.1. **File it with the "which of the five is unanswerable?" argument
  above** — that is the form the boundary asks for.
- ~~The per-species count and whether general creatures get zero.~~ **Ruled by R-SC1** (generals
  not zeroed), counts revised by **R9** — 2 per species, 8 per family, no general layer.
- ⛔ **The planner's ownership** — id minting is `item-seedgen` module 3's territory
  (`materials-gen`); filing the deterministic trophy planner there is a cross-program ask.
- The D5 exchange price, and whether it earns a §10 row.

**Never**
- ~~⛔ A per-species material id for all 904 species as the default.~~ **Struck by R-SC1** — every
  non-excluded species gets `perSpecies` ids, **generated**. What stays forbidden is
  **hand-authoring** them, and adding a new wallet or currency (the vision's rule is unchanged —
  trophies are materials on the existing shelf, not a fourth wallet).
- ⛔ **Source-tagged ids** in §3.4's sense — a **zone**-keyed id. The gating, the family layer and the
  five species-agnostic classes are what keep a species id from becoming one.
- ⛔ **A species-agnostic trophy scope** (`trophy.general.*` or any renamed equivalent) — R9: souls and
  essence already fill that role. Re-introducing one is a reviewed vocabulary change, never a tuning edit.
- ⛔ **A wildcard material** that dissolves the binding. If the tail bites, the answer is the Artian
  shape: a species-agnostic parallel path to an *equivalent item*.
- A trade-in shop as the answer to unreachable species — the Elder Melder requires you to already own
  one.
- Add a new `ContentRuleViolated` code. The closed 33-code list is unchanged.
- Key the family layer on **lineage** (D7, disproven by measurement) or on the legacy 53-row
  `family-assignments.json`. The family key is the consolidated `family-map.json`.
- Pin the trophy id total, or any per-scope total, in a test.
- Let a craft verb break or re-check a set bonus.
- Assert a population count.

## Success criteria

1. The sixth `MaterialClass` is added under a **filed, answered** ask, with its question stated in its
   doc comment.
2. `CostClassMatrix.Allows` has a narrow arm; no operation throws; verbs outside the improve set
   refuse.
3. `MaterialCatalog.All` is generated from declared shapes, and `ClassOf` still throws outside the set.
4. ⭐ **A species-bound set piece above the threshold rung is enhanced with its own species'
   material**, end to end — the decision this whole initiative exists to deliver.
5. Below the threshold and for species-less pieces, nothing changes.
6. The trophy registry is **generated** by a deterministic planner from `perSpecies` / `perFamily`
   (R-SC1 as revised by R9: 2 / 8, no general layer); it reconciles against the species corpus and the
   family map with no orphan; re-planning is append-only; general creatures yield exactly as unique
   ones do; a species with no family yields its species leg only.
7. No new error code; the closed 33-code list is unchanged.
8. Set bonus evaluation is provably unchanged.
9. `ItemSeedValidator`, Core, Data and pytest suites green; this module publishes no `creature-yield` file.

## Strengthen pass 2026-09-18 — failure paths and edges the design above did not close

Each item was argued against once (would the existing text already cover it?) and kept only because it
does not.

1. ⛔ **A new dependency: `creature-seed`'s C# mirror of `speciesKind` (creature-seed map ask 4).** The
   planner skips `speciesKind: "excluded"` rows, so the registry holds **no trophy id** for the 12
   excluded species. At runtime those 12 still ship as `Summonable` and `CreatureAdmission.cs:14-24`
   admits them to waves, the wild map and the Delve. A kill of one would resolve a trophy entry to an
   absent id — which `creature-drop-tables` Open question 3 correctly **refuses by name**, so every such
   kill would refuse its loot. The fix is not a runtime filler (that fabricates provenance) and not a
   planner exception (that mints trophies for "not a creature"): **the trophy draw groups (T34, and T30's
   parametric entry) do not ship before `CreatureAdmission` refuses excluded species.** Map build order
   carries the edge.
2. ⛔ **Registry drift is a key-set edge (DESIGN-GATE §2.16).** The registry is generated from the species
   corpus and `family-map.json`; a species that ships later has no trophy row until the planner re-runs,
   and its kills hit the same refusal. The planner therefore ships a **`--check` mode wired into CI**, the
   way every other generated tree here is (`AGENTS.md` "Generated trees are committed; CI fails if they
   drift"): regenerate-in-memory, diff against the committed registry, fail on any difference. Tested
   with a fixture species added to the corpus and absent from the registry.
3. **Recipe legs resolve at cost time in one place.** § Seedsmith says a recipe leg names a scope + slot
   "resolved against the bound piece's species at cost time". That resolution lives in **one** C# site —
   `MaterialRecipeCatalog.Resolve(recipeId, RecipeContext)` (`MaterialRecipeCatalog.cs:318`), with the
   bound species carried on `RecipeContext` — so the workbench preview, the spend
   (`TrySpendAndApply`'s `lines`) and the recorded `cost_json` all read one resolved line list. A second
   resolver in the endpoint or the FE would let the previewed and debited ids diverge (SOLID S). A
   species-bound piece whose species has no registry row refuses by name (the same `material.*` rule
   family), never silently drops the leg.
4. **Which family does a multi-family species' recipe demand? — Ruled R22 (2026-09-18).** The species
   counts as a member of **every** listed family (278 species list more than one, a reading re-taken
   2026-09-18), so a family-scope cost leg on its piece **accepts a trophy of any listed family**. The
   debit still takes one concrete id, so the one resolver (item 3 — the same resolved line list for
   preview, `TrySpendAndApply` and `cost_json`) resolves the leg to the **first family in
   `family-map.json` order whose stock covers the whole leg quantity**; a leg is never split across
   families (a split would record two ids for one line). If none covers it, the refusal names every
   acceptable id. T34 emits family-scope cost legs for multi-family species on this rule — nothing waits.
5. **Retry and idempotency are inherited, not re-built.** A trophy is credited by `creature-drop-tables`'
   E2 arm inside `PersistLootUnlocked`, after its `(player_id, correlation_id)` early return, and spent
   through `TrySpendAndApply`'s correlation-keyed replay. This module adds no write path of its own; a
   test proves a replayed kill credits once and a replayed craft debits once.

## Open questions

1. ✅ **RULED 2026-09-17 (R-SC1) — 2 per species, 4 per family, 4 per general, as seedsmith
   parameters; general creatures are not zeroed.** § Design 1, 4. The superseded recommendation was
   *"1 for unique species, 0 for general."* **Counts revised 2026-09-18 by R9: 2 per species, 8 per
   family, general layer removed.**
2. **Which verbs may spend a trophy?** **Recommendation: `Elevate` and `Temper` only** — the two
   *improve* verbs. Reroll is re-randomisation, not improvement, and socket work is module 16's.
3. *(Not an open question — it was already decided, and an earlier draft reversed it silently.)*
   ⛔ **Reversed 2026-09-18 by the owner (R25): the exchange is DEFERRED** to a future trading and economy
   program; it does not ship with this module, and trophies have no souls fallback until then. The text
   below is the reasoning trail of the earlier decision.
   ~~**D5's deterministic exchange ships WITH the first tier content.**~~ `tier-system-ideal.md` D5:
   *"A deterministic exchange ships **with** the first tier content (**undisputed**)"*, and
   § DISPOSITION: *"D5 — deterministic exchange | **Rides with D2**."* The map repeats it.
   ⚠ An earlier draft recommended shipping materials first and the exchange later, **without naming
   that it was reversing a settled, undisputed decision.** The decision stands: **D5 rides with this
   module.** If the EV-pricing concern is real it is a reason to *file a reversal*, not to quietly
   re-open it in an open-questions list.
4. **Is the sixth class named `Trophy` or something else?** A naming call, but not a trivial one: the
   name is what the next reader uses to decide whether *their* spend belongs in it. **Recommendation:
   `Trophy`** — it names the provenance question rather than the material's physical nature, which is
   the distinction that keeps it out of `Substrate`.
5. ~~**OWNER — what is the "general" in *"4 for each family and general"*?**~~ **Moot — R9
   (2026-09-18) removed the general layer.** No reading of "general" is built; nothing waits on it.
6. ✅ **Ruled R22 (2026-09-18) — multi-family cost legs.** ~~Recommendation: the first family on both
   sides~~ — not adopted. Drop side: one family per kill, equal odds, on the named seeded stream
   (§ Design 5.2). Cost side: the species counts as a member of every listed family, so any listed
   family's trophy pays the leg (§ Strengthen pass item 4). Both halves of the old concern close: every
   family trophy a two-family species drops is spendable on its own gear. Map O1 closed.

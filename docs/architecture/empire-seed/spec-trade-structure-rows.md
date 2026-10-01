# Spec: `trade-structure-rows`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `trade-structure-rows` · **Map row:** 12 ·
**Wave:** 2 (moved from 3 by round 4 — see §1)
**Depends on:** `exchange-role`, `structure-bands`, `world-name-index` · **Model calls:** **none** for the eight
feature buildings (their names are the owner's); `world-namer` runs only if the planner reports a deficit
outside them
**Status:** spec phase, rewritten 2026-09-19 for the round-4 owner decisions
([trade-network/decisions-round-4.md](../trade-network/decisions-round-4.md) §B, binding). Map approved by the
owner 2026-09-19. No build authorized until this spec is approved.

---

## 1. Objective

Round 4 §B: *"every trade and logistics feature in a sector is unlocked by a specific building kind. Higher
tiers widen the feature. Tiers are `variants` of one structure row (seedsmith generates the tier variants
deterministically); a tier is never a separate building and never a separate row."* This module puts the
**eight** feature buildings into the one structure corpus, each as **one row with its tiers as `variants`**:

| Feature | Building kind (tiers, low → high) |
|---|---|
| Storage | Storehouse → Warehouse → Granary Complex |
| Banking | Counting House → Treasury → Vault |
| Trade | Trading Post → Market → Exchange → Grand Exchange |
| Caravans | Caravan Yard → Convoy Depot |
| Cross-world | Rift Anchor |
| Diplomacy | Embassy → Consulate |
| Legion equipment | Workshop → Armory → Foundry |
| Legion standards (**round 6 L6**) | Banner Yard → Standard Hall → Hall of Triumphs (owner, 2026-09-20; §5.1a) |

**Round 6 L6 (owner, 2026-09-20):** *"Does forging a standard need a building — **yes, its own building
kind** — a Standard Hall, with tier variants gating the standard tier (an eighth kind in the building
ladder; tiers are variants of one row, as for every other building)."* It joins the ladder here and is
read by `legion-build` `legion-standards` through `sector-features`, exactly like the Workshop chain.

The owner named every building and every tier, so the names are **authored identity**, not model output. The
rows are emitted by the one structure writer, `generate_corpus.py`, as `_authored` rows — the same path the
owner approved on 2026-09-19 for `relic-vault`, `standing-stones` and `sunspire-throne` (map §12 question 1).
No model runs for them, which is why this module moves from Wave 3 to Wave 2: the rows can exist before
`trade-network` `sector-yield` needs them (umbrella build order, `trade-network-map.md` §3 item 1).

What each tier *does* is the consuming mechanism's, never this module's (§2).

**Done means:**
- The eight rows exist in the corpus, each with its tiers as a closed `variants` list, a `featureUnlock`
  value and the neutral `structureKind: Feature` (round 6 C2); the corpus regenerates byte-identically.
- The published budget is met with zero deficits for the roles these rows use.
- Every row passes the anchor audit and the closed-loop metric set.

## 2. Scope and non-goals

**In scope.**
- The eight rows, their roles, slot kinds and variants (§5.1–§5.3).
- Two anchor-schema widenings the rows need (§5.4): the `featureUnlock` field and a closed `variants` item
  shape.
- Emitting the neutral `structureKind: Feature` on all eight rows (round 6 C2, §5.4 item 4).
- The budget targets, published by principle (§5.5), and the recomputed grid density (§5.6).
- The retirement of two identity-only rows into these buildings: `convoy-depot` becomes the Caravan Yard row
  and `workshop` moves from `Multiply` to `Refine` (§5.2).

**Not in scope.**
- What a tier unlocks, and every number that follows from it: warehouse capacity (`sector-yield`
  `warehouse-axis`), the bank point and the per-good hold (`sector-yield` `bank-points`, `banking-fact`), clan
  barter / market orders / treaties / cross-world routes (`exchange`, `counterparties`, `rift-trade`), crews
  and range (`fleet`), legion-equipment production (`legion-build` `legion-equipment`).
- **The upgrade verb** — how a sector moves a building from tier *n* to *n + 1*. No such verb exists today
  (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:66-89` builds into an **empty** slot only and refuses an
  occupied one, `build.occupied`). **Owned by `trade-foundation` `sector-features`**
  (`docs/architecture/trade-network/trade-foundation/spec-sector-features.md` §3–§4: a `build` naming the
  structure already on the slot raises its tier; the slot carries the tier), which also owns
  `StructureDef.FeatureUnlock`, the per-variant tiers and the `TierOf` / `FactionTier` reads. This module
  supplies the rows those read.
- ~~A `StructureKind` value for any of the seven. Each loads when its consuming module adds its kind and
  bands (the `Exchange` precedent, `spec-exchange-role.md` §2). Until then each row is identity-registered
  with `structureKind: none` (`structure-bands` §5.4).~~ **Withdrawn by round 6 C2** — that rule made every
  feature building permanently unloadable (global audit C2: no Storehouse, Counting House, Caravan Yard,
  Rift Anchor, Embassy or Workshop could ever be placed, built or counted, so the A1 start kit, bank
  points, warehouses and every feature gate read tier 0). All eight rows now carry the **one neutral
  `StructureKind.Feature`** and load with the corpus (§5.4 item 4). The *behaviour* of a kind is still not
  in scope here, and no gate reads a kind — X1's intent is intact and its wording is amended by C2 to allow
  this one neutral member.
- The C# `StructureKind.Feature` member and `StructureDef.FeatureUnlock` themselves: they land together in
  the field's first reader, `trade-foundation` `sector-features` (§5.4). This module emits the values.
- Trade storylets (`narrative-seed`), a hauler catalog (withdrawn, `empire-seed-ideal.md` §6.2).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | Rows in the roles these buildings use: `Store` (`coffer`, `granary`, `stockyard`, `relic-vault`), `Move` (`causeway`, `convoy-depot`, `waystation`), `Bank` (`reliquary`, `soul-conduit`, `sunspire-throne`), `Enable` (`district-charter`, `garrison-charter`), `Multiply` (`hatchery`, `workshop`), `Refine` (`refinery`) | `gk-data/packs/fusion/data/seed/structures/<role>/` (listed this session) |
| Built | `convoy-depot` and `workshop` are authored generator rows with no `magnitudes`, so neither loads and no saved world can hold one | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:406-411`, `:435-440`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| Built | `variants` is an AUTHORED open array; no row authors one; the planner bounds a list at 0–4 | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:105`, `:180`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:52` |
| Built | A build places a structure only into an empty slot of the structure's one required slot kind | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89` |
| Built | The committed plan counts 25 generator rows, density 2500‰ (25 rows / 10 roles) | `gk-data/packs/fusion/data/seed/structures/_plan.json` (`actualCounts`, `gridDensityMilli`) — a reading |
| Real gap | Any `Exchange` row; any feature-building row; a field saying which feature a row unlocks | — |

## 4. The generation rules, as they bind this module

- **The planner runs first** (decision 33). This module changes the generator's authored source and the
  budget, then runs the planner; it never writes a JSON row by hand.
- **Owner-named identity is authored.** The owner's register names every building and tier, so the model has
  nothing to write. `world-namer` is not called for these rows. If a later pass wants `flavor` text for them,
  that is a `world-namer` run over the `flavor` field only, with the names fixed.
- **A stronger version is not a different unit** (seedsmith-design ⑥; round 4 §B). A tier is a `variants`
  entry, never a row, never a second building.
- **No numbers in a seed.** A variant carries ordinals only; every tier number resolves through `band-reader`
  in the consuming module's change.
- **Validation is by contract.** Tests assert that every building has its tier list, that tiers are closed
  and ordered, that the budget is met, never how many rows exist.

## 5. Design

### 5.1 The eight rows

Each role is chosen from the closed role definitions (`docs/architecture/base-defense-ideal.md:2071-2078`:
R1 Extract *geography → stock*, R2 Refine *one stock in, another out*, R3 Multiply *raise another producer's
yield*, R4 Store *capacity per stock*, R5 Move *throughput, range, protection*, R6 Bank *the Tier-2 faucet*,
R8 Enable *gates what may be built here*) plus `Exchange` (*clears trades between parties*, D-E1).

| Row id | Base name | Variants (T2 → Tn) | Role | Why this role | `featureUnlock` | Slot kind | New? |
|---|---|---|---|---|---|---|---|
| `storehouse` | Storehouse | Warehouse, Granary Complex | `Store` | R4: capacity for located goods, the third capacity axis beside loam `Storage` and `ItemStorage` (`trade-network-map.md` §4) | `storage` | `Wildland` | new |
| `counting-house` | Counting House | Treasury, Vault | `Bank` | R6: banking turns located goods into banked currency, a currency source — round 4: *"the `bank` structure role keeps its meaning (a currency source)"* | `banking` | `Wildland` | new |
| `trading-post` | Trading Post | Market, Exchange, Grand Exchange | `Exchange` | D-E1: clears trades | `trade` | `Wildland`; `requiredSlotKinds: [Wildland, Market]` (round 5 B1) | new |
| `caravan-yard` | Caravan Yard | Convoy Depot | `Move` | R5: the load/unload point and the start of a caravan's range (`fleet` `depot`) | `caravans` | `Wildland` | replaces `convoy-depot` (round 5 X12: `caravan-yard` is the row, `convoy-depot` its tier-2 variant) |
| `rift-anchor` | Rift Anchor | — (one tier) | `Move` | R5: throughput between two worlds (`rift-trade` `crossing-leg`: *"priced and bounded like a lane"*) | `cross-world` | `Wildland` (round 5 B2; the capacity bonus when the sector also has a rift-tear slot is `rift-trade`'s mechanism, a sector read — not a second slot kind) | new |
| `embassy` | Embassy | Consulate | `Enable` | R8: its whole purpose is to gate — it does nothing but open diplomatic acts in its sector (§5.3) | `diplomacy` | `Wildland` | new |
| `workshop` | Workshop | Armory, Foundry | `Refine` | R2: goods in, legion-equipment pieces out (`legion-build-ideal.md` §6.7) | `legion-equipment` | `Wildland` | re-roled from `Multiply` |
| `standard-hall` | Banner Yard | Standard Hall, Hall of Triumphs (§5.1a) | `Refine` | R2: goods in, a forged standard out — the same shape as the Workshop, and forging is a goods sink (`legion-build/spec-legion-standards.md` §3) | `standard` | `Wildland` | new (round 6 L6) |

Every row carries `structureKind: Feature` (round 6 C2, §5.4 item 4).

**Slot kinds.** Round 4's first-throttle answer is a one-click "build a Counting House" (§B, Q3) and clan trade
at world start opens by building a Trading Post (§B, Q1). A feature building that must be buildable wherever
the need arises goes on `Wildland`, the slot every sector type allows
(`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:57-101`). A preferred site is a **sector** bonus read by the
mechanism (the `rift-trade` precedent for a `Tear` slot: `trade-network/rift-trade-map.md` C5), never a
second row on a second slot kind. The trade hub is the one contested case — `exchange-hub` prices a bonus on
a `Market` **slot** and `counterparties` `clan-seeding` seeds each clan's Trading Post on a `Market` slot,
while `Market` exists only in `homeworld` and `nexus` sectors (`SectorTypeCatalog.cs:57-62`, `:90-95`), where
`district-charter` also needs it (`generate_corpus.py:451-458`). A row has exactly one required slot kind
(`BuildResolver.cs:83-88`), so no single-slot answer serves all three. ~~This is owner question ES-R4-1 (map
§12b); the recommended answer is a small widening … Until the owner answers, this spec emits
`requiredSlotKind: Wildland` only (a subset every option keeps).~~ **Decided, round 5 B1 (owner,
2026-09-20):** *"Wildland or Market — a structure row may allow more than one slot kind; a Market slot gives
a bonus."* The Trading Post row carries **`requiredSlotKinds: ["Wildland", "Market"]`** (§5.4 item 3); every
other feature row keeps one kind. The Market bonus is `exchange-hub`'s clearing term, not seed content.

**Prerequisites between buildings** (a Rift Anchor needs a Grand Exchange in the same world, round 4 §B) are
admission rules of the consuming mechanism (`rift-trade`), not seed content.

### 5.1a The Standard Hall's tier ladder (round 6 L6, named 2026-09-20)

The Standard Hall's tiers gate the **standard tier** a sector may forge, exactly as the Workshop chain gates
the best producible legion-equipment piece tier (round 4 §B, `legion-build` `legion-equipment`). The owner
named the ladder on 2026-09-20:

| Tier | Display name | Forges standards up to |
|---|---|---|
| 1 | **Banner Yard** | tier 1 |
| 2 | **Standard Hall** | tier 2 |
| 3 | **Hall of Triumphs** | tier 3 |

**The naming fixes the ladder's length.** The row has one variant per standard tier above 1, so three
building tiers means the standard tier ladder is **three tiers**. That length is now authored content, and
`spec-legion-bands.md` §5.1 emits a three-entry standard tier multiplier ladder in `legion-seed.v1.json`
(proposed; the file does not exist yet).

Consequences, decided by principle rather than guessed:

- **The row id stays `standard-hall`.** It names the building *kind* the owner gave in round 6 L6, not
  tier 1. This is the one feature row whose id is not its tier-1 slug; renaming it to `banner-yard` would
  churn eight documents for an id no consumer reads (every gate keys on `featureUnlock: standard` and
  `SectorFeature.standard`, never on the row id).
- **The names ship now; the magnitudes do not.** Display names are authored identity and land with this
  module. The per-tier *multipliers* still publish nothing until the `ssot-power-scale.md` §10.2 row for the
  standard ladder lands (`legion-build-map.md` *Audit 2026-09-20* A-LB4; `spec-legion-standards.md` Hard
  edges). Until then `legion-standards` forges **tier 1** only, at a Banner Yard, which is what that spec
  already does.
- Nothing about the ladder's length is asserted in a test; criterion 2 asserts the *shape* of whatever
  variants exist.

### 5.2 The two retired identity-only rows

- **`convoy-depot` → `caravan-yard`.** The generator's `convoy-depot` row cites R5's *"nothing gives
  protection"* gap (`generate_corpus.py:435-440`); protection is now the `ward` verb (`logistics-flow`), and
  `fleet` already uses this row as the caravan load/unload point (`trade-network/fleet-map.md` module 2). The
  row is re-emitted as `caravan-yard` with the variant `convoy-depot` ("Convoy Depot"). **Save-neutral:** the
  row never loaded (no `magnitudes`), so no saved world, command log or golden names it; the only code
  mentions are the generator and a test comment (`gk-forge/tools/seedsmith/tests/test_structure_corpus.py:258`).
- **`workshop`: `Multiply` → `Refine`.** Its current identity is *"a second, generic instance beyond
  Hatchery"* with no mechanism (`generate_corpus.py:406-411`). Producing pieces from goods is R2, not R3.
  The row moves from `gk-data/packs/fusion/data/seed/structures/multiply/` to `refine/` (the role-directory rule
  `test_file_tree_groups_by_role_directory` asserts). Save-neutral for the same reason.

Both changes go through the generator and a regeneration; the old files disappear because the one writer no
longer emits them.

### 5.3 The `Enable` description — a reviewed wording change, not a new member

`Enable` means *"gates what may be built here"* (`base-defense-ideal.md:2078`). An Embassy gates what may be
**agreed** from its sector (treaties, blocs, embargo leverage). D-E1 refused `Enable` for the trade hub because
a hub *does* something beyond gating (it clears trades); an embassy does nothing beyond gating, so `Enable`
is its honest role. The role description widens by one clause — *"gates what may be built or agreed here"* —
in the same role-registry version `exchange-role` publishes (`roles.v2.json`, `spec-exchange-role.md` §5.1).
The member list does not change; the negative clause (*"NOT storage, NOT a road"*) stays.

### 5.4 Two anchor-schema widenings

1. **`featureUnlock`** — a new VALIDATED anchor field, closed vocabulary
   `none · storage · banking · trade · caravans · cross-world · diplomacy · legion-equipment · standard`
   (nine, with `none` for every other row; `standard` added by round 6 L6). **Pinned as a closed vocabulary**
   because a new feature building is a
   reviewed change to round 4 §B. Description with a negative clause: *"Which trade or logistics feature this
   building unlocks in its sector. NOT what the feature does at each tier (that is the consuming mechanism),
   NOT the role (what the structure is for)."* Consumers read **the feature, never a row id** — a mechanism
   that tests `structureId == "counting-house"` would couple rules to content.
2. **`variants` items become closed.** Each item is `{ "variantId", "name", "costProfile", "strengthBand",
   "footprint" }`: identity plus the same ordinals a row carries, so each tier's cost, HP and size resolve
   through the existing bands. **The tier is the list position** (`tier = index + 2`; the base row is tier 1)
   — DERIVED, never a field, because `tier` is on the numeric audit's deny list
   (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py:18-21`). The planner's
   `VARIANT_COUNT_POLICY` bound (0–4) already admits the longest chain (three variants); its comment that 4
   "mirrors the tier ladder length" is wrong (the ladder has three rungs, `gk-core/data/tuning/structure-seed.v1.json:17`)
   and is corrected in the same change.

3. **`requiredSlotKinds`** (round 5 B1) — a new optional VALIDATED anchor field: a non-empty list of
   `SlotKind` names, no duplicates, whose **first** entry equals `requiredSlotKind` (kept, so every reader of
   the single field and every existing row is unchanged; a row without the list means
   `[requiredSlotKind]`). Every entry must be a legal slot for the row's role (the role registry's
   `legalSlotKinds`, `spec-exchange-role.md` §5.1, which already declares `Market` and `Wildland` for
   `Exchange`). Description with a negative clause: *"Every slot kind this building may stand on. NOT a
   preference or a bonus (that is the consuming mechanism), NOT a list of sectors."* Seedsmith readers of
   the single field follow in the same change: the planner's pair derivation reads every entry
   (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:75`), and the adapter's `requiredSlotKind`
   dimension checks each (`spec-structures-adapter.md`). The C# field (`StructureDef.RequiredSlotKinds`)
   and the `BuildResolver` membership test land in the field's first consumer, `exchange` `exchange-hub`
   §3 (`trade-network/exchange/spec-exchange-hub.md`).

4. **`structureKind: Feature` on all eight rows** (round 6 C2). The anchor value is emitted here; the C#
   member is the reviewed widening named below. `Feature` does nothing in the loam or siege economy (the
   `Obstacle` precedent, `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:32-38`); a feature building's whole
   behaviour is its `featureUnlock`, read through `sector-features`. No consumer adds a per-building kind,
   and `StructureKind.Exchange` is withdrawn (`exchange` `exchange-hub` §1 drops it in the same docs pass).
   **Consequence to carry:** a loadable row must resolve — every base row and every variant names every
   ordinal its band tables need (`structure-bands` §5.3, criterion 4), or `StructureCatalog.All` throws
   `SeedBandException`. That is what `corpus-metrics`' `bands_resolve` check covers
   (`spec-corpus-metrics.md`), and it is why the rows land after the band tables, not beside them.

On the C# side `StructureDef` gains `FeatureUnlock` and a per-variant tier list, and `StructureKind` gains
the neutral `Feature` member. All three land in the **first consumer's** change — `trade-foundation`
`sector-features`, which every consumer reads through `TierOf` /
`FactionTier` (`trade-network/trade-foundation/spec-sector-features.md` §2, §5) — because a field with no
reader is a converter with no consumer (`gk-core/src/FusionRpg.Core/World/Bands.cs:7-8`). This spec fixes their names
and meaning; `sector-features` pins the same nine-member `featureUnlock` vocabulary with a join test against
this one. **Landing order (round 6 C1, global audit M5):** the schema widening (items 1–4) is a step of its
own and lands **before** `sector-features`, then `sector-features`, then these rows; the order is recorded
once in [landing-order.md](../trade-network/landing-order.md).

### 5.5 Budget targets, decided by principle

Rule: each role's floor = its prior floor + the feature buildings this module adds to it − the rows it moves
out. The floor stays "exactly what was authored" (the file's own note, `gk-core/data/tuning/structure-seed.v1.json`
`_note`), so it keeps working as a regression guard.

| Role | Prior floor | Change | New floor | Rows after this module |
|---|---|---|---|---|
| `Store` | 3 | + `storehouse` | 4 | 5 (`coffer`, `granary`, `relic-vault`, `stockyard`, `storehouse`) |
| `Bank` | 2 | + `counting-house` | 3 | 4 (`reliquary`, `soul-conduit`, `sunspire-throne`, `counting-house`) |
| `Exchange` | 1 (`exchange-role`) | + `trading-post` | 1 | 1 |
| `Move` | 3 | `convoy-depot` → `caravan-yard`; + `rift-anchor` | 4 | 4 (`causeway`, `caravan-yard`, `waystation`, `rift-anchor`) |
| `Enable` | 2 | + `embassy` | 3 | 3 |
| `Refine` | 1 | + `workshop` (moved in), + `standard-hall` | 3 | 3 (`refinery`, `workshop`, `standard-hall`) |
| `Multiply` | 2 | − `workshop` (moved out) | 1 | 1 (`hatchery`) |

Row counts assume `structure-bands` has folded the three hand-authored rows into the generator (map §12
question 1). With these floors the planner reports **zero** `targetNewRows`, so `world-namer` is not needed by
this module.

### 5.6 Grid density — recomputed, a reading

The planner's density is rows per role (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:92`: `1000 × total_rows / len(ROLE)`). Readings along the
build order:

| After | Rows | Roles | Density |
|---|---|---|---|
| today's committed plan (generator rows only) | 25 | 10 | 2500‰ |
| `structure-bands` (three rows folded in) | 28 | 10 | 2800‰ |
| `exchange-role` (eleventh role, no row) | 28 | 11 | 2545‰ |
| this module (+6 net rows: six new buildings; `caravan-yard` replaces `convoy-depot` and `workshop` only changes role) | 34 | 11 | 3090‰ |

Every reading sits inside the published band `[2400, 4000]‰` (`gk-core/data/tuning/structure-seed.v1.json:23`), which
`check_plan` reads (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:146`). The band is the contract; these numbers are printed, never asserted.
The ideal's "~4.0–4.4 per cell" was a different denominator and is already corrected (map §11 item 3).

### 5.7 The run

1. Author the eight rows in `generate_corpus.py` (`_authored`, citing round 4 §B and round 6 L6), each with
   `structureKind: "Feature"`; re-emit `convoy-depot` as `caravan-yard`, re-role `workshop`.
2. Publish the budget (§5.5) through `gk-core/tools/tuning/publish.py`.
3. Regenerate the tree and the plan; run `corpus-metrics`.
4. Rebuild `world-name-index` so the new names and every variant name block later collisions (a variant name
   is a name).

## 6. Commands

```powershell
python gk-core/tools/tuning/publish.py structure-seed <budget keys per §5.5> --label "trade-structure-rows: round-4 feature buildings"
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith.adapters.structures.generate_corpus
python -m seedsmith.adapters.structures.planner
python -m seedsmith.adapters.structures.metrics
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q
.\scripts\verify-change.ps1 -Paths <any C# test touched> -Session <build-session-id>
```

## 7. Acceptance (contract level)

1. For every value of `featureUnlock` other than `none`, exactly one row carries it (one building kind per
   feature — a contract over the closed vocabulary, not a population pin).
2. Every feature row's `variants` list is in tier order, each item validates against the closed item shape,
   and no item carries a numeric field or a `tier` key.
3. `featureUnlock` and the `variants` item shape are closed vocabularies with descriptions carrying negative
   clauses; an unknown value is refused by the anchor audit.
3a. **`requiredSlotKinds` (round 5 B1).** The Trading Post row lists `Wildland` then `Market`; every other
   row either omits the field or lists exactly its `requiredSlotKind`; a list whose first entry differs from
   `requiredSlotKind`, that repeats a kind, or that names a kind outside the role's `legalSlotKinds` is
   refused by the anchor audit.
3b. **Start kit rows exist (round 5 A1).** Exactly one row carries `featureUnlock = banking` and exactly one
   `featureUnlock = storage` (already criterion 1), each allowing `Wildland` — the kit
   `world-continuity` `world-creation` §5a places by feature.
4. Per-role counts meet the published budget within tolerance, read from tuning; `targetNewRows` is 0 for
   every role this module touches.
5. No row id `convoy-depot` exists; `caravan-yard` carries a `convoy-depot` variant; `workshop` is a `Refine`
   row in `refine/`.
6. A regeneration is byte-identical and makes zero model calls.
7. (Rewritten by round 6 C2) The C# catalog loads the tree and **every one of the eight rows is loadable**:
   each carries `structureKind: Feature` and a non-`none` `featureUnlock`, each appears in
   `StructureCatalog.All`, `IsKnown` answers for it, and no row carries a non-`none` `featureUnlock` with
   `structureKind: none` (`structure-bands` §5.4a, criterion 10). No row carries a per-building kind and no
   row carries the withdrawn `Exchange` (Core.Tests). ~~the seven rows are identity-registered with
   `structureKind: none` and leave `StructureCatalog.All` unchanged~~
8. Every row and variant name is unique across corpora through `world-name-index`, and every authored
   building and variant name passes the release scan against `ip-censor`'s `avoid-list` (global audit m20:
   *"Grand Exchange"* is also a well-known name elsewhere — advisory, the scan is the gate, and the name
   stays the owner's call).
9. No test pins a row count, a density value or a generated string.

## 8. Test plan and verification boundary

Existing structure suites plus new pytest cases for criteria 1–5 and 8, and one Core test for criterion 7.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` and
`data/tuning/structure-seed.*` are unmapped (`gk-core/scripts/verify-change.py:771`); the owner of the fix is
`test-verification-boundary` `python-test-lane`. The pytest command is the boundary. The C# test runs through
`verify-change.py` (`core-tests-fallback`).

## 9. Hard edges

- **Closed-vocabulary widenings:** the `featureUnlock` field (nine members after round 6 L6 adds `standard`)
  and the `variants` item shape (anchor schema); the `Enable` description clause (role registry v2). Each is
  reviewed, and lands in one commit with its tests.
- **`StructureKind.Feature`** (round 6 C2) is a reviewed widening of a closed C# enum, and
  `StructureKind.Exchange` is withdrawn in the same pass. Neither is this module's file: both land with
  `StructureDef.FeatureUnlock` in `trade-foundation` `sector-features`, ahead of these rows
  ([landing-order.md](../trade-network/landing-order.md)). Emitting `Feature` before that member exists
  would fail the anchor's VALIDATED check, so the schema step (§5.4) and these rows follow it.
- **Wave and ruleset bump (round 6 C1).** This module is empire-seed **wave 2**. It publishes tuning and seed
  content and grants no capability flag of its own; the flag and the **one** `RulesetVersion` bump that make
  these rows buildable belong to the wave that lands `sector-features` (`trade-foundation`), taken at landing,
  never pre-assigned, and recorded in [landing-order.md](../trade-network/landing-order.md). Loading eight new
  buildable rows changes what a world admits, so it is never a silent mid-life change: a world stamped before
  that wave does not gain the features.
- **Row retirement** (`convoy-depot`) and **re-roling** (`workshop`) are save-neutral (§5.2); they still move
  the committed plan and the tree, regenerated, never hand-edited.
- **Order with `trade-network`.** These rows exist before `sector-yield` needs them; each becomes loadable in
  its consumer's change.

## 10. Dependencies

- Upstream: `exchange-role` (the role and registry v2), `structure-bands` (the `structureKind` anchor field,
  one writer), `world-name-index` (dedup across names and variant names).
- Cross-map (hard, **behaviour** only): `sector-yield` (storage, banking), `exchange` (trade tiers),
  `counterparties` (diplomacy tiers), `fleet` (caravan tiers), `rift-trade` (the anchor), `legion-build`
  `legion-equipment` (the workshop tier gates the best producible piece tier).
- Cross-map (hard, **mechanism**): `trade-foundation` `sector-features` — the field's first reader, the slot
  tier and the upgrade verb (§2).

## 11. Open questions

- ~~**ES-R4-1 — the trade hub's slot kind** (map round-4 reconciliation). Default here: `Wildland`.~~
  **Closed by round 5 B1 (2026-09-20):** `Wildland` or `Market` (§5.1, §5.4 item 3).
- ~~**Owner naming owed (round 6 L6):** the Standard Hall's tier names.~~ **Closed by the owner,
  2026-09-20:** Banner Yard → Standard Hall → Hall of Triumphs (§5.1a). The three variants ship with this
  module; their multipliers still wait on the `ssot-power-scale.md` §10.2 row, so `legion-standards` forges
  tier 1 only until it lands.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: structure corpus content, structure-seed tuning, anchor schema, role registry wording.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares data/ paths.
[x] Read this session: decisions-round-4.md (all), trade-network-map.md §1a/§4, empire-seed-ideal §6, the
    role definitions (base-defense-ideal.md:2071-2078), generate_corpus.py rows for Store/Move/Bank/
    Multiply/Enable, planner.py check_plan, SectorTypeCatalog slot lists, BuildResolver slot gating.
[x] decisions.md: the D-E1 and D-E2 rows are implemented by upstream modules; no lock on building tiers.
[x] Every claim cites file:line.
[x] audit-doc-citations: run on this file after the round-4 rewrite.
[x] Verified against code and data: convoy-depot/workshop are identity-only and unreferenced outside the
    generator; the plan's density and counts; BuildResolver refuses occupied slots (no upgrade path).
[x] Read surrounding sections.
[x] Tested: none claimed; density figures are arithmetic over counted rows.
[x] No §2 invariant contradicted.
[x] Correction propagated: map §5.12 and round-4 reconciliation; VARIANT_COUNT_POLICY comment named.
[x] No population pin; the one pin is the closed featureUnlock vocabulary, with its reason.
[x] No cache, no ordering, no actor magnitude.
[x] SOLID: rows in the one corpus through the one writer; consumers read one field, never a row id.
[ ] New rule registry row: none.
[x] Round 6 (2026-09-20): C2 — all eight rows carry the neutral `structureKind: Feature`; the withdrawn
    `none` rule struck in §2; criterion 7 rewritten; the enum member is `sector-features`' to land. L6 —
    the Standard Hall row (§5.1, §5.1a: Banner Yard → Standard Hall → Hall of Triumphs), `featureUnlock`
    gains `standard`, `Refine` floor 3, density 3090‰.
    C1 — wave 2 named; the bump belongs to the wave that lands `sector-features`. M5 — schema widening is
    its own step ahead of `sector-features`. m20 — ip-censor scan in criterion 8.
[x] Round 5 (2026-09-20): B1 — requiredSlotKinds field (§5.4 item 3) and the Trading Post's
    [Wildland, Market]; ES-R4-1 closed. B2 — Rift Anchor stays Wildland, bonus is rift-trade's. A1 — the
    banking and storage rows are the start kit (criterion 3b). X12 — caravan-yard row, convoy-depot
    variant. X16 — Embassy Enable (§5.3, unchanged). Verified BuildResolver.cs:83-88 and planner.py:75
    read one kind today.
```

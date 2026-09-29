# Spec: `exchange-hub`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 5 of the [exchange map](../exchange-map.md) (wave 2; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.1, §7.6, §14b (PS-5).
Decisions: `docs/architecture/decisions.md` *`exchange` structure role* (D-E1) and *Structure corpus
owner — empire-seed* (D-E2). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make a trade hub a real place on the map: a structure that **loads under the one neutral
`StructureKind.Feature`** (round 6 C2 — `StructureKind.Exchange` is withdrawn, §1), built
through the existing `BuildResolver` on any slot its corpus row allows, with a **clearing capacity**
(value that may leave the hub per turn), a bonus on the Market slot, and a **consignment** — the one
place a foreign trader's goods can sit at another faction's hub. A sector with at least one active
hub is a **hub sector**; `order-book` trades there and nowhere else.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md) §B) makes the hub the Trade
building ladder:** Trading Post (tier 1, clan barter) → Market (tier 2, empire market orders) →
Exchange (tier 3, preferential treaties and blocs) → Grand Exchange (tier 4, cross-world routes). The
four are **variants of one structure row**, never four rows. This spec adds the tier reads (§7) that
`trade-access` gates on; the tier-to-feature table is `treaty-vocabulary` §5.

**Round 6 (2026-09-20, [decisions-round-4.md](../decisions-round-4.md) *Round 6*):** `StructureKind.Exchange`
is **withdrawn** and the hub row loads under the neutral `StructureKind.Feature` (C2, §1); a feature building
counts for nobody until one faction owns both its sector and its slot, read from `sector-features` (S1, §7);
settlement at a bank point waits on the save-identity re-key (C3, `settlement-payment`); the `trade.exchange`
flag names its wave and its wave's one ruleset bump (C1, §5).

**Round 5 (2026-09-20, [decisions-round-4.md](../decisions-round-4.md) R5-A/R5-X):** the Trading Post
row may stand on a **Wildland or a Market** slot, and the Market slot keeps its bonus (B1, §3); a
foreign trader's caravan unloads or loads at a hub only when the **hub's owner** has a Caravan Yard in
that sector (B3, §4); the staffing term and its key are this module's (X9, §2); the Market slot's
display name changes, its id does not (C4, §3); every gate reads `sector-features` (X1, §7).

## Scope and non-goals

In scope: `StructureDef.ClearingValuePerTurn` and its validation; the clearing-capacity function; the
Market-slot bonus; consignment state and its rules; the `trade.exchange` capability flag with its wave and
bump; the Market slot's `Buildable` flag; a template check; the hub tier and the faction trade tier reads (§7).

Not in scope (round 6 C2): **any `StructureKind` member.** The neutral `Feature` member lands with
`StructureDef.FeatureUnlock` in `trade-foundation` `sector-features`; this module adds none and withdraws the
`Exchange` member it used to add.

Not in scope (round 4): how a slot records its tier and how an upgrade is built — the one shared
mechanism every ladder uses, `trade-foundation` `sector-features` ([spec](../trade-foundation/spec-sector-features.md)) (`SectorFeature.trade`, `WorldSlot.StructureTier`, the upgrade
arm of `build`; it answered this map's ask E-A14); the tier variants' rows (empire-seed); the Diplomacy
ladder (`counterparties` `diplomatic-stance` §9).

Not in scope: the `Exchange` **role** and the hub **rows** (empire-seed `exchange-role`,
`trade-structure-rows`, D-E1/D-E2); the warehouse capacity axis (`sector-yield` `warehouse-axis`);
upkeep (`sector-yield` `structure-upkeep`); crews (`fleet` `crew`); orders and prices (`order-book`,
`price-curve`); moving consignments (`logistics-flow`, `fleet`).

## Design

### 1. No new kind — the one neutral `Feature` kind, and this module's one field (round 6 C2)

- ~~`StructureKind.Exchange` — a seventh member of the closed enum, a reviewed widening. The corpus row
  carries `"structureKind": "Exchange"`.~~ **Withdrawn by owner decision C2 (2026-09-20):** *"One neutral
  `StructureKind.Feature` for all feature buildings; `StructureKind.Exchange` is withdrawn; ruling X1's
  wording is amended to allow this one neutral kind."* The hub row carries `"structureKind": "Feature"` like
  every other feature building (`empire-seed/spec-trade-structure-rows.md` §5.4 item 4), and
  `Enum.Parse<StructureKind>` still refuses an unknown spelling at load
  (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:296`). The member itself lands with
  `StructureDef.FeatureUnlock` in `trade-foundation` `sector-features`, not here.
  - Why C2 went this way rather than keeping one per-building kind: the global audit found that six of the
    seven round-4 feature buildings could never load at all (a row loads only with a kind, the rows were
    emitted `structureKind: none`, and X1 forbade giving them one), while the Trading Post escaped **only**
    because this module added `Exchange` — an exception X1 did not cover, whose stated justification was
    clearing, not loam or siege. One neutral kind makes all eight loadable and keeps X1's real intent: **no
    gate ever reads a kind.**
- `StructureDef.ClearingValuePerTurn` (`long`, value units per turn **at the pin**): read only for the
  **trade-feature** row. Validation keyed on the feature, not on a kind (C2): a row with
  `FeatureUnlock == trade` must have it `> 0`; every other row must have it `0` — the one-field-one-axis
  rule the two capacity fields already follow
  (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:71-78`). Its number is a band resolved by
  `empire-seed`'s band reader; empire-seed's *consumer-added anchor fields* table
  (`empire-seed-map.md` §16) names the clearing ordinal, its band table and this module as its consumer,
  landing with this change.
- **Per tier (round 4).** The hub row is the one `trade`-feature row (`StructureDef.FeatureUnlock ==
  trade`; tier 1 is the row, tiers 2–4 its three variants — `sector-features` §2). What a tier **does** is
  this mechanism's tuning keyed by tier, never a band on the variant (`sector-features` §2,
  `empire-seed` `trade-structure-rows` §5.4): `ClearingValuePerTurn` is the row's band, and tier *t*
  multiplies it by `hub.clearingByTierMilli.{t}` (tier 1 = 1000). That is a four-entry table over a
  **building tier**, not a curve over a power level, so EC5's ban on a private `f(level)` is untouched.
- **No kind carries behaviour any more (round 6 C2; answers `fleet-map.md` X-F1 the other way).**
  ~~The kind stays, the gate does not read it … a row is `Exchange` **iff** its feature is `trade`.~~ The
  behaviour a kind used to justify is carried by the **field** (`ClearingValuePerTurn`) and gated by the
  **feature** (`FeatureUnlock == trade`), so nothing is lost by withdrawing the member: `Feature` does
  nothing in the loam or siege economy, the `Obstacle` precedent of a kind that deliberately does nothing
  economic (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:32-38`). Every gate — `HubTier`, `TradeTier`,
  `trade-access` — reads the feature through `sector-features`, never a kind. The load rule becomes the
  feature/field pair: `FeatureUnlock == trade` **iff** `ClearingValuePerTurn > 0` (a load rejection naming
  the row otherwise), which is the same protection without an enum member. `fleet` withdrew its `Depot` kind
  (its C22) and `counterparties` never added `Embassy` (round 5 X10); with C2 this module joins them, and the
  family now has exactly one answer.

**Contradiction EC7.** The map listed the seedsmith role tuple and `ROLE_TO_STRUCTURE_KIND`
(`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41`, `:64-69`) under this module. The
role widening is `empire-seed` `exchange-role`, and `empire-seed` `structure-bands` deletes
`ROLE_TO_STRUCTURE_KIND` in favour of a validated `structureKind` anchor field (`empire-seed-map.md`
§5.4 point 3, §5.5). This module touches only the C# enum and field.

### 2. Clearing capacity — no level table

A structure has no level of its own (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:134`). The map's
`center.clearingByLevel` would be a private `f(level)`, which the closed power inventory forbids
(`ssot-power-scale.md` §10, PRINCIPLES §5) — **contradiction EC5; that key is dropped.** A bigger hub
is a bigger row or variant, whose band is empire-seed's content. Capacity per hub sector per turn:

```
C(sector) = Σ over active trade-feature structures h in sector:   // FeatureUnlock == trade (round 6 C2)
              ClearingValuePerTurn(h) × clearingByTierMilli[tier(h)] × (1000 + marketBonusMilli(h))
                × staffingMilli(h) × scaleMilli(sector)
            / 1_000_000_000_000                                        // one divide, last; checked
tier(h)             = h's active tier (trade-foundation sector-features; an upgrade in progress counts at its current tier)
marketBonusMilli(h) = h's slot kind is Market ? hub.marketSlotBonusMilli : 0
staffingMilli(h)    = LabourCurve.Evaluate(hub.staffingCurve, LabourAt(h), hub.crewNeededByTier[tier(h)])
                      (bounded ratio 0..1000, round 5 X9 + global audit m14 — one evaluator, this module's own points)
LabourAt(h)         = fleet `crew` Crew.LabourAt(world, sector, slot, owner) — a bearer COUNT
scaleMilli(sector)  = sector-yield `essence-loop-read`'s sector scale  (PS-5: same read as the goods)
```

- **Range — the product needs a wide intermediate (audit 2026-09-20).** The numerator is a magnitude
  (`ClearingValuePerTurn × scaleMilli`, which grows with `P(Θ)`) times three per-mille factors
  (`10⁹` or more together). In `long` it overflows long before any other trade magnitude: with a row
  band of 100, tier 4 at 4000‰ and a Market bonus, it passes `long.MaxValue` near `Θ` ≈ 190
  (`P(Θ) = 80 + 26.2·Θ + 0.2·Θ(Θ−1)` against the pin `P(20) = 680`, `gk-core/data/tuning/power-scale.v2.json:9`),
  far inside normal play. So the product is taken in `System.Numerics.BigInteger` (Core targets
  `net6.0`, `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`, which has no `Int128`; the repo precedent is
  `gk-core/src/FusionRpg.Core/Actions/Unlock/UnlockLadder.cs:38`), divided **once**, and narrowed to `long`
  **checked** — a result that does not fit `long` throws. Divide-last is kept; the old "one `long`
  product" reading is withdrawn. Acceptance 13 tests it at a deep `Θ`.
- **One labour-to-output evaluator (global audit m14).** The first draft's `min(1000, LabourAt × 1000 / need)`
  was a second shape for a curve the family already has: `fleet` `depot` and `rift-trade` `crossing-anchor`
  both read the one `LabourCurve` (`rift-trade/spec-crossing-anchor.md` §2). Round 5 X9 lets **exchange own
  its staffing term and its key** — it does not license a second evaluator, so the term is evaluated through
  `LabourCurve` with **this module's own points** (`hub.staffingCurve`, a bounded 0..1000 ratio whose
  default reproduces the old linear ramp exactly: 0 at no crew, 1000 at `crewNeededByTier`, linear between,
  flat after). One evaluator, three sets of points; a balance pass changes the points, never the code.
- **Active** means a structure is present and `ConstructionTurnsRemaining` is null or zero
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:119`, `:126`). An under-construction hub clears nothing.
- **Per-turn structural rate, not a progression cap.** The code comment says so (DESIGN-GATE caps row);
  it grows with the sector's content scale, so it never becomes a hidden ceiling at depth (§14b PS-5).
- **What it bounds:** the value of goods leaving the hub owner's stock to traders in one turn (buy
  legs). Sell legs are the payment side and are bounded by what they fund (`settlement-payment`).
- **Staffing — this module's term (round 5 X9).** `fleet` `crew` supplies only a bearer **count**
  (`Crew.LabourAt`, `fleet/spec-crew.md` interface: *"a bearer count, never a ratio"*); this module turns
  it into the ratio and owns the key `hub.crewNeededByTier.{1..4}` (bearers a hub of that tier needs to
  run at full clearing; ≥ 1, non-decreasing in tier, a load check). The `min(1000, …)` is the bound of
  a **ratio**, not a progression cap (commented as such, DESIGN-GATE caps row): extra bearers never
  raise clearing above the tier's capacity; a bigger hub is the next tier. Until `crew` lands,
  `staffingMilli` reads 1000 for every faction — a named wiring gap, identical for all factions, so not
  a handicap. (Superseded: *"`staffingMilli` = fleet `crew` staffing ratio"* — `crew` never exposes a
  ratio.)
- The same scaled value sizes `floor` and `stepUnits` for `price-curve`
  (`price.floorUnits`, `orderStepUnits` × `scaleMilli` / 1000, at least 1).

### 3. The Market slot

The Market slot exists once per shipped template, pre-claimed in the home sector
(`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:147`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:47`)
and is catalogued with `Buildable` unset (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`).
**Finding (contradiction EC8):** the engine never reads `Buildable`. `BuildResolver` gates on the slot
kind matching the row's `RequiredSlotKind` (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:83-88`);
`Buildable` is only validated (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:109-111`) and sent to the
web client (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:508`). So a Market-slot hub is buildable in the
engine the day a row allowing `Market` exists; this module sets `Buildable = true` on the Market slot
so the client offers it. That flag is not hashed, so no golden moves.

**Wildland or Market — round 5 B1 (owner, 2026-09-20).** *"A structure row may allow more than one slot
kind; a Market slot gives a bonus."* The Trading Post row allows **`Wildland` and `Market`**
(`empire-seed` `trade-structure-rows` §5.1, `requiredSlotKinds`). Today a row names exactly one kind:
`StructureDef.RequiredSlotKind` (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`), parsed at
`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:297` from the anchor field read at
`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:120`. The change, landed in this module's
commit because it is the multi-slot field's first consumer (`empire-seed` `trade-structure-rows` §5.4):

- `StructureDef.RequiredSlotKinds` (`IReadOnlyList<SlotKind>`, at least one, no duplicates) — parsed from
  the anchor's `requiredSlotKinds`; a row without it is `[requiredSlotKind]`, so every existing row loads
  unchanged. `RequiredSlotKind` stays as the **first** entry (the row's primary kind; the Seat range rule
  at `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:95` keeps reading it).
- **`BuildResolver`** (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`): refuse when the slot's
  kind is **not in** `RequiredSlotKinds`; the reason keeps its prefix, `build.wrong-slot-kind:{slotKind}-needs-{k1|k2}`.
  **`WorldValidation`** (`gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411`) applies the same membership
  test on load. Both are the world-map/structures program's files — coordinated, not taken over (the
  `sector-features` hard edge).
- **Readers that must follow in the same change** (verified this session; each compares one kind today):
  the siege board, `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:267` and
  `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:363` (a membership test; the Trading Post is not a siege
  structure, so no siege behaviour changes); the client DTO, `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:412`
  and `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:488` (add the list beside the single field).
- **Hash.** The slot's structure id is what is hashed, not the row's legal kinds, so a world with no
  Trading Post hashes byte-identically.

**Slot display names — round 5 C4, filed as one ask (global audit m15).** The `Market` slot's display name
(`SlotTypeCatalog.cs:74`, `Name = "Market"`) collides with the tier-2 building "Market"; the owner chose to
**rename the slot's display name** and keep the building names and every id (`market` slot type,
`SlotKind.Market`). `SlotTypeCatalog.cs` is **world-map's file**, and `trade-surface` `trade-lexicon` files
the same rename for the `vault` slot — two routes to one file was m15. **Resolved: one ask to world-map**
(global audit X-14), covering both slots, with the words from `trade-lexicon`'s §C4 table: *"rename the
display `Name` of the `market` and `vault` slot types; ids and `SlotKind` unchanged."* This module **does not
edit `SlotTypeCatalog.cs`** any more; it only depends on the ask, and nothing it owns is hashed by the
display name.

### 4. Consignment — a foreign trader's goods at a hub

The map's settlement text has the buyer pay *"from its stock at that hub"* (exchange-map module 8), but
located stock is one pool per (sector, good) owned with the sector (`sector-yield-map.md` §2.4). Nothing
represents a third party's goods sitting at another faction's hub — **contradiction EC9**. Resolution:

- `WorldSector.Consignments`: a sparse, hashed list of `(FactionId, GoodId, Qty : long)`; a zero row is
  never written, so an existing world hashes byte-identically. **Canonical order (audit 2026-09-20):**
  rows are kept and written sorted by `(FactionId, GoodId)` with `StringComparer.Ordinal`, one row per
  pair (a second write to the pair adds to it), so the canonical text — and the SHA-256 state hash
  taken over it (`gk-core/src/FusionRpg.Core/World/Turn/StateHasher.cs:17-23`) — never depends on the order
  fills, flows or caravans touched the list.
- Consignments **share the sector's one warehouse capacity axis** (ideal principle 12): occupancy =
  the owner's located stock + Σ consignments. A fill moves goods between the owner's stock and a
  consignment inside one warehouse, so it never changes occupancy; only fees and tariff sinks remove
  goods.
- **Writers:** `settlement-payment` (fills), `logistics-flow` (lane-flow arrivals into, and departures
  out of, a foreign hub sector — ask E-A5), `fleet` (a caravan unloading or loading at a foreign hub —
  fleet ask A6). The hub owner never holds a consignment at its own hub; its goods are its located stock.
- **A caravan needs the hub owner's yard — round 5 B3 (owner, 2026-09-20).** *"The hub's owner also
  needs a Caravan Yard in that sector (so seeded clan hubs get a yard too)."* A caravan may unload into,
  or load from, a consignment only at a **foreign site**: the hub owner's sector with
  `SectorFeatures.TierOf(hubSector, SectorFeature.caravans) ≥ 1`. **The check is `fleet` `depot`'s**
  (`ForeignSite.Of(world, hubSectorId, visitorFactionId)`, `fleet/spec-depot.md`; refusal
  `depot.no-foreign-yard`, the caravan waits) — the site predicate for every caravan leg lives there, so
  this module adds **no second check** (X1, SOLID S): a consignment write by `fleet` only ever happens at
  a site `ForeignSite.Of` returned. Lane-flow deliveries (`logistics-flow`, E-A5) are not unloading by a
  legion and need no yard. Each clan's seeded hub sector also holds a tier-1 Caravan Yard
  (`counterparties` `clan-seeding` rule 2a, E-A20). (Superseded: `fleet/spec-depot.md`'s round-4 default
  *"no"* for FQ1.)
- **Capture.** When the hub sector changes owner, each consignment stays its trader's: capture changes
  who owns the sector's own stock (`sector-yield`'s rule), not a third party's property. A consignment
  whose trader **is** the captor merges into the captor's located stock the same turn. Whether a
  trader can still move its consignment out is `Access` (`passage`) plus `logistics-flow`'s strand rule.
- Every change is a typed stock delta with an owner (ask E-A8 to `trade-foundation` `stock-deltas`),
  so the world-stock ledger reconciles consignments like any stock.

### 5. The capability flag, its wave and its bump (round 6 C1)

`trade.exchange` joins `trade-foundation` `world-stamp`'s closed capability vocabulary. On a world
whose stamp lacks it, no hub clears and no consignment is written; a legacy
world replays byte-identically (`world-stamp` acceptance).

**Corrected 2026-09-20 (reconciliation R-5).** This paragraph used to add *"and no `order-set` is
admitted"*. It does not: `order-set` arrives with `order-book` in exchange **wave 3**, which registers its
own flag `trade.exchangeOrders`. Gating a wave-3 command on this wave-2 flag would let a world stamped
between the two waves gain `order-set` mid-life — the R1 breach the stamp exists to prevent
([../landing-order.md](../landing-order.md) §1 R1, §10 R-5). `spec-order-book.md:53` and `:299` carry the
same correction.

**Owner decision C1 (2026-09-20):** *"One capability flag and one ruleset bump per wave. A world's rules never
change mid-life; the family keeps a single landing order."* The global audit's C1 found this module's flag
gating **ten** exchange modules across several waves, so a world stamped between two waves would have gained
behaviour mid-life. Applied here:

- **This module is exchange wave 2**, and it is the module that **registers** `trade.exchange`. The flag is
  registered in the change that lands this wave, and it grants **only what this wave ships**.
- **The wave takes exactly one `RulesetVersion` bump**, taken at landing, never pre-assigned, shared by every
  exchange module landing in it. This module does not claim "no bump" and does not mint a number.
- **A later exchange wave gets its own flag row and its own bump** (for example the treaty and bloc
  behaviour of `treaty-lifecycle`, or cross-world routes at tier 4). A module of a later wave never gates on
  `trade.exchange` alone for behaviour that wave adds.
- The whole order — wave, flag row, bump, golden re-bless — lives in one place:
  [../landing-order.md](../landing-order.md). Nothing here pre-assigns a number.
- **Grants throws on an unknown id** (`world-stamp` §2), so a module of a later wave never gates on a flag
  its own wave has not registered.

### 6. Template check

A template test asserts that every sector of every shipped template holds at least one slot of a kind the
loaded **trade-feature** row requires (`FeatureUnlock == trade`; round 6 C2 — keyed on the feature, not on a
withdrawn kind). If a sector fails, the template gains a slot under a **new
template version** (recorded on the stamp), never by editing the version old worlds were built from.

### 7. Tier reads — round 4

```
HubTier(world, sector)      = SectorFeatures.TierOf(sector, SectorFeature.trade)             // thin wrapper
TradeTier(world, faction)   = SectorFeatures.FactionTier(world, faction, SectorFeature.trade) // thin wrapper
```

Both delegate to `trade-foundation` `sector-features` ([spec](../trade-foundation/spec-sector-features.md)) and add no second building check (its interface table names them).

- **A split-owned building counts for nobody (round 6 S1).** *"A building whose sector and slot have different
  owners counts for nobody until one faction owns both."* That rule lives **once**, inside `TierOf` /
  `FactionTier`, and every gate in this cluster reads it from there: `HubTier`, `TradeTier`, `trade-access`'s
  admission, `treaty-lifecycle`'s `DiplomacyGate` delegation and `order-book`'s hub-sector test. No module
  here compares a slot owner with a sector owner itself, so a captured sector with an enemy-owned slot (or the
  reverse) can never make a hub clear for two factions or for none by accident — one answer, one read.

- **Active tier during an upgrade.** While a slot's upgrade to tier *t+1* is under construction, the
  hub keeps clearing and gating at tier *t* (the building is not torn down to be upgraded); the new tier
  counts from the turn its construction completes — `sector-features` §4 (*"an upgrade never switches a
  building off"*), relied on here because trade is the ladder where a lost turn of access would be felt.
- **Both reads are derived every step, never stored** (the `Access` rule, DESIGN-GATE §2.16 has no
  trigger set). A captured sector's hub counts for its new owner the same turn (`HubTier` reads the slot,
  `TradeTier` reads ownership).
- **Clans hold a seeded tier-1 hub.** `counterparties` `clan-seeding` places the clan's hub on its
  `Market` slot (its ask A9; legal since round 5 B1 lets the row stand on `Market`); this module requires
  that seeded structure to be the `Exchange` row at tier 1, **with a tier-1 Caravan Yard in the same
  sector** (round 5 B3, §4; seeded by `clan-seeding` rule 2a), so every clan can clear clan barter from turn 0, caravans can unload there,
  and the player's own Trading Post is the only missing half (`treaty-vocabulary` §5, "Whose buildings
  count"; round 5 B4: the trader's best Trade tier anywhere in that world is the one that counts).
- **Cross-world.** `rift-trade`'s Rift Anchor needs `TradeTier(world, faction) ≥ 4` in the same world
  (round 4 §B, Cross-world row); `rift-trade` reads this function and adds no second check.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The closed structure-kind enum and one-field-per-axis precedent | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-44`, `:71-78` |
| Built | Only rows with a `magnitudes` block load | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:55-66` |
| Built | The build pipeline, gated on slot kind | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:62-89` |
| Built | Construction state per slot | `gk-core/src/FusionRpg.Core/World/WorldState.cs:119-126` |
| Wiring gap | Market slot not offered by the client, no mechanism | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:508` |
| Real gap (round 5) | A row names exactly one slot kind; build, load validation and the siege board each compare one kind | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`; `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`; `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:411` |
| Wiring gap | Upkeep has no structure term yet | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:34-35` (`sector-yield` `structure-upkeep` adds it) |
| Real gap | The kind, the field, clearing capacity, consignment, the flag | — |

## Tunables

`data/tuning/trade.v{n}.json` — **created by `trade-foundation` `economy-report`** (global audit M8: one
creator per versioned file); every other spec, this one included, publishes `v{n+1}` and never writes
*"`trade.v1` (new)"*. Keys: `hub.clearingByTierMilli.{1,2,3,4}` (round 4; tier 1 = 1000, non-decreasing), `hub.crewNeededByTier.{1,2,3,4}` (round 5 X9; bearers, ≥ 1, non-decreasing), `hub.staffingCurve` (global audit m14; the `LabourCurve` points for staffing, a bounded 0..1000 ratio whose default reproduces the old linear ramp), `hub.marketSlotBonusMilli` (the map's `center.marketSlotBonusMilli`,
renamed to the player vocabulary *trade hub*, ideal §14b). `price.floorUnits` and `orderStepUnits` are
`price-curve`'s keys, scaled here. Clearing magnitudes are bands in empire-seed's tuning, never here.

## Acceptance (contract)

1. A hub built on any slot its row allows clears orders once active; under construction it clears
   nothing; a sector's capacity is the sum over its active hubs (asserted with 0, 1 and 2 hubs).
2. The same hub on a Market slot clears `(1000 + bonus)/1000` of its capacity elsewhere, to within the
   one final integer divide (asserted as `|C_market × 1000 − C_elsewhere × (1000 + bonus)| < 1000 + bonus`).
3. Capacity at the pin sector (`scaleMilli = 1000`) with full staffing equals the row's
   `ClearingValuePerTurn`; it grows with the sector's content scale and is computed by the same scale
   function the sector's goods read (a test fails if either side is given a different scale).
4. (Rewritten by round 6 C2) A row with `FeatureUnlock == trade` and `ClearingValuePerTurn ≤ 0`, and any
   other row with it `≠ 0`, are load rejections naming the row. No row carries a `StructureKind.Exchange`
   (the member does not exist), and the trade row loads under the neutral `Feature` kind.
5. Consignments: an empty list writes no canonical row (legacy hash unchanged); occupancy counts
   consignments; a negative quantity throws; capture leaves a third party's consignment unchanged and
   merges the captor's own.
6. A world without `trade.exchange` never clears, never writes a consignment, and replays
   byte-identically.
7. `Buildable = true` on the Market slot changes no `StateHash` (the flag is not canonical).
8. **Tiers (round 4).** `HubTier` is the highest active tier in the sector and 0 with no active hub;
   `TradeTier` is the highest over owned sectors; a hub mid-upgrade reads its old tier until the upgrade
   completes; capture moves `TradeTier` to the captor the same turn (criterion 4 carries the load rule after
   round 6 C2). **S1:** a hub whose sector and slot have different owners reads tier 0 for **both** factions,
   and the assertion is `sector-features`' — this module's test only proves it reads `TierOf` rather than
   deciding it.
9. Capacity at tier *t* equals `ClearingValuePerTurn × clearingByTierMilli[t] / 1000` at the pin
   (Acceptance 3 per tier), non-decreasing in *t* (a load check on the tuning).
10. **Slot kinds (round 5 B1).** The Trading Post builds on a `Wildland` and on a `Market` slot and is
    refused `build.wrong-slot-kind` on any other kind; a row without `requiredSlotKinds` loads as
    `[requiredSlotKind]` and builds exactly where it did (every existing row, asserted over the real
    corpus, never by count); `WorldValidation` accepts a saved Trading Post on either kind.
11. **Yard at a foreign hub (round 5 B3).** No consignment changes from a caravan leg at a hub sector
    where `fleet`'s `ForeignSite.Of` returns no site (asserted here over the consignment state; the
    predicate's own tests are `fleet` `depot`'s); a lane-flow arrival is unaffected.
12. **Staffing (round 5 X9).** `staffingMilli` is 0 with no bearers, `LabourAt × 1000 /
    crewNeededByTier[t]` below the need, and exactly 1000 at or above it; it reads the bearer count
    from `Crew.LabourAt` and nothing else.
13. **Range (audit 2026-09-20).** At a sector scale taken from `Θ` = 10,000 with tier 4, the Market bonus
    and full staffing, `ClearingCapacity` returns the exact value (computed independently with
    `BigInteger` in the test) and does not throw; a value past `long.MaxValue` throws rather than wraps.
14. **Canonical consignments (audit 2026-09-20).** Applying the same consignment deltas in two different
    orders yields byte-identical canonical text and the same `StateHash`.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Hub/` (new), trait `core.world-trade.hub`, boundary row
  `core-world-trade-hub`; canonical/hash tests beside the existing world hash tests.
- Seedsmith is untouched by this module (the role tuple is empire-seed's).
- Crosses `StructureCatalog` (shared by structures, siege, loam): run the focused boundary plus the
  structure catalog tests `verify-change.ps1` selects for `StructureCatalog.cs`; not the full suite.

## Hard edges

- **Identity is not behaviour.** Rows and roles are empire-seed's; no hub number is typed into a seed
  (D-E2).
- **No `StructureKind` member (round 6 C2).** This module used to widen a closed C# enum; it no longer does.
  The neutral `Feature` member lands once, with `StructureDef.FeatureUnlock`, in `trade-foundation`
  `sector-features`, and the family's landing order records that it precedes the rows
  ([../landing-order.md](../landing-order.md)).
- **Wave and ruleset bump (round 6 C1):** exchange **wave 2**, which registers `trade.exchange` and takes the
  wave's **one** bump, at landing. A later exchange wave gets its own flag row and bump (§5).
- **`SlotTypeCatalog.cs` is world-map's file (global audit m15/X-14):** the C4 display rename is one ask
  covering the `market` and `vault` slots, not an edit here (§3).
- **One capacity axis per stock family.** Consignments never get their own capacity field.
- **No `f(level)`.** Capacity reads the one content scale, never a per-level table.

## Dependencies

- Upstream: `trade-foundation` `world-stamp` (flag), `stock-deltas` (owner dimension, E-A8);
  `sector-yield` `warehouse-axis`, `essence-loop-read`, `located-stock`; `empire-seed` `exchange-role`,
  `trade-structure-rows`, `band-reader` (E-A2); `fleet` `crew` (soft — staffing reads 1000 until it lands);
  `trade-foundation` `sector-features` (feature, slot tier, upgrade — answered E-A14).
- Downstream: `order-book`, `settlement-payment`, `logistics-flow` (consignment as source/destination,
  E-A5), `fleet` (unload/load at a foreign hub), `counterparties` `conquest-consequences` (hub closure);
  `trade-access` (tier gate), `rift-trade` (tier 4 for the Rift Anchor), `trade-ai` `ai-trade-buildings`,
  `trade-surface` (`trade-panel`, `trade-unlock`).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `Hubs.IsHubSector(world, sectorId)`, `Hubs.ClearingCapacity(world, sectorId) : long` | `order-book` |
| `Hubs.ScaledFloor / ScaledStep(world, sectorId)` | `order-book` → `price-curve` |
| `WorldSector.Consignments` + `Consignment.Add/Remove` (checked, never negative) | `settlement-payment`, `logistics-flow`, `fleet` |
| `Hubs.HubTier(world, sectorId) : int`, `Hubs.TradeTier(world, factionId) : int` | `trade-access`, `rift-trade`, `trade-ai`, `trade-surface` `trade-wire` |
| `StructureDef.RequiredSlotKinds` (round 5 B1) | `BuildResolver`, `WorldValidation`, the siege board, the client DTO |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: structures, world map (build, templates), economy (capacity), power (PS-5), caps.
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §7.1, §7.6, §14b; sector-yield-map §2.1-§2.4, §2.9;
    empire-seed-map §5.4 (point 3), §5.5, §5.12; fleet-map (crew, trade-route-order, Q1, A6);
    decisions.md rows :147-:148.
[x] decisions.md :147 (corpus owner) and :148 (exchange role) respected.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: StructureCatalog enum/fields/Enum.Parse, BuildResolver gate, SlotTypeCatalog
    Buildable readers, WorldSlot construction fields, template Market slots.
[x] Surrounding sections read (StructureCatalog class doc; BuildResolver header).
[x] No constraint claimed without a run: "no golden moves" is stated as Acceptance 5-7, to be tested.
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC5, EC7, EC8, EC9 in the map.
[x] No population count pinned (hub counts in tests are fixture inputs, not assertions on content).
[x] No event-refreshed cache (capacity is computed per step).
[x] No ordering criterion.
[x] No actor magnitude.
[x] No SOLID-violating path: one build pipeline, one warehouse axis, one scale read.
[x] Registry row: no new rule beyond the load validations, which are their own guard.
[x] Round 4 reconciliation (2026-09-19): decisions-round-4.md read whole; the hub is the Trade ladder,
    tiers are sector-features' slot tiers; per-tier clearing is tuning keyed by tier (EC5 kept: no
    level curve); the kind stays for behaviour and is never a gate (fleet X-F1). Verified a slot carries
    no tier today (WorldState.cs:119) and an occupied slot refuses a build (BuildResolver.cs:71).
[x] Round 5 (2026-09-20): R5-A/R5-X read whole. B1 (multi-slot field; every one-kind reader found by
    grep and cited: BuildResolver.cs:84, WorldValidation.cs:411, BasicAttack.cs:267,
    BattleEffects.cs:363, WorldDtos.cs:412, WorldEndpoints.cs:488), B3 (fleet depot ForeignSite.Of is the
    one check; no exchange-side duplicate), C4 (slot Name
    only, SlotTypeCatalog.cs:74), X9 (staffing term and key here; Crew.LabourAt is a count), X1 (all
    gates through sector-features). WorldEndpoints Buildable line re-pointed :500 -> :508.
[x] Audit 2026-09-20 (independent): the clearing product overflowed long near Θ≈190 — now a BigInteger
    intermediate, divided once, narrowed checked (net6.0 has no Int128; FusionRpg.Core.csproj:3);
    consignment rows given an ordinal canonical order; Acceptance 2 stated to within the final divide.
```

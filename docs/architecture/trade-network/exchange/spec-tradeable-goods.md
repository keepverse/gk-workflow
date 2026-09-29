# Spec: `tradeable-goods`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 2 of the [exchange map](../exchange-map.md) (wave 1; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §3 principles 6–8, §7.3.
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

One **closed** table that says, for every good id, whether it may change hands between factions and
on what terms. Admission and settlement both read it, so a forbidden trade is refused with a named
reason before anything moves, and a trade that settles can never carry loam, recruits, souls-as-goods
or a world stock into a banked stock. The module also carries the three registry and document changes
the table requires — **as requirements on the change that lands it, not edits made in this spec
session** (see *Required amendments*).

## Scope and non-goals

In scope: the trade-class vocabulary; the per-good class lookup; the two **credit pools** the classes
imply; the admission and settlement checks; the required amendments to the materials doc, one code
comment and two registry rows.

Not in scope: prices (`price-curve`); who may trade where (`trade-access`); what a legion-equipment
piece is (`legion-build`); how a located good banks (`sector-yield`). Unique items and creatures are
not goods in v1 (ideal §7.3, §12).

## Design

### 1. Four classes — a closed vocabulary

| Class | Goods | May appear |
|---|---|---|
| `tradeable` | `essence.*`, `shard.*`, `substrate.*`, `catalyst.*` (all three verbs), legion-equipment pieces | Either leg of a fill, in the **bankable** credit pool |
| `world-barter-only` | `rubble`, `ironwork` | Either leg of a fill, in the **map-bound** credit pool only |
| `payment-only` | the soul wallet | Only as the player's soul top-up in the bankable pool; never as a good |
| `never` | `loam`, `recruit`, any located soul good | Nowhere; an order naming one is refused at admission |

The class count (4) is pinned in a test **because it is a closed vocabulary this code owns**: a fifth
class is a reviewed change, and the pin says so in its message. Which goods are in each class is a
join against the material catalog and the located-goods catalog, never a count.

- **`temper` is tradeable (contradiction EC3).** The registry lists three catalysts
  (`docs/architecture/empire-resource-ssot.md` §3, *catalyst.{forge,temper,flux}*); the ideal's table
  names forge and flux only. Temper has no salvage lock (salvage returns `enh / 3`,
  `docs/architecture/item/ssot-materials-crafting.md` §5.1), so it follows the banked-material rule:
  tradeable. Only forge and flux need the lock amendment below.
- **Located souls are `never`.** `sector-yield`'s located-goods catalog maps a located good to souls
  when a structure yields souls (`sector-yield-map.md` §2.1). Buying such a good and banking it would
  turn goods into souls through trade, which invariant I1 forbids. Souls reach the wallet from the map
  only by banking a sector's own yield.
- **Legion equipment is `tradeable` on one condition.** Pieces have no banked form
  (`sector-yield-map.md` §2.10), and they are made from goods (`legion-build-ideal.md` §6.7). If any
  `legion-build` recipe consumes a world stock (`rubble`, `ironwork`, `loam`, `recruit`), pieces become
  `world-barter-only`, because selling them for bankable goods would carry world production into an
  account path (`empire-resource-ssot.md` §4 rule 5). The class is computed from the recipe catalog at
  load, not authored; filed ask E-A6.

### 2. Two credit pools

A trader's fills at one hub in one turn are two separate baskets:

- **Bankable pool:** `tradeable` goods, plus the player's soul top-up.
- **Map-bound pool:** `world-barter-only` goods, plus legion equipment when the condition above
  makes it map-bound.

Value earned by selling in one pool can pay only for buying in the same pool (`settlement-payment`
§Design 2). This is what "world-to-world barter only" means as code: a unit of rubble can end up as
ironwork or as another faction's rubble, never as essence. The reverse direction is closed too, so the
rule is symmetric and easy to state.

### 3. Where the checks run

- **Admission** (`WorldCommandAdmission`, `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17`):
  an `order-set` naming a `never` good is refused `order.good-never-trades:{goodId}`; naming souls as
  a good is refused `order.souls-payment-only`.
- **Settlement:** a fill's two legs must share a pool; a mismatch is a thrown invariant (an order that
  reaches settlement with a cross-pool pairing is a code defect, not a player error).

## Required amendments (land in the same commit as this module's code, DESIGN-GATE evidence rule 6)

This spec session does not edit other programs' documents. The change that implements this module
must include:

1. **Catalyst lock (item program).** Amend the bottleneck paragraph of
   `docs/architecture/item/ssot-materials-crafting.md` §7.3 (*"The bottleneck is `catalyst.forge` and
   `catalyst.flux`, deliberately … cannot be accelerated by inventory management"*) and the matching
   comment at `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48`: trade becomes a second,
   **priced** catalyst source, gated by a hub and `Access`; **salvage stays at never** for forge and
   flux (§5.3's table is unchanged). Owner ruling, round 3 (ideal §7.3).
2. **Registry, `catalyst.*` row** (`docs/architecture/empire-resource-ssot.md` §3): Faucets gain
   *trade (priced; a hub and `Access`)*; Conversions gain *located goods ⇄ located goods at a hub, lossy
   (spread, fee, walk), rate-capped (clearing capacity), gated (hub, `Access`)*; crafting stays the
   named sink (P1).
3. **Registry, `souls` row:** Conversions gain *souls → located goods, one way, lossy, rate-capped,
   gated*; the row states that no goods → souls conversion exists or may be added.
4. **Registry, legion equipment:** the row is `legion-build`'s (`sector-yield` `legion-equipment-stock`
   lands it); this module adds only its trade class to that row's Conversions cell.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The closed material catalog the table joins against: shard ×10, substrate ×8, essence ×6, catalyst ×3 | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:57`, `:61-68` |
| Built | The write boundary refuses an unknown material id | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:187-188` |
| Built | The admission gate every order passes | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-20` |
| Built | The catalyst lock this module amends | `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48` |
| Real gap | The table, its pools, its checks, the amendments | — |

## Acceptance (contract)

1. Every good id resolves to exactly one class; the lookup is total over the material catalog, the
   located-goods catalog and the world stocks, and throws on an unknown id.
2. No id of `loam`, `recruit` or a located soul good is ever in a class other than `never` (asserted by
   name, because these are the invariant's subjects, not a population).
3. An order naming a `never` good or naming souls as a good is refused at admission with the reasons in
   §Design 3; an old log containing no `order-set` replays byte-identically.
4. Settlement refuses a cross-pool pairing by throwing; a property sweep over generated baskets finds no
   fill whose value earned in one pool pays for a buy in the other.
5. Legion equipment's class is `world-barter-only` whenever any loaded recipe consumes a world stock,
   and `tradeable` otherwise — tested with a fixture recipe of each shape.
6. The four amendments above land in the same commit as the code; `audit-doc-citations.py --scope` on
   the two amended documents reports no HIGH.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Goods/` (new), trait `core.world-trade.goods`; one boundary
  row `core-world-trade-goods` in `gk-core/scripts/verification-boundaries.v1.json`.
- Admission tests in the same folder drive `WorldCommandAdmission.Admit` directly.
- `verify-change.ps1 -Paths` with the code, the amended docs (it runs the citation audit on changed
  `.md` files) and the test files.

## Hard edges

- **No path turns goods into souls.** No class, pool or conversion lets a fill credit souls.
- **Loam never trades** (`docs/architecture/decisions.md:108`; `empire-resource-ssot.md` §4 rule 4).
- **World stocks never feed an account path** — the map-bound pool is the mechanism, not a guideline.

## Dependencies

- Upstream: `goods-valuation` (same wave; its key set is checked against this table);
  `sector-yield` `located-goods-registry` (the located catalog and the located-material class,
  filed ask E-A4); the **legion piece catalog**, whose producer is named once (global audit m10):
  `LegionPieceDef` is produced by **`empire-seed` `legion-bands`** from the legion seed rows
  (`empire-seed/spec-legion-bands.md`), and `legion-build` `legion-equipment` owns the slot vocabulary, the
  recipes and the production rule (E-A6). This table reads the piece ids from the producer and the
  tradeability rule from neither — it declares it here.

**Closed-cycle landing note (global audit M1).** `goods-valuation` ↔ `tradeable-goods` is a cycle inside this
sub-program: this table checks its key set against `goods-valuation`, and `goods-valuation` prices only what
this table admits. **One line closes it:** `goods-valuation` lands **first**, keyed by good id over the
registry (it needs no tradeability class to price a good); `tradeable-goods` lands next and its acceptance
asserts the two key sets agree. Neither is written against the other's unlanded code, and both are in the same
wave with one flag and one bump (round 6 C1), so no world ever sees one without the other.
- Downstream: `order-book` (admission), `settlement-payment` (pools), `rift-trade` `crossing-goods`
  (reads the `never` class for its own table).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `TradeGoods.ClassOf(string goodId) : TradeClass` | `order-book`, `settlement-payment`, `rift-trade` |
| `TradeGoods.PoolOf(string goodId) : CreditPool` (`Bankable`, `MapBound`) | `settlement-payment` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy (registry, P1, P5), items (catalyst lock), world commands.
[~] Session boundary: trade-network-idea-20260919; new file only. session-boundary-check.py exits 1 on
    the broad-lane crossings that record already notes.
[x] Read this session: empire-resource-ssot (whole), economy-principles (whole),
    ssot-materials-crafting §3, §4.3, §5, §7.3, §8.6, ssot-rarity §3.3/§4.3, legion-build-ideal §6.7,
    sector-yield-map §2.1/§2.10, trade-network-ideal §3, §7.3.
[x] decisions.md:108 respected; decisions.md "Legion equipment scope" row respected (counted stock).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: MaterialCatalog, SalvagePolicy comment, admission gate read directly.
[x] Surrounding sections read (materials §5.3 table, §7.3 whole).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC3 in the map; amendments listed as requirements, not made here.
[x] No population count pinned; the 4-class pin is a closed vocabulary with its reason.
[x] No event-refreshed cache.
[x] No ordering criterion.
[x] No actor magnitude (legion equipment's stats reach ActorHub through legion-build, never here).
[x] No SOLID-violating path: one table, read by admission and settlement alike.
[~] Registry row: "no fill crosses pools" gets a guard row with the property test that enforces it.
```

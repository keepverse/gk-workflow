# Spec: `legion-equipment-stock`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.10 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Owner ruling on legion equipment: [../../legion-build-ideal.md](../../legion-build-ideal.md)
§6.7 (*"Pieces are **located goods**: they sit in the producing sector's warehouse, travel by
logistics, can be traded between empires, and are fitted to stacks where the legion stands"*). Sibling
module: [../../legion-build-map.md](../../legion-build-map.md) §5.14 `legion-equipment`.

## Objective

Make a legion-equipment piece something a warehouse can hold: a counted `long` stock per (sector,
piece id) in the same located stock, under the same capacity, halt and stock-delta rules as every other
located good, so it can later travel (`logistics-flow`), be traded (`exchange`) and be fitted
(`legion-build`). 3,000 pikes are one stock entry, not 3,000 items (§6.7: *"no per-unit item rows"*).

## Scope and non-goals

**In scope:** the `LegionPiece` members of `LocatedGoodCatalog`, their capacity rule, their no-bank rule,
their registry row.

**Not in scope:** the piece catalog and its stats (`legion-build` mechanics; `empire-seed` seeds);
production recipes and the building that runs them (`legion-build`, on the legion-equipment building —
round 4 §B: **Workshop → Armory → Foundry**, tier variants of one row, where *"the tier is the best
legion-equipment tier the sector can produce"*, read through `trade-foundation` `sector-features`
`TierFor(sector, faction, legion-equipment)`, round 6 S1); fitting, casualties and the ActorHub contribution (`legion-build` `legion-equipment`,
through `general-member-hub`); carrying pieces between worlds (world-continuity cargo).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| The located stock, its one writer and its canonical form | `spec-located-stock.md` |
| The catalog's `LegionPiece` kind, with no members yet | `spec-located-goods-registry.md` §Design 4 |
| The one credit function, which a recipe's output goes through | `spec-production-halt.md` §Design 1 |
| A candidate production row: `workshop`, `multiply` role, identity only | `gk-data/packs/fusion/data/seed/structures/multiply/workshop.json` (no `magnitudes` key); `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |

### Wiring gap

None.

### Real gap

No piece catalog exists yet (`legion-build` owns it); nothing can hold a piece.

## Design

### 1. Piece ids join the catalog

`LocatedGoodCatalog` gains one `LegionPiece` entry per id in `legion-build`'s piece catalog, with
`BankedId = null`. The id set is **host-injected** (Core never reads a file, `PRINCIPLES.md` §5): the
host loads `legion-build`'s catalog and passes its ids to the located catalog at startup, before any
world steps. Piece ids must be disjoint from material ids and `souls`; a collision is a load rejection.

### 2. Same warehouse, same capacity

Pieces are counted in the same `LocatedStock`, and `LocatedStock.Total` — and therefore
`SectorWarehouse.Occupancy`, which is what `production-halt` compares to `SectorWarehouse.EffectiveCapacity`
(`spec-warehouse-axis.md` §3) — includes them. **No fourth capacity axis.** One piece weighs one
unit, like every located good (`spec-warehouse-axis.md` §Design 4).

### 3. No banked form

Pieces never bank (`banking-fact` skips `BankedId = null`). A banked form would make pieces an
account-scoped material fed by world production, which the registry forbids for map-scoped production
(`empire-resource-ssot.md` §4 rules 5 and 5b).

**Crossing worlds (round 6 S2, W1, W2).** A piece leaves its world by exactly two paths, and neither is a
new one here:

- **A `rift-trade` route** — pieces are on the closed crossing table (`../rift-trade/spec-crossing-goods.md`).
  *"Trade goods cross only through rift-trade routes"* ([../decisions-round-4.md](../decisions-round-4.md)
  Round 6 S2), so this is the path for moving equipment between worlds as **trade**.
- **An advance, inside its weight limit** — a piece on a legion that advances is legion cargo, and the
  advance is *"a weight limit, like a spacecraft's payload"*: Σ(unit count × that unit type's carry
  capacity), read from the `world.carry.capacity` derived channel, with **units and goods drawing on the
  same limit** (Round 6 W1). `world-continuity` `advance-carry` owns that arithmetic; this module owns
  nothing about it and states no second capacity.

Import/export through the rift gate and the gate's own weight limits are **`world-transit`**'s, a named
future program (Round 6 W2). No rule here anticipates it.

### 3a. When local stock runs short (round 6 CQ2)

Fitting a legion draws pieces from the warehouse where it stands. When that warehouse is short, the
shortfall **may be paid from banked goods** — *"Legion equipment and doctrine upkeep may draw on banked
goods when local stock runs short — the same rule for the player and every AI, so no handicap"*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 CQ2). Two boundaries this module holds:

- The draw is **not** a banked form of a piece (§3 stands). It spends banked **goods** — the material bill —
  and the piece is produced or fitted through the ordinary located path; nothing account-scoped ever holds a
  piece.
- The sink lives where the banked balance lives: `counterparties` `empire-goods-sinks` for an AI empire's
  treasury, the player's wallet for the player, symmetric by construction. The **legion-build side** — which
  fitting and which doctrine upkeep may fall back, and in what order — is an **ask to `legion-build`**
  (`legion-equipment`, `legion-doctrine`), not a rule this module writes.

### 4. Production enters through the one credit function

A recipe's output (`legion-build`) is credited with `LocatedProduction.Credit`, so a full warehouse
halts piece production exactly like any yield, and every piece made is a `produce` stock delta. A
recipe's input goods leave through `LocatedStockOps.Add` with their own factKind. This module only
guarantees both calls exist and are the only paths; the recipe rule is `legion-build`'s.

### 5. The registry row — one row, not two

Legion equipment stock is a new quantity and owes a row in `empire-resource-ssot.md` §3 with P4 (goods ×
building time is the bottleneck) and P6 (fitting stacks versus trade) in the change that ships it.
`legion-build-map.md` §5.14 also claims that row. **There is one row.** Whichever of the two modules
lands first writes it; the other amends it. This module owns its *Class* (Located good) and *Held by*
(sector warehouse) columns; `legion-build` owns *Sinks* (fitting, casualties) and the power column.

## Tunables

None here. Piece stats, recipe inputs and build time are `legion-build`'s and `empire-seed`'s.

## Numeric types

`long` counts, `checked`, through `LocatedStockOps.Add`. Counts are not content-scaled (Flat loop,
`spec-essence-loop-read.md` §Design 3): a piece is an object, its power is its stats.

## Acceptance (contract)

1. A piece id outside `legion-build`'s injected catalog is refused by `LocatedStockOps.Add` and by
   `LocatedStock.Unpack`.
2. Piece ids and material/souls ids are disjoint; an injected collision is a load rejection.
3. Pieces count toward `LocatedStock.Total` and `SectorWarehouse.Occupancy`: a warehouse full of pieces
   halts every yield in that sector, and a warehouse full of essence halts piece production.
4. `banking-fact` never decrements a piece; a bank point holding pieces keeps them.
5. The registry row exists once, with Class *Located good*, P4 and P6 stated.
6. A piece's stock changes only through `LocatedStockOps.Add` (the source scan from `located-stock`
   covers it).
7. **Transit loss row:** pieces read one family row `goods.legion-piece.transitLossMilli` in `lane-loss`'s
   key family (`logistics-flow/spec-lane-loss.md` Tunables), not one row per piece id — piece ids are
   seeded content, so a per-id row would make every new piece seed a tuning republish.

## Test plan and verification boundary

`tests/FusionRpg.Core.Tests/World/Goods/LegionPieceStockTests.cs` (new): items 1–4, 6, with a synthetic
injected piece catalog (the real one does not exist yet).

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LegionPieceStockTests.cs',
  'docs/architecture/empire-resource-ssot.md') -Session <active-session-id>
```

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs     MODIFIED — injected LegionPiece ids
gk-core/src/FusionRpg.Server/Program.cs                          MODIFIED — host injects the piece ids
docs/architecture/empire-resource-ssot.md                MODIFIED — one row (or amend legion-build's)
tests/FusionRpg.Core.Tests/World/Goods/LegionPieceStockTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** one warehouse, one capacity, one credit path, one registry row.
- **Ask first:** a banked form for pieces; a separate piece capacity.
- **Never:** a per-unit item row for a piece; pieces in a Data-side store that `Step` cannot read.
- **Hard edge — contradiction with `legion-build-map.md` §5.14.** That map says every inventory scope
  uses the one ownership root `rpg_item`/`rpg_item_stock` and that pieces sit in *"a sector's storage"*.
  `rpg_item_stock` is Data-side and unhashed (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:102-108`);
  `logistics-flow` moves goods inside `TurnEngine.Step`, which may read only hashed world state (P13,
  umbrella invariant 5). The ideal it implements (§6.7, quoted above) puts pieces in the warehouse. This
  spec follows the ideal. **Ruled 2026-09-20 (round 5 X4):** legion equipment is stored in the hashed
  sector warehouse (this module's located stock), never `rpg_item_stock`. `legion-build`'s
  `legion-equipment` spec re-points its storage root; this spec does not edit that map.

## Dependencies and interface

**Depends on:** `located-stock`, `production-halt`, `warehouse-axis`; external `legion-build` (piece
catalog ids).

| Exposed | Consumer |
|---|---|
| Pieces as located goods | `legion-build` (fitting consumes from the warehouse where the legion stands), `logistics-flow`, `exchange` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy registry, world state (located stock), legion equipment scope (storage only).
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: legion-build-ideal §6.7; legion-build-map §5.14; empire-resource-ssot §4-§5;
    the sector-yield map §2.10.
[x] decisions.md: scoped inventory row consulted through legion-build-map's citation; registry row.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: rpg_item_stock's keying; workshop is identity-only.
[x] Surrounding sections read: legion-build-ideal §6.7 whole.
[x] Constraints tested, not assumed: none claimed.
[x] No §2 invariant contradicted. Named contradiction with legion-build-map §5.14, recorded, not resolved
    by editing that map.
[x] Corrections propagated to the session report.
[x] No population pinned.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] ActorHub: pieces' stats reach the Hub through legion-build's general-member-hub; this module holds
    counts only.
[x] No SOLID fork: one stock, one capacity, one credit path.
[x] Registry row: one row, shared authorship stated.
```

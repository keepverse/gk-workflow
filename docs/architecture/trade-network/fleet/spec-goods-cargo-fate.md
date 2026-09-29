# Spec: `goods-cargo-fate`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`). Every `file:line` below was opened
in this session. Module id `goods-cargo-fate`, row 7 of the [fleet map](../fleet-map.md) (wave 3; depends
on `interception`, `carried-goods`, and the `cargo-fate` **rule** of `scoped-inventory-hierarchy`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §14b (*"Goods on a legion that loses a battle
follow `cargo-fate`"*), §7.6 (*"Goods in transit belong to the buyer"*; *"A counterparty captured
mid-route — goods not yet delivered follow the same fate rules as cargo on capture"*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Goods that leave a legion involuntarily — because it was destroyed, starved, or lost bearers in a fight —
become a **goods cache** at the legion's last place, a sector or a lane. Any legion standing there with
free goods capacity takes from it during the Logistics phase; an abandoned cache fades. This is
`cargo-fate`'s rule (a) — *"a destroyed legion's cargo becomes a revisit-lootable cache at its last-known
place — a sector … or a lane"* (`scoped-inventory-hierarchy-map.md` module 4) — carried by hashed world
state instead of Data-side item rows, because goods are hashed.

This module fills `carried-goods`' removal seam (replacing its wave-1 "lost" body) and receives
`interception`'s spill.

Success looks like: a caravan destroyed on a lane leaves a cache on that lane holding exactly what it
carried; the interceptor, if it has bearers, picks the goods up in the same turn's Logistics phase; if no
one comes, the cache shrinks every turn until it is gone; nothing in a cache ever reaches a wallet except
by being carried to a bank point.

## Locked anchors

- **The rule is `cargo-fate`'s; the carrier is ours.** Item cargo moves to a corpse cache Data-side, after
  `Step`, before the entity row is deleted (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:335-356`;
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:5-19,47-49`). Goods cannot take that path — they are
  hashed world state that banking and lane flow read inside `Step` — so the same rule runs inside `Step`
  on a hashed cache. No Data-side table, no second cache table for items, no call into item code.
- **Same place rule.** Last place = `AtSectorId` or `OnLaneId`, exactly one of which is set
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:292-295`); the item path relies on the same invariant
  (`RpgStore.WorldGraphDiff.cs:339-343`).
- **No empty header.** Nothing carried → no cache (the item rule's *"no empty cache row is ever created"*,
  `RpgStore.CargoFate.cs:32-33`).
- **A cache is not a bank point and not a warehouse.** Banking reads warehouses at bank points
  (`sector-yield` `banking-fact`); a cache on a bank-point sector banks nothing until a legion carries its
  goods into that sector's warehouse.
- **Contested capacity splits pro rata, never by faction id** (principle 10; ideal §14b).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `cargo-fate`'s item rule and place kinds (`world_sector`, `world_lane`) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:5-19`; call site `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:344-354` |
| Lanes are durable, revisitable world objects | `gk-core/src/FusionRpg.Core/World/WorldState.cs:246-263`; `docs/architecture/scoped-inventory-hierarchy-map.md` module 4 |
| The two in-`Step` removal sites and `carried-goods`' seam at both | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:33-35`; `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:134-151`; `spec-carried-goods.md` §5 |
| Conditional canonical rows for sparse state | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:123-128` |
| The item cache has its own claim command, `claim-cache`, resolved Data-side after `Step` | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:113-119` |

### Wiring gap

None.

### Real gap (this module closes it)

The hashed goods cache, its creation from removal and spill, the Logistics-phase claim, fade, and the
cache fact tokens.

## Design

### 1. State

```
WorldState.GoodsCaches : IReadOnlyList<GoodsCache>      ordered by (PlaceKind, PlaceId)
GoodsCache(GoodsPlaceKind PlaceKind, string PlaceId, IReadOnlyList<CachedGood> Goods)
CachedGood(string GoodId, long Qty)                      // a cache is a holder; load is measured on pickup
GoodsPlaceKind ∈ { Sector, Lane }                        closed enum
```

At most **one cache per place**: new goods at a place with a cache merge into it (sum per good). This
keeps the state sparse and makes "the cache at lane L" a single thing to claim and to show. Canonical
form: one conditional `goods-cache` row per (place, good) with non-zero quantity, emitted after
`carried-goods`' `entity-goods` rows. Persistence: one packed row per place in a new
`rpg_world_goods_caches` table, written through the diff writer only when it changes
(`logistics-canonical`'s packed-row rule); SQL only in `FusionRpg.Data`.

### 2. Creation

`CarriedGoods.OnEntityRemoved` (the seam at every removal site) gets this body for causes `battle` and
`starved`: merge the entity's whole pool into the cache at its last place; write `goods-cache.created` (or
`.grown`) with the cause. Cause `departed` (`world-continuity` `advance-carry`, `spec-carried-goods.md` §5)
never creates a cache: a legion that leaves the world on purpose is not a loss on the map, and its goods
follow **round 6 S2, W1 and W2**, which answer what was owner question FQ3: trade goods cross worlds only by
a `rift-trade` route, an advance carries only what its weight limit allows — Σ(unit count × that unit type's
carry capacity) from `world.carry.capacity`, units and goods on one limit — and anything over the limit is
refused at `depart` admission (`spec-carried-goods.md` §5). Whatever still reaches this seam as `departed` is
stripped as `lost`, never cached and never silently carried across. `interception`'s `Spill` calls the same `GoodsCache.Place(world, place, goods)`
function. Both in the same `Step` statement that removes or reduces the legion — the goods are never in
two places and never in none.

### 3. Claim (Logistics phase, fleet step, after arrivals, before banking)

For each cache in order, the claimants are every non-`Guard` entity at its place (`AtSectorId == sector`,
or `OnLaneId == lane`) with free load capacity > 0. The place's sector for `loadOf` is the sector itself,
or a lane's `From` sector (the convention stated once, here). Then, for each good in id order:

```
fitQty_i  = largest q with loadOf(q, place, good) ≤ free_i         // claimant i's room, in quantity
take      = min(cache[good], Σ fitQty)
share_i   = take × fitQty_i ÷ Σ fitQty    (integer; remainder one unit at a time by entity id, ordinal)
CarriedGoods.Load(share_i) with the cache as holder; recompute free_i
```

- **Any faction** may claim, including the force that destroyed the caravan — that is *capture
  mid-route*. Pro rata by free capacity: the split never reads a faction id (principle 10).
- **Automatic**, no command: a legion standing on a cache with room picks it up. The Data-side
  `claim-cache` command stays the item cache's (`WorldCommand.cs:113-119`); goods caches do not use it.
- Guards are slot state that project nothing (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:18-29`)
  and do not carry; they are excluded.
- Independent of the order entities appear or were created (the world's entity list is id-ordered;
  tested by constructing it in different orders).

### 4. Fade

After claims, every cache loses `ceil(qty × cache.fadePerTurnMilli / 1000)` of each good (a bounded
ratio, commented as such; rounding **up** so a non-empty cache always shrinks and every cache ends in
finitely many turns). Faded goods are a **sink**: they appear in no balance, ledger credit or other
cache; `stock-deltas` records them with factKind **`fade`** (a new world-scope kind, ask A14). An emptied
cache is removed. A tuning value of 0 is a load rejection — a cache must end, or it is a permanent free
stock (P1). *(Audit 2026-09-20: the first draft used `loss`, `lane-loss`'s kind. The economy report's P6
sink-share line groups by `(stock, factKind)` (`../trade-foundation/spec-economy-report.md`), so borrowing
`loss` would report cache fade as lane attrition and hide whether either sink dominates.)*

**Ledger holder (audit 2026-09-20).** A cache is a holder the stock-delta and ledger grammars cannot name
today: `StockHolderKind` is `{ Sector, Entity }` plus the `Faction` widening, and a ledger holder prefix is
`s:`/`e:`/`f:` (`../trade-foundation/spec-stock-deltas.md` §Design, `../trade-foundation/spec-ledger-keys.md`
§4a). A lane cache fits none, so the economy report's "Σ goods everywhere" reconciliation could not see it.
Ask A14 widens both with one member, `Cache` / `c:<placeKind>:<placeId>`, in this module's implementing
change. Creation (legion → cache) and claim (cache → legion) then record `carry` on both holders, and fade
records `fade` on the cache.

### 5. Ownership in transit (ideal §7.6)

Goods on a legion belong to that legion's faction. Nothing in this module — or anywhere in fleet — reads
the seller or a counterparty to decide the fate of goods already carried: a counterparty captured
mid-route touches neither a caravan's pool nor a cache it left. Goods still in a captured site's
warehouse change hands with the sector (`sector-yield`'s rule), not here.

### 6. What never happens

- No path from a cache credits a wallet, a treasury or a banking fact directly; a cache's goods reach a
  wallet only by being carried into a bank point's warehouse and banked by `banking-fact`.
- `rubble` and `ironwork` in a cache stay world stocks; they are never bankable from anywhere.
- A cache never grows except by §2's creation; fade and claims only shrink it.

### 7. Facts

Added to `FleetFacts`: `goods-cache.created`, `goods-cache.grown`, `goods-cache.claimed`,
`goods-cache.faded`, `goods-cache.gone`. Each names its place and (for claims) the claimant, and carries
an `Audience` so fog projection stays correct (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:12-32`).

## Tunables

| Key | Unit | Home |
|---|---|---|
| `cache.fadePerTurnMilli` | ‰ per turn, bounded ratio in (0, 1000] | `data/tuning/trade.v1.json` (new) |

## Numeric types

Quantities `long`, `checked`; the pro-rata share multiplies before dividing; fade computes
`(qty × fade + 999) / 1000` in `checked` `long`.

## Registry

No new quantity: a cache holds located goods (and world stocks) already registered by `sector-yield`'s
`located-goods-registry`. The located-goods row in `empire-resource-ssot.md` §3 gains, in this module's
implementing change, **holders** "legion carried pool, goods cache" and **sink** "cache fade" (P1 — the
fade is the named sink for goods nobody recovers). That edit belongs to the implementing change, which
owns the row's widening; this spec only names it.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldStoreTests|FullyQualifiedName~WorldGraphDiffTests"
python gk-core/scripts/guard-dal.py
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                     MODIFIED — GoodsCaches + record + enum
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                 MODIFIED — conditional goods-cache rows
src/FusionRpg.Core/World/Logistics/Fleet/GoodsCache.cs     (new) — Place, claim step, fade
src/FusionRpg.Core/World/Logistics/Fleet/CarriedGoods.cs   MODIFIED — OnEntityRemoved body → GoodsCache.Place
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs     MODIFIED — tokens
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs                MODIFIED — rpg_world_goods_caches schema + load
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs       MODIFIED — packed-row diff for caches
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/GoodsCacheTests.cs (new)
```

## Testing strategy

- **Conservation at creation:** destroyed caravan carrying three goods → the cache at its place holds
  exactly those goods; a starved one the same; a caravan carrying nothing creates nothing.
- **Merge:** two losses at one lane in one turn give one cache with the summed goods.
- **Reach:** a lane cache is claimed by a legion on that lane and not by one at either end sector; a
  sector cache by a legion standing there and not by one on an adjacent lane.
- **Pro rata:** at a place of scale 1000, two legions of different factions with free load 30 and 10 on
  a cache of 20 receive 15 and 5; swapping their faction ids or their creation order changes nothing; remainder units go by
  entity id.
- **Capture mid-route:** the destroying legion, with bearers, holds the goods at the end of the same
  turn; a fighter-only victor takes nothing and the cache stays.
- **Fade:** a cache never grows without a creation; it loses `ceil(qty × fade / 1000)` per good per turn
  and is removed in finitely many turns; fade 0 fails the tuning load.
- **Sink invariant:** over a scripted run, Σ goods everywhere changes only by recorded faucets and sinks;
  no cache quantity ever appears in a banking fact or ledger credit without first appearing in a
  warehouse.
- **Round trip and hash:** save → load → hash with caches present; a world with no caches hashes as
  before this module.
- **Transit ownership:** capturing a caravan's destination hub or source depot mid-route leaves its pool
  unchanged.

## Boundaries

- **Always:** place goods in `Step`, at the legion's last place, in the same statement that removes them;
  claim pro rata; fade as a recorded sink.
- **Ask first:** a claim command or opt-out; a cache that never fades; caches on anything but a sector or
  lane.
- **Never:** credit a wallet from a cache; route goods through the item corpse-cache tables; let a faction
  id break a tie.

## Success criteria (contract)

1. A legion's involuntarily lost goods equal the new or grown cache's goods, per good; nothing carried
   creates nothing.
2. A lane cache is reachable from its lane, a sector cache from its sector.
3. Claims conserve goods and split pro rata by free capacity, independent of faction ids and entity order.
4. A cache never grows except by creation, shrinks by its fade every turn, and is removed when empty.
5. No path from a cache credits a wallet directly.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `GoodsCache.Place` | `interception` (spill) |
| Caches in state + facts | `trade-surface` (a cache on the map); `trade-stories` `trade-quests` `recover` (see map C13) |

## Dependencies

`interception`, `carried-goods`; `scoped-inventory` `cargo-fate` (the rule, not its tables);
`logistics-flow` `logistics-phase`, `logistics-canonical`; `trade-foundation` `stock-deltas`.

## Hard edges

New hashed state and a new table (schema migration through the store's setup, `guard-dal` green);
hash-neutral when empty by the conditional-row rule.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world state and persistence, world turn engine (Logistics), economy (sinks, capture),
    scoped inventory (cargo-fate rule reused).
[~] Session boundary: trade-network-idea-20260919 covers this path; check script not run by me.
[x] Read this session: scoped-inventory-hierarchy-map.md module 4; RpgStore.CargoFate.cs header;
    DiffEntities' cargo-fate block; as spec-carried-goods.md.
[x] decisions.md: Scoped inventory hierarchy SSOT (items Data-side; goods hashed — a different class).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding.
[x] Verified against code: item fate path and ordering, placement invariant, claim-cache kind.
[x] Surrounding sections read: RpgStore.CargoFate.cs summary block in full.
[~] Constraints tested: none claimed.
[x] No §2 invariant contradicted: fade is a bounded ratio (commented); no faucet added; determinism.
[x] Corrections propagated: C13 (trade-stories recover template) recorded in fleet-map.md.
[x] No population pinned; GoodsPlaceKind is a closed enum with its reason.
[x] No event-refreshed cache (a goods cache is state, not a cache in the §2.16 sense).
[x] Orderings: entity creation order and faction ids never change a split (tested).
[x] No actor magnitude.
[x] No SOLID fork: one fate rule, one placement function for removal and spill, lane-flow's scale read.
[ ] Registry rows: "no cache path credits a wallet" wants a guard (source scan + property test) row.
    Named (audit 2026-09-20): invariant id `fleet-cache-never-credits-wallet`.
```

## Audit 2026-09-20

Fixed here: fade used `lane-loss`'s fact kind `loss` (now its own `fade`, ask A14); a goods cache had no
ledger holder kind, so the global conservation net could not include it (ask A14: `Cache` / `c:`); the
`departed` removal cause is excluded from cache creation. Checked and clean: pro-rata claims never read a
faction id; fade is a bounded ratio in (0, 1000] with rounding up so every cache ends; no cache path credits a
wallet. Round-trip tests run the store **in memory** (`DataTestStore.Create()`, testing-standard R1).
**Verification boundary:** the `core-world-logistics-fleet` owner boundary (`spec-carried-goods.md` Hard
edges); `RpgStore.World.cs`/`RpgStore.WorldGraphDiff.cs` keep their existing Data owners.

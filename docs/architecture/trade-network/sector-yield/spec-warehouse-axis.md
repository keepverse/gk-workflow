# Spec: `warehouse-axis`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.3 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §8.2 (*"its own capacity
axis"*), §10 C6, §13 (`warehouse.capacityByLevel`). Umbrella invariants 7 and 10.
**Round 4** ([../decisions-round-4.md](../decisions-round-4.md) §B): storage is unlocked by the storage
building — **Storehouse → Warehouse → Granary Complex**, tier variants of one row — and each tier widens
the axis.
**Round 5** ([../decisions-round-4.md](../decisions-round-4.md) R5-A A2, X13): every **held** sector has a
small **base yard capacity** (one tunable, `warehouse.baseYard`); the Storehouse ladder widens it. The
storage tier is read through `trade-foundation` `sector-features` only. This replaces round 4's "a sector
with no storage building has no warehouse capacity".

## Objective

Give a sector a **warehouse capacity** for located goods: a third capacity axis beside loam `Storage`
and `ItemStorage`, never a second meaning on either field. The owner already rejected overloading one
capacity field for two stocks (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:40-42`, `:74-78`), and the
ideal's C6 records the same for the warehouse.

Success: one reader answers "how many units of located goods can this sector hold"; its number comes
from the sector's buildings (the storage tier first), grows with development and the same scale as the
goods (so it is never a hidden ceiling); the loam and item readers cannot see it. A second reader answers
"how much of that is occupied", so every program that adds goods to a warehouse counts them once.

## Scope and non-goals

**In scope:** the capacity field and its per-tier resolution, the capacity reader, the occupancy
reader, their tunables, and the anchor ordinal that feeds them.

**Not in scope:** holding stock (`located-stock`), what happens at capacity (`production-halt`),
deliveries that overflow (`logistics-flow`), a trade hub's own warehouse row (`exchange` /
`empire-seed` `trade-structure-rows`), value-weighted capacity (see §Design 4).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Loam capacity: base + active `Storage` bonuses + development growth | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:86-100`; growth `gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:53-54` |
| Item capacity: the reader this one copies — active-slot gate, additive sum, `checked` | `gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14-27` |
| Each field is read by one axis only; the rule is written on the fields | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:71-78` |
| Only rows with a `magnitudes` block load into the catalog | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| `coffer` and `stockyard` are `store`-role rows with no magnitudes | `gk-data/packs/fusion/data/seed/structures/store/coffer.json`, `gk-data/packs/fusion/data/seed/structures/store/stockyard.json` (no `magnitudes` key) |
| The scale read | `spec-essence-loop-read.md` §Design 1 (`LocatedScale`) |

### Wiring gap

| What is inert | Evidence |
|---|---|
| `coffer`, `stockyard` exist as identity only | files above; `StructureCorpus.cs:65` |

### Real gap

The warehouse field, its reader and its tunables.

## Design

### 1. The field

Three sources, one reader. **The base yard**: a held sector (`WorldSector.OwnerFactionId` is set,
`gk-core/src/FusionRpg.Core/World/WorldState.cs:158`) has `warehouse.baseYard` whatever it builds (R5-A A2).
**The storage building** (`FeatureUnlock == storage`, `trade-foundation`
`sector-features`) contributes `warehouse.capacityByTier[t]` for its slot's tier `t` — what a tier does is
the consuming mechanism's tuning, never a band on the variant (`empire-seed` `spec-trade-structure-rows.md`
§2, §5.4). **Any other building whose design includes a warehouse** carries `StructureDef.WarehouseCapacityBonus`
(`long`, default 0), resolved from its row's `warehouseBand` ordinal. Its doc comment carries the same rule as its two siblings:
**read only by `SectorWarehouse`**; `LoamPhases.EffectiveCapacity` and `SectorItemCapacity.EffectiveCapacity`
never read it, and `SectorWarehouse` never reads `CapacityBonus` or `ItemStorageCapacityBonus`.

It is **not** gated on a `StructureKind` (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`). The storage
building is its main carrier, and a building whose own design includes a warehouse (a trade hub —
ideal §8.2 *"one warehouse per trade center"*, `exchange` ask E-A4; a depot, `fleet/spec-depot.md` §3)
carries it too. The reader sums the field over every active structure at its slot's tier, the shape
`FlatYieldPerTurn` already uses (`gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:48-56`). `StructureKind`
is not widened.

### 2. Where the number comes from

The storage building's per-tier capacity is `warehouse.capacityByTier` in `data/tuning/trade.v{n}.json`
(owned here). A non-storage row's bonus is resolved at load from an anchor ordinal `warehouseBand` through
`empire-seed`'s `band-reader`, against a band table in `data/tuning/structure-seed.v{n}.json`. The seed never carries the number. Per `empire-seed`
`trade-structure-rows` (*"a capacity or clearing ordinal is added to the anchor only when its consuming
`StructureDef` field lands"*), the ordinal and this field land in the same change: the generator emits
`warehouseBand` (the corpus is regenerated, never hand-edited). The storage row — `featureUnlock: storage`,
tiers Storehouse, Warehouse, Granary Complex — is `empire-seed`'s new `storehouse` row
(`spec-trade-structure-rows.md` §5.2, slot `Wildland`); `coffer` and `stockyard` stay identity-only.

### 3. The readers

```csharp
// src/FusionRpg.Core/World/SectorWarehouse.cs (new)
/// Soft cap, not a ceiling: grows with buildings, tiers, development and the content scale, and a halt
/// against it is reversible (decision 22). Exempt from the no-hard-ceilings rule on that ground.
public static long EffectiveCapacity(WorldSector sector, TradeTuning trade, PowerTuning power)
{
    long bonus = 0;
    foreach (var slot in sector.Slots)
    {
        var tier = SectorFeatures.ActiveTier(slot);            // sector-features §3: 0 = empty or first build;
        if (tier == 0) continue;                                // mid-upgrade counts at its current tier
        if (!StructureCatalog.IsKnown(slot.StructureId!)) continue;
        var def = StructureCatalog.Get(slot.StructureId!);
        bonus = checked(bonus + (SectorFeatures.Unlocks(def, SectorFeature.storage)
            ? trade.Warehouse.CapacityAtTier(tier)              // 1-based; a missing tier was a load rejection
            : def.WarehouseCapacityBonus));
    }
    long yard = sector.OwnerFactionId is null ? 0 : trade.Warehouse.BaseYard;   // R5-A A2: held sectors only
    long growth = SectorFeatures.TierFor(sector, sector.OwnerFactionId, SectorFeature.storage) >= 1   // round 6 S1
        ? checked((long)Math.Max(0, sector.DevelopmentLevel) * trade.Warehouse.CapacityByLevel)
        : 0;
    return LocatedScale.Apply(checked(yard + bonus + growth), LocatedScale.Milli(sector, power));
}

/// Everything that occupies the warehouse: the owner's located stock plus every registered term.
public static long Occupancy(WorldSector sector);
```

**Base yard (round 5, A2).** Round 4 removed the first draft's `warehouse.baseCapacity`, which left a
sector with no Storehouse at capacity 0; the owner's A2 answer (the map's §5c Q-R2) restores a **small
base yard on every held sector**, as one tunable, `warehouse.baseYard`. It is not the retired key reborn:
it applies only to a sector a faction holds (an unowned sector stores nothing), and it is deliberately
small so the Storehouse ladder stays the way to widen storage. The storage tier is still read only through
`sector-features` (X13) — and, from round 6 S1, through **`TierFor`** rather than `TierOf`: a Storehouse on
a slot held by someone other than the sector's owner widens nobody's warehouse until one faction owns both
(`../trade-foundation/spec-sector-features.md` §5a). The per-slot `bonus` loop above is the same rule: it
sums only slots the sector's owner also holds. Development growth applies only where a storage building
stands (it widens a warehouse, it does not create one).

**Occupancy** is `LocatedStock.Total` plus the terms other programs register for goods that sit in the
same warehouse but are not the owner's stock — today one: `exchange`'s consignments (`exchange-hub` §4,
its ask E-A4: *"occupancy = the owner's located stock + Σ consignments"*). `production-halt`, `income-parity`
and `logistics-flow` `transit-buffer` compare `Occupancy`, never `LocatedStock.Total`, against capacity.

### 4. Units — one unit per good, stated

Capacity counts **units of located goods, every good weighing one**. The ideal asks for
"value-normalised units"; the value of a good is `exchange`'s `goods.{id}.baseValue` (ideal §13), a
later sub-program, and reading it here would point a dependency back up the build order. The PS-5
hazard the ideal names (a flat capacity walling a scaling good) is closed by the scale read alone:
capacity and Content-loop yields grow by the same factor in the same sector. If `exchange` later wants
value weights, it adds them to this reader's sum by a reviewed change; no second capacity is built.

### 5. Tunables file

`data/tuning/trade.v1.json` does not exist yet. **One loader, one location:** the `TradeTuning` record,
its pure parser (Core never reads a file, `PRINCIPLES.md` §5) and the host-injected `TradeTuningHub` live
at `src/FusionRpg.Core/World/Trade/TradeTuning.cs`, the path `trade-foundation` `economy-report` names;
each sub-program adds its own block. **Creator (settled 2026-09-20, reconciliation R-19.3):** there is no
race — [landing-order.md](../landing-order.md) §5 fixes `trade-foundation` `economy-report` (row 0a) as the
one creator of the file, the loader and the `trade` domain in `gk-core/tools/tuning/publish.py`. **This module
publishes `v{n+1}`** with `--add-key` for its own keys, and so does `structure-upkeep`. A missing key is a
load rejection.

## Tunables

| Key | Unit | Meaning |
|---|---|---|
| `warehouse.baseYard` | units at the pin | The small base yard every held sector has with no storage building (R5-A A2); the storage tiers add to it |
| `warehouse.capacityByTier` | units at the pin, one entry per storage tier, **in tier order, entry *k* = tier *k*** (1..3; read through `CapacityAtTier(tier)`, never by raw index) | The storage building's capacity at each tier; strictly rising. A missing tier, or more entries than the storage feature's maximum tier, is a load rejection |
| `warehouse.capacityByLevel` | units at the pin per development level | Growth with development where a storage building stands (the F12 shape, `StructurePolicy.cs:49-54`) |
| `warehouse.deliveryOverflowWasteMilli` | ‰ per turn | Waste of a delivery that cannot unload at a full warehouse. **Owned here** with the axis; read by `logistics-flow` `transit-buffer` (L4) and `rift-trade` `crossing-handoff` |
| `bands.warehouseBand.*` (in `structure-seed.v{n}.json`) | units at the pin | Per-ordinal bonus for a non-storage row with a warehouse (hub, depot); `empire-seed`'s table |

`warehouse.baseCapacity` is **retired** before it ships (round 4 §B); it is not published. Round 5's
`warehouse.baseYard` replaces it with a different rule (held sectors only).

Values are decided by principle and published; they are not owner questions.

## Numeric types

`long` throughout, `checked`, widened before the multiply (`(long)devLevel * perLevel`), scaled once
through `ContentScale.Apply` (divide by 1000 once, last). Capacity is a content-scaled magnitude, so
`int` is not an option (CLAUDE.md range table).

## Acceptance (contract)

1. `SectorWarehouse` is the only reader of `WarehouseCapacityBonus` (a source scan over
   `gk-core/src/FusionRpg.Core`); `LoamPhases.EffectiveCapacity` and `SectorItemCapacity.EffectiveCapacity` return
   the same value for a sector whether or not its structures carry a warehouse bonus; `SectorWarehouse`
   returns the same value whatever `CapacityBonus` and `ItemStorageCapacityBonus` are. One test per
   direction.
2. A structure under first construction or unknown to the catalog contributes nothing; a structure being
   upgraded contributes its current tier.
3. A held sector with no active structure carrying a warehouse bonus has exactly the scaled base yard
   (`warehouse.baseYard`); an unowned sector has 0; development adds nothing without a storage building;
   each storage tier strictly raises the sector's capacity above the base yard.
4. At the pin (`dangerBand` 4) capacity equals the authored sum exactly; at every other band it equals
   `LocatedScale.Apply(authored, LocatedScale.Milli(sector))`.
5. Capacity never decreases when a structure is added, a tier rises or development rises.
6. `Occupancy` equals `LocatedStock.Total` plus every registered term; with no term registered it equals
   `LocatedStock.Total`.
7. A missing `warehouse.*` key, or a `warehouseBand` ordinal with no band row, is a load rejection.
8. `StructureCatalog.All` is otherwise unchanged by the new field: every existing field of every row
   resolves as before (the `structure-bands` byte-identity check extends to the new field defaulting
   to 0 for rows with no ordinal).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/SectorWarehouseTests.cs` (new): items 1–7, mirroring
  `gk-core/tests/FusionRpg.Core.Tests/World/SectorItemCapacityTests.cs`.
- Tuning parser tests beside the new `TradeTuning` loader; `gk-core/tools/tuning/test_publish_add_key.py` style
  test for the `trade` domain.

If this module creates `data/tuning/trade.v1.json`, it lands the `core-trade-tuning` owner row
(`trade-foundation` `economy-report` §Test plan) in the same change: `gk-core/data/tuning/**` has no fallback
mapping, so without it `verify-change.py` stops on the tuning file.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/StructureCatalog.cs',
  'src/FusionRpg.Core/World/SectorWarehouse.cs',
  'tests/FusionRpg.Core.Tests/World/SectorWarehouseTests.cs') -Session <active-session-id>
python -m pytest gk-core/tools/tuning -q
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Structure

```
gk-core/src/FusionRpg.Core/World/StructureCatalog.cs          MODIFIED — WarehouseCapacityBonus field
src/FusionRpg.Core/World/SectorWarehouse.cs           (new)
src/FusionRpg.Core/World/Trade/TradeTuning.cs         (new, if this module lands first)
data/tuning/trade.v1.json                             (new, if this module lands first)
gk-core/tools/tuning/publish.py                               MODIFIED — trade domain (if first)
data/tuning/structure-seed.v{n+1}.json                warehouseBand table (empire-seed publishes)
tests/FusionRpg.Core.Tests/World/SectorWarehouseTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** one field, one reader; scale through `LocatedScale`; numbers in tuning.
- **Ask first:** a new `StructureKind` for warehouses; value-weighted capacity; any base capacity beyond
  the one `warehouse.baseYard` term (R5-A A2), or a base yard on an unowned sector.
- **Never:** read or write `CapacityBonus` / `ItemStorageCapacityBonus` for goods; a number in a seed
  file; a flat capacity.
- **Hard edge — generated corpus.** `gk-data/packs/fusion/data/seed/structures/**` is generator output: the ordinal reaches
  `coffer`/`stockyard` by regenerating through `empire-seed`'s generator, never by editing the JSON.

## Dependencies and interface

**Depends on:** `essence-loop-read` (`LocatedScale`); `trade-foundation` `sector-features` (tiers and
`TierFor`, round 6 S1); external `empire-seed` `band-reader` (I2), `structure-bands` (I3) and `trade-structure-rows`
(the storage row and its tier variants).

| Exposed | Consumer |
|---|---|
| `SectorWarehouse.EffectiveCapacity(sector, trade, power)` | `production-halt`, `income-parity`, `legion-equipment-stock`; later `logistics-flow` (delivery room, overflow), `exchange` (hub warehouse), `fleet` (depot), `trade-surface` (forecast) |
| `SectorWarehouse.Occupancy(sector)` and its term registration | the same readers; `exchange` registers its consignment term |
| `TradeTuning.Warehouse` | same |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: structures and the structure corpus, tunables, power scale.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: trade-network-ideal §8.2, §10, §13; umbrella invariants; empire-seed-map
    band-reader, structure-bands, trade-structure-rows; ssot-power-scale §10.
[x] decisions.md: magic-numbers row (no literal), empire resource registry (no new quantity here).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: both existing capacity readers and their field comments; the magnitudes gate;
    the identity-only store rows.
[x] Surrounding sections read: LoamPhases.EffectiveCapacity's F12 note; SectorItemCapacity's exemption
    comment.
[x] Constraints tested, not assumed: no golden claim (a 0-default field moves nothing).
[x] No §2 invariant contradicted: capacity is a soft cap, scaled, in tuning; long.
[x] Corrections propagated: "value-normalised units" is interpreted and the interpretation stated here
    and in the session report.
[x] No population pinned.
[x] No event-refreshed cache (computed per call from hashed state).
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: a third field and reader, not an overloaded one; StructureKind not widened; one
    occupancy reader for every program that fills a warehouse.
[x] Round 4 applied (2026-09-19): capacity from the storage building's tiers; the overflow-waste key
    owned here; one TradeTuning location.
[x] Round 5 applied (2026-09-20): A2 base yard on every held sector (`warehouse.baseYard`); X13 the
    storage tier through sector-features only. OwnerFactionId re-verified at WorldState.cs:158.
[~] Registry row for the single-reader rule (specified in the audit of 2026-09-20): acceptance 1's source
    scan becomes a script guard `warehouse-single-reader` (tier `ci`, gating) plus invariant
    `tn-warehouse-single-reader` in gk-core/scripts/enforcement-registry.v1.json, landing with this module. The
    tier and feature reads go through sector-features' `ActiveTier`/`Unlocks` and are covered by its
    `feature-gate-one-read` guard.
```

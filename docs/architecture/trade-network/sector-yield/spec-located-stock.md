# Spec: `located-stock`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.4 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §8.1 (*"one pooled stock
per (sector, good)"*), §9.2 rule 8, §14b (*"a sparse canonical form … and one packed row per sector"*).
Umbrella invariants 5, 6 and 8.

## Objective

Hold located goods on the map: one pooled, hashed stock per (sector, located good), a single warehouse
per sector, changed only inside `TurnEngine.Step`, saved and diffed proportionally to change. A world
that holds no located goods must hash and persist exactly as today.

## Scope and non-goals

**In scope:** the field on `WorldSector`, its canonical form, its persistence and load, the one
mutation API every later module calls, and its stock deltas.

**Not in scope:** anything that adds or removes stock (yields, banking, flows, trade — each later
module calls this module's API); capacity (`warehouse-axis`); the ledger table (`trade-foundation`
`world-stock-ledger`).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Per-sector stocks on the sector record: `LoamStock`, `RubbleStock`, `IronworkStock`, `RecruitStock`, all `long` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:148`, `:173`, `:181`, `:187`, `:234` |
| Conditional canonical rows: a new field that is zero on every old world writes nothing, so old hashes do not move | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:118-128` (`sector-rubble`, `sector-ironwork`) |
| The diffing writer compares a sector row field by field and rewrites only changed rows | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:121-133` (`SectorRowEquals`), `:135` (`DiffSectors`), upsert `:150-191` |
| The diff writer's own equivalence guard: it re-reads the graph and compares hashes | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:32-34`, `:56-66` |
| Column-add precedent, and the lesson it records: rubble and ironwork were hashed but not persisted until the guard caught it | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:180-188` |
| Full write and load of sectors | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:272`, `:290-316`, load `:518-554` |
| Materials are keyed by player only; nothing holds a good per sector | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:191-193` |

### Wiring gap

None.

### Real gap

The located stock itself, its canonical row, its column, and its only writer.

## Design

### 1. The value

```csharp
// src/FusionRpg.Core/World/Goods/LocatedStock.cs (new)
public sealed class LocatedStock : IEquatable<LocatedStock>
{
    public static readonly LocatedStock Empty;
    public IReadOnlyList<(string GoodId, long Qty)> Entries { get; }  // Qty > 0, ordinal id order
    public long Of(string goodId);                                      // 0 when absent
    public long Total { get; }                                          // checked sum, for capacity
    public string Pack();                                               // "id=qty;id=qty", "" when empty
    public static LocatedStock Unpack(string packed);                   // throws on malformed or unknown id
    // value equality over Entries
}
```

`WorldSector.LocatedStock` (default `LocatedStock.Empty`). **Value equality** matters: `WorldSector` is
a record, and `SectorRowEquals` must see two equal stocks as equal or the diff writer rewrites every
sector every turn.

A **zero entry never exists**: taking a good to zero removes it. Every id is checked against
`LocatedGoodCatalog` (`spec-located-goods-registry.md`).

### 2. The only writer

```csharp
// src/FusionRpg.Core/World/Goods/LocatedStockOps.cs (new)
public static WorldSector Add(WorldSector sector, string goodId, long delta,
                              string factKind, StockDeltaRecorder deltas);
```

- Every change to a located stock goes through `Add`, which records a `trade-foundation`
  `stock-deltas` entry `(sector, goodId, delta, factKind)` in the same call. `factKind` comes from the
  closed `ledger-keys` vocabulary (`produce`, `income`, `bank`, `depart`, `deliver`, `return`,
  `settle-buy`, `settle-sell`, … — `spec-ledger-keys.md` §4a; there is no one-kind `settle`, round 5 X2).
  Goods that leave a warehouse for a route are recorded by `logistics-flow` `transit-buffer` as `depart`
  onto the route's `r:` holder, so the reconciliation below still closes while goods are on the road.
- A result below zero **throws**. A caller that wants "take what is there" reads `Of` first; this
  function never clamps.
- `checked` arithmetic.
- It is called only from phases inside `Step`. Data-side code constructs the field on load and never
  mutates it.

### 3. Canonical form

After the `sector-ironwork` loop (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:123-129`), one more
conditional row per sector, in the sector order the canonical writer already uses:

```
sector-goods|<sectorId>|<Pack()>      // written only when LocatedStock is not empty
```

Sparse by construction (non-zero entries only, ordinal order), so an empty warehouse adds no bytes and
every existing world hashes exactly as today.

**Append slot (audit M3) and the wave flag (round 6 C1).** Four modules in the family append a conditional
row *"after the `sector-ironwork` loop"*, and the canonical text is hashed, so their relative order is part
of every later golden. The family's order is fixed once, in
[../landing-order.md](../landing-order.md) §4: `world-stamp`'s stamp row, **this module**,
`logistics-flow` `logistics-canonical`, `fleet` `carried-goods`. Each spec states its slot as *"after the
last conditional row present at landing"* rather than an absolute position — so whichever of the four lands
second appends after the first without editing it. This module is **`sector-yield` wave 1** (row 1) and is
where the wave's capability row `trade.sectorYield` is registered, with the one `RulesetVersion` bump the
wave takes; `located-goods-registry`, `essence-loop-read`, `warehouse-axis`, `production-halt` and
`bank-points` land in the same wave and gate on the same flag.

### 4. Persistence — one packed row per sector

Decision (ideal §15 left it to the spec): **one packed column on the existing sector row**, not a row
per good and not a new table.

- `rpg_world_sectors.located_goods TEXT NOT NULL DEFAULT ''`, added with `EnsureColumn` beside
  `rubble_stock` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:187-188`). An old save reads `''`,
  which is `LocatedStock.Empty`.
- `SectorRowEquals` compares it; the diff upsert and the full write carry it; load unpacks it. **All
  four sites land in the same change as the field** — the rubble precedent (`RpgStore.World.cs:180-186`)
  is what happens otherwise.
- Why not a new table: the value is sector-scoped world state, and a world-graph column is scoped by
  `world_id` like every `rpg_world_*` row (`docs/architecture/solid-enforcement/spec-save-identity.md`
  "The rule for a table created after this module": instance-keyed rows carry no owner column). A new
  table would add a closure contract for no gain.
- Why not a row per good: goods × sectors rows, most of them churning every turn. One column keeps
  writes at one row per changed sector.

## Tunables

None.

## Numeric types

`long` quantities, `checked` add. The packed text uses invariant-culture integers. Entries are
unbounded above (no cap here; capacity is `production-halt`'s soft stop).

## Acceptance (contract)

1. A world with no located stock produces a canonical text **byte-identical** to today's for the same
   world, on the same template and command log.
2. A non-empty stock changes the hash, and two worlds that differ only in one sector's stock hash
   differently.
3. Save → load round-trips the stock exactly (every entry, every quantity), in the in-memory store.
4. The diff writer writes a sector's row when and only when its stock (or another sector field)
   changed; the equivalence guard (`RpgStore.WorldGraphDiff.cs:56-66`) passes on a turn that changes
   stock.
5. Every call to `LocatedStockOps.Add` produces exactly one stock delta, and the `stock-deltas`
   reconciliation holds for the located goods: per sector and good, Σ deltas = post − pre.
6. `Add` that would take a stock below zero throws and leaves the sector unchanged; a zero result
   removes the entry.
7. `Unpack` of a malformed string or an unknown good id throws.
8. No code outside `src/FusionRpg.Core/World/Goods/` assigns `LocatedStock` except the Data load path
   (a source scan).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Goods/LocatedStockTests.cs` (new): items 1, 2, 5–8.
- `tests/FusionRpg.Data.Tests/World/LocatedStockPersistenceTests.cs` (new, in-memory store): items 3–4.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/WorldState.cs',
  'gk-core/src/FusionRpg.Core/World/WorldCanonical.cs',
  'src/FusionRpg.Core/World/Goods/LocatedStock.cs',
  'src/FusionRpg.Core/World/Goods/LocatedStockOps.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedStockTests.cs',
  'tests/FusionRpg.Data.Tests/World/LocatedStockPersistenceTests.cs') -Session <active-session-id>
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
```

This change crosses Core and Data, so the full suite runs once at module end (AGENTS.md "Verification
boundary", point 2); no golden is expected to move (acceptance 1), and one that moves is a defect in
this change.

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedStock.cs          (new)
src/FusionRpg.Core/World/Goods/LocatedStockOps.cs       (new)
gk-core/src/FusionRpg.Core/World/WorldState.cs                  MODIFIED — WorldSector.LocatedStock
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs              MODIFIED — sector-goods row
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs             MODIFIED — column, write, load
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs    MODIFIED — equality, upsert
tests/FusionRpg.Core.Tests/World/Goods/LocatedStockTests.cs            (new)
tests/FusionRpg.Data.Tests/World/LocatedStockPersistenceTests.cs       (new)
```

## Boundaries and hard edges

- **Always:** sparse canonical row; column, equality, write and load in one change; every change
  through `Add` with a delta.
- **Ask first:** a separate goods table; a row per good.
- **Never:** clamp a negative; mutate the stock outside `Step`; a zero entry in the packed form.
- **Hard edge — save format.** The column is additive with a default, so no migration or backup is
  owed; an old save loads as empty. Removing or renaming the column later would be a migration.

## Dependencies and interface

**Depends on:** `located-goods-registry`; `trade-foundation` `stock-deltas` (and through it
`ledger-keys`). `stock-deltas`' reconciliation walks the registry's world-stock rows
(`trade-foundation-map.md` §2.6); it must walk the **Located good** class too — a one-line widening in
that module, named here so the gap cannot hide.

| Exposed | Consumer |
|---|---|
| `WorldSector.LocatedStock`, `LocatedStock.Of/Total/Entries` | `production-halt`, `banking-fact`, `legion-equipment-stock`; later `logistics-flow`, `exchange`, `trade-surface` |
| `LocatedStockOps.Add` | every module that changes a located stock |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world state and canonical hash; world store (Data/SQL); stock-delta recorder.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: trade-network-ideal §8, §9, §14b; umbrella invariants; trade-foundation-map
    §2.5-§2.7; spec-save-identity's new-table rule; empire-resource-ssot.
[x] decisions.md: save identity row — no new table, a world-graph column.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: the conditional canonical rows, SectorRowEquals, the equivalence guard, the
    rubble column history.
[x] Surrounding sections read: WorldCanonical's comments on conditional rows; RpgStore.World's rubble
    migration note.
[x] Constraints tested, not assumed: "no golden moves" is acceptance 1, to be proven by the suite.
[x] No §2 invariant contradicted: SQL in Data only; long; no cap.
[x] Corrections propagated: the stock-deltas walk widening is named in Dependencies and the report.
[x] No population pinned.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one writer, one packed form shared by hash and store.
[ ] Registry row: the "only writer" rule (acceptance 8) is a test source scan; its enforcement-registry
    row lands with this module.
```

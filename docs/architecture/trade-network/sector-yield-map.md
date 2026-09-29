# Capability map: `sector-yield` (trade-network sub-program 2)

**Status:** APPROVED 2026-09-19. Owner decisions recorded in §5a. Module specs written 2026-09-19 (§5b).
**Reconciled with the round-4 owner decisions** ([decisions-round-4.md](decisions-round-4.md)) on
2026-09-19 — §7 lists what changed; where §1–§6 and §7 differ, §7 and the specs win. Open questions from
the reconciliation are §5c.
**Umbrella:** [../trade-network-map.md](../trade-network-map.md) — its §5 invariants bind every module
here and are not repeated. **Ideal:** [../trade-network-ideal.md](../trade-network-ideal.md) §5 (real
gap: *"Sector yields of banked goods"*), §8.2, §8.5, §8.6, §11 row 2, §14 D-A, §14b.
**Specs land:** `docs/architecture/trade-network/sector-yield/spec-<module-id>.md`.
**Plan / tasks:** `tasks/trade-network-sector-yield-plan.md` / `-todo.md`.

> **The sub-program in one sentence.** Held ground pays: structures produce goods into a pooled,
> capacity-bounded warehouse in their own sector, production stops when the warehouse is full, and
> goods that sit at a bank point leave the map as a ledger fact into the wallet that has no location.

This is the reward layer `world/spec-sector-development.md` said *"names no module"*
(`docs/architecture/world/spec-sector-development.md:261`); owner decision D-A assigns it here, built
the Shape B way from the start. Moving goods between sectors is `logistics-flow`'s; this sub-program
produces, stores, halts and banks.

---

## 1. What already exists (read in code this session)

| Fact | Where |
|---|---|
| Structures do five things: `LoamSource`, `Storage`, `Yield`, `Refinery`, `Obstacle`, plus `ItemStorage` | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-43` |
| `Yield` structures *"produce loam and recruits only; the reward layer itself (souls, essence, materials) is unassigned"* | `StructureCatalog.cs:16-24` |
| Two capacity axes already exist, deliberately separate: loam `CapacityBonus` (read only by `Storage`) and `ItemStorageCapacityBonus` (read only by `ItemStorage`) — the owner rejected overloading one field | `StructureCatalog.cs:40-42`, `:71-78` |
| Item-storage capacity reader, the shape a warehouse reader copies | `gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14` |
| `FlatYieldPerTurn` adds to the **loam** total for every active structure | `StructureCatalog.cs:80-88`; `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:47-55` |
| Loam production clamps at capacity and reports `loam.overflow` (a waste, not a halt) | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-64`, capacity `:86` |
| Decision 22's halt rule exists as a function with **no caller** | `gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:56-58` |
| Rubble and ironwork production is *"uncapped by design"* | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:77-81` |
| `LoamUpkeep` has *"no structure term yet"*; the W10 projection reads `BreakdownFor`, not a copy | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:28-35`, `:40`, `:47` |
| Structure corpus: 28 hand-authored anchors in 11 role folders; only rows with a `magnitudes` block load | `gk-data/packs/fusion/data/seed/structures/`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| The `bank` role holds the soul conduit and the reliquary. The soul conduit is a `Yield` structure paying **20 loam** a turn on an `EssenceDeposit` slot | `gk-data/packs/fusion/data/seed/structures/bank/soul-conduit.json` (`magnitudes.flatYieldPerTurn`, `structureKind`) |
| `store`-role rows: `coffer`, `stockyard` (identity-only), `granary` (`Storage`), `relic-vault` (`ItemStorage`, on the `Vault` slot) | `gk-data/packs/fusion/data/seed/structures/store/*.json` |
| Slot kinds include `Vault` and `Market` | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:72-74` |
| The capital: exactly one `Home`-flagged sector, owned by the player faction; `Fortress` is a separate flag | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-215`; `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:5-16` |
| Connected components per faction (the reuse `empire-economy-ssot.md` §5 names for banking) | `gk-core/src/FusionRpg.Core/World/Loam/TerritoryComponents.cs:14-24` |
| World content scale for a sector: `PowerIndexComposer.MapLevel(dangerBand)` → `ContentScale.Milli` — already used by sector loot and siege loot | `gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:97`; `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15`, `:31`; `gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:81`; `gk-core/src/FusionRpg.Core/World/Turn/SiegeLoot.cs:46` |
| `Step` already accepts `PowerTuning` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-170` |
| The essence loop is flat on both sides today: expedition faucet +1 per kill; fusion cost a flat `int` | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:134-136`; `gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs:5` |
| Banked materials: 27 issuable ids in four classes (a closed catalog); souls carry no id — they are a ledger balance | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:61-68` |
| Materials are keyed by player only | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:191-193` |

**What does not exist:** a good with a location; a warehouse; a structure that yields anything but
loam and recruits; a halt; a bank point; a banking fact; structure upkeep; an AI empire that holds goods.

---

## 2. Modules

Ordered model-free first. Every behaviour change is gated by the world stamp's capability flag
(`trade-foundation` `world-stamp`), so a legacy world hashes and plays exactly as today.

### 2.1 `located-goods-registry`

**Capability.** Register the **located good** class — a map-scoped quantity held in a sector's
warehouse, which converts one way into its banked counterpart on a banking fact — in
`empire-resource-ssot.md` §2, with its §3 rows, and give Core a closed catalog that maps each located
good id to the banked id it becomes (`essence.*`, `shard.*`, `substrate.*`, `catalyst.*` materials, and
souls, whose banked form is the soul ledger). Loam, rubble, ironwork and recruits are **not** located
goods: they are world stocks already and never bank. This lands before any other module is specced
(ideal §14b).

- **State:** real gap. The registry has no class for a banked good that sits on the map
  (`docs/architecture/empire-resource-ssot.md` §2); without one, banking would breach *"world stocks
  never feed an account-scoped path"* (§4 rule 5).
- **Depends on:** —
- **Touches:** `docs/architecture/empire-resource-ssot.md` §2–§3, `src/FusionRpg.Core/World/Goods/`
  (new: `LocatedGoodCatalog`).
- **Acceptance (contract):** every located id maps to exactly one issuable banked id
  (`MaterialCatalog.All`) or to souls; no located id maps to loam, rubble, ironwork or recruits; the
  mapping is total and injective; an unknown id throws. The catalog is **derived** from
  `MaterialCatalog`, so its size is a reading — the test asserts the join, never a count. The registry
  rows state P4 and P6 for the class: the located form is the same good (P4 is its banked form's), its
  competing sinks are banking, trade (`exchange`) and loss/capture (`logistics-flow`).
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.2 `essence-loop-read`

**Capability.** Apply the PS-5 rule before any yield number exists: located-good yields, warehouse
capacity and the essence sink read **one scale** — `ContentScale.Milli(MapLevel(sector.DangerBand))`
for a sector's faucet and capacity, the same read sector loot already uses. `ssot-power-scale.md` §10.4
already decided that essence and materials **must** scale; today both halves of the essence loop are
flat, which is PS-5-consistent but contrary to §10.4 (umbrella X5). This module records the decision as
a §10 row and carries it to both halves **in one change**: no scaling essence yield ships while the
fusion essence cost stays flat.

- **State:** decision closed (§10.4, §14b); wiring gap in code (both halves flat).
- **Depends on:** —
- **Touches:** `docs/architecture/power/ssot-power-scale.md` §10 (one row), `src/FusionRpg.Core/World/Goods/`
  (the scale read), and — **cross-program** — `gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs`
  with the fusion tuning's next published version (the creature program's balance surface; the change
  is coordinated with it, not taken over).
- **Acceptance (contract):** at Θ = 20 (the pin) the scale is exactly 1000‰, so no number moves at the
  calibration point; faucet and sink call the same read function, proven by a test that fails if either
  side is given a different scale; `long`, `checked`, divide by 1000 last (`ContentScale.Apply`).
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`; `python gk-core/scripts/audit-overflow.py`; the power guard
  (`guard-power.py`).

### 2.3 `warehouse-axis`

**Capability.** A **third capacity axis** — the warehouse — beside loam `Storage` and `ItemStorage`,
never a second meaning on either field. A sector's effective warehouse capacity is ~~a tuned base plus~~
the resolved warehouse band of its active structures (**round 4: the storage building's tier — Storehouse
→ Warehouse → Granary Complex — first**, §7 Y2; **round 5: plus a small base yard on every held sector,
`warehouse.baseYard`**, §8 R5-Y2),
scaled by the same read as the goods it holds (`essence-loop-read`), in value-normalised units. The reader copies `SectorItemCapacity`'s shape. Which
rows raise it (`store`-role rows such as `coffer` and `stockyard`; later, the trade center's own
warehouse from `exchange`) is resolved through `empire-seed`'s band table, never typed into a seed.

- **State:** real gap. `coffer` and `stockyard` are identity-only rows (no `magnitudes`,
  `StructureCorpus.cs:65`).
- **Depends on:** `essence-loop-read`; external `empire-seed` I2 `band-reader` and I3 `structure-bands`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs` (one field), `src/FusionRpg.Core/World/SectorWarehouse.cs`
  (new), `data/tuning/trade.v1.json` (proposed; the file does not exist yet), `empire-seed`'s band table.
- **Acceptance (contract):** the warehouse field is read only by the warehouse reader, and the loam and
  item readers never read it (a test per direction, mirroring the `ItemStorageCapacityBonus` comment's
  rule); capacity is `long` and grows with the scale read; a missing tuning key is a load rejection,
  never a default.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.4 `located-stock`

**Capability.** A hashed, pooled stock per (sector, located good) on `WorldSector` — one warehouse per
sector — written only inside `Step`. Canonical form lists non-zero entries only, in ordinal id order,
so an empty warehouse adds nothing to the hash and a legacy world's hash does not move. Persisted as
**one packed row per sector** through the diff writer (ideal §14b), so persistence stays proportional to
change.

- **State:** real gap (materials are keyed by player only, `RpgStore.Materials.cs:191-193`).
- **Depends on:** `located-goods-registry`; `trade-foundation` `stock-deltas`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/WorldState.cs`, `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs`, `RpgStore.World.cs` (schema, load).
- **Acceptance (contract):** a world with no located stock hashes byte-identically to today; the stock
  round-trips through save and load exactly; the diff writer writes a sector's packed row only when its
  stock changed; every change to the stock appears as a `stock-deltas` record (reconciliation passes);
  a negative stock throws.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (canonical, hash), `gk-core/tests/FusionRpg.Data.Tests`
  (round-trip, diff).

### 2.5 `production-halt`

**Capability.** Decision 22, wired for located goods: when a sector's warehouse is at capacity, its
production **stops** — nothing is produced and nothing is wasted — and the turn report records a halt
fact with the good and sector, which `trade-surface` turns into the throttle forecast and a
notification. This is the first caller of `StructurePolicy.IsHaltedByCapacity`. Only **incoming
deliveries** that arrive at a full warehouse overflow and waste; that half belongs to
`logistics-flow`. Loam keeps its own shipped clamp-and-overflow rule; this module does not change it.

- **State:** wiring gap — the rule exists with no caller (`StructurePolicy.cs:56-58`; umbrella X1).
- **Depends on:** `located-stock`, `warehouse-axis`.
- **Touches:** `src/FusionRpg.Core/World/Goods/LocatedProduction.cs` (new — the one credit function
  every located yield goes through), `StructurePolicy.cs`.
- **Acceptance (contract):** at capacity, credited = 0 and a halt fact is emitted; below capacity,
  credited = min(yield, room) and the remainder is **not produced** (no overflow line, no waste delta);
  building more capacity resumes production on the next turn with no clawback; no rating spiral —
  a halt never lowers any future yield. The rule applies to every faction identically.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.6 `yield-structures`

**Capability.** Structures yield **located goods**: a structure's resolved magnitudes carry a yield
vector (good → band), resolved to amounts by `empire-seed`'s band table and scaled by
`essence-loop-read`, credited through `production-halt`'s one credit function in the `Production`
phase, for **every** faction that owns the sector. The soul conduit becomes the reward layer's first
row, as `empire-economy-ssot.md` §5 designed it (*"a plain building that yields souls"*): its yield
becomes located souls, changed through `empire-seed`'s band table, never by editing the seed file.
Capability-gated: a legacy world keeps today's loam-only yields.

- **State:** real gap (structures yield loam and recruits only, `StructureCatalog.cs:16-24`).
- **Depends on:** `production-halt`, `essence-loop-read`; external `empire-seed` I2/I3 (bands) and the
  structure rows it generates; `trade-foundation` `world-stamp`.
- **Touches:** `StructureCatalog.cs` (yield vector), `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs`
  (`Production` phase call), `src/FusionRpg.Core/World/Goods/`, `empire-seed`'s band table.
- **Acceptance (contract):** on a trade-granting stamp, a sector with an active yield structure
  gains exactly its resolved yield (or less, at capacity) each turn; on a legacy stamp, the same
  world's hash and stocks match today; an AI empire's and the player's identical sectors produce
  identical stock (principle 10); every credit appears in `stock-deltas` with factKind `produce`; a
  structure under construction yields nothing (the existing `ConstructionTurnsRemaining` gate,
  `LoamProduction.cs:50-53`). The P1 row lands with it: the economy report shows each new faucet's
  sinks.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World, and `trade-foundation`'s economy report).

### 2.7 `structure-upkeep`

**Capability.** The missing structure term in `LoamUpkeep`: every active structure adds a loam upkeep
amount by role, from `upkeep.structureTermByRole` in `data/tuning/trade.v1.json` (proposed), added to
the existing sum before the intensity, handicap and season multipliers, exposed through
`BreakdownFor` so the W10 projection shows it without a second formula. Loam stays Θ-invariant (PS-5
decided "neither" for loam, `ssot-power-scale.md` §10.4). Capability-gated, because it changes loam
outcomes on existing worlds.

- **State:** real gap, named in code (`LoamUpkeep.cs:34-35`).
- **Depends on:** `trade-foundation` `world-stamp`. Independent of the goods modules — it can land
  first.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs`, its breakdown record, the tuning file.
- **Acceptance (contract):** with every role's term at 0, upkeep is byte-identical to today on any
  stamp; on a legacy stamp the term is never read; the term is counted once per active structure
  (never for one under construction, never twice across the breakdown and the total); `checked`
  arithmetic in `long`.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World/Loam — `LoamUpkeepTests` stays green with no
  expected value changed).

### 2.8 `bank-points`

**Round 4 (supersedes this section's rule, §7 Y1):** a bank point is an owned sector holding an active
**Counting House** (any tier), read through `trade-foundation` `sector-features`; no capital rule, no
`Vault`-slot capability. The approved text follows for the record.

**Capability.** A pure query: which sectors are a faction's **bank points** this turn. A bank point is
the faction's capital — an owned sector whose type carries a seat flag, `Home` or `Boss` (the seat
definition world-continuity `seat-outcome` uses) — plus every sector holding an active structure whose
resolved magnitudes grant the bank-point capability. *(Corrected at spec time, 2026-09-19: this line
named the `Fortress` sector for an AI empire, but no sector type sets `Fortress`
(`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:60-99`; `gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:261-267`).
See `sector-yield/spec-bank-points.md`.)* Bank points are many (*"flows are not a star through one capital"*, ideal §8.5). An empire
that holds no capital and no bank-point structure banks nothing until it builds one — the same rule
for every faction.

- **State:** real gap. No structure takes goods off the map; the existing `bank` role means something
  else (umbrella X2; see owner question Q1).
- **Depends on:** — (reads existing flags and structure state).
- **Touches:** `src/FusionRpg.Core/World/Goods/BankPoints.cs` (new), the structure band table for the
  capability.
- **Acceptance (contract):** the capital is always a bank point while its owner holds it; losing the
  capital removes it; an inactive or under-construction structure grants nothing; the result is
  ordered by sector id; it is identical for every faction kind given the same holdings.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.9 `banking-fact`

**Capability.** Goods in a bank point's warehouse **leave the map**: inside `Step`, the stock is
decremented and a banking fact keyed `(save, owner, world, turn, bank, sector, good)` is emitted. In the
turn commit, a human empire's fact credits its wallet through `trade-foundation`'s `material-ledger`
verb (or the soul ledger, for souls) and writes the `world-stock-ledger` row; the wallet has no
location, so losing a sector — the capital included — never hands a banked good to anyone. An AI
empire's fact credits a **per-world, hashed treasury** on its faction (a world stock, ideal §14b). The
treasury is owned **and written** by `counterparties` `empire-treasury` (owner decision, §5a; round 5 X3),
registered into this module's destination seam; this module hands it the fact. This module creates the `Logistics` phase slot (after `Production`, before
`Growth`, ideal §8.7) with banking as its only step; `logistics-flow` adds its steps around it in
the fixed step order of `logistics-flow` `logistics-phase` §1 (banking is L3: refresh, arrivals and fleet load/unload before it; delivery overflow, rift departures, flow, loss, refine and facts after it — round 5 X5).
Auto-banking is on by default; the policy commands that change it belong to `logistics-flow`.
**Round 4 (§7 Y3):** a bank point banks up to its Counting House tier's rate per turn
(`banking.ratePerTurnByTier`, scaled — a rate, never a cap, R5-A A3) and, from the Treasury tier, keeps a
per-good hold (round 5 default, A4: enough to fill other traders' open buy orders at this hub). AI treasuries are credited through a destination seam `counterparties` registers
into, so this module no longer depends on `empire-treasury`.

- **State:** real gap (no code banks sector yields; ideal §10 C1).
- **Depends on:** `bank-points`, `located-stock`; `trade-foundation` `world-stock-ledger`,
  `material-ledger`, `world-stamp`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (the phase), `src/FusionRpg.Core/World/Goods/`,
  `WorldState.cs` (AI treasury), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (commit),
  `docs/architecture/decisions.md` (the phase-order row, amended in the same change — adding a phase
  changes the ruleset), `empire-resource-ssot.md` §3 (treasury row).
- **Acceptance (contract):** banking is idempotent under re-commit (the same key credits once); the sum
  of banked credits equals the sum of warehouse decrements for every good and turn; no fact ever
  credits loam, rubble, ironwork or recruits; capture of a sector after a banking fact moves nothing
  already banked; on a legacy stamp the phase does nothing and the hash matches today; the phase-order
  test (`TurnEngineTests`) names the new phase.
- **Declared, not hidden:** until `counterparties` gives AI treasuries their sinks, an AI treasury is a
  faucet with no reader — nothing spends it, so it cannot unbalance play, and the economy report prints
  it as monotone positive with the owning follow-up named.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`, `gk-core/tests/FusionRpg.Data.Tests`. Crosses Core and Data
  and moves the phase list: full suite once at module end, goldens triaged per the golden-ordering
  rule (`decisions.md` *Golden ordering across streams*), never re-blessed to pass.

### 2.10 `legion-equipment-stock`

**Capability.** Legion equipment pieces (`legion-build-ideal.md` §6.7) as a located good: a counted
`long` stock per (sector, piece id) in the same warehouse, under the same capacity, halt and
stock-delta rules, tradeable later through `exchange`. **Production recipes and the piece catalog are
not this module's** — they belong to `legion-build` (mechanics) and `empire-seed` (the piece seeds);
fitting pieces to stacks where a legion stands is `legion-build`'s. This module only makes a piece a
thing a warehouse can hold.

- **State:** real gap (no piece catalog exists yet; `legion-build` owns it).
- **Depends on:** `located-stock`, `production-halt`; external `legion-build` (piece catalog ids).
- **Touches:** `src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs` (a piece kind),
  `empire-resource-ssot.md` §3 (one row).
- **Acceptance (contract):** a piece id outside the `legion-build` catalog is refused; pieces share the
  warehouse's capacity axis (no fourth axis); the registry row states P4 (goods × building time is the
  bottleneck) and P6 (fitting stacks versus trade) in the same change, per legion-build §6.7.
- **Spec-time decision, recommendation included:** pieces have **no banked form** — they never
  auto-bank, and cross worlds only as cargo (world-continuity §6.2). A banked form would make them an
  account-scoped material fed by world production, which `empire-resource-ssot.md` §4 rule 5 forbids.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.11 `income-parity`

**Capability.** Income with a location — a claim or siege loot drop, a delve entered from a map door —
lands in that sector's warehouse as located goods and travels like any yield; income with no world
location (expeditions, Sanctum delves, web waves) banks as today (ideal §8.6). Round 4 Q11 assigns it here
(the umbrella §1 had placed it in `logistics-flow`). A closed located-source table, a Data-side divert at
loot persist, a logged per-turn input into `Step`, and a full credit through the one credit function with
factKind `income`, gated by `trade.incomeParity`.

- **State:** real gap; claim and siege loot are themselves inert today (unpassed `PowerTuning`), and a
  delve does not record its door sector.
- **Depends on:** `located-stock`, `production-halt`, `warehouse-axis`, `located-goods-registry`;
  `trade-foundation` `world-stamp`, `ledger-keys`, `stock-deltas`, `economy-report`. Its capability is
  introduced no earlier than `logistics-flow`'s `trade.logistics` (a registry ordering, not a code
  dependency).
- **Spec:** [sector-yield/spec-income-parity.md](sector-yield/spec-income-parity.md).

---

## 3. Dependency graph and build order

```text
located-goods-registry --> located-stock --------+----------------------+
                               ^                  |                      |
        trade-foundation       |                  v                      v
        stock-deltas ----------+           production-halt        banking-fact <-- bank-points
                                                  ^   |                  ^
essence-loop-read --> warehouse-axis -------------+   |                  |
        |                 ^ (empire-seed I2/I3)       v                  |
        +--------------------------------------> yield-structures        |
                                                  (world-stamp)          |
                                                                          |
structure-upkeep (world-stamp)                    legion-equipment-stock  |
                                                  (legion-build catalog)  |
                trade-foundation: world-stock-ledger, material-ledger ----+

trade-foundation sector-features --> warehouse-axis, bank-points        (round 4)
located-stock, production-halt, warehouse-axis --> income-parity        (round 4)
```

**Build order:**

1. `located-goods-registry`, `essence-loop-read`, `structure-upkeep`, `bank-points` — model-free,
   independent.
2. `warehouse-axis` (after `empire-seed` I2/I3), `located-stock`.
3. `production-halt`.
4. `yield-structures`.
5. `banking-fact` (after `trade-foundation`'s two ledgers).
6. `legion-equipment-stock` (when `legion-build`'s piece catalog exists).
7. `income-parity` (its code after `production-halt`; its capability shipped with or after
   `logistics-flow`'s `trade.logistics`).

`warehouse-axis` and `bank-points` also wait for `trade-foundation` `sector-features` and for
`empire-seed`'s storage and banking rows with their tier variants (round 4).

`logistics-flow` starts after `banking-fact`: it adds flow steps to the phase that module creates.

## 4. Tunables

In `data/tuning/trade.v1.json` (proposed; the file does not exist yet), published through
`gk-core/tools/tuning/publish.py`: `warehouse.baseYard` (round 5 A2), `warehouse.capacityByTier`, `warehouse.capacityByLevel` (value-normalised units, scaled by the
`essence-loop-read` read), `warehouse.deliveryOverflowWasteMilli` (owned here, read by `logistics-flow` and
`rift-trade`), `banking.ratePerTurnByTier` (round 4, scaled), `upkeep.structureTermByRole` (loam per turn,
flat). `warehouse.baseCapacity` is **retired before shipping** (round 4, §7 Y2). Yield bands, per-tier
warehouse bands and tier costs are **structure bands in `empire-seed`'s
`data/tuning/structure-seed.v{n}.json`**, never numbers in this sub-program; the bank-point capability is
no longer a band (it is the Counting House's `feature`). Values are decided by
principle and published; they are not owner questions.

Numeric types: every stock, yield and capacity is `long`, `checked`, widened before multiplying, and
scaled once through `ContentScale.Apply`.

## 5. Owner questions

**Q1 — What makes a structure a bank point?** The ideal names *"the `vault` slot, `bank` structure
role"* (§8.5). In the shipped corpus the `bank` role already means a banked-currency **faucet** (the
soul conduit and the reliquary, umbrella X2), so reading it as "bank point" would give one role two
meanings — the exact defect D-E1 avoided by adding `exchange` instead of reusing `enable`.
**Recommendation:** bank-point is a **capability** in a structure's resolved bands, granted by default
to structures on the `Vault` slot, with no role widened or redefined. The `bank` role keeps its current
meaning. Default if unanswered: the recommendation — it is reversible (a band change) and widens no
closed vocabulary. **Closed 2026-09-19 — see §5a D1. Superseded by round 4 §B: the bank point is the
Counting House building (§7 Y1).**

## 5a. Owner decisions (2026-09-19, with the approval)

| # | Decision | Where it is built |
|---|---|---|
| D1 (Q1) | ~~A bank point is a **structure capability**, granted by default to buildings on the `Vault` slot.~~ **Superseded by round 4 §B:** a bank point is the Counting House building (any tier). The existing `bank` role keeps its meaning | `bank-points` (`SectorFeatures.TierOf(sector, banking) ≥ 1`; `GrantsBankPoint` is not built) |
| D2 | `banking-fact` **creates the `Logistics` phase slot** (banking its only step); `logistics-flow` extends it with its steps in the fixed step order of `logistics-flow` `logistics-phase` §1 (banking is L3: refresh, arrivals and fleet load/unload before it; delivery overflow, rift departures, flow, loss, refine and facts after it — round 5 X5) | `banking-fact`; umbrella CM4 |
| D3 | The AI-empire treasury is owned by `counterparties` `empire-treasury`, which is also its writer, registered into `banking-fact`'s destination seam (round 4; round 5 X3). `sector-yield` hands it the banking fact | `banking-fact`; umbrella CM3 |

Consequence of D3 recorded at spec time (**retired by the round-4 reconciliation**: `banking-fact` now
exposes an `IBankingDestination` seam that `empire-treasury` registers into — counterparties ask A11 — so
the arrow below no longer exists): `banking-fact` depends on one `counterparties` module
(`empire-treasury`), which itself needs only `located-goods-registry`. The module order is therefore
`located-goods-registry` → `empire-treasury` → `banking-fact`; no cycle exists, but it is the one arrow
from this sub-program to a later one (umbrella §2 says arrows never point back up). If
`empire-treasury` is late, `banking-fact`'s AI branch waits and AI bank points hold their goods — a
declared temporary handicap (`sector-yield/spec-banking-fact.md`, hard edges).

## 5b. Module specs (2026-09-19)

| Module | Spec |
|---|---|
| `located-goods-registry` | [sector-yield/spec-located-goods-registry.md](sector-yield/spec-located-goods-registry.md) |
| `essence-loop-read` | [sector-yield/spec-essence-loop-read.md](sector-yield/spec-essence-loop-read.md) |
| `warehouse-axis` | [sector-yield/spec-warehouse-axis.md](sector-yield/spec-warehouse-axis.md) |
| `located-stock` | [sector-yield/spec-located-stock.md](sector-yield/spec-located-stock.md) |
| `production-halt` | [sector-yield/spec-production-halt.md](sector-yield/spec-production-halt.md) |
| `yield-structures` | [sector-yield/spec-yield-structures.md](sector-yield/spec-yield-structures.md) |
| `structure-upkeep` | [sector-yield/spec-structure-upkeep.md](sector-yield/spec-structure-upkeep.md) |
| `bank-points` | [sector-yield/spec-bank-points.md](sector-yield/spec-bank-points.md) |
| `banking-fact` | [sector-yield/spec-banking-fact.md](sector-yield/spec-banking-fact.md) |
| `legion-equipment-stock` | [sector-yield/spec-legion-equipment-stock.md](sector-yield/spec-legion-equipment-stock.md) |
| `income-parity` (round 4) | [sector-yield/spec-income-parity.md](sector-yield/spec-income-parity.md) |

Spec-time findings that refine this map (each argued in its spec):

- **Capital rule** (§2.8): `Fortress` replaced by the seat flags `Home`/`Boss` — no sector type sets
  `Fortress`. On shipped templates no `vault` slot and no `boss-lair` sector exist, so the player's `Home`
  is the only bank point and AI empires have none until content places one.
- **Loop table** (§2.2): a located yield reads the scale its loop's sink reads. Essence moves to the
  content scale only together with the fusion sink; souls read the content scale; shard, substrate and
  catalyst yields stay flat, because their crafting sinks are rung coefficients (`ssot-power-scale.md`
  §10.2 row 37) — a tension with §10.4's *"materials must scale"*, recorded, not resolved here.
- **Power tuning inside `Step`** (§2.2): the located read uses the host-injected `PowerTuningHub`, not
  `Step`'s `powerTuning` parameter; passing that parameter from the commit would also wake
  `ClaimResolver`'s inert sector-loot path.
- **Soul conduit** (§2.6): on a trade-granting stamp a structure with located yields does not also pay
  its flat loam; the catalog keeps the loam field so legacy worlds read today's number.
- **P2 dependency** (§2.6): `yield-structures` depends on `structure-upkeep` — a yield building never
  ships without its loam upkeep term. Build order §3 already places `structure-upkeep` first.
- **Warehouse units** (§2.3): one unit per good; value weighting would read `exchange`'s valuation, a
  later sub-program.
- **Legion pieces** (§2.10): stored in the located warehouse per `legion-build-ideal.md` §6.7, which
  contradicts `legion-build-map.md` §5.14's `rpg_item_stock` root; that map's spec must reconcile.

## 5c. Owner questions raised by the round-4 reconciliation

**All three answered 2026-09-20** ([decisions-round-4.md](decisions-round-4.md) R5-A): Q-R1 → **A1** (a
tier-1 Counting House and a tier-1 Storehouse in every empire's seat — option (a)); Q-R2 → **A2** (a small
base yard on every held sector — option (b)); Q-R3 → **A3** (a per-turn rate growing with the tier, never a
cap — option (a)). Applied in §8. The questions stay below as the record.

**Q-R1 — Does a world start with a Counting House in each seat?** Round 4 removed the implicit capital
bank point, so a new world banks nothing until a Counting House is built. The first-throttle answer
(*"build a Counting House"*) presumes a player who already banks at home.
- (a) **World creation places a tier-1 Counting House (and a tier-1 Storehouse) in each empire's seat
  sector** — content, by `world-continuity` `world-creation`, the template owners and `counterparties`
  `empire-roster`. *Recommended and the specs' default:* the rule stays one rule (a building), play starts
  banking, and the first throttle is a sector with no path home.
- (b) The seat is an implicit tier-1 bank point with no building — reintroduces the exception round 4
  removed.
- (c) Nothing is placed; the first End Turns teach "build a Counting House" at home — strict, but the
  first several turns bank nothing.

**Q-R2 — Does a sector without a storage building hold any goods?** Round 4 §B makes storage a
building-unlocked feature; read strictly, a sector without a Storehouse has capacity 0, so its yield
buildings halt and deliveries to it waste.
- (a) **Strict: capacity 0 without a warehouse-carrying building** (a storage building, a trade hub, a
  depot). *The specs' default*, because the register says a feature without its building is not
  available; yield buildings are planned beside a Storehouse, and the forecast answers the halt with
  *build storage*.
- (b) A small tuned yard capacity everywhere (the retired `warehouse.baseCapacity`), the Storehouse tiers
  widening it — softer onboarding, at the cost of an exception to §B. *Recommended if play-testing shows
  the halt spam of (a) at the start of a world;* it is a one-key republish.

**Q-R3 — Is "faster banking" a per-turn banking rate?** Round 4 says T2+ adds *"faster banking"*; before
round 4 banking took the whole stock at once.
- (a) **Yes: every tier banks up to a scaled per-turn rate that rises with the tier** (`banking-fact`
  §3). *Recommended and the specs' default:* it is the only reading under which tier 1 is slower.
- (b) Banking stays instant; higher tiers only add the hold (and "faster" means nothing mechanical).

## 6. DESIGN-GATE §5 checklist

```
[x] Subsystems: economy/resources (registry), structures and the structure corpus, world turn engine
    (a new phase slot), tunables, power scale (PS-5), world store, materials store.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/
    trade-network/**. session-boundary-check.py exits 1 on the crossing already recorded in that
    file (broad worktree lanes); this file is new.
[x] Read this session: empire-resource-ssot (whole), empire-economy-ssot §5-§6, economy-principles
    P13-P14 and §12-§13, ssot-power-scale §10-§10.4, structure-seed-ideal §4, legion-build-ideal
    §6.7, world-continuity-ideal, empire-seed-ideal. Not read in full: tunables-ssot.md,
    data-architecture.md, spec-soul-economy.md (rules taken from PRINCIPLES.md §5-§6 and §11).
[x] decisions.md checked: phase order lock (:7) — banking-fact amends it in its own change and says so;
    empire resource registry (:108) — every new quantity lands its row with its module.
[x] Every factual claim cites file:line (§1 table).
[x] audit-doc-citations.py --scope run on this map and every spec (2026-09-19 spec session).
[x] Verified against code: the halt function's missing caller, the soul conduit's loam yield, the two
    existing capacity axes, the capital flags, the flat essence loop, the ContentScale precedent.
[x] Surrounding sections read (LoamUpkeep's formula comment, SiegeConstruction's uncapped note,
    structure-seed-ideal's role table).
[x] Constraints tested, not assumed: "no golden moves on a legacy stamp" is an acceptance criterion to
    prove; banking-fact is the one module stated to move the phase list, with the golden rule named.
[x] No §2 invariant contradicted: no hard cap (halt is decision 22's reversible soft stop; capacity
    grows with the scale read), balance numbers in tuning, long magnitudes, one power ladder.
[x] Corrections propagated: X1, X2 and X5 are recorded in the umbrella map and here.
[x] No population pinned: the located catalog is derived from MaterialCatalog and asserted by join.
[x] No event-refreshed cache introduced (bank points are computed per turn, never cached).
[x] No ordering-fixed criterion: halt-then-build and build-then-halt both resume on the next turn.
[x] ActorHub: legion equipment's stat contribution is legion-build's, through the Hub; this map only
    stores the pieces.
[x] No SOLID fork: one credit function for every located yield, a third capacity axis rather than an
    overloaded field, the existing loam upkeep formula extended rather than copied, the ledgers reused.
[ ] Registry rows for new rules: the warehouse single-reader rule and the one-credit-function rule get
    guards or unguardableReason rows when their modules land.
```

## 7. Reconciliation 2026-09-19 (round 4)

Applied from [decisions-round-4.md](decisions-round-4.md), which wins over any spec. Cross-checked against
every other trade-network, `world-continuity`, `legion-build` and `empire-seed` spec.

| # | Change | Where |
|---|---|---|
| Y1 | **Bank point = the Counting House building** (any tier), read through `trade-foundation` `sector-features`. The `Vault`-slot capability (`GrantsBankPoint`, Q1/D1) and the capital rule are removed; the `bank` role stays a currency faucet | `spec-bank-points.md` |
| Y2 | **Storage capacity comes from the storage building's tiers** (Storehouse → Warehouse → Granary Complex, one row's variants); `warehouse.baseCapacity` retired; development widens only an existing warehouse; a new `Occupancy` reader counts `exchange` consignments (E-A4); `warehouse.deliveryOverflowWasteMilli` is owned here | `spec-warehouse-axis.md`; `spec-production-halt.md` (reads `Occupancy`) |
| Y3 | **Banking rate per Counting House tier and the per-good hold at the Treasury tier** (Q2; default hold = what open sell orders need, an `exchange` hold source — E-A11; *default superseded by round 5 A4, §8 R5-Y4*). The AI treasury is reached through an `IBankingDestination` seam `counterparties` registers into (A11), which retires §5a's cross-sub-program arrow | `spec-banking-fact.md` |
| Y4 | **New module `income-parity`** (Q11) | §2.11; `spec-income-parity.md` |
| Y5 | `production-halt` gains `CreditMode.FullCredit` (income only) and an `income` factKind; a zero-capacity sector halts every yield | `spec-production-halt.md` |
| Y6 | Essence sink `Θ_sink` = the fused creature's level through the power ladder — now an owner decision (Q7), not a recommendation | `spec-essence-loop-read.md` §4 |
| Y7 | Legion equipment: the Workshop → Armory → Foundry tier is the best producible piece tier, read through `sector-features` (`legion-build`'s recipe gate) | `spec-legion-equipment-stock.md` |
| Y8 | Tier variants of one row pay their row's role upkeep term | `spec-structure-upkeep.md` |
| Y9 | `located-goods-registry`'s faucet column names `income-parity`, not `logistics-flow` | `spec-located-goods-registry.md` |
| Y10 | One `TradeTuning` location, `World/Trade/TradeTuning.cs` (trade-foundation §8 R6); stale `TurnEngine.cs`/`WorldState.cs`/`LoamPhases.cs` line citations re-pointed after `RulesetVersion` 13 | specs |

**Closed vocabularies this reconciliation widens or creates:** `LocatedIncomeSources` (new, joined against
`DropTableValidator.KnownSourceKinds`); `CreditMode` (new, 2); `FactKinds` +`income`; capability
`trade.incomeParity`; `SoulEarnPolicy.Reasons` +`world-bank` (already in `banking-fact`); banking-destination
coverage of the five `WorldFactionKind` members. Retired before shipping: `StructureDef.GrantsBankPoint`, the
`bankPoint` anchor ordinal, the two-member seat-flag set, `warehouse.baseCapacity`.

**Cross-cluster items this map cannot fix (other owners' files):**

- `empire-seed/spec-trade-structure-rows.md` (updated concurrently) adds the `storehouse` and
  `counting-house` rows with `featureUnlock` and tier variants — consistent with Y1/Y2. It files both rows
  under existing roles (`Store`, `Bank`); `structure-upkeep` charges them their role's term, and `bank-points`
  never reads the role (acceptance 4).
- `legion-build/spec-legion-equipment.md` and `legion-build-map.md` keep pieces (and forge goods,
  `spec-legion-standards.md`) in Data-side `rpg_item_stock` checked before `Step`; this map, the ideal
  (`legion-build-ideal.md` §6.7), `exchange/spec-tradeable-goods.md` and `rift-trade/spec-crossing-goods.md` put
  them in the hashed located stock. *(Ruled 2026-09-20 by X4: the hashed located stock; see §8 R5-Y7.)*
- `exchange/spec-settlement-payment.md` (§4, and `exchange-map.md` EC12) and `rift-trade/spec-crossing-goods.md`
  still name `banking-fact` as the AI treasury's writer; CM3 plus the destination seam make
  `counterparties` `empire-treasury` the writer.
- `world-continuity/spec-background-yield.md` calls banking *"a player act on a visit"*; banking is automatic
  on an active world (a woken world banks on its next End Turn) — wording only.
- *(Fixed 2026-09-20, X6.)* The umbrella map §1 assigned income parity to `logistics-flow`.

## 8. Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A owner answers, R5-X rulings),
which wins over any spec. Code citations touched by this pass were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| R5-Y1 | **A1 start kit:** every empire's seat starts with a tier-1 Counting House and a tier-1 Storehouse, so every empire has one bank point at turn 0. `bank-points` still special-cases nothing; the placement is `world-continuity`'s (`world-creation` §5a, one placement in `Rebuild`), and `counterparties` `empire-roster` owes the template slots (two free `Wildland` per owned empire seat). Clans are not empires and get no kit (`clan-seeding`). §5c Q-R1 closed | `spec-bank-points.md` §3; `spec-banking-fact.md` §6 |
| R5-Y2 | **A2 base yard:** a held sector (`WorldSector.OwnerFactionId`, `gk-core/src/FusionRpg.Core/World/WorldState.cs:158`) has `warehouse.baseYard`; storage tiers add to it; an unowned sector has 0. Reverses round 4's "no base capacity"; §5c Q-R2 closed | `spec-warehouse-axis.md`; `spec-production-halt.md` §1 |
| R5-Y3 | **A3 banking rate:** "faster banking" is a per-turn rate that grows with the tier, scaled like goods, never a cap (what does not bank waits; nothing is refused or destroyed). §5c Q-R3 closed | `spec-banking-fact.md` §3 |
| R5-Y4 | **A4 / X15 hold default:** enough to fill **other traders' open buy orders at this hub** (replaces "what open sell orders need"); still one `IBankingHoldSource` registered by `exchange` `order-book` | `spec-banking-fact.md` §3a; `logistics-flow` `auto-banking` |
| R5-Y5 | **X3:** `counterparties` `empire-treasury` writes the AI treasury, registered into `banking-fact`'s destination seam (wording aligned; the seam was already round 4's) | `spec-banking-fact.md` header |
| R5-Y6 | **X1 / X13:** the Counting House and Storehouse tiers are read only through `trade-foundation` `sector-features` (`TierOf`) — already the case in `bank-points` and `warehouse-axis`; restated | `spec-bank-points.md`, `spec-warehouse-axis.md` |
| R5-Y7 | **X4:** legion equipment is stored in the hashed sector warehouse (located stock), never `rpg_item_stock` — the §7 cross-cluster item on `legion-build` is now ruled in this map's favour; `legion-build` re-points | `spec-legion-equipment-stock.md` (unchanged; already so) |
| R5-Y8 | **X6:** income parity is `sector-yield`'s (`income-parity`); the umbrella map now says so and cites `RulesetVersion` 13 (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`) | umbrella §1 |

**Closed vocabularies:** none widened; `TradeTuning.Warehouse` gains `BaseYard` (a tunable, not a
vocabulary).

**Still other owners' files:** `world-continuity` world creation must place the A1 start kit in the
player's seat (and every seat it creates); `legion-build` re-points legion pieces to located stock (X4);
`exchange` `order-book`'s hold source counts other traders' open **buy** orders (A4).

## Audit 2026-09-20

An independent audit of this map and its eleven specs against CLAUDE.md, AGENTS.md, DESIGN-GATE §2–§5,
PRINCIPLES, tunables-ssot, validation-ssot, the test-substrate standard, economy-principles,
`ssot-power-scale.md` §10–§11 and the round-4/5 register, with the load-bearing claims re-opened in code on
`features/mega-merge`. `audit-doc-citations.py --scope` reported 0 HIGH on every file before and after the
edits. Specs win over §1–§8 where they differ.

| # | Severity | Finding | Fix |
|---|---|---|---|
| SY-A1 | Critical | `banking-fact` §1 said "`RulesetVersion` is **not** bumped" while `trade-foundation` `world-stamp` grants a capability by `stamp.RulesetVersion >= IntroducedAtRuleset`. Without a bump `trade.sectorYield` would be granted to every world already stamped at the current ruleset — worlds created before banking existed would start banking mid-life (a D-C breach and a hash move on existing saves) | `spec-banking-fact.md` §1, hard edges and acceptance 14: the capability row is born with one bump; the gate stays the stamp. `trade-foundation-map.md` audit TF-A1 and owner question OQ1 |
| SY-A2 | Major | **PS-5 break for souls.** `essence-loop-read` put `souls` on the Content read (sector depth), but every soul sink prices at `SoulSinkPolicy.VanillaPvzTheta` (Θ = 20) and the policy's own pairing rule is *"a sink reads the SAME Θ its faucet reads"* (`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:23`, `:34`). A wallet sink has no sector, so a depth-scaled soul yield would outgrow every sink — the +2/kill shape §10.4 forbids | `spec-essence-loop-read.md` §3: `souls` reads the same pin placeholder (Flat) until the soul sinks get a real Θ signal; acceptance 4 fails a move to Content while any sink still reads the pin |
| SY-A3 | Major | The essence loop's faucet reads sector depth and its sink the fused creature's level (round 4 Q7 — decided, not reopened): two different Θ indices, so PS-5 holds only as far as they move together, and nothing measured it | `spec-essence-loop-read.md` §3 "Residual pairing" + `trade-foundation` `economy-report`'s printed PS-5 pairing row |
| SY-A4 | Major | `warehouse-axis`' capacity sketch read `slot.StructureTier` and `def.FeatureUnlock` directly and indexed `CapacityByTier[slot.StructureTier]` (off-by-one against a 1..3 list; wrong tier mid-upgrade), contrary to "the storage tier is read through `sector-features` only" (X13) | Sketch rewritten on `SectorFeatures.ActiveTier` / `Unlocks` and `CapacityAtTier(tier)`; the tunable states entry *k* = tier *k* and rejects surplus entries |
| SY-A5 | Major | `banking-fact` credited materials through `material-ledger` with a **world** key; the account ledger had no source kind for it | §4: account fact `grant` / `world-bank` / sourceId = the world `bank` key (`trade-foundation` `ledger-keys` §4a, `material-ledger` §3) |
| SY-A6 | Major | "Capture clears the sector's policy holds" needed a write in `ClaimResolver`/`LoamPhases` (other programs' phases) and had no order-independence criterion (DESIGN-GATE §2.16 corollary) | §3a: each hold records its setter and applies only while the setter owns the sector (inert on capture, revived on retake — the rule route policies already have); acceptance 12 tests both orders |
| SY-A7 | Major | `yield-structures` §2 still said a sector without a storage building "has no warehouse capacity … halts from the first turn" — the round-4 rule round 5 A2 replaced with a base yard | Corrected to the base-yard rule |
| SY-A8 | Major | Every "is this structure active" gate the sector-yield specs copy (`yield-structures` step 2, `structure-upkeep`, `warehouse-axis`) would switch a building **off** during an upgrade | All now read `SectorFeatures.ActiveTier(slot) >= 1` (`trade-foundation-map.md` TF-A3); `yield-structures` acceptance 4 covers a building mid-upgrade |
| SY-A9 | Major | `data/tuning/trade.v1.json` would have no verification boundary (`gk-core/data/tuning/**` has no fallback; `verify-change.ps1 -PlanOnly` stops on it) | `spec-warehouse-axis.md`: whichever module creates the file lands the `core-trade-tuning` owner row (`trade-foundation` `economy-report`) |
| SY-A10 | Minor | `banking-fact`'s rate unit said "value-normalised units", while `warehouse-axis` §4 counts one unit per good; destinations were "ordered" without saying by what (registration order would make banking depend on startup order) | Unit aligned with the warehouse; destinations ordered by a declared id and overlapping destinations fail at startup (acceptance 13); the rate also grows with the number of bank points (not a ceiling) |
| SY-A11 | Minor | `located-stock` §2 listed `settle` as a fact kind (retired by X2); `production-halt` step 5 hard-coded `"produce"` although `income` also passes through it; `legion-equipment-stock` compared `LocatedStock.Total` where the halt compares `Occupancy`; `structure-upkeep` said a bank point is "a band"; `income-parity` still called the umbrella stale | Each corrected in place |
| SY-A12 | Minor | `rpg_located_income` had no single-writer rule although `material-ledger`'s guard exists for exactly that | `spec-income-parity.md` §2: a `ledger-writers` registry row (two named writers) |
| SY-A13 | Minor | `lane-loss` wanted one `goods.{id}.transitLossMilli` row per located id, which for legion pieces couples the tuning file to a seeded population (validation-ssot §1) | One family row `goods.legion-piece.transitLossMilli` (`legion-equipment-stock` acceptance 7; `logistics-flow/spec-lane-loss.md` Tunables) |

**Checked and found sound:** the located catalog derived from `MaterialCatalog` and asserted by join; the
one credit function and its no-waste halt; the sparse canonical rows and packed persistence (no golden at
the neutral value); P1/P2 for yields (the soul conduit's loam upkeep is the territorial throttle,
`empire-economy-ssot.md` §5); loam never located and never banked; every quantity `long`, `checked`,
divide last; capacity and rate as scaled soft limits, never ceilings; RPG layer only.

**Could not fix here (other owners' files):**

- **Materials-scale tension** (recorded at spec time, still open): `ssot-power-scale.md` §10.4 says
  materials must scale, §10.2 row 37 makes crafting legs rung coefficients that never scale. Shard,
  substrate and catalyst yields stay Flat until the **power program** (owner of §10) reconciles the two.
- `SoulSinkPolicy` call sites (creature program) carry no real Θ; when that program adds one, SY-A2's
  souls row moves to Content in the same change.
- `decisions.md:7`'s stale `TurnEngine.cs:180-195` citation: `banking-fact` amends that row and should
  re-point it (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:191-207`).

No new owner question beyond `trade-foundation-map.md` OQ1 (the stamp model), which SY-A1 depends on.

---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6". The family's single landing order is
[landing-order.md](landing-order.md); this sub-program occupies **seven waves** in its §2 (rows 1–4, 8,
10, 11).

| # | Decision | What changed in the specs |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | The single `trade.sectorYield` flag spanned four waves (`banking-fact` registered it while `yield-structures`, `structure-upkeep` and `essence-loop-read` gated on it), which is the C1 breach exactly. Now: **W1** `trade.sectorYield` — `located-goods-registry`, `essence-loop-read`, `warehouse-axis`, `located-stock` (registers it), `production-halt`, `bank-points`; **W2** `trade.structureUpkeep` — `structure-upkeep`; **W3** `trade.yieldStructures` — `yield-structures`; **W4** `trade.bankingPhase` — `banking-fact`'s phase slot; **W5** `trade.banking` — `banking-fact`'s step; **W6** `trade.incomeParity` — `income-parity`; **W7** `trade.legionEquipStock` — `legion-equipment-stock`. Each wave takes one bump. `structure-upkeep`'s *"it can land first"* is now true as written (it was blocked on an unregistered flag, audit SY-A1 / build-readiness) |
| **C2** | One neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | No spec here names a `StructureKind`; the change is `trade-foundation` `sector-features` §Dependencies and `empire-seed`'s rows. What it unblocks here is real: `bank-points` and `warehouse-axis` read tier 0 forever while the Counting House and Storehouse rows could not load (audit C2), and the A1 start kit placed rows that never loaded |
| **C3** | Banking waits on the save-identity re-key | `spec-banking-fact.md` new §1a splits the module's landing: the **phase slot** (no ledger dependency) lands as W4, the **banking step** as W5 after `material-ledger` → `save-identity` SE4.12–SE4.38. Without the split every `logistics-flow` wave would inherit the wait, because CM4 makes this module the phase's creator. §Dependencies names the ruling, refuses the audit's option (b), and §1a states the interim: goods reach a bank point and stay there, nothing is credited, `economy-report` prints a banked zero **with the reason** |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | `spec-bank-points.md` §1 reads `SectorFeatures.TierFor(s, f, banking)` and drops its own separate *"f owns s"* test (which would have counted a Counting House on a slot the previous owner still held); `TierAt` takes a faction. `spec-warehouse-axis.md` §3 reads `TierFor` for the development-growth gate and states that the per-slot bonus loop sums only slots the sector's owner also holds. The rule itself lives once, in `sector-features` §5a |
| **S2 / W1 / W2** | Trade goods cross worlds only by rift route; an advance is weight-limited | `spec-legion-equipment-stock.md` §3: a piece leaves its world either on a `rift-trade` route (the trade path) or as legion cargo **inside the advance's weight limit** — Σ(unit count × unit carry capacity) from `world.carry.capacity`, units and goods on one limit, arithmetic owned by `world-continuity` `advance-carry`. Import/export through the gate is `world-transit`'s, a named future program |
| **CQ2** | Legion equipment and doctrine upkeep may draw banked goods when local stock is short | `spec-legion-equipment-stock.md` new §3a: the shortfall is paid from banked **goods**, never a banked piece (§3 stands); the sink lives with the banked balance (`counterparties` `empire-goods-sinks` for an AI, the wallet for the player), symmetric by construction; **which** fitting and doctrine upkeep may fall back is an ask to `legion-build` |
| **D2** | The six `world.*` channels read Hub output | Nothing in this sub-program reads one. `warehouse-axis` scales with development and the content scale, not with a world channel |

**Superseded text in §2–§5 of this map.** §2.7's *"Capability-gated"* and §2.9's flag now name the
per-wave flags above; the build-order list in §3 stays correct as a dependency order, but the **bump and
flag order is [landing-order.md](landing-order.md) §2's**, which splits item 5 (`banking-fact`) into two
landings and moves `income-parity` after banking as well as after `trade.logistics`.

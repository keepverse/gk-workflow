# Spec: `carried-goods`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`, branch `features/mega-merge`). Every
`file:line` below was opened in this session. Module id `carried-goods`, row 1 of the
[fleet map](../fleet-map.md) (wave 1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §3.12,
§3.13, §8.1, §8.3; [legion-build-ideal.md](../../legion-build-ideal.md) §6.5. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

A legion can carry **goods**: a hashed, sparse per-good pool on the legion, with its own capacity axis
that grows with **bearers only**. This module owns the pool, its capacity, the two pure transfer
primitives (load from a sector, unload into a sector) that later modules call, and the one seam every
in-`Step` removal of a legion passes carried goods through. It adds no command kind and decides nothing
about *when* goods move — that is `trade-route-order`'s — or *where* a load may happen — that is
`depot`'s.

Success looks like: a legion with three bearers and one fighter can hold exactly
`3 × goodsPerBearer` load units; adding a fighter changes nothing; a world with no
carried goods hashes byte-identically to today; a legion that starves or is destroyed while carrying
goods never loses them silently.

## Locked anchors

- **Capacity from bearers, burn from headcount.** The shipped loam rule is the precedent and the reason:
  `LegionSupply.Capacity` reads bearers only, `Burn` reads every member
  (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`), because *"capacity scaling with every member is
  degenerate"* (`docs/architecture/empire-economy-ssot.md` §6). Goods capacity follows the same rule.
- **Its own axis** (ideal §3.12). Not `CarriedLoam` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:325`, loam's
  axis), and not the Data-side item cargo overlay, whose capacity counts every member by that program's
  decision (`gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:20-25,39-47`). This module never
  reads either capacity.
- **Hashed world state, changed only inside `Step`** (P13). Item cargo resolves Data-side after `Step`
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:83-119`); goods do not, because goods feed banking and
  lane flow, which are in-`Step` hashed state.
- **No command kind.** The names `load-cargo` and `unload-cargo` already belong to the item overlay
  (`WorldCommand.cs:87,93`). Goods load and unload are driven by a standing order's state inside the
  `Logistics` phase; reusing either name would give one kind two meanings — the collision
  `WorldCommand.cs:43-51` already records being repaired once (`ward` vs `bind-warden`).
- **Load units are `lane-flow`'s.** A parcel of `qty` of a good loaded at sector *S* occupies
  `loadOf(qty, S, good) = ceil(qty × 1000 ÷ scaleMilli(S, good))` load units — the one definition
  `lane-flow` publishes for exactly this consumer (`docs/architecture/trade-network/logistics-flow/spec-lane-flow.md` §Design 1 and its interface
  table — that spec is on disk from the parallel `logistics-flow` spec session, uncommitted when this was
  written). Capacities are **flat** in load units; the scale lives in `loadOf`. So a caravan and a
  lane measure cargo the same way (PS-5), and no second unit exists.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Member roles `Fighter`, `Bearer` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:269-273` |
| Bearer count, bearer-only capacity, headcount burn | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25` |
| Entity row in the canonical text; members hashed row by row | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:60-67` |
| Conditional-row precedent: an off-default stock writes its own row, so older hashes do not move | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:123-128` (rubble/ironwork), `:95-99` (faction scope) |
| Enums hashed by name | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:157` |
| Column-add precedent for an entity field | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:170` (`carried_loam`) |
| World stocks live on the sector, not in a warehouse | `gk-core/src/FusionRpg.Core/World/WorldState.cs:181,187` |
| The two in-`Step` sites that remove a legion: a destroyed battle side, and a starved legion | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:33-35`; `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:134-151` |
| Every other `Entities =` write in the World tree keeps or adds entities (raise, build, sustain, movement, supply recovery, rout clear, Unmade spawn) | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:102`, `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:148`, `gk-core/src/FusionRpg.Core/World/Movement/SustainResolver.cs:69`, `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:166`, `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:144`, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:177`, `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:243-247` |

### Wiring gap

- Bearers are never produced by raising: `FoundLegion` builds one `Fighter` (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:124-142`).
  Closed by `legion-build` `raise-choice`. Until then only template bearers exist, and this module is
  tested on fixtures.
- Headcount reads member **rows**. `legion-build` `member-stack` moves every headcount to `Σ Count`
  (`legion-build-map.md` X10). This module's bearer read goes through the same function
  `member-stack` rewrites (`LegionSupply.BearerCount`), so it follows automatically.

### Real gap (this module closes it)

The pool, its canonical rows and persistence, its capacity, the load/unload primitives, the removal
seam, and the `trade.fleet` capability flag.

## Design

### 1. State

`WorldEntity` gains `CarriedGoods : IReadOnlyList<CarriedGood>`, where
`CarriedGood(string GoodId, long Qty, long Load)` — the quantity carried and the load units it occupies.
`Load` is stored because a parcel's load depends on the sector it was loaded at (`loadOf`'s scale), which
the pool would otherwise forget. Invariants, asserted by `WorldValidation`: ordered by `GoodId` (ordinal);
no duplicate id; every `Qty > 0` and `Load > 0` (a zero entry is removed, never stored). Default empty.

### 2. What may be carried (closed rule)

A carriable id is either a **located good** (`sector-yield` `located-goods-registry`'s catalog) or one of
the two **construction world stocks** `rubble` and `ironwork` — exactly the set `logistics-flow` moves
(`logistics-flow-map.md` rule 7). Each id has one **holder** on a sector:

| Id class | Holder it loads from and unloads into |
|---|---|
| Located good | The sector's warehouse (`sector-yield` `located-stock`) |
| `rubble` | `WorldSector.RubbleStock` (`WorldState.cs:181`) |
| `ironwork` | `WorldSector.IronworkStock` (`WorldState.cs:187`) |

Never loam (its own axis, and *never traded or converted*, `empire-resource-ssot.md` §4 rule 4); never
recruits (an accrual meter, same file §3). An id outside the rule is refused at the call, loudly
(`InvalidOperationException`), because only code builds these calls.

### 3. Capacity

```
bearers   = Σ over Bearer members of LegionSupply.BearerCount's unit (row today, Count after member-stack)
capacity  = checked((long)bearers * Tuning.Fleet.GoodsPerBearer)          // load units, flat
free      = capacity - Σ CarriedGoods.Load
```

Capacity is flat because the scale is already inside every parcel's load (`loadOf`). A carried pool never
changes load in transit, so the only way it can exceed capacity is losing bearers, which `interception`
handles.

**Round 6 D2 — `Tuning.Fleet.GoodsPerBearer` is an interim for a Hub-composed channel.** D2 creates six
world derived channels plus their own program, `world-derived` (idea round later):
`world.carry.capacity`, `world.march.range`, `world.supply.burn`, `world.sight`, `world.hazard.resist`,
`world.upkeep.discount`, which *"compose in `ActorHub` like every other channel and roll up per stack and
legion the way `legion-power` does"* ([../decisions-round-4.md](../decisions-round-4.md) Round 6 D2). The
carry axis is **`world.carry.capacity`**, and W1 defines the roll-up exactly as this formula's shape:
Σ(unit count × that unit type's carry capacity).

- **When the channel exists, `capacity` is that roll-up read from Hub output** — one read, never a private
  formula and never a fleet-local fold of species, equipment, standard, doctrine or tradition contributions
  (the one-ActorHub-compose rule).
- **Stated default until `world-derived` ships:** `bearers × Tuning.Fleet.GoodsPerBearer`, exactly as
  written above — a per-unit-type capacity of `GoodsPerBearer` for `Bearer` members and 0 for every other
  role. The switch is then a change of *source*, not of shape, so this module's tests and acceptance do not
  change with it.
- **No spec here implements `world-derived`.** This module names the channel, the default and the shape.

### 4. Transfer primitives (pure, called inside `Step`)

```
Load(world, entityId, sectorId, goodId, requestedQty, allowanceLoad) -> (world', movedQty, usedLoad)
  budget   = min(free(entity), allowanceLoad)                         // load units
  movedQty = the largest q ≤ min(requestedQty, holderStock(sector, goodId))
             with loadOf(q, sector, goodId) ≤ budget                   // q = floor(budget × scale ÷ 1000), then checked
  usedLoad = loadOf(movedQty, sector, goodId);  pool[good] += (movedQty, usedLoad)

Unload(world, entityId, sectorId, goodId, requestedQty, allowanceLoad) -> (world', movedQty, freedLoad)
  movedQty  = the largest q ≤ min(requestedQty, carried(goodId), room(sector, goodId))
              whose freed load (below) ≤ allowanceLoad
  remaining = ceil(Load_g × (Qty_g − q) ÷ Qty_g)                       // a small remainder never rides free
  freedLoad = Load_g − remaining
```

The holder is the sector's (§2) unless the caller passes another: `goods-cargo-fate` passes a goods
cache as the holder when a legion picks one up. A site's allowance is spent in the same load units
(`spec-depot.md` §3), so a crew moves goods the way a lane does.

- `room` for a located good is the warehouse's free capacity (`sector-yield` `warehouse-axis`); for
  `rubble`/`ironwork` it is unbounded, because those stocks are *"uncapped by design"*
  (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:77-81`).
- `allowanceLoad` is what the site still has this turn, in load units; `depot` owns it. These primitives never check
  *where* a load is legal — the caller passes an allowance of 0 when it is not.
- Conservation is local: `Δholder + ΔQty = 0` per call (load units are a measure, not a stock). Every
  non-zero move writes one `trade-foundation` `stock-deltas` record (factKind `carry`) so the economy report reconciles.
  *(Audit 2026-09-20: `carry` is not yet a `FactKinds` member — `trade-foundation/spec-ledger-keys.md` §4a
  lists it as "used as if it existed … no ask filed". The ask is now filed: fleet-map A14. It widens the
  pinned vocabulary in this module's implementing change.)*
- A short move is not an error. It returns what moved; the caller writes the report token.

### 5. The removal seam

`CarriedGoods.OnEntityRemoved(world, entity, cause) -> world'` is called at every in-`Step` removal site, in
the same statement that drops the entity: `BattleApplication.cs:35` (cause `battle`) and
`LegionSupply.cs:148-151` (cause `starved`) today. **Wave-1 body:** the goods leave play as a declared sink —
one `goods.lost:<cause>` report entry per good and a `stock-deltas` record with factKind **`lost`** — so the
economy report counts them. `lost` is `trade-foundation`'s existing v1 kind for exactly this fact (*"a
holder's stock leaves the world with it (a legion destroyed or starved)"*, `spec-ledger-keys.md` §4); the
first draft named `loss`, which is `logistics-flow` `lane-loss`'s kind and would have merged two different
sinks in the economy report's P6 sink-share line (audit 2026-09-20). `goods-cargo-fate` later replaces the
body with a cache at the legion's last place; the call sites do not change. The seam exists now because a
legion can starve out of supply as soon as `trade-route-order` ships, and a silent drop would be a
conservation hole.

**A third removal site is coming (audit 2026-09-20).** `world-continuity` `advance-carry` removes every
departing legion inside `Step`, in `Snapshot`, through a new `AdvanceResolver`
(`../../world-continuity/spec-advance-carry.md` §1: *"every `depart`ing legion … is **removed** from the
world, its `CarriedLoam` is zeroed"*). A departing legion's carried goods must pass this seam too (cause
`departed`), or they either vanish unrecorded or ride into another world outside the priced crossing leg
(`rift-trade` `crossing-leg`) — a lossless, ungated second channel for located goods between worlds (P5).
**FQ3 / ask A15 are answered by round 6 S2, W1 and W2** ([../decisions-round-4.md](../decisions-round-4.md)
Round 6):

- **S2 — the channel:** *"Trade goods cross only through rift-trade routes. An advance is a weight-limited
  transit."* So an advance is never the commerce channel between worlds; the priced, bounded crossing leg
  (`rift-trade` `crossing-leg`) is, and the second lossless channel this section warned about does not
  exist.
- **W1 — the limit:** an advance carries *"a weight limit, like a spacecraft's payload"* —
  Σ(unit count × that unit type's carry capacity) read from `world.carry.capacity`, with **units and goods
  drawing on the same limit**. `world-continuity` `advance-carry` owns that arithmetic; this module supplies
  the load of each parcel (`loadOf`) and nothing else.
- **W2 — the rest:** import and export through the rift gate, and the gate's own weight limits, are
  **`world-transit`**'s, a named future program. *"Until it exists, `world-continuity`'s advance moves only
  what the weight limit allows, and goods cross by rift-trade route."*

**The rule this module states, replacing the old default.** At `depart` admission (owned by
`world-continuity`), goods still aboard are refused with `depart.goods-over-carry` when they do not fit the
advance's weight limit — the player unloads or ships them by route first. What does fit rides the advance
and is re-created in the destination world with the same factKinds, so conservation closes on both sides.
The `departed` seam body remains the backstop for anything that reaches it anyway: strip as
`goods.lost:departed` with factKind `lost`, the `loam.stripped` precedent — never a silent crossing.
`rubble` and `ironwork` aboard follow the same weight limit.

### 6. Canonical form and persistence

- One conditional row per carried good, `entity-goods  <entityId>  <goodId>  <qty>  <load>`, emitted in a new
  loop after the `sector-ironwork` loop (`WorldCanonical.cs:123-129`), entities in id order, goods in id
  order. **Append slot (audit M3):** four modules append after that loop, the canonical text is hashed, and
  the family order is fixed once in [../landing-order.md](../landing-order.md) §4 — `world-stamp`'s stamp
  row, `sector-yield` `located-stock`, `logistics-flow` `logistics-canonical`, **this module**. The rule is
  *"after the last conditional row present at landing"*, and only one module at a time appends. Never a column on the `entity` row (`WorldCanonical.cs:60-62`) — appending would move every
  prior hash, the failure `WorldCanonical.cs:90-94`'s comment records finding live.
- One packed column `carried_goods TEXT NOT NULL DEFAULT ''` on `rpg_world_entities` (table
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:92`), added with `EnsureColumn` like `carried_loam`
  (`:170`), written through the entity insert/upsert (`:360-362`) and read back with the row. Packed
  format `id=qty:load;…` in id order, empty when nothing is carried — the `logistics-canonical` packed-row
  rule.

### 7. Capability flag

`trade.fleet` joins `trade-foundation` `world-stamp`'s closed capability vocabulary (*"each flag is added
by the sub-program that ships its behaviour"*, `trade-foundation-map.md` §2.4). A world whose stamp lacks
it runs no fleet step; its carried pools stay empty; its canonical text is unchanged. The ruleset change
is carried by the stamp, never by a global `RulesetVersion` move (`logistics-flow-map.md` module 1; today
`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`, value 13 — re-cited 2026-09-20, the line had moved).

### 8. Fact tokens

This module creates `src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs` (new), the one closed list of
fleet report tokens, written as `TurnReportKinds.Event` details (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10`
— the existing kind; fleet adds no report kind). Its first members: `goods.lost`, `goods.load-short`,
`goods.unload-short`. Each later fleet module adds its own tokens to this list in its own change.

## Tunables

| Key | Unit | Home | Note |
|---|---|---|---|
| `fleet.goodsPerBearer` | load units per bearer (`lane-flow`'s unit) | `data/tuning/trade.v1.json` (new) | Decided by principle and published through `gk-core/tools/tuning/publish.py`; a missing key is a load rejection (T5), never a default |

**Power ladder (PS-5, `ssot-power-scale.md` §10).** The capacity is flat in load units because the scale
lives in `loadOf`, whose `scaleMilli` is `sector-yield` `essence-loop-read`'s read. That one scale read is
the `§10` row `lane-flow` lands in its own change (`../logistics-flow/spec-lane-flow.md`, *"§10 row lands in
the same change"*). This module adds **no** row and no private curve; a second row for fleet capacity would
be a second entry for one scale.

## Numeric types

Quantities, loads and capacity are `long`, `checked`; the capacity product widens before multiplying
(`(long)bearers * goodsPerBearer`). `loadOf` is `lane-flow`'s (`ceil(qty × 1000 ÷ scale)`, `checked`);
the inverse used to size a load multiplies before dividing. Overflow throws (`PRINCIPLES.md` §5); no
clamp. `Qty`/`Load` never go negative — a negative result throws.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldStoreTests|FullyQualifiedName~WorldGraphDiffTests"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/audit-overflow.py --targets A3
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                    MODIFIED — CarriedGoods field + CarriedGood record
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                MODIFIED — conditional entity-goods rows (§6)
gk-core/src/FusionRpg.Core/World/WorldValidation.cs               MODIFIED — pool invariants (§1)
src/FusionRpg.Core/World/Logistics/Fleet/CarriedGoods.cs  (new) — carriable rule, capacity, Load/Unload, OnEntityRemoved
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs    (new) — closed token list (§8)
src/FusionRpg.Core/World/Logistics/Fleet/FleetTuning.cs   (new) — the fleet section of trade.v1, host-injected (tunables-ssot: Core never reads a file)
gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs        MODIFIED — one call to OnEntityRemoved at :35
gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs             MODIFIED — one call to OnEntityRemoved for each starved legion
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs               MODIFIED — carried_goods column, write, read
gk-core/scripts/verification-boundaries.v1.json                   MODIFIED — a fleet owner boundary (see Hard edges)
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/         (new)
```

Every Core file lives under `src/FusionRpg.Core/World/Logistics/**`, so `trade-foundation` `routing-guard`
covers it (`logistics-flow-map.md` C8).

## Testing strategy

- **Capacity reads bearers only:** fixture legion 3 bearers + 1 fighter → `3 × goodsPerBearer` load
  units; add a fighter → unchanged; add a bearer → up by exactly `goodsPerBearer`.
- **One load unit:** loading the same quantity at a sector of scale 2000 uses half the load units it uses
  at 1000 (rounded up), exactly `lane-flow`'s `loadOf` — asserted by calling `loadOf` itself, never a copy.
- **Unload frees load fairly:** unloading all of a good frees all its load; unloading part leaves
  `ceil(Load × remainingQty ÷ Qty)`. Burn
  (`LegionSupply.Burn`) is asserted unchanged in the same test.
- **Load/unload conserve:** property test over random holders, requests, allowances and scales:
  `Δholder + ΔQty = 0` per call; used load ≤ free and ≤ allowance; a load past free capacity moves the
  largest quantity that fits.
- **Refusals by construction:** allowance 0 moves 0; an id outside the carriable rule throws.
- **Sparse and hash-neutral:** a world with every pool empty produces byte-identical canonical text to the
  same world before this module (compare against a stored pre-change fixture); two worlds differing only
  in an absent good write equal text.
- **Round trip:** save → load → hash with a non-empty pool; the packed column round-trips exactly. The
  store runs **in memory** (`DataTestStore.Create()`, `docs/contributing/testing-standard.md` R1); disk is
  not the subject here.
- **Removal seam:** a destroyed battle side and a starved legion, each carrying two goods, each produce
  one `goods.lost:<cause>` entry per good and matching `stock-deltas` records of kind `lost`; Σ before = Σ
  recorded loss. Once `advance-carry` lands, a departing legion carrying goods produces the FQ3 outcome and
  never a silent drop (one test, cause `departed`).
- **Every removal site passes the seam:** a source scan of `gk-core/src/FusionRpg.Core/World/**` lists every
  statement that drops a `WorldEntity` from `Entities` and asserts each one calls
  `CarriedGoods.OnEntityRemoved` (the three sites named in §5). A new removal site without the call fails.
- **Global conservation net:** over a scripted multi-turn run, Σ goods across warehouses, carried pools,
  world stocks and transit changes only by the recorded faucets and sinks (`stock-deltas` reconcile).
- **Flag off:** the same world without `trade.fleet` runs no fleet code (a spy on the fleet step records
  zero calls) and hashes as before.

## Boundaries

- **Always:** change carried goods only inside `Step`; one conditional canonical row per non-zero good;
  capacity from bearers only; a `stock-deltas` record for every move.
- **Ask first:** letting capacity read anything but bearers; carrying loam or recruits; a command kind for
  goods.
- **Never:** reuse `load-cargo`/`unload-cargo`; read the item overlay's capacity; drop goods at a removal
  site without passing the seam; a `const` for `goodsPerBearer`.

## Success criteria (contract)

1. Capacity is a function of bearer count only; fighters never change it; each parcel occupies
   `lane-flow`'s `loadOf` load units.
2. Load and unload conserve per good per call and never exceed any bound.
3. A world with no carried goods hashes, persists and replays byte-identically to today.
4. No in-`Step` removal of a legion drops carried goods without a recorded fate.
5. Save → load → hash round-trips with a non-empty pool.
6. Nothing runs without `trade.fleet`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CarriedGoods.Capacity/Free/Carried` | `depot` (allocation), `trade-route-order` (trip targets), `goods-cargo-fate` (claim capacity), `interception` (spill) |
| `CarriedGoods.Load/Unload` | `trade-route-order` (via `depot`'s allowance), `goods-cargo-fate` (claim uses `Load` from a cache holder) |
| `CarriedGoods.OnEntityRemoved` (seam) | `goods-cargo-fate` fills its body |
| `FleetFacts` token list | every fleet module; `trade-surface` `trade-lexicon`; `trade-stories` `trade-fact-source` |
| `trade.fleet` flag | every fleet step |

## Dependencies

`logistics-flow` `logistics-phase` (the step slot, between arrivals and banking), `logistics-canonical`
(packed-row rule); `sector-yield` `located-goods-registry`, `located-stock`, `warehouse-axis`,
`essence-loop-read`; `trade-foundation` `world-stamp`, `stock-deltas`. Optional: `legion-build`
`member-stack` (before it, one row counts one unit).

## Hard edges

- **New hashed state and a schema column.** Hash-neutral by the conditional-row rule; the legacy-world
  goldens are the proof, run at module end, not assumed.
- **Widens a closed vocabulary:** `trade.fleet` in `world-stamp`'s capability registry (a reviewed change).
- **Verification boundary.** Paths under `gk-core/src/FusionRpg.Core/World/**` resolve today only to the
  `core-fallback` owner in `gk-core/scripts/verification-boundaries.v1.json` (it carries no `verificationId`). The
  first implementing task adds a `core-world-logistics-fleet` owner boundary covering
  `src/FusionRpg.Core/World/Logistics/Fleet/**` and `tests/FusionRpg.Core.Tests/World/Logistics/Fleet/**`
  — the "unmapped path is a boundary defect" rule (`AGENTS.md` Verification boundary).
- Touches two shared files (`BattleApplication.cs`, `LegionSupply.cs`) by one call each; no rule in either
  changes. The third site (`world-continuity`'s `AdvanceResolver`, not yet built) gets its call in whichever
  of the two changes lands second (ask A15); the source scan (Testing strategy) fails until it does.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (Logistics phase), world entities and persistence, economy (located
    goods, world stocks, loss as a sink), tunables, numeric range.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/
    trade-network/**; this session wrote only under that path. session-boundary-check.py not run by me.
[x] Read this session: DESIGN-GATE.md (whole), PRINCIPLES.md (whole), fleet-map.md, trade-network-map.md,
    trade-network-ideal.md §7.6-§8.7 and §13-§14b, legion-build-map.md (whole), legion-build-ideal.md
    §6.3-§11, logistics-flow-map.md (whole), sector-yield-map.md (whole), trade-foundation-map.md §2.4,
    empire-resource-ssot.md (whole), empire-economy-ssot.md §5-§6, economy-principles.md P1-P2, P9-P14,
    battle-engine-ssot.md §1, §5. Skimmed by heading only: match-runtime.md, unique-actor-runtime.md
    (lawn specimen lifecycle; this module touches neither), world-map-runtime-* (UI).
[x] decisions.md: phase-order row (the Logistics slot is sector-yield's amendment), Empire resource
    registry, Scoped inventory hierarchy (items stay Data-side; goods are hashed — different class).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: bearer rule, removal sites (every `Entities =` write read), canonical
    conditional rows, cargo kind names, column precedent.
[x] Surrounding sections read: LegionSupply's class comment and Resolve pass; WorldCanonical's
    faction-scope and structure-state comments; BattleApplication's header.
[~] Constraints tested: none claimed as measured. "Hash-neutral" is an acceptance criterion proven by
    the legacy goldens when built.
[x] No §2 invariant contradicted: in-Step determinism, no cap (a per-legion capacity grows with bearers
    and the scale read), long + checked.
[x] Corrections propagated: fleet-map.md updated in the same change (C8-C13).
[x] No population pinned; the token list is a closed vocabulary with its reason.
[x] No event-refreshed cache (capacity is computed at the call).
[x] No ordering-fixed criterion.
[x] No actor magnitude produced or consumed.
[x] No SOLID fork: one capacity axis, one removal seam for two sites, lane-flow's load unit reused.
[ ] Registry rows: "no removal site drops carried goods" wants a guard or an unguardableReason in
    gk-core/scripts/enforcement-registry.v1.json when its test lands — owed by the implementing task. Named
    (audit 2026-09-20): invariant id `fleet-carried-goods-removal-seam`, source
    `docs/architecture/trade-network/fleet/spec-carried-goods.md §5`, covered by the source-scan test
    above; until a guard script exists the row carries an unguardableReason naming that test.
```

## Audit 2026-09-20

Independent audit against the checklist in `fleet-map.md` *Audit 2026-09-20*. Fixed here: the removal-seam
fact kind (`loss` → `lost`); a third in-`Step` removal site (`world-continuity` `advance-carry`) and its
default (§5, owner question FQ3); the `carry` kind ask (A14); the stale `RulesetVersion` citation; the
in-memory store statement; the §10 power-ladder statement; a source-scan test that every removal site
passes the seam; the named registry row.

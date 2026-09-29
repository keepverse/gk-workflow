# Spec: `transit-buffer`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `transit-buffer`, row 5 of the
[logistics-flow map](../logistics-flow-map.md) (wave 2; depends on `lane-flow`, `path-cache`,
`logistics-canonical`; reads `sector-yield` `warehouse-axis` and `bank-points`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §8.2 (*only incoming deliveries overflow and
waste*), §8.4 (*transit time is `ceil(path LaneCost ÷ speed)`; a cut lane strands what is on it*), §6
lesson 6 (no rating spiral), §9 (cost grows with routes × goods × transit turns, never with volume).
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make goods take time to travel, and make that travel something a cut can interrupt. A departure
becomes a **packet** that walks its route lane by lane at the goods' speed, arrives a fixed number of
turns later, unloads into the destination warehouse, and — if the path is cut under it — stops where it
is and waits. It owns three steps of the phase: **L1** arrivals (and returns), **L4** delivery
overflow, and the **movement** half of L5.

Success looks like: goods sent on turn *t* along a path of transit *k* are delivered on turn *t + k*
exactly, absent a cut; every route's goods reconcile every turn; a cut strands, a restore resumes, a
`route-clear` returns — and nothing is ever created.

## Locked anchors

- **Nothing per unit** (ideal §8.1, D5). One packet per route per departure turn; never a crate, never
  a vehicle.
- **A bounded buffer.** A route holds at most `route.maxTransitTurns` live packets — a **structural**
  limit on how much in-motion state one route may keep (the hashed state stays proportional to
  routes × transit turns), commented as such in code, exempt from PS-8 as a buffer size
  (`docs/architecture/power/ssot-power-scale.md` §11.3's class).
- **Resumable position is the precedent.** A march resumes mid-lane from stored progress and heading
  (`gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-31`; heading and progress fields
  `gk-core/src/FusionRpg.Core/World/WorldState.cs:299-308`). A packet stores the same two things.
- **No rating spiral** (ideal §6 lesson 6). A stranded route's recovery never depends on its own past.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Mid-lane resume from `OnLaneId` + `OnLaneTowardSectorId` + progress | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-45` |
| A severed lane refuses a march | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:52` |
| Lane cost in per-mille units of a turn's base movement | `gk-core/src/FusionRpg.Core/World/WorldState.cs:254-255`; `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:134-147` |
| Nothing writes `LaneState.Severed` today — only readers exist; cuts reach goods through gates, presence and ownership until a severing mechanic ships | `gk-core/src/FusionRpg.Core/World/WorldState.cs:51-55`; readers `gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:129`, `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:52` |

### Wiring gap

None.

### Real gap (this module closes it)

Packets, their movement, arrival and delivery, delivery overflow, stranding, resume and return.

## Design

### 1. The packet lifecycle

`TransitPacket` (shape owned by `logistics-canonical`) carries its route key, departure turn, `Qty`,
`Load`, the lane it is on, the end it heads for, progress along that lane, and a status:

| Status | Meaning | Leaves it by |
|---|---|---|
| `Moving` | On a lane, walking | reaching the destination (`AtDoor`); losing its way (`Stranded`) |
| `AtDoor` | At its destination, not yet unloaded | L1 unloading it (fully → removed; partly → stays `AtDoor`) |
| `Stranded` | Its lane or next hop is unusable; holds position | a usable next hop again (`Moving`); `route-clear` (`Returning`) |
| `Returning` | Its route was cleared while stranded | L1 returning it to the source |

### 2. Departure (called by `lane-flow` in L5)

A granted departure leaves the source warehouse and becomes one packet on the first lane of the path,
progress 0, status `Moving`, with `Load` fixed at the granted load. Two refusals come first, each a
bottleneck reason for `logistics-facts`:

- `too-far` — transit `k = ⌈dist(source) ÷ goods.speedPerTurn⌉` exceeds `route.maxTransitTurns`. The
  route is refused whole; a path is never truncated.
- `buffer-full` — the route already holds `route.maxTransitTurns` live packets (strands fill it). New
  goods wait at the source; this back-pressure reaches `production-halt` through the warehouse, which is
  how a cut eventually throttles the faucet without any rating.

### 3. Movement (L5, after departures)

Every `Moving` packet — new ones included — gets `goods.speedPerTurn` cost units this turn, in packet
order. It walks like a march: progress along its lane; at the lane's end it stands at the toward-sector;
if that sector is a valid destination for its route (own, and a root of the route's current tree) it
becomes `AtDoor` and stops; otherwise it takes `path-cache`'s next hop with the budget left. It becomes
`Stranded`, holding position, when its current lane stops being usable (Supply-lens traversable and the
toward-sector open to the faction), or when it stands at a sector with no next hop. A `Stranded` packet
re-checks at the start of each L5 and resumes as `Moving` the moment a usable next hop exists — with the
full turn's budget, from where it stood.

Packets follow the route's **current** destination tree, so a `route-set` that changes the destination,
a captured bank point, or a new bank point re-aims goods already on the road without storing a path.

**Timing.** A packet departs on turn *t* and walks on *t* itself. It reaches its destination during the
movement of turn *t + k − 1* and is delivered by L1 on turn *t + k*. With `k ≥ 1`, goods always spend at
least one End Turn on the road.

### 4. Arrivals and returns (L1)

In packet order:

- **`AtDoor` at any destination, bank point or not** → unloads `min(Qty, room)`, with
  `room = EffectiveCapacity − Occupancy` from `sector-yield` `warehouse-axis`. The rest stays `AtDoor`. At a
  bank point, L3 then banks up to its Counting House tier's rate, and L4 unloads again into the room that
  freed (round 4 made banking rate-limited, so a bank point is no longer an unbounded sink).
- **`AtDoor` at a sector that is no longer a valid destination** (captured, lost its bank point, policy
  changed) → back to `Moving`; it re-aims in L5.
- **`Returning`** → delivered in full to the source warehouse if the faction still holds the source;
  otherwise it vanishes, recorded as loss with cause `stranded`.

### 5. Delivery overflow (L4)

After banking, every packet still `AtDoor`, in packet order, first unloads `min(Qty, room)` into the room
banking freed; then each packet still `AtDoor` wastes `⌊Qty × warehouse.deliveryOverflowWasteMilli ÷ 1000⌋`
and records it as `logistics.overflow` (cause: the full warehouse). Only deliveries waste — production at
a full warehouse halts instead (`sector-yield` `production-halt`; ideal §8.2). A bank point overflows
only when deliveries outrun its banking rate and its storage together (spec-logistics-phase §Design 1).
The waste vanishes — a sink, never a faucet. A held sector with no storage building has only its small
base yard (round 5 A2, `sector-yield` `warehouse-axis` `warehouse.baseYard`); once that is full a delivery
to it waits and wastes, and `forecast-facts` names the answer (*build storage*). An unowned sector has no
room at all, but it is never a valid destination (destinations are own). *(Corrected in the audit of
2026-09-20: this said a sector with no storage building has no room, the round-4 rule A2 replaced.)*

### 5a. Every move is a stock delta (audit 2026-09-20)

Goods on the road stay inside `trade-foundation` `stock-deltas`' reconciliation on a **route holder**
(`StockHolderKind.Route`, holder prefix `r:` — `spec-ledger-keys.md` §4a, `spec-stock-deltas.md` §5), which
this module adds together with the `Holdings` widening that walks `WorldState.Transit`. Every quantity it
moves is recorded in the same statement that moves it, through the turn's `StockDeltaRecorder`
(`report.Stocks`), and a located good's warehouse side goes through `LocatedStockOps.Add` (its one writer,
`sector-yield` `located-stock`):

| Step | Sector side | Route side | Fact kind |
|---|---|---|---|
| Departure (L5, called by `lane-flow`) | source −qty | +qty | `depart` |
| Arrival (L1) and L4's second unload | destination +unloaded | −unloaded | `deliver` |
| Return (L1) | source +qty | −qty | `return` |
| Returned to a lost source (vanishes) | — | −qty | `loss` (cause `stranded`) |
| Delivery overflow (L4) | — | −wasted | `waste` |
| Lane loss (L6, `lane-loss`) | — | −lost | `loss` |

A world stock (`rubble`, `ironwork`) writes its sector side to `RubbleStock`/`IronworkStock` through
`construction-chain`'s goods accessor, with the same fact kinds. The route holder's owner is the packet's
faction.

### 6. Stranding, restore, clear — the three outcomes

- **Cut, then restored** → the packet resumes from its slot; its arrival is late by the turns it waited.
- **Cut, then cleared** (`route-clear`, resolved in `Snapshot` by `auto-banking`) → every `Stranded`
  packet of the route becomes `Returning` and comes home at the next L1. `Moving` packets of the route
  continue to the route's new default destination.
- **Cut and left** → the packet waits, takes its lane's loss every turn (`lane-loss`, cause
  `stranded`), and occupies one buffer slot.

### 7. Determinism, allocation, numbers

Packets are processed in canonical order (faction, source, good, departure turn). No RNG. Movement
walks runtime arrays and the path trees — no allocation after warm-up; a changed packet list is written
back once per turn (allocation proportional to routes that changed, spec-logistics-phase §Design 5).
`Qty`, `Load`, `ProgressCost` and budgets are `long`, `checked`.

## Tunables

| Key | Unit | Home | Class |
|---|---|---|---|
| `goods.speedPerTurn` | `LaneCost` per-mille units per turn | `data/tuning/trade.v{n}.json` | tunable |
| `route.maxTransitTurns` | turns | same | **structural** buffer bound, commented in code; kept in tuning because a balance pass may want longer routes (tunables-ssot §1 grey zone: *"when both readings are defensible, it is tunable"*) |
| `warehouse.deliveryOverflowWasteMilli` | ‰ per turn | same, **owned by `sector-yield`** with the warehouse axis | read here |

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.TransitBuffer"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/TransitBuffer.cs   (new) — departure checks, movement, L1, L4
src/FusionRpg.Core/World/Ledger/StockDelta*.cs         MODIFIED — StockHolderKind.Route; registry Holdings walk Transit
src/FusionRpg.Core/World/Ledger/LedgerKey.cs           MODIFIED — `r:` holder prefix; + depart/deliver/waste/return kinds
tests/FusionRpg.Core.Tests/World/Logistics/TransitBufferTests.cs   (new)
```

## Testing strategy

- **Exact timing:** departures along paths of cost `c` with speed `s` arrive at L1 of `t + ⌈c/s⌉`, for
  every `c` in a sweep that crosses lane boundaries mid-turn.
- **Conservation per route, every turn:** `inTransit(t+1) = inTransit(t) + departed − delivered − lost −
  wasted − returned`, and returned goods appear in the source warehouse.
- **Too far:** a path of transit `route.maxTransitTurns + 1` is refused with `too-far`; nothing departs,
  nothing is truncated.
- **Buffer bound:** a route with every slot stranded refuses new departures with `buffer-full`.
- **Cut then restore:** the packet resumes from its slot; cut then clear: the goods return and
  `sum before = sum after + loss`.
- **Order-independent:** a cut (a hostile legion marching onto the path) and a `route-clear` filed the
  same turn give the same final stocks in either filing order (both tested).
- **Re-aim:** a destination captured while a packet is on the road sends it to the new nearest bank
  point; nothing is delivered into the captured sector.
- **Overflow only after banking frees what it can:** a full policy destination wastes the stated fraction
  per turn; a bank point wastes nothing while arrivals stay within its banking rate plus its free room,
  and wastes exactly the stated fraction of what is still `AtDoor` once they exceed both (round 4 made
  banking rate-limited; the earlier "a bank point wastes nothing" is withdrawn).
- **Deltas close:** `stock-deltas`' reconciliation is empty every turn with packets in every status, and
  each row of §5a's table is exercised by at least one fixture.

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics).

## Acceptance (contract)

1. Absent a cut, goods sent on turn *t* with transit *k* are delivered on turn *t + k* exactly.
2. Per-route conservation holds every turn; returned, lost and wasted goods are accounted exactly.
3. A path longer than `route.maxTransitTurns` is refused with a reason, never truncated.
4. A cut strands; a restore resumes from the slot; a clear returns; nothing is created.
5. A cut and a `route-clear` in the same turn resolve the same in either filing order.
6. Only deliveries waste, and only what is still `AtDoor` after L4 has unloaded into the room L3 banking
   freed — so a bank point wastes only when arrivals outrun its banking rate and its storage together.
   *(Corrected in the audit of 2026-09-20: this criterion said "only at a non-bank destination", which
   contradicted §5 and `spec-logistics-phase.md` §Design 1 since round 4.)*
7. Every move in §5a is recorded as a stock delta on the right holder with the right fact kind;
   `stock-deltas`' reconciliation, with the route holder, is empty every turn.

## Hard edges

- **Ruleset / goldens:** runs only under **`trade.logisticsLanes`** (round 6 C1: `logistics-flow` wave 2,
  one bump for the wave — landing order row 6); no existing golden moves.
- **Severance:** no shipped code severs a lane. Tests set `State = Severed` in fixtures; live cuts today
  come from gates, hostile presence and ownership. When a severing mechanic ships, it needs no change
  here (`path-cache` T1 already sees it).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Packet movement and statuses | `lane-loss` (which lanes a packet occupied this turn), `logistics-facts` (strand, overflow, arrival), `forecast-facts` |
| `too-far`, `buffer-full` reasons | `lane-flow`, `logistics-facts` |
| Returning on `route-clear` | `auto-banking` |

## Boundaries

- **Always:** one packet per route per departure turn; canonical order.
- **Ask first:** more than one packet per departure turn; a queue at intermediate sectors.
- **Never:** truncating a path; delivering into a sector that is not a valid destination; creating goods
  on return or restore.

## Design-gate checklist

```
[x] Subsystems: world turn engine (L1, L4, L5 movement), world lanes, warehouses (read).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md. Gap: spec-world-movement.md read at the cited
    line only.
[x] decisions.md: decision 22 (halt, not waste) respected — only deliveries waste.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: MarchResolver's resume and severed refusal; Severed has no writer.
[x] Surrounding sections read: MarchResolver's mid-march block.
[x] Constraints tested, not assumed: none claimed.
[x] §2 invariants: none contradicted; the buffer bound is structural and says so.
[x] Corrections propagated: L3-before-L4 order is stated here and in spec-logistics-phase.md.
[x] No population pinned.
[x] Event-refreshed cache: none here.
[x] Orderings: cut + route-clear tested in both filing orders.
[x] Actor magnitudes: none.
[x] No SOLID fork: path-cache's trees, warehouse-axis's room, MarchResolver's resume shape.
[x] Registry row: none owed.
[x] Audit 2026-09-20: goods on the road are recorded as stock deltas on a route holder (§5a); the stale
    no-storage and bank-point-never-wastes wording is corrected.
```

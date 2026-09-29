# Spec: `lane-flow`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `lane-flow`, row 4 of the
[logistics-flow map](../logistics-flow-map.md) (wave 2; depends on `path-cache`, `sector-yield` located
goods and `essence-loop-read`, `trade-foundation` `synthetic-graph`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §8.4 (*`Width` becomes throughput*), §9.2 rule 4
(*one flow pass plus at most one redistribution pass*), §14b (PS-5 scaled capacities; pro-rata contested
capacity, principle 10). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Turn `WorldLane.Width` — hashed, persisted and read by nothing today — into how much a lane can carry
per turn, and decide each turn how much of every route's goods leaves its source. Bounded work: one
priority pass and one redistribution pass, never a multi-commodity solve. Fair: when several empires
want one lane, it is shared in proportion to what each wants, never by faction id.

Success looks like: goods are conserved at every departure; no lane's committed flow exceeds its
capacity in any turn; two empires contending for one lane get shares in the ratio of their demand; and
scaling every good and its scale read by the same factor leaves the fraction of a sector's output a lane
can move unchanged.

## Locked anchors

- **`Width` becomes throughput** (ideal §8.4). Its comment says *"How large a force crosses at once"*
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:258-259`) but no code reads it — the only use is the
  canonical writer (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55-56`). Throughput is the one wired
  meaning; a later force-width rule must read the same field (map C3).
- **PS-5: capacity reads the same scale as the goods it carries** (`docs/architecture/power/ssot-power-scale.md`
  §10.4; ideal §14b). Capacity is counted in **load units** — goods normalised by the scale their own
  faucet reads (`sector-yield` `essence-loop-read`) — so throughput never becomes a hidden ceiling as
  `Θ` grows (PS-8, §11).
- **Every empire runs the same logistics** (ideal §3 principle 10). Contested capacity splits pro rata
  by demand across commanders; no tie ever favours a lower faction id.
- **A per-turn rate is a structural per-turn limit and says so** (umbrella §5 invariant 12). Lane
  capacity is per turn and grows without ceiling through `widen` (`lane-verbs`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Width` is on every lane, default 1000, hashed and persisted | `gk-core/src/FusionRpg.Core/World/WorldState.cs:259`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55` |
| No world template authors a `Width`; every shipped lane is at the default | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:166`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:249` (lane arrays with no `Width` set) |
| The content scale of a sector, already read by sector loot and siege loot | `gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:97`; `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15`, `:31` |
| Per-mille integer arithmetic discipline (`long`, divide by 1000 last) | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:138-144` |

### Wiring gap

`Width` has no reader (above).

### Real gap (this module closes it)

The capacity formula, the load unit, the two passes, the pro-rata split, per-lane utilisation and the
bottleneck reason for every short flow, and the `ssot-power-scale.md` §10 row.

## Design

### 1. Routes and demand

A **route** is `(faction, source sector, good)`. It exists this turn when the source is own, holds a
non-zero stock of the good, is not a bank point (goods at a bank point bank at L3 and never flow; what the
bank point's rate leaves stays there for the next L3), and a destination exists: the route's `RoutePolicy` destination if one is set and still valid, otherwise the
nearest own bank point (`auto-banking`). World stocks (`rubble`, `ironwork`) have no default destination
and form a route only under a policy (`construction-chain`). Loam never forms a route (ideal §3
principle 6).

**Consignments (exchange ask E-A5).** A faction's consignment at a foreign hub (`exchange` `exchange-hub`
§4) is a route source too: the source sector is the hub, the goods are read and written through the
consignment term `exchange` registers, and the path needs `passage` over the hub's ground (`path-cache`
T10). Arrivals into a foreign hub land as a consignment the same way. Lane-flow reads and writes every
holding — the owner's located stock, a world stock, a consignment — through one goods accessor, so no
step learns a fourth rule.

**Demand** `Dᵣ` is the route's whole available stock at the source, converted to load units:

```
loadOf(qty, source, good) = ceil(qty × 1000 ÷ scaleMilli(source, good))     // long, checked
```

`scaleMilli` is `sector-yield` `essence-loop-read`'s read — the same value the good's faucet at that
sector reads; a good whose faucet is flat (rubble, ironwork) reads 1000. Rounding the load **up** means a
small parcel never rides free.

### 2. Capacity

```
capacity(lane) = Width × lane.throughputPerWidth ÷ 1000       // load units per turn; long, checked
```

At the default `Width` of 1000 a lane carries `lane.throughputPerWidth` load units a turn. This is a
**structural per-turn limit** (a rate, not a stock ceiling) and the code says so in a comment; `widen`
raises it without limit.

### 3. The model — capacity is committed at departure

A route's path this turn is the next-hop walk from its source to its destination in `path-cache`'s tree.
Goods that depart this turn **commit** their load on **every lane of that path, for this turn**. A lane's
committed flow is the sum of the loads departing this turn on routes whose path crosses it, and it never
exceeds the lane's capacity. Packets already in transit do not commit again.

This is the pipeline model the ideal asks for (*"flow on a lane per turn is `min(demand on the lane,
Width × throughputPerWidth)`"*, §8.4). It is exact about what leaves each turn, needs no reservation
calendar and no queue at intermediate sectors, and keeps transit times exact absent a cut. What it
does not bound is a transient convergence — two packets that departed on different turns from
different distances entering one lane in the same turn. The map's acceptance *"no lane carries more
than its capacity in any turn"* is therefore stated here as **no lane's committed departures exceed its
capacity in any turn**. A literal per-turn crossing bound needs a per-lane future calendar re-planned on
every cut, which is the exact multi-commodity machinery §9.2 rule 4 forbids. Reported as a deviation.

### 4. Pass 1 — priority with pro-rata contention

For each lane, in lane-id order, with `T` the total demand of routes crossing it and `C` its capacity:

- `T ≤ C` → every crossing route's share on this lane is its demand.
- `T > C` → each commander `c` with demand `T_c` on the lane is allotted `⌊C × T_c ÷ T⌋`; the remaining
  units go one each to commanders in **turn-rotated order** (commanders sorted by id, then rotated left by
  `turn mod count`) — deterministic and even over time, never by faction id. Inside a commander, the
  allotment fills its routes by `RoutePolicy.Priority` (higher first; an auto-banking route has priority
  0), then route id.

A route's pass-1 grant `gᵣ` is the minimum of its shares over the lanes of its path.

### 5. Pass 2 — one redistribution

Residual `R_L = C_L − Σ gᵣ` over routes crossing `L`. Routes with `gᵣ < Dᵣ`, in order (priority desc,
turn-rotated commander, route id), each take `min(Dᵣ − gᵣ, min over its lanes of R_L)` and reduce those
residuals. One pass, then stop.

### 6. Departure

Granted load converts back to goods: `qty = Dᵣ == gᵣ ? available : ⌊gᵣ × scaleMilli ÷ 1000⌋` — never
more than is available, and the whole stock when the whole demand was granted. The quantity leaves the
source warehouse and becomes one new packet (`transit-buffer`), which fixes its `Load` at `gᵣ`; the move is
recorded as a `depart` stock delta, source −qty and route +qty (`spec-transit-buffer.md` §5a). What is
not granted stays at the source (it is not produced again; `sector-yield` `production-halt` stops the
faucet when the warehouse is full).

### 7. Utilisation and bottleneck reasons

For every lane with committed flow, the runtime records `(lane, committed, capacity)` per commander for
L8. Every route with `gᵣ < Dᵣ` records exactly one reason from the closed set `logistics-facts` owns:
`lane-capacity` (with the binding lane — the lane on its path where its share was smallest), or one of
the refusal reasons raised before capacity is considered: `no-path`, `contested` (the source is held
against the faction), `too-far`, `buffer-full` (the last two from `transit-buffer`).

### 8. Determinism, allocation, numbers

Lanes in id order; routes in (faction, source, good) order; commander order rotated by `turn`. All
arrays live in `LogisticsRuntime`; the passes allocate nothing after warm-up. Quantities are `long`;
products widen before multiplying and divide by 1000 last; `C × T_c` is computed `checked` — load units
are `Θ`-invariant by construction, so the product stays far inside `long`'s range, and an overflow
throws rather than wraps.

## Tunables

| Key | Unit | Home | Note |
|---|---|---|---|
| `lane.throughputPerWidth` | load units per turn at `Width` 1000 | `data/tuning/trade.v{n}.json` | Added through `gk-core/tools/tuning/publish.py trade --add-key`; the file is created by the first trade module to land (`trade-foundation` `economy-report`, or `sector-yield` `warehouse-axis`/`structure-upkeep` if either lands first). Missing key = load rejection (T5) |

`scaleMilli` is not a tunable here; it is `essence-loop-read`'s read. Values are decided by principle
and published; they are not owner questions (map assumption 5).

## `ssot-power-scale.md` §10 row owed (lands in the same change)

*Lane throughput in load units — `Width × throughputPerWidth ÷ 1000` against goods normalised by their
faucet's scale read. No curve of its own: the scale is `essence-loop-read`'s read of row 22
(`ContentScale`), so faucet, warehouse capacity and lane capacity move together (PS-5). A per-turn rate:
structural, commented, uncapped through `widen`.* Ordinal assigned when it lands (§10's rule).

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LaneFlow"
python scripts\audit-overflow.py --targets A3
python scripts\audit-magic-numbers.py --summary
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/LaneFlow.cs        (new) — demand, capacity, pass 1, pass 2, departure
gk-core/src/FusionRpg.Core/World/WorldState.cs                 MODIFIED — Width's doc comment: throughput (map C3)
src/FusionRpg.Core/World/Trade/TradeTuning.cs         MODIFIED — the Logistics block of the one trade tuning record
                                                       the first trade module creates (host-injected, T7.2)
data/tuning/trade.v{n+1}.json                          via gk-core/tools/tuning/publish.py (+ lane.throughputPerWidth)
docs/architecture/power/ssot-power-scale.md            §10 — one row
tests/FusionRpg.Core.Tests/World/Logistics/LaneFlowTests.cs   (new)
```

## Testing strategy

- **Conservation (every turn, every good):** stock before = departed + stock left at the source.
- **Capacity:** for every lane and turn, committed departures ≤ capacity (property over seeded runs on
  the synthetic graph).
- **Pro-rata:** two commanders with demand `d1`, `d2` on a lane of capacity `c < d1 + d2` receive
  `c·d1/(d1+d2)` and `c·d2/(d1+d2)` within one unit; swapping the two faction ids changes nothing but
  which id holds which share. Over a run of `n` turns, remainder units alternate (rotation).
- **Θ invariance:** multiply every good's faucet and its scale read by the same factor; the fraction of
  each sector's output that departs each turn is unchanged.
- **Priority:** within one commander, a higher-priority route is filled before a lower one on a shared
  lane.
- **Bottleneck reasons:** every short route carries exactly one reason; the closed set is pinned in
  `logistics-facts` with its reason for being closed.
- **Volume invariance:** multiplying every stock by 1000 changes no loop iteration count (instrumented
  runtime counter; `logistics-bench` re-checks it with allocation).

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics); the tuning loader's own tests where
the trade tuning record lives.

## Acceptance (contract)

1. Conservation holds per good, per route, per turn.
2. No lane's committed departures exceed its capacity in any turn.
3. Contested capacity splits pro rata by demand across commanders, within integer rounding, with
   remainders rotated by turn; faction ids never break a tie.
4. Scaling goods and their scale read together leaves every lane's movable fraction unchanged.
5. Every short route has exactly one reason from the closed set.
6. Stock volume never changes iteration counts.

## Hard edges

- **Ruleset / goldens:** runs only under **`trade.logisticsLanes`**, this module's own wave flag (round 6
  C1: `logistics-flow` wave 2, row 6 of [../landing-order.md](../landing-order.md) §2 — it used to gate on
  `trade.logistics`, which wave 1 registers, so a world stamped after wave 1 would have gained lane flow
  mid-life when wave 2 merged). The wave takes one `RulesetVersion` bump, shared with `path-cache`,
  `transit-buffer`, `lane-loss` and `logistics-facts`; no existing golden moves.
- **§10 row** lands in the same change (the power guard's closed inventory).
- **Deviation from the map:** acceptance 2 is stated on committed departures (§Design 3). Reported.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `LaneFlow.Run` (L5 departures) and the per-route grant/reason records | `transit-buffer`, `logistics-facts`, `forecast-facts` |
| `capacity(lane)` | `lane-verbs` (tests that widen raises it), `forecast-facts` |
| `loadOf(...)` | `fleet` `carried-goods`, `fleet` `depot` (their capacity axis reads the same scale, fleet map module 1) |
| The pro-rata split | `rift-trade` `crossing-leg` (the crossing reuses it; its `crossing.*` short reasons widen `logistics-facts`' set) |
| The goods accessor's consignment arm | `exchange` (registers the consignment term, E-A5) |

## Boundaries

- **Always:** stable order; turn-rotated commander order for every tie between commanders.
- **Ask first:** a third pass; per-good load weights (not in v1 — load is scale-normalised only).
- **Never:** an exact multi-commodity solve; a tie broken by faction id; a flat capacity against a
  scaling good.

## Design-gate checklist

```
[x] Subsystems: world lanes, turn engine (L5), power scale (PS-5 read), tunables.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md (incl. ssot-power-scale §10.2, §10.4, §11 and
    tunables-ssot §1-§3, §7). Gap: economy-principles.md not read in full.
[x] decisions.md: Power scale and Magic numbers rows respected (row owed, key in tuning).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: Width's only reader is the canonical writer; no template authors Width.
[x] Surrounding sections read: PS-5 (§10.4) and PS-8 (§11) in full.
[x] Constraints tested, not assumed: none claimed.
[~] §2 invariants: none contradicted. One deviation from the map's acceptance named (§Design 3).
[x] Corrections propagated: the deviation is in this spec and the session report.
[x] No population pinned; reasons are a closed vocabulary owned by logistics-facts.
[x] Event-refreshed cache: none here.
[x] Orderings: commander ties rotate by turn; pro-rata tested with ids swapped.
[x] Actor magnitudes: none.
[x] No SOLID fork: path-cache's trees, essence-loop-read's scale, one tuning file.
[ ] Registry row: "no tie by faction id" gets an unguardableReason or a test-backed guard row when
    the code lands.
```

# Spec: `crossing-leg`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19). Module 3 of `rift-trade`, wave 2. Every `file:line` below was opened this session.
Docs only. **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Price and bound the crossing between two worlds **like a lane** (world-continuity ideal §6.8; owner Q1): a
throughput per End Turn, a transit time, and a deterministic loss that vanishes — computed by
`logistics-flow`'s own functions with crossing tunables, never by a second formula. Let the player raise the
throughput by building (`widen`), on a rising price and with no ceiling.

Success looks like: a test that feeds a lane and a crossing the same numbers gets the same capacity and the
same loss; a crossing never carries more than its throughput in any End Turn; goods that depart at save counter
`c` are due at `c + crossing.transitTurns`.

## Scope and non-goals

**In scope:** route throughput from the two ends; its allocation across a route's goods and across routes that
share an anchor; transit time on the save counter; crossing loss; the `widen` verb aimed at an anchor.

**Not in scope:** moving goods and the crossing ledger (`crossing-handoff`); anchor capacity inputs
(`crossing-anchor`); sleeping ends (`sleeping-endpoint`); what may cross (`crossing-goods`).

**Deliberately absent from the crossing:** `ward` (the crossing has no siege meaning), hostile presence and
escort terms (nothing can stand on a crossing — nothing physically crosses, Q1).

## Locked anchors

- **One mechanism** (map rule 5; umbrella invariant 10): capacity scaling, the loss clamp and the widen price
  curve are `logistics-flow`'s functions called with crossing keys; labour-derived capacity is the Rift
  Anchor's own crew through `fleet`'s one `LabourCurve` evaluator (`crossing-anchor` §3; round 4 — the
  anchor is no longer a depot).
- **No fourth clock:** transit counts the save-scoped End Turn counter `world-continuity` adds.
- **PS-5:** throughput reads the same scale as the goods it carries (`sector-yield` `essence-loop-read`).
- **No hard ceilings:** width levels are uncapped; the price rises.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Lane cost is integer per-mille with widen-before-multiply discipline, the precedent for this arithmetic | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:105-147` |
| `WorldLane.Width` is hashed and read by nothing else; `logistics-flow` makes it throughput | `gk-core/src/FusionRpg.Core/World/WorldState.cs:256-257`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55-56` |
| `ward` is reserved for the unbuilt lane verb; nothing raises `Width` or `WardLevel` | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:43-47` |
| Build-slot resolvers run in `Snapshot` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:404` |
| Rubble and ironwork are per-sector `long` stocks | `gk-core/src/FusionRpg.Core/World/WorldState.cs:181`, `:187` |

### Wiring gap

None: every function this module calls is a `logistics-flow` deliverable that does not exist yet (`lane-flow`,
`lane-loss`, `lane-verbs`). That is a build-order dependency, not an inert path.

### Real gap

Crossing throughput and its allocation; the crossing's transit rule; crossing loss parameters; `widen` on an
anchor.

## Design

### 1. Throughput

For a route R from anchor A (world a) to anchor B (world b), at a resolution of world a:

```
capA  = crossing-anchor EndCapacity(a, A)                 // load units at A's scale, from world a's own state
capB  = crossing-anchor EndCapacity from the window's far-end row for B   // load units at B's scale
for each good g the route carries, the largest q with
    loadOf(q, A, g)              ≤ g's share of capA_remaining          // measured with A's scale read
    ceil(q × 1000 ÷ B.scale_milli) ≤ g's share of capB                  // measured with the far row's scale
```

**Units (corrected by the 2026-09-20 audit).** Each end's capacity is flat load units (`lane-flow`'s rule;
`crossing-anchor` §3), and a parcel's load depends on where it is measured (`loadOf`'s scale). The first draft
took `min(capA, capB)` as if both were "on the goods' scale"; two worlds can sit at different content scales,
so a parcel is measured against each end in that end's own units — the near scale from world a's state, the far
scale from the logged far-end row. PS-5 holds at both ends through `loadOf`, whose scale read is the §10 row
`lane-flow` lands; this module adds none.

- `capA_remaining`: routes sharing a source anchor split A's end capacity **pro rata by demand** (each route's
  demand is the sum of its shares, bounded by the stock at A), remainder by route id — `lane-flow`'s pro-rata
  rule, so the split does not depend on which route was created first. Within a route, goods take their share of
  the route's allocation in the player's listed priority, each up to its share.
- `capB` is B's whole end capacity. Several source worlds cannot coordinate at departure (they resolve at
  different times), so the destination bound is enforced **again at arrival**: B unloads at most its end
  capacity per resolution, and anything beyond waits in the crossing as `queued` (`crossing-handoff`), reported
  with the bottleneck reason `crossing.far-capacity`. For a single route, the departure bound means no queue
  ever forms.
- Bottleneck reasons (closed set, extending `lane-flow`'s): `crossing.near-capacity`, `crossing.far-capacity`,
  `crossing.no-stock`.

### 2. Transit

`arriveCounter = departCounter + crossing.transitTurns`, with `crossing.transitTurns ≥ 1` (a load rejection
otherwise). The crossing does not use `logistics-flow`'s `transit-buffer` store: that buffer is hashed per-world
state, and goods on a crossing belong to no world's hash (Q1). What the crossing shares with `transit-buffer` is
its **contract** — goods sent at `t` along transit `k` arrive at `t + k`, conservation per route — which
`crossing-handoff` asserts on the crossing ledger.

### 3. Loss

At departure, inside the source world's step:

```
lossMilli = LaneLoss.Milli(hazardMilli: crossing.hazardMilli,
                           hostilePresenceMilli: 0, perishMilli: goods.{id}.transitLossMilli,
                           wardLevel: 0, escortMilli: 0)                  // logistics-flow's function
lost      = checked((long)departed * lossMilli) / 1000                    // divide last
carried   = departed − lost
```

The clamp to `[0, 1000]` is `lane-loss`'s (a bounded ratio, exempt from the caps rule, commented there). Lost
goods vanish: they appear in no balance, ledger credit or cache. The dominant cause is `hazard` or
`perishability`, from `lane-loss`'s closed cause set.

### 4. `widen` on an anchor

The crossing is widened **one end at a time**, because each end's width level lives in its own world's hash
(`crossing-anchor` Design 3). The verb is `logistics-flow`'s `widen`, not a new kind: a `widen` naming a
`SectorId` that holds a working anchor and no `LanePath` targets the crossing there (ask A8 to `lane-verbs`). It
resolves in the `Snapshot` build slot beside the lane resolver, spends construction stocks (rubble, ironwork)
from **the anchor's own sector** by `crossing.widenCostCurve` at the next level, and raises
`CrossingWidthLevel` by one. The new level applies from the next resolution. Only the anchor's owner may issue
it; the AI would file it through the same path (routes are player-only today, so it never does).

## Tunables (`data/tuning/trade.v1.json`, new, through `gk-core/tools/tuning/publish.py`)

| Key | Unit | Principle |
|---|---|---|
| `crossing.transitTurns` | save End Turns, `≥ 1` | Longer than a typical intra-world route: the far world is far |
| `crossing.hazardMilli` | ‰, bounded ratio | Moving between worlds costs more than moving along a lane; the one sink this program adds |
| `crossing.widenCostCurve` | construction stock per level, rising | Same curve family as `lane.widenCostCurve`, steeper base: widening the scarce leg is dear |

`goods.{id}.transitLossMilli` is read from `logistics-flow`; `crossing.tearSiteBonusMilli` and
`crossing.widenStep` and the anchor's labour points `crossing.throughputCurve` are `crossing-anchor`'s (round 4;
the spec-time reuse of `fleet`'s `depot.throughputCurve` is withdrawn); the evaluator is `fleet`'s `LabourCurve`.

## Numeric types

Quantities and capacities `long`, `checked`, widen before multiplying, divide by 1000 last. Loss per-mille `int`
in `[0, 1000]`. Counters `long`. Price per level `long`, `checked` — a price that would overflow throws; no level is
refused for being high.

## Contract-level acceptance

1. **One implementation:** over a property sweep, a crossing and a lane given the same hazard and perishability
   produce identical loss (`LaneLoss.Milli`); a parcel's load at each end is `lane-flow`'s `loadOf`; the
   pro-rata split is `lane-flow`'s; the labour part is `crossing-anchor`'s
   `LabourCurve.Eval(crossing.throughputCurve, labour)` — `fleet`'s one evaluator — never a crossing formula.
   *(The first draft named a `LaneFlow.ScaledCapacity` function `lane-flow` does not define — audit 2026-09-20.)*
2. Loss is in `[0, departed]` for every input, including raw terms below 0 and above 1000.
3. No route carries more than its allocation in any resolution; the load departing from one anchor, measured at
   that anchor's scale, never exceeds its end capacity, and the same departures measured at the far row's scale
   never exceed the far end capacity.
4. **Θ invariance:** scaling every scaled good's yield and the scale read by the same factor leaves the fraction
   of an anchor's stock one crossing can move unchanged.
5. `arriveCounter − departCounter = crossing.transitTurns` for every departure.
6. A `widen` on an anchor with insufficient construction stock is refused with a reason and spends nothing; an
   accepted one spends exactly the curve's price; each level's price is strictly greater than the last.
7. **Order-independent:** two routes from one anchor with demands `d1`, `d2` against capacity `c < d1 + d2`
   receive shares proportional to `d1 : d2` within integer rounding, and creating them in either order gives the
   same allocation (both tested).
8. A `crossing.transitTurns` of 0 is a load rejection naming the key.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Equivalence with lane functions, loss bounds, capacity bound, Θ invariance | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| `widen` on an anchor: price, refusal, rising curve | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift, World/Turn) |
| Tuning load rejection | `gk-core/tests/FusionRpg.Core.Tests` (tuning) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
python gk-core/scripts/audit-overflow.py --targets A3
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Hard edges

- **Always:** call `LaneFlow`/`LaneLoss`/the widen curve function; read every number from tuning.
- **Ask first:** a `ward` or escort term on the crossing; a transit that depends on distance between worlds (there
  is no distance between worlds today).
- **Never:** a second loss or capacity formula; a cap on width; goods in a hashed transit buffer; a new command
  kind for widening the crossing.

## Dependencies

| Consumes | From |
|---|---|
| `loadOf`, the pro-rata split, `LaneLoss.Milli`, the widen curve function, `widen` kind and admission | `logistics-flow` `lane-flow`, `lane-loss`, `lane-verbs` (ask A8) |
| Scale read | `sector-yield` `essence-loop-read` |
| End capacity; width field | `crossing-anchor` |
| Save counter | `world-continuity` `hibernation-clock` |

| Exposes | To |
|---|---|
| `routeCap`, the allocation order, `arriveCounter`, `lost`/`carried` | `crossing-handoff`, `sleeping-endpoint` |
| The three crossing bottleneck reasons | `rift-facts`, `trade-surface` |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/CrossingLeg.cs   NEW — allocation, transit, loss call (pure)
src/FusionRpg.Core/World/Logistics/LaneVerbs.cs          MODIFIED by lane-verbs' owner per ask A8 — anchor target
data/tuning/trade.v{n}.json                              PUBLISHED — three keys
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (Logistics phase, Snapshot build slot), lanes (functions only),
    tunables, numeric range, power scale (PS-5 read).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: as spec-rift-route.md, plus logistics-flow-map.md modules 4-8 in full.
[x] decisions.md: no lock on the crossing.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: Width has no reader; ward reserved; Snapshot slot position.
[x] Read surrounding sections: logistics-flow lane-flow, transit-buffer, lane-loss, lane-verbs.
[x] Constraints tested: none claimed.
[x] No §2 invariant contradicted: bounded ratio clamp only; width uncapped; one ladder (PS-5 read).
[x] Corrections propagated: the map's reliance on transit-buffer is narrowed to its contract, here
    and in the map.
[x] No population count pinned: bottleneck reasons are a closed vocabulary.
[x] Event-refreshed cache: none.
[x] Orderings: routes sharing an anchor split pro rata, so creation order cannot matter; tested
    both ways. (The map's "route-id order" would have made the result depend on creation order;
    corrected here and in the map.)
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: logistics-flow's functions, pro-rata rule and widen verb reused.
[ ] Registry row: "no second loss formula under World/Logistics/Rift" is proven by the equivalence
    test; an invariants row lands with it (named by the 2026-09-20 audit: `rift-one-loss-formula`).
```

## Audit 2026-09-20

Fixed here: a phantom dependency (`LaneFlow.ScaledCapacity`) and a unit mismatch — the route bound now
measures each parcel in each end's own load units, through `lane-flow`'s one `loadOf`; acceptance 1 and 3 and
the dependency table follow. Checked and clean: loss is `lane-loss`'s one function, clamped as a bounded ratio;
the width level is uncapped and its price rises; transit counts the save End Turn counter (no fourth clock);
shared-anchor routes split pro rata, order-independent. Crossing loss is the sink this program adds (P1): the
located-goods registry row's sink list gains "crossing loss" in the change that ships `crossing-handoff` (the
row is `sector-yield`'s; named here so the sink is not silent). **Verification boundary:** the
`core-world-logistics-rift` owner boundary named in `spec-crossing-anchor.md` *Audit 2026-09-20*; until it
lands the path falls to `core-fallback`.

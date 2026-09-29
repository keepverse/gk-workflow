# Spec: `crossing-handoff`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19); **reconciled with the round-4 owner decisions 2026-09-19**
([../decisions-round-4.md](../decisions-round-4.md) Q10: system-issued world commands use **one shared path,
built in `trade-foundation`**; B: each end is a Rift Anchor). Module 4 of `rift-trade`, wave 2. Every
`file:line` below was opened this session. Docs only.

**Term.** A *consignment* in this spec is a **crossing consignment** — a crossing-ledger row (code type
`CrossingConsignment`) — never `exchange`'s hub `Consignment` (a trader's goods at a foreign hub,
`../exchange/spec-exchange-hub.md` §4). The two never meet: goods leave a crossing into an anchor's
warehouse, not into a hub (map C10). **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Move goods out of one world's hash, hold them in a save-scoped **crossing ledger** while they cross, and move
them into another world's hash — with neither world ever reading the other, every step logged so each world
replays alone, and every unit accounted for.

Success looks like: 100 fire essence departs world A at save counter 40 with a 5% crossing loss; A's anchor
stock drops by 100 inside A's step; the ledger holds 95 in crossing; world B, active at counter 43, receives a
logged arrival and its step puts 95 into its anchor warehouse before banking; replaying A alone and B alone
reproduces both hashes; the ledger's events sum to zero in crossing.

## Scope and non-goals

**In scope (wave 2 — the first playable case):** departures from a world resolving a **full step**; arrivals
into a world resolving a **full step**; the crossing ledger (consignments and their append-only events); the
`rift-arrive` system kind; the two Logistics-phase steps; queuing at a full far end; conservation and
idempotency.

**Not in scope:** departures from and arrivals into a world resolving a `CoarseStep` or an idle collect
(`sleeping-endpoint`, wave 3 — until it lands, goods due into a sleeping world simply wait in the crossing,
conserved); refusal, return and suspension (`endpoint-loss`); report kinds (`rift-facts`).

Because only one map world is active per save, the wave-2 playable loop is: ship from the world you stand in;
the goods wait in the crossing; they land when you switch to the other world and it takes its first full step.

## Locked anchors

- **Q1 (owner):** nothing physically crosses; goods on a crossing belong to no world's hash.
- **Every cross-world effect is a logged input** (`world-continuity-map.md` assumption 4).
- **P14 ledger before balance** (`economy-principles.md` P14): the in-crossing balance is derived from
  append-only, deduped events.
- **Arrivals precede banking** in the `Logistics` phase (`logistics-flow-map.md` phase-internal order), so a
  delivery into an anchor that is also a bank point banks the same turn.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The commit transaction: barrier, command read, `Step`, diff, post-step Data passes, log insert, turn advance — in that order, one transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:519`, `:539`, `:601`, `:607`, `:621`, `:667`, `:687` |
| A post-step Data pass inside the same transaction is an established shape (the cargo pass) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:613-621` |
| The stored hash is recomputed after post-step passes that change hashed state | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:630-661` |
| `Step` is pure over one world's state and commands; `TurnResult` carries world, report, hash | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:8`, `:157` |
| The report is the engine's only output channel ("the report IS the log") | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35` |
| The P14 pattern: `INSERT OR IGNORE` on a unique dedupe key | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:147-150`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:684-695` |
| Report re-derivation replays only `Step` from the command log | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769-775` |

### Wiring gap

None in shipped code. The `Logistics` phase, located stock and stock deltas are sibling deliverables
(`sector-yield` `banking-fact`, `located-stock`; `trade-foundation` `stock-deltas`) — build-order dependencies.

### Real gap

The crossing ledger; the departure and arrival steps; the `rift-arrive` kind; queuing.

## Design

### 1. Where each half runs

| Half | Runs | Why there |
|---|---|---|
| Departure (stock leaves world a) | **Inside** world a's `Step`, `Logistics` phase, after banking and before the lane-flow pass | A hashed stock may change only inside `Step` (umbrella invariant 5). Taking the crossing's share before lane flow lets a route claim goods before auto-banking sends them home. **Consequence of the canonical order (audit 2026-09-20):** banking (L3) runs *before* rift departures (L4r), so an anchor whose sector is also a bank point banks its stock at the banking rate before the route can take it; only what banking leaves (the round-5 A4 hold keeps stock for other traders' open buy orders, not for routes) can depart. Place the Rift Anchor outside a Counting House sector, or see the report to `sector-yield` (rift-map *Audit 2026-09-20*, RX2) |
| Ledger write (goods enter the crossing) | Data, post-step, same transaction | The crossing is outside every hash |
| Arrival filing (goods due) | Data, before the command read (`RpgStore.WorldTurns.cs:539`), same transaction | So the arrival is in world b's command log and its replay reproduces it |
| Arrival (stock enters world b) | **Inside** world b's `Step`, `Logistics` phase arrivals step, before overflow and banking | Same reason as departure; before banking so a bank-point anchor banks the same turn |
| Ledger write (goods leave the crossing) | Data, post-step, same transaction | — |

Both steps live in `src/FusionRpg.Core/World/Logistics/Rift/` and are called from `logistics-phase`'s step list
(ask A11); they add no phase.

### 2. The crossing ledger (Data, Tier A, outside every hash)

**Consignment** (`rpg_rift_consignments`): one row per `(route, departCounter, good, leg)`, immutable once
written — `save_id, empire_id, consignment_key, route_id, leg ('out'|'return'), good_id, from_world_id,
from_sector_id, to_world_id, to_sector_id, depart_counter, arrive_counter`.

**Event** (`rpg_rift_events`): append-only, `UNIQUE(consignment_key, counter, kind)` —
`consignment_key, counter, kind, qty, world_id`. Closed kind set: `depart`, `loss`, `arrive`, `waste`,
`refuse`, `strand-lost`. (`refuse` and `strand-lost` are written by `endpoint-loss`.)

In-crossing balance of a consignment = `depart − loss − arrive − waste − refuse − strand-lost`. It is computed,
never stored. The `consignment_key` is the stable string of `(save, empire, route, departCounter, good, leg)`;
the world-fact keys that `trade-foundation` `ledger-keys` defines stay for world-stock rows (below).

### 3. Departure

The step reads each `rift-window` (`rift-route`) in the revealed commands. For each live route whose ends are
both working (`endpoint-loss`'s derivation, from the window), it computes the allocation, loss and arrival
counter by `crossing-leg`, then:

- decrements the anchor sector's located stock (or `RubbleStock` / `IronworkStock` for a world stock admitted by
  `crossing-goods`) by `departed`, through the `stock-deltas` recorder with fact kind `rift-depart`;
- emits a typed `RiftDeparture(routeId, goodId, departed, lost, arriveCounter)` on `TurnResult`, threaded like
  the stock-delta recorder (the engine writes nothing else);
- writes the report entries `rift-facts` defines.

Post-step, the store inserts the consignment and its `depart` and `loss` events (`INSERT OR IGNORE`).

### 4. Arrival

Before the command read, the store selects consignments whose `to_world_id` is the resolving world and whose
in-crossing balance is positive and `arrive_counter ≤` this commit's counter, and files — through
`trade-foundation`'s one system-command path (round-4 Q10; map ask A7) — one `rift-arrive` system
command per consignment, payload: consignment key, anchor sector, good, balance, leg. Its `CommandId` is
`rift:a:` + the first 16 hex digits of SHA-256 of `(consignment_key, counter)` — deterministic, and inside the
64-character bound admission keeps for every command id (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:15`).

The arrivals step, if the anchor is working:

- splits the anchor's arrival capacity (its end capacity, flat load units — `crossing-anchor` §3) across the
  due consignments **pro rata by load measured at this anchor's scale**, `loadOf(balance, anchorSector,
  good)`, remainder by consignment key — order-independent; a consignment's delivered quantity is the largest
  `q` whose load fits its share *(corrected by the 2026-09-20 audit: "pro rata by balance" compared raw
  quantities of different goods against a capacity in load units)*;
- delivers each share into the anchor warehouse (located goods) or sector stock (rubble, ironwork), recording
  `rift-arrive` stock deltas; a located-goods delivery into a full warehouse wastes the excess by the delivery
  rule (decision 22, `logistics-flow` `logistics.overflow`), so the record splits into `arrive` and `waste`;
- leaves the rest in the crossing (**queued**) with the bottleneck reason `crossing.far-capacity`;
- emits a typed `RiftArrival(consignmentKey, arrived, wasted, queued)`.

If the anchor is not working, the step emits `RiftArrival(…, refused = balance)`; `endpoint-loss` owns what
follows. Post-step, the store appends the `arrive`, `waste` or `refuse` events.

An arrival whose counter is already past lands at the resolving world's **current** step — never in a past turn.

### 5. Ledger facts for world stocks and the fact vocabulary

Every stock change above is a `stock-deltas` record (`rift-depart`, `rift-arrive`) so `trade-foundation`'s
`world-stock-ledger` and economy report see it. The two fact kinds widen `ledger-keys`' closed vocabulary by a
reviewed change (ask A10).

### 6. Hash and stamp

The departure and arrival steps run only on a world whose stamp grants **`trade.riftCrossing`** — the flag
of **`rift-trade` wave 2**, which this module and `crossing-leg` share, registered here with the one
`RulesetVersion` bump that wave takes (round 6 C1; row 21 of [../landing-order.md](../landing-order.md) §2).
It is **not** a widening of wave 1's `trade.riftTrade` (`rift-route`, `crossing-goods`,
`crossing-anchor`, row 20): a world stamped after wave 1 has routes and anchors but must not start moving
goods mid-life when wave 2 merges, which is the audit's C1 defect. A world without the flag never receives a
window or an arrival (`rift-route` refuses to set a route to it), so its hash, turn for turn, is what it
would be without this module. The stamp, not a global `RulesetVersion` move, is the version gate
(`logistics-flow-map.md` C2).

## Tunables

None owned here. Numbers come from `crossing-leg` and `crossing-anchor`.

## Numeric types

All quantities `long`, `checked`; events store `qty` as `INTEGER` (64-bit). Counters `long`.

## Contract-level acceptance

1. **Conservation across worlds, per good, at every counter:** `Σ depart = Σ loss + Σ arrive + Σ waste +
   Σ refuse + Σ strand-lost + in-crossing` (reconciliation over a scripted multi-world run).
2. Source stock change for a departure equals `depart` exactly; destination stock change equals `arrive`.
3. **Idempotent:** retrying a commit that failed after filing writes no second consignment, event or command
   (dedupe on the keys above); a successful commit cannot be repeated (`turn.stale`).
4. A player- or AI-filed `rift-arrive` is refused `kind.system-only`.
5. Each world replays byte-identically from its own command log with the other world's rows absent from the
   store.
6. **Order-independent:** two consignments arriving at one anchor in the same step, over its capacity, split pro
   rata; creating their routes in either order gives the same result (both tested).
7. A delivery into an anchor that is a bank point banks in the same step (the arrival precedes `banking-fact`).
8. A goods row due into a sleeping world stays in the crossing, balance unchanged, until that world resolves.
9. A world without `trade.riftCrossing` hashes byte-identically to the same world before this module; a
   world with `trade.riftTrade` but not `trade.riftCrossing` has routes and anchors and moves no goods.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Departure and arrival steps (pure), pro-rata split, overflow split | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| Ledger, dedupe, filing before the command read, conservation over a two-world run | `gk-core/tests/FusionRpg.Data.Tests` (in memory) |
| Replay each world alone | `gk-core/tests/FusionRpg.Data.Tests` |
| System-only refusal | `gk-core/tests/FusionRpg.Core.Tests` (World/Turn) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
python gk-core/scripts/guard-dal.py
```

This module crosses Core and Data: run the full suite once at its end (AGENTS.md verification point 2).

## Hard edges

- **Always:** change hashed stock only inside `Step`; file arrivals before the command read; append events,
  never update them; one transaction.
- **Ask first:** goods that cross without a crossing loss; any retroactive delivery.
- **Never:** a world reading another world's rows inside `Step`; goods on a crossing inside any world hash; an
  arrival applied Data-side after `Step` (replay would not reproduce it — `RpgStore.WorldTurns.cs:769-775`
  replays `Step` only); a stored in-crossing balance.

## Dependencies

| Consumes | From |
|---|---|
| Route window, route lifecycle | `rift-route` |
| Allocation, loss, arrival counter | `crossing-leg` |
| Anchor working predicate, arrival capacity | `crossing-anchor` |
| Goods admission (located goods vs world stock) | `crossing-goods` |
| `Logistics` phase step list (arrivals first; departures between banking and lane flow) | `logistics-flow` `logistics-phase` (ask A11) |
| Located stock and warehouse | `sector-yield` `located-stock`, `warehouse-axis` |
| Stock deltas; fact kinds | `trade-foundation` `stock-deltas`, `ledger-keys` (ask A10) |
| Save counter | `world-continuity` `hibernation-clock` |
| The system-command path (closed system-kind set, `kind.system-only` refusal, one filing path in the commit) | `trade-foundation` `system-commands` (round-4 Q10; map ask A7) |

| Exposes | To |
|---|---|
| Consignments and events; `RiftDeparture` / `RiftArrival` | `sleeping-endpoint`, `endpoint-loss`, `rift-facts`, `trade-foundation` `economy-report` |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/CrossingHandoff.cs   NEW — departure and arrival steps (pure)
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs                  MODIFIED — TurnResult carries the typed rift records
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs                MODIFIED — rift-arrive registered in trade-foundation's system-kind path
src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs             MODIFIED — consignments, events, filing, post-step write
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs             MODIFIED — two calls in the commit
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (Logistics phase), world store (command log, commit), economy
    (located goods, world stocks, P14 ledger), save identity keying.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: as spec-rift-route.md; the whole CommitWorldTurn body; P13-P14.
[x] decisions.md: world-turn phase order (via logistics-flow's C1 and sector-yield banking-fact).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: the commit order, the post-step re-hash, the replay loop.
[x] Read surrounding sections: the cargo pass and budget-debit re-hash comments in full.
[x] Constraints tested: none claimed; "legacy worlds hash identically" is acceptance 9.
[x] No §2 invariant contradicted: SQL in Data; stock changes inside Step; determinism per world.
[x] Corrections propagated: arrival-side pro rata replaces the map's route-id order (order
    independence), in the map and here.
[x] No population count pinned: event kinds are a closed vocabulary.
[x] Event-refreshed cache: none — balances are computed from events.
[x] Orderings: arrivals at one anchor are pro rata; tested both creation orders.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: one commit transaction, one command log, stock-deltas and
    ledger-keys reused, one Logistics phase.
[ ] Registry row: "rift-arrive is system-only" and "no Data-side stock change after Step for
    rift" need invariants rows — land with the code (named by the 2026-09-20 audit:
    `rift-arrive-system-only`, `rift-no-post-step-stock-change`).
```

## Audit 2026-09-20

Fixed here: the arrival split compared raw quantities against a capacity in load units — it now measures each
due consignment with this anchor's `loadOf`; the departure row states the consequence of the canonical L3-before-L4r
order for an anchor in a bank-point sector. Checked and clean: conservation across worlds per good; P14 dedupe on
durable keys; the arrival is a logged system command so each world replays alone; stock changes only inside
`Step`; ledger tests in memory. Reported (other program's file): `sector-yield` `banking-fact`'s hold (round 5
A4) covers other traders' buy orders but not route exports — rift-map RX2. **Verification boundary:** the
`core-world-logistics-rift` owner boundary (`spec-crossing-anchor.md` *Audit 2026-09-20*) for the Core half;
the full suite once at module end because the module crosses Core and Data.

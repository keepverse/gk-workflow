# Spec: `trade-route-order`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`); **reconciled with the round-4
owner decisions and with `exchange`'s consignment model 2026-09-19** (§Round 4 below). Every `file:line`
below was opened in this session. Module id `trade-route-order`, row 4 of the [fleet map](../fleet-map.md) (wave 2; depends
on `carried-goods`, `depot`, `crew`, and `legion-build` `standing-orders`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §8.1 (*"Caravan — an ordinary legion running
a trade route automatically, with or without a commander"*), §8.3, §7.6;
[legion-build-ideal.md](../../legion-build-ideal.md) §6.3, §6.5. Owner decisions 2026-09-19 (recorded in
the map): **Q1** and **standing-order kinds**. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Round 4 (2026-09-19) — what changed

- **Caravans load and unload only at a working own caravan building** (Caravan Yard, T1; Convoy Depot, T2 —
  [decisions-round-4.md](../decisions-round-4.md) B). A route's source must hold one; an own destination
  must hold one. An own trade hub alone no longer qualifies (`spec-depot.md` §2).
- **A foreign hub is served through `exchange`'s consignment** (`exchange/spec-exchange-hub.md` §4), not by
  settlement reading the carried pool. The first draft had settlement debit the carried pool directly;
  `exchange` instead made a consignment the one record of a third party's goods at a hub, with fleet as a
  writer. Two records for one thing would be a parallel path, so this spec adopts the consignment (map C19).
- **The return leg exists.** The map says caravans carry *"a foreign hub's filled orders"* home when no open
  path reaches it; the first draft had no leg that loads at the destination. `ReturnGoods` and two phases
  close it (§1, §5).
- **A cross-world route's in-world end is an own sector with a Rift Anchor** (round 4: the crossing end is
  the Rift Anchor, not a depot). A caravan delivers there only if that sector also holds a caravan
  building — it is then an ordinary own destination; lane flow serves it otherwise.
- **T2 range** reaches a caravan through `depot`'s provisioning term, read at admission by `DepotRange`.

## Objective

A legion given a **trade-route** standing order becomes a caravan: it loads goods at a source site,
marches to a destination, unloads, marches back, and repeats — every turn re-emitting ordinary commands
through the one command pipe. This module owns the order kind's payload, its loop state and transitions,
its resolver, the admission rules for setting it, and the rule that decides **whether a caravan is
needed at all**.

Success looks like: a caravan with capacity 60 on a 2-turn-each-way route with one turn loading and one
unloading delivers 60 units every 6 turns, less anything lost to interception, without the player touching it; the same order
on a legion with no commander member produces the same commands; when an open lane-flow path to the
destination appears, the caravan stops starting new trips and says why.

## Locked anchors

- **Owner decision Q1 (2026-09-19): goods travel by lane flow wherever an open path exists; a caravan
  runs only where the path crosses closed ground or another world.** The predicate "an open path
  exists" is `logistics-flow` `path-cache`'s traversal — the one rule lane flow itself uses — never a
  second one (§Design 4).
- **Owner decision (2026-09-19): standing orders carry a kind, and each kind has its own resolver** (a
  request to `legion-build`, recorded as decided). `trade-route` is one kind; it expresses the
  load–march–unload–return loop. `legion-build` `standing-orders` owns the store, the set/clear command,
  explicit-order precedence, the emitter and its merge site (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:241-246`
  is where AI orders merge today). This module never stores, re-emits or replays an order itself.
- **A caravan is a legion** (owner ruling L3; ideal §8.3). Every caravan's `Kind` is
  `WorldEntityKind.Legion` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:61-68`); `Caravan` is retired by
  `legion-build` `caravan-kind-retire`.
- **Re-emit only existing command kinds.** The order produces `move` or nothing
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:13`); the engine sees no new movement path. A march
  resumes mid-lane because the re-issued path is resumed from the current lane
  (`gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:27-35` — whose comment already names a standing order).
- **Hashed state changes only inside `Step`** (P13). Loop transitions happen in the Logistics phase; the
  pre-`Step` resolver only reads.
- **`caravan-send` is the player's name for setting this order, not a command kind** (ideal §8.7 lists it;
  one set command for every standing-order kind is the SOLID shape).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| One command shape for every commander; the AI builds one per legion | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:137-217`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-584` |
| A believed-view, fewest-lanes path search (open, ungated, one-way-respecting lanes) | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:525-566` (private today) |
| Mid-lane resume of a re-issued path | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:27-35` |
| Reveal re-checks legality, drops a routed legion's orders for one turn, drops a `move` from a holding legion | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:208-256` (`:229-235`, `:242-249`) |
| Zone of control: a hostile projecting entity in a sector halts a marcher there; every non-guard entity projects | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:3-8,15-16,29,32-41` |
| Every other faction is hostile today | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` |
| Item-cargo act prices are a Data-side post-`Step` debit on item kinds only | `docs/architecture/world-action-economy/spec-budget-debit.md` §Design 2 |

### Wiring gap

None in shipped code: standing orders do not exist yet (`legion-build` `standing-orders`, real gap per
`docs/architecture/world-stage/spec-world-commands.md` as `legion-build-map.md` §5.8 cites).

### Real gap (this module closes it)

The kind, its payload and loop state, its transitions and resolver, the need rule, admission, the
caravan fact tokens, and the shared believed-view planner lift.

## Design

### 1. Payload and loop state

```
TradeRoutePayload
  SourceSectorId        own load site where trips start
  DestinationSectorId   an own load site (incl. one in a Rift Anchor's sector); or (with exchange) a foreign hub
  Goods                 ordered list of (GoodId, PerTripQty > 0) carried out; ids carriable (carried-goods §2)
  ReturnGoods           ordered list of (GoodId, PerTripQty > 0) carried back from a foreign hub; may be empty

TradeRouteState       (hashed; lives in legion-build's per-order state record)
  Phase   ∈ { Loading, Outbound, Unloading, ReturnLoading, Inbound, HomeUnloading, Idle }     closed enum
  Reason  token from FleetFacts, or none
```

The phase enum is a closed vocabulary pinned by a membership test with its reason (a reviewed change
adds a phase). `ReturnLoading` and `HomeUnloading` were added 2026-09-19 for the return leg; a route with
empty `ReturnGoods` and nothing aboard passes through both without spending a turn in them.

### 2. Admission (called by `legion-build`'s set command, through `WorldCommandAdmission`)

Refused, each with a named reason: legion not the commander's (`route.not-yours`); no bearer
(`route.no-bearers`); source not an own sector with a caravan building (a structure whose feature is `caravans`,
`trade-foundation` `sector-features`), built or under
construction (`route.no-source-site` — a trade hub alone does not qualify, round 4); an own destination
without one (`route.no-destination-yard`); destination equal to source (`route.same-site`); a goods id not
carriable (`route.bad-good`); a world stock (`rubble`, `ironwork`) toward or back from a foreign destination
(`route.world-stock-abroad` — principle 7); `ReturnGoods` on a route to an own destination
(`route.return-own` — moving own goods between own yards is two routes, never one that fetches); a foreign
destination before `exchange` lands (`route.destination-unsupported`).

Admitted with a warning token, never refused: a round trip beyond the legion's loam leash
(`depot.beyond-leash:<turns>`, `spec-depot.md` §4, with the source site's provisioning term). Initial
state: `Loading` if the legion stands at the source, else `Inbound` (walk to the source first).

### 3. The resolver (pre-`Step`, pure; called by `legion-build`'s emitter)

```
TradeRouteOrder.NextCommand(view, entity, payload, state) -> WorldCommand?
  Outbound  -> move along BelievedPath.Path(view, entity, payload.DestinationSectorId)
  Inbound   -> move along BelievedPath.Path(view, entity, payload.SourceSectorId)
  Loading | Unloading | ReturnLoading | HomeUnloading | Idle -> null   (stay put; no command, no stance change)
  no believed path           -> null        (the Logistics step records caravan.stalled:no-path)
```

`BelievedPath.Path` is the believed-view search at `FrontierRulesPolicy.cs:525-566`, **lifted into one shared
function** that the AI and this resolver both call, over the owner faction's believed view (ideal §8.5:
*"Plan on believed … lane states; settle on the truth"*). The lift is a refactor with byte-identical AI
behaviour, proven by the AI goldens and `WorldAiCommitTests`; no second path finder is written. It lives
in `gk-core/src/FusionRpg.Core/World/Movement/` (it plans marches, not goods flow, so the `routing-guard`
namespace does not apply — it never touches `ReconnectionCost`).

Staying put emits nothing rather than `hold` (`spec-crew.md` §2's reason: a holding legion's `move` is dropped at
Reveal, `TurnEngine.cs:242-249`, and a stance flip every loop would be noise).

### 4. The need rule (Q1)

At the start of a trip — the Logistics step for a legion in `Loading` at its source —
`logistics-flow` `path-cache` is asked whether the owner faction has an **open lane-flow path** from the
source to the destination (`PathCache.Next(faction, destinationKey, source)` returns a hop —
`docs/architecture/trade-network/logistics-flow/spec-path-cache.md` interface; the caravan's destination is
registered as a destination key, map ask A9) (own and unheld ground, and `passage`-or-better foreign ground once `exchange`
`trade-access` lands; the Supply lens). If it has:

- the caravan loads nothing; any goods aboard are unloaded into the source (bounded as any unload);
- phase → `Idle`, reason `caravan.idle:open-path`; the order stays stored;
- each later turn re-asks; when the path closes (war, embargo, contested ground, a cut lane), phase →
  `Loading`.

A trip already `Outbound` when a path opens finishes its delivery — the goods are aboard, and turning
round would cost more than arriving. Lanes the Supply lens excludes (`deep`, `one-way`) count as "no open
path", because lane flow cannot use them; a caravan (March lens) can. This follows from using lane flow's
own predicate and is stated so no reader mistakes it for a third rule.

The rule binds every faction identically (principle 10). It is the reason a caravan exists: to trade
**through** a war, out of a severed component, across a rift lane, or to a crossing anchor lane flow
cannot reach.

### 5. Transitions (inside `Step`, the fleet step of the Logistics phase)

The fleet step is the slot `logistics-phase` reserves for fleet, **L2** — after arrivals (L1), before banking
(L3) (`docs/architecture/trade-network/logistics-flow/spec-logistics-phase.md` §Design 1;
`logistics-flow-map.md` *Phase-internal order*). Crew labour, loading, unloading and cache claims all run
there.
Legions are processed in entity-id order; site allowances are shared by `spec-depot.md` §3.

| Phase | This turn's step | Next phase |
|---|---|---|
| `Loading` at source | Need rule (§4). Else load each good toward `PerTripQty` via `CarriedGoods.Load` within the site allowance | `Outbound` when every good reached its target, **or** when this turn loaded nothing new and something is aboard (a partial trip — a caravan never waits forever for stock that is not coming). Stays `Loading` with `caravan.idle:no-stock` when nothing is aboard and nothing could load |
| `Outbound` | Arrival test: `AtSectorId == Destination` | `Unloading` on arrival |
| `Unloading` at own site | `CarriedGoods.Unload` within the allowance and warehouse room | `Inbound` when empty. A turn that unloads nothing because the warehouse is full keeps it `Unloading` with `goods.unload-short:warehouse-full` — the caravan is its own buffer; nothing is wasted (waste is only for lane deliveries, ideal §8.2) |
| `Unloading` at a foreign hub | Only at a `depot` `ForeignSite` — the hub's owner has a working Caravan Yard there (round 5 B3); otherwise the caravan waits with `depot.no-foreign-yard`. Move carried `Goods` into the caravan owner's **consignment** at the hub (`Consignment.Add`, `exchange/spec-exchange-hub.md` §4), bounded by the hub sector's warehouse room (consignments share it). `exchange`'s settlement, later in the phase, fills sell orders from the consignment (exchange ask A6, as answered) | `ReturnLoading` when the carried `Goods` are all consigned; stays `Unloading` with `goods.unload-short:warehouse-full` otherwise |
| `ReturnLoading` at a foreign hub | Load each `ReturnGoods` entry toward its `PerTripQty` from the owner's own consignment there (`Consignment.Remove`, `CarriedGoods.Load`), bounded by free carried capacity; `Access` must still allow the requester (`exchange` `trade-access`) | `Inbound` when every target is met, or when this turn loaded nothing new (a partial return — the caravan never waits forever for a fill) |
| `Inbound` | Arrival test at source | `HomeUnloading` if anything is aboard, else `Loading` |
| `HomeUnloading` at source | `CarriedGoods.Unload` within the allowance and warehouse room | `Loading` when empty; stays with `goods.unload-short:warehouse-full` otherwise |
| `Idle` | Need rule re-asked | `Loading` when a caravan is needed |

**Validity.** At every step, if the source or destination is no longer a valid endpoint (site captured
or destroyed; a foreign hub's access lost), the order does not stall on a lane: if the source is still an
own site, phase → `Inbound` with `caravan.suspended:<reason>` so the goods come home and unload there; if
the source itself is lost, phase → `Idle` with `caravan.suspended:source-lost`, goods stay aboard, and
the legion stays where it is until the player or AI changes the order. Goods aboard a caravan are never
touched by a counterparty's fate — they belong to the carrier (ideal §7.6, *"Goods in transit belong to
the buyer"*).

**Explicit orders win** (`legion-build`'s rule): a hand order for the legion this turn replaces the emitted
one; the loop state does not change, and because arrival is tested by position, a hand-marched caravan
that reaches its destination still unloads.

**Rout.** The emitted command is dropped for the recovery turn exactly as a hand order is
(`TurnEngine.cs:229-235`); the loop state is untouched and the next turn resumes.

### 6. Budget and cost

A caravan pays what every legion pays (ideal §8.3): its march spends `MovementRemaining`; loading and
unloading turns are turns it does not march. There is no act-price debit for goods — `budget-debit`'s
seam prices the Data-side item verbs only (`spec-budget-debit.md` §Design 2) and goods never reach it.
Loam burn applies out of supply as for any legion (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:124-151`).

### 7. Throughput is emergent

Nothing declares a route's throughput. Over *N* uninterrupted loops it is
`N × min(Σ PerTripQty, capacity) − goods lost to interception and cargo fate` per `N × round-trip turns`
(ideal §8.3, *"throughput = trips × capacity ÷ round-trip turns"*). *(Audit 2026-09-20: this formula still
subtracted "lane-borne loss" while the next sentence said there is none.)* A caravan on a lane takes lane
loss through `logistics-flow` `lane-loss` only if that module applies loss to carried goods; **it does
not** — lane loss is defined on lane flow (`logistics-flow-map.md` module 6). A caravan's risk is
interception, not attrition. The map's acceptance line *"goods delivered = N × per-trip quantity − lane
loss"* is corrected to *"… − goods lost to interception and cargo fate"* (map C12). "Capacity" here is in
load units: the per-trip quantity that fits is the largest `q` with `loadOf(q, source, good) ≤ free`
(`spec-carried-goods.md` §4), so the identity is asserted in load units at a fixed scale.

### 8. Fact tokens

Added to `FleetFacts`: `caravan.loaded`, `caravan.delivered`, `caravan.idle`, `caravan.stalled`,
`caravan.suspended`. `trade-stories` reads `caravan.delivered`/`caravan.suspended` through its
`trade-fact-source`.

## Tunables

None of its own. Per-trip quantity is player (or AI) policy in the payload; every number that bounds a
trip belongs to `carried-goods` (capacity) or `depot` (allowance).

## Numeric types

Quantities `long`, `checked`. Phases and reasons are enums/tokens, hashed by name
(`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:157`).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet|FullyQualifiedName~World.Ai|FullyQualifiedName~MovementTurnTests"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldAiCommit"
```

## Structure

```
src/FusionRpg.Core/World/Logistics/Fleet/TradeRouteOrder.cs  (new) — payload, state, admission, resolver, transitions, need rule
src/FusionRpg.Core/World/Movement/BelievedPath.cs            (new) — the lifted planner
gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs           MODIFIED — calls BelievedPath (no behaviour change)
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs       MODIFIED — caravan tokens
<legion-build's standing-order kind registry>                MODIFIED — one registration line
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/TradeRouteOrderTests.cs (new)
```

## Testing strategy

- **Only existing kinds:** over a scripted 30-turn loop, every emitted command's `Kind` is `move`; the
  engine's movement path is the ordinary one (no fleet type referenced from `MovementPhase`).
- **Commander-independent:** the same order on a legion with and without a Commander member emits the same
  commands turn for turn.
- **Replay:** a world stepped from its command log reproduces the state hash byte-identically (the emitted
  commands are logged; the loop state is hashed).
- **Emergent throughput:** fixture route, *N* = 5 loops, no contact: delivered = `5 × min(ΣPerTripQty,
  capacity)` exactly, and turns taken = `5 × round-trip` — an identity, not a pinned number.
- **Need rule (Q1):** (a) closed path → trips run; (b) open the path mid-`Loading` → `Idle(open-path)`,
  goods aboard return to source; (c) open the path mid-`Outbound` → the trip completes, then `Idle`;
  (d) close it again → `Loading`. **Order-independent:** setting the order before vs after the path opens
  gives the same first-trip turn (both tested).
- **Validity:** destination captured while `Outbound` → `Inbound` + `caravan.suspended`, goods unload at
  source; source captured → `Idle`, goods stay aboard.
- **Warehouse full at destination:** the caravan waits with its goods; nothing is wasted.
- **Foreign hub round trip:** a fixture foreign hub with open `market` access: carried `Goods` land in the
  owner's consignment (conservation: Δcarried + Δconsignment = 0 per good); `ReturnGoods` load from it; the
  caravan unloads them at home. A consignment belonging to another faction is never loaded.
- **Yard required:** a source or own destination with only a trade hub is refused with its reason.
- **AI parity:** an AI faction's legion with the same order behaves identically.
- **Kind:** every caravan in every test world has `Kind == Legion`.
- **Planner lift:** the AI golden set and `WorldAiCommitTests` are unchanged by the lift.

## Boundaries

- **Always:** emit `move` or nothing; transitions inside `Step`; the need rule through `path-cache`.
- **Ask first:** a caravan running where lane flow has an open path; lane loss on carried goods; a new
  command kind for goods.
- **Never:** store or replay an order here; a second path finder; a caravan-specific movement or battle
  path; construct `WorldEntityKind.Caravan`.

## Success criteria (contract)

1. A trade route re-emits only existing command kinds; the engine has no new movement path.
2. With or without a commander, the same order produces the same commands.
3. Replay reproduces the state hash byte-identically.
4. Over *N* uninterrupted loops, delivered goods and elapsed turns satisfy the emergent-throughput identity.
5. A caravan never starts a trip while lane flow has an open path; one already under way finishes.
6. Every faction runs the same order kind through the same admission.
7. Every caravan is a `WorldEntityKind.Legion`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `trade-route` kind + payload | `trade-surface` `trade-policy-editor`; `trade-ai` `ai-logistics` |
| `TradeRouteOrder.IsCaravan(entity)`, current phase | `trade-ai` (ask T-A2); `trade-surface` (caravan state); `escort-link` |
| Consignment writes at a foreign hub (`Unloading`, `ReturnLoading`) — `exchange`'s record, fleet as a writer | `exchange` `exchange-hub`, `settlement-payment` (fleet ask A6, as answered) |
| Destination may be an own yard in a Rift Anchor's sector | `rift-trade` (its ask A5) |
| `BelievedPath` | `crew`; `FrontierRulesPolicy` |

## Dependencies

`carried-goods`, `depot`, `crew` (labour behind the allowance); `legion-build` `standing-orders` with
per-kind resolvers; `logistics-flow` `logistics-phase` (slot), `path-cache` (a point query — map ask A9).

**Not `exchange` and not `rift-trade` (audit M1, edge 5).** Those were listed as *"later"* dependencies,
which reads as an upward edge in the family build order. The direction is the other way: this module
**exposes** the trade-route standing-order kind and its payload, and `exchange` (foreign hubs,
`trade-access`, consignments) and `rift-trade` (anchor sectors) consume it in their own waves — rows 18 and
20 of [../landing-order.md](../landing-order.md) §2, after this module's row 13. A destination this module
cannot resolve yet is refused at admission with its own token, exactly as an unknown sector is today; it is
never a compile-time dependency on a later sub-program.

**Round 6 C1 — the wave flag.** This module is `fleet` wave 2 and gates on that wave's flag
`trade.fleetRoutes`, registered with the wave's one `RulesetVersion` bump and shared with `crew` (row 13). It
does not widen wave 1's `trade.fleet`.

## Hard edges

- The planner lift touches the AI; it must be byte-identical (AI goldens run once at the lift).
- Loop state is new hashed state on `legion-build`'s order record; its stamp/ruleset change is
  `legion-build`'s.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: standing orders (legion-build), world movement and admission, logistics (path-cache),
    world AI (planner lift), economy (goods delivery).
[~] Session boundary: trade-network-idea-20260919 covers this path; check script not run by me.
[x] Read this session: as spec-carried-goods.md; legion-build-map §5.8-§5.9; logistics-flow-map
    modules 1, 3, 6, 7 in full; decisions-round-4.md; exchange/spec-exchange-hub.md §2-§4 (consignment).
[x] decisions.md: phase-order row (fleet step inside Logistics — no new phase).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding.
[x] Verified against code: MarchResolver resume comment, Reveal drops, AI path BFS, ZoC rule, command kinds.
[x] Surrounding sections read: TurnEngine Reveal/Step; FrontierRulesPolicy path search and Order builder.
[~] Constraints tested: "planner lift is byte-identical" is an acceptance criterion, not a measurement.
[x] No §2 invariant contradicted: deterministic, in-Step transitions, no cap on trips or caravans.
[x] Corrections propagated: C12 (lane loss is not applied to caravans) recorded in fleet-map.md.
[x] No population pinned; the phase enum is a closed vocabulary with its reason.
[x] No event-refreshed cache here (path-cache is logistics-flow's and lists its triggers).
[x] Orderings: order-before/after path opening; explicit vs standing order is legion-build's rule, both
    directions tested there.
[x] No actor magnitude.
[x] No SOLID fork: one command pipe, one planner, one traversal predicate, one standing-order store.
[ ] Registry rows: "every caravan is a Legion" wants a guard (source scan: no construction of
    WorldEntityKind.Caravan) once caravan-kind-retire lands — the enum member will not exist, so the
    compiler becomes the guard; an unguardableReason row is owed until then. Named (audit 2026-09-20):
    invariant id `fleet-caravan-is-legion`.
```

## Audit 2026-09-20

Fixed here: the emergent-throughput formula subtracted lane loss that §7 itself says a caravan never
takes; the identity is now stated in load units. Checked and clean: the resolver runs pre-`Step` over the
believed view and only reads (P13); transitions run inside `Step`; the need rule reads `path-cache`'s one
traversal (no second predicate); both orders of order-set vs path-open are tested; no command kind is added.
Reported to `exchange` (not this program's file): a foreign caravan's consignment shares the host's one
warehouse axis (`exchange/spec-exchange-hub.md` §4), so a visitor can fill a host hub's warehouse and halt
the host's own production (`sector-yield` `production-halt`) — a griefing vector against clans and rivals.
`exchange` owns the bound (for example, a consignment inflow cap tied to the host's open buy orders, the
round-5 A4 rule for holds). **Verification boundary:** the `core-world-logistics-fleet` owner boundary
(`spec-carried-goods.md` Hard edges); the planner lift under `World/Movement/` stays on `core-fallback` and
is proven by the AI goldens the Commands block names.

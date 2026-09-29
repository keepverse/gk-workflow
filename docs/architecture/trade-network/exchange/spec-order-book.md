# Spec: `order-book`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 7 of the [exchange map](../exchange-map.md) (wave 3; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.2, §7.6, §8.7, §14b
(*"contested capacity and fills split pro rata"*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

The standing trade order and the pass that fills it. A faction files `order-set` to place, replace or
cancel a standing buy or sell order at a hub sector; every turn, inside the `Logistics` phase, one
**exchange pass** gathers every open order at every hub, walks each hub's price curve once per good
and side for the whole aggregate, and splits the result **pro rata** among traders. The output is a
`FillSet` — units and walked value per trader, good and side — which `settlement-payment` pays for and
writes. Nothing in the result depends on filing order, command ids, or how an order is split.

## Scope and non-goals

In scope: the command kind and its payload; admission; the hashed standing-order record; where the
pass runs; suspension; the aggregate walk; capacity; pro-rata allocation; the fill record.

Not in scope: prices (`price-curve`); credit, souls, fees, tariffs and all writes (`settlement-payment`);
moving filled goods away (`logistics-flow`, `fleet`); deciding what an AI orders (`trade-ai`
`ai-bidding`).

## Design

### 1. `order-set` — one command, three verbs

A new kind in `WorldCommandKinds` (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121-126`, 18 kinds
today — a reviewed widening). Payload, as typed optional fields on `WorldCommand`
(`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:137-150`):

| Field | Meaning |
|---|---|
| `SectorId` (existing) | The hub sector |
| `GoodId` | The good |
| `OrderSide` | `buy` or `sell` — closed vocabulary (2) |
| `OrderQty` (`long`) | Units; **0 cancels** (the map's EC4: no separate cancel kind) |
| `OrderMode` | `total` (remaining decrements, closes at 0) or `per-turn` (refreshes every turn) — closed (2) |
| `LimitMilli` (`long?`) | Buy: highest per-unit ask accepted; sell: lowest per-unit bid accepted (value × 1000) |
| `SoulCapPerTurn` (`long?`) | Player only, buy side, bankable pool only: most souls this order may draw per turn |

The standing order is keyed `(CommanderId, SectorId, GoodId, OrderSide)`: an `order-set` replaces the
record with that key, and quantity 0 deletes it. Policy only — **filing moves nothing** (ideal §8.7).

### 2. Admission (cheap, at submit, `WorldCommandAdmission.Admit`)

Refusals with named reasons (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-40` pattern):
`order.no-capability` (stamp lacks **`trade.exchangeOrders`** — this pass's own wave-3 flag, corrected
2026-09-20 by reconciliation R-5; never `trade.exchange`, which is wave 2's); `order.sector-unknown`; `order.own-hub` (the
commander owns the sector at submit); `order.side-unknown`, `order.mode-unknown`; `order.qty-negative`;
the `tradeable-goods` refusals (`order.good-never-trades:{id}`, `order.souls-payment-only`);
`order.soul-cap-not-player`, `order.soul-cap-on-sell`, `order.soul-cap-map-bound`. Admission does **not**
judge `Access` or hub existence — those can change before the pass and are legality-at-settlement.

### 3. The standing-order record

`WorldState.TradeOrders`: hashed, sparse, canonical rows in key order; a world with no orders writes
no row, so a legacy world hashes byte-identically. Each record: key, `Remaining`, `Mode`, `Limit`,
`SoulCap`, `PlacedTurn`. `per-turn` orders reset `Remaining` to their quantity at the start of each pass.
This is a **faction-level policy record**, like `logistics-flow`'s `route-set` policy — not a legion
standing order. It never re-emits a command, so it is not a second standing-order mechanism beside
`legion-build`'s (cross-map decision CM5).

### 4. Where the pass runs

In the `Logistics` phase, in row **A1** of `logistics-flow`'s canonical step table — after every flow
step L0–L8 (so after caravan load/unload L2 and banking L3) and before `counterparties` `clan-economy`
A2 (`logistics-flow/spec-logistics-phase.md` §1; round 5 X5 makes that table the one order every spec
quotes — this text cited the map's older arrow list until the 2026-09-20 audit). The pass:

1. applies this turn's admitted `order-set` commands in the reveal order
   (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:214-217`) — one commander filing twice for one key is
   its own last word, by its own `CommandId`;
2. reads every input once, **at the start of the pass** — owner stock, demand, reserve, consignments,
   band snapshot, `Access`;
3. computes fills; 4. hands them to `settlement-payment`.

**A change from the map (contradiction EC16):** the map said *"quote at the start of the step"*.
Reading at the start of the **pass** lets goods a caravan unloaded this turn sell this turn, which
`fleet` asks for (fleet ask A6), and it still meets the rule the start-of-step wording protected:
goods bought in this pass cannot be sold in this pass (§Design 6). The quote a player sees while
planning is computed from the last committed state; settlement may differ, which is what `LimitMilli`
is for.

### 5. Suspension, never deletion

An order is **suspended** this turn — skipped, reported, kept — when: the sector is not a hub sector
(no active trade building: `Hubs.HubTier` = 0, read through `trade-foundation` `sector-features`); the trader's `LevelAt` the sector's owner and that hub is below
`market` (`trade-access` §2a — the diplomatic level **and**, since round 4, the building gate: the
hub's tier and the trader's own trade tier must reach the deal class, `treaty-vocabulary` §5); the
trader now owns the sector; the hub's world lacks the capability. Report reason
`order.suspended:{cause}`, where a missing building reads `needs-building:{dealClass}:{tier}` so the
player sees *"build a Trading Post"*, not a bare "closed". It resumes by itself when the cause clears.

### 6. Computing fills at one hub

Hubs run in sector-id order; inside a hub, goods run in good-id order — every id comparison in this
module is `StringComparer.Ordinal` (culture-sensitive string ordering would make the fill order depend
on the host's locale). Each (good, side) is computed
**once for the aggregate**:

**Sell side** (traders deliver to the hub owner). Each trader's requested sell units are capped by
its consignment of that good **at pass start**. The aggregate walks the bid curve
(`price-curve` `Walk(Sell, …)`). Sell legs are not capacity-bound; `settlement-payment` trims them to
what they fund.

**Buy side** (the hub owner delivers). Stock bound = owner stock − owner reserve (never below 0); the
reserve is `need-vector`'s for the owner (ask E-A10). **A deliberate generalisation of the map:** the
map applied the reserve only to soul-paid sales; here it bounds every buy, for every owner, so no hub
is drained below what its owner needs whatever it is paid with (principle 10 symmetry, and simpler).
The aggregate walks the ask curve.

**A hub at a bank point sells nothing today (ask E-A11).** Banking runs earlier in the same phase
(L3, before this pass at A1 — `logistics-flow/spec-logistics-phase.md` §1) and takes every good in a bank point's warehouse off
the map (`sector-yield-map.md` §2.9). The home sector holds the only Market slot and is a bank point once it
holds a Counting House (round 4: the bank point is that building)
(`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:147`), so a player hub on its best site would have
no stock at pass time. Clan hubs are unaffected (clans have no bank points or treasury). Filed to
`sector-yield` / `logistics-flow`: a per-(sector, good) **hold** in the banking policy — goods up to
the hold stay on the map — set by the owner's policy command, and by `trade-ai` for AI owners.
**Answered by round 4 (Q2, B):** the hold lives in `sector-yield`'s banking policy and is **unlocked by
the Treasury tier** (Banking tier 2) in that sector; with only a Counting House, everything at a bank
point banks. Its **default** was worded *"keep what open sell orders need"*; **round 5 A4 (owner,
2026-09-20) decides it:** *"keep enough to fill other traders' open buy orders at this hub"* — the goods
the hub is being asked to sell (an owner cannot place an order at its own hub, `order.own-hub`, §2).
**Named `OpenBuyDemandAt` (global audit m16: the old `OpenSellNeed` said the opposite of what it returns):**
`OpenBuyDemandAt(owner, sector, good)` = Σ `Remaining` of other traders' open buy orders
at that hub for that good, capped by the owner's stock at the start of the Logistics phase. It reads the
orders as they stand when banking runs — this turn's `order-set` commands apply later, in the pass
(§4 step 1) — so a new buy order holds goods from the next turn on; deterministic either way. This module
exposes the function; `sector-yield`'s banking step calls it before it banks (EC21's reading, now the
owner's decision A4; exchange-map OQ-4 closed).

**Limits.** At each walk step only orders whose limit accepts that step's per-unit price take part;
the step's units split among them pro rata. An order with no limit accepts every step.

**Capacity.** If the walked value of all buy legs at the hub exceeds `ClearingCapacity`
(`exchange-hub`), every trader's buy request at that hub is scaled by `capacity / total` (floor, units)
and the walks are re-run once. A buy walk's cost is convex in volume with zero cost at zero volume, so a
scaled-down volume costs at most its proportional share of the original total; the re-run aggregate
`costMilli` is therefore ≤ `capacity × 1000` and the pass never iterates further. **The capacity bound
is on the aggregate walk, before the per-trader final `ceil`** (audit 2026-09-20): each trader's own
round-up can add under one value unit, so Σ of the per-trader rounded values may exceed capacity by
fewer than the number of buying traders. That excess is paid, not cleared — capacity bounds goods
leaving the hub, which the aggregate walk fixes, and the round-up only raises what traders pay.

**Pro rata.** A step's units split in proportion to each participant's remaining request: `floor`
shares, then leftover units one at a time by largest remainder, **ties broken by a stable hash** of
`(turn, sector, good, side, commanderId)` drawn from the step seed with `SeededRng.DeriveStream`
(`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`) — never by faction id order, which the ideal's round 3
removed (§14b). Aggregating per commander before the walk is what makes splitting an order into many,
or holding a lower `CommandId`, worth nothing.

**Price per trader.** Each trader's value for a (good, side) is the sum, over the walk steps it took
part in, of its units in that step times that step's per-unit price (in milli), rounded once at the
end: `ceil` for buys, `floor` for sells — every rounding against the trader. Two traders in the same
steps therefore pay the same average, whatever their filing order.

**No same-pass resale.** Buy fills credit consignments only after the pass computes; the sell side
read consignments at pass start. So a unit bought in a pass cannot be sold in it.

### 7. The fill record

`FillSet`: per hub, per trader, per good, per side — units and walked value — plus the hub owner and
the trader's pool. Emitted on `TurnResult` beside the stock deltas (`trade-foundation` `stock-deltas`
shape), consumed by `settlement-payment`, `counterparties` `relation-facts` (`trade.fulfilled`), and
`trade-stories`.

### 8. Numeric types

Quantities and values `long`, `checked`, widened before multiplying; pro-rata shares compute
`units × request / totalRequest` with the multiply first and one divide. The capacity scale factor
is applied as `request × capacity / total`, never as a per-mille ratio that loses range.

**Both of those products multiply two content-scaled magnitudes** (audit 2026-09-20), so in `long` they
overflow where the square of a goods magnitude passes `long.MaxValue` — near `Θ` ≈ 1.2 × 10⁵, the same
order as the `int` whole-unit limit the range table rejects (CLAUDE.md "Numeric types"; `long` alone
holds one magnitude to `Θ` ≈ 2.1 × 10⁸). So each is taken in `System.Numerics.BigInteger` (Core targets
`net6.0`, `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`, so no `Int128`; precedent
`gk-core/src/FusionRpg.Core/Actions/Unlock/UnlockLadder.cs:38`), divided once, and narrowed to `long` checked:
the quotient is at most one of the two factors, so the narrowing never throws on reachable input and
would throw rather than wrap on unreachable input. Acceptance 11 tests it.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | One command shape and one admission gate for every commander | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:129-150`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-40` |
| Built | Stable reveal order | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:208-227` |
| Built | A deterministic named stream from a seed | `gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26` |
| Built | The step is pure and hashes its result once | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-199` |
| Real gap | The kind, the record, the pass, fills | — |

## Tunables

None owned. Reads `price-curve`'s and `exchange-hub`'s keys through their functions.

## Acceptance (contract)

1. **Order-independent:** permuting the command list, renaming `CommandId`s, or permuting the filing
   commanders of a turn leaves every fill and every value identical (shuffled command sets, seeded).
2. **Split-invariant:** replacing one commander's order with k orders of equal total at the same key
   gives the same fills and values (k orders at one key collapse to one record; tested through the
   record and through the pass).
3. At every hub and turn: the aggregate buy walk's `costMilli` ≤ `ClearingCapacity × 1000` (the bound is
   on the aggregate, before per-trader rounding — §Design 6 *Capacity*); Σ buy units ≤ owner stock −
   reserve; each trader's sell units ≤ its pass-start consignment.
4. No same-pass resale: no trader's sell units of a good exceed its pass-start consignment even when
   the same pass credits it more of that good.
5. Suspension: an order at a hub whose `LevelAt` fell below `market` fills nothing, keeps its
   `Remaining`, and fills again when it returns — both edges tested (drop then restore, and restore
   across a capture), and the building edge tested too (the trader's only Trading Post razed, then
   rebuilt; a clan order waits for the player's first Trading Post).
6. `total` orders close at 0; `per-turn` orders refresh; quantity 0 deletes; a legacy world with no
   `order-set` replays byte-identically, and a world without `trade.exchange` refuses `order-set`.
7. Ties never favour a faction id: across generated worlds where two traders tie on a leftover unit,
   each wins about half of the ties (printed rate, asserted only as "neither side wins every tie").
8. Limits: no trader ever pays a per-unit ask above its buy limit or receives a bid below its sell
   limit.
9. `OpenBuyDemandAt` (renamed from `OpenSellNeed`, global audit m16) equals the sum of other traders' open
   buy `Remaining` at the hub for the good, capped by owner stock, and never counts the owner's own orders
   (it has none there).
10. **Locale-free order (audit 2026-09-20):** the same world run under two different
    `CultureInfo.CurrentCulture` settings gives identical fills and the same `StateHash`.
11. **Range (audit 2026-09-20):** at a goods magnitude taken from `Θ` = 10⁶, a pro-rata split and a
    capacity scaling return the exact value (checked against an independent `BigInteger` computation)
    and do not throw.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Orders/` (new), trait `core.world-trade.orders`, boundary
  row `core-world-trade-orders`; admission tests beside the existing admission tests.
- `WorldCommand` and the submit DTO widen (`gk-core/src/FusionRpg.Contracts/WorldDtos.cs:518`, `:580-584`,
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:122`, `:138-165`), so this module crosses Core, Contracts and Server:
  run the focused boundaries `verify-change.ps1` selects for those paths, and the world determinism
  guard (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs`). The full suite runs once, at
  the end of wave 3 with `settlement-payment` (AGENTS.md verification point 2), not per task.

## Hard edges

- **One pipe.** `order-set` enters through `WorldCommandAdmission` like every order; no side door for
  the AI.
- **Order-independence is the contract**, not a property of the test data.
- **The pass writes nothing.** All mutation is `settlement-payment`'s, in one place.

## Dependencies

- Upstream: `price-curve`, `exchange-hub`, `trade-access`, `tradeable-goods`; `counterparties`
  `need-vector` (demand and reserve at a sector, E-A10), `relation-facts` (band snapshot);
  `logistics-flow` `logistics-phase` (the slot); `trade-foundation` `world-stamp`; `sector-yield` /
  `logistics-flow` banking hold (E-A11 — soft: without it, hubs at bank points sell nothing).
- Downstream: `settlement-payment`; `trade-ai` `ai-bidding`; `trade-surface` policy editor;
  `trade-stories`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `order-set` kind and payload | human client, `trade-ai` `ai-bidding` |
| `ExchangePass.ComputeFills(world, inputs) : FillSet` | `settlement-payment` |
| `WorldState.TradeOrders` (read-only projection) | `trade-surface`, `trade-ai` (own orders only) |
| `IWorldView.OwnTradeOrders()` — the viewing faction's own standing orders, exact (trade-ai ask T-A6) | `trade-ai` `ai-bidding` |
| `OrderBook.OpenBuyDemandAt(world, owner, sectorId, goodId) : long` — **renamed** from `OpenSellNeed` (global audit m16): round 5 A4 redefined the Treasury hold's default as *"keep enough to fill **other traders' open buy orders** at this hub"*, so the old name said the opposite of what the function returns. Registered as `sector-yield`'s `IBankingHoldSource` (its `spec-banking-fact.md` §3a) — the Treasury hold's default (round 4 Q2, round 5 A4). **Waits on banking (round 6 C3):** the hold itself lands with `banking-fact`, after `material-ledger` and the save-identity re-key; this projection is pure and can land earlier | `sector-yield` `banking-fact` |

`LimitMilli` (§1) is the limit price trade-ai ask T-A6 asked for; it exists already.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine, commands, economy, determinism.
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §7.2, §7.6, §8.7, §14b; logistics-flow-map (phase order,
    auto-banking); fleet-map (A6, Q1); counterparties-map (need-vector); spec-budget-debit (reveal
    and replay precedent).
[x] decisions.md :7 (phase order) — this pass lives inside Logistics, adds no phase.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: Reveal ordering and admission, WorldCommand payload shape, SeededRng.
[x] Surrounding sections read (Reveal contract comment; admission class doc).
[x] No constraint claimed without a run; "legacy replays byte-identically" is an acceptance test.
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC16 and the reserve generalisation are in the map's module 7 text.
[x] No population count pinned; tie fairness is printed, not pinned.
[x] No event-refreshed cache.
[x] Orderings: order-independence and split-invariance are acceptance criteria with shuffled tests.
[x] No actor magnitude.
[x] No SOLID-violating path: one command pipe, one pass, not a second standing-order mechanism.
[~] Registry row: order-independence gets a guard row pointing at its shuffled-command test.
[x] Round 4 reconciliation (2026-09-19): suspension reads LevelAt (building gate); E-A11 answered
    (Treasury hold, default OpenSellNeed); T-A6 order half answered (own-order view, limit exists).
[x] Round 5 (2026-09-20): A4 adopted as the owner's wording (the hold = other traders' open buy
    orders at this hub); no behaviour change from the round-4 reading.
[x] Round 6 (2026-09-20): m16 — the projection is renamed `OpenBuyDemandAt` (A4 made the old name say the
    opposite); C3 — the Treasury hold it feeds lands with banking, after material-ledger and the
    save-identity re-key, while this pure projection may land earlier; C1 — **corrected 2026-09-20
    (reconciliation R-5/R-19.6): the hub gate and this pass do NOT share exchange wave 2's flag.** This pass
    lands in exchange wave 3 and registers **its own** flag, `trade.exchangeOrders`, sharing wave 3's single
    bump with `treaty-lifecycle`'s `trade.diplomacy`. Gating `order-set` on `trade.exchange` (registered in
    wave 2) would let a world stamped between the two waves gain `order-set` mid-life — the R1 breach the
    per-world stamp exists to prevent. `spec-exchange-hub.md:249` is corrected the same way; S1 — the
    hub-sector test reads sector-features, which is where the split-owner rule lives.
[x] Audit 2026-09-20 (independent): pass slot re-cited to logistics-phase §1 row A1 (was the map's stale
    arrow list); magnitude×magnitude products moved to a BigInteger intermediate; capacity bound stated
    on the aggregate walk; ordinal id ordering required and tested; acceptance renumbered 1-11.
```

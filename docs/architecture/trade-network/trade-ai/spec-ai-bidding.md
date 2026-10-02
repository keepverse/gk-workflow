# Spec: `ai-bidding`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `ai-bidding`, row 5 of the approved [trade-ai map](../trade-ai-map.md)
(wave 2). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.2, §7.5, §8.5 (*"plan on
believed prices … settle on the truth"*), §14b (*"AI bidding … its knobs"*). Upstream: `deal-valuation`,
`trade-intel`, `ai-spend-limit`; `exchange` `order-book`; `counterparties` `need-vector`.

## Objective

AI empires and clans run their hubs the way the player does: standing buy orders for what they lack,
standing sell orders for what they hold beyond need, filed through `exchange`'s `order-set` command and
settled by the same order book. The AI decides on the prices it **believes**; the book fills on the
**true** price, and a limit price on every order means a stale belief can cost the AI a missed trade
but never an overpayment.

Success looks like: an AI with a real shortage and a reachable open hub files a buy the turn it sees
the hub; it never sells into its own need; it never bids above what the good is worth to it; and a
stable AI files few order changes per turn.

## Scope and non-goals

**In:** which goods to buy and sell, how much, at which hub, at what limit price; when to re-file;
clans use the same module with clan weights.

**Not here:** the price curve, fills, pro-rata and settlement (`exchange` `order-book`,
`settlement-payment`); moving goods to a hub (`ai-logistics` files the route); treaty access
(`ai-treaty-policy`). The AI never files at a hub where its `LevelAt` is below `market` — since round 4
that includes the building gate: the hub's tier and the AI's own trade tier must reach the deal class
(`exchange` `trade-access` §2a; a Trading Post for clan barter, a Market for empire orders). An order
at such a hub would be admitted and then sit suspended, so filing it is noise (TC6).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Orders reveal in `(CommanderId, CommandId)` order | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:215-216` |
| Every AI order passes the player's admission; a refusal throws in the commit | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:277-281` |
| A re-filed identical command is skipped by `(world, turn, commander, command id)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:143-157`, `:283` |
| `INeedVector`: per-mille, neutral 1000 | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:12-22` |
| Hysteresis precedent: a standing choice must be beaten by a tunable margin before the AI changes it | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:415-432`; `gk-core/src/FusionRpg.Core/World/Ai/WorldAiTuning.cs:9-18` |

### Wiring gap

None. There is no hub, order or price in the code yet; all of that is `exchange`'s.

### Real gap

All of it.

## Design

### 1. What to buy and sell

For the faction's own goods (`NeedVector.For(view)`, exact on own stock — `counterparties/spec-need-vector.md` §4):

```text
reserve(g)  = demand(g) × needs.reserveTurns                 // counterparties' horizon, read not copied
buyQty(g)   = max(0, reserve(g) − stock(g))    when want(g) > 1000
sellQty(g)  = max(0, stock(g) − reserve(g))    when want(g) < 1000
```

`want > 1000` exactly when stock is below demand (the need-vector rule), so the two sets never overlap
for one good. Quantities are rounded down to whole `orderStepUnits`.

### 2. Where

- **Buy** at the hub with the lowest believed buy price (`trade-intel`, pessimistic reading), among hubs
  where the faction's `LevelAt` that hub is `market` or better (round 4: tier and treaty/band) and the
  faction holds a route or depot that can
  carry the goods home (`ai-logistics`); ties by hub sector id.
- **Sell** at a foreign hub with `LevelAt ≥ market`, with the highest believed sell price, where the
  goods already sit or can be routed; ties by sector id. **Corrected (round-4 reconciliation):** this
  line said "at the own hub", but `order-book` refuses an order at the commander's own hub
  (`order.own-hub`); an AI's own hub sells passively to other traders' buy orders, and at a bank point it
  keeps stock for them only through the Treasury hold (round 4 Q2; `order-book` `OpenSellNeed` — round 5
  A4: the default keeps enough to fill other traders' open buy orders at that hub). A
  missing Trading Post, Market or Treasury the plan wants is reported to `ai-trade-buildings` as payoff.
- Own hubs read the live exact quote (`trade-intel` `OwnHubQuote`); foreign hubs read belief. A hub the
  faction has never quoted is not a candidate.

### 2a. Barter pairs by hub (audit 2026-09-20)

Payment is **barter at the hub**: a trader's sells at a hub pay only for its buys **at that same hub, in
the same credit pool**, and a sell with nothing to buy there delivers nothing
(`exchange` `settlement-payment` §2, `order.sell-no-counter-leg`); and a sell leg is capped by the
trader's **consignment at that hub at pass start** (`order-book` §Design 6). The two bullets above,
read alone, file buys at the cheapest hub and sells at the dearest — two different hubs, so neither
order could ever settle. The plan is therefore built **per hub**:

1. For each candidate hub (the `LevelAt ≥ market` filter above), pair the buy list with the sell list
   in the same pool: the hub's **paired value** is `min(Σ buy value, Σ sell value + soul budget)` at the
   believed quotes (the soul budget is the player's only; an AI's is 0).
2. Choose hubs in descending paired value, ties by hub sector id (ordinal), assigning each good's buy and
   sell to at most one hub per turn.
3. A sell is filed only at a hub where a buy in the same pool is filed this turn, and only for goods the
   faction already holds in consignment there **or** that `ai-logistics` routes there this turn (the
   `route-set` to that hub, `ai-logistics` §1) — goods that arrive by route sell on the turn they are in
   the consignment at pass start.
4. What remains unpaired is dropped this turn and reported as the reason's shortfall
   (*"no hub pairs ice essence with a want this turn"*).

### 3. The limit price

```text
reservation(g, side) = deal-valuation's per-unit break-even for a one-leg deal of one step
buyLimit(g)          = reservation(g, buy)  × aiBidAggressionMilli[profile] / 1000
sellLimit(g)         = reservation(g, sell)                  // never sell below own valuation
file a buy  only if believedBuy(g, hub)  ≤ buyLimit(g)
file a sell only if believedSell(g, hub) ≥ sellLimit(g)
```

- **`aiBidAggressionMilli ∈ [1, 1000]`** is a load check: aggression lowers how close to its valuation
  the AI bids, and can never make it bid **above** it (a value above 1000 would turn a difficulty knob
  into a pump the player could sell into).
- The limit price travels **in the order** (T-A6). The book fills only at or better than it, so a
  believed price six turns old risks a missed fill, never an overpayment — the §8.5 promise, made
  mechanical.
- Payment is barter at the value index from the faction's stock at that hub (`exchange`
  `settlement-payment`); goods offered as payment obey the sell rule (never below reserve).

### 4. Fewer changes: re-file only on a real change

Standing orders persist until changed (`exchange` `order-book`). The AI files `order-set` for a
(hub, good, side) only when the new target differs from the standing order by at least
`trade.orderRefileSteps` order steps, or the limit price moves across a quote band, or the order must be
cancelled (quantity 0, or access lost). This is the momentum idea (`FrontierRulesPolicy.cs:415-432`)
applied to orders, so the command log reads one line per real decision.

### 5. Spend and file

The candidate set goes through `ai-spend-limit`'s `Trim` (lowest-want orders dropped first), then each
survivor is filed as one `order-set` with id `ai-{turn}-o-{hub}-{good}-{side}` — unique per commander
per turn by construction (the store key, `RpgStore.WorldTurns.cs:143-157`) — and a reason naming the
want and the believed price: *"buy 20 ice essence at frost-hub, want 1840, believed 118 ≤ limit 130"*.
Filing order does not matter: the book aggregates and fills pro rata (`exchange-map.md` module 7), so
ids carry no priority.

### 6. Capability gate

Nothing is filed unless the world's stamp grants the exchange capability, read through the view
(T-A8). A legacy world's AI files exactly what it files today.

### 7. Clans

Clans call the same module with the clan personality row (`counterparties` `empire-roster` /
`clan-seeding`); nothing here branches on faction kind.

## Tunables

| Key | File | Unit | Nature |
|---|---|---|---|
| `difficulty.<profileId>.aiBidAggressionMilli` | `data/tuning/trade.v1.json` (new; `counterparties`' row) | ‰ of reservation | difficulty knob, load check `[1, 1000]` |
| `trade.orderRefileSteps` | `gk-core/data/tuning/ai.v3.json` (next AI version) | order steps | how much a target must move before the AI re-files |

Reused: `needs.reserveTurns` (`counterparties`), `orderStepUnits` (`exchange`).

## Acceptance (contract)

1. **Never sells into need.** No sell order is filed for a good below its reserve; no payment leg
   draws a good below its reserve.
1a. **Pairs settle (audit 2026-09-20).** Every sell the AI files is at a hub where it files a buy in the
    same credit pool the same turn, and for goods in its consignment there or routed there; integrated
    with `exchange`'s book, a filed pair fills (subject to limits and capacity) rather than stranding
    as `order.sell-no-counter-leg`.
2. **Never buys what it has.** No buy is filed for a good whose want is ≤ 1000.
3. **Never above valuation.** Every buy's limit ≤ the reservation; every sell's limit ≥ it.
4. **Within the limit.** Every turn's filed set passes `ai-spend-limit`'s exposure check.
5. **Reachability.** An AI with a real shortage (want > 1000) and a hub it has quoted with `market`
   access and a way to carry goods home files a buy within one turn of the quote entering belief — a
   reachability test, not a count.
6. **Explained.** Every order carries a reason naming the want and the believed price.
7. **Stale belief cannot overcharge.** Given a stale believed quote below the true price, the filed
   order either does not fill or fills at ≤ its limit (asserted against `exchange`'s book in an
   integration test).
8. **Stable.** With unchanged needs, quotes and access, the AI files zero `order-set` commands on the
   second turn.
9. **Legacy.** On a legacy-stamped world no `order-set` is filed.
10. **No faction-kind branch.** A source scan finds no `WorldFactionKind` test in this module.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/AiBiddingTests.cs` (new): 1–6, 8, 10 over scripted views.
- `tests/FusionRpg.Core.Tests/World/Trade/` integration with `exchange`'s book: criterion 7.
- `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs` (extend): criterion 9 through the real fill.
- Run `.\scripts\verify-change.py -Paths <changed paths> -Session <id>` (`core-world-ai-trade`).

## Hard edges

None on hashed state (orders are commands; the book's state is `exchange`'s).

## Dependencies

| Consumes | From |
|---|---|
| `Reservation`, `DealValue` | `deal-valuation` |
| believed and own quotes | `trade-intel` |
| `Trim` | `ai-spend-limit` |
| `order-set` with a limit price; own open orders via the view | `exchange` `order-book` (T-A6) |
| want, demand, reserve horizon | `counterparties` `need-vector` |
| capability flag, profile id | `trade-foundation` `world-stamp` (T-A8) |

| Exposes | To |
|---|---|
| the faction's buy/sell plan per turn | `ai-logistics` (what to route to which hub), `clan-behaviour` |

## Boundaries

- **Always:** limit price on every order; reason on every order; re-file only on a real change.
- **Ask first:** an AI market-making strategy (buying to resell); bidding above valuation for any reason.
- **Never:** an order at a hub without access; a branch on faction kind; a price formula of its own.

## Design-gate checklist

```
[x] Subsystems: world map AI, economy (hub orders, barter — consumed), tunables, difficulty.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list. NOT read: world-map-runtime ideal/specs.
[x] decisions.md: no lock covers AI bidding; the registry's loam rule is untouched (loam is never a good).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: reveal order, fill admission, command idempotency key, momentum hysteresis.
[x] Surrounding sections read: exchange-map module 7 (pro-rata, aggregate walk).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: TC5/TC6 in the map; T-A6 filed for the limit price.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Orderings: fills are pro rata and filing-order independent (exchange); ids carry no priority.
[x] No actor magnitude.
[x] No SOLID-violating path: one valuation, one book, one limit.
[ ] Registry row for criterion 10 (no faction-kind branch) owed with the change.
[x] Round 4 reconciliation (2026-09-19): hubs filtered by LevelAt (building gate); the own-hub sell
    contradiction with order-book fixed; blocked plans feed ai-trade-buildings.
[x] Round 5 (2026-09-20): A4 wording for the hold default; no rule change.
[x] Audit 2026-09-20 (independent): the buy-cheapest / sell-dearest rule filed sells at hubs with no
    paired buy, which barter settlement refuses; plans are now built per hub as pools that pair
    (§2a, criterion 1a).
```

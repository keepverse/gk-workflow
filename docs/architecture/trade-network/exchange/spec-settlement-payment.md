# Spec: `settlement-payment`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 8 of the [exchange map](../exchange-map.md) (wave 3; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §3 principles 4, 7, 8;
§7.3, §7.7 (payment, tariffs); §14b (*"Souls for a purchase are reserved before the step and settled
with it"*). Cross-map decision CM3. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Pay for every fill `order-book` computed, and write it. Payment is **barter at the value index**:
what a trader sells at a hub pays for what it buys there, in the same credit pool. The **player alone**
may top up with souls, and every soul paid is **destroyed**. Fees and the sink share of tariffs are
destroyed too; the rest of a tariff goes to the grantor in goods. Everything that changes hashed state
happens inside `TurnEngine.Step`; the soul spend and the ledger rows land in the same commit
transaction. Afterwards: souls only ever went down, no world stock reached a banked stock, and every
trader gave up more than it got, measured at the hub's own prices.

## Scope and non-goals

In scope: the credit pools per trader and hub; the soul budget as a logged step input; the budget cut;
the sell trim; fees and tariffs; the goods waterfall; the in-step writes; the commit-side soul spend and
ledger rows; the fill records other programs read.

Not in scope: computing fills (`order-book`); tariff rates (`trade-access`); moving bought goods home
(`logistics-flow`, `fleet`); banking anything (`sector-yield` `banking-fact`); relation facts
(`counterparties` `relation-facts`, which reads the records this module emits).

## Design

### 1. The soul budget — a logged input, which is the reservation

Souls live in a Data-side wallet keyed by player (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-161`);
`Step` is pure and cannot read it (P13). So, inside the commit transaction, **before** `Step`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`):

```
budget(player) = min(soul balance, Σ SoulCapPerTurn over the player's open buy orders)
```

The budget is **stored with the turn's commands as a logged step input** and passed to `Step`; replay
reads the logged value, never the live wallet. This is the reservation the ideal asks for: the commit
runs under the store's lock (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:499`) in one
transaction, so nothing can spend those souls between the read and the spend, and an unused budget
needs no release — it is simply not spent. A failed step rolls the transaction back: no spend, no rows.
The logged input rides the same per-turn input record `counterparties` `relation-facts` adds for the
band snapshot — one channel for logged step inputs, never two (ask E-A7). Only `Player`-kind factions
(`gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:10`) ever have a budget.

Across one player's hubs the budget is drawn in sector-id order, each order up to its own cap — a rule
about one player's own orders, not a contest between traders.

### 2. Per trader, per hub, per pool

The two pools are `tradeable-goods`'. All arithmetic in value-milli, `long`, `checked`; each rounding
against the trader.

```
buyCost   = Σ buy values                           (from the FillSet)
fee       = ceil(buyCost × fee.milli / 1000)
tariff    = ceil(buyCost × TariffMilli(owner, trader, hub) / 1000) (trade-access; reads LevelAt the hub, round 4)
owed      = buyCost + fee + tariff
proceeds  = Σ sell values                          (from the FillSet)
souls     = bankable pool of a player ? ValueForSouls(budget left) : 0
```

1. **Budget cut.** If `owed > proceeds + souls`, the trader's buys in this pool shrink by the same
   factor across goods (floor units), computed against the budget less one unit of rounding slack per
   rounded term, so the recomputed `owed` never exceeds what it can pay. Freed units stay with the hub;
   they are **not** handed to another trader (keeps the pass order-independent).
2. **Goods first, souls last.** Sells pay first. If `proceeds > owed`, the trader's sells shrink to the
   smallest units whose value covers `owed` (ceil units — the trader delivers, never under-delivers);
   the unsold rest stays in its consignment. A sell with nothing to buy delivers nothing and reports
   `order.sell-no-counter-leg` — there is no gold and no sell price (ideal principle 8).
3. **Souls cover the tail.** `soulsUsed = SoulsBaseFor(owed − proceedsUsed)` when positive
   (`goods-valuation`, unscaled — the quantity already carries the scale, EC6). Every soul used is
   destroyed.

### 3. Where each unit of value goes — the waterfall

Goods delivered by the trader pay, in order: the buy cost, the tariff's grant share, then the sinks.
Souls pay whatever is left.

| Component | Paid in goods → | Paid in souls → |
|---|---|---|
| Buy cost | hub owner's stock | destroyed |
| Tariff grant share, `tariff × (1000 − tariff.sinkMilli) / 1000` | hub owner's stock (the grantor is the hub owner) | destroyed — *any souls part of a tariff is sunk in full* (ideal §7.7) |
| Tariff sink share and fee | destroyed (units rounded up) | destroyed |

So the hub owner never receives souls and never receives goods that were minted: it receives only
goods the trader delivered. When souls pay a buy, the hub owner gives goods and receives nothing for
that part — the `souls → located goods` conversion (a registry Conversions row, `tradeable-goods`),
lossy, rate-capped by clearing capacity, gated by a hub and `Access`. The reserve bound in `order-book`
is what keeps an owner from being drained by it.

### 4. Writes inside `Step` (hashed)

| State | Change |
|---|---|
| Hub owner's stock at the hub sector | − bought units; + delivered units not destroyed. Bankable goods: `sector-yield` located stock; map-bound: the sector's `RubbleStock`/`IronworkStock` |
| Trader's consignment at the hub (`exchange-hub`) | + bought units; − delivered units |
| `TradeOrders.Remaining` (`order-book`) | − filled units (after the cut and trim) |

**Nothing else.** Settlement never writes a wallet, a material row, or an AI treasury. The map said
the seller may receive goods *"in … an AI's treasury at a bank point"*; cross-map decision CM3 gives the
treasury one writer, `sector-yield` `banking-fact`, so goods the owner receives land in its stock and
bank on a later turn like any stock (**contradiction EC12**). And the AI treasury is not a payment
source: it is unlocated, and the player's banked materials cannot pay either, so allowing it would give
AI empires a payment channel the player lacks (principle 10) — `counterparties` `empire-treasury` lists
*"trade payments"* among its drains, which this module never produces (**contradiction EC10**, ask
E-A12).

**Round 6 C3 — where settlement touches banked materials, it waits for the save-identity re-key.** Owner
decision C3 (2026-09-20): *"Banking waits on the save-identity re-key. Save-identity is being built now;
`material-ledger` and the banking work that needs it start after it finishes."* Settlement itself is **not**
banking work — that is the point of the rule above: it writes located stock and consignments only, never a
wallet, a material row or a treasury. So this module **does not wait**, and the family's first value-moving
trade can ship before `material-ledger`. What waits is every path that would move value between a settlement
and a **banked** store:

| Path | Waits on | Until then |
|---|---|---|
| Goods the hub owner receives being **banked** on a later turn | `sector-yield` `banking-fact` → `trade-foundation` `material-ledger` → `solid-enforcement` SE4.12–SE4.38 (global audit C3) | The goods sit as located stock, tradeable and visible; they simply do not bank yet |
| An AI treasury as a payment **source** | refused permanently (EC10, principle 10 — not a scheduling question) | — |
| A hub at a bank point having stock to sell (the Treasury hold, round 4 Q2 / A4) | the same chain, through `OpenBuyDemandAt` (`order-book`) | `order-book` §Hub-at-a-bank-point states the interim: such a hub sells nothing until the hold lands |
| `legion-build`'s banked draw for equipment and doctrine upkeep (round 6 CQ2) | the same chain | Located stock only; a short sector refuses production and an unpayable doctrine lapses (`legion-build/spec-legion-equipment.md` §7a, `spec-legion-doctrine.md` §3a) |

**CQ2 does not add a settlement path.** The banked draw is a *sink* inside `legion-build`'s own production and
upkeep resolvers, through `material-ledger`'s single writer — it never passes through a fill, a consignment or
this module. I2 therefore stands unchanged and stays asserted by source scan: nothing under
`World/Trade/Settlement/` references a banked writer, before or after CQ2.

Because these writes happen inside `Step`, the state hash computed at `Step`'s return
(`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:198`) already covers them — unlike the cargo pass, which
runs after `Step` and re-hashes (`spec-budget-debit.md` §Design 5).

### 5. Commit side (Data, same transaction)

After `Step` and the diff (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601-607`):

1. **Soul spend:** one soul-ledger row per (player, hub sector, turn) with `delta = −soulsUsed`, where
   `soulsUsed` is the **sum of every soul leg at that hub that turn** — order top-ups and treaty-deal
   top-ups (§7) alike (audit 2026-09-20: two rows sharing one dedupe key would lose the second to
   `INSERT OR IGNORE`, leaving goods delivered for souls never taken),
   reason `trade` (a new `SoulEarnPolicy.Reasons` member, `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:49-84`
   — a reviewed widening of the creature program's reason list), dedupe key from `trade-foundation`
   `ledger-keys` with fact kind `soul-pay`. `INSERT OR IGNORE` makes a re-commit write nothing
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:147-150`). `soulsUsed ≤ budget ≤ balance`, so the
   balance never goes negative.
2. **World-stock ledger rows** from the stock deltas — **one row per ledger key, holding the sum of
   every delta of that turn that maps to it** (the `world-stock-ledger` rule, *"one row per aggregated
   delta"*, `trade-foundation/spec-world-stock-ledger.md` §Objective): three traders buying one good at
   one hub are one `settle-buy` row on the hub owner's holder, and an order fee and a deal-leg fee at
   the same hub and good are one `fee` row — fact kinds `settle-buy`, `settle-sell`, `fee`,
   `tariff-grant`, `tariff-sink` (a reviewed widening of `ledger-keys`' closed vocabulary; buy and sell
   are separate kinds because one trader may buy and sell one good at one hub in one turn, and the key
   `(save, owner, world, turn, factKind, sector, good)` must stay unique). **Round 5 X2 (binding):** these
   five are the settlement kinds for every writer — `counterparties` `empire-treasury`'s single `settle`
   kind re-points to them (a treasury credit from a sale is `settle-sell`); `trade-foundation`
   `ledger-keys` already lists the five.
3. **Fill records** on `TurnResult` for `counterparties` `relation-facts` (`trade.fulfilled`, capped per
   pair per turn there) and `trade-stories`.

### 6. Numeric types

Values in `long` value-milli; units `long`; souls `long`. Every product `checked`, widened first;
`ceil`/`floor` explicit, each against the trader; divide by 1000 once per quantity, last.

### 7. Treaty deal legs — the one settlement path (trade-ai ask T-A5, round 4 reconciliation)

A signed deal's goods legs (`treaty-vocabulary` §6, `treaty-lifecycle` §3a) settle **here, in the same
pass**, after the order fills, never through a second writer:

- **At the deal's leg hub** (`LegHubSectorId`): the hub owner's legs leave from / land in its located
  stock; the other party's leave from / land in its consignment there (`exchange-hub` §4). A leg needs
  `LevelAt ≥ market` for the non-owner at that hub this turn (`trade-access` §2a); otherwise it
  delivers nothing and counts as short.
- **Valued at the value index, not walked.** A treaty leg is a term both sides already valued with
  `deal-valuation`; it does not walk the curve and pays no tariff (the treaty is the terms). It pays
  `fee.milli` (destroyed at the hub), so a deal is never a lossless conversion (P5), and it counts
  against the hub's clearing capacity **after** order fills (orders are never displaced by a deal).
- **Sources are pass-start stock.** A giving leg draws only from the giver's located stock or
  consignment **as it stood at pass start, less what this pass's order sells already took** — never
  from goods an order fill credited in the same pass (the no-same-pass-resale rule of `order-book`
  §Design 6 holds for deals too, which is what keeps `exchange-invariants` I4's decomposition true).
- **Short legs settle in proportion — the default guard (audit 2026-09-20).** Delivering each leg
  independently would let a party that signs a one-off barter and cannot deliver its side still
  receive the other side in full, paying only a band drop — the classic accept-then-default deal
  exploit, open to the player and to an AI alike. So one deal settles as a unit: for each leg,
  `deliverable = min(owed, available, remaining capacity)`, and the deal's **fulfilment ratio**
  `r = min over legs of deliverable × 1000 / owed` (per-mille, floor — a bounded ratio). **Every leg**
  of that deal then delivers `floor(owed × r / 1000)` units this turn, soul top-up included
  (`SoulsBaseFor` of the scaled value). A deal with `r < 1000` is short: the leg(s) that set `r` name the
  short party on `SettlementRecords`, and `treaty-lifecycle` ends or breaks the treaty in Snapshot.
  Nothing is owed forward. At `r = 1000` the deal settles exactly as before.
- **A player's soul top-up** (one-off only) is taken from the same logged soul budget (§1) and
  destroyed; the counterpart receives nothing for it — the same `souls → located goods` rule as an
  order's soul leg, so I1 holds for deals too.
- Ledger fact kinds `deal-leg` and the existing `fee` (a reviewed widening of `ledger-keys`, beside
  `settle-buy`/`settle-sell`).

### 8. Asks answered here

- **counterparties A13** (*"reuse `empire-goods-sinks`' logged pre-step verdict shape for the souls
  reservation"*): the soul budget is **per player per turn**, not per command, so it is stored in the
  per-turn logged-input record `relation-facts` adds for the band snapshot (E-A7), not as a
  per-command verdict row. Two logged-input shapes inside `counterparties` (per-turn record, per-command
  cover table) are that program's to unify; recommended there: one step-input table keyed
  `(world, turn, inputKind, key)`, which this module would write a `soul-budget` row into. Reported in
  exchange-map *Cross-cluster conflicts*.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The P14 soul ledger: dedupe key, `INSERT OR IGNORE`, watermarked balance | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-175` |
| Built | Souls are keyed by player; no AI faction can hold them | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149` |
| Built | One commit transaction under one lock: Step, diff, Data-side passes | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:493-499`, `:601-620` |
| Built | Soul reasons as a closed list | `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:49-84` |
| Real gap | Budget input, pools, cut, trim, waterfall, writes, ledger rows | — |

## Tunables

`data/tuning/trade.v{n}.json`: `fee.milli` (seed 300 falling toward 50, ideal §13; must be ≥ 1 — a
free exchange would be a lossless conversion, P5; load rejection otherwise).
`data/tuning/diplomacy.v{n}.json`: `tariff.sinkMilli` (0–1000, bounded ratio).
`payment.soulsPerKiloValue` is `goods-valuation`'s.

## Acceptance (contract) — invariants I1, I2 and I3's settlement half

1. **I1 — no path increases souls.** Over generated worlds and order sets: every trade soul-ledger row
   has `delta ≤ 0`; Σ souls leaving each player = Σ souls destroyed; no non-player faction ever has a
   budget; a player's balance after the commit ≤ before.
2. **I2 — no world stock enters a banked stock.** Settlement writes no wallet, material or treasury
   row (source scan: nothing under `World/Trade/Settlement/` references the material or treasury
   writers); no fill pairs pools; `loam` and `recruit` appear in no record.
3. **Every order exchange loses, at the hub's own prices.** For every trader and hub with a non-empty
   **order** basket, the value it received is strictly less than the value it gave, both at the hub's
   pass-start mid prices, souls counted at `ValueForSouls`. (Measured at **base** value this is false and
   must not be asserted: buying what a hub has in surplus with what it lacks can gain base value — that
   is comparative advantage, ideal principle 5.) **Deal legs are excluded from this criterion** (audit
   2026-09-20): they are valued at the value index, not walked, so a deal that swaps a hub's surplus good
   for its scarce one can gain at mid prices; a deal's loss is the fee, asserted in criterion 8.
4. A reserved budget the step does not use is not spent; a step that throws leaves no soul row, no
   ledger row and no state change (one transaction).
5. Re-committing a turn, or replaying it from the log, writes no new soul or ledger row, and replay
   reads the logged budget: deleting soul-ledger rows after a turn leaves that turn's replay hash
   unchanged.
6. The hub owner's stock gains exactly the delivered units not destroyed; the destroyed units equal the
   fee and tariff-sink value paid in goods, rounded up; a soul-paid part delivers the owner nothing.
7. The budget cut and the sell trim never make a trader pay more than `proceeds + souls`, and never
   deliver less value than it owes.
8. **Deal legs:** a leg moves goods only between the leg hub owner's stock and the other party's
   consignment there; it pays the fee (strictly positive, so every non-empty deal loses at the value
   index) and no tariff; it never displaces an order fill from clearing capacity; a deal's soul top-up is
   destroyed and I1 holds over generated deals.
9. **No default gain (audit 2026-09-20):** for every generated deal and availability, each party
   receives at most `r` ‰ of what it was promised, where `r` is the ratio of what it delivered — a party
   that delivers nothing receives nothing; a giving leg never draws goods an order fill credited in the
   same pass.
10. **One row per key (audit 2026-09-20):** a turn with several traders at one hub, and an order and a
    deal leg at one hub and good, writes exactly one row per ledger key whose delta is the sum; the
    per-(player, hub, turn) soul row equals the sum of every soul leg there; re-committing writes
    nothing (criterion 5).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Settlement/` (new), trait `core.world-trade.settlement`,
  boundary row `core-world-trade-settlement`.
- `gk-core/tests/FusionRpg.Data.Tests/` (commit transaction: budget logging, soul row, dedupe, rollback,
  replay), in memory per the test-substrate rule; the existing Data boundary for
  `RpgStore.WorldTurns.cs` and `RpgStore.Souls.cs` is what `verify-change.py` selects.
- Crosses Core and Data together: run the full suite **once**, at the end of wave 3 with `order-book`
  (AGENTS.md verification point 2), plus `guard-dal.py` (all SQL stays in `FusionRpg.Data`).

## Hard edges

- **Souls only go down.** No branch, rounding or refund writes a positive trade soul delta.
- **One writer per stock.** Treasury: `banking-fact`. Wallet and materials: banking and their own
  programs. Settlement writes only hub stock and consignments.
- **No money.** A value amount exists only inside one settlement computation.

## Dependencies

- Upstream: `order-book` (fills), `tradeable-goods` (pools), `goods-valuation` (souls conversion),
  `trade-access` (tariff), `exchange-hub` (consignments); `trade-foundation` `ledger-keys`,
  `world-stock-ledger`, `stock-deltas` (owner dimension, E-A8); `counterparties` `relation-facts` (the
  logged-input record, E-A7); `sector-yield` `located-stock`.
- Downstream: `counterparties` `relation-facts` (`trade.fulfilled`), `trade-stories`, `trade-foundation`
  `economy-report` (fee, tariff and soul-sink lines), `exchange-invariants`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `Settlement.Apply(world, fills, inputs) : (WorldState, SettlementRecords)` inside `Step` | turn engine |
| `SettlementRecords` on `TurnResult` (fills after cut/trim, fee, tariff grant/sink, souls used) | Data commit, `relation-facts`, `trade-stories`, `economy-report` |
| Logged input `SoulBudget(playerId)` | Data commit (writes), `Step` (reads) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy (souls, P1, P5, P14), data/SQL (commit transaction), world turn engine.
[~] Session boundary: trade-network-idea-20260919; new file only; the check's exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: economy-principles (whole), empire-resource-ssot (whole), ssot-materials-crafting
    §4.3, trade-network-ideal §3, §7.3, §7.7, §14b; counterparties-map (treasury, relation-facts);
    trade-foundation-map §2.5-§2.8; sector-yield-map §2.9; trade-network-map §1a (CM3).
    Not read: data-architecture.md in full this session (the DAL rule is taken from AGENTS.md and
    guard-dal.py's purpose); creatures/spec-soul-economy.md.
[x] decisions.md :108 respected; no lock covers settlement.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: AppendSoulLedgerUnlocked body, commit sequence and lock, Step's hash point,
    SoulEarnPolicy.Reasons.
[x] Surrounding sections read (the commit method's header and pass comments).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted (SQL only in Data; no cap on a magnitude — fee and tariff are bounded
    ratios).
[x] Corrections propagated: EC10, EC12 and the base-value correction (Acceptance 3) are in the map.
[x] No population count pinned.
[x] No event-refreshed cache.
[x] Orderings: the budget cut never reallocates freed units, so the pass stays order-independent.
[x] No actor magnitude.
[x] No SOLID-violating path: one writer per stock; one logged-input channel.
[~] Registry rows: I1 and I2 get guard rows in exchange-invariants.
[x] Round 4 reconciliation (2026-09-19): tariff read per hub (LevelAt); treaty deal legs (T-A5) settle
    here as §7, one writer; counterparties A13 answered with the per-turn record and a unification
    recommendation reported cross-cluster.
[x] Round 5 (2026-09-20): X2 — these five settlement kinds are the ruling; empire-treasury's `settle`
    re-points; `deal-leg` (§7) is missing from ledger-keys' table (exchange-map E-A24).
[x] Audit 2026-09-20 (independent): E-A24 answered — ledger-keys lists `deal-leg`
    (trade-foundation/spec-ledger-keys.md §4). Fixed: dedupe-key collisions (one soul row and one
    world-stock row per key, summed); deal legs settle by one fulfilment ratio (accept-then-default
    exploit closed) and draw only pass-start stock; criterion 3 scoped to order baskets.
```

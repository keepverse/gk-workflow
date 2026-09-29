# Spec: `price-curve`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 4 of the [exchange map](../exchange-map.md) (wave 1; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.2, §14b (*"The price
formula divides by zero at empty stock and truncates cheap goods to free"*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Pure, integer price math for one good at one hub: the mid price from stock against demand, the buy
(ask) and sell (bid) prices after spreads, and the **walk** that prices a volume step by step so a large
order never trades at one price. No state, no I/O, no tuning file read — every coefficient is passed
in. Every guard the ideal's round-3 review asked for is a named part of the formula, not a comment.

## Scope and non-goals

In scope: the quote; the walk for either side; the load-time checks on the coefficients; the rounding
rules.

Not in scope: where stock, demand and band come from (`order-book` reads them); pro-rata allocation
across traders (`order-book`); fees, tariffs and payment (`settlement-payment`); a hub's capacity
(`exchange-hub`).

## Design

### 1. Inputs

| Input | Meaning | Type |
|---|---|---|
| `base` | `ValueOf(good)` (`goods-valuation`) | `long`, ≥ 1 |
| `stock` | The hub owner's own stock of the good in the hub sector, consignments excluded | `long`, ≥ 0 |
| `demand` | The hub owner's demand for the good at that sector (`counterparties` `need-vector`, ask E-A10) | `long`, ≥ 0 |
| `floor` | `price.floorUnits` scaled to the hub (`exchange-hub` supplies the scaled value) | `long`, ≥ 1 |
| `bandMilli` | `price.bandMilli` — how far price moves from base | `long`, 0 ≤ x < 1000 |
| `buySpreadMilli`, `sellSpreadMilli` | `spread.buyMilli`, `spread.sellMilli` | `long`, ≥ 0 |
| `relationSpreadMilli` | `spread.byDispositionBand.{band}Milli` for the trader's band with the hub owner | `long`, ≥ 0 |

### 2. The quote

```
d = max(demand, floor)        s = max(stock, floor)                 // both floored: no divide by zero
imbalanceMilli = clamp((d − s) × 1000 / min(d, s), −1000, +1000)   // bounded ratio (comment says so)
F1 = 1_000_000 + bandMilli × imbalanceMilli                         // > 0 because bandMilli < 1000
priceMilli = base × F1 / 1000                                       // value per unit, ×1000 (display)
askMilli   = ceil (base × F1 × (1000 + buySpreadMilli  + relationSpreadMilli) / 1_000_000)
bidMilli   = floor(base × F1 × (1000 − sellSpreadMilli − relationSpreadMilli) / 1_000_000)
```

- **Divide by zero is impossible:** both terms are floored at `floor ≥ 1`.
- **Cheap goods never price to free:** `base ≥ 1` and `F1 ≥ 1000` (because `bandMilli ≤ 999`) make the
  numerator of `askMilli` at least `10⁶`, so `askMilli ≥ 1` and any non-empty buy costs at least one
  value unit after the final round-up.
- **Round against the trader:** ask rounds up, bid rounds down. That is what makes `ask > bid` hold even
  when `priceMilli` is tiny (§Acceptance 1).
- **The relation band is one spread term**, never a second relation axis (ideal principle 11). The band
  comes from the logged snapshot (`counterparties` `relation-facts`, cross-map decision CM1).
- `imbalanceMilli` is a **bounded ratio** in [−1000, +1000]; its clamp is exempt from the caps rule and
  the code comment says so (`ssot-power-scale.md` §11.6).

### 3. The walk

`Walk(side, volume, stepUnits, quoteInputs) → (filledUnits, totalValue)`:

```
remaining = volume; costMilli = 0; s = stock
while remaining > 0:
    u = min(stepUnits, remaining)
    s = side == Buy ? s − u : s + u                      // move the stock FIRST ...
    per = side == Buy ? askMilli(s) : bidMilli(s)       // ... then price the step at the moved stock
    costMilli = checked(costMilli + u × per)
    remaining −= u
totalValue = side == Buy ? ceil(costMilli / 1000) : floor(costMilli / 1000)
```

**Each step is priced at the stock it leaves behind** — the worse end of the step for the trader, on
both sides. Pricing a step at the stock it starts from would let a trader buy a whole step at the
cheap end and sell it back at the dear end: with a step that moves the price by more than the two
spreads, that round trip gains. Pricing at the moved stock makes every unit's buy price at least the
ask at the level after that unit left, and every unit's sell price at most the bid at the level after
it arrived, which is the whole proof of Acceptance 5.
- A buy walk never takes `s` below the bound the caller passes (`order-book` passes stock above the
  owner's reserve); the walk itself throws if asked to.
- `stepUnits` is `orderStepUnits` scaled to the hub (value-normalised, map assumption 4), at least 1.
- Demand is held fixed inside one walk: it is recomputed from state each step of the turn engine, never
  stored (contradiction EC11 — so this module owes no `demandRecoveryPerTurnMilli` key).
- The flat-price batch loop (a whole batch filled at one quoted price, ideal §6) is impossible by construction: every step re-quotes.

### 4. Numeric types and range

All operands `long`, every product `checked`, widened before multiplying.
`base × F1 × (1000 + spreads)` is at most about `base × 2·10⁶ × 2·10³`; with `base` in the tens it
stays below 10¹², far inside `long`. The per-step product `u × per` is the first to reach the range
limit, at a step of roughly 10¹⁴ units — a quantity a hub reaches only at `Θ` in the tens of millions
(content scale grows with `Θ²`, `ssot-power-scale.md` §4). Past it, `checked` throws; it never wraps
(PRINCIPLES §5). **Magnitude × magnitude products are not made here:** every product in this file is a
magnitude (`u`, `base`) times a bounded per-mille factor. A caller that multiplies two content-scaled
magnitudes (`order-book`'s pro-rata and capacity scaling) owns its own wide intermediate (`order-book`
§Design 8). Floating point is allowed by the owner's 2026-09-15 ruling, but this math feeds the
state hash, and integer arithmetic needs no platform stamp (`ssot-power-scale.md` §10.7).

### 5. Load-time checks (T5)

Refused at load, naming the key: `bandMilli ≥ 1000`; any spread `< 0`;
`sellSpreadMilli + max(relationSpreadMilli) ≥ 1000` (a bid could go negative);
`buySpreadMilli + sellSpreadMilli < 1` (a lossless round trip would merge stocks, P5);
`floorUnits < 1`; `orderStepUnits < 1`; a disposition band with no `relationSpreadMilli` row (the join
is against the band registry, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`).

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | The per-mille discipline the formula follows (widen, `checked`, divide last) | `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:31-40` |
| Built | The band registry the spread joins against | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` |
| Real gap | All of it — `src/FusionRpg.Core/World/Trade/Pricing/` does not exist | — |

## Tunables

`data/tuning/trade.v{n}.json`: `price.bandMilli` (seed 750, the prior-art anchor in ideal §13), `price.floorUnits`,
`spread.buyMilli`, `spread.sellMilli` (seed range 120/110 to 250/600, ideal §13),
`spread.byDispositionBand.{eager,open,wary}Milli`, `orderStepUnits` (seed 10, ideal §13).
**Round 4:** the `hostile` spread key is dropped — `hostile` blocks trade outright
([decisions-round-4.md](../decisions-round-4.md) Q1; `trade-access` §2), so no fill ever reads it and a
key with no reader is not published. The band still sets the spread at every band that trades.
Values are decided by principle at publish time. The file is a Math surface: no bare literal in
`Pricing/` (T3); `1000`, `1_000_000` are the per-mille literals the audit exempts.

## Acceptance (contract)

1. For every generated input: `askMilli ≥ priceMilli ≥ bidMilli`, and `askMilli > bidMilli` (strict)
   under the load-time checks.
2. `stock = 0`, `demand = 0`, or both: no throw, no divide by zero; `imbalanceMilli` is finite and
   within [−1000, +1000].
3. For every `base ≥ 1`: `askMilli ≥ 1`, and a buy walk of volume ≥ 1 costs ≥ 1 value unit.
4. Monotone walk: for a buy, total value ≥ volume × the quoted ask at the starting stock (in milli,
   before the final round); for a sell, total ≤ volume × the quoted bid. Price is non-increasing in
   stock and non-decreasing in demand.
5. **Round-trip loss at a single hub (invariant I3, the pricing half).** For every stock `s₀`, demand
   and `q ≥ 1`, buying `q` then selling `q` loses value in both shapes the engine can produce:
   (a) both legs walked from `s₀` in one settlement pass (`order-book` reads both sides from pass-start
   state), and (b) the sell walked from the stock the buy left, `s₀ − q`, with nothing else changed
   (the next turn, no other trader). In both, `sellValue < buyValue`. For (b): the buy pays at least
   `Σ ask(x)` over the levels `x = s₀−q … s₀−1`, the sell earns at most `Σ bid(x+1)` over the same
   levels, and `ask(x) > bid(x) ≥ bid(x+1)` term by term. Tested with step sizes both smaller and
   larger than `q`, including a step large enough to move price by more than both spreads (the case a
   start-of-step price would get wrong).
6. Splitting a walk: walking `q₁` then `q₂` from the moved stock gives the same `costMilli` (before the
   final round) as walking `q₁ + q₂` when `q₁` is a multiple of `stepUnits` (the walk is additive on step
   boundaries). After the final round the split total is **≥** the joint total for a buy and **≤** for a
   sell (each part rounds against the trader), so splitting never helps a trader. *(Audit 2026-09-20:
   this criterion asserted equality in value units, which the per-walk `ceil`/`floor` makes false.)*
7. Integer overflow throws (`checked`); `python gk-core/scripts/audit-overflow.py --targets A3` reports nothing
   under `World/Trade/Pricing/`.
8. Every load-time check in §Design 5 rejects its bad document with the key named.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Pricing/` (new), trait `core.world-trade.pricing`, boundary
  row `core-world-trade-pricing`. Property tests draw inputs from a seeded generator
  (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`, `DeriveStream`), print the number of cases, and never
  assert a count of cases.
- `verify-change.ps1 -Paths` on the Pricing files and tests; `python gk-core/scripts/audit-overflow.py`;
  `python gk-core/scripts/audit-magic-numbers.py --targets M1` shows nothing in `Pricing/`.

## Hard edges

- **Pure.** No `WorldState`, no tuning hub, no clock, no RNG (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-48`
  covers the World tree).
- **No hidden ceiling.** Price moves within `base × (1 ± bandMilli/1000)`, a bounded ratio of a
  level-free base — not a cap on a magnitude. Volume is never capped here.

## Dependencies

- Upstream: `goods-valuation` (`base`).
- Downstream: `order-book` (walks), `trade-ai` `trade-intel` (quotes it records), `trade-surface`
  (displayed quotes).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `PriceCurve.Quote(QuoteInputs) : Quote(PriceMilli, AskMilli, BidMilli, ImbalanceMilli)` | `order-book`, `trade-ai`, `trade-surface` |
| `PriceCurve.Walk(Side, long volume, long stepUnits, QuoteInputs, long stockBound) : (long Filled, long Value)` | `order-book` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: tunables, numeric types, caps (bounded ratio), economy (P5 lossy conversion).
[~] Session boundary: trade-network-idea-20260919; new file only; boundary check exit 1 is the recorded
    broad-lane crossing.
[x] Read this session: trade-network-ideal §7.2, §13, §14b; tunables-ssot §0-§4; ssot-power-scale §9.4,
    §10.2, §10.7, §11.6 (by heading); PRINCIPLES §5.
[x] decisions.md: no lock covers prices.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH.
[x] Verified against code: ContentScale.Apply's arithmetic; SeededRng.DeriveStream signature.
[x] Surrounding sections read (§7.2 whole; §14b economy table whole).
[x] No constraint claimed without a run; the range threshold is arithmetic, shown.
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC11 (no demand recovery key) in the map's tunables line.
[x] No population count pinned; property tests print case counts.
[x] No event-refreshed cache.
[x] No ordering criterion (pure functions).
[x] No actor magnitude.
[x] No SOLID-violating path: one pricing function for player and AI.
[~] Registry row: invariant I3 (pricing half) rides the exchange-invariants guard row.
```

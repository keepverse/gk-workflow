# Spec: `goods-valuation`

**Status: written 2026-09-19 against code at `b82a4098` (`features/mega-merge`); every `file:line`
below was opened this session.** Module 1 of the [exchange map](../exchange-map.md) (wave 1; approved
2026-09-19). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.2, §7.5, §14b.
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Give every good one number, `ValueOf(goodId)`: a relative worth in **value-index units**, held by
nobody. It is the base of every hub price (`price-curve`), the unit fees and tariffs are charged in
(`settlement-payment`), the unit every AI deal is scored in (`trade-ai` `deal-valuation`), and the base
the item program derives item prices from (filed ask E-A1), which is what the Delve merchant is waiting
for. Beside it, one conversion, `SoulsBaseFor(valueUnits)`, turns value units into souls for the
player's soul top-up and for the item program.

Success looks like: one tuning block names a base value for every tradeable good; a missing good fails
the load by name; nothing in the World tree multiplies a value by a content scale; and the soul
conversion is applied to a quantity exactly once, never twice.

## Scope and non-goals

In scope: the value table and its loader; `ValueOf`; `SoulsBaseFor` and its inverse
`ValueForSouls`; the `§10.2` power-scale row and its `inventory.json` mirror; the first `trade`
tuning file if none exists yet.

Not in scope: prices (`price-curve`); need-weighted valuation of a deal (`trade-ai` `deal-valuation`
reads `ValueOf` and multiplies by `need-vector`); item prices (the item program derives them, E-A1);
the Delve merchant's formula (unchanged, `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:49-62`).

## Design

### 1. The value table

```
ValueOf(goodId) = trade.goods.{goodId}.baseValue        // long, ≥ 1, value-index units per unit of good
```

- Keys exist for every good whose `tradeable-goods` class is `tradeable` or `world-barter-only`.
  Goods of class `never` and the payment-only wallet (souls) have no key; asking for one throws.
- The value index is **relative and level-free**. It is never multiplied by `contentScale` or read
  through `P(Θ)` (ssot-power-scale PS-4). The scale of a trade lives in the **quantity**: a deeper
  sector yields more units (`sector-yield` `essence-loop-read`), each worth the same base.
- Seed shape from the ideal §13: a relative ratio ladder (1 / 2 / 4 / 10 / 20; prior art in ideal §6 and §13) across substrate,
  essence, shard rungs and catalysts, decided by principle at publish time and never an owner question.

### 2. The soul conversion — scaled once, where the scale already is

```
SoulsBaseFor(v)  = ceil(v × soulsPerKiloValue / 1000)     // souls a buyer owes for v value units
ValueForSouls(s) = floor(s × 1000 / soulsPerKiloValue)    // value units s souls can cover
```

Both round against the payer (`ceil` on what is owed, `floor` on what is covered), so a round trip
through the conversion never creates value. `soulsPerKiloValue` is `payment.soulsPerKiloValue`
(`long`, ≥ 1; the map's `payment.soulsBasePerValueMilli`, renamed for its unit, T6).

**Which callers scale, and why only one of them does (contradiction EC6, resolved here).** Every soul
price in the game ends in one scaling function, `SoulSinkPolicy.Price`
(`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40-41`), which multiplies by `ContentScale` once
(`gk-core/src/FusionRpg.Core/Power/ContentScale.cs:31-40`). The map told `SoulsBaseFor`'s callers to pass its
result through that function with the hub's `Θ`. For trade that would scale twice:

- Trade quantities are already content-scaled — a sector at depth yields more units
  (`sector-yield` `essence-loop-read`, map assumption 4). The soul faucet scales by the same content
  scale (`gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:92-93`). Souls per unit must therefore stay
  flat for the conversion to keep one scale on both sides (PS-5). Multiplying the soul leg by
  `ContentScale` again would make the same share of a deep sector's output cost `contentScale²` more
  souls.
- An **item** is one object whose magnitude, not count, carries the depth. Its bill of materials is
  priced at the pin, so the item program **does** pass `SoulsBaseFor(billValue)` through
  `SoulSinkPolicy.Price` once, exactly as the Delve merchant already does
  (`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:61`).

So the rule is one sentence: **a soul amount is scaled exactly once — in the quantity for trade, in
`SoulSinkPolicy.Price` for a pin-priced item.** Trade settlement never calls `SoulSinkPolicy.Price` or
`ContentScale` on a soul leg; a source-scan test enforces it (Acceptance 4). The map's external
dependency on `npc-story-events` `host-content-theta` for the soul leg is dropped.

### 3. Numeric types

All values `long`. `ValueOf × quantity` is computed by callers with `checked` multiplication, widened
before multiplying. `SoulsBaseFor` multiplies then divides once, last. Range: a value of 20 per unit
times a quantity near `long.MaxValue / 20` is the first overflow, far past any reachable `Θ`
(PRINCIPLES §5 table; `long` holds magnitudes to `Θ` ≈ 214.7 million); overflow throws, never wraps.

### 4. Loading

A `TradeTuningLoader.Parse` (host-injected, T8 — Core never reads a file) and a `TradeTuningHub`
static, the `WorldTuningLoader` / `WorldTuningHub.Configure` pattern
(`gk-core/src/FusionRpg.Server/Program.cs:47-49`). If another trade sub-program lands the loader first, this
module adds its block to that loader — one loader per tuning domain.

## What already exists

| | Finding | Evidence |
|---|---|---|
| Built | One soul-price scaling function, content-scaled once | `gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:40-41`; `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15-20`, `:31-40` |
| Built | The soul faucet scales by the same content scale | `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:92-98` |
| Built | The tuning load-and-inject pattern | `gk-core/src/FusionRpg.Server/Program.cs:47-49`; `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:245` |
| Wiring gap | The Delve merchant refuses to price until an item-side base exists | `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs:17`, `:56-58`; `docs/architecture/item/seed-contract.md` §2.1 (price is DERIVED, none exist) |
| Real gap | Any goods valuation; any `trade` tuning domain (`gk-core/data/tuning/` holds no `trade.*`) | — |

## Tunables

| Key | Unit | File |
|---|---|---|
| `goods.{goodId}.baseValue` | value units per unit of good | `data/tuning/trade.v{n}.json` |
| `payment.soulsPerKiloValue` | souls per 1000 value units | same |

**Publishing (contradiction EC14).** Several trade maps each say "`trade.v1.json` (new)". The publish
tool can only bump an existing file (`gk-core/tools/tuning/publish.py:60-68`) and adds a key with `--add-key`
(`gk-core/tools/tuning/publish.py:421-446`). So: if no `trade.v*.json` exists when this module lands, it
authors `trade.v1.json` holding only its own keys; otherwise it publishes `v{n+1}` with `--add-key`.
Every later exchange module follows the same rule.

## Acceptance (contract)

1. Every good in the `tradeable-goods` table whose class is `tradeable` or `world-barter-only` has
   `baseValue ≥ 1`; a missing or non-positive key is a load rejection naming the good (T5). The
   join is asserted against the table, never a count of goods.
2. `ValueOf` of a `never` good or of souls throws with the id named.
3. `SoulsBaseFor` is monotone non-decreasing in `v`, and the conversion rounds against the payer both
   ways: for every `v`, `ValueForSouls(SoulsBaseFor(v)) ≥ v`, and for every `s`,
   `SoulsBaseFor(ValueForSouls(s)) ≤ s` — asserted over a seeded property sweep.
4. Source scan (Guard.Tests): no file under `src/FusionRpg.Core/World/Trade/` references
   `ContentScale`, `SoulSinkPolicy` or `PowerLadder`. The one content-scale read exchange needs (hub
   clearing capacity, `exchange-hub`) goes through `sector-yield`'s sector-scale function, which lives
   outside this tree, so the scan has no allowlist.
5. `ssot-power-scale.md` §10.2 gains one row for the value index (relative, level-free, PS-4 standing),
   and `docs/architecture/power/inventory.json` mirrors it in the same change (`guard-power.py` G3).
   The change is not done without both.
6. Integer overflow in `SoulsBaseFor` throws (`checked`); `python gk-core/scripts/audit-overflow.py --targets A3`
   reports nothing under `World/Trade/Valuation/`.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Valuation/` (new): load rejection per missing key; the
  round-against-the-payer property sweep; monotonicity. Tests carry
  `[Trait("VerificationId", "core.world-trade.valuation")]`, the shape
  `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectMathTests.cs:30` uses.
- `gk-core/tests/FusionRpg.Guard.Tests/`: the source scan in Acceptance 4.
- **Boundary rows.** New paths today fall to `core-fallback` (`gk-core/src/FusionRpg.Core/**`, a whole-project
  run; `gk-core/scripts/verification-boundaries.v1.json` entry `core-fallback`). This module adds a focused
  boundary `core-world-trade-valuation` (paths `src/FusionRpg.Core/World/Trade/Valuation/**` and its
  tests, `verificationId` `core.world-trade.valuation`) so `verify-change.py` selects seconds, not the
  project. `gk-core/scripts/guard-verification-boundaries.py` stays green.
- Verify once: `.\scripts\verify-change.py -Paths <every changed file> -Session <id>`; plus
  `python gk-core/scripts/guard-power.py` and `python gk-core/scripts/audit-overflow.py`.

## Hard edges

- **Never a currency.** No balance of value units exists anywhere — not per faction, not per hub, not
  across a turn. A value amount lives only inside one settlement computation.
- **Scale once.** A soul leg is scaled in its quantity or by `SoulSinkPolicy.Price`, never both.
- **No `f(level)`.** `ValueOf` takes a good id and nothing else.

## Dependencies

- Upstream: `tradeable-goods` (the class of each good — built in the same wave; this module's key set
  is asserted against it). `trade-foundation` `world-stamp` is not needed: nothing here changes a
  hashed state.
- Downstream: `price-curve`, `settlement-payment`, `trade-ai` `deal-valuation`, item program (E-A1).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `GoodsValuation.ValueOf(string goodId) : long` | `price-curve`, `settlement-payment`, `trade-ai` |
| `GoodsValuation.SoulsBaseFor(long valueUnits) : long`, `ValueForSouls(long souls) : long` | `settlement-payment` (unscaled, trade); item program (then `SoulSinkPolicy.Price` once); `trade-ai` `deal-valuation` (`ValueForSouls` is the inverse trade-ai ask T-A6 called `ValueOfSouls` — one function, this name) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy (P5 conversion, soul sinks), tunables, numeric types, power (PS-4, PS-5).
[~] Session boundary: trade-network-idea-20260919 owns docs/architecture/trade-network/**; this file is
    new. session-boundary-check.py exits 1 on the broad-lane crossings that record already notes.
[x] Read this session: DESIGN-GATE (whole), PRINCIPLES §5/§11, economy-principles (whole),
    empire-resource-ssot (whole), tunables-ssot §0-§4, ssot-power-scale §9.4/§10.2/§10.4/§10.7,
    ssot-materials-crafting §3, §4.3, §5, §7.3, trade-network-ideal §3, §7, §13, §14b.
    Not read: creatures/spec-soul-economy.md (its sink rules taken from SoulSinkPolicy's code).
[x] decisions.md:108 (registry) respected; no lock covers valuation.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH (run recorded in the session report).
[x] Verified against code: SoulSinkPolicy, ContentScale, SoulEarnPolicy, DelvePrices bodies read.
[x] Surrounding sections read (SoulSinkPolicy class doc; DelvePrices class doc).
[x] No constraint claimed without a run; nothing here moves a golden (no hashed state).
[x] No §2 invariant contradicted.
[x] Corrections propagated: EC6 and EC14 recorded in the exchange map.
[x] No population count pinned; the key set is asserted as a join against tradeable-goods.
[x] No event-refreshed cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No SOLID-violating path: one value table, one soul scaling function.
[~] Registry row: Acceptance 4's source scan gets a guard row in gk-core/scripts/enforcement-registry.v1.json
    with the change that adds it.
```

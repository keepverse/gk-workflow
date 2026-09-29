# Spec: `deal-valuation`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `deal-valuation`, row 2 of the approved
[trade-ai map](../trade-ai-map.md) (wave 1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§6 lesson 9 (*"one valuation function for both sides of every AI deal"*), §7.5, §7.7. Upstream:
`exchange` `goods-valuation`, `treaty-vocabulary`, `trade-access`; `counterparties` `need-vector`
([spec](../counterparties/spec-need-vector.md)); this map's `trade-intel`.

## Objective

Every AI trade decision — a bid's limit price, a hub sale, a route redirect, a treaty proposal, an
answer to the player, an answer to another AI, a counter-offer step — reduces to one question: *is this
deal worth it to me?* This module is the **one function** that answers it, and the one rule that turns
the answer into accept or refuse. It is the same code for proposer and responder, for player-facing and
AI-to-AI deals, so no deal can be worth more to the AI because of who wrote it or which surface it came
through. That is the lesson of the classic 4X deal-screen failure: a separate buy and sell valuation, and
lump-sum-now for promises-later, leaked value to anyone who probed them (ideal §6).

Success looks like: the same deal, handed to the same faction in the same belief, always scores the
same; a deal and its exact mirror are never both accepted; dumping a large quantity at a peak want
earns no more than selling it in small steps; and every refusal can say why in numbers.

## Scope and non-goals

**In:** `DealValue(party, deal, view)`, the acceptance rule, the band gate order, the confidence and
territorial-risk considerations (the utility scorer's first production caller), the deal time-shape
rule, the explanation record.

**Not here:** prices at hubs (`exchange` `price-curve`); the article vocabulary and deal payload
(`exchange` `treaty-vocabulary`, ask T-A5); what to propose or when (`ai-treaty-policy`); the counter walk
(`counter-offer-articles`); anything inside `Step` — valuation runs only in policies, outside the engine.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `ValueMap` scores **sectors** on six per-mille axes; it has a need input its only caller never passes | `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:60-134`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60` |
| `INeedVector` is per-mille against a neutral 1000; the only implementation is uniform | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:15-41` |
| The utility scorer: integer curves, product of considerations with arity compensation, and `Weakest` to name the limiting consideration — **no production caller** (a repo grep finds none outside `Ai/Utility/`) | `gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:37-53`, `:83-98`; `gk-core/src/FusionRpg.Core/World/Ai/Utility/ResponseCurves.cs:41` |
| Threat with a defensive and an offensive reading, decayed by staleness | `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:47`, `:71` |
| Only the player holds souls; an AI faction has no soul balance | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149` |
| AI tuning is loaded once and a missing key is a load rejection | `gk-core/src/FusionRpg.Core/World/Ai/WorldAiTuning.cs:40-84`, `:116-118`; loaded at `gk-core/src/FusionRpg.Server/Program.cs:233-234` |

### Wiring gap

- The scorer has no caller. This module is its first.
- `ValueMap`'s need input is never passed (`FrontierRulesPolicy.cs:60`); `counterparties` `need-vector`
  closes that (its §5). This module reads the same vector and does not re-wire `ValueMap`.

### Real gap (this module closes it)

The deal function, the acceptance rule, the time-shape rule and the explanation record.

## Design

### 1. The deal, as valued

The deal payload is `exchange`'s (T-A5). This module values the shape it proposes there:

```text
Deal  = (Kind?, TermTurns, TariffMilli?, Legs[], SoulsTopUp, LiftsEmbargo, Shape)
Leg   = (GoodId, Qty, FromFaction, ToFaction)          // Qty in value-normalised units
Shape = OneOff | PerTurn                               // one shape for the whole deal
```

**One time shape per deal (the lump-sum guard).** A deal is either wholly one-off (a barter) or wholly
per-turn over `TermTurns` (a treaty with per-turn legs). A deal mixing a lump sum with a per-turn
promise is **out of vocabulary** and valued as `Rejected(OutOfVocabulary)` before anything else — the
ideal's *"no lump-sum-for-per-turn deals in v1"* made a type rule, not a heuristic.

### 2. `DealValue(party, deal, view) → long`

A signed sum of leg values **to `party`**, in value-index units (the `exchange` index, relative, never
scaled by `contentScale`). There is no proposer argument.

| Leg | Value to `party` |
|---|---|
| **Goods received / given** | walked in `orderStepUnits` steps. Step *k* of good *g* is worth `ValueOf(g) × step × want_k / 1000`, where `want_k` is the need vector's want **at the stock the party would hold after step *k*** (`NeedVector.Compute` over an adjusted input record — `counterparties/spec-need-vector.md` §4). Received steps add, given steps subtract. |
| **Souls top-up** | legal only from a party with a soul wallet (today: the player — a data fact, not a faction-kind branch); valued at `exchange` `goods-valuation`'s `ValueForSouls` (T-A6; the inverse already exists under that name, exchange EC26) |
| **Treaty kind** | `AccessValue(party, kind, counterpart, horizon)`: for the receiver, the believed per-turn trade gain it opens (quotes and flows from `trade-intel`) minus tariffs it will pay; for the grantor, the tariffs it will earn minus, for `passage`, a **territorial risk** term (§4) |
| **Tariff step** | at value, over the horizon |
| **Embargo lift** | the believed flows it restores (receiver) or re-admits (grantor), over the horizon |

- **Horizon.** A per-turn deal is valued over `min(TermTurns, treaty.minimumTermTurns)` — the part both
  sides are bound to. **Round 6 Q-A:** declaring **war** on a partner inside the minimum term now also writes
  `treaty.broken` (`exchange/spec-treaty-lifecycle.md` §5), so the `treatyBrokenWeightMilli` cost this module
  prices applies to *both* early exits — war is no longer a free way out of a term, and the valuation needs no
  war-specific term to say so. After the minimum term either side may end it without a `treaty.broken` fact, so
  a longer promise is worth nothing extra (the second guard: value only what binds).
- **Concavity is the dumping guard.** Want falls as stock rises (`need-vector` rule,
  `want = 1000 × (demand + k) / (stock + k)`), so each received step is worth no more than the last.
  Selling 100 units at a peak want earns the walked sum, never `100 × peak`.
- **Belief, not truth.** For `party == view.FactionId` the want is exact (own stock is never fogged).
  For another party the want comes from `NeedVector.Compute` over an input record built from what
  `party` is believed to hold and field (climate, surveyed stock, remembered forces); the code path is
  identical — only the input record differs (the `SupplyReach` one-rule-two-inputs precedent,
  `spec-ai-commander.md` §Believed supply). `need-vector`'s spec builds only the own-faction adapter, so
  the other-party adapter is ask T-A7; until it lands another party's want reads the neutral 1000.
- **Confidence.** Every believed input (a quote, a flow) is discounted by a confidence consideration
  (§4), so a six-turn-old quote argues less than today's.

### 3. The acceptance rule

```text
accepts(party, deal) =
    BandGate(pair, deal.Kind)      is Open                       // 1. the band limits what is possible
 && BuildingGate(pair, deal)       is Open                       // 1b. round 4: the buildings the deal class needs
 && DealValue(party, deal) ≥ max(1, acceptMilli[band] × Give(party, deal) / 1000)   // 2. valuation decides
```

- `Give(party, deal)` is the absolute value of the legs `party` gives — "gain at least `acceptMilli` ‰ of
  what you hand over".
- **Band gate first.** If the pair's logged band (`counterparties` `relation-facts`) is below the kind's
  lowest band (`exchange` `treaty-vocabulary`), the answer is `Refused(Band, required)` and no valuation
  runs.
- **Strictly positive margin (the anti-pump guard).** `acceptMilli[band] ≥ 1` for every band is a load
  check (a zero or negative threshold would let a friendly partner cycle a deal and its mirror forever,
  each at no loss to the AI). Each step is valued at the want **after** that step, so giving a good back
  is valued at the higher wants the receiving walk passed through: a round trip never gains,
  `DealValue(d) + DealValue(mirror(d) after d) ≤ 0`, and at most one of the two can clear a strictly
  positive threshold.
- **Building gate first too (round 4).** `BuildingGate` reads `exchange`'s tier tables
  (`treaty-vocabulary` §5) through the view: an empire treaty needs the **offerer's** Embassy
  (`counterparties` `DiplomacyGate`, offerer only — its CQ1 default), a `preferential` kind an Exchange,
  a bloc a Consulate and an Exchange, goods legs a hub where the other party's `LevelAt ≥ market`. A missing building answers `Refused(Building, tier)` before any valuation
  — the AI never values a deal admission or resolution would refuse. Clans need no embassy.
- **Explanation.** The rule returns a `Verdict(accepted, code, band, value, threshold, weakest)` where
  `code ∈ {Accepted, Band, Building, Shortfall, OutOfVocabulary}` (`treaty-vocabulary` §6's refusal codes) and `weakest` is the scorer's `Weakest`
  consideration name when a discount drove the shortfall (`Consideration.cs:83-98`). `counter-offer-articles`
  renders it; nothing else formats a refusal.

### 4. Where the utility scorer enters

The scorer's output is 0..1000 (`Consideration.cs:37-53`), so it scales quantities; it does not sum
them (TC3, refined). Two uses:

- **Confidence ‰** on each believed input: `Score([Freshness: Inverse(age × staleDecay), Sight:
  Linear(exact ? 1000 : bandConfidence)])`. `staleDecay` is the threat map's own
  `threatMap.staleDecayPerTurn` — one staleness rule for fear and for prices, not two.
- **Territorial risk ‰** for granting `passage`: `Score([Proximity: Linear(counterpart's believed
  offensive strength within reach of my seats ÷ my garrison — **my** garrison read from the power
  roll-up over my own legions once it lands (round 4 P; until then the stack count the ladder uses
  today), the counterpart's from belief bands as before), Appetite: Linear(counterpart war appetite
  from its personality row)])`, times the strategic worth of the sectors the passage crosses
  (`ValueMap`'s strategic axis, converted to value units by `trade.valuation.territoryValuePerPoint`).
  This is the only place `ValueMap` enters (TC2).

### 5. Determinism

Pure over `(view, deal)`. No seed is consumed; ties (equal-want goods in a walk) break by good id.
`long`, `checked`, widened before multiplying, divided by 1000 last (CLAUDE.md numeric rules); the
walk's step count is bounded by `Qty / orderStepUnits`, a structural loop bound.

### 6. Where it lives

`src/FusionRpg.Core/World/Ai/Trade/DealValuation.cs` (new) — under `World/Ai/`, so the existing
no-`WorldState` scan (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:108`) and the
no-clock scan cover it the day the folder exists.

## Tunables

| Key | File | Unit | Why tunable |
|---|---|---|---|
| `acceptMilli.{eager,open,wary}` | `data/tuning/diplomacy.v1.json` (new) — **owned by this module** (exchange EC22; both maps had named the other). `hostile` has no key: round 4 blocks every deal at `hostile` | ‰ of value given | the relation feel of every negotiation; load check `≥ 1` |
| `trade.valuation.bandConfidenceMilli` | `gk-core/data/tuning/ai.v3.json` (next AI version) | ‰ | how much a banded read is trusted |
| `trade.valuation.territoryValuePerPoint` | same | value units per `ValueMap` point | the exchange rate between ground and goods |
| `trade.valuation.passageRiskWeights` | same | consideration weights | how nervous a grantor is |

Reused, never duplicated: `threatMap.staleDecayPerTurn` (`gk-core/data/tuning/ai.v2.json`), `orderStepUnits`
and `treaty.minimumTermTurns` (`exchange`). Policy-only keys stay in the AI domain because `Step` never
reads it, so re-tuning the AI never trips the world stamp's replay check (TC5).

## Acceptance (contract)

1. **One implementation.** A source scan finds exactly one `DealValue` body; `ai-bidding`,
   `ai-treaty-policy`, `ai-logistics`, `counter-offer-articles` and `clan-behaviour` call it and contain
   no valuation arithmetic of their own.
2. **Symmetry.** For two factions with identical inputs, `DealValue(A, d) == DealValue(B, mirror(d))`
   for every generated deal.
3. **Proposer-blind.** The signature has no proposer; relabelling who proposed changes nothing.
4. **Need-monotone.** Raising `party`'s want of a good it receives never lowers `DealValue`; raising its
   want of a good it gives never raises it.
5. **Concave (dumping guard).** Splitting a received leg of `q` into consecutive legs `q1 + q2` valued in
   sequence (stock updated between) sums to exactly the single-leg value **when `q1` is a whole number of
   `orderStepUnits` steps** (the walk is additive on step boundaries — audit 2026-09-20; a split inside a
   step values the partial step at a different want); valuing `2q` at once is never more than twice
   valuing `q` from the same start.
6. **No pump.** For every generated deal `d`, `DealValue(d) + DealValue(mirror(d))` valued from the state
   after `d` is `≤ 0`; with every `acceptMilli ≥ 1`, `d` and its mirror are never both accepted.
7. **Band gate first.** A deal whose kind the pair's band does not reach returns `Band` without calling
   the need vector (asserted with a throwing need-vector fake).
8. **Time shape.** A deal mixing `OneOff` and `PerTurn` legs returns `OutOfVocabulary`.
9. **Horizon.** Two treaties differing only in `TermTurns` above the minimum term value identically.
10. **Souls legality.** A soul leg from a party with no soul wallet is `OutOfVocabulary`.
11. **Pure and deterministic.** Same `(view, deal)` ⇒ same `Verdict`, byte for byte, twice.
12. **Load.** A missing key, or any `acceptMilli < 1`, rejects the load naming the key.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/DealValuationTests.cs` (new): criteria 2–12 as property
  tests over seeded generated deals (the `WorldCommandRoundTripPropertyTests` style), plus hand cases
  for the band gate and the explanation.
- `gk-core/tests/FusionRpg.Guard.Tests/` (new source scan): criterion 1.
- `gk-core/tests/FusionRpg.Core.Tests/World/Ai/ConsiderationTests.cs` is unchanged; the scorer's contract is
  already tested.
- Run `.\scripts\verify-change.ps1 -Paths <changed paths> -Session <id>`. `World/Ai/**` resolves only to
  `core-fallback` today; the change adds a focused `core-world-ai-trade` boundary row covering
  `src/FusionRpg.Core/World/Ai/Trade/**` and its tests.

## Hard edges

- **None on hashed state.** Valuation runs outside `Step`; replay never re-runs a policy
  (`gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`), so no golden can move from this module.
- **AI tuning version.** This module's keys (`trade.valuation.*`) go into the AI domain file, which
  `ai-spend-limit` **creates** with the loader switch (global audit M8, round 6: one creator per versioned
  file). If this module lands after it, it publishes **`v{n+1}`** through `gk-core/tools/tuning/publish.py` and claims
  no switch; the old wording (this spec also claiming `ai.v3` and the switch) is withdrawn — three specs
  claimed it and only the first lander could have had it.
- **Wave and ruleset bump (round 6 C1):** trade-ai **wave 1**; valuation runs outside `Step`, grants no
  capability flag and takes no bump (see *Hard edges* first bullet: no golden can move from this module).

## Dependencies

| Consumes | From |
|---|---|
| `ValueOf`, `ValueForSouls` | `exchange` `goods-valuation` (T-A6) |
| lowest band per kind, `minimumTermTurns`, deal payload, tier tables, refusal codes | `exchange` `treaty-vocabulary` (T-A5, answered in its §5–§6) |
| `LevelAt`, `EffectiveLevel`; `TradeTier`; Diplomacy tier | `exchange` `trade-access` §2a, `exchange-hub` §7 (through the view, ask T-A9) |
| own legion power (force estimate) | `legion-build` `legion-power` (module 17) (round 4 P), through the view (ask T-A10) |
| `NeedVector.For(view)`, `NeedVector.Compute(inputs)` | `counterparties` `need-vector` |
| logged band snapshot, personality row | `counterparties` `relation-facts`, `empire-roster` (T-A7) |
| believed quotes and flows | `trade-intel` |

| Exposes | To |
|---|---|
| `DealValue`, `Accepts → Verdict` | every other module in this map |
| `Reservation(good, side)` (a one-leg deal's per-unit break-even) | `ai-bidding` |

## Boundaries

- **Always:** one function; band gate before valuation; strictly positive margin; value only the
  binding horizon; explain every refusal with numbers.
- **Ask first:** a lump-sum-for-per-turn deal shape; a threshold that depends on the proposer.
- **Never:** a second valuation path for any surface or faction kind; reading `WorldState`; a seed draw
  inside valuation.

## Design-gate checklist

```
[x] Subsystems: world map AI (policy layer, scorer, ValueMap, ThreatMap), economy (value index, souls
    conversion — read only), relation ladder (band gate), tunables, numeric types.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded in that record; this file is new.
[~] Read this session: as spec-trade-intel.md's list. NOT read: world-map-runtime ideal/specs (FE).
[x] decisions.md: no lock covers AI valuation; the economy registry row (souls never paid out) is
    respected — souls only ever flow from the player and are sunk (exchange settlement).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: ValueMap.For, INeedVector, Considerations.Score/Weakest, ResponseCurves,
    WorldAiTuningLoader, Program.cs ai load line, soul wallet keying.
[x] Surrounding sections read: spec-ai-commander §The decision layer and §The consideration arithmetic.
[x] No constraint claimed without a run: "no golden moves" rests on the existing replay test, cited.
[x] No §2 invariant contradicted; valuation is outside Step (P13 untouched).
[x] Corrections propagated: TC2, TC3 (refined), TC5 recorded in the map.
[x] No population pinned: the Verdict code set (5, round 4 adds `Building`) is `exchange`'s closed refusal-code list, pinned there.
[x] Round 4 reconciliation (2026-09-19): building gate before valuation; `ValueForSouls`; acceptMilli
    ownership settled here (EC22); garrison strength from the power roll-up when it lands.
[x] No event-refreshed cache.
[x] Orderings: none; valuation is order-free.
[x] No actor magnitude produced or consumed.
[x] No SOLID-violating path: one valuation for every caller; the built scorer reused, not re-written.
[ ] Registry rows (one-implementation scan, acceptMilli ≥ 1 load check) owed with the change.
[x] Audit 2026-09-20 (independent): one valuation confirmed (goods through goods-valuation × need, no
    second path); criterion 5 restated on step boundaries; franchise names replaced by generic terms.
```

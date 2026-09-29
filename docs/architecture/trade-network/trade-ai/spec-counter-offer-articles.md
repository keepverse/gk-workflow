# Spec: `counter-offer-articles`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `counter-offer-articles`, row 4 of the approved
[trade-ai map](../trade-ai-map.md) (wave 2). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.7 (counter-offers come from a fixed article list, never a solver — the "make it equitable" button
exploit; every refusal shows its terms). Upstream: `deal-valuation`; `exchange` `treaty-vocabulary`
and `treaty-lifecycle` (the article kinds and the payload — TC4, ask T-A5).

## Objective

When an AI will not accept a proposal as written, it either counters with a nearby deal it *would*
accept or declines — and in both cases the proposer is told exactly why. The counter is found by
**walking a fixed list of single-step changes in a fixed order**, re-scoring after each step with the
one valuation function, and stopping at the first deal that clears the threshold. There is no search,
no optimiser and no "make it fair" button, because a solver that balances a deal is a tool a player can
point at the AI to extract the exact break-even every time (the solver exploit, ideal §6).

Success looks like: the same proposal to the same faction in the same belief always gets the same
counter or the same refusal; every counter differs from the proposal by a short, listed sequence of
steps; every refusal names a band or a number.

## Scope and non-goals

**In:** the walk order over `exchange`'s article kinds, the direction rule per kind, the step bound, the
"never counter a counter" rule, the refusal terms record and its two renderings (the 200-character AI
reason and the structured terms the step writes into the proposer's report).

**Not here:** the article kinds themselves and the deal payload (`exchange` — TC4); the valuation
(`deal-valuation`); when to answer at all (`ai-treaty-policy`); the treaty screen that shows the terms
(`trade-surface` `treaty-screen`).

## The ownership correction (TC4)

The map had this module own "a closed article list". `exchange-map.md` module 9 already has
`treaty-propose` carry *"articles from `trade-ai`'s fixed article list"*, and `exchange` must validate
those articles at admission — so if the list lived here, `exchange` would depend on `trade-ai`, which
depends on `exchange`: a cycle. The player also counters with the same articles, so they are a
**command-payload contract**, which belongs upstream. Resolution: the **kinds** are `exchange`
`treaty-vocabulary`'s (T-A5); this module owns only the **order** they are tried in and the rule for
which direction each step moves.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| AI reasons: a nullable command column, cut to 200 characters at insert | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:196-205`; column `:57` |
| Report lines are fog-scoped by sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:12-31` |
| The scorer can name the consideration that limited a score | `gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:83-98` |
| Commands are the replay unit; a reason is not part of it | `gk-core/src/FusionRpg.Core/World/Ai/IFactionPolicy.cs:6-13` |

### Wiring gap

None.

### Real gap

The walk, the direction rules, the refusal record. The refusal **terms** must travel inside the
`treaty-respond` command, not only in the reason column: the reason is not in the replay unit
(`IFactionPolicy.cs:6-13`), and the proposer learns of the refusal from a turn-report line the step
writes from the command (ask T-A5).

## Design

### 1. The article kinds this walk expects (answered by `exchange` `treaty-vocabulary` §6, T-A5)

| # | Article | One step |
|---|---|---|
| 1 | `goods.ask-more` | +1 `orderStepUnits` of a good the responder already receives |
| 2 | `goods.give-less` | −1 step of a good the responder already gives |
| 3 | `goods.give-remove` | remove one good the responder gives, entirely |
| 4 | `goods.ask-add` | add 1 step of a good the proposer is believed to hold (a stock band > 0 in `trade-intel`) |
| 5 | `tariff.step` | move the tariff one band step in the responder's favour, inside the kind's band |
| 6 | `term.step` | move the term one step toward the responder's preference (shorter when the treaty costs it per turn, longer when it gains) — never below the kind's minimum |
| 7 | `kind.downgrade` | `preferential` → `market` → `passage` |
| 8 | `embargo-lift.drop` | drop an embargo lift the responder was asked to give |
| 9 | `souls.ask-more` | +1 soul step, only when the proposer holds a soul wallet |

The table was this spec's proposal; `exchange` adopted it unchanged as its closed `ArticleKind` list
(`treaty-vocabulary` §6, round-4 reconciliation 2026-09-19) and settles goods legs in `settlement-payment` §7.
`kind.downgrade` also steps **down to what the pair's buildings allow** (round 4): a `preferential`
proposal between parties without an Exchange walks to `market` rather than failing outright.

### 2. The walk

```text
Counter(responder, proposal, view):
    v = Accepts(responder, proposal)                         // deal-valuation
    if v.accepted:                 return Accept
    if v.code == Band:             return Decline(v)          // no step can fix a band
    if v.code == Building and not DowngradeClears(v):  return Decline(v)   // round 4: no step builds an Embassy; only a kind.downgrade to a level the buildings allow can help
    if v.code == OutOfVocabulary:  return Decline(v)
    if proposal.IsCounter:         return Decline(v)          // never counter a counter (§3)
    deal = proposal; tried = []
    for step in 1..counterStepBound:                          // structural loop bound
        a = first article in WalkOrder that is legal on `deal` and raises DealValue(responder)
        if a is none:              return Decline(v, tried)
        deal = a.Apply(deal); tried += a
        v = Accepts(responder, deal)
        if v.accepted:
            if DealValue(proposer, deal, view) < 0:          // same function, proposer side, belief
                return Decline(v, tried)                      // a counter no one would take is noise
            return Counter(deal, tried)
    return Decline(v, tried)
```

- **Walk order is the table order**, fixed and pinned in this module. Within one article, the good
  chosen is the one with the highest responder want (for asking) or the lowest (for giving less); ties
  by good id.
- **Monotone.** Each step must raise the responder's value; the walk never makes the deal worse for the
  responder and never cycles.
- **One function, both sides.** The proposer-side check is `deal-valuation`'s `DealValue` with the
  proposer as party, from the responder's belief — the same code the proposer's own AI would run
  (ideal §7.7).

### 3. Never counter a counter

A counter is a new offer from the responder. The AI answers a counter only with accept or decline, so
any negotiation is at most **proposal → counter → answer**. That bounds every thread at two turns of
offers (a response lands the next turn a party commits, `exchange-map.md` module 9) and removes a
ping-pong a player could farm for information.

### 4. The refusal terms

```text
RefusalTerms = (Code ∈ {Band, Building, Shortfall, OutOfVocabulary}, RequiredBand?, RequiredBuilding?, Shortfall: long,
                Threshold: long, ArticlesTried: [ArticleKind], Weakest: string?)
```

- Carried in the `treaty-respond` payload (T-A5), so the step writes a report line with `Audience =`
  the proposer (`TurnReport.cs:12-31`), and replay reproduces it.
- Rendered once more as the AI reason, ≤ 200 characters:
  `declined market with player-1: short 140 of 380 (tried ask-more ×3, tariff ×1); weakest: freshness`.
- **Transparency is the probing guard.** Because the shortfall is shown, a player learns nothing by
  probing that the refusal does not already say — and each probe costs a turn. What a shown shortfall
  reveals is the threshold, and the threshold is strictly positive (`acceptMilli ≥ 1`, `deal-valuation`
  §3), so even a proposal built to the exact number still leaves the AI its margin — the break-even a
  solver would extract is not on offer (audit 2026-09-20).

### 5. Determinism

Pure over `(view, proposal)`; no seed draw; the walk and its tie-breaks are ordinal.

## Tunables

| Key | File | Unit | Nature |
|---|---|---|---|
| `trade.counterStepBound` | `gk-core/data/tuning/ai.v3.json` (next AI version) | steps | structural loop bound, commented; how far an AI will bend before saying no |

Step sizes are `exchange`'s (`orderStepUnits`, tariff band steps, term step).

## Acceptance (contract)

1. **Listed steps only.** A counter differs from its proposal by a sequence of articles from the walk
   order, of length ≤ `counterStepBound`.
2. **Deterministic.** Same proposal and view ⇒ same counter or refusal, byte for byte.
3. **Explained.** Every refusal names its code's subject — a band (`Band`), a building and tier
   (`Building`), the vocabulary rule (`OutOfVocabulary`) or a positive shortfall (`Shortfall`); a refusal
   with none fails. *(Audit 2026-09-20: this read "a band or a positive shortfall", which the round-4
   `Building` code and `OutOfVocabulary` could never satisfy.)*
4. **No self-harm.** A counter always clears the responder's own threshold.
5. **No noise.** A counter is never produced when the proposer's value of it, from the responder's
   belief, is negative.
6. **Bounded thread.** A counter to a counter is always accept or decline.
7. **Monotone walk.** Responder value strictly increases at each step of a counter.
8. **Walk order is closed.** The order list is pinned (code-owned); every entry exists in `exchange`'s
   article vocabulary.
9. **Reason fits.** Every rendered reason is ≤ 200 characters before the store cuts it.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/CounterOfferTests.cs` (new): 1–7 and 9 as property tests
  over generated proposals and needs; hand cases per article.
- `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs` (extend): a declined player proposal writes one
  report line to the proposer carrying the terms, and replay reproduces it.
- Run `.\scripts\verify-change.ps1 -Paths <changed paths> -Session <id>` (the `core-world-ai-trade`
  boundary `deal-valuation` adds).

## Hard edges

None on hashed state: the walk runs in a policy. The payload fields it needs are `exchange`'s change.

## Dependencies

| Consumes | From |
|---|---|
| `Accepts`, `DealValue`, `Verdict` | `deal-valuation` |
| article kinds, deal and respond payload with refusal terms | `exchange` `treaty-vocabulary`, `treaty-lifecycle` (T-A5) |
| believed proposer stock bands | `trade-intel` |

| Exposes | To |
|---|---|
| `Counter(responder, proposal, view) → Accept · Counter · Decline(terms)` | `ai-treaty-policy`, `clan-behaviour` |
| `RefusalTerms` rendering | `trade-surface` `treaty-screen` (through the report line) |

## Boundaries

- **Always:** fixed order; one step at a time; re-score with the one function; say why.
- **Ask first:** a new article kind (that is `exchange`'s vocabulary change); countering a counter.
- **Never:** a solver, a search over deals, or any "balance the deal" operation; a refusal without terms.

## Design-gate checklist

```
[x] Subsystems: world map AI (policy), diplomacy payload (exchange), turn report (fog), tunables.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list. NOT read: world-map-runtime ideal/specs.
[x] decisions.md: no lock covers counter-offers.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: reason column and cut, TurnReportEntry audience, IFactionPolicy contract.
[x] Surrounding sections read: exchange-map module 9 (the cycle's source).
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: TC4 in the map (module 4 detail, contradictions, ask T-A5).
[x] No population pinned: the walk order is a closed code-owned list; the refusal codes are `exchange`'s
    closed list (round 4 adds `Building`).
[x] Round 4 reconciliation (2026-09-19): T-A5 answered upstream; `Building` refusal; downgrade steps to
    what the pair's buildings allow.
[x] No event-refreshed cache.
[x] Orderings: the walk order is fixed by design, not by filing order.
[x] No actor magnitude.
[x] No SOLID-violating path: one valuation, one article vocabulary (exchange's).
[ ] Registry row for "no solver" (a scan for any search over deals under World/Ai/Trade) owed with the change.
[x] Audit 2026-09-20 (independent): criterion 3 covers all four refusal codes; the shown threshold keeps
    a positive margin; franchise names replaced by generic terms.
```

# Spec: `ai-treaty-policy`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `ai-treaty-policy`, row 6 of the approved
[trade-ai map](../trade-ai-map.md) (wave 3). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§7.4 (*"You trade with an empire only through the routes it opens to you by treaty"*), §7.7. Upstream:
`counter-offer-articles`, `deal-valuation`, `ai-spend-limit`; `exchange` `treaty-lifecycle`,
`trade-access`; `counterparties` `diplomatic-stance`, `diplomacy-facts`, `relation-facts`,
`empire-roster`. Amends nothing by itself: `spec-ai-commander.md`'s *"no diplomacy"* non-goal is
amended by filed ask T-A1 (and counterparties A5), not here.

## Objective

Each AI empire decides, each turn and for each faction it knows, **one** diplomacy move: answer an
offer, make or accept peace, end a treaty that has turned against it, set or lift an embargo, declare
war, or propose a treaty — every one scored by the one valuation function, every one filed as the same
command the player files. The dominant enemy empire, the rival empires and (through `clan-behaviour`)
the clans all run this same code with different personality rows.

Success looks like: the diplomacy log reads one line per relationship per turn; an AI never accepts a
deal below its threshold and never declines one above it except for a named band or war reason;
replacing this policy with another leaves every stored world's replay unchanged.

## Scope and non-goals

**In:** the per-counterparty decision order, the candidate proposals, war and peace scoring, treaty
ending, embargo and bloc choices, the one-command-per-pair rule, how the diplomacy layer composes with
the military ladder into one policy per faction.

**Not here:** treaty mechanics, terms, minimum term and the facts written (`exchange`
`treaty-lifecycle`, `counterparties` `diplomacy-facts`); how bands move (`counterparties`
`relation-facts`); the default stance (`counterparties` Q1). **Round 4 Q4 (2026-09-19):** the dominant
enemy empire never makes peace or a treaty **with the player only**; with rivals and clans it runs this
same code like any empire. The locked pair is `diplomatic-stance`'s `IsLockedWar`, read through the view;
this module files nothing on that pair except what the military ladder already does. Building the
Embassy, Consulate or Exchange a proposal needs is `ai-trade-buildings`' job, not this module's.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| One policy per faction, resolved by id from a catalog; an unknown id is a load rejection | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:11-34`; `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:118-120` |
| `PolicyId` is in the state hash | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:30` |
| The policy contract: pure in `(belief, seed)`, never throws for a well-formed world | `gk-core/src/FusionRpg.Core/World/Ai/IFactionPolicy.cs:28-38` |
| Replay never re-runs a policy — the architectural test | `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`, `:168` |
| Hostility is one rule, today `a != b` for every pair | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16` |
| Threat with a defensive reading per sector, for "is my seat in danger" | `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:47` |
| `Rival` and `Clan` faction kinds exist; neither is seeded | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |

### Wiring gap

None.

### Real gap

All of it. Diplomacy was an explicit non-goal of the AI module (`spec-ai-commander.md` §Non-goals,
line 284).

## Design

### 1. One policy per faction, composed — not a second brain

`FrontierRulesPolicy` keeps its id and its entity walk (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:46-79`).
It gains a **personality id** and, after the entity walk, appends the trade layers' policy orders in a
fixed order: `ai-trade-buildings` (round 4; claims at most one `Hold` legion to `build`) →
`ai-logistics` → `ai-bidding` → `ai-treaty-policy`. Each layer is gated by the world's
capability flags through the view (TC6), so on a world without trade the policy returns exactly what it
returns today.

- **No `PolicyId` change for the dominant enemy empire.** `frontier-rules` maps to the default
  personality, so no template golden moves from a policy-id change (the hash cost named in
  `spec-ai-commander.md` §Corrections 5).
- **Rival personalities** are further ids in `FactionPolicies`, each mapping to the same class with a
  different personality row. `counterparties` `empire-roster` catalogues them; this module registers them.
- Personality is data (`personality.<policyId>.{tradeAppetite,warAppetite,treatyWillingness}Milli`,
  `counterparties`), never a per-empire branch.

### 2. The decision per counterparty

For each faction the AI has **met** — it owns a sector in the AI's belief, or appears in a remembered
force, or shares a diplomacy fact with it — in ordinal faction id order, the first applicable step
files **one** command and the walk moves to the next counterparty:

| # | Step | Fires when | Files |
|---|---|---|---|
| 1 | **Answer** | an offer from this counterparty awaits the AI (view read, T-A6) | `treaty-respond` with `counter-offer-articles`' result (accept, counter, or decline with terms) |
| 2 | **Peace** | at war, and `PeaceScore ≥ trade.diplomacy.peaceThresholdMilli` | `peace-accept` if the counterparty offered, else `peace-offer` |
| 3 | **End** | an active treaty's remaining binding value is negative, and either the minimum term has passed or the loss exceeds the `treaty.broken` cost | `treaty-end` |
| — | *(round 6 Q-A)* | **War is no longer a cheaper exit.** `war.declared` inside a treaty's minimum term also writes `treaty.broken` with the same observer effect (`exchange/spec-treaty-lifecycle.md` §5), so step 5's *"after subtracting the value of every treaty war would void"* term now also subtracts the **same `treaty.broken` cost step 3 pays** — one number, `trade.valuation.treatyBrokenWeightMilli`, for every early exit, per treaty still inside its term. A policy can no longer reach a better score by declaring war instead of ending a treaty, which is the loophole F-X2 named | — (a term in step 5's score, not a new command) |
| 4 | **Embargo** | the value of the counterparty's believed flows through the AI's hubs is negative to it (it gains more by closing than by trading), or lifting a standing embargo is positive; **`embargo-set` only while the AI holds a Consulate** (round 5 C3: a deliberate embargo needs one; lifting needs nothing, and a war embargo is automatic, never filed) — a blocked embargo reports its value to `ai-trade-buildings` like a blocked treaty | `embargo-set` / `embargo-lift` |
| 5 | **War** | at peace, and `WarScore ≥ trade.diplomacy.warThresholdMilli` after subtracting the value of every treaty war would void | `war-declare` |
| 6 | **Propose** | the best candidate (§3) has positive value to the AI and clears the counterparty's believed threshold | `treaty-propose` |

- **Scores.** `WarScore = Score([StrengthAdvantage: Smoothstep(my offensive ÷ their believed
  defensive near the target — **my** side read from the power roll-up over my own legions (round 4 P;
  owner of the roll-up: `legion-build` `legion-power`, round 5 X7, whose `LegionPower.Of` sums **Hub output
  only** and is never re-derived here; round 6 D2 adds the six `world.*` channels to the same roll-up, read
  the same way);
  until it lands, today's stack count), theirs from belief bands), TargetWorth: Linear(best ValueMap sector they hold, normalised),
  Appetite: Linear(warAppetite)])`; `PeaceScore = Score([SeatDanger: Linear(defensive threat on my
  seats ÷ garrison), Appetite: Inverse(warAppetite)])` — the built scorer
  (`gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:37-53`), so a single zero kills the move
  (a hopeless war is never declared).
- **Breaking cost** = `trade.valuation.treatyBrokenWeightMilli` × the value of every other treaty the
  AI holds with an observer of this one (the band drop `counterparties` `relation-facts` applies) — so
  an AI that trades with many breaks treaties rarely.
- **Blocs** are one extra candidate in step 6, `bloc-propose`/`bloc-join`, with the bloc as the subject;
  `bloc-leave` is a step-3 end. At most one bloc command per turn.

### 3. Candidate proposals — a fixed list, not a search

For a counterparty the band allows, the candidates are: each treaty kind whose lowest band the pair
reaches **and whose buildings the AI holds as offerer** (round 4: its own Embassy for an empire treaty —
`counterparties` `DiplomacyGate`, offerer only per its CQ1 default — an Exchange for `preferential`, a
Consulate and an Exchange for a bloc; `treaty-vocabulary` §5; clans need no embassy),
at the kind's minimum term, at the tariff band midpoint, with no goods legs — plus, for a
counterparty at war, the peace offer. Each is valued with `DealValue(self)`; those also valued
positive for the counterparty (same function, belief side) are ranked by own value, ties by kind order
in `treaty-kind.v1`. The best is proposed. No candidate is invented beyond the list.

- **A candidate blocked only by the AI's own missing building** is not proposed; its value is reported
  to `ai-trade-buildings` as the payoff of building it (one valuation, reused), so the AI builds an
  Embassy because a treaty is worth it, not by a separate heuristic.
- **Proposal cooldown.** After a declined proposal, the AI does not re-propose that kind to that
  counterparty for `trade.diplomacy.reproposeCooldownTurns` turns (a structural pacing limit, so neither
  side's log fills with the same refused offer).

### 4. Filing

- One command per pair per turn, id `ai-{turn}-d-{counterpartyId}` (bloc: `ai-{turn}-b-{blocId}`) —
  unique by construction, which makes the one-per-pair rule structural, not a check.
- Every command's reason carries the verdict: *"propose market to rival-2: +310 over 3 turns (tariffs
  in, passage risk 40)"*.
- All diplomacy kinds are in `AiPolicyOrderKinds` and count against the policy-order bound (`trade.policyOrdersBase` + `trade.policyOrdersPerOwnSector` × own sectors, `ai-spend-limit` §1)
  (`ai-spend-limit`); per-turn treaty legs the AI gives pass `SpendLimit.Trim`.

### 5. Acceptance is the one rule

The AI accepts exactly when `deal-valuation`'s `Accepts` is true. Personality does **not** move the
acceptance threshold — only `acceptMilli[band]` does — so two AIs in the same band and the same belief
accept the same deals. Personality changes what an AI **proposes** and how readily it goes to war.
(This narrows the map's module-6 wording, which allowed a "personality veto"; a veto would be a second
acceptance rule.)

## Tunables

| Key | File | Unit |
|---|---|---|
| `trade.diplomacy.warThresholdMilli`, `trade.diplomacy.peaceThresholdMilli` | `gk-core/data/tuning/ai.v3.json` (next AI version) | ‰ scorer output |
| `trade.diplomacy.warWeights`, `trade.diplomacy.peaceWeights` | same | consideration weights |
| `trade.diplomacy.reproposeCooldownTurns` | same | turns — structural pacing |
| `trade.valuation.treatyBrokenWeightMilli` | same | ‰ |

Read, never duplicated: `acceptMilli.{band}`, `treaty.minimumTermTurns`, tariff bands
(`data/tuning/diplomacy.v1.json` (new), `exchange`); personality rows (`data/tuning/trade.v1.json` (new),
`counterparties`).

## Acceptance (contract)

1. **One per pair.** At most one diplomacy command per counterparty (and one bloc command) per faction
   per turn, over a 20-turn run.
2. **The one rule.** An AI never accepts a deal `Accepts` refuses, and never declines one it accepts
   except with code `Band` or an at-war reason — asserted over generated offers.
3. **Replay-invariant (inherited).** Replaying a stored log with a different treaty policy registered
   leaves every hash unchanged (the `Replaying_a_stored_log_ignores_the_policy_that_produced_it` shape).
4. **Blind.** No diplomacy command names a faction the AI has not met (§2 rule).
5. **Legacy.** On a world without the diplomacy capability, the policy files byte-identically to today.
6. **Admissible.** Every filed command passes admission (the fill throws otherwise), over the 20-turn run.
7. **No hopeless war.** No `war-declare` is filed when any war consideration scores zero.
8. **Exploit guard — no break farming.** A player who signs and breaks treaties with an AI cannot
   extract more value than the binding horizon: over a scripted sign-then-break loop, the AI's value
   given never exceeds what `deal-valuation` counted when it accepted — and a short deal never gives the
   AI's side in full (`exchange` `settlement-payment` §7's one fulfilment ratio, audit 2026-09-20).
9. **Exploit guard — no offer spam from the AI.** A declined kind is not re-proposed to the same
   counterparty inside the cooldown.
10. **Same personality, same moves.** Two AIs with the same personality row in mirrored states file
    mirrored commands.
11. **Round 4 buildings.** No proposal or acceptance is filed that resolution would refuse for a missing
    Embassy, Consulate or Exchange (asserted over the 20-turn run: zero `*.needs-building:*` refusals of
    AI commands); nothing is ever filed on the `IsLockedWar` pair, while the dominant enemy empire does
    sign with a rival in a scripted fixture (Q4).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/TreatyPolicyTests.cs` (new): 1, 2, 4, 7, 8, 9, 10, 11.
- `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs` (extend): 3, 5, 6 through the real fill.
- A campaign scenario with one rival (the `counterparties` Q2 fixture) run for 20 turns; the existing
  campaign tests (`gk-core/tests/FusionRpg.Core.Tests/World/TwoHearthsCampaignTests.cs`) are **run and reported**,
  never assumed unchanged (`spec-ai-commander.md` §Momentum point 4).
- Run `.\scripts\verify-change.py -Paths <changed paths> -Session <id>` (`core-world-ai-trade`,
  `data-world-ai-fill`); `FrontierRulesPolicy.cs` changes, so the full suite runs once at module end.

## Hard edges

- **`FrontierRulesPolicy` gains a layer.** Its entity orders must stay byte-identical on worlds without
  trade (criterion 5); any campaign test that moves is a defect in this change, not a re-bless.
- **New policy ids enter the hash** only for worlds that use them (rival factions are new content).

## Dependencies

| Consumes | From |
|---|---|
| `Counter`, `RefusalTerms` | `counter-offer-articles` |
| `DealValue`, `Accepts` | `deal-valuation` |
| `Trim`, `AiPolicyOrderKinds` | `ai-spend-limit` |
| treaty, embargo, bloc commands; pending offers via the view | `exchange` `treaty-lifecycle` (T-A5, T-A6) |
| war/peace commands, stance | `counterparties` `diplomatic-stance` |
| diplomacy facts (public), band snapshot, personality rows | `counterparties` `diplomacy-facts`, `relation-facts`, `empire-roster` (T-A7) |

| Exposes | To |
|---|---|
| the composed policy and its personality ids | `counterparties` `empire-roster` (catalogue), `clan-behaviour` |

## Boundaries

- **Always:** one command per pair; the one acceptance rule; reasons with numbers; gate on capability.
- **Ask first:** changing the ladder's entity rules from this layer; a personality that alters acceptance.
- **Never:** a second policy per faction; a faction-kind branch; a proposal outside the candidate list.

## Design-gate checklist

```
[x] Subsystems: world map AI (policy composition, hash of PolicyId), diplomacy (exchange,
    counterparties — consumed), relation ladder, tunables.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list. NOT read: npc-story-events-ideal §6.4 in full
    (relation mechanics are counterparties'; only their output band is read here).
[x] decisions.md: no lock covers AI diplomacy; spec-ai-commander's non-goal is amended by ask T-A1.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: FactionPolicies, WorldValidation policy check, PolicyId hash row,
    IFactionPolicy contract, ZoneOfControl, replay tests.
[x] Surrounding sections read: spec-ai-commander §Corrections 5, §Who gets which policy, §Non-goals.
[x] No constraint claimed without a run: campaign tests are to be run and reported.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the "personality veto" narrowing is stated here and in the map.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Orderings: counterparties walked in ordinal order; one command each, so no cross-pair ordering.
[x] No actor magnitude.
[x] No SOLID-violating path: one policy per faction, one acceptance rule, one valuation.
[ ] Registry rows (one-command-per-pair, no faction-kind branch) owed with the change.
[x] Round 4 reconciliation (2026-09-19): Q4 (player-only lock via IsLockedWar); candidates filtered by
    both parties' buildings; blocked candidates feed ai-trade-buildings; own strength from the power
    roll-up when it lands.
[x] Round 5 (2026-09-20): C2 (offerer's Embassy only — unchanged, now the owner's decision), C3
    (embargo-set gated on the AI's Consulate), X7 (roll-up owner is legion-build legion-power).
```

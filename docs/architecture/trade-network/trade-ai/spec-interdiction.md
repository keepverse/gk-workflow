# Spec: `interdiction`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `interdiction`, row 8 of the approved
[trade-ai map](../trade-ai-map.md) (wave 4). **Owner decision Q1 (2026-09-19):** the rule sits **after
`Recover` and before `Explore`**, limited to a tunable share of the empire's legions. Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §14b (*"interdiction adapts to your busiest flows
(enemy counter-development)"*, *"interdiction presses the leader hardest"*);
`docs/guide/the-loops.md:95` (enemy counter-development); the anti-Nemesis rules,
[npc-story-events-ideal.md](../../npc-story-events-ideal.md) §6.12.

## Objective

Trade makes geography matter only if someone contests it. This rule sends AI legions to sit on the
lanes carrying the most value for their enemies — the lanes the AI **believes** are busiest — and leans
hardest on whichever enemy is moving the most goods. A hostile legion on a lane raises that lane's loss
through `logistics-flow` `lane-loss` (`hostilePresenceMilli`) and meets caravans through the ordinary
contact path. Nothing is spawned; no raider exists that is not a legion someone raised.

It reads **aggregates at faction level** — flows the AI saw on lanes — and never an individual
encounter, so it is counter-development, not a nemesis: the war answers what your whole economy is
doing, not who beat whom last time.

Success looks like: an empire running a rich route through open ground finds it contested within a few
turns; the leading empire draws more pressure than a trailing one; an empire that does not trade sees
no change at all in how the AI plays.

## Scope and non-goals

**In:** the rule's place in the ladder, the target score, the per-turn share, the posting behaviour,
the anti-Nemesis inputs rule.

**Not here:** loss arithmetic (`logistics-flow` `lane-loss`); battles (`fleet` `interception`, the
kind-agnostic contact path); what the legion carries away (`fleet` `goods-cargo-fate`); the faction-level
doctrine reading (`npc-story-events` `counter-doctrine`, a separate input the map may later combine).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The ladder: Defend → Abandon → Finish → Take → Sever → Recover → Explore → Expand → Hold, first match wins, one order per legion | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:62-70` |
| Reach per legion, computed once per legion in the walk | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:59`; `gk-core/src/FusionRpg.Core/World/Ai/ReachMap.cs:25` |
| Route with a supply-survival check (`Sever`'s precedent) | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:300-303`, `:474` |
| Staleness decay and hostility read in the threat map | `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:47`, `:71` |
| `Explore` files a stance or a move, never both | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:352-369` |
| Ladder weights come from `ai.v{n}.json`; a missing key is a load rejection | `gk-core/src/FusionRpg.Core/World/Ai/WorldAiTuning.cs:57-67`; `gk-core/data/tuning/ai.v2.json` |
| `Sever` reaches `ReconnectionCost` (O(V⁴)) through `SeveranceScore` | `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:23-32` |

### Wiring gap

None.

### Real gap

The rule, its pre-pass and its target score.

## Design

### 1. Place in the ladder (owner decision Q1)

```text
Defend ?? Abandon ?? Finish ?? Take ?? Sever ?? Recover ?? Interdict ?? Explore ?? Expand ?? Hold
```

An empire defends, cuts its losses, finishes what it started and heals first; then hunts flows; then
scouts and expands. `Interdict` is a new static rule in `FrontierRulesPolicy` beside the others, not a
second policy.

### 2. Targets — a pre-pass before the entity walk

```text
flows      = view.BelievedFlows() where IsHostile(flow.Owner, me)        // trade-intel; the one hostility rule
confidence = Score([Freshness: Inverse(age × threatMap.staleDecayPerTurn)])   // same staleness as fear
share(o)   = Σ believed flow of o × 1000 / Σ believed flow of all hostile owners  // ‰; 0 when the total is 0
score(f)   = f.Offensive × confidence / 1000
             × (1000 + interdict.leaderWeightMilli × share(f.Owner) / 1000) / 1000
targets    = flows where score ≥ interdict.minFlowValue, ordered by score desc, then lane id, then owner id
```

- `f.Offensive` is the exact value or the band midpoint (`trade-intel`), the same reading the threat
  map uses for "what should I expect".
- **Division guard (audit 2026-09-20).** `share` divides by the total believed hostile flow; when every
  remembered flow has value 0 (a band whose midpoint is 0) the total is 0 and `share` is defined as 0 —
  no divide by zero, and no leader term. The `× 1000` is applied before the divide (per-mille, divide
  last); both sums are `long`, `checked`.
- **The leader term** raises the score of whoever the AI believes moves the most goods — the ideal's
  catch-up. It reads shares of **believed flow**, so it favours no faction kind: the player is pressed
  hardest only when the player is the one the AI sees trading most (principle 10).
- No `ReconnectionCost`, no `SeveranceScore`: the score is linear in believed flows. Code lives in
  `src/FusionRpg.Core/World/Ai/Trade/InterdictionTargets.cs`, under the routing guard's widened path
  (T-A4).

### 3. Assignment and the share

```text
budget = floor(interdict.shareMilli × |own non-routed legions| / 1000)     // structural share
for target in targets:                                                  // at most one legion per target in v1
    pick the unassigned own legion with the fewest reach turns to either end of target.lane, ties by entity id
    stop when budget legions are assigned
```

In the walk, `Interdict(entity)` fires only for an assigned legion. A legion that fired a higher rule
never reaches `Interdict`, and its assignment simply lapses — the higher rule wins and the budget is
not spent. The share bounds **how many interdict**, never how strong anything is.

**Round 4 P (force estimates).** Among legions with equal reach, the pick prefers the one whose
rolled-up power (the power roll-up over its own stacks — the AI reading its **own** legions, which P
names as a use) best matches the target lane's believed hostile presence, so an AI does not post its
strongest army on a trickle. It is a **read of Hub output for choosing**, never a strength term in a
contest, so it needs no `ssot-power-scale.md` §10 row. Until the roll-up lands, the tie-break stays
entity id (today's behaviour).

### 4. What the rule files

- Not yet at the post (the lane end nearer by reach): `move` along `Route(...)`, only if
  `SurvivesTheRoute` holds (`FrontierRulesPolicy.cs:474`) — the `Sever` shape.
- At the post: `stand-fast` with reason *"interdicting l-ash-verdant: rival-2's flow, band 4, seen 2
  turns ago"*. Standing on a lane end is what `lane-loss` reads; no new stance is needed.
- The existing momentum hysteresis applies to moves as it does for `Expand`
  (`FrontierRulesPolicy.cs:415-432`), so a legion does not ping-pong between two near-equal lanes.

### 5. The anti-Nemesis rule (inputs)

Every input is a **faction-level aggregate from belief**: remembered flows, their owners, their ages.
No input is keyed by a battle, an encounter, a named character or a player-side unit
(`npc-story-events-ideal.md` §6.12 rules 1 and 3). A source-scan guard fails if any file under
`World/Ai/Trade/Interdiction*` references a battle report, the story ledger, the character registry, or
an entity id of another faction. The registry rows are shared with `npc-story-events`
`counter-doctrine` (ask T-A3).

### 6. A world with no trade is untouched

With no believed flows, `targets` is empty, `Interdict` returns null for every legion, and the ladder
behaves exactly as today. The dominant enemy empire keeps policy id `frontier-rules`, so no template
hash moves from an id change.

## Tunables

`gk-core/data/tuning/ai.v3.json` (next version of the AI domain; published through
`python gk-core/tools/tuning/publish.py ai …`; the loader and `gk-core/src/FusionRpg.Server/Program.cs:234` switch in the
same change):

| Key | Unit | Nature |
|---|---|---|
| `interdict.shareMilli` | ‰ of own non-routed legions | **structural share** (owner Q1), commented as such |
| `interdict.leaderWeightMilli` | ‰ | how much harder the leader is pressed |
| `interdict.minFlowValue` | value-index units per turn | a flow worth a legion |

Reused: `threatMap.staleDecayPerTurn`, `frontierRules.momentumMarginMilli` (`gk-core/data/tuning/ai.v2.json`).

## Acceptance (contract)

1. **Order.** In a scenario where `Recover` and `Interdict` would both fire, `Recover` wins; where
   `Interdict` and `Explore` would both fire, `Interdict` wins.
2. **Blind.** Only lanes with a remembered flow are targeted; a flow the faction never saw is never a
   target.
3. **Share.** At most `floor(interdict.shareMilli × legions / 1000)` legions file an `Interdict` order in
   any turn, over a 20-turn run.
4. **Ranking.** Given two believed flows, the higher-scored one is assigned first; given two hostile
   owners with equal flows, the one with the larger believed share is pressed first.
5. **Staleness.** A flow seen longer ago than the threat map's horizon scores zero and is never targeted.
6. **One order per legion** holds (the existing 20-turn invariant, `FrontierRulesTests.cs:115`).
7. **Anti-Nemesis.** The source-scan guard (§5) passes; no input is keyed by an encounter or character.
8. **No-trade identity.** On a world with no flows, the policy's orders are byte-identical to the
   pre-module ladder for the same view (asserted by running both over the existing AI scenarios).
9. **No spawn.** Interdiction files only `move` and `stand-fast`; no command kind is added.
10. **No hopeless march.** No `move` is filed along a route `SurvivesTheRoute` rejects.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/InterdictionRuleTests.cs` (new): 1–5, 9, 10 — one scenario that
  fires and one that does not, the `spec-ai-commander.md` §Testing shape.
- `gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs` (extend): 6, 8.
- `gk-core/tests/FusionRpg.Guard.Tests/` (new scan, shared rows): 7.
- `gk-core/tests/FusionRpg.Core.Tests/World/TwoHearthsCampaignTests.cs` and the AI acceptance scenario are
  **run and reported**; criterion 8 predicts no movement on worlds without trade, and a movement is a
  defect in this change, never a re-bless.
- Run `.\scripts\verify-change.py -Paths <changed paths> -Session <id>`; `FrontierRulesPolicy.cs`
  changes, so the full suite once at module end.

## Hard edges

- **Rule-order change** — owner-approved (Q1, 2026-09-19), which is what `spec-ai-commander.md`
  §Boundaries asked for (line 364). `spec-ai-commander.md`'s boundary text is amended by ask T-A1, not by
  this spec.
- **AI tuning version.** `ai-spend-limit` **creates** the AI domain's next version and carries the loader
  switch (global audit M8, round 6: one creator per versioned file). This module lands in wave 4, long after,
  so it publishes **`v{n+1}`** through `gk-core/tools/tuning/publish.py` and claims no switch.
- **Wave and ruleset bump (round 6 C1):** trade-ai **wave 4**; the policy runs outside `Step`, grants no
  capability flag and takes no bump.

## Dependencies

| Consumes | From |
|---|---|
| `BelievedFlows` | `trade-intel` |
| the ladder, `Route`, `SurvivesTheRoute`, momentum | `world-map-program` `ai-commander` (built) |
| hostility (stance-aware once built) | `counterparties` `diplomatic-stance` via `ZoneOfControl.IsHostile` |
| `hostilePresenceMilli` loss on a lane | `logistics-flow` `lane-loss` |
| shared anti-Nemesis rows | `npc-story-events` `counter-doctrine` (T-A3) |

| Exposes | To |
|---|---|
| the pressure caravans meet | `fleet` `escort-link` (why escorts matter), `trade-surface` (loss causes) |

## Boundaries

- **Always:** aggregates only; the share bound; survival-checked marches; a reason naming the lane,
  owner, band and age.
- **Ask first:** more than one legion per target; any input from battle history.
- **Never:** a spawned raider; a per-character memory; a strength bonus for the interdictor.

## Design-gate checklist

```
[x] Subsystems: world map AI (ladder — owner-reserved order, decided Q1), logistics (lane loss —
    consumed), narrative (anti-Nemesis rules), tunables.
[~] Session boundary: docs-only under trade-network-idea-20260919; check exits 1 on crossings already
    recorded; this file is new.
[~] Read this session: as spec-trade-intel.md's list, plus npc-story-events-ideal §6.12 in full and
    npc-story-events-map module 24.
[x] decisions.md: no lock covers interdiction; the rule order is the owner's (Q1, recorded in the map).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: ladder order, reach, Sever route + survival, Explore stance-or-move, momentum,
    ThreatMap hostility, SeveranceScore's O(V⁴) call.
[x] Surrounding sections read: spec-ai-commander §The decision layer, §Momentum, §Boundaries.
[x] No constraint claimed without a run: campaign tests are to be run and reported.
[x] No §2 invariant contradicted; no magnitude cap (the share is a structural count, commented).
[x] Corrections propagated: Q1 recorded in the map (status, module 8, Owner decisions).
[x] No population pinned.
[x] No event-refreshed cache.
[x] Orderings: assignment is by score then reach then id — deterministic and independent of filing order.
[x] No actor magnitude produced: interdictors are ordinary legions; no strength term is added. The
    power roll-up is only read (round 4 P) to choose among equal-reach legions — Hub output, one read.
[x] Round 4 reconciliation (2026-09-19): force estimate for own legions from the roll-up (ask T-A10).
[x] No SOLID-violating path: a rule in the one ladder; one hostility rule; one staleness rule.
[ ] Registry rows (anti-Nemesis scan) shared with counter-doctrine (T-A3), owed with the change.
```

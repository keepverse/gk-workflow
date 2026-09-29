# Spec: `trade-fact-kinds`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 1, wave 1). Every `file:line` below was opened this session. Docs only.

## Objective

The closed, reviewed list of **trade story facts** — the things trade does that are worth a story — each
with its scope, subject, attributes, dedupe key, the one durable source record it projects, and its
audience. Every later trade-stories module (hosts, leaves, pacing, quests, failure branches) reads this
list; nothing else invents a trade fact.

## Locked anchors

- **Facts are projections, not a second truth** (map §4 item 2). Each fact is keyed by its source record's
  durable id, so it can be rebuilt and never disagrees with the producer.
- **One ledger, one key grammar.** Facts live in npc-story-events' story ledger, whose dedupe key is
  `{kind}|{scope}|{world_id}|{subject_kind}:{subject_id}|{source_ref}` with `player_id` = the save
  ([spec-story-ledger.md](../../npc-story-events/spec-story-ledger.md) §2–§3). The ideal's trade key
  `(save_id, empire_id, world_id, turn, factKind, sector|lane, good)` maps onto it (Design 3); no second
  grammar is minted.
- **The story fact vocabulary is closed** (`StoryFactKind`, 22 members,
  [spec-narrative-vocabulary.md](../../npc-story-events/spec-narrative-vocabulary.md) §3). Each trade kind is a
  reviewed addition there.
- **No duplicate facts.** A trade kind never re-records a fact another program already writes under
  another name (Design 2).
- **World scope — the fact stays with its world; the world does not die.** Every trade fact is `world`
  scoped, because trade happens on a map and a fact about a hub, lane or sector means nothing off it.
  **Wording corrected (2026-09-20, round 6 S2 and `world-continuity`'s doc amendment):** *"trade dies with the
  map"* is the retired phrasing — worlds do **not** end; a world becomes `developing`, `hibernating`, `idle` or
  `fallen` and stays revisitable, and trade goods cross to another world **only over a `rift-trade` route**
  (never on an advance). So: a trade fact is world-scoped and stays with its world for as long as that world
  exists, which is for the rest of the save. Nothing here changes — the scope was right, the reason was
  stale.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Report lines with sector and audience (the fog basis for audience) | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |
| Detail-prefix report lines as the current event idiom | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:113` (`supply.besieged:`) |
| Report kinds, closed at five today | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` |

### Real gap

No trade code in `gk-core/src/FusionRpg.Core/World`; no story ledger (npc `story-ledger` specced, unbuilt); no
producer records (`sector-yield`, `logistics-flow`, `exchange`, `counterparties`, `fleet` unbuilt).

## Design

### 1. The trade kinds (declaration)

| Wire id | Source record (owner) | `subject_kind:subject_id` | `attrs` (closed) | Audience |
|---|---|---|---|---|
| `trade.warehouse.full` | production-halt line (`sector-yield` `production-halt`) | `sector:{id}` | `{goodId}` | the sector's owner |
| `trade.delivery.wasted` | `logistics.overflow` (`logistics-flow` `logistics-facts`) | `sector:{id}` | `{goodId}` | destination owner |
| `trade.lane.cut-stranded` | `logistics.strand` / `lane.cut` (`logistics-facts`) | `lane:{id}` | `{goodId?}` | the flow's owner |
| `trade.caravan.lost` | `caravan.lost` fact (`fleet` `interception`, [spec-interception.md](../fleet/spec-interception.md) `FleetFacts`); the cache id from `goods-cargo-fate` | `legion:{id}` | `{battleId, lastPlaceId, cacheId}` | the caravan's owner |
| `trade.caravan.intercepted` | `caravan.intercepted` fact (same) | `legion:{id}` | `{battleId, outcome}` | both sides |
| `trade.price.spike` | a hub price crossing the upper band edge (`exchange` `price-curve`) | `sector:{hubSectorId}` | `{goodId}` | factions whose `LevelAt` that hub is `market` or better (round 4: tier and treaty/band) |
| `trade.price.crash` | lower band edge, same source | `sector:{hubSectorId}` | `{goodId}` | same |
| `trade.treaty.signed` | `treaty.signed` diplomacy fact (`counterparties` `diplomacy-facts`) | `faction:{counterpartyId}` | `{treatyKindId}` | both parties |
| `trade.embargo.set` | `embargo.set` diplomacy fact (same) | `faction:{counterpartyId}` | `{}` | both parties |
| `trade.hub.lost` | claim resolution of a sector whose `trade` feature tier is ≥ 1 (`trade-foundation` `sector-features`) | `sector:{id}` | `{featureId, tier}` | the loser |
| `trade.depot.lost` | same, for the `caravans` feature (Caravan Yard / Convoy Depot, round 4) | `sector:{id}` | `{featureId, tier}` | the loser |
| `trade.demand.shock` | a shock starting (`seasonal-demand-shocks`) | `none:` | `{goodClassId, direction, untilTurn}` | every faction (seasons are public) |

**Twelve kinds**, pinned as a declaration: each names exactly one source record and one owner; a
thirteenth is a reviewed change to this spec and to `StoryFactKind`.

### 2. What is **not** a trade kind (read elsewhere, never duplicated)

| Story | Read as | Owner |
|---|---|---|
| A treaty broken, war declared, a treaty imposed, a clan conquered, a trade fulfilled | `treaty.broken`, `war.declared`, `treaty.imposed`, `clan.conquered`, `trade.fulfilled` | `counterparties` `relation-facts` |
| A sector lost | `sector.lost` | npc-story-events `failure-branches` |
| A clan request opened | npc's petition facts and leaf | npc-story-events `petition-host` |
| The relation band | derived, never a fact | npc-story-events `relation-ledger` |

`trade.hub.lost` and `sector.lost` come from one claim, but they are different facts: the subject is the
same sector and the **kind** differs (a trade-infrastructure loss vs a territorial loss), so their dedupe
keys differ and a storylet can react to either. The map listed `trade.treaty.broken` and
`trade.clan-request.opened`; both are dropped here because their owners already record them (correction
propagated to the map).

### 3. Keys

`source_ref = turn:{worldId}:{turn}:{entryIndex}` for report-derived kinds (the story ledger's own row for a
world turn entry); `diplomacy:{worldId}:{turn}:{factIndex}` for the two diplomacy-derived kinds;
`shock:{worldId}:{seasonOrdinal}:{goodClassId}:{climateId}` for a demand shock — the **absolute** season
ordinal and the climate (audit 2026-09-20: keyed on the cyclic season index and without the climate, a
later year's shock, or a second climate's shock of the same class, collided with the first and was
deduped away; `seasonal-demand-shocks` §1). The good travels in `attrs`, not the key,
except where two goods in one report entry would collide — the providers write one entry per
(sector|lane, good), so they do not. The save and empire are the ledger's `player_id` (one save, one
empire per world, per `save-identity`).

### 4. Subject kinds

`lane` and `legion` are not in the ledger's closed `subject_kind` list today (spec-story-ledger §2). Both
are filed as reviewed additions on npc-story-events `story-ledger`.

## Contract exposed

| Member | Consumer |
|---|---|
| The twelve wire ids, their subjects, attributes and source refs | `trade-fact-source`, `trade-predicates` (story-fact recency), `trade-hosts`, `trade-quests`, `trade-failure-branches`, `trade-trigger-reachability`, `trade-storylet-supply` |

## Acceptance (contract level)

1. Every kind names exactly one source record kind and one owner.
2. Every kind has a `source_ref` format and a closed `attrs` set; a writer with an unlisted attribute is
   refused.
3. The list is pinned (twelve, with the reason above).
4. **No duplicates:** a join check against `StoryFactKind` and `relation-facts`' emitted kinds finds no
   trade kind whose (source record kind, subject kind, qualifying condition) equals another kind's. The
   one declared overlap — `trade.hub.lost` / `trade.depot.lost` beside `sector.lost`, same claim and
   subject, qualified by the lost structure's role — is listed in the test with Design 2's reason.

## Test plan and verification boundary

Core: a vocabulary test over the kind table (pins, attribute sets, the no-duplicate join) —
`core-fallback` (`FusionRpg.Core.Tests`, Narrative / World/Trade). Web: none.

## Hard edges

- Every kind is a reviewed widening of npc-story-events' `StoryFactKind`; blocked until `narrative-vocabulary`
  and `story-ledger` are built.
- A kind whose producer has not landed is declared but has no writer; `trade-trigger-reachability` marks
  it pending, never green.

## Dependencies

npc-story-events `narrative-vocabulary` (`StoryFactKind`), `story-ledger` (keys, subject kinds); producers
named in the table; `seasonal-demand-shocks`.

## Boundaries

- **Always:** world scope; one source per kind; keys through the ledger grammar.
- **Ask first:** a save-scoped trade fact.
- **Never:** a relation band as a fact; a kind that duplicates another program's.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: story ledger (npc), world report, trade producers (read).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: npc-story-events-ideal §6.2/§6.7/§6.8, spec-story-ledger §1–§3, spec-narrative-vocabulary §2–§3,
    counterparties-map modules 3 and 7, trade-stories-map.
[x] decisions.md: no lock on story facts (npc NS rows are drafts).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: TurnReportKinds, TurnReportEntry, supply prefix idiom.
[x] Surrounding sections read (ledger append-only and attrs rules).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: two dropped kinds recorded in the map.
[x] No population pinned: twelve kinds is a declaration.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one ledger, one key grammar, no duplicate kinds.
[x] Registry row: the no-duplicate join is the guard; row added when built.
[x] Round 4 reconciliation (2026-09-19): hub and depot loss keyed by sector feature and tier (was
    role / row id); price-fact audience reads LevelAt. Still twelve kinds.
```

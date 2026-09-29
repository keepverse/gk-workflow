# Spec: `trade-quests`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 8, wave 4). Every `file:line` below was opened this session. Docs only.

## Objective

Trade as quests, through npc-story-events' one quest engine with the committed world turn report as a
fact source: **escort** a route, **deliver** goods by a turn, **recover** a lost caravan's cache, pay a
**ransom** for it. Four objective templates, added to the closed template registry as a reviewed change.

## Locked anchors

- **One quest engine, fact sources per place** (npc-story-events-ideal §6.5;
  [spec-quest-sources.md](../../npc-story-events/spec-quest-sources.md) §3): a quest anchor is a template
  instance, never a new mechanism (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:7-23`). Today the only
  fact source is a `DelveReport` (`gk-core/src/FusionRpg.Core/Delve/Quests/QuestProgress.cs:30`); `quest-sources`
  adds `world-turn`.
- **Closed template registry** `data/seed/narrative/_registry/quest-objectives.v1.json` (new), rows
  `{ templateId: { targetKind, sources: [..] } }` (spec-quest-sources §3). Four rows are requested here.
- **Standalone rule:** a template's sources must include a standalone source; `world-turn` is one
  (spec-quest-sources §3.1).
- **Every faucet names its sink; no souls out of trade** (trade-network umbrella invariant 3). A trade
  quest reward comes from its host's existing budget through existing grant paths, deduped on the quest's
  durable id; a ransom's souls are a sink.
- **One price.** Any goods or souls a quest exchanges settle through `exchange` at the value index; a quest
  names no price (map §3 principle 6).
- **World clock only** for expiry; abandoning is free.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Quest anchor as a template instance | `QuestRow.cs:7-23` |
| Quest evaluation with a `need`, over one report | `QuestProgress.cs:30` |
| The verb that claims a fallen cache | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:119` (`claim-cache`) |
| A dead legion's cargo becomes a revisit-lootable cache | [spec-cargo-fate.md](../../scoped-inventory-hierarchy/spec-cargo-fate.md) §Design 1 |

### Real gap

No trade templates; no world-turn fact source (npc `quest-sources`); no escort stance (`legion-build`
`escort-stance`), caravans (`fleet`) or settlement (`exchange`).

## Design

### 1. The templates (rows requested on the registry)

| Template | Target kind | Counts / completes when | Sources |
|---|---|---|---|
| `trade-escort` | a trade route (legion on a trade standing order) | N consecutive world turns in which that route delivered with no interception loss while an escort-stance legion accompanied it | `world-turn` |
| `trade-deliver` | a good | the faction banks ≥ `need` of that good, summed over banking facts from offer turn to expiry | `world-turn` |
| `trade-recover` | a goods cache (from a `trade.caravan.lost` fact's `cacheId`) | a `goods-cache.claimed` fact names the faction as claimant before the cache fades — a goods cache is claimed **by presence** in the Logistics phase (`fleet` `goods-cargo-fate` §7), not by `claim-cache`, which is the Data-side **item** cache verb (fleet ask A10; corrected in the round-4 reconciliation) | `world-turn` |
| `trade-ransom` | a cache claimed by a counterparty | the faction answers the counterparty's `offer:{stock}` choice and the settlement completes through `exchange` | `world-turn`, `story` |

Ids are prefixed `trade-` so they cannot collide with the registry's existing template ids.

### 2. Need and magnitudes

`trade-escort` counts turns from the quest's `CountBand` (the registry's `lone · few · several · many`).
`trade-deliver`'s `need` is set **at offer**, from the count band and the good's per-turn yield scale at the
host's `Θ_content`, read through `sector-yield`'s scaled goods read (PS-5 value-normalised) — the one power
ladder, no private `f(level)`. The need is stored on the `quest.offered` fact (spec-quest-sources records
`need`), so evaluation never recomputes it.

### 3. Ransom, precisely

When a counterparty claims a cache that a player caravan left (`fleet` `goods-cargo-fate`), a priority
storylet on that counterparty's hub (`world.trade-hub`) may offer the goods back. The choice is
`offer:{stock}`; its cost is priced by `exchange` at the value index for the goods returned. **Corrected in
the round-4 reconciliation:** an `order-set` walks the price curve, so it cannot settle "at the value
index"; the ransom is a **one-off deal** (`exchange` `treaty-vocabulary` §6, no treaty kind) whose legs
settle in `settlement-payment` §7 at the value index: the goods leave the counterparty's stock once and
land once in the player's **consignment at that hub** (then travel home by `logistics-flow`, like any
purchase); any souls paid are sunk (AI factions hold no soul balance). The deal needs the player's
`LevelAt ≥ market` at that hub (round 4: a Trading Post for a clan hub), otherwise the choice shows
locked with the missing building. How a storylet outcome becomes the counterparty's `offer.made` is an
ask on npc-story-events `outcome-routing` (an outcome kind that files a one-off deal offer on the host
faction's behalf) — reported in the map's §12.

### 4. Offer and reward

Quests are offered by storylet outcomes (`quest.offer`, npc `outcome-routing`) or by a clan petition
(npc `petition-host`). Rewards: the host's budget through existing grant paths, dedupe key
`quest.completed:{questId}` (spec-quest-sources), never souls from trade.

## Contract exposed

Four template rows; a trade objective evaluator over committed world facts
(`src/FusionRpg.Core/World/Trade/Stories/TradeQuestObjectives.cs`, new) registered with `quest-sources`.

## Acceptance (contract level)

1. **No soul faucet:** an invariant test over every trade template's reward path finds no path that
   increases souls through trade; a ransom's souls leave the player and enter no wallet.
2. **Ransom never duplicates goods:** per good, counterparty stock decreases and the player's
   **consignment at that hub** increases by the same amount, once (reconciliation), and a replayed answer
   settles nothing new. *(Audit 2026-09-20: this said "player warehouse stock", but §3 lands ransomed
   goods in the consignment, from where they travel home.)* A ransom the counterparty cannot fully
   deliver settles at the deal's one fulfilment ratio (`exchange` `settlement-payment` §7), so the player
   never pays in full for goods it did not get.
3. **Mode-agnostic:** no template's sources include `pvz`; the registry loader's lawn-only refusal passes.
4. **World clock:** expiry and escort counts are in world turns; no wall-clock read.
5. **Determinism:** the evaluator is pure over committed facts; the same facts give the same verdict in any
   evaluation order.
6. **One price:** the ransom cost equals `exchange`'s value-index price for the returned goods (fixture),
   settled through `settlement-payment` §7 (a deal leg), never an `order-set` walk.
7. **Recover by presence:** `trade-recover` completes on a `goods-cache.claimed` fact naming the faction and
   on nothing else (a `claim-cache` of an item cache never completes it).

## Test plan and verification boundary

Core evaluator and invariant tests — `core-fallback`; ransom settlement reconciliation — `exchange`'s
suite plus a trade fixture here (`core-fallback`).

## Hard edges

- `trade-escort` waits for `legion-build` `escort-stance` and `fleet` `escort-link`; the other three do not
  wait for it (map §8 default).
- Registry rows are a reviewed change on npc `quest-sources`' vocabulary.

## Dependencies

`trade-fact-source`, `trade-fact-kinds`; npc-story-events `quest-sources`, `outcome-routing`,
`petition-host`; `fleet` (`trade-route-order`, `interception`, `goods-cargo-fate`); `legion-build`
`escort-stance`; `exchange` (`settlement-payment`, `goods-valuation`); scoped-inventory `cargo-fate`;
`sector-yield` scaled goods read.

## Boundaries

- **Always:** template instances; grants from the host budget; settlement through `exchange`.
- **Ask first:** a trade template with a failure condition (none of the four has one).
- **Never:** souls paid out of trade; a quest-local price; a lawn-only objective.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: quest engine (npc), story ledger, exchange settlement, fleet, economy invariants.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: npc-story-events-ideal §6.5/§6.9, spec-quest-sources §3, trade-network-map §5 (invariants 3, 12).
    NOT read in full: spec-cargo-fate.md beyond §Design 1; empire-economy-ssot.md.
[x] decisions.md: Empire resource registry (:108).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: QuestRow, QuestProgress.Evaluate, claim-cache kind.
[x] Surrounding sections read (quest-sources standalone rule).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (one power ladder for need; souls a sink).
[x] Corrections propagated: template ids prefixed trade- (map named them bare); noted in the map.
[x] No population pinned: four templates are a declaration.
[x] No cache.
[x] Ordering: evaluation stated order-independent.
[x] No actor magnitude.
[x] No parallel path: one quest engine, one price, one ledger.
[x] Registry row: the no-soul-faucet invariant test is the guard; row added when built.
[x] Round 4 reconciliation (2026-09-19): recover reads goods-cache.claimed (fleet A10); ransom is a
    one-off deal leg (settlement-payment §7), gated by LevelAt; outcome-routing ask reported.
```

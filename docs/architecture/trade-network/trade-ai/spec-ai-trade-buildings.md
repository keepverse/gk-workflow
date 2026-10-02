# Spec: `ai-trade-buildings`

**Status: written 2026-09-19 against the code on `features/mega-merge`, during the round-4
reconciliation.** Every `file:line` below was opened in this session. Module id `ai-trade-buildings`,
row 10 of the [trade-ai map](../trade-ai-map.md) (wave 3), added by the round-4 owner decisions
([decisions-round-4.md](../decisions-round-4.md) §B and §P). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.5 (*"The AI uses the same machinery"*),
principle 10 (every empire runs the same economy).

## Objective

Round 4 makes every trade and logistics feature a building: no Trading Post, no clan barter; no
Market, no empire orders; no Embassy, no treaty with an empire; no Counting House, no bank point; no
Caravan Yard, no caravan. An AI empire that never builds would therefore never trade — a handicap the
player does not have, which principle 10 forbids. This module makes an AI empire **build and upgrade
the buildings its own trade plans need**, filed as the same `build` command the player files, scored
by the same valuation the rest of this map uses, and sited with **force estimates from the power
roll-up** (round 4 §P: *"the AI's force estimates where it reads its own legions"*).

Success looks like: an AI empire with a profitable clan barter in reach builds a Trading Post within a
few turns of seeing it; one whose treaty candidate is blocked only by its own missing Embassy builds
one; no AI builds a building no plan needs, builds into a loam deficit, or builds where it cannot hold
the ground.

## Scope and non-goals

**In:** which building kind, tier and sector to build; the payoff each blocked plan contributes; the
affordability and safety considerations; claiming one idle legion to file `build`; the per-turn
build budget.

**Not here:** what a building does (`exchange`, `sector-yield`, `fleet`, `counterparties`); how a slot
records a tier or how an upgrade resolves (`trade-foundation` `sector-features`);
the structure rows and their costs (`empire-seed`); legion equipment workshops and recruit, train or
hire buildings (`legion-build`, and the future unit-system program, round 4 §U); clans, which never
build (`clan-behaviour`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `build` is an entity order: admission requires an entity id | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:108-110` |
| The founding legion must stand in the sector and pays from its own carried loam | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`, `:134` |
| A slot that already holds a structure refuses a second build (no upgrade path yet) | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:71` |
| One order per entity per turn, thrown if broken; every AI order passes admission or throws | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:270-280` |
| The ladder's last rule is `Hold` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:70` |
| Own forces and own loam stock are read live through the view | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:34`, `:52` |

### Wiring gap

None.

### Real gap

**No AI files `build` today** — a search of `gk-core/src/FusionRpg.Core/World/Ai/` for `WorldCommandKinds.Build`
finds nothing. The whole module is new.

## Design

### 1. Candidates — a fixed list, not a search

The closed round-4 ladders this module may build (the ones trade needs): **Trade** (Trading Post →
Market → Exchange → Grand Exchange), **Diplomacy** (Embassy → Consulate), **Banking** (Counting House →
Treasury), **Caravans** (Caravan Yard → Convoy Depot), **Storage** (Storehouse → Warehouse → Granary
Complex). Legion equipment (Workshop ladder) is `legion-build`'s decision, not trade's.

A candidate is `(ladder, tier, sectorId, slotIndex)`: the **next** tier of a ladder the faction holds
in that sector (an upgrade), or tier 1 on a free slot of a kind that ladder's row allows (round 5 B1: a
row may allow several kinds — the Trading Post takes `Wildland` **or** `Market`, and a Market slot scores
its clearing bonus through the blocked plan's value, never a separate heuristic). **Start kit (round 5
A1):** every AI seat begins with a tier-1 Counting House and Storehouse, so those two ladders start at
tier 1 in the seat and their first candidates there are upgrades. Upgrades are
candidates once `trade-foundation` `sector-features` lands (its upgrade arm of `build`); until then only
tier 1 is.

### 2. Payoff — reported by the plans that are blocked, valued once

The payoff of a candidate is the **value the faction's own plans lose for want of it**, in value-index
units over `trade.build.horizonTurns`, reported by the modules that already valued those plans:

| Blocked plan | Reported by | Unblocked by |
|---|---|---|
| An order at a hub where `LevelAt < market` only because of a tier | `ai-bidding` | a Trade tier (own `TradeTier`) |
| A treaty candidate refused `Building` only on the AI's own side | `ai-treaty-policy` | Embassy, Consulate or Exchange |
| A caravan or a bank-point route the plan wants | `ai-logistics` | Caravan Yard, Counting House |
| Foreign caravans refused `depot.no-foreign-yard` at an own hub where foreign buy orders wait (round 5 B3: the **hub owner** needs the yard) | `ai-bidding` (the unfilled orders' value) | Caravan Yard in the hub sector |
| A deliberate embargo the AI wants (round 5 C3) | `ai-treaty-policy` | Consulate |
| Own goods halted at a full warehouse, or stuck with no bank point (own `production-halt` facts through `trade-intel` `OwnFlows`) | this module | Storehouse tier, Counting House |
| Own stock a bank point banks that `ai-bidding` wants held for buyers | `ai-bidding` | Treasury |

No second valuation exists here: each number is `deal-valuation`'s, computed by the module that owns
the plan (principle: one valuation for every caller).

**Every tier read is `sector-features`', and so is the ownership rule (round 6 S1 / X1).** The blocked plans
above name buildings; what the AI *has* is read through `SectorFeatures.TierOf` / `FactionTier` (via
`trade-intel`'s `OwnFeatureTier`, self-knowledge, exact), never through a `StructureKind` and never by
comparing owners here. **S1:** *"a building whose sector and slot have different owners counts for nobody
until one faction owns both"* — so a building on a slot the AI does not own reads tier 0 for it, and the
plan's blocked reason stands; the AI files a `build`, which is the right answer to a building that counts for
nobody. One rule, one place. **Round 6 C2** also matters here: until C2 the feature rows could never load, so
every `TierOf` answered 0 and this module would have filed builds that changed nothing — the neutral
`StructureKind.Feature` is what makes the whole loop real.

### 3. The score — considerations, never a loam price

Loam is never traded or converted (umbrella invariant 2), so a building's loam cost is **not** turned
into value units. The decision is a product of considerations on the built utility scorer
(`gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:37-53`), so a single zero kills it:

```text
BuildScore = Score([
  Payoff:     Linear(payoff ÷ trade.build.payoffScaleValue),                  // §2
  Affordable: Step(founder.CarriedLoam ≥ cost),                               // BuildResolver pays from it
  Upkeep:     Linear(projected own loam net after the building's upkeep ÷ upkeep), // never build into deficit
  Safe:       Smoothstep(own garrison power in reach of the sector ÷ believed hostile threat on it)
])
```

- **Safe — the force estimate (round 4 §P).** The own side is the **power roll-up** over the faction's
  own legions in reach (`legion-build` `legion-power` (module 17): stack = unit Standing × `Count`, legion = Σ fighting stacks, from ActorHub output; ask T-A10 for its view read) — the AI reading
  its own legions, which P names. The hostile side is the defensive `ThreatMap` reading from belief, as
  today. Until the roll-up lands, the own side is today's stack count, the same stand-in `ThreatMap`
  already compares against. The roll-up is **read** to choose, never used as a contest term, so it needs
  no `ssot-power-scale.md` §10 row.
- A candidate is built only when `BuildScore ≥ trade.build.minScoreMilli`. The best candidate by score
  wins; ties by ladder order, then tier, then sector id.

### 4. Filing — one idle legion, one order

After the ladder runs, this layer runs **first** among the trade layers (`ai-treaty-policy` §1). It
claims at most `max(1, floor(idle × trade.build.idleShareMilli / 1000))` legions, where `idle` is the
count of own legions whose ladder result is `Hold` this turn (a structural pacing **share**, so the
empire keeps its army and a large empire is not held to one build a turn — audit 2026-09-20: the flat
`trade.build.maxPerTurn = 1` was a flat rate against holdings that scale, a handicap on the AI the
player does not carry), each one whose ladder result is `Hold` and which **stands in** the chosen sector with
the loam the row costs. Its `stand-fast` is replaced by `build` (`SectorId`, `SlotIndex`, `StructureId`; an upgrade is a `build` naming the structure
already on the slot, `sector-features` §4), id `ai-{turn}-{entityId}` as every entity order is. The legion
still has exactly one order. If no idle legion stands there, the layer files nothing this turn (moving a
legion to build is the ladder's business; a later turn picks the candidate up again when one arrives).

### 5. Capability and blindness

Nothing is filed on a world whose stamp lacks the trade capability (T-A8); a legacy world's AI files
exactly what it files today. Only own sectors are candidates; the payoff reads own plans; hostile threat
is belief.

## Tunables

| Key | File | Unit |
|---|---|---|
| `trade.build.idleShareMilli` | `gk-core/data/tuning/ai.v3.json` (next AI version) | ‰ of idle own legions per turn — **structural** pacing share, commented (replaces `trade.build.maxPerTurn`, audit 2026-09-20) |
| `trade.build.horizonTurns` | same | turns |
| `trade.build.payoffScaleValue` | same | value units |
| `trade.build.minScoreMilli` | same | ‰ scorer output |
| `trade.build.weights` | same | consideration weights |

Policy-only keys stay in the AI domain because `Step` never reads it (TC5).

## Acceptance (contract)

1. **Admissible, always.** Over a 20-turn run every `build` this layer files is admitted and resolves
   (no `build.elsewhere`, `build.occupied`, `build.wrong-slot-kind` or loam drop) — the fill throws
   otherwise (`RpgStore.WorldTurns.cs:274-280`).
2. **One order per entity** holds; at most `max(1, floor(idle × idleShareMilli / 1000))` builds per
   faction per turn, and doubling a fixture empire's idle legions never lowers that bound.
3. **Needs, not speculation.** No building is filed whose payoff is zero (no plan reported it).
4. **Never into deficit.** No build is filed whose upkeep would make the faction's projected loam net
   negative.
5. **Reachability.** In a fixture where an AI empire has a clan hub in reach, an idle legion with loam in
   an own sector with a free trade slot, and a positive barter plan, the AI files a Trading Post within
   one turn — a reachability test, not a count. The same for an Embassy when a treaty candidate is
   blocked only by the AI's own missing Embassy.
6. **Replay-invariant (inherited).** Replaying a stored log with this layer changed leaves every hash
   unchanged.
7. **Legacy.** On a world without the trade capability the policy files byte-identically to today.
8. **Clans never build** (`clan-behaviour` criterion 9); this layer is not in the clan layer list.
9. **Force read, not contest.** A source scan finds no power-roll-up value used outside a consideration
   input in `World/Ai/Trade/` (no strength term is added to any resolution).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ai/Trade/TradeBuildingsTests.cs` (new): 2–5, 8, 9.
- `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs` (extend): 1, 6, 7 through the real fill.
- `.\scripts\verify-change.py -Paths <changed paths> -Session <id>` (`core-world-ai-trade`,
  `data-world-ai-fill`). The composed policy changes `FrontierRulesPolicy`'s layer list, so the full
  suite runs once at module end, not per task.

## Hard edges

- **Same command, same gate.** `build` through `WorldCommandAdmission`; no AI-only build path.
- **No loam price.** Loam enters only as affordability and upkeep considerations, never as value.
- **Upgrades wait for `sector-features`.** Until a slot records its tier, only tier-1 buildings are candidates.

## Dependencies

| Consumes | From |
|---|---|
| tier tables, `TradeTier`, `LevelAt` | `exchange` `treaty-vocabulary` §5, `exchange-hub` §7, `trade-access` §2a |
| blocked-plan payoffs | `ai-bidding`, `ai-treaty-policy`, `ai-logistics` (each reports; one valuation) |
| own feature tiers, own flows | `trade-intel` (`OwnFeatureTier`, `OwnFlows`) |
| own legion power | `legion-build` `legion-power` (module 17) (round 4 §P), through the view (ask T-A10) |
| features, slot tier, upgrade, `FactionTier` | `trade-foundation` `sector-features` |
| building rows, costs, upkeep | `empire-seed` rows; `sector-yield` structure upkeep term |
| capability flags | `trade-foundation` `world-stamp` (T-A8) |

| Exposes | To |
|---|---|
| the build layer in the composed policy | `ai-treaty-policy` §1 (composition order) |

## Boundaries

- **Always:** file only what admission takes; claim idle legions only; report the blocked plan in the
  reason (*"build trading post at s-ash: clan barter +220 over 5 turns blocked"*).
- **Ask first:** building recruit, train or hire buildings (round 4 §U — a future unit program); any
  speculative build with no reported plan.
- **Never:** a loam-to-value conversion; a second valuation; building for a clan; a private building check
  beside `sector-features` (round 6 S1 / round 5 X1).

## Hard edges (round 6)

- **Wave and ruleset bump (C1):** trade-ai **wave 3**. The policy runs outside `Step` and grants no capability
  flag, so it takes no bump; it **reads** the flags `world-stamp` grants (T-A8) and files nothing a flag does
  not allow. The wave is named because the family's landing order is one document
  ([../landing-order.md](../landing-order.md)).
- **Tuning:** `trade.build.*` lives in `ai.v{n}.json` (policy-only, never step-read); `ai-spend-limit` creates
  the AI domain's next version with the loader switch (global audit M8), so this module publishes `v{n+1}`.
- **The Standard Hall (round 6 L6) is not in this module's ladder list.** Forging standards is
  `legion-build`'s, and the AI's standard policy is not specced in this family; the building appears here only
  if a future AI plan reports it as a blocked plan, through the same table (§2) and the same `TierOf` read —
  never through a new check.
- **Power roll-up (D2):** force estimates read `legion-power`'s roll-up over the AI's own legions, and the six
  `world.*` channels the same way when a plan needs them (carry, march, sight). Nothing is computed here.

## Design-gate checklist

```
[x] Subsystems: world map AI (policy composition, ladder Hold), structures (build command), economy
    (loam upkeep — read only), power (roll-up — read only), tunables.
[~] Session boundary: docs-only round-4 reconciliation under the trade-network record; new file.
[x] Read this session: decisions-round-4.md (whole); trade-ai-map; ai-logistics, ai-bidding,
    ai-treaty-policy, deal-valuation specs; exchange treaty-vocabulary §5, trade-access §2a.
[x] decisions.md: no lock covers AI building.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: build admission (entity required), BuildResolver (presence, occupied slot,
    carried-loam cost), the one-order and admission throws in the fill, Hold, IWorldView reads; no AI
    build exists (search).
[x] Surrounding sections read: BuildResolver header, the fill's policy loop.
[x] No constraint claimed without a run.
[x] No §2 invariant contradicted: loam never converted; AI outside Step; one ActorHub read.
[x] Corrections propagated: composition order in ai-treaty-policy §1; clan exclusion in clan-behaviour.
[x] No population pinned: ladder list is the register's closed set; counts are fixture inputs.
[x] No event-refreshed cache.
[x] Orderings: candidate ties by ladder, tier, sector id; layer order fixed.
[x] Actor magnitudes: power roll-up read only, through Hub output (no second composer).
[x] No SOLID-violating path: same command, one valuation, one scorer.
[ ] Registry rows (no loam→value conversion scan; roll-up read-only scan) owed with the change.
[x] Round 5 (2026-09-20): A1 start kit (seat ladders start at tier 1), B1 (multi-kind slot
    candidates), B3 (own hub yard as a payoff row), C3 (Consulate for a deliberate embargo).
```

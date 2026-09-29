# Capability Map: trade-ai

**Status: APPROVED 2026-09-19** (owner). Owner question Q1 is decided — see *Owner decisions*. Module
specs written 2026-09-19 under `docs/architecture/trade-network/trade-ai/`; they correct this map where
the code disagreed (*Contradictions found*, TC1 and TC4–TC8). **Reconciled with the round-4 owner
decisions ([decisions-round-4.md](decisions-round-4.md)) on 2026-09-19** — new module 10
`ai-trade-buildings`, TC9–TC13, asks T-A9/T-A10; see *Reconciliation 2026-09-19 (round 4)* at the end.
**Program:** `trade-network` sub-program 7, `trade-ai` ([trade-network-ideal.md](../trade-network-ideal.md) §11).
**Ideal:** [trade-network-ideal.md](../trade-network-ideal.md) §7.5, §7.7, §8.5, §14b (player experience: interdiction, catch-up, difficulty).
**Specs land:** `docs/architecture/trade-network/trade-ai/spec-<module-id>.md` (the umbrella's layout,
[trade-network-map.md](../trade-network-map.md) §6).
**Plan:** `tasks/trade-network-trade-ai-plan.md` / `tasks/trade-network-trade-ai-todo.md` (written after approval).
**Siblings:** [counterparties-map.md](counterparties-map.md) and [exchange-map.md](exchange-map.md) (both upstream).

## What this sub-program is

How AI empires and clans **decide** — never how anything resolves. They move their goods, bid at hubs,
propose, accept and end treaties, send legions after the flows that matter most to their enemies, and
explain every refusal. Every decision is a `WorldCommand` filed through the same path the player uses,
by a policy running **outside `Step`** on the faction's own belief (`spec-ai-commander.md` §Where the AI
runs). The rule that shapes the whole map: **one valuation function for both sides of every deal**
(ideal §6 lesson 9, §7.5, §7.7).

## Assumptions (correct before approving)

1. **Model-free.** Deterministic policies over integer per-mille arithmetic; no LLM, no solver.
2. **Policies file data.** Replay never re-runs a policy, so improving the AI never breaks a save
   (`spec-ai-commander.md` §Design, and its *"most valuable test"*). Every module here inherits that test.
3. **Blind on the player's terms.** A policy reads `IWorldView` only; nothing under `World/Ai/` may
   mention `WorldState` (existing guard). Trade belief (prices, flows) must therefore be recorded as
   faction intel before an AI can use it.
4. **Difficulty is policy parameters, not stat bonuses** (`spec-ai-commander.md` assumption 3); the knobs
   are `counterparties`' `trade-difficulty-knobs`.
5. Numbers live in the AI domain, `gk-core/data/tuning/ai.v3.json` (the next version of `ai.v2.json`), for every
   policy-only key; `data/tuning/trade.v1.json` (new) holds only what `Step` reads (`intel.*`) and the
   difficulty rows `counterparties` owns; `data/tuning/diplomacy.v1.json` (new) holds `acceptMilli`
   (`exchange`'s list). Corrected at spec time — see TC5.

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| The AI fill: every policy faction, ordinal order, its own belief view and seed stream | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-245` |
| **The AI order bound is "entities + 1"** — a policy that files more throws inside the commit. The count is **every faction's** entities, not the filing faction's (corrected 2026-09-19, TC1) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:252` |
| The fill runs every AI order through the player's admission and **throws** on an inadmissible one | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:277` |
| `Hold` and a holding `Recover` file `stand-fast` with **no entity id**, so "entity-less" does not mean "policy order" | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:578` |
| AI reasons are a nullable command column, at most 200 characters | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:205`; column added at `:57` |
| AI command ids are `ai-{turn}-{entityId}` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:576` |
| The military ladder: Defend → Abandon → Finish → Take → Sever → Recover → Explore → Expand → Hold, one order per entity | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:62-70` |
| `ValueMap` scores **sectors** (yield, strategic, defensibility, cost, risk, curiosity), not goods or deals | `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:60-134` |
| Its caller passes no need vector, so needs are uniform | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60` |
| The utility scorer (`ResponseCurves`, `Consideration`) is built and has **no production caller** | `gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs`, `gk-core/src/FusionRpg.Core/World/Ai/Utility/ResponseCurves.cs` (a repo grep finds no caller outside that folder) |
| Belief carries sectors, slots, forces and structures — **no price, stock or flow** | `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:89`, `:143` |
| A faction policy sees a view with its own id and turn, and its own forces | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:17-37`; `BelievedWorldView` at `:76` |
| Threat is spread by staleness over the march graph and reads hostility through the one rule | `gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs:30`, `:71` |
| Boundaries of the AI module: *"Ask first: … a new command kind; changing the rule order"* | `docs/architecture/world/spec-ai-commander.md` §Boundaries (line 364) |
| *"No multi-turn plans, no stored intent, no diplomacy"* | `docs/architecture/world/spec-ai-commander.md` §Non-goals (line 284) — amended for this program (ideal §7.7) |

## Modules

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `trade-intel` | Faction belief for trade: last-seen hub quotes and lane flows, stale-stamped, recorded in the Intel phase | `exchange` `price-curve`; `logistics-flow` `lane-flow` | 1 |
| 2 | `deal-valuation` | **The one valuation function** for every deal, bid and treaty, both sides, in value-index units | `exchange` `goods-valuation`, `trade-access`; counterparties `need-vector` | 1 |
| 3 | `ai-spend-limit` | Per-turn AI spend limit (structural) and a widened, stated AI order bound | counterparties `empire-treasury`, `trade-difficulty-knobs` | 1 |
| 4 | `counter-offer-articles` | The fixed article list, the counter walk (no solver), explainable refusals | `deal-valuation`; `exchange` `treaty-vocabulary` | 2 |
| 5 | `ai-bidding` | AI and clan standing orders at hubs: buy wants, sell surplus above reserve, on believed prices | `deal-valuation`, `trade-intel`, `ai-spend-limit`; `exchange` `order-book` | 2 |
| 6 | `ai-treaty-policy` | When an AI proposes, accepts, counters, ends, embargoes, joins a bloc, makes war or peace | `counter-offer-articles`; `exchange` `treaty-lifecycle`; counterparties `diplomatic-stance` | 3 |
| 7 | `ai-logistics` | AI route policy, trade standing orders for AI legions, escorts on high-value flows | `trade-intel`, `deal-valuation`; `logistics-flow` `auto-banking`; `fleet`; `legion-build` standing orders | 3 |
| 8 | `interdiction` | Aim legions at the enemy's highest-value believed flows; adapt to the busiest; press the leader | `trade-intel`, `deal-valuation`; the military ladder | 4 |
| 9 | `clan-behaviour` | The `clan-keeper` policy: defend, never expand, run the hub from needs, answer treaties | `ai-bidding`, `ai-treaty-policy`; counterparties `clan-seeding`, `clan-economy` | 4 |
| 10 | `ai-trade-buildings` | **Round 4:** build and upgrade the buildings the AI's own trade plans need (Trade, Diplomacy, Banking, Caravans, Storage ladders), filed as `build` from one idle legion; sited with force estimates from the power roll-up | `deal-valuation`, `trade-intel`; payoffs from `ai-bidding`, `ai-treaty-policy`, `ai-logistics`; `exchange` tier reads; shared building-tier mechanism (exchange E-A14); power roll-up (T-A10) | 3 |

**Build order:** (`trade-intel` ∥ `deal-valuation` ∥ `ai-spend-limit`) → (`counter-offer-articles` ∥
`ai-bidding`) → (`ai-treaty-policy` ∥ `ai-logistics`) → `ai-trade-buildings` → (`interdiction` ∥
`clan-behaviour`). (`ai-trade-buildings` reads the blocked-plan payoffs of the three wave-3 layers, so it
lands after them; without it no AI empire can trade once round 4's building gates are live.)

**Dependency direction:** this map depends on `counterparties` and `exchange`; nothing there depends on
this map. The policies land as ids that `counterparties`' `empire-roster` catalogues.

**External dependencies (sibling module ids where maps exist):** `exchange` `goods-valuation`,
`price-curve`, `trade-access`, `order-book`, `treaty-vocabulary`, `treaty-lifecycle` · `counterparties`
`need-vector`, `empire-roster`, `empire-treasury`, `diplomatic-stance`, `trade-difficulty-knobs`,
`clan-seeding`, `clan-economy` · `logistics-flow` `lane-flow`, `auto-banking`, `lane-loss` (escort weight)
· `fleet` and `legion-build` (standing orders; no maps yet) · `world-map-program` `ai-commander` (the
commander loop, the ladder) · `trade-surface` `treaty-screen` (shows refusals and terms).

---

## Module detail

### 1. `trade-intel`

**Capability.** What a faction **believes** about trade, recorded like every other belief in the Intel
phase and hashed with it: the last quote it saw at each hub (price band, not exact stock — the
`RememberedForce` banding precedent), and the flow it saw on each lane it observed, both stamped with the
turn seen. A faction always knows its **own** hubs and flows exactly (holding ground grants full sight,
`world-map-program.md` line 46). The AI **plans on believed prices and flows and settles on the truth**
(ideal §8.5): an order placed on an old quote simply fills at the true price, or not at all. This is
faction belief, not AI memory, so it is also what the player's surfaces show (`trade-surface`
`trade-wire`), and it satisfies `spec-ai-commander.md` assumption 2 without stored intent.

- **Built:** the belief store, its staleness ladder and its banding pattern
  (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:89`, `:143`).
- **Real gap:** no price, stock or flow field in belief.
- **Touches:** `FactionIntel.cs` (new sparse fields), `IntelRecorder`, `IWorldView` (reads),
  `WorldCanonical.cs`.
- **Acceptance (contract):**
  - A faction never believes a quote or flow at a hub or lane it has not observed (blindness test, the
    `spec-ai-commander.md` §Testing precedent).
  - Own hubs and flows are exact; foreign ones are banded and carry `LastSeenTurn`.
  - A world with no trade records writes no new belief rows (sparse), so pre-trade worlds hash unchanged.
  - Two factions with different sight of one hub believe different quotes for it.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Intel, World/Ai); the `World/Ai` no-`WorldState`
  source scan in `FusionRpg.Guard.Tests`.

### 2. `deal-valuation`

**Capability.** One pure function, `DealValue(party, deal, view) → long` in value-index units, and one
acceptance rule, `accepts = DealValue ≥ acceptMilli[band] × dealSize / 1000`. It values:

- **goods legs** at `goods-valuation`'s index × the party's own per-good want from `need-vector`
  (giving away what you need costs more than giving away surplus);
- **soul legs** (player only) at the conversion base `exchange` publishes;
- **treaty legs** (`passage`, `market`, `preferential`, `bloc`, lifting an embargo) as the expected
  value, over the treaty's minimum term, of the flows it opens or closes, read from `trade-intel`, minus a
  **territorial risk term** for `passage` (letting foreign legions cross) read from `ThreatMap` and
  `ValueMap`'s risk axis — the only place `ValueMap` enters, because it scores sectors, not goods
  (contradiction TC2);
- **tariff and fee legs** at their value.

It is **the same function** for: scoring a player proposal, an AI-to-AI proposal, an AI's own decision to
open or close a route, an AI bid's reservation price, and every counter-offer step (ideal §7.7). The band
**limits what is possible** (`exchange` `treaty-vocabulary` lowest band per kind); valuation decides what
happens. No lump-sum-for-per-turn deals in v1 (ideal §7.5). The considerations are combined with the
built utility scorer (`ResponseCurves`/`Consideration`), giving it its first production caller.

- **Built:** `ValueMap`, `ThreatMap`, the utility scorer (see *What the code says*).
- **Wiring gap:** the scorer has no caller; `ValueMap`'s need input is never passed
  (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60`).
- **Real gap:** the deal function and its acceptance rule.
- **Touches:** `src/FusionRpg.Core/World/Ai/Trade/` (new; under `World/Ai/` so the no-`WorldState` scan and
  the determinism guard cover it); `diplomacy.v1.json` (new) `acceptMilli.{band}`.
- **Acceptance (contract):**
  - **Symmetry:** for any deal, the proposer's and the responder's scores are computed by the same code
    path with only `party` swapped; a source scan finds one implementation.
  - **Proposer-blind:** a deal's value to a party does not depend on who proposed it.
  - **Need-monotone:** raising a party's want of a good it receives never lowers `DealValue` for it.
  - **Band gate first:** a deal whose kind's lowest band the pair does not reach is refused before any
    valuation, with the band named.
  - A deal containing a per-turn-for-lump-sum exchange is rejected as out of vocabulary.
  - Pure and deterministic over `(view, deal, seed)`.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai/Trade); property tests over generated deals.

### 3. `ai-spend-limit`

**Capability.** Two bounds, both **structural** and commented as such:

1. **Spend:** an AI faction's total committed value per turn (bids, soul-free barter it gives up, tariffs
   it accepts) ≤ `difficulty.<profileId>.aiMaxSpendPerTurnMilli` ‰ of its income, where income is what its treasury banked last
   turn (hashed state, `counterparties` `empire-treasury`). The ‰ value per difficulty profile comes from
   `trade-difficulty-knobs` (ideal §14b, *"AI bidding and AI spend limit are its knobs"*).
2. **Orders:** the fill's bound becomes *at most one order per own entity plus one, and at most
   a policy-order bound that grows with owned sectors (`trade.policyOrdersBase` + `trade.policyOrdersPerOwnSector` × own sectors, audit 2026-09-20) of the policy-order kinds* (route, bank-hold, order-set, treaty, embargo,
   bloc, war/peace), counted **by kind**, not by a null entity id. Today's bound —
   `orders.Count > world.Entities.Count + 1` throws — counts every faction's entities, so its real limit
   on one faction depends on how many legions its enemies field (contradiction TC1, corrected).

- **Built:** the bound's site and its intent (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:249-253`).
- **Wiring gap:** the bound does not know entity-less policy orders.
- **Real gap:** the spend limit.
- **Touches:** `RpgStore.WorldTurns.cs` (the bound), `src/FusionRpg.Core/World/Ai/Trade/` (new),
  `ai.v3.json` (new) `trade.policyOrdersBase`, `trade.policyOrdersPerOwnSector`; the spend ‰ is read from `counterparties`'
  `difficulty.<profileId>.aiMaxSpendPerTurnMilli` (TC5).
- **Acceptance (contract):** over a 20-turn run no AI faction's committed value in any turn exceeds its
  limit; a policy that files one order per entity plus the policy-order allowance commits, and one more
  throws; the bound's comment names it structural; the limit reads the profile, and a missing key rejects
  the load.
- **Verification boundary:** `FusionRpg.Data.Tests` (world commit fill), `FusionRpg.Core.Tests` (World/Ai/Trade).

### 4. `counter-offer-articles`

**Capability.** A **closed article list** — the only moves a counter-offer may make, in a fixed order:
change a goods quantity by one `orderStepUnits` step, add or remove one good, step a tariff within its
kind's band, step the term, downgrade the kind (`preferential` → `market` → `passage`), add or drop an
embargo lift, and (player side only) add a soul top-up step. A counter is produced by **walking the list
in order**, one step at a time, re-scoring with `deal-valuation`, until the deal crosses the responder's
threshold or a structural step bound is reached — never a solver, never "make it equitable" (the
solver exploit, ideal §6). **Every refusal shows its terms**: the band gate or the value shortfall, and the
articles tried, as the command's reason (≤ 200 characters, the existing column) and as a turn-report
line `trade-surface` renders.

- **Built:** the reason column and its length rule (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:205`).
- **Real gap:** the walk order, the refusal format. **Ownership corrected at spec time (TC4):** the
  article *kinds* are part of the `treaty-propose`/`treaty-respond` payload that `exchange` admits, so the
  vocabulary lives in `exchange` `treaty-vocabulary` (ask T-A5); this module owns the **order** the walk
  tries them in and the direction rule per kind.
- **Touches:** `src/FusionRpg.Core/World/Ai/Trade/` (new).
- **Acceptance (contract):**
  - The walk order is a **closed list** over `exchange`'s article kinds (pinned because the code owns it;
    reordering is a reviewed change).
  - A counter differs from the proposal by a sequence of listed articles only, of length ≤ the structural
    step bound.
  - The walk is deterministic: the same proposal and view give the same counter.
  - Every refusal names either a band or a numeric shortfall; a refusal with neither fails the test.
  - A counter never gives the responder less than its threshold (no self-harming counter).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai/Trade).

### 5. `ai-bidding`

**Capability.** The AI's and clans' standing orders at hubs, filed as `exchange`'s `order-set`: **buy**
goods whose want exceeds 1000 up to a reserve horizon, **sell** stock above a need reserve, at a
reservation price from `deal-valuation` on the **believed** quote, scaled by the profile's bidding
aggressiveness, within `ai-spend-limit`. Orders are standing policy, so a stable AI files few changes per
turn. Because `exchange` fills pro rata and walks the aggregate, an AI cannot outbid by splitting or by
id order — only by wanting more and paying more.

- **Real gap:** all of it.
- **Touches:** `src/FusionRpg.Core/World/Ai/Trade/` (new).
- **Acceptance (contract):** an AI never files a sell of a good below its need reserve; never files a buy
  of a good whose want is ≤ 1000; never exceeds the spend limit; an AI with a real shortage and a
  reachable open hub files a buy within one turn of seeing it (a reachability test, not a count); every
  order carries a reason naming the want and the believed price.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai/Trade), `FusionRpg.Data.Tests` (fill).

### 6. `ai-treaty-policy`

**Capability.** Per AI empire per turn, **which** diplomacy command to file, all scored by
`deal-valuation`: propose treaties whose value to it clears its threshold; accept, counter or decline
offers (counters from `counter-offer-articles`); end a treaty when it has turned negative — weighing the
`treaty.broken` cost before the minimum term; set or lift embargoes; join or leave a bloc; declare war or
accept peace, weighted by the empire's personality (`counterparties` `empire-roster`). The dominant enemy
empire's stance toward the player follows `counterparties` Q1 — **confirmed by round 4 Q4: the lock is the
player pair only**; it treats with rivals and clans like any empire. One diplomacy decision per pair per turn,
so the log reads one line per relationship.

- **Real gap:** all of it; the amended `spec-ai-commander.md` non-goal (counterparties ask A5).
- **Touches:** `src/FusionRpg.Core/World/Ai/Trade/` (new); a new policy id registered in `FactionPolicies`
  that composes the existing military ladder for entities with this layer for policy orders — one policy
  per faction, not a second brain.
- **Acceptance (contract):**
  - At most one diplomacy command per pair per faction per turn.
  - An AI never accepts a deal below its threshold and never declines one above it without a named
    reason (band gate, war). *Narrowed at spec time: personality changes what an AI proposes, never
    its acceptance threshold — a personality veto would be a second acceptance rule.*
  - **The architectural test, inherited:** replaying a stored command log with a different treaty policy
    registered leaves every hash unchanged.
  - Blindness: no diplomacy command names a faction the AI has never met (intel), except the public facts
    of `diplomacy-facts`.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai/Trade), `FusionRpg.Data.Tests` (replay).

### 7. `ai-logistics`

**Capability.** The AI runs the same logistics the player does, through the same commands:
auto-banking by default (`logistics-flow` `auto-banking`), `route-set` when a hub or a bank point is worth
redirecting to, trade standing orders on legions for foreign routes (`fleet` / `legion-build`), and
**escorts** on its highest-value flows (the escort weight in `logistics-flow` `lane-loss`). A legion on a
trade standing order is skipped by the military ladder, so *one order per entity* still holds. It plans on
believed lane states.

- **Real gap:** all of it; `fleet` and `legion-build` standing orders must exist first.
- **Touches:** `src/FusionRpg.Core/World/Ai/Trade/` (new); the ladder's entity walk (skip standing-order
  legions).
- **Acceptance (contract):** no entity receives two orders in a turn (asserted over a 20-turn run, the
  existing invariant test extended); the AI files only command kinds the player can file; a severed
  route's goods are re-routed or the route cleared within one turn of the AI seeing the cut.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai).

### 8. `interdiction`

**Capability.** Enemy counter-development for trade (ideal §14b; `docs/guide/the-loops.md:95`): the AI
aims legions at the **highest-value flows it believes its enemies run** — lane value from `trade-intel`
× `deal-valuation`'s goods index — and presses **the leader** hardest (the target's score scales with its
share of believed banked flow, the catch-up rule). It reads the **aggregate** of flows at faction level
and never a record of individual encounters, so it keeps every anti-Nemesis rule
(`npc-story-events-ideal.md` §6.12: no enemy grows from meeting you, no enemy remembers you personally).
It is a new rule in the military ladder, **after `Recover` and before `Explore`** (owner decision Q1,
2026-09-19), and files the same `move` / `stand-fast` orders
every rule does; a hostile legion on a lane produces loss through `logistics-flow` `lane-loss`
(`hostilePresenceMilli`) and battles through the kind-agnostic contact path — no spawned raiders.

- **Built:** the ladder, `ReachMap`, `ThreatMap` (see *What the code says*).
- **Real gap:** the rule and its target score.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs` (a rule in the ladder), `ai.v2.json` →
  `ai.v3.json` (new) for its weights, published through the tuning tool.
- **Acceptance (contract):**
  - Targets only lanes the faction has observed (blindness).
  - At most `interdict.shareMilli` of a faction's legions interdict in one turn (a structural share, so
    the defend and finish rules keep their legions).
  - Given two believed flows, the higher-value one is targeted first; given two enemies, the one with the
    larger believed share is pressed first.
  - No interdiction input is keyed by a specific encounter or a player-side character (anti-Nemesis
    guard rows in `gk-core/scripts/enforcement-registry.v1.json`, shared with `npc-story-events`'
    `counter-doctrine`).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai); campaign scenario tests run and reported.

### 9. `clan-behaviour`

**Capability.** The `clan-keeper` policy for `Clan`-kind factions: militarily it **defends its ground and
never expands** (the kind's contract, `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:12-13`); economically
it runs its hub from its own needs through `ai-bidding` (sells surplus, buys wants), answers treaty offers
through `ai-treaty-policy` with clan weights, and never files a foreign trade route. Clan **requests** to
the player are `npc-story-events`' `petition-host`, computed from the same `need-vector` — this module
files none. A clan's personality is data (`counterparties` `clan-seeding`), never a branch per clan.

- **Built:** the kind and its contract (above); `stand-fast` as the current garrison posture for the wild.
- **Real gap:** the policy.
- **Touches:** `FrontierRulesPolicy` (its rules become an ordered list; `clan-keeper` is the same class
  with a rule subset — refined at spec time, no second policy file), `FactionPolicies` registration.
- **Acceptance (contract):** a clan never files `move` out of its own sectors or `claim`; two clans with the
  same personality data behave identically in identical states; a clan with no surplus files no sell.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Ai).

### 10. `ai-trade-buildings` (round 4)

**Capability.** Round 4 gates every trade feature on a building, so an AI that never builds never trades
— a handicap principle 10 forbids. This layer files `build` (and, once the shared building-tier
mechanism, `trade-foundation` `sector-features`, exists, upgrades) for the buildings the AI's **own blocked plans** need: a Trading Post or
Market for an order `ai-bidding` cannot place, an Embassy, Consulate or Exchange for a treaty candidate
`ai-treaty-policy` could not propose, a Caravan Yard or Counting House for `ai-logistics`, a Storehouse
tier for a halt, a Treasury for a hold. The payoff is the blocked plan's `deal-valuation` value; the
decision is a product of considerations (payoff, carried loam, upkeep, safety) on the built scorer —
loam is never priced. **Safety uses force estimates from the power roll-up** over the AI's own legions
(round 4 §P), belief for the enemy. It claims at most one idle (`Hold`) legion standing in the sector per
turn. Clans never build.

- **Built:** `build` and its resolver (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`, `:134`).
- **Real gap:** no AI files `build` today; all of it.
- **Acceptance (contract):** every AI `build` is admitted and resolves; no build with zero payoff or into a
  loam deficit; reachability of a Trading Post and an Embassy in fixtures; replay-invariant; legacy worlds
  unchanged. Spec: [spec-ai-trade-buildings.md](trade-ai/spec-ai-trade-buildings.md).

---

## Filed asks (other programs)

| # | To | Ask |
|---|---|---|
| T-A1 | `world-map-program` `ai-commander` | Amend §Non-goals (*"no diplomacy"*, line 284) and §Boundaries (*"a new command kind; changing the rule order"*) for this program: the new kinds are `exchange`'s and `counterparties`'; the new rule is `interdiction` (Q1) |
| T-A2 | `fleet`, `legion-build` | A legion on a trade standing order is identifiable from state so the ladder can skip it |
| T-A3 | `npc-story-events` `counter-doctrine` | Share the anti-Nemesis guard rows; interdiction is a trade-flow reading at faction level and must pass the same six rules |
| T-A4 | `trade-foundation` `routing-guard` | Add `src/FusionRpg.Core/World/Ai/Trade/**` to the guarded paths (TC7): trade-ai plans no routes, and the guard proves it |
| T-A5 | `exchange` `treaty-vocabulary`, `treaty-lifecycle` | Own the **article kinds** and the **deal shape** (one time shape per deal: one-off or per-turn over the term) in the `treaty-propose`/`treaty-respond` payload, and carry structured **refusal terms** (code, band, shortfall, articles tried) in `treaty-respond`, so the step can write the refusal line the proposer reads (TC4) |
| T-A6 | `exchange` `order-book`, `treaty-lifecycle`; `goods-valuation` | Project a faction's own open orders and the offers addressed to or from it through `IWorldView`; give `order-set` a **limit price**; export `ValueOfSouls` (the inverse of `SoulsBaseFor`) so no module re-derives the soul conversion |
| T-A7 | `counterparties` `need-vector`, `relation-facts`, `empire-treasury`, `clan-economy` | A pure `WantAt(good, stock)` read and a reserve quantity per good; a belief-side estimate of another faction's want; the logged band snapshot, own treasury/stock and last turn's own income, each through `IWorldView` (the `LastOrderedDestination` precedent) |
| T-A8 | `trade-foundation` `world-stamp` | The world's capability flags and difficulty profile id readable through `IWorldView` (public, not fogged), so a policy files trade orders only where admission will take them (TC6) |
| T-A9 | `exchange` `trade-access`, `exchange-hub` | The building gate (`LevelAt`, `EffectiveLevel`, tiers) callable on a belief view, so a policy sees *"needs a Trading Post"* before it files. **Answered in the round-4 reconciliation:** `trade-access` interface (one rule, a read interface implemented by the world and by `BelievedWorldView`); own tiers exact and foreign hub tiers believed through `trade-intel` |
| T-A11 | world-map-program `intel` (`RememberedSlot`) with `trade-foundation` `sector-features` | Remember a surveyed slot's `StructureTier` beside its `StructureId`, so a foreign hub's tier is believed, not read from truth (X-A4) |
| T-A12 | `fleet` `depot` (round 5 B3) | Expose `ForeignSite.Of` — the one foreign-hub yard check — in a believed form through the view (`trade-intel` `BelievedAcceptsCaravans`); no exchange-side predicate exists (filed in *Round 5* below; listed here so the table is complete — audit 2026-09-20) |
| T-A10 | `legion-build` `legion-power` (module 17) — the roll-up's owner, named by `legion-build-map.md` during this reconciliation (X-A1 resolved) | Expose `legion-power` for the faction's **own** legions through `IWorldView` (`OwnLegionPower(entityId)`), Hub output only — no second composer. Until it lands, every AI force estimate keeps today's stack count. **Round 6 D2 extends the same ask, not a second one:** the six `world.*` channels (`carry.capacity`, `march.range`, `supply.burn`, `sight`, `hazard.resist`, `upkeep.discount`) roll up through the same module (`spec-legion-power.md` §6) and reach a policy through the same view read, behind the stated defaults until the named future program `world-derived` registers them |
| T-A13 (**round 6**) | `counterparties` `trade-difficulty-knobs`, `empire-roster` | **Move the policy-only keys into the AI domain file:** `difficulty.<profileId>.{aiBidAggressionMilli,aiMaxSpendPerTurnMilli}` and `personality.<policyId>.*` belong in `ai.v3.json`, which `Step` never reads, not in the step-read `trade.v{n}.json` whose version enters every world stamp — otherwise an AI-appetite retune refuses replay of every trade world for nothing (audit A-X1, TC5, tunables-ssot T7). One home per key: while the move lands, nothing here duplicates one |

## Contradictions found

| # | Where | What | Recommended resolution |
|---|---|---|---|
| TC1 | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:252` vs ideal §7.5/§7.7 | **Corrected at spec time.** The bound compares against `world.Entities.Count` — every faction's entities — so it does not bound one faction by its own legions at all; and `Hold` already files entity-less `stand-fast` (`FrontierRulesPolicy.cs:578`), so "entity-less" cannot identify a policy order | `ai-spend-limit` replaces it with two counts: orders of ordinary kinds ≤ own entities + 1, orders of the closed policy-order kinds ≤ `trade.maxPolicyOrdersPerTurn` |
| TC2 | Ideal §7.5 (*"offers are scored by `ValueMap` with real needs"*) vs `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:60-134` | `ValueMap` values sectors, not goods or deals | `deal-valuation` is the one function; it values goods through `goods-valuation` × `need-vector` and uses `ValueMap`/`ThreatMap` only for the territorial risk of `passage` |
| TC3 | `spec-ai-commander.md` §The decision layer (*"Rules rather than scoring, deliberately — scoring wants an economy to score against"*) | The economy now exists | Trade decisions use the built utility scorer (its first caller); the military ladder stays a ladder. **Refined at spec time:** the scorer returns 0..1000 (`gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:37`), so it scores confidence, risk and war/peace appetite; deal value itself is a signed `long` sum in value-index units, because acceptance and the anti-pump guards need an additive quantity |
| TC4 | `exchange-map.md` module 9 (*"`treaty-propose` (a kind plus articles from `trade-ai`'s fixed article list)"*) vs this map's dependency direction | `exchange` admission must validate article kinds, so owning them here makes `exchange` depend on `trade-ai` — a cycle | The article kinds and the deal shape are `exchange`'s (T-A5); `counter-offer-articles` owns the walk order only |
| TC5 | This map's first tunables list (`trade.v1.json` `ai.*`) vs `trade-foundation` `world-stamp` (*"Replay refuses … when any recorded tuning version differs"*) | `trade.v1.json` is read by `Step`, so its version is in every world's stamp; policy-only knobs there would make every AI re-tune refuse replay for nothing, since replay never runs a policy | trade-ai's own keys go to the AI domain, `gk-core/data/tuning/ai.v3.json` (new version), which `Step` never reads. Keys other maps own stay theirs: `difficulty.<profileId>.*` in `trade.v1.json` (`counterparties`), `acceptMilli.{band}` in `diplomacy.v1.json` (`exchange`) |
| TC6 | Ideal §7.5 (*"the AI uses the same machinery"*) vs `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:277` | An AI order that admission refuses **throws** and rolls back the commit; on a legacy-stamped world every trade kind is refused | Every trade layer reads the world's capability flags through the view (T-A8) and files nothing a flag does not grant |
| TC7 | `logistics-flow-map.md` C8 (*"any sibling that plans routes (e.g. `trade-ai`) must"* live under `World/Logistics/`) vs `World/Ai/`'s no-`WorldState` scan | The two guards want different folders | trade-ai plans **no routes**: it names destinations and `logistics-flow`/`fleet` path them. Its code stays under `World/Ai/Trade/`, and the routing guard widens to that folder (T-A4) |
| TC8 | `trade-intel` capability (*"stamped with the turn seen"*) vs `gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs:78` | `Merge` keeps survey-only fields from an older survey while taking the glimpse's `LastSeenTurn`, so a quote kept on the snapshot would look fresh after any glimpse | Each remembered quote and flow carries its own seen-turn (spec `trade-intel` §Design 2) |
| TC9 | Round 4 §B (every trade feature needs a building) vs this map's nine modules | No module ever files `build`; the AI would be locked out of every feature the player unlocks by building — a handicap (principle 10) | New module 10 `ai-trade-buildings` |
| TC10 | `ai-bidding` §2: *"Sell at the own hub"* vs `exchange` `order-book` `order.own-hub` | An owner cannot place an order at its own hub | Own hubs sell passively; the Treasury hold (round 4 Q2) keeps stock for buyers (fixed in `ai-bidding`) |
| TC11 | `acceptMilli.{band}` ownership: this map and `deal-valuation` said `exchange`; `exchange` said `trade-ai` | Nobody owned the key | `deal-valuation` owns it (exchange EC22); `hostile` dropped |
| TC12 | `deal-valuation` cites `ValueOfSouls` (T-A6) | `goods-valuation` exports `ValueForSouls` | One function, `ValueForSouls` (exchange EC26) |
| TC13 | `ai-treaty-policy` scope left the dominant empire's treaty scope to counterparties' open question | Round 4 Q4 decided it: the lock is the player pair only | Read `IsLockedWar`; the dominant empire treats with rivals and clans |

## Owner decisions

| # | Question | Decision (2026-09-19) |
|---|---|---|
| Q1 | **Where `interdiction` sits in the military ladder.** `spec-ai-commander.md` reserves changing the rule order for the owner, and it changes how every AI empire plays | **After `Recover`, before `Explore`**: Defend → Abandon → Finish → Take → Sever → Recover → **Interdict** → Explore → Expand → Hold. An empire defends, cuts its losses, finishes what it started and heals first, then hunts flows, then scouts and expands. **Limited to a tunable share of the empire's legions** (`interdict.shareMilli`, structural) |
| Q4 (round 4) | May the dominant enemy empire treat with anyone? | **Yes, with rivals and clans; never with the player** ([decisions-round-4.md](decisions-round-4.md) Q4) |


No owner question remains open in this map; the round-4 reconciliation raised one (OQ-A1, below),
decided by round 5 A1.

## Tunables (keys owed by the specs; values decided by principle)

**One creator per versioned tuning file (global audit M8, round 6).** `ai.v3.json` is created by
**`ai-spend-limit`** — the wave-1 module whose keys are the structural bounds every other trade-ai module's
filing passes through, so the file must exist before any policy files an order — and that one change carries
the **loader switch** (`gk-core/src/FusionRpg.Server/Program.cs:234` names the file literally). Every other spec here
publishes **`v{n+1}`** through `gk-core/tools/tuning/publish.py` and never claims the switch; three specs used to claim
it, and only the first lander could have had it.

**Which file a key belongs in (the rule, stated once).** A key only a **policy** reads lives in the AI domain
file `ai.v{n}.json`, which `Step` never reads, so retuning AI appetite moves no world stamp. A key **`Step`**
reads lives in `trade.v{n}.json`, whose version enters every trade-stamped world's stamp — publishing it
refuses replay of older trimmed reports, which is correct for a rule and wrong for a preference (TC5,
tunables-ssot T7).

`gk-core/data/tuning/ai.v3.json` (the AI domain's next version, published through `gk-core/tools/tuning/publish.py`;
TC5; created by `ai-spend-limit`, above): `trade.policyOrdersBase`, `trade.policyOrdersPerOwnSector` (structural; replace the flat `trade.maxPolicyOrdersPerTurn`, audit 2026-09-20), `trade.counterStepBound`
(structural), `trade.orderRefileSteps`, `trade.caravanShareMilli` (structural), `trade.escortMinFlowValue`,
`trade.valuation.*` (confidence and territorial-risk consideration weights, `territoryValuePerPoint`,
`treatyBrokenWeightMilli`), `trade.diplomacy.*` (war and peace consideration weights and thresholds),
`interdict.shareMilli` (structural), `interdict.leaderWeightMilli`, `interdict.minFlowValue`.
`data/tuning/trade.v{n}.json` (**step-read**; the file is created by `trade-foundation` `economy-report`,
global audit M8 — every spec here publishes `v{n+1}`): `intel.quoteBandEdgesMilli`, `intel.flowBandEdges`
(this map — they belong here because the intel memory they band is **hashed state** written inside `Step`,
`trade-intel` §Hard edges).

**Moved out of the step-read file (round 6, closing A-X1 by principle).**
`difficulty.<profileId>.{aiBidAggressionMilli,aiMaxSpendPerTurnMilli}` and `personality.<policyId>.*` are
**policy-only** reads: nothing in `Step` touches them, yet placing them in `trade.v{n}.json` would put them in
every world's stamp, so a pure AI-appetite retune would refuse replay of every trade world for nothing. By the
rule above they belong in **`ai.v3.json`**, and this map reads them from there. The keys' owner is
`counterparties` (`trade-difficulty-knobs`, `empire-roster`), so the move is **filed as ask T-A13** (below) and
the reading modules here name `ai.v3.json` as the home. Until the move lands, `ai-spend-limit` and
`ai-bidding` read whichever file publishes them and neither duplicates the key — one home, never two.
`data/tuning/diplomacy.v1.json` (new): `acceptMilli.{eager,open,wary}` — **owned by `deal-valuation`** (its
only reader; corrected in round 4 — both this map and `exchange` had named the other, exchange EC22; the
`hostile` key is dropped because round 4 blocks every deal at `hostile`).
`gk-core/data/tuning/ai.v3.json` also gains `trade.build.{idleShareMilli (structural; replaces maxPerTurn, audit 2026-09-20),horizonTurns,payoffScaleValue,minScoreMilli,weights}`
(`ai-trade-buildings`).
The reserve horizon is `counterparties`' `needs.reserveTurns` (spec `counterparties/spec-need-vector.md`),
read, never duplicated.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world map AI (ai-commander, intel, ladder), economy (spend, sinks), tunables,
    numeric types, relation ladder (band gates), narrative (anti-Nemesis rules).
[~] Session boundary: working under trade-network-idea-20260919 (docs/architecture/trade-network/**).
    session-boundary-check.py exits 1 on crossings already recorded in that record; new files only.
[~] Read this session: as counterparties-map.md's checklist, plus npc-story-events-ideal §6.12 in full
    and spec-ai-commander.md in full. NOT read: world-map-runtime ideal and specs (FE only).
[x] decisions.md: no lock covers AI trade or diplomacy; spec-ai-commander's non-goals and boundaries
    are the binding text and are amended by ask T-A1, not bypassed.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH finding.
[x] Verified against code: the AI fill and its bound, the ladder, ValueMap's axes, belief fields, the
    utility scorer's (absent) callers — read or grepped directly.
[x] Surrounding sections read: spec-ai-commander §Design, §Non-goals, §Boundaries; ideal §7.5, §7.7,
    §14b; npc ideal §6.12.
[x] No constraint claimed without a run; replay-invariance is an inherited acceptance test.
[x] No §2 invariant contradicted; AI stays outside Step (invariant of spec-ai-commander).
[x] Corrections: none made outside this file (fence); contradictions and asks listed.
[x] No population count pinned. Pinned closed vocabularies: counter-offer article kinds (code-owned).
[x] Caches: none. Belief is hashed state recorded each turn, not an edge-refreshed cache.
[x] Orderings: pro-rata fills (exchange) make AI bids order-independent; one diplomacy decision per pair.
[x] Actor magnitudes: none produced or consumed.
[x] No SOLID-violating path: one valuation function for both sides; one policy per faction composing the
    existing ladder; the built utility scorer reused, not re-written.
[~] Registry rows: anti-Nemesis rows are shared with npc-story-events (ask T-A3); others owed by specs.
```

**Spec-time update (2026-09-19).** Status set to APPROVED and Q1 recorded on the owner's decision. The
nine module specs re-read the code this map cites and found TC1 mis-stated and TC4–TC8 new; each is
corrected above and carried into the specs. `audit-doc-citations.py --scope` was re-run on this file
after the edit.

---

## Reconciliation 2026-09-19 (round 4)

Applies [decisions-round-4.md](decisions-round-4.md) (binding) to this sub-program. Verified against
code this session: no AI policy files `build` (a search of `gk-core/src/FusionRpg.Core/World/Ai/` for
`WorldCommandKinds.Build` finds nothing); `build` is an entity order whose founder must stand in the
sector and pay from carried loam (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:110`,
`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`, `:134`); the fill throws on a second order for
one entity or an inadmissible order (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:272`, `:280`);
belief remembers a slot's structure (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:74`).

### R1. What round 4 changed here

| Decision | Where it landed |
|---|---|
| B — trade-ai builds and upgrades the buildings it needs | New module 10 `ai-trade-buildings` ([spec](trade-ai/spec-ai-trade-buildings.md)); composition order in `ai-treaty-policy` §1 |
| B — access = building tier AND treaty/band | `ai-bidding` (hubs filtered by `LevelAt`), `ai-treaty-policy` (candidates need both parties' buildings), `deal-valuation` (`BuildingGate` before valuation; refusal code `Building`), `counter-offer-articles` (downgrade to what the buildings allow), `ai-logistics` (Caravan Yard, Counting House), `trade-intel` (`OwnFeatureTier`, `BelievedHubTier`) |
| B/Q1 — clans need no treaty or embassy; `hostile` blocks | `clan-behaviour` (seeded tier-1 hub, never builds); `acceptMilli.hostile` dropped |
| P — AI force estimates from the power roll-up (own legions) | `ai-trade-buildings` (Safe), `ai-treaty-policy` (WarScore own side), `deal-valuation` (garrison in the passage risk), `ai-logistics` (escort choice), `interdiction` (legion choice). Read only, never a contest term — no §10 row needed; stack count until it lands (T-A10) |
| Q4 — never-peace applies to the player only | `ai-treaty-policy` (reads `IsLockedWar`; criterion 11) |

### R2. Asks aimed at this map

| Ask | From | Status |
|---|---|---|
| (none) — no other map files an ask on `trade-ai`; the asks this map filed on `exchange` (T-A5, T-A6, T-A9) are answered in the same reconciliation (`exchange-map.md` R2) | — | — |

### R3. Cross-cluster conflicts (outside this fence — not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-A1 (**resolved**: `legion-build` `legion-power` (module 17)) | The power roll-up (round 4 §P) had no owning module in any map, and three consumers wait on it (warden defence in `world-continuity`, escort strength in `logistics-flow` `lane-loss`, AI force estimates here) | Owner: **`legion-build`** — it owns stack `Count` and the member stack, so "a legion's power = Σ stacks" is its read over Hub output; `world-continuity` sums legions for a warden. Expose own-legion power through `IWorldView` (T-A10) |
| X-A2 | The shared building-tier mechanism had no owner (`exchange-map.md` X-1) | **Resolved:** `trade-foundation` `sector-features`; `ai-trade-buildings` offers tier-1 candidates only until it lands |
| X-A4 | Belief remembers a slot's `StructureId` (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:74`) but not its tier; `BelievedHubTier` needs it | Ask T-A11 on the intel owner (world-map-program `intel`) and `sector-features`: copy `StructureTier` onto `RememberedSlot` when surveyed (sparse, conditional canonical row, old hashes unchanged) |
| X-A3 | `legion-build`'s standing orders must mark a caravan legion in state for the ladder skip (T-A2, filed before) and, since round 4, carry which Caravans tier the order needs | `legion-build` / `fleet`: the standing-order record names the depot sector so the Caravan Yard check is one read |

### R4. Closed-vocabulary widenings

This map adds none of its own. It consumes `exchange`'s: refusal codes (+`Building`), article kinds (9),
deal shapes (2), tier ladders. The counter walk order (a closed list here) is unchanged in length.

### R5. Gap check

- Every module has a spec (10 of 10; `ai-trade-buildings` written in this reconciliation).
- Dependencies resolve: X-A1 became `legion-build` `legion-power` (module 17) and X-A2 `trade-foundation` `sector-features` during this
  reconciliation; both
  have a stated fallback (stack count; tier 1 only), so no module is blocked from starting.
- Tuning keys: `acceptMilli` now has one owner (`deal-valuation`); `trade.build.*` are new and unique;
  no key is claimed twice.

### R6. Owner question (genuine)

**OQ-A1 — DECIDED 2026-09-20 (round 5 A1): option (a), and the shared start is named** — every
empire's seat, player and AI, starts with a tier-1 Counting House and a tier-1 Storehouse; everything
else is built (`ai-trade-buildings`). *Original question:* Do AI empires start with the trade buildings,
or build them like the player?
- (a) **AI empires start with exactly what the player starts with and build the rest through
  `ai-trade-buildings`.** *Recommended:* principle 10 (a rule that binds the player binds every AI), and
  it makes the early world readable — the player sees rivals' Trading Posts appear.
- (b) AI empires start with a trade kit (Trading Post, Embassy) so the world trades from turn 1.
- (c) The difficulty profile decides how many starting buildings AI empires get
  (`trade-difficulty-knobs`), with (a) as the default profile.

### R7. Citation audit

`python scripts/audit-doc-citations.py --scope` was run on this map and every edited spec under
`trade-ai/` after these edits: no HIGH finding.

## Round 5 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 5* (R5-A, R5-X; binding). Re-verified this
session: no AI policy files `build` yet (no `WorldCommandKinds.Build` under `gk-core/src/FusionRpg.Core/World/Ai/`);
belief remembers a slot's structure (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:74`); a row names
one required slot kind (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`).

| Ruling | Where it landed |
|---|---|
| **A1** — every seat (player and AI) starts with a tier-1 Counting House and Storehouse | OQ-A1 closed; `ai-trade-buildings` §1 (seat ladders start at tier 1); `ai-logistics` (the seat is always a bank-point target) |
| **A4** — hold default = other traders' open buy orders at the hub | `ai-bidding` wording |
| **B1** — Trading Post on Wildland or Market | `ai-trade-buildings` §1 candidates |
| **B3** — caravans unload at a foreign hub only with the hub owner's yard | `ai-logistics` (foreign legs only where believed accepted), `trade-intel` (`BelievedAcceptsCaravans`, the believed `fleet` `ForeignSite.Of`), `ai-trade-buildings` §2 (own-hub yard payoff row) |
| **C2** — only the offerer needs an Embassy | Already the rule (`deal-valuation`, `ai-treaty-policy`); now the owner's decision |
| **C3** — a deliberate embargo needs a Consulate | `ai-treaty-policy` §2 step 4; `ai-trade-buildings` §2 payoff row |
| **X1** — every gate reads `sector-features` | `trade-intel` `OwnFeatureTier(SectorFeature)` (was keyed by kind) |
| **X7** — power roll-up owner is `legion-build` `legion-power` | Already cited in `ai-trade-buildings`; `ai-treaty-policy` and `ai-logistics` now name it |

**Ask filed:** T-A12 on `fleet` `depot` — its `ForeignSite.Of` (round 5 B3, the one foreign-hub yard
check) is read through the view in its believed form (`trade-intel` `BelievedAcceptsCaravans`); no
exchange-side predicate exists.

**Not applicable here:** A2, A3, B2, B4 (a trader-side rule `ai-bidding` already obeys through
`LevelAt`), C1, C4, D1, X2–X6, X8–X16. No new contradiction; no owner question.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and every edited
`trade-ai/` spec after these edits.

## Audit 2026-09-20

Independent audit of this map and its ten specs against DESIGN-GATE §2/§3/§5, PRINCIPLES,
tunables-ssot, validation-ssot, testing-standard, economy-principles, ssot-power-scale §10–§11 and the
round-4/round-5 register; code claims spot-checked this session (the AI fill bound,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:252`; the command-kind list,
`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:123-125`). Baseline `audit-doc-citations.py --scope` on this
map and `trade-ai/`: 0 HIGH before the edits.

### Findings

| # | Sev | Finding (evidence) | Status |
|---|---|---|---|
| A1 | HIGH | **AI sells could never settle.** `ai-bidding` §2 filed buys at the cheapest hub and sells at the dearest, but exchange payment is barter **at one hub, one pool** — a sell with no buy there delivers nothing (`exchange/spec-settlement-payment.md` §2, `order.sell-no-counter-leg`) and a sell is capped by the trader's pass-start consignment at that hub (`exchange/spec-order-book.md` §Design 6). No AI surplus would ever leave its stock | **Fixed:** `ai-bidding` §2a builds the plan per hub from pairing pools; `ai-logistics` §1 routes goods into the foreign hub's consignment; criterion 1a |
| A2 | MED | **Flat policy-order bound against a scaling empire.** `trade.maxPolicyOrdersPerTurn` capped policy orders at a constant while legitimate `order-set`/`route-set` counts grow with hubs, goods and sectors — a flat rate facing a scaling sink (ssot-power-scale PS-8) | **Fixed:** bound = base + per-owned-sector term, plus a duplicate-key throw (`ai-spend-limit` §1) |
| A3 | MED | **Flat AI build pace.** `trade.build.maxPerTurn = 1` let an AI of any size build one trade building a turn while the player builds with every legion — an unstated AI handicap (umbrella invariant 11) | **Fixed:** a share of idle legions, at least one (`ai-trade-buildings` §4) |
| A4 | MED | **A criterion tested a mechanism that does not exist.** `ai-spend-limit` criterion 6 said the AI limit bounds value leaving an AI hub when a player trades there; a hub owner files nothing at its own hub (`order.own-hub`), so that flow is `exchange`'s (capacity, need reserve) | **Fixed:** criterion re-pointed; the AI-only nature of the limit stated |
| A5 | LOW | `counter-offer-articles` criterion 3 ("a band or a shortfall") could not be met by the round-4 `Building` or `OutOfVocabulary` refusals | **Fixed** |
| A6 | LOW | `deal-valuation` criterion 5 asserted exact split additivity inside a step | **Fixed:** on step boundaries |
| A7 | LOW | `interdiction` `share` divided by the total believed flow with no zero guard, and divided before scaling to per-mille | **Fixed** |
| A8 | LOW | `AiPolicyOrderKinds` omitted `bank-hold` (`logistics-flow/spec-auto-banking.md` §2a), an entity-less policy kind the AI files for its Treasury hold | **Fixed** |
| A9 | LOW | T-A12 filed in *Round 5* but missing from the asks table; `ai-treaty-policy` acceptance numbered out of order; franchise names in new prose | **Fixed** |

**Checked and sound (no change):** one valuation (`deal-valuation` over `goods-valuation` × need — not a
second valuation function); AI decisions deterministic (pure over `(view, deal)`, ordinal tie-breaks,
named seed streams, replay never re-runs a policy); `World/Ai/` stays `WorldState`-free; no private
`f(level)`; the power roll-up is read, never a contest term; policy-only keys live in `ai.v3.json`
(TC5); closed vocabularies pinned with reasons.

### Violations this map cannot fix (other owners)

| # | Owner | Violation | Fix |
|---|---|---|---|
| A-X1 (**decided by principle, round 6; ask T-A13 filed**) | `counterparties` `trade-difficulty-knobs`, `empire-roster` | `difficulty.<profileId>.{aiBidAggressionMilli,aiMaxSpendPerTurnMilli}` and `personality.<policyId>.*` are **policy-only** reads but are placed in the **step-read** `data/tuning/trade.v1.json`, whose version enters every world stamp — so retuning AI appetite refuses replay of every trade world for nothing, the exact defect TC5 moved this map's own keys out of `trade.v1.json` to avoid | **AI-only settings move to `ai.v3.json`** (the Tunables section states the rule and this map now reads them there). The keys' file is `counterparties`', so it is ask **T-A13**; nothing here duplicates a key while the move lands |
| A-X2 | `legion-build` / `fleet` | T-A2 (identify a legion on a trade standing order from state, for the ladder skip) is still open | Land it with `standing-orders`; `ai-logistics` cannot start before it |

### Owner questions

None. A2 and A3 are corrections by the caps rule and invariant 11, not preferences; A-X1 is a
program-to-program fix by TC5's own reasoning.

---

## Round 6 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 6* (binding) and the global-audit items this
cluster owed. Where this section disagrees with anything above, it wins; each change is in the named spec.

| Ruling / finding | Change in this cluster | Where |
|---|---|---|
| **C1** — one capability flag and one ruleset bump **per wave** | **Corrected 2026-09-20 (reconciliation R-6): this cluster is not bump-free.** Nine of its ten modules are policies that run outside `Step` (replay never re-runs one, `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`), grant no flag and take no bump — they **read** the flags `world-stamp` grants (T-A8) and file nothing a flag does not allow, which is TC6. But `trade-intel` hashes faction belief **inside** `Step` and appends two conditional `WorldCanonical` row kinds (`intel-quote`, `intel-flow`), so a world stamped at an earlier wave would start emitting canonical rows it did not emit before — the R1 breach. So **wave 19a registers `trade.intel` and takes the cluster's one bump**, and the rest of row 19 registers nothing. The earlier sentence here (*"this cluster takes no `RulesetVersion` bump at all"*) is withdrawn. Each spec names its wave, because the family's landing order is one document and a policy must not file for behaviour a later wave will add | [trade-ai/spec-trade-intel.md](trade-ai/spec-trade-intel.md) §Hard edges (the open bump question this answers); [spec-ai-spend-limit.md](trade-ai/spec-ai-spend-limit.md), [spec-deal-valuation.md](trade-ai/spec-deal-valuation.md), [spec-interdiction.md](trade-ai/spec-interdiction.md), [spec-ai-trade-buildings.md](trade-ai/spec-ai-trade-buildings.md) Hard edges; [landing-order.md](landing-order.md) §2 row 19a, §10 R-6 |
| **Q-A** — war inside a treaty's minimum term also writes `treaty.broken` | `ai-treaty-policy`'s **War** step now subtracts the **same** `treaty.broken` cost its **End** step pays, per treaty still inside its term — one number (`trade.valuation.treatyBrokenWeightMilli`) for every early exit, so no policy can score better by declaring war than by ending a treaty. `deal-valuation` says the same on the pricing side. No new command, no war-specific term | [spec-ai-treaty-policy.md](trade-ai/spec-ai-treaty-policy.md) §the step table; spec-deal-valuation §Horizon |
| **CQ2** — legion equipment and doctrine upkeep may draw banked goods, symmetric | This is the recurring **drain** the audit's CA2/CQ2 said an AI treasury lacked, and it needs nothing AI-specific here: the draw is `legion-build`'s, the same rule for the player, so `ai-spend-limit`'s income read (*"what its treasury banked last turn"*) simply sees a treasury that is spent as well as filled. **No handicap key, no AI-only upkeep** — option (b) of CQ2 was declined by the owner for exactly that reason | [spec-ai-spend-limit.md](trade-ai/spec-ai-spend-limit.md) (income read unchanged); `legion-build/spec-legion-equipment.md` §7a, `spec-legion-doctrine.md` §3a |
| **C3** — banking waits on the save-identity re-key | `ai-spend-limit`'s income is *"what its treasury banked last turn"*, so the **limit** is inert until banking lands (`banking-fact` → `material-ledger` → `solid-enforcement` SE4.12–SE4.38). Stated default, already in the spec: *"an AI that banked nothing last turn files no buys; it can still sell"* — that is the correct pre-banking behaviour, not a bug to work around with a second income source | spec-ai-spend-limit §Zero income, zero buys |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | Every building read here is `SectorFeatures.TierOf` / `FactionTier` through `trade-intel`'s `OwnFeatureTier`, so the rule is read, never re-derived; `ai-trade-buildings` says so where it lists blocked plans, and a building that counts for nobody correctly reads as a blocked plan the AI answers with a `build` | [spec-trade-intel.md](trade-ai/spec-trade-intel.md) §the projection table; [spec-ai-trade-buildings.md](trade-ai/spec-ai-trade-buildings.md) §2, Boundaries |
| **C2** — one neutral `StructureKind.Feature`; `Exchange` withdrawn | Nothing here reads a kind (round 5 X1 already), and C2 confirms it. It matters for a different reason: until C2 **no feature row could load**, so every `TierOf` answered 0 and this cluster's builds would have changed nothing | spec-trade-intel; spec-ai-trade-buildings §2 |
| **D2** — six `world.*` channels compose in ActorHub and roll up like `legion-power` | Force estimates read the roll-up (`legion-power`, round 5 X7) and, when a plan needs carry, march or sight, the same module's `world.*` roll-up — through the **same** view ask, not a second one. T-A10 is extended rather than duplicated; nothing here computes a channel | T-A10; spec-ai-treaty-policy §Scores; spec-ai-trade-buildings Hard edges |
| **L6** — the Standard Hall | Not in this cluster's ladder list: forging standards is `legion-build`'s and no AI standard policy is specced in this family. If a future AI plan reports it blocked, it enters through the **same** blocked-plan table and the same `TierOf` read — never a new check | spec-ai-trade-buildings Hard edges |
| **M8 / A-X1** (global audit, owed) — one creator per versioned tuning file; AI-only settings in `ai.v3.json` | `ai.v3.json` has **one creator**: `ai-spend-limit` (wave 1; its structural bounds gate every other module's filing), which carries the loader switch (`gk-core/src/FusionRpg.Server/Program.cs:234`); `deal-valuation` and `interdiction` publish `v{n+1}` and claim no switch — three specs claimed it and only the first lander could have had it. `trade.v{n}.json` is `trade-foundation` `economy-report`'s to create. And the **rule** is stated once: a policy-only key lives in `ai.v{n}.json` (never step-read, so retuning appetite moves no stamp); a `Step`-read key lives in `trade.v{n}.json`. By it, `difficulty.<profileId>.*` and `personality.<policyId>.*` move to `ai.v3.json` — filed as **T-A13** because the keys' file is `counterparties`' — while `intel.quoteBandEdgesMilli` / `intel.flowBandEdges` stay step-read, because the intel memory they band is hashed state | §Tunables; spec-ai-spend-limit, spec-deal-valuation, spec-interdiction Hard edges; T-A13; A-X1 |

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, minor table), this
map and every spec edited · `[x]` Verified against code: `gk-core/src/FusionRpg.Server/Program.cs:245` (the literal AI tuning file name),
`WorldAiCommitTests.cs:136` (replay never re-runs a policy) · `[x]` citation audit run on every edited file ·
`[ ]` no suite run (documents only) · `[~]` session boundary: the caller's fence (this map, `trade-ai/**` and
the other named trees; `counterparties/**` read-only, which is why T-A13 is an ask, not an edit) ·
`[x]` corrections propagated (§Tunables, T-A10, A-X1) · `[x]` no population pinned · `[x]` no cap added
(the policy-order bound stays base + per-sector, the spend limit a per-turn rate) · `[x]` no AI handicap
introduced (CQ2 is symmetric by construction, invariant 11) · `[x]` no second valuation, no private
`f(level)`, no second building check.

# Capability map: `trade-stories`

**Status: APPROVED 2026-09-19.** Owner decisions recorded in §0. **Reconciled with the round-4 owner
decisions ([decisions-round-4.md](decisions-round-4.md)) on 2026-09-19** — see §12; where older text here
disagrees with §12, §12 and the register win. Module specs are written at
`docs/architecture/trade-network/trade-stories/spec-<module-id>.md` (all ten, 2026-09-19); plan and task list at
`tasks/trade-stories-plan.md` (new) · `tasks/trade-stories-todo.md` (new), the prefixed pair. The bare
`tasks/plan.md` / `tasks/todo.md` pair belongs to another stream and is never a fallback.

**Umbrella:** [trade-network-ideal.md](../trade-network-ideal.md) sub-program 9, `trade-stories`
(§11 row 9: *"Trade facts as storylet triggers (shortages, raids, requests, lost caravans), seasonal
demand shocks, escort and ransom quests, failure branches — through the `npc-story-events` engine"*),
plus §14b (story facts written at once; failure-branch questline; no second storylet generator).
**Engine it depends on:** [npc-story-events-map.md](../npc-story-events-map.md) (draft, awaiting
approval). **Content supply:** [narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.1–§6.2 and
[narrative-seed-map.md](../narrative-seed-map.md).
**Session record:** `tasks/sessions/trade-network-idea-20260919.json` (its `paths` include
`docs/architecture/trade-network/**`).

---

## 0. Owner decisions (2026-09-19, with approval)

Recorded identically in [trade-surface-map.md](trade-surface-map.md) §0. OD-3, OD-4 and OD-5 bind this
map; OD-1, OD-2 and OD-6 bind trade-surface and are listed for completeness.

| # | Decision | Where it lands |
|---|---|---|
| OD-1 | Treaties get a new "Diplomacy" rail layer, unlocked at first contact; needs an IA and `decisions.md` amendment, **listed as a requirement, not made** | trade-surface `treaty-screen`, `trade-unlock` |
| OD-2 | A seventh "flow" lens, as a reviewed widening of the closed lens set | trade-surface `flow-lens` |
| OD-3 | **narrative-seed owns the list of storylet host kinds.** Trade host kinds are rows in `storylet-vocab`'s `host-kinds.v1.json`; the runtime reads that file. Closes contradiction 1 | [spec-trade-hosts.md](trade-stories/spec-trade-hosts.md), [spec-trade-storylet-supply.md](trade-stories/spec-trade-storylet-supply.md) |
| OD-4 | **`trade-fact-source` registers into `counterparties`' `relation-facts` projection** (the `ICommitFactProjector` seam, projector id `trade-story`). Closes counterparties C5 | [spec-trade-fact-source.md](trade-stories/spec-trade-fact-source.md) |
| OD-5 | **Event frequency gets a per-empire budget in the one selection engine** — a request to npc-story-events `storylet-selection`, **recorded as decided**. Closes contradiction 2 | [spec-trade-story-pacing.md](trade-stories/spec-trade-story-pacing.md) |
| OD-6 | The first-throttle contradiction is resolved by naming the throttle's source in the spec | trade-surface `trade-unlock` §Design 3 |

## 1. What this sub-program is — and what it is not

Trade makes things happen that are worth a story: a warehouse overflowing, a caravan that never
arrived, a lane cut with goods stranded on it, a price that doubled, a treaty broken, a clan asking for
what it lacks. This sub-program turns those into **facts** the one storylet engine can read, gives
trade places the right to **host** a storylet, bounds how often trade stories fire, and wires trade
into quests and failure branches.

**It owns only facts, hosts and quest wiring.** It is not:

- **a storylet generator.** Storylet **rows** come from narrative-seed's `narrative` adapter
  (`narrative-seed-ideal.md` §6.1: one storylet generator for every place; ideal §14b: *"trade
  storylets are rows the `narrative` adapter emits; trade supplies facts and hosts"*). This map files
  coverage and registry asks on that program; it never authors or edits a row.
- **a storylet engine.** Selection, cooldown mechanics, pity, casting and outcome routing are
  npc-story-events' (`storylet-selection`, `choice-resolution`, `outcome-routing`). A trade deck is the
  dual-engine defect SOLID forbids (npc-story-events principle 11).
- **a second relation ladder, request generator or push path.** Relation is npc-story-events'
  `relation-ledger`; clan requests are its `petition-host`; pushes go through notification-ssot.
- **a mechanism for prices or flow.** A storylet never sets a price or moves goods directly; any goods
  or souls a storylet exchanges settle through `exchange`'s order path (§3 principle 6).

## 2. Which loop it extends

From [the-loops.md](../../guide/the-loops.md): **Loop 7 — Quests and events** (primary: *"delve
quests, world events and raids"*), **Place 3 — Farm, hunt, defend** (failure branches: a lost hub opens
a questline), **Place 4 — World map** (caravans, interception, escort) and **Place 5 — World stage**
(a hub has a face). World clock only; every cooldown and expiry counts world turns. No fourth clock, no
real-calendar timer.

## 3. Principles restated (binding on every module)

1. **RPG layer only; standalone-first.** Every trade fact, host and quest runs with the game closed and
   never reads PvZ. Objectives count mode-agnostic facts.
2. **React to past facts.** A storylet reacts to a committed fact; firing one turn late is correct.
3. **One engine, many hosts; a host decides when, never which or what it pays**
   (npc-story-events-ideal §6.2; its map, locked assumption 1).
4. **One relation ladder** — the four-band disposition ladder `eager, open, wary, hostile`
   (`gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`), derived from facts, never moved by time
   (trade-network principle 11; npc ruling R4).
5. **Every faucet names its sink.** A trade storylet pays out of its host's existing budget, never on
   top of it (npc-story-events-ideal §11 item 1), through existing grant paths with a dedupe key from a
   durable fact id. **No trade path increases souls** (trade-network principle 8): a storylet may take
   souls as payment; it never pays them out of trade.
6. **One price, one flow.** Prices are `exchange`'s, flows `logistics-flow`'s. A storylet outcome that
   buys, sells or ransoms goods files an order that settles through `exchange` at the value index; it
   never names a price of its own.
7. **Determinism.** Trade facts derive from hashed world state and committed records; rolls use
   `WorldSeed.DeriveRollSeed` with a named stream per purpose (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`),
   never `System.Random` or the wall clock.
8. **The balance surface is data.** Cooldowns, quiet weights, quotas and shock rates live in
   `gk-core/data/tuning/narrative.v1.json` (new, npc-story-events' file) or `data/tuning/trade.v1.json` (new),
   published through `gk-core/tools/tuning/publish.py`. Pacing limits are structural and say so in a comment.
9. **Generated data is never hand-edited.** A defect in a trade storylet is fixed in narrative-seed's
   generator and regenerated.
10. **A guardrail validates the contract.** Closed vocabularies (fact kinds, host kinds, leaves,
    objective templates) are pinned as declarations; storylet counts, pick rates and fire counts are
    readings, never assertions.
11. **No recurring antagonist** (npc ruling R13). An interceptor who beat your caravan does not grow,
    rank or remember you; antagonist memory is faction- and world-level only.
12. **No actor numbers.** Trade stories grant access, goods and quests, never stats. Any timed boon is
    an atom container at an `OwnerScope` through npc's outcome routing.

## 4. Locked assumptions (correct before approving)

1. The npc-story-events map's module ids are stable (`narrative-vocabulary`, `story-ledger`,
   `relation-ledger`, `narrative-predicates`, `storylet-selection`, `quest-sources`,
   `outcome-routing`, `world-events-host`, `petition-host`, `failure-branches`). This map depends on
   them by name; if that map changes an id, this map follows.
2. **Trade story facts are projections, not a second truth.** The source of each fact stays with its
   producer (`logistics-flow`'s phase output, `exchange`'s settlement ledger, `counterparties`' treaty
   ledger, `fleet`'s caravan outcome). The story-ledger fact is keyed by the source fact's durable id,
   so it can be rebuilt and never disagrees.
3. Ledger dedupe keys carry `(save_id, empire_id, world_id, turn, factKind, sector|lane, good)`
   (trade-network-ideal §14b); the one grammar is `trade-foundation` `ledger-keys`
   ([spec-ledger-keys.md](trade-foundation/spec-ledger-keys.md) §1–§2, `sector` widened to a holder).
   Story-ledger `source_ref`s are this sub-program's (`trade-fact-kinds` §3) and must be unique per
   fact, including across years (audit 2026-09-20).

## 5. What exists (verified against code, 2026-09-19)

### Built

| What | Evidence |
|---|---|
| An event engine with repeat scopes, pity and preflight (Delve-only today) | `gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:93-129` (repeat scopes validated); `EventFilters.cs:76,123` (`ByRepeatScope`); `EventDeck.cs:252` (`UnknownPity.Resolve`) |
| A world `Events` phase that rolls the calendar and reports seasons | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:341-366`; season change reported at `:363` |
| A deterministic season function | `gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:42` (`SeasonOf(turn)`), `:44-46` (`Roll`) |
| Turn report lines with sector and audience for fog | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` (five kinds), `:31` (`SectorId`, `Audience`); fog filter `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-587` |
| Detail-prefix report lines as the event idiom | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:113` (`supply.besieged:`) |
| A closed predicate leaf enum and a predicate compiler | `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46` (`LeafId`); `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs` |
| A quest engine over closed objective templates | `gk-core/src/FusionRpg.Core/Delve/Quests/QuestRow.cs:7-25` (template instance, never a new mechanism); `QuestProgress.cs:30` (only fact source is a `DelveReport`) |
| The cache left by a dead legion, and the verb that claims it | `docs/architecture/scoped-inventory-hierarchy/spec-cargo-fate.md` §Design 1 (a dead legion's cargo becomes a revisit-lootable cache); `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:119` (`claim-cache`) |
| Lane and slot kinds a host can attach to | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7,18` (`SlotKind.Market`); `gk-core/src/FusionRpg.Core/World/WorldState.cs:257-260` (lane `Width`, `WardLevel`) |

### Wiring gap (exists, inert — not a wall)

| What | Where | Closed by |
|---|---|---|
| The event engine has no production caller and lives under `Delve/` | npc-story-events map, cross-program table (`EventDeck.cs:146,218,339` referenced only inside `Delve/` and tests) | npc-story-events `storylet-reseam` |
| `WorldEntityKind.Caravan` is declared and never constructed; the trade umbrella retires it (caravans are legions) | `gk-core/src/FusionRpg.Core/World/WorldState.cs:66`; trade-network-ideal §8.3 | `fleet` (retirement); hosts here key on the legion's standing order, never on that kind |
| Clans have no policy and needs are uniform, so no clan request can be computed | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18`; `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31` | `counterparties` (needs) and npc `petition-host` (the request) |
| Special-week and special-month rolls exist with no effects | `TurnEngine.cs:341` (*"their effects belong to later modules"*) | `seasonal-demand-shocks` reads the season; it does not reuse the special rolls for trade (§6.7) |

### Real gap

| What | Why it matters |
|---|---|
| **No trade fact of any kind** — no trade code in `gk-core/src/FusionRpg.Core/World` | Nothing to trigger on until `logistics-flow`, `exchange`, `counterparties` and `fleet` produce records |
| **No story ledger** — npc-story-events `story-ledger` is unbuilt | Trade facts have no store to project into |
| **No escort stance** — stances are `March`, `Scout`, `Hold`, `Dowse` (`gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:22`) | Escort quests need `fleet` first |
| **No empire-scoped pulse** — npc `world-events-host` asks per sector holding a host slot | Story frequency would grow with empire size (§6.5, contradiction 2) |
| **No trade objective templates** — quest templates are Delve's closed set (`QuestRow.cs:7-25`) | Escort, deliver, recover and ransom have no template |

## 6. Modules

Stable kebab-case ids, chosen once. None is a UI module; storylet cards and the quest log are
npc-story-events' `storylet-card` / `quest-log-layer`, which go through `/idea-ui` there.

| # | Module id | Responsibility (one line) | Depends on | Wave |
|---|---|---|---|---|
| 1 | `trade-fact-kinds` | The closed vocabulary of trade story facts, their scope, dedupe key and source record | npc `narrative-vocabulary`, `story-ledger` | 1 |
| 2 | `trade-fact-source` | Projects committed trade records into story-ledger facts in the same commit as the turn | `trade-fact-kinds`; producers in `logistics-flow`, `exchange`, `counterparties`, `fleet` | 2 |
| 3 | `trade-hosts` | Host kinds `trade-hub`, `depot`, `trade-lane`, `trade-turn` and their host adapters | `trade-fact-kinds`; npc `storylet-reseam`, `world-events-host` | 2 |
| 4 | `trade-predicates` | Trade leaves for storylet eligibility, each a reviewed `LeafId` addition | `trade-fact-kinds`; npc `narrative-predicates` | 2 |
| 5 | `trade-story-pacing` | Rate limits in data: cooldowns, quiet weight, per-host quotas, an empire budget independent of empire size | `trade-hosts`; npc `storylet-selection` | 3 |
| 6 | `trade-trigger-reachability` | Every fact kind and leaf provably reachable through real commands; preflight refuses unreachable trade eligibility | `trade-fact-source`, `trade-predicates` | 3 |
| 7 | `seasonal-demand-shocks` | Deterministic seasonal demand shocks fed to the one demand function, announced as facts | `trade-fact-kinds`; `counterparties`, `exchange` | 3 |
| 8 | `trade-quests` | Escort, deliver, recover and ransom objective templates and their world fact source | `trade-fact-source`; npc `quest-sources`, `outcome-routing`; `fleet` | 4 |
| 9 | `trade-failure-branches` | Lost hub, depot or route as failure facts that open a questline; no second penalty | `trade-fact-source`; npc `failure-branches` | 4 |
| 10 | `trade-storylet-supply` | The registry and coverage asks on narrative-seed so trade hosts receive rows from the `narrative` adapter | `trade-hosts`, `trade-predicates`; narrative-seed `storylet-vocab`, `token-grammar`, `narrative-planner` | 2 |

### 6.1 `trade-fact-kinds`

**Capability.** The closed, reviewed list of trade story facts, each with its scope (world, because trade
happens on a map and a fact about a hub, lane or sector means nothing off it — ~~because trade dies with the
map~~, retired wording: worlds do not end, they become `developing`, `hibernating`, `idle` or `fallen` and stay
revisitable, and goods cross only over a `rift-trade` route, round 6 S2), its dedupe key (§4 item 3), the
durable source record it projects, and its audience (whose story it is). Initial set, from the request and ideal §6
lesson 5 / §14b:

| Fact kind | Source record (owner) |
|---|---|
| `trade.warehouse.full` | production halt at a full warehouse (`sector-yield`) |
| `trade.delivery.wasted` | overflow waste of a delivery (`sector-yield` / `logistics-flow`) |
| `trade.lane.cut-stranded` | goods stranded in a cut lane's transit buffer (`logistics-flow`) |
| `trade.caravan.lost` | a trade legion destroyed; cargo to a cache (`fleet`, `cargo-fate`) |
| `trade.caravan.intercepted` | a trade legion fought on its route (`fleet`, battle seam `Lane`/`Sector`) |
| `trade.price.spike` / `trade.price.crash` | a hub price crossing a band edge (`exchange`) |
| `trade.treaty.signed` / `trade.treaty.broken` / `trade.embargo.imposed` | treaty ledger (`counterparties`) |
| `trade.clan-request.opened` | a clan petition opened (npc `petition-host`) |
| `trade.hub.lost` / `trade.depot.lost` | a sector with a trade structure changing hands (claim resolution) |
| `trade.demand.shock` | a seasonal shock starting (`seasonal-demand-shocks`) |

The **relation band** is not a fact: it is derived by npc `relation-ledger` and read through its leaf.
Adding a kind is a reviewed change to npc-story-events' story fact vocabulary, which is closed.

**Bucket.** Real gap. **Depends on.** npc `narrative-vocabulary` (story fact kinds), `story-ledger`.
**Touches.** The story-fact registry file npc-story-events owns (row additions, reviewed).
**Acceptance.** Every kind names exactly one source record and one owner; every kind has a dedupe key
format; the list is pinned as a declaration with its reason. No kind duplicates a fact another program
already records under another name (join check against the story fact registry).
**Verification boundary.** `core-fallback` (`gk-core/scripts/verification-boundaries.v1.json`).

### 6.2 `trade-fact-source`

**Capability.** The classifier and writer: after a turn commits, read that turn's trade records and
report lines and write the matching story-ledger facts **in the same commit** as the turn, so a lane cut
or a lost caravan is a fact before any storylet reads it (ideal §14b: *"lane cuts and lost caravans
write story facts at once"*). Pure Core classification (records → fact drafts), Data-side append with
idempotent dedupe. It reads durable records other programs commit and never hooks their code (the npc
`failure-branches` rule).

**Bucket.** Real gap. Precedent built for the shape: notification-ssot's `world-notify-source` (a pure
Core classifier over committed report entries).
**Depends on.** `trade-fact-kinds`; producers' records (§6.1 table).
**Touches.** A Core classifier (trade namespace); a Data append through npc `story-ledger`'s API.
**Acceptance.** **Idempotent:** replaying a commit writes nothing new. **Complete and exact:** for a
fixture world driven through real commands, every source record of a covered kind yields exactly one
fact and no fact exists without its record (reconciliation both ways). **Fog:** a fact is written only
for the audience that can see its source line (the report visibility rule,
`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-587`, reused, never re-implemented — notification-ssot ask
A2 moves it into Core). **Hash-neutral:** writing facts moves no world state hash.
**Verification boundary.** `core-fallback` + `data-fallback`.

### 6.3 `trade-hosts`

**Capability.** The places where a trade storylet may appear, as host kinds added to the closed host
vocabulary and implemented as host adapters on npc-story-events' `IStoryletHost` seam (host kind, host
clock = world turns, seen scopes, stream name `event:<hostKind>`):

| Host kind | Where it attaches | Asks the engine |
|---|---|---|
| `trade-hub` | a sector with a trade-hub structure (ideal §7.1 — a structure row, not the `Market` slot) | in the `Events` phase, for the hub's owner and for factions with `market` access |
| `depot` | a sector with a depot structure (`convoy-depot`) | same phase, owner only |
| `trade-lane` | a lane carrying flow this turn | same phase, for factions with flow on it |
| `trade-turn` | the empire's trade as a whole, once per turn | same phase, one pulse per empire |

Each host's `Θ_content` inputs follow the SSOT formula (npc `host-content-theta`): sector `DangerBand`
for hubs and depots, the higher-danger endpoint for a lane, the empire's highest held danger for
`trade-turn`. Eligibility is fog-correct.

**Bucket.** Real gap. **Depends on.** `trade-fact-kinds`; npc `storylet-reseam` (the seam),
`world-events-host` (the `Events`-phase call site), `host-content-theta`.
**Touches.** Host adapters (trade namespace); the host-kind registry (reviewed widening — see
contradiction 1 for which program owns it).
**Acceptance.** A host decides only *when* to ask (principle 3): no adapter selects a storylet or sets
a payout (static guard: adapters reference no selection or reward type). A foreign hub never hosts for
a faction without access. One place is one host (contradiction 3). Streams are named per host kind and
never shared with a combat stream.
**Verification boundary.** `core-fallback`.

### 6.4 `trade-predicates`

**Capability.** Eligibility leaves for trade storylets, each a reviewed addition to the closed `LeafId`
enum (`PredicateNode.cs:28-46`) with a `FactReader`. Two kinds, kept apart on purpose:

- **Current-state leaves** (read hashed world state now): `WarehouseFillAtLeast` (per-mille of the
  sector's warehouse axis, a bounded ratio), `PriceBandIs` (a hub's price band for a good: spike,
  normal, crash — bands from `exchange`'s curve, never a second curve), `AccessIs` (derived access
  between viewer and counterparty: closed, passage, market, preferential — from `counterparties`),
  `TreatyIs` (an active treaty kind or embargo between viewer and counterparty).
- **Event recency** (read the story ledger): through npc-story-events' story-fact leaf with a trade fact
  kind and a turn window — **no trade-specific event leaf**, so the enum grows by state leaves only.

The relation band and "clan request open" read npc's own leaves (`relation-ledger`, `petition-host`);
trade adds no second leaf for either.

**Bucket.** Real gap. **Depends on.** `trade-fact-kinds`; npc `narrative-predicates`; providers'
state (`sector-yield`, `exchange`, `counterparties`).
**Touches.** `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs` (reviewed enum widening, owned by the
atom program's predicate grammar); readers in the trade namespace.
**Acceptance.** Each new leaf compiles through `PredicateCompiler` within the grammar's depth and node
bounds; each reader is deterministic over hashed state; a leaf that reads unhashed state inside the
step fails a guard. The added leaves are pinned as a declaration.
**Verification boundary.** `core-fallback`; the leaf enum sits in `seed-atoms-fallback`'s neighbourhood
only if generated catalogs change.

### 6.5 `trade-story-pacing`

**Capability.** How often trade stories fire, entirely in data, and **independent of empire size** —
the grand-strategy event-spam lesson (ideal §6: a size-scaling flag against event spam in large
countries). Rows in
`narrative.v1.json` (new), a trade section:

- **cooldowns** per trade storylet and per trade host kind, in world turns;
- **quiet weight** (the "no event" share) per host kind;
- **per-host quotas** — at most N trade storylets per host per window (structural pacing limit);
- **an empire budget** — at most `trade.maxStoryletsPerEmpirePerTurn` across **all** trade hosts of one
  empire, with the engine's tier order deciding which host wins. The chance that *some* trade storylet
  fires on a turn is then set by the budget and quiet weight, not by how many hubs the empire holds.

The budget is a selection rule, so it lives in the one engine: this module files the empire-scoped
pulse as an ask on npc `storylet-selection` and supplies the trade rows. It does not build a private
limiter (SOLID; contradiction 2).

**Bucket.** Real gap. **Depends on.** `trade-hosts`; npc `storylet-selection`, `narrative-vocabulary`
(the tuning loader).
**Touches.** `gk-core/data/tuning/narrative.v1.json` (new — rows), via `gk-core/tools/tuning/publish.py`.
**Acceptance.** **Size-independence:** on seeded fixture worlds identical except that one empire holds
twice the hubs, the per-turn fire count of trade storylets for that empire is bounded by the same
budget in both (a structural property, not a rate asserted to a number). **Cooldown:** a storylet never
re-fires inside its cooldown on its host clock. **Quiet:** with the quiet weight at its maximum, no
trade storylet fires. Missing tuning keys are rejected at load (tunables-ssot T5).
**Verification boundary.** `core-fallback`; the tuning file needs a mapped boundary (spec adds it).

### 6.6 `trade-trigger-reachability`

**Capability.** Proof that every trade trigger can actually happen in play. For each fact kind in
`trade-fact-kinds` and each leaf in `trade-predicates`, a fixture world driven **only by real, admitted
world commands** (never a debug fabricator — [live-probe-standard.md](../../contributing/live-probe-standard.md)
scope rule) reaches a state where the fact is written or the leaf is true, within a stated turn bound.
A preflight rule then refuses any trade storylet whose eligibility references a leaf value no fixture
reaches, so the corpus cannot contain a storylet that can never fire.

**Bucket.** Real gap. Precedent: npc-story-events' preflight rules (its map, contract checks).
**Depends on.** `trade-fact-source`, `trade-predicates`.
**Touches.** Tests and fixtures; one preflight rule filed on npc `storylet-contract`'s preflight.
**Acceptance.** Every fact kind and every leaf value has at least one reachability fixture (join closure
over the two closed vocabularies — declarations, not populations). The preflight refuses a fixture
storylet whose only condition is unreachable.
**Verification boundary.** `core-tests-fallback`.

### 6.7 `seasonal-demand-shocks`

**Capability.** Seasons move demand. At a season change (`TurnCalendar.SeasonOf`, `TurnCalendar.cs:42`;
reported at `TurnEngine.cs:363`) a deterministic roll per `(world, season, good class, climate)` from a
named stream decides which goods face a demand shock, its direction and its duration in turns. The
shock is a **term in the one demand function** `counterparties` owns (the real `INeedVector` — trade
ideal §14b: *"`counterparties` owns it"*), so prices move only through `exchange`'s curve and clan
demand, never by a storylet setting a price. The shock is announced as a `trade.demand.shock` fact and
can make trade storylets eligible (a clan short of fire essence in a cold season).

**Bucket.** Real gap. The season clock is built (§5).
**Depends on.** `trade-fact-kinds`; `counterparties` (the demand function to contribute into),
`exchange` (reads demand).
**Touches.** A Core shock schedule (trade namespace); `data/tuning/trade.v1.json` (new) keys
`shock.chanceMilli`, `shock.demandMilli`, `shock.durationTurns`; a contribution seam on the demand
function (ask on `counterparties`).
**Acceptance.** **Deterministic:** the same world seed and turn produce the same shocks. **One
mechanism:** a shock changes demand only; the price follows from the curve (a test finds no price
write outside `exchange`). **Only demand drifts:** a shock never adds stock (trade-network §7.2 — stock
that refills from nothing mints goods). **Bounded ratio:** `shock.demandMilli` is a bounded per-mille
modifier, commented as such.
**Verification boundary.** `core-fallback`.

### 6.8 `trade-quests`

**Capability.** Trade as quests, through npc-story-events' one quest engine with the world turn report
as a fact source. Four objective templates, added to the closed template registry (`QuestRow.cs:7-25`)
as a reviewed change:

| Template | Objective (mode-agnostic) | Needs |
|---|---|---|
| `escort` | a trade route delivers with no interception loss for N turns while an escort accompanies it | `fleet`'s escort stance |
| `deliver` | bank N units of a good by a turn bound, on the world clock | `logistics-flow` banking facts |
| `recover` | claim the cache a lost caravan left (`claim-cache`, `WorldCommand.cs:119`) before it decays | `cargo-fate` / `corpse-cache` |
| `ransom` | a counterparty that claimed your lost caravan's cache offers its goods back; pay through an `offer:{stock}` choice settled by `exchange` at the value index | `exchange`, `counterparties`, `cargo-fate` |

Quests are offered by storylet outcomes (`quest.offer`, npc `outcome-routing`) or by a clan petition.
Rewards come from the host's budget through existing grant paths, deduped on the quest's durable id;
expiry counts world turns; abandoning is free.

**Bucket.** Real gap. **Depends on.** `trade-fact-source`; npc `quest-sources`, `outcome-routing`;
`fleet` (escort), `exchange` (ransom settlement), scoped-inventory `cargo-fate`.
**Touches.** Quest template registry rows (reviewed); a trade objective evaluator over world facts.
**Acceptance.** **No soul faucet:** no trade quest reward path increases souls through trade (an
invariant test over every template's reward path); a ransom's souls are a sink. **Ransom never
duplicates goods:** ransomed goods leave the counterparty's stock and arrive once (reconciliation).
**Mode-agnostic:** no template reads a lawn fact. **Expiry on the world clock** only.
**Verification boundary.** `core-fallback`.

### 6.9 `trade-failure-branches`

**Capability.** Trade's failure branches (ideal §14b: *"a lost hub opens a failure-branch questline"*).
Losing a trade hub, a depot, or a route to an embargo writes or reads a failure fact (`trade.hub.lost`,
`trade.depot.lost`; for an embargo, `counterparties` `relation-facts`' own `treaty.broken` and
`trade.embargo.set` — `trade.treaty.broken` was dropped at spec time, T1) that npc `failure-branches` reads to make
priority storylets eligible: a questline to retake or replace the hub, a character who can reopen the
route, a branch place with a way back. The questline itself is an **arc** from narrative-seed's
`arc-pipeline`. Catch-up for the leader (interdiction pressing the busiest flows) is `trade-ai`'s, not
this module's.

**Bucket.** Real gap. **Depends on.** `trade-fact-source`; npc `failure-branches`, `spine-progress`
(tier order); narrative-seed arcs.
**Touches.** Failure fact rows (in `trade-fact-kinds`); arc coverage asks (in `trade-storylet-supply`).
**Acceptance.** **No second penalty:** a failure branch takes nothing the rules let the player keep
(npc-story-events-ideal §6.8); a test compares the player's stocks before and after the branch opens
and finds no debit caused by it. **Reachable:** each failure fact has a reachability fixture
(`trade-trigger-reachability`). **Priority:** an eligible branch storylet pre-empts pool storylets on
its host.
**Verification boundary.** `core-fallback`.

### 6.10 `trade-storylet-supply`

**Capability.** The contract between trade and the content generator, stated so no trade storylet is
ever written outside it. Filed on narrative-seed as asks: the four trade host kinds in the host-kind
registry; any runtime slot tokens trade needs beyond the closed set `{place}`, `{supply}`, `{reward}`,
`{cost}` (candidates `{good}`, `{route}`, `{counterparty}` — each a reviewed widening of
`token-grammar`, or mapped onto existing slots if the grammar owner prefers); coverage cells host kind ×
storylet kind × climate for the planner; choice patterns that use `offer`, `fight` and `bring`; the
trade roles already in the closed role list (`trader`, `envoy`, `clan elder` — npc-story-events-ideal
§6.3). The rows themselves are emitted, validated and regenerated by the `narrative` adapter.

**Bucket.** Real gap (no trade host in any registry). **Depends on.** `trade-hosts`,
`trade-predicates`; narrative-seed `storylet-vocab`, `token-grammar`, `narrative-planner`.
**Touches.** Asks only; no seed file is written by this sub-program.
**Acceptance.** Every trade host kind has at least one coverage cell in the planner's budget file (a
join, not a count). No file under `gk-data/packs/fusion/data/seed/narrative/**` is authored or edited by this sub-program
(guard: its specs' paths never include that tree).
**Verification boundary.** narrative-seed's seedsmith tests; `docs-and-assistant-config` for this map.

## 7. Dependency direction and build order

One way, no cycles.

```text
npc-story-events: narrative-vocabulary · story-ledger · storylet-reseam · narrative-predicates
                  storylet-selection · quest-sources · outcome-routing · failure-branches · world-events-host
producers:        sector-yield · logistics-flow · exchange · counterparties · fleet
        │
  trade-fact-kinds
        ├── trade-fact-source ──┬── trade-trigger-reachability
        ├── trade-hosts ────────┼── trade-story-pacing
        ├── trade-predicates ───┘
        ├── seasonal-demand-shocks
        ├── trade-storylet-supply (after hosts + predicates)
        ├── trade-quests (after trade-fact-source)
        └── trade-failure-branches (after trade-fact-source)
```

```text
Wave 1  trade-fact-kinds                                   (after npc story-ledger's fact registry exists)
Wave 2  trade-fact-source ∥ trade-hosts ∥ trade-predicates ∥ trade-storylet-supply
Wave 3  trade-story-pacing ∥ trade-trigger-reachability ∥ seasonal-demand-shocks
Wave 4  trade-quests ∥ trade-failure-branches
```

**Why this order.** The umbrella puts `trade-stories` last (ideal §11: "9 comes last"), after the
producers (4–7) exist, because a fact with no source is a fixture, not a story. Within the sub-program,
facts come before hosts and leaves because both read them; the content asks go out in wave 2 so the
generator's cycle runs in parallel with pacing and reachability; quests and failure branches come last
because they route through npc's outcome and quest modules, which are that program's wave 3.

## 8. Cross-program asks

| Ask | Owning program / module | Blocks | Default if unanswered |
|---|---|---|---|
| Trade story fact kinds in the closed story fact vocabulary | npc-story-events `narrative-vocabulary` / `story-ledger` | `trade-fact-kinds` | None |
| A per-empire budget per budget group in selection — **decided (OD-5)** | npc-story-events `storylet-selection` | `trade-story-pacing` | None — decided; the earlier fallback (fire only through `trade-turn`) is retired |
| Drop `Market` from `world-events-host`'s host slots, or name `trade-hub` its trade specialisation | npc-story-events `world-events-host` | `trade-hosts` | None — two hosts on one place double-fire |
| Trade host kinds (**narrative-seed owns the list, OD-3**), slot tokens, coverage cells, choice patterns | narrative-seed `storylet-vocab`, `token-grammar`, `narrative-planner` | `trade-hosts`, `trade-storylet-supply` | None |
| Register `trade-story` into the commit-time projection seam — **decided (OD-4)** | `counterparties` `relation-facts` | `trade-fact-source` | None |
| One generic story-fact recency leaf `StoryFactWithin` | npc-story-events `narrative-predicates` | `trade-predicates` (recency), `trade-failure-branches` | Trade storylets react to trade facts through flags set by outcomes only |
| `lane` and `legion` subject kinds in the story ledger | npc-story-events `story-ledger` | `trade-fact-kinds` | None |
| Four quest templates in the closed registry | npc-story-events `quest-sources` (template registry) | `trade-quests` | None |
| A demand contribution seam | `counterparties` | `seasonal-demand-shocks` | None |
| Producer records with durable ids (halt, waste, strand, loss, price band crossing, treaty facts, caravan outcomes) | `sector-yield`, `logistics-flow`, `exchange`, `counterparties`, `fleet` | `trade-fact-source` | None |
| An escort stance | `legion-build` `escort-stance` (consumed by `fleet` `escort-link`; corrected by the 2026-09-20 audit — `fleet` does not own the stance, trade-surface S2) | `trade-quests` (`escort` only) | `escort` template ships later; the other three do not wait |
| New `LeafId` members | atom program predicate grammar (`effect-atom/definitions.md` §3) with npc `narrative-predicates` | `trade-predicates` | None |
| Correct `spec-narrative-vocabulary.md` §2 ("members defined by the runtime") to OD-3 | npc-story-events `narrative-vocabulary` | none (text) | — |
| **Round 4:** an outcome kind that files a **one-off deal offer** (`offer.made` through `exchange` `treaty-lifecycle`) on the host faction's behalf, so a ransom storylet can offer goods back | npc-story-events `outcome-routing` | `trade-quests` (`trade-ransom` only) | `trade-ransom` ships later; the other three templates do not wait |

## 9. Owner questions (genuinely open)

**None.** The shapes above follow from locked rules: one engine, one ladder, one price, facts as
projections, rows from the adapter. Numbers are tunables set by principle at spec. The one decision
with a cost trade-off — how the relation band enters the hashed world step (contradiction 4) — belongs
to the `counterparties` and npc-story-events specs, not to the owner, unless those two disagree.

## 10. Contradictions and tensions found

1. **Two programs claim the host-kind vocabulary.** narrative-seed's `storylet-vocab` lists "host
   kinds" among its closed registries ([narrative-seed-map.md](../narrative-seed-map.md) §4 row 5), and
   npc-story-events' `narrative-vocabulary` lists host kinds among its **runtime-only** vocabularies
   ([npc-story-events-map.md](../npc-story-events-map.md) §Modules row 1). A seed's `hosts[]` must
   validate against the same list the runtime dispatches on, so one file must own it. Recommendation:
   narrative-seed's registry, read by the runtime (the pattern that map already uses for roles and choice
   kinds). Until resolved, `trade-hosts` cannot say where its rows go.
   **Resolved (OD-3):** narrative-seed owns the list; the runtime reads the same file.
2. **Story frequency scales with empire size.** npc `world-events-host` asks per sector holding a host
   slot, so a larger empire gets more events per turn — the event-spam failure trade-network §6
   cites. `trade-story-pacing` needs an empire-scoped budget in the one selection engine (§8 ask).
   **Resolved (OD-5):** a per-empire budget per budget group in the one selection engine (`trade-story-pacing`).
3. **One place, two hosts.** npc `world-events-host` lists the `Market` slot as a host; this map's
   `trade-hub` host sits on the same kind of place (the preferred trade-hub site is the Market slot,
   trade-network §7.1). Without a rule, a Market-slot hub asks the engine twice per turn.
   **Resolved in [spec-trade-hosts.md](trade-stories/spec-trade-hosts.md) §3:** a Market-slot sector with an
   active hub is hosted by `world.trade-hub` only; `world-events-host` skips `world.market` there (ask filed).
4. **The relation band is not hashed.** trade-network §14b requires disposition facts read inside `step`
   to be world-hashed or logged step inputs; npc `relation-ledger` derives the band from the Data-side
   story ledger. `AccessIs` and `counterparties`' treaty acceptance both read the band. The two programs
   must agree how the band enters the step before either spec is written. (Also recorded in
   [trade-surface-map.md](trade-surface-map.md) §10.)
   **Resolved by [counterparties-map.md](counterparties-map.md) assumption 3 / C4:** the band a turn uses is a
   logged step input; `AccessIs` reads `exchange` `trade-access` (C6), which reads that snapshot.
5. **Citation drift in the npc-story-events ideal:** it cites `WorldEntityKind.Caravan` at
   `WorldState.cs:61`; the member is at `gk-core/src/FusionRpg.Core/World/WorldState.cs:66` (the enum opens at
   `:61`). Not in this session's fence; noted for that program.

## 10a. Spec-time corrections (2026-09-19)

| # | Map text | Correction | Spec |
|---|---|---|---|
| T1 | §6.1 lists `trade.treaty.broken` and `trade.clan-request.opened` | Dropped: `relation-facts` already emits `treaty.broken`; npc `petition-host` owns petitions. `trade.embargo.imposed` becomes `trade.embargo.set` (the diplomacy fact's name). Twelve kinds | [spec-trade-fact-kinds.md](trade-stories/spec-trade-fact-kinds.md) |
| T2 | §6.4 `AccessIs` reads `counterparties` | `AccessIs` reads `exchange` `trade-access`; `TreatyIs` reads `counterparties` `diplomacy-facts` (counterparties C6) | [spec-trade-predicates.md](trade-stories/spec-trade-predicates.md) |
| T3 | §6.4 event recency through "npc's story-fact leaf" | npc's six leaves include no recency leaf; one generic `StoryFactWithin` is requested on `narrative-predicates` | same |
| T4 | §6.3 host kinds `trade-hub`, `depot`, `trade-lane`, `trade-turn` | Registry ids follow its `place.kind` grammar: `world.trade-hub`, `world.depot`, `world.trade-lane`, `world.trade-turn` | [spec-trade-hosts.md](trade-stories/spec-trade-hosts.md) |
| T5 | §6.8 templates `escort`, `deliver`, `recover`, `ransom` | Prefixed `trade-` to avoid collisions in the shared quest-objective registry | [spec-trade-quests.md](trade-stories/spec-trade-quests.md) |
| T6 | §6.2 classifier and Data append | Registered as `ICommitFactProjector` `trade-story` in `relation-facts`' `CommitFactProjection` (OD-4) | [spec-trade-fact-source.md](trade-stories/spec-trade-fact-source.md) |
| T7 | §6.1 caravan facts' source | `fleet` `interception` emits `caravan.intercepted` / `caravan.lost` (`FleetFacts`); the cache id comes from `goods-cargo-fate` | [spec-trade-fact-kinds.md](trade-stories/spec-trade-fact-kinds.md) |
| T8 | §6.3 `trade-hub` on an `exchange`-role structure, `depot` on a `convoy-depot` | **Round 4:** hosts attach by sector feature — `trade` tier ≥ 1 (Trading Post … Grand Exchange) and `caravans` tier ≥ 1 (Caravan Yard, Convoy Depot) — through `trade-foundation` `sector-features`; hub fog reads `LevelAt` | [spec-trade-hosts.md](trade-stories/spec-trade-hosts.md) |
| T9 | §6.1 `trade.hub.lost` / `trade.depot.lost` keyed by role / row | Keyed by feature and tier | [spec-trade-fact-kinds.md](trade-stories/spec-trade-fact-kinds.md) |
| T10 | §6.4 `AccessIs` | Reads `EffectiveLevel` (the building gate), so "market access to this clan" needs the viewer's Trading Post | [spec-trade-predicates.md](trade-stories/spec-trade-predicates.md) |
| T11 | §6.8 `recover`: *"claim the cache … (`claim-cache`)"* | A goods cache is claimed by presence; the objective reads `goods-cache.claimed` (fleet ask A10 / C13) | [spec-trade-quests.md](trade-stories/spec-trade-quests.md) |
| T12 | §6.8 `ransom`: *"settled by `exchange` at the value index"* through an order | An order walks the curve; the ransom is a one-off deal leg (`exchange` `settlement-payment` §7), gated by `LevelAt` | [spec-trade-quests.md](trade-stories/spec-trade-quests.md) |
| T13 | exchange E-A9 (a band-raising storylet for the first clan market) | Superseded by round 4: reachability of "build a Trading Post, fill a clan order" | [spec-trade-trigger-reachability.md](trade-stories/spec-trade-trigger-reachability.md) §2a |

**Spec index:** [trade-fact-kinds](trade-stories/spec-trade-fact-kinds.md) · [trade-fact-source](trade-stories/spec-trade-fact-source.md) ·
[trade-hosts](trade-stories/spec-trade-hosts.md) · [trade-predicates](trade-stories/spec-trade-predicates.md) ·
[trade-story-pacing](trade-stories/spec-trade-story-pacing.md) · [trade-trigger-reachability](trade-stories/spec-trade-trigger-reachability.md) ·
[seasonal-demand-shocks](trade-stories/spec-seasonal-demand-shocks.md) · [trade-quests](trade-stories/spec-trade-quests.md) ·
[trade-failure-branches](trade-stories/spec-trade-failure-branches.md) · [trade-storylet-supply](trade-stories/spec-trade-storylet-supply.md).

## 11. DESIGN-GATE §5 checklist

```
[x] Subsystems identified: world turn engine (Events phase, report), storylet engine and story ledger
    (npc-story-events), narrative-seed generator, predicates (atom grammar), quests, economy (trade
    stocks, souls invariant), scoped-inventory cargo-fate, notification (none directly).
[x] Session boundary: tasks/sessions/trade-network-idea-20260919.json lists docs/architecture/
    trade-network/** in its paths. session-boundary-check.py not re-run in this docs-only sub-task.
[~] §1 rows read this session: Economy row via trade-network-ideal.md in full; World map row via
    world-stage-ideal.md §0, §4 and world-stage-map.md modules; npc-story-events-ideal.md §0–§3, §5–§12
    and its map in full; narrative-seed-ideal.md §0, §6.1–§6.2 and its module table; UI row
    (game-gui-principles.md) for the surfaces this map hands to npc's FE modules. NOT read this session:
    empire-resource-ssot.md, empire-economy-ssot.md, economy-principles.md, effect-atom/definitions.md
    §3 (predicate grammar bounds are quoted from the npc map), battle-engine-ssot.md,
    spec-cargo-fate.md beyond its §Design 1 opening. Each module spec reads its row first.
[x] decisions.md checked for locks: Empire resource registry (:108). No trade or storylet row exists
    yet; npc's NS1–NS8 are drafts. This map locks nothing.
[x] Every factual claim cites file:line (verified by reading the lines this session).
[x] audit-doc-citations.py --scope run on this file; HIGH findings fixed.
[x] Claims verified against code, not comments (LeafId members, TurnReportKinds, stances, SeasonOf,
    claim-cache kind, quest template shape, Caravan line).
[x] Surrounding sections read for quoted rules (host rule npc §6.2, failure branches §6.8, trade §7.2
    stock rule, §14b rows).
[x] No constraint reported as tested when it was not; hash-neutrality of fact writes is an
    acceptance criterion to prove, not a claim.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none made outside this fence; each is listed in §10 with its owner.
[x] No assertion pins a population. Storylet counts, fire counts and pick rates are readings; pinned
    lists (fact kinds, host kinds, leaves, templates) are declarations with reasons.
[x] No event-refreshed cache introduced; facts are appended in the turn's commit.
[x] Ordering: fact projection is asserted as reconciliation both ways, independent of producer order.
[x] Actor numbers: none; stories grant access, goods and quests.
[x] No SOLID-violating parallel path: one engine, one ladder, one price, one demand function, one
    quest engine, one generator.
[ ] New rule registry rows: the "no trade storylet authored outside the narrative adapter" guard and
    the "no price write outside exchange" guard need rows in gk-core/scripts/enforcement-registry.v1.json at
    spec time.
```


---

## 12. Reconciliation 2026-09-19 (round 4)

Applies [decisions-round-4.md](decisions-round-4.md) (binding). Verified against code this session: the
`claim-cache` verb is the item cache's (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:119`), so a goods
cache needs `fleet`'s presence claim; a slot holds only a `StructureId` today
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:119`), so hosts must read `trade-foundation` `sector-features`'
tier, not a row id.

### 12.1 What round 4 changed here

| Decision | Where it landed |
|---|---|
| B — buildings unlock features (trade ladder, caravan ladder) | `trade-hosts` (attach by feature tier), `trade-fact-kinds` (loss facts keyed by feature and tier) |
| B / Q1 — access = building tier AND treaty/band; clans need a Trading Post, not a treaty | `trade-predicates` (`AccessIs` reads `EffectiveLevel`), `trade-hosts` and price facts (fog reads `LevelAt`), `trade-quests` (ransom gated by `LevelAt`) |
| Q1 — the first clan market opens with a Trading Post (exchange E-A9 superseded) | `trade-trigger-reachability` §2a |
| Q5 — a clan on both shipped templates | used by `trade-trigger-reachability` §2a's fixture (counterparties owns it) |

### 12.2 Asks aimed at this map

| Ask | From | Status |
|---|---|---|
| A10 / C13 (`recover` must read `goods-cache.claimed`, not `claim-cache`) | `fleet-map.md` | Answered: T11, `trade-quests` |
| E-A9 (first-clan-market reachability) | `exchange-map.md` | Answered as superseded: T13, `trade-trigger-reachability` §2a |
| CM2 / OD-4 (register into `relation-facts`' projection) | umbrella, `counterparties` | Already answered (`trade-fact-source`) |

### 12.3 Cross-cluster conflicts (outside this fence — not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-T1 | A ransom needs a storylet outcome that makes the **counterparty** offer a deal; `outcome-routing` has no such outcome kind | npc-story-events `outcome-routing` adds one outcome kind that files a one-off deal offer through `exchange` `treaty-lifecycle` (ask in §8); `trade-ransom` waits for it |
| X-T2 | npc `world-events-host` hosts the `Market` **slot** as `world.market`; round 4 names the tier-2 trade building "Market" too | The one-place-one-host rule (`trade-hosts` §3) already keys on the trade feature, so hosting is unambiguous; the player-facing collision was `exchange-map.md` OQ-2, decided by round 5 C4 (slot display names renamed, `trade-lexicon` §4a) |

### 12.4 Closed-vocabulary widenings

None new. Fact kinds stay twelve (their key fields change from role to feature and tier); host kinds stay
four; leaves stay four; quest templates stay four.

### 12.5 Gap check

- Every module has a spec (10 of 10).
- Dependencies resolve; `trade-ransom` is blocked on X-T1 with a stated default (ships later).
- Tuning keys: none added; `shock.*` and the pacing rows stay single-owner.

### 12.6 Owner questions

None for this map.

### 12.7 Citation audit

`python scripts/audit-doc-citations.py --scope` was run on this map and every edited spec under
`trade-stories/` after these edits: no HIGH finding.

## 13. Round 5 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 5* (R5-A, R5-X; binding). Re-verified this
session: `SlotKind.Market` (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:18`) and the one-kind build gate
(`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:84`) that B1 widens.

| Ruling | Where it landed |
|---|---|
| **B1** — Trading Post on Wildland or Market | `trade-hosts` §3: one-place-one-host re-keyed on `TierOf(trade)`, so a hub on Wildland beside an empty Market slot is still one host (the old slot-keyed rule gave it two) |
| **B4** — the trader's best Trade tier anywhere counts | `trade-trigger-reachability` §2a (the Trading Post case) |
| **X1** — every gate reads `sector-features` | `trade-hosts` §3 no longer reads the `exchange` role |

**Not applicable here:** A1–A4, B2, B3 (caravan unloading gates no host or predicate), C1–C4 (the host
kind id `world.market` is not a display name; C4 renames only slot display names), D1, X2–X16. No new
contradiction; no owner question.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and every edited
`trade-stories/` spec after these edits.

## Audit 2026-09-20

Independent audit of this map and its ten specs against DESIGN-GATE §2/§3/§5, PRINCIPLES,
tunables-ssot, validation-ssot, testing-standard, economy-principles and the round-4/round-5 register;
code re-checked this session: `TurnCalendar.SeasonOf` is cyclic
(`gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:42`), `WorldSeed.DeriveRollSeed` keys a roll by
`(stream, target)` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`), `LeafId` holds 16 members
(`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`). Baseline `audit-doc-citations.py --scope`
on this map and `trade-stories/`: 0 HIGH before the edits.

### Findings

| # | Sev | Finding (evidence) | Status |
|---|---|---|---|
| T-A1 | HIGH | **Seasonal shocks repeated every year and their facts deduped away.** The roll target used the season index, which `SeasonOf` computes modulo the year, so every spring drew the same shocks forever; the fact key `shock:{worldId}:{season}:{goodClassId}` also lacked the climate, so a later year's shock — or a second climate's — collided with the first and was dropped | **Fixed:** absolute `seasonOrdinal` in the roll and the key, climate in the key; the term scoped to sectors of that climate (`seasonal-demand-shocks` §1–§2, criteria 1a/1b; `trade-fact-kinds` §3) |
| T-A2 | MED | **A pinned total of a shared closed enum.** `trade-predicates` pinned `LeafId`'s total at 26 — correct only if npc-story-events' six leaves land first; any other order fails the suite with no defect | **Fixed:** pin the four trade leaves by membership; the atom program owns the total |
| T-A3 | MED | **Stale ownership and facts in the map:** §6.9 still named `trade.treaty.broken` (dropped at spec time, T1); §8 filed the escort stance on `fleet` (it is `legion-build` `escort-stance`); X-T2 left OQ-2 open (decided, round 5 C4) | **Fixed** |
| T-A4 | LOW | `trade-quests` criterion 2 reconciled ransomed goods into the "player warehouse", but §3 lands them in the player's consignment at the hub | **Fixed;** and a short ransom now settles at the deal's one fulfilment ratio (the exchange audit's default guard) |
| T-A5 | LOW | Franchise names in new prose (`trade-story-pacing`, §6.5, §10) | **Fixed:** generic terms, prior art at ideal §6/§13 |

**Checked and sound (no change):** no second storylet engine, generator or relation ladder (facts are
projections into the one story ledger; rows come from the `narrative` adapter; the band is read, never
stored); one price (a storylet never sets a price — shocks move demand only, ransoms are exchange deal
legs); no souls out of trade; determinism (named streams, ordinal walks, same-commit idempotent
projection); pacing independent of empire size through the one engine's budget; reachability proven with
admitted commands only; no population pinned.

### Violations this map cannot fix (other owners)

| # | Owner | Violation | Fix |
|---|---|---|---|
| T-X1 | npc-story-events `outcome-routing` | No outcome kind can make a counterparty file a one-off deal offer, so `trade-ransom` is blocked (X-T1) | Add the outcome kind; `trade-ransom` ships after it |
| T-X2 | npc-story-events `story-ledger` | `lane` and `legion` subject kinds are still not in the ledger's closed list | Add them before `trade-fact-kinds` lands |
| T-X3 | `counterparties` `need-vector` | The shock term needs per-sector demand (exchange ask E-A10) to scope a climate shock to the sectors of that climate | Land E-A10's per-sector read first; until then the shock term cannot be climate-correct and must not ship |

### Owner questions

None.

---

## 14. Round 6 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 6* (binding) and the global-audit items this
cluster owed. Where this section disagrees with anything above, it wins; each change is in the named spec.

| Ruling / finding | Change in this cluster | Where |
|---|---|---|
| **C1** — one capability flag and one ruleset bump **per wave** | **Corrected 2026-09-20 (reconciliation R-7): this cluster registers exactly one flag and takes exactly one bump.** Nine of its ten modules register nothing, and for the reason this row always gave: trade story facts are projected from producers' records into the one story ledger, so the flag a trade story rides is the **producer's** (a fact about a hub cannot exist on a world whose stamp never granted `trade.exchange`), and a world stamped before a producer's wave simply never produces the fact. The tenth is `seasonal-demand-shocks`, which is not a projection: its shock is a **term in the demand function** `counterparties` computes and `exchange` reads, so it moves prices on a live world. That cannot ride row 15's `counterparties.needs` either — R1 forbids widening an earlier wave's flag. So **sub-wave 25c registers `trade.demandShock` and takes one bump**, and the blanket *"registers no capability flag and takes no `RulesetVersion` bump"* is withdrawn. Each spec's wave is the §7 table. One consequence stands unchanged: a trade fact kind is registered in the **same wave as, or after,** the producer whose record it projects — never earlier, or `trade-trigger-reachability` would have to prove a kind reachable through a command the world cannot admit | §7; [trade-stories/spec-trade-fact-kinds.md](trade-stories/spec-trade-fact-kinds.md) §Locked anchors; [trade-stories/spec-seasonal-demand-shocks.md](trade-stories/spec-seasonal-demand-shocks.md):131 (which already said a demand behaviour change rides the per-world stamp); [landing-order.md](landing-order.md) §2 row 25c, §10 R-7 |
| **S2 / W1 / W2** — goods cross worlds only by a rift route; an advance is a weight-limited transit | The **reason** given for world-scoped facts was the retired phrase *"trade dies with the map"*. Corrected in both places: worlds do not end (they become `developing`, `hibernating`, `idle` or `fallen` and stay revisitable), and goods cross only over a `rift-trade` route. A trade fact is world-scoped because a fact about a hub, lane or sector means nothing off that map, and it stays with its world for the rest of the save. **No scope changes** — the scope was right, the reason was stale (it is also the stale line `world-continuity/spec-continuity-doc-amendment.md` reported against this cluster) | spec-trade-fact-kinds §Locked anchors; §6.1 |
| **C3** — banking waits on the save-identity re-key | No story fact here is a banking fact, so nothing waits. One ordering note: a storylet whose trigger reads a *banked* figure would wait on banking, and none does — trade story triggers read hub, lane, sector and treaty records | — (stated) |
| **C2 / S1 / L6** — the neutral `Feature` kind, the split-owner rule, the Standard Hall | No story predicate reads a `StructureKind` or a building's owner: a building-shaped trigger (*"a hub was lost"*) reads the producer's own fact, and any tier a leaf needs comes from `sector-features` through the producer. So C2 and S1 need no change here, and L6 adds no fact kind (forging a standard is `legion-build`'s, and no trade story is written about it) | [spec-trade-predicates.md](trade-stories/spec-trade-predicates.md) (unchanged); §6.4 |
| **CQ2 / D2** | Nothing owed: no trade story reads a banked draw or a `world.*` channel | — (stated) |
| **M1** (global audit, owed) — two cycles inside this cluster needed landing notes | **`seasonal-demand-shocks` ↔ `trade-fact-kinds`:** `trade-fact-kinds` lands **first** (wave 1) with the shock's announcement kind **declared and unwritten** — a declared kind with no producer is legal and is exactly what `trade-trigger-reachability` (wave 3) later proves reachable; `seasonal-demand-shocks` (wave 3) lands the shock and becomes that kind's producer. **`trade-failure-branches` ↔ `trade-storylet-supply`:** `trade-storylet-supply` lands **first** (wave 2) with the failure hosts' registry rows and **no rows required to exist**; `trade-failure-branches` (wave 4) adds the branch facts and its acceptance asserts the coverage ask it needs was filed, never that content exists (a population would be a reading, not a contract). Neither pair is written against the other's unlanded code, and the reachability preflight is what keeps an unproduced kind honest | §7; the two module rows in §6.7 and §6.9 |

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, minor table), this
map and the specs edited · `[x]` citation audit run on every edited file · `[ ]` no suite run (documents only) ·
`[~]` session boundary: the caller's fence (this map, `trade-stories/**` and the other named trees;
`npc-story-events/**` and `narrative-seed/**` untouched by instruction) · `[x]` corrections propagated (the
retired *"dies with the map"* reason in §6.1 and the spec) · `[x]` no population pinned — the coverage asks
stay asks, and no acceptance counts storylets · `[x]` no cap added · `[x]` no second fact ledger, no second
pacing engine.

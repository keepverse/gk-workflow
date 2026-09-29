# Capability map: `logistics-flow`

**Status: APPROVED 2026-09-19.** Module specs are written against this map (owner decisions below).
**Reconciled with the round-4 owner decisions** ([decisions-round-4.md](decisions-round-4.md)) on
2026-09-19 — the last section lists what changed; where the two differ, that section and the specs win.
Sub-program 3 of the [trade-network](../trade-network-ideal.md) umbrella (ideal §11).
**Specs land:** `docs/architecture/trade-network/logistics-flow/spec-<module-id>.md` (new).
**Plan / tasks:** `tasks/trade-network-logistics-flow-plan.md` / `tasks/trade-network-logistics-flow-todo.md`
(the umbrella's §6 convention; this line first named `tasks/logistics-flow-*.md`), written only after
approval.

**Ideal it implements:** [trade-network-ideal.md](../trade-network-ideal.md) §3 (principles), §8.1–§8.7
(logistics), §9 (performance), §14b (round-3 gaps closed by principle). It does not reopen any §14 or §14b
decision.

---

## What this sub-program is

The **Logistics phase** of the one world turn engine: every End Turn, goods sitting in a sector's
warehouse flow along the lanes that connect them to a bank point (or to a destination a route policy
names), bounded by lane throughput, delayed by transit time, bled by a deterministic loss, and banked on
arrival as a ledger fact. It also makes lanes something you **build**: a `widen` verb raises `Width`
(throughput) and a `ward` verb raises `WardLevel` (protection), both paid in construction stocks that
this sub-program's construction chain finally produces (rubble → refinery → ironwork).

It moves **aggregate flow**, never agents (decision D5). Nothing here is a vehicle, a crate or a
per-unit path. Caravans — legions carrying goods to foreign or cross-world hubs — are [fleet](fleet-map.md);
cross-world legs are [rift-trade](rift-trade-map.md); prices and settlement are `exchange`.

**Loops:** Place 5 (world stage — where warehouses and bank points sit), Place 4 (world map — lanes,
distance, hazard), Place 3 (farm/hold/defend — a route is ground to hold). World clock only; no lawn,
no PvZ, no injector (ideal §3 principle 1).

### Load-bearing rules restated (a downstream session reads this map, not its links)

1. **One phase in the one turn engine** (ideal §3.17). No second turn loop, no parallel pricer: movement
   cost is `LaneCost`, connectivity is `LaneGraph`/`SupplyReach`, battles are the one battle engine.
2. **Determinism (P13).** Every hashed stock changes inside `TurnEngine.Step`, in stable id order, with
   integer math. A Data-side ledger row is written after `Step` inside the same commit, keyed on a
   durable fact id (P14). The report is the log: the engine writes nowhere else
   (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35`).
3. **Numbers.** Goods quantities and throughputs are `long`, `checked`, widen before multiplying, divide
   by 1000 last. Loss is a **bounded ratio** clamped to `[0, 1000]` ‰ and says so in a comment. Every
   balance number lives in `data/tuning/trade.v{n}.json` (new); a missing key is a load rejection (T5).
4. **No hard ceilings (PS-8).** `Width` and `WardLevel` grow without a ceiling; their cost rises on a
   curve. A per-turn rate (throughput, refine rate) is a **structural** per-turn limit and says so.
5. **PS-5.** Lane throughput reads the **same scale read** as the goods it carries (ideal §14b), and owes
   a row in `ssot-power-scale.md` §10 in the change that adds it.
6. **Every empire runs the same logistics** (principle 10). Nothing here branches on the player faction.
7. **Loam never flows here** (principle 6). Loam keeps its own supply and upkeep path. World stocks
   (`rubble`, `ironwork`) flow between own sectors but **never bank** (principle 7).
8. **Performance is a design constraint** (§9). Nothing per unit; cost grows with graph size, never with
   cargo volume; zero allocation in the phase after warm-up; paths recompute on graph change only and
   **never** through `ReconnectionCost`.

## Owner decisions (2026-09-19, with the approval)

| # | Decision |
|---|---|
| OD1 (Q1) | **Escort strength in v1 is a count of legions in the escort stance, weighted by tuning.** It switches to a **power-difference contest** once `legion-build` provides a Hub-composed power index (Q1 below, now closed). **Round 4 §P refines the switch:** the contest reads the **power roll-up** (a legion's power = the sum of its stacks' Hub power, like file sizes) and waits for its `ssot-power-scale.md` §10 row; until then the v1 count stands |
| OD2 (C6) | **`sector-yield` `banking-fact` creates the `Logistics` phase; this program owns the flow steps, their order and the `trade.logistics` flag** (umbrella §1a CM4) |

## Assumptions (correct before approving)

1. `trade-foundation` lands first and supplies (module ids from
   [trade-foundation-map.md](trade-foundation-map.md)): `step-benchmark`, `synthetic-graph`, `world-stamp`
   (with the `trade.logistics` capability flag), `ledger-keys`, `stock-deltas`, and `routing-guard` — the
   source-scan guard that fails any file under `src/FusionRpg.Core/World/Logistics/**` referencing
   `ReconnectionCost`. This map's code lives in that namespace so the guard covers it.
2. `sector-yield` lands first and supplies (module ids from [sector-yield-map.md](sector-yield-map.md)):
   `located-stock` (hashed, sparse, packed per sector), `warehouse-axis`, `essence-loop-read` (the scale
   read PS-5 requires), `production-halt` (the halt and its report fact), `bank-points` (a pure query), and
   `banking-fact` — which **creates the `Logistics` phase slot** with banking as its only step and amends
   the `decisions.md` phase-order row. This map adds its steps around banking inside that phase, in
   the fixed step order of `logistics-flow` `logistics-phase` §1 (banking is L3: refresh, arrivals and fleet load/unload before it; delivery overflow, rift departures, flow, loss, refine and facts after it — round 5 X5); it neither re-creates the slot nor writes banking facts.
3. "Own goods between own hubs is logistics, not trade" (ideal §7.4): no price and no spread inside this
   sub-program. Its one read of diplomacy is traversal — `passage` or better opens foreign ground (ideal
   §7.6). Ground that stays closed is crossed only by a legion that fights through it (`fleet`).
4. The one hostility rule stays `ZoneOfControl.IsHostile`
   (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16`); `counterparties`' `diplomatic-stance`
   turns it into a read of a derived stance. This map only calls it.
5. Exact numbers are tunables decided by principle and published through `gk-core/tools/tuning/publish.py`; they
   are not owner questions.

---

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| `Step` runs **ten** phases: Reveal, Movement, Sieges, **Assaults**, Production, Growth, Pressure, Events, Snapshot, Intel | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:191-207`; the phase list test `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107` |
| `RulesetVersion` is one global constant, 13 (12 when this map was approved; warden-freeze-fix bumped it) | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125` |
| A stored turn stops replaying the moment the constant moves | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-760` |
| `rpg_worlds.ruleset_version` exists and defaults to 1 | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:31` |
| `WorldLane.Width` (default 1000) is hashed and **read by nothing else** — the only reader is the canonical writer | `gk-core/src/FusionRpg.Core/World/WorldState.cs:258-259`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55-56` |
| `WorldLane.WardLevel` sets siege approach depth for an attacker on that lane | `gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:342-350` → `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:116` → `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:170-171` |
| Nothing raises `WardLevel` or changes `Width`; `ward` is reserved for the unbuilt lane verb | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:41-55` |
| Nothing ever writes `LaneState.Severed`; only readers exist | `gk-core/src/FusionRpg.Core/World/WorldState.cs:51-55`; `gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:129`; `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:52` |
| `LaneGraph` already builds an ordinal-ordered graph with a **Supply** lens (deep and one-way excluded) and a March lens | `gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:20-27,92-136`; lane types `gk-core/src/FusionRpg.Core/World/LaneTypeCatalog.cs:58-63` |
| Supply is a BFS recomputed every turn, never cached; a contested owned sector is a roadblock | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:7-11,19-45` |
| `ReconnectionCost` is O(V⁴) and has three production callers (two AI, one endpoint) | `gk-core/src/FusionRpg.Core/World/Topology/ReconnectionCost.cs:18-19`; `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:32`; `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:167`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:864` |
| `LaneCost` is integer per-mille: length × type × hazard, ley discount | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:105-147` |
| `SiegeConstruction.Refine`/`RefineGated` have **no production caller** (tests only); the raw rubble/ironwork faucets are wired into Production | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:33-48,90-106`; callers `gk-core/tests/FusionRpg.Core.Tests/World/SiegeConstructionTests.cs:56-79`; Production slot `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:302-314` |
| The refine tunables exist; the per-turn gate is unset (`-1`) | `gk-core/data/tuning/siege.v1.json` keys `refineRubblePerIronwork`, `refineYieldMilli`, `refinePerTurnCap` (see `gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs:41`) |
| The `refinery`, `convoy-depot` and `causeway` structure rows are identity-only (no `magnitudes` block), so none is playable | `gk-data/packs/fusion/data/seed/structures/refine/refinery.json`; `gk-data/packs/fusion/data/seed/structures/move/convoy-depot.json`; `gk-data/packs/fusion/data/seed/structures/move/causeway.json`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| Production halts at capacity (decision 22), not overflow | `gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:56-58` |
| The canonical writer already emits **conditional rows** for sparse stocks (a zero rubble/ironwork stock writes nothing) | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128` |
| The state hash rewrites the whole canonical text every turn | `gk-core/src/FusionRpg.Core/World/Turn/StateHasher.cs:17` |
| The diff writer touches only changed rows | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:45-69` |
| `Stopwatch`, `DateTime.Now/UtcNow` and `System.Random` are banned in the World/Battle/Effects trees | `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-47,253-266` |
| A benchmark project exists, with a zero-allocation measurement precedent and a world-graph write bench | `gk-core/tests/FusionRpg.Bench/AtomFormBench.cs:120-140`; `gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs` |
| A pure per-sector projection precedent (world-stage's next-turn forecast) | `gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:9` |
| Turn report kinds are a five-string list today | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-10` |

---

## Modules

Stable kebab-case ids, chosen once. Model-free throughout: no module needs generated content to be
built or tested (structure magnitudes come from `empire-seed` tuning bands, and every test runs on a
fixture or the synthetic graph).

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `logistics-phase` | The step order inside the `Logistics` phase and the `trade.logistics` capability read; the slot itself is created by `sector-yield` `banking-fact` | `trade-foundation` `world-stamp`; `sector-yield` `banking-fact` | 1 |
| 2 | `logistics-canonical` | Hashed, sparse state for everything this sub-program adds (transit buffers, lane flow state, route policies — **no graph-version counter**, R-19.1); packed persistence rows | `logistics-phase` | 1 |
| 3 | `path-cache` | Cached supply-lens paths keyed on an **unhashed exact topology key**; full invalidation trigger set (T1–T12); never `ReconnectionCost` | `logistics-canonical` | 2 |
| 4 | `lane-flow` | `Width` as throughput; one priority flow pass plus one redistribution pass; pro-rata contested capacity; bottleneck reasons | `path-cache`; `sector-yield` goods | 2 |
| 5 | `transit-buffer` | Transit time from `LaneCost`; a bounded per-route in-transit buffer; stranding on a cut path | `lane-flow` | 2 |
| 6 | `lane-loss` | Deterministic per-lane loss clamped to [0, 1000] ‰ that vanishes; readable causes | `lane-flow` | 2 |
| 7 | `auto-banking` | Default flow destination = nearest bank point (a Counting House, round 4); the `route-set`/`route-clear`/`bank-hold` policy commands; arrivals handed to `banking-fact` the turn they land | `lane-flow`, `transit-buffer`; `sector-yield` `bank-points`, `banking-fact` | 3 |
| 8 | `lane-verbs` | `widen` (raises `Width`) and `ward` (raises `WardLevel`, keeps its siege meaning), priced in construction stocks on a rising curve | `lane-flow`, `lane-loss`, `construction-chain` | 3 |
| 9 | `construction-chain` | Wire `SiegeConstruction.RefineGated` at working refineries; route world stocks between own sectors; never bank them | `lane-flow`; `empire-seed` refinery magnitudes | 3 |
| 10 | `logistics-facts` | The closed logistics report vocabulary (`lane.cut`, loss with cause, strand, delivery overflow) written from day one, fog-scoped | `lane-flow`, `transit-buffer`, `lane-loss` | 2 |
| 11 | `forecast-facts` | A side-effect-free dry run of the turn for next-turn halt/strand/waste facts and bottleneck reasons, each with its answers — `build` [a sector feature] among them (round 4: the first throttle's answer is *build a Counting House*) | `logistics-facts`, `auto-banking`, `construction-chain`; `trade-foundation` `sector-features` | 4 |
| 12 | `logistics-bench` | Budgets at medium and giant tiers, zero-allocation assertion, volume-invariance test (the `ReconnectionCost` ban is `trade-foundation` `routing-guard`) | every module above; `trade-foundation` `step-benchmark`, `synthetic-graph` | 4 (gate) |

**Build order:**

```
Wave 1  logistics-phase → logistics-canonical
Wave 2  path-cache → lane-flow → (transit-buffer ∥ lane-loss) → logistics-facts
Wave 3  construction-chain → lane-verbs ;  auto-banking (∥ construction-chain)
Wave 4  forecast-facts ;  logistics-bench (the gate — the sub-program is not done until it is green)
```

**Dependency direction, no cycles.** `lane-verbs` depends on `construction-chain` because the verbs are
paid in ironwork/rubble; `construction-chain` depends only on `lane-flow` (to move world stocks between
own sectors). `logistics-facts` reads what `lane-flow`/`transit-buffer`/`lane-loss` computed; nothing
upstream reads it back. `fleet` and `rift-trade` depend on this map; this map depends on neither.

**Phase-internal order** (inside `Logistics`, fixed by `logistics-phase`, each step reading the previous
one's output — **corrected at reconciliation** to the order `spec-logistics-phase.md` §Design 1 fixed,
which moved banking ahead of overflow): L0 path refresh → L1 arrivals from transit buffers (with
`rift-trade`'s rift arrivals) → L2 `fleet` load/unload → L3 **banking** (`sector-yield` `banking-fact`, up
to the Counting House tier's rate — round 4) → L4 delivery overflow (unload into room banking freed, then
waste) → L4r `rift-trade` departures → L5 lane-flow pass (new departures, movement) → L6 loss → L7
construction-chain refine → L8 report entries → A1 `exchange` quote and settlement → A2 `counterparties`
`clan-economy` consumption (after settlement, its ask A12) (ideal §8.7; `counterparties-map.md` module 9;
`exchange-map.md` `order-book`) — this map fixes the order, those maps own the passes.

---

## Module detail

### 1. `logistics-phase`

**Capability.** The `Logistics` phase sits between Production and Growth (ideal §8.7). Its **slot** is
created by `sector-yield`'s `banking-fact` (which lands first, with banking as the phase's only step, and
amends the locked `decisions.md` phase-order row in that change). This module owns what the ideal gives
`logistics-flow`: the **flow steps** placed around banking (L3), the **step order inside the phase** (above;
canonical for every program, round 5 X5),
and the `trade.logistics` capability read from `trade-foundation`'s `world-stamp` — a world whose stamp
grants `trade.sectorYield` but not `trade.logistics` banks only goods produced at a bank point and moves
nothing; a legacy-stamped world runs no trade step at all and replays byte-identically (ideal §14 D-C). The
ruleset change is carried by the stamp, never by a global `RulesetVersion` move that would stop every old
world replaying (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-760`).

- **Built:** the phase pipeline and report phase list (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209`,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:90`); the phase-list test (`gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107`).
- **Wiring gap:** `rpg_worlds.ruleset_version` is stored but always 1 and never read as a stamp
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:31`) — `trade-foundation` `world-stamp` wires it.
- **Real gap:** the `trade.logistics` flag's reader and the step order.
- **Depends on:** `trade-foundation` `world-stamp`; `sector-yield` `banking-fact` (the slot).
- **Touches:** `src/FusionRpg.Core/World/Logistics/LogisticsSteps.cs` (new); the phase method `banking-fact`
  adds to `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (one call per flow step, no new phase).
- **Acceptance (contract):**
  - A world without the `trade.logistics` flag produces the same state hash, turn for turn, as the same
    world before this module (no flow step runs; banking behaves exactly as `banking-fact` alone).
  - With the flag, the steps run in the stated order every turn, observable in the report's phase entries;
    reordering two steps in code fails a test that asserts the order (the order is a contract).
  - Every step is a pure function of `(state, revealed commands, seed)`; none reads a clock, ambient state or
    a Data-side store (`WorldDeterminismGuardTests` already scans the World tree).
  - Legacy-, sector-yield- and logistics-stamped worlds coexist in one store and all three replay,
    independent of creation order (all orders tested).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Turn); `FusionRpg.Data.Tests` for the stamped
  replay path; `FusionRpg.Guard.Tests` (determinism).

### 2. `logistics-canonical`

**Capability.** Owns the hashed and persisted form of every piece of state this sub-program adds: the
graph-version counter, per-route transit buffers, and per-lane per-turn flow records the forecast and
report read. **Sparse canonical form** — only non-zero entries write a canonical row, extending the
conditional-row precedent (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128`) — so hashing cost grows
with what is actually moving, not with sectors × goods × routes. Persistence is **one packed row per
sector** (and per route for buffers), ridden through the diff writer so an unchanged sector writes nothing
(ideal §14b, closing §15's "per good vs packed" choice). `sector-yield`'s `located-stock` already follows
the same rule for warehouse stock; this module holds logistics' own state to it.

- **Built:** the canonical writer and its conditional-row shape; the diff writer
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:45-69`).
- **Wiring gap:** —
- **Real gap:** the new fields, their canonical rows and their packed persistence columns.
- **Depends on:** `logistics-phase`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/WorldState.cs`, `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs`.
- **Acceptance (contract):**
  - A world with no goods, no routes and no transit writes byte-identical canonical text to today's
    (field additions are invisible at their zero value).
  - Canonical text length is invariant under adding goods ids that are zero everywhere (sparse, asserted
    by comparing two worlds that differ only in zero rows).
  - Save → load → hash round-trips byte-identically for a world with non-zero buffers and a non-zero
    graph version (every new field has a column; the base-defense lesson of write-only fields,
    `TurnEngine.cs:66-71`, is tested, not assumed).
  - A turn that changes one sector's goods writes exactly that sector's packed row and no other goods row.
- **Verification boundary:** `FusionRpg.Core.Tests` (World canonical); `FusionRpg.Data.Tests` (round trip,
  diff writer).

### 3. `path-cache`

**Capability.** Caches, per faction, the path from every goods-holding sector to its flow destination
(nearest bank point by default, or the route policy's destination) on the **Supply lens** of `LaneGraph`
— so `deep` and `one-way` lanes carry no goods, exactly as they carry no supply
(`gk-core/src/FusionRpg.Core/World/LaneTypeCatalog.cs:61-62`; ideal §8.4 left this to the spec; one traversal rule
for supply and goods is the recommendation). Sector traversability follows ideal §7.6 (*"your own and
unheld ground is always open"*; another empire's ground only under `passage`): a sector is open to a
faction's flow when it is **own** or **unheld**, and not held against the faction by a hostile projecting
entity (the `SupplyGraph` roadblock rule, `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:30-31`), or when
its owner grants the faction `passage` or better through `exchange`'s `trade-access` (from the turn that
module lands; until then foreign ground is closed). Ground that stays closed — hostile, embargoed, contested
— is crossed only by a legion that can fight through it (`fleet`). The cache is keyed on a **hashed graph-version
counter** and rebuilt only when it changes. It **never** calls `ReconnectionCost` (ideal §9.2 rule 3).

Invalidation follows DESIGN-GATE §2.16 — the trigger set is enumerated in full, including the edges where
the cache's **key set** moves, and each trigger gets its own test:

| # | Trigger | Why it invalidates | Key set moves? |
|---|---|---|---|
| T1 | A lane's `State` changes (Open ↔ Severed) | Traversable edge set | No |
| T2 | A lane's `GateKeyId` changes (gate shut/opened) | `LaneGraph.IsTraversable` refuses a keyed gate (`LaneGraph.cs:131-132`) | No |
| T3 | A lane is added or removed | Edge set | No |
| T4 | A lane's `Length`, `TypeId` or `HazardMilli` changes | Edge cost, so shortest path | No |
| T5 | A sector's owner changes (claim, capture, cede, fade) | Traversable node set **and** the set of goods-holding sectors | **Yes** |
| T6 | A hostile projecting entity enters or leaves an owned sector (zone of control) | Contested sector becomes a roadblock (`SupplyGraph.cs:30-31`) | No |
| T7 | A bank point appears or disappears (structure activates, is destroyed, sector lost) | Destination set | **Yes** |
| T8 | A route policy is set or cleared | Destination for that source | **Yes** |
| T9 | Hostility between two factions changes (`counterparties` `diplomatic-stance`) | T6's predicate changes for every sector | No |
| T10 | An `Access` level between two factions crosses the `passage` threshold (`exchange` `trade-access`: treaty signed, broken, embargo, war) | The grantor's sectors join or leave the traversable set; a new foreign sector can become a source or pass-through | **Yes** |

Width and WardLevel changes are **not** triggers: they change capacity and loss, not paths.

**Corrected 2026-09-20 (reconciliation R-19.1).** This paragraph used to describe a hashed graph-version
counter bumped at one choke point per mutating phase, cross-checked in test mode against a cheap topology
fingerprint, with ten triggers (T1–T10). That design is withdrawn.
[logistics-flow/spec-path-cache.md](logistics-flow/spec-path-cache.md):241-242 replaces it with an
**unhashed exact topology key** and **twelve** triggers (T1–T12), and
[logistics-flow/spec-logistics-canonical.md](logistics-flow/spec-logistics-canonical.md):189-190 asserts
that **no counter is hashed**. The key *is* the cross-check: a stale key cannot survive a comparison
against the current topology, so there is no fingerprint to keep in step with a counter. The specs win;
this map was the stale document.

- **Built:** `LaneGraph` with lenses and ordinal ordering (`gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:44-136`);
  `SupplyReach.From`/`LinksOf` (`gk-core/src/FusionRpg.Core/World/Movement/SupplyReach.cs:24,67`).
- **Wiring gap:** none — the graph exists; nothing caches it (`SupplyGraph.cs:7-11` deliberately recomputes).
- **Real gap:** the topology key and the cache (no counter, no fingerprint cross-check — see the
  correction above).
- **Depends on:** `logistics-canonical` (the counter is hashed state); `sector-yield` `bank-points` (T7);
  `counterparties` `diplomatic-stance` (T9) and `exchange` `trade-access` (T10) — both optional: absent,
  every other faction is hostile and foreign ground is closed, today's rule.
- **Touches:** `src/FusionRpg.Core/World/Logistics/PathCache.cs` (new), `src/FusionRpg.Core/World/Logistics/GraphVersion.cs` (new);
  the phases that mutate T1–T8 inputs (a one-line bump each).
- **Acceptance (contract):**
  - **Equivalence:** for every turn of a scripted run and of a seeded random run on the synthetic graph,
    the cached path set equals a fresh uncached computation (property test).
  - One test per trigger T1–T10, each asserting the counter moves and the cache rebuilds; T5, T7, T8 and
    T10 additionally assert the **new key** (the newly owned sector, the new bank point, the new route
    source, the newly opened foreign sector) is present in the cache the same turn.
  - **Order-independent:** a claim and a bank-point activation landing in the same turn produce the same
    cache whether the claim or the structure resolves first in the fixture (both orders tested).
  - A turn with no T1–T9 event does not rebuild (counter unchanged, rebuild count 0).
  - Every file of this module lives under `src/FusionRpg.Core/World/Logistics/**`, so `trade-foundation`'s
    `routing-guard` (the `ReconnectionCost` ban) covers it from its first commit.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics); `FusionRpg.Guard.Tests` (`routing-guard`).

### 4. `lane-flow`

**Capability.** Turns `Width` into throughput: a lane carries at most
`Width × lane.throughputPerWidth ÷ 1000` load units per turn (ideal §8.4), in **value-normalised units**
that read the same scale as the goods' own yield — `sector-yield`'s `essence-loop-read` (PS-5; ideal §14b) — so throughput never becomes a hidden
ceiling as `Θ` grows. One flow pass in route-priority order plus at most one redistribution pass; never an
exact multi-commodity solve (ideal §9.2 rule 4). When several commanders' flows contend for one lane, the
lane's capacity is split **pro rata by demand across commanders** (principle 10 — never by faction id),
then by route priority within a commander, then by stable id. Every lane records its utilisation and, when
a flow is short, a **bottleneck reason** from a closed set (lane capacity, destination full, path cut,
contested sector, no path). Repurposing `Width`: its comment says "how large a force crosses at once"
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:258`) but no code reads it; the ideal assigns it to throughput,
and any later force-width reading must share the field (Contradictions C3).

- **Built:** `Width` is hashed and persisted (`WorldCanonical.cs:55`); `LaneCost` supplies per-lane cost.
- **Wiring gap:** `Width` is read by nothing (`gk-core/src/FusionRpg.Core/World/WorldState.cs:258-259`).
- **Real gap:** the flow pass, pro-rata split, utilisation, bottleneck reasons, the §10 row.
- **Depends on:** `path-cache`; `sector-yield` (located goods, warehouse capacity at the destination);
  `trade-foundation` (synthetic graph).
- **Touches:** `src/FusionRpg.Core/World/Logistics/LaneFlow.cs` (new); `data/tuning/trade.v1.json` (new) keys
  `lane.throughputPerWidth`; `docs/architecture/power/ssot-power-scale.md` §10 (one new row).
- **Acceptance (contract):**
  - Conservation: goods leaving sources this turn = goods entering transit + goods refused (still at the
    source), per good, per turn, asserted every turn (reconciliation).
  - No lane carries more than its capacity in any turn.
  - **Pro-rata:** two commanders with demand `d1`, `d2` on a lane of capacity `c < d1 + d2` receive shares
    proportional to `d1 : d2` within integer rounding (remainder by stable id), and swapping the faction ids
    swaps nothing else.
  - **Θ invariance:** scaling every scaled good's yield and the scale read by the same factor leaves the
    fraction of a sector's output one lane can move unchanged.
  - Every short flow carries exactly one reason from the closed set; the set's cardinality is pinned as a
    **closed vocabulary** (a reviewed change adds a reason), never a count of flows.
  - Volume invariance: multiplying every stock by 1000 changes no iteration count (checked by
    `logistics-bench`).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics).

### 5. `transit-buffer`

**Capability.** Goods take time to travel: transit turns = `ceil(path LaneCost ÷ goods speed)` with the
speed a tunable in `LaneCost`'s own per-mille units (ideal §8.4). Each route keeps a short in-transit
buffer of at most `route.maxTransitTurns` slots — a **structural** limit, commented as such — so a
route's cost is `goods × transit turns`, not cargo volume. When a path is cut (any `path-cache` trigger that
removes the route's path), goods already on the cut lane are **stranded**: they hold position, keep taking
that lane's loss each turn, and resume when a path reopens; the player can clear the route, which returns
stranded goods to the source warehouse at the next turn. There is no rating spiral: a stranded route's
recovery never depends on its own past performance (ideal §6 lesson 6).

- **Built:** mid-march resume from lane progress is the precedent for resumable position
  (`gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-31`).
- **Wiring gap:** —
- **Real gap:** the buffer, stranding, return on clear.
- **Depends on:** `lane-flow`, `path-cache`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/TransitBuffer.cs` (new); `logistics-canonical` fields.
- **Acceptance (contract):**
  - Goods sent on turn *t* along a path of transit *k* arrive on turn *t + k* exactly, absent a cut.
  - Conservation per route: in transit(t+1) = in transit(t) + departed − arrived − lost − returned.
  - A path longer than `route.maxTransitTurns` is refused with a reason; it is never truncated silently.
  - Cut then restore: goods resume from their slot; cut then clear: goods return to source and nothing is
    created (sum before = sum after + loss).
  - **Order-independent:** a cut and a `route-clear` filed in the same turn give the same final stocks in
    either filing order (both tested).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics).

### 6. `lane-loss`

**Capability.** Per lane per turn, goods crossing it lose
`goods × clamp(hazardMilli + hostilePresenceMilli + goods.{id}.transitLossMilli − WardLevel × lane.protectionPerWard − escortMilli, 0, 1000) ÷ 1000`
(ideal §8.4, §14b). The clamp is a **bounded ratio** (exempt from PS-8, commented). The lost goods
**vanish** — a pure sink, never a faucet for anyone. `hostilePresenceMilli` reads hostile projecting
entities at the lane's ends and on the lane (the `ZoneOfControl.IsHostile` rule); `escortMilli` reads own
legions posted on the lane. **Which** legions count is a **stance-weight table in tuning keyed by stance
id**, so the `escort` stance `legion-build` adds (`legion-build-map.md` `escort-stance`) is a tuning row, not a
code change here, and this map needs nothing from `fleet`. **How strongly** a posted legion counts is owner
question Q1 below — the ideal says an escort's *strength* feeds `escortMilli` (§8.3; `legion-build-ideal.md`
§6.5) but names no strength read, and the one strength figure the world has is forbidden for this use
(`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`: *"Never call this to decide a battle"*). Every
non-zero loss carries its **dominant cause** from a closed set (hazard, hostile presence, perishability,
stranded) for the report and the status line.

- **Built:** `HazardMilli` and `WardLevel` on the lane (`gk-core/src/FusionRpg.Core/World/WorldState.cs:261-262`);
  the hostility rule (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16,32-40`).
- **Wiring gap:** `WardLevel` has no logistics reader.
- **Real gap:** the formula, the cause set, the stance-weight table.
- **Depends on:** `lane-flow`, `transit-buffer`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/LaneLoss.cs` (new); `data/tuning/trade.v1.json` (new) keys
  `lane.protectionPerWard`, `lane.hostilePresenceMilli`, `lane.stanceEscortMilli.{stance}`,
  `goods.{id}.transitLossMilli`.
- **Acceptance (contract):**
  - Loss is in `[0, goods]` for every input, including a negative raw term (floored at 0) and a raw term
    above 1000 (clamped); asserted over a property sweep.
  - No path increases any stock anywhere when loss is applied (the lost quantity appears in no balance,
    ledger credit or cache) — the sink invariant.
  - Raising `WardLevel` by one never increases loss; adding an own legion on the lane never increases loss;
    adding a hostile one never decreases it (monotonicity).
  - Same inputs, same loss, byte for byte, across runs (determinism; no RNG is consumed).
  - A stance with no row in the weight table is a **load rejection** naming it (T5), never weight 0.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics).

### 7. `auto-banking`

**Capability.** Shape B's default (ideal §8.6): with no route policy, a sector's located goods flow toward
the **nearest bank point** (`sector-yield` `bank-points`) in the faction's connected own component, and a
delivery that lands in a bank point's warehouse is banked **the same turn** by `sector-yield`'s
`banking-fact`, which runs after arrivals (phase order above) and owns the fact, its key and its ledger
credit. Goods produced at a bank point never flow at all. Auto-banking is **on by default**. Two policy
commands, `route-set` and `route-clear`, admitted through `WorldCommandAdmission`, redirect a sector's flow of
a good to a named own destination or restore the default; they set policy and move nothing themselves
(ideal §8.7; `sector-yield-map.md` §2.9: *"the policy commands that change it belong to `logistics-flow`"*).
A world stock (`rubble`, `ironwork`) may be routed between own sectors (`construction-chain`) but never has a
bank-point destination (principle 7).

- **Built:** one command shape and one admission gate for every commander
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:140`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:24`).
- **Wiring gap:** —
- **Real gap:** the default-destination rule and both policy commands.
- **Depends on:** `lane-flow`, `transit-buffer`, `path-cache`; `sector-yield` `bank-points`, `banking-fact`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/AutoBanking.cs` (new); `WorldCommandKinds` (+`route-set`,
  `route-clear`); `WorldCommandAdmission.cs`; the policy's hashed record (through `logistics-canonical`).
- **Acceptance (contract):**
  - With no policy, every located good in a connected own sector flows to the nearest bank point by path
    cost, ties broken by sector id; a sector with no reachable bank point sends nothing and reports why.
  - Delivered into a bank point's warehouse on turn *t* ⇒ banked on turn *t* (the arrival precedes
    `banking-fact`); asserted per good.
  - `route-set` changes only the named sector-and-good flow; `route-clear` restores the default exactly.
  - No policy can name a bank point as the destination of a world stock or accrual meter (admission refuses
    with a reason; closed-enum membership test against the registry classes).
  - **Order-independent:** a `route-set` and a capture of its destination sector in the same turn resolve
    the same in either filing order (both tested; the captured destination falls back to the default).
  - The AI and the player file the same two commands through the same admission path (no player branch).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics, World/Turn).

### 8. `lane-verbs`

**Capability.** Two lane commands make throughput and protection something you build (ideal §8.4):
`widen` raises a lane's `Width` by `lane.widenStep`; `ward` raises its `WardLevel` by one. Both are paid
in **construction stocks** (ironwork, rubble) from a sector the commander holds at one end of the lane, on
a **rising cost curve per level** — never a cap (PS-8). `ward` keeps its siege meaning: the same field
still sets the district approach depth for an attacker on that lane
(`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:170-171`) and now also suppresses lane loss.
The two meanings point the same way (a warded lane is a defended lane), and a guard test asserts both
readers read the one field so no later program splits it (ideal §8.4). The command name `ward` is the one
the code already reserves (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:41-55`).

- **Built:** the admission gate; the siege reader of `WardLevel`.
- **Wiring gap:** "Nothing raises `WardLevel` or changes `Width`" (ideal §5) — confirmed, no writer exists.
- **Real gap:** both verbs, their cost curves, the dual-reader guard.
- **Depends on:** `lane-flow`, `lane-loss`, `construction-chain`.
- **Touches:** `WorldCommandKinds` (+`widen`, `ward`); `WorldCommandAdmission.cs`; a resolver in the
  `Snapshot` build slot, beside `BuildResolver` (same ownership-race reasoning as `raise`/`develop`,
  `WorldCommand.cs:61-81`); `data/tuning/trade.v1.json` (new) keys `lane.widenStep`, `lane.widenCostCurve`,
  `lane.wardCostCurve`.
- **Acceptance (contract):**
  - A `widen` or `ward` with insufficient construction stock is refused with a reason and spends nothing;
    an accepted one spends exactly the curve's price (conservation).
  - No level is ever refused for being "too high"; the next level's price is strictly greater than the
    previous (rising, uncapped). Arithmetic is `checked` and throws rather than wraps.
  - Guard: `WardLevel` is read by the siege approach path and by `lane-loss`, and by no second
    ward-shaped field (a source scan fails on any `*Ward*Level*` field on `WorldLane` other than the one).
  - The siege read stays well-formed for large `WardLevel` values (`DistrictAssaultResolver.cs:170-172`
    already computes it `checked`; the spec verifies the zone geometry at high levels rather than assuming).
  - Only a commander holding a lane end may issue either verb; the AI files them through the same path.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics, World/Siege); `FusionRpg.Guard.Tests`.

### 9. `construction-chain`

**Capability.** Closes the base-defense refine chain the world never ran: at a **working refinery** a sector
turns rubble into ironwork each turn through the already-shipped, already-tested
`SiegeConstruction.RefineGated` (lossy by `refineYieldMilli`, gated by the structure — decision 28), at a
per-turn refine rate per refinery that is a **structural per-turn limit** in tuning (replacing the unset
`refinePerTurnCap = -1`, which today makes an automatic refine an unbounded drain —
`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:83-89`). And it moves **world stocks between own
sectors**: rubble to a refinery's sector, ironwork to where construction, `widen` and `ward` spend it, under
the same `route-set` policy, the same lane flow and the same loss — but a world stock **never** reaches a
banking fact (principle 7). The refinery row gets its magnitudes from `empire-seed`'s tuning bands; this
module writes no structure content.

- **Built:** `Refine`/`RefineGated` (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:33-48`); raw faucets
  wired into Production (`SiegeConstruction.cs:90-106`, called at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:309`);
  `StructureKind.Refinery` (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:30`).
- **Wiring gap:** `Refine`/`RefineGated` have zero production callers (tests only); the refinery row has no
  magnitudes (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`).
- **Real gap:** the per-turn refine pass and rate; routing world stocks between sectors.
- **Depends on:** `lane-flow`, `auto-banking` (policy commands); `empire-seed` (refinery magnitudes).
- **Touches:** `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs` (a caller, not a rewrite);
  `src/FusionRpg.Core/World/Logistics/ConstructionFlow.cs` (new); `data/tuning/siege.v{n+1}.json` via
  `gk-core/tools/tuning/publish.py` (the refine rate).
- **Acceptance (contract):**
  - Refining spends rubble and produces `Refine(spent, yieldMilli)` ironwork exactly — the two stock
    deltas reconcile every turn; a sector without a working refinery refines nothing and spends nothing.
  - Refine per turn never exceeds the tuned per-turn rate × working refineries (structural bound, stated).
  - Guard: no code path turns rubble, ironwork, loam or recruits into a banking fact, a material or a
    wallet credit (source scan plus a property test over random routes).
  - Moving a world stock between two own sectors conserves it except for the lane loss.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Siege, World/Logistics).

### 10. `logistics-facts`

**Capability.** Every loss has a readable cause **from the first turn the phase runs** (ideal §14b), and the
facts other programs react to are written at once, before any storylet reads them. A closed report
vocabulary joins `TurnReportKinds`: `lane.cut` (a route lost its path), `logistics.loss` (quantity and
dominant cause), `logistics.strand`, `logistics.overflow` (a delivery wasted at a full warehouse — only
deliveries waste, decision 22 — the halt half is `sector-yield`'s `production-halt`). Banking and halt
entries are written by `sector-yield`'s `banking-fact` and `production-halt`; this module never duplicates
them. Every entry names its sector or lane (`SectorId`) and its faction (`Audience`) so it
is fog-correct (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:12-31`). The committed turn report is the
fact source `npc-story-events`' `failure-branches` and `quest-sources` already plan to read ("reading durable
records other programs already commit", `npc-story-events-map.md` modules 14 and 23) and the source
`trade-surface`'s status line folds (*banked N · lost M (main cause) · stuck K (worst bottleneck)*). This map
publishes the closed token sets; `trade-surface`'s `trade-lexicon` translates them.

- **Built:** the report entry shape with sector and audience scoping (`TurnReport.cs:31-32`).
- **Wiring gap:** —
- **Real gap:** the kinds and their token sets.
- **Depends on:** `lane-flow`, `transit-buffer`, `lane-loss`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs` (new kinds); `src/FusionRpg.Core/World/Logistics/LogisticsFacts.cs` (new).
- **Acceptance (contract):**
  - Every non-zero loss in a turn has exactly one `logistics.loss` entry with a cause from the closed set;
    Σ reported loss = Σ applied loss (reconciliation).
  - Every path loss produces one `lane.cut` the turn it happens, and none on a turn with no cut.
  - Every entry carries a non-null `Audience`; an entry about a sector carries its `SectorId`; a projection
    for faction A never contains an entry whose audience is faction B (fog test).
  - The kind list and each cause/reason set are pinned as **closed vocabularies** with a comment saying why
    (a reviewed change adds one); no test counts entries.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Turn, World/Logistics).

### 11. `forecast-facts`

**Capability.** The read model for `trade-surface`'s throttle forecast (ideal §14b: *"next turn a sector
halts: 40 fire essence has nowhere to go"*). A **side-effect-free dry run** of the Logistics step on a copy
of the committed state with no new orders, returning per-sector next-turn facts — halt (production has
nowhere to go), strand, delivery waste, and the bottleneck reason per affected flow — plus, for each, the
command kinds that would answer it (`route-set`, `widen`; `fleet`'s escort and `exchange`'s sell are named
by those maps). Same pure-projection shape as `LoamForecast` (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:9`):
one function, never a second copy of the flow rules.

- **Built:** the projection precedent.
- **Wiring gap:** —
- **Real gap:** the dry run and its fact records.
- **Depends on:** `logistics-facts`, `auto-banking`, `construction-chain`; `sector-yield` (halt rule and
  next-turn production).
- **Touches:** `src/FusionRpg.Core/World/Logistics/LogisticsForecast.cs` (new).
- **Acceptance (contract):**
  - **Faithful:** for any fixture world, committing the next turn with no new orders produces exactly the
    halts, strands and waste the forecast named, and nothing it did not name (both directions tested).
  - **Pure:** the input state hash is unchanged after the forecast runs.
  - The forecast calls the same flow, loss and transit functions the phase calls (a test proves a changed
    tuning value moves both identically).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics).

### 12. `logistics-bench`

**Capability.** The sub-program's gate against ideal §9: budgets measured, not asserted from design. Runs in
`gk-core/tests/FusionRpg.Bench` (Release; outside the clock-banned World tree) on `trade-foundation`'s synthetic
graph builder at medium (≤ 18 sectors) and giant (≤ 144 sectors, ≤ 500 routes, ≤ 40 goods) tiers.
Targets from ideal §9.3: Logistics phase ≤ 1 ms at medium, ≤ 10 ms p99 at giant; path-cache rebuild ≤ 5 ms at
giant; the **whole End Turn** (hash + diff included, ideal §14b) timed by `trade-foundation`'s `Step`
benchmark with the phase on and off. The zero-allocation and volume-invariance properties are asserted in
the ordinary test suite so CI enforces them; the millisecond budgets are Bench readings reported against the
targets (a target missed is a finding to fix, never a number bumped).

- **Built:** the Bench project and its allocation-measurement precedent
  (`gk-core/tests/FusionRpg.Bench/AtomFormBench.cs:120-140`); an in-suite allocation precedent
  (`gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs:407-409`).
- **Wiring gap:** —
- **Real gap:** the logistics benches; nothing times a full `Step` yet (`trade-foundation` `step-benchmark`).
- **Depends on:** every module above; `trade-foundation` `step-benchmark`, `synthetic-graph`.
- **Touches:** `tests/FusionRpg.Bench/LogisticsBench.cs` (new); `tests/FusionRpg.Core.Tests/World/Logistics/LogisticsAllocationTests.cs` (new).
- **Acceptance (contract):**
  - After warm-up, one Logistics phase on the giant synthetic graph allocates **0 bytes**
    (`GC.GetAllocatedBytesForCurrentThread` delta), asserted in `FusionRpg.Core.Tests`.
  - **Volume invariance:** multiplying every stock and every in-transit quantity by 1000 changes neither the
    allocation nor the number of flow iterations (counted by an instrumented pass, not timed).
  - A turn with no graph change performs zero path rebuilds.
  - The Bench report prints medium and giant phase times, rebuild time and whole-`Step` time with the phase on
    and off, against the §9.3 targets.
- **Verification boundary:** `FusionRpg.Core.Tests` (allocation, invariance); `gk-core/tests/FusionRpg.Bench`
  (timings; Release, not in CI — its readings are recorded in `docs/research/perf/` beside
  `02-world-graph-write.md`).

---

## Tunables (keys owed by the specs; values decided by principle)

`data/tuning/trade.v1.json` (new), published through `gk-core/tools/tuning/publish.py`: `lane.throughputPerWidth`,
`lane.widenStep`, `lane.widenCostCurve`, `lane.wardCostCurve`, `lane.protectionPerWard`,
`lane.hostilePresenceMilli`, `lane.stanceEscortMilli.{stance}`, `goods.{id}.transitLossMilli`,
`goods.speedPerTurn`, `route.maxTransitTurns` (structural, commented),
`warehouse.deliveryOverflowWasteMilli` (read here, owned with the warehouse axis by `sector-yield`). The
refine rate is published into `siege.v{n+1}` because the siege domain owns the refine concept
(tunables-ssot §2: one domain owns a number; the other reads it).

## Filed asks (other maps)

| # | To | Ask |
|---|---|---|
| A1 | `trade-foundation` | `world-stamp` carries `trade.logistics` separately from `trade.sectorYield`; `synthetic-graph` seeds located goods, bank points, route policies and hostile presence on lanes, so `logistics-bench` needs no second builder |
| A2 | `sector-yield` | `banking-fact`'s `decisions.md` phase-order amendment names the step order this map fixes inside `Logistics`, so the row is right once (its `Assaults` half is already done upstream — C1) |
| A3 | `legion-build` | The `escort` stance lands as a stance id in `MovementPolicy.Stances` (`gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:22`) so `lane-loss` weights it through tuning; no other coupling is needed |
| A4 | `counterparties` | When `diplomatic-stance` changes hostility for a pair, the same step bumps the graph version (`path-cache` trigger T9) |
| A7 | `exchange` | Accepted from `exchange-map.md` E-A3: `path-cache` reads `passage` from `trade-access` (trigger T10). An `Access` change must bump the graph version in the step that derives it, so the cache never reads a stale level |
| A5 | `empire-seed` | Magnitudes for `refinery`, `causeway` and `convoy-depot` through tuning bands (all identity-only today) |
| A6 | `trade-surface` | Consume `logistics-facts`' closed token sets and `forecast-facts`' dry run; this map's forecast module is `forecast-facts`, distinct from that map's `throttle-forecast` UI module |
| A8 | `trade-surface` (round 4) | `throttle-forecast`'s closed four-answer vocabulary gains a `build-feature` answer (it renders `forecast-facts`' `build` [feature] rows), so *build a Counting House* is one click (Q3); `trade-unlock`'s first-throttle "show me" becomes that answer |
| A9 | power program (round 4 §P) | The `ssot-power-scale.md` §10 row for a contest between two rolled-up powers; `lane-loss`'s strength switch waits for it. *(The roll-up's owner is ruled — round 5 X7: `legion-build` `legion-power`, `LegionPower.Of`.)* |
| A10 | `legion-build` `escort-stance` | Publish the `lane.stanceEscortMilli.escort` row in the change that adds `escort` to `MovementPolicy.Stances` (`lane-loss` owns the key family and rejects a stance with no row); `fleet` `escort-link` then publishes nothing |
| A11 | `counterparties` `trade-difficulty-knobs` | `difficulty.{profile}.laneLossMilli` is read by `lane-loss` after the clamp and re-clamped; the hub it is read through must know every stamped profile id |

## Contradictions found

| # | Where | What | Recommended resolution |
|---|---|---|---|
| C1 | `docs/architecture/decisions.md` *World turn phase order* row vs code | The locked row listed nine phases; the engine runs ten — `Assaults` was added without amending the row (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:141,195`; `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107`) | **Resolved 2026-09-19 upstream** (verified in the audit of 2026-09-20): `decisions.md:7` now lists ten phases with `Assaults`. `banking-fact`'s amendment adds only `Logistics` (and should re-point the row's stale `TurnEngine.cs:180-195` citation to `:191-207`) |
| C2 | Ideal §5 *"`RulesetVersion = 12` (`:114`)"* plus *"old reports stop replaying after a bump"* vs D-C's per-world stamp | A global bump and a per-world stamp cannot both be the version gate | The stamp is the gate; the global constant becomes the newest ruleset the engine can run (`trade-foundation`) |
| C3 | `WorldLane.Width` comment (*"How large a force crosses at once"*, `gk-core/src/FusionRpg.Core/World/WorldState.cs:258`) vs ideal §8.4 (*"`Width` becomes throughput"*) | Two meanings, neither wired | Throughput is the one wired meaning; if a force-width rule is ever built it must read the same field, as `WardLevel` serves siege and logistics (recorded in `lane-flow`) |
| C4 | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:83-89` vs this map | The comment defers an automatic per-turn refine as "economically live" because the cap is unset | `construction-chain` replaces the unset cap with a structural per-turn rate per refinery; the comment is updated in that change |
| C5 | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:6-9` (*"Unwired — … nothing here is called from `TurnEngine` yet"*) vs `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:349` | A stale comment: `LegionSupply.Resolve` runs in Pressure | Not this map's file; recorded so `fleet` (which reads bearer capacity) does not trust it |
| C6 | Ideal §11 row 3 (`logistics-flow` owns *"the Logistics phase"*) vs `sector-yield-map.md` §2.9 (`banking-fact` *"creates the `Logistics` phase slot"*) | Two sub-programs claim the phase | Resolved in this map: the slot is born with `banking-fact` (it lands first and needs it); `logistics-flow` owns the flow steps, their order and the `trade.logistics` flag (`logistics-phase`). No phase is created twice |
| C7 | `sector-yield-map.md` §2.9 (*"An AI empire's fact credits a per-world, hashed treasury on its faction"*) vs `counterparties-map.md` module 4 `empire-treasury` (*"its banking hook in the Logistics phase (`logistics-flow` calls it, this module owns the balance)"*) | Two maps define the AI treasury, and one says `logistics-flow` calls it | `logistics-flow` never touches a treasury — banking is `banking-fact`'s step. The two sibling maps must pick one owner for the balance (recommended: `counterparties` `empire-treasury` owns the field, `banking-fact` credits it). *(Ruled 2026-09-20, X3: `empire-treasury` owns and writes it, registered into `banking-fact`'s destination seam.)* |
| C8 | Namespaces across sibling maps: `trade-foundation` `routing-guard` scans `src/FusionRpg.Core/World/Logistics/**`; `counterparties-map.md` proposes `World/Trade/…`; `sector-yield-map.md` proposes `World/Goods/…` | A routing file placed outside `World/Logistics/` escapes the `ReconnectionCost` guard | This map and `fleet` put every file under `World/Logistics/`. Any sibling that plans routes (e.g. `trade-ai`) must too, or the guard's path list widens in the same change |

## Owner questions (closed 2026-09-19)

| # | Question | Recommendation |
|---|---|---|
| Q1 | **How does lane loss read an escort's (and a hostile presence's) strength?** The ideal says an escort's *strength* feeds `escortMilli` (§8.3; `legion-build-ideal.md` §6.5; `legion-build-map.md` `escort-stance`), but no strength read exists for a whole legion: `ForceStrength.Of` is fog-only by its own contract (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`), and inventing one would be a private power curve (§10's closed inventory). | **v1: presence, not strength.** `escortMilli` and `hostilePresenceMilli` are flat per posted legion, by stance, from tuning — no actor number is read, so no curve and no Hub coupling. **Later, as a reviewed change:** once `legion-build`'s `general-member-hub` and `stack-combatant` give a legion a Hub-composed Θ, the two terms become a **Θ-difference contest** (own posted vs hostile posted) through the existing `CombatProbability.Sigmoid` — contests read `Θ`, one ladder, consume Hub output only. Default if unanswered: the v1 rule, which is reversible (a tuning table). **Decided 2026-09-19 (OD1):** v1 escort strength is a tuning-weighted count of escort-stance legions; the contest replaces it once `legion-build` provides a Hub-composed power index |

Everything else is decided in the ideal (§8, §9, §14, §14b) or here by an existing rule, and each such
choice says which rule: goods use the Supply lens (one traversal rule with supply); own and unheld ground
is open, foreign ground only under `passage` (ideal §7.6); the refine rate is a structural per-turn limit (ideal §3.15);
stranded goods keep taking loss and return on `route-clear` (no rating spiral, ideal §6 lesson 6). Any of
these is overturned by a sentence from the owner at map review.

---

## DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: world turn engine, world lanes/topology, economy
    (located goods, banking, construction stocks), tunables, numeric range, performance, battle
    (WardLevel's siege reader only).
[~] Session boundary: this work runs under the existing record
    tasks/sessions/trade-network-idea-20260919.json, whose paths include
    docs/architecture/trade-network/**. I did not run scripts/session-boundary-check.py myself
    in this session; the record's own notes log its crossing check.
[x] I read every doc in the §1 rows this session: Anything-at-all (software-architecture.md,
    decisions.md), Economy (empire-resource-ssot.md, empire-economy-ssot.md §5-§7,
    economy-principles.md headings and P-rules), Any cap (ssot-power-scale.md §11), Tunables
    (tunables-ssot.md §1-§3), Numeric (PRINCIPLES.md §5, ssot-power-scale.md §9.4, §10.4),
    Performance (perf-probe-plan.md, research/perf/00-baseline.md headings, 02-world-graph-write.md),
    World map (world-map-program.md, world-map-runtime-map.md), Battle (battle-engine-ssot.md §4-§5).
    Honest gap: match-runtime.md, unique-actor-runtime.md, battle-timeline-map.md, battle-turn-ideal.md,
    spec-world-map-runtime.md, spec-world-map-gaps.md and the two world-map-runtime plans were skimmed
    by heading only — none governs world-turn logistics, but they were not read in full.
[x] I checked decisions.md for a lock covering this: the phase-order row (C1), Scoped inventory,
    Empire resource registry, Power scale, Caps, Magic numbers, World store — delve worlds.
[x] Every factual claim cites file:line (the "What the code says" table and each module).
[x] audit-doc-citations.py --scope on this file: see the session report; no HIGH finding left.
[x] I verified claims against CODE, not comments (Width has no reader; Refine has no production
    caller; Severed has no writer; the Assaults phase exists) — and flagged two stale comments (C4, C5).
[x] I read the surrounding section of every rule I quoted (decisions.md phase row in full;
    SiegeConstruction's class and Production docs; SupplyGraph's traversal and besieged rules).
[~] Constraints tested, not assumed: none claimed. "Old-stamp worlds replay byte-identically" is an
    acceptance criterion to be proven by the goldens, not a claim made here.
[x] Nothing contradicts a §2 invariant (RPG-layer only, deterministic, no ceilings, one ladder,
    SOLID: one phase in one engine, one hostility rule, one traversal lens).
[x] Corrections propagated: this map only; C1-C5 name the owning documents to fix.
[x] No assertion pins a population count: closed vocabularies (report kinds, loss causes, bottleneck
    reasons) are pinned with a reason; flows, entries and goods counts are never asserted.
[x] Event-refreshed cache (§2.16): path-cache lists all ten triggers including the four key-set
    edges (T5, T7, T8, T10), one test each, plus a fingerprint cross-check for a forgotten trigger.
[x] Orderings: path-cache, transit-buffer state order-independence and test both orders.
[x] Actor magnitudes: none produced or consumed in v1 (Q1's recommendation: presence by stance, no
    strength). The deferred strength read, if the owner takes it, consumes Hub output only — never a
    private fold — and is a reviewed change.
[x] No SOLID-violating parallel path: one phase, one flow pass, LaneGraph/LaneCost/SupplyReach reused,
    RefineGated called rather than re-derived, WardLevel kept as one field for two readers.
[ ] Registry row for new rules: the ReconnectionCost ban and the WardLevel single-field guard need
    rows in gk-core/scripts/enforcement-registry.v1.json when their guards land — owed by those modules' specs.
```

## Reconciliation 2026-09-19 (round 4)

Applied from [decisions-round-4.md](decisions-round-4.md), which wins over any spec. Cross-checked against
every other trade-network, `world-continuity`, `legion-build` and `empire-seed` spec.

| # | Change | Where |
|---|---|---|
| L1 | **Bank points are Counting Houses** (round 4 §B): auto-banking's default destination, path-cache trigger T7 (a Counting House finishing, destroyed or captured; a tier change is not a trigger) | `spec-auto-banking.md`, `spec-path-cache.md` |
| L2 | **`bank-hold` policy command** (Q2): keeps a quantity of a good at a Treasury-tier bank point; state and application are `sector-yield` `banking-fact`'s; `trade-ai` files it the same way (exchange E-A11) | `spec-auto-banking.md` §2a |
| L3 | **Banking is rate-limited** per Counting House tier, so a bank point is no longer an unbounded sink: L1 unloads up to room at every destination, L4 unloads into room banking freed before anything wastes; the first draft's "a bank point never overflows" is withdrawn | `spec-logistics-phase.md`, `spec-transit-buffer.md` |
| L4 | **First-throttle answer = build a Counting House** (Q3): `forecast-facts`' answer table gains `build` [feature] rows (banking, storage), with `no-path` answered first by `build` [banking] | `spec-forecast-facts.md` §2 |
| L5 | **Storage is a building** (§B): a sector with no storage has no room; deliveries to it wait and waste, and halts there are answered by `build` [storage] | `spec-transit-buffer.md`, `spec-forecast-facts.md` |
| L6 | **Escort strength → power roll-up** once its §10 row exists (§P); v1 count until then; the switch is a stamp capability | `spec-lane-loss.md` §4, OD1 |
| L7 | Phase-internal order corrected here to the spec's (banking before overflow) and extended with the reserved rift steps (rift A11) and the after-passes in order: settlement, then clan economy (counterparties A12) | this map; `spec-logistics-phase.md` §Design 1 |
| L8 | Asks answered in the specs: lane-loss difficulty multiplier and the pure `LaneLoss.Milli` signature (counterparties knobs; rift `crossing-leg`); the escort row's owner (A10); consignments as lane-flow sources (exchange E-A5); `widen` on a crossing anchor (rift A8); `PathCache.Next` for fleet (A9); `qty=` on `logistics.short` (trade-surface); rift widenings of the report vocabulary | `spec-lane-loss.md`, `spec-lane-flow.md`, `spec-lane-verbs.md`, `spec-path-cache.md`, `spec-logistics-facts.md` |
| L9 | Income parity is **not** this sub-program's (Q11 moves it to `sector-yield` `income-parity`); the umbrella's §1 sentence placing it here was stale *(fixed 2026-09-20, round 5 X6)* | — |
| L10 | Plan/task paths corrected to the umbrella convention; one `TradeTuning` location (`World/Trade/`); stale `TurnEngine.cs`/`WorldCommand.cs`/`WorldCommandAdmission.cs`/`WorldState.cs` citations re-pointed after `RulesetVersion` 13 (the "What the code says" row now reads 13) | header; specs |
| L11 | C7 closed: CM3 plus `banking-fact`'s destination seam — `counterparties` `empire-treasury` writes the AI treasury; logistics touches no treasury | C7 |
| L12 | Spec-time deviations from this map's module text, restated here so the map is not read against its specs: `auto-banking` lets a world stock be routed to a bank point (it never banks); `forecast-facts` dry-runs the whole `Step`, not the phase alone; `logistics-facts` drops "destination full" as a short reason (a full destination waits and overflows) and keeps utilisation out of the report; `lane-flow` bounds committed departures per lane per turn, not every crossing; `logistics-phase` bounds kernel allocation, not write-back | the named specs |

**Closed vocabularies this reconciliation widens:** `WorldCommandKinds` +`bank-hold` (with `route-set`,
`route-clear`, `widen`, `ward` already planned); `bank-hold`'s drop reason `bank.hold-needs-treasury`;
`forecast-facts`' answer table (+`build` rows carrying a `SectorFeature`); the report token sets gain
`qty=` on `logistics.short` and, from `rift-trade`, rift kinds and `crossing.*` short reasons; the
`logistics-phase` step list gains the reserved rows L4r, A1, A2.

**Cross-cluster items this map cannot fix (other owners' files):**

- `trade-surface/spec-throttle-forecast.md` pins a closed four-answer vocabulary without *build*; round 4 Q3
  needs a fifth (A8). `spec-trade-unlock.md`'s first-throttle remedy should be that answer.
- `exchange/spec-order-book.md` quotes the draft order (*arrivals → overflow → banking*); the fixed order is
  banking before overflow. *(Round 5 X5 makes this spec's L0–L8 order canonical; `exchange` must quote it.)*
- `legion-build/spec-escort-stance.md` says the escort row is logistics-flow's; `fleet/spec-escort-link.md`
  publishes it. Recommended (A10): `legion-build` publishes it with the stance; lane-loss owns the family.
- `trade-stories-map.md` attributes banking facts to `logistics-flow`; they are `sector-yield` `banking-fact`'s.
- `world-continuity/spec-coarse-step.md` runs no Logistics or banking on a hibernating world — consistent with
  continuity §6.6 (background yields are never banked without collection); no change asked.

## Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A, R5-X), which wins over any spec.
Citations touched were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| LR1 | **X5:** `logistics-phase` §1's L0–L8 table (with L4r, A1, A2) is the **canonical** step order for every program; the umbrella (§1, CM4) and `sector-yield` (`banking-fact`, map D2) now quote it instead of "flow, loss and delivery ahead of banking" | `spec-logistics-phase.md` §1 (unchanged); §1 prose above |
| LR2 | **X7:** the power roll-up is `legion-build` `legion-power` (`LegionPower.Of`); `lane-loss`'s strength switch reads it; ask A9 now asks the power program only for the §10 contest row | `spec-lane-loss.md` §4; asks A9 |
| LR3 | **A4 / X15:** the default banking hold is enough to fill other traders' open buy orders at this hub; `bank-hold` stays the commander's override | `spec-auto-banking.md` §2a |
| LR4 | **A1 / A2:** every seat starts with a Counting House (the default destination exists from turn 1) and every held sector has a base yard, so the forecast's "no storage (capacity 0)" row becomes "base yard full, no storage building" | `spec-auto-banking.md` header; `spec-forecast-facts.md` |
| LR5 | **X6:** income parity is `sector-yield`'s; `RulesetVersion` 13 (already stated in the "What the code says" table, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`) | L9 |
| LR6 | **X14:** unchanged here — `path-cache` and `lane-loss` already read hostility and `passage` from the logged band snapshot (CM1) | `spec-path-cache.md`, `spec-lane-loss.md` |

**Still other owners' files:** `exchange` `order-book` quotes the canonical order and counts other traders'
open buy orders for the hold source (A4); the power program's §10 contest row (A9).

## Audit 2026-09-20

An independent audit of this map and its twelve specs against CLAUDE.md, AGENTS.md, DESIGN-GATE §2–§5
(§2.16 in particular), PRINCIPLES, tunables-ssot, validation-ssot, the test-substrate standard,
economy-principles, `ssot-power-scale.md` §10–§11 and the round-4/5 register, with the load-bearing claims
re-opened in code on `features/mega-merge`. `audit-doc-citations.py --scope` reported 0 HIGH on every file
before and after the edits. Specs win over this map where they differ; module text above that the specs
superseded is left as approved and listed here.

| # | Severity | Finding | Fix |
|---|---|---|---|
| LF-A1 | Critical | **No logistics step recorded a stock delta.** A grep of every spec in `logistics-flow/` for `stock-delta`, `StockDelta`, `factKind` or `LocatedStockOps` found nothing, yet `sector-yield` `located-stock` makes `LocatedStockOps.Add` (with its delta) the only writer of a warehouse and `trade-foundation` `stock-deltas` fails any unrecorded change. Departures, arrivals, returns, lane loss, delivery waste, refine and lane-verb payments would each have broken the reconciliation and left the world-stock ledger unable to explain a single flow | `spec-transit-buffer.md` §5a (route holder `r:`; `depart`/`deliver`/`return`/`loss`/`waste`, one table), `spec-lane-flow.md` §6, `spec-lane-loss.md` §2, `spec-construction-chain.md` §1 (`refine`), `spec-lane-verbs.md` §2 (`construct`); `spec-logistics-phase.md` acceptance 6 asserts the whole phase closes. The holder and kinds are widened in `trade-foundation` (`ledger-keys` §4a, `stock-deltas` §5) |
| LF-A2 | Critical | `logistics-phase` said `RulesetVersion` never moves for logistics, while `world-stamp` grants by `stamp.RulesetVersion >= IntroducedAtRuleset`; without a bump `trade.logistics` would be granted to worlds stamped before logistics existed | `spec-logistics-phase.md` locked anchor, hard edges, boundaries and acceptance 7: one bump births the capability row; the stamp stays the gate (`trade-foundation-map.md` TF-A1, OQ1) |
| LF-A3 | Major | `path-cache`'s trigger set (DESIGN-GATE §2.16) omitted the two edges that **resize** the key — a faction or a sector added to or removed from the world — and the key had no index part, so a resized world could compare equal element by element; the per-world `LogisticsRuntime` memo's own lifetime edges (a rolled-back commit, a cold or evicted runtime, a coarse-stepped world, a reused world id) were not enumerated or tested | `spec-path-cache.md`: an `Index` key part; triggers T11, T12 (both key-set edges) and memo edges E1–E4, one test each; acceptance 2 and 6 |
| LF-A4 | Major | `transit-buffer` acceptance 6 and its test plan said "only at a non-bank destination" / "a bank point wastes nothing", contradicting its own §5 and `logistics-phase` §Design 1 since round 4 made banking rate-limited | Acceptance 6 and the test rewritten to "waste only what is still `AtDoor` after L4's second unload" |
| LF-A5 | Major | `transit-buffer` §5 still said a sector with no storage building has no room (round 4), replaced by round 5 A2's base yard | Corrected |
| LF-A6 | Major | `forecast-facts` claimed "faithful by construction" but fed `Step` only an empty command list; `Step` also takes logged per-turn inputs (pending `located_income`, and the band snapshot once `counterparties` lands), so the forecast would diverge the first turn a delve drop was pending | §1: the forecast receives exactly the logged inputs the next commit would pass, gathered by the same Data function; acceptance 6 |
| LF-A7 | Major | `lane-verbs` let the siege depth product throw inside `Step` at a high `WardLevel`, which would fail the whole End Turn for every faction | §5: the resolver refuses a level whose arithmetic would overflow (`ward.level-unrepresentable`, `widen.level-unrepresentable`) — an absolute bound derived from the type range, not a tunable cap; acceptance 6 |
| LF-A8 | Major | `logistics-bench` adds `tests/FusionRpg.Bench/LogisticsBench.cs`, but `gk-core/tests/FusionRpg.Bench/**` has no verification boundary (`verify-change.ps1 -PlanOnly` stops on it, run in this audit); `construction-chain` publishes `siege.v{n+1}`, and `gk-core/data/tuning/**` has no mapping either | An owner row `logistics-bench` (bench + allocation tests) and a `siege-tuning` row (each published version as an exact path — the matcher takes exact paths and `dir/**` only, `scripts/verify-change.ps1:70-75`) |
| LF-A9 | Minor | `lane-loss` required one `goods.{id}.transitLossMilli` row per located id, which for legion pieces couples the tuning file to a seeded population (validation-ssot §1) | One family row `goods.legion-piece.transitLossMilli`; the per-id rows cover only the closed vocabularies |
| LF-A10 | Minor | `auto-banking` did not say what happens to a policy whose **source** sector is captured; `banking-fact`'s `bank-hold` state lacked its setter | Policies are commander-owned and go dormant on a lost source, revive on retake (acceptance 8, both orders); `BankingHolds.Set` carries the setter |
| LF-A11 | Minor | `logistics-facts`' token-set table was cut in two by a prose paragraph, orphaning the "Route details" row | Table repaired |
| LF-A12 | Minor | `construction-chain` repurposes the siege key `refinePerTurnCap` as a **rate**; the name says "Cap" | Kept (the siege domain owns the name); the reader's comment must say "rate, uncapped in count"; a rename to `refineRubblePerRefineryPerTurn` is recommended to the siege domain |
| LF-A13 | Minor | Map text superseded by the specs and not yet flagged: module 3's "hashed graph-version counter" and "no T1–T9 event" (the spec uses an exact key and T1–T12), module 1's "never by a global `RulesetVersion` move", module 6's "appear in no … ledger credit" (a loss now leaves a negative `loss` delta, never a credit), C1 (resolved upstream) | C1 and ask A2 updated; the rest recorded here, specs authoritative |

**Checked and found sound:** one phase in the one engine with a tested step order; the pro-rata split by
demand with turn-rotated remainders (no faction-id tiebreak); loss as a commented bounded ratio and a pure
sink; `Width`/`WardLevel` growing without a cap on a rising price ladder with its §10 row owed; the
structural buffer bound and refine rate commented as such; the kernel zero-allocation boundary stated
honestly; `ReconnectionCost` banned by `routing-guard`; the v1 escort count reading no actor number (the
power roll-up switch consumes Hub output only, round 5 X7); loam never routed; world stocks never banked
(guarded); in-memory store tests; no population pinned. RPG layer only.

**Could not fix here (other owners' files):**

- `exchange/spec-order-book.md` must quote the canonical L0–L8 order and count **other traders' open buy
  orders** for the hold source (round 5 X5, A4) — owner `exchange`.
- `trade-surface/spec-throttle-forecast.md` needs the `build-feature` answer (ask A8) — owner
  `trade-surface`.
- The power program owes the §10 contest row the lane-loss strength switch waits for (ask A9).
- The siege domain owns `refinePerTurnCap`'s name and its loader rule change (LF-A12).

No new owner question beyond `trade-foundation-map.md` OQ1 (the stamp model), which LF-A2 depends on.

---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6". The family's single landing order is
[landing-order.md](landing-order.md); this sub-program occupies rows 5, 6, 7, 9 and 23 of its §2.

| # | Decision | What changed in the specs |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | The map's four waves had **one** flag, `trade.logistics`, which wave 1 registers — so a world stamped after wave 1 would have gained lane loss, transit buffers and the refine step mid-life when waves 2 and 3 merged (the audit's C1, evidenced at `spec-lane-flow.md`, `spec-lane-loss.md`, `spec-construction-chain.md`). Now one flag per wave, each with the wave's one bump: **W1** `trade.logistics` (`logistics-phase` registers it, `logistics-canonical` shares the bump); **W2** `trade.logisticsLanes` (`path-cache`, `lane-flow`, `transit-buffer`, `lane-loss`, `logistics-facts`); **W3** `trade.logisticsPolicy` (`auto-banking`, `construction-chain`, `lane-verbs`); **W4** `forecast-facts` + `logistics-bench` take **none** — *"the forecast writes nothing"* and the bench is a test (the one case a spec may still say "no bump"); **W5** `trade.laneLossPower` for the §4 strength switch, which lands only when the power program's contest row exists (ask X-2) |
| **C2** | One neutral `StructureKind.Feature` | No spec here names a `StructureKind`. What it unblocks: `auto-banking`'s default destination is *the nearest bank point*, which is a Counting House read through `sector-features` — until C2 the row could not load and every sector read tier 0 |
| **C3** | Banking waits on the save-identity re-key | `spec-auto-banking.md` Hard edges: this wave lands **before** anything banks, because `banking-fact` splits its landing (its §1a) into the phase slot (no ledger) and the banking step (after `material-ledger`). Interim: goods flow to the nearest bank point, the `bank-hold` state is set and stored, the hold source seam registers — and nothing leaves the map. No acceptance criterion here asserts a banked total. `spec-logistics-phase.md` §1 says the same for L3 being present and empty |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | Every building read in this sub-program is already indirect: `auto-banking` reads bank points through `sector-yield` `bank-points`, `construction-chain` reads the refinery through `sector-features`. Both now inherit `TierFor`'s S1 rule from `sector-features` §5a and add no owner test of their own |
| **S2 / W1 / W2** | Trade goods cross worlds only by rift route | Unchanged here and worth stating: L4r is a **reserved position** this map fixes and `rift-trade` fills. Nothing in a lane step moves a good between worlds, and an advance is `world-continuity`'s weight-limited transit, not a lane |
| **CQ2** | Legion equipment and doctrine upkeep may draw banked goods | No change: this sub-program moves goods and never spends them. The draw is `counterparties` `empire-goods-sinks`' (AI) or the wallet's (player) |
| **D2** | Six `world.*` channels compose in `ActorHub` | `spec-lane-loss.md` new §4a: `world.hazard.resist` is this sub-program's channel. It is read as **Hub output rolled up per legion the way `legion-power` is** — never a local fold of species/equipment/standard/doctrine contributions — and its **stated default until `world-derived` ships is 0**, so today's `hazard − ward × protection − escortMilli` is unchanged. It joins the same subtraction and the same floor, behind the same `trade.laneLossPower` wave as the escort strength switch, because both replace a count with a Hub read |

**Superseded map text.** The module table's Wave column still reads 1–4; those waves are right, and their
flags are now per-wave as above. LF-A13's list of stale map lines stands, with one more: module 1's
*"a world whose stamp grants `trade.logistics`"* is wave 1's flag only.

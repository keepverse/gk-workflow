# Capability map: `rift-trade`

**Status: APPROVED 2026-09-19.** The owner approved this map and decided Q1 and Q2 (see *Owner decisions*
below). **Reconciled with the round-4 owner decisions 2026-09-19** ([decisions-round-4.md](decisions-round-4.md))
— see *Reconciliation 2026-09-19 (round 4)* at the end; where this map and that register disagree, the
register wins. Sub-program 11 of the [trade-network](../trade-network-ideal.md) umbrella (ideal §11), built on
[world-continuity](../world-continuity-map.md)'s world states.
**Specs (written 2026-09-19):** [rift-route](rift-trade/spec-rift-route.md) ·
[crossing-anchor](rift-trade/spec-crossing-anchor.md) · [crossing-leg](rift-trade/spec-crossing-leg.md) ·
[crossing-handoff](rift-trade/spec-crossing-handoff.md) · [sleeping-endpoint](rift-trade/spec-sleeping-endpoint.md) ·
[endpoint-loss](rift-trade/spec-endpoint-loss.md) · [crossing-goods](rift-trade/spec-crossing-goods.md) ·
[rift-facts](rift-trade/spec-rift-facts.md).
**Plan / tasks:** `tasks/trade-network-rift-trade-plan.md` / `tasks/trade-network-rift-trade-todo.md` (new) — the
umbrella's path convention (`trade-network-map.md` §6); this map's draft named `tasks/rift-trade-*.md`.

**Ideals it implements:** [trade-network-ideal.md](../trade-network-ideal.md) §8.3 (cross-world routes),
§11 row 11; [world-continuity-ideal.md](../world-continuity-ideal.md) §6.8 (*"A route may join trade hubs in
two worlds the player holds. It follows trade-network's rules — located goods, throughput, loss, ledger facts
— with one extra leg: the crossing between worlds, priced and bounded like a lane"*), §6.6 (background yield
is collected by visiting, cargo or a cross-world route), decision W6. It does not reopen any decision.

**Vocabulary.** `rift-trade` is the program id only. Player-facing text says *cross-world route* and
*crossing* (ideal §14b's generic strategy terms); it never names an engine type.

---

## What this sub-program is

A **cross-world route** joins a crossing anchor — a **Rift Anchor** building (round 4), in a world where the
player also holds a working **Grand Exchange** — in one world the player holds to a crossing anchor in
another. Goods reach the source anchor by that world's ordinary logistics, cross between worlds over a
**crossing leg** that has a throughput, a transit time and a loss exactly like a lane, and land in the
destination anchor's warehouse, from where that world's ordinary logistics takes them on — to a bank point,
a construction site or a trade hub. It is how a mature old world feeds the frontier of a new one, and how
background yield in a hibernating world gets collected without a visit.

**The fact that shapes everything below:** exactly one map world per save is `active`
(`world-continuity-map.md` assumption 2 — a SQL-enforced fact once `world-state-vocabulary` lands). So **every
cross-world route has at most one endpoint that steps each End Turn**; the other end is hibernating
(lazy coarse steps), idle (expedition wall clock) or fallen. Designing for the sleeping endpoint is the main
case, not an edge case.

**Loops:** Place 5 (world stage — anchors and crews in held sectors), Place 4 (world map — the far world is
still a map you hold), Place 2 (idle — an idle world's output leaves by route). No fourth clock: transit is
counted in the save-scoped End Turn counter world-continuity already adds. Nothing touches the lawn or PvZ.

### Load-bearing rules restated

1. **Never step N full worlds per End Turn** (world-continuity ideal §3.2). A route never causes a `Step` or
   `CoarseStep` of a world that would not otherwise run; the sleeping side's share is computed **inside** the
   coarse step or idle collect that world-continuity already schedules.
2. **Every cross-world effect is a logged input to the affected world** — a system-issued `WorldCommand` filed
   into its durable command list for a full step (`world-continuity-map.md` assumption 4; the seam at
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:539`), a field of the coarse or idle record for a sleeping
   world. A world's hash and replay never read another
   world's state; goods between worlds live in a save-scoped **crossing ledger** (P14), never in a second
   world's hash.
3. **Leaving must never pay better than staying** (world-continuity ideal §3.3). A route adds no yield; it
   only moves yield that background production already made, at a loss.
4. **Loam never crosses worlds**; recruits never cross (accrual meter). Rubble and ironwork may cross and are
   never auto-banked (owner decision Q2).
5. **One mechanism.** The crossing leg reuses `logistics-flow`'s throughput, transit and loss functions with
   crossing-specific tunables; crews and the one labour-to-output evaluator are `fleet`'s; the anchor is its
   own **Rift Anchor** building (round 4 — no longer a `fleet` depot) whose tier-free presence and whose
   world's Grand Exchange are read through `trade-foundation` `sector-features`; banking is `sector-yield`'s;
   system-issued commands go through `trade-foundation`'s one path (round-4 Q10).
6. **Determinism, numbers, tunables** as in `logistics-flow`: `long`, `checked`; loss a bounded ratio clamped
   to [0, 1000] ‰; every balance number in `data/tuning/trade.v{n}.json` (new) — the crossing is a trade
   concept, so its keys live in the trade domain (`world-continuity-map.md` tunables: *"Cross-world crossing
   cost is `rift-trade`'s"*).

## Assumptions (correct before approving)

1. `world-continuity` lands, at least: `world-state-vocabulary` (states and `outcome`, one active world),
   `hibernation-clock` (the save-scoped End Turn counter), `coarse-step` (with an `inputs` parameter),
   `idle-world` (collect on the wall-clock pattern), `world-fall`, `background-yield` (output into
   warehouses, never into a wallet), `away-digest`.
2. `logistics-flow` and `fleet` land first (ideal §11: *"Sub-program 11 follows 3 and 4"*).
3. A route joins **two worlds of one save and one empire**, both held by the player; it is never a trade
   with another faction (foreign trade in either world is `exchange` + `fleet`, unchanged).
4. The capability flag `trade.riftTrade` rides `trade-foundation`'s `world-stamp`; a world without it cannot be
   an endpoint, so a legacy world never has cross-world effects.

---

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| `rpg_worlds` carries `state` (default `'active'`), `mode`, `turn_period_seconds`, `catch_up_cap`, `last_advanced_utc`; `catch_up_cap` is never read | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:25-36` |
| Several worlds per save already coexist (`kind`, `parent_world_id`) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:204-206` |
| The "active world" is the first active map world by id, not a chosen one | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:415-428` |
| The only `UPDATE rpg_worlds` is the turn advance; nothing ends or sleeps a world | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:683-690` |
| A world's commands are read from its own durable list inside the commit, just before resolution | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:537-539` |
| `Step` is pure over one world's state and commands | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-163` |
| Replay refuses a log whose engine/ruleset differs | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-760` |
| Lazy, pure idle resolution: dispatch stamps a seed and times, resolution happens at collect | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-62`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:71-93` |
| A `Tear` slot kind ("Rift Tear") exists and is buildable — but neither shipped template places one | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:15,71`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs` and `WorldTemplateCatalog.TwoHearths.cs` contain no `tear` slot |
| No code moves anything between two worlds | world-continuity ideal §4 *Real gap*; `world-continuity-map.md` `advance-carry` real gap |
| The P14 ledger pattern (durable, deduped fact rows) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:147,234` |

---

## Modules

Stable kebab-case ids, chosen once. Model-free throughout.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `rift-route` | The save-scoped route record between two held worlds' anchors; set/clear; admission; the per-resolution route window, a logged system-issued input to each endpoint world | `world-continuity` `world-state-vocabulary`; `trade-foundation` `world-stamp`, `ledger-keys` | 1 |
| 2 | `crossing-anchor` | A working own **Rift Anchor** (a `cross-world`-feature structure, one tier — `trade-foundation` `sector-features`) as a world's end of the crossing, working only while that world holds the owner's working **Grand Exchange** (trade tier 4); crew-staffed through its own `crossing.throughputCurve`; a site bonus when the anchor's sector holds a rift-tear slot; the far-end view | `rift-route`; `fleet` `crew`, `depot` (`LabourCurve`); `exchange` `exchange-hub` (the trade building's tiers); `trade-foundation` `sector-features`; `empire-seed` `trade-structure-rows` (ask A13) | 1 |
| 3 | `crossing-leg` | Throughput, transit (in save End Turns) and loss for the crossing, through `logistics-flow`'s functions; `widen` applies | `crossing-anchor`; `logistics-flow` `lane-flow`, `transit-buffer`, `lane-loss`, `lane-verbs` | 2 |
| 4 | `crossing-handoff` | Departure out of the source world's hash into the crossing ledger; arrival as a system-issued command into the destination world's Logistics phase, filed through `trade-foundation`'s one system-command path (round-4 Q10) | `crossing-leg`; `world-continuity` `hibernation-clock`; `trade-foundation` `stock-deltas` and its system-command path (ask A7) | 2 |
| 5 | `sleeping-endpoint` | The hibernating and idle sides: exports and imports resolved inside `CoarseStep` or the idle collect, in closed form, never forcing a step | `crossing-handoff`; `world-continuity` `coarse-step`, `idle-world`, `background-yield` | 3 |
| 6 | `endpoint-loss` | An anchor lost or a world fallen: suspension, return of goods still in the crossing, no stranded faucet | `crossing-handoff`; `world-continuity` `world-fall` | 3 |
| 7 | `crossing-goods` | The closed table of what may cross, and guards: loam never, recruits never, located goods and legion equipment yes, world stocks per Q2, nothing ever banks on the crossing | `rift-route`; `sector-yield` `located-goods-registry` | 1 |
| 8 | `rift-facts` | Report and digest entries for departures, arrivals, crossing loss and suspension, fog-scoped per world | `crossing-handoff`, `endpoint-loss`; `world-continuity` `away-digest`; `logistics-flow` `logistics-facts` | 3 |

**Build order:**

```
Wave 1  rift-route ∥ crossing-goods → crossing-anchor
Wave 2  crossing-leg → crossing-handoff          (active ↔ active-then-hibernating, the first playable case)
Wave 3  sleeping-endpoint ∥ endpoint-loss → rift-facts
```

**Dependency direction.** Everything points at `world-continuity`, `logistics-flow`, `fleet`, `sector-yield`
and `trade-foundation`; none of them depends on this map (`world-continuity-map.md`: *"Consumes this
program's states; not a dependency of it"*). No cycles.

---

## What flows when the far world is hibernating (or idle, or fallen)

The question the owner named, answered as the contract `sleeping-endpoint` and `endpoint-loss` build:

| Far world is | Goods **out of** it (it is the source) | Goods **into** it (it is the destination) | Clock |
|---|---|---|---|
| `active` (incl. *developing* = active + won) | Its Logistics phase moves goods to its anchor; the crossing departs them each End Turn | Arrivals enter its Logistics phase as system-issued commands at their arrival counter | Save End Turn counter |
| `hibernating` | Nothing steps. When world-continuity runs its `CoarseStep` (on a visit or its small background budget), the route's drain is one of the step's **inputs**: over the `n` pending turns (capped by `catch_up_cap`), exports = min(crossing throughput × `n`, what background production and the anchor's warehouse hold), minus crossing loss, in closed form. Each export is ledgered once per good at the counter the coarse step runs, arriving `crossing.transitTurns` later (no back-dating — `sleeping-endpoint`); an arrival already in the past lands at the next step, never retroactively | Arrivals queue in the crossing ledger and land in its anchor warehouse at its next `CoarseStep` (as that step's input), capped by warehouse capacity — overflow wastes by the delivery rule (decision 22). It never auto-banks there (world-continuity `background-yield`) | Save End Turn counter, lazily |
| `idle` | The route's draw is an **idle collect** (world-continuity `idle-world`), resolved Data-side outside `Step` like an expedition collect and handed to the crossing as a logged input, bounded by crossing throughput per active End Turn; the uncollected remainder stays credited inside the idle world's capped window | Arrivals land in the anchor warehouse at the idle world's next collect/resolution (an input to it) | Expedition wall clock for the idle side; save counter for the crossing |
| `fallen` (or the anchor sector lost) | The route **suspends** the turn the anchor is not held; nothing departs | Goods still in the crossing toward it **return to the origin anchor** at their arrival counter (loss already applied, nothing re-created); the route stays suspended until cleared or the anchor is retaken | — |

In every row: a route never adds production; it collects what the far world made at the background
multiplier, and it loses a share on the way. That is how "leaving must never pay better than staying" and
"background yield must be collected" hold at once.

---

## Module detail

### 1. `rift-route`

**Capability.** The route record: source world and anchor, destination world and anchor, goods and a per-turn
share (policy), priority. Save- and empire-scoped Data (a route belongs to neither world's hash). Setting or
clearing one is a player verb on the server. A world learns about its routes only through a **route window**
logged at each of its own resolutions — a system-issued command for a full step, a field of the coarse or idle
record otherwise — so each world's replay is self-contained and no per-world policy has to be invalidated
(world-continuity assumption 4; spec Design 4). Admission:
both worlds belong to the same save and empire, both stamps carry `trade.riftTrade`, both anchors are working
(a Rift Anchor held by the player, in a world where the player holds a working Grand Exchange — round 4), and
the two worlds differ. Routes between **two sleeping worlds** are allowed (resolved lazily on
both sides) — refusing them would suspend every route the moment the player switches worlds.

- **Built:** several worlds per save (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:204-206`); the command-list seam
  (`RpgStore.WorldTurns.cs:537-539`).
- **Wiring gap:** the active world is first-by-id, not selected (`RpgStore.World.cs:415-428`) —
  `world-state-vocabulary`'s.
- **Real gap:** the route record, its verbs, its system commands.
- **Depends on:** `world-continuity` `world-state-vocabulary`; `trade-foundation` `world-stamp`, `ledger-keys`.
- **Touches:** `src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs` (new); `src/FusionRpg.Core/World/Logistics/Rift/RiftRoute.cs` (new);
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (set/clear routes).
- **Acceptance (contract):**
  - A route across two saves, two empires, a legacy-stamped world, a non-held anchor or the same world twice
    is refused with a named reason.
  - Each resolution of an endpoint world logs exactly one window per live route touching it; replaying either
    world alone reproduces its hash.
  - Clearing a route stops future departures only; goods already in the crossing complete (conservation).
  - SQL only in `FusionRpg.Data` (`guard-dal.py`).
- **Verification boundary:** `FusionRpg.Data.Tests`; `FusionRpg.Core.Tests` (World/Logistics/Rift);
  `FusionRpg.Server.Tests` (endpoints).

### 2. `crossing-anchor`

**Capability.** A world's end of a crossing is a **working own Rift Anchor** — its own structure kind and row,
one tier (round 4: *"Rift Anchor — a cross-world route end; needs a Grand Exchange in the same world"*). The
anchor works only while the player also holds a working **Grand Exchange** (the trade building at tier 4,
`exchange`'s) anywhere in the same world. *(Round 4 overturns the approval-time "no new structure role — a
depot"; C9.)* Its crossing throughput is set by its own **crew** (`fleet` `crew`, a legion on a crew order
naming the anchor's slot) through its own point list `crossing.throughputCurve` and `fleet`'s one
`LabourCurve` evaluator, and the crossing leg's throughput is the smaller of the two anchors' (a bottleneck,
reported as such). An anchor
whose **sector holds** a rift-tear slot gets a crossing bonus — the preferred site, never the only one, the same
shape ideal §7.1 gives the Market slot for trade hubs. *(Corrected at spec time: the draft said "a depot on a
`Tear` slot", but `convoy-depot` requires a `Wildland` slot and `BuildResolver` refuses any other kind —
`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89`.)* The other world reads this end's capacity through a
Data-side **far-end view** that every resolution of this world republishes (full trigger set in the spec).

- **Built:** the `Tear` slot kind (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:15,71`).
- **Wiring gap:** no template places a `Tear` slot; the world generator (`world-map-program.md` wave 4) is where
  placement constraints go.
- **Real gap:** the Rift Anchor kind and row, anchor semantics (incl. the Grand Exchange test), the site
  bonus, the width level, the far-end view. A placed structure has no tier
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:96-126`) — closed by `trade-foundation` `sector-features`
  (`SectorFeature.CrossWorld`, `SectorFeatures.TierOf`).
- **Depends on:** `rift-route`; `fleet` `crew`, `depot` (`LabourCurve`); `exchange` `exchange-hub`;
  `trade-foundation` `sector-features`; `empire-seed` `trade-structure-rows` (A13).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Rift/CrossingAnchor.cs` (new); no `StructureKind` member (C12);
  `data/tuning/trade.v1.json` (new) keys `crossing.throughputCurve`, `crossing.tearSiteBonusMilli`,
  `crossing.widenStep` (the draft key `crossing.throughputPerCrew` is dropped as a second labour rule — found at
  spec time; the spec-time reuse of `fleet`'s `depot.throughputCurve` is withdrawn in round 4).
- **Acceptance (contract):**
  - An anchor that is not a working own Rift Anchor, or whose world holds no working Grand Exchange of its
    owner, carries nothing and reports why (`anchor.no-grand-exchange` for the latter).
  - Crossing throughput = min(source anchor, destination anchor) for every crew pair; raising either side's
    crew never lowers it (monotone).
  - The site bonus is additive to the anchor's own labour figure and applies exactly when the anchor's sector
    holds a rift-tear slot. *(Said "the depot's own figure" until the 2026-09-20 audit — pre-round-4 wording.)*
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Rift).

### 3. `crossing-leg`

**Capability.** The crossing is **priced and bounded like a lane** (world-continuity ideal §6.8): a throughput
per End Turn (from `crossing-anchor`, raised by `lane-verbs`' own `widen` aimed at an anchor — one end at a time,
because each end's width lives in its own world's hash — on the same rising curve, paid in that anchor sector's
construction stocks), a transit time
`crossing.transitTurns` counted on the **save-scoped End Turn counter**, and a deterministic loss
`clamp(crossing.hazardMilli + goods.{id}.transitLossMilli, 0, 1000)` ‰ per crossing that **vanishes**. It calls
`logistics-flow`'s flow and loss functions with crossing tunables — never a second formula. No `ward` (the
crossing has no siege meaning and no hostile presence) and no escort term.

- **Built:** nothing specific — the functions come from `logistics-flow`.
- **Wiring gap:** —
- **Real gap:** the crossing's parameters and its use of the shared functions.
- **Depends on:** `crossing-anchor`; `logistics-flow` `lane-flow`, `lane-loss`, `lane-verbs`; the **contract** of
  `transit-buffer` (arrive at `t + k`, conservation), not its store — goods on a crossing are in no world's hash.
  Routes sharing an anchor split its capacity pro rata by demand (order-independent), not by route id.
- **Touches:** `src/FusionRpg.Core/World/Logistics/Rift/CrossingLeg.cs` (new); `data/tuning/trade.v1.json` (new) keys
  `crossing.transitTurns`, `crossing.hazardMilli`, `crossing.widenCostCurve`.
- **Acceptance (contract):**
  - A test proves the crossing and a lane with the same parameters produce identical flow and loss (one
    implementation).
  - Loss is in [0, goods] for every input (clamp, bounded ratio); nothing lost appears in any balance.
  - Throughput is never exceeded in any End Turn; `widen` on the crossing is refused without stock and spends
    exactly the curve's price.
  - Throughput is flat load units at each end; a parcel is measured with each end's own `loadOf` scale, so it reads
    the same scale as the goods (`sector-yield` `essence-loop-read`, PS-5) — corrected by the 2026-09-20 audit, which
    found a phantom `LaneFlow.ScaledCapacity` and a unit mismatch in the specs.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Rift).

### 4. `crossing-handoff`

**Capability.** How goods leave one world's hash and enter another's without either world reading the
other. In the source world's Logistics phase, goods at the anchor up to throughput **depart**: they leave
that world's located stock (a `stock-deltas` record and a report entry) and become **crossing ledger rows**
keyed `(save, empire, route, departure counter, good)` with an arrival counter — Data-side, deduped on the
durable key (P14). When the destination world next resolves (a full `Step` if active, or the sleeping case
in `sleeping-endpoint`), the server files each due row as a **system-issued arrival command** into that
world's list; its Logistics phase applies the arrival at the arrivals step (before banking, so a delivery
into a bank-point anchor banks the same turn). Because the arrival is a logged command, the destination's
replay reproduces it without the source world.

- **Built:** the command list read inside the commit (`RpgStore.WorldTurns.cs:537-539`); the P14 pattern
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:147,234`).
- **Wiring gap:** —
- **Real gap:** the crossing ledger, the arrival command kind, the departure step.
- **Depends on:** `crossing-leg`; `world-continuity` `hibernation-clock`; `trade-foundation` `stock-deltas`,
  `ledger-keys`; `logistics-flow` `logistics-phase` (the arrivals step).
- **Touches:** `src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs` (new); `WorldCommandKinds` (+ a system-only arrival kind,
  refused from players at admission); `src/FusionRpg.Core/World/Logistics/Rift/CrossingHandoff.cs` (new).
- **Acceptance (contract):**
  - Conservation across worlds, per good: departed = arrived + lost + in crossing + returned, at every counter
    value.
  - Re-committing a turn creates no second ledger row and no second arrival (dedupe on the durable key).
  - A player-filed arrival command is refused at admission (system-issued only).
  - Each world replays byte-identically from its own log with the other world absent.
  - **Order-independent:** two consignments arriving at one anchor over its capacity split it pro rata by
    balance, and creating their routes in either order gives the same result (both tested). *(The draft's
    route-id order would have made the result depend on creation order.)*
- **Verification boundary:** `FusionRpg.Data.Tests`; `FusionRpg.Core.Tests` (World/Logistics/Rift). Crosses Core and
  Data: the full suite once at the module's end (AGENTS.md verification point 2).

### 5. `sleeping-endpoint`

**Capability.** The hibernating and idle rows of the table above. For a **hibernating** endpoint, the route's
exports and imports are extra **inputs** to world-continuity's `CoarseStep(summary, seed, n, stamp, inputs)`:
exports over `n` pending turns are computed in closed form from the anchor's warehouse and background
production, bounded by throughput × `n` and reduced by crossing loss; imports due by the current counter land
in the anchor warehouse, capped by capacity. For an **idle** endpoint, the route's draw is an idle collect
resolved Data-side (wall clock read outside `Step`, as expedition collects are) and passed in as a logged
input, bounded by throughput per active End Turn. Neither ever runs a step the continuity scheduler would not
run.

- **Built:** the lazy idle resolver shape (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-62`;
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:71-93`); `catch_up_cap` column (`RpgStore.World.cs:27`, unread).
- **Wiring gap:** —
- **Real gap:** everything — no coarse step exists yet (`world-continuity` `coarse-step`).
- **Depends on:** `crossing-handoff`; `world-continuity` `coarse-step`, `idle-world`, `background-yield`,
  `hibernation-clock`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/Rift/SleepingEndpoint.cs` (new) — a pure input builder and
  closed-form drain that `CoarseStep` calls; the idle collect path.
- **Acceptance (contract):**
  - An End Turn in the active world performs **zero** `Step` or `CoarseStep` calls on other worlds because a
    route exists (asserted by counting calls, not timing).
  - Split invariance: coarse-stepping `a` then `b` pending turns exports the same total as `a + b` at once
    (matching `coarse-step`'s own order-independent split).
  - Cost is independent of `n` (closed form; asserted structurally).
  - Exports never exceed what the far world produced plus what its anchor held (no route-made goods), and
    per-period exports from a sleeping world are ≤ what the same world would export if active (leaving never
    pays better).
  - An arrival whose counter is already past lands at the next resolution, never in a past turn.
  - Idle draws are idempotent under retry (the idle collect's own rule) and never exceed its credited window.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Rift, World/Turn); `FusionRpg.Data.Tests`.

### 6. `endpoint-loss`

**Capability.** A route whose anchor sector is lost, or whose world's `outcome` becomes `fallen`, **suspends**
the turn it happens: nothing further departs toward or from that anchor. Goods still in the crossing toward a
lost anchor **return** to the origin anchor at their arrival counter (crossing loss already applied — a
return is not a second crossing and re-creates nothing); goods already delivered into the lost anchor's
warehouse follow the sector capture rule (`sector-yield`). A suspended route resumes if the anchor is
retaken, or is cleared by the player. The route's validity is **derived each resolution** from world states
and anchor ownership, never stored as a flag. The near half is computed from the resolving world's own state; the
far half is read from `crossing-anchor`'s far-end view, a projection with an enumerated trigger set (corrected at
spec time: the draft's "never cached" cannot hold for the far half without reading the other world).

- **Built:** —
- **Wiring gap:** no code sets `fallen` or any non-active state (`RpgStore.WorldTurns.cs:683-690` is the only
  update) — `world-continuity` `world-fall`.
- **Real gap:** suspension and return.
- **Depends on:** `crossing-handoff`; `world-continuity` `world-fall`, `world-state-vocabulary`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/Rift/EndpointLoss.cs` (new); the crossing ledger.
- **Acceptance (contract):**
  - Returned goods + goods lost on the crossing = goods that departed toward the lost anchor (conservation).
  - A fallen or captured anchor receives nothing after the turn it was lost; the capture itself moves only
    what was already in its warehouse.
  - **Order-independent:** an anchor lost and a route cleared in the same turn give the same final stocks in
    either order (both tested).
  - Retaking the anchor resumes the route on the next resolution with no retroactive deliveries.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Rift); `FusionRpg.Data.Tests`.

### 7. `crossing-goods`

**Capability.** The closed table of what a crossing carries, with guards: **loam never** (principle 6;
world-continuity ideal §3.6); **recruits never** (an accrual meter); **located goods** (the `sector-yield`
registry class) and **legion equipment** (a located good, ideal §7.3) **yes**; **world stocks** rubble and
ironwork **yes, never auto-banked** (owner decision Q2); **souls and banked materials never** — they are unlocated
and have no place to cross from. Nothing banks on the crossing: goods reach a wallet only through the destination world's
banking step.

- **Built:** the registry classes (`docs/architecture/empire-resource-ssot.md` §2).
- **Wiring gap:** —
- **Real gap:** the table and its guards.
- **Depends on:** `rift-route`; `sector-yield` `located-goods-registry`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/Rift/CrossingGoods.cs` (new).
- **Acceptance (contract):**
  - Membership is a closed vocabulary over registry classes, pinned with the reason "closed vocabulary the
    code owns"; a new registry class is refused by the crossing until the table names it.
  - A property test over random routes finds no path that moves loam or recruits between worlds, and no path
    that credits a wallet or material ledger from the crossing itself.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Rift); `FusionRpg.Guard.Tests` (a source scan for
  loam on any crossing type).

### 8. `rift-facts`

**Capability.** Report entries for departures, arrivals, crossing loss (with its cause) and suspension, written
into each world's own report and fog-scoped by `Audience`, plus the lines world-continuity's `away-digest`
folds into the *"while you were away"* summary when a sleeping endpoint resolves. The kinds extend
`logistics-flow`'s closed vocabulary (`logistics-facts`), so `trade-surface`'s status line reads cross-world
flow the same way it reads lane flow.

- **Built:** the report entry shape (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:31-32`).
- **Wiring gap:** —
- **Real gap:** the kinds.
- **Depends on:** `crossing-handoff`, `endpoint-loss`; `logistics-flow` `logistics-facts`; `world-continuity`
  `away-digest`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs` (new kinds); `src/FusionRpg.Core/World/Logistics/Rift/RiftFacts.cs` (new).
- **Acceptance (contract):** every departure, arrival, loss and suspension produces exactly one entry in the
  world where it happened; Σ reported = Σ ledgered per good and counter; an entry never names a sector of the
  other world to a faction that cannot see it; the kind list is a closed vocabulary (pinned with a reason).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Turn, World/Logistics/Rift).

---

## Tunables (keys owed by the specs; values decided by principle)

`data/tuning/trade.v1.json` (new): `crossing.throughputCurve` (round 4; points for `fleet`'s `LabourCurve`),
`crossing.tearSiteBonusMilli`, `crossing.widenStep`, `crossing.transitTurns`, `crossing.hazardMilli` (bounded
ratio), `crossing.widenCostCurve` (rising, uncapped). The Rift Anchor's build cost, turns and upkeep are
`empire-seed` bands (A13), not trade keys.
The background multiplier, `catch_up_cap` and the idle window are `world-continuity`'s
(`data/tuning/world-continuity.v1.json` (new)).

## Filed asks (other maps)

| # | To | Ask |
|---|---|---|
| A1 | `world-continuity` `coarse-step` | The `inputs` parameter carries route exports and due imports; the closed form includes an anchor warehouse drain bounded by throughput × `n` |
| A2 | `world-continuity` `idle-world` | The idle collect is callable as a route draw bounded by an amount, leaving the remainder credited, and is idempotent under retry |
| A3 | `world-continuity` `away-digest` | Fold `rift-facts` entries into the digest |
| A4 | `trade-foundation` `world-stamp` | A `trade.riftTrade` capability flag |
| A5 | `fleet` `crew`, `depot` | **Rewritten for round 4 (answered in `fleet`):** the anchor is not a depot. It needs crew labour readable **per building slot** (`Crew.LabourAt(world, sector, slot, faction)`, `fleet/spec-crew.md` §3 — so a caravan building's crew in the same sector is never counted for the anchor) and the one labour-to-output evaluator (`LabourCurve.Eval`, `fleet/spec-depot.md` §3) to run its own points. The spec-time "one more demand in `Depot.Share`" is withdrawn |
| A6 | `world-map-program` `world-generator` | A placement constraint: worlds with a rift-tear slot in reach of the home sector, in a sector that also has a `Wildland` slot for the Rift Anchor (`storm` and `warcamp` sector types allow both, `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:79-89`) |
| A7 | **`trade-foundation` `system-commands`** (§2.10; retargeted from `world-continuity` by round-4 Q10 — **answered**) | **Owner named by the owner: one shared system-command path, built in `trade-foundation`.** Its shape: a closed system-kind set, admission refusing those kinds from every commander (`kind.system-only`), one Data filing path inside the commit transaction with deterministic command ids. `rift-trade` registers `rift-window` and `rift-arrive` in it and adds no second path. Built as `trade-foundation/spec-system-commands.md` (the one `FileSystemCommandUnlocked`); `world-continuity`'s spec no longer defines its own |
| A8 | `logistics-flow` `lane-verbs` | `widen` may name an anchor sector (no lane path) to raise that anchor's crossing width, priced on `crossing.widenCostCurve`, resolved beside the lane resolver — one verb, one resolver (added at spec time) |
| A9 | `world-continuity` `advance-carry`, `world-warden` | Any Data-side move of a legion into or out of a world outside a step republishes that world's crossing-anchor view in the same transaction (trigger T5 in `spec-crossing-anchor.md`) (added at spec time) |
| A10 | `trade-foundation` `ledger-keys`, `stock-deltas` | Widen the closed fact-kind vocabulary with `rift-depart` and `rift-arrive` (added at spec time) |
| A11 | `logistics-flow` `logistics-phase` | Two rift steps in the fixed step order: rift arrivals inside the arrivals step (before overflow and banking); rift departures after banking and before the lane-flow pass (added at spec time) |
| A12 | `world-continuity` `continuity-doc-amendment` | Rule 5b in `empire-resource-ssot.md` must read *"world stocks cross between worlds only as cargo or over a cross-world route, and never bank"* — Q2 widens the continuity wording *"only as cargo"* (added at spec time) |
| A13 | `empire-seed` `trade-structure-rows` | **Round 4:** a **Rift Anchor** row — one row, no tier variants — in the one structure corpus, with magnitudes (build cost, turns, upkeep role term) through bands. `spec-trade-structure-rows.md` §5.1 has no row serving the cross-world function; by its own rule (*"a role the trade umbrella needs has at least one row per distinct trade function"*) this is a deficit. Required slot kind **`Wildland`** (round 5 B2, decided; RQ1 closed). Which structure role it takes is `empire-seed`'s (`Move` is the nearest of the ten) |
| A14 | `exchange` `exchange-hub` | **Round 4:** a Grand Exchange read for `crossing-anchor`, and no second cross-world gate in `exchange`. **Answered by `exchange`** (its E-A18, `exchange/spec-exchange-hub.md` §7): `crossing-anchor` reads `Hubs.TradeTier(world, faction) ≥ 4` and adds no second check — adopted |

## Contradictions found

| # | Where | What | Recommended resolution |
|---|---|---|---|
| C1 | trade-network ideal §8.3 (*"Foreign and cross-world routes are run by legions on a trade standing order"*) vs world-continuity ideal §6.8 (*"one extra leg: the crossing between worlds, priced and bounded like a lane"*) | A legion crossing worlds per trip, or a lane-like flow between two anchors | **Resolved by owner decision Q1** (2026-09-19): lane-like flow between crew-staffed depots; nothing physically crosses |
| C2 | trade-network ideal §7.3 (rubble, ironwork: *"World-to-world barter only"*) vs world-continuity ideal §6.2 and `world-continuity-map.md` `advance-carry` (*"World stocks … may cross only as cargo"*) | Whether a crossing may carry world stocks | **Resolved by owner decision Q2** (2026-09-19): they may cross, never auto-banked. The continuity wording is widened through ask A12 |
| C3 | world-continuity ideal §8 (*"cross-world crossing cost and loss"* in `world-continuity.v1.json`) vs `world-continuity-map.md` tunables (*"Cross-world crossing cost is `rift-trade`'s"*) | Two homes for the crossing numbers | Already resolved by the world-continuity map: the keys live in `trade.v{n}.json`; the ideal's §8 line is stale |
| C4 | trade-network ideal principle 7 (rubble, ironwork, recruits *"die with the map"*) vs world-continuity (maps no longer die) | Stale wording | Already listed by `world-continuity-map.md` `continuity-doc-amendment` row 7; no action here |
| C5 | This map's draft (*"a depot on a `Tear` slot gets a crossing bonus"*) vs `gk-data/packs/fusion/data/seed/structures/move/convoy-depot.json` (`requiredSlotKind: Wildland`) and `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89` (wrong slot kind refused) | A depot can never stand on a rift-tear slot | Corrected here and in `spec-crossing-anchor.md`: the bonus applies when the anchor's **sector** holds a rift-tear slot (found at spec time) |
| C6 | This map's draft (*"validity … derived each resolution … never cached"*) vs the rule that no world reads another | The far end's state cannot be derived without reading the other world | Corrected: the far half is a Data projection every resolution of its own world republishes, with a full trigger set and a recompute cross-check (`spec-crossing-anchor.md` Design 4) (found at spec time) |
| C7 | This map's draft (route-id order for routes sharing an anchor; each coarse export back-dated to "the arrival counter it would have had") vs order-independence and the closed form | Route ids follow creation order, so the result depended on it; back-dating costs a row per pending turn | Corrected: pro rata by demand/balance; one consignment per good at the coarse step's counter (found at spec time) |
| C8 | This map's draft (`tasks/rift-trade-*.md`) vs `trade-network-map.md` §6 (`tasks/trade-network-<sub-program>-*.md`) | Two plan-path conventions | Corrected to the umbrella's (found at spec time); `fleet-map.md` has since been corrected too (its C14) |
| C9 | This map's module 2 and `spec-crossing-anchor.md` (*"a working own depot — no new structure role"*; the crossing a pro-rata share of `Depot.Share`) vs round 4 B (*"Rift Anchor — a cross-world route end; needs a Grand Exchange in the same world"*) | The approved anchor was a depot | The anchor is a Rift Anchor with its own crew and point list, gated on a Grand Exchange in its world; `rift-route` admission, `crossing-leg`, `endpoint-loss` reasons and the far-end view follow (round 4) |
| C10 | `spec-crossing-handoff.md` (*"consignment"* = a crossing-ledger row) vs `exchange/spec-exchange-hub.md` §4 (*"Consignment"* = a trader's goods at a foreign hub) | One word, two records in the same family | Rift-trade prose reads *crossing consignment*, code type `CrossingConsignment`; noted at the top of `spec-crossing-handoff.md`. The two never meet |
| C11 | `spec-rift-route.md` and `spec-crossing-handoff.md` (the system-command seam *"`world-continuity` owns"*, ask A7 *"owner to be named"*) vs round-4 Q10 | The seam's owner | `trade-foundation` `system-commands` (§2.10) owns it (A7 retargeted and answered); both specs updated |
| C12 | An earlier draft of this reconciliation (`StructureKind.RiftAnchor`) vs `trade-foundation/spec-sector-features.md` §1–§2 (`StructureDef.Feature`) | Two classifications of one fact | The Rift Anchor is `Feature == cross-world`; no `StructureKind` member |

## Owner decisions (2026-09-19)

- **Q1 — nothing physically crosses between worlds.** Each world's end of a route is a depot staffed by a crew
  legion (since round 4: a crew-staffed **Rift Anchor**, C9), and the crossing is lane-like flow, which keeps each world's state hash and replay self-contained.
- **Q2 — rubble and ironwork may cross, and they are never auto-banked.**

**Opened by round 4 (default until answered):**

| # | Question | Options | Recommendation |
|---|---|---|---|
| RQ1 *(answered 2026-09-20, R5-A B2: option (a))* | **Which slot does a Rift Anchor stand on?** The register names the building but not its site; neither shipped template places a rift-tear slot, and the tear is also a delve entrance hint (`docs/architecture/party-dungeon/spec-domain-catalog.md:67`). | (a) **`Wildland`**, with the existing bonus when the anchor's sector holds a rift-tear slot. (b) **Requires a `Tear` slot** — thematic, but no cross-world route is possible on any shipped template until the templates or the world generator place tears (ask A6). (c) Either slot, via two rows | **(a).** It keeps the approved tear-as-preferred-site shape (the Market-slot precedent, ideal §7.1), leaves the tear for delve entrances, and needs no template edit before cross-world trade is playable; the Grand Exchange requirement already makes the anchor a late-game building. (c) is two rows for one building, which round 4 forbids |

The questions as they were put, with the recommendations the owner accepted:

| # | Question | Recommendation (accepted) |
|---|---|---|
| Q1 | **Does anything physically cross between worlds on a route?** The ideal says cross-world routes are run by legions (§8.3); the continuity ideal says the crossing is a lane-like leg (§6.8). A legion that crosses every trip needs world-continuity's advance transaction (departure and genesis commands, `advance-carry`) per trip and would live in no world's hash while crossing. | **No entity crosses.** Each world's end is a crew-staffed depot (legions on crew orders, `fleet`), and the crossing is lane-like flow between the two anchors. This satisfies both texts — legions run the route (as crews, and as caravans inside each world where lane flow cannot reach the anchor) and the crossing is priced and bounded like a lane — keeps each world's hash and replay self-contained (world-continuity assumption 4), and keeps advance the only way a legion changes worlds. Default if unanswered: this |
| Q2 | **May a crossing carry rubble and ironwork?** §7.3 allows them *"world-to-world"*; world-continuity allows world stocks across worlds *"only as cargo"*. | **Yes, as carried goods of a crewed crossing** — the crossing is the route's carrier just as cargo is a legion's, so the continuity rule's intent (never auto-bank, never copied, move not copy) holds; they land as world stock in the destination sector and never bank. If the owner reads "cargo" strictly, the table in `crossing-goods` drops them with one row. Default if unanswered: allow |

Everything else is decided by a rule already stated: routes between two sleeping worlds are allowed (else a
world switch would suspend them); the `Tear` slot is a preferred site, not a requirement (the Market-slot
precedent, ideal §7.1, and no shipped template has one); a crossing has no `ward` (no siege meaning, no
hostile presence); returns re-create nothing.

---

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store and world states (world-continuity), world turn engine (Logistics
    phase, CoarseStep inputs), economy (located goods, crossing ledger), tunables, numeric range,
    performance (never step N worlds), data/SQL (crossing ledger, route rows).
[~] Session boundary: runs under tasks/sessions/trade-network-idea-20260919.json (paths include
    docs/architecture/trade-network/**); I did not run session-boundary-check.py myself.
[x] Read this session: the §1 rows listed in logistics-flow-map.md's checklist, plus
    world-continuity-ideal.md in full and world-continuity-map.md (assumptions, principles,
    modules 1, 2, 6, 9, 10, 11), and the Data / SQL row (data-architecture.md §3 SSOT map and §6
    DAL boundary; contributing/architecture-map.md) — the route rows and crossing ledger live in
    FusionRpg.Data only; the Server files commands and holds no SQL.
[x] decisions.md checked: World store — delve worlds (several worlds per save, kind column), World
    turn phase order, Empire resource registry (loam never converted or moved across worlds).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: see the session report; no HIGH finding left.
[x] Verified against code: no Tear slot in shipped templates; the only rpg_worlds UPDATE is the turn
    advance; the command list is read inside the commit.
[x] Read surrounding sections: world-continuity §3, §6.1-§6.8; its map's assumptions 1-4 and the
    coarse-step, idle-world and advance-carry sections.
[~] Constraints tested: none claimed; "each world replays alone" is an acceptance criterion.
[x] No §2 invariant contradicted: determinism per world, one turn engine, no fourth clock (the crossing
    counts the save End Turn counter world-continuity adds), no ceilings (widen is uncapped).
[x] Corrections propagated: none edited outside this file; C1-C4 name their owners.
[x] No population count pinned: the crossing-goods table and report kinds are closed vocabularies with
    reasons; no count of routes, goods or entries is asserted.
[x] Event-refreshed cache: one — the far-end view (`crossing-anchor` §5), with its full trigger set T1-T7,
    the key-set edges T4 (grow) and T7 (shrink), one test each and a recompute cross-check. *(This line said
    "none" until the 2026-09-20 audit; C6 had already introduced the projection.)* Route validity itself is
    derived each resolution.
[x] Orderings: two routes into one anchor, anchor loss vs route clear, coarse split a+b — all
    order-independent and tested both ways.
[x] Actor magnitudes: none produced or consumed.
[x] No SOLID-violating parallel path: the crossing calls logistics-flow's functions; anchors are Rift
    Anchors using fleet's one crew read and one labour evaluator (round 4; this line said "fleet depots"
    until the 2026-09-20 audit); banking stays sector-yield's; cross-world effects use trade-foundation's
    one system-command path (round-4 Q10).
[ ] Registry rows: the loam-never-crosses scan and the system-only arrival command need
    enforcement-registry rows when their guards land — each module spec names its row
    (spec-crossing-goods, spec-crossing-handoff, spec-rift-route); none is written yet.
[x] Spec pass 2026-09-19: all eight specs written; corrections C5-C8 and asks A7-A12 recorded
    above; audit-doc-citations.py --scope on this map and on rift-trade/ reports 0 HIGH (the LOW
    D1 findings are proposed new files, each marked "new").
```

---

## Reconciliation 2026-09-19 (round 4)

Against [decisions-round-4.md](decisions-round-4.md) (binding; it wins where this map disagreed). Docs only.

**Round-4 decisions applied**

| Register item | Where it landed |
|---|---|
| B — *Rift Anchor: a cross-world route end; needs a Grand Exchange in the same world* | `crossing-anchor` rewritten: the `cross-world` feature (`trade-foundation` `sector-features`), one tier; `IsWorking` also requires the owner's working Grand Exchange (trade tier 4) in that world; own crew (slot-keyed) and own `crossing.throughputCurve` through `fleet`'s `LabourCurve` (C9); slot kind `Wildland` + tear bonus (round 5 B2) |
| B — *Trade T4 (Grand Exchange): cross-world routes* | the Grand Exchange is read, never re-gated, through `exchange`'s `Hubs.TradeTier(world, faction) ≥ 4` (A14 / E-A18) |
| Q10 — system-issued world commands: one shared path, built in `trade-foundation` | ask A7 retargeted; `spec-rift-route.md` and `spec-crossing-handoff.md` register `rift-window` and `rift-arrive` in that path (C11) |
| Q1 (map) unchanged — nothing crosses; each end is crew-staffed | now "a crew-staffed Rift Anchor" instead of "a crewed depot" |

**Contradictions fixed in this cluster:** C9 (anchor was a depot), C10 (*consignment* named two records in the
family), C11 (seam owner), C12 (no `StructureKind` member for the anchor); `rift-route` admission reason `rift.anchor-not-depot` →
`rift.anchor-not-working:<reason>`; `endpoint-loss` reason set gains `anchor.no-anchor`,
`anchor.anchor-building`, `anchor.no-grand-exchange` (replacing `anchor.no-depot`, `anchor.depot-building`);
`crossing-leg`'s labour reference moved from `Depot.Allowance` to the anchor's own curve; the far-end view
gains `anchor_slot` and `grand_exchange` inputs, whose changes fall inside the existing triggers T1/T2.

**Asks received and answered here:** `exchange` E-A18 (read `Hubs.TradeTier ≥ 4`, no second check) —
adopted in `spec-crossing-anchor.md` §2. No other map aims an ask at `rift-trade` (searched every
trade-network, world-continuity, legion-build and empire-seed map). `logistics-flow/spec-lane-verbs.md`
already names `crossing.widenCostCurve` as `crossing-leg`'s — consistent.

**Cross-cluster conflicts (files this session does not own)**

| # | Conflict | Recommended resolution |
|---|---|---|
| X-R1 | *(Resolved during this round.)* `world-continuity/spec-world-state-vocabulary.md` §5 once defined its own `FileSystemCommandUnlocked`; `trade-foundation` `system-commands` (§2.10) now owns the one function and `world-continuity`'s spec says it no longer defines one | None; `rift-trade` registers `rift-window` and `rift-arrive` there. `system-commands` must land before `crossing-handoff` (`trade-foundation-map.md` build order) |
| X-R2 | No `empire-seed` row serves the cross-world function (`spec-trade-structure-rows.md` §5.1) | Add a Rift Anchor row, no tiers (A13) |
| X-R3 | `exchange/spec-exchange-hub.md` §1 still widens `StructureKind` with `Exchange`, beside `trade-foundation` `sector-features`' `trade` feature | `exchange` computes `HubTier`/`TradeTier` over `SectorFeatures.TierOf(sector, trade)` so there is one tier read under both (as `fleet-map.md` X-F1). *(Ruled 2026-09-20, X1.)* |

**Gap check**

- Every module row has a spec (8 of 8).
- Dependencies resolve to real module ids (`world-continuity`, `logistics-flow`, `fleet`, `sector-yield`,
  `trade-foundation` incl. its new `system-commands` and `sector-features`, `exchange`, `empire-seed`).
  `world-map-program`
  `world-generator` is a program wave, not a map module (A6).
- Tuning keys: `crossing.throughputCurve` (new), `crossing.tearSiteBonusMilli`, `crossing.widenStep`,
  `crossing.transitTurns`, `crossing.hazardMilli`, `crossing.widenCostCurve` — each claimed once; the
  spec-time reuse of `depot.throughputCurve` is withdrawn, so no key is shared with `fleet`.
- Closed-vocabulary widenings: no `StructureKind` member (C12; `cross-world` is `sector-features`'); system
  kinds `rift-window`, `rift-arrive` (in
  `trade-foundation`'s set); `factKind` + `rift-depart`, `rift-arrive` (A10); the anchor reason set above;
  `rift-facts` report kinds; the `crossing-goods` table.

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/rift-trade`
— see the session report; no HIGH finding.

## Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A, R5-X), which wins over any spec.
Citations touched were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| RR1 | **B2 (RQ1 → a):** the Rift Anchor stands on `Wildland`, with the capacity bonus when its sector also has a rift-tear slot; both tear-capable sector types allow `Wildland` (`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:79-89`) | `spec-crossing-anchor.md` §1; ask A13 |
| RR2 | **X1:** the anchor gate reads `SectorFeatures.TierOf(sector, cross-world)`; the Grand Exchange gate reads the `trade` faction tier (`FactionTier`), which `exchange`'s `Hubs.TradeTier` wraps and delegates to | `spec-crossing-anchor.md` §2 |
| RR3 | **X3:** an AI treasury is `counterparties` `empire-treasury`'s (owner and writer); routes never carry it | `spec-crossing-goods.md` table |
| RR4 | **X11:** `rift-window` and `rift-arrive` are two of the three system-only kinds (with `release-warden`); unchanged here, now a closed set in `trade-foundation` `system-commands` | `spec-rift-route.md`, `spec-crossing-handoff.md` (unchanged) |
| RR5 | **X5:** rift arrivals (L1) and rift departures (L4r) sit in `logistics-flow`'s canonical step order; the handoff spec already quotes it | `spec-crossing-handoff.md` (unchanged) |

**Still other owners' files:** `empire-seed` already authors `Wildland` on the `rift-anchor` row (`../empire-seed/spec-trade-structure-rows.md`, B2 consistent); `exchange`'s
`Hubs.TradeTier` delegates to `FactionTier` (X1).

## Audit 2026-09-20

An independent audit of this map and its eight specs against the checklist stated in
[fleet-map.md](fleet-map.md) *Audit 2026-09-20* (RPG layer and one mechanism; numbers and the power ladder;
determinism and per-world replay; economy; tests and caches; boundaries and registry rows; vocabulary; spec
quality), each claim checked in code on `features/mega-merge`. Docs only.

### Findings

| # | Sev | Where | Finding | State |
|---|---|---|---|---|
| RA1 | HIGH | `crossing-anchor` §3; `crossing-leg` §1, acceptance 1/3, Dependencies | The capacity formula called `LaneFlow.ScaledCapacity`, a function `lane-flow` does not define (its capacity is flat load units, `Width × throughputPerWidth ÷ 1000`, with the scale inside `loadOf` — `logistics-flow/spec-lane-flow.md` §Design 1–2). It also added a scaled term to flat load units, and `crossing-leg` compared two worlds' capacities as if one scale served both | **Fixed:** every capacity term is flat load units; each parcel is measured with each end's own `loadOf` scale (the far scale from the logged view row) |
| RA2 | MED | `crossing-handoff` §4; `sleeping-endpoint` §1-§2 | Arrival capacity was split "pro rata by balance" — raw quantities of different goods against a capacity in load units | Fixed (split by load at the arrival anchor's scale) |
| RA3 | MED | `crossing-anchor` §5 | The far-end view's trigger table had the key-set **grow** edge (T4) but not the **shrink** edge (a route cleared, an anchor gone) — DESIGN-GATE §2.16 | Fixed (T7, with its test) |
| RA4 | MED | this map's §5 checklist | "Event-refreshed cache: none" contradicted C6's projection; "anchors are fleet depots" contradicted round 4 | Fixed |
| RA5 | MED | `crossing-goods` | An advancing legion's `fleet` carried goods are a second, lossless path between worlds the table does not govern (P5) | Named here; decided by `fleet` owner question **FQ3** (ask A15 on `world-continuity`) |
| RA6 | LOW | `crossing-handoff` §1 | The canonical L3-before-L4r order means an anchor in a bank-point sector exports only what banking leaves; unstated | Fixed (stated); **reported** RX2 |
| RA7 | LOW | `rift-route` §1 | The route table had no primary key | Fixed |
| RA8 | LOW | module 2 acceptance, ask A6, owner decision Q1 | Pre-round-4 "depot" wording | Fixed |
| RA9 | LOW | every spec | Verification boundary: `World/Logistics/Rift/**` maps only to `core-fallback` | Named: a `core-world-logistics-rift` owner boundary lands with the first implementing task |
| RA10 | LOW | every spec's §5 checklist | Registry rows owed with no id | Ids named (`rift-window-system-only`, `rift-anchor-view-trigger-set`, `rift-one-loss-formula`, `rift-arrive-system-only`, `rift-no-post-step-stock-change`, `rift-no-extra-world-step`, `rift-loam-never-crosses`); they land with their tests |

**Checked and clean:** no entity crosses worlds on a route (Q1); each world replays from its own log with the
other absent (every cross-world effect is a logged input — window, arrival command, coarse or idle record); no
route causes a `Step` or `CoarseStep` (probe-counted); loam and recruits never cross, nothing banks on the
crossing, and souls never come out of it; crossing loss is the named sink (P1, P5 lossy); width is uncapped with
a rising price; loss is a bounded ratio clamped by `lane-loss`; all splits are pro rata and order-independent;
SQL only in `FusionRpg.Data`; no actor magnitude; no IP name in new prose.

### Reported to other programs (their files; not edited)

| # | To | Finding | Recommended fix |
|---|---|---|---|
| RX1 | `trade-foundation` `sector-features` | A Rift Anchor's (or Grand Exchange's) **slot** can be held by an enemy after an assault while the sector is not (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`); `TierOf`/`FactionTier` read no slot owner | One owner rule in `sector-features` (fleet-map FX1) |
| RX2 | `sector-yield` `banking-fact` | The round-5 A4 hold keeps stock for other traders' open buy orders at a hub; nothing keeps stock for an open cross-world route from an anchor in a bank-point sector, and banking (L3) runs before rift departures (L4r) | Extend the hold with "the route shares departing from this sector this turn" (one hold rule), or document that anchors and Counting Houses should not share a sector |
| RX3 | `sector-yield` `located-goods-registry` | The located-goods registry row must list **crossing loss** as a sink when `crossing-handoff` ships (P1) | Add it in that change |
| RX4 | `world-continuity` `advance-carry` | RA5 | `fleet` FQ3 / ask A15 |

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/rift-trade`
and `--scope docs/architecture/trade-network/rift-trade-map.md`, run after these edits — no HIGH finding.

---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6". The family's single landing order is
[landing-order.md](landing-order.md); this sub-program is rows 20, 21 and 22 of its §2, after `exchange`
(the Grand Exchange read) as the umbrella's build order already requires.

| # | Decision | What changed |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | One `trade.riftTrade` covered all three waves (assumption 4 of this map; `spec-crossing-handoff.md` §6). Now: **W1** `trade.riftTrade` (`rift-route` registers it; `crossing-goods`, `crossing-anchor` share the bump) — routes and anchors exist; **W2** `trade.riftCrossing` (`crossing-leg`, `crossing-handoff`) — goods actually move; **W3** `trade.riftEndpoints` (`sleeping-endpoint`, `endpoint-loss`, `rift-facts`) — sleeping and lost endpoints resolve. One bump per wave, and a world stamped at W1 never starts moving goods mid-life when W2 merges. `spec-rift-route.md` and `spec-crossing-handoff.md` state their wave; the three W3 specs name no flag today and take W3's |
| **C2** | One neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | `spec-crossing-anchor.md` §1: *"no `StructureKind` member"* was read as `structureKind: none`, and a row with no kind **cannot load** (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`, `:330`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`), so no Rift Anchor could ever be placed and §2 would answer `anchor.no-anchor` forever (audit C2). The row loads as the neutral `Feature` kind — the `Obstacle` precedent (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`) — and the predicate still reads the feature, never the kind. The heading changed with it. This also matters for the Grand Exchange read: `exchange`'s own row retires `StructureKind.Exchange` for `Feature` |
| **C3** | Banking waits on the save-identity re-key | No rift module banks — *"nothing ever banks on the crossing"* is a locked anchor. `crossing-goods`' located-good row already says a good banks only *"by the destination world's own banking step"*, which is `sector-yield` `banking-fact`'s step half (row 8). Until that lands, a crossed good sits in the destination anchor's warehouse; nothing here changes |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | `spec-crossing-anchor.md` §2 reads `SectorFeatures.TierFor(sector, owner, CrossWorld)` instead of `TierOf`, and its Dependencies row names `TierFor`/`FactionTier`. An anchor on a slot a previous owner still holds leaves the crossing closed (`anchor.no-anchor`) rather than working for whoever holds the ground. The rule lives once, in `sector-features` §5a; the Grand Exchange test keeps delegating to `FactionTier`, which now carries S1 too |
| **S2 / W1 / W2** | Trade goods cross worlds only by rift route; an advance is weight-limited; `world-transit` is a named future program | `spec-crossing-goods.md` Locked anchors: this table is **the** trade channel between worlds, not one of two. The advance channel is closed by the weight limit — Σ(unit count × unit carry capacity) from `world.carry.capacity`, units and goods on one limit, excess refused at `depart` admission (`fleet/spec-carried-goods.md` §5) — and import/export through the gate is `world-transit`'s. No rule here anticipates that program |
| **CQ2** | Legion equipment and doctrine upkeep may draw banked goods | No change: a crossing carries equipment pieces (Q2 table) and never spends them |
| **D2** | Six `world.*` channels compose in `ActorHub`, read as Hub output | The anchor's end capacity is **crew labour through `LabourCurve`**, and staffing is deliberately **not** one of the six channels (X9 leaves the staffing term to each consumer; `fleet/spec-crew.md` keeps `LabourAt` a bearer count). So `crossing-anchor` reads no world channel and states no default. Where a legion's own carry matters — what a crossing's cargo weighs on the far side — the channel is `world.carry.capacity` and the reader is `fleet` `carried-goods` |
| **M1 (audit), edges 1 and 6** | Two edges pointed up or cycled | `spec-crossing-anchor.md` §2: `IsWorking` is **registered** into `fleet` `crew`'s `IWorkingSite` registry in this program's own change, so `crew` (row 13) no longer depends on this module (row 20) and the cycle with `spec-crew.md` is gone. Its Dependencies row for `world-continuity` `advance-carry` becomes a **registration into `advance-carry`'s post-move hook** rather than a publish call this module is owed — which, with round 6 S2 removing the goods half of an advance, closes that cycle too |

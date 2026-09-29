# Capability map: `trade-network` (umbrella)

**Status:** APPROVED 2026-09-19 (umbrella and all ten sub-program maps, with the sibling maps
[world-continuity-map.md](world-continuity-map.md), [legion-build-map.md](legion-build-map.md) and
[empire-seed-map.md](empire-seed-map.md)). Module specs may now be written against the owning
sub-program map; the cross-map decisions in §1a bind every one of them.
**Owner decisions after approval:** [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md)
(round 4, 2026-09-19; round 5, 2026-09-20) — binding over every map and spec in the family; see §10.
**Ideal:** [trade-network-ideal.md](trade-network-ideal.md) (owner decisions D1–D5, §14 D-A to D-E2,
§14b round 3 — all closed 2026-09-19).
**Sibling ideals:** [world-continuity-ideal.md](world-continuity-ideal.md),
[legion-build-ideal.md](legion-build-ideal.md), [empire-seed-ideal.md](empire-seed-ideal.md),
[npc-story-events-ideal.md](npc-story-events-ideal.md).

> **The program in one sentence.** Held sectors produce goods into a pooled warehouse; the goods flow
> home along lanes every End Turn and bank as a ledger fact; beyond your borders, clans and other
> empires trade those goods at priced hubs under treaties. All of it runs as one phase of the one
> world turn engine, and nothing is simulated per unit.

This file is the **index** for the umbrella. It owns no modules of its own. Each sub-program has its
own map, and the map, not a filename, says which spec is active.

---

## 1. Sub-programs

| # | Sub-program id | Scope (one line) | Depends on | Map |
|---|---|---|---|---|
| 1 | `trade-foundation` | `TurnEngine.Step` benchmark, synthetic giant-tier graphs, per-world stamp and its migration, P14 ledgers for materials and world stocks, the world economy report as a test, the no-`ReconnectionCost`-in-routing guard | — (external: `save-identity` SE4.12 / SE4.38 for ledger keys) | [trade-network/trade-foundation-map.md](trade-network/trade-foundation-map.md) |
| 2 | `sector-yield` | The reward layer, Shape B: located goods, yield structures, the warehouse capacity axis, production halt at capacity, bank points and the banking fact, income parity, the `LoamUpkeep` structure term, registry rows, the essence PS-5 read, legion equipment stock as a located good | 1; `empire-seed` (band reader, structure bands) | [trade-network/sector-yield-map.md](trade-network/sector-yield-map.md) |
| 3 | `logistics-flow` | The `Logistics` phase: cached paths, `Width` as throughput, the `ward` and `widen` verbs, lane loss, in-transit buffers, auto-banking default, delivery overflow, the construction chain, and the canonical step order inside the phase | 2 | [trade-network/logistics-flow-map.md](trade-network/logistics-flow-map.md) |
| 4 | `fleet` | Depots, crews, trade standing orders on legions (caravans), escort, refine wiring | 3; `legion-build` (standing orders); `scoped-inventory` (`cargo-fate`) | [trade-network/fleet-map.md](trade-network/fleet-map.md) |
| 5 | `counterparties` | Clan seeding and production, clan policy, the relation ladder consumed, conquest consequences, transit rights, AI-empire goods economy and sinks, the real `INeedVector`, diplomacy and treaties | 2; `npc-story-events` (relation ledger); `world-generator` for scale | [trade-network/counterparties-map.md](trade-network/counterparties-map.md) |
| 6 | `exchange` | Trade center structure (`exchange` role), price curve, order lifecycle, fees and tariffs, the shared goods valuation (also for the delve merchant and the item program), Conversions rows | 3, 5 | `trade-network/exchange-map.md` (written by its own session) |
| 7 | `trade-ai` | AI-empire logistics, bidding, treaty decisions, interdiction aimed at the busiest flows, clan behaviour | 5, 6 | `trade-network/trade-ai-map.md` (written by its own session) |
| 8 | `trade-surface` | Trade panel, policy editor, flow lens, turn-report and notification entries, the one-sentence status line, the throttle forecast, the unlock and teaching ladder, a click-budget acceptance criterion | starts after 3; grows with 4–7 | `trade-network/trade-surface-map.md` (written by its own session) |
| 9 | `trade-stories` | Trade facts and hosts for the storylet engine (shortages, raids, requests, lost caravans), seasonal demand shocks, escort and ransom quests, failure branches — rows emitted by the `narrative` adapter, never a second generator | 4–7; `npc-story-events` | `trade-network/trade-stories-map.md` (written by its own session) |
| 10 | `legion-build` | What a legion is built from: stack `Count`, roles, layer 5c (standard, traditions, doctrine, cohesion), standing orders and `escort`, recruitment choice, legion equipment scope — every number through `ActorHub` | 1; `empire-seed` for its catalog; **`sector-yield`** for located equipment stock (corrected 2026-09-20, audit M1) | [legion-build-map.md](legion-build-map.md) (separate map, written by its own session) |
| 11 | `rift-trade` | Trade routes between two worlds the player holds, with a priced, bounded crossing leg | 3, 4; `world-continuity` world states | [trade-network/rift-trade-map.md](trade-network/rift-trade-map.md) |

**Ownership of the income-parity rule** (ideal §8.6 — income with a location, such as a delve door or
a battle sector, lands in that sector's warehouse and travels like any yield) was not assigned by the
ideal's §11 table. **It is `sector-yield`'s** (`income-parity`, owner decision round 4 Q11; restated by
round 5 X6): the rule is a credit into a warehouse, which `sector-yield` owns, and needs nothing from
`logistics-flow` to hold. The first draft of this map placed it in `logistics-flow`; that is withdrawn.

**The `Logistics` phase slot** (ideal §8.7: after `Production`, before `Growth`) is created by
`sector-yield`'s `banking-fact` module, with banking at bank points as its only step, because goods
already sitting at a bank point must bank before any flow exists. `logistics-flow` adds its steps around
banking in the same phase. **The step order inside the phase is `logistics-flow`'s and is canonical
(round 5 X5)** — [logistics-flow/spec-logistics-phase.md](trade-network/logistics-flow/spec-logistics-phase.md)
§1: L0 refresh, L1 arrivals (with rift arrivals), L2 fleet load/unload, **L3 banking**, L4 delivery
overflow, L4r rift departures, L5 flow, L6 loss, L7 refine, L8 facts; then `exchange` settlement and
`counterparties` clan economy after it. Every other spec quotes that table and never restates its own
order. One phase, two contributing sub-programs, in dependency order.

## 1a. Cross-map decisions (2026-09-19)

Approved by the owner with the maps. Each settles a question two or more maps answered differently;
the owning module is the only one that builds it, and every other map consumes it.

| # | Decision | Owner | Source |
|---|---|---|---|
| CM1 | The relation band enters `TurnEngine.Step` as a **logged per-turn input** (a band snapshot), never a live read of the relation ledger | `counterparties` `relation-facts` | [counterparties-map.md](trade-network/counterparties-map.md) module 7; [exchange-map.md](trade-network/exchange-map.md) |
| CM2 | `counterparties` `relation-facts` owns the commit-time **fact projection** into the story ledger; `trade-stories` `trade-fact-source` registers its story kinds into that seam, never a second writer | `counterparties` | counterparties-map C5 |
| CM3 | `counterparties` owns **and writes** the **AI-empire treasury** (`empire-treasury` holds the field and registers itself into `sector-yield` `banking-fact`'s destination seam, its hand-off point — round 5 X3); `banking-fact` hands it the banking fact and writes no treasury field; `logistics-flow` never touches a treasury | `counterparties` | logistics-flow-map C7; counterparties-map module 4; round 5 X3 |
| CM4 | `sector-yield` `banking-fact` **creates the `Logistics` phase** (banking at bank points as its only step); `logistics-flow` extends the same phase with its steps in its canonical order (banking is L3 — round 5 X5) | `sector-yield`, then `logistics-flow` | §1 above |
| CM5 | **Standing orders carry a kind** — one kind-keyed standing order with a per-kind resolver; the emitter and the one command pipe stay `legion-build`'s, and `fleet`'s trade route is one kind | `legion-build` | fleet-map C6 / ask A1 |
| CM6 | `narrative-seed` owns the **storylet host kinds**; trade and continuity hosts register rows there, never a local host enum | `narrative-seed` | [trade-stories-map.md](trade-network/trade-stories-map.md) modules 3 and 10 |
| CM7 | A **per-empire event budget** in storylet selection is requested from `npc-story-events` (an ask on its map, not built here) | `npc-story-events` (requested) | trade-stories-map asks (`trade-story-pacing`); world-continuity-map `world-event-budget` |
| CM8 | `legion-build` owns the **`WorldEntityKind.Caravan` retirement** (`caravan-kind-retire`); `fleet` consumes it | `legion-build` | legion-build-map X15; fleet-map C1 |
| CM9 | Old ruleset code retires only when **no world in any state** (active, hibernating, idle, fallen) carries its stamp — not "no active world" | `trade-foundation` | world-continuity-map contradiction 6 |
| CM10 | Each world's **difficulty-profile id lives on `trade-foundation`'s per-world stamp**; `world-continuity` owns the profile catalog, not its storage | `trade-foundation` (storage) | world-continuity-map module 14 |

## 2. Dependency graph

```text
                     save-identity (SE4.12, SE4.38)          empire-seed I1-I3
                              |                                    |
                              v                                    |
 legion-build <---------- trade-foundation                         |
      |                       |                                    |
      |                       v                                    |
      |                  sector-yield <----------------------------+
      |                       |
      |                       v
      |                 logistics-flow ------------------+----------------+
      |                       |                          |                |
      +----------> fleet <----+                          v                |
                     |        |                   counterparties <-- npc-story-events
                     |        v                          |
                     |      (trade-surface trails from here, grows with 4-7)
                     |                                   |
                     |                                   v
                     |                               exchange
                     |                                   |
                     |                                   v
                     |                               trade-ai
                     v
               rift-trade <-- world-continuity (world states)

        trade-stories <-- fleet, counterparties, exchange, trade-ai, npc-story-events
```

`counterparties` depends on `sector-yield` (clan production uses the same rules), not on
`logistics-flow`; it is drawn under `logistics-flow` only to keep the picture legible.

**Corrected 2026-09-20 (audit M1).** *"Arrows never point back up"* was false in eight places. It is now a
**rule the design holds to, not an observation**: where a module needed something from a later sub-program,
the edge is inverted through a **registration seam owned by the earlier module** — `crew`'s `IWorkingSite`
predicate registry, `stock-deltas` kinds that `settlement-payment` registers, `diplomatic-stance`'s passage
seam, `advance-carry`'s post-move hook. The eight edges, their resolutions and the order that makes each
work are in [trade-network/landing-order.md](trade-network/landing-order.md) §3. One edge was **real, not
invertible**: `legion-build` `legion-equipment` and `legion-standards` depend on `sector-yield`, so §1 row 10
reads `1; empire-seed; sector-yield` and any argument that relied on the old row ("legion-build depends on
trade-foundation and not on sector-yield") is withdrawn.

## 3. Build order

1. **`trade-foundation`** first. Its model-free modules (benchmark, synthetic graph, guard, stamp)
   need no other program. Its two ledger modules are sequenced behind `save-identity` (§5).
   **`legion-build`** starts its own map in parallel and must land standing orders before `fleet`
   needs them. **`empire-seed`**'s model-free infrastructure (I1–I5) runs in parallel; its
   `band-reader` and `structure-bands` must land before `sector-yield`'s yield module.
2. **`sector-yield`** — the reward layer. Nothing downstream has goods to move until it lands.
3. **`logistics-flow`**. `trade-surface` starts here.
4. **`fleet` ∥ `counterparties`**.
5. **`exchange`**, then **`trade-ai`**.
6. **`rift-trade`** after `logistics-flow`, `fleet` and `world-continuity`'s world states.
7. **`trade-stories`** last.

## 4. Sibling programs and the boundary each owns

| Program | Owns | This umbrella's relation |
|---|---|---|
| `world-continuity` ([ideal](world-continuity-ideal.md)) | World states (`active`, `developing`, `hibernating`, `idle`, `fallen`), the selected-world pointer, `CoarseStep`, advancing and carry, wardens, the difficulty profile catalog | Consumes `trade-foundation`'s per-world stamp (it records the difficulty profile id beside the ruleset). `rift-trade` consumes its world states. Background yields land in warehouses and are never banked without collection (its §6.6) — the located-goods rule `sector-yield` defines |
| `empire-seed` ([ideal](empire-seed-ideal.md)) | Every world and empire content family, the structure corpus included (D-E2); the shared seed-plus-bands reader; the `exchange` role widening (D-E1) — the closed role list has **10** roles today (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41`), `exchange` makes **11**, and `gk-data/packs/fusion/data/seed/structures/wonder/` is a folder, not a role (X7); legion content seeds; trade storylet rows through the `narrative` adapter | Supplies structure rows and their resolved magnitudes. `sector-yield` and `exchange` never type a building number; they read resolved bands |
| `npc-story-events` ([ideal](npc-story-events-ideal.md), [map](npc-story-events-map.md)) | The one storylet engine, the story ledger, the four-band relation ledger, named characters (traders, clan elders) | `counterparties` reads the relation ladder; `trade-stories` supplies facts and hosts. Trade never adds a second relation axis or a second storylet generator |
| `base-defense` ([ideal](base-defense-ideal.md)) | The structure anchor schema, the siege loop, decision 22 (production halts at capacity), decision 18 (world stocks die with the map — amended by world-continuity) | Decision 22 is the rule `sector-yield`'s `production-halt` wires. The corpus boundary moved to `empire-seed` (D-E2) |
| `scoped-inventory` ([map](scoped-inventory-hierarchy-map.md)) | Legion cargo, sector item storage (`ItemStorage` axis), `cargo-transfer`, `cargo-fate` | `fleet` uses legion cargo; goods on a legion that loses a battle follow `cargo-fate`. The warehouse axis is deliberately a third axis beside loam `Storage` and `ItemStorage` |
| Item program ([item-map.md](item-map.md)) | Item instances, item price derivation, the materials catalog, the `rpg_creature_materials → rpg_materials` rename (ruled, not scheduled) | Consumes `exchange`'s shared goods valuation. The catalyst lock (`gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs:46-48`) is amended by `exchange` in the change that makes catalysts tradeable (ideal §7.3) |
| `solid-enforcement` `save-identity` ([spec](solid-enforcement/spec-save-identity.md)) | `SaveId`, `EmpireRef`, `rpg_save_empires`, Tier A/B keying, the migration | Every new trade table is born Tier A `(save_id, empire_id, …)` (its "rule for a table created after this module"). The materials ledger waits for the Tier B typing of the materials store |
| `world-map` / `world-stage` | The world generator (wave 4), the command pipeline, `WorldCommandAdmission`, `BuildResolver` | Trade placement constraints (a buildable site for a trade center in every sector; a guaranteed first throttle) go into the generator's constraint table. The building upgrade verb is `build` on the building's own slot (`sector-features` §4, round 5 X8); `world-map` is asked to confirm it in `BuildResolver` |

## 5. Cross-cutting invariants every sub-program inherits

Restated here in full because a sub-program map reads this file, not its links.

1. **RPG layer only.** Trade and logistics are world-stage mechanics. They never touch PvZ, the
   injector or the lawn.
2. **Loam is never traded or converted — only moved** (`decisions.md` *Empire resource registry*;
   `empire-resource-ssot.md` §4 rule 4). No trade path, conversion, tariff, fee or banking fact takes
   or pays loam. A route never carries loam to a counterparty.
3. **No souls out of trade.** Trade may spend souls; it never pays them. Any souls part of a tariff is
   sunk in full. Invariant, tested: *no trade path increases souls; buying then selling the same
   quantity at the same hub always loses value; any closed trade cycle across any number of hubs in
   one turn loses value.*
4. **Every faucet names its sink in the same change (P1); territorial income needs territorial upkeep
   (P2); conversions are lossy, rate-capped or gated (P5); a new quantity passes P4 and P6 and lands a
   row in `empire-resource-ssot.md` §3 in the change that ships it.**
5. **Determinism (P13).** Every stock, flow, price and settlement that changes hashed state is computed
   inside `TurnEngine.Step` from hashed state, in stable id order. Relation facts that trade reads are
   world-hashed state or logged inputs to the step. No wall clock, no `System.Random`, no `Stopwatch`
   in `gk-core/src/FusionRpg.Core/World`, `Battle` or `Effects`
   (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-48`).
6. **Ledger before balance (P14).** Every mutation of a banked or world stock carries a dedupe key from
   a durable fact id: `(save_id, empire_id, world_id, turn, factKind, sector, good)`. The key grammar
   and the closed `factKind` vocabulary are `trade-foundation`'s; no sub-program mints a second one.
7. **PS-5 scaled capacities.** Within one economy loop, faucet and sink read the same scale, or neither
   does (`power/ssot-power-scale.md` §10.4). Lane throughput, warehouse capacity, clearing capacity and
   order steps read the **same scaled value as the goods they carry** (value-normalised units), each
   with a row in `ssot-power-scale.md` §10. A flat capacity facing a scaling good is a hidden ceiling,
   which the caps rule forbids. Loam stays Θ-invariant (§10.4 decided "neither" for loam).
8. **No per-unit simulation.** Pooled stock per (sector, good); aggregate flow per lane; vehicles are
   capacity. Turn cost scales with sectors × goods + routes × goods × transit turns, never with cargo
   volume. One flow pass plus at most one redistribution pass; paths recompute on graph change only;
   routing never calls the O(V⁴) `ReconnectionCost` sweep.
9. **One ActorHub compose, one read.** Any number that changes what a creature's stats are (legion
   standards, traditions, doctrine combat effects, legion equipment, a warden's strength) contributes
   through a registered `IActorStatSubsystem` or atom reader with a GG-49 SourceId, or consumes Hub
   output. No `LegionComposer`, no trade-local fold. Guard: `gk-core/scripts/guard-actor-hub.py`.
10. **SOLID and one mechanism.** One `Logistics` phase in the one turn engine; one valuation function
    for both sides of every deal; one structure corpus; one storylet engine; one relation ladder; one
    capacity axis per stock family. A caravan is a legion on a standing order, never a separate entity
    kind or mode (`WorldEntityKind.Caravan` is retired). Extending along a SOLID-violating seam waits
    for a named remediation.
11. **Every empire runs the same economy.** A rule that throttles the player's goods throttles every AI
    empire's; a rule that binds only the player is a handicap and says so.
12. **The balance surface is data; no hard ceilings; one power ladder.** Numbers live in
    `data/tuning/trade.v{n}.json` and `data/tuning/diplomacy.v{n}.json` (both proposed; neither file
    exists yet), published through `gk-core/tools/tuning/publish.py`. A limit on a magnitude is a soft cap; a
    per-turn rate is a structural limit and says so in a comment. Integer magnitudes are `long`,
    `checked`, widened before multiplying, divided by 1000 last. Floating point is allowed; a `double`
    feeding a hash records a platform stamp.
13. **Generated content obeys the seed law.** Seedsmith writes identity; deterministic tables write
    magnitudes; the runtime rolls concrete objects. Generated trees are never hand-edited.
14. **A guardrail validates the contract, never a population.** No test pins how many goods, routes,
    clans, structures or storylets exist, or a generated name. Reports print scale; they never assert it.
15. **One world clock.** Virtual turns, End Turn. No fourth clock.
16. **Buildings unlock features, through one gate** (round 4 §B; round 5 X1, **amended by round 6 C2**).
    Every trade and logistics feature in a sector is unlocked by a specific building kind whose tiers are
    `variants` of one row, and every gate reads `trade-foundation` `sector-features` — never a
    program-local "has building" check and never a `StructureKind` used as one. **X1's amended wording:** a
    new `StructureKind` is added only where loam or siege rules need one — **plus the one neutral
    `StructureKind.Feature`, which every feature building loads under and which no gate reads.**
    `StructureKind.Exchange` is withdrawn. The amendment exists because a row cannot load without a kind
    (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`;
    `IsKnown` at `:330`), so six of the seven feature buildings could never be placed, built or counted —
    every gate read tier 0 and the A1 start kit placed rows that never loaded (audit C2). `Feature` does
    nothing in the loam or siege economy; its behaviour is its `FeatureUnlock` — the `Obstacle` precedent
    (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`).
17. **A feature building counts for nobody until one faction owns both its sector and its slot**
    (round 6 S1). The rule lives once, in `sector-features` (`CountsFor`/`TierFor`, over
    `WorldSlot.OwnerFactionId` at `gk-core/src/FusionRpg.Core/World/WorldState.cs:105` and
    `WorldSector.OwnerFactionId` at `:158`), and **every feature gate reads `TierFor` or `FactionTier`**;
    owner-blind `TierOf` stays only for non-gate ground reads (report, inspector, editor, "build one here").
18. **One capability flag and one ruleset bump per wave, and one family landing order** (round 6 C1). A
    flag never spans waves; a wave takes exactly one bump, shared by the rows it registers; a wave that
    grants no capability takes neither and says why. The order, the flag per wave and the bump ordinal live
    in [trade-network/landing-order.md](trade-network/landing-order.md), which also carries the
    `WorldCanonical` append order, the hot-file landing order, one creator per tuning file, the golden
    re-bless points and the cross-program blockers.
19. **Trade goods cross worlds only by a rift-trade route** (round 6 S2). An advance is a weight-limited
    transit — Σ(unit count × that unit type's carry capacity), read from `world.carry.capacity`, with units
    and goods drawing on the same limit (W1). Import/export through the rift gate is **`world-transit`**'s
    and the six `world.*` channels are **`world-derived`**'s: two named future programs (W2, D2). No spec in
    this family implements either; each consumes their reads **behind a stated default**, from Hub output,
    never a private formula.

## 6. Where things live

| Artifact | Path |
|---|---|
| Umbrella map (this file) | `docs/architecture/trade-network-map.md` |
| Sub-program map | `docs/architecture/trade-network/<sub-program>-map.md` (`legion-build` keeps its own top-level `docs/architecture/legion-build-map.md`) |
| Module spec | `docs/architecture/trade-network/<sub-program>/spec-<module-id>.md` |
| Plan / tasks | `tasks/trade-network-<sub-program>-plan.md` / `tasks/trade-network-<sub-program>-todo.md` |
| Tunables | `data/tuning/trade.v{n}.json`, `data/tuning/diplomacy.v{n}.json` (proposed) |

Module ids are unique across the umbrella, so a task list can name a module without its sub-program.

## 7. Contradictions found between the ideal and the code (2026-09-19)

Each was read in code this session. None changes a decision; each changes a sub-program's starting
point.

| # | The ideal says | The code says | Consequence |
|---|---|---|---|
| X1 | Production halts at capacity — *"the shipped decision-22 rule for construction stocks"* (ideal §8.2, citing `StructurePolicy.cs:56-66`) | `StructurePolicy.IsHaltedByCapacity` (`gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:58`) has **no caller**. Rubble and ironwork production is *"uncapped by design"* (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:77-81`). Loam clamps at capacity and reports `loam.overflow` (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-64`) | Decision 22 is a **wiring gap**, not a shipped rule. `sector-yield` `production-halt` is its first caller |
| X2 | Bank points are *"the capital and any vault-role structure"* on the `bank` structure role (ideal §8.5) | The corpus's `bank` role means *"the Tier-2 faucet"* — the soul conduit and the reliquary (`gk-data/packs/fusion/data/seed/structures/bank/soul-conduit.json`, whose provenance cites structure-seed-ideal §5.21 R6). The soul conduit ships as a `Yield` structure paying 20 **loam** a turn (same file, `magnitudes`). No structure takes goods off the map | A bank point is a new capability, not an existing role. `sector-yield` `bank-points` states which rows carry it (§ that map) |
| X3 | The stamp's home is `rpg_worlds.ruleset_version`, *"always written as 1"* | Correct, and worse than stated: the column's default is 1 (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:31`), world creation writes the literal 1 (`:244`), while every turn-log row writes the live `TurnEngine.RulesetVersion`, which is **13** (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:675`; `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`; re-verified 2026-09-20, round 5 X6) | The column has never carried a real ruleset. Backfill must not read it as one (`trade-foundation` `world-stamp`) |
| X4 | *"Old worlds keep their rules, new worlds get trade"* (§14 D-C) with tuning versions in the stamp | Tuning is loaded once per process into static policies (`gk-core/src/FusionRpg.Server/Program.cs:36`, `:48`, `:74`, `:243`); nothing can run two tuning versions side by side | The stamp **records** tuning versions and makes replay refuse honestly on a mismatch; *rules* mean capability flags. A balance publish applies to every world, as it does today. Stated as an assumption in `trade-foundation`, not re-opened |
| X5 | PS-5 must pick one read for the essence loop (§14b) | Both halves are flat today: the expedition essence faucet adds 1 per kill (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:139-141`) and the fusion essence cost is a flat `int` (`gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs:5`, `EssenceCount`). That satisfies PS-5 ("neither"), but `ssot-power-scale.md` §10.4 already decided essence **must** scale | `sector-yield` `essence-loop-read` carries §10.4's decision to both halves at once; the fusion side is a cross-program change |
| X6 | Phase order `Reveal → … → Production → Growth → Pressure → Events → Snapshot → Intel` (§5) | `Step` also runs `Assaults` between `Sieges` and `Production` (`TurnEngine.cs:195-196`) | None: `Logistics` still goes after `Production`, before `Growth` |
| X7 | *"11 roles incl. `store`, `move`, `bank`, `refine`, `extract`"* (ideal `trade-network-ideal.md:161`, counting `wonder`) | The closed role list has **ten** (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41`); `gk-data/packs/fusion/data/seed/structures/wonder/` is a directory whose rows are `Extract` and `Bank` (`empire-seed-map.md` §11 item 1) | Ten roles today; `exchange` (D-E1) makes eleven. `empire-seed` `exchange-role` and `decision-45-revision` carry it |

## 8. Owner questions

None at the umbrella level. Every question it raised is closed in the ideal (§14, §14b) or decided by a
rule the repo already states. The sub-program questions raised after approval are answered in
[decisions-round-4.md](trade-network/decisions-round-4.md) (round 4 Q1–Q12; round 5 A1–D1); `sector-yield`
Q1 (umbrella X2) is answered by round 4 §B (the Counting House).

## 9. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: world turn engine, economy/resources, structures,
    tunables, power scale, data/SQL (ledgers), stats (legion-build only, via ActorHub).
[~] Session boundary: recorded in tasks/sessions/trade-network-idea-20260919.json; this file is inside
    its `paths`. `session-boundary-check.py --session trade-network-idea-20260919` exits 1 on the
    crossing already recorded in that file's notes (broad worktree lanes); this file is new, so it
    cannot conflict.
[x] I read every doc in the §1 rows this session: Economy (empire-resource-ssot, empire-economy-ssot
    §5-§6, economy-principles P13-P14 and §12-§13), Any cap / numeric / power (ssot-power-scale §10,
    §10.4), tunables (via PRINCIPLES §5 and CLAUDE.md), Data/SQL (spec-save-identity new-table rule),
    Anything at all (decisions.md rows, PRINCIPLES). Not read in full this session:
    software-architecture.md, data-architecture.md, tunables-ssot.md, spec-soul-economy.md — their
    rules were taken from PRINCIPLES.md's digest and CLAUDE.md, which restate them.
[x] I checked decisions.md for a lock: world turn phase order (:7), empire resource registry (:108),
    save identity (:80), scoped inventory (:47), power scale (:57), magic numbers (:63).
[x] Every factual claim cites file:line.
[ ] audit-doc-citations.py --scope on this file: see the session's report for the result.
[x] I verified claims against code, not comments (X1-X6 were each read in code).
[x] I read the surrounding section of every rule I quoted.
[x] Constraints tested, not assumed: no "moves goldens" or "needs sign-off" claim is made here.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated: the contradictions are recorded here and in the two sub-program maps this
    session wrote; the ideal is not edited by this session (outside this task's scope).
[x] No assertion pins a population count or generated text (invariant 14).
[x] No event-refreshed cache is introduced at the umbrella level (path caches belong to
    logistics-flow, which must list its triggers: lane added, lane cut, owner change, treaty change).
[x] No ordering-fixed acceptance criterion at this level.
[x] ActorHub: legion-build contributes through the Hub; nothing here composes actor numbers.
[x] No SOLID-violating parallel path: one phase, one ledger key grammar, one valuation, one corpus.
[ ] New rules and their registry rows: invariants 6 and 8 (ledger keys; no ReconnectionCost in
    routing) get guards in trade-foundation; the rest reuse existing guards. Rows land with those
    modules, not with this map.
```

## 10. Round 5 (2026-09-20)

Applied from [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) "Round 5" (R5-A owner
answers, R5-X cross-cluster rulings), which binds every map and spec of the family. Code citations this pass
touched were re-opened on `features/mega-merge`.

| Ruling | What changed at the umbrella | Where it lands in the sub-programs |
|---|---|---|
| **X1** one feature gate | New invariant 16 | `trade-foundation` `sector-features`; `fleet` `depot`, `counterparties` `diplomatic-stance`, `rift-trade` `crossing-anchor`, `sector-yield` `bank-points`/`warehouse-axis` delegate to it |
| **X3** AI treasury writer | CM3: `empire-treasury` writes, registered into `banking-fact`'s destination seam | `sector-yield` `banking-fact` §2; `counterparties` `empire-treasury` |
| **X5** step order | §1 names `logistics-flow`'s L0–L8 table as canonical; CM4 re-worded | `logistics-flow` `logistics-phase` §1 |
| **X6** staleness | Income parity → `sector-yield` (§1 table and paragraph); `RulesetVersion` 13 at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125` (§7 X3); `Assaults`, `Program.cs` and `ExpeditionResolver.cs` citations re-pointed | — |
| **X7** power roll-up | Owner is `legion-build` `legion-power`: lane loss (escort strength), warden defence and AI force estimates cite it | `logistics-flow` `lane-loss`; `fleet` `escort-link` |
| **X8** upgrade verb | §4 `world-map` row | `trade-foundation` `sector-features` §4 |
| **X11** system commands | Closed set `release-warden`, `rift-window`, `rift-arrive`; `depart`/`advance` are the player's orders | `trade-foundation` `system-commands` |
| **X12** caravan building | `caravan-yard` is the row id; `convoy-depot` is its tier-2 variant | `fleet` `depot` |
| **X13–X15** | Bank point and storage read through `sector-features`; the passage seam receives the logged band snapshot and `counterparties` keeps one step-input table (CM1 unchanged); the banking hold follows A4 | `sector-yield`; `counterparties` `relation-facts`; `logistics-flow` `auto-banking` |
| **A1** start kit | Every empire's seat (player and AI) starts with a tier-1 Counting House and a tier-1 Storehouse | Placement: `world-continuity` world creation (every seat it creates); `counterparties` `empire-roster`, `clan-seeding` |
| **A2–A4** | — | `sector-yield` `warehouse-axis` (base yard), `banking-fact` (rate, hold) |
| **B2, B3, C1–C3** | — | `rift-trade` `crossing-anchor` (Wildland slot); `fleet` `depot` (foreign-hub yard, provisioning top-up); `counterparties` `diplomatic-stance` (offerer-only Embassy, deliberate embargo needs a Consulate) |

Each touched sub-program map carries its own "Round 5 (2026-09-20)" note with the per-spec detail.

## Audit 2026-09-20 (global)

An independent, read-only audit of all 13 maps, the 150 module specs and the round-4/5 register:
[trade-network/audit-2026-09-20-global.md](trade-network/audit-2026-09-20-global.md). It changed no spec; the
findings are for the cluster owners and the owner. **3 Critical, 8 Major, 20 Minor**; 30 cross-program asks.

| # | Finding (short) | Affects this map |
|---|---|---|
| C1 | One capability flag per sub-program gates behaviour that lands in several waves, so a world stamped between waves changes rules mid-life (D-C) — owner question 1 | §5: add the chosen rule as an invariant |
| C2 | Six of the seven feature buildings can never load: rows ship `structureKind: none`, a row loads only with a kind, and X1 forbids new kinds — owner question 2 | §4 `empire-seed` row; invariant 16 |
| C3 | Banking waits on `save-identity` SE4.38, which is not scheduled — owner question 3 | §3 item 2 |
| M1 | Eight dependency edges point up the build order (`crew`, `clan-seeding`, `relation-facts`, `advance-carry`, `legion-equipment`, …) | §2's *"Arrows never point back up"*; §1 row 10 (legion-build also depends on `sector-yield`) |
| M2–M4, M7, M8 | No family ledger for `RulesetVersion` bumps, `WorldCanonical` append order, hot-file landing order, `structure-seed` publishes and corpus regeneration, or versioned tuning-file creators | proposed new section here: "Integration ledger" |
| M5 | `sector-features` lands after empire-seed's schema widening, not "independent" | §3 item 1 |
| M6 | Seedsmith, corpus and `gk-core/data/tuning/**` paths have no verification boundary | §3 item 1 (before empire-seed I1) |
| m9 | The §10 A1 row names `clan-seeding` as a start-kit placer; A1 is for empires only | §10 A1 row |

Build-readiness of the first slice: 19 modules ready, 9 ready with a stated caveat, 5 blocked
(`material-ledger`, `trade-structure-rows`, `banking-fact`, `yield-structures`, `essence-loop-read`).

## Round 6 (2026-09-20) and the landing order

Applied from [trade-network/decisions-round-4.md](trade-network/decisions-round-4.md) "Round 6", the owner's
decisions after the standards audit. They bind every map and spec in the family.

**The family's integration ledger is [trade-network/landing-order.md](trade-network/landing-order.md)** —
one file answering the global audit's M1–M8: the wave order with a capability flag and a bump ordinal per
wave, the eight backwards edges and their resolutions, the shared-file landing order with the one-appender
rule, one named creator per versioned tuning file, the golden re-bless points, and the cross-program
blockers with who must land first. Invariants 16–19 above carry the rules; that file carries the order.

| Ruling | What changed at the umbrella | Where it lands in the sub-programs |
|---|---|---|
| **C1** one flag and one bump per wave | New invariant 18; `landing-order.md` §1 R1–R4 and §2 | Every flag owner names its wave and its bump: `sector-yield` 7 waves, `logistics-flow` 5, `fleet` 3, `counterparties` 3, `rift-trade` 3. `trade-foundation` `world-stamp`'s requested-rows table is replaced with the per-wave list; **this closes its owner question OQ1 as option (a)** |
| **C2** one neutral `StructureKind.Feature` | Invariant 16 amended, with X1's new wording quoted in full | `trade-foundation` `sector-features` §Dependencies (the rule and the precedent), `fleet` `depot` §1, `rift-trade` `crossing-anchor` §1, `counterparties` `diplomatic-stance` §9, `clan-seeding`; the rows themselves are `empire-seed` `trade-structure-rows`' and `exchange` retires `StructureKind.Exchange` |
| **C3** banking waits on the save-identity re-key | §3 item 2's sequencing, via `landing-order.md` §7 | `trade-foundation` `material-ledger` §Dependencies; `sector-yield` `banking-fact` **splits its landing** (§1a) into the phase slot (no ledger, row 4) and the banking step (row 8) so `logistics-flow` does not inherit the wait; `counterparties` `empire-treasury` §7 states that every treasury reads zero until then |
| **S1** a building counts for nobody until one faction owns both | New invariant 17 | `sector-features` §5a owns `CountsFor`/`TierFor`; `bank-points`, `warehouse-axis`, `depot`, `crew`, `crossing-anchor`, `diplomatic-stance` and `clan-seeding` all move off owner-blind `TierOf` |
| **S2 / W1 / W2** trade goods cross only by rift route; a weight-limited advance; `world-transit` named | New invariant 19 | `rift-trade` `crossing-goods` (this table is *the* trade channel), `fleet` `carried-goods` §5 (**FQ3 / ask A15 answered**: excess refused at `depart` admission), `goods-cargo-fate` §2, `sector-yield` `legion-equipment-stock` §3 |
| **CQ2** legion equipment and doctrine upkeep may draw banked goods | — | `counterparties` `empire-goods-sinks` §5 (two recurring sink reasons, shortfall only, symmetry tested against invariant 11 — **this answers its map's CQ2 and removes the finite-sink gap**), `empire-treasury` §7, `sector-yield` `legion-equipment-stock` §3a; the legion-build half is filed as an ask |
| **Q-A** war inside a treaty's minimum term also writes `treaty.broken` | — | `counterparties` `diplomacy-facts` §7a (two facts in one step, the vocabulary still pinned at 12 — only the writer column widens), `relation-facts` §2 |
| **L6** forging a standard needs its own building | — | `trade-foundation` `sector-features` §1: the closed feature vocabulary becomes **nine** members (`standards`, the Standard Hall); its maximum tier is an ask to `legion-build` `legion-standards` |
| **D2** six `world.*` channels compose in `ActorHub` | New invariant 19's second half | `fleet` `carried-goods` §3 (`world.carry.capacity`, default `bearers × GoodsPerBearer`), `depot` §4 (`world.march.range`, `world.supply.burn`, default `LegionSupply.Capacity`/`Burn`), `logistics-flow` `lane-loss` §4a (`world.hazard.resist`, default 0), `escort-link` (reads neither; `legion-power` stays the strength source), `crew` (staffing is **not** one of the six — X9) |

**Still open at the umbrella after this pass:** nothing that this family can decide. The remaining blockers
are other programs' schedules — `save-identity` SE4.12–SE4.38, the power program's §10 rows, world-map's
`BuildResolver` arms, and the verification-boundary rows for seedsmith, the corpus and `gk-core/data/tuning/**` —
each listed in `landing-order.md` §7 with the wave it blocks.

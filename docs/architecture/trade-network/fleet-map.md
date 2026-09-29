# Capability map: `fleet`

**Status: APPROVED 2026-09-19** (owner). Sub-program 4 of the [trade-network](../trade-network-ideal.md)
umbrella (ideal §11). Owner decisions at approval are recorded below; module specs are written.
**Reconciled with the round-4 owner decisions 2026-09-19** ([decisions-round-4.md](decisions-round-4.md)) —
see *Reconciliation 2026-09-19 (round 4)* at the end; where this map and that register disagree, the
register wins.
**Specs:** `docs/architecture/trade-network/fleet/spec-<module-id>.md` — see *Module specs* below.
**Plan / tasks:** `tasks/trade-network-fleet-plan.md` / `tasks/trade-network-fleet-todo.md` (new; the
umbrella's path convention, `trade-network-map.md` §6 — this line said `tasks/fleet-plan.md` until
2026-09-19, C14).

**Ideal it implements:** [trade-network-ideal.md](../trade-network-ideal.md) §8.3 (caravans are legions,
round 3), §7.6 (deal lifecycle, transit, capture mid-route), §8.5 (depots), §14b; and the trade half of
[legion-build-ideal.md](../legion-build-ideal.md) §6.5. It does not reopen any decision in either.

## Owner decisions — 2026-09-19 (at approval)

| # | Decision | Where it lands |
|---|---|---|
| Q1 | **Goods travel by lane flow wherever an open path exists; a caravan (an automated legion) runs only where the path crosses closed ground or another world.** "Open path" is `logistics-flow` `path-cache`'s traversal — the one predicate lane flow uses (own, unheld, and `passage`-or-better ground on the Supply lens). A caravan that finds an open path does not start a trip; one already under way finishes it | `spec-trade-route-order.md` §4; ask A9; resolves C7 |
| SO | **Standing orders carry a kind, and each kind has its own resolver** — a request to `legion-build` (ask A1), recorded here as decided. The **trade-route** kind expresses the load–march–unload–return loop; `crew` is a second kind. `legion-build` keeps the store, the set/clear command, precedence and the emitter | `spec-trade-route-order.md`, `spec-crew.md`; resolves C6 |

## Module specs

| Module | Spec |
|---|---|
| `carried-goods` | [fleet/spec-carried-goods.md](fleet/spec-carried-goods.md) |
| `depot` | [fleet/spec-depot.md](fleet/spec-depot.md) |
| `crew` | [fleet/spec-crew.md](fleet/spec-crew.md) |
| `trade-route-order` | [fleet/spec-trade-route-order.md](fleet/spec-trade-route-order.md) |
| `escort-link` | [fleet/spec-escort-link.md](fleet/spec-escort-link.md) |
| `interception` | [fleet/spec-interception.md](fleet/spec-interception.md) |
| `goods-cargo-fate` | [fleet/spec-goods-cargo-fate.md](fleet/spec-goods-cargo-fate.md) |

Where a spec corrected this map after reading the code, the correction is applied below and listed as
C8–C14; the round-4 reconciliation (2026-09-19) added C15–C21.

---

## What this sub-program is

**A caravan is a legion.** Owner ruling (2026-09-19): *"A caravan is an automatic legion, with or without a
commander. We don't need to split legions into multiple modes; we need to extend its architecture."* This
sub-program is the trade extension of that one legion architecture: a legion given a **trade route** as its
standing order loads goods at a **depot**, marches its route, unloads at the far hub, and comes back — every
turn re-emitting ordinary commands through the same pipe every human and AI order uses. Its capacity comes
from its **bearers**; its cost is the loam burn and the action budget every legion already pays. **Crews** —
bearers assigned to depots and hubs — are the labour those buildings need. An **escort** is a legion in the
`escort` stance. **Interception** is an ordinary `Sector`/`Lane` battle. Goods on a caravan that is destroyed
follow **cargo fate**. Nothing here is a new entity kind, a new battle kind, a new pricer or a second
standing-order mechanism.

Who needs a caravan (ideal §8.3, §10 C11): **not banking** — own goods reach bank points by lane flow alone
([logistics-flow](logistics-flow-map.md)), which already crosses own and unheld ground and any ground whose
owner grants `passage` (ideal §7.6). Caravans serve what lane flow cannot: ground that stays **closed**
(hostile, embargoed, contested) — a caravan can fight through it; a **severed** own component cut off by such
ground; a **foreign** hub's filled orders **when no open lane-flow path reaches it** (owner decision Q1);
and the in-world legs to a **cross-world** route's crossing anchor ([rift-trade](rift-trade-map.md)) that
lane flow cannot reach.

**Loops:** Place 4 (world map — a caravan is a legion on lanes), Place 3 (farm/hold/defend — escort and
interception), Place 5 (world stage — depots and crews in held sectors). World clock only; nothing touches
the lawn or PvZ.

### Load-bearing rules restated

1. **One legion architecture** (legion-build ideal §3.6; owner ruling L3). Caravan, escort and crew are
   **orders and stances on legions**, never entity kinds or modes.
2. **Standing orders belong to `legion-build`** (its §6.3). This map registers a **trade-route order kind**
   through `legion-build`'s standing-order seam; it never stores, re-emits or replays orders itself.
3. **One battle engine** (`battle-engine-ssot.md` §1, §5). A caravan fights through the existing
   `BattleKinds.Sector`/`Lane` requests; it owns no mechanism. Its loop (who is placed where) is
   `legion-build`'s role-aware placement.
4. **One ActorHub compose.** Nothing here produces or consumes an actor combat number; an escort's or a
   crew's strength is what the battle engine and `ActorHub` already compute.
5. **Capacity must not scale with the thing that burns it** (ideal §3.13; `empire-economy-ssot.md` §6). Goods
   capacity comes from **bearers**; burn stays by headcount (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`).
6. **One capacity axis per stock family** (ideal §3.12). Carried goods get their own axis — not `CarriedLoam`,
   and not the item cargo overlay.
7. **Determinism, numbers, tunables** as in `logistics-flow`: every hashed change inside `Step`; `long`,
   `checked`; balance numbers in `data/tuning/trade.v{n}.json` (new); no hard ceilings (a caravan count is
   priced by the per-legion cost curve `legion-build` owns, never capped).
8. **Every empire runs the same caravans** (principle 10). The AI files the same orders through the same
   admission; `trade-ai` decides *when*, this map decides *how*.

## Assumptions (correct before approving)

1. `legion-build` lands before this map's wave 2 (module ids from [legion-build-map.md](../legion-build-map.md)):
   `standing-orders`, `escort-stance`, `member-stack` (stack `Count`), `raise-choice` (bearers can be raised),
   `role-aware-placement`, `field-battle-kinds` (`Sector`/`Lane` battles resolve), and `caravan-kind-retire`.
   Its `standing-orders` stores a **kind-keyed** order with a per-kind resolver and a small per-order state
   record (owner decision SO; `legion-build-map.md` §5.8 still says one `WorldCommand` — that map owes the
   amendment, ask A1).
2. `logistics-flow` lands first: the Logistics phase, path cache, lane loss, facts vocabulary. Goods
   loaded on or unloaded from a caravan move **inside** that phase.
3. `sector-yield` supplies located goods in warehouses; a depot's warehouse is a warehouse.
4. Until `exchange` lands there is nothing to buy or sell. Fleet's first playable use is hauling own goods
   out of a severed component and to a cross-world crossing depot; foreign trade arrives with `exchange`'s
   Access and orders, with no change to this map's modules.

---

## What the code says (verified 2026-09-19)

| Fact | Where |
|---|---|
| `WorldEntityKind.Caravan` is declared and never constructed; its only readers are a display-name label, one naming test and one FE translation row | `gk-core/src/FusionRpg.Core/World/WorldState.cs:61-68`; `gk-core/src/FusionRpg.Core/World/EntityNaming.cs:34`; `gk-core/tests/FusionRpg.Core.Tests/World/EntityNamingTests.cs:72-76`; `gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.ts:53`; `gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.test.ts:53` |
| Entity kinds are persisted and hashed **by name**, not ordinal — removing a member moves no hash | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:60,157`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:378,632` |
| A legion carries: position, lane progress, stance, movement budget, routed flag, members, `CarriedLoam` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:286-326` |
| Member roles are `Fighter`, `Bearer`; raising founds exactly one Fighter | `gk-core/src/FusionRpg.Core/World/WorldState.cs:269-273`; `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:132-141` |
| Loam carry capacity scales with bearers; burn with headcount | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25` |
| Item cargo capacity (the Data-side overlay) scales with **every** member, by an owner decision in that program | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:20-47` |
| Item cargo commands resolve **Data-side after `Step`**, never in the engine | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:80-117` |
| A destroyed legion's item cargo moves into a revisit-lootable corpse cache at its last sector or lane (`cargo-fate`, built) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:5-19,47`; called from `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:349-352` |
| The AI builds one `WorldCommand` per legion per turn, in the player's shape | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582` |
| A re-issued march resumes mid-lane | `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-31` |
| Stances are `march`, `scout`, `hold`, `dowse` — no `escort` | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-22` |
| Contact builds `Lane` and `Sector` battle requests kind-agnostically | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:150-151,278-280`; kinds `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6-22` |
| The only resolver refuses every non-district kind — a lane or open-field sector battle today has no winner | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:101-104` |
| Every other faction is hostile; every non-guard entity projects a zone of control | `gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:15-16,28` |
| `convoy-depot` and `waystation` rows exist; `convoy-depot` is identity-only (no `magnitudes`) | `gk-data/packs/fusion/data/seed/structures/move/convoy-depot.json`; `gk-data/packs/fusion/data/seed/structures/move/waystation.json`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` |
| Waystation range is a hop count from an own source | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:177-192` |

---

## Modules

Stable kebab-case ids, chosen once. Model-free: nothing here needs generated content; the depot's
magnitudes come from `empire-seed` tuning bands.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `carried-goods` | A hashed, sparse goods pool on a legion; capacity from bearers on its own axis; load/unload inside the Logistics phase | `logistics-flow` `logistics-phase`, `logistics-canonical`; `sector-yield` | 1 |
| 2 | `depot` | The **caravan building** (one structure row, today `convoy-depot`; tiers **Caravan Yard** T1 → **Convoy Depot** T2, round 4) as the only load/unload point and the start of route range; per-tier throughput and provisioning; its warehouse and loam upkeep | `carried-goods`; `sector-yield`; `empire-seed` tier variants and magnitudes; `trade-foundation` `sector-features` (ask A11) | 1 |
| 3 | `crew` | Crews as assigned bearer units: a legion on a crew order naming a building's **slot** is that building's labour input (caravan building, trade hub, Rift Anchor) | `depot`; `legion-build` standing orders, stack `Count` | 2 |
| 4 | `trade-route-order` | The trade-route standing-order kind: load → march → unload → return, re-emitted through `legion-build`'s seam | `carried-goods`, `depot`; `legion-build` standing orders | 2 |
| 5 | `escort-link` | Escort use: an `escort`-stance legion screens a caravan — joins its battles and posts lane protection | `trade-route-order`; `legion-build` `escort` stance; `logistics-flow` `lane-loss` | 3 |
| 6 | `interception` | Hostile contact with a caravan is an ordinary `Sector`/`Lane` battle; routed and destroyed outcomes applied to carried goods | `trade-route-order`; `legion-build` battle kinds routed | 3 |
| 7 | `goods-cargo-fate` | A destroyed caravan's goods become a located goods cache at its last place (cargo-fate's rule, hashed carrier); capture mid-route | `interception`; `scoped-inventory` `cargo-fate` (rule) | 3 |

**`WorldEntityKind.Caravan` retirement is owned by `legion-build`** — its module `caravan-kind-retire`
(`legion-build-map.md` row 2 and its X15, *"Owned here … `fleet` consumes the result"*). This map carries
no module for it and adds only an acceptance criterion that every caravan is a `Legion`.

**Build order:**

```
Wave 1  carried-goods → depot
Wave 2  crew ∥ trade-route-order          (needs legion-build standing orders)
Wave 3  escort-link ∥ interception → goods-cargo-fate   (needs legion-build escort + battle kinds)
```

**Dependency direction.** Everything points at `logistics-flow` and `legion-build`; neither depends on this
map. `rift-trade` depends on `depot` and `crew`. `exchange` depends on `crew` (hub labour) and on
`trade-route-order` (a caravan's arrival is where a foreign order fills). No cycles.

### Ownership of the Caravan retirement

Both ideals list it: trade-network §5 (wiring gap) and §8.3, and legion-build §4 (wiring gap) and §6.6.
**Assigned to `legion-build`.** Reasons: the retirement is a change to the legion architecture's entity
vocabulary, which `legion-build` owns (its §3.6 "one legion, many behaviours"); `legion-build` starts in
parallel with `trade-foundation`, well before this map's wave 1, so the kind is gone before any trade code
could construct it; and one owner means one change touching `WorldState.cs`, `EntityNaming.cs`, the naming
test and the FE enum row. The change is hash-neutral (kinds are written by name, `WorldCanonical.cs:157`) and
save-neutral (no row was ever written with it). `legion-build-map.md` already carries it as
`caravan-kind-retire` (wave 1), so the two maps agree.

---

## Module detail

### 1. `carried-goods`

**Capability.** A legion can carry **located goods**: a sparse per-good pool on `WorldEntity`, hashed, with
its own capacity axis — `Σ bearer count × fleet.goodsPerBearer`, in value-normalised units that read the
same scale as the goods (PS-5, as `logistics-flow`'s throughput does). It is neither `CarriedLoam` (loam's
axis) nor the Data-side item cargo overlay (items, unhashed, capacity from every member). A legion standing
at a depot or hub of its own faction **loads** from or **unloads** into that sector's warehouse inside the
Logistics phase, bounded by carried capacity, the warehouse's stock and free capacity, and the depot's
crew throughput. Loading never moves loam and never moves a world stock across a banking boundary
(principle 7); world stocks (rubble, ironwork) may be carried between own sectors like any located good.

- **Built:** the bearer-capacity rule (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`); the entity row
  and its conditional-row canonical form (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:58-68,119-128`).
- **Wiring gap:** bearers are never produced by raising (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:132-141`) —
  `legion-build`'s to close; until then only template bearers exist.
- **Real gap:** the pool, its axis, load/unload.
- **Depends on:** `logistics-flow` (`logistics-phase`, `logistics-canonical`); `sector-yield` (located goods,
  warehouse); `legion-build` (stack `Count` for bearer counting).
- **Touches:** `gk-core/src/FusionRpg.Core/World/WorldState.cs`, `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs`,
  `src/FusionRpg.Core/World/Logistics/Fleet/CarriedGoods.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs`.
- **Acceptance (contract):**
  - Capacity is a function of bearer count only: adding fighters leaves it unchanged; adding a bearer raises
    it by exactly `goodsPerBearer` (scaled). Burn is unchanged by this module.
  - Load/unload conserves goods: Δwarehouse + Δcarried = 0 per good per turn.
  - A legion at a sector it does not own, or with no depot/hub, loads nothing and reports why.
  - Carried goods never exceed capacity; a load that would exceed it loads the remainder only.
  - Sparse: a legion carrying nothing writes byte-identical canonical text to today's.
  - Save → load → hash round-trips with a non-empty pool.
  - Every in-`Step` removal of a legion — battle, starvation, and `world-continuity`'s advance (A15) —
    passes the one carried-goods seam; a source scan fails on a removal site without it (audit 2026-09-20).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet); `FusionRpg.Data.Tests` (round trip,
  in memory). Gap named: `gk-core/src/FusionRpg.Core/World/**` maps only to `core-fallback` in
  `gk-core/scripts/verification-boundaries.v1.json`; the first implementing task adds the
  `core-world-logistics-fleet` owner boundary (`spec-carried-goods.md` Hard edges), which every fleet
  module then uses.

### 2. `depot`

**Capability.** The caravan building becomes playable (round 4: *"Caravans: Caravan Yard → Convoy Depot. T1
legions load and unload goods; T2 more crew, more range"*). It is **one** structure row — **`caravan-yard`**
(round 5 X12; today's identity-only `convoy-depot` row is re-emitted under that id by `empire-seed`) — whose
tier variants are the Caravan Yard (T1) and the Convoy Depot (T2, variant `convoy-depot`); a tier is never a
second row or a second building. Built, and upgraded, through the shipped `BuildResolver`, it is the **only**
place trade legions load from or unload into their own warehouse (an own trade hub no longer is — C15) and
where a trade route's **range starts** (ideal §8.3, §8.5). Route range is the **loam leash** — a caravan tops
up its `CarriedLoam` from its supply pool in supply and burns by headcount outside it
(`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:32-36`, `:64-150`); a route beyond the leash is admitted with a
warning, never refused (C9). **T2 "more range"** is a provisioning top-up on that leash (**round 5 C1**): a
caravan topping up at its own Convoy Depot fills to `Capacity × depot.provisionMilliByTier[T2] ÷ 1000`
(bearer capacity only; FQ2 answered). **A foreign hub is a caravan site only where its owner has a Caravan
Yard in that sector (round 5 B3**; FQ1 answered (b)). **T2 "more crew"** is the T2 point list of `depot.throughputCurveByTier` — a later knee,
never a crew limit. A depot has a warehouse (the `sector-yield` axis) and pays loam upkeep through
`sector-yield`'s `LoamUpkeep` structure term (principle 3) — no second upkeep path. Its load/unload allowance
per turn is a structural per-turn rate: its tier's curve over the labour `crew` reports, diminishing and
uncapped, evaluated by the one `LabourCurve` evaluator.

- **Built:** the structure build pipeline (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs`); the row's
  identity (`gk-data/packs/fusion/data/seed/structures/move/convoy-depot.json`).
- **Wiring gap:** the row has no `magnitudes` block and an empty `variants` list, so it is not
  catalog-loadable (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`).
- **Real gap:** depot semantics (load/unload site, range origin, per-tier output). A placed structure has no
  tier at all (`gk-core/src/FusionRpg.Core/World/WorldState.cs:96-126`; *"a structure has no level of its own"*,
  `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:132-135`) — closed for every round-4 building by
  `trade-foundation` `sector-features` (`WorldSlot.StructureTier`, `StructureDef.Feature`,
  `SectorFeatures.TierOf`; ask A11, answered).
- **Depends on:** `carried-goods`; `sector-yield` (warehouse, structure upkeep term); `empire-seed` (tier
  variants, magnitudes); `trade-foundation` `sector-features` (the `caravans` feature and its tier).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/Depot.cs`, `LabourCurve.cs`, `DepotRange.cs` (new);
  no `StructureKind` member (C22); the Pressure top-up in `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs` (provisioning);
  `data/tuning/trade.v1.json` (new) keys `depot.throughputCurveByTier`, `depot.provisionMilliByTier`.
- **Acceptance (contract):**
  - Load/unload into an own warehouse happens only at a working (constructed, owned) caravan building of
    tier ≥ 1; a building under construction serves nothing; an own sector with only a trade hub refuses
    with `depot.no-yard`.
  - At every labour, the T2 allowance is ≥ the T1 allowance (an upgrade never lowers throughput).
  - A route beyond the loam leash is admitted with a warning naming the shortfall, for every faction (C9).
  - The depot's loam upkeep appears in `LoamUpkeep`'s breakdown through the one structure term (no second
    charge in this module — asserted by summing upkeep with and without the depot).
  - Capture of a depot sector stops it being the old owner's site the same turn; its warehouse goes with
    the sector (the `sector-yield` rule); routes that start or end there are suspended by
    `trade-route-order` with a `caravan.suspended` fact.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet, World/Movement).

### 3. `crew`

**Capability.** *"Crews are units. Hubs and depots need assigned bearers to run — labour is both a production
input and an upkeep line (P11)"* (ideal §8.3). A crew is **a legion on a crew order** standing in the
building's sector: its bearer count is the building's labour. The order names the building's **slot**, not
only its sector (C16): round 4 puts several buildings in one sector, and a sector-keyed read would count the
same bearers for each. No new holder of units exists — the crew stays
a legion, keeps paying the burn and action budget every legion pays (*"upkeep, without double charging"*,
ideal §8.3), defends the sector if it is attacked, and returns to service when the order is cleared. A
building's output rises with crew with diminishing returns (P9) — the depot's curve is `depot`'s, a hub's
clearing rule `exchange`'s; `crew` owns only the labour read (a bearer **count**), exposed to the caravan
building, `exchange`'s trade hub and `rift-trade`'s Rift Anchor. The crew order is a
standing-order kind registered through `legion-build`'s seam, like `trade-route-order`.

- **Built:** bearers and roles (`gk-core/src/FusionRpg.Core/World/WorldState.cs:269-283`).
- **Wiring gap:** bearers are never produced (`RaiseResolver.cs:132-141`); siege placement has no role filter
  (legion-build ideal §4) — both `legion-build`'s.
- **Real gap:** the crew order kind and the labour read.
- **Depends on:** `depot`; `legion-build` (standing orders, stack `Count`, bearer production).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/Crew.cs` (new). No tunable (the curve moved to
  `depot`).
- **Acceptance (contract):**
  - A building's labour equals the bearer count of own legions on a crew order naming its slot, standing in
    its sector — fighters count zero; a legion without the order counts zero; a crew of another building in
    the same sector counts zero (no bearer is labour twice).
  - (Diminishing, monotone throughput is `depot`'s curve contract.)
  - A crew legion's loam burn is exactly what the same legion burns off-order (no extra charge).
  - **Order-independent:** assigning the crew order before or after the depot finishes construction gives
    the same labour on the first working turn (both orders tested — the key-set edge is the depot becoming
    active, DESIGN-GATE §2.16).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet).

### 4. `trade-route-order`

**Capability.** The **trade-route** standing-order kind. Its payload names a source caravan building, a destination
(an own caravan building — including one in a Rift Anchor's sector — or a foreign hub once `exchange`
lands), the goods and the per-trip quantity, and, for a foreign hub, the goods to bring back from the
owner's consignment there (C19). Each turn `legion-build`'s standing-order resolver asks this kind for the legion's next
ordinary command — a `move` along the planned path (resuming mid-lane as `MarchResolver` already does), or a
hold at a depot/hub while the Logistics phase loads or unloads — and re-emits it through the one command
pipe. The route's small state (outbound, loading, inbound, unloading) lives in the standing order's own
hashed record, which `legion-build` owns; this module defines its values and transitions. Throughput is not
declared anywhere: it emerges as trips × capacity ÷ round-trip turns (ideal §8.3). Paths use the March lens
(a legion can walk a deep rift) through the same planner the AI uses; crossing another faction's ground
follows the zone-of-control and hostility rules unchanged (so, until `counterparties` makes peace possible,
a caravan entering held foreign ground stops there, exactly as any legion does).

`caravan-send` (ideal §8.7) is **the player's name for setting this order**, not a new command kind, if
`legion-build`'s standing-order command carries an order kind — recommended, so one command sets every
standing order (SOLID). If `legion-build`'s spec instead lands a fixed command, this module adds the kind
through `WorldCommandAdmission`, never a second admission path.

- **Built:** one command shape for every commander and the AI's per-legion order builder
  (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-582`); mid-lane resume (`MarchResolver.cs:29-31`).
- **Wiring gap:** —
- **Real gap:** standing orders themselves (`legion-build`'s — explicitly out of scope of
  `docs/architecture/world-stage/spec-world-commands.md` per legion-build ideal §4); this order kind.
- **Depends on:** `carried-goods`, `depot`; `legion-build` (standing-order seam with per-kind resolvers).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/TradeRouteOrder.cs` (new); the standing-order kind
  registry `legion-build` creates.
- **Acceptance (contract):**
  - A trade route re-emits only command kinds that already exist; the engine sees no new resolution path
    for movement.
  - At a foreign hub, goods move only between the carried pool and the owner's own consignment
    (`exchange`'s record); conservation holds per good.
  - With or without a commander member, the same order produces the same commands (automation reads the
    order, not the roster — legion-build ideal §6.3).
  - Replay: a world stepped from its command log with standing orders reproduces the state hash
    byte-identically.
  - Over *N* uninterrupted round trips, goods delivered = *N* × min(per-trip quantity, capacity) and the
    turns taken = *N* × round-trip turns (the emergent-throughput identity, not a pinned number). Lane loss
    applies to lane flow, not to carried goods; a caravan's risk is interception (C12).
  - A caravan never starts a trip while lane flow has an open path to its destination (owner decision Q1).
  - An AI faction can hold the same order kind and produces the same behaviour (no player branch).
  - Every caravan's `Kind` is `WorldEntityKind.Legion` (the only kind this map ever constructs).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet, World/Movement).

### 5. `escort-link`

**Capability.** The trade use of `legion-build`'s `escort-stance` (*"a legion in `escort` names another legion of
its faction, moves with it along its path, and is present in any battle that legion is drawn into"*,
`legion-build-map.md` §5.9). That module owns the stance, the following and the battle presence. This module
owns only what a **caravan** adds: a caravan's turns are not all marches — it holds at a depot or hub while
the Logistics phase loads or unloads — so the escort must hold with it. (No re-binding on a loop restart
is needed: the escort names the caravan's entity id, which a loop never changes — C11.) It also names the escort answer the
throttle forecast offers (`trade-surface` `throttle-forecast`): the answer files `legion-build`'s escort
command targeting the caravan — no second command. Lane protection from the escort is `logistics-flow`'s
`lane-loss`: by stance weight in v1 (its OD1), and by the escort legion's **power roll-up** once that lands
(round-4 P: a legion's power is the sum of its stacks' Hub power; one read, never a second composer — ask
A13). `escort-link` publishes no tuning row (C21).

- **Built:** contact builds `Lane`/`Sector` requests (`gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:145-156,276-286`).
  **Not built** (C10): a request names one attacker and one defender, and the combatant list is exactly
  those two (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-55`; `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:44-54`).
- **Wiring gap:** —
- **Real gap:** the stance (`legion-build` `escort-stance`); an escort's presence in its charge's battle
  (multi-entity sides — `legion-build`, ask A8); holding with a loading caravan; the `escort` lane-loss row.
- **Depends on:** `trade-route-order`; `legion-build` `escort-stance`; `logistics-flow` `lane-loss`.
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/EscortLink.cs` (new).
- **Acceptance (contract):**
  - Over a full trade loop (march, load, march, unload), the escort ends every turn on the caravan's lane or
    sector, or the report names why it could not (its own budget).
  - At every contact the caravan meets, the escort is in the same battle request (asserted on the request,
    not the winner) — through `escort-stance`'s rule, with no caravan branch.
  - Lane loss with the escort posted is ≤ loss without it, for every input (via `lane-loss`'s
    monotonicity).
  - **Order-independent:** assigning the escort before or after the caravan's order is set gives the same
    first escorted turn (both tested — the key-set edge is the caravan acquiring its order).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet).

### 6. `interception`

**Capability.** *"A hostile legion meeting a caravan triggers the kind-agnostic `Sector`/`Lane` battle"*
(ideal §8.3). Contact with a caravan uses the existing requests unchanged. What this module owns is the
**caravan-side consequence** of the outcome: a **routed** caravan keeps its goods and loses one turn of orders
(the shipped rout rule, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:167-178`), its route resuming after; a
**destroyed** caravan hands its goods to `goods-cargo-fate`. Bearers are placed by `legion-build`'s role-aware
placement (they carry, they do not front-line) — a loop rule, not a mechanism. Today every non-district
battle is refused and has no winner (`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:101-104`), so
interception is inert until `legion-build` routes the `Sector`/`Lane` kinds into the engine; this is a
**wiring gap with a named owner**, not a wall.

- **Built:** contact detection and request building (`MovementPhase.cs:150-151,278-280`); battle kinds
  (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6-22`); rout handling.
- **Wiring gap:** `Sector`/`Lane` battles resolve to no outcome (`DistrictAssaultResolver.cs:101-104`) —
  `legion-build`'s final build-order item (legion-build ideal §10).
- **Real gap:** applying the outcome to carried goods.
- **Depends on:** `trade-route-order`, `carried-goods`; `legion-build` (battle kinds routed, role-aware
  placement).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/Interception.cs` (new); the battle-application seam
  (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs`) as a caller, not a fork.
- **Acceptance (contract):**
  - A caravan in contact produces a request of kind `lane` or `sector` — never a caravan-specific kind (the
    `BattleKinds` set is a closed vocabulary; this module adds nothing to it).
  - Routed: carried goods unchanged; orders dropped for exactly one turn; the route resumes the turn after.
  - Destroyed: carried goods leave the entity in the same step and appear in `goods-cargo-fate`'s cache
    (conservation: carried before = cache after, per good).
  - While the battle kinds are still refused, a caravan in contact keeps its goods and the report records a
    refused battle (the current behaviour, asserted so the later change is visible).
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet, World/Turn).

### 7. `goods-cargo-fate`

**Capability.** *"Goods on a legion that loses a battle follow `cargo-fate`"* (ideal §14b) — and so do goods on
a legion that **starves** (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:134-151`, the second in-`Step` removal
site, C8). `cargo-fate`'s
rule (a) — a destroyed legion's cargo becomes a revisit-lootable cache at its last-known place, a sector or a
lane — applies to carried goods **by rule**; the carrier differs because goods are hashed world state, not
Data-side item rows: the cache is a sparse, hashed **located goods cache** on the sector or lane, created inside
`Step`, claimable by any legion standing at that place with free goods capacity during the Logistics phase,
and fading by a tunable per-turn loss (a sink) so an abandoned cache does not persist forever as free stock.
The same module applies ideal §7.6: goods in transit belong to the buyer, so a **counterparty captured
mid-route** does not touch a caravan already carrying them; goods still in a captured depot's or hub's
warehouse change hands with the sector (the `sector-yield` rule). Rubble and ironwork in a cache stay world
stocks (never bankable from a cache).

- **Built:** `cargo-fate`'s item rule and its place kinds (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:5-19,47`;
  `docs/architecture/scoped-inventory-hierarchy-map.md` module 4).
- **Wiring gap:** —
- **Real gap:** the hashed goods cache and its claim.
- **Depends on:** `interception`, `carried-goods`; `scoped-inventory` `cargo-fate` (the rule, not its tables).
- **Touches:** `src/FusionRpg.Core/World/Logistics/Fleet/GoodsCache.cs` (new); `WorldState.cs`/`WorldCanonical.cs`
  (sparse cache rows); `data/tuning/trade.v1.json` (new) key `cache.fadePerTurnMilli` (bounded ratio).
- **Acceptance (contract):**
  - A destroyed caravan's goods equal the new cache's goods, per good (conservation); a caravan carrying
    nothing creates no cache (the `cargo-fate` "no empty header" rule).
  - A cache on a lane is reachable by a legion on that lane; on a sector, by a legion standing there.
  - Claiming conserves goods; two legions of different factions claiming the same cache in one turn split
    it **pro rata by free capacity** (principle 10), never by faction id — and the result is independent of
    filing order (both orders tested).
  - Fade: the cache never grows; it loses `fadePerTurnMilli` ‰ per turn (clamped [0, 1000]) and is removed
    when empty.
  - No path from a cache credits the wallet directly; goods reach the wallet only by being carried to a
    bank point and banked.
- **Verification boundary:** `FusionRpg.Core.Tests` (World/Logistics/Fleet).

---

## Tunables (keys owed by the specs; values decided by principle)

`data/tuning/trade.v1.json` (new): `fleet.goodsPerBearer`, `depot.throughputCurve` (diminishing, uncapped),
`cache.fadePerTurnMilli` (bounded ratio). The `escort` row of `lane-loss`'s table
(`lane.stanceEscortMilli.escort`) is **`lane-loss`'s key**, published with `legion-build` `escort-stance`;
this map no longer claims it (C21). **Round 4:** `depot.throughputCurve` becomes `depot.throughputCurveByTier`
(one point list per tier) and `depot.provisionMilliByTier` is new (T1 = 1000). `depot.rangeCost`,
`depot.throughputPerCrew` and `crew.throughputCurve` were dropped at spec time (C9; one curve per tier, owned
by `depot`). Per-tier build and upgrade costs are `empire-seed` bands, not fleet keys. Nothing here caps a
caravan count: the per-legion cost curve is `legion-build`'s (`data/tuning/legion.v1.json` (new)).

## Filed asks (other maps)

| # | To | Ask |
|---|---|---|
| A1 | `legion-build` `standing-orders` | **Decided by the owner 2026-09-19 (SO).** Store a standing order as a **kind plus payload with a per-kind resolver and a small per-order hashed state record**, not one fixed `WorldCommand`. The emitter still re-emits ordinary commands into the one pipe; `trade-route-order` and `crew` register kinds through it. `legion-build-map.md` §5.8 owes the amendment in its own spec |
| A2 | `legion-build` `caravan-kind-retire` | None — already carried (row 2, X15); listed so the ownership is visible from this side |
| A3 | `legion-build` `escort-stance`, `role-aware-placement` | The escort follows a legion that is **holding** at a depot for a load/unload turn as well as marching (the table in `spec-escort-link.md` §1); bearers stay off the battle board (their row 3 already says so). *(The row-publishing clause is withdrawn: `lane-loss` owns `lane.stanceEscortMilli.*` and publishes the `escort` row in `escort-stance`'s change — C21.)* |
| A4 | `legion-build` `field-battle-kinds` | None beyond its own scope — interception is inert until it lands, and this map's `interception` acceptance asserts today's refusal so the change is visible |
| A5 | `empire-seed` `trade-structure-rows` | **Widened (round 4):** the caravan building is one row (today `convoy-depot`) with **two tier variants** — Caravan Yard (T1), Convoy Depot (T2) — each with magnitudes (build and upgrade cost, turns, upkeep role term, warehouse band) through tuning bands; and `waystation` range. `spec-trade-structure-rows.md` §5.1 lists the `Move` role as "no new row" — still true, but the row now needs its variants filled |
| A6 | `exchange` | Read `crew` labour for trade-hub clearing capacity rather than inventing a second labour rule; fill foreign orders on a caravan's arrival. **Answered by `exchange`** (`exchange/spec-exchange-hub.md` §2, §4): hub labour is read from `crew`; a caravan's goods at a foreign hub are the owner's **consignment**, with fleet as a writer — adopted by `trade-route-order` (C19) |
| A7 | `trade-surface` | The escort throttle answer depends on `legion-build`'s `escort` stance and this map's `escort-link`, not on `fleet` alone (`trade-surface-map.md` gap table says "needs `fleet` first") |
| A8 | `legion-build` `escort-stance`, `field-battle-kinds` | An escort *"is present in any battle that legion is drawn into"* needs a battle side of **more than one entity**: today a request names one attacker and one defender and the resolver receives exactly those two (C10). Widen the request/combatant seam in the battle-kinds work; `escort-link`'s presence test is skipped, visibly, until then |
| A9 | `logistics-flow` `path-cache` | Expose a point query — *does faction F have an open lane-flow path from sector A to sector B this turn* — on the cache's own traversal, so `trade-route-order`'s need rule (Q1) reads the one predicate. `logistics-flow/spec-path-cache.md` exposes `PathCache.Next(faction, destinationKey, sector)`; registering a caravan's destination as a destination key and asking `Next(F, key(B), A)` is enough. No second traversal |
| A10 | `trade-stories` `trade-quests` | The `recover` template names `claim-cache` (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:119`), the Data-side **item** cache command. A lost caravan's **goods** cache is claimed by presence in the Logistics phase, with a `goods-cache.claimed` fact (`spec-goods-cargo-fate.md` §3); the template's objective should read that fact too (C13) |
| A11 | `trade-foundation` `sector-features` (§2.11) | **Round 4 B needs a placed tier, and nothing had one** (a slot carries `StructureId` and `ConstructionTurnsRemaining` only, `gk-core/src/FusionRpg.Core/World/WorldState.cs:96-126`). **Answered by `trade-foundation`** in the same reconciliation round: `SectorFeature` (closed; `caravans` max tier 2), `StructureDef.Feature`, `WorldSlot.StructureTier`, the upgrade as a `build` of the same structure, and `SectorFeatures.TierOf(sector, feature)` ([trade-foundation/spec-sector-features.md](trade-foundation/spec-sector-features.md)). `depot` gates on `caravans`; `rift-trade` on `cross-world` and `trade`; `counterparties` on `diplomacy` and `trade`. Fleet adds no `StructureKind` member (C22) |
| A12 | `exchange` `exchange-hub` | `spec-exchange-hub.md` §2 reads *"`fleet` `crew` staffing ratio for h, in [0, 1000]"*. `crew` exposes a bearer **count** (`Crew.LabourAt(world, sector, slot, faction)`), never a ratio: a ratio needs a crew target per hub, and that target is a hub number. `exchange` turns the count into its staffing term (for example through `depot`'s `LabourCurve` evaluator with its own points, or a per-tier crew target from its tier variant) and owns that key |
| A13 | `logistics-flow` `lane-loss` | **Round 4 P:** escort strength is the power roll-up (Hub output summed over the escort legion's stacks), replacing OD1's v1 stance count once the roll-up and its `ssot-power-scale.md` §10 contest row land. `escort-link` adds no strength read and publishes no row — the `escort` stance row is `lane-loss`'s (C21; re-worded by the 2026-09-20 audit, which found this cell still said "keeps publishing") |
| A14 | `trade-foundation` `ledger-keys`, `stock-deltas` | **Added by the 2026-09-20 audit.** Widen `FactKinds` (world scope) with `carry` (a holder-to-holder transfer: warehouse ↔ carried pool ↔ goods cache; `spec-ledger-keys.md` §4a already lists it as "used as if it existed … no ask filed") and `fade` (goods-cache decay, a sink distinct from lane loss). Widen `StockHolderKind` and the ledger holder grammar with one member for a goods cache (`Cache`, `c:<placeKind>:<placeId>`), so the global conservation net reaches caches on lanes. Carried goods' removal uses the existing `lost` kind |
| A15 | `world-continuity` `advance-carry` | **Added by the 2026-09-20 audit.** `AdvanceResolver` removes departing legions inside `Step` (`world-continuity/spec-advance-carry.md` §1) — a third removal site. (a) Call `CarriedGoods.OnEntityRemoved(…, departed)` in the same statement that drops the legion; (b) until the owner answers FQ3, refuse a `depart` for a legion carrying located goods (`depart.goods-aboard`). Also reconcile the `world_stock` cargo-kind ask that spec files on `scoped-inventory` (its §5) with fleet's hashed carried pool: two carriers for rubble and ironwork on one legion would be two capacity axes for one stock family (umbrella invariant 10) — FQ3 decides which |

## Contradictions found

| # | Where | What | Recommended resolution |
|---|---|---|---|
| C1 | trade-network ideal §5, §8.3 and legion-build ideal §4, §6.6 | Both ideals claim the `WorldEntityKind.Caravan` retirement | Resolved: `legion-build` owns it as `caravan-kind-retire`, and `legion-build-map.md` X15 says the same; this map adds no module |
| C2 | `gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs:20-47` (*"every member counts, not just Bearers"*) vs ideal §3.13 and `empire-economy-ssot.md` §6 (*"capacity scaling with every member is degenerate"*) | Two capacity rules for "what a legion carries" | Not a conflict to fix in `scoped-inventory` — items and goods are separate axes (ideal §3.12). `carried-goods` uses bearers only and never reads the item overlay's capacity; recorded so no spec "reuses" the item capacity for goods |
| C3 | trade-network ideal §11 row 3 (*"the construction chain"* in `logistics-flow`) vs row 4 (*"refine wiring"* in `fleet`) | The refine step is listed under two sub-programs | `logistics-flow`'s `construction-chain` owns it; this map carries none |
| C4 | legion-build ideal §4 (*"a stance beyond `march`/`scout`/`hold`"*) vs `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-22` | A fourth stance, `dowse`, already ships | Minor, ideal only — `legion-build-map.md` §5.9 already lists `dowse`; `escort` is the fifth |
| C5 | `trade-surface-map.md` gap table (*"The 'escort' throttle answer needs `fleet` first"*) vs legion-build ideal §6.4 | The escort stance is `legion-build`'s; `fleet` only uses it | Filed as A7 |
| C6 | legion-build ideal §6.3 and `legion-build-map.md` `standing-orders` (*"A stored per-legion `WorldCommand`, re-emitted each turn"*) vs trade-network ideal §8.3 (a caravan runs a load–march–unload–return loop automatically) | One re-emitted command cannot express a loop with phases | **Resolved by owner decision SO (2026-09-19):** kind-keyed orders with per-kind resolvers; `legion-build-map.md` owes the wording |
| C7 | `exchange-map.md` (filled goods travel through `logistics-flow`'s `transit-buffer`; `market` lanes *"join the route graph"*) vs trade-network ideal §8.3 and §2 (*"Foreign and cross-world routes are run by legions on a trade standing order"*) | Two carriers for a filled foreign order | **Resolved by owner decision Q1 (2026-09-19):** lane flow where an open path exists, a caravan only where it does not. `exchange-map.md` already matches; ideal §8.3's sentence owes the qualifier |
| C8 | This map's `goods-cargo-fate` (a legion *"that loses a battle"*) vs code | A legion also leaves the map by **starving** out of supply (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:134-151`), the only other in-`Step` removal site (every `Entities =` write read) | Both sites pass one `carried-goods` removal seam; `goods-cargo-fate` fills it (`spec-carried-goods.md` §5) |
| C9 | This map's `depot` (*"route range … extended by waystations the same way `LoamPolicy.WaystationRangeHops` already extends source range"*) vs `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:176-196` | `WaystationRangeHops` is a **founding** range for `build`, not a travel range; the only travel range is the loam leash | Range is the leash; beyond it a route is warned, never refused, for every faction (`spec-depot.md` §4); `depot.rangeCost` dropped |
| C10 | This map's `escort-link` **Built** line (*"battle requests gather every entity at the contact location"*) vs `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-55` and `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:44-54` | Requests are pairwise; the combatant list is exactly attacker and defender | Moved to real gap; ask A8 to `legion-build` |
| C11 | This map's `escort-link` (*"re-bound when the caravan's trade-route order restarts a loop"*) | The escort names the charge's entity id, which a loop never changes; there is nothing to re-bind | Dropped |
| C12 | This map's `trade-route-order` acceptance (*"… − lane loss"*) vs `logistics-flow-map.md` module 6 | Lane loss is defined on lane flow; carried goods are not lane flow | A caravan takes no lane loss; its risk is interception (`spec-trade-route-order.md` §7). Hazard bleeding caravans too would be a `lane-loss` change, not a fleet one |
| C13 | `trade-stories-map.md` `recover` template (*"claim the cache a lost caravan left (`claim-cache`, `WorldCommand.cs:119`)"*) vs `spec-goods-cargo-fate.md` | `claim-cache` is the item cache's Data-side command; goods caches are claimed by presence | Ask A10 |
| C14 | This map's plan path (`tasks/fleet-plan.md`) vs `trade-network-map.md` §6 (`tasks/trade-network-<sub-program>-plan.md`) | Two conventions | This map now uses the umbrella's |
| C15 | `spec-depot.md` §2 (*"… whose kind is Depot, or — once `exchange` lands — Exchange"*) vs round 4 B (*"Caravans: Caravan Yard … T1 legions load and unload goods"*) | An own trade hub was a load site | Removed: only a working caravan building is a load site; `trade-route-order` admission refuses a hub-only source or own destination (round 4) |
| C16 | `spec-crew.md` §3 (`LabourAt(world, siteSectorId, factionId)`) vs round 4 (caravan building, trade hub, Rift Anchor and Embassy are separate buildings that may share a sector) | One bearer would be labour for every building in its sector | The crew order and the read are keyed by the building's **slot** (`SiteSlotIndex`, `gk-core/src/FusionRpg.Core/World/WorldState.cs:98`) |
| C17 | `spec-depot.md` §3 / `rift-trade` `spec-crossing-anchor.md` §2 (the crossing takes a pro-rata share of the depot's one allowance) vs round 4 (the crossing end is its own **Rift Anchor** building) | The crossing no longer shares a depot | The depot's split covers caravan loads and unloads only; the anchor has its own crew and its own curve through the shared `LabourCurve` evaluator (`rift-trade` C9) |
| C18 | `spec-depot.md` §4 (*"a waystation's sector is a `LoamSource`, so it anchors supply"*) vs `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:44-48` | Supply is seeded by owned, uncontested sectors holding a `Seat` slot, not by a structure kind | Wording corrected; the effect (a waystation on a `Seat` shortens the out-of-supply stretch) stands |
| C19 | `spec-trade-route-order.md` §5 (settlement *"debits the carried pool"* at a foreign hub) and `spec-depot.md` §2 vs `exchange/spec-exchange-hub.md` §4 (a trader's goods at a hub are a **consignment**; fleet is one of its writers) | Two records for a third party's goods at a hub | Adopted `exchange`'s consignment; the caravan unloads into and loads from its owner's consignment, and gains the return leg the map already promised (`ReturnGoods`, `ReturnLoading`, `HomeUnloading`) |
| C20 | `spec-trade-route-order.md` Dependencies (*"`path-cache` (a point query — map ask A8)"*) vs this map | The point query is ask **A9**; A8 is the multi-entity battle side | Corrected |
| C22 | `spec-depot.md` §1 (a seventh `StructureKind` member, `Depot`) vs `trade-foundation/spec-sector-features.md` §1–§2 (`StructureDef.Feature` names the feature a building unlocks) | Two classifications of one fact | Withdrawn: the caravan building is `Feature == caravans`; tier from `SectorFeatures.TierOf` |
| C21 | `spec-escort-link.md` §3 and this map's tunables/A3 (fleet publishes `lane.stanceEscortMilli.escort`, or whichever of two changes lands second) vs `logistics-flow/spec-lane-loss.md` Tunables (*"This module owns the key family … `fleet` `escort-link` reads it and publishes nothing"*) | One tuning key claimed by two modules | `lane-loss` owns it; it lands with `escort-stance`; fleet's claim withdrawn |

## Owner questions

**One open: FQ3** (opened by the 2026-09-20 audit — goods on an advancing legion). Two opened by round 4
(FQ1, FQ2 — below). **Both answered 2026-09-20** ([decisions-round-4.md](decisions-round-4.md)
R5-A): **FQ1 → B3, option (b)** — the hub's owner also needs a Caravan Yard in that sector (so seeded clan
hubs get a yard); this reverses the recommendation below. **FQ2 → C1, option (a)** — provisioning top-up.
Q1 was decided at approval (above); the original framings are kept for the record:

| # | Question | Options | Recommendation (default until answered) |
|---|---|---|---|
| FQ1 | **Does a caravan unloading at a *foreign* hub need a caravan building in that sector?** Round 4 says caravans need a Caravan Yard to load and unload; it does not say whose. | (a) **No** — the foreign hub (Trading Post and up) is the foreign-facing building; the yard gates loading into and out of your own warehouse. (b) **Yes** — the hub's owner must also have built a yard there, or no caravan can deliver. (c) The visiting faction must own a yard somewhere in the hub's world | **(a).** It reads the rule as "the feature needs its building in the sector" with the trade feature unlocked by the hub; (b) would make every clan and rival need a yard before a caravan could reach it — a second gate on trade that the register does not name — and (c) is a building that does nothing where it stands. Reversible: one clause in `LoadSite` |
| FQ2 | **What is T2's "more range" mechanically?** The only travel range is the loam leash (C9). | (a) **Provisioning** — a caravan topping up at its own Convoy Depot fills to a tier multiple of its bearer capacity (`depot.provisionMilliByTier`). (b) **Supply reach** — a Convoy Depot seeds its owner's supply a few hops beyond held ground, for every legion. (c) A lower burn for caravans sourced at a T2 site | **(a).** It changes one input of the one range rule, scales with bearers (ideal §3.13) and touches only caravans that use the building. (b) is a second supply rule that also lengthens every army's reach — a military effect bought with a trade building. (c) breaks "burn by headcount" for one class of legion |
| FQ3 *(open — opened by the 2026-09-20 audit)* | **What happens to goods on a legion that advances to another world?** `world-continuity` `advance-carry` moves legions and their item cargo between worlds and strips loam; it does not know fleet's carried goods. Left alone, located goods would cross worlds with no loss, no throughput bound and no Grand Exchange — beside the priced crossing leg `rift-trade` exists to be (P5; `rift-trade` owner decision Q1: *"keeps advance the only way a legion changes worlds"*, for legions, not for trade goods). | (a) **Located goods may not ride an advance:** `depart` is refused while located goods are aboard (unload first); `rubble`/`ironwork` aboard **do** cross in the carried pool, which becomes the one carrier for world stocks on a legion (`advance-carry`'s `world_stock` cargo-kind ask is withdrawn). (b) **Everything aboard crosses, and pays the crossing hazard once** (`crossing-leg`'s `LaneLoss.Milli` with `crossing.hazardMilli`) on arrival. (c) **Everything aboard is stripped** at departure as a declared sink (`lost`), like loam | **(a).** It keeps one priced channel for trade goods between worlds (P5) and one carrier for world stocks on a legion (umbrella invariant 10), matches the PRINCIPLES rule *"rubble and ironwork cross worlds only as legion cargo"*, and costs the player one unload click with a named refusal. (b) makes advance an unbounded, Grand-Exchange-free crossing for any legion with bearers. (c) silently punishes a player who forgot to unload. Default until answered: refuse located goods at `depart` (ask A15) and strip anything still aboard (`spec-carried-goods.md` §5) — reversible, conservative, and conservation-safe |

| # | Question | Recommendation (**adopted 2026-09-19**) |
|---|---|---|
| Q1 | **Does every foreign trade need a caravan?** Ideal §8.3 and §2 say foreign routes are run by legions; ideal §7.7 says a `market` treaty makes the grantor's *"lanes join your route graph"*, and `exchange-map.md` has filled goods travel by lane flow. Both cannot be the only carrier. | **Lane flow when a path exists, a caravan when it does not.** A filled order's goods travel by `logistics-flow` whenever the buyer has an open path (own, unheld, or `passage`/`market` ground — ideal §7.6, §7.7); a caravan is needed where the path crosses closed ground (war, embargo, contested), out of a severed component, and across worlds. Reasons: §7.7's wording, the automation lesson (*"Automate the flow; the player sets policy"*, ideal §6 lesson 8), and fewer simulated entities (§9). It keeps caravans meaningful — they are how you trade *through* a war. Default if unanswered: this rule; it is reversible (a traversal predicate) |

Everything else is tied to a rule already stated: crew is a legion on an order
(owner ruling L3 — no separate modes; ideal §8.3 — no double upkeep); goods get their own capacity axis
(ideal §3.12); a destroyed caravan's goods follow `cargo-fate`'s rule with a hashed carrier (ideal §14b);
contested claims split pro rata (principle 10); `caravan-send` is not a second command if `legion-build`'s
order command carries a kind (SOLID, now decided — SO). The Caravan retirement's owner (`legion-build`)
matches both maps.

**Handed to another map, not open here:** whether anything physically crosses between worlds on a route is
`rift-trade`'s Q1 (decided there: no entity crosses). Since round 4 each world's end is a crewed **Rift
Anchor**, not a depot; fleet supplies the crew read and the `LabourCurve` evaluator, and a caravan serves an
anchor's sector only as an ordinary own destination with a caravan building in it.

---

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world legions and standing orders (legion-build), world turn engine (Logistics
    phase), battle (Sector/Lane requests only), economy (located goods, cargo fate), tunables,
    numeric range, match/actor lifecycle (attached uniques ride as members; no entity:{ptr} grant
    is involved on the world map).
[~] Session boundary: runs under tasks/sessions/trade-network-idea-20260919.json, whose paths
    include docs/architecture/trade-network/**; I did not run session-boundary-check.py myself.
[x] Read this session: the same §1 rows as logistics-flow-map.md's checklist, plus
    legion-build-ideal.md in full, scoped-inventory-hierarchy-map.md (modules and cargo-fate),
    battle-engine-ssot.md §4-§5. Honest gap: match-runtime.md and unique-actor-runtime.md were
    skimmed by heading; they govern lawn-bound specimens, and this map changes no specimen FSM.
[x] decisions.md checked: Scoped inventory hierarchy SSOT (items stay Data-side; goods here are
    hashed world state — a different class, no conflict), World turn phase order, Empire resource
    registry, Battle engine is the SSOT.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: see the session report; no HIGH finding left.
[x] Verified against code: Caravan's only readers; kinds hashed by name; lane/sector battles refused;
    raise founds fighters only; item cargo counts every member.
[x] Read surrounding sections: legion-build §6.3-§6.7 in full; cargo-fate's module text and its
    Data file header; DistrictAssaultResolver's refusal block and its T20 note.
[~] Constraints tested: none claimed. "Retirement is hash-neutral" is argued from WorldCanonical.cs:157
    (enums written by name) and must be proven by the goldens in legion-build's change.
[x] No §2 invariant contradicted: one battle engine, one legion architecture, one standing-order
    mechanism, determinism inside Step.
[x] Corrections propagated: none edited outside this file; C1-C5 name their owners.
[x] No population count pinned: throughput is asserted as an emergent identity, never a number;
    BattleKinds stays a closed vocabulary with nothing added.
[x] Event-refreshed cache: none introduced (carried goods and caches are state, not caches).
    The crew key-set edge (a depot becoming active) is tested order-independently.
[x] Orderings: crew assignment vs construction, contested cache claims — both orders tested.
[x] Actor magnitudes: none produced or consumed; escort and crew strength are Hub/engine outputs.
[x] No SOLID-violating parallel path: no new entity kind, battle kind, pricer, upkeep path, range
    rule or standing-order store.
[ ] Registry rows: the "every caravan is a Legion" and "no new BattleKinds" assertions need
    enforcement-registry rows when their tests land — each module spec names the row it owes.
[x] Spec round (2026-09-19): seven specs written against code; each ran audit-doc-citations.py
    --scope with no HIGH finding; corrections C8-C14 applied to this map.
```

---

## Reconciliation 2026-09-19 (round 4)

Against [decisions-round-4.md](decisions-round-4.md) (binding; it wins where this map disagreed). Docs only.

**Round-4 decisions applied**

| Register item | Where it landed |
|---|---|
| B — *Caravans: Caravan Yard → Convoy Depot; T1 legions load and unload goods; T2 more crew, more range* | `depot` is the caravan building — one row (today `convoy-depot`), two tier variants; the only own load site (C15); T2 "more crew" = `depot.throughputCurveByTier`, T2 "more range" = `depot.provisionMilliByTier` on the loam leash (FQ2); `spec-depot.md`, `spec-trade-route-order.md` |
| B — tiers are `variants` of one row, never a second row | A5 widened to `empire-seed`; no second building anywhere |
| B — buildings unlock features generally | every fleet gate reads `trade-foundation` `sector-features` (`TierOf(sector, caravans)`; A11, C22); crew keyed by building slot, since several buildings now share a sector (C16) |
| B — *Rift Anchor: a cross-world route end* | the crossing no longer shares a depot's allowance (C17); fleet supplies only the slot-keyed crew read and the `LabourCurve` evaluator |
| P — escort strength comes from the power roll-up | `spec-escort-link.md` §3; ask A13 to `lane-loss`; fleet adds no strength read |

**Contradictions fixed in this cluster:** C15 (hub as load site), C16 (sector-keyed labour double count),
C17 (crossing share), C18 (waystation supply wording vs `SupplyGraph.cs:44-48`), C19 (settlement debiting the
carried pool vs `exchange`'s consignment; the return leg added), C20 (ask-number typo), C21 (double claim on
`lane.stanceEscortMilli.escort`), C22 (a `StructureKind.Depot` member beside `sector-features`'
`StructureDef.Feature`).

**Asks received and answered here:** `exchange` (its reading of fleet A6 — consignments, hub labour): adopted
(C19), with the staffing-ratio mismatch returned as A12; `trade-ai` T-A2 (a trade legion identifiable from
state): `Crew.IsCrew`, `TradeRouteOrder.IsCaravan` (already in the specs); `rift-trade` A5: rewritten for
round 4 and answered (`Crew.LabourAt` by slot, `LabourCurve`); `trade-stories` T7 (`caravan.intercepted`,
`caravan.lost` in `FleetFacts`): matches `spec-interception.md`; `legion-build` S8 (kinds `trade-route`,
`crew`): matches.

**Cross-cluster conflicts (files this session does not own)**

| # | Conflict | Recommended resolution |
|---|---|---|
| X-F1 | `exchange` and `sector-yield` specs written before `trade-foundation` `sector-features` may still widen `StructureKind` (e.g. `StructureKind.Exchange`, `exchange-map.md` `exchange-hub`) for what is now `StructureDef.Feature` | Each gates on `SectorFeatures.TierOf` only (`spec-sector-features.md` Boundaries: *"gate a trade feature on `TierOf` only"*); a `StructureKind` member stays only where it names a non-feature engine behaviour |
| X-F2 | `exchange/spec-exchange-hub.md` §2 expects a staffing **ratio** from `crew` | `exchange` derives its own staffing term from the bearer count and owns that key (A12). *(Ruled 2026-09-20, X9: exactly this.)* |
| X-F3 | `logistics-flow/spec-lane-loss.md` OD1 still ends at "a Hub-composed power index" from `legion-build` | Restate as round-4 P: the container power roll-up (sum of Hub output), replacing the stance count once the `ssot-power-scale.md` §10 contest row lands (A13). *(Round 5 X7: the roll-up is `legion-build` `legion-power`; `lane-loss` §4 now cites it.)* |
| X-F4 | `empire-seed/spec-trade-structure-rows.md` §5.1 lists `Move` → `convoy-depot`, "no new row", with no tier variants | *(Ruled 2026-09-20, X12: `caravan-yard` is the row, `convoy-depot` its tier-2 variant; `empire-seed` already re-emits it so.)* |
| X-F5 | `legion-build/spec-standing-orders.md:7,27-28,60`, `spec-escort-stance.md:7`, `spec-field-battle-kinds.md:8`, `spec-caravan-kind-retire.md:7` cite `fleet-map.md` by **line number**; this reconciliation added lines above those targets, so the citations now drift | Re-cite by module or ask id (e.g. "fleet-map module 4", "ask A8"), which survive edits |

**Gap check**

- Every module row has a spec (7 of 7, *Module specs* table).
- Dependencies resolve to real module ids in `legion-build-map.md`, `logistics-flow-map.md`,
  `sector-yield/`, `exchange-map.md`, `trade-ai-map.md`, `trade-surface-map.md`, `trade-stories-map.md`,
  `empire-seed-map.md`, `scoped-inventory-hierarchy-map.md` and `trade-foundation`'s `sector-features`.
- Tuning keys: `fleet.goodsPerBearer`, `depot.throughputCurveByTier`, `depot.provisionMilliByTier`,
  `cache.fadePerTurnMilli` — each claimed once, by this map; `lane.stanceEscortMilli.escort` released to
  `lane-loss` (C21). No other trade-network, world-continuity, legion-build or empire-seed doc claims them
  (searched).
- Closed-vocabulary widenings: none of `StructureKind` (withdrawn, C22; the `caravans` member of
  `SectorFeature` is `sector-features`'); `FleetFacts` tokens (incl. new `depot.no-yard`);
  `TradeRouteState.Phase` + `ReturnLoading`, `HomeUnloading`; `trade-route` admission reasons
  `route.no-destination-yard`, `route.return-own`; `BattleKinds` unchanged.

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/fleet` —
see the session report; no HIGH finding.

## Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A, R5-X), which wins over any spec.
Citations touched were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| FR1 | **X12:** the caravan row id is `caravan-yard`; `convoy-depot` is its tier-2 variant (`empire-seed` re-emits today's identity-only `convoy-depot` row) | module 2; `spec-depot.md` |
| FR2 | **B3 (FQ1 → b):** a foreign hub is a caravan site only where the hub's owner has a working Caravan Yard in that sector; new `ForeignSite.Of` and token `depot.no-foreign-yard`; `counterparties` `clan-seeding` gives seeded clan hubs a yard | `spec-depot.md` §2; `spec-trade-route-order.md` (Unloading at a foreign hub) |
| FR3 | **C1 (FQ2 → a):** T2 "more range" is the provisioning top-up to a multiple of bearer capacity (`LegionSupply.Capacity` is bearers × carry, `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:20-21`); the top-up it changes is the Pressure-pass demand at `:193-195` (the old `:124-129` citation pointed at the burn loop) | `spec-depot.md` §4, Hard edges |
| FR4 | **X1:** every fleet gate reads `sector-features` — unchanged (C22), restated | `spec-depot.md` |
| FR5 | **X7:** escort strength's roll-up owner is `legion-build` `legion-power` | `spec-escort-link.md` §3; X-F3 |
| FR6 | **X9:** crew supplies a bearer count; `exchange` owns the staffing term — X-F2 ruled as recommended | X-F2 |
| FR7 | Wording fix found while re-verifying: an in-supply legion's top-up is **drawn from its supply component's loam stock** (`LegionSupply.cs:95-103`), not free | `spec-depot.md` anchors; module 2 |

**Closed vocabularies:** `FleetFacts` +`depot.no-foreign-yard`.

**Still other owners' files:** `counterparties` `clan-seeding` gives clan hubs a yard (done in this pass,
same session); `exchange` `exchange-hub` should treat a foreign caravan's consignment writes as gated by
`depot` `ForeignSite` (B3).

## Audit 2026-09-20

An independent audit of this map and its seven specs, against a fixed checklist, with each claim checked
in code on `features/mega-merge`. Docs only; nothing committed by the audit.

**Checklist used** (the same one for `fleet`, `rift-trade` and `counterparties`): (1) RPG layer only, one
ActorHub compose, one battle engine (a mode owns its loop, never a mechanism), no parallel path; (2) numbers —
`long`, `checked`, widen before multiply, divide last, no hard caps, every balance number a tunable with a
unit, one power ladder, §10 inventory, PS-5; (3) determinism and hashing — P13, P14, the per-world stamp;
(4) economy — P1, P2, P4/P6 and registry rows, P5, loam never traded, world stocks never auto-bank, no souls
out of trade; (5) tests — contract level, order-independent, edge-refreshed caches with their full trigger
set, store tests in memory, a named verification boundary; (6) boundaries — DAL, single writer, Funnel,
guards and `gk-core/scripts/enforcement-registry.v1.json` rows; (7) vocabulary — GG-23/GG-62, no IP names in new
prose; (8) spec quality — built / wiring gap / real gap, acceptance, test plan, hard edges, dependencies
that resolve, an honest §5 checklist.

### Findings

| # | Sev | Where | Finding | State |
|---|---|---|---|---|
| FA1 | HIGH | `carried-goods` §5; `goods-cargo-fate` §2 | A **third** in-`Step` removal site is specced but missing from the seam: `world-continuity` `advance-carry`'s `AdvanceResolver` removes departing legions in `Snapshot`. Unhandled, carried goods would vanish unrecorded or cross worlds with no loss and no gate — a second, lossless channel beside `rift-trade`'s priced crossing (P5) | **Fixed in fleet** (seam cause `departed`, source-scan test, default body); **needs** ask A15 (`world-continuity`) and owner question **FQ3** |
| FA2 | MED | `carried-goods` §5 | The removal sink recorded factKind `loss`, which is `lane-loss`'s kind; `trade-foundation` v1 already has `lost` for exactly this fact. Borrowing `loss` merges two sinks in the P6 sink-share line | Fixed (`lost`) |
| FA3 | MED | `goods-cargo-fate` §4 | Cache fade recorded `loss` too; it is a distinct sink | Fixed in fleet (`fade`); **needs** A14 |
| FA4 | MED | `goods-cargo-fate`; `carried-goods` §4 | A goods cache (on a lane) has no stock-delta or ledger holder kind (`StockHolderKind` is `Sector`/`Entity` + `Faction`), and `carry` is used without an ask (`spec-ledger-keys.md` §4a says so). The global conservation net cannot see caches | Fixed in fleet (named); **needs** A14 (`trade-foundation`) |
| FA5 | MED | `depot` Hard edges | T2 provisioning tops a caravan **past** `Capacity`, but `supply.restored` fires only when carried loam equals `Capacity` (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:117-120`); moving only the demand read would silently stop that report for provisioned caravans | Fixed (both reads take one provisioned target; test added) |
| FA6 | MED | `depot` Numeric types | The provisioning table was validated ≥ 1000 only; an upgrade could lower range | Fixed (monotone by tier) |
| FA7 | MED | `interception` Locked anchors | The battle-engine answer did not address register row 20 (*settlement — what is lost*) | Fixed (why this is the world's application of the engine's outcome, not a second owner) |
| FA8 | LOW | `interception` §1 | Rounding a spill's quantity up could leave an entry with `Qty 0` and positive load | Fixed |
| FA9 | LOW | `trade-route-order` §7 | The throughput identity subtracted lane loss the next sentence says a caravan never takes | Fixed |
| FA10 | LOW | `escort-link` §3; this map A13 | "keeps publishing the `escort` stance row" contradicted C21 | Fixed |
| FA11 | LOW | `crew` Tunables, Hard edges | Named the pre-round-4 key; said "no hard edges" while widening three closed vocabularies | Fixed |
| FA12 | LOW | `carried-goods` §7 | `TurnEngine.cs:114` for `RulesetVersion`; it is `:125` | Fixed |
| FA13 | LOW | every spec | Verification boundary: `gk-core/src/FusionRpg.Core/World/**` resolves only to `core-fallback`; only `carried-goods` named the gap | Fixed (named in module 1 and each spec's audit note) |
| FA14 | LOW | every spec's §5 checklist | "Registry row owed" with no row id | Fixed (ids named: `fleet-carried-goods-removal-seam`, `fleet-load-site-only`, `fleet-caravan-is-legion`, `fleet-no-battle-kind`, `fleet-cache-never-credits-wallet`). The rows land with their tests; none is written into the registry now, because a row naming a guard that does not exist fails the registry meta-test |

**Checked and clean** (no change needed): no actor magnitude is produced or consumed (escort strength is
`legion-build` `legion-power`'s Hub roll-up, read by `lane-loss`); no battle kind or mechanism is added;
every per-turn allowance is uncapped (diminishing curves, commented as structural rates); load units reuse
`lane-flow`'s one scale read, which carries the §10 row (`carried-goods` Tunables); determinism — every
hashed change is inside `Step`, and every split is pro rata with an ordinal remainder, never by faction id;
loam is never carried as goods and never traded; SQL stays in `FusionRpg.Data`; no IP name in new prose.

### Reported to other programs (their files; not edited)

| # | To | Finding | Recommended fix |
|---|---|---|---|
| FX1 | `trade-foundation` `sector-features` | `TierOf` reads no owner and `FactionTier` takes the max over owned **sectors**, but an assault hands a **slot** to the attacker without the sector (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161` writes slot owners only). A caravan building, Counting House or Rift Anchor whose slot an enemy holds would still count for the sector's owner | Decide the owner rule once in `sector-features`: a feature building counts for a faction only while that faction owns **both** its sector and its slot (a split building is inert, like one under construction). Every consumer inherits it; no program adds its own check (X1) |
| FX2 | `exchange` `exchange-hub` | A foreign caravan's consignment shares the host's one warehouse axis, so a visitor can fill a clan's or rival's warehouse and halt the host's own production (`sector-yield` `production-halt`) | Bound consignment inflow per visitor (for example, to the host's open buy orders for that good — the round-5 A4 shape), owned by `exchange` |
| FX3 | `world-continuity` `advance-carry` | See FA1 and ask A15; also its §5 `world_stock` cargo-kind ask would give rubble and ironwork a second carrier on a legion | Answer FQ3; route world stocks through the one carried pool |
| FX4 | `trade-foundation` `ledger-keys` | A14: `carry`, `fade`; holder `Cache` | Widen in the change that ships each emitter |

**Citation audit:** `python scripts/audit-doc-citations.py --scope docs/architecture/trade-network/fleet` and
`--scope docs/architecture/trade-network/fleet-map.md`, run after these edits — see the audit report; no HIGH
finding.

---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6". The family's single landing order is
[landing-order.md](landing-order.md); this sub-program is rows 12, 13 and 14 of its §2.

| # | Decision | What changed in the specs |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | One `trade.fleet` covered all three waves (`spec-carried-goods.md` §Dependencies, the audit's C1 table). Now: **W1** `trade.fleet` (`carried-goods` registers it, `depot` shares the bump); **W2** `trade.fleetRoutes` (`crew`, `trade-route-order`); **W3** `trade.fleetEscort` (`escort-link`, `interception`, `goods-cargo-fate`). Each wave takes one bump and no later wave widens an earlier flag |
| **C2** | One neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | `spec-depot.md` §1 is rewritten. Its old line — *"the row's `StructureKind` stays whatever `empire-seed`'s role mapping derives"* — derived `none`, and a row with no kind **cannot load** (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`; `:330`), so the Caravan Yard could never be placed, built or counted and every read in this spec returned tier 0 (audit C2). The row now loads as `Feature`, whose precedent is `Obstacle` (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`). This module still gates on no kind |
| **C3** | Banking waits on the save-identity re-key | No fleet module banks. `depot`'s load/unload and the route loop are unaffected; the only visible consequence is that goods a caravan unloads at a bank point wait there until `banking-fact`'s step half lands (`sector-yield/spec-banking-fact.md` §1a) |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | `spec-depot.md`: `LoadSite.Of`, `ForeignSite.Of` and the tier read in *Load-bearing rules* all move from `TierOf` to **`TierFor`** (`sector-features` §5a), and the B3 foreign-yard read is the hub **owner's** tier under the same rule. `spec-crew.md` §Dependencies: a crew at a building whose slot its faction does not hold supplies no labour and reports `crew.idle:not-owned`. No fleet spec writes an owner test of its own any more |
| **S2 / W1 / W2** | Trade goods cross worlds only by rift route; an advance is weight-limited; `world-transit` is a named future program | `spec-carried-goods.md` §5: **FQ3 and ask A15 are answered.** An advance is never the commerce channel; it carries what fits Σ(unit count × unit carry capacity) from `world.carry.capacity`, units and goods on one limit; the excess is refused at `depart` admission with `depart.goods-over-carry`; the `departed` seam stays the backstop that strips as `lost`. Import/export through the gate is `world-transit`'s. `spec-goods-cargo-fate.md` §2 re-points its FQ3 sentence to the same answer |
| **CQ2** | Legion equipment and doctrine upkeep may draw banked goods | No change here: a caravan moves goods and never spends them. The draw is `counterparties` `empire-goods-sinks`' (AI) or the wallet's (player), with the legion-build side filed as an ask |
| **D2** | Six `world.*` channels compose in `ActorHub`, read as Hub output | `spec-carried-goods.md` §3: `capacity` becomes the rolled-up **`world.carry.capacity`** — W1's Σ(unit count × unit carry capacity) is that roll-up's shape — with the **stated default** `bearers × Tuning.Fleet.GoodsPerBearer` until `world-derived` ships, so the switch changes the *source*, not the shape, and no test moves. `spec-depot.md` §4: the leash's capacity and burn inputs become **`world.march.range`** and **`world.supply.burn`**, default `LegionSupply.Capacity`/`Burn` (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`), keeping *one range rule* and *no second budget*. `spec-crew.md`: staffing is **not** one of the six — `LabourAt` stays a bearer count (X9) |
| **M1 (audit)** | Two fleet edges pointed up the build order | `spec-crew.md` §4 and §Dependencies: `crew` owns an `IWorkingSite` **predicate registry**; `exchange-hub` and `crossing-anchor` register their own predicates in their own waves, so the dependency (and the cycle with both) is gone. `spec-trade-route-order.md` §Dependencies drops `exchange` and `rift-trade` as *"later"* dependencies and states the exposure direction instead |

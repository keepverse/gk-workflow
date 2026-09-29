# Spec: `crossing-anchor`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19); **reconciled with the round-4 owner decisions 2026-09-19**
([../decisions-round-4.md](../decisions-round-4.md) B — see *Round 4* below); **round 5 applied 2026-09-20**
(B2 slot, X1 gate — see *Round 5* below). Module 2 of `rift-trade`,
wave 1. Every `file:line` below was opened this session. Docs only. **House style:**
[../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Round 4 (2026-09-19) — what changed

The register's building table says: **Cross-world → Rift Anchor** — *"A cross-world route end; needs a Grand
Exchange in the same world"*; and **Trade T4 (Grand Exchange)** unlocks *"cross-world routes"*. So:

- A world's end of a route is a **Rift Anchor**, its own structure (one tier), not a `fleet` depot. The
  first draft's *"no new structure role … an anchor is `fleet`'s depot"* is overturned by the register.
- An anchor works only while the player holds a working **Grand Exchange** (the trade building at tier 4,
  `exchange`'s) somewhere in the **same world**.
- The anchor's crew is its own (a crew order names the anchor's slot, `fleet/spec-crew.md` §1), and its
  labour-to-throughput points are its own key, `crossing.throughputCurve`, evaluated by `fleet`'s one
  `LabourCurve` evaluator. It no longer takes a pro-rata share of a depot's allowance.
- Unchanged: owner decision Q1 (nothing physically crosses; each end is crew-staffed), the rift-tear site
  bonus, the width level and the far-end view.

## Round 5 (2026-09-20) — what changed

- **B2 (decided; map RQ1 answered (a)):** a Rift Anchor stands on a **`Wildland`** slot, with a capacity
  bonus when its sector also has a rift-tear slot (`crossing.tearSiteBonusMilli`, §3) — exactly this spec's
  round-4 default, now binding. The tear stays free for a delve entrance.
- **X1:** both building checks read `trade-foundation` `sector-features` — the anchor by
  `SectorFeatures.TierFor(sector, owner, cross-world)` (round 6 S1), the Grand Exchange by the faction tier of the `trade`
  feature (`SectorFeatures.FactionTier(world, owner, trade) ≥ 4`, which `exchange`'s `Hubs.TradeTier` wraps
  and must delegate to). No `StructureKind` member.

## Objective

Give each world's end of a cross-world route a defined **capacity per End Turn** and a defined answer to
"is this end working right now?" — computed from that world's own state only — and give the other end a way
to read those answers without loading or stepping the world they belong to.

Success looks like: an anchor in world B that gains a crew legion raises B's end capacity at B's next
resolution; losing B's Grand Exchange stops B's end working at B's next resolution; world A's next End Turn
sees both through its logged route window; nothing in A's step ever opened B's graph.

## Scope and non-goals

**In scope:** the Rift Anchor as a route end (a `cross-world`-feature structure); the anchor predicate (a working own Rift Anchor in a world
where the player holds a working Grand Exchange); the end-capacity function (crew labour through its own
curve, the rift-tear site bonus, the crossing width level); the sparse hashed width-level field; the
**far-end view**, a Data-side projection of each anchor's inputs, and its complete refresh trigger set.

**Not in scope:** the Rift Anchor's identity row and magnitudes (`empire-seed` `trade-structure-rows`, ask
A13); the trade building and its tiers (`exchange` `exchange-hub`); which feature a structure unlocks and
its placed tier (`trade-foundation` `sector-features`); crew orders and the labour evaluator (`fleet` `crew`, `depot`);
the `widen` verb that raises the width level and its price (`crossing-leg`); the min-of-both-ends throughput
(`crossing-leg`); the scale read itself (`sector-yield` `essence-loop-read`); suspension semantics
(`endpoint-loss`); placing rift-tear slots in generated worlds (`world-map-program` `world-generator`, ask A6).

## Locked anchors

- **Round 4 B:** the cross-world feature exists in a sector only while a working Rift Anchor stands there,
  and only while its world holds a working Grand Exchange of the same owner.
- **Q1 (owner, 2026-09-19): each end is staffed by a crew legion; nothing crosses.** No new entity kind; the
  anchor's labour is `fleet`'s crew read, keyed by the anchor's slot.
- **Capacity must not scale with the thing that burns it** (trade ideal §3.13): crossing capacity comes from
  crew labour (bearers), never from total headcount.
- **One mechanism** (map rule 5): one labour read (`Crew.LabourAt`), one labour-to-output evaluator
  (`LabourCurve`), one feature-and-tier read (`trade-foundation` `sector-features`,
  `SectorFeatures.TierFor`). This module owns only its own point list.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| A `Tear` slot kind ("Rift Tear"), buildable | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:15`, `:71` |
| Two sector types may carry a rift-tear slot: `storm` and `warcamp`; both also allow `Wildland` | `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:79-89` |
| A build is refused on any slot whose kind differs from the structure's required kind | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89` |
| Structure kinds are a closed enum of six; a placed structure carries no tier | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-44`; `gk-core/src/FusionRpg.Core/World/WorldState.cs:96-126` |
| Sparse canonical rows: a zero-valued field writes no row, so adding one moves no hash | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128` |
| The rift-tear slot is also a delve domain entrance hint | `docs/architecture/party-dungeon/spec-domain-catalog.md:67` |

### Wiring gap

| Inert | Evidence | Owner |
|---|---|---|
| Neither shipped template places a rift-tear slot | no `tear` slot in `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs` or `WorldTemplateCatalog.TwoHearths.cs` (searched) | `world-map-program` `world-generator` (ask A6) |

### Real gap

The Rift Anchor row; the anchor predicate; the end-capacity function; the width-level field; the far-end
view and its triggers. Which feature a structure unlocks and its placed tier (needed to recognise a Rift
Anchor and a Grand Exchange) are `trade-foundation` `sector-features`' (`StructureDef.Feature`,
`WorldSlot.StructureTier`, `SectorFeatures.TierFor` — `../trade-foundation/spec-sector-features.md` §5a).

### Corrections to the map (propagated)

1. *(Spec time.)* The map's draft said *"a depot on a `Tear` slot gets a crossing bonus"*; the depot row
   requires `Wildland` and `BuildResolver` refuses any other slot kind (`BuildResolver.cs:82-89`). The bonus
   is a **site** bonus on the anchor's sector.
2. *(Round 4.)* The anchor is a Rift Anchor, not a depot, and needs a Grand Exchange in the same world
   (map C9).

## Design

### 1. The Rift Anchor — the `cross-world` feature, loaded as the neutral `Feature` kind

A Rift Anchor is a structure whose **`StructureDef.Feature == SectorFeature.CrossWorld`** (`sector-features`
§1–§2; the feature's maximum tier is 1). An earlier draft of this reconciliation added a `StructureKind.RiftAnchor`
member; with `sector-features` owning "which feature does this building unlock", a second classification
would be a second source for one fact, so **no per-building kind is added and nothing here gates on a kind**
(map C12).

**Round 6 C2 — the row still needs a kind to load, and it is the neutral one.** "No `StructureKind` member"
was read as *"the row ships `structureKind: none`"*, and a row with no kind **cannot load at all**:
`StructureDef.Kind` is a required enum with no "none" member
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`), a corpus row loads only with magnitudes
(`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`), and `TierOf` counts only slots whose
structure is known (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:330`). So no Rift Anchor could ever be
placed, built or counted, and §2's predicate would answer `anchor.no-anchor` forever (global audit C2). The
owner's answer: **one neutral `StructureKind.Feature`** for every feature building, `StructureKind.Exchange`
withdrawn, X1's wording amended to allow that one kind
([../decisions-round-4.md](../decisions-round-4.md) Round 6 C2). `Feature` does nothing in the loam or siege
economy — its behaviour is its `FeatureUnlock` — the `Obstacle` precedent
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`). The gate in §2 is unchanged: it reads the feature, never
the kind. One row, **no tier
variants** (the register gives the Rift Anchor a single tier), identity and magnitudes from `empire-seed`
(ask A13). Its required slot kind is **`Wildland`** (round 5 **B2**, owner decision; `empire-seed` authors
it on the row), which keeps the rift-tear slot free for a delve entrance and keeps the tear a preferred
site through the sector bonus (§3). Map owner question RQ1 is closed. `Wildland` is allowed in both sector
types that can carry a tear (`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:79-89`), so the bonus is
reachable wherever a tear exists.

### 2. Anchor predicate

`CrossingAnchor.IsWorking(world, sectorId)` — pure, over one `WorldState`:

- the sector is owned by the world's `Player`-kind faction (`FactionKindCatalog.cs:7-18`);
- `SectorFeatures.TierFor(sector, owner, SectorFeature.CrossWorld) ≥ 1` — an active Rift Anchor that
  **counts for the sector's owner**: round 6 S1 makes a feature building count for nobody until one faction
  owns both its sector and its slot, and `TierFor` applies that rule once, in `sector-features` §5a (one
  under first construction still reads 0, §5). An anchor on a slot a previous owner still holds leaves the
  crossing closed with `anchor.no-anchor` rather than working for whoever holds the ground;
- `exchange`'s `Hubs.TradeTier(world, faction) ≥ 4` — the owner holds a **Grand Exchange** (the trade
  ladder's tier 4) anywhere in this world. `exchange` owns that read (`../exchange/spec-exchange-hub.md` §7;
  its ask E-A18: *"`rift-trade` reads this function and adds no second check"*); `TradeTier` is the maximum
  hub tier over the sectors the faction owns — a thin wrapper that **must** delegate to
  `SectorFeatures.FactionTier(world, faction, trade)` (round 5 X1; `sector-features` §5). The threshold 4 is the ladder
  position the register names (a declaration, not a balance number).

It returns a reason from a closed set when false: `anchor.not-held`, `anchor.no-anchor`,
`anchor.anchor-building`, `anchor.no-grand-exchange`. (Pre-round-4 tokens `anchor.no-depot` and
`anchor.depot-building` are replaced.)

**This predicate is *registered*, not called from `fleet` (audit M1, edge 1).** `fleet` `crew` needs a
working-site predicate to decide `crew.idle`, and listing `crew` as depending on this module pointed **up**
the family build order and cycled with `spec-crew.md`. Instead `crew` owns an `IWorkingSite` predicate
registry keyed by the feature, and **this module registers `IsWorking` for `SectorFeature.CrossWorld` in its
own change** (`../fleet/spec-crew.md` §4; row 20 registering into row 13,
[../landing-order.md](../landing-order.md) §3). Until it does, an anchor slot is "not working" to `crew`,
which is the same answer `crew` already gives for a site that does not exist.

### 3. End capacity

```
labour      = Σ fleet Crew.LabourAt(world, sectorId, slot, playerFaction)            // crew bearers, over the sector's
                                                                                      // cross-world-feature slot(s)
base        = fleet LabourCurve.Eval(crossing.throughputCurve, labour)               // load units per End Turn
siteBonus   = hasTearSlot(sector) ? checked(base × crossing.tearSiteBonusMilli) / 1000 : 0
widen       = checked((long)sector.CrossingWidthLevel × crossing.widenStep)          // load units per End Turn
endCapacity = checked(base + siteBonus + widen)                                      // load units at THIS anchor's scale
```

**Units — one rule, the lane's (corrected by the 2026-09-20 audit).** The first draft computed `widen`
through `LaneFlow.ScaledCapacity(…, scaleRead)`. No such function exists: `lane-flow` defines lane capacity
as **flat load units**, `capacity(lane) = Width × lane.throughputPerWidth ÷ 1000`, and puts the scale inside
`loadOf(qty, sector, good) = ceil(qty × 1000 ÷ scaleMilli(sector, good))`
(`../logistics-flow/spec-lane-flow.md` §Design 1–2). Scaling the width term as well would have applied the
scale twice to one term and not at all to `base`, adding two different units. So every term of
`endCapacity` is flat load units, and a parcel is measured in **each end's own** load units: at the near end
by `loadOf(q, nearAnchorSector, good)`, at the far end by the same formula with the far view's `scale_milli`
(§5) — which is exactly why the view carries it. PS-5 holds through `loadOf`, whose scale read is the §10 row
`lane-flow` lands; this module adds no row.

There is **one labour-to-output evaluator** — `fleet`'s `LabourCurve`, monotone, diminishing and uncapped,
whose load-time validation this key inherits (`spec-depot.md` §3) — and this module owns only its **point
list**. The anchor's crew is its own: a crew order names the anchor's slot, so no bearer is labour for both a
caravan building and an anchor in the same sector. With no crew, `base = 0`; a width level alone still
carries (a built crossing needs no labour to exist, but labour is how it grows cheaply). `endCapacity` is in
load units; the goods' scale enters only through `loadOf` when a parcel is measured against it.

For the **far** end, a resolution of the near world uses the far anchor's published inputs (§5); the exact
arrival bound is enforced when the far world resolves the arrival (`crossing-handoff` Design 4).

### 4. The width level (hashed, sparse)

`WorldSector.CrossingWidthLevel : int`, default 0, written to canonical text only when non-zero (a new
`sector-crossing` conditional row beside `sector-rubble`, `WorldCanonical.cs:119-128`). No ceiling. Raised
only by `crossing-leg`'s widen resolution. Lost with the sector on capture: the captor inherits a widened
site, like any built structure.

### 5. The far-end view (Data projection) and its full trigger set

A world's step must know the **other** end's capacity and whether it is working, but must never load the other
world. So each world, at each of its own resolutions, publishes its anchors' **inputs** — not the computed
capacity — into `rpg_rift_anchor_view`:

`(save_id, empire_id, world_id, sector_id, anchor_slot, crew_bearers, tear_site, width_level, scale_milli,
grand_exchange, working, working_reason, world_outcome, as_of_counter)` — `scale_milli` is the anchor
sector's `essence-loop-read` value and `grand_exchange` whether the world holds a working Grand Exchange of
the anchor's owner — inputs like the others.

Capacity is computed at read time with the tuning loaded now, so a tuning publish never leaves a stale figure.
`rift-route` copies the row into the route window, so the value a step used is in that step's log.

This is an edge-refreshed projection, so DESIGN-GATE §2.16 applies. Every event that can change an input:

| # | Trigger | Changes | Key set moves? |
|---|---|---|---|
| T1 | A full `Step` of the anchor's world commits | any input, incl. `grand_exchange` (a hub captured, built, upgraded) | No |
| T2 | A `CoarseStep` record of the anchor's world is written | any input (fall, loss, background change) | No |
| T3 | An idle collect of the anchor's world is written | any input | No |
| T4 | A route is set naming this anchor | the row must exist | **Yes** |
| T5 | A Data-side move of a legion out of or into the anchor's world outside a step (`world-continuity` `advance-carry` departure/genesis, `world-warden` stationing) | `crew_bearers` | No |
| T6 | A tuning publish | nothing stored (inputs only) | No — not a trigger by construction |
| T7 | A route naming this anchor is cleared, or the anchor stops being a Rift Anchor | the row may become unread | **Yes (shrinks)** — the row is left in place; it is read only through a live route's window, so a stale unread row changes no outcome, and the next T4 recomputes it before any window copies it (added by the 2026-09-20 audit: the key-set shrink edge was unlisted) |

Inputs change **only** through T1–T5: a sleeping world's state does not move between its resolutions (lazy by
design); the world's outcome changes only inside T1 or T2 (`world-fall`); a structure — the anchor or the
Grand Exchange — is built, upgraded, captured or destroyed only inside a step (T1) or a coarse record (T2).
T4 computes the row from the anchor world's persisted state in the set transaction. T5 is filed as ask A9:
those modules call the same publish function in their own transaction.

The net for a forgotten trigger: in test mode, every window filing recomputes the far row from the far world's
persisted state and fails if they differ.

## Tunables (`data/tuning/trade.v1.json`, new, through `gk-core/tools/tuning/publish.py`)

| Key | Unit | Principle |
|---|---|---|
| `crossing.throughputCurve` | points `[labour (bearers), load units per End Turn]` | The anchor's own point list for the one `LabourCurve` evaluator (round 4: the anchor is its own building) |
| `crossing.tearSiteBonusMilli` | ‰ of `base` | A preferred site, never a requirement (the Market-slot precedent, trade ideal §7.1) |
| `crossing.widenStep` | load units per End Turn per width level | Owned here as a unit; the price curve is `crossing-leg`'s |

*(The map's draft key `crossing.throughputPerCrew` is dropped: a per-crew multiplier would be a second,
linear labour rule. The spec-time reuse of `fleet`'s `depot.throughputCurve` is replaced by
`crossing.throughputCurve` in round 4 — one point list per building, one evaluator.)* The Rift Anchor's build
cost, turns and upkeep are `empire-seed` bands.

## Numeric types

`crew_bearers`, `base`, `siteBonus`, `widen`, `endCapacity`: `long`, `checked`, widen before multiplying,
divide by 1000 last. `CrossingWidthLevel`: `int` (a level count; the capacity it buys is computed in `long`).
`crossing.tearSiteBonusMilli`: `int` ‰, not a bounded ratio (a bonus may exceed 1000); no clamp.
Tiers are `int` levels read from `sector-features`.

## Contract-level acceptance

1. `IsWorking` is false, with its named reason, for a sector not held, with no Rift Anchor, with an anchor
   under construction, or in a world where the owner holds no working Grand Exchange; true otherwise.
2. Capacity is a function of bearers on a crew order **naming the anchor's slot** only: adding fighters
   leaves it unchanged; adding a crew bearer never lowers it (monotone); a caravan building's crew in the
   same sector adds nothing to it.
3. The site bonus applies exactly when the anchor's sector contains a rift-tear slot, and is zero otherwise.
4. `CrossingWidthLevel` at zero leaves canonical text byte-identical to today's (sparse).
5. Save → load → hash round-trips with a non-zero width level.
6. One test per trigger T1–T5 asserts the view row equals a recomputation from persisted state after the
   trigger; T4 additionally asserts the row exists in the same transaction as the route; a T1 test captures
   the Grand Exchange and asserts `grand_exchange = false` and `working_reason = anchor.no-grand-exchange`.
   T7: after the only route naming an anchor is cleared and the anchor's world then changes, setting a new
   route recomputes the row before its first window copies it (the stale row is never copied).
7. **Order-independent:** assigning a crew before the anchor finishes and after it finishes give the same
   capacity on the first working turn; building the Grand Exchange before or after the anchor gives the same
   first working turn (both pairs tested — the key-set edges are the anchor becoming active and the world
   gaining its Grand Exchange).

## Test plan and verification boundary

| Test | Project |
|---|---|
| Predicate, capacity function, monotonicity, site bonus, no cross-building labour | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| Sparse canonical row, round trip | `gk-core/tests/FusionRpg.Core.Tests` (World canonical); `gk-core/tests/FusionRpg.Data.Tests` |
| View triggers T1–T5 and the cross-check | `gk-core/tests/FusionRpg.Data.Tests` (in memory) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
python gk-core/scripts/guard-dal.py
```

## Hard edges

- **Always:** read the crew and labour evaluator from `fleet` and the tier from the shared read; store
  inputs, compute capacity at read.
- **Ask first:** making the rift-tear slot a requirement (round 5 B2 decided `Wildland` + bonus); a stance or order other than `fleet`'s
  crew counting as labour; tiers on the Rift Anchor.
- **Never:** a second labour rule or evaluator; a stored computed capacity; a far-world load inside a step; a
  cap on the width level; an anchor that works without a Grand Exchange in its world.
- **Depends on** `trade-foundation` `sector-features` and `exchange`'s `TradeTier`; until they land no anchor
  works, which is correct — no structure can yet carry the `cross-world` feature or a trade tier of 4.

## Dependencies

| Consumes | From |
|---|---|
| `Crew.LabourAt` (slot-keyed); `LabourCurve.Eval` | `fleet` `crew`, `depot` (`spec-crew.md` §3, `spec-depot.md` §3; ask A5) |
| `SectorFeatures.TierFor(sector, owner, SectorFeature.CrossWorld)` and `FactionTier` (round 6 S1) | `trade-foundation` `sector-features` §5a |
| `Hubs.TradeTier(world, faction)` (the Grand Exchange test) | `exchange` `exchange-hub` §7 (E-A18) |
| Rift Anchor identity row and magnitudes | `empire-seed` `trade-structure-rows` (ask A13) |
| Save counter | `world-continuity` `hibernation-clock` |
| A **registration** into `advance-carry`'s post-move hook (audit M1, edge 6) | `world-continuity` `advance-carry` (ask A9) |

| Exposes | To |
|---|---|
| `IsWorking`, `EndCapacity` (load units at that anchor's scale), the far-end view row | `rift-route` (window payload), `crossing-leg`, `endpoint-loss` |
| `CrossingWidthLevel` field | `crossing-leg` (writer) |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/CrossingAnchor.cs   NEW — predicate, capacity (pure)
gk-core/src/FusionRpg.Core/World/WorldState.cs                      MODIFIED — WorldSector.CrossingWidthLevel
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                  MODIFIED — sparse sector-crossing row
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs                 MODIFIED — column + load/diff
src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs            MODIFIED — rpg_rift_anchor_view + publish
data/tuning/trade.v{n}.json                                 PUBLISHED — three keys
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world model (slots, sectors, canonical), structures (Rift Anchor, the trade building's tier),
    fleet crews, world store projection, tunables.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: the §1 rows listed in spec-rift-route.md, plus fleet-map.md in full,
    decisions-round-4.md in full, and party-dungeon spec-domain-catalog.md's entrance line.
[x] decisions.md: no lock on crossing anchors.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding (re-run after the round-4 rewrite).
[x] Verified against code: BuildResolver's slot-kind refusal; a slot carries no tier today; the active test.
    Read trade-foundation/spec-sector-features.md (the feature vocabulary and TierOf) this session.
[x] Read surrounding sections: BuildResolver's build loop; the canonical conditional rows; WorldSlot.
[x] Constraints tested: none claimed.
[x] No §2 invariant contradicted: no ceiling on the width level; capacity from bearers; one evaluator.
[x] Corrections propagated: the site-bonus correction and the round-4 anchor are written here and in the map
    (C5, C9).
[x] No population count pinned: the predicate reason set is a closed vocabulary; the Grand Exchange tier is
    the register's ladder position read through exchange's TradeTier (a declaration), not a population.
[x] Event-refreshed cache: the far-end view — full trigger set T1-T7 with the key-set edges T4 (grow) and
    T7 (shrink, added by the 2026-09-20 audit), one test each,
    the Grand Exchange edge inside T1, plus a recompute cross-check.
[x] Orderings: crew-before/after-anchor and hub-before/after-anchor tested.
[x] Actor magnitudes: none (a crew's labour is a bearer count, not a Hub number).
[x] No SOLID-violating parallel path: fleet's crew read and labour evaluator are reused; one tier read.
[ ] Registry row: the view cross-check is a test, not a guard; an invariants row lands with it
    (named by the 2026-09-20 audit: `rift-anchor-view-trigger-set`, unguardableReason pointing at the
    per-trigger tests and the recompute cross-check).
```

## Audit 2026-09-20

Fixed here: the capacity formula depended on a function `lane-flow` does not define
(`LaneFlow.ScaledCapacity`) and mixed a scaled term with flat load units — every term is now flat load
units, and each end measures a parcel with its own `loadOf` scale (the reason the view carries
`scale_milli`); the width product is widened before multiplying; the width step's unit is stated; the view's
trigger table gains the key-set **shrink** edge (T7). Reported (another program's file): an assault can hand a
Rift Anchor's **slot** to an enemy without the sector (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`),
and `sector-features` reads no slot owner — the owner rule belongs there (fleet-map FX1).
**Verification boundary:** `src/FusionRpg.Core/World/Logistics/Rift/**` resolves only to `core-fallback`
(`gk-core/scripts/verification-boundaries.v1.json`); the program's first implementing task adds a
`core-world-logistics-rift` owner boundary (paths `src/FusionRpg.Core/World/Logistics/Rift/**`,
`tests/FusionRpg.Core.Tests/World/Logistics/Rift/**`), the fleet precedent. The Data half stays on its
existing Data owner; view tests run in memory.

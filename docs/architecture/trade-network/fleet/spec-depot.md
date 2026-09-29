# Spec: `depot`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`); **reconciled with the round-4
owner decisions 2026-09-19** ([decisions-round-4.md](../decisions-round-4.md) B — see *Round 4* below);
**round 5 applied 2026-09-20** (B3, C1, X1, X12 — see *Round 5* below).
Every `file:line` below was opened in this session. Module id `depot`, row 2 of the
[fleet map](../fleet-map.md) (wave 1; depends on `carried-goods`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §8.3 (*"Depots (the `convoy-depot` row) are where
trade legions load and unload and where route range starts"*), §8.5.
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Round 4 (2026-09-19) — what changed

The owner's round-4 register (B, *Buildings unlock features*) makes the caravan feature a **building with
two tiers**: **Caravan Yard** (T1 — legions load and unload goods) → **Convoy Depot** (T2 — more crew, more
range). Tiers are `variants` of **one** structure row, never two rows or two buildings. This module is that
building: "the depot" below means *the caravan building at whatever tier it stands*. Consequences:

- The load site is **only** a working own caravan building (tier ≥ 1). An own trade hub is no longer a
  load site (the first draft said *"or — once `exchange` lands — Exchange"*); a sector with a hub and no
  yard takes lane-flow deliveries only.
- T2's *"more crew"* is a **per-tier throughput curve** (§3); T2's *"more range"* is a **per-tier
  provisioning term** on the loam leash (§4). Neither is a cap.
- A tier is read through **`trade-foundation` `sector-features`** — `SectorFeatures.TierFor(sector,
  factionId, SectorFeature.caravans)` over `WorldSlot.StructureTier` (round 6 S1;
  [../trade-foundation/spec-sector-features.md](../trade-foundation/spec-sector-features.md) §5a);
  this module never stores a tier of its own and gates on no `StructureKind` (C22). The row itself loads as
  the neutral `StructureKind.Feature` (round 6 C2, §1).

## Round 5 (2026-09-20) — what changed

- **X12 — the row id is `caravan-yard`**; `convoy-depot` is its **tier-2 variant** (display "Convoy
  Depot"). `empire-seed` re-emits today's identity-only `convoy-depot` row as `caravan-yard`
  (`../../empire-seed/spec-trade-structure-rows.md`, its `caravan-yard` row, *"replaces `convoy-depot`"*).
- **B3 — unloading at a foreign hub needs the hub owner's Caravan Yard in that sector.** Map owner
  question FQ1 is answered **(b)**, reversing this spec's round-4 default (§2). Seeded clan hubs get a yard
  (`counterparties` `clan-seeding`), so a clan hub stays reachable.
- **C1 — T2 "more range" is the provisioning top-up** (map FQ2 answered **(a)**, this spec's default): a
  caravan legion tops up loam at its Convoy Depot to a multiple of its bearer capacity (§4).
- **X1 — the tier is read only through `sector-features`** (unchanged; restated).

## Objective

Make the caravan building playable as the place goods get on and off a legion. This module owns four
things: the **load site** predicate (where a load or unload may happen this turn), the **site allowance**
(how many load units a site moves per turn, from its labour and its tier, and how that allowance is shared
by the legions using it), the **range assessment** a trade route gets at admission, and the **provisioning
term** a T2 site gives the caravans it serves. It owns no labour counting (`crew`), no route logic
(`trade-route-order`), no warehouse (`sector-yield`) and no tier storage (`sector-features`).

Success looks like: a working, crewed own Caravan Yard moves up to its allowance per turn and shares it
pro rata among the legions loading there; upgrading it to a Convoy Depot never lowers that allowance and
lengthens the leash of the caravans it sources; a yard under construction, captured, or unstaffed moves
nothing and says why; a route beyond a caravan's loam leash is admitted with a warning that names the
shortfall.

## Locked anchors

- **Buildings unlock features; tiers are variants of one row** (round-4 register B). The caravan feature
  exists in a sector only while a working caravan building stands there.
- **One structure pipeline.** The building is built — and upgraded to a higher tier — by the shipped
  `build` command through `BuildResolver` (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:96,148`); no
  depot-specific build path. An upgrade is a `build` of the same structure on its own slot
  (`sector-features` §4).
- **One structure corpus, owned by `empire-seed`** (ideal §14 D-E2). **The row is `caravan-yard`** (round 5
  X12), with `convoy-depot` as its tier-2 variant. Today the corpus holds only the identity-only
  `convoy-depot` row — no `magnitudes` block and an empty `variants` list
  (`gk-data/packs/fusion/data/seed/structures/move/convoy-depot.json`), so it is not catalog-loadable
  (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`); `empire-seed` re-emits it as
  `caravan-yard` with the Convoy Depot variant and their magnitudes from its bands (fleet-map ask A5,
  widened). This module never edits a seed row and never names a row id in code — it reads the caravans
  feature.
- **One upkeep path.** The building pays loam through `sector-yield` `structure-upkeep`'s role term in
  `LoamUpkeep` (principle 3); this module adds no charge.
- **One range rule.** A legion's range away from supply is its **loam leash** — capacity over burn
  (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-36`), the rule `empire-economy-ssot.md` §6 built
  bearers for. The depot is where that range starts because a legion in its faction's supply tops its
  `CarriedLoam` up toward `Capacity` from the supply pool's sector stock in the Pressure pass
  (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:95-103` draw, `:193-195` demand). This module adds **no
  second range budget**; T2's range is a term on the leash's capacity input, never a second budget.
- **Capacity must not scale with the thing that burns it** (ideal §3.13). The provisioning term multiplies
  **bearer** capacity only.
- **Every empire, same rule** (principle 10). No faction branch anywhere below.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Structure kinds are a closed enum of six | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-44` |
| A placed structure is a slot's `StructureId` plus `ConstructionTurnsRemaining`; a slot carries no tier | `gk-core/src/FusionRpg.Core/World/WorldState.cs:96-126` |
| *"A structure has no level of its own"* — hit points read the sector's development level | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:132-135` |
| An active structure is one with an id and no construction turns left | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:48-56` |
| The build pipeline, including a hop-range rule for founding on ground you do not hold | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:96,176-196` |
| The waystation row is a `LoamSource` on a `Seat`; its "range" is the founding range above, measured in hops from a habitable held sector (`LoamPolicy.WaystationRangeHops`) | `gk-data/packs/fusion/data/seed/structures/move/waystation.json`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs:147` |
| Supply is seeded from every owned, uncontested sector with a `Seat` slot and spreads through owned ground | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:19-48` |
| A legion in supply tops up (drawn from its supply component's stock) and never burns; out of supply it burns by headcount and starves at zero | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:64-120` (top-up), `:123-150` (burn) |
| Capacity is bearer capacity: bearers × `LoamPolicy.CarryPerBearer` | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:20-21` |
| Leash turns = capacity ÷ burn; turns until exhausted = carried ÷ burn | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:32-36,46-50` |
| Capture moves a sector's slots, and so its structures, to the captor | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:108-116` |

### Wiring gap

- The caravan row (today `convoy-depot`, to be re-emitted as `caravan-yard`, X12) has no magnitudes and no
  tier variants (above). Closed by `empire-seed` (ask A5).
  Until then tests use the structure catalog test bootstrap
  (`gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogTestBootstrap.cs`).

### Real gap (this module closes it)

The load-site predicate, the per-tier allowance and its sharing, the range assessment, the provisioning
term, and the depot fact tokens. **Not closed here:** which feature a structure unlocks, a placed
structure's tier and the upgrade — `trade-foundation` `sector-features` (`StructureDef.Feature`,
`WorldSlot.StructureTier`, `SectorFeatures.TierFor` — round 6 S1).

## Design

### 1. The caravan feature — a `Feature` kind, never a gate on a kind

The caravan building is recognised by **`StructureDef.Feature == SectorFeature.caravans`** (`sector-features`
§1–§2; the caravans feature's maximum tier is 2). The first draft widened `StructureKind`
(`StructureCatalog.cs:10-44`) with a `Depot` member; with `sector-features` owning "which feature does this
building unlock", a second classification would be a second source for one fact, so that widening is
withdrawn (C22). The building's warehouse capacity, if its band grants any, is `sector-yield`'s
`warehouse-axis` field, never a depot field.

**Round 6 C2 — the row's kind is `StructureKind.Feature`.** This spec used to say *"the row's
`StructureKind` stays whatever `empire-seed`'s role mapping derives"*, and what it derived was `none` — so
the Caravan Yard **could never load into the catalog at all** (`StructureDef.Kind` is a required enum with
no "none" member, `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`; `TierOf` counts only slots whose
structure is known, `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:330`), and every read below would have
returned tier 0 forever (global audit C2). The owner's answer is **one neutral `StructureKind.Feature`** for
all feature buildings, `StructureKind.Exchange` withdrawn, with X1's wording amended to allow that one kind
([../decisions-round-4.md](../decisions-round-4.md) Round 6 C2). `Feature` does nothing in the loam or siege
economy — its behaviour is its `FeatureUnlock` — the `Obstacle` precedent
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`). **This module still gates on no kind**; the kind only
makes the row loadable.

**Round 6 S1 — whose depot it is.** Its **tier** is
`SectorFeatures.TierFor(sector, factionId, SectorFeature.caravans)`, not `TierOf`: *"it counts for nobody
until one faction owns both"* its sector and its slot (Round 6 S1; the rule lives once, in
`../trade-foundation/spec-sector-features.md` §5a). So a Caravan Yard on a slot the previous owner still
holds is a load site for neither side — which also settles the B3 case cleanly: unloading at a foreign hub
needs *that hub owner's* yard, and a contested yard belongs to nobody.

### 2. Load site

```
LoadSite.Of(world, sectorId, factionId) -> Site?
  a sector is an own site for faction F this turn when
    SectorFeatures.TierFor(sector, F, SectorFeature.caravans) >= 1
        (round 6 S1: F owns the sector AND the slot; an active caravan building; one under first
         construction reads 0, sector-features §5 and §5a)
  Site = (SectorId, Tier)
```

- **An own trade hub is not a load site** (round 4: *"Caravans need a Caravan Yard building to load/unload
  goods"*). The first draft's *"or Exchange"* clause is removed.
- **A foreign hub** is not an own site. A caravan at a foreign working hub moves goods between its carried
  pool and **its own consignment there** — `exchange` `exchange-hub`'s record for a third party's goods at a
  hub (`exchange/spec-exchange-hub.md` §4) — bounded by the hub sector's warehouse room, not by a yard
  allowance (`trade-route-order` §Design 5). **Round 5 B3: the hub's owner must also have a Caravan Yard in
  that sector** — the foreign hub is a foreign site only while
  `SectorFeatures.TierFor(hubSector, hubOwner, SectorFeature.caravans) >= 1` — the hub **owner's** tier, read
  with round 6 S1's rule, so a yard on a slot the hub owner does not hold counts for nobody and the hub is
  not a foreign site that turn (`sector-features` §5a). Without one, the caravan cannot unload or load
  there and reports `depot.no-foreign-yard`. Seeded clan hubs are born with a yard (`counterparties`
  `clan-seeding`), so this gate never strands a clan. (Map FQ1, answered (b); round 4's default "no" is
  withdrawn.)

```
ForeignSite.Of(world, hubSectorId, visitorFactionId) -> Site?
  a sector is a foreign site for visitor V this turn when
    sector.OwnerFactionId is set and != V
    and the sector holds a working trade hub (exchange's HubTier >= 1, itself a sector-features read)
    and SectorFeatures.TierFor(sector, sector.OwnerFactionId, SectorFeature.caravans) >= 1
        (round 5 B3; round 6 S1 — the hub owner must hold the yard's slot too)
    and trade access allows V (exchange trade-access)
  Site = (SectorId, Tier)   -- the tier is the hub owner's yard; it sets nothing for the visitor
```

One predicate answers "may goods move to or from my warehouse here" for every fleet caller; nothing else
re-derives it.

### 3. Allowance and its sharing — one curve per tier

- A site's allowance for the turn is `Allowance = LabourCurve.Eval(depot.throughputCurveByTier[tier], labour)`
  **load units** — `lane-flow`'s unit, in which the scale already lives (`loadOf`,
  `docs/architecture/trade-network/logistics-flow/spec-lane-flow.md` §Design 1) — where `labour` is `crew`'s
  read summed over the sector's caravans-feature slots (`Σ Crew.LabourAt(world, sectorId, slot, factionId)`).
  Like a lane's
  capacity, it is flat in load units (PS-5 holds because every parcel is measured by `loadOf`).
- `LabourCurve.Eval` is a piecewise-linear curve through authored points `[labour, units]`; past the last
  point it continues at the last segment's slope. Load-time validation refuses a curve whose segment slopes
  are not positive and non-increasing. So throughput is **monotone, diminishing and uncapped** (P9; PS-8 —
  no point past which another bearer adds nothing). Labour 0 gives 0: an unstaffed site moves nothing and
  reports `depot.unstaffed`. `LabourCurve` is the **one** labour-to-output evaluator; every building that
  turns crew into output (this module; `rift-trade` `crossing-anchor`) calls it with its own points, so there
  is one evaluator and one owner per point list.
- **Tiers.** `depot.throughputCurveByTier` holds one point list per tier of the caravan building (T1, T2).
  Load-time validation also refuses a higher tier whose curve is below a lower tier's at any labour, so an
  upgrade never lowers throughput. *"More crew"* (T2) is the T2 curve's later knee — more bearers stay
  useful before returns diminish — never a crew limit. A tier the table does not name is a load rejection.
- Loads and unloads at one site in one turn share one allowance. Demands are collected, then split
  **pro rata by requested units** — `share_i = checked((long)allowance × request_i) / Σ request`, widened
  before the multiply and divided once — remainder by entity id (ordinal) — principle 10's rule for contested
  capacity, never by faction id. (Only the owner's legions use an own site, so the split is within one
  faction; the rule is still stated so a later shared site inherits it.) A crossing no longer takes a share
  here: the round-4 Rift Anchor is its own building with its own crew (`rift-trade` `crossing-anchor`).
- The allowance is a **per-turn structural rate**, commented as such in code (PS-8 exemption).

### 4. Range assessment — the loam leash, with a T2 provisioning term

The map's first draft said route range is *"a path-cost budget from the depot, extended by waystations
the same way `LoamPolicy.WaystationRangeHops` already extends source range"*. Read in code,
`WaystationRangeHops` is a **founding** rule — how far from a habitable held sector a `build` may land
(`BuildResolver.cs:176-196`) — not a travel range. The only travel range the world has is the loam leash.
A second budget would be a second range rule for the same question.

**Round 6 D2 — range and provisioning read Hub-composed world channels.** D2 creates six world derived
channels plus their own program, `world-derived` (idea round later); two are this section's:
**`world.march.range`** and **`world.supply.burn`** (lower is better). They *"compose in `ActorHub` like
every other channel and roll up per stack and legion the way `legion-power` does"*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 D2). The rules:

- **Read Hub output, never a private formula.** When the channels exist, the leash's capacity input reads the
  rolled-up `world.march.range` and its burn input the rolled-up `world.supply.burn` — one read per legion,
  no depot-local fold of species, equipment, standard, doctrine or tradition contributions.
- **Stated default until `world-derived` ships:** exactly the formula below —
  `LegionSupply.Capacity(entity)` for capacity and `LegionSupply.Burn(entity)` for burn
  (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-25`), with the per-tier `provisionMilliByTier` term as
  the depot's own contribution. The switch replaces the two *inputs*, keeps the leash arithmetic, and so
  keeps *"one range rule"* and *"no second range budget"* intact.
- **No spec here implements `world-derived`**, and the T2 term stays a depot tunable either way: it is a
  building's effect, not a unit's channel.

```
Provision.MilliFor(world, entity) -> int
  = depot.provisionMilliByTier[tier of the source site of entity's trade-route order]   when that site is
    a working own site and the legion stands in it
  = 1000 otherwise                                                                     (no term)

DepotRange.Assess(world, entity, path) -> Assessment
  outOfSupplyTurns = turns of the planned round trip spent outside the faction's supply
                     (march budget per turn from MovementPolicy.BudgetFor, lane cost from LaneCost)
  leash            = floor(LegionSupply.Capacity(entity) × Provision.MilliFor ÷ 1000 ÷ LegionSupply.Burn(entity))
  result           = WithinLeash | BeyondLeash(outOfSupplyTurns - leash)
```

- **T2's *"more range"*** is the provisioning top-up (**round 5 C1, decided**: *"a caravan legion tops up
  loam at its Convoy Depot to a multiple of its bearer capacity"*): a caravan topping up at its own Convoy
  Depot fills its `CarriedLoam` to `Capacity × provisionMilli ÷ 1000` instead of `Capacity`, where
  `Capacity` is bearer capacity (`LegionSupply.cs:20-21`). T1's row is 1000 (no term). The term multiplies
  **bearer** capacity (ideal §3.13 holds) and is read by the one top-up demand in the Pressure pass
  (`LegionSupply.cs:193-195`) through `Provision.MilliFor` — a change to that shared pass, named in
  *Hard edges*. (Map FQ2, answered (a).)
- `trade-route-order` calls `Assess` at admission. `BeyondLeash` is **admitted with a report warning**
  (`depot.beyond-leash:<turns>`), for every faction alike: the engine never refuses a march for loam — the
  player's suicide march is a real play (`empire-economy-ssot.md` §6) — and the AI's harder gate belongs to
  the AI's policy (`trade-ai` `ai-logistics`), which simply does not file such a route. That keeps one
  admission for every commander (principle 10).
- **Waystations** shorten the out-of-supply stretch because a waystation sits on a `Seat` slot, and every
  owned, uncontested `Seat` sector seeds its owner's supply (`SupplyGraph.cs:44-48`). *(Corrected
  2026-09-19: the first draft said the waystation anchors supply because it is a `LoamSource`; the code
  seeds supply from the `Seat` slot, not from the structure kind.)*

### 5. Capture and loss

A depot sector changing hands stops being the old owner's site in the same turn (the predicate reads
ownership); the building, at its tier, passes to the captor with the sector's slots
(`ClaimResolver.cs:108-116`); its warehouse goes with the sector (`sector-yield` rule). The consequence for
routes that start or end there is `trade-route-order`'s (§Design 6). A building under first construction
serves nothing; one under an upgrade keeps serving at its current tier (`sector-features` §4–§5).

### 6. Fact tokens

Added to `FleetFacts` (`carried-goods` §8): `depot.unstaffed`, `depot.inactive`, `depot.beyond-leash`,
`depot.no-yard` (a caravan asked to load or unload in an own sector with no working caravan building),
`depot.no-foreign-yard` (round 5 B3: a foreign hub whose owner has no working Caravan Yard in that sector).

## Tunables

| Key | Unit | Home |
|---|---|---|
| `depot.throughputCurveByTier` | per tier: points `[labour (bearers), load units per turn]` | `data/tuning/trade.v1.json` (new) |
| `depot.provisionMilliByTier` | per tier: ‰ of bearer loam capacity at top-up; T1 = 1000 | `data/tuning/trade.v1.json` (new) |
| Build cost, build turns, upgrade cost, upkeep role term, warehouse band — per tier variant | structure bands | `empire-seed`'s band table; `sector-yield` `upkeep.structureTermByRole` |

The map's `depot.rangeCost` and `depot.throughputPerCrew` are dropped: range is the leash (§4), and one
curve per tier replaces a flat per-crew rate (§3). `crew` owns no throughput number (see `spec-crew.md`).
The pre-round-4 key `depot.throughputCurve` is replaced by `depot.throughputCurveByTier`; `rift-trade` no
longer reads it (its anchor has its own `crossing.throughputCurve`).

## Numeric types

Allowance and curve values are `long`, `checked`. The curve interpolation multiplies before dividing and
throws on overflow. `provisionMilli` is an `int` ‰ multiplier ≥ 1000 (validated), applied to a `long`
capacity, divided by 1000 last. Load-time validation also refuses a provisioning table that is not
monotone by tier (`provisionMilliByTier[T2] ≥ provisionMilliByTier[T1] = 1000`), the same "an upgrade
never lowers" rule the throughput curves carry (audit 2026-09-20: the first draft validated only ≥ 1000).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet|FullyQualifiedName~StructureCatalog"
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Structure

```
src/FusionRpg.Core/World/Logistics/Fleet/Depot.cs         (new) — LoadSite, allowance, pro-rata share
src/FusionRpg.Core/World/Logistics/Fleet/LabourCurve.cs   (new) — the one labour-to-output evaluator
src/FusionRpg.Core/World/Logistics/Fleet/DepotRange.cs    (new) — leash assessment, Provision.MilliFor
gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs             MODIFIED — top-up reads Provision.MilliFor (Hard edges)
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs    MODIFIED — depot tokens
src/FusionRpg.Core/World/Logistics/Fleet/FleetTuning.cs   MODIFIED — per-tier curves, provisioning + validators
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/DepotTests.cs (new)
```

## Testing strategy

- **Site predicate:** own + active caravans-feature building → site with its tier; under construction, unowned, foreign, a
  structure of another feature, or an own sector holding only a trade hub → not a site; each returns its
  reason token.
- **Foreign site (B3):** a foreign hub sector whose owner has a working yard → a foreign site; the same hub
  without a yard → `depot.no-foreign-yard`; a yard under first construction → not a site; the result is
  identical whatever the hub owner's faction kind.
- **Curve:** validation refuses a flat, rising-slope or negative segment, and a T2 curve below T1's at any
  labour; monotone (adding labour never lowers throughput) and diminishing (each added bearer adds ≤ the
  previous) over a property sweep; past the last point it keeps rising.
- **Upgrade never lowers:** the same labour at T2 moves ≥ what it moved at T1, over a property sweep.
- **Sharing:** two legions requesting `r1`, `r2` load units against allowance `a < r1 + r2` receive `a × r1/(r1+r2)`
  and the rest, remainder to the lower entity id; renaming the legions' factions changes nothing.
- **Leash:** a fixture route entirely in supply is `WithinLeash`; one with an out-of-supply stretch longer
  than the leash is `BeyondLeash(n)` with the exact shortfall; building a waystation on a `Seat` slot that
  brings the stretch into supply turns it `WithinLeash`; the same route sourced at a T2 site has a leash
  of `floor(capacity × provisionMilli ÷ 1000 ÷ burn)`.
- **Provisioning is bearer-only:** adding fighters to a caravan at a T2 site never raises its provisioned
  capacity.
- **`supply.restored` still fires for a provisioned caravan:** a caravan at a T2 site that tops up to its
  provisioned target reports `supply.restored` exactly once, and a T1-sourced legion's report is
  byte-identical to today's (the shared-pass hard edge).
- **Provisioning table:** a T2 row below T1, or a T1 row other than 1000, is a load rejection naming the key.
- **Upkeep once:** total loam upkeep with a depot minus without equals exactly the role term (no second
  charge from this module).

## Boundaries

- **Always:** one site predicate; allowance from labour, tier and the scale read; pro rata sharing; one
  labour evaluator.
- **Ask first:** a second range rule; a depot-specific build or upgrade path; a depot field for warehouse
  capacity; a crew limit per tier.
- **Never:** refuse a route for loam inside the engine; hand-edit `convoy-depot.json` (or its `caravan-yard` successor); a flat throughput
  cap; a tier stored on the depot instead of `sector-features`; a `StructureKind` member for the caravan
  building.

## Success criteria (contract)

1. Goods move to or from an own warehouse only at a working own caravan building, and to or from a foreign
   hub's consignment only where the hub's owner has a working Caravan Yard in that sector (B3); every
   refusal names its reason.
2. Allowance rises with labour on a diminishing, uncapped curve per tier, never lower at a higher tier, and
   is shared pro rata.
3. Range is the loam leash (with the T2 provisioning term); beyond it a route is admitted with a named
   shortfall, for every faction.
4. The building's upkeep appears once, through the structure term.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `LoadSite.Of` | `trade-route-order`, `crew` (is my site working?) |
| `ForeignSite.Of` (round 5 B3) | `trade-route-order` (`Unloading` / `ReturnLoading` at a foreign hub) |
| `Depot.Allowance`, `Depot.Share` | `trade-route-order`'s Logistics step |
| `LabourCurve.Eval` | `rift-trade` `crossing-anchor` (with its own points) |
| `DepotRange.Assess`, `Provision.MilliFor` | `trade-route-order` admission; `trade-ai` (to avoid filing beyond-leash routes); the Pressure top-up |

## Dependencies

`carried-goods`; `crew` supplies labour (until it lands, labour is 0 and every depot is unstaffed — which
is correct, since nothing loads goods before `trade-route-order` either); `trade-foundation`
`sector-features`; `sector-yield` `essence-loop-read`, `structure-upkeep`, `warehouse-axis`; `empire-seed` tier
variants and magnitudes (ask A5).

## Hard edges

- New tuning keys in a new file (`trade.v1.json` is proposed by the umbrella; `gk-core/tools/tuning/publish.py`
  may need the domain added).
- **The provisioning term touches the shared legion top-up** (`LegionSupply.cs:193-195`, the demand toward
  `Capacity`). It is the one
  top-up for every legion; the term is 1000 for every legion not sourced at a T2 site, so an existing
  world's arithmetic is unchanged (asserted), but the change is a reviewed edit to loam-legions code.
  **Two readers of "full" in the same pass must move together (audit 2026-09-20).** `supply.restored` fires
  only when `carriedById[e] == Capacity(entity)` (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:117-120`),
  and `RationedDemand` computes the deficit as `Capacity(entity) − carried` (`:193-196`). A provisioned
  caravan tops up **past** `Capacity`, so if only the demand read took the term, `supply.restored` would never
  fire for it again (its carried loam never equals `Capacity`). Both reads take the one target
  `ProvisionedCapacity = Capacity × Provision.MilliFor ÷ 1000`; `LeashTurns` (`:32-36`) stays the unprovisioned
  full-tank figure the leash UI already explains. A provisioned legion that walks back into ordinary supply
  keeps its surplus (`RationedDemand` floors at 0, `:195`) and burns it down only outside supply — stated so no
  reader "fixes" it into a drain.
- **Depends on `sector-features`.** Until it lands no structure carries the caravans feature, so no load
  site exists — which is correct, since nothing loads goods before `trade-route-order` either.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: structures and the corpus, world turn engine (Logistics), loam supply, tunables.
[~] Session boundary: trade-network-idea-20260919 record covers this path; check script not run by me.
[x] Read this session: as spec-carried-goods.md, plus BuildResolver, LegionSupply, LoamPolicy, SupplyGraph,
    ClaimResolver and the two structure seed rows in code; decisions-round-4.md in full (round 4).
[x] decisions.md: Empire resource registry (no new quantity), phase-order row (no new phase).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding (re-run after the round-4 edit).
[x] Verified against code: waystation range is a founding rule; supply seeds from Seat slots (corrected);
    convoy-depot has no magnitudes or variants; a slot has no tier; active test; supply top-up.
[x] Surrounding sections read: BuildResolver's G5 comment; LegionSupply's Pressure-pass comment;
    SupplyGraph.ConnectedSectors; empire-economy-ssot §6 in full.
[~] Constraints tested: none claimed.
[x] No §2 invariant contradicted: uncapped per-tier curves (structural per-turn rate commented), no second
    range or upkeep rule, provisioning scales with bearers only.
[x] Corrections propagated: the range correction, the curve ownership, the round-4 tiers and the Seat
    correction are recorded in fleet-map.md (C9, C15-C18, tunables) in the same change.
[x] No population pinned; no closed vocabulary widened here (the caravans feature is sector-features').
[x] No event-refreshed cache.
[x] Orderings: sharing is independent of request order (tested by permuting).
[x] No actor magnitude.
[x] No SOLID fork: one build path, one upkeep term, one range rule, one site predicate, one labour evaluator.
[ ] Registry row: "goods move only at a load site" — guard or unguardableReason owed with its test.
    Named (audit 2026-09-20): invariant id `fleet-load-site-only`, covered by the site-predicate tests.
```

## Audit 2026-09-20

Fixed here: the shared Pressure pass has **two** readers of a legion's full tank (`supply.restored` and the
top-up demand); both now take the provisioned target (Hard edges, one new test); the provisioning table is
validated monotone by tier; the pro-rata split's arithmetic is spelled out (widen, divide once). Reported,
not fixed here (another program's file): `trade-foundation` `sector-features` reads no slot owner, while an
assault can hand a **slot** to the attacker without the sector (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`
writes `OwnerFactionId` on slots only). `LoadSite.Of` reads the sector owner, so a caravan building whose slot
an enemy holds would still serve the sector's owner. The owner rule for a feature building whose slot and
sector owners differ belongs to `sector-features` (fleet-map *Audit 2026-09-20*, owner question for
`trade-foundation`); this module adds no second check (round 5 X1).
**Verification boundary:** `src/FusionRpg.Core/World/Logistics/Fleet/**` resolves today only to the
`core-fallback` owner (`gk-core/scripts/verification-boundaries.v1.json`, no `verificationId`); the
`core-world-logistics-fleet` owner boundary that `spec-carried-goods.md` Hard edges adds covers this module.

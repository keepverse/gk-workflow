# Spec: `crew`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`); **reconciled with the round-4
owner decisions 2026-09-19** ([decisions-round-4.md](../decisions-round-4.md) B: the caravan building has
tiers, and the crossing end is its own Rift Anchor building). Every `file:line` below was opened
in this session. Module id `crew`, row 3 of the [fleet map](../fleet-map.md) (wave 2; depends on `depot`
and `legion-build` `standing-orders`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §8.3
(*"Crews are units. Hubs and depots need assigned bearers to run — labour is both a production input and
an upkeep line (P11), and it gives the never-produced Bearer role a job"*);
[legion-build-ideal.md](../../legion-build-ideal.md) §6.5 (*"Crews for depots and hubs are bearers
assigned from legions"*). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Give depots and trade hubs their labour. A **crew** is an ordinary legion holding a **crew standing
order** for a building's sector and standing in it; the building's labour is the bearer count of such
legions. This module owns the `crew` order kind (registered through `legion-build`'s standing-order
kind registry), its resolver, and the one **labour read** every building consumer calls. It owns no
throughput number: a caravan building turns labour into an allowance (`spec-depot.md` §3); a hub turns it
into clearing capacity (`exchange` `exchange-hub`); a Rift Anchor into crossing throughput (`rift-trade`
`crossing-anchor`).

**A crew staffs one building, not a sector** (corrected 2026-09-19, round 4). Round 4 makes the caravan
building, the trade hub, the Rift Anchor and the Embassy separate buildings that can stand in one sector.
A sector-keyed labour read would count the same bearers once for **each** of them — the double charge ideal
§8.3 forbids (*"upkeep, without double charging"*) turned into a double benefit. So the order names the
building's **slot** and the read is keyed by it.

Success looks like: three bearers of a legion on a crew order standing at a working caravan building give
that building labour 3; a fighter in the same legion adds nothing; the same legion off its order, or one
sector away, adds nothing; a trade hub in the same sector gets none of that labour; the legion burns and
pays exactly what it would with no order.

## Locked anchors

- **A crew is a legion on an order, not a new holder of units** (owner ruling L3, legion-build ideal §8;
  load-bearing rule 1 of the map). No crew table, no member transfer, no new entity kind.
- **Standing orders carry a kind; each kind has its own resolver** (owner decision 2026-09-19, recorded
  in the map). `crew` is one kind. `legion-build` `standing-orders` owns storage, the set/clear command,
  explicit-order precedence and the emitter; this module supplies the kind's payload shape and resolver.
- **Upkeep without double charging** (ideal §8.3). The crew legion pays what every legion pays and nothing
  more: a legion in supply never burns (`gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:124-129`), and an
  own working building's sector is ordinarily in supply.
- **Labour is presence, counted per turn, never stored** — so there is no cache to go stale (DESIGN-GATE
  §2.16 does not apply) and nothing new is hashed except the order itself, which `legion-build` hashes.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Member roles `Fighter`, `Bearer`; a member row has no count yet | `gk-core/src/FusionRpg.Core/World/WorldState.cs:269-283` |
| Bearer count helper | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:16-17` |
| A legion is at a sector or on a lane, never both | `gk-core/src/FusionRpg.Core/World/WorldState.cs:292-295` |
| A slot is identified within its sector by `SlotIndex` and carries at most one `StructureId` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:96-119` |
| A routed legion loses one turn of orders; the flag clears at the top of that turn | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:165-178,229-235`; flag `gk-core/src/FusionRpg.Core/World/WorldState.cs:318` |
| One command shape for every commander; the AI builds one per legion | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:137-217`; `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:568-584` |

### Wiring gap

- Bearers are never produced by raising (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:124-142`) —
  `legion-build` `raise-choice`. Until then crews are fixture legions.
- `Σ Count` — `legion-build` `member-stack`; before it, a bearer row counts one.

### Real gap (this module closes it)

The `crew` order kind, its resolver, the labour read, the crew fact tokens.

## Design

### 1. The `crew` order kind

Payload: `SiteSectorId` and `SiteSlotIndex` (the building's sector and the slot it stands on). Validation
when the order is set (called by `legion-build`'s set command): the legion belongs to the commander; the
sector and slot exist; the legion has at least one bearer (else refused `crew.no-bearers` — a crew of
fighters has no labour to give). The site need **not** be working when the order is set: assigning a crew
to a building still under construction is the normal way to staff it on its first working turn (see §4).

### 2. Resolver (called by `legion-build`'s emitter, before `Step`)

```
Crew.NextCommand(view, entity, order) -> WorldCommand?
  if entity stands at order.SiteSectorId      -> null   (stay; no command, no stance change)
  else                                        -> move along the shared believed-view path to the site
```

The path comes from the one believed-view planner (`trade-route-order` §Design 3 lifts it out of
`FrontierRulesPolicy.cs:525-566`); this module adds no path finder. Emitting nothing to stay put, rather
than a `hold` stance, keeps a crew free to use any stance and avoids a `hold`-only rule the Reveal gate
would interfere with (`TurnEngine.cs:242-249` drops a `move` from a holding legion).

### 3. The labour read

```
Crew.LabourAt(world, siteSectorId, siteSlotIndex, factionId) -> long
  Σ over legions L with
      L.OwnerFactionId == factionId
      L.AtSectorId == siteSectorId
      L holds a crew order whose (SiteSectorId, SiteSlotIndex) == (siteSectorId, siteSlotIndex)
      L.Routed == false
    of L's bearer units (rows today, Σ Count after member-stack)
```

- Fighters count zero; a legion without the order counts zero; a legion on its way counts zero; a legion
  crewing another building in the same sector counts zero here. Each bearer is labour for exactly one
  building.
- A legion newly routed this turn has already fallen back off the site (`BattleApplication.cs:37-48`);
  the `Routed == false` clause also excludes one still standing there on its recovery turn, the turn its
  orders are dropped.
- Called inside `Step` (Logistics phase), from hashed state only. Pure; no allocation beyond the sum.

### 4. When the site is not working

**The predicate arrives by registration, not by a dependency (audit M1, edge 1).** This module used to
depend on `exchange` `exchange-hub` and `rift-trade` `crossing-anchor` for their working predicates, which
points **up** the family build order and cycles with both specs. Instead this module owns an
`IWorkingSite` **predicate registry** keyed by the feature a site unlocks: it ships with the caravan
building's predicate (`LoadSite.Of`, `spec-depot.md` §2) and every later site kind registers its own in its
own wave — `exchange-hub` at landing-order row 18, `crossing-anchor` at row 20
([../landing-order.md](../landing-order.md) §3). A feature with no registered predicate is *not working*,
which is the same answer this module gives today for a site that does not exist. No arrow points up, and
`crew` lands at row 13 without waiting for either.

If the building's registered working predicate (`LoadSite.Of` for a caravan building, `spec-depot.md` §2;
the hub's and the anchor's for theirs, registered by them) says it is not working — under construction, destroyed, captured — the
order **stays stored** and the legion keeps standing there (or walking there);
labour at a non-working site is still computed but no consumer reads it. A fact `crew.idle:<reason>` is
written once per turn per such legion. When the site starts working, the labour is there on its first
working turn, whichever came first. This is `legion-build`'s *"stays stored until cleared"* option,
chosen for this kind (legion-build-map §5.8 asks each spec to pick one).

A crew whose site is **captured** is now a legion in a sector another faction owns; contact and zone of
control apply unchanged (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:32-41`). The order does not
make it leave; the player or AI clears or retargets it.

### 5. Defence and service

A crew legion is an ordinary legion: it projects zone of control, is drawn into a sector battle at its
site by the shipped contact rule, and returns to any other use the moment its order is cleared. It pays
the same burn and action budget as any legion (§Locked anchors).

### 6. Fact tokens

Added to `FleetFacts`: `crew.idle`.

## Tunables

None. Labour is a count; the depot's curve and the hub's and crossing's rules own every number that
turns labour into output. (The map's `crew.throughputCurve` moved to `depot`'s per-tier
`depot.throughputCurveByTier` — round 4; the anchor's points are `rift-trade`'s `crossing.throughputCurve`;
one owner per number, `tunables-ssot.md` §2. Re-worded 2026-09-20: this line still named the pre-round-4
key.)

## Numeric types

Labour is `long` (a sum of `Count`, which `member-stack` types as `long`), `checked`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet"
```

## Structure

```
src/FusionRpg.Core/World/Logistics/Fleet/Crew.cs          (new) — order kind, resolver, LabourAt
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs    MODIFIED — crew tokens
<legion-build's standing-order kind registry>             MODIFIED — one registration line
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/CrewTests.cs (new)
```

## Testing strategy

- **Labour counts exactly bearers of ordered, present, unrouted own legions:** one fixture, six variants
  (fighter-only; no order; order for another site; order for **another slot in the same sector**; on the
  lane toward the site; routed) each give 0; the valid legion gives its bearer count; two valid legions sum.
- **No double count:** a sector holding a caravan building and a trade hub, with one crew legion per
  building, gives each building exactly its own legion's bearers.
- **Burn unchanged:** the same legion with and without the order, in supply and out, burns identically
  (`LegionSupply.Burn` and the Pressure pass result compared).
- **Order-independent (DESIGN-GATE §2.16 corollary):** (a) set the crew order, then the depot finishes
  construction; (b) depot finishes, then the order is set and the legion arrives. Both give the same labour
  on the first turn both conditions hold. Both orders tested.
- **Resolver:** at the site → null; elsewhere → a `move` whose path equals the shared planner's.
- **Replay:** a world stepped from its command log with a crew order reproduces its hash.
- **AI parity:** an AI faction's legion on a crew order gives labour by the same read (no player branch).

## Boundaries

- **Always:** labour from the one read; a crew stays a legion; its costs are every legion's costs.
- **Ask first:** labour from fighters; a throughput number in this module; a stance requirement for crews.
- **Never:** a crew table or entity kind; a second standing-order store; extra upkeep for a crew.

## Success criteria (contract)

1. A building's labour equals the bearer count of own, present, unrouted legions on a crew order naming
   its slot; no bearer is labour for two buildings.
2. A crew legion's burn and budget equal the same legion's off the order.
3. Labour on a site's first working turn is independent of whether the order or the building came first.
4. The order re-emits only existing command kinds; replay is byte-identical.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `Crew.LabourAt(world, sector, slot, faction)` — a bearer **count**, never a ratio | `depot` (allowance), `exchange` `exchange-hub` (clearing capacity, its ask A6 — exchange turns the count into its own staffing term; fleet-map ask A12), `rift-trade` `crossing-anchor` (its ask A5) |
| `crew` order kind | `trade-surface` `trade-policy-editor`; `trade-ai` `ai-logistics` |
| `Crew.IsCrew(entity)` | `trade-ai` (its ask T-A2: a legion on a trade standing order is identifiable from state) |

## Dependencies

`depot` (`LoadSite.Of`); `legion-build` `standing-orders` with per-kind resolvers (owner decision
2026-09-19); optional `legion-build` `member-stack`, `raise-choice`. **Not** `exchange` or `rift-trade`:
their working predicates register into this module's `IWorkingSite` registry (§4), which is what inverts the
two upward edges the global audit found (M1 edge 1).

**Round 6 S1 — a crew orders a slot, and the slot's owner matters.** A crew order names a building's slot
(§1). Round 6 S1 makes a feature building count for nobody until one faction owns both its sector and its
slot, so a crew at a building whose slot its faction does not hold supplies **no** labour and reports
`crew.idle:not-owned` (§4's existing fact, one reason more) — the read is
`SectorFeatures.TierFor(sector, faction, feature)` through `sector-features` §5a, never a local owner test.

**Round 6 D2 — the labour read is a count of bearers, not a world channel.** The six `world.*` channels
compose in `ActorHub` and roll up per legion (Round 6 D2), and none of them is *staffing*: `Crew.LabourAt`
stays a bearer **count** (X9 leaves the staffing *term* to each consumer). Where a consumer turns that count
into a capacity it may read a world channel — `depot`'s range and provisioning read `world.march.range` and
`world.supply.burn` (`spec-depot.md` §4), `carried-goods`' capacity reads `world.carry.capacity`
(`spec-carried-goods.md` §3) — always as Hub output behind a stated default until `world-derived` ships, and
never as a fold computed here.

## Hard edges

- The order record is `legion-build`'s hashed state and its `RulesetVersion`/stamp change.
- **Closed vocabularies widened** (reviewed changes, each pinned with its reason in its own test): the
  standing-order kind registry gains `crew`; `FleetFacts` gains `crew.idle`; the set command's refusal
  reasons gain `crew.no-bearers`. *(Audit 2026-09-20: this section said "none".)*
- **Verification boundary:** covered by the `core-world-logistics-fleet` owner boundary that
  `spec-carried-goods.md` Hard edges adds; until then the path falls to `core-fallback`.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world legions, standing orders (legion-build), world turn engine, economy (labour, P11).
[~] Session boundary: trade-network-idea-20260919 record covers this path; check script not run by me.
[x] Read this session: as spec-carried-goods.md; legion-build-map §5.8 in full; decisions-round-4.md
    (round 4 — the slot-keyed read follows from buildings sharing a sector).
[x] decisions.md: no lock covers crews; the phase-order row is untouched.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding.
[x] Verified against code: rout timing, hold-move drop, bearer helper, placement invariant.
[x] Surrounding sections read: TurnEngine Reveal in full; LegionSupply Pressure pass.
[~] Constraints tested: none claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: crew.throughputCurve → depot.throughputCurve recorded in fleet-map.md.
[x] No population pinned.
[x] No cache: labour is computed per call; the key-set edge (site becoming active) is still tested
    order-independently.
[x] Orderings: order-then-build and build-then-order both tested.
[x] No actor magnitude.
[x] No SOLID fork: one labour read for three consumers; one standing-order store (legion-build's).
[x] Registry rows: none new (no new rule beyond the read's contract, enforced by its tests).
```

## Audit 2026-09-20

Fixed here: the Tunables line named the pre-round-4 key; Hard edges said "none" while the module widens
three closed vocabularies (order kind, fact token, refusal reason); the verification boundary is named.
Checked and clean: labour is a per-turn count (no cache, §2.16 does not apply); the key-set edge (site
becoming active) is tested order-independently; no actor magnitude; crew burn equals off-order burn.

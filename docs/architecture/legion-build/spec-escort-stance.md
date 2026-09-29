# Spec: `escort-stance`

**Status: written against shipped code 2026-09-19.** Module id `escort-stance`, row 9 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `standing-orders`; prioritised because
`trade-network` `fleet` needs it). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.4, §6.5.
Contract requested by `fleet`: `docs/architecture/trade-network/fleet/spec-escort-link.md` §1 (the hold
contract, fleet ask A3) and fleet ask A8 (multi-entity battle sides, `fleet-map.md:419`).

## Objective

`escort` joins the stances. A legion in `escort` names another legion of its own faction (its **charge**),
moves with it, and stands in any battle its charge is drawn into. It is a stance plus a standing order of
kind `escort`, so it re-emits every turn without the player re-filing it. Nothing about escort is a battle
mechanism: any combat effect of the stance is an atom through layer 5c, never an engine branch.

Success looks like: an escort never outpaces its charge and follows it through a caravan's whole loop;
losing the charge ends the escort with a named reason; a world with no escort resolves byte-identically.

## Scope and non-goals

- **In:** the `escort` stance value; the `escort` standing-order kind and its resolver (the hold contract);
  the join rule that puts an escort on its charge's battle side; the drop and end reasons.
- **Out:** widening the battle request to more than one entity per side (`field-battle-kinds` owns that
  seam — this module states the rule it must implement); lane-loss arithmetic (`logistics-flow`
  `lane-loss` reads the stance through its own `lane.stanceEscortMilli.{stance}` tuning row,
  `docs/architecture/trade-network/logistics-flow-map.md:343-349`); caravan specifics (`fleet`
  `escort-link`).
- **Escort strength.** The map's §5.9 says *"its strength is what `trade-network`'s lane-loss formula
  reads"*. `logistics-flow` decided v1 reads **presence, not strength** (`logistics-flow-map.md:596`, its
  Q1), because the only whole-legion strength figure is fog-only by contract
  (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`). This module exposes presence; it computes no
  strength. **Round 4 (2026-09-19, owner P):** the later strength read is the **power roll-up** of the escorting
  legion (`spec-legion-power.md`, map row 17) — Hub output summed, never a figure computed here — and it
  replaces the v1 count only once the power program's `ssot-power-scale.md` §10 contest row exists.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The closed stance list `{march, scout, hold, dowse}`; a stance is loop behaviour priced by `BudgetFor` | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:8-60` (list at `:22`, pricer at `:50-60`) |
| Built | Postures land in Snapshot and set the refilled budget | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:449-459` |
| Built | The command already carries a target entity | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:197` (`TargetEntityId`) |
| Built | Contact is kind-agnostic; a lane meeting and a sector contact each build one request | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:145-156,276-286` |
| Real gap | A request names one attacker and at most one defender, and the resolver receives exactly those two | `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-55`; `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:34-56` |
| Real gap | No `escort` stance, no following | — |

## Design

### 1. The stance

`MovementPolicy.Escort = "escort"` joins `Stances`. `BudgetFor(escort)` is the march budget
(`PointsPerTurn`): an escort marches at a marching pace. A bare `stance` command asking for `escort` is
refused at admission (`stance.escort-needs-charge`) — escort only exists with a charge, so it is set
through `set-order`.

### 2. Setting and ending

`set-order { EntityId = escort, Kind = "escort", Template.TargetEntityId = charge }` (`standing-orders`'
command). Validation (named reasons): charge is a legion of the same faction (`escort.not-ally`); charge is
not the escort itself (`escort.self`); charge is not itself escorting (`escort.chain` — no escort chains).
Resolving it in Snapshot sets the stance to `escort`. Clearing the order, replacing it, or a `stance`
command to any other stance ends the escort and returns the stance to `march`.

### 3. The hold contract — the `escort` resolver's `Emit`

`fleet`'s ask A3, adopted as written (`spec-escort-link.md` §1). "The charge's command" is whatever the
charge has **filed or had emitted** this turn — so the emitter processes non-escort orders first and escort
orders last, in one barrier pass (`standing-orders` §5):

| Charge's command this turn | Escort's emitted command |
|---|---|
| `move` along path *P* | `move` along *P* from the escort's own position (resumed mid-lane by `MarchResolver`, `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:29-31`) |
| none | none if the escort stands with the charge; else `move` to the charge's sector along the owner's believed path |
| the charge is routed | the escort is not routed; it follows the rule above next turn |

**Never ahead.** Following the same path is not enough: an escort whose banner earns a ley discount its
charge does not (`LaneCost.cs:142-144`) would march further on the same budget. So `MovementPhase`
resolves an escort's march after its charge's and clips the escort's end point to the charge's end point
on the shared path — a loop rule in the one movement phase, keyed on the stance, never a second movement
path. A clipped escort keeps its unspent budget exactly as any halted march does.

`Advance` ends the order with `escort.charge-lost` when the charge no longer exists or has changed faction.
An escort that cannot keep up (the other direction of the same lane-cost difference) keeps following and
reports `escort.lagging` that turn — a report token, never a stop.

### 4. The join rule — who stands in the charge's battle

Stated here, implemented through `field-battle-kinds`' widened seam (map ask A8):

> When a battle request names entity *C* on a side, every legion of *C*'s faction that is in `escort`
> stance with charge *C* **and** stands at the battle's location (same sector, or same lane) joins that
> side.

This is the kind-agnostic contact rule plus one membership predicate; no battle kind special-cases it, and
the district assault gains it the same way. Until `field-battle-kinds` widens the request, the rule is
declared and its test is skipped with the reason visible (`fleet`'s own escort-link test is gated the same
way, `spec-escort-link.md:136-138`).

### 5. Combat effect

None by default. If a doctrine or tradition wants an escort bonus, it is a 5c atom bound through
`legion-owner-scope` — never a branch in the engine or here.

## Tunables

None owned. The `escort` lane-loss weight is `logistics-flow`'s tuning row. `BudgetFor(escort)` reuses
`PointsPerTurn`, which is a structural `const` today (`LaneCost.cs:32`).

## Numeric types

No new magnitude. Lane progress and budgets keep their `int` per-mille frame.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Stance|FullyQualifiedName~Movement|FullyQualifiedName~Contact|FullyQualifiedName~Crossing|FullyQualifiedName~StandingOrder"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs            MODIFIED  Escort stance, BudgetFor arm
gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs       MODIFIED  escort resolved after charge; end point clipped
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs   MODIFIED  bare stance:escort refused
src/FusionRpg.Core/World/Orders/EscortOrderResolver.cs   NEW       Validate / Emit (hold contract) / Advance
src/FusionRpg.Core/World/Orders/StandingOrder.cs         MODIFIED  one registration line
src/FusionRpg.Core/World/Turn/EscortJoin.cs              NEW       the §4 predicate (consumed by field-battle-kinds)
gk-web/web/fusion-rpg-web stance word table                     MODIFIED  one word
```

## Testing strategy

- **Hold contract:** one test per row of §3, over a charge running a `repeat move` order and over a charge
  moved by hand orders; and over a full load–march–unload–return loop once `fleet` registers `trade-route`.
- **Never outpaces:** over any path, the escort's lane progress never passes its charge's on the same lane.
- **Charge lost:** charge destroyed, disbanded or captured → `escort.charge-lost`, stance back to `march`.
- **Validation:** each refusal in §2 with its reason; bare `stance: escort` refused.
- **Join rule:** a predicate test over sector and lane locations, including an escort at the wrong
  location (not joined) and an escort of another charge (not joined). The integration test that the escort
  appears in the battle is gated on `field-battle-kinds` with a visible skip.
- **Byte identity:** worlds with no escort resolve unchanged (`StanceTests`, `MovementTurnTests`,
  `ContactAndClearTests`, `CrossingSymmetryTests`).

## Boundaries

- **Always:** set escort through `set-order`; follow the charge's command of this turn.
- **Ask first:** escort chains; escorting another faction's legion; a strength-based lane-loss term other
  than `legion-power`'s roll-up (round 4 P).
- **Never:** a combat branch for escort; an escort special case in contact or movement code.

## Success criteria

1. The hold contract holds for every row, including a caravan loop.
2. Charge loss ends the order with a reason.
3. The join predicate exists and is the one rule `field-battle-kinds` applies.
4. No-escort worlds unchanged.

## Interface exposed to dependents

`MovementPolicy.Escort`, the `escort` order kind, `EscortJoin.JoinsSide(world, request, entity)` —
consumed by `fleet` `escort-link`, `logistics-flow` `lane-loss` (stance id only), `field-battle-kinds`.

## Hard edges

- **Stance vocabulary widened** (+`escort`): the list is pinned by a membership test with its reason.
  `world-continuity` `world-warden` adds `warden` to the same list, so the pinned members are whatever the
  list holds when each lands (audit 2026-09-20: the first draft's "4 → 5" would be stale).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 3** and grants a player-facing feature (the `escort`
  stance), so it rides **wave 3's single bump** and no longer claims "no bump". ~~No `RulesetVersion` bump:
  the stance is only reachable through `set-order` … Corrects map §4's bump list.~~ Those facts still hold and
  still matter — the stance is reachable only through `set-order`, a command no stored log carries
  (`TurnEngine.cs:134-140`), and the value is hashed by name only for entities that hold it — which is why
  **no golden moves and no world is migrated**. The bump is about the *stamp*, not the bytes.
- **Cross-program:** the battle presence clause waits on `field-battle-kinds` (map ask A8).

## Dependencies

`standing-orders` (the kind seam and the barrier emitter). The join clause's integration waits on
`field-battle-kinds`.

## Design-gate checklist

```
[x] Subsystems: world movement (stances), standing orders, world battle contact (rule only).
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, fleet spec-escort-link.md (design + asks), fleet-map A8/C10,
    logistics-flow-map lane-loss section and Q1. NOT read: world-map row documents, spec-world-movement.md.
[x] decisions.md checked: World turn phase order (postures land in Snapshot).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: stance list and BudgetFor, posture landing, TargetEntityId, contact requests,
    the pairwise request and combatant list.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted: loop only; no mechanism.
[~] Corrections propagated: strength→presence and the no-bump call recorded in map §10.
[x] Pinned: stance list (5) and order kinds are closed vocabularies with reasons.
[x] No event-refreshed cache.
[x] Orderings: charge-first emission is a fixed pipeline order inside one pass; hand vs emitted charge
    commands both tested.
[x] No actor magnitude.
[x] No parallel path: one stance list, one emitter, one join predicate.
[x] No new rule beyond standing-orders' registry row.
```

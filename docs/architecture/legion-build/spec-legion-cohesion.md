# Spec: `legion-cohesion`

**Status: written against shipped code 2026-09-19.** Module id `legion-cohesion`, row 10 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `member-stack`, `legion-owner-scope`).
Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1 (*"Cohesion — mono-element legions gain,
three or more elements lose"*) and its prior art (Heroes III alignment: one town +1 morale, three or more
−1).

## Objective

A legion's element mix becomes a real choice with no extra UI. Read from its fighting roster —
count-weighted — a legion falls into one **cohesion band**, and the band's `world-buff` container binds to
the legion through layer 5c. A mono-element legion gains; a legion of three or more elements loses; two
is neutral by default.

Success looks like: cohesion is a pure function of the fighting roster; reordering members never changes
it; its contribution appears and disappears in the same commit the roster crosses a band edge; every
magnitude comes from tuning scaled by the one ladder.

## Scope and non-goals

- **In:** the band reader; the band vocabulary; the projection of each band's container from tuning; the
  contributor it registers with `legion-owner-scope`.
- **Out:** what the band grants in battle beyond composing contributions (the engine reads channels as it
  always does); secondary elements (cohesion reads `ElementPrimary`, the same field the banner reads).

## Layer answers

Layer **5c** (through `legion-owner-scope`) · scope: one legion's fighting members · lifetime: live, derived
from the roster every commit, never stored · carrier: `world-buff.cohesion-{band}` · SourceId
`legion:{entityId}:world-buff.cohesion-{band}`.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The banner vote: most common primary element, ties by the ring's declared order, never stored | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:63-93` |
| Built | Species primary element | `CreatureSpeciesCatalog` via `LaneCost.cs:71-72` |
| Built (after `member-stack`) | Count-weighted, fighting-only unit sums | `spec-member-stack.md` §5 |
| Built (after `legion-owner-scope`) | 5c reconcile and reader | `spec-legion-owner-scope.md` §2–§3 |
| Real gap | No cohesion read, no band, no container | — |

## Design

### 1. The reader

```csharp
// src/FusionRpg.Core/World/Legion/LegionCohesion.cs (new; the file does not exist yet)
public static class LegionCohesion
{
    // Elements whose share of the legion's FIGHTING units is ≥ minShareMilli count toward the band.
    // Shares are Σ Count per ElementPrimary over rows where Fights(Role), divided once at the end.
    public static CohesionBand BandOf(WorldEntity legion, CohesionTuning tuning);
}
public enum CohesionBand { None, Mono, Pair, Mixed }   // None = no fighting unit
```

`Mono` = one counted element; `Pair` = two; `Mixed` = three or more. `minShareMilli` keeps a single token
unit from flipping a 400-unit legion into `Mixed` — the count weighting the map asked for, made legible as
one threshold rather than a curve.

The reader is order-free by construction (a sum per element, then a count of elements), and it shares the
banner's element source so the two can never disagree about what element a unit is.

### 2. Containers from tuning

Each band except `None` has one container, `world-buff.cohesion-mono|pair|mixed`, **projected** at host boot
from `legion.v1.json`'s (proposed; the file does not exist yet) `cohesion.bands` and validated through `ContainerValidator` like any container
(`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs:35` accepts the `world-buff` prefix). A band with no
atoms projects no container and binds nothing. No container row is hand-edited or generated elsewhere.

### 3. The contributor

`LegionBuffSources` gains `cohesion`: desired = `{ world-buff.cohesion-{BandOf(legion)} }` when that
container exists, else `{}`. `legion-owner-scope`'s reconcile does the rest, so a roster change that crosses a
band edge withdraws the old band and binds the new one in the same commit.

## Tunables

`data/tuning/legion.v1.json` (proposed; the file does not exist yet), section `cohesion`, published through
`gk-core/tools/tuning/publish.py` (extended for the new domain if needed):

| Key | Unit | First publish |
|---|---|---|
| `minShareMilli` | per-mille of fighting units | a provisional value chosen by principle at the tuning publish |
| `bands.mono` / `bands.pair` / `bands.mixed` | list of `{ channel, op, amount }` — `stat.derived` atoms; `amount` is the band value `ContentScale` scales per member | **empty** in the first publish (see Hard edges) |

Magnitudes are never literals in code; the ladder is applied once, by `legion-owner-scope`'s reader
(`ContentScale.Apply`). The cohesion curve is not a level curve, so it adds nothing to the power-scale §10
inventory.

## Numeric types

Unit sums are `long` (`member-stack`); the share is computed as `checked(elementUnits * 1000 / totalUnits)`
with the division last. Band values are `long` in tuning and pass through `ContentScale.Apply`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Cohesion|FullyQualifiedName~Banner"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LegionBuff"
python gk-core/scripts/audit-magic-numbers.py --summary
```

## Structure

```
src/FusionRpg.Core/World/Legion/LegionCohesion.cs       NEW       reader + band enum
src/FusionRpg.Core/World/Legion/LegionTuning.cs         NEW       the legion.v1 domain record + a pure parser over a string
                                                                   (the host reads the file and injects it — tunables-ssot §7.2; audit 2026-09-20)
src/FusionRpg.Core/World/Legion/LegionBuffSources.cs    MODIFIED  cohesion contributor
data/tuning/legion.v1.json                              NEW       via publish.py only
gk-core/tools/tuning/publish.py                                 MODIFIED  legion domain (if not yet supported)
```

## Testing strategy

- **Bands:** mono, pair, mixed, none; a token unit below `minShareMilli` does not count; exactly at the
  threshold it does.
- **Order-free:** shuffling member rows never changes the band (property test).
- **Fighting only:** bearers never count; a legion of fighters of one element plus bearers of another is
  `Mono`.
- **Withdrawal edge, both directions:** a raise/attach/casualty that moves the band withdraws the old
  binding and binds the new one in the same commit; a change that stays in band touches nothing.
- **Empty publish:** with every band empty, no binding is written and every golden is unchanged.
- **Closed vocabulary:** `CohesionBand` pinned to its four members with the reason (the HoMM3 shape: one,
  two, three-or-more, plus none).

## Boundaries

- **Always:** read elements through the species catalog's primary element; decide bands in `BandOf` only.
- **Ask first:** secondary elements in the vote; a band per element (a fire-mono bonus different from an
  ice-mono bonus).
- **Never:** store cohesion; scale a magnitude outside the 5c reader; a cohesion branch in battle.

## Success criteria

1. Pure, order-free band reader over fighting units.
2. Band containers projected from tuning; bindings follow the roster in the same commit.
3. Empty first publish moves nothing; the filling publish is one explained bump.

## Interface exposed to dependents

`LegionCohesion.BandOf` (the FE legion card may show the band — a later UI module).

## Hard edges

- **Tunable domain file** `legion.v1.json` (proposed; the file does not exist yet) is created here (shared with modules 11–15).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave** (owner decision C1, 2026-09-20): a world's rules never change mid-life, and the family keeps a single landing order in [landing-order.md](../trade-network/landing-order.md). The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1). This module is **wave 3**.
- **Two-step landing.** The code lands with empty bands (no behaviour change) and rides **wave 3's single
  bump**. The tuning publish that gives bands atoms changes every legion's battles, so it is its **own
  landing** with its own capability row and bump in the landing order, and it re-blesses the siege goldens
  with the reason — the W58 precedent of a tuning-only publish that makes an inert term real
  (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:89-96`). Two landings, two bumps; never one flag whose
  behaviour arrives later, which is the C1 breach the register closed.

## Dependencies

`member-stack`, `legion-owner-scope`, `role-aware-placement` (`Fights`).

## Design-gate checklist

```
[x] Subsystems: world legions, atom layer (world-buff containers), stats (5c through ActorHub), tunables.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, actor-layer-compose-ideal.md, definitions.md §0-§6. NOT read:
    tunables-ssot.md, ssot-power-scale.md, element-hub-ssot.md.
[x] decisions.md checked: Actor layer stack (5c via legion-owner-scope).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: BannerElement, ContainerValidator prefix, the W58 tuning-publish precedent.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted; no cap; one ladder application.
[~] Corrections propagated: map §10 records the bump correction.
[x] Pinned: CohesionBand (4) is a closed vocabulary with its reason.
[x] No cache: derived per commit; the band-edge key-set change has tests in both directions.
[x] Order-free criteria tested by shuffle.
[x] Contributes through legion-owner-scope's registered reader (SourceId legion:...).
[x] No parallel path.
[x] No new rule beyond legion-owner-scope's registry row.
```

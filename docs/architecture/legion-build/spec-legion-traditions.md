# Spec: `legion-traditions`

**Status: written against shipped code 2026-09-19.** Module id `legion-traditions`, row 12 of the
[legion-build map](../legion-build-map.md) (wave 3; depends on `legion-owner-scope`; external `empire-seed`
exemplars). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.1, owner decision **L2** (reset on
disband or rout).

## Objective

A legion earns **traditions** from its own history. Counters over a closed list of world facts advance as
the legion fights and marches; each tradition seed names one fact and has rank tiers; a reached rank binds
that tradition's container through layer 5c. A rout or disband wipes the history.

Success looks like: each counter advances from exactly one kind of fact, once per fact; rank thresholds come
from tuning on a soft curve with no top; reset is total; the fact list is a closed vocabulary `empire-seed`
mirrors.

## Scope and non-goals

- **In:** the fact vocabulary (`empire-seed` waits on it, `docs/architecture/empire-seed-map.md` §5.13, *Real gap*);
  per-legion counters; the one observer; ranks; the contributor.
- **Out:** tradition seeds and their rank-tier numbers (`empire-seed`; tier multipliers in
  `legion-seed.v1.json`, proposed; the file does not exist yet); magnitude scaling (the 5c reader);
  **registering or rolling up the six `world.*` channels** (round 6 D2 names traditions as a *source* of
  them: a tradition container may carry one, as an ordinary 5c Hub contribution. `world-derived` registers
  the channels; `legion-power`'s `LegionWorldChannels` rolls them up, `spec-legion-power.md` §6. This module
  computes none and folds none).

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The only per-legion memory is `Routed` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:314-320` |
| Built | Battle outcomes enter the world in one place | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:10` (`Apply`), called from `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:34` |
| Built | Outcome carries winner and guard-cleared | `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:208-217` |
| Built | Raise report lines are named events, the idiom for fact lines | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:113` |
| Real gap | No history counters | — |

## Design

### 1. The fact vocabulary (closed)

```csharp
public enum TraditionFact
{
    BattleWon,        // the legion is the outcome's winner
    BattleHeld,       // the legion fought, was not the winner, survived, and was not routed
    GuardCleared,     // the legion's guard battle cleared its slot
    SectorClaimed,    // a claim by the legion settled in Snapshot
    LaneCompleted,    // the legion finished a lane (arrived at its far sector)
    ClimateFought,    // the legion fought in a climate it had not fought in before (one per new climate)
}
```

**Registry (round 4, owner Q12):** the members live in the one shared legion vocabulary registry, `data/seed/legion/_registry/vocab.v1.json` (`empire-seed/spec-legion-seed-contract.md` §5.2); this C# enum is validated against it at load, so there is one list, never a mirror plus a sync test.

Each is observable today from one existing site. The list is pinned by a membership test with the reason
("world facts a tradition may count; `empire-seed`'s `triggerKind` validator mirrors it").

### 2. Counters

`WorldEntity.History` — a map `TraditionFact → long`, plus the set of climates fought (six elements at
most, for `ClimateFought`). Hashed as a `history` row only when non-empty.

### 3. The one observer

`LegionHistory.Observe(world, entityId, fact, context)` — a pure function, called from exactly the site of
each fact: `BattleApplication.Apply` (won, held, guard cleared, climate), the claim settle in Snapshot,
the march arrival in the movement phase. It increments once per fact occurrence; a source-scan test
asserts it is the only writer of `History`.

### 4. Ranks and the contributor

For each tradition seed whose `triggerKind` matches a fact, rank = the number of thresholds its counter has
reached on `legion.v1.json` (proposed; the file does not exist yet) `traditions.rankThresholds` — a soft
curve with no last rank (the curve is authored as points and extended by its last slope, so no count is
the top). `LegionBuffSources` gains `tradition`: desired = one container per tradition at rank ≥ 1,
`world-buff.legion-tradition-{seedId}-r{rank}`. Which tradition seeds a legion can earn: every tradition seed
of the world's catalog (no per-legion pick; the history decides).

### 5. Reset

`Routed` set this turn, or the legion disbanded: `History` cleared, total, in Snapshot before the reconcile.

## Tunables

`legion.v1.json` (proposed; the file does not exist yet) `traditions.rankThresholds` (points
`[rank, counterValue]`, extended by last slope). Rank names cover the authored points only; later ranks reuse the last name (a finite name list is presentation, never a rank cap — `empire-seed/spec-legion-seed-contract.md` §5.1). Tier multipliers: `legion-seed.v1.json` (proposed; the
file does not exist yet).

## Numeric types

Counters `long`, `checked`. Rank `int` (an ordinal).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Tradition|FullyQualifiedName~TurnEngine|FullyQualifiedName~Battle"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                MODIFIED  WorldEntity.History
src/FusionRpg.Core/World/Legion/LegionHistory.cs      NEW       fact enum, observer, ranks, contributor
gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs    MODIFIED  observe battle facts
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs           MODIFIED  claim-settle observe; reset; RulesetVersion
gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs    MODIFIED  lane-completed observe
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs            MODIFIED  history row when non-empty
```

## Testing strategy

- One test per fact: it advances exactly its counter, exactly once per occurrence.
- `ClimateFought` counts a climate once, however many battles there.
- Rank crossing binds the rank container and withdraws the lower one in the same commit; no top rank.
- Reset on rout and on disband is total; the 5c contributions vanish the same commit.
- Observer is the only writer (source scan).
- Fact enum pinned with reason.

## Boundaries

- **Always:** observe at the fact's own site through the one observer.
- **Ask first:** a new fact; inheritance across disband (L2 says reset).
- **Never:** parse report strings to count facts; a hard top rank.

## Success criteria

1. Counters exact, per fact, once.
2. Ranks soft, uncapped, tuned.
3. Reset total; contributions follow.

## Interface exposed to dependents

`TraditionFact` (mirrored by `empire-seed`); `History` on the legion DTO.

## Hard edges

- **Wave and ruleset bump (round 6 C1):** this module is legion-build **wave 3** and grants a player-facing
  feature, so it rides **wave 3's single `RulesetVersion` bump** — one bump per wave, taken at landing (never
  pre-assigned) and recorded with the wave's one capability flag in
  [landing-order.md](../trade-network/landing-order.md); it no longer claims a bump of its own. The
  **re-bless** is still this module's and still large: every legion that fights accumulates hashed history,
  so every world golden with a battle moves. One explained re-bless, in this module's commit.
- Closed vocabulary declared in the shared registry both programs read (Q12).
- **Two power-ladder rows owed (audit 2026-09-20).** `ssot-power-scale.md` §10 is a closed inventory.
  (1) `traditions.rankThresholds` — how many fact events a counter needs to reach rank *r* — is a cost
  ladder over a lifetime counter, the exact shape of §10.2 row 33 (`MasteryIndex.CountToReach`, *"a cost
  ladder for how many qualifying events a lifetime counter needs to reach mastery index m"*), which got its
  own row; it owes one too, with its last-slope extension named as the no-top rule. (2) The rank tier
  multipliers (`legion-seed.v1.json` `traditions.rankTierMultiplierMilli`) are a per-rank quality
  multiplier on a `P(Θ)` magnitude — row 38's shape — and owe a PS-4 row. Both are requested from the power
  program; until they land, ranks bind their rank-1 container only (no rank multiplier is read).

## Dependencies

`legion-owner-scope`, `member-stack`; external `empire-seed` exemplars.

## Design-gate checklist

```
[x] Subsystems: world turn (observers), legions, 5c.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: map, ideal, empire-seed-map legion sections. NOT read: world-map row documents.
[x] decisions.md checked: World turn phase order — no phase added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: Routed, BattleApplication/BattleReporting, outcome fields.
[x] Read the surrounding section of every rule quoted.
[~] No suite run.
[x] No §2 invariant contradicted; no ceiling.
[~] Corrections propagated (map §10).
[x] Pinned: TraditionFact (6) closed, with reason.
[x] No cache; reset and rank edges tested.
[x] Rout-then-death and death-then-rout in one turn converge (reset is total).
[x] Contributes via 5c reader.
[x] No parallel path.
[ ] Registry row owed: "History written only by LegionHistory.Observe" — the scan test is the guard.
```

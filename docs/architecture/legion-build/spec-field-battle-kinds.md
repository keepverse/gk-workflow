# Spec: `field-battle-kinds`

**Status: written against shipped code 2026-09-19.** Module id `field-battle-kinds`, row 16 of the
[legion-build map](../legion-build-map.md) (wave 4; depends on `role-aware-placement`, `stack-combatant`,
`general-member-hub`). **Owner decision Q3 (2026-09-19):** this module takes over the tracked
`world-actor-combat` work (`docs/architecture/actor-hub-and-combat-power-solid-fixing/spec-placeholder-battle-hub.md:22`).
Law: [battle-engine-ssot.md](../battle-engine-ssot.md). Also closes `fleet`'s ask A8 (multi-entity sides,
`docs/architecture/trade-network/fleet-map.md:419`).

## Objective

`Sector`, `Lane` and `Guard` battles resolve through `BattleEngine.Resolve` on a board, as the district
assault already does, so interception, escort and guard clearing have real outcomes. The world owns the
loop — who fights, where, when in the turn — and the engine owns every mechanism.

Success looks like: every kind resolves through the one engine entry; a district assault is unchanged; a
fight with no living attacker is still refused, not invented; replay is byte-identical.

## Scope and non-goals

- **In:** a field board projection for sector and lane fights; guard fights against their wave; the
  resolver dispatch; widening the request to more than one entity per side (A8) with `escort-stance`'s join
  predicate; outcome translation for the three kinds.
- **Out:** any new mechanism (none needed — stacks, placement and composition arrive from their modules);
  kill attribution and XP from world battles (`battle-engine-ssot.md` §4 D9, `species-progression`); intel
  strength (stays fog-only, `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:6-13`).

## §5 answers

Responsibility: none new — this is a **loop** (a board and a dispatch), every mechanism is the engine's ·
decides or resolves: the world chooses nothing in battle; intent comes through `IIntentSource` (the siege
AI path already used, `DistrictAssaultResolver.cs:214-230`) · every mode: the same engine entry ·
deterministic: seeds derived per battle id as the district resolver does (`:120`).

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built (refused by design) | Every non-district kind returns a winnerless outcome — the T20 feature-absence guarantee | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:13-25,101-104` |
| Built | Requests for each kind: lane meeting, sector contact, guard clear | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:145-156,276-286`; `gk-core/src/FusionRpg.Core/World/Turn/SiegePhase.cs:59-70` |
| Built | Kind-agnostic seam, request, outcome; pairwise combatants | `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6-72,178-217,280-289`; `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:34-58` |
| Built | Guard waves are content | `GuardWaveId` on the request (`BattleSeam.cs:63`); `gk-core/src/FusionRpg.Core/Battle/WaveCatalog.cs:78,120` |
| Built | Engine outcome `Victory / Defeat / Stalemate` | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:562-567` |
| Built | The district join: setups, placement, `BattleEngine.Resolve`, side outcomes | `DistrictAssaultResolver.cs:99-285,415-541` |

## Design

### 1. One resolver, one dispatch

`DistrictAssaultResolver` is renamed `WorldBattleResolver` (the one `IBattleResolver`) and dispatches on
kind to a board builder; setups (`BuildAnimateSetups`, with `Fights`, stack counts and the Hub provider),
the engine call and side outcomes are shared by every kind. The T20 early return stays for a request that
cannot be simulated (no board, no living fighting attacker) — refusal, never an invented winner.

### 2. Boards

- **Sector / Lane:** `FieldLayout.Build(kind, locationId, worldSeed)` — an open board with two deployment
  edges, no slots, no core; size from `legion.v1.json` (proposed; the file does not exist yet)
  `field.boardRows/boardCols` per kind. A lane board is keyed by the lane's type.
- **Guard:** the attacker against the slot's `GuardWaveId` wave built by `WaveCatalog`, on the sector's
  field board.

**A field board is sized to fit both forces (corrected by the 2026-09-20 audit).** The first draft
refused a fight whose force outgrew its deployment edge, as the district resolver does
(`DistrictAssaultResolver.cs:175-178`, *"a board too small for the forces standing on it refuses
cleanly"*). A district board has authored geometry, so refusal is its honest answer there; an open field
board has none, and refusing there would make any force with more stacks than an edge has cells
impossible to intercept, guard or catch — a hidden count ceiling that pays the largest army. So
`FieldLayout.Build` takes both sides' fighting-stack counts and sets the board's depth to
`max(field.boardRows, ranks needed)` — the tuned size is a **minimum**, stated as structural in the code
comment, and the growth is deterministic from the inputs. Refusal stays only for the two cases the T20
guarantee names: no board (an unknown location) and no living fighting attacker.

### 3. Multi-entity sides (A8)

`BattleRequest` gains `AttackerAllyIds` / `DefenderAllyIds`, filled at request build by
`EscortJoin.JoinsSide` (`escort-stance` §4) — the only membership rule. `BattleReporting.Fight` passes every
named entity to the resolver; each entity's survivors come back as their own `BattleSideOutcome`. Empty lists
are serialized absent so existing requests are unchanged.

### 4. Outcomes

| Kind | Engine result | World result |
|---|---|---|
| Sector / Lane | `Victory` / `Defeat` | winner holds; the losing side routs if any fighter survives, else is destroyed (`role-aware-placement`'s bearer rule) |
| Sector / Lane | `Stalemate` | no winner; both keep their ground; both wounded as reported |
| Guard | attacker wins | `GuardCleared = true` |
| Guard | otherwise | guard stays; the attacker routs or is destroyed |

## Tunables

`legion.v1.json` (proposed; the file does not exist yet) `field.boardRows`, `field.boardCols` per kind —
**minimum** sizes (the board grows to fit, §2).

## Numeric types

As the district resolver: `long` HP, `checked` arithmetic.

## Commands

The full suite is the right tool here (a change crossing program boundaries, `AGENTS.md` verification
boundary point 2):

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
.\scripts\test-fast.ps1 -AllDefault
python gk-core/scripts/guard-actor-hub.py
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs → WorldBattleResolver.cs  RENAMED + dispatch
src/FusionRpg.Core/World/District/FieldLayout.cs          NEW       field boards
gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs               MODIFIED  ally id lists
gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs          MODIFIED  multi-entity combatants
gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs        MODIFIED  per-entity outcomes
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs          MODIFIED  constructs the renamed resolver
```

## Testing strategy

- District goldens unchanged (the dispatch is a no-op for them).
- One test per outcome row per kind.
- Refusal kept: no living fighting attacker → winnerless.
- (Audit 2026-09-20) A sector or lane fight whose attacker fields more stacks than `field.boardRows` ranks
  resolves on a grown board — never refused; the grown board is identical for identical inputs.
- Escort joins its charge's side at a lane and at a sector; fleet's gated escort test un-skips.
- Replay from a recorded intent trace is byte-identical.
- World turn goldens re-blessed where a refused fight became real, each with the reason.

## Boundaries

- **Always:** one resolver entry; mechanisms only from the engine.
- **Ask first:** capture on the field; retreat as a player choice mid-battle.
- **Never:** an abstract strength comparison; a per-kind mechanism.

## Success criteria

All four kinds resolve through `BattleEngine.Resolve`; district unchanged; refusal kept; A8 closed.

## Interface exposed to dependents

The resolver for every kind; ally lists — consumed by `fleet` `interception`, `escort-link`.

## Hard edges

**Round 6 C1:** this module is **wave 4**; it rides **wave 4's single `RulesetVersion` bump**, taken at
landing and recorded in [landing-order.md](../trade-network/landing-order.md), and it carries the turn-golden
re-bless wherever a refused fight becomes real. The
`world-actor-combat` track id is retired into this module (a line owed in the solid-fixing program's docs,
not made here). Full suite at landing.

## Dependencies

`role-aware-placement`, `stack-combatant`, `general-member-hub`, `escort-stance` (join predicate).

## Design-gate checklist

```
[x] Subsystems: world battle loop, battle engine (consumer only), world seam.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: battle-engine-ssot.md (whole), spec-placeholder-battle-hub.md, fleet asks.
    NOT read: battle-timeline-map.md, battle-turn-ideal.md, world-map row documents.
[x] decisions.md checked: Battle engine is the SSOT.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: the refusal, the three request sites, the seam, outcome enum, the district join.
[x] Read the surrounding section of every rule quoted.
[~] No suite run; golden movement is expected and re-blessed with reasons.
[x] No §2 invariant contradicted: loop only.
[~] Corrections propagated: track retirement listed as owed.
[x] No population count pinned.
[x] No cache.
[x] No ordering assumption; ally lists derive from one predicate.
[x] Consumes Hub output via the provider; no fold.
[x] No parallel path: one resolver.
[x] No new rule needing a registry row.
```

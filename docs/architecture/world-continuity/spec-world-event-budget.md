# Spec: `world-event-budget`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 12 of the
[world-continuity map](../world-continuity-map.md) (wave 4; depends on `world-state-vocabulary`,
`coarse-step`, external npc-story-events `storylet-selection`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.9. House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

Active worlds have the most events. Each world gets an **event budget keyed by its two state columns**:
full when active and contested, reduced when won, low and coarse-only when hibernating,
maintenance-only when idle. The storylet engine reads it; the shipped calendar in the `Events` phase
reads it; hibernating events resolve inside `CoarseStep` from the **same** deck — never a second one.

## Scope and non-goals

**In scope:** the budget table (a pure lookup); the budget as a logged coarse input; the rule that a
coarse draw uses the active draw's deck; the ask to npc-story-events.

**Not in scope:** storylet content, selection, pity and cooldowns (`storylet-selection`); the world host
(`world-events-host`); calendar effects (the `Events` phase keeps rolling the calendar exactly as today).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The `Events` phase rolls the calendar and reports boundaries; effects belong to later modules | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:352-377` |
| Phase order is locked | `docs/architecture/decisions.md` *World turn phase order* row |
| npc-story-events: selection identical for every host, with a fire chance and pity for sparse hosts | `docs/architecture/npc-story-events-map.md:215` (`storylet-selection`) |
| npc-story-events adds content to the world `Events` phase through `world-events-host` | `docs/architecture/npc-story-events-map.md:185` |

### Real gap

No per-state budget; npc-story-events' map has no hibernating host and a world scope that ends with the
world (`docs/architecture/npc-story-events-map.md:209`).

## Design

### 1. The budget — a pure lookup over the two columns

```csharp
// src/FusionRpg.Core/World/Continuity/WorldEventBudget.cs
public static int PullsPerTurnMilli(WorldAttention a, WorldOutcome o, WorldEventBudgetTuning t) => (a, o) switch
{
    (_, WorldOutcome.Fallen)                          => t.FallenMilli,       // enemies' world; digest only
    (WorldAttention.Idle, _)                          => t.IdleMilli,         // maintenance-only
    (WorldAttention.Hibernating, _)                   => t.HibernatingMilli,
    (WorldAttention.Active, WorldOutcome.Won)         => t.ActiveWonMilli,
    (WorldAttention.Active, WorldOutcome.Contested)   => t.ActiveContestedMilli,
};
```

Validated at load: `ActiveContested ≥ ActiveWon ≥ Hibernating ≥ Idle ≥ 0` — active worlds have the most
events (ideal §6.9), and nothing in the background is busier than the foreground.

- **Active world:** `world-events-host` scales its host fire chance by the budget; the budget is read from
  hashed state inside the step (`WorldState.Outcome`, `world-victory` §1) plus the attention, which is
  **not** hashed — so the attention enters `Step` as an explicit input recorded in the turn log's row
  (the active world is always `active` when it steps, `world-state-vocabulary` §5, so the value is a
  constant for full steps and needs no new column).
- **Hibernating / idle world:** `CoarseStep` receives `EventBudgetMilli` in its logged inputs
  (`coarse-step` §1) and draws at most `⌊EventBudgetMilli × n / 1000⌋` pulls.

### 2. One deck

A coarse draw calls the same `storylet-selection` entry point with the same deck id the active world's
host uses, with the host id `world` and a `coarse` flag that restricts storylets to those whose content
marks them resolvable without a player choice (maintenance: a raid lost or repelled, a sector unrest).
**Never a second deck** (ideal §6.9). Until `storylet-selection` exists, the coarse slot draws nothing
and the digest shows no events — the budget still exists and is logged.

### 3. The ask filed to npc-story-events

- Add a hibernating/idle **host** (coarse, choice-free) to `world-events-host`, reading this budget.
- World-scoped story state survives a revisitable world: the map's *"World scope ends with the world"*
  (`npc-story-events-map.md:209`) no longer has an event to end on — a world never ends; a `fallen`
  world is still revisitable. Filed as an ask; not edited by this program (its map is another session's
  file).

## Acceptance (contract)

1. The budget is a pure lookup over `(state, outcome)`; all 9 pairs return per §1 (exhaustive test over a
   closed product).
2. The load-time ordering holds; a tuning file that violates it is rejected.
3. The number of event pulls in a coarse record never exceeds `⌊budget × n / 1000⌋`.
4. The deck id a coarse draw uses equals the active draw's deck id for the same world.
5. A world's budget changes only through its two columns (no other input).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/WorldEventBudgetTests.cs` (new): 1, 2, 5.
- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (extend): 3, 4 (with a fake selection
  seam until `storylet-selection` lands).

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
```

## Hard edges

- **`rpg_worlds` schema:** none.
- **Replay:** the coarse budget is a logged input; the full-step budget reads hashed outcome plus the
  constant `active` attention.
- **Corpse-cache tick key:** none.

## Dependencies

`world-state-vocabulary`, `coarse-step`, `world-victory` (outcome); external `storylet-selection`,
`world-events-host`. Consumed by `away-digest`.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `eventBudget.activeContestedMilli` | pulls per turn, per-mille | 1000 | `data/tuning/world-continuity.v1.json` |
| `eventBudget.activeWonMilli` | same | 600 | same |
| `eventBudget.hibernatingMilli` | same | 200 | same |
| `eventBudget.idleMilli` | same | 0 (maintenance only) | same |
| `eventBudget.fallenMilli` | same | 0 | same |

## Boundaries

- **Always:** one deck; budget logged for coarse records.
- **Ask first:** a player-choice storylet in a hibernating world.
- **Never:** a second deck; a background world busier than the active one.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldEventBudget.PullsPerTurnMilli` | `world-events-host`, `coarse-step` input builder |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine Events phase, coarse step, storylet selection (external).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: npc-story-events-map.md rows 185, 209, 215; see spec-world-state-vocabulary.md.
[x] decisions.md checked: phase order row — no phase added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: Events phase body.
[x] Surrounding sections read.
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the npc-story-events ask is listed in the map's contradictions.
[x] No population pinned; the 9-pair product is a closed vocabulary product.
[x] No cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one deck, one selection.
[x] No new cross-cutting rule beyond the load-time ordering check.
```

# Spec: `idle-world`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 9 of the
[world-continuity map](../world-continuity-map.md) (wave 3; depends on `world-warden`). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.1 (`idle`), §6.3, W3 (idle rides the
expedition wall clock, capped). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

A world with a stationed warden may be turned **idle**: it stops riding the End Turn counter and rides
the **expedition wall clock** instead — it records when it went idle and, at collect, resolves the whole
periods elapsed, inside a capped credited window (the Melvor shape, ideal §5). Idle resolution is
`CoarseStep` with a different clock source and the idle event row — never a second simulation and never
`TurnEngine.Step`. Leaving idle returns the world to `hibernating`.

## Scope and non-goals

**In scope:** the `idle` attention value's entry, collect and leave transitions; the idle anchor; the
periods computation (Server/Data side, like expeditions); the credited window; the "idle never pays more
than hibernating" rule.

**Not in scope:** what a period computes (`coarse-step`); the yield multiplier's curve
(`background-yield`); the warden (`world-warden`); the FE collect button (`multiverse-surface`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Wall-clock pro-rating at collect: `elapsed = min(tickCount, (now − dispatched) / tickMinutes)`, floored at already-logged battles | `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:98-101` |
| Dispatch stamps `dispatched_utc` / `due_utc`; the wall clock is read in Data/Server, never in Core | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:71-93` |
| Pure resolver over elapsed ticks | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-67` |
| The idle-shaped clock is one of the three the product allows | `docs/guide/the-loops.md:18`, `:20` (old worlds ride it — amended row) |

### Wiring gap

`turn_period_seconds` exists and is never read (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:26`).
Decided in `hibernation-clock` §1: tunables are the SSOT for balance numbers, so the idle period is a
tunable and this column stays reserved-unused.

### Real gap

No idle transition, no idle anchor, no world collect.

## Design

### 1. Store

`rpg_worlds.idle_anchor_utc TEXT` (nullable, additive): the wall-clock instant from which the next
collect counts. Set on entering idle and advanced at each collect by **whole periods only**, so a
partial period is never lost and never counted twice.

### 2. Transitions (all in one transaction each; order-independent where two are reachable)

| Transition | Preconditions | Writes |
|---|---|---|
| `hibernating → idle` (`POST /api/world/{worldId}/idle`) | the world has a stationed warden (`world-warden` §4); outcome is not `fallen` (`world-fall` §3) | catch up hibernation first (`coarse-step`, pending turns), then `state='idle'`, `idle_anchor_utc = now` |
| collect (`POST /api/world/{worldId}/collect`) | `state='idle'` | `periods = min(⌊(now − anchor) / idlePeriodSeconds⌋, idleCreditedWindowPeriods)`; if `periods > 0`: `CoarseStep(n = periods, Mode = Idle)`, then `anchor += periods × idlePeriodSeconds` — or `anchor = now` when the window capped it (the excess is forfeited, the same rule as `hibernation-clock` §3) |
| `idle → hibernating` (recall, or the warden is gone at a collect) | `state='idle'` | collect first, then `state='hibernating'`, `clock_mark = end_turns` (`hibernation-clock` §4 — idle time is never also credited as hibernating time), `idle_anchor_utc = NULL` |
| `idle → active` (select) | `state='idle'` | collect, then `SelectWorld` (`world-state-vocabulary` §4) |

Refusals, named: `idle.no-warden`, `idle.fallen`, `idle.not-idle`, `idle.not-hibernating`.

- **The wall clock is read by the Server/Data caller only**; `CoarseStep` receives an integer `n`. This
  is exactly the expedition split (`ExpeditionEndpoints.cs:98-101` reads the clock; the resolver does
  not).
- **Idempotent collect:** a retry after a crash resolves the same periods, because the anchor and the
  coarse record are written in the same transaction; a second collect in the same period finds
  `periods = 0` and writes nothing.
- **A clock that runs backwards** (skew) yields `periods = 0`, never a negative span.
- **A bounded route draw (answers `rift-trade-map.md` ask A2, round-4 reconciliation).** `rift-trade`
  `sleeping-endpoint` draws exports from an idle world's anchor warehouse through this collect, never by a
  second path: the collect accepts the route amounts as `CoarseInputs.RouteFlows` (`coarse-step` §1), each
  bounded by an amount the caller names; what the draw does not take stays credited in the warehouse. The
  draw is part of the same transaction as the anchor move and the coarse record, so a retry resolves the
  same periods and draws the same amounts (the idempotency above), and a draw on a world with
  `periods = 0` moves nothing.

### 3. Idle never pays more than hibernating

Per period, the idle yield multiplier is **≤** the hibernating multiplier for the same world and the same
hibernating count (`background-yield` owns both values; this module asserts the inequality at load and in
a test). Idle's events row is *maintenance only* (`world-event-budget`). Upkeep is not reduced
(`coarse-step` §2). So stationing a warden buys **protection and wall-clock progress while you play
elsewhere**, not a better rate (ideal §3.3).

### 4. Replay

Idle resolution appends an ordinary coarse record (`record_kind='coarse'`, its `span` = periods,
`Mode = Idle` in the logged inputs), so replay is `coarse-step` §4 unchanged. The wall-clock instants are
**not** replay inputs — only `n` is — so replay never reads a clock.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | expedition wall-clock pattern; pure resolver shape | reused |
| Wiring gap | `turn_period_seconds` never read | left reserved (tunable is the SSOT) |
| Real gap | idle transitions, anchor, collect | §1–§2 |

## Acceptance (contract)

1. Entering idle without a stationed warden, or on a fallen world, is refused with a named reason.
2. Credited periods never exceed `idleCreditedWindowPeriods`; excess is forfeited and reported.
3. Resolution is pure over `(world, seed, periods, stamp, inputs)` — the same function as a hibernating
   catch-up (asserted by calling `CoarseStep.Run` in the test, not a copy).
4. A collect is idempotent: a retry resolves the same periods; a second collect in the same period writes
   nothing.
5. Idle never pays more per period than hibernating for the same world (load-time check + test).
6. Leaving idle never double-credits: hibernating pending after leaving starts at 0.
7. Clock skew backwards yields 0 periods.

## Test plan and verification boundary

- `tests/FusionRpg.Data.Tests/WorldIdleTests.cs` (new, in memory, injected `utcNow` as the expedition
  store tests do): 1, 2, 4, 6, 7.
- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (extend): 3, 5.
- `tests/FusionRpg.Server.Tests/WorldIdleEndpointTests.cs` (new): routes and reasons.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
```

## Hard edges

- **`rpg_worlds` schema:** one nullable column (`idle_anchor_utc`).
- **Replay:** unchanged (coarse records).
- **Corpse-cache tick key:** idle collects never tick decay (only End Turn does, `hibernation-clock` §5).

## Dependencies

`world-warden` (entry condition), `coarse-step`, `hibernation-clock`, `world-state-vocabulary`. Consumed
by `away-digest`, `multiverse-surface`.

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `idlePeriodSeconds` | seconds per period | 3600 | `data/tuning/world-continuity.v1.json` |
| `idleCreditedWindowPeriods` | periods (structural bound, §11.4 row, commented) | 24 (the Melvor 24 h window, ideal §5) | same |

## Boundaries

- **Always:** clock read outside Core; whole periods only; collect before any leave.
- **Ask first:** idle without a warden.
- **Never:** `TurnEngine.Step` on an idle world; a second resolver; a rate above hibernating.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| idle / collect / recall routes and reasons | `multiverse-surface` |
| idle coarse records (`Mode = Idle`) | `away-digest` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store, expeditions (pattern only), coarse step.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; the-loops.md clock table (as amended).
[x] decisions.md checked: no lock on idle worlds.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: expedition pro-rating and floor, dispatch stamps, resolver signature.
[x] Surrounding sections read (the expedition clock-skew comment).
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted: no fourth clock (the-loops.md row).
[x] Corrections propagated.
[x] No population pinned.
[x] No cache.
[x] Order-independent: recall vs collect, select vs collect — each collects first.
[x] No actor magnitude produced (the warden term is world-warden's).
[x] No SOLID fork: idle is CoarseStep with another clock source.
[x] Rule "no wall clock in Core" is the existing determinism guard.
```

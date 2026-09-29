# Spec: `sleeping-endpoint`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19). Module 5 of `rift-trade`, wave 3. Every `file:line` below was opened this session.
Docs only. **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make routes work when one end is **not** the active world — the main case, since exactly one map world per save
is active. A hibernating end exports and imports inside the `CoarseStep` `world-continuity` already schedules; an
idle end exports through a bounded idle draw and imports at its next idle resolution. No route ever causes a
step that would not otherwise run.

Success looks like: the player stands in world B for 30 End Turns while old world A hibernates with a route to
B. Nothing steps A. When A is next coarse-stepped (a visit or the background budget), one closed-form drain
computes A's exports over those turns, ledgered as one consignment per good, due in B after the crossing's
transit; B's next full step receives them.

## Scope and non-goals

**In scope:** the pure export and import functions a `CoarseStep` calls; the bounded idle draw per End Turn for
an idle source; arrivals into a sleeping world as inputs to its next resolution; the logged form of all three.

**Not in scope:** the coarse step itself, its scheduler, its background multiplier and warehouse landing
(`world-continuity` `coarse-step`, `background-yield`); the idle resolver and its window (`idle-world`); fallen
worlds and lost anchors (`endpoint-loss`); the crossing ledger itself (`crossing-handoff`).

## Locked anchors

- **Never step N full worlds per End Turn** (world-continuity ideal §3.2). A route is an **input** to a
  resolution that was going to run anyway, never a reason to run one.
- **Leaving must never pay better than staying** (ideal §3.3). A route adds no production; it collects what the
  background multiplier already made, at a loss.
- **Background yield is collected, never auto-banked** (ideal §6.6): a coarse or idle path writes no wallet.
- **Determinism:** a coarse step is a pure closed form of `(summary, seed, n, stamp, inputs)`
  (`world-continuity-map.md` module 6); route exports and imports are part of `inputs`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Lazy, pure idle resolution: dispatch stamps times, resolution clamps elapsed ticks at collect | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61-67`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:71-93` |
| `catch_up_cap` and `turn_period_seconds` columns exist and are never read | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:26-27` |
| `Step` is pure over one world's state and commands — the rule functions `CoarseStep` composes | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157` |

### Wiring gap

| Inert | Evidence | Owner |
|---|---|---|
| Nothing reads `catch_up_cap` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:27` | `world-continuity` `hibernation-clock` |

### Real gap

Everything: there is no coarse step, no idle world, no background yield yet. This module specifies the route's
share of each, against the approved `world-continuity` map.

## Design

### 1. Hibernating source (export inside `CoarseStep`)

When `world-continuity` runs `CoarseStep` for world a over `n` pending turns (already capped by `catch_up_cap`)
at save counter `C`, the store passes, for each live route whose source is a, the window payload `rift-route`
builds (route, anchor, goods, shares, far-end row) as part of `inputs`. `CoarseStep` calls:

```
SleepingEndpoint.Exports(stock0, landingPerTurn, n, nearCap, farCap, shares, lossMilli) →
    per good: departed, lost
where
    available   = stock0 + landingPerTurn × n                 // anchor-warehouse figures from CoarseStep's own closed form
    routeCapN   = crossing-leg allocation of min(nearCap, farCap) × n
    departed_g  = min(share_g × n, routeCapN share of g, available_g)
    lost_g      = crossing-leg loss of departed_g
```

- **Units (audit 2026-09-20):** `nearCap` and `farCap` are end capacities in flat load units, each at its own
  anchor's scale (`crossing-anchor` §3), and `routeCapN share of g` is converted to a quantity with
  `crossing-leg` §1's per-end `loadOf` rule — never by comparing a quantity with a load. `share_g × n` and
  `cap × n` are `checked` `long`, widened before multiplying.
- `stock0` and `landingPerTurn` are the anchor warehouse's stock at wake and the background yield `CoarseStep`
  lands **in the anchor's own warehouse** per turn. Whether goods produced elsewhere in the hibernating world
  reach the anchor during a coarse step is `coarse-step`'s decision, not this module's (ask A1). Until it
  decides otherwise, a sleeping route drains only its anchor.
- The warehouse halt and waste after the drain stay inside `CoarseStep`'s closed form: it subtracts `departed`
  before applying its own capacity rule.
- One consignment per `(route, C, good)`, `depart_counter = C`, `arrive_counter = C + crossing.transitTurns`.
  **No back-dating:** a coarse drain never pretends goods left in the past. This delays goods relative to an
  active source, which is the direction "leaving never pays better" requires. *(Correction to the map's draft,
  which ledgered each export "with the arrival counter it would have had"; that would cost one row per pending
  turn and break the closed form.)*
- Cost is a function of routes × goods, never of `n`.

### 2. Hibernating destination (import inside `CoarseStep`)

The same resolution passes every consignment due into a's anchors (`arrive_counter ≤ C`, positive balance). The
coarse step delivers them into the anchor warehouse up to `endCapacity × n` (load units), split pro rata by
load at this anchor's scale as `crossing-handoff` does, capped by warehouse capacity (overflow wastes by the delivery rule); the rest stays
queued. Nothing it delivers is banked: a hibernating world's banking step does not run (`background-yield`).

### 3. Idle source (bounded draw per End Turn)

An idle world does not coarse-step; it resolves on the expedition wall clock at collect
(`world-continuity` `idle-world`). A route from an idle world draws through idle-world's **bounded collect**
(ask A2): on each End Turn of the active world, inside its commit transaction, for each live route whose source
is idle, the store requests at most `min(Σ shares, routeCap)` of each good from the idle world's credited window.
Idle-world resolves the elapsed wall-clock periods it has not yet resolved (pure, as expeditions do), hands back
up to the requested amount and keeps the remainder credited inside its capped window. The draw is recorded in the
idle world's own idle record (so the idle world replays), and the store writes one consignment per
`(route, C, good)`. The draw is idempotent on `(route, C)`.

This runs no `Step` and no `CoarseStep`; its cost is routes × goods per End Turn.

### 4. Idle destination

Due consignments into an idle world's anchor land at its next idle resolution — a player collect or an idle
draw by one of its own outbound routes — as an input to that resolution, with the same pro-rata, capacity and
waste rules as Design 2.

### 5. Past-due arrivals

An arrival whose counter has already passed lands at the next resolution of its world, in that resolution, never
in a past turn and never twice (the event key includes the resolution counter).

## Tunables

None owned here. `catch_up_cap`, the background multiplier and the idle window are `world-continuity`'s
(`data/tuning/world-continuity.v1.json`, new); crossing numbers are `crossing-leg`'s and `crossing-anchor`'s.

## Numeric types

`long`, `checked`; `share × n` and `cap × n` widen before multiplying (`n` is bounded by `catch_up_cap`, a
structural bound with its own `ssot-power-scale.md` §11 row owed by `hibernation-clock`).

## Contract-level acceptance

1. An End Turn in the active world performs **zero** `Step` or `CoarseStep` calls on any other world because a
   route exists — asserted by counting calls through an injected probe, not by timing.
2. **Split invariance:** coarse-stepping `a` then `b` turns departs the same total per good as `a + b` at once
   when landing is linear and no warehouse halt binds; crossing loss differs by at most one unit per good per
   extra split (integer division), and the test states that bound.
3. **Closed form:** the export function's operation count does not depend on `n` (asserted structurally).
4. Exports never exceed `stock0 + landingPerTurn × n` (no route-made goods).
5. **Leaving never pays better:** for the same world, route and `n`, exports while hibernating ≤ exports while
   active over `n` full steps (property test over the background multiplier range).
6. Imports into a sleeping world never credit a wallet or material ledger (no banking fact is emitted).
7. An arrival whose counter is past lands at the next resolution, never earlier, never twice.
8. An idle draw never exceeds the idle world's credited window; a retried commit draws nothing more.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Export/import functions, split invariance, closed form, leaving-never-pays | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift, World/Turn) |
| No extra steps per End Turn; idle draw idempotency; coarse inputs logged | `gk-core/tests/FusionRpg.Data.Tests` (in memory) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
python gk-core/scripts/audit-overflow.py --targets A3
```

Crosses Core and Data: full suite once at module end.

## Hard edges

- **Always:** compute inside the resolution that was going to run; log every input; closed form.
- **Ask first:** letting a hibernating world's lane flow feed the anchor (that is `coarse-step`'s call, ask A1).
- **Never:** schedule, force or speed up a coarse step or idle collect because of a route; per-turn loops over `n`;
  a wall-clock read in Core; a banking fact from a sleeping world.

## Dependencies

| Consumes | From |
|---|---|
| `CoarseStep` with an `inputs` parameter; per-warehouse landing | `world-continuity` `coarse-step`, `background-yield` (ask A1) |
| Bounded, idempotent idle collect | `world-continuity` `idle-world` (ask A2) |
| Save counter, `catch_up_cap` | `world-continuity` `hibernation-clock` |
| Window payload; allocation and loss; ledger | `rift-route`, `crossing-leg`, `crossing-handoff` |

| Exposes | To |
|---|---|
| `SleepingEndpoint.Exports` / `Imports` (pure) | `world-continuity` `coarse-step` (caller) |
| Consignments written from sleeping resolutions | `endpoint-loss`, `rift-facts` |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/SleepingEndpoint.cs   NEW — Exports, Imports (pure)
src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs              MODIFIED — coarse inputs, idle draw, consignments
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (coarse step inputs), idle clock pattern (expeditions), economy
    (background yield, warehouses), performance (never step N worlds).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: as spec-rift-route.md; world-continuity-map modules 2, 6, 9, 11 in full;
    world-continuity-ideal §3, §6.3, §6.6.
[x] decisions.md: no lock on sleeping routes.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: the expedition resolver's clamp; the unread catch_up_cap.
[x] Read surrounding sections: world-continuity coarse-step and idle-world acceptance.
[x] Constraints tested: none claimed; split invariance is stated with its rounding bound, not
    assumed exact.
[x] No §2 invariant contradicted: no fourth clock; determinism; perf rule 10 (no extra steps).
[x] Corrections propagated: no back-dating of coarse exports; the map is corrected.
[x] No population count pinned.
[x] Event-refreshed cache: none.
[x] Orderings: coarse split a+b vs a,b is tested both ways.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: coarse-step and idle-world own their resolutions; this module
    only supplies pure functions and inputs.
[ ] Registry row: "no Step/CoarseStep caused by a route" becomes an invariants row with its probe
    test when built (named by the 2026-09-20 audit: `rift-no-extra-world-step`).
```

## Audit 2026-09-20

Fixed here: capacities and shares are now stated in load units with the per-end `loadOf` rule (the same
correction as `crossing-leg` §1), and the import split follows `crossing-handoff`'s load-based split. Checked and
clean: no step is caused by a route (probe-counted); closed form independent of `n`; no back-dating; no banking
fact from a sleeping world; `n` is bounded by `catch_up_cap`, whose §11 row `hibernation-clock` owes.
**Verification boundary:** the `core-world-logistics-rift` owner boundary (`spec-crossing-anchor.md`
*Audit 2026-09-20*); Data tests in memory; the full suite once at module end.

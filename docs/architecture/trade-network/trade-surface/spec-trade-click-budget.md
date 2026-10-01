# Spec: `trade-click-budget`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 12, wave 5). Not a UI-gate module: it adds tests only. Every `file:line` below
was opened this session. Docs only.

## Objective

The counted acceptance the umbrella asks for (trade-network ideal §11 row 8, *"a click-budget acceptance
criterion"*), in the form world-notify already proved: each budget row is a test that counts user events,
so a later trade surface that raises a row's cost fails the suite.

## Locked anchors

- **The shape is shipped:** `web/fusion-rpg-web/src/stages/world/notify/clickBudget.test.tsx:50,59,75,85`
  counts four rows (0 clicks routine, 1 to act, 0 per item to clear, 1 to re-route a category).
- **Shape B** (ideal D2): a steady-state trade turn needs no trade input.
- Budgets are **structural presentation limits**, not tunables: a balance pass never changes them.

## What already exists

| Finding | Evidence |
|---|---|
| Counted click-budget tests over the rail | `clickBudget.test.tsx:50` (row 1), `:59` (row 2), `:75` (row 3), `:85` (row 4) |
| Rail flush on an advancing commit (row 1's mechanism) | `gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts:18-23` |

Real gap: no trade surface exists to count.

## Design — the budget, stated

| Row | Scenario | Budget (user events beyond End Turn) | Surfaces exercised |
|---|---|---|---|
| T1 | Steady-state trade turn: goods bank, nothing lost or stuck | **0** | status strip (quiet), no trade notification (`trade-notify` quiet rule) |
| T2 | Answer a forecast throttle from the stage | **≤ 2** (open the forecast chip or nag, pick an answer) | `throttle-forecast` |
| T3 | Answer a forecast throttle from an open `trade` block | **1** (pick the answer) | `trade-panel` forecast row |
| T4 | Re-route a trade notification category | **1** (inherited row 4) | `trade-notify` + rail |
| T5 | Read why goods were lost this turn | **1** (select the status strip) | `trade-status` attribution |
| T6 | Switch the map to trade flow | **1** (key `7` or the picker) — **0** when a hub or caravan is selected (auto-activation) | `flow-lens` |

T2/T3 apply to every throttle, **including the teaching throttle** since round 4 ([decisions-round-4.md](../decisions-round-4.md) Q3): its
`no-path` row now carries the `build-feature` answer, *"build a Counting House"* (`trade-unlock` §3), so it costs
≤ 2 from the stage like any throttle. When no legion stands in the sector, the first click sends one and
the build is one more click on a later turn — counted as that later turn's T2, never folded into this one.

Each row is a vitest test that mounts the real surfaces with fixture data, drives the scenario with user
events only, and asserts the event count equals the budget (not ≤ a looser bound, so an improvement is a
deliberate budget change).

## Contract exposed

Six budget rows, each a test id `trade-click-budget/T<n>`. A change to a budget is a reviewed edit of
this spec.

## Acceptance (contract level)

1. Each row T1–T6 exists as a test that counts user events and passes against the built surfaces.
2. A fixture change that adds one required click to any row fails that row.
3. T1 asserts zero trade drafts reach the rail and the strip shows the quiet sentence.

## Test plan and verification boundary

Vitest only. **Gap, stated:** `gk-core/scripts/verification-boundaries.v1.json` has no `web/` path (grep count 0)
and its `projects` map is `.csproj`-only, so `verify-change.py` cannot select these tests; report it,
never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
Lands last: every counted surface must exist. A row whose surface is blocked (e.g. T6 if the seventh lens
edit is refused) is marked pending with its blocker, never deleted.

## Dependencies

`trade-status`, `throttle-forecast`, `trade-panel`, `flow-lens`, `trade-notify`, `treaty-screen` (no row
yet: diplomacy is a standing decision, not a per-turn cost).

## Boundaries

- **Always:** count user events; equal, not ≤.
- **Ask first:** raising any budget.
- **Never:** a budget row that needs a hard block or a band-3 open.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: FE tests over world stage surfaces.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: clickBudget.test.tsx rows, GG-53, trade-surface-map §6.12.
[x] decisions.md: Game GUI (:110).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: the four shipped rows and the flush.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: T2/T3 scope vs the teaching throttle stated here and in trade-unlock.
[x] No population pinned: budgets are declarations with a reason.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path.
[x] Registry row: the budget tests are the guard; a registry row is added when they land.
[x] Round 4 reconciliation (2026-09-19): the teaching throttle joins T2/T3 (Q3 build answer); map S5 superseded.
```

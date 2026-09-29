# Spec: `trade-trigger-reachability`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 6, wave 3). Every `file:line` below was opened this session. Docs only.

## Objective

Prove every trade trigger can actually happen in play. For each fact kind in `trade-fact-kinds` and each
value of each leaf in `trade-predicates`, a fixture world driven **only by real, admitted world commands**
reaches a state where the fact is written or the leaf is true, within a stated turn bound. A preflight rule
then refuses any trade storylet whose eligibility needs a leaf value no fixture reaches, so the corpus
cannot hold a storylet that can never fire.

## Locked anchors

- **No debug fabrication** ([live-probe-standard.md](../../../contributing/live-probe-standard.md): a debug API
  may trigger a real operation, never fabricate its result). Fixtures submit commands through the same
  admission path a player's order takes (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs`).
- **Join closure over two closed vocabularies** — declarations, not populations (validation-ssot). No test
  counts storylets.
- **Preflight is the engine's.** The rule is filed on npc-story-events' storylet preflight
  (`storylet-contract`), the successor of the Delve's preflight.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Load-time rule validation in the event catalog (the preflight precedent) | `gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:93-129` |
| The command admission path | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs` (file) |
| Shipped templates to drive | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:15-18` (`first-light`, `two-hearths`) |

### Real gap

No trade facts or leaves; no many-faction fixture (counterparties relies on `trade-foundation`
`synthetic-graph`).

## Design

### 1. The reachability matrix

A test table keyed by `(factKind)` and `(leafId, value)`:

```csharp
// tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeTriggerReachabilityTests.cs (new)
public sealed record ReachabilityCase(string Trigger, string FixtureId, IReadOnlyList<WorldCommand> Script,
                                      int TurnBound, Func<WorldState, IStoryFacts, bool> Holds);
```

Each case builds its fixture (a shipped template or `trade-foundation`'s synthetic graph), commits the
scripted commands turn by turn through the real admission and commit path, and asserts `Holds` becomes
true at or before `TurnBound`. The facts side reads the story ledger through `ListStoryFacts` after each
commit (Data test), so a fact written by `trade-fact-source` is proved end to end.

### 2. Closure

A meta-test joins the matrix to the declared vocabularies: every trade fact kind and every value of every
trade leaf (e.g. each band ordinal of `PriceBandIs`, each access ordinal of `AccessIs`) has at least one
case. A kind or value whose producer has not landed is listed **pending** with its blocker, and the
meta-test reports pending entries without passing them.

### 2a. Round-4 cases ([decisions-round-4.md](../decisions-round-4.md))

Two cases replace `exchange` ask E-A9 (a band-raising storylet, superseded by round 4):

- **`AccessIs(clan, market)`** — on a first-world template with a clan (round 4 Q5 puts one on both
  shipped templates), a script of admitted commands builds the player's first Trading Post (on a
  `Wildland` or `Market` slot, round 5 B1 — anywhere in the world counts, round 5 B4); the leaf is
  false the turn before the post is active and true the turn it is, with the clan still at `wary`.
- **`trade.price.*` at a clan hub** — the same script then files an `order-set` at the clan's seeded
  tier-1 hub and the fill writes the settlement records a price-band fact can follow.

Both use only admitted commands (`build`, `order-set`); a Trading Post fabricated by a debug entry point
would prove nothing (the live-probe scope rule).

### 3. The preflight rule

Filed on npc `storylet-contract`'s preflight: a storylet hosted on a trade host whose eligibility tree
requires (as a direct `And` child, the engine's own priority test) a trade leaf value marked pending or
absent from the matrix is refused at load with `storylet.unreachable-trade-trigger`, naming the leaf and
value.

## Contract exposed

The matrix (test data), the closure meta-test, the preflight refusal code. Consumers: CI; narrative-seed
(its generated trade storylets must pass preflight).

## Acceptance (contract level)

1. Every trade fact kind and every trade leaf value has a passing case or an explicit pending entry.
2. No case uses a debug endpoint or writes state outside admitted commands (a scan of the test sources for
   debug entry points).
3. The preflight refuses a fixture storylet whose only condition is an unreachable leaf value, and accepts
   one whose condition is reachable.

## Test plan and verification boundary

`FusionRpg.Core.Tests` (state leaves, admission) and `FusionRpg.Data.Tests` (facts through the commit) —
`core-tests-fallback`, `data-tests-fallback`.

## Hard edges

- Pending entries are expected while producers land; none may be deleted to go green.
- The preflight rule is npc's code; this module supplies its data and tests.

## Dependencies

`trade-fact-source`, `trade-predicates`, `trade-fact-kinds`; `trade-foundation` `synthetic-graph`; npc
`storylet-contract` (preflight).

## Boundaries

- **Always:** real commands; closure over declarations.
- **Ask first:** a turn bound above the fixture's natural horizon.
- **Never:** a fabricated fact; counting storylets.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world commands/admission, story ledger (read), storylet preflight.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: live-probe-standard rule (CLAUDE.md/AGENTS.md restatement), validation-ssot rule, trade-stories-map §6.6.
[x] decisions.md: no lock.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: catalog validation, admission file, template ids.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none needed.
[x] No population pinned.
[x] No cache.
[x] Ordering: each case asserts a turn bound, not a sequence of intermediate states.
[x] No actor magnitude.
[x] No parallel path.
[x] Registry row: the closure meta-test is the guard; row added when built.
[x] Round 4 reconciliation (2026-09-19): §2a adds the Trading Post reachability cases (E-A9 replaced).
[x] Round 5 (2026-09-20): B1/B4 noted on the Trading Post case; no case added (B3's yard gates
    caravans, not AccessIs).
```

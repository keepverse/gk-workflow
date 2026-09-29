# Spec: `trade-failure-branches`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 9, wave 4). Every `file:line` below was opened this session. Docs only.

## Objective

Trade's failure branches (trade-network ideal §14b: *"a lost hub opens a failure-branch questline"*).
Losing a trade hub or depot, or being cut off by an embargo, writes a failure fact that makes **priority
storylets** eligible: a questline to retake or replace the hub, a character who can reopen the route, a
branch place with a way back. It offers content; it never adds a second penalty.

## Locked anchors

- **Failure branches are npc-story-events'** (`failure-branches`; npc-story-events-ideal §6.8): a failure
  writes a fact; the fact makes priority storylets eligible; *"No failure branch takes back what the game's
  own rules let you keep … It offers content; it never adds a second penalty on top of the loss."* This
  module supplies trade's failure facts and the arc asks; it builds no branch engine.
- **The questline is an arc** from narrative-seed's `arc-pipeline` (3–5 linked storylets with a persistent
  cast), requested through `trade-storylet-supply`.
- **Priority, not luck.** An eligible consequence storylet pre-empts pool storylets on its host and
  bypasses the fire roll ([spec-storylet-selection.md](../../npc-story-events/spec-storylet-selection.md) §2,
  §4) — subject to the per-empire budget (`trade-story-pacing`).
- **Catch-up for the leader is `trade-ai`'s** (`interdiction`), not this module's.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Capture happens in one place (`ClaimResolver` in Snapshot) | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:29-31` (class and `Run`) |
| Report lines with sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |

### Real gap

No failure facts, no failure-branches engine (npc, unbuilt), no trade structures to lose.

## Design

### 1. Trade's failure facts

From `trade-fact-kinds`: `trade.hub.lost`, `trade.depot.lost` (a claim of a sector holding that structure,
subject the sector, written for the loser), and `trade.embargo.set` read as a failure when it closes the
faction's last `market`-or-better access to a good it was trading (`attrs.closesLastAccess = true`, set by
`trade-fact-source` from `trade-access` before and after). npc's `sector.lost` is written for the same
claim; trade's fact is the more specific one and a storylet chooses which to react to.

### 2. What becomes eligible

Consequence storylets whose eligibility requires the failure (via `StoryFactWithin`, the generic recency
leaf requested by `trade-predicates`, or a flag the first link sets), hosted on:

| Failure | Host | Branch content (arc shape, narrative-seed's) |
|---|---|---|
| hub lost | `world.trade-turn` (the loser no longer holds the hub) | retake it, or found a replacement hub elsewhere; a `trader` character who lost their stall |
| depot lost | `world.trade-turn` | rebuild the supply line; an `envoy` offering an alternative route |
| last access closed by embargo | `world.trade-turn` | reopen the route: a smuggler character, a treaty path through a third party (`bloc`) |

### 3. No second penalty

The branch's outcomes route only through npc's legal paths (npc-story-events-ideal §6.9) and draw rewards
and costs from the host budget. Nothing in the branch debits a stock the loss did not already debit.

## Contract exposed

Failure semantics for three trade facts; arc coverage asks (via `trade-storylet-supply`). Consumer: npc
`failure-branches`.

## Acceptance (contract level)

1. **No second penalty:** a test compares the player's stocks, roster and souls before and after a branch's
   first link opens and finds no debit caused by it.
2. **Reachable:** each trade failure fact has a reachability case (`trade-trigger-reachability`).
3. **Priority:** an eligible branch storylet is chosen over pool storylets on its host within the budget.
4. **Loser only:** the failure fact is written for the losing faction's save only (fog + audience).
5. **Embargo precision:** `closesLastAccess` is true only when access to some traded good drops below
   `market` for every hub the faction could reach.

## Test plan and verification boundary

Core tests over fixture claims and embargoes — `core-fallback`; ledger writes — `data-fallback`.

## Hard edges

- Blocked on npc `failure-branches`, `spine-progress` (tier order) and narrative-seed arcs.

## Dependencies

`trade-fact-source`, `trade-fact-kinds`, `trade-predicates`, `trade-story-pacing`, `trade-storylet-supply`;
npc-story-events `failure-branches`, `storylet-selection`; `exchange` `trade-access`; narrative-seed
`arc-pipeline`.

## Boundaries

- **Always:** content, not penalty; priority through the engine.
- **Ask first:** a branch that grants something the loss took (it would undo a rule).
- **Never:** a trade-local branch engine; a debit on branch open.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: failure branches (npc), story ledger, claims, access (read).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: npc-story-events-ideal §6.8/§6.9, spec-storylet-selection §2/§4, trade-stories-map §6.9.
[x] decisions.md: no lock.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: ClaimResolver entry, TurnReportEntry.
[x] Surrounding sections read.
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: trade.treaty.broken replaced by relation-facts' treaty.broken + embargo semantics.
[x] No population pinned.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: npc's branch engine, narrative-seed's arcs.
[x] Registry row: none new (npc's no-second-penalty rule covers it).
```

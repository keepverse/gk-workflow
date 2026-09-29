# Spec: `endpoint-loss`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19). Module 6 of `rift-trade`, wave 3. Every `file:line` below was opened this session.
Docs only. **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Say exactly what a route does when one of its ends stops working — the anchor sector is captured, the Rift
Anchor is destroyed, its world loses its last working Grand Exchange (round 4,
[../decisions-round-4.md](../decisions-round-4.md) B), or the whole world falls — so that no good is created, none silently disappears, and nothing is left
as a free store the player can draw on later.

Success looks like: 95 goods are in the crossing toward world B when B's anchor is captured. B's next resolution
refuses them; they return to A's anchor at A's next resolution with no second loss; the route sends nothing
further until B's anchor is retaken, then resumes without delivering anything retroactively.

## Scope and non-goals

**In scope:** the per-resolution derivation "can this route carry now?"; suspension of departures; refusal of
arrivals at a non-working anchor; returns to the origin; stranded returns; terminal loss when a route is cleared
with no working end.

**Not in scope:** what happens to goods already delivered into a captured anchor's warehouse (`sector-yield`'s
capture rule); the world's own fall (`world-continuity` `world-fall`); reclaim (`world-reclaim`, reserved).

## Locked anchors

- **No stranded faucet, no re-creation:** a return is not a second crossing; crossing loss was taken once, at
  departure (`crossing-leg`).
- **Validity is derived, not stored** (`rift-route` Design 1): there is no "suspended" flag.
- **Order-independent** where real play can order events either way (DESIGN-GATE §2.16 corollary).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Sector capture and binding clear | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:101-107` |
| The only `UPDATE rpg_worlds` is the turn advance; nothing sets a non-active state or an outcome | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:687-690` |

### Wiring gap

| Inert | Evidence | Owner |
|---|---|---|
| No `fallen` outcome exists; a world cannot fall | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:687-690` (the only update) | `world-continuity` `world-state-vocabulary`, `world-fall` |

### Real gap

The carry derivation, suspension, refusal, return, stranding and terminal loss.

## Design

### 1. Can the route carry at this resolution?

At every resolution of an endpoint world W (full step, coarse step, idle resolution), for each live route with an
end in W:

```
nearOk = crossing-anchor IsWorking(W, nearAnchor) && outcome(W) != fallen
farOk  = far-end view row: working && outcome != fallen          // logged in the route window
carry  = nearOk && farOk
```

`nearOk` is computed from W's own state inside its resolution. `farOk` comes from the far-end view
`crossing-anchor` publishes, copied into the logged window, so W's replay sees the same value. The view is a
projection with an enumerated trigger set (`crossing-anchor` Design 4), not a cache that can go stale silently.
*(Correction to the map's draft, which said validity is "never cached": the far half cannot be computed without
reading the other world, so it is a projection — refreshed by every resolution of its own world and
cross-checked in tests.)*

When `carry` is false at a source resolution: nothing departs on that route, and one `rift.suspend` entry names
the reason (closed set: `anchor.not-held`, `anchor.no-anchor`, `anchor.anchor-building`,
`anchor.no-grand-exchange`, `world.fallen`, each prefixed `near.` or `far.` — `crossing-anchor` §2; the
pre-round-4 `anchor.no-depot` and `anchor.depot-building` are replaced). A lost Grand Exchange suspends
exactly like a lost anchor: goods already in the crossing toward that world are refused at arrival and
return (§2), and the route resumes on the first resolution at which the world holds one again.

### 2. Refusal at arrival

When a destination resolution receives a due consignment (`crossing-handoff` Design 4) and its anchor is not
working, the step emits `RiftArrival(…, refused = balance)`. Post-step, the store appends a `refuse` event to the
consignment and writes a **return consignment** (leg `return`) from the refused anchor to the origin anchor,
`depart_counter = arrive_counter = ` this resolution's counter, with a `depart` event of the refused quantity and a
`loss` event of zero. The return does not cross again, so it loses nothing more.

### 3. Destinations that will never resolve again

A destination world whose outcome is `fallen` may not resolve for a long time (it is revisited only for reclaim).
So at the **origin's** resolution, the store converts every consignment due into a fallen world into a return,
exactly as Design 2, reading `fallen` from the far-end view (terminal: `world-fall` never reverses it, only
`world-reclaim` may). A hibernating or idle destination with a lost anchor is **not** handled this way: it
resolves lazily, and its own next resolution decides (Design 2), because its anchor may be retaken during its
own catch-up.

### 4. Returns and strands

A return consignment is due at the origin at its counter and arrives like any consignment. If the origin anchor
is working, the goods land there. If not, the return is **stranded**: its balance stays in the crossing, one
`rift.strand` entry is written, and it is offered again at each later origin resolution. It never bounces back
to the destination.

If the player **clears** a route while a stranded return has no working anchor at either end, its balance is lost.
The clear itself only records the intent; the loss is decided inside the origin world's next resolution (the
return is offered once more with a `clearing` flag, and if the origin anchor still is not working the step
emits the loss), so the report entry is written by the engine like every other: a `strand-lost` event and one
`logistics.loss` entry with cause `stranded`. This is the only way crossing goods are lost after departure, and it
is the player's choice.

### 5. Recovery

When an anchor is working again, the route carries from the next resolution. Consignments already returned stay
returned. Consignments still in the crossing and now due land at that resolution. Nothing is delivered for turns
that are past.

## Tunables

None. There is no loss rate here beyond `crossing-leg`'s; a strand never decays (it is not a store the player can
draw on: it can only land at its origin).

## Numeric types

`long`, `checked`.

## Contract-level acceptance

1. **Conservation per consignment pair:** refused quantity = the return consignment's `depart`; for a route whose
   destination anchor is lost, returned + lost at departure = departed toward it.
2. No anchor receives anything at a resolution where it is not working; a captured anchor's warehouse moves only by
   `sector-yield`'s capture rule.
3. A return is never delivered to the destination and never takes a second loss.
4. A stranded return lands at the first origin resolution where the origin anchor is working; it is lost only by a
   `clear` while neither end works (one `strand-lost` event, one report entry).
5. **Order-independent:** an anchor lost and its route cleared at the same resolution give the same final stocks
   and events in either order (both tested).
6. **Order-independent:** an anchor retaken and a consignment falling due at the same resolution deliver the same
   way whichever the fixture resolves first (both tested — the key-set edge is the anchor becoming working).
7. Retaking an anchor resumes departures at the next resolution and delivers nothing for past turns.
8. Every suspension reason is from the closed set; the set's size is pinned as a closed vocabulary with a reason.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Carry derivation, suspension reasons, refusal and return (pure step) | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| Return consignments, fallen-destination conversion, strand, clear-while-stranded | `gk-core/tests/FusionRpg.Data.Tests` (in memory) |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
```

## Hard edges

- **Always:** decide a refusal inside the destination's own resolution, except for a `fallen` destination.
- **Ask first:** a decay on stranded goods; routing a refused consignment to a different anchor.
- **Never:** a stored "suspended" flag; a second crossing loss on a return; a retroactive delivery; a return that
  lands anywhere but the origin anchor.

## Dependencies

| Consumes | From |
|---|---|
| `outcome`, `fallen` | `world-continuity` `world-state-vocabulary`, `world-fall` |
| `IsWorking`, far-end view | `crossing-anchor` |
| Consignments, events, arrivals | `crossing-handoff` |
| Sleeping resolutions | `sleeping-endpoint` |

| Exposes | To |
|---|---|
| Suspension, refusal, return and strand outcomes | `rift-facts` |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/EndpointLoss.cs   NEW — carry derivation, refusal (pure)
src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs          MODIFIED — return consignments, fallen conversion, strand-lost
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine, world states (continuity), crossing ledger.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: as spec-rift-route.md; world-continuity-map modules 1, 7.
[x] decisions.md: no lock on route loss.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: the only rpg_worlds update; capture in ClaimResolver.
[x] Read surrounding sections: world-fall's acceptance ("terminal for this program").
[x] Constraints tested: none claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: "never cached" corrected to "projection with triggers", here and in
    the map.
[x] No population count pinned: the reason set is a closed vocabulary.
[x] Event-refreshed cache: the far half reads crossing-anchor's view (its triggers are listed
    there); nothing new is cached here.
[x] Orderings: loss vs clear, retake vs due arrival — both tested both ways.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: sector capture stays sector-yield's; world fall stays
    world-continuity's.
[ ] Registry row: none new beyond crossing-handoff's.
```

## Audit 2026-09-20

Checked and clean: validity is derived per resolution (no stored flag); the far half reads `crossing-anchor`'s
projection, whose trigger set now includes the key-set shrink edge (T7); returns take no second loss and
re-create nothing; strands never decay and are lost only by the player's clear; both same-resolution orderings are
tested. **Verification boundary:** the `core-world-logistics-rift` owner boundary (`spec-crossing-anchor.md`
*Audit 2026-09-20*) for the Core half; Data tests in memory. The `fallen` wiring gap (`world-continuity`
`world-fall`) is named, not assumed.

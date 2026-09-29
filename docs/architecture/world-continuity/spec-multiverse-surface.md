# Spec: `multiverse-surface` (FE)

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 15 of the
[world-continuity map](../world-continuity-map.md) (wave 5; depends on `world-state-vocabulary`,
`advance-carry`, `away-digest`). Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §2,
§10 (how the multiverse map is drawn is undecided). **This spec is a contract for data and gates, not a
screen design: the screen is designed through `/idea-ui` first** (`docs/architecture/idea-ui-phase.md`),
per the DESIGN-GATE *Anything a player sees* and *Player menus* rows.

## Objective

The player can see their worlds and act on them: a list of the save's worlds with their label
(*active*, *developing*, *hibernating*, *idle*, *fallen*), select/switch, the advance dialog with the carry
limit, station a warden and turn a world idle or collect it, and the "while you were away" digest. All of
it is a **layer over the World stage**, never a new route (GG-1, `docs/architecture/game-gui-principles.md:38`).

## Scope and non-goals

**In scope:** the data each surface consumes and the server calls it makes; the gates (what is disabled
and the reason shown); the removal of the retired bind-warden confirm already scheduled by `world-warden`
§2 is **not** here — that module removes it.

**Not in scope:** the multiverse map's drawing (ideal §10 — `/idea-ui` decides); copy (authored catalog
rows, GG-62); trade routes between worlds (`rift-trade`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The web reads the active world header through the bus | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:584` |
| World stage shell, HUD, inspector, confirms, playback, notify folders | `gk-web/web/fusion-rpg-web/src/stages/world/` (`WorldStage.tsx`, `hud/`, `inspector/`, `confirms/`, `playback/`, `notify/`) |
| World-stage program's module ids for inspector, playback and confirms | `docs/architecture/world-stage-map.md:76`, `:82-83` |

### Real gap

No world list, no switch, no advance dialog, no idle/collect controls, no digest layer. The server
routes they call are this program's (`world-state-vocabulary` §4, `world-creation` §1, `advance-carry`
§1, `idle-world` §2, `coarse-step` §7).

## Design — the contract `/idea-ui` designs against

| Surface | Reads | Calls | Gate (disabled reason shown) |
|---|---|---|---|
| World list (a layer) | `GET /api/world/{playerId}/worlds` (new read: header rows with `state`, `outcome`, label, pending turns, idle periods due) | — | — |
| Switch | the list row | `POST /api/world/{worldId}/select` | `world.fallen` |
| Look at an old world | — | `POST /api/world/{worldId}/catch-up` when its view opens (a `GET` never writes, `coarse-step` §7) | — |
| Advance dialog | the carry **weight** budget for the current outcome and the load of what is picked so far (round 6 W1: Σ unit count × that unit type's `world.carry.capacity`, read from `advance-carry` §2 — never recomputed here); legions and their cargo; next-world preview (`WorldContinuityRules.NextWorld`) | files `depart` × k + `advance`, then End Turn (`advance-carry` §1) | `carry.limit`, `carry.goods-aboard` |
| Station warden | eligible legions (a commander-role member) | the ordinary `stance` order with `warden` (`world-warden` §4) | `warden.no-commander` (audit 2026-09-20: several warden legions per world are legal; the one-per-world refusal was withdrawn) |
| Idle / collect / recall | idle periods due, credited window | `POST …/idle`, `…/collect`, recall | `idle.no-warden`, `idle.fallen` |
| Digest layer | the coarse row's stored report (`away-digest`) | — | — |

- **Player vocabulary:** the five labels and *advance*, *warden*, *hibernating*, *idle*, *fallen* are
  glossary rows (`continuity-doc-amendment`); engine ids never reach the surface (GG-23).
- **Numbers state their meaning** (GG-46): "credited N of M turns", the yield multiplier as a share of
  active, the carry weight budget with the reason it is larger after a win, and the load picked so far.
- **Buy before build:** list, dialog and digest use the locked library set (`docs/design/tech-stack.md`);
  a multiverse *map* drawing, if `/idea-ui` wants one, uses the locked graph library before a hand-rolled
  one.

## Acceptance (contract)

Per the `/idea-ui` output, plus these fixed ones:

1. No new top-level route; every surface opens over the World stage.
2. Every disabled verb shows the server's reason verbatim through the authored copy catalog.
3. Opening a hibernating world's view triggers exactly one catch-up call; reopening it with no pending
   turns makes a call that writes nothing.
4. The advance dialog never lets the picked load pass the carry weight budget and shows why (round 6 W1),
   and it says plainly that **trade goods do not cross with an advance** — they cross by a `rift-trade` route
   (round 6 S2), with the `carry.goods-aboard` refusal explained in the player's words, never a raw code.

## Test plan and verification boundary

`npm test` (vitest, components and bus), `npm run build` (types), Playwright for the switch → catch-up →
digest path and the advance path, with agent-CV screenshots per the World map row's checkpoint rule.

```powershell
cd gk-web/web/fusion-rpg-web; npm test; npm run build; npm run test:e2e
```

## Hard edges

None on the server; the surface calls only routes other modules own.

## Dependencies

`world-state-vocabulary`, `advance-carry`, `away-digest`, `idle-world`, `world-warden`, `coarse-step`
(routes). `/idea-ui` (design, first).

## Boundaries

- **Always:** a layer over the stage; reasons verbatim; authored copy.
- **Ask first:** a separate multiverse stage (a new stage is explicit travel, GG-1 — `/idea-ui` decides).
- **Never:** a new route; engine ids on screen; a `GET` that writes.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world stage FE, bus.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[~] Read this session: game-gui-principles.md GG-1 heading only; NOT read: information-architecture.md,
    design/README.md, fe-game-foundation.md, gui-lego docs, idea-ui-phase.md in full. This spec is a
    data/gate contract; /idea-ui must read them before any screen design. Gap stated.
[x] decisions.md checked: GUI Lego row noted by title; not re-read.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: the bus read, the world stage folders.
[x] Surrounding sections read.
[ ] Constraint tested: none.
[x] No §2 invariant contradicted.
[x] Corrections propagated.
[x] No population pinned.
[x] Cache: the world list is server state (TanStack Query); its invalidation triggers are select,
    advance, catch-up, collect, End Turn — each named here for the /idea-ui spec to test. Audit
    2026-09-20 completed the set (DESIGN-GATE §2.16 — the key-set edge is a world entering the list):
    `begin` (first world), `idle` and recall (attention changes), and the End Turn's background
    catch-ups (a hibernating world's pending and outcome change with no action on that world). One test
    per trigger.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork.
[x] No new cross-cutting rule.
```

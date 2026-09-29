# Spec: `rift-route`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19, decisions Q1 and Q2); **reconciled with the round-4 owner decisions 2026-09-19**
([../decisions-round-4.md](../decisions-round-4.md): a route end is a **Rift Anchor** in a world holding a
**Grand Exchange** (B); system-issued commands go through **`trade-foundation`'s one shared path** (Q10)).
Module 1 of `rift-trade`, wave 1. Every `file:line` below was
opened this session on `features/mega-merge`. Docs only — no code is authorized by this file.
**Program vocabulary:** player text says *cross-world route* and *crossing*; `rift-trade` is the program id.
**House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

A player who holds two worlds can join a Rift Anchor in one to a Rift Anchor in the other and name which goods
cross, how much per End Turn, and in what priority. This module owns that **route record** and the two
player verbs that set and clear it, plus the one rule every later module relies on: **how a route's
instructions reach each world without either world reading the other.**

Success looks like: a route set between world A (active) and world B (hibernating) is a Data row owned by
the save and the empire; A's next End Turn carries, in A's own command log, one logged instruction for that
route; replaying A alone from its log reproduces A's hash; B is untouched until B next resolves.

## Scope and non-goals

**In scope:** the save-scoped route table; `set` and `clear` verbs on the server; admission (who may join
what); the **per-resolution route window** — the logged input each endpoint world receives at each of its
resolutions; the closed system-command kind that carries it; the route's lifecycle states.

**Not in scope:** anchor capacity (`crossing-anchor`); throughput, transit and loss arithmetic
(`crossing-leg`); moving goods and the crossing ledger (`crossing-handoff`); sleeping worlds
(`sleeping-endpoint`); suspension and return (`endpoint-loss`); the goods table (`crossing-goods`); report
kinds (`rift-facts`); any FE surface (a later `trade-surface` row).

## Locked anchors (owner decisions and map rules this spec does not reopen)

- **Q1 (owner, 2026-09-19): nothing physically crosses between worlds.** Each world's end of a route is a
  Rift Anchor staffed by a crew legion (round 4 B; the approval-time text said "a depot"); the crossing is
  lane-like flow. So a route never moves an entity, never
  files an advance, and never puts one world's goods into another world's hash.
- **One active world per save** (`world-continuity` `world-state-vocabulary`, approved). At most one end of
  any route steps per End Turn; the other resolves lazily.
- **Every cross-world effect is a logged input to the affected world** (`world-continuity-map.md` assumption
  4): a system-issued command for a full `Step`, a field of the coarse record for a `CoarseStep`, a field of
  the idle record for an idle collect.
- **A route belongs to one save and one empire** (map assumption 3); foreign trade stays `exchange` + `fleet`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Several worlds per save coexist, distinguished by `kind` and `parent_world_id` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:204-206` |
| `rpg_worlds.player_id` is the save: `SaveId`'s value is `players.id` (ruling R17) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:21-23`; `gk-core/src/FusionRpg.Core/Saves/SaveId.cs:5-12` |
| The human side of every world is the one faction of kind `Player` | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |
| The command log: one durable row per `(world, turn, commander, command)`, read in `(commander, seq)` order | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:21-33`, `:443-446` |
| The commit reads the turn's commands from that log inside its transaction, just before `Step` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:519`, `:539`, `:601` |
| Report re-derivation replays `Step` from the template and the command log, so a logged command is replayed | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:769-775` |
| Admission refuses an unknown kind and a commander that is not a faction of the world | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-30` |
| The kind vocabulary is one closed list | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:121-126` |
| The rule for a new table: empire-scoped tables are born Tier A `(save_id, empire_id, …)` | `docs/architecture/solid-enforcement/spec-save-identity.md:594-603` |

### Wiring gap

| Inert | Evidence | Owner |
|---|---|---|
| The "active world" is the first active map world by id, not a chosen one | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:416-429` | `world-continuity` `world-state-vocabulary` |
| No path files a command on behalf of the system: every command is admitted as some faction's order | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:26-30` | **`trade-foundation` `system-commands`** (round-4 Q10: *"System-issued world commands — one shared path, built in trade-foundation"*) — ask A7, retargeted and answered |

### Real gap (this module closes it)

The route table; the `set`/`clear` verbs and their admission; the `rift-window` system kind and the step that
files it; the route lifecycle.

## Design

### 1. The route record (Data, save- and empire-scoped, outside every world hash)

`rpg_rift_routes`, born Tier A:

| Column | Type | Meaning |
|---|---|---|
| `save_id` | `INTEGER` | `SaveId` (the `players.id` value) |
| `empire_id` | `TEXT` | The human empire of the save (`EmpireRef`) |
| `route_id` | `TEXT` | Stable id, unique per save |
| `a_world_id`, `a_sector_id` | `TEXT` | Source end: world and anchor sector |
| `b_world_id`, `b_sector_id` | `TEXT` | Destination end |
| `goods_json` | `TEXT` | Ordered list of `(goodId, sharePerTurn)`; list order is priority |
| `state` | `TEXT` | `open` \| `cleared` (closed vocabulary) |
| `set_counter`, `cleared_counter` | `INTEGER` | Save End Turn counter values (`hibernation-clock`) |

A route is **one-directional**. Two-way trade is two routes; this keeps every conservation equation
single-signed. `sharePerTurn` is a `long` in the good's own units; `0` is refused. Primary key
`(save_id, route_id)`; every read and write also filters by `empire_id` (the Tier A rule) — stated by the
2026-09-20 audit, which found the table had no key.

Suspension is **not** a stored state. Whether a route can carry this turn is derived at each resolution from
world states and anchor ownership (`endpoint-loss`), so there is no flag to forget to clear.

### 2. Verbs

`POST /api/world/rift-routes` (set) and `POST /api/world/rift-routes/{routeId}/clear`, in
`gk-core/src/FusionRpg.Server/WorldEndpoints.cs`, calling `RpgStore.SetRiftRoute` / `ClearRiftRoute`. The server holds
no SQL (`guard-dal.py`). Setting is idempotent on a client-supplied correlation id, the soul-ledger shape
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:684-695`).

Clearing stops **future departures only**. Goods already in the crossing finish their journey (or return, per
`endpoint-loss`). A cleared route is never reopened; the player sets a new one.

### 3. Admission (checked at set time, re-derived at every resolution)

Refused with a named reason, nothing written:

| Reason | Condition |
|---|---|
| `rift.same-world` | `a_world_id == b_world_id` |
| `rift.not-your-save` | either world's `player_id` is not the caller's save |
| `rift.not-a-map` | either world is not `kind='map'` (delves never trade) |
| `rift.not-stamped` | either world's stamp lacks `trade.riftTrade` (`trade-foundation` `world-stamp`, ask A4) |
| `rift.anchor-not-working:<reason>` | either anchor fails `CrossingAnchor.IsWorking` — not held, no Rift Anchor, anchor under construction, or no working Grand Exchange in that world (`crossing-anchor` §2; round 4) |
| `rift.good-refused:<id>` | a good fails `crossing-goods` |
| `rift.share-invalid` | a share ≤ 0 or a duplicate good |
| `rift.world-fallen` | either world's `outcome` is `fallen` |

Routes between **two sleeping worlds** are admitted: refusing them would suspend every route the moment the
player switches worlds. A hibernating or idle end is served by `sleeping-endpoint`.

### 4. How instructions reach a world: the per-resolution window

A world learns about its routes **only through a logged input at each of its own resolutions**, never through
stored per-world policy. At every resolution of world W:

- **Full `Step` (W active):** inside `CommitWorldTurn`'s transaction, after the barrier releases and before the
  command read at `RpgStore.WorldTurns.cs:539`, the store files one `rift-window` system command per open route
  whose **source** is W. Its payload: `routeId`, the source anchor sector, the ordered goods and shares, and the
  **far-end snapshot** `crossing-anchor` supplies (far capacity inputs, far held flag, far world outcome).
- **`CoarseStep` or idle collect (W sleeping):** the same payload is a field of that resolution's logged record
  (`sleeping-endpoint`).

Why a per-resolution window rather than a policy command filed once at `set`: a policy filed once would be
hashed state that must be invalidated when the far end changes — an edge-refreshed cache (DESIGN-GATE §2.16).
A window read fresh at every resolution has no trigger set to forget, costs one log row per route per
resolution, and makes every world's replay self-contained.

`rift-window` is a **system-only** kind: player and AI admission refuse it with `kind.system-only`. Its
`CommandId` is deterministic — `rift:w:<routeId>:<counter>`, with `routeId` bounded so the whole id stays inside
admission's 64-character bound (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:15`) — so a retried commit files nothing new
(`INSERT OR IGNORE` on the log's primary key, `RpgStore.WorldTurns.cs:30`). The filing path is the one
system-command path **`trade-foundation` `system-commands`** builds (round-4 Q10; ask A7, retargeted from `world-continuity`);
this module registers the kind in it and never adds a second filing path.

### 5. Lifecycle

`open` → (`clear`) → `cleared`. A route is **live** at a resolution when it is `open`. Whether a live route
carries goods at that resolution is `endpoint-loss`'s derivation. Deleting rows is never done: history stays
for the economy report and for `world-reclaim`.

## Tunables

None owned here. Admission reads no number. Share values are player input, not balance.

## Numeric types

`sharePerTurn` and every quantity: `long`, `checked`. Counters: `long` (structural, never a magnitude).

## Contract-level acceptance

1. Every refusal in Design 3 returns its named reason and writes nothing (asserted by row counts).
2. A route set between world A and world B, with A active: A's next commit logs exactly one `rift-window` for
   that route; B's command log is unchanged.
3. Replaying A alone (`GetWorldTurnReport` path) from its command log reproduces A's stored hash with B absent
   from the store.
4. Re-committing the same turn (retry) logs no second window (dedupe on the deterministic `CommandId`).
5. A player or AI submission of `rift-window` is refused `kind.system-only` at admission.
6. Clearing a route stops windows from the next resolution on; goods already in the crossing are untouched by
   the clear (conservation is `crossing-handoff`'s test; this module asserts the ledger rows are unchanged).
7. **Order-independent:** setting route R1 then R2 from one anchor gives the same windows, in route-id order, as
   setting R2 then R1 (both tested).
8. A route between two hibernating worlds is admitted and produces no window until one of them resolves.
9. SQL only in `FusionRpg.Data` (`gk-core/scripts/guard-dal.py`).

## Test plan and verification boundary

| Test | Project |
|---|---|
| Admission table (one test per reason) | `gk-core/tests/FusionRpg.Data.Tests` (store, in memory) |
| Window filing, dedupe on retry, order independence | `gk-core/tests/FusionRpg.Data.Tests` |
| Replay of one endpoint alone | `gk-core/tests/FusionRpg.Data.Tests` (commit + `GetWorldTurnReport`) |
| `kind.system-only` refusal | `gk-core/tests/FusionRpg.Core.Tests` (World/Turn admission) |
| Set/clear endpoints | `gk-core/tests/FusionRpg.Server.Tests` |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
python gk-core/scripts/guard-dal.py
```

Store tests run in memory (`docs/contributing/testing-standard.md`). This module crosses Core, Data and Server:
run the full suite once at its end (AGENTS.md verification point 2), not per edit.

## Hard edges

- **Always:** refuse before writing; one transaction per verb; the window is filed inside the commit
  transaction, before the command read; deterministic command ids.
- **Ask first:** two-way routes as one record; routes that join a world of another save or another empire;
  any stored per-world route policy (it would reintroduce a cache).
- **Never:** a read of world B's state from inside world A's `Step`; a route that moves an entity; a second
  command-filing path beside the system-command seam; a route row inside any world hash; deleting route rows.

## Dependencies

| Consumes | From | State |
|---|---|---|
| One active world per save; `outcome` column | `world-continuity` `world-state-vocabulary` | Map approved; not built |
| Save End Turn counter | `world-continuity` `hibernation-clock` | Map approved; not built |
| System-command path (a closed system-kind set; admission refuses those kinds; one Data filing path inside the commit) | `trade-foundation` `system-commands` (round-4 Q10; ask A7; `../trade-foundation/spec-system-commands.md`) | Specced 2026-09-19 |
| `trade.riftTrade` flag — **`rift-trade` wave 1's**, registered in this wave's change with its one `RulesetVersion` bump (round 6 C1; landing-order row 20), shared with `crossing-goods` and `crossing-anchor`; waves 2 and 3 take their own flags (`trade.riftCrossing`, `trade.riftEndpoints`) and never widen this one | `trade-foundation` `world-stamp` (ask A4) | Map approved; not built |
| Working-anchor predicate (Rift Anchor + Grand Exchange); far-end snapshot | `crossing-anchor` | This program |
| Goods admission | `crossing-goods` | This program |

| Exposes | To |
|---|---|
| The route record and its lifecycle | every other `rift-trade` module |
| The `rift-window` payload | `crossing-leg`, `crossing-handoff`, `sleeping-endpoint`, `endpoint-loss` |

## Files

```
src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs        NEW — table, SetRiftRoute, ClearRiftRoute, FileRiftWindowsUnlocked
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs        MODIFIED — one call before the command read
src/FusionRpg.Core/World/Logistics/Rift/RiftRoute.cs    NEW — record, admission rules (pure)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs           MODIFIED — rift-window kind through the system-kind seam
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                  MODIFIED — two routes
gk-core/src/FusionRpg.Contracts/WorldDtos.cs                    MODIFIED — request/response DTOs
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store (rpg_worlds, command log), world turn commit, save identity keying,
    server endpoints. No actor, lawn or injector subsystem.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json (paths include
    docs/architecture/trade-network/**). session-boundary-check.py not re-run by me.
[x] Read this session: DESIGN-GATE §1 rows Economy (empire-resource-ssot.md in full; economy-principles
    P13-P14), Data/SQL (data-architecture.md §3, §6; contributing/architecture-map.md), World map
    (world-map-program.md); §2, §3, §5; PRINCIPLES.md §11; the rift-trade, trade-network,
    world-continuity, logistics-flow, fleet, trade-foundation and sector-yield maps;
    world-continuity-ideal.md in full. Not read in full: world-map-runtime-ideal.md, the
    world-map-runtime spec/map/gaps pair and their plans, spec-soul-economy.md — none governs
    cross-world routes; stated as a gap.
[x] decisions.md: World store — delve worlds (kind column) and the world-turn phase order row,
    both via the maps that cite them; no lock covers cross-world routes.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding (see session report).
[x] Verified against code: the command log key and order, the commit's read point, admission's
    first checks, the replay loop.
[x] Read surrounding sections: the whole CommitWorldTurn body (WorldTurns.cs:494-705).
[x] Constraints tested: none claimed. Replay self-containment is an acceptance test, not a claim.
[x] No §2 invariant contradicted: SQL in Data only; determinism per world; no ceiling.
[x] Corrections propagated: the map's "one system command at set time" wording is replaced by the
    per-resolution window, in the map and here.
[x] No population count pinned: the reason set and the route-state set are closed vocabularies.
[x] Event-refreshed cache: none owned here — the window is read fresh every resolution (why: Design 4).
    The far-end snapshot the window copies IS an edge-refreshed projection; it is crossing-anchor's, with
    its full trigger set T1-T7 there (stated by the 2026-09-20 audit so "none" is not read as "no cache
    anywhere on this path").
[x] Orderings: route creation order is tested both ways.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: one command log, one system-command path (owned by
    trade-foundation since round-4 Q10), one admission gate.
[ ] Registry row: "rift-window is system-only" needs an invariants row in
    gk-core/scripts/enforcement-registry.v1.json with its admission test — lands with the code (named by the
    2026-09-20 audit: `rift-window-system-only`).
```

## Audit 2026-09-20

Fixed here: the route table gains its primary key; the checklist's "no cache" now names the far-end projection
the window copies (owned by `crossing-anchor`, with its trigger set). Checked and clean: each world replays alone
from its own log; refusals write nothing; deterministic command ids inside admission's bound; SQL only in Data;
store tests in memory. **Verification boundary:** the Core half joins the `core-world-logistics-rift` owner
boundary (`spec-crossing-anchor.md` *Audit 2026-09-20*); the Data and Server halves use their existing owners;
the module crosses three projects, so the full suite runs once at its end.

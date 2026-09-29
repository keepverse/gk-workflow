# Spec: `world-state-vocabulary`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Every `file:line` below was
opened in this session. Module 1 of the [world-continuity map](../world-continuity-map.md) (wave 1, no
dependencies). Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §6.1. Owner decision
**Q1 (2026-09-19)**: `state` (attention) and `outcome` (result) are two columns; the ideal's five words
are player-facing labels derived from them. House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

`rpg_worlds.state` is a column nothing reads except `GetActiveWorld`, and nothing writes after insert.
This module turns it into the **attention** axis (`active | hibernating | idle`), adds the **result**
axis `outcome` (`contested | won | fallen`), makes *"exactly one active map world per save"* a fact
SQLite enforces, gives the player a real **select** transition, and refuses every order or End Turn
on a map world that is not `active`.

Success looks like: a save can hold several map worlds; exactly one is `active`; selecting another
swaps them in one transaction; `GET /api/world/{playerId}` returns the one the player chose, never
"the first by id"; a command or commit aimed at a hibernating world is refused with `world.not-active`.

## Scope and non-goals

**In scope:** two closed Core vocabularies and the derived label; the `outcome` column; the partial
unique index; a one-time reconciliation of saves that already hold two active map worlds; the new
`GetActiveWorld` contract; the `SelectWorld` store verb and its route; the not-active gate on submit
and commit; the `CreateWorld` rule for a save that already has an active world.

**Not in scope:** what makes `outcome` change (`world-victory`, `world-fall`); the End Turn counter and
the hibernating world's clock mark (`hibernation-clock`, which `SelectWorld` calls into once it
exists); entering `idle` (`idle-world`); catching a world up on select (`coarse-step`); the advance
verb (`advance-carry`); any player surface (`multiverse-surface`). Delve rows (`kind='delve'`) are
never touched.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `state TEXT NOT NULL DEFAULT 'active'`, index `(player_id, state)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32`, `:36` |
| `kind` / `parent_world_id` columns and index `(player_id, kind, state)` | `RpgStore.World.cs:204-206` |
| `CreateWorld` validates before any write, then inserts `state='active'` as a literal | `RpgStore.World.cs:219-253`; insert `:243-245` |
| Delve rows are also inserted `state='active'`, `kind='delve'` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:190-192` |
| `WorldHeaderRow.State` is read back | `RpgStore.World.cs:737-740` |
| The player row **is** the save (R17): `players.id` is the `SaveId` | `gk-core/src/FusionRpg.Core/Saves/SaveId.cs:5-9`; `players` DDL `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:198-203` |
| Closed id-addressed vocabulary precedent | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-25` |

### Wiring gap

| Gap | Evidence |
|---|---|
| The active world is "first active map by id", not a choice | `RpgStore.World.cs:416-431` (`ORDER BY world_id LIMIT 1`, `:425`) |
| Its only production caller is `GET /api/world/{playerId}`; the web reads it | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:28-32`; `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:584` |
| Commit checks `kind`, never `state` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:507-508` |
| Submit checks `kind`, never `state` | `RpgStore.WorldTurns.cs:103-107` |
| Nothing writes `state` after insert; the only `UPDATE rpg_worlds` is the turn advance | `RpgStore.WorldTurns.cs:687-689` (only hit of `UPDATE rpg_worlds` under `src/`) |

### Real gap

No closed vocabulary type for either axis; no `outcome` column; nothing makes the active world unique;
no select verb.

## Design

### 1. Two closed vocabularies in Core, one derived label

New file `src/FusionRpg.Core/World/WorldLifecycle.cs`:

```csharp
public enum WorldAttention { Active, Hibernating, Idle }      // rpg_worlds.state
public enum WorldOutcome   { Contested, Won, Fallen }         // rpg_worlds.outcome

public static class WorldLifecycle
{
    // Id <-> enum, the FactionKindCatalog shape. Unknown id throws (load rejection).
    public static WorldAttention AttentionOf(string id);
    public static WorldOutcome OutcomeOf(string id);
    public static string IdOf(WorldAttention a);
    public static string IdOf(WorldOutcome o);

    // The ideal's five words, derived — never stored.
    public static WorldLabel LabelOf(WorldAttention a, WorldOutcome o) => o switch
    {
        WorldOutcome.Fallen => WorldLabel.Fallen,
        _ => a switch
        {
            WorldAttention.Hibernating => WorldLabel.Hibernating,
            WorldAttention.Idle        => WorldLabel.Idle,
            _ => o == WorldOutcome.Won ? WorldLabel.Developing : WorldLabel.Active,
        },
    };
}
public enum WorldLabel { Active, Developing, Hibernating, Idle, Fallen }
```

Label precedence is fixed: `fallen` wins over attention (a fallen world is fallen whether or not you
are looking at it); otherwise attention wins over `won` (a won world you left is *hibernating*, and its
won-ness is carried by `outcome`, which is what the carry limit and the event budget read). Display
names are catalog rows (GG-62), never title-cased ids; the glossary rows are
`continuity-doc-amendment`'s.

**Legal pairs.** All nine are representable; two are restricted by later modules, not here:
`idle` requires a warden (`idle-world`) and `fallen` can be `active` only through `world-reclaim`
(reserved). This module stores whatever the owning module writes and asserts only the vocabularies.

### 2. Schema — additive, one index, one reconciliation

In `EnsureWorldSchemaUnlocked` (after `:206`):

```sql
-- EnsureColumn: an existing world reads back 'contested', which is what every shipped world is.
ALTER TABLE rpg_worlds ADD COLUMN outcome TEXT NOT NULL DEFAULT 'contested';
-- One fact, one place (map assumption 2): no pointer table beside the state column.
CREATE UNIQUE INDEX IF NOT EXISTS ux_rpg_worlds_one_active_map
  ON rpg_worlds(player_id) WHERE state = 'active' AND kind = 'map';
```

**Reconciliation before the index.** `CREATE UNIQUE INDEX` fails on a database that already has two
active map worlds for one save, which the test route can produce today (`WorldEndpoints.cs:601-625`
creates any `worldId` for any player). So, in one transaction and before the index statement: for each
`player_id` with more than one `state='active' AND kind='map'` row, keep active the row
`GetActiveWorld` returns **today** (lowest `world_id`) and set the others to `hibernating`. That choice
preserves exactly what every client currently sees. Idempotent: a second run finds nothing to change.
The clock mark those rows need is `hibernation-clock`'s; when this module lands first, its column does
not exist yet and the reconciliation writes only `state`.

`outcome` is legal only for `kind='map'`; delve rows keep the default and nothing reads it for them.

### 3. `GetActiveWorld` — the unique row or none

Same signature (`RpgStore.World.cs:416`), same projection plus `outcome`. The `ORDER BY world_id LIMIT 1`
goes; the query can return at most one row because the index guarantees it. `WorldHeaderRow` gains
`string Outcome = "contested"` as a trailing optional field (the `Kind`/`ParentWorldId` precedent,
`:737-740`), so no existing constructor call changes.

### 4. `SelectWorld(saveId, worldId)` — one transaction

```
refuse world.unknown        when the row does not exist or belongs to another save
refuse world.not-a-map      when kind != 'map'
refuse world.fallen         when outcome = 'fallen'   (only world-reclaim may select one — reserved)
ok.already-active           when it is already the active one (idempotent replay)
otherwise, in one tx:
  current active map row (if any) -> state = 'hibernating'   (+ clock mark, hibernation-clock)
  target row                      -> state = 'active'          (+ catch-up first, coarse-step)
  revision + 1 on both rows
```

**Order-independent** (DESIGN-GATE §2.16 corollary): selecting B then A, and A then B, from any
starting pair ends with exactly one active row, and which world was created first never matters.
Selecting an `idle` world first collects it (`idle-world`'s hook) and then activates it; until that
module lands, an `idle` row cannot exist.

Route: `POST /api/world/{worldId}/select` with `{ playerId }` in `WorldEndpoints.cs`, mapped in the
production group (not the `/api/test` group). The result DTO carries the reason verbatim.

### 5. The not-active gate

- `SubmitWorldCommands` (`RpgStore.WorldTurns.cs:88`): after the existing `kind` refusal (`:103-107`),
  refuse every command with `world.not-active` when `header.State != "active"`, before any write.
- `CommitWorldTurn` (`:493`): same check beside `:508`, before `MarkCommittedUnlocked` (`:521`).
- **System-issued commands are not submissions.** `world-warden`, `advance-carry` and `rift-trade` file
  system commands into non-active worlds. **Round 4 (owner Q10, 2026-09-19): the filing path is the one
  shared system-command path `trade-foundation` builds (`trade-foundation` `system-commands`)** — a closed system-kind set that admission refuses
  from every commander, one Data filing path inside the commit transaction that reuses
  `InsertCommandUnlocked` (`:159`), deterministic command ids (`rift-trade-map.md` ask A7). This module no
  longer defines a `FileSystemCommandUnlocked` of its own; it owns only the rule that this not-active gate
  admits that path's commands and nothing else, never admission. No route reaches the path.

### 6. `CreateWorld` on a save that already has an active map world

`CreateWorld` (`:219`) inserts `state='active'` only when the save has no active map world; otherwise
it inserts `hibernating`. Creation never selects. The production advance path (`advance-carry`) creates
and selects in one transaction; the test route keeps working and simply creates a non-active second
world. This is decided by principle: a second `active` would violate the index, and failing the insert
would make the test route unusable.

### 7. Determinism, hashing, replay

`state` is a store column that `WorldCanonical.Write` never reads: its only header row is
`TemplateId, Seed, CurrentTurn` (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:27`), which `decisions.md`
*World store — delve worlds* also records. Attention is **never** hashed and `WorldState` gains no
attention field — the rule the delve scope used for `kind` (`RpgStore.WorldTurns.cs:98-101` comment,
verified against `WorldCanonical.cs`) — because which world the player is looking at is not world
history.

`outcome` is world history, so [`world-victory`](spec-world-victory.md) §1 makes it a hashed
`WorldState` field produced inside the step, persisted in this module's column and emitted in the
canonical text only when not `contested`. **In this module** nothing writes `outcome` except its
default, so no world hash and no golden moves, and replay (`RpgStore.WorldTurns.cs:738-777`) is
untouched.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | `state` column + indexes | reused |
| Wiring gap | first-by-id active world; no state gate on submit/commit; nothing writes `state` | §3, §5, §4 |
| Real gap | vocabularies, `outcome`, uniqueness, select verb | §1, §2, §4 |

## Acceptance (contract)

1. Both vocabularies are closed enums; their member lists are pinned (3 and 3) with the reason
   "closed vocabulary the code owns; a new member is a reviewed change". An unknown stored id throws on
   load (`world.state-unknown`, `world.outcome-unknown`).
2. `LabelOf` returns the five labels for the nine pairs per §1's table; tested exhaustively (9 cases,
   a closed product, not a population).
3. A second `active` map world for one save is refused by SQLite (the index), and the store surfaces it
   as a named reason, never an unhandled exception.
4. `GetActiveWorld` returns the unique active map row or `null`; a delve id that sorts first never
   wins (keeps `DelveScopeTests.GetActiveWorld_returns_the_map_even_when_a_delve_id_sorts_first`,
   `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveScopeTests.cs:116`, green).
5. `SelectWorld` swaps attention in one transaction, is idempotent, refuses a fallen or unknown world,
   and is order-independent (both orders tested).
6. Submit and commit on a non-active map world return `world.not-active` and write nothing (command
   table and commit table unchanged, verified by row count before/after).
7. The reconciliation leaves exactly one active map world per save, choosing the lowest `world_id`, and
   a second run is a no-op.
8. No `StateHash` changes for any existing world (`state` is never hashed; `outcome` stays at its
   default in this module).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/WorldLifecycleTests.cs` (new): id round-trip, unknown throws,
  exhaustive `LabelOf`.
- `gk-core/tests/FusionRpg.Data.Tests/WorldStoreTests.cs` (extend): index refusal; reconciliation of a seeded
  two-active save; `GetActiveWorld` after select; select idempotency; select refusals; both-order select.
- `gk-core/tests/FusionRpg.Data.Tests/WorldCommandStoreTests.cs`, `WorldTurnCommitTests.cs` (extend):
  `world.not-active` on submit and commit, zero rows written.
- `gk-core/tests/FusionRpg.Server.Tests` (new `WorldSelectEndpointTests.cs`): route mapping, reasons verbatim.
- Existing tests that commit turns on a second map world of the same player must select it first — a
  failure there is this module's expected fallout, fixed in the test, never by weakening the gate.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
```

Store tests run in memory (testing-standard). This module crosses Core, Data and Server in one change,
which is AGENTS.md verification point 2: the full suite once at module end.

## Hard edges

- **`rpg_worlds` schema:** one additive column and one partial unique index. The reconciliation is the
  only data write; it runs before the index in one transaction and is idempotent. No column is renamed
  or dropped.
- **Replay:** untouched (header columns are not replay inputs).
- **Corpse-cache tick key:** not touched here (see `hibernation-clock`).

## Dependencies

None inside the program. Consumed by every later module. `hibernation-clock` adds the clock mark to
§4 and §2; `coarse-step` adds catch-up to §4; `idle-world` adds collect-on-select to §4.

## Boundaries

- **Always:** refuse before any write; one transaction per transition; reasons verbatim.
- **Ask first:** letting a player select a `fallen` world (that is `world-reclaim`, reserved).
- **Never:** a pointer table beside `state`; a `Kind`/`State` field on `WorldState`; a `state` write
  from any path other than the verbs this program defines; touching delve rows.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldAttention`, `WorldOutcome`, `WorldLifecycle.LabelOf` | every module; `multiverse-surface` |
| `SelectWorld` and its hooks (clock mark, catch-up, idle collect) | `hibernation-clock`, `coarse-step`, `idle-world`, `advance-carry` |
| `world.not-active` gate (admits only `trade-foundation`'s system-command path, Q10) | `world-warden`, `advance-carry`, `rift-trade` |
| `WorldHeaderRow.Outcome` | `world-victory`, `world-fall`, `advance-carry`, `world-event-budget` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store (rpg_worlds), world turn submit/commit, world endpoints.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json lists
    docs/architecture/world-continuity/**. session-boundary-check.py not re-run by me (docs only,
    new file).
[x] Read this session: DESIGN-GATE (rows Anything, Product vision, Economy, Data/SQL, World map,
    Performance; §2, §3, §5), PRINCIPLES.md, the-game.md, the-loops.md, world-continuity-map.md,
    world-continuity-ideal.md, warden-mortality-ideal.md, trade-foundation-map.md, spec-budget-debit.md.
    Not read: data-architecture.md, software-architecture.md, contributing/architecture-map.md
    (rules taken from PRINCIPLES.md §3, §6).
[x] decisions.md checked: World store — delve worlds row (header not hashed, kind column); no lock on
    world states.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: GetActiveWorld SQL text, both inserts, the only UPDATE, submit/commit gates.
[x] Surrounding sections read (the delve-scope comments at the submit and commit gates).
[ ] Constraints tested: "no golden moves" rests on WorldCanonical.Write not reading header columns
    (verified by reading it), not on a suite run.
[x] No §2 invariant contradicted: SQL stays in Data.
[x] Corrections propagated to the map (status + decisions).
[x] No population pinned; the two 3-member vocabularies are pinned as closed vocabularies with a reason.
[x] No event-refreshed cache.
[x] Select is order-independent and both orders are tested.
[x] No actor magnitude.
[x] No SOLID fork: one fact (state column), no pointer table.
[ ] Registry row for "one active map world per save": enforced by the index itself; the
    enforcement-registry row is added when the module is built.
```

# Spec: `hibernation-clock`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 2 of the
[world-continuity map](../world-continuity-map.md) (wave 1; depends on `world-state-vocabulary`).
Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §3.2, §3.5, §6.3. Map assumption 3
(pending turns are computed, never incremented per world). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

Hibernating worlds ride the world-turn clock without being stepped. Every committed End Turn in the
active world raises one **save-scoped** counter by one; a hibernating world records the counter value
up to which its time has been applied; its pending turns are a subtraction, bounded by a tunable
credited window. The same counter becomes the tick key for corpse-cache decay, which today collides
across worlds.

Success looks like: after N End Turns in world A, world B (hibernating) reports `pending = min(N, cap)`
with **zero** writes to B's row; switching worlds never skips or doubles a corpse-cache decay tick.

## Scope and non-goals

**In scope:** the save counter table; the per-world clock mark; pending as a pure function; the counter
advance inside `CommitWorldTurn`'s transaction; the corpse-cache decay re-key (tick, start stamp, both
first-by-id reads); the credited-window tunable and its §11 register row.

**Not in scope:** doing anything with pending turns (`coarse-step`); idle worlds' wall clock
(`idle-world`); the tunables file's first publish mechanics beyond naming the key (the first module to
build extends `gk-core/tools/tuning/publish.py`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `catch_up_cap INTEGER`, `turn_period_seconds INTEGER`, `last_advanced_utc TEXT` on `rpg_worlds` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:26-29` |
| The commit is one transaction; the turn advance is its only `UPDATE rpg_worlds` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:519`, `:687-689` |
| The decay tick runs in the same commit, after the advance | `RpgStore.WorldTurns.cs:700` |
| Decay idempotency row `rpg_corpse_cache_decay_log PRIMARY KEY (cache_id, tick)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs:46-53` |
| The player row is the save (R17); a save-scoped new table carries one `save_id` column | `gk-core/src/FusionRpg.Core/Saves/SaveId.cs:5-9`; `docs/architecture/solid-enforcement/spec-save-identity.md:594-603` |

### Wiring gap

| Gap | Evidence |
|---|---|
| `catch_up_cap` and `turn_period_seconds` are never read — the only `src/` hits are the DDL | `RpgStore.World.cs:26-27` (searched `src/`) |
| `last_advanced_utc` is written only by the turn advance | `RpgStore.WorldTurns.cs:688` |

### Real gap — and one defect found

- No save-scoped turn counter; no per-world clock mark.
- **Defect: the corpse-cache decay clock is keyed by the committing world's bare turn number.** The
  tick query selects every cache of the **save** (`owner_player_id = $p`) not yet logged for tick `$t`
  (`RpgStore.CacheDecay.cs:130-145`), called with `result.World.CurrentTurn` of whichever world
  committed (`RpgStore.WorldTurns.cs:700`). With two map worlds, world B's turn 3 and world A's turn 3
  are the same tick: after switching from A (turn 10) to B (turn 0), B's next ten commits find ticks
  1–10 already logged and **skip** every cache's decay for ten turns.
- **Defect: the decay start stamp reads "first map world by id".** Both start paths read
  `SELECT current_turn FROM rpg_worlds WHERE player_id = $p AND kind = 'map' ORDER BY world_id LIMIT 1`
  — with no `state` filter at all (`RpgStore.CacheDecay.cs:87-91`; the copy in
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:175-179`).

## Design

### 1. Homes — decided by principle

| Fact | Home | Why |
|---|---|---|
| The save's End Turn count | new table `rpg_save_world_clock(save_id INTEGER PRIMARY KEY, end_turns INTEGER NOT NULL DEFAULT 0)` | Save-scoped, so one `save_id` column (spec-save-identity new-table rule). Not a column on `players`: the core account row stays narrow and a clock row is created lazily |
| A world's applied time | new column `rpg_worlds.clock_mark INTEGER` (nullable) | Per world. `NULL` for delve rows; set for every map row |
| The credited window | tunable `catchUpCapTurns` in `data/tuning/world-continuity.v1.json` | A balance number (tunables-ssot). **`rpg_worlds.catch_up_cap` stays unread**: a per-world column beside a tunable would be two homes for one number. The column is left in place (dropping columns is a rebuild) and documented as reserved-unused in a DDL comment |

Both counters are `long` — structural counts, never magnitudes (map *Principles restated*).

### 2. The counter advances once per committed End Turn

Inside `CommitWorldTurn`'s transaction, in the same block as the turn advance (`:683-697`):

```
end_turns' = end_turns + 1              (UPSERT on rpg_save_world_clock, checked long)
active row: clock_mark = end_turns'     (same UPDATE statement as current_turn — no extra row write)
```

Only an **advancing** commit counts (the path that reaches `:687`); a `waiting` commit (`:531-535`)
does not. Replaying a commit cannot double-count: `CommitWorldTurn` refuses a stale `expectedTurn`
(`:515`) before any write, so the same turn never reaches the advance twice.

### 3. Pending is computed, never stored

```csharp
// Core, pure. src/FusionRpg.Core/World/Continuity/HibernationClock.cs
public static long Pending(long saveEndTurns, long clockMark, long catchUpCapTurns)
{
    var raw = checked(saveEndTurns - clockMark);
    if (raw < 0) throw new InvalidOperationException("clock mark ahead of the save counter");
    // Structural bound (ssot-power-scale §11.4 row, this module): the credited catch-up window.
    // Not a magnitude cap: it bounds how many turns ONE catch-up may simulate.
    return Math.Min(raw, catchUpCapTurns);
}
```

Store read: `GetPendingTurns(worldId)` joins the world's `clock_mark` with its save's `end_turns`.
**No per-world write on End Turn** — hibernating rows are never touched by a commit.

**Excess beyond the window is forfeited, not banked.** When `coarse-step` applies a catch-up it sets
`clock_mark = end_turns` (not `clock_mark + pending`). That is the Melvor shape the ideal adopted
(credited window, ideal §3.5 and §5): a world left alone for 500 turns catches up `catchUpCapTurns`
worth of history, not 500. It bounds cost and cuts both ways — gains and losses stop accruing past the
window — and it is stated to the player by `away-digest` ("N turns credited of M elapsed").

**Audit 2026-09-20 — forfeiture is a safety bound, never the routine path.** Forfeiting past the window
would also forfeit that world's upkeep and enemy pressure, so a player who simply never looked at an old
world would pay nothing for it — leaving would pay better than staying, which the map's principles forbid.
So `coarse-step` §7 catches up **every hibernating world whose pending has reached the window** in the
background pass of the End Turn that brings it there, outside the per-turn budget. In normal play a
hibernating world's pending never exceeds the window and nothing is forfeited; the window remains the
structural bound on one catch-up (and the forfeit rule covers a save migrated with a larger gap, or an
idle world, whose own window is `idle-world`'s).

### 4. Transitions write the mark

| Transition | Mark write |
|---|---|
| Map world created (any state) | `clock_mark = end_turns` (0 for a new save) |
| `active → hibernating` (select-away, advance) | `clock_mark = end_turns` — it is already current (§2), so this is a no-op assertion |
| `hibernating → active` (select) | catch-up first (`coarse-step`), which sets `clock_mark = end_turns` |
| enter / leave `idle` | `idle-world` owns it: entering catches up first; leaving sets `clock_mark = end_turns` so idle time is never also credited as hibernating time |

### 5. Corpse-cache decay re-keyed to the save counter

- **Tick:** `TickCorpseCacheDecayForPlayerUnlocked(db, tx, playerId, newTick: end_turns', seed, now)`
  — the call at `RpgStore.WorldTurns.cs:700` passes the save counter instead of the world's turn. The
  `(cache_id, tick)` key (`RpgStore.CacheDecay.cs:52`) is then unique per save End Turn, whichever
  world committed. **Type (audit 2026-09-20):** the method's parameter is `int newTurn` today
  (`RpgStore.CacheDecay.cs:144`) while the save counter is `long` (§1); the parameter widens to `long`
  in this change — never a narrowing cast at the call site.
- **Start stamp:** both first-by-id reads (`RpgStore.CacheDecay.cs:87-91`,
  `RpgStore.CargoFate.cs:175-179`) read `end_turns` of the save instead. A save with no clock row reads
  `0` after the lazy upsert — the "no map world, wait clockless" branch (`RpgStore.CacheDecay.cs:94`) keeps its meaning by
  checking "save has a map world" instead of "first map world's turn".
- **Seed:** the stream label stays `corpse-decay:{cacheId}:{tick}:{seq}` over the committing world's
  seed (`RpgStore.CacheDecay.cs:180`). Unchanged by principle: decay is not part of any world's replay,
  and the key it must not collide on is the tick.
- **Migration, one time, idempotent, in schema setup:** for each save, `end_turns := MAX(current_turn)`
  over its map worlds, and every map world's `clock_mark := end_turns`. Every tick already logged is
  ≤ that maximum, so every future tick is strictly greater: **no skip, no double tick**. A save with one
  map world (every production save today — the only creation route is the test group,
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:601-625`) keeps tick numbers equal to its world's turns, so
  its future decay rolls are **byte-identical** to what the old code would have rolled.

### 6. Determinism and replay

`clock_mark` and `end_turns` are store columns outside `WorldCanonical.Write` (header row
`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:27`): no hash moves, no golden moves. World replay
(`RpgStore.WorldTurns.cs:738-777`) never reads them. `Pending` is pure and reads no clock; the Core
file sits under the world determinism guard's scan root (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:253-266`).

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | commit transaction; decay log key | reused |
| Wiring gap | `catch_up_cap` / `turn_period_seconds` never read | §1: declared reserved-unused; the tunable is the SSOT |
| Real gap | save counter, clock mark, pending | §1–§4 |
| Defect | decay tick collision; first-by-id start stamp | §5 |

## Acceptance (contract)

1. Committing N advancing turns in the active world raises `Pending` of every hibernating world of that
   save by N (up to the window) with **zero** writes to their rows (row `revision` unchanged).
2. `Pending` never exceeds `catchUpCapTurns`; a negative raw value throws.
3. A `waiting` commit does not advance the counter.
4. Decay ticks are unique per `(cache, save counter)` whichever world committed: switching A→B→A across
   commits rolls each cache exactly once per End Turn (no skip, no double) — tested in both switch
   orders.
5. The migration is idempotent; a one-world save's post-migration decay outcomes equal the pre-change
   outcomes for the same commits (same tick numbers, same seed, same stream label).
6. No `StateHash` changes for any world.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/HibernationClockTests.cs` (new): `Pending` arithmetic,
  window, negative throws.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs` (extend): counter advance, waiting commit, zero
  writes to hibernating rows.
- `gk-core/tests/FusionRpg.Data.Tests/CacheDecay/CacheDecayTests.cs` (extend): two-world switch in both orders;
  migration idempotency; one-world byte-identity of outcomes.
- `gk-core/tests/FusionRpg.Data.Tests/CargoFate/` (extend): start stamp reads the save counter.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-dal.py
python scripts\audit-magic-numbers.py --summary
```

## Hard edges

- **`rpg_worlds` schema:** one nullable column (`clock_mark`); a new save-scoped table.
- **Replay:** untouched.
- **Corpse-cache tick key:** re-keyed from world turn to save counter (§5). This is the module that
  owns the change; the migration is what makes it safe for existing caches.
- **Register row:** `catchUpCapTurns` lands in `ssot-power-scale.md` §11.4-style "structural bound" with
  its comment, in the same change.

## Dependencies

`world-state-vocabulary` (map worlds exist beside each other; `SelectWorld` calls §4). Consumed by
`coarse-step` (pending), `idle-world` (mark on leave), `away-digest` (credited vs elapsed).

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `catchUpCapTurns` | turns | 28 (four in-world weeks at the shipped `DaysPerWeek`, `gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:22`) | `data/tuning/world-continuity.v1.json` |

## Boundaries

- **Always:** one counter per save; writes inside the commit transaction; `checked` long arithmetic.
- **Ask first:** banking forfeited turns instead of forfeiting them (that is a design change to the
  credited window).
- **Never:** a per-world increment on End Turn; reading `catch_up_cap`; a wall clock in `Pending`.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `HibernationClock.Pending`, store `GetPendingTurns(worldId)` | `coarse-step`, `multiverse-surface` |
| `clock_mark` write on transitions | `world-state-vocabulary` (select), `idle-world`, `advance-carry` |
| Save counter as the decay tick | deployment-hierarchy `cache-decay-void` (its tick contract changes key, not shape) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store, world turn commit, corpse-cache decay, cargo fate.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json (docs only);
    boundary check not re-run.
[x] Read this session: the rows listed in spec-world-state-vocabulary.md, plus spec-save-identity.md
    new-table rule (:594-603).
[x] decisions.md checked: no lock on a save clock; World store — delve worlds row for the header.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: the tick query SQL, both first-by-id start reads, the call site at :700.
[x] Surrounding sections read (CacheDecay file header "no wall clock"; the tick's own doc comment).
[ ] Constraints tested: "one-world decay outcomes byte-identical" is an acceptance test to write, not
    a measured claim.
[x] No §2 invariant contradicted.
[x] Corrections propagated: map contradiction 4 names this module.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Switch orders tested both ways (acceptance 4).
[x] No actor magnitude.
[x] No SOLID fork: one counter, one tick key.
[ ] Registry row for "no per-world write on End Turn": added when built (a Data test is the guard).
```

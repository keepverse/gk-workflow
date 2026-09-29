# Spec: notify-store

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `notify-store` of the
[notification-ssot map](../notification-ssot-map.md), wave 2, depends on `notify-vocabulary`.
**Strengthen pass 2026-09-18:** the column is `save_id` (R17); the pump's rows, prune and cursor are
committed in one transaction; a key ledger keeps idempotency across the prune; a per-save `rev` makes
catch-up see state changes as well as new rows (map §Strengthen pass S1, S3, S4).

**Rulings it carries:** R-N2 (a centre, bounded at `retainPerCategory` per category, per save),
R-N5 (the stable dedup key is a uniqueness constraint), R17 (the player row is the save).

---

## Objective

The durable, per-save notification log the ideal found missing (§Real gap: "No
notification-shaped table anywhere in `FusionRpg.Data`"). It is the only thing a disconnected player
can catch up from. SQL lives only here, behind `RpgStore`, and `guard-dal.py` enforces that (ideal
finding H1; DESIGN-GATE §2 invariant 6).

"Save" is the `players` row (R17, map §Identity). New tables name the column `save_id`, following
`save-identity`'s naming rule (`solid-enforcement/spec-save-identity.md` Decision 1). The value is
today's player id, so nothing here waits for that module to ship.

The log has five properties, each a success criterion:

1. **Idempotent append, across the prune.** Appending a draft whose `(save_id, dedup_key)` was already
   stored stores nothing and reports nothing as new, **even if the retention prune has since deleted
   that row**. The key ledger (§1) is what makes this hold. So a source can be re-run safely, and a
   pruned row can never come back as a new one.
2. **Bounded per category.** After every append, each touched `(save, category)` keeps at most its
   newest `retainPerCategory` rows. The prune runs in the **same transaction** as the insert, and the
   append returns only rows that survived it, so nothing is pushed that is not stored.
3. **Atomic per turn.** One call writes one world turn's rows for every save it addresses, the prune
   and the source cursor, in one transaction. A crash leaves either the whole turn published with the
   cursor advanced, or nothing and the cursor where it was. There is no half-published turn to re-run.
4. **One catch-up cursor for rows and state.** `rev` is a per-save counter bumped by every insert and
   every state change. `rev > since` returns new rows **and** rows whose state changed, so a client
   that was offline while another session dismissed something still sees the dismiss.
5. **A source cursor.** `rpg_notification_source_cursor` records, per `(source, scope)`, the last
   position a source published. It advances only inside property 3's transaction.

## Design

### 1. Schema (hot DB, `RpgStore.Notifications.cs`, new partial)

```sql
CREATE TABLE IF NOT EXISTS rpg_notification (
  seq          INTEGER PRIMARY KEY AUTOINCREMENT,   -- identity; never reused
  save_id      INTEGER NOT NULL,                    -- players.id (R17)
  dedup_key    TEXT    NOT NULL,
  category     TEXT    NOT NULL,
  severity     TEXT    NOT NULL,            -- routine | important | critical
  source_id    TEXT    NOT NULL,
  message_key  TEXT    NOT NULL,
  args_json    TEXT    NOT NULL,            -- NotifyArgDto[] as stored, never re-rendered here
  subject_key  TEXT,
  world_id     TEXT,
  world_turn   INTEGER,
  state        TEXT    NOT NULL DEFAULT 'unread',   -- unread | read | dismissed
  rev          INTEGER NOT NULL,            -- per-save change counter (property 4)
  created_utc  TEXT    NOT NULL,
  UNIQUE (save_id, dedup_key)
);
CREATE INDEX IF NOT EXISTS ix_rpg_notification_save_rev     ON rpg_notification (save_id, rev);
CREATE INDEX IF NOT EXISTS ix_rpg_notification_save_cat_seq ON rpg_notification (save_id, category, seq);
CREATE INDEX IF NOT EXISTS ix_rpg_notification_repeat       ON rpg_notification (save_id, category, subject_key, world_turn);

-- The per-save rev counter. A row, not MAX(rev): the prune can delete the row holding the highest
-- rev, and a counter read from the rows would then go backwards past a client's cursor.
CREATE TABLE IF NOT EXISTS rpg_notification_save_rev (
  save_id  INTEGER PRIMARY KEY,
  rev      INTEGER NOT NULL
);

-- The dedup key ledger (property 1). It outlives the row, so a pruned key is still refused.
CREATE TABLE IF NOT EXISTS rpg_notification_key (
  save_id     INTEGER NOT NULL,
  dedup_key   TEXT    NOT NULL,
  world_turn  INTEGER NOT NULL,
  PRIMARY KEY (save_id, dedup_key)
);

CREATE TABLE IF NOT EXISTS rpg_notification_source_cursor (
  source_id  TEXT    NOT NULL,
  scope_key  TEXT    NOT NULL,              -- e.g. the worldId for the world-turn pump
  position   INTEGER NOT NULL,              -- e.g. the last resolved world turn published
  PRIMARY KEY (source_id, scope_key)
);
```

- The DDL runs from `EnsureNotificationSchemaUnlocked(db)`, called in the schema sequence beside the
  other partials (`RpgStore.cs:822-860` is where those calls live). It follows the "DDL beside its
  store partial" convention the world tables use (`EnsureWorldSchemaUnlocked`, `RpgStore.cs:823`).
- **No soft-delete column.** R-N2 keeps history, and `dismissed` is a **state**: it takes a row off
  the feed but leaves it in the centre. The only deletion is the retention prune (ideal Open
  question 2, answered by R-N2).
- `created_utc` is presentation metadata only. No game rule reads it. Turn-clocked rules read
  `world_turn`, which keeps the no-wall-clock rule of the world-turn feeders intact (ideal finding
  M6).
- The table joins nothing and has no foreign key to `players`, matching the other `player_id`
  columns in the hot schema (for example `rpg_worlds.player_id`, `RpgStore.World.cs:22`).
- **Why a ledger and not only the `UNIQUE` constraint.** The constraint lives on the row, and the
  prune deletes rows. A source that re-reads an event after its row was pruned would otherwise insert
  it again as new. `cache-notify-source` re-reads on purpose (its window spans two turns). The ledger
  keeps each key for `DedupKeyMemoryWorldTurns` world turns after the turn it was stored under:

  ```csharp
  // Structural, not tunable: the widest re-read span of any registered source (cache-notify-source
  // reads [t, t+1]), plus one turn of margin. Changing it changes whether dedup is correct, not how the
  // game feels. A source with a wider window raises it in the same reviewed change.
  const int DedupKeyMemoryWorldTurns = 3;
  ```

  The ledger prune runs in the append's transaction and deletes `world_turn < appendTurn -
  DedupKeyMemoryWorldTurns` for the saves it touched, so the ledger is bounded by the sources' own
  window, not by history length. Every v1 draft carries a world turn (both sources run on the world
  clock). A future draft with no world turn relies on the row's `UNIQUE` constraint only, and the
  source that adds one says so.

### 2. Store API (all under the store's one write gate)

```csharp
public sealed record NotificationSaveAppend(long SaveId, IReadOnlyList<NotificationInsert> Rows);
public sealed record NotificationCursorAdvance(string SourceId, string ScopeKey, long Position);

public sealed partial class RpgStore
{
    /// <summary>One transaction: for each save, ledger INSERT OR IGNORE then row INSERT OR IGNORE on
    /// (save_id, dedup_key); bump that save's rev once per inserted row; prune every touched category
    /// to its newest <paramref name="retainPerCategory"/> rows; age the key ledger; then, when
    /// <paramref name="cursor"/> is set, upsert the source cursor. Returns, per save, only the rows that
    /// were inserted AND survived the prune, in seq order: exactly what the publisher may push. A re-run
    /// returns empty lists.</summary>
    public IReadOnlyDictionary<long, IReadOnlyList<NotificationRow>> AppendNotificationTurn(
        IReadOnlyList<NotificationSaveAppend> saves, int retainPerCategory, string createdUtc,
        NotificationCursorAdvance? cursor);

    /// <summary>New rows and state changes: rev > sinceRev, rev ascending.</summary>
    public NotificationPage ListNotificationChanges(long saveId, long sinceRev, int limit);
    public NotificationPage ListNotificationsByCategory(long saveId, string category, long? beforeSeq, int limit);

    /// <summary>Allowed moves: unread→read, unread|read→dismissed, and the one undo dismissed→read.
    /// Anything else, or a seq the prune already removed, is a no-op for that seq. Each changed row gets a
    /// new rev. Returns (seq, rev) for the rows actually changed.</summary>
    public IReadOnlyList<NotificationStateChange> SetNotificationState(long saveId, IReadOnlyList<long> seqs, string state);

    /// <summary>True when (save, category, subject) has a stored row with world_turn >= fromTurn —
    /// the repeat-window read (notify-service §Design 2).</summary>
    public bool HasRecentNotification(long saveId, string category, string subjectKey, int fromTurn);

    public long? GetNotificationCursor(string sourceId, string scopeKey);
    /// <summary>Only for initialising an absent cursor (notify-service §3 step 2). Advancing a cursor
    /// over published rows goes through AppendNotificationTurn, never through this.</summary>
    public void InitNotificationCursor(string sourceId, string scopeKey, long position);
}
```

- **The prune, with its required comment.** R-N2 names this a retention tail, the kind `CLAUDE.md`'s
  caps rule exempts only when the code says so:

  ```csharp
  // Retention tail (CLAUDE.md "Caps" exemption: retention tails). Not a progression ceiling: it
  // bounds history rows, never a magnitude. The depth is the tunable
  // notification.v1.json retainPerCategory (R-N2), applied per (save, category) so a noisy
  // category can never evict a quiet one's history.
  ```

- **Prune order.** By `seq` descending, keeping the newest N. State is ignored: an unread row older
  than N newer rows of the same category is pruned (map §Open questions, "Can unread rows be
  pruned?"). If one turn inserts more than N rows of one category for one save, the oldest of those
  are pruned in the same transaction and are **not** returned, so they are never pushed. Their keys
  stay in the ledger, so they are not re-inserted either.
- **A pruned row sends no signal.** A client holding it keeps it until its next reset or reload, and a
  state change on it is a no-op. The centre reads history from the server, so it never lists a pruned
  row.
- **Where `retainPerCategory` comes from.** It is passed in by the caller (the publisher holds the
  injected tuning, tunables-ssot T7.2). The store never reads a tuning file.
- **State transitions:** `unread → read`, `unread|read → dismissed`, plus one backward move,
  `dismissed → read`. That move is the rail's existing undo (`spec-world-notify.md` §3: "Leaves the
  rail, with an undo in its place"; today a local gesture at `WorldStage.tsx:528-534`), and it is
  persisted so a second session and a reload agree. Every other move (for example back to `unread`)
  is a no-op for that seq, not an error.
- **The source cursor** moves only inside `AppendNotificationTurn`, in the same transaction as the rows
  it vouches for. `InitNotificationCursor` exists for the one case with no rows: a world entering the
  system (`notify-service` §3 step 2).

### 3. Numeric types

`seq`, `rev`, `save_id` and the cursor `position` are `long` (ideal H4; `CLAUDE.md` numeric rule 1;
`SaveId` is `long`, `spec-save-identity.md` "`SaveId` is `long`"). The rev bump is `checked`.
`world_turn` is `int`, because a world turn is `int` wherever it is held (`WorldHeaderRow.CurrentTurn`,
`RpgStore.World.cs:737-740`). `retainPerCategory` and `limit` are `int`: they are row counts that a
structural page bound caps well below `int`'s range (`notify-service`). None of these is a magnitude,
so `audit-overflow.py` has nothing to widen.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Notification"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Notifications.cs           → DDL + the API above
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs                         → one EnsureNotificationSchemaUnlocked(db) call
gk-core/src/FusionRpg.Data/Notifications/NotificationRow.cs           → NotificationRow / NotificationInsert / NotificationPage /
                                                                NotificationSaveAppend / NotificationCursorAdvance /
                                                                NotificationStateChange records
gk-core/tests/FusionRpg.Data.Tests/Notifications/NotificationStoreTests.cs
```

## Code style

```csharp
// The ledger decides "new"; the row insert is the second line of defence. Only a key the ledger
// accepted reaches the row table, and only a row that survives the prune is returned.
ledger.CommandText = """
    INSERT OR IGNORE INTO rpg_notification_key (save_id, dedup_key, world_turn) VALUES ($p, $k, $t);
    SELECT changes();
    """;
// 0 ⇒ the key was stored before (even if its row is gone): nothing new, nothing to push.
row.CommandText = """
    INSERT OR IGNORE INTO rpg_notification
      (save_id, dedup_key, category, severity, source_id, message_key, args_json,
       subject_key, world_id, world_turn, rev, created_utc)
    VALUES ($p, $k, $c, $sev, $src, $m, $a, $subj, $w, $t, $rev, $now);
    SELECT CASE WHEN changes() = 1 THEN last_insert_rowid() END;
    """;
// Same last_insert_rowid() idiom as CreatePlayer (RpgStore.cs:1177); no RETURNING clause, which
// nothing in FusionRpg.Data uses today.
```

## Testing strategy

Data.Tests, **in-memory store only** (`RpgStore.InMemory()`/`DataTestStore`, testing-standard;
`guard-test-substrate.py`). Assertions are about the contract, never about populations:

1. **Idempotency.** Append the same `(save, dedupKey)` twice. The second call returns an empty list,
   and the row count for that key stays 1.
2. **Idempotency across the prune.** With `retainPerCategory = 1`, append key A, then key B in the
   same category (A is pruned), then A again within `DedupKeyMemoryWorldTurns`. Nothing is stored or
   returned the third time.
3. **Per-save uniqueness.** The same `dedupKey` for two saves stores two rows.
4. **Retention.** With `retainPerCategory = 2` (constructed inline, T7.2), append three rows in
   category A and one in B. A keeps its two newest seqs and B is untouched. The prune removes an
   **unread** row when it is the oldest. A single call inserting three rows in one category returns
   only the two that survived.
5. **Atomic turn.** Force a failure after the inserts and before the cursor upsert. Nothing from that
   call persists: no row, no ledger key, no rev bump, and the cursor is unchanged. This is the same
   forced-failure shape `spec-sector-storage.md` uses. A successful call leaves rows and cursor both
   written.
6. **Rev catch-up.** `ListNotificationChanges(p, r, limit)` returns strictly increasing revs `> r`,
   and a follow-up from the last rev returns the rest, with no gap and no repeat. A state change on an
   old row makes that row reappear after the client's cursor. Pruning the row that holds the highest
   rev never makes the next rev smaller.
7. **State moves.** `dismissed → read` (undo) changes the row and bumps its rev. `dismissed → unread`,
   `read → unread` and a pruned seq are no-ops, and they are absent from the returned list.
8. **Repeat read.** `HasRecentNotification` is true at `fromTurn = world_turn` and false at
   `world_turn + 1`.
9. **Cursor.** An absent cursor reads `null`. `InitNotificationCursor` round-trips.
10. **Ledger bound.** A key stored under turn `t` is gone from the ledger after an append under turn
    `t + DedupKeyMemoryWorldTurns + 1`.

## Boundaries

- **Always:** one transaction per `AppendNotificationTurn`, with the prune, the ledger aging and the
  cursor in it; return only inserted rows that survived the prune; carry the retention-tail comment
  and the structural comment on `DedupKeyMemoryWorldTurns`.
- **Ask first:** any column that stores rendered text. The words belong to the web (R-N3, map
  §Where this map departs).
- **Never:** SQL for these tables outside `FusionRpg.Data`; a wall-clock rule on `created_utc`; a hard
  delete on dismiss; reading a tuning file inside Data; advancing a source cursor outside the
  transaction that stored its rows; deriving `rev` from `MAX(rev)` over the rows.

## Success criteria

1. All four tables exist on a fresh and on an existing hot DB (`CREATE TABLE IF NOT EXISTS`).
2. Tests 1–10 green on the in-memory store.
3. `guard-dal.py` and `guard-test-substrate.py` green.
4. The retention prune carries the exemption comment verbatim, and `audit-magic-numbers.py` reports
   nothing new in this file.

## Seedsmith / generator

None. A schema with rows written at runtime by the publisher only.

## Open questions

None. R-N2 decided retention versus soft-delete. R-N5 decided the dedup key. R17 decided the column.

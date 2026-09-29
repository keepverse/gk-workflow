# Spec: notify-service

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `notify-service` of the
[notification-ssot map](../notification-ssot-map.md), wave 3. Depends on `notify-vocabulary`,
`player-routing` and `notify-store`.

**Rulings it carries:** R-N1 (content goes only to the save's group), R-N4 (a severity above the
category's ceiling is refused), R-N5 (dedup by key), R-N6 (one batch per save per turn), R17 (the
player row is the save; map §Identity).

**Strengthen pass 2026-09-18:** a turn is published in one store transaction with its cursor; every
batch says whether it is `live` or `catch-up`, and only `live` may toast; the pump reads only a
stored report and never triggers a replay; a delve world is skipped (map §Strengthen pass S1, S2, S5).

---

## Objective

The server's application layer for notifications. It has three parts, each with one responsibility:

| Part | Responsibility | Depends on |
|---|---|---|
| `NotificationPublisher` | Validate drafts against the catalog, drop repeats inside the window, append durably, **then** push one `NotificationBatch` to each save's group | catalog, tuning, `RpgStore`, `IPlayerPush` |
| `WorldTurnNotificationPump` | For every world turn resolved since its cursor, ask each registered `IWorldTurnNotificationSource` for drafts, and publish them, one batch per save per turn, with the cursor advanced in the same transaction | the publisher, the sources, `RpgStore` |
| `NotificationEndpoints` | The catch-up page, the per-category history page and state changes (read / dismiss) | `RpgStore`, `IPlayerPush` |

**Durable first, then push.** The ideal fixes this order (§The shape rework 3, finding M3) after
`IDelveLivePush`: *"a live push is best-effort telemetry about an already-durable state change"*
(`gk-core/src/FusionRpg.Server/DelveLivePush.cs:66-70`). The publisher pushes **only** the rows the store
reports as newly inserted (`notify-store` §2). So a re-run pushes nothing, and a dropped frame is
recovered by the catch-up GET.

**Open for extension (SOLID O/D).** A new domain adds a class that implements
`IWorldTurnNotificationSource` and registers it in DI, and it does not edit the pump. The pump depends
on the interface, never on a concrete source. There is one pump per clock (`the-loops.md` §Three
clocks). v1 builds the **world-turn** pump only, because every source in this program runs on that
clock. A lawn or expedition source would bring its own pump with the same shape.

## Design

### 1. Drafts (Core, pure)

```csharp
// gk-core/src/FusionRpg.Core/Notify/NotificationDraft.cs (new)
public sealed record NotificationDraft(
    string DedupKey,          // R-N5: stable, deterministic, source-derived — never a Guid
    string CategoryId,
    NotifySeverity Severity,
    string SourceId,
    string MessageKey,
    IReadOnlyList<NotifyArg> Args,
    string? SubjectKey,       // the repeat-window key, e.g. "legion:{entityId}"
    string? WorldId,
    int? WorldTurn);
```

`NotifySeverity` and the argument types are `notify-vocabulary`'s. Core carries no transport type:
the publisher maps a draft to `NotificationDto` at the edge.

### 2. The publisher

`PublishTurn(IReadOnlyList<AddressedDraft> drafts, NotifyDelivery delivery, NotificationCursorAdvance? cursor)`,
in this order. (`Publish(saveId, drafts, delivery)` is the same call with one save and no cursor.)

1. **Validate** each draft. The category must be registered, the message key must be one of that
   category's `messageKeys`, the severity must be at or below `CeilingOf(category)`, and every argument
   kind must come from the closed set. A failure throws `NotificationContractException` naming the
   category and key. It is a code defect, and `world-notify-source`'s classifier test catches it before
   runtime.
2. **Repeat window.** Drop a draft when it has a `SubjectKey` and a `WorldTurn`, its severity is
   **not** `Critical`, and `HasRecentNotification(save, category, subject, WorldTurn -
   repeatWindowWorldTurns)` is true. A Critical is never throttled, because R-N4 exists so a Critical
   is never lost to routine traffic.
3. **Append** the survivors for every save, and the cursor, in **one** call
   (`AppendNotificationTurn`, with the injected `retainPerCategory`; `notify-store` §2). The store
   returns, per save, only the new rows that survived the prune. A crash before this call returns
   leaves nothing stored and the cursor unmoved.
4. **Push**, after the transaction committed, one `NotificationEvents.Batch` per save with a
   non-empty list, through `IPlayerPush.Push(saveId, …)`, carrying `delivery`. **Order inside the
   batch:** severity descending, then `seq` ascending. That is one fixed order, which is what R-N6
   needs for preemption to be deterministic on the client. A crash after step 3 and before step 4 loses
   only the push: the rows are stored, the cursor has moved, and the client's catch-up GET (by `rev`)
   delivers them without a toast.

**`NotifyDelivery` (closed: `Live`, `CatchUp`).** It answers one question for the client: may this
batch toast? `Live` means "this just happened". `CatchUp` means "this is late", and the client routes
it to the rail and the centre only (map §Open questions, "Does catch-up toast?"). The publisher never
decides a channel. It only labels how late the batch is.

### 3. The world-turn pump

```csharp
// gk-core/src/FusionRpg.Server/Notifications/IWorldTurnNotificationSource.cs (new)
public interface IWorldTurnNotificationSource
{
    string SourceId { get; }
    /// <summary>Drafts for ONE resolved turn, each already addressed to a player. Pure over the
    /// context plus read-only store reads; never writes, never pushes.</summary>
    IEnumerable<AddressedDraft> Collect(WorldTurnNotificationContext ctx);
}

public sealed record AddressedDraft(long SaveId, NotificationDraft Draft);   // SaveId = players.id (R17)

public sealed record WorldTurnNotificationContext(
    string WorldId,
    int ResolvedTurn,
    bool IsLatestResolved,        // forecast-style sources speak only about the newest turn
    WorldHeaderRow Header,        // RpgStore.World.cs:737-740 — its PlayerId is the SaveId
    WorldState CurrentWorld,      // post-commit state (only meaningful when IsLatestResolved)
    TurnReport? Report);          // null when the stored body was trimmed (step 4); never a replay
```

`WorldTurnNotificationPump.Run(worldId, trigger)`, where `trigger` is `Commit` or `Boot`:

1. Load the header. **A world whose `Kind` is not `map` is skipped.** A delve world never runs
   `TurnEngine.Step` (`decisions.md` "World store — delve worlds" row), so it has no turn report to
   read. Resolved turn `R = header.CurrentTurn - 1`. That is the turn the playback panel reads too
   (`WorldStage.tsx:543`, `turn={dto.currentTurn - 1}`).
2. Cursor `c = GetNotificationCursor("world-turn", worldId)`. **If it is absent,
   `InitNotificationCursor(…, R)` and return.** A world that existed before this module shipped does
   not back-fill its whole history into the feed.
3. For `t = c + 1 … R`: read the report (step 4). Build the context with `IsLatestResolved = (t == R)`.
   Collect from every source, catching and logging a failure **per source**, so one broken source
   never silences the rest. Then `PublishTurn(drafts, delivery, cursor: ("world-turn", worldId, t))`,
   which stores every save's rows for turn `t` and moves the cursor to `t` in one transaction.
   `delivery` is `Live` only when `trigger == Commit` **and** `t == R`. Every other turn is `CatchUp`:
   all turns of a `Boot` run, and the older turns of a commit run that found the cursor lagging.
4. **Stored report only, never a replay.** `GetWorldTurnReport` does not return `null` past the hot
   tail: it replays the world from turn zero (`RpgStore.WorldTurns.cs:731-771`). The replay runs
   `TurnEngine.Step` alone, so it also drops the post-Step lines Data writes (`AddPostStep`, for
   example `RpgStore.CacheRetrieval.cs:399`, `RpgStore.CargoCommands.cs:296`). The pump therefore reads
   `GetWorldTurnLog(worldId, t)` (`RpgStore.WorldTurns.cs:701`) first. If its `ReportJson` is `null`
   (trimmed; the hot tail is `ReportHotTail`, `RpgStore.WorldTurns.cs:476`), the context has
   `Report = null`. Otherwise it calls `GetWorldTurnReport`, which serves the stored body. Sources
   that need the report yield nothing for a trimmed turn, the miss is logged, and the cursor still
   moves. It only happens when the pump lagged more than the hot tail. Sources that read other durable
   tables (the cache source) still publish that turn.

**Triggers, all of them (DESIGN-GATE §2 invariant 16).** The pump's cursor is the "what has been
published" record for a world:

| Trigger | Where | Why |
|---|---|---|
| A commit that advanced | `WorldEndpoints.cs:378-382`: after `store.CommitWorldTurn(...)` returns `Advanced`, call `pump.Run(worldId)` before the response | The only path that advances a world turn today (repo grep: `CommitWorldTurn(` has one caller) |
| Server boot | A hosted startup step runs `Run(…, Boot)` for each save's active map world: `ListPlayers()` (`RpgStore.cs:1159`; once `save-identity` ships it skips archived rows, so the legacy Zomboss row is not visited), then `GetActiveWorld(saveId)` (`RpgStore.World.cs:416`, which selects `state = 'active' AND kind = 'map'` at `:424`) | Closes the crash gap between a durable commit and its notifications. Every batch it pushes is `CatchUp`, so a client that reconnected before this step ran is caught up and never toasted |
| Cursor absent | The first `Run` for a world | The key-set edge: a world entering the system. It initialises and does not back-fill |
| A new save or a new map world | No trigger of its own. Its first `Commit` run meets an absent cursor, which is the row above | Listed so the key-set edge is not mistaken for a missing trigger |

A pump failure never fails the commit response: the commit is already durable, the failure is logged,
and the cursor stays put for the next trigger. Runs for the same world are serialised by a per-world
lock, which the boot step and a commit share. The atomic per-turn append makes an overlap harmless
anyway, and the lock only stops wasted work.

**The pump never runs inside `CommitWorldTurn`'s transaction.** It runs after the commit returns, on
the committed state. So it adds no work to the turn engine and cannot change a state hash
(`StateHasher.Hash`, `RpgStore.WorldTurns.cs:653`).

### 4. REST (Server, save-scoped like `/api/pvz-stats/{playerId:long}` at `gk-core/src/FusionRpg.Server/Program.cs:975`; the path value is the `SaveId`, as `save-identity` §Contracts rules for every `{playerId}` route)

| Verb + route | Body / query | Returns |
|---|---|---|
| `GET /api/notifications/{playerId:long}` | `since` (a `rev`, long, default 0), `limit` | `NotificationPageDto { items, nextSince, hasMore }`, rev ascending. `items` holds new rows **and** rows whose state changed after `since` (`notify-store` property 4) |
| `GET /api/notifications/{playerId:long}/history` | `category` (required), `before` (a `seq`, long?), `limit`. A query parameter, not a route segment, because category ids contain dots | Same DTO, seq descending (history) |
| `POST /api/notifications/{playerId:long}/state` | `SetNotificationStateRequest { seqs: long[], state: "read" \| "dismissed" }` | `{ changed: [{ seq, rev }] }`. Pushes `NotificationStateChanged { changes: [{ seq, rev }], state }` to the save's group, so a second session of the same save stays in step. A session that misses the push gets the change from its next catch-up, because the change bumped `rev` |

An unknown save gets 404. An unregistered category on the history route gets 400 with
`reason = "category.unknown"`. `limit` is bounded by `MaxPageSize`, a **structural** const whose
comment says it is a buffer bound for one response, not a balance number (tunables-ssot T2).

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests   --filter "FullyQualifiedName~Notify"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-core/src/FusionRpg.Core/Notify/NotificationDraft.cs
gk-core/src/FusionRpg.Core/Notify/NotifyArg.cs
gk-core/src/FusionRpg.Server/Notifications/NotificationPublisher.cs
gk-core/src/FusionRpg.Server/Notifications/NotificationContractException.cs
gk-core/src/FusionRpg.Server/Notifications/IWorldTurnNotificationSource.cs
gk-core/src/FusionRpg.Server/Notifications/WorldTurnNotificationPump.cs
gk-core/src/FusionRpg.Server/Notifications/NotificationBootCatchUp.cs      → hosted startup step
gk-core/src/FusionRpg.Server/NotificationEndpoints.cs
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                             → one pump.Run call after an advancing commit
gk-core/src/FusionRpg.Server/Program.cs                                    → DI + MapNotificationEndpoints
gk-core/src/FusionRpg.Contracts/NotificationDtos.cs                        → NotificationPageDto, SetNotificationStateRequest
gk-core/tests/FusionRpg.Server.Tests/Notifications/*.cs
```

## Code style

```csharp
public void PublishTurn(IReadOnlyList<AddressedDraft> drafts, NotifyDelivery delivery, NotificationCursorAdvance? cursor)
{
    foreach (var d in drafts) _contract.Validate(d.Draft);          // loud: a defect, not a runtime choice
    var perSave = drafts.Where(d => !_repeat.Suppresses(d.SaveId, d.Draft))
        .GroupBy(d => d.SaveId)
        .Select(g => new NotificationSaveAppend(g.Key, g.Select(d => ToInsert(d.Draft)).ToList()))
        .ToList();
    var inserted = _store.AppendNotificationTurn(perSave, _tuning.RetainPerCategory,
        _clock.UtcNowIso(), cursor);                                // durable FIRST, cursor in the same tx
    foreach (var (saveId, rows) in inserted)
    {
        if (rows.Count == 0) continue;                              // a re-run pushes nothing
        var batch = rows.OrderByDescending(r => r.Severity).ThenBy(r => r.Seq).Select(ToDto).ToList();
        _push.Push(saveId, NotificationEvents.Batch,
            new NotificationBatchDto { PlayerId = saveId, Delivery = delivery, Items = batch });
    }
}
```

## Testing strategy

Server.Tests with the in-memory store and fake `IPlayerPush` / fake sources, with no live SignalR,
following the `IDelveLivePush` precedent (`DelveLivePush.cs:48-52`).

1. **Durable before push.** The fake push looks the row, and the cursor, up in the store at the
   moment it is called, and both must already be there.
2. **Idempotent.** Publishing the same drafts twice pushes once. Running the pump twice over the same
   turn pushes once.
3. **Routed.** Drafts for saves 1 and 2 in one pump run produce two batches, each to its own
   `PlayerGroup`, and nothing to `WebGroup`.
4. **Contract refusals.** An unregistered category, an undeclared message key, a severity above the
   ceiling, or an unknown argument kind each throw `NotificationContractException` naming the key.
5. **Repeat window.** A routine draft inside the window is dropped. The same draft marked Critical is
   kept. A draft with no subject is never dropped.
6. **Batch order.** A batch built from shuffled inserts is ordered severity descending, then seq
   ascending. The test covers two input orders.
7. **Pump cursor.** An absent cursor initialises to `R` with no publish. A cursor at `R - 2` publishes
   two turns in order and ends at `R`. A throwing source does not stop a second source or the cursor.
   A trimmed turn (`ReportJson = null`) advances the cursor and never calls a replay (a fake store
   fails the test if `GetWorldTurnReport` is called for a trimmed turn). A delve-kind world is skipped.
8. **Crash between store and push.** A fake push that throws after `AppendNotificationTurn` returned
   leaves rows and cursor stored. A second run pushes nothing, and the catch-up GET returns the rows.
9. **Delivery label.** A commit run over a cursor at `R - 2` pushes turn `R - 1` as `CatchUp` and `R`
   as `Live`. A boot run pushes only `CatchUp`. A boot run and a commit run on the same world, in
   either order, end at `R` with each row stored once.
10. **Commit coupling.** A pump that throws still lets `/commit` return `Ok` with `Advanced = true`.
11. **REST.** Unknown save → 404. `since` paging by `rev` has no gap and no repeat, and a state change
    made by another session appears after the cursor. The state POST pushes `NotificationStateChanged`
    to that save's group only.

## Boundaries

- **Always:** append before push; push only inserted rows; one batch per save per turn; advance the
  cursor only inside the append's transaction; label every batch `Live` or `CatchUp`; register new
  sources through DI.
- **Ask first:** a second pump (a new clock); any content push that bypasses `IPlayerPush`.
- **Never:** text on the server; a `Guid` or wall-clock value in a dedup key; back-filling history
  on cursor initialisation; failing a world commit because notifications failed; a `Live` batch from
  a boot run or a lagging turn; triggering a report replay; SQL here (`guard-dal.py`).

## Success criteria

1. Tests 1–11 green.
2. The only change to `WorldEndpoints.cs` is the pump call after an advancing commit.
3. `verify-change.ps1` and `guard-dal.py` green.
4. Map gate **G1** (routed and durable) holds end to end with `player-routing` in place.

## Seedsmith / generator

None. Validation, persistence orchestration and transport, with no content.

## Open questions

None. The order (durable, then push), the batch (R-N6) and the routing (R-N1, R17) are all ruled. The
cursor-without-back-fill rule, the atomic turn and the delivery label are technical, and each follows
from a named failure (the GG-50 volume concern, ideal finding C1; map §Strengthen pass S1, S2).

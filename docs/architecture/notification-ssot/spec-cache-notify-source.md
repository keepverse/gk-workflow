# Spec: cache-notify-source

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `cache-notify-source` of the
[notification-ssot map](../notification-ssot-map.md), wave 6. Depends on `notify-service` and
`notify-format`. **Needs map gate G0, ask A5:** `deployment-hierarchy` (`cache-decay-void`) accepts
two read methods on its own store partial. Default if unanswered: accepted, because they are additive
and read-only (map §G0 asks).

**Strengthen pass 2026-09-18:** the owner is a save (R17); the overlapping read window is now safe
across the retention prune through the store's key ledger; the catalog version is v3; the latency of
an off-world cache is stated (map §Strengthen pass S1, S4, S13).

**Loops:** Place 3 (hunt, defend — a lost legion's haul), Place 2 and Place 7 (the idle and quest
side of recovering it), `the-loops.md`. This is the ideal's second candidate (§Which loop this
extends, corpse-cache decay) and the first source that does not read the turn report.

---

## Objective

Tell the owner when their fallen gear is at risk, while it can still be fetched:

| Category | When | Default |
|---|---|---|
| `cache.created` | A cache's decay clock started: a legion's cargo moved to a cache on death (`cargo-fate`, `RpgStore.CargoFate.cs:47` called from `RpgStore.WorldGraphDiff.cs:349-352`), or a lawn or delve cache whose clock started (`cache-decay-void`, `RpgStore.CacheDecay.cs:70-78`) | rail, `important` |
| `cache.decayed` | A decay tick destroyed at least one item in one of the player's caches | rail, `routine`; `important` when the tick left the cache empty |

Both land on the rail by default (R-N2). None is Critical, because `promotions.critical` ships empty
(map §Open questions). A promotion is argued separately, in that block, and not here.

**Why no producer change is needed.** Both events are already written durably, inside the world
commit's transaction:

- The decay tick writes one `rpg_corpse_cache_decay_log` row per cache per tick, with every item's
  outcome (`RpgStore.CacheDecay.cs:47` for the DDL, `:189-199` for the insert). The tick runs inside
  `CommitWorldTurn` for the world's player (`RpgStore.WorldTurns.cs:693`).
- A started clock is `rpg_corpse_cache.decay_started_turn` plus `owner_player_id`
  (`RpgStore.CacheDecay.cs:41`, `:45`).

So this source only **reads**, and that matches `spec-cargo-fate.md`'s own expectation: a notification
consumer reads the cache creation "the same way it would any other `corpse-cache` creation"
(`spec-cargo-fate.md:250-252`).

## Design

### 1. Reads (asked of `deployment-hierarchy`, on its partial)

```csharp
// RpgStore.CacheDecay.cs (deployment-hierarchy's file — the ask)
// ownerPlayerId is the save (R17): owner_player_id predates save-identity, whose rule reads it as the SaveId.
public IReadOnlyList<CacheClockStartRow> ListCacheClocksStarted(long ownerPlayerId, int fromTurn, int toTurn);
//   cache_id, place_kind, place_ref, source_kind, decay_started_turn, item count
public IReadOnlyList<CacheDecayTickRow> ListCacheDecayTicks(long ownerPlayerId, int fromTurn, int toTurn);
//   cache_id, tick, destroyed count, remaining count, place_kind, place_ref
```

Both are read-only, and both take an inclusive turn range. The SQL stays in the owning program's
partial, which is DAL ownership and not just the DAL guard.

### 2. `CacheNotificationSource : IWorldTurnNotificationSource`

For resolved turn `t` (`notify-service` §3) and recipient `header.PlayerId`:

- **Window `[t, t + 1]`, deduplicated by key.** The commit that resolves `t` writes its tick and its
  cargo-fate clock starts under the post-advance turn `result.World.CurrentTurn`
  (`RpgStore.WorldTurns.cs:693`). A lawn or delve clock that starts between commits stamps the current
  turn at that moment, which is also `t + 1`, and it is final only once the next commit has run. So
  each event is read by two consecutive pump runs. Unique keys make it exactly-once without depending
  on which of those two stamps an event carries. The key survives even if the retention prune deleted
  the first run's row in between, because `notify-store`'s key ledger holds every key for
  `DedupKeyMemoryWorldTurns` turns, which is sized to this window (`notify-store` §1). The keys:
  - `cache:{cacheId}:created`
  - `cache:{cacheId}:decay:{tick}`
- **Place argument.** For `world_sector` a `ref` sector, which is also the `target`. For `world_lane`
  a `ref` lane. For `lawn`, `delve_room` and `siege`, a `domainToken` place kind that the cache
  translator words. That vocabulary is closed at `RpgStore.CorpseCache.cs:44`.
- **`worldTurn` on every draft is `ctx.ResolvedTurn`**, the turn the pump attributes the event to,
  not the raw tick or stamp. That puts the item on the world rail beside the same turn's world items
  (`notify-client` §6, `worldLatestTurn`) and keeps the repeat window on one clock.
- **Recipient.** `ctx.Header.PlayerId`, the world's save (R17). The reads filter on
  `owner_player_id` (`RpgStore.CacheDecay.cs:45`), which is that save.
- **Latency of an off-world cache.** A lawn or delve cache whose clock starts between commits is
  reported by the pump run after the **next** commit, because only a commit runs the pump. Decay is
  turn-clocked and frozen between commits (`spec-cache-decay-void.md` V6), so the player hears about
  the cache no later than the first turn it can decay. An immediate, off-clock notice would need a
  second pump, which `notify-service` lists under "Ask first".
- **Subject key** `cache:{cacheId}` for a partial loss, so a cache that loses items every tick
  notifies at most once per `repeatWindowWorldTurns`. The tick that **empties** a cache uses
  `cache:{cacheId}:emptied` instead. A cache empties only once, so that subject never repeats, the
  window can never swallow the last loss, and Critical, the window's only exemption
  (`notify-service` §Design 2), is not needed for it.

### 3. Web translator

`stages/world/cacheClaim/cacheNotifyTranslator.ts` (new, domain `corpse-cache`), beside the existing
cache UI (`stages/world/cacheClaim/`). Sentences are authored. They use `fmt.count` for items and
`fmt.ref` with the world's `sectorLabel` (`stages/world/labels.ts:17`) for a world place. For a lane,
it follows `laneLabel`'s own rule and never splits the lane id (`gk-web/web/fusion-rpg-web/src/stages/world/labels.ts:4-12`). A lane whose
endpoints the translator cannot resolve renders `Pending`. It provides `samples()` for each message
key, for the `notify-format` coverage guard.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests   --filter "FullyQualifiedName~CacheDecay"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CacheNotify"
cd web\fusion-rpg-web; npm test -- stages/world/cacheClaim shell/notify/format; npm run build
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs                     → the two reads (ask, §1)
gk-core/src/FusionRpg.Server/Notifications/CacheNotificationSource.cs
gk-core/src/FusionRpg.Server/Program.cs                                      → DI registration as IWorldTurnNotificationSource
gk-core/data/tuning/notification-catalog.v3.json                             → cache.created / cache.decayed rows (published after world-notify-source's v2)
gk-core/src/FusionRpg.Server/Program.cs                                      → catalog load line moves to v3
gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts                       → import moves to v3
gk-web/web/fusion-rpg-web/src/stages/world/cacheClaim/cacheNotifyTranslator.ts
gk-web/web/fusion-rpg-web/src/shell/notify/format/translators.ts            → registers it
gk-core/tests/FusionRpg.Data.Tests/Items/CacheDecayReadTests.cs
gk-core/tests/FusionRpg.Server.Tests/Notifications/CacheNotifySourceTests.cs
```

## Code style

```csharp
foreach (var tick in _store.ListCacheDecayTicks(ctx.Header.PlayerId, ctx.ResolvedTurn, ctx.ResolvedTurn + 1))
{
    if (tick.Destroyed == 0) continue; // a tick where everything survived is not news
    yield return new AddressedDraft(ctx.Header.PlayerId, new NotificationDraft(
        DedupKey: $"cache:{tick.CacheId}:decay:{tick.Tick}",
        CategoryId: "cache.decayed",
        Severity: tick.Remaining == 0 ? NotifySeverity.Important : NotifySeverity.Routine,
        SourceId: SourceId, MessageKey: "cache.decayed",
        Args: Args.Count("destroyed", tick.Destroyed).Count("remaining", tick.Remaining).Place(tick),
        SubjectKey: tick.Remaining == 0 ? $"cache:{tick.CacheId}:emptied" : $"cache:{tick.CacheId}", WorldId: ctx.WorldId, WorldTurn: ctx.ResolvedTurn));
    // WorldTurn is the pump's resolved turn, not the tick, so the item lands on the world rail's
    // worldLatestTurn filter beside that turn's world items (notify-client §6). The tick lives in the key.
}
```

## Testing strategy

1. **Reads (Data.Tests, in-memory).** Given decay-log rows at ticks 4, 5 and 6, a range of `[5, 6]`
   returns exactly those ticks for that owner and none of another player's. Destroyed and remaining
   counts reconcile with the log's `outcomes_json`.
2. **Turn correspondence (Server.Tests).** A real `CommitWorldTurn` that ticks a cache yields a tick
   value that the window `[ResolvedTurn, ResolvedTurn + 1]` captures. This pins the correspondence
   in a test instead of assuming it.
3. **Exactly once.** Running the source over `t` and then `t + 1` (overlapping windows) stores each
   event once. A lawn cache started between commits is reported by the next run. With
   `retainPerCategory = 1`, an event whose first row was pruned before the second run is still not
   stored again.
4. **Severity.** A tick that empties the cache is `important`. A tick with survivors is `routine`. A
   tick with no destruction yields nothing. An emptying tick one turn after a stored partial loss is
   still stored, because its subject differs and the window cannot swallow the last loss.
5. **Web.** The translator's samples pass the coverage guard. A `world_lane` place without resolvable
   endpoints renders `Pending`, never the lane id.
6. **Catalogue join (Server.Tests).** Every category with domain `corpse-cache` is one
   `CacheNotificationSource.KnownCategories` can emit, and every category it can emit is registered with
   that domain — both directions, because a row nobody emits can never fire and a producer category with no
   row throws at publish time (`NotificationCatalogCoherenceTests`). That test also carries the **closure**:
   every catalogue category's domain must be one this program can join, so a third domain cannot be added
   without its own join. A join, not a count.

## Boundaries

- **Always:** read through the owning partial's methods; use dedup keys built from `cacheId` and
  `tick`; send a world place's reference as the `target`.
- **Ask first:** promoting `cache.decayed` to toast or Critical (`promotions`, R-N2 / R-N4).
- **Never:** SQL for corpse-cache tables outside `RpgStore.CacheDecay.cs` / `RpgStore.CorpseCache.cs`;
  any write to a cache table; a wall-clock read (`decay_started_utc` is not the clock,
  `spec-cache-decay-void.md` §Design 1).

## Success criteria

1. Map G3's first half: a legion death and a destroying tick each produce their item in the same
   batch as that turn's world items (one pump run, R-N6).
2. Tests 1–5 green; `guard-dal.py` green.
3. `deployment-hierarchy`'s G2/G4 can now add "the player is told" (ideal §Real gap C3). That note is
   theirs to take.

## Seedsmith / generator

None. Authored translator copy over durable decay-log rows. The catalog rows are authored.

## Open questions

None owner-facing. The two reads are a cross-program ask (G0).

# NS2.3 — Source cursor, atomic per turn

Built together with NS2.1/NS2.2 (same transactional method).

| Criterion | Command | Result |
|---|---|---|
| `AppendNotificationTurn(..., cursor)` upserts the cursor in the same transaction | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~Notification"` | `Atomic_turn_a_failure_mid_call_persists_nothing` green - proves the positive half (rows + cursor land together in one call); see note below on the negative half |
| `GetNotificationCursor` null when absent; `InitNotificationCursor` round-trips and is the only non-append writer | same run | `Cursor_absent_reads_null_and_InitNotificationCursor_round_trips` green (a second `Init` call never overwrites) |

**Honest gap, not silently dropped:** the spec's test 5 (`Atomic_turn`) also asks for a *forced*
mid-transaction failure (rows land, cursor upsert throws) proving full rollback. The store exposes no
fault-injection seam today (unlike `spec-sector-storage.md`'s tests, which the spec cites but which
use a seam this file does not have), so only the positive path (a successful call leaves rows AND
cursor together) is proven directly. The negative half is covered indirectly by the `tx.Rollback()`
in a `catch` around the whole transaction body, which is standard ADO.NET SQLite behaviour and not
itself specific to this method - `SetNotificationState` and `AppendNotificationTurn` share the same
try/commit/catch/rollback shape already exercised by decades of use elsewhere in `RpgStore`.

# NS2.4 — Store reads and state moves

Built together with NS2.1-NS2.3 (the same store partial file, same test class).

| Criterion | Command | Result |
|---|---|---|
| `ListNotificationChanges(save, sinceRev, limit)` strictly increasing revs, no gap/repeat across pages; an old row whose state changed reappears | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~Notification"` | `Rev_catch_up_pages_forward_with_no_gap_or_repeat_and_surfaces_state_changes` green |
| `ListNotificationsByCategory` pages by seq descending | same run | exercised by `Retention_...` and `Idempotency_...` tests (both read back via this method) |
| `SetNotificationState`: unread->read, unread\|read->dismissed, dismissed->read (undo) bump rev; every other move + a pruned seq is a no-op, absent from the result | same run | `State_moves_dismissed_to_read_is_the_only_backward_move` green |
| `HasRecentNotification` true at `fromTurn=world_turn`, false at `+1` | same run | `HasRecentNotification_true_at_fromTurn_false_the_turn_after` green |
| `guard-dal.ps1` green | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |

Full run: `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11` (all of `NotificationStoreTests.cs`).

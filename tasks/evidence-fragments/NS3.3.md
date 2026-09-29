# NS3.3 — World-turn pump and the source seam

| Criterion | Command | Result |
|---|---|---|
| `IWorldTurnNotificationSource`, `AddressedDraft`, `WorldTurnNotificationContext`; non-`map` skipped; absent cursor -> Init(R), no publish; cursor at R-2 publishes two turns in order, ends at R | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.WorldTurnPumpTests"` | `Passed! - Failed: 0, Passed: 9, Skipped: 0, Total: 9` |
| reads `GetWorldTurnLog(...).ReportJson` first; a trimmed turn gets `Report=null`, advances the cursor, never calls a replay | same run | `A_trimmed_turn_advances_the_cursor_and_never_replays` (forces `TrimWorldTurnReports(keepLast:0)`, asserts the source's own `ctx.Report is null`) |
| `Live` only for `trigger==Commit && t==R`; every other turn `CatchUp`; a per-world lock serialises runs | same run | `Delivery_label_commit_pushes_the_newest_turn_Live_and_older_turns_CatchUp`, `A_boot_run_pushes_only_CatchUp` |
| a throwing source never silences a second source or the cursor | same run | `A_throwing_source_does_not_stop_a_second_source_or_the_cursor` |

**Off-by-one self-caught while writing these tests:** `R = header.CurrentTurn - 1` after N commits is
`N - 1`, not `N` - three tests' expected turn numbers were wrong on the first draft (traced by hand
against `WorldTurnCommitTests`'s own `CurrentTurn` semantics, fixed before committing).

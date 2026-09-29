# NS3.7 — Gate G1 end to end: routed and durable

| Criterion | Command | Result |
|---|---|---|
| routing+store+publisher+pump composed (fake sources, in-memory store): a draft for save A stored before any push, reaches only `player:A`; re-publishing (incl. after its row was pruned) stores/pushes nothing | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.NotificationG1Tests"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` - `A_draft_for_save_A_is_stored_before_any_push_and_reaches_only_player_A`, `Republishing_the_same_draft_including_after_its_row_was_pruned_stores_and_pushes_nothing` |
| a crash injected between commit and push leaves rows+cursor, catch-up GET delivers them; a connection joining after the push still gets the row by GET; a boot run pushes only CatchUp | same run | `A_crash_between_commit_and_push_leaves_rows_and_cursor_and_the_catchup_GET_delivers_them`, `A_connection_that_joins_after_the_push_still_gets_the_row_through_the_catchup_GET`, `A_boot_catch_up_run_produces_no_toast_delivery_label` |

Built against a REAL `HubPlayerPush` over a live SignalR TestServer (not a fake), plus a real REST
catch-up GET - the map's own G1 gate, proven end to end rather than piece by piece.

Closes Checkpoint 3.

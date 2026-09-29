# NS3.5 — Boot catch-up step

| Criterion | Command | Result |
|---|---|---|
| hosted startup step runs `Run(..., Boot)` for each save's active map world (`ListPlayers()` -> `GetActiveWorld(saveId)`); every batch it pushes is `CatchUp` | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.NotificationBootCatchUpTests"` | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3` |
| a boot run and a commit run on the same world, in either order, end at R with each row stored once | same run + `WorldTurnPumpTests.A_boot_run_and_a_later_commit_run_end_at_R_with_each_row_stored_once` | one row stored despite three pump runs (Boot, Commit, Boot again) touching the same world |
| a save with no active world is skipped without error; a boot step with nothing to do still completes | same run | `A_save_with_no_active_world_is_skipped_without_error`, `A_failing_world_never_blocks_the_boot_step_from_starting` |

Registered as `builder.Services.AddHostedService<NotificationBootCatchUp>();` in `Program.cs`, beside
the tuning/DI wiring NS3.1-NS3.3 added.

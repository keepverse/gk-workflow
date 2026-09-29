# NS7.1 — `JoinPlayer` refuses an archived save

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `JoinPlayer` on an archived row returns `false`, reading the same filter `ListPlayers` uses | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting\|FullyQualifiedName~NotificationBootCatchUp"` | `Passed! - Failed: 0, Passed: 10, Skipped: 0, Total: 10` — `JoinPlayer_refuses_an_archived_row_and_joins_nothing` asserts `ListPlayers` excludes the archived id, `JoinPlayer` returns `false`, and a push to it reaches no connection | gk-core/src/FusionRpg.Server/RpgHub.cs |
| the boot catch-up (NS3.5) skips the legacy Zomboss row by that same filter (assert it is not visited) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting\|FullyQualifiedName~NotificationBootCatchUp"` | `Passed! - Failed: 0, Passed: 10` — `An_archived_row_is_never_visited_by_the_boot_catch_up` asserts the live world's cursor is initialised (`1`) and the archived world's cursor is untouched (`null`) | gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationBootCatchUpTests.cs |
| boundary command + guards | `.\scripts\verify-change.ps1 -Paths 'gk-core/src/FusionRpg.Server/RpgHub.cs','gk-core/tests/FusionRpg.Server.Tests/PlayerRoutingTests.cs','gk-core/tests/FusionRpg.Server.Tests/Notifications/NotificationBootCatchUpTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; `Passed! - Failed: 0, Passed: 733, Skipped: 0, Total: 733, Duration: 3 m 10 s` | — |

`JoinPlayer`'s predicate is now `RpgStore.IsLiveSave` (`SELECT COUNT(*) FROM players WHERE id=$p AND
archived_utc IS NULL`), the same filter `ListPlayers` (`RpgStore.cs:1221`) and `SetCurrentPlayer` use.

**NOT proved:** no live probe of a real archived save (NS7.1's Verify line is the two test filters
above); this lane did not re-run `gk-core/tests/FusionRpg.Data.Tests` migration tests — `IsLiveSave` itself is
unchanged and already covered there (`SaveEmpiresStoreTests`, `SaveIdentityMigrationTests`).

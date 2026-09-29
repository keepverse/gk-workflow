# NS3.6 — REST: catch-up, history, state

| Criterion | Command | Result |
|---|---|---|
| `GET /api/notifications/{playerId}?since=&limit=` rev asc (new rows + state changes); `GET .../history?category=&before=&limit=` seq desc, 400 `category.unknown`; `POST .../state` returns `{changed:[{seq,rev}]}`; unknown save 404; `limit` bounded by structural `MaxPageSize` | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.NotificationEndpointsTests"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` |
| the state POST pushes `NotificationStateChanged` to that save's group only; `since` paging has no gap/repeat and shows another session's state change after the cursor | same run | `The_state_POST_pushes_NotificationStateChanged_to_that_saves_group_only`, `Since_paging_by_rev_has_no_gap_or_repeat`, `A_state_change_made_by_another_session_appears_after_the_cursor` |
| `guard-dal.ps1` green | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |

`MaxPageSize = 200` carries the structural (not tunable) comment per tunables-ssot T2 - a response
buffer bound, not a balance number.

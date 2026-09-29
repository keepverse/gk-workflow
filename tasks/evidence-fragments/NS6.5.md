# NS6.5 — Gate G3 first half: cache items ride the same batch as the turn's world items

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| in-memory store: a legion death that starts a cache produces `cache.created`, and a destroying tick produces `cache.decayed`, each in the **same** `NotificationBatch` as that turn's world items (one pump run, R-N6) | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CacheNotify"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` — `Cache_items_ride_the_same_batch_as_that_turns_world_items` asserts `Assert.Single(_push.Pushes)` (one batch, not one per source), `NotifyDelivery.Live`, and that the one batch carries `loam.shortfall` **and** `cache.created` **and** `cache.decayed`, each with `WorldTurn == 1` | gk-core/tests/FusionRpg.Server.Tests/Notifications/CacheNotifyEndToEndTests.cs |
| boundary command + guard | `.\scripts\verify-change.ps1 -Paths 'gk-core/tests/FusionRpg.Server.Tests/Notifications/CacheNotifyEndToEndTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; scopes `guard: dal`, `test: server`; `Passed! - Failed: 0, Passed: 751, Skipped: 0, Total: 751, Duration: 2 m 4 s` | — |

Both sources are the real ones (`CacheNotificationSource` + `WorldReportNotificationSource`) behind the
real pump and publisher, driven by the real `POST /api/world/{worldId}/commit` route, and the catalog
and tuning are the SHIPPED files (`notification-catalog.v3.json`, `notification.v1.json`) — so both
domains' words are validated exactly as the host validates them. The world item comes from the real loam
pressure phase on the starving-homeworld fixture (NS5.12's), the cache half from a cache whose clock
started at the resolved turn plus a destroying tick stamped `t+1`, which is the tick number
`CacheNotificationSource`'s own window comment names.

**The destroying tick is seeded, not rolled** — survival is 994/1000, so a real roll could not be
counted on to destroy anything inside ONE publishing run, and a retry loop would publish further turns
(the opposite of what this row asserts). The seeded row uses the tick's own shape and its own
`(cache_id, tick)` key, which also makes the real tick loop skip that cache (its own
`NOT EXISTS … tick = $t` guard), so nothing double-inserts.

**NOT proved:** no live probe — that is NS5.13's own acceptance; and the cache clock start is inserted
by raw SQL (no `InternalsVisibleTo` grant from `FusionRpg.Data` to `FusionRpg.Server.Tests`), the same
setup convention `CacheNotifySourceTests` and `CacheDecayTests` already use.

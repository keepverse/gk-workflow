# NS5.12 — Server end to end: a real commit's shortfall reaches only its player

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| in-memory store, existing world-endpoint fixture: a commit that starves a component -> exactly one `NotificationBatch` to the world's save, `delivery = live`, carrying a `loam.shortfall` item whose `worldTurn` is the resolved turn; nothing to any other save | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify"` | `Passed! - Failed: 0, Passed: 12, Skipped: 0, Total: 12` — `A_real_commit_that_starves_a_component_pushes_one_live_batch_for_its_own_save_only` asserts `Assert.Single(_push.Pushes)`, `push.SaveId == new SaveId(_save)`, `batch.PlayerId == _save`, `NotifyDelivery.Live`, one item with `Category == "loam.shortfall"`, `WorldTurn == 1`, `MessageKey == "world.turn-entry"`, an `entry` domainToken arg, and no push for the second save | gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifyEndToEndTests.cs |
| running the pump again over the same turn pushes nothing | same run | `Running_the_pump_again_over_the_same_turn_pushes_nothing` — after the live push, `_pump.Run(WorldId, WorldTurnTrigger.Boot)` leaves `_push.Pushes.Count` unchanged | as above |
| boundary command + guard | `.\scripts\verify-change.ps1 -Paths 'gk-core/tests/FusionRpg.Server.Tests/Notifications/WorldNotifyEndToEndTests.cs' -Session notification-ssot-20260920` | `DAL GUARD OK`; scopes `guard: dal`, `test: server`; `Passed! - Failed: 0, Passed: 750, Skipped: 0, Total: 750, Duration: 3 m 5 s` (the `notify-server-domain` module scope) | — |

The chain is real end to end: `POST /api/world/{worldId}/commit` (the real route) -> the real pump ->
the REAL `WorldReportNotificationSource` -> the real publisher -> the fake push. The catalog and tuning
are the SHIPPED files (`notification-catalog.v3.json`, `notification.v1.json`), so the batch's words are
the ones the real host validates.

The starvation fixture turns the shipped first-light template's homeworld into a developed, dangerous,
empty sector (`LoamStock = 0, DevelopmentLevel = 10, DangerBand = 24` — `LoamForecastTests`' own proven
starving shape) before `CreateWorld`, so every other element (seats, lanes, legions, the other two
factions) stays exactly as shipped and the entry comes from the real loam pressure phase.

**NOT proved:** no live probe — that is NS5.13's own acceptance (a real server, a real screen); this is
the in-memory equivalent of the same chain, not a substitute for it.

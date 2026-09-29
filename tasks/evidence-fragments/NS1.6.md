# NS1.6 — `JoinPlayer` and the connection registry

| Criterion | Command | Result |
|---|---|---|
| `RpgConstants.PlayerGroupPrefix`/`PlayerGroup(id)`; `JoinPlayer` refuses unknown id, never reads `current_player_id`, moves the connection out of its previous group | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~PlayerRouting"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` (real `HubConnectionBuilder` clients against a live TestServer, matching `AptitudesInjectorBroadcastTests`'s house style) |
| `PlayerConnectionRegistry` singleton, in-memory, never persisted; `OnDisconnectedAsync` removes the entry | same run | `Disconnect_clears_the_registry_entry` green |
| `guard-dal.ps1` green (no SQL added) | `.\scripts\guard-dal.ps1` | `DAL GUARD OK - no SQLite/SQL outside FusionRpg.Data` |

**Regression found and fixed in the same change:** `RpgHub`'s new constructor parameter broke every
test file that constructs its own minimal DI container and a real `RpgHub` instance (6 files, 11
tests): `ActorSheetHotLiveStateTests`, `AptitudesInjectorBroadcastTests`,
`CommanderSnapshotBroadcastTests`, `PassiveTreeEndpointsTests`, `SpeciesBuildEndpointsTests`,
`UniqueActorAtomRepushTests`. Each gets one added line,
`builder.Services.AddSingleton<PlayerConnectionRegistry>();`. Full `Server.Tests` project:
`Passed! - Failed: 0, Passed: 566, Skipped: 0, Total: 566`.

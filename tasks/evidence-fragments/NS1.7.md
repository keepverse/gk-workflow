# NS1.7 — `IPlayerPush` seam and the isolation test (R-N1)

| Criterion | Command | Result |
|---|---|---|
| `IPlayerPush`/`HubPlayerPush` shaped like `IDelveLivePush`; DI singletons in `Program.cs` | code review | `PlayerPush.cs` mirrors `DelveLivePush.cs`'s doc-comment precedent verbatim; `Program.cs` registers `IPlayerPush -> HubPlayerPush` beside `IDelveLivePush -> HubDelveLivePush` |
| a push to save 1 reaches only save 1's connection; a fake `IHubContext` shows routing to `PlayerGroup(id)`, never `WebGroup`/`Clients.All` | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~PlayerRouting"` | `Isolation_a_push_to_save_1_reaches_only_save_1_s_connection` and `HubPlayerPush_never_reaches_a_connection_joined_only_to_WebGroup` green (real `IHubContext<RpgHub>`/`HubPlayerPush`, not a fake - a real push through a live TestServer) |
| two connections joined as saves 1 and 2 - a push to 1 reaches only the first | same run | same isolation test, quoted: `receivedA` true, `receivedB` still false after a 200ms grace window |

Determinism: the whole `PlayerRoutingTests` file (5 tests, real async SignalR + disconnect timing)
run twice back to back, `Passed! - Failed: 0, Passed: 5` both times.

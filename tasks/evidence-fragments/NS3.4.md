# NS3.4 — Commit trigger: pump after an advancing commit

| Criterion | Command | Result |
|---|---|---|
| only change to `WorldEndpoints.cs` is one `pump.Run(worldId, Commit)` after `CommitWorldTurn` returns `Advanced`, outside its transaction | `git diff features/mega-merge -- gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (this lane's own diff) | one new parameter + a 4-line try/catch calling `notifyPump.Run(...)` right after the existing `WorldUpdated` broadcast; no other line touched |
| a pump that throws still lets `/commit` return `Ok` with `Advanced=true`; the cursor still moved from the append that ran before the throwing push | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.WorldTurnPumpCommitTests"` | `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2` |

**Regression found and fixed in the same change:** ASP.NET Core's minimal-API route compiler infers
every mapped route's parameters eagerly, so the new `notifyPump` parameter broke EVERY test file that
calls `app.MapWorld()` in its own DI container - 16 files (a non-recursive first grep missed the one
under `WorldClaimEndpoints/`, caught by a full-suite run), 88 tests, all failing at host startup
(`Failure to infer one or more parameters`), not just tests that hit `/commit`. Fixed with one shared
`AddNotificationEndpointStubs()` extension (harmless stub services, never exercised by these files)
plus `[Collection("NotificationHub")]` on 15 of them (the 16th, `WorldMarchCostProjectionTests`,
already belongs to `SpeciesCatalogSwapCollection` - xUnit allows only one collection per class, so it
keeps its own; the residual race against my catalog config is a single reference-assignment with
equivalent content either way, so a race is behaviorally harmless). All 16 files:
`Passed! - Failed: 0, Passed: 66, Skipped: 0, Total: 66` (44 + `ClaimEndpointsTests` 22).

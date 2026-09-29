# EP4.7 — `GET /api/players/{playerId}/empires/{empireId}/level` and the `EmpireLevelUp` broadcast

Commit `@EP4.7` (two commits: the route, then the broadcast proof) · session `empire-progression-3` · branch `cmdc/ep-3` ·
spec `docs/architecture/empire-progression/spec-empire-level.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The route returns `{empireId, level, xp, xpToNext, highestLevel, freeRespecStock, freeRespecsPerLevel}` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~EmpireEndpoints"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` | `gk-core/src/FusionRpg.Server/EmpireEndpoints.cs` (new), `gk-core/tests/FusionRpg.Server.Tests/EmpireEndpointsTests.cs` (new) |
| Against a REAL in-process host, not a mock | same | the harness builds a minimal `WebApplication` on a loopback port, maps the route and the real hub, `AptitudeEndpointsTests`/`CommanderSnapshotBroadcastTests`' own pattern | same |
| A fresh empire reads level 1 with an empty stock, `xpToNext` from the loaded curve | same | `A_fresh_empire_reads_level_one_with_an_empty_stock` | same |
| A credited empire reads its level and the stock it paid for | same | `A_credited_empire_reads_its_level_and_the_stock_it_paid_for` — one real `AppendPvzActivityFact` placement credits the empire (level > 1, stock > 0) and the read matches the stored row | same |
| An unknown player reads 404 | same | `An_unknown_player_reads_404` | same |
| **`EmpireLevelUp` fires once per empire level crossed, after commit, with its grants** | same | `A_level_crossing_broadcasts_one_EmpireLevelUp_per_level_with_its_grants`: a REAL SignalR client joins the web group, the credit's own returned dirties are broadcast through the host's own `IHubContext`, and the test asserts one message per queued crossing with its `(levelBefore, levelAfter)` pair, its `playerId`, its `empireId`, a positive `freeRespecStock`, and a `FreeEmpireRespec` grant of the published amount — then waits a beat to prove no extra message arrived | `EmpireLevelBroadcast` in `EmpireEndpoints.cs`, called by `Program.cs`'s fact-ingest loop |
| The existing `/api/rpg/progression/{playerId}/empire/0` accepts `empire` | same | `The_generic_progression_read_accepts_the_empire_kind` asserts the read that route performs by the kind string a caller would pass, plus `RpgActorKinds.IsKnown("empire")`. The route's own lambda is `Program.cs`'s and this minimal host maps only the route under test, so the URL itself is not exercised here — the route needs no change (it passes its kind straight through) | — |
| Path-owned boundary | `.\scriptserify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/EmpireEndpoints.cs','gk-core/src/FusionRpg.Server/Program.cs','gk-core/tests/FusionRpg.Server.Tests/EmpireEndpointsTests.cs') -Session empire-progression-3` | **exit 0** — `DAL GUARD OK` and `Server.Tests 774/774`. The Server boundary is not sharded, so this row never hit the TVB-F6 empty-exit misreport the Data boundary produced all session | — |

**How the broadcast was proven, and the seam that makes it checkable.** The emission is three lines that belong to a route
lambda in `Program.cs`, so a test that had to reach the payload through the whole host would be testing the host. It is now a
named public seam, `EmpireLevelBroadcast.SendEmpireLevelUpsAsync` + `Payload`, called by that route loop (the production caller,
which sends it after the append committed) and by the test with the host's own `IHubContext` and a real client on the real wire.
The payload shape is a public method for the same reason: asserted, not described. This is the shape this repo's other extracted
seams use — `WorldTurnHubInputsForTests` drives the real delegate the host calls for exactly the same reason.

**Not proved** (owned elsewhere):
- `NS` renders the payload: the spec says this task only emits, and the notification-ssot program owns the surface.
- The generic progression route's URL and the fact-ingest route's URL are both `Program.cs` lambdas; this row proves the read
  and the broadcast they carry, not the URLs themselves (the ingest route is exercised by other suites).

# SE4.31 — REST: a save's empires, `empireId` on specimens, `?empire=`

**State: code + tests landed, row NOT ticked** — one acceptance-side artefact is outside this lane's
fence (see the last row). Reads below are the printed output of the commands as run.

| Criterion | Command | Result |
|---|---|---|
| `GET /api/players/{playerId}/empires` → `[{empireId, controller}]` | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Players\|FullyQualifiedName~UniqueActor"` | `Passed! - Failed: 0, Passed: 25, Skipped: 0, Total: 25` |
| `UniqueActorDto.empireId`; AI specimen under `?empire=<ai>`, absent from the human roster; unknown empire 404; Tier B route → `409 empire_scope_not_widened` | same run (`PlayersEmpireEndpointsTests`, 5 facts) | included in the 25 above |
| Empire-route family regression (mapper renamed `MapEmpireLevel` → `MapEmpireRoutes`) | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~EmpireEndpointsTests"` | `Passed! - Failed: 0, Passed: 10, Total: 10` |
| `POST /api/players` creates the save AND its empires, REST-level, real host (`RpgApiFactory : WebApplicationFactory<Program>`) | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --filter "FullyQualifiedName~SaveEmpire"` | `Passed! - Failed: 0, Passed: 2, Total: 2` (12 s) |
| Guards | `pwsh -NoProfile -File scripts/guard-dal.ps1` / `gk-core/scripts/guard-test-substrate.py` | `DAL GUARD OK` / `TEST SUBSTRATE GUARD OK` |
| Data module | `pwsh -NoProfile -Command "& ./scripts/test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj -ExtraFilter 'Category!=DiskSemantics&Category!=Heavy' -Root (Get-Location).Path"` | `TEST-SHARDED OK: 4 shards, 1741 tests, no overlap` |
| Server module | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 832, Total: 832` |
| `verify-change.ps1 -Paths <the 13 paths> -AllowUnscoped` | same | **fails at `test: core`** — `ActionsPurityGuardTests.Action_sources_contain_no_wall_clock_ambient_rng_or_dictionary_enumeration`: `Failed: 1, Passed: 9637, Total: 9638`; the violation is `Cost/ExhaustionEdgeDetector.cs:85 → .Values`, introduced by `467cfa058` (LR/LW1.3, an ancestor of HEAD — pre-existing, not this change; that file is inside active session `cmdc/adg-f5`'s fence) |
| Full E2E module | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | `Failed: 3, Passed: 273, Total: 276` — `ContractFixtureTests.Commander_list_fixture_matches_live_dto` and `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` are pre-existing (fixtures last blessed 2026-09-13; `CommanderEndpoints.cs` changed 2026-09-19/09-21); `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` **is** this change |
| ⛔ The one blocked acceptance artefact | re-bless `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json` with `"empireId": "dave"` (`FUSIONRPG_BLESS_CONTRACT_FIXTURES=1`) | **not runnable from this lane** — `web/**` is outside the allowed paths; needs a one-file fence grant (or the manager's own re-bless) |

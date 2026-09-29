# RS1 — slice 0: `first-session-forward` (lane `sim-slice0`, 2026-09-22)

Scenario `first-session-forward` — `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, executed by
`gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` against the real in-process server
(`RpgApiFactory : WebApplicationFactory<Program>`). No product code, no new route, not wired into `ci.yml`
(C3 (c)).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| runs green locally | `powershell -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths 'gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs' -Session rpg-simulator-slice0"` | pass — `Failed: 0, Passed: 232, Skipped: 0, Total: 232` (2 m 9 s), `TEST SUBSTRATE GUARD OK` | this file |
| the new test alone | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj --no-build --nologo --filter "FullyQualifiedName~RpgScenarioSlice0E2ETests" -l "console;verbosity=detailed"` | pass — `Total tests: 1 / Passed: 1` (4 consecutive runs); trace `first-session-forward: player=2 roster=10 squad=2 expedition=1 battles=1` | this file |
| steps are real routes | the scenario file names every step's route and `Run` refuses a mismatch (`Assert.Equal(declared, step.route)`) | pass — 8 steps, 0 mismatches | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` |
| the squad came from the roster | `Assert.Equal(ctx.SquadIds, foughtWith)` where `foughtWith` is `GET /api/expeditions/{playerId}` → `squadInstanceIds` and `ctx.SquadIds` comes from `GET /api/creatures/{playerId}` | pass | `RpgScenarioSlice0E2ETests.cs` |
| not in CI | `grep -c "RpgScenario" .github/workflows/ci.yml` | `0` | — |
| the boundary is otherwise clean | the same scoped command, re-run | 6 of 8 runs `Failed: 0, Passed: 232, Total: 232`; 2 runs `Failed: 1, Passed: 231, Total: 232` on the PRE-EXISTING `UniqueEquipmentE2ETests.Award_xp_levels_and_refuses_retired` 500 — see `RS-CF2` | `tasks/rpg-simulator-todo.md` |
| that flake is not this lane's | `dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName!~RpgScenarioSlice0E2ETests"` ×4 | `Failed: 1, Passed: 230, Total: 231` once, `231/231` three times — reproduces with this lane's test excluded | `RS-CF2` |

**Read-backs asserted** (all GET, all the routes the web FE calls): `/api/souls/{id}`, `/api/creatures/{id}`,
`/api/expeditions/{id}` (state + persisted squad), `/api/runs?playerId=` (runs exist, `game == webrpg-1`,
ids equal the collect's battles, `result` in the emitter's closed vocabulary),
`/api/rpg/progression/{id}/summary`, `/api/rpg/progression/{id}/ledger` (web-mode rule:
`kind ∈ {player, species}` only, every row attributed to a run this scenario created),
`/api/souls/{id}/ledger` (`seed` and `expedition` rows present).

**Named bypass:** step 6 is `POST /api/test/expedition-due` → `RpgStore.ForceExpeditionDue`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202`), the SIM-only `UPDATE`. Retired by RS3 (owner ruling
B3 → A). No second bypass was invented.

**One green reading needed a retry:** the second scoped run came back `Failed: 1, Passed: 231, Total: 232` on
the pre-existing `UniqueEquipmentE2ETests` 500 (`RS-CF2`), reproduced with this lane's test excluded. The
counts above are the green runs; the red run is `RS-CF2`, not RS1.

**NOT proved:** the real-process host (`FusionRpg.Server.exe`) — that is RS2's slow lane; the browser (C4 (a),
HTTP-only); anything requiring the game or a live injector; that the XP-ledger row set is stable — a webrpg
run credits `kill` on a victory, `defeat` on a defeat and nothing on a stalemate, so the scenario pins the
web-mode rule and the run attribution, never a count; and that the fixture path is verification-owned — it is
not (below).

**Findings routed (rows in the owning todos):**
`RS-CF2` (`tasks/rpg-simulator-todo.md`) — `POST /api/unique/actors/{instanceId}/xp` intermittently answers
**500**, caught only sometimes by `UniqueEquipmentE2ETests.Award_xp_levels_and_refuses_retired`
(`gk-core/tests/FusionRpg.E2E.Tests/UniqueEquipmentE2ETests.cs:126`); the only throwing call on that route is
`ua.AwardXp` (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:120`) →
`RpgStore.AwardUniqueActorXpUnlocked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2029`).
Pre-existing (reproduced with this lane's test excluded). Owner unknown — the action program wrote the
throw path; the manager should route it.

`RS-F1` (`tasks/rpg-simulator-todo.md`) — `/api/souls` maps only reads (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:9`),
so "award souls through the real `/api/souls` path" (idea §5.3) is satisfied by the sanctioned SIM seed route
`/api/test/seed-souls-demo` (`:29`, real `AwardSouls` write), named in the scenario file.
`RS-F2` → `TVB-F23` (`tasks/test-verification-boundary-todo.md`) — `gk-core/tests/fixtures/rpg-scenarios/**` is unmapped
under the enforced root `gk-core/tests/fixtures/**` (`scripts/lib/VerificationBoundaries.ps1:46`), so
`guard-verification-boundaries.py` exits 1 with `unmapped enforced-root file:
gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` and `verify-change.ps1` refuses that path. **CI-gating
(`.github/workflows/ci.yml:347`) — this must land with or immediately after RS1.** The lane's fence excludes
`scripts/**`, so the row could not ride along.

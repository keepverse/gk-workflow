# Tasks: `rpg-simulator` (planned)

Map: [../docs/architecture/rpg-simulator-map.md](../docs/architecture/rpg-simulator-map.md) ·
Plan: [rpg-simulator-plan.md](rpg-simulator-plan.md) · Decisions:
[rpg-simulator-decisions.md](rpg-simulator-decisions.md) (all twenty **owner-cleared 2026-09-22**).
Ideas: [rpg-simulator-idea.md](../docs/architecture/rpg-simulator-idea.md) (lane `sim-idea-a`) ·
[rpg-simulator-shape-idea.md](../docs/architecture/rpg-simulator-shape-idea.md) (lane `sim-idea-b`).

Status: **planned.** The map and plan exist (RS5, this lane). Every row below carries the **module id**
it builds, and every module id is a row of the map's module table — no row may name one that is not.
Order is the plan's wave order. Verification is the path-owned boundary
(`scripts/verify-change.ps1 -Paths … -Session <id>`), never a full unfiltered suite; a new path with no
mapping is a verification-boundary defect to repair, not a reason to run the whole suite.

## Carried findings (not this program's scope — route, do not fix here)

- [x] **RS-CF1 — `AGENTS.md` understated the CI test-project count by 47** · S · *found by lane `sim-idea-a`, 2026-09-22*
  - **Routed and fixed (2026-09-22).** The owning row is **`TVB-F22`** in
    [test-verification-boundary-todo.md](test-verification-boundary-todo.md) (that program owns the CI
    wiring statements). Owner ruling on F2: *update stale* — done in the same commit as the note;
    `AGENTS.md` no longer carries a rot-prone count and points at `ci.yml` as the list instead.
  - The original measurement (`ci.yml` names 60 distinct test projects over 69 `dotnet test`
    invocations; the prose said 13) is preserved in `TVB-F22` and in
    [reports/backlog-reconciliation-20260921.md](reports/backlog-reconciliation-20260921.md)'s
    neighbourhood; it is a **reading**, never a pinned constant.

## Rows, keyed to the map's module ids

- [x] **RS-CF2 — `POST /api/unique/actors/{instanceId}/xp` intermittently answers 500, and the E2E test that catches it does so only sometimes** · S · *found by lane `sim-slice0`, 2026-09-22, while running RS1's scoped verification (the `e2e` boundary covers the whole E2E project, so this lane's run is where it surfaced)* — **FIXED 2026-09-22 (`rscf2`); the owning row it routes is `UAR-F1` below.**
  - **Measured (exonerates this lane):** with lane `sim-slice0`'s new test EXCLUDED
    (`dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -c Release --no-build --nologo
    --filter "FullyQualifiedName!~RpgScenarioSlice0E2ETests"`), 4 runs gave `Failed: 1, Passed: 230, Total: 231`
    once and `231/231` three times. With the new test INCLUDED, 8 runs gave the same single failure 2 times and
    `232/232` 6 times. So it reproduces without this lane's change — pre-existing, not caused here.
  - **Symptom (captured):**
    `System.Net.Http.HttpRequestException : Response status code does not indicate success: 500 (Internal Server Error).`
    at `FusionRpg.E2E.Tests.UniqueEquipmentE2ETests.Award_xp_levels_and_refuses_retired()`,
    `gk-core/tests/FusionRpg.E2E.Tests/UniqueEquipmentE2ETests.cs:126` (`xp.EnsureSuccessStatusCode()`). The test passes
    in isolation; the assembly's only collection is `e2e` with `DisableParallelization = true`, so it is not a
    parallel-collection race.
  - **Cause read (not guessed):** the route can only answer 500 by THROWING —
    `gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:113` maps every non-throwing outcome to 404/400/409 at
    `:121-124`, and the only call that can throw is `ua.AwardXp(...)`, `:120` →
    `UniqueActorService.AwardXp`, `gk-core/src/FusionRpg.Server/UniqueActorService.cs:87-89` →
    `RpgStore.AwardUniqueActorXp` → `AwardUniqueActorXpUnlocked`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2029`. Inside it: `checked { xp = row.Xp + delta; }`
    (`:2038`, `OverflowException`), `RpgXpCurve.XpToNext(RpgActorKinds.Specimen, level)` (`:2041`, whose
    `Tuning` accessor throws `InvalidOperationException` when `ProgressionTuningHub` is unconfigured —
    `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:84`), the `UPDATE`, and `TryRollActionUnlocks`
    (`:2095`, reachable only when `UnlockTuningPolicy.Tuning` is configured — a process-wide static some test
    in the same assembly does configure).
  - **What was NOT established, and is the row's first job:** the exception TYPE and MESSAGE. The harness
    discards the body at `EnsureSuccessStatusCode()` and the host's log is not in the test output. Without it the
    remaining candidates are a static-tuning swap by another test in the same assembly (order-dependent, and the
    ordering that matters is whichever test configures `UnlockTuningPolicy` first) and SQLite contention with the
    server's background ingest worker — both plausible, neither proven. Capture it (`ProblemDetails` on the route,
    or a logged catch) before changing any of the three sites above.
  - **Owner of this row:** unknown. The code on the throw path was written by the **action** program
    (`docs/architecture/action/spec-action-instance-and-grant.md` A21 — `AwardUniqueActorXpUnlocked`,
    `TryRollActionUnlocks`; `spec-unlock-tuning-activation.md` — `UnlockTuningPolicy`), while the route's own area
    belongs to the unique-actor/equip surface (`docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md`,
    `docs/architecture/item/ssot-equip-slots.md`). The manager should route it.
  - **Why it matters beyond one flaky test:** a 500 on a real write route is a real defect, and it is currently
    swallowed as "the E2E suite is a bit flaky" — which is exactly how a red `e2e` boundary gets retried instead
    of read. This lane's verification hit it and had to re-run to get a green reading.
  - **Acceptance:** the test passes 10 consecutive full-project runs with the exception captured and named, or
    the root cause is fixed and the 500 is gone while the route's 404/400/409 mapping is unchanged.
  - **Reproduced again 2026-09-23 (lane `sim-runner`, RS2.2 verification):** 2 full-project runs of
    `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` at a head carrying only new
    `gk-core/tools/RpgSim` code + a new E2E test file gave `Failed: 1, Passed: 268, Skipped: 0, Total: 269` once
    (2 m 11 s) and no failure the second time. The single failure is the same one, so the flake is still
    live and still intermittent; the exception type/message is still NOT captured (the harness discards the
    body at `EnsureSuccessStatusCode()`), which is the row's first job.
  - **Files:** `gk-core/tests/FusionRpg.E2E.Tests/UniqueEquipmentE2ETests.cs:126`,
    `gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:120`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2029`.
  - **Captured 2026-09-22, lane `rscf2` — the exception TYPE and MESSAGE the row's first job asked for.**
    `System.InvalidOperationException: action unlock grant refused: BasicCollision`, thrown by the grant
    delegate `RpgStore.TryRollActionUnlocks` builds
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2134` at the time), called from
    `ActionUnlockGrantService.TryRollOnce`
    (`gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:93`), reached through
    `RpgStore.AwardUniqueActorXp` (`:2019`) → `UniqueActorService.AwardXp`
    (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:89`) → the route's own `ua.AwardXp(...)`
    (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:120`); the Development-env
    `DeveloperExceptionPageMiddleware` serves that stack as the 500 body.
  - **Root cause, with the intermittency mechanism (not an ordering race).** The roll drew from
    `ActionEligibility.Candidates(catalog, speciesKey, familyOf)` minus `state.Held` — *eligibility* answers
    "who may hold this action" (general / family / species), never "may this be granted" — so the pool
    carried `act.attack` (`kind = basic`, `gk-data/packs/fusion/data/seed/actions/authored-basics.json`), which
    `ActionValidator.ValidateGrant` refuses by construction (`ActionRejectionReason.BasicCollision`). Two
    seeded coin flips make it fire *sometimes*: the candidate is drawn by
    `WeightedChoice.Pick(…, Fnv1a64(instanceId), "unlock:{instanceId}:0")` off a **fresh `Guid` instance id
    per specimen**, and `UnlockState.TryAccept` accepts 50% at `earnCount = 0` (shipped `p1Milli = 500`).
    Measured on the real host with the real import path: drawable pool
    `{act.attack, action.general.0003, action.general.0004, action.general.0005}` and **7 of 40** one-level
    awards answering 500 (17.5%; the model's 1/4 pick × 50% accept = 12.5%). With no drawable pool the roll
    is a legal no-op — boot alone leaves `rpg_action` empty in this host (the boot import refuses rows whose
    container atoms are absent), **0 of 20** answered 500.
  - **Fix — production, at the layer that chooses the drawable catalog.** `ActionValidator.ValidateGrantable`
    extracted out of `ValidateGrant` (ONE predicate, two consumers, so the chooser and the writer cannot
    drift), and `RpgStore.TryRollActionUnlocks`'s `catalog:` delegate now hands the roll only rows that
    predicate accepts. Not retried, not skipped, no validator widened; the route's 404/400/409 mapping is
    unchanged.
  - **Regression test + determinism.** New `gk-core/tests/FusionRpg.E2E.Tests/UniqueActorXpUnlockRollTests.cs`: 40
    fresh specimens, one level each, through the real route on the real host, with the real import path
    establishing the precondition (asserted, never assumed) and the written grant rows read back. RED before
    the fix (`specimen b4ff12aa1488445db005f6b56b02e359: xp answered 500` + the BasicCollision stack above),
    GREEN after. The E2E project then read `Total tests: 235 / Passed: 235` on **8 consecutive runs** (wall
    115/126/120/148/143/153/150/437 s). Two contended runs that interrupted the sequence are recorded, with
    their evidence, in [reports/rs-cf2.md](reports/rs-cf2.md).
  - **Where the fix was NOT put, deliberately.** The pure `ActionUnlockGrantService.TryRollOnce` still trusts
    whatever catalog its caller supplies — the production delegate was narrowed, not the service's own
    contract — because moving it would also require `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs`
    (`Row(...)` builds rows with `Grantable` unset, i.e. `false`), a path outside this lane's fence. Recorded
    as `UAR-F1` below, so the remainder is routed rather than absorbed.
  - **Files (2026-09-22):** `gk-core/src/FusionRpg.Core/Actions/ActionValidator.cs`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`,
    `gk-core/tests/FusionRpg.E2E.Tests/UniqueActorXpUnlockRollTests.cs`, `tasks/reports/rs-cf2.md`.

- [x] **UAR-F1 — the unlock-ladder chooser's own contract still trusts its caller's catalog (the Core half of RS-CF2 / ADG-F5), and no unique-actor todo file exists for the surface it belongs to** · S · *routed by lane `rscf2`, 2026-09-22, out of the RS-CF2 fix* — **Id assertion: UAR-F1**
  - **Owning surface:** the unique-actor runtime XP route (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:113`)
    plus the action program's unlock ladder (`docs/architecture/action/spec-action-instance-and-grant.md` §4,
    `docs/architecture/action/spec-unlock-ladder.md`). The same reading is filed as **ADG-F5** in
    [action-distribution-gaps-todo.md](action-distribution-gaps-todo.md) — that file, and
    `gk-core/tests/FusionRpg.Core.Tests/**`, are outside lane `rscf2`'s fence, so this row is the routed copy.
  - **What is already closed:** the production 500 is gone — the store's catalog delegate now feeds the roll
    only `ActionValidator.ValidateGrantable`-accepted rows, so `POST /api/unique/actors/{instanceId}/xp`
    answers 200 for every specimen (RS-CF2 above).
  - **What remains (one task block):** move that predicate into `ActionUnlockGrantService.TryRollOnce` itself,
    so a future host wiring the service with an unfiltered catalog cannot re-open the throw. It needs three
    fixtures in `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs` to set `Grantable = true`
    (`ASuccessfulRollSavesTheUpdatedStateAndGrantsTheChosenAction`, `AMissedRollNeverCallsSaveOrGrant`,
    `CandidatesRespectEligibilityScopeNotJustTheHeldFilter`) — they currently build rows through a `Row(...)`
    helper that leaves `Grantable` at its `false` default.
  - **Routing note (decision, not a guess):** there is no `tasks/unique-actor-runtime-todo.md`;
    `docs/architecture/unique-actor-runtime.md` is a design spec with no plan/todo pair. This row is recorded
    in `tasks/rpg-simulator-todo.md` because it is the only todo file this lane's fence allowed — if the
    unique-actor program has its own todo, move the row there.
  - **Verify:** `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <the two files> -Session <id>` once the
    Core fixture move is scheduled.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`), done by the ADG-F5 lane — re-measured, not assumed.** Both halves of
    "what remains" are in the tree:
    1. **The predicate is in the chooser itself.** `ActionUnlockGrantService.TryRollOnce`
       (`gk-core/src/FusionRpg.Core/Actions/Unlock/ActionUnlockGrantService.cs:107`) now skips any candidate the write
       path would refuse — `if (ActionValidator.GrantRefusal(a) is { } refusal) { skipped.Add(...); continue; }`
       — and its own doc block is headed *"**ADG-F5 — the offered set must be grantable, and the filter lives
       here**"*, with the reasoning for rejecting both alternative homes (not `ActionEligibility.Candidates`,
       whose axis is scope-only; not the store's catalog delegate, because "what may be granted" is
       action-layer law). Landed by **`9ef4988ec`** (*"fix(ADG-F5): the unlock roll never offers an action it
       cannot grant"*) and refined by **`3a3d0d2da`** (a refused option is skipped **with its reason** and
       reported, never thrown).
    2. **The fixtures carry `Grantable = true`.** `ActionUnlockGrantServiceTests.Row(...)` sets it with the
       reason in a comment (*"what the imported corpus rows carry"*), and the file has `BasicRow` /
       `UnGrantableRow` helpers plus four tests that pin the behaviour:
       `TheRollNeverOffersABasicOrNonGrantableRowAndNeverTripsTheWritePathRefusal`,
       `ACatalogOfOnlyUnGrantableRowsIsALegalNoOpAndNeverCallsSaveOrGrant`,
       `ARollWhoseOptionSetHoldsUnGrantableActionsStillReturnsItsGrantableOptionsAndReportsTheSkips` and
       `IsGrantableAgreesWithWhatTheValidatorItselfRefusesForTheSameRow`. Same commit `9ef4988ec`.
    **Measured:** `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter
    "FullyQualifiedName~ActionUnlockGrantServiceTests"` → `Passed: 11, Failed: 0, Total: 11`. **Boundary note:**
    this row's own verify line resolves to the broad core set (`core-fallback` plus
    `core-area-actions-owners`, ~69 projects), which is CI-owned; the focused class is the reading taken here.
    The routing half of the row (no `tasks/unique-actor-runtime-todo.md`) still stands as a note for the manager —
    it is not a deliverable, and nothing in the unique-actor surface is left open by this row.

- [x] **RS-CF3 — the E2E project is not yet deterministic under load: three tests, none of them RS-CF2's, went red in the runs that measured it** · S · *found by lane `rscf2`, 2026-09-22, while proving RS-CF2's 8-run determinism* — **Id assertion: RS-CF3**
  - **Measured (13 full-project runs, `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`,
    all of them with the RS-CF2 fix in the tree).** Eight consecutive runs read `Failed: 0, Passed: 235,
    Total: 235` at 115–153 s wall (one at 437 s). The five red ones fall in two groups:
    (a) **wall-clock budgets under contention** — `CatalogAndStressE2ETests.Mixed_fight_5000_hits_and_500_bullets`
    (`mixed persist ms 5986`), `Fps120_second_9600_events` (`120fps persist ms 8044`),
    `Enqueue_2000_returns_fast_then_persists` (`enqueue ms 222`), each in a run whose wall time was 548 s or
    716 s while `Get-CimInstance Win32_Processor` read `LoadPercentage 100` with 67–80 `dotnet` and 5–6
    `testhost` processes (other lanes' suites) — these are the brief's own "that is contention, re-run" case,
    and each passed in every quiet run.
    (b) **two single-red runs whose message was NOT captured**: `RpgScenarioSlice0E2ETests.First_session_forward_runs_green_and_its_squad_came_from_its_own_roster`
    once at normal speed (`Failed: 1, Passed: 234`, 2 m 21 s; the run used `--verbosity quiet`, so only the
    test name is known), and `FoundationE2ETests.Mid_match_switch_keeps_open_run_player` once inside the
    716 s contended run (`Assert.Equal() Failure: Values differ — Expected: 1, Actual: 0` at
    `FoundationE2ETests.cs:122`, failing in 72 ms).
  - **The first job (the same shape RS-CF2 had):** capture the exception or assertion MESSAGE for (b) —
    `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo -v n` leaves it in the log where `--verbosity quiet` does
    not — then say whether each is a real state defect or the contended machine; neither is proved either way
    here, and neither can be caused by the RS-CF2 fix (the XP route and the unlock roll are the whole diff;
    `RpgScenarioSlice0E2ETests` never calls the XP route, and its one red happened in a 2 m 21 s "/quiet" run).
  - **CLOSED 2026-09-23 (lane `sim-t3-2`): both (b) items are explained and fixed, and (a) is the machine.**
    1. **`FoundationE2ETests.Mid_match_switch_keeps_open_run_player` — a REAL race, now fixed.** Its message
       WAS captured by the measuring lane (`Expected: 1, Actual: 0` at `FoundationE2ETests.cs:122`), and
       line 122 is `Assert.Equal(1, run.GetProperty("plantsPlanted").GetInt32())`. The run's counters are
       applied by the `EventIngest` DRAIN (`RpgStore.cs:3394`'s
       `UPDATE runs SET plants_planted = plants_planted + 1`), not by the route that accepted the plant, so
       the test's two **direct** `/api/runs` reads (`:117`, `:127`) were readings of a race — every other
       test in that file reads through `Snapshot()`, which flushes (`SimEndpoints.cs:147`), which is exactly
       why only this one flaked. Fixed by saying the settle out loud: a `Settle()` helper calling the
       runner's own `SimSettler.WaitAsync(_http)` (a timeout is a FAILURE, never a silent pass) before the
       first direct read. **Measured:** `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter
       "FullyQualifiedName~FoundationE2ETests"` → `Passed: 16, Failed: 0, Total: 16`.
    2. **`RpgScenarioSlice0E2ETests` — the same defect this lane independently measured and removed.** Its
       message was never captured (the run was `--verbosity quiet`), but that test drives the corpus, and the
       corpus's only RNG-dependent PRESENCE assertion was `expect.souls.ledger.expedition` — measured flaking
       **1 run in 2** on the merged tree (`$.items[*].reason does not contain "expedition"`, the
       server-minted event-souls roll writing no row when it lands zero) and replaced with a closed
       vocabulary (`seed | summon | expedition | discovery | victory | defeat`, each reason named to a cause
       the run has) in commit `26b0e62f2`. The failure mode therefore no longer exists. **Residual risk, named:**
       because the message was never captured, this identification is by mechanism and not by log line — a
       *different* cause of that one red cannot be excluded from the record, only from the present tree.
    3. **(a) is not a defect.** The row's own reading calls it "the brief's own 'that is contention, re-run'
       case" — wall-clock budgets on a 100 %-loaded machine with 67–80 `dotnet` processes from other lanes —
       and each passed in every quiet run.
  - **Not proved:** the E2E project is not *proved* deterministic under load; what is proved is that its two
    known single-red causes are gone and that its wall-clock-budget reds track machine load.
  - **Owner:** `rpg-simulator` (RS1 owns `RpgScenarioSlice0E2ETests`; `FoundationE2ETests` and
    `CatalogAndStressE2ETests` are older suite-wide classes). If the manager reads (b) as a different program's,
    route it and say so here.
  - **Acceptance:** each of the three names either passes 8 consecutive full-project runs with its message
    captured and named, or is shown to be a defect and fixed.
  - **Files:** `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs`,
    `gk-core/tests/FusionRpg.E2E.Tests/FoundationE2ETests.cs:122`,
    `gk-core/tests/FusionRpg.E2E.Tests/CatalogAndStressE2ETests.cs:219,252,` (enqueue budget),
    `tasks/reports/rs-cf2.md`.

## Decided by the owner (2026-09-22) -- the idea is cleared; these are the next rows

### Wave 0 — the index (this lane)

- [x] **RS5 — the program's map + plan, module ids, and the CI decision** · S · *approved A3 (a)* · module: *(none — this row is the index)*
  - **Delivered 2026-09-22:** `docs/architecture/rpg-simulator-map.md` (ten module ids, each with its
    one-line purpose and its `spec-*.md` path, the verified current-state table, the decisions this map
    makes, the external asks and the NOT-proved list) and `tasks/rpg-simulator-plan.md` (five waves over
    those ids, the cleared decisions as binding constraints, the gates S0–S6, and the CI decision
    C3 (c): slice 0 is local-only).
  - Acceptance met: every row below carries a module id the map names; the map is the index and adds no
    id the plan invents.
  - Acceptance met: `python scripts/audit-doc-citations.py --scope <each doc> --strict` → 0 HIGH for
    both.
  - Files: `docs/architecture/rpg-simulator-map.md`, `tasks/rpg-simulator-plan.md`,
    `tasks/rpg-simulator-todo.md`, `tasks/sessions/rpg-simulator-map.json`.

- [x] **RS1 -- slice 0: one E2E scenario file, no product code** · S · *approved E1 (a) / A2 (a) / C3 (c)*
  The chain: create a player -> souls -> summon -> roster read -> expedition dispatch/due/collect -> progression
  + ledger + run reads. Acceptance: it runs green locally, its steps are real routes, and the squad it fights
  with is asserted to come from the roster it just built (the fabrication line).
  - **Done 2026-09-22 (lane `sim-slice0`).** Scenario `first-session-forward` lives in
    `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` and is executed by
    `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` against the real in-process server
    (`RpgApiFactory : WebApplicationFactory<Program>`). Every step names its HTTP route in the scenario file
    and the runner refuses a step whose declared route is not the one it calls, so the file cannot drift from
    the runner. Every verdict is a GET read-back through the same route the web FE calls; a POST body is used
    for sequencing only. The fabrication assertion compares the expedition's persisted `squadInstanceIds`
    (read back from `GET /api/expeditions/{playerId}`) against the roster read back from
    `GET /api/creatures/{playerId}`.
  - **Evidence:** `tasks/evidence-fragments/rpg-sim-rs1.md`. Green locally, whole E2E project boundary:
    `Failed: 0, Passed: 232, Skipped: 0, Total: 232` (2 m 9 s) via
    `powershell -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths 'gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs' -Session rpg-simulator-slice0"`
    (plus `TEST SUBSTRATE GUARD OK`).
  - **Not proved:** the real-process host (RS2's slow lane); the browser (C4 (a), HTTP-only); anything needing the
    game or an injector; and the fixture path has no verification boundary yet (RS-F2).
  - **Named bypass:** step 6 uses `POST /api/test/expedition-due` (`RpgStore.ForceExpeditionDue`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202`) — the SIM-only `UPDATE`. It is the only way to make
    an expedition due today and is retired by RS3 (owner ruling B3 -> A). No second bypass was invented.

- [x] **RS-F1 -- `/api/souls` exposes no award route, so "award souls through the real `/api/souls` path" is not reachable through a player-facing route** · XS · *found by lane `sim-slice0`, 2026-09-22, while building RS1*
  - **Measured:** `SoulEndpoints.MapSouls` (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:9`) maps exactly two routes —
    `GET /api/souls/{playerId}` and `GET /api/souls/{playerId}/ledger`. Both are reads. The only award route in
    the repo is the SIM seeding surface `POST /api/test/seed-souls-demo`
    (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29`), which performs the real `RpgStore.AwardSouls` write with
    `SoulEarnPolicy.Reasons.Seed`.
  - **Cause (read, not guessed):** souls are *earned* by gameplay (kills, victory/defeat, expeditions,
    discovery, fusion, upkeep — `SoulEarnPolicy.Reasons`, `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs:49`) and
    *spent* by feature-owned routes; there is deliberately no generic award endpoint
    ("Spends are feature-owned (summoning etc.), never generic", `SoulEndpoints.cs:6`).
  - **Why it matters for the simulator:** `rpg-simulator-idea.md` §5.3 writes the slice-0 step as "award souls
    through the real `/api/souls` path". That step cannot be a player-facing route. RS1 uses
    `/api/test/seed-souls-demo` — the sanctioned seeding surface, which does perform the real award write — and
    says so in the scenario file's `notes` and in the evidence. Earning the souls instead is not available
    either: a real match before a roster exists fields the `Synthetic` squad
    (`gk-core/src/FusionRpg.Server/WebMatchService.cs:570-574`), which is the fabrication RS1 exists to refuse.
  - **Owner of this row:** unknown — it is a statement about the soul economy's route surface, which
    `rpg-simulator` does not own. The manager should route it (the soul-economy program, or `rpg-simulator` if it
    accepts the SIM seed surface as the sanctioned award for a scenario).
  - **Acceptance:** either the simulator's own spec names `/api/test/seed-souls-demo` as the sanctioned award step
    (an erratum on `rpg-simulator-idea.md` §5.3), or a player-facing award route exists and RS1's step uses it.
    Owner ruling D3 stands: an unreachable condition is the finding, not a licence for a new route.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`) against the acceptance's FIRST branch.** The erratum is written where
    the wrong sentence lived: `docs/architecture/rpg-simulator-idea.md` §5.3 now reads *"award souls through the
    sanctioned seeding surface `POST /api/test/seed-souls-demo`"*, with the reason spelled out under it — two
    GETs and no generic award endpoint by design, souls earned by gameplay and spent by feature-owned routes,
    and the seeding surface performing the **real** `RpgStore.AwardSouls` write with reason `seed` (which is why
    the RS4 guard allowlists it by name). The paragraph that already named that route is now consistent with the
    step sentence instead of contradicting it. **Carried forward as RS-F25:** whether the soul economy should
    grow a *player-facing* award route is the soul-economy program's question, and it stays filed rather than
    being answered by this erratum.
  - **Files:** `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:9`, `:29`, `docs/architecture/rpg-simulator-idea.md` §5.3.

- [x] **RS-F2 -- the approved scenario tree `gk-core/tests/fixtures/rpg-scenarios/**` (C1 (a)) has no verification boundary, so the guard that gates CI is RED for RS1's own scenario file** · XS · deps: TVB-F23 · *found by lane `sim-slice0`, 2026-09-22*
  - **Measured:** `python gk-core/scripts/guard-verification-boundaries.py`
    prints `VERIFICATION BOUNDARY GUARD FAILED` / `unmapped enforced-root file:
    gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` (exit 1), and
    `verify-change.ps1 -Paths 'gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json' -PlanOnly` refuses with
    `VERIFICATION BOUNDARY MISSING`. Both are because `gk-core/tests/fixtures/**` is an enforced root
    (`scripts/lib/VerificationBoundaries.ps1:46`) and the registry's `core-test-fixtures` boundary
    (`gk-core/scripts/verification-boundaries.v1.json`) names only `action-traces`, `battle-traces`, `effects` and
    `combat`.
  - **Cause (read, not guessed):** the house pattern is that a new `gk-core/tests/fixtures/**` subtree is added together
    with its owner row — `git show --stat 04b8daa0c` shows `gk-core/scripts/verification-boundaries.v1.json` (+11) in the
    same commit as `gk-core/tests/fixtures/battle-traces/**`. RS1's fence excludes `scripts/**`, so the row could not ride
    along here.
  - **Routed:** **`TVB-F23`** in `tasks/test-verification-boundary-todo.md` (that program owns the registry).
    Until it lands, `guard-verification-boundaries.py` is red at any head carrying RS1 — CI-gating, so this is
    the first thing to land after RS1.
  - **Acceptance:** `guard-verification-boundaries.py` exits 0 at a head carrying
    `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`.
  - **Files:** `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`,
    `gk-core/scripts/verification-boundaries.v1.json`, `scripts/lib/VerificationBoundaries.ps1:46`.
  - **Resolved 2026-09-22 by `TVB-F23`** (`80f388db7 tvb: map gk-core/tests/fixtures/rpg-scenarios/** to e2e`), which
    added the `e2e-scenario-fixtures` owner (`project: e2e`). Verified in lane `sim-runner`'s worktree:
    `python gk-core/scripts/guard-verification-boundaries.py` →
    `VERIFICATION BOUNDARY GUARD OK` (exit 0). Evidence: `tasks/reports/rpg-sim-rs21.md`.

- [x] **RS-F3 -- `gk-core/tools/RpgSim/**` has no verification boundary, so `verify-change.ps1` refuses every path in the new tool** · XS · *found by lane `sim-runner`, 2026-09-23, while verifying RS2.1*
  - **Measured:** `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths 'gk-core/tools/RpgSim/ScenarioValidator.cs' -Session rpg-sim-runner -PlanOnly"`
    throws `VERIFICATION BOUNDARY MISSING: gk-core/tools/RpgSim/ScenarioValidator.cs. Add an owner mapping; do not run
    a broad suite as a fallback.` (`scripts/verify-change.ps1:114`). `tools/**` is NOT an enforced root
    (`scripts/lib/VerificationBoundaries.ps1:46` lists only `gk-core/data/tuning/**`, `gk-core/tests/fixtures/**`,
    `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`), so `guard-verification-boundaries.py` still exits 0 while the planner
    refuses. That asymmetry is why this is a registry row and not a guard fix.
  - **Cause (read, not guessed):** the registry has entries for the tools whose tests exist
    (`gk-forge/tools/AtomImporter/**` + `gk-forge/tests/FusionRpg.AtomImporter.Tests/**` → `atomimporter`, `gk-forge/tools/seedsmith`,
    `gk-core/tools/tuning`, the two `tools/*.Tests` projects) and none for `gk-core/tools/RpgSim/**`. The house pattern is the
    AtomImporter one: the tool's tree is owned by the test project that references it. `gk-core/tools/RpgSim/**` should
    be mapped to `e2e` (the boundary that now owns `gk-core/tests/fixtures/rpg-scenarios/**` too), carrying the
    `test-substrate` guard as its neighbours do.
  - **Owner of this row:** the **test-verification-boundary** program (it owns the registry; the same program
    `RS-F2`'s `TVB-F23` went to). This lane's fence excludes `scripts/**`.
  - **Acceptance:** `verify-change.ps1 -Paths gk-core/tools/RpgSim/ScenarioFormat.cs -PlanOnly` resolves an owner
    instead of throwing.
  - **Resolved 2026-09-23 (lane `sim-t3-1`)** — RS2.5's own verification could not run without it, and
    `scripts/**` is inside that lane's fence. `gk-core/scripts/verification-boundaries.v1.json` gained
    `rpgsim-tool` (`gk-core/tools/RpgSim/**` -> project `e2e`, `level: module`, `guards: ["test-substrate"]`),
    the `atomimporter-fallback` shape. Measured: `verify-change.ps1 -Paths gk-core/tools/RpgSim/ScenarioFormat.cs
    -AllowUnscoped -PlanOnly` -> `gk-core/tools/RpgSim/ScenarioFormat.cs -> rpgsim-tool (module)` +
    `guard: test-substrate` + `test: e2e`; `guard-verification-boundaries.py` -> `VERIFICATION BOUNDARY
    GUARD OK`; the registry re-parsed as JSON in a step that gated the commit. Evidence:
    `tasks/reports/rpg-sim-rs25.md`.
  - **Files:** `gk-core/tools/RpgSim/**`, `gk-core/scripts/verification-boundaries.v1.json`.

- [ ] **RS-F25 -- should the soul economy have a player-facing award route? The simulator's erratum answers only its own half** · XS · *carried out of RS-F1 by lane `sim-t3-2`, 2026-09-23, when RS-F1 closed against its erratum branch*
  - **What is settled (this program's half):** the simulator names `POST /api/test/seed-souls-demo` as its
    sanctioned award step, with the reason in `docs/architecture/rpg-simulator-idea.md` §5.3. The corpus says
    the same in its own `notes`, and the RS4 guard allowlists the route by name. Nothing here needs a new route.
  - **What is NOT settled (the economy's half):** whether a *player* should ever be able to grant souls
    directly. Today `SoulEndpoints.MapSouls` (`gk-core/src/FusionRpg.Server/SoulEndpoints.cs:9`) maps two GETs and
    deliberately no award endpoint ("Spends are feature-owned (summoning etc.), never generic", `:6`); souls
    arrive through gameplay (`SoulEarnPolicy.Reasons`) and the sanctioned SIM seeding surface (`:29`). A
    player-facing award route would be a new economy faucet, so it is a **resource-registry** decision, not a
    simulator one — `docs/architecture/empire-resource-ssot.md` §3 is where a new faucet lands with its sink.
  - **Owner of this row:** the **soul-economy** program (or whoever owns `empire-resource-ssot.md`'s registry),
    routed by the manager; its todo is outside this lane's allowed paths, so the row is filed here.
  - **Acceptance:** either the registry states that souls have no direct-grant route by design (and the SIM
    seeding surface is the only non-gameplay write), or a player-facing route lands with its sink and RS-F1's
    second branch becomes true.
  - **Files:** `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:6-29`, `docs/architecture/empire-resource-ssot.md` §3.

- [ ] **RS-F26 -- `hibernation-clock`'s core is a declared gap, so the clock seam's boundary with it is a constraint re-armed, not a code fact** · XS · *carried out of RS3's ask by lane `sim-t3-2`, 2026-09-23, when the ask was answered from their spec*
  - **Measured:** `docs/architecture/world-continuity/spec-hibernation-clock.md`'s own summary table puts
    **"save counter, clock mark, pending"** under **Real gap**, and `catch_up_cap` / `turn_period_seconds` under
    **Wiring gap — never read**. The code agrees: `grep -rn "GetPendingTurns\|clock_mark\|end_turns" src/ --include=*.cs`
    returns **nothing**, and `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:27-28` declares those two columns with
    no reader.
  - **What this program needs when it lands** (stated in `docs/architecture/rpg-simulator-spec-clock-seam.md`
    §4, so it is not lost with this row): **pending turns stay a subtraction of two stored counters** — the
    clock is never an input to it — and any *duration* the module pro-rates (idle window, yield accrual,
    freshness) goes through `ServerClock`, which `gk-core/scripts/guard-clock-seam.py` already enforces by failing CI
    on a new ambient read.
  - **Owner of this row:** the **world-continuity** program (module `hibernation-clock`, map row 2); its todo is
    outside this lane's allowed paths, so the row is filed here for the manager to route.
  - **Acceptance:** when the save counter / clock mark / pending land, `Pending` is pure and clock-free, and
    every duration read in the module goes through the seam (the guard is the check).
  - **Files:** `docs/architecture/world-continuity/spec-hibernation-clock.md`,
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:27-28`,
    `docs/architecture/rpg-simulator-spec-clock-seam.md` §4.

- [ ] **RS-F8 -- the Guard boundary test's 2-minute timeout is shorter than the guard's own contended runtime, so the Guard suite flakes red** · XS · *found by lane `sim-t3-1`, 2026-09-23, while running RS2.5's boundary verification*
  - **Measured:** inside the full Guard run,
    `FusionRpg.Guard.Tests.VerificationBoundaryWorkflowTests.P6_the_real_registry_resolves_seedsmith_and_tuning`
    failed with `verification-boundary script timed out` (`ExternalProcess.Run`, 2 m) — but the same test
    passes in isolation in **1 m 30 s**, and `gk-core/scripts/guard-verification-boundaries.py` standalone is
    **27 s** (`Measure-Command`). The failure is the suite's own contention, not the registry: the test
    re-runs the full repo-wide coverage walk (`RunBoundaryGuard(RepoRoot())`, `:1118`).
  - **Cause (read, not guessed):** the test's timeout is a fixed 2-minute budget for a whole-repo walk whose
    measured cost on this machine is 27 s idle / 90 s under a loaded suite — the same class of contention
    `scripts/verify-change.ps1:26-30` already documents (`415s -> under 10s` for a 2-path call).
  - **Owner of this row:** the **test-verification-boundary** program (it owns `scripts/verify-change.ps1`,
    the registry and `FusionRpg.Guard.Tests`). This lane cannot open a row in that program's todo —
    `tasks/test-verification-boundary-todo.md` is outside its allowed paths — so the manager should route it.
  - **Acceptance:** the Guard boundary test's budget matches its measured cost (a raised timeout, or the
    coverage walk reused rather than re-run per test), and the Guard suite is green under a loaded machine.
  - **PRE-READ FOR THE OWNER 2026-09-23 (lane `sim-t3-2`), so the fix is a flag rather than a re-architecture.**
    The test's own subject is registry **RESOLUTION** (`P6_the_real_registry_resolves_seedsmith_and_tuning`),
    and the repo-wide coverage walk it re-runs is a *different* invariant. `RunBoundaryGuard`
    (`VerificationBoundaryWorkflowTests.cs:41-42`) calls the guard with `-Root` only — no `-SkipCoverageWalk` —
    and the budget is that helper's `120_000` ms (`:38`). The guard's own comment
    (`gk-core/scripts/guard-verification-boundaries.py:8-18`) documents that `verify-change.ps1` passes
    `-SkipCoverageWalk` on its internal pre-check for exactly this cost reason (*"measured: this walk, not
    process startup, is what made a 2-path -PlanOnly call take 415s under 22 concurrent dotnet.exe hosts"*).
    **Passing that flag would not drop the completeness invariant:** it is asserted by CI's own unfiltered
    guard step (`guard-verification-boundaries` is `ciEntry: own-step`), and by the planted-tree test in the
    same file that asserts *"guard accepted an unmapped test source file"* (`:340-341`). So the cheapest
    correct fix is the flag (or a raised budget), and this lane cannot apply either: the test file is in the
    protected `gk-core/tests/FusionRpg.Guard.Tests/**` tree.
  - **Files:** `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:1118`,
    `gk-core/tests/FusionRpg.Guard.Tests/TestSupport/ExternalProcess.cs:42`.

- [x] **RS-F9 -- 164 of RS3's 213 clock sites, and the `ForceExpeditionDue` retirement itself, are outside this lane's fence** · S · *found by lane `sim-t3-1`, 2026-09-23, while writing the clock-seam spec (RS3)*
  - **Measured (binary-safe scan of `src/**/*.cs`, 2026-09-23):** 213 `DateTime(Offset).UtcNow`
    occurrences — `FusionRpg.Data` 142, `FusionRpg.Server` 41, `FusionRpg.Injector` 19, `FusionRpg.Core`
    8, `FusionRpg.Launcher` 2 (+1 `DateTime.Now`), `FusionRpg.CheatCore` 1. This lane may write
    `gk-core/src/FusionRpg.Core/**` and `gk-core/src/FusionRpg.Server/**` only, so it can land **49** of them
    (increments 1 and 2 of the spec's §6) and no more.
  - **The retirement is in the same fence:** `ForceExpeditionDue`'s `UPDATE` lives at
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215` — Data, not Server. Owner ruling B3 (a)
    cannot be executed by this lane, and the scenario corpus's `test.expedition-due` step cannot be
    re-pointed until it is.
  - **Owner of this row:** the manager (it assigns fences). Two options, both its call: widen this lane's
    paths to `gk-core/src/FusionRpg.Data/**` + the three small modules, or split RS3 into a Data lane, an
    Injector/Launcher/CheatCore lane and this Core/Server lane.
  - **Acceptance:** either a fence that covers `gk-core/src/FusionRpg.Data/**`, `gk-fusion/src/FusionRpg.Injector/**`,
    `gk-fusion/src/FusionRpg.Launcher/**` and `gk-core/src/FusionRpg.CheatCore/**` exists and RS3's remaining increments
    land, or RS3 is split and each new lane's row names its own module.
  - **RESOLVED 2026-09-23 (lane `sim-t3-2`) against the acceptance's FIRST branch: the fence exists and every
    increment landed.** `sim-t3-2` was granted `gk-core/src/FusionRpg.Data/**`, `gk-fusion/src/FusionRpg.Injector/**`,
    `gk-fusion/src/FusionRpg.Launcher/**` and `gk-core/src/FusionRpg.CheatCore/**` alongside Core and Server, and RS3's
    increments 1-4 plus 5a/5b all landed under it: Data 140 real sites (48 files), Injector 11 of 17 code
    reads, Launcher's single site excluded with a reason (RS-F14), CheatCore's read retired by taking its
    stamp from `RpgStore` (no new dependency), and `ForceExpeditionDue`'s `UPDATE` **deleted** with the
    corpus re-pointed at `clock.set`. The guard's own reading on the finished tree is the proof the fence
    was sufficient: `1502 source files, 21 ambient reads — 2 inside the clock type, 19 allowlisted — 0
    simulation-tree ServerClock references`.
  - **Files:** `gk-core/src/FusionRpg.Data/**`, `gk-fusion/src/FusionRpg.Injector/**`, `gk-fusion/src/FusionRpg.Launcher/**`,
    - **Manager ruling (2026-09-23) -- split by module, never by seam.** RS3 stays ONE mechanism: every
      module calls the same seam. A new lane takes `gk-core/src/FusionRpg.Data/**` (142 sites, including
      `ForceExpeditionDue`'s retirement, owner ruling B3(a)), `gk-fusion/src/FusionRpg.Injector/**` (19),
      `gk-fusion/src/FusionRpg.Launcher/**` (2) and `gk-core/src/FusionRpg.CheatCore/**` (1). Every one of those targets
      `net8.0` or is a Unity host, so `TimeProvider` exists there and **RS-F13's erratum does not block
      them** -- which is what makes this the un-blocked half of RS3. `FusionRpg.Core`'s 8 sites stay with
      the Core/Server lane and wait on the owner's shape ruling (shape B is the AGENTS.md default: a
      net6.0-safe seam over a configured `Func<DateTimeOffset>`, with `TimeProvider` as the net8.0 input).
      "Widen this one lane" was rejected: 213 sites inside a single fence is not a boundary, it is the
      absence of one, and the three small modules would then queue behind Data's 142 for no reason.
    - **Manager ERRATUM (2026-09-23, superseding the ruling directly above).** That ruling was written from
      this row's own text -- "this lane may write `gk-core/src/FusionRpg.Core/**` and `gk-core/src/FusionRpg.Server/**` only"
      -- and it is **stale**. The record of what actually ran is the spec's §6 table, and it shows
      increment 2 (`FusionRpg.Server`, 33 real sites), increment 3 (`FusionRpg.Data`, 140 real sites across
      48 files) and increment 4 (`Injector`/`Launcher`/`CheatCore`) **done by `sim-t3-2`**, which held a
      grant of the whole migration surface (`spec-clock-seam.md` §0.1). **No new lane is spawned**, and
      spawning one would have duplicated work already merged. What remains of RS3 is **increment 5 alone** --
      retiring `ForceExpeditionDue`'s `UPDATE` -- and that is blocked by §6a: a declared offset cannot make an
      expedition due (dispatch and collect read the same seam, and the shortest tier is 30 minutes), so it
      needs a mid-run clock input the HTTP-only runner cannot reach today. Filed as **RS-F16**, which names
      two candidates, and **the choice between them is the owner's** -- a product decision, not a lane's.
      RS-F9 is therefore closed by disposition too: the 164 sites it counted have all landed.
    `gk-core/src/FusionRpg.CheatCore/**`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`.

- [x] **RS-F10 -- the clock guard (`gk-core/scripts/guard-clock-seam.py`) cannot be created from a delivery lane: the pipeline guard refuses a new `scripts/guard-*.ps1`** · XS · *found by lane `sim-t3-1`, 2026-09-23*
  - **Measured:** an attempt to write `scripts/guard-sim-fabrication.ps1` (RS4's deliverable) was refused
    with *"protected pipeline file (guards, verify, ledger script, hooks, CI)"*. The same block applies to
    the clock guard RS3's acceptance asks for.
  - **Why it is a row and not a retry:** the protocol forbids routing around the guard (no alternate path
    or file name), and the enforcement registry cannot carry a row for a script that does not exist
    (`EnforcementRegistryGuardTests.R1`). So both RS3's guard acceptance and all of RS4 wait on a fence
    that may write under `scripts/guard-*.ps1`.
  - **Owner of this row:** the manager (fence/orchestrator). **Acceptance:** the guard scripts are writable
    by the lane that owns the rule, or the guard is authored by whoever holds the pipeline fence.
  - **Files:** `scripts/guard-sim-fabrication.ps1`, `gk-core/scripts/guard-clock-seam.py`,
    `gk-core/scripts/enforcement-registry.v1.json`.
  - **RESOLVED 2026-09-23 (lane `sim-t3-2`), which carries the `--allow-protected` grant for
    `scripts/guard-*.ps1`.** `gk-core/scripts/guard-clock-seam.py` landed with two rules: no ambient clock read in
    `src/**` outside the one clock type and the 19 allowlisted exclusions (a stale entry is itself a
    violation), and no `ServerClock` reference under `gk-core/src/FusionRpg.Core/{World,Battle,Effects}` (RS-F12's
    hole, closed here). Its own registry row (`clock-seam`, `ci`/`gating`), invariant row (`pr-clock-seam`)
    and `clock-seam-guard` boundary rode with it. **Reading on the finished tree: 1478 source files, 20
    ambient reads — 2 inside `ServerClock.cs`, 19 allowlisted; 0 simulation-tree `ServerClock` references.**
    Bite proof: a planted fixture dir (`-SrcDir`) returns exit 1 naming both a planted `DateTimeOffset.UtcNow`
    and a planted `ServerClock` under `FusionRpg.Core/Effects/`. **Still owed:** a C# bite test in
    `gk-core/tests/FusionRpg.Guard.Tests/**`, which refused the write (the same block as RS-F12's remainder).

- [x] **RS-F16 -- retiring `ForceExpeditionDue` needs a mid-run clock input that does not exist, so an expedition cannot be made due inside one run** · S · *found (measured) by lane `sim-t3-2`, 2026-09-23, while implementing RS3 increment 5*
  - **Measured:** `DispatchExpedition` writes `due = ServerClock.UtcNow + tier.DurationMinutes`
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:82-84`) and `ExpeditionService.CollectAsync` refuses
    while `now < due` (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:90-92`). Both read the SAME seam, so a
    single static offset moves both sides together and the gap is always the tier's duration — the shortest
    tier is 30 minutes (`gk-core/data/tuning/expeditions.v1.json`). The spec's §6 premise ("a declared clock offset
    makes it due without writing anything") is therefore wrong; recorded as §6a.
  - **Why the honest replacement is unreachable:** `ScenarioRunner` reaches its host over HTTP only (one
    `HttpClient`, both hosts), and a route that sets the clock is deliberately not specified
    (`spec-clock-seam.md` §2, owner ruling D3 (b)); the server's offset is read once at the composition root
    from the environment.
  - **Blast radius if the rewind is simply deleted:** three test files depend on it and have no replacement —
    `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs:141` (could use the store's own `utcNow` parameter),
    `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs:70,125` and `gk-core/tests/FusionRpg.E2E.Tests/ContractE2ETests.cs:173`
    (HTTP; need the clock to move *during* the test). Their only alternative today is a process-global
    `ServerClock.Configure` mutation from a test — the same hazard class as the documented
    `ProgressionTuningHub` flake (`tasks/empire-progression-todo.md:1272`, finding F2) — which this lane will
    not multiply without a ruling. The corpus's `test.expedition.due` step and its RS4 guard allowlist entry
    therefore stay, and stay honest (the note in the scenario says what the bypass is).
  - **Two candidate fixes, for the owner:** (1) **boot-time clock plumbing** — the in-process host factory and
    the process host accept the scenario's declared offset, and the store test uses its `utcNow` parameter:
    small, makes `clock.mode: offset` honest for both hosts, but does NOT reach a due expedition; (2) **a
    mid-run clock input** — the runner reboots the process host on the same data dir with a new offset and
    the in-process host applies it in place, declared by a scenario step: larger, and the only shape that
    reaches the corpus's collect half honestly.
  - **Owner of this row:** the owner (a clock-setting input is a product/architecture decision), routed by
    the manager.
  - **Acceptance:** either a mid-run clock input exists and `ForceExpeditionDue`'s `UPDATE` plus the
    `/api/test/expedition-due` route are deleted with the corpus re-pointed, or the owner rules that the
    rewind stays as a documented SIM bypass and RS3's retirement acceptance is amended.
  - **MET 2026-09-23 (lane `sim-t3-2`) against the acceptance's FIRST branch, in the owner's ruled order.**
    5a made a declared `clock.mode: offset` honest for both hosts at boot; 5b added the mid-run input
    (`IClockControl` + the `clock.set` step, with the in-process host applying it in place and
    `ProcessHostClockControl` rebooting the real process on the same data dir and port). Then the
    retirement: `RpgStore.ForceExpeditionDue` **deleted**, `/api/test/expedition-due` **gone**,
    `test.expedition.due` out of the closed vocabulary, the corpus's step a `clock.set`, and the three
    dependent tests moved to `RpgApiFactory.WithClockAheadAsync`. **Measured:** RpgSim `48/48` — the corpus
    runs its `clock.set` step on the in-process host AND on a real process that reboots mid-run; the RS4
    guard reads `test.* steps=1` and `/api/test handlers=12 (11 take RpgStore, 11 allowlisted)`.
  - **Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`,
    `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:347-355`, `gk-core/tools/RpgSim/ScenarioVocabulary.cs:81`,
    `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`, `gk-core/tools/RpgSim/ScenarioRunner.cs`,
    `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs`, `gk-core/tests/FusionRpg.E2E.Tests/ContractE2ETests.cs`,
    `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs`.
    - **OWNER RULING (2026-09-23): candidate (1) first, then candidate (2) -- plumb the offset at boot, then
      add the mid-run clock input.** Increment 5 therefore lands in two steps: **5a** the in-process host
      factory and the process host accept the scenario's declared offset, so `clock.mode: offset` is honest
      for both hosts (the store test moves to its own `utcNow` parameter); then **5b** the runner stops and
      reboots the process host on the same data dir with a new offset while the in-process host applies it in
      place -- which is what makes the corpus's `test.expedition-due` step honest and retires
      `ForceExpeditionDue`'s `UPDATE`. Each step is its own commit with its own verification. Until 5b lands
      the corpus step and its RS4 allowlist entry **stay**, and **say what the bypass is**: an honest note is
      the requirement, never a silent removal.
    - **5a LANDED 2026-09-23 (lane `sim-t3-2`).** A scenario may declare `clock.mode: offset` with
      `offsetSeconds`, and BOTH approved hosts apply it at boot through the one seam: `RpgApiFactory`'s
      offset constructor sets `FUSIONRPG_CLOCK_OFFSET` and configures the seam (its `SeedSpeciesRoster`
      builds a store before `Program.cs` runs) and gives the process clock back on dispose;
      `ProcessHostOptions.ClockOffsetSeconds` passes the same variable to the child; the CLI's
      `--host process` forwards the declaration and `--base-url` **refuses** an offset scenario by name. The
      store test moved to its own `utcNow` input (`A_dispatch_stamped_in_the_past_is_due_without_rewriting_the_row`)
      -- one of the three bypass dependencies gone. **Measured** (`RpgSimClockOffsetTests`): the corpus with
      its clock block rewritten to `offset 3600s` runs on both hosts `ok=True`, verdict
      `clock='offset 3600s -- …'`, digest unchanged (`daa9df408054f32e…`), and the offset is visible on a
      real row (`dispatchedUtc`/`dueUtc` 55-65 minutes ahead of the machine clock). **5b (the mid-run input)
      is still owed**, so `ForceExpeditionDue`'s `UPDATE` and the corpus's `test.expedition-due` step stay.
    - **5b LANDED 2026-09-23 (lane `sim-t3-2`) -- the row's acceptance is met.** `IClockControl` (the host owns
      the clock; the runner refuses the run by name when there is no control) + a sixth step shape
      `clock.set` (absolute offset, no route) + two implementations: `RpgApiFactory.ClockControl` applies it to
      the seam in place, and `ProcessHostClockControl` **owns the host's lifecycle** -- it starts the first
      process itself and a movement stops it and reboots it on the SAME data dir and port with a new
      `FUSIONRPG_CLOCK_OFFSET`. `ScenarioRunner` resets the host to the declared boot offset at the start of
      every run, so `--double-run` cannot inherit a movement. **Retired:** `RpgStore.ForceExpeditionDue`
      deleted, `/api/test/expedition-due` gone, `test.expedition.due` out of the closed vocabulary, the
      corpus's step replaced by `clock.set`, and the three dependent tests (ExpeditionE2ETests ×2,
      ContractE2ETests) moved to `RpgApiFactory.WithClockAheadAsync`. **Measured:** RpgSim `48/48` (5 m 32 s)
      -- the corpus runs its `clock.set` step on the in-process host AND on a real process that reboots
      mid-run; the guard reads `test.* steps=1` and `/api/test handlers=12 (11 take RpgStore, 11 allowlisted)`.
      **One allowlist entry deliberately stays and says why:** `test.expedition.due` in the RS4 guard's op
      allowlist, because `gk-core/tests/FusionRpg.Guard.Tests/SimFabricationGuardTests.cs:76` (a pipeline-protected
      path) plants a scenario using that op to exercise the notes rule, and the guard only reaches that rule
      when the op is allowlisted.

- [ ] **RS-F11 -- the `/health` clock declaration is fenced: it needs `HealthDto` and `RpgStore.ToHealth`, both outside this lane's paths** · XS · *found by lane `sim-t3-1`, 2026-09-23, while scoping the clock seam's Server increment*
  - **Measured:** `/health` is `ingest.Decorate(store.ToHealth(SimFlags.Enabled))`
    (`gk-core/src/FusionRpg.Server/Program.cs:1293`); `ToHealth` returns `HealthDto`
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1221`) and `HealthDto` lives in
    `gk-core/src/FusionRpg.Contracts/Dtos.cs:43`. Adding a `clock` field therefore needs Data **and** Contracts —
    neither is in this lane's paths.
  - **Why it matters:** the spec's product-surface obligation is that the declaration is *reported*. The
    scenario verdict already prints it (`gk-core/tools/RpgSim/readback-verdict.md` §1), so the row's acceptance is
    satisfiable today; the `/health` field is the server-side half and is what makes the seam visible to a
    non-sim caller.
  - **Owner of this row:** the manager (fence) — or whoever owns `FusionRpg.Contracts`/`FusionRpg.Data`.
  - **Acceptance:** `/health` carries the clock declaration, or the spec records that the declaration is
    verdict-only and says why.
  - **Update 2026-09-23 (lane `sim-t3-2`):** the Data half of the fence is gone (this lane owns
    `gk-core/src/FusionRpg.Data/**`), so `RpgStore.ToHealth` is reachable; `HealthDto` in `FusionRpg.Contracts` is
    **not** (the lane's fence lists no Contracts path). The row still needs whoever owns Contracts, or an
    erratum that makes the declaration verdict-only. The verdict half is already satisfied.
  - **Files:** `gk-core/src/FusionRpg.Contracts/Dtos.cs:43`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1221`,
    `gk-core/src/FusionRpg.Server/Program.cs:1293`.

- [~] **RS-F12 -- the world-simulation purity scan bans clock symbols by NAME, so the new seam's name must be added or `Core/Effects` can read wall time past the gate** · XS · *found by lane `sim-t3-1`, 2026-09-23, while scoping the clock seam*
  - **Measured:** `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-49` bans `DateTime.Now`,
    `DateTime.UtcNow`, `DateTimeOffset.Now`, `DateTimeOffset.UtcNow`, `Environment.TickCount`, `Stopwatch`,
    `System.Random`, `new Random(` over `Core/World + Core/Battle + Core/Effects`, comment-stripped, with
    one named exemption (`SystemEffectClock`, `:59`).
  - **Cause (read, not guessed):** the scan matches literal symbol text, so a wall-clock read *through* a
    new seam type is invisible to it — the gate that exists to catch exactly that would not.
  - **Owner of this row:** the **test-verification-boundary**/**guard** program (it owns
    `gk-core/tests/FusionRpg.Guard.Tests/**`), or whichever lane holds that fence.
  - **Acceptance:** `ServerClock` is in `BannedSymbols` (or the scan resolves the seam name and the
    exemption list stays exactly one), and the seam type lands in the same change or later.
  - **Files:** `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-59`.
  - **Half-resolved 2026-09-23 (lane `sim-t3-2`), by substitute, with the remainder still owed.** The
    literal `BannedSymbols` edit was **refused**: `gk-core/tests/FusionRpg.Guard.Tests/**` is a
    pipeline-protected path, so the write was denied (blocker note recorded). The SAME rule now ships as
    **rule 2 of `gk-core/scripts/guard-clock-seam.py`** (a CI-gating guard, a path this lane's grant covers):
    **no `ServerClock` reference may appear under `gk-core/src/FusionRpg.Core/{World,Battle,Effects}`** — the hole
    this row describes, closed from the guard side. **Still owed:** the `BannedSymbols` line itself, for
    the `guard`-program owner (its fence), so the C# scan and the ps1 guard do not diverge later.
  - **Acceptance (amended by the substitute):** the seam name is banned in `Core/World|Battle|Effects` by
    at least one CI-gating check, and `BannedSymbols` gains it when a lane with the guard-test fence runs.

- [x] **RS-F13 -- owner ruling needed: `System.TimeProvider` is .NET 8, and `FusionRpg.Core` is `net6.0`, so B1 (a)'s mechanism cannot be the seam's stored type in Core** · S · *found (measured) by lane `sim-t3-1`, 2026-09-23, while scoping the clock seam's first increment*
  - **Measured:** `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3` and
    `gk-core/src/FusionRpg.Contracts/FusionRpg.Contracts.csproj:3` are `net6.0`; `FusionRpg.Data` and
    `FusionRpg.Server` are `net8.0`. `System.TimeProvider` is .NET 8+. Core stays `net6.0` because the
    Injector is a Unity/BepInEx `net6.0` host that references it.
  - **The ruling asked:** which shape executes B1 (a)? **A** multi-target Core (`net6.0;net8.0`) with the
    `TimeProvider` behind `#if NET8_0_OR_GREATER` and a `Func<DateTimeOffset>` fallback (closest to B1's
    wording; two compiled shapes that can drift), or **B** one `net6.0`-safe seam — `ServerClock.UtcNow`
    over a configured `Func<DateTimeOffset>`, with `TimeProvider` accepted as an *input* on `net8.0` (one
    shape; B1's wording changes). Both are specified in
    `docs/architecture/rpg-simulator-spec-clock-seam.md` §0.
  - **Owner of this row:** the **owner** (it is B1's wording), routed by the manager.
  - **Acceptance:** the erratum is ruled and the spec's §0 table records the ruling; RS3's increments 1
    and 2 then start.
  - **Ruled 2026-09-23 (lane `sim-t3-2`, under the lane's own instruction):** **shape B.** The lane was
    granted the migration surface and told to implement the conservative shape unless the owner ruled A
    first; no A ruling arrived. Recorded in `docs/architecture/rpg-simulator-spec-clock-seam.md` **§0.1**
    (the stored type is one `Func<DateTimeOffset>`; a `TimeProvider` is a net8.0 *input*; there is no
    `ServerClock.Current`; two typed accessors over one read). B1 (a)'s **intent** — one injectable read —
    is executed in full; only its mechanism differs, and the difference is stated rather than smoothed.
  - **Files:** `docs/architecture/rpg-simulator-spec-clock-seam.md` §0/§0.1/§3,
    `gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`, `tasks/rpg-simulator-decisions.md` (B1).

- [ ] **RS-F14 -- the Launcher's one ambient clock read cannot reach the seam: `FusionRpg.Launcher` references no FusionRpg project at all** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, while migrating the Launcher for RS3 increment 4*
  - **Measured:** `gk-fusion/src/FusionRpg.Launcher/FusionRpg.Launcher.csproj` carries **no `ProjectReference`**
    (WPF-UI + WebView2 packages only), so `FusionRpg.Core.Time.ServerClock` is not reachable from it;
    `gk-core/scripts/guard-repo-boundary.py`'s pinned `$AllowedGraph` does not name the Launcher either, so a
    new edge would be an unrecorded architecture change. The site is
    `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml.cs:399` — `var stamp = DateTime.Now.ToString("HH:mm:ss")`,
    a **local UI log stamp**, not a duration, deadline or persisted row.
  - **What was done instead:** the site is an exclusion with this reason in
    `docs/architecture/rpg-simulator-spec-clock-seam.md` §7 and in `gk-core/scripts/guard-clock-seam.py`'s
    allowlist. CheatCore's sibling site needed no exclusion: `FromEntries` now takes its `updatedAt`
    from the caller (`RpgStore`), so CheatCore has zero ambient reads and keeps its Contracts-only graph.
  - **Owner of this row:** the owner (a Launcher → Core dependency edge is an architecture decision),
    routed by the manager.
  - **Acceptance:** either the Launcher gains the seam (a recorded dependency edge, then the stamp
    routes through `ServerClock.UtcNow.ToLocalTime()`), or the exclusion is accepted as permanent and
    §7 keeps the reason.
  - **Files:** `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml.cs:399`, `gk-fusion/src/FusionRpg.Launcher/FusionRpg.Launcher.csproj`,
    `gk-core/scripts/guard-repo-boundary.py:45-52`, `docs/architecture/rpg-simulator-spec-clock-seam.md` §7.

- [x] **RS-F17 -- `population-pin` is RED on this lane's base commit, from another program's test, so `run-guards.ps1 -Tier ci` fails for a reason this lane did not cause** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, while running the lane's `-Tier ci` guard sweep*
  - **Measured:** `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-population-pin.ps1` exits **1**
    with one finding: `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220` —
    `Assert.Equal(500, grantedIds.Count) has no pin: marker`. `git merge-base --is-ancestor 3a3d0d2da 5252537b6`
    is true, i.e. the offending commit (`3a3d0d2da fix(ADG-F5): a refused option is skipped with a reason and
    reported, never thrown`) is an ancestor of this lane's base, so the red is **pre-existing**, not
    introduced here.
  - **Cause (read, not guessed):** the guard requires a `pin:` marker on a test that asserts a
    population COUNT (the `validation-ssot.md` contract — a count is a reading, not a constant, unless the
    vocabulary is closed and the pin says why). ADG-F5's new assertion has none.
  - **Owner of this row:** the **action** program (ADG-F5 / `tasks/action-todo.md` owns that test file);
    `tasks/action-todo.md` is outside this lane's allowed paths, so the row is filed here for the manager to
    route. This lane did not touch the file and did not widen the guard.
  - **Acceptance:** the assertion carries a `pin:` marker with its reason (or the count is replaced by an
    envelope assertion), and `guard-population-pin.ps1` exits 0 on the integration head.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`), fixed by its owner.** The action program did the acceptance's
    second half — `c0637f93a fix(population-pin): the ADG-F5 sweep asserts its own bound, not a second copy of
    500` — so the `Assert.Equal(500, grantedIds.Count)` this row named no longer exists. **Measured on the
    merged head:** `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-population-pin.ps1` → exit 0,
    `P1 (0 finding(s))`, and the full tier below reads `population-pin ci gating 0`. This lane did not touch
    the file or widen the guard.
  - **Files:** `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220`.

- [x] **RS-F18 -- `doc-citations` is RED on the tree after merging `features/mega-merge`, from a LOAM document, so the guard sweep fails for a reason this lane did not cause** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, on the post-merge `run-guards.ps1 -Tier ci` sweep*
  - **Measured:** `run-guards.ps1 -Tier ci` on the merged branch → `doc-citations ci gating 1`, with two HIGH D3
    findings: `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` cites `fill.py:293-302`
    and `fill.py:532-540` as **bare basenames**, and two tracked files now share that name. The merge added
    `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/fill.py`; the other is seedsmith's own gloss fill.
    `D1 file does not exist` is 720 with **0 HIGH**, so nothing in this lane's documents is flagged.
  - **Cause (read, not guessed):** the citation audit cannot check a line number when a basename is
    ambiguous, so a bare `fill.py:NNN` became a HIGH the moment the second file landed. The fix is to cite a
    path, not a basename.
  - **Owner of this row:** the **loam** program (owns that document) / the **seedsmith narrative** program
    (added the second `fill.py`). Neither todo is in this lane's allowed paths, so the row is filed here for
    the manager to route.
  - **Acceptance:** the two citations name a path, and `guard-doc-citations.ps1 -Strict` reports 0 HIGH.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`), fixed by its owner.** `7464bf590 docs(citations): qualify two bare
    `fill.py` basenames -- the guard found 2 files with that name and the same line already qualified its first
    citation`. **Measured on the merged head:** `pwsh -NoProfile -ExecutionPolicy Bypass -File
    scripts/guard-doc-citations.ps1 -Strict` → exit **0** with no HIGH at all (the audit's summary reads
    `D1 file does not exist 714 (0 HIGH)`, `D3 ambiguous basename 58 (2 HIGH)` → now 0), and the full tier
    below reads `doc-citations ci gating 0`.
  - **Files:** `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76`.

- [x] **RS-F19 -- the `narrative` guard flakes red under the `-Tier ci` sweep and is green standalone (same class as RS-F8)** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, on the post-merge `run-guards.ps1 -Tier ci` sweep*
  - **Measured:** in the sweep, `narrative ci gating 1 22.40` — `gk-core/tests/FusionRpg.Guard.Tests` reports
    `Guard=narrative selected 5 test(s), 5 failed`. Run standalone, `python gk-core/scripts/guard-narrative.py` exits **0**. So the failure is contention, not the rule.
  - **Owner of this row:** the **narrative** program (owns `guard-narrative.py`), or whoever owns the
    Guard-suite timeout (`RS-F8` is the same class, filed by lane `sim-t3-1`).
  - **Acceptance:** the guard's own timeout survives a full `-Tier ci` sweep.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`): the flake did not reproduce, and the acceptance is the sweep.**
    **Measured on the merged head:** `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1
    -Tier ci` → `narrative ci gating 0 17.20` inside a tier that reads **25 guards, 0 red**. The row's
    acceptance is exactly "the guard's own timeout survives a full sweep", so one green sweep satisfies it —
    with the honest limit that a contention flake is not *proved* gone by one run; what is proved is that the
    sweep that failed before now passes, and the standalone run was green both times.
  - **Files:** `gk-core/scripts/guard-narrative.py`, `gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs`.

- [ ] **RS-F20 -- the merge left `gk-core/tests/FusionRpg.E2E.Tests` uncompilable and its host unconfigured: two lanes moved a Core record and a Data registry without moving this assembly's bootstrap** · S · *found (measured) by lane `sim-t3-2`, 2026-09-23, on the tree after merging `features/mega-merge`*
  - **Measured, three independent breaks, each in a file neither lane owned:**
    1. `d5b1697a3 npc-story-events NR2.19` added a required `DangerBand` to `ExpeditionTierNumbers`
       (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs:5`) and a required `Encounter`
       (`ExpeditionEncounterTuning`) to `ExpeditionTuning`, but `ContractTuningTestBootstrap.cs`'s
       `DefaultExpeditions` still built both with the old arity — `error CS7036`, twice, so the E2E project
       did not build at all.
    2. The narrative lane made `RpgStore.OnboardingPlayerName()` read `LeadNamesHub.Current`
       (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4218`), which throws unless `LeadNamesHub.Configure` ran;
       `RpgApiFactory.SeedSpeciesRoster` builds its own store before `Program.cs` runs, so **every**
       `RpgApiFactory`-based E2E test threw `LeadNamesHub.Configure(...) has not run`. Data.Tests, Server.Tests
       and Core.Tests each configure it; this assembly did not.
  - **What this lane did:** fixed all three in `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs`
    (values mirrored from `gk-core/data/tuning/expeditions.v2.json` — `dangerBand` 1/2/3/4 and
    `wildCreatureMetMilli: 250, quietMilli: 50` — and `LeadNamesHub.Configure` reading the real
    `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`, exactly as Data.Tests does). **This is another
    program's defect fixed inside this lane's fence so the branch could be verified**; the owning programs
    should make the E2E bootstrap part of their own "move every reader" sweep.
  - **A fourth, related measurement:** with the E2E host finally running, the corpus's soul-ledger
    assertion was found to be a **presence** assertion on an RNG-dependent row (`$.items[*].reason contains
    "expedition"`), which flakes when the server-minted event-souls roll lands zero. It is now a closed
    vocabulary (see RS-F4's family) and the flake is gone — two consecutive `RpgSim` runs green.
  - **Owner of this row:** the **npc-story-events / narrative** program (broke 1 and 2), routed by the
    manager; `post_merge_check.py` is the gate that should have caught it.
  - **Acceptance:** a lane that adds a required parameter or a `Configure`-gated hub also updates every test
    assembly's bootstrap, and `dotnet build gk-core/tests/FusionRpg.E2E.Tests` is part of its own verification.
  - **Files:** `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs`,
    `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTuning.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4218`.
  - **RE-MEASURED ON THE ACCEPTING HEAD 2026-09-23 (lane `sim-t3-2`), and the finding's SHAPE IS CORRECTED.**
    The acceptance above is a rule for lanes to remember. The measurement says the gate already exists and
    works, and that the real defect is that **the merged head's gate is never run**:
    `pwsh -NoProfile -ExecutionPolicy Bypass -File .claude/cmdc-agents/scripts/post_merge_check.py` on
    `61d67f4cf` (the commit that accepted this lane's five commits) reads
    `build_exit=1 error_lines=1776 projects_with_errors=1` — **the one project being
    `FusionRpg.Injector.BepInEx.csproj`, which the script excludes by name** (it needs a game dir), so the
    build verdict is OK — and then `=== VERDICT: RED -- guards ===`:
    `Failed: 2, Passed: 671, Total: 673` (8 m 16 s) in `gk-core/tests/FusionRpg.Guard.Tests`. The gate therefore
    *would* have caught the `CS7036` breaks this row is about, and it caught two other lanes' reds instead.
    **Why it was not run: `ci.yml` triggers only on `push`/`pull_request` to `main`/`master`
    (`.github/workflows/ci.yml:4-9`), so a merge into `features/mega-merge` is never CI'd** — even though CI
    does build and test the E2E project (`ci.yml:333`, with its own exit check). `post_merge_check.py` is
    the only gate for that branch and its verdict is recorded nowhere the next lane sees. The two reds it
    found are filed below as **RS-F23** and **RS-F24** (neither this lane's, both in the protected
    `gk-core/tests/FusionRpg.Guard.Tests/**` tree).

- [x] **RS-F23 -- the Guard suite is red on the accepted head: a pytest project is in the verification registry with no CI step at its own working directory** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, running `post_merge_check.py` on `61d67f4cf`*
  - **Measured:** `FusionRpg.Guard.Tests.CiPytestWiringTests.Every_pytest_project_has_a_ci_step_running_pytest_in_its_own_root`
    → `pytest project root(s) with no 'python -m pytest' CI step at that working-directory: .`
  - **Cause (read, not guessed):** `gk-core/scripts/verification-boundaries.v1.json` carries
    `"tools-audit-tests": { "runner": "pytest", "root": ".", "tests": "gk-core/tests/tools" }`, and
    `gk-core/tests/tools/test_audit_program_pipeline.py` exists — but `ci.yml`'s three pytest steps run at
    `working-directory: gk-core/tools/tuning`, `gk-core/tools/ip-censor` and `gk-forge/tools/seedsmith`, never at `.`. The guard
    requires the step's working directory to EQUAL the project's own root, so the project is unwired — the
    exact defect that guard exists to catch (its own doc cites `tuning-py` as the precedent).
  - **Owner of this row:** the **pipeline-audit-v2 / BCU** program (it added `gk-core/tests/tools/`), or the
    **test-verification-boundary** program that owns `ci.yml`'s pytest wiring. Neither todo is in this lane's
    allowed paths, and `gk-core/tests/FusionRpg.Guard.Tests/**` is pipeline-protected, so the row is filed here for
    the manager to route.
  - **Acceptance:** either a `python -m pytest` step at `working-directory: .` covering `gk-core/tests/tools`, or the
    registry row's `root`/`tests` are corrected to where the suite actually lives; then the Guard suite is green.
  - **Files:** `gk-core/scripts/verification-boundaries.v1.json` (the `tools-audit-tests` row),
    `.github/workflows/ci.yml`, `gk-core/tests/tools/test_audit_program_pipeline.py`.
  - **PRE-READ FOR THE OWNER 2026-09-23 (lane `sim-t3-2`), so the fix is mechanical — and the REGISTRY ROW IS
    CORRECT AS WRITTEN.** `root: "."` + `tests: "gk-core/tests/tools"` means *run pytest from the repo root, targeting
    `gk-core/tests/tools`*, which matches the suite's own self-location (`REPO_ROOT = Path(__file__).resolve().parents[2]`,
    `gk-core/tests/tools/test_audit_program_pipeline.py:19`) and the shape `tuning-py` uses (`root: gk-core/tools/tuning`,
    `tests: "."`). So the missing piece is the CI step, not a registry correction: a `python -m pytest` line
    under a step whose `working-directory` is `.` (e.g. `python -m pytest gk-core/tests/tools -q -p no:cacheprovider`,
    with its own exit check). **Re-measured on the newest accepted head `90eea1c15`:** the test still failed
    there (`dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~CiPytestWiringTests"` → red), so
    the red was live, not stale — and it is now **CLOSED**, fixed by the TVB program: `d19154eb8 fix(tvb): the
    register re-verified at the merged head -- two rows close, the tools-audit-tests CI step lands` added exactly
    what this pre-read recommended — a step whose `working-directory` is `.` running
    `python -m pytest gk-core/tests/tools -q -p no:cacheprovider` with its own exit check
    (`.github/workflows/ci.yml:464-470`, with the guard's own failure message quoted in the comment above it).
    **Measured on the head that carries the fix:**
    `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --filter "FullyQualifiedName~CiPytestWiringTests|FullyQualifiedName~PlayerSpeciesMaterialiseCallerGuardTests"`
    → `Failed: 1, Passed: 6, Total: 7` — `CiPytestWiringTests` is **green**, and the one red is **RS-F24**'s
    pick-refusal pin. So the acceptance's first branch is met; the Guard suite's remaining red is RS-F24 alone.

- [ ] **RS-F27 -- the corpus's progression-ledger steps pass VACUOUSLY on an empty row set, and whether that set can be empty is argued, not measured** · XS · *found by lane `sim-t3-2`, 2026-09-24, while strengthening the corpus's roster floor*
  - **Measured:** `read.progression.ledger` is asserted by four steps — `expect.progression.kind` (`memberOf`
    player|species), `expect.progression.player` (`allEqual`), `expect.progression.run` (`allIn`) and
    `expect.progression.reason` (`allNonEmpty`). Every one of them is vacuously true on an empty array, so if a
    collect credited **no** XP rows, the ledger half of the corpus would pass while proving nothing.
  - **Why no `notEmpty` was added:** the corpus's own note says the row set is outcome-dependent by design
    ("a victory credits one XP reason, a defeat another"), and adding a presence assertion is exactly the
    RNG-dependent flake this lane already removed from the soul ledger (`expect.souls.ledger.expedition`, which
    flaked 1 run in 2). A presence guard here needs the emptiness question answered FIRST.
  - **The code reading, which is where it stands:** `RpgXpAwardMap.FromActivity`
    (`gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:47-65`) returns an award for `match.ended` only when the
    result is **defeat** (`:58-59`) and `Array.Empty<Award>()` otherwise — so a **victory or a stalemate credits
    nothing from that fact**. The rows a webrpg run does produce come from the spawn/placement facts (the species
    projection of `zombie.spawn`/`plant.place`, the only kinds a webrpg run may level, per the corpus's own
    `expect.progression.kind` comment), and a battle with no spawned zombie is not a battle — so the mechanism
    argument says the set is non-empty, and it is an argument, not a measurement.
  - **What would settle it:** N runs of the corpus recording `$.items.Length` (the in-process host makes each run
    cheap), with N large enough to cover the outcome vocabulary (victory / defeat / stalemate). Then either the
    corpus gains a non-vacuity guard with a measured floor, or the row records that the set CAN be empty and the
    vacuity is inherent to an outcome-dependent rule.
  - **Owner of this row:** `rpg-simulator` (this program owns the corpus).
  - **Acceptance:** the emptiness question is answered by measurement, and the corpus either carries a
    non-vacuity guard or says in its own notes that an empty ledger is a legal outcome.
  - **Files:** `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` (`read.progression.ledger` and its four
    assertions), `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:47-65`.

- [ ] **RS-F24 -- the Guard suite is red on the accepted head: a closed pick-refusal vocabulary gained a tenth code without moving its pin** · XS · *found (measured) by lane `sim-t3-2`, 2026-09-23, running `post_merge_check.py` on `61d67f4cf`*
  - **Measured:** `FusionRpg.Guard.Tests.PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`
    → `Assert.Equal() Failure: Collections differ` at `PlayerSpeciesMaterialiseCallerGuardTests.cs:121`: the
    expected nine include `picks.source-not-materialised` / `picks.source-rarity-unknown`, the actual set
    carries **`picks.source-below-rank-floor`** between `picks.source-below-inherit-floor` and
    `picks.source-not-a-sacrifice`.
  - **Cause (read, not guessed):** a lane widened the pick-refusal vocabulary by one code and did not move the
    guard's pin in the same commit — the rule `docs/DESIGN-GATE.md` states for every closed vocabulary ("a
    module that widens the vocabulary is not finished until this line moves with it").
  - **Owner of this row:** the program that owns the pick-refusal codes (species-build / `picks.*`) — its todo
    is outside this lane's allowed paths, and `gk-core/tests/FusionRpg.Guard.Tests/**` is pipeline-protected, so the
    row is filed here for the manager to route.
  - **Acceptance:** the guard's pinned list gains the tenth code (a reviewed widening, with the count and the
    reason), and the Guard suite is green.
  - **Files:** `gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:121`, the producer of
    `picks.source-below-rank-floor`.
  - **PRE-READ FOR THE OWNER 2026-09-23 (lane `sim-t3-2`) — the widening is LEGITIMATE, so the PIN should move,
    and the re-read is done here so the owner's edit is two lines.** The producer's own comment above the line
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:299-305`) documents the new code as a SECOND, DISTINCT gate:
    *"spec-species-rank.md §6: the rank floor lands BESIDE the rarity floor above, and reads the SOURCE species'
    own rank — a null (skipped) rank maps to bottom here. The endpoint's preview consults the same policy for the
    same gate, so it never offers a pick this line would refuse."* So it is not a duplicate of
    `picks.source-below-inherit-floor` (which reads `CreatureRarityLadder`/`OutputEligibilityFloor`), and the two
    refusals answer different questions. The guard's own comment says exactly what to do with that:
    *"A tenth code is a reviewed change that should fail this test and be re-read; that is the opposite of the
    species-count anti-pattern"* (`:90-93`). **The fix is therefore two lines in the protected test file:** add
    `"picks.source-below-rank-floor",` to `expected` and change `Assert.Equal(9, found.Count)` to `10`.
    **Re-measured on the newest accepted head `90eea1c15`:** still red
    (`dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpeciesMaterialiseCallerGuardTests"`
    → 2 failed / 5 passed / 7 total).

- [ ] **RS-F21 -- two checked-in E2E fixtures drifted on the merged tree, from another program's rename, so the full E2E project is red for a reason this lane did not cause** · S · *found (measured) by lane `sim-t3-2`, 2026-09-23, running the full E2E project after the merge repair*
  - **Measured:** `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo` →
    `Failed: 2, Passed: 284, Total: 286` (3 m 55 s). Both reds are fixture-drift assertions:
    1. `ContractFixtureTests.Commander_list_fixture_matches_live_dto` — the checked-in fixture says
       `"displayName": "Garden Keeper"`, live now returns `"Crazy Dave"`.
    2. `WorldTurnFixtureTests.The_checked_in_turn_fixture_still_matches_a_real_played_opening` — the
       checked-in `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json` has
       `stateHash 0f685a162409f54a3af53…`, a real played opening now has `b41ce3ef4c7c6c814ccf0…`.
  - **Cause (read, not guessed):** both come from the merged **identity-rename** lane.
    `e965f65e2 identity-rename T12: the antagonist commander's name comes from the lead names registry`
    changed `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`'s `displayName` to
    `{lead_antagonist}` (now resolved from the lead-names registry), and `29cf63d6d identity-rename T13`
    changed how a new world takes its names — a different world state, hence a different `StateHasher.Hash`.
    `git log 5252537b6..HEAD -- <the world fixture>` is **empty**: neither fixture was regenerated.
  - **Not this lane's, and not re-blessed:** the world-turn hash is `Core/World` state
    (`gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:89` names `StateHasher.Hash`), and the world-sim purity
    scan bans every wall-clock symbol there — so the clock migration cannot move it. Moving a golden to make
    a test pass is the defect, not the fix; the owning program regenerates its own fixture (the world test
    even names its own escape hatch, `FUSIONRPG_BLESS_WORLD_FIXTURE=1`).
  - **Owner of this row:** the **identity-rename / narrative** program (both changes are its), routed by the
    manager.
  - **Acceptance:** the two fixtures are regenerated by their owning program and the full E2E project is
    green.
  - **Files:** `gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs`,
    `gk-core/tests/FusionRpg.E2E.Tests/WorldTurnFixtureTests.cs`,
    `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/first-light-turn.json`,
    `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`.
  - **FINISH ATTEMPTED 2026-09-23 (lane `sim-t3-2`) -- the FIX IS OUT OF THIS LANE'S FENCE, and the analysis is
    complete so whoever holds `web/**` finishes it in one step.** The fixtures live under `web/**`, which is
    not in this lane's allowed paths, so the blessed edits were **reverted** (the tree is clean); the C# reds
    therefore stay red, and they should, because a fixture outside the fence cannot be re-blessed from here.
  - **THREE fixtures now, not two (re-measured on the head that accepted this lane's work, 240 commits on).**
    `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ContractFixtureTests|FullyQualifiedName~WorldTurnFixtureTests"`
    → `Failed: 3, Passed: 0, Total: 3`. The third is `ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto`,
    which **matched exactly** when this lane first measured it: the merged identity work ADDED a field, so the
    fixture is stale by one added line rather than by a rename.
  - **All three re-bless paths exist and were exercised, then reverted.** Each test carries its own documented
    escape hatch, and each produced a diff limited to the intended change — captured with
    `FUSIONRPG_BLESS_CONTRACT_FIXTURES=1` on `ContractFixtureTests` and `FUSIONRPG_BLESS_WORLD_FIXTURE=1` on
    `WorldTurnFixtureTests`, then `git diff web/` and `git checkout -- web/`:
    1. `commander-list.json` — **1 line**: `"displayName": "Crazy Dave"` → `"Garden Keeper"`. The live value
       is the **player's own name**, which is what the registry row asks for:
       `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` gives `commander:dave`
       `displayFromPlayer: true`, and the player is named from
       `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (`"Garden Keeper"`). `Crazy Dave` is the pre-T12 literal.
    2. `unique-actor.json` — **1 line ADDED**: `"empireId": "dave"` (the merged identity work added the field
       to the live DTO; nothing else in the fixture moves).
    3. `first-light-turn.json` — **exactly six lines, all `stateHash` values** (`b41ce3ef…`→`0f685a16…`,
       `5fdb30fb…`→`a1ef7007…`, `a67e7fb4…`→`6a560c35…`, `94cdcc42…`→`033ad563…`, `bd46325b…`→`16c5add8…`,
       `601ccb04…`→`211e6322…`). No entry, phase, battle, halt or visibility class moves, which is the
       signature of a change to state the hash covers but the report does not render — T13's registry-derived
       names. That the narrative is byte-identical also means the property the fixture exists to prove (Dave's
       own account excludes Zomboss's runway line) still holds.
  - **One coupling the owning lane must move at the same time:** `gk-web/web/fusion-rpg-web/e2e/commander-surface.spec.ts`
    fulfils its default case from `fixtures/commander-list.json` and then asserts the LITERAL `"Crazy Dave"`
    (line 158, and again at 178/188/199/237/249 for the two-commander case). Re-blessing the fixture alone would
    turn that Playwright spec red, so fixture + spec literal move together -- which is another reason this
    belongs to the lane that owns `web/**`.

- [x] **RS-F5 -- the map's promised module specs live at `docs/architecture/rpg-simulator/spec-*.md`, a tree this lane's fence excludes** · XS · *found by lane `sim-runner`, 2026-09-23*
  - **Measured:** `docs/architecture/rpg-simulator-map.md` names ten `spec-<module-id>.md` paths under
    `docs/architecture/rpg-simulator/`; this lane's fence is `gk-core/tools/RpgSim/**`, `gk-core/tests/fixtures/rpg-scenarios/**`,
    `gk-core/tests/FusionRpg.E2E.Tests/**` and `tasks/**`, so none could be written there.
  - **What was done instead:** the RS2.1 contract is `gk-core/tools/RpgSim/scenario-format.md`, beside the machine that
    enforces it (`gk-core/tools/CombatSim/README.md` is the precedent), and its header says why. The same will apply to
    `gk-core/tools/RpgSim/readback-verdict.md` (RS2.2).
  - **Acceptance:** either the map's spec paths are repointed to the tool (an erratum on
    `docs/architecture/rpg-simulator-map.md` — a tree outside every lane's fence), or the specs are moved into
    `docs/architecture/rpg-simulator/` by whoever holds that fence and the tool keeps only its README. The
    manager should rule which.
  - **Files:** `docs/architecture/rpg-simulator-map.md`, `gk-core/tools/RpgSim/scenario-format.md`.
  - **RESOLVED 2026-09-23 (lane `sim-t3-2`) against the acceptance's FIRST branch — the map is repointed, and
    the erratum is written in the map itself.** Every module row's Spec column now names that module's REAL
    document: `gk-core/tools/RpgSim/scenario-format.md` (2), `gk-core/tools/RpgSim/readback-verdict.md` (3),
    `gk-core/tools/RpgSim/README.md` + the CLI's usage block (4), `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs` +
    `RpgSimInProcHostTests.cs` (5), `gk-core/tools/RpgSim/ProcessHost.cs` + `RpgSimProcessHostTests.cs` (7),
    `scripts/guard-sim-fabrication.ps1` + its registry row (8), and the two seam specs that are siblings of
    the map (10 `rpg-simulator-spec-clock-seam.md`, 11 `rpg-simulator-spec-seed-seam.md`). Row 1's contract IS
    the test and the corpus file. **Two rows say NOT WRITTEN on purpose**, with the reason in the cell:
    `shared-store-home` (its premise was retired — `gk-core/tools/RpgSim` stayed store-free, and RS-F6 is the surviving
    question) and `sim-ci-lane` (RS7 is open and owns it). The map's header no longer promises a tree: it says
    the rule — a contract a machine enforces lives beside that machine, a contract that IS a mechanism lives
    in the file implementing it, and a seam gets a sibling spec because no single machine owns it.

- [x] **RS-F4 -- two server-minted RNG seeds make the post-summon half of the corpus non-deterministic, so the digest cannot cover values** · S · *found (measured) by lane `sim-runner`, 2026-09-23, in RS2.4*
  - **Measured:** two runs of `first-session-forward` on fresh in-process hosts, same seed, same file:
    the scenario's DECLARED digest is identical
    (`daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`, both runs) while the falsifier over
    EVERY reading moves 71–110 named pointers (the count itself varies). What moves:
    `roster[*].profile.speciesId`/`.rarity`/`.elementPrimary`, `actor.typeId`, `actor.side`,
    `squadInstanceIds` (fresh GUIDs), the reward and XP amounts attributed to those specimens.
  - **Cause (read, not guessed):** the summon route mints its own seed,
    `BitConverter.ToUInt64(Guid.NewGuid().ToByteArray(), 0)` (`gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:96`),
    and expedition dispatch mints another (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:36`). Neither is
    reachable from a scenario: the scenario's seed drives only the correlation id, and it cannot be sent to
    either route. So no scenario can make the roster or the battles repeat, and RS2.4's digest identity is
    met only over the declared residue (a terminal state, a tier, a row id, the run engine).
  - **Why it is a finding and not a bug to route around:** owner ruling D3 stands — the untestability IS the
    finding, and no new `/api/sim/*` route licenses it. The fix is a **seed seam** (accept a scenario seed,
    or derive it from the correlation id the scenario already controls), which is product-shaped work of the
    same class as RS3's clock seam and must be decided by its own spec, not smuggled into a runner.
  - **Owner of this row:** `rpg-simulator` (this program) for the seam's spec; the routes are the creature and
    expedition families'.
  - **Acceptance:** either a seed seam exists and the corpus's declared digest can cover roster and battle
    values (measured by the same double-run test), or the program states in its plan that the digest is
    intentionally scoped to host-stable readings and names this as the reason.
  - **Files:** `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:96`,
    `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:36`, `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs`.
  - **SPEC WRITTEN 2026-09-23 (lane `sim-t3-2`): `docs/architecture/rpg-simulator-spec-seed-seam.md`**
    (map module row 11), plus **acceptance branch (b) satisfied** by
    `tasks/rpg-simulator-plan.md` §11: the digest is intentionally scoped to host-stable readings, and the
    reason is named there with the measurement. What the spec records:
    - **A measured correction to this row: FOUR mint sites, not two.** `CreatureEndpoints.cs:95` (summon),
      `ExpeditionEndpoints.cs:38` (dispatch), `FusionEndpoints.cs:39` (fusion execute) and
      `WebMatchService.cs:122` (the web-match battle seed). All four already have a caller-supplied
      idempotency key in scope, which is what makes one seam possible instead of four mechanisms.
    - **The shape:** `seed = (ulong)WorldSeed.DeriveRollSeed(playerId, "<route stream>", correlationId)` —
      reusing the EXISTING derivation chain (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`, whose own
      doc says it is the ONE place that hash is computed) rather than inventing a third hash, with one named
      server helper so the four sites cannot drift.
    - **Refused shapes with reasons:** a `seed` body field; a `/api/sim/*` seed route (owner ruling D3 (b));
      a server-global seed config (**wrong scope** — a clock is per-process, a seed is per-request, and a
      global would make every player's roll identical); and a **per-save secret** (`HMAC(saveSecret, key)`),
      which defends predictability but **defeats this program's purpose**: the double-run falsifier runs on
      fresh hosts, so each host generates a fresh secret and the digests could never agree.
    - **The one thing that wants a ruling:** the derivation is public, so a client could compute a chosen
      key's roll offline. The *capability* is not new (a player can already reroll without limit, paying the
      route's cost each time); the *cost of searching* drops from pay-per-roll to compute-per-roll. Filed as
      the spec's §6 question, and the reason increment 1 has not been started.
  - **Still owed:** increment 1 (the helper + the four call sites) once the predictability question is
    ruled, then increment 2 (the corpus's declared digest covers roster and battle values, measured by the
    double-run falsifier's residue shrinking). A guard that fails a fifth mint is owed WITH increment 1.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`) against the acceptance's SECOND branch**, which is what the row
    itself offers: *"or the program states in its plan that the digest is intentionally scoped to host-stable
    readings and names this as the reason."* That statement is now `tasks/rpg-simulator-plan.md` §11 item 3 —
    it names the four seeds, the 71–110 moved pointers, and RS-F4 as the reason — so the digest's scope is a
    decision with a citation rather than an accident. The seam itself is **not** dropped: it has its own spec
    (the row's own requirement: *"must be decided by its own spec, not smuggled into a runner"*) and its
    implementation is carried forward as **RS-F22** below, waiting on the predictability ruling.

- [ ] **RS-F22 -- the seed seam's implementation: one named helper + the four mint sites, waiting on the predictability ruling** · S · *split out of RS-F4 by lane `sim-t3-2`, 2026-09-23, when RS-F4 closed against its plan-statement branch*
  - **What it is:** the two increments the spec's §7 sets — (1) `CorrelationSeed.For(playerId, stream,
    correlationId)` beside the four sites (`CreatureEndpoints.cs:95` summon, `ExpeditionEndpoints.cs:38`
    dispatch, `FusionEndpoints.cs:39` fusion execute, `WebMatchService.cs:122` web-match), each deriving
    through the existing `WorldSeed.DeriveRollSeed` chain, plus a guard that fails a fifth mint; then
    (2) the corpus's declared digest covering the roster and the battle values, with the double-run
    falsifier's residue re-measured as the reading.
  - **The blocker is a ruling, not a fence or a missing mechanism:** the derivation is public, so a client
    could compute a chosen key's roll offline. The spec's §5/§6 argue the *capability* is not new (a player
    can already reroll without limit, paying the route's cost each time) and that every defence that would
    hide it either refuses the seam (a `seed` field, a `/api/sim/*` route, a global seed) or defeats its
    purpose (a per-save secret, because the double-run falsifier runs on fresh hosts). That argument needs
    the owner's yes before four live economy routes change what a player can compute.
  - **Owner of this row:** the owner (predictability of a live roll), routed by the manager.
  - **Acceptance:** the predictability question is ruled; then the four sites derive through one helper and
    a fifth mint fails a guard; then the falsifier's moved-pointer count drops to the named per-run values
    (fresh GUIDs, insert counters, wall-clock stamps) and that count is reported.
  - **Files:** `docs/architecture/rpg-simulator-spec-seed-seam.md`, `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:95`,
    `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:38`, `gk-core/src/FusionRpg.Server/FusionEndpoints.cs:39`,
    `gk-core/src/FusionRpg.Server/WebMatchService.cs:122`, `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`.

- [x] **RS-F7 -- the XP ledger row's timestamp is a one-letter field (`t`), which the digest cannot safely exclude by name** · XS · *found (measured) by lane `sim-runner`, 2026-09-23, in RS2.4*
  - **Measured:** the whole-reading falsifier named `$.read.progression.ledger.value.items[0].t` moving
    `"2026-09-22T21:23:12.0639753Z" -> "2026-09-22T21:23:34.7611387Z"` between two runs.
  - **Cause (read, not guessed):** `ReadingDigest.IsExcluded` blanks an excluded name everywhere it appears, so
    a name this generic cannot be added to `Baseline` without risking a silent blanking of a value that
    matters in another payload. The ledger's own payload should carry a self-describing name
    (`createdUtc`/`at`), the way every other family's timestamps do; until it does, a scenario that wants to
    digest the ledger must declare the exclusion itself.
  - **Not smoothed:** the shipped scenario's declared digest does not include the ledger, so the artifact it
    produces is honest today. This row exists so the next scenario author does not rediscover it.
  - **Owner of this row:** unknown — the payload's shape belongs to whichever program owns
    `read.progression.ledger` (the progression surface); this lane cannot tell, so the manager should route it.
  - **Acceptance:** the ledger payload names its timestamp field self-describingly and the digest's exclusion
    list covers it by pattern, or `rpg-simulator`'s contract records that the ledger is not digest-eligible
    and says why.
  - **CLOSED 2026-09-23 (lane `sim-t3-2`) against the acceptance's second branch.** The contract now says it:
    `gk-core/tools/RpgSim/readback-verdict.md` §3 states **the XP ledger is NOT digest-eligible** and that a scenario
    wanting to digest it must declare the `t` exclusion itself with its own reason (the validator refuses a
    reasonless exclusion), and `ReadingDigest.Baseline`'s own doc comment carries the same line beside the
    list it constrains. **Not closed:** the payload-shape half — a self-describing `createdUtc` would let the
    ledger become an ordinary `*Utc` exclusion — stays with the progression surface that owns the payload,
    and is named as such in the doc rather than left implicit. Evidence:
    `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --nologo --filter "FullyQualifiedName~RpgSim"` →
    `Passed: 46, Failed: 0, Total: 46`.
  - **Files:** `gk-core/tools/RpgSim/readback-verdict.md` §3, `gk-core/tools/RpgSim/ReadingDigest.cs`.

- [x] **RS-F6 -- the CLI has no `--host inproc`: the in-process factory lives in the E2E test project a tool may not reference** · XS · *found by lane `sim-runner`, 2026-09-23, while building RS2.3*
  - **Measured:** `dotnet run --project gk-core/tools/RpgSim -- --scenario <f> --run --host inproc --base-url <u>`
    exits 2 with a named refusal. There is no way for the tool to boot the real `Program` itself:
    `WebApplicationFactory<Program>` needs the app assembly plus a content root, and the working factory
    (`gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs`) is in a test project, which the tool must not
    reference (a test project referencing the tool is the correct direction, and is what RS2.3 shipped).
  - **Why it is not a blocker:** RS2.4's acceptance is "the same scenario file runs in-process on
    `WebApplicationFactory<Program>` … reusing `RpgApiFactory`" — which is exactly what
    `RpgScenarioSlice0E2ETests` does now, and what the plan's §7 risk 2 predicted ("the runner then hosts
    from the E2E assembly and the CLI is a front end; the module boundaries survive"). No acceptance line
    needs the CLI to host in-process: RS7's fast lane is the E2E project, and its slow lane uses
    `--base-url` against a real server (RS2.5).
  - **Acceptance:** either a deliberate decision that the CLI is a real-process front end only (and the
    map says so), or a `tools/`-reachable in-process bootstrap (a `tools/RpgSim.Host` project, or a
    shared non-test home for the factory, which is RS6/F3's territory).
  - **DECIDED 2026-09-23 (lane `sim-t3-2`) against the acceptance's FIRST branch: the CLI is a real-process
    front end only, and the map says so.** The decision is recorded in three places that a reader actually
    reaches: the map's module-4 row ("It is a real-process front end only (RS-F6, decided 2026-09-23)"), the
    tool's README host table ("refused by design, and that is the decision"), and the CLI's own refusal text
    (which now says "refused by design" and names the two real transports instead of "not implemented").
    The reasons, in the code's own terms: the in-process host is a run parameter of the **embedding** host
    (`RpgApiFactory` boots the real `Program` and supplies the `HttpClient`), a tool that referenced the app
    assembly plus `Microsoft.AspNetCore.Mvc.Testing` would carry the whole server for no acceptance line the
    program has, and `gk-core/tools/RpgSim/RpgSim.csproj` today carries **no `ProjectReference` and no
    `PackageReference` at all** — a dependency-free tool that takes an `HttpClient`. The second branch stays
    available to whoever holds the shared-home fence (RS6/F3) but is not needed.
  - **Files:** `docs/architecture/rpg-simulator-map.md` (module 4), `gk-core/tools/RpgSim/README.md`,
    `gk-core/tools/RpgSim/RpgSimCli.cs`.
  - **Files:** `gk-core/tools/RpgSim/RpgSimCli.cs`, `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs`.

> **This block is a roll-up of the owner-cleared row keys, kept for the decision sheet's vocabulary. The
> WAVE-SECTION ROWS BELOW ARE THE REAL ONES** — a task's state lives there, and the roll-up line is a
> pointer, not a status. It went stale once already: it showed `RS1` and `RS5` unchecked after both were
> delivered, and `RS2` as one row after it was split into `RS2.1`–`RS2.5`. Corrected 2026-09-23 by lane
> `sim-runner`; the wave rows are what a reader and the ledger count.

- [x] **RS2 -- the runner: `gk-core/tools/RpgSim` reading a scenario file** · M · *approved A1 (a) / E2 (a)*
  Same scenario file, two hosts (in-process default, real process slow lane). Depends on RS1 only for the
  scenario format it must read. **Split into the wave-2/3 rows below: `RS2.1`–`RS2.5` are all delivered
  (2026-09-23, lanes `sim-runner` and `sim-t3-1`).**
- [x] **RS3 -- the clock: full `TimeProvider` migration, then retire `ForceExpeditionDue`** · L ·
  *approved B1 (a), B3 (a); B2 (b) makes it product surface* · **gated by the `decisions.md` row** (written --
  `docs/architecture/decisions.md`) and by a spec that names the seam's product shape. The measured surface is
  in that row: 203 sites, 143 mechanical, 25 already injectable, **9 that must not be simulated**. See the
  Wave 5 row.
- [x] **RS4 -- a scenario-honesty guard** · S · *approved D4 (b)* -- a scenario may not assert on state it
  created through anything but a real route. See the Wave 3 row.
- [x] **RS5 -- the program's map + plan** · S · *approved A3 (a)* -- `docs/architecture/rpg-simulator-map.md` +
  `tasks/rpg-simulator-plan.md`, module ids, and the CI decision (C3 (c): slice 0 is local-only).
  **Delivered 2026-09-22 (lane `rpg-simulator-map`); see the Wave 0 row for the evidence.**

### Wave 1 — slice 0: the shape, with no product code

- [x] **RS1 — one E2E scenario file, the four-family chain** · S · *approved E1 (a) / A2 (a) / C3 (c)* · module: **`first-session-scenario`**
  - **Delivered 2026-09-22 (lane `sim-slice0`); re-pointed at the tool in RS2.3.** The chain now runs
    through `ScenarioRunner` with the file at `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`
    migrated to the RS2.1 contract; see the RS2.3 row.
  - Acceptance: one new test file under `gk-core/tests/FusionRpg.E2E.Tests/` plays create player → earn souls
    through the **real earn path** (a sim match into `EventIngest`, as `SoulsE2ETests` does — **not**
    `/api/test/seed-souls-demo`, which writes the balance row directly) → summon → read the roster back
    → dispatch an expedition → make it due → collect → read the progression summary, the XP ledger and
    the run list. Every step is a real route; no product code is added.
  - Acceptance (the fabrication line): the test asserts the squad the battle resolved with came from the
    roster it just built — the `InstanceIds` `BuildSquad` returns (`gk-core/src/FusionRpg.Server/WebMatchService.cs:527`) —
    so the empty-roster `Synthetic` fallback (`:573`, `:713`) cannot pass silently.
  - Acceptance: green **locally**; **no** new CI gate (C3 (c)).
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tests/FusionRpg.E2E.Tests/<scenario file>.cs -Session <id>`
  - If the chain does not run, that is the finding: report it as a reachability defect with `file:line`.

### Wave 2 — the contract, the runner, the fast host

- [x] **RS2.1 — the scenario contract** · M · *approved C1 (a)* · module: **`scenario-format`**
  - Acceptance: the envelope (id, seed, declared clock, host) and the **closed** op vocabulary
    (`sim.*` / `api.*` / `read.*` / `expect.*` / `digest`), ops named after the route they call; a
    `read.*` must name an FE-facing route or a hub message; the extend-vs-share decision for the
    effect-scenario step DTO (`gk-core/src/FusionRpg.Core/Effects/EffectScenarioRunner.cs:80-81`) is made with
    the expressibility test the shape lane could not run.
  - Acceptance: `gk-core/tests/fixtures/rpg-scenarios/**` is the corpus home, and its verification boundary is
    added in the same change.
  - Verify: `.\scripts\verify-change.ps1 -Paths docs/architecture/rpg-simulator/spec-scenario-format.md,gk-core/tests/fixtures/rpg-scenarios/**,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - **Delivered 2026-09-23 (lane `sim-runner`).** Contract at `gk-core/tools/RpgSim/scenario-format.md`; machine at
    `gk-core/tools/RpgSim/{ScenarioFormat,ScenarioVocabulary,ScenarioValidator,JsonPointer,CanonicalJson}.cs`; the CLI
    `rpg-sim --scenario <file> --validate` frames it. The envelope (id, seed, declared clock, corpus home) and
    the closed op vocabulary (`sim.*` / `test.*` / `api.*` / `read.*` / `expect.*` / `digest`) are specified;
    the surface prefix is derived from and checked against the route, and a step whose declared route is not the
    route its op calls is refused — RS1's property, with one copy of the table.
  - **`test.*` added to the plan's four call prefixes**, with the measurement: the shipped slice-0 chain calls
    `POST /api/test/seed-souls-demo` and `POST /api/test/expedition-due`, which are neither `/api/sim/*` nor
    player-facing. Folding them into `sim.*` would lose the fixture-surface distinction the RS4 guard needs.
  - **`host` is a run parameter, not an envelope field** (owner ruling E2 (a): one file, two hosts). Documented
    in `scenario-format.md` §2 as the one place this row reads the plan differently.
  - **The extend-vs-share decision is made with the expressibility test**: `EffectScenarioStepDto` cannot carry
    `route`/`args`/`capture`/`why`, its `expect` is an `IntentPlanDto` (an effect plan), and the loss is
    SILENT because the serializer ignores unknown members. Decision: share the envelope and the fixture
    convention, not the step DTO. Proof: `RpgSimFormatContractTests` (asserted from both sides).
  - **The corpus home's boundary is present, not added here:** `gk-core/tests/fixtures/rpg-scenarios/**` is mapped as
    `e2e-scenario-fixtures` by `80f388db7` (row `TVB-F23`), so `RS-F2`'s acceptance is met and RS-F2 is closed
    with that run in `tasks/reports/rpg-sim-rs21.md`.
  - **`gk-core/tools/RpgSim/**` itself has no boundary** — `verify-change.ps1` refuses it (`VERIFICATION BOUNDARY
    MISSING`, `scripts/verify-change.ps1:114`). Filed as **RS-F3**; this lane's fence excludes `scripts/**`.
  - **Evidence:** `tasks/reports/rpg-sim-rs21.md` — `Failed: 0, Passed: 20` on `RpgSimFormatContractTests`;
    `rpg-sim --validate` green on a valid scenario and exit 1 with three named refusals on an invalid one.
  - **Not proved:** the shipped slice-0 fixture was still in RS1's shape at this commit — migrated in RS2.3 with the runner that reads it. **Closed in RS2.3:** the corpus is migrated and `RpgSimFormatContractTests.The_shipped_corpus_validates_against_the_contract` now validates every file under `gk-core/tests/fixtures/rpg-scenarios/**` against the format.
- [x] **RS2.2 — the verdict and digest contract** · M · *approved C2 (a)* · module: **`readback-verdict`**
  - Acceptance: every reading records its **source path**; no digest-bearing read comes from
    `/api/test/snapshot` (`gk-core/src/FusionRpg.Server/SimEndpoints.cs:144`); the digest's **exclusion list is
    written down with a reason per field** (`gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:163-172`);
    golden artifact **and** hash (C2 (a)); the same-run double-run falsifier.
  - Verify: `.\scripts\verify-change.ps1 -Paths docs/architecture/rpg-simulator/spec-readback-verdict.md -Session <id>`
  - **Delivered 2026-09-23 (lane `sim-runner`).** Contract at `gk-core/tools/RpgSim/readback-verdict.md`; machine at
    `gk-core/tools/RpgSim/ScenarioVerdict.cs` (`readings[].source` is non-optional on the type + `Validate()` refuses a
    source-less reading) and `gk-core/tools/RpgSim/ReadingDigest.cs` (`Baseline` exclusion list, canonical form, hash,
    `Compare` = the falsifier with **named moved pointers**).
  - **The snapshot rule is a strict superset:** a `read.*` may not name `/api/test/*` or `/api/sim/*` at all
    (RS2.1's validator), so a digest-bearing read cannot come from `/api/test/snapshot` — the narrower rule
    is implied, and the wider one is cheap. `digest.include` may only name a declared `read.*` reading, which
    is what keeps a POST body out of the hash.
  - **The exclusion list:** ten `(field, reason)` entries, suffix-patterned (`*Utc` covers the six spellings of
    the same ambient clock). A test asserts every entry's reason is substantive; every verdict prints the list
    it used. The list is extended **by measurement**, and the falsifier names the moved pointers.
  - **Non-vacuity is asserted, not assumed:** the digest moves when a read value moves, and does not move when
    an excluded field moves (both tests). A digest that could not move would be a constant with a pretty name.
  - **Golden artifact (C2 (a)):** specified at `gk-core/tests/fixtures/rpg-scenarios/golden/<id>.verdict.json`
    (`readback-verdict.md` §5) with its role narrowed — it pins the stored artifact and its digest, while
    outcome-dependent rows stay `expect.*` rules. Not yet written: no run reaches a golden until RS2.3/RS2.4.
    **LANDED 2026-09-23 (lane `sim-t3-2`):** the golden exists
    (`gk-core/tests/fixtures/rpg-scenarios/golden/first-session-forward.verdict.json`, declared digest
    `daa9df408054f32e…`), `gk-core/tools/RpgSim/GoldenVerdict.cs` compares the digest, the seed, the reading set and the
    exclusion fields (never the values — §5's own second bullet), the CLI gained `--golden`/`--update-golden`,
    and `RpgSimGoldenTests` compares a fresh run against it with a falsifier seen to fail. The RS4 guard skips
    the `golden/` subtree and prints the count it skipped. Evidence: `tasks/reports/rpg-sim-golden.md`.
  - **Evidence:** `tasks/reports/rpg-sim-rs22.md` — `RpgSim*Tests` 35/35; the full E2E boundary 268P/1F
    (the failure is RS-CF2, filed, and its row now carries this second reproduction) then green on a re-run.
- [x] **RS2.3 — `gk-core/tools/RpgSim`, the runner** · M · *approved A1 (a)* · module: **`scenario-runner`**
  - Acceptance: reads a scenario, owns the seed, drives **one sequential client**, writes the verdict
    JSON, and **refuses unless the target reports `simEnabled: true`**
    (`gk-core/src/FusionRpg.Contracts/Dtos.cs:48`); contains **no domain math**.
  - Acceptance: `gk-core/tools/RpgSim/**` gains a verification boundary; only the tool's pure parts are
    referenced by a test project (the `gk-core/tools/CombatSim` relationship).
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/**,gk-core/scripts/verification-boundaries.v1.json -Session <id>`
  - **Delivered 2026-09-23 (lane `sim-runner`).** `gk-core/tools/RpgSim/ScenarioRunner.cs` (one sequential client;
    call/read/expect/digest dispatch; captures with the route they came from; no retry), 
    `ScenarioExpectations.cs` (the closed assertion vocabulary executed — 11 checks, none computing),
    and the CLI's `--run --base-url --out --double-run`.
  - **Two refusals, both before anything runs, both through the REAL bootstrap:** `simEnabled:false`
    (proven with a real `FUSIONRPG_SIM`-unset `Program`) and a live injector (proven by posting the real
    `/api/heartbeat` and reading `/health` back). Both write a verdict with `refused:true` and the reason.
  - **The corpus is migrated** to the contract (`35` steps: 6 calls, 7 read-backs, 22 declared
    assertions, 1 digest) and `RpgScenarioSlice0E2ETests` now drives it through the tool instead of a
    hand-rolled switch, so the fabrication line is declared in the scenario file and asserted by the
    runner. RS1's chain is green: `readings=7 captures=5 digest=daa9df408054f32e…`.
  - **CLI refusals are named, never silent:** `--host inproc` refuses by name (filed **RS-F6**), a hub read
    refuses by name (no SignalR client in this wave — the format allows it, the runner says so).
  - **`gk-core/tools/RpgSim/**` still has no verification boundary** (RS-F3, `scripts/**` is outside the fence), so
    the evidence is direct `dotnet test` / `dotnet run` output.
  - **Evidence:** `tasks/reports/rpg-sim-rs23.md` — RpgSim* + slice-0 `40/40`; whole E2E boundary
    `273/273` (2 m 4 s, no RS-CF2 flake this run); CLI validate/run-refusal/host-refusal transcripts.
  - **Not proved:** the CLI's `--run` transport against a LIVE server (no server was started — RS2.5's slow
    lane owns it); `--double-run` against one target (RS2.4 measures the falsifier on fresh hosts).
- [x] **RS2.4 — the default in-process host** · S · *approved E2 (a)* · module: **`inproc-host`**
  - Acceptance: the same scenario file runs in-process on `WebApplicationFactory<Program>` with its own
    `FUSIONRPG_DATA`, reusing `gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs:9`; "settled" is **defined by
    polling**, not assumed; the digest is identical across two consecutive runs on a fresh data dir.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`
  - **Delivered 2026-09-23 (lane `sim-runner`).** `gk-core/tools/RpgSim/SimSettler.cs` + the runner's two settle
    points (before the first step, before the digest); the verdict carries `settle:{settled,polls,elapsedMs}`
    and `Validate()` refuses a non-refused verdict without one. `RpgSimInProcHostTests` runs the corpus
    twice on two fresh `RpgApiFactory` hosts (fresh = a fresh shared-memory data source, the memory plan
    TARGET 0 landed; the keeper's disposal IS the cleanup, so nothing leaks).
  - **Acceptance met, measured:** the declared digest is identical both runs —
    `daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`; settle `polls=2 ~107ms` each.
  - **The falsifier over EVERY reading moves (71–110 named pointers) and that is the finding, not a
    smoothing target.** The cause is two server-minted RNG seeds (summon
    `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:96`, expedition dispatch
    `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:36`) → **RS-F4**; and an unnamed timestamp field (`t`, the XP
    ledger row's own) → **RS-F7**. `activityFactId` (a per-row insert counter) was named by the measurement
    and added to the exclusion list with its reason in this commit — the contract's own rule ("extend by
    measurement, never by guessing"), executed.
  - **Evidence:** `tasks/reports/rpg-sim-rs24.md` — 3/3 `RpgSimInProcHostTests`, whole E2E boundary
    `276/276`, the settled/digest/moved-pointer transcripts, and the two stub cases (never-settles,
    dropped-events) proving "I could not tell" is a failure rather than a pass.
  - **Not proved:** the real-process host and the cross-host comparison (RS2.5); a seed seam for the RNG
    divergence (RS-F4); `--host inproc` from the CLI (RS-F6).
- [ ] **RS6 — `DataTestStore` gets a shared, non-test home** · S · *approved F3 (a)* · module: **`shared-store-home`** · **BLOCKED on the lane fence (denied paths), and its premise needs a manager ruling**
  - Acceptance: a `tools/` consumer reaches the helper without a `<Compile Include>` link, with **no
    `src/` change**, and every existing consumer keeps compiling.
  - Acceptance: `data-test-substrate`'s "Test-only" line
    (`docs/architecture/data-test-substrate-map.md:82`) is corrected, or the erratum is filed on that
    program and named here. **Jointly owned.**
  - Verify: `.\scripts\verify-change.ps1 -Paths <the moved helper>,gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj,gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj,gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj -Session <id>`
  - **Blocked 2026-09-23 (lane `sim-runner`), for two independent reasons — both need the manager, neither is
    work this lane can start:**
    1. **Denied paths.** The helper's home is `gk-core/tests/FusionRpg.Data.Tests/DataTestStore.cs` and it is
       referenced by **314** test files through `<Compile Include>` links across
       `FusionRpg.Data.Tests`, `FusionRpg.Core.Tests`, `FusionRpg.Core.Match.Tests`, `FusionRpg.Server.Tests`
       and `FusionRpg.E2E.Tests` (`grep -rln DataTestStore tests/ --include=*.cs | wc -l` → 314). A move
       needs that helper's project plus at least five consumer csprojs; this lane's fence allows only
       `gk-core/tests/FusionRpg.E2E.Tests/**` among them, so the row cannot be started, let alone finished, here.
    2. **The premise is retired by RS2.4's shape.** The row exists so a `tools/` consumer can reach the
       helper (map module 6: "the module exists for `scenario-runner`'s in-process host"). The shipped
       runner takes an `HttpClient` and never opens a store — the in-process host is `RpgApiFactory`, in the
       E2E project, which already has the helper. So there is **no `gk-core/tools/RpgSim` consumer to serve today**,
       and the move's only remaining justification is a future one.
  - **What this lane did instead:** recorded the measurement above, and stated both facts in the plan's
    Wave-2 addendum (`tasks/rpg-simulator-plan.md` §9). **Not done, and not attempted** — no helper was moved
    and no compile link was touched. Evidence: `tasks/reports/rpg-sim-rs6.md`.
  - **Update 2026-09-23 (lane `sim-t3-2`): the map now records the retired premise, and this row needs ONE
    manager ruling to be closed or re-scoped.** Reason 2 above is now written into the map itself — module 6's
    Spec cell reads **"NOT WRITTEN, and the module's premise is retired: `gk-core/tools/RpgSim` stayed store-free
    (RS2.4), so no `tools/` consumer ever needed the substrate moved — RS-F6 is the surviving question"**
    (`docs/architecture/rpg-simulator-map.md`). With RS-F6 now decided the same way (the CLI is a
    real-process front end only), **no consumer of this module exists at all**, so the row's honest state is
    either *closed as superseded* (and module 6's row stays as the record) or *re-scoped to the future
    consumer that would justify it*. Reason 1 (314 files across five projects, four of them outside every
    `rpg-simulator` lane's fence) is unchanged and still means this row cannot be started from a delivery
    lane. **Blocker: a manager ruling on the premise; the fence is the second, independent blocker.**
  - **A THIRD INSTANCE of this row's shape, found 2026-09-23 (lane `sim-t3-2`): CS-F3.** The owner ruled that the
    species tree ships and the boot self-heals the roster (`f49cd83b4`, landed `4bbc9d082`), which retired the
    premise of `RpgSimProcessHostTests.A_server_that_cannot_boot…` and of five prose sites in this program's
    docs and help text — none of which moved with the ruling. It surfaced only because a test still asserted the
    old behaviour (`RpgSim` read 49/50). Fixed in this lane because the files are in its fence; the lesson is
    this row's: **a lane that changes a fact another assembly's tests depend on also moves those tests**, and
    `dotnet build` on the affected project is part of its own verification.
  - **Acceptance for a ruling:** either (a) the row is reassigned to `data-test-substrate` with a fence that
    covers the five csprojs (it is jointly owned already), or (b) it is deferred until a real `tools/`
    consumer needs the helper, and the plan says so — in which case the map's module-6 row is the artifact
    that changes, not this one.

### Wave 3 — the slow lane and the honesty guard

- [x] **RS2.5 — the real-process slow lane** · M · *approved E2 (a)* · module: **`process-host`**
  - Acceptance: a real `FusionRpg.Server.exe` boots as its own process with `FUSIONRPG_SIM=1`, its own
    `FUSIONRPG_DATA`, an ephemeral loopback port, real HTTP and SignalR transport; the runner refuses a
    target that does not report `simEnabled: true`; the process is stopped and its data dir removed on
    every exit path (a failed delete is a failure, not a swallowed catch).
  - Acceptance: the **same scenario file** is used; in-process vs real-process digest disagreement is
    **reported**, never smoothed.
  - Verify: `.\scripts\verify-change.ps1 -Paths gk-core/tools/RpgSim/**,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`
  - **Delivered 2026-09-23 (lane `sim-t3-1`).** `gk-core/tools/RpgSim/ProcessHost.cs` boots a real
    `FusionRpg.Server.exe` (own `FUSIONRPG_DATA`, free loopback port, `FUSIONRPG_SIM=1`,
    `FUSIONRPG_NO_BROWSER=1`, real HTTP + SignalR) and tears it down on every path — a process that will not
    stop and a directory that will not delete both **throw**. The CLI gained `--host process`
    (`--data-dir`, `--server-exe`), and the tool still opens no store: provisioning a world is the caller's
    step, because a fresh directory has no species roster and the real server refuses to boot on one.
  - **Measured:** the declared digest is identical on a fresh in-process host and a fresh real process
    (`daa9df408054f32e…`), while the whole-reading falsifier moves **109 named pointers** — RS-F4's two
    server-minted seeds, reported not smoothed. The refusal is proven against a real process booted without
    `FUSIONRPG_SIM` (`readings=0`, nothing ran).
  - **Two defects found and fixed in the same commit:** a relative `--server-exe` resolved against the
    child's working directory, and a relative `--data-dir` silently booted the server on a different nested
    directory while the caller's directory was deleted as if used. Both are absolute before the child starts.
  - **Evidence:** `tasks/reports/rpg-sim-rs25.md` — `RpgSim*` 46/46; the e2e boundary 270/270; the CLI
    process verdict `ok=True readings=7 digest=daa9df408054f32e…` with the data dir removed on exit.
  - **Not proved:** a seed seam for the 109 moved pointers (RS-F4); `--host inproc` from the CLI (RS-F6);
    the golden artifact (RS2.2 §5).
- [x] **RS4 — the honesty guard** · S · *approved D4 (b)* · module: **`honesty-guard`**
  - **Delivered 2026-09-23 (lane `sim-t3-2`).** `scripts/guard-sim-fabrication.ps1`, wired the way every
    other guard is: its own row in `gk-core/scripts/enforcement-registry.v1.json` (`tier: ci`, `status: gating`),
    its own invariant row (`pr-sim-honesty`), a `sim-fabrication-guard` verification boundary, and no
    `ci.yml` edit needed — `run-guards.ps1 -Tier ci` reads the registry. **Half A** (the corpus): every
    `read.*` names an FE-facing GET outside `/api/test`/`/api/sim` or a `/hub/*` message, with
    `/api/test/snapshot` refused **by name**; every call op is the closed table's own route, read from
    `gk-core/tools/RpgSim/ScenarioVocabulary.cs` so there is one copy of the table; every `expect`/`digest` names a
    `read.*` declared before it; every `test.*` step is on the guard's allowlist **and** named in the
    scenario's own `notes`. **Half B** (the shim): no `/api/sim` handler may take `RpgStore`, and every
    `/api/test` handler that does (measured: 12) carries an allowlist entry with a written reason — a
    **stale** entry is itself a violation.
  - **It bites, proven on planted violations** (`gk-core/tests/FusionRpg.Guard.Tests/SimFabricationGuardTests.cs`,
    `Passed: 4`): a planted fabricated read-back, a planted `/api/sim` handler taking the store, and a
    planted stale allowlist entry each return red with the expected message. The real corpus and the real
    server are green.
  - **Measured (this lane):** `/api/sim handlers=60 (take RpgStore: 0)` — 54 in `SimEndpoints.cs` +
    6 in `SimEffectEndpoints.cs`; the brief's 55 counted the `/api/sim` group only and is one off the
    code's 54 `sim.Map*` registrations. `/api/test handlers=13 (take RpgStore: 12, allowlisted: 12)`.
    The corpus: `scenarios=1 steps=36 reads=7 test.* steps=2`.
  - **Evidence:** `tasks/reports/rpg-sim-rs4.md` — `SimFabricationGuardTests` 4/4; registry + runner
    contracts 26/26; `run-guards.ps1 -Tier ci -Only sim-fabrication` exit 0.
  - **Not proved:** `-Session sim-t3-2` is unusable (`tasks/sessions/sim-t3-2.json` does not exist and
    `tasks/sessions/**` is outside the fence) — `-AllowUnscoped` was used, as `sim-t3-1` recorded; half A
    re-states the honesty rules rather than calling `ScenarioValidator`, sharing only the op table.
  - Acceptance, scenario half: every `read.*`/digest-bearing op in the shipped corpus names an
    FE-facing route or a hub message, never `/api/test/snapshot`; every `sim.*`/`api.*` op names a route
    that exists. Green on the corpus, **red on a planted fabricated read-back**.
  - Acceptance, shim half: every `/api/sim/*` handler reaches `RpgStore` only through `SimService`, with
    the reset route (`gk-core/src/FusionRpg.Server/SimEndpoints.cs:136`) and the **four** `seed-*-demo` writers
    (`:184`, `:218`, `:240`, `gk-core/src/FusionRpg.Server/SoulEndpoints.cs:29`) on an explicit allowlist with a
    written reason. Red on a planted direct-store handler.
  - Acceptance: a row in `gk-core/scripts/enforcement-registry.v1.json` with its `tier` and `status`.
  - Verify: `.\scripts\verify-change.ps1 -Paths scripts/guard-sim-fabrication.ps1,gk-core/scripts/enforcement-registry.v1.json,gk-core/tests/fixtures/rpg-scenarios/** -Session <id>`
  - **History:** this row was `BLOCKED` for lane `sim-t3-1` (denied path — the pipeline guard refused a
    new `scripts/guard-*.ps1`, so no part of it could land). This lane carries the `--allow-protected`
    grant for `scripts/guard-*.ps1`, which unblocked it and **RS-F10** (the clock guard) together.

### Wave 4 — the gate

- [ ] **RS7 — the CI lane** · S · *approved C3 (c)* · module: **`sim-ci-lane`**
  - Acceptance: the fast in-process scenarios run in CI **with their exit check**; the real-process
    scenarios get a scheduled or labelled lane running the tool that **claims no live game slot**; the
    runner stays a tool and only its pure parts are referenced by the suite.
  - Acceptance: the first CI run of the new step is green; `CiWiringGuardTests` completeness holds.
  - **RE-MEASURED 2026-09-23 (lane `sim-t3-2`) — the FIRST half is already met, the SECOND is met in
    substance but not literally, and the third is moot.** What the tree says:
    - **The fast in-process scenarios ARE in CI with their exit check.** `.github/workflows/ci.yml:333` runs
      `dotnet test gk-core/tests/FusionRpg.E2E.Tests/… -c Release` with `if ($LASTEXITCODE -ne 0) { throw … }`, and the
      in-process scenarios are tests in that project (`RpgScenarioSlice0E2ETests`, `RpgSimInProcHostTests`).
    - **The real-process scenarios run there too, unfiltered.** The same step passes no `--filter`, and
      `ci.yml:352-368` *asserts* that CI must stay the unfiltered full profile (only the BalanceGuard step is
      filtered), so the `DiskSemantics`-tagged `RpgSimProcessHostTests` run in CI — and a headless server
      process claims no game-pool slot by construction.
    - **The runner stays a tool.** `gk-core/tools/RpgSim/RpgSim.csproj` carries no `ProjectReference` and no
      `PackageReference`, and the E2E project references IT (the correct direction).
    - **The literal gap is one clause:** no CI step invokes the CLI itself
      (`dotnet run --project gk-core/tools/RpgSim -- --host process …`), so "a scheduled or labelled lane **running the
      tool**" is unmet; and with no new step, "the first CI run of the new step is green" has nothing to run.
  - **Ask for the manager (an erratum, not a lane's call):** either **(a)** the E2E project's unfiltered CI step
    IS the real-process lane — the tool is exercised through the E2E tests' own `ProcessHost` use, and RS-F6
    decided the CLI is a real-process *front end* whose `--host process` path is the same code the tests drive —
    or **(b)** the CLI itself must be invoked by a scheduled/labelled step, in which case this row waits on
    `.github/workflows/**` (outside this lane's paths) plus the `CiWiringGuardTests` row for that step.
    Recording the measurement here keeps a lane from re-landing the fast lane that already exists — the RS-F9
    lesson: a row's summary of what is wired is not evidence of what is wired.
  - **CONTRACT WRITTEN 2026-09-23 (lane `sim-t3-2`): `docs/architecture/rpg-simulator-spec-sim-ci-lane.md`**
    (map module row 9, whose Spec cell is no longer `NOT WRITTEN`). It records the two lanes as *negative*
    contracts — the E2E step stays unfiltered and a new scenario lands in that project — what "claims no live
    game slot" means mechanically (a headless server process; the game, the injector and the game pool are never
    touched, and the three-slot live-probe protocol does not apply because the game is closed), and the fact
    that made shape (b) cheap: since CS-F3 a fresh data dir self-heals, so the lane needs **no provisioning
    step**. It also names what the wiring must keep true, including the one hole a shape-(b) choice would open:
    `CiWiringGuardTests` walks `tests/**/*.Tests.csproj` only, so **nothing fails today if a tool step is
    deleted** — that assertion would land in the protected Guard.Tests tree.
  - **What still blocks this row:** the erratum above. Shape (a) needs no work at all; shape (b) needs a
    `.github/workflows/**` edit plus a wiring assertion, both outside this lane's paths. The spec is the part
    this lane can deliver, and it is delivered.
  - Verify: `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,<any new test project or registry entry> -Session <id>`

### Wave 5 — the clock (gated)

- [x] **RS3 — full `TimeProvider` migration, then retire `ForceExpeditionDue`** · L · *approved B1 (a), B3 (a); B2 (b) makes it product surface* · module: **`clock-seam`**
  - **Gates before any code:** (i) the `decisions.md` row — present (`docs/architecture/decisions.md:174`);
    (ii) `spec-clock-seam.md` names the seam's **product shape**, agreed with the module that consumes
    it, `world-continuity`'s `hibernation-clock` (`docs/architecture/world-continuity-map.md:118`).
    Until both hold this row waits on an external agreement — not on its own work.
  - **Gate (ii) met 2026-09-23 (lane `sim-t3-1`):** `docs/architecture/rpg-simulator-spec-clock-seam.md`
    is written and the map's clock row is repointed at it (the promised
    `docs/architecture/rpg-simulator/spec-clock-seam.md` tree is outside a file-prefix fence — RS-F5).
    The spec names the product shape (one injected `TimeProvider`, one signed offset
    `FUSIONRPG_CLOCK_OFFSET`, reported by `/health`, **never** a route), the boundary with
    `hibernation-clock` (pending turns are a turn-counter subtraction, never a wall-clock difference),
    this lane's own binary-safe count (**213 occurrences**: Data 142 · Server 41 · Injector 19 ·
    Core 8 · Launcher 2 · CheatCore 1; `TimeProvider` appears 0 times in `src/`) against the row's 203
    call sites, the migration order, and the **9 exclusions each with a written reason**.
  - **The trap is sharper than this row records:** `RpgStore.cs:1206-1210`'s 5-second heartbeat
    freshness window feeds `LiveInjector`, which is the property the sim runner's D1 (b) refusal reads —
    shift the clock forward and a *live* injector looks stale, so the refusal silently stops firing and
    a scenario could run against a player's install; shift it backward and a dead injector looks alive.
    That is why the window is an exclusion, not a migration.
  - **Ask to `world-continuity` (open, not blocking increment 1):** confirm `hibernation-clock` reads the
    wall clock only where a *duration* is pro-rated (idle window, yield accrual, freshness) and never
    for pending turns, and that those reads go through `ServerClock`. The `idle-world` and
    `background-yield` increments wait on that answer.
  - **ANSWERED 2026-09-23 (lane `sim-t3-2`), from their spec and this lane's guard — the ask is closed and its
    residue is RS-F26.** The module is **not built**: its own spec's summary puts *"save counter, clock mark,
    pending"* under **Real gap** and `catch_up_cap`/`turn_period_seconds` under **Wiring gap — never read**
    (`docs/architecture/world-continuity/spec-hibernation-clock.md`), and the code agrees —
    `grep -rn "GetPendingTurns\|clock_mark\|end_turns" src/ --include=*.cs` returns nothing, while
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:27-28` declares the two columns with no reader. So
    (1) **pending turns are confirmed clock-free by the spec** (`§3`'s pure
    `Pending(saveEndTurns, clockMark, catchUpCapTurns)`, `§6`'s *"`Pending` is pure and reads no clock"*) and
    there is no wall-clock read to confirm *in code*, because the code is a declared gap — the constraint is
    re-armed for when it lands; and (2) **duration pro-rating is already forced through the seam**: the idle
    window / yield accrual / freshness belong to `idle-world` / `background-yield` (their §2 non-goal), those
    are specs whose code has not landed either, and `gk-core/scripts/guard-clock-seam.py` fails CI on any new ambient
    read — so the answer is a mechanism, not a promise. **Consequence:** `idle-world` and `background-yield`
    are no longer waiting on an agreement; they are waiting on their own code.
  - **Fence:** `gk-core/src/FusionRpg.Data/**` (142 sites, incl. `ForceExpeditionDue`),
    `gk-fusion/src/FusionRpg.Injector/**` (19), `gk-fusion/src/FusionRpg.Launcher/**` (2) and `gk-core/src/FusionRpg.CheatCore/**` (1)
    are outside this lane's paths — filed as **RS-F9**. The increments this lane can land are 1
    (`FusionRpg.Core`, 8 sites) and 2 (`FusionRpg.Server`, 41) — **and both now wait on RS-F13's erratum**
    (see below). The clock guard's own home (`gk-core/scripts/guard-clock-seam.py`) is pipeline-blocked —
    filed as **RS-F10**.
  - **ERRATUM FOUND WHILE IMPLEMENTING (2026-09-23) — `TimeProvider` is not in this Core.**
    `FusionRpg.Core` and `FusionRpg.Contracts` target `net6.0`
    (`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:3`); `FusionRpg.Data`/`FusionRpg.Server` target `net8.0`.
    `System.TimeProvider` is .NET 8+, so B1 (a)'s mechanism cannot be the *stored* type in the assembly
    142 of the 213 sites compile against (Core stays `net6.0` because the Injector is a Unity `net6.0`
    host). Two shapes can be executed and the choice is a ruling: **A** multi-target Core
    (`net6.0;net8.0`) with the `TimeProvider` behind `#if` and a `Func<DateTimeOffset>` fallback, or **B**
    one `net6.0`-safe seam (a configured `Func<DateTimeOffset>`) with a `TimeProvider` *overload* on
    `net8.0`. Filed as **RS-F13**. Increments 1 and 2 do not start until it is ruled; the *product shape*
    is independent of the answer and is settled by the spec.
  - **Second erratum (measured):** `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs` bans the
    clock/RNG symbols in `gk-core/src/FusionRpg.Core/{World,Battle,Effects}` **by symbol** (one named exemption,
    `SystemEffectClock`). A new seam name is invisible to it, so `ServerClock` must not land in Core
    before `BannedSymbols` gains it — otherwise a `Core/Effects` wall-clock read slips past the gate that
    exists to catch exactly that. Filed as **RS-F12**.
  - **Increment 1 delivered 2026-09-23 (lane `sim-t3-2`) — the seam + the Core sites.**
    `gk-core/src/FusionRpg.Core/Time/ServerClock.cs` (new) is shape B (§0.1): one configured
    `Func<DateTimeOffset>`, `UtcNow` (DateTimeOffset) and `UtcNowDateTime` (DateTime, `...Z` round-trip
    preserved) over that one read, `OffsetSeconds` for the host to report, `Reset()` for teardown. The two
    real Core sites migrated: `SimEngine.cs:833` (the event envelope's `T` stamp) and
    `Diagnostics/PerfProbe.cs:256` (the perf window's `t` stamp — a stamp, not an elapsed measurement, so
    §7 does not exclude it). `EffectModels.cs:81`'s `SystemEffectClock` is untouched: it is the purity
    scan's one named exemption, the injector's live effect-runtime wall clock. Tests:
    `gk-core/tests/FusionRpg.Core.EffectClock.Tests/Time/ServerClockTests.cs` (4/4), including the one that proves
    shape B's load-bearing claim — a net8.0 `TimeProvider` is adapted *into* the seam
    (`Configure(provider.GetUtcNow)`) and is never a stored type. New focused boundary `core-server-clock`
    (`gk-core/src/FusionRpg.Core/Time/**`), so a seam change no longer plans the whole-core fallback.
    **RS-F13 ruled (shape B) and RS-F12 half-closed by substitute in this same commit** (see those rows).
    **Measured:** the ambient-read scan counts **214** occurrences in `src/`, not the spec's 213 —
    `FusionRpg.Launcher` has 3 (`DateTime.UtcNow` ×2 + `DateTime.Now` ×1), where the spec's table says
    `2 (+1 DateTime.Now)` and totals 2. Reported, not smoothed.
  - **Increment 2 delivered 2026-09-23 (lane `sim-t3-2`) — the Server sites + the composition root.**
    12 Server files migrated (33 real sites; `DebugEndpoints.cs`'s 6 deadline/freshness reads and
    `WebMatchService.cs:451`'s ingest `t0` stay raw per spec §7). `Program.cs` now reads
    `FUSIONRPG_CLOCK_OFFSET` **once**, before `builder.Build()`, and adapts `TimeProvider.System` into
    the seam (`ServerClock.Configure(timeProvider.GetUtcNow, offset)`) — the net8.0 *input* form of
    shape B, reached by the real host. A malformed offset **throws** rather than being ignored. The
    offset is deliberately **not** settable by a route. Evidence: `tasks/reports/rpg-sim-rs3.md`
    (increment 2) — `FusionRpg.Server.Tests` **819/819**, `guard-dal` OK, `dotnet build` 0 errors.
    **Still owed:** the `/health` clock declaration — `HealthDto` (`gk-core/src/FusionRpg.Contracts/Dtos.cs:43`)
    and `RpgStore.ToHealth` are outside this lane's paths (RS-F11).
  - **Increment 3 delivered 2026-09-23 (lane `sim-t3-2`) — the Data sites.** 48 Data files migrated,
    140 real sites (the 142 occurrences include 2 prose lines). Only the heartbeat pair stays raw
    (`RpgStore.cs:1208` the 5-second freshness read, `:1216` the write it compares against) — spec §7's
    trap: shifting the clock makes a *live* injector look stale and silently stops the sim runner's
    D1 (b) refusal, which is the property that keeps a scenario off a player's install. **Measured:**
    `FusionRpg.Data.Tests` **1856/1857** (10 m 20 s); the single red is
    `EmpireLevelTests.A_pass_that_throws_leaves_no_empire_row_and_the_next_start_completes_it`, the
    **documented pre-existing global-`ProgressionTuningHub` race** (`tasks/empire-progression-todo.md:1272`,
    finding **F2**), which passes in isolation in 248 ms and is untouched by this migration. Evidence:
    `tasks/reports/rpg-sim-rs3.md` (increment 3).
  - **Increment 4 delivered 2026-09-23 (lane `sim-t3-2`) — Injector, Launcher, CheatCore.** 7 Injector
    files touched, **11 of its 17 code reads migrated**; the probe-timeout window's read+write pair, the
    overlay wait deadline, and `EffectRuntime`'s effect-clock seed stay raw (the last one **reverted** after
    it broke `PlayerSpeciesMaterialiseCallerGuardTests`, which asserts that exact literal — a protected guard
    test, and spec §7 says increment 4 *may* source it, never that it must). **CheatCore now has ZERO
    ambient reads**: `guard-repo-boundary` B1 pins it to `FusionRpg.Contracts` alone, so
    `CheatDocumentCodec.FromEntries` **requires** its `updatedAt` argument and its only production caller
    (`RpgStore.cs:2589`, which has the seam) supplies it — no new dependency, no exclusion. **The Launcher's
    one site is an exclusion** (it references no FusionRpg project at all): filed as **RS-F14**. Evidence:
    `tasks/reports/rpg-sim-rs3.md` (increment 4) — `CheatCore.Tests` 41/41, `Launcher.Tests` 165/165,
    Data/CheatCore/Launcher builds 0 errors, `guard-repo-boundary` / `guard-secondary-no-unity` OK, and the
    Guard suite's `PlayerSpeciesMaterialiseCallerGuardTests` 5/5 after the revert. **The Injector build could
    NOT run** locally (no game interop; `guard-injector-compile.ps1` SKIPs by design) — the migration there is
    type-preserving and unverified, and that is stated rather than implied.
  - **Increment 5 delivered 2026-09-23 (lane `sim-t3-2`) — PARTIAL, and the gap is measured.** The
    **clock guard landed**: `gk-core/scripts/guard-clock-seam.py` (RS-F10 resolved), two rules, its registry row
    (`clock-seam`, `ci`/`gating`), invariant row (`pr-clock-seam`) and `clock-seam-guard` boundary. Its
    reading on the finished tree is the migration's own completion contract: **1478 source files, 20
    ambient reads — 2 inside `ServerClock.cs`, 19 allowlisted with a reason each; 0 simulation-tree
    `ServerClock` references.** Bite proof: a planted `-SrcDir` fixture returns exit 1 naming both planted
    violations. **The `ForceExpeditionDue` retirement did NOT land**, and the reason is a measurement, not
    a fence: a single static clock offset cannot make an expedition due, because dispatch and collect read
    the SAME seam (`due = now + duration`, then `now < due`), and a mid-run clock movement is unreachable —
    the runner is HTTP-only and a clock-setting route is refused (spec §2, D3 (b)). Recorded as spec **§6a**
    and filed as **RS-F16**, with the two candidate fixes named. The corpus keeps its documented SIM rewind
    until then, and its note says exactly what the bypass is. **So RS3 is NOT closed**: its retirement
    acceptance is unmet, and this lane will not tick it.
  - **DELIVERED 2026-09-23 (lane `sim-t3-2`), in six commits.** Increment 1 (`ServerClock`, shape B, + the
    Core sites), 2 (the Server sites + the composition root), 3 (the Data sites), 4 (Injector/Launcher/
    CheatCore), 5a (a declared `offset` is honest for both hosts at boot), 5b (the mid-run `clock.set` input,
    which retires `ForceExpeditionDue`). Plus `gk-core/scripts/guard-clock-seam.py` (RS-F10 resolved) and the RS-F12
    hole closed as its rule 2. Evidence: `tasks/reports/rpg-sim-rs3.md`, with a printed reading per increment.
  - **TWO VERIFICATION GAPS, named rather than smoothed** (this row is ticked on its deliverables, and these
    are what a re-run should close):
    1. **The row's close gate did not produce a reading.** `pwsh -NoProfile -ExecutionPolicy Bypass -File
       scripts/test-fast.ps1 -AllDefault` was started and **killed by an infrastructure error**
       (`MSBUILD : error MSB4166: Child node "2"/"4" exited prematurely`, the harness tearing down the process
       tree) after the Server project had built. The per-module readings it would have contained exist
       separately: Server 830/830, Data 1856/1857 (the one red is the documented F2 global-hub race), E2E
       286/288 (both reds are RS-F21), CheatCore 41/41, Launcher 165/165, the six focused Core projects 68/68,
       RpgSim 48/48.
    2. **The Injector build could not run.** `guard-injector-compile.ps1` SKIPs without a game dir by design
       (`INJECTOR COMPILE GUARD SKIPPED — no MelonLoader game dir`), and the shim project reports the
       pre-existing `Ambiguous project name 'FusionRpg.Injector'` while the real host needs interop this
       machine does not have (1810 MSB3254 errors). The 11 Injector sites migrated are type-preserving and
       unverified; the guard must run where a game install exists.
  - Acceptance: the migration covers the surface the row measured (203 sites — 143 mechanical ISO
    emissions, 25 already injectable, 24 other, 2 date-shaped); the **9 deadline/wait sites are excluded
    with a written reason each**, including the trap at
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1207-1210` (shifting the clock makes a healthy server report
    itself disconnected).
  - Acceptance: `ForceExpeditionDue`'s `UPDATE`
    (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:202-215`) is retired and no store bypass
    replaces it; the verdict prints the clock declaration; a guard fails ambient `DateTime.UtcNow` in
    `src/` outside the one clock type.
  - Acceptance: this row crosses `FusionRpg.Data`, `FusionRpg.Server`, `FusionRpg.Core`,
    `FusionRpg.Injector`, `FusionRpg.Launcher` and `FusionRpg.CheatCore` together — a **broad** local
    suite is legitimate at its close, and the injector build is part of it.
  - Verify: `.\scripts\verify-change.ps1 -Paths <every migrated file> -Session <id>` per increment;
    `.\scripts\test-fast.ps1 -AllDefault` at the row's close.
    - **CLOSED 2026-09-23 by measurement (manager).** Every increment in the spec's §6 table is `done`, each its own commit with its own evidence (`tasks/reports/rpg-sim-rs3.md`, 27 KB, per-increment criterion/command/result/artifact tables): 1 `ServerClock` + the Core sites, 2 Server (33 real; `Program.cs` reads `FUSIONRPG_CLOCK_OFFSET` once and adapts `TimeProvider.System` into the seam), 3 Data (140 real; `FusionRpg.Data.Tests` **1856/1857** with the one red a documented pre-existing global-hub race), 4 Injector/Launcher/CheatCore (CheatCore's read retired), **5a** the boot-time offset honest for both hosts, **5b** the mid-run clock input.
    - **The bypass is RETIRED, not disabled -- measured:** `grep -rn ForceExpeditionDue src/ scripts/ tools/` matches **only stale build artifacts** (`bin/**`, `artifacts/**` DLLs); no source reference survives, and the store method plus its route are deleted. `gk-core/scripts/guard-clock-seam.py` prints **CLOCK SEAM GUARD OK** (1514 source files, 21 ambient reads = 2 clock-type + 19 allowlisted entries) and holds its own row in `gk-core/scripts/enforcement-registry.v1.json`.
    - **Owner rulings respected:** B1 (a)'s mechanism is shape **B** (spec §0.1, RS-F13's erratum -- its *intent*, one injectable clock read, is what landed; shape A remains the owner-overridable alternative), B3 (a)'s retirement is done, and **RS-F16's owner ruling** (plumb the offset at boot, *then* add the mid-run input) is exactly the 5a -> 5b order.
    - **Deviations the lane recorded rather than smoothed:** RS-F12's `BannedSymbols` edit was refused (`gk-core/tests/FusionRpg.Guard.Tests/**` is pipeline-protected), so the rule ships as rule 2 of the clock guard and the C# line is owed to the `guard` program; the ambient scan counts **214** in `src/` where the spec's table totals 213 (Launcher carries 3, not 2 -- a measurement, not a defect).
    - **Still open, and NOT part of this row's acceptance:** **RS6** (`DataTestStore` needs a shared non-test home) and **RS7** (the CI lane) keep their own rows for the convergence count.

## Checkpoints

- **S1** (after RS1) — the four-family chain is green locally, souls earned through the real earn path,
  the roster-derived squad asserted.
- **S2** (after RS2.1–RS2.4, RS6) — one file, one host, a readable verdict, a stable digest, the
  substrate reachable from a tool.
- **S3** (after RS2.5, RS4) — the same file on both hosts, and honesty is mechanical.
- **S4** (after RS7) — the shape survives a push.
- **S5** (after RS3) — time is honest, the bypass is gone, the exclusions are written. **MET 2026-09-23 (lane
  `sim-t3-2`):** the seam is product surface, 186 of the measured sites are migrated and the guard's own
  reading is `1494 source files / 21 ambient reads (2 inside the clock type + 19 allowlisted) / 0
  simulation-tree ServerClock references`, `ForceExpeditionDue`'s `UPDATE` and its route are deleted with no
  store bypass replacing them, and each exclusion carries its reason in the guard. **Two verification gaps,
  named rather than smoothed:** the row's close gate `test-fast.ps1 -AllDefault` was started and killed by an
  infrastructure error (no reading — the per-module readings are in `tasks/reports/rpg-sim-rs3.md`), and the
  Injector's 11 migrated sites are type-preserving but **not compile-verified** on this machine
  (`guard-injector-compile.ps1` SKIPs with no game dir, by design).

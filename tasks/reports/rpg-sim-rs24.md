# Evidence — rpg-simulator RS2.4 (the default in-process host)

Lane `sim-runner`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-runner`
(branch `cmdc/sim-runner`). Module `inproc-host`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The same scenario file runs in-process on `WebApplicationFactory<Program>` with its own data source, reusing `RpgApiFactory` | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --logger "console;verbosity=detailed" --filter FullyQualifiedName~RpgSimInProcHostTests` | pass: 2 runs on 2 fresh `RpgApiFactory` hosts, `ok=True readings=7 captures=5` each | `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs` |
| "Settled" is defined by polling, not assumed | same run + `A_host_that_cannot_settle_is_a_failure_not_a_verdict` + `A_host_that_dropped_ingest_events_is_refused_immediately` | settle `polls=2 107ms` / `polls=2 106ms`; a stub that never goes quiet is **not settled** (`did not settle within 0.4s`, ≥2 polls); a dropped-event host is refused immediately with `dropped 3 event(s)` | `gk-core/tools/RpgSim/SimSettler.cs`, `ScenarioVerdict.Settle` + `Validate()` |
| The digest is identical across two consecutive runs on a fresh data source | same run | `daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e` both runs (declared digest) | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` (`digest.include`) |
| The falsifier reports rather than smooths | same run, `whole-reading comparison: …` | **MOVED** — 110 named pointers in one measurement, 71 in another (the count itself varies); every pointer named with both values | `ReadingDigest.CompareVerdicts` |
| What moved is named, and the list is extended by measurement | read the report | roster roll (`profile.speciesId` `tanglekelp → projectilezombie`, `profile.rarity`, `profile.elementPrimary`, `actor.typeId`, `actor.side`), `squadInstanceIds` (fresh GUIDs), ledger `activityFactId: 7 → 8` → **added to `Baseline` with its reason**; ledger `t` (`21:23:12Z → 21:23:34Z`) → **not** added, filed as **RS-F7** | `gk-core/tools/RpgSim/ReadingDigest.cs`, `readback-verdict.md` §3 |
| Runner + contract + host tests | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter FullyQualifiedName~RpgSim` | `Failed: 0, Passed: 43, Skipped: 0, Total: 43` (1 m 12 s) | — |
| Whole E2E boundary | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Failed: 0, Passed: 277, Skipped: 0, Total: 277` (2 m 28 s) | — |

**NOT proved.**

- **The RNG divergence is not fixed** — it is measured and filed (**RS-F4**): the summon route
  (`gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:96`) and expedition dispatch
  (`gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:36`) mint their own seeds, so no scenario can make the
  roster or the battles repeat. The declared digest is therefore deliberately scoped to host-stable
  readings (a terminal state, a tier, a row id, the run engine); the outcome-dependent readings are
  asserted by closed-vocabulary `expect.*` rules instead. A seed seam is the fix, and it is
  product-shaped work that needs its own spec.
- **The real-process host and the cross-host comparison** (RS2.5). `ReadingDigest.CompareVerdicts` is the
  call it will use; nothing cross-host was executed here.
- **`--host inproc` from the CLI** (**RS-F6**) — the host is supplied by the embedding test host.
- **`t` is not excludable by name** (**RS-F7**); the shipped scenario does not digest the ledger, so no
  artifact is dishonest today.
- **`gk-core/tools/RpgSim/**` has no verification boundary** (**RS-F3**), so the evidence above is direct
  `dotnet test` output rather than `verify-change.ps1`.
- **No disk is written** by these tests beyond build output: the E2E host is on the memory plan
  (TARGET 0), and a fresh host means a fresh shared-memory data source whose cleanup is the keeper's
  disposal — there is no directory to leak.

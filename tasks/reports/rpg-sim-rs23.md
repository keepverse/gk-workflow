# Evidence — rpg-simulator RS2.3 (`gk-core/tools/RpgSim`, the runner)

Lane `sim-runner`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-runner`
(branch `cmdc/sim-runner`). Module `scenario-runner`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Reads a scenario, owns the seed, one sequential client, writes the verdict JSON | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter FullyQualifiedName~RpgScenarioSlice0` | pass: `readings=7 captures=5 digest=daa9df408054f32e…` from the real in-process server | `gk-core/tools/RpgSim/ScenarioRunner.cs`, `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` |
| Refuses unless the target reports `simEnabled: true` | `--filter FullyQualifiedName~A_target_that_does_not_report_sim_enabled` | pass (real `Program` with `FUSIONRPG_SIM` unset): `refused:true`, one named failure, no steps, no readings | `RpgSimRunnerTests.cs` |
| Refuses while a live injector is connected (D1 (b)) | `--filter FullyQualifiedName~A_target_with_a_live_injector` | pass: real `/api/heartbeat {"source":"injector"}` → `/health` reports `injectorConnected:true` → refused | `RpgSimRunnerTests.cs` |
| Hub read refused by name, not silently skipped | `--filter FullyQualifiedName~A_hub_read_is_refused` | pass: `hub reads need the SignalR client` | `RpgSimRunnerTests.cs` |
| Non-2xx carries the route and the status | `--filter FullyQualifiedName~A_call_that_answers` | pass: `GET /api/souls/999999 -> 404` | `RpgSimRunnerTests.cs` |
| No domain math | read `ScenarioRunner.cs` + `ScenarioExpectations.cs` against the op table | every call is a declared route; the only synthesized value is `sim-{seed}-{index}` (correlation id); the 11 checks are comparisons | `gk-core/tools/RpgSim/` |
| The corpus validates and runs under the contract | `dotnet run --project gk-core/tools/RpgSim -- --scenario gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json --validate` | exit 0: `{"steps":36,"calls":6,"reads":7,"expects":22,"digests":1}` | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` |
| CLI refuses a dead target and still writes the artifact | `--run --base-url http://127.0.0.1:1/ --out /tmp/verdict-refusal.json` | exit 3; console `REFUSED — … did not answer GET /health`; file has `"refused": true` + the reason | `RpgSimCli.cs` |
| CLI refuses `--host inproc` by name | `--run --host inproc --base-url http://127.0.0.1:1/` | exit 2, names the gap and **RS-F6** | `RpgSimCli.cs` |
| Runner + contract tests | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~RpgSim\|FullyQualifiedName~RpgScenarioSlice0"` | `Failed: 0, Passed: 40, Skipped: 0, Total: 40` (1 m 3 s) | — |
| Whole E2E boundary | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Failed: 0, Passed: 273, Skipped: 0, Total: 273` (2 m 4 s; no RS-CF2 flake this run) | — |

**NOT proved.**

- **The CLI's `--run` transport against a LIVE server.** No server was started (the lane rule: no
  leftover processes), so `--run` is proven for argument handling, the gate refusal and the artifact
  write, and the *runner* is proven in-process. The real-process lane is RS2.5.
- **`--double-run` against one target** is implemented but not measured here — two runs on one server
  legitimately see new row ids, so the falsifier is measured on fresh hosts in RS2.4.
- **Hub reads** (a `/hub/*` read-back) are in the format but have no client in this wave; the runner
  refuses them by name.
- **No golden artifact is written** — `--golden` is specified in `readback-verdict.md` §5 and RS2.4's
  fresh-host comparison is what makes one meaningful.
- **`gk-core/tools/RpgSim/**` has no verification boundary** (**RS-F3**): `scripts/**` is outside the fence, so
  the evidence above is direct `dotnet test`/`dotnet run` output rather than `verify-change.ps1`.
- **No disk was written by these tests** beyond the build output — the E2E host is on the memory plan
  (TARGET 0). Nothing new writes to `%TEMP%`; the CLI refusal wrote only the `--out` file it was asked for.

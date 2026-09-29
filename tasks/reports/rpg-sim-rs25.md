# Evidence — rpg-simulator RS2.5 (the real-process slow lane) + RS-F3 (the tool's verification boundary)

Lane `sim-t3-1`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-1`
(branch `cmdc/sim-t3-1`). Module `process-host`; carried row `RS-F3`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A real `FusionRpg.Server.exe` boots as its own process: `FUSIONRPG_SIM=1`, own `FUSIONRPG_DATA`, free loopback port, real HTTP **and SignalR** | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo --filter "FullyQualifiedName~RpgSimProcessHostTests" --logger "console;verbosity=detailed"` | `Passed: 3, Failed: 0, Total: 3` (58 s); `signalr: connected to http://127.0.0.1:62842/hub/rpg`; `booted FusionRpg.Server.exe pid=58876` | `gk-core/tools/RpgSim/ProcessHost.cs`, `gk-core/tests/FusionRpg.E2E.Tests/RpgSimProcessHostTests.cs` |
| The runner refuses a target that does not report `simEnabled:true` — proven on a REAL process booted without the flag | same run, `The_runner_refuses_a_real_process_that_does_not_report_sim_enabled` | `refused: the target http://127.0.0.1:63269/ reports simEnabled:false — that is a player install, not a sim server`; `readings=0` (nothing ran) | same |
| The process is stopped and its data dir removed on **every** exit path | same run — happy path asserts pid gone + dir gone; `A_server_that_cannot_boot…` asserts the dir is gone after a boot failure | pid gone, dir gone; a failed boot reports the server's own reason (`CreatureSpeciesCatalog.Configure received an empty species roster`, exit `-532462766`) and still removes the dir | `ProcessHost.DisposeAsync`, `LogTail` |
| The **same scenario file** on both hosts, digest compared and any disagreement **reported** | same run, `The_same_scenario_file_runs_on_the_real_process_and_in_process…` | declared digest identical: `daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e` (both hosts); whole-reading comparison **MOVED 109 named pointers** — the two server-minted RNG seeds of **RS-F4**, reported not smoothed | `ReadingDigest.CompareVerdicts` |
| The CLI drives the real-process lane itself (`--host process`) | `dotnet run --project gk-core/tools/RpgSim -c Release -- --scenario gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json --run --host process --data-dir <dir> --server-exe tests/FusionRpg.E2E.Tests/bin/Release/net8.0/FusionRpg.Server.exe --out …/cli-process-verdict.json` | exit 0; `booted … pid=55228 at http://127.0.0.1:63870 (simEnabled=True)`; verdict `ok=True host=process:… readings=7 captures=5 digest=daa9df408054f32e…`; data dir removed on exit | `gk-core/tools/RpgSim/RpgSimCli.cs` |
| Runner + contract + both hosts | `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --no-build --nologo --filter "FullyQualifiedName~RpgSim"` | `Failed: 0, Passed: 46, Skipped: 0, Total: 46` (9 m 45 s) | — |
| **RS-F3**: `gk-core/tools/RpgSim/**` resolves a verification owner instead of throwing | `verify-change.ps1 -Paths gk-core/tools/RpgSim/ScenarioFormat.cs -AllowUnscoped -PlanOnly` | `gk-core/tools/RpgSim/ScenarioFormat.cs -> rpgsim-tool (module)` + `guard: test-substrate` + `test: e2e` | `gk-core/scripts/verification-boundaries.v1.json` |
| The path-owned boundary, all changed paths | `verify-change.ps1 -Paths <the 7 changed paths> -AllowUnscoped` | e2e boundary `Failed: 0, Passed: 270, Total: 270` (2 m 48 s); `TEST SUBSTRATE GUARD OK`; `VERIFICATION BOUNDARY GUARD OK` (27 s) | — |

**Two defects found and fixed while building this row** (`ProcessHost.cs`): a relative `--server-exe`
resolved against the child's working directory (start failure), and a relative `--data-dir` made the server
create a *different* nested directory and die on the empty roster while the caller's directory was deleted as
if it had been used. Both are now made absolute before the child starts.

**NOT proved / deviations.**

- **`-Session sim-t3-1` could not be used.** `tasks/sessions/sim-t3-1.json` does not exist and
  `tasks/sessions/**` is outside this lane's allowed paths, so the brief's exact form throws
  `session record not found`. `-AllowUnscoped` was used for every `verify-change.ps1` call above.
- **One Guard-suite failure, exonerated:** `FusionRpg.Guard.Tests.VerificationBoundaryWorkflowTests.P6_the_real_registry_resolves_seedsmith_and_tuning`
  failed with `verification-boundary script timed out` inside the full Guard run, but passes in isolation in
  1 m 30 s against the 2-minute timeout, and the same guard standalone is 27 s. Contention flake, pre-existing;
  filed as **RS-F8** for the owning program.
- **The cross-host digest agreement is scoped to this scenario's declared readings.** The 109 moved pointers
  are RS-F4's two server-minted seeds; no seed seam exists, so the digest deliberately excludes them.
- **No golden artifact** (`readback-verdict.md` §5); RS2.5's acceptance does not ask for one.

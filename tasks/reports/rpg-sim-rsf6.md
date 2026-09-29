# Evidence — rpg-simulator RS-F6 (the CLI is a real-process front end, by decision)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS-F6, acceptance's first branch: *"a deliberate decision that the CLI is a
real-process front end only (and the map says so)."*

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The refusal is a named decision, not "not implemented" | `dotnet run --project gk-core/tools/RpgSim -c Release --no-build -- --scenario gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json --run --host inproc --base-url http://127.0.0.1:1` | exit **2**, and the message says `--host 'inproc' is refused by design. This CLI is a real-process front end only (RS-F6, docs/architecture/rpg-simulator-map.md module 4)` — naming both real transports | `gk-core/tools/RpgSim/RpgSimCli.cs` |
| The map says so, in the module row a reader reaches | read: map module 4 (`scenario-runner`) | "**It is a real-process front end only (RS-F6, decided 2026-09-23):** `--host process` or `--base-url`, never `--host inproc` … for no acceptance line the program has" | `docs/architecture/rpg-simulator-map.md` |
| The tool's own README says so | read: the `--host` table | the `inproc` row now reads "**refused by design, and that is the decision (RS-F6, closed 2026-09-23)**" with the reason | `gk-core/tools/RpgSim/README.md` |
| The tool stays dependency-free, which is the load-bearing fact | `grep -n "ProjectReference\|PackageReference" gk-core/tools/RpgSim/RpgSim.csproj` | **no matches** — no project reference and no package reference; it takes an `HttpClient` and owns the transport only | `gk-core/tools/RpgSim/RpgSim.csproj` |
| The tool still builds | `dotnet build gk-core/tools/RpgSim/RpgSim.csproj -c Release --nologo` | `Build succeeded. 0 Error(s)` | — |

**Why the second branch was not taken, stated rather than implied.** RS-F6's alternative is a `tools/`-reachable
in-process bootstrap (a `tools/RpgSim.Host` project, or a shared non-test home for the factory — RS6/F3's
territory, outside this lane's fence). It is not needed: no acceptance line requires the CLI to host in-process,
the fast lane is the E2E project (`RpgScenarioSlice0E2ETests`, `RpgSimInProcHostTests` — both boot
`RpgApiFactory` and drive this same file), and the slow lane is `--host process` or `--base-url`. Taking it
would also put the app assembly plus `Microsoft.AspNetCore.Mvc.Testing` inside a tool that today references
nothing, to run what the embedding host already runs.

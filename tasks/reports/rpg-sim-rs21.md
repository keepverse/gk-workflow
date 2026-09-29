# Evidence — rpg-simulator RS2.1 (the scenario contract)

Lane `sim-runner`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-runner`
(branch `cmdc/sim-runner`). Module `scenario-format`. Contract: `gk-core/tools/RpgSim/scenario-format.md`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Envelope + closed op vocabulary specified, ops named after the route they call | read `gk-core/tools/RpgSim/scenario-format.md` §2–§3 against `ScenarioVocabulary.cs` | 6 call ops in the closed table; `test.*` added to the plan's 4 prefixes (measurement in §3) | `gk-core/tools/RpgSim/{scenario-format.md,ScenarioVocabulary.cs}` |
| `read.*` must name an FE-facing route or a hub message | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter FullyQualifiedName~RpgSimFormatContractTests` | `Failed: 0, Passed: 20, Total: 20` (168 ms) | `gk-core/tests/FusionRpg.E2E.Tests/RpgSimFormatContractTests.cs` |
| Extend-vs-share decided with the expressibility test | same run, `The_effect_scenario_step_dto_cannot_express_the_rpg_step_and_drops_it_silently` + `..._carries_the_route_args_capture_and_why` | pass: the effect DTO has no `Route`/`Args`/`Capture`/`Why`, its `Expect` is `IntentPlanDto`, and the loss is SILENT | same file |
| Validator frames the CLI | `dotnet run --project gk-core/tools/RpgSim -- --scenario /tmp/scen-min.json --validate` | exit 0, `{"ok":true,...,"calls":1,"reads":1,"expects":1}` | `RpgSimCli.cs` |
| Validator refuses, by name | `... --scenario /tmp/scen-bad.json --validate` | exit 1, 3 refusals printed (`seed`, `clock`, `no read.* step`) | `RpgSimCli.cs` |
| Corpus home named; its verification boundary present | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK`, exit 0 | `gk-core/scripts/verification-boundaries.v1.json` (`e2e-scenario-fixtures`, `80f388db7`) |
| RS-F2 acceptance (carried finding, closed here) | same command | `VERIFICATION BOUNDARY GUARD OK` at a head carrying `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` | `tasks/rpg-simulator-todo.md` RS-F2 |
| Whole E2E boundary still green after the new ProjectReference | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Failed: 0, Passed: 254, Skipped: 0, Total: 254` (3 m 8 s) | — |

**NOT proved.**

- The shipped slice-0 fixture is still in RS1's original shape: it is migrated in RS2.3, in the commit
  that lands the runner reading the new shape. Until then the validator is exercised by its own tests
  and the CLI, never by the corpus (`scenario-format.md` §7).
- `gk-core/tools/RpgSim/**` has no verification boundary, so `verify-change.ps1 -Paths gk-core/tools/RpgSim/...` refuses
  (`VERIFICATION BOUNDARY MISSING`, `scripts/verify-change.ps1:114`). Filed as **RS-F3**; the tool's
  evidence here is the direct `dotnet test`/`dotnet run` commands above.
- No server was run, no scenario was executed, no verdict was produced — RS2.3/RS2.4 own those.
- The clock stays `ambient` and the validator refuses the other two modes by name; no clock seam exists
  (RS3 is gated).
- `docs/architecture/rpg-simulator/spec-scenario-format.md` (the map's promised path) was not written —
  outside this lane's fence. Filed as **RS-F5**.

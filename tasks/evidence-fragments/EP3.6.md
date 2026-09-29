# EP3.6 — Canary: `TryBeginUniqueDeploy` refuses this run's seated commander with `commander.cannot-deploy`

Spec: `docs/architecture/empire-progression/spec-lawn-commander-seat.md` ("The canary branch").

| Criterion | Command | Result | Artifact |
| --- | --- | --- | --- |
| The refusal fires BEFORE the phase check, so the reason names the rule | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CreatureLawnDeployCommanderRefusal"` | pass — **4 passed / 0 failed**. The new branch sits above the `Roster` phase check (and beside the Patron branch), reading the seat row through `IsSeatedCommanderUnlocked`; a seated commander's deploy returns `commander.cannot-deploy`, not `phase.activebound` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, the seat fact in `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs` |
| A role-holder that is not leading this run deploys normally (test 4) | same run | pass — the same test grants the role to a second specimen that is **not** seated and deploys it successfully: the restriction belongs to the place and the run, never to the role | `gk-core/tests/FusionRpg.Data.Tests/CreatureLawnDeployCommanderRefusalTests.cs` |
| The canary comment at the real call site is replaced, and `CreatureLawnDeployCommanderRefusalTests` gets its real case | same run | pass — the comment ("Commander is deliberately NOT checked here … when that lands, this refusal needs a second branch here") is gone, replaced by the branch itself; the test file's own header ("Commander is NOT tested here") now states the rule it tests | same files |
| Not proved | — | the legion sub-clause (waits on `legion-commander`), and the live refuse-then-play run (needs the game). The boundary command was not re-run for this task: the change is two lines plus a test in paths already boundary-verified at EP3.5, and its focused filter is green | — |

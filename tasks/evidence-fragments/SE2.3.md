# SE2.3 — Extend `guard-test-substrate` to swallowed `File.Delete`

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| An empty/comment-only catch around `File.Delete` fails the guard | `Find-SwallowedDelete`'s regex `Directory\.Delete` -> `(?:Directory\|File)\.Delete` | scan of the real tree found 5 pre-existing hits (`WorldGraphWriteBench.cs`, `CombatSimJsonEmitTests.cs`, `ProveAptitudeJsonEmitTests.cs`, `CreatureSpeciesGenExplainTests.cs`, `ClassSystemPhase9ReadinessGateTests.cs`) | gk-core/scripts/guard-test-substrate.py |
| Any other hits fixed in the same commit (green-first) | `powershell gk-core/scripts/guard-test-substrate.py` | all 5 confirmed genuine `Path.GetTempPath()` scratch (never tracked content), swallow removed -> plain `File.Delete(...)`; guard now `TEST SUBSTRATE GUARD OK` | the 5 files above |
| Falsifier | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TestSubstrateGuardTests"` | **5/5 pass**, incl. new `Guard_fails_on_a_planted_swallowed_File_Delete` | gk-core/tests/FusionRpg.Guard.Tests/TestSubstrateGuardTests.cs |
| Fixed sites still pass | `dotnet test` on each affected project | Core.Tests 9/9, Guard.Tests (Phase9) 4/4, `FusionRpg.Bench` builds clean | — |
| Task-boundary check | `run-guards.ps1 -Tier ci` | **15/15 gating guards, 0 red** | — |

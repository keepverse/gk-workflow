# TVB1.6 — `gk-core/tools/TestSplitAnalyzer` skeleton: csproj reader + test project + wiring (E3)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `TestSplitAnalyzer` Exe with `CsprojReader` (Compile/Link, ProjectReference, None) | `dotnet test tests\FusionRpg.TestSplitAnalyzer.Tests -c Release` | 5/5 passed (incl. A8) | `CsprojReader.cs`, `CsprojReaderTests.cs` |
| Exit 2 with a message when build output is absent | `dotnet run --project tools\TestSplitAnalyzer -- --project tests\FusionRpg.FileMove.Tests\FusionRpg.FileMove.Tests.csproj --configuration NoSuchConfig` | exit 2, named message | console |
| Happy path (real build output) | `dotnet run --project tools\TestSplitAnalyzer -- --project tools\TestSplitAnalyzer\TestSplitAnalyzer.csproj --configuration Release` | exit 0, prints counts | console |
| Registry: `testsplitanalyzer` project id + `testsplitanalyzer-fallback` owner boundary (tool+tests, filemove's shape) | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | `gk-core/scripts/verification-boundaries.v1.json` |
| `ci.yml` E3 pair, same commit, after the FileMove pair, not in `release.yml` | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~CiWiringGuardTests\|FullyQualifiedName~WorkflowExitCheckTests"` | 9/9 passed | `.github/workflows/ci.yml` |
| Roslyn (`Microsoft.CodeAnalysis.CSharp` 4.14.0) referenced by the analyzer tool project only | inspect `TestSplitAnalyzer.csproj` | approved R26; no other project references it | csproj |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/*,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/*,gk-core/scripts/verification-boundaries.v1.json,.github/workflows/ci.yml -Session summoner-convergence-lane-d2-20260919` | `guard.verification-boundaries` 16/16; `guard.workflows` 10/10; `testsplitanalyzer` 5/5 | plan resolved all four boundaries |

FileMove's own boundary does not exist yet (`registry-contract` TVB2.1-2.7, wave 2, not landed) —
"filemove's shape" is the intended shape from that spec, applied here ahead of it since this task
runs in the independent wave-1b track.

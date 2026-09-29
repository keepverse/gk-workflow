# TVB1.8 — String-keyed and location-sensitive findings (`BLOCKS SPLIT`)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Literal hits for `fixtures/`, `Goldens/`, tool assembly names -> content requirement | `dotnet test tests\FusionRpg.TestSplitAnalyzer.Tests -c Release` | 27/27 (was 18; +9 this task) | `Findings.cs`, `FindingsTests.cs` |
| A5 (content requirement) | `A5_a_fixtures_literal_is_a_content_requirement` + Goldens/tool-name variants | passed | same |
| Own-path literal crossing candidates -> `BLOCKS SPLIT` | A9 | `OwnPathRequirement.BlocksSplit` true only when the literal's target candidate differs from the one holding it; false for a same-candidate own-path literal | same |
| `[CallerFilePath]` users listed | A10 | passed (syntactic attribute match, no semantic binding required) | same |
| Namespace-vs-folder mismatches | A11 | `FusionRpg.Core.Tests.B` declared in `B/C/File.cs` reports implied `FusionRpg.Core.Tests.B.C`; a matching namespace and a root file both report nothing | same |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/Findings.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/FindingsTests.cs -Session summoner-convergence-lane-d2-20260919` | 27/27 passed | plan resolved `testsplitanalyzer-fallback` |

`Findings.Build` takes `ownProjectRoot` and `rootNamespace` as explicit parameters (not hardcoded to
Core.Tests) so the same code serves any analyzed project; the real run (TVB1.10) supplies them from
the `--project` argument's own directory and its csproj's `RootNamespace`.

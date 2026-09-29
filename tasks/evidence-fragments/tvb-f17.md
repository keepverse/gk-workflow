# TVB-F17 — `GlobalUsings.cs` is declared out of the candidate model (option b)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the decision | `gk-core/tests/core-test-projects.v1.json` | project 30 `FusionRpg.Core.GlobalUsings.Tests` removed from `projects`; the file stays in the residual, where its own header says it belongs | `gk-core/tests/core-test-projects.v1.json` |
| manifest size | `python -c "len(json.load(...)['projects'])"` | **67** — every one applied | — |
| the policy rules | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~CoreTestProjectPolicy"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` (W1 is the rule that would catch an unlisted csproj) | — |
| the tool still parses it | `dotnet tools/FileMove/bin/Release/net8.0/FileMove.dll split gk-core/tests/core-test-projects.v1.json --project FusionRpg.Core.Hud.Tests` | `REFUSED: manifest fails 3 A1 rule(s)` — all three about that applied project's own directory/include patterns, none about the manifest | — |
| registry integrity | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |

The row offered (a) move the file into the `shared` set, or (b) keep it in the residual and declare it out of
the candidate model. (a) is the more elegant answer and needs a shared-set DRIFT entry point that does not
exist — the props and the shared moves are written only when `isFirstIncrement` is true (`SplitPlanner.cs:120`,
`:158-181`), which is false for all 67 projects, and A1 refuses an applied project, so no
`split --project <n> --apply` can carry it. (b) is correct on the evidence: a `global using` is
per-compilation, the residual's default glob already compiles the file, and no split project uses either alias
— every increment's own apply gate proved that.

What (b) removes is the trap the row filed: `split --project FusionRpg.Core.GlobalUsings.Tests --apply` is no
longer a name anyone can type, because the project is no longer declared. What it costs is the manifest's
one-candidate-per-root-file model being one candidate short, which the row's own option (b) sanctions and this
fragment records.

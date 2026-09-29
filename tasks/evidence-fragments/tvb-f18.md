# TVB-F18 — the production map's three missing causes, and the fourth found while fixing them

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| before | `TestSplitAnalyzer --project gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --production-map --configuration Release` | 35 areas; **16 test projects with compilation errors**, the map declaring itself UNDER-reported for them (residual 57 errors, `Server.Tests` 795, `Hud.Tests` 64, `Commanders.Tests` 58) | this fragment |
| after | same command | **`Test projects with compilation errors: 0 (every scanned project resolved its references, so the map is complete for them)`**; 35 areas, 83 projects scanned | this fragment |
| the analyzer's own suite | `dotnet test gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests -c Release` | `Passed! - Failed: 0, Passed: 35, Skipped: 0, Total: 35` (32 existing + 3 new) | `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/LinkedSourcePathsTests.cs` |
| registry integrity | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |

**Cause 1 — the linked sources were never parsed.** `BuildCompilation` scans the project DIRECTORY, so
`gk-core/tests/Shared/KeepverseRoots.cs` (`Directory.Build.props:18`) and the shared props' four files were
never in the compilation; the project's own previously-built DLL, which the analyzer happened to
reference, supplied those types by accident. Excluding that DLL alone — the obvious fix — made the map
WORSE (11 erroring projects → 16; the residual 16 → 57 errors). `CsprojReader.LinkedSourcePaths` now
follows `<Import>` transitively, resolves `$(MSBuildThisFileDirectory)` and bare relative includes
against the DECLARING file, and the own-output reference is dropped.

**Cause 2 — `Directory.Build.props` is auto-imported, not named by the project.** No `<Import>` points
at it, so the walk has to look for it. The first version walked to the filesystem root, and this repo's
worktrees live under `<main>/.claude/worktrees/<lane>/`, so it reached the MAIN checkout's own
`Directory.Build.props` and parsed a second `gk-core/tests/Shared/KeepverseRoots.cs` from a different absolute
path — `the namespace 'FusionRpg.TestSupport' already contains a definition for 'KeepverseLayout'` in
every project. MSBuild stops at the first file found; so does the walk now.

**Cause 3 — the ASP.NET shared framework is not in the process's TPA list.** `FusionRpg.Server.Tests`
reported 489 errors on `Microsoft.AspNetCore.*`. The framework is now found beside this process's own
`System.Private.CoreLib`, **version-matched to the project's `<TargetFramework>`** (a 9.x reference
against a net8.0 project was measured as its own error), with native images (`aspnetcorev2_inprocess.dll`)
refused up front — `CreateReferenceFromFile` is lazy, and a native image only fails at bind time, as
CS0009 in every project.

**Cause 4 — found while fixing them: the map over-counted once the shared sources were parsed.** Shared
test infrastructure is compiled into every project, so counting its references as the project's own
pushed 17 of 35 areas to 70-71 of 83 projects — the whole `core` group, i.e. no narrowing at all.
`AreasReferencedBy` now walks the project's OWN sources (`SourceFiles`) only. The resulting sizes are
readings, not constants: Events/Onboarding/Settings/Time 1, Diagnostics/Lawn/Scope 2 … Stats 29,
Effects 32. `null` keeps the whole-compilation shape the K-T1 synthetic fixture uses.

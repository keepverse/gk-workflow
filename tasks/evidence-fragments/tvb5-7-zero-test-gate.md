# TVB5.7 — the increment whose new project ran **zero tests** and passed

Found by reading the first real increment's own verification output, not by the tool: the apply gate
reported `kept.` four times over, and `verify-change` was green, while the new project's test step said

```
No test is available in D:\...\FusionRpg.Core.AchievementTitlesTuningTests.Tests.dll.
Make sure that test discoverer & executors are registered ...
```

and `dotnet test` **exited 0**. This is the exact quiet failure `core-split-wiring` exists to prevent —
a runner that still points somewhere the tests no longer are, and reports success.

## Cause, read from the code and the artifact

`SplitPlanner.BuildSharedProps` copied the residual's package references with a regex matching only the
**self-closing** shape (`<PackageReference … />`). The residual's own `coverlet.collector` and
`xunit.runner.visualstudio` are **paired** elements (`IncludeAssets`/`PrivateAssets` children), so they
never moved into `CoreTests.Shared.props` and stayed in the residual. The new project therefore had no
xunit test adapter: nothing was discovered, nothing ran, exit code 0. `core-split-apply` A2 says the
props carries "the package references (`FusionRpg.Core.Tests.csproj:10-22`)" — lines 10-22 are that
whole `ItemGroup`, paired elements included.

Two defects, one per layer:

| Layer | Defect | Fix |
|---|---|---|
| the tool | the props builder understood only self-closing `PackageReference` elements | `PackageReferenceElement` matches both shapes as whole lines; `Reindent` keeps a paired element's children indented under their parent; the residual loses both shapes |
| the gate | `dotnet test`'s exit code was the only verdict, so a **zero-test** run passed | `SplitExecutor.TestsReported(output)` reads the console summary's `Total:`; a test step that reports `null` or `0` is treated as a failure and reverts the increment, exactly like a non-zero exit |

The gate is strictly stronger than before, never weaker: no step was removed, no filter changed.

| Criterion | Command | Result |
|---|---|---|
| The defect, live, before the fix | `dotnet test gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests.csproj -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | **exit 0**, `No test is available in …` — 0 tests run |
| Paired element moves with its children | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release --filter "FullyQualifiedName~A_paired_package_reference_moves_to_the_shared_props_with_its_children"` | 1 passed |
| Zero-test output is not a pass | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release --filter "FullyQualifiedName~A_test_run_reports_how_many_tests_it_ran\|FullyQualifiedName~A_test_run_that_discovered_nothing_reports_no_count_rather_than_a_pass"` | 3 passed |
| Whole tool suite | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release` | **44 passed / 0 failed** |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitPlanner.cs,gk-core/tools/FileMove/SplitExecutor.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs -Session tvb58` | exit 0; `filemove-fallback` module run **44/44**; `test-substrate` guard OK |

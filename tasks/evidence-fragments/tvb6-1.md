# TVB6.1 — Analyzer `--production-map`

## Result

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| K-T1 (fixture: area symbols referenced from two synthetic projects → the map lists both) | `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Debug -- --production-map --self-check` | `K-T1 PASS - the production map lists both synthetic projects that reference Alpha, and only TestTwo for Beta` (exit 0) | `gk-core/tools/TestSplitAnalyzer/ProductionMap.cs` (`RunFixture`) |
| Per `gk-core/src/FusionRpg.Core/<dir>`, the test projects referencing its symbols; same compilation model, read-only | `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Debug -- --production-map --project gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --test-projects tests --configuration Debug --format md` | 2709 declared types, 34 areas, **7 areas referenced across 2 scanned test projects**; `Battle`/`Power`/`Stats` from BOTH `FusionRpg.Core.Atoms.Tests` and `FusionRpg.Core.ClassSystem.Tests`, `Combat`/`Effects`/`Match`/`Status` from Atoms; 24 projects skipped (no build output) and named | this fragment |
| Both modes share one compilation model | build + both runs | `BuildCompilation` extracted once; `--project` main mode re-run below | `gk-core/tools/TestSplitAnalyzer/Program.cs` |
| The map cannot silently under-report a scanned project | `dotnet run --project gk-core/tools/TestSplitAnalyzer -c Debug -- --production-map --project gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --test-projects tests --configuration Debug --format md` | `Test projects with compilation errors (the map UNDER-reports these): gk-core/tests/FusionRpg.Core.Atoms.Tests (1047), gk-core/tests/FusionRpg.Core.ClassSystem.Tests (421), gk-core/tests/FusionRpg.Guard.Tests (3553)` — every scanned project's error count is printed (and `testProjectsWithCompilationErrors` in json), so an unresolved-reference project is named instead of silently contributing fewer areas | `gk-core/tools/TestSplitAnalyzer/Program.cs` |
| No regression in the existing grouping report | `dotnet test gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests` | see verify-change row below | `gk-core/tools/TestSplitAnalyzer/Program.cs` |

## Method

`ProductionMap.BuildAreaIndex` walks the production compilation's own `Assembly.GlobalNamespace` and keys each
declared type by `type.ToDisplayString()` → the first path segment below `gk-core/src/FusionRpg.Core/`. `AreasReferencedBy`
resolves every `SimpleNameSyntax` through one test compilation's semantic model and matches the referenced type (or
its containing type) against that index — so a name in a comment or a string never counts, and the area comes from
the symbol's declaration, never from a project name that happens to match the folder (K1's own "never by name
alone"). Both halves are pure and read-only; no MSBuild, no Workspaces — `Program.cs` now has ONE
`BuildCompilation` that both `--production-map` and the existing grouping mode call.

The production assembly is added to every test compilation explicitly: the split test projects' `ProjectReference`
to `FusionRpg.Core` does not copy `FusionRpg.Core.dll` into their own output directory in every case, so the
output-directory metadata scan alone can leave Core types unresolved (an error symbol matches no area — the map
would be empty for a reason nothing reports; found by this task's first real run returning "0 referenced areas"
for a project known to reference Core).

## Not proved

- **The real run's 7-area list is a FLOOR, not the answer.** The diagnostic added at the end of this task
  reports that both scanned test compilations have unresolved references (Atoms 1047 errors, ClassSystem
  421; Guard.Tests 3553 and it references no Core symbol at all), so each project references more areas
  than the map can see. The analyzer's compilation model takes metadata from the project's own build
  output plus the runtime's TPA list, which is evidently not the full reference set these projects build
  with — see TVB-F18. TVB6.2 must not derive an owner from these numbers until that is fixed; the fixture
  (K-T1) is unaffected because it supplies its own reference set.
- K-T1 is proven by the tool's own `--self-check` fixture, **not** by an xunit test: the row's Files line names
  `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ProductionMapTests.cs` (that file does not exist yet), and this lane's fence excludes `tests/**`
  (tvb58's single-writer surface). Routed as TVB-F17 with an erratum request; the fixture run above is the
  strongest achievable check and is reproducible by anyone.
- The real run covers only the 2 test projects with a Debug build in this worktree (24 skipped, each named in the
  output), and its area list is a floor (see above) — TVB6.2 consumes it once the split has landed (dep TVB5.9)
  and TVB-F18 is fixed.

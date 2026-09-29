# Phase 0B verification-boundary mapping repair

**Session:** `resume-00b-verification-mapping-20260925`
**Date:** 2026-09-25
**Status:** Partial implementation complete; the current isolated worktree cannot pass the direct registry integrity check until the separate Seedsmith acceptance lane supplies its two owned test files.

## Change

Added one focused owner boundary, `seedsmith-bcu212`, before `seedsmith-fallback`. It owns exactly the three requested concrete paths and selects exactly the three BCU2.12/J9 test files:

- `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`
- `.claude/cmdc-agents/scripts/bcu212-report.py`
- `gk-forge/tools/seedsmith/_j9_batch_run.py`
- `gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py`
- `gk-forge/tools/seedsmith/tests/test_bcu212_report.py`
- `gk-forge/tools/seedsmith/tests/test_j9_batch_run.py`

No root was broadened, no Seedsmith code/data was edited, no BCU2.12 run was resumed, and no commit/push/merge was performed.

## Exact diff

### `gk-core/scripts/verification-boundaries.v1.json`

```diff
diff --git a/scripts/verification-boundaries.v1.json b/scripts/verification-boundaries.v1.json
index 680a445e8..5b11987d1 100644
--- a/scripts/verification-boundaries.v1.json
+++ b/scripts/verification-boundaries.v1.json
@@ -2555,6 +2555,23 @@
       "guards": [],
       "level": "module"
     },
+    {
+      "id": "seedsmith-bcu212",
+      "kind": "owner",
+      "paths": [
+        ".claude/cmdc-agents/scripts/bcu212-full-run.ps1",
+        ".claude/cmdc-agents/scripts/bcu212-report.py",
+        "gk-forge/tools/seedsmith/_j9_batch_run.py"
+      ],
+      "project": "seedsmith",
+      "testFiles": [
+        "gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py",
+        "gk-forge/tools/seedsmith/tests/test_bcu212_report.py",
+        "gk-forge/tools/seedsmith/tests/test_j9_batch_run.py"
+      ],
+      "guards": [],
+      "level": "focused"
+    },
     {
       "id": "seedsmith-fallback",
       "kind": "owner",
       "paths": [
         "gk-forge/tools/seedsmith/**"
```

### `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs`

The new file is 293 lines. Its exact content is:

```diff
diff --git a/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs b/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs
new file mode 100644
index 000000000..3ff029f4a
--- /dev/null
+++ b/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs
@@ -0,0 +1,293 @@
+using System.Diagnostics;
+using System.Text.Json;
+using System.Text.RegularExpressions;
+using Xunit;
+
+namespace FusionRpg.Guard.Tests;
+
+/// <summary>
+/// Structural regression coverage for the BCU2.12 verification-boundary repair.
+///
+/// The launcher/report tests are owned by the separate Seedsmith acceptance lane.  The planner
+/// proof therefore uses a tiny planted registry with the same boundary shape instead of making
+/// this structural test depend on that lane's dirty files; the first two tests still read and
+/// assert the real registry itself.
+/// </summary>
+[Trait("VerificationId", "guard.verification-boundaries")]
+public sealed class VerificationBoundaryMappingRepairTests
+{
+    private const string RegistryPath = "gk-core/scripts/verification-boundaries.v1.json";
+    private const string BoundaryId = "seedsmith-bcu212";
+    private const string FallbackId = "seedsmith-fallback";
+    private const string TreeOwnerId = "seedsmith-trees";
+    private const string NeighborPath = "gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py";
+    private const string NeighborTestPath = "tools/seedsmith/tests/test_tree_species_fixture.py";
+
+    private static readonly string[] ConcretePaths =
+    {
+        ".claude/cmdc-agents/scripts/bcu212-full-run.ps1",
+        ".claude/cmdc-agents/scripts/bcu212-report.py",
+        "gk-forge/tools/seedsmith/_j9_batch_run.py",
+    };
+
+    private static readonly string[] FocusedTestFiles =
+    {
+        "gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py",
+        "gk-forge/tools/seedsmith/tests/test_bcu212_report.py",
+        "gk-forge/tools/seedsmith/tests/test_j9_batch_run.py",
+    };
+
+    private static string RepoRoot()
+    {
+        var directory = new DirectoryInfo(AppContext.BaseDirectory);
+        while (directory is not null)
+        {
+            if (File.Exists(Path.Combine(directory.FullName, "scripts", "verify-change.ps1")))
+                return directory.FullName;
+            directory = directory.Parent;
+        }
+
+        throw new DirectoryNotFoundException("Could not find repository root with scripts/verify-change.ps1");
+    }
+
+    [Fact]
+    public void Bcu212_boundary_maps_exactly_the_three_paths_to_the_three_real_tests()
+    {
+        using var document = ReadRegistry();
+        var boundary = FindBoundary(document.RootElement, BoundaryId);
+
+        Assert.Equal("owner", boundary.GetProperty("kind").GetString());
+        Assert.Equal("seedsmith", boundary.GetProperty("project").GetString());
+        Assert.Equal("focused", boundary.GetProperty("level").GetString());
+        Assert.Equal(ConcretePaths, StringArray(boundary, "paths"));
+        Assert.Equal(FocusedTestFiles, StringArray(boundary, "testFiles"));
+        Assert.Empty(StringArray(boundary, "guards"));
+
+        var boundaries = document.RootElement.GetProperty("boundaries").EnumerateArray().ToArray();
+        Assert.All(ConcretePaths, path => Assert.Equal(BoundaryId, ResolveOwnerId(path, boundaries)));
+    }
+
+    [Fact]
+    public void Bcu212_boundary_precedes_the_fallback_and_does_not_steal_the_tree_owner()
+    {
+        using var document = ReadRegistry();
+        var boundaries = document.RootElement.GetProperty("boundaries").EnumerateArray().ToArray();
+        var bcuIndex = Array.FindIndex(boundaries, b => b.GetProperty("id").GetString() == BoundaryId);
+        var fallbackIndex = Array.FindIndex(boundaries, b => b.GetProperty("id").GetString() == FallbackId);
+
+        Assert.True(bcuIndex >= 0, $"missing {BoundaryId}");
+        Assert.True(fallbackIndex >= 0, $"missing {FallbackId}");
+        Assert.True(bcuIndex < fallbackIndex,
+            $"{BoundaryId} must precede {FallbackId}: {bcuIndex} is not before {fallbackIndex}");
+
+        var treeOwner = FindBoundary(document.RootElement, TreeOwnerId);
+        Assert.Contains("gk-forge/tools/seedsmith/seedsmith/adapters/trees/**", StringArray(treeOwner, "paths"));
+        Assert.Equal(TreeOwnerId, ResolveOwnerId(NeighborPath, boundaries));
+    }
+
+    [Fact]
+    public void PlanOnly_selects_only_the_three_bcu212_tests_and_keeps_the_neighbor_on_seedsmith_trees()
+    {
+        var root = PlantPlannerFixture();
+        try
+        {
+            var bcuPaths = PowershellPathArray(ConcretePaths);
+            var (bcuExit, bcuStdout, bcuStderr) = RunPowerShell(
+                root,
+                $"-Command \"& .\\scripts\\verify-change.ps1 -Paths {bcuPaths} -Root '{root}' " +
+                "-AllowUnscoped -PlanOnly -Format json\"");
+
+            Assert.True(bcuExit == 0,
+                $"BCU2.12 plan failed exit={bcuExit}\nstdout:\n{bcuStdout}\nstderr:\n{bcuStderr}");
+            Assert.DoesNotContain(FallbackId, bcuStdout, StringComparison.Ordinal);
+
+            using var bcuPlan = JsonDocument.Parse(bcuStdout);
+            var bcuSelections = bcuPlan.RootElement.GetProperty("selections").EnumerateArray()
+                .Where(s => ConcretePaths.Contains(s.GetProperty("path").GetString(), StringComparer.Ordinal))
+                .ToArray();
+            Assert.Equal(ConcretePaths.Length, bcuSelections.Length);
+            Assert.All(bcuSelections, selection =>
+                Assert.Equal(BoundaryId, selection.GetProperty("boundary").GetString()));
+
+            var pytest = bcuPlan.RootElement.GetProperty("checks").EnumerateArray()
+                .Single(check => check.GetProperty("kind").GetString() == "pytest");
+            Assert.Equal(
+                FocusedTestFiles.OrderBy(path => path, StringComparer.Ordinal),
+                pytest.GetProperty("targets").EnumerateArray().Select(e => e.GetString() ?? ""));
+
+            var (neighborExit, neighborStdout, neighborStderr) = RunPowerShell(
+                root,
+                $"-Command \"& .\\scripts\\verify-change.ps1 -Paths '{NeighborPath}' -Root '{root}' " +
+                "-AllowUnscoped -PlanOnly -Format json\"");
+            Assert.True(neighborExit == 0,
+                $"neighbor plan failed exit={neighborExit}\nstdout:\n{neighborStdout}\nstderr:\n{neighborStderr}");
+
+            using var neighborPlan = JsonDocument.Parse(neighborStdout);
+            var neighborSelection = neighborPlan.RootElement.GetProperty("selections").EnumerateArray()
+                .Single(selection => selection.GetProperty("path").GetString() == NeighborPath);
+            Assert.Equal(TreeOwnerId, neighborSelection.GetProperty("boundary").GetString());
+        }
+        finally
+        {
+            Directory.Delete(root, recursive: true);
+        }
+    }
+
+    private static JsonDocument ReadRegistry()
+    {
+        var path = Path.Combine(RepoRoot(), RegistryPath.Replace('/', Path.DirectorySeparatorChar));
+        return JsonDocument.Parse(File.ReadAllText(path));
+    }
+
+    private static JsonElement FindBoundary(JsonElement root, string id) =>
+        root.GetProperty("boundaries").EnumerateArray()
+            .Single(boundary => boundary.GetProperty("id").GetString() == id);
+
+    private static string[] StringArray(JsonElement value, string property) =>
+        value.GetProperty(property).EnumerateArray().Select(item => item.GetString() ?? "").ToArray();
+
+    private static string ResolveOwnerId(string path, JsonElement[] boundaries)
+    {
+        var hits = boundaries
+            .Where(boundary => boundary.GetProperty("kind").GetString() == "owner")
+            .SelectMany(boundary => StringArray(boundary, "paths").Select(pattern => new
+            {
+                Id = boundary.GetProperty("id").GetString()!,
+                Pattern = pattern,
+                Specificity = PatternSpecificity(pattern),
+            }))
+            .Where(hit => Matches(path, hit.Pattern))
+            .ToArray();
+
+        Assert.NotEmpty(hits);
+        var best = hits.Max(hit => hit.Specificity);
+        var owners = hits.Where(hit => hit.Specificity == best)
+            .Select(hit => hit.Id)
+            .Distinct(StringComparer.Ordinal)
+            .ToArray();
+        Assert.Single(owners);
+        return owners[0];
+    }
+
+    private static bool Matches(string path, string pattern)
+    {
+        if (pattern.EndsWith("/**", StringComparison.OrdinalIgnoreCase))
+            return path.StartsWith(pattern[..^2], StringComparison.OrdinalIgnoreCase);
+        if (!pattern.Contains('*', StringComparison.Ordinal))
+            return path.Equals(pattern, StringComparison.OrdinalIgnoreCase);
+
+        var lastSlash = pattern.LastIndexOf('/');
+        var directory = lastSlash < 0 ? "" : pattern[..(lastSlash + 1)];
+        var tail = pattern[(lastSlash + 1)..];
+        if (!path.StartsWith(directory, StringComparison.OrdinalIgnoreCase)) return false;
+        var pathTail = path[directory.Length..];
+        if (pathTail.Contains('/', StringComparison.Ordinal)) return false;
+        return Regex.IsMatch(
+            pathTail,
+            "^" + Regex.Escape(tail).Replace("\\*", "[^/]*") + "$",
+            RegexOptions.IgnoreCase);
+    }
+
+    private static int PatternSpecificity(string pattern)
+    {
+        var rank = pattern.EndsWith("/**", StringComparison.OrdinalIgnoreCase) ? 0
+            : pattern.Contains('*', StringComparison.Ordinal) ? 2
+            : 3;
+        return rank * 100_000 + pattern.Length;
+    }
+
+    private static string PowershellPathArray(IEnumerable<string> paths) =>
+        "@(" + string.Join(",", paths.Select(path => $"'{path.Replace("'", "''")}'")) + ")";
+
+    private static (int Exit, string Stdout, string Stderr) RunPowerShell(string root, string arguments)
+    {
+        var psi = new ProcessStartInfo
+        {
+            FileName = "powershell",
+            Arguments = $"-NoProfile -ExecutionPolicy Bypass {arguments}",
+            WorkingDirectory = RepoRoot(),
+            CreateNoWindow = true,
+        };
+        return ExternalProcess.Run(psi, 120_000, "verification-boundary planner fixture timed out");
+    }
+
+    private static string PlantPlannerFixture()
+    {
+        var repo = RepoRoot();
+        var root = Path.Combine(Path.GetTempPath(), "verification-boundary-bcu212-" + Guid.NewGuid().ToString("N"));
+        Directory.CreateDirectory(Path.Combine(root, "scripts", "lib"));
+        Copy(repo, "scripts/verify-change.ps1", root);
+        Copy(repo, "gk-core/scripts/guard-verification-boundaries.py", root);
+        Copy(repo, "scripts/lib/VerificationBoundaries.ps1", root);
+        File.WriteAllText(Path.Combine(root, "scripts", "test-fast.ps1"),
+            "$Filter = \"Category!=DiskSemantics&Category!=Heavy\"\n");
+        File.WriteAllText(Path.Combine(root, "scripts", "enforcement-registry.v1.json"),
+            "{\"schemaVersion\":1,\"guards\":{},\"invariants\":[]}\n");
+
+        foreach (var path in ConcretePaths)
+            WriteFixtureFile(root, path, "fixture\n");
+        foreach (var path in FocusedTestFiles)
+            WriteFixtureFile(root, path, "def test_fixture(): pass\n");
+        WriteFixtureFile(root, NeighborPath, "fixture\n");
+        WriteFixtureFile(root, NeighborTestPath, "def test_fixture(): pass\n");
+
+        var registry = new
+        {
+            schemaVersion = 5,
+            projects = new
+            {
+                seedsmith = new { runner = "pytest", root = "gk-forge/tools/seedsmith", tests = "tests" },
+            },
+            boundaries = new object[]
+            {
+                new
+                {
+                    id = BoundaryId,
+                    kind = "owner",
+                    paths = ConcretePaths,
+                    project = "seedsmith",
+                    testFiles = FocusedTestFiles,
+                    guards = Array.Empty<string>(),
+                    level = "focused",
+                },
+                new
+                {
+                    id = FallbackId,
+                    kind = "owner",
+                    paths = new[] { "gk-forge/tools/seedsmith/**" },
+                    project = "seedsmith",
+                    guards = Array.Empty<string>(),
+                    level = "module",
+                },
+                new
+                {
+                    id = TreeOwnerId,
+                    kind = "owner",
+                    paths = new[] { "gk-forge/tools/seedsmith/seedsmith/adapters/trees/**" },
+                    project = "seedsmith",
+                    testFiles = new[] { NeighborTestPath },
+                    guards = Array.Empty<string>(),
+                    level = "focused",
+                },
+            },
+        };
+        File.WriteAllText(
+            Path.Combine(root, RegistryPath.Replace('/', Path.DirectorySeparatorChar)),
+            JsonSerializer.Serialize(registry));
+        return root;
+    }
+
+    private static void Copy(string repo, string relativePath, string root)
+    {
+        var destination = Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));
+        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
+        File.Copy(Path.Combine(repo, relativePath.Replace('/', Path.DirectorySeparatorChar)), destination);
+    }
+
+    private static void WriteFixtureFile(string root, string relativePath, string content)
+    {
+        var destination = Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));
+        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
+        File.WriteAllText(destination, content);
+    }
+}
```

## Commands and observed output

| Command | Exit | Output/result |
|---|---:|---|
| `python scripts/session-boundary-check.py --session resume-00b-verification-mapping-20260925` | 0 | `[session-boundary] clean for 'resume-00b-verification-mapping-20260925'` |
| `$doc = Get-Content -LiteralPath scripts\verification-boundaries.v1.json -Raw \| ConvertFrom-Json; ...` | 0 | `schemaVersion=5`; `seedsmith-bcu212` index `171`; `seedsmith-fallback` index `172`; exact three paths and three test files present; level `focused`. |
| `. .\scripts\lib\VerificationBoundaries.ps1; ... Resolve-Owner ...` | 0 | All three concrete paths resolved to `seedsmith-bcu212`; none resolved to `seedsmith-fallback`. |
| `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj --filter "FullyQualifiedName~VerificationBoundaryMappingRepairTests" --verbosity minimal` | 0 | `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3`. The PlanOnly fixture test asserts the three concrete paths select `seedsmith-bcu212`, the pytest target list is exactly the three named files, and the neighboring tree path remains `seedsmith-trees`. |
| `git diff --check` | 0 | No whitespace errors. |
| `git diff --stat -- gk-core/scripts/verification-boundaries.v1.json gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs` | 0 | Registry: 17 insertions; new test file: 293 lines (untracked until the manager harvests it). |
| `.\scripts\verify-change.ps1 -Paths .claude/cmdc-agents/scripts/bcu212-full-run.ps1,.claude/cmdc-agents/scripts/bcu212-report.py,gk-forge/tools/seedsmith/_j9_batch_run.py -PlanOnly -AllowUnscoped -Format json` | **1** | The direct current-tree check is blocked before planning: `testFiles pattern matches no test file: seedsmith-bcu212: gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py` and the same for `test_bcu212_report.py`. The two files are owned by the active `seedsmith-p1-audit-acceptance-20260925` lane and are not present in this worktree. |

BLOCKED: the direct current-root `verify-change.ps1 -PlanOnly` check cannot pass its integrity precheck because `test_bcu212_launcher.py` and `test_bcu212_report.py` are owned by the active Seedsmith acceptance lane and are absent from this worktree. The focused Guard fixture is a structural/planner proof with three tiny test files; it is **not** a broad Seedsmith run and is not evidence that the missing acceptance files are already present.

## Open issues

1. `gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py` and `gk-forge/tools/seedsmith/tests/test_bcu212_report.py` are absent from this worktree. The active Seedsmith acceptance session owns those paths; this lane did not edit or copy them.
2. Consequently, the exact current-root `verify-change.ps1 -PlanOnly` command cannot pass its registry integrity precheck yet. The final manager acceptance must rerun it after the acceptance lane's files are present.
3. No BCU2.12 generation or resume was attempted. No broad Seedsmith test run was used as evidence.

## Next steps

1. The manager should apply/accept the Seedsmith acceptance-lane test files without changing this mapping boundary.
2. Rerun the exact three-path `verify-change.ps1 -PlanOnly -Format json` command in the composite tree; expect three `seedsmith-bcu212` selections and one pytest check whose targets are exactly the three named test files.
3. Run the focused Guard filter again in that composite tree, then inspect the final diff. Do not commit or merge from this lane.

<<<REPORT {"status":"partial","summary":"Added the focused seedsmith-bcu212 boundary before seedsmith-fallback and a three-test structural/planner regression. JSON parse, focused Guard tests, structural owner resolution, and diff checks pass. The direct current-root verify-change proof is blocked only because the active Seedsmith acceptance lane's two owned test files are not present in this isolated worktree; no BCU2.12 run was resumed.","changed_files":["gk-core/scripts/verification-boundaries.v1.json","gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs","tasks/reports/resume-00b-verification-mapping-20260925.md"],"verification":[{"command":".\\scripts\\session-boundary-check.py --session resume-00b-verification-mapping-20260925","result":"exit 0; session clean"},{"command":"Get-Content -LiteralPath scripts\\verification-boundaries.v1.json -Raw | ConvertFrom-Json","result":"exit 0; schemaVersion 5 parsed; bcu212 index 171 before fallback index 172"},{"command":"dotnet test tests\\FusionRpg.Guard.Tests\\FusionRpg.Guard.Tests.csproj --filter \"FullyQualifiedName~VerificationBoundaryMappingRepairTests\" --verbosity minimal","result":"exit 0; 3 passed, 0 failed, 0 skipped"},{"command":"git diff --check","result":"exit 0; no whitespace errors"},{"command":".\\scripts\\verify-change.ps1 -Paths .claude/cmdc-agents/scripts/bcu212-full-run.ps1,.claude/cmdc-agents/scripts/bcu212-report.py,gk-forge/tools/seedsmith/_j9_batch_run.py --plan-only -AllowUnscoped -Format json","result":"exit 1; integrity guard reports the two acceptance-lane test files are absent, so planning cannot start"}],"open_issues":["The active Seedsmith acceptance lane must supply test_bcu212_launcher.py and test_bcu212_report.py before the direct current-root verify-change proof can pass.","The final composite-tree PlanOnly and focused Guard checks remain to be rerun after that dependency is applied.","No commit, push, merge, or BCU2.12 resume was performed."]} REPORT>>>

# TVB5.2 — `FileMove` split manifest model + A1 validation

New `SplitManifest`/`SplitProject` record pair plus `SplitManifestValidator.Validate(...)`
(`gk-core/tools/FileMove/SplitManifest.cs`), implementing every A1 rule from `spec-core-split-apply.md`:

- an `Include` pattern must match at least one file
- no file may be claimed by two projects, and no file may be both shared and claimed
- every `References` entry must exist, live under `src/`/`tools/`, never be a `.Tests.csproj`, and
  be a subset of what the residual project references today (a split narrows, never widens)
- a project `Name` must end `.Tests` and must never contain `FusionRpg.Data` (the Core/Data layering
  guard substring-scans project names)
- a project directory must be a direct child of `tests/` and must not already exist

All filesystem-shaped questions (`filesMatching`, `referenceExists`, `projectDirectoryExists`,
`residualReferences`) are injected delegates, matching the existing `FileMover` seam
(`readText`/`enumerateFiles`) — so every case in this task runs **in memory**, no disk touched.

## Tests

`gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs` (new), 11 cases, covering exactly the F-numbers
this module owns per the spec's own testing table (F2, F3, F4, F5, F11) plus one happy-path baseline
and two adjacent A1 rules exercised alongside them (empty include match, missing reference):

| Case | Spec ref | What it proves |
|---|---|---|
| `A_well_formed_manifest_validates_ok` | baseline | a correct manifest is `Ok` |
| `F2_a_file_claimed_by_two_projects_is_refused` | F2 | double-claim refused before any edit |
| `F2_a_shared_file_also_claimed_by_a_project_is_refused` | F2 | shared+claimed refused |
| `F3_a_reference_naming_a_test_project_is_refused` | F3 | a `.Tests.csproj` reference refused |
| `F4_a_name_containing_FusionRpg_Data_is_refused` | F4 | Core/Data substring-scan guard respected |
| `F4_a_name_not_ending_in_Tests_is_refused` | F4 | name-shape rule |
| `F5_a_reference_the_residual_does_not_have_today_is_refused` | F5 | a split never widens dependencies |
| `F11_a_project_directory_that_already_exists_is_refused` | F11 | no silent overwrite |
| `F11_a_project_name_that_is_not_a_direct_child_of_tests_is_refused` | F11 | nesting refused |
| `An_include_pattern_matching_no_file_is_refused` | A1 | a dead include pattern is a defect, not a no-op |
| `A_reference_that_does_not_exist_is_refused` | A1 | a stale/typo'd reference is refused |

## Verification

| Criterion | Command | Result |
|---|---|---|
| Build | `dotnet build gk-core/tools/FileMove/FileMove.csproj -v q` | exit 0, 0 Error(s) |
| Focused run | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release --filter "FullyQualifiedName~SplitManifestTests"` | 11/11 passed |
| Whole affected project | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitManifest.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs -Session tvb-wave5-20260920` | test-substrate guard OK; `FusionRpg.FileMove.Tests` 20/20 passed (11 new + 9 pre-existing `FileMoverTests`) |

No production code outside `gk-core/tools/FileMove/` touched; no doc citation invalidated (no doc names
`SplitManifest.cs` yet — `spec-core-split-apply.md` describes the shape, not the file, and needs no
edit). `SplitManifest`/`SplitProject`/`ManifestViolation`/`ManifestValidationResult` records and
`MatchesPattern` were already present from the prior increment (build-verified there); this task adds
only the test file and turns the build-only proof into a behavior-verified one.

Files: `gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestTests.cs` (new). `gk-core/tools/FileMove/SplitManifest.cs`
already existed from the prior work session; unchanged in this task.

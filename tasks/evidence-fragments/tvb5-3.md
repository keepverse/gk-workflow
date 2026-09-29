# TVB5.3 — `SplitPlanner` + dry-run `split` verb + dirty-path refusal

New `gk-core/tools/FileMove/SplitPlanner.cs`: `SplitOp`/`SplitOpKind`/`SplitPlan` (per `core-split-apply` A4's
exact shape) and `SplitPlanner.Plan(manifest, projectName, filesMatching, readBytes, fileExists,
dirtyPaths)`. Every filesystem-shaped input is an injected delegate, matching `FileMover`'s existing
`readText`/`enumerateFiles` seam, so planning — including the dirty-path check — runs in memory.

Never calls `FileMover.Plan` or `MovePlanner.RewriteNamespace` (A2: a split moves bytes unchanged and
never touches a namespace, unlike `move` mode).

## What one increment's plan contains

- `CreateDirectory` for the new project directory (+ the shared directory, first increment only)
- `CreateFile` for the new project's `.csproj` (imports the shared props, declares `ProjectReference`s
  from the manifest, `RootNamespace = FusionRpg.Core.Tests` per A2)
- First increment only: `CreateFile` for `CoreTests.Shared.props` (carries the residual's
  `PackageReference`s + one linked `Compile` item per `shared` pattern) and `ModifyFile` for the
  residual csproj (adds the props import, drops the `PackageReference`s and explicit `Compile`/`None`
  items that now live in the props)
- `CreateFile`/`ModifyFile` for `InternalsVisibleTo.CoreTests.cs`, regenerated from the **whole**
  manifest's `coreInternals: true` project names every run (deterministic regardless of which project
  is being planned — F8)
- `MoveFile` for every file the project's `include` patterns match (and, first increment, every
  `shared`-matched file) — `Before`/`After` both null, since a move never reads the source into a
  string (the record's own doc comment)
- `ModifyFile` for `FusionRpg.slnx` (one new `<Project Path=.../>` line inside `/tests/`)

**A4 extension 1 (defensive cycle check), implemented rather than left as a comment:** builds a small
`AssemblyGraph` from the residual csproj's own text plus each direct reference's csproj text (reusing
`readBytes` — no new delegate needed) and refuses if any reference's graph already reaches back to the
residual. The manifest's own rules (A1: references exist, are under `src/`/`tools/`, are a subset of
what the residual references today) are the real protection and this can never fire against a
legitimate manifest — proven by `A_reference_whose_own_graph_already_reaches_the_residual_is_refused`,
which rigs a reference csproj to reference the residual back and confirms the refusal actually fires.

## `Program.cs`

Added a `split <manifest.json> --project <name> [--apply]` verb, dry-run by default (same convention as
the existing `move` verb). `--apply` is not implemented yet — prints "not implemented yet (TVB5.4 adds
SplitExecutor)" and exits 2; TVB5.4 wires `SplitExecutor.Apply` in. Smoke-tested against the **real**
repo tree with a throwaway manifest (`Zzz/**`, deleted after the run, `git status --short` confirmed
clean before and after): dry run printed 9 real operations against `gk-core/tests/FusionRpg.Core.Tests`,
`FusionRpg.slnx`, and `gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs`, exit 0, nothing written.

## Tests

`gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs` (new), 11 cases, covering F1, F7 and F8 (the
F-numbers this module owns per the spec's testing table) plus supporting cases:

| Case | Spec ref |
|---|---|
| `F1_the_plan_moves_exactly_the_claimed_folder_with_bytes_unchanged` | F1 |
| `F1_the_plan_also_creates_the_project_directory_and_csproj` | F1 |
| `The_first_increment_also_moves_the_shared_files_and_edits_the_residual_csproj` | A2/A3 (supporting F1) |
| `A_later_increment_does_not_recreate_the_shared_props_or_edit_the_residual_csproj_again` | A5 (supporting F1) |
| `F7_a_dirty_moved_file_refuses_the_plan` | F7 |
| `F7_a_dirty_residual_csproj_refuses_the_plan` | F7 |
| `F7_a_dirty_slnx_refuses_the_plan` | F7 |
| `F7_a_dirty_path_outside_the_plan_does_not_refuse_it` | F7 (negative case) |
| `F8_two_runs_of_the_same_manifest_produce_an_identical_plan` | F8 |
| `A_reference_whose_own_graph_already_reaches_the_residual_is_refused` | A4 ext. 1 |
| `An_unknown_project_name_is_refused` | defensive |

## Verification

| Criterion | Command | Result |
|---|---|---|
| Build | `dotnet build gk-core/tools/FileMove/FileMove.csproj -v q` | exit 0, 0 Error(s) |
| Focused run | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release --filter "FullyQualifiedName~SplitPlannerTests"` | 11/11 passed |
| Whole affected project | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release` | 31/31 passed (11 new SplitPlanner + 11 SplitManifest + 9 pre-existing FileMoverTests) |
| Real-tree smoke | `dotnet run --project gk-core/tools/FileMove -c Release -- split <manifest> --project <name>` against the real repo tree | exit 0, 9 ops printed, dry run, `git status --short` clean before and after |
| Whole affected project via the boundary tool | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitPlanner.cs,gk-core/tools/FileMove/Program.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs -Session tvb-wave5-20260920` | test-substrate guard OK; `FusionRpg.FileMove.Tests` 31/31 passed |

No doc citation invalidated (no doc names `SplitPlanner.cs`'s file path; `spec-core-split-apply.md`
describes the shape, unchanged). `--apply` remains unimplemented by design — TVB5.4 is the next task.

Files: `gk-core/tools/FileMove/SplitPlanner.cs` (new), `gk-core/tools/FileMove/Program.cs` (modified: `split` verb),
`gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs` (new).

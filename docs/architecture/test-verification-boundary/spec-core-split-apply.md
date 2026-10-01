# Spec: `core-split-apply`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
[`core-split-analyzer`](spec-core-split-analyzer.md), [`registry-contract`](spec-registry-contract.md)
C7 (project groups), and the **owner-reviewed manifest** (map §7.3 checkpoint) · lands together with
[`core-split-wiring`](spec-core-split-wiring.md), one project per increment · R-TV1 step 2 · every
analyzer `BLOCKS SPLIT` finding that touches a project's files is fixed in its own earlier commit.

## Objective

Perform the split the owner approved, mechanically and reversibly: create each new test project,
move its files, give it exactly the references and internals access the manifest declares, and prove
it builds and its moved tests pass — or undo the increment. The tool **never decides a grouping**
(ideal: "The tool never decides groupings — that stays a human/design call").

**User:** whoever executes the split, one project at a time.

## Design

### A1 — the manifest: `gk-core/tests/core-test-projects.v1.json` (new, authored)

```jsonc
{
  "schemaVersion": 1,
  "analyzerCommit": "<sha the analyzer report was produced at>",
  "sharedDir": "gk-core/tests/FusionRpg.Core.Tests.Shared",        // no .csproj — linked sources + one .props
  "shared": ["TestSupport/**", "ContractTuningTestBootstrap.cs", "AssemblyInfo.cs"],
  "residual": "FusionRpg.Core.Tests",
  "projects": [
    {
      "name": "FusionRpg.Core.World.Tests",
      "include": ["World/**"],                       // relative to gk-core/tests/FusionRpg.Core.Tests/
      "references": ["gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj"],
      "links": [],                                   // extra linked sources beyond the shared set
      "content": [],                                 // None items: fixtures/…, Goldens/…
      "coreInternals": true
    }
  ]
}
```

Rules, validated before anything is written:

- every `include` matches ≥1 file; no file is claimed by two projects; `shared` files are claimed by
  no project;
- every `references` path exists, is under `src/` or `tools/` (**never a test project**, map §3.6),
  and is one the residual csproj references today (`FusionRpg.Core.Tests.csproj:24-50`). A split
  only divides the dependencies the one project already had; widening them is a separate, reviewed
  change;
- every `name` ends in `.Tests` (so `CiWiringGuardTests.cs:56` sees it) and does not contain the
  substring `FusionRpg.Data` (the Core/Data layering guard substring-scans text,
  `gk-core/src/FusionRpg.Core/InternalsVisibleTo.Fusion.cs:10-14`);
- the project directory is `tests/<name>/`, a **direct child of `tests/`**, and does not exist yet.
  The depth invariant (map §3.5) depends on the first half. The second is what makes `Revert`'s
  "delete the directory" safe.

The manifest stays in the repo after the split as the **declared dependency policy** of the Core test
projects; `core-split-wiring` adds a Guard test that every new csproj's `ProjectReference`s are a
subset of its manifest `references`. That is the permanent half of R-TV1's "architectural enforcement".

### A2 — layout of a new project (namespaces untouched)

```
tests/FusionRpg.Core.World.Tests/
  FusionRpg.Core.World.Tests.csproj     # imports ..\FusionRpg.Core.Tests.Shared\CoreTests.Shared.props
  World/**                               # moved byte-for-byte from gk-core/tests/FusionRpg.Core.Tests/World/**
```

- `RootNamespace` = `FusionRpg.Core.Tests`, and each file keeps its path below the project
  directory. **No file's text changes** (map §3.5), and whatever namespace a file declares today it
  still declares. That includes the 25 files whose namespace does not match their folder (map G17),
  so split mode never calls `FileMover.Plan`, whose namespace rewrite
  (`gk-core/tools/FileMove/FileMover.cs:51-63`) would "fix" them.
- Files move **byte for byte** (`File.Move`, or a byte copy and delete), never through
  `ReadAllText`/`WriteAllText`. A text round-trip is how an encoding or BOM changes silently. There
  are no BOMs in the project today (a reading), and 175 files use CRLF; the invariant must not depend
  on either.
- Every `[CallerFilePath]` walk (map G17) resolves to the same directory after the move, because the
  project directory sits at the same depth as `gk-core/tests/FusionRpg.Core.Tests/`.
- The shared files move once, in the first increment, to `sharedDir`; from then on **every** Core test
  project, the residual included, imports the shared `.props`. It carries what every Core test assembly needs today: the package references
  (`FusionRpg.Core.Tests.csproj:10-22`), the linked shared sources (so each assembly gets its **own**
  copy of the `[ModuleInitializer]`, `gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:43` — a module initializer in a
  referenced library would not run until that library is first touched, and the catalogs would be
  unconfigured), and `AssemblyInfo.cs`'s `DisableTestParallelization` (`gk-core/tests/FusionRpg.Core.Tests.Shared/AssemblyInfo.cs:6`).
  Parallelism across the new assemblies is by process, which is safe: the statics that forced
  serialisation are per-process.
- `DataTestStore.cs` and the three Injector sources stay linked exactly as today (`:58-61`), but only
  into projects whose manifest `links` name them.
- **The residual csproj is edited once, in the first increment.** It gains the `.props` import, and
  it loses the package references and linked items that now come from the props. Its remaining
  `ProjectReference`s and `None` items stay. Because the residual uses SDK default globs, a moved
  folder simply drops out of it, with no per-file csproj edit (the case `FileMover.cs:83-98` already
  handles by editing only explicit items).

### A3 — internals access

Core grants internals to one assembly name (`gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj:18`). Each
new project with `coreInternals: true` gets one
`[assembly: InternalsVisibleTo("<name>")]` line in a generated attribute file
`gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs` (new) — the attribute-file route the repo already
uses to keep grants out of the text-scanned csproj (`InternalsVisibleTo.Fusion.cs:10-16`). The file
is regenerated from the manifest, never hand-edited, and says so in its header.

### A4 — the tool: a `split` mode on `gk-core/tools/FileMove`

`dotnet run --project gk-core/tools/FileMove -- split <manifest> [--project <name>] [--apply]`. Dry run is the
default, as for `move` (`gk-core/tools/FileMove/Program.cs:5-11`).

Plan (the dry run prints it): the csproj to create, the `.props` to create or update, the residual
csproj edit, files to move, attribute-file lines, and the `FusionRpg.slnx` entry.

**Why `PlannedEdit` alone cannot carry a split (map G18).** `PlannedEdit(Path, Before, After, Reason)`
(`MovePlan.cs:10`) has no notion of create, modify or delete. For a moved file, `Plan` puts the
**source** text in `Before` at the **destination** path (`FileMover.cs:60`), and the source deletion
is not an edit at all (`FileMover.cs:113-115`). A `Revert` that "restores every `Before`" would write
the source text to the destination and never bring the source back. So split mode keeps
`PlannedEdit` for printing, and executes a `SplitPlan` of explicit operations:

```csharp
public enum SplitOpKind { CreateFile, ModifyFile, MoveFile, CreateDirectory }
public sealed record SplitOp(SplitOpKind Kind, string Path, string? From, byte[]? Before, byte[]? After);
```

Extensions to `FileMove`:

1. **Cycle check, restated honestly.** `AssemblyGraph` covers `src/` and `tools/` only
   (`FileMover.cs:41`). A new test project references only `src/`/`tools/` projects and nothing
   references it, so it cannot close a cycle; the manifest rules (no test references, references ⊆
   the residual's) are the real protection. Split mode still runs the graph check, as a defensive
   invariant, not as a claimed feature.
2. **`Apply(splitPlan)` writes a journal before it touches anything**: the ordered op list plus the
   original bytes of every file it will modify or move. The journal goes to
   `<temp>/filemove-split-<guid>/journal.json` and is deleted only after a kept increment.
3. **`Revert(journal)` undoes in reverse order.** A `MoveFile` is moved back byte for byte. A
   `ModifyFile` gets its original bytes. A `CreateFile` is deleted. A `CreateDirectory` is removed
   recursively, including the `bin/` and `obj/` the build step produced; that is safe only because
   A1 required the directory not to exist before. Before undoing each op, `Revert` checks that the
   path still holds what `Apply` wrote. If anything else changed it, `Revert` **stops**, prints the
   journal location, and exits 3. It never clobbers a change it did not make.
4. **Partial failure is the same path.** An I/O exception halfway through `Apply` reverts the ops
   already applied from the journal, so there is no half-applied state. If the process dies instead,
   the journal on disk is the recovery: `FileMove split --revert <journal>`.
5. **Dirty-path refusal.** `Apply` refuses to start if `git status --porcelain` shows changes under
   any path the plan touches: every moved file and its destination, the new project directory, the
   shared directory, the residual csproj, `FusionRpg.slnx`, and
   `gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs`. So a revert can never touch someone else's
   work.

The apply sequence for one project: write the journal → create the directory, csproj, props and
attribute file → edit the residual csproj (first increment only) → move files → `dotnet build` the
new project **and** the residual → `dotnet test` both with the default-profile filter (the one
`gk-core/scripts/test_fast.py:81` owns) → keep, or revert and exit 1 with the compiler or test output.

### A5 — increments and the residual

One manifest project per increment, in manifest order. After each, the residual is smaller and still
green. The split is **done** when every project in the approved manifest is applied; whatever the
manifest leaves in the residual stays there. Emptying the residual is not a goal of this module.

**What the manifest leaves is declared, not discovered (2026-09-23, lane `tvb60`).** A1 resolves an
`include` pattern against `gk-core/tests/FusionRpg.Core.Tests/`, so a residual file that a pattern matches is
*claimed* by that project — the manifest did not "leave" it, and the sentence above does not cover it.
Nothing checked that on disk: the patterns are validated only when an increment is applied, and A1
then requires the target directory **not** to exist, so a file that lands in a claimed residual folder
*after* its increment can never be moved by the tool. Measured at `0c7fb6c69`: **four** Stats-area test
files added to the residual after increment 60/68 (`cb0f048fb`) — `Stats/ActorLivenessRevisionTests.cs`
(`6eb250bc4`, lawn LW1.5), `Stats/ActorLivenessRevisionsTests.cs` (`fcfc39789`, lawn LW1.6),
`Stats/ResourceRegenUnitTests.cs` (`423579089`, lawn LW2.1), `Stats/TurnChannelDeclarationTests.cs`
(`18139aec6`, battle T17). They are recorded, not blessed, in
`gk-core/tests/FusionRpg.FileMove.Tests/SplitManifestReconciliationTests.cs`, which reconciles the real manifest
against the real residual and fails on a fifth; repairing them needs an erratum on A1's directory rule
(filed as `TVB-F30` in `tasks/test-verification-boundary-todo.md`).

## Commands

```powershell
dotnet run --project tools\FileMove -- split tests\core-test-projects.v1.json                         # plan, all
dotnet run --project tools\FileMove -- split tests\core-test-projects.v1.json --project FusionRpg.Core.World.Tests --apply
dotnet test tests\FusionRpg.FileMove.Tests -c Release
.\scripts\verify-change.ps1 -Paths <every moved and created path> -Session <id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/tools/FileMove/SplitPlanner.cs` | (new) manifest validation → `SplitPlan` (+ `PlannedEdit` view for printing) |
| `gk-core/tools/FileMove/SplitManifest.cs` | (new) manifest model + rules (A1) |
| `gk-core/tools/FileMove/SplitExecutor.cs` | (new) journal, `Apply`, `Revert` (A4) |
| `gk-core/tools/FileMove/Program.cs` | `split` verb; `split --revert <journal>` |
| `gk-core/tests/FusionRpg.FileMove.Tests/` | cases below |
| `gk-core/tests/core-test-projects.v1.json` | (new, authored, owner-approved) |
| `gk-core/tests/FusionRpg.Core.Tests.Shared/CoreTests.Shared.props` | (new) |
| `gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs` | (new, generated from the manifest) |
| `tests/FusionRpg.Core.<Area>.Tests/**` | (new, per increment) |
| `FusionRpg.slnx` | one entry per new project (`:14` is today's) |

## Code style

```csharp
// Split mode never rewrites a namespace: the move is bytes-in, bytes-out, and it is undoable.
foreach (var file in manifest.FilesFor(project))
    ops.Add(new SplitOp(SplitOpKind.MoveFile, Path: Dest(project, file), From: file,
                        Before: null, After: null));   // Revert moves it back; no text is read
```

## Testing

Planning goes through `FileMover`'s injected `readText`/`enumerateFiles` delegates
(`FileMover.cs:14-22`), so plan cases (F1–F5, F7, F8, F11) run **in memory** over a synthetic tree;
the dirty-path check gets the same treatment (an injected `git status` reader). `Apply`/`Revert`
write real files, so F6, F9 and F10 use the existing fixture's temp tree — the disk is the subject
there (`testing-standard.md` R2) — deleted with the throwing delete the fixture already uses
(`gk-core/tests/FusionRpg.FileMove.Tests/FileMoverTests.cs:36-40`, no `catch`):

| # | Fixture | Asserts |
|---|---|---|
| F1 | two folders, manifest claims one | plan moves exactly those files, bytes unchanged |
| F2 | a file claimed twice | refused before any edit |
| F3 | `references` names a `.Tests.csproj` | refused |
| F4 | project name containing `FusionRpg.Data` / not ending `.Tests` | refused |
| F5 | `references` names a `src/` project the residual does not reference | refused (a split never widens dependencies) |
| F6 | `Apply` then `Revert` | every original file byte-identical and back at its source path; created files and the new directory (incl. a planted `bin/`) gone |
| F7 | dirty path in the plan (a moved file, the residual csproj, or `FusionRpg.slnx`) | refused |
| F8 | two runs, same manifest | identical plan |
| F9 | `Apply` with an injected I/O failure on the third op | the first two ops are undone; the tree equals the start |
| F10 | `Revert` when a moved file was edited after `Apply` | stops with exit 3 and the journal path; that file is untouched |
| F11 | project directory already exists / is not a direct child of `tests/` | refused |

The real increments are proven by the build+test step inside `--apply` and by `verify-change.py` on
the moved paths — not by a test that counts moved files.

## Boundaries

- **Always:** one project per increment; dry run first; build **and** test the new project and the
  residual before keeping an increment; land each increment with its `core-split-wiring` changes.
- **Ask first:** the manifest itself (map §7.3 checkpoint) — no `--apply` before the owner has
  reviewed it.
- **Never:** rewrite a namespace or any file's content; add a `ProjectReference` between test
  projects; a second file-mover tool; `git stash`/`reset` around another session's files (the dirty-path
  refusal exists so this never comes up).

## Success criteria

- [ ] F1–F11 green, verified with `.\scripts\verify-change.ps1 -Paths <every changed gk-core/tools/FileMove and gk-core/tests/FusionRpg.FileMove.Tests path> -Session <id>`.
- [ ] Each applied project builds, its moved tests pass under the default profile, and the residual
      stays green.
- [ ] No moved file differs from its source by a single byte (`git diff -M --stat` shows pure renames).
- [ ] Every new csproj's references ⊆ its manifest `references`; no test→test `ProjectReference` exists.
- [ ] After the last increment, a one-subsystem Core test change builds one small project — record the
      `Csc` time with `/clp:PerformanceSummary` against the ideal's projection, as a **reading** in the
      ideal (it was a projection, not a measurement — ideal §"Net, honest verdict").

## Open questions

None for the tool. The grouping is the owner's call at the manifest checkpoint (map §7.3), with the
analyzer's clean-SCC proposal as the default.

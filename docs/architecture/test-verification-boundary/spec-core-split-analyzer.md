# Spec: `core-split-analyzer`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
nothing · R-TV1 step 1 ("a read-only analyzer first", ideal §"If lever 3 is commissioned").

## Objective

R-TV1 authorizes splitting `FusionRpg.Core.Tests` into per-subsystem projects. The ideal forbids
deciding the split by "coincidence of today's folder layout" and names what nobody has measured:
whether the folders are **reference-clean** (ideal, "What this deliberately does not decide", last
two bullets). This tool measures it and proposes a grouping. It mutates nothing.

What it must see, from the project as it is today (`gk-core/tests/FusionRpg.Core.Tests/`: 31 test-code
folders plus `TestSupport/` and `Goldens/`, and 45 root files on this commit — readings):

- test→test symbol references across folders (a helper in `Battle/` used from `Combat/` breaks a split);
- shared inputs every test depends on implicitly: the `[ModuleInitializer]` in
  `gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:43`, the assembly-wide `DisableTestParallelization`
  (`gk-core/tests/FusionRpg.Core.Tests.Shared/AssemblyInfo.cs:6`), `TestSupport/`, and linked sources (`FusionRpg.Core.Tests.csproj:58-61`:
  three Injector files and `DataTestStore.cs`);
- which production and tool assemblies each folder needs (the csproj references Core, Data and nine
  tools, `:24-50`; most folders need a fraction);
- use of Core `internal` symbols (the grant is to one assembly name, `FusionRpg.Core.csproj:18`);
- xUnit collections: a `[CollectionDefinition]` must sit in the same assembly as its users;
- string-keyed inputs a compiler cannot see: `fixtures/…` and `Goldens/…` paths (`:64-66`), tool
  apphost names shelled out to by cold-process tests, and **literal paths into the test project
  itself**. For example, `PassiveTree/GateCounters/GateCounterBoundaryGuardTests.cs:97` reads
  `"gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/PassiveTreeTuningTests.cs"`, which breaks
  the moment that folder moves (map G17);
- location-sensitive code: the files that use `[CallerFilePath]`, most of them to walk `..` to the
  repo root or to `gk-core/tests/fixtures` (25 files, a reading, e.g. `Actions/ActionAdoptionFixtures.cs:18-23`). The split
  keeps them working only because of the depth invariant (map §3.5), and the report is what lets the
  manifest reviewer check it;
- namespace-vs-folder mismatches (25 files, a reading; map G17). The split carries them unchanged,
  but a later `FileMove move` of one of them would rewrite its namespace, so the report lists them;
- where each `VerificationId` and `Category` trait lives (feeds `core-registry-rekey` and the CI
  BalanceGuard step, `gk-core/.github/workflows/ci.yml:176`).

**User:** the owner and whoever writes the split manifest.

## Design

- **New tool** `gk-core/tools/TestSplitAnalyzer/` (net8.0 `Exe`). Separate from `gk-core/tools/FileMove` on purpose:
  `FileMove` is text-only and dependency-free by design (`gk-core/tools/FileMove/MovePlan.cs:42-45`,
  `FileMove.csproj` comment); this job needs a semantic model.
- **Roslyn compiler API only** — `Microsoft.CodeAnalysis.CSharp`, no `Workspaces`/`MSBuildWorkspace`
  (so no `Microsoft.Build.Locator` and no dependency on the installed MSBuild's version). The tool
  reads the csproj as text for `Compile Include` links and `ProjectReference`s, parses every source
  (including linked ones), and builds a `CSharpCompilation` whose metadata references are the DLLs in
  the project's **already built** output directory. Precondition: `dotnet build` of
  `FusionRpg.Core.Tests` in the given configuration; absent output → exit 2 with that message.
- **Candidate units:** each top-level folder is one candidate; each root file is its own candidate
  (they are the ones with no natural home). `TestSupport/`, the bootstrap, `AssemblyInfo.cs` and the
  linked files are classified **shared**, not candidates.
- **Per candidate, report:** files; `[Fact]`/`[Theory]` method count (a reading); outbound references
  to other candidates as `(symbol, declaring file, referencing file:line)`; references to shared;
  required assemblies (from each referenced symbol's containing assembly → maps back to a
  `ProjectReference`); `internal` Core symbols used; collections defined/used; string-literal hits
  for `fixtures/`, `Goldens/`, `FusionRpg.Core.Tests/` and each referenced tool's assembly name;
  `[CallerFilePath]` parameters; declared namespace vs folder-implied namespace; trait values.
- **Blocking findings.** An own-path string literal that crosses candidates is flagged `BLOCKS SPLIT`.
  A move cannot fix it, because split mode never edits content (`core-split-apply` A2). It is fixed
  in its own commit **before** the increment that moves either end, for example by resolving the
  path relative to `[CallerFilePath]` instead of the literal project name.
- **Grouping proposal:** strongly connected components of the candidate reference graph (a cycle must
  share a project); every SCC with no edges into another SCC is **clean**. Proposal = one project per
  clean SCC, named `FusionRpg.Core.<Area>.Tests` from its largest folder, plus a **residual**
  `FusionRpg.Core.Tests` holding everything coupled. Printed as a manifest draft in the
  `core-split-apply` schema; the tool never writes the manifest file.
- **Determinism:** candidates, edges and files sorted ordinally; no timestamps in the JSON body; same
  tree + same build → byte-identical output.

Output: `--format json` (machine) and `--format md` (the owner's review), to stdout or `--out <path>`.

## Commands

```powershell
dotnet build tests\FusionRpg.Core.Tests -c Release
dotnet run --project tools\TestSplitAnalyzer -c Release -- `
    --project tests\FusionRpg.Core.Tests\FusionRpg.Core.Tests.csproj --configuration Release --format md
dotnet run --project tools\TestSplitAnalyzer -c Release -- `
    --project tests\FusionRpg.Core.Tests\FusionRpg.Core.Tests.csproj --configuration Release --format json --out <scratch>\core-split.json
dotnet test tests\FusionRpg.TestSplitAnalyzer.Tests -c Release
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/tools/TestSplitAnalyzer/TestSplitAnalyzer.csproj` | (new) `Exe`, `Microsoft.CodeAnalysis.CSharp` |
| `gk-core/tools/TestSplitAnalyzer/CsprojReader.cs` | (new) links, `ProjectReference`s, `None` content items — text, like `FileMove`'s `AssemblyGraph` |
| `gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs` | (new) symbol walk → candidate edges |
| `gk-core/tools/TestSplitAnalyzer/Grouping.cs` | (new) SCCs, clean/coupled, manifest draft |
| `gk-core/tools/TestSplitAnalyzer/Report.cs` | (new) json/md, sorted |
| `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/` | (new) |
| `gk-core/scripts/verification-boundaries.v1.json` | a `projects` id for the new test project (required by `registry-contract` C2) and one owner boundary over tool + tests (`filemove`'s shape) |
| `.github/workflows/ci.yml` | map §7.1 E3 (approved, R15). In "Restore / test (.NET)", directly after the FileMove pair (`gk-core/.github/workflows/ci.yml:350-351`) and in the same commit as the project, because `CiWiringGuardTests.cs:45-71` fails without it: `dotnet test gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/FusionRpg.TestSplitAnalyzer.Tests.csproj -c Release --verbosity minimal --blame-hang --blame-hang-timeout 10min`, then `if ($LASTEXITCODE -ne 0) { throw "FusionRpg.TestSplitAnalyzer.Tests failed" }`. Not in `release.yml` (map §7.1) |

## Code style

```csharp
// One edge = one fact the manifest reviewer can check by opening the file.
public sealed record CandidateEdge(string From, string To, string Symbol, string DeclaredIn, string UsedAt);

foreach (var id in root.DescendantNodes().OfType<IdentifierNameSyntax>())
{
    if (model.GetSymbolInfo(id).Symbol is not { } symbol) continue;
    var declared = symbol.DeclaringSyntaxReferences.FirstOrDefault()?.SyntaxTree.FilePath;
    if (declared is null) continue;                        // metadata symbol -> assembly requirement instead
    var to = Classify(declared);                           // candidate id, or Shared
    if (to != from) edges.Add(new(from, to, symbol.ToDisplayString(), Rel(declared), Rel(id)));
}
```

## Testing

Synthetic sources compiled **in memory** (`CSharpSyntaxTree.ParseText` over strings, references from
`typeof(object).Assembly` etc.) — no temp directories, no disk (`testing-standard.md` R1/R2):

| # | Fixture | Asserts |
|---|---|---|
| A1 | folder A uses a helper declared in folder B | edge A→B with symbol and both locations |
| A2 | A↔B mutual use | one SCC {A,B}, proposed as one project |
| A3 | A uses only production + shared | A clean |
| A4 | a `[CollectionDefinition]` in A used by B | reported as a cross-candidate collection edge |
| A5 | a string literal `"fixtures/combat/x.json"` in A | content requirement on A |
| A6 | an `internal` production symbol used in A | internals requirement on A |
| A7 | same input twice, shuffled file order | byte-identical JSON |
| A8 | csproj text with `Compile Include … Link=` | linked file classified shared |
| A9 | a string literal `"tests/FusionRpg.Core.Tests/B/x.cs"` in candidate A | own-path requirement on A, `BLOCKS SPLIT` when A ≠ B |
| A10 | a `[CallerFilePath]` parameter in A | listed as location-sensitive |
| A11 | a file in folder `B/C/` declaring namespace `Root.B` | listed as a namespace-vs-folder mismatch |

One smoke run on the real project is a Success criterion, not a test: its outputs are readings.
No test asserts how many folders, files, tests or edges the real project has.

## Boundaries

- **Always:** read-only on the repo; sorted output; every edge carries both locations.
- **Ask first:** adding the `Microsoft.CodeAnalysis.CSharp` package. The ideal names Roslyn ("Build
  on Roslyn/MSBuild's own APIs"), but a new package is still a dependency addition, and no project
  references it today. The `ci.yml` line is approved (R15, map §7.1 E3).
- **Never:** write or edit the manifest; move files; decide the grouping (it proposes; the owner decides —
  ideal: "the tool never decides groupings"); add `MSBuildWorkspace`.

## Success criteria

- [ ] A1–A11 green; the CI line lands with the project and the first CI run is green.
- [ ] One real run over `FusionRpg.Core.Tests` produces the md report, and its clean/coupled
      classification is spot-checked by opening three reported edges.
- [ ] The report lists, for the real project: the shared set, per-candidate required references,
      internal-symbol users, collections, string-keyed inputs, and trait locations.
- [ ] Two runs on the same build produce identical JSON.

## Open questions

None for this module. What the report finds (which folders are coupled) feeds the manifest
checkpoint (map §7.3).

# TVB1.7 — Reference graph: cross-candidate edges, shared set, assemblies, internals, collections

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Roslyn `Compilation` over synthetic sources (no `MSBuildWorkspace`); folder/root-file candidates; `TestSupport/`/bootstrap/`AssemblyInfo.cs`/linked classified shared | `dotnet test tests\FusionRpg.TestSplitAnalyzer.Tests -c Release` | 18/18 (was 16 before this task; +2 net after 2 bugs found+fixed) | `ReferenceGraph.cs`, `ReferenceGraphTests.cs` |
| A1 (edge with symbol + both locations) | `A1_folder_a_uses_a_helper_declared_in_folder_b` | passed | same |
| A4 (cross-candidate collection) | `A4_a_collection_definition_in_a_used_by_b_is_a_cross_candidate_collection_edge` | passed | same |
| A6 (internal Core symbol) | `A6_an_internal_production_symbol_used_in_a_is_reported` (real `InternalsVisibleTo` grant + emitted metadata reference) | passed | same |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/ReferenceGraph.cs,gk-core/tools/TestSplitAnalyzer/TestSplitAnalyzer.csproj,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ReferenceGraphTests.cs -Session summoner-convergence-lane-d2-20260919` | 18/18 passed | plan resolved `testsplitanalyzer-fallback` |

**Two real bugs found by the tests themselves, fixed same commit:**
1. A namespace segment in a `using` directive (e.g. `using Ns.B;`) resolves to an `INamespaceSymbol`
   declared "in" whichever file happens to contain that namespace's first declaration — reported as
   spurious coupling edges (`Ns`, `Ns.B`) with no real manifest-reviewer meaning, since many files
   across many candidates can share one namespace. Fixed: `ReferenceGraph.Build` skips
   `symbol.Kind == SymbolKind.Namespace`.
2. `[Xunit.CollectionDefinition("...")]` (fully qualified) did not match the plain-name check
   (`attr.Name.ToString()` returns `"Xunit.CollectionDefinition"`, not `"CollectionDefinition"`).
   Fixed: `SimpleAttributeName` takes the rightmost identifier of a qualified name, so both the
   qualified and `using Xunit;`-unqualified forms are recognised.

The A1 test asserts the contract (every found edge has the right shape; at least one references
`Helper`) rather than an exact edge count, since `Helper.Do()` is genuinely two real facts (the type
`Helper` and the method `Do`, both declared in the same file) — not a defect to suppress.

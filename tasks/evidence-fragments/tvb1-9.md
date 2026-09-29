# TVB1.9 — Grouping (SCCs) + deterministic json/md report with manifest draft

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| SCCs of the candidate graph (Tarjan); clean = no edges into another SCC | `dotnet test tests\FusionRpg.TestSplitAnalyzer.Tests -c Release` | 32/32 (was 27; +5 this task) | `Grouping.cs`, `GroupingTests.cs` |
| A2 (mutual cycle -> one project) | `A2_a_mutual_cycle_between_a_and_b_is_proposed_as_one_project` | passed | same |
| A3 (no cross-candidate edges -> clean) | `A3_a_candidate_with_no_cross_candidate_edges_is_clean` | passed | same |
| A7 (shuffled input -> byte-identical JSON) | `A7_shuffled_input_order_produces_byte_identical_json` | passed | same |
| One project per clean SCC named from its largest member; residual keeps the rest | `A_clean_multi_member_scc_is_named_from_its_largest_member` | `Big` (20 files) named over `Small` (2 files) | same |
| `--format json\|md`, `--out` | `dotnet run --project tools\TestSplitAnalyzer -- --project tests\FusionRpg.FileMove.Tests\FusionRpg.FileMove.Tests.csproj --configuration Release --format json --out <path>` | valid manifest-draft JSON in `core-split-apply` A1 shape | console |
| Two runs, same build -> identical JSON | same command run twice, `Compare-Object` | `IDENTICAL` | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths gk-core/tools/TestSplitAnalyzer/{Grouping,Report,Program,CsprojReader}.cs,gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/GroupingTests.cs -Session summoner-convergence-lane-d2-20260919` | 32/32 passed | plan resolved `testsplitanalyzer-fallback` |

**One real bug my own test found:** a one-way dependency A->B (no edge back) puts only A in the
residual, not both — B has no outbound edge to anywhere, so B alone is clean regardless of who
depends on it (splitting A away would need a forbidden test-project ProjectReference to B; B has no
such need). My first draft of that test asserted the wrong expectation; fixed the test, not the code.

**`Program.cs` now wires the real analysis** (compilation from the project's build output DLLs +
the analyzer's own trusted-platform-assembly list for framework types, sources parsed in sorted
order for determinism) — `CsprojReader` gained `RootNamespace` extraction for this. The manifest
draft is printed/written, never saved as `gk-core/tests/core-test-projects.v1.json` itself (that file is
authored and owner-reviewed at TVB5.5).

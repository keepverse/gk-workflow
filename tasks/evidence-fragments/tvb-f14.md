# TVB-F14 — the report names the cross-candidate symbol edges

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| before | `TestSplitAnalyzer --project gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj -c Release --format md` | `## Cross-candidate collections (0 — a reading)` was the only cross-candidate section; TVB1.10 reported **0 `BLOCKS SPLIT`** repo-wide, because that class is literal-based | `tasks/evidence-fragments/tvb1-10.md` |
| after | same command | **`## Cross-candidate symbol edges (514 — a reading)`**, e.g. `` `Actions` uses `FusionRpg.Core.Tests.Battle.BattleGoldenTests` from `Battle` (declared at Battle/BattleGoldenTests.cs, used at Actions/BasicAttackAdoptionTests.cs:43) `` | this fragment |
| the section is pinned | `dotnet test gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests -c Release` | `Passed! - Failed: 0, Passed: 38, Skipped: 0, Total: 38` (36 + 2 new `ReportTests` cases: the edges print, and an empty set says `(none)`) | `gk-core/tests/FusionRpg.TestSplitAnalyzer.Tests/ReportTests.cs` |
| the JSON already had them | `Report.ToJson` | `edges` has carried `CandidateEdge(From, To, Symbol, DeclaredIn, UsedAt)` since TVB1.7; only the markdown was missing it | `gk-core/tools/TestSplitAnalyzer/Report.cs` |

**Decision, recorded rather than assumed:** the row asked for the shape "as `BLOCKS SPLIT`". It is printed
as a **reading section** instead, because a cross-candidate symbol edge is not always a blocker — the
manifest's `links` field answers it (`Atoms/EffectSeedFixtureOracle.cs` was linked, not abandoned) and the
SCC grouping already decides which candidates are clean. Making it a hard blocker would fail the tool on
shapes that split perfectly well. What the row needed was to be *visible* in the report a manifest author
reads, and it now is.

The Atoms case the row cites is the worked example: two out-of-folder files
(`Atoms/EffectSeedFixtureOracle.cs`, `World/StructureCatalogTestBootstrap.cs` — a `[ModuleInitializer]`)
that the hand-derived manifest's `include` list had to name, found one revert at a time by the apply gate.

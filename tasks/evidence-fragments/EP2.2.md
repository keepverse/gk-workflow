# EP2.2 — `BuildFavourMeasurer.Measure`: lead and shape histograms over real creatures only

Spec: `docs/architecture/empire-progression/spec-favour-detector.md` ("What is measured"), incl. the
erratum this commit adds for `LeanByPrimary`. All corpora below are synthetic; the real-corpus
reconciliation is EP2.3's, on the committed artifact.

| Criterion | Command | Result | Artifact |
| --- | --- | --- | --- |
| Lead histogram; max lead as per-mille; one dominant lead reads 1000 (tests 1) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildFavourMeasure"` | pass — `One_aptitude_leading_every_species_reports_1000_permille`: 6/6 Onslaught → `MaxLeadPermille` 1000, `MaxLeadAptitude` "Onslaught"; 12 leads spread evenly (catalog read live) → 83 (1000/12) | `gk-core/src/FusionRpg.Core/Creatures/Generation/BuildFavourMeasure.cs` |
| Shape is owner-blind (test 2) | same run | pass — `{Might:600,Vigor:400}` vs `{Vigor:600,Might:400}` share one key `600,400`, count 2, `LargestShapePermille` 1000 | `gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs` (new) |
| Ties are ordinal (test 3) | same run | pass — a 400/400 Vigor/Might tie counts on `Might`; `Vigor` absent | same file |
| Determinism across input order (test 4) | same run | pass — reversed species list and reversed vector list give identical canonical bytes; ends LF, contains no CR | same file |
| `speciesKind: excluded` rows are out of every count; `mimic` is roster | same run | pass — 3 rows (one `excluded` with a 1000‰ vector and deliberately no plan vector) → `SpeciesCount` 2, no Onslaught lead, no Onslaught lean; a `mimic` row counts 1. Envelope: a roster row with no vector **throws** rather than being skipped | same file |
| No exact-vector distinctness member (test 5) | same run | pass — the record's property set is pinned to its 7 declared names and no member contains `Distinct`/`Unique` | same file |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/BuildFavourMeasure.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs,docs/architecture/empire-progression/spec-favour-detector.md -Session empire-progression-20260920` | doc path → `docs-and-assistant-config` (focused): doc-citations 1 document / 7 citations, D1×3 = **0 HIGH**. Both Core paths have no focused boundary → `core-fallback (module)`: `Failed: 4, Passed: 14916, Total: 14920` — the four are the pre-existing ISG-F1 set; Passed rose by exactly this task's 9 tests | `docs/architecture/empire-progression/spec-favour-detector.md` (erratum) |
| Not proved | — | No production host calls `Measure`/`Canonical` yet (EP2.3 wires the generator and the committed artifact); no live/game evidence | — |

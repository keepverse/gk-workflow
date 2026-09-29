# SSH8.4 — a materials current-revision constant — **constant + readers landed, the literal-guard line is the pipeline lane's**

`SocketTuningFiles` gains `Materials = "materials.v4.json"` (the revision those readers already loaded —
this row changes no behaviour, it names what was a literal), `Program.cs` reads it, the seedsmith
`recipegen/brief.py` constant documents itself as its mirror, and `MaterialCorpusTests.TuningJson()` reads
it instead of a literal.

**Not landed:** `every_reader_loads_the_current_materials_revision`, the literal-guard extension — its only
home is `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`, a pipeline-protected path outside
this lane's fence (the same class as SSH6.5, SSH7.1's extension, CAI-guard-1). The row stays OPEN on it.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `SocketTuningFiles` gains the materials constant, and the entry point reads it | `dotnet build gk-core/src/FusionRpg.Server -c Release` | build succeeded; `Program.cs:342` is now `SocketTuningFiles.Materials` where it was the literal |
| the tests that mean the shipped file read the constant | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~MaterialCorpus\|FullyQualifiedName~StrainSpliceGrid"` | **47 passed / 0** |
| the wider blast radius | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" -c Release`; `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **15103 passed / 0**; **PASS — 3978 entries / 1013 files / 2589 warnings** (the constant names the same file, so nothing moves) |
| the existing literal guard still passes | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"` | **2 passed / 0** — the sockets half is untouched; the materials extension is the pipeline lane's |
| **`every_reader_loads_the_current_materials_revision`** | — | **NOT DONE — blocked**: protected path. Recommended shape: the same regex widened to `materials\.v[0-9]+\.json`, `SocketTuningFiles.cs` allowlisted as the constant's own file, comment lines exempt as they already are; `recipegen/brief.py` is Python, which that guard does not scan, so its literal is covered only if the SSH5.6-style Python scan is widened too |

## Not proved / open

- The guard extension above — the row's one unmet line, routed to the pipeline lane.
- `ItemWorkbench.cs` does not read a materials path at all (it receives the catalog by injection); the
  only C# reader is the boot, and the only Python reader is `recipegen/brief.py`. Recorded so a reviewer
  does not look for a third.
- Prose that still says `materials.v1.json`/`v2` in `MaterialRecipeCatalog.cs:437`,
  `RarityBudgetKeys.cs:41` and `recipegen/repair.py:5` is stale-looking history: SSH5.10-P2's own rule is
  that a doc comment naming an old revision as history is prose, not a reader, and the guard exempts
  comment lines. Left for whichever program next touches those files.

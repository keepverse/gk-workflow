# Evidence — party-dungeon D4.31's sibling-collision half (lane `pd-d3`, 2026-09-23)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| spec §8's "StS sibling rule" — the caller half D4.31 named as not built | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DomainEncounterCoverageTests"` | `Passed: 11, Failed: 0` (4 prior + 7 new) | `gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainEncounterCoverageTests.cs` |
| the group key is load-bearing, both halves | same filter, mutating the key to `"{kind}"` then to `"{row}"` | `Failed: 3` each time, by name; restored byte-identical | — |
| no regression across the module | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve"` | `Passed: 1746, Failed: 0` (1739 + 7) | — |
| DAL boundary (Core only) | `pwsh -NoProfile -File scripts/guard-dal.ps1` | `DAL GUARD OK` | — |
| no new magic number / overflow | `python gk-core/scripts/audit-magic-numbers.py --domain dungeon` · `python gk-core/scripts/audit-overflow.py` | 0 findings · 0 critical | — |

**What was built, and the one-owner split it respects**

`DomainEncounterCoverage.SiblingCollisions(graph, …)` is the CALLER half of the already-shipped
`EncounterCoverage.SiblingCollisions` (D2.7). The primitive owns the "did two cells come out identical"
comparison and reads the caller's own grouping; this method owns only what needs a rolled graph — which
facts are siblings (grouped `"{row}:{kind}"`) and what cell each one's own room draw produces
(`DelveStreams.Room(row, col)` off the delve seed, exactly the caller derivation spec §9 names). It is
deliberately not folded into `Report`, which samples each room independently on its own derived seed and
never rolls a graph.

**NOT proved**

- D4.31's own acceptance line — "the cell-coverage metric passes per domain" — still FAILS and was not
  touched. Its blocker is exact and named in the row: **F1** in the same todo (`threat-audit` over the
  species anchors lacking a `threatBand`, owned by `creature-seed` module 7). `SlotFilter.Candidates`
  refuses eagerly on any anchor with a null `ThreatBand`, so all six real domains still report zero
  distinct cells. The row therefore stays `[ ]`; this pass built one of its named gaps, not its acceptance.
- No real-content graph was found where a sibling collision actually FIRES: the real `domain.fire-001`
  graph's own encounter draws all refuse on the same classified-corpus thinness, so the real-content test
  asserts determinism and key validity, not a positive finding. The positive case is proved against a
  hand-built graph whose anchor can only produce one cell.
- No live/injector probe: this is a pure-Core function with no production host yet (the import-time
  caller is `domain-catalog`'s own importer, another program's task).

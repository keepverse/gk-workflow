# TB-H1 — threatBand coverage, reported as a before/after reading (2 of 3 boxes; box 3 is party-dungeon's)

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` TB-H1 (received from `party-dungeon` F1 via BCU4.6, 2026-09-20).
Added: `gk-core/tests/FusionRpg.Core.Tests/Delve/Encounter/ThreatBandCorpusReconciliationTests.cs`.
**The row is NOT closed:** its first two boxes are satisfied and evidenced here; the third belongs to
`party-dungeon` and is named below.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Coverage as a before/after reading | `python - <<'PY' … walk gk-data/packs/fusion/data/seed/creatures/species/**, count threatBand coverage … PY` | **BEFORE (the row's own 2026-09-20 reading): 721 of 906 anchors lacked a `threatBand`. AFTER (measured 2026-09-23): 904 of 904 anchors carry a resolved one — 1000‰; key absent/null 0, literal `"unresolved"` 0, so the unclassified remainder is ZERO and no reason is owed for it.** By side: plant 677, zombie 227, all resolved | — |
| Every produced rung maps to a real table row | `python … same run` + `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~ThreatBandCorpusReconciliation"` | all **10** rungs of `creature-threat.v1.json` are populated (`nuisance 224 · pest 60 · marauder 74 · raider 81 · warden 87 · scourge 70 · tyrant 101 · harbinger 77 · cataclysm 55 · calamity 75`), **0 orphan rungs** and **0 empty rungs**; the new test asserts it over the real corpus and resolves each rung through `OffsetFor` (the same reader the Θ path takes) — **Passed! 3/3, 151 ms** | `ThreatBandCorpusReconciliationTests.cs` |
| A rung with no row fails loudly, never classifying to nothing | same test run — `A_rung_with_no_row_is_refused_loudly_by_the_corpus_join` | `ConcreteAnchor.From` with `threatBand: "not-a-rung"` throws `InvalidOperationException` naming **both** the rung and `creature-threat.v1.json`; the sibling test pins the OTHER case (an absent field takes the table's sanctioned `inferredDefaultRung` offset instead) so the two cannot be confused | same |
| How each rung was chosen (the honest-provenance reading) | `python … same run` | `scored 719 · high 126 · split 49 · deterministic-fallback 10` — i.e. 10 of 904 rungs are honestly-stamped deterministic fallbacks, not real classifications (the quality report's own provenance split already prints this) | — |
| No regression in the rest of Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **Failed! — 1 failed, 9611 passed, Total 9612, 1 m 27 s**; the single red is **CS-R3**, another program's file, not this change | see below |
| Static guards | `guard-magic-numbers` · `guard-population-pin` · `guard-test-substrate` | `M1=0 M2=0 M3=0 M4=0` · `total 0 finding(s)` · `TEST SUBSTRATE GUARD OK` | — |

## What blocks this row (exactly)

**Box 3 — "`party-dungeon` F1 can close on a real six-domain run, not on this row's own say-so" — is
`party-dungeon`'s own acceptance, not this lane's.** Nothing further can be done here: the coverage it
needed is now complete and asserted (the two boxes above), and the six-domain run is a `party-dungeon`
execution against their own resolver. So this row stays open on that single box, owned by that program —
which is what the box's own wording asks for ("not on this row's own say-so").

## Findings filed from this run

- **CS-R3 (filed in `tasks/creature-seed-todo.md`) — the action-layer purity guard is red at the
  integration tip.** `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionsPurityGuardTests.cs:35` fails with
  `Cost/ExhaustionEdgeDetector.cs:85 → .Values`: `WindowCount`'s getter iterates `_byPtr.Values`, and the
  guard forbids dictionary enumeration in the action layer because iteration order is not a contract
  (insertion/hash dependent). Introduced by `467cfa058 feat(lawn): LW1.3 exhaustion as an edge-triggered
  event…`, so the owner is the **lawn** program (LW1.3), not this lane. This lane's diff over
  `gk-core/src/FusionRpg.Core/Actions/**` is empty; the only file it added in this increment is the new test above.

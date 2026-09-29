# Task 5 — `AnchorRow.rank` + expansion

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 5. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §1.
Edited: `Generation/AnchorRow.cs` (nullable `Rank` + reader), `Generation/SpeciesExpander.cs` (`ResolveRank`,
resolved after Θ/P(Θ)), `Generation/ConcreteSpecies.cs` (the row field rank lands in),
`gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesExpanderTests.cs`, `…/AnchorRowReaderTests.cs`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| nullable `rank` on `AnchorRow`, `Rarity` nullability untouched | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~AnchorRowReader"` | green — `rank` reads verbatim; `"unresolved"` → `null`; an absent key → `null` (§1.7's sentinel mapping); `Rarity` still non-nullable and unchanged | `AnchorRowReaderTests.cs` |
| `SpeciesExpander` resolves rank post-expansion | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~SpeciesExpand"` | **Passed! — Failed 0, Passed 25, Total 25, 70 ms**; the real `Peashooter` anchor expands to the tuning table's own cell for its pair | `SpeciesExpanderTests.cs` |
| Θ path byte-identical | same run — `Rank_never_moves_theta_pTheta_or_a_single_magnitude` | the SAME anchor with `Rank = null` and `Rank = "cultivated"` expands to identical `Theta`, `PTheta` and `Magnitudes` (rank is resolved after both, read by no channel) | same |
| Unknown id refuses, never reads as skipped | same run — `An_unknown_rank_id_refuses_rather_than_reading_as_skipped` | throws naming `'legendary'` + `not a known CreatureRank` | same |
| The concrete tree did not move | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | `--check: clean, 904 species match …\data\generated\creatures` — `Canonical` is an explicit dictionary, so the new row field is not serialized until Task 6 wires it | — |
| Anchor/row/anchor-adjacent Core tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~SpeciesExpand\|FullyQualifiedName~AnchorRow\|FullyQualifiedName~CreatureRank\|FullyQualifiedName~ConcreteSpecies\|FullyQualifiedName~SpeciesRollPreview\|FullyQualifiedName~EligibilityAxis"` | **Passed! — Failed 0, Passed 103, Total 103, 19 s** | — |
| Task 1-2 files still green | included in the same run (`~CreatureRank` 29/29 within the 103) | green | — |
| Static guards | `pwsh -NoProfile -File scripts/guard-population-pin.ps1` · `guard-test-substrate.py` · `guard-magic-numbers.ps1` | `total 0 finding(s)` · `TEST SUBSTRATE GUARD OK` · `M1=0 M2=0 M3=0 M4=0` | — |

## NOT proved / decisions the manager may overrule

- **"`SpeciesExpander` computes rank": implemented as resolving the anchor's DERIVED rank id, not as a
  second grid lookup.** `AnchorRow.Rank` is the C# boundary of seedsmith's `derive_rank` (spec §1.7), and
  `SpeciesKind` is the exact precedent for a DERIVED anchor field riding through. Re-deriving in C# would
  mean two derivation sites reading the same table — the "second source of truth" this program's own
  one-authority rule exists to prevent. The ordering requirement IS met: `ResolveRank` runs after Θ/P(Θ),
  so rank is excluded from both by construction. **If the intent was a C# grid recompute, say so and this
  becomes a `rankTuning` parameter on `Expand` plus 5 tool call sites** — a mechanical change, deliberately
  not made on a guess.
- **"unresolved reporting covers rank-skipped" is satisfied as `ConcreteSpecies.Rank == null`, not by
  widening `UnresolvedFields`.** `UnresolvedFields` is a BATCH-SKIP list (`EncounterCorpusBuilder:45`,
  `CreatureSpeciesBuildPlanGen`, `CreatureSpeciesImport`, `RealCorpusFixture` …) and the spec's own Never
  list forbids "blocking generation on rank (skip, don't fabricate)" — adding `rank` there would make a
  rank-skipped species un-generatable, contradicting that line and flipping every synthetic fixture anchor.
  The skip signal is available to Task 9's coverage line as a null rank.
- `ConcreteSpecies.Rank` (an init-only property, additive) is added here because rank otherwise has nowhere
  to land in this task's own output; the serializer key, the seed reader and the `gk-data/packs/fusion/data/generated/**` regen
  remain Task 6's, which is why `--check` is still clean.
- The corpus has 0 rank-skipped anchors, so "skipped → null" is proven by the reader/expander tests, not by
  a real row.

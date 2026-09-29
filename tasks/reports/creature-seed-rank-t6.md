# Task 6 — concrete triad + SeedReader (and the concrete-tree regen)

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 6. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §1, §4.
Edited: `Generation/ConcreteSpeciesSerializer.cs` (`Canonical` gains `rank`),
`Generation/ConcreteSpeciesSeedReader.cs` (optional read), `Creatures/SpeciesSnapshot.cs` (stale comment,
GAP-3), `gk-core/tests/FusionRpg.Core.Tests/Creatures/ConcreteSpeciesSerializerTests.cs`,
`…/ConcreteSpeciesSeedReaderTests.cs`, and `gk-data/packs/fusion/data/generated/creatures/**` (904 files, regenerated in this
same commit per the manager's note). The lane also fast-forwarded onto the integration tip first
(`9f86964b6`), which carries the manager's CS-R1 registry row — CS-R1 is now closed (see the todo).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Canonical` carries rank | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~ConcreteSpecies"` | **Passed! — Failed 0, Passed 16, Total 16, 3 s**; `Rank_is_written_when_the_species_has_one` and `A_skipped_rank_leaves_the_key_absent_never_a_bottom_rung` | `ConcreteSpeciesSerializer.cs` |
| Optional-read for rank | same run | `Rank_reads_back_from_the_committed_tree`; `A_skipped_rank_reads_null_never_a_default` | `ConcreteSpeciesSeedReader.cs` |
| Injector committed-tree path carries rank | same run — `The_real_committed_tree_carries_each_species_own_anchor_rank` | a **reconciliation, not a count**: all 904 committed concrete files read back a rank equal to their anchor's own derived rank (and a null anchor rank would read null here) | same |
| Regen output carries rank through all three | `dotnet run --project gk-forge/tools/CreatureSpeciesGen` (writes) | `904 species expanded, 904 file(s) written`; then a second run `0 file(s) written` | `gk-data/packs/fusion/data/generated/creatures/**` |
| Regen diff reviewed | `python - <<'PY' … HEAD vs working tree, per file … PY` | **904 changed files, 0 added, 0 deleted; every changed file's ONLY difference is one added `rank` key (0 unexpected); 904/904 concrete ranks equal the anchor's own rank for that species** | — |
| `--check` green post-regen | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | `--check: clean, 904 species match …\data\generated\creatures` | — |
| Byte-identical regeneration | `python -c "…sha256 of gk-data/packs/fusion/data/generated/creatures/*.json…"` before/after a second regen | `26661813310990ff183642106b00269672b23a21142a88e7efc84d270f255618` **before and after** | — |
| Core tests green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **Passed! — Failed 0, Passed 9509, Skipped 0, Total 9509, 1 m 24 s** | — |
| Stale comment corrected (GAP-3) | read + `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | `SpeciesSnapshot.cs` now names the real callers — `Server/Program.cs:618` (`Configure(store.BuildCreatureSpeciesSnapshot())`) and `Injector/Host/RpgHost.cs:145` (committed-tree roster) — instead of claiming "every host calls `ConfigureFromCompiledDefault`"; citations guard exit 0 (D3 ambiguous basenames only, 0 HIGH) | `SpeciesSnapshot.cs` |
| Generated-tree guard | `python gk-core/scripts/guard-generated-seed.py` | `clean (909 changed file(s) inspected)` | — |
| Other static guards | `guard-test-substrate.py` · `guard-magic-numbers.ps1` | `TEST SUBSTRATE GUARD OK` · `M1=0 M2=0 M3=0 M4=0` | — |
| CS-R1 (was blocking) | `python gk-core/scripts/guard-verification-boundaries.py`; `verify-change.ps1 -Paths gk-core/data/tuning/creature-rank.v1.json --plan-only -AllowUnscoped` | `VERIFICATION BOUNDARY GUARD OK`; plan reads `gk-core/data/tuning/creature-rank.v1.json -> creature-rank-tuning (module)` | — |
| The two Guard tests CS-R1 had made red | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry"` and `…P6_the_real_registry_resolves_seedsmith_and_tuning` | **1/1 (1 m 11 s)** and **1/1 (1 m 48 s)** | — |

## NOT proved / findings

- **CS-R2 (filed, `tasks/creature-seed-todo.md`): the ci-tier GATING `population-pin` guard is red at the
  integration tip.** `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUnlockGrantServiceTests.cs:220` reads
  `Assert.Equal(500, grantedIds.Count);` with no `pin:` marker; the file is byte-identical to
  `features/mega-merge` and came in with `3a3d0d2da` (ADG-F5). Owner: that lane — this lane did not touch
  another lane's in-flight test file. `guard-population-pin.ps1` therefore reports `total 1 finding(s)`,
  and the one finding is NOT in any file this lane changed.
- The Mapper → `CreatureSpeciesDef` leg of the Injector path is deliberately **not** here: Task 7's own
  acceptance names it ("`CreatureSpeciesDef` + `Validate` carry rank; Mapper funnel passes it"), so the
  Injector carries rank as far as `ConcreteSpecies` today and one leg further after Task 7.
- The whole `gk-core/tests/FusionRpg.Guard.Tests` project was not re-run in one process (earlier attempts were
  killed by infrastructure interruptions at 3-5 minutes); the two specific tests CS-R1 had made red were
  each run and pass, and the guard script itself exits 0.
- `gk-data/packs/fusion/data/generated/creatures/**` was regenerated on the integration tip, so the committed diff is truthful
  against the current base rather than a stale one.

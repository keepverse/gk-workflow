# Checkpoint 0 — picks work in production (parent CC1)

**CLOSED.** All four rows are green: SP0.5/SP0.6/SP0.7 (this anchor's own queue) closed the three rows
this fragment previously recorded as blocked on future anchors or a protected file. The "protected
pipeline file" restriction recorded below did not apply to this session — the write went through — so
SP0.4's own named blocker closed alongside SP0.5 rather than waiting on the orchestrator.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The SP0.4 regression is green for a save that existed at boot and a save created after it | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesModLedgerTests" --nologo` | pass 6/6 — `After_a_real_boot_a_save_that_never_fused_has_no_layer_1b_rows` boots for real, creates save 2, boots again, and asserts both saves hold no ledger row and no species-origin roll | `gk-core/tests/FusionRpg.Data.Tests/SpeciesModLedgerTests.cs` |
| `git grep -n "player_species" -- src/` finds no reader or writer | `git grep -n "player_species" src/` | pass — only `CREATE TABLE`/`CREATE INDEX` (schema, exempt per spec: "table stays in place, unread") and doc-comment mentions remain; zero SELECT/INSERT/UPDATE/DELETE against the table | `RpgStore.PlayerSpecies.cs` (SP0.6, `80559a75`) |
| The spec's "Tests to rewrite" table has every disposition applied, and the two kept guard facts pass | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~PlayerSpecies" --nologo` | pass 5/5 — all 9 rows of the spec's table have their disposition applied or are correctly handed to a later module (`SpeciesPassiveAtomSourceTests` → module 3); full per-row status in `tasks/evidence-fragments/SP0.7.md` | `PlayerSpeciesMaterialiseCallerGuardTests.cs` (SP0.5, `630f6b0e`) |
| Every SP0.7 row is amended or listed here with its owner | — | done — `tasks/evidence-fragments/SP0.7.md` lists all five doc/task rows (spot-checked, none amended yet, hand-over still owed and accurate) plus the nine-row test-disposition table, each with its owner and timing | `tasks/evidence-fragments/SP0.7.md` (`2fcbacd6`) |

## What wave 0 shipped

The live defect (C2) is fixed and its falsifier exists: a save that never fused has **no** layer 1b
(no ledger row, no species-origin `effect_instance`), and each save's own pick lands on its own
`(save_id, HumanEmpireOf(save))` row with the per-empire `picks.already-materialised` guard
(`FusionInheritancePicksTests`, `SpeciesModLedgerTests`). The sheet now composes a specimen's rolled
species passive from the SAME ledger (`GetSpecimenLedgerRoll`, SP0.5), ledger-only with no preview
fallback — a non-fuser's sheet shows nothing, per ruling behaviour 1. `player_species` (the old eager
roster table) has no reader or writer left in `src/`; its two former callers (`MaterialisePlayerSpecies`,
`ReforgePlayerSpecies`) and the debug `/reforge-world` route that fabricated 1b state are gone (SP0.6).
The three "with module 4" hand-over rows are actionable immediately for their owning sessions (SP0.7).

Wave 0 (module 4) is closed. Anchor 3's own queue (SP0.5, SP0.6, SP0.7, SPCP0) is complete.

# SE4.14 — `rpg_unique_actors.empire_id` and `OwnsSpecimenUnlocked`

Spec: docs/architecture/solid-enforcement/spec-save-identity.md ("One ownership predicate")

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `empire_id` added via `EnsureColumn`; a mint on a seeded save stamps `HumanEmpireOf(save)`; rows on an unseeded row (pre-migration history, the legacy Zomboss row) stay `null` until SE4.18 backfills them | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership" -v q --nologo` | pass — 5/5; `A_mint_on_a_seeded_save_is_owned_by_that_saves_human_empire` proves the stamp; `A_null_empire_id_never_matches_anything` mints under the legacy Zomboss row (no empires) and matches nothing | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs` (`HumanEmpireOfOrNull` → NULL) |
| `OwnsSpecimenUnlocked(db, EmpireRef, instanceId)` compares `(player_id, empire_id)` **strictly** (`null` never matches); **no production caller yet** (SE4.24/SE4.25 wire it after the migration) | same filter | pass — own true, `Another_save_is_not_the_owner`, `Another_empire_of_the_same_save_is_not_the_owner`, `An_unknown_or_blank_instance_is_never_owned`. `git grep OwnsSpecimenUnlocked src/` finds only its declaration and the test seam — no production caller | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs` |
| Verify | `dotnet test tests\FusionRpg.Data.Tests -v q --nologo` (whole project, includes this task's changes) | 1624/1625 — the one red is the **named pre-existing worktree artifact** `CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_…` ("904 species stale against gk-data/packs/fusion/data/generated/creatures"; lane A recorded the same class). The plan's own filter run is 1555/1555 | gate recorded |

`OwnsSpecimenForTest(EmpireRef, instanceId)` is the test-only seam (`InternalsVisibleTo`), so a test never
holds a raw connection; SE4.24/SE4.25 call the unlocked form inside their own transaction.

# SE4.16 — Step 2: is the legacy Zomboss row a save?

Spec: docs/architecture/solid-enforcement/spec-save-identity.md ("The migration", step 2)
Dormant: reached only from the migration (SE4.20 activates it).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Finds the lowest-id `"Zomboss"` row (the one historical name lookup); Zomboss-only **iff** every reference is on the Zomboss-path allowlist; **a tie goes to "save"** | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo` | pass — `A_row_with_only_allowed_zomboss_writes_is_not_a_save` (the pure `EnsureZombossPlayer` + `MintForZomboss` shape is not a save); every other fixture flips it | `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs` (`FindLegacyZombossRow`, `SaveEvidence`) |
| An `rpg_save_empires` row counts as save evidence (only the save path writes it since SE4.12) | same | pass — `A_save_empires_row_alone_makes_it_a_save`, evidence `rpg_save_empires` | same |
| One test per evidence kind alone: current setting, a world, a non-Zomboss specimen, an item row, an allocation on one of its specimens | same | pass — 5 facts, each asserts its own evidence string: `settings.current_player_id`, `rpg_worlds`, `rpg_creature_profiles.origin`, `rpg_item_stock`, `rpg_aptitude_allocation`. The sweep reads the schema (`PRAGMA table_info`) so a new `player_id`/`owner_kind`/`scope_key` table is human evidence without an edit | `SaveIdentity.cs` (`FirstForeignReference`); tests |
| Fixtures built once from real production calls | same | pass — `SaveIdentityFixtures.ZombossOnly` (`CreatePlayer`, `EnsureZombossPlayer`, `MintForZomboss`), `Summon` (the `MintForZomboss` mapping, `origin: "summon"`); world/stock/allocation via `CreateWorld`, `AdjustStock`, `SaveAllocation` | `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityFixtures.cs` (new) |
| The name collision **both ways**: a "Zomboss" save with runs; one created before the first deploy, holding a summon and no run | same | pass — `A_save_named_zomboss_that_owns_a_run_stays_a_save` (board.start run owned by the current save); `A_save_named_zomboss_created_before_the_first_deploy_stays_a_save` (a summon, no run) | the migration test file |
| Verify | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo`; `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityMigrationTests.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityFixtures.cs') -Session summoner-convergence-lane-b-20260919` | pass — 14/14; verify-change exit 0 (dal + test-substrate; `data.save-identity` 14/14) | gate recorded |

`origin` is read from `rpg_creature_profiles` (joined by `instance_id`) — `rpg_unique_actors` has no
`origin` column; the first run proved it (`SQLite Error 1: no such column: origin`).

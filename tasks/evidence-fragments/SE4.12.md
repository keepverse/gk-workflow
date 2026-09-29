# SE4.12 — `rpg_save_empires`, the one seeder, `HumanEmpireOf` / `EmpiresOf` / `IsLiveSave`

Spec: docs/architecture/solid-enforcement/spec-save-identity.md

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Table as specced; **one** `SeedSaveEmpiresUnlocked(db, save)` called by `SeedPlayerIfEmpty` and by `CreatePlayer` in the same transaction as the row, and idempotently for the current save at `Init` and on `SetCurrentPlayer`; `EnsureZombossPlayer`'s row is created **without** empires | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveEmpires" -v q --nologo` | pass — 6/6; `Seeding_is_idempotent_across_a_save_switch` re-seeds three times and `Zomboss_is_found_or_created_without_empires` asserts no rows, `A_save_with_no_seeded_empires_throws_rather_than_guessing_dave` the refusal | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs` |
| `HumanEmpireOf` reads the `human` row and throws `SaveEmpiresNotSeeded` on an unseeded save (never guesses `"dave"`); `players.archived_utc` added via `EnsureColumn`; `IsLiveSave` = exists and not archived | same filter | pass — `Assert.Throws<SaveEmpiresNotSeeded>`, `Is_live_save_is_true_for_a_real_save_and_false_for_a_missing_one` | `RpgStore.cs` (`EnsureSaveEmpiresSchemaUnlocked` + `EnsureColumn` in `Init`) |
| Contract test: every seeded save has exactly one `human` empire; a fresh boot yields save 1 with both registry empires and **no** Zomboss player row | same filter | pass — `Every_save_has_exactly_one_human_empire`, `A_fresh_boot_has_save_1_with_the_registry_empires_and_no_zomboss_player_row`. No test asserts a count of empires | `gk-core/tests/FusionRpg.Data.Tests/Saves/SaveEmpiresStoreTests.cs` |
| `guard-dal` · `guard-test-substrate` · path-owned verification | `.\scripts\guard-dal.ps1` · `python gk-core/scripts/guard-test-substrate.py` · `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Saves/NewSaveEmpiresHub.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SaveEmpires.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj,gk-core/tests/FusionRpg.Data.Tests/Saves/SaveEmpiresStoreTests.cs,gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs,tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs,gk-core/tests/FusionRpg.Server.Tests/CommanderDirectoryTestBootstrap.cs -Session summoner-convergence-lane-b-20260919 -PlanOnly` | both guards OK; `-PlanOnly` exit 0, every path one owner (core + data projects + the dal/test-substrate guards). Run directly: the whole Data project `-c Release --filter "Category!=DiskSemantics&Category!=Heavy"` → **1553/1553** | gate recorded |

Host wiring: `Program.cs` reads `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json` into `NewSaveEmpiresHub`
**before** `store.Init()` (Core never touches a path), plus a server content-copy rule for `gk-data/packs/fusion/data/seed/saves/**`.
The four test bootstraps (Core, Data, Server, E2E) configure the same hub.

## Review fix — no host can reach `Init` unconfigured (manager review, blocking)

The first revision configured the hub in `Program.cs` and three test bootstraps, and **missed
`gk-core/tests/FusionRpg.E2E.Tests`**: `RpgApiFactory.SeedSpeciesRoster` builds its own `RpgStore` and calls `Init`
before `Program.cs` runs, so 225/226 E2E tests failed in the factory with `NewSaveEmpiresHub.Configure(...)
has not run`. Fixed in two parts:

- **The store resolves the registry itself** (`RpgStore.ResolveNewSaveEmpires`): the configured hub, else the
  authored file found by `SeedImportRunner.FindUp` walking up from the running image — the same lookup every
  other seed reader in `FusionRpg.Data` already uses. No hardcoded fallback: a missing file throws naming the
  path. That makes the miss impossible for *every* host, including the eleven `tools/*` programs that
  construct a store and `Init` it (`AlmanacSeedBackfill`, `AtomImporter`, `CreatureCatalogGen`,
  `CreatureCorpusDump`, `CreatureCorpusEmit`, `CreatureRecipeDistributionIndex`,
  `CreatureRecipeReconcileInput`, `CreatureSpeciesImport`, `ProveHubCombat`, …) and `Guard.Tests`' planted
  probe (a string, never executed). `RpgHost` never seeds: the injector constructs no `RpgStore`.
- **E2E's bootstrap now configures it too** (and the commander directory), for explicitness.
- **Guard test**: `NewSaveEmpiresHostWiringTests.A_host_that_never_configured_the_hub_still_boots_and_seeds_from_the_authored_file`
  resets the hub, builds a store, and asserts the save resolves — the falsifier for this exact miss.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Whole E2E project (not a filter) | `dotnet test tests\FusionRpg.E2E.Tests -v q --nologo` | pass — **226/226**, exit 0 (was 1/226 before this fix) | — |
| Whole Server project | `dotnet test tests\FusionRpg.Server.Tests -v q --nologo` | pass — **552/552**, exit 0 | — |
| Whole Data project | `dotnet test tests\FusionRpg.Data.Tests -v q --nologo` | 1624/1625 — the one red is the **named pre-existing worktree artifact** `CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_…`: the tool refuses with *"904 species stale against gk-data/packs/fusion/data/generated/creatures"* (the committed generated tree is stale in a worktree; lane A recorded the same class). The plan's own `Category` filter excludes it, and the filtered run is 1555/1555 | — |
| The host-wiring guard test | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~NewSaveEmpiresHostWiring" -v q --nologo` | pass — 1/1 | `gk-core/tests/FusionRpg.Data.Tests/Saves/NewSaveEmpiresHostWiringTests.cs` |

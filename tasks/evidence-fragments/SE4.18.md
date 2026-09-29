# SE4.18 — Step 5: `empire_id` backfill and legacy Zomboss specimens re-homed by provenance

Spec: docs/architecture/solid-enforcement/spec-save-identity.md (step 5)
Dormant: reached only from the migration (SE4.20 activates it).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every save's own specimens get `HumanEmpireOf(save)` whatever their `origin` (counted); the backfill **sets** every row, not only nulls | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo` | pass — `A_saves_own_specimen_gets_its_human_empire_whatever_its_origin` (a `Zomboss`-named save's `origin='zomboss'` specimen is the human's); the UPDATE runs over every row of every save, no `IS NULL` filter | `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs` (`BackfillSpecimenEmpires`) |
| A Zomboss-only row's specimens get `zomboss` and a save by (a) match provenance (specimen, lawn session or lawn-XP receipt `match_key` → `runs`), (b) the only save, else (c) stay `Retired` on the legacy row, ids in the report | same | pass — `A_lawn_session_provenance_rehomes_to_the_runs_save` (deployed specimen, real `TryBeginUniqueDeploy`/`TryAckUniqueSpawn`); `A_lawn_xp_receipt_provenance_rehomes_after_the_session_and_column_are_gone` (session gone and column cleared; only the receipt names the match); `One_save_and_no_provenance_rehomes_to_that_save` (rule b); `Two_saves_and_no_provenance_retire_on_the_legacy_row` (rule c: `player_id` stays, `empire_id='zomboss'`, phase `Retired`). Report carries `rehomedByProvenance`, `rehomedByOnlySave`, `unattributedSpecimenIds` | same |
| Re-homing moves `rpg_unique_lawn_sessions` / `rpg_unique_actor_recovery` with the specimen and releases its legacy contract (`bound = 0`); nothing deleted | same | pass — `Provenance_survives_the_sweep_and_moves_the_session_with_the_specimen` (session's `player_id` follows the specimen); `A_rehomed_specimens_legacy_contract_is_released` (`bound` 1 → 0, `released_utc` set). No DELETE anywhere in step 5 | same |
| Provenance survives the sweep: an `ActiveBound` specimen of an open run is attributed **before** `SweepStaleActiveBoundUnlocked` clears its `match_key` | same | pass — the same sweep fact: after `Migrate` the session moved while the specimen was `ActiveBound`; `_store.CloseAbandonedRunsAndSweep()` afterwards leaves it on the run's save | same |
| Verify | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo`; `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityMigrationTests.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityFixtures.cs') -Session summoner-convergence-lane-b-20260919` | pass — 25/25; verify-change exit 0 (dal + test-substrate; `data.save-identity` 25/25) | gate recorded |

The receipt row in that one fixture is inserted directly (`RecoverToRosterKeepingReceipt`): the award that
writes it (`AwardUniqueLawnKillUnlocked`) is tuning-gated on `specimenLawnKill`, which this assembly's
test bootstrap leaves at 0. The migration's input is the row; the session and column branches are
exercised through real production calls.

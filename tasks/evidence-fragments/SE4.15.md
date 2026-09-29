# SE4.15 — `SaveIdentity.Migrate`: gate, backup, one transaction, marker

Spec: docs/architecture/solid-enforcement/spec-save-identity.md ("The migration", steps 0, 1, 7)
Dormant by design: nothing in `Init` calls it until SE4.20 (parent H2 / ruling R27).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Step 0 gate: marker present → return, a second run is a no-op | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo` | pass — 5/5, run 6× consecutively; `A_memory_store_skips_the_backup_and_writes_the_marker_once` runs twice, second returns false | `gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs` |
| Step 1: `VACUUM INTO` a **new, never-reused** `.bak` before any write; memory skips it; two attempts share a millisecond → second gets a nudged stamp | same | pass — `The_backup_exists_before_the_first_write_and_a_second_attempt_never_reuses_it`: after an injected failure the `.bak` exists and the marker does not; a second attempt yields 2 `.bak`s and the first is byte-identical | `SaveIdentityBackupDiskTests.cs` (`DiskSemantics`) |
| A failed backup writes nothing and propagates (⇒ `Init` refuses to start) | same | pass — `A_failed_backup_writes_nothing_and_propagates`: no marker, no `.bak`, `InvalidOperationException` escapes `Migrate`. The boot-refusal assertion itself is SE4.20's (no `Init` caller yet) | same |
| Steps 2–7 in one transaction whose **last** statement is the marker with the JSON report, mirrored to console; injected failure leaves marker/schema/rows unchanged | same | pass — `An_injected_failure_leaves_no_marker_and_a_later_run_still_works`; the failure injector fires between the steps and the marker write | `SaveIdentity.cs` |
| Verify | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SaveIdentity" --nologo`; `python gk-core/scripts/guard-test-substrate.py`; `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/Migrations/SaveIdentity.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityMigrationTests.cs','gk-core/tests/FusionRpg.Data.Tests/Saves/SaveIdentityBackupDiskTests.cs','gk-core/scripts/verification-boundaries.v1.json') -Session summoner-convergence-lane-b-20260919` | pass — 5/5; guard OK; verify-change exit 0 (dal + test-substrate; `data.save-identity` 5/5; `guard.verification-boundaries` 14/14) | gate recorded |

Boundary repair (in the same commit): these paths matched `data-fallback` (whole Data project, >600 s, over
the agent cap). Added owner `data-save-identity` → `data.save-identity`, the focused boundary they need
(`gk-core/scripts/verification-boundaries.v1.json`; `guard-verification-boundaries.py` OK).
Flake fix found by rerunning: the two failure injectors were process-wide statics and the two classes ran in
parallel; both shared the `save-identity-migration` collection as a stopgap. Backup name nudges its stamp on collision.

**Superseded (race-fix commit, same anchor):** the stopgap collection is removed. `SaveIdentity.Migrate`
now takes its test injectors (`backupFailure`, `failAfterStep`, `failureInjector`) as parameters on a
test-only `MigrateForTest` entry point instead of process-wide statics
(`FailureInjectorForTests`/`BackupFailureForTests`/`FailAfterStepForTests`, all deleted). No shared
mutable state remains, so `SaveIdentityBackupDiskTests` and `SaveIdentityMigrationTests` (plus the three
other classes in that file) need no `[Collection]` and run safely under xUnit's default parallelism.
Proof: `FusionRpg.Data.Tests` run whole, twice consecutively — 1676/1677 passed both times, the same
single pre-existing unrelated failure (`CreatureSpeciesImportCliTests`, stale generated creature data)
both runs, zero flakes in any `SaveIdentity*` class.

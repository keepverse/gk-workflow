# Manager acceptance review — expedition durability and identity closure

**Source lane:** `resume-04-expedition-durability-final-20260925` (worker result preserved; no direct merge)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-expedition-durability-20260925`
**Status:** **PARTIAL until exact-SHA clean checkout; scoped expedition evidence is green**

## Change reviewed

- Expedition collect/recall now persists a versioned result manifest in the same transaction as the terminal transition and rewards; a retry reads the original reveal without paying again.
- A partial unique SQLite index enforces one active membership per specimen across independent handles. Archived saves are rejected at expedition entry routes.
- Test-only barrier/fault seams exercise real concurrent collect and post-commit response loss; they do not fabricate persisted state.
- No Contracts, generated data, or unrelated product paths were changed.

## Independent focused evidence

```text
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ExpeditionStoreTests"
# 13 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ExpeditionE2ETests"
# 8 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesExpeditionTests"
# 3 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ExpeditionRewardApplyTests&FullyQualifiedName!~Soul_trim_keeps"
# 5 passed, 0 failed, 0 skipped; exit 0

verify-change.ps1 -Paths <five concrete executable paths>
  -Session resume-04-expedition-acceptance-20260925 -PlanOnly -Format json
# exit 0; DAL, test-substrate, and session-boundary checks passed
```

The worker's path-owned aggregate was fail-closed on one out-of-fence Data storage-plan test: `RpgStoreStoragePlanTests.Memory_schema_is_identical_to_the_file_store` exceeded the Windows path limit during SaveIdentity backup. It reported 1199/1200 selected Data tests passing. This is not counted as a green aggregate and is not silently attributed to the expedition code.

## Known product questions

- Legacy terminal expedition rows have no durable manifest and retain the prior closed/conflict response; no reconstruction was guessed.
- Existing databases with duplicate active memberships fail closed when the new unique index is installed; no destructive automatic repair was added.
- No deployed production database, multi-process WAL test, browser, or live game/server proof was run.

## Remaining requirements

1. Commit the reviewed five code/test paths and this report at an exact SHA.
2. Run the focused tests and PlanOnly from a clean detached checkout.
3. Validate/write the exact-SHA artifact and merge only that SHA.
4. Keep the out-of-fence path-length failure and the legacy migration questions open in the owning ledger.

<<<REPORT {"status":"partial","summary":"Manager review confirms durable expedition result persistence, database-level active membership, archived-save rejection, and real concurrency/fault seams. Thirteen store, eight E2E, three species-expedition, and five reward tests passed; PlanOnly and DAL/test-substrate/session-boundary checks passed. The path-owned Data aggregate is explicitly red on an out-of-fence Windows long-path SaveIdentity test, and exact-SHA clean-checkout acceptance remains.","changed_files":["gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs","gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs","gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs","gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs","gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs","tasks/reports/resume-04-expedition-acceptance-20260925.md"],"verification":["13 ExpeditionStoreTests passed","8 ExpeditionE2ETests passed","3 SpeciesExpeditionTests passed","5 filtered ExpeditionRewardApplyTests passed","path-owned PlanOnly, DAL, test-substrate, and session-boundary checks passed","out-of-fence path-owned Data aggregate recorded as RED on Windows long-path SaveIdentity test"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","out-of-fence path-length Data test remains red","legacy terminal rows have no manifest reconstruction","duplicate active memberships fail closed on migration","no live/browser proof"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification and artifact","merge exact SHA","route the Data path-length failure and migration questions to owners","run merged-head/live gates at the appropriate boundary"]} REPORT>>>

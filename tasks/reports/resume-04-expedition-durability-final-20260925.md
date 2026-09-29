# Resume P1 04 final — expedition durable result and identity closure

**Date:** 2026-09-25  
**Session:** `resume-04-expedition-durability-final-20260925`  
**Base/full HEAD SHA:** `838befd9625885d59cc9b2c3321c1faeafc609bf`  
**State:** implementation and focused verification complete; dirty for manager review; no commit, push, merge, branch, or Contracts edit.

## Result

- A successful collect/recall now writes a versioned durable result manifest in the same SQLite transaction as the `Dispatched -> Collected/Recalled` transition, active-membership release, event Souls, specimen XP, wild-join mint, and materials. A retry reads and returns that stored result without re-running reward writes.
- Active expedition membership is enforced by the partial unique SQLite index `ux_rpg_expedition_members_active`, not only by `RpgStore`'s instance-local pre-read. Independent store handles deterministically race at the check/write boundary; one dispatch wins and the other returns `specimen.on-expedition`.
- Expedition route admission now distinguishes an unknown save (`404`, `player.unknown`) from an archived save (`409`, `save.archived`) before expedition service/domain work. The store repeats the live-save check for dispatch as defense in depth.
- SIM-only seams coordinate two real collect requests and inject a failure after the real store commit. They do not fabricate result, battle, reward, or membership state.
- No reward policy, resolver, battle math, expedition tier, or balance value changed. The existing reward entry point remains as a compatibility overload for non-route Data callers.
- A shared `FusionRpg.Contracts` DTO was not needed. The durable route contract is an expedition-owned Data record consumed by Server, so the web-recovery lane's Contracts fence was not crossed.

## Implementation

### Durable result and replay

- Added additive `rpg_expeditions.result_schema_version` / `result_json` columns for fresh and migrated stores.
- `ExpeditionResultContract.Version = 1` gates reads; unknown versions, partial rows, malformed JSON, and missing required list/identity fields fail loudly rather than replaying a guessed response.
- `CommitExpeditionRewardsAndResult` writes the final manifest after wild joins have been minted and before the one transaction commits. The exact `wildJoins` returned by a later retry are therefore the original minted specimens, not a re-resolution.
- `ExpeditionService.CollectAsync` checks a terminal row's durable manifest before returning the old `409`; both `/collect` and `/recall` replay the stored payload.
- Concurrent callers that both reach settlement receive the same stored result. Only the transaction winner performs loyalty/notification side effects; the replay path returns before them.

### Database identity boundary

- Added `CREATE UNIQUE INDEX ... ON rpg_expedition_members(instance_id) WHERE active = 1`.
- Dispatch still keeps its friendly pre-read, but the index is authoritative. Correlation and active-membership unique violations are translated to the established outcomes.
- The internal barrier seam is used only by Data tests with two independent handles over the same named shared-memory database.

### Archived admission

- `RejectUnavailableSave` runs first in expedition list, materials, dispatch, collect, and recall handlers.
- The E2E test sends an archived save plus otherwise-invalid tier/squad data and receives `409 save.archived`, proving admission precedence, then reads expedition rows through a separate store handle and observes none.

## Changed files

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`
- `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs`
- `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs`
- `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs`
- `tasks/reports/resume-04-expedition-durability-final-20260925.md`

`gk-core/tests/FusionRpg.Data.Tests/ExpeditionRewardApplyTests.cs` was allowed but did not require modification; its existing compatibility coverage was run.

## Database and test substrate

- New Data tests use `DataTestStore.Create()` named shared-memory SQLite, reopen the same named databases for independent handles, and hold keepers for the test lifetime. No task-added test writes a temp/data directory.
- The additive-schema test uses `DataTestStore.CreateWithPreInitHot`, still in memory, to create the pre-manifest table/index shape before `RpgStore.Init()`.
- E2E uses the real `WebApplicationFactory<Program>` host and its named shared-memory hot/media stores. Routes exercised include dispatch, collect, recall, `/api/runs`, `/api/souls/1`, `/api/creatures/1`, `/api/expeditions/1`, and `/api/expeditions/1/materials`.
- The only file-backed failure is a pre-existing selected-boundary test attempting to create a long SaveIdentity backup filename below this worktree's long Release output path.

## Exact commands and results

### Session and static checks

```powershell
python scripts/session-boundary-check.py --session resume-04-expedition-durability-final-20260925
```

Result: exit `0`; `clean for 'resume-04-expedition-durability-final-20260925'`.

```powershell
git diff --check
```

Result: exit `0`, no output.

### Focused RED proof before implementation

```powershell
dotnet test tests\FusionRpg.Data.Tests --no-restore --filter "FullyQualifiedName~ExpeditionStoreTests" --logger "console;verbosity=minimal"
```

Result: expected RED compile failure for the not-yet-implemented durable result records/commit API and independent-handle dispatch seam.

```powershell
dotnet test tests\FusionRpg.E2E.Tests --no-restore --filter "FullyQualifiedName~ExpeditionE2ETests" --logger "console;verbosity=minimal"
```

Result: expected RED `3/8` failures: both SIM fault routes returned `405`, and archived dispatch returned `400` instead of deliberate `409`.

### Focused GREEN proof

```powershell
dotnet test tests\FusionRpg.Data.Tests --no-restore --filter "FullyQualifiedName~ExpeditionStoreTests" --logger "console;verbosity=minimal"
```

Result: exit `0`; `13 passed, 0 failed, 0 skipped`.

```powershell
dotnet test tests\FusionRpg.E2E.Tests --no-restore --filter "FullyQualifiedName~ExpeditionE2ETests" --logger "console;verbosity=minimal"
```

Result: exit `0`; `8 passed, 0 failed, 0 skipped`. This includes normal dispatch/due/collect, deterministic concurrent collect, real post-commit `500` plus two identical successful replays, recall replay, archived admission, seed secrecy, and bad requests.

```powershell
dotnet test tests\FusionRpg.Data.Tests --no-restore --filter "FullyQualifiedName~SpeciesExpeditionTests" --logger "console;verbosity=minimal"
```

Result: exit `0`; `3 passed, 0 failed`.

```powershell
dotnet test tests\FusionRpg.Data.Tests --no-build --no-restore --filter "FullyQualifiedName~ExpeditionRewardApplyTests&FullyQualifiedName!~Soul_trim_keeps" --logger "console;verbosity=minimal"
```

Result: exit `0`; `5 passed, 0 failed`. This was run after the Data assembly had been built by the preceding focused command.

```powershell
dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj --filter "FullyQualifiedName~UniqueAllocationReaderGuardTests" --logger "console;verbosity=minimal"
```

Result: restored the previously absent Guard test assets, then exit `0`; `2 passed, 0 failed`.

```powershell
dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj --no-restore --filter "VerificationId=guard.unique-allocation-reader" --logger "console;verbosity=minimal"
```

Result: exit `0`; `2 passed, 0 failed` (the planner's exact VerificationId check, now proven non-zero).

### Reachable path-selected module checks

```powershell
dotnet test tests\FusionRpg.Server.Tests\FusionRpg.Server.Tests.csproj --filter "Category!=DiskSemantics&Category!=Heavy" --logger "console;verbosity=minimal"
```

Result: restored the previously absent Server.Tests assets, then exit `0`; `859 passed, 0 failed, 0 skipped`.

```powershell
dotnet test tests\FusionRpg.E2E.Tests\FusionRpg.E2E.Tests.csproj --no-restore --filter "Category!=DiskSemantics&Category!=Heavy" --logger "console;verbosity=minimal"
```

Result: exit `0`; `281 passed, 0 failed, 0 skipped`.

### Path-owned verification

```powershell
$changed = @(
  'gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs',
  'gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs',
  'gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs'
)
.\scripts\verify-change.ps1 -Paths $changed -Session resume-04-expedition-durability-final-20260925
```

Result: planner selected Data module, Server module, E2E module, DAL, test-substrate, and the unique-allocation-reader seam.

- DAL guard: PASS.
- Test-substrate guard: PASS.
- Release Data.Tests build: PASS, `0 errors`.
- Data shards `a`, `b`, `c`: PASS (`464`, `41`, `83` tests).
- Data shard `rest`: FAIL, one test. Exact reproduction executed `1200` tests: `1199 passed`, `1 failed`.
- Sole failure: `FusionRpg.Data.Tests.RpgStoreStoragePlanTests.Memory_schema_is_identical_to_the_file_store`.
- Failure cause: SaveIdentity cannot create `rpg-hot.sqlite.pre-save-identity.<timestamp>.bak` below the already-long `...\opencode-resume-04-expedition-durability-final-20260925\tests\FusionRpg.Data.Tests\bin\Release\net8.0\msp-parity-...\` path (`SQLite Error 14`). The same environment failure reproduced before implementation in `ExpeditionRewardApplyTests.Soul_trim_keeps_a_mixed_earn_spend_ledger_consistent`; it is not caused by the expedition paths and its source is outside this lane's fence.

Final rerun after this report was created, with all six concrete paths (the five code/test files plus this report):

```powershell
$changed = @(
  'gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs',
  'gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs',
  'gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs',
  'tasks/reports/resume-04-expedition-durability-final-20260925.md'
)
.\scripts\verify-change.ps1 -Paths $changed -Session resume-04-expedition-durability-final-20260925
```

Result: the same fail-closed boundary result. Session-boundary, DAL, and test-substrate checks passed; Release Data build passed with `0 warnings, 0 errors`; shards `a`, `b`, and `c` passed (`464`, `41`, `83`); `rest` alone failed with the same single pre-existing long-path backup failure. The report path was accepted by the planner; no unmapped-path error occurred.

## Untested live behavior

- No deployed Windows game, injector, `dist/` server, production file database, or manual browser session was used.
- Independent-handle concurrency is proven in-process over one named shared-memory SQLite database. A real multi-process launch against a shared file database and WAL contention was not exercised.
- No live-game expedition behavior exists to probe; expedition is standalone/web. The real ASP.NET route host and normal read-back routes were exercised in E2E.

## Open questions and known limits

1. **Manager blocker/follow-up for green planner:** accept the selected Data failure as the known Windows path-length defect, or assign the out-of-fence `RpgStoreStoragePlanTests` / SaveIdentity backup-path owner and rerun. This lane did not modify that test or migration.
2. **Legacy terminal rows:** expeditions collected before this schema change have no durable manifest. Their retries retain the prior `409` behavior because the exact original wild-mint DTOs/battle reveal cannot be reconstructed truthfully. No guessed backfill was added.
3. **Existing duplicate active rows:** installing the unique index intentionally fails closed if an old multi-process race already left two active rows for one specimen. No automatic row deletion/reassignment was invented; manager may want a separate audited repair if a real save exhibits this.
4. **No Contracts blocker:** no shared DTO was required. If a future web lane needs a separately versioned wire contract for these fields, that manager-owned Contracts change remains a named follow-up rather than an implicit dependency here.

## Next plan

1. Manager reviews the five code/test diffs plus this report; no commit has been created.
2. Manager accepts the focused GREEN evidence and either accepts the known path-length selected-test failure or routes its out-of-fence repair.
3. If manager wants clean-checkout acceptance, run the same `verify-change.ps1` command from a shorter checkout/output path and record the exact SHA/artifact.
4. No live probe is required for this standalone loop; optional production-like proof would be two server processes against one scratch file store, only if manager promotes that topology to a requirement.

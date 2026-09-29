# EP4.6 — Empire-level backfill at store start, for every empire with no `kind = 'empire'` row

Commit `@EP4.6` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-empire-level.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| For a seeded store the backfill produces the same empire row and grants as live crediting | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11` — `The_backfill_produces_what_live_play_credited` plays two matches, captures the live row and its credit rows, ERASES both (the state a pre-feature save is in), and asserts a fresh store start rebuilds the identical `(level, xp, highest)` and the identical `(levelBefore, levelAfter, delta)` triples | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` (`BackfillEmpireLevelsUnlocked`), `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` |
| A second start changes nothing, including after the empire's ledger rows are deleted | same | `Passed: 11` — `A_second_start_changes_nothing_even_after_the_empires_ledger_rows_are_deleted`: a second start is a no-op, and after deleting every `kind='empire'` ledger row a third start still changes nothing and re-pays no credit. The pass keys off the empire ROW, not the `sp:*` dedupe keys compaction trims | same |
| A pass that throws midway leaves no empire row, and the next start completes it (test 9) | same | `Passed: 11` — `A_pass_that_throws_leaves_no_empire_row_and_the_next_start_completes_it`: a tuning with no `xpCurve.empire` makes the credit refuse, the store start throws, the empire row is **absent** (one transaction per empire, so the rollback is total), and the next start creates it with its credit rows | same |
| Runs before any reader, and only for an empire that has none | read of the diff | `BackfillEmpireLevelsUnlocked(db)` is called from `RpgStore.cs`'s `Init`, beside `BackfillWorldSeedsUnlocked` — the store's own existing store-start backfill — so it runs before a host serves a request. Its candidate query needs `highest_level > 1`, so an empty or never-played database does no work and never touches the progression tuning | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` |
| The same credit path, the same side rule, the same grants | read of the diff | it calls `CreditEmpireForSpeciesLevelsUnlocked` with `highestBefore = 1`, `highestAfter = highest_level`, `runId: 0` and a throwaway side-effect list — so the R1 side rule, the curve, the `sp:{typeId}:L{n}` dedupe keys and the `FreeEmpireRespec` grants are live play's own, level for level. `highest_level` rather than `level`: a demoted species still earned its highest level once | `RpgStore.EmpireLevel.cs` |
| `guard-dal.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/guard-dal.ps1` (inside the boundary run) | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`; `TEST SUBSTRATE GUARD OK` | — |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs') -Session empire-progression-3` | exit 1, entirely the known TVB-F6 misreport: both guards OK, then the Data sharded runner printed its four shard counts with no failure line and an empty exit code | — |
| The Data half, re-run because that exit code is empty | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 1753, Skipped: 0, Total: 1753, Duration: 11 m 18 s`, exit 0 (1750 before this row's 3 tests) | — |

**Idempotence is by construction, not by the ledger.** The first credit creates the `kind = 'empire'` row, so once an
empire's transaction has committed the "no empire row" test is false and the pass never runs there again — even after
compaction has trimmed the very `sp:*` keys a ledger-based rule would depend on. That is the same argument EP4.3 made for
reading `highest_level`, applied to the pass that has to survive a save never having run the credit at all.

**One transaction per empire** is the spec's own shape, and it is what makes the failure case total: a throw rolls that
empire's row and grants back together, so the next start reads a clean slate rather than a half-credited empire.

**Not proved** (owned by later rows):
- Nothing here serves a response: the level read (`GET /api/players/{playerId}/empires/{empireId}/level`) and the
  `EmpireLevelUp` broadcast are EP4.7's.
- A save whose species rows belong to an empire that is NOT the human's is not exercised end-to-end (nothing credits
  Zomboss's species rows until `ai-empire-species` routes them); the pass is empire-agnostic by construction — it iterates
  the distinct `(save_id, empire_id)` pairs the species rows carry and never resolves the human empire.
- The pass does not trim or reconcile an EXISTING empire row whose species have since climbed above it: a species level-up
  credits live, so a row that exists is already current by the same code path.

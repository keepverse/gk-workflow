# EP4.5 — `rpg_empire_free_respec_ledger` and the `FreeEmpireRespec` grant in the level-change transaction

Commit `@EP4.5` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Crossing `k` empire levels writes `k` grants of `freeRespecsPerEmpireLevel`, keyed `L{n}` | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireFreeRespec\|FullyQualifiedName~EmpireLevel"` | `Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13` — `Crossing_empire_levels_writes_one_grant_per_level_keyed_by_it`: two rows for a two-level crossing, `level` = 2 and 3, `delta` = 1, `reason` = `empire-level` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs` (new) |
| A replayed level-up adds nothing | same | `Passed: 13` — `A_replayed_level_up_adds_nothing` applies the same crossing twice (primary-key idempotence) **and** replays the fact that produced it; the row count and stock are unchanged | `RpgStore.EmpireFreeRespec.cs` (`INSERT OR IGNORE` on `PRIMARY KEY (save_id, empire_id, level)`) |
| A value of 0 writes nothing | same | `Passed: 13` — `A_published_zero_writes_nothing`: with `freeRespecsPerEmpireLevel = 0` the empire LEVEL still moves and the ledger and stock stay empty (no zero-delta row) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` + `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` (the grant apply beside the level change) |
| The stock is `SUM(delta)` per `(save_id, empire_id)` and never negative | same | `Passed: 13` — `The_stock_is_the_sum_of_the_ledger_and_a_negative_sum_throws` asserts stock == the ledger's sum, then writes an over-spend row and asserts the read THROWS (`"a grant is never taken back"`) rather than clamping to 0 | `RpgStore.FreeRespecStock` / `FreeRespecStockUnlocked` |
| Zomboss accrues under his own `EmpireRef` (test 10, accrual half) | same | `Passed: 13` — `Zomboss_accrues_under_his_own_empire_ref_and_the_human_does_not_move`: Zomboss's stock is 2 while the human's is unchanged, from the same save | same |
| The X13 note lives on `save-identity`'s consumer row | read of `docs/architecture/solid-enforcement/spec-save-identity.md` | **already there**: `:600` — *"the free-respec **stock** ledger and the empire-level row are keyed for **every** empire `(SaveId, EmpireId)`, so Zomboss's empire accrues on the same track (R19). Only the **spend** stays human-only … Recorded as empire-progression X13"*. This row's implementation matches it (nothing here reads `HumanEmpireOf` for the key); no doc edit was needed, and the file is outside this lane's fence | — |
| **H2 — the table lands as a migration before the code that writes it** | read of the diff | the same commit adds `EnsureEmpireFreeRespecSchemaUnlocked` and calls it from `RpgStore.cs`'s `Init` schema cluster (beside `EnsureCommanderRoleSchemaUnlocked`), so `CREATE TABLE IF NOT EXISTS` runs before any writer; the DDL lives beside its store partial, the house convention | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` |
| `guard-dal.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data`, exit 0 | — |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs') -Session empire-progression-3` | exit 1, entirely the known TVB-F6 misreport: `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK`, then the Data sharded runner printed `444 + 40 + 83 + 1158` tests with no failure line and an empty exit code | — |
| The Data half, re-run because that exit code is empty | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 1750, Skipped: 0, Total: 1750, Duration: 10 m 49 s`, exit 0 (1745 before this row's 5 tests) | — |

**Why the stock is a sum and not a column.** A stored balance is a second source of truth for the same number and can
disagree with its own ledger; a sum cannot. The read therefore derives its bound: grants are only ever positive ("a grant is
never taken back"), so a negative sum is a corrupt ledger and the read throws rather than clamping — the API and the spend that
consumes it (EP4.9) must see the defect, not a flattened zero.

**Keyed for every empire, on purpose.** This table is the *stock*; the spend is the human-only half (EP4.9's `EmpireRef`
refusal). That split is exactly what X13 records, and it is why the applier takes an `EmpireRef` and never resolves the human
empire itself.

**Not proved** (owned by the next rows):
- The spend: nothing consumes the stock here. EP4.9 spends one at a species respec (writing a negative-delta row and refusing
  an over-spend), EP4.11 asserts no compaction path trims this ledger, and the registry row (`empire-resource-ssot.md` §3) is
  EP4.11's.
- The read surface: `FreeRespecStock(EmpireRef)` is in place for EP4.7's route and the `freeRespecStock` field of the broadcast;
  neither is wired here.
- Zomboss's accrual through real gameplay: today's R1 side rule keeps zombie species XP on the human's empire, so the KEYING is
  proved through the applier (as the fragment's row says) and `ai-empire-species` is what will feed his row for real.

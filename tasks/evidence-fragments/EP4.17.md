# EP4.17 - the one empire-keyed commander-pool read

`RpgStore.CommanderPoolOf(EmpireRef, theta, tuning)` (+ its `...Unlocked(db, …)` sibling) is the one read
that answers "what is this empire's commander pool?". Explicit allocation under the empire's own scope key
wins wholesale (D2); else the rule is read from DATA (`rpg_save_empires.controller`), never a `switch` over
`EmpireId`: a **human** empire has no silent default (D1) and resolves Empty, an **AI** empire gets
`AssignLadder.Suggest`'s commander-context default at its own budget. Computed at read, never persisted.
Commit `@EP4.17` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| test 10: non-zero budget resolves the ladder's commander-context distribution, skips recorded, points sum to the budget | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderPool"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` - `A_zomboss_pool_resolves_the_ladders_commander_default_at_his_budget_and_writes_nothing` asserts `RuleId ==` the ladder's own answer (not a pinned rung), `Skipped` non-empty, `TotalForScope(Commander) == PointBudget.PointsFor(Commander, 100, tuning)` and the stored row still 0 | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/CommanderAllocation.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs` (new) |
| test 10 (zero budget) resolves Empty | same | `Passed: 6` - `A_zero_budget_resolves_Empty` | same |
| test 12: save A's pool never reaches save B | same | `Passed: 6` - `Save_As_pool_never_reaches_save_B`: A's explicit row reads 9 (IsDefault false), B and C (both unseeded) both resolve the ladder default and agree with each other | same |
| test 13: an empty Dave pool stays Empty; an explicit one is read | same | `Passed: 6` - `An_empty_Dave_pool_stays_Empty_and_takes_no_silent_default` | same |
| An empire the save does not carry reads Empty (never a guessed empire) | same | `Passed: 6` - `An_empire_the_save_does_not_carry_reads_Empty` | same |
| Explicit pool under his key wins wholesale | same | `Passed: 6` - `An_explicit_pool_under_his_key_wins_wholesale` | same |
| Not wired into any seam; no golden moves | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs','gk-core/src/FusionRpg.Core/Stats/Aptitudes/CommanderAllocation.cs','gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs' -Session empire-progression-4"` | `EXIT=0` - dal + test-substrate guards OK; core fallback all green (Core.Tests 11055/11055, Balance 210, Commanders 64, ClassSystem 238, ActorHub 498, …); data `TEST-SHARDED OK: 4 shards, 1753 tests, no overlap`. `guard-power.py` OK | - |

**Decision (rounding).** The row's text says "the same largest-remainder … math the silent default already
uses … no third rounding function", and its acceptance says the points sum to the budget. `Materialize`
(the D13/preset path) truncates and leaves a legal leftover (E2), so it cannot satisfy "sum to the budget";
the largest-remainder scheme lives in each scope's own `Baseline` (`SpeciesAllocation`,
`UniqueCreatureAllocation`). Following EP1.13's own consumer shape, this adds
`CommanderAllocation.Baseline` — the third per-scope copy of the SAME scheme (the duplication is the
documented, deliberate precedent in `UniqueCreatureAllocation`'s type doc, not a new rounding rule) — for a
distribution rung, and keeps `Materialize` for an `active-preset` rung (which cannot win today: an AI has
no preset surface, so the walk records that skip). No new *scheme* was introduced.

**NOT proved / owed to the next row:** `CommanderPoolOf` has no production caller yet. That is this row's
own acceptance ("It is not wired into any seam yet, so no golden moves") — the wire is EP4.18's
deliverable, together with the R23 golden commit.

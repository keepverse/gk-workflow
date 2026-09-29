# EP4.3 — Credit an empire level-up inside `TryApplyXpUnlocked` for each new `highest_level` of its own species

Commit `@EP4.3` · session `empire-progression-3` · branch `cmdc/ep-3` · spec `docs/architecture/empire-progression/spec-empire-level.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Both species XP paths credit once per `(species, level)` over `(highestBefore, highestAfter]` | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"` | `Passed! - Failed: 0, Passed: 8, Skipped: 0, Total: 8` — `The_per_placement_path_...` and `The_run_completion_path_...` each assert one ledger row per new species level, in commit order, each row carrying `RpgXpAwards.SpeciesLevelUp` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` (the hook + the dirty envelope), `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` (new) |
| Demote and re-climb credits nothing, **even after the empire's `sp:*` ledger rows are deleted** (what compaction leaves) | same | `Passed: 8` — `A_demote_and_reclimb_credits_nothing_even_after_the_ledger_rows_are_trimmed` demotes via SQL (the state `RpgXpApply` produces; no fact vocabulary produces it yet), deletes every `kind='empire'` ledger row, re-climbs to exactly the earlier peak, and asserts the empire level and ledger are unchanged | same |
| R1 side rule: a human-owned zombie species never moves the human's empire | same | `Passed: 8` — `A_human_owned_zombie_species_never_moves_the_humans_empire`: the zombie species row levels to ≥2 and the human's empire row is **never created at all** | same |
| A replay changes nothing | same | `Passed: 8` — `A_replayed_fact_changes_neither_the_species_nor_the_empire` | same |
| The dirties are collected by the caller; `EmpireLevelUp` is queued and broadcast only after commit; a rolled-back transaction queues nothing | same | `Passed: 8` — `One_credit_that_crosses_several_empire_levels_queues_one_event_each` reads the crossings off the dirty returned to the caller (`PvzActivityAppendResult.Progression`), one event per level crossed, and `A_rolled_back_transaction_credits_nothing_and_queues_nothing` forces the credit to throw mid-transaction (a tuning with no `xpCurve.empire`), then asserts the species row kept its pre-append level/xp/highest AND nothing of the failed append survives | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` (`EmpireLevelUpEvent` rides `RpgProgressionDirty.LevelUps`) |
| Nothing is registered in `ProgressionPipeline` | read of the diff | the empty pipeline is untouched — the credit is post-ledger-insert work inside the caller's transaction, exactly as the spec requires (a pipeline handler would fire before the dedupe and re-pay a replay) | — |
| The empire levels exactly when `RpgXpCurve.XpToNext(Empire, L)` says, for L from the loaded tuning (test 5, curve half) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"` | `Passed: 8` — `The_empire_levels_exactly_when_the_loaded_curve_says` folds each match's gain through `XpToNext`/`TotalToReach` for the loaded curve and asserts level **and** within-level xp every match, walking both branches | same |
| Path-owned boundary | `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs','gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs','gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs','gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs','gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs') -Session empire-progression-3` | exit 1, entirely the known TVB-F6 misreport: `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK`, all twelve core shards green (`12759`, `15`, `498`, `31`, `1351`, `30`, `210`, `7`, `12`, `238`, `4`, `9`), then the Data sharded runner printed its shard counts with no failure line and an empty exit code, aborting before `test: e2e`. Both skipped halves were then run directly | — |
| The Data and E2E halves of that boundary, re-run | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --no-build --filter "Category!=DiskSemantics&Category!=Heavy"`; `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release` | `Passed! 1745/1745, exit 0` (1737 before this row's 8 tests) and `Passed! 231/231` | — |
| Regression on the XP path this row edits | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesProgression\|FullyQualifiedName~ZombossCommanderClock\|FullyQualifiedName~WorldTurn\|FullyQualifiedName~ParentOf\|FullyQualifiedName~CommanderAttach"` | `Passed! - Failed: 0, Passed: 54, Skipped: 0, Total: 54` | — |

**The one real trap this row had, for the next reader.** `RpgXpApply.Apply` **mutates the `RpgActorState` it is handed**,
`HighestLevel` included. Reading `state.HighestLevel` after the call makes `highestAfter <= highestBefore` always true, so the
credit silently pays nothing and every assertion in the file fails with an empty empire row. The pre-apply value is therefore
captured next to `levelBefore`/`xpBefore`/`demotionBefore` — the three locals that exist for exactly this reason — and the
comment there says so.

**Three tuning bootstraps moved with it.** `gk-core/tests/FusionRpg.Core.Tests.Shared`, `gk-core/tests/FusionRpg.Data.Tests` and
`gk-core/tests/FusionRpg.E2E.Tests`' `ContractTuningTestBootstrap.DefaultProgression` now mirror the shipped `progression.v3.json`
(`EmpireCurve` = 10/5, `SpeciesLevelUp` = 1) — they claim to be "the same working set as the shipped file", and from EP4.2 that
file carries both keys, so a bootstrap without them was the stale one. `Age…`/`Version` moved to 3 for the same reason; nothing
asserts it.

**Not proved / deviations, named for the manager:**
- **spec testing-strategy test 4 as literally worded is unreachable, and this file proves the same claim where it IS reachable.**
  "One award that crosses `k` species levels credits `k` times" cannot happen with the shipped species curve: its thresholds are
  `60 + 24·(n−1)`, so the two smallest consecutive ones sum to 144 while the largest award the fact vocabulary produces is 100
  (a resolved run) — a single award can never cross two species levels, by the curve's own anti-grind design. Reaching it would
  mean reconfiguring `SpeciesProgressionTuningHub`, which changes what `RpgXpAwardMap` and `SpeciesProgressionTests` compute while
  they run; that contention already produced one red run this session and is rejected in the test's own comment. What IS proved:
  the range claim `(highestBefore, highestAfter]` (row count and per-row delta on both paths), and the `k`-fan-out one step along
  — one credit crossing `k` empire levels queues `k` events (`One_credit_that_crosses_several_empire_levels_queues_one_event_each`).
  Filed as a finding for an erratum ruling rather than silently reworded.
- The `EmpireLevelUp` **broadcast** is EP4.7's (route + SignalR). This row proves the queue reaches the caller and dies with a
  rolled-back transaction; nothing here renders it.
- The grants on a queued event are **empty today**: `EmpireGrants` is the `EmpireLevelTuning` slot EP4.4's host wiring fills from
  `freeRespecsPerEmpireLevel`, so `EmpireLevelGrants.For` returns nothing until then. The level moves; the payout arrives with
  EP4.4/EP4.5, which is the order the plan specifies.
- Zomboss's own feed (`ai-empire-species`) is untouched: zombie species XP still credits the human's rows, and the R1 rule makes
  that pay nothing. `A_human_owned_zombie_species_never_moves_the_humans_empire` is the assertion, not a comment.

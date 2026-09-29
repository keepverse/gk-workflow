# SE4.41 — closure contracts (Tier A owners, world factions)

`gk-core/tests/FusionRpg.Data.Tests/Saves/SaveEmpireClosureTests.cs` (new, in-memory store, raw SQL for the
closure reads only — no SQL in `src/` beyond `FusionRpg.Data`). Every check is a violation LIST, never
a row count; each of the two checks has the violation it exists to catch planted, per the program's
"a guard that cannot fail is not a guard" rule.

| Criterion | Command | Result |
|---|---|---|
| Every Tier A `(save_id, empire_id)` is in `rpg_save_empires`; no `empire_id` is null | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~SaveEmpireClosure"` | `Passed! - Failed: 0, Passed: 6, Total: 6` (1 s) |
| Non-vacuity of the green case | same run, `Tier_A_rows_of_a_real_state_all_resolve_to_a_seeded_empire` | specimens / progression / ledger each `COUNT(*) > 0` after `SeedRpgProgressionDemo` + two `MintForEmpire` |
| The check can fail — null owner | same run, `A_specimen_with_no_owner_is_reported` | planted `empire_id = NULL` → reported as `specimen:<id>` |
| The check can fail — unseeded owner | same run, `A_specimen_owned_by_an_empire_no_save_seeded_is_reported` and `A_progression_row_owned_by_an_empire_no_save_seeded_is_reported` | planted `'empire-no-save-seeded'` → reported for specimen, progression and ledger |
| Every `rpg_world_factions.faction_id` naming an empire is an empire of its world's save | same run, `A_world_of_a_seeded_save_names_only_its_own_empires` (empty) and `A_world_of_an_unseeded_save_naming_an_empire_is_reported` (planted: legacy save, template factions `dave`/`zomboss`) | empty / non-empty as asserted; `wild` is not an empire id and is not the check's subject |
| No row count asserted anywhere | the file | every assertion is membership, emptiness or emptiness-of-violations; the two `COUNT(*)` uses are `> 0` vacuity guards |
| Module boundary | `pwsh -NoProfile -Command "& ./scripts/test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj -ExtraFilter 'Category!=DiskSemantics&Category!=Heavy' -Root (Get-Location).Path"` | `TEST-SHARDED OK: 4 shards, 1747 tests, no overlap` (1741 before this file's 6), every shard `exit 0` |

Checkpoint 4b item 2 ("exactly one `human` per save; no null `empire_id`; no Zomboss player row; a
13th deploy") is ticked in the same commit, each clause citing the test that holds it.

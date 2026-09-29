# EP4.9 - the species respec spend takes `payWith`; replay on both ledgers; the quote

Commit `@EP4.9` (this commit closes the row the partial groundwork commit opened) - session
`empire-progression-3` - branch `cmdc/ep-3` - spec
`docs/architecture/empire-progression/spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| With stock >= 1 and no `payWith`: `respec.payment.choice-required`, carrying the quote, nothing written (test 1) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec\|FullyQualifiedName~EmpireFreeRespec"` | `Passed! - Failed: 0, Passed: 21, Skipped: 0, Total: 21` - `With_stock_and_no_choice_the_spend_refuses_carrying_the_quote_and_writes_nothing` asserts the reason, `Priced`, `PriceAmount` == the quote's soul amount, a positive `FreeStock`, and that stock, soul balance and churn counter are all unchanged | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs` |
| `freeRespec` spends 1 and leaves the churn counter unchanged (test 2) | same | `Passed: 21` - `A_free_respec_spends_one_and_leaves_the_churn_counter_alone`: stock 1 -> 0, one `species-respec` row, the soul balance untouched and the counter still 0 | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs` (`TrySpendFreeRespecUnlocked`) |
| `souls` charges `PriceOf` and leaves the stock unchanged (test 3) | same | `Passed: 21` - `A_souls_spend_charges_the_price_and_leaves_the_stock_alone`: balance 1000 -> 1000 - quote, stock unchanged, counter 1, no spend row | same |
| With no stock, `freeRespec` refuses `respec.free.none`, and an omitted `payWith` behaves exactly as today (test 4) | same | `Passed: 21` - `With_no_stock_a_free_respec_refuses_and_an_omitted_choice_charges_souls_as_before` | same |
| With the key at 0, every existing `SpeciesRespecTests` case passes (test 5) | same (the filter includes that suite) | `Passed: 21` - the whole `SpeciesRespecTests` class is in the run and unchanged, so the omitted-choice path is byte-identical with no stock | `gk-core/tests/FusionRpg.Data.Tests/SpeciesRespecTests.cs` (unedited) |
| First override and revert move neither the stock nor the counter (test 6) | same | `Passed: 21` - `A_first_override_and_a_revert_ask_no_choice_and_move_neither_stock_nor_counter` (the free branch returns `PaidWith == ""` before the choice is ever consulted) | `RpgStore.SpeciesRespec.cs` |
| A replay on either ledger returns the original payment (test 7) | same | `Passed: 21` - `A_replay_returns_the_original_payment_on_either_ledger`: the free replay reports `replay` + `freeRespec` and spends nothing more; the soul replay reports `replay` + `souls` and charges nothing more | same |
| Preview equals spend for stock 0 and stock >= 1, at counts 0 to 3 (test 9) | same | `Passed: 21` - `The_preview_equals_the_spend_for_both_stocks_at_counts_zero_to_three` compares `QuoteSpeciesRespec` against the spend's own `PriceAmount` on the souls path and against `FreeAvailable` on the free path | `QuoteSpeciesRespec` |
| A human spend never touches Zomboss's stock (test 10, spend half) | same | `Passed: 21` - `A_human_free_respec_never_touches_zomboss_stock`: same save, both stocks seeded, the human's goes to 0 and Zomboss's is untouched | same |
| The Core price/quote surface still holds | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy"` | `Passed! - Failed: 0, Passed: 27, Skipped: 0, Total: 27` | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs` (`RespecPayment`, `RespecPayments`) |
| Path-owned boundary | `.\scriptserify-change.ps1 -Paths @(<the five files>) -Session empire-progression-3` | exit 1, entirely the known TVB-F6 misreport: `DAL GUARD OK`, `TEST SUBSTRATE GUARD OK`, every core shard green, then the Data sharded runner printed its shard counts with no failure line and an empty exit code. The Data half was run directly as the two filters above | - |

**The one place this row had to read the existing rules closely.** A species' FIRST override is free
(spec-species-respec.md's own rule, and the reason `rpg_species_respec` marks a species touched at count 0), so
the choice only applies to a PRICED change. Every test here therefore touches the species first - and the
first draft failed loudly until it did, which is why the helper says so in its own doc comment. That also fixes
what "an omitted `payWith` behaves exactly as today" means: with no stock the pre-EP4.9 path is unchanged, and
with stock the store refuses rather than guessing.

**Design decisions, both recorded in the ledger:**
- A free spend keys on the next NEGATIVE integer in the ledger's `level` column (grants keep the paying level),
  so the EP4.5 primary key separates them and `SUM(delta)` still reads one stock. The replay guard is the
  `dedupe_key` column plus a partial unique index - an additive migration - because a spend has to be
  recognised by WHAT was asked for, not by the key it would mint.
- The free stock is the payment, so the churn counter does not move on a free spend: that counter prices SOUL
  churn.

**Not proved:** the wire (`POST /species-build/respec` carrying `payWith`) is EP4.10's; this row is the store
contract. `RespecPayments.TryParse` has no test yet - it is the route layer's parser and lands with it.

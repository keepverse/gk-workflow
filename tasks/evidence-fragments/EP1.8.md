# EP1.8 — `rpg_allocation_respec` and the one gate `TryReallocate(Unlocked)` / `QuoteReallocation`

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| Adding is free, no ledger/counter row; a take-back charges `PriceOf(UniqueRespec, effectiveCount)`, bumps the counter, escalates; decay follows `DecayDays` (tests 2, 3) | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationRespec"` | pass (13/13) |
| Commander pool and a specimen keep separate counters (test 4) | same run | pass — `The_commander_pool_and_a_specimen_keep_separate_counters` |
| A replayed correlation id charges once under the new `respec-unique`/`respec-commander` reasons (test 5) | same run | pass — `A_replayed_correlation_charges_once_under_the_respec_unique_reason`, `A_commander_respec_ledgers_under_the_respec_commander_reason` |
| Every refusal writes nothing: insufficient souls, missing correlation id, a specimen the caller's empire does not own (incl. a Zomboss specimen of the same save), a non-human payer (test 6) | same run | pass — 4 named refusal tests, each asserts unchanged balance + unchanged allocation |
| No path reads the free stock (test 11) | same run | pass — `No_quote_ever_carries_a_nonzero_free_stock` |
| `guard-dal.ps1` (SQL stays inside `FusionRpg.Data`) | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs,gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs -Session empire-progression-20260920` | exit 0 — `RpgStore.cs` maps to the sharded Data.Tests boundary: `TEST-SHARDED OK: 4 shards, 1648 tests, no overlap`, all 4 shards exit 0 |

## Notes

- Born with `save-identity`'s `EmpireRef` signature (that module landed first, per the spec's own
  "Landing order" branch): `TryReallocate`/`TryReallocateUnlocked`/`QuoteReallocation` all take the
  caller's own `EmpireRef payer`, never a bare player id — enabling the "non-human payer" refusal
  (`empire.notHuman`) the spec's test 6 names, which a `HumanEmpireOf`-derived payer could never trigger.
- Commander-scope ownership is structural (no specimen row to own): `scopeKey` must equal the payer's
  own `"player:{save}"` key, mirroring `AptitudeEndpoints.ScopeKey`'s format inline since Data may not
  reference Server.
- `RespecPolicy.IsRespec` (a real per-aptitude decrease) is a different — and, per spec, more precise —
  semantic than `rpg_species_respec`'s "any change after the first is priced" rule. One consequence
  proven by test: replaying the EXACT same proposed target after it already landed reads as a free
  no-op (state already matches), not a `"replay"`-tagged outcome; the replay path is reached when the
  reused correlation id's second call is still a respec relative to the now-updated state — matching
  the spec's own "a correlation id is the caller's promise that repeats mean the same request," which
  never requires the reused call to repeat the same target.

# EP1.10 — Preset activation's commander and unique branches call `TryReallocateUnlocked`

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| Activating over a commander or specimen charges exactly what the same change charges by hand: equal soul-ledger deltas entry for entry, equal `rpg_allocation_respec` rows at one injected clock (test 10) | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationRespec"` | pass (15/15) — `Preset_activation_over_a_specimen_charges_exactly_what_TryReallocate_charges_by_hand` |
| A respec activation without a `correlationId` refuses with `correlation.missing` and writes nothing | same run — `A_respec_activation_without_a_correlation_id_refuses_and_writes_nothing` | pass |
| One-writer guard (EP1.9's own test 9) now closes with only the three permanent allowed files, `RpgStore.AptitudePresets.cs` no longer needing an exception | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~AllocationWriter"` | pass (2/2) |
| Existing `AptitudePresetEndpointsTests` (unaffected — the endpoint already threaded `correlationId` to every scope) | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"` | pass (12/12) |
| `guard-dal.ps1` | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |
| Server still builds against the changed store file | `dotnet build gk-core/src/FusionRpg.Server -c Debug --nologo` | 0 errors |

## Notes

- Both preset-activation branches build `payer = new EmpireRef(new SaveId(playerId), HumanEmpireOf(playerId))`
  from the ALREADY-AVAILABLE `playerId` parameter (the preset's own owner) rather than re-deriving it
  from the specimen — ownership of the target (`scopeKey`) is `TryReallocateUnlocked`'s own
  `respec.target.not-owned` check, not re-implemented here.
- `RpgStore.AptitudePresets.cs`'s `AptitudePresetActivateOutcome` record already carried
  `Priced`/`PriceAmount`/`RespecCount`/`Balance` fields (built for the species branch's
  `TryRespecSpeciesUnlocked` call) — the commander/unique branches now populate them for real instead
  of hardcoding `false, 0, 0, null`.
- `AptitudePresetEndpoints.cs`'s `/activate` route needed NO change: it already forwarded
  `body.CorrelationId` into `TryActivateAptitudePreset` for every scope before this task.
- Ledger-ordering gotcha found while writing test 10: `ListSoulLedger` returns newest-first, so the
  two new rows from this test are the FRONT of the list (`.Take(2)`), not a suffix
  (`.Skip(ledgerBefore)` would wrap into the older seed-award row) — fixed in the test, not the store.
- `SaveAptitudePreset` requires the full twelve-aptitude row set summing to exactly 1000 (E5); the
  test's `AllTwelveEntries` helper puts the whole 1000 on one named aptitude and 0 on the other eleven,
  reading `AptitudeCatalog.All` rather than hand-listing twelve ids.

## Merge reconciliation folded into this commit

Re-merged `features/mega-merge` (build-preset lane D landed: BP1.1-BP1.8, BP2.1/2.2/2.12) then
`cmdc/lane-b` at the EP1.9 -> EP1.10 boundary. One real conflict, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs`:
lane D's BP2.1 extracted a shared `PatronPreconditionsUnlocked` helper (needed by its new `QuotePatron`)
from `SetPatron`'s inline body, but the extraction used a bare `actor.PlayerId != playerId` equality
instead of the SE4.24 `OwnsSpecimenUnlocked(EmpireRef)` ownership check HEAD's inline body carried —
silently letting a Zomboss specimen of the same save be quoted/designated as the human's patron.
Resolved by keeping lane D's shared-helper structure but restoring the real ownership check inside it,
so both `SetPatron` and `QuotePatron` get the same guard. Verified: `dotnet test
tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Patron"` — 18/18 pass (includes the new
`PatronQuoteTests.cs` from lane D). `cmdc/lane-b`'s merge was clean, no conflicts.

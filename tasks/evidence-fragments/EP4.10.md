# EP4.10 (increment) - the routes carry the choice: `/respec` and `/respec-price`

**Row stays OPEN.** The two species-build routes are done and their own suite is green; the preset
activation pass-through and the new acceptance tests are not. Commit `@EP4.10` (partial) - session
`empire-progression-3` - branch `cmdc/ep-3` - spec
`docs/architecture/empire-progression/spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `POST /respec` accepts `payWith` and returns `paidWith` and `freeRespecStock` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~SpeciesBuild\|FullyQualifiedName~AptitudePreset"` | `Passed! - Failed: 0, Passed: 30, Skipped: 0, Total: 30` - the existing suites, whose assertions still hold because the new fields are additive | `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs` |
| A missing choice returns 409 with `{soulPrice, freeRespecStock}` | same | implemented, not yet asserted: the `respec.payment.choice-required` arm returns `Results.Conflict(new { reason, soulPrice = outcome.PriceAmount, freeRespecStock = outcome.FreeStock })`; an unknown spelling is a 400 `respec.payment.unknown` rather than a default | same |
| `GET /respec-price` adds `freeRespecStock` and `freeAvailable` | same | implemented: the route now reads ONE `QuoteSpeciesRespec` (sharing `RespecPolicy.Quote` with the spend) and reports its soul price, its resource, the stock and `freeAvailable`, keeping `everRespecced` | same |
| Parsing happens at the edge | same | `RespecPayments.TryParse` (EP4.9) gets its first caller here; empty `payWith` stays null, so the store decides whether the choice was ambiguous | same |

**Landed since this fragment was first written (same row, same branch):**
1. DONE - `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs`: `ActivateRequest` gains `PayWith`, parsed at
   the edge (`respec.payment.unknown` -> 400), passed into `TryActivateAptitudePreset`, with
   `respec.payment.choice-required` mapped to the same 409 shape the respec route sends.
2. DONE - `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs`: `TryActivateAptitudePreset` gains
   `RespecPayment? payWith = null` AFTER `utcNow` and forwards it to the species-scope
   `TryRespecSpeciesUnlocked`; `AptitudePresetActivateOutcome` gained `PaidWith`/`FreeStock` (additive init
   properties) filled from the respec's own outcome on both the refusal and the success path.

**Landed tests (three of the four):** `gk-core/tests/FusionRpg.Server.Tests/SpeciesBuildEndpointsTests.cs` -
`With_stock_and_no_payWith_the_respec_returns_409_with_the_two_numbers`,
`A_freeRespec_payWith_spends_the_stock_and_reports_what_was_paid` and
`The_price_route_reports_the_stock_and_whether_it_is_available`, all against a real in-process host. The
fixture seeds the free-respec STOCK directly on the store's connection: `FusionRpg.Server.Tests` has no
internals access, and the public fact path was DIAGNOSED not to work in this host - sixteen placements took
a species to L21 while no `kind='empire'` row was ever written, although every input the credit's R1 gate
reads was asserted correct (`def.Side='plant'`, human empire `dave`, `KillAttribution.EmpireOf("plant")='dave'`,
roster 84). Filed in the ledger as a finding about the Server test host.

**All four acceptance points are now proved** (34/34 through the row's own filter), and proving the last
one found a real defect: the activate SUCCESS path built `AptitudePresetActivateOutcome` without
`PaidWith`/`FreeStock`, so an activation reported nothing paid even after spending a free respec. Fixed in
the same commit, on the same return the refusal path already annotated.

**Superseded remaining-work note, kept for the record:**
The fourth case, for the OTHER acceptance clause (the preset pass-through), belongs in
`gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs`, whose harness already maps the preset routes
and can create the preset this one needs: activate a species-scope preset with `payWith: "freeRespec"` and a
seeded stock, and assert the stock was spent (or that omitting the choice returns the same 409). The source
already implements and compiles the pass-through; only that proof is missing.

**Not proved:** nothing above is asserted yet, which is why the row is open.

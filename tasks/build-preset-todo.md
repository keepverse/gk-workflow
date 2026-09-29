# Tasks: `build-preset` (prefix `BP`)

Plan: [build-preset-plan.md](build-preset-plan.md) · Map:
[../docs/architecture/build-preset-map.md](../docs/architecture/build-preset-map.md) · Specs:
[../docs/architecture/build-preset/](../docs/architecture/build-preset/) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane B, after `EP`).

**Conventions used in every task below:**
- `<sid>` is the building session's id.
- Wave A = `BP1`, B = `BP2`, C = `BP3`.
- Tests run on the in-memory store (`docs/contributing/testing-standard.md`).
- A cross-program reference is written `<prefix><id>`.
- Tests assert contracts, price equality and closed vocabularies, never a count of presets, items or
  creatures.

---

## Wave A — callable gates, item loadouts, the store (`BP1`)

- [x] **BP1.1 — `PatronService.SetAsync`: lift the patron route's post-write work out of the lambda (byte-identical)** · S · deps: — · *(spec: gate-services)*
  - Acceptance:
    - Every existing patron route test and `PatronE2E` passes **unedited** (test 1). The endpoint keeps
      only its request validation, and its reason and status codes are unchanged.
    - Driving the service directly and driving the route give the same stored rows and the same reason
      (test 2). `SetAsync` enqueues the injector `patron.aura` command exactly as the route did (test 3).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Patron"`; `dotnet test tests\FusionRpg.E2E.Tests --filter "FullyQualifiedName~PatronE2E"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/PatronService.cs,gk-core/src/FusionRpg.Server/PatronEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/Gates/PatronServiceTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/PatronService.cs` (new), `gk-core/src/FusionRpg.Server/PatronEndpoints.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/Gates/PatronServiceTests.cs` (new)

- [x] **BP1.2 — `ContractService.BindAsync` / `ReleaseAsync`: lift, byte-identical** · S · deps: — · *(spec: gate-services)*
  - Acceptance:
    - Existing contract route tests and `ContractE2E` pass unedited.
    - Service-versus-route parity on stored rows and reasons. The contract/souls notification still
      fires.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Contract"`; `dotnet test tests\FusionRpg.E2E.Tests --filter "FullyQualifiedName~ContractE2E"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/ContractService.cs,gk-core/src/FusionRpg.Server/ContractEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/Gates/ContractServiceTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/ContractService.cs` (new), `gk-core/src/FusionRpg.Server/ContractEndpoints.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/Gates/ContractServiceTests.cs` (new)

- [x] **BP1.3 — `ActionLoadoutService.Set` / `Preview`: the held and mid-run predicates, named once** · S · deps: — · *(spec: gate-services)*
  - Acceptance:
    - Existing loadout route tests pass unedited, including aura ids being admitted as held
      (`LoadoutEndpoints.cs:60-63`).
    - `Preview` returns the same `LoadoutValidation` that `Set` then enforces, and writes nothing.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Loadout"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/ActionLoadoutService.cs,gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/Gates/ActionLoadoutServiceTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/ActionLoadoutService.cs` (new), `gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/Gates/ActionLoadoutServiceTests.cs` (new)

- [x] **BP1.4 — `AptitudePresetActivation.Activate`: lift the activate route (budget, materialize, check, store, broadcast); thread `payWith`** · M · deps: EP1.10, EP4.10 · *(spec: gate-services)*
  - Acceptance:
    - Existing aptitude-preset route tests pass unedited. This lifts the route as it stands **after**
      `specimen-respec-price` and `respec-free-counter`: the commander and unique branches are priced,
      and the species branch takes `payWith`.
    - Service-versus-route parity on the allocation, the preset-active row, the soul ledger and the
      free-stock ledger.
    - No new rule, price or write is introduced.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs,gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/Gates/AptitudePresetActivationTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs` (new), `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/Gates/AptitudePresetActivationTests.cs` (new)

- [x] **BP1.5 — `AptitudePresetActivation.Preview`: the read half, with no write, through the one quote per scope** · M · deps: BP1.4 · *(spec: gate-services)*
  - Acceptance:
    - `Preview`'s shares, leftover and quote equal what `Activate` writes and charges, for these cases:
      a species target paid with a free respec; a species target paid in souls; a species target with
      no choice while stock exists (refused by name, nothing written); a commander target adding
      points; a commander target taking points back; a unique target adding points; and a unique target
      taking points back (test 4).
    - After `Preview`, the row counts of the allocation, preset-active, soul-ledger and free-stock
      tables are unchanged (test 5). The species quote comes from `QuoteSpeciesRespecUnlocked` and the
      commander/unique quote from `QuoteReallocation`. No Data method is added.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePresetActivation"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs,gk-core/tests/FusionRpg.Server.Tests/Gates/AptitudePresetActivationTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/AptitudePresetActivation.cs`, `gk-core/tests/FusionRpg.Server.Tests/Gates/AptitudePresetActivationTests.cs`

- [x] **BP1.6 — `DeleteLoadout` (owner-checked, one transaction) and `LoadoutReport.AssignmentRefKindFor` (X4)** · S · deps: — (first check `tasks/item-todo.md` P1.2 for a concurrent build) · *(spec: item-loadout-apply)*
  - Acceptance:
    - An owner mismatch refuses. A delete removes both tables' rows in one transaction (test 6).
    - `AssignmentRefKindFor` maps `item` to `rolled` and `stock` to `stock`, and throws on an unknown
      kind. It is the only place the two spellings meet.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Armoury"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LoadoutReport"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs,gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs,gk-core/tests/FusionRpg.Data.Tests/Items/ArmouryTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs`, `gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/ArmouryTests.cs`, the `LoadoutReport` test

- [x] **BP1.7 — `ItemLoadoutApplyService`: preview and apply; each entry goes through the flow that owns its ref kind; `force` reports what it stripped** · M · deps: BP1.6 · *(spec: item-loadout-apply)*
  - Acceptance:
    - A conflict refuses with the cells named, and the assignment rows are unchanged (test 2). A stock
      entry with no legacy slot, or aimed at the commander, is a named plan refusal, found by preview.
    - A rolled entry goes through `ItemEquipService`. A stock entry goes through the relic wire, together
      with its `mods_json` and bindings, and neither flow writes the other's kind (test 3). A commander
      target lands in the player-scope table (test 4).
    - Applying twice leaves the same rows, and every role is `Ok` the second time (test 5). One lawn
      runtime sync runs after the last write. `Missing` entries are reported, never dropped.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemLoadout"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/Gates/ItemLoadoutApplyService.cs,gk-core/src/FusionRpg.Server/Program.cs,tests/FusionRpg.Server.Tests/ItemLoadoutApplyServiceTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/Gates/ItemLoadoutApplyService.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Server.Tests/ItemLoadoutApplyServiceTests.cs` (new)

- [x] **BP1.8 — `ItemLoadoutEndpoints`: the five armoury routes (list, save, delete, preview, apply)** · S · deps: BP1.7 · *(spec: item-loadout-apply)*
  - Acceptance:
    - The routes match `spec-armoury.md:220` exactly, with `targetId` resolved by the equip route's own
      `TryResolveTarget`.
    - Over HTTP, three tests are green: the armoury's `a_loadout_entry_whose_item_was_salvaged_returns_missing`,
      `applying_a_loadout_whose_item_is_held_elsewhere_refuses_with_LoadoutConflict`, and the new
      `force_reports_what_it_stripped` (test 1).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemLoadout"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/ItemLoadoutEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/ItemLoadoutEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/ItemLoadoutEndpoints.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemLoadoutEndpointsTests.cs` (new)

### Checkpoint 1 — the gates are callable (CP1)
- [x] The existing route tests over the patron, contract, loadout and aptitude-preset groups all pass
  with **no edit** (`git diff --stat tests/` shows only added files for those groups). — **Met
  2026-09-23**: patron (BP1.1), contract (BP1.2), action-loadout (BP1.3) and aptitude-preset
  (BP1.4/BP1.5) groups all pass unedited; the aptitude-preset group was blocked on EP1.10/EP4.10
  until those landed on the integration head.
- [x] An item loadout saves, lists, previews and applies over HTTP. A conflict refuses by cell, and
  `force` reports what it stripped. — BP1.6/BP1.7/BP1.8, 2026-09-20.

- [x] **BP1.9 — `BuildPresetPieceKind` (closed, 5) and `BuildPresetShape` (pure save-time rules)** · S · deps: EP3.3, SE4.4 · *(spec: preset-store)*
  - Acceptance:
    - The enum has exactly five members and every id round-trips. It is pinned because it is a declared
      vocabulary, and the test comment says so (test 1). An unknown stored id parses as "unknown" and
      never throws.
    - Each shape rule refuses by its own code: `build-preset.empty`, `.patron.multiple`, `.field.shape`,
      `.patron.outside-field`, `.aptitudes.scope`, `.skills.shape`, `.name.missing` (test 2, pure half).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildPreset"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetPieceKind.cs,gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetShape.cs,gk-core/tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetShapeTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetPieceKind.cs` (new), `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetShape.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetShapeTests.cs` (new)

- [x] **BP1.10 — `build-preset.v1.json` (the first version of a new domain) and the `BuildPresetTuning` loader and hub; server load (H7)** · S · deps: BP1.9 · *(spec: preset-store)*
  - Acceptance:
    - `softMaxBuildPresets` is a `long` of at least 1, and a missing key is a load rejection naming it.
      The code comment says this is a list-length soft refusal, not a §11 cap.
    - The server `Program.cs` loads `v1` beside the aptitude-presets load, in the same commit. Later
      revisions go only through `publish.py`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildPresetTuning"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetTuning.cs,gk-core/data/tuning/build-preset.v1.json,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetTuningTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetTuning.cs` (new), `gk-core/data/tuning/build-preset.v1.json` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetTuningTests.cs` (new)

- [x] **BP1.11 — `RpgStore.BuildPresets`: two tables born `(save_id, empire_id)`, CRUD, validate-on-read, a human-only `EmpireRef` API** · M · deps: BP1.10, SE4.12, SE4.14 (the first slice; reuse `SE4.37`'s `RequireHumanEmpire` if it has landed) · *(spec: preset-store)*
  - Acceptance:
    - Save then read returns every piece in ordinal order, and the order of pieces in the request does
      not matter (test 3).
    - Retire the patron, delete the aptitude preset, delete the item loadout and retire a field member:
      each piece reads `Missing` with its reason, and the rows read equal the rows saved (test 4).
      Deleting a build preset never cascades (test 5). Create refuses at `softMaxBuildPresets`, read
      from tuning (test 6).
    - Another save's id refuses update and delete. A non-human `EmpireRef` throws
      `EmpireScopeNotWidened` (test 7).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPreset"`; `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs,gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs` (new)

- [x] **BP1.12 — `BuildPresetEndpoints`: `GET`/`POST`/`PUT`/`DELETE /api/build-presets…`** · S · deps: BP1.11 · *(spec: preset-store)*
  - Acceptance:
    - The four routes serve list-with-validated-pieces, create (soft max), replace (bumps `revision`)
      and delete. The wire `playerId` is the `SaveId` (R17).
    - Every shape refusal reaches the client by its code, and nothing is written on a refusal.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetEndpoints"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs` (new)

---

## Wave B — appliers, orchestrator, capture (`BP2`)

- [x] **BP2.1 — Extract the patron precondition: `PatronPreconditionsUnlocked(…, assumeBound)` and `QuotePatron`** · S · deps: BP1.1 · *(spec: piece-appliers)*
  - Acceptance:
    - `SetPatron` calls the extracted function with `assumeBound = false`, and its existing tests pass
      unedited.
    - `QuotePatron` refuses for exactly the reasons `SetPatron` refuses. It prices `switchCostSouls` on a
      switch, and returns 0 on a first designation or a replay (test 4, patron half).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Patron"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs,gk-core/tests/FusionRpg.Data.Tests/PatronQuoteTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs`, `gk-core/tests/FusionRpg.Data.Tests/PatronQuoteTests.cs` (new)

- [x] **BP2.2 — Extract the contract preconditions: bind and release; `QuoteBind` / `QuoteRelease`** · S · deps: BP1.2 · *(spec: piece-appliers)*
  - Acceptance:
    - `BindContract` and `ReleaseContract` call the extracted functions, and their existing tests pass
      unedited.
    - Each quote refuses exactly as its write does. A bind prices `UpkeepPerDay` and is free when that
      creature's day is already paid (`bind:{id}:{day}`). A release is free.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Contract"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs,gk-core/tests/FusionRpg.Data.Tests/ContractQuoteTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs`, `gk-core/tests/FusionRpg.Data.Tests/ContractQuoteTests.cs` (new)

- [ ] **BP2.3 — `IBuildPresetPieceApplier` and its records; `PatronApplier` and `SkillsApplier`; registered as an `IEnumerable`** · M · deps: BP2.1, BP1.3, BP1.12 · *(spec: piece-appliers)*
  - Acceptance:
    - A `Missing` piece row previews as `build-preset.piece.missing:{kind}`.
    - The patron applier previews against `plan.WillBeBound(id)` and applies through `PatronService`. The
      skills applier previews through `ActionLoadoutService.Preview` and applies through `Set`.
    - For both kinds, preview equals apply (test 2), and preview writes nothing (test 3, these kinds).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/IBuildPresetPieceApplier.cs,src/FusionRpg.Server/BuildPresets/Appliers/PatronApplier.cs,src/FusionRpg.Server/BuildPresets/Appliers/SkillsApplier.cs,gk-core/src/FusionRpg.Server/Program.cs,tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/IBuildPresetPieceApplier.cs` (new), `.../Appliers/PatronApplier.cs` (new), `.../Appliers/SkillsApplier.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs` (new)

- [ ] **BP2.4 — `FieldApplier`: an exact-set diff, capacity after the diff, wardens outside the diff, the old patron's release deferred** · M · deps: BP2.2, BP2.3 · *(spec: piece-appliers)*
  - Acceptance:
    - A field piece that omits a warden applies and leaves the warden bound.
    - A preset that replaces the patron and drops the old one releases the old one after the switch, as a
      deferred release. A preset that drops the current patron without replacing it refuses with
      `contract.is-patron` (test 5).
    - Preview equals apply, and preview writes nothing (tests 2 and 3, field).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/Appliers/FieldApplier.cs,tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/Appliers/FieldApplier.cs` (new), `tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs`

- [ ] **BP2.5 — `AptitudesApplier`: per target through `AptitudePresetActivation`; a species target gets a `PaymentChoice`; commander and unique targets pay souls only** · M · deps: BP1.5, BP2.3 · *(spec: piece-appliers)*
  - Acceptance:
    - A species respec with stock at 1 or more and no choice returns a `PaymentChoice` and applies
      nothing for that target. A unique or commander target never produces a `PaymentChoice` or a
      `freeRespec` line (test 8).
    - Choices resolve in target order against a running stock in `PlanState`. A second `freeRespec`
      past the stock refuses with `build-preset.free-respec.insufficient` at preview.
    - Prices come as `PriceLine`s whose `Resource` is `souls` or `freeRespec`, and the two are never
      summed together.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/Appliers/AptitudesApplier.cs,tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/Appliers/AptitudesApplier.cs` (new), `tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs`

- [ ] **BP2.6 — `GearApplier`: per target through `ItemLoadoutApplyService`; a double claim across targets refuses** · S · deps: BP1.7, BP2.3 · *(spec: piece-appliers)*
  - Acceptance:
    - Two gear pieces naming one rolled copy refuse at preview, by name (test 6). The price is always 0.
    - `force` passes through only when the orchestrator passes it.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/Appliers/GearApplier.cs,tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/Appliers/GearApplier.cs` (new), `tests/FusionRpg.Server.Tests/BuildPresets/AppliersTests.cs`

- [ ] **BP2.7 — The program's contract tests: preset price equals by-hand price; preview writes nothing; the build-preset namespaces reference no Hub type** · M · deps: BP2.4, BP2.5, BP2.6 · *(spec: piece-appliers)*
  - Acceptance:
    - On two identical in-memory stores, a preset apply and the equivalent by-hand calls give equal
      soul-ledger deltas entry for entry, equal free-stock deltas, and equal churn counters
      (`rpg_species_respec`, `rpg_allocation_respec`) at one injected clock (test 1). This runs for each
      kind and for all five combined, covering: first patron and a switch; a species respec paid free,
      paid in souls, and with no stock; commander and unique targets adding and taking back; a same-day
      re-bind and a fresh bind.
    - After any preview, the ledger, allocation, patron, contract, assignment and loadout tables are
      unchanged (test 3).
    - An architecture test: `FusionRpg.Server.BuildPresets` and `FusionRpg.Core.BuildPresets` reference
      no `DerivedModifier`, `ActorHub` or `ContributionSourceIds` (test 7, D6).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetAppliers|FullyQualifiedName~BuildPresetPriceEquality"`; `.\scripts\guard-actor-hub.ps1`; `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Server.Tests/BuildPresets/PriceEqualityTests.cs,tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetArchitectureTests.cs -Session <sid>`
  - Files: `tests/FusionRpg.Server.Tests/BuildPresets/PriceEqualityTests.cs` (new), `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetArchitectureTests.cs` (new)

- [ ] **BP2.8 — `BuildPresetPlan` (pure): the structural `Steps`, a `checked` price sum per resource, `DerivedCorrelation`** · S · deps: BP1.9 · *(spec: apply-orchestrator)*
  - Acceptance:
    - `Steps` membership and order are pinned, with the structural reason in the test comment.
    - `DerivedCorrelation` is deterministic, starts with `bp-`, and is at most 64 characters. An
      overflowing sum throws and never wraps (test 8).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildPresetPlan"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/BuildPresets/BuildPresetPlan.cs,tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetPlanTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Core/BuildPresets/BuildPresetPlan.cs` (new), `tests/FusionRpg.Core.Tests/BuildPresets/BuildPresetPlanTests.cs` (new)

- [ ] **BP2.9 — `POST /api/build-presets/{id}/preview`: a whole-plan walk, totals per resource, affordability, and choices** · M · deps: BP2.7, BP2.8 · *(spec: apply-orchestrator)*
  - Acceptance:
    - A preset with one refusing piece among five valid ones names that piece and writes nothing
      (test 1). An unaffordable plan refuses with the shortfall, in souls or in free respecs (test 2).
    - An unanswered species choice is returned in `choices`, with no default. The rest of the plan is
      still previewed.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetApply"`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/BuildPresetOrchestrator.cs,gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs,tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/BuildPresetOrchestrator.cs` (new), `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs` (new)

- [ ] **BP2.10 — `POST /api/build-presets/{id}/apply`: stale guard, re-preview, price guard, the ordered execution, one apply per player at a time** · M · deps: BP2.9 · *(spec: apply-orchestrator)*
  - Acceptance:
    - A stale `presetRevision` refuses. A price that rose after the preview (a by-hand specimen respec in
      between) refuses with both numbers (test 3). A choice of `freeRespec` whose stock was spent in
      between refuses `build-preset.free-respec.insufficient` and never switches silently to souls
      (test 3a). A missing species choice refuses by name, and the same apply with the choice succeeds
      (test 3b).
    - A patron swap with the old patron's release completes in one apply (test 6).
    - Every "applied" assertion reads the layer back through its normal route, never from the apply
      response (test 7). The per-player lock is commented as a structural limit.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetApply"`; `.\scripts\guard-actor-hub.ps1`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/BuildPresets/BuildPresetOrchestrator.cs,gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs,tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/BuildPresets/BuildPresetOrchestrator.cs`, `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs`

- [ ] **BP2.11 — Convergence: an interrupted apply finishes on retry without a second charge; steps 5–7 are order-independent** · S · deps: BP2.10 · *(spec: apply-orchestrator)*
  - Acceptance:
    - Inject a failure after step 3. The second apply with the same `correlationId` completes, and the
      soul-ledger and free-stock totals each equal one uninterrupted apply's (test 4).
    - Steps 5–7 applied in every permutation leave identical stored rows (test 5).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetApply"`
  - Files: `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetApplyTests.cs`

### Checkpoint 2 — a preset applies (CP2)
- [ ] BP2.7's price equality is green for every kind and for the combined preset.
- [ ] A five-kind preset previews at the by-hand price, applies, and a retry charges nothing. Each layer
  reads back through its own route (RPG Server scope, on a real save the gameplay could have produced;
  never a debug-fabricated row).

- [x] **BP2.12 — `AptitudePresetCapture.FromAllocation` (pure): points to shares of the spent total, largest remainder, summing to 1000** · S · deps: — · *(spec: capture-current)*
  - Acceptance:
    - Any non-empty allocation, including a single aptitude or many ties, sums to exactly 1000, with ties
      broken by id (test 1).
    - `Materialize(FromAllocation(a), budget)` differs from `a` per row by at most
      `⌈budget / 1000⌉ + 1`, computed from the budget under test and never a literal (test 2). The
      arithmetic is `long` and `checked`, multiplying by 1000 before dividing once.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudePresetCapture"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetCapture.cs,tests/FusionRpg.Core.Tests/Stats/AptitudePresetCaptureTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetCapture.cs` (new), `tests/FusionRpg.Core.Tests/Stats/AptitudePresetCaptureTests.cs` (new)

- [ ] **BP2.13 — Extract the transaction-scoped cores `SaveAptitudePresetUnlocked`, `SaveLoadoutUnlocked`, `SaveBuildPresetUnlocked` (public methods unchanged)** · S · deps: BP1.11, BP1.6 · *(spec: capture-current)*
  - Acceptance:
    - The three public save methods are thin wrappers. Their existing tests (aptitude preset, armoury,
      build preset) pass unedited.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AptitudePreset|FullyQualifiedName~Armoury|FullyQualifiedName~BuildPreset"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`

- [ ] **BP2.14 — `CaptureBuildPreset` (one transaction) and `POST /api/build-presets/capture`** · M · deps: BP2.12, BP2.13, BP1.12 · *(spec: capture-current)*
  - Acceptance:
    - When the active aptitude preset still materializes to the current allocation, it is referenced and
      no new row is written (test 3). Otherwise a `player` preset is created through `FromAllocation`.
    - With a library at its soft max, capture refuses by that library's name, and afterwards no item
      loadout, aptitude preset or build preset row exists (test 5).
    - Each skip is named in the response: no patron, auto-equipped skills (never frozen), empty gear,
      empty allocation (test 6). Wardens are excluded from the captured field (test 7).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~BuildPresetCapture"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetCapture"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs,gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs,tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetCaptureTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`, `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, `tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetCaptureTests.cs` (new)

- [ ] **BP2.15 — Capture then apply restores the captured build (read back per layer)** · S · deps: BP2.14, BP2.10 · *(spec: capture-current)*
  - Acceptance:
    - Capture; change the patron, field, skills, gear and aptitudes by hand; apply the captured preset.
      Each layer then reads back equal to the captured state through its own route, with aptitudes held
      to the lean equality of BP2.12's bound (test 4).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BuildPresetCapture"`
  - Files: `tests/FusionRpg.Server.Tests/BuildPresets/BuildPresetCaptureRoundTripTests.cs` (new)

### Checkpoint 3 — keep what you have (CP3)
- [ ] BP2.15 green. The captured aptitude and gear parts are rows in their own libraries and are listed
  by those libraries' own routes.

---

## Wave C — the surface (`BP3`)

- [x] **BP3.1 — `/idea-ui` pass: the host, recipe tree and piece choices, and the relabel copy (X1)** · S · deps: — (layout-only; runs early) · *(spec: preset-surface)*
  - Acceptance:
    - The pass is recorded per `docs/architecture/idea-ui-phase.md`. It names the host, the recipe tree
      (reusing the aptitude preset console's gallery where it fits), any new pieces with their
      `spec-<piece-id>.md`, and the "Aptitude presets" / "Build presets" copy.
    - `docs/design/gui-lego/recipes/build-preset-console.json` is committed.
  - Verify: `python scripts/audit-doc-citations.py <the recorded idea-ui doc>`
  - Files: the `/idea-ui` output doc, `docs/design/gui-lego/recipes/build-preset-console.json` (new)

- [ ] **BP3.2 — `lib/bus/buildPresets.ts` API client and the pure `foldBuildPresetConsoleVm`** · M · deps: BP2.10, BP2.14 · *(spec: preset-surface)*
  - Acceptance:
    - The fold is pure and total: every `phase`, and a `Missing` piece counted and shown. Prices render
      from `valueRaw`, with `valueText` formatted in the fold (GG-46). The fold invents no number
      (test 1).
    - A species choice shows both options with no default. A commander or unique target shows a price
      only.
  - Verify: `cd web\fusion-rpg-web; npm test -- foldBuildPresetConsoleVm; npm run build`
  - Files: `web/fusion-rpg-web/src/lib/bus/buildPresets.ts` (new), `web/fusion-rpg-web/src/features/gui-lego/foldBuildPresetConsoleVm.ts` (new), its vitest

- [ ] **BP3.3 — The closed `buildPresetConsoleBus` and the host: `build.apply` only after a preview, never with an unanswered choice** · M · deps: BP3.1, BP3.2 · *(spec: preset-surface)*
  - Acceptance:
    - The event list equals the declared union. It is a closed vocabulary, pinned with its reason
      (test 2).
    - The host refuses `build.apply` without a preview for the current revision (test 3), or while any
      species choice is unanswered. It sends `acceptedTotals` and `respecPayment` exactly as the last
      preview used them.
    - The host fetches and pieces render. There is no fetch or SignalR inside a piece, and it mounts in
      the existing panel host.
  - Verify: `cd web\fusion-rpg-web; npm test -- buildPresetConsoleBus; npm run build`
  - Files: `web/fusion-rpg-web/src/features/gui-lego/buildPresetConsoleBus.ts` (new), the host component (location from BP3.1), their vitests

- [x] **BP3.4 — Relabel the aptitude console "Aptitude presets" (X1)** · XS · deps: BP3.1 · *(spec: preset-surface)*
  - Acceptance:
    - `AptitudePresetConsoleHost.tsx:384` and the entry labels in `foldAptitudesSurfaceVm.ts:205,262`
      read "Aptitude presets". "Build presets" names only the new surface.
    - `npm run extract` has been run, and any locale change is committed.
  - Verify: `cd web\fusion-rpg-web; npm test -- --run aptitude; npm run build; npm run extract`
  - Files: `gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx`, `gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts`, `gk-web/web/fusion-rpg-web/src/i18n/locales/**`

- [ ] **BP3.5 — Playwright `build-preset.spec.ts` (CP4); rewrite the guide page from "Vision"** · S · deps: BP3.3, BP3.4 · *(spec: preset-surface)*
  - Acceptance:
    - Capture; preview, with a price and a refusal visible by name; apply. The patron, contracts and
      aptitude surfaces then show the new state from their own reads (test 4).
    - `docs/guide/mechanisms/build-presets.md` describes what ships, rewritten only once this test is
      green (map X2).
  - Verify: `cd web\fusion-rpg-web; npm run test:e2e -- build-preset`
  - Files: `web/fusion-rpg-web/e2e/build-preset.spec.ts` (new), `docs/guide/mechanisms/build-presets.md`

### Checkpoint 4 — the player can reach it (CP4)
- [ ] BP3.5 Playwright green; the guide page has been updated; the aptitude console has been relabelled.
- [ ] `.\scripts\test-fast.ps1 -AllDefault` green once. This is the end of a large feature that crosses
  Core, Data, Server and Web (AGENTS.md conditions 1 and 2).

- [ ] **`BP2.3` needs a piece-state type nobody has built, and a sketch of it exists only in a
  worktree about to be cleared** · S · deps: BP2.3 · *(filed by manager adjudication, 2026-09-26,
  from the `cmdc/bp-1` worktree)* — **cross-reference, not a new task.** `BP2.3`'s first acceptance
  clause is *"A `Missing` piece row previews as `build-preset.piece.missing:{kind}`"*, which needs a
  piece state carrying `Missing`. `git grep ValidatedPiece` at `features/mega-merge` returns **one
  hit, and it is a spec** — `docs/architecture/build-preset/spec-piece-appliers.md:30,33,127`, where
  `ValidatedPiece` appears in the applier interface signatures. **No such type exists in code.**

  The `cmdc/bp-1` worktree holds a sketch: `src/FusionRpg.Core/BuildPresets/ValidatedPiece.cs`
  (37 lines) defining `enum BuildPresetPieceState { Present = 0, Missing = 1 }` and a
  `ValidatedPiece` record, documented as *"The reference is gone … The row still comes back — a hole
  the player can see, never a silently shorter preset."* **It was deliberately not landed**, for two
  reasons both measured here. `BP2.3`'s own `Files` line is entirely Server-side
  (`src/FusionRpg.Server/BuildPresets/…`, `Program.cs`, `tests/…/AppliersTests.cs`), so a Core-side
  type is not where the row asks for it. And the same worktree's `RpgStore.BuildPresets.cs` is **354
  lines against integration's 455**, so its store design is an earlier one the shipped
  implementation replaced. Committing it would add a type nothing calls and regress a file that has
  moved on.

  **The spec's status line is the stale part here, not the code.** `spec-piece-appliers.md` reads
  **"Status: spec, not reviewed, no build authorized"** while `BP2.3`–`BP2.7` sit open in this
  ledger — so the module *is* authorized and the header is what has not been updated. Worth fixing
  before BP2.3 is built rather than after: a header saying "no build authorized" is exactly what
  would make the next reader believe the open rows are wrong.
  **Acceptance for whoever builds BP2.3:** name the piece-state type, and either update
  `spec-piece-appliers.md`'s status line or record why the spec is still unauthorized.


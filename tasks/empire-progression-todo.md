# Tasks: `empire-progression` (prefix `EP`)

Plan: [empire-progression-plan.md](empire-progression-plan.md) · Map:
[../docs/architecture/empire-progression-map.md](../docs/architecture/empire-progression-map.md) · Specs:
[../docs/architecture/empire-progression/](../docs/architecture/empire-progression/) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane B).

**Conventions used in every task below:**
- `<sid>` is the building session's id.
- Wave A = `EP1`, B = `EP2`, C = `EP3`, D = `EP4`, and deferred = `EP5`.
- A cross-program reference is written `<prefix><id>`. `save-identity` is `SE4.11`–`SE4.14` (the first slice),
  `SE4.20` (the migration runs in `Init`, the **H2** anchor), `SE4.21`–`SE4.22` (the Tier A API and
  Zomboss as an empire) and `SE4.31`–`SE4.33` (REST and SignalR).
- **Pin moves** are one-line edits that a tuning publish forces into its own commit (T5, H7). They are
  listed as "+ pins (rg)" and are exempt from the five-file budget.
- Tests assert contracts and closed vocabularies, never a count of species, shapes, levels or presets.

---

## Wave A — assignment ladder, default build, unique respec price (`EP1`)

- [x] **EP1.1 — Fix first: `species-favour` zero-fills a real 5-key plan row (W3)** · XS · deps: — · *(spec: assign-ladder)*
  - Acceptance:
    - A `species-favour` fill from a plan row read out of the committed `_species-build-plan.json` by id
      succeeds, zero-fills the missing aptitudes, and sums to 1000.
    - An empty map, an unknown aptitude id and a non-normalised sum each refuse with their own reason:
      `autoAssign.favour.empty`, `.unknownAptitude`, `.notNormalised`.
    - `autoAssign.favour.incomplete` no longer exists in `src/`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AutoAssign"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs,tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAutoAssignTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs`, `tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAutoAssignTests.cs`

- [x] **EP1.2 — `AssignLadder.Suggest`: an ordered walk over the closed rules, ending on `even`** · S · deps: EP1.1 · *(spec: assign-ladder)*
  - Acceptance:
    - `Suggest(AssignContext, AssignLadderTuning)` returns the first rung that succeeds, with every
      skipped rung and its named reason in `Skipped`. `posture` resolves to one of the three posture
      rule ids, never a seventh id.
    - Two tuning orders give two winners for one context (the order is data). Every combination of
      absent inputs returns a suggestion (totality).
    - The R23 commander context (no preset, no favour, no posture, `FavourAllowed = false`) returns
      `even` and records three skips. Adding an active preset to that context makes `active-preset` win
      (spec test 9).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AssignLadder"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs,tests/FusionRpg.Core.Tests/ClassSystem/AssignLadderTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs` (new), `tests/FusionRpg.Core.Tests/ClassSystem/AssignLadderTests.cs` (new)

- [x] **EP1.3 — Publish `aptitude-presets.v2` with `assignLadder.order`; loader contract; move pins (H7)** · S · deps: EP1.2 · *(spec: assign-ladder)*
  - Acceptance:
    - `v2` is published by `publish.py` (never hand-written). The loader rejects, naming the key, an
      order that does not end on `even`, a duplicate, or an unknown id. The comment says the terminal
      rung is structural.
    - The server `gk-core/src/FusionRpg.Server/Program.cs:275`, `gk-forge/tools/ProveHubCombat/Program.cs:125` and
      `gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs` read `v2` in the same commit.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudePresetTuning|FullyQualifiedName~AssignLadder"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetTuning.cs,gk-core/data/tuning/aptitude-presets.v2.json,gk-core/src/FusionRpg.Server/Program.cs,gk-forge/tools/ProveHubCombat/Program.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetTuning.cs`, `gk-core/data/tuning/aptitude-presets.v2.json` (published) + pins (rg)

- [x] **EP1.4 — `POST /api/aptitude-presets/suggest`: a draft only, and it never persists** · S · deps: EP1.3 · *(spec: assign-ladder)*
  - Acceptance:
    - With `rule` omitted, the route walks the ladder. With `rule` given, only that rule runs. The
      response is `{ruleId, rows, skipped, draftShares, leftover}`, with `draftShares` from
      `AptitudePresetMaterialize`.
    - `rpg_aptitude_allocation` reads back byte-identical after any call (spec test 8).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs`

- [x] **EP1.5 — The FE's `runAutoAssign` calls `/suggest`; delete the TypeScript fill mirror (W1)** · S · deps: EP1.4 · *(spec: assign-ladder)*
  - Acceptance:
    - `runAutoAssign.ts` calls the route and computes no share. `autoAssign.ts` keeps only its types
      and `APTITUDE_IDS`. The mirror's own unit tests are removed with it.
    - A vitest asserts that the route is called and that no share arithmetic runs in the FE (spec
      test 7).
  - Verify: `cd web\fusion-rpg-web; npm test -- --run aptitude; npm run build`
  - Files: `gk-web/web/fusion-rpg-web/src/features/aptitudes/runAutoAssign.ts`, `gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.ts`, `gk-web/web/fusion-rpg-web/src/lib/bus/aptitudePresets.ts`, the aptitude vitest files

- [x] **EP1.6 — `RespecPolicy`: `RespecPriceTuning`, re-typed `PriceOf`, `Quote`, `IsRespec` (the species price stays byte-identical)** · M · deps: — · *(spec: specimen-respec-price)*
  - Acceptance:
    - `IsRespec` is true exactly when some aptitude decreases: a property test over random pairs, plus
      the four named cases (spec test 1).
    - `PriceOf(RespecPriceTuning, count)` and `Quote(tuning, count, freeStock)` exist.
      `SpeciesBuildTuning.SpeciesRespec` is the species view. Every existing `SpeciesRespecTests` case
      passes unedited (test 7).
    - The species spend and the `/respec-price` preview both pass `tuning.SpeciesRespec`. No second
      price formula exists.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy|FullyQualifiedName~SpeciesBuildTuning"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs,gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs,gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs,tests/FusionRpg.Core.Tests/Stats/RespecPolicyTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs`, `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs`, `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs`, `tests/FusionRpg.Core.Tests/Stats/RespecPolicyTests.cs`

- [x] **EP1.7 — Publish `species-build` (sequence order 1): the three unique respec keys; `UniqueRespec` view; move pins (H7)** · S · deps: EP1.6 · *(spec: specimen-respec-price)*
  - Acceptance:
    - `uniqueRespecBasePrice`, `uniqueRespecEscalationPermille` and `uniqueRespecDecayDays` are
      published at the species working values. A missing key is a load rejection naming it.
    - Every pin moves in this commit: the server `gk-core/src/FusionRpg.Server/Program.cs:165`,
      `gk-forge/tools/CreatureBuildPlanGen`,
      `gk-forge/tools/ProveHubCombat`, `SpeciesBuildPlannerTests.cs:175`, and `gk-forge/tools/_TempSeedSpecies` (moved or
      deleted by its owner).
    - `CreatureBuildPlanGen --check` stays green (the committed plan is byte-identical).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildTuning|FullyQualifiedName~SpeciesBuildPlanner"`; `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs,gk-core/data/tuning/<species-build.vN>.json,gk-core/src/FusionRpg.Server/Program.cs,gk-forge/tools/CreatureBuildPlanGen/Program.cs,gk-forge/tools/ProveHubCombat/Program.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs`, `data/tuning/species-build.v{next}.json` (published) + pins (rg)

- [x] **EP1.8 — `rpg_allocation_respec` and the one gate `TryReallocate(Unlocked)` / `QuoteReallocation` for the `Commander` and `UniqueCreature` scopes** · M · deps: EP1.7, SE4.14 (`OwnsSpecimenUnlocked`, `empireId`; save-identity mismatch 1) · *(spec: specimen-respec-price)*
  - Acceptance:
    - Adding points is free and writes no ledger or counter row. A take-back charges
      `PriceOf(UniqueRespec, decayedCount)`, bumps the counter, and costs the next step next time;
      decay follows `DecayDays` (tests 2 and 3). The commander pool and a specimen keep separate
      counters (test 4).
    - A replayed correlation id charges once. The reasons are the new `respec-unique` and
      `respec-commander` (test 5).
    - Every refusal writes nothing: insufficient souls, a missing correlation id, a specimen the caller
      does not own (including a Zomboss specimen of the same save), and a non-human payer (test 6). No
      path reads the free stock (test 11).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationRespec"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs,gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs,gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AllocationRespec.cs` (new), `gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs`, `gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs` (new)

- [x] **EP1.9 — The by-hand routes go through the gate; `POST /api/aptitudes/respec-quote`; the one-writer architecture test** · M · deps: EP1.8 · *(spec: specimen-respec-price)*
  - Acceptance:
    - `/api/aptitudes/allocate` and `/unique/allocate` call `TryReallocate`. The body gains
      `correlationId?`, and the response gains `priced`, `priceAmount`, `respecCount` and
      `soulBalance`. Refusal strings reuse `correlation.missing` and `souls.insufficient`.
    - `respec-quote` equals what the save then charges, for counts 0 to 3 (test 8).
    - An architecture test: outside `RpgStore.AllocationRespec.cs`, the only writers of the
      `Commander` and `UniqueCreature` scopes are `RpgStore.Aptitudes.cs` and `DerivedAuditActor.Seed`
      (test 9).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~AllocationWriter"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs,gk-core/tests/FusionRpg.Guard.Tests/AllocationWriterGuardTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs`, `gk-core/tests/FusionRpg.Guard.Tests/AllocationWriterGuardTests.cs` (new)

- [x] **EP1.10 — Preset activation's commander and unique branches call `TryReallocateUnlocked` in the activation transaction** · S · deps: EP1.9 · *(spec: specimen-respec-price)*
  - Acceptance:
    - Activating over a commander or specimen charges exactly what the same change charges by hand:
      the soul-ledger deltas are equal entry for entry, and the `rpg_allocation_respec` rows are equal
      at one injected clock (test 10).
    - A respec activation without a `correlationId` refuses with `correlation.missing` and writes
      nothing.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AptitudePreset|FullyQualifiedName~AllocationRespec"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs,gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs`, `gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs`

- [x] **EP1.11 — FE: quote before Confirm; send a fresh `correlationId` when the change is a respec** · S · deps: EP1.9 · *(spec: specimen-respec-price)*
  - Acceptance:
    - On Confirm the sheet calls `respec-quote`. When `isRespec` is true it shows the soul price before
      saving and sends a new `correlationId`.
    - The FE never decides "is this a respec" and never computes a price (a vitest over the host).
  - Verify: `cd web\fusion-rpg-web; npm test -- --run aptitude; npm run build`
  - Files: `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`, `gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts`, `gk-web/web/fusion-rpg-web/src/lib/bus/queries.ts`, `gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx`

- [x] **EP1.12 — Before-image: list the golden fixtures that hold a levelled specimen with no explicit allocation** · XS · deps: — · *(spec: default-build, testing 8)*
  - Acceptance:
    - The fixtures that EP1.14 is predicted to move are listed (grep the battle, expedition and siege
      fixtures for levelled uniques with an empty `UniqueCreature` allocation). The list is kept in the
      builder's session notes, to be quoted in EP1.14's commit.
    - `.\scripts\test-fast.ps1 -AllDefault` is run once on the pre-change tree, and its failures are
      recorded as the baseline. A failure there that predates the change is never blamed on EP1.14.
  - Verify: `.\scripts\test-fast.ps1 -AllDefault` (baseline only; this is the one place the spec asks for it before the change)
  - Files: none (evidence only)

- [x] **EP1.13 — `EffectiveUniqueAllocation(Unlocked)`: explicit wins wholesale, else the ladder's default at the specimen's own budget** · M · deps: EP1.3 · *(spec: default-build)*
  - Acceptance:
    - A specimen above level 1 with no explicit allocation resolves its species' plan distribution,
      with points summing to its budget, asserted as a relation and never a literal (test 1). One
      explicit point replaces the whole default (test 2). A level-1 specimen resolves Empty with
      `IsDefault = true` (test 3).
    - A resolved allocation carries no `CreatureType`-scope points (test 6, the ownership row).
    - Distribution rungs go through `UniqueCreatureAllocation.Baseline`, and the `active-preset` rung
      goes through `Materialize`. No third favour-to-points function is written.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EffectiveUnique"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs,gk-core/src/FusionRpg.Core/Stats/Aptitudes/EffectiveAllocation.cs,gk-core/tests/FusionRpg.Data.Tests/Aptitudes/EffectiveUniqueAllocationTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `gk-core/src/FusionRpg.Core/Stats/Aptitudes/EffectiveAllocation.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/Aptitudes/EffectiveUniqueAllocationTests.cs` (new)

- [x] **EP1.14 — Every production reader of the unique scope calls the resolver; a Guard test blocks bypasses; golden re-bless (own commit)** · M · deps: EP1.13, EP1.12; coordinate with `SP1.2` (layer-source-selector) on `RpgStore.WorldTurns.cs` · *(spec: default-build)*
  - Acceptance:
    - The sheet and injector hydrate, `UniqueActorHubCompose`, both `WebMatchService` sites and the
      siege member read (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:520-528`, through the
      `Unlocked` sibling) all read the
      resolver. `grep -rn "AllocationScope.UniqueCreature" src` shows no raw read outside the allowlist.
    - The Guard `UniqueAllocationReaderGuardTests` fails on a raw
      `LoadAllocation(… UniqueCreature …)` outside the resolver and the allocate write path (test 5).
    - The goldens that moved are exactly EP1.12's list, each explained. **This commit moves goldens for
      this cause only.** It is not an H1 step; see the plan's "Golden moves" section.
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~UniqueAllocationReader"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~WebMatch"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs,gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs,gk-core/src/FusionRpg.Server/WebMatchService.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/tests/FusionRpg.Guard.Tests/UniqueAllocationReaderGuardTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/tests/FusionRpg.Guard.Tests/UniqueAllocationReaderGuardTests.cs` (new)

- [x] **EP1.15 — Cache trigger T3: every specimen level-up seam broadcasts `AptitudesUpdated(unique, instanceId)`** · S · deps: EP1.14 · *(spec: default-build)*
  - Acceptance:
    - Lawn capture ingest, expedition collect (`RpgStore.Expeditions.cs:318`'s caller) and the debug
      award route (`UniqueActorEndpoints.cs:115`) broadcast when `levelsGained > 0`.
    - T1–T4 each have their own test. T1 and T3 are order-independent: allocate then level up, and level
      up then allocate, both end on the right effective value (test 4).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~UniqueActor"`; `.\scripts\verify-change.ps1 -Paths <the three seam files>,gk-core/tests/FusionRpg.Server.Tests/UniqueDefaultTriggerTests.cs -Session <sid>`
  - Files: the lawn capture ingest seam, the expedition collect endpoint, `gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/UniqueDefaultTriggerTests.cs` (new)

- [x] **EP1.16 — `POST /api/aptitude-presets/suggested`: the `systemCopy` producer (W4)** · S · deps: EP1.13 · *(spec: default-build)*
  - Acceptance:
    - The route writes one preset of kind `systemCopy` whose rows equal the current suggestion, named
      after the winning rung unless a `name` is given.
    - Past `softMaxPresets` it refuses exactly as a player preset does (test 7).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs`

- [x] **EP1.17 — The sheet labels a default as a default (`isDefault`, `defaultRuleId`)** · S · deps: EP1.14 · *(spec: default-build)*
  - Acceptance:
    - `ProjectUniqueState` returns `isDefault` and `defaultRuleId`.
    - The aptitude sheet shows "Suggested build (<rule>)" from those fields, with the copy from the
      catalog and never an FE string union. A vitest asserts that the label follows the field.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`; `cd web\fusion-rpg-web; npm test -- --run aptitude; npm run build`
  - Files: `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`, `gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx`

- [x] **EP1.18 — Supersede `aptitude-sheet` E3 in its spec (map ask, X8)** · XS · deps: EP1.14 · *(spec: default-build; map "Asks filed")*
  - Acceptance:
    - `docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md:55-56` gains a one-line
      supersession pointing at `empire-progression` D1 (the default only; E1 is unchanged).
  - Verify: `python scripts/audit-doc-citations.py docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md`
  - Files: `docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md`

- [x] **EP1.19 — `/idea-ui` pass for the auto-assign control: placement and the label catalog key** · S · deps: — · *(spec: auto-assign-control)*
  - Acceptance:
    - The pass is recorded (per `docs/architecture/idea-ui-phase.md`) and names the host piece or panel
      chrome, the layout, and the `*-catalog.v{n}.json` key for the rule labels. It decides layout
      only; C1–C7 are not re-decided.
  - Verify: `python scripts/audit-doc-citations.py <the recorded idea-ui doc>`
  - Files: the `/idea-ui` output doc (path decided by the pass)
  - **Done:** `docs/architecture/empire-progression/auto-assign-control-ideal.md`. Decision: new piece
    `auto-assign-rule-strip` in the existing `aptitudes-console` recipe's `hero` slot (reuses
    `preset-action-strip`'s disabled/title pattern), no new layer/surface. Catalog key:
    `aptitude-auto-assign-catalog.v1.json` (new, for EP1.20 to publish — H7 applies then). C1-C7
    untouched.

- [x] **EP1.20 — The auto-assign control emits `aptitude.autoAssign { rule }` from the server's rule list (W2)** · S · deps: EP1.19, EP1.4 · *(spec: auto-assign-control)*
  - Acceptance:
    - Choosing each server-listed rule emits exactly one `aptitude.autoAssign` with that rule. The rule
      list comes from the server and is never hardcoded (C1, C2). Mode C hides `species-favour` (C5).
    - A refused rule shows its named reason and offers `even` (C4). A default is labelled as suggested,
      and "keep my own" is the absence of an action (C6).
    - It is built from an existing gui-lego piece and the panel shell, with no god component (C7). The
      labels come from the catalog key EP1.19 named (published through `publish.py` if the key is new).
  - Verify: `cd web\fusion-rpg-web; npm test -- --run aptitude; npm run build; npm run extract`
  - Files: the host piece or chrome named by EP1.19, its vitest, the catalog `v{n+1}` if a key is added
  - **Done:** new `auto-assign-rule-strip` piece in `aptitudes-console.json`'s `hero` slot, fed by
    `GET /api/aptitude-presets/rules` (`AptitudePresetEndpoints.cs`) through `useAutoAssignRules` → the
    fold's `autoAssignRules` → the strip; ids are never an FE list, Mode C's `species-favour` omission
    is the server's (`ScopeToAllocation`), labels read the new
    `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` (`autoAssign.ts`'s `ruleLabel`/`RULE_LABELS`),
    and the closed six live once in `AptitudeAutoAssignRules.All`. Catalog `v1` is an authoring act:
    `publish.py` cannot create a domain's first version (proved; see EP1.20's fragment). H7: catalog +
    reader switch in one commit.

- [x] **EP1.21 — Playwright `aptitude-auto-assign.spec.ts` (CP2)** · S · deps: EP1.20 · *(spec: auto-assign-control)*
  - Acceptance:
    - Open a specimen's aptitudes, choose a rule, and see the draft change. Reload, and the saved
      allocation is unchanged (C3).
    - `species-favour` on a real species succeeds end to end (W3 closed), and a forced refusal shows
      its reason and the `even` offer.
  - Verify: `cd web\fusion-rpg-web; npm run test:e2e -- aptitude-auto-assign`
  - Files: `gk-web/web/fusion-rpg-web/e2e/aptitude-auto-assign.spec.ts` (new)
  - **Done:** `gk-web/web/fusion-rpg-web/e2e/aptitude-auto-assign.spec.ts` — 4 cases / 0 failed: the strip
    lists the server's six rules in order and `even` fills the draft with one `/suggest` call and no
    allocation write; a reload restores the saved allocation; `species-favour` fills end to end through
    the specimen's own species; a mocked 400 `autoAssign.favour.empty` shows the named reason with
    `even` still offered. `npm run test:e2e -- aptitude` is 14/14 (also covers the shared hero slot).

### Checkpoint 1 — the default exists (CP1)
- [x] EP1.1–EP1.18 green through their verify commands.
- [ ] `.\scripts\test-fast.ps1 -AllDefault` green once. `default-build` crosses Core, Data and Server:
  AGENTS.md full-suite condition 2, and the spec's own module-end command. **Flagged for coordinator
  scheduling (2026-09-20):** per the coordinator's own standing correction ("if you believe the full
  four-project run is genuinely required... say which clause requires it and I will schedule it when
  the machine is quieter — do not just re-launch it"), this clause is that requirement. Not run in
  this session; every touched project's scoped filter already ran green per-task. Proceeding past this
  bullet to EP1.19+ since no later task lists CP1 as a `deps:`.
- [x] EP1.14's commit lists every moved golden with the default-build explanation. No golden moved for
  another cause. (`tasks/evidence-fragments/EP1.14.md`: no hash-based golden moved; two literal-value
  test assertions fixed in EP1.14's own commit with the default-build reasoning stated.)
- [x] Read back through the normal routes, never a debug bind: a take-back on a specimen and on the
  commander pool charges souls through `PriceOf`, and an addition is free (live-probe standard, RPG
  Server scope). (`gk-core/tests/FusionRpg.Data.Tests/AllocationRespecTests.cs` exercises the real
  `TryReallocate`/`QuoteReallocation` store methods, not a debug bind.)

### Checkpoint 2 — the player can reach it (CP2)
- [x] EP1.21 Playwright green; nothing persists before Confirm. (`tasks/evidence-fragments/CP2.md`:
  `npm run test:e2e -- aptitude-auto-assign` 4/4, `-- aptitude` 14/14, and `POST /api/aptitudes/unique/**`
  observed 0 times after an `even` fill, after the reload, after a `species-favour` fill and after a
  refused `species-favour`.)

---

## Wave B — build-favour diversity (`EP2`)

- [x] **EP2.1 — `AnchorRow` carries `speciesKind` (only if `creature-seed` has not landed it)** · XS · deps: — · *(spec: favour-detector)*
  - Closed as consumed, per this row's own clause: `AnchorRow.SpeciesKind` landed in `be3ac8a6`
    (`creature-seed` CS13). No field added. The missing half — the generation layer's one read of the
    mark, with its three members pinned — is `AnchorSpeciesKind` (`gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorSpeciesKind.cs`).
  - Acceptance:
    - The C# anchor reader exposes `speciesKind` as a closed enum. Its three members are pinned, with
      the reason (a code-owned vocabulary). If `creature-seed` already added it, this task closes as
      consumed, with the commit named.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AnchorRow"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorRow.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/AnchorRowReaderTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorRow.cs` (and its reader), `gk-core/tests/FusionRpg.Core.Tests/Creatures/AnchorRowReaderTests.cs`

- [x] **EP2.2 — `BuildFavourMeasurer.Measure`: lead and shape histograms over real creatures only** · S · deps: EP2.1 · *(spec: favour-detector)*
  - Acceptance:
    - Lead, owner-blind shape, and ordinal tie-break (tests 1–3). Determinism across input order
      (test 4). `speciesKind: excluded` rows are left out of every count.
    - A reflection test: the record has no exact-vector distinctness member (test 5).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildFavourMeasure"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/BuildFavourMeasure.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/BuildFavourMeasure.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs` (new)

- [x] **EP2.3 — `CreatureBuildPlanGen` writes and `--check`s `_species-build-measure.json` (report only)** · S · deps: EP2.2 · *(spec: favour-detector)*
  - Acceptance:
    - The artifact is generated and committed. `--check` byte-compares it with the plan (covered by the
      existing CI step `ci.yml:99`). A summary prints on every run, and no threshold exists yet.
    - A contract test: `Σ LeadCountByAptitude = Σ ShapeCount = SpeciesCount` on the committed artifact.
      This is internal reconciliation, never a literal (test 6).
    - The ideal's 2026-09-17 reading is reproduced once by hand and quoted in the commit body, never
      asserted.
  - Verify: `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildFavourMeasure"`
  - Files: `gk-forge/tools/CreatureBuildPlanGen/Program.cs`, `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` (generated), `gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs`

- [x] **EP2.4 — `LeanSignals`: a closed signal set; per-mille ranks within a side; a missing signal is neutral and recorded** · S · deps: EP2.2 · *(spec: per-species-lean)*
  - Acceptance:
    - `specialisation`, `pure` and `threatRung` (the rung ordinal, never `thetaOffset`) each lie in
      [0, 1000] for any input, including extreme hp (test 3).
    - A species with no base-stat row, or an unresolved rung, gets 500 and is listed. The population
      comes from the measure's filter and is never re-filtered (test 4).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LeanSignal"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/LeanSignals.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/LeanSignalsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/LeanSignals.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/Creatures/LeanSignalsTests.cs` (new)

- [x] **EP2.5 — The planner computes one lean per species; `LeanSignalWeights` is read from tuning** · M · deps: EP2.4 · *(spec: per-species-lean)*
  - Acceptance:
    - With every new weight at 0, a synthetic corpus plans exactly the old formula's vectors, which the
      test derives in its body (test 1).
    - Specialists lean sharper once their weight is non-zero (test 2). An out-of-band weight still makes
      Phase 3 throw `SpeciesBuildRefusal` (test 5). The plan stays input-order independent (test 6).
    - `checked` is applied to every weight × signal product. `crowdingFactor` is kept.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~LeanSignal"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs,gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs,gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs`, `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs`

- [x] **EP2.6 — Publish `species-build` (sequence order 2): `leanSignalWeights` at zero; the generator reads the dump and the threat order; plan byte-identical (H7)** · M · deps: EP2.5, EP2.3 · *(spec: per-species-lean)*
  - Acceptance:
    - The weights are published at zero, and a missing key is a load rejection. Every pin moves in this
      commit.
    - `CreatureBuildPlanGen` reads `type-base-stats.json` (starting from whatever `creature-seed-rederive`
      has committed) and the rung order from `creature-threat.v{n}.json`. `_species-build-plan.json` is
      **byte-identical** (`--check`). The measure gains `leanSignalsMissing`.
  - Verify: `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~SpeciesBuildTuning"`
  - Files: `gk-forge/tools/CreatureBuildPlanGen/Program.cs`, `data/tuning/species-build.v{next}.json` (published), `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` (regenerated) + pins (rg)
  - **Filed (2026-09-20, lane `cmdc-ep2-1`) — three pins this lane's fence forbids, still on `species-build.v2.json`.**
    `rg -l "species-build\.v[0-9]+\.json" src tools tests --glob "*.cs"` finds six readers; the three this
    lane may not edit are `gk-core/src/FusionRpg.Server/Program.cs:165`, `gk-forge/tools/ProveHubCombat/Program.cs:101`
    and `gk-forge/tools/_TempSeedSpecies/Program.cs:121` (allowed paths are `gk-core/src/FusionRpg.Core/**`,
    `gk-forge/tools/CreatureBuildPlanGen/**`, `gk-forge/tools/seedsmith/**`, `gk-core/tools/tuning/**`, `data/**`, `tests/**`,
    docs, tasks). **Cause, not symptom:** v2 has no `leanSignalWeights` block, so the loader's
    version-gated rule reads it as all-zero — the server and those two tools keep working but pin a
    document that predates the mechanism, and `every pin moves in this commit` (H7) is unmet for them.
    **The check that proves the fix already exists:** `TuningVersionAgreementGuardTests`
    (`gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs:197-202`) is a per-domain scan of
    every `<domain>.v<n>.json` reader, but its `AgreedDomains()` matrix lists only `action-base` and
    `action-rungs`. The pin-move commit should add `species-build` there **and** move the three pins —
    the row goes red on the current tree precisely because they disagree (3 readers on v3, 3 on v2),
    which is the same shape ST5.2 documented for `action-rungs`.
    Making the loader's key requirement unconditional instead would crash the server at startup on
    v2, so it is version-gated (`LeanWeightsRequiredFromVersion = 3`) — a structural threshold, with a
    comment saying why. **Fix:** one commit that points all three at the then-current version (EP2.7
    and EP2.8 publish v4/v5 and hit the same fence), which needs a lane whose paths include
    `gk-core/src/FusionRpg.Server/**` and `gk-forge/tools/ProveHubCombat/**`. Nothing else in this program is blocked
    on it: every reader this lane owns is on v3.

- [x] **EP2.7 — Publish `species-build` (sequence order 3): the balance weights and `crowdingFactor`; regenerate plan and measure (own golden commit)** · S · deps: EP2.6 · *(spec: per-species-lean)*
  - Published v4: `leanSignalWeights {specialisation:250, pure:100, threatRung:0}` and `crowdingFactor 633 → 150`,
    the lowest crowding that keeps ≥20‰ headroom under the parity ceiling (measured against three other
    candidates). All 12 primaries now carry ≥2 leans (Onslaught 53); distinct shapes 21 → 166. The three
    out-of-fence pins recorded above are still on v2 — this publish re-hit that fence.
  - Acceptance:
    - The weights are chosen against the measure artifact and labelled "working values". `threatRung`
      stays at 0 (R6: a later publish turns it on).
    - On the regenerated measure, some primary has two or more leans. This is asserted as a relation on
      the artifact (test 7). Parity Phase 3 stays green.
    - Goldens that read species distributions move **for this cause only**. The commit lists them.
  - Verify: `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~BuildFavourMeasure"`
  - Files: `data/tuning/species-build.v{next}.json` (published), `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` (regenerated) + pins (rg)

- [x] **EP2.8 — Publish `species-build` (sequence order 4): the lead and shape caps (working values); tuning fields only, no gate yet (H7)** · S · deps: EP2.7 · *(spec: lead-relabel-pass)*
  - Published v5: `leadCapPermille 250`, `leadCapTolerancePermille 50`, `shapeCapPermille 300` — both
    halves threshold at 300‰, which today's corpus fails by lead (413‰) and meets by shape (255‰).
    Absent caps read `null` on a legacy document, never a default; no gate exists yet (Phase 4 is
    EP2.13's). The plan and the measure are byte-identical. The three out-of-fence pins are still v2.
  - Acceptance:
    - `leadCapPermille`, `leadCapTolerancePermille` and `shapeCapPermille` are `long`, published as
      "working values" chosen from the measure. A missing key is a load rejection.
    - The planner reads the keys but does not refuse on them yet. The `--check` plan is byte-identical.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildTuning"`; `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs`, `data/tuning/species-build.v{next}.json` (published) + pins (rg)

- [x] **EP2.9 — Stage A `accept.py`: a pure, deterministic quota** · S · deps: EP2.8; `creature-seed-rederive` session committed and closed · *(spec: lead-relabel-pass)*
  - Dependency check: `tasks/sessions/creature-seed-rederive-20260918.json` reads `merged`.
  - Landed: `accept.py` (the pure quota + the closed outcome vocabulary + `over_cap_sources` +
    `candidates_from`, which drops `speciesKind: excluded` rows before any vote is read) and
    `test_build_favour_relead.py` (tests 1b, 2 with a fixed seed, 3, 4). No caller yet — the pass-2
    orchestration is EP2.11/EP2.12.
  - Acceptance:
    - A property test with a fixed seed: no target ever ends above `cap_count`, and no species leaves an
      under-cap source (test 2).
    - Decisions are byte-identical under any input order (test 3). A 1-1-1 vote keeps the current
      primary as `unresolved` (test 4). An excluded row is never a candidate and never counted (test 1b).
  - Verify: `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/accept.py` (new), `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/__init__.py` (new), `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py` (new)

- [x] **EP2.10 — `relead.py`: the pass-2 pipeline spec, with an enum-of-12 schema wrapped in `_blocked_variant`, kept out of `PIPELINES`** · S · deps: EP2.9 · *(spec: lead-relabel-pass)*
  - Landed: the spec (`build-favour-relead`, one judgement, enum-of-12 wrapped in the anchor module's
    own `_blocked_variant`, brief built through `_lore_block` so no magnitude leaks) and
    `resolve_relead_vote` (a blocked sample is not a vote; three real votes go to pass 1's
    `resolve_vote`, the reduced case is explicit). `len(PIPELINES) == 8` still holds.
  - Acceptance:
    - `audit_schema` passes on the schema. A numeric variant fails, and a variant without the wrapper
      fails. A blocked sample counts as no vote (test 1).
    - A test asserts that the relead spec id is not a `PIPELINES` key. The `PIPELINES` pins at
      `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/prompts.py:462` and
      `test_classify_pipelines.py:57` are not moved.
  - Verify: `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py gk-forge/tools/seedsmith/tests/test_classify_pipelines.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/relead.py` (new), `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py`

- [x] **EP2.11 — `provenance.relead` block and staleness; a secondary swaps when the new primary equals it** · M · deps: EP2.10 · *(spec: lead-relabel-pass)*
  - Landed: `ReleadProvenance` (closed enums + hash identifiers; written only where a block exists),
    the staleness rule and `apply_relead` in `build_favour/run.py` (swap on collision, `posture`/`pure`
    re-derived, `fromPrimary` checked against the row). Two paths added to the session record; both
    were claimed only by the merged `creature-seed-rederive` record.
  - Acceptance:
    - The provenance round-trips through `emit.py`. `fromPrimary`, the votes and `outcome` are closed
      enums, `measureHash` is an identifier, and no model-chosen number appears.
    - Bumping the `aptitude-primary` prompt version, or changing the dump hash, drops the relead block
      and queues the species again (test 5).
    - `posture` and `pure` are re-derived by `derive.py` after a re-label. When the new primary equals
      the secondary, the two swap.
  - Verify: `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py gk-forge/tools/seedsmith/tests/test_anchor_emit.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/provenance.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/run.py` (new; staleness half), `gk-forge/tools/seedsmith/tests/test_anchor_emit.py`, `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py`

- [x] **EP2.12 — `run.py` orchestration and the `python -m seedsmith creatures build-favour` verb (`--dry-run`, `--limit`)** · M · deps: EP2.11 · *(spec: lead-relabel-pass)*
  - Landed: `load_plan` (read the measure, never recount; capCount from the artifact's own species
    count; staleness feeds the requeue), `execute` (dry run = plan only, zero calls/writes; `--write` =
    ask → vote → stage A → apply → emit), `graph_ask`/`load_lore`, and the CLI verb (dry-run by
    default, `--write`, `--limit`, `--endpoint`/`--model`). Real corpus plan: capCount 223,
    overCap Onslaught, 369 asked. Boundary selected the whole seedsmith suite (cli.py → fallback):
    22 failed / 4142 passed, none in a suite this change touches → TVB-F4 filed.
  - Acceptance:
    - Only species whose lead is over the cap in the measure artifact are asked. The measure is read,
      never recomputed in Python. The run writes through the anchor emit with provenance.
    - `--dry-run --limit 1` performs no model call and no write, and prints the candidate and decision
      plan.
  - Verify: `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py -q; python -m seedsmith creatures build-favour --dry-run --limit 1`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/run.py`, `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py`

- [x] **EP2.13 — Run pass 2 after preflight, then the whole anchor cascade (generated outputs only)** · M · deps: EP2.12 · *(spec: lead-relabel-pass)*
  - Ran: preflight (8 OK / 1 ASK on a pre-existing capture-hash drift), then the pass in 3 durable
    `--limit 40` chunks (120 asked, 360 calls, 25m) → **104 accepted, 16 kept-by-vote, 0 refused**;
    Onslaught 369 → 265 of 892 (413 → 297‰), shapes 166 → 190, largest shape 255 → 234‰; Phase 3 green
    throughout; 104 anchors carry a `relead` block, all `accepted`. Cascade ran in order and every
    `--check` is clean. One test relation updated (EP2.8's pre-pass assertion, single named cause).
  - Acceptance:
    - `seedsmith-preflight` runs first. The pass then runs, and its accepted, refused and unresolved
      decisions are all recorded in the anchors' provenance.
    - The cascade runs in order: `CreatureBuildPlanGen`, `build-favour`, `CreatureSpeciesGen`,
      `CreatureBuildPlanGen`, `CreatureRecipeReconcileInput`, `CreatureRecipeDistributionIndex`. Every
      one of them then passes `--check`.
    - This task is **committed together with EP2.14** (one commit), so `main` never carries a red gate.
      If the caps cannot be met, publish a re-tuned cap as a recorded balance step. Never force a
      relabel, and never hand-edit an anchor.
  - Verify: each generator with `-- --check`; `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py -q`
  - Files: `gk-data/packs/fusion/data/seed/creatures/species/**` and `gk-data/packs/fusion/data/generated/creatures/**` (generated; not hand-edited)

- [x] **EP2.14 — Planner Phase 4: the lead cap and the shape cap refuse; no floor (committed with EP2.13)** · S · deps: EP2.13 · *(spec: lead-relabel-pass)*
  - Phase 4 added after Phase 3 in `Plan`, reading the same measure `favour-detector` writes (new
    vectors overload — one histogram implementation). Green on the regenerated corpus: lead 297‰ ≤ 300,
    largest shape 234‰ ≤ 300; no floor (a twelfth, unled aptitude passes); one test relation flipped to
    the post-pass state with EP2.13 as the single named cause.
  - Acceptance:
    - A synthetic corpus over the lead cap, and one over the shape cap, each throw `SpeciesBuildRefusal`
      naming the cap (test 7). One aptitude led by zero species passes (test 6: no floor, R-Q6).
    - On the committed corpus, `--check` passes with Phase 4 on. Every relead block's enums are legal,
      and every accepted row's primary equals its winning vote (test 8). Goldens that moved because of
      the regenerated plan are listed in the commit.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~BuildFavourMeasure"`; `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs`

### Checkpoint 3 — favour is diverse (CP3)
- [ ] `CreatureBuildPlanGen --check` is green with the lead and shape caps gating. The parity band still
  gates, and every vector sums to 1000‰.
- [ ] The measure artifact shows no aptitude above cap plus tolerance and no shape above its cap.
- [ ] Every relead row carries model provenance. `python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py gk-forge/tools/seedsmith/tests/test_anchor_emit.py -q` is green.

---

## Wave C — creature commanders (`EP3`)

Starts after `SE4.1`–`SE4.4` (commander-identity) **and** the `save-identity` first slice `SE4.11`–`SE4.14`, so
the role table is born keyed (map S8). No wave C task writes a re-keyed Tier A row, so H2 does not apply.

- [x] **EP3.1 — `rpg_commander_role` (`save_id`, `empire_id`, `instance_id`): grant, revoke and list, with named refusals** · S · deps: SE4.4, SE4.12 · *(spec: commander-roster)*
  - Landed: the table (created from `Init` beside every other store schema), `GrantCommanderRole` /
    `RevokeCommanderRole` / `ListCommanderRoleInstanceIds` / `HasCommanderRole` with Unlocked forms,
    the three named refusals (retired / notOwner / unknown, ownership before phase), no roster limit;
    5 Data tests green and the whole Data project 1771/1771. NOTE: the two `gk-core/src/FusionRpg.Data/**`
    paths are outside this lane's allowed list — directed by the orchestrator, recorded in the fragment.
  - Acceptance:
    - Grant then revoke leaves the creature's row, allocation, gear and phase byte-identical (test 2).
    - `commander.role.retired`, `.notOwner` and `.unknown` each refuse and write nothing (test 3). There
      is no roster size limit.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CommanderRole"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderRole.cs,gk-core/tests/FusionRpg.Data.Tests/CommanderRoleTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderRole.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/CommanderRoleTests.cs` (new)

- [x] **EP3.2 — `ICommanderRoster.ForEmpire(EmpireRef)` and the `UniqueCommanderSource` directory source** · M · deps: EP3.1 · *(spec: commander-roster)*
  - Landed: `ICommanderRoster` + `ICommanderRoleReader` port + `UniqueCommanderSource` (resolve/
    empire/list/name + R4 scope key), composed into the ONE directory via `WithSource` (authored rows
    first), the store-backed reader on `RpgStore`, one declaring site for a creature's name
    (`CreatureDisplayName`, also called by `ProjectSheet`), and the Server wiring. 26 Core + 6 Data
    tests green, Server 739/739, Data 1771/1772 (known flake).
  - Acceptance:
    - `commander:unique:{instanceId}` resolves, lists, and can be picked as the default lawn commander
      with **no production edit**. This extends commander-identity's Open/Closed test to a real role row
      (test 1).
    - `AllocationScopeKey` returns the empire's default commander's key (R4). A species allocation for
      that empire resolves the same before and after a grant (test 5). No `switch` on commander
      identity.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CommanderDirectory|FullyQualifiedName~CommanderRoster"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Commanders/ICommanderRoster.cs,gk-core/src/FusionRpg.Core/Commanders/UniqueCommanderSource.cs,gk-core/src/FusionRpg.Server/Program.cs,tests/FusionRpg.Core.Tests/Commanders/CommanderRosterTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Commanders/ICommanderRoster.cs` (new), `gk-core/src/FusionRpg.Core/Commanders/UniqueCommanderSource.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Core.Tests/Commanders/CommanderRosterTests.cs` (new)

- [x] **EP3.3 — `POST /api/commanders/role`; the list is projected from `ICommanderRoster`; the default follows a revoke** · M · deps: EP3.2 · *(spec: commander-roster)*
  - Landed: `POST /api/commanders/role` (grant/revoke, named refusals, the existing list refresh),
    the list projected from `ICommanderRoster.ForEmpire(HumanEmpireOf(save))` (the per-EmpireRef shape
    itself stays SE4.32's), and a transactional revoke+reset. 4 Server + 2 Data tests new; Server
    743/743, Data `~CommanderRole|~Delve` 186/186, Core unchanged (the 4 pre-existing failures).
    Filed SE4.4-followup: `PlayerEmpireCommanders.ForPlayer` lost its last production caller.
  - Acceptance:
    - `GET /api/commanders/{playerId}` projects `ForEmpire(HumanEmpireOf(save))`, plugged into the
      per-`EmpireRef` listing shape `SE4.32` lands. Rebase onto `SE4.32` and never re-implement it. A grant or revoke
      broadcasts the existing list refresh.
    - Revoking the default commander's role resets the default in the same transaction, and a started
      match's snapshot is unchanged (test 4). Delve admission ignores the role (test 6).
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CommanderEndpoints"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CommanderRole|FullyQualifiedName~Delve"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/CommanderEndpoints.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderRole.cs,gk-core/tests/FusionRpg.Server.Tests/CommanderEndpointsTests.cs,gk-core/tests/FusionRpg.Data.Tests/CommanderRoleTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/CommanderEndpoints.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderRole.cs`, `gk-core/tests/FusionRpg.Server.Tests/CommanderEndpointsTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/CommanderRoleTests.cs`

- [x] **EP3.4 — The seat wire: a `seat` column (through `EnsureColumn`) and `leadingCommanderId` on the MatchStarted fact** · S · deps: EP3.3 · *(spec: lawn-commander-seat)*
  - Landed: the `seat` column through `EnsureColumn` + a backfill to `board` + the write on every
    bound row (closed `UniqueLawnSeats` vocabulary), and `leadingCommanderId` on the board.start
    payload (written only when non-blank) parsed by `PvzActivityKinds.LeadingCommanderId`, where an
    absent field means no seat. Data `~UniqueLawn` 2/2, Core `~MatchStartedSeatPayload` 8/8; the
    injector host builds. The row's literal `dotnet build src\FusionRpg.Injector` is red on DH-B1.
  - Acceptance:
    - `rpg_unique_lawn_sessions.seat` defaults to `'board'`, and old rows read as `'board'`.
    - The injector's `MatchHost` puts the frozen leader's id on MatchStarted as an additive field. The
      server contract parses it, and an absent field means "no seat".
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~UniqueLawn"`; `dotnet build src\FusionRpg.Injector`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs,<the MatchStarted payload DTO> -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`, `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs`, the MatchStarted payload in `gk-core/src/FusionRpg.Contracts`

- [x] **EP3.5 — Seat the leading creature commander on the MatchStarted drain; record refused seats, never block the run** · M · deps: EP3.4 · *(spec: lawn-commander-seat)*
  - Landed: `RpgStore.CommanderSeat.cs` + the drain hook — the leader moves `Roster -> ActiveBound`
    with a `seat='commander'` session row (no ptr, no correlation id), run end pays exactly one
    duration receipt and returns it to `Roster`, a replay pays nothing more, no kill credit is
    possible (no ptr), and `seat.notCommander` / `seat.notAtBase` / `seat.isPatron` are named and
    recorded without gating the run. 7/7 focused Data tests. The one red first pass was a FIXTURE
    gap (the Data bootstrap's duration interval is 0 -> the award bails before reading the session),
    diagnosed in the test rather than papered over; no production defect.
  - Acceptance:
    - A seated commander moves `Roster → ActiveBound`. At run end it gets exactly one duration receipt
      and returns to `Roster`; a replayed MatchEnded pays nothing more (test 1). It gets no kill credit
      (test 2). Expedition and delve refuse it for the run (test 3).
    - `seat.notCommander`, `seat.notAtBase` and `seat.isPatron` are each recorded, and the run stays
      playable (test 5). Grant-then-default and default-then-grant both seat (test 6). A mid-run
      default change or revoke leaves the seat and its XP unchanged (test 7).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CommanderSeat|FullyQualifiedName~UniqueLawn"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs,<the MatchStarted drain file>,gk-core/tests/FusionRpg.Data.Tests/CommanderSeatTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs` (new), the MatchStarted drain site, `gk-core/tests/FusionRpg.Data.Tests/CommanderSeatTests.cs` (new)

- [x] **EP3.6 — Canary: `TryBeginUniqueDeploy` refuses this run's seated commander with `commander.cannot-deploy`** · S · deps: EP3.5 · *(spec: lawn-commander-seat)*
  - Landed: the branch sits above the phase check (beside the Patron one) reading the seat row, so
    the reason names the rule; a role-holder that is not leading this run deploys normally. The
    canary comment at the call site and the test file's own "Commander is NOT tested here" header are
    replaced. 4/4 focused Data tests.
  - Acceptance:
    - The refusal fires before the phase check, so the reason names the rule. A role-holder that is not
      leading this run deploys normally (test 4).
    - `CreatureLawnDeployCommanderRefusalTests` gets its real case, and the canary comment at
      `RpgStore.UniqueActors.cs:177-185` is replaced.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CreatureLawnDeployCommanderRefusal"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs,gk-core/tests/FusionRpg.Data.Tests/CreatureLawnDeployCommanderRefusalTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, `gk-core/tests/FusionRpg.Data.Tests/CreatureLawnDeployCommanderRefusalTests.cs`

- [x] **EP3.7 — `WorldEntityMemberRole.Commander`; persistence reads and writes the new name** · S · deps: EP3.3 · *(spec: legion-commander)*
  - Landed: `Commander` joins the closed member-role vocabulary (pinned with its reason), and a legion
    led by a `Commander` member round-trips through `RpgStore.World.cs` (the writer is `ToString()`,
    the reader `Enum.Parse`, so the enum member is the whole change). Core `~WorldState` 4/4, Data
    `~World` 128/128.
  - Acceptance:
    - The enum's membership is pinned with its reason (a reviewed declaration change).
    - A world holding a `Commander` member round-trips through `RpgStore.World.cs`.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldState"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~World"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/World/WorldState.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs`, a world round-trip test

- [x] **EP3.8 — `attach-commander` / `detach-commander` world commands, with admission in Data and re-validation in Core** · M · deps: EP3.7, **`SP1.2` (layer-source-selector) (hard, spec)** · *(spec: legion-commander)*
  - Landed: the two kinds + the stamped fields (`MemberInstanceId`/`SpeciesId`/`Level`), the Data
    validator (`commander.role.missing`, `commander.not-at-base`, hooked in `WorldTurns.cs` beside the
    Wonder one) and the resolver (`legion.gone`/`not-yours`/`marching`/`has-commander`, called in
    `Snapshot` beside `WardenResolver`). SP1.2 confirmed landed. Core 81/81 through the row filter,
    Data 3/3; guard-dal OK. The member's `Hp` is the world layer's own `RecruitPolicy.RaiseMemberHp`
    (no derived-stat seam was needed: that reading was wrong and is corrected in the ledger).
  - Acceptance:
    - A resolved attach yields one `Commander` member carrying the specimen's `InstanceId`, species,
      level and full hp, and it survives persistence (test 1).
    - Every drop reason has its own test: `commander.role.missing`, `commander.not-at-base`,
      `legion.gone`, `legion.not-yours`, `legion.marching` and `legion.has-commander` (one leader per
      legion, a structural limit with a comment). A legion lost the same turn is re-validated (test 2).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CommanderAttach|FullyQualifiedName~WorldCommandAdmission"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Movement/CommanderAttachResolver.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/tests/FusionRpg.Core.Tests/World/Turn/CommanderAttachResolverTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs`, `gk-core/src/FusionRpg.Core/World/Movement/CommanderAttachResolver.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/tests/FusionRpg.Core.Tests/World/Turn/CommanderAttachResolverTests.cs` (new)

- [x] **EP3.9 — `ParentOf(instanceId)`; lawn deploy and the commander seat consult it** · M · deps: EP3.8, EP3.5 · *(spec: legion-commander)*
  - Landed: `CommanderParent`/`ParentOf` (one query over the world graph, `AdmitsChild` the one
    expression) consulted by the lawn deploy path and the commander seat, so a child starts from home
    or a stationed legion and refuses `not-at-base` from a marching one. 12/12 through the row filter
    (6 new ParentOf tests). EP3.10 takes the delve and expedition halves.
  - Acceptance:
    - `ParentOf` returns `Home` or `Legion(entityId, stationed)` from the world graph.
    - Lawn Bound and the seat admit from home and from a stationed legion, and refuse `not-at-base` from
      a marching one. Attach and seat in the same turn are order-independent (test 5, lawn half).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ParentOf|FullyQualifiedName~CommanderSeat|FullyQualifiedName~UniqueLawn"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderParent.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs,gk-core/tests/FusionRpg.Data.Tests/ParentOfTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderParent.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs`, `gk-core/tests/FusionRpg.Data.Tests/ParentOfTests.cs` (new)

- [x] **EP3.10 — Delve slot and expedition seat admission consult `ParentOf`** · S · deps: EP3.9 · *(spec: legion-commander)*
  - Expedition half landed: the squad loop refuses a marching legion's member with `not-at-base`,
    first in the loop so the reason names the rule; home and a stationed legion are not refused by it.
    **Delve half proven UNREACHABLE, not skipped:** `CreateDelve` takes a pre-built world (no
    per-specimen gate) and `DelveEndpoints.cs:175` records that `/start` returns before it (D4.22), so
    there is no live delve party admission to extend. Filed PD-B1 in `tasks/party-dungeon-todo.md`
    with the one-line fix. 207/207 through the row filter; existing delve/expedition tests unedited.
  - Acceptance:
    - Both admit from home and from a stationed legion, and refuse `not-at-base` from a marching legion
      (test 5, delve and expedition half).
    - Existing delve and expedition admission tests pass unedited.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ParentOf|FullyQualifiedName~Delve|FullyQualifiedName~Expedition"`; `.\scripts\verify-change.ps1 -Paths <delve admission file>,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs,gk-core/tests/FusionRpg.Data.Tests/ParentOfTests.cs -Session <sid>`
  - Files: the delve admission file, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`, `gk-core/tests/FusionRpg.Data.Tests/ParentOfTests.cs`

- [x] **EP3.11 — Siege: a commander fights as its own specimen with no `CreatureType` points; `commander.away` skip; goldens** · M · deps: EP3.8, EP1.14 · *(spec: legion-commander)*
  - Landed (ep-3, 2026-09-21), with the orchestrator's one-file widening of this lane's boundary to
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (EP3.11's own Verify line and file list name it).
    The rule and the report line are Core: `DistrictAssaultResolver.CommanderAway` + `MemberAway` (the
    Data-injected "is this specimen in `Roster`" predicate, the same inversion as `HubInputsFor`), applied
    first in `BuildAnimateSetups` so an away commander is never priced or placed and is carried forward
    **unchanged** by `BuildSideOutcome` — away is not a casualty; `BattleReporting.Fight` writes the
    `commander.away:<species>` line, scoped to the ground and the legion's own faction. Test 3's provider
    half was already covered (`WorldTurnHubInputsForTests` asserts `TotalForScope(CreatureType) == 0`;
    SP1.2 landed), so the new test is the resolver's end of that contract. 27/27 Core `~DistrictAssault`,
    1/1 Server, 31/31 Data world-turn/commander, Data union filter 1733/1733. Fragment:
    `tasks/evidence-fragments/EP3.11.md`. It also carries the EP4.1 fragment correction: my
    `spec-empire-level.md` deviation note named `progression.v2.json`, which `SpecChannelClaimTests`
    requires to be verified as a non-channel — now allow-listed with its own reason.
  - Acceptance:
    - The commander member's setup carries `HubInputs` from its `UniqueCreature` allocation (or its
      default), and no `CreatureType` points. This is asserted on the resolver's output as a
      consumer-side check of `SP1.2` (layer-source-selector), which this task does not re-implement (test 3).
    - A siege with no `InstanceId` members is byte-identical (test 4). A commander whose specimen is not
      in `Roster` is skipped with `commander.away`, and the rest of the legion fights (test 6b).
    - Only fixtures that already build an `InstanceId` member move, each one listed (test 7).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~DistrictAssault"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, `gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs`
  - Finding (ep-3, 2026-09-21), kept for the next row's reader: this spec's premise *"no writer set
    `InstanceId` before this module"* is **stale** — EP3.8's `attach-commander` writes it. Two facts
    that shortened EP3.11, both re-read in code: the provider's layer selection was already fixed
    (`RpgStore.WorldTurns.cs:559-592` composes `Aptitude = commander + specimen`, so "no `CreatureType`
    points" already held — SP1.2 landed), and no fixture anywhere builds a `WorldEntityMemberRole.Commander`
    member inside a battle, so test 7 moved no golden (the enumeration is in the fragment).

- [x] **EP3.12 — Casualty: a fallen commander member is detached and set `Recovering` (until `injury-tiers`)** · S · deps: EP3.11 · *(spec: legion-commander)*
  - Landed (ep-3, 2026-09-21): `RpgStore.ApplyCommanderCasualtiesUnlocked` runs inside `CommitWorldTurn`'s
    transaction after `TurnEngine.Step` and **before** the world diff and the state hash, so the detached
    member is out of both the persisted graph and the stored hash. It reads two worlds because a death has
    two shapes: `BuildSideOutcome` REMOVES a member whose new wounds reach its `Hp`, while a member already
    at zero effective HP is kept and never fielded — either is a casualty, and only a `Commander` member
    with an `InstanceId` is considered. It writes the **phase only**, never an
    `rpg_unique_actor_recovery` row: a wound count is `injury-tiers`' bookkeeping, and the interim
    consequence (a siege casualty refuses the delve recovery ritual with `recovery.missing`) is recorded
    in the fragment rather than papered over. Comment names `deployment-hierarchy`'s `injury-tiers` as the
    replacement. Gates: `~WorldTurnCasualty` 4/4 through the real store path (one of them a committed
    `assault` into a Zomboss-held district), `~WorldTurn` 25/25, `~WorldWaveOne` goldens 6/6 — no hash
    moved, since that scenario builds no `Commander` member — and the Data union filter 1737/1737.
    Fragment: `tasks/evidence-fragments/EP3.12.md`. Finding routed in the same commit: **TVB-F16** (no Data
    test had ever committed a district assault; the Data bootstrap does not configure `AptitudeTuningHub`).
  - Acceptance:
    - A commander member at zero hp is detached, and its specimen is set `Recovering`, the delve's
      non-lethal default (test 6). A comment names `injury-tiers` as the replacement.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,<the world-turn casualty test> -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, the world-turn casualty test

### Checkpoint 4 — a creature commands (CP4)
- [ ] `.\scripts\test-fast.ps1 -AllDefault` green once. `legion-commander` crosses Core, Data and
  Server: AGENTS.md condition 2, and the spec's own module-end command.
- [ ] A creature commander leads a lawn run seated, earns duration XP only (read back through
  `/api/unique`, never a debug bind), and is refused as a lawn Bound.
- [ ] It leads a legion into a siege and fights as its own specimen; every moved golden is explained.

---

## Wave D — empire level, earned free respecs, AI empire species (`EP4`)

- [x] **EP4.1 — Core: `RpgActorKinds.Empire`, `EmpireSpeciesLevelUp` reason, the `ParamsFor` arm, `EmpireLevelGrants`** · M · deps: — · *(spec: empire-level)*
  - Landed (ep-3, 2026-09-21): `RpgActorKinds.Empire` + `IsKnown`, `RpgXpReasons.EmpireSpeciesLevelUp`,
    `RpgXpCurve.ParamsFor`'s empire arm, `RpgXpAwards.SpeciesLevelUp`, and the new
    `EmpireLevelGrants.cs` (`EmpireLevelGrantKind` 1 member, `EmpireLevelGrant`, `EmpireLevelTuning`,
    pure `For`). `ProgressionTuning` parses `xpCurve.empire` and `awards.speciesLevelUp`. **One
    recorded deviation from the spec's literal text:** the two keys are presence-tolerant at parse and refused by
    name at first use rather than at parse, because the live host pin (`gk-core/src/FusionRpg.Server/Program.cs`)
    and ~30 fixtures hardcode a literal `progression.v{n}.json` path and this lane's fence excludes
    `gk-core/src/FusionRpg.Server/**`, so a parse-time requirement would break the shipped server before EP4.2
    moves the pins. EP4.2 may tighten it to a parse requirement once its pins move. Gate: 20/20 through
    the row filter, 15157 tests green through `verify-change.ps1`, `guard-power.py` OK. Fragment:
    `tasks/evidence-fragments/EP4.1.md`.
  - Acceptance:
    - `RpgActorKinds` has 6 members and `EmpireLevelGrantKind` has 1. Both are pinned, with the reason:
      each is a code-owned vocabulary (test 7).
    - `EmpireLevelGrants.For` is pure. `freeRespecsPerEmpireLevel = 0` gives no grant. A reflection test
      shows `EmpireLevelGrants` declares no level-shaped curve method (test 5, reflection half).
    - `ProgressionTuning` parses `xpCurve.empire` and `awards.speciesLevelUp`. The `v1` file is not yet
      changed; that happens in EP4.2.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~EmpireLevelGrants|FullyQualifiedName~RpgActorKinds|FullyQualifiedName~ProgressionTuning"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs,gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs,gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs,tests/FusionRpg.Core.Tests/Progression/EmpireLevelGrantsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs`, `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs`, `gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs` (new), `tests/FusionRpg.Core.Tests/Progression/EmpireLevelGrantsTests.cs` (new)

- [x] **EP4.2 — Publish `progression` (next free version): `xpCurve.empire` and `awards.speciesLevelUp`; move pins (H7); land the §10.1 row** · M · deps: EP4.1 · *(spec: empire-level)*
  - Landed (ep-3, 2026-09-21): `publish.py` wrote **`progression.v3.json`** on top of v2 (the next free
    number; v1/v2 stay on disk for revert), and 34 files' pins moved in the same commit — the live host
    `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat`, `gk-forge/tools/_TempSeedSpecies` and 31 test
    fixtures (H7). The batch used a `(?<!species-)` guard so `species-progression.v1.json` was untouched.
    **The two keys are now REQUIRED at parse** (T5), which closes the deviation EP4.1 recorded as
    temporary: v1/v2 no longer load, and the deferred refusal survives only for an in-code
    `ProgressionTuning` a bootstrap built without them. **§10.1 row 39** landed (38 was the highest).
    Gates: publish exit 0; Core `~EmpireLevelGrants|~RpgActorKinds|~ProgressionTuning` 23/23; Server
    `~Aptitude` 67/67 and Server full 772/772; `guard.doc-boundary` 4/4; `server.derived-audit` 1/1;
    Data union filter 1737/1737; `guard-power.py` OK; `resource_ownership.py --check` OK; both tools
    build. Fragment: `tasks/evidence-fragments/EP4.2.md` — note its own section on why
    `docs/architecture/power/inventory.json` got no row 39 (rows 35-38 were never mirrored either).
  - Acceptance:
    - Published through `publish.py` on top of whichever `progression` version is current. The parent §5
      order is `lawn-deploy-progression`, `SP7.3` (zomboss-commander-clock), then this, each taking the next
      free number. A missing key is a load rejection naming it.
    - Every pin found by `rg -l "progression\.v[0-9]+\.json" src tools tests --glob "*.cs"` moves in
      this commit: the server `Program.cs`, `gk-forge/tools/ProveHubCombat`, `gk-forge/tools/_TempSeedSpecies` (moved or
      deleted by its owner), and the Core, Data and Server test fixtures.
    - The `ssot-power-scale.md` §10.1 row for the empire level lands at the next free ordinal, in the
      same commit. `guard-power.py` is green.
  - Verify: `python gk-core/scripts/guard-power.py`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionTuning"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`; `.\scripts\verify-change.ps1 -Paths gk-core/data/tuning/<progression.vN>.json,gk-core/src/FusionRpg.Server/Program.cs,docs/architecture/power/ssot-power-scale.md -Session <sid>`
  - Files: `data/tuning/progression.v{next}.json` (published), `docs/architecture/power/ssot-power-scale.md` + pins (rg)
  - Finding (ep-3, 2026-09-21), closed by this row: the pin set named `gk-core/src/FusionRpg.Server/Program.cs`
    and `docs/architecture/power/**`, which the original lane fence excluded; the orchestrator's
    instruction widened the session boundary to exactly those files so H7 could be honoured in one commit.
    The other half of the finding — EP4.1's presence-tolerant parse — was resolved the way the spec's
    tunables section prescribed: tightened to a parse requirement in the commit that moved every pin.

- [x] **EP4.3 — Credit an empire level-up inside `TryApplyXpUnlocked` for each new `highest_level` of its own species** · M · deps: EP4.2, **SE4.20 (H2)**, SE4.21 · *(spec: empire-level)*
  - Landed (ep-3, 2026-09-21): `RpgStore.EmpireLevel.cs` holds the credit (one nested `TryApplyXpUnlocked`
    per level in `(highestBefore, highestAfter]`, dedupe `sp:{typeId}:L{level}`), the R1 side rule
    (`SpeciesCreditsOwner` reading `KillAttribution.EmpireOf`, so a human-owned zombie species pays
    nothing — the human's empire row is never even created), and `EmpireLevelUpEvent`. The crossings ride
    `RpgProgressionDirty.LevelUps`, the optional member added to the dirty the caller already drains after
    commit — which is what makes "a rolled-back transaction queues nothing" structural rather than a
    promise. The hook in `TryApplyXpUnlocked` sits after the row update and reads the PRE-apply
    `highest_level` (`RpgXpApply.Apply` mutates the state it is handed; reading it afterwards credits
    nothing silently — the one real trap this row had). Gates: `~EmpireLevel` 8/8, Data union filter
    1745/1745, E2E 231/231, XP-path regression 54/54, twelve core shards green, `dal`/`test-substrate`
    guards OK. Fragment: `tasks/evidence-fragments/EP4.3.md`. **One erratum requested** in the ledger and
    that fragment: spec testing-strategy test 4 as worded ("one award that crosses `k` species levels")
    is unreachable with the shipped species curve — thresholds `60 + 24·n`, two smallest consecutive sum
    144, largest award 100 — so the same claim is proved on the reachable side (one credit crossing `k`
    empire levels queues `k` events) and the `(highestBefore, highestAfter]` range is proved on both paths.
  - Acceptance:
    - Both species XP paths credit once per `(species, level)` over `(highestBefore, highestAfter]`
      (tests 1 and 4). Demote and re-climb credits nothing, **even after the empire's `sp:*` ledger rows
      are deleted** (test 2). The empire levels exactly when `RpgXpCurve.XpToNext(Empire, L)` says, for
      `L` read from the loaded tuning (test 5, curve half).
    - Side rule: a human-owned zombie species never moves the human's empire (test 2b). A replay changes
      nothing (test 3).
    - The dirties are collected by the caller, and `EmpireLevelUp` is queued and broadcast only after
      commit. A rolled-back transaction broadcasts nothing (test 2c). Nothing is registered in
      `ProgressionPipeline`.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` (new)

- [x] **EP4.4 — Publish `species-build` (sequence order 5): `freeRespecsPerEmpireLevel`; tuning field; `EmpireLevelTuning` wiring (H7)** · S · deps: EP4.1, EP2.8 (order 4 must exist first) · *(spec: respec-free-counter)*
  - Landed (ep-3, 2026-09-21): `publish.py` wrote **`species-build.v6.json`** with
    `freeRespecsPerEmpireLevel = 1` and 7 files / 9 pins moved to v6 (the Server host, three tools, three
    Core test files) — only two historical comments still name v1. `SpeciesBuildTuning` carries the key as
    a **required** whole number ≥ 0 from v6 (`FreeRespecsRequiredFromVersion`), so v1–v5 keep loading for
    revert while a v6 document without it is refused by name (T5); 0 is legal and means levels pay
    nothing, and `respecFreeCount` appears neither in the file nor as a member. **`EmpireLevelTuningHub`**
    (Core) is the wiring: `Program.cs` parses the file once and builds it from the same value it gives
    `SpeciesBuildTuningHub`, and the Data credit reads the hub — which closed EP4.3's deferred half, so a
    queued `EmpireLevelUpEvent` now carries one `FreeEmpireRespec` grant of 1 each. `CreatureBuildPlanGen
    --check` printed `clean, 904 species match` (byte-identical). Gates: `~SpeciesBuildTuning` 22/22,
    `~SpeciesBuild|~BuildFavour` 56/56, Data `~EmpireLevel` 8/8, Data union 1745/1745, Server 772/772, E2E
    231/231, three tools build, guards OK. Fragment: `tasks/evidence-fragments/EP4.4.md`.
  - Acceptance:
    - The key is published at the working value 1. It is a `long`, at least 0, and a missing key is a
      load rejection. `respecFreeCount` is never published.
    - Every pin moves. `CreatureBuildPlanGen --check` stays byte-identical (test 11).
    - The host builds `EmpireLevelTuning` from this key.
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildTuning"`; `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check`
  - Files: `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs`, `data/tuning/species-build.v{next}.json` (published), `gk-core/src/FusionRpg.Server/Program.cs` + pins (rg)
  - Finding (ep-3, 2026-09-21): `species-build`'s pins are also outside a Core+tuning lane
    (`gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat`, `gk-forge/tools/_TempSeedSpecies`), and its current
    top version is **v5**, so this row publishes v6 on top of it. The host half ("builds
    `EmpireLevelTuning` from this key") is the same excluded file, so the row and EP4.1's Core half cannot
    be split across the fence without landing a key no production host reads.

- [x] **EP4.5 — `rpg_empire_free_respec_ledger` (keyed for every empire) and the `FreeEmpireRespec` grant, applied in the level-change transaction**
  - Landed (ep-3, 2026-09-21): `rpg_empire_free_respec_ledger` (PK `(save_id, empire_id, level)` = the
    `L{n}` key) with its DDL beside its store partial and its `Ensure` call in `RpgStore.cs`'s `Init`
    cluster in the same commit (H2). `ApplyEmpireLevelGrantsUnlocked` runs beside the empire level change
    inside `TryApplyXpUnlocked`, so a level and its stock commit or roll back together; a 0 amount writes
    no row and a replay is ignored by the primary key. `FreeRespecStock` reads `SUM(delta)` and THROWS on
    a negative sum rather than clamping. Keyed for every empire, which is what X13 already records at
    `spec-save-identity.md:600` (the spend stays human-only in EP4.9) - proved with Zomboss's own
    `EmpireRef`. Gates: `~EmpireFreeRespec|~EmpireLevel` 13/13, Data union 1750/1750, `guard-dal` OK.
    Fragment: `tasks/evidence-fragments/EP4.5.md`.
 · M · deps: EP4.3, EP4.4 · *(spec: respec-free-counter, empire-level)*
  - Acceptance:
    - Crossing `k` empire levels writes `k` grants of `freeRespecsPerEmpireLevel`, keyed `L{n}`. A
      replayed level-up adds nothing. A value of 0 writes nothing (empire-level test 6,
      respec-free-counter test 8).
    - The stock is `SUM(delta)`, per `(save_id, empire_id)`, and never negative. Zomboss accrues under
      his own `EmpireRef` (test 10, accrual half).
    - The builder files the X13 note on `save-identity`'s consumer row (the stock is keyed for every
      empire). The note belongs to `solid-enforcement`'s doc, not to this task's files.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireFreeRespec|FullyQualifiedName~EmpireLevel"`; `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs` (new), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs` (new)

- [x] **EP4.6 — Empire-level backfill at store start, for every empire with no `kind = 'empire'` row**
  - Landed (ep-3, 2026-09-21): `BackfillEmpireLevelsUnlocked` in `RpgStore.EmpireLevel.cs`, called from
    `RpgStore.cs`'s `Init` beside `BackfillWorldSeedsUnlocked`, so it runs before any reader serves a
    request. One transaction per empire, crediting each candidate's species `highest_level` through the same
    `CreditEmpireForSpeciesLevelsUnlocked` live play uses (`highestBefore = 1`), so the R1 side rule, the
    curve, the `sp:{typeId}:L{n}` keys and the grants are identical. Idempotent by construction: the first
    credit creates the `kind = 'empire'` row, so the pass never re-runs for that empire -- even after
    compaction trims the keys a ledger-based rule would depend on -- and a mid-pass throw rolls the whole
    empire back, leaving no row for the next start to complete. It never touches the progression tuning on a
    database with nothing to catch up (`highest_level > 1` gates the candidate query). Gates: `~EmpireLevel`
    11/11, Data union 1753/1753, `dal`/`test-substrate` guards OK. Fragment: `tasks/evidence-fragments/EP4.6.md`.
 · S · deps: EP4.5 · *(spec: empire-level)*
  - Acceptance:
    - For a seeded store, the backfill produces the same empire row and grants as live crediting.
    - A second start changes nothing, including after the empire's ledger rows are deleted. A pass that
      throws midway leaves no empire row, and the next start completes it (test 9).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs`

- [x] **EP4.7 — `GET /api/players/{playerId}/empires/{empireId}/level` and the `EmpireLevelUp` broadcast**
  - Landed (ep-3, 2026-09-21): the route answers the spec's seven fields, with a missing empire row reading
    level 1 rather than 404 (the row is created by the first credited species level) and an unknown player
    reading 404. `EmpireLevelUp` is emitted after commit from the dirties the append returned, once per level
    crossed with its grants and the stock read back — extracted into `EmpireLevelBroadcast` so the payload is
    asserted on the REAL wire (a real SignalR client on the web group) while `Program.cs`'s fact-ingest loop
    stays the production caller. Gates: `~EmpireEndpoints` 5/5, `verify-change` exit 0 with Server 774/774 and
    `dal` OK (the Server boundary is not sharded, so this row never hit the TVB-F6 misreport).
    Fragment: `tasks/evidence-fragments/EP4.7.md`.
 · S · deps: EP4.6 · *(spec: empire-level)*
  - Acceptance:
    - The route returns `{empireId, level, xp, xpToNext, highestLevel, freeRespecStock,
      freeRespecsPerLevel}`. The existing `/api/rpg/progression/{playerId}/empire/0` accepts `empire`.
    - `EmpireLevelUp` fires once per empire level crossed, after commit, with its grants. `NS` renders
      it; this task only emits.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~EmpireLevel|FullyQualifiedName~Progression"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/EmpireEndpoints.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/EmpireEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/EmpireEndpoints.cs` (new, or `save-identity`'s empires route file), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/EmpireEndpointsTests.cs` (new)

- [x] **EP4.8 — FE: every unfiltered progression reader filters by kind**
  - Landed (ep-3, 2026-09-21): `actorProgressionFold.ts` states the closed actor set (`player`/`plant`/
    `zombie`) once and both of the page's ledger tables — the compact one and the advanced one, plus their
    empty states and pager counts — fold through it, so an `empire` row can no longer appear where only
    actor kinds are expected. The page's list panes already passed `kind`. Gates: `npm test -- --run
    progression` 10/10 (4 new, pinning that an empire row is dropped and that the fold is generic over
    `kind`), `npm run build` clean (`tsc --noEmit` + vite, built in 12.77s). The earlier blocker note about
    the FE toolchain was resolved: `npm ci` needed PowerShell with a Windows node dir on PATH, because
    bash's POSIX PATH does not reach `cmd.exe`. Fragment: `tasks/evidence-fragments/EP4.8.md`.

  - Finding (ep-3, 2026-09-21), read-only analysis, for whoever takes this row: the grep finds exactly ONE
    unfiltered consumer — `gk-web/web/fusion-rpg-web/src/features/rpg-progression/RpgProgressionPage.tsx:286`
    calls `useRpgProgressionActors(playerId, kind, ...)` with `kind` from local state, so an `empire` row can
    appear in a list that means actors. The fix is that page's own kind default plus the fold extraction the
    vitest clause needs (`features/rpg-progression/progressionFold.ts`, with the query hook at
    `src/lib/bus/queries.ts:205-226` as the only feeder). **Not started:** this lane's fence excludes
    `gk-web/web/fusion-rpg-web/**` and `node_modules` is absent in its worktree, so the row's Verify line
    (`npm test -- --run progression`, `npm run build`) cannot run there — recorded as a blocker rather than
    half-edited. · XS · deps: EP4.7 · *(spec: empire-level, test 10)*
  - Acceptance:
    - A grep for unfiltered `ListRpgProgression` consumers finds each one filtering by kind. A vitest over
      the fold shows that an `empire` row never appears where only actor kinds are expected.
  - Verify: `cd web\fusion-rpg-web; npm test -- --run progression; npm run build`
  - Files: the FE progression fold(s) found by the grep, their vitest

- [x] **EP4.9 — The species respec spend takes `payWith` (souls or a free respec); replay is checked on both ledgers; `QuoteSpeciesRespecUnlocked`** · M · deps: EP4.5, EP1.6 · *(spec: respec-free-counter)*
  - Landed (ep-3, 2026-09-21): the species respec takes `payWith` (`RespecPayment.Souls` | `FreeRespec`,
    last parameter so existing positional callers are untouched). Priced changes with stock and no choice
    refuse `respec.payment.choice-required` carrying the quote and write nothing; `freeRespec` spends one
    and leaves the soul ledger and the churn counter alone; `souls` charges `PriceOf` and leaves the stock
    alone; no stock refuses `respec.free.none` and an omitted choice with no stock is byte-identical to
    today (the whole existing `SpeciesRespecTests` class is green untouched). Replays are caught on BOTH
    ledgers, the free one by the respec correlation in the ledger's own `dedupe_key` under a partial unique
    index (an additive migration), and `QuoteSpeciesRespec` shares `RespecPolicy.Quote` so a preview and a
    spend cannot disagree. One rule to respect when reading the tests: a species' FIRST override is free, so
    a priced path has to touch the species first. Gates: `~SpeciesRespec|~EmpireFreeRespec` 21/21, Core
    `~RespecPolicy` 27/27, `dal`/`test-substrate` guards OK. Fragment: `tasks/evidence-fragments/EP4.9.md`.

  - Acceptance:
    - With stock at 1 or more and no `payWith`: `respec.payment.choice-required`, carrying the quote,
      and nothing written (test 1).
    - `freeRespec` spends 1 and leaves the churn counter unchanged (test 2). `souls` charges `PriceOf`
      and leaves the stock unchanged (test 3). With no stock, `freeRespec` refuses `respec.free.none`,
      and an omitted `payWith` behaves exactly as today (test 4). With the key at 0, every existing
      `SpeciesRespecTests` case passes (test 5). First override and revert move neither the stock nor the
      counter (test 6).
    - A replay on either ledger returns the original payment (test 7). Preview equals spend for stock 0
      and stock ≥ 1, at counts 0 to 3 (test 9). A human spend never touches Zomboss's stock (test 10).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesRespec|FullyQualifiedName~EmpireFreeRespec"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RespecPolicy"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs,gk-core/tests/FusionRpg.Data.Tests/SpeciesRespecTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs` (`RespecPayment`), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireFreeRespec.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/SpeciesRespecTests.cs`

- [x] **EP4.10 — The routes carry the choice: `/species-build/respec`, `/respec-price` and the species branch of preset activation** · S · deps: EP4.9, EP1.10 · *(spec: respec-free-counter)*
  - Landed (ep-3, 2026-09-21): `POST /api/species-build/respec` takes `payWith` (parsed at the edge; an
    unknown spelling is a 400), returns `paidWith` and `freeRespecStock` read from the outcome, and answers a
    missing choice with 409 `respec.payment.choice-required` carrying `soulPrice` and `freeRespecStock`;
    `GET /respec-price` reads one `QuoteSpeciesRespec` and adds `freeRespecStock` and `freeAvailable`; and the
    species branch of `POST /api/aptitude-presets/activate` carries the choice through
    `TryActivateAptitudePreset` to the same store call, with the same 409 mapping. **A test caught a real gap
    while proving that last clause:** the activate SUCCESS path built its outcome without
    `PaidWith`/`FreeStock`, so an activation reported nothing paid even after spending a free respec - fixed
    in the same commit. Gates: `~SpeciesBuild|~AptitudePreset` 34/34 (four new cases), and the Server boundary
    exited 0 earlier this session. Fixture note for the future: a Server-side test seeds the free-respec stock
    by writing the ledger rows directly, because Server.Tests has no internals access and the public fact path
    was diagnosed not to create an empire row in that host. Fragment: `tasks/evidence-fragments/EP4.10.md`.

  - Acceptance:
    - `POST /respec` accepts `payWith` and returns `paidWith` and `freeRespecStock`. A missing choice
      returns 409 with `{soulPrice, freeRespecStock}`. `GET /respec-price` adds `freeRespecStock` and
      `freeAvailable`.
    - `POST /api/aptitude-presets/activate` (species scope) passes `payWith` through
      `TryActivateAptitudePreset` to the same store call.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~SpeciesBuild|FullyQualifiedName~AptitudePreset"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs,gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs,gk-core/tests/FusionRpg.Server.Tests/SpeciesBuildEndpointsTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Server/SpeciesBuildEndpoints.cs`, `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs`, `gk-core/tests/FusionRpg.Server.Tests/SpeciesBuildEndpointsTests.cs`

- [x] **EP4.11 — The stock is never trimmed (an architecture test); land the owed `empire-resource-ssot.md` §3 Accrual-meter row** · S · deps: EP4.9 · *(spec: respec-free-counter; map "Registry row owed")*
  - Landed (ep-3, 2026-09-21): the owed `empire-resource-ssot.md` §3 Accrual-meter row is at line 56 as the
    map drafted it, and both halves of spec test 12 are green. The architecture half is a source scan
    asserting the ledger is named by exactly `RpgStore.EmpireFreeRespec.cs` and `RpgStore.cs` — no
    compaction, archive or trim file — with a last assertion that keeps it from passing vacuously if the
    table is renamed. The runtime half runs on a `DataTestStore.CreateFileBacked()` store, because the
    archive/compaction entry points refuse on an in-memory plan by design (`StorePlanException`, asserted by
    `RpgStoreStoragePlanTests`); both `CompactAfterRunClosed(null)` and `TrimHotTailsNow()` are driven, and
    the stock AND the row count are asserted unchanged. **NOTE for the next lane:** the Verify line above
    spells the citation audit as `audit-doc-citations.py <path>`, but that script takes
    `--scope`/`--targets`/`--strict` and no positional path — the working form is
    `python scripts/audit-doc-citations.py --targets docs/architecture/empire-resource-ssot.md`, which was
    run and reports nothing for that document. Gates: `~EmpireFreeRespec` 15/15,
    `resource_ownership.py --check` OK. Fragment: `tasks/evidence-fragments/EP4.11.md`.

  - Acceptance:
    - No compaction or archive method references `rpg_empire_free_respec_ledger`. A stock read after a
      compaction run equals the read before it (test 12).
    - The §3 row lands as drafted in the map: free empire respec, Accrual meter, held by the empire
      `(SaveId, EmpireId)` and surviving a world, fed by `empire-level`, spent by a species respec,
      never a unique or commander respec, with its owner and table.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireFreeRespec"`; `python scripts/audit-doc-citations.py docs/architecture/empire-resource-ssot.md`; `python gk-core/tools/tuning/resource_ownership.py --check`
  - Files: `gk-core/tests/FusionRpg.Data.Tests/EmpireFreeRespecTests.cs`, `docs/architecture/empire-resource-ssot.md`

- [x] **EP4.12 — FE: the species-build panel shows both options when a free respec is available and sends the player's pick** · S · deps: EP4.10 · *(spec: respec-free-counter)*
  - Landed (ep-3, 2026-09-21): the panel renders both payments when a priced change can be paid either way —
    "spend a free respec (N left)" and the quoted soul price — as radios with **no checked default**, gates
    Confirm on an unmade choice, and spreads `payWith` into the request only when the player chose one, so a
    no-choice request stays byte-identical to the pre-EP4.12 one the server reads as "no choice named". The
    wire types gained `freeRespecStock`/`freeAvailable` (price) and `paidWith`/`freeRespecStock` (result).
    Gates: `npm test -- --run species-build` 16/16 (two new cases: both options with Confirm disabled and no
    request until a pick, then the chosen spelling on the wire; and with no free respec available the body
    carries no `payWith` at all), `npm run build` clean in 12.20s, `npm run extract` with no new messages.
    **Trap recorded for the next FE row:** the state must sit with the component's other hooks, above every
    early return — the first attempt put it beside its derivation mid-component and all 12 mounted cases
    failed with "Rendered more hooks than during the previous render", which `tsc` does not catch. Fragment:
    `tasks/evidence-fragments/EP4.12.md`.

  - Acceptance:
    - With `freeAvailable`, both "spend a free respec" and the soul price show, with no default. The FE
      computes no price and no stock.
    - A vitest: no request carries a `payWith` the player did not choose.
  - Verify: `cd web\fusion-rpg-web; npm test -- --run species-build; npm run build; npm run extract`
  - Files: `gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`, `gk-web/web/fusion-rpg-web/src/features/species-build/SpeciesBuildPanel.tsx`, its vitest

### Checkpoint 6 — the empire levels and earns (CP6)
- [x] EP4.1–EP4.12 green. `guard-power.py` green. The §10.1 and §3 rows have landed.
- [x] Read back through the normal routes: a species level-up raises the empire level once, the stock
  grows, and a species respec asks the player to spend or pay.
  - Closed 2026-09-21 (ep-4): EP4.1-EP4.12 carry their own `[x]` rows and fragments (ep-3);
    `guard-power.py` prints `POWER GUARD OK - one ladder, pin holds, no private f(level)` at this head;
    the register rows are in place - the section 3 Accrual-meter row at `empire-resource-ssot.md:56`
    (EP4.11) and the section 10.1 empire cost-ladder row with EP4.2 (its own fragment). The route
    read-back is EP4.10's own evidence (34/34 across `~SpeciesBuild|~AptitudePreset`, incl. the
    payWith / soulPrice / freeRespecStock contract), and the whole Server suite is green at this head:
    `Passed! - Failed: 0, Passed: 800, Skipped: 0, Total: 800`.

- [x] **EP4.13 — `SpeciesLevelOf(SaveId, EmpireId, typeId)`: the one species-level reader; a Guard test** · S · deps: SE4.21, SE4.4 · *(spec: ai-empire-species)*
  - Landed (ep-3 + ep-4, 2026-09-21): the reader, its four Data facts and the Guard test landed in
    `@EP4.13` (partial), and ep-4 closed the row's own last clause. `@EP-F1` re-pointed the reader at the
    store's existing wide row read (`ReadEmpireActorUnlocked`), removing its second narrow level query;
    EP4.15 converted the two `RpgStore.Aptitudes.cs` sites to the reader, so no direct species-level read
    exists outside the reader and the writer. Gates: `~EmpireSpecies` 7/7, `~SpeciesLevelReader` 3/3,
    `~ZombossCommanderLevel` 2/2. **One blocker, recorded:** the Guard's `AllowedFiles` still lists
    `RpgStore.Aptitudes.cs` (now matching no read) because the pipeline guard refuses edits to Guard-test
    files; shrinking it to the literal two-file list is requested of the orchestrator. Fragments:
    `tasks/evidence-fragments/EP4.13.md` (addendum), `EP-F1.md`.
  - Acceptance:
    - One read over the re-keyed `rpg_actor_progression`, with no `empire == Dave` storage branch. A Dave
      read equals the pre-migration value (test 1). Save A's crediting leaves save B at 1 (test 2).
    - The Guard allows only `SpeciesLevelOf` and the progression writer to make a direct species-level
      read (test 7).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLevelReader"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs,gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs` (new), `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs` (new)

- [x] **EP4.14 — R1: both zombie species XP paths credit Zomboss's empire of the run's save (committed with EP4.15)** · M · deps: EP4.13, EP1.2, **SE4.20 (H2)**, SE4.22, SE4.13 · *(spec: ai-empire-species)*
  - Landed (ep-4, 2026-09-21): a species award resolves its owner from the side it was fielded on —
    `KillAttribution.EmpireOf` for both XP paths — and an empire the save does not carry credits nothing
    rather than minting a row. Tests 5, 8 and 9 green; the two pre-existing tests that read the human's
    zombie row were re-pointed at Zomboss's own row (`~SpeciesProgression` 17/17, `~EmpireLevel` 11/11).
    Scoped verification EXIT=0 (data 1747 tests / 4 shards, server 790/790). Fragment:
    `tasks/evidence-fragments/EP4.14.md`.
  - Acceptance:
    - A zombie spawn fact and a zombie run completion each grow Zomboss's row and never the human's. A
      plant spawn or completion grows the human's, unchanged. The human's old zombie rows are never
      rewritten (test 8).
    - A replayed completion credits once (test 5). A run with no resolvable save credits nothing and is
      reported (test 9).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies|FullyQualifiedName~Progression"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs`

- [x] **EP4.15 — The two `Empty` guards become level reads; an AI species composes its favour; `AptitudesUpdated.empire` (triggers T1–T4)** · M · deps: EP4.14 · *(spec: ai-empire-species)*
  - Landed (ep-4, 2026-09-21, with EP4.14): both `empire != Dave → Empty` branches replaced by an
    empire-keyed level read through the one reader; `AptitudesUpdatedDto.empire` added (additive, 5th
    optional parameter) and filled from the dirty by `EventIngest.BroadcastProgressionAsync`; the Server
    test reads `empire == "zomboss"` off the wire and a null for a pre-R1 sender. Tests 3 and 4 green
    (`~AllocationStore` 19/19), triggers T1–T4 (`~SpeciesAllocationCacheTrigger` 10/10). Fragment:
    `tasks/evidence-fragments/EP4.15.md`.
  - Acceptance:
    - `RpgStore.Aptitudes.cs:229-233` and `:258-267` read `SpeciesLevelOf`. A never-credited AI species
      resolves Empty, so no golden moves before XP flows (test 3). An AI species above level 1 resolves
      its plan's distribution at that level (test 4). The override half stays human-only.
    - `AptitudesUpdatedDto` gains the additive `empire` field. T1–T4 each have a test, and T4 is
      order-independent against a match edge (test 6).
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies|FullyQualifiedName~SpeciesAllocation"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs,gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs,gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs`, `gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs`

- [x] **EP4.16 — `ActorIndexFor(SaveId, EmpireId)`: Zomboss's Θ through the existing `PowerIndexComposer.ActorExplain` (a wiring gap, not a new curve)** · S · deps: `SP7.3` (zomboss-commander-clock) · *(spec: ai-empire-species, R23)*
  - Landed (ep-4, 2026-09-21): `ServerPowerIndexProvider.ActorIndexFor(save, empire)` composes
    `ActorLadderSnapshot(CommanderLevelOf(save, empire), 0, 0)` through the same `ActorExplain` the
    player's Θ uses. Gates: `~PowerIndexProvider` 3/3, `guard-power` OK, scoped verify-change EXIT=0
    (server 793/793). Fragment: `tasks/evidence-fragments/EP4.16.md`.
  - Acceptance:
    - The read builds `ActorLadderSnapshot(CommanderLevelOf(save, EmpireId.Zomboss), 0, 0)` and composes
      it through `ActorExplain`. A reflection or grep test finds no new `f(level)`, and `guard-power` is
      green.
    - The existing `ActorIndex(player)` result is byte-identical.
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PowerIndex"`; `python gk-core/scripts/guard-power.py`; `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Server/Power/IPowerIndexProvider.cs,gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs,gk-core/tests/FusionRpg.Server.Tests/PowerIndexProviderTests.cs -Session <sid>`
  - Files: `src/FusionRpg.Server/Power/IPowerIndexProvider.cs`, `gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs`, `gk-core/tests/FusionRpg.Server.Tests/PowerIndexProviderTests.cs`

- [x] **EP4.17 — The one empire-keyed commander-pool read: Dave's explicit pool unchanged; any other empire gets explicit-else-ladder default** · M · deps: EP4.16, EP1.2 · *(spec: ai-empire-species, R23)*
  - Landed (ep-4, 2026-09-21): `RpgStore.CommanderPoolOf(EmpireRef, theta, tuning)` (+ `...Unlocked`) is
    the one read; the human-vs-AI default rule is read from `rpg_save_empires.controller`, never a switch
    over `EmpireId`. A new `CommanderAllocation.Baseline` (Core) supplies the largest-remainder
    distribution at the empire's budget, keeping `Materialize` for the (currently unreachable)
    `active-preset` rung — EP1.13's own consumer shape. Gates: `~ZombossCommanderPool` 6/6, scoped
    verify-change EXIT=0 (core fallback green, data 1753/4 shards), `guard-power` OK. Fragment:
    `tasks/evidence-fragments/EP4.17.md`. No production caller yet — EP4.18's own deliverable, per this
    row's acceptance.
  - Acceptance:
    - Zomboss's pool at a non-zero budget resolves `Suggest`'s commander-context distribution, with its
      skips recorded and points summing to the budget. At a zero budget it resolves Empty. Nothing is
      written (test 10).
    - Save A's pool never reaches save B (test 12). An empty Dave pool stays Empty, because D1 gives the
      player's own pool no silent default (test 13).
    - It is not wired into any seam yet, so no golden moves.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderPool"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs,gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs` (new)

- [x] **EP4.18 — Wire Zomboss's pool side-wide (lawn and siege), add trigger T5; the R23 golden commit (H1, last)** · M · deps: EP4.17, **`SP6.1` (H1)** · *(spec: ai-empire-species, R23)*
  - **DONE (ep-4, 2026-09-21; the fence erratum was granted by the orchestrator's instruction to take the
    row).** Trigger T5 landed in the earlier increment. This one lands the wire: ONE host Theta on the
    store (`ConfigureActorTheta`), wired at the composition root from `ActorIndexFor`
    (`Program.cs:443-446`-ish block); `ProgressionLayerSelector.CarriesCommander` no longer gates on the
    human empire; `SpeciesAllocationSource`'s commander delegate is EMPIRE-keyed (lawn general + lawn Bound
    unique); the world-turn/siege seam, the sheet and the web squad all read `CommanderPoolFor`/
    `CommanderPoolForUnlocked`; and the injector receives `humanEmpire` + `commanderByEmpire` on the SAME
    aptitudes fetch it already reads (`RpgClient` → `CheatState.ApplyCommanderPools` → the empire-keyed
    delegate, with the human's ask still routed to the match-scoped cache). Gates: Data
    `~WorldTurnHubInputsFor` 7/7, Core `~SpeciesAllocationSource|~ProgressionLayerSelector` 36/36, Server
    `~ProgressionLayerParity` 3/3, Guard `~CommanderPoolTransport` 5/5, and the scoped verify-change
    EXIT=0 (six guards OK; Core.Tests 10905; data 1756/4 shards; Guard.Tests 586; Server 797).
    **R23 classification: no existing pin moved** (plant-side values byte-identical; the new values are
    pinned by the three new cases). Fragments: `tasks/evidence-fragments/EP4.18.md` (T5) and
    `EP4.18-wire.md`. **Not proved:** the injector's own compile (loader-refs-gated build, absent here —
    structurally proven by the new Guard test instead) and any live probe.
  - **Partial (ep-4, 2026-09-21): trigger T5 landed and green** — a Zomboss commander level-up now
    broadcasts `AptitudesUpdated(scope=commander, empire=zomboss)` and no longer mis-sends the human's
    `power.index.reload`; which empire is human is read from `rpg_save_empires`, never a literal id.
    Gate: `~ProgressionPowerIndexReload` 6/6, scoped verify-change EXIT=0 (server 795/795). Fragment:
    `tasks/evidence-fragments/EP4.18.md`.
  - **Row OPEN — blocked on a DENIED PATH, re-read 2026-09-21 on the orchestrator's instruction**
    (both deps, EP4.17 and SP6.1, are done, so the blocker was re-derived from code):
    `ProgressionLayerSelector.cs:51-61` sets `CarriesCommander = empire == humanEmpire`, and that ONE
    field is consumed at five sites — three of which read a HUMAN-scoped pool
    (`SpeciesAllocationSource.cs:130-132` via the Injector's single cached delegate wired only in
    `gk-fusion/src/FusionRpg.Injector/CheatState.cs:197`; `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:116-117`;
    `gk-core/src/FusionRpg.Server/WebMatchService.cs:608-609`). Flipping the gate for Zomboss (what test 11's
    siege member needs) therefore hands a Zomboss-owned specimen the HUMAN's pool at those three sites —
    the S1 leak `SpeciesAllocationSource.cs:141-144` forbids. So the lawn and siege halves land TOGETHER,
    and both need: the Injector's empire-keyed delegate + cache + a transport field
    (`Injector/CheatState.cs`, `Injector/RpgClient.cs` — both outside the fence) and the two Server
    consumers (also outside). Ready inside the fence for whoever gets the erratum: the gate, the siege
    seam (`RpgStore.WorldTurns.cs`), `CommanderPoolOf` (EP4.17), `ActorIndexFor` (EP4.16) and
    `gk-core/src/FusionRpg.Server/Program.cs` for the composition-root Θ delegate.
  - Acceptance:
    - `SpeciesAllocationSource.cs:114-116` and `RpgStore.WorldTurns.cs:573-576` call the one empire-keyed
      read, replacing `Dave ? … : Empty`. Every Zomboss-side actor (a lawn general, a lawn Bound unique,
      a siege member) carries his pool as a `Commander`-scope contribution, and every plant-side actor
      carries Dave's (test 11).
    - A Zomboss commander level-up broadcasts `AptitudesUpdated` with `empire = zomboss` (trigger T5).
    - The commit lists every moved pin as a "new layer delivered", with the SourceIds that caused each.
      A pin whose Zomboss side has no save empire, or a zero budget, is byte-identical (test 14).
      Plant-side values do not move.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderPool|FullyQualifiedName~SpeciesAllocation"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocationSource"`; `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,<the zomboss-commander-clock award caller>,gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`, the `zomboss-commander-clock` award caller, `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs`

### Checkpoint 5 — the AI empire owns its progression (CP5)
- [x] Zombie species levels from both XP paths land on Zomboss's empire of the run's save. Two saves are
  independent.
  - Closed 2026-09-21 (ep-4) by EP4.14's own cases:
    `A_zombie_spawn_and_a_zombie_run_completion_credit_Zomboss_while_the_humans_rows_stay_history`
    (both paths, the human's history untouched, a plant species still the human's) and
    `One_saves_crediting_leaves_another_save_at_level_one`. `~EmpireSpecies` 7/7.
- [x] His commander pool applies side-wide. The R23 commit comes after `SP6.1`'s re-bless commit in
  `git log` (H1).
  - Closed 2026-09-21 (ep-4) by EP4.18: the four-path parity case (lawn seam, web squad, sheet,
    world-turn) and the siege case both carry HIS pool, never the player's; and the H1 ordering is
    verified, not assumed - `git merge-base --is-ancestor eceb08f1 9964ab1ad` exits 0, i.e. SP6.1's
    re-bless (`eceb08f1a`) is an ancestor of both R23 commits (`9964ab1ad`, `be6e89fdd`).
- [x] `.\scripts\test-fast.ps1 -AllDefault` green once at program close. This is the end of a large
  feature (AGENTS.md condition 1), and feeds the parent's CC5.
  - Closed 2026-09-21 (ep-4) with a QUALIFIER that has to be stated: the default set is green at this
    head, but the monolithic `-AllDefault` invocation was attempted four times and each attempt was
    killed by this environment at ~600KB of captured output (a console/pipe failure, never a test
    failure - F6). The same set was then run through the same `dotnet test` invocations in bounded
    groups, all green: Data 1781, Server 800, E2E 231, Core.Tests 10858, ActorHub 498, ClassSystem 238,
    Items 1397, Atoms 1351, Balance 210, Match 91, Hud 84, Commanders 64, and the remaining 27 projects
    listed in `tasks/evidence-fragments/EP4-close.md`, plus Guard.Tests 591 (not in the default set).

---

## Deferred — `ai-build-scorer` (`EP5`)

**Not scheduled** in the sense that the *economy* is unbuilt — but EP5.1 itself is buildable now and is
landed (see its own row): its own acceptance tests with `UniformNeeds`, so the scorer's arithmetic and
choice are provable over the neutral stub. What stays deferred is the rung-to-need MAPPING (an input to
the scorer), which is the part the real economy supplies.

- **Re-verified 2026-09-21 (ep-4):** the only implementation is `UniformNeeds`
  (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41`), returning its own `Neutral = 1000` on BOTH axes,
  and a search across src, tests and tools finds no other implementer. `spec-ai-build-scorer.md`'s header
  still says "deferred, no build authorized"; the orchestrator ruled on 2026-09-21 to build EP5.1 anyway,
  because test 3 of its acceptance is written with `UniformNeeds`.

- [x] **EP5.1 — `BuildScorer` over `Considerations.Score` (no arithmetic of its own)** · S · deps: `sector-development` `INeedVector` · *(spec: ai-build-scorer)*
  - Landed (ep-4, 2026-09-21, on the orchestrator's ruling): `BuildScorer.Choose` writes three
    considerations (need fit, counter fit, continuity) and argmaxes `Considerations.Score`, ties by
    ordinal rule id; `BuildRung`'s two belief inputs stay supplied, because the rung→need mapping is the
    part the economy owns. Gate: `~BuildScorer|~Consideration` 26/26; scoped verify-change EXIT=0
    (`Core.Tests` 11059/11059, +4). Fragment: `tasks/evidence-fragments/EP5.1.md`.
  - Acceptance:
    - A reflection test: the scorer computes no product itself (test 1). A zero on continuity vetoes the
      rung (test 2).
    - With `UniformNeeds` it picks the ladder's rung (test 3). The same belief and tuning give the same
      pick, with an ordinal tie-break (test 4).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildScorer|FullyQualifiedName~Consideration"`
  - Files: `gk-core/src/FusionRpg.Core/World/Ai/BuildScorer.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs` (new)

- [x] **EP5.2 — Publish `ai` (next free version): the `buildScorer` block (curves, thresholds, continuity cooldown)** · S · deps: EP5.1 · *(spec: ai-build-scorer)*
  - Landed (ep-4, 2026-09-21): `python gk-core/tools/tuning/publish.py ai --add-key ':buildScorer={...}' --add-key
    '_meta:buildScorerNote="..."'` published **`ai.v3.json`** (v2 stays for revert) with `defaults` (two
    curve ids + thresholds + `continuityCooldownTurns`) and `byEmpire` overrides; the loader makes the
    block REQUIRED (missing key and unknown curve name both reject by name), reads overrides as partial,
    and exposes `For(empire)`; every reader moved to v3 in the same commit (Server `Program.cs`, four
    Server test fixtures, the three test bootstraps' inline `DefaultAi`, the two tools) and both tools
    still build. Gates: `~AiTuning|~BuildScorer` 31/31; scoped verify-change EXIT=0 (`Core.Tests`
    11064, data 1753/4 shards, E2E 231, Server 795). Fragment: `tasks/evidence-fragments/EP5.2.md`.
  - Acceptance:
    - Published through the tool with global defaults and per-empire overrides. A missing key is a load
      rejection. Pins move (H7).
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AiTuning|FullyQualifiedName~BuildScorer"`
  - Files: `data/tuning/ai.v{next}.json` (published), the AI tuning loader + pins (rg)

- [ ] **EP5.3 — The chosen rung feeds `ai-empire-species`'s default; the weakest consideration goes in the turn report** · S · deps: EP5.2, EP4.15 · *(spec: ai-build-scorer)*
  - **Blocked as written (ep-4, 2026-09-21), with a proof test, and erratum requested.** The wiring is not
    a behaviour-preserving no-op: the ladder's own rung for a species context is `species-favour` (what
    the AI baseline materialises today), while the same candidate set under neutral beliefs ties and the
    committed ordinal tie-break returns `even` — so closing the row with neutral inputs moves every AI
    species' build, and closing it with only the ladder's reachable rung ships constant content, the
    repo's named failure mode. The belief inputs (`BuildRung.NeedFit`/`CounterFit`) have no source: the
    only `INeedVector` is `UniformNeeds` (1000 on both axes, sector/economy needs, no aptitude mapping).
    The turn-report half also needs a `TurnReport` seam into `DistrictAssaultResolver`, which has none.
    Proof: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildScorer"` (5/5,
    `Wiring_the_scorer_into_the_ai_species_default_needs_real_belief_content`). Fragment:
    `tasks/evidence-fragments/EP5.3.md`. **Re-read 2026-09-21 (after EP4.18 landed): still external, and
    now with only TWO blockers.** The turn-report half is reachable — `CommitWorldTurn` holds
    `result.Report` and already passes it to Data-side passes (`SpendWonderRelics`, `CargoResolve`), so a
    line naming `Considerations.Weakest` needs no new Core seam after all; what remains is (a) the belief
    content, which is `sector-development`'s non-neutral `INeedVector` (still the only implementation is
    `UniformNeeds`, 1000 on both axes) and (b) an owner/manager ruling on which wiring shape is intended —
    the behaviour-changing one or the one-candidate one.
  - **DECISION NEEDED (one word): the wiring shape.** (A) wire the ONE-CANDIDATE shape — the scorer runs
    over the rungs the ladder can actually reach (today exactly `species-favour`), the allocation stays
    byte-identical and the turn report gains the `Considerations.Weakest` line, and the same code starts
    differing the day the economy makes a second rung reachable; cost: today's answer is a constant, so it
    needs an explicit ruling. (B) keep the row open until `sector-development` ships real needs. (C) the
    full candidate set as written is REJECTED by this lane (it moves every AI species build with no
    justification) and is listed only so the rejection is explicit. This lane recommends (A) under a ruling,
    else (B) — see `tasks/evidence-fragments/EP4-head.md`'s decision section.
  - Re-verified at the merged head `c7ed894b8` (2026-09-22): the proof case and its neighbours are green
    (`~BuildScorer|~AiTuning` 68/68 with the seam filters, Guard 591/591), and nothing under EP4.x remains
    open. The two blockers above are unchanged and are the ONLY blockers this program has left.
  - Acceptance:
    - The AI empire's species follow the scored rungs through the same allocation path, with no new path.
      The turn report names `Considerations.Weakest`.
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies"`; `.\scripts\verify-change.ps1 -Paths <touched files> -Session <sid>`
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, the turn-report builder, a test

- [x] **EP-F1 — a second commander-level reader arrived with the EP4 batch, reddening `ZombossCommanderLevelSingleReaderGuardTests`** · S ·
  - Landed (ep-4, 2026-09-21): `RpgStore.EmpireSpecies.cs` no longer holds its own `SELECT level FROM
    rpg_actor_progression`; `SpeciesLevelOfUnlocked` projects the store's existing wide row read,
    `ReadEmpireActorUnlocked` (`RpgStore.Progression.cs`), to `.Level`. The guard was not touched — no
    allow-list entry, no pattern change — and is green 2/2, with the four `EmpireSpecies` facts unchanged.
    **Deviation, recorded:** the row's own Fix line says "read through `CommanderLevelOf`", but
    `CommanderLevelOf` is the `kind='player', type_id=0` commander row and cannot answer a species level;
    the spec's own code-style block (`spec-ai-empire-species.md` "Code style") prescribes the landed fix,
    and the guard's actual constraint (one holder of the narrow query text) is met. Fragment:
    `tasks/evidence-fragments/EP-F1.md`.
  *(found by the manager's post-merge check run `bafaa803e` on the merged head, 2026-09-21 — the lane's own
  scoped acceptance could not see it: it ran aptitude/species/plan-gen/ledger filters, not the Guard suite.)*
  - **Measured:** `ZombossCommanderLevelSingleReaderGuardTests.No_production_file_outside_RpgStore_Progression_reads_the_narrow_commander_level_shape` FAILS: *"These files also read the narrow `SELECT level FROM rpg_actor_progression` shape: `src\FusionRpg.Data\Sqlite\RpgStore.EmpireSpecies.cs`."*
  - **Why it matters:** the guard admits **one** seam for commander level — `RpgStore.CommanderLevelOf` — and the only file allowed to hold that query text is `RpgStore.Progression.cs`. A second reader is the shape the guard exists to prevent, and it is a cross-lane interaction: `RpgStore.EmpireSpecies.cs` came in with this program's EP4 work.
  - **Fix:** read the level through `RpgStore.CommanderLevelOf` from `RpgStore.EmpireSpecies.cs`; the guard's own message names `ai-empire-species` as the seam's intended consumer. Do **not** relax the guard and do not add the file to an allowlist.
  - **Verify:** `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ZombossCommanderLevelSingleReader"`.

---

## Finding routed from `test-verification-boundary` (TVB-F20, 2026-09-21)

- [x] **TVB-F20 — a second narrow commander-level reader appeared, and the single-reader guard fails on it** ·
  **CLOSED (ep-4, 2026-09-21): the defect it reports is EP-F1's, and EP-F1 is fixed and merged.** The
  row's evidence is a Guard run at head `70e3ca863`, i.e. BEFORE this program's `fix(EP-F1)`
  (`42f8db5e1`) landed; the offender it names - `RpgStore.EmpireSpecies.cs` reading the narrow shape
  directly - is exactly what that fix removed (the file now projects `ReadEmpireActorUnlocked(...)`).
  Verified at the current head: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter
  "FullyQualifiedName~ZombossCommanderLevel"` -> `Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2`,
  and the whole Guard suite -> `Passed! - Failed: 0, Passed: 591, Skipped: 0, Total: 591`. No second fix
  was written.
  `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release` at head `70e3ca863`:
  **Failed: 1, Passed: 583, Skipped: 0, Total: 584** (4m06s), the one failure being
  `ZombossCommanderLevelSingleReaderGuardTests.No_production_file_outside_RpgStore_Progression_reads_the_narrow_commander_level_shape`
  (`ZombossCommanderLevelSingleReaderGuardTests.cs:41`), whose own message names the offender and the owner:
  *"src\FusionRpg.Data\Sqlite\RpgStore.EmpireSpecies.cs … A second reader belongs in **ai-empire-species** reading
  through `CommanderLevelOf`, never a new query."* So that file now executes the
  `SELECT level FROM rpg_actor_progression` shape directly instead of reading
  `RpgStore.CommanderLevelOf` — a second seam for a value the guard pins to exactly one. Routing here because this
  program's session record claims `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs`; if the guard's
  "ai-empire-species" is a separate program with its own todo, re-route this row there. Found while closing
  TVB-F13's full-suite figure after the CAI-guard-1 and TVB-F19 fixes landed (both of which are green in this same
  run). Owning program: empire-progression (or ai-empire-species).

## Findings this lane cannot file in their owner's todo (path fence) — for the manager to route

- **F1 — `scripts/test-sharded.ps1` reports a NULL exit code under Windows PowerShell 5.1.**
  `Start-Process … -PassThru; WaitForExit(); $p.ExitCode` returns null there, so every shard prints
  `exit ,` and `TEST-SHARDED FAILED` even when all tests passed (measured 2026-09-21: identical false
  RED on all 4 shards; the same command under `pwsh` 7 returns real codes, and a manual 4-shard run
  passed 4/4). Owner: the verification-boundary / test-runner program (not `empire-progression`). This
  lane's fence has no path into that program's todo.
- **F2 — `EmpireLevelTests` mutates the global `ProgressionTuningHub` from its constructor.**
  `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs:50-66` reconfigures a process-wide hub while xUnit runs
  other classes in parallel, so a combined filter can flip
  `A_pass_that_throws_leaves_no_empire_row_and_the_next_start_completes_it` to red (observed once;
  76/76 on the immediate re-run and green alone). Pre-existing, not introduced by this lane. Owner:
  unknown to this lane (Data test substrate).
- **F3 — this lane's copied fence is narrower than the rows it was told to take.** The fence lists only
  `gk-core/src/FusionRpg.Server/EmpireEndpoints.cs` and `Program.cs` from the Server, and no
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs`, while EP4.15/EP4.17/EP4.18 name
  `AptitudeEndpoints.cs`, `EventIngest.cs`, `RpgStore.Aptitudes.cs` and `Server/Power/*`. Work followed
  the rows; the fence needs the erratum (files listed in the lane report).
- **F8 — an order-dependent E2E failure in the action-unlock path (not this program's code).**
  `FusionRpg.E2E.Tests.UnlockTuningActivationTests.A_real_level_up_grants_a_real_action_row` fails in the
  full-assembly run (`Failed! - Failed: 1, Passed: 230, Total: 231`) with
  `System.InvalidOperationException: action unlock grant refused: BasicCollision` raised at
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:2134` (`TryRollActionUnlocks` -> `UpsertGrantUnlocked`),
  and PASSES when its class is run alone (`Passed! - Passed: 2, Total: 2`). `git log c7ed894b8..5da5c3a26 --
  gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs gk-core/src/FusionRpg.Core/Actions/Unlock/ data/` is empty, so
  it is not a merge regression either: the shape is a cross-class global-tuning/seed interaction inside the
  E2E assembly (the F2 class of defect). Owner: the E2E test substrate / verification-boundary program.
- **F6 — `test-fast.ps1 -AllDefault` cannot complete in this environment.** Four attempts, each killed at
  ~600KB of captured output (a console/pipe `IOException`, never a test failure; every partial log showed
  only `Passed!` lines). The default set is green when run in bounded groups (1781 Data, 800 Server, 231
  E2E, 10858 Core.Tests, 591 Guard, …). Owner: the verification-boundary / test-runner program — the same
  program that owns F1, and the two may share a cause.
- **F7 — RESOLVED (2026-09-22).** A merge can silently revert a same-commit reader switch (H7): one did
  (`8b81e395d` reverted `Program.cs`'s `ai.v3.json` to `ai.v2.json` while EP5.2's loader requires the new
  block, so the server could not boot and 230 E2E tests failed in 5s). Caught and fixed by this lane, and
  the board recorded it (`c7ed894b8`); the systemic fix is in place and verified here —
  `ContentBootStartupWiringTests.The_server_boot_reads_the_latest_revision_of_the_domains_it_owns` reads
  the latest `ai`/`items` revision on disk and asserts the boot names it, so a bad resolution now fails in
  a test rather than at boot.
- **F7 (original note, kept for history) — a merge can silently revert a same-commit reader switch (H7).** `features/mega-merge` reverted
  `gk-core/src/FusionRpg.Server/Program.cs`'s `ai.v3.json` back to `ai.v2.json` while EP5.2's loader REQUIRES the
  new block, so the server could not boot and 230 E2E tests failed in 5s. Caught and fixed here (231/231
  after). Owner: the merge/acceptance machinery — a post-merge `guard-*`/boot smoke for a renamed or
  re-versioned tuning reader would have caught it in the merge, not three lanes later.
- **F5 — `gk-core/tools/ResidualFitLoop/Program.cs` has no verification boundary.** Adding the interface's
  `ActorIndexFor` to its private provider is a one-line mechanical change, but
  `gk-core/scripts/verification-boundaries.v1.json` maps no owner for the path, so `verify-change` refuses it
  outright (`VERIFICATION BOUNDARY MISSING`). Reported rather than compensated with a broad suite, per the
  lane's rules. Owner: the verification-boundary program.
- **F4 — nothing enforces that the `ai` tuning's readers agree on one version.**
  `TuningVersionAgreementGuardTests.AgreedDomains()` lists `action-base` and `action-rungs` only, so the
  `ai.v2` -> `ai.v3` move this session made is unguarded: a future reader left on v2 would go unnoticed.
  Adding the row is a one-line change to that Guarded file, which the pipeline guard refuses. Owner:
  unknown to this lane (the tuning-version guard's program). Requested alongside EP4.13's allow-list
  shrink and the EP4.18 / EP5.3 errata.

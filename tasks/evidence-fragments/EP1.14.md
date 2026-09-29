# EP1.14 — Every production reader calls the resolver; Guard test; the goldens that moved (own commit, H1)

Spec: docs/architecture/empire-progression/spec-default-build.md

## The five call sites wired

| Site | Change |
|---|---|
| `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:196` (`ProjectUniqueState`) | `store.LoadAllocation(...)` → `store.EffectiveUniqueAllocation(...).Allocation` |
| `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:119` (`ResolveAptitudeAllocation`) | same swap |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs` (~431, `aptitude.snapshot` telemetry) | same swap |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs` (~633, `BuildSquad`'s `HubInputs.Aptitude`) | same swap — the real combat-math input |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:521` (`WorldTurnHubInputsForUnlocked`, siege member) | `LoadAllocationUnlocked(...)` → `EffectiveUniqueAllocationUnlocked(...).Allocation` |

`grep -rn "AllocationScope.UniqueCreature" src --include=*.cs \| grep -E "LoadAllocation\(\|LoadAllocationUnlocked\("`
now shows exactly one hit: the resolver's own definition (`RpgStore.Aptitudes.cs:328`).

## Guard test (test 5)

`gk-core/tests/FusionRpg.Guard.Tests/UniqueAllocationReaderGuardTests.cs` (new) — the exact structural twin
of `AllocationWriterGuardTests.cs`: outside `RpgStore.Aptitudes.cs` (the resolver),
`RpgStore.AllocationRespec.cs` (the priced gate's own free-vs-priced read), and
`DerivedAuditActor.cs` (the allowed RPG Server Debug fixture), no file may read the scope directly.

## A real design defect found and fixed — not a golden move

Wiring `WebMatchService.BuildSquad` broke ~13 pre-existing tests across `BuildSquadEquippedActionsTests`,
`EquippedHubParityTests`, and one `AuraDerivedEndpointsTests` method with a HARD THROW:
`AptitudePresetTuningHub.Configure(...) has not run`. `EffectiveUniqueAllocationUnlocked` reads that
hub unconditionally once a specimen has no explicit allocation, and every one of those pre-existing
fixtures builds a squad without ever configuring it (they test equipped-action wiring, not
aptitudes). This is not a golden move — a resolve that used to succeed at Empty now throws, taking
down an unrelated caller's whole test.

**Fix:** added `AptitudePresetTuningHub.IsConfigured` (`AptitudePresetTuning.cs`), the SAME
best-effort contract `EffectiveSpeciesAllocationUnlocked` already gives an unconfigured
`SpeciesBuildPlanCatalog` — a real server always configures this at boot (confirmed:
`gk-core/tests/FusionRpg.E2E.Tests/RpgApiFactory.cs` boots the real `Program.cs`, so E2E never hits this
fallback), but a fixture reached indirectly through an unrelated seam must not have its whole
resolve taken down by a hard throw. `EffectiveUniqueAllocationUnlocked` now returns
`AptitudeAllocation.Empty` (matching the pre-EP1.13 behaviour those fixtures already expect) when
the hub is unconfigured, instead of running the ladder.

## The two tests that DID need updating — real, explained, in this commit (H1)

`gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs` — `AptitudePresetTuningHub` is a
process-wide static; once configured it stays configured, so a broad filtered run that also
exercises `AptitudePresetEndpointsTests` (which does configure it) made this file's assertions
order-dependent. Fixed at the root: this file's own `InitializeAsync` now configures the hub
deterministically, matching every other file that reads `EffectiveUniqueAllocation` (`AllocationRespecTests.cs`,
`AllocationStoreTests.cs`, `EffectiveUniqueAllocationTests.cs`). With that in place, two tests'
expectations are genuinely, permanently wrong under default-build and are corrected here, not
merely re-blessed:

- `UniqueGet_freshSpecimen_returnsEmptySharesAndLeftoverEqualsBudget` → renamed
  `..._withNoSpeciesProfile_resolvesTheEvenDefault_notEmpty`. This actor has no creature profile
  (`EnsureUniqueActorForAudit` never writes one), so species-favour and posture both refuse and the
  ladder lands on `even`. Rewritten to assert the CONTRACT (every share `> 0`, `spent == budget`,
  `leftover == 0`) rather than a literal, matching this program's own no-population-pin discipline.
- `UniquePost_overBudget_409_neverClamps` — PS-8's own "refused, never clamped" comparison was
  hardcoded against `0`; now compared against `before.Shares["Might"]` (whatever the default reads),
  which is what "never clamps" actually means. The raw-store assertion (`_store.LoadAllocation(...)`)
  needed no change: the persisted row is genuinely still empty since nothing was ever explicitly saved.

No other test's expected value moved. No hash-based golden (`BattleGoldenTests.cs`,
`ExpeditionResolverTests.cs`) moved — EP1.12 already predicted this (neither is reachable by this
resolver swap) and this commit confirms it holds.

## Verification

| Command | Before wiring | After wiring + fixes |
|---|---|---|
| `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude\|FullyQualifiedName~WebMatch\|FullyQualifiedName~ProjectStanding\|FullyQualifiedName~ProgressionLayerParity\|FullyQualifiedName~SpeciesLayerPath\|FullyQualifiedName~ActorSheetHotLiveState\|FullyQualifiedName~EquippedHubParity\|FullyQualifiedName~StarLoyaltyHubParity\|FullyQualifiedName~ZombossAdaptiveSeam\|FullyQualifiedName~BuildSquadEquippedActions\|FullyQualifiedName~SpecimenLoadoutEndpoints"` | 99/99 | 99/99 (run twice, deterministic) |
| `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn\|FullyQualifiedName~ActionCatalogBuilder\|FullyQualifiedName~ActionContainerEffectResolverFactory\|FullyQualifiedName~ActionUnlockGrantWiring\|FullyQualifiedName~BattleHolderWiring\|FullyQualifiedName~ItemGrantStore\|FullyQualifiedName~AllocationRespec\|FullyQualifiedName~AllocationStoreTests\|FullyQualifiedName~EffectiveUnique"` | 56/56 (WorldTurn+ subset) | 94/94 |
| `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~UniqueAllocationReader\|FullyQualifiedName~AllocationWriter"` | n/a (new file) | 4/4 |
| `.\scripts\guard-dal.ps1` | — | `DAL GUARD OK` |
| `grep -rn "AllocationScope.UniqueCreature" src \| grep -E "LoadAllocation\("` | 5 raw reads | 1 (the resolver itself) |

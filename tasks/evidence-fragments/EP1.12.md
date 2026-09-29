# EP1.12 — Before-image: golden fixtures baseline

Spec: docs/architecture/empire-progression/spec-default-build.md, testing strategy item 8

## Fixture search (acceptance clause 1)

Grepped every hash/golden-named test file for a levelled `UniqueCreature` specimen with an empty
allocation, per the acceptance text ("grep the battle, expedition and siege fixtures"):

```
grep -rln "Golden" tests --include=*.cs | grep -iE "battle|expedition|siege"
  -> BattleGoldenTests.cs, ExpeditionResolverTests.cs (no siege-named golden file exists)
grep -n "UniqueCreature|EnsureUniqueActorForAudit|MintForEmpire|level:" tests/.../ExpeditionResolverTests.cs
  -> no matches: pure tier-resolution math, no unique specimen at all
BattleGoldenTests.cs actors are built via a local `Actor(key, side, level, ...)` helper producing
`BattleActorSetup` records directly in Core -- they never call RpgStore.LoadAllocation at all (no
store, no connection in this test class), so EP1.14's resolver swap cannot move these hashes: the
swap only changes what `LoadAllocation(Unlocked)` returns, and this file never calls it.
grep -rln "EnsureUniqueActorForAudit|MintForEmpire" tests --include=*.cs
  -> AllocationRespecTests.cs, Saves/AiEmpireSpecimenTests.cs, Saves/SaveIdentityFixtures.cs,
     Saves/SpecimenOwnershipTests.cs, ZombossDeployStoreTests.cs, AptitudeEndpointsTests.cs,
     AptitudePresetEndpointsTests.cs, AtomPushServiceOwnersForSaveTests.cs,
     ZombossDeployEndpointsTests.cs -- none of these files assert a hash or a literal combat-derived
     magnitude for a levelled, unallocated specimen (all either assert ownership/refusal shape or
     drive their own explicit allocation).
```

**Finding: no fixture in the current test suite holds a levelled `UniqueCreature` specimen with an
empty allocation and asserts an exact/hash-based combat outcome.** The two real golden-hash test
files in the repo (`BattleGoldenTests.cs`, `ExpeditionResolverTests.cs`) are both structurally
unreachable by EP1.14's resolver swap (Battle's actors never call the store at all; Expedition's
tier math never touches a unique specimen). This is a reading, not an assumption: EP1.14's own
commit is where this prediction gets its real test, since nothing here can be verified without the
resolver actually wired in. If EP1.14 moves a golden anywhere, this list explains it did NOT come
from a fixture named here — a defect, not an expected move (H1 boundary).

## Baseline capture (acceptance clause 2) — scoped, not the four-project suite

**Correction (2026-09-20, coordinator):** the machine is running 22 concurrent `dotnet.exe` test
hosts across seven lanes; a `test-fast.ps1 -AllDefault` run stretched past 10 minutes twice and was
stopped both times without reporting. Re-scoped to the boundary that actually covers what EP1.14
touches — the exact filters EP1.14's own Verify line names, run in the foreground:

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude\|FullyQualifiedName~WebMatch"` | pass (55/55) — covers `AptitudeEndpoints.cs`, `UniqueActorHubCompose.cs` (via `AptitudeEndpointsTests`'s sheet-compose paths), both `WebMatchService.cs` sites |
| `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"` | pass (21/21) — covers `RpgStore.WorldTurns.cs`, the siege member read |

No failure predates EP1.14 in this boundary. If a broader four-project run is later found necessary
(e.g. a cross-boundary failure this scoped pair cannot see), that is the orchestrator's call to
schedule when the machine is quieter — not a default reflex for this task.

## The five call sites EP1.14 will wire (research recorded here, executed there)

1. `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:119` — `ResolveAptitudeAllocation`
2. `gk-core/src/FusionRpg.Server/WebMatchService.cs` (~line 431) — the `aptitude.snapshot` telemetry event
3. `gk-core/src/FusionRpg.Server/WebMatchService.cs` (~line 633) — `BuildSquad`'s `HubInputs.Aptitude` (the real combat-math input)
4. `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:521` (`WorldTurnHubInputsForUnlocked`, already `Unlocked`-shaped)
5. `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:196` (`ProjectUniqueState`)

A full-tree `grep -rn "AllocationScope.UniqueCreature" src` confirmed these are the only production
reads outside the resolver's own definition, vocabulary mapping, and the allowed `DerivedAuditActor.cs`
write path.

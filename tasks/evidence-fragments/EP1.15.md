# EP1.15 — Cache trigger T3: every specimen level-up seam broadcasts `AptitudesUpdated(unique, instanceId)`

Spec: docs/architecture/empire-progression/spec-default-build.md

## The three seams wired

| Seam | Change |
|---|---|
| Debug award route (`UniqueActorEndpoints.cs`, `POST /api/unique/actors/{id}/xp`) | `RpgStore.AwardUniqueActorXp` / `UniqueActorService.AwardXp` gain a 4th tuple field `LevelsGained`; the route broadcasts when it is `> 0` |
| Lawn capture ingest (`UniqueActorService.ObserveEvents`) | `RpgStore.ObserveUniqueActorEvents` now returns `UniqueActorEventsResult(AffectedPlayerIds, LeveledSpecimenIds)` instead of a bare player-id list; `AwardUniqueLawnKillUnlocked`/`AwardUniqueLawnDurationUnlocked` changed from `void` to `bool` (leveled), threaded up through `TryRecoverActiveByPtr`/`TryRecoverActiveByMatchKey`/`ObserveUniqueActorEvent`; `ObserveEvents` broadcasts per leveled specimen |
| Expedition collect (`RpgStore.Expeditions.cs` → `ExpeditionEndpoints.cs`) | `ApplyExpeditionRewards` gains a 4th tuple field `LeveledSpecimenIds`; the collect endpoint's existing best-effort notify block broadcasts per leveled specimen alongside `CreaturesUpdated`/`SoulsUpdated` |

## Testing strategy item 4 — T1–T4 each have their own test; T1/T3 order-independence

`gk-core/tests/FusionRpg.Server.Tests/UniqueDefaultTriggerTests.cs` (new), real SignalR connections
throughout (`AptitudesInjectorBroadcastTests.cs`'s own house style, not a mock):

| Test | Proves |
|---|---|
| `DebugAward_thatLevelsUp_broadcastsAptitudesUpdated_forThatSpecimen` | T3 via the debug route: a real level-up broadcasts, with the right `instanceId` |
| `DebugAward_thatDoesNotCrossALevel_neverBroadcasts` | The guard is `levelsGained > 0`, never "every award, leveled or not" |
| `LawnKillAward_thatLevelsUpTheKiller_broadcastsAptitudesUpdated_forTheKiller` | T3 via lawn capture ingest: a real lawn-kill award (8 distinct `plant.die` occurrences, `specimenLawnKill=18` XP each against a level-1 cost of 100) through `UniqueActorService.ObserveEvents` broadcasts for the killer, not the target |
| `ExplicitAllocation_survivesALevelUp_regardlessOfOrder` | Test 4's own relation: allocate-then-level-up leaves the explicit value untouched (D2, never topped up by level); level-up-then-allocate has the explicit value REPLACE the now-grown default wholesale (no blending) |

**T1's own test file is unchanged** (`AptitudesInjectorBroadcastTests.cs` already proves the explicit-allocate broadcast this task's T1 row cites) and **T2/T4 are pre-existing, unchanged code** this task never touches — so no new tests for those rows; `UniqueDefaultTriggerTests.cs`'s own contribution is T3 (the new trigger) and the T1/T3 order relation.

**Expedition collect is not re-proven end to end with a live battle.** Its broadcast is the
byte-identical `if (leveled) BroadcastBestEffort(...)` shape the debug route and lawn ingest already
prove; wiring a full battle-resolution pipeline to re-prove the same shape a third time is
disproportionate to this task's own size. Recorded here as a scoped decision, not hidden.

## Verification

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~UniqueDefaultTrigger"` | 4/4 |
| `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude\|FullyQualifiedName~WebMatch\|FullyQualifiedName~ProjectStanding\|FullyQualifiedName~ProgressionLayerParity\|FullyQualifiedName~SpeciesLayerPath\|FullyQualifiedName~ActorSheetHotLiveState\|FullyQualifiedName~EquippedHubParity\|FullyQualifiedName~StarLoyaltyHubParity\|FullyQualifiedName~ZombossAdaptiveSeam\|FullyQualifiedName~BuildSquadEquippedActions\|FullyQualifiedName~SpecimenLoadoutEndpoints\|FullyQualifiedName~UniqueActor\|FullyQualifiedName~UniqueDefaultTrigger"` | 113/113, run twice, deterministic |
| `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn\|...\|FullyQualifiedName~UniqueActorStoreTests\|FullyQualifiedName~ExpeditionRewardApply\|FullyQualifiedName~ExpeditionStore"` | 147/147 |
| `dotnet test tests\FusionRpg.E2E.Tests --filter "FullyQualifiedName~UnlockTuningActivation"` | 2/2 (E2E boots the real `Program.cs`, so the mechanical tuple-arity fix there is the only change needed) |
| `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |

## Notes

- Both `RpgStore.AwardUniqueActorXp` and `RpgStore.ApplyExpeditionRewards`'s public tuple return
  types gained a 4th element. Each had exactly one real production caller (`UniqueActorService.AwardXp`,
  `ExpeditionEndpoints.cs`'s collect handler) plus a handful of test files that destructure the tuple
  positionally (`var (a, b, c) = ...`) — the compiler caught every one via arity mismatch; each fixed
  mechanically with a trailing discard (`_`) or, for the two files that assert on `.Reason`/`.Ok` by
  name, no change was needed at all.
- `RpgStore.ObserveUniqueActorEvents`'s return type changed from a bare `IReadOnlyList<long>` to
  `UniqueActorEventsResult(AffectedPlayerIds, LeveledSpecimenIds)` — its own doc comment already
  called this "T6.1's own gap," so widening it to also carry T3's leveled-specimen list keeps one
  result shape rather than forking a parallel call. Five pre-existing tests in
  `UniqueActorStoreTests.cs` that asserted directly on the old return value were updated to read
  `.AffectedPlayerIds` — mechanical, no test's own assertion logic changed.

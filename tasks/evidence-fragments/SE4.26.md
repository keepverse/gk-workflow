# SE4.26 — Specimen reads by purpose: an empire's roster vs the match's runtime

Spec: save-identity, "Specimen reads are classified by purpose". `ListUniqueActors(EmpireRef)` (new)
reads `WHERE player_id=$pid AND empire_id=$emp` — an empire's own roster, never another empire's
specimen sharing the save's row; `ListUniqueActors(long playerId)` defaults to `HumanEmpireOf(playerId)`.
`AtomPushService.OwnersForPlayer` → `OwnersForSave(store, saveId)`: the human's own `player:{save}`
scope plus the ActiveBound specimens of **every** `EmpiresOf(save)`, not just the human's — the runtime
question stays unfiltered by empire on purpose. The stale-`ActiveBound` sweep
(`SweepStaleActiveBoundUnlocked`) and the kill-credit lookup (`ResolveLawnKillCreditUnlocked`, SE4.25)
already carry **no** player/empire filter at all, so both already covered every empire before this task
— confirmed by re-reading their SQL, no code change needed there.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Roster test: a Zomboss specimen of save 1 is absent from save 1's human roster | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AtomPushServiceOwnersForSaveTests" --nologo` | pass 4/4 — `ListUniqueActors_the_roster_read_excludes_the_same_Zomboss_specimen`, `ListUniqueActors_by_EmpireRef_returns_only_that_empires_own_specimens` | `RpgStore.UniqueActors.cs` |
| Runtime test: an ActiveBound Zomboss specimen of save 1 keeps its pushed atoms | same | pass — `OwnersForSave_includes_an_ActiveBound_Zomboss_specimen_of_the_same_save`, `OwnersForSave_still_carries_the_saves_own_player_scope` | `AtomPushService.cs` (`OwnersForSave`) |
| No regression: every `OwnersForPlayer` call site renamed | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AtomPush\|FullyQualifiedName~ItemEquipEndpointsTests\|FullyQualifiedName~MultiOwnerPushTests\|FullyQualifiedName~UniqueActor" --nologo` | pass 64/64 (`RpgHub.cs`, `UniqueActorService.cs`, `ItemEquipEndpointsTests.cs` all updated; grep confirmed zero remaining `OwnersForPlayer` code references) | `RpgHub.cs`, `UniqueActorService.cs`, `ItemEquipEndpointsTests.cs`, `UniqueActorAtomRepushTests.cs` (doc-only) |
| No regression: Data.Tests | `--filter "FullyQualifiedName~SpecimenOwnership\|FullyQualifiedName~UniqueActorStoreTests\|FullyQualifiedName~AiEmpireSpecimen"` | pass 58/58 | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |

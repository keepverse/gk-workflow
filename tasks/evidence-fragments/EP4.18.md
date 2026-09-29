# EP4.18 (increment) - trigger T5 lands; the side-wide wire stays open

**Row stays OPEN.** Its third acceptance bullet (T5) is landed, tested and wired to a real consumer; the
first (the side-wide pool on the lawn and the siege) and the R23 golden commit are not — the wire needs
paths this lane does not hold. Commit `@EP4.18` (partial) - session `empire-progression-4` - branch
`cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A Zomboss commander level-up broadcasts `AptitudesUpdated` with `empire = zomboss` (trigger T5) | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionPowerIndexReload"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` - `A_zomboss_commander_level_change_names_his_empire_and_not_the_players_reload` (scope `commander`, empire `zomboss`, and NO `power.index.reload`: that command re-reads the HUMAN's Theta, which his level-up does not change) | `gk-core/src/FusionRpg.Server/EventIngest.cs` |
| The human's own level-up keeps its correct signal | same | `Passed: 6` - `A_human_commander_level_change_still_sends_only_the_players_reload` (the human empire comes from `HumanEmpireOf`, never a literal id) | same |
| T1's additive field is unchanged | same | `Passed: 6` - the two EP4.15 cases still green | same |
| Scoped verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Server/EventIngest.cs','gk-core/tests/FusionRpg.Server.Tests/ProgressionPowerIndexReloadTests.cs' -Session empire-progression-4"` | `EXIT=0` - dal guard OK, server `Passed! - Failed: 0, Passed: 795, Skipped: 0, Total: 795` | - |

**NOT done (the row's remaining two thirds), with the cause read in code, not guessed:**

1. **The lawn half is denied to this lane and under-named by the row.** `SpeciesAllocationSource.cs:147-149`
   resolves the commander term through the injected `Func<long?, AptitudeAllocation> resolveCommanderAllocation`
   delegate, whose only production wiring is `gk-fusion/src/FusionRpg.Injector/CheatState.cs:197`
   (`resolveCommanderAllocation: _ => CommanderAllocation.Resolve(DummyStatContextForCommanderRead)` — the
   injector's ONE cached human pool). Making it empire-keyed therefore needs, at minimum:
   `SpeciesAllocationSource`'s delegate re-typed to take an `EmpireId`, `CheatState.cs` + `RpgClient.cs`
   caching a per-empire commander map, and a NEW server→injector transport field on
   `AptitudeEndpoints.ProjectState` (`/api/aptitudes/{playerId}`, whose `shares` is the human pool only).
   The row's Files line names none of those, and `gk-fusion/src/FusionRpg.Injector/**` is outside this lane's fence.
2. **The siege half needs a Theta provider that does not exist yet.** `RpgStore.WorldTurns.cs:510-513`
   resolves the commander term from the human commander scope key; the pool read needs that member's OWNER
   empire's Theta, and `DistrictAssaultResolver` (Core) has no Theta seam (its injected seams are
   `HubInputsFor`, `UnlockStateFor`, `MemberAway` — read this session). So `CommitWorldTurn` /
   `WorldTurnHubInputsForUnlocked` must take a new `Func<EmpireId, long>`-shaped provider wired from the
   Server (`IPowerIndexProvider.ActorIndexFor`, EP4.16) — a public store-API change plus its Server caller.
   Data cannot resolve Theta itself without a private `f(level)`, which `guard-power` forbids.
3. **The R23 golden commit (H1, last) cannot precede the wire:** it exists to list the pins that move when
   Zomboss's pool starts applying; with no seam reaching `CommanderPoolOf`, nothing moves, so the commit
   would be empty.

Requested of the manager: an erratum that either extends this lane's fence to
`gk-fusion/src/FusionRpg.Injector/**` + the aptitudes transport (and the store's `CommitWorldTurn` signature), or
splits the row into EP4.18a (transport + Injector cache) and EP4.18b (seams + T5 + golden). Recorded as a
blocker note in the ledger.

---

**Addendum (ep-4, 2026-09-21) — the blocker re-read on the orchestrator's instruction: the siege half
cannot land alone either.**

Both of this row's deps are DONE (EP4.17, SP6.1), so the blocker was re-derived from code rather than
re-stated. The remaining work is blocked by a DENIED PATH, and the siege half is not independently
landable because the AI-vs-human gate is SHARED:

- `ProgressionLayerSelector.Select` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/ProgressionLayerSelector.cs:51-61`)
  sets `CarriesCommander = empire == humanEmpire` — and that one field is consumed at FIVE sites, three of
  which read a HUMAN-scoped pool:
  - `SpeciesAllocationSource.cs:130-132` (lawn, a Bound unique) → `_resolveCommanderAllocation(ctx.PlayerId)`,
    the Injector's single cached pool, wired only in `gk-fusion/src/FusionRpg.Injector/CheatState.cs:197`;
  - `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:116-117` → `AptitudeEndpoints.ScopeKey(playerId)`;
  - `gk-core/src/FusionRpg.Server/WebMatchService.cs:608-609` → the human `commanderAllocation`.
- So flipping `CarriesCommander` true for Zomboss — the gate EP4.18's test 11 needs ("a siege member
  carries his pool", R4 mirrored) — hands a Zomboss-owned specimen the HUMAN's pool at those three sites:
  exactly the S1 wrong-empire leak `SpeciesAllocationSource.cs:141-144`'s own comment forbids. Flipping it
  therefore requires the Injector's empire-keyed delegate + cache + a transport field, and the two
  Server consumers, in the SAME change.

Denied paths that block this (outside the lane's fence): `gk-fusion/src/FusionRpg.Injector/CheatState.cs`,
`gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`,
`gk-core/src/FusionRpg.Server/WebMatchService.cs`. What IS in the fence and ready when the erratum lands:
`ProgressionLayerSelector.cs` (the gate), `RpgStore.WorldTurns.cs` (the siege seam),
`RpgStore.Aptitudes.cs` (`CommanderPoolOf`, EP4.17) and `ServerPowerIndexProvider.ActorIndexFor` (EP4.16)
— plus `gk-core/src/FusionRpg.Server/Program.cs`, which is where a store-level Θ delegate would be wired from the
composition root (`AddSingleton(new RpgStore(dataDir))` at `Program.cs:443`, the provider registration at
`:445-446`), so no edit to the denied `WorldEndpoints.cs` would be needed for the siege half.

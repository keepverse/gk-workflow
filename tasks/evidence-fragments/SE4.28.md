# SE4.28 — Spawn-command ownership fields; the injector reads, never infers

Spec: save-identity, "Injector ownership", decisions S4. `RpgStore.SpecimenOwnerEmpire(instanceId)`
(new) reads a specimen's own `(empire_id, controller)`; `UniqueActorService.DeployAsync` calls it in
the same call that decides the deploy and stamps `empireId`/`controller` onto the `pvz.spawn.extra`
payload beside `playerId`. `CheatState.SpecimenOwnerByPtr` becomes `ptr -> (EmpireId, EmpireController)`
(was `ptr -> long`); `RegisterSpecimenOwner`/`CheatActions.SpawnExtra*`/`CheatCommandRunner`'s two
`pvz.spawn.extra` handlers thread the two string fields through instead of `playerId`. Either field
missing or unparseable registers nothing — genuinely unknown, mechanical side decides, never `Ally`.
`MatchHost.CheckZombossDeployTrigger` finds Zomboss's own units by `CheatState.TryGetSpecimenEmpire(ptr)
== EmpireId.Zomboss` directly; the elimination rule ("not the human's, therefore Zomboss's", inverting
the oracle's Ally/Enemy answer) is deleted.

**Verification boundary named up front**: this machine has no MelonLoader game dir, so
`guard-injector-compile.ps1` SKIPs (confirmed by running it) and the Injector project cannot be built
locally in this session. Every Injector call site of the changed API (`RegisterSpecimenOwner`,
`TryGetSpecimenController`, `TryGetSpecimenEmpire`, `SpecimenOwnershipOracle`) was enumerated by grep
(exactly 2 in `CheatActions.cs`, 2 in `CheatCommandRunner.cs`, 1 in `MatchHost.cs` — all four files in
this commit) and reviewed line-by-line against the diff. This is the strongest check achievable here;
the orchestrator's live-probe gate is the real compile+behaviour proof.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `pvz.spawn.extra` carries `empireId`/`controller` from the specimen's own row | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~UniqueActor" --nologo` | pass 8/8 | `UniqueActorService.cs`, `RpgStore.SaveEmpires.cs` (`SpecimenOwnerEmpire`) |
| Real host proof: a Zomboss deploy's actual queued command carries the fields | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ZombossDeployEndpointsTests" --nologo` | pass 5/5 — `Deploy_sends_empireId_and_controller_on_the_spawn_command` drains the real `InjectorCommandInbox` and reads `empireId="zomboss"`, `controller="ai"` off the real queued payload (T24: real host, not a payload-builder unit test) | `ZombossDeployEndpointsTests.cs` |
| `SpecimenOwnerEmpire` resolves human/Zomboss/unknown correctly | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AiEmpireSpecimen" --nologo` | pass 5/5 | `AiEmpireSpecimenTests.cs` |
| A payload without the fields registers as unknown; elimination rule deleted | manual review (Injector unbuildable here) | `CheatState.RegisterSpecimenOwner` no-ops on missing/unparseable empireId/controller (unchanged null-safe guard shape); `MatchHost.cs`'s `oracle`/inversion switch removed entirely, replaced by a direct `== EmpireId.Zomboss` check | `CheatState.cs`, `Match/MatchHost.cs` |
| `guard-injector-compile.ps1` | same | SKIPPED — no MelonLoader game dir on this machine (confirmed, not silently ignored) | orchestrator/owner gate |
| Regression | `--filter "FullyQualifiedName~ZombossDeploy"` (Server) | pass 5/5 (superset above) | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py`; `.\scripts\guard-secondary-no-unity.ps1` | pass — all OK | — |

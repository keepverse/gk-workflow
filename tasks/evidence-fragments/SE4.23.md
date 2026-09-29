# SE4.23 — AI-empire specimens never touch a human-only table (fixes D6)

Spec: save-identity, "AI-empire specimens never touch a human-only table". `MintCreatureUnlocked` skips
`UpsertCodexUnlocked`/`AutoBindNewSpecimenUnlocked` when the stamped empire is not the save's human
empire (a save with no seeded empires keeps prior behaviour — never a new refusal for a legacy row).
New predicate `RpgStore.IsHumanEmpireSpecimen(instanceId)` (+ `...Unlocked`) scopes `TryBeginUniqueDeploy`'s
contract gate and `UniqueActorService.DeployAsync`'s `RecordExtraSpawnIntent` to human-empire specimens.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| AI-empire mint writes no codex/contract/contract-state row; human mint unchanged | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~AiEmpireSpecimen" --nologo` | pass 4/4 | `RpgStore.Creatures.cs`, `AiEmpireSpecimenTests.cs` (new) |
| Contract gate applies to human-empire specimens only | same | pass — `An_AI_empire_specimen_deploys_with_no_contract_row...` | `RpgStore.UniqueActors.cs` |
| D6: 13th Zomboss deploy in one save still deploys | same | pass — `D6_a_13th_Zomboss_deploy_in_one_save_still_deploys`; human `GetContractState(1)` stays null throughout | same |
| `DeployAsync` records no `ExtraSpawnFired` for a non-human empire | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ZombossDeployEndpointsTests" --nologo` | pass 4/4 — real endpoint call, `GetPvzActivityRollup(1).ExtraSpawnsFired` unchanged | `UniqueActorService.cs`, `ZombossDeployEndpointsTests.cs` (new test added) |
| No regression: existing contract/deploy/Zomboss/save-identity suites | `--filter "FullyQualifiedName~Contract\|~ZombossDeploy\|~SpecimenOwnership\|~SaveEmpires\|~AiEmpireSpecimen\|~SaveIdentity"` (Data); `~UniqueActorAtomRepushTests\|~ItemEquipEndpointsTests` (Server) | pass 99/99 (Data); pass 38/38 (Server) | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Cross-project `verify-change.ps1` | `-Paths` (6 files, Data+Server) | **orchestrator-owned** — `RpgStore.Creatures.cs`/`UniqueActorService.cs` have no focused mapping (fallback, whole-project, over the 600s agent cap — SE4.15/SE4.20/SE4.22 precedent). Verified instead via the five scoped filters above | ledger note |

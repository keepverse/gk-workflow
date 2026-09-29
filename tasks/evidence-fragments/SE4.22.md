# SE4.22 — Zomboss is an empire of the match's save

Spec: save-identity, "Zomboss stops being a player row", G5/X12. `MintForEmpire(EmpireRef, speciesId,
seed)` replaces `MintForZomboss`; `EnsureZombossPlayer`/`ZombossPlayerName` deleted (no code reference
remains, `grep` confirmed — the doc-only mentions in `SaveIdentity.cs`/`KillAttribution.cs` describe the
pre-SE4.22 shape). Blast radius: 4 more test files fixture Zomboss via the deleted API — replaced with a
new internal test seam `RpgStore.CreateUnseededPlayerForTest` (the unseeded-row shape `EnsureZombossPlayer`
used to build) plus the ordinary `MintCreature`/`MintForEmpire` primitives.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `MintForEmpire` mints under the empire's save, not a Zomboss row | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossDeploy\|FullyQualifiedName~SaveEmpiresStoreTests\|FullyQualifiedName~SpecimenOwnershipTests\|FullyQualifiedName~SaveIdentity" --nologo` | pass 44/44 | `RpgStore.ZombossDeploy.cs`, `RpgStore.Creatures.cs` (`MintCreatureForEmpire`) |
| `/api/zomboss/deploy` requires `matchKey`; unresolved match → 409 `match_unresolved`, mints nothing | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ZombossDeployEndpointsTests" --nologo` | pass 3/3 — `Missing_matchKey_is_refused...`, `A_matchKey_that_resolves_to_no_run_is_refused...` (roster count unchanged) | `ZombossDeployEndpoints.cs` (new host test) |
| Zomboss minted into save 1 is not save 2's | same two filters | pass — `ZombossDeployStoreTests.Zomboss_minted_into_save_1_is_not_save_2s` (data layer) + `ZombossDeployEndpointsTests.Zomboss_minted_into_save_1_is_not_save_2s` (HTTP layer) both assert distinct `player_id`/shared `empire_id=zomboss` | `gk-core/tests/FusionRpg.Data.Tests/ZombossDeployStoreTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/ZombossDeployEndpointsTests.cs` |
| Doc-only correction (KillAttribution.cs cited the deleted `EnsureZombossPlayer` as current) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~KillAttribution" --nologo` | pass 12/12 | `gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs` |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
| Cross-project `verify-change.ps1` | `-Paths` (11 files across Core/Data/Server) | **orchestrator-owned** — 3 of 11 paths (`KillAttribution.cs`, `RpgStore.Creatures.cs`, `ZombossDeployEndpoints.cs`) have no focused mapping and resolve to `core-fallback`/`data-fallback`/`server-fallback` (whole-project, Release build), which together exceed the agent's 600s cap (SE4.15/SE4.20 precedent). Verified instead via the four scoped filters above, which are the exact tests those fallbacks would also run | ledger note |

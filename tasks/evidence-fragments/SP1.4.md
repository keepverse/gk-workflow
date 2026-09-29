# SP1.4 — The web squad and the sheet ask the selector; three-path parity

Spec: `layer-source-selector`.

`WebMatchService.BuildSquad`'s commander allocation is still loaded ONCE per squad build (unchanged
perf shape — the comment beside it stays true), but the per-actor DECISION to apply it is now
selector-driven per specimen. `UniqueActorHubCompose.Build`'s aptitude compose is extracted into
`ResolveAptitudeAllocation` (internal, static) so it is directly comparable, by value, against the
other two paths without driving a full sheet render.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `WebMatchService.BuildSquad` and `UniqueActorHubCompose.Build` ask the selector; behaviour unchanged | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity\|FullyQualifiedName~Sheet\|FullyQualifiedName~EquippedHubParity\|FullyQualifiedName~ProjectStanding\|FullyQualifiedName~BuildSquadEquippedActions\|FullyQualifiedName~RolledItemEquipRuntime" --nologo` | pass 32/32 — no regression across every existing squad/sheet-adjacent test file | `WebMatchService.cs`, `UniqueActorHubCompose.cs` |
| For one specimen, the lawn (Bound ctx), the web squad and the sheet compose equal aptitude by scope and points, for a plant-side unique | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity" --nologo` | pass — `Plant_side_human_owned_unique_gets_equal_aptitude_across_all_three_paths` asserts `lawn.Entries == webSquad.Entries == sheet.Entries` (structural record equality, not per-field spot checks) | `ProgressionLayerParityTests.cs` (new) |
| ...and for a zombie-side human-owned unique | same | pass — `Zombie_side_human_owned_unique_gets_equal_aptitude_across_all_three_paths`; all three paths agree the specimen carries the human commander term (40 pts) despite fighting on the zombie side | — |
| Guards | `.\scripts\guard-actor-hub.ps1`; `.\scripts\guard-dal.ps1` | pass — both green | — |
| Build | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj --nologo` | Build succeeded, 0 errors | — |

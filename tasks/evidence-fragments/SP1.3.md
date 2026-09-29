# SP1.3 — The lawn source asks the selector; a Bound unique's empire is its owner's

Spec: `layer-source-selector`, rule 3 / C10.

**The spec's own anticipated re-type already happened.** The spec text reads the injector's
specimen-owner map "through one call site so `SE4.28` only retypes that site" — but `SE4.28` (this
same lane, save-identity wave 4) already landed: `CheatState.SpecimenOwnerByPtr` is already
`ConcurrentDictionary<string, (EmpireId, EmpireController)>`, with `TryGetSpecimenEmpire(ptr)` already
typed and ready to wire in directly — no interim re-type site needed.

`SpeciesAllocationSource.Resolve`'s Bound branch moved to the TOP of the method (before any
side-derived empire is computed) and now asks `ProgressionLayerSelector`, with the empire coming from
a new optional `resolveSpecimenOwnerEmpire` delegate (production: `CheatState.TryGetSpecimenEmpire`),
falling back to the human empire when unregistered — the same "unregistered reads as human" fallback
this class already uses elsewhere.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SpeciesAllocationSource.Resolve` asks the selector; its three value delegates stay | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesAllocationSource\|FullyQualifiedName~ProgressionLayerSelector" --nologo` | pass 24/24 | `SpeciesAllocationSource.cs` |
| For a Bound ctx, empire comes from the specimen-owner map, not `ctx.Side` | same | pass — `A_zombie_side_human_owned_unique_carries_the_human_commander_term_on_the_lawn`, `A_zombie_owned_unique_still_carries_no_commander_term_regardless_of_which_side_it_occupies` | — |
| A zombie-side, human-owned unique now carries the human commander term — the one named behaviour change | same | pass — the first test above is exactly this case, and it fails against the pre-fix code (side-derived: Zombie -> Zomboss -> Empty) | `SpeciesAllocationSourceTests.cs` |
| The three existing pins stay green unchanged | same | pass — `Bound_entity_resolves_commander_plus_unique_never_the_species_lookup`, `Bound_unique_sharing_a_species_id_with_a_general_never_inherits_empire_shares`, `A_lawn_zombie_never_inherits_the_players_commander_or_species_allocation` all still pass, none edited | — |
| Unregistered fallback (no owner map wired, or ptr not registered) reads as the human empire | same | pass — `An_unregistered_bound_specimen_falls_back_to_the_human_empire` | — |
| Production wiring: `CheatState.SpeciesAllocation` passes `resolveSpecimenOwnerEmpire: TryGetSpecimenEmpire` | manual review (Injector cannot be built here — `guard-injector-compile.ps1` SKIPs, no MelonLoader game dir; a direct `dotnet build gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj` also fails with an unrelated "Ambiguous project name" NuGet restore error on this machine, unrelated to this change) | `TryGetSpecimenEmpire`'s signature (`public static EmpireId? TryGetSpecimenEmpire(string ptr)`) matches `Func<string, Commanders.EmpireId?>` exactly by method-group conversion — the identical pattern the SAME constructor call already uses one line above for `resolveBoundInstanceId: ResolveBoundInstanceId`. `CheatState.cs`'s own `using FusionRpg.Core.Commanders;` resolves `EmpireId` without qualification. Added as a new named, optional, trailing constructor argument — no positional-argument risk to the five existing named arguments | `CheatState.cs` |
| Guards | `.\scripts\guard-actor-hub.ps1`; `.\scripts\guard-secondary-no-unity.ps1` | pass — both green | — |
| Build | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj --nologo` | Build succeeded, 0 errors | — |

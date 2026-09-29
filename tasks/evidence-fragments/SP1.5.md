# SP1.5 — The world-turn parity leg and the C1 shape guard

Spec: `layer-source-selector`.

Added `RpgStore.WorldTurnHubInputsFor` (public, locked — the same locked-wrapper/unlocked-worker shape
as `SpecimenOwnerEmpire`/`SpecimenOwnerEmpireUnlocked`) so the world-turn provider is callable from a
DIFFERENT test assembly than `FusionRpg.Data.Tests` (Server.Tests has no `InternalsVisibleTo` into
`FusionRpg.Data`, so the SP1.2-era `WorldTurnHubInputsForUnlocked` alone was not reachable from
`ProgressionLayerParityTests.cs`).

`ProgressionLayerSelectorGuardTests.cs`'s scan is a real per-member brace-matched scan (comments and
string/char literals stripped first), not a whole-file heuristic — a whole-file check would have
false-positived on files like `AptitudeEndpoints.cs`, which legitimately has both markers in
*different, unrelated* minimal-API route lambdas. One regex bug was found and fixed mid-task: the
member-signature pattern's `\s` alternative let a match start on a preceding BLANK line, corrupting
line-number bookkeeping on `SimEngine.cs` — caught by running the real scan against the whole `src/`
tree, not assumed from the probe tests alone (the probes exercise the pure detector function directly,
which never saw the bug; only the real file-walking path did).

**Found and fixed while validating (full `FusionRpg.Guard.Tests` run):**
`DebugScopeGuardTests.Guard_passes_green_on_the_real_current_DebugEndpoints_with_zero_exemptions` had a
stale hardcoded assertion expecting `/reforge-world` to still appear in `guard-debug-scope.py`'s
output — SP0.6 (already committed, `80559a75`) removed that route outright. Fixed in this commit:
the assertion is retired (`Assert.DoesNotContain` instead), not repointed, since the route genuinely no
longer exists. This was missed at SP0.6 time because only the PowerShell guard itself and the
`~PlayerSpecies` filter were run then, not this specific xUnit wrapper.

**Pre-existing, out of scope, NOT fixed:** `LegacyEquipTableRetirementGuardTests.No_production_file_outside_the_migration_names_the_retired_table`
fails because `SaveIdentity.cs` (save-identity's own migration, commit `a0e69bb60`, landed before this
anchor's work and before my current continuation) references `rpg_unique_equipment`, which a
DIFFERENT, older retirement effort (guard test committed `50fcdf87`, 2026-09-06 — weeks before
`SaveIdentity.cs`'s own commit) expects only `RpgStore.MigrateUniqueEquipmentToAssignments` to name.
This is a genuine save-identity-vs-legacy-equip-retirement conflict, unrelated to species-progression
and outside this anchor's queue; touching a migration file for an unrelated guard is out of scope here.
Recorded, not silently dropped.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The parity test gains its fourth path (world-turn); all four equal for plant-side and zombie-side owner cases | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ProgressionLayerParity" --nologo` | pass 2/2 — `Plant_side_human_owned_unique_gets_equal_aptitude_across_all_four_paths`, `Zombie_side_human_owned_unique_gets_equal_aptitude_across_all_four_paths` | `ProgressionLayerParityTests.cs`, `RpgStore.WorldTurns.cs` (`WorldTurnHubInputsFor`, new) |
| `ProgressionLayerSelectorGuardTests` fails when any `src/` member outside the selector both loads `AllocationScope.UniqueCreature` and calls `EffectiveSpeciesAllocation*`, proven by a probe | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ProgressionLayerSelectorGuard" --nologo` | pass 4/4 — the real scan finds zero unexempted violations across all of `src/`; `The_probe_fires_on_a_reintroduced_unconditional_pairing` proves the detector fires on the reconstructed map C1 shape; `The_sanctioned_shape_through_the_selector_does_not_fire` proves no false positive on the shape SP1.2 actually ships; `A_member_that_reads_only_one_scope_never_fires` | `ProgressionLayerSelectorGuardTests.cs` (new) |
| `guard-actor-hub.ps1` green | `.\scripts\guard-actor-hub.ps1` | pass | — |
| No regression: full `FusionRpg.Guard.Tests` | `dotnet test tests\FusionRpg.Guard.Tests --nologo` | pass 434/434 after the `DebugScopeGuardTests.cs` fix (was 431/434 before it; the third failure, `LegacyEquipTableRetirementGuardTests`, is pre-existing and out of scope — see above) | `DebugScopeGuardTests.cs` |
| Build | `dotnet build gk-core/src/FusionRpg.Data/FusionRpg.Data.csproj --nologo` | Build succeeded, 0 errors | — |

Wave 1 (`layer-source-selector`, SP1.1-SP1.6) is now closed. Checkpoint 1 itself spans waves 1-3 and
stays deferred (anchor 4's own scope note) until wave 3 (`species-layer-projector`) also lands.

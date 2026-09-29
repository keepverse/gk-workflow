# EP1.7 — Publish `species-build` (sequence order 1): the three unique respec keys; `UniqueRespec` view; move pins (H7)

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| `uniqueRespecBasePrice`/`Escalation`/`DecayDays` published at species working values | `python gk-core/tools/tuning/publish.py species-build --label "R18 unique creature respec price" --add-key ':uniqueRespecBasePrice=50' --add-key ':uniqueRespecEscalationPermille=500' --add-key ':uniqueRespecDecayDays=3'` | `published species-build (v1 -> v2, 3 change(s))` |
| A missing key is a load rejection naming it | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildTuning"` | pass (2/2) — `A_missing_uniqueRespecBasePrice_is_a_load_rejection_naming_the_key` |
| Every pin moves in this commit (H7) | `grep -rn "species-build\.v1\.json" src tools tests --include="*.cs"` | no real-code matches (2 comment mentions updated to `v{n}.json`); `Program.cs`, `CreatureBuildPlanGen`, `ProveHubCombat`, `SpeciesBuildPlannerTests.cs`, `_TempSeedSpecies` all read v2 |
| `CreatureBuildPlanGen --check` stays green (committed plan byte-identical) | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` | `--check: clean, 904 species match` |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths <every touched path>,gk-core/scripts/verification-boundaries.v1.json -Session empire-progression-20260920` | Core 14712/14713 (same named pre-existing `ExpeditionResolverTests` drift); Server 25/25, Data 8/8 confirmed separately |

## Notes

- `UniqueRespec` is a working-values copy of `SpeciesRespec` (same three numbers) — two independently
  tunable parameter sets, one formula, per spec: *"a specimen re-spec starts at the price a player
  already knows... not a balance decision."*
- Two more verification-boundary gaps found and fixed (own additive registry rows): `species-build-tuning`
  (`data/tuning/species-build.v{1,2}.json` had no owner at all) and `creature-build-plan-gen-tool`
  (`gk-forge/tools/CreatureBuildPlanGen/**` had none). Neither is this task's cause.
- Adding the three new required record fields broke 6 direct `new SpeciesBuildTuning(...)` test
  construction sites across three test projects (`SpeciesBuildPlannerTests.cs`, `RespecPolicyTests.cs`,
  `SpeciesRespecTests.cs`, `AptitudePresetEndpointsTests.cs`, `SpeciesAllocationEndpointsTests.cs`,
  `SpeciesBuildEndpointsTests.cs`); each now passes the same working values for the new keys.

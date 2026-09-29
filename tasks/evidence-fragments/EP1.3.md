# EP1.3 — Publish `aptitude-presets.v2` with `assignLadder.order`; loader contract; move pins (H7)

Spec: docs/architecture/empire-progression/spec-assign-ladder.md

| Criterion | Command | Result |
|---|---|---|
| `v2` published by `publish.py`, never hand-written | `python gk-core/tools/tuning/publish.py aptitude-presets --label "assign ladder order" --add-key ':assignLadder={"order":["active-preset","species-favour","posture","even"]}'` | `published aptitude-presets (v1 -> v2, 1 change(s))` |
| Loader rejects (naming the key) a non-`even`-terminated order, a duplicate, or an unknown id; terminal rung documented as structural | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudePresetTuning\|FullyQualifiedName~AssignLadder"` | pass (17/17) — `An_order_not_ending_on_even_is_a_load_rejection_naming_the_key`, `A_duplicate_rung_...`, `An_unknown_rung_id_...`, `A_missing_assignLadder_block_...`, `An_empty_order_...` |
| Every reader moves to v2 in this commit (H7) | `grep -rn "aptitude-presets\.v1\.json" src tools tests --include="*.cs"` | no matches — `Program.cs:268`, `gk-forge/tools/ProveHubCombat/Program.cs:125`, `gk-forge/tools/_TempSeedSpecies/Program.cs:164` (a 4th pin the task text didn't name but H7 covers), and both `AptitudePresetEndpointsTests.cs` sites all read v2 |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetTuning.cs,gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs,gk-core/data/tuning/aptitude-presets.v2.json,gk-core/src/FusionRpg.Server/Program.cs,gk-forge/tools/ProveHubCombat/Program.cs,gk-forge/tools/_TempSeedSpecies/Program.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs,gk-core/tests/FusionRpg.Data.Tests/AptitudePresetStoreTests.cs,tests/FusionRpg.Core.Tests/ClassSystem/AptitudePresetTuningTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session empire-progression-20260920` | Core 14672/14673, same named pre-existing `ExpeditionResolverTests` drift as EP1.1/EP1.2 (identical hash); Server 7/7, Data 5/5 |

## Notes

- Two verification-boundary gaps found and fixed (own registry rows, additive): `aptitude-presets-tuning`
  (`data/tuning/aptitude-presets.v{1,2}.json` had **no owner at all**, not even for v1) and
  `prove-hub-combat-tool` (`gk-forge/tools/ProveHubCombat/**`). Neither is this task's cause; both are gaps a
  publish touching those files would always have hit.
- `AptitudePresetTuning` gained a required `AssignLadder` field; the three test call sites that
  construct it by hand (not through the loader) now pass a minimal legal `AssignLadderTuning`
  (`["even"]`) via a small `MinimalAssignLadder()` helper.

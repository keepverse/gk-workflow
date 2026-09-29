# EP1.4 — `POST /api/aptitude-presets/suggest`: a draft only, and it never persists

Spec: docs/architecture/empire-progression/spec-assign-ladder.md

| Criterion | Command | Result |
|---|---|---|
| `rule` omitted walks the ladder; `rule` given runs only that rule | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"` | pass (12/12) — `Suggest_omitted_rule_walks_to_species_favour_when_no_active_preset`, `Suggest_walks_to_active_preset_first_when_one_is_bound`, `Suggest_with_rule_given_runs_only_that_rule` |
| Response is `{ruleId, rows, skipped, draftShares, leftover}`, `draftShares` from `AptitudePresetMaterialize` | same run | pass — all four suggest tests read `ruleId`/`rows`/`skipped`; `draftShares`/`leftover` come from `AptitudePresetMaterialize.Materialize(rows, budget)` |
| R23 commander context (no favour, no posture) returns `even` with 3 named skips | same run | pass — `Suggest_commander_scope_skips_favour_and_posture_by_name_R23_shape` |
| `rpg_aptitude_allocation` reads back byte-identical after any call | same run | pass — `Suggest_never_persists_allocation_stays_byte_identical` |
| `AssignLadder.TryOne` (the new single-rule entry point) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AssignLadder"` | pass (18/18) |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs,gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs,gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs,tests/FusionRpg.Core.Tests/ClassSystem/AssignLadderTests.cs,tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAutoAssignTests.cs -Session empire-progression-20260920` | Core 14693/14694 (same named pre-existing `ExpeditionResolverTests` drift, identical hash to EP1.1-1.3); the scoped Core-project failure stops the script before Server runs, so Server 12/12 was confirmed separately (above) |

## Notes

- `AssignLadder.TryOne` (new) is a second dispatch entry point beside `Suggest`'s own walk, reusing the
  same private `TryRung` switch — no duplicated rung logic. It additionally accepts the three raw
  `posture-force`/`-finesse`/`-bastion` ids directly (a button naming a posture itself), which the
  walk's own `order` vocabulary (`KnownRungs`) never allows.
- `BuildAssignContext`'s `FavourAllowed` is structural (`scope != "commander"`), matching Mode
  A/B/C from `aptitude-sheet-ideal.md` "Mode C — Commander": the commander pool has no species, so
  `species-favour` never applies there — this task derives it from the scope name, never a caller flag.
- The species' "primary" aptitude (for the `posture` rung) is the plan row's own highest-share entry,
  read back from `SpeciesBuildPlanCatalog.SharesFor` — the same fact `CreatureBuildPlanGen`'s
  `aptitudePrimary` names at generation time, not re-derived a second way.

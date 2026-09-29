# EP1.16 — `POST /api/aptitude-presets/suggested`: the `systemCopy` producer (W4)

Spec: docs/architecture/empire-progression/spec-default-build.md

| Criterion | Command | Result |
|---|---|---|
| The route writes one preset of kind `systemCopy` whose rows equal the current suggestion | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~AptitudePreset"` | pass (15/15) — `Suggested_writesASystemCopyPreset_whoseRowsEqualTheCurrentSuggestion` asserts the relation (12 rows, every value 83 or 84, exactly four at 84, sum 1000‰) never a literal, and confirms the row is really persisted via a follow-up GET |
| Named after the winning rung unless a `name` is given | same run — `Suggested_namesThePresetAfterTheWinningRung_unlessNameGiven` | pass |
| Past `softMaxPresets` it refuses exactly as a player preset does (test 7) | same run — `Suggested_refusesPastSoftMax_exactlyAsAPlayerPreset` | pass — same `SaveAptitudePreset` gate a player preset's own `SoftMax_create_past_cap_returns_conflict` test exercises, not a second one |
| Full Aptitude-filtered Server.Tests unaffected | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"` | pass (60/60 = 55 baseline + 5 new) |
| `guard-dal.ps1` | `.\scripts\guard-dal.ps1` | `DAL GUARD OK` |

## Notes

- `POST /suggested` always runs the ladder's own WALK (`AssignLadder.Suggest`), never an explicit
  `rule` — that distinction (walk vs. one named rung) is `/suggest`'s own job (EP1.4), and
  `/suggested`'s request shape (`playerId`, `scope`, `scopeKey?`, `name?`) has no `rule` field at all.
- No budget resolution needed: `AssignLadder.Suggest` only needs an `AssignContext` (species favour,
  posture, active-preset binding), never a budget — a preset's rows are permille, not points, so the
  specimen/commander's own budget plays no part in which rung wins or what its rows are.
- Writes through the SAME `RpgStore.SaveAptitudePreset` gate every player-created preset uses (no
  second write path), which is exactly what makes the soft-max refusal identical by construction
  rather than by parallel implementation.

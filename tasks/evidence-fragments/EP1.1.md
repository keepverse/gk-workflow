# EP1.1 — `species-favour` zero-fills a real 5-key plan row (W3)

Spec: docs/architecture/empire-progression/spec-assign-ladder.md

| Criterion | Command | Result |
|---|---|---|
| A real 5-key plan row (e.g. `abyssswordstar`) zero-fills and sums to 1000 | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AutoAssign"` | pass (12/12), incl. new `Fill_species_favour_zero_fills_a_real_five_key_plan_row` |
| Empty map / unknown id / non-normalised sum each refuse with own reason | same run | pass — `FillFromPermille_empty_favour_refuses_S7`, `Fill_species_favour_unknown_aptitude_id_refuses`, `Fill_species_favour_non_normalised_sum_refuses` |
| `autoAssign.favour.incomplete` no longer exists in `src/` | `grep -rn "favour.incomplete" src/` | no matches |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs,tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAutoAssignTests.cs -Session empire-progression-20260920` | Core 14650/14651. The one failure, `ExpeditionResolverTests.Tier_goldens_are_locked` (`hunt` tier hash), is **named pre-existing merge drift**: reproduced identically with EP1.1's two files fully reverted via a tagged stash (`ep1.1-baseline-check-a62e66ae`, applied+dropped after the check). No reference to `AptitudeAutoAssign`/`FillFromPermille` exists anywhere under `tests/FusionRpg.Core.Tests/Expeditions/`. Not owned by this session's paths fence; not caused by this change. |

## Notes

- Zero-fill and the three refusal reasons live in `AptitudeAutoAssign.FillFromPermille`; the
  unknown-id/sum checks run on the caller's own keys before zero-fill (zero-fill never changes the
  sum), so the reasons are `autoAssign.favour.{empty,unknownAptitude,notNormalised}` exactly as spec'd,
  never `AptitudePresetMaterialize`'s own `presets.*` reasons.

# EP1.2 — `AssignLadder.Suggest`: an ordered walk over the closed rules, ending on `even`

Spec: docs/architecture/empire-progression/spec-assign-ladder.md

| Criterion | Command | Result |
|---|---|---|
| First succeeding rung wins; every skipped rung + reason recorded; `posture` resolves to one of 3 ids | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~AssignLadder"` | pass (10/10) — `Posture_resolves_to_one_of_the_three_real_rule_ids_never_a_seventh` (theory, 3 cases) |
| Two tuning orders give two winners for one context (order is data) | same run | pass — `Ladder_order_is_data_two_orders_pick_two_different_winners` |
| R23 commander context (no preset/favour/posture, `FavourAllowed=false`) returns `even`, 3 named skips; adding an active preset makes it win | same run | pass — `R23_commander_context_returns_even_with_three_named_skips`, `Adding_an_active_preset_to_the_R23_context_makes_active_preset_win` |
| Totality (every absent-input combo returns a suggestion) | same run | pass — `Totality_every_absent_input_still_returns_even` |
| Rows are 12, permille, sum to 1000 for favour/even/posture | same run | pass — asserted in every rung test |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Stats/Aptitudes/AssignLadder.cs,tests/FusionRpg.Core.Tests/ClassSystem/AssignLadderTests.cs -Session empire-progression-20260920` | Core 14665/14666. Same named pre-existing `ExpeditionResolverTests.Tier_goldens_are_locked` drift as EP1.1's evidence (identical hash mismatch) — unaffected by this change. |

## Notes

- `AssignLadderTuning` (the walk order) is defined in `AssignLadder.cs`, not `AptitudePresetTuning.cs`
  — EP1.3 adds the JSON loader/load-contract onto this same record.
- `EvenRows()` mirrors the FE's `evenPermille.ts` `evenPermilleRows()` exactly (83‰ × 8, 84‰ × 4, first
  four by catalog order) so a future FE/BE parity check has one algorithm, not two.
- Re-merged `features/mega-merge` (9cf2e578) and `cmdc/lane-b` (f903dcb3) at this task boundary before
  building EP1.2 (see the ledger's `merge-reconcile` gate) — conflict resolution details there.

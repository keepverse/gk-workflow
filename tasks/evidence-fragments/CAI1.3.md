# CAI1.3 — ActionStage + ReserveFloorAffordability

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One pass, all gates at identity | `dotnet test --filter "FullyQualifiedName~ActionStageTests"` | 14 passed | `ActionStage.cs` |
| Gate order is UsabilityEvaluator's, not reimplemented | same run | `Gate_order_is_the_shipped_UsabilityEvaluator_order_not_reimplemented` (direct `Evaluate` call + source scan) | — |
| `runWasteGuards=false` skips the census entirely | same run | `RunWasteGuards_false_skips_the_census_entirely` (0 calls to either counting fake) | — |
| Each waste guard off-at-seed / switched-on | same run | 6 tests (Min/Kill/FightEnding × off + on) | — |
| Reserve floor: gate 3, never starves Basic | same run | `Reserve_floor_refuses_through_gate_3_and_never_starves_a_basic_attack` | `ReserveFloorAffordability.cs` |
| Poise floor = max(authored, expected reaction spend); identity at 0/0 | same run | `Poise_floor_is_the_max_of_the_authored_floor_and_the_expected_reaction_spend`, `Both_reaction_arguments_zero_leaves_every_floor_at_its_authored_value` | — |
| Action-layer purity (no dictionary-Keys enumeration) | `dotnet test --filter "FullyQualifiedName~ActionsPurityGuardTests"` | caught+fixed: `.Keys` on the floor map replaced with a walk over the closed `DerivedStatChannels.ResourceIds` (6 ids, deterministic order); now green | — |
| No regression | `dotnet test --filter "FullyQualifiedName~ActionStageTests\|FullyQualifiedName~ActionsPurityGuardTests\|FullyQualifiedName~Actions.Ai\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | 103 passed, 0 failed | — |
| `audit-overflow.py --targets A3` gains no finding | `python gk-core/scripts/audit-overflow.py --targets A3` | exit 0 | — |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | both | OK | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <3 files> -Session combat-ai-build-20260920` | exit 0; `FusionRpg.Core.Tests` (fallback): 14543 passed, 0 failed | — |

**Design note for CAI1.6/1.9 (module 2/3):** `ActionStage.TryPick` takes a `Func<CompiledAction,bool>? actionFilter` seam rather than module 2's `AiActionFilter` record directly — module 1 has no dependency on module 2, so the record cannot be referenced here yet. The first caller that owns a real `AiActionFilter` (module 3's `CoreIntentPolicy`) turns it into this predicate once per decision. `AiReserveFloor` IS declared here (in `ReserveFloorAffordability.cs`), matching the `ScoringWeights`/`SelectionPolicy` precedent, since module 1's own type needs it to compile; module 2 reuses it verbatim.

No re-bless: byte-identical, no golden moved.

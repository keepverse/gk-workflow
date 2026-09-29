# CAI1.2 — TargetStage: cap before any per-candidate work

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Cap-before-work == cap-after-work | `dotnet test --filter "FullyQualifiedName~TargetStageCapTests"` | 3 passed | `Cap_before_work_selects_the_same_candidate_as_cap_after_work` (40 enemies, cap 32, identical winner + breakdown) |
| Phase A filters run in view order | same run | passed | `Phase_A_filters_run_in_view_order` |
| Per-candidate work bounded to the cap | same run | passed | `Per_candidate_inputs_are_computed_only_for_the_capped_set` (counted, not timed) |
| Siege wired to `TargetStage`, byte-identical | `dotnet test --filter "FullyQualifiedName~SiegeAi\|FullyQualifiedName~CandidateScorerTests\|FullyQualifiedName~TargetStageCapTests\|FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | 80 passed, 0 failed | `SiegeAiIntentSourceTests`/`SiegeAiLiveWiringTests` unedited and green against the real `TargetStage`-wired production code |
| `audit-overflow.py --targets A3` gains no finding | `python gk-core/scripts/audit-overflow.py --targets A3` | exit 0 | — |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | both | OK | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <3 files> -Session combat-ai-build-20260920` | exit 0; `FusionRpg.Core.Tests` (fallback): 14529 passed, 0 failed | — |

No re-bless: byte-identical, no golden moved.

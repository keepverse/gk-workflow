# CAI1.6 — Vocabularies, records, parser, row selector (no file, no reader switch)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Six closed vocabularies, pinned member counts | `dotnet test --filter "FullyQualifiedName~CombatAiTuningTests"` | 18 passed | `AiVocabulary.cs`: TargetSelector 8, AiTier 2, AiPlace 4, AiRole 4, AiRowCondition 6, AiCensusCondition 5, PersonalityAxis 4 |
| Unknown vocabulary string throws naming value+key | same run | `An_unknown_selector_throws...`, `An_unknown_place_throws...` | `AiVocabularyParse.Enum<T>` |
| `router`/`*/default` required; last-row-conditional rejected | same run | `A_file_without_a_router_block_is_rejected`, `Missing_root_profile_is_rejected`, `A_profile_whose_last_row_is_conditional_is_rejected` | `CombatAiTuningLoader.Parse` |
| `AiTriggerBlock` has exactly three fields | manual diff | `CombatAiProfile.cs` (SwingsN, TicksT, PostCastLockL only) | — |
| Key resolution 4-step fallback, each step exercised | same run | `Key_resolution_falls_back_in_the_stated_order` | `CombatAiProfilePolicy.For` |
| `AiRowSelector.TryPick` is the only rank walk | `dotnet test --filter "FullyQualifiedName~AiRowSelectorTests"` | 6 passed: first-match-wins, no-target-is-false, census-read-once (counted), total-over-census, empty-list-returns-false | `AiRowSelector.cs` |
| `Core_reads_no_file` | same run | signature assertion, passed | — |
| No regression | `dotnet test --filter "FullyQualifiedName~Actions.Ai\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|FullyQualifiedName~ActionsPurityGuardTests"` | 135 passed, 0 failed | — |
| `audit-overflow.py --targets A3` / `audit-magic-numbers.py --summary` gain no row | both | clean (0 findings) | — |
| **Caught by an existing cross-program guard, fixed:** `RungSemanticsTests.MinRung_has_zero_hits_outside_the_unrelated_aura_ladder_constant` (action-skill-tiers `rung-semantics`, A-U1) | `dotnet test --filter "FullyQualifiedName~RungSemanticsTests"` | `AiActionFilter`'s `MinRung`/`MaxRung` fields (spec's own literal names) renamed to `RungAtLeast`/`RungAtMost` (matching this module's own `EnemiesAtLeast`/`EnemiesAtMost` census naming) — a different concept from the reserved rung-window term that guard protects; renamed rather than editing another program's guard | `CombatAiProfile.cs`, `CombatAiTuningLoader.cs` |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | both | OK | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <7 files> -Session combat-ai-build-20260920` | exit 0; `FusionRpg.Core.Tests` (fallback): 14589 passed, 0 failed | — |

Golden: byte-identical (nothing constructs `combat-ai.v1.json` yet; no reader switch in this task).
Deviation from spec's literal code sample, recorded: `AiActionFilter.MinRung`/`MaxRung` -> `RungAtLeast`/`RungAtMost`.

# CAI1.1 — move the scorer: `CandidateScorer` + selection

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `AiScoring` moved, no second copy | manual diff review | `CandidateScorer.cs` (new) holds the arithmetic; `SiegeAi.cs`'s `AiScoring` is a projection-only shim | gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs |
| Siege suites pass unedited | `dotnet test --filter "FullyQualifiedName~SiegeAi\|FullyQualifiedName~CandidateScorerTests"` | 77 passed, 0 failed | SiegeAiTests/SiegeAiIntentSourceTests/SiegeAiLiveWiringTests untouched |
| Byte-identical (no golden moved) | `dotnet test --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | 14 passed, 0 failed | — |
| `audit-overflow.py --targets A3` gains no finding | `python gk-core/scripts/audit-overflow.py --targets A3` | exit 0, no output (baseline via stash also 0) | `ScoringWeights` marked `// overflow-bounded:` (weight coefficients, not Theta-scaled) |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | `.\scripts\guard-actor-hub.ps1`; `.\scripts\guard-single-writer.ps1` | both OK | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <4 files> -Session combat-ai-build-20260920` | exit 0; ran full `FusionRpg.Core.Tests` (fallback mapping): 14526 passed, 0 failed | — |

No commit-worthy re-bless: this task moves no golden. `CAI1.5`/`CAI1.11` are the only wave-1 tasks permitted to move siege behaviour.

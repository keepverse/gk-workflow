# CAI1.5 — kill/value read the real `baseOverlayDamage` at `EffectiveRungOf`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SiegeAiIntentSource.cs:214`'s omission closed | manual diff | `baseOverlayDamage` computed from `heldActions[0]` via `ActionBaseDerivation.BasePowerMilli` at a new `effectiveRungOf` seam (defaults to the action's authored `Rung`; wired to `BattleRunState.EffectiveRungOf` in production) | — |
| No siege test edited, all pass | `dotnet test --filter "FullyQualifiedName~SiegeAi"` | 77 passed, 0 failed (incl. 2 new wiring tests) | one comment fix needed: `ActionTagPreference` literal in a new comment tripped `ActionTagPreferenceTests.TheSiegeAiReadsTheOneSortedListRatherThanReSorting`'s source-text scan — reworded, no behavior change |
| Battle/expedition unmoved (required) | `dotnet test --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | 14 passed, 0 failed | `RulesetVersion` stays 5 |
| Predicted-delta writeup | — | `docs/research/combat-ai/predicted-delta-kill-estimate.md` | no siege test's own outcome moved (both existing suites are either non-discriminating fixtures or don't exercise this code path); the fix is real and monotonic (`ExpectedDamage` non-decreasing in `baseOverlayDamage`), effect is honestly reported as unobserved in this corpus |
| `audit-overflow.py --targets A3` gains no finding | `python gk-core/scripts/audit-overflow.py --targets A3` | exit 0 | — |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | both | OK | — |
| `guard-doc-citations.ps1` | 4 pre-existing findings (`CombinationEvaluator.cs`, another lane) remain, none new | not this session's files | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <4 files> -Session combat-ai-build-20260920` | `FusionRpg.Core.Tests` (fallback): 14564/14565 passed; the one failure (`AtomBenchGuardTests.The_compiled_form_stays_inside_its_ns_per_atom_budget`, a wall-clock ns/atom benchmark in `Atoms/`, unrelated to `Actions/Ai`/`Battle/Siege`) reproduced as a machine-load flake — re-ran in isolation (`--filter FullyQualifiedName~AtomBenchGuardTests`), 3/3 passed | known flake class (concurrent-sessions-heavy-machine-load); not a regression from this task |

`RulesetVersion` stays 5. `EngineVersion` untouched.

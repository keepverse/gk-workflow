# CAI1.4 — RetargetLedger: anti-repeat moved and widened

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Moved out of `SiegeAiIntentSource.cs`, sole anti-repeat mechanism | manual diff | `Actions/Ai/RetargetLedger.cs` (new); `SiegeAiIntentSource.cs` keeps a one-line pointer comment | — |
| `Latency_zero_holds_nothing`, `Commitment_bonus_zero_is_byte_identical`, `Repeat_decay_1000_is_byte_identical`, `Ledger_state_is_battle_scoped` | `dotnet test --filter "FullyQualifiedName~RetargetLedgerTests"` | 6 passed (incl. 2 extra: commitment-applies-to-held-target, decay-recovers) | — |
| No regression (siege suites, Ai suite, goldens) | `dotnet test --filter "FullyQualifiedName~RetargetLedgerTests\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~Actions.Ai\|FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | 100 passed, 0 failed | `SiegeAiIntentSourceTests.cs` needed one `using FusionRpg.Core.Actions.Ai;` line (namespace-only, per spec-core-scorer.md S8's own sanctioned exception for this class of move) |
| `audit-overflow.py --targets A3` gains no finding | `python gk-core/scripts/audit-overflow.py --targets A3` | exit 0 | — |
| Action-layer purity | `dotnet test --filter "FullyQualifiedName~ActionsPurityGuardTests"` | 9 passed | — |
| `guard-actor-hub.ps1` / `guard-single-writer.ps1` | both | OK | — |
| verify-change boundary | `.\scripts\verify-change.ps1 -Paths <5 files> -Session combat-ai-build-20260920` | exit 0; `FusionRpg.Core.Tests` (fallback): 14549 passed, 0 failed | — |

`CommitmentBonusFor`/`RepeatDecayFor` are unwired in every module of this program (grepped: no other spec references either name) — pure API surface for a future caller, identity-safe at `bonus=0`/`halfLifeTicks<=0`. Added a symmetric `RecordActionChosen` write method (not named in the spec's 2-member snippet) so `RepeatDecayFor` has a real write half, mirroring `RecordRetarget`'s own discipline.

No re-bless: byte-identical, no golden moved.

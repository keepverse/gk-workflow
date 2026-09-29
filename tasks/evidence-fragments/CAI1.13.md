# CAI1.13 — `aggression-tier-map`: the throw becomes a saturating clamp

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `EffectiveTier` saturates instead of throwing; `aggressionRange <= 0` still throws; `saturatedBy` is signed | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AggressionTierMapTests"` | 8 passed, 0 failed (all rows below are from this run unless stated) | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AggressionTierMapTests.cs` |
| `Inside_the_range_is_unchanged` (byte-identity proof) | same run | passes — for `aggression ∈ [-2,2]`, tier `= -aggression` and `saturatedBy = 0`, identical to the pre-CAI1.13 body | — |
| `Outside_the_range_saturates_to_the_edge` | same run | passes — `+5 → tier -2`, `-5 → tier +2`, `int.MaxValue → -2`, `int.MinValue → +2` | — |
| `SaturatedBy_reports_the_signed_overshoot` | same run | passes — `+3 → +1`, `-4 → -2`, `+2 → 0`, `0 → 0` | — |
| `A_stacked_channel_plus_a_personality_offset_saturates_as_a_sum` | same run | passes — `+2 channel + +2 offset = +4 → tier -2, saturatedBy +2`; `-1 + -2 = -3 → tier +2, saturatedBy -1` | — |
| `Non_positive_range_still_throws` | same run | passes — `0` and `-1` throw `ArgumentOutOfRangeException`, for both overloads | — |
| `Tier_vocabulary_width_is_two_range_plus_one` | same run | passes — exactly `2*2+1 = 5` distinct tiers across `aggression ∈ [-10,10]` (pinned literal, reason in the test) | — |
| `Ai_aggression_keeps_composing_as_FlatSum_with_no_Cap` | same run | passes — `DerivedStatRegistry.CreateDefault()`'s `ai.aggression` def is `FlatSum`, `Cap is null` | `DerivedStatRegistry.cs` |
| §4: the trace line names a saturated choice, and stays silent otherwise | same run | passes — driven through the REAL `SiegeAiIntentSource` with a real `BattleTrace`: an `aggression: 3` candidate yields `saturatedBy=1(wave:taunt)`; an `aggression: 1` candidate adds nothing | `SiegeAiIntentSource.cs:341-355` |
| No siege test edited except the one asserting the removed throw | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CandidateScorerTests\|FullyQualifiedName~SiegeAiTests\|FullyQualifiedName~SiegeAiIntentSourceTests"` | 58 passed, 0 failed (66 with the 8 above) | `SiegeAiTests.Aggression_range_is_bounded_and_the_bound_is_authored` rewritten — the ONLY siege test edited, called out here |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Dominance\|Category=BalanceGuard\|FullyQualifiedName~ExpeditionResolver"` | **45 passed, 0 failed** — nothing re-blessed | — |
| `guard-doc-citations.ps1 -Strict` / `guard-battle-responsibility.py` / `guard-actor-hub.ps1` | `pwsh -NoProfile -File scripts/…` | all exit 0 | — |
| `audit-overflow.py` | `python gk-core/scripts/audit-overflow.py` | `A2=0 A3=0 A4=0 A5=0 A6=1`, total 1, **0 critical**. The single A6 is `CoreIntentPolicy.cs:282`'s pre-existing `unchecked((long)selfFacts.StatusMask)` (a bitfield widening cast, introduced by CAI1.9, not a magnitude path) — unchanged by this task; its line number moved with CAI1.11's earlier edit | — |
| `verify-change.ps1` | `-Paths <4 code/test paths> -Session combat-ai-build-20260920` | `core-fallback` + `core-tests-fallback` → `FusionRpg.Core.Tests`: **14857 passed, 4 failed**. All 4 are the same pre-existing `e0f1375d` Items/Atoms corpus failures named in CAI1.11/CAI1.12 (untracked `data/seed/items/socket-words/sockwords.json`; no local edit under `data/`), unrelated to these paths | — |

## Delegated out of this lane's fence (filed, not fixed)

- **The two `Stats/Derived/**` stale comments §3 requires correcting in the same commit could NOT be
  edited here**: `gk-core/src/FusionRpg.Core/Stats/**` is outside this lane's allowed-file fence. Filed with
  `file:line` and the cause read in `tasks/derived-stats-todo.md` → "Post-program corrections":
  `DerivedStatChannels.cs:573-575` and `DerivedStatRegistry.cs:293-295` both still claim
  `EffectiveTier` throws out of range. Everything else in the spec shipped.

## Doc re-anchoring (rules.md rule 3)

`CandidateScorer.EffectiveTier` moved (`:79-86` → `:91-118`) and `SiegeAiIntentSource.cs` gained the
reordered trace block, so `spec-aggression-tier-map.md`'s `file:line` citations into both were
re-anchored in this same commit, alongside its status line.

## What held

- `RulesetVersion` unmoved (5) — no policy behaviour changes: every production `AggressionOf` returns 0.
- Battle/expedition/dominance goldens unmoved and unblessed.
- `ai.aggression` still `FlatSum`, still `Cap is null` — the clamp is at the READ, never in composition.

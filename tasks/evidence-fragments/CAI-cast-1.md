# CAI-cast-1 — the plan refuses an intent whose envelope names a different action

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## The hazard

`LawnCastPlan.Build` charges `intent.ActionId` and arms `intent.Envelope`. `ActionIntent` is a public
readonly struct with public members, so a caller can pair one action's id with **another** action's
envelope — and the plan would then charge one action and cool a different one. That is a **silent
mis-charge**, not a visible refusal: the ledger says "paid", the cooldown says "a different action is
ready", and nothing anywhere reports the disagreement.

**Verified before declaring it, not assumed.** Every `ActionIntent` construction in `src/` was read:
`StubIntentSource` (two sites), `SiegeAiIntentSource` (two), `CoreIntentPolicy`, `InteractiveIntentSource`
(two) and `TimelineDispatch` all pair the id with the envelope it came from — and `CoreIntentPolicy`
looks the envelope up by the *same* id it returns (`FindAction(heldActions, actionId)`), so they agree by
construction. **So the guard breaks no shipped caller.** The one place a wrong row can arrive is a lookup
keyed by id, which is exactly what `commander-direct-orders`' owed order path will do: an order names an
`ActionId`, and the host must resolve that action's envelope.

## The change

`LawnCastPlan.Build` now refuses with `ArgumentException` naming **both** ids, before the pay step.
Throws rather than degrades, and says why in its comment: a programming error, not state. No tuning file,
no new vocabulary, nothing a balance pass would touch.

Test: `An_intent_whose_envelope_names_a_different_action_is_refused_loudly` — asserts the throw, that the
message contains both action ids, and that **nothing was charged or cooled on the way to the refusal**.

| Criterion | Command | Result |
|---|---|---|
| The cast-plan suite | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnCastPlan"` | **8 passed / 0 failed** (was 7) |
| Row Verify line | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Match/Ai/LawnCastPlan.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs','tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnDecisionLoopViewTests.cs') -Session combat-ai-4` | exit 0; 41 distinct projects, 0 with any failure |
| **Mutation**: the guard removed | planted, run, reverted | 1 red (the new test); 8/8 green after revert |
| Guards | `guard-actor-hub.ps1`; `audit-overflow.py --targets A3` | OK; exit 0, no finding |

Not claimed: this does not make the owed order path correct — it makes the *plan* refuse a mismatched
pair loudly when that path (or any other) gets it wrong.

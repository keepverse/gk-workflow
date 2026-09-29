# `CAI2.4` — the router's fourth arm: `AiDecisionOrigin.Order` had no producer

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found while looking for in-fence work; it is the last
unmet line of CAI2.4's acceptance, and the row asked for a *ruling* to unblock it.

## What the row said, and what is actually true

The row's text: *"**"all four policies behind the router record through the same sink"**, which needs
`IntentRouter.cs`/`CoreIntentPolicy.cs`/`ActionStage.cs`/`StubIntentSource.cs` — none of which this row's
Files list names. **RULING NEEDED:** re-scope CAI2.4 to that surface, or land the router sink as its own
task."*

Measured, the router sink is **not** missing:

```
IntentRouter.cs:68   policy   = new AiDecisionRecordingSource(policy,   sink, AiDecisionOrigin.Policy);
IntentRouter.cs:69   fallback = new AiDecisionRecordingSource(fallback, sink, AiDecisionOrigin.Policy);
IntentRouter.cs:70   steered  = new AiDecisionRecordingSource(steered,  sink, AiDecisionOrigin.Steered);
```

So "every arm records" holds **by construction at the router's one construction entry point** — the
property `AiDecisionRecordingSource`'s own class doc claims, and the reason it decorates rather than adding
sink parameters to three policy constructors. **No ruling was needed.**

## The gap that WAS real

`AiDecisionOrigin.Order` had **no producer anywhere in `src/`**:

```
grep -rn "AiDecisionOrigin.Order" src/ tests/ --include=*.cs    ->  no matches
```

The order step sits in `IntentRouter.Resolve` and returns **before** any wrapped source runs, so an
order-driven decision produced **no record at all** — and the closed three-member vocabulary D4 defines
(policy / order / steered) had a member nothing could emit. That is the field CAI4.9's criterion 7 needs
the inspector to **read** rather than infer, and `IntentRouterTests` had no `sink` reference at all, so the
property was pinned by nothing either way.

## What landed

- `IntentRouter` gains a trailing-optional `IAiDecisionSink? sink = null` (ctor **and** `Compose` forwards
  it), so every existing construction keeps compiling and a null sink changes nothing.
- `Resolve`'s order step records through that sink with `AiDecisionOrigin.Order` when the forced-intent
  hook answers.
- `AiDecisionRecordingSource.RecordRouterDecision(sink, actorKey, nowTick, origin, intent)` is the ONE
  place a router-level record is shaped, used by both the decorator and the order arm — so the four arms
  cannot drift apart, and the null-sink early return keeps "off costs nothing" true.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One case per arm, each asserting its own origin | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouterTests\|FullyQualifiedName~DecisionInspectorTests" --nologo --verbosity quiet` | **32 passed / 0 failed** (24 `IntentRouterTests`, 5 of them new) | `gk-core/tests/FusionRpg.Core.Tests/Actions/IntentRouterTests.cs` |
| Each case is load-bearing (four planted violations) | same command with (a) the `RecordRouterDecision(..., AiDecisionOrigin.Order, ...)` line deleted, (b) the policy wrap deleted, (c) the fallback wrap deleted, (d) the steered wrap deleted | **4 failed** — exactly `The_order_arm_records_with_the_Order_origin`, `The_policy_arm_records_with_the_Policy_origin`, `The_fallback_arm_records_through_the_same_sink_when_the_policy_returns_none`, `The_steered_arm_records_with_the_Steered_origin`; reverted green | — |
| The whole Core project | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **9718 passed / 0 failed** (was 9713) | — |
| No golden moved | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --nologo --verbosity quiet` | **210 passed / 0 failed** | — |
| The lawn/match surface is unmoved | `dotnet test gk-core/tests/FusionRpg.Core.Match.Tests --nologo --verbosity quiet` | **182 passed / 0 failed** | — |
| The program's guards | `guard-actor-hub`, `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-battle-responsibility`, `guard-secondary-no-unity` | all **exit 0** | — |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** | — |

**The fallback case pins something worth naming:** the chain records **every arm it consults**, not only
the winner — so a fallback answer appears as TWO records (the policy's `None`, then the fallback's), and an
inspector can explain "the policy had nothing, the fallback answered" rather than seeing only the outcome.
That is the decorator's own stated rule ("A None intent still records … a missing record would be
indistinguishable from the router never running"), now asserted.

## NOT proved

- **No live probe and no siege/delve run.** The property is asserted at the router, which is the one
  construction entry point every caller uses; whether a production composition passes a sink to it was not
  re-measured here.
- **`Round` stays 0 and `Candidates`/`TopThree` stay empty on an order record** — the router does not know
  the round or the per-candidate detail, which the decorator's own doc states. So an order record is
  identifiable by its origin but is not a substitute for the policy's own candidate-level record.

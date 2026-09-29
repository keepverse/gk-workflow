# CAI4.9 row 14 — the forced-intent hook, landed without moving an interface

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's owed item (2) was recorded — by me, last
segment — as needing *"a forced-intent hook on `IIntentSource` … seven implementations would move"*.
Re-read against the code, that was wrong: the hook belongs on the ROUTER, which already owns the order
seam (`IOrderQueue? orders`, `orderTimeoutTicks`, `ConsumeExpiredOrder`), so nothing outside
`IntentRouter.cs` had to change.

## The design, and why the gates stay where they are

`IntentRouter` gains a trailing-optional `Func<DirectOrder, ActionIntent?>? forcedIntent` on both the
constructor and `Compose`. `Resolve` consults it for a LIVE order **before** the steered step, because the
chain's own pinned order is *"order-injected, then steered, then policy, then default"*
(`The_fallback_chain_is_order_injected_then_steered_then_policy_then_default`).

**The hook owns the gates, and that is the point.** The router never runs `UsabilityEvaluator` and cannot
answer "did this order clear the gates" — so it does not pretend to: it takes the hook's answer when there
is one and falls through when there is not. That is the spec's *"a top-rank candidate, not a bypass"*
expressed structurally rather than argued. A `null` hook leaves every caller byte-identical to today's
inert state, where a live order is peeked and falls through because nothing can fire it.

| Criterion | Command | Result |
|---|---|---|
| "An order that clears the gates wins over the profile's own row 0" | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouterTests"` | **19 passed / 0 failed** (was 14) — the returned intent is the ORDER's action and target, not the policy's |
| "The identical order that fails a gate does not fire and the policy's own choice is returned" | same run | **19 / 0** — the hook returns `null` and `act.policy` is returned |
| The identity: no hook changes nothing | same run | **19 / 0** — `Without_a_hook_a_live_order_still_falls_through_to_the_policy` |
| An expired order is never offered to the hook | same run | **19 / 0** — counted, `hookCalls == 0` at exactly the timeout |
| The order step really is first | same run | **19 / 0** — with a steered key set for the same actor, the order wins and the steered source's `Seen` stays empty |
| Golden and the program's guard | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`; `guard-actor-hub.ps1` | **5 / 0**; guard **exit 0** |

## What this does not close

The row still owes its **injector host** (nothing offers an order yet — `LawnOrderQueue` is Core and its
producer is the FE -> Server -> Injector path) and the two `web/**` files, which are outside this lane's
fence. What changed is that the ROUTER side is now complete and tested, so the remaining work is transport,
not plumbing.

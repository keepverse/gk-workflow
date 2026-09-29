# CAI1.10 — The router, cause A: one chain, two routers deleted

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `IntentRouter` exists; `RaidIntentSource.cs` + `SiegeIntentSource` deleted; every former caller constructs the router | manual diff | `RaidIntentSource.cs` deleted (whole file); `SiegeIntentSource` class deleted from `SiegeAi.cs` (219→115→75 lines across CAI1.1/1.8/1.10); `DelveBattleSession.cs` now calls `IntentRouter.Compose`; `BasicAttack.cs`/`TimelineDispatch.cs` construct one per decision | — |
| `IntentRouter.Compose` is the only construction entry point | `dotnet test --filter "FullyQualifiedName~IntentRouterTests"` | 14 passed (incl. `Compose_invokes_steeredSourceFor_exactly_once_with_the_policy_it_was_given`, `Compose_with_a_null_fallback_returns_None_rather_than_inventing_a_stub`, `A_router_built_through_Compose_and_one_built_through_the_constructor_resolve_identically`) | `IntentRouterTests.cs` |
| The fallback chain is order→steered→policy→fallback, pinned | same run | `The_fallback_chain_is_order_injected_then_steered_then_policy_then_default` passes | — |
| Byte-identity harness | same run | `Constructing_a_router_with_no_decorators_and_no_queue_reproduces_the_shipped_chain` passes | — |
| `RetargetFor` | same run | `RetargetFor_keeps_the_committed_action_and_changes_only_the_target`, `RetargetFor_returns_null_when_nothing_resolves` pass | — |
| No policy consulted for a reaction | same run | `The_router_consults_no_policy_for_a_reaction` passes (structural source-scan of `TimelineDispatch.cs`'s own reaction-lane block — see Deviations) | — |
| No second `?? new StubIntentSource(` | `grep -rn "?? new StubIntentSource(" src/` | zero matches | — |
| Golden: byte-identical | `dotnet test --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | **14 passed, 0 failed** | quoted below |
| Broader regression | `dotnet test --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~SiegeAiLiveWiring\|FullyQualifiedName~Raid\|FullyQualifiedName~ActionSelection\|FullyQualifiedName~IntentSource"` | 192 passed, 0 failed | — |
| `Category=BalanceGuard` | `dotnet test --filter "Category=BalanceGuard"` | 25 passed, 0 failed | — |
| `guard-battle-responsibility.py` | — | OK (19 mechanisms, 1548 files scanned) | — |
| `guard-actor-hub.ps1` | — | OK | — |
| `guard-doc-citations.ps1 -Strict` | — | exit 0, 0 HIGH (see Deviations — this task's own deletion of `SiegeIntentSource` shrank `SiegeAi.cs` from 115 to 75 lines, breaking 23 MORE citations across 9 docs; all re-anchored in this same commit) | — |
| Full Core.Tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests` | 14792 passed, 0 failed | — |
| Full Server.Tests | `dotnet test gk-core/tests/FusionRpg.Server.Tests` | 706 passed, 0 failed | — |
| Full Data.Tests | `dotnet test gk-core/tests/FusionRpg.Data.Tests` | 1743 passed, 0 failed | — |
| Delve E2E | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~Delve"` | 2 passed, 0 failed | — |
| `audit-overflow.py --targets A3` | — | no new finding | — |

**Golden output quoted verbatim** (`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~ExpeditionResolver"`):
```
Passed!  - Failed:     0, Passed:    14, Skipped:     0, Total:    14, Duration: 237 ms - FusionRpg.Core.Tests.dll (net8.0)
```

## Deviations from the spec's own illustrative snippet, each stated in code

1. **The fallback chain resolves the four steps as SELECT-by-presence for order/steered, then a
   CASCADE-on-`None` between `policy` and `fallback`** — not documented as two different rules
   anywhere in one place in the spec, but forced by two hard constraints together: (a) `policy` is
   MANDATORY (never null) in `Compose`'s own signature, so a pure select-by-presence model could never
   reach `fallback`; (b) `RaidIntentSourceTests`' own ported contract
   (`A_steered_actor_that_declares_nothing_is_never_handed_to_the_policy`) proves NO cascade at the
   steered/policy boundary. Both are satisfied by: order (structural) → steered (select, no cascade) →
   policy (tried) → fallback (only on policy's own `None`). `Compose_with_a_null_fallback_returns_None_
   rather_than_inventing_a_stub` (CAI1.10's OWN acceptance line) is the test that requires this cascade
   to be real, not deferred.
2. **`policy` is never actually nullable at the two call sites** — `BasicAttack.cs`/`TimelineDispatch.cs`
   supply `state.DefaultAiIntentSource ?? NoneIntentSource.Instance` (a new, trivial always-`None`
   singleton, `IntentSource.cs`, matching `NoStanceHeld`/`AlwaysAffordable`'s own "no real
   implementation yet" precedent) rather than leaving `policy` null, which `IntentRouter`'s own
   constructor refuses. Byte-identical: for every non-siege battle (`DefaultAiIntentSource` is null
   today), `policy` is the inert source, which ALWAYS returns `None`, cascading to `fallback` (the
   SAME stub literal every call already built) every single time — matching today's `null ?? stub`
   exactly. For siege, `SiegeAiIntentSource.TryDeclare` already reproduces the stub's own no-target/
   no-action/movement/pass shape internally (traced by hand: both walk the same held-action list, the
   same gates, the same movement-tag fallback), so it returns `None` in exactly the cases the stub
   would too — the policy→fallback cascade is therefore inert on every reachable production path.
   Confirmed, not assumed: `SiegeAiLiveWiringTests` (the one test that pairs `aiTuning` with a
   dispatch profile, per the spec's own §5 note) and `BattleGoldenTests`/`ExpeditionResolverTests` all
   pass unedited.
3. **`The_router_consults_no_policy_for_a_reaction` is a structural source-scan, not a live multi-round
   battle.** `IntentRouter` itself has no reaction-handling code to unit-test directly — reactions are
   entirely `TimelineDispatch.cs`'s own domain (`ReactionCounter.TryCounter`, consulting
   `PoiseLedger`/`ReactionLanePolicy` only). The test reads the real `TimelineDispatch.cs` source, finds
   the reaction-lane block (`reactionLane.TryEnter(...)` through `reactionLane.Exit(...)`), and asserts
   it names no `IIntentSource`/`TryDeclare`/`Reselect` symbol — a stronger, cheaper proof than a live
   battle for the same claim (a live battle would only sample ONE run; the source scan proves the
   property for every possible run).
4. **`RetargetFor`'s `actionId`/`deadTargetKey` parameters are unused this commit** — matching
   `TimelineDispatch.Reselect`'s own current body, which never reads its own `deadTargetKey` parameter
   either. A real per-action-id target stage is module 1's `CoreIntentPolicy.RetargetFor` (CAI1.9),
   reached once a wiring module (13) supplies it as `policy`.
5. **`IOrderQueue`/`DirectOrder` ship as structural types only** — the router checks
   `_orders.TryPeek`/expires a stale order (the one piece of order handling actually implemented), but
   a LIVE order cannot yet "fire as a rank-0 candidate" because no `IIntentSource` implementation
   exposes a hook to accept a forced (action, target) pair. Named as `commander-direct-orders`'
   (module 20) own remaining work in the code's own doc comment, not silently worked around. Inert
   today: every caller this module ships passes `orders: null`.
6. **`Battle/BattleRunState.cs` was not touched**, though the todo's own Files list named it —
   `state.DefaultAiIntentSource`'s own construction (siege's `SiegeAiIntentSource`) was already
   correct and untouched; only the two CALL SITES that CONSUME it (`BasicAttack.cs`,
   `TimelineDispatch.cs`) needed rewiring.

## The doc-citation ripple this task's own deletion caused

Deleting `SiegeIntentSource` shrank `SiegeAi.cs` from 115 to 75 lines, which broke 23 MORE citations
(beyond the 27 CAI1.8/CAI1.1 already re-anchored) across 9 documents: `combat-ai-ideal.md` (2),
`spec-aggression-tier-map.md` (4), `spec-auto-policy-switch.md` (1), `spec-core-scorer.md` (8),
`spec-decision-inspector.md` (1), `spec-decision-perf.md` (2), `spec-intent-router.md` (2, in
paragraphs this same task's own earlier edit had touched), `spec-profile-schema.md` (1), and
`empire-progression-ideal.md` (2, outside combat-ai's own doc tree entirely — describes the additive
scorer as prior art for the empire-progression AI). Every one re-anchored in this same commit, per H1's
own re-bless-order discipline applied to citations: `guard-doc-citations.ps1 -Strict` exit 0 (24738
citations checked, 0 HIGH). For `SiegeIntentSource`'s own content (now deleted with no successor
address, only a ported test contract), the citation states the class is gone rather than inventing a
new line number for it.

## Not done (named, not silently deferred)

`commander-direct-orders` (module 20) still owns: a real `IOrderQueue` producer, and the plumbing that
lets a live order actually fire through a gate check. `intent-router`'s own trait decorators
(`bloodthirsty`/`loyal` reaching every policy, not only the stub) are CAI1.11's "cause B" — a real,
siege-visible behaviour change, deliberately kept out of this byte-identical commit per the map's
one-cause-per-commit rule.

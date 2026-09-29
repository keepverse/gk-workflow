> **Path deviation, recorded deliberately.** The todo's own Files list names
> `docs/research/combat-ai/predicted-delta-router-cause-b.md`. `docs/research/**` is outside this
> session's allowed paths (the runner refuses any changed file outside them), so the note lives in the
> spec tree instead. Same content, same commit, same author; nothing else changed.

# Predicted delta: CAI1.11, `intent-router` cause B (trait decorators on every policy)

**Program:** [combat-ai](../combat-ai-map.md) · **Task:** CAI1.11 (`intent-router`, spec
[spec-intent-router.md](spec-intent-router.md) §2, §5 cause B) · **Cause:** one — `bloodthirsty`'s
pre-decision view decoration and `loyal`'s post-decision redirect now reach every policy, not only the
`StubIntentSource` fallback (audit M1), and the reselect site shares the one chain (audit M5).
**`RulesetVersion` unmoved (stays 5).**

## What changed

| Seam | Before | After |
|---|---|---|
| `bloodthirsty` (pre-decision view) | `BasicAttack.cs` built `BloodthirstyViewFor` per decision and handed it **only** to `new StubIntentSource(view, …)` | `BattleRunState.TraitView` (a `TraitAwareBattleView` over the run state, built once) is what `SiegeAiIntentSource` — and any policy constructed with it — binds. `bloodthirsty` is an `ITraitDecorator` whose `Decorate` reorders `IBattleView.LiveActorKeys` **for the deciding actor**, reached through the new viewer-relative `IBattleView.LiveActorKeysFor`. The stub keeps its own per-decision view, unchanged. |
| `loyal` (post-decision redirect) | an inline `FindAdjacentWithTrait(state.Actors, target, "loyal")` + `IsCcLocked` block in `DeclareBasicAttack` | one `ITraitDecorator.EffectiveTargetOf` (`LoyalTargetRedirect`, same body including its CC gate), applied **once** by `IntentRouter.TryDeclare` on the engine side and **once** by `CoreIntentPolicy`'s candidate build on the scorer side (its `loyalRedirect` seam, CAI1.9, now reads the redirected target's facts for `kill`/`lowHp`). `IntentRouter.RetargetFor` deliberately does **not** redirect — `Reselect` never did. |
| The chain | `BasicAttack.cs` `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(…)`; `TimelineDispatch.Reselect` the same minus `state.DefaultAiIntentSource` (M5) | both resolve through `IntentRouter.TryDeclare`'s one method (CAI1.10 closed M5; CAI1.11 pins it with a test). |

## Why behaviour can move, and where

`bloodthirsty` reorders `LiveActorKeys`; a scoring policy scores every candidate and tie-breaks on
ordinal actor key, so the reorder changes its answer **only where `maxCandidatesScored` truncation
bites** (`combat-ai.v1.json` `siege/default` → 32). It cannot change any decision with fewer than 33
eligible candidates, which is every shipped battle fixture. That is the honest prediction: **the
goldens do not move, and siege decisions with a capped candidate set do.**

`loyal`'s redirect body is byte-for-byte the pre-existing one and its one engine-side call site is the
same decision path, so the engine half is inert. The scorer half (feeding `kill`/`lowHp` the redirected
target's facts) changes a *scoring input*, and `CoreIntentPolicy` has **no production constructor
caller** yet (`delve-automated-wiring`, module 13, is its first — CAI1.9's own recorded posture), so it
cannot move a shipped battle.

## Measured, not assumed

```
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"
Passed!  - Failed:     0, Passed:    36, Skipped:     0, Total:    36
```

**Moved tests: none.** No golden and no `BalanceGuard` row moved, so no test was re-blessed. That is the
predicted outcome, and the reason is measurable rather than argued: every shipped siege fixture has
fewer eligible candidates than the 32-cap.

The move was then **demonstrated** rather than claimed, on the real host
(`gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/SiegeAiLiveWiringTests.cs`,
`With_aiTuning_a_cap_dropped_candidate_is_scored_once_a_bloodthirsty_actor_carries_the_trait`): a
33-enemy board places a 1-HP enemy LAST in `setup.Wave`, i.e. exactly the entry the 32-cap drops.
`BattleEngine.Resolve` with `aiTuning` (so the real `SiegeAiIntentSource` answers):

- control, no trait → `wave:low` is never in the scored set and stays at 1 HP;
- `TraitIds = ["bloodthirsty"]` → the same candidate is moved inside the cap and dies.

Both assertions pass, so the decorator genuinely reaches the scored policy through production wiring —
not only the stub, which is the whole of audit M1. A second, parallel delta this commit does **not**
claim: the stub path (no `aiTuning`) already ordered by `bloodthirsty` before this change.

## What held

- `RulesetVersion` unmoved (5) — `decisions.md`'s bump trigger is module 14's cause, not this one.
- Battle and expedition goldens unmoved and unblessed.
- No existing test edited; the three new tests are additions.
- `EngineVersion` untouched — every change here is on the deciding side.

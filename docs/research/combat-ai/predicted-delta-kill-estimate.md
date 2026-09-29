# Predicted delta: CAI1.5, the `baseOverlayDamage` kill/value estimate fix

**Program:** [combat-ai](../../architecture/combat-ai-map.md) · **Task:** CAI1.5 (`core-scorer`, spec
[spec-core-scorer.md](../../architecture/combat-ai/spec-core-scorer.md) §8 commit 2) · **Cause:** one —
`SiegeAiIntentSource`'s kill/value estimate now reads a real `baseOverlayDamage` instead of a hardcoded
`0.0`. **`RulesetVersion` unmoved (stays 5).**

## What changed

`SiegeAiIntentSource.cs:214`'s own omission — `SiegeExpectedDamage.IsKillingBlow(selfDerived,
targetDerived, targetCurrentHp)` called with no `baseOverlayDamage`, defaulting to `0.0` — no longer
exists. The candidate builder now computes:

```
theta            = selfDerived.Get(ProgressionPower)
preferred        = heldActions[0]                              // the actor's most-preferred held action
effectiveRung    = effectiveRungOf(actorKey, preferred.ActionId) ?? preferred.Rung
basePowerMilli   = ActionBaseDerivation.BasePowerMilli(preferred.Kind, preferred.ActionId, effectiveRung, RungTable, ActionBaseTuning)
baseOverlayDamage = ActionBaseMath.BasePerHit(basePowerMilli, BattleRuleset.PowerValue(theta))
```

and passes that into `IsKillingBlow`. Target selection runs before action selection (the actor has not
yet swung anything), so there is no "the swung action" to read — `heldActions[0]` (already frozen in the
actor's own held-action preference order, offensive first) is the honest stand-in for "what this actor
will most likely use", matching what step 3 actually picks in the common case. `SiegeAiIntentSource`
gained one new optional constructor parameter, `effectiveRungOf: Func<string,string,int>?`, wired to
`BattleRunState.EffectiveRungOf` in production (the same instance resolver `CostLedger`'s own `rungOf`
already reads) and defaulting to the held action's own authored `Rung` for any caller that supplies
nothing (every existing test).

## Why the mitigated fraction changes, not just the raw number

`SiegeExpectedDamage.ExpectedDamage`'s divisive-mitigation branch reads `baseOverlayDamage` in BOTH the
`offense` term and the `ladderScale` term:

```
offense     = baseOverlayDamage + power
ladderScale = baseOverlayDamage + power
damage      = DivisiveMitigation(offense, effectiveDefense, K, ladderScale)
```

Raising `baseOverlayDamage` from `0.0` to a real positive value raises both the numerator (`offense`)
and the ladder scale the mitigation curve compares defense against — the file's own doc comment states
this plainly: *"omitting it does not merely shift the estimate, it changes the mitigated fraction."*
The direction is unambiguous: `ExpectedDamage` is monotonically non-decreasing in `baseOverlayDamage`,
so **`IsKillingBlow` can only flip `false -> true` from this change, never `true -> false`.** Before this
fix, expected damage was systematically UNDER-estimated, so the kill term under-counted how often a hit
would actually finish a target — siege under-valued near-kill candidates relative to their real lethality.

## Measured effect against this program's own test corpus

`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi"`: **55 passed, 0 failed,
no test edited.** `dotnet test --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~ExpeditionResolver"`:
**14 passed, 0 failed** — required, and unmoved (`RulesetVersion` stays 5; a battle/expedition hash
moving here would be a stop-and-report, not this cause).

No siege test's own asserted outcome moved. Two structural reasons, both checked directly rather than
assumed:

1. **`SiegeAiTests.cs`'s scenarios never exercise this code path at all.** Its `Candidate(...)` helper
   hand-constructs `AiCandidate`/`TargetCandidate` values directly (`isKillingBlow: true`/`false`
   supplied by the test), scoring them through `CandidateScorer`/`AiScoring` in isolation — it never
   calls `SiegeAiIntentSource.ChooseTarget`'s real candidate builder, so the fix (which lives inside
   that builder) cannot move anything there by construction.
2. **`SiegeAiIntentSourceTests`/`SiegeAiLiveWiringTests`'s live scenarios are decisive at either
   estimate.** `SiegeAiLiveWiringTests.With_aiTuning_SiegeAiIntentSource_attacks_the_scored_better_enemy_instead`
   uses a 1-HP target (`FarButLethal`) — `ExpectedDamage(...) >= 1` was already true at
   `baseOverlayDamage = 0.0` for any actor with positive `CombatPowerOmni`, so raising the estimate
   cannot change that comparison's outcome. No fixture in this suite places a target's HP inside the
   narrow band this fix could newly cross.

**This is an honest absence of an observed move, not a claim the fix is inert.** The fix changes a real
input to a real comparison; it simply does not cross a decision boundary any FIXTURE in this corpus
happens to sit near. The failure mode it closes — siege under-valuing a target it could actually finish
— surfaces in play at HP margins these hand-built fixtures do not probe. No fixture was altered to
manufacture a move; per the plan's own risk table, a re-bless outside `CAI3.6` is a stop-and-report, not
a target to hit.

## What held

- `RulesetVersion` unmoved (5) — this is siege AI, not the default battle/expedition policy switch
  (`decisions.md`'s bump trigger is module 14's cause, not this one).
- Battle and expedition goldens (`BattleGoldenTests`, `ExpeditionResolverTests.Tier_goldens_are_locked`)
  unmoved and unblessed.
- No existing siege test edited.
- `EngineVersion` untouched — this is a decision-side estimate, never an engine mechanic.

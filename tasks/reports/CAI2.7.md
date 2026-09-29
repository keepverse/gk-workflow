# `CAI2.7` — the kill-margin waste guard: the shipped seam idles, the twin falls through

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Filed, not fixed: the two readings pull in opposite
directions and the choice is an owner ruling. This is the row `CAI2.3`'s own text says is owed.

## THE RULING ASKED, in one line

*When the kill-margin waste guard fires, does the actor go IDLE — `ActionIntent.None`, which is what the
shipped `ActionStage.TryPick` does — or does it fall through to the FREE option, which is what the twin's
`ActionSchedule.Choose` does — and if it falls through, does a fired guard skip only COSTED options or
every option?*

## The two rules, read rather than paraphrased

| Side | Where | What it does |
|---|---|---|
| Seam | `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs:125-126` | Guard 2 refuses the action when `guards.KillMarginMilli >= 0 && targetFacts.HpMilli <= guards.KillMarginMilli`. The loop `continue`s (`:102-103`) and, when nothing passes, returns `actionId = ""` / `false` (`:108-109`) — so the policy idles. The free fallback (`ActionKind.Basic`) carries **no** waste-guard exemption; only the reserve floor exempts Basic. |
| Twin | `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs:171-172` | The free fallback (`CostResourceId is null`) **returns first**, before `skipCosted` is consulted (`:163`) — its own comment: *"the free fallback is never floored and never skipped: that is what keeps Walk's own 'a dry actor has nothing to do' validation true for every floor value"*. |

The ideal lists the waste guards in the same action-choice pass as the reserve floor
(`docs/architecture/combat-ai-ideal.md:319`, step 3), which is the reading the twin implements.

## Measured

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The divergence is pinned by a passing witness | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests" --nologo --verbosity quiet` | **3 passed / 0 failed** | `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs:335-350` |
| The seam's reader is in production | `grep -n "WasteGuardThresholds" gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs` | `:224` passes `state.AppliedProfile.Guards.ToWasteGuardThresholds()` into the stage | `CoreIntentPolicy.cs:224` |
| The only shipped profile that reaches it authors a ZERO margin | `sed -n '45,100p' gk-core/data/tuning/combat-ai.v2.json` | `siege/default` is `tierOverride: "smart"` with `guards.killMarginMilli: 0` | `gk-core/data/tuning/combat-ai.v2.json` |

Witness behaviour (smart tier, margin 50, target `HpMilli` 30 from round 2, `fightEndsThisRound` true from
round 2): twin `[skill, skill, pass, pass]`; seam `[skill, skill, null, null]`.

## Why the ruling turns on the margin being zero

With `killMarginMilli: 0` the guard fires only at `HpMilli <= 0` — an already-dead target — so it refuses
nothing a live decision would otherwise take. The divergence therefore moves no golden and changes no live
battle today; it becomes real at the commit that authors a non-zero margin. That is the same shape as
`CAI2.6`'s floor, which was inert until the decorator was wired and a floor authored.

## NOT proved

- **Whether a 0-HP target can still reach `TryPick` on any place.** Liveness comes from the view
  (`CoreIntentPolicy` iterates the view's live keys; on the lawn `LiveActorKeysFor` is the census list,
  where a death-animation actor may linger). Both possible answers leave the guard inert for a live target,
  and neither changes the ruling.
- **No golden run.** No shipped profile authors a non-zero margin, so the guard's firing condition cannot
  change a battle; the golden filter was not run for this row.

## Every document searched — and the deciding gap

`CAI2.6` was closed by a document that *decided* the case: the ideal's §6.1 step 3 said a pool "may not
drop below a fraction of its max **after paying**", and the spec quoted it verbatim. **This row's case is
the opposite: no document decides it.** That is what the owner is being asked to settle, and it is worth
stating because it changes the question from "which side contradicts the documents?" to "which of two
undocumented behaviours should ship?".

| Document | What it says | Decisive? |
|---|---|---|
| `combat-ai-ideal.md:319` (§6.1 step 3) | the waste guards are a step of the SAME pass as the reserve floor; then "the highest rank row wins" | **No** — silent on what happens when no row passes |
| `spec-action-schedule-twin.md:295,298` | "A floor that it does not clear falls through to the next affordable option, and to the free option when none clears"; "A floor of 1000 never hangs and never throws: the free fallback is unfloored by construction" | argues against the seam — but about the FLOOR |
| `spec-action-schedule-twin.md:300-302` (heading **Waste guard**) | "round *k* takes the free option while rounds before it are unchanged" | argues against the seam — but phrased as a criterion about the TWIN |
| `spec-action-schedule-twin.md:140-143` | "The free fallback is never floored … which is what keeps `Walk`'s own validation — 'must contain at least one free action … a dry actor has nothing to do' — true for every floor value including 1000. A floor that could starve the walk would be a hang, not a balance decision." | states the system invariant the seam breaks |
| `ActionSchedule.cs:107-109` | the twin REFUSES an option list with no cost-free entry, naming "a dry actor has nothing to do" | the invariant, enforced |
| `spec-core-scorer.md:269-271,466` — the seam's own spec | what each guard refuses; "refuses exactly its own case when switched on and `runWasteGuards` is true" | **No** — silent on the aftermath; nothing says a refusal means `ActionIntent.None` |

**So the seam's idling is an implementation choice, not a documented rule.** And the cost is not local:
the seam has no free-option floor of last resort, which is the same defect `CAI2.6`'s ruling was made to
end — that row's own words are that the post-payment comparison "is what ends the idling".

## Recommended, not taken

**A cost-free action is never refused by a waste guard.** It matches the twin's short-circuit
(`ActionSchedule.cs:171-172`, taken before `skipCosted` is consulted), the spec's waste-guard criterion,
and `ActionSchedule`'s construction invariant. The seam-side fix is one line in
`ActionStage.PassesWasteGuards` (`action.Costs.Count == 0` ⇒ pass) — measured, the parity fixture's free
action carries **zero** cost rows, not a zero-amount row — plus flipping the witness's `real` expectation
to parity and re-fixturing `ActionStageTests`' two kill-margin cases onto a COSTED action, because its
current fixture is cost-free and the guard's own test would otherwise stop testing the guard.

**Golden risk, measured rather than assumed:** the shipped profiles author `killMarginMilli: 0`, so the
guard fires only at `HpMilli <= 0`. A golden moves only if a golden battle has a 0-HP candidate with a
cost-free action available — which the golden filter must be run to decide. It was NOT run, because no code
moved.

**Not taken here** because the documents argue against the seam without deciding it, and this row's own
text says no code may move before the ruling.

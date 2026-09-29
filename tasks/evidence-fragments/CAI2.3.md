# CAI2.3 — `action-schedule-twin`: the identity half

Lane `combat-ai-2`. This is the module's own FIRST commit as its spec splits it: *"It ships with an
identity row. `SchedulePolicy.Greedy` reproduces today's walk byte-for-byte, so every existing caller,
test and baseline is unchanged by this module alone. Changing the policy AND the expressiveness in one
commit would make a moved number unattributable."* The parity test against the live core policy, the
profile→`Predictor.ActionEconomy.Options` projection and the dominance re-measure are the row's
remaining half and are named below, not claimed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `SchedulePolicy.Greedy` is the default and every existing case passes UNEDITED | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionSchedule\|FullyQualifiedName~Predictor"` | **35 passed, 0 failed** — `Walk(..., policy: null)` and `Walk(..., Greedy)` are asserted identical, and all fourteen pre-existing `ActionScheduleTests` cases plus `PredictorTests` compile and pass untouched | `Balance/Analytic/ActionSchedule.cs:54` (`SchedulePolicy`), `:97` (`Walk`) |
| Reserve floor is a floor on what REMAINS, per-row override `-1` defers, 1000 never hangs | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SchedulePolicyTests"` | **8 passed, 0 failed** — `The_reserve_floor_is_on_what_remains_not_on_what_is_spent` (max 100, cost 30, floor 200: the costed action is taken, which a "may spend at most 20%" reading would refuse), `Reserve_floor_minus_one_defers_to_the_policy_and_a_row_value_overrides_it`, `A_floor_of_1000_never_hangs_and_never_throws` (12 rounds, all free) | `ActionSchedule.cs:157-187` (`Choose`) |
| `MinTargets > 1` throws naming the option; an out-of-vocabulary `AiTier` throws naming it | same run | passes — `MinTargets_above_one_throws_naming_the_option` (names `heavy`, `minTargets=3`), `An_out_of_vocabulary_tier_throws_naming_it` (names `rogue/default`, `99`) | `:104-124` (validation preamble) |
| `SkipOverkill` is the waste guard and is off at Greedy | same run | passes — `SkipOverkill_skips_every_costed_option_when_the_free_one_ends_the_round`, and the same predicate under Greedy changes nothing | `:159-163` |
| `gk-core/tools/CombatSim` carries identical semantics | `dotnet build gk-core/tools/CombatSim/CombatSim.csproj`; `FORCE`/`FINESSE`/`BASTION` parity below | **Build succeeded** — `ActionPolicy.Choose` takes the same `reserveFloorMilli`/`skipCosted` knobs and the same `MinTargets` throw, over `ActionSet.ActionDef.ReserveFloorMilli`/`.MinTargets` (defaults `-1`/`1`, so an absent JSON field reads as the identity) | `gk-core/tools/CombatSim/ActionEconomy.cs` |
| Reference↔port parity still holds | `dotnet run --project gk-core/tools/ProvePredictor` | **PASS (max diff 8.836E-007)** at the 1e-4 threshold, on BOTH scopes — `Actions-only PASS (max diff 8.836E-007)` and `Actions+status PASS (1e-4): PASS (max diff 8.836E-007)` | — |
| Dominance / termination / geared / residual green and UNCHANGED | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Dominance\|FullyQualifiedName~Termination\|FullyQualifiedName~GearedCorner\|FullyQualifiedName~ResidualFitLoop"` | **47 passed, 0 failed** — no baseline moved | — |
| G7 (`Balance/Analytic` references a shipped combat symbol) still holds | `python gk-core/scripts/guard-class-system.py` | exit 0 — "closed form calls shipped combat symbols" | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs','gk-core/tools/CombatSim/ActionEconomy.cs','tests/FusionRpg.Core.Tests/Balance/SchedulePolicyTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14925 passed, 4 failed** — the same four pre-existing corpus facts | — |
| Doc citations re-anchored (`ActionSchedule.cs` 119 -> 195) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`; `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | 0 HIGH on both; three citations in the module's own spec re-pointed (`:15` -> `:16`, `:33-120` -> `:35-195`, `:100-112` -> `:157-187`) | `docs/architecture/combat-ai/spec-action-schedule-twin.md` |

## NOT done — the row stays open

1. **`ActionScheduleMatchesCorePolicyTests` is not written.** It needs a live `IIntentSource` fixture
   (an `IBattleView` + `CooldownLedger` + `IStanceCheck` + `IAffordabilityCheck` over a `CostLedger`)
   driving the real core policy in its performance tier against the twin over the same fixture. Without
   it the twin is a fork of the selection policy that nothing proves agrees with its owner — this is the
   module's mechanism of the guarantee, and it is the next thing to build.
2. **The projection from a `CombatAiProfile` into `Predictor.ActionEconomy.Options` is not built.**
   Every call site still hand-builds that list, exactly as the row says.
3. **Smart/Performance "provably collapse" is carried, not proved.** `SchedulePolicy.Tier` is validated
   and never branched on, and the collapse argument is written out in the record's own doc; a test that
   *proves* it needs the core-policy fixture from (1).
4. **The dominance run is not recorded.** The row asks for the run as evidence it did not move; the tool
   is `gk-forge/tools/DominanceBaseline`, which is outside this lane's allowed paths. The four named test classes
   are green and unchanged (run above), which is the strongest check available here.
5. **`docs/research/combat-ai/REVIEW-B.md:55` and `docs/research/combat-math-dedup-audit-2026-09-16.md:147,254`
   cite `ActionSchedule.cs` line numbers that this change moves.** Both files are outside this lane's
   documentation fence (`docs/architecture/combat-ai/**`, `combat-ai-ideal.md`, `DESIGN-GATE.md`), so they
   are named here for the mechanical sweep rather than edited.

## Second slice — the policy reaches the predictor, and the tier collapse is proved

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The reserve floor reaches the duel predictor | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SchedulePolicyTests"` | **11 passed, 0 failed** — `A_reserve_floor_reaches_the_duel_predictor`: at 500 per-mille the 54-cost `skill-strike` cannot leave 27 in the qi pool, so the mix drops to the 1.0-multiplier `strike`; `NetAttritionA` is strictly lower than Greedy's and `WinShareA` stays 0.5 on a symmetric apparatus | `Balance/Analytic/Predictor.cs:38-42` (`ActionEconomy.Policy`), `:255-257` (`MixedStrike` passes it) |
| The new field is the identity at `Greedy` | same run | passes — `An_explicit_Greedy_policy_is_the_same_economy_as_no_policy` compares `Predict` with `Policy = Greedy` against `Policy = null` and gets an equal `DuelPrediction` | — |
| §4: Smart and Performance provably collapse | same run | passes — `Smart_and_Performance_tiers_produce_the_identical_sequence` runs the same options and pools under both tiers and gets identical action sequences | `ActionSchedule.cs:54-61` |
| The reference↔port gate and every pre-existing case | `dotnet run --project gk-core/tools/ProvePredictor`; `dotnet test ... --filter "FullyQualifiedName~ActionSchedule|~Predictor"`; `--filter "Category=BalanceGuard"` | ProvePredictor **PASS both scopes (max diff 8.836E-007)** at 1e-4; action/predictor suites **46 passed, 0 failed** with `PredictorTests` untouched; BalanceGuard **25 passed, 0 failed** | — |
| Dominance / termination / geared / residual unchanged | `dotnet test ... --filter "FullyQualifiedName~Dominance|~Termination|~GearedCorner|~ResidualFitLoop"` | **47 passed, 0 failed** | — |
| G7 + doc citations (`Predictor.cs` 297 -> 299) | `python gk-core/scripts/guard-class-system.py`; `guard-doc-citations.ps1 -Strict`; `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | class-system exit 0; **0 HIGH** on both doc checks; seven `Predictor.cs` citations re-anchored (`:38-41`→`:38-42`, `:72-73`→`:73-74`, `:255-258`→`:256-259`, `:258-287`→`:259-288`, `:68-71`→`:69-72`, `:41`→`:42`, `:102`→`:103`) | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Balance/Analytic/Predictor.cs','tests/FusionRpg.Core.Tests/Balance/SchedulePolicyTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14928 passed, 4 failed** — the four pre-existing corpus facts | — |

### ERRATUM REQUESTED — the projection is claimed by two documents

The row's acceptance says *"**The projection from a real profile into `Predictor.ActionEconomy.Options`
lands here.** Owned by this task so CAI3.6 does not discover it inside its one-cause commit."* The
module's own spec says the opposite, at `spec-action-schedule-twin.md:407-408`:

> `PredictorTests.cs:15-18`). Nothing yet projects a real `combat-ai` profile into that list. That
> projection belongs to `profile-schema` (module 2) or to module 14's re-fit — naming it here so it is
> [not forgotten].

Two documents in one program disagree about who owns it, **and neither specifies the mapping**: a
`CombatAiProfile` carries `AiActionFilter`s and a reserve floor, never a cost or a damage multiplier,
while `ActionOption.CostShareOfOutputMilli` is a share of the action's own nominal output and the live
ledger prices an *absolute* amount scaled by rung and `Θ`. Converting one into the other is the twin's
cost model — a design decision with numbers, not a mechanical projection. **Requesting a ruling on (a)
which module owns it and (b) the conversion**, rather than inventing either. The parity test
(`ActionScheduleMatchesCorePolicyTests`) is blocked behind the same question, because it must compare a
round-by-round trajectory and the correspondence between the two cost models is exactly what it would
have to assert.

**Also still not done (unchanged from the first slice):** the overkill predicate through `Predictor`
needs `MixedStrike` to drive rounds incrementally (the predicate reads a cumulative mean the guarded
walk itself produces — a fixed point, not a pre-computable input), and the `gk-forge/tools/DominanceBaseline`
run is outside this lane's fence.

## Attempted and REVERTED — the overkill guard through `Predictor` needs a different assertion seam

I implemented the spec's §2 prescription (`MixedStrike` supplies the predicate from a pass over the
cumulative mean, then walks with the guard) as a two-pass estimate-then-walk, with the estimate pass
sharing the strike-mixture cache so it costs no extra distribution work, and gated on
`policy?.SkipOverkill == true` so every existing caller (and therefore `gk-core/tools/ProvePredictor`) takes the
single-walk path byte-for-byte. It is **reverted**, because I could not write an assertion for it that I
can explain:

- Sized so the guard fires near the finish (defender HP 600 vs a ~144 mean), `guarded == greed` exactly.
- Sized so it fires from round 0 (defender HP 1), `guarded` was neither the costed nor the free mean:
  with the free option at multiplier 2.5 the pair was 143.75 vs 156.25, and at 100.0 it was 1000 vs 6250.

`DuelPrediction.NetAttritionA` is a **derived rate** (attrition net of recovery, over the rounds that
happened), not the swing mean, so it is not a clean read-out of which action fired — and a 1000-vs-6250
gap between two all-free mixes is a symptom I do not understand well enough to assert on. The honest
conclusion is that the guard is provable at the `ActionSchedule` level (where it is: 8 tests) but needs a
**mix-observing seam** — the chosen action per round, or a record of the mix — before it can be proven
*through* the predictor. Shipping the code with an assertion that merely happens to pass would have been
worse than not shipping it, so the change and its test are both gone; `ActionEconomy.Policy` and the
reserve floor's reach (both tested and explained) stay.

Recorded here and on the row so the next lane does not repeat the attempt blind.

## Third slice — the parity test, and the divergence it found

The row's "mechanism of the guarantee" is landed: `ActionScheduleMatchesCorePolicyTests` drives the real
`CoreIntentPolicy` (performance tier, a parsed profile, a REAL `CostLedger` over real pools) and the
analytic twin over the same fixture round by round and compares the chosen action each round. The two
correspondences the comparison needs are made explicitly in the fixture and documented there: regen is
ZERO on both sides (which removes the spec's Open question 2 — the round↔tick mapping — instead of
inventing one), and each twin share is derived from the authored amount as
`amount × 1000 / (baseDamage × multiplier)` at Θ=0 and rung 1, where the real cost IS the authored amount.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The twin matches the core policy round by round (the row's parity line) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests"` | **2 passed, 0 failed** — `The_twin_matches_the_core_policy_round_by_round_with_no_reserve_floor` agrees over 8 rounds from a 200-point pool, including the round where the pool runs out and both fall to the free fallback | `tests/.../Balance/ActionScheduleMatchesCorePolicyTests.cs` |
| **The reserve-floor rule DIFFERS, and the test pins it** | same run | passes — `The_reserve_floor_rule_differs_between_the_twin_and_the_shipped_seam` asserts both sequences: twin `[skill, pass, pass, pass]`, real `[skill, skill, null, null]` | — |
| Golden: nothing moved | `--filter "FullyQualifiedName~BattleGolden"`; `--filter "FullyQualifiedName~ActionSchedule"` | **5/5** and **17/17**, 0 failed | — |
| Boundary (real path, numbers) | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tests/FusionRpg.Core.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs') -Session combat-ai-20260920"` | **15102 passed / 0 failed** | — |
| Guards | `guard-actor-hub.ps1`; `guard-battle-responsibility.py` | both exit 0 | — |

### FINDING (needs an owner ruling; filed on this row and in the todo)

**The reserve-floor rule differs between the shipped seam and both the twin and the ideal's own wording.**

- `ReserveFloorAffordability.cs:92-108` refuses when `current <= floor` — evaluated BEFORE the action's
  own cost and applying to EVERY action.
- The ideal's words (spec §2, quoting §6.1 step 3) are that a pool *"may not drop below a fraction of its
  max **after paying**"* — `current - cost >= floor` — which is what the twin implements.

Two consequences, both measured rather than argued. **(a)** With max 1000, floor 900 and costs 80/40 from
a full pool, the seam allows the 80-cost action TWICE (1000 > 900 → 920 > 900 → 840) where the twin allows
it once (1000−80 = 920 ≥ 900, then 920−80 = 840 < 900). **(b)** Once at or below the floor the seam refuses
**even a zero-cost action**, so the actor returns `ActionIntent.None` and idles instead of falling through
to its free option — the twin never floors the free fallback, and that is documented as load-bearing
there because a floor that could starve the walk would be a hang.

**Why this is filed rather than fixed:** aligning the seam to the ideal's rule changes live behaviour and
would move battle goldens, which this row's Golden line forbids ("byte-identical"); aligning the twin to
the seam's rule would make the ideal's wording stale and would floor the free fallback. Either is a
decision for whoever owns `ReserveFloorAffordability`'s contract. The witness test means whichever way it
is ruled, the current behaviour cannot drift unnoticed.

---

## Fourth slice — the OVERKILL parity case (lane `combat-ai-3`, 2026-09-21)

Reopened because the row's deps (`CAI1.8`, `CAI1.9`) are **done in the ledger**, so the acceptance's
"and the overkill case" is this session's work rather than a denied path.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The overkill case is measured, not assumed | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~ActionScheduleMatchesCorePolicy"` | **3 passed, 0 failed** (2 before, +1 new) | `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs` |
| The two sequences, as measured | same run | twin `[act.skill, act.skill, act.pass, act.pass]`; seam `[act.skill, act.skill, null, null]` (`null` = `ActionIntent.None`) | — |
| Non-vacuous — the guard actually fired | same run | the two `Assert.Equal` on the full sequences mean a walk in which neither guard existed (both sides taking `act.skill` every round) fails the test | — |
| The four acceptance-named classes, green and unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~DominanceBaseline\|FullyQualifiedName~TerminationGuard\|FullyQualifiedName~GearedCorner\|FullyQualifiedName~ResidualFitLoop"` | **32 passed, 0 failed** | — |
| Nothing else in the balance module moved | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests` | **210 passed, 0 failed** | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs') -Session combat-ai-3"` | `core-balance (module)` → **210 passed / 0 failed**, exit 0 | — |

### FINDING (the same family as the reserve-floor one; needs a ruling, filed on this row)

**The core's `KillMarginMilli` waste guard refuses EVERY action and the actor idles; the twin's
`SkipOverkill` falls through to the free option.**

- `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs:126`:
  `if (guards.KillMarginMilli >= 0 && targetFacts.HpMilli <= guards.KillMarginMilli) return false;` — and
  `TryPick`'s loop applies that to each held action in order, with no exemption for an uncosted one, so
  with all of them refused `TryDeclare` returns `ActionIntent.None` and the actor does nothing.
- `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs:171-187`: when the caller's `fightEndsThisRound`
  predicate is true, costed options are `continue`d and the **free** option is returned — it short-circuits
  *before* the guard is consulted, deliberately, because a guard that could starve the walk is a hang.
- So one word ("overkill") produces "idles" in the seam and "passes" in the twin. Same shape as the
  reserve-floor divergence: the seam refuses everything, the twin always has a free fallback.
- **Reachable in production** — the guard runs when `KillMarginMilli >= 0` at smart tier, and the shipped
  `gk-core/data/tuning/combat-ai.v1.json` profile `siege/default` is `tierOverride: "smart"` with
  `killMarginMilli: 0`. It is ON today; it only fails to bite because it fires on an already-0-HP target.
  A tuning pass authoring a positive margin makes the two walkers disagree about what the actor **does**.
- **Why filed rather than fixed:** the same two options and the same consequence as `CAI2.6` — aligning the
  seam to fall through changes live smart-tier behaviour, and aligning the twin to idle contradicts
  §2's own wording ("the free one is taken") and its never-floor-the-free-fallback rule. That is an owner
  decision, and the witness test gives the ruling a target.

### NOT proved in this slice

- **The projection from a real profile into `Predictor.ActionEconomy.Options` is NOT landed.** It is the
  erratum this row already requested: the acceptance claims it, `spec-action-schedule-twin.md:421-423`
  assigns it to `profile-schema` (module 2) or module 14's re-fit, and no document specifies the mapping
  (a profile carries action FILTERS and a reserve floor but no cost or multiplier, while
  `ActionOption.CostShareOfOutputMilli` is a share of the action's own nominal output). Whoever owns it
  must also own that mapping design.
- **The `gk-forge/tools/DominanceBaseline` run is NOT measured** — `gk-forge/tools/DominanceBaseline/**` is outside this
  lane's fence. Its four test classes are green (above), which is the in-fence half of that criterion.
- **The overkill predicate *through* `Predictor`** (`MixedStrike` -> `Walk`) is still not asserted. This
  slice proves the guard's own behaviour and pins the parity divergence at the walk level, which is what
  the row's earlier note called "proven at the `ActionSchedule` level"; a mix-observing seam in the
  predictor remains a separate change and is not required by this acceptance line.

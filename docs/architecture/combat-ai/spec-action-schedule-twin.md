# Spec: `action-schedule-twin` (combat-ai module 9)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) §7
"The balance twin" · **Depends on:** `profile-schema` (2), `ai-tiers-personality` (3) ·
**Unblocks:** `auto-policy-switch` (14) · **Status:** spec, 2026-09-20. **Identity half BUILT**
(lane `combat-ai-2`, 2026-09-20): `SchedulePolicy` + `Greedy` as the identity default, the reserve floor,
`SkipOverkill`, the `MinTargets`/tier throws, and the `gk-core/tools/CombatSim` mirror — every pre-existing test
unedited, `ProvePredictor` PASS at 1e-4. **The parity test against the live core policy LANDED** (`ActionScheduleMatchesCorePolicyTests`, 3 tests — the reserve-floor parity, the overkill divergence witness and the smart/performance collapse) and the `gk-forge/tools/DominanceBaseline` run is **DONE** (it reproduces the checked-in baseline: same names, same wins, `dominantCorners == ["Might"]`, `theta == 100`). **The profile→`Predictor.ActionEconomy.Options` projection remains, and it is an owner erratum rather than work:** this module's own acceptance claims it while the Open-questions section assigns it to module 2 or 14, and no document specifies the mapping — a profile carries filters and a floor but no cost or multiplier. Two rulings the parity work found are filed: `CAI2.6` (the reserve floor's rule, closed by ruling) and `CAI2.7` (the kill-margin waste guard's rule, open).

## Objective

`Balance/Analytic/ActionSchedule.cs` is the closed-form model of how an actor spends its pools per
round. Its own doc comment states what it models: *"lazy regen, priority-ordered affordability,
pay-on-commit"* (`ActionSchedule.cs:16`), and `Choose` is literally "the first option in priority order
whose pool covers its cost" (`:100-112`). It says, in the same comment, that it deliberately ports
`gk-core/tools/CombatSim`'s `ActionPolicy` because *"there is nothing else to defer to for this piece"*
(`:8-16`). `ActionPolicy.Choose` is the same three lines (`ActionEconomy.cs:150-157`) and its doc
admits the same thing: *"deliberately the simplest policy that exercises the economy — action-selection
(A7) is a whole module and inventing a clever policy here would make the measurement about the policy
instead of the distribution."*

That module is now being built. Its policy has a **reserve floor** (a pool may not drop below a
fraction of its max after paying), **waste guards** (minimum targets, target not about to die, fight
not about to end) and a **tier** (ideal §6.1 step 3, §6.2a). The moment `auto-policy-switch` (14) makes
that the battle default, the analytic twin models a policy the game no longer plays — `AUDIT.md` M4.
Ideal §7 rules it: *"`ActionSchedule` is the core's analytic twin. It models the default profile's
reserve and waste guards, and it changes in the same change as the core."*

This module teaches the twin those three things, keeps `gk-core/tools/CombatSim` consistent so the
reference↔port parity gate stays meaningful, and **names exactly which fits and baselines must be
re-measured** — which, measured rather than assumed, is a shorter list than the ideal implies (§"What
must be re-measured" below).

**It ships with an identity row.** `SchedulePolicy.Greedy` reproduces today's walk byte-for-byte, so
every existing caller, test and baseline is unchanged by this module alone. Changing the policy *and*
the expressiveness in one commit would make a moved number unattributable — the same one-cause argument
`spec-mode-profile.md` §Objective makes and that H1 makes for goldens.

## Tech stack

`FusionRpg.Core` (`Balance/Analytic/ActionSchedule.cs`, `Predictor.cs`), `gk-core/tools/CombatSim`
(`ActionEconomy.cs`, `Simulator.cs`, `Analytic.cs`), `gk-core/tools/ProvePredictor`. No new dependency. No new
project. Closed vocabularies referenced, not redefined: `AiTier` is `ai-tiers-personality`'s (module 3).

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionSchedule|Predictor"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProvePredictor"      # the parity gate
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Dominance|Termination|GearedCorner"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"
dotnet run --project gk-core/tools/ProvePredictor                    # prints MAX ABS DIFF per scope
dotnet run --project gk-forge/tools/DominanceBaseline -- --theta 100  # record, expected unchanged (see below)
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

No `publish.py`: this module adds no tuning key. The numbers it newly reads (reserve per-mille, waste
thresholds) are `profile-schema`'s rows in `gk-core/data/tuning/combat-ai.v1.json` (new — **landed**, CAI1.8 —
module 2 publishes it).

## Project structure

| What | Where |
|---|---|
| The walk + the new policy record | `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs:35-195` |
| The economy DTO the predictor passes through | `gk-core/src/FusionRpg.Core/Balance/Analytic/Predictor.cs:38-42` |
| The closed-form consumer | `gk-core/src/FusionRpg.Core/Balance/Analytic/Predictor.cs:256-259` |
| Sim-side policy (must stay consistent) | `gk-core/tools/CombatSim/ActionEconomy.cs:136-157` |
| Sim-side call sites | `gk-core/tools/CombatSim/Simulator.cs:351-354`, `gk-core/tools/CombatSim/Analytic.cs:501` |
| The reference↔port gate that would go red on drift | `gk-core/tools/ProvePredictor/Program.cs:114-160` |
| Existing tests (must stay green untouched) | `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleTests.cs`, `.../PredictorTests.cs:250-276` |
| New parity test | `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ActionScheduleMatchesCorePolicyTests.cs` (new — **landed**, CAI2.3) |

## The shape

### 1. Why a twin is not a second mechanism

`battle-engine-ssot.md` §5's rule that is not a question — *"the feature calls the engine's mechanism.
It never re-implements it"* — has to be answered head-on, because this module deliberately keeps a
second expression of action selection.

The twin **cannot** call the core policy. The core policy needs an `IBattleView`, a `CooldownLedger`,
an `IStanceCheck`, an `IAffordabilityCheck` and a live `CostLedger` (`StubIntentSource.cs:33-38`,
`SiegeAiIntentSource.cs:84-95`); `Predictor` is a closed-form duel estimator over two
`CombatActorSnapshot`s with no board at all (`Predictor.cs:26-32`). What keeps the two honest is not a
shared call but a **proven agreement**, and this repo already has that pattern by name:
`ResolverMatchesSimulatorTests` and `gk-core/tools/ProvePredictor`'s exact cross-check at `1e-4`
(`ProvePredictor/Program.cs:152-160`), which is what caught a real DoT side-attribution bug
(`Predictor.cs:103`, `PredictorTests.cs:277-300`).

So this module owes a **parity test**, not a shared call: `ActionScheduleMatchesCorePolicyTests` drives
the real core policy (module 1's generalised scorer, in its performance tier) and the twin over the same
fixture and asserts the same action sequence. That is the mechanism of the guarantee, and without it the
twin is exactly the fork the rule bans.

### 2. `SchedulePolicy` — the three additions, with an identity row

```csharp
// ActionSchedule.cs
/// <summary>How the walk chooses, modelled after the shipped combat-ai profile. `Greedy` is the
/// IDENTITY: it reproduces the pre-combat-ai walk byte-for-byte, so every existing caller and
/// baseline is unchanged by this module alone.</summary>
public sealed record SchedulePolicy(
    string ProfileId,            // provenance only — which combat-ai profile these rows express
    AiTier Tier,                 // closed vocabulary (module 3); see §4
    long ReserveFloorMilli,      // default per-mille of Max that must REMAIN after paying
    bool SkipOverkill)           // waste guard: no costed action when the free option already kills
{
    public static readonly SchedulePolicy Greedy = new("greedy", AiTier.Performance, 0, false);
}

public readonly record struct ActionOption(
    string Id, int Priority, double DamageMultiplier,
    string? CostResourceId, long CostShareOfOutputMilli,
    long ReserveFloorMilli = -1,   // -1 = "use the policy's default"; a per-row override
    int MinTargets = 1);           // waste guard the duel domain cannot express — see §3
```

`Walk` gains a trailing `SchedulePolicy? policy = null` (null ⇒ `Greedy`), so every existing call site
and every one of `ActionScheduleTests`' fourteen cases compiles and passes untouched. That is the
acceptance, not a convenience.

**Reserve floor**, inside `Choose` (`ActionSchedule.cs:157-187`):

```csharp
var have = pools.TryGetValue(a.CostResourceId, out var p) ? p.Value : 0.0;
var cost = CostOf(a, baseDamage);
var floorMilli = a.ReserveFloorMilli >= 0 ? a.ReserveFloorMilli : policy.ReserveFloorMilli;
if (have - cost >= p.Max * (floorMilli / 1000.0)) return a;
```

Three properties this shape must keep, each of them a rule this repo already states:

- **It is a floor on what REMAINS, not a floor on what is spent.** The ideal's words: *"a pool may not
  drop below a fraction of its max after paying"* (§6.1 step 3). Reading it the other way would make a
  full pool unspendable.
- **It is a bounded ratio of a pool, not a progression cap**, so it is exempt from the no-hard-ceiling
  rule *and must say so in a comment* (`ssot-power-scale.md` §11; DESIGN-GATE §1 cap row). The floor
  caps no magnitude; it changes which option is chosen.
- **The free fallback is never floored.** `CostResourceId is null` short-circuits before the floor is
  consulted (`:102`), which is what keeps `Walk`'s own validation — *"must contain at least one free
  action … a dry actor has nothing to do"* (`:69-72`) — true for every floor value including 1000.
  A floor that could starve the walk would be a hang, not a balance decision.

**Waste guard — overkill.** `MixedStrike` already walks with a running `cumDamage` and stops at the
target's HP (`Predictor.cs:259-288`, and its doc comment at `:242-253` explains why: *"averaging over
rounds that never happen is the exact mistake"*). The guard is the same quantity, one round earlier:
when `SkipOverkill` is set and the free option's own mean already reaches the remaining HP this round,
every costed option is skipped and the free one is taken. Because the twin's `Walk` is pure and knows
no HP, the predicate is supplied by the caller:

```csharp
public static IReadOnlyList<RoundOutcome> Walk(
    IReadOnlyList<ActionOption> options, IReadOnlyDictionary<string, PoolState> initialPools,
    double baseDamage, int rounds,
    SchedulePolicy? policy = null,
    Func<int, bool>? fightEndsThisRound = null);   // round index -> "the free option finishes it"
```

`null` means "never", which is the identity. `Predictor.MixedStrike` supplies it from the cumulative
mean it already computes — one closure, built once per `MixedStrike` call, not per round.

**"Target not about to die" and "fight not about to end" are the same condition in a duel**, because
there is exactly one target. The twin models one predicate and says so here rather than pretending to
two; when a multi-target domain exists, they separate.

### 3. What the twin refuses to model, loudly

`MinTargets > 1` is an **area** waste guard, and `Predictor` is a 1v1 duel estimator
(`DuelPrediction`, `Predictor.cs:26-32`; `DominanceGuard` predicts ordered pairs,
`DominanceGuard.cs:59-66`). There is no honest closed form for "this area action needs three live
targets" in a duel. So:

```csharp
if (a.MinTargets > 1)
    throw new ArgumentException(
        $"option '{a.Id}' is gated on minTargets={a.MinTargets}; ActionSchedule is a DUEL model and " +
        "cannot express an area waste guard. Model it in a multi-target predictor or exclude the row.",
        nameof(options));
```

A loud throw, not a silent skip and not a silent model. A silently-ignored guard is precisely the M4
failure this module exists to end, arriving from the other direction — and "declared, not deferred" is
this repo's own discipline for an absence (`WebMatchService.cs:88-92`).

### 4. Tier

`AiTier` is module 3's closed vocabulary: **smart** runs the full core (target-first scoring over the
capped candidate set, reserve, waste guards, anti-repeat, personality); **performance** runs the same
core with the scoring stage switched off — a fixed selector, first usable action after the gates, and
the reserve floor (ideal §6.2a).

**In the duel domain those two collapse, and the twin states that as a finding rather than modelling a
scoring pass it cannot see.** The reason is structural, not an approximation: the smart tier's extra
work is *target* selection over a candidate set, and a duel has one candidate. What remains — one pass
over the held actions, in the profile's preference order, subject to the gates and the reserve floor —
is what `Walk` already does.

So `SchedulePolicy.Tier` is **carried and validated, never branched on**, and the module proves the
collapse instead of assuming it:

- `Walk` asserts `Tier` is a known `AiTier` member (an unknown value throws, naming it — the closed-
  vocabulary discipline).
- A test asserts `Walk(..., policy with Tier = Smart)` and `Walk(..., policy with Tier = Performance)`
  produce the identical sequence for the same options and pools.
- The field earns its place as provenance: a recorded fit says which profile and tier it was fitted
  against, which is what `auto-policy-switch` (14) needs when it re-fits.

### 5. `gk-core/tools/CombatSim` stays consistent

`ActionPolicy` is shared by the simulator and the closed form *"so a disagreement between them can never
be two different action policies"* (`ActionEconomy.cs:134-135`). That sentence is the contract this
module must not break. `ActionPolicy.Choose` (`:150-157`) gains the same reserve floor and the same
overkill predicate, with the same identity default, and its two call sites
(`Simulator.cs:351-354`, `Analytic.cs:501`) pass the policy through.

`gk-core/tools/ProvePredictor` is the gate that notices if they drift: it builds `economyOptions` from
`ActionSet.Load("basic")` (`gk-core/tools/ProvePredictor/Program.cs:114-115`) and compares `Analytic.Predict` (CombatSim's own
reference) against `Predictor.Predict` (the Core port) across every ordered archetype pair, holding the
max absolute win-share difference below `1e-4` (`:152-160`). The file's own comment records that this
axis *"WAS RED at 9.222E-004 … until 2026-09-17"* and that the cause was a real port bug — this gate
catches exactly the class of drift this module could introduce. **Both sides must gain the policy in
the same change**, or the gate goes red for a reason that is the module's own defect.

## What must be re-measured — and what, verified, does not move

This is the list the ideal asks for, checked against code rather than assumed.

| Baseline / fit | Path | Verdict |
|---|---|---|
| `gk-core/tools/ProvePredictor` reference↔port gate, both scopes | Constructs a real `Predictor.ActionEconomy` (`gk-core/tools/ProvePredictor/Program.cs:137`) and runs `MixedStrike` | **Must be re-measured, and it is the module's gate.** Green at `Greedy`; green again only if CombatSim gains the identical semantics. |
| `PredictorTests` action-economy cases (`:250-276`) | `BasicEconomy` + `Predict(a, b, null, economy, null)` | **Re-run; must stay green untouched** under `Greedy`. New cases added for reserve and overkill. |
| `ActionScheduleTests`, incl. the hand-traced 7-round cycle (`:129-147`) | `Walk` directly | **Re-run; must stay green untouched.** The cycle `skill-strike, strike, strike, skill-strike, …` is the identity proof. |
| `docs/research/class-system/_baseline-dominance.json` + `DominanceBaselineTests` | `DominanceGuard.cs:64` calls `Predictor.Predict(actors[i], actors[j])` — the **two-argument overload** (`Predictor.cs:73-74`), which passes `economy: null` | **Does not move.** The action economy is not on the dominance path at all. Re-run and record the measurement as confirmation; a *moved* number here would mean the economy reached a path nobody expected, and is a stop-and-report. |
| `TerminationGuardTests`, `GearedCornerTests` | `TerminationGuard.cs:100` uses the same two-argument overload; `ToActor` builds `BaseDamage: 0.0` (`:151`) | **Does not move**, same reason. |
| `ResidualFitLoopTests` / `gk-core/tools/ResidualFitLoop` | Drives `TerminationGuard`/`Predictor` (`ResidualFitLoop/Program.cs:16`); its own gate is *"0 change(s) computed … nothing to publish"* (`ResidualFitLoopTests.cs:17-26`) | **Does not move**, and its no-op assertion is a strong tell: if it starts computing changes, the twin leaked into the fit. |
| `BattleGoldenTests` | Hashes `BattleEngine.Resolve` reports; `ActionSchedule` is analytic-only and is never on the engine path | **Does not move.** No re-bless, no `RulesetVersion` bump. Stated as this module's acceptance. |

**The honest headline:** extending `ActionSchedule` re-measures the predictor's own parity gate and
nothing else, because every balance guard in `Balance/Guards/` calls the economy-free overload. That
makes this module cheap and safe to land early — and it narrows what module 14 actually owes (14's
"dominance baseline re-measured" is a confirmation run, not an expected movement; see
`spec-auto-policy-switch.md`).

## Tunables

**None owned here.** Every number this module newly reads is a `profile-schema` (module 2) row in
`gk-core/data/tuning/combat-ai.v1.json` (new — **landed**, CAI1.8), published `v{n+1}` through
`gk-core/tools/tuning/publish.py`:

| Number | Owner file | Unit | Class |
|---|---|---|---|
| `reserveFloorMilli` (per profile, optional per action row) | `combat-ai.v1.json` | per-mille of the pool's `Max` | **Tunable.** A balance pass moves it. Seed value is module 2's; ideal §6.2 says the lawn's default sits *"just above the basic attack's own cost"*, and the `battle/auto` seed is `0` so `Greedy` is the identity. |
| `skipOverkill` | `combat-ai.v1.json` | flag | **Tunable** (a profile row). |
| `minTargets` | `combat-ai.v1.json` | count | **Tunable**, and refused by this module (§3). |

Structural, in code, with the comment the rule requires:

| Constant | Where | Why it is not tunable |
|---|---|---|
| `rounds` / `MaxRounds = 400` | `ActionSchedule.Walk`'s `rounds` param; `Predictor.ActionEconomy.MaxRounds` (`Predictor.cs:42`) | Already documented as *"the same kind of integration bound `RoundLimit` is … a ceiling on the computation, never a balance parameter"* (`ActionSchedule.cs:20-24`). Unchanged by this module. |
| The reserve floor's per-mille denominator (1000) | `ActionSchedule.Choose` | A unit, not a number. |

**Numeric types.** `ReserveFloorMilli` is `long` (per-mille of a magnitude the power ladder grows;
`CLAUDE.md` range table — `int` per-mille exceeds its range at Θ=3,213). The comparison itself is
`double` arithmetic because `PoolState.Value`/`Max`/`Regen` are already `double`
(`ActionSchedule.cs:38`) and floating point is allowed for a ratio (owner ruling 2026-09-15). The
per-mille is divided once, at the comparison, and never accumulated.

## Code style

- The identity default is a named `static readonly` on the record (`SchedulePolicy.Greedy`), the same
  shape `UsabilityResult.Usable` uses (`UsabilityResult.cs:38`) — never a magic `null` check scattered
  across call sites.
- New optional parameters are trailing and defaulted, so no existing caller moves — the same discipline
  `SiegeAiIntentSource`'s `retarget`/`trace` parameters follow (`SiegeAiIntentSource.cs:84-85`) and
  `UsabilityEvaluator`'s second overload (`UsabilityEvaluator.cs:31-34`, *"no existing caller or test
  moved"*).
- A bounded ratio carries the comment saying it is structural and why (`ssot-power-scale.md` §11).
- A refusal names the offending option id and what to do instead, matching
  `ActionSchedule.Walk`'s existing validation messages (`:67-79`).
- `Walk` stays pure and non-mutating — `ActionScheduleTests.Walk_doesNotMutateTheCallersInitialPoolsDictionary`
  (`:162-173`) is an existing contract, and the predicate parameter must not become a back door into it.

## Testing strategy

**Identity (the module's own acceptance)**
- ✅ Every existing `ActionScheduleTests` case passes with no edit, including the hand-traced 7-round
  cycle (`:129-147`).
- ✅ Every existing `PredictorTests` action-economy case passes with no edit (`:250-276`).
- ✅ `Walk(..., policy: null)` and `Walk(..., SchedulePolicy.Greedy)` produce identical sequences.

**Reserve floor**
- ✅ A floor that the post-payment balance clears leaves the choice unchanged.
- ✅ A floor that it does not clear falls through to the next affordable option, and to the free option
  when none clears.
- ✅ A per-row `ReserveFloorMilli` overrides the policy default; `-1` defers to it.
- ✅ **A floor of 1000 never hangs and never throws**: the free fallback is unfloored by construction.

**Waste guard**
- ✅ With `SkipOverkill` and a predicate true at round *k*, round *k* takes the free option while
  rounds before it are unchanged.
- ✅ With `SkipOverkill` false, the predicate is never consulted (assert the delegate is not invoked).
- ✅ `MinTargets > 1` throws, and the message names the option id.

**Tier**
- ✅ `Smart` and `Performance` produce identical sequences in the duel domain — the collapse, proven.
- ✅ An out-of-vocabulary `AiTier` value throws, naming it. (`AiTier`'s **member count** is module 3's
  closed-vocabulary pin, not this module's.)

**Parity — `ActionScheduleMatchesCorePolicyTests` (new)**
- ✅ Over a fixture of held actions with costs, the generalised core policy's chosen action id per
  round equals the twin's, for the reserve-floor case and the overkill case. Same shape as
  `ResolverMatchesSimulatorTests` / `ProvePredictor`: prove the agreement, do not assert it in prose.

**Cross-tool**
- ✅ `gk-core/tools/ProvePredictor` both scopes stay under `1e-4` after CombatSim gains the same semantics.
- ✅ `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests`, `ResidualFitLoopTests`
  green and **unchanged** — the verified no-move claim, asserted by running them.

**Never**
- ❌ Assert how many action options a profile has, how many profiles exist, or any weight/floor value.
  Those are readings that content moves (DESIGN-GATE §3 rule 7).
- ❌ Assert a specific `WinShareA` number produced by the new policy. The *relations* are the contract
  (starving a pool favours the other side — `PredictorTests.cs:261-275`'s own shape), not the value.

## Boundaries

**Always**
- Ship the identity row and prove it before adding a single new behaviour.
- Change `ActionSchedule` and `gk-core/tools/CombatSim`'s `ActionPolicy` in the same commit.
- Refuse, loudly and by name, a profile row the duel domain cannot express.
- Comment every bounded ratio as structural.
- Keep `Walk` pure and free of a clock, a file and an RNG (`ActionSchedule.cs:18-24`).

**Ask first**
- Changing `MaxRounds` or any `roundLimit` default — `Predictor.cs:69-72` carries a verbatim
  *"⛔ NOT A BALANCE METRIC"* warning about judging balance with a clock.
- Wiring an `ActionEconomy` into `DominanceGuard`/`TerminationGuard`. That would put the action economy
  on the dominance path for the first time and **would** move `_baseline-dominance.json`. It is a real
  design question and it is **not** this module's to take.

**Never**
- Let the twin and `ActionPolicy` diverge.
- Model a guard the duel domain cannot see.
- Branch on `AiTier` to invent a second selection algorithm — that is the mechanism fork the parity
  test exists to refuse.
- Put a balance number in code (`tunables-ssot.md`); every floor and threshold arrives from
  `combat-ai.v{n}.json`.
- Re-bless any golden from this module. It touches no engine path; a moved golden means it is wrong.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** **None — it is not battle logic.** It is a closed-form *model* of
   responsibility 6 (resource resolve and consume) used for balance prediction. §3c lists *"loot and
   reward generation, and progression credit"* among adjacent-but-not-the-engine systems for the same
   reason: an estimator is not a resolver. The closed register is untouched.
2. **Decide or resolve?** **Neither — it predicts.** It never enters `IIntentSource.TryDeclare` and
   never resolves a hit. It is the off-line twin of the deciding side.
3. **Mechanism or loop?** A **model**, which is why it needs the parity test to stay honest. The
   *mechanism* is module 1's core scorer; this is one bounded expression of it for a domain that
   mechanism cannot enter (no board, no view, no ledger).
4. **Which implementation does it extend?** `ActionSchedule` itself and `gk-core/tools/CombatSim`'s
   `ActionPolicy` (`ActionEconomy.cs:136-157`), which already share their selection semantics by
   design. It adds no third expression.
5. **Does every mode get it?** It is not a mode feature. It applies wherever a balance measurement runs
   a duel: `Predictor`, `gk-core/tools/ProvePredictor`, `gk-core/tools/CombatSim`. The balance guards do not run it
   today (verified above), and that is recorded as a measured fact, not an exemption.
6. **Deterministic and seeded?** Yes, and it must stay so: *"No RNG here either … a bounded,
   deterministic walk, not a simulation"* (`ActionSchedule.cs:18-24`). The predicate parameter takes a
   round index and returns a bool; it may not close over a clock or a generator, and
   `Walk_isPure_sameInputsSameOutputs` (`ActionScheduleTests.cs:149-160`) keeps that honest.

## Success criteria

1. `SchedulePolicy.Greedy` is the default, and every existing `ActionScheduleTests` and `PredictorTests`
   case passes **with no edit**.
2. Reserve floor, overkill guard and tier are expressible, with per-row override and the free fallback
   provably unfloored.
3. `MinTargets > 1` throws with the option id named.
4. Smart and Performance provably collapse in the duel domain.
5. `gk-core/tools/CombatSim`'s `ActionPolicy` carries the identical semantics, in the same commit.
6. `gk-core/tools/ProvePredictor` holds both scopes under `1e-4`.
7. `DominanceBaselineTests`, `TerminationGuardTests`, `GearedCornerTests` and `ResidualFitLoopTests`
   are green and unchanged, and the dominance run is recorded as evidence that it did not move.
8. `BattleGoldenTests` untouched; no `RulesetVersion` bump.
9. `ActionScheduleMatchesCorePolicyTests` proves the twin agrees with the real core policy.

## Open questions

0. **The reserve floor's rule differs between this twin and the shipped seam — CAI2.6 holds the ruling.**
   `ActionSchedule.Choose` implements §2's own words (*"may not drop below a fraction of its max **after
   paying**"*, i.e. `balance - cost >= floor`) while `Actions/Ai/ReserveFloorAffordability` implements the
   floor as a PRE-condition on the balance — it refuses every non-basic action once a watched pool is at or
   below its floor, before any cost is considered, so it also refuses a zero-cost action. At the same
   balance the two therefore admit different actions (max 1000, floor 900, costs 80/40 from a full pool:
   twin `[skill, pass, pass, pass]`, seam `[skill, skill, idle, idle]`). **Measured, not argued** — the
   witness test is `ActionScheduleMatchesCorePolicyTests.The_reserve_floor_rule_differs_between_the_twin_and_the_shipped_seam`,
   and `ActionStageTests.The_floor_refuses_at_exactly_the_balance_and_would_admit_one_point_above_it` pins
   the seam's boundary. Which reading wins is a decision (CAI2.6): aligning the seam to this section's
   wording changes live behaviour and moves battle goldens, so it must be its own one-cause commit with a
   predicted-delta note — never folded into `auto-policy-switch`'s re-bless; aligning the twin to the seam
   makes this section's wording stale and floors the free fallback, which the twin's own comment calls a
   hang. Recorded here because the whole defect is that two files use one phrase for two rules.

1. **Whether the balance guards should eventually run the action economy.** Today `DominanceGuard` and
   `TerminationGuard` call the economy-free `Predict(a, b)` overload, so the dominance matrix is
   measured with every swing free — which is a *different* actor than the one the game will play once
   module 14 lands. Options: (a) leave it, and treat the dominance matrix as a pure offence/defence
   comparison it has always been; (b) add an economy-carrying dominance variant beside it; (c) switch
   the existing one, moving `_baseline-dominance.json`. **Recommended default: (a) for this module**,
   with (b) as a named follow-up for whoever owns the class-system fit — (c) moves a committed baseline
   for a reason no one has asked for yet, and is an Ask-first balance decision.
2. **Whether the lawn's reserve floor is even in the twin's domain.** The lawn profile's floor *"sits
   just above the basic attack's own cost, so it never starves"* (ideal §6.2), but the lawn is
   real-time and has no rounds. Options: (a) the twin models turn-mode profiles only and says so;
   (b) a rounds↔ticks mapping. **Recommended default: (a)** — the twin's job is the predictor's
   domain, and inventing a tick mapping would be modelling a schedule the lawn does not run.
3. *(Cross-module note, outside this module's responsibility.)* `Predictor`'s `ActionEconomy` supplies
   `Options` from a hand-built list at every call site (`ProvePredictor/Program.cs:115-119`,
   `PredictorTests.cs:15-18`). Nothing yet projects a real `combat-ai` profile into that list. That
   projection belongs to `profile-schema` (module 2) or to module 14's re-fit — naming it here so it is
   not discovered during 14's one commit.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: balance analytics (Predictor/ActionSchedule), CombatSim tooling, tunables,
    battle engine boundary (§3c, estimator discipline).
[x] Session boundary: backlog-clean-up-20260920; this session wrote only the four
    docs/architecture/combat-ai/spec-*.md files, edited nothing else, ran no git mutation and no build.
[x] Read this session: combat-ai-map.md, combat-ai-ideal.md rev 3 (§7 + D1-D6), AUDIT.md (M4),
    S1-battle-core.md, battle-engine-ssot.md §2/§3c/§5, DESIGN-GATE §1 (tunables, magnitude, power,
    battle rows) + §5, decisions.md rows 43-44, CLAUDE.md + AGENTS.md hard rules.
[x] decisions.md checked: row 44 governs the bump that CONSUMES this twin (module 14); this module
    itself moves no golden and is not covered by a lock.
[x] Every factual claim cites file:line; every cited file was opened this session.
[~] audit-doc-citations.py reports no HIGH finding for this file -- run after writing; the one new
    file is marked "(new; does not exist yet)".
[x] Verified against CODE, not comments: DominanceGuard.cs:64 and TerminationGuard.cs:100 call the
    two-argument Predict overload (Predictor.cs:73-74, economy: null), which is why the dominance
    baseline does not move. This is the finding that changes the module's scope, and it was read,
    not assumed.
[x] Read the surrounding section of every rule quoted (battle-engine-ssot §5's "rule that is not a
    question"; ssot-power-scale §11's structural-limit exemption; ActionSchedule's own doc comment).
[~] Constraints tested, not assumed: the "does not move" verdicts are derived from the call-site
    overload, which IS the decisive evidence -- but the confirming runs (ProvePredictor,
    DominanceBaseline, the four guard suites) are listed as commands to RUN at build time. This
    session ran no suite (spec-only lane).
[x] Nothing contradicts a §2 invariant. Invariant 12 (balance surface is data) drives the tunables
    table; 13 (magnitudes fit their range) drives the `long` per-mille; 15 (SOLID) is answered
    head-on in §1 with a parity test rather than a claim.
[x] Corrections propagated: the ideal's §7 and the map's row 14 imply the dominance baseline moves
    with the twin. It does not. The correction is stated in "What must be re-measured", carried into
    Success criteria, and carried into spec-auto-policy-switch.md's own obligations.
[x] No assertion pins a derived population, item total, generated text, or per-cycle outcome; the
    testing section bans asserting profile/option counts and any WinShareA value explicitly.
[x] §2.16 event-refreshed cache: this module introduces none. Walk is pure and holds no state
    between calls (proven by the existing non-mutation test).
[x] No acceptance criterion fixes an ordering that can vary: the identity-then-behaviour ordering is
    a build sequence, not a runtime ordering, and is stated as such.
[x] Produces/consumes no actor combat or derived magnitude through ActorHub -- it reads a
    CombatActorSnapshot the caller already composed, and folds nothing.
[x] Extends no SOLID-violating path. The one real risk (a third expression of action selection) is
    named in §1 and closed with a parity test, not waived.
[x] New rule has a guard: the twin/core agreement is guarded by ActionScheduleMatchesCorePolicyTests
    and the twin/sim agreement by gk-core/tools/ProvePredictor's 1e-4 gate. No repo-wide rule is added, so no
    enforcement-registry row is owed.
```

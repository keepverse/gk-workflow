# Spec: `core-scorer` (combat-ai module 1)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** nothing · **Unblocks:** `profile-schema`, `ai-tiers-personality`, `intent-router`,
`resolvable-here`, `aggression-tier-map`, `siege-loadout-wiring` · **Status:** **built** (CAI1.1, 2026-09-20): `Actions/Ai/CandidateScorer.cs` holds the one additive scorer (`Score`, `ChooseTarget`, `TopThree`), and `Battle/Siege/SiegeAi.cs` no longer holds a scorer at all.

## Objective

Make `AiScoring` **the** scorer for every place, by moving it out of `Battle/Siege/` into `Core/Actions/Ai/`
and giving it the three things it is missing: the candidate cap applied **before** per-candidate work, a
selection stage that covers both argmax and an opt-in seeded weighted pick, and an action stage that reads
the real base damage through the one estimator. Siege becomes consumer #1 in this same module — not a later
refactor — because that is what keeps one scorer instead of two.

The defect this closes is named in the audit and confirmed in code. **There is exactly one scorer today and
it is siege-shaped**: `AiScoring.Score` / `EffectiveTier` / `ChooseTarget` / `ScoreBreakdownOf` / `TopThree`
lived in Battle/Siege/SiegeAi.cs at spec-authoring time — since moved verbatim to
`gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` by this module's own CAI1.1 commit — and the only other policy,
`StubIntentSource` (`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:27-97`), scores nothing at all — it takes
the nearest enemy (`:104-131`) and the first usable action (`:64-75`). Adding a second scorer beside
`AiScoring` is a mechanism fork (SOLID **S**; [battle-engine-ssot.md](../battle-engine-ssot.md) §2 and §5
Q3/Q4), which the audit caught as design challenge 1
([AUDIT.md](../../research/combat-ai/AUDIT.md) §4.1). So this module moves the one that exists.

Three concrete defects ride along, each verified in code:

1. **The work bound is applied too late.** `AiScoring.ChooseTarget` truncates to `MaxCandidatesScored`
   at `Actions/Ai/CandidateScorer.cs:147-149` (moved from SiegeAi.cs line 135 by CAI1.1) — *after*
   `SiegeAiIntentSource.ChooseTarget` has already built an `AiCandidate` for
   every live enemy and run an O(live) threat loop for each one
   (`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:179-262`, threat loop at `:234-244`). The cap
   bounds the *scoring*, not the *work*.
2. **The kill term reads a zero base.** `SiegeAiIntentSource.cs:214` calls
   `SiegeExpectedDamage.IsKillingBlow(selfDerived, targetDerived, targetCurrentHp)` and omits the optional
   `baseOverlayDamage`, which defaults to `0.0`
   (`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeExpectedDamage.cs:113-116`). That file's own parameter doc says
   omitting it *"does not merely shift the estimate, it changes the mitigated fraction"* (`:48-50`).
   The action's real base is already derivable: `ActionBaseDerivation.BasePowerMilli`
   (`gk-core/src/FusionRpg.Core/Actions/ActionBaseDerivation.cs:19-33`) at the holder's effective rung,
   `BattleRunState.EffectiveRungOf` (`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:708-709`).
3. **Anti-repeat would be a second mechanism.** `RetargetLedger`
   (`SiegeAiIntentSource.cs:316-351`) is the shipped anti-oscillation memory. A commitment bonus and a
   repeat-decay added beside it would be two mechanisms for one problem (audit M9). They merge into it.

## Tech stack

`FusionRpg.Core` only — new files under `gk-core/src/FusionRpg.Core/Actions/Ai/`, changed files under
`gk-core/src/FusionRpg.Core/Battle/Siege/`. No new dependency, no injector work, no server work, no SQL. Core stays
I/O-free: every number arrives as a constructed object ([tunables-ssot.md](../tunables-ssot.md) §7.2), and
this module constructs none of them — `profile-schema` (module 2) does.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionSelection|UsabilityEvaluator|ActionTagPreference"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
dotnet test gk-core/tests/FusionRpg.Guard.Tests
python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/scripts/audit-overflow.py --targets A3
```

No `publish.py` call: this module publishes no tuning. No `deploy-play.py`: it is Core-only and
gameless-first (ideal §3 principle 10).

## Project structure

| What | Where |
|---|---|
| Candidate/weights/selection types + the scorer | `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` (new — **landed**, CAI1.1) |
| The target stage (cap-before-work, filters, candidate build seam) | `gk-core/src/FusionRpg.Core/Actions/Ai/TargetStage.cs` (new — **landed**, CAI1.2) |
| The action stage (gates → resolvable-here → reserve → waste guards) | `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs` (new — **landed**, CAI1.3) |
| Reserve floor as an `IAffordabilityCheck` decorator | `gk-core/src/FusionRpg.Core/Actions/Ai/ReserveFloorAffordability.cs` (new — **landed**, CAI1.3) |
| Anti-repeat memory (moved + widened) | `gk-core/src/FusionRpg.Core/Actions/Ai/RetargetLedger.cs` (**landed**, CAI1.4 — the type moved out of `SiegeAiIntentSource.cs`, which no longer holds it) |
| The shipped scorer, emptied to a forwarding shim or deleted | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs` |
| Consumer #1: builds candidates behind the cap, passes the real base | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs` |
| Move-fidelity + behaviour tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CandidateScorerTests.cs` (new — **landed**, CAI1.1) |
| Cap-placement identity test | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/TargetStageCapTests.cs` (new — **landed**, CAI1.2) |
| Existing siege suites — **not edited** | `gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/SiegeAiTests.cs`, `SiegeAiIntentSourceTests.cs`, `SiegeAiLiveWiringTests.cs` |

## The shape

### 1. The types, and why they are field-for-field copies

```csharp
namespace FusionRpg.Core.Actions.Ai;

/// The scorer's own closed term vocabulary. Adding a term is a REVIEWED change (a new weight key,
/// a new column in every breakdown, a new line in every trace) — not a balance pass.
public enum ScoreTerm { HitChance = 0, Objective, Kill, LowHp, CannotCounter, Round, Risk }

/// Identical field list, order and types to the shipped `AiCandidate` (SiegeAi.cs:71-74), so the
/// siege projection is a positional copy and the move is auditable by eye.
public readonly record struct TargetCandidate(
    string ActorKey, int BaseTier, int Aggression,
    int HitChanceMilli, int ObjectiveClassMilli, bool IsKillingBlow,
    int TargetMissingHpMilli, bool TargetCanCounter, long IncomingThreatMilli);

/// Identical to the shipped `AiScoreBreakdown` (SiegeAi.cs:83-84).
public readonly record struct ScoreBreakdown(
    long HitChance, long Objective, long Kill, long LowHp, long CannotCounter, long Round, long Risk, long Total);

/// The scoring half of `Siege.AiTuning` (SiegeAi.cs:60-64), with the two siege-geometry fields and the
/// two dead fields left behind. `MaxCandidatesScored` and `AggressionRange` are STRUCTURAL: a
/// per-decision work bound and a closed vocabulary width. Neither is a progression ceiling.
public sealed record ScoringWeights(
    int HitChance, int Objective, int Kill, int LowHp, int CannotCounter, int Round, int Risk,
    int AggressionRange, int MaxCandidatesScored);
```

`AggressionRange` travels with the weights because `EffectiveTier` needs it inside the same call, and
module 6 (`aggression-tier-map`) changes only what that function *does* with it.

### 2. Scoring — moved, not rewritten

`Score`, `ScoreBreakdownOf`, `TopThree` and `FormatTopThree` move from SiegeAi.cs (was lines 110-189
at spec-authoring time) to
`CandidateScorer` **with no arithmetic edit**. Three properties are load-bearing and the move must not
disturb any of them:

- **Accumulation order is fixed** — hit-chance, objective, kill, low-HP, cannot-counter, round, then
  `-risk` (`Actions/Ai/CandidateScorer.cs:102-108`, moved from SiegeAi.cs by CAI1.1). The sum is `checked`, so reordering could change *which* term overflows
  first. The order is a contract, not a style choice.
- **Widen before multiply** — every term is `(long)weight * input`, never `(long)(weight * input)`
  (`Actions/Ai/CandidateScorer.cs:102-108`, moved from SiegeAi.cs by CAI1.1). This is `CLAUDE.md`'s rule 2, already correct; keep it.
- **`Total` is `Score`'s own return value**, never a re-sum of the broken-out terms
  (`Actions/Ai/CandidateScorer.cs:251`, moved from SiegeAi.cs line 164 by CAI1.1).
  The breakdown is trace readability; it can never disagree with the number a decision used.

The only widening is a `ScoringWeights` parameter type in place of `AiTuning`. Siege's call sites project
one to the other positionally.

### 3. Target stage — the cap moves in front of the work

Today the filter and the work are one loop (`SiegeAiIntentSource.cs:181-262`), and the cap is downstream
(`Actions/Ai/CandidateScorer.cs:147-149`, moved from SiegeAi.cs line 135 by CAI1.1). The stage splits into three ordered phases:

```
phase A  cheap filters, in view order   : key != self ; SideOf(key) != mySide ; DerivedOf(key) is not null
phase B  TRUNCATE to MaxCandidatesScored  <-- the work bound, applied here
phase C  per-candidate inputs            : hit chance, objective distance, killing blow, threat
```

**Phase A is exactly the shipped filter set, in the shipped order** (`SiegeAiIntentSource.cs:184-188`),
read from `IBattleView.LiveActorKeys` in the view's own order (`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:22`).
Because the surviving order is preserved, *"build all, keep the first N"* and *"keep the first N, build
those"* produce the **same set in the same order**. That is why the cap can move in front of the work
without moving a decision — it is a provable identity, not a hoped-for one, and
`TargetStageCapTests` asserts it directly (§Testing strategy).

The candidate-input builder is a **caller-supplied delegate**, not a method on the scorer:

```csharp
public delegate bool TryBuildCandidate(string candidateKey, out TargetCandidate candidate);
```

Siege supplies the one that exists today; the lawn and delve supply their own later. The scorer never
reads `IBattleView` itself, which keeps the same structural-determinism property `Actions/Ai/CandidateScorer.cs:65-67` (moved from SiegeAi.cs by CAI1.1) already
claims for its own file ("no `IBattleView` read anywhere in this file ... provable from the type
signatures alone").

Phase C's threat term reads only the capped candidates, so the loop that is O(live) per candidate becomes
O(cap x live) rather than O(live x live). Removing its **allocations** is `decision-perf`'s (module 7) job,
not this module's; the cap placement is what makes that fix bounded.

### 4. Selection — dual utility, with argmax as the identity case

```csharp
public enum SelectionMode { Argmax = 0, SeededWeighted = 1 }

public sealed record SelectionPolicy(
    SelectionMode Mode,        // Argmax is the default and is RNG-free
    int KeepPctMilli,          // 1000 = keep only ties with the best; lower widens the pool
    string RngStreamName);     // e.g. "ai.select" — a battle-owned SeededRng.DeriveStream name
```

The algorithm is Dill's dual utility (Game AI Pro 2 ch. 3, recorded in
[S5-prior-art.md](../../research/combat-ai/S5-prior-art.md) §3), with **tier as the rank**:

1. **Veto.** Phase A's filters are the veto; nothing that survives them is vetoed again here.
2. **Rank.** Keep only candidates at the best effective tier — the shipped `Min` / `Where` pair, now a
   manual loop (`Actions/Ai/CandidateScorer.cs:151-156`, moved from SiegeAi.cs lines 137-138 by CAI1.1).
   `EffectiveTier` is module 6's to change; this module calls it unchanged.
3. **Cut.** Shift every surviving score so the minimum is 1 — `w_i = score_i - min + 1` — then drop any
   `w_i < best * KeepPctMilli / 1000`. **The shift is mandatory, not cosmetic:** the risk term subtracts
   (`Actions/Ai/CandidateScorer.cs:108`, moved from SiegeAi.cs line 121 by CAI1.1), so a raw score is
   routinely negative and a percentage cut on a negative number is
   meaningless. Integer division runs last, once, on the shifted weights (`CLAUDE.md` numeric rule 5).
4. **Select.**
   - `Argmax`: highest score, ties broken by `StringComparer.Ordinal` on `ActorKey` — byte-for-byte the
     shipped `OrderByDescending(...).ThenBy(...)` pair, now a manual loop
     (`Actions/Ai/CandidateScorer.cs:191-203`, moved from SiegeAi.cs lines 140-145 by CAI1.1). Reads no RNG.
   - `SeededWeighted`: order the survivors by `ActorKey` ordinal **first** (a draw over an unordered set
     is not deterministic), then draw one index by cumulative weight from
     `SeededRng.DeriveStream(runSeed, RngStreamName)`
     (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:9-28`). Never `System.Random`, never a clock.

At `Mode = Argmax, KeepPctMilli = 1000` the pipeline reduces to the shipped `ChooseTarget` exactly. Those
are the defaults, and they are what siege gets at migration.

### 5. Action stage — one pass, cheapest gate first, tier-gated at the last step

The stage takes one flag, because §5 step 4 is the one part of it a tier switches off:

```csharp
/// `runWasteGuards` gates EXACTLY ONE THING: step 4. Every gate, ledger, ordering rule and
/// short-circuit below is shared — this is one implementation with one branch, never a second action
/// stage (SOLID S).
///
/// It is a BOOL, not an `AiTier`, and that is deliberate: `AiTier` is module 2's vocabulary and module
/// 2 depends on THIS module, so taking the enum here would invert the map's arrow and make module 1
/// unbuildable on its own. Module 3 (`ai-tiers-personality`) owns the one-line mapping
/// `tier == AiTier.Smart` and states it; this module owns only the branch. Default `true` = today's
/// behaviour, so the parameter is identity at migration.
public bool TryPick(string actorKey, string targetKey, AiActionFilter filter,
                    out string actionId, bool runWasteGuards = true);
```

For the one chosen target, walk `IBattleView.HeldActionsOf(actorKey)`
(`IBattleView.cs:39`) in the order `FrozenActionSet` already froze it
(`gk-core/src/FusionRpg.Core/Actions/Grants/FrozenActionSet.cs:26-28`), sorted once by
`ActionTagPreference.Compare` (`gk-core/src/FusionRpg.Core/Actions/ActionTagPreference.cs:53-60`) — never sorted
per decision, which is the allocation `StubIntentSource.cs:22-25` already refuses. For each action:

1. `UsabilityEvaluator.Evaluate` — the six shipped gates, stance → bound → cooldown → afford → range →
   condition, short-circuiting (`gk-core/src/FusionRpg.Core/Actions/UsabilityEvaluator.cs:36-84`). Called, never
   re-implemented. This is where Lewis's *"stop at the first 0, cheap checks first"* already lives.
2. **Resolvable-here.** A `Func<string /*actionId*/, bool>` seam this module declares and module 5
   (`resolvable-here`) implements from each place's executor allowlist. The default delegate is
   `_ => true`, which is today's behaviour.
3. **Reserve floor.** Not a fourth gate — a decorator on gate 3. `ReserveFloorAffordability` wraps the
   real `IAffordabilityCheck` (production passes `state.CostLedger`,
   `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:175-180`) and refuses when paying would drop a pool below
   its floor. Wrapping keeps **one cost authority** (ideal §3 principle 6): the AI never computes a cost
   itself, and the refusal is a normal typed `UsabilityResult` the trace already understands.
   Structurally exempt: `ActionKind.Basic`. Starving the basic attack is the hoarding failure S5 names
   under *"Per-rest resources"*, and the floor exists to protect skill headroom, not to stop swinging.

   **This decorator is also the implementer of `intent-router`'s `poise` contract, and naming it here
   is the point.** Module 4 publishes the rule — *"the `poise` reserve floor is
   `max(profileFloor, expectedReactionSpend)`"* ([spec-intent-router.md](spec-intent-router.md) §4) —
   because the engine counters whenever `poise` pays, consulting no policy
   (`gk-core/src/FusionRpg.Core/Battle/Timeline/ReactionCounter.cs:38-45`). A rule with no implementer is a
   paragraph, so the decorator takes the two numbers as constructor inputs and computes the max itself:

   ```csharp
   public ReserveFloorAffordability(
       IAffordabilityCheck inner,
       IReadOnlyList<AiReserveFloor> floors,      // module 2's authored per-resource values
       long reactionPoiseSpend,                   // ReactionLanePolicy.Tuning.PoiseSpend, exposed by module 4
       int reactionsPerRoundExpected);            // combat-ai.v1.json `router.reactionsPerRoundExpected`
   ```

   The max is applied **only** to the `poise` resource id — every other pool's floor is the authored
   value unchanged. Both new arguments default to `0`, which makes the max a no-op and keeps the
   decorator byte-identical until module 4 supplies them. Computing the max here rather than folding it
   into the authored value keeps the authored number readable as *what the profile wants* and the
   engine's reaction budget readable as *what the engine will take anyway*; folding them would make a
   balance pass on the floor silently also a balance pass on the reaction budget.
4. **Waste guards — only when `runWasteGuards` is true.** A closed set of three, each a named predicate
   with a tunable threshold (module 2 owns the keys; the *names* are code). When the flag is false the
   whole step is **skipped by the branch above**, not by authoring the thresholds at identity: each
   guard needs either a live-count census or an expected-damage estimate, which is exactly the work the
   performance tier exists not to do ([spec-ai-tiers-personality.md](spec-ai-tiers-personality.md) §2).
   Authoring the thresholds off is a *different* lever — it makes a guard answer "pass" after paying
   for the census — and it does not replace the branch.
   - `minTargetsForArea` — an area envelope needs at least N live targets in its area;
   - `targetNotAboutToDie` — refuse when the target's current HP is already at or below the margin a
     cheaper action would deal (the *"ultimate on the last dying enemy"* complaint, S5 §5);
   - `fightNotAboutToEnd` — refuse a buff/heal when the opposing side's live count is at or below N
     (*"shields cast one turn before the fight ends"*, S5 §5).

   Live counts come from `IBattleView.LiveActorKeys` + `SideOf` (`IBattleView.cs:22,26`) — no new read.

The first action that clears all four wins. Which *rank row* it must come from is module 2's profile —
and the walk that picks that row is **`AiRowSelector.TryPick`**, specified in
[spec-profile-schema.md](spec-profile-schema.md) §4 and owned there. This module does not re-specify it
and must not re-implement it; it receives the row's `AiActionFilter` as the `filter` argument above and
the row's `TargetSelector` at the target stage. The division is deliberate: the *walk* is a question
about the profile's shape (module 2's type), the *pass* is a question about held actions (this
module's), and putting both here would make module 1 depend on module 2 against the map's arrow.

Cost is O(held actions) whatever the profile says, plus module 2's O(rows) walk and the one O(live)
census that walk is handed.

### 5a. Who assembles all of this into a policy — and why it is not this module

`TargetStage`, `ActionStage`, `ReserveFloorAffordability` and `RetargetLedger` are **building blocks,
not an `IIntentSource`**. Something has to hold a `CombatAiProfile`, resolve a tier and a personality,
run module 2's row walk, drive the two stages and return an `ActionIntent`. That type is
**`CoreIntentPolicy`, and it belongs to `ai-tiers-personality` (module 3)** —
[spec-ai-tiers-personality.md](spec-ai-tiers-personality.md) §6 declares it, with its constructor and
its `Create` factory, and delve (module 13) and battle (module 14) both construct it from there.

**Why module 3 and not this one, stated so it is a decision and not an accident:** assembling a policy
requires a `CombatAiProfile` (module 2's type) *and* an `AiTier`/`AiPersonality` (module 3's). This
module's dependency line is *"Depends on: nothing"*, and module 2 depends on **this** module — so
declaring `CoreIntentPolicy` here would invert the map's own arrow and make module 1 unbuildable until
module 2 exists. Module 3 is the first module that already depends on both, so it is the first place
the type can legally live.

Siege needs no such wrapper in this module: `SiegeAiIntentSource` stays consumer #1 and keeps its own
`IIntentSource` implementation, which is why this module can land byte-identical before module 3 does.

### 6. Anti-repeat — one mechanism, inside `RetargetLedger`

`RetargetLedger` moves verbatim from `SiegeAiIntentSource.cs:316-351` to `Actions/Ai/` and gains two
members. The shipped ones are untouched, including the property that makes `retargetLatencyTicks == 0`
(the value `siege.v1.json` ships) behave exactly like the stateless path (`Actions/Ai/RetargetLedger.cs:26-36`, its post-CAI1.4 home):

```csharp
public bool TryGetHeld(string actorKey, long nowTick, long retargetLatencyTicks,
                       Func<string, bool> stillValid, out string targetKey);   // unchanged
public void RecordRetarget(string actorKey, string targetKey, long nowTick);   // unchanged
public void Forget(string actorKey);                                           // unchanged

/// Added to the score of the currently-held target only. 0 by default => byte-identical.
public long CommitmentBonusFor(string actorKey, string candidateKey, long bonus);
/// Per-mille multiplier on a recently-chosen action's rank ordering. 1000 by default => no decay.
public int RepeatDecayFor(string actorKey, string actionId, long nowTick, int halfLifeTicks);
```

Both are memory, and memory is rebuilt by replay from tick 0 — the ledger is battle-scoped, constructed
once per battle exactly as `BattleRunState.cs:743-757` already constructs it, never static. Lewis's
warning travels with the code: a commitment bonus only *moves* the oscillation zone; the real fix is a
distinguishing consideration.

### 7. Numeric types

Scores are `long` and `checked` throughout, already correct at `Actions/Ai/CandidateScorer.cs:97-110` (moved from SiegeAi.cs by CAI1.1). Per-mille inputs
(`HitChanceMilli`, `ObjectiveClassMilli`, `TargetMissingHpMilli`, `KeepPctMilli`) stay `int` because they
are **bounded ratios**, 0..1000, not magnitudes — comment says so at each declaration.
`IncomingThreatMilli` is already `long`. The estimator inputs are `double` (`Derived.Get`,
`CombatProbability.Sigmoid` via `Math.Exp`), which is allowed (owner ruling 2026-09-15: precision is not
overflow) and means cross-platform identity rests on the shipped `BattleEnvironment.Stamp`
(`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:660-684`), **not** on any claim of integer purity. The ideal
states this and the audit's design challenge 4 is why.

### 8. How "siege stays byte-identical" is proven — exactly

This module lands as **two commits**, because it contains two golden causes and H1 allows one per commit.

**Commit 1 — the move. Byte-identical, and the acceptance is that it is.**

- Every function body moves with no arithmetic edit; `git log --follow` / a reviewer's diff shows a move,
  not a rewrite. The accumulation order, the `checked` arithmetic, the ordinal tie-break and
  `Total = Score(...)` are all preserved verbatim (§2).
- Every new lever ships at its identity value: `SelectionMode.Argmax`, `KeepPctMilli = 1000`,
  resolvable-here `_ => true`, reserve floor absent (and its two reaction arguments `0`, so the `poise`
  `max` is a no-op), `runWasteGuards = true` with all three thresholds off, `CommitmentBonusFor`
  bonus 0, `RepeatDecayFor` 1000, `baseOverlayDamage` still `0.0` at the siege call site.
- The cap moves in front of the work, which is an identity because phase A preserves view order (§3).
  `TargetStageCapTests` proves it at the boundary: with 40 live enemies and a cap of 32, the chosen key
  and the full `ScoreBreakdown` of the winner are identical to the shipped build-all-then-truncate path.
- **No existing siege test is edited.** `SiegeAiTests.cs`, `SiegeAiIntentSourceTests.cs` and
  `SiegeAiLiveWiringTests.cs` pass unchanged against the moved code (namespace-only edits are permitted
  and are the one change a reviewer should expect to see). If a siege test needs a value changed, the
  move is wrong.
- `BattleGoldenTests` and `ExpeditionResolverTests.Tier_goldens_are_locked` are unchanged and unblessed.
  A moved golden hash fails this commit.
- **One honest exception, stated rather than hidden:** in a fight with more live enemies than the cap,
  `TopThree` now sees the capped set instead of every candidate, so the `BattleTrace.AiDecision` line
  (`gk-core/src/FusionRpg.Core/Battle/Timeline/BattleTrace.cs:125`) can name different runners-up. That text is
  kept out of `Digest` and is golden-neutral by construction (`Battle/Timeline/BattleTrace.cs:121`), and no test may assert
  it — generated text is never a guardrail
  ([validation-ssot.md](../validation-ssot.md), `AGENTS.md` Hard boundaries). The **chosen** target is
  unchanged, which is the part that can move an outcome.

**Commit 2 — the estimator fix. Its own single cause.** The siege candidate builder starts passing
`ActionBaseDerivation.BasePowerMilli(kind, actionId, EffectiveRungOf(actorKey, actionId), rungTable, tuning)`
(`ActionBaseDerivation.cs:19-33`, `BattleRunState.cs:708-709`) into
`SiegeExpectedDamage.IsKillingBlow`'s `baseOverlayDamage` (`SiegeExpectedDamage.cs:113-116`), closing the
`SiegeAiIntentSource.cs:214` omission. This **can** change which target siege picks, so it carries its own
predicted-delta writeup and its own re-bless if any golden moves. It does not bump `RulesetVersion`: siege
decisions are AI, and `decisions.md`'s bump trigger is the *default battle policy* changing, which is
module 14's (`auto-policy-switch`) cause, not this one. If a battle or expedition golden moves here, that
is a finding to report, not to bless — it would mean siege scoring reaches a non-siege golden, which
nothing in the evidence predicts.

## Tunables

**This module publishes none.** Every number it reads arrives in a `ScoringWeights` / `SelectionPolicy` /
guard-threshold object constructed by module 2 from `gk-core/data/tuning/combat-ai.v1.json`, and until module 2
lands, siege keeps constructing them from `gk-core/data/tuning/siege.v1.json`'s `ai` block through
`SiegeTuningLoader` (`gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs:333-367`) exactly as today. **Corrected 2026-09-22:** module 2 has landed — CAI1.8 moved the ten keys into `gk-core/data/tuning/combat-ai.v1.json`'s `profiles["siege/default"]`, and the loader now reads only the two dead and the two siege-geometry keys, saying so in its own comment at `:333-339`. Core reads
no file ([tunables-ssot.md](../tunables-ssot.md) §7.2).

The numbers that pass through, with the label each must carry in code:

| Number | Seed today | Kind | Label required in code |
|---|---|---|---|
| `weightHitChance` 70, `weightObjective` 50, `weightKill` 15, `weightLowHp` 10, `weightCannotCounter` 10, `weightRound` 1, `weightRisk` 120 | `gk-core/data/tuning/siege.v1.json` `ai.*` | balance | tunable — moves in module 2 |
| `maxCandidatesScored` 32 | same | **structural** | *"a per-decision work bound, not a progression ceiling"* — the wording `siege.v1.json`'s own `ai._note` already uses |
| `aggressionRange` 2 | same | **structural** | *"the range IS the taunt/stealth/decoy vocabulary"* (`Actions/Ai/CombatAiProfile.cs:59`, moved from SiegeAi.cs by CAI1.1/CAI1.8) |
| `retargetLatencyTicks` 0 | same | balance | tunable |
| `KeepPctMilli` | 1000 (new, identity) | **bounded ratio** 0..1000 | comment states the bound and that 1000 = argmax |
| `commitmentBonus` | 0 (new, identity) | balance | tunable |
| `repeatDecayHalfLifeTicks` | 0 = off (new, identity) | balance | tunable |
| `minTargetsForArea`, `killMarginMilli`, `fightEndingLiveCount` | all off (new, identity) | balance | tunable |

No literal on the balance surface: `CandidateScorer`, `TargetStage` and `ActionStage` are Math/Policy-class
files and carry no bare numbers beyond `0`, `1` and the per-mille divisor `1000`
([tunables-ssot.md](../tunables-ssot.md)).

## Code style

- **Indexed `for`, never `foreach`, over an `IReadOnlyList<T>`** in any per-decision loop — `foreach` over
  an interface-typed collection boxes the enumerator, which is the exact per-decision allocation
  `StubIntentSource.cs:61-63` already refuses and `SiegeAiIntentSource.cs:181,286,299` already follows.
- **`ActionIntent` stays a struct** with absence encoded in the value (`ActionIntent.None`,
  `gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:12-18,29-37`). Never a `Nullable<ActionIntent>`.
- **Doc comments carry the reasoning and the citation**, in the register the neighbouring files use —
  `SiegeAi.cs` and `StubIntentSource.cs` both explain *why* a choice was made and name the rule it obeys.
  A moved function keeps its original comment, with the move and its date appended.
- **`checked` on every integer magnitude sum**, `Math.Clamp` for a bounded ratio, `(long)a * b` never
  `(long)(a * b)`.
- **Core is Unity-free and DB-free.** No `File`, no `DateTime.UtcNow`, no `System.Random`.

## Testing strategy

Contracts and closed vocabularies only. Named tests, in
`gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/`:

**`CandidateScorerTests`**
- ✅ `Score_matches_the_shipped_siege_weights_term_for_term` — a fixed candidate table scored against the
  siege seed weights produces the same `ScoreBreakdown` the shipped `AiScoring.ScoreBreakdownOf` produces.
  This is a *migration-fidelity* assertion of specific numbers, and it is legitimate for exactly one
  reason, stated in the test: the module's whole claim is "the same arithmetic", so the expected values
  are the contract, not a reading.
- ✅ `Total_is_Score_not_a_resum` — the breakdown's `Total` equals `Score` for the same candidate.
- ✅ `Overflow_throws_rather_than_inverting_a_comparison` — a weight/input pair past `long` range throws,
  never wraps (`checked`, `Actions/Ai/CandidateScorer.cs:88-96`, moved from SiegeAi.cs by CAI1.1).
- ✅ `Argmax_ties_break_ordinal` — two identical scores resolve to the ordinally-lower `ActorKey`.
- ✅ `KeepPct_1000_and_Argmax_reduce_to_the_shipped_ChooseTarget` — over a generated candidate table,
  every pick matches.
- ✅ `Weighted_pick_is_reproducible_from_the_same_stream_name_and_seed`, and
  `Weighted_pick_shifts_negative_scores_before_cutting` — a table with negative scores still selects.
- ✅ `ScoreTerm_has_seven_members` — the closed term vocabulary, pinned with the reason: adding a term
  changes every weight key, every breakdown column and every trace line.
- ❌ Never assert how many candidates a fight produces, how many profiles exist, or the text of
  `FormatTopThree`.

**`TargetStageCapTests`**
- ✅ `Cap_before_work_selects_the_same_candidate_as_cap_after_work` — 40 live enemies, cap 32: same chosen
  key and same winning breakdown as the shipped order. **This is the byte-identity proof for the cap
  move.**
- ✅ `Phase_A_filters_run_in_view_order` — self, same-side and unreadable (`DerivedOf` null) candidates are
  dropped in `LiveActorKeys` order, so truncation is order-stable.
- ✅ `Per_candidate_inputs_are_computed_only_for_the_capped_set` — a counting `TryBuildCandidate` fake is
  invoked at most `MaxCandidatesScored` times. Counted, not timed.

**`ActionStageTests`**
- ✅ Gate order is `UsabilityEvaluator`'s, unchanged: an action both on cooldown and unaffordable reports
  `OnCooldown` (`UsabilityEvaluator.cs:62-67`).
- ✅ `Resolvable_here_default_admits_everything` — the identity default.
- ✅ `Reserve_floor_refuses_through_gate_3_and_never_starves_a_basic_attack`.
- ✅ `Poise_floor_is_the_max_of_the_authored_floor_and_the_expected_reaction_spend`, and
  `Both_reaction_arguments_zero_leaves_every_floor_at_its_authored_value` — module 4's published
  contract, with its identity case. Only the `poise` resource id is affected; a second resource with a
  floor is asserted unchanged in the same test.
- ✅ `runWasteGuards_false_skips_the_census_entirely` — a counting fake for the live-count read is
  **never invoked**. Counted, not timed. This is the assertion that distinguishes the branch from
  "thresholds authored off", which still pays for the census.
- ✅ Each waste guard, off at seed, refuses exactly its own case when switched on **and**
  `runWasteGuards` is true.

**`RetargetLedgerTests`** (extending, not replacing, the siege coverage)
- ✅ `Latency_zero_holds_nothing` — the shipped property, now at `Actions/Ai/RetargetLedger.cs:26-36`.
- ✅ `Commitment_bonus_zero_is_byte_identical`; `Repeat_decay_1000_is_byte_identical`.
- ✅ `Ledger_state_is_battle_scoped` — two ledgers do not see each other's memory.

**Golden impact.** Commit 1: **byte-identical**, and that is its acceptance — `BattleGoldenTests` and
`ExpeditionResolverTests.Tier_goldens_are_locked` unchanged and unblessed; the three siege suites pass
unedited. Commit 2 (the `baseOverlayDamage` fix): **one cause**, siege target choice only, with a
predicted-delta writeup; no `RulesetVersion` bump (that is module 14's).

## Boundaries

**Always**
- Move `AiScoring`'s bodies; do not retype them.
- Keep the scorer free of any `IBattleView` reference, so determinism stays provable from signatures
  (`Actions/Ai/CandidateScorer.cs:65-67`, moved from SiegeAi.cs by CAI1.1).
- Call `UsabilityEvaluator`, `CostLedger`, `ActionTagPreference`, `ActionBaseDerivation`,
  `SiegeExpectedDamage` — never re-derive what they compute.
- Default every new lever to its identity value.

**Ask first**
- Anything that would move a golden in commit 1.
- Adding an eighth `ScoreTerm`, or a ninth field to `TargetCandidate`.

**Never**
- Implement the rank walk here. `AiRowSelector` is module 2's (`spec-profile-schema.md` §4); a second
  walk is a second answer to *"which row is this actor on"*.
- Declare an assembling `IIntentSource` here. `CoreIntentPolicy` is module 3's (§5a), and declaring it
  in this module would invert the map's 1 → 2 → 3 arrows.
- Take `AiTier` as a parameter anywhere in this module — it is module 2's vocabulary. The waste-guard
  branch is a `bool`.
- A second scorer, a private fold of the same additive numbers, or a "temporary" parallel path
  (SOLID **S**; the `BattleStatComposer` dual-compose incident of 2026-09-12 is the closed precedent, and
  citing it as permission fails the DESIGN-GATE §5 checklist).
- A private value or damage formula. `SiegeExpectedDamage` was the named anti-example before it was fixed
  (battle-engine-ssot §4 D7).
- `System.Random`, a clock read, or an unseeded draw anywhere in a decision.
- Changing what the engine **resolves**. This module is entirely on the deciding side of
  `IIntentSource.TryDeclare`.
- Asserting a population count or generated trace text in a test.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** **None, and not a new one.** Deciding is outside the
   closed register by §3c ("battle AI is not battle engine"). This module adds no battle mechanism; it
   changes what an actor *tries* to do, never what happens when it does.
2. **Does it DECIDE or RESOLVE?** **Decide, exclusively.** Its only contact with the engine is the
   shipped seam `IIntentSource.TryDeclare(actorKey, nowTick)` (`IntentSource.cs:29-37`). It touches no
   resolution step.
3. **Mechanism or loop?** **A mechanism** — one scorer, one implementation, every mode. *When* a decision
   is asked for stays each mode's loop: per round in siege and battle (`BasicAttack.cs:175-180`,
   `TimelineDispatch.cs:79-81`), on a trigger edge on the lawn.
4. **Which existing implementation does it extend?** `AiScoring` (`Actions/Ai/CandidateScorer.cs`, moved
   from SiegeAi.cs by CAI1.1) — moved, so there
   is one, not two. It **calls** `UsabilityEvaluator` (`:36-84`), `ActionTagPreference` (`:53-60`),
   `CooldownLedger`, `CostLedger`, `ActionBaseDerivation` (`:19-33`) and `SiegeExpectedDamage` (`:113-116`).
5. **Does every mode get it?** **Yes.** Siege in this module (byte-identical); battle, expedition and
   delve through modules 13 and 14; the lawn through wave 4. There is no "only in battle" clause.
6. **Is it deterministic and seeded?** **Yes.** Argmax reads no RNG; the opt-in weighted pick draws only
   from `SeededRng.DeriveStream` (`SeededRng.cs:9-28`) over an ordinally-sorted set; nothing reads a clock
   or ambient state; policy memory is battle-scoped and rebuilt by replay from tick 0. Decisions are
   deterministic in `(setup, seed, human trace, profile version, BattleEnvironment.Stamp)` — the profile
   version joins replay identity in module 8 (`replay-identity`), which is why that module exists.

## Success criteria

1. `AiScoring` exists in exactly one place, under `gk-core/src/FusionRpg.Core/Actions/Ai/`, and
   `Battle/Siege/SiegeAi.cs` holds no second copy of the additive score.
2. The candidate cap is applied before any per-candidate input is computed, and
   `TargetStageCapTests.Cap_before_work_selects_the_same_candidate_as_cap_after_work` proves the placement
   moved no decision.
3. Commit 1 leaves every siege test unedited and every golden hash unmoved.
4. Commit 2 passes the real `baseOverlayDamage` at `EffectiveRungOf`, with a predicted-delta writeup, and
   `SiegeAiIntentSource.cs:214`'s omission no longer exists.
5. Selection covers argmax + ordinal tie-break (default, RNG-free) and a seeded weighted pick that is
   reproducible from `(runSeed, streamName)`.
6. `RetargetLedger` is the only anti-repeat mechanism, and the commitment bonus and repeat decay live
   inside it.
7. The action stage runs one pass over held actions and reaches `UsabilityEvaluator`, the resolvable-here
   seam, the reserve-floor decorator and the three waste guards — each at its identity default — and
   takes a `runWasteGuards` flag that skips step 4's census entirely when false.
8. `ReserveFloorAffordability` computes `max(authored poise floor, PoiseSpend × reactionsPerRound)` for
   the `poise` id only, and is byte-identical with both reaction arguments at `0`.
9. This module declares **no** `IIntentSource`: the assembling policy is module 3's `CoreIntentPolicy`
   (§5a), and the rank walk is module 2's `AiRowSelector` (§5). Neither is re-implemented here.
10. `python gk-core/scripts/audit-overflow.py --targets A3` reports nothing new; `guard-actor-hub.py` and
    `guard-single-writer.py` green.
11. No file this module writes reads a file, a clock or `System.Random`.

## Open questions

1. **Does `StubIntentSource` survive as a class, or become a profile?** The ideal (§6.1) says it *"may stay
   as the named fallback class, but its gates and ordering are the core's."* Options: (a) keep the class,
   reimplemented over the core with a trivial profile; (b) delete it and have `intent-router` (module 4)
   resolve the trivial profile. **Recommended default: (a) in this module** — the class is named at two
   production fallback sites (`BasicAttack.cs:177`, `TimelineDispatch.cs:80`) and touching those is module
   4's fallback-chain work, not this module's. Deleting it here would fold two causes into one commit.
   **Resolved half:** the related question *"what is the generic scored `IIntentSource`, if not the
   stub?"* is no longer open — it is `CoreIntentPolicy`, owned by module 3 (§5a). This question is now
   only about the stub's own survival, and (a) stands.
2. **Should the row conditions of a profile reuse `ICompiledPredicate`/`FactReader` (gate 5,
   `UsabilityEvaluator.cs:80-81`) instead of a new closed enum?** This is `profile-schema`'s (module 2)
   call and is raised there; it is noted here because the action stage is where the two would meet.
   **Recommended default: a closed enum for v1**, with a stated trigger to revisit.
3. *(Cross-module note, not this module's to specify.)* `TimelineDispatch.Reselect` needs a **target-only**
   re-query for an already-committed action (`TimelineDispatch.cs:75-82` returns `intent.TargetKey`). The
   target stage answers it natively — phases A-C plus selection, with no action stage — but the entry
   point belongs to `intent-router` (module 4). Module 4 should name it explicitly rather than assume a
   full `TryDeclare` covers it.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: battle AI / action selection (DESIGN-GATE §1 rows
    "Anything that changes what happens in a BATTLE" and "Battle / turns").
[x] Session boundary: backlog-clean-up-20260920, recorded at tasks/sessions/backlog-clean-up-20260920.json.
    Paths owned by this lane are the four combat-ai spec files only; no source file is edited.
[x] I read every doc in the §1 row(s) this session: battle-engine-ssot.md (§2, §3c, §4, §5),
    combat-ai-map.md, combat-ai-ideal.md rev 3, research/combat-ai/AUDIT.md, S1, S3, S5,
    tunables-ssot.md §7, DESIGN-GATE §1/§5.
[x] I checked decisions.md for a lock: the "Action selection (battle adoption)" row locks
    bloodthirsty/loyal as engine-side wrappers and names the next RulesetVersion bump trigger.
    Nothing there forbids this module; the bump belongs to module 14.
[x] Every factual claim cites file:line, and every file cited was opened in this session.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-core-scorer.md
    reports no HIGH finding.
[x] I verified claims against CODE, not comments — the two comments that disagree with the design
    (DerivedStatChannels.cs:568-577, DerivedStatRegistry.cs:289-294, both asserting the aggression
    throw is correct) are named as debt in module 6's spec, not quoted as evidence here.
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. NOT DONE, and stated honestly: this is a
    spec lane with a no-build, no-test boundary (SPEC-BRIEF). "Commit 1 is byte-identical" is an
    ARGUMENT from the code, not a measurement — the cap-move identity rests on phase A preserving
    LiveActorKeys order (SiegeAiIntentSource.cs:181-188) and every new lever defaulting to identity.
    TargetStageCapTests is specified precisely so the implementer measures it instead of assuming it.
[x] Nothing contradicts a §2 invariant; the SOLID-S invariant is what this module exists to restore.
[x] Corrections propagate: no doc outside this spec is edited by this lane, and the two stale
    aggression comments are handed to module 6 by name.
[x] No assertion pins a derived-population count or generated text. The two pinned literals are
    ScoreTerm's seven members (a closed vocabulary the code owns) and the siege weight table in
    CandidateScorerTests (a migration-fidelity contract, with the reason stated in the test).
[ ] Event-refreshed cache (§2.16): not applicable — this module introduces no cache. The lawn's
    per-frame derived snapshot is module 15's, and its invalidation set is that spec's to enumerate.
[x] No acceptance criterion fixes an ordering that can vary in real play. The two orderings this
    module DOES fix are named and justified: the checked accumulation order (SiegeAi.cs:115-121)
    and the ordinal tie-break (SiegeAi.cs:143), both already shipped.
[x] Actor combat/derived magnitude: this module CONSUMES Hub output only (ActorDerivedSnapshot via
    IBattleView.DerivedOf, IBattleView.cs:51). It registers no subsystem, invents no channel and
    folds nothing. guard-actor-hub.py has nothing to catch.
[x] Does not invent or extend a SOLID-violating parallel path — it removes the one the audit found.
[ ] A new rule has a registry row. NOT DONE: this module adds no new enforceable rule, so it adds no
    row to gk-core/scripts/enforcement-registry.v1.json. If the program later wants "no second AI scorer"
    guarded mechanically, that guard belongs with module 4 (intent-router), which is where the last
    parallel router is removed. Named here rather than left silent.
```

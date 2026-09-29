# Spec: `ai-tiers-personality` (combat-ai module 3)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `core-scorer` (module 1), `profile-schema` (module 2) ·
**Unblocks:** `action-schedule-twin`, `decision-inspector`, `delve-automated-wiring`,
`auto-policy-switch` · **Status:** **built** (CAI1.9, 2026-09-20): `AiTierResolver`, `AiPersonality`/`AiPersonalityApply` and `CoreIntentPolicy`, with `Nothing_in_tier_resolution_reads_a_difficulty_input` keeping a difficulty lever out.

## Objective

Make a decision's **cost** a property of the profile and a creature's **character** a seeded offset inside
that profile's own bounds — without adding a second implementation of anything.

Two owner rulings drive this and neither is reopened here. **D6:** the tier is decided by the actor's
class — unique creatures run *smart*, general creatures run *performance* — and it is never a difficulty
lever (**D2**: *"in this game we don't make difficulty by AI"*). **D5:** a profile is keyed `place x role`,
and each actor additionally carries a bounded, seeded **personality** that shades the role and never breaks
it. A unique's personality derives from its **instance id**, so it is stable for life and identical in
every match, with nothing stored. A general's derives from `(match seed, actor key)`, so it is reproducible
per match.

The gap this closes is a real one, not a wiring gap. There is no tier concept anywhere today: every actor
in a siege runs the full scorer (`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:743-757` builds one
`SiegeAiIntentSource` for the whole battle), and every actor everywhere else runs the scorer-free
`StubIntentSource` (`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:27-97`, reached via the fallback chain
at `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:175-180`). The cost split exists by accident of *which mode*
an actor is in, not by *what kind of creature* it is. And there is no personality of any kind: no AI
decision in the repo reads a seeded stream at all — `BattleRunState` declares seeded streams for crit,
essence, riders and capture, and none for AI ([S1-battle-core.md](../../research/combat-ai/S1-battle-core.md),
"Determinism").

**The rule that shapes every choice below: a tier is a profile property, not a second implementation.**
Performance is the one core with the scoring stage switched off, the same way `StubIntentSource` is the one
core with a trivial profile (ideal §6.1). Two decision classes would be the SOLID **S** fork this whole
program exists to avoid.

## Tech stack

`FusionRpg.Core` only — new files under `gk-core/src/FusionRpg.Core/Actions/Ai/`, reading module 2's profile and
driving module 1's stages. The personality stream is the shipped `SeededRng`
(`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:9-28`). No new dependency, no store access, no injector work.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AiTier|AiPersonality|CombatAiProfile"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi|ActionSelection"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/tools/tuning/publish.py combat-ai "profiles.*/default.personality.bounds.recklessness=10"
python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-ai-tiers-personality.md --summary
```

## Project structure

| What | Where |
|---|---|
| Tier resolution (profile override, else actor class) | `gk-core/src/FusionRpg.Core/Actions/Ai/AiTierResolver.cs` (new — **landed**, CAI1.9) |
| Personality draw + bounds clamp | `gk-core/src/FusionRpg.Core/Actions/Ai/AiPersonality.cs` (new — **landed**, CAI1.9) |
| Applying a personality to a profile (weights, reserve, aggression) | `gk-core/src/FusionRpg.Core/Actions/Ai/AiPersonalityApply.cs` (new — **landed**, CAI1.9) |
| **The assembling policy** — the `IIntentSource` every non-siege place constructs (§6) | `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs` (new — **landed**, CAI1.9) |
| Performance-tier path through module 1's stages | `gk-core/src/FusionRpg.Core/Actions/Ai/ActionStage.cs` (module 1's file — no edit: module 1 already ships the `runWasteGuards` flag; this module supplies its value) |
| `AiTier`, `PersonalityAxis` — already closed vocabularies | `gk-core/src/FusionRpg.Core/Actions/Ai/AiVocabulary.cs` (module 2's file) |
| `AiActorClass` + the host-supplied resolver delegate | `gk-core/src/FusionRpg.Core/Actions/Ai/AiVocabulary.cs` (module 2's file, one enum added) |
| Tier tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiTierResolverTests.cs` (new — **landed**, CAI1.9) |
| Personality tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiPersonalityTests.cs` (new — **landed**, CAI1.9) |
| Policy-composition tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CoreIntentPolicyTests.cs` (new — **landed**, CAI1.9) |

## The shape

### 1. Tier as a profile property

```csharp
/// D6's class split. Closed, and deliberately two members: "unique creature" and "general creature" are
/// the vocabulary DESIGN-GATE's creature row already fixes, and a third class would be a new concept.
public enum AiActorClass { Unique = 0, General = 1 }

public static class AiTierResolver
{
    /// The one rule. A profile that names a tier wins; otherwise the actor's class decides, through the
    /// file's own `tierByActorClass` map (module 2's schema). Never a difficulty input: nothing here
    /// reads a danger band, a wave number or a side (D2).
    public static AiTier For(CombatAiProfile profile, AiActorClass actorClass) =>
        profile.TierOverride ?? profile.TierByActorClass[actorClass];
}
```

The actor's class comes from a **host-supplied delegate**, never from a store read inside Core:

```csharp
public delegate AiActorClass AiActorClassOf(string actorKey);
```

**The default, when a host supplies nothing, is `Unique`.** That is deliberate and it is what makes this
module byte-identical at landing: with no resolver wired, every actor resolves `Unique` → `smart` → the
full scorer, which is exactly what siege does today (`BattleRunState.cs:743-757` gives every actor the
scoring policy). A default of `General` would silently downgrade every siege actor to a non-scoring path
the day this module merged — a behaviour change disguised as a default. The direction of the default is
therefore a correctness decision, not a taste one, and the spec states it so nobody flips it.

What the class actually *is*, when a host wires it: a **unique creature** is a real `UniqueActor`
specimen — it has a persistent instance id — and a **general creature** has none. The distinction already
exists in the world model: `WorldEntityMember.InstanceId` is documented as *"Roster specimen
(`rpg_unique_actors`); null for non-player forces and guards"*
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:277-280`). So a host's resolver is *"does this actor key map to a
row with an instance id"*, answered on its own side of the DAL boundary. Core never asks.

### 2. What each tier may do

| | **smart** | **performance** |
|---|---|---|
| Who | unique creatures, in every place | general creatures, in every place |
| Target stage | module 1's full pipeline: phase A filters, cap, phase C inputs, tier rank, score, selection | the profile row's **fixed selector only** (`nearest` / `same-lane-then-adjacent`), no scoring inputs computed, no `TopThree` |
| Action stage | gates → resolvable-here → reserve floor → waste guards, at the best rank row | gates → resolvable-here → **reserve floor**, first survivor wins |
| Anti-repeat | commitment bonus + repeat decay + retarget latency | retarget latency only (it is free — one dictionary hit, `Actions/Ai/RetargetLedger.cs:26-36`, moved from `SiegeAiIntentSource.cs` by CAI1.4) |
| Personality | all four axes bite | only the axes with something to move: `Aggression` and `Thrift` |
| Cost envelope | `maxCandidatesScored` x held actions | O(held actions), with no target scan beyond the cached view |

The performance path is **not a second class**. It is module 1's `TargetStage` with `TryBuildCandidate`
never invoked and selection short-circuited to the fixed selector's first result, plus module 1's
`ActionStage` called with `runWasteGuards: false`. Every gate, every ledger and every ordering rule is
the same code. That is the ideal's own framing — *"the core with the scoring stage switched off, the
same way `StubIntentSource` is the trivial profile"* — and it is what keeps one mechanism.

**The branch is module 1's, and this module owns only its value.** `ActionStage.TryPick` takes a
`bool runWasteGuards` parameter, declared and defaulted to `true` by
[spec-core-scorer.md](spec-core-scorer.md) §5 step 4. This module supplies it with one expression, in
`CoreIntentPolicy` (§6) and nowhere else:

```csharp
runWasteGuards: tier == AiTier.Smart
```

That one line is the whole of the tier's effect on the action stage. It is a `bool` rather than an
`AiTier` because `AiTier` is module 2's vocabulary and module 2 depends on module 1 — module 1 taking
the enum would invert the map's arrow (module 1's own Boundaries state the refusal).

**Why the reserve floor survives into performance tier and the waste guards do not.** The floor is a
single affordability comparison inside gate 3, which every tier runs anyway (module 1's
`ReserveFloorAffordability` decorates the check `UsabilityEvaluator.cs:66-67` already makes), so it costs
nothing extra and it is the one guard that prevents the *hoarding-or-starving* failure S5 documents. The
waste guards need a live-count census or an expected-damage estimate, which is exactly the work the
performance tier exists not to do — **and skipping them is a code branch, not authored thresholds.**
Authoring `minTargetsForArea`/`killMarginMilli`/`fightEndingLiveCount` at identity would still pay for
the census and then answer "pass"; the branch does not run it at all. Both levers exist, they are not
the same lever, and a profile may use the thresholds on top of the branch.

### 3. Personality — bounded, seeded, stored nowhere

```csharp
/// One actor's offsets, one per axis, always inside the profile's own bounds.
public readonly record struct AiPersonality(IReadOnlyList<int> OffsetByAxis);

public static class AiPersonalityFactory
{
    /// A unique's personality is a function of its instance id alone: stable for life, identical in
    /// every match, in every place, with NOTHING STORED. No new RNG type and no new public API on
    /// SeededRng — DeriveStream(0, name) is exactly `0 ^ Fnv1a64(name)`, a pure function of the name
    /// (SeededRng.cs:9-28).
    public static AiPersonality ForUnique(string instanceId, AiPersonalityBounds bounds) =>
        Draw(SeededRng.DeriveStream(0UL, "ai.personality:" + instanceId), bounds);

    /// A general creature has no instance id, so its personality is a function of the match it is in.
    /// Reproducible per match, and covered by replay identity because the match seed is already part of
    /// (setup, seed).
    public static AiPersonality ForGeneral(ulong matchSeed, string actorKey, AiPersonalityBounds bounds) =>
        Draw(SeededRng.DeriveStream(matchSeed, "ai.personality:" + actorKey), bounds);

    static AiPersonality Draw(SeededRng rng, AiPersonalityBounds bounds)
    {
        var offsets = new int[PersonalityAxisCount];
        for (var axis = 0; axis < PersonalityAxisCount; axis++)
        {
            var bound = bounds.BoundByAxis[(PersonalityAxis)axis];
            // ALWAYS draw, even at bound 0. See "the draw-order contract" below.
            var span = checked(2 * bound + 1);
            offsets[axis] = rng.NextInt(span) - bound;     // unbiased: SeededRng.cs's rejection sampling
        }
        return new AiPersonality(offsets);
    }
}
```

**The draw-order contract**, which is the part an implementer will otherwise get wrong:

1. **Axes draw in `PersonalityAxis` declaration order**, one value each. Two draws from one stream are
   order-dependent, so the order is a contract and the enum is **append-only** (module 2 states that).
2. **Every axis draws unconditionally, including at bound 0**, where `NextInt(1)` always returns 0. This
   costs one cheap call and buys a real property: changing one axis's bound in tuning does not shift any
   other axis's value. Skipping a zero-bound axis would make a balance edit to `recklessness` silently
   re-roll every creature's `thrift`, which is a reproducibility bug nobody would attribute correctly.
3. **The stream name embeds the identity, not the seed.** `"ai.personality:" + instanceId` keeps every
   actor's stream independent, so an extra draw for one actor never shifts another's — the property
   `SeededRng`'s own summary claims for per-system streams (`SeededRng.cs:3-9`).

**What each axis moves**, and each one lands somewhere that already has a bound:

| Axis | Applies to | Direction | Where the result is bounded |
|---|---|---|---|
| `Aggression` | the actor's own contribution to the effective tier | + pulls it toward engaging; − toward caution | **saturated into the closed tier range** by module 6 (`aggression-tier-map`) — it can never leave the vocabulary |
| `Recklessness` | `weightRisk` | + lowers risk aversion | clamped to the profile's own min/max for that weight, and a negative AUTHORED weight is refused at parse — `CombatAiTuningLoader.NonNegativeWeight` (`gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiTuningLoader.cs:198-206`) checks all seven weights and names the key, restored by `CAI-find-2` (2026-09-23) after CAI1.8's key move dropped the refusal the old `SiegeTuning` reader carried. The clamp remains the POLICY's (`AiPersonalityApply.ClampNonNegative`) and bounds the RESULT |
| `Focus` | `weightLowHp` and `weightKill` together | + focuses the weak and the finishable | clamped to the profile's min/max |
| `Thrift` | every reserve floor's `FloorMilliOfMax` | + hoards, − spends | clamped to the bounded ratio 0..1000 |

**A personality shades a role and never breaks it.** The offset is applied, and then the result is clamped
to the profile's own min/max for that lever. Both steps are required: the bound limits the *draw*, the
clamp limits the *result*, and a profile that sets a tight range still gets a tight range even if a bound
is authored too wide.

### 4. Where personality is computed, and how often

**Once per actor per battle**, at the same point the policy is constructed — beside
`BattleRunState.cs:743-757`, where the AI source is already built once and reused for the whole battle.
Never per decision: a per-decision draw would advance the stream and make the second decision differ from
the first for no reason, and it would allocate on the hot path.

On the lawn (wave 4) the same rule applies per actor, computed when the actor's held-action set is frozen,
and withdrawn with the rest of the actor's AI state before a `ptr` is reused
(`overlay-control-loops.md` §6 rule 4, restated in the ideal §3 principle 5).

### 5. Identity at landing

Every bound ships at **0** in `combat-ai.v1.json` (module 2's identity posture), so every offset is 0, the
applied profile equals the authored profile, and no decision moves. The actor-class resolver is unwired, so
every actor is `Unique` → `smart` → today's siege behaviour. **This module is byte-identical on the day it
lands**, and turning either half on is a later, separately-caused commit with its own predicted-delta
writeup — the same H1 discipline module 1 and module 2 follow.

### 6. `CoreIntentPolicy` — the one composition entry point, and why it is this module's

Modules 1 and 2 ship **building blocks**: `TargetStage`, `ActionStage`, `ReserveFloorAffordability`,
`RetargetLedger`, `CombatAiProfile`, `AiRowSelector`. None of them is an `IIntentSource`. Siege needs no
wrapper — `SiegeAiIntentSource` stays consumer #1 (module 1 §"Objective") — but **every other place
does**: `delve-automated-wiring` (13) and `auto-policy-switch` (14) both need a generic scored policy,
and the lawn reaches the same one through module 19's loop. A type two specs assume and none declares is
the gap this section closes.

**Ownership, decided and stated.** It is **this module's**, not module 1's. Assembling a policy needs a
`CombatAiProfile` (module 2's type) *and* an `AiTier`/`AiPersonality` (this module's). Module 1's
dependency line is *"Depends on: nothing"* and module 2 depends on module 1, so declaring the type in
module 1 would invert the map's own arrow. This module is the first that already depends on both, so it
is the first place the type can legally live.

```csharp
namespace FusionRpg.Core.Actions.Ai;

/// The ONE scored IIntentSource for every non-siege place. It composes; it decides nothing itself.
/// Constructed ONCE per actor-set per battle, beside BattleRunState.cs:743-757 where the view,
/// Cooldowns, CostLedger and the stance seam already are (`RaidIntentSource.cs:13-20`: no external
/// caller of BattleEngine.Resolve ever holds an IBattleView, so this cannot be built outside).
public sealed class CoreIntentPolicy : IIntentSource
{
    public static CoreIntentPolicy Create(
        IBattleView view,                       // the run state itself
        CooldownLedger cooldowns,
        IStanceCheck stance,                    // module 11's BattleRunState.Stance seam
        IAffordabilityCheck affordability,      // the real CostLedger; the reserve floor decorates IT
        string profileId,                       // resolved through CombatAiProfilePolicy.For (module 2 §3)
        AiActorClassOf? actorClassOf = null,    // §1; null => every actor is Unique => smart
        ulong matchSeed = 0UL,                  // §3, for a general creature's personality
        RetargetLedger? retarget = null,        // null => a fresh battle-scoped ledger
        Func<string, string>? loyalRedirect = null,   // module 4's ITraitDecorator.EffectiveTargetOf
        Action<TracedDecision>? trace = null);        // module 10's seam; null => no trace

    public ActionIntent TryDeclare(string actorKey, long nowTick);

    /// Target-only re-query for an already-committed action — module 4's `RetargetFor` delegates here
    /// (`ActionRunner.cs:393-396`'s contract). Runs the target stage alone: no action stage, no row
    /// walk past the row that chose the selector.
    public string? RetargetFor(string actorKey, string actionId, string? deadTargetKey, long nowTick);
}
```

**What one `TryDeclare` does, in order.** Every step is somebody else's mechanism; this type is the
sequence and nothing else:

1. `CombatAiProfilePolicy.For(place, role)` → the `CombatAiProfile` (module 2 §3), resolved once per
   actor and cached on the per-actor state, never per decision.
2. `AiTierResolver.For(profile, actorClassOf?.Invoke(actorKey) ?? AiActorClass.Unique)` (§1).
3. `AiPersonalityApply` of the per-actor personality drawn once at construction (§3, §4) → the applied
   profile. At all-bounds-0 this is the authored profile, field for field.
4. `AiRowSelector.TryPick(profile, facts, …)` (module 2 §4) → a `TargetSelector`, an `AiActionFilter`
   and a `rankIndex`. The census facts that walk needs are gathered **once**, here, before the call.
5. `TargetStage` phases A→B→C + `SelectionPolicy` (module 1 §3, §4) → one target key. At performance
   tier the fixed selector short-circuits it and `TryBuildCandidate` is never invoked (§2).
6. `ActionStage.TryPick(actorKey, targetKey, filter, out actionId, runWasteGuards: tier == AiTier.Smart)`
   (module 1 §5).
7. `RetargetLedger.RecordRetarget` + the optional `trace` callback, then `new ActionIntent(...)` — or
   `ActionIntent.None` when any step yields nothing. Never a nullable intent
   (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:12-18`).

**Identity at landing.** With no class resolver, all personality bounds `0`, and a profile carrying
module 2's identity levers, `CoreIntentPolicy` produces the same target and action the shipped stack
produces for the same inputs — but **nothing in production constructs it in this module's commit**.
Siege keeps `SiegeAiIntentSource`; module 13 is its first production caller. So this module stays
byte-identical for the reason module 1 and 2 are: the new path exists and nothing walks it yet.

**Boundary, stated because it is the tempting shortcut.** `CoreIntentPolicy` holds no scoring
arithmetic, no gate, no cost read and no row-walk logic of its own. If a reviewer finds a comparison of
two candidates' scores inside this file, the composition has grown a second scorer and the change is
wrong.

## Tunables

No new file. Everything lives in module 2's `gk-core/data/tuning/combat-ai.v1.json`, published `v{n+1}` through
`gk-core/tools/tuning/publish.py`.

| Key | v1 value | Unit | Why this seed |
|---|---|---|---|
| `profiles["*/default"].tierByActorClass.unique` | `"smart"` | enum | D6 |
| `profiles["*/default"].tierByActorClass.general` | `"performance"` | enum | D6 |
| `profiles["siege/default"].tierOverride` | `"smart"` | enum | siege scores every actor today; an explicit override makes the migration's byte-identity independent of whether a host ever wires a class resolver |
| `profiles["*/default"].personality.bounds.aggression` | 0 | tier offset, +/- | identity at landing; also the safest axis to leave at 0 longest, because it interacts with a closed vocabulary |
| `.personality.bounds.recklessness` | 0 | weight offset, +/- | identity |
| `.personality.bounds.focus` | 0 | weight offset, +/- | identity |
| `.personality.bounds.thrift` | 0 | per-mille offset, +/- | identity |

**Structural, not tunable:** the number of personality axes (a closed vocabulary), the draw order (a
determinism contract), and the two-member `AiActorClass` enum. Each carries a comment saying so, per
`AGENTS.md`'s no-hard-ceiling rule's requirement that a structural limit states why it is one.

**Not a cap:** a personality bound limits an *offset into a designed range*, not a magnitude an actor can
grow. It is a bounded ratio of a designed band, which the rule exempts explicitly, and the code says so at
the field.

## Code style

- **No allocation on the decision path.** The personality is computed once and held; `AiPersonalityApply`
  produces a `CombatAiProfile` once per actor per battle, not per `TryDeclare`.
- **`checked` on `2 * bound + 1`.** A bound authored absurdly large is a configuration error that should
  throw at parse (module 2's loader range-checks it), and the arithmetic is `checked` anyway.
- **Never `System.Random`.** Only `SeededRng.DeriveStream` (`SeededRng.cs:9-28`), as
  `BattleRunState` already does for crit, essence, riders and capture.
- **No clock, no ambient state, no store read** anywhere in this module — the §3c determinism boundary.
- **A comment at every structural declaration** naming what it is and why.

## Testing strategy

Contracts and closed vocabularies only.

**`AiTierResolverTests`**
- ✅ `Profile_override_wins_over_actor_class`.
- ✅ `Unique_resolves_smart_and_general_resolves_performance` — D6's rule, from the file's own map.
- ✅ `Unwired_class_resolver_defaults_to_unique` — the byte-identity default, asserted so a later change
  of direction fails loudly.
- ✅ `AiActorClass_has_two_members` and `AiTier_has_two_members` — closed vocabularies the code owns,
  pinned with the reason in the test.
- ✅ `Nothing_in_tier_resolution_reads_a_difficulty_input` — a signature assertion: `For` takes a profile
  and a class and nothing else (D2 made structural, not promised in prose).

**`AiPersonalityTests`**
- ✅ `Same_instance_id_gives_the_same_personality` — two draws, two processes' worth of construction, and
  two different match seeds all agree. This is D5's *"stable for life, with no storage"*.
- ✅ `Same_match_seed_and_actor_key_give_the_same_personality`, and
  `Different_actor_keys_draw_independently`.
- ✅ `Every_offset_is_inside_its_bound` — over a generated table of bounds.
- ✅ `Changing_one_axis_bound_does_not_shift_another_axis` — the draw-order contract, asserted directly.
  Without this test the unconditional-draw rule is a comment nobody enforces.
- ✅ `All_bounds_zero_is_byte_identical` — the applied profile equals the authored profile, field for
  field.
- ✅ `Applied_offsets_are_clamped_to_the_profile_range` — a bound wider than the profile's own min/max
  still produces an in-range profile.
- ✅ `Aggression_offset_never_leaves_the_tier_vocabulary` — delegated to module 6's saturation; the test
  asserts the composition, not a second clamp.
- ❌ Never assert a specific drawn offset value for a specific id. That is generated content: the contract
  is *reproducible and in-bounds*, not *equal to 3*.

**`PerformanceTierTests`** (in module 1's `ActionStageTests` file, since it is module 1's code path)
- ✅ `Performance_tier_computes_no_candidate_inputs` — a counting `TryBuildCandidate` fake is never
  invoked. **Counted, not timed** — a timing assertion is a flake, and the repo's zero-allocation
  acceptance lines are counted too (`StubIntentSource.cs:22-25`).
- ✅ `Performance_tier_still_runs_the_reserve_floor_and_the_six_gates`.
- ✅ `Performance_tier_and_smart_tier_share_one_ledger_and_one_gate_set` — asserted by construction: both
  paths take the same `CooldownLedger` and `IAffordabilityCheck` instances.

**`CoreIntentPolicyTests`** (§6)
- ✅ `A_declaration_runs_the_seven_steps_in_order` — a recording fake for each collaborator asserts the
  sequence of §6, not the numbers each one returned. The order is the contract; the numbers are theirs.
- ✅ `The_profile_is_resolved_once_per_actor_and_not_once_per_decision`, and
  `The_census_is_gathered_once_per_decision_and_not_once_per_row` — both counted with fakes. These are
  the two costs a naive composition adds, so they are asserted rather than hoped for.
- ✅ `Tier_smart_passes_runWasteGuards_true_and_performance_passes_false` — the one-line mapping §2
  names, pinned so a later edit cannot silently invert it.
- ✅ `RetargetFor_runs_the_target_stage_alone_and_never_the_action_stage` — module 4's `RetargetFor`
  contract, asserted where it is implemented.
- ✅ `A_step_that_yields_nothing_returns_ActionIntent_None_and_never_throws`.
- ✅ `No_scoring_arithmetic_lives_in_this_type` — a source scan of `CoreIntentPolicy.cs` finds no
  comparison of two candidates' scores. The Boundary in §6 made mechanical, because it is the one
  failure this composition invites.
- ❌ Never assert which action a real corpus profile picked, or how many rows it walked.

**Golden impact: byte-identical.** All bounds 0, the class resolver unwired, `siege/default` carrying an
explicit `smart` override. `BattleGoldenTests` and `ExpeditionResolverTests.Tier_goldens_are_locked`
unchanged and unblessed. If a golden moves, this module is wrong.

## Boundaries

**Always**
- Keep performance as *the same core with a stage off*, sharing every gate, ledger and ordering rule.
- Draw every axis, in declaration order, from one per-actor stream.
- Compute a personality once per actor per battle.
- Clamp the applied result to the profile's own range, not only the draw to its bound.
- Default an unwired class resolver to `Unique`.

**Ask first**
- A third tier. The ideal reserves a "dumb" variant and D6 defers vanilla control to a later program; a
  third member is a reviewed vocabulary change, not an implementation detail.
- A fifth personality axis (append-only, and it shifts nothing — but it is still a vocabulary change).

**Never**
- Put scoring arithmetic, a gate, a cost read or a row-walk inside `CoreIntentPolicy`. It composes; the
  moment it compares two candidates it has become a second scorer.
- A second decision class, a `if (tier == Performance)` branch that re-implements a gate, or a
  performance-only ledger. That is the SOLID **S** fork the program exists to remove.
- A difficulty input of any kind — side, wave number, danger band, player rank — reaching tier or
  personality (**D2**). The resolver's signature is the enforcement.
- Storing a personality. A unique's is a function of its instance id; persisting it would create a second
  source of truth that can drift from the id.
- `System.Random`, a clock, or a per-decision draw.
- Asserting a drawn value for a given id in a test.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** **None.** Tier and personality shape *how much work a
   decision does* and *which way it leans*. Both are deciding, and §3c puts deciding outside the engine.
   Nothing is added to the closed register.
2. **Does it DECIDE or RESOLVE?** **Decide.** It never touches a resolution step; it configures module 1's
   stages before they produce an `ActionIntent` for `IIntentSource.TryDeclare`
   (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:29-37`).
3. **Mechanism or loop?** **A mechanism.** One tier rule and one personality rule for every place. What
   changes per place is only *when* the decision is asked for.
4. **Which existing implementation does it extend?** `SeededRng.DeriveStream`
   (`SeededRng.cs:9-28`) for the draw — no new RNG and no new public API; module 1's `TargetStage` /
   `ActionStage` for the tier path; module 2's `CombatAiProfile` for the data. It re-implements none of
   them.
5. **Does every mode get it?** **Yes.** The tier rule is by actor class, not by place, which is the whole
   point of D6 — a unique creature is smart on the lawn, in a delve, in a siege and in a web battle. Every
   place therefore needs a class resolver; a place that wires none keeps today's behaviour rather than
   getting a different rule.
6. **Is it deterministic and seeded?** **Yes, and this is the first AI use of a seeded stream in the
   repo.** A unique's personality is a pure function of its instance id; a general's of `(match seed,
   actor key)`. Both use `SeededRng.DeriveStream` and neither reads a clock. The draw is reproducible on
   replay because the match seed is already part of `(setup, seed)`, and the personality *bounds* are part
   of the profile version, which joins replay identity in module 8 (`replay-identity`). The tier rule
   reads no RNG at all.

## Success criteria

1. `AiTierResolver.For(profile, actorClass)` is the only place a tier is decided, and it takes no
   difficulty input.
2. An unwired class resolver yields `Unique`, and `AiTierResolverTests.Unwired_class_resolver_defaults_to_unique`
   pins it.
3. The performance tier computes no candidate inputs — proven by a counting fake, not by timing — and
   still runs all six gates, the resolvable-here filter and the reserve floor.
4. A unique's personality is reproducible from its instance id alone, across matches and across
   constructions, with nothing stored.
5. A general's is reproducible from `(match seed, actor key)`.
6. Every axis draws unconditionally in declaration order, and
   `Changing_one_axis_bound_does_not_shift_another_axis` passes.
7. Every offset is inside its bound, and every applied lever is inside the profile's own range.
8. With all bounds at 0 and no class resolver wired, every golden hash is unmoved and no existing test is
   edited.
9. `CoreIntentPolicy` exists, is the **only** assembling scored `IIntentSource` in the repo, runs §6's
   seven steps in that order, resolves the profile once per actor and the census once per decision, and
   holds no scoring arithmetic of its own (proven by the source scan, not asserted in prose).
10. Nothing in production constructs `CoreIntentPolicy` in this module's commit — module 13 is its first
    caller — so the new path exists and nothing walks it yet.
11. No `System.Random`, no clock read, no store read, and no per-decision allocation in this module.

## Open questions

1. **Who supplies `AiActorClassOf` in each place, and when?** The delegate is Core-side; the answer is
   host-side and differs per place (battle and expedition through `WebMatchService`, delve through the
   session, siege through `DistrictAssaultResolver`, lawn through the injector's deploy path). Options:
   (a) each wiring module supplies it as part of its own commit (`delve-automated-wiring`,
   `siege-loadout-wiring`, wave 4); (b) one shared resolver built from the roster. **Recommended default:
   (a)** — a shared resolver would need a roster read inside Core, which the DAL boundary forbids, and
   each place already holds the setup that knows the answer. Named here because leaving it implicit is how
   a default of `General` sneaks in.
2. **Does a personality persist for a general creature across an expedition's several encounters?** A
   general's stream is `(match seed, actor key)`, so it is stable within one match by construction; whether
   an expedition's successive encounters share one match seed was not verified in this session. Options:
   (a) stable within an encounter, re-drawn per encounter; (b) stable across the whole expedition.
   **Recommended default: (a)**, because it needs nothing new and is what falls out of the seed the
   encounter already has. Flagged rather than asserted, because I did not open the expedition resolver.
3. *(Cross-module note.)* The `Aggression` axis writes into the same quantity the `ai.aggression` derived
   channel feeds (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:568-577`). Module 6
   (`aggression-tier-map`) must saturate the **sum** of the channel and the personality offset, not the
   channel alone — otherwise a +2 channel plus a +1 personality throws exactly where module 6 exists to
   stop it throwing. Module 6's spec states this; it is repeated here so the two are not implemented
   against different assumptions.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: battle AI (DESIGN-GATE §1 "Anything that changes what
    happens in a BATTLE"), plus the creature vocabulary row for unique vs general.
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json). This
    lane writes four spec files and edits no source.
[x] I read every doc in the §1 row(s) this session: battle-engine-ssot.md §2/§3c/§5, combat-ai-map.md,
    combat-ai-ideal.md rev 3 (§6.2a carries D1-D6), AUDIT.md, S1, S3, S5, DESIGN-GATE §1 row 48
    (general vs unique creature vocabulary) and §5.
[x] I checked decisions.md for a lock: nothing locks AI tiering or personality. The Deployment
    hierarchy row's unique/general distinction is consistent with the class split used here.
[x] Every factual claim cites file:line, and every file cited was opened this session: SeededRng.cs,
    BattleRunState.cs, BasicAttack.cs, StubIntentSource.cs, SiegeAiIntentSource.cs, IntentSource.cs,
    UsabilityEvaluator.cs, WorldState.cs, DerivedStatChannels.cs, SiegeTuning.cs.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-ai-tiers-personality.md
    reports no HIGH finding.
[x] I verified claims against CODE, not comments. "No AI decision reads a seeded stream today" comes
    from S1's own grep-backed row plus reading BattleRunState's AI construction at :627-630, not from
    the ideal's prose.
[~] I tested (not assumed) any constraint I am reporting. NOT DONE — spec lane, no builds or tests
    (SPEC-BRIEF). "Byte-identical at landing" is an argument from three facts (bounds 0, resolver
    unwired defaulting to Unique, siege carrying an explicit smart override), not a measurement. The
    tests named above are specified so the implementer measures each one.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagate: the aggression/personality interaction is handed to module 6 by name in
    Open questions, and the per-place class resolver to the three wiring modules by name.
[x] No assertion pins a derived-population count or generated text. Pinned literals are AiTier's and
    AiActorClass's member counts (closed vocabularies). The tests explicitly REFUSE to assert a drawn
    offset value for a given id, which would be generated content.
[ ] Event-refreshed cache (§2.16): not applicable. The personality is computed once per actor per
    battle and is not a cache — it is never invalidated, only withdrawn with the rest of the actor's
    AI state before a lawn ptr is reused (wave 4's rule, named here, specified there).
[x] No acceptance criterion fixes an ordering that can vary in real play. The one fixed order — the
    personality draw order — cannot vary (it is the enum's declaration order) and is tested.
[x] Actor combat/derived magnitude: this module CONSUMES one Hub channel (ai.aggression, read through
    IBattleView.AggressionOf) and produces none. It registers no subsystem, invents no channel, and
    folds nothing. A personality offset is a POLICY number, not an actor stat, and it never enters the
    Hub compose.
[x] Does not invent or extend a SOLID-violating parallel path. The performance tier is explicitly the
    same code with a stage off, and "never a second decision class" is a stated Boundary.
[ ] A new rule has a registry row. NOT DONE: this module adds no mechanically-guardable rule. The two
    rules it does add - "no difficulty input reaches tier resolution" and "personality is never
    stored" - are enforced by signature and by the absence of a persistence call, and are asserted by
    AiTierResolverTests. Stated rather than silently skipped; if the program later wants a guard, the
    natural one is a source scan for `System.Random` under Actions/Ai/, which belongs with module 7.
```

# Spec: `intent-router` (combat-ai module 4)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) rev 3 ·
**Depends on:** `core-scorer` (module 1) · **Unblocks:** `decision-perf` (7), `decision-inspector` (10),
`stance-wiring` (11), `delve-automated-wiring` (13), `commander-direct-orders` (20) ·
**Status:** **built** (CAI1.10 + CAI1.11, 2026-09-20). `Actions/IntentRouter.cs` is the one chain — both older routers were deleted (`Delve/Battle/RaidIntentSource.cs` whole-file, and `SiegeAi.cs`'s `SiegeIntentSource`), and `ITraitDecorator`s now reach every policy, so the reselect site resolves through the same router instead of a second expression. `IntentRouterTests` and `TraitDecoratorTests` cover both halves.

## Objective

There were two identical routers in the tree and neither routed anything else. `RaidIntentSource`
(was src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs, whole file) and `SiegeIntentSource`
(was inside `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs`) — both DELETED 2026-09-20 by this module's
own CAI1.10 commit (zero production callers confirmed for the latter via
`DistrictAssaultResolver.cs`'s own doc comment) — were the same four lines — *steered key set → player
source, everything else → the automated source* — written twice, in two subsystem namespaces, each with a
doc comment explaining that it copies the other. Lane S1 named this as the one real duplication in the
decision layer, and the lawn's direct orders (D3) would be its third copy. **This module replaces both
with one router in `Core/Actions/`.**

Dedup is the cheap half. The expensive half is that **four separate decisions about *who decides* are
made in four places, and they disagree**:

| Decision | Where it is made today | The defect |
|---|---|---|
| The fallback chain | was `BasicAttack.cs:175-180`, now `BasicAttack.cs:175-180` — `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)` | and `TimelineDispatch.cs:79-80` `intentSource ?? new StubIntentSource(...)` — **`state.DefaultAiIntentSource` is omitted**, so a reselect silently drops the mode's own policy (audit M5) |
| Retarget for an already-committed action | `ActionRunner.cs:393-396` calls a `Func<string, string?, string?>` supplied at `TimelineDispatch.cs:85-89` | A *target-only* second query with no owner. `Reselect` (`:68-83`) re-derives the whole chain by hand, which is why it drifted from `BasicAttack`'s |
| Trait decorators | `BasicAttack.cs:152` builds `BloodthirstyViewFor` and hands it **only** to the stub at `:165`; the `loyal` bodyguard redirect ran **after** the decision (was `:190-192`; now `LoyalTargetRedirect`, `BasicAttack.cs:571-595`) | An injected or mode policy gets the raw view, so a trait a species really carries is silently dropped for that policy (audit M1). The post-decision `loyal` redirect means a scorer's kill and low-HP terms scored an actor the engine then did not hit |
| A player order | Nowhere. `InteractiveIntentSource` (`:119-145`) replaces the whole policy for an actor; there is no "order this one creature, AI resumes underneath" | D3 requires both, and a second decision system for the second kind is the shape this program exists to avoid |

The router owns all four, once, for every place. It also states the boundary the ideal drew around engine
reactions: `TimelineDispatch.cs:241-253` counters **whenever `poise` pays**, consulting no policy
(`ReactionCounter.TryCounter`, `gk-core/src/FusionRpg.Core/Battle/Timeline/ReactionCounter.cs:38-45`). That stays
automatic, and profiles are told so, or every `poise` reserve floor is defeated by a spend the profile
never authorised (audit M6).

This module changes no scoring and no resolution. It changes **which policy object answers
`IIntentSource.TryDeclare`** (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:29-37`), and **what
view that policy sees**.

## Tech stack

`FusionRpg.Core` only — `Core/Actions/` for the router, and edits at the four seam call sites under
`Core/Battle/`. No new dependency. Two tuning keys in `gk-core/data/tuning/combat-ai.v1.json` (new; the file is
`profile-schema`'s, module 2) published through `gk-core/tools/tuning/publish.py`. No injector work: the lawn
adapter (module 20) consumes this router from `Core`, because CI never builds the injector
(`combat-ai-ideal.md` §3 principle 5).

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouter|IntentSource|ActionSelection|SiegeAi|Raid"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"
python gk-core/scripts/guard-battle-responsibility.py
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/tools/tuning/publish.py combat-ai router.orderTimeoutTicks=5000
```

## Project structure

| What | Where |
|---|---|
| The router | `gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs` (new — **landed**, CAI1.10) |
| Decorator + redirect contracts | `gk-core/src/FusionRpg.Core/Actions/IIntentDecorator.cs` (new — **landed**, CAI1.10) |
| Direct order + queue contract | `gk-core/src/FusionRpg.Core/Actions/DirectOrder.cs` (new — **landed**, CAI1.10) |
| Engine-side decorators (moved, not rewritten) | `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` — `BloodthirstyViewFor` (`:475-485`), `BloodthirstyView` (`:489-515`) and `FindAdjacentWithTrait` (`:190`) become the two `ITraitDecorator`/`ITargetRedirect` implementations, still declared inside `BattleEngine` |
| Chain call site 1 | `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:152,175-180` |
| Chain call site 2 (the reselect defect) | `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs:68-83,85-89` |
| Router construction | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:743-757` (the `aiTuning != null` block where `DefaultAiIntentSource` is built today; its field is declared at `:162`) |
| Deleted: siege router | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:220-239` |
| Deleted: delve router | `src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs` (whole file; `KeysForParty` at `:49-50` moves to the router as a static helper) |
| Tuning rows | `gk-core/data/tuning/combat-ai.v1.json` (new; module 2 owns the file, this module owns its `router` block) |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/IntentRouterTests.cs` (new — **landed**, CAI1.10) |

## The shape

### 1. The router

```csharp
/// One router, every place. It decides WHO answers TryDeclare for an actor and WHAT view that
/// answer is computed against. It never scores, never gates and never resolves.
public sealed class IntentRouter : IIntentSource
{
    public IntentRouter(
        IIntentSource policy,                        // the mode's profiled policy (module 1+3)
        IIntentSource? fallback = null,               // the default — StubIntentSource's role today
        IIntentSource? steered = null,               // player source (interactive / raid steered party)
        IReadOnlySet<string>? steeredKeys = null,    // precomputed BEFORE the battle; never a live view read
        IReadOnlyList<ITraitDecorator>? decorators = null,
        IOrderQueue? orders = null,
        long orderTimeoutTicks = 0,
        Func<DirectOrder, ActionIntent?>? forcedIntent = null,   // `CAI4.9` row 14: the order arm's hook
        IAiDecisionSink? sink = null);                           // `CAI2.4`: every arm records through it

    public ActionIntent TryDeclare(string actorKey, long nowTick);

    /// The retarget-for-a-FIXED-action entry ActionRunner needs (`ActionRunner.cs:393-396`): the
    /// action is already committed, only its target is in question. Returns null to fizzle.
    public string? RetargetFor(string actorKey, string actionId, string? deadTargetKey, long nowTick);

    /// RaidIntentSource.KeysForParty, moved verbatim — still built from BattleSetup.Squad before
    /// Resolve runs, never re-derived from a live IBattleView.
    public static IReadOnlySet<string> KeysForParty(BattleSetup setup, int partyIndex);
}
```

#### 1a. `Compose` — the one construction entry point every caller uses

**This module owns exactly one construction signature, and every other spec cites it rather than
restating it.** Two downstream specs construct routers — `delve-automated-wiring` (13) and
`commander-direct-orders` (20) — and a constructor is the wrong shape for both, for one concrete
reason: **the delve's player source cannot exist before the automated policy does.**
`InteractiveIntentSource` takes the automated policy as its *timeout fallback* and records the
fallback's choice into the trace as `DecisionSource.Timeout`
(`gk-core/src/FusionRpg.Core/Battle/Timeline/InteractiveIntentSource.cs:139-146`). Passing an
already-built `steered` would force the caller to invert that wrap, which skips the `Record` call and
silently breaks replay of an AFK turn. So `steered` is supplied as a **factory of the policy**:

```csharp
/// The ONE way a router is constructed. `BattleRunState` calls it where the view exists
/// (BattleRunState.cs:743-757); nothing outside the engine ever does (RaidIntentSource.cs:13-20).
/// Every parameter after `policy` is optional and its omission is today's behaviour.
public static IntentRouter Compose(
    IIntentSource policy,                                  // the mode's profiled policy (module 1 + 3)
    IIntentSource? fallback = null,                        // see "what fallback null means" below
    Func<IIntentSource, IIntentSource>? steeredSourceFor = null,   // policy in, player source out
    IReadOnlySet<string>? steeredKeys = null,              // precomputed; never a live view read
    IReadOnlyList<ITraitDecorator>? decorators = null,
    IOrderQueue? orders = null,
    long orderTimeoutTicks = 0,
    IAiDecisionSink? sink = null,                          // `CAI2.4`: forwarded to the constructor
    Func<DirectOrder, ActionIntent?>? forcedIntent = null);  // `CAI4.9` row 14
```

**Corrected 2026-09-23 (lane `cai3`): the two signatures above now match the code, and one sentence below
no longer does.** `forcedIntent` (`CAI4.9` row 14) and `sink` (`CAI2.4`) are both trailing and optional, so
every caller this spec shows still compiles. The per-arm recording wrap lives in the **CONSTRUCTOR**, not
here: measured, with it in `Compose` a caller using the public constructor directly with a sink got the
ORDER arm recorded and the three source arms silent, so "every arm records" holds for every construction
path. `Compose` therefore still invokes `steeredSourceFor(policy)` once and hands the result in as
`steered` — but "the constructor stays exactly as declared" is no longer literally true, which is why this
note is here rather than in the constructor's own block.

`Compose` invokes `steeredSourceFor(policy)` once, then hands the result to the constructor above as
`steered`. The constructor stays exactly as declared — a built `steered`, a built `fallback` — because
the inversion is a one-line concern and it belongs in one place. This is the resolution of
`delve-automated-wiring`'s Open question 1, decided here, in the spec that owns the seam:
**option (b) of that question, with the inversion inside `Compose` rather than open-coded in
`BattleRunState`.**

**What `fallback: null` means, stated rather than left to the implementer.** It means **the chain has
no step 4** and the router returns `ActionIntent.None` when `policy` declares nothing. It does **not**
mean "build a `StubIntentSource` for me": a stub needs an `IBattleView`, a `CooldownLedger`, an
`IStanceCheck` and a `CostLedger` (`BasicAttack.cs:175-180`), which only `BattleRunState` holds, so
inventing one inside `Compose` is impossible and pretending otherwise would hide the dependency.

| Caller | `fallback` | Why |
|---|---|---|
| `BattleRunState`, every turn-based place | `new StubIntentSource(view, state.Cooldowns, state.Stance, state.CostLedger)` — today's literal | preserves `BasicAttack.cs:175-180`'s chain exactly |
| The lawn (module 20's queue, module 19's loop) | `null` | the lawn's loop has already decided the actor is *due*; there is no second policy underneath, and a stub that re-picks "nearest enemy, first usable action" would be a second lawn decision path |
| A test | whatever it is testing | — |

**Ordering note for callers:** the arguments are named, not positional. A call that reads
`Compose(steered, automated, steeredKeys)` is wrong in this spec's vocabulary — `policy` is the
automated side and comes first.

**The one chain**, in order, used by `TryDeclare` and `RetargetFor` alike:

1. a live **direct order** for this actor (below);
2. `steered` when `steeredKeys.Contains(actorKey)` — the two deleted routers' whole body;
3. `policy` — `state.DefaultAiIntentSource`'s role;
4. `fallback` — today's `new StubIntentSource(view, state.Cooldowns, NoStanceHeld.Instance, state.CostLedger)`.

An explicitly injected `intentSource` (a replay trace source, `InteractiveIntentSource`) is passed in as
`steered` with the key set it covers, or as `policy` when it covers every actor. **Both call sites resolve
through this one method**, which is what closes M5: `TimelineDispatch.Reselect` can no longer disagree
with `DeclareBasicAttack` because there is no second expression to disagree with.

`RetargetFor` is not "score the (action, target) pair again". The committed envelope is fixed; only the
target is open. It asks the resolved source for a target **for that action id**, which the core scorer
answers by running its target stage alone. A policy with no notion of a fixed action (the fallback stub)
answers with its ordinary target pick, which is byte-identical to what `Reselect` returns today.

### 2. Trait decorators, applied to every policy

```csharp
/// A trait that changes WHAT A POLICY SEES or WHERE ITS ANSWER LANDS. The implementations stay
/// engine-side (decisions.md:44 — "bloodthirsty/loyal stay BattleEngine-side wrapping, never
/// reimplemented in the action program"); the router owns only the ORDER and the COVERAGE.
public interface ITraitDecorator
{
    bool AppliesTo(string actorKey);
    IBattleView Decorate(string actorKey, IBattleView inner);      // pre-decision (bloodthirsty)
    string EffectiveTargetOf(string actorKey, string targetKey);   // post-decision redirect (loyal)
}
```

- **`bloodthirsty`** is `Decorate` — `BloodthirstyViewFor` (`BasicAttack.cs:495-506`) unchanged, now reaching
  every policy instead of only the stub.
- **`loyal`** is `EffectiveTargetOf` — the same body as the former inline redirect, now `BasicAttack.cs:571-595`, including its CC gate
  (`!IsCcLocked(state.Status, bodyguard.Setup.Key, now)`), declared **once** and called **twice**: once by
  the core scorer while building candidates, so `kill` and `lowHp` score the actor that will actually be
  hit, and once by the engine at the existing redirect site, which is what moves the target. Applied
  **exactly once on each side**; the scorer never chains a redirect of a redirect.

  The scorer consumes it as `Func<string, string>?` (null = identity), so a policy built with no decorator
  is byte-identical. That delegate is the whole of the "communicated to the scorer" requirement — it adds
  no trait vocabulary to `Core/Actions/`, which is the half `decisions.md:44` locks.

**`bloodthirsty` and a scoring policy — say what this actually buys.** `BloodthirstyView` only reorders
`IBattleView.LiveActorKeys` (`BasicAttack.cs:607-633`). A first-usable policy reads the first enemy it
finds, so the reorder *is* the trait. A **scoring** policy scores every candidate and tie-breaks on
ordinal actor key (`Actions/Ai/CandidateScorer.cs:191-203`, `Argmax`, moved from SiegeAi.cs lines 140-145
by CAI1.1), so list order changes its answer **only where the structural
`maxCandidatesScored` truncation bites** (`Actions/Ai/CandidateScorer.cs:147-149`, was SiegeAi.cs line 135).
That is honest, not a gap to paper over: for a
smart-tier actor, "focus the weakest" is expressed by the profile's `lowest-hp` selector and `weightLowHp`,
and the trait decorator biases which candidates survive the cap. The overlap is audit M1's flag; resolving
it into one mechanism is **`profile-schema`'s** call, not the router's (see Open questions).

### 3. Direct orders

```csharp
/// D3's second kind: an order to one creature, not a takeover of it. Deterministic by construction —
/// every field is a value, and expiry is a TICK comparison, never a wall clock (DecisionTrace.cs:11-19:
/// "recorded as a DECISION AT A TICK, never re-measured on replay").
public readonly record struct DirectOrder(
    string ActorKey, string ActionId, string? TargetKey, long IssuedTick);

public interface IOrderQueue
{
    /// Non-blocking, never awaits. Returns false when this actor has no live order.
    bool TryPeek(string actorKey, out DirectOrder order);
    void Commit(string actorKey);   // the order produced an intent
    void Expire(string actorKey);   // orderTimeoutTicks elapsed
}
```

Inside `TryDeclare`, an order is **a top-rank candidate, not a bypass**:

1. `TryPeek`; if `nowTick - IssuedTick >= orderTimeoutTicks`, `Expire` and fall through to step 2 of the chain.
2. Offer the order to the resolved policy as the rank-0 candidate. If the action clears the ordinary gates
   (`UsabilityEvaluator.cs:52-83`, the `resolvable-here` filter, the reserve floor), it wins and `Commit`
   fires. **If it does not clear them, the order does not fire and the AI decides underneath** — an order
   never bypasses cost, cooldown or legality, because that would be a second, weaker declaration path
   (battle-engine-ssot §5 Q4).
3. The rank vocabulary itself is `profile-schema`'s closed enum; the router names its top member and
   never invents a number.

**Replay.** In a mode with a replay contract, a direct order is a **human decision** and is recorded into
`DecisionTrace` with `DecisionSource.Player` exactly as `InteractiveIntentSource.cs:132` records one —
otherwise a replay re-derives the AI's answer and diverges. On the lawn there is no replay contract (S4:
"no lawn combat goldens exist to protect"), so the lawn queue records nothing. The router takes the trace
as the same optional `Action<TracedDecision>?` seam `InteractiveIntentSource.cs:43-50` already defines,
rather than reaching for `DecisionTrace` itself.

### 4. Reactions stay automatic — stated, and stated to the profile

`TimelineDispatch.cs:241-253` enters the reaction lane and calls `ReactionCounter.TryCounter(pools,
ReactionLanePolicy.Tuning.PoiseSpend, ...)`, which commits `poise` through `PoiseLedger.TryCommit`
(`ReactionCounter.cs:41-44`) whenever the actor can afford it. **No `IIntentSource` is consulted, and this
module does not make one be.** A reaction is the engine resolving a defence, not the AI deciding one
(battle-engine-ssot §3c).

The consequence a profile must be told: a `poise` reserve floor computed as *"never drop below X‰ after
paying for my own action"* is silently defeated, because the engine will spend the remainder on counters
the profile never saw. So the contract this module publishes to `profile-schema` is:

> **The `poise` reserve floor is `max(profileFloor, expectedReactionSpend)`**, where
> `expectedReactionSpend` = `ReactionLanePolicy.Tuning.PoiseSpend` × the profile's authored
> reactions-per-round expectation. The router exposes `PoiseSpend` to the profile layer as a read; it
> never changes it, and it never asks a policy whether to counter.

**Who implements that max — named, because a contract with no implementer is a paragraph.** It is
**module 1's `ReserveFloorAffordability` decorator**, which already wraps gate 3 and already reads the
authored per-resource floor ([spec-core-scorer.md](spec-core-scorer.md) §5 step 3, which carries the
constructor signature). This module's two jobs are to *expose* `ReactionLanePolicy.Tuning.PoiseSpend`
as a read and to *own the tuning key* `router.reactionsPerRoundExpected`; module 1's decorator takes
both as constructor inputs and computes `max` for the `poise` resource id only. Both arguments default
to `0`, so the max is a no-op until this module supplies them — which is what keeps module 1's commit
byte-identical.

It is deliberately **not** folded into module 2's authored value. Folding would make a balance pass on
the profile's floor silently also a balance pass on the engine's reaction budget, and the two are
different quantities with different owners.

### 5. Byte-identity, cause by cause

The map's rule 7 is one cause per commit. This module carries three causes and they are **not** equal:

| Cause | Behaviour change | Evidence it is inert today |
|---|---|---|
| **A. Router dedup + one chain (incl. the reselect fix)** | **None, provably.** | `Reselect` exists only inside `RunTimelineActionPhase` (`TimelineDispatch.cs:44-48`), reached only when `activeProfile.UsesTimelineDispatch` (`BattleEngine.cs:569`). The three profiles that set it are `ClassicRound`/`GalaxySync`/`HybridAtb` (`BattleModeProfile.cs:221,235,251`). `state.DefaultAiIntentSource` is non-null only when `aiTuning` is supplied (`BattleRunState.cs:743-757`), and the **only** production caller that supplies it is `DistrictAssaultResolver.cs:225`, which resolves under `BattleModeProfileCatalog.SiegeId` (`:215`) — and `Siege` (`BattleModeProfile.cs:279-283`) does **not** set `UsesTimelineDispatch`. So on every production path today, the omitted term is null. The fix is real and becomes live at `auto-policy-switch` (module 14) |
| **B. Trait decorators on every policy** | **A real change for siege.** `DistrictAssaultResolver.cs:437` sets `TraitIds = species.TraitPool`, and `bloodthirsty`/`loyal` are both live in that pool (`CreatureSpeciesCatalog.Generated.cs`, 20 species carry `loyal`). Bloodthirsty moves siege's answer only where the `maxCandidatesScored` cap truncates; the `loyal` pre-decision feedback moves `kill`/`lowHp` wherever a bodyguard stands adjacent to a candidate | **Its own commit.** Run `SiegeAiLiveWiringTests`, `BattleGoldenTests` and `ExpeditionResolverTests` and **report what moved** — do not assume either way (DESIGN-GATE §3 rule 4) |
| **C. The order queue** | None until a producer exists | `IOrderQueue` is null for every caller this module ships; module 20 is the first producer |

`SiegeAiLiveWiringTests.cs:73` is the one *test* that pairs `aiTuning` with a dispatch profile, so it is
the one place cause A is observable at all. Check it explicitly.

## Tunables

**Where the `router` block lives, and who declares it.** Both keys below sit in a **top-level `router`
object** in `gk-core/data/tuning/combat-ai.v1.json` — not inside a profile, because a router is one object per
battle rather than one per `place × role`. The block's record, `AiRouterBlock`, is **declared by
`profile-schema` (module 2)** alongside `CombatAiTuning`
([spec-profile-schema.md](spec-profile-schema.md) §2), and module 2's parser rejects a file that omits
it. This module is its only reader. That split is deliberate: module 2 owns the file's shape and its
parser, so a block it does not declare is a block nothing can parse; this module owns what the numbers
*mean*, which is what the table below states.

| Key | File | Unit | Seed | Why |
|---|---|---|---|---|
| `router.orderTimeoutTicks` | `gk-core/data/tuning/combat-ai.v1.json` (new; module 2 creates it, and declares this block) | ticks (1 tick = 1 ms, `decisions.md` Battle time model) | `5000` | Five seconds of virtual time. `classic-round` resolves roughly one action per actor per 1000-ms round, so five rounds' worth is long enough for a slow actor to reach its next decision and short enough that an order does not outlive the situation that motivated it. A balance pass will move it; it is not structural |
| `router.reactionsPerRoundExpected` | same file | count (per-mille of a round) | `1000` (one per round) | What the `poise` reserve floor budgets for engine counters. One per round is the worst case the reaction lane can produce at `wReact = 1`. Tuned down when telemetry shows lanes are rarer. **Read by module 1's `ReserveFloorAffordability`**, which this module hands it to (§4) |
| `MaxLiveOrdersPerActor` | code `const` | count | `1` | **Structural, not a balance number** — a second live order for the same actor is a queue, and a queue of orders is a plan, which this program does not have. A new order replaces the old. Comment says so (tunables-ssot.md §1) |

No `Θ`-derived number, no magnitude, no cap on a magnitude: this module carries none
(ssot-power-scale.md §11 does not gain a row).

## Code style

- Indexed `for` over `IReadOnlyList<T>`, never `foreach` — `StubIntentSource.cs:61-63` names the boxed
  enumerator as the exact per-decision allocation the acceptance line forbids, and this module's router
  sits on the same path.
- `ActionIntent` stays a struct and `None` stays in the value (`IntentSource.cs:12-18`); the router never
  returns `ActionIntent?`.
- Constructor-validated seams with `ArgumentNullException`, C# 10 (`net6.0`), no `required` — this was
  `SiegeIntentSource`'s own recorded reason before CAI1.10 deleted the class; the same discipline
  applies to `IntentRouter`'s own constructor.
- A precomputed key set, never a live `IBattleView.SideOf` dispatch — both deleted routers (now gone;
  RaidIntentSource.cs, whole file, and `SiegeIntentSource`, inside `SiegeAi.cs`) carried this
  correction in their own doc comments, and this module
  inherits it verbatim.
- Deleted code is deleted, not left inert beside the router. A second, unused router is the wiring gap
  this module exists to close.

## Testing strategy

`gk-core/tests/FusionRpg.Core.Tests/Actions/IntentRouterTests.cs` (new):

| Test | Asserts |
|---|---|
| `Steered_keys_route_to_the_player_source_and_everyone_else_to_the_policy` | The two deleted routers' whole contract, once. Ported from `SiegeAiIntentSourceTests` / the raid router's tests |
| `The_fallback_chain_is_order_injected_then_steered_then_policy_then_default` | The chain as a contract, not as two expressions |
| `Reselect_and_declare_resolve_the_same_source_for_the_same_actor` | **M5 as a test.** Fails against today's `TimelineDispatch.cs:79-80` |
| `RetargetFor_keeps_the_committed_action_and_changes_only_the_target` | `ActionRunner.cs:393-396`'s contract |
| `Every_policy_sees_the_bloodthirsty_view_not_only_the_fallback` | M1 half 1. A fake policy records the view type it was handed |
| `A_loyal_redirect_is_applied_once_on_each_side_and_the_scorer_reads_the_redirected_target` | M1 half 2. The candidate's `kill`/`lowHp` inputs name the bodyguard, and the engine's own redirect still moves the target to the same actor |
| `An_order_that_fails_a_gate_does_not_fire_and_the_policy_decides_underneath` | An order is a candidate, never a bypass |
| `An_order_expires_on_a_tick_comparison_and_never_on_a_clock` | Determinism. Reads no `DateTimeOffset` |
| `An_order_in_a_replay_mode_is_recorded_as_a_Player_decision_and_replays_identically` | `DecisionTrace.cs:50-55` + `InteractiveIntentSource.cs:132` |
| `The_router_consults_no_policy_for_a_reaction` | A fake policy asserts zero calls across a battle whose reaction lane fires |
| `Constructing_a_router_with_no_decorators_and_no_queue_reproduces_the_shipped_chain` | The byte-identity harness for cause A |
| `Compose_invokes_steeredSourceFor_exactly_once_with_the_policy_it_was_given` | §1a. A recording factory asserts it receives the automated policy, not a null or a second instance — the delve's whole constraint |
| `Compose_with_a_null_fallback_returns_None_rather_than_inventing_a_stub` | §1a's stated semantics, pinned so the lawn's case cannot silently grow a second decision path |
| `A_router_built_through_Compose_and_one_built_through_the_constructor_resolve_identically` | One construction entry point, not two behaviours |

**Closed-vocabulary assertions only.** Nothing here pins a species count, a trait count, or generated
text. The one pinned literal is the **four-step chain length**, and it is pinned because the chain is a
closed vocabulary this code owns (`validation-ssot.md`).

**Golden impact.** Cause A: byte-identical, and the argument is structural (see §5) — but *run*
`BattleGoldenTests` and `ExpeditionResolverTests` and say what they printed; the claim is testable and an
untested claim is an opinion (DESIGN-GATE §3 rule 4). Cause B: expected to move siege behaviour, its own
commit, with the moved tests named. No `RulesetVersion` bump is claimed here — `decisions.md:44`'s named
trigger is *a real divergent multi-action loadout reaching a live battle*, which is module 14's cause, not
this one.

## Boundaries

**Always**

- Keep the router in `Core/Actions/` and Unity-free; the lawn adapts to it (ideal §3 principle 5).
- Construct through `Compose` (§1a) — one entry point, named arguments, every optional parameter's
  omission being today's behaviour.
- Resolve the source through the one chain method — both call sites, no exceptions.
- Supply decorators from the engine; the router holds the list, never the trait vocabulary.
- Expire an order on a tick, and record it where a replay contract exists.

**Ask first**

- Anything that would make cause B land in the same commit as cause A.
- Giving the router a scoring opinion of any kind (that is module 1's, and a second scorer is the SOLID S
  fork the audit caught).

**Never**

- Re-implement `bloodthirsty`/`loyal` inside `Core/Actions/` — `decisions.md:44` locks them engine-side.
- Dispatch on a live `IBattleView.SideOf`: `BattleEngine.Resolve` builds its view internally, after it is
  called, so no external caller holds one — the correction `SiegeIntentSource`'s own doc comment
  recorded before CAI1.10 deleted the class.
- Let an order bypass a gate, a cost or a cooldown.
- Ask a policy whether to counter a reaction.
- Leave `RaidIntentSource`/`SiegeIntentSource` in the tree as dead code.
- Add a second construction entry point beside `Compose`, or let a caller invert the
  `steeredSourceFor` wrap itself — that inversion skips `InteractiveIntentSource`'s `Record` call
  (`:139-146`) and breaks replay of an AFK turn.
- Build a `StubIntentSource` inside `Compose` to fill a null `fallback`. The chain simply has no step 4.
- Read a wall clock anywhere on this path.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** None. This is entirely on the **deciding** side of §3c, which
   the register does not cover. It touches responsibility 5 (targeting) only at its deciding half — *which
   target to pick* — and never at its resolving half.
2. **Does it DECIDE or RESOLVE?** Decide. Every line of it sits before `IIntentSource.TryDeclare` returns.
   The one adjacent resolving mechanism — the `loyal` redirect — keeps its engine-side implementation and
   its engine-side call; this module only reads it earlier, as a pure function.
3. **Mechanism or loop?** **Mechanism.** One router, one chain, every mode. *When* a place asks for a
   decision stays the place's loop (per turn in battle/delve/siege; a trigger edge on the lawn).
4. **Which existing implementation does it extend?** `IIntentSource` (`IntentSource.cs:29-37`) — the seam
   §3c already calls correct. It fuses `RaidIntentSource` and `SiegeIntentSource` into one implementation
   and takes over `BasicAttack.cs:175-180` and `TimelineDispatch.cs:79-80`. It copies nothing.
5. **Does every mode get it?** Yes — battle, expedition, delve, siege now; the lawn through module 20's
   adapter. There is no "battle only" branch anywhere in it.
6. **Is it deterministic and seeded?** Yes, and it reads no RNG at all. The chain is a function of
   `(actorKey, steeredKeys, order queue state, nowTick)`; order expiry is a tick comparison; an order in a
   replay mode is recorded exactly as a human decision already is, so `(setup, seed, human trace, profile
   version, BattleEnvironment.Stamp)` stays a complete description (ideal §3 principle 4).

## Success criteria

1. `RaidIntentSource.cs` and `SiegeIntentSource` are **deleted**, and every former caller constructs
   `IntentRouter`.
2. `BasicAttack.DeclareBasicAttack` and `TimelineDispatch.Reselect` both resolve their source through the
   same router method — grep finds no second `?? new StubIntentSource(` in `src/`.
3. `ActionRunner`'s reselect delegate is fed by `IntentRouter.RetargetFor`.
4. A fake policy handed to the router receives the bloodthirsty-decorated view; a fake scorer receives the
   `loyal`-redirected target key.
5. A direct order fires as a top-rank candidate, is refused by an ordinary gate when it should be, expires
   on a tick, and is recorded as a `Player` decision in a replay mode.
6. No policy is consulted for a reaction; `ReactionLanePolicy.Tuning.PoiseSpend` is exposed as a read,
   `router.reactionsPerRoundExpected` is authored in module 2's file, and module 1's
   `ReserveFloorAffordability` is the single implementer of the `max` — no second computation of it
   exists anywhere.
7. `IntentRouter.Compose` is the only construction entry point; `steeredSourceFor` is invoked exactly
   once with the automated policy; a null `fallback` yields `ActionIntent.None` and never an
   invented stub. `delve-automated-wiring`'s Open question 1 is closed by this signature.
8. Cause A commit: `BattleGoldenTests` + `ExpeditionResolverTests` green and **unchanged**, with the run
   output quoted in the commit body. Cause B commit: a predicted-delta note naming every moved siege test.
9. `guard-battle-responsibility.py` and `guard-actor-hub.py` green.

## Open questions

1. **`bloodthirsty` vs the `lowest-hp` selector — two mechanisms for "focus the weakest" (audit M1).**
   Options: (a) the trait stays a view decorator and the profile expresses focus through `lowest-hp` /
   `weightLowHp` — the ideal's locked shape, and what this spec builds; (b) the trait decorator also
   contributes a bounded scoring offset, which makes it a second scoring input; (c) the trait *selects* a
   profile row. **Recommended default: (a)**, unchanged, because (b) forks the scorer's input vocabulary
   and `decisions.md:44` locks the trait as a wrapper. **Cross-module note for `profile-schema` (module 2)
   and `core-scorer` (module 1):** if (a) leaves the trait too weak to read as a trait in play, that is a
   profile-vocabulary decision, and it needs a row in module 2's spec, not a branch in the router.
2. **Does a direct order survive the actor's death and ptr reuse?** On the lawn, `entity:{ptr}` grants are
   withdrawn before a ptr is reused (`overlay-control-loops.md` §6 rule 4), and an order keyed by a reused
   ptr would command a different creature. Options: (a) the queue is cleared on the same withdrawal edge as
   every other per-actor state; (b) an order carries the instance id and is validated at `TryPeek`.
   **Recommended default: (a)**, because it reuses the withdrawal edge that already exists rather than
   adding a second identity check — **cross-module note for `commander-direct-orders` (module 20)**, which
   owns the lawn queue implementation and must state the edge in its own spec.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: battle decision seam (IIntentSource), siege AI, delve
    routing, the battle timeline dispatch path.
[~] I established and recorded this session's boundary: this is a /spec authoring lane under session
    backlog-clean-up-20260920, whose record exists (tasks/sessions/backlog-clean-up-20260920.json,
    named by combat-ai-map.md). I did NOT run session-boundary-check.py — this lane is instructed to
    run no repo mutations and writes only this spec file. GAP NAMED.
[x] I read every doc in the §1 row(s) for those subsystems, this session: DESIGN-GATE.md,
    battle-engine-ssot.md (§2, §3c, §5), decisions.md row 44 (Action selection), combat-ai-map.md,
    combat-ai-ideal.md rev 3, research/combat-ai/AUDIT.md + S1 + S3 + S4.
[x] I checked decisions.md for a lock covering this: row 44 locks bloodthirsty/loyal as engine-side
    wrappers and names the next RulesetVersion trigger. This spec keeps both locks.
[x] Every factual claim cites file:line, and every file cited was opened in this session.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments — the reselect/DefaultAiIntentSource/profile chain in
    §5 cause A was traced through five files, not inferred from TimelineDispatch.cs's own header
    comment (which says "siege/delve were not re-checked here").
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. The byte-identity argument for cause A is
    STRUCTURAL and is stated as a claim to run, not a result: this lane runs no builds or tests by
    instruction. §5 and Success criterion 7 require the implementer to run and report.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated: the audit's M1/M5/M6 and the map's module-4 row are all answered here;
    nothing in this spec contradicts the ideal.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal (chain length 4) is a closed vocabulary this code owns.
[x] No event-refreshed cache is introduced (§2.16). The order queue is not a cache: it holds orders,
    not a projection of state, and Open question 2 names its one lifecycle edge.
[x] No acceptance criterion fixes an ordering that can vary in real play — the chain order IS the
    contract and is asserted as such.
[x] Produces/consumes no actor combat magnitude; composes nothing. ActorHub is untouched.
[x] Does not invent or extend a SOLID-violating parallel path — it DELETES one (two routers → one)
    and refuses to add a second scorer or a second declaration path.
[x] A new rule has a registry row: the "one chain, both call sites" rule is covered by
    guard-battle-responsibility.py's existing scope plus Success criterion 2's grep; if the
    implementer finds that guard does not reach it, add a row to gk-core/scripts/enforcement-registry.v1.json
    rather than leaving the rule unguarded.
```

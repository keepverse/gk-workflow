# Spec: `lawn-actor-view` (combat-ai module 15)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `core-scorer` (module 1) · **Unblocks:** `lawn-cast-trigger` (module 19) ·
**Status:** **built, host included** (Core `CAI4.1`; the injector host also `CAI4.1`, lane `cai2`, 2026-09-23). `Actions/Ai/Lawn/{LawnBattleView,LawnRelationChain,LawnDerivedCache}.cs` exist with 18 tests — side taken only from the oracle, one Hub resolve per (ptr, revision) per frame, the downed read answered rather than inherited — and the host, `Injector/Effects/LawnActorViewHost.cs`, is in with its seven seams and 10 tests. **It has a production caller:** `InjectorLoop` → `LawnDecisionHost.Tick` → `ViewFor(perspective, frame)`, one view per due actor's own side per frame. **One stated absence, not a defect:** `statusMaskOf` reads `0`, because no per-ptr status-mask producer exists in `src/` (the class doc says so; `FactsOf.StatusMask` under-reports until one does).

## Objective

**The lawn has no `IBattleView`, and that single absence is why the whole shipped decision stack is
unreachable there.** `IBattleView` (`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:17-97`) is the one read
seam every policy uses — `StubIntentSource` reads nothing else
(`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:29,44-53`) — and its only implementors are
`BattleRunState`, `FoggedBattleView`, a private `BloodthirstyView` nested in `BasicAttack.cs`, and test
fakes. The injector has zero hits for `IIntentSource | ActionIntent | FrozenActionSet | IBattleView`
(`../research/combat-ai/S4-lawn.md:32-33`, re-confirmed by the audit's verified-correct list,
`../research/combat-ai/AUDIT.md:45`). This module builds the lawn's implementation and nothing else.

It is **partly built, not a green field** — the audit's bucket correction B6
(`../research/combat-ai/AUDIT.md:56`). `ILawnBoardView` / `ILawnUnitView`
(`gk-core/src/FusionRpg.Core/Match/Ai/ILawnBoardView.cs:15-21,36-41`) already exist as a Unity-free lawn board
view, and `IOwnSideOracle.RelationOf`
(`gk-core/src/FusionRpg.Core/Battle/BattlefieldOwnSideReactor.cs:18-23`) is *"the one, enforced seam"* for side
and relation, with two shipped production implementations —
`MechanicalOwnSideOracle` (`gk-core/src/FusionRpg.Core/Battle/MechanicalOwnSideOracle.cs:22-56`, which flips on
mind control at `:50-52`) and `SpecimenOwnershipOracle`
(`gk-core/src/FusionRpg.Core/Battle/SpecimenOwnershipOracle.cs:24-50`, *"which player deployed it"*). The
adapter's job is to answer `IBattleView`'s ten members from those two types, **never** from a unit's raw
on-board side.

Two performance defects are designed out from the first line rather than fixed later, because both are
already measured elsewhere in this repo:

1. **A per-frame board census is O(board) on every frame, including frames with nothing to decide.**
   The audit names it (`../research/combat-ai/AUDIT.md:101-102`: *"Build it lazily, only on frames that
   have at least one edge"*). This view is therefore built **only** when module 19 has at least one
   decision edge for that frame, and it reuses the already-frame-cached
   `InjectorBoardSnapshot.Capture()` (`gk-fusion/src/FusionRpg.Injector/Effects/InjectorBoardSnapshot.cs:21`,
   invalidated by lifecycle hooks at `:36`) rather than adding a scan.
2. **`DerivedOf` must never be `ResolveDerived` per check.** Today the lawn's gate 3 goes
   `CostLedger.Check` → `derivedFor` → `InjectorStatusBridge.ResolveDerived`
   (`gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs:63,101`;
   `gk-fusion/src/FusionRpg.Injector/Effects/InjectorStatusBridge.cs:18-24`), which is the *"uncached resolve"*
   the perf audit blames (`../combat-ai-ideal.md:161`). This view owns a per-frame, revision-keyed memo
   and is the single derived reader every decision-time consumer shares.

## Tech stack

`FusionRpg.Core` (the adapter, the relation chain, the memo — all Unity-free, because CI never builds
the injector: `gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:10-14`) and `FusionRpg.Injector` (the
thin host that supplies the board snapshot, the oracles and the derived resolver). No new dependency,
no new interface — `IBattleView` is the contract and it does not change.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnBattleView|FullyQualifiedName~LawnRelationChain|FullyQualifiedName~LawnDerivedCache"
# The Match/Ai narrow-view guard must stay green and UNMODIFIED -- see §Project structure.
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ILawnBoardViewTests"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-core/scripts/guard-actor-hub.py ; python gk-core/scripts/guard-secondary-no-unity.py ; python gk-fusion/scripts/guard-single-writer.py
```

No tuning publish: this module has no tunables (see below).

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnBattleView.cs` | **new — landed (CAI4.1)** | The `IBattleView` over `ILawnBoardView` + `IOwnSideOracle`, built per (frame, perspective) |
| `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnRelationChain.cs` | **new — landed (CAI4.1)** | An `IOwnSideOracle` that asks the shipped oracles in order, first non-null wins |
| `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnDerivedCache.cs` | **new — landed (CAI4.1)** | `(ptr, revision) → ActorDerivedSnapshot` memo with pass-through on a miss |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnActorViewHost.cs` | **new — landed (CAI4.1, lane `cai2`)** | Injector composition root: board snapshot → `ILawnBoardView`, oracle construction, derived delegate |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/Lawn/LawnBattleViewTests.cs` | **new — landed (CAI4.1)** | Contract tests over synthetic fixtures |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/Lawn/LawnDerivedCacheTests.cs` | **new — landed (CAI4.1)** | Resolve-count and revision-key tests |

Nothing under `gk-core/src/FusionRpg.Core/Battle/`, `gk-core/src/FusionRpg.Core/Actions/` (outside the new `Ai/Lawn/`
folder) or `gk-core/src/FusionRpg.Core/Match/Ai/` is edited.

### ⚠️ Why these three files are NOT under `Match/Ai/`, and why that is a decision

The obvious home looks like `gk-core/src/FusionRpg.Core/Match/Ai/`, beside `ILawnBoardView` and the Zomboss
scorer, and the rest of wave 4 (modules 16, 18, 19, 20) does put its new files there. **This module is
the one that must not**, and the reason is a live, compile-time-enforced invariant that belongs to a
different consumer.

`ILawnBoardView`'s own doc comment states the invariant: it is *"the ONLY thing the Zomboss scorer
(T3.3) may read … deliberately narrow: wave, visible units, HP — nothing else (no element matchups, no
status list) until a real policy build (T3.3) proves it needs more"*
(`gk-core/src/FusionRpg.Core/Match/Ai/ILawnBoardView.cs:23-34`). It is enforced, not merely documented:
`Nothing_under_Match_Ai_may_read_the_board_itself`
(`gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/ILawnBoardViewTests.cs:70-86`) enumerates **every** `.cs` file
under `gk-core/src/FusionRpg.Core/Match/Ai/` recursively (`:111-119`) and fails the build if any non-comment
line contains `MatchRuntime`, `MatchSnapshot`, `: Board`, `(Board ` or ` Board.` (`:100-109`).

`LawnBattleView` reads `BoardSnapshot` (`gk-core/src/FusionRpg.Core/Combat/BoardSnapshot.cs`) directly for
`PositionOf`/`FactsOf` — Row, Col, TypeId, `IsMindControlled` — which is a **wider census** than
`ILawnUnitView` exposes (`Ptr`/`Relation`/`HpCurrent`/`HpMax`, and deliberately no position and no
type: `ILawnBoardView.cs:15-21`). The current guard would not fail it today, because `BoardSnapshot`
is a different literal from the five patterns it scans — but that is an accident of the pattern list,
not permission. Tightening the list to include `BoardSnapshot` is an obvious and correct future edit
for the Zomboss folder, and it would break this module without warning.

**Decision: the three files live in `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/` instead**, which is
option (a) of the two the review named, and it is the better home on its own merits:

- `IBattleView` — the contract this module implements — lives under `Actions/`
  (`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs`), not under `Match/`.
- `core-scorer` (module 1) already creates `gk-core/src/FusionRpg.Core/Actions/Ai/`, and `decision-inspector`
  (module 10) puts its files there too. The lawn's adapter is a `combat-ai` deliverable, so it belongs
  in `combat-ai`'s folder.
- Nothing has to be widened. Option (b) — relaxing
  `Nothing_under_Match_Ai_may_read_the_board_itself` with a carve-out distinguishing "no full board
  access (Zomboss)" from "a combat-ai adapter's richer census read" — weakens a guard to fit a new
  file, which is the shape this repo's hard rules refuse. It is explicitly **not** taken.

**The rest of wave 4 stays in `Match/Ai/`, and the criterion is stated so it is checkable, not a
habit.** `LawnHeldActionSets` (16), `LawnCastPlan` (18), `LawnDecisionTrigger`/`LawnDecisionBudget`/
`LawnCastTokenPool` (19) and `LawnOrderQueue` (20) read **no board census at all** — they hold
per-actor state, a held-action set, or a plan — so the folder's invariant is nothing they can violate
and moving them would be churn. **The rule: a file that reads a board census belongs in
`Actions/Ai/Lawn/`; a file that holds per-actor or per-match state belongs in `Match/Ai/`.** This
module is the only one in the wave on the first side of that line.

## The shape

### A view has a perspective, because a relation does

`IBattleView.SideOf` is **absolute** — its own doc defines enemy as `SideOf(other) != SideOf(self)`
(`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:24-26`). `IOwnSideOracle.RelationOf` is **relative**: both
shipped oracles are constructed with a perspective (`MechanicalOwnSideOracle.cs:33` takes `mySide`;
`SpecimenOwnershipOracle.cs:35` takes `myPlayerId`). The adapter reconciles them by being
perspective-scoped:

```csharp
public sealed class LawnBattleView : IBattleView
{
    // 0 == "my side" (Self/Ally), 1 == "the other side" (Enemy). The SAME 0/1 vocabulary
    // IBattleView.SideOf already documents -- never EntityFacts.Side read off the raw board.
    public int SideOf(string actorKey) =>
        _relation.RelationOf(actorKey) switch
        {
            RelationKind.Self or RelationKind.Ally => 0,
            _ => 1,   // Enemy, Any, and (via LawnUnitViewFactory) an un-owned vanilla unit
        };
}
```

A lawn board has exactly **two** deciding perspectives: the player's and Zomboss's. `LawnActorViewHost`
caches at most one view per perspective per frame. Two is a **structural** limit on a closed set (there
are two commanders on a lawn), not a progression cap, and the constant says so in a comment.

**Hypnosis is how this earns its keep.** A unique creature deployed by the player but mechanically
sitting on the zombie side (`CreatureDeployMode.HypnoAlly`, named in `ILawnBoardView.cs:12`) resolves
`Ally` to the player's `SpecimenOwnershipOracle` and `Enemy` to Zomboss's. Both answers are correct and
neither reads the board's side field. A raw vanilla unit has no owner row, so `RelationOf` returns
`null` and `LawnUnitViewFactory.Build` resolves it to `RelationKind.Enemy`
(`gk-core/src/FusionRpg.Core/Match/Ai/ILawnBoardView.cs:68`) — *never silently dropped, never mis-read as
Self/Ally*, that file's own words.

### The relation chain

```csharp
/// <summary>Asks each shipped oracle in order and returns the FIRST non-null answer. Not a third
/// oracle: it composes MechanicalOwnSideOracle (T21a) and SpecimenOwnershipOracle (T21b) without
/// re-deciding what either one means. Order is specimen-first, because "which player deployed it"
/// outranks "which mechanical side is it on" whenever both can answer.</summary>
public sealed class LawnRelationChain : IOwnSideOracle
{
    readonly IOwnSideOracle[] _links;   // structural: exactly the two shipped oracles
    public RelationKind? RelationOf(string ptr)
    {
        for (var i = 0; i < _links.Length; i++)
            if (_links[i].RelationOf(ptr) is { } r) return r;
        return null;   // LawnUnitViewFactory resolves a null to Enemy (ILawnBoardView.cs:68)
    }
}
```

### Answering all ten members, including the ones the lawn does not have

A seam is only honest if every member has a stated answer. Guessing on four of them is how a view
silently lies to a scorer.

| Member (`IBattleView.cs`) | Lawn answer |
|---|---|
| `LiveActorKeys` (`:22`) | The perspective's ptr list, in `BoardSnapshot.Entities` order (`gk-core/src/FusionRpg.Core/Combat/BoardSnapshot.cs:17-23`, already filtered to `Living`). Stable within a frame. |
| `SideOf` (`:26`) | The chain above. |
| `PositionOf` (`:31`) | `new GridPos(snap.Row, snap.Col)` from `BoardSnapshot.cs:8-9`. **Never null** — the lawn always has a board, so `StubIntentSource`'s no-board `SourceOrder` fallback (`StubIntentSource.cs:119`) is unreachable here. |
| `FactsOf` (`:34`) | `EntityFacts` (`gk-core/src/FusionRpg.Core/Effects/Atoms/FactReader.cs:34-51`): `Side` from the chain, `TypeId`/`Row`/`Col`/`IsMindControlled` from the snap, `HpMilli` from `ILawnUnitView.HpCurrent/HpMax`, `ElementId` from the already-per-ptr-cached lawn element resolve (the same `LawnElementResolverHost.Resolve` the grant binder uses, `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs:237`), `StatusMask` from `EffectRuntime.Status`. `IsKiller` is **false**: it is a battle-turn concept with no lawn producer, and answering `false` is the neutral value every consumer already treats as "no". |
| `HeldActionsOf` (`:39`) | Delegated to module 16's registry through a `Func<string, IReadOnlyList<CompiledAction>>`, so this module lands and is testable before module 16 exists (the delegate returns an empty list until then, which `StubIntentSource.cs:45` already handles as "cannot act at all"). |
| `DerivedOf` (`:51`) | The memo below. **Never null for a live actor** — see "No fog". |
| `GarrisonedStructureKeyOf` (`:61`) | Always `null`. There are no siege emplacements on a lawn; `null` is that member's own documented absence convention. |
| `ObjectivePositionOf` (`:73`) | Always `null`. Its own doc already says `null` for *"every non-siege battle"* (`:67-68`). The core's objective weight therefore contributes nothing on the lawn, which is correct, not a gap. |
| `MaxHpOf` (`:82`) | `ILawnUnitView.HpMax` (`ILawnBoardView.cs:20`). |
| `AggressionOf` (`:97`) | The Hub-composed `ai.aggression` value read out of the memo'd `ActorDerivedSnapshot`, saturated onto the closed tier range by module 6 `aggression-tier-map`. Never a private fold, never a second read path. Its own doc already says a real implementor *"need only forward its own already-held `Derived` snapshot"* (`:47-48`). |

`HpMilli` is a **bounded ratio**, and its arithmetic says so:

```csharp
// Bounded ratio 0..1000 of a live magnitude, not a progression cap (CLAUDE.md "Caps").
// HpCurrent/HpMax are long (ILawnBoardView.cs:19-20): the multiply happens in long and the
// divide is last, so the narrowing cast cannot lose range -- the result is already in 0..1000.
static int HpMilli(long hpCurrent, long hpMax) =>
    hpMax <= 0 ? 0 : (int)Math.Clamp(hpCurrent * 1000L / hpMax, 0L, 1000L);
```

### Lazy build, and what "lazy" means precisely

`LawnActorViewHost.ViewFor(perspective, frame)` returns a cached view when `frame` matches the cached
frame **and** the board snapshot has not been invalidated since; otherwise it builds one. The host is
called **only from module 19's decision tick, and only when that tick has at least one due actor.** A
frame with no edge performs no board read, no relation resolve and no allocation — the property the
audit asked for (`../research/combat-ai/AUDIT.md:101-102`).

The build itself is O(live units) **once** per (frame, perspective), reusing
`InjectorBoardSnapshot.Capture()`'s existing per-frame cache (`InjectorBoardSnapshot.cs:21`). It adds
no `FindObjectsOfType`: the only remaining one on the combat path is
`InjectorEntityRegistry.Resync` (`gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs:180-199`),
which this module does not touch.

The build is measured inside whatever `PerfProbe` scope its caller opened. **This module does not add a
`PerfSection` member** — `lawn.ai.decide` is module 19's, and adding it twice would fork a closed
vocabulary (`gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41,50-51`).

### The derived memo, and the revision it is keyed on

```csharp
/// <summary>One ActorHub resolve per (ptr, revision) per frame. Consumes Hub output -- it never
/// composes, never folds, and never caches a number Hub did not return (CLAUDE.md "One ActorHub
/// compose / one read").</summary>
public sealed class LawnDerivedCache
{
    readonly Func<string, ActorDerivedSnapshot> _resolve;   // InjectorStatusBridge.ResolveDerived
    readonly Func<string, long> _revisionOf;                // actor-liveness-refresh; see below
    public ActorDerivedSnapshot Get(string ptr);            // memo hit, or one _resolve call
    public void BeginFrame();                               // drops the memo
}
```

**The invalidation channel is `actor-liveness-refresh`'s, and this module does not re-specify it.**
That module (`../lawn-playable/spec-actor-liveness-refresh.md`) owns `ActorLivenessRevision`, *"a `long`
counter per `(playerId, entityKey)`; every consumer keys on it"* (`:93-95`), and its rule 3 is that a
living entity re-composes lazily when its revision moves (`:104-109`). It is **spec, not built**
(`:5` *"Status: spec, 2026-09-16. Not built."*), so:

- `_revisionOf` is a seam. Until `ActorLivenessRevision` ships it returns a constant, which makes the
  memo **frame-scoped only** — correct, just colder than it will be.
- The memo is frame-scoped **and** revision-guarded, both, not either. Frame scope bounds staleness to
  one frame (~16 ms). The revision guard is what honours an invalidation that arrives *inside* a frame,
  which is exactly the case rule 3 exists for.
- This is a wiring dependency, named with that word. Module 19 must not ship default-on before it is
  wired, because a decision reading a frozen Θ is the class of defect
  `spec-actor-liveness-refresh.md:14-21` measured.

### No fog — and what that costs

`FoggedBattleView` is battle/siege only (`../research/combat-ai/S4-lawn.md:64-66`: *"the PvZ lawn has
no fog-of-war"*). This view composes nothing over itself. Three consequences, stated rather than
discovered later:

1. `DerivedOf` returns a real snapshot for every live actor, never `null`. `null` on this seam means
   *hidden*, and nothing on a lawn is hidden.
2. `AggressionOf` is not fog-gated. In siege, `FoggedBattleView` gates it
   (`../research/combat-ai/AUDIT.md:124-126`), so taunt and decoy read differently by viewer. On the
   lawn both sides read the same number.
3. **A lawn stealth status would have no effect on AI targeting.** There is no such status today —
   `charm_pulse`/`hypno` are CC and there is no `silence` or stealth
   (`../research/combat-ai/AUDIT.md:73`) — and if one ships, making it matter on the lawn is a new
   decorator over this view, the same one-implementation swap `IBattleView.cs:8-10` was designed for.
   It is not a silent property of this module.

## Tunables

**None.** This module introduces no number a balance pass would change. The three constants it does
introduce are structural and each carries a comment saying so:

| Constant | Value | Why structural |
|---|---|---|
| Perspectives cached per frame | 2 | A lawn has two commanders. A closed set, not a ceiling. |
| `HpMilli` bound | `0..1000` | A bounded ratio (`tunables-ssot.md` §1 exempt class). |
| Relation-chain length | 2 | Exactly the two shipped `IOwnSideOracle` implementations. |

## Code style

- Indexed `for` over `IReadOnlyList<T>`, never `foreach` — `foreach` over an interface-typed list boxes
  its enumerator, which is the per-decision allocation `StubIntentSource.cs:61-63` already refuses by
  name.
- A dead or unknown ptr is a **skip that returns a neutral answer**, never a throw
  (`overlay-control-loops.md:148-149`, Hot rule 1).
- Logic in Core, adapter in the injector, because CI never builds the injector
  (`KernelDriveHost.cs:10-14`).
- Doc comments name the spec section and the defect, the house style every file cited here uses.

## Testing strategy

All Core, over synthetic `ILawnBoardView` / `IOwnSideOracle` fixtures — no game, no Unity, in memory
(`docs/contributing/testing-standard.md`).

| # | Test | Asserts the contract |
|---|---|---|
| 1 | A unit whose raw board side is `zombie` but whose oracle answers `Ally` reads `SideOf == SideOf(self)` | Side comes **only** from the oracle (hypno) |
| 2 | A ptr no oracle knows reads as the other side | `ILawnBoardView.cs:68`'s null → `Enemy` rule |
| 3 | `_resolve` is called **at most once** per (actor, frame) across N `DerivedOf` + N gate checks | The per-frame memo replaces per-check `ResolveDerived` |
| 4 | A revision bump mid-frame causes **exactly one** further resolve for that actor and none for others | Revision key, scoped (not a storm) |
| 5 | With no decision edge, the board-snapshot delegate is **never invoked** | Lazy build |
| 6 | `GarrisonedStructureKeyOf` and `ObjectivePositionOf` are `null` for every actor | The lawn's stated shape, not an accident |
| 7 | `PositionOf` is non-null for every live actor | `StubIntentSource`'s no-board path is unreachable here |
| 8 | A second `ViewFor(same perspective, same frame)` allocates nothing | Zero-allocation-once-warm, the line `StubIntentSource` already carries |
| 9 | `HpMilli` with `hpMax = 0` is 0; with `hpCurrent > hpMax` is 1000 | Bounded ratio, both edges |
| 10 | `IBattleView`'s member set is exactly the ten this view implements | Closed contract — a new member must be answered here, not defaulted |

**Never asserted:** how many units a board holds, how many actors decided, or any fps/share number.
Those are readings (`validation-ssot.md`), and the 300-zombie A/B reports them.

**Mutation to kill:** replace `SideOf`'s oracle read with the raw `BoardEntitySnap.Side` — test 1 must
go red. That is the one property this module exists for.

**Goldens: byte-identical, zero movement.** No battle, siege or delve file is edited; no existing
`IBattleView` implementation is touched; the lawn has no golden contract at all
(`../research/combat-ai/S4-lawn.md:67-68`). This is a claim to verify, not assume: run
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` and report either
way.

## Boundaries

- **Always:** take side and relation from `IOwnSideOracle`; build lazily on an edge frame; resolve
  derived at most once per (actor, frame, revision); answer every `IBattleView` member explicitly;
  keep the logic in Core.
- **Ask first:** giving the lawn a fog decorator (a product decision about what a lawn stealth status
  means); widening `IBattleView` (it is a shared seam — a new member changes four implementations).
- **Never:** read `BoardEntitySnap.Side` for a relation; call `ResolveDerived` inside a gate check;
  build a census on a frame with no edge; add a `PerfSection` member here; compose or fold an actor's
  derived numbers (consume Hub output only); add a `FindObjectsOfType`; put a board-census reader
  under `gk-core/src/FusionRpg.Core/Match/Ai/`, or widen
  `ILawnBoardViewTests.Nothing_under_Match_Ai_may_read_the_board_itself` to admit one.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Responsibility 5, *targeting and area effect* — its **deciding**
   half's read surface. No new responsibility; the register (`battle-engine-ssot.md:123`) is closed and
   this adds nothing to it.
2. **Decide or resolve (§3c)?** Neither: it is the **data seam** the deciding side reads through.
   §3c puts every deciding system outside the engine, handing it data through
   `IIntentSource.TryDeclare` (`battle-engine-ssot.md:173`); this is what feeds those policies.
3. **Mechanism or loop?** **Mechanism** — one `IBattleView` contract, one adapter per place. *When* a
   decision is asked for is module 19's loop, and a mode may own its loop (`battle-engine-ssot.md:64`).
4. **Which existing implementation does it extend?** `IBattleView`
   (`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:17`), the same interface `BattleRunState` and
   `FoggedBattleView` implement, plus the two shipped `IOwnSideOracle` classes. It copies neither.
5. **Does every mode get it?** Every mode already has an `IBattleView`; the lawn was the one place
   without one. This closes that, so the answer is yes after this module, not "lawn-only".
6. **Deterministic and seeded?** It reads no clock and no RNG. It reads live Unity state, which is
   non-deterministic **by construction** — the lawn is the non-deterministic *driver* of deterministic
   mechanisms (`battle-engine-ssot.md:106-111`), and it carries no replay or golden contract
   (`../research/combat-ai/S4-lawn.md:67-68`). Determinism is asserted where it is real: the adapter is
   a pure function of its fixture inputs, which is what every test above exercises.

## Success criteria

1. `StubIntentSource` — unmodified — runs against this view in a Core test and returns a real
   `ActionIntent` for a lawn fixture.
2. A hypnotised unit reads `Ally` to its deploying player and `Enemy` to the other side, with no read
   of the raw board side anywhere in the file (grep-checkable).
3. `ResolveDerived` is called at most once per (actor, frame, revision), proven by call count.
4. A frame with no decision edge touches no board and allocates nothing.
5. All ten `IBattleView` members have an explicit lawn answer, and the four absent ones are `null`/
   neutral by stated decision.
6. The three new Core files are under `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/`, **not** under
   `Match/Ai/`, and `ILawnBoardViewTests.Nothing_under_Match_Ai_may_read_the_board_itself` is green
   and **unmodified** — its pattern list is not widened and its scope is not carved out.
7. No battle, siege or delve golden moves; the suite is run and the result stated.

## Open questions

1. **Does the memo's revision seam block module 19's default-on?** `actor-liveness-refresh` is spec,
   not built (`../lawn-playable/spec-actor-liveness-refresh.md:5`). Options: (a) ship with the seam
   returning a constant, frame-scoped only; (b) block Wave 4 until that module lands.
   **Recommended default: (a)** — a frame-scoped memo is already correct for a single decision, and
   the revision key only extends its life. But module 19 must not ship **default-on** until (b) is
   satisfied, because a decision priced on a frozen Θ is the exact defect that spec measured.
   *Cross-module note for the plan, not a change to that spec.*
   **ANSWERED 2026-09-22 (lane `cai4`):** **both halves of the recommendation are in force.** (a) shipped: the memo is
   frame-scoped with the revision seam returning a constant (`LawnDerivedCache`, `CAI4.1`). And module
   19 is **not** default-on — `CAI5.3` is open and the feature ships `DefaultEnabled = false` — which
   reads the (b) half as a precondition on the flip rather than as a Wave-4 block. `CAI-loop-2`
   measures the memo through the real profiled policy: the demand (derived reads) exceeds the supply
   (resolves), and the supply stays inside the board's own actor count.
2. **Cross-module (module 6):** `AggressionOf` returns an `int` and `AiScoring.EffectiveTier` throws
   outside ±`aggressionRange` (`../combat-ai-ideal.md:290`). This view forwards whatever the Hub
   composed. The saturation onto the closed tier range is `aggression-tier-map`'s, and it must land
   before any content writes `ai.aggression` — noted here only because this view is the lawn's reader.
   **ANSWERED 2026-09-22 (lane `cai4`):** **landed.** `CAI1.13` replaced the throw with a saturating clamp that reports a signed
   `saturatedBy` (`CandidateScorer.EffectiveTier(int, int, int, out int)`) and pins the tier
   vocabulary's width as `2 × range + 1`; `ai.aggression` stays `FlatSum` with no `Cap`. The reader
   this note worried about can no longer make the scorer throw.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: lawn AI read seam, actions/targeting, stats (read-only).
[x] Session boundary: backlog-clean-up-20260920, recorded at tasks/sessions/backlog-clean-up-20260920.json.
    This lane writes only docs/architecture/combat-ai/spec-lawn-*.md.
[x] I read every doc in the §1 row(s): overlay-control-loops.md, battle-engine-ssot.md,
    combat-ai-ideal.md, combat-ai-map.md, AUDIT.md, S4-lawn.md, spec-actor-liveness-refresh.md.
[x] I checked decisions.md for a lock: the "Action selection (battle adoption)" row (:44) locks
    IBattleView as the seam and bloodthirsty/loyal as engine-side wrappers; nothing here touches either.
[x] Every factual claim cites file:line, and every cited file was opened this session.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments (IBattleView's ten members, the two oracles,
    InjectorBoardSnapshot's frame cache, and the uncached ResolveDerived were each read).
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. **Gap named honestly:** this spec authorizes
    no build and ran no test suite; the "no golden moves" claim is written as a claim to verify during
    implementation, with the exact command given, not as a measured result.
[x] Nothing contradicts a §2 invariant. Hot rules 1 (dead ptr skip) and 3 (never await) are honoured;
    no server round-trip exists on this path.
[x] Corrections propagated: none needed — this is a new file and the map row already matches.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal (IBattleView's ten members) is a closed, code-owned contract and
    the test says why.
[x] Event-refreshed cache (§2.16): the derived memo's invalidators are listed in full — frame edge,
    board-snapshot invalidation, and the actor-liveness revision bump — and its KEY SET changes on
    spawn (a new ptr) and on death (InjectorEntityRegistry.Remove, module 19's cleanup). Each has a
    named test. The trigger set is NOT copied from another cache.
[x] No acceptance criterion fixes an ordering that can vary: LiveActorKeys order is the snapshot's own
    and every test that depends on order states it.
[x] This consumes Hub output only (LawnDerivedCache wraps InjectorStatusBridge.ResolveDerived, which
    calls CheatState.ActorHub.ResolveDerived at InjectorStatusBridge.cs:23). No second composer, no
    private fold. BattleStatComposer is not cited as precedent anywhere.
[x] Does not invent or extend a SOLID-violating parallel path: it implements the existing IBattleView
    and composes the two existing IOwnSideOracle implementations rather than forking either.
[x] A new rule has a registry row. RESOLVED (was: "close to the existing guard, not resolved here").
    The guard in question is `Nothing_under_Match_Ai_may_read_the_board_itself`, whose real class is
    `ILawnBoardViewTests` (gk-core/tests/FusionRpg.Core.Match.Tests/Match/Ai/ILawnBoardViewTests.cs:70-86) -- NOT
    `ZombossDeployAiGuardTests`, which is a STALE NAME in the shipped source comment at
    gk-core/src/FusionRpg.Core/Match/Ai/ILawnBoardView.cs:29-31 and no longer exists as a class. That guard
    is left exactly as it is and is NOT widened: this module's three files move to
    Actions/Ai/Lawn/ instead (§Project structure), so its scope is unchanged and the Zomboss
    narrow-view invariant keeps its full strength. The rule this module does add -- "side and
    relation come only from IOwnSideOracle, never BoardEntitySnap.Side" -- is enforced by test 1 plus
    its named mutation (§Testing strategy) rather than a shell guard, and that is the honest fit: it
    is a one-file property, not a folder-wide one. No gk-core/scripts/enforcement-registry.v1.json row is
    proposed, and the reason is stated rather than left blank.
    Owed elsewhere, NOT fixed by this lane: the stale `ZombossDeployAiGuardTests` name in
    ILawnBoardView.cs:29-31 is shipped source, outside this spec lane's paths. It is a one-word doc
    fix for whichever change next touches that file.
```

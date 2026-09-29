# Spec: `commander-direct-orders` (combat-ai module 20)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) rev 3
§6.2a "Orders (D3)" + §10 D3 · **Depends on:** `intent-router` (module 4), `lawn-cast-trigger` (module 19);
reads `profile-schema` (2)'s tuning file and `lawn-held-actions` (16)'s per-ptr held set ·
**Unblocks:** nothing (it is the last module of wave 4) · **Status:** **part built (Core half, CAI4.9, 2026-09-22).** `gk-core/src/FusionRpg.Core/Match/Ai/{LawnOrderQueue,DirectOrderAdmission}.cs` are in — one live order per actor with replacement reporting, the structural cap, every key-set edge, the retryable/terminal split, and all five §2 refusal RULES (the three identity ones take the durable identity as arguments) — with 20 tests at `tests/FusionRpg.Core.Balance.Tests/CombatAi/`. **Owed:** the supply for those three refusals (the two additive `SubjectId`/`ScopeId` fields on `gk-core/src/FusionRpg.Core/Actions/DirectOrder.cs`), the router's forced-intent hook (row 14), the Server endpoint, the Injector host and the two `web/**` files. See `tasks/evidence-fragments/CAI4.9.md`.

## Objective

Owner ruling **D3** is *"both"*: a lawn commander order may be **the commander's own cast** — which
`lawn-interactive`'s `commander-action-bar` already specifies (`../lawn-interactive/spec-commander-action-bar.md:37`,
*"Enqueue off-board commander combat orders onto the lawn via a Band-1 bottom-center hotbar"*) — **or a
direct order telling one specific creature to cast now**. The second kind *"lasts until the cast commits
or times out. The creature's AI resumes underneath"* (`../combat-ai-ideal.md:355-358`), and
*"One router and one candidate path serve both kinds, with no second decision system"* (`:360-362`).

**The mechanism for the second kind already has a designed home and no producer.** `intent-router`
(module 4) ships `DirectOrder` and `IOrderQueue` and makes an order *"a top-rank candidate, not a
bypass"* (`spec-intent-router.md:207-233`), and its own table records the gap this module closes:
*"A player order — Nowhere. `InteractiveIntentSource` (`:119-145`) replaces the whole policy for an
actor; there is no 'order this one creature, AI resumes underneath'"* (`spec-intent-router.md:26`). Its
byte-identity table then states plainly that `IOrderQueue` *"is null for every caller this module ships;
module 20 is the first producer"* (`:279`). **This module is that producer, on the lawn.**

It closes three things, and nothing else:

1. **A transport.** A player action in the browser becomes a `DirectOrder` sitting in a lawn queue, with
   no `await` anywhere between the injector receiving it and a decision reading it.
2. **An identity.** An order names a creature that is still the creature the player pointed at — across a
   transport window whose worst case is the injector's 250 ms inbox poll (`gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs:133-138`)
   plus a 2,000-deep durable server inbox (`gk-core/src/FusionRpg.Server/InjectorCommandInbox.cs:15-17`), against
   an IL2CPP runtime that reuses pointers.
3. **A lifecycle.** The order ends — on commit, on a typed refusal that cannot become true with time, on
   expiry, on the actor's death, or at the board edge — and the player is told which.

It changes no scoring, no gate, no cost, no cooldown and no write path. The commander's **own** casts stay
`lawn-interactive`'s (§9).

## Tech stack

`FusionRpg.Core` (`Match/Ai/` — the queue, the admission rules and the refusal classification: pure,
Unity-free, CI-built, because CI never builds the injector — `../combat-ai-map.md:24-25`),
`FusionRpg.Injector` (one `CheatCommandRunner` verb and the admission adapter), `FusionRpg.Server` (one
endpoint class, the `OverlayEndpoints` shape), `gk-web/web/fusion-rpg-web` (one mutation and two observe
vocabulary members). **No new dependency, no new transport, no new clock, no new kill switch** — the
switch is module 19's, because *"A cast cannot occur without a decision, so a second switch would be a
second answer to one question"* (`spec-lawn-cast-activation.md:173-174`).

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnOrderQueue|FullyQualifiedName~DirectOrder|FullyQualifiedName~IntentRouter"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~LawnOrderEndpoint"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"   # must be UNCHANGED
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-core/scripts/guard-debug-scope.py ; python gk-fusion/scripts/guard-funnel-delta.py ; python gk-fusion/scripts/guard-single-writer.py
cd web\fusion-rpg-web ; npm test -- --run src/ui/lawn ; npm run build
python gk-core/tools/tuning/publish.py combat-ai --label "lawn direct-order lifetime" lawn.order.lifetimeTicks=80
```

⚠️ `publish.py` *"refuses to invent a key by design"* and writes `v{n+1}` of an **existing** domain
(`gk-core/tools/tuning/publish.py:10-11,22-23`). `gk-core/data/tuning/combat-ai.v2.json` (**published by `CAI4.7` + `CAI-F1`**; `CombatAiTuningFiles.Current` — a `v{n+1}` revision carrying THIS module's two keys is still owed, and the H7 blocker this sentence named is closed) is created by `profile-schema`
(module 2) and must already carry this module's two keys — the same dependency module 19 records
(`spec-lawn-cast-trigger.md:453-461`).

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnOrderQueue.cs` | **landed (CAI4.9)** | `IOrderQueue` for the lawn: one live order per actor, admission, expiry, lifecycle — pure |
| `gk-core/src/FusionRpg.Core/Match/Ai/DirectOrderAdmission.cs` | **landed (CAI4.9)** — the vocabulary, the classifier, `IsHeld`, and the `CheckScope`/`CheckSubject` rules | The pure admission rules and the typed refusal vocabulary |
| `gk-core/src/FusionRpg.Core/Actions/DirectOrder.cs` | **the file exists** (CAI1.10); its two additive identity fields are still owed (CAI4.9) | Two additive identity fields on `DirectOrder` (§2) |
| `gk-core/src/FusionRpg.Server/LawnOrderEndpoints.cs` | **landed (CAI4.9)** | `POST /api/lawn/order` → one `CommandDto` through `InjectorCommandSender` (**corrected 2026-09-23, lane `cai3`: the shipped route has no `.direct` suffix — this spec drafted one, and the code plus its two test suites pin the shorter name**) |
| `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs` | changed | One `lawn.order` verb beside the existing non-debug cases (**corrected 2026-09-23**: `LawnOrderEndpoints.CommandName` and `LawnOrderHost.CommandName` are both `"lawn.order"`) |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnOrderHost.cs` | **landed (CAI4.9)** | Admission adapter: stamp the lawn tick, resolve identity, report. **It does NOT mark the actor due** — that is module 19's frame slot, which its own class doc states |
| `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs` | changed | Drop this ptr's order in `Remove` (`:129-146`) / `Clear` (`:148-157`) — module 19 edits the same two methods |
| `gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts` | changed | One `useLawnDirectOrder` mutation, the `sendJson` shape at `:150` |
| `gk-web/web/fusion-rpg-web/src/ui/lawn/lawnInteractiveObserve.ts` | changed | Two members on the closed `LawnInteractiveEvent` union (`:1-15`) |
| `tests/FusionRpg.Core.Balance.Tests/CombatAi/{LawnOrderQueueTests,DirectOrderAdmissionTests}.cs` | **landed (CAI4.9)** | Every rule below, with planted violations |
| `gk-core/tests/FusionRpg.Server.Tests/LawnOrderEndpointTests.cs` | **landed (CAI4.9)** | The endpoint sends exactly one command and awaits nothing else (**corrected 2026-09-23: the file has no `Lawn/` directory**) |
| `gk-core/data/tuning/combat-ai.v2.json` | **published by `CAI4.7` + `CAI-F1`**; these two keys await a `v{n+1}` revision, and the H7 blocker is CLOSED | Two keys in the lawn section |

## The shape

### 1. The path, end to end, and where the awaits stop

```
CellOccupancyDock select (Occupant.ptr + Occupant.instanceId)   web/.../CellOccupancyDock.tsx:13-28,
  + CommanderActionBar arm (slot -> actionId)                   web/.../lawnViewModel.ts:47-74,
                                                                web/.../CommanderActionBar.tsx:19-29
   │  POST /api/lawn/order                                     ── Intent loop (overlay-control-loops.md:83)
   ▼
LawnOrderEndpoints  ->  InjectorCommandSender.SendAsync         gk-core/src/FusionRpg.Server/InjectorCommandSender.cs:32-42
   │                      ├─ InjectorCommandInbox.Enqueue       ...InjectorCommandInbox.cs:23-33  (reliable)
   │                      └─ SignalR "Command" to InjectorGroup ...InjectorCommandSender.cs:36    (best effort)
   ▼
RpgClient `_hub.On<CommandDto>("Command")`                      gk-fusion/src/FusionRpg.Injector/RpgClient.cs:131-146
   or RpgClient.PullPendingCommandsAsync (every 0.25 s)         ...RpgClient.cs:235-255, InjectorLoop.cs:133-138
   ▼  CheatCommandRunner.Enqueue (ConcurrentQueue + id dedupe)  gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:28-43
════════════════════════ every await is above this line ════════════════════════
CheatCommandRunner.Drain()  — MAIN THREAD                       ...CheatCommandRunner.cs:46-52, InjectorLoop.cs:57
   ▼  LawnOrderHost.Admit(...)  -> LawnOrderQueue (Core)
   ▼  module 19 frame slot: due set -> view -> router -> module 18
```

**Two properties of that diagram are load-bearing and both are already true of the shipped code.**

- **`CheatCommandRunner.Drain()` runs at `InjectorLoop.cs:57`, before `KernelDriveHost.Tick` at `:117`.**
  An order admitted this frame is visible to this frame's decision slot. Nothing is scheduled a frame
  late to make the ordering work.
- **The server never waits for the lawn.** `InjectorCommandSender` enqueues to the durable inbox and
  swallows a SignalR failure (`:38-41`, *"inbox poll is the reliable path"*), and the endpoint answers
  `accepted`, not `done` — exactly the honest answer `OverlayEndpoints.cs:24-26` already gives for the
  same class of call (*"we do not wait on the window, so 'accepted' is the honest answer rather than a
  claim that the window is already gone"*). That is `overlay-control-loops.md:87`'s hard ban held:
  **Server FSM must not sit between capture and apply**, and `:164`'s permission used exactly as
  written — the Server may *"Accept **non-combat** Intent"*. Issuing an order is Intent; **resolving**
  it is the injector's, in process.

`OverlayEndpoints.cs` is the precedent to copy rather than re-derive: a route named for the player
action, carrying one named command, over *"the SAME server→injector command seam every other host
command uses… One close path; no second transport"* (`gk-core/src/FusionRpg.Server/OverlayEndpoints.cs:6-16`).

### 2. The order DTO and its identity

Module 4 declares `DirectOrder(string ActorKey, string ActionId, string? TargetKey, long IssuedTick)`
(`spec-intent-router.md:211-212`). On the lawn `ActorKey` **is the ptr** — module 15's view answers
`SideOf(actorKey)` from the ownership oracle keyed by ptr (`spec-lawn-actor-view.md:139-140`) and
`LiveActorKeys` is *"the perspective's ptr list"* (`:186`). A ptr alone is **not** an identity across the
transport window, because IL2CPP reuses pointers and `overlay-control-loops.md:151` (Hot rule 4) exists
precisely for that.

So this module adds **two additive fields**, and they are identity, not payload:

```csharp
// gk-core/src/FusionRpg.Core/Actions/DirectOrder.cs — module 4's file, two fields appended
public readonly record struct DirectOrder(
    string ActorKey,          // module 4: the lawn ptr, NORMALIZED (MatchUniqueBindings.NormalizePtr:234)
    string ActionId,
    string? TargetKey,
    long IssuedTick,          // module 4: stamped in the PLACE'S OWN tick base -- see §4
    // --- module 20 ---
    string SubjectId,         // the DURABLE identity the order was issued against (lawn: instanceId)
    string ScopeId);          // the run the order was issued in (lawn: MatchRuntime.MatchKey)
```

**Why two, and not a validation inside `TryPeek`.** Module 4's Open question 2 asks exactly this and
recommends *"(a) the queue is cleared on the same withdrawal edge as every other per-actor state"*, over
*"(b) an order carries the instance id and is validated at `TryPeek`"*, *"because it reuses the withdrawal
edge that already exists rather than adding a second identity check"* — and hands the decision to this
module (`spec-intent-router.md:434-439`). **This spec takes (a) for the queue's lifecycle and adds the
durable id at ADMISSION only, which is neither of the two options as written and is better than both.**

- (a) is correct and is adopted verbatim for everything **already in** the queue: §6.
- (a) cannot cover the transport window. The withdrawal edge fires while the order is still on the wire;
  the order then arrives *after* it, naming a ptr that a new creature now owns. No queue-clearing edge
  can retract a message that has not been delivered.
- (b)'s cost is a per-decision check on the hot path. Admission is **once per order**, in the main-thread
  drain, and costs one dictionary lookup — so the hazard is closed where it actually is, and the hot path
  is untouched. `TryPeek` stays the three-line non-blocking read module 4 specified.

**Resolution at admission** (`DirectOrderAdmission`, pure; the injector supplies the two lookups):

| Step | Rule | Refusal |
|---|---|---|
| 1 | `ScopeId` equals the live `MatchHost.Runtime.MatchKey` (`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:19-21,119`) | `StaleRun` |
| 2 | `SubjectId` resolves through `MatchUniqueBindingsFacet.TryGet` (`gk-core/src/FusionRpg.Core/Match/UniqueBindings.cs:183`) to a row in phase `Bound` with a non-null `Ptr` | `SubjectGone` |
| 3 | That row's `Ptr` equals the order's normalized `ActorKey` | `SubjectMoved` — the ptr was reused, or the FE's observation is stale |
| 4 | The ptr is live in `InjectorEntityRegistry` | `SubjectGone` |
| 5 | `ActionId` is in that ptr's `FrozenActionSet` (module 16's `LawnHeldActionRegistry`, `spec-lawn-held-actions.md:110`) | `NotHeld` |
| 6 | The queue is below its cap (§3) | `QueueFull` |

Steps 2 and 3 are the whole of the ptr-reuse answer, and they are cheap because
`MatchUniqueBindingsFacet` already maintains `_ptrToInstance` both ways (`UniqueBindings.cs:117-146`,
`:192`). **Order identity is therefore `(matchKey, instanceId)`**, and the ptr is a *claim about the
present* that admission checks rather than trusts.

**Consequence, stated rather than hidden: v1 can only order an actor that has a live `UniqueBinding`.**
That is D6's smart tier — *"Unique creatures (Bound specimens, commanders, deployed uniques)"*
(`../combat-ai-ideal.md:315`), capped at five per side (`:326`) — and it is also exactly what the FE can
name: `Occupant.instanceId` is *"Only from Snapshot Bindings observe — never invent"*
(`gk-web/web/fusion-rpg-web/src/features/lawn/lawnViewModel.ts:71-72`). A general creature has no durable id on
the lawn today, so ordering one is an **open question with a named option** (Open question 1), not a
silent ptr-keyed order with a race in it.

### 3. Queue semantics

```csharp
/// <summary>The lawn's IOrderQueue (spec-intent-router.md:214-220). Not a plan: an order is a
/// STANDING PREFERENCE for one actor's next decision, and the actor has exactly one next decision.</summary>
public sealed class LawnOrderQueue : IOrderQueue
{
    /// <summary>Structural (tunables-ssot.md T2) -- a memory bound on a per-actor map, not balance and
    /// not a progression ceiling. The orderable population is already bounded by D6's five-unique-per-
    /// side deploy cap (combat-ai-ideal.md:326); 16 is that bound with headroom, so the cap can only
    /// ever be reached by a defect, and reaching it is reported rather than absorbed.</summary>
    public const int Cap = 16;

    /// <summary>Structural (spec-intent-router.md:299) -- "a second live order for the same actor is a
    /// queue, and a queue of orders is a plan, which this program does not have." A new order REPLACES.</summary>
    public const int MaxLiveOrdersPerActor = 1;

    public bool TryPeek(string actorKey, out DirectOrder order);   // module 4's contract, non-blocking
    public void Commit(string actorKey);
    public void Expire(string actorKey);
}
```

- **One live order per actor; a new order replaces the old, silently to the queue and loudly to the
  player** — the replaced order emits `superseded` (§7), because an order that vanished with no word is
  the failure the refusal vocabulary exists to prevent.
- **The cap refuses the NEW order, never evicts another actor's.** Evicting a stranger's order to make
  room for yours is a silent cross-actor failure, and `InjectorCommandInbox`'s own overflow
  (`:29-32`, drop-oldest) is the wrong shape here for that reason: that queue holds interchangeable
  messages, this one holds per-actor state.
- **The queue is not a cache.** It holds orders, not a projection of any other state — module 4 already
  records this against DESIGN-GATE §2.16 (`spec-intent-router.md:474-475`). Its **key set** still moves,
  on admission, commit, expiry, death and the board edge, and §6 enumerates all five.

### 4. Expiry, and the one time base

`IssuedTick` is stamped **at admission, on the injector main thread, in lawn ticks**:
`KernelDriveHost.NowTicks / 100` (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:103-104`), the exact
expression `LawnBasicAttackCostCharger.NowTick()` already uses (`:60-61`) and the base module 19 chose
after finding the map's `AdvancedEffectClock` row to be a wall-clock-seeded `DateTimeOffset`
(`spec-lawn-cast-trigger.md:181-195`). **A third lawn time base would recreate D15 — *"one board, two
notions of when"* (`spec-lawn-cast-trigger.md:193-194`) — so the order reads the one the cost ledger, the
cooldown ledger and the trigger already read.**

Three consequences, each deliberate:

1. **The server never stamps the expiry.** A client or server timestamp travels with the order as
   telemetry only; the lawn clock is pause-respecting (`KernelDriveHost.cs:170-176` advances nothing at
   `timeScale 0`) and a wall clock is not, so an order issued and then paused for a minute must still
   have its full life when the board resumes. Reading a wall clock here would silently expire every order
   a player issues before opening a menu.
2. **Expiry is a tick comparison**, module 4's rule verbatim (`spec-intent-router.md:209-210`: *"expiry is
   a TICK comparison, never a wall clock"*), evaluated inside `TryPeek`.
3. **The router instance for the lawn is constructed with the lawn's lifetime**, in lawn ticks. Module 4's
   `orderTimeoutTicks` is a constructor argument (`spec-intent-router.md:90`), and its `5000` seed is
   *"ticks (1 tick = 1 ms, decisions.md Battle time model)"* for turn modes (`:297`). This module supplies
   `80` **lawn** ticks to the lawn router. **One parameter, per-place values — not a second mechanism.**

### 5. An order is a trigger edge, and the lock still holds

Module 19 owns *when* to ask (`spec-lawn-cast-trigger.md:410-413`). An order arriving is an external
event on exactly the footing a first-of-swing record is, so **admission marks the actor due**: it sets the
`Pending` flag on module 19's per-actor trigger state (`spec-lawn-cast-trigger.md:89-98`), which is the
same "hold at N" due flag a refused decision already sets (`:119-123`). The actor is then served by module
19's ordinary FIFO budget (`:199-210`) and must still take a cast token (`:211-224`).

**Why an edge, and not "wait for the next swing".** The OR'd timer `T` is 50 lawn ticks
(`spec-lawn-cast-trigger.md:306`), so an order that waited for the ordinary cadence could sit unconsidered
for five seconds. A player order that takes five seconds to be *looked at* is indistinguishable from a
broken button.

**What the order edge does NOT do, and why each refusal matters:**

| It does not bypass | Because |
|---|---|
| the post-cast lock `L` | `L` is the cadence invariant (`spec-lawn-cast-trigger.md:152-159`); bypassing it makes an order a second cast rate |
| the per-frame decision budget | a structural per-frame cap (`:199-210`); an order that jumped it would let N players' orders unbound the frame |
| the cast-token pool | `:211-224`; a token is the concurrency bound, not a courtesy |
| any `UsabilityEvaluator` gate, the `resolvable-here` filter, the reserve floor or a waste guard | module 4: *"an order never bypasses cost, cooldown or legality, because that would be a second, weaker declaration path"* (`spec-intent-router.md:229-230`) |
| `LawnCastPlan`'s pay-on-commit ordering | `spec-lawn-cast-activation.md:78-92` |

**Cross-module correction owed to module 19 — reported, and now FIXED there.** This module's review of
module 19's carry-over expression found that `state.Swings = Math.Min(state.Swings - n, n)` goes
**negative** when an order-driven cast commits with `Swings < N`, silently delaying the actor's next
natural cast by up to `2N` swings. [spec-lawn-cast-trigger.md](spec-lawn-cast-trigger.md) §3 now carries
`Math.Clamp(state.Swings - n, 0, n)` with the reason in the code comment, and its test 4a plants the
`Math.Min` violation directly. **Nothing is owed here any more**; this paragraph stays as the record of
where the finding came from, because the fix reads as arbitrary without it.

### 6. Death, ptr reuse and the board edge — the full trigger set

Module 4's Open question 2 recommendation, adopted: *"the queue is cleared on the same withdrawal edge as
every other per-actor state"* (`spec-intent-router.md:436-438`). The ideal extends Hot rule 4 in the same
words — *"Grants are withdrawn before a `ptr` is reused (§6 rule 4). This covers any per-actor AI state"*
(`../combat-ai-ideal.md:80-81`; `overlay-control-loops.md:151`).

| Trigger | Effect on the queue | Test |
|---|---|---|
| An order is admitted for `ptr` | upsert (replacing any live order for that ptr) and mark the actor due | ✅ |
| The order produces an intent | `Commit(ptr)` — module 4 calls it (`spec-intent-router.md:218`) | ✅ |
| `nowTick - IssuedTick >= lifetimeTicks` | `Expire(ptr)`, inside `TryPeek` | ✅ |
| A gate refuses with a **terminal** reason (§7) | remove — retrying cannot help | ✅ |
| `ptr` dies | **remove** — the KEY-SET edge, in `InjectorEntityRegistry.Remove` (`:129-146`), beside the shield flush (`:136-142`) and the resource-pool drop (`:143-145`) whose own comment is the reason: *"a reused ptr must not inherit a stranger's drained pool"* | ✅ |
| `ptr` spawns (possibly a reused address) | **remove** any stale entry before the first decision; the board-start barrier `InjectorEntityRegistry.Clear()` (`:148-157`) covers the match case, and admission step 3 covers the within-match case | ✅ both orders |
| Board end / `match.result` | clear — `MatchHost.Apply` already routes both to `EffectRuntime.ClearAll("match")` and nulls `GameHooks.MatchKey` (`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:119-130,171-172`) | ✅ |
| Module 19's kill switch turns off mid-match | clear the queue with the rest of the per-actor state, the `FeatureSwitchEdge.TurnedOff` shape module 19 specifies (`spec-lawn-cast-trigger.md:276-280`) | ✅ |

**No new die hook.** Module 19 gives the reason and this module inherits it verbatim: *"Every death path
funnels through those two methods, which is why a new die hook would be both redundant and easier to
miss"* (`spec-lawn-cast-trigger.md:235-237`). One edit, two neighbours, one reason.

`MatchUniqueBindingsFacet.MembershipChanged` (`gk-core/src/FusionRpg.Core/Match/UniqueBindings.cs:51,146,224`) is
deliberately **not** used as the clearing edge here: it fires on the *binding's* `Bound`/`Cleared`
transitions (`ScopeMembershipEvents.cs:8-15`), which is a different lifetime from the ptr's own. The
inspector's per-actor index uses it (`spec-decision-inspector.md:195-197`) because it indexes bindings; the
order queue is keyed by ptr and therefore uses the ptr's own edge. Both are correct for their key.

### 7. What the player sees when the order does not fire

This is the half an order-as-candidate design usually gets wrong: a refused order that says nothing is
indistinguishable from a broken button, and a refused order that *cancels itself* is indistinguishable
from a bug the first time a cooldown is one tick out.

**The repo already owns the vocabulary, and it already encodes the split.** `UsabilityReason` exists
*"Never a bare boolean: the FE needs to explain a greyed button, and `A7` needs to know whether
re-checking next tick could change the answer — `OnCooldown` and `CannotAfford` become true with time,
`NotBound` never does"* (`gk-core/src/FusionRpg.Core/Actions/UsabilityResult.cs:3-8`). So:

| Class | Members | The order | The player sees |
|---|---|---|---|
| **Retryable** | `OnCooldown`, `CannotAfford`, `MissingStock`, `OutOfRange`, `TooClose`, `NoValidTarget`, `ConditionFailed`, `StanceHeld` | **stays live** until expiry; reconsidered on every edge | the armed slot shows the reason and stays armed. The AI decides underneath meanwhile |
| **Terminal** | `NotBound`, `NotEquipped`, `AlreadyActive` | **removed at once** | the slot disarms with the reason |

That table is a **projection of the existing closed enum** (`UsabilityResult.cs:9-28`), not a second
refusal vocabulary — module 10's boundary forbids one (`spec-decision-inspector.md:376-377`) and this
module honours it. A new `UsabilityReason` member added later must be classified in the same switch, and
the test asserts the switch is **total over the enum** so a new member fails the build rather than
defaulting to "retryable forever".

**The report path is observe-only.** One `lawn.order.*` event per outcome through
`RpgHost.Client?.Enqueue(kind, payload, MatchKey)` (`gk-fusion/src/FusionRpg.Injector/GameHooks.cs:139`) → server
ingest → `WebGroup` `Event`/`EventBatch` (`gk-core/src/FusionRpg.Server/EventIngest.cs:217-219`) → the FE's
existing subscription (`gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx:188-189`). It is
`overlay-control-loops.md:137`'s *"async fork: events → Server / Data (observe, Activity) — **NOT a
decision gate**"*, and nothing on the decision path reads it back.

Kinds, matching the FE's existing closed union (`gk-web/web/fusion-rpg-web/src/ui/lawn/lawnInteractiveObserve.ts:1-15`,
which already carries `order.arm` / `order.intent` / `order.cancel` and gains `order.reject` and
`order.commit`):

| Kind | When |
|---|---|
| `lawn.order.accepted` | admission passed |
| `lawn.order.rejected` | admission refused; carries the §2 refusal |
| `lawn.order.refused` | a gate refused at decision time; carries the `UsabilityResult` and its class |
| `lawn.order.committed` | the order produced an intent that paid and fired |
| `lawn.order.expired` / `lawn.order.superseded` / `lawn.order.dropped` | lifetime end, replacement, actor gone |

```csharp
/// <summary>Structural -- an observability rate bound, not balance. One report per order per DISTINCT
/// reason: an order living 80 lawn ticks is reconsidered on every edge, and an unbounded report would
/// put ~8 identical "on cooldown" rows on the wire per second per ordered actor.</summary>
const int ReportsPerOrderPerReason = 1;
```

### 8. The inspector: an order is a visible decision source

Module 10 records *"every candidate with its gate verdicts and score breakdown, the chosen action and the
top-3"* (`../combat-ai-map.md:55`) in `AiDecisionRecord` (`spec-decision-inspector.md:89-97`), and an
order is already expressible there as the rank-0 `AiCandidateVerdict` carrying its `UsabilityResult`
(`:102-103`). **What is not expressible is whether the chosen action came from the order or from the
profile**, and inferring it from "`Candidates[0]` happens to equal `ChosenActionId`" is exactly the kind
of read-time re-derivation module 10 bans (`spec-decision-inspector.md:268-271`: *"No field is recomputed
at read time"*).

This module therefore **supplies** a decision origin and asks module 10 to **carry** it:

```csharp
/// <summary>Closed vocabulary: where the CHOSEN intent came from. Three members, because the router's
/// chain has three producers (spec-intent-router.md:153-158) once `steered` is folded in as a player
/// source. A fourth member is a reviewed change.</summary>
public enum AiDecisionOrigin { Policy = 0, Order = 1, Steered = 2 }
```

**Corrected 2026-09-23 (lane `cai3`): the MEMBERS above are the code's, not this spec's draft.** The draft
named them `Profile` / `PlayerOrder` / `Fallback`; module 10 shipped `Policy` / `Order` / `Steered`, and the
code is what the tests pin (`AiDecisionOrigin.Policy` in `DecisionInspectorTests`, `.Steered` at the
router's steered wrap, `.Order` from `IntentRouter.Resolve`'s order step). The three-member count and the
closed-vocabulary rule are unchanged; only the spellings were stale.

One field on `AiDecisionRecord`, written from the value the router already resolved — never recomputed.
It is a **cross-module note for module 10** (Open question 3), not a change this module makes to module
10's file.

**Debug scope, named.** The lawn's order queue is readable only through module 10's ring, which is
**Game Injector Debug** scope and banner-labelled (`spec-decision-inspector.md:256-260`,
`guard-debug-scope.py`). Two rules follow from `DESIGN-GATE.md:64` and are restated here because this
module adds the one surface that could break them:

- **The `POST /api/lawn/order` endpoint is not a debug route and must never be one.** It runs the
  real Intent path against a real `UniqueBinding` row that real gameplay created (§2 step 2). It cannot
  invent a subject: an `instanceId` with no `Bound` row is refused, which is the *"must resolve to a row
  real gameplay could have created, never one the debug call invents"* rule held by construction.
- **An accepted order is not evidence that a cast happened.** `accepted` means the command was enqueued.
  Whether the cast resolved is module 18's proof, read back through the normal path
  (`spec-decision-inspector.md:272-274`).

### 9. The boundary with the commander's own casts

| | Commander's own cast | Direct order (this module) |
|---|---|---|
| Owner | `lawn-interactive` (`../lawn-interactive/spec-commander-action-bar.md`) | combat-ai module 20 |
| Subject | the commander, who is *"**off the hex**"* and *"**never** drawn as a lawn tile"* (`:16-19`) — no ptr, no `IBattleView` actor | one deployed creature, a live ptr with a `UniqueBinding` |
| Decision layer | none — the player chose; the Server/injector re-resolve (`:20-22`: *"FE does **not** run A10 / battle A2 range math… Do not say the player 'casts.'"*) | the shared router and the shared core; the order is a candidate, the AI decides underneath |
| Verb | that spec's own | `lawn.order` — **shipped**; this spec drafted `.direct`, and the code plus both test suites pin the shorter name |
| Bar | the same Band-1 hotbar, `CommanderActionBar.tsx:19-29` | the same bar, plus an occupant selected in `CellOccupancyDock` (`:13-28`) |

**One bar, two verbs, distinguished by whether a subject creature is selected.** This module does not edit
`CommanderActionBar.tsx`'s slot, cost, lock or refusal logic — it consumes the armed `actionId` the bar
already produces (`CommanderActionBar.tsx:4-14`) and the `Occupant` the dock already selects.

⚠️ `spec-commander-action-bar.md:6` is *"Draft — pending owner review. **No build authorized until
approved.**"* **This module does not depend on it being built.** It needs the occupant selection and its
own endpoint; if the commander's own-cast half never ships, direct orders still work, and the bar degrades
to the locked-slot state that spec already specifies (`:26`).

## Tunables

`gk-core/data/tuning/combat-ai.v2.json` (**published by `CAI4.7` + `CAI-F1`** — module 2 created the domain; the two keys below are still owed a `v{n+1}` revision, and the H7 blocker is closed, `../combat-ai-ideal.md:436`), lawn section. Neither value is an owner decision
(`../combat-ai-ideal.md:466-467`).

| Key | Unit | Seed | Why this seed |
|---|---|---|---|
| `lawn.order.lifetimeTicks` | lawn ticks (100 ms) | **80** (8 s) | **Derived, not chosen.** An order must survive long enough to be *considered at least once*, or a retryable refusal is indistinguishable from a dropped order. Worst case to the next edge for an actor that just cast is the post-cast lock plus a full timer period: `L + T = 10 + 50 = 60` ticks (`spec-lawn-cast-trigger.md:306-307`). 80 is that bound with ~33% headroom for a budget-deferred frame. It is **not** structural — a balance pass that wants a snappier order moves it, and module 4's own turn-mode seed (`5000` battle ticks = 5 s, `spec-intent-router.md:297`) is the same reasoning in a different base |
| `lawn.order.queueCap` | orders | **16** | **Structural** (comment required). A memory bound on a per-actor map, not a progression ceiling and not a magnitude. The orderable population is already bounded by D6's five-unique-per-side cap (`../combat-ai-ideal.md:326`), so 16 can only be reached by a defect — and reaching it reports `QueueFull` rather than evicting |
| `MaxLiveOrdersPerActor` | count | **1** | **Structural**, module 4's constant reused, not redeclared (`spec-intent-router.md:299`) |
| `ReportsPerOrderPerReason` | count | **1** | **Structural** — an observability rate bound (§7) |

No `Θ`-derived number, no magnitude, no cap on a magnitude:
`../power/ssot-power-scale.md` §11 gains no row.

## Numeric types

- `IssuedTick` and the lifetime are `long` lawn ticks, matching `KernelDriveHost.NowTicks`'s own `long`
  (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:104`). The expiry test is a subtraction of two
  monotonic `long`s on the same base — a board that ran long enough to overflow it would have run for
  ~2.9 × 10^8 years.
- `Cap`, `MaxLiveOrdersPerActor` and the report counter are `int` structural counts with proven small
  bounds, each with the comment saying so.
- No magnitude is computed here, so `python gk-core/scripts/audit-overflow.py` should report no new finding. Run
  it and state the result either way.

## Code style

- **Logic in Core, thin adapter in the injector** — CI never builds the injector
  (`../combat-ai-map.md:24-25`), so `LawnOrderQueue` and `DirectOrderAdmission` are pure and tested, and
  `LawnOrderHost` holds only the two lookups and the report.
- **Fail closed, never throw into the frame.** The `CheatCommandRunner` drain already wraps every command
  in `try/catch` and reports through `CheatState.Error` (`gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:48-51`);
  an admission that throws must be a refusal, not a killed frame.
- **Command verbs are named constants, not bare literals** — the reason `OverlayCommandNames.Hide` exists
  rather than `"overlay.hide"` inline (`gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:107-112`).
- **Indexed `for` over `IReadOnlyList<T>`, never `foreach`** — the router sits on the same path and
  `spec-intent-router.md:306-308` names the boxed enumerator as the forbidden per-decision allocation.
- **A struct, no allocation on the hot path** — `DirectOrder` is a `readonly record struct` (module 4), and
  `TryPeek` returns it by `out` rather than boxing, the same discipline `ScopeMembershipEvent` documents
  (`gk-core/src/FusionRpg.Core/Match/ScopeMembershipEvents.cs:36-38`).
- **`ActionIntent` stays a struct and `None` stays in the value** (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:13-18`);
  nothing here returns `ActionIntent?`.
- **Every structural constant carries a comment saying why it is structural.**

## Testing strategy

Core, in memory, over a fake clock and fake lookups. No game, no server, no disk
(`docs/contributing/testing-standard.md`).

| # | Test | Asserts the contract |
|---|---|---|
| 1 | An admitted order is returned by `TryPeek` for its actor and for no other actor | The queue's basic contract |
| 2 | A second order for the same actor **replaces** the first and emits `superseded`; the first is never returned again | `MaxLiveOrdersPerActor = 1`, and the replacement is reported |
| 3 | An order whose `ScopeId` is not the live run is refused `StaleRun`. **Planted violation:** removing the check lets an order issued in the previous match command a creature in the next one | §2 step 1 |
| 4 | An order whose `SubjectId` resolves to a binding whose `Ptr` is a *different* address is refused `SubjectMoved`; the same order with a matching ptr is admitted | §2 step 3 — the ptr-reuse answer, asserted directly rather than argued |
| 5 | An order for an `instanceId` with no `Bound` row is refused `SubjectGone` — never admitted against a ptr the FE supplied | The debug-scope rule as a test: admission cannot invent a subject |
| 6 | An order for an action not in the ptr's `FrozenActionSet` is refused `NotHeld` | §2 step 5 |
| 7 | `TryPeek` at `IssuedTick + lifetime - 1` returns the order; at `+ lifetime` it expires and returns false. No `DateTimeOffset` / `DateTime` is read anywhere on the path | Expiry is a tick comparison (`spec-intent-router.md:209-210`) |
| 8 | An order refused with a **retryable** reason stays live and is offered again on the next edge; one refused with a **terminal** reason is removed | §7's split, both directions |
| 9 | The refusal classifier is **total over `UsabilityReason`** — a member with no classification fails compilation/test | The closed vocabulary, pinned because the code owns it (`validation-ssot.md`) |
| 10 | The same reason reported twice for one order puts **one** event on the wire; a different reason puts a second | `ReportsPerOrderPerReason` |
| 11 | Death removes the order; a **reused ptr address** finds no stale order. Spawn-then-death and death-then-spawn both leave nothing | Hot rule 4 (`overlay-control-loops.md:151`), order-independent |
| 12 | The board edge and the kill switch turning off each clear every order | §6's last two rows |
| 13 | At `Cap`, a **new** order is refused `QueueFull` and **no existing** order is evicted | The cross-actor failure this refuses |
| 14 | An order that clears the gates wins over the profile's own row 0; the identical order that fails a gate does not fire and the policy's own choice is returned | Module 4's *"a top-rank candidate, not a bypass"* (`spec-intent-router.md:223-230`), from this module's producer side |
| 15 | An order-driven commit calls `Commit(actorKey)` exactly once and the order is gone afterwards | Module 4's `Commit` contract (`:218`) |

**Never asserted:** how many orders a real match produced, how long one lived in wall time, any authored
action name or description, or any score value — readings and generated text (`validation-ssot.md`;
`../combat-ai-map.md:32-33`).

**Server:** `LawnOrderEndpointTests` asserts the route sends exactly one `CommandDto` through
`InjectorCommandSender` and returns without awaiting anything else — the shape
`OverlayLeaveEndpointsTests` already proves for `/api/overlay/leave`
(`gk-core/src/FusionRpg.Server/OverlayEndpoints.cs:15`).

**Goldens: byte-identical, and verified rather than assumed.** No battle, siege or delve path is touched;
the lawn has no golden contract (`../research/combat-ai/S4-lawn.md` as module 19 cites it,
`spec-lawn-cast-trigger.md:377-378`). The two additive `DirectOrder` fields live on a type module 4
creates and that no golden serialises. Run
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` and state the result
either way.

## Boundaries

**Always**

- Resolve identity at admission through `(matchKey, instanceId)`; treat the ptr as a claim to check.
- Stamp `IssuedTick` in lawn ticks (`KernelDriveHost.NowTicks / 100`) on the main thread, at admission.
- Drop the order on the same edges every other per-actor AI state is dropped —
  `InjectorEntityRegistry.Remove`/`Clear`, the board edge, the kill switch.
- Classify every refusal through `UsabilityReason`, and keep the classifier total over the enum.
- Report every outcome as observe-only, rate-bounded, and never read it back on the decision path.
- Answer the endpoint `accepted`, never `done`.

**Ask first**

- Extending orders to actors with no durable binding (Open question 1) — it needs a ptr generation
  counter that does not exist.
- Letting an order bypass the post-cast lock `L` (§5) — that is a cadence change, not a tuning one.
- Any *queue* of orders per actor, or an order that names more than one action. That is a plan, and
  `spec-intent-router.md:299` refuses it by construction.

**Never**

- Let an order bypass a gate, a cost, a cooldown, the reserve floor, a waste guard, the decision budget
  or the token pool (`spec-intent-router.md:229-230`).
- Await SignalR, HTTP or SQLite anywhere below `CheatCommandRunner.Drain` (`overlay-control-loops.md:150`,
  Hot rule 3), or put a Server FSM between capture and apply (`:87`).
- Read a wall clock for `IssuedTick` or for expiry.
- Introduce a third lawn time base, a second transport, a second kill switch, or a second refusal
  vocabulary.
- Build a second decision path for orders — D3 is explicit: *"One router and one candidate path serve
  both kinds, with no second decision system"* (`../combat-ai-ideal.md:361-362`).
- Present an accepted order, or an inspector record of one, as proof that a cast resolved
  (`DESIGN-GATE.md:64`).
- Evict another actor's order to admit this one.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** **None.** Every line sits on the **deciding** side of §3c,
   which the closed register does not cover (`battle-engine-ssot.md:160-200`). It touches responsibility 8
   (actions) and 5 (targeting) only at their deciding halves — *"which action to use"* and *"which target
   to pick"* — and never at *"cost, cooldown, effect, outcome"* or *"whether the pick is legal"*
   (`:193-196`).
2. **Does it DECIDE or RESOLVE?** **Decide**, and only by *supplying a candidate*. It never returns an
   `ActionIntent` itself: it puts a `DirectOrder` where module 4's router reads it, and module 4 offers it
   to the policy under the ordinary gates. The engine's contract is untouched —
   `IIntentSource.TryDeclare(actorKey, nowTick)` still returns the whole answer
   (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:29-37`).
3. **Mechanism or loop?** **Both halves, split the way §2 requires** (`battle-engine-ssot.md:60-68`). The
   *order contract* — `DirectOrder`, `IOrderQueue`, "a top-rank candidate that never bypasses a gate" — is
   a **mechanism** and is module 4's, shared by every place. The *lawn transport, admission and order
   edge* are this module's contribution to the **lawn's loop**, which §2 permits a mode to own: *"a
   turn-based delve and a real-time lawn cannot share a scheduler"* (`:63`). There is no second scorer, no
   second gate and no second declaration path.
4. **Which existing implementation does it extend?** Four, all by calling: module 4's `IOrderQueue`
   (`spec-intent-router.md:214-220`), the shipped server→injector command seam
   (`InjectorCommandSender.cs:32-42` + `InjectorCommandInbox.cs:23-44` + `CheatCommandRunner.cs:28-52`),
   `MatchUniqueBindingsFacet` for identity (`UniqueBindings.cs:183,192`), and module 19's trigger, budget
   and token pool. It copies none of them and adds no transport.
5. **Does every mode get it?** **The mechanism already does** — module 4 ships `IOrderQueue` for every
   place, and its own tests cover an order recorded as a `Player` decision in a replay mode
   (`spec-intent-router.md:333`). This module ships the **lawn producer**, because the lawn is the only
   place that had no order path at all; battle and delve already have `InteractiveIntentSource`
   (`spec-intent-router.md:26`). §5 Q5 warns that a "lawn-only" answer will be refused — this one survives
   because what is lawn-only is the *transport*, and every mechanism it feeds is shared.
6. **Is it deterministic and seeded?** It reads **no RNG at all**. Expiry is a `long` tick comparison on
   the engine's pause-respecting simulated clock, never a wall clock. Determinism is
   `(setup, seed, human trace, profile version, BattleEnvironment.Stamp)` (`../combat-ai-map.md:22-23`),
   and **a direct order is an external input exactly like a human declaration**: where a replay contract
   exists, module 4 records it into `DecisionTrace` with `DecisionSource.Player`
   (`spec-intent-router.md:235-239`; `gk-core/src/FusionRpg.Core/Battle/Timeline/DecisionTrace.cs:5-9,23-24,50-55`,
   whose own comment is the rule this obeys — *"Recorded as a DECISION AT A TICK, never re-measured on
   replay"*, `:13-19`). **The lawn has no replay contract**, so the lawn queue records nothing and this
   spec claims nothing about replaying a lawn match. The lawn is the non-deterministic driver of
   deterministic mechanisms (`battle-engine-ssot.md:106-111` as module 19 cites it,
   `spec-lawn-cast-trigger.md:424-428`) — stated, not overclaimed.

## Success criteria

1. A player selects a deployed unique creature on the lawn, arms an order slot, and that creature casts
   that action on its next decision edge — through the shared router, the shared gates, module 18's
   activation and the existing Funnel → `EntityStatWriter` tail, with no new write path.
2. Nothing between `CheatCommandRunner.Drain` and the cast awaits SignalR, HTTP or SQLite, and the server
   endpoint returns without waiting for the lawn.
3. An order issued against a creature that died before delivery is refused `SubjectGone` or
   `SubjectMoved`, never executed against whatever now owns that pointer — proven by a planted violation
   (test 4), not by argument.
4. An order that fails a gate does not fire, the AI decides underneath, and the player is told the reason;
   a retryable reason keeps the order armed and a terminal reason disarms it.
5. An order expires on a tick comparison, and pausing the game does not consume its life.
6. Death, ptr reuse, the board edge and the kill switch each leave no stale order, in either spawn/death
   order.
7. The decision inspector shows the order as the decision's origin and as a rank-0 candidate with its gate
   verdict — and never synthesises one.
8. `guard-debug-scope.py`, `guard-funnel-delta.py` and `guard-single-writer.py` green; no golden moves,
   with the suite run and the result stated.
9. The commander's own-cast path is neither required nor changed by this module.

## Open questions

1. ~~**Can a general (performance-tier) creature be ordered?**~~ **CLOSED — owner ruling 2026-09-20:
   uniques only in v1** (option (a) below). A general creature keeps running its own AI; the spawn
   generation counter (option (b)) is a named follow-up, not this module's work, and it is revisited only
   if players ask to order general creatures. The record below is the reasoning that led there.

   **Can a general (performance-tier) creature be ordered?** §2 admits only an actor with a live
   `UniqueBinding`, because that is the only durable lawn identity that exists
   (`UniqueBindings.cs:183`; `lawnViewModel.ts:71-72`). Options: (a) uniques only in v1 — D3's *"a
   specific creature"* is satisfied, D6 already makes uniques the smart tier
   (`../combat-ai-ideal.md:315`), and the FE can only name those; (b) add a per-ptr **spawn generation
   counter** to `InjectorEntityRegistry` so a ptr-keyed order can detect reuse, and admit any RPG-backed
   actor. **Recommended default: (a)**, with (b) as a named follow-up — (b) is a lifecycle change to a
   type two other modules are already editing in the same wave, and it should not ride in on an orders
   feature. **Cross-module note for `creature-lawn-deploy`:** if general creatures gain a durable lawn
   identity for another reason, (b) becomes free and this restriction should be revisited.
2. ~~**Module 19's carry-over expression goes negative on an order-driven cast (§5).**~~ **CLOSED —
   fixed in module 19, not open here.** The finding was real: `Math.Min(state.Swings - n, n)` assumed
   the cast happened at or above `N` swings, which an order-driven cast need not.
   [spec-lawn-cast-trigger.md](spec-lawn-cast-trigger.md) §3 now specifies
   `Math.Clamp(state.Swings - n, 0, n)` — option (a), for the reason given when it was raised: option
   (b) (leave the counter untouched by an order-driven cast) would make an order a *free* cast on top
   of the natural one, which is a balance decision wearing a bug's clothes. Module 19 also gained a
   test for it (its test 4a, the order-driven case at `Swings = 2, N = 7`, with the `Math.Min`
   violation planted). **This module depends on that fix having landed and adds nothing of its own to
   it**; the record of where it came from is in §5.
3. **`AiDecisionRecord` has no decision-origin field (§8).** Options: (a) module 10 adds
   `AiDecisionOrigin Origin` (three members, closed); (b) the inspector infers the origin from
   `Candidates[0]`; (c) the order is not distinguishable in the record. **Recommended default: (a)** —
   (b) is read-time re-derivation, which `spec-decision-inspector.md:268-271` forbids, and (c) fails
   D4's *"see the full mechanism"* for the one decision a player actually caused. **Cross-module note
   for `decision-inspector` (module 10).**
   **ANSWERED 2026-09-22 (lane `cai4`):** **option (a) landed.** `Actions/Ai/AiDecisionRecord.cs` now declares
   `enum AiDecisionOrigin { Policy = 0, Order = 1, Steered = 2 }` with `AiDecisionRecord` carrying it
   (`CAI2.4`), and this module supplies the value rather than module 10 inferring it. The three members
   are pinned by their own count test, so a fourth is a reviewed change.
4. **Should an order ever be issued from the injector's own debug surface?** No route is specified here
   and none should be added casually: an injector-side "order this ptr" entry point would be Game
   Injector Debug scope and could fabricate a subject, which is exactly the 2026-09-13 shape
   (`DESIGN-GATE.md:64`). If a debug order is ever wanted, it must adapter-wrap
   `POST /api/lawn/order` and be banner-labelled, never re-implement admission. Named so a later
   session does not add one by reflex.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: the battle decision seam (IIntentSource / the router),
    the lawn AI loop, the injector<->game command pipeline (Intent loop), match/actor lifecycle and ptr
    reuse, injector debug scope, the lawn FE, tunables.
[~] I established and recorded this session's boundary: this is a /spec authoring lane under session
    backlog-clean-up-20260920, whose record exists (tasks/sessions/backlog-clean-up-20260920.json,
    named by combat-ai-map.md:12). I did NOT run session-boundary-check.py -- this lane is instructed
    to run no repo mutations and writes only this one spec file. GAP NAMED.
[x] I read every doc in the §1 row(s) for those subsystems, this session: DESIGN-GATE.md (§1 rows for
    "anything at all", battle, battle/turns, live-probe; §5 in full), overlay-control-loops.md in full
    (§3, §6 rules 1-7, §7), battle-engine-ssot.md (§2 incl. the 2026-09-16 clock ruling, §3c, §5, §7),
    combat-ai-map.md, combat-ai-ideal.md rev 3, and the four sibling specs this module builds on
    (intent-router, lawn-cast-trigger, lawn-cast-activation, decision-inspector) plus profile-schema,
    lawn-actor-view, lawn-held-actions, core-scorer and resolvable-here for their contracts, and
    lawn-interactive/spec-commander-action-bar.md in full.
[x] I checked decisions.md for a lock covering this: row 44 (Action selection) locks the
    IIntentSource seam as battle's live targeting path and names the next RulesetVersion trigger
    ("a real divergent multi-action loadout reaching a live battle") -- which is module 14's cause, not
    this one. No row locks a lawn order path, a command verb, or an Intent transport.
[x] Every factual claim cites file:line, and every cited file was opened in this session -- including
    RpgClient's SignalR Command handler and HTTP inbox poll, CheatCommandRunner's Enqueue/Drain and its
    pvz.spawn.extra and overlay.hide verbs, InjectorLoop's tick ORDER (drain at :57 before the kernel
    at :117), InjectorCommandSender/Inbox, OverlayEndpoints, MatchHost.Apply's match-end clearing,
    UniqueBindings' bind/clear/lookup and MembershipChanged, ScopeMembershipEvents, IntentSource,
    DecisionTrace, UsabilityResult/UsabilityEvaluator, InjectorEntityRegistry.Remove/Clear,
    KernelDriveHost.NowTicks, LawnBasicAttackCostCharger.NowTick, GameHooks' event enqueue,
    EventIngest's WebGroup sends, CommandDto, publish.py, and the four FE files.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the *(2026-09-22:
    the queue, the admission rules and their tests have since landed; the marker now applies only to the
    Server, Injector, Contracts and web rows)*
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses. **Updated 2026-09-23 (lane
    `cai3`): the Server endpoint, the Injector host and their tests have landed too, so the only markers
    left are the two `web/**` rows and the owed tuning revision — and this spec's own scope audit now
    reports D1 0, D2 0, D3 0, D4 0.**
[x] I verified claims against CODE, not comments. The two that matter most are both NEGATIVE checks:
    (1) the frame ORDER that makes "admitted this frame, decided this frame" true was read off
    InjectorLoop.Tick's body (:57 vs :117), not inferred from any doc; (2) Occupant.instanceId's own
    comment ("Only from Snapshot Bindings observe -- never invent") was checked against
    MatchUniqueBindingsFacet's actual bind path before the identity design was built on it.
[x] I read the surrounding section of every rule I quoted -- overlay-control-loops §6 rules 1-7 and §7
    in full (not only the "never await" line), battle-engine-ssot §2's mechanism/loop paragraph and
    §3c's consequences table, and UsabilityResult's own header paragraph before using its
    "becomes true with time" distinction as the retryable/terminal split.
[~] I tested (not assumed) any constraint I am reporting. GAP NAMED: no suite, build or probe was run
    in this spec session, by instruction. The golden claim is written as a command to run with the
    result stated either way, and the byte-identity argument is structural (nothing outside
    Core/Match/Ai, one additive record, no battle path touched), stated as a claim to verify.
[x] Nothing contradicts a §2 invariant. Hot rules 1-4 and 7 are each honoured and cited by line; the
    Intent loop's §7 permission ("accept non-combat Intent") is quoted with its own "must not block or
    await before injector Hot apply" sibling, not in isolation.
[x] Corrections propagated: Open question 2 reports a real defect found in a SIBLING spec's shipped
    expression (module 19's negative carry) rather than absorbing it; Open question 3 hands module 10
    the one field this module needs; §2 resolves module 4's Open question 2 explicitly and says why it
    takes neither of the two options as written.
[x] No assertion pins a derived-population count, an item total, generated name/description text, or a
    per-cycle outcome. The pinned literals are the closed refusal vocabulary's totality over
    UsabilityReason (a vocabulary the code owns, UsabilityResult.cs:9-28) and AiDecisionOrigin's three
    members; each test states why.
[x] Event-refreshed cache (§2.16): the order queue is NOT a cache -- it holds orders, not a projection
    of other state (spec-intent-router.md:474-475). Its KEY SET nonetheless moves, and §6 enumerates
    all eight triggers INCLUDING both key-set edges (a ptr entering on spawn, a ptr leaving on death)
    plus the board edge and the kill switch, each with a named test, and the spawn/death pair is
    tested in both orders.
[x] No acceptance criterion silently fixes an ordering that can vary in real play. Death/spawn is
    explicitly order-independent and both directions are tested (test 11). The one order that IS fixed
    -- drain before kernel tick -- is not variable: it is the shipped body of InjectorLoop.Tick, cited
    by line, and success criterion 1 depends on it rather than assuming it.
[x] Produces/consumes no actor combat or derived magnitude, and composes nothing. It carries an action
    id and a target key; every number the cast produces is authored atoms resolved by the shipped
    dispatcher through module 18. ActorHub is untouched; BattleStatComposer is not cited.
[x] Does not invent or extend a SOLID-violating parallel path. It is the FIRST PRODUCER of an existing
    contract (spec-intent-router.md:279), and it explicitly refuses a second decision system, a second
    transport, a second clock, a second kill switch and a second refusal vocabulary.
[~] A new rule has a registry row. GAP NAMED: two rules here want enforcement -- "an order never
    bypasses a gate" and "an order's subject is resolved through a durable binding, never a bare ptr"
    -- and both are covered today only by this module's planted-violation tests (4, 5, 14). The debug-
    scope half IS guarded (gk-core/scripts/guard-debug-scope.py, already wired into deploy-play.py). Whether
    the other two earn a gk-core/scripts/enforcement-registry.v1.json row or a guard script is a plan
    decision, unresolved here.
```

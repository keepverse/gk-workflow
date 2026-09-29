# Spec: `lawn-held-actions` (combat-ai module 16)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `profile-schema` (module 2) · **Unblocks:** `lawn-cost-authority` (module 17),
`lawn-cast-activation` (module 18) · **Status:** **part built (Core half, CAI4.2, 2026-09-22).** `gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs` is in — the per-key per-match `FrozenActionSet`, the compile-and-order pass, empty-for-an-unknown-key and the loud-once refusal — with 13 tests at `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs` (this row's own `tests/FusionRpg.Core.Tests/Match/Ai/` path is outside that lane's fence; moving them is `CAI-tests-1`). **Owed:** every Injector and Server row below, which is `CAI4.3` — the ptr registry and the Cold push are what give the store a production host. See `tasks/evidence-fragments/CAI4.2.md`.

## Objective

**No lawn actor is associated with a compiled action list, ever.** The injector's entire
`CompiledAction` surface is one hand-built row: `LawnBasicAttackRow.TryGet()`
(`gk-fusion/src/FusionRpg.Injector/Actions/LawnBasicAttackRow.cs:31`, built from the shared
`BasicAttackFactory` at `:38`). Grep under `gk-fusion/src/FusionRpg.Injector` finds zero hits for
`FrozenActionSet`, `ActionCatalog`, `HeldAction`, `heldActions`, `LoadoutRuntime` or `EquippedAction`
(`../research/combat-ai/S4-lawn.md:35`). That is the lane's real gap: not a missing wire, but a missing
**feed** — nothing on the lawn ever asks "what can this creature cast".

Battle has the feed and it is the one to reuse, not re-derive.
`BattleRunState` compiles each actor's `EquippedActionIds` once at setup into a preference-ordered
`CompiledAction` list and stores it per actor key
(`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:226,540-596`), then hands it out through
`HeldActionsOf` (`:873-882`) — which is the member `IBattleView.HeldActionsOf` exposes
(`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:39`) and the only thing `StubIntentSource` iterates
(`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:44,64-75`). The assembly half is already generic and
persistence-free: `ActionSetAssembler.Assemble(basics, liveGrants, isDefaultAttackEligible)`
(`gk-core/src/FusionRpg.Core/Actions/Grants/ActionSetAssembler.cs:41-45`) wrapped by `FrozenActionSet`
(`gk-core/src/FusionRpg.Core/Actions/Grants/FrozenActionSet.cs:18-46`), whose whole job is the **one snapshot
moment** (`:3-8`).

This module gives the lawn a per-ptr `FrozenActionSet` fed through the **Cold** loop, and drops it on
death before IL2CPP reuses the ptr.

## Tech stack

`FusionRpg.Core` (the per-match keyed set store; Unity-free, CI-built),
`FusionRpg.Injector` (ptr binding on the existing record-then-drain frame slot), and
`FusionRpg.Server` (the Cold push, beside the two rehydrate pushes that already exist). No new
transport: `RpgHub` already enqueues a command into `InjectorCommandInbox` and broadcasts it on the
`Command` channel (`gk-core/src/FusionRpg.Server/RpgHub.cs:73-85` for the patron push, `:98-110` for the grant
snapshot), and `CheatCommandRunner` dispatches by command name
(`gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:651-759`). No new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnHeldAction|FullyQualifiedName~FrozenActionSet|FullyQualifiedName~ActionSetAssembler"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~LawnHeldActionPush"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-core/scripts/guard-actor-hub.py ; python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-secondary-no-unity.py
```

No tuning publish: no tunables (see below).

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnHeldActionSets.cs` | **landed (CAI4.2)** | Per-match store keyed by species / bound instance; assembly, compile and preference order, all Unity-free |
| `src/FusionRpg.Injector/Effects/LawnHeldActionRegistry.cs` | **new; does not exist yet** | `ptr → set` binding, bound in the frame drain, dropped on death |
| `gk-core/src/FusionRpg.Server/RpgHub.cs` | changed | One more Cold push, the same shape as `PushPatronAsync` (`:73-85`) |
| `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs` | changed | One more command case beside the existing non-debug cases (`:651-759`) |
| `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs` | changed | Drop the ptr's entry in `Remove` (`:129-146`) and `Clear` (`:148-157`) |
| `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnHeldActionSetsTests.cs` | **landed (CAI4.2)** | Freeze, order, sharing and fallback contracts |

## The shape

### Where the set comes from: Cold, per match, per key — never per ptr from the server

The server owns both inputs. `SpeciesBasicsRow`
(`gk-core/src/FusionRpg.Core/Actions/ActionRow.cs:162`) is read from SQLite by
`RpgStore.GetSpeciesBasics(speciesKey)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Actions.cs:673`), and the
live `rpg_action_grant` rows are the `liveGrants` argument `ActionSetAssembler.Assemble` already takes
(`ActionSetAssembler.cs:36-38`: *"a withdrawn row must never reach here"*). The server therefore:

1. assembles through `FrozenActionSet.FreezeAtRunStart(basics, liveGrants, isDefaultAttackEligible)`
   (`FrozenActionSet.cs:26-28`);
2. resolves each `AssembledAction.ActionId` (`ActionSetAssembler.cs:16`) to a `CompiledAction` through
   the same `ActionCatalog` path battle uses (`BattleRunState.cs:582-640`), refusing loudly on an id
   the catalog does not know — the same posture `BattleRunState.cs:556-559` already takes;
3. sorts once by `ActionTagPreference`, so the pushed list is already preference-ordered;
4. pushes the compiled list keyed by **species key** and, where one exists, by **Bound instance id**.

**The server never sees a ptr**, and must not: ptr identity is `MatchRuntime` RAM, not durable
(`overlay-control-loops.md:99,105`). Binding a set to a ptr is the injector's job.

This is the **Cold** loop doing exactly what it is for: *"Catalog / grant push at deploy"* is listed as
Cold → Hot (`overlay-control-loops.md:187`), seconds of latency are fine (`:82`), and the push
rehydrates on reconnect the same way the patron and grant-snapshot pushes already do
(`RpgHub.cs:71-72`: *"A fresh inject/reconnect always receives the current…"*). Nothing about this path
touches the hit path, so the §6.10/§7 ban is untouched.

### Freezing, and what "the run" means on a lawn

`FrozenActionSet` is deliberately a refusal, not a cache: `Snapshotted()` *"explicitly does NOT
re-assemble"* (`FrozenActionSet.cs:30-36`) and only `RefreshAtNextRunStart` re-reads (`:38-45`). On the
lawn, **a run is one match**. That is not a new decision — it is the lifecycle the lawn's resource
pools already state: *"match-scoped and full at spawn… there is no cross-match persistence"*
(`gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs:38-45`).

So:

- One `FrozenActionSet` **per key per match**, frozen when the key is first pushed for that match.
- A creature spawning mid-match references the already-frozen set for its key. It does **not** trigger
  a fresh assembly, which is both the freeze rule and the reason N spawns in one frame cost one
  assembly rather than N.
- A grant arriving mid-match applies **at the next match**. `RefreshAtNextRunStart` is called at
  `board.start` and nowhere else.

### Binding a ptr, on the slot that already exists

`LawnHeldActionRegistry` is `ptr → FrozenActionSet` (a reference to the shared per-key set, never a
copy). It binds in the **same record-then-drain slot** `LawnBasicAttackGrantBinder.Tick` occupies
(`gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs:101`), for the reason that class documents verbatim:
resolving inline from a spawn hook forces one board capture per spawn, because every spawn invalidates
the frame cache first (`LawnBasicAttackGrantBinder.cs:10-19`).

Resolution of ptr → key reuses what already exists and adds no lookup of its own:

| Step | Existing mechanism |
|---|---|
| ptr → Bound instance id | the injector's binding cache, the same one `UniqueBoundLoadout` reads (`gk-fusion/src/FusionRpg.Injector/CheatState.cs:280-285` — `ResolveBoundInstanceId`, which reads `MatchHost.Runtime`'s ptr→binding index, never a second lookup) |
| ptr → (side, gameTypeId) → species id | `CheatState`'s lazily built lawn element/species index (`gk-fusion/src/FusionRpg.Injector/CheatState.cs:135-152`) |
| a ptr the board does not know **yet** | requeue for a bounded number of frames, exactly as `LawnBasicAttackGrantBinder.TryBindOrRequeue` does (`:170-182`), for the spawn-hook race that class documents at `:21-38` |

**Instance key wins over species key.** A Bound specimen's own loadout is its own; falling back to its
species' set would give a built specimen a stranger's kit.

### Dropping it before the ptr is reused

`overlay-control-loops.md:151` (Hot rule 4): *"Withdraw `entity:{ptr}` grants on die **before** IL2CPP
reuses the ptr."* The ideal extends that to AI state explicitly: *"This covers any per-actor AI state"*
(`../combat-ai-ideal.md:81`).

The drop lands in `InjectorEntityRegistry.Remove(ptr)`
(`gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs:129-159`), beside the shield flush (`:132-139`)
and the resource-pool drop (`:143-145`), whose own comment is the reason: *"a reused ptr must not
inherit a stranger's drained pool"* (`:143-144`). Every death path funnels through that method, which
is why adding a fourth line there is correct and adding a new die hook would not be.

`InjectorEntityRegistry.Clear()` (`:148-157`) drops every entry at the board edge, alongside the shield
and pool clears already there.

⚠️ **The registry holds a reference, so the drop is a dictionary remove — there is nothing durable to
withdraw here.** The per-actor state that *does* need releasing on death (the swing counter, the cast
token) is module 19's, and lands on the same line for the same reason. This spec names the obligation;
it does not implement module 19's half.

### The basic attack is never in this registry

`LawnBasicAttackRow.TryGet()`'s row (`LawnBasicAttackRow.cs:31`) is **not** added to any held set. It is
the vanilla swing the rider observes and charges
(`LawnBasicAttackCostCharger.ShouldApplyRider`, `:135-168`), not a candidate the AI chooses between.
The ideal's own framing is *"a creature casts **between** basic attacks"*
(`../combat-ai-ideal.md:47`).

This is the load-bearing boundary with modules 17 and 18: an actor whose species has no pushed set gets
an **empty** held list, and `StubIntentSource` answers `ActionIntent.None`
(`StubIntentSource.cs:45`: *"cannot act at all"*). That is the correct "this creature has no kit"
answer. Falling back to the basic attack would make the AI re-cast the vanilla swing, double-charging
it through a path that already charges it.

### Failing loudly, once

Construction failure follows the established injector shape exactly: report once through `RpgHost.Log`,
never retry, never throw per frame — `LawnBasicAttackRow.TryGet` (`:31-51`) and
`LawnBasicAttackCostCharger.TryGetGate` (`:71-120`) both do this, and both say why: *"a silent per-hit
skip is indistinguishable from working, and a per-hit exception would crash the lawn on every swing"*
(`LawnBasicAttackRow.cs:19-20`).

## Tunables

**None.** No number here would be changed by a balance pass. Which actions a creature holds is content
(seed data and grant rows); the ordering vocabulary (`ActionTag`, `ActionTagPreference`) is a closed,
code-owned vocabulary; the requeue bound copies `LawnBasicAttackGrantBinder.MaxRetryFrames`
(`:52-56`), which that file already labels *"structural retry bound, not a balance tunable"*.

## Code style

- Assemble and sort **once per key per match**, never per decision —
  `StubIntentSource.cs:23-25` states the rule and the reason (*"sorting per call would be the exact
  per-decision allocation this module's own zero-allocation acceptance line forbids"*).
- Record-then-drain for anything touching the board; O(1) on the record side
  (`LawnBasicAttackGrantBinder.QueueSpawn`, `:127-131`).
- Loud once, never retried, on construction failure.
- Core holds the logic; the injector holds the ptr binding only.

## Testing strategy

Core tests over in-memory fixtures; server tests over the push shape. No disk store
(`docs/contributing/testing-standard.md`).

| # | Test | Asserts the contract |
|---|---|---|
| 1 | Assembling the same `(basics, liveGrants)` twice yields the same ids in the same order | Deterministic, preference-ordered once |
| 2 | A grant added after the freeze does **not** appear in `Snapshotted()`; it does after `RefreshAtNextRunStart` | `FrozenActionSet.cs:30-45`'s own guarantee, on the lawn's match boundary |
| 3 | N ptrs of the same species share **one** `FrozenActionSet` instance — the assembler runs once | The per-key, per-match freeze; no per-ptr assembly |
| 4 | A Bound instance key resolves to its own set, not its species' set | Instance wins over species |
| 5 | A species with no pushed set yields an **empty** held list, never the basic-attack row | The module-17/18 boundary |
| 6 | `Remove(ptr)` drops exactly that ptr's entry and no other; a reused ptr address starts unbound | Hot rule 4, asserted directly rather than argued |
| 7 | `Clear()` drops every entry | Board edge |
| 8 | A compile failure reports once and returns empty on every later call | Loud once, never retried |
| 9 | An id the catalog does not know is refused loudly, not silently dropped | `BattleRunState.cs:556-559`'s posture, preserved |

**Never asserted:** how many species have sets, how many actions a species holds, or any authored
action name — those are derived-population readings and generated text (`validation-ssot.md`).

**Mutation to kill:** make `Snapshotted()` re-assemble — test 2 must go red.

**Goldens: byte-identical.** No battle, siege or delve code path is changed; `BattleRunState`'s own
held-action compile is read as the reference shape and not edited. The lawn has no golden contract
(`../research/combat-ai/S4-lawn.md:67-68`). Verify rather than assume:
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"`, and state the
result either way.

## Boundaries

- **Always:** assemble through `ActionSetAssembler`; freeze through `FrozenActionSet`; push from the
  server keyed by species / instance, never by ptr; bind on the existing frame drain slot; drop the
  entry in `InjectorEntityRegistry.Remove`.
- **Ask first:** letting a mid-match grant apply mid-match (it overturns `FrozenActionSet`'s stated
  guarantee and the lawn pool lifecycle in one step); adding a second key scope beyond species and
  instance.
- **Never:** put the basic-attack row in a held set; assemble per ptr or per decision; sort per
  decision; have the server address a ptr; await anything on the bind path
  (`overlay-control-loops.md:150`, Hot rule 3); read SQLite outside `FusionRpg.Data`
  (`gk-core/scripts/guard-dal.py`).

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Responsibility 8, *action system* — specifically the held set that
   feeds it. No addition to the closed register (`battle-engine-ssot.md:123,136`).
2. **Decide or resolve (§3c)?** Neither: it supplies the **candidate set** both sides of the seam read.
   The engine's half (`ActionRunner`, `CooldownLedger`) and the AI's half (`HeldActionsOf`) both take
   this list as input.
3. **Mechanism or loop?** **Mechanism.** One assembler, one freeze rule, shared by every mode
   (`battle-engine-ssot.md:64`: a mechanism has exactly one implementation).
4. **Which existing implementation does it extend?** `ActionSetAssembler.Assemble`
   (`ActionSetAssembler.cs:41-45`) and `FrozenActionSet` (`FrozenActionSet.cs:26-45`), plus
   `BattleRunState`'s compile-and-order shape (`BattleRunState.cs:582-638`). It copies neither into the
   injector; the injector only binds a ptr to a set Core produced.
5. **Does every mode get it?** Battle, delve and siege already have it via `BattleRunState._heldActions`
   (`:226`). This closes the lawn, the one place without it — and closing it is what makes the ideal's
   *"every creature's kit is dead weight today"* (`../combat-ai-ideal.md:22-24` of
   [lawn-combat-ai-ideal.md](../lawn-combat-ai-ideal.md)) stop being true.
6. **Deterministic and seeded?** The assembly is pure (`ActionSetAssembler.cs:28-30`: *"Pure — no
   persistence, no cap enforcement, no run-phase check"*), reads no clock and no RNG, and the push
   carries no timestamp. The binding step reads live Unity state, which is the lawn's
   non-deterministic driver half (`battle-engine-ssot.md:106-111`), and carries no replay contract.

## Success criteria

1. A lawn plant or zombie with a pushed set answers `IBattleView.HeldActionsOf` with a non-empty,
   preference-ordered `CompiledAction` list, verified in a Core test.
2. One assembly per key per match, regardless of how many ptrs of that key spawn.
3. A mid-match grant does not change a live set; the next match's set includes it.
4. `Remove(ptr)` unbinds that ptr and a reused address starts unbound.
5. An unknown species yields empty, and `StubIntentSource` answers `None` for it.
6. Zero SQL outside `FusionRpg.Data`; `guard-dal.py` green.
7. No golden moves; the suite is run and the result stated.

## Open questions

1. **Does the pushed set carry per-holder unlock state?** `UnlockState` has no production caller even in
   battle — only tests pass `unlockStateFor`
   (`../action-skill-tiers/spec-holder-rung-pricing.md:46-48`). Options: (a) push the compiled list
   only, and let module 17 price at the action's authored rung until an unlock-state producer exists;
   (b) push unlock state alongside. **Recommended default: (a)** — (b) would ship a second consumer of a
   producer that does not exist. This is module 17's pricing question; recorded here because the push
   shape is this module's.
   **ANSWERED 2026-09-22 (lane `cai4`):** **option (a) is what shipped.** `LawnHeldActionSets` takes no unlock-state input and
   pushes only the compiled, preference-ordered list (`CAI4.2`), and the rung pricing the option defers
   to is real: `Actions/Unlock/EffectiveRungResolver.cs` carries the resolution with the lawn's own
   `floorWhenUnknown: 1` (`CAI4.4`). Option (b) was not taken, so there is still exactly one consumer
   of the `UnlockState` producer that does not exist.
2. **Cross-module note (module 2, `profile-schema`):** the map lists module 16's dependency as
   `profile-schema`, but nothing in this spec reads a profile — the held set is content, not policy.
   The real ordering constraint is that module 17 consumes this module's sets, and module 19 consumes
   the tuning file module 2 creates. Suggest the plan re-reads that dependency row; it does not change
   what this module builds.
   **ANSWERED 2026-09-22 (lane `cai4`):** **landed upstream.** `docs/architecture/combat-ai-map.md:78` now reads
   `— *(corrected: it reads no profile)*`, and the plan/todo carry the same correction (`CAI4.2`'s row
   names no `profile-schema` dependency). Nothing left to re-read.
3. **Cross-module note (`creature-lawn-deploy`):** the unique deploy cap (D6, 5 per side) bounds how
   many *smart-tier* sets are live at once (`../combat-ai-ideal.md:326-337`). It is owned by
   `creature-lawn-deploy` and admitted at deploy, not here. This registry deliberately does not count or
   cap anything — a second admission rule is exactly what that ruling forbids.
   **Still open 2026-09-22** and unchanged by the landing: no task in any todo owns the D6 cap — it is
   filed as the lawn plan's `LW5.1`, and it is `CAI5.3`'s first precondition. `LawnHeldActionSets`
   counts and caps nothing, as this question required.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: actions/held sets, match/actor lifecycle, Cold push.
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json).
[x] I read every doc in the §1 row(s): action-related rows via combat-ai-ideal/map and the code,
    overlay-control-loops.md (§3 and §6 in full), battle-engine-ssot.md, match-lifecycle via
    InjectorEntityRegistry, AUDIT.md, S4-lawn.md.
[x] I checked decisions.md: the "Action selection (battle adoption)" row (:44) locks the compile-once
    shape this module copies; nothing here overturns it.
[x] Every factual claim cites file:line, and every cited file was opened this session.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the *(2026-09-22:
    the store and its tests have since landed, so the marker now applies only to the Injector rows)*
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE: FrozenActionSet's refusal, ActionSetAssembler's signature,
    RpgStore.GetSpeciesBasics, BattleRunState's compile loop, InjectorEntityRegistry.Remove/Clear,
    RpgHub's push shape and CheatCommandRunner's dispatch were each read.
[x] I read the surrounding section of every rule I quoted (control-loops §6 rules 1-7 in full).
[~] I tested (not assumed) any constraint I am reporting. **Gap named honestly:** no build or suite was
    run in this spec session; the golden claim is written as a command to run, not a result.
[x] Nothing contradicts a §2 invariant. The push is Cold (seconds OK), never on the hit path; the bind
    never awaits; the drop happens before ptr reuse.
[x] Corrections propagated: Open question 2 records a map dependency row worth re-reading, rather than
    silently diverging from it.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. Test 3 asserts "one instance shared", not how many ptrs or species exist.
[x] Event-refreshed cache (§2.16): the registry's invalidators are listed in full -- board.start
    (refresh), a Cold push (a new/changed key's set), spawn (KEY SET grows: a new ptr binds), death via
    InjectorEntityRegistry.Remove and board end via Clear (KEY SET shrinks). Each has a named test
    (2, 3, 6, 7). The trigger set is derived from this cache's own key behaviour, not copied.
[x] No acceptance criterion fixes an ordering that can vary: the preference order is produced once and
    asserted as "same inputs, same order", which is order-independent of spawn sequence.
[x] Produces/consumes no actor combat magnitude at all -- it carries action ids and compiled rows.
    Pricing is module 17's and goes through CostLedger; no composer, no fold.
[x] Does not invent or extend a SOLID-violating parallel path: it calls ActionSetAssembler and
    FrozenActionSet rather than adding a lawn-local assembler.
[~] A new rule has a registry row. **Gap named honestly:** the rule "a lawn ptr's AI state is dropped in
    InjectorEntityRegistry.Remove before reuse" is currently guarded only by this module's test 6.
    Whether it earns a registry row or rides an existing lifecycle guard is a plan decision, unresolved
    here.
```

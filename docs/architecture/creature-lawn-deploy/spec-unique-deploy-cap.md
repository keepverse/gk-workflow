# Spec: `unique-deploy-cap` (creature-lawn-deploy module 5)

**Program:** [creature-lawn-deploy](../creature-lawn-deploy-map.md) ·
**Ruling source:** [combat-ai-ideal.md](../combat-ai-ideal.md) §6.2a "Lawn deploy cap (D6)" and §10 D6 ·
**Depends on:** `lawn-deploy-core` (built), `lawn-deploy-events` (built), `zomboss-deploy-ai` (built) ·
**Unblocks:** `combat-ai` `lawn-cast-trigger` shipping default-on (that program's hard edge) ·
**Consumer, not owner:** [combat-ai](../combat-ai-map.md) lists this spec as a prerequisite only; it
never plans or builds it. ·
**Implementation home:** `creature-lawn-deploy`, scheduled once in the backlog-clean-up **lawn plan**
(`tasks/backlog-clean-up-todo.md` BCU2.4). ·
**Status:** spec, 2026-09-20. Not built.

## Objective

Owner ruling **D6**: *"Lawn deploy cap: at most 5 unique creatures per side, 10 on the board."* The
ideal states its class in the same breath — *"This is a **structural concurrency limit** that protects
the frame budget, not a progression ceiling. It limits how many **smart-tier** actors run at once. It
caps no magnitude and no roster size."* ([combat-ai-ideal.md](../combat-ai-ideal.md) §6.2a.) It also
states the reconciliation this spec owes: *"It must reconcile with the existing Zomboss own-unit cap
(`ZombossDeployPolicy`) and the demon-contract binding slots, so there is one admission rule, not
three."*

⚠️ **"the demon-contract binding slots" names nothing in code, and §5 reconciles what it must have
meant.** There is no "binding slot" type. The two nearest real things are `LoyaltyRank.Bound` — a
loyalty *tier*, not a count — and `ContractPolicy.Capacity(purchased) = BaseSlots + max(0, purchased)`
(`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:171`), a **roster-size** limit. This spec
reads the phrase as the latter, verifies in §5 that it is a roster axis rather than a concurrency one,
and therefore **declines to fold it into the concurrency admission rule** — three axes folded into one
number would make that number mean three things. (`demon` is also the retired name for `creature`;
`AGENTS.md` bars reintroducing it, which is a second reason the phrase should not be repeated as if it
named something.) **Owed upstream, not fixed here:** the phrase itself lives in
[combat-ai-ideal.md](../combat-ai-ideal.md) §6.2a and the map's cross-program table, both outside this
spec's paths — they should name `ContractPolicy.Capacity`/`BaseSlots` so a future reader does not go
looking for a type that does not exist.

**The gap, verified in code: there is no such limit anywhere today, on either side.** The one
server-side admission gate for a unique lawn deploy is
`RpgStore.TryBeginUniqueDeploy` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250`). It
refuses on `bad_args` (`:154`), `not_found` (`:161`), `expedition.locked` (`:170`),
`patron.cannot-deploy` (`:187`), `phase.<phase>` (`:190`), `contract.unbound` (`:198`),
`contract.insubordinate` (`:199`) and `deploy.hypno-ally-not-implemented` (`:217`). **Not one of those
counts how many specimens are already out.** `UniqueActorService.DeployAsync`
(`gk-core/src/FusionRpg.Server/UniqueActorService.cs:113-190`) forwards whatever the store returns and then
enqueues `pvz.spawn.extra` (`:165-182`); the injector's `MatchHost.TryBeginUniquePending`
(`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:39-56`) only registers a pending binding. Nothing between
the REST endpoint (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:43-61`) and the board bounds the
count, so N deploy calls put N smart-tier actors on the lawn.

The reason that matters is not fairness, it is the frame. The ideal's own reasoning: *"a vanilla board
at high spawn levels already drops fps. AI control moved out of the PvZ engine still costs the host."*
`KernelDriveHost` runs the lawn clock against a clamp of `0.05 ms`–`0.15 ms` per board
(`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:54-56`), and combat-ai's `lawn-cast-trigger` adds a
per-frame decision budget beside it. An unbounded number of deciding actors is a frame-budget hole, so
this cap lands **before** that module ships default-on.

This spec turns D6 into **one admission rule, at one gate, with a named refusal**, and states exactly
which of the three existing limits it subsumes and which it leaves alone.

## Tech stack

`FusionRpg.Core` (the pure policy type), `FusionRpg.Data` (the count query and the gate call inside the
existing transaction), `FusionRpg.Contracts` (the refusal reason constants, beside the existing ones),
`gk-core/data/tuning/lawn-deploy.v1.json` (new; does not exist yet). `gk-core/tools/tuning/publish.py` publishes later
versions and needs one new flag (see **Tunables**). No new dependency, no new table, no schema change.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~UniqueActor|DeployCap"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnUniqueDeployCap|ZombossDeploy"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ZombossDeployPolicy"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/tools/tuning/publish.py lawn-deploy limits.maxConcurrentUniquesPerEmpire=<n>
python gk-core/tools/tuning/publish.py zomboss-deploy-ai --drop-key scorer:maxConcurrentOwnUnits   # new flag, see Tunables
```

## Project structure

| What | Where |
|---|---|
| The pure cap policy (count in, `GateResult` out) | `gk-core/src/FusionRpg.Core/Match/LawnUniqueDeployCap.cs` (new; does not exist yet) |
| The tuning record + host-injected hub, shaped like `LawnDeployEventsTuning` | `gk-core/src/FusionRpg.Core/Match/LawnDeployLimitsTuning.cs` (new; does not exist yet) |
| Two refusal reason constants, beside `GateReasons` | `gk-core/src/FusionRpg.Core/Match/CapPolicy.cs` (changed — `GateReasons`, `:68-90`) |
| The live-count query, inside the existing `_gate` lock | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` (changed) |
| The gate call inside `TryBeginUniqueDeploy` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250` (changed) |
| Zomboss's pre-check reads the shared cap | `gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployPolicy.cs:68-70` (changed) |
| Its tuning record drops the forked field | `gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployRoster.cs:15-16` (changed) |
| Host load + inject (server) | server composition root, beside the existing tuning loads |
| Host load + inject (injector) | `RpgHost` startup, beside `LawnDeployEventsTuningHub` / `ZombossDeployTuningHub` |
| The tuning file | `gk-core/data/tuning/lawn-deploy.v1.json` (new; does not exist yet) |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Match/LawnUniqueDeployCapTests.cs` (new; does not exist yet), `tests/FusionRpg.Data.Tests/UniqueActors/UniqueDeployCapTests.cs` (new; does not exist yet) |

## The shape

### 1. One rule, expressed once

```csharp
/// <summary>
/// D6 (combat-ai-ideal.md §6.2a): how many unique specimens may be BOUND TO ONE LAWN BOARD AT ONCE.
///
/// <para><b>STRUCTURAL LIMIT — per-frame/runtime class, not a progression ceiling</b>
/// (decisions.md "Caps (project-wide)": structural limits and per-frame/runtime caps are exempt "and
/// each carries a comment naming its class"; ssot-power-scale.md §11.3 "Runtime and board caps — perf
/// protection, not progression"). It bounds what exists at ONE MOMENT on ONE BOARD. It caps no
/// magnitude, no roster size, no lifetime total and no rate of progress: a player may own, contract
/// and level any number of specimens, and deploy a different five next run. The thing it protects is
/// the Unity frame: every admitted unique is a smart-tier AI actor deciding inside
/// KernelDriveHost's 0.05-0.15 ms board budget (KernelDriveHost.cs:54-56).</para>
///
/// <para>Pure: no I/O, no clock, no ambient state. The caller supplies the counts.</para>
/// </summary>
public static class LawnUniqueDeployCap
{
    public static GateResult TryAdmit(int liveForThisEmpire, int liveOnBoard, LawnDeployLimits limits);
}
```

`GateResult` and the reason-code convention are `CapPolicy`'s, reused rather than re-declared
(`gk-core/src/FusionRpg.Core/Match/CapPolicy.cs:54-66` for `GateResult`, `:68-90` for `GateReasons`). Two
constants join `GateReasons`:

| Constant | Value | When |
|---|---|---|
| `GateReasons.CapUniquePerEmpire` | `"cap.unique_per_empire"` | this empire already holds `maxConcurrentUniquesPerEmpire` |
| `GateReasons.CapUniqueBoard` | `"cap.unique_board"` | the board already holds `maxConcurrentUniquesOnBoard` |

**The per-empire check runs first**, so a refusal names the side that is full rather than the board,
which is the more useful message and the one a UI can act on.

### 2. What is counted, and by which key

The count is **live bindings for one `matchKey`**, keyed by **owning `player_id`**, over the phases
`Deploying` **and** `ActiveBound` (`FusionRpg.Contracts.UniqueActorPhases`). Both columns already exist
and are already written by this path: `TryBeginUniqueDeploy` sets `phase = Deploying` and
`match_key = $mk` (`RpgStore.UniqueActors.cs:232-247`), and `TryAckUniqueSpawn` moves the row to
`ActiveBound` keeping `match_key` (`:293-309`).

- **`Deploying` counts.** It is a reservation. A row that has been queued to the injector but not yet
  acked is a specimen that is about to exist; not counting it lets a burst of calls overshoot the cap
  by the whole in-flight window. The reservation is released by the mechanism that already exists for
  a stuck deploy — `UniqueActorService.FailExpiredDeploys` → `RpgStore.FailExpiredUniqueDeploys`
  (`gk-core/src/FusionRpg.Server/UniqueActorService.cs:100-107`), which returns `Deploying` rows to `Roster`.
  No new lifecycle, no new sweep.
- **The key is the owning empire, not the `side` column.** `player_id` is the axis
  `SpecimenOwnershipOracle` already uses to tell "which player deployed it" apart from "which
  mechanical side it is on", and it is the axis Zomboss's own mints already carry:
  `RpgStore.EnsureZombossPlayer` / `MintForZomboss` own every Zomboss specimen under a dedicated
  player row (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25-29`, `:42-58`), with the file's
  own reason: *"they simply carry different `player_id` values, exactly like any other two real
  players already would."* The `side` column would give the same answer today **only because**
  `deploy.hypno-ally-not-implemented` (`RpgStore.UniqueActors.cs:217`) refuses the one case where a
  specimen's mechanical side and its owner diverge. Keying on `side` would silently mis-count the day
  that refusal is lifted; keying on `player_id` never does.
- **Vanilla PvZ units are not counted**, and neither are general creatures. They hold no specimen row
  and run the performance tier (combat-ai-ideal §6.2a: *"General creatures are not counted; they run
  the performance tier."*).

### 3. Where the gate sits inside `TryBeginUniqueDeploy`

Inside the existing `lock (_gate)` and the existing connection, in this order:

1. `bad_args` (`:153-154`), `not_found` (`:161`).
2. **The idempotent re-entry branch** (`:163-166`): a repeat call with the same `correlationId` on a
   row already `Deploying` returns `(true, "", row, queued: false)`. **This must stay ahead of the cap
   check.** A retry of an in-flight deploy would otherwise be refused by its own reservation — the row
   it is retrying is one of the rows being counted. This ordering is load-bearing and is tested.
3. `expedition.locked` (`:170`), `patron.cannot-deploy` (`:187`), `phase.*` (`:190`), the contract
   gate (`:195-219`).
4. **The cap gate** — count, then `LawnUniqueDeployCap.TryAdmit`, then `return (false, reason, row,
   false)` on a refusal.
5. Only then `ReconcileCreatureTraitBindingsUnlocked` / `ReconcileCreatureMagnitudeBindingsUnlocked`
   (`:225-231`) and the `UPDATE` (`:232-248`).

Placing it at step 4 means **a refused deploy does no work and changes no state**: no trait
reconciliation, no phase move, no `match_key` write, no `revision` bump, nothing for the injector to
undo. That is the difference between a refusal and a rollback.

**A missing `matchKey` refuses, it does not pass.** `matchKey` is optional on the signature
(`TryBeginUniqueDeploy(string instanceId, string correlationId, string? matchKey = null)`, `:151-152`)
and is stored as `NULL` when absent (`:244`). A board-scoped cap cannot be evaluated without knowing
which board, and silently admitting is the failure mode this spec exists to remove. A deploy with no
`matchKey` returns `cap.unique_board` with the message naming the missing key — loud over silent, the
same discipline `SpeciesAllocationSource`'s `reportUnconfigured` already applies to an unresolvable
input.

### 4. Zomboss's own pre-check reads the same number

`ZombossDeployPolicy.Decide` declines when `ownCount >= tuning.MaxConcurrentOwnUnits`
(`gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployPolicy.cs:68-70`), counting `RelationKind.Ally` units off
`ILawnBoardView` (`:60-66`), with the injector excluding the unregistered vanilla horde from that
count (`gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs:318-327`). That is a second number on the **same
axis** as the new cap, which is exactly the fork D6 forbids.

**Resolution: the policy keeps its pre-check and loses its own number.** `ZombossScorerTuning`
(`gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployRoster.cs:15-16`) drops `MaxConcurrentOwnUnits`, and
`Decide` takes the per-empire cap from `LawnDeployLimits` instead. The pre-check is a **decision
courtesy** — it stops the AI spending a seeded roll on a deploy the gate will refuse — and it is never
the authority; the store gate is. Two evaluations of one rule at two moments is correct; two rules is
not.

**This changes nothing observable today, and that is checkable rather than asserted.**
`CheckZombossDeployTrigger` returns early on
`ZombossDeployRunStateHolder.AlreadyFired` (`MatchHost.cs:297`), so Zomboss deploys **at most once per
run** regardless of any concurrency number. Raising his effective ceiling from `2` to the shared cap
is inert until that once-per-run rule changes, which is `zomboss-deploy-ai`'s own decision, not this
spec's.

### 5. The reconciliation, stated as a table

| Existing limit | Where | Axis | This spec |
|---|---|---|---|
| `ZombossScorerTuning.MaxConcurrentOwnUnits` = 2 | `ZombossDeployRoster.cs:15-16`, read `ZombossDeployPolicy.cs:68-70`, value `gk-core/data/tuning/zomboss-deploy-ai.v1.json` `scorer.maxConcurrentOwnUnits` | **Same axis** — concurrent own deployed uniques | **Subsumed.** The field is dropped; the policy reads the one cap. |
| `ContractPolicy.Capacity(purchased) = BaseSlots + max(0, purchased)` | `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:171`, `gk-core/data/tuning/contracts.v1.json` `slots.baseSlots` = 12 | **Roster** — how many specimens the empire holds under contract, over its whole life | **Left alone, deliberately.** `ContractPolicy.MaxSlots` (48) was **removed** as a progression ceiling (owner, 2026-08-23; `ssot-power-scale.md` §11.1/§11.1a: *"the price was already the cap"*, and `decisions.md` "Caps (project-wide)"). Nothing here re-introduces a roster ceiling, and the board cap must never be described as one: five on a board at once and an unbounded roster are compatible statements. |
| `CapPolicy.TryAdmit` / `MatchRuntime.TryAdmitSpawn`, `MaxLivingPlants` 50 / `MaxLivingZombies` 80 | `gk-core/src/FusionRpg.Core/Match/CapPolicy.cs:98-116`, `gk-core/src/FusionRpg.Core/Match/MatchRuntime.cs:224-241`, `gk-core/data/tuning/match.v1.json` | **Entity RAM gate** over all of *our* Intent/FA4/debug spawns, unique or not (`gk-core/src/FusionRpg.Core/Match/CapPolicy.cs:4`: *"not vanilla waves"*) | **Left alone, and still applies.** It is a superset that never distinguishes a unique from a debug-created plant. Both gates run; this one is stricter and more specific, and it runs first (server admission, before the spawn command exists), so its reason reaches the caller instead of a later `cap.plants`. |
| `LawnDeployEventsTuning` `maxFiresPerRun` = 1 | `gk-core/data/tuning/lawn-deploy-events.v1.json`, `LawnDeployEventEvaluator` | **Frequency** — how often the *opportunity* appears in a run | **Left alone.** A frequency limit and a concurrency limit are different questions; collapsing them would make "you may be offered a deploy" depend on how many are currently alive, which is not what the trigger means. |
| `ZombossDeployRunStateHolder.AlreadyFired` | `MatchHost.cs:297` | **Frequency**, zombie side | **Left alone**, same reason. |

**One admission rule** = one place that can refuse an admission on the concurrency axis
(`LawnUniqueDeployCap`, called from `TryBeginUniqueDeploy`). Frequency and roster are different axes
with their own owners, and saying so is part of the reconciliation, not a dodge of it.

## Tunables

New domain `gk-core/data/tuning/lawn-deploy.v1.json`, owner
`docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md`. A first version is authored by
hand exactly as `lawn-deploy-events.v1.json`'s own `_meta.rebalance` records for its own v1
(*"First version -- authored by hand, matching every other tuning file's own v1"*); **every later
change publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`**, never a hand edit
(`tunables-ssot.md`).

| Key | Unit | v1 value | Why |
|---|---|---|---|
| `limits.maxConcurrentUniquesPerEmpire` | count | 5 | D6, owner-set. **Structural** — `_meta` names the class and the frame-budget reason. |
| `limits.maxConcurrentUniquesOnBoard` | count | 10 | D6, owner-set. **Structural.** Not redundant with the row above: the per-empire number is the structural/fairness statement, the board number is the one that actually bounds the frame, and they only coincide while exactly two empires can deploy. A third deploying empire would separate them without a schema change. |

The `_meta.note` states, in the file: that both are structural per-frame limits and not progression
ceilings; that the register row is `ssot-power-scale.md` §11.3; and that raising them is a measured
perf decision (the 300-zombie A/B `lawn-scale-live-proof` owns), never a balance pass.

**Moving Zomboss's forked number needs one new `publish.py` flag.** The tool deliberately refuses to
invent a key and has no delete path, because both are *schema* changes rather than balance changes
(`gk-core/tools/tuning/publish.py` header, and its `--add-edge`/`--add-key` rationale). Dropping
`scorer.maxConcurrentOwnUnits` is a schema change, and the standing rule is *"extend the tool when a
domain lacks support"* (tunables-ssot T4). So: add `--drop-key <container.path:leaf>`, symmetric with
the existing `--add-key`, publish `zomboss-deploy-ai.v2.json` with it, and **land the reader change in
the same commit** (H7 — a tuning publish lands with its reader). Leaving the key behind as dead config
is not an option: *"Dead keys … **Wired** or **deleted**. Never migrated as dead config."*
([combat-ai-ideal.md](../combat-ai-ideal.md) §8.)

## Code style

- The structural-limit comment sits **on the type**, in the words `decisions.md`'s Caps row asks for —
  naming the class (per-frame/runtime), what it does not bound (magnitude, roster, lifetime), and the
  register row. A cap without that comment is indistinguishable from a progression ceiling to the next
  sweep, and `ssot-power-scale.md` §11.2a is the record of a sweep that missed one.
- Counts are `int` and compared, never multiplied — no widening question arises. The store query
  returns `int` from `COUNT(*)` over a board's rows, a quantity bounded by `MaxLivingPlants` +
  `MaxLivingZombies` long before it approaches any type's range.
- Refusal strings are constants in `GateReasons`, never literals at the call site, matching the eight
  reasons `TryBeginUniqueDeploy` already returns.
- The DAL boundary holds: the SQL count lives in `FusionRpg.Data`, the rule lives in
  `FusionRpg.Core`, and `guard-dal.py` proves it.

## Testing strategy

Contract assertions only (`validation-ssot.md`). Store tests run **in memory** — the disk is not the
thing under test (`testing-standard.md`, `guard-test-substrate.py`).

`gk-core/tests/FusionRpg.Core.Tests/Match/LawnUniqueDeployCapTests.cs`:
- ✅ At the per-empire limit, `TryAdmit` refuses with `GateReasons.CapUniquePerEmpire`; below it, admits.
- ✅ Under the per-empire limit but at the board limit, refuses with `GateReasons.CapUniqueBoard`.
- ✅ The per-empire reason wins when both are at their limit (the stated precedence).
- ✅ The policy is pure: the same inputs give the same answer, and it touches no ambient state.
- ❌ Never asserts the literal 5 or 10. The limits are supplied by the test; the **relationship**
  `board >= perEmpire` is asserted against the shipped file as a schema invariant, with the reason
  stated — a nonsensical row (a board cap below a side cap) is a config defect, not a balance choice.

`tests/FusionRpg.Data.Tests/UniqueActors/UniqueDeployCapTests.cs`:
- ✅ A deploy over the cap returns the reason **and leaves the row in `Roster`** — phase, `match_key`,
  `deploy_correlation_id` and `revision` all unchanged. This is the "refusal, not rollback" property.
- ✅ A `Deploying` row counts toward the cap (the reservation property).
- ✅ After `FailExpiredUniqueDeploys` returns a stuck `Deploying` row to `Roster`, the slot is free again.
- ✅ **A repeat call with the same `correlationId` on an already-`Deploying` row still succeeds at the
  cap** — the step-2 ordering above. Written as its own named test, because getting it wrong produces
  a bug that only appears under retry.
- ✅ Dave's and Zomboss's rows are counted separately: five under each admits ten; six under one refuses.
  The Zomboss row is created through `EnsureZombossPlayer`, not fabricated.
- ✅ Two different `matchKey`s do not count against each other.
- ✅ A deploy with no `matchKey` refuses with the board reason.

`tests/FusionRpg.Core.Tests/.../ZombossDeployPolicy*`:
- ✅ The existing decline path still fires, now sourced from the shared limit (the existing tests keep
  passing with the field supplied from the new tuning record).
- ✅ `ZombossScorerTuning` no longer exposes `MaxConcurrentOwnUnits` — a compile-level assertion that
  the fork is gone.

**Golden impact: byte-identical.** No battle, delve or siege golden reaches unique lawn deploy;
`BattleGoldenTests` never constructs a `rpg_unique_actors` row. The lawn has no golden to move
(`docs/research/combat-ai/S4-lawn.md:65-68`: *"No lawn combat goldens exist to protect"*). If a golden
moves, this module is wrong.

## Boundaries

- **Always:** count `Deploying` + `ActiveBound`; key on `player_id`; refuse with a named constant;
  leave state untouched on a refusal; keep the structural-limit comment on the type; publish `v{n+1}`.
- **Ask first:** changing the shipped 5/10 (owner-set in D6 — a tuning change, but this pair is the
  ruling itself); giving Zomboss a concurrency allowance different from the player's (D6 says *"per
  side"*, which means symmetric, and D2 forbids AI-side difficulty levers).
- **Never:** re-introduce a roster ceiling (`ContractPolicy.MaxSlots` is a deleted progression ceiling,
  `ssot-power-scale.md` §11.1a); clamp silently — this refuses with a reason, it never drops a deploy;
  put the count in the injector as the authority (the store owns the phase FSM; the injector's view is
  a projection); add a second concurrency number anywhere; migrate
  `scorer.maxConcurrentOwnUnits` forward as dead config.

## battle-engine-ssot §5 — the six answers

| | Question | Answer |
|---|---|---|
| 1 | Which responsibility (§3), or is it new? | **None of them, and not new.** This is match **admission** — who may be on the board — not a battle mechanism. Its nearest existing kin is `CapPolicy`, which the engine also does not own (`decisions.md` MatchRuntime row: *"Caps gate **our** Intent/FA4/debug extras"*). The §3 register is untouched. |
| 2 | Does it DECIDE or RESOLVE? | **Neither.** It runs before any actor exists to decide for or resolve about. It gates whether a specimen may enter the board at all. |
| 3 | Mechanism or loop? | **Loop.** It is a per-place population rule for the lawn. Every mode already has one (a battle has its setup size, a delve its party size); this is the lawn's, and it never claims to be theirs. |
| 4 | Which existing implementation does it extend? | `CapPolicy`'s `GateResult`/`GateReasons` vocabulary (`gk-core/src/FusionRpg.Core/Match/CapPolicy.cs:54-90`) and `TryBeginUniqueDeploy`'s refusal-string contract (`RpgStore.UniqueActors.cs:150-250`). Nothing is copied and no formula is estimated. |
| 5 | Does every mode get it? | **No — and the reason is the frame, stated so it can be refused.** The lawn is the only place where an unbounded number of independently-deciding RPG actors can accumulate in real time inside one Unity frame budget (`KernelDriveHost.cs:54-56`). Battle, delve and siege fix their participant count in the setup before the run, so they already have this bound by construction. |
| 6 | Is it deterministic and seeded? | **Yes, trivially.** It reads no clock, no RNG and no ambient state — it compares two counts against two tunables. The counts are ordered by the store's existing `_gate` lock, not by time. |

**And the rule that is not a question:** nothing here re-implements or estimates a battle number. It
admits or refuses, and everything downstream is unchanged.

## Success criteria

1. `gk-core/data/tuning/lawn-deploy.v1.json` exists, carries both limits with the structural `_meta`, and is
   loaded by both hosts.
2. A deploy that would exceed either limit returns a named refusal, and the row is still in `Roster`
   afterwards — verified by reading the row back, not from the response body
   (`live-probe-standard.md`: a response body is never proof).
3. A retry with the same `correlationId` on an in-flight deploy succeeds at the cap.
4. `ZombossScorerTuning.MaxConcurrentOwnUnits` no longer exists; `ZombossDeployPolicy` declines from
   the shared limit; `zomboss-deploy-ai.v2.json` is published through `publish.py` in the same commit
   as its reader.
5. `ContractPolicy.Capacity` and `CapPolicy.TryAdmit` are unchanged, and a test says why each is a
   different axis.
6. Every golden and every existing test is byte-identical.
7. `guard-dal.py` and `guard-test-substrate.py` green.
8. The enforcement registry gains a row for the structural-comment rule, or an `unguardableReason`
   (`gk-core/scripts/enforcement-registry.v1.json`).

## Open questions

1. **Does `HypnoAlly` change the counted side when it is implemented?** Today it cannot arise:
   `deploy.hypno-ally-not-implemented` (`RpgStore.UniqueActors.cs:217`) refuses the one case where a
   specimen's mechanical side and its owner diverge. **Options:** (a) count by owner `player_id`
   always, so a hypnotised specimen stays on its owner's tally; (b) count by the side it fights on.
   **Recommended default: (a)**, which is what this spec builds — it needs no change when hypno lands,
   and it matches `SpecimenOwnershipOracle`'s own axis. Recorded here so the choice is visible to
   whoever implements hypno rather than being rediscovered.
2. **Cross-module note, not this spec's to decide:** `zomboss-deploy-ai` currently allows Zomboss
   exactly one deploy per run (`MatchHost.cs:297`). Whether that stays once a concurrency cap exists
   is that module's question. This spec deliberately does not change it, and states that the cap is
   inert on the zombie side until it does.

## Design gate checklist (DESIGN-GATE §5)

```
[x] I identified the subsystem(s) this touches: creature-lawn-deploy (admission), match runtime caps,
    contracts (named as out of scope), tunables.
[x] Session boundary: backlog-clean-up-20260920, recorded at tasks/sessions/. This spec writes one
    new file under docs/architecture/creature-lawn-deploy/ and edits nothing else.
[~] I read the §1 rows for those subsystems this session: Caps/power (ssot-power-scale.md §11.1,
    §11.1a, §11.3), tunables-ssot (via CLAUDE.md + publish.py itself), validation-ssot (via the
    restated rule), battle-engine-ssot §5, creature-system vocabulary (via creature-lawn-deploy-map).
    GAP: I read tunables-ssot.md's rules as restated in CLAUDE.md and enforced by publish.py's own
    header, not the document itself.
[x] decisions.md checked: "Caps (project-wide)" (:60) exempts structural/per-frame limits and requires
    the class-naming comment; "MatchRuntime" (:65) locks caps as gating our own spawns. Neither
    conflicts; both are cited.
[x] Every factual claim cites file:line, and every file cited was opened in this session.
[x] audit-doc-citations.py --scope <this file> --strict: 0 HIGH findings, exit 0. Remaining:
    4 x D1 (LOW) are the files this spec proposes, and 2 x D3 (LOW) are bare basenames the audit
    refuses to guess at (CapPolicy.cs / ContractPolicy.cs each have a namesake elsewhere in src/);
    every one of those is fully pathed at its first mention.
[x] Verified against CODE, not comments: the absence of any concurrency limit was established by
    reading every refusal in TryBeginUniqueDeploy, not by grep for "cap".
[x] I read the surrounding section of every rule quoted (ssot-power-scale §11.1a in full before
    claiming MaxSlots was redundant; decisions.md's Caps row in full before claiming the exemption).
[~] I tested (not assumed) the constraints I report. NOT RUN: no test or build was executed — the
    brief forbids it for this session. The two golden claims are argued from code (no golden
    constructs rpg_unique_actors; S4-lawn.md records no lawn goldens exist), not from a run, and are
    marked as arguments rather than measurements.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated: none needed — no existing doc claims a deploy cap exists.
[x] No assertion pins a derived population count or generated text. The 5/10 pair is a tuning value
    supplied to tests, never asserted; only the schema invariant board >= perEmpire is pinned, with
    its reason stated.
[x] Event-refreshed cache (§2.16): none introduced. The count is read inside the store's existing
    lock on every call — deliberately not cached, because a cache here would need exactly the
    key-set-moving trigger the 2026-09-13 incident is about.
[x] No acceptance criterion fixes an ordering that can vary: the one ordering that matters (idempotent
    re-entry before the cap check) is stated as a requirement AND tested, not assumed.
[x] Actor combat/derived magnitude: this feature produces and consumes none. It is a count gate.
[x] Does not invent or extend a SOLID-violating parallel path: it REMOVES one (the forked Zomboss
    concurrency number) rather than adding to it.
[x] New rule has a registry row: success criterion 8 requires the structural-comment rule to land in
    gk-core/scripts/enforcement-registry.v1.json or carry an unguardableReason.
```

# Spec: `lawn-cast-activation` (combat-ai module 18)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `lawn-held-actions` (module 16), `lawn-cost-authority` (module 17) ·
**Unblocks:** `lawn-cast-trigger` (module 19) · **Status:** **part built (pure half, CAI4.6, 2026-09-22).** `gk-core/src/FusionRpg.Core/Match/Ai/LawnCastPlan.cs` is in — pay → cooldown → the `OnActivate` event, with an `InsufficientFunds` refusal that starts no cooldown and builds no event — with 7 tests at `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs`. **Owed:** the record-kind discriminator (`EffectEventDto.CastOrigin`, `gk-core/src/FusionRpg.Contracts/**`), the fire site and its guards (`gk-fusion/src/FusionRpg.Injector/**`). See `tasks/reports/CAI4.6.md`.

## Objective

**A chosen action has nowhere to go on the lawn.** Battle already has the activation edge and it is one
event: after the intent resolves, it raises the runner, then the bag, then flushes —

```csharp
// gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:215-232, as shipped
state.Host.Runner?.OnEvent(new RunnerEvent(
    TriggerIndex.Ordinal(AtomTriggers.OnActivate), attacker.Setup.Key, target.Setup.Key, …));
state.Host.Bag.OnEvent(new Contracts.EffectEventDto
{
    Trigger = AtomTriggers.OnActivate,
    ActorPtr = attacker.Setup.Key, TargetPtr = target.Setup.Key,
    Tick = nowTick, HitCount = 1,
});
state.Host.Flush();
```

The lawn has the same tail already running: `EffectRuntime.OnDrained` → `AtomPushReceiver.OnEvent` →
`Bag.OnEvent` (`gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:359,375-377`) → plan →
`InjectorEffectActionSink.Execute` → Funnel → `EntityStatWriter`
(`../combat-ai-ideal.md:120`; `../research/combat-ai/S4-lawn.md:79-80`: *"the single execution tail
every mode's chosen action already rides; an AI-chosen intent needs no new write path"*). What is
missing is a **caller** that raises `OnActivate` for an action the AI chose, having paid for it.

This module is that caller, plus the one guarantee the ideal names as a real gap
(`../combat-ai-ideal.md:148`): **cast records carry a record-kind discriminator, so a cast never
increments the swing counter (a feedback loop) and is never charged as a basic-attack swing (a double
charge).**

⚠️ **State the current risk precisely, because it changes what this module is for.** The loop is
**latent today, not live**: `overlay-control-loops.md:154` (Hot rule 7) already bans FA10 from calling
Unity `TakeDamage` and fixes *"Re-entry depth = 0: overlay apply must not emit `combat.hit` that
nested-flushes Funnel"*, so a cast's HP delta produces **no drained record at all**. The discriminator
is therefore not a bug fix — it is the structural guarantee that the loop stays impossible when
`GameEventKind.ChainSynthetic`, documented as *"drain-generated (overlay procs, counter bursts)"*
(`gk-core/src/FusionRpg.Core/Events/GameEventRec.cs:12`) and today **producerless**, finally gets a producer.
§"The shape" gives the exact lines that would close the loop if it did.

## Tech stack

`FusionRpg.Core` (the pure cast plan: pay → cooldown → event construction, in order),
`FusionRpg.Contracts` (one additive field on `EffectEventDto`), `FusionRpg.Injector` (the thin fire
site). No new dependency. No new write path, no new trigger — `OnActivate` is already in the closed
trigger vocabulary (`gk-core/src/FusionRpg.Contracts/EffectDtos.cs:45`, aliased by `AtomTriggers`).

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnCast|FullyQualifiedName~EffectEventDto|FullyQualifiedName~FoundationContract"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-fusion/scripts/guard-funnel-delta.py ; python gk-fusion/scripts/guard-single-writer.py ; python gk-core/scripts/guard-secondary-no-unity.py
```

No tuning publish: no tunables (see below).

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnCastPlan.cs` | **landed (CAI4.6)** | The pure, ordered plan: pay, start cooldown, build the `OnActivate` event — no Unity, no bag |
| `src/FusionRpg.Injector/Effects/LawnCastActivation.cs` | **new; does not exist yet** | The fire site: liveness re-check, depth guard, runner → bag → flush |
| `gk-core/src/FusionRpg.Contracts/EffectDtos.cs` | changed | One additive `CastOrigin` flag on `EffectEventDto` (`:172-237`) |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs` | changed | One early return for a cast-origin record in `ShouldApplyRider` (`:135-168`) |
| `tests/FusionRpg.Core.Balance.Tests/CombatAi/LawnCastPlanTests.cs` | **landed (CAI4.6)** | Order, refusal, discriminator, re-entry |

## The shape

### 1. The ordered plan, and why the order is not negotiable

`LawnCastPlan.Build(actorKey, intent, nowTick, ledger, cooldowns, rng)` performs, in this order:

1. **Pay on commit.** `CostLedger.TryPay(actorKey, actionId, ActionCostTiming.OnCommit, rng)`.
   A `CostPayOutcome.InsufficientFunds` (`gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs:7-19`) is a
   **refusal**: no cooldown starts, no event is built, nothing is flushed. *"Committing is what costs,
   not landing"* (`CostLedger.cs:28-30`) — a cast that misses still paid, a cast that was never
   afforded never happened.
2. **Start the cooldown** on the shared `CooldownLedger`, the mode-agnostic ledger the ideal already
   lists as built (`../combat-ai-ideal.md:107`).
3. **Build the event**, then hand it to the fire site.

The fire site then does **runner → bag → flush**, and that order is copied for the reason
`BasicAttack.cs:226-214` states verbatim: *"the runner runs BEFORE the bag, not after — `EffectBag.OnEvent`
calls `Funnel.Flush()` inside itself, so a dispatch enqueued afterwards would sit in the mailbox until
the next event."* Swapping them is a real, documented trap; test 1 plants it.

### 2. The record-kind discriminator

**The mechanism it protects, with the lines.** If a lawn cast ever produced a drained damage record:

| Step | Line | What happens |
|---|---|---|
| The record's kind has swing identity | `gk-core/src/FusionRpg.Core/Events/EventDrain.cs:118` | `HasSwingIdentity` is `CombatHit or ChainSynthetic` |
| So it is counted and deduped as a swing | `EventDrain.cs:120-129` (`SwingBump`), `:135-146` (`ConsumeSwingTriggerAndRelease`) | one record of the group is stamped first-of-swing |
| It maps to `OnDamageDealt` with `IsFirstOfSwing` | `EventDrain.cs:605-631` | `ChainSynthetic` shares the `CombatHit` DTO case |
| The drain gates every record on the rider charge | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:367` | `ShouldApplyRider(ev)` |
| Which charges a basic-attack swing | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs:137,152` | `OnDamageDealt` + `IsFirstOfSwing` → `TryChargeForSwing` |
| And module 19's counter reads the same flag | module 19 | cast → record → counter → cast |

Two failures in one path: a **double charge** (the cast already paid at commit) and a **positive
feedback loop** (a cast manufactures its own next trigger).

**The discriminator is one additive field on the DTO:**

```csharp
/// <summary>combat-ai `lawn-cast-activation`: true when this record originates from an AI or
/// commander CAST rather than a vanilla swing. Two consumers, both refusals: the lawn basic-attack
/// charge must not charge it (the cast already paid at commit), and the lawn decision trigger's
/// per-actor swing counter must not count it (a cast that manufactures its own next trigger is a
/// feedback loop). Additive, defaults false -- every existing construction site is unchanged, the
/// same argument SwingId, Wave and TargetRow already make (EffectDtos.cs:194-215), so
/// FoundationContractVersion.Current does not move.</summary>
[JsonPropertyName("castOrigin")] public bool CastOrigin { get; set; }
```

**`EventDrain` is not modified.** Changing `HasSwingIdentity` (`:118`) would change the **dedupe**,
which is a different mechanism with a different job — one physical swing producing N victim records
(`EffectDtos.cs:219-226`). The discriminator rides the DTO, where its two consumers already read.

`ShouldApplyRider` gains one early return, before the charge:

```csharp
// A cast paid at commit (LawnCastPlan step 1). Charging it again as a basic-attack swing would
// be a double charge; returning true means "let the record's effects flow, do not charge".
if (ev.CastOrigin) return true;
```

**The obligation this module records but does not build:** when a `ChainSynthetic` producer lands, it
must carry the flag onto `GameEventRec` as a trailing optional field — the established additive shape
there (`GameEventRec.cs:47-58` for `SwingPtr`, `:63-70` for `InstakillShaped`) — and `ToDto`
(`EventDrain.cs:598-631`) must thread it onto the DTO. Specifying that field now, with no producer,
would be speculative; stating the obligation is not.

### 3. Re-entry depth 0, enforced rather than argued

`overlay-control-loops.md:154` (Hot rule 7) is the invariant. This module makes it a refusal:

```csharp
// Hot rule 7 (overlay-control-loops.md:154): a cast raised from inside a Funnel flush would
// nest-flush. Refuse and report -- never recurse, never throw into the drain.
[ThreadStatic] static int _depth;
```

`Fire` entered at `_depth > 0` refuses, releases the module-19 cast token, and reports through
`CheatState.Error` — the same fail-closed posture `EffectRuntime.OnDrained` already takes around the
bag (`EffectRuntime.cs:381-384`). `Flush()` is called **once**, at the end, matching
`BasicAttack.cs:232`.

### 4. Fail-closed liveness

Both ptrs are re-checked against `InjectorEntityRegistry` at fire time, because a decision taken earlier
in the frame may reference an actor that has since died:

- missing or dead actor ptr → skip, release the token, **do not throw** (`overlay-control-loops.md:148`,
  Hot rule 1);
- target already gone → skip, release the token (`:149`, Hot rule 2);
- nothing awaits SignalR, HTTP or SQLite anywhere on this path (`:150`, Hot rule 3).

A skip after `TryPay` has already succeeded **does not refund**: committing is what costs
(`CostLedger.cs:28-30`), and a refund path would be a second spend authority.

### 5. What this module does not do

- It does not choose an action or a target — that arrives as an `ActionIntent` from the policy.
- It does not decide *when* — module 19 owns the trigger, the budget and the token pool.
- It does not own a kill switch: one switch governs the whole lawn AI and it is module 19's. A cast
  cannot occur without a decision, so a second switch would be a second answer to one question.
- It does not write to Unity directly. Every HP delta goes Funnel → FA10 `Add`
  (`overlay-control-loops.md:153`, Hot rule 6: signed deltas, never absolutes; `guard-funnel-delta.py`),
  and every combat stat write goes through `EntityStatWriter` (`guard-single-writer.py`).

## Tunables

**None.** Cost amounts, rung multipliers and cooldown multipliers are already tunables read by
`CostLedger` and the catalog (module 17). This module introduces no number a balance pass would touch.
One structural constant: the re-entry depth ceiling, `0`, which is the invariant itself and carries the
control-loops citation in its comment.

## Numeric types

None introduced. `Tick` is `long` (`EffectDtos.cs:183`) and is supplied
by module 19 from the engine clock. `HitCount` is `1`, matching `BasicAttack.cs:230`. No magnitude is
computed here — the cast's damage is authored by its atoms and resolved by the shipped
`CombatDamageDispatcher`/`OverlayCombatCalculator` path the injector already wires
(`EffectRuntime.cs:551-554`, `WireCombatMath`).

## Code style

- Pure plan in Core, thin fire site in the injector (CI never builds the injector,
  `gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:10-14`).
- Fail closed, never throw into the drain; report once through `CheatState.Error`, the shape
  `EffectRuntime.cs:383` already uses.
- Additive DTO fields default to the value every existing construction site already implies, with the
  reason in the doc comment — the convention `EffectDtos.cs:194-226` establishes three times.
- The activation event is built exactly like battle's (`BasicAttack.cs:220-231`), field for field, plus
  the discriminator.

## Testing strategy

Core, in memory, over the pure plan; the injector half is a thin adapter with no logic to test
separately.

| # | Test | Asserts the contract |
|---|---|---|
| 1 | The plan's steps occur in order pay → cooldown → event; **planted violation:** emitting the event before paying fails | Commit ordering |
| 2 | An `InsufficientFunds` outcome starts no cooldown and produces no event | Refusal is total |
| 3 | The built event has `Trigger == EffectTriggers.OnActivate`, `HitCount == 1`, and the post-decision target | Parity with `BasicAttack.cs:220-231` |
| 4 | `CastOrigin` is `true` on a cast event and `false` on a default-constructed `EffectEventDto` | The additive default |
| 5 | A synthetic `OnDamageDealt` record with `CastOrigin == true` and `IsFirstOfSwing == true` charges **nothing**; the same record with `CastOrigin == false` charges once | The double-charge refusal, both directions |
| 6 | The same record does not increment module 19's per-actor swing counter | The feedback-loop refusal (shared fixture with module 19's tests) |
| 7 | `Fire` entered at depth 1 refuses, reports, and releases its token | Hot rule 7, as a refusal not an argument |
| 8 | A dead actor or target ptr skips without throwing and releases the token | Hot rules 1 and 2 |
| 9 | `FoundationContractVersion.Current` is unchanged by the added field | A closed, code-owned version constant; the test says why it is pinned |

**Never asserted:** how many casts occur, how much damage one deals, or any authored action name —
readings and generated text (`validation-ssot.md`).

**Mutation to kill:** delete the `if (ev.CastOrigin) return true;` early return — test 5 must go red.

**Goldens.** Battle is untouched: `BasicAttack.cs` is read as the reference and not edited. The one
shared-surface change is an additive, default-`false` field on `EffectEventDto`, the same shape
`TargetRow`/`Wave`/`InstakillShaped` already took without moving the contract version
(`EffectDtos.cs:194-215,219-236`). **Verify rather than assume** — a DTO that any golden serializes
would gain a key: run
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` plus the effects
contract tests, and state the result either way. If a golden moves, it moves for one stated cause and
is re-blessed in its own commit (`tunables-ssot.md` T7 ordering, as
`../action-skill-tiers/spec-holder-rung-pricing.md:167-171` applies it).

## Boundaries

- **Always:** pay on commit before anything else; runner → bag → flush, in that order; flush once;
  stamp `CastOrigin` on every event this module raises; re-check liveness at fire time; release the
  token on every refusal path.
- **Ask first:** whether the lawn basic-attack **elemental rider** should also be suppressed on a
  cast-origin record (Open question 1 — it is a grant-scoping decision, not a charging one); refunding a
  cast whose target died between decision and fire.
- **Never:** modify `EventDrain`'s swing identity or dedupe; call Unity `TakeDamage` from FA10; emit an
  absolute HP value through the Funnel (`overlay-control-loops.md:153`); recurse into `Fire`; add a
  second kill switch; introduce a new trigger string (the vocabulary is closed and reviewed,
  `EffectDtos.cs:27-29`).

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Two, both already on the closed register: 7, *proc and trigger
   condition* (`battle-engine-ssot.md:135`) and 8, *action system* (`:136`). Nothing is added.
2. **Decide or resolve (§3c)?** **Resolve.** The choice arrived from the AI through
   `IIntentSource.TryDeclare`; this executes it. §3c's table is explicit: *"which action to use"* is the
   AI's, *"cost, cooldown, effect, outcome"* is the engine's (`battle-engine-ssot.md:193`).
3. **Mechanism or loop?** **Mechanism** — one activation edge, one trigger string, raised identically in
   battle and on the lawn. *When* it is raised is module 19's loop.
4. **Which existing implementation does it extend?** `EffectBag.OnEvent` + the Funnel → FA10 tail
   already running in the injector (`EffectRuntime.cs:359,375-377`), and battle's own `OnActivate` raise
   (`BasicAttack.cs:215-232`). It copies neither into a new write path — S4's inventory is explicit that
   *"no new write path"* is needed (`../research/combat-ai/S4-lawn.md:79-80`).
5. **Does every mode get it?** `OnActivate` is battle-raised today (`BasicAttack.cs:220-231`) and is one
   of the four triggers battle does fire (`battle-engine-ssot.md:231`). This closes the lawn's side, so
   the answer is yes after this module.
6. **Is it deterministic and seeded?** It reads no clock — `Tick` is passed in from the engine clock by
   module 19. Its only randomness is a spread cost's `AtomRng`, supplied by the caller
   (`CostLedger.cs:106,121`). The lawn itself is the non-deterministic driver of deterministic
   mechanisms (`battle-engine-ssot.md:106-111`) and carries no replay contract
   (`../research/combat-ai/S4-lawn.md:67-68`); the plan half is a pure function of its inputs and every
   test above exercises it that way.

## Success criteria

1. An `ActionIntent` chosen by a policy results in the action's `OnActivate` atoms reaching
   `EffectBag`, the Funnel and `EntityStatWriter` on a live lawn, through the existing tail with no new
   write path.
2. The cast's cost is charged exactly once, at commit, through module 17's ledger.
3. A cast-origin record is never charged as a basic-attack swing and never counted as a swing —
   both proven by planted violations, not by argument.
4. `Fire` cannot recurse: depth 1 refuses and reports.
5. A dead ptr at fire time is a skip, not a throw, and the token is released.
6. `guard-funnel-delta.py` and `guard-single-writer.py` green; no golden moves, with the suite run
   and the result stated.

## Open questions

1. **Should the basic-attack elemental rider fire on a cast-origin damage record?** The discriminator's
   contract covers the two failures the ideal names — the charge and the counter. A third question sits
   next to them: the per-ptr basic-attack grant is `OnDamageDealt`-triggered
   (`gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs:247-248`), so with
   `ShouldApplyRider` returning `true` for a cast record, a cast's damage would also carry the
   *basic-attack's* elemental payload, which the cast's own atoms did not author.
   Options: (a) let it fire — simplest, and the rider is the actor's element either way;
   (b) suppress it by scoping the grant off cast records — one line, `return false` instead of `true`,
   which also skips the cast record's other on-hit procs.
   **Recommended default: (a)**, because (b) silently disables every on-hit proc for cast damage, which
   is a larger behaviour change than the one being avoided. The implementation is one line apart either
   way, and this is a grant-scoping decision owned by the basic-attack rider, not by this module.
   **Still open 2026-09-22**, and it cannot be settled here: the choice lives in `ShouldApplyRider`
   (`gk-fusion/src/FusionRpg.Injector/**`) and depends on the `EffectEventDto.CastOrigin` field landing first -
   the same two out-of-fence files this spec's status line already names as owed.
2. **Cross-module note (module 19):** the token release on every refusal path (steps 3, 4 and the depth
   guard) is specified here but implemented in module 19's pool. Doom 2016's documented failure is *a
   token never released* (`../combat-ai-ideal.md:210`), so module 19's timeout backstop must cover a
   refusal this module fails to report, not merely a slow cast.
   **ANSWERED 2026-09-22 (lane `cai4`):** **the pool half has landed.** `LawnCastTokenPool` (`CAI4.7`) is the timeout backstop -
   `ReclaimExpired` reclaims *at* the timeout, release is idempotent and can never go negative, and
   re-leasing for the same actor is the same cast rather than a second token. `CAI-loop-1` composes
   acquisition and release around the cast. What is still owed is this module's own `Fire`, so the
   backstop has no live refusal to cover yet.
3. **Cross-module note (`event-pipeline`):** `GameEventKind.ChainSynthetic` (`GameEventRec.cs:12`) has
   no producer anywhere in `src/`. Whoever adds the first one inherits the obligation in §2 — carry
   `CastOrigin` onto the record and through `ToDto` — or the latent loop becomes live at that moment.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: effects/atoms (activation edge), injector-to-game
    event pipeline, actions, lawn AI.
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json).
[x] I read every doc in the §1 row(s) this session: overlay-control-loops.md (§3 and §6 in full),
    battle-engine-ssot.md, combat-ai-ideal.md, combat-ai-map.md, AUDIT.md (M11 in particular),
    S4-lawn.md.
[x] I checked decisions.md: the "Battle engine is the SSOT" row (:53) and the "Action selection" row
    (:44). Neither locks a lawn activation path; :53's own D3 records that 9 of 13 triggers never fire
    in battle, which is why OnActivate (one of the four that do) is the right edge to copy.
[x] Every factual claim cites file:line, and every cited file was opened this session -- including
    EventDrain's swing dedupe, GameEventRec's kind enum, EffectDtos' trigger list and DTO fields, and
    BasicAttack's OnActivate raise.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the *(2026-09-22:
    the plan and its tests have since landed; the marker now applies only to the Contracts and Injector rows)*
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments. The most important verification is a NEGATIVE one:
    grep for ChainSynthetic across src/ returns only EventDrain.cs:81,118,605 and the enum declaration,
    so the feedback loop is latent rather than live -- and the spec says so instead of overstating it.
[x] I read the surrounding section of every rule I quoted (control-loops §6 rules 1-7 in full, §5's
    worked Hot example, battle-engine-ssot §3c and §5 in full).
[~] I tested (not assumed) any constraint I am reporting. **Gap named honestly:** no suite was run in
    this spec session. The golden/contract-version claim is written as a command to run with the result
    stated either way, and the re-entry claim is derived from the locked invariant plus the absence of a
    ChainSynthetic producer, both cited, not measured live.
[x] Nothing contradicts a §2 invariant. Hot rules 1, 2, 3, 6 and 7 are each honoured and cited by line.
[x] Corrections propagated: Open question 3 hands the ChainSynthetic obligation to whoever builds that
    producer rather than leaving it implicit.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal (FoundationContractVersion.Current) is a closed, code-owned version
    constant and the test states why it is pinned.
[x] Event-refreshed cache (§2.16): this module introduces no cache. It consumes module 15's derived
    memo through module 17's ledger, whose invalidators module 15 lists in full including its key-set
    edges (spawn, death).
[x] No acceptance criterion silently fixes an ordering that can vary. The one order that is fixed --
    runner before bag before flush -- is NOT variable in real play: it is a documented trap
    (BasicAttack.cs:226-214), and test 1 plants the violation rather than assuming the order.
[x] Produces no actor combat/derived magnitude itself: the cast's numbers are authored atoms resolved
    by the shipped dispatcher. It consumes Hub output through module 17's ledger only. No second
    composer, no private fold; BattleStatComposer is not cited as precedent.
[x] Does not invent or extend a SOLID-violating parallel path: it calls the existing activation edge
    and the existing Funnel tail, and explicitly refuses to add a second write path or a second kill
    switch.
[~] A new rule has a registry row. **Gap named honestly:** the rule "a cast-origin record is never
    charged and never counted" is guarded by this module's planted-violation tests 5 and 6 only.
    Whether it also earns an enforcement-registry row (or rides guard-funnel-delta's family) is a plan
    decision, unresolved here.
```

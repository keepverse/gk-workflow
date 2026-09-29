# Spec: `resolvable-here` (combat-ai module 5)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) rev 3 ·
**Depends on:** `core-scorer` (module 1) · **Unblocks:** `auto-policy-switch` (14), and every place-wiring
module that gives an actor a real loadout (`siege-loadout-wiring` 12, `delve-automated-wiring` 13,
`lawn-held-actions` 16) · **Status:** the Core half is built (CAI1.12, 2026-09-20), and the lawn sink's
own declaration landed in the same module's follow-up session (CAI1.12, injector half); no policy
consumes the filter yet (`auto-policy-switch`, module 14, is the first).

## Objective

**An action can be perfectly legal and still do nothing, because the place it was chosen in has no
executor for its effects.** Battle's plan-item executor consumes exactly four opcodes —
`ApplyStatus`, `ModifyStat`, `PlaceStructure`, `ApplyResourceDelta` — and its own comment says the rest are
inert: *"battle mode consumes ApplyResourceDelta (FA10) / ApplyStatus (FA2) / ModifyStat (FA1) /
PlaceStructure (Siege) only; every other action is inert here"*
(`gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:241-264`). Battle also raises only a handful of the 13 atom
triggers — `OnActivate` (`BasicAttack.cs:226`, `Siege/ConstructionActions.cs:274`) and `OnDamageDealt`
(`BasicAttack.cs:436`) from its own code, plus the bag's `OnGranted`/`OnRemoved` lifecycle — which is
battle-engine-ssot **D3**: *"9 of 13 atom triggers never fire in battle."*

`UsabilityEvaluator` (`gk-core/src/FusionRpg.Core/Actions/UsabilityEvaluator.cs:52-83`) does not and must not
catch this. Its six gates answer *"may this actor legally do this"* — stance, bound, cooldown, afford,
range, condition. All six pass for an action whose every effect is inert here. So a scorer that values a
`status.clear` support action in battle will commit the turn, pay the `onCommit` cost
(`TimelineDispatch.cs:161`), start the cooldown — and apply nothing. Today no AI scores, so nobody has
paid for this; the moment `auto-policy-switch` makes a profiled policy the default for every battle and
expedition, every such action becomes a wasted turn on the idle economy's own path.

**This module builds the filter, and it derives it from each place's own executor — never from an authored
per-profile allowlist.** An authored list is the defect in advance: it is a second copy of the executor's
truth, it drifts the first time a sink gains an opcode, and a profile author has no way to know which
opcodes a place runs.

The repo already has this exact question asked one moment earlier. `BindGate.Check`
(`gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs:37-92`) is *"the bind-time gate. Load-time validation proves
a row is **well-formed**; this proves it is **executable here**"* — it reads
`AtomKind.SupportIn(runtime)` (`AtomKind.cs:217`) against the audited `RuntimeSupportMatrix`
(`AtomKind.cs:78-87`). **`resolvable-here` is the same question at decision time**, and it extends that
mechanism rather than forking it.

## Tech stack

`FusionRpg.Core` (the filter and the contracts), plus a declaration on each executor sink:
`Core/Battle/BattleEffects.cs` and `Injector/Effects/InjectorEffectActionSink.cs`. No new dependency, no
tuning file, no data. The injector edit is a declaration only — no logic crosses into it, and
`guard-secondary-no-unity.py` stays green because the filter itself never references Unity.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ResolvableHere|BattleEffects|AtomKindRegistry|BindGate"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
python gk-core/scripts/guard-battle-responsibility.py
python gk-core/scripts/guard-secondary-no-unity.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

No `publish.py` call: this module introduces no tunable (see Tunables).

## Project structure

| What | Where |
|---|---|
| The filter, the place profile, the footprint | `gk-core/src/FusionRpg.Core/Actions/ResolvableHere.cs` (new — **landed**, CAI1.12) |
| The declaration contract a sink implements | `gk-core/src/FusionRpg.Core/Effects/EffectModels.cs` — a sibling interface beside `IEffectActionSink` (`:120-124`) |
| Battle's declaration (the four opcodes) | `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:238-284` — the `Execute` body is a dispatch table, and the table **is** the allowlist |
| Battle's raised-trigger declaration | `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs` — a static array beside the sink; D3's four |
| Lawn's declaration | `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEffectActionSink.cs` — a declared array + the drift test below |
| Footprint construction (once per battle) | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:780-811`, beside `BindContainers`, which already walks action → `ContainerId` → `effectIds` |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/ResolvableHereTests.cs` (new — **landed**, CAI1.12) |
| Anti-drift source scan | same file — reads `BattleEffects.cs` / `InjectorEffectActionSink.cs` as text, the idiom `ActionSelectionTests.cs:334-342` already uses |

## The shape

### 1. What a place declares

```csharp
/// What a PLACE can actually execute. Every field is read from the place's own sink and host —
/// never authored in a profile, never copied into tuning.
public readonly record struct PlaceExecutionProfile(
    RuntimeId Runtime,                        // AtomKind.cs:89-94 — Lawn | Battle | Sim
    IReadOnlySet<string> ExecutedActions,     // EffectActions.* opcodes this place's sink runs
    IReadOnlySet<string> RaisedTriggers,      // AtomTriggers.* this place actually raises
    bool IsPlanner);                          // BindGate's own PlanOnly distinction (BindGate.cs:77-81)
```

**A place declares its allowlist by handing over its sink's own dispatch table.** Concretely:

```csharp
/// Implemented BY THE SINK, next to Execute. A sink that does not declare is refused loudly —
/// there is no permissive default, because "assume it executes everything" is exactly the silent
/// no-op this layer refuses (BindGate.cs:24).
public interface IDeclaresExecution
{
    IReadOnlySet<string> ExecutedActions { get; }
}
```

- **Battle.** `BattleEffectSink.Execute` (`BattleEffects.cs:238-284`) was four
  `string.Equals(item.Action, EffectActions.X, OrdinalIgnoreCase)` branches and a fall-through comment.
  It is now one `IReadOnlyDictionary<string, Handler>` keyed `OrdinalIgnoreCase`, dispatched through,
  and `ExecutedActions => _handlers.Keys`. **The list cannot drift from the executor because it *is* the
  executor.** Behaviour is identical: the same four opcodes, the same order-independent match, the same
  `return true` (inert, not a failure) for anything else.
- **Lawn.** `InjectorEffectActionSink` runs ten opcodes and is much larger; converting it to a table is
  not required by this module. It declares a `static readonly string[] Executes` beside its switch, and a
  **source-scan test** asserts the declared set equals the set of `EffectActions.*` constants the file's
  own dispatch references — the drift backstop, in the idiom `ActionSelectionTests.cs:334-342` already
  uses for a seam it wants to keep honest.
- **Triggers** are raised by the host, not the sink, so the host declares them: battle's array is
  `BattleEffectHost.RaisedTriggers`, with a source-scan test asserting that every `AtomTriggers.X`
  reference under `gk-core/src/FusionRpg.Core/Battle/**` appears in it. That test is battle-engine-ssot D3
  expressed as a check instead of a sentence — when battle starts raising a twelfth trigger, the
  declaration moves with it or the test fails.

> **CORRECTION, CAI1.12 (2026-09-20) — the trigger set is eleven, not four.** This spec's §1, §5 and
> Objective all say battle raises four triggers. Read against the code, that is a stale subset:
> `BattleRunState`'s `RaiseTrigger`/`RaiseLifecycle` call sites raise `OnSpawn`, `OnDamageDealt`,
> `OnDamageTaken`, `OnDeath`, `OnActivate`, `OnTimer`, `OnWave`, `OnMatchStart`, `OnMatchEnd`, and
> `EffectBag` raises the `OnGranted`/`OnRemoved` lifecycle pair. Only `OnSunCollect` and `OnGridPlace`
> are genuinely absent. The shipped array therefore carries all eleven, and the source scan reads every
> `AtomTriggers.X` reference (not just `Trigger = AtomTriggers.` literals) so the `RaiseTrigger(...)`
> arguments count too. Declaring the four would make this filter veto real content whose trigger DOES
> fire. `OnGranted`/`OnRemoved` are declared explicitly because `EffectBag` lives outside `Battle/**`.
>
> **CORRECTION, CAI1.12 — the lawn sink's declaration, and where the interface lives.** The lane that
> built the Core half could not reach `Effects/EffectModels.cs` or `gk-fusion/src/FusionRpg.Injector/**`, so it
> left `IDeclaresExecution` in `Actions/ResolvableHere.cs` and did not build the lawn half.
> **Both are now done** (CAI1.12, injector half): the interface sits beside `IEffectActionSink` in
> `Effects/EffectModels.cs` as §1 says, no second copy remains, and
> `InjectorEffectActionSink` declares its opcodes in `Executes`, held to its own dispatch switch by
> `The_lawn_sinks_declared_allowlist_matches_every_EffectActions_constant_its_dispatch_references`.
> The `InjectorEffectActionSink` declaration is appended at the end of the class deliberately: an
> insertion beside the switch would have shifted every `file:line` citation into that file.

### 2. What an action declares

```csharp
/// One action's effect surface, computed ONCE per battle (never per decision) from the same
/// action -> ContainerId -> effectIds walk BindContainers already does (BattleRunState.cs:780-811),
/// reading each EffectDefDto's own Triggers and Actions (EffectDtos.cs:285-301).
public readonly record struct ActionEffectFootprint(
    string ActionId,
    int DeclaredUnits,                        // (trigger, opcode) pairs the action's effects declare
    int ResolvableUnits,                      // how many of them this place can both raise and execute
    ActionCategory? Category);                // CompiledAction.Category (CompiledAction.cs:51)
```

An **effect unit** is one `(trigger, opcode)` pair: an `EffectDefDto.Triggers` entry crossed with an
`EffectDefActionDto.Action` entry (`EffectDtos.cs:292-300`). It is resolvable here when the place both
**raises** that trigger and **executes** that opcode. Two effect paths exist and both terminate at the
same sink — the Compiled path through `EffectBag`, and the Runner path (`containersWithRunnerCoverage`,
`BattleRunState.cs:780-811`) whose dispatch is `EffectFunnel.EnqueueModifier` into the same bag — so **one
allowlist per place covers both**. A container resolvable through neither path already throws at bind
(`BattleRunState.cs:780-811`); this module never re-decides that.

Declarative kinds have no opcode by design — `stat.derived` is *"No opcode — direct derived-channel
mods"* and `AtomKindRegistry.cs` gives it `AtomTriggers.None`, and `bullet.modify` is read as a resolved
grant rather than executed. Those contribute **zero declared units**, because there is nothing for a
trigger to fire; they are folded at resolve time, so an action carrying only declarative atoms is never
"inert" and is never vetoed.

### 3. The verdict, and exactly when it vetoes

```csharp
public enum Resolvability { Full, Partial, Inert }

public static class ResolvableHere
{
    public static Resolvability Of(in ActionEffectFootprint f) =>
        f.DeclaredUnits == 0            ? Resolvability.Full
        : f.ResolvableUnits == 0        ? Resolvability.Inert
        : f.ResolvableUnits < f.DeclaredUnits ? Resolvability.Partial
        : Resolvability.Full;

    /// The gate. Vetoes ONLY an action whose value is carried entirely by effects that cannot fire
    /// here. Attack and Movement actions carry an engine-resolved outcome of their own (the hit at
    /// TimelineDispatch.cs:271; the move), so an inert rider never removes them from the pool.
    public static bool Veto(in ActionEffectFootprint f) =>
        Of(f) == Resolvability.Inert
        && f.Category is ActionCategory.Support or ActionCategory.Status or ActionCategory.Defense;
}
```

Three decisions worth defending, because each is where this could go wrong:

1. **Why not "vetoes anything with an inert unit".** A damage action with an inert on-hit rider still
   deals its damage. Removing it would delete working content from the pool, which is a worse failure than
   the one this module fixes. `Partial` is **reported, never vetoed** — it is one of the fields
   `decision-inspector` (module 10) shows, so a designer can see *"this rider does nothing in battle"*
   instead of guessing.
2. **Why the category test.** `ActionCategory` is a closed five-member vocabulary the code owns
   (`ActionEnums.cs:26-33`), so keying on it invents nothing. `Attack`/`Movement` resolve through the
   engine regardless of atoms. `Support`/`Status`/`Defense` are the three whose whole point is the effect.
3. **Why `null` fails open.** `CompiledAction.Category` is *"`null` for an action the corpus has not
   categorized"* (`CompiledAction.cs:17-21`). An uncategorised action is never vetoed: silently removing
   content the filter cannot classify is the bug, and the `Partial`/`Inert` report still surfaces it.

### 4. Where the gate runs, and where it must not

The filter runs **inside the policy**, in the core scorer's action stage — after `UsabilityEvaluator`'s six
gates, before the reserve floor (ideal §6.1 step 3). It is **not** a seventh `UsabilityEvaluator` gate, and
that is deliberate: the evaluator is shared with non-AI callers, and `CostLedger.Check`'s own doc says a
caller *"may poll this every frame (a greyed-out button)"* (`CostLedger.cs:79-84`). Greying a player's
button because the AI would waste the turn is a different product decision, in a different layer. The AI
declines; the player may still choose.

Cost: one `int` comparison and one enum test per candidate action, against a footprint computed once per
battle. **Zero allocation per decision** — the footprint table is built at setup and read by
`actionId`; the filter takes it `in` and returns an enum (`decision-perf`, module 7, holds the line).

### 5. How a place gets its profile

| Place | `Runtime` | `ExecutedActions` | `RaisedTriggers` | Built where |
|---|---|---|---|---|
| Battle / expedition / delve / siege | `RuntimeId.Battle` | `BattleEffectSink`'s dispatch table (4 today) | battle's declared array (`BattleEffectHost.RaisedTriggers` — see §1's correction note below) | `BattleRunState`, beside `BindContainers` |
| Lawn | `RuntimeId.Lawn` | `InjectorEffectActionSink`'s declared set (`Executes` — 13 arms today) | the injector's raised set (all 13 per ideal §4.3) | module 16's lawn held-action registry |
| Sim | `RuntimeId.Sim` | the sim host's own | the sim host's own | `SimEffectHost` |

Delve and siege are `RuntimeId.Battle` because they resolve through `BattleEngine` with the same sink;
that is the correct answer, not an approximation — if a mode ever gains a different sink it declares a
different profile, and nothing else changes.

## Tunables

**None.** Every input is a closed vocabulary or a read of an executor:

- `EffectActions.*` (`gk-core/src/FusionRpg.Contracts/EffectDtos.cs:57-109`) — opcodes, code-owned.
- `AtomTriggers` — 13, code-owned (`AtomKindRegistry.cs:48` `TriggerCount = 13`, structural).
- `ActionCategory` — 5, code-owned (`ActionEnums.cs:26-33`).
- `RuntimeId` — 3 (`AtomKind.cs:89-94`).

A number here would be a copy of an executor, which is the exact failure this module exists to avoid.
No `const` is added either, so `tunables-ssot.md` gains no row and `ssot-power-scale.md` §11 gains no cap.

## Code style

- The allowlist is the dispatch table, not a list beside it. A second list that must agree with the code
  is the drift this module is about.
- Refuse loudly, never permissively: a sink that does not declare is an exception at construction, not an
  assumed-full default (`BindGate.cs:24` and `AtomKindRegistry.cs`'s own `RuntimeState.None` are the
  precedents — *"Unknown kind is a refusal, never a skip"*).
- `OrdinalIgnoreCase` for opcode comparison, matching `BattleEffects.cs:241-264` exactly.
- Struct records and `in` parameters on anything the decision path touches
  (`IntentSource.cs:6-11` states the reason: one heap object per actor per turn on a 200-entity board).
- Footprints are computed once at setup and frozen, the same discipline `CompiledAction.cs:10-15` states
  for its own record (*"Nothing here is re-derived per resolve"*).

## Testing strategy

`gk-core/tests/FusionRpg.Core.Tests/Actions/ResolvableHereTests.cs` (new):

| Test | Asserts |
|---|---|
| `Battles_declared_allowlist_equals_its_dispatch_table` | The declaration and the executor are the same object. This is the anti-drift contract |
| `The_lawn_sinks_declared_allowlist_matches_every_EffectActions_constant_its_dispatch_references` | Source-scan drift backstop for the injector sink |
| `Every_trigger_battle_raises_appears_in_its_declared_trigger_set` | Source scan over `gk-core/src/FusionRpg.Core/Battle/**` for `Trigger = AtomTriggers.` — battle-engine-ssot D3 as a check |
| `An_action_with_no_declared_effect_units_is_Full_everywhere` | The basic attack, and every plain attack, is never touched |
| `A_status_only_support_action_is_Inert_in_battle_and_Full_on_the_lawn` | `status.clear` is `RuntimeState.Full` on the lawn and `None` in battle (`AtomKindRegistry.cs:701`); the filter agrees with the matrix without reading it |
| `An_attack_action_with_an_inert_rider_is_Partial_and_is_never_vetoed` | Decision 1 above |
| `An_uncategorised_action_is_never_vetoed_and_still_reports_its_resolvability` | Fail-open |
| `A_place_profile_is_built_from_the_sink_and_never_from_a_profile_row` | Architecture test: the new `gk-core/src/FusionRpg.Core/Actions/ResolvableHere.cs` contains no reference to the tuning/profile types |
| `A_sink_that_does_not_declare_is_refused_at_construction` | Loud refusal |
| `The_filter_allocates_zero_bytes_across_two_hundred_candidate_actions` | `GC.GetAllocatedBytesForCurrentThread` with the warm+collect harness `KernelAllocationTests.cs:18-28` established |
| `A_footprint_is_computed_once_per_battle_and_not_per_decision` | A counting resolver asserts one walk per action per battle |

**Contract assertions only.** Nothing pins how many actions exist, how many are inert, or any generated
name. The pinned literals are closed vocabularies with a named reason: `EffectActions` membership,
`AtomTriggers` count, `ActionCategory`'s five. The battle allowlist's *size* is deliberately **not**
pinned — it is asserted equal to the dispatch table, so widening the executor (a reviewed change, per the
DESIGN-GATE Battle/turns row) moves both together and the test stays green for the right reason.

**Golden impact: byte-identical.** No policy consumes the filter until `core-scorer`'s profiled policy is
the default, which is module 14's own single cause. The one change to shipped behaviour is
`BattleEffectSink.Execute`'s refactor from four `if`s to a table, which executes the same four opcodes —
run `BattleGoldenTests`, `ExpeditionResolverTests` and the battle status/stat/structure apply suites and
report the result rather than asserting it.

## Boundaries

**Always**

- Derive the allowlist from the executor, and keep the executor and the declaration the same object where
  the sink's size allows.
- Compute a footprint once per battle, never per decision.
- Report `Partial`; veto only `Inert`, and only for the three effect-carried categories.
- Fail open on an uncategorised action.

**Ask first**

- Widening a place's executor allowlist to make an action resolvable. That is a reviewed change to the
  Battle row's four-opcode rule (DESIGN-GATE §1, Battle / turns) and belongs to whichever program wants
  the opcode — never to the AI, which only reads it.

**Never**

- Author a per-profile or per-place opcode list in `gk-core/data/tuning/**`. The ideal §4.3 names this
  explicitly: *"The filter derives from the executor allowlist and is not authored per profile."*
- Add a seventh gate to `UsabilityEvaluator` — it serves non-AI callers who must not be gated by an AI's
  opinion.
- Build a second runtime-support matrix beside `AtomKindRegistry`'s. The registry answers *"can this kind
  ever run here"*; this module answers *"will this action's effects fire here, now"*. Two questions, one
  vocabulary.
- Veto an action the filter cannot classify.
- Let the injector own any of this logic: the filter is Core, the injector declares and adapts.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** None — no new register row. It reads two existing ones
   (7 proc/trigger, 8 action system) and decides nothing about either. Its own subject, "will this action's
   effects fire in this place", is a property of the register, not a member of it.
2. **Does it DECIDE or RESOLVE?** Decide. It removes an option from the AI's pool before
   `IIntentSource.TryDeclare` returns. It never changes what the executor does with an action that is
   chosen anyway — a player, a scripted encounter or a debug call can still fire an inert action, and it
   stays inert.
3. **Mechanism or loop?** **Mechanism**, one implementation for every mode. The *content* of a place's
   allowlist is per-place because the executors genuinely differ; the way a place declares one, and the
   way the filter reads it, is shared. That is the §2 split applied exactly: battle and the lawn differ in
   what their sinks run, never in what "resolvable" means.
4. **Which existing implementation does it extend?** `BindGate` / `RuntimeSupportMatrix`
   (`BindGate.cs:37-92`, `AtomKind.cs:78-87`) — the same *executable here* question, asked at decision time
   instead of bind time, over the same vocabulary. It also extends `BattleEffectSink`'s existing allowlist
   rather than restating it. It copies nothing and estimates nothing.
5. **Does every mode get it?** Yes. Battle, delve and siege share one profile because they share one sink;
   the lawn and sim declare their own. There is no "battle only" carve-out, and the lawn's larger
   allowlist is a fact about its sink, not an exception to the rule.
6. **Is it deterministic and seeded?** Yes, and it reads no RNG. `Of`/`Veto` are pure functions of
   `(footprint, place profile)`; the footprint is built once from frozen content at setup. No clock, no
   ambient state, nothing to seed. A replay computes the same footprints from the same setup.

## Success criteria

1. `BattleEffectSink` dispatches through a table, and `ExecutedActions` returns that table's keys — grep
   finds no second list of battle's opcodes anywhere.
2. The injector sink declares its set, and the source-scan test fails if the two diverge.
3. Battle's raised-trigger declaration exists and the D3 source-scan test passes against it.
4. `ResolvableHere.Of` returns `Full` for a zero-unit action, `Inert` for a battle-inert status-only
   support action, and `Partial` for an attack with an inert rider.
5. `Veto` is true only for `Inert` × {`Support`, `Status`, `Defense`}, and never for a `null` category.
6. The filter allocates zero bytes across a 200-action measured pass.
7. No file under `gk-core/data/tuning/**` names an opcode.
8. `BattleGoldenTests` and `ExpeditionResolverTests` unchanged, with the run output quoted in the commit.
9. `guard-battle-responsibility.py` and `guard-secondary-no-unity.py` green.

## Open questions

1. **Should battle's four-opcode allowlist be widened instead of filtered around?** battle-engine-ssot D1
   and D3 are open defects: battle's `EffectBag` never sets `CombatMath`, and nine triggers never fire
   there. A wider battle executor would make most of this filter return `Full`. Options: (a) build the
   filter now and let it narrow as the executor widens — what this spec does, and the filter stays correct
   either way; (b) block on widening the executor first; (c) both, in parallel programs. **Recommended
   default: (a).** The filter is correct at every width, costs one comparison, and closing D1/D3 is
   explicitly another program's work (battle-engine-ssot §4). **Cross-program note:** whoever closes D1/D3
   must move battle's declared trigger array in the same change, and the source-scan test makes that
   automatic rather than remembered.
2. **Does a `Partial` verdict deserve a score penalty rather than only a report?** An action that fires one
   of four riders here is worth less than one that fires all four, and the scorer currently cannot tell.
   Options: (a) report only — this spec; (b) scale the action's score by `ResolvableUnits / DeclaredUnits`;
   (c) let a profile weight it. **Recommended default: (a)**, because (b) values each unit equally, which
   is false (one rider can be the whole point), and the AI has no per-atom value model to do better.
   **Cross-module note for `core-scorer` (module 1) and `profile-schema` (module 2):** if a penalty is
   wanted later it is a weight in the profile, reading the `ResolvableUnits`/`DeclaredUnits` the footprint
   already carries — no new mechanism, and no change here.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: the atom/effect layer's executable-here gate, battle's
    plan-item executor, the action model, and the AI decision path.
[~] I established and recorded this session's boundary: /spec authoring lane under session
    backlog-clean-up-20260920 (record named by combat-ai-map.md). I did NOT run
    session-boundary-check.py — this lane runs no repo mutations and writes only this spec file.
    GAP NAMED.
[x] I read every doc in the §1 row(s) for those subsystems, this session: DESIGN-GATE.md (Battle /
    turns row, which carries the BattleEffects.cs:278-279 rule in code rather than in a doc; the atom
    layer row's 9/18/13 vocabulary), battle-engine-ssot.md §2/§3c/§4 (D1, D3)/§5, combat-ai-map.md,
    combat-ai-ideal.md rev 3 §4.3, research/combat-ai/AUDIT.md (M7).
[x] I checked decisions.md for a lock covering this: the atom attach-point row and the Battle/turns
    row both say widening an executor allowlist is a reviewed change. This spec never widens one.
[x] Every factual claim cites file:line, and every file cited was opened in this session.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses.
[x] I verified claims against CODE, not comments — the four-opcode allowlist was read in
    BattleEffects.cs itself, and battle's raised triggers were counted by grepping
    `Trigger = AtomTriggers.` under Core/Battle rather than taken from D3's sentence (the grep agrees
    with D3: OnActivate x2, OnDamageDealt x1).
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. The "byte-identical" claim for the
    BattleEffectSink table refactor is stated as a claim to RUN, not a result: this lane runs no
    builds or tests by instruction. Success criterion 8 requires the implementer to run and report.
[x] Nothing contradicts a §2 invariant. Invariant 8 (Foundation is sealed) holds: this reads the
    sink's dispatch set, it does not change the Foundation contract.
[x] Corrections propagated: audit M7 and ideal §4.3's last row are answered here; the map's module-5
    row is satisfied in full (derived from the executor, not authored per profile).
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The allowlist's SIZE is deliberately unpinned and asserted equal to the dispatch table
    instead; the only pinned literals are closed vocabularies (EffectActions membership,
    AtomTriggers' 13, ActionCategory's 5) with the reason stated.
[x] If this introduces or touches an event-refreshed cache (§2.16): the footprint table IS a cache,
    keyed by actionId and built at battle setup. Its full invalidation set is enumerated: (1) battle
    setup — the only build; (2) a mid-battle grant that adds a held action (AdditionalHeldActions /
    the garrison-lent union), which is the KEY-SET edge and must add a footprint rather than read a
    missing one; (3) content reload in a long-lived host, which rebuilds every footprint. Each has
    its own test. It is NOT keyed by actor, so an actor entering a state cannot move its key set.
[x] No acceptance criterion fixes an ordering that can vary in real play — the filter is order-free
    by construction (a set membership test).
[x] Produces/consumes no actor combat magnitude; composes nothing. ActorHub is untouched.
[x] Does not invent or extend a SOLID-violating parallel path — it explicitly refuses to build a
    second runtime-support matrix or a second allowlist, and makes the battle sink's allowlist and
    its executor one object.
[x] A new rule has a registry row: the "declaration equals dispatch" rule is enforced by the two
    source-scan tests named above rather than by a shell guard. If the implementer prefers a guard
    script, add it to gk-core/scripts/enforcement-registry.v1.json under `guards`; if the tests are kept as
    the enforcement, the rule needs no new row because it is test-covered, not unguardable.
```

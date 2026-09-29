# Spec: `stance-wiring` (combat-ai module 11)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `profile-schema` (module 2 — it owns the siege→`combat-ai` key migration this spec
finishes), `intent-router` (module 4 — it is the one place a policy is constructed, so it is where a
stance seam is read) · **Unblocks:** nothing in `combat-ai`; it closes the ideal §8 "dead keys" row so
`auto-policy-switch` (14) lands with no unread config behind it ·
**Status:** **built** (CAI3.1, 2026-09-20/21; completed 2026-09-23 by lane `cai2`). `BattleRunState.Stance` is the one `IStanceCheck` and has its one writer (`BattleEngine.Resolve`'s trailing optional `IStanceCheck? stance`), so both behavioural tests drive a real battle and `StanceSeamTests` still pins the single `NoStanceHeld.Instance` literal. **Outcomes 2/3 landed too** — `ai.stanceDefault` and `ai.autoResolveHandicapMilli` are gone: `siege.v3.json` was produced by ONE `--remove-key ×2` invocation, `AiTuning` is narrowed to two members, the four `AiTuning` constructions (including the two test bootstraps this line used to call out-of-fence) were fixed in the same commit, and `SiegeTuning.Parse` deliberately still validates the two removed keys when present (`ValidateRemovedKeys` — absent is legal, wrong is not).

## Objective

The ideal names gate 0 as a wiring gap: *"`Actions/Defence/StanceRuntime.cs:27` has no production
constructor. Every production policy gets `NoStanceHeld.Instance` … `AiTuning.StanceDefault` is parsed
(`SiegeTuning.cs:435`) and read nowhere, and neither is `AutoResolveHandicapMilli`"*
([combat-ai-ideal.md](../combat-ai-ideal.md) §4.2). The map gives this module one instruction and one
test for choosing between its two halves: *"Give `StanceRuntime` a production constructor and route
stance into gate 0 for every policy, **or** delete `StanceRuntime` / `stanceDefault` /
`autoResolveHandicapMilli` with a stated reason. Decision criterion: is any held action a stance action
today?"* ([combat-ai-map.md](../combat-ai-map.md) row 11).

**The criterion's answer is no, and the three things the map lists are not one thing.** Two of them are
a *siege posture enum* that has nothing to do with gate 0, and one of them is another program's shipped,
tested module. So this spec answers the criterion once and then splits the outcome three ways: **wire the
seam, defer the runtime, delete the two dead keys.** §"The decision" is the argument; the rest of the
spec builds it.

The defect actually closed here is smaller than the map's framing and more real than it: **one decision
— "which `IStanceCheck` does a policy get?" — is hardcoded at three separate call sites**
(`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:177`, `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs:80`,
`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:194`, each literally `NoStanceHeld.Instance`). Three copies
of one answer is the S/O shape `intent-router` is already fusing for the fallback chain; this module
fuses the stance half of the same construction, so the day a stance action exists there is **one** line
to change, in `BattleRunState`, not three to find.

## The decision

### The criterion, answered against code

> **Is any held action a stance action today?** **No.** Four independent readings, none of them a
> comment:

| Evidence | What it shows |
|---|---|
| `gk-core/src/FusionRpg.Core/Actions/ActionRow.cs:15-109` | The action row has **no** stance or release-id field. Identity, kind, rung, tags, grant, container, envelope, targeting, range, LoS, projectile penalties, conditions, eligibility, category, pairing role, structure axes, atom families, rung band — and nothing that says "this action raises a stance whose release is action X". The corpus **cannot** declare a stance. |
| `gk-core/src/FusionRpg.Core/Actions/Defence/StanceRuntime.cs:59-67` | `Raise(...)` is the only writer of `_releaseActionIdByActor`, and it takes `releaseActionId` as a caller-supplied argument. Its only callers are `gk-core/tests/FusionRpg.Core.Tests/Actions/DefenceActionStanceTests.cs` and `.../DefenceActionStanceSlotTests.cs`. Zero production callers. |
| `gk-core/src/FusionRpg.Core/Actions/ActionRow.cs:163` + `gk-core/src/FusionRpg.Core/Actions/Grants/ActionSetAssembler.cs:58` | `SpeciesBasicsRow.GuardActionId` looks like a stance and is not one: `AddIntrinsic(basics.GuardActionId)` grants it as an ordinary intrinsic action, with no release id and no raise call. |
| `gk-data/packs/fusion/data/seed/actions/authored-basics.json:9` | The corpus says it in its own words: *"Only the ATTACK basic is authored here. action-ideal.md D1 names three basics (attack, guard, move); **guard is a STANCE (D3)** and move is movement — neither is needed … and authoring them unused would be content nobody reads."* Two of 55 tracked files under `gk-data/packs/fusion/data/seed/actions/` mention "stance" at all, and this is the one that means it; the rest of the word's occurrences sit in `data/seed/actions/_candidates/`, which `.gitignore:113` excludes from the repo entirely — untracked staging, not corpus. |

**So gate 0 being inert is correct, not broken.** `NoStanceHeld.Instance` returns `null`
(`gk-core/src/FusionRpg.Core/Actions/IAffordabilityCheck.cs:38`), `UsabilityEvaluator` reads that as "does not
refuse" and proceeds to gate 1 (`gk-core/src/FusionRpg.Core/Actions/UsabilityEvaluator.cs:52-55`). That is the
right answer for a world in which no actor can hold a stance. The gap is not *"gate 0 does nothing"*; it
is *"three call sites each decided that separately."*

### Outcome 1 — `StanceRuntime`: **wire the seam, defer the runtime.** Keep the class.

**Wire:** `BattleRunState` gains one `IStanceCheck Stance` property, defaulted to
`NoStanceHeld.Instance`, and the three hardcoded `NoStanceHeld.Instance` arguments become `state.Stance`
/ `Stance`. The `intent-router` (module 4) reads that one property when it constructs any policy, so
every policy — stub, core, siege, and any future one — is gated by the same stance object by
construction rather than by three authors remembering.

**Defer:** this module does **not** construct a `StanceRuntime` in production. Constructing one would be
observably identical to `NoStanceHeld` (its `Check` can only refuse for an actor present in
`_releaseActionIdByActor`, and only `Raise` puts one there — `StanceRuntime.cs:97-103`, `:67`), while
costing an allocation and a `StatusCatalog` registration per battle
(`StanceRuntime.cs:34-47` registers `stance.guard` into the catalog on construction). Wiring a runtime
that provably cannot refuse is wiring for its own sake.

**Do not delete:** deleting `StanceRuntime` would delete another program's shipped, tested deliverable —
A8, [action/spec-defence-actions.md](../action/spec-defence-actions.md) §1 and its Structure block
naming `Actions/Defence/StanceRuntime.cs` — together with its siblings `PoiseLedger.cs` and
`Riposte.cs`, and with the `UsabilityReason.StanceHeld` vocabulary
(`gk-core/src/FusionRpg.Core/Actions/UsabilityResult.cs:12`) that a second module already asserts against
(`gk-core/tests/FusionRpg.Core.Tests/Actions/Aura/AuraRuntimeTests.cs:111-117`, the anti-`StanceHeld`
regression). `combat-ai` decides what its policies read; it does not own `action`/A8's modules, and a
deletion here would be a capability loss and a boundary crossing at once.

**Named trigger for the deferred half, so this is a decision and not a punt:** the moment an action row
can declare a release id — i.e. when A8's raise/release content lands — `BattleRunState.Stance` is
assigned a real `StanceRuntime` in **one** place, and gate 0 becomes live for every policy with no
further routing work. That trigger belongs to the **action** program (A8), and is recorded as a
cross-module note in §"Open questions".

### Outcome 2 — `ai.stanceDefault`: **delete.** Not a capability loss.

It is **not** gate 0. `Siege.Stance` is `Hold / Guard / Engage`
(`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:32`) — a posture governing how far a unit may leave its
post — carried on `AiTuning` at `SiegeAi.cs:62`, parsed and validated at
`gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs:351-353`, seeded `"Guard"` in
`gk-core/data/tuning/siege.v1.json:111`, and read by nothing: `SiegeAiIntentSource` holds an `IStanceCheck`
(`SiegeAiIntentSource.cs:57,84`) and has no `Hold`/`Guard`/`Engage` branch anywhere — the only
occurrences of the `Stance` type in `gk-core/src/FusionRpg.Core/Battle/Siege/` are the enum declaration, one
doc-comment reference, and the `AiTuning` field itself.

**Why deleting is not a loss.** The *capability* — posture gating movement — is siege's own named,
unbuilt work in `spec-siege-ai.md`, not this key. A key that no reader consults expresses nothing; all
it does today is make `SiegeTuning.Parse` reject a tuning file that omits it (`SiegeTuning.cs:465-470`
throws on a missing string). When posture ships, it authors its key beside its reader in one commit
(H7), which is the discipline the ideal states for this exact row: *"**Wired** (stance, §4.2) or
**deleted**. Never migrated as dead config"* ([combat-ai-ideal.md](../combat-ai-ideal.md) §8).

### Outcome 3 — `ai.autoResolveHandicapMilli`: **delete.** Its only possible reader is forbidden.

Parsed and range-checked at `SiegeTuning.cs:355-357`, carried at `SiegeAi.cs:62`, seeded `1000` at
`gk-core/data/tuning/siege.v1.json:112`, read nowhere. Unlike `stanceDefault` it has no deferred owner: **a
handicap on the auto-resolved side is a difficulty lever, and owner ruling D2 rules difficulty out of
AI entirely** — *"In this game we don't make difficulty by AI — only a smart AI, maybe a
performance/dumb AI later. Difficulty will have its own sub-program, designed on gameplay mechanisms"*
([combat-ai-ideal.md](../combat-ai-ideal.md) §10 D2; map load-bearing rule 5: *"There is no difficulty
lever in AI"*). Deleting it removes a key whose only conceivable consumer the program has already
refused to build. That is a correctness improvement, not a capability loss.

## Tech stack

`FusionRpg.Core` (the `IStanceCheck` seam on `BattleRunState`; the `AiTuning` record and
`SiegeTuning` parser) and `data/tuning/siege.v{n+1}.json` published through
`gk-core/tools/tuning/publish.py --remove-key`, a verb **`profile-schema` (module 2) builds and owns** — this
module neither extends nor re-specifies it (§Tunables). No new dependency, no new package, no new
project.

## Commands

```powershell
# `--remove-key` is module 2's verb (spec-profile-schema.md §Tunables) and already exists by the time
# this module runs. ONE invocation, ONE version bump: siege.v2 -> siege.v3.
python gk-core/tools/tuning/publish.py siege --remove-key ai.stanceDefault --remove-key ai.autoResolveHandicapMilli `
  --reason "stance-wiring: two dead ai keys, no reader (SiegeTuning.cs:351-357)" --label "drop dead ai keys"

dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Stance|FullyQualifiedName~SiegeTuning|FullyQualifiedName~DefenceAction"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi|FullyQualifiedName~Golden"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Golden"

.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs',
  'gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs',
  'gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs',
  'gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs',
  'gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs',
  'gk-core/data/tuning/siege.v3.json'
) -Session backlog-clean-up-20260920

python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
```

## Project structure

| File | New/changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | changed | Add `public IStanceCheck Stance { get; init; } = NoStanceHeld.Instance;`; pass it at `:629` instead of the literal. |
| `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | changed | `:165` `NoStanceHeld.Instance` → `state.Stance`. |
| `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs` | changed | `:80` `NoStanceHeld.Instance` → `state.Stance`. |
| `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs` | changed | Drop `Stance StanceDefault` and `int AutoResolveHandicapMilli` from the `AiTuning` record (`:60-64`), taking it from module 2's four members to **two**. Keep the `Stance` enum (`:32`) — it is siege's declared, reviewed vocabulary, and `EmplacementFireMode` (`:46`) is the shipped precedent for a vocabulary that outlives its first consumer. |
| `gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs` | changed | Delete the two parse blocks (`:351-357`) and their two arguments in the `new Siege.AiTuning(...)` construction (`:432-439` on `HEAD`; module 2 has already removed ten of its arguments by then). |
| `gk-core/data/tuning/siege.v3.json` | **new — landed (CAI3.1, lane `cai2`)** | The siege file `profile-schema` leaves behind (its `siege.v2.json`), minus the two keys, published by **one** `--remove-key ×2` invocation. Earlier versions stay on disk as history. |
| `gk-core/tools/tuning/publish.py` | **not changed here** | `--remove-key` is built and owned by `profile-schema` (module 2), which needs it first for its own ten-key migration. This module is its second caller, not its author (§Tunables). |
| `tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs` | changed | Its `new AiTuning(...)` at `:510` loses two arguments **from module 2's four-argument constructor**, leaving two. |
| `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs` | changed | Same, at `:504`. |
| `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs` | changed | Same, at `:441`. |
| `gk-core/tests/FusionRpg.Core.Tests/Battle/Board/SiegeTuningContractTests.cs` | **new — landed (CAI3.1)** | The parser contract (§Testing strategy). There is no siege-tuning parse test file today. |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/SiegeKeyMigrationTests.cs` | changed (created by module 2) | Its `Siege_v2_still_carries_the_two_dead_keys` is superseded and deleted here; the migration-fidelity assertions it also holds are untouched. |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/StanceSeamTests.cs` | **new — landed (CAI3.1)** | The one-seam contract (§Testing strategy). |

`gk-core/src/FusionRpg.Core/Actions/Defence/StanceRuntime.cs`, `PoiseLedger.cs` and `Riposte.cs` are **not
touched**. Neither is `IAffordabilityCheck.cs` (which declares `IStanceCheck` and `NoStanceHeld`).

## The shape

### One stance seam on the run state

```csharp
// BattleRunState -- beside Cooldowns and CostLedger, which are the two seams it already owns and
// hands to every policy (BasicAttack.cs:177, TimelineDispatch.cs:80, BattleRunState.cs:629 all read
// state.Cooldowns / state.CostLedger today and hardcode only the stance argument).
/// <summary>Gate 0's one answer for this battle (UsabilityEvaluator.cs:52-55). Defaults to
/// NoStanceHeld.Instance -- the CORRECT implementation while no action row can declare a stance
/// (ActionRow.cs:15-109 has no release-id field), not a placeholder. A8's raise/release content is
/// what assigns a real StanceRuntime here, in this one place, for every policy at once.</summary>
public IStanceCheck Stance { get; init; } = NoStanceHeld.Instance;
```

Three call sites then read it:

```csharp
// BasicAttack.cs:175-180 (the fallback chain the router takes over in module 4)
?? new StubIntentSource(view, state.Cooldowns, state.Stance, state.CostLedger);

// TimelineDispatch.cs:79-80 (Reselect)
?? new StubIntentSource(view, state.Cooldowns, state.Stance, state.CostLedger);

// BattleRunState.cs:743-757 (the siege default policy)
DefaultAiIntentSource = new SiegeAiIntentSource(this, Cooldowns, Stance, CostLedger, aiTuning, ...);
```

**Byte-identity is by construction, not by measurement:** `Stance`'s default is the same
`NoStanceHeld.Instance` singleton the three sites pass today
(`IAffordabilityCheck.cs:37` — `public static readonly NoStanceHeld Instance = new();`), and no
production code assigns the property. Reference-identical argument, identical `Check` return, identical
short-circuit at `UsabilityEvaluator.cs:54-55`.

**Interaction with `intent-router` (module 4).** Module 4 owns the *one* fallback chain and collapses
these three constructions into itself; its chain's step 4 is written as *"today's
`new StubIntentSource(view, state.Cooldowns, NoStanceHeld.Instance, state.CostLedger)`"*
([spec-intent-router.md](spec-intent-router.md) §1, "The one chain"). This module supplies the property
that literal becomes. Because 11 depends on 4, the normal path is that 11 edits **one** site — the
router's — instead of three. If the order inverts, 4 inherits `state.Stance` already threaded. Either
way there is exactly one seam, which is the point.

### The `AiTuning` shrink

**Start from what module 2 leaves behind, not from what ships today.** `Siege.AiTuning`
(`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:60-64`) has **fourteen** members on `HEAD`, but this module
runs *after* `profile-schema` (module 2), which moves ten of them out and narrows the record to
**four** — *"`SiegeTuningLoader.Parse` stops reading the ten (`SiegeTuning.cs:333-366`), and
`Siege.AiTuning` (`SiegeAi.cs:60-64`) **narrows to exactly four**"*
([spec-profile-schema.md](spec-profile-schema.md) §7 item 3). That four-member record is this module's
**before**:

```csharp
// SiegeAi.cs:60-64 — BEFORE this module, AFTER module 2's commit
public sealed record AiTuning(
    Stance StanceDefault, int AutoResolveHandicapMilli,
    int ObjectiveReferenceDistanceCells, int ThreatRadiusCells);
```

This module deletes the two dead ones, so its **after** is two:

```csharp
// SiegeAi.cs:60-64 — AFTER this module
public sealed record AiTuning(
    int ObjectiveReferenceDistanceCells, int ThreatRadiusCells);
```

Two members, and both are **siege board geometry** — the record is now exactly what its name should
have meant all along: the two numbers the *candidate builder* needs
(`SiegeAiIntentSource.cs:423-430`, `SiegeAiIntentSource.cs:484`), with every scoring number living in
`combat-ai.v1.json` under module 2's schema. If an implementer finds a fourteen- or twelve-member
record in front of them, module 2 has not landed and this module is being built out of order.

**Ordering against `profile-schema` (module 2) — already agreed, in that spec's own words.** Module 2
moves ten `ai` keys to `gk-core/data/tuning/combat-ai.v1.json`, leaves `objectiveReferenceDistanceCells` /
`threatRadiusCells` in its `siege.v2.json`, and explicitly does **not** migrate the two dead ones:
*"The two dead keys stay exactly where they are, untouched … They are `stance-wiring`'s (module 11) to
wire or delete"* ([spec-profile-schema.md](spec-profile-schema.md), migration table and the paragraph
under it). So this module publishes `siege.v3.json` from module 2's `v2`, deletes the two parse blocks
and the two record fields, and never has to un-migrate anything.

**Version numbers, and the tool property they depend on.** Module 2's ten removals are **one**
`publish.py` invocation producing `siege.v2.json`; this module's two removals are **one** invocation
producing `siege.v3.json`. Both rest on `--remove-key` being repeatable within a single invocation with
a single `v{n+1}` write — the semantics module 2 specifies and owns
([spec-profile-schema.md](spec-profile-schema.md) §Tunables). A one-key-per-invocation tool would put
module 2 on `v11` and this module on `v12`.

**One consequence to carry out, not to leave behind.** Module 2 ships
`Siege_v2_still_carries_the_two_dead_keys`, whose stated reason is *"deleting them is module 11's
decision. A test that asserts they are gone would be asserting a decision nobody has made."* This
module **is** that decision, so that test is **superseded** by
`A_siege_tuning_file_without_the_two_removed_keys_parses` (§Testing strategy) and is deleted in this
commit. Leaving both would leave a test asserting the thing this module removed.

### Why the publish and the parser must be one commit (H7)

`SiegeTuning.Str`/`Int` throw `SiegeTuningRejection` on a **missing** key
(`SiegeTuning.cs:458-470`). So publishing `siege.v2.json` without the key removes it from the file and
makes every host that loads it refuse; deleting the parse lines without publishing leaves an
unreferenced key. **One commit: publish `v{n+1}`, delete the parse block, delete the record fields,
update the three test bootstraps.** That is the same-commit reader switch
[combat-ai-map.md](../combat-ai-map.md) hard-edge "A tuning publish lands with its reader (H7)" names.

## Tunables

Nothing is added. Two keys are removed from the siege domain and one number is stated as structural.

| Key | File | Unit | Action | Why |
|---|---|---|---|---|
| `ai.stanceDefault` | `gk-core/data/tuning/siege.v1.json:111` → absent in `v2` | closed enum `Hold`/`Guard`/`Engage` | **remove** | Parsed (`SiegeTuning.cs:351-353`), carried (`SiegeAi.cs:62`), read nowhere. Its capability is siege's own deferred posture work; a dead key is not that capability. |
| `ai.autoResolveHandicapMilli` | `gk-core/data/tuning/siege.v1.json:112` → absent in `v2` | per-mille | **remove** | Parsed (`SiegeTuning.cs:355-357`), carried (`SiegeAi.cs:62`), read nowhere, and its only possible reader is a difficulty lever D2 forbids. |
| `ai.aggressionRange`, `ai.maxCandidatesScored` | stay wherever module 2 puts them | count | **unchanged here** | Already labelled STRUCTURAL in the file's own `_note` (`gk-core/data/tuning/siege.v1.json:102`) — a bounded vocabulary and a per-decision work bound, not progression ceilings. This module does not move or re-label them. |

**The publisher's removal verb is `profile-schema`'s, and this module only calls it.**
`gk-core/tools/tuning/publish.py` ships `key=value` sets, `--add-key`, `--rename-key`, `--add-edge` and several
domain-specific verbs (`gk-core/tools/tuning/publish.py:550-596`) and **no removal path**. `--remove-key` is
built by **module 2**, which needs it first for its own ten-key migration, and that spec owns its full
semantics — the refusal on an unresolvable path, the required `--reason`, and the property that matters
here: **it is repeatable within one invocation and one invocation writes exactly one `v{n+1}`**
([spec-profile-schema.md](spec-profile-schema.md) §Tunables). This module states no rules of its own
about the tool; restating them is how two specs end up describing one flag differently.

The one consequence for this module: its two removals are a **single** publish
(`--remove-key ai.stanceDefault --remove-key ai.autoResolveHandicapMilli`) producing `siege.v3.json`
from module 2's `v2` — never two publishes and never a `v3`/`v4` pair. Hand-editing is not an option:
`gk-core/data/tuning/**` is authored but never hand-edited in place (`CLAUDE.md`, generated/tuning hard rule).

## Code style

- **The seam's default carries its own justification in the doc comment**, the idiom `FamilyDials`
  uses in [lawn-tuning-profile/spec-mode-profile.md](../lawn-tuning-profile/spec-mode-profile.md): say
  *why* `NoStanceHeld` is correct rather than provisional, so the next reader does not "fix" it.
- **`init`-only property with a today-identical default**, matching the optional-seam pattern already
  on `BattleRunState`/`BattleEngine.Resolve` (`aiTuning`, `roundOf`, `board`, `containerResolver` are
  all trailing optionals defaulting to today's behaviour — `BattleEngine.cs:184-233`).
- **A deleted vocabulary member gets a one-line obituary at the deletion site** naming what replaced
  it or why nothing did — the same courtesy `SiegeAi.cs:34-45` pays `EmplacementFireMode` for the
  opposite case.
- No `[JsonIgnore]` work: neither removed key ever touched a serialized battle record.

## Testing strategy

Contract and closed-vocabulary assertions only ([validation-ssot.md](../validation-ssot.md)).

**`gk-core/tests/FusionRpg.Core.Tests/Actions/StanceSeamTests.cs` (new — **landed**, CAI3.1)**

- ✅ `Every_policy_construction_reads_the_run_states_one_stance_seam` — a source-scan over
  `gk-core/src/FusionRpg.Core/Battle/*.cs` finds **zero** remaining `NoStanceHeld.Instance` literals outside
  `IAffordabilityCheck.cs`'s own declaration. This is the module's actual deliverable, so it is the
  assertion, and it is stable across generations (it names a type, not a count of policies).
- ✅ `A_run_state_with_no_stance_assigned_refuses_nothing` — `state.Stance.Check(anyActor, anyAction)`
  is `null`, and an action that would otherwise pass returns `UsabilityResult.Usable`. The identity
  property, asserted rather than assumed.
- ✅ `A_supplied_stance_check_reaches_gate_zero_through_the_run_state` — construct a run state with a
  fake `IStanceCheck` that refuses, drive one decision, assert the refusal is
  `UsabilityReason.StanceHeld`. Proves the seam is *load-bearing*, which the identity test above
  cannot. The existing `FixedStance` fake in
  `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionUsabilityEvaluatorTests.cs:192` is the shape to reuse —
  do not write a second fake.
- ❌ Never assert how many policies exist, or how many call sites there are.

**`gk-core/tests/FusionRpg.Core.Tests/Battle/Board/SiegeTuningContractTests.cs` (new — **landed**, CAI3.1)**

- ✅ `A_siege_tuning_file_without_the_two_removed_keys_parses` — the whole point of the commit, and the
  **supersession** of module 2's `Siege_v2_still_carries_the_two_dead_keys`, which is deleted here
  (§The shape, "One consequence to carry out").
- ✅ `A_siege_tuning_file_that_still_carries_them_parses_too` — removal is a *reader* deletion; an
  unknown extra key must be ignored, not rejected, or every host holding an older file breaks on
  upgrade. (`SiegeTuning.Parse` reads named keys and never enumerates, so this holds today; the test
  pins it.)
- ✅ `Ai_tuning_names_exactly_the_two_siege_geometry_values` — assert the `AiTuning` member **names**
  are exactly `ObjectiveReferenceDistanceCells` and `ThreatRadiusCells`. A declaration, so pinning it
  is correct, and the reason is stated in the test: *after module 2 every scoring number lives in
  `combat-ai.v1.json`, so anything left on this record is siege board geometry — and a field nobody
  reads is what this module deleted.*
- ❌ Never assert a weight's value, or the number of keys in the file.

**Unchanged suites that must stay green, untouched:**
`gk-core/tests/FusionRpg.Core.Tests/Actions/DefenceActionStanceTests.cs` and `DefenceActionStanceSlotTests.cs`
(they construct `StanceRuntime` directly and never went through a production seam — this module does
not change what they prove), `AuraRuntimeTests.Does_not_implement_IStanceCheck_the_anti_StanceHeld_regression`
(`:111-117`), and every `SiegeAi*` test.

### Golden impact: **byte-identical. If a golden moves, this module is wrong.**

Argued from the two hash inputs, not asserted from a feeling:

- `BattleGoldenTests`' four hashes embed `BattleReport`, which embeds `RulesetVersion`
  (`gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:74-77`;
  `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:284,691`). **This module does not bump
  `RulesetVersion`** — it changes no resolution and no magnitude.
- The stance seam's default is the same singleton instance the three sites pass today, so gate 0's
  behaviour is reference-identical (`IAffordabilityCheck.cs:37-38`).
- The two deleted keys have no reader, so no decision, no magnitude and no serialized field depends on
  them. `AiTuning` is not serialized into any report: `BattleReport`/`BattleActorResult` carry no
  tuning (`BattleModels.cs:598-620`), and the siege resolver passes `aiTuning:` as a live argument
  (`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:225`).
- Siege's own tests assert contract and determinism, not pinned outcomes
  (`gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs:111-150` — two sides, a
  version stamp, survivor counts bounded by the roster, and the same seed ten thousand times), so
  there is no siege outcome hash for this to move either.

## Boundaries

**Always:** keep `NoStanceHeld.Instance` the default, so absence is today's behaviour; publish
`v{n+1}` through the tool; land the publish and the parser deletion in one commit (H7); state in the
commit body that the criterion was answered *no* and which of the three outcomes each change is.

**Ask first:** constructing a real `StanceRuntime` in production (that is A8's trigger, not this
module's); removing the `Siege.Stance` enum itself; any change to `UsabilityEvaluator`'s gate order.

**Never:** delete `StanceRuntime`, `PoiseLedger` or `Riposte` — another program's shipped modules, and
the `UsabilityReason.StanceHeld` vocabulary has a live regression guard
(`AuraRuntimeTests.cs:111-117`). Never migrate `stanceDefault`/`autoResolveHandicapMilli` into
`combat-ai.v1.json` as dead config (the ideal §8 row forbids exactly this). Never hand-edit
`gk-core/data/tuning/siege.v1.json`. Never add a second `IStanceCheck` supplier beside `BattleRunState.Stance`
— that is the three-copies defect this module exists to remove. Never reintroduce
`autoResolveHandicapMilli` under another name: a handicap is a difficulty lever and D2 rules it out of
AI.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility is it (§3), or a new one?** None — and that is the answer, not an evasion.
   Gate 0 is on the **deciding** side of `IIntentSource`, which
   [battle-engine-ssot.md](../battle-engine-ssot.md) §3c places outside the engine. This module moves
   no responsibility onto or off the closed register.
2. **Does it DECIDE or RESOLVE?** Decide. It changes *which stance object a policy consults*, never
   what the engine does with the resulting intent. No line of `BattleEngine.Resolve`'s round order
   changes.
3. **Mechanism or loop?** Mechanism — and that is precisely the defect: one mechanism ("is this actor
   mid-stance?") had three construction sites. After this module it has one
   (`BattleRunState.Stance`), which is what §2's *"exactly one implementation, shared by every mode"*
   requires.
4. **Which existing implementation does it extend?** `IStanceCheck` / `UsabilityEvaluator`'s gate 0
   (`UsabilityEvaluator.cs:52-55`) and `BattleRunState`'s existing `Cooldowns`/`CostLedger` seam
   pattern. Nothing is copied; one literal becomes one property.
5. **Does every mode get it?** Yes, by construction — battle, expedition, delve and siege all reach
   gate 0 through `UsabilityEvaluator`, and all three policy constructions now read the same property.
   The lawn does not construct these policies today; when `lawn-actor-view` (module 15) does, it
   inherits the same seam because it builds an `IBattleView` for the same evaluator.
6. **Deterministic and seeded?** Yes. No clock, no RNG, no ambient state; `NoStanceHeld.Check` is a
   constant `null`, and `StanceRuntime.Check` is a dictionary lookup over per-battle state that a
   replay rebuilds from tick 0 (the same discipline `RetargetLedger` follows —
   [combat-ai-ideal.md](../combat-ai-ideal.md) §3 principle 4).

## Success criteria

1. `BattleRunState` exposes exactly one `IStanceCheck`, and a source scan finds no
   `NoStanceHeld.Instance` literal in `gk-core/src/FusionRpg.Core/Battle/**` outside the declaration in
   `Actions/IAffordabilityCheck.cs`.
2. `data/tuning/siege.v{n+1}.json` exists, carries neither `ai.stanceDefault` nor
   `ai.autoResolveHandicapMilli`, and was produced by `gk-core/tools/tuning/publish.py` — not by hand.
3. `siege.v3.json` was produced by **one** `--remove-key ×2` invocation of module 2's verb — not by
   extending the tool here, and not by two publishes.
4. `AiTuning` has **two** members — `ObjectiveReferenceDistanceCells` and `ThreatRadiusCells`, the two
   siege geometry values module 2 left on it — and `SiegeTuning.Parse` reads exactly those and rejects
   neither an older file that still carries the two removed keys nor a newer one that does not.
5. `StanceRuntime.cs`, `PoiseLedger.cs` and `Riposte.cs` are unmodified, and
   `DefenceActionStanceTests` / `DefenceActionStanceSlotTests` / `AuraRuntimeTests` pass unchanged.
6. **Every golden and every existing test is byte-identical.** `RulesetVersion` stays 5. This is the
   module's whole proof — a moved golden means outcome 1 was implemented as a live `StanceRuntime`
   rather than as the seam.
7. The commit body states the criterion's answer ("no held action is a stance action today") and names
   which of the three outcomes each file change belongs to.

## Open questions

**None blocking.** Two cross-module notes, neither of which this spec decides:

1. **A8's raise/release content needs a field this spec does not add.** `ActionRow`
   (`ActionRow.cs:15-109`) cannot say "this action is a stance whose release is X", so
   [action/spec-defence-actions.md](../action/spec-defence-actions.md)'s decided shape (*"The release
   has its own `action_id`"*, §1) is unreachable from data today. That is the **action** program's
   field to add, on its own reviewed change; `combat-ai` records it here as the trigger that flips
   `BattleRunState.Stance` to a real `StanceRuntime`. Recommended default when A8 takes it up: a
   nullable `string? StanceReleaseActionId` on `ActionRow` (absent = not a stance), because gate 0 is
   already an ordinal id comparison (`StanceRuntime.cs:102`) and A8's own §1 chose a distinct id for
   exactly that reason.
2. **`spec-siege-ai.md` should lose its `stanceDefault` reference in the same wave.** Deleting the key
   leaves that spec naming a tuning row that no longer exists. Owner of the edit: the **base-defense**
   program. Recommended default: a one-line status note — *posture is deferred; its key lands with its
   reader* — rather than a rewrite.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches. (Battle engine / AI seam; siege tuning; action A8's
    defence module, which this deliberately does not touch.)
[~] I established and recorded this session's boundary. The session record
    tasks/sessions/backlog-clean-up-20260920.json exists and this lane writes only the three spec
    files named in its prompt. I did NOT run session-boundary-check.py -- the lane brief forbids
    running scripts that mutate or build; the gap is named here rather than hidden.
[x] I read every doc in the §1 row(s) for those subsystems, this session: combat-ai-map.md,
    combat-ai-ideal.md, research/combat-ai/{AUDIT,S2,S3}.md, battle-engine-ssot.md §2/§3c/§5,
    action/spec-defence-actions.md, DESIGN-GATE.md §5, CLAUDE.md, AGENTS.md.
[x] I checked decisions.md for a lock covering this. The "Action selection (battle adoption)" row
    locks the intent-source seam and the next RulesetVersion bump trigger; this module bumps nothing.
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope <this file> --summary` run this session:
    0 HIGH findings. The remaining D1 rows are the files this spec marks "(new; does not exist
    yet)", which the audit exempts because the line says so.
[x] I verified claims against CODE, not comments. Two doc/comment drifts found and reported:
    (a) AUDIT.md C3 cites `SiegeTuning.cs:435` for the StanceDefault PARSE; :435 is the AiTuning
    construction argument, the parse is at :351-357. (b) `BattleModels.cs:84-90` still says
    EquippedActionIds is "purely carried data: nothing in BattleEngine's round loop reads it today",
    which BattleRunState.cs:582 contradicts -- reported to module 12's spec, which owns that file.
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. The byte-identity claim is argued from the
    two hash inputs (RulesetVersion in the hashed payload; the stance default being the same
    singleton) and from reading the siege tests' assertions -- NOT from a run. The lane brief bars
    running tests. The build task must run them before claiming the identity.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated to prose, Structure, Testing, Boundaries within this spec.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal (AiTuning's member set) is a closed vocabulary the code owns, and
    the test states why.
[x] No event-refreshed cache is introduced or touched.
[x] No acceptance criterion fixes an ordering that can vary in real play. The module-2/module-4
    ordering is explicitly handled in both directions (§The shape).
[x] Produces/consumes no actor combat or derived magnitude: it moves no number. No second compose,
    no private fold.
[x] Does not invent or extend a SOLID-violating parallel path. It REMOVES one (three copies of one
    stance decision) and refuses to add a second IStanceCheck supplier.
[~] A new rule has a registry row. The "one stance seam" rule is enforced by the source-scan test
    named in §Testing strategy rather than by a shell guard; whether
    gk-core/scripts/enforcement-registry.v1.json needs a row for a test-enforced rule is the build task's
    call, and it is named here rather than assumed.
```

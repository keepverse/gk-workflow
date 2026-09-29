# Spec: `delve-automated-wiring` (combat-ai module 13)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `ai-tiers-personality` (module 3 — the tier a delve actor runs at), `intent-router`
(module 4 — the router this module hands delve's steering inputs to), `replay-identity` (module 8 —
without a pinned profile a resumed delve replays a fight the policy no longer plays) ·
**Unblocks:** `auto-policy-switch` (14) only in the sense that both must not move goldens at once ·
**Status:** **part built** (CAI3.4, 2026-09-20/21). The vocabulary and the policy landed: `IBattleView.DownedAllyKeysOf` (default empty; the real read in `BattleRunState`, forwarded by the three view decorators) and `DelveBattle.RoleOf` with its six tests. Two battle-integration tests remain, and they are a decision about how a test reaches a live view (`CAI3.4`); the consumer is `CAI3.5`'s `RpgHub.Resume`, still open.

## Objective

The delve is the one place in the repo where the AI gap is a **`throw`**.
`gk-core/src/FusionRpg.Server/RpgHub.cs:251-260` refuses `Resume` outright:

> *"RpgHub.Resume needs a real siege-ai-class automated `IIntentSource` for the raid's un-steered
> actors and every wave enemy — none exists in production yet … `StubIntentSource` is explicitly barred
> from standing in for it."*

Everything else on that path is real and tested. `RaidIntentSource` dispatches on a precomputed
steered-key set (`src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs:42-43,49-50`).
`DelveBattleSessionManager.Resume` builds a genuine new session from the persisted
`(setup_json, seed, decisions_json)` row (`gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs:267-321`)
and is directly tested against a *supplied* automated policy. `DelveBattleSession.Start` composes
`InteractiveIntentSource.ResumeReplayThenLive(_automated, Ask, EnvelopeOf, Trace, OnRecorded)` and wraps
it in a `RaidIntentSource` (`gk-core/src/FusionRpg.Server/DelveBattleSession.cs:182-184`).
`Steer` and `Declare` are live (`RpgHub.cs:214-235`). The delve profile row is built and pinned
(`gk-core/src/FusionRpg.Core/Battle/Timeline/BattleModeProfile.cs:295-300`).

**The premise behind the throw is false, and the ideal says so:** *"**False premise:**
`SiegeAiIntentSource` exists with generic dependencies (`SiegeAiIntentSource.cs:83-85`)"*
([combat-ai-ideal.md](../combat-ai-ideal.md) §4.2). What was genuinely missing is a policy that is not
siege-shaped — one that does not need an objective, a 2-D board, or a cover model — and that is exactly
what `core-scorer` + `profile-schema` + `ai-tiers-personality` produce.

This module supplies the delve's half: **`RpgHub.Resume` stops throwing and hands the session the
router and the core policy**, the delve's profile rows are named (`delve/frontliner`, `delve/support`,
`delve/striker`, `delve/enemy`), and the `ally-downed` selector gets the one view read it needs to see
a downed party member at all.

Two things it deliberately does **not** do:

- **It does not build `StartSession`'s content caller.** `DelveBattleSessionManager.StartSession`
  (`:191`) has zero production callers — nothing yet decides *"a party arrived at a fight room."* That
  is party-dungeon's D2.16/D5.11 content wiring ([research/combat-ai/S2-delve.md](../../research/combat-ai/S2-delve.md)),
  named here as a **dependency**, specified elsewhere. `StartSession`'s signature already takes
  `IIntentSource automated` (`:191-196`), so the day that caller exists it consumes this module's
  factory with no further work here.
- **It does not touch the freeze contract.** Switching a player away from a party cancels and discards
  that fight; it never finishes on autopilot. That is a structural guarantee via an uncaught
  `OperationCanceledException`, not a policy choice (§"The freeze contract" below), and this module's
  whole risk is accidentally breaking it.

## Tech stack

`FusionRpg.Core` (the delve profile rows' *consumption*; one `IBattleView` member for downed party
members), `FusionRpg.Server` (`RpgHub.Resume`, one composition-root factory beside
`DelveBattleSessionManager`), `gk-core/data/tuning/combat-ai.v1.json` (rows only — the file and its parser are
`profile-schema`'s, module 2). No new dependency, no schema change, no new endpoint.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve|FullyQualifiedName~RaidIntent|FullyQualifiedName~NoCatchInLiveBattleCallStack"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Golden|FullyQualifiedName~Expedition"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Delve"
dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~Delve"

.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Server/RpgHub.cs',
  'gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs',
  'src/FusionRpg.Server/DelveAutomatedPolicy.cs',
  'gk-core/src/FusionRpg.Core/Actions/IBattleView.cs',
  'gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs',
  'gk-core/src/FusionRpg.Core/Delve/Battle/DelveBattle.cs',
  'gk-core/data/tuning/combat-ai.v1.json'
) -Session backlog-clean-up-20260920

python gk-core/tools/tuning/publish.py combat-ai --add-key profiles.delve/frontliner=... --label "delve role rows"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
```

## Project structure

| File | New/changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Server/RpgHub.cs` | changed | `Resume` (`:251-260`) stops throwing: resolve the player id, build the policy inputs, call `_delveBattles.Resume(...)`, push the update. |
| `src/FusionRpg.Server/DelveAutomatedPolicy.cs` | **new; does not exist yet** | The one composition root that turns `(store, matchKey, partyIndex, setup)` into the steering inputs `Resume` and (later) `StartSession` both pass. |
| `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs` | changed | `Resume`/`StartSession` take the steering inputs instead of a pre-built `IIntentSource automated` (§"Why the policy cannot be built outside"). |
| `gk-core/src/FusionRpg.Server/DelveBattleSession.cs` | changed | `Start` (`:182-184`) stops building `RaidIntentSource` itself and passes steering inputs through `DelveBattle.Run`. |
| `gk-core/src/FusionRpg.Core/Delve/Battle/DelveBattle.cs` | changed | `Run` gains the same steering parameters and threads them into `BattleEngine.Resolve`, dropping the explicit `intentSource:` for the automated path. |
| `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | changed | Compose the router where the view exists, beside the existing `aiTuning`-triggered `DefaultAiIntentSource` construction (`:622-631`). **The seam itself is module 4's to declare** — this spec states delve's requirement and the recommended shape. |
| `gk-core/src/FusionRpg.Core/Actions/IBattleView.cs` | changed | One member: `DownedAllyKeysOf(actorKey)` — without it `ally-downed` is inert (§"ally-downed"). |
| `src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs` | deleted by module 4 | Replaced by the router. Listed so its row in the no-catch guard's file list moves rather than disappears. |
| `gk-core/data/tuning/combat-ai.v1.json` | changed (module 2 creates it) | Four `delve/*` profile rows. |
| `gk-core/tests/FusionRpg.Core.Tests/Battle/Timeline/NoCatchInLiveBattleCallStackTests.cs` | changed | The router and core-policy files join `CallStackFiles` (`:53-88`). |
| `tests/FusionRpg.Server.Tests/Delve/DelveAutomatedWiringTests.cs` | **new; does not exist yet** | `Resume` no longer throws; the freeze contract still holds. |
| `gk-core/tests/FusionRpg.Core.Tests/Delve/Battle/DelveRolePolicyTests.cs` | **new — landed (CAI3.4)** | Role derivation + `ally-downed` contract. |

## The shape

### 1. Why the policy cannot be built outside the engine — and what delve passes instead

`RaidIntentSource`'s own doc comment states the constraint, and it is the single most important fact in
this module:

> *"`BattleEngine.Resolve` builds its `IBattleView` internally, AFTER it is called — no external caller
> of `Resolve` (this class's whole reason to exist) ever holds one to construct this class with."*
> — was src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs's own doc comment; the class was deleted
> 2026-09-20 (combat-ai `intent-router`, CAI1.10) and the SAME correction now lives in
> `Actions/IntentRouter.cs`'s own doc comment

That is why `RaidIntentSource` (now `IntentRouter`) dispatches on a precomputed **key set** and takes both sources as
already-built objects: a key-set lookup needs no view. A **scored** policy does. `BattleRunState`
*is* the `IBattleView` (`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:40`
`sealed class BattleRunState : IBattleView`), and it is a **private nested class inside
`BattleEngine`** (`BattleRunState.cs:32,40`) — deliberately, to keep its members private
(`BattleRunState.cs:20-31` records the reasoning). So no Server-side factory can ever be handed one.

The shipped answer already exists for siege: `Resolve`'s `aiTuning:` parameter is an **opt-in flag**,
and the run state builds the policy itself, where the view, `Cooldowns`, `CostLedger` and the stance
seam all are (`BattleRunState.cs:672-699`, whose comment says *"built AFTER Cooldowns/CostLedger exist
… using `this` as the live `IBattleView`"*).

**So the delve passes *steering inputs*, not a built policy:**

```csharp
// BattleEngine.Resolve -- trailing optionals, the same additive pattern as aiTuning/board/roundOf.
// DECLARED BY intent-router (module 4), which already places router construction at
// BattleRunState.cs:743-757; this module states delve's requirement and uses it.
IReadOnlySet<string>? steeredKeys = null,
Func<IIntentSource, IIntentSource>? steeredSourceFor = null,
string? aiProfileId = null,
AiActorClassOf? actorClassOf = null      // module 3's delegate; null => every actor is Unique
```

The fourth one closes **module 3's Open question 1** for this place: that spec's recommended default is
*"each wiring module supplies it as part of its own commit"*
([spec-ai-tiers-personality.md](spec-ai-tiers-personality.md) §Open questions 1), and the delve's
supplier is `DelveAutomatedPolicy` (§3) — *"does this actor key map to a row with an instance id"*,
answered on the Server's own side of the DAL boundary. Passing `null` keeps module 3's stated
byte-identity default (`Unique` → `smart`), which is what every non-delve `Resolve` call does.

and `BattleRunState` composes, in the one place the view exists. **Both types below are declared
elsewhere and are used here exactly as their owning specs declare them** — this module invents no
signature:

```csharp
// beside the existing aiTuning arm at BattleRunState.cs:743-757
if (aiProfileId is { } profileId)
{
    // CoreIntentPolicy.Create -- ai-tiers-personality (module 3) §6 declares this factory.
    var automated = CoreIntentPolicy.Create(
        view: this, cooldowns: Cooldowns, stance: Stance, affordability: CostLedger,
        profileId: profileId, actorClassOf: actorClassOf,
        matchSeed: RunSeed,                     // the run state already holds it; no new parameter
        retarget: new RetargetLedger(), trace: trace);

    // IntentRouter.Compose -- intent-router (module 4) §1a declares this factory, including the
    // `steeredSourceFor` FACTORY parameter this module's §Open questions asked for, and the meaning
    // of a null `fallback`. Named arguments, because `policy` comes first, not `steered`.
    DefaultAiIntentSource = IntentRouter.Compose(
        policy: automated,
        fallback: new StubIntentSource(this, Cooldowns, Stance, CostLedger),
        steeredSourceFor: steeredSourceFor,
        steeredKeys: steeredKeys);
}
```

**`steeredSourceFor` is a factory, not a second source, and it has to be one.**
`InteractiveIntentSource` takes the automated policy as its **timeout fallback** and *records* the
fallback's choice into the trace as `DecisionSource.Timeout`
(`gk-core/src/FusionRpg.Core/Battle/Timeline/InteractiveIntentSource.cs:139-146`). So the player source cannot
be built before the automated one exists. Inverting the wrap (router falls through to the policy when
the interactive source returns `None`) would skip that `Record` call and silently break replay of an
AFK turn. `Compose` invokes the factory once, with the automated policy, and hands the result to the
router's constructor as a built `steered` — the inversion lives in one place, inside module 4, and
module 4's `IntentRouterTests` asserts it
(`Compose_invokes_steeredSourceFor_exactly_once_with_the_policy_it_was_given`).

The `fallback` above is today's literal from `BasicAttack.cs:175-180`, passed explicitly because the
delve is a turn-based place with a stub underneath. A null `fallback` means *no step 4* rather than
*invent a stub* — module 4 §1a states that, and it is the lawn's case, not the delve's.

`DelveBattle.Run` then **stops passing `intentSource:`** for the automated path, so
`BasicAttack.cs:175-180`'s chain (`intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)`)
picks the router — and `TimelineDispatch.Reselect` (`gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs:79-80`),
which today omits `DefaultAiIntentSource` entirely, gets its fix from module 4 in the same place rather
than needing a delve-specific one.

### 2. `RpgHub.Resume`, after

```csharp
/// <summary>Reconnect after a freeze — replays the recorded prefix, then goes live (spec §4b).
/// The "no real siege-ai-class policy exists" premise that made this throw was retired by combat-ai:
/// the automated side is the core policy under the delve profile rows, composed inside the engine
/// where the view exists (spec-delve-automated-wiring.md §1).</summary>
public async Task Resume(string matchKey)
{
    if (!_playerConnections.TryGet(Context.ConnectionId, out var playerId))
        playerId = _store.GetCurrentPlayerId();

    var session = _delveBattles.Resume(
        matchKey, playerId,
        policy: DelveAutomatedPolicy.For(_store),        // the steering inputs, not a built source
        connectionId: Context.ConnectionId);
    if (session is null) return;                          // no row, already ingested, or no trace -- Resume's own refusals
    await NotifyDelveUpdatedAsync(session.DelveId);
}
```

`Resume` already returns `null` rather than throwing for every legitimate refusal — no log row, a row
already ingested (`entry.RunId is not null`), or an absent/incomplete trace
(`DelveBattleSessionManager.cs:271-295`, whose comment cites *"spec §9: an absent/incomplete trace
refuses, never re-resolves blind"*). This module adds no new refusal and removes no existing one; it
removes only the unconditional `NotImplementedException`.

**Player id.** `_playerConnections.TryGet(connectionId, out playerId)`
(`gk-core/src/FusionRpg.Server/PlayerConnectionRegistry.cs:25`) is the primary read, because a connection that
reached `Resume` has normally called `JoinPlayer` (`RpgHub.cs:43-52`). `GetCurrentPlayerId()` is the
same fallback `DelveEndpoints` already uses (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:37`). The id is
only used to look up *that player's* web-match log row, so a wrong id refuses (returns `null`) rather
than resuming someone else's fight.

### 3. `DelveAutomatedPolicy` — one composition root, two future callers

```csharp
// src/FusionRpg.Server/DelveAutomatedPolicy.cs (new; does not exist yet)
/// <summary>The one place the delve's automated side is configured. Resume uses it today;
/// StartSession's content caller (party-dungeon D2.16/D5.11, not this module) uses the same call the
/// day it exists -- so there is never a second answer to "what does the un-steered side run".</summary>
public static DelvePolicyInputs For(RpgStore store) => new(
    AiProfileId: CombatAiProfiles.DelveId,                 // module 2's closed profile-id vocabulary
    ActionCatalog: store.BuildActionCatalog(RungPolicy.Table),
    Effects: ActionContainerEffectResolverFactory.Build(store));
```

`DelveBattleSessionManager.Resume`/`StartSession` already take `actionCatalog` and `containerResolver`
as optional parameters and already pass them into `DelveBattleSession`
(`DelveBattleSessionManager.cs:192-194,267-269`, `:236-240`); this bundles them with the profile id so
the three always travel together, for the same reason
[spec-siege-loadout-wiring.md](spec-siege-loadout-wiring.md) §1 bundles siege's: ids with no catalog
degrade to the basic attack with a warning (`BattleRunState.cs:637-681`), which is a policy that looks
wired and is not.

### 4. The delve profile rows

Four rows in `gk-core/data/tuning/combat-ai.v1.json`, under the schema `profile-schema` (module 2) owns.
Keyed **place × role** per owner ruling D5. Values are seeds, principle-derived, marked `UNMEASURED`.

| Row | Who | Ranked rows (rank, selector, condition, action filter) | Why |
|---|---|---|---|
| `delve/frontliner` | party members whose held actions skew `Defensive`/`Construct` | 1 `ally-downed` + tag `Heal` · 2 `highest-threat` + tag `Defensive` · 3 `nearest` + tag `Offensive` | A frontliner's job is to be the thing worth hitting; it picks up a downed ally first because it is nearest to one. |
| `delve/support` | skew `Heal`/`Buff`/`Debuff` | 1 `ally-downed` + tag `Heal` · 2 `ally-lowest-hp` + tag `Heal`/`Buff` · 3 `lowest-hp` + tag `Debuff` · 4 `nearest` + tag `Offensive` | Reserve floor highest of the four rows: a support that runs dry is a support that stopped existing. |
| `delve/striker` | skew `Offensive` | 1 `lowest-hp` + tag `Offensive` (kill-weighted) · 2 `highest-threat` + tag `Offensive` · 3 `nearest` | Finishing a target removes its whole future output; this is where the kill weight earns its 15. |
| `delve/enemy` | every wave actor (`PartyIndex is null`) | 1 `lowest-hp` + tag `Offensive` · 2 `nearest` | Symmetric with `delve/striker` by D2 (*"the same for all"*) — an enemy is not a worse AI, it is an actor with a simpler kit. Its simplicity is its **kit's**, not a difficulty dial. |

**How an actor gets a role, using only facts that exist.** There is no combat-role field anywhere:
`BattleActorSetup` carries `Key`/`Side`/`SpeciesId`/`TypeId`/`Level`/elements/traits/HP/atk/defense/
interval/`PartyIndex`/`Kind` (`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:7-176`, the record's whole
span; `PartyIndex` itself is the property at `:176`), and the only
`RoleId` vocabulary in the repo is *equipment slots*
(`gk-core/src/FusionRpg.Core/ActorSurface/ActorSheetSurfaceCatalog.cs:27-29`,
`gk-core/data/tuning/actor-sheet.v1.json:66-129` — `armament-primary`, `core-guard`, …). Inventing a second
`role` vocabulary in seed data would be the third-vocabulary defect `ActionEnums.cs:20-24` names.

So **role is derived, once at setup, from the actor's own held actions**, over the closed nine-member
`ActionTag` enum (`gk-core/src/FusionRpg.Core/Actions/ActionEnums.cs:47-58`) that `CompiledAction` already
carries (`gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs:35`):

```text
counts = tally of held actions by ActionTag, excluding the hand-built basic attack
support    if Heal + Buff + Debuff  is the largest bucket
frontliner if Defensive + Construct is the largest bucket
striker    otherwise                          (Offensive, Movement, Summon, Utility, and the default)
ties       break in the order support > frontliner > striker, stated, so it is deterministic
```

- An actor with **no** loadout (every actor holding only `BasicAttackCompiled` —
  `BattleRunState.cs:637-681`) is a `striker`, which is exactly today's behaviour expressed as a role.
- `PartyIndex is null` is `delve/enemy` before any tally runs
  (`BattleModels.cs:176`; the delve profile's `DownedOnDeplete` branch keys on the same field,
  `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:699`).
- Derivation is **not** a tunable and not seed data: it is a pure function of a closed enum, so it is a
  reviewed code change like any vocabulary mapping.

### 5. `ally-downed` needs a view read, or it is inert

**The selector cannot see its targets today.** Under the delve profile, an actor at HP ≤ 0 with a
`PartyIndex` transitions to `TurnState.Downed` and is *not* cleaned up — its statuses and shields stay,
because it is *"still present, targetable, and revivable"* (`BattleEngine.cs:689-694`). But it is also
not `Alive` (`BattleEngine.cs:99` `Alive => Hp > 0`), therefore not `Active`
(`:88 Active => Alive && !Retreated`), therefore **absent from `LiveActorKeys`**
(`BattleRunState.cs:939`, which filters on `a.Active`). `IBattleView` exposes no other roster read.

So `ally-downed` gets one member, following the absence convention every other per-actor read on that
interface already uses:

```csharp
/// <summary>combat-ai delve-automated-wiring: the actor's own side's DOWNED members -- present,
/// targetable and revivable under a DownedOnDeplete profile (BattleEngine.cs:689-694), and
/// deliberately absent from LiveActorKeys, which lists only Active actors (BattleRunState.cs:939).
/// Empty for every profile without DownedOnDeplete, which is every profile but `delve`
/// (BattleModeProfile.cs:295-300) -- so this is byte-identical to today everywhere else. Self-side
/// only: who on YOUR side is down is not fog-gated, the same reasoning
/// GarrisonedStructureKeyOf/ObjectivePositionOf already established on this interface.</summary>
IReadOnlyList<string> DownedAllyKeysOf(string actorKey);
```

Three existing implementors move: `BattleRunState` (real), `FoggedBattleView` (forwards — self-side is
not fog-gated), and the private `BloodthirstyView` (`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs:607-633`,
forwards), plus the test fakes.

**And its consumer does not exist yet — say so rather than imply otherwise.** A revive today is a
**supply**, not an action: `ConsumableClass.Revive` fires `resource.delta` gated on `memberDowned`
(`gk-core/src/FusionRpg.Core/Delve/Supplies/SupplyUse.cs:48-53`, whose own comment sits just above at `:39`,
`gk-core/src/FusionRpg.Core/Delve/Supplies/SupplyClassMap.cs:26`), and its own comment calls it *"the one legal
Downed → Charging trigger OUTSIDE a corpus action"*. Nothing in `EquippedActionIds` can revive, so a
`delve/frontliner` scoring rank 1 will find a target and no usable action, and fall through to rank 2 —
correct behaviour, and worth zero until a revive-class corpus action exists. Shipping the vocabulary
and the read ahead of the consumer is this repo's stated pattern, not an oversight:
`EmplacementFireMode` (`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:34-45`) and `AggressionOf`
(`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs`, *"a wiring seam for content that does not exist yet …
not a promise of a non-default value today"*) are both it.

### 6. The freeze contract — unchanged, and actively defended

Steering away from a party **freezes** its fight: cancel-and-discard, never finish-on-autopilot. The
mechanism is an `OperationCanceledException` raised inside `Ask` and left **uncaught** all the way out
through `InteractiveIntentSource.TryDeclare` and `BattleEngine.Resolve`'s synchronous loop, so the
`Task` lands `Canceled` rather than `RanToCompletion`
(`gk-core/src/FusionRpg.Server/DelveBattleSession.cs:185-206,226-239`). `Resume` is always a *new* session
replaying the persisted trace, never a reattachment (`DelveBattleSessionManager.cs:259-266`).

**This module's single largest risk is putting a `catch` on that path**, and the repo already has the
compile-time guard: `gk-core/tests/FusionRpg.Core.Tests/Battle/Timeline/NoCatchInLiveBattleCallStackTests.cs`
holds an explicit closed file list (`:53-88`) with the discipline *"Adding a new file to this chain …
means adding a row here too."*

**So the router and the core policy join that list, and this module must also repair a pre-existing
hole in it:** `Actions/StubIntentSource.cs` and `Battle/Siege/SiegeAiIntentSource.cs` are **not** in
`CallStackFiles` today, despite both being reachable from `Resolve` via `BasicAttack.cs:175-180`. Each
candidate file is read for an existing `catch` before it is added (the guard is a line-based
heuristic, and a config-loading `catch (JsonException)` in a newly-added file would fail it for the
wrong reason — the list's own doc comment at `:16-32` explains exactly this trap).

## Tunables

Rows only. The file, its schema, its parser and its host injection are `profile-schema`'s (module 2);
this module authors four rows in it and nothing else.

| Key | File | Unit | v1 seed | Why |
|---|---|---|---|---|
| `profiles.delve/frontliner.rows[]`, `.delve/support.rows[]`, `.delve/striker.rows[]`, `.delve/enemy.rows[]` | `gk-core/data/tuning/combat-ai.v1.json` | ranked rows (rank, selector, conditions, action filter) | §4's table | Selector and condition **vocabularies** are closed and live in code; the rows are data. |
| `profiles.delve/*.weights.*` | same | integer per-mille | siege's shipped weights (`gk-core/data/tuning/siege.v1.json:103-109` — hitChance 70, objective **0**, kill 15, lowHp 10, cannotCounter 10, round 1, risk 120) | The ideal names siege's weights as the seed set. `objective` seeds **0** for delve: a delve room has no Core to breach, and `ObjectivePositionOf` returns `null` for a battle with no siege context (`IBattleView`'s own doc). A weight over an always-absent term is noise. |
| `profiles.delve/support.reserveFloorMilli` | same | per-mille of pool max | 300 `UNMEASURED` | The prior art's hoarding fix is a reserve threshold, not a ban ([combat-ai-ideal.md](../combat-ai-ideal.md) §5). Support highest because its late-fight action is worth most. |
| `profiles.delve/{frontliner,striker,enemy}.reserveFloorMilli` | same | per-mille | 150 / 100 / 100 `UNMEASURED` | Above zero so a finisher stays affordable; low enough not to read as hoarding. |
| `profiles.delve/*.tier` | same | closed tier vocabulary | by actor class, **not** by row: unique → `smart`, general → `performance` (module 3) | D6/D2: a tier is actor class, never difficulty. A delve enemy is not given a worse tier because it is an enemy. |

**No lawn keys** (`N`/`T`/`L`, budget, token pool): the delve is turn-based with a dwell window, so the
trigger is the engine's per-turn pull ([combat-ai-ideal.md](../combat-ai-ideal.md) §6.2). Stating this
keeps the delve rows out of the real-time section of the schema.

## Code style

- **A delegate seam rather than a leaked type**: `steeredSourceFor` is `Func<IIntentSource, IIntentSource>`
  for the same reason `HubInputsFor` is a `Func<>` — the caller owns the construction, the engine owns
  the moment.
- **A trailing, defaulted, null-is-today parameter** for every addition to `Resolve` and `DelveBattle.Run`,
  matching `aiTuning`/`board`/`roundOf`/`containerResolver` (`BattleEngine.cs:184-233`).
- **No `catch` anywhere on the live call stack**, and the new files say so in their own doc comment, so
  the guard's list and the code agree without a reader having to check.
- **The absence convention is `null`/empty, never a sentinel actor key** — `IBattleView`'s own repeated
  rule.
- **Role derivation is a `switch` over a closed enum**, with the tie-break order written down in the
  method, not implied by dictionary order.

## Testing strategy

**`tests/FusionRpg.Server.Tests/Delve/DelveAutomatedWiringTests.cs` (new; does not exist yet)**

- ✅ `Resume_no_longer_throws_and_returns_a_live_session` — the module's headline. The
  `NotImplementedException` at `RpgHub.cs:253-259` is gone.
- ✅ `Resume_still_refuses_an_absent_or_incomplete_trace` and
  `Resume_still_refuses_an_already_ingested_run` — the two refusals that must survive
  (`DelveBattleSessionManager.cs:271-295`). Losing them would turn "refuses, never re-resolves blind"
  into a silent re-resolve.
- ✅ `Steering_away_still_cancels_the_task_rather_than_completing_it` — asserts
  `RunTask.Status == TaskStatus.Canceled`, never `RanToCompletion`. This is the freeze contract, and it
  is the assertion that catches a `catch` the guard's heuristic misses.
- ✅ `A_steered_actor_that_declares_nothing_is_never_handed_to_the_automated_policy` — the guarantee
  `RaidIntentSourceTests.cs` proved before CAI1.10 deleted both the class and its test file, ported
  test-for-test into `Actions/IntentRouterTests.cs`'s own
  `A_steered_actor_that_declares_nothing_is_never_handed_to_the_policy`, so the replacement did not
  quietly lose it.
- ✅ `A_timeout_on_a_steered_actor_is_recorded_as_a_timeout_decision` — proves the decorator wrap in §1
  kept `InteractiveIntentSource.cs:139-146`'s `Record` call, which replay depends on.

**`gk-core/tests/FusionRpg.Core.Tests/Delve/Battle/DelveRolePolicyTests.cs` (new — **landed**, CAI3.4)**

- ✅ `Role_is_derived_from_held_action_tags_and_ties_break_in_the_stated_order` — one case per branch
  plus the tie. Asserts against the closed `ActionTag` enum, never against a corpus action id.
- ✅ `An_actor_with_no_loadout_is_a_striker` — today's behaviour, named.
- ✅ `A_wave_actor_is_the_enemy_row_before_any_tally` — `PartyIndex is null` short-circuits.
- ✅ `Downed_party_members_are_absent_from_LiveActorKeys_and_present_in_DownedAllyKeysOf` — the §5
  finding, pinned, so a later change to `Active` cannot silently make `ally-downed` inert again.
- ✅ `DownedAllyKeysOf_is_empty_under_every_profile_without_DownedOnDeplete` — the byte-identity claim
  for battle, expedition and siege.
- ✅ `Ally_downed_falls_through_when_no_held_action_can_revive` — the honest state of §5's consumer gap,
  asserted rather than left as prose.
- ❌ Never assert how many profile rows the delve has, how many actions a role tallied, or any generated
  action name. Those are readings of a corpus that grows.

**`NoCatchInLiveBattleCallStackTests`** gains rows for the router, the core policy and the two
pre-existing omissions (`StubIntentSource.cs`, `SiegeAiIntentSource.cs`), and lost
Delve/Battle/RaidIntentSource.cs when module 4 deleted that file (CAI1.10, 2026-09-20).

### Golden impact: **byte-identical. If a golden moves, this module is wrong.**

- `RulesetVersion` stays 5 (`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:284`). This module changes no
  resolution rule and no magnitude. The **battle/expedition** default policy switch is module 14's
  single cause and its own bump — the two must not land together, which is map hard edge H1.
- `BattleGoldenTests`' four hashes (`gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:74-77`) and
  `ExpeditionResolverTests.Tier_goldens_are_locked` are `classic-round`/expedition fixtures. Every new
  `Resolve` parameter is a trailing optional defaulting to null, so those calls are unchanged, and
  `DownedAllyKeysOf` returns empty for any profile with `DownedOnDeplete: false` — which is every
  profile but `delve` (`BattleModeProfile.cs:295-300`).
- **No delve golden exists to move.** Delve fights had no production entry point at all
  (`RpgHub.Resume` threw; `StartSession` has no caller), so there is nothing pinned to re-bless. That
  absence is a risk, not a comfort, and §Success criteria 6 closes it with a fixed-seed delve fixture
  authored in the test, in the same shape [spec-siege-loadout-wiring.md](spec-siege-loadout-wiring.md)
  proposes for siege.

## Boundaries

**Always:** compose the router where the view exists; pass steering **inputs**, never a pre-built
scored policy, from the Server; keep every new `Resolve`/`Run` parameter trailing, optional and
null-is-today; keep `InteractiveIntentSource` wrapping the automated policy so a timeout is still
recorded; add every new live-call-stack file to `NoCatchInLiveBattleCallStackTests`; state
`UNMEASURED` on every seeded row.

**Ask first:** changing what `Resume` refuses; giving the delve a dwell-window change; a fifth delve
profile row; any `RulesetVersion` bump.

**Never:** `StubIntentSource` as the raid policy — [spec-delve-battle-profile.md](../party-dungeon/spec-delve-battle-profile.md)
§Boundaries makes this an explicit `Never`, and §3 names a real policy as a **consumed dependency**;
this module satisfies that dependency rather than reinterpreting it. Never `catch` anything on
`Resolve`'s live call stack. Never finish a switched-away fight on autopilot. Never resolve a delve
through `ProfileForExpedition`/`ProfileForWave` (the same spec's `Never`, and
`DelveBattleProfileGuardTests` is the source-scan that enforces it). Never build
`StartSession`'s content caller here. Never give the enemy side a different AI *quality* — D2 forbids
a difficulty lever in AI; a simpler enemy is a simpler **kit**.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility is it (§3), or a new one?** None — it is on the **deciding** side of
   `IIntentSource`, which [battle-engine-ssot.md](../battle-engine-ssot.md) §3c places outside the
   engine. The one engine-adjacent addition, `IBattleView.DownedAllyKeysOf`, is a *read* of state the
   engine already owns (responsibility 15, death/body state) and changes none of it.
2. **Does it DECIDE or RESOLVE?** Decide, entirely. `BattleEngine.Resolve`'s round order, damage,
   status, shields and the `Downed` transition are untouched; only who answers `TryDeclare` changes.
3. **Mechanism or loop?** The **loop** stays the delve's (a live SignalR session with a dwell window
   and a freeze). The **mechanism** — how a decision is gated, scored and selected — is the one core
   scorer under a data profile, shared with battle and siege. That split is §2's rule applied exactly:
   *"A mode may own its loop. A mode may never own a mechanism."*
4. **Which existing implementation does it extend?** `IIntentSource` (`IntentSource.cs:29-37`),
   `InteractiveIntentSource` (unchanged, still shared with web battle), `BattleRunState`'s existing
   `aiTuning`-triggered policy construction (`:622-631`), and `RaidIntentSource`'s steered-key-set
   dispatch, which the router absorbs. Nothing is copied.
5. **Does every mode get it?** Yes for the policy: it is the same core scorer battle, siege and the
   lawn run. The delve-specific parts are exactly two, and both are profile-gated rather than
   code-gated: the `DownedOnDeplete` read (empty elsewhere) and the four `delve/*` rows.
   `StartSession`'s content caller is the one remaining delve-only hole and it is named, owned by
   party-dungeon, and not specified here.
6. **Deterministic and seeded?** Yes, with one edge this module must respect. A delve fight is
   deterministic in `(setup, seed, human trace, profile version)` — **and the un-steered parties' and
   wave enemies' decisions are never recorded.** `DecisionTrace` holds only `Player`/`Timeout`
   (`Battle/Timeline/DecisionTrace.cs:5-20`), so the automated side is **re-derived** on every resume
   (`DelveBattleSessionManager.cs:296-310` replays the persisted prefix). A `combat-ai.v{n+1}` publish
   between the freeze and the resume would therefore replay a fight the policy no longer plays. **That
   is why this module depends on `replay-identity` (module 8)**: the match pins its profile at start,
   and `AppendWebMatchLog` already carries a `profile_id` column
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs:28-63`, `:206`) that the delve already stamps
   with `BattleModeProfileCatalog.DelveId` (`DelveBattleSessionManager.cs:205`) — module 8 extends what
   is stamped; this module must not resume without it. No clock, no unseeded RNG; personality offsets
   come from `SeededRng.DeriveStream` (module 3).

## Success criteria

1. `RpgHub.Resume` contains no `throw new NotImplementedException`, and a frozen delve fight resumes
   end-to-end through SignalR with un-steered parties and wave enemies acting.
2. `Resume`'s existing refusals (no row, already ingested, absent/incomplete trace) are unchanged, each
   asserted.
3. The freeze contract holds: steering away leaves `RunTask.Status == TaskStatus.Canceled`, and
   `NoCatchInLiveBattleCallStackTests` is green with the router, the core policy,
   `StubIntentSource.cs` and `SiegeAiIntentSource.cs` all on its list.
4. Four `delve/*` rows exist in `gk-core/data/tuning/combat-ai.v1.json`, published through
   `gk-core/tools/tuning/publish.py`, every seeded number marked `UNMEASURED`.
5. `IBattleView.DownedAllyKeysOf` returns the downed party members under the delve profile and **empty**
   under every other, asserted both ways.
6. A fixed-seed delve fixture is locked — the delve's first pinned outcome — authored in the test, not
   read from `gk-data/packs/fusion/data/seed/**`.
7. **Every existing golden and test is byte-identical.** `RulesetVersion` stays 5.
8. No production code path anywhere passes `StubIntentSource` as the raid policy.

## Open questions

**None blocking.** Three notes:

1. ~~**`steered` must be a factory, not a built source, for the delve.**~~ **RESOLVED in module 4.**
   [spec-intent-router.md](spec-intent-router.md) §1a now declares `IntentRouter.Compose`, whose
   `steeredSourceFor` parameter is `Func<IIntentSource, IIntentSource>?` and which invokes it **once**
   with the automated policy before constructing the router — so the inversion lives inside module 4,
   the constructor keeps its built `steered`, and `InteractiveIntentSource`'s `Record` call
   (`InteractiveIntentSource.cs:139-146`) is preserved. §1 above calls that factory verbatim, by named
   argument. Module 4 also states what a null `fallback` means; the delve passes one explicitly.
   Nothing about this is open in this module any more, and no signature here is this module's to
   invent.
2. **Cross-module (delve content / action corpus): `ally-downed` has no consumer.** A revive is a
   **supply** today, not an action (`SupplyUse.cs:39,48-53`), so no `EquippedActionIds` entry can revive a
   downed ally. The selector and the view read ship here as vocabulary; the revive-class corpus action
   is the delve/action programs' content. **Recommended default:** leave it as a rank-1 row that falls
   through, and do **not** special-case supplies into the AI — a supply is the player's verb, and
   routing it through `IIntentSource` would be a second decision path.
3. **Cross-module (party-dungeon D2.16/D5.11): `StartSession` still has no production caller.**
   `DelveBattleSessionManager.StartSession` (`:191`) is reachable only from tests. This module makes
   the *resume* path live; the *start* path needs the room→fight trigger party-dungeon owns.
   `StartSession` already takes the automated side as a parameter, so no further change here is needed
   when that caller lands — it calls `DelveAutomatedPolicy.For(store)` exactly as `Resume` does.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches. (Battle engine AI seam; the delve session/hub surface;
    IBattleView; combat-ai tuning rows.)
[~] I established and recorded this session's boundary. tasks/sessions/backlog-clean-up-20260920.json
    exists and this lane writes only the three spec files named in its prompt. I did NOT run
    session-boundary-check.py -- the lane brief bars running scripts; named rather than hidden.
[x] I read every doc in the §1 row(s) for those subsystems, this session: combat-ai-map.md,
    combat-ai-ideal.md, research/combat-ai/{AUDIT,S2,S3}.md, battle-engine-ssot.md §2/§3c/§5,
    party-dungeon/spec-delve-battle-profile.md, DESIGN-GATE.md §5, CLAUDE.md, AGENTS.md.
[x] I checked decisions.md for a lock covering this. The "Battle time model" row locks
    (setup, seed, decision-trace) determinism for live interactive sessions and the "refuse an
    incomplete trace" rule -- both preserved and asserted. The "Action selection (battle adoption)"
    row's next-bump trigger is module 14's, not this module's.
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope <this file> --summary` run this session:
    0 HIGH findings. The remaining D1 rows are the files this spec marks "(new; does not exist
    yet)", which the audit exempts because the line says so.
[x] I verified claims against CODE, not comments. The module's central finding -- that `ally-downed`
    cannot see a downed ally through the shipped view -- came from reading BattleEngine.cs:99-102 and
    BattleRunState.cs:939 against BattleEngine.cs:689-694, not from any doc.
[x] I read the surrounding section of every rule I quoted (including spec-delve-battle-profile.md's
    Boundaries table, which is where the "Never: StubIntentSource as the raid policy" line lives).
[~] I tested (not assumed) any constraint I am reporting. Byte-identity is argued from the trailing-
    optional parameter shape, from DownedOnDeplete being false on every non-delve profile, and from
    the golden fixtures' own setups -- NOT from a run. The lane brief bars running tests. The build
    task must run them.
[x] Nothing contradicts a §2 invariant. The loop stays the delve's; the mechanism is shared.
[x] Corrections propagated to prose, Structure, Testing, Boundaries within this spec.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. Testing strategy explicitly bans asserting row counts and corpus action ids; the one
    pinned fixture hashes a deterministic engine outcome from a test-authored catalog.
[x] No event-refreshed cache is introduced or touched. Role is derived once at setup from an
    already-compiled held-action list, not cached with invalidation triggers.
[x] No acceptance criterion fixes an ordering that can vary in real play. The role tie-break order is
    stated and asserted; the router's steered/automated split is a key-set lookup, order-free.
[x] Produces/consumes no actor combat or derived magnitude: it reads Hub output through
    IBattleView.DerivedOf like every other policy. No second compose, no private fold.
[x] Does not invent or extend a SOLID-violating parallel path. It removes one (RaidIntentSource and
    SiegeIntentSource collapsing into the router) and refuses a delve-local scorer.
[~] A new rule has a registry row. The "no catch on the live call stack" rule already has its
    enforcement (NoCatchInLiveBattleCallStackTests) and this module extends its list; whether
    gk-core/scripts/enforcement-registry.v1.json needs a row for the new IBattleView member's empty-elsewhere
    contract is the build task's call, named here rather than assumed.
```

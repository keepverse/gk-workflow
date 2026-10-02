# Spec: `siege-loadout-wiring` (combat-ai module 12)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `core-scorer` (module 1 — the scorer that will finally have more than one action to
choose between) · **Unblocks:** nothing structurally; it is the module that makes siege's shipped AI
worth having, and it is a prerequisite in spirit for `auto-policy-switch` (14) because a policy tested
only against basic attacks has not been tested ·
**Status:** **part built** (CAI3.3, 2026-09-20). `CompositeContainerEffectResolver` landed in `Actions/IContainerEffectResolver.cs` (first non-empty wins, ordinal, empty rather than null, 0 bytes per call, seven tests). The two production halves are out of fence: `CAI3.2`'s one-home equipped-action rule (Data + Server) and `CAI3.3`'s `DistrictAssaultResolver` composition.

## Objective

Siege ships a real scored AI — stance-free additive XCOM-shaped targeting, an objective fallback, a
frozen acting order, a decision trace
([research/combat-ai/S3-siege.md](../../research/combat-ai/S3-siege.md)) — and then hands it, for every
legion member in every real assault, **exactly one action to choose from: the hand-built basic attack.**

The cause is two lines that were never written.
`gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:415-460` builds each member's
`BattleActorSetup` with `Key`, `Side`, `SpeciesId`, `TypeId`, `Level`, elements, traits, HP, atk,
defense, attack interval, `AdditionalHeldActions`, `SpecimenId` and `HubInputs` — and **no
`EquippedActionIds`**. `BattleRunState`'s setup loop reads that null and falls back to
`new[] { BasicAttackCompiled }` (`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:637-681`). The one
loadout that does reach a siege actor is the hardcoded construction grant
(`DistrictAssaultResolver.cs:450`, attacker side only), added through the deliberately additive
`AdditionalHeldActions` sibling field (`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:101-118`) precisely
because the root cause was left unfixed. The `Resolve` call passes
`containerResolver: ConstructionActions.ContainerResolver`
(`DistrictAssaultResolver.cs:217`) — the four construction containers and nothing else — and passes no
`actionCatalog` at all.

`BattleModels.cs:101-106` names this itself: *"`DistrictAssaultResolver.BuildAnimateSetups` never set
`EquippedActionIds` … a MAJOR finding"*. S3 files it as the lane's headline wiring gap. The ideal files
it as *"Siege members fight with basic attacks only"* ([combat-ai-ideal.md](../combat-ai-ideal.md)
§4.2).

**This module threads the real loadout and the shared container resolver into siege, the way
`WebMatchService` already does for a web match, through the delegate inversion
`DistrictAssaultResolver` already uses twice.** It is byte-identical to every existing test by
construction (the providers default to null, which is today's behaviour — §Testing strategy), and it is
**its own golden cause**: it lands alone, in one commit, so that when live siege outcomes change there
is exactly one candidate explanation.

It also removes a SOLID S defect it would otherwise deepen: the "which action ids is this specimen
entering with" rule is **already written twice** (`gk-core/src/FusionRpg.Server/WebMatchService.cs:654-675` and
`gk-core/src/FusionRpg.Server/SpecimenLoadoutEndpoints.cs:83-94`, whose own doc comment admits it copies the
former). A third copy for siege is not on the table; one copy moves down to `RpgStore` and all three
callers read it.

## Tech stack

`FusionRpg.Core` (three optional `init` properties on `DistrictAssaultResolver`, threaded into the
existing `BattleEngine.Resolve` call; one tiny composite `IContainerEffectResolver`),
`FusionRpg.Data` (`RpgStore` gains the one loadout-resolution method the Server already has twice, and
`RpgStore.WorldTurns.cs` injects the providers beside the two it already injects),
`FusionRpg.Server` (two call sites start reading the moved method). No new dependency, no new tuning
file, no schema change.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault|FullyQualifiedName~Siege"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Golden|FullyQualifiedName~Expedition"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn|FullyQualifiedName~Loadout|FullyQualifiedName~Grant"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WebMatch|FullyQualifiedName~SpecimenLoadout"

.\scripts\verify-change.py -Paths @(
  'gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs',
  'gk-core/src/FusionRpg.Core/Actions/IContainerEffectResolver.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs',
  'gk-core/src/FusionRpg.Server/WebMatchService.cs',
  'gk-core/src/FusionRpg.Server/SpecimenLoadoutEndpoints.cs'
) -Session backlog-clean-up-20260920

python gk-core/scripts/guard-dal.py          # the loadout read moves INTO FusionRpg.Data -- this is the guard it must satisfy
python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
```

## Project structure

| File | New/changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs` | changed | Three optional `init` providers beside `HubInputsFor`/`UnlockStateFor`; `BuildAnimateSetups` sets `EquippedActionIds`; `Resolve` threads `actionCatalog`, the composite resolver, `runnerBindings`, `containersWithRunnerCoverage` and `equipEffectIdsFor`, and registers the extra defs in the existing `onEffectHostReady`. |
| `gk-core/src/FusionRpg.Core/Actions/IContainerEffectResolver.cs` | changed | Add `CompositeContainerEffectResolver` — first non-empty wins, ordinal, no allocation per call. |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs` | changed | `public IReadOnlyList<string> EquippedActionIdsFor(string instanceId)` — the one copy of the two-scope grant merge + `GetLoadoutOrAutoEquip`. |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | changed | Build the providers inside the same transaction that already builds `HubInputsFor`/`UnlockStateFor` (`:556-600`) and assign them on the `DistrictAssaultResolver` initializer. |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs` | changed | `EquippedActionIdsFor` (the `static` at `:654-675`) deleted; `:625` calls `_store.EquippedActionIdsFor(...)`. |
| `gk-core/src/FusionRpg.Server/SpecimenLoadoutEndpoints.cs` | changed | `HeldSkillCandidates` (`:83-94`) deleted; reads the same store method's candidate half. |
| `gk-core/tests/FusionRpg.Core.Tests/World/Turn/SiegeLoadoutWiringTests.cs` | **new — landed (CAI3.3)** | The wiring contract + the new pinned siege fixture (§Testing strategy). |
| `tests/FusionRpg.Data.Tests/Items/EquippedActionIdsForTests.cs` | **new; does not exist yet** | The moved rule's contract, at its new home. |

## The shape

### 1. Three providers, the inversion this file already uses twice

`DistrictAssaultResolver` is Core-only and statics-constructible (`DistrictAssaultResolver.cs:55`
`public static readonly DistrictAssaultResolver Instance = new();`), and `guard-dal.py` holds the line
that Core never reads a store. It already solves this twice, and says why:

> *"This resolver is Core-only and statics-constructible; `RpgStore` lives in `FusionRpg.Data` and
> reaching it from here would cross the DAL boundary `guard-dal.py` exists to hold. So Core declares
> the need and the Data layer injects the implementation at its own call site, which is dependency
> inversion rather than a layering exception."* — `DistrictAssaultResolver.cs:58-64`

Three more of the same shape, each defaulting to `null` = today's behaviour:

```csharp
/// <summary>The member's real entering loadout, keyed by InstanceId -- the SAME ids a web match
/// resolves for the SAME specimen (RpgStore.EquippedActionIdsFor, one rule, three callers). Null,
/// or a member with no InstanceId, keeps the pre-seam behaviour exactly: EquippedActionIds stays
/// null and BattleRunState falls back to the hand-built basic attack (BattleRunState.cs:637-681).
/// Same inversion and the same null-contract as HubInputsFor/UnlockStateFor above.</summary>
public Func<string, IReadOnlyList<string>>? EquippedActionIdsFor { get; init; }

/// <summary>The catalog those ids resolve against. Required the moment the provider above returns a
/// non-empty list -- BattleRunState warns and falls back to the basic attack when a loadout has no
/// catalog (BattleRunState.cs:553-558), which would make this module a silent no-op. Supplied by the
/// same Data-layer call site, from RpgStore.BuildActionCatalog(RungPolicy.Table).</summary>
public Actions.ActionCatalog? ActionCatalog { get; init; }

/// <summary>The store-backed container/equip effect bundle, exactly what
/// ActionContainerEffectResolverFactory.Build/BuildEquip hand a web match
/// (WebMatchService.cs:387-405). Composed WITH ConstructionActions.ContainerResolver, never instead
/// of it (see 2 below).</summary>
public SiegeEffectBundle? Effects { get; init; }
```

`SiegeEffectBundle` is a Core-side record carrying exactly the four things `BattleEngine.Resolve`
already takes and `ActionContainerEffectResolverFactory.Build`/`BuildEquip` already return
(`gk-core/src/FusionRpg.Data/Sqlite/ActionContainerEffectResolverFactory.cs:41,134`):

```csharp
public sealed record SiegeEffectBundle(
    IContainerEffectResolver Resolver,
    IReadOnlyList<Contracts.EffectDefDto> Defs,
    IReadOnlyList<RunnerBinding> RunnerBindings,
    IReadOnlySet<string> ContainersWithRunnerCoverage,
    Func<string, IReadOnlyList<string>>? EquipEffectIdsFor);
```

One record rather than five loose properties, because the five are only ever correct **together** —
`Defs` must be registered into the same host whose `Resolver` will be asked for them, and
`ContainersWithRunnerCoverage` is what keeps `BindContainers` from throwing on a runner-path container
(below). Five independent optionals invite a caller to set four.

### 2. The container resolver composes; it never replaces

**This is the half that cannot be skipped, and the reason is a throw, not a preference.**
`BattleRunState.BindContainers` (`BattleRunState.cs:787-818`) throws `ArgumentException` when a held
action carries a `ContainerId` that the supplied resolver cannot resolve (`:720-723`) — and throws
again if no resolver was supplied at all (`:714-717`). Real authored actions carry real container ids.
So threading `EquippedActionIds` while still passing only
`ConstructionActions.ContainerResolver` would not degrade: **it would throw inside
`RpgStore.CommitWorldTurn`'s single transaction and fail the whole world turn.** The two halves land
together or neither does.

```csharp
/// <summary>Several resolvers, asked in order, first non-empty answer wins. A decorator over the
/// one-method IContainerEffectResolver seam -- the same "wrap, never fork" shape FoggedBattleView
/// already uses for IBattleView -- not a second resolution mechanism. Ordinal, allocation-free per
/// call (no LINQ, no closure), and deterministic: the order is the constructor's order.</summary>
public sealed class CompositeContainerEffectResolver : IContainerEffectResolver
{
    readonly IContainerEffectResolver[] _inner;
    public CompositeContainerEffectResolver(params IContainerEffectResolver[] inner) => _inner = inner;

    public IReadOnlyList<string> EffectIdsFor(string containerId)
    {
        for (var i = 0; i < _inner.Length; i++)
        {
            var ids = _inner[i].EffectIdsFor(containerId);
            if (ids.Count > 0) return ids;
        }
        return Array.Empty<string>();   // BindContainers turns this into its own loud rejection
    }
}
```

Siege composes `[store bundle's resolver, ConstructionActions.ContainerResolver]`. The construction
containers keep resolving exactly as today (they are four fixed ids in a dictionary —
`gk-core/src/FusionRpg.Core/Battle/Siege/ConstructionActions.cs:70-77` — that the store bundle does not know),
and real authored containers now resolve too.

### 3. `Resolve`'s call, after

`DistrictAssaultResolver.cs:212-250`, with the five additions marked. Everything else is unchanged,
including `aiTuning: SiegeTuningPolicy.Ai` and the existing `onEffectHostReady` body that sets
`ConstructionBoard`, `AttackerEdge` and upserts `ConstructionActions.CompiledEffects`:

```csharp
report = BattleEngine.Resolve(setup, battleSeed,
    profile: BattleModeProfileCatalog.Resolve(BattleModeProfileCatalog.SiegeId),
    board: boardState,
    actionCatalog: ActionCatalog,                                   // NEW
    containerResolver: Effects is null
        ? ConstructionActions.ContainerResolver                     // unchanged when no bundle
        : new CompositeContainerEffectResolver(Effects.Resolver, ConstructionActions.ContainerResolver),
    runnerBindings: Effects?.RunnerBindings,                        // NEW
    containersWithRunnerCoverage: Effects?.ContainersWithRunnerCoverage, // NEW
    equipEffectIdsFor: Effects?.EquipEffectIdsFor,                  // NEW
    aiTuning: SiegeTuningPolicy.Ai,
    unlockStateFor: unlockStateFor,
    unlockTuning: UnlockTuning,
    onEffectHostReady: host =>
    {
        host.ConstructionBoard = constructionBoard;
        host.AttackerEdge = board.AttackerEdge;
        if (host.Bag.Catalog is Effects.InMemoryEffectCatalog catalog)
            foreach (var def in ConstructionActions.CompiledEffects) catalog.Upsert(def);
        if (Effects is { Defs.Count: > 0 })                         // NEW -- the same two-piece
            ActionContainerEffectResolverFactory.RegisterInto(host, Effects.Defs);   // hand-off web match uses
    });
```

⚠️ `RegisterInto` lives in `FusionRpg.Data`
(`gk-core/src/FusionRpg.Data/Sqlite/ActionContainerEffectResolverFactory.cs:112`) and Core cannot call it. So
the registration is **part of the bundle**, not a Core call: `SiegeEffectBundle` carries
`Defs`, and the Data-layer injector hands the resolver an
`Action<BattleEffectHost>? RegisterEffects` alongside it (or, equivalently, the bundle carries the
delegate). Either spelling is fine; what is not fine is Core naming a `FusionRpg.Data` type. The build
task picks one and states it in the commit body; the recommended default is a
`Action<BattleEffectHost>` on the bundle, because it keeps `SiegeEffectBundle` free of `EffectDefDto`
plumbing and mirrors `HubInputsFor`'s "Core declares a delegate" idiom exactly.

### 4. `BuildAnimateSetups`, after

One added initializer line at `DistrictAssaultResolver.cs:453-460`, beside the existing `SpecimenId`
and `HubInputs` lines that already carry the same `InstanceId` guard:

```csharp
SpecimenId = member.InstanceId,
// The InstanceId guard lives HERE, not in the provider (the existing comment at :455-457) --
// a member without one is a non-player force or a guard, so there is nothing to look up.
HubInputs = string.IsNullOrWhiteSpace(member.InstanceId) ? null : HubInputsFor?.Invoke(member),
EquippedActionIds = string.IsNullOrWhiteSpace(member.InstanceId)     // NEW
    ? null
    : EquippedActionIdsFor?.Invoke(member.InstanceId!),
AdditionalHeldActions = side == AttackerSide ? ConstructionActions.CompiledActionsForGrant : null,
```

**`AdditionalHeldActions` stays, unchanged, attacker-side only.** It is not superseded: it is
pre-compiled, catalogue-free content the resolver already holds
(`BattleModels.cs:108-113`), appended after `EquippedActionIds` resolves
(`BattleRunState.cs:586-594`), so an actor never loses construction by gaining a loadout and never
loses its loadout by gaining construction. The two fields are additive by design and the setup loop
keeps them that way.

**`null` vs empty is load-bearing.** The provider returns `null` for a member with no instance id, and
`BuildAnimateSetups` must pass `null` — never `Array.Empty<string>()`. `EquippedActionIds` is
`[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]`
(`BattleModels.cs:98-99`, and the mirror on `BattleActorResult` at `:612-613`), whose own comment says
why: an empty array serializes as `"EquippedActionIds":[]` and moves every golden that hashes a
`BattleActorSetup`, *"for a reason that is not a determinism break."*

### 5. One loadout rule, three callers

`RpgStore` gains the rule that already exists twice in the Server:

```csharp
// RpgStore.Loadouts.cs -- beside GetLoadoutOrAutoEquip (:116), which it already calls.
/// <summary>The one answer to "which action ids is this specimen entering with". Two grant scopes
/// with two deliberate lifetimes, merged: OwnerKind.UniqueActor carries the durable unlock-ladder
/// grant (action-grant-owner-kind-durability, 2026-09-07 -- it must survive the boot sweep's
/// ClearSessionScopedBindings), OwnerKind.Entity carries an ITEM's granted action, whose opposite
/// lifetime is the point (unequipping must make it disappear). Reading one scope silently drops the
/// other. Moved here from WebMatchService.EquippedActionIdsFor so siege, web match and the loadout
/// endpoint cannot drift -- three readers of one rule, never three rules.</summary>
public IReadOnlyList<string> EquippedActionIdsFor(string instanceId);

/// <summary>The candidate half alone, for the loadout endpoint, which needs the candidates and not
/// the resolved loadout (SpecimenLoadoutEndpoints.cs:83-94's own job).</summary>
public IReadOnlyList<AutoEquipCandidate> HeldSkillCandidatesFor(string instanceId);
```

Both bodies are the existing `WebMatchService.cs:663-675` text, moved verbatim (two `ListGrants`
calls, `GetAction`, the `ActionKind.Skill` filter, `Distinct`, then `GetLoadoutOrAutoEquip` on the
entity scope). Nothing about the rule changes — which is what makes the move provable by the two
callers' existing tests staying green.

### 6. The Data-layer injection, in the transaction that already exists

`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:556-600` already constructs the resolver with
`HubInputsFor` and `UnlockStateFor` inside `CommitWorldTurn`'s single transaction, and states the
reason: *"the allocation used to compose a fight and the state the turn commits are then the same
snapshot, never two values that could move between them."* The three new providers join it, for the
same reason and in the same object initializer.

**Build the bundle once per turn, not once per member.**
`ActionContainerEffectResolverFactory.Build(store)` compiles every referenced container
(`ActionContainerEffectResolverFactory.cs:41`) and `BuildEquip` compiles the equip atoms for a supplied
specimen id list (`:134`). A world turn can resolve several assaults (`Two_assaults_in_one_turn_get_different_seeds`,
`gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs:150-164`), so the bundle is
built once and shared, and `BuildActionCatalog(RungPolicy.Table)` is likewise called once. Per-assault
rebuilding would be an O(assaults × corpus) compile inside a write transaction.

## Tunables

**None.** This module adds no number and moves no number. The two tuning reads siege already performs —
`SiegeTuningPolicy.Ai` (`DistrictAssaultResolver.cs:225`) and `UnlockTuningPolicy.Tuning` — are
untouched, and `RungPolicy.Table` is the same rung table a web match already prices against
(`WebMatchService.cs:130`). A loadout is *content* (grants and a stored loadout row), not a balance
surface.

## Code style

- **A new provider states its null-contract in its own doc comment**, the way `HubInputsFor` does
  (`DistrictAssaultResolver.cs:65-66`: *"Null keeps the previous behaviour exactly"*). That sentence is
  the module's byte-identity proof living next to the code that has to keep it true.
- **The `InstanceId` guard stays at the call site**, not inside the provider — the existing comment at
  `DistrictAssaultResolver.cs:455-457` argues this explicitly, and a second provider must not relitigate
  it.
- **`null`, never `Array.Empty<string>()`, for "no loadout"** — `WhenWritingDefault` is doing golden
  work (`BattleModels.cs:90-99`).
- **Wrap, never fork**: the composite resolver is a decorator over the one-method seam, the same shape
  `FoggedBattleView` uses for `IBattleView`.
- **Moved code moves verbatim.** The loadout rule's body is copied character-for-character into
  `RpgStore`; any behaviour change in the same commit would make the two callers' green tests
  meaningless as evidence that nothing moved.

## Testing strategy

**`gk-core/tests/FusionRpg.Core.Tests/World/Turn/SiegeLoadoutWiringTests.cs` (new — **landed**, CAI3.3)** —
`BuildAnimateSetups` is already `internal` for exactly this reason
(`DistrictAssaultResolver.cs:413-414`: *"`internal` rather than `private` since solid-remediation T3.3:
the D4 seam's own test drives this directly"*), so these drive the seam, not a whole world.

- ✅ `With_no_provider_every_member_setup_carries_a_null_loadout` — the identity property. Asserted,
  not assumed, because every existing siege test depends on it.
- ✅ `A_member_with_no_instance_id_never_consults_the_provider` — the guard, with a provider that
  throws if called.
- ✅ `A_member_with_an_instance_id_carries_exactly_the_ids_the_provider_returned` — no filtering, no
  reordering, no dedupe in the resolver; the rule lives in `RpgStore`.
- ✅ `Additional_held_actions_are_still_attacker_side_and_still_additive` — the construction grant
  survives, and a member with both carries both.
- ✅ `A_real_container_id_with_only_the_construction_resolver_throws` — pins the coupling in §2 as a
  *test*, so a later refactor cannot quietly split the two halves. Drives `BattleRunState`'s
  `BindContainers` rejection (`BattleRunState.cs:795-797`) and asserts the thrown message names the
  container.
- ✅ `The_composite_resolver_prefers_the_store_bundle_and_falls_through_to_construction` — both
  directions, plus an id neither knows returning empty.
- ❌ Never assert how many actions a member holds, how many containers the store bundle resolved, or
  any generated action name. Those are readings of a corpus that grows.

**`tests/FusionRpg.Data.Tests/Items/EquippedActionIdsForTests.cs` (new; does not exist yet)** —
in-memory store (`testing-standard.md`: a store test runs in memory; no temp directory, no swallowed
delete).

- ✅ `Both_grant_scopes_are_merged` — a UniqueActor grant and an Entity grant both appear; dropping
  either scope fails. This is the defect the Server comment at `WebMatchService.cs:656-662` records,
  now pinned at the rule's one home.
- ✅ `Only_skill_kind_grants_are_candidates` — a basic/innate grant is never loadout-eligible.
- ✅ `A_stored_loadout_wins_over_auto_equip` and `absent_falls_back_to_auto_equip` — the contract
  `GetLoadoutOrAutoEquip` already owns, asserted through the new front door.
- ❌ Never assert a candidate count or a specific generated action id from the corpus.

**Unchanged suites that must stay green, untouched, and are the move's proof:**
`gk-core/tests/FusionRpg.Server.Tests` web-match and specimen-loadout tests (the rule moved, the behaviour did
not), and every test in `gk-core/tests/FusionRpg.Core.Tests/World/Turn/` and
`gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/`.

### Golden impact — stated precisely, because the map's phrase needs refining

The map calls this module *"its own golden cause"*. Measured against the actual golden surface, the
honest statement is sharper and must be in the commit body:

1. **No committed golden hash moves.** `BattleGoldenTests`' four hashes
   (`gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs:74-77`) are hand-built battle fixtures with
   no `EquippedActionIds` and no district assault; `ExpeditionResolverTests.Tier_goldens_are_locked`
   hashes expedition setups that siege actors never enter, and `EquippedActionIds`'
   `WhenWritingDefault` suppression (`BattleModels.cs:98-99`) means setting it on siege actors adds no
   key anywhere else. `RulesetVersion` stays 5 — this module changes no resolution rule, only which
   actions an actor holds.
2. **Every existing siege test stays byte-identical**, because they all construct
   `DistrictAssaultResolver.Instance` with no providers
   (`DistrictAssaultResolverTests.cs:111-150`, `SiegeLootTests.cs`, `ConstructionLiveWiringTests.cs`),
   and a null provider is today's behaviour by construction.
3. **The behaviour that genuinely changes — a live world turn's siege outcomes — is pinned by nothing
   today.** The resolver's own tests assert shape, determinism and bounds (*two sides and a version
   stamp*, *survivor counts ≤ roster*, *same seed ten thousand times*), never an outcome. So "re-bless
   the siege golden" is not available: **there is no siege golden.** That absence is itself the risk
   this module must close, so it ships one:

   ✅ `Siege_loadout_fixture_is_locked` — a fixed roster, a fixed board, a fixed seed and a small
   hand-built `ActionCatalog` + `DictionaryContainerEffectResolver` (synthetic, the
   `SyntheticLoadoutHarness.cs:17-22` precedent), hashing the resulting `BattleOutcome`'s
   winner + per-side survivor keys. It pins a **deterministic engine output**, not a population
   reading, and it is what any later siege change re-blesses against. The fixture's catalog is
   authored in the test, never read from `gk-data/packs/fusion/data/seed/**`, so a corpus that grows never moves it.

## Boundaries

**Always:** default every provider to `null` and keep null == today; land the loadout and the container
resolver in the **same commit** (§2 — the other order throws inside a world-turn transaction); build
the effect bundle and the action catalog once per turn; pass `null` and never an empty array for "no
loadout"; keep `AdditionalHeldActions` attacker-side and additive; move the loadout rule's body
verbatim.

**Ask first:** granting construction actions to the defender side (`DistrictAssaultResolver.cs:445-449`
names this as a separate, unspecced question and this module does not answer it); any change to which
grant scopes a loadout reads; bumping `RulesetVersion`.

**Never:** read a store from `FusionRpg.Core` (`guard-dal.py`; the delegate inversion is the whole
pattern here). Never write a **third** copy of the loadout-resolution rule — the two that exist
(`WebMatchService.cs:654-675`, `SpecimenLoadoutEndpoints.cs:83-94`) collapse into one in this commit,
and a siege-local copy would be the SOLID S defect `CLAUDE.md` makes binding. Never replace
`ConstructionActions.ContainerResolver` — compose with it, or `Built`/`Assembled`/`Summoned`/`Laboured`
become unresolvable and `BindContainers` throws. Never set `EquippedActionIds` without
`actionCatalog`: `BattleRunState.cs:637-681` degrades to the basic attack with a warning, which would
make this module look shipped and do nothing. Never make the siege AI grant actions — it only chooses
among actions an actor already holds (`DistrictAssaultResolver.cs:243-247` records this correction
against its own earlier wrong comment).

## battle-engine-ssot §5 — the six answers

1. **Which responsibility is it (§3), or a new one?** Responsibility 8, **action system**, on its input
   side — *which* actions an actor enters battle holding. No addition to the closed register.
2. **Does it DECIDE or RESOLVE?** **Neither, strictly** — it supplies an *input* to both. It changes the
   candidate set the deciding side (`IIntentSource`) chooses from, and the container grants the
   resolving side executes. The decision rule and the resolution rule are untouched; only the data
   reaching them changes.
3. **Mechanism or loop?** Mechanism, and the module's point is that siege currently owns a *degenerate
   copy* of it: every other real caller (`WebMatchService.cs:391-405`) threads catalog + resolver +
   runner bindings + equip ids, and siege threads one hardcoded resolver. After this, one mechanism,
   two callers, with the per-mode part being only the composite's construction arm.
4. **Which existing implementation does it extend?** `ActionContainerEffectResolverFactory.Build`/
   `BuildEquip`/`RegisterInto` (`ActionContainerEffectResolverFactory.cs:41,112,134`),
   `RpgStore.BuildActionCatalog` (`RpgStore.ActionCatalog.cs:38`), `RpgStore.GetLoadoutOrAutoEquip`
   (`RpgStore.Loadouts.cs:116`) and `BattleRunState`'s existing setup loop. Nothing is re-implemented;
   the composite resolver is a decorator over a one-method interface.
5. **Does every mode get it?** Web match and expedition already have it; siege gains it here; **delve
   does not yet** — `DelveBattleSessionManager.StartSession`/`Resume` take `actionCatalog` and
   `containerResolver` as optional parameters (`DelveBattleSessionManager.cs:192-194`, `:267-269`) and
   the delve's content caller does not exist, which is party-dungeon's D2.16/D5.11 and is named as a
   dependency in [spec-delve-automated-wiring.md](spec-delve-automated-wiring.md), not built here. The
   lawn's equivalent is `lawn-held-actions` (module 16). So: three of five today, four after this, with
   each remainder named and owned.
6. **Deterministic and seeded?** Yes. The providers read the store **inside the turn's transaction**
   (the snapshot discipline `RpgStore.WorldTurns.cs:551-554` already states), the composite resolver is
   ordinal with a fixed constructor order, and `BattleRunState` sorts the resolved loadout by
   `ActionTagPreference.Compare` (`BattleRunState.cs:582`). No clock, no RNG, no ambient state. The
   siege AI itself remains RNG-free (S3: *"Zero RNG anywhere"*).

## Success criteria

1. A real legion member with an `InstanceId` and a stored or auto-equipped loadout enters a district
   assault holding those actions — asserted at the `BuildAnimateSetups` seam, not inferred.
2. A real authored container resolves in a siege, and the four construction containers still resolve;
   a container neither knows still produces `BindContainers`' loud rejection.
3. `RpgStore.EquippedActionIdsFor` is the only implementation of that rule in `src/`; a repo search
   finds no second `ListGrants(UniqueActor) … Concat … GetLoadoutOrAutoEquip` chain.
4. Every existing test in `gk-core/tests/FusionRpg.Core.Tests/World/Turn/`,
   `gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/`, `BattleGoldenTests`, `ExpeditionResolverTests` and the
   Server's web-match/loadout tests passes **unchanged**. `RulesetVersion` stays 5.
5. `Siege_loadout_fixture_is_locked` exists and passes, giving siege its first pinned outcome.
6. `guard-dal.py`, `guard-actor-hub.py` and `guard-single-writer.py` are green.
7. One commit, one cause. The body names the cause ("siege members now enter with their real
   loadouts"), states that no committed golden moved, and states which spelling of the
   `RegisterInto` hand-off (§3) was chosen.

## Open questions

**None blocking.** Three notes, two of them cross-module:

1. **Which spelling of the effect-registration hand-off.** Core cannot name
   `ActionContainerEffectResolverFactory` (a `FusionRpg.Data` type), so `SiegeEffectBundle` either
   carries the raw `Defs` and the Data injector wraps the registration, or it carries an
   `Action<BattleEffectHost>`. **Recommended default: the delegate**, matching `HubInputsFor`'s
   established "Core declares a need, Data injects" idiom and keeping `EffectDefDto` out of the Core
   record. A build-task call, not an owner one.
2. **Cross-module (module 1, `core-scorer`): siege's action choice is still "first usable".**
   `SiegeAiIntentSource.TryDeclare` scores *targets* and then takes the first usable action in
   preference order for the chosen target (`SiegeAiIntentSource.cs:105-123` — its own comment says
   *"Identical to `StubIntentSource`'s own step 3, verbatim"*). Until then, giving siege five actions
   means it takes the highest-`ActionTagPreference` usable one, every round. That is still a large
   improvement over one basic attack, and it is honest to say the *choice* quality is module 1's, not
   this module's.
3. **Doc drift found and not fixed here.** `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:84-90` still says
   `EquippedActionIds` is *"Purely carried data: nothing in `BattleEngine`'s round loop reads it
   today"* — contradicted by `BattleRunState.cs:582-640`, which compiles the loadout from it.
   Code beats docs. The one-line correction belongs in this module's commit, since this is the file it
   edits the contract of; it is named here so the build task does not skip it.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches. (Battle engine action input; siege world-turn
    resolver; the DAL boundary; the loadout/grant rule.)
[~] I established and recorded this session's boundary. tasks/sessions/backlog-clean-up-20260920.json
    exists and this lane writes only the three spec files named in its prompt. I did NOT run
    session-boundary-check.py -- the lane brief bars running scripts; named rather than hidden.
[x] I read every doc in the §1 row(s) for those subsystems, this session: combat-ai-map.md,
    combat-ai-ideal.md, research/combat-ai/{AUDIT,S2,S3}.md, battle-engine-ssot.md §2/§3c/§5,
    DESIGN-GATE.md §5, CLAUDE.md, AGENTS.md.
[x] I checked decisions.md for a lock covering this. The "Action selection (battle adoption)" row is
    the governing lock; see the note under it in Open questions 2 and the RulesetVersion argument in
    Testing strategy.
[x] Every factual claim cites file:line.
[x] `python scripts/audit-doc-citations.py --scope <this file> --summary` run this session:
    0 HIGH findings. The remaining D1 rows are the files this spec marks "(new; does not exist
    yet)", which the audit exempts because the line says so.
[x] I verified claims against CODE, not comments -- and found one comment that is wrong
    (BattleModels.cs:84-90, reported in Open questions 3) and one audit citation that is off
    (AUDIT.md C8 already corrects :452 to :450; confirmed :450 is the AdditionalHeldActions line).
[x] I read the surrounding section of every rule I quoted.
[~] I tested (not assumed) any constraint I am reporting. "No committed golden moves" is argued from
    the golden fixtures' own setups and from EquippedActionIds' WhenWritingDefault suppression, and
    "every existing siege test stays green" from those tests constructing Instance with no providers
    -- NOT from a run. The lane brief bars running tests. The build task must run them.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagated to prose, Structure, Testing, Boundaries within this spec.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The new fixture hashes a deterministic engine outcome from a test-authored catalog, and
    Testing strategy explicitly bans asserting held-action or container counts.
[x] No event-refreshed cache is introduced or touched. (The per-turn bundle is built once inside one
    transaction and discarded; it is a snapshot, not a cache with invalidation triggers.)
[x] No acceptance criterion fixes an ordering that can vary in real play. The composite resolver's
    order is fixed by construction and asserted in both directions.
[x] Produces/consumes no actor combat or derived magnitude: HubInputs is untouched and no new fold or
    composer appears.
[x] Does not invent or extend a SOLID-violating parallel path -- it collapses an existing duplicate
    (two copies of the loadout rule) rather than adding a third.
[~] A new rule has a registry row. "One loadout-resolution rule" is enforced by success criterion 3
    (a repo search) rather than by a shell guard today; whether it earns a row in
    gk-core/scripts/enforcement-registry.v1.json is the build task's call, named here rather than assumed.
```

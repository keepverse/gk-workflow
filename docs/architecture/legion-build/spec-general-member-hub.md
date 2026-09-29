# Spec: `general-member-hub`

**Status: written against shipped code 2026-09-19.** Module id `general-member-hub`, row 5 of the
[legion-build map](../legion-build-map.md) (wave 2; depends on `member-stack`; external
`species-progression` `layer-source-selector`, `empire-species-container`, `species-layer-delivery`,
`empire-progression` `ai-empire-species`). **Owner decision Q2 (2026-09-19):** *a general world member
reads the progression of the empire that owns its legion.* Map X2 records that no other map claimed this.

## Objective

A general world member — a row with no `InstanceId` — fights today with nothing from the RPG layer: no
empire species progression, no layer 5c, no legion equipment. Two guards return `null` for it before any
store is asked. This module makes such a member compose through `ActorHub` like every other actor, from
the layers a general actor carries: **layer 2b of the empire that owns its legion** (Q2), layer 1a/1b once
`species-layer-delivery` 6.2 delivers them, and the `BoundAtoms` that layer 5c (`legion-owner-scope`) and
legion equipment (`legion-equipment`) produce. It is the **one** place the world answers "what does this
member bring into battle".

Success looks like: for the same `(empire, species, level)`, a general world member and a general lawn
actor resolve the same 2b contribution by channel and SourceId; a general member never carries a 2a or a
commander term; a Wild-faction force carries no 2b; with 2b empty a member resolves exactly as today; the
actor-hub guard stays green.

## Scope and non-goals

- **In:** the two guards; the provider's general branch through `ProgressionLayerSelector`; the Q2 empire
  rule; the one join of `BoundAtoms` from 5c and legion equipment for **every** fighting member (general or
  unique); the provider's signature (it needs the member's legion).
- **Out:** how 2b is projected, stored or re-projected (`species-progression`); the enemy empire's (`zomboss`) species XP
  (`ai-empire-species`); what 5c and legion equipment contain (their own modules); the commander aura
  (`aura-skill`); kill attribution in world battles (`battle-engine-ssot.md` §4 D9).

## Correction to the map (§5.5)

The map says a general member composes *"instead of flat `BattleRuleset.BaseAtk/BaseDefense(level)`"*.
That is not what the code does or should do. `BaseAtk`/`BaseDefense` are the **baseline** every battle
actor carries — unique members included (`DistrictAssaultResolver.cs:439-440` applies them to every row)
— and `BattleHubCompose` registers them as the baseline and affinity subsystems, then folds every Hub
input **on top** (`gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:52-100`, baseline at `:81-83`). So this
module adds contributions to the one fold; it never replaces the baseline and never overrides Hub output.

## ActorHub gate

**Contribute**, through existing registered subsystems only — no new subsystem, no new SourceId family:

| Layer | Reaches the fold through | SourceId |
|---|---|---|
| 2b empire species | `BattleHubInputs.Aptitude` → `AptitudeSubsystem` (registered by `ActorHubBootstrap.CreateDefault` when an allocation is present, `BattleHubCompose.cs:66-68`) | `aptitude.{Share}` (`actor-hub-ssot.md` §8.1) |
| 1a / 1b species | `BattleHubInputs.SpeciesLayers`, the field `species-layer-delivery` 6.2 adds | owned by that module (`rpg.species-layer`) |
| 5c legion | `BattleHubInputs.BoundAtoms` → `AtomDerivedSubsystem` (`BattleHubCompose.cs:72`) | `legion:{entityId}:{containerId}` (`legion-owner-scope`) |
| 3 legion equipment | `BattleHubInputs.BoundAtoms` → `AtomDerivedSubsystem` | `legion-equip:{slot}:{pieceId}` (`legion-equipment`) |

`BoundDerivedAtom` already carries its SourceId (`gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:91-92`),
so no join here mints one: the producing module does.

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built | The provider seam: Core declares `HubInputsFor`, Data injects it inside the commit transaction | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:71`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:548-600` |
| Built | `BattleHubInputs` with `Aptitude` and `BoundAtoms` | `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs:15-31` |
| Wiring gap | **Guard 1**, in the resolver: `HubInputs = IsNullOrWhiteSpace(InstanceId) ? null : …` — the provider is never called for a general | `DistrictAssaultResolver.cs:459` |
| Wiring gap | **Guard 2**, in the provider: `if (IsNullOrWhiteSpace(member.InstanceId)) return null;` | `RpgStore.WorldTurns.cs:561` |
| Wiring gap | The provider picks the empire from the species' **side** | `RpgStore.WorldTurns.cs:568-569` (`KillAttribution.EmpireOf(... .Side)`) |
| Wiring gap | A non-Dave empire resolves `Empty` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:238-243`; closed by `ai-empire-species` |
| Owned elsewhere | Unique branch merges `commander + species + specimen` (2a and 2b together) | `RpgStore.WorldTurns.cs:581-590`; fixed by `layer-source-selector` (its C1) |
| Owned elsewhere | The selector API: `ProgressionLayerSelector.Select(source, empire, humanEmpire)` → `ProgressionOwner.Species` for a general | `docs/architecture/species-progression/spec-layer-source-selector.md:80-113` |
| Built | Faction ids and empire ids are one id space (`"dave"`, `"zomboss"`) | `gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs:3-14`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:56-58` |
| Built | Raise founds zombie-side species for every faction | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:157-170` |

## Design

### 1. The provider takes the legion

```csharp
// DistrictAssaultResolver.cs:71 — the delegate gains the member's entity.
public Func<WorldEntity, WorldEntityMember, Battle.BattleHubInputs?>? HubInputsFor { get; init; }
```

Guard 1 is deleted: the resolver calls the provider for **every** fighting row and the provider decides.
Rationale: which layers an actor carries is the selector's rule (`spec-layer-source-selector.md`, *"the
whole point is that it no longer contains a rule"*), and a guard in the resolver is a second copy of it.

### 2. The Q2 empire rule — one function

```csharp
// src/FusionRpg.Core/World/LegionEmpire.cs (new; the file does not exist yet)
public static class LegionEmpire
{
    // The empire a general world member reads 2b from: the empire that owns its legion (owner Q2).
    // Faction ids and empire ids are one id space (EmpireId.cs:3-9). A faction that is not an empire of
    // this save (Wild, Clan, Rival today) has none, and its members carry no 2b.
    public static EmpireId? Of(WorldEntity legion, IReadOnlySet<EmpireId> saveEmpires);
}
```

`saveEmpires` comes from `save-identity`'s `rpg_save_empires` when it lands; until then it is
`{EmpireId.Dave, EmpireId.Zomboss}`, the two values the code already names (`EmpireId.cs:13-14`).

This is deliberately **not** `KillAttribution.EmpireOf(side)`. On the lawn side and empire coincide; on the
world map a player raises zombie-side species (`RaiseResolver.cs:162`), and Q2 rules that the player's
legion reads the **player's** empire progression of that species.

### 3. The provider's general branch

```text
member.InstanceId blank (a general):
  empire = LegionEmpire.Of(legion, saveEmpires)
  if empire is null → Aptitude = null                     (no 2b; Wild/Clan/Rival)
  else layers = ProgressionLayerSelector.Select(
                  CreatureProgressionSource.EmpireGeneral(member.SpeciesId), empire, HumanEmpireOf(save))
       Aptitude = the Species owner's 2b allocation ALONE (species-progression R2), never + commander
  SpeciesLayers = species-layer-delivery 6.2's 1a/1b rows, when that field exists
  BoundAtoms    = LegionMemberAtoms(world, legion, member)          (§4)
member.InstanceId set (a unique):
  unchanged from layer-source-selector's fixed branch, plus BoundAtoms = LegionMemberAtoms(...)
```

A general member never carries a commander term. `CarriesCommander` from the selector is ignored on the
general branch: `species-progression` ruling R2 resolves 2b alone, and a legion commander's aura is
`aura-skill`'s, not an allocation.

### 4. `LegionMemberAtoms` — the one join

A Data-side function, read inside the same transaction as the allocation (the precedent the provider
states at `RpgStore.WorldTurns.cs:551-553`): the member's legion 5c atoms (`legion-owner-scope`'s reader)
concatenated with its fitted legion-equipment atoms (`legion-equipment`'s reader). Until those modules
land it returns an empty list, and an empty `BoundAtoms` composes exactly as `null`
(`BattleHubInputs.cs:9-11`).

### 5. Stacks

A stack is one combatant (`stack-combatant`), so the provider runs once per stack, not once per unit. The
contributions are **per unit** — a stack's `Atk` scales by living count inside the engine, never here.

## Tunables and numeric types

None. No number is decided here; every magnitude comes from a projector or a band another module owns.
Allocation and atom amounts keep their existing types.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~DistrictAssault"
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/guard-dal.py
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs  MODIFIED  delegate takes the entity; guard 1 removed
src/FusionRpg.Core/World/LegionEmpire.cs                  NEW       Q2 rule
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs          MODIFIED  general branch; LegionMemberAtoms join
tests/FusionRpg.Data.Tests/World/...                      EXTEND    parity + Q2 cases
```

## Testing strategy

- **Parity.** For the same `(empire, species, level)` and allocation rows, a general world member's
  composed 2b contributions equal a general lawn actor's, by channel, amount and SourceId (the
  four-path parity test `layer-source-selector` owns gains a fifth path).
- **Q2.** A player (`dave`) legion of a zombie-side species reads `dave`'s rows for that species, not
  `zomboss`'s; a `zomboss` legion reads `zomboss`'s; a `wild` legion reads none. Each its own test.
- **Exclusivity.** A general member's inputs never contain a `UniqueCreature` or `Commander` allocation;
  a unique member's never contain a species term (inherited from the selector, re-asserted here).
- **Identity.** With every 2b row empty and no 5c/equipment, every siege golden is unchanged.
- **One call per stack.** A stack of 40 calls the provider once.
- **Guard.** `guard-actor-hub.py` green; no type named `*Composer*` added.

## Boundaries

- **Always:** decide layers through the selector; decide the empire through `LegionEmpire.Of`; read inside
  the commit transaction.
- **Ask first:** giving Clan/Rival/Wild factions an empire (that is `counterparties`'); any commander term
  for a general.
- **Never:** a guard on `InstanceId` outside the selector; `KillAttribution.EmpireOf(side)` for a world
  member's 2b; replacing `BaseAtk`/`BaseDefense`; folding an atom or allocation here.

## Success criteria

1. Generals compose 2b from their legion's empire through the Hub, with parity to the lawn.
2. Wild/Clan/Rival generals carry no 2b; uniques are unaffected beyond the shared `BoundAtoms` join.
3. Empty 2b ⇒ unchanged siege results.
4. Guards green.

## Interface exposed to dependents

The provider's general branch and `LegionMemberAtoms` — `legion-owner-scope` and `legion-equipment` plug
their readers into the join; `field-battle-kinds` reuses the provider for every battle kind.

## Hard edges

- **Golden re-bless and bump.** Siege goldens move for general members once 2b rows exist. Ordered after
  `species-progression`'s own re-bless (its map §8: `layer-source-selector` C1, then
  `species-layer-delivery` 6.1) so no value moves twice. **Round 6 C1:** the world bump is **wave 2's single
  bump**, shared with the other wave-2 modules and taken at landing, not a value this module mints
  ([landing-order.md](../trade-network/landing-order.md)) — it is needed because the same command log now
  resolves general fights differently.
- **Trimmed-report re-derivation.** `GetWorldTurnReport` re-derives a trimmed turn by stepping with the
  store-free resolver (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:773`), so any fight whose members
  carried Hub inputs re-derives on flat stats — pre-existing for uniques since D4, widened by this module to
  every general member, 5c and legion equipment. Decision: re-derivation **refuses** (returns `null`, the
  existing "refuse rather than fabricate" answer at `:760-761`) for a turn whose stored report contains a
  battle composed with store inputs, instead of fabricating flat-stat results. The flag is one boolean on
  the stored turn log, written by the commit that injected a provider.
- **Cross-doc requirements (not made here — owed by their owners, filed with this spec):**
  1. `decisions.md` *Actor layer stack* row: *"2b reads the empire that owns the species"* holds on the
     lawn; **on the world map a general member reads the empire that owns its legion** (owner Q2).
  2. `spec-layer-source-selector.md` rule 2 (*"for a general, from the ONE side mapping … No third
     mapping"*) and its Boundaries "Ask first: giving a general world-battle member any 2b term": both
     answered by Q2; the world-map general passes `LegionEmpire.Of`, which is the owner-ruled mapping, not a
     third invention.
  3. `spec-species-layer-delivery.md:28` ("Battle general member … unchanged"): now this module's.
  4. `spec-legion-commander.md:117-121` ("a separate, pre-existing gap for `species-progression`"): closed
     here.

## Dependencies

`member-stack`; external `layer-source-selector` (must land first), `empire-species-container`,
`species-layer-delivery` (6.1 before this module's re-bless; 6.2 for 1a/1b), `ai-empire-species`
(the enemy empire's rows), `save-identity` (`rpg_save_empires`; an interim two-value set until then).

## Design-gate checklist

```
[x] Subsystems: stats (ActorHub, actor layer stack), battle (world join), general vs unique creature.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: actor-hub-ssot.md §1-§2 and §6-§13, actor-layer-compose-ideal.md (whole),
    creature-system-map.md Vocabulary + amendments, DESIGN-GATE Stats/General-vs-unique rows,
    spec-layer-source-selector.md Design + Boundaries, spec-species-layer-delivery.md table.
    NOT read: stat-system.md, spec-derived-stat-sheet.md, spec-magnitude-and-units.md,
    combat-power-number-ideal.md (the Stats row's other documents).
[x] decisions.md checked: Actor layer stack, Creature progression source and spawn ownership (:113).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: both guards, the provider, BattleHubCompose's registration and baseline,
    RpgStore.Aptitudes' empire rule, EmpireId, template faction ids.
[x] Read the surrounding section of every rule quoted.
[~] "Empty 2b ⇒ goldens unchanged" is an acceptance test, not run here.
[~] Contradiction named, not hidden: Q2 amends the Actor layer stack row's 2b rule for world members.
[~] Corrections propagated: map §10; the four cross-doc requirements listed above, not made.
[x] No population count pinned.
[x] No event-refreshed cache (read inside the commit transaction each turn).
[x] No ordering assumption.
[x] Contributes via ActorHub registered subsystems with existing SourceId grammar; no private fold.
[x] No parallel path: one selector, one empire rule, one join.
[x] No new rule needing a registry row beyond the actor-hub guard already covering it.
```

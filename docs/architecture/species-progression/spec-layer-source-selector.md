# spec — `layer-source-selector`

**Module 1 of `species-progression`** ([map](../species-progression-map.md)). Depends on nothing.
Status: spec, 2026-09-18, strengthened the same day (R3/R4/R16, `commander-identity`'s `EmpireId`,
`save-identity` G5). No build authorized until the map is reviewed.

**Typed against `commander-identity`.** The empire type below is `EmpireId` (`spec-commander-identity.md`
"Types"), which deletes the `CommanderId` enum. If this module builds first, it uses today's
`CommanderId` in the same positions and `commander-identity`'s rename sweep (which already inventories
`== CommanderId.X` branches) re-types it; nothing here depends on the enum being closed. The same holds for
the three `save-identity` seams the code below names (`HumanEmpireOf`, `SpecimenOwnerUnlocked`'s
`empire_id`, `CommanderScopeKey(EmpireRef)`): built first, this module passes today's equivalents — the
human empire is `CommanderId.Dave`, a specimen's owner is the human save unless its row is the by-name
Zomboss row (`RpgStore.ZombossDeploy.cs:25-29`), and the key stays `$"player:{header.PlayerId}"` — each
behind the one call site `save-identity` later re-types. **This module therefore does not wait on either
program**; its C1 fix must not, because step 6.1 of `species-layer-delivery` is ordered after it.

## Objective

Every compose path asks **one** Core function which progression layers an actor carries — commander
term (and for which empire), **2a** (its own specimen) **or** **2b** (its empire's species), never both —
instead of each path re-deriving the answer. Today three paths derive it separately and one of them is
wrong.

**The defect this closes (map C1).** `RpgStore.WorldTurns.cs:559-593` — the district-assault
`HubInputsFor` provider added by `solid-remediation` T4.4 — returns `commander + species + specimen` for
every member with an `InstanceId`. `WorldState.cs:277-278` documents that field as *"Roster specimen
(`rpg_unique_actors`); null for non-player forces and guards"*, so every member that reaches that line is
a **unique**, and it receives the empire species fallback. That violates:

- `decisions.md` *Creature progression source and spawn ownership* — a unique *"never receives the
  empire species fallback"*;
- `actor-hub-ssot.md` §8.2 — *"Empire CreatureType / species allocation is for empire generals only"*;
- the ideal's own exclusivity table (a unique carries 2a only).

It survived because the rule lives in three copies: the lawn's `SpeciesAllocationSource.Resolve`
(`SpeciesAllocationSource.cs:118-123`, correct — Bound branch returns before the species lookup), the
web squad build (`WebMatchService.cs:600-603`, correct — commander + unique only), and the world-turn
provider (wrong). A copied rule drifts; that is the SOLID-S / DRY defect, and the fix is one owner.

**User-visible success:** a legion unique in a district assault composes exactly what the same specimen
composes on its sheet and on the lawn (commander term + its own allocation), and a general actor composes
commander term + its empire's species. No path can answer differently, because none answers at all —
they ask. (How the two terms normalise — merged today, each alone after R16 — is not this module's
question: `species-layer-delivery` step 6.1 splits them in the one resolver every path shares, so this
module's parity test holds on both sides of that change.)

**This module moves world-turn unique values, and that is a defect correction, not a re-bless.** Removing
the leaked species term changes a battle unique's composed numbers wherever its species holds levelled
CreatureType points. It lands in this module's own commit with the red-then-green test below; a golden
that pinned the leaked term is a pin of a defect and is corrected there with that classification. It
lands **before** `species-layer-delivery` step 6.1 so world-turn uniques move only once per reason (map
§3, "Re-bless order").

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionLayerSelector|FullyQualifiedName~SpeciesAllocationSource"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ProgressionLayerSelectorGuard"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python gk-core/scripts/guard-actor-hub.py
```

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/ProgressionLayerSelector.cs` | **(new)** the pure selector |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs` | `Resolve` asks the selector; its three delegates stay (they are where values come from, not which apply). For a Bound ctx the empire is the specimen's owner, read from the injector's specimen owner map (`CheatState.cs:316`, `:322`, which `save-identity` re-types to carry `EmpireId`), not `ctx.Side` — the one behaviour change on the lawn (rule 3) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | `HubInputsFor` asks the selector — a unique member gets `commander + specimen` |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs` | `BuildSquad` asks the selector (behaviour unchanged, now structural) |
| `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs` | `Build` asks the selector (behaviour unchanged) |
| `gk-core/tests/FusionRpg.Core.Stats.Tests/Stats/Aptitudes/ProgressionLayerSelectorTests.cs` | **(new)** |
| `gk-core/tests/FusionRpg.Guard.Tests/ProgressionLayerSelectorGuardTests.cs` | **(new)** source scan |

## The contract

```csharp
namespace FusionRpg.Core.Stats.Aptitudes;

/// <summary>Which progression layers an actor carries. 2a and 2b are mutually exclusive by construction:
/// the record has one slot for "whose points", never two.</summary>
public sealed record ProgressionLayers(
    EmpireId Empire,                        // the army it fights for — the commander term's owner
    bool CarriesCommander,                  // only the save's HUMAN empire has a commander allocation today
    ProgressionOwner Owner);                // exactly one of: Specimen(instanceId) | Species(speciesId) | None

public abstract record ProgressionOwner
{
    public sealed record Specimen(string InstanceId) : ProgressionOwner;   // layer 2a
    public sealed record Species(string SpeciesId) : ProgressionOwner;     // layer 2b, read against Empire
    public sealed record None : ProgressionOwner;                          // no species resolved
}

public static class ProgressionLayerSelector
{
    /// The mechanism declares the source (decisions.md "Creature progression source"): never inferred
    /// from a typeId. `empire` is the actor's empire: for a general, from the ONE side mapping
    /// (SpeciesAllocation.EmpireForSide / KillAttribution.EmpireOf); for a specimen, its OWNER empire
    /// (rpg_unique_actors.empire_id, save-identity G5) — never inferred from its side. `humanEmpire` is
    /// HumanEmpireOf(save): code never assumes the human empire is "dave" (save-identity Decision 2).
    public static ProgressionLayers Select(
        CreatureProgressionSource source, EmpireId empire, EmpireId humanEmpire) =>
        source switch
        {
            CreatureProgressionSource.UniqueSpecimenSource u =>
                new(empire, empire == humanEmpire, new ProgressionOwner.Specimen(u.InstanceId)),
            CreatureProgressionSource.EmpireGeneralSource g =>
                new(empire, empire == humanEmpire, new ProgressionOwner.Species(g.SpeciesId)),
            CreatureProgressionSource.CommanderSource =>
                new(empire, empire == humanEmpire, new ProgressionOwner.None()),
            _ => throw new ArgumentOutOfRangeException(nameof(source), source, "unknown progression source"),
        };
}
```

Rules the implementation keeps:

1. **The input is `CreatureProgressionSource`** (`CreatureProgressionSource.cs:8-75`, the closed
   `creature.progression.v1` grammar). A world member with an `InstanceId` is a
   `UniqueSpecimen`; a general spawn is `EmpireGeneral`. A caller that cannot name a source does not
   call — it composes nothing from progression, and that is reported, never defaulted.
2. **The empire is passed in, not recomputed.** For a **general**, the lawn passes
   `SpeciesAllocation.EmpireForSide(ctx.Side)` (`SpeciesAllocation.cs:38-39`) and battle passes
   `KillAttribution.EmpireOf(...)` (`KillAttribution.cs:58-116`), which T4.3 already asserts agrees with
   it. For a **specimen**, the caller passes the specimen's owner empire (`save-identity` G5:
   `rpg_unique_actors.empire_id`), because ownership is data, not side: a human-owned zombie-species
   unique fights for the human empire and carries its commander term (R4: the side's commander applies
   side-wide). Until `save-identity` lands the owner column, every specimen with a human owner row maps to
   `humanEmpire` and a Zomboss-minted one (`RpgStore.ZombossDeploy.cs:42-47`) to `EmpireId.Zomboss` — the
   same answer, read from ownership rather than side. No third mapping.
3. **`CarriesCommander` keeps today's answer, typed by ownership** (`SpeciesAllocationSource.cs:114-116`,
   `RpgStore.WorldTurns.cs:573-576`): only the save's human empire has a commander allocation. The
   `empire == CommanderId.Dave` literal in both places becomes `empire == HumanEmpireOf(save)`
   (`save-identity` X9). Zomboss's commander allocation is `empire-progression`'s work (its W7).
   **Behaviour change, named:** the sheet today hands a zombie-side human-owned unique the human
   commander term (`UniqueActorHubCompose.cs:48-49`, no side check) while the lawn withholds it
   (`SpeciesAllocationSource.cs:114-116`, side check). Keying by owner makes both paths agree with the
   sheet — the owner's commander — which the parity test below pins.
4. The selector decides **which**, never **how much**. Values still come from the existing loaders
   (`LoadAllocationUnlocked`, `EffectiveSpeciesAllocationUnlocked`, the injector caches).

## Code Style

The world-turn provider after the fix — the whole point is that it no longer contains a rule:

```csharp
HubInputsFor = member =>
{
    if (string.IsNullOrWhiteSpace(member.InstanceId)) return null;   // unchanged: generals here get nothing (map §5, Wild)

    var save = new SaveId(header.PlayerId);                          // rpg_worlds.player_id IS the save (R17)
    var owner = SpecimenOwnerUnlocked(db, member.InstanceId!);        // EmpireRef from rpg_unique_actors (G5)
    var layers = ProgressionLayerSelector.Select(
        CreatureProgressionSource.UniqueSpecimen(member.InstanceId!, occurrenceId: "world-turn"),
        owner.Empire, HumanEmpireOf(save));

    var aptitude = layers.CarriesCommander
        ? LoadAllocationUnlocked(db, AllocationScope.Commander, CommanderScopeKey(new EmpireRef(save, layers.Empire)))
        : AptitudeAllocation.Empty;
    aptitude += layers.Owner switch
    {
        ProgressionOwner.Specimen s => LoadAllocationUnlocked(db, AllocationScope.UniqueCreature, s.InstanceId),
        ProgressionOwner.Species g => EffectiveSpeciesAllocationUnlocked(db, new EmpireRef(save, layers.Empire),
                                         g.SpeciesId, AptitudeTuningHub.Tuning),
        _ => AptitudeAllocation.Empty,
    };
    return new BattleHubInputs { Aptitude = aptitude };
};
```

Naming: `Select`, `ProgressionLayers`, `ProgressionOwner` — the words of the layer stack, not of a mode.
`CommanderScopeKey(EmpireRef)` is `save-identity` X9's one encoder (the persisted `player:{save}` string is
unchanged); the literal `$"player:{header.PlayerId}"` (`RpgStore.WorldTurns.cs:575`) is retired with it.
The `aptitude +=` merge above builds **one allocation object** holding scopes; how each scope normalises is
the resolver's rule (`species-layer-delivery` step 6.1), not this provider's.

## Testing Strategy

- **Core, the selector** (`ProgressionLayerSelectorTests`): the full matrix over the closed source
  vocabulary (3 variants, pinned **because it is a closed vocabulary the code owns**,
  `validation-ssot.md`) × the two **relations** an empire can have to the save — *is the human empire* /
  *is not* — six cells, each asserting `Owner` and `CarriesCommander`. The set of empires is **not**
  pinned: under `commander-identity` `EmpireId` is an open id and a save's empires are authored rows
  (`new-save-empires.v1.json`), a population. An unknown source subtype throws.
- **Data, the regression for C1:** a district-assault member with an `InstanceId` whose species has a
  levelled CreatureType row composes **commander + specimen and nothing from the species** — asserted by
  comparing the `BattleHubInputs.Aptitude` points by scope (`TotalForScope(AllocationScope.CreatureType) == 0`).
  Verified to fail against the current `RpgStore.WorldTurns.cs:590`.
- **Parity:** for one specimen, the aptitude input built by the lawn source (Bound ctx), the web squad
  build, the world-turn provider and `UniqueActorHubCompose.Build` are equal by scope and points — for a
  plant-side **and** a zombie-side human-owned unique (the owner rule above).
- **Guard** (`ProgressionLayerSelectorGuardTests`, source scan, lives in `FusionRpg.Guard.Tests`
  because it must run in CI): outside `ProgressionLayerSelector.cs` (new), no production file under `src/`
  both loads `AllocationScope.UniqueCreature` and calls `EffectiveSpeciesAllocation*` in the same member.
  That is the structural shape of C1; the guard fails on it rather than on a count.
- Existing pins stay green unchanged: `Bound_entity_resolves_commander_plus_unique_never_the_species_lookup`,
  `Bound_unique_sharing_a_species_id_with_a_general_never_inherits_empire_shares`,
  `A_lawn_zombie_never_inherits_the_players_commander_or_species_allocation`.

## Numeric

No new magnitude. Allocations are `long` points summed with `checked` (`AptitudeAllocation.cs:129-137`);
nothing here multiplies.

## Tunables

None. The selector is a structural rule (which layer), not a balance number.

## Seedsmith / generator

No generator involved.

## ActorHub gate

Consumes nothing and composes nothing: it chooses which existing allocation reaches the existing
`AptitudeSubsystem` (`rpg.aptitude`, GG-49 `aptitude.{share}`). No private fold.

## Boundaries

- **Always:** pass a declared `CreatureProgressionSource`; pass a general's empire from the one side
  mapping and a specimen's from its owner; pass `HumanEmpireOf(save)`, never a literal; run the four-path
  parity test; land before `species-layer-delivery` step 6.1.
- **Ask first:** giving Zomboss's empire a commander term (that is `empire-progression`'s W7); giving a
  general world-battle member (no `InstanceId`) any 2b term (map §5 — Wild faction is an open category
  question).
- **Never:** infer the source from a `typeId`; let any path compose `specimen + species` for one actor;
  add a second empire mapping.

## Success Criteria

- [ ] `ProgressionLayerSelector` exists in Core; the six-cell matrix is pinned with its reason.
- [ ] A district-assault unique receives no CreatureType points (C1 closed), verified red-then-green.
- [ ] The four compose paths produce equal aptitude input for the same specimen.
- [ ] The guard fails on a reintroduced `UniqueCreature + EffectiveSpeciesAllocation` pairing.
- [ ] `guard-actor-hub.py` green.

## Open Questions

None. C1 is a technical defect against a locked decision, not a business question.

## Rulings applied 2026-09-18 (strengthen pass)

- **R3 / R17 (`save-identity` G5, X9):** a specimen's empire is its owner's; the human empire is asked
  for, never assumed; the commander key goes through the one `EmpireRef` encoder.
- **R4:** the side's commander term applies whoever leads — `CarriesCommander` is per empire, not per
  leader.
- **R16:** unchanged here by design; the split lives in the one resolver (`species-layer-delivery` 6.1),
  so this module's four-path parity holds before and after it.

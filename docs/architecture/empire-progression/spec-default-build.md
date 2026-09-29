# Spec: `default-build`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave A** · depends on:
[`assign-ladder`](spec-assign-ladder.md). **Rulings honoured:** R-Q3 (*"default auto-assign, player may
overwrite"*), `species-progression-ideal.md` R-S1 (*"if unique unit have no equipment, is literally a
general unit with same level and same stats/passive skill distribution"*). **Status:** spec, not
reviewed, no build authorized.

## Objective

A unique specimen the player has never built should fight with its species' build, not with nothing.
Today it fights with nothing: its `UniqueCreature` allocation is empty until the player allocates by
hand, while a **general** creature of the same species already gets its species favour for free.

| | General creature (species scope) | Unique specimen (today) |
|---|---|---|
| Silent default | ✅ compute-at-read baseline: override first, else plan shares × species budget (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:216-238`) | ❌ none. `LoadAllocation(UniqueCreature, id)` read raw at every seam |
| Baseline math | `SpeciesAllocation.Baseline` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocation.cs:59`) | `UniqueCreatureAllocation.Baseline` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/UniqueCreatureAllocation.cs:43`) is **built, tested, and has no production caller** |

R-S1 makes the gap a defect, not a missing feature: with no equipment, a unique *is* a general unit
with the same distribution. This module wires the baseline that already exists, through the ladder
that `assign-ladder` built, behind **one** resolver.

It also gives `systemCopy` its producer (W4): the orphan preset kind at
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:53,193` becomes "a copy of the build the game
suggested".

**Out of scope, deliberately:** the player's own commander pool. See map D1 for the reason.

## Design

### One resolver, compute-at-read (map D1, D2)

```csharp
// gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs — beside EffectiveSpeciesAllocation
public EffectiveAllocation EffectiveUniqueAllocation(string instanceId, AptitudeTuning tuning); // (new)

public sealed record EffectiveAllocation(                                                        // (new)
    AptitudeAllocation Allocation,
    bool IsDefault,             // true: no explicit allocation; this is the ladder's suggestion
    string? DefaultRuleId,      // the winning ladder rung when IsDefault
    IReadOnlyList<AssignSkip> Skipped);
```

Resolution, identical in shape to the species path:

1. **Explicit wins.** `LoadAllocation(UniqueCreature, instanceId)` with a total above zero is returned
   as-is. It is never topped up (map D2).
2. **Else the ladder.** Build an `AssignContext` from the specimen: its species from
   `rpg_creature_profiles` (the unambiguous link, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:355-365`),
   that species' plan row, the posture of its primary aptitude, and the active preset binding for
   `(unique, instanceId)` if one exists. Call `AssignLadder.Suggest`.
3. **Points by the scope's own math.** A distribution rung goes through
   `UniqueCreatureAllocation.Baseline(rows, specimenLevel, tuning)`. The `active-preset` rung goes
   through `AptitudePresetMaterialize.Materialize` at the same budget, as preset activation already
   does.
4. **Never persisted.** Nothing is written, so changing the plan or the tuning changes every default at
   once, and no migration ever exists.

A never-levelled specimen stays empty by construction: `UniqueCreatureSourceFromLevel(1) = 0`
(`gk-core/src/FusionRpg.Core/Stats/Aptitudes/PointBudget.cs:53`), so the budget is zero.

### Every reader goes through it

Measured 2026-09-18, the production reads of this scope:

| Seam | Today |
|---|---|
| Sheet and injector hydrate (`GET /api/aptitudes/unique/{id}`, read by `gk-fusion/src/FusionRpg.Injector/RpgClient.cs:606`) | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:127` |
| Server Hub compose for a specimen | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:53` |
| Web battle, two sites | `gk-core/src/FusionRpg.Server/WebMatchService.cs:416`, `gk-core/src/FusionRpg.Server/WebMatchService.cs:603` |
| Siege member | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:585-586` |

Each becomes a call to `EffectiveUniqueAllocation` (the siege one to an `...Unlocked` sibling inside
its transaction, the established pattern at `RpgStore.Aptitudes.cs:212-216`). Re-measure with
`grep -rn "AllocationScope.UniqueCreature" src` at build: any production read that bypasses the
resolver is a defect, and a Guard test enforces it (Testing 5).

### The sheet shows it is a default

`ProjectUniqueState` gains `isDefault` and `defaultRuleId`, so the sheet can say *"Suggested build
(species favour)"* and the player knows an explicit allocation will replace it. This mirrors
`HasSpeciesOverride` (`RpgStore.Aptitudes.cs:280-285`) for the species scope.

### Allocating over a default is free

A unique allocation has no respec price today (`gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:64-93`
saves without spending). Replacing a default is not a respec, because nothing was spent, and that stays
true. **Amended 2026-09-18 by ruling R18:** a *later* change that takes points back out of a specimen's
explicit allocation is priced, through [`specimen-respec-price`](spec-specimen-respec-price.md), which
compares against the stored explicit allocation and never against this default. So the first explicit
allocation over a default remains free.

### `systemCopy` producer (W4)

| Route | Effect |
|---|---|
| `POST /api/aptitude-presets/suggested` (new) `{ playerId, scope, scopeKey, name? }` | Copies the ladder's current suggestion for that scope into the player's preset library as a `kind = "systemCopy"` preset, named after the winning rung unless `name` is given. Refused past `softMaxPresets` exactly as a player preset is |

The preset's rows are the suggestion's permille rows. After the copy it is the player's to edit. The
kind records provenance only and grants nothing.

### Cache triggers — §2.16, the full set

The injector's per-Bound-specimen allocation cache (`unique-lawn-wire`) is keyed by `instanceId`. A
default moves when any input moves:

| # | Trigger | Why the effective allocation changes | Refresh |
|---|---|---|---|
| T1 | Explicit allocate or clear | explicit replaces default, or back | existing `AptitudesUpdated(unique)` (`AptitudeEndpoints.cs:91`) |
| T2 | Preset activate | the `active-preset` rung wins | existing broadcast (`gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:339`) |
| T3 | **Specimen level-up** (new trigger) | the budget grows, so the default's points grow | **new**: every server seam that can return `levelsGained > 0` for a specimen broadcasts `AptitudesUpdated(unique, instanceId)`: lawn capture ingest, expedition collect (`RpgStore.Expeditions.cs:318`), the debug award route (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:115`) |
| T4 | Bind (key-set edge) | the specimen enters the cache's key set | existing `unique-lawn-wire` bind refresh |
| T5 | Plan or tuning change | the distribution or rates change | server restart only; both are loaded at boot |

T3 is the one that did not exist before, and it is the trap §2.16 describes: nothing about an
allocation changed, yet the resolved value did. Each trigger gets its own test (Testing 4).

## Seedsmith / generator

**None.** The default reads the committed `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`
(`gk-forge/tools/CreatureBuildPlanGen` output). A diversity change there reaches every default through
Wave B with no change here.

## Tunables

None new. Rates are `aptitudes.v{n}.json` `pointEconomy` (already read by
`PointBudget.PointsFor`, `PointBudget.cs:64-72`); the ladder order is `assign-ladder`'s key;
`softMaxPresets` is `aptitude-presets.v1.json`.

## ActorHub gate

**Contributes through the existing aptitude seam, no new subsystem.** The default is an
`AptitudeAllocation` in `AllocationScope.UniqueCreature`, delivered into the same `BattleHubInputs.Aptitude`
and sheet compose as an explicit one. Its contributions carry the existing GG-49 id
`aptitude.{share}` (`gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs:61`). No private fold,
and no second resolver per mode: every mode calls the one method.

**The ownership row holds.** `decisions.md` "Creature progression source": a unique uses its own
`UniqueCreature` allocation and never the empire species fallback. The default is computed **in the
unique's own scope at the unique's own level**; it reads the species only to pick a *distribution*,
exactly as R-S1 says. No species *points* reach a unique.

## Integer widths and the power ladder

`long` for budgets and points, `checked` multiply, largest remainder, all inherited from
`UniqueCreatureAllocation.Baseline` (`UniqueCreatureAllocation.cs:57-79`). The budget is
`PointBudget`'s existing scope rate. No new curve and no new `f(level)`.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EffectiveUnique"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~UniqueAllocationReader"
# golden movement is expected: run the suite once at module end (crosses Core, Data and Server)
.\scripts\test-fast.ps1 -AllDefault
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs` | `EffectiveUniqueAllocation` + `...Unlocked` sibling |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/EffectiveAllocation.cs` (new) | the result record |
| `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` | `ProjectUniqueState` reads the resolver; `isDefault`, `defaultRuleId` |
| `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | read the resolver |
| `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs` | `POST /suggested` |
| level-up seams listed under T3 | broadcast |
| `gk-core/tests/FusionRpg.Data.Tests/Aptitudes/EffectiveUniqueAllocationTests.cs` (new) | resolver |
| `gk-core/tests/FusionRpg.Guard.Tests/UniqueAllocationReaderGuardTests.cs` (new) | no bypassing read |

## Code style

```csharp
internal EffectiveAllocation EffectiveUniqueAllocationUnlocked(
    SqliteConnection db, string instanceId, AptitudeTuning tuning)
{
    var explicitAllocation = LoadAllocationUnlocked(db, AllocationScope.UniqueCreature, instanceId);
    if (explicitAllocation.TotalForScope(AllocationScope.UniqueCreature) > 0)
        return new EffectiveAllocation(explicitAllocation, IsDefault: false, null, []);   // D2: wholesale

    var actor = ReadUniqueActorUnlocked(db, instanceId)
        ?? throw new InvalidOperationException($"unique actor '{instanceId}' not found");
    var suggestion = AssignLadder.Suggest(ContextFor(db, actor), AptitudePresetTuningHub.Tuning.AssignLadder);
    var points = suggestion.RuleId == AptitudeAutoAssignRules.ActivePreset
        ? MaterializeAtBudget(suggestion.Rows, actor.Level, tuning)
        : UniqueCreatureAllocation.Baseline(ToPermille(suggestion.Rows), actor.Level, tuning);
    return new EffectiveAllocation(points, IsDefault: true, suggestion.RuleId, suggestion.Skipped);
}
```

## Testing strategy

1. **The default exists.** A specimen at level > 1 with no explicit allocation resolves non-empty, with
   the distribution of its species' plan row and points summing to its budget. The row is read from
   the committed plan by id; the test asserts the relation, never a literal point value.
2. **Explicit replaces wholesale.** One explicit point replaces the whole default (D2).
3. **Level 1 is empty.** A fresh specimen resolves empty, `IsDefault = true`.
4. **Each cache trigger T1–T4 has its own test**, and T1/T3 are **order-independent**: allocate then
   level up, and level up then allocate, both end on the right effective value (§2 corollary).
5. **Guard: no bypass.** A Guard test fails if a production file outside the resolver reads
   `LoadAllocation(Unlocked)?(… UniqueCreature …)`. The allowlist is the resolver and the allocate
   write path only.
6. **The ownership row.** A specimen's resolved allocation contains no `CreatureType`-scope points.
7. **`systemCopy`.** `/suggested` writes one preset of kind `systemCopy` whose rows equal the current
   suggestion; the soft cap refuses as for player presets.
8. **Goldens.** A battle or expedition fixture holding a levelled specimen with no explicit allocation
   now composes that specimen's default. Each moved golden is listed with that explanation before it is
   re-blessed. A golden that moves for any other reason stops the module.

## Boundaries

- **Always:** one resolver; compute at read; explicit wins wholesale; broadcast on every T1–T4 edge.
- **Ask first:** persisting a default; extending a silent default to the commander pool; changing the
  budget rate.
- **Never:** give a unique `CreatureType` points; read the raw allocation at a new seam; price the first
  explicit allocation over a default.

## Success criteria

- [ ] `UniqueCreatureAllocation.Baseline` has production callers, through the resolver only.
- [ ] Every production reader of the unique scope calls the resolver (Guard green).
- [ ] The sheet shows a default as a default.
- [ ] `systemCopy` has a producer.
- [ ] Full suite green at module end; every moved golden explained.

## Open questions

None. The commander-pool exclusion is a scoping decision with its reason recorded in map D1.

## Self-audit — the debate

- **"This silently changes every existing save's specimens."** It does, and it is the ruling. A save
  whose specimens were deliberately left empty loses nothing it chose: an explicit allocation still
  wins, and an empty *choice* was not expressible before this module either (empty meant "never
  built"). If the owner wants "keep empty" to be a choice, it is a flag on the explicit allocation, not
  a reason to drop the default.
- **"R-S1 says *same stats*, but the unique's budget rate differs from the species rate."** R-S1's test
  is the *distribution*; the rates per scope are the shipped point economy (`commander smallest, unique
  largest`, `decisions.md` Class system row). Equal stats would require equal rates, which nobody ruled.
- **"When Wave B regenerates the plan, every default build changes under the player."** Yes, for
  specimens the player never built, and that is D1's point: a default is the game's current suggestion,
  not a saved choice. A built specimen is untouched. The sheet labels a default as a default, so the
  change is never mistaken for the player's own build moving.
- **"Zomboss's own specimens get defaults too."** They do (`MintForZomboss`,
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:42`, mints them under his player row), and that is
  correct: an AI empire has nobody to click, which is R-Q3's first case. **R3 (2026-09-18,
  [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):** Zomboss stops being a player row, and his specimens belong to his empire of the save,
  `(SaveId, EmpireId)`. The resolver keys by the specimen, not by its owner, so the default is unaffected;
  the re-homing of his mints is `solid-enforcement` `save-identity`'s.
- **"The active-preset rung and preset activation both exist."** Activation writes an explicit
  allocation today (`RpgStore.AptitudePresets.cs:387`), so after activation rung 1 is shadowed by rule 1
  (explicit wins). The rung matters for a binding that exists without a write, and it keeps the ladder
  one contract for every scope.

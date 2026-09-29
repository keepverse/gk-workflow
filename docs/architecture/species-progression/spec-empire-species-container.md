# spec — `empire-species-container`

**Module 5 of `species-progression`** ([map](../species-progression-map.md)). Depends on
`layer-source-selector`, `species-layer-projector`, and external `solid-enforcement` `save-identity`
(the `(SaveId, EmpireId)` key, R3). **Q1 answered by R2** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
2b resolves alone. Status: spec, 2026-09-18, rulings R1–R3 applied the same day. No build authorized
until the map is reviewed.

## Objective

Persist layer **2b** as the owner ruled it: *"2b is a per-`(empire, species)` container, re-projected
when that species levels — for the player's empire and for Zomboss's alike"*, with *"the allocation math
demoted from runtime contributor to projector"* (`actor-layer-compose-ideal.md` OQ1, ruled 2026-09-16;
`decisions.md` Actor layer stack: *"Every layer is a CONTAINER"*). R-S1 fixes what the container holds —
**allocation**, the same aptitude-shaped points a specimen gets, over the species' plan shares — and R-S3
fixes that it is built by the one projector (module 3).

Concretely: for each `(empire, species)` with a non-empty 2b allocation, one `species-progression.*`
container exists, projected by `SpeciesLayerProjector.ProjectEmpire`, and it is **re-projected exactly
once** whenever an input changes, **withdrawn** when the allocation becomes empty, and never
double-written — the care `ApplyEquipProjection` already takes for equipment
(`RpgStore.Items.cs:857-863`: diff against stored, withdraw what is no longer backed).

## What the container holds — 2b alone (R2)

The owner ruled R2: *"Each species container resolves only its own points; the commander is its own
layer. General actors' numbers change once, with one explained re-bless."* So this module projects
`species(save, empire, speciesId)` **alone**. The commander allocation stays where it is, in
`rpg.aptitude`, and normalises over its own total.

Why that moves numbers, stated once so the re-bless can explain it: today the lawn and battle resolve
**one merged** allocation, commander + species (`SpeciesAllocationSource.cs:114-137`, wired at
`CheatState.cs:55`; `RpgStore.WorldTurns.cs:590`), and `AptitudeAllocation.Share` divides each
aptitude's points by the **merged** grand total (`AptitudeAllocation.cs:118-122`). Splitting the two
terms makes each normalise over its own total, so every general actor whose commander **and** species
both hold points composes a different share. This module changes no composed number by itself —
nothing reads the container until `species-layer-delivery` cuts over — and the one re-bless is owned by
that cutover (its §"The cutover").

What R2 removes from this module: the container carries **no commander term**, so it never re-projects
on a commander reallocation, and the match-frozen commander (`MatchCommanderSnapshotHolder.cs:9`, read
at `CheatState.cs:89-90`) keeps working unchanged, because the commander never left `rpg.aptitude`.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpeciesContainer|FullyQualifiedName~SpeciesRespec|FullyQualifiedName~Progression"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project Structure

| Path | Change |
|---|---|
| `src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpeciesLayer.cs` | **(new)** schema, `ReprojectEmpireSpeciesUnlocked(db, tx, EmpireRef owner, speciesId)`, `ReconcileEmpireSpeciesLayers()` (boot, every save × `EmpiresOf(save)`), `ListEmpireSpeciesLayers(SaveId)` (read for delivery: every empire of the save) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` | `TryApplyXpUnlocked` (`:169`; re-typed to take an `EmpireRef` by `save-identity`) re-projects in the same transaction when a `Species`-kind row's level changes — **for every empire, through this one hook** |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs` | the override write re-projects in the same transaction as the override (and, under R18, as the respec charge) |
| `gk-core/src/FusionRpg.Server/Program.cs` | boot reconcile after the content boot and tuning configuration |
| `tests/FusionRpg.Data.Tests/EmpireSpeciesContainerTests.cs` | **(new)** |

## Storage (new) — an Ask-first boundary

- Container id: `species-progression.{saveId}-{empireToken}-{kebab(speciesId)}` — the prefix is the
  new `ContainerKind` (module 3); `kebab` is the synthesizer's own rule (`RpgStore.Species.cs:257-260`),
  moved to Core by module 3, never re-spelled. The container lives in `effect_container` like every
  other container, so existing tools can list and explain it.
- A projection ledger beside it:

```sql
CREATE TABLE IF NOT EXISTS rpg_species_layer_projection (
  save_id        INTEGER NOT NULL,   -- the save that owns the empire (solid-enforcement save-identity, R3)
  empire_id      TEXT    NOT NULL,   -- EmpireId within that save (save-identity's column naming)
  species_id     TEXT    NOT NULL,
  container_id   TEXT    NOT NULL,
  source_level   INTEGER NOT NULL,   -- the species level it was projected from (read through SpeciesLevelOf)
  input_digest   TEXT    NOT NULL,   -- hash of (allocation points, aptitude tuning version, plan revision, projector revision)
  projected_utc  TEXT    NOT NULL,
  PRIMARY KEY (save_id, empire_id, species_id)
);
```

**Keyed by `(SaveId, EmpireId)`, never by a player row (R3).** An empire is not a player: the owner
ruled that *"a Save owns its empires … each keyed `(SaveId, EmpireId)`; the player row stops doubling as
an empire, and Zomboss stops being a player row"*. This module takes the key from `save-identity`
and does not define it. Until `save-identity` lands, this module does not build.

`input_digest` is what makes "re-project exactly once" checkable: a re-projection whose digest equals
the stored one is a no-op, so a replayed XP fact or a double boot never rewrites a container. The digest
includes `SpeciesLayerProjector.Revision` (new, a structural constant bumped only when the projection's
arithmetic changes, for example by `ladder-scale-parity`): without it, a projector change with unchanged
inputs would leave every stored container computed by the old arithmetic, and module 3's parity invariant
would hold in memory while failing on disk. Every `(save_id, empire_id)` must exist in `rpg_save_empires`
(`save-identity`'s join-closure contract).

## Re-projection triggers (write side) — every one enumerated

| # | Trigger | Where | Same transaction as the cause |
|---|---|---|---|
| 1 | A species level change for any empire | the **one** hook in `TryApplyXpUnlocked` (`RpgStore.Progression.cs:169`), which `save-identity` re-types to take an `EmpireRef` and which writes every empire's levels into the one re-keyed `rpg_actor_progression` (`spec-save-identity.md`: `ai-empire-species`'s separate `rpg_empire_species_progression` table *"is superseded"*). R1's two zombie XP paths — the per-placement award (`RpgStore.Progression.cs:31-51`) and run completion (`:113-120`) — both call it, so Zomboss's rows re-project here with no second hook. `ai-empire-species` decides only **which** `EmpireRef` an award names | yes |
| 2 | A CreatureType override write or respec | `RpgStore.SpeciesRespec.cs` (the path at `:150-162`). Under R18 the empire respec is priced (spend an earned free respec, or pay); the charge, the override and the re-projection commit in **one** transaction, and a refused charge writes and re-projects nothing | yes |
| 3 | Aptitude tuning version, species-build tuning, plan revision or projector revision changed since projection | boot reconcile (digest mismatch), over every save and every empire of `EmpiresOf(save)` | n/a — boot |
| 4 | The allocation became empty | any of the above | yes — the container and its ledger row are **removed**, never left empty |

A commander reallocation is **not** a trigger: under R2 the container holds no commander term.
**Save creation** is not one either: a new save has no species levels, so there is nothing to project
(trigger 4's empty case). **R19:** a species level-up also credits the empire-level track
(`empire-progression` `empire-level`) in the same transaction; both writes read the same level change and
neither reads the other's output, so their order inside the transaction is irrelevant.

`LevelChangePipeline` (`RpgProgression.cs:257-285`) was considered for trigger 1 and rejected: its
handlers are Core, and a re-projection writes SQL inside the causing transaction, which Core may not
hold (`guard-dal.py`).

## Scope rules

- **Zomboss's empire (R1):** zombie species XP credits Zomboss's empire, so his species levels are
  written under `(SaveId, EmpireId.Zomboss)` through the same `TryApplyXpUnlocked` (routed there by
  `empire-progression` `ai-empire-species`), and trigger 1 fires for them exactly as for the player's. Today nothing writes one (`RpgStore.Aptitudes.cs:229-233`,
  `:266-267`), so until that module lands there are **no** Zomboss containers — the honest `Empty`. Zomboss
  has no override surface (`RpgStore.SpeciesRespec.cs:155-157`), so trigger 2 never fires for him.
- **A unique never has one.** 2b containers are keyed by `(empire, species)`, not by actor; which actors
  read them is `layer-source-selector`'s rule, applied by module 6.
- **Level 1 has no container:** `PointBudget.CreatureTypeSourceFromLevel` gives 0 points at level 1
  (`SpeciesAllocation.cs:49-58`), so the allocation is empty and trigger 4 applies.

## Code Style

```csharp
internal void ReprojectEmpireSpeciesUnlocked(
    SqliteConnection db, SqliteTransaction tx, SaveId save, EmpireId empire, string speciesId)
{
    // R2: the species term alone. No commander term is ever added here.
    var owner = new EmpireRef(save, empire);
    var allocation = EffectiveSpeciesAllocationUnlocked(db, owner, speciesId, AptitudeTuningHub.Tuning);
    var digest = EmpireSpeciesLayerDigest.Of(allocation, AptitudeTuningHub.Tuning,
        SpeciesBuildPlanCatalog.Revision, SpeciesLayerProjector.Revision);
    var stored = ReadProjectionUnlocked(db, save, empire, speciesId);
    if (stored?.InputDigest == digest) return;                       // exactly once

    if (allocation.TotalForScope(AllocationScope.CreatureType) == 0)
    {
        RemoveProjectionUnlocked(db, tx, save, empire, speciesId);   // withdraw, never leave an empty container
        return;
    }
    var rows = SpeciesLayerProjector.ProjectEmpire(empire, speciesId, allocation,
        AptitudeTuningHub.Tuning, DerivedStatRegistry.CreateDefault());
    UpsertProjectionUnlocked(db, tx, save, empire, speciesId,
        SpeciesLayerProjector.ToContainer(rows), digest);
}
```

(`SpeciesBuildPlanCatalog.Revision` is **new** — the catalog is loaded once from the committed plan
(`SpeciesBuildPlanCatalog.cs:13-25`); its content hash is the revision. `SaveId` comes from
`save-identity` and `EmpireId` from `commander-identity`; both are unbuilt. Today's
`EffectiveSpeciesAllocationUnlocked` takes `(playerId, speciesId, tuning, CommanderId)`
(`RpgStore.Aptitudes.cs:214-239`); its re-key to `EmpireRef` is `save-identity`'s migration, and its level
read goes through `ai-empire-species`'s `SpeciesLevelOf(SaveId, EmpireId, typeId)` over the one re-keyed
`rpg_actor_progression`. `empire` is `commander-identity`'s `EmpireId`, which replaces the `CommanderId`
enum `RpgStore.Aptitudes.cs:216` takes today.)

## Testing Strategy

- **Exactly once:** replaying the same XP fact, or booting twice, leaves one container and one ledger
  row with an unchanged `projected_utc`.
- **Each trigger, one test each** (triggers 1–4): cause → container content changes to match
  `ProjectEmpire` of the new allocation.
- **No commander term (R2):** a commander reallocation leaves every species container and its
  `input_digest` untouched.
- **Withdraw:** a species reset to level 1 (demotion path) removes its container.
- **Zomboss (R1):** with no Zomboss rows, a reconcile writes no Zomboss container; after a zombie species
  is credited to Zomboss's empire through `ai-empire-species`'s writer, one appears under
  `(save, zomboss)` and nothing appears for Dave's empire.
- **Two saves (R3):** a container projected for save A's Zomboss does not exist for save B.
- **Both zombie XP paths (R1):** a zombie spawn fact and a zombie run completion each re-project Zomboss's
  container through the one `TryApplyXpUnlocked` hook. No second hook exists, asserted by a source scan:
  no call to `ReprojectEmpireSpeciesUnlocked` outside that hook, the respec path and the boot reconcile.
- **Projector revision:** bumping `SpeciesLayerProjector.Revision` with unchanged inputs re-projects every
  container at the next boot.
- **R18:** a refused respec charge leaves the override, the container and its digest untouched.
- **Content equality:** the persisted container's atoms, read back through the container store and the
  module 3 reader, resolve to the same modifiers as `ProjectEmpire` in memory (persistence is lossless).
- No test asserts how many species or containers exist.

## Numeric

Points `long`, `checked` sums; coefficients `long` via module 3; `source_level` `long` in C# (the column is
SQLite `INTEGER`). No new magnitude arithmetic.

## Tunables

None new. Inputs: `aptitudes.v{n}.json`, `species-build.v1.json`, `species-progression.v1.json`
(XP curve for the level). No per-species number is authored in `gk-core/data/tuning` (owner ruling 2026-09-16,
`actor-layer-compose-ideal.md` Tunables).

## Seedsmith / generator

Reads `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, produced by `gk-forge/tools/CreatureBuildPlanGen`
(`SpeciesBuildPlanner`). No generator change. After any plan regeneration
(`dotnet run --project gk-forge/tools/CreatureBuildPlanGen`, CI runs `-- --check`), trigger 3 re-projects at the
next boot — the container is derived state and is never hand-edited.

## ActorHub gate

Persistence only. The container reaches the fold through module 6's registered subsystem with
`species-empire:{empireToken}:{speciesId}:{aptitudeId}` SourceIds. `DerivedModifier`s are never persisted
(`decisions.md` ActorHub row: *"Ban: persist Derived / AppliedCombat … as SQLite SSOT"*) — the container
holds projected rows (allocation-derived coefficients), not composed values.

## Boundaries

- **Always:** re-project in the causing transaction; compare digests before writing; remove on empty.
- **Ask first:** the two schema additions.
- **Never:** persist a composed value; project from another layer's output; write a Zomboss row this
  module did not receive from a real writer.

## Success Criteria

- [x] Q1 answered: R2, 2b resolves alone ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)).
- [ ] Every levelled `(empire, species)` has exactly one container equal to its current projection.
- [ ] All enumerated triggers re-project exactly once, each with a test.
- [ ] An emptied allocation leaves no container.

## Open Questions

None.

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md). Not reopened here.

- **R2 (was OWNER Q1):** 2b resolves alone. The container projects the species term only; the
  merged-reading trigger (commander reallocation) is retired; the one re-bless belongs to
  `species-layer-delivery`'s cutover.
- **R1 (was OWNER Q2):** zombie species XP goes to Zomboss's empire, written by `ai-empire-species`;
  trigger 1 covers his rows.
- **R3 (was OWNER Q3):** storage keyed `(SaveId, EmpireId)` from `solid-enforcement` `save-identity`,
  never a player row. That module is now a dependency. The column is spelled `empire_id`; trigger 1 is the
  one `TryApplyXpUnlocked` hook for every empire (the separate AI table is superseded there).
- **R18/R19 (strengthen pass):** the priced empire respec commits charge + override + re-projection in one
  transaction; a species level-up's empire-level credit is independent of the re-projection.

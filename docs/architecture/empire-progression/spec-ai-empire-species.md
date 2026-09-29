# Spec: `ai-empire-species`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave D** · depends on:
[`assign-ladder`](spec-assign-ladder.md), external `solid-enforcement`
[`commander-identity`](../solid-enforcement/spec-commander-identity.md) (`EmpireId`) and external
`solid-enforcement` `save-identity` (`SaveId`, R3). **OWNER question 1 is answered by R1**
([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)): zombie species XP goes to Zomboss's
empire. The only gates left are the two external modules. **Status:** spec, BUILT IN PART
(2026-09-21): EP4.13-EP4.17 landed (the one species-level reader, R1's two crediting paths, the level
reads, Zomboss's `ActorIndexFor`, the one empire-keyed commander-pool read) and EP4.18 landed trigger T5
only - the side-wide wire and the R23 golden commit stay OPEN, see the program todo. Not reviewed as a
whole; rulings R1 and R3 applied 2026-09-18; **ruling R23** applied the same day (session
`rulings-r20-r24-20260918`): this module also owns **Zomboss's commander pool default**, read side-wide
for his members — § *Zomboss's commander pool — R23*. For that half it also depends on
`species-progression` [`zomboss-commander-clock`](../species-progression/spec-zomboss-commander-clock.md)
(the level) and lands after `species-progression` `species-layer-delivery` step 6.1 (per-layer resolve
and weight).

## Objective

Close **R1**: the AI empire owns no species progression, while the human's row levels zombie species
the human never fields.

Read in code:

| Fact | Where |
|---|---|
| **Before EP4.14/EP4.15 landed** (kept as the module's own starting point; the state below has since been replaced — see § *Landed*): a non-Dave empire resolved Empty for species allocation, in both paths | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs` (the two `empire != EmpireId.Dave` branches; the file has since grown, so cite by symbol, not line) |
| The reason, in the code's own words: *"the species LEVEL row is per-player, and no Zomboss species level exists anywhere"* | the same two branches (both comments are gone as of EP4.15) |
| The level row was `(player_id, kind = species, creatureTypeId)`, with no empire in its key | `rpg_actor_progression`; `save-identity` SE4.20 re-keyed it to `(save_id, empire_id, …)` |
| Species run-completion XP credits `playerId` for every fielded species, zombie side included | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:105-120` |
| The side-to-empire mapping already exists, as one function | `gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs:58-59` → `SpeciesAllocation.EmpireForSide` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocation.cs:38-39`) |
| The override key already carries the empire | `SpeciesAllocation.ScopeKey` (`SpeciesAllocation.cs:28-31`) |
| Zomboss has no workbench, correctly | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:155-157` |

So the missing pieces are: **somewhere to store** a non-player empire's species level, **the crediting
rule** R1 fixes (a fielded species earns for its side's empire), and **the read** that stops returning
Empty.

## The rulings this module builds (R1, R3)

*Naming note:* the Objective's **R1** is the ideal's gap id; the rulings below are rows of
`spec-rulings-2026-09-18.md`. The labels coincide, and so do the subjects: ruling R1 closes gap R1.

**R1** answers OWNER question 1 (the ideal's open question 2, the same shape as `SR-18`): *"Zomboss's
empire. Plant species progress for the player's empire, zombie species for Zomboss's."* It is an economy
decision, and its consequence is stated plainly: the human's zombie species rows **stop growing** from
zombie spawns and zombie run completions. They are left as history, never rewritten.

**R3** answers where an empire's rows live: *"A Save owns its empires (Dave's, Zomboss's, later AI),
each keyed `(SaveId, EmpireId)`; the player row stops doubling as an empire, and Zomboss stops being a
player row."* So every key below is `(SaveId, EmpireId)`. `save-identity` defines `SaveId` and the
migration of today's player-keyed rows; this module consumes both and re-specifies neither.

## Design

### Storage — one reader, no migration

```csharp
namespace FusionRpg.Data;

/// The one place code asks "what level is this species, for this empire, in this save?"
public long SpeciesLevelOf(SaveId save, EmpireId empire, int creatureTypeId);   // (new) on RpgStore
```

- **Every empire reads one table** (reconciled 2026-09-18 with
  [`save-identity`](../solid-enforcement/spec-save-identity.md), which made that call): `rpg_actor_progression`
  is rebuilt once to `(save_id, empire_id, …)` by save-identity's backed-up migration, and existing rows land
  on `(SaveId, EmpireId.Dave)`, so every existing save keeps its species levels byte for byte. **No separate
  `rpg_empire_species_progression` table** — two tables for one concept would be a Dave-special storage
  branch. This module owns only the reader/credit writer over that table; the rebuild is save-identity's.
- **Why not Zomboss's player row.** `EnsureZombossPlayer` finds one global row by name
  (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs:25-29`). Levelling species on it would leak one
  save's war into every other save, and R3 retires Zomboss as a player row altogether.

Every species-level read goes through `SpeciesLevelOf`. A Guard test forbids a direct
`GetRpgActor(…, RpgActorKinds.Species, …)` outside it, so two storages never become two readers.

### Crediting — R1

The empire of a fielded species is `KillAttribution.EmpireOf(side)` (`gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs:58-59`),
the existing single mapping. The save is the run's save, resolved through `save-identity`. Both species
XP paths change, because both credit the human's `playerId` today:

| Path | Today | Under R1 |
|---|---|---|
| Per-placement award (`zombie_spawn` → species award, `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs:68-71`, applied at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:31-45`) | `TryApplyXpUnlocked(db, playerId, …)` | a zombie species award credits `(save, EmpireId.Zomboss, typeId)` in the re-keyed `rpg_actor_progression` (`save-identity`); a plant species award is unchanged |
| Run completion (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:113-120`) | every fielded species credits `playerId` | each fielded species credits its side's empire of the run's save; plants unchanged |

The human's existing zombie species rows are left as history, never rewritten. The dedupe keys stay as
they are (`run-complete:{runId}:{speciesId}` and the run-scoped fact key), so a replay credits once. A
run whose save cannot be resolved credits nothing and is reported, never a guessed save. The credit
writer runs in the causing transaction and is what fires `species-progression`
`empire-species-container`'s trigger 1 for Zomboss's rows.

### Reading — the default for an empire with no workbench

With a level available, the two guards that used to return Empty for a non-Dave empire **are level reads as
of EP4.15** (`RpgStore.Aptitudes.cs`, the `SpeciesLevelOfUnlocked` call in
`EffectiveSpeciesAllocationUnlocked` and the `SpeciesLevelOf` call in `SpeciesBaselineAllocation`), and the
effective allocation is the one the ladder picks for a scope
with no preset: **species favour**, applied by `SpeciesAllocation.Baseline` at the empire's species
level. That is the "writer for a non-Dave empire" the ideal asked for (§4): not a workbench, an
assigner. The override half stays Dave-only because only a player has a respec surface.

### Zomboss's commander pool — R23

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


R23: *"Zomboss's commander pool (`zomboss:{save}`), levelled by his commander clock: assign-ladder default and side-wide effect like the player's pool (R4)?"* — **"Yes, mirror the player. Symmetric empires."** The map's gap *"Zomboss's commander allocation (the ideal's W7) has no owner"*
is owned here.

**Today** Zomboss's side gets no commander term on any path: the lawn resolver hands a non-Dave empire
`AptitudeAllocation.Empty` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs:110-116`), so
does the world-turn/siege seam (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:571-576`), and nothing
writes his key (`zomboss:{playerId}`, `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:71`).

**The mirror, piece by piece:**

| Player's pool (as shipped / ruled) | Zomboss's pool (R23) |
|---|---|
| Keyed `player:{id}` today (`CommanderId.cs:70`), `(SaveId, EmpireId.Dave)` after `save-identity` (map X9) | Keyed **`(SaveId, EmpireId.Zomboss)`** per [`spec-save-identity.md`](../solid-enforcement/spec-save-identity.md) — the `zomboss:{playerId}` string (keyed under the **human** row, save-identity D3) is re-keyed by that migration, never by this module |
| Budget = `PointBudget` commander rate × `Θ_player` (`AptitudeEndpoints.cs:46-47`, `:158-159`) | Budget = the same `PointBudget.PointsFor(AllocationScope.Commander, …)` (`PointBudget.cs:64`) over **Zomboss's Θ**, composed by the **same** composer as `Θ_player`: `ServerPowerIndexProvider.ReadSnapshot` builds `new ActorLadderSnapshot(daveLevel, RealmsAdvanced: 0, PvzRuns: 0)` and hands it to `PowerIndexComposer.ActorExplain` (`gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs`, `ActorIndex` at `:37` and `ActorIndexFor` at `:54` — LANDED, EP4.16); Zomboss's budget feeds that composer `new ActorLadderSnapshot(CommanderLevelOf(save, EmpireId.Zomboss), 0, 0)` (`zomboss-commander-clock`'s read seam). **Wiring gap, not a new curve** (verified 2026-09-18): the provider reads only `ctx.PlayerId` and the hydrated cache keys by player only (`IPowerIndexProvider.cs:76`), so this module adds one empire-keyed read `ActorIndexFor(SaveId, EmpireId)` (new) beside `ActorIndex`, composed by the existing `ActorExplain` — no `ssot-power-scale.md` §10 row is needed. **Magnitudes on the lawn are unchanged:** lawn zombies still read the player's Θ plus `lawn-tuning-profile`'s tunable offset (its 2026-09-16 ruling); this Θ sets only the size of Zomboss's commander point budget |
| Allocated by hand (map D1: no silent default for the player's own sheet) | **Computed at read, never persisted** (map D1's *"nobody to click"* covers an AI exactly): `AssignLadder.Suggest` ([`assign-ladder`](spec-assign-ladder.md)) with the commander context — no active preset (an AI has no preset surface), no species, no posture — so the walk records those skips and lands on `even` today; an `active-preset` binding authored for his pool later wins with no code change. Points by the same largest-remainder permille→points math the silent default already uses (`assign-ladder`'s consumer table) at that budget — no third rounding function. An explicit allocation under his key (none exists; he has no workbench, `RpgStore.SpeciesRespec.cs:155-157`) would win wholesale (map D2) |
| Applies **side-wide** to every member of his side (ruling R4); a leading creature adds only its aura | Applies **side-wide** to every Zomboss-side member on every path that today hands them Empty — lawn (`SpeciesAllocationSource.cs:114-116`) and world-turn/siege (`RpgStore.WorldTurns.cs:573-576`); a leading Zomboss creature adds only its aura (R4 mirrored) |
| Resolves alone (R16) and is scaled by the commander layer weight (R21) | Same: it is a `Commander`-scope allocation, so `AptitudeResolver` resolves it alone and applies `read.layerWeightMilliByScope.commander` — no Zomboss branch in the resolver |

**One resolver, two empires.** The read is one function taking `(SaveId, EmpireId)`: for Dave it returns
his explicit allocation unchanged (D1 — no silent default for the player's own pool); for any non-player
empire it returns explicit-else-ladder-default. The two `empire == CommanderId.Dave ? … : Empty` branches
above are replaced by that one call, never by a second Zomboss-specific reader.

**Golden impact (stated before the build).** Today every Zomboss-side actor's commander term is `Empty`.
After this change, any actor on Zomboss's side whose save has a Zomboss empire with a **non-zero
commander budget** gains `aptitude.{Share}` contributions (`ContributionSourceIds.Aptitude`), so its
composed values move once. That is **a new layer delivered** (the same class as `species-layer-delivery`
step 6.2), not a re-bless of existing values: the commit lists every moved pin with the SourceIds that
caused it. A pin whose Zomboss side resolves no save empire, or a zero budget, is byte-identical — any
move there is a defect. It lands **after** `species-layer-delivery` step 6.1 so 6.1's one re-bless table
never has to explain a Zomboss commander term, and the move is never counted twice. Plant-side (Dave)
values do not move.

### Cache triggers — §2.16

The injector's species cache (`spec-allocation-transport.md`) sends only species the player has
levelled. It now also carries the AI empire's levelled species, keyed by `(empire, speciesId)` within the
save (R3). `species-progression` `species-layer-delivery` carries the same rows as projected 2b; this
table's triggers are the ones it inherits.

| # | Trigger | Refresh |
|---|---|---|
| T1 | AI empire species level-up (new) | `AptitudesUpdated` gains an optional `empire` field (additive, the transport spec's own rule); the crediting transaction's caller broadcasts it |
| T2 | Session start, reconnect | existing |
| T3 | Match edges | existing |
| T4 | Key-set edge: a zombie species reaching level 2 for the first time enters the sent set | covered by T1, since that level-up is what adds the key; its own test proves it |
| T5 | **Zomboss commander level-up** (R23, new) — his budget grows, so his pool default grows | the `zomboss-commander-clock` award's caller broadcasts `AptitudesUpdated` with `empire = zomboss` (the same additive field as T1); the lawn's commander cache for his side refreshes |
| T6 | Assign-ladder order or aptitudes tuning publish (R23) | boot-time load, as every tuning read; no runtime trigger (compute-at-read, D1) |

## Seedsmith / generator

**None.** Runtime attribution and reads. The species favour it applies is the committed plan.

## Tunables

None new. Budget rates are `aptitudes.v{n}.json`'s `CreatureType` rate; XP awards are the existing
`progression.v{n}.json` and species-progression tuning.

## ActorHub gate

**Contributes through the existing species seam.** The AI empire's species allocation reaches Hub as
the `CreatureType` term of the aptitude input, where the Dave empire's already travels
(`RpgStore.WorldTurns.cs:581-583` for sieges; the lawn species transport for general spawns). GG-49 id
unchanged (`aptitude.{share}`). No new subsystem.

**Ownership row:** only **general** creatures receive this; a Zomboss-owned unique specimen uses its own
`UniqueCreature` scope (and `default-build`'s resolver), never the empire fallback (`decisions.md`
"Creature progression source").

## Integer widths and the power ladder

Levels and XP `long`, as `rpg_actor_progression` stores them. Budget by `PointBudget.PointsFor`
(`checked`). The level feeds allocation, per R-S1, never a private curve.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireSpecies|FullyQualifiedName~SpeciesAllocation"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLevelReader"
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs` (new) | `SpeciesLevelOf`, credit writer over `rpg_actor_progression` |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs` | guards become level reads (landed, EP4.15); `CommanderPoolOf`/`CommanderPoolOfUnlocked` (landed, EP4.17) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` | the crediting branch |
| `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` | `AptitudesUpdatedDto.empire` (additive) |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs` (`:114-116`) | R23: the `Dave ? … : Empty` commander branch becomes one empire-keyed commander read |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (`:573-576`) | R23: same, on the world-turn/siege seam |
| `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderPoolTests.cs` (new) | R23 tests 10–14 |
| `gk-core/tests/FusionRpg.Data.Tests/EmpireSpeciesProgressionTests.cs` (new) | below |
| `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLevelReaderGuardTests.cs` (new) | one reader |

## Code style

```csharp
public long SpeciesLevelOf(SaveId save, EmpireId empire, int creatureTypeId) =>
    ReadEmpireActorUnlocked(db, new EmpireRef(save, empire), RpgActorKinds.Species, creatureTypeId)?.Level ?? 1;
    // one read over save-identity's rebuilt rpg_actor_progression; no branch on which empire asks
```

**No `empire == Dave` storage branch.** An earlier draft read Dave's levels from "the old row" and every
other empire's from a new table. `save-identity` superseded that (its consumer row for this module): every
empire's species levels live in the one re-keyed table, so the reader has one path.
`ReadEmpireActorUnlocked` is `save-identity`'s re-typed read (`spec-save-identity.md` §"Seams this module provides to consumers").

## Testing strategy

1. **Dave unchanged.** Every existing species-allocation test passes untouched; a Dave read returns the
   level its row held before `save-identity`'s migration, byte for byte.
2. **Two saves, two wars (R3).** Crediting Zomboss's empire in save A leaves save B's empire level at 1.
   The key is `(SaveId, EmpireId)`; no test keys by a player row.
3. **Empty until earned.** A never-credited AI species resolves Empty (level 1 → budget 0), so no
   golden moves before XP flows.
4. **The default applies.** An AI species at level > 1 resolves its plan's distribution at that level.
5. **Replay.** A replayed run-completion credits once.
6. **Cache triggers T1 to T4**, each tested, T4 order-independent against a match edge.
7. **Guard:** no direct species-level read outside `SpeciesLevelOf`.
8. **R1, both paths:** a zombie spawn fact and a zombie run completion each grow Zomboss's empire row
   and never the human's; a plant spawn and a plant run completion grow the human's, unchanged.
9. **Unresolved save:** a run with no resolvable save credits nothing and reports.
10. **R23, the default:** Zomboss's pool at a non-zero budget resolves `AssignLadder.Suggest`'s
    distribution for the commander context (skips recorded) and its points sum to the budget; at a zero
    budget it resolves Empty; nothing is written to `rpg_aptitude_allocation` (read back through
    `LoadAllocation`, byte-identical).
11. **R23, side-wide:** every Zomboss-side actor — a lawn zombie general, a lawn Zomboss Bound unique and a
    world-turn/siege member — carries his pool as a `Commander`-scope contribution
    (`aptitude.{Share}`); every plant-side actor carries Dave's, never his.
12. **R23, keying (R3):** save A's Zomboss pool never reaches save B's actors; the read takes
    `(SaveId, EmpireId.Zomboss)` and uses both.
13. **R23, Dave unchanged:** the player's own pool still has no silent default (map D1) — an empty Dave
    pool stays Empty.
14. **R23, golden classification:** a test whose Zomboss side resolves no save empire or a zero budget is
    byte-identical before and after.

## Boundaries

- **Always:** one level reader; empire from `KillAttribution.EmpireOf`; history never rewritten.
- **Ask first:** any change to the human's existing species rows. (No new table: storage is save-identity's rebuilt `rpg_actor_progression`.)
- **Never:** level species on the global Zomboss player row or on any player row for a non-player
  empire; give the AI empire a respec surface; rewrite the human's existing zombie species rows.

## Success criteria

- [x] OWNER question 1 answered: R1 ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)).
- [x] Both zombie species XP paths credit Zomboss's empire of the run's save (EP4.14).
- [x] `SpeciesLevelOf` is the only species-level reader (EP4.13/EP4.15; the Guard's allow-list still names `RpgStore.Aptitudes.cs`, whose entry now matches no read - shrunk by the manager, see the EP4.13 addendum).
- [x] The Empty guards are gone; an AI empire's levelled species composes its favour (EP4.15).
- [~] Every trigger in the table tested: T1-T4 by the cache-trigger guard, T5 by EP4.18's Server test; T6 has no runtime trigger by design (boot-time load).
- [~] R23, IN PART: the pool read resolves the ladder's computed default at his commander budget, keyed
      `(SaveId, EmpireId.Zomboss)`, never persisted, and applies side-wide to his members on the lawn and
      the world-turn/siege seam; the moved pins are listed in the commit as a new layer delivered.

## Open questions

None for the owner. The build waits on `save-identity` (`SaveId`, the run→save mapping, the migration of
the player's existing species rows) and `commander-identity` (`EmpireId`).

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md). Not reopened here.

- **R1 (was map question 1):** zombie species XP credits Zomboss's empire. The "no" branch is deleted;
  both XP paths are re-routed.
- **R23 (was map Q-S1):** Zomboss's commander pool mirrors the player's — the assign-ladder computed
  default at his commander level's budget, applied side-wide to his members (R4 mirrored), keyed
  `(SaveId, EmpireId.Zomboss)`; § *Zomboss's commander pool — R23*.
- **R3:** every empire-owned row is keyed `(SaveId, EmpireId)` from `solid-enforcement` `save-identity`.
  The separate `rpg_empire_species_progression` table this spec first proposed is **superseded**: every
  empire reads the one `rpg_actor_progression` that `save-identity` rebuilds.

## Self-audit — the debate

- **"Two tables for one concept is the dual-store defect."** It would have been; that is why the second
  table was dropped when `save-identity` rebuilt `rpg_actor_progression` with the empire in its key. One
  table, one reader (`SpeciesLevelOf`), and the Guard test keeps it that way.
- **"Re-key the credit now and wire the read later."** Shipping the credit without the read would level
  Zomboss's species while his allocation still resolves Empty, a mechanism whose content is a constant, the
  ideal's named fourth neutral stub. R1 settled the branch, so the credit and the read ship together, once
  `save-identity` gives them a key.
- **"The Guard test forbids the progression writer's own reads."** The writer (`TryApplyXpUnlocked`,
  `EnsureActorRowUnlocked`) reads the row it is about to update; that is a write path, not a level read.
  The Guard allowlists the progression writer and `SpeciesLevelOf` by name, and nothing else.

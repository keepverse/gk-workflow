# spec — `species-layer-delivery`

**Module 6 of `species-progression`** ([map](../species-progression-map.md)). Built in **three ordered
steps**, each with its own dependencies (strengthen pass, 2026-09-18):

| Step | What | Depends on | Moves composed numbers? |
|---|---|---|---|
| **6.1** | Per-layer resolve (R2 + R16) in the one aptitude resolver — **the one explained re-bless** | module 1 (`layer-source-selector`, C1 landed); `action-enrich` `action-base`'s golden re-bless landed | **yes — the only step that re-blesses** |
| **6.2** | 1a core + 1b delivery through `rpg.species-layer` | module 4 (`species-mod-ledger`) | adds new layers' contributions (new SourceIds); not a re-bless (see §"What each step may move") |
| **6.3** | 2b cutover: the species term leaves the aptitude allocation and arrives as `species-empire:` rows | module 5 (`empire-species-container`) | **no** — value-neutral by module 3's parity invariant |

**Q1 is answered by R2** and extended to 2a by **R16** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
commander, species and specimen each resolve only their own points, and this module owns the one
explained re-bless that causes. Status: spec, 2026-09-18, rulings R1–R3 and R16 applied the same day,
strengthened the same day. No build authorized until the map is reviewed.

## Objective

Make layers 1a (species-passive core), 1b and 2b reach **every** compose that should carry them, through
**one** registered `IActorStatSubsystem`, and retire the paths they reach today:

| Compose path | Today | After |
|---|---|---|
| Lawn general actor | 2b as allocation math inside `rpg.aptitude` (`CheatState.cs:55`, `SpeciesAllocationSource.cs:125+`), **merged** with the commander into one share (`SpeciesAllocationSource.cs:137`); no 1a core, no 1b | commander resolves alone (6.1); 1a core + 1b of its empire + 2b rows via `rpg.species-layer` (6.2, 6.3); the species term leaves the aptitude allocation |
| Lawn Bound unique | commander + unique allocation **merged** (`SpeciesAllocationSource.cs:122`); no 1a core, no 1b | commander and 2a each resolve alone (R16, 6.1); + 1a core + 1b of its **owner empire** via `rpg.species-layer` (6.2) |
| Sheet (`UniqueActorHubCompose`) | commander + unique **merged** (`UniqueActorHubCompose.cs:84`); T4.6 joined the eager roll as `BoundDerivedAtom`s (`UniqueActorHubCompose.cs:65-68`) | each resolves alone (6.1); that join removed; 1a core + 1b via `rpg.species-layer` (6.2) |
| Battle unique (world turn, web squad) | commander + unique **merged** (`RpgStore.WorldTurns.cs:590`, species term removed by module 1; `WebMatchService.cs:602-603`); no 1a core, no 1b | each resolves alone (6.1); + 1a core + 1b via `BattleHubInputs.SpeciesLayers` (new field, 6.2) |
| Battle general member (no `InstanceId`) | nothing — `HubInputsFor` returns `null` for it (`RpgStore.WorldTurns.cs:561`) | unchanged. Giving world forces any layer is a world-battle change, and which empire a Wild-faction force belongs to is an open category (map §5) |

**R-S1 is honoured, not bent.** *"Reuses `SpeciesAllocationSource` wholesale"* is about **what** a species
level grants — that source's allocation, over the plan shares — and that does not change. What moves is
**where** it resolves (the 2026-09-16 container ruling): into a projected container read by one
subsystem, instead of into the aptitude allocation.

The owner's acceptance sentence is the target: *"the plant/zombie in lawn run that spawned will get their
empire's specie progression, the final stats will be base specie stats + progression stats"* (ideal,
"What this is"). For plants this module makes it true. For zombies it delivers exactly what Zomboss's
empire owns: under R1 zombie species XP credits Zomboss's empire (`empire-progression`
`ai-empire-species`), so a lawn zombie carries its 2b rows once that module has credited any. Until
then the zombie half is the honest `Empty`, by missing data, not by missing design.

**Units already on the board get the change.** The Age of Empires lesson the ideal adopted (*"apply to
units already on the board, not only to future spawns"*) is a cache-trigger requirement, enumerated below.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerSubsystem|FullyQualifiedName~SpeciesAllocationSource|FullyQualifiedName~BattleHubCompose"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger|FullyQualifiedName~SpeciesAllocationCacheTrigger"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Aptitude|FullyQualifiedName~Sheet"
# step 6.1 (the re-bless) additionally — see §"Step 6.1", procedure step 1
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests|FullyQualifiedName~ModeComposeParity|FullyQualifiedName~AptitudeResolver|FullyQualifiedName~PointBudget|FullyQualifiedName~ContributionSourceIds"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore|FullyQualifiedName~WorldTurn"
python gk-core/scripts/guard-actor-hub.py
python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python gk-core/scripts/probe_perf.py --scenario <lawn-300z-scenario-id> --duration-sec 60
```

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/SpeciesLayerSubsystem.cs` | **(new)** `SubsystemId "rpg.species-layer"`, `Order 100` (the progression band `rpg.aptitude` already uses — not a new band, `actor-hub-ssot.md` §6) |
| `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs` | `ActorHubBootstrap.CreateDefault` (`:141`) gains an opt-in `speciesLayers` delegate, same shape as `aptitudeAllocation` / `boundDerivedAtoms` |
| `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs` | **(new field)** `IReadOnlyList<ProjectedLayerRow>? SpeciesLayers` |
| `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs` | passes it through; Θ is the existing `FixedPowerIndexProvider(setup.ThetaActor ?? setup.Level)` |
| `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` | the `/api/aptitudes/{playerId}` response (`:155-178`) gains `speciesLayers` (see Transport) |
| `gk-fusion/src/FusionRpg.Injector/RpgClient.cs` | the same fetch (`:554-569`) parses `speciesLayers` and calls `CheatState.ApplySpeciesLayers` |
| `gk-fusion/src/FusionRpg.Injector/CheatState.cs` | the cache, wholesale replace + `Stats.Invalidate()`; the delegate wired into `ActorHub` (`:49`) |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeResolver.cs` | **step 6.1:** `Resolve` resolves **each `AllocationScope` present alone** — share taken over that scope's own total (`AptitudeAllocation.ShareWithinScope`, a pure addition made by whichever of module 3 or step 6.1 lands first) — and concatenates. The merged `Share` (`AptitudeAllocation.cs:118-122`) loses its only production reader (`AptitudeResolver.cs:36`) and is removed unless the build finds another reader |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuning.cs` | **step 6.1 (R21):** parses `read.layerWeightMilliByScope`; a PRESENT block refuses a missing scope key, an unknown scope key, or a negative weight by name; a totally ABSENT block resolves every scope to 1000 (unweighted identity) — corrected 2026-09-19 against evidence, see below |
| `gk-core/src/FusionRpg.Server/Program.cs` (`:247`), `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` (`:185`) | **step 6.1 (R21):** the literal `aptitudes.v8.json` readers move to the published revision in the same commit |
| `data/tuning/aptitudes.v{n+1}.json` | **step 6.1 (R21):** published by `gk-core/tools/tuning/publish.py` (`--add-key read:layerWeightMilliByScope=…`), never hand-written |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs` | **step 6.1:** the class comment *"Scopes sum before share, never the reverse"* (`:17-21`) is rewritten to the per-layer contract |
| `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs` | **step 6.1:** `Aptitude(scope, share)` — `aptitude.{Share}` for `Commander` (unchanged, so no commander attribution moves), `aptitude.{scopeText}.{Share}` for the other scopes. `scopeText` is the one scope↔text mapping, moved from `RpgStore.ScopeToText` (`RpgStore.Aptitudes.cs:53-60`) to Core beside `AllocationScope`; Data delegates to it (one vocabulary, not two) |
| `gk-fusion/src/FusionRpg.Injector/CheatState.cs` (comment `:51-54`) | **step 6.1:** the comment *"one merged AptitudeAllocation, one resolve, never two scopes resolved separately"* states the retired contract; rewritten in the same commit |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs` | **step 6.3:** the species term removed from the returned allocation for a general ctx (R2, below) |
| `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs`, `WebMatchService.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` | **step 6.2:** feed 1a core + 1b rows for uniques (their aptitude inputs need no edit in 6.1: the resolver splits them) |
| `gk-core/src/FusionRpg.Server/EventIngest.cs`, `FusionEndpoints.cs` | after commit, broadcast through the one emitter `AptitudeEndpoints.BroadcastBestEffort` (`AptitudeEndpoints.cs:107-119`, which already reaches the injector group) with kind `"species"`: from `EventIngest` when the progression dirty set holds a `Species`-kind level change (it already broadcasts `RpgProgressionUpdated` to the web group only, `EventIngest.cs:240`), and from `/execute` (`FusionEndpoints.cs:30`) after a fusion appends a ledger row. The Data layer never broadcasts |
| `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` | **(new)** |

## The subsystem

```csharp
public sealed class SpeciesLayerSubsystem : IActorStatSubsystem
{
    readonly Func<StatContext, IReadOnlyList<ProjectedLayerRow>> _rowsFor;
    readonly IPowerIndexProvider _powerIndex;
    readonly PowerLadder _ladder;
    // one slot per rows-reference; recomputed only when Θ or the reference changes
    readonly Dictionary<IReadOnlyList<ProjectedLayerRow>, (int Theta, IReadOnlyList<DerivedModifier> Mods)> _memo =
        new(ReferenceEqualityComparer.Instance);

    public string SubsystemId => "rpg.species-layer";
    public int Order => 100;

    public void ContributeDerived(StatContext ctx, ICollection<DerivedModifier> mods)
    {
        var rows = _rowsFor(ctx);
        if (rows.Count == 0) return;
        var theta = _powerIndex.ActorIndex(ctx);
        if (!_memo.TryGetValue(rows, out var hit) || hit.Theta != theta)
            _memo[rows] = hit = (theta, SpeciesLayerProjector.Resolve(rows, _ladder.Value(theta)));
        foreach (var m in hit.Mods) mods.Add(m);
    }
}
```

- **Θ is read per resolve, never stored in the cache** — the same freshness the aptitude path has today
  (`AptitudeSubsystem.cs:97-110`). Projected rows are Θ-free (module 3), so a Θ change needs **no**
  trigger.
- Every emitted modifier carries the row's GG-49 SourceId (`species-base:` / `species-player:` /
  `species-empire:`); an empty SourceId is skipped, as `AtomDerivedSubsystem` does
  (`AtomDerivedSubsystem.cs:59-61`).
- The memo is bounded by the number of distinct row lists the cache hands out (one per
  `(empire, species)` plus one per Bound unique's `(owner, species)`), never by actor count.

## Which rows an actor gets — `layer-source-selector` decides

| Selector answer | Rows |
|---|---|
| `Species(speciesId)` for empire E of save S | 1a core of `speciesId` + 1b of `(S, E, speciesId)` + 2b of `(S, E, speciesId)` |
| `Specimen(instanceId)` | 1a core of its species + 1b of `(S, owner empire, its species)` — the owner empire is the specimen's own `rpg_unique_actors.empire_id` (`save-identity` G5), never inferred from its side (never 2b) |
| `None` | nothing |

1b is **empire-scoped**, not player-scoped (`save-identity` G3: the empire whose resources paid for the
pick). 1b of Zomboss's empire is empty by design (no ledger rows — Zomboss does not fuse). 2b of
Zomboss's empire is empty until `ai-empire-species` credits his species (R1), keyed
`(SaveId, EmpireId.Zomboss)` (R3).

## Transport (lawn) — one fetch, as today

The injector already receives every species term through **one** fetch, and T4.2 proved its trigger
set complete *because* there is one (`spec-species-empire-scope.md` §"The enumerated set"). This module
extends **that** fetch — it does not add a second one:

```jsonc
// GET /api/aptitudes/{playerId}  — path value = SaveId (save-identity); existing fields unchanged
"speciesLayers": {
  "saveId": 1,                                                  // the save these rows belong to
  "base":   { "<speciesId>": [ /* ProjectedLayerRow */ ] },   // 1a core — global
  "mod":    { "<empireId>": { "<speciesId>": [ ... ] } },       // 1b, per empire of this save (G3)
  "empire": { "<empireId>": { "<speciesId>": [ ... ] } }        // 2b, every empire of EmpiresOf(save) (R1, R3)
}
```

The route is keyed by `playerId` today (`AptitudeEndpoints.cs:155-178`). `save-identity` rules the path
value **is** the `SaveId` and that this one fetch serves every empire of `EmpiresOf(save)`
(`spec-save-identity.md` "Contracts"). Empire keys are `EmpireId` values from `rpg_save_empires`, never a
literal `{dave, zomboss}` list. This module adds no second route and no second key.

`CheatState.ApplySpeciesLayers` replaces the whole cache (never merges) and calls `Stats.Invalidate()`,
matching `ApplySpeciesAllocations` (`CheatState.cs:198`).

## Cache trigger set (DESIGN-GATE §2.16) — every trigger, each with a test

This cache is the **same** cache T4.2 enumerated, with the same key-set behaviour (keyed by
`(empire, speciesId)`, empire derived from `ctx.Side` at read time, fed by one fetch). Its three
triggers are therefore inherited, not copied from a different cache. What this module adds are the
edges where the **server-side rows** change mid-session, which the allocation cache never needed because
nothing re-projected:

| # | Trigger | Where | New? | Test |
|---|---|---|---|---|
| 1 | Session start | `RpgClient.StartAsync` | inherited | extend `Trigger1_session_start_refreshes_the_species_cache` to assert `speciesLayers` |
| 2 | SignalR reconnect | `_hub.Reconnected` | inherited | extend `Trigger2_…` |
| 3 | `AptitudesUpdated` broadcast | `aptitudes.allocation.reload` → `CheatState` | inherited | extend `Trigger3_…` |
| 4 | **A 2b re-projection committed** (module 5 triggers 1–4) — a species of **either** empire levels **mid-run** (a zombie species now levels Zomboss's empire, R1) | server broadcasts `AptitudesUpdated(kind "species")` after commit | **new** | `A_species_level_up_mid_run_reaches_actors_already_on_the_board`, once per side |
| 5 | **A 1b ledger append committed** (a fusion) | same broadcast | **new** | `A_fusion_pick_reaches_actors_already_spawned` |
| 6 | **The save the lawn plays changes — the key-set edge (R3).** Every row in this cache belongs to one save (`speciesLayers.saveId`); a save switch replaces the whole key set at once | `save-identity`'s T2 signal for `PUT /api/players/current` (`gk-core/src/FusionRpg.Server/Program.cs`, which broadcasts nothing today) — **one** signal shared with the empires cache, never a species-specific second one. If a run is open, the rows of the run's save stay until that run ends (`decisions.md` "Mid-match switch": *"Open run keeps the player it started with"*), and the refresh applies at the next `board.start` | **new** | `A_save_switch_replaces_every_species_layer_row`, in **both orders** (hydrate→switch, switch→hydrate), plus `A_mid_run_save_switch_keeps_the_runs_rows_until_the_run_ends` |
| 7 | **A 2b re-projection by the boot reconcile** (module 5 trigger 3: tuning or plan revision changed) | boot precedes any injector session, so trigger 1 already carries it | inherited through trigger 1 | covered by trigger 1's test; named so it is not re-derived |
| — | Refresh reaches live entities | `ApplySpeciesLayers` → `Stats.Invalidate()` | inherited shape | `Applying_species_layers_invalidates_live_stats` |
| — | Wholesale replace | `_speciesLayers = parsed` | inherited shape | `A_refresh_replaces_the_whole_layer_cache` |
| — | **Θ is not a trigger** | rows are Θ-free, Θ read per resolve | — | `Theta_is_never_cached_in_species_layers` — fails if a Θ-resolved value is ever stored |

**The key-set edges, answered.** Two dimensions of the key, two answers:

1. **Which empire an actor reads never moves on state** (derived per read from `ctx.Side` for a general,
   from the specimen's owner empire for a unique — T4.2's `The_key_set_edge_is_resolved_per_read_…` still
   holds for the side half). Under R1 the set of empires the cache answers for is every empire of the
   save from the first build, not the human empire widened later. So
   `The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another` is **replaced**, in this
   module, by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other`: a zombie ctx reads
   only Zomboss's rows, a plant ctx only the human empire's, and a Zomboss row never reaches a plant. The
   first Zomboss credit is trigger 4 (it is a re-projection), so no further trigger is owed for it.
2. **Which save the rows belong to moves on a save switch** — trigger 6. T4.2 needed no such trigger
   only because its rows were one player's; under R3 the cache is a save's, and a switch is the edge
   where every key moves at once (the §2.16 trap). T4.2's
   `A_match_edge_is_not_a_species_trigger_and_the_trigger_set_was_not_copied` is **amended**, not kept:
   a `board.start` that follows a mid-run save switch **is** this cache's edge; any other match edge
   still is not.

**Order independence (DESIGN-GATE §2.16 corollary).** Level-up-then-spawn and spawn-then-level-up must
both end with the actor carrying the new rows; both orders are tested (trigger 4 covers the second).

**Tests live in `FusionRpg.Guard.Tests`**, beside `SpeciesAllocationCacheTriggerTests`, because
`FusionRpg.Injector.Tests` is not in CI (`AGENTS.md`).

## Step 6.1 — the one explained re-bless (R2 + R16, one ordered change)

R2: *"General actors' numbers change once, with one explained re-bless."* R16: *"2a resolves alone too
… the same one-explained-re-bless procedure covers uniques."* Both rulings are the same rule — each
layer's points normalise over their own total — so they land as **one** change in **one** place.

**The mechanism: one seam, every path at once.** `AptitudeAllocation.Share` divides by the grand total
of every scope it holds (`AptitudeAllocation.cs:118-122`), and its only production reader is
`AptitudeResolver.Resolve` (`AptitudeResolver.cs:36`), which every compose path reaches through
`rpg.aptitude`. Step 6.1 changes that one resolver to resolve **each `AllocationScope` present alone**
and concatenate. No compose path is edited to do it, so no path can be missed: the lawn general, the lawn
Bound unique, the sheet, the web squad and the world-turn unique all split in the same commit.

| Path | Allocation it builds (unchanged by 6.1) | Moves in 6.1 when |
|---|---|---|
| Lawn general actor | commander + species (`SpeciesAllocationSource.cs:137`) | both terms hold points (R2) |
| Lawn Bound unique | commander + unique (`SpeciesAllocationSource.cs:122`) | both terms hold points (R16) |
| Sheet | commander + unique (`UniqueActorHubCompose.cs:84`) | both terms hold points (R16) |
| Web squad unique | commander + unique (`WebMatchService.cs:602-603`) | both terms hold points (R16) |
| World-turn unique | commander + unique, after module 1 removes the species term (`RpgStore.WorldTurns.cs:590`) | both terms hold points (R16) |

An actor with at most one non-empty scope is **byte-identical**: a single-scope share is the same number
merged or alone. `Aspect` has no production source today (`PointBudget.cs:13-16`), so it moves nothing;
when a source lands it resolves alone like every other scope, with no new ruling.

**What moves, stated exactly so the table can explain it.** Both read functions depend on a layer's
**share**, never on its point total (`AptitudeReadFunctions.cs:33-44` contest, `k · share^γ · span`;
`:48-68` magnitude, `k · share^γ · P(Θ)`). So the move on one edge is
`read(share_commander) + read(share_other) − read(share_merged)`, and an actor whose two layers both hold
points gains up to one extra layer's worth of each funded edge. That is the ruling's consequence, not a
defect. It is also why the merged design weighted scopes by point rate, which resolve-alone no longer
does. **Ruled R21 (2026-09-18, closes map §7 OQ-S1): a tunable weight per layer**, applied in the same
one resolver — § *Per-layer weight (R21)* below. The weight ships **in** 6.1, so the re-bless stays one.

### Per-layer weight (R21) — the class-system intent kept as data

R21: *"A tunable weight per layer (commander, species, specimen) in tuning, so the intent is kept as
data; step 6.1's re-bless measures it."* The intent is the one in `decisions.md` — 'Class system (2026-08-26)': *"commander smallest, unique
largest — a commander allocation replicates across the whole roster, so a dominant one is the worst
case"*, which the merged denominator carried implicitly and resolve-alone drops.

**Where it is applied — the one resolver, nowhere else.** `AptitudeResolver.Resolve`
(`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeResolver.cs:23`) already computes one value per funded edge
(`:46-48`). In 6.1 it loops per `AllocationScope` present, and multiplies each edge's read value by that
scope's weight before emitting the `DerivedModifier` (`:60-61`):

```text
contest:   value = Contest(kMilli, share_scope, …) × w_scope / 1000                          (double)
magnitude: value = RoundHalfAway( checked( Magnitude(kMilli, share_scope, …, P(Θ)) × w_scope ) / 1000 )  (long)
```

The magnitude path widens before multiplying (both operands are already `long`, `AptitudeReadFunctions.cs:48`),
multiplies `checked`, and divides by 1000 once with the resolver's existing round-half-away-from-zero
per-mille helper (`ScaleMilli`, `AptitudeResolver.cs:86-90`) — no new rounding rule. The share and the
read functions are untouched: the weight scales a layer's **output**, so a layer's share stays a bounded
`[0,1]` ratio and both PS-3 reads keep their shape (one power ladder, no private curve). No compose path,
subsystem or caller learns about weights — the same one-seam argument as the split itself.

**Tuning file and keys.** One new block in the aptitudes domain, published with the tool as the next
revision (`aptitudes.v9.json` if nothing else publishes first — `gk-core/tools/tuning/publish.py` derives the
number; never an in-place edit of `aptitudes.v8.json`):

```powershell
python tools\tuning\publish.py aptitudes --add-key "read:layerWeightMilliByScope={\"commander\":500,\"creatureType\":667,\"aspect\":667,\"uniqueCreature\":1000}" --label "R21 per-layer aptitude weight"
```

- **Key:** `read.layerWeightMilliByScope`, keyed by the **same four scope names** every sibling per-scope
  table in that file already uses (`pointEconomy.aptitudePointsPerThetaMilliByScope`,
  `gk-core/data/tuning/aptitudes.v8.json:24-29`) — `commander` (commander layer), `creatureType` (species, 2b),
  `aspect` (no production source today, `PointBudget.cs:13-16`; it resolves alone when one lands),
  `uniqueCreature` (specimen, 2a). Per-mille, a **bounded ratio** (exempt from the long-magnitude rule,
  and says so in a `_note`), **not a cap**: any non-negative value loads, including above 1000.
- **Defaults, derived not guessed:** the shipped point-rate table `{3, 4, 4, 6}` (`aptitudes.v8.json:25-28`)
  is the file's own statement of the intended ordering (its `_weightsWhy`: *"Ordered commander smallest,
  uniqueCreature largest per 2.1's decision"*). Normalising it to the largest scope gives
  **commander 500, creatureType 667, aspect 667, uniqueCreature 1000** — the intent holds
  (`commander < creatureType ≤ aspect < uniqueCreature`, the same legal ordering as that file's
  `spec-point-economy.md` §7 test 3), and a specimen's own points keep their unweighted value. They are
  UNMEASURED in the same sense the rate table's are; residual-fit / squad-harness owns real values, and a
  later change is a `publish.py` publish, never a code edit.
- **Readers switched in the same commit:** `AptitudeTuning` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuning.cs`)
  parses the block; if it is PRESENT it **refuses by name** a missing scope key, an unknown scope key or a
  negative weight — never a silent partial table. Both literal `aptitudes.v8.json` readers move to the new
  revision: `gk-core/src/FusionRpg.Server/Program.cs:247` and `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:185`.
  **Corrected 2026-09-19, against evidence, not merely style:** an earlier draft additionally had
  `AptitudeLayerWeights.Of` throw at first REAL RESOLVE for a scope the table does not carry, meaning a
  file with the block totally ABSENT (every pre-R21 `aptitudes.v1`-`v8.json`) could still be *parsed*
  but could not be *resolved*. That broke every real regression fixture that deliberately pins an exact
  old file and genuinely resolves against it on purpose — `TerminationGuardTests`, `DominanceGuardTests`,
  `BossBuildTests`, `ZombossPatternTests`, `ChannelModsHubParityTests`, `DominanceBaselineTests`,
  `ProveAptitudeJsonEmitTests` all do this, to prove a numbered historical behaviour never drifts. `Of`
  now reads a missing scope as 1000 (the unweighted identity, i.e. exactly the pre-R21 read those pinned
  files were always meant to reproduce). This carries no silent-typo risk for a current, intentionally
  weighted file: `Of` only ever sees an empty table when the whole block was absent at parse — a PRESENT
  block missing one scope key still fails loudly at parse, so this default can never mask a
  half-authored weight table.

**Consequence for the re-bless classification.** With `commander` ≠ 1000, an actor whose only non-empty
scope is the commander (a lawn general before any species level) is **no longer byte-identical** — its
commander contribution is scaled. That move is R21's and is re-blessed in the same commit, classified
under R21 (procedure step 3 below). An actor whose only scope is `uniqueCreature` stays byte-identical
at the default 1000.

**Ordering against the other re-blesses (decided, strengthen pass 2026-09-18).**

1. **`action-enrich` `action-base` re-blesses first** ([spec-action-base.md](../action-enrich/spec-action-base.md)
   acceptance 4, `BattleGoldenTests`). It has no dependency and changes the damage formula itself
   (`BasicAttack.cs:369` stops reading `LiveAtk`). Aptitude edges target `progression.bonus.atk`
   (`gk-core/data/tuning/aptitudes.v8.json`), so a split re-blessed *before* it would explain `atk`-driven damage
   values that `action-base` then moves again. After it, the 6.1 table explains only channels still read.
2. **Module 1 (`layer-source-selector`) lands before 6.1.** Its C1 fix removes the leaked species term
   from world-turn uniques. That is a **defect correction** of a value a locked decision forbids
   (`decisions.md` *Creature progression source*), recorded in module 1's own commit with its
   red-then-green test; it is not a re-bless, and a golden that pinned the leaked term is corrected there
   as a defect pin. Running 6.1 first would move world-turn uniques twice.
3. **Step 6.1**, the one re-bless.
4. **Steps 6.2 and 6.3 never re-bless** (§"What each step may move").

If `action-base` has not landed when 6.1 is otherwise ready, 6.1 waits: two re-bless commits over the
same goldens in the other order is the double move R2 forbids. Each re-bless commit touches only its own
moved values and names its ruling.

**The procedure, in this order, in step 6.1's change:**

1. **Before**, on a tree where items 1 and 2 above have landed, run the scoped suites named in Commands
   plus `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGoldenTests|FullyQualifiedName~ModeComposeParity|FullyQualifiedName~AptitudeResolver|FullyQualifiedName~PointBudget"`
   and `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~AllocationStore|FullyQualifiedName~WorldTurn"`,
   and record every composed value a test or golden pins for **any** actor whose allocation holds two or
   more non-empty scopes: general, Bound, sheet, web squad and world-turn unique alike.
2. **Apply** the per-scope resolve, re-run the same suites, and list every assertion that fails.
3. **Classify each failure.** It is a re-bless **only** if the actor's allocation holds two or more
   non-empty scopes (R2/R16), **or** holds one non-empty scope whose layer weight is not 1000 (R21).
   Any other failure is a defect in 6.1 and is fixed, never re-blessed.
4. **Re-bless once**, in one commit, with a table per moved value: actor class (general / Bound / sheet /
   web squad / world-turn), channel, before, after, and **each layer's share vector and the merged share
   vector** that explain it (point totals do not explain it; see above). ⭐ **R21: the table reports the
   per-layer effect** — for each moved value, each layer's contribution **unweighted** (`w = 1000`) and
   **weighted** (the published default), and the layer weight used, so the split's move (R2/R16) and the
   weight's move (R21) are separately attributable in the one commit. A per-layer summary row (sum of
   weighted minus unweighted per scope, over every moved value) states the size of R21's effect — a
   reading, printed, never asserted.
5. **Rewrite, never re-bless, the tests whose subject is the merge.** Each pins the retired contract:
   `SpeciesAllocationSourceTests.Commander_and_species_merge_into_one_allocation`
   (`SpeciesAllocationSourceTests.cs:18`), `PointBudgetTests.Four_scopes_sum_to_the_effective_allocation`
   (`PointBudgetTests.cs:55-72`, *"Share is taken on the SUM … never per scope"*) and
   `AllocationStoreTests.ScopesSum_anActorWithBothCommanderAndCreatureType_readsTheSum_shareTakenOnTheSum`
   (`AllocationStoreTests.cs:370-385`). Each is restated as the per-layer contract: one scope's
   contribution is unchanged by adding points to another scope.
6. **No second re-bless.** A later move in the same values needs its own ruling.

No test asserts how many values moved; the table is the evidence, and its size is a reading.

**Docs owed in the same change** (outside this spec's paths; exact lines in the map §9):
`decisions.md` *Class system* row (*"`share` is taken **on the sum**, never per scope"*; amendment text
for R2/R16/R21 in the map §9),
`actor-hub-ssot.md` §8.2 (*"`commander + UniqueCreature(instanceId)`"*) and §8.1 (the per-scope aptitude
SourceId row).

## What each step may move

| Step | Composed values that may move | Classification |
|---|---|---|
| 6.1 | actors with two or more non-empty scopes (R2/R16); actors with one non-empty scope whose layer weight ≠ 1000 (R21) | **the re-bless** (above) |
| 6.2 | actors whose species has a `species-passive` core (1a) or whose empire holds a 1b row, gaining `species-base:` / `species-player:` contributions for the first time | **a new layer delivered**, not a re-bless. Asserted by the per-path tests below (which SourceId families reach the fold). A pre-existing pin that moves because a layer it never saw now arrives is listed in 6.2's commit under that class, with the SourceIds that caused it. The retired T4.6 sheet join is replaced, not added to: for a fuser the same atoms move from `species-passive:` to `species-base:` + `species-player:` with equal values (module 3's partition test); for a non-fuser the eager random roll disappears (`species-mod-ledger` behaviour 1, the ruling) |
| 6.3 | none | the cutover must be value-identical; any moved value is a defect in 6.3 |

## Step 6.3 — the cutover: no double count, no value move

For a general actor, the species term must reach the fold **once**. The cutover lands in the same change
that starts delivering 2b rows. `SpeciesAllocationSource.Resolve` returns the **commander term only** for
a general ctx (today it returns `commander + species`, `SpeciesAllocationSource.cs:137`); 2b arrives as
`species-empire:` rows from the species' own container. The commander keeps its own normalisation and
keeps following the match-frozen snapshot.

Because 6.1 already resolves the species scope alone, and module 3 proves
`Resolve(ProjectEmpire(A), P(Θ)) == AptitudeResolver.Resolve(A, …)` value for value for a species-only
allocation, the cutover changes **SourceIds only** (`aptitude.creatureType.{Share}` →
`species-empire:{empireId}:{speciesId}:{aptitudeId}`), never a value.

`A_general_actor_composes_its_species_term_exactly_once` asserts that for a general ctx no contribution
with an `aptitude.creatureType.` SourceId is present while `species-empire:` rows are (a Hub
`ResolveDerivedWithContributions` read, never a count of rows). `The_cutover_moves_no_composed_value`
asserts, for a grid of general actors (commander empty, species empty, both funded), that every channel's
composed value is equal before and after 6.3.

## Testing Strategy

- **Per path, one test each:** lawn general plant, lawn general zombie (1a core, plus Zomboss's 2b once his empire holds a levelled species, R1), Bound unique,
  sheet, world-turn unique, web squad unique — each asserts which SourceId families reach the fold, read
  back through `ResolveDerivedWithContributions`.
- **Per-layer resolve (6.1, R2 + R16):** for each of the five paths in the 6.1 table, an actor with one
  non-empty scope composes the same value before and after 6.1 (asserted); adding points to a second scope
  leaves the first scope's contributions unchanged (the per-layer contract, asserted by SourceId family);
  an actor with two funded scopes moves by exactly `read(share_a) + read(share_b) − read(share_merged)`,
  reported per channel in the re-bless table, never asserted away.
- **Per-layer weight (6.1, R21):** with a fixture weight table, each scope's contribution equals its
  unweighted read × `w/1000` (contest) or the round-half-away per-mille of the `checked` product
  (magnitude); a scope at `w = 1000` is identical to the unweighted read; changing one scope's weight
  moves only that scope's SourceId family. The loader refuses a missing block, a missing or unknown scope
  key and a negative weight, each by name. The **ordering contract** of the shipped file is asserted —
  `commander < creatureType ≤ aspect < uniqueCreature` — never the literal values (they are tunables).
- **Cutover is value-neutral (6.3):** `The_cutover_moves_no_composed_value` (above).
- **SourceIds (6.1):** a commander contribution keeps `aptitude.{Share}`; every other scope's carries
  `aptitude.{scopeText}.{Share}` and round-trips through `FictionLabel` to a non-raw label.
- **Two saves (R3):** save A's Zomboss 2b rows, and save A's 1b rows, never reach an actor in save B —
  including after a save switch (trigger 6).
- **A unique's 1b follows its owner empire, not its side (G5):** a specimen whose `empire_id` is the
  human empire reads the human empire's 1b whatever its side.
- **1b end to end (live-probe standard):** a real fusion through the real `/execute` route
  (`FusionEndpoints.cs:30`) on real specimens — no debug route, no `test.*` mint — then the lawn actor's
  composed value read back through the normal query path (`/derived` or the sheet), never from
  injector telemetry alone (`live-probe-standard.md`).
- **The trigger table:** every row above.
- **Perf:** the lawn per-hit compose stays within the budget the ideal records as closed
  (`hub.resolveDerived` 823–895 µs average, pipeline 3.46% of wall at 59.7 fps,
  `docs/research/perf/_baseline-lcw-300z-hud-resync-b60.json`); a regression is a failure to fix, never a default-off flag.

## Numeric

Values via `LadderScale.Micro` (`long`, throws past range) or contest `double`s. The Unity boundary is
unchanged: composed values reach PvZ only as deltas over `hp`/`armor1`/`armor2` through
`EntityStatWriter` (`guard-single-writer.py`); every other channel stays in the RPG layer.

## Tunables

| Key | File | Default | Owner |
|---|---|---|---|
| `read.layerWeightMilliByScope` — `commander`, `creatureType`, `aspect`, `uniqueCreature` (per-mille, bounded ratio, not a cap) | `data/tuning/aptitudes.v{n+1}.json`, published by `gk-core/tools/tuning/publish.py` in step 6.1 | 500 / 667 / 667 / 1000 — the shipped rate table `{3,4,4,6}` (`aptitudes.v8.json:25-28`) normalised to its largest scope, so *"commander smallest, unique largest"* holds (R21) | step 6.1; real values residual-fit / squad-harness |

## Seedsmith / generator

No generator involved. (Delivery reads rows modules 3-5 produced from generated inputs.)

## ActorHub gate

Contributes through **one** registered `IActorStatSubsystem` (`rpg.species-layer`) with GG-49
SourceIds minted by `ContributionSourceIds`, on every host through `ActorHubBootstrap.CreateDefault` —
the lawn, the sheet and `BattleHubCompose` register the same subsystem. No mode gets its own reader.

## Boundaries

- **Always:** extend the one fetch; test every trigger including the three new ones (4, 5, 6); land
  the cutover in the same change as 2b delivery; land 6.1 only after `action-base`'s re-bless and module
  1; explain every re-blessed value.
- **Ask first:** giving a general world-battle member any species row; any perf regression.
- **Never:** a second fetch or a poll for species layers; cache a Θ-resolved value; deliver 2b to a
  unique; let 2b reach a general actor twice; re-bless in 6.2 or 6.3; split layers anywhere but the one
  resolver (no per-path split).

## Success Criteria

- [ ] One subsystem delivers 1a core, 1b and 2b on lawn, sheet and battle.
- [ ] A fusion pick changes a real lawn actor's composed value, read back through the normal path.
- [ ] A mid-run species level-up reaches actors already on the board.
- [ ] No general actor composes its species term twice.
- [ ] The R2 + R16 re-bless landed once (step 6.1), in one commit, after `action-base`'s re-bless and
      module 1, covering general, Bound, sheet, web squad and world-turn actors, with every moved value
      explained by its share vectors; the three merge-contract tests rewritten, not re-blessed.
- [ ] Step 6.3 moved no composed value.
- [ ] A save switch replaces every row, in both orders; a mid-run switch keeps the run's rows.
- [ ] Every trigger in the table has a test that fails when its wiring is removed.
- [ ] Lawn perf within the recorded budget.

## Open Questions

None.

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md). Not reopened here.

- **R2 (was OWNER Q1):** the cutover is the standalone shape; the merged branch is deleted; the one
  explained re-bless is specified above (step 6.1).
- **R16:** 2a resolves alone too; the same step 6.1 covers Bound, sheet and battle uniques, because the
  split lives in the one resolver every path uses.
- **R21 (was map OQ-S1):** a tunable weight per layer, `read.layerWeightMilliByScope`, applied in
  `AptitudeResolver` to each layer's read output; defaults 500 / 667 / 667 / 1000 keep *"commander
  smallest, unique largest"* as data; the one 6.1 re-bless measures and reports it per layer
  (§ *Per-layer weight (R21)*).
- **R1 (was OWNER Q2):** a lawn zombie's 2b comes from Zomboss's empire; the cache answers both empires
  from the first build.
- **R3 (was OWNER Q3):** the empires a fetch serves are the save's, keyed `(SaveId, EmpireId)` by
  `solid-enforcement` `save-identity`; 1b is empire-keyed (its G3); the save switch is trigger 6.
- **R4:** the commander term applies side-wide whoever leads; the leading creature's aura is another layer
  and never enters this subsystem.

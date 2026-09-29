# Lane `ep-4` — empire-progression's remaining rows, named

**Session:** `empire-progression-4` · **Program:** empire-progression · **Mode:** worktree
**Fence:** copy of your predecessor's (`gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`,
`gk-forge/tools/CreatureBuildPlanGen/**`, `gk-forge/tools/seedsmith/**`, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/generated/**`,
`gk-data/packs/fusion/data/seed/creatures/**`, `tests/**`, `docs/architecture/empire-progression/**`, `tasks/**`)

## Take these rows, in this order

1. **`EP-F1` FIRST — a guard red this program introduced.** The manager's post-merge check found
   `ZombossCommanderLevelSingleReaderGuardTests` failing: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs`
   (added by your predecessor's EP4 batch) reads the narrow `SELECT level FROM rpg_actor_progression` shape, where
   the guard admits **one** seam, `RpgStore.CommanderLevelOf`, and `RpgStore.Progression.cs` as the only file that
   may hold that query text. Read the level through `CommanderLevelOf`; ⛔ never relax the guard or allowlist the
   file. Verify: `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter FullyQualifiedName~ZombossCommanderLevel`.
2. **`EP4.13`** — `SpeciesLevelOf(SaveId, EmpireId, typeId)`, the one species-level reader, plus its Guard test.
3. **`EP4.14`/`EP4.15`** — R1: both zombie species XP paths credit Zomboss's empire of the run's save (committed
   together); the two `Empty` guards become level reads, an AI species composes its favour,
   `AptitudesUpdated.empire` triggers.
4. **`EP4.16`** — `ActorIndexFor(SaveId, EmpireId)`: Zomboss's Θ through the existing
   `PowerIndexComposer.ActorExplain`.
5. **`EP4.17`** — the one empire-keyed commander-pool read.
6. **`EP4.18`** — wire Zomboss's pool side-wide (lawn and siege), add trigger T5, and the **R23 golden commit
   (H1, last)**.
7. **`EP5.1`/`EP5.2`** — `BuildScorer` over `Considerations.Score` (no arithmetic of its own), then publish `ai`
   (next free version) with its readers in the same commit.

Deps are in the rows; follow them rather than the number order where they disagree.

## Evidence contract (binding — the manager accepts on exactly this)

The exact command text; the numbers it printed; the committed artefact; an explicit **NOT-proved** list; and any
finding that belongs to another program **named with that program**, not fixed here. A summary is not evidence.

## Hard rules that bind every row here

- Generated data is never hand-edited — fix the generator and regenerate. Tuning is **published**
  (`gk-core/tools/tuning/publish.py`, `v{n+1}`) with its readers switched in the **same commit** (H7); never an in-place
  edit. A moved golden moves in its own commit with one named cause (H1); a migration precedes writes to a
  re-keyed table (H2).
- Never widen a guard's allowlist and never add a `knownRed` entry to make a check pass.
- Combat writes only via `EntityStatWriter`/Funnel; SQL only inside `FusionRpg.Data`; one ActorHub compose/read.
- A debug API may trigger a real operation, never fabricate its result — name the scope you are in.
- Commit per row with explicit `paths`, one logical change per commit.

## Why you are a fresh lane

Your predecessor's last four segments returned **empty output in ~12 seconds each** (measured), after four
feeds that produced no commits. That is a spent context, not a laziness judgement: the fix is a new lane with a
brief that names the work, which is what this is. Do not re-derive the program's whole history — read your todo
rows, then the code they name.

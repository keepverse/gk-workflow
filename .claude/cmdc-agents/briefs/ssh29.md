# Lane `ssh29` — strain-splice-host's remaining rows, named

**Session:** `strain-splice-host-20260922` · **Program:** strain-splice-host · **Mode:** worktree
**Fence:** copy of your predecessor's (`gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`,
`gk-forge/tools/seedsmith/**`, `gk-forge/tools/ItemSeedValidator/**`, `gk-data/packs/fusion/data/seed/**`, `gk-core/data/tuning/**`, `tests/**`,
`docs/architecture/**`, `tasks/strain-splice-host-todo.md`, `tasks/reports/**`)

## Take these rows, in this order

1. **`SSH6.4`** — the items combo-budget `--report`: it needs a **C# entry point** that builds the shipped atom
   catalog (`FamilyExpansion` over `gk-data/packs/fusion/data/seed/atoms/**`) and prices the budget; the lane that was to do it never
   started it.
2. **`SSH7.8`** — ✅ **OWNER APPROVED 2026-09-21**: drop `socket_combo_ingredient.min_tier` and
   `ComboIngredient.MinTier`, drop and re-seed the content table at boot, under **H2** (migration before writes to
   the re-keyed table). `SSH7.5`'s write-0-never-read default retires with it.
3. **`SSH5.9`** — combo-bind carries the circuit: the same word in two circuits is two contributions.
4. **`SSH4.4`**, **`SSH4.6`**–**`SSH4.9`** — one acceptance set built and upserted at boot before the seed; the
   arm-2 projection bind; `EquippedBoundAtoms` recognising combo bindings per host; every trigger refreshing the
   binding set; then the live probe (RPG Server Debug scope) on a real word on the real sheet — use the three-slot
   game pool (`gk-core/scripts/live_slot.py --acquire --session strain-splice-host-20260922`), never the owner's game.
5. **`SSH2.8`/`SSH2.9`** — the combination naming backlog repair (ledger-aware, then one re-run) and the shifted
   `combination-regen` doc citations.

⚠ `SSH4.4`/`SSH4.6` are the rows blocked on 58 shipped combination grants naming 10 families with no atom: the
corpus must be regenerated with the current catalog. Route that finding rather than hand-editing a seed.

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

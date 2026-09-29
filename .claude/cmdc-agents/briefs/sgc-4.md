# Lane `sgc-4` — species-gear-chain's remaining rows, named

**Session:** `species-gear-chain-4` · **Program:** species-gear-chain · **Mode:** worktree
**Fence:** copy of your predecessor's (`gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`,
`gk-forge/tools/seedsmith/**`, `gk-forge/tools/ItemSeedValidator/**`, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/**`, `tests/**`,
`docs/architecture/species-gear-chain/**`, `tasks/species-gear-chain-todo.md`, `tasks/reports/**`)

## Take these rows, in this order

The reconciliation (`tasks/reports/backlog-reconciliation-20260921.md` §3) measured this program at **6 open task
blocks** — not the 286 unchecked lines, which are mostly the acceptance boxes of tasks that shipped:

1. **`T57`** — `gk-core/tools/tuning/publish.py` stringifies a list-valued key (`resolutionOrder=[...]` publishes a
   *string* and reports `1 change(s)`), and one verify line selects nothing. XS/M.
2. ⛔ **`T55` is NOT yours — corrected 2026-09-22.** The manager first listed it here and that was wrong: the
   row's own text says its fix "is a registry owner's, and the file is pipeline-guarded"
   (`gk-core/scripts/verification-boundaries.v1.json`), and this lane's fence holds no `scripts/` path at all. It is
   routed to the test-verification-boundary lane that owns that file. Do not attempt it, and do not ask for a
   fence widening to reach it.
3. **`T37`** — `item-upgrade-tree` a: the executor and the per-base-type armour successor edges; **the owner
   ruled 2026-09-21: author the per-base-type edges.** Slice 3 (the production caller) needs, in ONE commit,
   `WorkbenchMutation`'s consumed/produced instance fields, the apply path in `RpgStore.Workbench.cs`, and the
   wiring.
4. **`T59`** — the routed register: nine tuning domains whose LATEST revision no code reads; the manager routed
   them because the lane could not tell which program owns each — pick up the ones this program owns and report
   the rest.
5. **`T58`** (prose-only) and **`T16-F1`** (`test_publish_is_idempotent` mutates the production registry on its
   first run — CRLF).

⛔ **Owner-gated, not yours:** the "Review with owner before Phase 2/3/4/5" rows (`:677`, `:1059`, `:1749`,
`:1805`) and "Ready for owner sign-off" (`:2898`) — report them as owner-gated rather than working around them.

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

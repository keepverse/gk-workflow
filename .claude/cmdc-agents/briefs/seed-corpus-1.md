# Lane brief — `seed-corpus-1` · the four corpus runbooks, in their own order

**Program**: `seed-corpus` (anchor `tasks/seed-corpus-anchor.md`; **no map/plan of its own — the four
runbooks are the plan**):
`tasks/item-seedgen-todo.md`, `tasks/passive-tree-todo.md`,
`tasks/action-distribution-gaps-todo.md`, `tasks/seedsmith-generated-seed-repair-todo.md`.
**Ledger**: `tasks/seed-corpus-ledger.jsonl` (append-only, written only through
`python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl …`; `check` must exit 0).
**Session id**: `seed-corpus-20260920`. **Branch**: `cmdc/seed-corpus-1`, cut from `features/mega-merge`.

## Why this lane exists

The program holds **53 unchecked rows** across those four runbooks (measured 2026-09-21: item-seedgen 4,
passive-tree 33, action-distribution-gaps 13, seedsmith-generated-seed-repair 3) and no lane is running
it. `item-seed-gen` closed the item-corpus generation work and its lane is retired; this lane takes the
rest.

## Read before you write (binding — the design gate)

`docs/DESIGN-GATE.md` §1 for every subsystem you touch, then the documents its rows name, **in this
session**. At minimum: the runbook of the row you are on, `PRINCIPLES.md`, and the `decisions.md` locks
it cites. Code beats docs; docs beat comments.

## Your slice, in this order

1. **`H5-wire`** (`tasks/item-seedgen-todo.md`) — give `PassiveTreePlanCtx.tree_seed_roots` a real call
   site and run `HiddenFileCountMetric` for real. `tree_seed_roots` defaults to `()` at
   `gk-forge/tools/seedsmith/seedsmith/metrics/passive_tree.py:156`; the metric is instantiated in exactly one
   place repo-wide (its own test). A metric that only its own test calls is not a gate.
2. **`ISG-lens`** — clear the reported type blockers in the seedsmith test files
   (`gk-forge/tools/seedsmith/tests/test_combogen.py` L260/L407/L409, `test_items_adapter.py` L22/L166). The
   suites are green; CI gates on pytest, not on type checks — hygiene, and it is yours while you hold
   the files.
3. **`ISG7-follow-up`** — retire the last `socket-word` name residue
   (`gk-forge/tools/seedsmith/seedsmith/planner/schedule.py:64`, `invents_identity`). **Do not touch
   `maxCombosPerActor`** (`gk-core/data/tuning/sockets.v1.json:25`) — that is a separate retirement.
4. **`ISG-F1`** — four committed-corpus tests were red at HEAD `3f4d6411`. Re-measure at your base
   first: fix what is genuinely still red, and where a red is pre-existing and owned elsewhere, say so
   with the printed names instead of widening anything.
5. **action-distribution-gaps** — `T4.5` (B0 preflight), then `T4.6`/`T4.7`/`T4.11`/`T4.12` in order.
   `T3.2`/`T3.3` are **owner-gated**: do not run them, do not spend a model call on them.
6. **passive-tree / seedsmith-generated-seed-repair** — take only rows whose acceptance is executable
   without an owner. A row whose acceptance is "the owner eyeballs it" is **not** yours: leave it
   unchecked and say why in the fragment.

## Hard edges

- **Generated seed data is never hand-edited.** Fix the generator/tuning/registry, regenerate with the
  documented command, commit the diff. `gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/seed/actions/**`,
  `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/atoms/generated/**` are generated; `gk-core/data/tuning/**` is authored but
  published (`gk-core/tools/tuning/publish.py`), never edited in place, and **H7**: a publish switches its
  readers in the same commit.
- **`gk-core/data/tuning/**` and `gk-data/packs/fusion/data/generated/**` are `EnforcedRoots`**: a new file under either needs a
  `boundaries[]` owner row in `gk-core/scripts/verification-boundaries.v1.json` in the same commit, or
  `guard-verification-boundaries.py` fails (TVB-F8 is this exact defect).
- **Test substrate**: an in-memory store test stays in memory; a failed temp-delete is a failure, never
  `catch { }`.
- **A guardrail validates a contract, never a population count.** Do not assert "N species/items exist".
- **Findings route out; code stays in.** A finding outside your fence becomes a row in the OWNING
  program's todo in the same commit as the fragment that reports it.
- `sgc-2` (lane `cmdc/sgc-2`) works `gk-forge/tools/seedsmith/**` + `gk-data/packs/fusion/data/seed/items/**` on the set-planning
  system. Your fences overlap there but do not block (both worktree). Merge `features/mega-merge` into
  your branch before each new task so you do not fight a moving file, and never resolve a conflict by
  discarding their side.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Put the real output in the fragment:

- `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q` — **compare against
  the pre-existing baseline first**: `test_actions_description_completeness.py` fails on a clean HEAD
  (registered as `knownRed` SR-25).
- `dotnet run --project gk-forge/tools/ItemSeedValidator` and `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests`
  when a row touches the item corpus.
- `python gk-core/scripts/guard-test-substrate.py` and
  `python gk-core/scripts/guard-verification-boundaries.py`.
Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session seed-corpus-20260920
```
  path-owned boundary. Never the full suite; that belongs to CC8 or this program's final checkpoint.
- `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` after every ledger line.
- The row's own Verify line — each row carries one, and it is the acceptance you are held to.

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with the table
`| Criterion | Command | Result | Artifact |`, the exact commands, **the numbers printed**, the
committed artifact, an explicit **Not proved** list, and every finding routed to its owning row in the
same commit.

## Queue

`H5-wire` → `ISG-lens` → `ISG7-follow-up` → `ISG-F1` → action-dist `T4.5`/`T4.6`/`T4.7`/`T4.11`/`T4.12`
→ passive-tree executable rows → seedsmith-generated-seed-repair. One task = one commit.

# BCU2.12 — the 388 `NameCollision` nodes: the gate exists, the ledger says it did not hold

Lane `cmdc/bcu8-4`, head `d79237a9d`. Companion to `tasks/reports/bcu2-12-census.md` (the J10 census:
3030 note, **543 gap**, 1 not_measured over 42 trees / 1,679 nodes, of which **389 findings —
388 colliding nodes** — are `PassiveTree/NameCollision`).

The row's run is a manager-run model job, in flight (`tasks/run-board-20260920.md:1562`,
`2004b5a42`), writing `gk-data/packs/fusion/data/seed/passive-tree/**` and `gk-data/packs/fusion/data/generated/passive-tree/**`. Everything
below is model-free; nothing was written under `data/`.

## What the contract is, read at its sources

- `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:162-249` — gate 21's generation-time half
  ("closed 2026-09-11"): a draft's `name` is checked with `name_collision` against `takenNames`.
- `…/nodegen/run.py:1031-1047` — `taken_names` is seeded from **the whole ledger**
  (`gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json`), every subject's `record.name`, and
  extended as this run accepts (`:1189`).
- `…/species/generate_tree.py:192` — the species path calls that same `run_language_stage`, so the
  gate is on the species path too.
- `gk-forge/tools/seedsmith/seedsmith/metrics/passive_tree.py:1008` — `PassiveTree/NameCollision` is the
  read-only metric (`gates = False`) that reports what the gate let through.

## What the ledger actually contains

Read from the ledger's own `done` map (2,249 accepted subjects, 58 tree prefixes):

| reading | value |
|---|---:|
| subjects with a name | 2,247 |
| **names recorded by more than one subject** | **303** |
| accepts of `Kinetic Recirculation` | **12**, across 7 trees, **five of them inside `BigGatling`** (ledger indices 2161, 2164, 2168, 2176, 2177) |
| accepts of `Thickened Bark` | 15 subjects |
| accepts of `Rooted Stance` | 6 subjects |

Ledger order is append order (236 contiguous tree blocks over 58 prefixes), so `might`'s copy at index
203 predates `AbyssSwordStar`'s at 1708, `AllPeater`'s at 1752, `ArmedGargantuar`'s at 1830 and
`BigGatling`'s five — every one of those later accepts happened with the name already seeded into
`taken_names`. So the gate is not missing; it did not fire.

## Where it can still be wrong — superseded by [bcu2-12-namegate-mechanism.md](bcu2-12-namegate-mechanism.md)

**Correction (same lane, later commit):** the two candidates below were both excluded by model-free
probes. `build_response_gate(..., taken_names=["Kinetic Recirculation"])` **does** refuse a draft with
that name (`name_collision` is reached, as its docstring claims), so it is not a `nameKey`-vs-`name`
re-gate; and the codex/finalize stage deals in `codexSummary` sentences and never mints node names, so it
cannot be the writer. What remains: `_derive_unique_name_key` (`nodegen/run.py:703-724`, called `:909`)
can always make the **key** unique from the accepted **name**, so a duplicate name that reaches a
persisted record is silently key-suffixed — the ledger's `Kinetic Recirculation` fingerprints
(`-2`, `-4`, … `-13`) are that sequence. The original two candidates are kept below for the trail.

1. **The re-gate may compare the wrong field.** `record.nameKey` (`tree.node.unsteady-equilibrium`) and
   `record.name` (`Unsteady Equilibrium`) are both persisted; `run.py:1041-1047` seeds `taken_names`
   from `name` (correct), but the persist-time re-gate (`run.py:1114-1118`) and the vote-composite path
   pass `taken_names=others_taken` through a second comparison — if that one compares name **keys** it
   cannot see a cross-tree name reuse.
2. **The codex/finalize stage never runs gate 21.** `grep -rn "name_collision\|taken_names\|
   known_name_keys" gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/ gk-forge/tools/seedsmith/_j9_batch_run.py`
   → **0 hits**, and `_j9_batch_run.py:138`'s `finalize_codex` re-draws the three-sample vote and writes
   the species record — the only name-bearing write in that path that cannot pass the gate. Five
   same-tree accepts are the shape this produces.

**The decision between them is one controlled re-generation** (a model call, so not this lane's): clear
one species whose name duplicates a committed `might` name and run it with the ledger in place; a
refusal means (1) or (2) is confined to the codex write, an accept means the gate itself is not seeing
the ledger.

## The part that is not a code question

`git log -1 -- gk-data/packs/fusion/data/seed/passive-tree/nodes/<tree>.json` dates the colliding files: `jala`, `might`,
`precision` last written **2026-09-07** — before gate 21 closed — and `agility` **2026-09-19** by SE1.6
("regenerate generated content, **no model call**", `fd650d072`), which by construction cannot run a
model-driven language gate. So a large share of the 388 colliding nodes is pre-gate or
regenerate-sourced content, and the J9 run's re-generation is the thing that must move the number.

## The gap that let it ship

No test pins the tree path's gate: `grep -rln "taken_names\|name_collision" gk-forge/tools/seedsmith/tests/` finds
the primitives only in `test_base_types_gen.py`, the four `test_dungeon_*` files, `test_quality_gates.py`
and `test_unique_pipelines.py` — the tree/species path has none, so a `taken_names` regression there is
invisible to the suite. That is the contract-with-no-guard shape
[docs/architecture/validation-ssot.md](../../docs/architecture/validation-ssot.md) names, one level up
from the count itself.

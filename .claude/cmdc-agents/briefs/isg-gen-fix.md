# Lane `isg-gen-fix` — the items generator's hybrid-set role defect (BCU2.11's `SetCompletability` GAPs)

**Session:** `item-seedgen-genfix` · **Program:** `item-seedgen` · **Mode:** worktree
**Fence:** `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/items/**`, `tasks/item-seedgen-todo.md`, `tasks/reports/**`

## The defect — already measured at the current head, do not re-derive it

`python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` exits **1** with `[GAP] Linkage/SetCompletability`:

- `set.verdant-graft-001`: `'Halfgreen'` claims role `'head-guard'`, **which is not in the hybrid role core**
- `set.verdant-graft-002`: `'Sapvein'` claims role `'sense'` — not in the hybrid role core
- `set.verdant-graft-005`: `'Rootstock of the Conjunction'` claims `head-guard` / `sense`

Read the full reading in `tasks/item-seedgen-todo.md` row **`ISG-gap-1`** and the BCU2.11 run report
(`tasks/reports/`, itemJsonFiles 1048; 68 files changed / 129,299 insertions on `corpus/bcu211`).

**Why it matters:** those sets can never be completed in play — a hybrid frame cannot satisfy a role the
hybrid role core does not contain. So the corpus is not merely failing a check; it is shipping content a
player cannot finish.

## The hard rule that governs the fix

`gk-data/packs/fusion/data/seed/items/**` is **GENERATED**. ⛔ Never hand-edit an emitted row to make the check pass. Editing
the JSON forks the corpus from its generator: the next run reverts it, the provenance ledger stops
describing the file, and the fix becomes invisible to every other consumer. **Fix the generator (or its
brief/quota/registry input), then regenerate and commit both.** If the generator cannot yet express the
fix, then fixing the generator *is* the deliverable — stop and do that.

## Deliverable

1. **The generator-side root cause, named by `file:line`** — where the role list for a hybrid set is
   produced/validated, and why `head-guard`/`sense` can reach it. State whether the defect is (a) a
   wrong role vocabulary for hybrid frames, (b) a missing validation, or (c) a brief/quota input. Those
   have different fixes; do not blur them.
2. **The fix plus a regenerated corpus** — the generator change and the regenerated diff, in that order,
   with the regeneration command printed.
3. **`python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` exits 0** — print the exit code and the
   report it emits (a GAP list shorter than the three above is not a pass).
4. **Focused tests green**, and say plainly which failed on a clean HEAD before your change:
   `gk-forge/tools/seedsmith/tests/test_combogen.py`, `test_strain_splice_gen.py`, `test_materials_gen.py`,
   `test_recipes_gen.py`, `test_items_adapter.py`.
5. **A row update in `tasks/item-seedgen-todo.md` (`ISG-gap-1`)** recording the fix and its evidence, plus
   **a reading, not a guess**: does any *other* hybrid set carry the same defect? Report the number you
   measured across the corpus.
6. **A NOT-proved list.** State what you did not check, especially anything about roles in the *runtime*
   consumer rather than the generator.

## Context — what this unblocks, and what is not yours to do

Once the check is green, the branch `corpus/bcu211` can be merged (68 files, 129,299 insertions) and the
action-distribution runs `T3.2`/`T3.3` can be sequenced after it. **Do not merge `corpus/bcu211`** and do
not run those corpus runs — the manager owns both.

## Verification

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith check ../../data/seed/items --adapter items   # must exit 0
$env:PYTHONPATH = "."; python -m pytest tests/test_combogen.py tests/test_strain_splice_gen.py -q
cd ../..
.\scripts\verify-change.ps1 -Paths <every changed path> -Session item-seedgen-genfix
```

Commit the generator fix and the regenerated corpus together, with `paths` explicit — never the whole
tree, because other lanes are live in this checkout.

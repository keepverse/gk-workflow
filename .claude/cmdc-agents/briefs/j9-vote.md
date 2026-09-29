# Lane `j9-vote` — make one J9 driver invocation converge (the codex vote resolves ~1 attempt in 2)

**Session:** `passive-tree-j9-vote` · **Program:** passive-tree · **Mode:** worktree
**Fence:** `gk-forge/tools/seedsmith/seedsmith/adapters/trees/**`, `gk-forge/tools/seedsmith/_j9_batch_run.py`,
`gk-forge/tools/seedsmith/tests/test_j9_batch_run.py`, `tools/seedsmith/tests/test_species_tree*.py`,
`gk-data/packs/fusion/data/seed/passive-tree/**`, `tasks/passive-tree-todo.md`, `tasks/reports/**`
**Row:** `J9-B2` in `tasks/passive-tree-todo.md`.

⚠ **Concurrent lane on the same subtree, different half:** `isg-gen-fix` (session `item-seedgen-genfix`) holds
the **items** half — `seedsmith/adapters/items/**` and `seedsmith/report/**`. Do not touch those files; do not
"tidy" a shared module to make your change easier. If your fix genuinely needs a file outside your fence, say
so in your fragment and let the manager widen it deliberately.

## The defect, already measured — do not re-derive it

The BCU2.12 bounded re-proof on the merged head (`tasks/reports/BCU2.12-proof-20260921.json`, 2 species,
4 attempts, local `google/gemma-4-26b-a4b-qat`) found:

- **Pass 1:** `AbyssSwordStar` wrote its metadata (`metadataWritten: true`, codex 136 chars);
  `AcientSunNut` returned `codexUnresolvedReason: "vote_unresolved"`, `metadataWritten: false`.
- **Resume pass:** exactly inverted — `AbyssSwordStar` unresolved, `AcientSunNut` resolved.

So the codex vote (J9-B1's single-linkage clustering at `nodegen.dedup`'s 600 ‰ rung) resolves **about one
attempt in two**, and **one invocation does not converge**. The resume pass retries species whose metadata was
never written — correct and useful — but the retry depth needed at 840-species scale is unmeasured, and a
species unlucky on every attempt ends with **no codex summary at all**.

**Not the defect:** the same-tree `nameKey` refusal is gone (`nodeKeyRefusedReason: null` in every line of both
passes), so do not re-open J9-B1(b).

## Deliverable

1. **One invocation converges.** The driver writes `gk-data/packs/fusion/data/seed/passive-tree/species/<id>.json` for **every**
   species in its slice, each with either a resolved codex summary or a **named, bounded** failure — not a
   silent gap. A bounded retry inside one invocation is the expected shape (re-vote only the unresolved
   species, up to a stated attempt count, then record the failure by name). State the bound and why that
   number; an unbounded loop that hides a bad prompt is not a fix.
2. **The retry is covered by the harness's own tests** (`gk-forge/tools/seedsmith/tests/test_j9_batch_run.py`, which
   already exists with 5 tests). Add the retry case with a fake voter — no model calls in tests.
3. **A measured resolve rate, not an assertion:** run ≥8 species through the same invocation and record, per
   attempt, how many resolved. Write it into `tasks/reports/` as a reading with the command that produced it.
   Nine species is the smallest number that makes "about half" falsifiable; if the rate turns out to depend on
   the species, that is the more interesting finding and worth one sentence.
4. **The row `J9-B2` updated** in `tasks/passive-tree-todo.md` with what you changed, the measured rate, and
   whether the 840-species run can now be released.
5. **A NOT-proved list.** Especially: whether the instability is the clustering rung, the sample count, or the
   prompt — a fix that converges without explaining the flakiness must say so.

⛔ **Do not run the 840-species roster.** That is BCU2.12's job and the manager's, after this row closes.
⛔ Never hand-edit a file under `gk-data/packs/fusion/data/seed/passive-tree/**` to make a reading look better — the ledger is the
resume mechanism and a hand-edit forks the corpus from its generator.

## Evidence contract (the manager accepts on exactly this)

Exact command text; the numbers printed; the committed artefact; the NOT-proved list; findings that belong to
another program named with the owning program, not fixed here.

## Verification

```powershell
cd gk-forge/tools/seedsmith; $env:PYTHONPATH = "."
python gk-forge/tools/seedsmith/_j9_batch_run.py --check
python -m pytest tests/test_j9_batch_run.py -q
python gk-forge/tools/seedsmith/_j9_batch_run.py --count 8 --out gk-data/packs/fusion/data/seed/passive-tree/_runs/j9-vote-rate.json
cd ../.. ; .\scripts\verify-change.ps1 -Paths <every changed path> -Session passive-tree-j9-vote
```

Commit the driver change and the tests together, with explicit `paths`.

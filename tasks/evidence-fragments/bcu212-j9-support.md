# BCU2.12 support — J9's real invocation, a bounded live run, resume proof, and the manager's two scripts (2026-09-21)

Task: establish the invocation for passive-tree J9 (the species production run), run it bounded against
the local model, prove resume safety, and hand the manager a detached-run pair. **The full run was NOT
started by this lane.**

## 1. The invocation (no production entry point exists — the harness is the real one)

There is **no production batch entry point**: `run_species_tree`
(`gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py`) is a per-species unit, and its own
docstring says it "never loops over a roster". No CLI under `gk-forge/tools/seedsmith/seedsmith/adapters/trees/`
and no `__main__` drives a roster. The batch harness that DOES exist — written by the 2026-09-07 J9
de-risking pass and tracked — is:

```powershell
# from the worktree root, PYTHONPATH=gk-forge/tools/seedsmith
python gk-forge/tools/seedsmith/_j9_batch_run.py <count>
```

It loads the real roster, calls `assign_favour_cells` once over the FULL roster (so a later, larger
continuation reuses the same assignments), then `run_species_tree` for the first `<count>` species in the
roster's stable `_index.json` order, writing real output to the real paths and per-species results to
`tools/seedsmith/_j9_batch_run_results.json` (a scratch file, deleted after this pass — see below).

## 2/3. Bounded live run + resume proof (2 species, `google/gemma-4-26b-a4b-qat`)

| Criterion | Command (verbatim) | Result | Artifact |
|---|---|---|---|
| Bounded pass 1 | `PYTHONPATH=gk-forge/tools/seedsmith python gk-forge/tools/seedsmith/_j9_batch_run.py 2` | exit `0` in **601 s**, **68** `call complete` lines | `/tmp/j9_batch1.txt` |
| — species 1 | the `[1/2]` line | `AbyssSwordStar`: favour resolved `Pierce\|air\|nerve.afflicted`; `nodeKeyRefusedReason: null`; `outcomeCounts {accepted: 5}` (last internal pass); `codexUnresolvedReason: "vote_unresolved"`; `metadataWritten: false` | `gk-data/packs/fusion/data/seed/passive-tree/nodes/AbyssSwordStar.json` |
| — species 2 | the `[2/2]` line | `AcientSunNut`: favour resolved `Onslaught\|air\|cold`; **`nodeKeyRefusedReason: "nameKey 'tree.node.solar-marrow-2' is used by both node index 4 and node index 6 in the same tree — refused, never renamed out from under the model's answer"`**; nothing written | — |
| Nodes actually written | `python -c "import json;print(len(json.load(open('gk-data/packs/fusion/data/seed/passive-tree/nodes/AbyssSwordStar.json',encoding='utf-8'))['nodes']))"` | `40` (the file was a 0-node stub at base; `AcientSunNut.json` still does not exist) | same |
| Per-species metadata | `ls gk-data/packs/fusion/data/seed/passive-tree/species/` | only `AshThreePeater.json` (from an earlier PoC). **Neither bounded species wrote one** — AbyssSwordStar's codex is `vote_unresolved`, AcientSunNut's tree was refused | `gk-data/packs/fusion/data/seed/passive-tree/species/` |
| Resume pass | the identical command again | exit `0` in **35 s**, **14** `call complete` lines, `[1/2] outcomeCounts {}` (no subject regenerated), `[2/2]` the same refusal | `/tmp/j9_batch2.txt` |
| Resume is byte-identical | `sha256sum` of the node file before/after | `0d63036faefb8147…2cd144` unchanged → **NODES BYTE-IDENTICAL** | — |
| What the 14 resumed calls are | the pass-2 log | the non-node stages only: the favour-fit probe and the codex vote for AbyssSwordStar (still `vote_unresolved`). Node generation made **zero** calls — every one of the 80 subjects was read back from the shared ledger | `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json` |
| Ledger grew by the bounded run | `git diff --numstat -- gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json` | `445 0` (80 rows: 40 per species), `done` rows `2120 → 2200` | same |

**Invocation for the full run:** `python gk-forge/tools/seedsmith/_j9_batch_run.py <len(roster)>` — and the count
is the **roster's own length, 904 today, never the spec's "840"** (see the routed row below). The
manager's script computes it, so a hardcoded literal cannot silently under-run by 64 species.

## 4. The two manager scripts

| Criterion | Path | What it does |
|---|---|---|
| Detached full-run driver | `.claude/cmdc-agents/scripts/bcu212-full-run.ps1` | reads `HEAD`/branch, computes the roster length, runs a 2-species smoke → the full run → a resume pass → `python -m seedsmith check --family PassiveTree` → the report; each step prints `*_exit` |
| Report artefact writer | `.claude/cmdc-agents/scripts/bcu212-report.py` | writes `tasks/reports/BCU2.12-full-run.json`; J10 census derived from the **ledger + committed node files** (not the harness's last-pass file, which the resume pass overwrites — measured: it read `acceptedNodesThisPass: 0` while 40 nodes sat on disk) |
| The pair is runnable and its artefact is real | `PYTHONPATH=gk-forge/tools/seedsmith python .claude/cmdc-agents/scripts/bcu212-report.py` | exit `0`; wrote the artefact below | `tasks/reports/BCU2.12-full-run.json` |
| Census reading at this base | the artefact's `census` | roster **904**; `complete 0`; `nodesWithoutCodexSupplement 4` (`AbyssSwordStar`, `AllPeater`, `ArmoredImpZombie`, `BambooDragon`); `startedIncomplete 12` (ledger rows, zero nodes on disk — the earlier PoC runs used a temp `seed_root`, so their accepted rows persist in the shared ledger but their documents were never committed); `untouched 888`; generic trees `42 / 1679 nodes` | same |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Kept / discarded
- **Kept, committed:** `gk-data/packs/fusion/data/seed/passive-tree/nodes/AbyssSwordStar.json` (40 real model-generated nodes)
  and the shared ledger's 80 new rows. Discarding them would throw away 10 minutes of real model time and
  force the full run to redo two species; the ledger rows are what make the resume work.
- **Caveat, not hidden:** AbyssSwordStar's tree has **no** `species/AbyssSwordStar.json` codex supplement
  (codex `vote_unresolved`), and its `_provenance.promptVersion` is `"mixed"` (35 nodes unstamped, 5 at
  `tree-language/3` against the current `PROMPT_VERSION = "tree-language/3"`). It is a real tree that has
  not cleared its own ship bar yet — the full run's next pass re-attempts the codex.
- **Deleted (not committed):** `tools/seedsmith/_j9_batch_run_results.json` — the harness overwrites it every pass, so
  after the resume pass it describes only that pass (0 accepted this pass). Its content is preserved
  inside the committed report artefact; the full run recreates it.

## Not proved
- **The full 904-species run was NOT started** (manager's job, detached). Bounded: 2 species only.
- **No species is complete.** Both bounded species stopped short of the ship bar: one on an unresolved
  codex, one on a nameKey refusal. That is the reading, not a failure of the harness.
- `AcientSunNut`'s refusal is **permanent on repeat**: the 40 accepted records stay in the ledger, so
  every future pass rebuilds the same duplicate-nameKey document and refuses again. Routed below.
- `gk-data/packs/fusion/data/seed/actions/**`-style boundary coverage does not exist for `gk-data/packs/fusion/data/seed/passive-tree/**` either;
  the bounded outputs are committed on direct evidence, and the census above is the check.

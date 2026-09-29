# BCU2.12 / J10 — the PassiveTree census at `3e7a51d16`, recorded while J9 is in flight

Lane `cmdc/bcu8-4`. Owner of the row: `tasks/passive-tree-todo.md` (J9/J10/J13) via register BCU2.12.
BCU2.12 is a manager-run detached model job and its corpus (`gk-data/packs/fusion/data/generated/passive-tree/**`,
`gk-data/packs/fusion/data/seed/passive-tree/**`) is outside this lane's fence, so the lane-reachable half is this model-free
reading — the same BEFORE/after shape BCU2.10 got in `tasks/reports/bcu2-10-readings.json`.

## The command and the reading

```
PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree
→ 3030 note, 543 gap, 1 not_measured        (exit 0 — none of these gate)
```

The full gap and not-measured lines are in `tasks/reports/bcu2-12-census.txt` (545 lines, the notes
elided). Gaps by metric:

| metric | gaps | what the tool says |
|---|---:|---|
| `PassiveTree/NameCollision` | **389** | `388/1679 nodes (231‰) share a name with another node in the corpus`, plus one per offender — **and the gate that should have refused them is correct**: `python tasks/reports/bcu2-12-namegate-probe.py` shows `build_response_gate` refusing a draft that reuses a taken name, so what lets a duplicate persist is the key-suffix path (`_derive_unique_name_key`, `nodegen/run.py:703-724`) — see [bcu2-12-namegate-mechanism.md](bcu2-12-namegate-mechanism.md) |
| `PassiveTree/QuotaDrift` | 83 | cells where `corpus shows N, the re-derived quota is M` beyond tolerance, e.g. `blight:element=earth` 4 vs 6 (drift −2, tolerance 1) |
| `PassiveTree/SpeciesUniqueness` | 67 | name/flavor pairs repeated across trees, e.g. `U1:Accelerated Cadence` in `rally:skill.rally-off-t6-n0` and `rally:skill.rally-off-t9-n1` |
| `UnresolvedCount`, `NearDuplicate`, `MechanismRamp`, `ExclusionRate` | 1 each | one corpus-level finding each |
| **total** | **543** | |

Corpus size in the same run: `reverse index built over 42 tree(s), 1679 node(s)`
(`PassiveTree/SpeciesUniqueness`'s own note).

## Provenance — and what a delta needs

`tasks/reports/BCU2.12-full-run.json` (the merged manager artefact) carries the run's *ledger* side:
`rosterSpecies: 904`, `ledgerDoneRows: 2200`, `census.complete.count: 0`, `12` started-incomplete
(`ledgerRows == ledgerAccepted`, `nodesOnDisk: 0`), `4` nodes without the codex supplement. The board
has the run in flight (`tasks/run-board-20260920.md:1562` `[133/904]`; `2004b5a42` `[134/904]`).

So the two readings disagree in a way that is worth one line, not a conclusion: the ledger records work
done (2,200 rows) while the corpus holds 42 trees / 1,679 nodes — the artefact's own
`startedIncomplete` samples (e.g. `AcientSunNut` 40/40 rows, 0 nodes on disk) are the same shape. This
is a mid-run reading; re-run the command above after the run completes for the delta, and trust the
ledger-side artefact only for what it measured.

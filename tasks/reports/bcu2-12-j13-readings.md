# BCU2.12 / J13 — the acceptance table it must move, read at `7785aa934`, and the vintage it names is gone

Lane `cmdc/bcu8-4`. Owner: `tasks/passive-tree-todo.md` **J13: Regenerate the 42 shared trees under
`tree-language/2`** (model spend AUTHORISED 2026-09-21), sequenced by register BCU2.12. The row is a
manager-run model job (`tasks/run-board-20260920.md:1562`, `2004b5a42`; the run is in flight) writing
`gk-data/packs/fusion/data/seed/passive-tree/**` — outside this lane's fence. Everything below is model-free; nothing under
`data/` was written.

## J13's own Verify line, quoted

> **Verification:** `check --family PassiveTree` exit 0 under `--gate`; full family report shows no GAP
> on the three generation-vintage metrics above.

At this head:

```
PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree --gate
→ 3030 note, 543 gap, 1 not_measured        (exit 0)
```

So the **exit-0 clause already holds**, and that is exactly why the row cannot be closed on it: none of
the three metrics below is promoted to gate (`NameCollision` is `gates = False`,
`metrics/passive_tree.py:1008`), so `--gate` is green while the acceptance's own second clause — *no GAP
on the three generation-vintage metrics* — is red on all three.

## The three generation-vintage metrics: J13's target vs this head

| metric | J13's 2026-09-10 reading | at `7785aa934` (this head) | J13 target | state |
|---|---|---|---|---|
| `ExclusionRate` | 1676/1677 nodes (999‰), almost all `reroute` | **1071/1679 (637‰)** — form split `none` 608, `nullification` 24, `reroute` 1047; **1053 nodes outside their cell's allocation** | ≤30‰ | still **21× over** |
| `NameCollision` | 646/1677 (385‰) | **388/1679 (231‰)** | 0 preferred | 388 colliding nodes remain |
| `NearDuplicate` | 116/1677 (69‰) | **116/1679 (69‰)** — unchanged | ≤5‰ | **14× over** |
| `MechanismRamp` | 3 missing mechanism nodes (`dark-def-t4-n0`, `fire-def-t9-n0`, `wither-def-t9-n1`) | **1** shortfall: `wither:defensive:t9` holds 2 mechanism nodes where the archetype ramp names exactly 3 | clean | down to one |
| `UnresolvedCount` (also named by J13) | not recorded there | **92/1680 (54‰)**, target ≤50‰ | ≤50‰ | marginally over |

The run has real work to do on `ExclusionRate` and `NearDuplicate` in particular; `NameCollision` is the
metric this lane already read to a mechanism in
[tasks/reports/bcu2-12-namecollision-finding.md](bcu2-12-namecollision-finding.md).

## The vintage J13 names is gone — its title target is unattainable as written

Read from the 42 shared tree documents themselves — reproduce with
`python tasks/reports/bcu2-12-vintage-reading.py --out tasks/reports/bcu2-12-vintage-reading.json`
(`gk-data/packs/fusion/data/seed/passive-tree/nodes/`'s 9 species files are J9's own output, not part of the 42):

| reading | value |
|---|---|
| file-level `_provenance.promptVersion` | `tree-language/1` **22** · `mixed` **20** · **`tree-language/2` 0** |
| node-level `promptVersion` across those 42 files (1,679 nodes) | `tree-language/3` **613** · absent **1,066** |
| `PROMPT_VERSION` in code | **`tree-language/3`** — `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:57` |

Two consequences, both erratum-shaped and both already half-recorded by the owning program:

1. **J13's title says `tree-language/2`; nothing in the corpus is at `/2` and the code now writes `/3`.**
   `tasks/passive-tree-todo.md`'s PT-J9-F2 records the premise as stale with the reading
   `tree-language/1` (22) / `tree-language/2` (4) / `mixed` (21); at this head the same measurement is
   **22 / 0 / 20**, i.e. the `/2` file moved and four of the mixed files flipped. The row's target version
   needs restating to `/3` before its acceptance can be judged at all — which is what PT-J9-F2 asked for.
2. **`mixed` is not "two prompt versions in one file" here.** The 20 mixed files hold `tree-language/3`
   nodes beside nodes with **no** `promptVersion` field at all (`agility` 39/1, `air` 37/3, `blight`
   33/7), so a regenerated `/3` tree does not need to reconcile two labelled vintages — the older rows are
   simply unlabelled. That matters for the row's third acceptance clause ("every regenerated seed document
   carries `promptVersion: tree-language/2`", which must become `/3`).

## Clauses 3 and 5, measured

| clause | reading at this head |
|---|---|
| *"Every regenerated seed document carries `promptVersion: tree-language/2` and a persisted `quotaCell`"* | `promptVersion` and `quotaCell` sit on the **same 700 of 2,019** node records — **613** of the 1,679 shared-tree nodes and **87** of the 340 species-tree nodes, across 28 documents. The other 1,319 rows carry neither, which `nodegen/emit.py:96-99` names for exactly what they are: its loader *"returns None when absent (every pre-persistence committed record), never invents defaults"*. So the emit wiring landed for 700 rows and everything older is pre-wiring — and the two fields moving together is the wiring change this clause describes. |
| *"No hand-edits of exclusion forms, names, or `kMicro` — regenerate only"* | `kMicro` is **not a field of any node record (0 of 2,019)** nor of any bound/refused row in the generated reports (0 of 2,240), and the repair program rescoped its carriage — *"A4 … `kMicro = 0` + real `kindId`, or new field? … ✅ RESCOPED 2026-09-15: neither — no structural carriage exists to shape; mechanism-class atoms travel the existing resolve path once anchor-priced"* (`tasks/passive-tree-repair-todo.md:695`). So that object of the clause is **vacuous at this head**; the live half is "regenerate only", and the only corpus signal for it is the provenance vintage above (a hand-edit and a regenerate are otherwise indistinguishable once committed). |

Both readings are raw file reads over `gk-data/packs/fusion/data/seed/passive-tree/nodes/**` and `gk-data/packs/fusion/data/generated/passive-tree/**` —
model-free, nothing written.

## What this lane cannot do

The regeneration itself (`python -m seedsmith trees generate --all --write`, ~5,040 base+vote calls, or
per-tree) writes `gk-data/packs/fusion/data/seed/passive-tree/**` and spends model time — a manager-run detached job. This
report is the BEFORE its acceptance needs, and `tasks/reports/bcu2-12-census.md` carries the raw
per-finding census (`tasks/reports/bcu2-12-census.txt`).

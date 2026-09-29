# TVB-F20 — the replacement metric: open TASK BLOCKS per todo

The manager's published burn-down (`524 open / 967 done`) does not reproduce under any of the 13
definitions the recon lane tried, so it was retired until this landed. This is that instrument.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the counter | `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` | **TOTAL open=734 done=2750 boxes=2014 (not a work count) shaded=857 · unmeasured=2 file(s)** over **117** todo files | `gk-core/scripts/audit-program-pipeline.py` |
| the marker map | `gk-core/scripts/todo-shapes.v1.json` | **119** files, each `{shape, exemplar}`; extracted from the report's own §3 classification and re-checked against each file (one disagreement found and fixed: `trade-network-todo.md` is `H-bracket`, its `### [ ] 0a.1 …` headings, not the `H-id` its §3 row says) | `gk-core/scripts/todo-shapes.v1.json` |
| the guard | `python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q` | `25 passed` — 10 new fixture cases; behaviour only, never a repo population | `gk-core/tests/tools/test_audit_program_pipeline.py` |
| RECON-F7 | `python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes` | **24 open**, `loam` gone — its `:1361` phase banner is now seen | — |
| RECON-F8 | the same counter's `--json` output | **2 unmeasured** (`player-guide-todo.md`, `world-map-gaps-followup-todo.md`); an undeclared file is reported, never defaulted to zero | — |
| cross-check | the census | `rpg-simulator-todo.md` reads **open=20 done=17** here and **20** in `convergence-census.py` — two instruments, same number | — |

**The rule implemented** is the report's §1 block rule, and the four places it had to be read out of the
files rather than guessed are each pinned by a fixture:

1. a header banner (`closed by the header above`) closes every block, and its unticked boxes are shaded;
2. a CLOSED-status banner closes the blocks that **start after** it — a file-end banner closes nothing
   before it (`species-gear-chain`), and `loam`'s phase banner sits above the rows it kills;
3. a heading that declares itself `(OPEN)` is never closed by a file banner (`achievement-title`'s
   four `Task 7b-…` rows say so in their own words);
4. the contract clause (`a ticked task's acceptance boxes are its original contract`) shades a ticked
   block and never closes an unticked one — treating it as a closer gave `species-gear-chain` 0 open
   where the report reads 6.

**What it cannot prove**, printed in the tool's own output: that a tick is true; that an open block is
unfinished rather than deferred, blocked, superseded or owner-only; that the marker map is complete; that
no work exists outside the todo; and any **size** — `L-run` and `XS` count the same. It also prints that
the report's per-file hand overrides are deliberately not implemented, so a count here is reproducible by
rule and need not equal the prototype's `858 / 2,705`.

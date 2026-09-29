# ISG-H5 — the ledger queue's id for the H5 work routed to item-seedgen (recorded 2026-09-21)

The anchor's original queue named this item `ISG-H5`; the runbook row and the lane brief call the same
task `H5-wire`. They are one task, already closed — full evidence in
`tasks/evidence-fragments/H5-wire.md`. This fragment records the queue id against real evidence and
re-runs the task's own **Verify line** fresh at base `00baecb5`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Verify: a fixture root with one `_`-prefixed file is found | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest "gk-forge/tools/seedsmith/tests/adapters/trees/test_passive_tree_metrics.py::HiddenFileCountMetricTests::test_a_canary_parked_entry_in_an_underscore_file_is_found" -q` | `1 passed` | `gk-forge/tools/seedsmith/tests/adapters/trees/test_passive_tree_metrics.py:931` |
| Verify: a corpus with one over-priced tree fails `TreeEqualValue` | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest "gk-forge/tools/seedsmith/tests/adapters/trees/test_passive_tree_metrics.py::TreeEqualValueContentSideMetricTests::test_an_over_priced_node_fails_tree_equal_value" -q` | `1 passed` | `gk-forge/tools/seedsmith/tests/adapters/trees/test_passive_tree_metrics.py:790` |
| Both picked up together | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest <the two node ids above> -q` | `2 passed in 0.28s` | — |
| The real call site, re-run for real | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree 2>&1 \| grep HiddenFileCount` | `[NOTE] PassiveTree/HiddenFileCount — (corpus): walked 0 \`_\`-prefixed file(s) across 1 seed root(s)` | `gk-forge/tools/seedsmith/seedsmith/report/cli.py:323,345` |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- The non-zero `visitedFileCount` acceptance clause remains unsatisfiable against today's passive-tree
  corpus and stays routed as **PTR-EF1**; this fragment does not reopen it.
- No commit of its own: the queue id is an alias of an already-committed task, so the ledger writes ride
  along with the ISG7-F2 commit (per the "no bookkeeping-only commit" rule).

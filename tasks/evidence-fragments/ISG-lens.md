# ISG-lens — clear the pi-lens type blockers in the seedsmith test files (closed 2026-09-21)

Re-measured at base `00baecb5`: most of the listed blockers were already cleared by the SSH5.10 flip
(`611d9c23`) and by ISG6/ISG7; one real, reproducible blocker remained — the unsorted import block.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Unsorted import block cleared | `ruff check --select I --fix --no-cache gk-forge/tools/seedsmith/tests/test_combogen.py` | `Found 1 error (1 fixed, 0 remaining).` — `import dataclasses` now follows `import argparse` | `gk-forge/tools/seedsmith/tests/test_combogen.py` |
| Both named files lint-clean | `ruff check --select I,UP,B,SIM,C4,PIE,RET,ARG,PL,F --ignore E501,PLC0415 --no-cache --output-format concise gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_items_adapter.py` | `All checks passed!` | both files |
| `read_text`-on-`None` already narrowed | `grep -n "assert result.file is not None" gk-forge/tools/seedsmith/tests/test_combogen.py` | `293:        assert result.file is not None   # narrows the Optional for the type checker` (added in `611d9c23`) | `test_combogen.py:293` |
| Useless lambda already gone | `grep -c "lambda" gk-forge/tools/seedsmith/tests/test_combogen.py` | `0` (was `to_dict=lambda: {}`, replaced in `611d9c23`) | `test_combogen.py` |
| `SimpleNamespace` not passed where a `Namespace` is declared | `grep -n "def _exit_for_graph_batch" gk-forge/tools/seedsmith/seedsmith/report/cli.py` | `60:def _exit_for_graph_batch(result) -> int:` — unannotated param, so the `SimpleNamespace(outcomes=…)` fakes at `test_combogen.py:402-407` are not a type error; the only `argparse.Namespace` call site builds an `argparse.Namespace` | `gk-forge/tools/seedsmith/seedsmith/report/cli.py:60`, `test_combogen.py:402-441` |
| Item-adapter import/annotation findings already fixed | `ruff check --select I,UP --no-cache --output-format concise gk-forge/tools/seedsmith/tests/test_items_adapter.py` | `All checks passed!` — fixed once already by ISG6/ISG7 (the row says so) | `test_items_adapter.py` |
| Both files' own tests green | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_items_adapter.py -q` | `45 passed in 1.66s` | — |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- `pi-lens` itself is **not installed** on this machine (`command -v pi-lens` → not found), so the exact
  pi-lens diagnostics could not be re-run. The blockers are re-measured with `ruff` (I/UP/B/SIM/…) plus a
  direct `grep` for each named construct — the achievable check, not the original instrument.
- No wider regression proof: an import reorder cannot reach another test, and the full-suite baseline was
  already measured (`20 failed, 4260 passed, 3 skipped`) in `H5-wire`.

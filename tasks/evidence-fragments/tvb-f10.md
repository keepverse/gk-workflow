# TVB-F10 — `report/**` gets a focused owner, so its path no longer runs the whole pytest tree

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| before | `verify-change.ps1 -Paths @('gk-forge/tools/seedsmith/seedsmith/report/cli.py') -PlanOnly` | `seedsmith-fallback (module)` → the whole `pytest: seedsmith` tree | `tasks/test-verification-boundary-todo.md` |
| after | same command | `seedsmith-report (focused)` (plus the pre-existing `gen-creature-report-seam`) | `gk-core/scripts/verification-boundaries.v1.json` |
| the new row | registry | `seedsmith-report`: `paths: ["gk-forge/tools/seedsmith/seedsmith/report/**"]`, `project: "seedsmith"`, `testFiles: ["gk-forge/tools/seedsmith/tests/test_cli.py"]`, `level: focused` | — |
| the focused selection | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_cli.py -q -p no:cacheprovider` | **`1 failed, 23 passed in 17.91s`** — against the row's own fallback reading of `22 failed, 4142 passed, 3 skipped` in **9m27s** | — |
| that one failure | the same run | `test_actions_check_uses_domain_loader_and_excludes_round_scratch` (`assert 1 == 0`, `test_cli.py:100`) — pre-existing and already filed in `tasks/action-corpus-todo.md`, so nothing is filed again here | `tasks/action-corpus-todo.md` |
| registry integrity | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |

`tests/test_cli.py` is the file that imports `from seedsmith.report.cli import (...)` directly, so it is the
honest focused set for that module — the same shape every other `seedsmith-*` focused row already uses.

**Still open:** the row's second option. The network-dependent node is reachable through
`seedsmith-actions`' own `testFiles` (it names `tests/test_actions_description_completeness.py`), so a change
to `seedsmith/adapters/actions/**` still runs it. It is already a `knownRed` entry (debt SR-25), so the
boundary reports it as pre-existing — keeping it out of the *selection* needs a pytest-exclusion field, a
schema change in the pipeline-protected guard plus the planner.

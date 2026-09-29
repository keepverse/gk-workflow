# ST3.2 — the coverage report and innate picker take the loaded windows, and `RUN_WINDOW` is gone

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `RUN_WINDOW` no longer exists anywhere in seedsmith | `Get-ChildItem -Recurse gk-forge/tools/seedsmith -Include *.py -File \| Select-String -Pattern "RUN_WINDOW"` | **No output.** The last copy was deleted from `distribution_planner/derive.py`, and both importers that kept it alive moved to the loaded windows in this same change. | gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py |
| The coverage report takes the loaded windows | `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_coverage_report.py gk-forge/tools/seedsmith/tests/test_innate_picker.py -q` | **123 passed.** `build_cell_groups` and `next_round_targets` take a `windows` argument; the three cell metrics read it off the ctx; the entrypoint loads it once (`load_scope_windows`) and it rides `ActionCoverageCtx.scope_windows` to every metric that already receives the ctx. | coverage_report/derive.py, coverage_report/ctx.py, generate_coverage_report.py |
| The innate picker takes the loaded windows | same command | **123 passed.** `CAP` and its `RUN_WINDOW` import are gone; `parse_candidate`, `pick_for_species` and `pick_all_species` take `cap` as a **required** parameter, and `generate_innate_picker.regenerate` computes it once as `load_scope_windows(rung_table_path)["species"][1]`. | innate_picker/derive.py, generate_innate_picker.py |
| A retuned window reaches **each** stage's output | same command | **Both new tests pass.** Coverage: a fixture with `general.ceiling = 6` moves the PLANNED cell's own `rungBand` to `(1, 6)`, and a row authored at that band counts as the planned cell rather than an off-window group. Innate: a fixture with `species.ceiling = 8` refuses a candidate authored at the shipped ceiling — the stage's own acceptance gate moves with the file. | tests/test_coverage_report.py, tests/test_innate_picker.py |
| Everything that shares the changed modules | `python -m pytest test_coverage_report.py test_innate_picker.py test_distribution_planner.py test_validate_heal.py test_characteristic_pool.py -q` | **386 passed, 1 skipped, 3 subtests passed.** | — |
| No window value is written in code | `python gk-core/scripts/audit-magic-numbers.py --summary` | **0 findings across every domain** — the audit sees no new window literal. | gk-forge/tools/seedsmith/*, gk-core/scripts/audit-magic-numbers.py |

## Deliberate deviations, both forced

1. **`coverage_report/ctx.py` is touched** (not in this task's Files line). The three cell metrics run
   through `run_all(registry, ctx)`, so the windows have to ride the ctx they already receive; adding
   the field is what lets the entrypoint load once and hand them to every metric without a second
   parameter threaded through `metrics/action_coverage.py`.
2. **Both entrypoints name the rung-table path by importing the planner's own `RUNGS_PATH`**
   (`from .generate_distribution_planner import RUNGS_PATH as RUNG_TABLE_PATH`) rather than each
   defining a path of their own. H7's whole point is one file for windows and structures, and ST5's
   own list moves `generate_distribution_planner.py:60` to v4 — with one name there is one place to
   bump instead of three that can drift apart.

## Test-call-site handling

`cap` became a required parameter with no fallback, so every parsing assertion has to supply the same
value production does. Rather than repeat the load at ~15 call sites, `test_innate_picker.py` gained
two module-level helpers — `_cap()` and `_parse_candidate(row)` — and `test_coverage_report.py` gained
`_windows()`. All three read the shipped file; no test pins a window value.

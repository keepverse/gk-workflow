# ST4.4 — `publish.py --reprice-rung-power-budget REF` + `--mark-tuned`

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `--reprice-rung-power-budget 800` writes v{n+1} | `python -m pytest gk-core/tools/tuning/test_publish_reprice.py -q` | **5 passed, 3 subtests passed.** `test_main_publishes_the_next_version_with_the_new_scalar` runs the real `main()` against a temp `TUNING_DIR` holding a v3 fixture and asserts a `action-rungs.v4.json` appears with `version: 4`. | gk-core/tools/tuning/publish.py, gk-core/tools/tuning/test_publish_reprice.py |
| Every row equals the published derivation at 800 | same command | **Passes.** Each row's `powerBudgetMilli` equals `poolRolls × 800 × qPowerMilli / 1000` — the same arithmetic `--add-rung-power-budget` derives with, read from the row's own columns, so the retune keeps the one-scalar property `_meta` promises instead of hand-setting ten cells. | gk-core/tools/tuning/publish.py |
| `_meta.referencePower == 800` | same command | **Passes**, in both the unit call and the end-to-end publish. | gk-core/tools/tuning/publish.py |
| `referencePowerUntuned` stays `true` unless `--mark-tuned` is given | same command | **Passes.** A reprice alone leaves it `true` (asserted with the reason in the message); `mark_tuned=True` clears it. The two are separate flags because "we repriced to the report's value" and "the owner signed this scalar off" are different statements (ruling 3). | gk-core/tools/tuning/publish.py |
| A table without the column is refused | same command | **Passes.** The refusal names the missing column and points at `--add-rung-power-budget` — this flag reprices a budget, it never introduces one. A non-positive (or boolean) REF is refused too. | gk-core/tools/tuning/publish.py |
| The suite | `python -m pytest gk-core/tools/tuning -q` | **26 passed, 3 subtests passed, 1 failed** — the failure is the pre-existing `test_resource_ownership.py::test_1_...` stale pin (it expects `aptitudes.v5.json`; v8 is shipped, and the test was last changed 2026-09-04 against a file that landed 2026-09-12). It is outside this session's fence and unrelated to this task; the same red is recorded at ST3.1. | gk-core/tools/tuning/** |

## Why two flags instead of one

`--reprice-rung-power-budget` alone would have been the smaller change, and it would have made the
"untuned" marker meaningless the moment anyone repriced to a test value. Ruling 3's whole point is that
a neutral scalar stays *visible* as neutral until someone decides otherwise, so clearing the marker is
its own explicit act: `--mark-tuned`.

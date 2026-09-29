# ISG7-follow-up — drop the retired `socket-word` name from `invents_identity` (closed 2026-09-21)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Residue dropped | `grep -n "invents_identity" -A9 gk-forge/tools/seedsmith/seedsmith/planner/schedule.py` | the frozenset lists `base-type, unique, set, charm, combination, consumable, gem, material` — no `socket-word` | `gk-forge/tools/seedsmith/seedsmith/planner/schedule.py` |
| Stale pin rewritten to the retiring contract | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q -k "stronger_model or renamed_not_removed or KINDS_assertion or ingredient_unsatisfiable_still_gates"` | `4 passed, 65 deselected in 0.34s` | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` |
| Planner tests green | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_schedule.py -q` | `14 passed in 0.24s` | `gk-forge/tools/seedsmith/tests/test_schedule.py` |
| Pre-existing red isolated, not caused | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | `1 failed, 82 passed` — `ChassisTests::test_the_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling` (`test_strain_splice_gen.py:294`, `4 != 8`), already in the H5 full-suite baseline | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` |
| `maxCombosPerActor` untouched | `git diff --name-only` on this commit | no `gk-core/data/tuning/**` path present | `gk-core/data/tuning/sockets.v1.json` |
| Second, inert residue routed (not silently left) | `grep -n "socket" gk-forge/tools/seedsmith/seedsmith/adapters/items/_registry_snapshot/allocated_partitions.json` | `116:  "socket-words": "socket-word",` → filed as **ISG7-F2** in `tasks/item-seedgen-todo.md` | `_registry_snapshot/allocated_partitions.json` |
| Path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-forge/tools/seedsmith/seedsmith/planner/schedule.py','gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py','tasks/item-seedgen-todo.md','tasks/evidence-fragments/ISG7-follow-up.md','tasks/seed-corpus-ledger.jsonl') -Session seed-corpus-20260920"` | exit `1`; doc-citations `0 HIGH`; session-boundary clean; `pytest: seedsmith` (module fallback) `21 failed, 4259 passed, 3 skipped` vs baseline `20 failed, 4260 passed, 3 skipped` | the one added failure, `test_audit_doc_citations.py::RealTreeTests::test_the_real_scan_runs_and_produces_a_report` (`doc_count 0`), is a transient `git ls-files`-under-load flake: it passes 4/4 in isolation (its whole file: `23 passed in 18.66s`) and scans only `docs/`, which this task does not touch |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- The full seedsmith suite was not re-run for this task; the H5-wire baseline (`20 failed, 4260 passed,
  3 skipped`) stands, and the two changed files' own groups are green (4 + 14).
- `socket-word` remains only where it is load-bearing history: the migration code (`combogen/migrate.py`,
  `combogen/authored.py`), the rename comments in `adapters/items/kinds.py`, the retired-kind handling in
  `metrics/linkage.py`, and the migration tests' legacy-kind fixtures. Those are the legacy kind's real
  names, not residue; they are deliberately kept.

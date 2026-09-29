# TVB0.2 — Drop the two pinned readings in test_resource_ownership.py

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `:38` `version == 5` and `:40` `len == 166` deleted; `:39` triple equality kept | read `gk-core/tools/tuning/test_resource_ownership.py:34-41` | both pins gone; `assert ro.edge_triples(generated) == ro.edge_triples(shipped)` remains as the contract | gk-core/tools/tuning/test_resource_ownership.py |
| no tuning file changes | `git status --porcelain -- gk-core/data/tuning` | empty (0 lines) | — |
| `gk-core/tools/tuning` suite fully green (was 18 passed / 1 failed — a reading) | `python -m pytest . -q -p no:cacheprovider` (cwd `gk-core/tools/tuning`) | `27 passed, 3 subtests passed in 0.26s` — exit 0 | — |
| the failing pin was the version (live highest aptitudes file is v8) | glob `data/tuning/aptitudes.v*.json` | v1–v8 present; highest v8 ≠ 5, so the deleted `version == 5` assert was the one failure | — |

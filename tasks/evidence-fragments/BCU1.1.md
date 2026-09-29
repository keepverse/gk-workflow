# BCU1.1 — paperwork-reconcile P1 (tools/infra todos)

9 files: rift-gate-todo.md, onboarding-rift-todo.md, debug-mcp-todo.md, game-control-todo.md,
live-probe-screenshot-todo.md, data-test-substrate-todo.md, phaser-kernel-todo.md,
overlay-switch-todo.md, world-map-runtime-gaps-todo.md, drop-tables-todo.md (10, matches lane E/F/G
lists).

```
$ python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes | grep -iE "rift-gate|onboarding-rift|debug-mcp|game-control"
(no output — all four suppressed by the new banner)
```

`audit-doc-citations.py --scope <file> --strict` run per file: 0 HIGH in every case. rift-gate-todo.md
(3 HIGH) and world-map-runtime-gaps-todo.md (5 HIGH) carry pre-existing HIGH findings far from the
edited lines (`git diff` confirms my hunks are lines 6-9 / 44-51 only) — not introduced by this batch.

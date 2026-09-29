# RS5 — the program's map + plan (module ids, CI decision)

Lane `rpg-simulator-map` · branch `cmdc/sim-map` · worktree
`D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-sim-map` (absolute).
Map: `docs/architecture/rpg-simulator-map.md` · Plan: `tasks/rpg-simulator-plan.md`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The map names every module id with a purpose and a spec path; the plan sequences only ids the map names | cross-read: 10 ids extracted from the map's module table, then every backticked kebab token in the plan/todo checked against it | 10/10 present; the only other kebab tokens are cross-program ids (`hibernation-clock`, `test-store-helper`) and lane/program names, each named as external in the map | map §Modules · plan §3–§4 |
| Every todo row carries its module id | read back | RS1 `first-session-scenario`; RS2.1–RS2.5 `scenario-format`/`readback-verdict`/`scenario-runner`/`inproc-host`/`process-host`; RS3 `clock-seam`; RS4 `honesty-guard`; RS6 `shared-store-home`; RS7 `sim-ci-lane`; RS5 is the index and names none | `tasks/rpg-simulator-todo.md` |
| No dead citation in any of the three docs | `python scripts/audit-doc-citations.py --scope docs/architecture/rpg-simulator-map.md --strict` | 60 resolvable citations, D1/D2/D3/D4 all 0, 0 HIGH, exit 0 | this file |
| (same, plan) | `python scripts/audit-doc-citations.py --scope tasks/rpg-simulator-plan.md --strict` | 35 citations, 0 D1–D4, 0 HIGH, exit 0 | this file |
| (same, todo) | `python scripts/audit-doc-citations.py --scope tasks/rpg-simulator-todo.md --strict` | 14 citations, 0 D1–D4, 0 HIGH, exit 0 | this file |
| Session boundary is clean and the worktree path is absolute | `powershell -NoProfile -Command "python scripts/session-boundary-check.py --session rpg-simulator-map"` | `[session-boundary] clean for 'rpg-simulator-map'`, exit 0 | this file |
| Path-owned verification for all five paths | `powershell -NoProfile -Command ".\scripts\verify-change.ps1 -Paths 'docs/architecture/rpg-simulator-map.md','tasks/rpg-simulator-plan.md','tasks/rpg-simulator-todo.md','tasks/evidence-fragments/RS5.md','tasks/sessions/rpg-simulator-map.json' -Session rpg-simulator-map"` | exit 0; `FusionRpg.Guard.Tests` 591 passed / 0 failed (5 m 38 s); `guard.doc-boundary` filter 4 passed / 0 failed (33 s); plan selected `docs-and-assistant-config` (focused), `session-and-program-records` (module) and `doc-citations` for all four docs; "full evidence: CI/nightly/release" printed, not run | this file |
| The CI decision is recorded (C3 (c): slice 0 local-only) | read back | map §"Decisions this map makes" 9; plan §2 C3 row + §4 wave 4; todo RS7 | all three |
| Nothing was built, booted or probed | — | the NOT-proved section in the map and in the plan | map/plan §NOT proved |

Pre-existing failure noted, not caused here: none — the change is docs-only and every selected check is
green.
Ledger: this program has no `tasks/rpg-simulator-ledger.jsonl` and neither idea lane created one, so the
run-state ledger protocol does not apply to this single-task docs lane; the acceptance evidence lives
in this fragment and in the report block.

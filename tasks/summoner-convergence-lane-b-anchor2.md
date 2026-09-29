# Anchor 2: summoner-convergence lane B — save-identity migration unit
Map: docs/architecture/solid-enforcement-map.md (SE wave 4, stage b) · Plan: tasks/summoner-convergence-plan.md §4 H2 · Todo: tasks/solid-enforcement-todo.md (§(b) `save-identity`, SE4.15–SE4.30 + Checkpoint 4b)
Specs: docs/architecture/solid-enforcement/spec-save-identity.md (migration steps 0–7, rollback, Contracts) · docs/architecture/spec-rulings-2026-09-18.md (R27)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: tasks/sessions/summoner-convergence-lane-b-20260919.json
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Data/SQL/schema, Anything) + decisions.md locks S1–S4 (read in the anchor-1 session)
Queue: SE4.15,SE4.16,SE4.17,SE4.18,SE4.19,SE4.20,SE4.21,SE4.22,SE4.23,SE4.24,SE4.25,SE4.26,SE4.27,SE4.28,SE4.29,SE4.30,SE4CP4b
Next: SE4.15
Peers: | lane D (SE waves 0–3) | SE0.x/SE1–SE3 | SE0.8 debt-ledger rows | guard runner | · | SP waves 1–7 + EP + BP | later lane-B anchors | the seams this unit provides (`HumanEmpireOf`, `EmpireRef` store API) | H2 |
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard per task Verify line; `test-fast.ps1 -AllDefault` at SE4.30 only.
H2 (binding): SE4.15–SE4.19 build the migration **dormant** (tests only) and SE4.20 is the one task that makes `Init` call it; no task writes a re-keyed row before SE4.20. R27: direct on the branch, SE4.20 last of the unit.
Blocked-out-of-agent: SE4.30's live rehearsal on a copy of a real save (orchestrator/owner) and the full suite; record blocked with the dependency named.
Guard-protected files: `gk-core/tests/FusionRpg.Guard.Tests/**` and `scripts/**` cannot be edited by this agent — record the intended content in the evidence fragment for `--allow-protected`.

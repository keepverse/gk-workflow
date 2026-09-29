# Anchor: summoner-convergence lane B (identity & progression) — anchor 1, identity foundation
Map: docs/architecture/solid-enforcement-map.md (SE wave 4) · docs/architecture/species-progression-map.md · Plan: tasks/summoner-convergence-plan.md §2 lane B, §4 H1/H2 · Todo: tasks/solid-enforcement-todo.md (wave 4: SE4.1–SE4.4, SE4.11–SE4.14 + Checkpoint 4a) then tasks/species-progression-todo.md (SP0.1–SP0.4 + Checkpoint 0)
Specs: docs/architecture/solid-enforcement/spec-commander-identity.md · spec-save-identity.md · docs/architecture/species-progression/spec-species-mod-ledger.md · docs/architecture/spec-rulings-2026-09-18.md (R2/R3/R16/R17/R27/R28)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: the fence in tasks/sessions/summoner-convergence-lane-b-20260919.json
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Anything, Data/SQL/schema, Stats, Creatures/unique, Battles) + decisions.md locks (Players S1, RpgProgression S2, key-widening S3, ownership bridge S4), read in this session
Queue: SE4.1,SE4.2,SE4.3,SE4.4,SE4.11,SE4.12,SE4.13,SE4.14,SE4CP4a,SP0.1,SP0.2,SP0.3,SP0.4,SPCP0
Next: SE4.1
Peers: | Lane A (actions) | tasks/summoner-convergence-lane-a-anchor.md | AE1.5 done, H1 position 3 consumed | SP1.2 follows here (H1 position 4) | · | Lane C (items) | species-gear-chain | SP/EP tables are born `(save_id, empire_id)` | — | · | Lane D (infra) | solid-enforcement waves 0–3 + OS | SE0.8 debt ledger row for SE4.1 | SE0.5 runner | · | Later anchors (this lane) | anchor 2 = migration unit SE4.15–SE4.30; then SP waves 1–7, EP, BP | seams | — |
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919` (+ `--plan-only` to preview)
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`); "no change" declares `No commit: <reason>`
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — append-only run-state (`anchor|task|note|gate|queue|complete`); EVERY event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`; never hand-write. `resume` first each window; `check` must exit 0.
Verify: focused filter + guard per task Verify line. The full suite (`test-fast.ps1 -AllDefault`) and live probes are orchestrator gates: record `blocked` with the dependency named, keep working.
H1: lane A consumed positions 1–3 (ST2.3 no-move, ST1.3 no-move, AE1.5 = commit `04b8daa0`). Lane B owns SP1.2 (C1 defect fix, H1 position 4) → SP6.1 → EP4.18. One cause per commit, never red. Register each in CV.2.
H2: SE4.20 (the task that turns the migration on) lands before any task that WRITES a `(save_id, empire_id)`-keyed row of a table it re-keys. SP0's ledger table is born in final shape, so it is exempt (todo says so).
Coupling: the one save-switch notice to the injector is built by SP6.6; SE and NS reuse it. `RpgStore.WorldTurns.cs` order: SP1.2 → EP1.14 → EP3.8/EP3.11 → EP4.18.
Next anchor: after SPCP0 this anchor names anchor 2 (save-identity migration unit, SE4.15–SE4.30 + Checkpoint 4b), then one anchor per SP/EP/BP plan/todo pair — continue in this same session, never stop between anchors.
Peers note: lane A's record was still `active` at setup and claimed 16 shared paths; it was marked `merged` (see ledger note) to satisfy the clean-boundary precondition.

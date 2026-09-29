# Anchor 3: summoner-convergence lane B — species-progression wave 0 close-out
Map: docs/architecture/species-progression-map.md (module 4) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 0 tail: SP0.5, SP0.6, SP0.7 + Checkpoint 0)
Specs: docs/architecture/species-progression/spec-species-mod-ledger.md (read in anchor 1's session) · docs/architecture/spec-rulings-2026-09-18.md
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: the fence in tasks/sessions/summoner-convergence-lane-b-20260919.json
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Anything, Data/SQL/schema, Stats) + decisions.md locks S1-S4, read in anchor 1's session
Queue: SP0.5,SP0.6,SP0.7,SPCP0
Next: SP0.5
Peers: | SE save-identity (this lane, done) | SE4.14 (owner empire of a specimen) | SP0.5's interim sheet join | done, no wait | · | solid-remediation-20260917 session | owns tests/** per this todo's own rule | SP0.6/SP0.7 test edits coordinate via hand-over, never a live merge wait | · | Guard.Tests | protected, add-only for this agent | SP0.4's own three-fact replacement stays a named blocker in SPCP0 | —
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard per task Verify line; full suite is orchestrator-owned (record blocked, keep working).
H-edges: none in this anchor's own queue — SP0.5/0.6/0.7 touch no golden and no re-keyed table (the ledger table was born in final shape at SP0.1, already committed). SP1.2 (H1 position 4) and SP6.0/SP6.1 (H7 tuning publish + golden re-bless) are named explicitly as OUT of this anchor's queue — they need their own anchor with full, unhurried attention, not folded in here.
Scope note: `tasks/species-progression-todo.md` is 429 lines across 7 waves (0-6+), several later waves carrying H1/H7 hard edges (SP1.2, SP6.0, SP6.1) and heavy EP/BP cross-coupling. Per the implement-anchor skill's size gate, this anchor covers ONLY wave 0's remaining tail (closing Checkpoint 0 as far as achievable); wave 1 onward is anchor 4+, built after this one closes.

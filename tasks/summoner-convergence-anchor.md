# Anchor: summoner-convergence
Map: none (parent; §1 of summoner-convergence-plan.md lists the 11 sub-program maps) · Plan: tasks/summoner-convergence-plan.md · Todo: tasks/summoner-convergence-todo.md (CV.1–CV.3, CC1–CC8)
Specs: docs/architecture/spec-rulings-2026-09-18.md (R1–R28, binding) · Handoff: tasks/summoner-convergence-handoff.md
Session: summoner-convergence-impl-20260918 (direct, features/mega-merge) · Paths: tasks/summoner-convergence-*; tasks/evidence-fragments/**; tasks/sessions/summoner-convergence-impl-20260918.json — lane build paths appended per lane start
Standards: PRINCIPLES + DESIGN-GATE §1 rows (Anything, Actions, Battle-engine-SSOT, Tunables, Magnitudes, Power, Caps, Stats) + decisions locks, read in this session
Peers: | action-skill-tiers | tasks/action-skill-tiers-anchor.md | holder-rung window + single cost scale | EffectiveRungOf resolver shared with action-enrich | · | action-enrich | (own anchor at lane start) | EffectiveRungOf resolver, qPower base | ST2 pre-scale line | · 9 more peer anchors at their lane starts |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <changed> -Session summoner-convergence-impl-20260918` (+ `-PlanOnly` to preview)
Evidence: `tasks/evidence-fragments/[task-id].md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-ledger.jsonl` — append-only run-state (`anchor|task|note|gate|complete`);
  one line per event, last line per id wins. A fresh agent runs `python gk-core/scripts/anchor-ledger.py
  <ledger> resume` first, never re-reads history. `... check` must exit 0; `resume` prints the
  brief (scope, done, blocked+reason, active, gates, last 5 notes, next action).
Verify: focused filter + guard per task Verify line, never full suite by default.
Active lane: A — ST2.1 → ST2.2 → ST2.3 (H1 #1) → ST2.4 → ST2.5, then ST1 wave per H1 order.
H1 chain: ST2.3 → ST1.3 → AE1.5 → SP1.2 → SP6.1 → EP4.18 (one cause per commit, never red).
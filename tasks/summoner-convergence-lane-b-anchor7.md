# Anchor 7: summoner-convergence lane B — species-progression wave 5 (`empire-species-container`) — BLOCKED
Map: docs/architecture/species-progression-map.md (module 5) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 5: SP5.1-SP5.5)
Specs: docs/architecture/species-progression/spec-empire-species-container.md (read in full this session)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: unchanged fence, covers Core/Data/Server/Injector/tools/tests
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Actor layer stack, Stats/Aptitudes) + decisions.md locks, read in anchor 1's session
Queue: (none — blocked before any task started)
Next: none in this wave; proceeding to wave 6 (anchor 8)
Peers: none new
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/SP5.1.md` records the full blocker (real code checked, not the spec's own assumed-future shape)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl`

BLOCKED, no task started: SP5.1's own reprojection function needs `ai-empire-species`'s
`SpeciesLevelOf(SaveId, EmpireId, typeId)` (`empire-progression` `EP4.13`) and a re-key of
`EffectiveSpeciesAllocationUnlocked` (`RpgStore.Aptitudes.cs:210-239`) to `EmpireRef` — neither exists;
`empire-progression` has not been started by any lane (`ls tasks/evidence-fragments/ | grep '^EP4\.'` =
zero). Per this session's contract: stop and record the blocker naming the edge; do not ship a partial
(Zomboss-unaware) ordering that would need redoing once `EP4.13` lands. SP5.1-SP5.5 all build on SP5.1's
own function, so the whole wave is skipped, not partially built.

Confirmed NOT blocked, per the map's own module-6 dependency row (step 6.1 needs module 1 + `action-base`'s
re-bless; step 6.2 needs module 4; only step 6.3 needs module 5): wave 6 steps 6.1 (SP6.0-SP6.1) and 6.2
(SP6.2-SP6.9) proceed now. Step 6.3 (SP6.10-SP6.11) is recorded blocked on the same dependency when reached.

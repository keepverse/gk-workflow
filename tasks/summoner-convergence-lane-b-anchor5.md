# Anchor 5: summoner-convergence lane B — species-progression wave 2 (`ladder-scale-parity`)
Map: docs/architecture/species-progression-map.md (module 2) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 2: SP2.1-SP2.2)
Specs: docs/architecture/species-progression/spec-ladder-scale-parity.md (full code sample provided, read in full this session)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: unchanged fence, covers Core/Data/Server/Injector/tools/tests
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Numeric types/overflow, Stats/Aptitudes, Effect atoms) + decisions.md locks, read in anchor 1's session; CLAUDE.md "Numeric types — overflow is RANGE" rule applies directly (widen before multiply, checked/throw, no clamp)
Queue: SP2.1,SP2.2
Next: SP2.1
Peers: none new — module 2 depends on nothing
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard/audit per task Verify line; full suite is orchestrator-owned (record blocked, keep working).
H-edges: SP2.2 carries its own **named Ask-first gate** (not H1-H7, but the same discipline): "If a golden moves, report the list and stop... that is the Ask-first, not a re-bless." If TreeBinder/tree-resolve/BattleGoldenTests show ANY moved value, record SP2.2 **blocked** with the exact moved values named, do not re-bless unilaterally, and continue with the next unblocked queue item (per the coordinator's explicit instruction).
Correction (coordinator, this session): existing Guard.Tests files are add-only from here on — the manager is reviewing this lane's two prior edits to existing Guard.Tests files (SP0.4 rewrite, DebugScopeGuardTests fix). Any further needed change to an EXISTING Guard.Tests file is recorded as a ledger blocker note, never edited directly. New Guard.Tests files authored by this lane remain fine.

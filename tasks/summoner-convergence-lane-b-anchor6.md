# Anchor 6: summoner-convergence lane B — species-progression wave 3 (`species-layer-projector`)
Map: docs/architecture/species-progression-map.md (module 3) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 3: SP3.1-SP3.8 + Checkpoint 1)
Specs: docs/architecture/species-progression/spec-species-layer-projector.md (full code sample provided, read in full this session)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: unchanged fence, covers Core/Data/Server/Injector/tools/tests
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Actor layer stack, Stats/Aptitudes, Effect atoms) + decisions.md locks, read in anchor 1's session
Queue: SP3.1,SP3.2,SP3.3,SP3.4,SP3.5,SP3.6,SP3.7,SP3.8
Next: SP3.1
Peers: none new — module 3 depends on module 1 (`layer-source-selector`, done) and module 2 (`ladder-scale-parity`, SP2.1 done; SP2.2 blocked at Ask-first, not a listed dep of any SP3.x task per the todo's own per-task `deps:` rows)
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard/audit per task Verify line; full suite is orchestrator-owned (record blocked, keep working).
Reviewed-vocabulary notes (spec Boundaries: "Ask first: the ContainerKind addition and the §8.1 amendment"): SP3.1 (three `actor-hub-ssot.md` §8.1 rows) and SP3.2 (`ContainerKind.SpeciesProgression`) are closed-vocabulary changes. The spec's own SP3.1 acceptance text reads "spec Ask-first; the change is shown in review" — softer than SP2.2's literal "stop at Ask-first" — so both are BUILT and flagged clearly in their commit bodies as reviewed vocabulary changes, matching every prior closed-vocab addition this lane has already made (SP0.x, SP1.x), not blocked outright. If the manager wants either reverted pending explicit sign-off, that is a correction to apply after the fact, not a reason to stall wave 3.
H-edges: none of SP3.1-SP3.8 individually cross H1/H2/H7 — SP3.4's parity claim reuses SP2.1's already-blessed `LadderScale.Micro` (not SP2.2's blocked AtomCompiler wiring), so no golden-move risk carries over from the SP2.2 block.
Carry-forward: existing Guard.Tests files stay add-only (manager reviewing SP0.4/DebugScopeGuardTests edits) — no SP3.x task touches Guard.Tests per its Files list, so this should not recur here.

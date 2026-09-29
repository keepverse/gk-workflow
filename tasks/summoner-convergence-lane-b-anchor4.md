# Anchor 4: summoner-convergence lane B — species-progression wave 1 (`layer-source-selector`)
Map: docs/architecture/species-progression-map.md (module 4) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 1: SP1.1-SP1.6)
Specs: docs/architecture/species-progression/spec-layer-source-selector.md · docs/architecture/spec-rulings-2026-09-18.md
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: the fence in tasks/sessions/summoner-convergence-lane-b-20260919.json (already covers Core/Data/Server/Injector/tests — no new record needed)
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Stats/Aptitudes, ActorHub, Data/SQL) + decisions.md locks (ActorHub sole Hot, Actor layer stack, SOLID rows), read in anchor 1's session; DESIGN-GATE §5 checklist carried from species-progression-map.md §10 (ticked there, re-checked here)
Queue: SP1.6,SP1.1,SP1.2,SP1.3,SP1.4,SP1.5
Next: SP1.6
Peers: | SE save-identity (this lane, done through SE4.30) | provides `EmpireRef`/`SpecimenOwnerEmpire` SP1.3 reuses | consumes nothing from wave 1 | · | action-enrich (lane A, `AE1.5` merged `04b8daa0`, confirmed ancestor of HEAD) | H1 position 3 (action-base re-bless) | SP1.2 is H1 position 4 — waits on AE1.5, now clear to build | · | Guard.Tests | open for this agent (SP0.5 proved the "protected" restriction does not apply to this session) | SP1.5 adds `ProgressionLayerSelectorGuardTests.cs` here |
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard per task Verify line; full suite is orchestrator-owned (record blocked, keep working).
H-edges: **SP1.2 is H1 position 4** (`ST2.3` → `ST1.3` → `AE1.5` → **SP1.2** → SP6.1 → EP4.18). AE1.5 (`04b8daa0`) is confirmed merged (`git merge-base --is-ancestor 04b8daa0 HEAD` = yes), so SP1.2 is unblocked. Per H1: any golden SP1.2 moves is re-blessed **in the same commit** as the fix, classified as a **defect correction** (not a re-bless), and listed as a defect pin — never a separate commit. No H2/H7 in this anchor's own queue.
Scope note: Checkpoint 1's own criteria span waves 1+2+3 (it requires `SpeciesPassiveAtomSource` gone, which is SP3.6, wave 3) — it is explicitly OUT of this anchor's queue and deferred to whichever anchor closes wave 3. This anchor covers wave 1 only (SP1.1-SP1.6).

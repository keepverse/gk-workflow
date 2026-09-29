# Anchor 8: summoner-convergence lane B — species-progression wave 6 (`species-layer-delivery`), steps 6.1 + 6.2
Map: docs/architecture/species-progression-map.md (module 6) · Plan: tasks/species-progression-plan.md · Todo: tasks/species-progression-todo.md (wave 6: SP6.0-SP6.9; step 6.3 SP6.10-SP6.11 blocked, see below)
Specs: docs/architecture/species-progression/spec-species-layer-delivery.md (472 lines, read in full this session)
Session: summoner-convergence-lane-b-20260919 (worktree, cmdc/lane-b) · Paths: unchanged fence, covers Core/Data/Server/Injector/tools/tests
Standards: docs/PRINCIPLES.md + DESIGN-GATE §1 rows (Actor layer stack, Stats/Aptitudes) + decisions.md locks, read in anchor 1's session
Queue: SP6.0,SP6.1,SP6.2,SP6.3,SP6.4,SP6.5,SP6.6,SP6.7,SP6.8
Next: SP6.0
Peers: none new
Drift gates: `python scripts/session-boundary-check.py` · `.\scripts\verify-change.ps1 -Paths <changed> --session summoner-convergence-lane-b-20260919`
Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/summoner-convergence-lane-b-ledger.jsonl` — every event through `python gk-core/scripts/anchor-ledger.py <ledger> ...`
Verify: focused filter + guard/audit per task Verify line; full suite is orchestrator-owned (record blocked, keep working).

H-edges — SP6.0 is H7 (tuning publish, both host readers switch same commit). SP6.1 is THE program's one
explained H1 golden re-bless: confirmed both hard preconditions landed before starting —
(1) `action-enrich action-base`'s re-bless: `BasicAttack.cs:365-367`'s own comment confirms `LiveAtk`
already left production reads, replaced by `ActionBaseMath.BasePerHit`/`ActionBaseDerivation.BasePowerMilli`
(AECP1.md/AECP2.md checkpoints closed); (2) module 1 (`layer-source-selector`) C1 fix, SP1.2, closed this
lane's own Checkpoint 1. SP6.1 follows the spec's own 6-step procedure exactly (§"Step 6.1", "The
procedure, in this order"): before/after over BattleGoldenTests/ModeComposeParity/AptitudeResolver/
PointBudget/AllocationStore/WorldTurn for every actor with 2+ non-empty scopes, classify each failure
(re-bless only if 2+ scopes (R2/R16) or 1 scope with weight != 1000 (R21)), one commit with the full
per-value table (before/after/share vectors/unweighted+weighted), 3 named tests REWRITTEN not re-blessed.

Order lock respected: action-base first (done), module 1 C1 second (done), step 6.1 third (this anchor),
steps 6.2/6.3 never re-bless.

Step 6.3 (SP6.10, SP6.11) is BLOCKED: its own `deps:` line names SP5.4 (module 5, `empire-species-container`),
which anchor7 already recorded blocked on `empire-progression` EP4.13 (`SpeciesLevelOf`) not existing.
Step 6.3 is deferred until wave 5 unblocks; NOT in this anchor's queue.

SP6.9 (live proof of 1b + perf) needs a real running game/server (`live-probe-standard.md`, `/execute`
route, `gk-core/scripts/probe_perf.py`) — outside a background implementer's own capability without the owner's machine.
Recorded blocked (owner-only) when reached, per the same discipline `goal-loop-owner-only-gate` established
elsewhere in this program's history; SP6.2-SP6.8's own code/test work does not need it.

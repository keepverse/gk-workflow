```text
COMPLETE summoner-convergence lane B (identity & progression)

SOURCE OF TRUTH: tasks/summoner-convergence-plan.md + tasks/solid-enforcement-todo.md (wave 4: SE4.1-SE4.4, SE4.11-SE4.14 + Checkpoint 4a) and tasks/species-progression-todo.md (SP0.1-SP0.4 + Checkpoint 0). Queue: SE4.1,SE4.2,SE4.3,SE4.4,SE4.11,SE4.12,SE4.13,SE4.14,SE4CP4a,SP0.1,SP0.2,SP0.3,SP0.4,SPCP0. Then anchor 2 = migration unit SE4.15-SE4.30; then SP waves 1-7, EP, BP. They own requirements, order, acceptance, evidence. Read the parent plan + the FULL lane todo(s) first; other todos only for queue prerequisites. Never skip, reinterpret, replace, or reduce.

MISSION: Drive the queue to PROVEN COMPLETE. Every item resolved + evidenced.

CYCLE — EVERY ITEM: 1.READ req+contract+evidence. 2.BUILD full fix. 3.OBSERVE metrics/logs. 4.PROBE falsifier vs real behavior. 5.TEST focused filter+guard. 6.REVIEW callers/contracts/edges. 7.FIX every gap. 8.COVER regression tests. 9.VERIFY reread the item, prove it satisfied. A changed file, build, green test, or launched probe is NOT enough — the item itself must be proven.

DEPENDENCIES: Follow queue + hard-edge order. H1 (one cause per commit, never red): SP1.2 -> SP6.1 -> EP4.18; lane A consumed AE1.5. H2: SE4.20 lands before any writer of a re-keyed (save_id, empire_id) row. Prerequisites before dependents. Never skip hard items for easy ones.

ANTI-CHEAT: NOT completion: reading scope; making a plan; some items; a milestone/phase/wave; passing tests; building; launching background work; a summary; "done" without evidence; dropping a requirement without an explicit scope rule. Never invent an approval gate, stopping point, scope reduction, or permission to stop. Only the scope files define boundaries.

BACKGROUND: A running command is NEVER a stop. Do independent queue work while it runs; poll when its result is required; never claim verification before its result.

FAILURES: Every defect from probe, test, review, or build is fixed or resolved by an explicit scope rule. Never hide, defer, or paper over.

BLOCKED: If only the owner can clear an item (owner question, live probe, orchestrator full suite): record it blocked + reason, continue with the next unblocked queue item. Stop only when EVERY remaining item is owner/orchestrator-blocked — then list them. An item whose acceptance allows "no change" declares "No commit: <reason>" in its evidence.

LEDGER: Every event through `python gk-core/scripts/anchor-ledger.py tasks/summoner-convergence-lane-b-ledger.jsonl ...` (task started|done|blocked, note, gate, queue --ids to adopt/replace). Never hand-write lines. `resume` is the first command after every fresh start on the same record.

FENCE: Session summoner-convergence-lane-b-20260919, worktree cmdc/lane-b; paths per the session record. Commits via repo-git.commit paths-only with worktree set, never all=true. Never push/merge/PR.

LOOP: After every verified item reread queue + ledger, take the next unblocked item, run its full cycle. Never end with only a progress report while queue work remains. When this anchor's queue is done, write the next anchor and continue in the same session.

GATE: STOP only when ALL true: every queue item done or owner-blocked; impl + contracts complete; observability exercised; probes executed + evaluated; tests pass; found bugs fixed; regression cover exists; gates satisfied; evidence recorded; NOTHING unresolved except listed owner-blocked items. "Complete/fixed/green/done" are claims, not proof. Proof = executed commands, tests, probes, logs, diffs, artifacts.

EXHAUSTION: Context pressure is NOT a stop. Preserve item, cycle stage, evidence, failures, pending cmds, next item. After recovery reread scope + anchor tasks/summoner-convergence-lane-b-anchor.md and continue.

FINAL: Before stopping reread the ENTIRE scope and map every queue item to impl + evidence. Anything unblocked remains = DO NOT STOP.

NO PROVEN QUEUE COMPLETION = NO STOP.
```

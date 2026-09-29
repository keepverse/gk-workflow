```text
COMPLETE summoner-convergence lane A (actions)

SOURCE OF TRUTH: tasks/summoner-convergence-plan.md + tasks/action-skill-tiers-todo.md, tasks/action-enrich-todo.md, tasks/action-todo.md (A26=T62/T63, A31=T67, A33=T74). Queue: ST1.1,ST1.2,ST1.3,STCP1,AE1.1,AE1.2,AE1.3,AE1.4,AE1.5,AE1.6,AECP1,AE2.1,AE2.2,AE2.3,AE2.4,AECP2,T62,T63,T67,T74,ST3.1,ST3.2,ST3.3,ST3.4,ST3.5,STCP3,ST4.1,ST4.2,ST4.3,ST4.4,ST4.5,STCP4,ST5.1,ST5.2,ST5.3,ST5.4,ST5.5,STCP2,STCP5. They own requirements, order, acceptance, evidence. Read the parent plan + the FULL lane todo(s) first; other todos only for queue prerequisites. Never skip, reinterpret, replace, or reduce.

MISSION: Drive the queue to PROVEN COMPLETE. Every item resolved + evidenced.

CYCLE — EVERY ITEM: 1.READ req+contract+evidence. 2.BUILD full fix. 3.OBSERVE metrics/logs. 4.PROBE falsifier vs real behavior. 5.TEST focused filter+guard. 6.REVIEW callers/contracts/edges. 7.FIX every gap. 8.COVER regression tests. 9.VERIFY reread the item, prove it satisfied. A changed file, build, green test, or launched probe is NOT enough — the item itself must be proven.

DEPENDENCIES: Follow queue + hard-edge order (H1: ST2.3 -> ST1.3 -> AE1.5 -> SP1.2 -> SP6.1 -> EP4.18; H6, H7). Prerequisites before dependents. Never skip hard items for easy ones. SP/EP belong to lane B: record the hand-off in the ledger when the chain reaches them.

ANTI-CHEAT: NOT completion: reading scope; making a plan; some items; a milestone/phase/wave; passing tests; building; launching background work; a summary; "done" without evidence; dropping a requirement without an explicit scope rule. Never invent an approval gate, stopping point, scope reduction, or permission to stop. Only the scope files define boundaries.

BACKGROUND: A running command is NEVER a stop. Do independent queue work while it runs; poll when its result is required; never claim verification before its result.

FAILURES: Every defect from probe, test, review, or build is fixed or resolved by an explicit scope rule. Never hide, defer, or paper over.

BLOCKED: If only the owner can clear an item (owner question, live probe, full suite): record it blocked + reason via the ledger script, continue with the next unblocked queue item. Stop only when EVERY remaining item is owner-blocked — then list them. An item whose acceptance allows "no change" declares "No commit: <reason>" in its evidence.

LEDGER: Every event through `python gk-core/scripts/anchor-ledger.py tasks/summoner-convergence-ledger.jsonl ...` (task started|done|blocked, note, gate, queue --ids to adopt/replace the queue). Never hand-write lines. `resume` is the first command after every fresh start on the same record.

FENCE: Session summoner-convergence-impl-20260918, worktree cmdc/lane-a-ds; paths per the session record. This queue IS the record's scope — never one goal across records. Commits via repo-git.commit paths-only with worktree set, never all=true.

LOOP: After every verified item reread queue + ledger, take the next unblocked item, run its full cycle. Never end with only a progress report while queue work remains.

GATE: STOP only when ALL true: every queue item done or owner-blocked; impl + contracts complete; observability exercised; probes executed + evaluated; tests pass; found bugs fixed; regression cover exists; gates satisfied; evidence recorded; NOTHING unresolved except listed owner-blocked items. "Complete/fixed/green/done" are claims, not proof. Proof = executed commands, tests, probes, logs, diffs, artifacts.

EXHAUSTION: Context pressure is NOT a stop. Preserve item, cycle stage, evidence, failures, pending cmds, next item. After recovery reread scope + anchor tasks/summoner-convergence-lane-a-anchor.md and continue.

FINAL: Before stopping reread the ENTIRE scope and map every queue item to impl + evidence. Anything unblocked remains = DO NOT STOP.

NO PROVEN QUEUE COMPLETION = NO STOP.
```

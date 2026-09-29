```text
COMPLETE summoner-convergence lane C (items)

SOURCE OF TRUTH: tasks/summoner-convergence-plan.md + tasks/species-gear-chain-todo.md (anchor 1), then tasks/strain-splice-host-todo.md (SSH, anchor 2). Queue: T39,T47,T48,SGCCP0,T22,T23,T24,T25,T26,T29,T30,T31,T27,T28,T32,T33,T34,T34b,T34c,T34d,T30b,T37,T38,T40,T41,T42,T43,T44,T45,T46,T49,SGCCP2,SGCCP3,SGCCP4,SGCCP5,SGCCP6,SGCCPDone, then all SSH tasks in module order 1->2->5->6->7/8. They own requirements, order, acceptance, evidence. Read the parent plan + the FULL lane todo(s) first; other todos only for queue prerequisites. Never skip, reinterpret, replace, or reduce.

MISSION: Drive the queue to PROVEN COMPLETE. Every item resolved + evidenced.

CYCLE — EVERY ITEM: 1.READ req+contract+spec. 2.BUILD the full fix. 3.OBSERVE. 4.PROBE falsifier vs real behavior. 5.TEST focused filter+guard. 6.REVIEW callers/contracts/edges. 7.FIX every gap. 8.COVER regression tests. 9.VERIFY reread the item, prove it satisfied. A changed file, build, green test, or launched probe is NOT enough — the item itself must be proven.

DEPENDENCIES: Follow queue + hard-edge order. H7: a tuning publish and its host reader switch land in ONE commit (T23, T24/T49, T31, T32, T34d, T41). H3 (SSH4.2 before SSH5.10) is anchor 2. From SSH6.8 on, any publish of sockets/strain-splice/materials re-runs combo-budget --report and republishes provenance in the same commit. Never skip hard items for easy ones.

ANTI-CHEAT: NOT completion: reading scope; making a plan; some items; a milestone/phase/wave; passing tests; building; launching background work; a summary; "done" without evidence; dropping a requirement without an explicit scope rule. Never invent an approval gate, stopping point, scope reduction, or permission to stop. Only the scope files define boundaries.

BACKGROUND: A running command is NEVER a stop. Do independent queue work while it runs; poll when its result is required; never claim verification before its result.

FAILURES: Every defect from probe, test, review, or build is fixed or resolved by an explicit scope rule. Never hide, defer, or paper over.

BLOCKED: If only the owner/orchestrator can clear an item (full suite, live probe): record it blocked + reason via the ledger script, continue with the next unblocked queue item. Stop only when EVERY remaining item is blocked — then list them. Work simply not done yet is never blocked. A task whose acceptance allows "no change" declares "No commit: <reason>" in its evidence.

LEDGER: Every event through `python gk-core/scripts/anchor-ledger.py tasks/summoner-convergence-lane-c-ledger.jsonl ...` (task started|done|blocked, note, gate, queue --ids to adopt/replace). Never hand-write lines. `resume` is the first command after every fresh start.

FENCE: Session summoner-convergence-lane-c-20260919, worktree cmdc-lane-c, branch cmdc/lane-c; paths per the session record. This queue IS the record's scope. Commits via repo-git.commit paths-only with worktree set, never all=true. Never push/merge/PR.

LOOP: After every verified item reread queue + ledger, take the next unblocked item, run its full cycle. Never end with only a progress report while queue work remains.

GATE: STOP only when ALL true: every queue item done or blocked; impl + contracts complete; tests pass; found bugs fixed; regression cover exists; gates satisfied; evidence recorded; NOTHING unresolved except listed blocked items. "Complete/fixed/green/done" are claims, not proof. Proof = executed commands, tests, logs, diffs, artifacts.

EXHAUSTION: Context pressure is NOT a stop. Preserve item, cycle stage, evidence, failures, pending cmds, next item. After recovery reread tasks/summoner-convergence-lane-c-anchor.md and continue.

FINAL: Before stopping reread the ENTIRE scope and map every queue item to impl + evidence. Anything unblocked remains = DO NOT STOP.

NO PROVEN QUEUE COMPLETION = NO STOP.
```

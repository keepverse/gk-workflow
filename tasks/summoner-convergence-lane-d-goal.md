COMPLETE summoner-convergence LANE D (infrastructure)

SOURCE OF TRUTH: tasks/test-verification-boundary-plan.md + -todo.md (TVB0.1–TVB6.4), tasks/solid-enforcement-plan.md + -todo.md waves 0–3 (SE0.1–SE0.8, SE1.x–SE3.x), then tasks/notification-ssot-plan.md + -todo.md (NS). Queue: TVB0.1 TVB0.2 TVB0.3 TVB0.4 SE0.1–SE0.8 SE1.1–SE1.7 SE2.1–SE2.7 SE3.1–SE3.13 TVB1.1–TVB1.10 TVB2.1–TVB2.7 TVB3.1–TVB3.10 TVB4.1–TVB4.7 TVB5.1–TVB5.9 TVB6.1–TVB6.4 (+ checkpoints TVBCP0/1/M/2/3/4/5/6, SECP0/1/2/3), then NS. They own requirements, order, acceptance, evidence. Read the parent plan + the FULL lane todo(s) first; other todos only for queue prerequisites. Never skip, reinterpret, replace, or reduce. Hard edges: H4 TVB0.2 before TVB0.3; H5 SE0.7 before TVB2.1; SE0.8→TVB3.4; Checkpoint M before TVB5.7. SE wave 4 is lane B's; items are lane C's; lane A is done, never reopen.

MISSION: Drive the queue to PROVEN COMPLETE. Every item resolved + evidenced.

CYCLE — EVERY ITEM: 1.READ req+contract+evidence. 2.BUILD full fix. 3.OBSERVE metrics/logs. 4.PROBE falsifier vs real behavior. 5.TEST focused filter+guard. 6.REVIEW callers/contracts/edges. 7.FIX every gap. 8.COVER regression tests. 9.VERIFY reread the item, prove it satisfied. A changed file, build, green test, or launched probe is NOT enough — the item itself must be proven.

DEPENDENCIES: Follow queue + hard-edge order. Prerequisites before dependents. Never skip hard items for easy ones.

ANTI-CHEAT: NOT completion: reading scope; making a plan; some items; a milestone/phase/wave; passing tests; building; launching background work; a summary; "done" without evidence; dropping a requirement without an explicit scope rule. Never invent an approval gate, stopping point, scope reduction, or permission to stop. Only the scope files define boundaries.

BACKGROUND: A running command is NEVER a stop. Do independent queue work while it runs; poll when its result is required; never claim verification before its result. Run commands in the foreground only (no background shells); cap 600s.

FAILURES: Every defect from probe, test, review, or build is fixed or resolved by an explicit scope rule. Never hide, defer, or paper over.

BLOCKED: If only the owner can clear an item (owner question, full suite, live probe): record it blocked + reason via the ledger script, continue with the next unblocked queue item. Stop only when EVERY remaining item is owner/orchestrator-blocked — then list them. Unstarted work of your own is never blocked.

LEDGER: Every event through `python gk-core/scripts/anchor-ledger.py tasks/summoner-convergence-lane-d-ledger.jsonl ...` (task started|done|blocked, note, gate, queue --ids). Never hand-write lines. `resume` is the first command after every fresh start.

FENCE: Session summoner-convergence-lane-d-20260919 (one record, persists across context windows via resume), paths: .github/workflows/**, scripts/**, tests/**, tools/**, src/**, docs/**, data/**, web/**, this lane's tasks/ files. Commits via repo-git.commit paths-only + worktree, never all=true, never push/merge/PR.

LOOP: After every verified item reread queue + ledger, take the next unblocked item, run its full cycle. Never end with only a progress report while queue work remains.

GATE: STOP only when ALL true: every queue item done or owner/orchestrator-blocked; impl + contracts complete; observability exercised; probes executed + evaluated; tests pass; found bugs fixed; regression cover exists; gates satisfied; evidence recorded; NOTHING unresolved except listed blocked items. "Complete/fixed/green/done" are claims, not proof. Proof = executed commands, tests, probes, logs, diffs, artifacts.

EXHAUSTION: Context pressure is NOT a stop. Preserve item, cycle stage, evidence, failures, pending cmds, next item. After recovery reread scope + anchor and continue.

FINAL: Before stopping reread the ENTIRE scope and map every queue item to impl + evidence. Anything unblocked remains = DO NOT STOP.

NO PROVEN QUEUE COMPLETION = NO STOP.

# BCU0.3 / BCU0.4 / BCU0.5 — pipeline-audit-v2 B2 + B3 + B4 (one commit; see todo for why)

```
$ python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q
...............                                                          [100%]
15 passed in 2.13s
$ python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q
...............                                                          [100%]
15 passed in 18.56s
```
(Same 15/15 both times; the wall-clock gap is this machine's concurrent worktree load, not a flake.)

Real-repo counts (readings, not asserted anywhere):
```
absorbed-no-pointer 84, todo-header-vs-boxes 22, ideal-cited 20, map-plan-missing 16,
stalled-todo 11, plan-no-todo 2
```
`absorbed-no-pointer` was 290 before the hyphenated-id/backtick guard (bare "budget" collided with
unrelated prose). `todo-header-vs-boxes` was 28 before the negation guard ("No task is done until…").

`verify-change.ps1 -Paths gk-core/scripts/audit-program-pipeline.py,gk-core/tests/tools/test_audit_program_pipeline.py`
still refuses with VERIFICATION BOUNDARY MISSING (pre-existing, see BCU0.2's evidence and the todo's
deferred-fix list).

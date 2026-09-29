# BCU0.2 — pipeline-audit-v2 B1 (blockquote status banners)

```
$ python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q
...                                                                      [100%]
3 passed in 0.15s
$ python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q
...                                                                      [100%]
3 passed in 0.11s
```

`verify-change.ps1 -Paths gk-core/scripts/audit-program-pipeline.py,gk-core/tests/tools/test_audit_program_pipeline.py`
refuses: `VERIFICATION BOUNDARY MISSING: gk-core/scripts/audit-program-pipeline.py` — pre-existing (v1 was
never registered either). `gk-core/scripts/verification-boundaries.v1.json` is in the active diff of
cmdc/lane-b, cmdc/lane-c, cmdc/lane-d, worktree-agent-a7caaafc906532c18 (lane D2) and
worktree-agent-ae078137978cf8e26 (lane A2) right now — deferred in the todo's deferred-fix list
rather than edited.

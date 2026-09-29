# TVB-F36 manager repair — checked H-checkbox headings

**Status:** focused repair ready for exact-SHA acceptance.

## Finding and fix

The `H-checkbox-heading` shape in `gk-core/scripts/audit-program-pipeline.py` recognized headings such as
`## - [x] ...`, but the block classifier's generic fallthrough treated the heading as prose/open.
The repair adds one explicit checked-heading predicate. An explicit `(OPEN)` declaration still wins;
checked headings are closed, and unticked acceptance boxes inside them remain shaded contract lines.

The regression fixture covers one checked heading with an unticked acceptance box and one open sibling.
It does not read the real repository or pin a population count.

## Verification

```text
python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q -p no:cacheprovider
# 26 passed; exit 0

python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
# exit 0
# TOTAL open=671 done=2885 boxes=1884 shaded=843 unmeasured=2
```

The pre-repair inventory reading at the earlier snapshot was `open=696 done=2858`; the change is a
classifier correction, not a claim that 25 task blocks were completed. The exact current census is a
reading, not a work/effort total. `git diff --check` passed. External log SHA-256:
`9829F7B977ED5E686D80E067C3A9AB34FC821EE1FAB19A1405178ADB896DA7D6`.

## Boundary

No product code, generated data, CI, verification-boundary registry, or other task ledger changed.
The separate onboarding-rift header/heading contradiction is recorded as `BCU2-R1`; it is not hidden
by this classifier fix. Manager must run the focused test and census again from a clean checkout at
the exact reviewed SHA before merging.

<<<REPORT {"status":"done","summary":"Repaired the H-checkbox-heading task-block classifier: checked checkbox headings now close as done, explicit OPEN declarations still win, and a regression fixture proves checked/open sibling behavior. The focused audit suite passes 26/26 and the reproducible census exits 0 with open=671, done=2885, boxes=1884, shaded=843, unmeasured=2; the count remains a reading, not a work total.","changed_files":["gk-core/scripts/audit-program-pipeline.py","gk-core/tests/tools/test_audit_program_pipeline.py","tasks/reports/resume-14-tvb-f36-classifier-20260925.md"],"verification":["pytest gk-core/tests/tools/test_audit_program_pipeline.py -q -p no:cacheprovider — 26 passed","python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks — exit 0","git diff --check — exit 0","external log SHA-256 9829F7B977ED5E686D80E067C3A9AB34FC821EE1FAB19A1405178ADB896DA7D6"],"open_issues":["exact-SHA clean checkout and manager merge remain","onboarding-rift ledger contradiction is separately filed as BCU2-R1","the census still contains other stale/contradictory rows"],"next_steps":["commit exact reviewed SHA","clean-checkout pytest/census/diff verification","merge manager acceptance and refresh the consolidated inventory reading"]} REPORT>>>

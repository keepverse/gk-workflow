# BCU7.5 — achievement-title T7b scheduling

Identified: "P4 rail work" is gui-lego's own P4 priority, confirmed fully shipped this session
(BCU7.3). FE toolchain half also cleared (npm ci, BCU7.1). T7b itself stays genuinely open: no
Hall-console/actor-title-tab React component exists yet, real unbuilt fold+mount work plus an
owner-only side-by-side visual gate. Corrected the blocker description to match.

```
$ python scripts/audit-doc-citations.py --scope tasks/achievement-title-todo.md --strict
0 HIGH (10 pre-existing D1, not HIGH)
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH
```

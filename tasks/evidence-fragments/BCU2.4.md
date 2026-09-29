# BCU2.4 — lawn plan

New files: tasks/lawn-plan.md, tasks/lawn-todo.md (16 tasks, LW1.1-LW4.2, 4 waves).
Edited: both lawn maps' Plan/Tasks lines.

```
$ python gk-core/scripts/audit-program-pipeline.py --only map-plan-missing | grep -i lawn
(no output)
$ python gk-core/scripts/audit-program-pipeline.py --only spec-no-plan | grep -i lawn
(no output)
```

Real defect caught and fixed: the map text originally quoted the literal old promised filenames
("tasks/lawn-playable-plan.md") even while explaining they were superseded -- the audit's own regex
matched that literal string regardless of context, so map-plan-missing kept firing. Reworded to
describe the supersession without repeating the exact path pattern.

audit-doc-citations.py --strict: 0 HIGH across tasks/lawn-plan.md, tasks/lawn-todo.md, both maps.

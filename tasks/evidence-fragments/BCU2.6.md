# BCU2.6 — effect-pipeline plan

Real finding: 10/12 modules already built via seed-to-concrete-todo.md's `ep N` tasks.

```
$ grep -n "\`ep 1\`\|\`ep 2\`\|\`ep 3\`\|\`ep 4\`\|\`ep 5\`\|\`ep 6\`\|\`ep 7\`\|\`ep 8\`\|\`ep 9\`\|\`ep 10\`" tasks/seed-to-concrete-todo.md
(all 10 matches are [x] done tasks)
$ grep -n "affix-power-class\|affix-channel-weights" tasks/seed-to-concrete-todo.md
(no output -- modules 11-12 never folded in)
```

New: tasks/effect-pipeline-plan.md, tasks/effect-pipeline-todo.md (6 tasks, EPL1.1-EPL2.3, covering
only modules 11-12). Edited: the map's plan line.

audit-doc-citations.py --strict: 0 HIGH across all 3 files. spec-no-plan clean for effect-pipeline.

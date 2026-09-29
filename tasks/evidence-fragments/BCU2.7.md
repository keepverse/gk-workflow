# BCU2.7 — battle-wire-remainder plan

New: `tasks/battle-wire-remainder-plan.md`, `tasks/battle-wire-remainder-todo.md` (15 tasks,
BWR1.1-BWR3.2, 3 waves). Covers the true remainder of `battle-derived-wire` and
`combat-math-dedup` after `paperwork-reconcile` P5 (BCU1.5) closed 11 rows by pointer.

H1 named explicitly for BWR1.1 (W3 reflect) and BWR1.6 (W17 AppliedCombat merge) — both may
move battle goldens; change + re-bless required in the same commit.

No map owns this pair (draws from 2 closed todos + 2 audits) — no map pointer to edit.

```
$ python scripts/audit-doc-citations.py --scope tasks/battle-wire-remainder-plan.md --strict
0 HIGH (3 citations)
$ python scripts/audit-doc-citations.py --scope tasks/battle-wire-remainder-todo.md --strict
0 HIGH (27 citations)
$ python gk-core/scripts/audit-program-pipeline.py | grep -i "battle-wire\|battle-derived-wire\|combat-math-dedup"
(no output)
```

Self-found bug: header's own "closed"/"done" wording (describing source todos as retired)
tripped `todo-header-vs-boxes` on this file's own 16 open boxes. Reworded the header, did not
touch the shared tool — same class as the `map-plan-missing` trap hit twice earlier.

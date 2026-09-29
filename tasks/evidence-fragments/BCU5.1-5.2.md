# BCU5.1, BCU5.2 — world-remainders (world-stage, party-dungeon D4.30)

BCU5.1: world-stage-todo.md/map.md both said "proposed, pending owner review" while the todo's own
Checkpoint C reads "complete" (0 open, 141 done, all 15 modules). Corrected both stale headers.
Loam L44-L50 ownership answered by cross-referencing `backlog-clear` LO0 (merged this session):
delivered under world-stage, except L47-L49 which are delivered-then-retired (Q3 bind-warden
retirement, found during the mega-merge).

BCU5.2: D4.30's own "needs a split" premise from 2026-09-06 was already resolved by its own later
2026-09-07/08 dated notes (quest/layout/supply-ext/event/encounter/room all shipped; pipeline
mechanism built and proven). Corrected the stale opening framing instead of re-splitting already-done
work. The one real remaining blocker is external (F1 threat-audit, same fence as BCU4.6).

```
$ python scripts/audit-doc-citations.py --scope tasks/world-stage-todo.md --strict
82 HIGH, all pre-existing (my hunk is lines 1-10; lowest HIGH line is 84)
$ python scripts/audit-doc-citations.py --scope docs/architecture/world-stage-map.md --strict
0 HIGH
$ python scripts/audit-doc-citations.py --scope tasks/party-dungeon-todo.md --strict
8 HIGH, all pre-existing context lines (no +/- diff marker)
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH
```

# BCU3.1-3.4, BCU3.6-3.7 — aura-close-out batch

Discovered while starting BCU3.1: the concurrent `backlog-clear-20260920` session already built
BP1-BP3 (commits `c9facf71`, `67fddada`) and AU2 (`3623153d`), all merged into this branch at
`0b33bbf9`. AU1 (BCU3.2) collided with my own independent fix in the merge; theirs won (more
complete). No re-build needed for BCU3.1/3.2/3.3/3.4/3.6 — ticked by pointer.

BCU3.5 (BP4 live proof) stays open — genuinely owner-run, needs a deploy and live board.

BCU3.7 (SR-14) is real new work: T13/AU2 do not close it (`AuraContentRow` has no rung/share;
`AuraMagnitude.Compute` needs a caller). Added `aura-skill` T23 as the named owner, re-pointed
`battle-derived-wire-todo.md` Tasks 4/5 and `battle-wire-remainder-plan.md` from stale T13 to T23.

```
$ python scripts/audit-doc-citations.py --scope tasks/aura-skill-todo.md --strict
6 HIGH, all pre-existing (diff hunk @@ -2035,6 +2035,24 -- none of the 6 HIGH lines fall in it)
$ python scripts/audit-doc-citations.py --scope tasks/battle-derived-wire-todo.md --strict
1 HIGH (line 516), pre-existing -- my hunks at 139-148/165-173 don't touch it
$ python scripts/audit-doc-citations.py --scope tasks/battle-wire-remainder-plan.md --strict
0 HIGH
```

# BCU6.1 — item modules 24/25 plan

Real finding: item-todo.md's own Phase 7 (P7.3-P7.7 + Checkpoints 7B/7C) already fully plans both
modules 24 (equipment-activation) and 25 (set-requirement-reconciliation), against their own real
specs (spec-equipment-activation.md, spec-set-requirement-reconciliation.md). The paperwork-reconcile
P7 note routing readers to BCU6.1 to "plan" them was itself stale, pointing past the very section
that already answers it.

Corrected the misleading cross-reference in place rather than writing a duplicate plan.

```
$ python scripts/audit-doc-citations.py --scope tasks/item-todo.md --strict
16 HIGH, none in my edit range (9833-9844); confirmed via line-number filter
```

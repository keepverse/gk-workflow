# BCU1.3 — paperwork-reconcile P3 (status lines)

7 files fixed: aura-skill-map.md, drop-tables-map.md, world-map-program.md, world-map-todo.md,
docs/architecture/actor-sheet/spec-{derived-stats,gear,locked-preview,progression}-tab.md (4).

`audit-doc-citations.py --scope <file> --strict`: actor-sheet dir 0 HIGH; aura-skill-map.md 0 HIGH;
drop-tables-map.md 0 HIGH; world-map-program.md 0 HIGH; world-map-todo.md 4 pre-existing HIGH
(lines 186/330/364, `git diff` confirms my hunk is lines 1-7 only — not introduced).

Deferred: `spec-aura-content.md:303` — fenced by `cmdc/lane-d` at batch time; on the todo's deferred
list, re-checked after the mega-merge merge that follows this commit.

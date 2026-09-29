# BCU1.4 — paperwork-reconcile P4 (backlog-clear-todo.md)

3 files: backlog-clear-todo.md (10 sections fixed), aura-skill-todo.md (3 misattribution lines),
commander-surface-map.md (1 naming-drift line).

`audit-doc-citations.py --scope <file> --strict`:
- backlog-clear-todo.md: 2 pre-existing HIGH (lines 318, 405); `git diff` hunk ranges (92-99, 214-238,
  344-359, 372-402, 417-456, ...) do not cover either line.
- aura-skill-todo.md: 6 pre-existing HIGH (88, 98, 252, 521, 1362, 1406); hunk ranges (1584-1593,
  1959-1967, 2018-2025) do not cover any.
- commander-surface-map.md: 0 HIGH.

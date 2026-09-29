# BCU1.2 — paperwork-reconcile P2

3 files: story-scene-todo.md, achievement-title-todo.md, commander-surface-todo.md.

story-scene F1 stale-fence check:
```
$ grep -A2 '"session": "verification-boundaries-20260913-6f31"' tasks/sessions/verification-boundaries-20260913-6f31.json
... "status": "merged" ...
```

`audit-doc-citations.py --scope <file> --strict`: story-scene-todo.md carries 5 pre-existing HIGH
findings (lines 964/985/1379/1381/1475); `git diff` hunks are at 5-13/1322/1341 only — not introduced.
achievement-title-todo.md and commander-surface-todo.md: 0 HIGH.

# BCU7.6 — story-scene F3/F6/F7/F8 + T27b

F7 closed for real: stale fence claim, no session held menu-refactor-queue.md. Added the real
story-scene row (7 pieces + storySceneTokens.ts). Also fixed the same file's separately-stale
"P2+ Not started" row.

F3/F6/F8 stay open (genuine decisions or real unbuilt work, not defects).

T27b re-confirmed still blocked: no WebMessageReceived/postMessage anywhere, unchanged since
2026-09-16.

Corrected story-scene-todo.md's own stale summary counts (5 open -> 3 open follow-ups).

```
$ python scripts/audit-doc-citations.py --scope tasks/story-scene-todo.md --strict
7 pre-existing HIGH, 0 introduced (diff-hunk range confirmed)
$ python scripts/audit-doc-citations.py --scope docs/architecture/gui-lego/menu-refactor-queue.md --strict
0 HIGH
```

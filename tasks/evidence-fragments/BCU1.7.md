# BCU1.7 — paperwork-reconcile P7 (misc absorbed/obsolete)

10 files: actor-hub-enforcement-todo.md, derived-cook-todo.md, verification-boundaries-todo.md,
action-distribution-gaps-todo.md, item-todo.md, empire-development-{plan,todo}.md, loam-todo.md,
passive-tree-repair-todo.md, gui-lego-todo.md.

Live re-verifications:
```
$ git merge-base --is-ancestor bbdd8f94 HEAD; echo $?
0
$ git merge-base --is-ancestor 69ba6a7b3 HEAD; echo $?
0
$ ls src/FusionRpg.Core/Battle/BattleStatComposer.cs
No such file or directory
```

`audit-doc-citations.py --strict` per file: item-todo.md (16 pre-existing HIGH), loam-todo.md (16),
passive-tree-repair-todo.md (2) all confirmed via `git diff` hunk ranges to be outside every edited
region; the rest 0 HIGH outright.

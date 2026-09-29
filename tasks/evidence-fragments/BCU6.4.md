# BCU6.4 — item internal residuals scheduled

Added item-todo.md Phase 8 (P8.1-P8.5 + Checkpoint 8): forge mint, reroll/transfer, socket-imbue
recipe, SetDisclosure multi-set, recipe listing route. Each already named with a reason somewhere
in the file (never silently skipped) — now given a real task id, acceptance, files.

P8.1 reuses BCU6.2's own live finding (boot-wiring gap, Program.cs:712-723) directly, no
re-derivation.

```
$ python scripts/audit-doc-citations.py --scope tasks/item-todo.md --strict
16 pre-existing HIGH, 0 introduced
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH
```

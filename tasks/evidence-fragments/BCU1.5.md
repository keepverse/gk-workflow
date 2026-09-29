# BCU1.5 — paperwork-reconcile P5 (absorbed audits)

6 files: battle-derived-wire-{todo,plan}.md, combat-math-dedup-{todo,plan}.md, both
docs/research/*-audit-2026-09-16.md.

`audit-doc-citations.py --scope <file> --strict`: 0 HIGH in all 6 (battle-derived-wire-todo.md and
combat-math-dedup-todo.md carry pre-existing LOW "file does not exist"/"ambiguous basename" findings,
0 HIGH; `git diff` hunk ranges confirmed away from the one pre-existing HIGH each carried before this
batch where applicable).

Matched by content per the batch's own rule (never by D/W-number): solid-remediation's internal D7/D8/D9
labels are unrelated numbering coincidences with combat-math-dedup's D7/D8/D9 — flagged inline at
Tasks 5/7/8 so a future reader does not conflate them.

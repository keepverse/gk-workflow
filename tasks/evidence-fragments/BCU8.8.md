# BCU8.8 — closed as erratum (orchestrator ruling 2026-09-20)

**Ruling: the stale-premise finding IS the accepted deliverable.** The row closes as *closed-as-erratum*,
not blocked: P11.1's replacement is filed as **P11.1r** in `tasks/passive-tree-repair-todo.md`, P11.0 is
routed to the `decisions.md` owner, and the H5 finding is routed to `item-seedgen`
(`tasks/item-seedgen-todo.md`). The earlier "attempted, not closed" read is kept below as the analysis
the ruling was made on.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Erratum text on the row, closed | `git diff tasks/backlog-clean-up-todo.md` | BCU8.8 `[x]` with the erratum and every routed owner named | `tasks/backlog-clean-up-todo.md` |
| Corrected row filed | `grep -c "P11.1r" tasks/passive-tree-repair-todo.md` | 3 (ruling pointer, heading, the corrected task) | `tasks/passive-tree-repair-todo.md` |
| H5 routed to its owner | `rg -n "H5-wire" tasks/item-seedgen-todo.md` | 1 — with the exact file:line and the separately-unsatisfiable clause named | `tasks/item-seedgen-todo.md` |
| Ledger lifecycle | `python gk-core/scripts/anchor-ledger.py tasks/backlog-clean-up-ledger.jsonl check` | `LEDGER OK` — BCU8.8 `started` → `done` | — |

## Analysis the ruling was made on

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| P11.1's premise checked against code | `sed -n '8,13p' gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs` | **stale** — *"No new subsystem, no new order band… a PRODUCER composed into the existing fan-in, never a fourth registration"*; the real gap is `TreeAtomSource.cs:68`'s `if (atom.KindId != "stat.derived") continue;` | `TreeAtomSource.cs` |
| P11.0's target file is fenced | `python -c "import json;print([p for p in json.load(open('tasks/sessions/keepverse-split.json'))['paths'] if 'decisions' in p])"` | `['docs/architecture/decisions.md']`, and that record is `status: active` → not this lane's to edit | `tasks/sessions/keepverse-split.json` |
| H5's fix is outside this lane's paths | `rg -n "tree_seed_roots" gk-forge/tools/seedsmith/seedsmith/metrics/passive_tree.py` | `:156` — the wiring is `gk-forge/tools/seedsmith/**`; the row's "non-zero `visitedFileCount`" half is separately unsatisfiable against today's corpus | `passive_tree.py`; `tasks/passive-tree-todo.md:3369-3383` |
| Status-atom executor already has the right owners | `rg -n "StatusAtoms" gk-core/src/FusionRpg.Core --glob '!**/obj/**' -l` | bound at bake (`NodeRecord.cs`, `BoundNode.cs`); no executor — MC-2/P6.1 already filed against mechanism-wiring | `tasks/passive-tree-repair-todo.md:482,498` |
| Owning-program row opened for the erratum | `git diff tasks/passive-tree-repair-todo.md` | G13 row corrected (gate premise false) + a "BCU8.8" section naming each item's owner | same file |
| Doc citations clean in the files touched | `python scripts/audit-doc-citations.py --strict --scope tasks/passive-tree-repair-todo.md` | 0 HIGH (two pre-existing D3/D1 citations fixed while there: a bare `Program.cs` and a gone-file line) | — |

No commit for a fix, because there is no fix this lane may land. The erratum request is in the ledger
(`task BCU8.8 blocked`) and on the todo row.

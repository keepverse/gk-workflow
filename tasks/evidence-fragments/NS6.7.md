# NS6.7 — Ask: the `notices` row in the GUI Lego menu-refactor queue

| Criterion | Command | Result |
|---|---|---|
| the gui-lego program (resolver: the owner) accepts a queue row, or the owner adds it. Default if unanswered when NS6.8 starts: the row is added with the notify-centre spec as its brief | edited `docs/architecture/gui-lego/menu-refactor-queue.md` | Unanswered as NS6.8 is about to start (same session) — applied the stated default: added `P4 · Notices` row, brief = `notify-centre-ideal.md` / `spec-notify-centre.md`, pieces = `tool-search`/`chip`/`channel-row`'s Row rung |
| `Select-String -Path docs/architecture/gui-lego/menu-refactor-queue.md -Pattern "notices"` | `grep -n "notices" docs/architecture/gui-lego/menu-refactor-queue.md` | matches the new row |

`P4`'s own Notes cell dropped "Chronicle" from its shared-stream list (now carved into its own row,
matching the precedent P1b already set for Shield-under-Condition) and names the removal explicitly
so the two rows never drift apart. `audit-doc-citations.py --strict` reports 0 findings for this file.

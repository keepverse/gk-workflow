# Anchor: backlog-clean-up

Map: `docs/architecture/backlog-clean-up-map.md`
Plan: `tasks/backlog-clean-up-plan.md` · Todo: `tasks/backlog-clean-up-todo.md`
Specs: `docs/architecture/backlog-clean-up/**` — the active module per the todo row
Session: `backlog-clean-up-20260920` (direct, branch `features/mega-merge`) · Paths: `tasks/**`, `docs/architecture/**`, `docs/research/**`, `scripts/**`, `tools/**`, `tests/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 6 unchecked `- [ ]` lines (measured 2026-09-21). The bar for this program is 0
Queue (todo order, hard edges first): BCU2.10, BCU2.11, BCU2.12, BCU2.13, BCU8.4
Next: BCU2.10
Peers:
| `seed-corpus` | `tasks/seed-corpus-anchor.md` | the runbooks it executes (BCU2.10–2.13) | the seedsmith generators |
| every program | per its own map | the stale-premise audit + row routing | each program's open rows |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session backlog-clean-up-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/backlog-clean-up-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/backlog-clean-up-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

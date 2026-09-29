# Anchor: test-verification-boundary

Map: `docs/architecture/test-verification-boundary-map.md`
Plan: `tasks/test-verification-boundary-plan.md` · Todo: `tasks/test-verification-boundary-todo.md`
Specs: `docs/architecture/test-verification-boundary/**` — the active module per the todo row
Session: `test-verification-boundary-20260920` (direct, branch `features/mega-merge`) · Paths: `scripts/**`, `.github/workflows/**`, `tests/**`, `gk-core/src/FusionRpg.Core/**`, `gk-core/tools/TestSplitAnalyzer/**`, `docs/architecture/test-verification-boundary/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 31 unchecked `- [ ]` lines (re-measured 2026-09-21; 19 at anchor creation, 23 after TVB-F1..F4, +4 more from TVB-F5..F8). The bar is 0
Queue (todo order, hard edges first): TVB4.7, TVB5.7, TVB5.8, TVB5.9, TVB6.1, TVB6.2, TVB6.3, TVB6.4, TVB6.5
Next: TVB4.7
Peers:
| every program | per its own map | the verification registry + the path-owned test mapping | each program's changed paths |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session test-verification-boundary-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/test-verification-boundary-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/test-verification-boundary-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

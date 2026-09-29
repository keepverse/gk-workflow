# Anchor: empire-progression

Map: `docs/architecture/empire-progression-map.md`
Plan: `tasks/empire-progression-plan.md` · Todo: `tasks/empire-progression-todo.md`
Specs: `docs/architecture/empire-progression/**` — the active module per the todo row
Session: `empire-progression-20260920` (direct, branch `features/mega-merge`) · Paths: `gk-core/src/FusionRpg.Core/Stats/Aptitudes/**`, `gk-core/src/FusionRpg.Core/Commanders/**`, `gk-core/src/FusionRpg.Server/**`, `src/FusionRpg.Data/Sqlite/RpgStore.Empire*.cs`, `gk-core/src/FusionRpg.Contracts/**`, `gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tests/FusionRpg.Server.Tests/**`, `gk-core/tests/FusionRpg.Data.Tests/**`, `gk-web/web/fusion-rpg-web/**`, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `gk-data/packs/fusion/data/generated/creatures/**`, `docs/architecture/empire-progression/**`, `docs/architecture/aptitude-sheet/**`, `docs/architecture/power/ssot-power-scale.md`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 35 unchecked `- [ ]` lines (measured 2026-09-21; was 62 at anchor creation). The bar is 0
Queue (todo order, hard edges first): EP1.20, EP1.21, EP2.1, EP2.2, EP2.3, EP2.4, EP2.5, EP2.6, EP2.7, EP2.8, EP2.9, EP2.10, EP2.11, EP2.12, EP2.13, EP2.14, EP3.1, EP3.2, EP3.3, EP3.4, EP3.5, EP3.6, EP3.7, EP3.8 … (+25 more, the todo's own row order)
Next: EP1.20
Peers:
| `species-progression` | its own | empire level fed by species levels (decisions row "Empire level (2026-09-18)") | the per-species lean rows |
| `aptitude-sheet` | its own | the respec price function + auto-assign rule list | the aptitude piece vocabulary |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session empire-progression-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/empire-progression-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/empire-progression-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

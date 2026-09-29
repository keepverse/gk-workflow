# Anchor: strain-splice-host

Map: `docs/architecture/strain-splice-host-map.md`
Plan: `tasks/strain-splice-host-plan.md` · Todo: `tasks/strain-splice-host-todo.md`
Specs: `docs/architecture/strain-splice-host/**` — the active module per the todo row
Session: `strain-splice-host-20260920` (direct, branch `features/mega-merge`) · Paths: `gk-core/src/FusionRpg.Core/Items/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/src/FusionRpg.Contracts/**`, `gk-forge/tools/seedsmith/**`, `gk-forge/tools/ItemSeedValidator/**`, `gk-data/packs/fusion/data/seed/items/**`, `gk-core/data/tuning/**`, `gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tests/FusionRpg.Data.Tests/**`, `gk-core/tests/FusionRpg.Server.Tests/**`, `docs/architecture/strain-splice-host/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 55 unchecked `- [ ]` lines (re-measured 2026-09-21; 71 at anchor creation, 55 at the round-3 reading — ssh27 keeps adding rows as it works the program). The bar is 0
Queue (todo order, hard edges first): SSH2.7, SSH3.1, SSH3.2, SSH3.3, SSH4.1, SSH4.2, SSH4.3, SSH4.4, SSH4.5, SSH4.6, SSH4.7, SSH4.8, SSH4.9, SSH5.1, SSH5.2, SSH5.3, SSH5.4, SSH5.5, SSH5.6, SSH5.7, SSH5.8, SSH5.9, SSH5.10, SSH5.11 … (+24 more, the todo's own row order)
Next: SSH2.7
Peers:
| `species-gear-chain` | its own | sockets, combinations, the helm host | the material + socket vocabulary |
| `seed-corpus` | `tasks/seed-corpus-anchor.md` | the combination grant fix in seedsmith | the generated atom catalogue |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session strain-splice-host-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/strain-splice-host-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/strain-splice-host-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

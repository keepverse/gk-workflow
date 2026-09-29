# Anchor: combat-ai

Map: `docs/architecture/combat-ai-map.md`
Plan: `tasks/combat-ai-plan.md` · Todo: `tasks/combat-ai-todo.md`
Specs: `docs/architecture/combat-ai/**` — the active module per the todo row
Session: `combat-ai-20260920` (direct, branch `features/mega-merge`) · Paths: `gk-core/src/FusionRpg.Core/Actions/**`, `gk-core/src/FusionRpg.Core/Battle/**`, `gk-core/src/FusionRpg.Core/Effects/**`, `gk-fusion/src/FusionRpg.Injector/**`, `gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tests/FusionRpg.Guard.Tests/**`, `gk-core/data/tuning/**`, `docs/architecture/combat-ai/**`, `docs/research/combat-ai/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 38 unchecked `- [ ]` lines (measured 2026-09-21; was 43 at anchor creation, +1 from the routed CAI-guard-1). The bar is 0
Queue (todo order, hard edges first): CAI1.12, CAI1.14, CAI1.15, CAI2.1, CAI2.2, CAI2.3, CAI2.4, CAI2.5, CAI3.1, CAI3.2, CAI3.3, CAI3.4, CAI3.5, CAI3.6, CAI4.1, CAI4.2, CAI4.3, CAI4.4, CAI4.5, CAI4.6, CAI4.7, CAI4.8, CAI4.9, CAI5.1 … (+2 more, the todo's own row order)
Next: CAI1.12
Peers:
| `effect-atom` | its own | the per-place executor allowlist (`IDeclaresExecution`) | the atom kind + trigger vocabulary |
| `battle-wire-remainder` | its own | every AI decision read through `IBattleView` | the battle hub compose |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session combat-ai-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/combat-ai-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/combat-ai-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

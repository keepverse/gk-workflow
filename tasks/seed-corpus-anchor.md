# Anchor: seed-corpus

Map: — this program has no map/plan of its own; the runbooks below are the source
Plan: — the runbooks are the plan · Todo: `tasks/item-seedgen-todo.md` (1 open), `tasks/passive-tree-todo.md` (33 open), `tasks/action-distribution-gaps-todo.md` (13 open), `tasks/seedsmith-generated-seed-repair-todo.md` (3 open)
Specs: the runbooks
Session: `seed-corpus-20260920` (worktree lane `seed-corpus-1`, branch `cmdc/seed-corpus-1`, brief
  `.claude/cmdc-agents/briefs/seed-corpus-1.md`; not yet spawned — next free slot) · Paths: `gk-forge/tools/seedsmith/**`, `gk-forge/tools/ItemSeedValidator/**`, `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, `gk-core/data/tuning/**`, `tests/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 52 unchecked `- [ ]` lines across the four runbooks — item-seedgen 4, passive-tree 33, action-distribution-gaps 13, seedsmith-generated-seed-repair 2 (re-measured 2026-09-21 after the item-seed-gen merge routed the 15 unregistered seedsmith reds into one row). The bar is 0
Queue (todo order, hard edges first): H5, Verification, The, This, T3.2, T3.3, T4.5, T4.6, T4.7, T4.11, T4.12
Next: H5
Peers:
| `item-seedgen` | `tasks/item-seedgen-todo.md` | seedsmith item/atom generation | the item corpus tree |
| `passive-tree-repair` | `tasks/passive-tree-todo.md` | the tree corpus | the tree generator |
| `action-distribution-gaps` | `tasks/action-distribution-gaps-todo.md` | the action corpus rounds | the action pipeline |
| `species-gear-chain` | `tasks/species-gear-chain-anchor.md` | the drop/set tables it consumes | the generated species corpus |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session seed-corpus-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/seed-corpus-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.

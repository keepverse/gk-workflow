# The description backfill targeted AUTHORED content — fixed, and the `--force` path pinned

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the defect, measured | `python -c "from ...generate_action_descriptions import plan; print(plan(...))"` | before: `['act.attack', 'action.family.academic.004']` — the plan named the row of `gk-data/packs/fusion/data/seed/actions/authored-basics.json`, a file whose own `_meta.authored` says "A generator must never write here, and a regeneration run must never overwrite it" |
| the consequence, read from `backfill` | `generate_action_descriptions.py:128-155` | the write loop takes `file_path = actions_root / rel_path` from the LOADED corpus and `write_text`s the stamped row back — so a real run would have replaced the authored prose with a generated description and added a `_provenance` block, destroying the marker that distinguishes authored content from generator output |
| the marker | read | the FILE's `_meta.authored`, not the row's missing `_provenance`: the never-backfilled GENERATED row `action.family.academic.004` lacks `_provenance` too, so provenance-presence cannot be the test |
| the fix | `is_authored` + `plan()` filter | `plan()` now returns `['action.family.academic.004']` — the real gap is still planned, the authored row never is |
| `--force`, the most dangerous path | `plan(force=True)` | **180 targets, `act.attack` ABSENT** (181 entries − 1 authored). `--force` bypasses the ledger, so `is_authored` is the only thing standing between it and the authored file — now pinned by the test |
| the guard | `python -m pytest tests/test_actions_description_completeness.py -q -k backfill_plan_never_targets` | **1 passed** — asserted STRUCTURALLY: every file under the live actions tree that declares `_meta.authored` is enumerated from the tree (not named), and no plan in either mode names any of their rows; the real gap is still planned. A new authored file is covered the moment it lands |
| the contract error in the suite | `--tb=line` | `test_every_real_committed_action_carries_provenance` required a `description_backfill` `_provenance` on EVERY `action-seed` row, the authored one included — i.e. it demanded the hand-edit the authored-content rule forbids, and the backfill plan was the way to satisfy it. It now asserts the split contract (generated rows: `description` + provenance; authored rows: a description and **no** provenance), keeps its name so its `knownRed` entry stays valid, and still fails — on SGC5-F4's real gap |
| the file, after | `python -m pytest tests/test_actions_description_completeness.py -q` | **5 failed, 7 passed** — the same 5 registered `knownRed` nodeids, so the registry needs no change; the split moved from 3/3 (one test naming both ids) to **4 naming SGC5-F4, 1 naming SGC5-F2** |
| the program-wide total is unchanged | the three whole-suite chunks | still **8 failed / 4617 passed / 4 skipped** — only the attribution moved, 3/4/1 across the authored row, SGC5-F4 and SGC5-F3 ⚠ *the PASSED count later moved to **4618** when this lane added a case to `test_actions_description_completeness.py`, which sits inside the `test_[a-c]` sub-chunk; the FAILED count never moved — 8, from three causes* |

**Scope note — the sweep for the same hazard elsewhere was run, and it is NEGATIVE.** Every seedsmith
module that loads a shipped corpus and writes back into a path derived from what it read was checked:
the `group_ids_by_path`/`rel_path` writers (`actions/generate_action_descriptions.py` — the case above,
now guarded; `creatures/run/runner.py` and `creatures/anchor/emit.py`, both writing generator-owned
anchor/family files), and the item repairs (`items/basetypegen/reslate.py`, `resocket.py`,
`successor_edges.py`, `setgen`, `affixfamgen`, `recipegen`, ... all writing generated partition trees).
The one other repair that rewrites files in place is `items/meta_registry_repair.py`
(`_atomic_write(bump.path, ...)`), which does reach hand-authored item files — but it is a documented,
evidence-gated `_meta.registryVersions` stamp bump whose own docstring requires the caller to have proven
safety per (registry, old, new) triple, and whose surgical-token-edit design exists precisely so no other
byte moves. No second instance of "a generator's plan silently overwrites authored content" was found.

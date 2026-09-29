# H5-wire — a real call site for `tree_seed_roots` / `HiddenFileCountMetric` (closed 2026-09-21)

Re-measured at this lane's base `00baecb5`: the wiring the row asks for **already exists at base** (a
prior lane landed it and never ticked the row), so this task verifies it for real and closes the rows.
The unsatisfiable second clause is routed, not forced green.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Real call site exists at base | `git show HEAD:gk-forge/tools/seedsmith/seedsmith/report/cli.py \| grep -n "registry.register(HiddenFileCountMetric())\|tree_seed_roots="` | `323:    registry.register(HiddenFileCountMetric())` and `345:        tree_seed_roots=(seed_root / "passive-tree",))` | `gk-forge/tools/seedsmith/seedsmith/report/cli.py` |
| Metric runs for real (not its own test) | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree 2>&1 \| grep HiddenFileCount` | `[NOTE] PassiveTree/HiddenFileCount — (corpus): walked 0 \`_\`-prefixed file(s) across 1 seed root(s)` | real run over `gk-data/packs/fusion/data/seed/passive-tree` |
| Call site covered by a test entering the real command | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_cli.py -q -k "hidden_file_count"` | `1 passed, 18 deselected in 9.06s` | `test_nodegen_cli.py:88` |
| Canary proof unchanged | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees/test_passive_tree_metrics.py -q -k HiddenFileCountMetric` | `5 passed, 77 deselected in 0.17s` | `test_passive_tree_metrics.py:911` |
| Non-zero clause unsatisfiable against the passive-tree root | `find gk-data/packs/fusion/data/seed/passive-tree -name "_*.json" \| wc -l` | `0` | `gk-data/packs/fusion/data/seed/passive-tree` |
| Why widening the root is not the fix | `find gk-data/packs/fusion/data/seed -name "_*.json" \| sort` | 12 files; the 4 outside `_index.json` are `actions/_manifest.json`, `creatures/_dump/_manifest.json`, `creatures/_dump/_preflight.json`, `structures/_plan.json` — all structured manifests/plans, so a wider walk adds 4 false-positive GAPs | `gk-data/packs/fusion/data/seed` |
| Passive-tree H5 call-site bullet closed; unsatisfiable clause routed | `grep -c "PTR-EF1" tasks/passive-tree-todo.md` | `3` (bullet note, addendum, erratum row) | `tasks/passive-tree-todo.md` |
| Seedsmith full-suite baseline (no code changed by this task) | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q` | `20 failed, 4260 passed, 3 skipped, 5003 subtests passed in 702.66s (0:11:42)` | pre-existing at base; unchanged here |
| Pre-existing D3 citation re-anchored while holding the file (ride-along) | `python scripts/audit-doc-citations.py --scope tasks/item-seedgen-todo.md --strict` | `D3 ambiguous basename 0 (0 HIGH)` — was 1 HIGH at `:572`; `--strict` exit `0` | `tasks/item-seedgen-todo.md` |
| Pre-existing citation HIGHs swept in the other changed todo (ride-along) | `python scripts/audit-doc-citations.py --scope tasks/passive-tree-todo.md --strict` | `926 citations, D1 14 (0 HIGH), D3 0 (0 HIGH)` — was 13 HIGH (7 D1 + 6 D3); `--strict` exit `0` | `tasks/passive-tree-todo.md` |
| Path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/item-seedgen-todo.md','tasks/passive-tree-todo.md','tasks/evidence-fragments/H5-wire.md','tasks/seed-corpus-ledger.jsonl','tasks/sessions/seed-corpus-20260920.json') -Session seed-corpus-20260920"` | exit `1`; doc-citations all `0 HIGH`; `[session-boundary] clean for 'seed-corpus-20260920'`; `test: guard` `Failed: 1, Passed: 579, Total: 580` | the one failure is the pre-existing, other-owned `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`tasks/combat-ai-todo.md:1089`, awaiting the `tvb58` re-pin); no code in this task's diff can reach a `BattleEffects.cs` hash |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- The `non-zero visitedFileCount` acceptance clause is **not met and cannot be** against today's
  passive-tree seed corpus. Routed as **PTR-EF1** (`tasks/passive-tree-todo.md`) for the passive-tree
  program to reword; `docs/architecture/passive-tree/spec-tree-review.md` §7 is outside this lane's fence.
- The wider `gk-data/packs/fusion/data/seed` root was deliberately **not** adopted: it would report four legitimate
  manifests/plans as GAPs while §7 still names only `_index.json` as a legitimate `_`-file.
- No code change: the call site and its test exist at base; this task verified them for real, ticked
  both rows, and filed the erratum.
- `verify-change.ps1` exits `1` on one **pre-existing, other-owned** Guard failure (named above), not on
  anything this task changed; the `guard: session-boundary` step is clean and doc-citations are `0 HIGH`.
- The Guard failure is **not** re-pinned here: `gk-core/tests/FusionRpg.Guard.Tests/**` is a protected path and the
  re-pin is already owned by `combat-ai` (`tasks/combat-ai-todo.md:1089`) and riding lane `tvb58`.

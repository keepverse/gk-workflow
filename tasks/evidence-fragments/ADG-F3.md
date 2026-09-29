# ADG-F3 — the pipeline dry-run's expected plan hash is now the one a real run computes (resolved 2026-09-21)

Found while unblocking T4.6: `run_pipeline` computed its two foundation stages with
`regenerate(write=not dry_run)`. `type_weights` derives its `leanHash` from the **raw text** of
`_generated/role-lean.json`, so under `--dry-run` it hashed the STALE committed role-lean while the
characteristic-pool hash beside it was fresh. The expected hash was therefore a third value that matched
neither the committed plan nor a real run's — a preflight that could report a hash no run would produce.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The seam exists and computes both stages into one root | `sed -n '/def _foundation_inputs/,/return {"characteristicPool"/p' gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_pipeline.py` | `characteristic_pool.regenerate(actions_root=…, write=True)` then `type_weights.regenerate(actions_root=…, role_lean_path=…/_generated/role-lean.json, write=True)` | `gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_pipeline.py` |
| The dry-run uses a throwaway root, the real run the tracked tree | `grep -n "TemporaryDirectory" -A4 gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_action_pipeline.py` | `with tempfile.TemporaryDirectory() as tmp: foundation = _foundation_inputs(Path(tmp))` / `else: foundation = _foundation_inputs(ACTIONS_ROOT)` | same |
| The stale-role-lean case is pinned | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_action_generation_batches.py -q` | `9 passed in 6.28s` — incl. `test_type_weights_hashes_the_freshly_derived_role_lean_not_a_stale_one` (a planted stale `role-lean.json` is rewritten before type-weights reads it), `test_both_stages_land_under_the_root_they_were_given`, and `test_the_tracked_foundation_files_are_untouched_by_a_computation_into_a_temp_root` | `gk-forge/tools/seedsmith/tests/test_action_generation_batches.py` |
| The run preflight stays green end to end | `PYTHONPATH=gk-forge/tools/seedsmith python gk-forge/tools/seedsmith/action_run_preflight.py` | `preflight GREEN` — `plan freshness committed=188e8625f6e4… fresh=188e8625f6e4…`, `pipeline accepts the plan`, `pipeline dry-run: stops only on absent candidate scratch` | `gk-forge/tools/seedsmith/action_run_preflight.py` |
| The dry-run writes nothing tracked | `git status --porcelain gk-data/packs/fusion/data/seed/actions` after the preflight | *(empty)* | `gk-data/packs/fusion/data/seed/actions/_generated/**` |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- **The pipeline hash is compared, not re-derived end to end here**: the fix makes the dry-run compute the
  same foundation a real run computes; that equality is what `action_run_preflight.py`'s plan-freshness
  step then checks against the committed plan. No real (writing) pipeline run was executed — T4.6 is the
  manager's detached job.
- The **ADG-F2** half is untouched: `generate_distribution_planner` still validates its on-disk role-lean
  by species **ID SET** only, so a catalog-content drift is caught by the pipeline (and by the preflight's
  step 5) rather than at the planner. That row stays open.

# SSH5.11 — `basetypegen/resocket.py`, the deterministic re-stamp verb (DRY RUN only)

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/resocket.py` (new) — `plan_resocket` /
  `apply_resocket` / `main`, modelled on `reslate.py`: for every enabled base-type row it recomputes
  `socketMax` through the ONE resolver `tuning.resolve_socket_max(role, band, seq_index)` under the
  current sockets revision, where `seq_index` is the row's own 0-based position in its partition file
  (the corpus stores no `seq`; the emission order is that position + 1). Only `socketMax` moves; on
  `--write` one `_meta.amendments` record (`batch: resocket`) documents the batch. No model call.
- `gk-forge/tools/seedsmith/tests/test_base_types_gen.py` — `test_resocket_is_deterministic_and_changes_only_socket_max`.

## Evidence

| Criterion | Command | Result |
|---|---|---|
| dry-run on the real corpus | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith.adapters.items.basetypegen.resocket --dry-run` | exit 0; `total 1158, unchanged 321, resocketed 837` |
| determinism + only `socketMax` moves | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py -q` | 69 passed |
| the named test | same run | `test_resocket_is_deterministic_and_changes_only_socket_max` — identical plan across two runs; every non-`socketMax` field byte-equal; `_meta.amendments[-1].batch == "resocket"`; a re-plan after the write changes 0 rows |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

## NOT proved / still open

- `--write` was NOT run — it is SSH5.12, the owner-run ask-first corpus rewrite. The verb's write path
  and its amendment are implemented and covered by the fixture test, but the real corpus is untouched.
- The re-stamp's consequence (the corpus host set widening to the tuning set, helm included) is
  SSH5.12's `the_corpus_host_set_equals_the_tuning_host_set` tightening, not this row's.
- `verify-change` not run: it still aborts on other sessions' session-boundary drift.

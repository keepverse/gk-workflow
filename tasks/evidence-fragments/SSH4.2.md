# SSH4.2 — R12: delete the Python per-actor cap

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` — `ComboTuning.max_combos_per_actor`
  and its `_require(..., "maxCombosPerActor")` read removed; the module docstring's "per-actor
  backstop" and `geometric_combo_ceiling`'s backstop prose reworded (the function stays — it is a
  reading, now compared to nothing). `SOCKETS_OWNED_KEYS` keeps the key name.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/__init__.py` — the "no second copy of module
  16's socket numbers" bullet no longer names the retired key.
- `gk-forge/tools/seedsmith/seedsmith/report/cli.py` — the run summary no longer carries `maxCombosPerActor`.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — the backstop test deleted;
  `test_the_combogen_tuning_loads_without_module_16s_retired_cap` added (v1 with the key and a fixture
  without it both load).
- `docs/architecture/strain-splice-host/spec-combo-bind.md` — the deletion table's rows marked done
  and re-anchored (deleted symbols say so on their own line).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| field, `_require` and summary key removed; prose reworded | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | 90 passed, 0 failed |
| backstop test deleted; tuning loads without the key | same run | `test_the_combogen_tuning_loads_without_module_16s_retired_cap` |
| no `max_combos_per_actor` reader survives | `grep -rn "max_combos_per_actor" gk-forge/tools/seedsmith/` | no matches (outside `__pycache__`) |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

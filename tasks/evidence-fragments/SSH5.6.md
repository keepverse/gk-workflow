# SSH5.6 — one Python sockets-revision constant; `basetypegen` imports it

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py` — its duplicate
  `SOCKETS_TUNING = REPO_ROOT / "data" / "tuning" / "sockets.v1.json"` is gone; the module imports
  `SOCKETS_PATH as SOCKETS_TUNING` from `combogen/tuning.py`, which owns the one constant.
- `gk-forge/tools/seedsmith/tests/test_combogen.py` — `test_no_other_python_module_names_a_sockets_revision_path_literal`
  scans `gk-forge/tools/seedsmith/seedsmith/**/*.py` for a `sockets.v{n}.json` PATH join (`/ "sockets.vN.json"` /
  `Path("sockets.vN.json")`), allowing only `combogen/tuning.py`; message/docstring mentions are prose.
- `gk-forge/tools/seedsmith/tests/test_base_types_gen.py` — `test_the_sockets_revision_is_the_combogen_modules_one_constant`
  asserts the imported path equals combogen's.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| one constant, imported | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | 159 passed, 0 failed |
| no other Python path literal | same run | scan test green |
| both test files read it | same run | `test_strain_splice_gen.py` uses `tuning_mod.SOCKETS_PATH`; the new base-types test reads `tuning_mod.SOCKETS_TUNING` |

Note: the editor's Python linter reports ~40 pre-existing style findings in
`basetypegen/tuning.py` (quoted forward-ref annotations, `json.loads` without `try/except` on a
file that is deliberately fatal, unused loop vars). None is introduced here; the file is otherwise
untouched and the tests are authoritative.

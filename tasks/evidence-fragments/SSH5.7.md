# SSH5.7 — `publish.py --remove-key container.path:leaf`

## What changed

- `gk-core/tools/tuning/publish.py` — **no code change needed**: `remove_key` and the `--remove-key` flag
  already exist (built by the solid-enforcement lane; `main` catches its `KeyError` and returns 1,
  publishing nothing). This row's job was the named test, and the tool already meets the discipline.
- `gk-core/tools/tuning/test_publish_remove_key.py` — added `test_publish_remove_key_refuses_an_absent_key`
  (helper raises; `main` exits 1; no `v{n+1}` file is written). The existing batch-property and
  unresolvable-path tests are untouched.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| removes an existing key in `v{n+1}` | `python -m pytest gk-core/tools/tuning/test_publish_add_key.py gk-core/tools/tuning/test_publish_remove_key.py -q` | 30 passed, 0 failed |
| `publish_remove_key_refuses_an_absent_key` | same run | helper `KeyError` + `main()` returns 1 + no v2 written |
| refusal discipline matches `--add-key`/`--rename-key` | same run | `KeyError` → `main` prints `refused: …` and returns 1 |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

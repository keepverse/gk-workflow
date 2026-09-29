# ISG3 — `--overwrite <ids>` for `--kind combination` cells

Sub-agent task `item-seed-gen`. A generator capability gap SSH2.5 named and had to work around.

## The gap

`authored.plan_overwrite` already accepted an explicit subject-id list, and
`_cmd_items_combination_write` already passed one through — but only ever the list
`--retry-blocked` had just computed. There was no flag to name a cell that is `persisted` but wrong.
SSH2.5 hit exactly this (`tasks/evidence-fragments/SSH2.5.md`, "Finding on `--limit`"): `--limit N`
does not partition `--retry-blocked` work (a `blocked` subject is re-offered on every call by
design), so "small batches" were impossible and it had to run each shape's FULL walk instead.

## What changed

- `gk-forge/tools/seedsmith/seedsmith/report/cli.py`
  - new `_combination_overwrite_subjects(plan, token)`: comma-separated entry ids
    (`combo.splice-x-y`, the validator's spelling) or subject ids (`combination-splice-x-y`, the
    ledger's), or the literal `all`; returns the matching subjects in grid order, or `None` when a
    name matches nothing so a typo refuses (exit 2) instead of silently re-running nothing.
  - `_cmd_items_combination` narrows to those subjects; `--overwrite` together with
    `--retry-blocked` refuses (they select different sets — "one, not both").
  - `--overwrite`'s help text extended to name the combination spelling.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` — 3 new CLI tests.

No seed JSON changed in this commit.

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One named cell selects exactly that cell (entry id or subject id) | `python -m seedsmith items generate --kind combination --shape splice --dry-run --overwrite combo.splice-composure-bulwark` | `toGenerate 1`, `plannedBeforeLimit 66` | stdout |
| A name matching no cell refuses loudly | same with `--overwrite combo.splice-nope-no-such` | exit 2, `not a grid subject` | stderr |
| `--overwrite` + `--retry-blocked` refuses | same with both | exit 2, `one, not both` | stderr |
| The combination + wiring suites stay green | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_grant_repair.py gk-forge/tools/seedsmith/tests/test_item_gen_wiring.py gk-forge/tools/seedsmith/tests/test_items_generate_passthrough.py -q` | pass — 183 passed, 90 subtests | stdout |

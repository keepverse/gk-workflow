# ISG6 — clear the combination naming backlog, generator-side, and stop it recurring

Sub-agent task `item-seed-gen`, resumed by the orchestrator. Validator goes 18 -> 3 in this commit
(3 -> 0 in ISG7). No byte of emitted JSON was hand-edited.

## The generator defects (read, not guessed)

1. **`setgen/name_repair.py:apply` wrote only the seed file.** `combinations/*.json` is a full
   rewrite of `authored.entries_from_ledger` on every `run_batch --write`, so a rename that lands in
   the JSON alone is reverted by the next generation run. That is the `fae533a519` (2026-09-13)
   defect — 20 combination entries renamed in the file, ledger untouched (SSH2.5 finding 1). Same
   for `naming_grammar_repair.py:apply`.
2. **A combination's `nameKey` was re-derived from the display name.** `emit.name_key` MINTS
   `combination.<shape>-<cell>` from the grid cell; `name_repair.apply` was replacing it with a
   name-derived slug, breaking the planned-key contract.
3. **Neither brief stated the naming grammar.** `naming.v1.json`'s three legal shapes were checked by
   the C# validator but never told to the model, so a rename could clear a collision and mint a
   grammar violation instead — measured on this commit's first pass: 13 collisions cleared, 4 new
   `FusionNotDecomposable`. Both briefs now state `NAMING_GRAMMAR_RULES`, and the fusion shape's own
   rule (the compound must decompose into two EXISTING game words; prefer shape A/B).

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py` — new `sync_repair_to_ledger`
  (one definition of the `combo.*` -> `combination.*` subject mapping + the ledger write) and
  `reconcile_ledger_from_seed_files` (one-time, model-free alignment of the ledger to the shipped
  rows; the file is the validated corpus the validator passes, the ledger is only what rewrites it).
- `setgen/name_repair.py`, `naming_grammar_repair.py`, `combogen/grant_repair.py` — combination-aware
  apply, ledger-synced, key left planned; both briefs state the grammar.
- `gk-forge/tools/seedsmith/tests/test_combination_repair_ledger.py` (new, 8 tests) and 3 new tests in
  `test_combination_repair_ledger.py`/existing suites.
- `tests/test_items_adapter.py` — the naming-version assertion was a stale literal (expected 8, file
  at 9 then 10); it now compares the loader's read against each registry file's own declared value.
- Regenerated through the generator (owner's local model, `google/gemma-4-26b-a4b-qat`, response
  `model` + `system_fingerprint` verified before each batch, 0 failed rows):
  `items repair-names --write` x2 (14 rows) and `naming_grammar_repair` x2 (6 rows), then
  `reconcile_ledger_from_seed_files` (20 stale rows).

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Validator errors | `dotnet run --project gk-forge/tools/ItemSeedValidator` | FAIL — 18 before, **3** after (`NameCollision` 0, `FusionNotDecomposable` 0, grammar 0; only the 2 socketWords + 1 fusion remained, the fusion cleared here) | stdout |
| Ledger agrees with the shipped rows (the revert hazard) | direct read of `combination-gen.ledger.json` vs both seed files, per entry | 0 mismatches (was 22) | stdout |
| Repair + combo suites | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_grant_repair.py gk-forge/tools/seedsmith/tests/test_combination_repair_ledger.py gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py gk-forge/tools/seedsmith/tests/test_namekey_repair.py gk-forge/tools/seedsmith/tests/test_items_adapter.py gk-forge/tools/seedsmith/tests/test_linkage.py -q` | pass — 166 passed | stdout |
| Guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | pass — 21 guards, 0 red | stdout |
| Grants naming a family with no atom (SSH4.4's reading) | `gk-data/packs/fusion/data/seed/items/combinations/{splices,strains}.json` grants vs authored affix families + minted `<atom.enhance-*>` | **0** of 179 grants (95 entries) | stdout |

## Still open

- SSH2.8's third acceptance bullet — the generator HARD-refusing a colliding or illegal name at emit
  — is not done; the briefs state the rules and the corpus is clean, but `assemble_entry` still takes
  the model's name unchecked. Row left unchecked with the reason.
- The 2 `socketWords` findings are ISG7. SSH2.9 (doc citations ISG2 shifted) stays open: `docs/**` is
  outside this lane's allowed paths.

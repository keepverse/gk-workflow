# SSH2.8 — combination naming backlog (closed; the code half landed in SSH5.13-P1)

Three acceptance lines, all satisfied. Lines 1–2 were closed by ISG6; line 3 (the generator refuses a
colliding/illegal name, so a later regen cannot reintroduce the backlog) was cleared by **SSH5.13-P1**,
which validates the candidate before persist in the generation graph — not in `emit.py`. This row
previously asked for a manager erratum because that half looked open; it is not.

| Criterion | Command | Result |
|---|---|---|
| a colliding or illegal name is refused before the write | `grep -n "answer_uses_a_legal_name\|answer_reuses_a_shipped_idea" gk-forge/tools/seedsmith/seedsmith/workflow/graphs/item_combination.py gk-forge/tools/seedsmith/seedsmith/report/cli.py` | `COMBINATION_VALIDATORS` carries both; the production write path wires `taken_keys`/`key_of`/`name_defects` (`report/cli.py:1689`, `:1696`), so `--retry-blocked`/`--write` refuse before persist |
| 0 `NameCollision` / 0 naming-grammar findings over the corpus | `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items` | **PASS — 3978 entries across 1013 files** |
| the four naming defect codes are absent | `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items --findings-json --codes=NameCollision,InventedConnective,NameGrammarViolation,FusionNotDecomposable` | **count 0**, `findings: []` |
| the ledger read agrees with the file after a repair | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_namekey_repair.py gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py gk-forge/tools/seedsmith/tests/test_combination_repair_ledger.py gk-forge/tools/seedsmith/tests/test_items_adapter.py -q` | **44 passed** |
| the emit-time validators are exercised | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **37 passed / 7 subtests** |

## Not proved / open

- `emit.assemble_entry` still accepts a `name` string without validating it. That is by design: the
  refusal belongs in the graph's validate node, which every persisted answer passes through, and a second
  check inside the emitter would be the "validator not wired to a production caller" it replaces.
- `No commit: SSH2.8's deliverable was already in the tree (ISG6 + SSH5.13-P1); this row closes on the
  re-verification above, recorded here and in the todo/ledger.`

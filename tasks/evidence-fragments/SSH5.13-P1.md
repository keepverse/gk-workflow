# SSH5.13-P1 — the combogen authoring graph now checks the naming GRAMMAR, not only collisions

Fixed on the production path: `ItemSeedValidator --check-names` (a new mode beside `--normalize-names`,
running `NamingCheck.CandidateNameDefects` — the validator's OWN regexes, connective rule and pool
decomposition), `name_repair.name_defects()` as its authority-wrapping caller, and
`answer_uses_a_legal_name` in the combination graph, armed by `_cmd_items_combination_write` exactly the
way the shipped-name guard is. `run_batch` carries the callable through to the graph.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| a single-word fusion that does not decompose is refused BY NAME before the write | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **34 passed** (31 + 3 new). `test_a_name_the_naming_grammar_refuses_is_refused_by_the_graph` + `test_the_grammar_guard_stops_a_run_persisting_a_name_it_refuses` (both cells escalate, nothing persists); a declared `blocked` answer is never judged on a name; with no authority wired the check is OFF, never guessed |
| the C# grammar is the authority, never a Python copy | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release -- gk-data/packs/fusion/data/seed/items --check-names` (names on stdin) | `Ironstead` → *a fusion that does not decompose into exactly one pair of known pool words*; `Ashfang` → same; `Ferocity bastion` → *matches none of the three legal patterns*; `Ferocity Bulwark`, `Ember Legion`, `Fang of Ash`, `Bastion of the Hollow Crown`, `Wind-borne Inlay` → clean. The same reading the C# gate produced for the two names the R11 re-run had written (`Ironstead`, `Ironheart`) |
| the tool's own tests + the corpus gate are unaffected | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests`; `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **97 passed / 0**; **PASS — 3960 entries / 1013 files / 2589 warnings** |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-forge/tools/ItemSeedValidator/Checks/NamingCheck.cs','gk-forge/tools/ItemSeedValidator/Program.cs','gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/name_repair.py','gk-forge/tools/seedsmith/seedsmith/workflow/graphs/item_combination.py','gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py','gk-forge/tools/seedsmith/seedsmith/report/cli.py','gk-forge/tools/seedsmith/tests/test_combogen.py') -Session strain-splice-host-20260921"` | exit **1** for the pre-existing reason: `report/cli.py` and `item_combination.py` map to `seedsmith-fallback (module)`, whose check is the WHOLE seedsmith project — **23 failed / 4198 passed / 3 skipped**, the same 23 as before this change and none in combogen/tuning/name_repair/report. Its `test-substrate` guard printed OK; the `itemseedvalidator` boundary it never reached was run directly (97/0 + the corpus PASS above) |

## What it covers, stated (so nothing reads as more)

`CandidateNameDefects` checks the three naming patterns, the engine-only pattern, the apostrophe rule, the
lowercase-connective rule and pool decomposability — the classes this row measured. Pool-plural spelling
and markup stay with the corpus validator: no generator authors them, and they need the whole registry
surface. That boundary is written into the method's own doc comment, not implied.

## Not proved / open

- Re-authoring `combo.strain-ferocity-balance` with the guard armed is **not** done here: that cell is
  `escalated` in the ledger and reported by id (SSH5.13), and R13 makes its next step an owner ruling, not
  a lane retry. The guard is proven against the same names the gate refused.
- The graph check refuses a name, it does not RENAME one: the repair path for a persisted name remains
  `items repair-names` (which now has the same authority for collisions and a keeper named in words).

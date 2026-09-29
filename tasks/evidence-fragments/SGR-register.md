# SGR-register — the seedsmith suite's unregistered reds, individually registered (2026-09-21)

The `seedsmith-generated-seed-repair` row "15 unregistered pre-existing failures" closes on its own
alternate acceptance: *"green or individually registered with a row that names its cause"*. Every
cause below is the test's own printed assertion, re-measured at base `00baecb5`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The row's 15 named tests, re-run | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest <each of the 15 named tests> -q --tb=line` | `14 failed`; `test_themes_v2.py::test_publish_is_idempotent` **passes** — the CRLF cause was fixed by lane `sgc-2` (T51) and is in the base | `tasks/seedsmith-generated-seed-repair-todo.md` |
| A 15th unregistered red the row's list omitted | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | `1 failed, 82 passed` — `ChassisTests::test_the_corpus_host_set_is_a_subset_of_the_tuning_host_set_and_no_row_exceeds_its_ceiling` (`4 != 8`) | same |
| Full-suite reading matches the arithmetic | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q` | `20 failed, 4260 passed, 3 skipped` = 15 unregistered + 5 `knownRed` (`SR-25`) | — |
| Every cause is the printed assertion, not a guess | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest <each test> -q --tb=line \| grep -E "^E "` | 15 per-test printed causes, one row each, in the todo's registration table | `tasks/seedsmith-generated-seed-repair-todo.md` |
| The shared cause of three reds, read to source | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --adapter actions --metric Actions/Loader gk-data/packs/fusion/data/seed/actions` | `1 gap` — `act.attack: field 'atomFamilies' refused — unknown value 'atom.fx-overlay-damage'`; already known and documented at `gk-forge/tools/seedsmith/tests/test_coverage_report.py:888` ("the action program's spec question, not this generator's") | `gk-data/packs/fusion/data/seed/actions/authored-basics.json:25` |
| The five worked-example reds' cause, read to source | `grep -n "REAL_GENERAL_CANDIDATES_PATH" gk-forge/tools/seedsmith/tests/test_general_propose.py` | `:69` → `data/seed/actions/_candidates/general/round-1.json`, **gitignored** (`.gitignore:113`) and never committed → `render_worked_example()` returns `""` | test-isolation defect |
| `ItemSeedValidator` is not the gate | `dotnet run --project gk-forge/tools/ItemSeedValidator --nologo` | `partitions  1129 allocated prefixes`, `errors 0`, exit `0` | — |
| Path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('tasks/seedsmith-generated-seed-repair-todo.md','tasks/evidence-fragments/SGR-register.md','tasks/seed-corpus-ledger.jsonl') -Session seed-corpus-20260920"` | exit `1`; doc-citations `0 HIGH` on both docs; session-boundary clean; `test: guard` `Failed: 1, Passed: 579, Total: 580` | the one failure is the pre-existing, other-owned `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`tasks/combat-ai-todo.md:1089`, riding `tvb58`) |
| Ledger intact | `python gk-core/scripts/anchor-ledger.py tasks/seed-corpus-ledger.jsonl check` | `LEDGER OK` | `tasks/seed-corpus-ledger.jsonl` |

## Not proved
- **No test was made green.** This task registers causes, which the row's own acceptance permits; the
  underlying defects still need their own fixes (the table's Reading column names each).
- `test_usage_stats`'s `acceptedCount == 0` is registered on its printed assertion plus a *probable*
  shared cause with the `act.attack` refusal; the loader path was not traced further.
- The full-suite total was measured twice (H5-wire and ISG7-follow-up) and once showed a transient
  `git`-subprocess flake in `test_audit_doc_citations.py`; the registered 15 are stable across both.

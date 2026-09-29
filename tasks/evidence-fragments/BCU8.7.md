# BCU8.7 — spec the seedsmith naming-grammar pass

Wrote `docs/architecture/item-seedgen/spec-naming-grammar-repair.md` (item-seedgen module 13) and added
it to that map's module table. The module's **code already shipped** (`d401f446`, `750b0dfd`), so the
spec documents the shipped shape instead of inventing one. **The finding is the wiring**: no
`seedsmith items` verb reaches it, and the corpus batches ran through an uncommitted driver.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Spec written, indexed, citations resolvable | `python scripts/audit-doc-citations.py --strict --scope docs/architecture/item-seedgen/spec-naming-grammar-repair.md` | 0 HIGH | the spec; `docs/architecture/item-seedgen-map.md` module table |
| Module code is real and tested | `rg -c "def test" gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py` | 13 | `naming_grammar.py`, `naming_grammar_repair.py`, that test file |
| The wiring gap, read not assumed | `rg -n "naming_grammar_repair" gk-forge/tools/seedsmith/seedsmith/report/cli.py` | **no hits** — the module has no CLI verb; its only importer is its own test | `gk-forge/tools/seedsmith/seedsmith/report/cli.py` |
| The batches ran outside a host | `git show --format=%b -s 750b0dfd` | the message names "the still-uncommitted driver script" | commit `750b0dfd` |
| Owning-program rows opened | `git diff tasks/seedsmith-generated-seed-repair-todo.md` | WIRE 1 (`seedsmith-cli-ux`) + WIRE 2 (`item-seed-regen`) with acceptance | that file |
| Stale `NOT-BUILT` row corrected | `git diff docs/research/backlog-clean-up/lane-B2-seedsmith-content.md` | → `PARTIAL — code built; no production host reaches it` | that file |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('docs/architecture/item-seedgen/spec-naming-grammar-repair.md','docs/architecture/item-seedgen-map.md','tasks/seedsmith-generated-seed-repair-todo.md','docs/research/backlog-clean-up/lane-B2-seedsmith-content.md') -Session bcu8"` | doc-citation step 0 HIGH; guard module 575 passed / 3 failed (the same 3 pre-existing, unrelated — lane D's `FusionRpg.FileMove.Tests/SplitExecutorTests.cs:262-263` plus two `VerificationBoundaryWorkflowTests` 120 s timeouts vs a 3m05s guard script) | — |

Counts are readings, not constants: 1125 findings at `d401f446`, 811 remaining at `750b0dfd`. The
acceptance is the validator reporting 0 for the six codes through the CLI verb, whenever that happens —
never a pinned number, and never a hand-edited row.

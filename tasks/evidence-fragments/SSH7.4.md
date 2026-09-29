# SSH7.4 — `combogen-reemit`: re-emit the corpus from the run ledger, no model call

`authored.reemit_entry` rebuilds ONE ledger entry through the CURRENT emit shape (families expanded from
the row's quantities, grants/name/flavor/shape/aptitudes/archetype/host pins verbatim, no tier written),
`authored.reemit` does it for a whole shape, and `python -m seedsmith items combogen-reemit
--dry-run|--write` drives it and records a `_meta.amendments` batch on a write.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| it re-emits through `entries_from_ledger`; no model call | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combogen-reemit --dry-run` | exit 0, `{"strain": {"entries": 32, "changed": 32}, "splice": {"entries": 66, "changed": 66}}` plus every changed id. Nothing under `data/` changed (`git status` proves the dry run wrote nothing), and no transport is reachable from the path — the entries come from the ledger's own `done` rows |
| `reemit_is_byte_identical_on_a_second_run` | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **111 passed, 11 subtests passed**. Re-emitting the re-emission is equal for both shapes |
| `reemit_changes_no_model_answer` (families, grants, pins, names) | (above) | the same id set, and per entry: `name`, `flavor`, `grants`, `hostRole`, `hostFrame`, `archetype` identical, `aptitudes` equal as a set, and the ingredient FAMILY MULTISET equal — while the shape moved (no `grantedTier`, rows exactly `{family, quantity}`) |
| `_meta.amendments` records the batch (on `--write`) | the verb's write path | `__record_combogen_reemit_amendment` appends `combogen-reemit/<shape>-1` with the changed ids, a deterministic `authoredUtc`, and a note saying the model's answers are unchanged and only the shape moved |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('...authored.py','...cli.py','...test_strain_splice_gen.py') -Session strain-splice-host-20260921"` | exit **1** for the pre-existing reason only: `report/cli.py` maps to `seedsmith-fallback`, so the check is the WHOLE project — **23 failed / 4209 passed / 3 skipped**, the same 23 as before this change and **none** in combogen/authored/reemit. The scoped pytest file the row names is 111 passed / 11 subtests |

## Not proved / open

- **The corpus write is SSH7.6's**, deliberately: this row lands the VERB and its dry run. Until SSH7.5
  flips the C# consumers (`CombinationCorpus` filling `BaseTier` from tuning, `KindCatalog` dropping
  `grantedTier`), writing the re-emitted corpus would put rows in the tree the importer reads
  differently — the sequencing the module's own row order describes.
- `entries_from_ledger` reads whatever the ledger holds; a ledger whose `entry` rows were written by a
  later shape re-emits idempotently, which is what the byte-identity test pins.

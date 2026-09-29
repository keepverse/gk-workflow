# SSH8.1 — `recipegen/imbue.py`: the derived imbue emitter

New `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/imbue.py`, called from `run.py`'s existing
`--emit-deterministic` step (the caller `forgegem.py` and `repair.py` already share). One row per
`(bore frame, concrete element)`: the bore row's substrate + catalyst lines and its band VERBATIM, plus
`essence.<element>`; a derived `Imbue: <Frame> <Element>` name; idempotent on `(frame, element)`.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| one row per `(bore frame, concrete element)`, `omni` excluded, bore's lines + bands verbatim, derived name | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_recipes_gen.py -q` | **62 passed / 0** (60 + 4 new). `imbue_rows_are_derived_and_idempotent`: the plan is the PRODUCT of the two closed sets (today **3 bore frames × 6 concrete elements = 18 rows**), each row's lines are the bore frame's verbatim plus one essence line, one band per row taken from the bore row, `outputKind` `mutation`, no tags; a corpus already carrying the plan plans **0** |
| idempotent | (above) + the emitter's own dry run | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith.adapters.items.recipegen.run --emit-deterministic` → `"planned": 18` with no `--write`, so nothing under `data/` changes; re-planning over the merged corpus is empty |
| `opvocab.SUPPORTED_FOR_GENERATION` is NOT widened | (above) | `imbue_is_never_offered_to_the_model`: `"imbue" not in SUPPORTED_FOR_GENERATION`, it IS in `ALL_OPERATIONS`, and `require_supported_operation("imbue")` still raises. The pre-existing `test_unsupported_operation_is_refused_not_silently_accepted` (which asserts exactly that) is green again — the map it reads IS the gate, so the emitter's `outputKind` is stated locally in `imbue.py` with that reason in a comment, never added to the map |
| `every_imbue_row_names_a_concrete_element_essence` | (above) | exactly one `essence.<element>` line per row, and its element is in `concrete_elements()` |
| `omni_is_never_an_imbue_element` | (above) | `omni` is not in `concrete_elements()` (it lives under its own registry key) and `build_entry(..., "omni", ...)` refuses by name |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/imbue.py','gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/run.py','gk-forge/tools/seedsmith/tests/test_recipes_gen.py') -Session strain-splice-host-20260921"` | exit **1** for the pre-existing reason: the `seedsmith-items` focused run is **1 failed / 1089 passed**, and the failure is `tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` — the actions-corpus loader, unrelated to this change and red before it. Nothing in `test_recipes_gen.py` fails (62/0) |

## Not proved / open

- **The write is SSH8.2's**, not this row's: only the DRY RUN was executed, so `gk-data/packs/fusion/data/seed/items/recipes/
  recipes.json` is untouched. When SSH8.2 writes, `KindCatalog`/`ItemSeedValidator` must accept the new
  rows (an `imbue` row's `outputRef` is absent — it is a mutation — which the validator already allows for
  every mutation row).
- The `essence` band is the bore row's band by rule; a future bore row whose lines disagree on a band is
  refused by name rather than having the emitter pick one.
- The four priced legs (`materials.v{n}.json` `imbue`: souls + substrate + essence + catalyst) are the
  C# parser's business; this emitter only authors the corpus row.

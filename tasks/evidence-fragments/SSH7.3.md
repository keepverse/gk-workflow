# SSH7.3 — the generator emits no tier numbers; the ladder is validated instead (mirrors C#)

`emit.py` stops zipping `minTierPlan`: `IngredientRow` is `(family, quantity)`, identical families FOLD,
and `assemble_entry` writes no `grantedTier` (the `granted_tier` helper is deleted with it — nothing read
it any more). `combogen/tuning.py` gains the `TierLadderRung` mirror and validates an optional
`recipe.tierLadder` with the C# validator's rules, rule for rule.

**The shipped corpus is untouched by this row** — `gk-data/packs/fusion/data/seed/items/combinations/**` is still the old
shape until SSH7.4's deterministic re-emit, and the C# importer still reads the `minTier` those rows
carry until SSH7.5/7.6. This row changes what the generator WOULD emit.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `the_emitted_entry_carries_no_tier_number` | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **108 passed, 7 subtests passed**. The emitted entry has no `grantedTier`, each ingredient row is exactly `{family, quantity}`, and `minTier`/`grantedTier`/`baseTier`/`"tier"` appear nowhere in the document — plus the same four picks in another arrangement emit a byte-identical entry (the fold is order-independent) |
| identical families fold to `{family, quantity}` | (above) | `ingredient_rows(["atom.a","atom.a","atom.b","atom.c"])` → `[{atom.a: 2}, {atom.b: 1}, {atom.c: 1}]` in family order |
| `combogen/tuning.py` validates `tierLadder` with the same rules as C# | (above) | `TierLadderParityTests`: the shipped file loads as the one-rung ladder its `minTierPlan` describes (rung 1, those floors, delta 0); a published two-rung ladder replaces it whole; and SEVEN refusal cases — floors falling inside a rung, a grant delta that does not rise, a higher rung asking for less, a floor outside the insert ladder, a top rung past the atom ladder, rung 1 carrying a delta, an empty ladder — each raise `ComboTuningError`. The same seven are refused by the C# validator (`StrainSpliceGridTests.A_non_ascending_or_non_increasing_ladder_throws` + `A_ladder_whose_top_exceeds_the_atom_ladder_throws`) |
| the seedsmith items suites | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q -k "combination or combogen or strain_splice or items_adapter or base_types or linkage"` | **231 passed, 7 subtests passed** (4001 deselected) |
| the corpus is untouched and still validates | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **PASS — 3978 entries / 1013 files / 2589 warnings** (the same reading as before this row) |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<5 paths>) -Session strain-splice-host-20260921"` | exit **1** for the pre-existing reason only: the `seedsmith-items` focused run is **1 failed / 1093 passed**, and the failure is `tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` (the actions corpus loader, red before this change and unrelated to it). Nothing in combogen/tuning/emit fails |

## The top-bound rule's mirror, stated

The C# rule bounds the ladder's top against `FamilyExpansion.TierCount` (5). Python has no
`FamilyExpansion`; it validates against `seedsmith/numerics/model.py`'s `TIER_COUNT` (also 5), imported at
the call site so the two ladders are visibly one number. If those ever diverge, the parity test's
`a top rung past the atom ladder` case is the one that fires.

## Not proved / open

- SSH7.4 (the deterministic `combogen-reemit` that rewrites the shipped corpus into this shape) and
  SSH7.5/7.6 (the C# consumer flips and the corpus write) are untouched: until they land the corpus still
  carries `minTier`/`grantedTier` and the importer still reads `minTier`, which is the sequencing the
  module's own row order describes.
- `KindCatalog` (C#) and the Python `KindSpec` still REQUIRE `grantedTier` — removing it from the
  registries is SSH7.5/7.6's, in the same commit as the re-emit.

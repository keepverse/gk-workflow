# SSH7.6 — the shipped corpus carries no tier number (the deterministic re-emit ran)

`python -m seedsmith items combogen-reemit --write` (SSH7.4's verb) re-shaped all **98** shipped rows —
**32 strain + 66 splice** — and `KindCatalog`'s `combination` row lost `grantedTier` from `extra` in the
same commit, so a row that reintroduces a tier is refused rather than tolerated.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| the agent runs the deterministic re-emit; no model call | `cd gk-forge/tools/seedsmith; SEEDSMITH_ALLOW_PRODUCTION_TREE=1 PYTHONPATH=. python -m seedsmith items combogen-reemit --write` | exit 0, `strain 32/32 changed, splice 66/66 changed`; the same command without `--write` had printed the plan first |
| no combination row carries `minTier` or `grantedTier` | a JSON census over both files | **0 entries carry a tier field**; every ingredient row is exactly `{family, quantity}`; `_meta.amendments` gains `combogen-reemit/strain-1` and `combogen-reemit/splice-1` |
| `KindCatalog` extra drops `grantedTier` | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | **98 passed / 0** — the conforming fixture is tier-free, and a NEW test (`A_combination_row_carrying_a_tier_number_is_refused_by_name`) proves a row that adds `grantedTier` is refused (`UnknownKey`), so the narrowing is enforced rather than assumed |
| behaviour unchanged under v1 (one rung) | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" -c Release`; `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **15103 passed / 0** and **764 passed / 0**. `the_shipped_corpus_has_no_refusal` and the matcher's rung-1 tests are green; `CombinationCorpusTests.A_shipped_recipe_carries_the_mapped_fields` now asserts the tier comes from TUNING (the row no longer states one) and that every imported `MinTier` is 0 |
| the corpus still validates | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **PASS — 3978 entries / 1013 files / 2589 warnings** |
| the seedsmith gate | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --gate` | 57 gap / 607 note / 153 not_measured — **0 GAPs name a combination row** |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<3 mapped paths>) -Session strain-splice-host-20260921"` | `KindCatalog.cs` + the two test files resolve and are green (Core 15103/0, validator tests 97/0 at that point, `test-substrate` OK). ⛔ The two CORPUS paths cannot be passed: `gk-data/packs/fusion/data/seed/items/combinations/**` still has **no owner row** in `gk-core/scripts/verification-boundaries.v1.json`, which is the already-filed **TVB-F14** — the corpus evidence here is the validator, the seedsmith gate and the two suites run directly |

## Stale tests this row had to update (both were reading the fields it removes)

1. `GemTierTests`' `ToRecipe` helper re-mapped the corpus by hand, reading `grantedTier`/`minTier` — it now
   mirrors `CombinationCorpus.ToRecipes` (tuning's `BaseTierFor` + the ladder's rung-1 floors, `MinTier` 0),
   and `Every_ingredient_minTier_falls_inside_the_recipe_authoring_range` asserts the new SHAPE (no row
   carries a tier) plus the range check at its new home (the ladder's floors are inside `[1..insertTiers.count]`).
2. `SeedFixture.CombinationEntry`'s "conforming" template emitted the old shape, so it stopped being
   conforming the moment `extra` narrowed — updated, with a new test pinning the refusal.

## Not proved / open

- **The boot provenance check does not need a re-measure here** because SSH6.8 has not landed: no
  `sockets` revision carries `comboPricing.measuredAgainst` yet, so the corpus digest moving changes
  nothing at boot. SSH7.7 is the row that must republish provenance with the new digest.
- The corpus digest therefore changed with no published measurement to invalidate — recorded so the
  reviewer does not read the missing re-measure as an omission.

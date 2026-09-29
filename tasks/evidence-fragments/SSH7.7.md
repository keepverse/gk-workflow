# SSH7.7 — THE LADDER FLIP — **BLOCKED** on SSH6.8's prerequisites, with one defect fixed on the way

`publish.py strain-splice --add-key "recipe:tierLadder=[…]" --remove-key recipe:minTierPlan` can be run,
but landing it now would make the server **refuse to boot**, which is the opposite of this row's own
acceptance line.

## The coupling, proved

`ComboPricingProvenance.Check` refuses by name when a **multi-rung** ladder has no measurement:

- `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~A_multi_rung_ladder_needs_measured_combination_pricing"` → **1 passed / 0** — the test asserts
  `socket.combo-pricing-unmeasured` for a two-rung ladder with `measuredAgainst: null`, and `null` for a
  one-rung ladder.
- The spec's own rule for the other half: `measuredAgainst` is written **"only when the report passes"**
  (spec-combo-budget §4).

So the ladder publish, the passing report and the provenance are one atomic act — and the report is red:

| Check | Command | Result |
|---|---|---|
| the report's reading (after the fix below) | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith items combo-budget --report` | exit **1**: **47 cells cheaper than the rarity route, 126 unpriced**. The 47 need **SSH8.5**'s derived `materials` publish (SSH6.8's own dep) and the 126 need **SSH4.4**'s owner-run atom/corpus remedy — the same two blockers SSH6.8 carries |

Publishing rungs 2..n before those land would therefore either fail the boot check or (if published
without provenance, and the ladder stayed one rung) change nothing at all. The row stays OPEN.

## The defect this row found, and fixed here

**The pricing dump priced four tier-0 gems.** `ComboBudgetDump` derived its `IngredientTiers` from
`recipe.Ingredients`' `MinTier` — which SSH7.5/7.6 wrote as `0` — so after the re-emit the report read
**0 cells failing and 196 unpriced** instead of a real verdict: every floor collapsed to tier 0, and the
container refusals grew because the gem legs resolved against rung index −1. The dump now takes its tiers
from **`ComboRecipe.BaseFloors`** (rung 1's floors, read from the tuning at import) — exactly the floors
the matcher compares against — which is why the reading above is the honest 47/126.

| Criterion | Command | Result |
|---|---|---|
| the dump prices the ladder's floors, not the retired row field | `dotnet build gk-forge/tools/ItemSeedValidator -c Release`; the report above | build succeeded; the reading moved from a meaningless `0 failing / 196 unpriced` to `47 failing / 126 unpriced` |

## Not proved / open

- Everything else in the acceptance: the `strain-splice.v2.json` publish, the constant move (C# + Python),
  rungs 2..n being priced, the provenance republish and the server-boot reading. All of it waits on
  SSH6.8's two prerequisites.
- The `47`/`126` figures are the CURRENT corpus's reading; they will move again when SSH8.5 reprices and
  SSH4.4 materialises atoms, which is the point of re-measuring after those land.

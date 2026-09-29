# SSH7.2 — the matcher returns a rung; granted tier = base + rung delta + attunement

`ComboMatcher.Match` claims on `(family, quantity)` only and reads the LADDER: the claimed tiers, sorted
ascending, are compared positionally against the highest rung whose floors they meet. `MultisetMatch`
carries `Rung` (0 = none) and `TierShortfall(position, have, need)`; `CombinationEvaluator` grants
`baseTier + ladder[rung].grantDelta + attunement`; `CombinationDistance` counts the rung shortfalls so its
own distance-zero == "the evaluator fires" invariant survives; `StrainSpliceTuning` gains
`RungGrantDelta(rung)` + the four-argument `GrantedTier`.

**No ladder passed is not a second rule.** It is rung 1 with the floors the recipe's own ingredients state
(one floor per FILL, expanded by `quantity`) — exactly the shipped flat floor, so every pre-ladder caller
keeps its behaviour and `rung_one_reproduces_the_shipped_flat_floor` holds by construction.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `rung_one_reproduces_the_shipped_flat_floor` | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~ComboMatcher\|FullyQualifiedName~CombinationEvaluator\|FullyQualifiedName~ItemSurface"` | **81 passed / 0**. The no-ladder match reaches rung 1 and a fill below that floor does not fire |
| `higher_tier_gems_reach_a_higher_rung` | (above) | tiers 1/1/2/2 → rung 1; 2/2/3/3 → rung 2 (and the same tiers in any listed order → the same rung) |
| `every_permutation_of_a_fill_reaches_the_same_rung` | (above) | four permutations of one fill → one rung |
| `attunement_adds_its_bonus_on_top_of_the_rung_and_never_gates` | (above) | `GrantedTier(rung 2, attuned=false)` is `base + 1`; attuned adds exactly `attunedTierBonus`; rung 1 carries no delta; a fill whose affinities match nothing reaches the SAME rung as a fully attuned one |
| `a_fill_below_rung_one_reports_tier_shortfalls_not_missing_families` | (above) | all four families claimed, `Missing` empty, `ShortOfNext` names positions 2 and 3 as `have 1 / need 2`, `Rung` 0 |
| `rebalancing_the_ladder_needs_no_regeneration` | (above) | the same recipe + fill + a different ladder: rung 1 → no match → rung 2, with the corpus untouched |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<5 paths>) -Session strain-splice-host-20260921"` | exit **0** — `core-fallback` → **Core.Tests 15102 passed / 0** |
| the wider blast radius | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" -c Release`; `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **15102 passed / 0** (whole project) and **764 passed / 0** |

## Two defects this row found and fixed in itself (recorded, because both were caught by EXISTING tests)

1. **Floors must be per FILL, not per ingredient ROW.** The shipped shape authors one row with
   `quantity: 4`; deriving one floor per row made a four-insert recipe a ONE-floor ladder, so a
   perfectly good fill stopped firing. `FloorsFromTheRecipe` expands by `quantity`.
2. **A family match with too-low tiers is not distance zero.** The preview's old distance counted only
   missing families, so a fill the evaluator refuses now reported distance 0 — breaking the file's own
   property test (`distance-zero == evaluator fires`). The distance now adds the rung's shortfall
   positions, which is also what the socket bench needs to say *why*.

## Not proved / open

- SSH7.3-7.8 remain: the generator still emits `minTier`/`grantedTier`, the corpus is not re-emitted, the
  preview DTO does not yet SHOW the shortfalls (the matcher reports them; wiring the row is module 20's),
  and the ladder is still one rung until SSH7.7 publishes it.
- `CombinationDistanceRow` carries the missing families as before; the tier shortfalls reach the caller
  through `ComboMatcher.Match`'s `ShortOfNext` and are counted in the distance, not yet added as a row
  field.

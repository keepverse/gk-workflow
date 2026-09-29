# SSH7.5 — the C# side stops reading the corpus's tier fields

`CombinationCorpus.ToRecipes` fills `ComboRecipe.BaseTier` from `StrainSpliceTuning.BaseTierFor(shape)`
and writes `ComboIngredient.MinTier = 0` on every loaded ingredient — the row's own `grantedTier`/`minTier`
are parsed (SSH7.6 drops them from the seed) and deliberately UNREAD. `ComboRecipe` gains `BaseFloors`
(rung 1's floors, read from the tuning's ladder at import) so a pre-ladder caller's rung 1 stays
byte-identical while no seed carries a tier; the matcher derives its no-ladder rung 1 from them and now
REFUSES a non-empty recipe that carries no floor at all. `StrainSpliceRules.BaseTierNotTunable` and its
check are deleted, and `KindCatalog` no longer requires `grantedTier`.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `BaseTier` from tuning, `MinTier` written 0, the rung-1 floors carried on the recipe | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~CombinationCorpus"` | **7 passed / 0**. `The_imported_recipe_takes_its_tier_and_floors_from_tuning_never_from_the_row`: a row declaring `grantedTier: 9` and `minTier: 5` imports with `BaseTier == tuning.BaseTierFor(Strain)` (and NOT 9), `MinTier == 0` on every ingredient and `BaseFloors == tuning.TierLadder[0].Floors` |
| `strainsplice.base-tier-not-tunable` is DELETED, not left as dead code | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" --filter "FullyQualifiedName~StrainSpliceGrid\|FullyQualifiedName~CombinationCorpus"` | **33 passed / 0** (82 with the matcher/evaluator filters). The const and its check are gone, and `Every_refusal_is_a_namespaced_content_rule_and_all_of_them_are_returned` now asserts the absence by reflection over the rule ids — 4 content rules where it used to be 5 — so a resurrected id fails rather than silently checking nothing |
| `KindCatalog` drops `grantedTier` from required (extra still allows it until SSH7.6) | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests`; `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **97 passed / 0** and **PASS — 3978 entries / 1013 files / 2589 warnings**: today's rows still carry the field and still validate through `extra` |
| the matcher's no-ladder path does not silently qualify every fill | (the Core filters above) | `FloorsFromTheRecipe` refuses a non-empty recipe with no floors at all (the loud failure SSH7.2 documented) while a recipe with NO ingredients still answers "unsatisfied" rather than throwing |
| the wider blast radius | `dotnet test "gk-core/tests/FusionRpg.Core.Tests" -c Release`; `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **15103 passed / 0** (whole Core) and **764 passed / 0** |
| boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<7 paths>) -Session strain-splice-host-20260921"` | exit **0** — `core-fallback` 15103/0, `itemseedvalidator-fallback` 97/0, `test-substrate` guard OK |

## The one design choice worth naming

The seed stops carrying tiers (SSH7.3) while the matcher still needs a rung-1 floor. Rather than plumb
the tuning through every `Evaluate` call site, the IMPORTER reads it once and puts it on the recipe
(`BaseFloors`) — the same "filled from tuning at import" rule the spec already states for `BaseTier`. A
caller that HAS the full ladder still passes it (rungs 2..n are SSH7.7's); a caller that does not gets
rung 1 exactly as shipped.

## Not proved / open

- **The corpus write is SSH7.6's**: the shipped rows still carry `grantedTier`/`minTier`, which is why
  the KindCatalog field is only moved from `required` to `extra`. Dropping it from `extra` and re-emitting
  land together.
- SSH7.7 (the ladder publish + re-measure) and SSH7.8 (the owner DDL) remain.

# SSH7.8 — DDL: drop `socket_combo_ingredient.min_tier` and `ComboIngredient.MinTier`

**Owner-approved 2026-09-21** (brief): execute the drop under **H2** — a migration precedes writes to a
re-keyed table. The re-key is `(combo_id, family_id, min_tier)` → `(combo_id, family_id)`; the table is
DROPPED whole on a boot that still sees `min_tier` and rebuilt by the same `CREATE` (idempotent
afterwards), and `CombinationBoot` re-seeds the content on that boot.

**One consequential addition (H2, same commit):** `socket_combo_recipe.base_floors`. `ComboRecipe.BaseFloors`
(SSH7.5) is the no-ladder rung 1 the matcher reads, and the store round-trip (`GetComboRecipes` →
`GET /api/items/{id}/combinations`) was previously reconstructing it from the `min_tier` column. With that
column gone the recipe's floors had to be persisted, or every store-loaded recipe throws at match time.
The column is additive (`EnsureColumn`, before any write) and boot re-seeds it, so a ladder publish cannot
leave a stale floor behind.

| Criterion | Command | Result |
|---|---|---|
| `min_tier` leaves the columns and the primary key | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~The_pre_SSH78_ingredient_table_is_re_keyed"` (in the suite below) | PASS — boot over a hand-seeded pre-init hot DB: `PRAGMA table_info(socket_combo_ingredient)` reads exactly `combo_id`, `family_id`, `qty` |
| the content table is dropped and re-seeded at boot | (above) | PASS — the pre-migration ingredient row is GONE after `Init()` (`GetComboRecipes` → `Empty`), then `SeedComboRecipes` lands on the new key and reads back `atom.might x4`; a second `Init()` does not drop again |
| `ComboIngredient` loses `MinTier` | `grep -rn "MinTier" gk-core/src/FusionRpg.Core/Items/Sockets/` | no `ComboIngredient.MinTier` remains; `MissingIngredient` dropped its tier label too (a shortfall is family+count; `TierShortfall` carries the rung's position/need). `ComboRecipe.BaseFloors` is the only floor carrier |
| the socket store stays green | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"` | **13 passed / 0** (was 12; +1 re-key test) |
| the DAL boundary is intact | `pwsh -NoProfile -File scripts/guard-dal.ps1` | DAL GUARD OK |
| scoped boundary | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths @(…15 paths…) -Session strain-splice-host-20260921` | **exit 0** — Core.Items.Tests 1396/0, Data (filtered ItemSocketStore) 41/0, Server.Tests 788/0, test-substrate guard OK |

## Not proved / open

- **The corpus digest moved.** `CombinationCorpus.Digest` no longer folds `@minTier` (constant 0 since
  SSH7.5), so the digest reading changes. Nothing published a `comboPricing.measuredAgainst` yet
  (SSH6.8/SSH7.7 are red-blocked), so no boot check is invalidated today; a future publish takes the new
  digest from the report.
- **Session id.** The brief names `strain-splice-host-20260922`; no such record exists and the allowed
  paths list only `tasks/sessions/strain-splice-host-20260921.json`, so verification ran under the
  existing active record for this program.
- The preview endpoint still evaluates with **no ladder** (`ItemSurfaceEndpoints.cs:209`), so it reads the
  recipe snapshot rather than `StrainSpliceTuning.TierLadder`. Passing the live ladder is the SSH7.7/SSH4.x
  wiring, not this row's.

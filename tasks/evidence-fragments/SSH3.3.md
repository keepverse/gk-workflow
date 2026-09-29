# SSH3.3 — Boot reads `combinations/*.json`, validates, prints and skips, seeds + disables

## What changed

- `gk-core/src/FusionRpg.Server/CombinationBoot.cs` (new) — the boot import: `ReadArchetypes(seedRoot)` (module
  13's registry, host-side) and `Seed(store, sockets, strainSplice, archetypes, combinationsDir, log)`:
  read `*.json` → `CombinationCorpus.Parse` → `ToRecipes` → `StrainSpliceGrid.ValidateRecipe` per
  recipe → seed `resonances.Concat(accepted)` → `DisableCombinationsNotIn(accepted ids)`. Prints each
  refusal by rule id and a one-line count. An absent archetype axis refuses every authored recipe
  (never seeds an unvalidated one).
- `gk-core/src/FusionRpg.Server/Program.cs` — the inline "print and seed" block is replaced by one call to
  `CombinationBoot.Seed(...)`; the archetype read moved with it.
- `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs` — `the_shipped_corpus_has_no_refusal`.
- `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs` (new) — the three Server-side acceptance
  tests. (A new file rather than an endpoint test file: the import is a boot sequence, not a route.)

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| print and skip; accepted seeded, then `DisableCombinationsNotIn` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~CombinationImport"` | 3 passed, 0 failed (`A_refused_recipe_is_never_seeded`) |
| `the_shipped_corpus_has_no_refusal` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus"` | 6 passed, 0 failed |
| `boot_seeds_the_real_corpus_end_to_end` (real corpus, Strain read back) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~CombinationImport"` | 3 passed |
| `the_item_card_and_the_endpoint_read_the_same_catalog` (one construction site) | same run | 3 passed |
| endpoints unchanged | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints\|FullyQualifiedName~ItemCardEndpoints"` | 37 passed, 0 failed |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

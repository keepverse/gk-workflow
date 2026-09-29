# SSH3.2 — `RpgStore.DisableCombinationsNotIn(acceptedIds)`

## What changed

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs` — `DisableCombinationsNotIn(IReadOnlySet<string>)`
  selects the enabled rows whose id is in the authored space (`combo.strain-` / `combo.splice-`,
  read from `StrainSpliceGrid`'s own prefixes, never literals) and not in the accepted set, then sets
  `enabled = 0` (never deletes; `revision` bumps). Resonance rows are a different id space and are
  never touched. No DDL.
- The same `SeedComboRecipes` upsert now sets `enabled = 1` on conflict: without it, a row retired one
  boot would stay dark even after the corpus authors it again, since `DisableCombinationsNotIn` is the
  only writer of `enabled = 0`.
- `gk-core/tests/FusionRpg.Data.Tests/Items/ItemSocketStoreTests.cs` — the two acceptance tests.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| absent combination is disabled and drops out of `GetComboRecipes` | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"` | 11 passed, 0 failed (`A_combination_absent_from_the_corpus_is_disabled_on_next_boot`) |
| resonance rows are never disabled | same run | `Resonance_rows_are_never_disabled_by_the_import` (empty accepted set still retires 0 resonances) |
| SQL stays inside `FusionRpg.Data` | `pwsh -NoProfile -File scripts/guard-dal.ps1` | exit 0, `DAL GUARD OK` |

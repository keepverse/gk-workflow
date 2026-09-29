# Task 7 — persist + catalog + Mapper

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 7. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §4.
Edited: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs` (nullable column, INSERT/ON CONFLICT, read-back,
`SameContent`, validator note), `gk-core/src/FusionRpg.Core/Creatures/CreatureSpeciesCatalog.cs`
(`CreatureSpeciesDef.Rank` + `Validate` treatment named), `Generation/ConcreteSpeciesSeedReader.cs`
(the Mapper funnel passes it), `gk-core/tests/FusionRpg.Data.Tests/SpeciesImportStoreTests.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureCatalogTests.cs`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| nullable column via `EnsureColumn` | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~SpeciesImportStoreTests"` | **Passed! — Failed 0, Passed 17, Total 17, 1 s**; the column is `TEXT`, no default, and `A_skipped_rank_round_trips_as_null_never_a_bottom_rung` proves the NULL path | `RpgStore.Species.cs` |
| null-safe read-back | same run | `Rank == null` reads back as null; a present-but-unparseable id THROWS naming the species (same shape as rarity/elementPrimary) | same |
| `SameContent` compares rank (reimport idempotent) | same run — `A_reimport_with_the_same_rank_is_unchanged_and_a_changed_rank_rewrites` | same rank → `Unchanged == 1`; a rank-only change → `Written == 1` and the new value reads back | same |
| `CreatureSpeciesDef` + `Validate` carry rank | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~Catalog\|FullyQualifiedName~ConcreteSpecies\|FullyQualifiedName~CreatureRank"` | **Passed! — Failed 0, Passed 331, Total 331, 1 m 17 s**; `The_mapper_carries_rank_and_a_skipped_rank_survives_Validate_untouched` asserts both the ranked and the skipped case survive `Validate` with the value untouched | `CreatureSpeciesCatalog.cs` |
| Mapper funnel passes it | same run | `ConcreteSpeciesMapper.ToCreatureSpeciesDef` carries `Rank` through, defaulted nowhere (null stays null) | `ConcreteSpeciesSeedReader.cs` |
| SQL stays in the DAL | `pwsh -NoProfile -File scripts/guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data` | — |
| Whole Data project (sharded) + Core group + guards | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs','gk-core/src/FusionRpg.Core/Creatures/CreatureSpeciesCatalog.cs','gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSeedReader.cs','gk-core/tests/FusionRpg.Data.Tests/SpeciesImportStoreTests.cs','gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureCatalogTests.cs') -Session creature-seed-rank"` | **`VERIFY_EXIT=0`** — plan resolved `data-fallback (module)`, `core-fallback` ×2, `core-creature-catalog-generator (focused)`, `data-tests-fallback`; `test: core` + `test: core core.creature-catalog-generator` + `test: data (sharded runner)`; **67 `Passed!` assemblies, 0 `Failed!`, 15 647 tests passed in total**; `TEST-SHARDED OK: 4 shards, 1732 tests, no overlap` | — |
| Species/creature surface of Data.Tests (unsharded, direct) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~Species\|FullyQualifiedName~Creature"` | **Passed! — Failed 0, Passed 136, Total 136, 2 m** | — |

## NOT proved / decisions

- "Old DBs read null without crash" is proven at the ROW shape, not by building a genuinely pre-rank
  database file: `EnsureColumn` adds the column nullable with no default, and a row written with
  `Rank = null` is byte-for-byte the shape such a database yields. The migration path itself
  (`EnsureColumn` on an existing table) is exercised by the store's own long-standing column-addition
  tests, which ran green in the sharded Data project above.
- `Validate` deliberately refuses NOTHING for rank: it is a closed enum already parsed at every boundary
  (DAL read-back, committed-tree SeedReader, Mapper) and null is legal, so a refusal or a default there
  would either be dead code or would fabricate the bottom rung (Assumption 4). Stated in code.
- The DAL validator likewise needed **no** rank refusal — a nullable column whose NULL is non-failing.
  One line, stated on purpose so it does not read as an oversight.
- `guard-dal.ps1` is the only static guard in this task's Verify line and it is green; the full
  `run-guards.ps1 -Tier ci` was not run (the `population-pin` red of CS-R2 is still open at the
  integration tip and belongs to another lane).

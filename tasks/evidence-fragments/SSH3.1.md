# SSH3.1 — `CombinationCorpus.ToRecipes`, a pure Core mapper that refuses by name

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs` (new) — `CombinationEntry` (the
  `combination` kind's field shape) + `CombinationCorpus.Parse(string)` (host reads the file, Core
  parses the text, the `SocketTuning.Parse` split) + `ToRecipes(entries, tuning)`. Mapping refuses a
  blank id, an unknown shape, a missing ingredients array, a duplicate id, or a shape the tuning
  prices no `baseTier` for — each refusal names the row; a null/non-object row is a refusal, never a
  throw. `ComboRecipe`: `Element = ""`, `Threshold = 0`, `HostRole`/`HostFrame` `?? ""`,
  `MinSockets`, `BaseTier = grantedTier`, ingredients carried through.
- `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceGrid.cs` — `StrainSpliceRules.MalformedEntry`
  (`strainsplice.malformed-entry`) added to the registered rule namespace (no new rejection enum).
- `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs` (new).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| maps `CombinationEntry` → `ComboRecipe` per spec §1 | `dotnet test tests.FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus\|FullyQualifiedName~StrainSpliceGrid"` | 27 passed, 0 failed |
| a malformed entry is an `AtomRejection`, never an exception | same run | `A_refusal_names_the_entry_that_caused_it`, `A_local_row_can_never_throw_the_mapper_down` |
| `every_shipped_combination_entry_maps_or_is_refused_by_name` (real corpus, `recipes + refusals == entries on disk`) | same run | `recipes + refusals == 95 on disk`, 0 refusals |
| Core reads no file | `CombinationCorpus.Parse(string)`; the tests do the `File.ReadAllText` | — |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |

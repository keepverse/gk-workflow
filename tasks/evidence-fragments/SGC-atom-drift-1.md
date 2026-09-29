# SGC-atom-drift-1 — the stale generated atom tree regenerated (closes `atom-family-expansion-todo.md:623`)

The live-qa lane filed this on 2026-09-20 (`tasks/atom-family-expansion-todo.md:623`) and could not
fix it; `gk-data/packs/fusion/data/seed/atoms/generated/**` is inside this lane's fence, so wave 1 ran the generator and
committed the diff. No generator edit: `gk-forge/tools/FamilyExpandGen` was not touched.

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| The drift reproduces, one file named | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | exit=1 :: `1 generated file(s) stale … gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` | — |
| Regenerated, not hand-edited | `dotnet run --project gk-forge/tools/FamilyExpandGen` | `1 file(s) written, 0 stale file(s) removed`; `git diff --stat` = **5 insertions, 10 deletions** in that one file | gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json |
| The drift is gone | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | exit=0 :: `--check: clean, 11 generated file(s) match` | — |
| The red byte-identity test is green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FamilyExpansion" -v minimal --nologo` | exit=0 :: `Passed: 36, Failed: 0` (the previously red `Committed_generated_files_match_the_generator_byte_for_byte` included) | tests/FusionRpg.Core.Tests/Atoms/Generation/FamilyExpansionTests.cs |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json -Session species-gear-chain-20260920` | exit=0 :: `test: core` **14899 passed, 0 failed** (was 14898/1) + `test: elementenumgen` **17 passed** | — |

Notes
- The diff is five rows' `tags` dropping `"utility": "1"` while keeping `"defensive": "1"`. The filed
  row's description was **directionally inverted** ("the fresh output carries a `utility` key beside
  `defensive` that the committed file lacks"): the committed tree carried both keys, so the stale tree
  was the pre-exclusivity one. The remedy it named was right, and it is what ran here.
- Cause (read from the tree, not the symptom): `e1d9103e item-seed corpus: enforce tag-axis exclusivity
  at emit time, then regenerate (cause 8a)` changed this tree's own input
  (`gk-data/packs/fusion/data/seed/items/affix-families/g-evade.json`) and regenerated the item-side trees, but left
  `gk-data/packs/fusion/data/seed/atoms/generated/**` behind. One cause, one file, no hand edit.
- NOT proven here: the other ten generated atom files are byte-identical (that is what `--check: clean`
  reads), but the generator's own 11-file output was not diffed against a second run for determinism —
  `--check` is the tool's own determinism gate and it passes.

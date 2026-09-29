# Spec: `recipe-import`

**Module id:** `recipe-import` · **Program:** [strain-splice-host](../strain-splice-host-map.md) ·
**Build order:** 3 of 8 · **Depends on:** `combination-regen` (2) · **Finding closed:** F2.

## Objective

**Nothing the combination generator writes reaches the running game.** The server seeds
`socket_combo_recipe` with exactly the 25 generated resonances
(`gk-core/src/FusionRpg.Server/Program.cs:458` builds them, `gk-core/src/FusionRpg.Server/Program.cs:491` seeds them);
no code in `src/` reads `gk-data/packs/fusion/data/seed/items/combinations/`. The grid validator that was put in "before the
content" (`gk-core/src/FusionRpg.Server/Program.cs:479`) runs over the resonances only — and even there it
**prints** a refusal and then seeds the recipe anyway (`gk-core/src/FusionRpg.Server/Program.cs:482` → `gk-core/src/FusionRpg.Server/Program.cs:491`).

This is a wiring gap in the RPG layer, not a missing capability: the table, the evaluator, the
validator, the item card and the socket bench all exist. This module connects the corpus to them.

**User outcome:** every legal Strain and Splice the generator authored is evaluable, previewable and
(after `combo-bind`) bindable; an illegal one is refused at boot by name and never seeded.

## Design

### 1. A pure mapper in Core, file I/O in the host

Core reads no file (tunables-ssot §7.2). Add (new) `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs`:

```text
CombinationCorpus.ToRecipes(IReadOnlyList<CombinationEntry> entries, StrainSpliceTuning t)
    -> (IReadOnlyList<ComboRecipe> recipes, IReadOnlyList<AtomRejection> refusals)
```

`CombinationEntry` mirrors the `combination` kind the C# validator already defines
(`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132`). `ComboRecipe` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:124`)
is filled as: `ComboId = id`, `Shape` from `shape`, `Element = ""`, `Threshold = 0`,
`HostRole = hostRole ?? ""`, `HostFrame = hostFrame ?? ""`, `MinSockets`, `BaseTier = grantedTier`,
`Ingredients` from `ingredients[]`. A malformed entry is a refusal, never an exception, so one bad row
does not block boot (the refusal-by-name pattern `GemContainerBuild.TryBuildOne` already uses,
`gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:43`).

The server reads `gk-data/packs/fusion/data/seed/items/combinations/*.json` next to the other item seed reads (the tree is
already copied to output, `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj:66`, ledgers excluded).

### 2. The validator gates the seed

Every mapped recipe goes through `StrainSpliceGrid.ValidateRecipe`
(`gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceGrid.cs:123`) with the tuning supplied, so all five
rules apply: on the grid, four ingredients, `minSockets` derived, host role can hold four, `baseTier`
equals the tunable one. **A recipe with any refusal is not seeded** — the boot block is changed from
"print and seed" to "print and skip". Refusals are printed by rule id and counted, the same shape the
block already has. Once `combo-bind` lands, a recipe whose combination container cannot be built is
refused the same way (`combo-bind` §1: one acceptance set).

**Skip at boot, fail in CI — decided (strengthen pass 2026-09-18).** Refusing to *boot* over one bad row
would make one generator defect take the whole game down; skipping it silently would let a defect ship
as a quietly missing word. Both halves are needed: boot skips by name, and a Core test over the **real**
corpus asserts that the shipped corpus produces **zero** refusals (a contract on the shipped files, not a
population count), so the skip path is reachable only by an un-validated local tree, never by a commit.
R13's still-blocked cells are not refusals: a blocked cell writes no entry.

### 3. Retired rows go dark, not stale

`SeedComboRecipes` upserts and never deletes (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs:161`); a
Strain removed from the corpus would keep firing from last boot's row. The import therefore owns the
`combo.strain-*` / `combo.splice-*` id space: after seeding, any row in that space **not** in this boot's
accepted set is set `enabled = 0` (the column exists, `RpgStore.Sockets.cs:61`, and the catalog read
filters on it, `RpgStore.Sockets.cs:251`). Resonance rows (`combo.pure-*` etc.) are untouched. No DDL
change.

### 4. One catalog read for every consumer

After this module the evaluator, the item card and the combinations endpoint all read the same
`GetComboRecipes()` result; nothing constructs a recipe list elsewhere.

## Seedsmith / generator

**No generator change.** This module consumes what `combination-regen` writes.

| Item | Detail |
|---|---|
| Adapter / stage | none changed; the contract it reads is `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:144` (`assemble_entry`) |
| New seed fields | none |
| Magnitudes | `baseTier` is checked against `gk-core/data/tuning/strain-splice.v1.json`; ingredient count against `gk-core/data/tuning/sockets.v1.json` |
| Check (pre-flight) | `python -m seedsmith items validate --deps` · `dotnet run --project gk-forge/tools/ItemSeedValidator` |
| Pytest | none (C# only) |

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ItemCardEndpoints"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session-id>
```

## Project structure

```text
gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs      (new)  entry -> ComboRecipe, refusals by name
gk-core/src/FusionRpg.Server/Program.cs                                    read combinations/*.json, validate, seed accepted only
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs                      DisableCombinationsNotIn(acceptedIds)
gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs (new)
```

## Code style

```csharp
// "Print and skip", never "print and seed": a recipe the grid refuses is content no cell asked
// for, and seeding it anyway makes the refusal decorative.
var accepted = recipes.Where(r => StrainSpliceGrid.ValidateRecipe(r, sockets, archetypes, strainSplice).Count == 0).ToList();
store.SeedComboRecipes(resonances.Concat(accepted).ToList());
store.DisableCombinationsNotIn(accepted.Select(r => r.ComboId).ToHashSet(StringComparer.Ordinal));
```

## Testing strategy

| Test | Asserts |
|---|---|
| `every_shipped_combination_entry_maps_or_is_refused_by_name` | over the real corpus: `recipes + refusals == entries on disk`, never a silent drop |
| `a_refused_recipe_is_never_seeded` | fixture with an off-grid id, a 3-ingredient recipe, a `ward-array` host under today's ceilings |
| `a_combination_absent_from_the_corpus_is_disabled_on_next_boot` | seed, remove from the fixture corpus, re-seed → `enabled = 0`, absent from `GetComboRecipes` |
| `resonance_rows_are_never_disabled_by_the_import` | the id-space boundary |
| `the_item_card_and_the_endpoint_read_the_same_catalog` | one read |
| `the_shipped_corpus_has_no_refusal` | over the real `gk-data/packs/fusion/data/seed/items/combinations/`: grid refusals (and, after `combo-bind`, container refusals) are empty — CI fails where boot would only skip |
| `boot_seeds_the_real_corpus_end_to_end` | a Server test booting against the real `gk-data/packs/fusion/data/seed/items/combinations/` and reading a real Strain back through `GetComboRecipes` |

⛔ No test asserts how many combinations load. `accepted + refused == on disk` is the contract.

## Boundaries

**Always:** validate before seeding; refuse by name; keep resonance generation where it is
(`ResonanceGenerator`).

**Ask first:** any DDL change to `socket_combo_recipe` (none is needed).

**Never:** read the combination corpus from Core; seed a refused recipe; delete recipe rows (disable
them — a row may be referenced by history); hand-edit the corpus to make a refusal go away (fix the
generator, module 2).

## Success criteria

- [ ] Boot seeds every grid-valid generated Strain/Splice beside the 25 resonances.
- [ ] A grid-invalid entry is printed by rule id and not seeded.
- [ ] A combination removed from the corpus stops evaluating after the next boot.
- [ ] Every consumer reads one catalog.

## Open questions

None.

# SSH8.3 + SSH8.2 — the essence names the element, and the imbue rows ship with their executor

Two rows land together, because the corpus cannot outrun its executor: SSH8.3 adds the essence/element
rule to `ItemWorkbench.SocketImbue` (and refreshes the doc that still said the verb had no recipes), and
SSH8.2 re-runs the deterministic write now that an executor exists. The guard that forced the pairing —
`EveryRecipeOperationWithRowsHasAnExecutorExceptElevate` — gains `"imbue"` in the same commit as the rows.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `imbue_element_mismatch` refused by name, no new enum member | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"` | **62 passed / 0** (59 + 3 new). `SocketRules.ImbueElementMismatch = "socket.imbue-element-mismatch"` joins the existing `socket` namespace; `Imbuing_with_a_mismatched_essence_is_refused_by_name` posts the FIRE row (`recipe.070`, `essence.fire`) asking for `ice` → **409** with the rule, `essence.fire` and `ice` all in the reason, no spend row, and the socket's affinity still `""` |
| a chaff chassis goes bore → imbue → fill end to end, with real debit | (above) | `A_chaff_chassis_can_be_bored_imbued_and_filled_end_to_end`: a chaff host (`SeedHostAt("chaff")`) is bored, attuned to `fire` (`CountMaterialSpendLog` strictly grows — the essence is really paid), then filled through `socket-insert`; read back through `GetSockets` → `Affinity == "fire"`, the gem id and a real minted `InsertInstanceId`, not empty |
| rarity scales the price, never the possibility (D23) | (above) | `Bore_and_imbue_cost_more_on_a_higher_rung_and_succeed_on_both`: bore and imbue souls legs resolve strictly higher at the top rung than at `chaff` (asserted with both values printed on failure), and both hosts complete **both** verbs, each priced at its own rung |
| `imbue_legs_equal_bore_legs_plus_essence` stays green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~MaterialCorpus"` | **20 passed / 0** (`Socket_imbue_has_a_cost_row_and_prices_like_bore` included) |
| the corpus rows land with their executor (SSH8.2) | `cd gk-forge/tools/seedsmith; SEEDSMITH_ALLOW_PRODUCTION_TREE=1 PYTHONPATH=. python -m seedsmith.adapters.items.recipegen.run --emit-deterministic --write` | **18 imbue rows** (`recipe.070`–`recipe.087`, one per bore frame × concrete element) plus `_meta.amendments: recipegen/deterministic-emit-1` recording exactly those ids; `EveryRecipeOperationWithRowsHasAnExecutorExceptElevate` **1 passed / 0** with `imbue` in the set |
| the corpus still validates | `dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` | **PASS — 3978 entries / 1013 files / 2589 warnings** (3960 + 18) |
| the seedsmith gate | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --gate` | 57 gap / **607 note** / 153 not_measured — **0 GAPs name an imbue row** |
| the emitter's own suites | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_recipes_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **96 passed** |
| whole Server suite | `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **764 passed / 0** (761 + the 3 new) |
| scoped verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs','gk-core/src/FusionRpg.Server/ItemWorkbench.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs','gk-data/packs/fusion/data/seed/items/recipes/recipes.json') -Session strain-splice-host-20260921"` | exit **0** — `recipes-corpus` (the corpus path HAS an owner row), `core-fallback` **15091 passed / 0**, `server-item-workbench` **65 passed / 0**, `server-tests-fallback` **761 passed / 0**, DAL guard OK |

## A defect the fixture taught, recorded

`PersistLoot` returns early for a `LootManifest.CorrelationId` it has already seen **without inserting the
generation rows**, so a second host seeded with the same manifest id gets no `item_generation` stamp and
every later verb refuses it with `item.generation-missing`. `SeedHostAt` now keys one manifest per rung and
asserts the stamp landed, so that failure surfaces at the helper rather than as a puzzling refusal.

## Not proved / open

- No live probe: an imbued socket has not been exercised in a running game (CC8's deferred live half).
- `SocketOperations.TryImbue`'s own Core rules (empty socket, crafted at the bench, concrete element only)
  were already landed and unchanged; this row added the corpus/price side and the essence rule.
- The 9 extra gate NOTES the new rows introduce are note-severity provenance/pairing readings, not gaps.

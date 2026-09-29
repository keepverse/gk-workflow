# T34d-wire — wire the real species binding into `ItemWorkbench` (T34d prerequisite)

Task: tasks/species-gear-chain-todo.md T34d-wire · coordinator ruling 2026-09-20 ("unwired is not done")

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Real Enhance call resolves the real concrete trophy id; species-less costs unchanged; two disagreeing sets refuse by name | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchSpeciesWiringTests"` | exit=0 :: 3 passed (real spend debits `trophy.species.abyssswordstar.1`; species-less has no trophy line; ambiguous species refuses `item.species-ambiguous`) | `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs` |
| Every existing workbench call byte-identical (T32 SC2 still holds) | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpointsTests"` | exit=0 :: 58 passed, unchanged | `gk-core/src/FusionRpg.Server/ItemWorkbench.cs` |
| `RecipeContext.TrophyStock` resolver unaffected by the delegate-type change | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"` | exit=0 :: 125 passed | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialRecipeCatalog.cs` |
| Spend-side store round trip unaffected | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"` | exit=0 :: 12 passed | — |
| No parallel composer; SQL only in Data | `.\scripts\guard-actor-hub.ps1` | ACTOR-HUB GUARD OK | — |
| Full boundary re-run | `.\scripts\verify-change.ps1 -Paths <5 touched files> -Session summoner-convergence-lane-c-20260919` | dal guard OK; Core.Tests 14393/14393; Server.Tests 564/564; server.item-workbench focused 59/59 | — |

## The wiring

`SetCorpus.SpeciesIdFor(containerId, sets)` — new `ContainerSpeciesLookup(SpeciesId, Ambiguous)`,
narrowing `SetEvaluator.Hits`'s own `(ContainerId, Role) -> set ids` join to one container's
`SpeciesId`; 0 hits -> `None`, 1 -> resolved, 2+ disagreeing -> `Ambiguous: true` (refuse, never guess).

`ItemWorkbench` gains three optional delegates (`speciesIdForContainer`/`speciesRungIndexFor`/
`familiesForSpecies`, all `null` by default — the same "wire it now, real callers catch up later"
posture as `_lookupGemSeed`). `TryResolve` calls `speciesIdForContainer` once per resolve and refuses
by name (`item.species-ambiguous`) on a disagreement instead of picking either set.
`RecipeContextFor` is now an instance method taking `playerId`; when `BoundSpeciesId` is set, its
`TrophyStock` delegate is `materialId => _store.GetMaterialQty(playerId, materialId)` — one targeted
read per candidate id the resolver actually asks about, never a bulk snapshot (T34d-wire's own "never
a full-table scan" criterion). This forced `RecipeContext.TrophyStock`'s own type from T34b's
`IReadOnlyDictionary<string, long>?` to `Func<string, long>?`; the 2 affected T34b tests
(`MaterialTrophyResolveTests.cs`) now wrap their fixture dictionaries through a small `StockOf` adapter.

The Server test seeds a real `DataTestStore`, imports a real `SetDef` naming the container's species
via `RpgStore.ImportSetCorpus`, grants a real trophy balance via `RpgStore.GrantMaterials`, and calls
`ItemWorkbench.Enhance` end to end — matching the live-probe-standard's own bar (a debug API proves
nothing; this drives the real path: `TryResolve` -> `RecipeContextFor` -> `MaterialRecipeCatalog.Resolve`
-> `TrySpendAndApply`), then reads the debited balance back through `RpgStore.GetMaterialQty` rather
than trusting the DTO alone.

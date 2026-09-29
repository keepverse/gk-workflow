# SSH8.6 — `no_price_reads_the_actors_worn_combinations`

**DONE 2026-09-22 (lane `ssh29`).** The scan lives in SSH6.5's guard file
(`gk-core/tests/FusionRpg.Guard.Tests/ComboCountCapGuardTests.cs`), which is what the row's Files field already
named and what the row's Verify filter already selected.

| Criterion | Command | Result |
|---|---|---|
| the workbench cost path reads nothing the actor wears | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ComboCountCap"` | **2 passed / 0** |
| identifiers | (in the guard) | `Loadout`, `Equipped`, `EquippedBoundAtoms`, `CombinationResult`, `GetComboRecipes`, `ComboCount` over `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, comments skipped — **zero hits** |
| the cost path's shape is target + recipe only | (in the guard) | `RecipeContextFor(long playerId, WorkbenchTarget t)` is matched and required to take exactly **two** parameters, so a later edit cannot add a loadout/equipped-set input unnoticed |
| the two guard tests together | (above) | 2 passed, 0 failed |

## Not proved / open

- The scan covers the workbench cost path file the spec names (`ItemWorkbench.cs`). The Core resolvers it
  calls (`MaterialRecipeCatalog.Resolve`, `SocketOperations`) already take a `RecipeContext` and a recipe,
  and no `*Composer*`/loadout type appears in their signatures; a wider scan was not added because the
  acceptance names the workbench cost path, and a redundant second walker is the cost the sockets guard
  explicitly warns against.
- No commit: the row's whole deliverable is the scan in `ComboCountCapGuardTests.cs`, committed with
  SSH6.5's row (one file, one Verify filter, one commit).

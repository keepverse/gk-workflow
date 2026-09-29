# Mega-merge QC 4 — item-2 (item test trees) on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites. No live game.

## Verdict: GREEN, no new findings

The `item-2` merges under QC are test-hygiene (ITEM-vacuous-1: item trees contain
no vacuous tests). QC re-ran every named tree on the merged head:

| Check | Command | Result |
|---|---|---|
| Core items | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests` (measured in QC 2) | 1470/1470 |
| Data items | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter FullyQualifiedName~Items` | 297/297 (2 m 18 s) |
| Server items | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter FullyQualifiedName~Item` | 204/204 |
| Corpus tool | `dotnet run --project gk-forge/tools/ItemSeedValidator` (measured in QC 1) | exit 1, 498 errors — unchanged, routed to items/seedsmith |

No merge-interaction red. The open item-todo rows are program work, out of QC scope.

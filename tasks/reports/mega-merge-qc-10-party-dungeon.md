# Mega-merge QC 10 — party-dungeon on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites incl. in-process E2E. No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Core Delve | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~Delve` | 1765/1765 |
| Data Delve | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter FullyQualifiedName~Delve` | 187/187 |
| E2E Delve/Dungeon | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "Delve\|Dungeon"` | 2/2 (thin — program's weight is in the Core/Data filters above) |

## Open rows noted, not QC failures

party-dungeon-todo: D4.17 open on row 5 only (curio rule → seedsmith pipeline, owner-ruled);
D4.30+ later waves are program work. No merge-interaction red.

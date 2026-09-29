# Mega-merge QC 8 — notification-ssot on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites (C# + web). No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Notify domain | `dotnet test gk-core/tests/FusionRpg.Core.Notify.Tests` | 41/41 |
| Notification endpoints | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter FullyQualifiedName~Notification` | 60/60 |
| Web notify rail + volume | `npx vitest run src/stages/world/notify src/ui/volumeMatrix.test.ts` | 22/22 (3 files) |

## Open rows noted, not QC failures

notification-ssot-todo: 63 done / 5 open — NS6.8 recipe + owner piece review (queue row confirmed,
review pending), NS6.11 React surface. Program work; no merge-interaction red.

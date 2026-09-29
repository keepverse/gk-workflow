# Mega-merge QC 12 — world-stage on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Focused suites (C# + web) incl. in-process E2E. No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Core World | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~World` | 1275/1275 |
| Web world | `npx vitest run playbackTable.test.ts adaptWorld.test.ts useLensData.test.tsx` | 36/36 |
| E2E turn fixture | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter WorldTurnFixtureTests` (QC 5) | 1/1 |

# Mega-merge QC 17 — Data + Server full suites (default profile) on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Default-profile full projects (`Category!=DiskSemantics&Category!=Heavy`, the AllDefault filter). No live game.

## Verdict: GREEN, no new findings

| Check | Command | Result |
|---|---|---|
| Data full | `dotnet test gk-core/tests/FusionRpg.Data.Tests` (default filter) | 1783/1783 (11 m 51 s) |
| Server full | `dotnet test gk-core/tests/FusionRpg.Server.Tests` (default filter) | 858/858 |

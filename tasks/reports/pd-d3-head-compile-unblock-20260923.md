# Evidence — the integration head's broken `Data.Tests` fixture (lane `pd-d3`, 2026-09-23)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the head really was broken for `FusionRpg.Data.Tests` | `dotnet build gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` (before the fix) | `error CS7036: There is no argument given that corresponds to the required parameter 'DangerBand' of 'ExpeditionTierNumbers.ExpeditionTierNumbers(int, int, int, int, int)'` at `ContractTuningTestBootstrap.cs:458-461`; then, after that one was supplied, the same class of error for `ExpeditionTuning`'s new required `Encounter` parameter | `gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs` |
| the fix compiles | `dotnet build gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj -v q --nologo` | `Build succeeded.` | — |
| the fixture's new values mirror the real published file | `gk-core/data/tuning/expeditions.v2.json` | tiers' `dangerBand` = 1/2/3/4; `encounter` = `{wildCreatureMetMilli: 250, quietMilli: 50}` — both copied, not invented | — |
| the path-owned verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Data.Tests/ContractTuningTestBootstrap.cs') -Session party-dungeon-d3"` | `EXIT=0`; `TEST-SHARDED OK: 4 shards, 1741 tests, no overlap` | — |

**Cause, read not inferred**

Commit `d5b1697a3` ("npc-story-events NR2.19: publish expeditions.v2.json and move every reader in one
commit") widened `ExpeditionTierNumbers` with a required `DangerBand` and `ExpeditionTuning` with a
required `Encounter`, but did not update this hand-built fixture, which is the only `ExpeditionTuning`
constructor call in `tests/`. The head therefore did not compile for `FusionRpg.Data.Tests` — every
Data-side verification in every lane was red on a compile error, not on a test.

**NOT proved**

- Not a party-dungeon defect: no file this program owns is involved. `tests/**` is inside this lane's
  fence, so the unblock was made here rather than left for a lane that cannot touch the file.
- Only the missing constructor arguments were supplied; the fixture's own `SchemaVersion: 1, Version: 1`
  was deliberately left alone (it is a hand-built default, not a read of the published file, and changing
  it could move other suites' assertions). If NR2.19 wants this fixture to track `v2`'s version, that is
  its call, not this lane's.
- The `verify-change.ps1` run above is the sharded whole-Data-suite boundary for this path; the full
  unfiltered suite remains CI-owned.
- A finding row for `npc-story-events` was NOT filed: that program's todo
  (`tasks/npc-story-events-todo.md`) is outside this lane's allowed paths, so this report is the record
  and the fix is committed here.

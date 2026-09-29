# SE4.2 — Migrate Core call sites, by meaning

Spec: docs/architecture/solid-enforcement/spec-commander-identity.md
(One commit with SE4.3: `gk-core/tests/FusionRpg.Core.Tests` references `FusionRpg.Data`, so the Core-only half cannot build or run its gate. Per-file meaning is in the commit body.)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every Core use typed `EmpireId` / `CommanderRef` by meaning | `dotnet build src\FusionRpg.Core -v q --nologo` | pass — the faction sites read `EmpireId`; `MatchCommanderSessionCache`/`CommanderResourcePools` read `CommanderRef`; `Commanders/`, `Battle/`, `Stats/Aptitudes/` migrated | diff (48 paths) |
| The four enum switches and the `TryParseStableId` string switch deleted (→ `TryResolve`); `CommanderIds.All` deleted | `dotnet build src\FusionRpg.Core -v q --nologo` | pass — the `CommanderIds` class is gone (`CommanderId.cs` emptied); display/scope-key/parse now come from `DataCommanderDirectory` | `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs` |
| The Core `== CommanderId.Dave` sites become `== EmpireId.Dave`; `SpeciesAllocation.cs:29` stays `EmpireId.Dave` for good | `dotnet build src\FusionRpg.Core -v q --nologo` | pass — `PlayerEmpireCommanders.IsPlayerDefaultAllowed` compares the empire, `SpeciesAllocation.ScopeKey`/`EmpireForSide` take `EmpireId` | diff |
| Core builds | `dotnet build src\FusionRpg.Core -v q --nologo` | pass — 0 errors | — |
| Verify | `.\scripts\verify-change.ps1 -Paths <the 49 changed paths> -Session summoner-convergence-lane-b-20260919` | ran; Core 14223/14224 — the one red is the **named pre-existing CRLF worktree artifact** `DungeonLootTableSeedFileTests.The_committed_file_matches_the_generator_byte_for_byte_no_hand_edits`. The remaining selected checks, run directly: core-focused 121/121, data 1547/1547, server 552/552, guard 395/397 (see SE4.3), 7 guards green | gate recorded with that named exception |

`World/**`, `Match/**`, `Creatures/**` carry no enum use: their `CommanderId` hits are `WorldCommand.CommanderId`, a string property.

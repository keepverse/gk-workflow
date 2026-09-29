# SE4.3 — Migrate Data, Server, Injector, Contracts

Spec: docs/architecture/solid-enforcement/spec-commander-identity.md
(One commit with SE4.2 — see its fragment.)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every remaining `src/` use migrated by meaning; `enum CommanderId` deleted; persisted strings unchanged | `dotnet build src\FusionRpg.Server -v q --nologo` | pass — Data (`RpgStore.{PlayerCommander,Items,Aptitudes,SpeciesRespec,WorldTurns,ZombossAdaptive}`), Server (`CommanderEndpoints`,`ItemEquipEndpoints`,`LoadoutEndpoints` comment), Injector (`CheatState`,`RpgClient`,`RpgHost`) migrated; `git grep "enum CommanderId" src/` finds none | diff |
| Persisted strings unchanged | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | pass — 1547/1547, incl. `PlayerCommanderStoreTests` pinning `"commander:dave"` and `"player:42"`/`"zomboss:42"` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.PlayerCommander.cs` |
| `/api/commanders/{id}` shows the player's name; the "player unknown" fallbacks use a neutral label, never a name | `dotnet test tests\FusionRpg.Server.Tests -v q --nologo` | pass — 552/552; `CommanderListEndpointsTests.List_fresh_save_...` asserts the row's display equals the save's player name; `MatchCommanderSessionCache` and `RpgClient` fall back to the registry's neutral label | `gk-core/src/FusionRpg.Server/CommanderEndpoints.cs` |
| `dotnet build src\FusionRpg.Server` | `dotnet build src\FusionRpg.Server -v q --nologo` | pass — 0 errors | — |
| `.\scripts\guard-injector-compile.ps1` | `.\scripts\guard-injector-compile.ps1` | **SKIPPED** — "no MelonLoader game dir (set FUSIONRPG_ML_GAMEDIR); injector NOT compiled". Injector sources (3 files) are therefore compile-unproven here; the orchestrator/owner has the game dir | — |
| `.\scripts\verify-change.ps1` | `.\scripts\verify-change.ps1 -Paths <the 49 changed paths> -Session summoner-convergence-lane-b-20260919` | Core red on the named pre-existing CRLF artifact (SE4.2); the rest run directly: 7 guards green (`actor-hub`, `dal`, `funnel-delta`, `secondary-no-unity`, `session-boundary`, `single-writer`, `test-substrate`), data 1547/1547, server 552/552, guard 395/397 | gate recorded with that named exception |

Guard.Tests' two reds: `SpeciesAllocationCacheTriggerTests.The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another`
(source-scan expects `CommanderId.Dave` in `CheatState.cs`; now `EmpireId.Dave`) — **BLOCKED**, that file is a protected pipeline file,
the one-word fix needs `--allow-protected`; and `StubRegisterTests.Every_row_points_at_a_file_that_exists` (SR-19 register stale,
pre-existing, also recorded by lane A).

## Finding — the spec's `DisplayName(CommanderRef, long playerId)` cannot be implemented without a store

SE4.1 shipped it with an injected `Func<long,string?>` name lookup. SE4.3 found that a process-global lookup binds the directory to a
store whose lifetime it does not own (a test store disposed under it made `/api/commanders` 500). The directory now takes the
caller's player name (`DisplayName(CommanderRef, string? playerName)`) — the same rule, with the caller, which already holds the
name, owning the read. Asking the manager to record this as an erratum against the spec's literal signature.

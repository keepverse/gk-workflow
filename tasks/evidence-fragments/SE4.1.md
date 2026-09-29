# SE4.1 — `EmpireId`, `CommanderRef`, `ICommanderDirectory` and the default-commanders registry

Spec: docs/architecture/solid-enforcement/spec-commander-identity.md

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Both value types exist, open, well-known values only (no "all empires" list) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander" -v q --nologo` | pass (97/97) | `gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs`, `CommanderRef.cs`; `ICommanderDirectory` has no enumeration method |
| `ICommanderDirectory` exposes `TryResolve`, `EmpireOf`, `DisplayName`, `AllocationScopeKey`, `DefaultFor` | (compile) `dotnet test …` builds Core + tests | pass | `gk-core/src/FusionRpg.Core/Commanders/ICommanderDirectory.cs` |
| Data-backed by the authored registry, two rows | `dotnet test … --filter "FullyQualifiedName~Commander"` | pass — `Shipped_registry_resolves_each_authored_stable_id`, `Default_for_resolves_each_shipped_empire` | `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` |
| Scope keys byte-identical to today: `player:{id}` / `zomboss:{id}` | `dotnet test … --filter "FullyQualifiedName~Commander"` | pass — `Shipped_registry_allocation_scope_keys_are_byte_identical_to_the_retired_helpers` asserts `player:42` / `zomboss:42` | test file |
| Display "Dr. Zomboss" for Zomboss; the player's own name for `commander:dave`; neutral label when the player is unknown | `dotnet test … --filter "FullyQualifiedName~Commander"` | pass — `Zomboss_displays_his_authored_name_not_a_players`, `The_players_own_commander_displays_the_players_name`, `An_unknown_player_falls_back_to_a_neutral_label_never_another_persons_name` | test file |
| Unknown stable id refused | `dotnet test … --filter "FullyQualifiedName~Commander"` | pass — `Unknown_stable_ids_are_refused` (7 cases), `An_unknown_commander_ref_throws_rather_than_returns_a_default` | test file |
| No callers moved yet (additive only) | `git status --porcelain` | 4 new Core files + 1 new registry + 1 new test file; no existing production file edited | diff |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Commanders/EmpireId.cs,gk-core/src/FusionRpg.Core/Commanders/CommanderRef.cs,gk-core/src/FusionRpg.Core/Commanders/ICommanderDirectory.cs,gk-core/src/FusionRpg.Core/Commanders/DataCommanderDirectory.cs,gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json,tests/FusionRpg.Core.Tests/Commanders/CommanderDirectoryTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session summoner-convergence-lane-b-20260919` | Core 14227/14228; the one failure is the **named pre-existing CRLF worktree artifact** `DungeonLootTableSeedFileTests.The_committed_file_matches_the_generator_byte_for_byte_no_hand_edits` (Expected `\r\n` from the CRLF checkout, Actual `\n` from the LF generator; SE4.1 touches no dungeon-loot file). `guard-verification-boundaries` ran green. | gate recorded with that named exception |

## Notes

- **Design decision (recorded in the ledger).** `DisplayName(CommanderRef, long playerId)` returns the
  player's own name for a row authored `displayFromPlayer: true`, through a `Func<long,string?>`
  player-name accessor injected at construction (Core cannot reach `players.name`; the host wires it in
  SE4.3). With no accessor the row's authored neutral name (`"Commander"`) is returned — never another
  person's name. The registry row order is the directory's order; `DefaultFor` returns the first row of
  that empire, so a third commander for `dave` (SE4.4's Open/Closed test) is legal.
- **Superseded by SE4.3:** the signature is now `DisplayName(CommanderRef, string? playerName)`. A
  process-global name accessor coupled the directory to a store lifetime it does not own (a disposed
  test store made `/api/commanders` 500); the caller, which already holds the name, supplies it and the
  directory keeps only the rule. Same ruled behaviour.
- **Boundary added.** `gk-data/packs/fusion/data/seed/commanders/**` had no owner in `gk-core/scripts/verification-boundaries.v1.json`
  (`VERIFICATION BOUNDARY MISSING`); added owner `commander-directory` (project `core`, level `module`).
- Process slip: the ledger `task --state started` line for SE4.1 was written after the first edit; from
  SE4.2 on, `started` is written before editing (the lane-A correction).

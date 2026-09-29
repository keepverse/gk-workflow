# Evidence — npc-story-events NR2.23 (`EnterRoomWithDraw`: move, mark and seen in one transaction)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch `cmdc/npc-story-events-2`.
Program `npc-story-events`; row `tasks/npc-story-events-todo.md` NR2.23; spec `spec-delve-live-rooms.md`.
Cross-program note: party-dungeon's `pd-d3` lane named this row as a dependency of its D4.14/D4.32 in
`1fc9d1fea` ("no party can stand in a room until NR2.23/NR2.24 do"), so this closes one link of that chain.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One call moves the party, marks the room with its drawn id and records each persisted scope | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~EnterRoomWithDraw"` | `Failed: 0, Passed: 5, Total: 5` (536 ms) — the party is at `r1c0`, the room is `Visited` with the drawn `event_id`, and `LoadPersistedEventSeen` returns the per-domain and once-per-player rows | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs` |
| A room with a stored `event_id` writes nothing and returns it | same run (`A_room_with_a_stored_event_id_writes_nothing_and_returns_it`) | pass — the second entry returns `event.already-drawn` + the STORED id; the party is still in `r0c0`, the room's id is unchanged, and neither new scope was written | same |
| A fault injected after the mark leaves neither the move, the mark nor a seen row | same run (`A_fault_after_the_mark_leaves_neither_the_move_the_mark_nor_a_seen_row`) | pass — `EnterRoomMidTestHook` throws after `MarkRoomUnlocked`; afterwards the party is back in `r0c0`, `r1c0` is not `Visited` and carries no `event_id`, and both seen sets are EMPTY (one transaction, rolled back) | `gk-core/tests/FusionRpg.Data.Tests/Delve/EnterRoomWithDrawTests.cs` |
| A refused move enters nothing | same run (`A_refused_move_enters_nothing`, `An_entry_with_no_draw_is_refused_by_the_signature…`) | pass — `lane.unknown` for a non-adjacent target, `ArgumentException` for a blank draw; in both cases nothing was written | same |
| The extraction is behaviour-preserving for the existing writers | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~Delve"` | `Failed: 0, Passed: 187, Total: 187` (41 s) — includes `DelveScopeTests`' own `MoveParty` and gate tests and the event-seen round-trips | — |
| Path-owned verification (the row's own line, renamed for the session reason) | `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs','gk-core/tests/FusionRpg.Data.Tests/Delve/EnterRoomWithDrawTests.cs') -AllowUnscoped` | exit 0 — plan `data-fallback` + `data-tests-fallback` (module) with guards `dal`, `test-substrate`; printed `shard a: exit 0, 459 tests` / `shard b: 41` / `shard c: 83` / `shard rest: 1163` and `TEST-SHARDED OK: 4 shards, 1746 tests, no overlap` | — |
| The DAL guard the row names | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data` (also run inside the verify-change plan above) | — |
| Test substrate | inside the same verify-change run | `TEST SUBSTRATE GUARD OK — no new swallowed deletes, temp-backed or untagged file-backed stores` | — |

**Design notes.**

- **The dependency's own escape hatch was taken, and that is what the row allows:** "NR2.11 (or the
  pre-migration store; the signatures are unchanged)". `rpg_delve_event_seen` already exists and
  `RecordEventSeen`/`LoadPersistedEventSeen` are unchanged, so the composed call writes the same scopes the
  reader reads back — `per-domain` (keyed by the domain id) and `once-per-player`. `PerDelveSeen` is the
  room's own `event_id` (the spec's literal definition, no second table) and `RecentCells` is not a table
  concern; neither is written here, and the class doc says so.
- **One writer per column, two callers.** `MoveParty` and `RecordEventSeen` keep their public signatures and
  now delegate to `MovePartyUnlocked`/`RecordEventSeenUnlocked`, which the composed entry calls inside its own
  transaction — so there is no second SQL text for either write. `MarkRoom` keeps its wider column set
  (`cleared`/`resolved_kind`/`resolved_archetype_id`); the entry uses a focused `MarkRoomUnlocked` that writes
  only `visited`/`event_id`, which is all an entry marks.
- **The fault seam is the repo's own idiom** (`FusionMidTestHook`, `SummonMidPullTestHook`): an
  `internal Action? EnterRoomMidTestHook`, reachable from the test assembly through the existing
  `InternalsVisibleTo`.

**NOT proved / named deviations.**

- The row's Verify line is run renamed: `-Session <sid>` cannot resolve in this lane (no session record;
  `tasks/sessions/**` is outside its allowed paths), so it passes `-AllowUnscoped`.
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs` resolves to `data-fallback` (module) rather than NR0.2's
  focused `data-delve-live` row, because that row's glob covers `DungeonDomainImportRunner.cs` and not this
  file; the fallback ran the whole Data project, which is strictly broader than the row needs.
- No route, no server, and no narrative engine is touched by this row: the HTTP entry is NR2.24, which also
  needs NR2.2 (deferred) and NR2.22. Nothing was started, so no live probe was run.

# Evidence — party-dungeon blocker register: PD-B1, D4.14, D4.13 + new row D4.32 (lane `pd-d3`, 2026-09-23)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| PD-B1's Fix line is stale — the wire is another module's | `grep -rn "CreateDelve(" src tests --include=*.cs` | definition `RpgStore.Delve.cs:164` + test callers only; **no Server file calls it** | `tasks/party-dungeon-todo.md` (PD-B1 note) |
| D4.14's missing `Kills` slice has no producer at all | `grep -rn "DelveReportKill" src --include=*.cs` | only the record's own declaration (`Delve/Report/DelveReport.cs:11,42`) | D4.14 note |
| D4.14's other five slices have sources | `grep -rn "RecordClear\|MarkRoom\|WriteQuestVerdicts" gk-core/src/FusionRpg.Data` | `RecordClear` `:1531`, `MarkRoom` `:379`, `WriteQuestVerdicts` `:550`, `SettleExtractionUnlocked` called `:777` | D4.14 note |
| D4.13's remaining half is a named dependency row | read `QuestCoverage.cs` + `spec-delve-quests.md` §Testing | needs the Phase-5 run loop; the pure `WithinRegressionBand` piece is built | D4.13 note |
| D4.32's premise: the routes are retained but unsliced | `grep -n "Not transferred" -A1`; `grep -c "DelveEndpoints.cs\` has no close/extraction/room-clear route at all"` | transfer note retains "the extraction and room-clear routes"; the D3.16 note exists; **no `[ ]` row names them** | new row D4.32 |

**What this commit is**

Not code: it makes four rows' blockers exact, which is the deliverable the manager asked for ("a row that
ends the segment still open must name EXACTLY what blocks it"). Three of the four are edits to existing
rows; the fourth is a **new row (D4.32)** because the gap it describes had no row at all — the transfer
note explicitly retains the extraction and room-clear routes here while D3.11/D3.15/D3.16 (all `[x]`)
carry that same gap only as a note inside a closed row.

**NOT proved**

- No code was written and no test was run for this commit: every claim is a read of the tree, quoted with
  its `file:line` in the rows themselves.
- D4.32's own acceptance is unproven by construction (the routes do not exist). Its blocker is an **owner
  ruling** — which module owns the live room path — because the transfer note retains the routes here
  while `npc-story-events`' `delve-live-rooms` is specified as owning the production callers of
  `MarkRoom`/`RecordEventSeen` on the same path.
- The `hungerExhaustedStatusId` parameter `QuestProgress.Evaluate` takes still has no source anywhere;
  named in D4.14's note as a second, smaller gap rather than resolved.

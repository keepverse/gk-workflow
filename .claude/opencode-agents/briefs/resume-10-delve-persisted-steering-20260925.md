# D2.16a — implement the owner-ruled persisted steering record

The owner ruled on 2026-09-25: replace the temporary selector-zero fail-closed policy with a
**persisted steering record**. The accepted P1 report intentionally left this as an owner question;
the ruling is now durable and this lane owns the scoped implementation.

## Read first

- `AGENTS.md` and `docs/DESIGN-GATE.md` (anything/data/battle/live rows)
- `docs/architecture/party-dungeon/spec-delve-battle-profile.md` §3–4b
- `docs/architecture/party-dungeon/spec-delve-scope.md` (delve header/decision log)
- `docs/architecture/party-dungeon/spec-wild-room.md` (pre-room admission)
- `docs/architecture/data-architecture.md` (DAL boundary)
- current `tasks/party-dungeon-todo.md` D2.16/D2.16a and accepted P1 report/artifact

## Allowed paths

- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Server/RpgHub.cs`
- `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` only if an existing reset/migration list must change
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/**`
- focused Core tests only if an existing pure steering type is proven necessary
- `tasks/reports/resume-10-delve-persisted-steering-20260925.md`

No Contracts, web, generated/data, tuning, CI, `RpgHub.Resume`/CAI3.5 automated-policy implementation,
economy redesign, or unrelated Delve paths. If a shared wire DTO or a new schema primitive is required,
stop and report the exact need instead of widening the fence.

## Required behavior

1. The server owns one canonical durable steering record for each active Delve. `RpgHub.Steer` may
   request a change, but the Data-owned persisted value is authoritative after reconnect, process
   restart, and a new store handle. Do not trust `DelveWildJoinRequest.PartyEntityId` as proof.
2. Validate the requested party against the persisted raid mode's configured party count and the
   player-owned persisted warband/location. Missing, stale, closed, or invalid records refuse by a
   named reason; no default-to-zero and no always-true predicate.
3. The wild/cage precheck and the Data write transaction read the same persisted authority. The
   existing `steer{from,to}` decision-log/freeze semantics remain intact; do not create a second
   in-memory session map.
4. If a schema change is required, migration/reader/writer land in the same commit and an old-schema
   fixture proves the upgrade. Prefer an existing Data-owned record shape when it satisfies the
   contract; explain the choice in the report.
5. Add focused tests for persisted selector 0 and a nonzero configured party, invalid/stale/closed
   refusals, reconnect/new-handle read-back, no write on refusal, and unchanged decision-log ordering.
   Do not claim `RpgHub.Resume` or live multi-party battle completion; CAI3.5 remains open.

## Verification/report

Run restored focused Server/Data/Core tests, DAL/test-substrate/ActorHub guards, and path-owned
`verify-change -PlanOnly` for every executable path. If the full selected owner run is too costly,
record the exact bounded result and focused replacement. Write a disk-backed report with source
reasoning, changed files, commands/results, migration evidence, open owner questions, and next steps.
Leave the tree dirty for manager review; no commit/push/merge.

Use only OpenCode CLI `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent,
and no external-directory reads.

# Manager acceptance review — D2.16a persisted Delve steering

Review the dirty output of `resume-10-delve-persisted-steering-20260925` at a clean exact SHA. Accept
only the owner-ruled persisted steering record and its Server/Data read/write/transaction tests.
Do not broaden into `RpgHub.Resume`, CAI3.5, live proof, or a new wire DTO.

## Allowed paths

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
- `gk-core/src/FusionRpg.Server/RpgHub.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveSteeringRecordTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs`
- `tasks/reports/resume-10-delve-persisted-steering-20260925.md`
- `tasks/reports/resume-16-delve-persisted-steering-acceptance-20260925.md`

No Contracts, web, generated data, tuning, CI, unrelated Delve code, or live game paths.

## Acceptance boundary

1. Verify the Data-owned `steering_json` distinguishes present selector zero, explicit JSON null,
   and SQL NULL/legacy missing; malformed/out-of-range/stale/closed/ownership/location/raid-mode
   refusals do not mutate steering, revision, or decisions.
2. Verify the HTTP precheck and transaction authority use the same persisted record, and a failed
   persistence prevents freeze/decision/notification side effects.
3. Verify reconnect/new store-handle read-back through the focused tests; do not fabricate live
   multi-party evidence.
4. Run focused Data/Server tests, DAL/test-substrate/ActorHub guards, path-owned PlanOnly, and the
   boundary check. Run the same focused checks from a clean detached checkout at the reviewed SHA.
5. Write a schema-v2 acceptance artifact with exact reviewed SHA, clean-checkout log hash, changed
   paths, known limitations, and merge SHA. Commit/merge only through the manager.

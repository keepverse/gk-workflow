# Manager acceptance review — D2.16a persisted Delve steering

**Reviewed lane:** `resume-10-delve-persisted-steering-20260925`

**Verdict:** GREEN for the owner-ruled persisted steering record and the existing Server/Data
transaction seam. Live multi-party proof, the full aggregate, and CAI3.5 remain explicitly open.

## Review findings

The implementation keeps one durable authority in the nullable `rpg_delves.steering_json` column.
A present `partyIndex: 0` is distinct from present JSON `null` (deliberate steer-to-none), and SQL
`NULL` is the named legacy `delve.steering.missing` state. New delves write selector zero explicitly;
old rows are not silently backfilled.

`TrySetDelveSteering` validates the current record, optimistic `from` value, raid party bound,
player-owned Warband, persisted location, and closed state before its compare-and-set update. A
refused mutation returns before revision, steering JSON, or decision-log changes. The HTTP wild/cage/
altar precheck and the Data transaction both use `ValidateSteeringUnlocked`; the precheck is not the
authority. `DelveBattleSessionManager.TrySteer` persists first, then performs the existing freeze or
decision-log side effect. A disconnect freeze intentionally does not erase the durable selection.
No new wire DTO, subsystem, generated data, tuning, CI, or unrelated Delve path was introduced.

The existing SignalR player-routing precondition remains: a web connection normally calls
`JoinPlayer` before invoking `Steer`; this review did not broaden that established routing contract.
The manager/Data tests use the direct bounded seam where no Hub connection exists.

## Independent checks

Run from the review worktree with the copied dirty output:

```text
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~DelveSteeringRecordTests" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~DelveWildTransactionTests" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveWildEndpointsTests" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveBattleSessionManagerTests" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Delve" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelvePricesTests" --no-restore
# exit 0

scripts/guard-dal.ps1
# DAL GUARD OK; exit 0

gk-core/scripts/guard-test-substrate.py
# TEST SUBSTRATE GUARD OK; exit 0

scripts/guard-actor-hub.ps1
# ACTOR-HUB GUARD OK; exit 0

scripts/verify-change.ps1 -Paths <eight concrete code/test paths>
  -Session resume-10-delve-persisted-steering-20260925 -PlanOnly -Format json
# exit 0; Data/Server module owners and applicable DAL/test-substrate/ActorHub seams selected

 git diff --check
# exit 0
```

The worker report records the same focused counts: Data Delve 199/199, Server Delve 63/63, new
steering record tests 9/9, wild transaction tests 18/18, wild endpoint tests 18/18, battle-manager
tests 18/18, and DelvePricesTests 22/22. The independent run's external log SHA-256 is
`3F4CF88C2E42AC016B296906F390E2F3E49A42DCF84A92C3C569BE21AC67D1D4`.

The first attempt to invoke the path-owned planner with the new acceptance session failed because
that manager control record had not yet been copied into this isolated review worktree; it was an
acceptance-harness setup error, not a product/test failure. The planner was rerun with the worker
session record and passed. The manager session record is committed separately before the merge.

## Open boundaries

- No live game, browser, or multi-party battle proof is claimed. Reconnect/new-handle read-back is
  proven in the real Data/Server tests, not by a running client.
- The full unfiltered path-owned aggregate remains CI/nightly/release-owned; PlanOnly is the correct
  local boundary.
- `RpgHub.Resume` and CAI3.5 automated-policy wiring remain outside this change.
- The worker process was stopped after its report and dirty tree were preserved; no product edits
  were discarded.

## Exact-SHA steps remaining

1. Commit the reviewed code/tests/report set at an exact SHA.
2. Run the same focused checks from a clean detached checkout and record its log hash/status.
3. Write the schema-v2 acceptance artifact with reviewed and merged SHAs.
4. Merge only the exact reviewed SHA and mark the worker/acceptance sessions reconciled.

<<<REPORT {"status":"done","summary":"Accepted the D2.16a persisted Delve steering repair: one nullable Data-owned steering record distinguishes selector zero, explicit none, and legacy missing; Data transactions and HTTP prechecks share the authority; manager steering persists before freeze/log side effects; focused Data/Server/Core tests, guards, PlanOnly, and diff checks passed. Live proof, full aggregate, RpgHub.Resume, and CAI3.5 remain open.","changed_files":["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs","gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs","gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs","gk-core/src/FusionRpg.Server/RpgHub.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveSteeringRecordTests.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs","gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs","gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs","tasks/reports/resume-10-delve-persisted-steering-20260925.md","tasks/reports/resume-16-delve-persisted-steering-acceptance-20260925.md"],"verification":["Data/Server/Core focused test commands all exit 0","worker counts: Data Delve 199, Server Delve 63, steering records 9, wild transactions 18, wild endpoints 18, battle manager 18, DelvePrices 22","DAL, test-substrate, ActorHub guards exit 0","path-owned PlanOnly exit 0","git diff --check exit 0","independent log SHA-256 3F4CF88C2E42AC016B296906F390E2F3E49A42DCF84A92C3C569BE21AC67D1D4"],"open_issues":["exact-SHA clean checkout and acceptance artifact remain","no live multi-party proof","full aggregate remains CI/nightly/release-owned","RpgHub.Resume/CAI3.5 remains open"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification","merge exact SHA and record schema-v2 artifact"]} REPORT>>>

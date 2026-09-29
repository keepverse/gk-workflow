# D2.16a implementation / verification report — persisted Delve steering

**Session:** `resume-10-delve-persisted-steering-20260925`
**Worktree:** `opencode-resume-10-delve-persisted-steering-20260925`
**Status:** **PARTIAL for manager acceptance** — the scoped implementation and focused evidence are green; the tree is intentionally uncommitted and no live/multi-party battle proof is claimed.

## Scope and fence

Implemented only in the allowed Server/Data/test/report surface:

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
- `gk-core/src/FusionRpg.Server/RpgHub.cs`
- the listed Data/Server tests
- this report

No Contracts, web, generated data, tuning, CI, economy redesign, unrelated Delve path, `RpgHub.Resume`, or CAI3.5 implementation was changed. No commit, push, or merge was made.

## Design choice

The canonical record is one nullable `rpg_delves.steering_json` header value, represented in Data as `DelveSteeringRecord(int? PartyIndex)`:

- A present object with `partyIndex: 0` is the explicit selector-zero state.
- A present object with `partyIndex: null` is an explicit steer-to-none state and is not read back as zero.
- SQL `NULL` is reserved for a row created before this record existed. It is reported as `delve.steering.missing`; it is never silently defaulted to zero.

This additive column was preferred over putting a singular selector into `parties_json` (mutable per-party state) or deriving current state from `decisions_json` (append-only history). It stays inside the Data schema/fence; no shared wire DTO, second table, or second in-memory steering map was added. The existing `EnsureColumn` migration path is sufficient because this is an additive column on `rpg_delves`, so `RpgStore.cs` did not need a reset-list change.

## Implementation

### Data authority and refusal behavior

`RpgStore.Delve.cs` now provides:

- `ReadDelveSteering` for durable read-back and malformed/out-of-range refusal.
- `ValidateDelveSteering` for the side-effect-free HTTP precheck.
- `TrySetDelveSteering` for the authoritative mutation.

Mutation validation checks the persisted raid mode and configured party count, the persisted player-owned `Warband`, and its persisted location. The requested `from` selector is an optimistic concurrency check; a null source is valid only when the persisted current value is also explicitly null. The update uses a compare-and-set predicate on the previously read `steering_json`, so a stale writer cannot overwrite a newer selection.

Named refusals include:

- `delve.steering.missing`
- `delve.steering.invalid`
- `delve.steering.stale`
- `delve.steering.closed`
- `delve.steering.party-invalid`
- `delve.steering.party-not-owned`
- `delve.steering.party-location`
- `delve.steering.raid-mode`
- `delve.steering.not-owned`
- `wild.party-not-steered` for a valid but non-selected party

Refused reads and mutations return before the write. `TalkJoin` and `PullAtAltar` repeat the same persisted steering/world validation inside their write transactions; the HTTP precheck is not the authority.

### Server seam

`DelveWildEndpoints.ValidateRoom` reads the Data-owned record for `/talk`, `/cage`, and `/pray`. The request's `PartyEntityId` is only the requested selector, never proof of ownership or steering. The existing route/cage, room, player, and transaction behavior remains in place.

`DelveBattleSessionManager.TrySteer` persists the Data record first, then preserves the existing explicit `steer{from,to}` decision-log and fight-freeze side effect. A failed persistence/refusal performs no freeze, decision append, or notification. `RpgHub.Steer` calls this path and retains the existing SignalR signature; no new wire response DTO was introduced.

A transient disconnect still performs the existing freeze/log behavior, but deliberately does not erase the durable selection. Reconnect, process restart, and a new store handle therefore read the same persisted party back. The existing connection/session tracking is not used as a second steering authority.

## Migration and persistence evidence

- `CreateDelve` writes selector zero explicitly.
- An old-schema fixture creates `rpg_delves` without `steering_json`; initialization adds the column through `EnsureColumn`.
- The upgraded old row reads as `delve.steering.missing`, and a steering mutation against it refuses without backfill or overwrite.
- A pair-mode delve with parties `0` and `1` persists selector `1`; a reopened store handle reads `1` back.
- Explicit steer-to-none persists a JSON null and is distinct from both zero and missing.
- Malformed JSON, out-of-range party, stale source, closed Delve, wrong location, and non-selected party cases are covered without changing revision, steering JSON, or decision log.

## Verification evidence

All commands below were run in the worktree. Counts are from the recorded command output.

```text
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~DelveSteeringRecordTests" --no-restore --logger "console;verbosity=minimal"
# Passed: 9, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~DelveWildTransactionTests" --no-restore --logger "console;verbosity=minimal"
# Passed: 18, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveWildEndpointsTests" --no-restore --logger "console;verbosity=minimal"
# Passed: 18, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveBattleSessionManagerTests" --no-restore --logger "console;verbosity=minimal"
# Passed: 19, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve" --no-restore --logger "console;verbosity=minimal"
# Passed: 199, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Delve" --no-restore --logger "console;verbosity=minimal"
# Passed: 64, Failed: 0, Skipped: 0; exit 0

dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelvePricesTests" --logger "console;verbosity=minimal"
# Passed: 22, Failed: 0, Skipped: 0; exit 0
```

```text
.\scripts\guard-dal.ps1
# DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data

python gk-core/scripts/guard-test-substrate.py
# TEST SUBSTRATE GUARD OK — exit 0

.\scripts\guard-actor-hub.ps1
# ACTOR-HUB GUARD OK — exit 0

git diff --check
# exit 0
```

The final path-owned planner invocation was:

```powershell
$paths = @(
  'gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs',
  'gk-core/src/FusionRpg.Server/RpgHub.cs',
  'gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs',
  'gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs',
  'gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs',
  'gk-core/tests/FusionRpg.Data.Tests/Delve/DelveSteeringRecordTests.cs'
)
.\scripts\verify-change.ps1 -Paths $paths -Session resume-10-delve-persisted-steering-20260925 -PlanOnly -Format json
```

It exited `0`, selected the Data/Server module owners and applicable DAL/test-substrate/ActorHub checks, and reported `fullEvidenceOwner: CI/nightly/release`. The non-PlanOnly aggregate was not run in this session, so no aggregate verdict is claimed; the focused replacements above are the bounded local evidence.

The session boundary check also passed:

```text
python scripts/session-boundary-check.py --session resume-10-delve-persisted-steering-20260925
# clean for the active session; exit 0
```

## Explicit non-claims and remaining manager work

1. The tree is intentionally dirty. There is no commit SHA, clean-checkout artifact, push, or merge in this report.
2. No live game/server/browser proof was run. This report does not claim live multi-party steering or a live battle outcome.
3. CAI3.5 / `RpgHub.Resume` automated-policy wiring remains open and untouched.
4. The full unfiltered path-owned aggregate remains CI/nightly/release-owned; only the recorded focused tests and PlanOnly are claimed here.
5. Manager review should inspect the additive nullable-column choice and the explicit-null disconnect semantics before any exact-SHA acceptance or merge.

## Changed files

- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
- `gk-core/src/FusionRpg.Server/RpgHub.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveSteeringRecordTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs`
- `tasks/reports/resume-10-delve-persisted-steering-20260925.md`

<<<REPORT {"status":"partial","summary":"D2.16a persisted Delve steering is implemented inside the Server/Data fence. A nullable Data-owned steering_json record distinguishes selector zero, explicit none, and missing legacy state; mutations validate configured party count, player-owned Warband/location, stale source, closed state, and malformed/out-of-range records without writes. HTTP wild/cage/altar prechecks and Data write transactions use the same authority, while RpgHub.Steer preserves the existing steer freeze/decision-log ordering. Focused Data, Server, Core, guard, PlanOnly, and session-boundary evidence is green. The tree remains intentionally uncommitted; no live proof, full aggregate verdict, or CAI3.5 completion is claimed.","changed_files":["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs","gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs","gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs","gk-core/src/FusionRpg.Server/RpgHub.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveSteeringRecordTests.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs","gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs","gk-core/tests/FusionRpg.Server.Tests/DelveBattleSessionManagerTests.cs","tasks/reports/resume-10-delve-persisted-steering-20260925.md"],"verification":["9 DelveSteeringRecordTests passed","18 DelveWildTransactionTests passed","18 DelveWildEndpointsTests passed","19 DelveBattleSessionManagerTests passed","199 Delve Data tests passed","64 Delve Server tests passed","22 DelvePricesTests passed","guard-dal passed","guard-test-substrate passed","guard-actor-hub passed","git diff --check passed","path-owned verify-change -PlanOnly passed with CI/nightly/release fullEvidenceOwner","session-boundary-check passed"],"open_issues":["no exact-SHA clean-checkout acceptance because the brief requires leaving the tree uncommitted","no live game/server/browser proof","no full non-PlanOnly aggregate verdict","CAI3.5 and RpgHub.Resume remain outside this session"],"next_steps":["manager review the additive nullable steering_json choice and explicit-none disconnect semantics","run exact-SHA clean-checkout acceptance if the manager chooses to commit","run live multi-party proof at the appropriate live gate","keep CAI3.5 and economy/schema follow-ups in their owning ledgers"]} REPORT>>>

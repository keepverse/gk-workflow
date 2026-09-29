# Resume P1 04 final — expedition durable result and identity closure

The first expedition lane was stopped before edits because its original fence overlapped the web recovery lane on `gk-core/src/FusionRpg.Contracts/**`. This successor owns only expedition server/data/tests. Do not edit any shared Contracts file; if a durable result response truly requires a shared DTO, stop at a named manager blocker rather than crossing the fence.

## Allowed paths

- `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`
- `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/ExpeditionRewardApplyTests.cs`
- `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs`
- `tasks/reports/resume-04-expedition-durability-final-20260925.md`

## Requirements

1. Persist a schema-safe collect result manifest/replay response or equivalent durable result contract; a retry after post-commit reconnect must return the same result without duplicate rewards.
2. Enforce active membership uniqueness at the database boundary, not only with an instance-local gate; cover independent handles/process topology where the store contract permits it.
3. Reject archived save IDs at the expedition entry boundary with a deliberate 4xx/contract response, before service/store work.
4. Add deterministic post-commit fault, concurrent collect, multi-handle dispatch, archived-ID, and replay tests. Keep the normal single-store loop green.
5. Do not invent a second reward engine or alter expedition balance without a separate ruling.

## Evidence/report contract

Use real routes and normal read-back. Report full SHA, changed files, exact commands/results, database/test substrate used, untested live behavior, open questions, and next plan. Leave dirty for manager review; no commit/push/merge. Use restored focused tests (a clean `--no-restore` run that executes zero tests is not evidence) and path-owned verification for every concrete path. No subagent or alternate model.

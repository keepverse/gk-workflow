# Resume P1 04 — expedition durable result and identity closure

## Goal

Close the confirmed expedition P1/P2s: a committed collect must be replayable after reconnect, active membership must be database-enforced, archived saves must be refused at the route boundary, and the tests must exercise crash/concurrency windows.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/architecture/data-architecture.md`
- `docs/architecture/standalone/spec-expeditions.md`
- `docs/architecture/unique-actor-runtime.md`
- `docs/contributing/testing-standard.md`
- the current expedition endpoint/service/store/schema and focused tests

## Allowed paths

- `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`
- `gk-core/src/FusionRpg.Contracts/**`
- `gk-core/tests/FusionRpg.Data.Tests/ExpeditionStoreTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/ExpeditionRewardApplyTests.cs`
- `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs`

## Requirements

1. Persist a schema-safe collect result manifest/replay response or equivalent durable result contract; a retry after post-commit reconnect must return the same result without duplicate rewards.
2. Enforce active membership uniqueness at the database boundary, not only with an instance-local gate; cover independent handles/process topology where the store contract permits it.
3. Reject archived save IDs at the expedition entry boundary with a deliberate 4xx/contract response, before service/store work.
4. Add deterministic post-commit fault, concurrent collect, multi-handle dispatch, archived-ID, and replay tests. Keep the normal single-store loop green.
5. Do not invent a second reward engine or alter expedition balance without a separate ruling.

## Evidence/report contract

Use real routes and normal read-back. Report full SHA, changed files, exact commands/results, database/test substrate used, untested live behavior, open questions, and next plan. Leave dirty for manager review.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Data.Tests --no-restore --filter "FullyQualifiedName~ExpeditionStoreTests|FullyQualifiedName~ExpeditionRewardApplyTests"`
- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --no-restore --filter "FullyQualifiedName~ExpeditionE2ETests"`
- `git status --porcelain`
- `git rev-parse --short HEAD`

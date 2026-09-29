# Resume P1 01 — server-owned Delve join outcome and price

## Goal

Close the confirmed Delve P1: the public wild/cage join routes must derive candidate, party eligibility, and altar price from server-owned persisted/tuning facts. Caller fields may be validated or ignored, never substituted.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/architecture/party-dungeon/spec-wild-room.md`
- `docs/architecture/party-dungeon-map.md`
- `docs/architecture/data-architecture.md`
- `docs/architecture/decisions.md`
- the current endpoint, store, price policy, and focused tests

## Allowed paths

- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`

## Requirements

1. Resolve room kind, cage state, candidate species, party ownership, and `OfferFloor` on the server from persisted/tuning facts.
2. Reject or ignore caller-supplied species/price substitutions; never mint a roster row from untrusted candidate data.
3. Make party-steered semantics explicit and test the chosen owner ruling; do not preserve an always-true placeholder by accident.
4. Add black-box/focused tests for wrong room kind, wrong candidate, wrong party, `Price = 1`, and successful server-resolved joins. Assert unchanged balances/roster on refusal.
5. Do not broaden the task into a Delve economy redesign or unrelated endpoint cleanup.

## Evidence/report contract

Use current code, not stale QC. Report the full SHA, changed files, exact commands/results, tests executed, untested live behavior, open questions, and next plan. Leave the tree dirty for manager review; no direct commit/push/merge.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Server.Tests --no-restore --filter "FullyQualifiedName~DelveWildEndpointsTests"`
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~DelvePricesTests"`
- `git status --porcelain`
- `git rev-parse --short HEAD`

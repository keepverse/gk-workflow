# P1 01 recovery — review the failed Delve owner draft

The original Delve worker left a six-file dirty draft but failed during unrelated external-directory/process-lock investigation and produced no report. This recovery lane receives that draft as read-only input copied into its own worktree. Do not reset, checkout, or discard it. Review the actual diff, finish only the server-owned Delve candidate/party/price contract, and produce a disk-backed report.

## Allowed paths

- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`
- `tasks/reports/resume-01-delve-owner-recovery-20260925.md`

No Contracts, web, generated/data, tuning, or unrelated paths. No commit, push, or merge.

## Requirements

1. Verify room kind, cage state, candidate species, party ownership, and altar `OfferFloor` are resolved from server-owned persisted/tuning facts. Caller fields may be rejected or ignored, never substituted.
2. Make party semantics explicit; surface any unresolved owner ruling instead of preserving an always-true placeholder by accident.
3. Retain focused black-box tests for wrong room/candidate/party, `Price = 1`, successful joins, and unchanged balances/roster on refusal.
4. Do not broaden into economy redesign.

## Verification/recovery rules

- Use OpenCode CLI `opencode/space-bunny-free#max`, no fallback, no subagent, no external-directory reads, and no process-lock hunting.
- Run restored focused tests one project at a time; a clean `--no-restore` command that executes zero tests is not evidence. If a test/build lock occurs, record the exact bounded failure and continue with the other project; do not inspect `C:\Users` or kill unrelated processes.
- Use `verify-change.ps1` with every concrete executable path if it completes within the selected boundary; do not substitute a broad suite.
- Leave the tree dirty and write the report with full changed paths, exact commands/results, source reasoning, open owner questions, and next steps.

<<<REPORT {"status":"done|partial|blocked","summary":"...","changed_files":["..."],"verification":["..."],"open_issues":["..."],"next_steps":["..."]} REPORT>>>

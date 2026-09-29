# ST4.5b — per-rung `aboveP90` action ids in the calibration report

**Status: done.** Manager's ask: *"the report must let ST5.2 list the actions above each rung's p90 by id
(spec contract 6: 'the change description lists the actions above the report's p90'). Add per-rung
aboveP90 ids to BudgetCalibration + the endpoint (read-only, same helper, contract test, no count pins)."*

## What changed

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Actions/Rungs/BudgetCalibration.cs` | `RungCalibration` gains `ActionsAboveP90`; `Read` computes it from the ids whose implied scalar is **strictly above** the p90 that same row publishes |
| `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` | `aboveP90 = r.ActionsAboveP90` on each rung of `GET /api/debug/action-budget-report` |
| `gk-core/tests/FusionRpg.Core.Tests/Actions/Rungs/BudgetCalibrationTests.cs` | 4 tests (strictness, the property, the all-equal case, the fewer-than-ten case) |
| `gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs` | the endpoint's `aboveP90` per rung, each named id checked against the store's own priced rung |

Read-only and the same helper: the list is derived inside `BudgetCalibration.Read` from the same
`entries`/`p90` the row publishes, so the list and the percentile cannot disagree about where the line
is — the discipline `ActionsAboveLoadedScalar` already applies. Nothing new is priced.

**Strictly above, deliberately.** Contract 6 says "the actions above the report's p90". The p90 is
nearest-rank, so on a rung with fewer than ten priced actions `ceil(0.9n) = n`, p90 IS the max, and the
list is empty by construction — there is no tenth action to be above it, and the largest reading is
already published as `max`. That consequence is a recorded property (`A_rung_with_fewer_than_ten_...`)
rather than a surprise in the live reading. On the real corpus the field is non-empty on rung 7 (n=10):
its p90 is the ninth of ten, so the one action above it — the max-setter that drives
`recommendedReferencePower` — is named.

## Evidence

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~BudgetCalibration"` | **Passed — Failed 0, Passed 12, Total 12** (8 pre-existing + 4 new) |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release --verbosity minimal --filter "FullyQualifiedName~ActionBudgetReport"` | **Passed — Failed 0, Passed 1, Total 1** |
| `.\scripts\verify-change.ps1 -Paths <the four paths above> -Session summoner-convergence-impl-20260918` | guards DAL + test-substrate **OK**; core module **14192/14193**; e2e/server steps not reached (the script exits on the first non-zero) |
| `[System.IO.File]::ReadAllBytes(...)` on `gk-data/packs/fusion/data/seed/loot/tables-dungeon.json`, main tree vs this worktree | main **1230 CR bytes**, worktree **0 CR bytes** |

The one Core failure is `DungeonLootTableSeedFileTests.The_committed_file_matches_the_generator_byte_for_byte_no_hand_edits`,
the CRLF worktree artifact the ledger already names for ST1.1 and AE1.2 — and the cause is now **measured,
not assumed**: the same tracked file is CRLF in the main checkout (1230 CR bytes) and LF in this worktree
(0 CR bytes), while `DungeonLootTableGen.ToJson` emits CRLF, so the byte-exact comparison can only fail
here. The test's own message shows exactly that (`Expected "{\r\n…" / Actual "{\n…"`). This change touches
nothing in the loot pipeline. Gate recorded with that named exception, as ST1.1/AE1.2 did.

## Not in this change

- `spec-budget-calibration-report.md` contract 2's field list does not yet name `ActionsAboveP90`. That
  file (`docs/architecture/action-skill-tiers/`) is **outside this session's `paths` fence**, so the spec
  amendment is a manager action, not an unattended edit.
- Contract 6's *other* half — "the change description lists the actions above the report's p90" in the
  v4 publish — is ST5.2's commit, and it waits on the reading ST4.5 produces.

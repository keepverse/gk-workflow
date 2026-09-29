# ST4.3 — `GET /api/debug/action-budget-report` (RPG Server Debug, read-only)

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| The endpoint returns the report against a store seeded through the **real** import path | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ActionBudgetReportTests"` | **1/1 pass.** The host boots through `RpgApiFactory`; the test seeds with the same real path the host's boot import uses (`ActionCorpusImporter.Import` over the committed `committed-round-{1,2}.json` + `authored-basics.json`, with the shipped `action-corpus-cost-templates.v2.json`), then GETs the endpoint. `kind`, `cap`, `pricedActionCount`, the per-rung reconciliation and `recommendedReferencePower` all come back from real rows — never a fixture action. | gk-core/src/FusionRpg.Server/DebugEndpoints.cs, gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs |
| It performs **no write** | same test | **Passes.** `store.ComputeContentHash().ToCompact()` and `store.ListActionPricing().Count` are captured before the GET and asserted identical after it. | gk-core/tests/FusionRpg.E2E.Tests/ActionBudgetReportTests.cs |
| It prices through the one shared path, not a second one | code read | `BudgetCalibration.Read(store.ListActionPricing(), RungPolicy.Table)` — the store read ST4.1 added and the table the catalog check reads. Contract 4's "runs the real store read and the real pricing against real imported rows" is the whole body. | gk-core/src/FusionRpg.Server/DebugEndpoints.cs |
| Labelled **RPG Server Debug** | code read | The endpoint carries the `// RPG Server Debug` label and states its scope: it must run the real domain path against real rows, writes nothing and fabricates nothing (`live-probe-standard.md`). | gk-core/src/FusionRpg.Server/DebugEndpoints.cs |
| Boundary | `.\scripts\verify-change.ps1 -Paths … -Session summoner-convergence-impl-20260918` + `.\scripts\guard-dal.ps1` | `dal` OK · `test-substrate` OK · **e2e 226/226** · **server 532 passed / 18 failed / 550 total**, identical to the recorded baseline. | tasks/summoner-convergence-ledger.jsonl |

## Three things this task had to decide, all declared

1. **The test lives in E2E, not `Server.Tests`.** The acceptance's Files line names
   `tests/FusionRpg.Server.Tests/Actions/ActionBudgetReportTests.cs`, but that project has no host-boot
   reference at all — T63 hit the same wall and recorded the same deviation. The endpoint only exists
   inside `MapDebug`, on a real host, so the test sits where the host is reachable. Its Verify filter is
   therefore `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ActionBudgetReportTests"`
   rather than the Server.Tests filter the todo names.
2. **`gk-core/scripts/verification-boundaries.v1.json` gained an `e2e-action-budget-report` owner.** `verify-change`
   refused the new path as unmapped; repairing the map is the fix, not dropping the path.
3. **`BattleHolderRungHostTests` (T74) is fixed in this commit — my new test broke it, and the fixture was
   the defect.** That fixture built its container from *the first enabled atom the store happened to
   hold*. This task's seeding imports the real atom seed, so that pick changed, and the chosen atom's
   container was one the resolver cannot bind — `BattleRunState.BindContainers` threw and both T74 tests
   failed **only in a full-module run** (they passed alone, and had passed in the full module before this
   task). The container now holds an atom the test authors itself, so the fixture no longer depends on
   ambient content. Fixed at the cause, not by isolating the suites.

## A measurement worth recording

The E2E module is `226` tests now and green; `Server.Tests` is `18 failed / 532 passed / 550 total` in
**both** Debug and Release, matching the baseline recorded at T62. One intermediate `verify-change`
execution reported `531/549` for the server module; a direct re-run of the same configuration returned
`532/550`, and `--list-tests` discovers 550 in both configurations — so that was a one-off partial report
from that execution, not a lost test.

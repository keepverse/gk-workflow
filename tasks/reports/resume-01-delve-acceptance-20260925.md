# Manager acceptance review — Delve server-owned wild/cage join

**Source lane:** `resume-01-delve-owner-recovery-20260925` (worker report preserved; no direct merge)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-delve-owner-20260925`
**Status:** **PARTIAL until exact-SHA clean checkout; scoped join contract is green**

## Review verdict

The recovered diff closes the confirmed caller-controlled join seam within its stated scope:

- `/talk` and `/cage` ignore compatibility `Spec`, `Price`, and `SinkKey` fields.
- Room kind and cage state use the persisted effective kind (`ResolvedKind ?? Kind`) in both HTTP precheck and the Data transaction.
- Party selector is checked against the configured raid party count and a persisted player-owned `Warband` at the requested sector; the same check is repeated inside the write transaction.
- Candidate, traits, offer floor, and sink are derived from persisted delve/room state, catalogs, and tuning. The request cannot substitute them.
- Blank effective persisted archetype data refuses. Archetype-specific encounter-pool expansion is explicitly not invented in this join-only repair.
- The production steering policy is explicit and fail-closed: selector zero is admitted, other selectors return `wild.party-not-steered` until an owner-approved persisted/live steering signal exists. This is surfaced as an open owner question, not presented as a final multi-party ruling.

No Contracts, generated data, tuning, or unrelated path was changed.

## Independent evidence

```text
dotnet test gk-core/tests/FusionRpg.Core.Tests
  --filter "FullyQualifiedName~DelvePricesTests"
# 22 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests
  --filter "FullyQualifiedName~DelveWildTransactionTests"
# 18 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests
  --filter "FullyQualifiedName~DelveWildEndpointsTests"
# 18 passed, 0 failed, 0 skipped; exit 0

scripts/guard-dal.ps1
# DAL GUARD OK; exit 0
gk-core/scripts/guard-test-substrate.py
# exit 0
verify-change.ps1 -Paths <six concrete executable paths>
  -Session resume-01-delve-acceptance-20260925 -PlanOnly -Format json
# exit 0; intended Core/Data/Server/DAL owners selected
scripts/session-boundary-check.py --session resume-01-delve-acceptance-20260925
# clean; exit 0
```

The worker's complete executable-path `verify-change` run exceeded its 300-second bound after starting split Core projects and produced no final verdict. It is recorded as incomplete, not green. The focused project tests, DAL, substrate, PlanOnly, and boundary checks are the manager's acceptance evidence for this scoped change.

## Open owner decision and limitations

1. The durable/live source and semantics for multi-party steering remain unresolved. Selector zero is deliberately a temporary fail-closed policy; the owner must rule before it can be treated as final `duo`/`quad` behavior.
2. Join pricing uses the persisted `ThetaRun` watermark because the room schema has no room-local theta column. `/pray` retains its pre-existing caller theta seam; this lane does not redesign it.
3. Archetype-specific candidate pools are not expanded; the effective persisted archetype is validated/passed, while the current candidate stream remains coordinate-derived.
4. The existing unbanked-soul primitive does not persist the descriptive sink key as a separate ledger row; this lane does not broaden the economy.
5. No live game/server/browser proof was run.

## Remaining acceptance steps

1. Commit this reviewed six-file production/test diff and this report at an exact SHA.
2. Run the focused tests, DAL/substrate guards, PlanOnly, and boundary check from a clean detached checkout.
3. Write the exact-SHA artifact and merge only that SHA.
4. Keep the steering ruling, live proof, and later economy/schema questions open in the owning program ledger.

<<<REPORT {"status":"partial","summary":"Manager review accepts the scoped Delve server-owned wild/cage join contract: persisted effective room kind/cage state, persisted party ownership/location, server-resolved candidate/traits/price/sink, and fail-closed explicit temporary steering. Core 22/22, Data 18/18, Server 18/18, DAL, substrate, PlanOnly, and boundary checks passed. The full path-owned aggregate timed out without a verdict, no live proof exists, and the durable multi-party steering ruling remains an explicit owner question; exact-SHA clean-checkout acceptance remains.","changed_files":["gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs","gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs","gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs","gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs","gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs","tasks/reports/resume-01-delve-acceptance-20260925.md"],"verification":["22 DelvePricesTests passed","18 DelveWildTransactionTests passed","18 DelveWildEndpointsTests passed","DAL guard passed","test-substrate guard passed","path-owned PlanOnly passed","session boundary check passed","full path-owned aggregate exceeded 300 seconds without a final verdict; not counted as green"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","durable/live multi-party steering source and semantics await owner ruling","room-local theta and archetype-specific encounter expansion remain separate","no live game/server/browser proof"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification and artifact","merge exact SHA","route steering decision and later schema/economy work to the owning ledger","run merged-head and live gates at their explicit boundaries"]} REPORT>>>

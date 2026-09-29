# TVB-F2 (first half) — the drain-guard offender was this program's own test file

| Criterion | Command | Result |
|---|---|---|
| The offender, before | `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "FullyQualifiedName~SubprocessPipeDrainGuardTests"` | **1 failed** — `sequential stdout-then-stderr ReadToEnd() ... tests\FusionRpg.FileMove.Tests\SplitExecutorTests.cs` |
| Cause read | `git show HEAD:gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs \| grep -n ReadToEnd` | lines 289-290: `StandardOutput.ReadToEnd()` **then** `StandardError.ReadToEnd()` — the documented pipe-deadlock hazard, pre-existing (not introduced by TVB5.7/5.8) |
| Fix | `SplitExecutorTests.RunDotnetBuild` drains both pipes concurrently (`ReadToEndAsync` on both, `WaitForExit`, then a bounded `Task.WaitAll`), the same shape `tests/FusionRpg.Guard.Tests/TestSupport/ExternalProcess.Run` uses — inlined, because test projects in this repo do not reference each other | applied |
| The offender, after | same command as row 1 | **1 passed / 0 failed** |
| No regression in the tool's own suite | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release` | **47 passed / 0 failed** |

The row's second half (the two `VerificationBoundaryWorkflowTests` timeouts) is the TVB-F3 family and is
**not** resolved here: the pipeline hook refuses `gk-core/tests/FusionRpg.Guard.Tests/**` for this lane, recorded
as a blocker in `tasks/tvb-wave5-ledger.jsonl`.

## Confirmed green on this tip (2026-09-21, against manager baseline job b6712875b)

The manager's baseline at integration head `48fd754e` lists this drain guard red. It is **green here**,
and so are the other two in-scope reds:

```
dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release \
  --filter "FullyQualifiedName~CoreTestProjectPolicyTests.W3|FullyQualifiedName~Every_tools_test_project_is_wired_and_exit_checked|FullyQualifiedName~SubprocessPipeDrainGuardTests"
-> Passed! - Failed: 0, Passed: 3, Total: 3
```

- **The drain half turned green**: `31df0398` is not an ancestor of `48fd754e`, so the baseline job ran
  before this fix; the guard is 1/0 here (and 0/1 at HEAD before the fix).
- **W3 and W7 are not reproducible from this branch**: `find tools -name "*.Tests.csproj"` is exactly
  `gk-fusion/tools/LawnCombatObserver.Tests` and `gk-fusion/tools/ProveLiveProbe.Tests`, both wired in `ci.yml` with their own
  exit checks, identical at `48fd754e` and here, and no commit in `48fd754e..3da77ab4` touched `ci.yml` or
  `tools/`. The baseline table itself (`tasks/evidence-fragments/TVB-guard-baseline-20260921.md`) is not in
  this branch, so the two tips must be compared before those two are treated as live.

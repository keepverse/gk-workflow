# TVB-F3 — the reported "printed failures, exited 0" shape does not reproduce on either tip this lane can measure

Both measurements use the same selection and the shape the audit reported (a whole-project check with
failing tests in it):

| Criterion | Command | Result |
|---|---|---|
| The shape, pre-merge tip | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths gk-core/tests/FusionRpg.Guard.Tests/SubprocessPipeDrainGuardTests.cs -Session tvb58"` | `Failed: 1, Passed: 572, Total: 573` and **exit 1** |
| The shape, merged tip (`features/mega-merge` re-merged, 330 files) | same command | `Failed: 3, Passed: 577, Total: 580` and **exit 1** (the 3: the stale CAI-guard-1 pin + the two `VerificationBoundaryWorkflowTests` timeouts) |
| The exit path that makes it correct | `grep -n 'exit \$LASTEXITCODE' scripts/verify-change.ps1` | `:309`, `:313`, `:317` — one after **every** `dotnet test` — and `:322` after every guard / doc-citations / script check |
| A guard check's failure also propagates | `verify-change.ps1 -Paths tasks/test-verification-boundary-todo.md,tasks/item-todo.md -Session tvb58` | **exit 1** at the `doc-citations` check (19 pre-existing HIGH in `item-todo.md`) |

**The one real hole in this family, found and fixed elsewhere this session.** `dotnet test` exits **0**
when it discovers *no* tests — it prints `No test is available in … Make sure that test discoverer &
executors are registered` and reports success. Measured live (2026-09-20, while fixing TVB5.7):

```
dotnet test gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests.csproj -c Release --filter "Category!=DiskSemantics&Category!=Heavy"
EXIT=0        # 0 tests run, "No test is available in …"
```

So a **selected check that runs zero tests** is indistinguishable from a pass — the same class of
gate-breaking defect as TVB-F3, and the reason the split tool's own gate now refuses a test step that
reports no/zero tests (`gk-core/tools/FileMove`, `tvb5-7-zero-test-gate.md`). `scripts/verify-change.ps1` has no
such check, and it is pipeline-protected for this lane.

**NOT proved**: the `ep-autoassign` observation itself (their tip, `Failed: 4 … 14838` and
`Failed: 3 … 573`, both with exit 0). With a failing selected check on either tip this lane can measure,
verify-change exits 1. The plausible remaining mechanisms are a test-host crash that prints `Failed!`
while VSTest still exits 0, or a caller that read the wrapper's status rather than the script's — both
need the original command line and tip to settle.

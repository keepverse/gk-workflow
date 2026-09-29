# CAI-guard-2 — the two CI-tier guard reds that were this program's own files

Lane `combat-ai-2`. Both findings are from this lane's own CAI1.14 work (the decision scratch buffers) and
its own test file, and both fixes are in-fence with no guard edit anywhere.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| M1 HIGH cleared: no bare numeric literal in a balance-surface file | `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` | **`M1=0  M2=0  M3=0  M4=0`, total 0 findings** — "MAGIC-NUMBER GUARD OK". The two flagged lines were `new(64)` on `_eligibleScratch`/`_candidateScratch`; the capacity is now the named, documented `DecisionScratchCapacity`, so the structural role is reviewable instead of looking like a balance dial | `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs` |
| P1 cleared: no unpinned literal count assertion | `pwsh -NoProfile -File scripts/guard-population-pin.ps1` | **clean, total 0 findings** — `Assert.Equal(32, result.Count)` now reads `Assert.Equal(cap, result.Count)` where `cap` comes from a `ScoringWeights`, so the assertion pins the WORK BOUND's contract rather than a count | `gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs` |
| The row's acceptance: the CI tier reports 0 red for both guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | **only `doc-citations` red** ("guards failed: doc-citations"); `magic-numbers` and `population-pin` are both 0. The remaining red is the attributed notify-rail migration in OTHER programs' docs — 20 HIGH, none in `docs/architecture/combat-ai/**` | — |
| Behaviour unchanged | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests"`; `--filter "FullyQualifiedName~CoreIntentPolicy"` | **12 passed / 0 failed** and **8 passed / 0 failed** — one is a rename of a buffer capacity, the other an assertion that derives its value | — |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed, 0 failed** | — |
| Neighbouring suites | `--filter "FullyQualifiedName~ActionScheduleMatchesCorePolicyTests\|~ActionStageTests"` | **18 passed, 0 failed** | — |
| Boundary, every selected project's numbers | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs') -Session combat-ai-20260920"` | **15104 passed / 0 failed** across the five projects: Core.Tests 13209, Atoms.Tests 1351, ActorHub.Tests 498, ActorSurface.Tests 31, AchievementTitlesTuningTests 15 | — |

## Why the two fixes are the ones the guards intend, not dodges

**The `64`s are structural, and the guard has a stated mechanism for that.** `docs/architecture/tunables-ssot.md`
T2 asks a structural const to say why it is not tunable; the audit's own reader (`EXEMPT_NAMES`) is full of
exactly this shape with a reason beside each. Naming the capacity and documenting it in place is the fix the
row's own text allows ("or by showing the guard's own justification for a structural constant") — and it is
what `CostLedger.StackCostRows` already does for the same kind of value. The capacity caps no magnitude: a
decision with more candidates than this still works, the list just grows once, which is why every
zero-allocation assertion in that suite warms first.

**The count assertion now pins the bound it depends on.** `Assert.Equal(32, result.Count)` was a bare
population reading of the fixture; `Assert.Equal(cap, result.Count)` with `cap` taken from a `ScoringWeights`
asserts that the stage builds exactly its configured cap and no more — the contract, not the number. The
fixture still configures 32, but as configuration rather than as the thing being asserted.

**No guard was edited.** Both files are inside this lane's fence; `scripts/**`, where the auditors live, is
not, so an exemption could not have been added even if it were the right answer.

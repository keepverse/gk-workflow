# Manager acceptance review — verification-boundary mapping repair

**Draft source:** `resume-00b-verification-mapping-20260925` (partial worker result)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-verification-mapping-20260925`
**Status:** **PARTIAL — structural repair is ready; composite path verification remains pending**

## Independent review

The worker added a focused `seedsmith-bcu212` owner before the broad `seedsmith-fallback`, with the three BCU2.12 production paths and only the launcher/report/J9 test files. The manager extended the same focused registry with a `manager-fail-closed` pytest project and a `manager-fail-closed` owner before the Seedsmith boundary. The owner covers all four concrete Phase 0A files and selects only `test_fail_closed_pipeline.py`; no broad root or unfiltered fallback is used.

The registry remains valid JSON, and the new structural regression covers both owners, fallback ordering, and a neighboring Seedsmith path. The isolated worktree does not contain the dependent Phase 0A/Seedsmith test files, so a real composite `verify-change.ps1 -PlanOnly` cannot be run here without crossing another session's fence. That limitation is recorded rather than hidden.

## Commands run

```text
Get-Content gk-core/scripts/verification-boundaries.v1.json -Raw | ConvertFrom-Json
# exit 0; schemaVersion 5 parsed

dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-build --filter "FullyQualifiedName~VerificationBoundaryMappingRepairTests" --verbosity minimal
# 4 passed, 0 failed, 0 skipped; exit 0

git diff --check
# exit 0
```

## Acceptance blockers

- The mapping worker ended `partial`; its runner could not prove the current-root plan because the two Seedsmith acceptance test files are absent in that isolated worktree.
- The Phase 0A manager test file is likewise absent from this isolated mapping worktree.
- No exact manager commit/SHA or schema-valid acceptance artifact exists yet.

## Required next steps

1. Commit this mapping/test/report set at an exact SHA and merge only after manager review.
2. In the composite acceptance check, run `verify-change.ps1 -PlanOnly` and the actual path-owned verification with the Seedsmith and Phase 0A test files present; assert every concrete path maps to its focused owner and not `seedsmith-fallback`.
3. Run the focused Guard regression and clean-checkout evidence at the merged exact SHA.
4. Only then write a GREEN acceptance artifact and release the Seedsmith/Phase 0A acceptance gates.

No generated data, product code, model run, or release/live claim is made here.

<<<REPORT {"status":"partial","summary":"Manager review confirms the focused Seedsmith and fail-closed manager boundary definitions are structurally correct and 4 structural tests pass, but composite path-owned verification cannot run in this isolated mapping worktree because dependent test files are not present. No exact-SHA acceptance or merge is claimed.","changed_files":["gk-core/scripts/verification-boundaries.v1.json","gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs","tasks/reports/resume-00b-verification-mapping-20260925.md","tasks/reports/resume-00b-verification-mapping-acceptance-20260925.md"],"verification":["verification-boundaries JSON parsed","4 VerificationBoundaryMappingRepairTests passed with --no-build","git diff --check passed"],"open_issues":["composite PlanOnly/path-owned verification is pending with the Phase 0A and Seedsmith test files present","no exact manager SHA or acceptance artifact yet","mapping worker result is partial"],"next_steps":["commit the focused mapping at an exact SHA","run composite PlanOnly and concrete path-owned verification in the dependency acceptance worktree","run clean-checkout structural checks","write and validate the mapping acceptance artifact before merging dependent lanes"]} REPORT>>>

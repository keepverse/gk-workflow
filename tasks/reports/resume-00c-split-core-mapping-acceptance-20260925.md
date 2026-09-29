# Manager acceptance review — split-Core verification mapping

**Source lane:** `resume-00c-split-core-mapping-20260925` (stopped after its selected Guard verifier stalled)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-split-core-mapping-20260925`
**Status:** **PARTIAL until exact-SHA clean-checkout acceptance; scoped mapping checks are green**

## Change reviewed

The seven production areas now resolve to their existing narrow owner groups instead of `core-residual`:

- Activity → `core-area-activity-owners`
- Delve → `core-area-delve-owners`
- Expeditions → `core-area-expeditions-owners`
- PassiveTree → `core-area-passivetree-owners`
- Progression → `core-area-progression-owners`
- Scope → `core-area-scope-owners`
- Vfx → `core-area-vfx-owners`

The Events path remains on the existing `core-events` owner as a control. The new test is included in the focused `guard-verification-boundary-tests` boundary.

## Independent evidence

```text
Get-Content gk-core/scripts/verification-boundaries.v1.json -Raw | ConvertFrom-Json
# schemaVersion 5 parsed; exit 0

dotnet test gk-core/tests/FusionRpg.Guard.Tests
  --filter "FullyQualifiedName~SplitCoreVerificationMappingTests"
# 2 passed, 0 failed, 0 skipped; exit 0

dotnet test gk-core/tests/FusionRpg.Guard.Tests
  --filter "FullyQualifiedName~VerificationBoundaryWorkflowTests"
# 57 passed, 0 failed, 0 skipped; exit 0

verify-change.ps1 -Paths <eight representative production paths>
  -Session resume-00c-split-core-mapping-acceptance-20260925
  -PlanOnly -Format json
# exit 0; every named area selected its intended owner and no core-residual test check appeared

git diff --check
# exit 0
```

The source worker's full selected `verify-change` Guard process was terminated after two prolonged waits; that timeout is preserved as a limitation and is not counted as a green result. The manager's focused structural and planner evidence is recorded separately; no broad retry was used as a substitute.

The clean detached checkout at the reviewed SHA was also checked. The 2-test mapping selection passed. The first 57-test `VerificationBoundaryWorkflowTests` run was load-sensitive: 56 passed and the known subprocess P6 test hit its 120-second timeout. P6 was then rerun alone and passed (1/1); the direct boundary guard also returned `VERIFICATION BOUNDARY GUARD OK` (198.41s under the current concurrent load). The new planner regression initially inherited the same 120-second timeout when invoked with Windows PowerShell; manager review changed it to `pwsh` with a bounded 300-second timeout, after which both mapping tests passed. The clean checkout remained CLEAN. This is recorded as a timeout plus focused rerun and a bounded test correction, not silently upgraded to an all-green claim.

## Data and safety

- No `gk-data/packs/fusion/data/seed`, `gk-data/packs/fusion/data/generated`, tuning, product, CI, or unrelated test paths changed.
- No population count was used as a guard; the tests assert owner identity, existing group membership, ordering, and planner resolution.
- No generated data or live model run was touched.

## Required next steps

1. Commit this scoped registry/test/report set at an exact SHA.
2. Verify the exact SHA from a clean detached checkout using the focused tests and PlanOnly command.
3. Write/validate the exact-SHA acceptance artifact, then merge only that SHA.
4. Re-run the merged-head gate after the mapping merge; the prior legal-game/interops BLOCKED result remains open.

<<<REPORT {"status":"partial","summary":"Manager independently verified the seven split-Core owner mappings and the Events control: JSON parses, 2 mapping tests pass, 57 VerificationBoundaryWorkflowTests pass, and PlanOnly resolves all representative paths to the intended owners without core-residual. The worker's full Guard verifier timed out and is not treated as green; exact-SHA clean-checkout acceptance remains.","changed_files":["gk-core/scripts/verification-boundaries.v1.json","gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs","tasks/reports/resume-00c-split-core-mapping-acceptance-20260925.md"],"verification":["verification-boundaries JSON parsed","2 SplitCoreVerificationMappingTests passed","57 VerificationBoundaryWorkflowTests passed","PlanOnly selected all seven intended owner groups and no core-residual check","git diff --check passed"],"open_issues":["exact-SHA clean-checkout artifact is not yet created","worker full verify-change Guard selection timed out twice and was terminated","merged-head gate remains blocked on legal game/interops"],"next_steps":["commit exact scoped SHA","clean-checkout focused/planner verification","write and validate exact-SHA artifact","merge exact SHA","rerun merged-head gate after mapping merge"]} REPORT>>>

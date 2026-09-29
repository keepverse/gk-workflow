# Composite manager acceptance — Phase 0A + verification mappings + Seedsmith recovery

**Scope:** exact fail-closed merge contracts, focused verification-boundary mappings, CI wiring required by the new manager pytest project, and the Seedsmith BCU2.12 finalization code/tests. Generated corpus files and the live model run are outside this scope.

## Review inputs

- Phase 0A source draft: `opencode-resume-00a-fail-closed-final-20260925`
- Seedsmith source draft: `opencode-seedsmith-p1-audit-final-20260925`
- Mapping draft: `opencode-resume-00b-verification-mapping-20260925`, extended by manager review
- Composite base: current `features/mega-merge` plus reviewed mapping commit `dd48ce163`
- No worker branch was merged directly into the integration branch.

## Findings closed in this composite check

1. Phase 0A exact verdict matching and integration-ancestry checks are present in both direct acceptance and batch merge paths. The 57-test fail-closed fixture passes, including junk-suffix, orphan-history, exact-SHA, clean-tree, and non-integration-branch regressions.
2. `seedsmith-bcu212` maps the launcher, report, and J9 batch driver to only the three focused BCU2.12 test files. `manager-fail-closed` maps the four fail-closed files to the single regression fixture. Both owners precede the broad fallback.
3. The first composite path-owned run exposed a real CI wiring defect: the new manager pytest project had no matching CI step. The owning Phase 0B review worktree added the exact-root `python -m pytest test_fail_closed_pipeline.py` step; the targeted CI-wiring test passed before the composite rerun.
4. The rerun selected no `seedsmith-fallback` and no missing owner for any concrete executable path.

## Exact verification evidence

The complete concrete executable path set was passed to:

```powershell
$changed=@(
  '.claude/cmdc-agents/scripts/post_merge_check.py',
  '.claude/cmdc-agents/scripts/accept-lane.ps1',
  '.claude/cmdc-agents/scripts/merge-lanes.py',
  '.claude/cmdc-agents/scripts/test_fail_closed_pipeline.py',
  '.claude/cmdc-agents/scripts/bcu212-full-run.ps1',
  '.claude/cmdc-agents/scripts/bcu212-report.py',
  'gk-forge/tools/seedsmith/_j9_batch_run.py',
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py',
  'gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py',
  'gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py',
  'gk-forge/tools/seedsmith/tests/test_j9_batch_run.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py',
  'gk-forge/tools/seedsmith/tests/test_bcu212_report.py',
  'gk-core/scripts/verification-boundaries.v1.json',
  'gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs',
  '.github/workflows/ci.yml'
)
.\scripts\verify-change.ps1 -Paths $changed -Session resume-00-composite-acceptance-20260925
```

Terminal selected results from the successful rerun:

- manager fail-closed pytest: `57 passed`, exit 0;
- Seedsmith focused selection: `774 passed, 27 subtests passed`, exit 0;
- Guard module: `677 passed, 0 failed, 0 skipped`, exit 0;
- Guard verification-boundary selection: `61 passed`, exit 0;
- Guard workflow selection: `17 passed`, exit 0;
- the CI-wiring regression was independently run after the correction: `2 passed`, exit 0;
- YAML parsing for the modified workflow, PowerShell parsing for the changed scripts, Python compilation, JSON parsing, and `git diff --check` all passed.

The first composite attempt is retained as a RED finding, not hidden: it failed only at the new manager project's missing CI wiring. The correction and successful rerun are the current evidence.

## Data and safety review

- `git diff --name-only -- gk-data/packs/fusion/data/seed gk-data/packs/fusion/data/generated src` returned no paths.
- The captured BCU2.12 evidence remains read-only and incomplete at 361/904. No corpus completion or model-call claim is made.
- No resume, live endpoint, browser, release, or product merge was performed by this acceptance worktree.

## Remaining Phase 0 work

The separate Phase 0B release-topology review still has unresolved contract findings around the raw `VERIFICATION_GATE` comment check and the existing-`node_modules` reproducibility branch in `publish-player.ps1`. Those paths were not silently included in this scoped acceptance. They must be repaired and independently accepted before the full Phase 0 merged-head gate is GREEN.

## Acceptance state

This worktree is intentionally dirty until the two logical code commits and this report are committed. After commit, the manager must pin the exact final SHA, verify a clean checkout, validate the acceptance artifact, and merge only that reviewed SHA. Until then: **not merged; BCU2.12 resume remains blocked.**

<<<REPORT {"status":"partial","summary":"Composite manager verification is GREEN for the scoped Phase 0A fail-closed scripts, focused verification mappings/CI wiring, and Seedsmith BCU2.12 code/tests: 57 fail-closed tests, 774 Seedsmith tests plus 27 subtests, 677 Guard tests, 61 verification-boundary tests, and 17 workflow tests passed. The worktree still needs exact-SHA commit/clean-checkout acceptance; separate Phase 0B release/publish contract findings remain open.","changed_files":[".claude/cmdc-agents/scripts/post_merge_check.py",".claude/cmdc-agents/scripts/accept-lane.ps1",".claude/cmdc-agents/scripts/merge-lanes.py",".claude/cmdc-agents/scripts/test_fail_closed_pipeline.py",".claude/cmdc-agents/scripts/bcu212-full-run.ps1",".claude/cmdc-agents/scripts/bcu212-report.py","gk-forge/tools/seedsmith/_j9_batch_run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py","gk-forge/tools/seedsmith/seedsmith/adapters/trees/species/generate_tree.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_nodegen_language_stage.py","gk-forge/tools/seedsmith/tests/adapters/trees/test_tree_species_generate_tree.py","gk-forge/tools/seedsmith/tests/test_j9_batch_run.py","gk-forge/tools/seedsmith/tests/test_bcu212_launcher.py","gk-forge/tools/seedsmith/tests/test_bcu212_report.py","gk-core/scripts/verification-boundaries.v1.json","gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs",".github/workflows/ci.yml","tasks/reports/resume-00-composite-acceptance-20260925.md"],"verification":["complete concrete-path verify-change rerun passed: 57 manager tests, 774 Seedsmith tests plus 27 subtests, 677 Guard tests, 61 verification-boundary tests, 17 workflow tests","CI pytest wiring regression 2 passed after correction","JSON/Python/PowerShell/YAML parse checks passed","git diff --check passed","no generated/source data diff"],"open_issues":["exact final SHA and clean-checkout acceptance artifact are not yet created","Phase 0B raw release marker contract remains a separate finding","publish-player existing-node_modules reproducibility branch remains a separate finding","full merged-head post-merge gate has not run","BCU2.12 corpus remains incomplete and resume is blocked"],"next_steps":["commit the scoped code in logical commits","pin and clean-checkout the final reviewed SHA","write and validate the exact-SHA acceptance artifact","repair and independently accept the remaining Phase 0B release/publish findings","run the merged-head post-merge gate before resuming BCU2.12"]} REPORT>>>

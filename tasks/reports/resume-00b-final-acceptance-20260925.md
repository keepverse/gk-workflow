# Final manager acceptance — Phase 0B release and verification topology

**Scope:** release superset wiring, CI/verification topology, native guard/session/seed/packaging checks, and the two independently confirmed Phase 0B contract gaps. The accepted CI pytest wiring and verification-boundary registry are already present in the integrated base. The split-Core registry remap remains explicitly deferred.

## Repairs reviewed and applied

1. **Release superset is structural.** The release workflow's `ci-superset` job calls `./.github/workflows/ci.yml`, and `publish` depends on that job. The contract step now checks the actual `workflow_call` trigger, reusable-workflow call, and dependency. It no longer treats `VERIFICATION_GATE` comments as evidence; the duplicated raw marker block was removed from `release.yml`.
2. **Player packaging is reproducible.** `publish-player.ps1` now runs `npm ci` unconditionally before `npm run build` and checks the native exit. The structural test rejects the old `node_modules`-existence bypass.
3. **The existing Phase 0B topology changes were preserved.** CI reusable workflow wiring, explicit history/ranges, generated-seed and session-boundary checks, failure-checked native commands, enforcement exemptions, and the structural Guard tests remain in the reviewed diff.

## Independent verification

```text
YAML parse: ci.yml, release.yml, nightly.yml — exit 0
PowerShell parser: run-guards, guard-generated-seed, verify-change,
  session-boundary-check, publish-player — exit 0

dotnet test gk-core/tests/FusionRpg.Guard.Tests
  --filter "FullyQualifiedName~VerificationTopologyTests"
# 10 passed, exit 0

dotnet test gk-core/tests/FusionRpg.Guard.Tests
  --filter "FullyQualifiedName~WorkflowExitCheckTests|FullyQualifiedName~VerificationTopologyTests|FullyQualifiedName~VerificationBoundaryWorkflowTests|FullyQualifiedName~GuardRunnerTests|FullyQualifiedName~EnforcementRegistryGuardTests|FullyQualifiedName~CiWiringGuardTests|FullyQualifiedName~CiPytestWiringTests"
# 104 passed, 0 failed, 0 skipped, exit 0

git diff --check — exit 0
```

The complete concrete path-owned command was run with the active session id. Its selected groups all passed: 687 Guard tests, 18 verification-boundary tests, 8 workflow/wiring tests, 61 registry/guard tests, 17 workflow tests, and 166 Launcher tests. The command is recorded in the session report and is not replaced by a broad unfiltered suite.

An earlier `dotnet test --no-restore` invocation in a clean worktree produced a successful build but no test execution; it is explicitly excluded from the evidence. The restored focused runs above are the valid results.

## Data and scope checks

- No `gk-data/packs/fusion/data/seed`, `gk-data/packs/fusion/data/generated`, tuning, or product paths were changed.
- No generated corpus was edited.
- No remote GitHub Actions run, release, browser, live injector, or model run was performed.
- The split-Core verification-boundary project remap is a named deferred dependency, not silently treated as complete.

## Remaining gates before Phase 0 is fully green

- Commit this exact reviewed diff and run a clean-checkout path-owned verification with an on-disk log.
- Merge the exact Phase 0B SHA only after its acceptance artifact validates.
- Re-run the merged-head `post_merge_check.py` with a legal game/interops environment. The prior merged-head attempt was BLOCKED at the legal-game-dependent Injector build and is not green.
- Keep BCU2.12 resume blocked until the merged-head gate reaches a terminal GREEN result and the Seedsmith evidence is reconciled.

<<<REPORT {"status":"partial","summary":"Final Phase 0B review closes the raw release-marker false proof and the publish-player dependency-tree bypass. Ten topology tests, 104 focused Guard tests, structural parsing, and the complete concrete path-owned verification passed; the worktree still needs exact-SHA clean-checkout acceptance, the split-Core remap remains deferred, and the merged-head gate is still BLOCKED by legal game/interops.","changed_files":[".github/workflows/ci.yml",".github/workflows/release.yml",".github/workflows/nightly.yml","gk-core/scripts/enforcement-registry.v1.json","gk-core/scripts/guard-generated-seed.py","scripts/publish-player.ps1","scripts/run-guards.ps1","scripts/session-boundary-check.py","scripts/verify-change.ps1","gk-core/tests/FusionRpg.Guard.Tests/VerificationTopologyTests.cs","tasks/reports/resume-00b-final-acceptance-20260925.md"],"verification":["YAML and PowerShell parsing passed","10 VerificationTopologyTests passed","104 focused Guard tests passed","complete concrete path-owned verify-change passed with 687/18/8/61/17/166 selected tests","git diff --check passed"],"open_issues":["exact-SHA clean-checkout artifact is not yet created","split-Core verification-boundary remap is deferred","merged-head post-merge gate remains BLOCKED on legal game/interops","remote CI/release and live evidence not run"],"next_steps":["commit Phase 0B at an exact SHA","clean-checkout rerun and acceptance artifact","merge exact SHA","rerun merged-head gate with legal environment or preserve BLOCKED","only then resume BCU2.12"]} REPORT>>>

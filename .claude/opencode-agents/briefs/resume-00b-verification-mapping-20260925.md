# Phase 0B verification-boundary mapping repair

The failed `build-preset-bp1` worker has been reconciled as abandoned, so `gk-core/scripts/verification-boundaries.v1.json` is no longer owned by a live lane. Repair the two concrete Seedsmith mapping defects that block the manager acceptance gate:

- `.claude/cmdc-agents/scripts/bcu212-full-run.ps1`
- `.claude/cmdc-agents/scripts/bcu212-report.py`
- `gk-forge/tools/seedsmith/_j9_batch_run.py`

At the current tree, the broad `seedsmith-fallback` entry appears before the focused tree owner and captures the batch driver, causing `verify-change.ps1` to select the entire `gk-forge/tools/seedsmith` module. The launcher/report scripts have no owner mapping at all. Add a focused owner boundary before the fallback, with the smallest real test set: the BCU2.12 launcher/report tests plus `test_j9_batch_run.py`; do not broaden a root or use an unfiltered suite as a substitute.

## Allowed paths

- `gk-core/scripts/verification-boundaries.v1.json`
- `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryMappingRepairTests.cs`

Do not edit Phase 0B's existing `VerificationTopologyTests.cs`, CI/release files, enforcement registry, Seedsmith code, generated data, or any other path. Do not commit, push, or merge.

## Required checks

1. Parse the JSON before committing.
2. Prove `verify-change.ps1 -PlanOnly` maps all three concrete paths to the new focused boundary, not `seedsmith-fallback` and not missing.
3. Prove the focused project selection names the intended test files and does not silently select the whole module.
4. Add a structural regression test for exact path mapping, fallback ordering, and a neighboring unrelated Seedsmith path remaining on its existing owner.
5. Run the focused Guard test project/filter and `git diff --check`; record exact commands and exit codes.

Do not claim that a broad Seedsmith run is evidence. Do not resume BCU2.12. Write `tasks/reports/resume-00b-verification-mapping-20260925.md` with the exact diff, commands, outputs, open issues, and next steps, ending with the required report marker.

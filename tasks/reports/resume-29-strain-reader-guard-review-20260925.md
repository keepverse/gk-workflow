# Resume 29 — SSH7.1/SSH8.4 exact-SHA manager review

**Date:** 2026-09-25
**Program:** `strain-splice-host`
**Worker base:** `29df9959829447faba9fbf00483fe165d8555b16`
**Reviewed implementation SHA:** `a120ce2d8f83617228017a020c063c35e3c37dd0`
**Worker report:** `tasks/reports/resume-29-strain-splice-reader-guard-20260925.md`

## Disposition

The worker returned terminal `partial` after implementing the bounded SSH7.1 current-revision guard
and the named SSH8.4 materials companion. The implementation was harvested into this independent
review worktree. The manager review found no out-of-fence product change, no tuning publish, no
generated-data edit, and no reason to widen the lane. The reviewed SHA is ready for exact-SHA
acceptance; the known Data sharded-runner defect remains an explicit verification limitation.

## Exact reviewed paths

The implementation commit contains the worker's 14 reader/guard/test paths, the worker report, and
this review session record. The concrete product/test fence is:

- `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`
- `gk-forge/tools/seedsmith/tests/test_combogen.py`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs`
- `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs`

The review session record is
`tasks/sessions/resume-29-strain-reader-guard-review-20260925.json`; the worker report is retained
as the worker's disk-backed execution record.

## Review findings

The C# guard was checked against the actual source reader shapes. It strips comments while
preserving string contents and line structure, recognizes path construction/read syntax, excludes
only the canonical `SocketTuningFiles` home, and keeps an empty conversion allowlist. The Python
check tokenizes path syntax and enforces the two canonical assignments rather than copying a
literal list. The converted C# tests now use `SocketTuningFiles.StrainSplice` and
`SocketTuningFiles.Materials`; the server and existing sockets canonical-reader assertions remain
intact. Prose/history mentions are not treated as readers.

No defect was found that would justify changing the worker's implementation during review. The
report's open issue is verification infrastructure, not a hidden product green claim.

## Independent focused evidence

All commands ran in the review worktree after the implementation was committed:

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter "FullyQualifiedName~TuningRevisionLiteral"
# Passed: 5, Failed: 0

python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q
# 39 passed, 7 subtests passed

dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus|FullyQualifiedName~ItemUpgradeCostContract"
# Passed: 78, Failed: 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~CraftWearInstanceOp|FullyQualifiedName~MaterialSpend"
# Passed: 16, Failed: 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --filter "FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport|FullyQualifiedName~ItemWorkbench|FullyQualifiedName~ItemUpgradeEndpoint"
# Passed: 111, Failed: 0
```

The exact path-owned planner was also run with every concrete changed path and the review session:

```powershell
& .\scripts\verify-change.ps1 -Paths @(
  'gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs',
  'gk-forge/tools/seedsmith/tests/test_combogen.py',
  'gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs',
  'gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs',
  'gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs',
  'gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs',
  'gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs',
  'gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs'
) -Session resume-29-strain-reader-guard-review-20260925 -PlanOnly
# exit 0; selected core-items, data-tests-fallback, guard-tests-fallback,
# server-tests-fallback, focused Seedsmith, and CI/nightly/release full evidence
```

The worker's direct full verifier reached the selected Core, Python, and Data `Items` checks but the
Data sharded runner returned exit 1 for the unrelated `rest` shard; a second attempt timed out while
that shard was still running. An independent unsharded Data union was then run to separate the
runner defect from a product failure: 1,809/1,810 tests passed, with the sole failure
`RpgStoreStoragePlanTests.Memory_schema_is_identical_to_the_file_store` reporting SQLite Error 14
while creating a backup file. The changed Data Items tests remained green. This is recorded as an
external file/AV limitation and is not laundered into a GREEN aggregate claim.

## Clean-checkout and evidence checks

A detached clean checkout is required at the exact implementation SHA before acceptance. The
manager will run the same focused commands and citation/diff checks there. The acceptance artifact
must record `before: CLEAN` and `after: CLEAN`; any build output is ignored and any source/evidence
path change invalidates the acceptance.

The worker report's strict citation audit passed with 34 resolvable citations and zero HIGH findings.
The manager will rerun that audit against the retained report and the review report before creating
schema-v2 evidence.

## Non-actions and remaining gates

- No tuning revision was published; SSH7.7/H7 remains out of scope.
- No generated data, model, Seedsmith corpus, browser, server process, or live game was started.
- No SSH4.9 live path or current-head merged-head claim is created by this review.
- The known Data sharded-runner and external backup-file failures must remain visible in acceptance
  evidence; they do not justify changing the implementation or rerunning an unrelated broad suite.
- Merge is deferred until the main cleanup-owned and owner-routed `.commandcode` paths are resolved.

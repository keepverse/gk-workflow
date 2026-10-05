# Resume 29 — SSH7.1 revision-literal guard with SSH8.4 companion

**Date:** 2026-09-25
**Lane:** `resume-29-strain-splice-reader-guard-20260925`
**Scope:** deterministic reader/guard slice only. No production reader, tuning revision, generated corpus, CI, server, browser, or live-game path changed.

## Boundary and SHAs

- Product base required by the brief: `6d77888cca860805e5a11e617e201847e01c16b7`.
- Prepared boundary commit and starting `HEAD`: `29df9959829447faba9fbf00483fe165d8555b16`.
- Final `HEAD`: `29df9959829447faba9fbf00483fe165d8555b16` (the lane is intentionally left dirty; no commit was created).
- Before work, `git diff 6d77888cca860805e5a11e617e201847e01c16b7..HEAD` contained only the manager-owned session record. The product diff for this lane is the 14 implementation/test files below relative to the product base.
- The worktree boundary check was run before editing:

```text
python scripts/session-boundary-check.py --session resume-29-strain-splice-reader-guard-20260925
[session-boundary] clean for 'resume-29-strain-splice-reader-guard-20260925'
```

The current verification-boundary owner for `gk-core/tests/FusionRpg.Guard.Tests/**` is `guard-tests-fallback` in `gk-core/scripts/verification-boundaries.v1.json:2098-2107`; the manager explicitly granted this lane the protected guard path. No registry or ownership file was edited.

## Contract implemented

### C# guard

`gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` now has separate literal rules for:

- `sockets.v[0-9]+.json` (the existing rule remains);
- `strain-splice.v[0-9]+.json`;
- `materials.v[0-9]+.json`.

The scanner examines C# source under `src`, `tools`, and `tests`, removes comments/doc text while preserving source line positions, and reports only actual path-reader syntax. A filename in `MaterialRecipeCatalog.cs:437`'s exception prose is therefore not treated as a reader and that production file was not changed. `SocketTuningFiles.cs` remains the sole C# filename-constant file. The existing `UnconvertedTests` stale-entry check remains active and the set is empty.

The server reader assertion now requires both `SocketTuningFiles.StrainSplice` and `SocketTuningFiles.Materials` in `gk-core/src/FusionRpg.Server/Program.cs`, while the existing sockets server/validator assertion remains intact.

### Python guard

`gk-forge/tools/seedsmith/tests/test_combogen.py` now tokenizes the Seedsmith package and examines actual path-join syntax (`/` joins and `Path("...")` calls), rather than matching prose. The only allowed assignments are:

- `STRAIN_SPLICE_PATH` in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`;
- `MATERIALS_TUNING_PATH` in `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/brief.py`;
- the existing `SOCKETS_PATH` mirror in `combogen/tuning.py`.

Comments, docstrings, exception text, and documentation do not become an allowlist.

### Test-reader conversions

All shipped-file path joins in the fenced current test readers now use `SocketTuningFiles.StrainSplice` or `SocketTuningFiles.Materials`. Comments and historical/prose literals were preserved. No new reader was found outside the fence.

## Literal reader inventory

### Before conversion

The C# path-reader joins exposed by the new guard were:

- **strain-splice — 10 joins across 5 files**
  - `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs:105`
  - `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs:29`
  - `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:39,225,250,298,590`
  - `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:43,51`
  - `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs:43`
- **materials — 10 joins across 7 files**
  - `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs:22`
  - `gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs:43`
  - `gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs:43`
  - `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs:72,706,747`
  - `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs:82`
  - `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs:83,686`
  - `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs:135`
- Python already had the canonical `STRAIN_SPLICE_PATH` and `MATERIALS_TUNING_PATH` joins; the old Python test did not enforce that contract.

### After conversion

- C# strain-splice path-reader joins outside the canonical constants: **0**.
- C# materials path-reader joins outside the canonical constants: **0**.
- Python strain-splice/materials path joins outside the two canonical assignments: **0**.
- Existing sockets canonical-reader coverage and stale-allowlist behavior remain in force.
- Prose/history mentions remain where they were written, including `gk-core/src/FusionRpg.Core/Items/Materials/MaterialRecipeCatalog.cs:437`; they are not readers and were not allowlisted.

## TDD evidence

### RED

The new C# assertions were added before the reader conversions. The smallest guard run was genuinely red:

```text
dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter "FullyQualifiedName~TuningRevisionLiteral"
Failed!  - Failed:     2, Passed:     3, Skipped:     0, Total:     5
```

The two failures were the new strain-splice and materials facts. Their reported offenders were exactly the 10 + 10 path joins listed in the inventory above. The sockets fact and the two source-text reader assertions passed.

The Python focused assertion run at the same point was already green because the two canonical Python path constants were already present:

```text
python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q -k TuningRevisionLiteral
2 passed, 37 deselected in 2.12s
```

### GREEN

After the minimal reader conversions:

```text
dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter "FullyQualifiedName~TuningRevisionLiteral"
Passed!  - Failed:     0, Passed:     5, Skipped:     0, Total:     5, Duration: 1 s

python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q
39 passed, 7 subtests passed in 11.96s

dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus|FullyQualifiedName~ItemUpgradeCostContract"
Passed!  - Failed:     0, Passed:    78, Skipped:     0, Total:    78, Duration: 766 ms

dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter "FullyQualifiedName~CraftWearInstanceOp|FullyQualifiedName~MaterialSpend"
Passed!  - Failed:     0, Passed:    16, Skipped:     0, Total:    16, Duration: 1 s

dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --filter "FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport|FullyQualifiedName~ItemWorkbench|FullyQualifiedName~ItemUpgradeEndpoint"
Passed!  - Failed:     0, Passed:   111, Skipped:     0, Total:   111, Duration: 15 s
```

## Verification-boundary result

The exact command from the brief was attempted first:

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs','gk-forge/tools/seedsmith/tests/test_combogen.py','gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs','gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs','gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs','gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs','gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs','gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs') -Session resume-29-strain-splice-reader-guard-20260925
verify-change.ps1: Cannot validate argument on parameter 'Format'. The argument "gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs" does not belong to the set "text,json" specified by the ValidateSet attribute.
Exited with code 1
```

That is a `pwsh -File` array-argument binding limitation: the comma-separated array was not evaluated before the script binder. The same script, exact path list, and session were therefore invoked directly in the worker PowerShell as `& .\scripts\verify-change.ps1 -Paths @(...) -Session ...`.

The direct invocation produced this plan and result on its first complete attempt:

```text
Verification plan:
  ... -> core-items (module)                 [4 Core paths]
  ... -> data-tests-fallback (module)        [2 Data paths]
  ... -> guard-tests-fallback (module)       [guard path]
  ... -> server-tests-fallback (module)      [6 Server paths]
  gk-forge/tools/seedsmith/tests/test_combogen.py -> seedsmith-tests (focused)
  pytest: seedsmith
  test: core-items
  test: data  (sharded runner)
  test: guard
  test: server
  full evidence: CI/nightly/release
39 passed, 7 subtests passed
Core.Items.Tests: 1470 passed, 0 failed
Data.Tests: shard a exit 0 (476), shard b exit 0 (41), shard c exit 0 (83), shard rest exit 1 (1185)
TEST-SHARDED FAILED: shard 'rest' exited 1
Exited with code 1
```

A second direct invocation rebuilt the same selected projects and passed Python (39/7), Core (1470/0), and the Data build (0 errors), then exceeded the 600-second command timeout while the unrelated Data `rest` shard was still running:

```text
Command exceeded timeout of 600000 ms. Retry with a larger timeout if the command is expected to take longer.
```

The two changed Data files are in the `Items` shard, which passed in the first direct run; the failing `rest` shard excludes `FusionRpg.Data.Tests.Items`. The direct path-owned Data filter above is green at 16/16. This is recorded as an open verification/infrastructure issue, not hidden as a green boundary result. No verification-boundary registry, script, or CI file was changed.

## Final checks

```text
python scripts/audit-doc-citations.py --scope tasks/reports/resume-29-strain-splice-reader-guard-20260925.md --strict
Doc-citation audit - 1 documents, 34 resolvable citations checked
D1 file does not exist          0   (0 HIGH)
D2 line past end of file        0   (0 HIGH)
D3 ambiguous basename           0   (0 HIGH)
D4 ideal vs approved map        0   (0 HIGH)
D5 registry entry moved         0   (0 HIGH)
exit 0

git diff --check
exit 0
```

Both final report checks passed after the report was written.

## Changed files

1. `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`
2. `gk-forge/tools/seedsmith/tests/test_combogen.py`
3. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs`
4. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs`
5. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs`
6. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs`
7. `gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs`
8. `gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs`
9. `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs`
10. `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs`
11. `gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs`
12. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs`
13. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
14. `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs`
15. `tasks/reports/resume-29-strain-splice-reader-guard-20260925.md`

## Explicit non-actions and open questions

No tuning revision or `publish.py` operation was started. No H7 publish, SSH7.7 ladder flip, SSH4.9 live work, generator/re-emit, model call, generated corpus edit, server process, browser, or live game was started. No commit, merge, push, or branch creation was performed.

Open questions:

- The manager should decide whether to rerun `verify-change.ps1` after the unrelated Data `rest` shard failure/timeout is cleared; the selected Core, Data-items, Guard, Server, and Python checks are green.
- SSH7.7 remains a separate publish/H7 row. SSH4.9 remains live-only. No ownership or fence question was discovered for this slice.

<<<REPORT {"status":"partial","summary":"Implemented the bounded SSH7.1 current-revision guard with SSH8.4 as the named materials companion. Added C# path-join guards for sockets, strain-splice, and materials; added tokenized Python canonical-path checks; converted all fenced C# test readers to SocketTuningFiles constants. RED was 2 failing guard facts with 20 path-join offenders; focused GREEN was Guard 5/5, Seedsmith 39/7, Core 78/78, Data 16/16, and Server 111/111. The required verify-change command was attempted but its pwsh -File array form failed parameter binding; the direct equivalent exposed an unrelated Data rest-shard failure/timeout while the changed Data Items shard passed. Final report checks passed: 34 resolvable citations, 0 HIGH, and git diff --check exit 0.","changed_files":["gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs","gk-forge/tools/seedsmith/tests/test_combogen.py","gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationCorpusTests.cs","gk-core/tests/FusionRpg.Core.Items.Tests/Items/ComboContainerBuildTests.cs","gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs","gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs","gk-core/tests/FusionRpg.Data.Tests/Items/CraftWearInstanceOpTests.cs","gk-core/tests/FusionRpg.Data.Tests/Items/MaterialSpendTests.cs","gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs","gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs","gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs","gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchAssuranceTests.cs","gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs","gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchSpeciesWiringTests.cs","tasks/reports/resume-29-strain-splice-reader-guard-20260925.md"],"verification":["RED: dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter \"FullyQualifiedName~TuningRevisionLiteral\" — Failed 2, Passed 3, Total 5; 10 strain-splice and 10 materials path joins reported","GREEN: dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo --filter \"FullyQualifiedName~TuningRevisionLiteral\" — Passed 5, Failed 0","GREEN: python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py -q — 39 passed, 7 subtests passed","GREEN: dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter \"FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus|FullyQualifiedName~ItemUpgradeCostContract\" — Passed 78, Failed 0","GREEN: dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --filter \"FullyQualifiedName~CraftWearInstanceOp|FullyQualifiedName~MaterialSpend\" — Passed 16, Failed 0","GREEN: dotnet test gk-core/tests/FusionRpg.Server.Tests --nologo --filter \"FullyQualifiedName~ComboPricingBoot|FullyQualifiedName~CombinationImport|FullyQualifiedName~ItemWorkbench|FullyQualifiedName~ItemUpgradeEndpoint\" — Passed 111, Failed 0","required pwsh -File verify-change form — exit 1 at PowerShell parameter binding before script execution","direct verify-change equivalent — selected plan; Python 39/7 and Core 1470/0 passed; Data Items shard passed, unrelated rest shard exited 1; later direct rerun timed out at 600000 ms during rest shard","git diff --check — exit 0","audit-doc-citations strict scope — 34 resolvable citations, 0 HIGH; exit 0"],"open_issues":["verify-change remains red/incomplete because the selected Data fallback uses a sharded runner whose unrelated rest shard failed once and timed out on a second run; changed Data Items tests are green 16/16","final report citation audit and final git diff --check must be rerun after the report is finalized","no tuning publish, H7/SSH7.7, SSH4.9, generator/model/generated corpus, live game, server, browser, commit, merge, or push was started"]} REPORT>>>

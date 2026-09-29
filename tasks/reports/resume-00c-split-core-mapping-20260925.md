# Phase 0C split-Core verification mapping repair

**Date:** 2026-09-25  
**Session:** `resume-00c-split-core-mapping-20260925`  
**Branch/worktree:** `opencode/resume-00c-split-core-mapping-20260925` / the worktree named by the session record  
**Boundary:** no commit, push, or merge; leave the dirty tree for manager review.

## Scope and inspection

The existing `core-fallback` owner is still the broad `gk-core/src/FusionRpg.Core/**` owner on the full `core` project group. The seven area globs already existed and were ordered before the seven `core-area-*` entries' old residual projects:

- `gk-core/src/FusionRpg.Core/Activity/**`
- `gk-core/src/FusionRpg.Core/Delve/**`
- `gk-core/src/FusionRpg.Core/Expeditions/**`
- `gk-core/src/FusionRpg.Core/PassiveTree/**`
- `gk-core/src/FusionRpg.Core/Progression/**`
- `gk-core/src/FusionRpg.Core/Scope/**`
- `gk-core/src/FusionRpg.Core/Vfx/**`

The corresponding existing owner groups were already registered in `gk-core/scripts/verification-boundaries.v1.json`:

| Area | Existing group selected |
|---|---|
| Activity | `core-area-activity-owners` |
| Delve | `core-area-delve-owners` |
| Expeditions | `core-area-expeditions-owners` |
| PassiveTree | `core-area-passivetree-owners` |
| Progression | `core-area-progression-owners` |
| Scope | `core-area-scope-owners` |
| Vfx | `core-area-vfx-owners` |

Before the repair, the real planner resolved all seven representative files to their area boundary but with `project: "core-residual"`. The Events control already resolved to `core-area-events` / `core-events` and was left unchanged.

## Changes

1. Re-keyed the seven existing area owner entries to the matching existing project groups. No new project group, composer, production path, or population-count assertion was introduced.
2. Added `gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs` with:
   - a structural registry check for the seven globs/groups, the preserved `core-fallback`, the neighboring Events control, and the focused test owner; and
   - a real `verify-change.ps1 -PlanOnly -Format json` regression covering one representative file from each area plus the Events control, asserting the intended owner group is selected and `core-residual` is absent.
3. Added the new test file to the existing focused `guard-verification-boundary-tests` owner so registry/test changes select the regression through the existing Guard project.

Changed files:

- `gk-core/scripts/verification-boundaries.v1.json`
- `gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs`
- `tasks/reports/resume-00c-split-core-mapping-20260925.md`

No CI, generated/data, product, existing-test, or other path was edited.

## Exact commands and outputs

### RED reproduction before the registry re-key

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SplitCoreVerificationMappingTests" -v minimal
```

Relevant output before the fix:

```text
Expected: "core-area-activity-owners"
Actual:   "core-residual"
Failed FusionRpg.Guard.Tests.SplitCoreVerificationMappingTests.Planner_resolves_representative_split_core_files_to_area_owners_not_residual
Failed FusionRpg.Guard.Tests.SplitCoreVerificationMappingTests.Registry_maps_each_split_area_to_its_existing_narrow_owner_group
Failed!  - Failed: 2, Passed: 0, Skipped: 0, Total: 2
```

### JSON parse

```powershell
Get-Content gk-core/scripts/verification-boundaries.v1.json -Raw | ConvertFrom-Json | Out-Null; 'JSON parse: OK'
```

Output:

```text
JSON parse: OK
```

### Focused Guard regression

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SplitCoreVerificationMappingTests" -c Release -v minimal
```

Output:

```text
Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2, Duration: 12 s
```

### Registry integrity guard

```powershell
python gk-core/scripts/guard-verification-boundaries.py
```

Output:

```text
VERIFICATION BOUNDARY GUARD OK
```

### Path-owned verification

The required final planning command was run against both concrete executable paths:

```powershell
$changed = @('gk-core/scripts/verification-boundaries.v1.json','gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs'); .\scripts\verify-change.ps1 -Paths $changed -Session resume-00c-split-core-mapping-20260925 -PlanOnly -Format json
```

Relevant final output:

```text
gk-core/scripts/verification-boundaries.v1.json -> guard-verification-boundary-tests (focused)
gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs -> guard-verification-boundary-tests (focused)
test: guard guard.verification-boundaries
full evidence: CI/nightly/release
```

The full execution command was also run:

```powershell
$changed = @('gk-core/scripts/verification-boundaries.v1.json','gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs'); .\scripts\verify-change.ps1 -Paths $changed -Session resume-00c-split-core-mapping-20260925
```

A 900-second run passed the selected Guard verification set:

```text
Passed!  - Failed: 0, Passed: 63, Skipped: 0, Total: 63, Duration: 8 m 3 s
```

After a no-op cleanup of an unused test-record field, the same full command was rerun. The registry/test selection was unchanged, but the run encountered a pre-existing timeout in `VerificationBoundaryWorkflowTests.Planner_can_select_a_registered_deleted_path_without_reading_the_filesystem` after 2 minutes under concurrent worktree load:

```text
Failed FusionRpg.Guard.Tests.VerificationBoundaryWorkflowTests.Planner_can_select_a_registered_deleted_path_without_reading_the_filesystem [2 m]
verification-boundary script timed out
Failed!  - Failed: 1, Passed: 62, Skipped: 0, Total: 63
```

The isolated existing test was then run directly and passed:

```powershell
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Planner_can_select_a_registered_deleted_path_without_reading_the_filesystem" -c Release --no-restore -v minimal
```

Output:

```text
Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1, Duration: 2 m
```

This is an existing Guard verification test timeout/resource-contention issue, not a mapping assertion failure; the new regression, JSON parse, registry guard, and final plan all pass.

### Final hygiene

```powershell
git diff --check
```

Output: exit code `0`, no output.

```powershell
python scripts/session-boundary-check.py --session resume-00c-split-core-mapping-20260925
```

Relevant output:

```text
[session-boundary] clean for 'resume-00c-split-core-mapping-20260925'
```

## Open issues

- The final full `verify-change.ps1` rerun was not green because one existing Guard test exceeded its fixed 120-second child-process timeout under concurrent worktree load. The same selected set passed 63/63 in the prior full run, and the isolated timed-out test passed 1/1. No code outside this lane's allowed paths was changed to mask it.

## Next steps

- Manager review/acceptance should rerun the full path-owned verification in a less contended slot (or at the merged review SHA). No mapping or test change is indicated by the current evidence.
- Harvest the three allowed dirty files only; do not add generated/data, CI, or product changes.

<<<REPORT {"status":"partial","summary":"Re-keyed Activity, Delve, Expeditions, PassiveTree, Progression, Scope, and Vfx to their existing split-Core owner groups; added structural and real-planner regression coverage with an Events control. JSON, focused tests, registry guard, final plan, and a prior 63-test verify-change run pass. A final full verify-change rerun encountered a pre-existing concurrent-load timeout in one Guard workflow test.","changed_files":["gk-core/scripts/verification-boundaries.v1.json","gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs","tasks/reports/resume-00c-split-core-mapping-20260925.md"],"verification":[{"command":"Get-Content gk-core/scripts/verification-boundaries.v1.json -Raw | ConvertFrom-Json | Out-Null; 'JSON parse: OK'","result":"JSON parse: OK"},{"command":"dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter \"FullyQualifiedName~SplitCoreVerificationMappingTests\" -c Release -v minimal","result":"Passed: 2, Failed: 0"},{"command":".\\scripts\\guard-verification-boundaries.py","result":"VERIFICATION BOUNDARY GUARD OK"},{"command":"$changed = @('gk-core/scripts/verification-boundaries.v1.json','gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs'); .\\scripts\\verify-change.ps1 -Paths $changed --session resume-00c-split-core-mapping-20260925 --plan-only -Format json","result":"Both paths selected guard-verification-boundary-tests; focused guard.verification-boundaries check planned"},{"command":"$changed = @('gk-core/scripts/verification-boundaries.v1.json','gk-core/tests/FusionRpg.Guard.Tests/SplitCoreVerificationMappingTests.cs'); .\\scripts\\verify-change.ps1 -Paths $changed --session resume-00c-split-core-mapping-20260925","result":"Prior full run: Passed 63, Failed 0 in 8m3s; final rerun: Passed 62, Failed 1 due existing 2-minute child-process timeout under concurrent load"},{"command":"git diff --check","result":"Exit 0, no output"}],"open_issues":["Final full verify-change rerun needs a less contended manager/acceptance slot; no mapping assertion failed."]} REPORT>>>

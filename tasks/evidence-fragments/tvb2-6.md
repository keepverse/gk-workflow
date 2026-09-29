# TVB2.6 — `tests/**` enforced root (C1) + test-project completeness (C2)

| Criterion | Result |
|---|---|
| C1: `tests/**/*.cs` and `tools/*.Tests/**/*.cs` walked (excl. bin/obj/TestResults); unmatched fails `unmapped test source: <path>` | added to `guard-verification-boundaries.py` |
| C2: every `*.Tests.csproj` under `tests/`/`tools/` registered or exempt with a reason (guard-owned `$ExemptTestProjects` hashtable, not a JSON field) | added; initial exemption `FusionRpg.Injector.Tests` |
| Five project ids + fallbacks: `atomimporter`, `itemseedvalidator`, `filemove`, `passivetreerostergen` (+ pre-existing `e2e`) | added to `verification-boundaries.v1.json`, folding each tool tree in per the `lawncombatobserver-fallback`/`proveliveprobe-fallback` precedent |
| `test-substrate` guard on all five | done |
| Real registry: closed the six-root backlog in one change | before: 61 `unmapped test source` + 4 `test project not in registry`; after: `VERIFICATION BOUNDARY GUARD OK` |
| T1 (unmapped test source fails) | passed |
| T2 (unregistered non-exempt test project fails) | passed |
| T9 (real registry passes) | `Integrity_guard_passes_on_the_current_registry` passed |
| `software-architecture.md` §10, `testing-standard.md` §6 | one line / one sentence each, updated |

**Two real bugs found by this task's own tests, both fixed in this commit:**
1. `PlantGroupFixture` (T10/T11's fixture) plants `tests/FakeA/SomeTests.cs` and
   `tests/FakeB/SomeTests.cs` with no owner boundary. Once C1 enforces `tests/**`, `verify-change.ps1`'s
   delegated integrity check on that synthetic root started failing, breaking T10/T11 even though
   their own assertions were unrelated. Fixed by adding `fakea-tests-fallback` /
   `fakeb-tests-fallback` owner boundaries to the fixture's planted registry.
2. `scripts/lib/VerificationBoundaries.ps1`'s `Resolve-Owner` declared
   `[Parameter(Mandatory)][array]$OwnerBoundaries` with no `[AllowEmptyCollection()]` — a real
   PowerShell quirk where Mandatory rejects an empty array as if it were missing
   ("Cannot bind argument ... because it is an empty array"). T1's fixture (zero boundaries) was the
   first caller to pass an empty owner list and tripped it. Fixed by adding
   `[AllowEmptyCollection()]`. Also found and removed while in this function: the whole
   `Resolve-Owner` function was defined twice, verbatim, in the same file (a latent dupe from an
   earlier task) — deleted the second copy.

**Third real bug found and fixed:** the plan's own verify command names
`docs/architecture/software-architecture.md`, which had no owner boundary at all
(`VERIFICATION BOUNDARY MISSING`) — a pre-existing gap, unrelated to C1/C2, that the scoped verify
caught immediately. Fixed by adding `software-architecture-doc` (module, project `guard`, no guards),
mirroring the existing `testing-standard-doc` boundary exactly.

**Performance regression found and fixed before landing:** the first cut of C1's `tests/`/`tools/`
walk used `Get-ChildItem -Recurse | Where-Object` (post-filter), which — combined with the
**pre-existing, unrelated** `src/**` walk using the same unpruned pattern — pushed individual guard
invocations from a few seconds to 2-3.5 minutes, tripping several tests' 120s `ExternalProcess`
timeout (`Planner_selects_only_the_socket_group_...`, `Integrity_guard_passes_on_the_current_registry`,
`A_back_end_tool_tree_selects_its_own_boundary`). Root cause (confirmed via instrumented profiling,
not guesswork): recursing into every project's `bin`/`obj`/`TestResults` before filtering. Fixed with
a shared `Get-FilesPruned` helper (stack-based `[System.IO.Directory]::EnumerateFiles`/
`EnumerateDirectories`, skipping build-artifact directory names during traversal, never after) used
for **both** the gk-core/tests/tools walk (new) and the src walk (pre-existing, now also fixed since it was
the dominant cost — 74s of the measured total, vs ~19s for gk-core/tests/tools). Single real-registry guard
run: 2m45s-3m33s before -> 48s after. Also converted `$resolved`'s array `+=` to a
`List[object].Add()` (O(n^2) growth) while investigating, though the pruning was the dominant fix.

One test (`Planner_selects_only_the_socket_group_for_source_and_its_test`) still hit the 120s timeout
once in a full-class run under concurrent machine load (other sessions' processes); re-run in
isolation immediately after: 27s, passed. Re-ran the whole `VerificationBoundaryWorkflowTests` class
twice in a row per the determinism requirement: 36/36 both times (9.6 min once with the one
contention flake counted as a retry, 6m49s clean).

Final scoped verify (`docs/architecture/software-architecture.md`, `docs/contributing/testing-standard.md`,
`gk-core/scripts/guard-verification-boundaries.py`, `scripts/lib/VerificationBoundaries.ps1`,
`gk-core/scripts/verification-boundaries.v1.json`, `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs`):
`guard` project full run 467/467 (module-level doc boundaries run the whole project), focused
`guard.verification-boundaries` 36/36. Both green.

# TVB-F29 — `tools-audit-tests` had no CI step, so `CiPytestWiringTests` was red at the merged head

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the red, at the merged head | `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "FullyQualifiedName~CiPytestWiringTests"` (inside the wider run below) | `pytest project root(s) with no 'python -m pytest' CI step at that working-directory: .` — root `.` is `tools-audit-tests` | `tasks/evidence-fragments/tvb60-register-reverify-merged-head.md` |
| the project and its owner | `python -c "json.load(open('gk-core/scripts/verification-boundaries.v1.json'))['projects']['tools-audit-tests']"` | `{runner: pytest, root: ".", tests: "gk-core/tests/tools"}` (`:183`); boundary `pipeline-audit-scripts` (`:3325`) owns `gk-core/scripts/audit-program-pipeline.py` + `gk-core/scripts/fix-doc-citations.py` | this fragment |
| the merge introduced it | `git show 4f60fc741:gk-core/scripts/verification-boundaries.v1.json \| grep -c 'tools-audit-tests'` | **0** — the project is not in this lane's pre-merge head | this fragment |
| the suite the step runs is green | `python -m pytest gk-core/tests/tools -q -p no:cacheprovider` | `25 passed in 4.60s` (stdlib-only: `datetime`, `importlib`, `json`, `os`, `subprocess`, `sys`, `pathlib`) | this fragment |
| the fix, and the exit check `WorkflowExitCheckTests` requires | `dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release --filter "FullyQualifiedName~VerificationBoundary\|FullyQualifiedName~CoreTestProjectPolicy\|FullyQualifiedName~CiPytestWiringTests\|FullyQualifiedName~WorkflowExitCheckTests\|FullyQualifiedName~CiWiringGuardTests"` | `Passed! - Failed: 0, Passed: 74, Skipped: 0, Total: 74, Duration: 5 m 48 s` | this fragment |
| the registry is still valid | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | this fragment |

The step's `working-directory` must be exactly the project's `root` for `CiPytestWiringTests` to count it
(`gk-core/tests/FusionRpg.Guard.Tests/CiPytestWiringTests.cs:25`), so the new step says `working-directory: .`
literally. It sits after the seedsmith lockfile install, which is where `pytest` comes from for the
`gk-core/tools/tuning` step too.

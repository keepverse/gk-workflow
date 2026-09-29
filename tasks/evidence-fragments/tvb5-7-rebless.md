# TVB5.7 — re-bless at the merged head (lane `tvb59`)

TVB5.7's deliverable is tvb58's commit `1d0fb2eb`, already in this branch's base. This is a
read-only re-verification at the head, not a re-implementation.

| Acceptance | Command | Result |
|---|---|---|
| shared set moved once; residual imports it | `ls gk-core/tests/FusionRpg.Core.Tests.Shared/CoreTests.Shared.props` / `grep -c "CoreTests.Shared.props" gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj` | file present; **1** import in the residual csproj |
| `InternalsVisibleTo.CoreTests.cs` generated, one line per `coreInternals` project | `grep -c "InternalsVisibleTo" gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs` | **68** |
| ci.yml + release.yml pair, no BalanceGuard line | `grep -n "AchievementTitles" .github/workflows/ci.yml .github/workflows/release.yml` | one `dotnet test` line + its `if ($LASTEXITCODE -ne 0) { throw … }` in each (`ci.yml:150-151`, `release.yml:54-55`) |
| `test-fast.ps1` list | `grep -n "AchievementTitles" scripts/test-fast.ps1` | present at `:59` |
| registry: group member, project id, boundaries | `python -c "…"` over `gk-core/scripts/verification-boundaries.v1.json` | `core` group **12 members**; `core-achievementtitles` -> the new csproj; boundaries `core-achievementtitles`, `core-tests-shared` |
| W1–W6 green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~CoreTestProjectPolicyTests"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` |
| CiWiringGuardTests + WorkflowExitCheckTests green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~CiWiringGuardTests|FullyQualifiedName~WorkflowExitCheckTests"` | `Passed! - Failed: 0, Passed: 9, Skipped: 0, Total: 9` |
| the new project still passes | `dotnet test gk-core/tests/FusionRpg.Core.AchievementTitlesTuningTests.Tests -c Release` | `Passed! - Failed: 0, Passed: 15, Skipped: 0, Total: 15` |
| the residual is green with the 11 landed increments | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | `Passed! - Failed: 0, Passed: 12742, Skipped: 0, Total: 12742` (41 s) — the residual's count is down from the 14822 tvb57 recorded, which is the split's own reading: 11 projects have moved out |
| boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` |
| No commit | the deliverable is already committed as `1d0fb2eb`; a re-bless changes no code, so this fragment rides the next lane commit (`TVB5.8.k` or the lane's close) rather than making a bookkeeping-only commit | — |

## Not proved

- The `git diff -M --stat` pure-rename proof is tvb58's reading at the increment's own commit; not re-run
  here (a re-bless verifies the current state, and every moved file's bytes are its own commit's concern).
  The residual's 12742/0 above and the 15/15 of manifest project 1 are re-measured at this head.
- `verify-change.ps1 -Paths <19 moved/created paths> -Session tvb58` cannot be replayed from this
  lane: those paths are under `tests/**`, `FusionRpg.slnx` and `.github/workflows/**`, outside this
  lane's runner fence. The named Guard tests above are the achievable proof.

# TVB5.7 — first real increment: shared set + manifest project 1, with its wiring

One commit: the tool's own writes, the hand-edited wiring they invalidate, and the evidence.
Increment 1 of 68 (`gk-core/tests/core-test-projects.v1.json`, manifest order).

| Acceptance | Command | Result |
|---|---|---|
| `split --project <1> --apply` keeps the increment | `dotnet run --project gk-core/tools/FileMove -- split gk-core/tests/core-test-projects.v1.json --project FusionRpg.Core.AchievementTitlesTuningTests.Tests --apply` | `kept.` — build+test of the new project **15/15** and the residual **14822/0** under the default profile |
| shared set moved once; residual imports it | `cat gk-core/tests/FusionRpg.Core.Tests.Shared/CoreTests.Shared.props` | 5 package references (both paired elements included) + the 4 linked shared sources; residual csproj imports the props and keeps only what it still owns |
| `InternalsVisibleTo.CoreTests.cs` generated | `grep -c InternalsVisibleTo gk-core/src/FusionRpg.Core/InternalsVisibleTo.CoreTests.cs` | **68** — one line per manifest project with `coreInternals: true` (W4) |
| pure renames | `git diff -M --cached --stat` | the 5 moved files show `\| 0` — bytes unchanged |
| ci.yml + release.yml pair, residual last | `grep -n "FusionRpg.Core.AchievementTitles" .github/workflows/ci.yml .github/workflows/release.yml` | one `dotnet test` line + its `if ($LASTEXITCODE -ne 0) { throw … }` in each, above the residual line; **no BalanceGuard line** — the project holds no `Category=BalanceGuard` trait (W6) |
| `test-fast.ps1` `-AllDefault` list | `cat scripts/test-fast.ps1` | the new project added before the residual; no existing line removed |
| registry: group member, project id, fallbacks, no stale exact path | `python -c "…"` on `gk-core/scripts/verification-boundaries.v1.json` | `core` group gains the member; new `core-achievementtitles` id + `core-achievementtitles`/`core-tests-shared` owner boundaries; **no exact path needed rewriting** — no registry pattern names a file this increment moved |
| W1–W6 green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-build --filter "FullyQualifiedName~CoreTestProjectPolicyTests"` | **6 passed** (W1, W2, W3, W4, W5, W6) |
| CiWiringGuardTests + WorkflowExitCheckTests green | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-build --filter "FullyQualifiedName~CiWiringGuardTests\|FullyQualifiedName~WorkflowExitCheckTests"` | **9 passed** |
| boundary guard | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (**50 s**, timed) |
| CI-tier guards | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | exit 0, all gating guards 0 |
| path-owned verification | `.\scripts\verify-change.ps1 -Paths <19 paths> -DeletedPaths <5 moved files> -Session tvb58` | exit 0 for every check; one `guard.verification-boundaries` case flaked as `verification-boundary script timed out` (TVB-F3, see below) and passed in the same session's isolated run |
| doc citations re-anchored | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` | exit 0 — 8 D3 + 2 D2 HIGH findings the move created, all 5 documents re-anchored to `…Shared/` and to the residual csproj's new line numbers |

Two tool defects this increment exposed were fixed in their own commits (see `tvb5-7-tool-hygiene.md`
and `tvb5-7-zero-test-gate.md`); the registry also gained mappings for two paths the brief required
verified and the registry did not own (`scripts/test-fast.ps1` → the boundary-test boundary;
`FusionRpg.slnx` → the tool whose tests define its shape). Known cosmetic residue: removing every
`PackageReference` leaves an empty `<ItemGroup>` in the residual csproj.

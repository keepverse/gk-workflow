# TVB1.4 — CI adoption: `ci.yml` Data.Tests line → sharded runner (E4) + H-T5

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ci.yml`'s Data.Tests line replaced with exactly the spec's two lines | `grep -n "test-sharded.ps1" .github/workflows/ci.yml` | `.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` + exit check, line 152-153 | `.github/workflows/ci.yml` |
| Leak-alarm re-run untouched; `release.yml` untouched; no `--filter` added | `grep` both files | leak-alarm still a plain `dotnet test ... --no-build`; `release.yml:52-53` unchanged; only pre-existing BalanceGuard line matches `dotnet test.*--filter` | both workflow files |
| H-T5 green (line + next-line exit check, carries `guard.workflows`) | `dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestShardManifestTests"` | 18/18 passed (incl. 3 new H-T5 facts/falsifiers) | `TestShardManifestTests.cs` |
| `WorkflowExitCheckTests` still green against the new `ci.yml` text | same run, filtered to `WorkflowExitCheckTests` | 4/4 passed | console |
| `CiWiringGuardTests` unaffected (path substring still present) | same run, filtered to `CiWiringGuardTests` | 5/5 passed | console |
| Scoped verify | `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs -Session summoner-convergence-lane-d2-20260919` | `guard.workflows`: 14/14; `guard.test-shards`: 10/10 | plan resolved `ci-workflows` + `test-shards-guard` |

First CI run after this commit is CI/nightly/release-owned evidence, not reproducible locally
(AGENTS.md verification boundary); the local scoped checks above are this session's full evidence.

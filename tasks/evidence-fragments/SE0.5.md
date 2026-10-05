# SE0.5 — CI cutover

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| the "Boundary guards" step is one `run-guards.ps1 -Tier ci` call | read `.github/workflows/ci.yml:230-239` | the eight hand-written calls and the inline `$seedRange` block are replaced by the one call plus its exit check | .github/workflows/ci.yml |
| the `guard-generated-seed` range moves into registry `args` | read `gk-core/scripts/enforcement-registry.v1.json:95-108` | the row carries `"args": { "ci": ["-Range", "{ciRange}"] }` | gk-core/scripts/enforcement-registry.v1.json |
| the integrity step stays separate with its comment | read `.github/workflows/ci.yml:241-249` | "Verification-boundary integrity" and its comment are unchanged | — |
| R5 post-runner: CI invokes the runner and hand-wires no guard beside it except `ciEntry: own-step` | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~EnforcementRegistry\|FullyQualifiedName~GuardRunner"` | `Passed!  - Failed: 0, Passed: 25, Skipped: 0, Total: 25`; two new R5 falsifiers (hand-wired guard, ci that never calls the runner) green | gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs |
| the runner is green on the real tree at tier ci | `.\scripts\run-guards.ps1 -Tier ci` | exit 0 (8 guards, 0 red; `generated-seed` now receives `-Range HEAD~1..HEAD`) | scripts/run-guards.ps1 |
| verify-change resolves both changed paths | `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml,gk-core/scripts/enforcement-registry.v1.json -Session summoner-convergence-lane-d-20260919 -PlanOnly -Format json` + `guard-verification-boundaries.py` | exit 0 → `ci-workflows` and `enforcement-registry` (both focused); integrity guard OK | — |
| one real CI run green with the summary table in the log | — | not_run — CI is the orchestrator's to observe; locally the same command exits 0 with the table printed | — |

# SE0.4 — scripts/run-guards.ps1 plus GuardRunnerTests

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| child process per guard; runs all, then fails; summary table | `.\scripts\run-guards.ps1 -Tier ci` | exit 0; 8 guards run, 0 red; table `id tier status exit s`; the own-step row `verification-boundaries` is skipped | scripts/run-guards.ps1 |
| no-masking: a red guard does not stop a later guard | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~GuardRunner"` | `Passed!  - Failed: 0, Passed: 6, Skipped: 0, Total: 6`; `A_red_gating_guard_does_not_stop_a_later_guard` asserts the next guard's marker file exists | gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs |
| an `exit 3` guard does not stop the next | same run | `A_guard_that_exits_three_does_not_stop_the_next` green | GuardRunnerTests.cs |
| backlog guards never fail and print under `BACKLOG` | same run | `A_red_backlog_guard_reports_under_BACKLOG_and_never_fails_the_run` green (exit 0, `BACKLOG` printed) | GuardRunnerTests.cs |
| unknown `-Only` id throws | same run | `An_unknown_Only_id_throws` green (non-zero exit, "unknown guard") | GuardRunnerTests.cs |
| `-Only` on a backlog guard reports and never fails | same run | `An_Only_backlog_guard_reports_and_never_fails` green (exit 0, `BACKLOG`) | GuardRunnerTests.cs |
| registry `args` with `{ciRange}` substitution | same run | `CiRange_is_substituted_from_the_registry_and_dropped_with_no_parent` green — `-Range HEAD~1..HEAD` when given, the pair dropped with no parent commit | GuardRunnerTests.cs |
| the runner's own path is mapped | `.\scripts\verify-change.ps1 -Paths scripts/run-guards.ps1,gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs -Session summoner-convergence-lane-d-20260919 -PlanOnly -Format json` + `guard-verification-boundaries.py` | exit 0 → both paths `guard-runner (focused)`; integrity guard OK | gk-core/scripts/verification-boundaries.v1.json |

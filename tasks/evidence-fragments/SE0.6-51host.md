# SE0.6 (5.1 host) — the runner's verdict is the exit code, never a stderr write

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| the runner completes under Windows PowerShell 5.1 | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run-guards.ps1 -Tier local -IncludeBacklog -Skip game-profile` | exit 0; `GUARDS OK - 18 guard(s) run, 0 red` (was: aborted mid-batch on the commit-policy guard's stderr) | scripts/run-guards.ps1 |
| a guard that writes to stderr does not abort the batch (5.1) | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~GuardRunner"` | `Passed!  - Failed: 0, Passed: 8, Skipped: 0, Total: 8`; `Under_windows_power_shell_a_guard_that_writes_to_stderr_does_not_abort_the_batch` green — the guard AFTER the stderr writer ran | gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs |
| a red guard still fails the run and is named (5.1) | same run | `Under_windows_power_shell_a_red_guard_still_fails_the_run_and_is_named` green (non-zero exit, `only-red` named) | gk-core/tests/FusionRpg.Guard.Tests/GuardRunnerTests.cs |
| mechanism | the child call is wrapped in a scoped `$ErrorActionPreference = 'Continue'` with `2> <per-guard stderr log>`; pass/fail comes only from `$LASTEXITCODE`; the log is echoed when the guard fails | — | scripts/run-guards.ps1 |

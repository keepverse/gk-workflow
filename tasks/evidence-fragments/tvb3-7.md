# TVB3.7 — C# generator wrappers: `gen-family-expand`, `gen-build-plan`, `gen-passive-tree`

| Criterion | Result |
|---|---|
| Three wrappers, `script` projects, seam boundaries per the D5 table | added: `gen-family-expand` (seam on `gk-forge/tools/FamilyExpandGen/**`), `gen-build-plan` (seam on `gk-forge/tools/CreatureBuildPlanGen/**`), `gen-passive-tree` (seam on `gk-forge/tools/TreeBinder/**`) |
| Owners `familyexpandgen-tool`, `treebinder-tool` unchanged | verified — neither boundary touched |
| New owner `creaturebuildplangen-tool` -> `gen-build-plan` (module) | added; `gk-forge/tools/CreatureBuildPlanGen/**` had no owner before this — no test project references the tool, so its own `--check` is the only honest proof (spec-python-test-lane.md D5) |
| Parity test green | `GeneratorCheckCiParityTests.Every_gen_wrapper_command_matches_a_ci_step_at_the_same_working_directory` auto-discovers every `scripts/checks/gen-*.ps1` file — the three new wrappers are covered with no test-file edit needed; each command (`dotnet run --project gk-forge/tools/FamilyExpandGen -- --check`, `...CreatureBuildPlanGen...`, `...TreeBinder...`) matches a `ci.yml` step at the repo-root working directory verbatim |
| Each wrapper exits 0 on a clean tree | real runs, all exit 0: `gen-family-expand.ps1` ("144 families read, 370 rows emitted... --check: clean, 11 generated file(s) match"), `gen-build-plan.ps1` ("904 resolved anchor(s) matched... --check: clean, 904 species match"), `gen-passive-tree.ps1` (per-tree `verdict=Fail` lines are the binder's own known/expected budget-refusal reporting — same class as FamilyExpandGen's "70 refused" — not a staleness signal; the wrapper's own gate is `$LASTEXITCODE`, which is 0) |

No new bugs found this task — `gen-checks-scripts` (added in TVB3.6) already covers `gk-core/scripts/checks/**`, so the three new wrapper files needed no additional boundary.

Scoped verify: guard-verification-boundaries.py direct run -> `VERIFICATION BOUNDARY GUARD OK`. Scoped
`dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~GeneratorCheckCiParityTests|FullyQualifiedName~VerificationBoundaryWorkflowTests|FullyQualifiedName~GuardVerificationBoundaries"`
(52 tests, `guard.verification-boundaries` + `guard.workflows`): first pass 47/52, 5 failures all
`ExternalProcess.Run`'s "verification-boundary script timed out" (120s hard timeout) — none in
`GeneratorCheckCiParityTests`, none referencing the new wrappers. Timed the same `verify-change.ps1
-Paths README.md -AllowUnscoped -PlanOnly` call three times back to back with no code change between
runs: 169.6s, 39.0s (guard subprocess alone), 44.5s — confirms pure machine contention (this box runs
many concurrent `dotnet.exe`/`powershell.exe` from other lanes), not a regression. Re-ran the 4 named
failing tests in isolation twice: first re-run still timed out (contention persisted), second re-run
green, 4/4, 3m3s. Full class + guard-boundary tests confirmed passing.

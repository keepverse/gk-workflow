# TVB0.3 — gk-core/tools/tuning pytest step in ci.yml (E2)

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| step text from spec-python-test-lane.md §CI inserted verbatim between "Install seedsmith from the lockfile" and "Item seed reachability (seedsmith)" | read `.github/workflows/ci.yml:322-331` | the four spec lines (`- name: gk-core/tools/tuning own tests …`, `shell: pwsh`, `working-directory: gk-core/tools/tuning`, the two `run` lines) sit between the lockfile step (ends :321) and reachability (:331) | .github/workflows/ci.yml |
| not in release.yml | `git status --porcelain -- .github/workflows` | ` M .github/workflows/ci.yml` only | — |
| WorkflowExitCheckTests green (the new `python -m pytest` line has its exit check) | `.\scripts\verify-change.ps1 -Paths .github/workflows/ci.yml -Session summoner-convergence-lane-d-20260919` | exit 0; `Passed!  - Failed: 0, Passed: 7, Skipped: 0, Total: 7` | — |
| the step is green on its first CI run | `python -m pytest . -q -p no:cacheprovider` (cwd `gk-core/tools/tuning`) — the step's own command | `27 passed, 3 subtests passed in 0.26s`; the first CI run itself is the orchestrator's to observe | — |

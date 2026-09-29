# SE1.2 — Commit policy accepts GitHub web merges, narrowly — **retired, nothing to build**

Owner ruling (2026-09-19, commit `6b9f6d21`): the whole git gate is retired — `scripts/commit-tool/`
(the `repo-git` MCP server, `validate.py`, `check_history.py`, `policy.json`, templates), `.githooks`,
the shell blockers, the CI commit-tool step **and the `commit-policy` guard itself** are removed, and
`pr-commit-attribution` carries an `unguardableReason` instead of a guard. The merged todo marks SE1.2
`RETIRED 2026-09-19: ... there is no commit policy left to extend. Nothing to build.`

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| the tool this task would extend no longer exists | `ls scripts/commit-tool` | only stale `__pycache__/` remains (no `policy.json`, `validate.py`, `check_history.py`) | — |
| the guard it would flip is gone, not merely unregistered | `ls scripts/guard-commit-policy.ps1` | `No such file or directory`; `ls scripts/guard-*.ps1` = 17 files, none of them it | — |
| the registry keeps the retirement | read `gk-core/scripts/enforcement-registry.v1.json:160` | no `commit-policy` row; `pr-commit-attribution` = `"guards": []` + the 2026-09-19 retirement reason | gk-core/scripts/enforcement-registry.v1.json |
| the retirement already documents itself where the task's acceptance points | read `docs/architecture/solid-enforcement/spec-commit-policy-green.md:3` | the spec opens with the RETIRED banner naming the same removals | docs/architecture/solid-enforcement/spec-commit-policy-green.md |
| the stale register row this task's module owned is struck | `dotnet test tests\FusionRpg.Guard.Tests\FusionRpg.Guard.Tests.csproj -c Release --verbosity minimal --filter "FullyQualifiedName~StubRegister"` | `Passed!  - Failed: 0, Passed: 7, Skipped: 0, Total: 7`; `SR-23` reads `~~SR-23~~` + `6b9f6d21` (struck in `b1ffa3d0`, not in this task) | docs/architecture/stub-register.md |

**No commit: the deliverable is retired by owner ruling — there is no commit policy, no guard and no
alias/`allowedMergeCommitters` surface left to extend; every acceptance item is either moot or already
satisfied by `6b9f6d21`.**

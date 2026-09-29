# TVB-F13 — the Guard suite at the merged head: 1 failed / 579 passed / 580 total

Lane `tvb58`, merged head `386a29c4` (this branch with `features/mega-merge` `30c585de` merged in, so the
walker fix `6bdd696c`/`GuardWiring.SafeFiles`, the boundaries row `8d26f137`, the session-boundary fix
`733ef458` and the anchors' verify path `26fc765` are all present).

```
dotnet test gk-core/tests/FusionRpg.Guard.Tests/FusionRpg.Guard.Tests.csproj -c Release
-> Failed!  - Failed: 1, Passed: 579, Skipped: 0, Total: 580, Duration: 6 m 40 s
```

| # | Red at the pre-fix head | At this head | Evidence |
|---|---|---|---|
| 1 | `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` | **still RED** — the only failure | `Failed ... [3 ms]`; current `02B04A25…` vs pinned `52F843…` |
| 2 | `SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously` | **GREEN** | fixed on this branch by `31df0398`; focused run 1 passed / 0 failed, and it passed inside this 580-test run |
| 3 | `CiWiringGuardTests.Every_tools_test_project_is_wired_and_exit_checked` | **GREEN** | the manager's walker fix; focused 3/3 with W3 + drain (`tvb-f2-drain.md`) |
| 4 | `CoreTestProjectPolicyTests.W3_no_test_project_references_another_test_project` | **GREEN** | same measurement |
| — | `VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry` | **GREEN** (did not reproduce) | the two timeout cases are load-fragile; the full guard was green standalone at 37.5 s in the same session |
| — | `VerificationBoundaryWorkflowTests.P6_the_real_registry_resolves_seedsmith_and_tuning` | **GREEN** (did not reproduce) | same |

**CAI-guard-1 is BLOCKED for this lane.** The pipeline hook refused
`gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs` a **third** time after the merge —
*"Blocked by the orchestrator pipeline guard: protected pipeline file (guards, verify, ledger script,
hooks, CI)"* — so the `--allow-protected` grant this row and CAI-guard-1 both name is not in effect at this
lane's edit boundary. The exact two-line change (hash + the comment's re-pin date/cause) is written into
CAI-guard-1's row in `tasks/combat-ai-todo.md`, so whoever holds the file can clear the single remaining red
without re-deriving anything.

**NOT proved**: that the two `VerificationBoundaryWorkflowTests` cases are *reliably* green — they are
load-fragile (TVB-F2/TVB-F4) and this run happened while the machine was quiet enough; a repeat on a loaded
machine can time them out again. Nothing else in the suite was left unattributed: every failure in this run
is named above.

# TVB — the Guard-suite baseline at the integration head (2026-09-21)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The Guard suite's failures at the integration head are named, so a lane's reds can be separated into pre-existing vs introduced | `dotnet test gk-core/tests/FusionRpg.Guard.Tests` (detached job `b6712875b`, `D:/tmp/guard-head.ps1`) | `Failed: 7, Passed: 573, Total: 580, Duration: 11 m 56 s` at `HEAD=48fd754e`, `dirty paths=0` | `.pi/tasks/session-65144-65144/b6712875b.output` |

## The seven failing tests at the integration head

| Failing test | Owning row / program |
|---|---|
| `CiWiringGuardTests.Every_tools_test_project_is_wired_and_exit_checked` | TVB-F1 (`tasks/test-verification-boundary-todo.md`) |
| `CoreTestProjectPolicyTests.W3_no_test_project_references_another_test_project` | TVB-F1 |
| `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` | CAI-guard-1 — CAI1.12 moved the baseline deliberately; the re-pin rides `tvb58` by executor ruling |
| `SubprocessPipeDrainGuardTests.No_test_file_reads_stdout_then_stderr_synchronously` | TVB-F2 — first half fixed by `tvb58` at `31df0398` (`gk-core/tests/FusionRpg.FileMove.Tests` helper drains both pipes concurrently) |
| `TuningRevisionLiteralGuardTests.No_reader_names_a_sockets_revision_literal` | `ssh27` (seg 10 gave it this red; its guard green at `0dc4b307`) — **CLEARED 2026-09-21 by `e99242c4`** |
| `VerificationBoundaryWorkflowTests.Integrity_guard_passes_on_the_current_registry` | TVB-F1 |
| `VerificationBoundaryWorkflowTests.P6_the_real_registry_resolves_seedsmith_and_tuning` | TVB-F1 — both of these pass when re-run alone; the row records them as a fixed subprocess timeout under machine load, not a registry defect |

## How this is used

`cai-sink`'s acceptance ran the same suite at its reviewed tip `e37a9f58` and reported
`Failed: 4, Passed: 576`. Every one of those four is a member of the set above, so the lane introduced
none of them; the manager merged it as `04da1747` on that attribution. `test-verification-boundary`
owns the rows that clear them.

**Cleared since the baseline, 1 of 7.** `ssh27` read the `TuningRevisionLiteral` failure as a guard
*coverage* defect (the filter is 2/2 green at the merged head and no committed reader names a literal)
and reported itself blocked because `gk-core/tests/FusionRpg.Guard.Tests/**` is a protected path outside its
fence. Confirmed at HEAD and fixed on the manager's own plane (guards): the failure was
`System.UnauthorizedAccessException: Access to the path 'tools/seedsmith/.tmp-seedsmith-pytest-audit'
is denied` thrown from `Directory.EnumerateFiles` at `TuningRevisionLiteralGuardTests.cs:52` — a
filesystem permission fact reddening a guard whose subject is source text. `e99242c4` walks
explicitly and skips what it cannot open; the filter is 2/2. Six of the seven remain, all in
`test-verification-boundary`'s rows plus CAI-guard-1's re-pin.

## NOT proved

- **Per-test attribution at the lane tip.** The acceptance log's name extraction printed an empty
  `=== FAILURES: guard tests ===` section, so the four names at `e37a9f58` were inferred from the
  seven at the head, not read. The inference is safe only because `4 + 3 = 7` and the head set is
  stable, and it is stated here rather than presented as a measurement.
- **Stability of the two `VerificationBoundaryWorkflowTests` failures.** They are load-sensitive; the
  baseline does not establish how often they fire. That belongs to whichever lane takes TVB-F2.
- **The three Core suite reds** (item/atom facts) are a different project and are out of this
  fragment's scope; they are registered as `knownRed` by `tvb58`.

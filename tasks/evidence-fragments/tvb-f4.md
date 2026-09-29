# TVB-F4 — a completed revert no longer leaves its journal behind (and three stale findings closed)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the defect | read `gk-core/tools/FileMove/SplitExecutor.cs` | `Keep` deleted the journal directory, `Revert` never did — the auto-revert after a failed build/test left `<temp>/filemove-split-<guid>/`; `%TEMP%` held 47 of them | this fragment |
| the fix | `Revert` calls `Keep(journalPath)` when `result.Ok` | a COMPLETED revert deletes the journal directory; a BLOCKED revert keeps it (the exit-3 recovery path) | `gk-core/tools/FileMove/SplitExecutor.cs` |
| the pin | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests -c Release` | `Passed! - Failed: 0, Passed: 48, Skipped: 0, Total: 48` — 47 existing + `A_successful_revert_deletes_the_journal_directory` | `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` |
| F10 unchanged | same run | `F10_revert_stops_at_a_file_edited_after_apply_and_leaves_it_untouched` still asserts the journal stays on a blocked revert | — |
| TVB-F2 re-verified | registry read | `seedsmith-tests` is still `paths: ["gk-forge/tools/seedsmith/tests/**"]`, `project: "seedsmith"`, `selfSelect: true`, `level: focused` — closed as recorded | `gk-core/scripts/verification-boundaries.v1.json` |
| TVB-F5 audited | read of every runner chosen by a path/filter/trait in this program's surface | only the split gate can run zero tests silently; `test-fast.ps1`, `test-sharded.ps1` (H-T6 reads TRX and fails an empty NAMED shard) and `verify-change.ps1` either count or partition — no second instance | — |
| TVB-F19 already implemented | `VerificationBoundaryWorkflowTests.cs:121,131-148,154-169,206-210,175-198` | the row's four prepared steps are all in the file, pinned by `In_scope_file_search_prefers_a_code_file_but_accepts_a_documentation_fence`; the brief's Guard filter is 63/63 at `01e0dd525` | — |

Two rows stay open with their own reason, not "needs investigation": **TVB-F1** (a `web` boundary needs
an erratum ruling, because the runner vocabulary is closed at `dotnet|pytest|script`) and **TVB-F3**
(`Resolve-Owner` indexing; both scripts are pipeline-protected, so it needs a ruling or a lane grant).
**TVB-F17** is narrowed to its single remaining cause: option (a) needs a shared-set DRIFT entry point,
because every plan today is `isFirstIncrement == false` and A1 refuses an applied project, so no
`split --project <n> --apply` can carry it.

The A4 sentence in `docs/architecture/test-verification-boundary/spec-core-split-apply.md` ("deleted only
after a kept increment") is now narrower than the code; that file is outside this lane's allowed paths,
so the code's own doc comment records the widening instead.

# BCU0.5 — pipeline-audit-v2 B4 (stalled-todo + --stale-days + --strict)

Same commit as BCU0.3/BCU0.4 — see [BCU0.3.md](BCU0.3.md) for the shared pytest evidence.

`git_history()` is the one `git log` pass (subject+date per commit, newest-file-date per path);
`test_stale_days_threshold_moves_the_verdict`, `test_stalled_todo_suppressed_by_merged_session`,
`test_stalled_todo_suppressed_by_ledger_done_ids`, and `test_reconciled_banner_suppresses_both_...`
each isolate one suppression path. `--strict` proven by `test_fail_on_open_excludes_advisory_unless_strict`.

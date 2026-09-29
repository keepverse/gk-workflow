# NS3.2 — `NotificationPublisher`: durable first, then one ordered batch per save

| Criterion | Command | Result |
|---|---|---|
| repeat window drops a routine draft with subject+turn inside the window; Critical and subject-less drafts never dropped | `dotnet test tests\FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~Notifications.NotificationPublisherTests"` | `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6` (`A_routine_draft_inside_the_repeat_window_is_dropped_but_critical_and_subjectless_never_are`) |
| one `AppendNotificationTurn` call per publish; fake push sees rows+cursor already stored; a re-publish pushes nothing; two saves get separate batches to their own group, nothing merged | same run | `Durable_before_push_...`, `Publishing_the_same_drafts_twice_pushes_once`, `Drafts_for_two_saves_produce_two_batches_each_addressed_to_its_own_save` |
| batch order severity desc then seq asc, two input orders tested | same run | `Batch_order_is_severity_descending_then_seq_ascending_regardless_of_input_order` |
| a push that throws after append leaves rows+cursor; a re-run pushes nothing | same run | `A_push_that_throws_after_append_leaves_rows_and_cursor_and_a_rerun_pushes_nothing` |

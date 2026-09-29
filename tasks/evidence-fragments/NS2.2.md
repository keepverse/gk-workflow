# NS2.2 — Per-category retention prune and ledger ageing in the append's transaction

Built together with NS2.1: the spec's own `AppendNotificationTurn` is one transactional method
(schema §1, API §2) with no natural seam between "insert" and "prune+age" — splitting them into two
passes would mean writing and then immediately deleting the interim shape. Implemented and tested
as one unit; this task's own acceptance lines are covered by the same run.

| Criterion | Command | Result |
|---|---|---|
| each touched (save, category) keeps its newest `retainPerCategory` rows by seq, state ignored; 3-into-N=2 returns only 2 survivors | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~Notification"` | `Retention_keeps_the_newest_N_per_category_and_leaves_other_categories_untouched` green (asserts an unread row is the one pruned) |
| a pruned key still refused within `DedupKeyMemoryWorldTurns`; ledger rows aged out at `appendTurn - N` | same run | `Idempotency_holds_across_the_prune`, `Ledger_bound_a_key_is_gone_after_DedupKeyMemoryWorldTurns_plus_one` green |
| the retention-tail exemption comment is verbatim | code review | `RpgStore.Notifications.cs`'s prune block carries the CLAUDE.md-quoted comment word for word |
| `audit-magic-numbers.py --targets M1` shows nothing new | `python scripts\audit-magic-numbers.py --targets M1` | `total 0 finding(s)` |

# NS1.3 — Catalog v1 + tuning v1 + Core parsers

| Criterion | Command | Result |
|---|---|---|
| `notification-catalog.v1.json` (empty categories/promotions), `notification.v1.json` (100/3, working-values note) exist; empty catalog parses, every query answers unknown | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Notify"` | `Passed! - Failed: 0, Passed: 51, Skipped: 0, Total: 51` (includes `The_shipped_v1_file_parses...`, `An_empty_catalog_answers_unknown_for_any_id`) |
| parser rejects duplicate id / unregistered promotion / critical not subset of toast / empty messageKeys / row carrying channel or severity | same run | `Duplicate_category_id_is_rejected`, `A_promotion_naming_an_unregistered_id_is_rejected`, `A_critical_id_missing_from_toast_is_rejected`, `Empty_messageKeys_is_rejected`, `A_row_carrying_channel_is_rejected`, `A_row_carrying_severity_is_rejected` all green |
| missing tuning key throws naming the key (T5), no built-in default | same run | `Missing_retainPerCategory_throws_naming_the_key`, `Missing_repeatWindowWorldTurns_throws_naming_the_key` green |
| `audit-magic-numbers.py` sees no new M1/M2 in the notify parsers | `python scripts\audit-magic-numbers.py --domain notification` | `M1=0 M2=0 M3=0 M4=0` — `total 0 finding(s), 0 high` (the two new Core parsers hold no bare literals; both numbers come from the parsed tuning file) |
| process-wide static Hub determinism (extra rigor: two full runs) | `dotnet test tests\FusionRpg.Core.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` x2 | run 1: `Passed! ... Passed: 14310`; run 2: `Passed! ... Passed: 14310` - identical, 0 failed both times |

`NotificationCatalogHub`/`NotificationTuningHub` follow `ActionBaseTuningHub`'s exact shape
(Configure/throws-until-configured/IsConfigured/Reset); only this file's own two tests touch them,
each resets before and after, so no cross-test static-state race exists yet.

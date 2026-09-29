# NS5.5 — `publish.py`: `notification-catalog` domain with a row-append operation

| Criterion | Command | Result |
|---|---|---|
| `publish.py notification-catalog` can append a category row and set a `promotions.*` list, publishing `v{n+1}` from whatever the current version is, keeping the old file (T4) | `python -m pytest gk-core/tools/tuning/test_publish_notification_catalog.py -q` | `15 passed` |
| pytest covers append, promotions set, refusal of a row carrying `channel`/`severity` | same run | `test_appends_a_category_row`, `test_promote_toast_sets_the_whole_list`, `test_promote_critical_accepts_an_id_already_in_toast`, `test_refuses_a_channel_field`, `test_refuses_a_severity_field` all pass |
| whole domain, end to end: two categories added then promoted in ONE publish call, v1 stays on disk, refusal writes nothing | same run | `test_add_category_then_promote_in_one_call`, `test_a_row_carrying_channel_refuses_and_publishes_nothing` pass |
| no regression to sibling publish.py domains | `python -m pytest gk-core/tools/tuning/ -q` | `42 passed, 3 subtests passed` |

`--promote-critical` enforces critical-subset-of-toast against the CURRENT (possibly just-updated
in the same call) `promotions.toast`, so `--promote-toast` then `--promote-critical` in one
invocation works without a second publish round-trip — the shape NS5.6 needs.

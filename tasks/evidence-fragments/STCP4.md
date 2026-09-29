# STCP4 — the budget is measured before it bites

**Status: DONE.** All three rows hold now that the ST4.5 reading exists.

| Row | Requirement | State |
|---|---|---|
| 1a | The report is committed for the real imported catalog | **Green.** `docs/research/action-corpus/_budget-2026-09-19.json`, taken by the manager on the real published server at 7a1974ba (fresh publish + boot import, confirmed by `power_trigger_frequency` = 5 rows). 18 priced actions. Committed in `b0e06781`. |
| 1b | Its realized power matches the catalog check **by construction** | **Green.** ST4.1's planted violation is proven rather than assumed: with `PriceContainer` temporarily returning a different number, exactly the two agreement guards fail (`The_report_prices_exactly_as_an_independent_second_pricing_does`, `The_report_and_the_catalog_check_agree_on_where_the_budget_line_is`), and they pass again once it is restored. ST4.5c/e kept that property: `Compose` is `ComposeWithFindings(...).Power`, so naming findings cannot move the price. Evidence: `tasks/evidence-fragments/ST4.1.md`, `ST4.5e.md`. |
| 2 | `recommendedReferencePower` is stated, and the outliers above p90 are listed by id | **Green.** `recommendedReferencePower` = **1512**; the actions above the report's p90, by id: **`action.family.pea.002`** (rung 7) — every other rung's list is empty, rungs 1/4/10 because nearest-rank p90 equals max below ten actions and rungs 2/3/5/6/8/9 because they carry no content. The scalar's setter is additionally named: **`action.general.0004`** (`recommendedBy`, ST4.5f). The three unpriced actions are named and bounded by ST4.5e. |
| 3 | `publish.py --reprice-rung-power-budget … --mark-tuned` is tested and ready for ST5.2 | **Green.** ST4.4 done: the flag recomputes every row from its own `poolRolls`/`qPowerMilli` and `REF`, writes `_meta.referencePower`, and `--mark-tuned` is the only way to clear the untuned marker (`gk-core/tools/tuning/test_publish_reprice.py`). |

**Nothing here is a code gap, and nothing is left blocked.** Every producer STCP4 names exists and is
verified; the reading it waited on is committed, and `recommendedReferencePower` is stated above.

One reading-level observation recorded rather than fixed, because it belongs to ST5.2/ST5.3 and not to
this checkpoint: the report shows `powerBudgetMilli: null` and `aboveLoadedScalar: []` on every rung,
because production still loads `action-rungs.v1.json` (`Program.cs:256`), which predates the column. The
scalar is computed from `poolRolls`/`qPowerMilli`, which v1–v4 share, so the value ST5.2 publishes is
valid — but the column the check reads is not live until ST5.2 publishes v4 and ST5.3 proves the check
evaluates. That is the exact sequence H7 exists to keep atomic.

# BCU7.4 — actor-hud boss-tier + perf B2

Boss-tier: re-scoped, not built. ActorHudTier.Boss exists in the enum but Compose never assigns it,
and the Injector-side builder has no expedition/boss context or override cache for it (unlike the
real ActorHudMeterOverride/InjectorDerivedOverride precedents). Real multi-file Core+Injector task,
corrected the stale S-size claim in backlog-clear-todo.md Phase 9.

Perf B2: published from 4 raw baseline JSONs that already existed on disk (2026-08-20, never
written up). Factual table only -- one capture has an unexplained ~18.4s maxMs outlier, no doc ties
any -oN suffix to a specific change, so no causal story invented.

```
$ python scripts/audit-doc-citations.py --scope docs/research/perf/B2-baseline-published-2026-09-20.md --strict
0 HIGH
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clear-todo.md --strict
2 pre-existing HIGH, none in my hunk (545-570)
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH
```

# TVB2.7 — Orphan-trait reading in `-Report` (C6)

| Criterion | Result |
|---|---|
| `-Report` prints every `VerificationId` trait no boundary selects, grouped by project | added |
| Never a failure | `python gk-core/scripts/guard-verification-boundaries.py --report` exits 0 regardless |
| Nothing asserts its size (a reading) | no new test added — the spec's own T1-T15 table is closed and explicitly excludes a C6 case ("No test asserts how many files, projects, boundaries or orphans exist") |

Real-registry `-Report` run:

```
Orphan VerificationId traits (no boundary selects them): 10
  core: core.advanced-effect-clock, core.battle-mode-parity, core.kill-attribution,
        core.siege-estimator-parity, core.species-passive-atoms, core.species-term-compose,
        core.vocabulary-single-declaration
  data: data.action-budget-live, data.action-pricing
  server: server.lawn-quick-start
```

Matches map G12's description exactly: seven `core.*` orphans plus `server.lawn-quick-start`
(deliberately orphaned per the ideal, "R-TV2 execution"). The two `data.*` orphans are additional
real findings, printed as a reading only — nothing asserts or requires fixing them here.

Scoped verify: `.\scripts\verify-change.ps1 -Paths gk-core/scripts/guard-verification-boundaries.py --session summoner-convergence-lane-d2-20260919`
-> `guard.verification-boundaries` focused, 36/36 passed (6m54s).

# Manager follow-up acceptance — RS-F27 defeat-floor tightening

The RS-F27 worker continued after the first accepted SHA and tightened the conditional non-vacuity
check. Review that late delta separately at a clean exact SHA; do not amend the prior artifact.

## Allowed paths

- `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs`
- `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`
- `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md`
- `tasks/reports/resume-19-rpg-simulator-defeat-floor-acceptance-20260925.md`

No production code, generated data, CI, or unrelated simulator changes.

## Acceptance boundary

1. Confirm a sampled real `defeat` requires a ledger row whose `kind` is `player` and whose `reason`
   is `defeat`; a non-empty ledger containing only an unrelated row is not enough.
2. Confirm the test still reads real route payloads, accepts only the closed outcome vocabulary, and
   does not fabricate outcomes or pin a population.
3. Run the focused 20-sample measurement, scenario/host contracts, `guard-sim-fabrication.ps1`, the
   report citation audit, scoped verification, and a clean detached checkout at the new exact SHA.
4. Merge only the follow-up SHA and record the prior accepted SHA as superseded by this tightened
   test, while preserving the open deterministic victory/stalemate seam.

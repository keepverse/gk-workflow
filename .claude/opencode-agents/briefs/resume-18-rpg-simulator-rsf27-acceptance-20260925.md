# Manager acceptance review — RS-F27 progression-ledger measurement

Review the completed dirty output of `resume-13-rpg-simulator-rsf27-20260925` at a clean exact SHA.
Accept the measurement harness and legal-empty policy only; do not invent a deterministic
victory/stalemate seed seam or change production progression behavior.

## Allowed paths

- `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs`
- `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`
- `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md`
- `tasks/reports/resume-18-rpg-simulator-rsf27-acceptance-20260925.md`

No `RpgXpAwardMap` production change, generated data, CI, seedsmith, or unrelated simulator module.

## Acceptance boundary

1. Verify the heavy test uses fresh in-process hosts and normal FE-facing read-backs, accepts only
   the closed outcome vocabulary, and applies a non-vacuity floor only after a real `defeat`.
2. Verify the fixture notes document that empty victory/stalemate ledgers are legal, that the
   20-run sample was all defeat due to server-minted seeds, and that no population-count assertion
   or fabricated row was added.
3. Run scenario validation, the 20-sample measurement, focused Core XP-map/E2E contracts, path-owned
   PlanOnly, the actual scoped E2E boundary, and a clean detached checkout at the exact reviewed SHA.
4. Preserve the deterministic outcome-selection seam as an open owner decision.

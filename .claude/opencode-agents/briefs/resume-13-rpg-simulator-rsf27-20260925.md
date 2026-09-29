# RpgSim RS-F27 — measure progression-ledger non-vacuity

Answer the row's evidence question before changing an assertion. Measure repeated in-process scenario
runs across the outcome vocabulary, then either add a justified non-vacuity check or document that an
empty progression ledger is a legal outcome. Do not add a random `notEmpty` guard.

## Read first
- `gk-core/tools/RpgSim/scenario-format.md`
- `tasks/rpg-simulator-todo.md` RS-F27
- current first-session-forward scenario and RpgXpAwardMap

## Allowed paths
- `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs`
- `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json`
- existing `gk-core/tools/RpgSim/**` runner/read-back files only when required for the measurement
- focused `gk-core/tests/FusionRpg.E2E.Tests/**` scenario tests
- `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md`

No generated corpus, population-count assertion, CI, unrelated simulator modules, or fabricated rows.
Use real scenario read-backs only.

## Required behavior
1. Run enough deterministic in-process repetitions to cover victory/defeat/stalemate or document the
   exact limitation; record `read.progression.ledger` lengths and outcome sources.
2. If a non-vacuity floor is justified, encode the measured contract in the scenario/fixture notes or
   assertions without pinning a population count; if empty is legal, state the policy evidence in the
   scenario notes and report the decision boundary.
3. Keep the scenario format's read-back and closed-vocabulary rules intact.

## Verification/report
Run focused Core/E2E/RpgSim tests and path-owned `verify-change -PlanOnly` for every executable path.
Record commands, sample count/outcome distribution, exact files, open owner decision, and next steps.
Use only `opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, no external reads.

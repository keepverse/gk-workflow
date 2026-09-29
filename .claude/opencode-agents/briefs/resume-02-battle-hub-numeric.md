# Resume P1 02 — battle ActorHub and numeric integrity

## Goal

Close the confirmed battle P1s without creating a second composer: live derived updates must flow through ActorHub, higher-level damage observers must receive sink-retained damage, and reachable HP magnitudes must not narrow to int.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/architecture/actor-hub-ssot.md`
- `docs/architecture/effect-funnel.md`
- `docs/architecture/combat-damage-ssot.md`
- `docs/architecture/battle-engine-ssot.md`
- `docs/architecture/power/ssot-power-scale.md`
- the current battle state/effect/damage files and focused tests

## Allowed paths

- `gk-core/src/FusionRpg.Core/Battle/BattleDerivedModifierLedger.cs`
- `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`
- `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`
- `gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleDerivedModifierLedgerTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHubComposeTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectMathTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectHostTests.cs`

## Requirements

1. Remove the reachable private live derived-stat fold; contribute through the one ActorHub contract or consume Hub output. Do not add another composer.
2. Return/emit the actual sink-retained damage to higher-level observers while preserving the existing delta contract.
3. Remove the reachable long-to-int HP narrowing; use the repository's checked magnitude rules and preserve host-boundary exceptions only where explicitly allowed.
4. Add focused tests for overkill, live recomposition, observer damage, and the numeric boundary. Initial setup through BattleHubCompose must remain valid.
5. Do not change unrelated combat mechanics or tuning numbers.

## Evidence/report contract

Trace one reachable path and cite exact source/test lines. Report full SHA, changed files, exact commands/results, what was not proven, open questions, and next plan. Leave dirty for manager review; no commit/push/merge.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~BattleDerivedModifierLedgerTests|FullyQualifiedName~BattleHubComposeTests|FullyQualifiedName~BattleEffectMathTests|FullyQualifiedName~BattleEffectHostTests"`
- `python gk-core/scripts/audit-overflow.py`
- `git status --porcelain`
- `git rev-parse --short HEAD`

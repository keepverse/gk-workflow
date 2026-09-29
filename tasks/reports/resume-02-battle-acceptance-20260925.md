# Manager acceptance review — battle ActorHub and numeric integrity

**Source lane:** `resume-02-battle-hub-numeric-20260925` (worker result preserved; not merged directly)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-battle-hub-20260925`
**Status:** **PARTIAL until exact-SHA clean checkout; scoped code evidence is green**

## Change reviewed

- Live battle derived contributions are converted to bound atom rows and resolved through the existing `BattleHubCompose.Resolve` path. The compatibility fold is isolated to ledger tests; production installs the Hub resolver in `BattleRunState`.
- Damage observers receive the sink-retained signed amount through the optional retained-delta capability; the requested transport delta still goes through the Funnel unchanged.
- Reachable HP and per-mille calculations use checked/widened arithmetic, with the bounded host projection narrowed only after clamping.
- No second ActorHub composer, product tuning change, or generated-data change is present.

## Independent evidence

```text
dotnet test gk-core/tests/FusionRpg.Core.Tests
  --filter "FullyQualifiedName~BattleDerivedModifierLedgerTests|FullyQualifiedName~BattleHubComposeTests|FullyQualifiedName~BattleEffectMathTests|FullyQualifiedName~BattleEffectHostTests"
# 33 passed, 0 failed, 0 skipped; exit 0

python gk-core/scripts/audit-overflow.py
# A2=0, A3=0, A4=0, A5=0, A6=0; exit 0

scripts/guard-actor-hub.ps1
# ACTOR-HUB GUARD OK; exit 0
scripts/guard-single-writer.ps1
# SINGLE-WRITER GUARD OK; exit 0
scripts/guard-funnel-delta.ps1
# FUNNEL DELTA GUARD OK; exit 0

verify-change.ps1 -Paths <all eight concrete executable paths>
  -Session resume-02-battle-acceptance-20260925 -PlanOnly -Format json
# exit 0; selected the battle/effect/combat owners and focused guards
```

The concrete path-owned aggregate was attempted with a disk-backed log. It passed the selected Core project with `9749/9749` tests and the battle responsibility/Funnel guards, then exceeded the 20-minute command limit while entering the broad Data owner selection. The external log SHA-256 is `8A41EFCD258A1BE84EE428CB0D6669A666EC57251BB551F36B7A04FB62E1842F`. This is recorded as an incomplete aggregate, not a green result; the focused battle/numeric evidence above is the acceptance boundary.

The worker also reported an unrelated SQLite Error 14 in an aggregate Data test. No Data path is in this fence, and the failure was not independently reproduced before the manager timeout; it remains an open verification limitation.

## Remaining requirements

1. Commit the reviewed eight-file diff and this report at an exact SHA.
2. Run the focused tests, ActorHub/overflow/guard checks, and PlanOnly from a clean detached checkout.
3. Validate/write the exact-SHA artifact and merge only that SHA.
4. Keep live battle proof and the broad Data/Core aggregate as explicit later gates; neither is claimed here.

<<<REPORT {"status":"partial","summary":"Manager review confirms the battle draft routes live derived output through the existing ActorHub, reports retained damage without rewriting transport deltas, and removes reachable narrowing. Thirty-three focused tests, overflow audit, ActorHub/single-writer/Funnel guards, and path-owned PlanOnly passed; the broad path-owned aggregate timed out after 9749/9749 Core tests and is not treated as green. Exact-SHA clean-checkout acceptance remains.","changed_files":["gk-core/src/FusionRpg.Core/Battle/BattleDerivedModifierLedger.cs","gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs","gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs","gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs","gk-core/tests/FusionRpg.Core.Tests/Battle/BattleDerivedModifierLedgerTests.cs","gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHubComposeTests.cs","gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectMathTests.cs","gk-core/tests/FusionRpg.Core.Tests/Battle/BattleEffectHostTests.cs","tasks/reports/resume-02-battle-acceptance-20260925.md"],"verification":["33 focused battle tests passed","overflow audit clean with zero findings","ActorHub, single-writer, and Funnel guards passed","path-owned PlanOnly selected the intended owners and guards","path-owned aggregate passed 9749 Core tests before timing out in the broad Data owner; log SHA-256 8A41EFCD258A1BE84EE428CB0D6669A666EC57251BB551F36B7A04FB62E1842F"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","broad Data/Core aggregate did not reach a terminal result","worker-reported unrelated SQLite Error 14 remains unreproduced/open","no live battle proof"],"next_steps":["commit exact reviewed SHA","clean-checkout focused verification and artifact","merge exact SHA","run merged-head gate and live proof at the appropriate boundary"]} REPORT>>>

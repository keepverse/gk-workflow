# `CAI-reverify-09158294` — the program's landed slices re-verified at the post-merge head

Lane `combat-ai-3`, 2026-09-21. `features/mega-merge` was merged into this branch
(`git merge features/mega-merge` → fast-forward to **`09158294`**, 44 commits, clean, no conflicts; my
seven commits were already in it as `51b64520`). Every open row of this program is blocked on an external
dependency, so what a lane can still do is prove that the **landed half of each blocked row is still green
at the new head**. That is this fragment.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The program's main suite | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Ai"` | **4618 passed, 0 failed, 0 skipped** (4617 at the pre-merge head; the merge added one matching test) | — |
| Every blocked row's landed slice | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Stance\|FullyQualifiedName~Delve\|FullyQualifiedName~Lawn\|FullyQualifiedName~Container\|FullyQualifiedName~EffectiveRung"` | **5173 passed, 0 failed** — covers `StanceSeamTests` (CAI3.1), `DefenceActionStanceTests`/`…SlotTests`, `AuraRuntimeTests`, `DelveRolePolicyTests` (CAI3.4), `LawnBattleViewTests`/`LawnRelationChainTests`/`LawnDerivedCacheTests` (CAI4.1), the composite-container tests (CAI3.3) and `EffectiveRungResolverTests` (CAI4.4) | — |
| Battle goldens unmoved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | **14 passed, 0 failed** | — |
| The balance module | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests` | **210 passed, 0 failed** (includes `ActionScheduleMatchesCorePolicyTests` 3/0 from CAI2.3 slice 4) | — |
| CAI3.1's "unmodified" clause | `git diff --stat 28537b6d2^ HEAD -- $(git ls-files \| grep -E "StanceRuntime\.cs$\|PoiseLedger\.cs$\|Riposte\.cs$")` | **empty** — all three byte-unchanged since before the program's first commit | — |
| The `DESIGN-GATE.md:57` row has not gone stale | brace-counting member parse over `gk-core/src/FusionRpg.Core/**/*.cs` (11 enums) | **all 11 match**: `TargetSelector` 8, `AiTier` 2, `AiPlace` 4, `AiRole` 4, `AiRowCondition` 6, `AiCensusCondition` 5, `PersonalityAxis` 4, `AiActorClass` 2, `ScoreTerm` 7, `SelectionMode` 2, `Resolvability` 3. This is the exact failure the row warns about ("the atom row above has already gone stale four times"), and it held across 44 merged commits | `docs/DESIGN-GATE.md:57` |
| No dependency of a blocked row landed | existence probe of every file the 21 rows name | **none appeared**: `Injector/Effects/{LawnActorViewHost,AiInspectFeature,LawnCombatAiFeature}.cs`, `Core/Match/Ai/{LawnHeldActionSets,LawnCastPlan,LawnDecisionTrigger,LawnOrderQueue}.cs`, `Server/CombatAiProfileFiles.cs` all absent; `gk-core/data/tuning/` holds no `siege.v3.json` and no `lawn-perf-budget.v1.json`; `docs/research/combat-ai/` gained nothing; `AiTuning` still has its four members | — |
| The citation guard on this program's own docs | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | 23 documents, 1167 citations; `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0`. All 7 D1 are **LOW** and read as *proposed* files — the specs naming `LawnDecisionTrigger.cs`/`LawnDecisionBudget.cs`/`LawnCastTokenPool.cs` (CAI4.7's own new files), two filed test files, `lawn-combat-ai.v1.json` (a rejected alternative) and `mode-profiles.v1.json` (LW2.2's) | — |
| **This lane's own commits broke no citation** | `grep -rn "AiRowSelector\.cs:\|CoreIntentPolicy\.cs:\|LawnBattleView\.cs:" docs/architecture/combat-ai/ docs/architecture/combat-ai-ideal.md` | **exactly 1** hit: `spec-decision-perf.md:29` → `CoreIntentPolicy.cs:321`. `CAI-mask-1` changed no line count in that file (both edits were in place), so the citation points at the same line it did before; and that line is the `AiRowFacts` construction, not the `ScoredTarget` the prose names — **stale before this lane, not because of it**. `AiRowSelector.cs` (+18) and `LawnBattleView.cs` (+4) gained lines and have **zero** citations into them | — |
| The stale-citation sweep, sized | symbol-on-citing-line vs a ±30-line window, over the same 23 documents | **874 citations checked, 101 suspects**. Method: for each `X.cs:N` citation take every backticked identifier on the citing line and require one to appear within ±30 lines of `N` in `X`. The heuristic has a real false-positive rate (a line naming `BattleGoldenTests` is not a symbol in `BattleRunState.cs`), so 101 is an **upper bound on the queue, not a defect count** | — |

## Not proved

- **No row closed, and this fragment claims none.** All 21 blocked rows were re-read against the post-merge
  tree and every dependency is still absent, so each stays blocked on its named external — the ledger's
  re-triage lines and the todo's `Blocked re-triage` table are current as of `09158294`.
- **The 101-suspect sweep was NOT acted on.** Re-anchoring 101 citations is not one commit, and a
  re-anchor is only safe where the prose describes *current* behaviour: `CAI1.11`'s fragment already
  warned that several of these citations deliberately quote a **pre-fix defect** ("which re-anchoring
  would falsify"). It is filed as a sized row instead of guessed at.
- **No `verify-change.ps1` run appears here.** This commit changes no production or test path — it records
  runs — so there is nothing for the boundary command to select; the runs above are the evidence.

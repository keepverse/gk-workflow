# `CAI-merge-1` — merge `features/mega-merge` to `b79e28ff`, resolve the one conflict, and route its three guard reds

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The merge | `git merge features/mega-merge --no-edit` | 24 commits; **one conflict**, in this program's own `tasks/combat-ai-todo.md` (both sides appended rows at the end). Everything else auto-merged | `18968f7a` |
| The incoming rows are stale duplicates, **measured not assumed** | `git merge-base --is-ancestor 5f51d6fcd492 5fd0feba` | **true** — the ssh28 lane's observation head is an ancestor of the commit that fixed the finding, so the red was real when seen and the fix landed afterwards. The incoming text also reused the id `CAI-guard-2`, which this todo already carries, so those two rows are renamed `CAI-guard-4`/`CAI-guard-5` and closed as duplicates | `tasks/combat-ai-todo.md` |
| This program's own half of those findings is gone | `sed -n '84p;86,87p' gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs`; `sed -n '405p' gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs` | `const int DecisionScratchCapacity = 64;` read by both scratch lists at `:86-87`; the count assertion reads `Assert.Equal(cap, result.Count)` | — |
| …but the **guards are still red**, at the merged head, on someone else's new files | `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1`; `pwsh -NoProfile -File scripts/guard-population-pin.ps1` | magic-numbers **exit 1**, `M1=0  M2=1  M3=0  M4=1`, 2 findings (1 high), both at `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46`; population-pin **exit 1**, 1 finding at `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70` | — |
| The numbers were re-run rather than quoted | the two runs above vs `CAI-guard-4`/`CAI-guard-5`'s own text | my pre-merge run read `M1=M2=M3=M4=0` and population-pin `clean`; the merged head reads `M2=1  M4=1` and 1 population pin. **Both rows were corrected** to say so, instead of claiming a green guard | — |
| The new reds are routed to their owner | `grep -rln "ComboPricing" tasks/*-todo.md` | `tasks/strain-splice-host-todo.md` (plus its `spec-combo-budget.md`/`spec-tier-ladder.md`) → new section "Findings routed from `combat-ai`" with `SSH-route-1` and `SSH-route-2`, each carrying `file:line`, the cause read, the reproduce command and the verify | `tasks/strain-splice-host-todo.md` |
| No conflict marker survives | `grep -c "^<<<<<<<\|^=======$\|^>>>>>>>" tasks/combat-ai-todo.md` | **0** | — |
| No duplicate row ids | `grep -n "CAI-guard" tasks/combat-ai-todo.md` | `CAI-guard-1` open; `CAI-guard-2`, `CAI-guard-4`, `CAI-guard-5` closed — one id per row | — |
| My blocked rows' dependencies, re-probed after the merge | existence probe of all ten files the blocked rows name | **none landed**: no `LawnActorViewHost.cs`, no `AiInspectFeature.cs`, no `Core/Match/Ai/{LawnHeldActionSets,LawnCastPlan,LawnDecisionTrigger,LawnOrderQueue}.cs`, no `Server/CombatAiProfileFiles.cs`, no `LawnCombatAiFeature.cs`, no `lawn-perf-budget.v1.json`, no `siege.v3.json`; `AiTuning` still carries its four members | — |
| Working tree | `git status --short` | clean | — |

## Not proved

- **Neither routed red was fixed**, and correctly so: `gk-core/src/FusionRpg.Server/**` and
  `gk-core/tests/FusionRpg.Server.Tests/**` are both outside this lane's allowed paths. The routing is the
  deliverable, and the two rows name the decision each one needs rather than a unilateral remedy.
- **`run-guards.ps1 -Tier ci` was not re-run after the merge.** The two focused guards were, and they are
  the ones this program's acceptance names; the tier as a whole also carries the repo-wide
  `doc-citations` red that is not this program's.
- **The merge was not verified by a build or a test run.** It is a fast-forward-equivalent content merge
  with one todo conflict and no source conflict, and the merged tip is the integration branch's own
  reviewed head; a full build here would re-verify other lanes' work, not this change.
- **The 24 merged commits are not audited.** They are other programs' work arriving through the
  integration branch; the probe above covers only the dependency names this program's blocked rows use.

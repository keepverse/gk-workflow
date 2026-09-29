# `CAI-reverify-ab7dcc110` — the program's suite re-verified after a 56-commit merge that split the test project

Lane `combat-ai-3`. `features/mega-merge` advanced 56 commits (fast-forward to **`ab7dcc110`**; my seven
commits were already in it). Those 56 include a **test-project split**: 24 test files were renamed out of
`gk-core/tests/FusionRpg.Core.Tests/**` into new per-area projects (`Core.Commanders.Tests`, `Core.Diagnostics.Tests`,
`Core.Dungeon.Tests`, `Core.CombatFanoutTests.Tests`, nine `Core.Effect*.Tests`, …). A split can silently drop
coverage, so this fragment re-measures the program's own surface at the new head and audits the split itself.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Program surface, **by namespace** (precise, not a substring) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FusionRpg.Core.Tests.Actions."` / `…Battle.` / `…Delve.` | **Actions 833 / 0**, **Battle 1260 / 0**, **Delve 1684 / 0** — all passed, 0 failed, 0 skipped | — |
| The balance module | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests` | **210 passed / 0 failed** (includes the CAI2.3 parity test). The residual project's `…Balance.` namespace no longer exists — those files moved to that project long before this merge | — |
| H1: goldens byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver"` | **14 passed / 0 failed** | — |
| None of **this program's** test files moved | existence check of 8 named files under `gk-core/tests/FusionRpg.Core.Tests/` (`Actions/Ai/AiRowSelectorTests.cs`, `Actions/Ai/AiDecisionRingTests.cs`, `Actions/Ai/CoreIntentPolicyTests.cs`, `Actions/Ai/Lawn/LawnBattleViewTests.cs`, `Actions/StanceSeamTests.cs`, `Actions/EffectiveRungResolverTests.cs`, `Delve/Battle/DelveRolePolicyTests.cs`, `Battle/BattleGoldenTests.cs`) | **8 of 8 present** — the rename list (`git diff --name-status -M 2f43cd8c2..ab7dcc110 -- tests/`) contains **no** file under `Actions/`, `Battle/`, `Delve/` or `Balance/` | — |
| The split did not orphan anything | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~CoreTestProjectPolicy"` | **6 passed / 0 failed**, including **W1** (every core test csproj on disk is a manifest project or the residual) and **W5** (every existing core test project is wired in CI *and* release) | `gk-core/tests/FusionRpg.Guard.Tests/CoreTestProjectPolicyTests.cs` |
| Every new project is wired | `grep -c "<project>" FusionRpg.slnx .github/workflows/ci.yml` for the 8 sampled new projects | **slnx = 1 and ci.yml = 2 for every one** (`Core.CombatFanoutTests.Tests`, `Core.CombatHitEmitPolicyTests.Tests`, `Core.Commanders.Tests`, `Core.DamageFxPaletteTests.Tests`, `Core.Diagnostics.Tests`, `Core.Dungeon.Tests`, `Core.EffectClock.Tests`, `Core.EffectScenarioRunnerTests.Tests`) | — |
| The blocked rows' dependencies, re-probed | existence check of 16 files the blocked rows name | **none landed**: no `Injector/Effects/{LawnActorViewHost,AiInspectFeature,LawnCombatAiFeature}.cs`, no `Core/Match/Ai/{LawnHeldActionSets,LawnCastPlan,LawnDecisionTrigger,LawnDecisionBudget,LawnCastTokenPool,LawnOrderQueue,DirectOrderAdmission}.cs`, no `Server/{CombatAiProfileFiles,LawnOrderEndpoints}.cs`, no `gk-core/data/tuning/{lawn-perf-budget.v1,siege.v3,combat-ai.v2,combat-ai.v3}.json`; `AiTuning` still four members; `PerfProbe` still has no `AiDecide` | — |

## The one number that moved, and why it is not lost coverage

The fuzzy filters I had been quoting dropped across the merge: `~Ai` **4624 → 4613** and the landed-slice
filter **5175 → 5167**. A `~` filter is a **case-insensitive substring** match on the fully-qualified name, and
the 24 renamed files left the residual project, so any of their methods whose FQN happens to contain one of my
filter terms moved out of *that project's* run. Measured on the moved files:

- `~Ai` ("ai" anywhere): **6** methods in `DungeonTuningTests.cs`, **1** in `EffectPluginLifecycleTests.cs`,
  **2** in `NotificationCatalogCoherenceTests.cs` — words like `…_fails_…`, `…_available_…`, never the
  `Actions/Ai` namespaces this program owns.
- slice terms (`lawn|stance|delve|container|rung`): **1 + 1 + 4 + 7 + 3** across `CommanderRosterTests`,
  `ThirdCommanderOpenClosedTests`, `DungeonRegistryTests`, `DungeonTuningTests` and `EffectOfflineKitTests`.

So the delta is filter dynamics, not a coverage loss — and the three things that could actually hide a loss
were each checked: **W1** (no unrecognised project), **W5** (all wired), and the **namespace-scoped counts**
above, which are exact rather than substring-based.

## Not proved

- **The deltas are not reconciled to the test.** The filter is a substring match and the moved files are
  renames, so the arithmetic is approximate by construction; what is exact is W1/W5 and the
  namespace-scoped counts, and those are what the conclusion rests on.
- **No blocked row changed state.** Every dependency is still absent, so the 23 blocked rows stand exactly as
  the previous segment's re-triage left them, as does the CI-tier picture (`doc-citations` in other programs'
  docs, plus the two `SSH-route` reds on `strain-splice-host`'s new files).
- **No production file was touched this segment**, so there is nothing for `verify-change.ps1` to select; the
  runs above are the evidence.

# CAI1.11 — The router, cause B: trait decorators on every policy

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Reselect_and_declare_resolve_the_same_source_for_the_same_actor` (M5) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~TraitDecoratorTests"` | 3 passed, 0 failed | `gk-core/tests/FusionRpg.Core.Tests/Actions/TraitDecoratorTests.cs` |
| `Every_policy_sees_the_bloodthirsty_view_not_only_the_fallback` | same run | passes (a policy bound to `TraitAwareBattleView` reads the decorated `LiveActorKeysFor`; a non-applicable actor reads the raw order) | — |
| `A_loyal_redirect_is_applied_once_on_each_side_and_the_scorer_reads_the_redirected_target` | same run | passes (engine: `a -> b`, never chained to `c`, `RetargetFor` unredirected; scorer: the redirected target's facts flip the winner, control without the redirect does not) | — |
| Production reach: the decorator changes a real `BattleEngine.Resolve` siege decision | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAiLiveWiringTests"` | 3 passed, 0 failed — control (no trait) leaves the 33rd, cap-dropped candidate at 1 HP; `TraitIds = ["bloodthirsty"]` kills it | `SiegeAiLiveWiringTests.cs` |
| Named verification filter | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~IntentRouter\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~CoreIntentPolicy"` | 76 passed, 0 failed (was 75 before this commit) | — |
| Golden: one cause, nothing moved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Dominance\|Category=BalanceGuard"` | **36 passed, 0 failed** — no test re-blessed; predicted delta in `docs/architecture/combat-ai/predicted-delta-router-cause-b.md` | — |
| `guard-battle-responsibility.py` | `python gk-core/scripts/guard-battle-responsibility.py` | OK (19 mechanisms, 1555 files scanned), exit 0 | — |
| `guard-doc-citations.ps1 -Strict` | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0; 1679 documents, 24804 citations, 0 HIGH (D2 line-past-end 12, unchanged from HEAD) | — |
| `verify-change.ps1` | `-Paths <9 code/test paths> -Session combat-ai-build-20260920` | selected `core-fallback`/`core-tests-fallback` + `battle-effect-math` focused + battle-responsibility/funnel-delta guards → `FusionRpg.Core.Tests`: **14837 passed, 4 failed**. All 4 are Items/Atoms corpus tests, unrelated to this change and pre-existing at `e0f1375d`: `SocketOperationsTests` requires `data/seed/items/socket-words/sockwords.json`, which `git cat-file -e HEAD:...` proves is **not tracked at HEAD**, and `git status --porcelain data/` is empty, so none of the drift is local. | — |

## Deviations, stated rather than silent

1. **The seam is `IBattleView.LiveActorKeysFor`, a default interface member.** The ruling said "every
   `IBattleView` method already takes an `actorKey`"; `LiveActorKeys` is a property and takes none, and
   `bloodthirsty`'s whole effect is a reordering of exactly that member. A policy that binds ONE view
   for its life (`SiegeAiIntentSource`, persistent `RetargetLedger`/`BattleTrace`) can therefore only
   reach a viewer-relative decoration through a viewer-relative read. The new member's default is the
   identity, so no existing implementer or test fake changed and every unwrapped view is byte-identical.
2. **`IntentRouter.RetargetFor` does not apply `EffectiveTargetOf`.** `TimelineDispatch.Reselect` never
   carried the `loyal` redirect; adding it there would be a second unannounced behaviour change inside
   this one cause. Recorded in the method's own doc comment.
3. **The predicted-delta note lives at `docs/architecture/combat-ai/predicted-delta-router-cause-b.md`,
   not the todo's `docs/research/combat-ai/…`.** `docs/research/**` is outside this session's allowed
   paths.
4. **Pre-CAI1.11 `BasicAttack.cs` line anchors in several specs are now semantically stale** (the file
   grew 521 → 609 lines) and were NOT re-anchored: the citation guard is bounds-only, so it reports 0
   HIGH and names none of them, and the affected prose describes the *pre-fix defect* (`combat-ai-ideal.md:142`,
   `spec-intent-router.md:25-27`), which re-anchoring would falsify. Recorded as a finding, not silently
   left.
5. **`verify-change.ps1` selected the full `FusionRpg.Core.Tests` module fallback** (`core-fallback` +
   `core-tests-fallback`), not a focused group — this repo's registry has no finer mapping for
   `Core/Actions/**`. Its 4 failures are the pre-existing Items/Atoms corpus drift named above; the three
   named verification filters the brief specifies are all green, and the new tests are in them.

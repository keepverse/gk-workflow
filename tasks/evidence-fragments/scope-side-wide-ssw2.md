# scope-side-wide SSW2 — the aura asks for the plant side, and the grant store answers it

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A patron-shaped grant reaches plants of any type id, through the REAL pipeline (real `InMemoryEffectGrantStore` + compiled `AtomCompiler` def + `GrantedDerivedAtomReader`) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"` | PASS — 3037/3037, 0 failed (+15 vs the 3022 pre-change baseline); `A_patron_shaped_grant_reaches_plant_reads_of_any_type_id` (typeIds 0/3/999, `combat.power.fire` 47.0) | `tests/FusionRpg.Core.Tests/Effects/PatronAuraScopeTests.cs` |
| ⭐ It does NOT apply on the zombie side (the PT7 case) | same run | PASS — `A_patron_shaped_grant_does_not_apply_on_the_zombie_side`; composed channel 47 on plant, **0** on zombie via `AtomDerivedSubsystem`+`ActorHub` | same |
| Non-vacuous: the same read DOES reach a zombie for a `match` grant | same run | PASS — `A_match_scoped_grant_of_the_same_effect_still_reaches_both_sides` | same |
| The plugin stamps the side-wide key + ownerKind | same run | PASS — `The_patron_plugin_grants_the_side_wide_plant_key_at_match_start` (`plant:*`, `plant`) | `gk-core/src/FusionRpg.Core/Effects/Plugins/PatronSecondaryPlugin.cs` |
| board.end still withdraws it | same run | PASS — `Board_end_withdraws_the_side_wide_grant` | `gk-core/src/FusionRpg.Core/Effects/EffectFunnel.cs` |
| Falsified before claimed: store widening is load-bearing | same command, `ForOwner` reverted to exact equality | 3 FAILED (`..._reaches_plant_reads...`, `..._does_not_apply_on_the_zombie_side`, `A_zombie_side_wide_grant_does_not_reach_a_plant`) — restored, 15/15 | `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:133` |
| Falsified: the funnel withdraw is load-bearing | same command, `WithdrawByPluginId` reverted to the `match` default | 1 FAILED (`Board_end_withdraws_the_side_wide_grant`) — restored, 15/15 | `gk-core/src/FusionRpg.Core/Effects/EffectFunnel.cs:143` |
| No golden moved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"` | PASS — 36/36, identical to the pre-change baseline (no re-bless) | — |
| ActorHub sole-compose guard | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | `ACTOR-HUB GUARD OK` | — |
| Scoped verification plan + guards | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs','gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs','gk-core/src/FusionRpg.Core/Effects/EffectBag.cs','gk-core/src/FusionRpg.Core/Effects/EffectFunnel.cs','gk-core/src/FusionRpg.Core/Effects/Plugins/PatronSecondaryPlugin.cs','gk-core/tests/FusionRpg.Core.Tests/Scope/StatApplyScopeSideWideTests.cs','tests/FusionRpg.Core.Tests/Effects/PatronAuraScopeTests.cs') -Session scope-side-wide"` | exit 1 — **4 pre-existing failures, none in this diff** (see below); guards OK: `BATTLE RESPONSIBILITY GUARD OK`, `FUNNEL DELTA GUARD OK`; 14848/14852 | `/tmp/ssw-verify.txt` (plan: 4 paths `core-fallback`, 1 `battle-effect-math`) |

**The 4 failures are not this change's, and the diagnosis is a reading, not a guess.** All four read
only item/atom *data* files: `data/seed/items/socket-words/sockwords.json` (**absent** — lane C's SSH2.6
retirement, handoff §4.2, while `SocketOperationsTests.cs:340` still reads it), the gem/unique item
corpus, and `gk-data/packs/fusion/data/seed/atoms/generated/**` (the `TagAxisExclusive` `defensive`+`utility` drift handoff §5
assigns to the item-seed lane). `git diff --name-only e0f1375d` contains no `data/**` path. Both are
already-owned rows in `tasks/item-todo.md`, not new findings.

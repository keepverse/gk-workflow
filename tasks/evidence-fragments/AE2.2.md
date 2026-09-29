| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| `BasicAttackGrantBuilder.Build(…, long amount)` writes `amount = -BasePerHit(base, P(Θ))` and `filters.excludeInstakill = true`; `elementPayload` and `icd_ms` unchanged; a neutral owner gets an amount and no payload | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BasicAttackGrant"` | **21/21 pass**, including `TheBakedAmountIsTheBattleBaseForTheSameTheta_negativeForDamage`, `TheBakedAmountFollowsTheta`, `TheAmountDoesNotDisturbThePayloadOrCooldown_andTheGrantOptsOutOfInstakill`, `ANeutralOwnerGetsAnAmountAndStillNoPayload`, and `AnOmittedAmountLeavesTheDefDrivenPathInCharge`. | gk-core/src/FusionRpg.Core/Combat/BasicAttackGrantBuilder.cs, gk-core/tests/FusionRpg.Core.Tests/Combat/BasicAttackGrantBuilderTests.cs |
| The `fx.overlay_damage` def and generated atoms are NOT edited | `git status --short` / the commit's own path list | four files only — the builder, its tests, the binder, `RpgHost`. No `gk-data/packs/fusion/data/seed/**`, no `gk-data/packs/fusion/data/generated/**`, no def. The amount rides the grant overlay (`resource.delta` already allows an `amount` overlay; `EffectBag` merges overlay over def params), so a plain number resolves through `DamagePacketBuilder.ResolveAmount`'s plain branch. | — |
| **Parity**: for the same action at the same Θ the lawn amount equals the battle base, through the SAME expression | same filter | The test's expected value is built with `ActionBaseDerivation.BasePowerMilli(Basic, …)` x `ActionBaseMath.BasePerHit(…, BattleRuleset.PowerValue(Θ))` — the exact expression `BasicAttack.cs` uses — and the binder produces its amount with those same two calls, so a private fold on either side breaks the equality. `P(Θ)` is `BattleRuleset.PowerValue`, the battle hit's own cached ladder. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs:177-182 |
| The binder's Θ is the Hub's value, not a private fold | code read | `CheatState.PowerIndex` is the `IPowerIndexProvider` `RpgProgressionSubsystem` writes `progression.power` from verbatim, and `HydratedPowerIndexProvider.Key(ctx)` is `(ctx.PlayerId ?? 0)` ALONE — the binder builds `new StatContext { PlayerId = CheatState.CurrentPlayerId > 0 ? CheatState.CurrentPlayerId : null }` and calls `ActorIndex`, so both lawn sides read the commander's Θ. The **planted-second-contributor falsifier** is built and green — see the `LawnGrantThetaParity` row below. | gk-fusion/src/FusionRpg.Injector/CheatState.cs:240-245, gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs:76 |
| `RpgHost.Initialize` configures `ActionBaseTuningHub` from the version `Program.cs` loads; an unconfigured hub makes bind throw and `TryBindOrRequeue` reports it | build + code read | `RpgHost.cs:228-237` adds the configure beside `RungPolicy.Configure`, reading `action-base.v2.json` — the same version `Program.cs:261-263` loads. `ActionBaseTuningHub.Tuning` throws when unconfigured, and `TryBindOrRequeue`'s existing `catch` calls `CheatState.Error("lawn-basic-attack bind: " + ex.Message)` — the never-a-silent-zero path. | gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs |
| The injector actually compiles with these changes | `$env:FUSIONRPG_ML_GAMEDIR="H:\Games\PVZ-Fusion-3.9_MelonLoader"; dotnet build src\FusionRpg.Injector.MelonLoader.39\FusionRpg.Injector.MelonLoader.39.csproj -p:GameProfile=pvzrh-3.9 -v q --nologo` | **Build succeeded — 0 Error(s)**, 23 pre-existing warnings, and NO "Skipping …" line (that project prints a skip instead of compiling when its MelonLoader dir is unset, so this is a real compile of `LawnBasicAttackGrantBinder.cs` and `RpgHost.cs`). The first attempt built the default `pvzrh-3.8.1` profile against the 3.9 pack and failed inside `Bridges\pvzrh-3.8.1\CreateZombieSpawn.cs` — a profile/pack mismatch, not this change. | — |
| Per-task boundary | `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Combat/BasicAttackGrantBuilder.cs,gk-core/tests/FusionRpg.Core.Tests/Combat/BasicAttackGrantBuilderTests.cs,gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs,gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs -Session summoner-convergence-impl-20260918` | core **14168/14169** (+5 new tests, no new red; the one red is the named pre-existing `core.autocrlf` artifact). Guards: `actor-hub`, `funnel-delta`, `single-writer`, `secondary-no-unity` all OK. `injector-compile` SKIPPED in that process (its env var is unset there) — covered by the explicit build row above instead. | tasks/summoner-convergence-ledger.jsonl |
| **Planted second contributor fails the parity test** (the falsifier the acceptance names) | `$env:FUSIONRPG_GAME_DIR="H:\Games\PVZ FUSION 3.8.1 FULL MOD TOOL"; dotnet test tests\FusionRpg.Injector.Tests\FusionRpg.Injector.Tests.csproj --filter "FullyQualifiedName~LawnGrantThetaParity"` | **3/3 pass.** `The_Hub_channel_carries_the_power_providers_Theta` drives a fixture hub with `FixedPowerIndexProvider(37)` and reads **37** — a real value, not the `0 == 0` this started as; `The_binders_Theta_source_is_the_provider_that_writes_that_channel` proves the provider the binder reads is the one the hub channel is written from; and `A_planted_second_contributor_to_progression_power_breaks_that_parity` registers a REAL second subsystem contributing to `progression.power` and the channel stops equalling Θ (the assertion fails without the plant). **Why the plant needed Priority:** `progression.power` composes as `FlatReplace` (`DerivedStatRegistry.cs:82`) and `DerivedComposer.ComposeFlatReplace` breaks `Replace` ties by `OrderByDescending(Priority).ThenBy(SourceId)` — a same-priority plant loses to `rpg.progression` on the source-id tie-break and would have proven nothing. This project is not in CI, so the command is spelled out in full. | gk-fusion/tests/FusionRpg.Injector.Tests/LawnGrantThetaParityTests.cs |

## Correction 2026-09-19 (task reopened → closed): `ActionBaseTuningHub` was never wired into `Server.Tests`

**What was wrong.** The row above says the hub is configured by `Program.cs`, `RpgHost.cs`, and — in the
AE1.1 bootstrap work — by `Core.Tests`, `Data.Tests` and `Injector.Tests`. It was **never** added to
`gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs`, and that omission is not cosmetic:
`BattleEngine.ApplyBasicAttack` (`BasicAttack.cs:381`) reads `ActionBaseTuningHub.Tuning` on every basic
attack, so every class in that assembly that resolves a REAL battle threw

```
System.InvalidOperationException : ActionBaseTuningHub.Configure(...) has not run. Read
data/tuning/action-base.v{n}.json at startup — there is no built-in default to fall back to.
```

**How it was found.** Lane A ran the Server boundary for ST4.5c (the manager asked for it while checking
whether the trigger-frequency seed moved a budget) and got **534/552**. All 18 failures were this one
cause: `AptitudeChannelModsTests.RealBattle_...` and `RolledItemEquipRuntimeTests.An_equipped_items_...`
surfaced the exception directly; the `DelveBattleSession*` classes showed its consequence (the fight task
`Faulted` instead of `Canceled`, or "condition never became true within the test timeout"). The earlier
review had read the count as a pre-existing baseline — it was not: the hub is this lane's own AE1.1/AE2.2
addition, so this is lane A's escaped defect.

**Why it stayed invisible.** This lane's `verify-change` never reached the `server` check: the plan
selects `core`, `e2e` and `server` in that order and exits on the first non-zero, and `core` carries a
named CRLF worktree failure — so the server boundary was never actually executed by a task in this lane.

**The fix (one commit).** The assembly's existing `[ModuleInitializer]` bootstrap now configures the hub
from the real published file, the same way `Core.Tests`/`Data.Tests`/`Injector.Tests` do — never an
inline default, because the value is authored, measured data (AE1.4's corrected `basePowerMilli` 140):

```csharp
FusionRpg.Core.Actions.ActionBaseTuningHub.Configure(
    FusionRpg.Core.Actions.ActionBaseTuningLoader.Parse(
        File.ReadAllText(Path.Combine(tuningDir, "action-base.v2.json"))));
```

**Verified.** `dotnet test tests\FusionRpg.Server.Tests -c Release --verbosity minimal` →

```
Passed!  - Failed:     0, Passed:   552, Skipped:     0, Total:   552 - FusionRpg.Server.Tests.dll (net8.0)
```

**0 failures from this cause, and no residue at all: the assembly is 552/552.** One configuration line
removed all 18.


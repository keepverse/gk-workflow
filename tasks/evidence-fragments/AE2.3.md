| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| The snapshot edge only RECORDS: `MarkThetaDirty()` is lock-protected, O(1), and makes **no** grant call | `$env:FUSIONRPG_GAME_DIR="H:\Games\PVZ FUSION 3.8.1 FULL MOD TOOL"; dotnet test tests\FusionRpg.Injector.Tests\FusionRpg.Injector.Tests.csproj --filter "FullyQualifiedName~LawnBasicAttackGrantBinderRefresh"` | **10/10 pass** (run at 2026-09-19 03:10:41, after every edit in this task). `The_snapshot_edge_records_only_and_never_rebinds` calls `CheatState.ApplyPowerSnapshot` twice and asserts **0** rebind attempts and an unchanged grant count. Code: `MarkThetaDirty` is three lines — `lock (Gate) _thetaDirty = true;` — and `CheatState.ApplyPowerSnapshot` calls it once, after the hydrate. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs, gk-fusion/src/FusionRpg.Injector/CheatState.cs |
| The next main-thread `Tick` re-runs `Bind(ptr)` for every live grant it owns, enumerated as `WithdrawAllBound` does | same filter | `The_next_drain_rebinds_every_live_grant_this_binder_owns`: two live grants, one dirty edge, one `Tick` -> **2** rebind attempts. `RebindAllBound` walks the same `EffectRuntime.Bag.Grants.All()` list with the same `IsBasicAttackGrantId` filter `WithdrawAllBound` uses, and derives the ptr from the grant's own `entity:` owner key. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs |
| Two dirty drains in a row leave exactly one grant per ptr (idempotent), and an identity change is one of those drains | same filter | `Two_dirty_drains_leave_one_grant_per_ptr`: two dirty edges (player 1 @ Θ20, then player 2 @ Θ30 — the identity-change trigger row) -> **2** attempts, **1** grant. Idempotence is the deterministic `GrantId`'s upsert, not a second mechanism. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs |
| A `Tick` with nothing dirty is a no-op | same filter | `A_tick_with_nothing_dirty_rebinds_nothing`: 0 attempts. | — |
| The off-switch leaves nothing to rebind | same filter | `The_off_switch_leaves_nothing_to_rebind`: with the module off, the L-N8 off edge withdraws everything bound and a Θ that moves while off drains to **0** attempts / **0** grants. The row primes an observed ON first — the off edge is a transition, and without that priming the assertion would depend on which test ran before it. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs |
| Every Θ-moving trigger (session start, SignalR reconnect, `power.index.reload`) reaches `ApplyPowerSnapshot` -> `MarkThetaDirty` | same filter | `Every_Theta_moving_trigger_reaches_ApplyPowerSnapshot` (source scan, the cadence idiom this assembly already uses): `RpgClient.cs` calls `RefreshPowerIndexAsync()` at least twice (`StartAsync`, the `Reconnected` handler), `CheatCommandRunner.cs`'s `power.index.reload` case calls it, and `CheatState.ApplyPowerSnapshot` contains the `MarkThetaDirty()` call. | gk-fusion/src/FusionRpg.Injector/RpgClient.cs, gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs |
| The injector compiles with these changes | `$env:FUSIONRPG_ML_GAMEDIR="H:\Games\PVZ-Fusion-3.9_MelonLoader"; dotnet build src\FusionRpg.Injector.MelonLoader.39\FusionRpg.Injector.MelonLoader.39.csproj -p:GameProfile=pvzrh-3.9 -v q --nologo` | **Build succeeded, 0 Error(s)** — a real compile (that project prints "Skipping" instead of compiling when its game dir is unset). | — |
| Per-task boundary | `.\scripts\verify-change.ps1 -Paths gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs,gk-fusion/src/FusionRpg.Injector/CheatState.cs,gk-fusion/tests/FusionRpg.Injector.Tests/LawnBasicAttackGrantBinderRefreshTests.cs -Session summoner-convergence-impl-20260918` | guards `actor-hub`, `funnel-delta`, `single-writer`, `secondary-no-unity` all OK. Guard suite 385/388 — the **3 red are the known baseline** named in the session brief (`StubRegisterTests.Every_row_points_at_a_file_that_exists` + 2x `VerificationBoundaryWorkflowTests.A_back_end_tool_tree_selects_its_own_boundary`), red on the unchanged tree too. `injector-compile` SKIPPED there (env unset in that process) — covered by the explicit build row above. | tasks/summoner-convergence-ledger.jsonl |
| Named, not fixed here | `dotnet test tests\FusionRpg.Injector.Tests\FusionRpg.Injector.Tests.csproj` (whole project) | **38 passed / 3 failed / 41 total.** The 3 red are all `LawnBasicAttackFeatureFlagTests` (`DefaultEnabled_constant_is_false_by_owner_decision`, `Enabled_defaults_off_with_no_explicit_toggle_ever_set`, `Enabled_ignores_a_stale_true_backing_field_when_never_explicitly_set`) — **stale**: they assert the switch defaults OFF, but the owner turned it ON on 2026-09-16 and the CI guard `LawnBasicAttackDefaultGuardTests` asserts `DefaultEnabled = true`. Pre-existing, untouched by this task, and reported rather than absorbed. | gk-fusion/tests/FusionRpg.Injector.Tests/LawnBasicAttackFeatureFlagTests.cs |
| The trigger table's FIRST row — **a spawn binds** | same filter | `A_spawn_binds_and_bakes_the_amount`: a queued spawn bakes a non-zero amount (so `Bind` ran for the spawned ptr) with **0** drain attempts — the spawn path bound it, not a rebind. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs |
| **Ordering 1 of 3: bind, then a snapshot** — the drain must re-bake to the new Θ | same filter | `The_bind_then_snapshot_ordering_ends_on_the_new_amount`: binds at the LOW Θ first (asserted *different* from the peak, so a binder that cached the amount at bind time fails here), then the snapshot arrives and the drain re-bakes to the peak. | gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs |
| **Ordering 2 of 3: snapshot, then a bind** | same filter | `The_snapshot_then_bind_ordering_ends_on_the_same_amount`: the bind after the snapshot produces the peak amount. | — |
| **Ordering 3 of 3: snapshot between the queue and the drain** | same filter | `The_snapshot_between_queue_and_drain_ordering_ends_on_the_same_amount`: queued, snapshot, drained — the same peak amount. All three are compared against `PeakAmount()`, which is produced by a REAL bind, never by re-deriving the formula in the test. | — |

**Design note — why the drain is observed through a counter.** `Bind` resolves the owner's element through
`LawnElementResolverHost`, which reads the live board; headless it early-returns *before* touching the grant
bag, so the bag cannot show that a rebind was attempted. `RebindAttemptsForTest` (the `HeldActionIdsForTest`
precedent) is what makes the attempt observable, and the two assertions are kept separate on purpose:
attempts prove the drain ran once per live grant, the grant count proves the deterministic `GrantId` kept it
an upsert.

**Second seam, same reason.** The three ordering rows need the amount the bind actually produced, so
`LastBakedAmountForTest` records it exactly where the real bake happens. To make that reachable the
magnitude now resolves at the TOP of `Bind`, before the board scan — it depends only on Θ and the tuning,
never on the board, so this is the natural order rather than a test accommodation, and it strengthens the
acceptance's "an unconfigured hub never yields a silent zero": the hub is now reported on the first bind
attempt instead of only for an actor the board happens to know. The consequence is stated: a bind attempt
for a ptr the board does not know now resolves the amount too, and with an unconfigured hub it throws
(which `TryBindOrRequeue` reports) rather than returning a quiet `false`.

**Test isolation — three layers, each one diagnosed rather than assumed (corrected 2026-09-19).**

*What actually broke, and why it looked like flakiness.* Two `UniqueAptitudeRefreshCadenceTests` debounce
tests failed intermittently (and, once the classes were serialized, deterministically). The cause is not
timing: `MatchHost`'s own static initializer reads `MatchTuningPolicy` (`CapPolicyConfig.Defaults()`), and
whichever class touches `MatchHost` first wins. A class that has not configured that policy makes the
initializer throw, and the CLR then caches the `TypeInitializationException` **on the type for the rest of
the process** — so every later test that touches `MatchHost` fails, permanently. Reproduced exactly:
`UniqueAptitudeRefreshCadence` alone is 7/7 across three runs; beside this class it was 15/17 on two
consecutive runs, both failures
`System.TypeInitializationException ... MatchTuningPolicy.Configure(...) has not run`.
**Root-cause fix:** `InjectorTestTuningBootstrap` (a `[ModuleInitializer]`, the pattern `TreeBinder.Tests`
already uses) configures the host tunings from the real shipped files before any test runs, so no class can
poison `MatchHost` by reaching it first.

*Isolation, scoped.* The first attempt was an assembly-wide
`[assembly: CollectionBehavior(DisableTestParallelization = true)]`; it is **reverted** — it changed
scheduling for every class while the conflicts are between specific ones, and it is what made the
`MatchHost` ordering (and so the failure) deterministic. This class now joins the pre-existing
`[Collection("CheatState statics")]` — the same named collection `LawnBasicAttackFeatureFlagTests`,
`MatchModifyTests` and `WaveControlTests` already use for exactly these statics. `UniqueAptitudeRefreshCadenceTests`
joins it too.

*A write removed.* The ctor no longer calls `CheatState.ResetAll()` (it wiped `MatchModifyTests`' entries:
that class is 13/13 alone and failed intermittently beside this one) and no longer `SetToggle`s: the module
is on by its own default, and even one toggle rewrites the whole cheat registry through `MaybeSave`. Only
the off-switch test moves the toggle, and it restores it in its own `finally`.

*Measured after all of it* — the whole project twice, back to back: **48 passed / 3 failed / 51 total,
both runs**, the 3 being the known stale `LawnBasicAttackFeatureFlagTests` reds. No test was weakened or
skipped to get there.

**One more real defect found while testing.** The Θ-dirty mark survived `ClearPending`, so a snapshot arriving at
the end of a match would drain into the next one and rebind the previous match's grants — the exact
stale-edge hazard `ClearPending` already exists to prevent, one field along. Two tests failed on it before
the fix (`A_tick_with_nothing_dirty_rebinds_nothing`, `The_off_switch_leaves_nothing_to_rebind`, both
observing a stray attempt). `ClearPending` now clears the flag, with the reason recorded at the call site.

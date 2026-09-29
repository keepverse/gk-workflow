# CAI4.1 — the injector view host: all seven seams, one view per (perspective, frame, census)

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row's last open half was recorded as a **denied
path**: *"`Injector/Effects/LawnActorViewHost.cs` … is under `gk-fusion/src/FusionRpg.Injector/**`, outside this
lane"*. `gk-fusion/src/FusionRpg.Injector/**` is in this lane's fence, so the half landed rather than being routed
again. Evidence lives here rather than in `tasks/evidence-fragments/` because that directory is not in
this lane's allowed paths.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| "a second `ViewFor(same perspective, same frame)` allocates nothing" | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnActorViewHostTests"` | **10 passed / 0 failed** — `A_repeat_call_in_the_same_frame_and_perspective_returns_the_same_view` asserts `Assert.Same`, i.e. the same object, not merely an equal one | `gk-fusion/src/FusionRpg.Injector/Effects/LawnActorViewHost.cs` |
| The frame is not the whole key — a spawn or death inside one frame must rebuild | same run | **10 / 0** — `A_new_census_in_the_same_frame_builds_a_new_view` swaps the census instance at the same frame number and asserts `Assert.NotSame` plus the new `LiveActorKeys` | same |
| One view per perspective, and the perspective IS the oracle's side | same run | **10 / 0** — `Two_perspectives_in_one_frame_get_their_own_views` (different objects, and the second call for the same perspective is the same object) and `The_perspective_decides_which_side_is_my_side` (one census, mirror-image answers: a plant is `0` from the plant view and `1` from Zomboss's) | same |
| Hypnosis reads correctly through the composed chain | same run | **10 / 0** — `A_mind_controlled_entity_fights_for_the_other_side`: a `zombie`-side, `MindControlled` unit reads as the player's own | same |
| An unknown ptr never reads as mine; the census is really read | same run | **10 / 0** — `An_unknown_ptr_reads_as_the_other_side_never_as_mine`; `The_held_actions_stand_in_reads_empty_and_the_census_is_really_read` (`LiveActorKeys` in census order, `PositionOf` non-null) | same |
| The injector host still compiles (a skip-stub is not a build) | `pwsh -NoProfile -File scripts/guard-injector-compile.ps1` | `INJECTOR COMPILE GUARD OK — MelonLoader host compiled to %TEMP%\fusionrpg-injector-compile\` | — |
| The project, for the record, and the program's guards | `dotnet test gk-fusion/tests/FusionRpg.Injector.Tests`; `guard-dal`, `guard-single-writer`, `guard-funnel-delta`, `guard-actor-hub`, `guard-secondary-no-unity`, `guard-test-substrate`, `guard-debug-scope` | **77 passed / 3 failed** — all three are the PRE-EXISTING stale `LawnBasicAttackFeatureFlagTests` filed as `CAI-find-1`, none of them this task's; **all seven guards exit 0** | — |

## The seven seams, and where each really comes from

| Seam | Production source |
|---|---|
| `censusOf` | `InjectorBoardSnapshot.Capture()` — already frame-cached, so a repeat call is free |
| `relation` | `new LawnRelationChain(new SpecimenOwnershipOracle(CheatState.TryGetSpecimenController), new MechanicalOwnSideOracle(perspective, census.FindPtr))`, built PER perspective |
| `unitOf` | `LawnUnitViewFactory.Build(ptr, hp, hpMax, relation)` over `InjectorEntityRegistry.FindPlant`/`FindZombie` (`thePlantHealth`/`thePlantMaxHealth`, `Bridges.ZombieCombatFields.GetHp`/`GetMaxHp`) |
| `heldActionsOf` | empty until `CAI4.3` — the spec's own endorsed stand-in |
| `elementOf` | `LawnElementResolverHost.Resolve(ptr)` → `(int)Elements.Primary`, mirroring `BattleRunState.cs:971`'s shipped shape for the same field |
| `statusMaskOf` | **`0` — a stated absence** (see below) |
| `derived` | `InjectorStatusBridge.ResolveDerived(ptr, attackerLess: false)`, which `LawnDerivedCache`'s own parameter doc names for production; the revision seam is the CONSTANT the row records until `actor-liveness-refresh` |

## The two residuals, each named

1. **`CAI4.8` is the only production caller.** `ViewFor` is reached by tests, not yet by a live decision
   tick — the module-19 frame slot is CAI4.8's, and CAI4.8's own dependency (`CAI4.7`'s lawn tuning keys)
   is blocked on the lawn plan's `lawn-perf-budget.v1.json` (`LW1.1`, measured absent). So the row stays
   open on a **named dependency row**, which is why the box is not ticked.
2. **The status-mask seam has no producer.** The spec's table says `StatusMask` comes from
   `EffectRuntime.Status`. Measured 2026-09-23: `SimEffectHost.StatusMaskOf` is an **instance** property of
   Core's sim host and is set by nobody in `src/`, and `StatusRuntime` exposes status *instances* rather
   than a mask — the mask needs the compiler's status-id→bit interning, which no injector caller supplies.
   So `statusMaskOf` returns `0`, stated in the class doc as an absence. The alternative — reading
   `ForHost(ptr)` and re-deriving bits — would fork the compiler's own mapping, which is the mechanism-fork
   this program exists to prevent. `FactsOf.StatusMask` therefore under-reports until a producer lands.

## Why the census is a settable delegate

`LawnActorViewHost.CensusOf` defaults to `InjectorBoardSnapshot.Capture` and production never sets it —
but `Capture()` needs `UnityEngine.CoreModule` at runtime (a test process has the reference assembly, not
the runtime), so a test that exercised this class's cache would otherwise need a running game. A public
settable delegate is the shipped idiom for exactly this (`ActorHudInvalidator.Install` sets
`ActorHudCache.Build`), so the test uses it and restores it in `Dispose`. Asserting the cache is the point:
the Core view's own 18 tests cover the view, and nothing covered the wiring or the cache key until now.

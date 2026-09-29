# Todo: `battle-wire-remainder`

**Plan:** [battle-wire-remainder-plan.md](battle-wire-remainder-plan.md) · **Sources:**
[battle-derived-wire-todo.md](battle-derived-wire-todo.md), [combat-math-dedup-todo.md](combat-math-dedup-todo.md)
(both retired by pointer, `paperwork-reconcile` P5) · **Status:** plan approved 2026-09-20
(`backlog-clean-up` BCU2.7). Prefix `BWR`. Every box below is freshly opened work to build.

Verification: `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` unless a task names
otherwise. No task exceeds 5 files.

---

## Wave 1 — the three real gaps + the smaller wiring tail

- [x] **BWR1.1 — W3: route the basic-attack's `ApplyHp` through the reflect step** · M · deps: — · *(spec: battle-derived-wire)* — **CLOSED 2026-09-23 (`bdw-1`)** at **`6c8187e20`**: `TryReflect` made `internal static` and called from `BattleRunState.ApplyHp` (basic attack, guardian share, DoT pulse); one body, no copy. H1 reading: **0 of 5 battle goldens moved** (fixtures are bare), `BattleReflectTests` 3/3, and `ProcDepthLimit` is the only bound (mutual-reflect termination test). Evidence: `tasks/battle-derived-wire-evidence.md` §T2/W3.
  - Acceptance: `BattleRunState.ApplyHp`'s basic-attack path enters `DispatchInstant` (or an equivalent
    reflect tail), matching effect-driven hits; a battle with reflect at 0 on both sides is
    byte-identical. **H1: re-bless any moved battle goldens in this same commit**, with the per-fixture
    delta in the commit body.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Battle.*Reflect"`; `.\scripts\test-fast.ps1 -AllDefault` if goldens move (H1 crosses the golden-fixture boundary).
  - Files: `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`, `gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs`, focused tests, battle goldens if moved.

- [x] **BWR1.2 — W4 decision: one owner of status → `combat.*`** · M · deps: — · *(spec: battle-derived-wire)* — **CLOSED 2026-09-23 (`bdw-1`)** at **`1021589c6`**: battle's OWN `BattleDerivedModifierLedger` owns status→`combat.*` (via `Host.AddDerivedContribution`), so `StatusDerivedSubsystem` is deliberately NOT registered — registering it would double-apply. Pinned by `BattleStatusDerivedContributionTests.Battle_registers_progression_but_not_the_status_derived_subsystem`; `guard-actor-hub` green. Evidence: `tasks/battle-derived-wire-evidence.md` §T5/W6.
  - Acceptance: decide which of `StatusDerivedSubsystem` or `BattleStatModifierLedger` owns
    status→`combat.*` in battle; migrate the other's callers; `guard-actor-hub.ps1` proves no
    double-apply. This is a decision task, not a re-run of the original Task 14.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "StatusDerived|BattleStatModifier"`; `.\scripts\guard-actor-hub.ps1`.
  - Files: `BattleHubCompose.cs`, the migrated mechanism's callers, focused tests.

- [ ] **BWR1.3 — W8: `BattleHubInputs.Draughts` production producer** · S · deps: — · *(spec: battle-derived-wire)* — **STILL OPEN, blocked EXTERNAL (owner: `item` program)**: the authored draught is a seed (`Family` + `PowerBand`, no magnitude) and no seed→channel resolver exists, so there is nothing to assign. Owning row: `tasks/item-todo.md` ~6839, "The seed → concrete generator". Measured: `Unique`/`Equipment`/`Gem ContainerBuild.From` all exist and there is **no consumable sibling**, so the fix is a fourth builder of an existing shape, not a call-through. Re-checked 2026-09-23: still absent.
  - Acceptance: a real production call sets `.Draughts =` at a real battle setup site (today zero
    hits repo-wide), in the same shape `solid-remediation` T3.3 already used for Aptitude/BoundAtoms/
    StarLoyalty.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Draughts`.
  - Files: the setup builder, focused tests.

- [x] **BWR1.4 — W13 (narrowed): the `ApplyHp` positive-amount heal path** · S · deps: — · *(spec: battle-derived-wire)* — **CLOSED 2026-09-23 (`bdw-1`)** at **`aee1ebe8d`**: `BattleRunState.ApplyHp` routes a positive amount through the same `OverlayCombatMath.Finalize` the effect path uses, so `resource.restore.hp` reaches regenerator/immortal/soul-eater heals with one formula. `BattleHealPowerTests` 4/4; `HealingPairTests` 11/11; no goldens moved. Evidence: `tasks/battle-derived-wire-evidence.md` §T3.
  - Acceptance: direct/trait heals (regenerator, guardian, lifesteal) reach `resource.restore.hp` —
    the DoT-pulse half is already done (`solid-remediation` T2.6); this task is the `ApplyHp`
    positive-amount path only, not a re-do of the pulse half.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter BattleHealPower`.
  - Files: `BattleRunState.cs`, focused tests.

- [x] **BWR1.5 — W14/W15: `loadout.slots` feed + `turn.moveSpeed` register-or-delete** · S · deps: — · *(spec: battle-derived-wire)* — **CLOSED 2026-09-23 (`bdw-1`)**: W14 at **`ce6e602be`** (option b — `loadout.slots` listed in `DominanceGuard.BuildReservedFamilies` with a stated reason, plus a registry `UnitClassNote`; option (a) stays the Data-layer owner's) and W15 at **`18139aec6`** (`turn.moveSpeed` deleted, with a guard preventing a declared-unregistered turn channel). `LoadoutSlotsChannelTests` + `TurnChannelDeclarationTests` 13/13. Evidence: `tasks/battle-derived-wire-evidence.md` §T18 and §T17.
  - Acceptance: `loadout.slots` is fed from the actor's composed `Derived` at the loadout-resolve seam,
    or added to `DominanceGuard.BuildReservedFamilies` with a named reason; `turn.moveSpeed` is either
    registered with a named consumer or deleted with a one-line note in `battle-timeline-map.md`.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "LoadoutSlots|MoveSpeed"`.
  - Files: `LoadoutSet.cs`, `DerivedTurnChannels.cs`, `DerivedStatRegistry.cs`, focused tests.

- [x] **BWR1.6 — W17: `BattleHubCompose` merges `AppliedCombat` (`Resolve`, not `ResolveDerived`)** · M · deps: — · *(spec: battle-derived-wire)* — **CLOSED 2026-09-23 (`bdw-1`)** at **`ee4d217bc`**: `BattleHubCompose.Resolve(setup)` calls `hub.Resolve(ctx)` (the merge itself) and `ActorState` consumes it by the delta `AppliedCombat − RuntimePrimary`. H1 reading: **0 of 5 goldens moved**; `Fortitude(7)` maxHp 215→1935 (Δ1720), defense 7→2351 (Δ2344). Evidence: `tasks/battle-derived-wire-evidence.md` §T15/W17 and the audit's §7b.
  - Acceptance: `BattleHubCompose.cs:92` calls `hub.Resolve(ctx)`; `progression.bonus.*` reaches
    battle. **One ActorHub compose** — this is the merge itself, never a second fold. **H1: re-bless
    any moved battle goldens in this same commit**, with the per-fixture delta in the commit body.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "BattleHubCompose|AppliedCombat"`; `.\scripts\guard-actor-hub.ps1`; `.\scripts\test-fast.ps1 -AllDefault` if goldens move.
  - Files: `BattleHubCompose.cs`, focused tests, battle goldens if moved.

### Checkpoint BWR-C1/C2
- [x] W3 and W17 each land with a re-blessed golden set and a recorded delta (H1). — Both landed with **0 goldens moved** (bare fixtures), so no re-bless was needed and the per-fixture delta is **0**; the mechanism deltas are recorded at `6c8187e20` (reflect) and `ee4d217bc` (progression).
- [x] W4's decision is made, migrated, and `guard-actor-hub.ps1` proves no double-apply. — `1021589c6`; the pin test asserts the registered subsystem set has `rpg.progression` and not `l2b.derived`.

## Wave 2 — CombatSim dedup + display parity

- [ ] **BWR2.1 — D6: pool regen, one implementation** · M · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `ActionSchedule.cs`'s `Math.Clamp` pool advance goes through `ResourcePoolState`/
    `ActorResourcePools` (per-mille `long`, carry-corrected, `checked`), matching the real gate exactly.
    This changes predicted numbers — record a before/after, not a silent re-bless.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ActionSchedule`; `.\scripts\regen-class-system-baselines.ps1 --check`.
  - Files: `Balance/Analytic/ActionSchedule.cs`, focused tests.

- [ ] **BWR2.2 — D9: `gk-core/tools/CombatSim/ActionEconomy.cs` calls `ActionSchedule`** · S · deps: BWR2.1 (shared file) · *(spec: combat-math-dedup)*
  - Acceptance: `ActionEconomy`'s walk calls the now-fixed `ActionSchedule` rather than duplicating it,
    or (if the JSON action-set shape makes that impractical) a parity test instead, stated plainly.
  - Verify: `dotnet run --project gk-core/tools/ProvePredictor`; a parity test.
  - Files: `gk-core/tools/CombatSim/ActionEconomy.cs`, focused tests.

- [ ] **BWR2.3 — D7 (part b): one `Phi`/`Erf` implementation** · S · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `tools/CombatSim/Analytic.Phi` is deleted; call sites use `Race.Phi` (which already
    guards NaN/±∞, unlike the deleted copy). Part (a), the verification-boundary mapping, is already
    done by `solid-remediation` T1.7/T1.8 — reused, not re-added.
  - Verify: a test asserting the A&S coefficient `0.254829592` appears in exactly one file (`Race.cs`).
  - Files: `gk-core/tools/CombatSim/Analytic.cs`, `Balance/Analytic/Race.cs`, focused tests.

- [ ] **BWR2.4 — D8: `gk-core/tools/CombatSim/StatusModel.cs` calls `StatusUptime`** · S · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `StatusMath.ExpectedDotPerRound`/`Expected` call the shared `StatusUptime`; the uptime
    formula appears once; baselines/`ProvePredictor` residuals unchanged or reported.
  - Verify: `.\scripts\regen-class-system-baselines.ps1 --check`; `dotnet run --project gk-core/tools/ProvePredictor`.
  - Files: `gk-core/tools/CombatSim/StatusModel.cs`, focused tests.

- [ ] **BWR2.5 — D11/D12: sigmoid display parity, C# and TS** · M · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `ItemDisplayRenderer` (C#) and `magnitude.ts` (TS) agree on the same displayed number;
    TS's hardcoded tuning constants read from the same source C# does, never a second copy.
  - Verify: a C# test + a vitest, per `spec-magnitude-and-units.md` §5.
  - Files: `ItemDisplayRenderer.cs`, `gk-web/web/fusion-rpg-web/src/**/magnitude.ts`, both test files.

## Wave 3 — the cosmetic tail (fully parallelizable, single-file each)

- [ ] **BWR3.1 — D13/D14/D15/D16/D18/D19: closed-vocabulary duplicates** · M · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `DamageFxTag`, `AreaShapes`, the rarity ladder, the 28 combat-channel families, the
    inspect-scope vocabulary, and `DerivedStatSurfaceCatalog` each reference one declaring type,
    never re-literalise; a partition test (`∪` = the whole, disjoint) where applicable.
  - Verify: focused `dotnet test` per item; source-scan guard tests per the original tasks' own shape.
  - Files: one file + one test per item — split into per-item sub-commits if touching more than 5 files total.

- [ ] **BWR3.2 — D20/D21: the two HUD folds call the shared helper** · S · deps: — · *(spec: combat-math-dedup)*
  - Acceptance: `Injector/Hud/ActorHudDirector.cs` calls `Core/Hud/ActorHudShieldStacks.cs`'s `Totals`
    instead of re-implementing it; the raw `hp/max` "true ratio" is written from one place.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ActorHudShieldStacks`.
  - Files: `ActorHudDirector.cs`, `ActorHudShieldStacks.cs`, `ActorHudPool.cs`, focused tests.

### Checkpoint BWR-C3
- [ ] Every D-item in this wave is fixed, or moved to the audit's own "Deliberately kept" table with
  its reasoning intact — never silently dropped.

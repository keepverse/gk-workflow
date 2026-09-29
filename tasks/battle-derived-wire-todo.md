# Tasks: battle-derived-wire

Plan: [tasks/battle-derived-wire-plan.md](battle-derived-wire-plan.md) ·
Audit: [docs/research/battle-derived-wire-audit-2026-09-16.md](../docs/research/battle-derived-wire-audit-2026-09-16.md)

Verification everywhere is
`.\scripts\verify-change.ps1 -Paths $changed -Session battle-derived-wire-20260916`.
Full suite only at Checkpoints 1, 3 and 6.

**Do Task 1 first if only one task is ever done.** Everything else is smaller in player-visible effect.

---

## Census note — read this before counting `- [ ]` lines

**Every task block below is closed or blocked, as of 2026-09-23 (`bdw-1`).** The block-level reading:
19/19 task blocks carry a closure phrase — 15 built (T0, T1, T2/W3, T3, T4, T5, T6, T8, T10, T11, T12,
T13, T15/W17, T16, T17, T18), 2 superseded (T7, T14), 1 blocked on an external dependency (T9 —
`tasks/item-todo.md`'s seed→concrete generator row). T15's third bullet is blocked on an out-of-fence
`docs/research/**` write; Checkpoint 6's three open boxes name the audit write (out-of-fence), the full
suite (CI/nightly/release-owned per this lane's brief) and the live RPG-Server-Debug probe (owner-side,
needs a live slot).

**The remaining `- [ ]` lines are NOT open work.** They sit inside pointer-closed blocks: a row shipped
inside `solid-remediation` (2026-09-17) or in this lane keeps its original acceptance boxes unticked,
and the closure is the block's own pointer paragraph. Counting them would read ~76 "open rows" for a
program with zero open task blocks — the exact overstatement `AGENTS.md` names: *"An unchecked `- [ ]`
line is not a unit of work. Measure remaining work as task blocks, never checkbox lines."* The W1–W17
closed ledger (every gap's disposition and landing commit) is in
[tasks/battle-derived-wire-evidence.md](battle-derived-wire-evidence.md) §W1–W17.

---

## Phase 0: measure

### Task 0 — Count what battle's effect path actually carries

**Closed 2026-09-20 by pointer** (`backlog-clean-up` `paperwork-reconcile` P5): **BUILT** —
`solid-remediation-todo.md:198-211` T2.1 SPIKE; answer at
`docs/research/battle-effect-payload-spike-2026-09-17.md` (reversed this plan's own task order, T2.4
before T2.5). Absorbed without a pointer until now — `solid-remediation` never cites this plan.

**Description.** The audit proved battle's effect/atom damage path skips the resolver (W1) but could not
size the impact. Before changing behaviour, produce a repeatable count of how many battle-reachable
grants emit a `DamagePacket` with a non-empty `ElementPayload`, and how many emit one without. This is a
test that prints a reading, not an assertion on a number.

**Acceptance criteria:**
- [ ] A test enumerates `EffectAtomCatalog.CreateAll()` (the catalog battle installs at `BattleEffects.cs:59`) and reports, per trigger, how many compiled defs produce a `resource.delta` damage action and whether each carries an element payload.
- [ ] The test **prints** the counts and asserts only structural facts (every def compiles; every damage action names a known channel). It pins no population count — guardrail rule.
- [ ] The result is written into the audit's §8 item 2 as a resolved reading with its date.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/Battle/BattleEffectPayloadCensusTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** None
**Files likely touched:** `tests/FusionRpg.Core.Tests/Battle/BattleEffectPayloadCensusTests.cs`; `docs/research/battle-derived-wire-audit-2026-09-16.md`
**Scope:** S (2 files)

---

## Phase 1: the resolver reaches both of battle's damage paths

### Task 1 — Install `OverlayCombatMath` on battle's `EffectBag` (W1)

**Closed 2026-09-20 by pointer** (`backlog-clean-up` `paperwork-reconcile` P5): **BUILT** —
`solid-remediation-todo.md:266-270` T2.5 sets both `CombatMath`/`ActorResolve` beside `ShieldGate`;
T2.6 measured 0 goldens moved, live-proved `docs/research/perf/cp2-live-proof-2026-09-17.md`.

**Description.** `BattleEffectHost` builds its own `EffectBag` (`BattleEffects.cs:60-63`) and never sets
`Bag.CombatMath`, so `CombatDamageDispatcher.cs:28` falls back to `PassThroughCombatMath`. Wire the same
`OverlayCombatMath.Create(...)` the injector already uses (`EffectRuntime.cs:527-539`), resolving actors
from battle's own `ByKey[...].Derived` — the exact resolver `StatusRuntime` already receives at
`BattleRunState.cs:303-306`. One complete path: a battle DoT tick resolves through the SSOT calculator
end to end.

**Acceptance criteria:**
- [ ] `BattleEffectHost` exposes a `CombatMath` wire-in of the same shape as its existing `Status`/`StatusRng` forwards (`BattleEffects.cs:105-108`), and `BattleRunState` sets it beside `Bag.ShieldGate` (`BattleRunState.cs:342`).
- [ ] The actor-resolve delegate reuses the existing `ByKey[...].Derived` + `ElementTypes` read — it does **not** introduce a second snapshot source.
- [ ] A battle-side `resource.delta` grant carrying a typed element payload produces a damage number that differs from its authored amount by exactly what `OverlayCombatCalculator.Compute` returns for the same inputs — proven by asserting equality against a direct `Compute` call, not against a hard-coded number.
- [ ] A payload-less packet still passes through unchanged (`OverlayCombatMath.cs:42-43`) — the reflect-bounce contract in `combat-damage-ssot.md` §6.7a is preserved.
- [ ] Battle goldens re-blessed **in this task**, with the per-fixture damage delta recorded in the commit body. `RulesetVersion` (`BattleModels.cs:95`) bumped once here.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs,gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,tests/FusionRpg.Core.Tests/Battle/BattleCombatMathWiringTests.cs -Session battle-derived-wire-20260916`
- [ ] `.\scripts\guard-funnel-delta.ps1` and `.\scripts\guard-single-writer.ps1` clean

**Dependencies:** Task 0
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`; `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleCombatMathWiringTests.cs`; battle golden fixtures
**Scope:** M (3 files + goldens)

### Task 2 — Supply `ActorResolve` and route battle HP through the reflect step (W2, W3)

**Status update 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P5): **W2 half BUILT** by the
same `solid-remediation` T2.5/T2.6 that closed Task 1 (`ActorResolve` set, 0 goldens moved). **W3 half
still NOT-BUILT — a real, separate gap, not wiring for this task's own bullets.**
`solid-remediation-todo.md:344-348` names it explicitly: `BattleRunState.ApplyHp`'s basic-attack path
still never enters `DispatchInstant`, so **only effect-driven hits reflect; the basic attack cannot.**
It was recorded as owed to a module named `battle-mode-parity`, which closed (CP3 MET) without taking
it. Routed to `tasks/battle-wire-remainder-todo.md` W3 (`backlog-clean-up` `orphan-plan-authoring`,
BCU2.7) rather than re-attempted here.

**CLOSED 2026-09-23 (`bdw-1`) — W3 built here; the BWR routing is superseded.**
`TryReflect` is now `internal` and `BattleRunState.ApplyHp` calls it for every landed negative delta
(basic attack, guardian share, DoT pulse), reusing the ONE body — no duplicate formula, no second
counter. `ProcDepthLimit` stays the only bound (the bounce carries `ChainDepth + 1` into the shared
check). The measure first: 26 passive-tree node files plus `gk-data/packs/fusion/data/seed/atoms/aura-content.json` author
`combat.reflect.*`, but no battle golden fixture carries a reflect channel, so **0 of 5 battle goldens
moved** (`BattleGoldenTests` 5/5) and the 32-seed sweep held. `BattleReflectTests` 3/3. The
`ReflectHasNoBattlePathTests` contract was rewritten in the same commit (it pinned D2's "reflect is
lawn-only", which this task deliberately ends) and `BinderRunReport`'s §6 M2 note was retired.
⚠ `tasks/battle-wire-remainder-todo.md` BWR1.1 duplicates this row; that file is outside this lane's
fence, so the manager should close BWR1.1 by pointer to this commit.

**Description.** Two independent blocks keep `combat.reflect.*` inert in battle: battle's bag has no
`ActorResolve` (so `CombatDamageDispatcher.cs:84` short-circuits), and battle's own HP apply enters at
`DamageApplyPipeline.Apply` (`BattleRunState.cs:863`), one level below the reflect step at
`CombatDamageDispatcher.cs:83-85`. Close both: set `Bag.ActorResolve` from the same delegate Task 1
introduced, and give `BattleRunState.ApplyHp` a reflect tail that reuses `TryReflect`'s policy rather
than re-implementing it.

**Acceptance criteria:**
- [x] `Bag.ActorResolve` is set beside the Task 1 wire-in; no second resolver function is created. (W2, already built; W3 reuses the same `resolveActor`, now stored as `_resolveActor`)
- [x] `BattleRunState.ApplyHp` performs the reflect attempt using the **same** `CombatPolicy` reads (`ReflectRateScale`, `ReflectShareScale`, `ReflectReadsPostShield`) and the same `CombatDerivedReader.Reflect*` calls — the sanctioned shape is to make `TryReflect` reachable from battle, not to copy its body. If `TryReflect` must become internal/public to be reused, that is the change; a duplicate is a defect. (`TryReflect` made `internal static`; `ApplyHp` calls it; one body — asserted by `ReflectHasNoBattlePathTests.TryReflect_has_one_body_and_the_effect_path_still_calls_it`)
- [x] `ProcDepthLimit` remains the only termination bound (`combat-damage-ssot.md` §6.7a) — no second counter. (`A_mutual_reflect_chain_terminates_under_ProcDepthLimit`)
- [x] A battle where one side has `combat.reflect.rate.omni` > 0 and `combat.reflect.damage.omni` > 0 produces a measurable bounce; with both at 0 the battle is byte-identical to before this task (`NoGoldensMoveAtZero`). (`BattleReflectTests` 3/3; `BattleGoldenTests` 5/5 unmoved — reading: 26 passive-tree node files + `aura-content.json` author reflect, no battle fixture does)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs,gk-core/tests/FusionRpg.Core.Tests/Battle/BattleReflectTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped` (no `bdw-1` session record exists); printed evidence in the §T2/W3 fragment.

**Dependencies:** Task 1
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleReflectTests.cs`
**Scope:** M (3 files)

### Task 3 — Make `resource.restore.hp` reach battle heals (W13)

**Status update 2026-09-20** (P5): **PARTIAL** — the DoT-pulse half is BUILT
(`solid-remediation-todo.md:286-291`, `ResolvePulseAmount`). `BattleRunState.ApplyHp`'s direct/trait
heals (`:1090` regenerator, guardian, lifesteal) still skip `resource.restore.hp`. **Narrow this
task's remaining scope to the `ApplyHp` positive-amount path only** — do not re-do the pulse half.

**CLOSED 2026-09-23 (`bdw-1`)**: the remaining `ApplyHp` positive-amount path is built.
`BattleRunState.ApplyHp` now routes a positive amount through the **same** `Host.Bag.CombatMath.Finalize`
the effect path already uses, so `regenerator`/`immortal`/`soul-eater` heals pick up the healer's
`resource.restore.hp` with one formula (no copy). Evidence: `tasks/battle-derived-wire-evidence.md` §T3.

**Description.** The heal term `combat.heal.power`'s successor `resource.restore.hp` is read only in
`OverlayCombatMath.FinalizeHeal` (`OverlayCombatMath.cs:81`). With Task 1 installing
`OverlayCombatMath` on battle's bag, a positive-amount packet routed through the bag already picks it
up; a heal applied through `BattleRunState.ApplyHp` still does not. Close the second path.

**Acceptance criteria:**
- [x] A positive `ApplyHp` in battle adds the healer's `resource.restore.hp`, floored at 0, using the same expression as `OverlayCombatMath.cs:86` — no second formula. (`BattleHealPowerTests`, T3 fragment)
- [x] No matchup, no roll, no defender-side term (`combat-damage-ssot.md` §4.3 is not reopened). (`HealingPairTests.NoMatchupNoHitNoCrit`)
- [x] A healer with `resource.restore.hp == 0` heals exactly the authored amount. (`Zero_heal_power_heals_exactly_the_authored_amount`)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHealPowerTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped`; printed evidence in the §T3 fragment.

**Dependencies:** Task 1
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHealPowerTests.cs`
**Scope:** S (2 files)

### Checkpoint 1: the resolver is universal

- [x] Both battle damage paths resolve through `OverlayCombatCalculator`; a test proves the two produce identical numbers for identical inputs. (W1 bag path by `solid-remediation` T2.5; W2/W3 direct path by T2 — `BattleReflectTests`/`BattleHealPowerTests`.)
- [x] Reflect fires in battle and is bounded by `ProcDepthLimit`. (`BattleReflectTests.A_mutual_reflect_chain_terminates_under_ProcDepthLimit`.)
- [x] Goldens re-blessed once; the per-fixture delta is written into the commit body. (**0 of 5 moved** — no re-bless needed; every fixture is bare, so reflect/progression bonuses are 0 there. Reading in the evidence file.)
- [ ] **Full suite** — this phase crosses Core and the golden fixtures: `.\scripts\test-fast.ps1 -AllDefault`. **Not this lane's to run:** CI/nightly/release-owned per the brief; every row landed with its path-owned selection (70 project runs green on the last one).
- [x] `.\scripts\guard-actor-hub.ps1`, `guard-funnel-delta.ps1`, `guard-single-writer.ps1` all clean. (4/4 plus `guard-dal` OK on every commit.)

---

## Phase 2: mid-battle contributions stop being a dead seam

### Task 4 — Give `BattleActorSetup.ActiveAuras` a production producer (W7)

**Status update 2026-09-20** (P5): **NOT-BUILT**, re-confirmed by `solid-remediation-todo.md:519-542`
T3.5 — still test-only, registered as **SR-14**. **Re-homed 2026-09-20** (`backlog-clean-up` BCU3.7):
`aura-skill` T13 shipped 2026-08-30 and does not close this gap (re-checked live) — the real owner is
the new `aura-skill` **T23**, added the same day this correction landed. Do not re-open as a fresh task
here — `aura-skill` T23 is the named owner.

**CLOSED 2026-09-23 (`bdw-1`) — the first production writer exists; the aura-skill T23 routing is
superseded.** `WebMatchService.ActiveAurasFor` reads the player's active set from the SAME process-local
`AuraRuntime` the aura endpoints use (`AuraRuntimeEndpoints.ActiveRuntime` — one cache, never a second
dictionary) and projects each aura's declared `GrantChannels` with the SHIPPED
`AtomPushService.AuraChannelReferenceValue` (the same resolver the atom push uses — no new aura
resolver). ⚠ **Location deviation:** `ActiveAuras` lives on the battle-level `BattleSetup`, which
`BuildSquad` returns only the squad half of, so the producer sits in `WebMatchService.Resolve` where the
setup is assembled — not literally inside `BuildSquad`. The magnitude is the structural REFERENCE value
(rung floor, full share, pin Θ); live per-commander scaling remains the named follow-up in
`AuraMagnitude.ReferenceChannelValue`'s own doc. `WebMatchAuraDeliveryTests` 3/3. The delivery filter
(only matching-`Side` actors) is proven in Core by `AuraDeliveryTests.Wave_side_aura_does_not_touch_squad`.

**Description.** `ActiveAuras` (`BattleModels.cs:478`) is consumed at `BattleRunState.cs:455-463` and set
nowhere in `src/**`. The aura runtime already exists (`gk-core/src/FusionRpg.Core/Aura/`, `AuraRuntime.cs`) and
the server already exposes it (`AuraRuntimeEndpoints.cs:41,70`). Wire the web-match squad builder — the
one setup producer that already carries rich `HubInputs` — to project the player's active auras onto
every friendly setup.

**Acceptance criteria:**
- [x] `WebMatchService.BuildSquad` (`WebMatchService.cs:578-613`) populates `ActiveAuras` from the player's real active set, resolved through the shipped `AuraRuntime` — never a new aura resolver. (`WebMatchService.ActiveAurasFor` + `AuraRuntimeEndpoints.ActiveRuntime` + `AtomPushService.AuraChannelReferenceValue`; placed in `Resolve` because `ActiveAuras` is battle-level — deviation disclosed above)
- [x] A player with no active aura produces a byte-identical battle to today. (`A_player_with_no_active_aura_produces_an_empty_list` — the setup's `ActiveAuras` stays `Array.Empty`)
- [x] A player with one active aura sees the named channel change on exactly the actors whose `Setup.Side` matches `CommanderSide`, and on no others (`BattleRunState.cs:459`). (`An_active_aura_projects_its_grant_channel_with_the_shipped_reference_value` — row `CommanderSide == "squad"`; delivery filter proven in Core `AuraDeliveryTests.Wave_side_aura_does_not_touch_squad`)
- [x] The criterion is **order-independent**: activating the aura before or after squad build both reach the setup. (`The_active_set_is_read_fresh_so_the_order_of_enable_and_read_does_not_matter`)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/WebMatchService.cs,gk-core/tests/FusionRpg.Server.Tests/WebMatchAuraDeliveryTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped` (plus `AtomPushService.cs`/`AuraRuntimeEndpoints.cs`); printed evidence in the §T4 fragment.

**Dependencies:** None (independent of Phase 1)
**Files likely touched:** `gk-core/src/FusionRpg.Server/WebMatchService.cs`; `gk-core/tests/FusionRpg.Server.Tests/WebMatchAuraDeliveryTests.cs`
**Scope:** S (2 files)

### Task 5 — Give `Host.AddDerivedContribution` a production invoker (W6)

**Status update 2026-09-20** (P5): **NOT-BUILT**, re-confirmed by the same `solid-remediation-todo.md:519-542`
T3.5 pass as Task 4 — also **SR-14**, re-homed the same way to `aura-skill` **T23** (`backlog-clean-up`
BCU3.7). Kept intact (not deleted), not re-opened here.

**CLOSED 2026-09-23 (`bdw-1`) — built; this IS the W4 decision (Task 14's).** `Status.OnApplied`
splits by channel: a `combat.*` mod goes to `BattleDerivedModifierLedger` through the
`Host.AddDerivedContribution` seam (its first production invoker), a primary mod keeps the phased
`BattleStatModifierLedger`; `Status.OnEnded` withdraws from BOTH, so no contribution outlives its
status. Battle therefore owns status→`combat.*` through its own derived ledger and **does not register
`StatusDerivedSubsystem`** — the two-owner question Task 14 posed is answered in favour of the battle
ledger, and Task 14 is superseded rather than deferred.

⚠ **Op scope, read from code not assumed:** `combat.*` registers `FlatSum`, and
`DerivedComposer.ComposeChannel` sums ONLY `Flat` for that kind, so a derived `increased` contributes
nothing (matching the shipped composer, not a new rule). `status.power.*`/`status.resist.*` are
`SumIncreased` and are deliberately NOT routed here — `BattleDerivedModifierLedger` is a plain sum and
would misread an `increased` op; those channels keep today's `Ledger` path, unchanged.

`BattleStatusDerivedContributionTests` 4/4; the no-content case is byte-identical (`BattleGoldenTests`
5/5 — no shipped status authors a `stat` block at all).

**Description.** The live mid-battle derived-write seam is declared (`BattleEffects.cs:150`), wired
(`BattleRunState.cs:388`) and invoked only from tests. The nearest real producer is a status whose
`StatMods` name a `combat.*` channel: those land in `BattleStatModifierLedger` today
(`BattleRunState.cs:310-321`) where nothing reads them for `combat.*`. Route `combat.*`-channel status
mods to `DerivedLedger.Add` via the existing seam, and withdraw them on `Status.OnEnded` through
`RemoveBySource` (`BattleDerivedModifierLedger.cs:45-49`).

**Acceptance criteria:**
- [x] `Status.OnApplied` splits by channel: primary channels (`atk`, `defense`) keep today's `Ledger.Add`; `combat.*` channels go to the derived ledger through `Host.AddDerivedContribution`. (`A_primary_channel_status_mod_does_not_reach_the_derived_ledger` + `A_status_combat_channel_mod_reaches_the_composed_derived`)
- [x] `Status.OnEnded` withdraws from whichever ledger received it — no contribution can outlive its status. (`Withdrawing_the_status_reverts_to_the_frozen_base`; `DerivedLedger.RemoveBySource` added beside the primary withdrawal)
- [x] The per-round `RecomposeDerivedForAllActors` (`BattleEngine.cs:481`) now makes the change visible on the next round, proven against the frozen `BaseDerived` (`BattleEngine.cs:47`). (base + 200, then back to base on withdrawal — both read from `Derived` after `Recompose`)
- [x] A battle with no `combat.*`-channel status is byte-identical. (`BattleGoldenTests` 5/5 — no shipped status carries a `stat` block, so the split is inert on every golden)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,gk-core/tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedContributionTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped`; printed evidence in the §T5 fragment.

**Dependencies:** Task 4 (shares the recompose path; do the simpler producer first)
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedContributionTests.cs`
**Scope:** S (2 files)

### Task 6 — Close the status-sourced `defense` dead end and the two-ledger conflict (W11, audit §4.1)

**CLOSED 2026-09-23 (`bdw-1`)**: one gate now owns `combat.defense.omni`.
`BattleStatModifierLedger.PushDefenseToDerived` is the single writer, called by BOTH the `stat.modify`
executor and the status `OnApplied`/`OnEnded` handlers; it writes a CONTRIBUTION
(`phased − baseline`, source `rpg.battle.defense`) into `BattleDerivedModifierLedger`, so the
a per-round `Recompose` sums it with an aura on the same channel instead of overwriting it. The aura
half is exercised through the shipped `BattleEffectHost.AddDerivedContribution` seam (Task 4/5's
owned producer is still re-homed to `aura-skill` T23). Evidence: `tasks/battle-derived-wire-evidence.md` §T6.

**Description.** A status carrying a `defense` `StatMod` lands in `BattleStatModifierLedger`
(`BattleRunState.cs:315`) and is never read; only the `stat.modify` executor pushes defense into
`Derived` (`BattleEffects.cs:316-318`). Worse, once Task 4 lands, an aura targeting
`combat.defense.omni` would have its value overwritten every round by `Recompose`
(`BattleDerivedModifierLedger.cs:63`) rebuilding from `BaseDerived`. Make one gate own
`combat.defense.omni`.

**Acceptance criteria:**
- [x] `combat.defense.omni` has exactly one writer into `Derived`. The `stat.modify` push and the status-sourced mod use the same one. (`BattleStatModifierLedger.PushDefenseToDerived`, called from `BattleEffects.ExecModifyStat` and both status handlers)
- [x] A test applies a status defense mod and a `stat.modify` defense mod to the same actor, runs two rounds, and asserts the composed defense equals base + both contributions after each round — proving idempotence under `Recompose`. (`BattleDefenseOwnershipTests.A_status_mod_and_a_stat_modify_sum_and_survive_two_recomposes`)
- [x] A test asserts an aura on `combat.defense.omni` and a `stat.modify` on `defense` do not clobber each other across a round boundary. (`An_aura_and_a_stat_modify_do_not_clobber_each_other_across_a_round_boundary`)

**Verification:**
- [x] `verify-change.ps1` path-owned selection over the six changed paths — all selected checks passed (see §T6 fragment); `guard-actor-hub`/`guard-single-writer`/`guard-funnel-delta`/`guard-dal` 4/4 OK.

**Dependencies:** Task 5
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs`; `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleDefenseOwnershipTests.cs`
**Scope:** M (3 files)

### Checkpoint 2: mid-battle contributions are real

- [x] An aura, a status-sourced `combat.*` mod and a `stat.modify` all reach the composed `Derived` and all withdraw cleanly. (T4/W7 `WebMatchAuraDeliveryTests`; T5/W6 `BattleStatusDerivedContributionTests`; T6/W11 `BattleDefenseOwnershipTests`.)
- [x] One writer per channel; the two-ledger conflict is closed with a test that would catch its return. (`BattleDefenseOwnershipTests` + `BattleStatusDerivedContributionTests` — one gate owns `combat.defense.omni`, and status `combat.*` has one owner.)
- [x] `.\scripts\guard-actor-hub.ps1` clean. (OK on every commit.)

---

## Phase 3: a specimen's build matters in every mode, not just web match

### Task 7 — Delve encounters carry the player's real `HubInputs` (W9, delve half)

**Status update 2026-09-20** (P5): **SUPERSEDED (moot)** — `solid-remediation-todo.md:485-489`: "no
production entry exists… zero production callers of `DelveBattle.Run`." There is no delve squad
builder to populate yet. Re-open only when a delve-battle trigger ships; the dependency is noted in
both this todo and `solid-remediation`.

**Description.** `Encounter.Emit` (`Encounter.cs:206-212`) builds every delve actor with no `HubInputs`;
only the boss gets `Aptitude` (`Encounter.cs:143`). A player specimen therefore fights the Delve without
its aptitude allocation, its equipped `stat.derived` atoms, or its star/loyalty — the same specimen in a
web match gets all three (`WebMatchService.cs:600-609`). Reuse that exact projection.

**Acceptance criteria:**
- [ ] The delve party-member setup path populates `HubInputs` with `Aptitude`, `BoundAtoms` and `StarLoyalty` using the **same** producers web match uses (`EquippedBoundAtoms.DerivedFromStore`, `store.LoadAllocation`, `StarLoyaltyContribution`) — never a delve-local projection.
- [ ] Enemy/monster actors are unchanged (they have no specimen).
- [ ] The task reports a win-rate delta over the existing delve encounter fixtures before it closes. An out-of-band delta is fixed by publishing `gk-core/data/tuning/**` `v{n+1}`, not by clamping in code.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs,tests/FusionRpg.Core.Tests/Delve/DelveHubInputsTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Checkpoint 1
**Files likely touched:** `gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs`; delve setup builder; `tests/FusionRpg.Core.Tests/Delve/DelveHubInputsTests.cs`
**Scope:** M (3 files)

### Task 8 — Siege animate setups carry the player's real `HubInputs` (W9, siege half)

**Closed 2026-09-20 by pointer** (P5): **BUILT** — `solid-remediation-todo.md:474-497` T3.3:
`Encounter.cs`/`RpgStore.WorldTurns.cs:545` inversion (`HubInputsFor`); `guard-dal.ps1`/
`guard-actor-hub.ps1` green.

**Description.** `DistrictAssaultResolver.BuildAnimateSetups` (`:360-385`) names this gap itself at
`:339-345`: *"a player-owned specimen's real loadout/aptitude/equipment bonuses are NOT read here."*
Same remedy as Task 7, same producers.

**Acceptance criteria:**
- [ ] Player-owned animate setups populate `Aptitude`, `BoundAtoms` and `StarLoyalty` from the shared producers.
- [ ] Structure setups (`:307-321`) are untouched.
- [ ] The self-documenting comment at `:339-345` is updated in the same change (DESIGN-GATE §3 rule 6 — propagate the correction).
- [ ] Win-rate delta over the existing district-assault fixtures is reported before the task closes.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs,tests/FusionRpg.Core.Tests/World/DistrictAssaultHubInputsTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Task 7
**Files likely touched:** `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs`; `tests/FusionRpg.Core.Tests/World/DistrictAssaultHubInputsTests.cs`
**Scope:** S (2 files)

### Task 9 — Give `BattleHubInputs.Draughts` a production producer (W8)

**Status update 2026-09-20** (P5): **NOT-BUILT, confirmed still open** — `grep -rn "\.Draughts\s*="
src/` returns nothing; `BattleHubCompose.cs:77` still only *consumes* `inputs?.Draughts`. Not
mentioned anywhere in `solid-remediation-*`. This task stands as written — the smallest remaining
battle-derived-wire task, one producer call in the same shape T3.3 already used for Task 8.

**BLOCKED 2026-09-23 (`bdw-1`) — the row is not "one producer call"; the amount has no producer.**
`DraughtMod` carries a concrete channel + `long` amount (`DraughtProjection.cs:21`), but the authored
draught is a SEED: `ConsumableSeed` holds a `Family` + `PowerBand` and no magnitude
(`ConsumableCorpus.cs:44-57`, seed-contract.md §3), and `ConsumableCatalog` exposes only
`Resolve`/`GateManifest` — no seed→channel resolver exists (`ConsumableCatalog.cs:96,108`). There is
therefore nothing to put in `BattleHubInputs.Draughts` yet. **Named external dependency (re-confirmed
2026-09-23):** `tasks/item-todo.md`'s own OPEN row **"The seed → concrete generator — the runtime
generator's"** (~line 6839): the 60 seeds have no `effect_container`/`effect_container_atom` rows, and
rolling a seed into a container with its atom rows is a **shared-SDK** job, explicitly deferred by the
`item` program (whose module 17 made the identical deferral). `DraughtProjection`'s own doc names that
generator as the owner (`DraughtProjection.cs:11-17`). Re-open when that row ships.

**Description.** `Draughts` is declared (`BattleHubInputs.cs:27`) and read (`BattleHubCompose.cs:61-62`)
but never set, so `DraughtSubsystem` never registers. `DraughtProjection.cs:24-33` already describes the
intended road ("the same road `ExpeditionResolver.ApplyInjuries` already drives"). Drive it.

**Acceptance criteria:**
- [ ] A consumed draught's effect reaches the actor's composed `Derived` for the battle it was drunk for, through `DraughtSubsystem` — never a bespoke apply.
- [ ] The projection preserves any `HubInputs` already on the setup, exactly as `ExpeditionResolver.cs:278` does with `Injuries`.
- [ ] A squad with no active draught is byte-identical.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Items/Consumables/DraughtProjection.cs,gk-core/src/FusionRpg.Server/WebMatchService.cs,tests/FusionRpg.Core.Tests/Items/DraughtBattleReachTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Task 8
**Files likely touched:** `gk-core/src/FusionRpg.Core/Items/Consumables/DraughtProjection.cs`; `gk-core/src/FusionRpg.Server/WebMatchService.cs`; `tests/FusionRpg.Core.Tests/Items/DraughtBattleReachTests.cs`
**Scope:** M (3 files)

### Checkpoint 3: build parity across modes

- [x] The same specimen composes the same combat numbers in web match, delve and siege — proven by a test that builds one specimen and asserts equal `Derived` across the three setup producers. (Siege by `solid-remediation` T3.3; **delve has no production entry** — `DelveBattle.Run` has zero callers, so its half is superseded (moot), not outstanding.)
- [ ] Win-rate deltas recorded for delve and siege; any tuning response published as `v{n+1}` via `gk-core/tools/tuning/publish.py`. **Delve moot** (no production entry); siege's delta belongs to T8's `solid-remediation` T3.3 pointer, and the tuning response was none (0 goldens moved).
- [ ] **Full suite** — this phase crosses Core and Server: `.\scripts\test-fast.ps1 -AllDefault`. **Not this lane's to run:** CI/nightly/release-owned per the brief.

---

## Phase 4: atom triggers fire on both sides

Each task below **starts** by counting how many shipped atoms name the trigger, and records the reading.
A trigger with zero authored content lands as a seam plus a test, with no behaviour change.

### Task 10 — Raise `OnDamageTaken` and `OnDeath` in battle (W10)

**Closed 2026-09-20 by pointer** (P5): **BUILT** — `solid-remediation-todo.md:499-517` T3.4: 9 of 13
atom triggers now fire in battle (7 wired: `OnDamageTaken`, `OnSpawn`, `OnDeath`, `OnTimer`,
`OnMatchStart`, `OnMatchEnd`, `OnWave`; 2 correctly excepted: `OnSunCollect`, `OnGridPlace` — PvZ
lawn-economy, no battle analogue). `BattleTriggerCoverageTests` pins the closed 13-trigger vocabulary.
This pointer covers Tasks 10–13 below and Checkpoint 4.

**Description.** Battle already raises `OnDamageDealt` at `BasicAttack.cs:387,399`. The defender-side
twin and the death event have no battle raise at all, while the lawn raises both
(`EffectEventAdapterCore.cs:191,209`; `EventDrain.cs:640,656,668`). Raise them from the sites battle
already computes: after a landed hit, and in the death-cleanup phase (`BattleEngine.cs:661-680`).

**Acceptance criteria:**
- [ ] `OnDamageTaken` fires on the **target**, after the same landed-hit check `OnDamageDealt` uses, to both `Host.Runner` and `Host.Bag` in the same runner-before-bag order as `BasicAttack.cs:386-399`.
- [ ] `OnDeath` fires once per actor, in the death-cleanup phase, before shields are stripped.
- [ ] `ProcDepthLimit` still bounds any chain the new events start — no second counter.
- [ ] A battle whose content names neither trigger is byte-identical.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/Actions/BasicAttack.cs,gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs,tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Checkpoint 1
**Files likely touched:** `src/FusionRpg.Core/Actions/BasicAttack.cs`; `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs`
**Scope:** M (3 files)

### Task 11 — Raise `OnSpawn` in battle (W10)

**Closed 2026-09-20 by pointer** — covered by Task 10's `solid-remediation` T3.4 pointer above. Live:
`BattleRunState.cs:555` (initial roster) and `:1505` (mid-battle arrivals) both raise `OnSpawn`; the
closed 13-trigger vocabulary is pinned by `BattleTriggerCoverageTests` (`OnSpawn` row at `:33`).

**Description.** Battle creates actors at construction and at reinforcement (`BattleRunState.cs:1100`).
Neither raises `OnSpawn`; the lawn raises it at `EffectEventAdapterCore.cs:230` and `EventDrain.cs:656`.

**Acceptance criteria:**
- [ ] `OnSpawn` fires once per actor, after its `Derived` is composed and its grants are bound — never before, or the atom reads an empty snapshot.
- [ ] Reinforcement actors fire it too (`BattleRunState.cs:1100`), order-independent with respect to the round they arrive in.
- [ ] A battle whose content names no `OnSpawn` atom is byte-identical.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Task 10
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs`
**Scope:** S (2 files)

### Task 12 — Raise `OnTimer` on battle's status pulse (W10)

**Closed 2026-09-20 by pointer** — covered by Task 10's `solid-remediation` T3.4 pointer above. Live:
`BattleEngine.cs:437` raises `OnTimer` on the round clock (battle's own timer), and
`BattleTriggerCoverageTests` pins the closed 13-trigger vocabulary (`OnTimer` row at `:35`).

**Description.** The lawn's `EffectBag.TickDots` raises `OnTimer` (`EffectBag.cs:831`). Battle pulses
statuses through `BattlePulseSink` (`BattleEngine.cs:422`), which never touches the bag, so no `OnTimer`
atom can fire in a battle. Raise it from the same status-pulse event.

**Acceptance criteria:**
- [ ] `OnTimer` fires once per status-pulse event, not once per round — the two are different cadences (`BattleEngine.cs:413-428` vs `:472`).
- [ ] The event carries the same tick the pulse used (`BattleRunState.NextStatusPulseAt`), not the round clock.
- [ ] A battle with no `OnTimer` atom is byte-identical.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs,tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Task 11
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs`
**Scope:** S (2 files)

### Task 13 — Raise `OnMatchStart`, `OnMatchEnd` and `OnWave` in battle (W10)

**Closed 2026-09-20 by pointer** — covered by Task 10's `solid-remediation` T3.4 pointer above. Live:
`BattleEngine.cs:423` (`OnMatchStart`), `:424` (`OnWave`), `:759` (`OnMatchEnd`, every exit path), and
`BattleTriggerCoverageTests` pins the closed 13-trigger vocabulary (`OnMatchStart`/`OnWave` rows at
`:36`/`:38`). `OnSunCollect`/`OnGridPlace` stay lawn-only, commented as deliberate.

**Description.** Three match-scoped triggers with exact battle analogues: battle start, battle end, and
the reinforcement-wave event (`BattleEngine.cs:301-304`, `ReinforcementEventKind`). The lawn raises all
three (`EffectEventAdapterCore.cs:103,118,132`).

**Acceptance criteria:**
- [ ] `OnMatchStart` fires once before the first round event; `OnMatchEnd` once after the loop exits, on every exit path (victory, defeat, tick cap).
- [ ] `OnWave` fires on each reinforcement arrival.
- [ ] A battle whose content names none of the three is byte-identical.
- [ ] `OnSunCollect` and `OnGridPlace` are explicitly **left lawn-only**, with a one-line comment saying they are PvZ-board inputs with no battle analogue — so the next reader does not treat the omission as an oversight.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs,tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Task 12
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleTriggerFireTests.cs`
**Scope:** S (2 files)

### Checkpoint 4: trigger parity

- [x] Nine of thirteen triggers fire in battle; the four that do not (`OnSunCollect`, `OnGridPlace`
  correctly excepted; `W6`/`W7`'s two aura triggers, SR-14) are commented as deliberate — closed
  2026-09-20 by the Task 10 pointer above (corrects this line's own original "eleven" count, which
  predates the SR-14 finding).
- [x] A test asserts, per trigger, whether battle raises it — pinned against the **closed** 13-trigger vocabulary (a legitimate pin; say so in the test) and not against any content count — `BattleTriggerCoverageTests`.
- [x] `.\scripts\guard-funnel-delta.ps1` clean — part of the same T3.4 verification.

---

## Phase 5: the two subsystems with an unresolved owner reading

Both tasks land **default-off** behind a named value. **Resolver:** the owner.
**Default if the reading does not arrive:** stay off, keep the delta report, ship everything else.
Nothing downstream depends on either.

### Task 14 — Register `StatusDerivedSubsystem` in battle, default-off (W4)

**Status update 2026-09-20** (P5): **PARTIAL — a real SOLID-shaped divergence, not simple wiring.**
`solid-remediation-todo.md:464-469` T3.2 deliberately did **not** register this subsystem: battle
already owns the responsibility via `BattleStatModifierLedger` (`BattleRunState.cs:313`), so also
registering `StatusDerivedSubsystem` would double-apply. **This task as written is superseded by a
different one:** decide which of `StatusDerivedSubsystem` or `BattleStatModifierLedger` is the one
owner of status→`combat.*`, migrate the other's callers, and never register both. Routed to
`tasks/battle-wire-remainder-todo.md` W4 (`backlog-clean-up` `orphan-plan-authoring`, BCU2.7) as a
decision task, not re-attempted here.

**SUPERSEDED 2026-09-23 (`bdw-1`) — the W4 decision is MADE, in favour of the battle ledger.** Task 5
(T5 above, commit in the same segment) routes a status's `combat.*` StatMod into
`BattleDerivedModifierLedger` through `Host.AddDerivedContribution`, so **battle's own derived ledger is
the one owner of status→`combat.*`** and `StatusDerivedSubsystem` must NOT also be registered — doing
so would double-apply the same mod. This task's own acceptance (register the subsystem default-off,
read battle's `StatusRuntime` through `StatusDerivedModReader`, write a delta report into the audit)
is therefore refused as written: the first two bullets are the losing half of the decision, and the
last needs a `docs/research/**` write outside this lane's fence. `BattleStatusDerivedContributionTests`
proves the winning path. Do not re-open.

**Description.** A live status writing `stat.<combat.*>.<op>` reaches the composed value on the lawn
(`CheatState.cs:74`) and nowhere else. Battle registers no `StatusDerivedSubsystem`
(`BattleHubCompose.cs:41-64`). The reader that would feed it already exists:
`StatusDerivedModReader.Read` over a live `StatusRuntime`, and battle has one
(`BattleRunState.cs:303-306`).

**Acceptance criteria:**
- [x] `BattleHubCompose` registers `StatusDerivedSubsystem` when a named value is on; off is byte-identical to today. **REFUSED by the W4 decision above:** registering it would double-apply every status `combat.*` mod that Task 5's derived-ledger path already carries. Pinned by `BattleStatusDerivedContributionTests.Battle_registers_progression_but_not_the_status_derived_subsystem`.
- [x] The delegate reads battle's own `StatusRuntime` through the existing `StatusDerivedModReader` — never a battle-local reader. **REFUSED with the bullet above** — there is no registered status subsystem to feed; battle reads its own `StatusRuntime` directly in `Status.OnApplied`/`OnEnded`.
- [x] Interaction with Task 5 is decided and tested: a status must contribute through **one** of the two paths, not both. The test asserts no double-count. (`BattleStatusDerivedContributionTests.Battle_registers_progression_but_not_the_status_derived_subsystem` — the subsystem set contains `rpg.progression` and does NOT contain `l2b.derived`.)
- [x] A delta report (composed `combat.*` before/after, over the existing battle fixtures) is written into the audit and handed to the owner. (Written 2026-09-23 under the manager's grant: `docs/research/battle-derived-wire-audit-2026-09-16.md` §7a — base 7 → +200 status = 207, withdrawal → 7; fixture delta 0 because no shipped status authors a `stat` block.)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs,tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedSubsystemTests.cs -Session battle-derived-wire-20260916` — the named test file does not exist; the assertion lives in `BattleStatusDerivedContributionTests.cs`, run with `-AllowUnscoped`; evidence in the evidence file.

**Dependencies:** Task 6
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`; `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedSubsystemTests.cs`
**Scope:** M (3 files)

### Task 15 — Register `RpgProgressionSubsystem` in battle, default-off (W5, W17)

**Status update 2026-09-20** (P5): **W5 half BUILT** — `solid-remediation-todo.md:426-472` T3.1
(ratification question answered: NOT ratified, per `decisions.md:51`) → T3.2 registers it; 0 goldens
moved. **It landed always-on, not default-off as this task specifies** — an owner-adjacent ruling in
T3.1, not a defect to fix. **W17 half (`progression.bonus.*` → battle) still NOT-BUILT, confirmed
today:** `BattleHubCompose.cs:92` still calls `hub.ResolveDerived(ctx)`, never `hub.Resolve(ctx)` — the
exact line this task's own bullet 2 named as needing a **separate** task if the owner wants it. That
separate task is now written: `tasks/battle-wire-remainder-todo.md` W17 (BCU2.7) — an H1 golden-move
task, not re-attempted here.

**W17 CLOSED 2026-09-23 (`bdw-1`) — the H1 integration is done; 0 goldens moved.** `BattleHubCompose`
now exposes `Resolve(setup)`, which calls `hub.Resolve(ctx)` (the merge itself — never a second fold),
while `Compose` keeps `hub.ResolveDerived(ctx)` so callers that have not configured `StatsTuningHub`
(`gk-core/tools/ProveAptitude`) are unchanged. `ActorState` consumes the merge by the delta
`AppliedCombat − RuntimePrimary`: `MaxHp` gains its maxHp term, `BaselineDefense` and the composed
`combat.defense.omni` gain its defense term (arm1/arm2 have no battle analogue and are ignored).

**Printed readings** (`BattleProgressionSubsystemTests`, shipped `aptitudes.v10.json`, `Fortitude`
carries the maxHp edge k=8000 and the defense edge k=10000): no allocation → `maxHp=215 defense=7`;
`Fortitude(7)` → `maxHp=1935` (delta **1720**) and `defense=2351` (delta **2344**). **0 of 5 battle
goldens moved** (`BattleGoldenTests` 5/5) because every golden fixture is bare — no `HubInputs.Aptitude`
— so the bonus is 0 there; no re-bless was needed. The earlier "H1 golden-moving" estimate was the
measurement, and the actual reading is that the fixtures do not carry the inputs.
⚠ `tasks/battle-wire-remainder-todo.md` BWR1.6 duplicates this row; that file is outside this lane's
fence, so the manager should close BWR1.6 by pointer to this commit.

**Description.** `progression.power`/`progression.realm` are absent from every battle snapshot, so
`ActorDerivedSnapshot.TierPower` (`:44-45`) falls back to `1.0` and `ResistanceEvaluator.cs:278,302`
loses its level term in battle while keeping it on the lawn. Battle already has a Θ
(`BattleHubCompose.cs:39`); registering the subsystem with a `FixedPowerIndexProvider(theta)` is one
line of the shape already used at `BattleHubCompose.cs:47`.

**Acceptance criteria:**
- [x] Off is byte-identical. On, `progression.power`/`realm` compose from battle's own Θ — never a second power curve (`ssot-power-scale.md`, one ladder). (W5 half, built; 0 goldens moved)
- [x] The task states explicitly whether `progression.bonus.*` should also reach battle. If yes, it is a **separate** task, because it requires battle to consume `AppliedCombat` and battle currently calls only `ResolveDerived` (`BattleHubCompose.cs:71`) — do not fold two changes into one. (Stated yes; the separate task is W17/BWR1.6 and is now DONE in this commit — see the readings above)
- [x] A status-contest delta report across levels is produced and handed to the owner. (Written 2026-09-23 under the manager's grant: `docs/research/battle-derived-wire-audit-2026-09-16.md` §7b — `progression.power` L1=1 L5=5 L10=10 L20=20 from battle's own Θ; W17 `Fortitude(7)` maxHp 215→1935 (Δ1720), defense 7→2351 (Δ2344); fixture delta 0, goldens 5/5.)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs,gk-core/tests/FusionRpg.Core.Tests/Battle/BattleProgressionSubsystemTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped` (plus `BattleEngine.cs`/`BattleRunState.cs`); printed readings in the §T15/W17 fragment.

**Dependencies:** Task 14
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs`; `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleProgressionSubsystemTests.cs`
**Scope:** S (2 files)

### Checkpoint 5: owner reading

- [ ] Both subsystems registered and default-off; both delta reports written into the audit.
- [ ] The owner has the two readings. **Not a gate** — the program proceeds to Phase 6 regardless.

---

## Phase 6: cleanup of channels with no reader

### Task 16 — Element-typed readers for parry, block and reflect (W12)

**Closed 2026-09-20 by pointer** (P5): **BUILT** — `solid-remediation-todo.md:223-241` T2.3: extended
to `omni + element`; `PerElementAvoidanceTests` (61 cases); 0 goldens moved (no content authors these
yet, as expected).

**Description.** Twelve families register 7 slots each (`DerivedStatChannels.cs:167-182`) but their
readers are omni-only (`CombatDerivedReader.cs:58-65,69-72`), leaving 72 registered channels unreadable
in any mode. Extend the readers to the element-typed shape the other 16 families already use
(`CombatDerivedReader.cs:9-50`).

**Acceptance criteria:**
- [ ] Each of the 12 families gains an element overload following the existing `(snap, element)` pattern; the omni overload is unchanged.
- [ ] The calculator consumes the element form on its per-component path and the omni form on its `Components.Count == 0` fallback — matching how `Power`/`Defense` already split (`OverlayCombatCalculator.cs:143-155` vs `:166-202`).
- [ ] With every element slot at 0 the result is byte-identical.
- [ ] The self-documenting comments at `CombatDerivedReader.cs:53-57,67-68` are updated in the same change.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Combat/CombatDerivedReader.cs,gk-core/src/FusionRpg.Core/Combat/OverlayCombatCalculator.cs,gk-core/tests/FusionRpg.Core.Tests/Combat/CombatDerivedReaderTests.cs -Session battle-derived-wire-20260916`

**Dependencies:** Checkpoint 1
**Files likely touched:** `gk-core/src/FusionRpg.Core/Combat/CombatDerivedReader.cs`; `gk-core/src/FusionRpg.Core/Combat/OverlayCombatCalculator.cs`; `gk-core/tests/FusionRpg.Core.Tests/Combat/CombatDerivedReaderTests.cs`
**Scope:** M (3 files)

### Task 17 — Register `turn.moveSpeed`, or delete it (W15)

**CLOSED 2026-09-23 (`bdw-1`) — deleted; removal note relocated in-fence (erratum request).**
`DerivedTurnChannels.MoveSpeed` had zero references repo-wide, so it was deleted and the removal note
placed in the declaring type plus the in-fence `docs/architecture/battle/spec-readiness-model.md`,
which already discusses the reserved movement family. **Erratum requested:** the acceptance names
`docs/architecture/battle-timeline-map.md`, which is outside this lane's fence
(`docs/architecture/battle*/**` matches the `battle/` and `battle-tempo/` DIRECTORIES only; verified
against `verify-change.ps1`'s own `Matches-SessionPath`). If the manager requires the note in that file,
it is a one-line addition for whoever owns it. A new guard
(`TurnChannelDeclarationTests.Every_declared_turn_channel_is_registered`) now fails if a
declared-unregistered turn channel is ever reintroduced.

**Description.** `turn.moveSpeed` is declared (`Battle/Timeline/DerivedTurnChannels.cs:21`) and never
registered (`DerivedStatRegistry.cs:119-125` registers only `Speed` and `Haste`). Either it has a reader
and should be registered, or it does not and should go. A declared-unregistered channel is the exact
shape that makes the next channel census wrong.

**Acceptance criteria:**
- [x] Either registered with a named consumer, or deleted with a one-line note in `battle-timeline-map.md`. (Deleted; note relocated to the declaring type + `docs/architecture/battle/spec-readiness-model.md` because the named file is out of fence — erratum requested)
- [x] `DerivedAuditCoverage.RegistryPin` (`:39`) updated if the census moves, with the reason stated. (The channel was never registered, so the census does not move; stays 268)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/Timeline/DerivedTurnChannels.cs,gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs,tests/FusionRpg.Core.Tests/Stats/DerivedStatRegistryTests.cs -Session battle-derived-wire-20260916` — the named test file does not exist; ran the real one (`gk-core/tests/FusionRpg.Core.Tests/Stats/TurnChannelDeclarationTests.cs`) with `-AllowUnscoped`; printed evidence in the §T17 fragment.

**Dependencies:** None
**Files likely touched:** `gk-core/src/FusionRpg.Core/Battle/Timeline/DerivedTurnChannels.cs`; `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs`; `tests/FusionRpg.Core.Tests/Stats/DerivedStatRegistryTests.cs`
**Scope:** S (3 files)

### Task 18 — Feed `loadout.slots`, or mark it reserved (W14)

**CLOSED 2026-09-23 (`bdw-1`) — option (b) implemented in-fence.** The channel is now listed as
reserved in the task's named home, `DominanceGuard.BuildReservedFamilies` (`loadout.slots`, with an
in-line reason and an amended class doc that scopes its "matches the tracked baseline exactly" claim),
and its own registry row carries a `UnitClassNote` recording that readers exist but no production site
supplies a nonzero value. The three XML doc comments now state the unfed status, and
`LoadoutSlotsChannelTests` asserts both the reservation and the unchanged-at-0 behaviour.

**Option (a) remains the Data-layer owner's to do, and is the honest fix:** the only feeder seam is
`RpgStore.SetLoadout`/`AutoEquip.Select` (`RpgStore.Loadouts.cs:46,121`, `FusionRpg.Data` — outside
this lane's fence), which take no channel parameter; `ActionLoadoutService.Set`
(`gk-core/src/FusionRpg.Server/Gates/ActionLoadoutService.cs:31`) holds no composed `Derived` for the
player-commander scope. Note also: `loadout.slots` carries ZERO aptitude edges
(`gk-core/data/tuning/aptitudes.v10.json`), so this entry is a content-granted channel the predictor cannot
exercise, not an aptitude-spend family.

**Description.** Three consumers take the value as a defaulted parameter (`LoadoutSet.cs:57`,
`gk-core/src/FusionRpg.Core/Actions/Grants/CapPolicy.cs:44`, `AutoEquip.cs:38`) and no production site ever supplies it, so the channel is dead at
runtime while looking wired in every doc comment. Supply it from the actor's composed `Derived` at the
loadout-resolve seam, or add it to `DominanceGuard.BuildReservedFamilies` (`:110-133`) with the same
in-line reason that family already carries.

**Acceptance criteria:**
- [x] Either a production call site passes `derived.Get(DerivedStatChannels.LoadoutSlots)`, or the channel is listed as reserved with a stated reason. (Option (b): `DominanceGuard.BuildReservedFamilies` + the registry row's `UnitClassNote`)
- [x] The three XML doc comments stop implying a live reader if it stays reserved (DESIGN-GATE §3 rule 6). (`LoadoutSet.EffectiveMaxSize`, `CapPolicy.EquippedSkillCap`, `AutoEquip.Select` now state the unfed status)
- [x] With the channel at 0, loadout size is unchanged. (`EffectiveMaxSize_with_nothing_worn_is_the_structural_base_five`; `Validate_with_no_channel_argument_keeps_the_original_five_slot_behaviour`)

**Verification:**
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Actions/Loadout/LoadoutSet.cs,gk-core/src/FusionRpg.Core/Actions/Grants/CapPolicy.cs,gk-core/tests/FusionRpg.Core.Tests/Actions/LoadoutSlotsChannelTests.cs -Session battle-derived-wire-20260916` — ran with `-AllowUnscoped` (plus `DominanceGuard.cs`/`AutoEquip.cs`); printed evidence in the §T18 fragment.

**Dependencies:** None
**Files likely touched:** `gk-core/src/FusionRpg.Core/Actions/Loadout/LoadoutSet.cs`; `gk-core/src/FusionRpg.Core/Actions/Grants/CapPolicy.cs`; `gk-core/tests/FusionRpg.Core.Tests/Actions/LoadoutSlotsChannelTests.cs`
**Scope:** S (3 files)

### Cross-program finding — the missing-reader families (W16, R1–R4) — linked, not duplicated

**This is ONE finding seen from two audits.** It is recorded here and in `class-system-todo.md`, and the
two rows point at each other, so neither program re-discovers it as its own new gap.

**The families:** `resource.efficiency.*`; `skill.cooldown` and `skill.effectiveness` for 4 of the 5
categories (no shipped action names them); `progression.xpRate` / `progression.breakthroughSuccess`;
`move.range`. R1–R4 add `status.expose.*`, non-hp `resource.restore.*`, and the same cooldown /
effectiveness absence.
**Two independent readings agree:**

- This program's audit, `docs/research/battle-derived-wire-audit-2026-09-16.md:433` (W16) and `:440-443`
  (R1–R4); `DerivedStatRegistry.cs:198,204` state the skill-family half in-line.
- `class-system`'s P9 readiness gate, live 2026-08-27: `scripts/gate-class-system-phase9.ps1` exits 1
  reporting *"6 of 48 aptitude-fed families still have no reader (18 of 486 edges, 3.7%) — not ready:
  resource.efficiency, skill.cooldown, skill.effectiveness, move.range, progression.xpRate,
  progression.breakthroughSuccess"* (`tasks/class-system-todo.md:665`), matching
  `gk-core/scripts/audit-reader-census.py --json`'s `families_without_reader` exactly.

**The cause, read rather than inferred:** no consumer subsystem exists for these families. The layer
that would read them is the action-cost / usability layer `class-system`'s P9 gate measures; this
program cannot supply it. Building one here is refused by this plan's own [Explicit
non-goals](battle-derived-wire-plan.md) — so the channel inventory lives here and the reader lives
there, deliberately.

**Disposition:** not a W-item to close in this program, and not a P9 defect in that one — one open
gap with one owner. Until a reader ships, every one of these channels is `no-producer` on the derived
sheet, which is the honest state, not a regression. Merged write-up: `backlog-clean-up` BCU8.9,
2026-09-20.

### Checkpoint 6: program complete

**2026-09-23 (`bdw-1`) — closed ledger built; the remaining boxes name their blockers.**

- [x] Every **wiring gap** W1–W17 is closed, or explicitly reclassified with a cited reason. (Closed ledger in `tasks/battle-derived-wire-evidence.md` §W1–W17: 15 closed, W8 blocked on the `item` program's seed→concrete row, W9 delve half superseded (moot), W16 another program's — each with its landing commit.)
- [x] The audit document is updated in place — §7's wiring-gap table becomes a closed ledger, and §8's "could not determine" items 2 and 3 are answered with readings. (Written 2026-09-23 under the manager's grant: `docs/research/battle-derived-wire-audit-2026-09-16.md` now carries the closed ledger table (every W1–W17 with a disposition + landing commit) and §8 items 2/3 each with an `Answered 2026-09-23` reading.)
- [ ] **Full suite** — end of program: `.\scripts\test-fast.ps1 -AllDefault`. **CI-OWNED, not run by this lane** (manager ruling 2026-09-23: the brief wins over the todo here — CI owns unfiltered full evidence, and the manager-run CC8 greens stand as the evidence). Deliberately left unticked because no run happened here.
- [x] All five boundary guards clean. (`guard-actor-hub`/`guard-single-writer`/`guard-funnel-delta`/`guard-dal` 4/4 OK, plus `battle-responsibility` and `funnel-delta` in every path-owned run.)
- [ ] A live probe through the **RPG Server Debug** scope (a real `/api` battle resolve on a real stored specimen, read back through the normal query path) confirms the same specimen's numbers match between its sheet and its battle. **Blocked on a live slot and a running server/game (owner-side):** not runnable from an unattended lane; `docs/contributing/live-probe-standard.md` governs it.

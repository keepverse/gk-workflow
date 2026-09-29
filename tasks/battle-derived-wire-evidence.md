# battle-derived-wire — evidence fragments

One section per closed task. Shape: `| Criterion | Command | Result | Artifact |`. Commands are copied
from the command line as run; `verify-change.ps1` is invoked with `-AllowUnscoped` because no
`tasks/sessions/bdw-1.json` record exists and `tasks/sessions/**` sits outside this lane's fence (the
same path-owned selection runs either way; the explicit filter rows are the printed numbers).

## W1–W17 closed ledger (Checkpoint 6's "§7 becomes a closed ledger")

The audit's §7 table lives in `docs/research/battle-derived-wire-audit-2026-09-16.md`, which is outside
this lane's fence, so the closed ledger is recorded here instead. Every wiring gap now has a
disposition and a landing pointer; the two that are not "closed" name their exact dependency.

| W | Disposition | Landing / blocker |
|---|---|---|
| W1 `CombatMath` on battle's bag | CLOSED | `solid-remediation` T2.5 (2026-09-17) |
| W2 `ActorResolve` on battle's bag | CLOSED | `solid-remediation` T2.5/T2.6 |
| W3 reflect step unreachable from battle HP apply | CLOSED | T2/W3, `6c8187e20` (0 of 5 goldens moved) |
| W4 status→`combat.*` has no battle owner | CLOSED by DECISION | T5/T14, `1021589c6` — battle's derived ledger owns it; `StatusDerivedSubsystem` must NOT be registered |
| W5 `RpgProgressionSubsystem` unregistered | CLOSED | `solid-remediation` T3.1/T3.2 (always-on) |
| W6 `Host.AddDerivedContribution` had zero invokers | CLOSED | T5/W6, `1021589c6` — status `combat.*` mods are its production invoker |
| W7 `ActiveAuras` had zero production writers | CLOSED | T4/W7, `474c92d74` — `WebMatchService.ActiveAurasFor` |
| W8 `Draughts` has zero production writers | **BLOCKED (external)** | `tasks/item-todo.md` ~line 6839, "The seed → concrete generator" — no seed→channel resolver exists, so no `DraughtMod` amount can be produced |
| W9 delve/siege `HubInputs` | siege CLOSED; delve SUPERSEDED (moot) | `solid-remediation` T3.3; delve has no production entry (`DelveBattle.Run` zero callers) |
| W10 atom triggers in battle | CLOSED | `solid-remediation` T3.4 (7 triggers) + T4/W7 + T5/W6 (the 2 aura triggers); 2 correctly excepted (`OnSunCollect`, `OnGridPlace`); `BattleTriggerCoverageTests` pins the closed 13-trigger vocabulary |
| W11 status-sourced `defense` stored and never read | CLOSED | T6/W11, `5e33ad647` — one gate owns `combat.defense.omni` |
| W12 72 per-element avoidance channels unread | CLOSED | `solid-remediation` T2.3 |
| W13 `resource.restore.hp` battle-unreachable | CLOSED | T3/W13, `aee1ebe8d` (DoT-pulse half by `solid-remediation` T2.6) |
| W14 `loadout.slots` never fed | CLOSED (option b) | T18/W14, `ce6e602be` — reserved with a stated reason; option (a) stays the Data-layer owner's |
| W15 `turn.moveSpeed` declared-unregistered | CLOSED | T17/W15, `18139aec6` — deleted; a guard prevents reintroduction |
| W16 `skill.cooldown/effectiveness` content absent | NOT THIS PROGRAM'S | cross-linked to `class-system` P9.0 (one finding, two documents) |
| W17 `progression.bonus.*` never reaches battle | CLOSED | T15/W17, `ee4d217bc` — readings below (maxHp 215→1935, defense 7→2351; 0 of 5 goldens moved) |

**§8 item 2 (element-payload blast radius):** answered by the Task 0 spike at
`docs/research/battle-effect-payload-spike-2026-09-17.md` (out of fence; referenced, not re-derived).

**§8 item 3 (`TierPower = 1.0` neutral or a real shift):** W5 registered `RpgProgressionSubsystem`, so
`progression.power` now composes from battle's own Θ through `FixedPowerIndexProvider(theta)` — never a
second curve. The cross-level status-contest delta report Checkpoint 6 asks for belongs in
`docs/research/**` (out of fence); the mechanism is closed, the report is owed to the audit's owner.

**Checkpoint 6's other boxes:** all five boundary guards are clean (readings above); the full suite is
CI/nightly/release-owned per this lane's brief; the live RPG-Server-Debug probe needs a live slot and a
running server/game (owner-side), so it is not runnable from this lane.

## T3 / W13 — `resource.restore.hp` reaches battle's `ApplyHp`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Positive `ApplyHp` adds the healer's `resource.restore.hp`, floored at 0, one formula | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleHealPowerTests"` | Passed 4, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHealPowerTests.cs` |
| Same expression as `OverlayCombatMath.cs:86` — no second formula | same — `Battle_heal_is_the_one_OverlayCombatMath_formula` asserts equality against a direct `OverlayCombatMath.Finalize` call | passed | same |
| Healer at `resource.restore.hp == 0` heals exactly the authored amount | same — `Zero_heal_power_heals_exactly_the_authored_amount` | passed | same |
| §4.3 not reopened (no matchup / roll / defender term) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~HealingPairTests"` | Passed 11, Failed 0, Skipped 0 | existing `Combat/HealingPairTests.cs` |
| Boundary guards | `guard-actor-hub` · `guard-single-writer` · `guard-funnel-delta` · `guard-dal` | 4/4 OK (printed verdicts) | — |
| Path-owned selection | `pwsh -NoProfile -ExecutionPolicy Bypass -Command "& './scripts/verify-change.ps1' -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHealPowerTests.cs') -AllowUnscoped"` | all selected checks passed | this file |

## T6 / W11 — one gate owns `combat.defense.omni`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| One writer; `stat.modify` and the status-sourced mod share it | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleDefenseOwnershipTests"` | Passed 5, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleDefenseOwnershipTests.cs` |
| Status mod + `stat.modify` sum, idempotent under two recomposes | same — `A_status_mod_and_a_stat_modify_sum_and_survive_two_recomposes` (base + 10 + 20) | passed | same |
| Aura and `stat.modify` do not clobber across a round boundary | same — `An_aura_and_a_stat_modify_do_not_clobber_each_other_across_a_round_boundary` (base + 20 + 40) | passed | same |
| Battle goldens unmoved (no shipped content authors a `defense` status mod) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleGoldenTests"` | Passed 5, Failed 0 | `tests/.../Battle/BattleGoldenTests.cs` |
| Path-owned selection (6 paths) + guards | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs','gk-core/src/FusionRpg.Core/Battle/BattleDerivedModifierLedger.cs','gk-core/src/FusionRpg.Core/Battle/BattleStatModifierLedger.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/BattleDefenseOwnershipTests.cs') -AllowUnscoped` | exit 0 — all selected checks passed (incl. `battle-responsibility`, `funnel-delta` guards) | — |
| Boundary guards | `guard-actor-hub` · `guard-single-writer` · `guard-funnel-delta` · `guard-dal` | 4/4 OK | printed verdicts |

## T18 / W14 — `loadout.slots` is listed as reserved (option (b))

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Listed as reserved with a stated reason | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~LoadoutSlotsChannelTests|FullyQualifiedName~TurnChannelDeclarationTests"` | Passed 13, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Actions/LoadoutSlotsChannelTests.cs` |
| The three doc comments stop implying a live reader | same run — the three XML docs now say no production site supplies a value | passed | `LoadoutSet.cs`, `CapPolicy.cs`, `AutoEquip.cs` |
| At 0, loadout size unchanged | same — `EffectiveMaxSize_with_nothing_worn_is_the_structural_base_five`, `Validate_with_no_channel_argument_keeps_the_original_five_slot_behaviour` | passed | same |
| Path-owned selection (T17+T18 paths) + guards | `verify-change.ps1 -Paths @(...9 paths...) -AllowUnscoped` | exit 0 — all selected checks passed; 0 HIGH doc-citation findings | `/tmp/bdw-verify-t1718.txt` |

## T17 / W15 — `turn.moveSpeed` deleted (note relocated in-fence)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Deleted, not merely unregistered | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~TurnChannelDeclarationTests"` | Passed 2, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Stats/TurnChannelDeclarationTests.cs` |
| Removal note | placed in `DerivedTurnChannels.cs` (the declaring type) and `docs/architecture/battle/spec-readiness-model.md` — the task's named home `battle-timeline-map.md` is OUTSIDE this lane's fence (`docs/architecture/battle*/**` matches directories only; verified with `Matches-SessionPath`) | note present | both files |
| Census unchanged | the channel was never registered, so `DerivedAuditCoverage.RegistryPin` stays 268 (bullet is conditional on the census moving) | no change | `DerivedAuditCoverage.cs:39` |
| Path-owned selection | same combined run as T18 | exit 0 | `/tmp/bdw-verify-t1718.txt` |

## T2 / W3 — battle's direct HP path reaches the reflect step

Measure first (Task 0 discipline): `grep -l "combat.reflect" gk-data/packs/fusion/data/seed/passive-tree/nodes/*.json | wc -l` → **26** node files author reflect, and `gk-data/packs/fusion/data/seed/atoms/aura-content.json` authors `combat.reflect.damage.omni`; **no battle golden fixture carries a reflect channel**, so the change is inert on every golden.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A defender with reflect bounces onto the attacker | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleReflectTests|FullyQualifiedName~BattleGoldenTests"` | Passed 8, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleReflectTests.cs` |
| At reflect 0 the attacker takes nothing / goldens unmoved | same — `With_reflect_at_zero_the_attacker_takes_nothing` + `BattleGoldenTests` 5/5 | passed, **0 of 5 goldens moved** | same |
| `ProcDepthLimit` is the only bound | same — `A_mutual_reflect_chain_terminates_under_ProcDepthLimit` | passed | same |
| `TryReflect` reused, not copied; battle reaches it, not `DispatchInstant` | `dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests -c Release --nologo --filter "FullyQualifiedName~ReflectHasNoBattlePathTests"` | Passed 3, Failed 0, Skipped 0 | `tests/FusionRpg.Core.PassiveTree.Tests/.../ReflectHasNoBattlePathTests.cs` |
| Path-owned selection + guards | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/src/FusionRpg.Core/PassiveTree/Binding/BinderRunReport.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/BattleReflectTests.cs','gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Binding/ReflectHasNoBattlePathTests.cs') -AllowUnscoped` | exit 0 — 69 project runs, 0 failures, incl. `Core.Balance.Tests` 301/301 and `ResidualFitLoopTests` | `/tmp/bdw-verify-t2w3.txt` |
| Boundary guards | `guard-actor-hub` · `guard-single-writer` · `guard-funnel-delta` · `guard-dal` | 4/4 OK | printed verdicts |

## T4 / W7 — the first production `ActiveAuras` writer

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| No active aura → empty list (byte-identical battle) | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --filter "FullyQualifiedName~WebMatchAuraDeliveryTests"` | Passed 3, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Server.Tests/WebMatchAuraDeliveryTests.cs` |
| One active aura → its grant channel, shipped reference value, `CommanderSide == "squad"` | same — `An_active_aura_projects_its_grant_channel_with_the_shipped_reference_value` (value equals `AuraMagnitude.ReferenceChannelValue(0, 1, pin, AuraTuningHub.Tuning, AptitudeTuningHub.Tuning)`) | passed | same |
| Order-independent (fresh read, never cached) | same — `The_active_set_is_read_fresh_so_the_order_of_enable_and_read_does_not_matter` | passed | same |
| Delivery to matching-`Side` actors only | Core `AuraDeliveryTests.Wave_side_aura_does_not_touch_squad` (existing, unchanged) | passed in the path-owned run | `gk-core/tests/FusionRpg.Core.Tests/Battle/AuraDeliveryTests.cs` |
| Path-owned selection + guards | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/WebMatchService.cs','gk-core/src/FusionRpg.Server/AtomPushService.cs','gk-core/src/FusionRpg.Server/AuraRuntimeEndpoints.cs','gk-core/tests/FusionRpg.Server.Tests/WebMatchAuraDeliveryTests.cs') -AllowUnscoped` | exit 0 — Server.Tests 819/819, 0 failures | `/tmp/bdw-verify-t4.txt` |
| Boundary guards | `guard-actor-hub` · `guard-single-writer` · `guard-funnel-delta` · `guard-dal` | 4/4 OK | printed verdicts |

## T5 / W6 — status→`combat.*` reaches the derived ledger (the W4 decision)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `combat.*` mod reaches the composed derived; primary does not | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleStatusDerivedContributionTests|FullyQualifiedName~BattleGoldenTests|FullyQualifiedName~BattleDefenseOwnershipTests|FullyQualifiedName~BattleHealPowerTests|FullyQualifiedName~BattleReflectTests|FullyQualifiedName~BattleStatusStatModsTests"` | Passed 23, Failed 0, Skipped 0 | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedContributionTests.cs` |
| Withdrawal reverts to the frozen base | same — `Withdrawing_the_status_reverts_to_the_frozen_base` | passed | same |
| `increased` on a FlatSum `combat.*` channel contributes nothing | same — `An_increased_op_on_a_combat_channel_contributes_nothing` | passed | same |
| No `combat.*` status → byte-identical | same — `BattleGoldenTests` 5/5 (no shipped status authors a `stat` block) | 0 goldens moved | `tests/.../Battle/BattleGoldenTests.cs` |
| Path-owned selection + guards | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/BattleStatusDerivedContributionTests.cs') -AllowUnscoped` | exit 0 — 69 project runs, 0 failures | `/tmp/bdw-verify-t5.txt` |
| W4 decision cannot regress (no `StatusDerivedSubsystem` in battle) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleStatusDerivedContributionTests"` | Passed 5, Failed 0, Skipped 0 — `Battle_registers_progression_but_not_the_status_derived_subsystem` asserts `rpg.progression` present and `l2b.derived` absent | `BattleStatusDerivedContributionTests.cs` |

## T15 / W17 — `progression.bonus.*` reaches battle

Measure first (Task 0 discipline): `gk-core/data/tuning/aptitudes.v10.json` carries **6 edges into `progression.bonus.*`** (maxHp 2, defense 2, arm1 1, arm2 1); `Fortitude` carries the maxHp edge (k=8000) and the defense edge (k=10000).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `hub.Resolve(ctx)` is the merge; `Compose` stays `ResolveDerived` (no new `StatsTuningHub` dependency) | `dotnet test gk-core/tests/FusionRpg.Core.ClassSystem.Tests -c Release --nologo --filter "FullyQualifiedName~ProveAptitudeJsonEmitTests"` | Passed 4, Failed 0, Skipped 0 | `gk-core/tools/ProveAptitude` fixture |
| `progression.bonus.maxHp` reaches the battle pool | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleProgressionSubsystemTests" --logger "console;verbosity=detailed"` | **printed reading:** no-allocation `maxHp=215`; `Fortitude(7)` `maxHp=1935` (**delta 1720**) | `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleProgressionSubsystemTests.cs` |
| `progression.bonus.defense` reaches the composed defense | same run | **printed reading:** no-allocation `defense=7`; `Fortitude(7)` `defense=2351` (**delta 2344**) | same |
| Goldens unmoved (H1) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --filter "FullyQualifiedName~BattleGoldenTests"` | Passed 5, Failed 0 — **0 of 5 moved** (every fixture is bare: no `HubInputs.Aptitude`, so the bonus is 0) | `tests/.../Battle/BattleGoldenTests.cs` |
| Path-owned selection + guards | `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs','gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/BattleProgressionSubsystemTests.cs') -AllowUnscoped` | exit 0 — 70 project runs, 0 failures | `/tmp/bdw-verify-w17.txt` |

## Cross-lane finding — Expeditions regression on the merged head — **RESOLVED (2026-09-23, later merge)**

Recorded, then resolved; kept here because the diagnosis is still the useful part if it returns.

`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:186` — `PlannedRungFor` runs
`wave.Select(e => CreatureSpeciesCatalog.Get(e.SpeciesId).BaseRarity).Max().ToId()` with **no empty-wave
guard**, so `ExpeditionResolver.Resolve` throws `InvalidOperationException: Sequence contains no
elements` whenever the tier's wave roster resolves empty.

**Seen:** 2026-09-23 mid-day, `FusionRpg.Core.Expeditions.Tests` = **Failed 11, Passed 27, Total 38**,
with `ExpeditionResolver`'s own tier goldens failing — after `d9d1b3195` (`creature-seed` T10,
"expedition wild-band rank floor") landed in one merge but the wave-roster data/bootstrap it needs
landed in a LATER one. **Proven not this lane's:** reverting this lane's only source edit and re-running
still failed 9 of 11 `ExpeditionResolverTests`, and `ExpeditionResolver` has zero references to
`BattleHubCompose`.

**Resolved:** a subsequent `features/mega-merge` (head `de5e0d363`) carries the missing half —
`dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests -c Release --nologo` now reads **Passed 38, Failed 0,
Skipped 0, Total 38**. No code change was needed in this lane; the earlier failure was a transient
half-merged state, not a defect this lane introduced or owns.

## Cross-lane finding — `combat-ai` docs cited moved lines in battle files — **RE-ANCHORED (2026-09-23)**

Found while re-checking this lane's own citation obligations, then fixed: `docs/architecture/combat-ai/**`
is inside this lane's fence (`docs/architecture/combat*/**`), and the manager's triage ruled the work
in — so the drifted citations were re-anchored here rather than routed. **35 citation tokens across 11
docs** now point at the symbol each one names.

Why it needed finding at all: the doc-citation guard cannot see this class — the cited line still
EXISTS, so it reports neither D1 nor D2, and only the **content** is wrong.

| Was (occurrences reproduced with `grep -rho`) | Names | Now |
|---|---|---|
| `BattleRunState.cs:687-699` (12) | the battle's one AI-source construction (`if (aiTuning != null)` → `new SiegeAiIntentSource(…)`) | `BattleRunState.cs:743-757` |
| `BattleRunState.cs:1037-1044` (4) + `:1043-1044` (2) | `AggressionOf` composing `combat.aggression` | `BattleRunState.cs:1089-1090` |
| `BattleRunState.cs:877-885` (3) | the live-roster build filtering on `a.Active` | `BattleRunState.cs:939` |
| `BattleRunState.cs:595-620` (3) + `:597-604` (2) | the degrade-to-basic-attack-with-a-warning branches | `BattleRunState.cs:637-681` |
| `BattleEngine.cs:673-694` (3) | the `DownedOnDeplete` death-cleanup region | `BattleEngine.cs:689-694` |
| `BattleEngine.cs:683` (1) | the delve `DownedOnDeplete` + `PartyIndex` branch | `BattleEngine.cs:699` |
| `BattleEngine.cs:85` (1) + `:85-88` (1) | `Alive => Hp > 0` / `Active => Alive && !Retreated` | `BattleEngine.cs:99` / `:99-102` |
| `BattleEffects.cs:238-250` (3) | the plan-item handler table (four-action allowlist) | `BattleEffects.cs:241-264` |
| `BattleRunState.cs:118` (1) | `ActionCatalog` wired into battle | `BattleRunState.cs:297` |
| `BattleEngine.cs:182-183` (1, in-fence copy) | claimed "shield `DurationMs` ceilings ms→rounds" | **claim retired, not just moved** — B17 removed the ceiling (`BattleRunState.cs:560-576`); the `battle/spec-virtual-time-core.md` cell now says so and cites `ShieldRuntime.cs:361` |

Left alone deliberately: `docs/architecture/battle/audit-2026-08-21.md:59` carries the same
`BattleEngine.cs:182-183` token, but a dated audit is a historical record of what was read that day,
not a live claim.

Reading: `guard-doc-citations.ps1` → **0 HIGH** (D1 694, D2 7, D3 56, D4 0), and a `grep` for the old
tokens across the re-anchored docs returns **0**.

## Manager triage — every remaining blocked row, one line each (2026-09-23)

### Rulings → closing commit (the granted rows are DONE; recorded so they are not re-worked)

| Ruling | Row | Closed by | Evidence in that commit |
|---|---|---|---|
| (1) audit write granted | T14 bullet 4 | **`ba4a8d0e5`** | audit §7a — W4 before/after: base 7 → +200 status = 207, withdrawal → 7; fixture delta 0 |
| (2) audit write granted | T15 bullet 3 | **`913a6d76e`** | audit §7b + the new printed reading: `progression.power` L1=1 L5=5 L10=10 L20=20; `Fortitude(7)` maxHp 215→1935 (Δ1720), defense 7→2351 (Δ2344) |
| (3) audit write granted | Checkpoint 6 | **`bd30cd7de`** | audit §7 closed ledger (disposition per W1–W17) + §8 items 2/3 answered |
| (4) full suite CI-owned | Checkpoint 6 | **`bd30cd7de`** | box annotated CI-owned with the pointer; deliberately NOT ticked (no run here) |
| (7) tick-only granted | BWR1.1 / BWR1.2 / BWR1.6 | **`9fc56c549`** | pointer ticks to `6c8187e20` / `1021589c6` / `ee4d217bc` |
| (7) extended, disclosed | BWR1.4 / BWR1.5 | **`32045b5a1`** | pointer ticks to `aee1ebe8d` / `ce6e602be`+`18139aec6` |
| (8) session record | `-Session bdw-1` | manager **`e5980809c`** | `tasks/sessions/bdw-1.json` present; the session-scoped command resolves and runs |
| — (this segment) | guard-pin re-verify | **`9129f318f`** | current sha256 reading for the manager's re-pin |

Fence-attribution = the work is a call-through the todo itself names, but this lane's allowed paths
forbid the file. Those are manager-rulable by widening the path; the rest are external.

| # | Row | Exact blocker | Class |
|---|---|---|---|
| 1 | T14 bullet 4 — delta report handed to the owner | **CLOSED** — written into the audit §7a under the manager's grant (`ba4a8d0e5`) | done |
| 2 | T15 bullet 3 — status-contest delta report across levels | **CLOSED** — audit §7b, with the printed cross-level reading (`913a6d76e`) | done |
| 3 | Checkpoint 6 — §7 closed ledger + §8 items 2/3 | **CLOSED** — audit §7 now carries a disposition row per W1–W17; §8 items 2/3 each carry an `Answered 2026-09-23` reading (`bd30cd7de`) | done |
| 4 | Checkpoint 6 — full suite (`test-fast.ps1 -AllDefault`) | manager ruling 2026-09-23: **CI-owned**, this lane does NOT run it; the box is annotated and deliberately left unticked | ruled |
| 5 | Checkpoint 6 — live RPG-Server-Debug probe | needs a live slot plus a running server and game, read back through the normal query path | **EXTERNAL** — owner-side |
| 6 | T9 / W8 `Draughts` producer (and BWR1.3) | `tasks/item-todo.md` ~line 6839, the consumable seed→concrete generator; no `ConsumableContainerBuild` in `src/` | **EXTERNAL** — owner `item` program |
| 7 | BWR1.1 / BWR1.2 / BWR1.4 / BWR1.5 / BWR1.6 | **CLOSED** by pointer in the granted file (`9fc56c549` + `32045b5a1`); 1.4/1.5 extended beyond the named three and disclosed | done |
| 8 | `-Session bdw-1` verification | **RESOLVED** — the manager committed `tasks/sessions/bdw-1.json`; the session-scoped command now resolves and runs | done |
| 9 | combat-ai citation drift | **RESOLVED** — 35 tokens re-anchored across 11 docs (`1ae8e8cbe`) | done |
| 10 | `PlantSideStatusGuardTests.BattleEffects` baseline pin | **RESOLVED (manager, `f73ed1d33`)** — re-pinned to `E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8` with the T6 provenance in the comment. **Verified on the merged head:** the pinned test now passes (three-test filter reads Failed 2, Passed 1 — the pass is this one). | done |
| 11 | Two further `FusionRpg.Guard.Tests` failures on the merged head | **`CiPytestWiringTests` root cause read 2026-09-23:** the registry's `tools-audit-tests` project is `runner: pytest, root: ".", tests: "gk-core/tests/tools"`, and `.github/workflows/ci.yml` has no step with `working-directory: .` running `python -m pytest` — so the one file `gk-core/tests/tools/test_audit_program_pipeline.py` runs nowhere in CI. The entry was touched by `7624370dc` (keepverse KS3.1/L4); the honest fix is a CI step at `working-directory: .` (protected) or a corrected registry entry, never a `root` rewrite that would make the guard pass without wiring the tests. `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary` fails on creature-seed T10's new `picks.source-below-rank-floor`. | **EXTERNAL** — keepverse / creature-seed |

Worked under the rulings this segment: the three audit writes (rows 1–3), the BWR pointer ticks (row 7, plus
two same-class rows disclosed), and the combat-ai re-anchor (row 9). Row 10 is blocked by the pipeline guard
and needs a manager re-pin; rows 5/6/11 are external.

## Triage — the `battle-wire-remainder` remainder (a DIFFERENT spec: `combat-math-dedup`)

`battle-derived-wire`'s own todo has **0 open task blocks**, and in the merged BWR file only **BWR1.3**
belongs to this program (W8, external). The other **seven** open rows are `combat-math-dedup`'s (D6–D21),
absorbed into BWR when the two source todos were retired by pointer. They are listed here only so the
manager can rule on them in one place — each needs a path this lane does not own, verified against the
tree, not guessed:

| Row | Spec | In-fence part | Needs a grant for |
|---|---|---|---|
| BWR1.3 (W8 `Draughts`) | battle-derived-wire | — | **EXTERNAL** — the `item` program's consumable seed→concrete generator (`tasks/item-todo.md` ~6839) |
| BWR2.1 (D6 pool regen) | combat-math-dedup | `gk-core/src/FusionRpg.Core/Balance/Analytic/ActionSchedule.cs` | `docs/research/class-system/_baseline-{dominance,goldens,residual}.json` — its own Verify is `regen-class-system-baselines.ps1 --check`, which rewrites those tracked baselines |
| BWR2.2 (D9 `ActionEconomy`) | combat-math-dedup | — | `gk-core/tools/CombatSim/ActionEconomy.cs` |
| BWR2.3 (D7b one `Phi`/`Erf`) | combat-math-dedup | `gk-core/src/FusionRpg.Core/Balance/Analytic/Race.cs` | `gk-core/tools/CombatSim/Analytic.cs` (the copy to delete) |
| BWR2.4 (D8 `StatusModel`) | combat-math-dedup | — | `gk-core/tools/CombatSim/StatusModel.cs` |
| BWR2.5 (D11/D12 display parity) | combat-math-dedup | `gk-core/src/FusionRpg.Core/Items/Display/ItemDisplayRenderer.cs` | `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts` + its vitest |
| BWR3.1 (D13–D19 vocabulary duplicates) | combat-math-dedup | not enumerated per item | likely `gk-fusion/src/FusionRpg.Injector/**`; needs the per-item file list first |
| BWR3.2 (D20/D21 HUD folds) | combat-math-dedup | `gk-core/src/FusionRpg.Core/Hud/ActorHudShieldStacks.cs` | `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudDirector.cs` |

No active session owns `combat-math-dedup` (only the retired `backlog-clean-up-build-20260920` and
`open-items-clear-20260916-8d2e` records mention it), so these rows are unowned rather than contested.
A `gk-core/tools/CombatSim/**` grant would unblock BWR2.2/BWR2.3/BWR2.4 together; `web/**` unblocks BWR2.5;
`gk-fusion/src/FusionRpg.Injector/**` unblocks BWR3.2 (and probably BWR3.1); `docs/research/class-system/**`
unblocks BWR2.1. I have not touched any of them: they are another spec's rows, and the parts that are
in-fence are not the parts that make each row completable.

## Open rows that end this segment blocked (finding for the manager)

| Row | Exact blocker | Evidence |
|---|---|---|
| T9 / W8 `Draughts` producer | The authored draught is a seed (`Family` + `PowerBand`), not a magnitude, and no seed→channel resolver exists — so there is nothing to assign. Named external dependency: `tasks/item-todo.md`'s OPEN row "The seed → concrete generator — the runtime generator's" (~line 6839) — the 60 seeds have no `effect_container`/`effect_container_atom` rows and rolling them is a shared-SDK job. **Re-measured 2026-09-23:** the build-at-use-time pattern already exists three times (`UniqueContainerBuild.From`, `EquipmentContainerBuild.From`, `GemContainerBuild.From`) and has **no consumable sibling**, so the item owner's fix is a fourth builder of an existing shape, not new architecture. | `DraughtProjection.cs:11-21`, `ConsumableCorpus.cs:44-57`, `ConsumableCatalog.cs:96,108`, `tasks/item-todo.md:6839`, `gk-core/src/FusionRpg.Core/Items/**/*ContainerBuild.cs` |

T17 and T18 were reopened and closed in this session (above); T3 and T6 were closed earlier, and T2/W3 in this segment.

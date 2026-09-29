# Battle derived-stat / effect-mechanism wire audit — 2026-09-16

**Status:** research finding, not a spec. Read-only audit of what actually changes a battle outcome.
**Question asked:** *"We have one battle engine for multiple gameplay modes. Which of the RPG's derived
stats and effect mechanisms actually change a battle outcome, and which are inert in `BattleEngine`
while working on the lawn?"*

**Method.** Every claim below was verified against `src/**` at HEAD `466c5040` (2026-09-16). Doc and
comment claims were used only to locate code, never as evidence (DESIGN-GATE §3 rule 2). Population
numbers are **readings taken 2026-09-16**, never constants (DESIGN-GATE §3 rule 7).

**Documents read this session** (DESIGN-GATE §1 rows *Combat damage / HP*, *Stats*, *Battle / turns*,
*Status effects*, *Anything at all*): `docs/DESIGN-GATE.md`; `docs/architecture/combat-damage-ssot.md`
(§4.1–4.3, §5, §6.7a); `docs/architecture/actor-hub-ssot.md` (§1, §2, §7, §8, §8.1–8.3);
`docs/architecture/battle-timeline-map.md` (header + reconciliation + power-ladder position);
`docs/architecture/battle-turn-ideal.md` (§1–§2); `CLAUDE.md`; `AGENTS.md`;
`.claude/skills/planning-and-task-breakdown/SKILL.md`.

---

## 0. The one-paragraph answer

There is genuinely **one resolver** and **one apply pipeline**, and battle does use both — but only on
**one of its two damage paths**. Battle's *basic-attack* path calls `OverlayCombatCalculator.Compute`
and gets the full 20-family combat stack. Battle's *effect/atom* path — every `resource.delta` packet,
every DoT pulse, every on-hit rider — runs through the **same** `CombatDamageDispatcher` but with
`ICombatMath` left null, so it silently falls back to `PassThroughCombatMath`
(`gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs:28`, `gk-core/src/FusionRpg.Core/Combat/ICombatMath.cs:15-16`)
and skips the resolver entirely. Separately, battle's HP apply enters the pipeline **one level below**
the reflect step, so all four `combat.reflect.*` families are unreachable in battle. And on the compose
side, battle registers a **different set of `IActorStatSubsystem`s** from the lawn — no progression, no
status-derived — so two of the largest non-combat families never reach a battle decision at all. None
of this is an architectural wall: every gap below is a null delegate, an unset property, an
unregistered subsystem, or a missing fire site.

---

## 1. Compose paths — which subsystems are registered per mode

This is the highest-value table in the audit. `ActorHub` is the sole composer everywhere
(`actor-hub-ssot.md` §8.3, and verified: `BattleStatComposer` no longer exists in `src/**`), but each
mode **registers a different subsystem set**, and a subsystem registered in one mode and not another
*is* a per-mode stat difference.

Four production compose sites exist:

| Mode | Compose site | Builder |
|---|---|---|
| **Lawn** (injector) | `gk-fusion/src/FusionRpg.Injector/CheatState.cs:49-81` | `ActorHubBootstrap.CreateDefault` |
| **Sheet** (server, cold) | `gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs:70-76` | `ActorHubBootstrap.CreateDefault` |
| **Battle / delve / siege / web-match** | `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:41-64` | hand-built `new ActorHub(...)` |
| **Sim** | `gk-core/src/FusionRpg.Core/SimEngine.cs:43` | `ActorHubBootstrap.CreateDefault(Stats)` — bare |

### 1.1 Subsystem-per-mode matrix

Legend: **Y** = always registered · **opt** = registered only when the caller supplies the delegate/input ·
**—** = never registered in this mode.

| `IActorStatSubsystem` | Lawn | Sheet | Battle | Sim | Registration line (battle / hub) |
|---|---|---|---|---|---|
| `RpgProgressionSubsystem` (`progression.power`, `progression.realm`) | **Y** | **Y** | **—** | **Y** | `ActorHub.cs:156` — battle never calls this builder |
| `ResourceBaselineSubsystem` (`resource.max.*`, `resource.regen.*`) | **Y** (`CheatState.cs:81`) | **Y** (`UniqueActorHubCompose.cs:75`) | **Y** | — | `BattleHubCompose.cs:47` / `ActorHub.cs:154-155` |
| `AptitudeSubsystem` | **Y** (`CheatState.cs:50,55`) | **Y** (`:72-73`) | **opt** | — | `BattleHubCompose.cs:49-56` (only if `HubInputs.Aptitude`) |
| `AtomDerivedSubsystem` (equip + tree `stat.derived`) | **Y** (`CheatState.cs:66-69`) | **Y** (`:74`) | **opt** | — | `BattleHubCompose.cs:57-58` |
| `StatusDerivedSubsystem` (live status → `combat.*`) | **Y** (`CheatState.cs:74`) | **—** | **—** | — | `ActorHub.cs:173-174`; **no battle registration exists** |
| `StarLoyaltySubsystem` | **—** | **Y** (`:76`) | **opt** | — | `BattleHubCompose.cs:59-60` |
| `DraughtSubsystem` | **—** | **—** | **opt** | — | `BattleHubCompose.cs:61-62` |
| `ExpeditionInjurySubsystem` | **—** | **—** | **opt** | — | `BattleHubCompose.cs:63-64` |
| `BattleBaselineSubsystem` (Θ → defense/accuracy/dodge/crit) | — | — | **Y** | — | `BattleHubCompose.cs:42` |
| `BattleAffinitySubsystem` (element `combat.power/defense.{el}`) | — | — | **Y** | — | `BattleHubCompose.cs:43-44` |
| `BattleTraitSubsystem` | — | — | **Y** | — | `BattleHubCompose.cs:45` |
| `BattleTempoSubsystem` (`turn.speed`) | — | — | **Y** | — | `BattleHubCompose.cs:46` |

### 1.2 The `opt` column is the real story — who actually supplies `HubInputs`

`BattleHubCompose` reads `setup.HubInputs` (`BattleHubCompose.cs:38`). Five of its nine subsystems only
register when that record carries the matching field. Every production `BattleActorSetup` construction:

| Producer | `Aptitude` | `BoundAtoms` | `StarLoyalty` | `Draughts` | `Injuries` |
|---|---|---|---|---|---|
| `gk-core/src/FusionRpg.Server/WebMatchService.cs:600-609` (squad) | **Y** (`:602`) | **Y** (`:604`) | **Y** (`:605`) | — | — |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs:503` (zomboss wave) | **Y** | — | — | — | — |
| `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:278` | (preserved) | (preserved) | (preserved) | — | **Y** |
| `gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs:143` (boss only) | **Y** | — | — | — | — |
| `gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs:206-212` (all other delve actors) | — | — | — | — | — |
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:360-385` (siege animate) | — | — | — | — | — |
| `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:307-321` (siege structures) | — | — | — | — | — |
| `gk-core/src/FusionRpg.Core/Battle/WaveCatalog.cs:166-180` (waves) | — | — | — | — | — |
| `gk-core/src/FusionRpg.Server/WebMatchService.cs:662-672` (synthetic) | — | — | — | — | — |

**Consequences, each a separate finding:**

- **`BattleHubInputs.Draughts` has zero production writers.** Declared `BattleHubInputs.cs:27`, read
  `BattleHubCompose.cs:61-62`, set nowhere in `src/**` or `tools/**`. `DraughtSubsystem` therefore never
  registers in any real battle. → **wiring gap**
- **Delve and siege carry no `HubInputs` at all** except the one delve boss. A player specimen that
  fights in the Delve or a district assault composes **without** its aptitude, equipment and
  star/loyalty — the same specimen in a web match composes with all three. `DistrictAssaultResolver.cs:339-345`
  names this itself. → **wiring gap**

### 1.3 Per-mode divergences this matrix produces

| Divergence | Lawn | Battle | Evidence |
|---|---|---|---|
| Live status writing a `combat.*` channel reaches the composed value | yes | **no** | `CheatState.cs:74` vs `BattleHubCompose.cs:41-64` (no `StatusDerivedSubsystem`) |
| `progression.power` / `progression.realm` composed | yes | **no** | `ActorHub.cs:156` unreachable from battle; `BattleHubCompose.cs:15-17` states the intent |
| Status contest reads a real tier-power term | yes | **no** — falls back to `1.0` | `ResistanceEvaluator.cs:278,302` reads `TierPower`; `ActorDerivedSnapshot.cs:44-45` defaults both channels to `1.0`; `StatusPolicy.cs:30` `IncludeTierPowerInDelta = true` |
| Θ reaches combat numbers | via `progression.*` + aptitude | via `BattleBaselineSubsystem` + `BattleRuleset` | `BattleHubCompose.cs:39,42` |
| `progression.bonus.*` → `AppliedCombat` merge | yes (`ActorHub.cs:89-113` → `EntityApply.cs:406-416`) | **n/a** — battle never calls `ActorHub.Resolve`, only `ResolveDerived` | `BattleHubCompose.cs:71` |
| Star / loyalty | **no** | yes, in web match only | `CheatState.cs:49-81` passes no `starLoyalty`; `WebMatchService.cs:605` |

---

## 2. The two damage paths, and why only one of them resolves

### 2.1 Path A — basic attack (built)

`BasicAttack.cs:364` calls `calculator.Compute(new OverlayCombatRequest { ... })` with
`Profile = CombatProfile.BattleSim` at `:379`. The calculator instance is battle's own,
`BattleRunState.cs:279`. The resulting signed delta is applied through `BattleRunState.ApplyHp` →
`DamageApplyPipeline.Apply` (`BattleRunState.cs:863-867`), which passes battle's `ShieldGate`
(`BattleRunState.cs:342`, gate built `:331-332`). **This path is fully built**: 20 combat families
plus 4 shield families reach a real battle decision.

### 2.2 Path B — effect / atom damage (wiring gap)

Battle's `BattleEffectHost` constructs its own `EffectBag` at `BattleEffects.cs:60-63`. It later wires
`Bag.ShieldGate` (`BattleRunState.cs:342`), `Bag.Status` / `Bag.StatusRng` (`:367-368`) and
`Bag.BoardSnapshot` (`:356`, `:1021`).

**It never sets `Bag.CombatMath` and never sets `Bag.ActorResolve`.**

The only production site that sets either is the injector's
`gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:539` (`bag.CombatMath = new ConditionalOverlayCombatMath(overlay)`)
and `:556` (`bag.ActorResolve = InjectorCombatBridge.ResolveActor`). A repo-wide search for
`.CombatMath =` / `.ActorResolve =` returns exactly those two lines plus the test harness
(`gk-core/src/FusionRpg.Core/Effects/FoundationHarness.cs:138,147`).

So every battle-side `DamagePacket` that reaches `CombatDamageDispatcher.DispatchInstant`
(`EffectBag.cs:567`, `EffectBag.cs:637`) hits the **inert line**:

```
gk-core/src/FusionRpg.Core/Combat/CombatDamageDispatcher.cs:28
    math ??= PassThroughCombatMath.Instance;
```

and then

```
gk-core/src/FusionRpg.Core/Combat/ICombatMath.cs:15-16
    public long Finalize(long signedAmount, string ptr, DamagePacket packet, BoardEntitySnap? entity) =>
        signedAmount;
```

**Result:** in battle, an atom-granted damage effect, a DoT pulse and an on-hit rider all apply their
authored amount **verbatim** — no hit roll, no crit, no element matchup, no penetration/absorption, no
amplification/reduction, no parry/block. On the lawn the same packet resolves through
`OverlayCombatMath.Finalize` → `OverlayCombatCalculator.Compute` (`OverlayCombatMath.cs:62`).

The same asymmetry shows in DoT pulses specifically: the lawn builds a `StatusFunnelPulseSink` carrying
`CombatMath` and `ActorResolve` (`EffectBag.cs:829-841`), while battle uses `BattlePulseSink`
(`BattleEngine.cs:132-137`, invoked `BattleEngine.cs:422`) which goes straight to
`DamageApplyPipeline.Apply` (`BattleRunState.cs:863`).

**This is the largest single finding in the audit.** It is a wiring gap — two unset properties on a bag
that already exists — not a missing mechanism.

### 2.3 Reflect is structurally unreachable in battle (wiring gap)

`TryReflect` is `private static` and has exactly one caller: `CombatDamageDispatcher.cs:85`, guarded at
`:84` by `actorResolve != null && rng != null`. So reflect requires (a) entering `DispatchInstant` at
all, and (b) a non-null `actorResolve`.

Every `DispatchInstant` caller in `src/**`:

| Caller | Mode |
|---|---|
| `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:567` | lawn *and* battle — but battle's bag has `ActorResolve == null` (§2.2), so the `:84` guard fails |
| `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:637` | same |
| `gk-core/src/FusionRpg.Core/Status/StatusEffectBridge.cs:98,144` | lawn only (`StatusEffectBridge.cs:96` records that battle uses `BattlePulseSink` instead) |
| `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:1403` | lawn debug |

Battle's own HP apply (`BattleRunState.cs:863`) calls `DamageApplyPipeline.Apply` directly — one level
*below* `DispatchInstant`, so the reflect step at `CombatDamageDispatcher.cs:83-85` is never in the call
stack. Same for `SimEngine.cs:353,390`.

**Finding 3 of the main session is CONFIRMED and strengthened**: reflect is lawn-only, and it is
double-gated (missing caller *and* missing `actorResolve`). The SSOT specifies reflect as part of the
shared damage path (`combat-damage-ssot.md` §6.7a), so this is a divergence from the SSOT, not a design
choice recorded anywhere.

---

## 3. Channel reachability — 28 combat families + the non-combat families

**Reading, 2026-09-16:** `DerivedStatChannels.CombatChannelFamilies` holds **28** combat families
(`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:186-216`), expanded per family to
`omni` + one slot per enabled element (`DerivedStatChannels.cs:417-429`). With today's 6-element roster
that is 28 × 7 = **196 combat channels** — matching the owner's figure. `CombatDerivedReader` exposes
**28** typed reader methods, 1:1 with the families
(`gk-core/src/FusionRpg.Core/Combat/CombatDerivedReader.cs:9-89`). The registry's own census lock is
`DerivedAuditCoverage.RegistryPin = 269` (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedAuditCoverage.cs:39`)
— that one *is* a legitimate pinned literal: the registry is a closed vocabulary a developer edits, not
a content population.

**Finding 5 of the main session is CONFIRMED** (28 readers / 28 families), with one correction to the
consumer split: 20 families reach the calculator, 4 reach `ShieldRuntime`, 4 reach the dispatcher's
reflect path — and the reflect four are **not** battle-reachable (§2.3).

### 3.1 Combat families

| Family (×7 slots) | Reader | Production consumer | Lawn | **Battle** | Bucket (battle) |
|---|---|---|---|---|---|
| `combat.power` | `CombatDerivedReader.cs:9` | `OverlayCombatCalculator.cs:166`, omni fallback `:143-144` | yes | **yes** | built |
| `combat.defense` | `:12` | `OverlayCombatCalculator.cs:174`, `:141` | yes | **yes** | built |
| `combat.accuracy` | `:15` | `OverlayCombatCalculator.cs:193`, `:149` | yes | **yes** | built |
| `combat.dodge` | `:18` | `OverlayCombatCalculator.cs:194`, `:149` | yes | **yes** | built |
| `combat.crit.rate` | `:21` | `OverlayCombatCalculator.cs:197`, `:152` | yes | **yes** | built |
| `combat.crit.resist` | `:24` | `OverlayCombatCalculator.cs:198`, `:152` | yes | **yes** | built |
| `combat.crit.damage` | `:27` | `OverlayCombatCalculator.cs:201`, `:155` | yes | **yes** | built |
| `combat.crit.resist.damage` | `:30` | `OverlayCombatCalculator.cs:202`, `:155` | yes | **yes** | built |
| `combat.penetration` | `:36` | `OverlayCombatCalculator.cs:172`, `:139` | yes | **yes** | built |
| `combat.absorption` | `:39` | `OverlayCombatCalculator.cs:173`, `:140` | yes | **yes** | built |
| `combat.amplification` | `:47` | `OverlayCombatCalculator.cs:190`, `:147` | yes | **yes** | built |
| `combat.reduction` | `:50` | `OverlayCombatCalculator.cs:191`, `:147` | yes | **yes** | built |
| `combat.parry.rate` / `.break` | `:58`, `:59` | `OverlayCombatCalculator.cs:214` | yes | **yes** (omni only) | built · partial |
| `combat.parry.strength` / `.shred` | `:60`, `:61` | `OverlayCombatCalculator.cs:301` | yes | **yes** (omni only) | built · partial |
| `combat.block.rate` / `.break` | `:62`, `:63` | `OverlayCombatCalculator.cs:215` | yes | **yes** (omni only) | built · partial |
| `combat.block.strength` / `.shred` | `:64`, `:65` | `OverlayCombatCalculator.cs:306` | yes | **yes** (omni only) | built · partial |
| `combat.shield.capacity` | `:77` | `ShieldRuntime.cs:122` | yes | **yes** | built |
| `combat.shield.toughness` | `:81` | `ShieldRuntime.cs:311` | yes | **yes** | built |
| `combat.shield.pen` | `:85` | `ShieldRuntime.cs:309` | yes | **yes** | built |
| `combat.shield.regen` | `:89` | `ShieldRuntime.cs:404` | yes | **yes** | built |
| `combat.reflect.rate` | `:69` | `CombatDamageDispatcher.cs:113` | yes | **NO** | **wiring gap** — `CombatDamageDispatcher.cs:84` guard / `BattleRunState.cs:863` bypass |
| `combat.reflect.resist.rate` | `:70` | `CombatDamageDispatcher.cs:113` | yes | **NO** | **wiring gap** |
| `combat.reflect.damage` | `:71` | `CombatDamageDispatcher.cs:117` | yes | **NO** | **wiring gap** |
| `combat.reflect.resist.damage` | `:72` | `CombatDamageDispatcher.cs:117` | yes | **NO** | **wiring gap** |

> **All 24 "built" rows above are built on battle's basic-attack path only.** On battle's effect/atom
> path (§2.2) all 20 calculator families are inert; the 4 shield families still apply, because
> `DamageApplyPipeline.Apply` takes the `ShieldGate` directly (`BattleRunState.cs:866`).

**Per-element partial (wiring gap, both modes):** the 12 parry/block/reflect families each register 7
slots (`DerivedStatChannels.cs:167-182`), but their readers are **omni-only**
(`CombatDerivedReader.cs:58-65`, `:69-72`, self-documented at `:53-57` and `:67-68`). That is
12 × 6 = **72 registered channels with no reader in any mode.**

### 3.2 Non-combat families

| Family | Reader / consumer | Lawn | **Battle** | Bucket (battle) |
|---|---|---|---|---|
| `status.power.*`, `status.resist.*` | `ResistanceEvaluator.cs:279-281`, `:286-303` | yes | **yes** — battle's `StatusRuntime` gets a real derived resolver (`BattleRunState.cs:303-306`) | built |
| `status.immune.*`, `status.immuneReduction.*` | `ResistanceEvaluator.cs:171`, `:200-201` | yes | **yes** | built |
| `status.duration.*`, `status.durationReduction.*` | `ResistanceEvaluator.ComputePotencyDelta` `:320-338`, called `:190` | yes | **yes** | built |
| `status.intensity.*`, `status.intensityReduction.*` | same, called `:192` | yes | **yes** | built |
| `status.expose.*` | **none anywhere** — exempted from the audit at `DerivedAuditCoverage.cs:198,207`; `PredicateNode.cs:5` uses it as the repo's byword for an unread channel | no | no | **real gap** |
| `resource.max.*`, `resource.regen.*` | `ResourceChannelReader.cs:17,42` → `ActorResourcePools.cs:25,54,69,96,120` | yes | **yes** — `BattleRunState.cs:560-561` feeds `ByKey[key].Derived` into the pools | built |
| `resource.restore.hp` | `OverlayCombatMath.cs:81` (heal term) | yes | **NO** — battle never calls `OverlayCombatMath` | **wiring gap** |
| `resource.restore.{stamina,hunger,spirit,qi,poise}` | none — `DerivedStatRegistry.cs:253` says so | no | no | **real gap** (awaits action-cost layer) |
| `resource.efficiency.*` (all six) | none — `DerivedStatRegistry.cs:244`, `DominanceGuard.cs:116` | no | no | **real gap** (awaits action-cost layer) |
| `progression.power`, `progression.realm` | `ActorDerivedSnapshot.TierPower` `:44-45` → `ResistanceEvaluator.cs:278,302`, `CostLedger.cs:153` | yes | **NO** — `RpgProgressionSubsystem` unregistered (§1.1) | **wiring gap** |
| `progression.bonus.{maxHp,atk,defense,arm1,arm2}` | `ActorHub.cs:91-95` → `EntityApply.cs:406-416` | yes | **NO** — battle calls `ResolveDerived`, not `Resolve` (`BattleHubCompose.cs:71`), so no `AppliedCombat` merge | **wiring gap** |
| `progression.xpRate`, `progression.breakthroughSuccess` | **zero consumers anywhere** | no | no | **real gap** |
| `skill.cooldown.attack` | `ActionCategoryChannels.cs:20` → `BasicAttack.cs:44`, read `:438` | n/a | **yes** | built |
| `skill.effectiveness.attack` | `ActionCategoryChannels.cs:30` → `BasicAttack.cs:45`, read `:445`, applied `:378` | n/a | **yes** | built |
| `skill.cooldown/effectiveness.{defense,support,movement,status}` | mechanism exists, no shipped action names them — `DerivedStatRegistry.cs:198,204` | n/a | no | **wiring gap** (content) |
| `move.range` | `BasicAttack.cs:311`, `:349` | n/a | **yes** | built |
| `ai.aggression` | `BattleRunState.cs:847` | n/a | **yes** | built |
| `turn.speed`, `turn.haste` | `BattleTempoSubsystem.cs:38`; registry `DerivedStatRegistry.cs:119,121` | n/a | **yes** | built |
| `turn.moveSpeed` | declared `Battle/Timeline/DerivedTurnChannels.cs:21`, **never registered** (`DerivedStatRegistry.cs:119-125` registers only Speed/Haste) | n/a | no | **wiring gap** |
| `loadout.slots` | reader chain exists (`LoadoutSet.cs:57`, `CapPolicy.cs:44`, `AutoEquip.cs:38`) but **no production site ever supplies the value** — every `src/**` mention is an XML doc reference | no | no | **wiring gap** |
| `combat.heal.power` (retired 2026-09-02) | none, deliberately — `DerivedStatRegistry.cs:221-222` | no | no | n/a — retired |

> **Caveat on `Balance/Analytic/**`.** `StrikeMixture.cs`, `PhaseModel.cs` and `Predictor.cs` sit under
> `src/**` and read many of these channels, but their only callers are `DominanceGuard` /
> `TerminationGuard` / `FrameDominanceGuard`, and **those have no caller in `src/**`** — only under
> `tests/**`. Their reads are offline balance-model only and were **not** counted as lawn or battle
> reachability anywhere above.

---

## 4. Mid-battle recompose — the seam is wired, the producer is missing

**Compose cadence.** `Derived` is composed exactly once per actor, at `ActorState` construction:
`BattleEngine.cs:42` (`Derived = BattleHubCompose.Compose(setup)`), with a frozen copy at `:47`
(`BaseDerived`). Reinforcements get their own one-time compose (`BattleRunState.cs:1100`). Nothing
re-runs `BattleHubCompose` for a live actor.

**The recompose mechanism exists and runs.** `BattleEngine.cs:481` calls
`state.RecomposeDerivedForAllActors()` at the top of every round →
`BattleRunState.cs:212-216` → `BattleDerivedModifierLedger.Recompose` (`BattleDerivedModifierLedger.cs:60-64`),
which rewrites `live = BaseDerived + Σ(active sources)` for every tracked channel. Idempotent, and a
hard no-op on an empty ledger (`:62` iterates only tracked keys).

**But the ledger has one production writer, and it fires only at construction:**

- `BattleRunState.cs:460` — `DerivedLedger.Add(...)` inside `foreach (var aura in setup.ActiveAuras)`
  (`:455-463`).
- `BattleRunState.cs:388` — `Host.AddDerivedContribution = DerivedLedger.Add`, the live seam declared at
  `BattleEffects.cs:150`. **Zero production invokers.** The only callers are
  `gk-core/tests/FusionRpg.Core.Tests/Battle/Adoption/PassiveTreeMechanismRoundRecomposeTests.cs:49,71` and
  `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleHubComposeTests.cs:183`.

And **`BattleActorSetup.ActiveAuras` has zero production writers** — declared `BattleModels.cs:478`,
consumed `BattleRunState.cs:455`, set only in `gk-core/tests/FusionRpg.Core.Tests/Battle/AuraDeliveryTests.cs:42`
and `gk-core/tests/FusionRpg.Core.Tests/Battle/Ai/ZombossAuraTests.cs:81`.

> **So the per-round `Derived` recompose at `BattleEngine.cs:481` is, in every shipped battle, a no-op
> that reproduces the construction-time value.** → **wiring gap** (two null producers, one live seam).

### 4.1 What *is* live mid-battle

| Channel | Live? | Path |
|---|---|---|
| primary `atk` | **yes** | `Status.OnApplied` → `Ledger.Add` (`BattleRunState.cs:310-321`) and `stat.modify` (`BattleEffects.cs:301-310`) → `ActorState.LiveAtk` (`BattleEngine.cs:101`) → `BasicAttack.cs:369` |
| `combat.defense.omni` | **partly** | pushed into `Derived` only from the `stat.modify` executor (`BattleEffects.cs:316-318`) |
| `combat.defense.omni` from a **status**'s `StatMods` | **no** | lands in `Ledger` (`BattleRunState.cs:315`) with no reader — half-wired |
| any other `combat.*` | **no** | needs `DerivedLedger`, which has no live producer (above) |
| shield layers | **yes** | `BattleEngine.cs:682-693` upkeep + `ShieldGate` on every apply |
| statuses themselves | **yes** | own event kind, `BattleEngine.cs:413-428`, `Status.Tick` at `:422` |

> **Latent conflict worth naming:** if an aura ever did target `combat.defense.omni`, the per-round
> `Recompose` (`BattleDerivedModifierLedger.cs:63`) would overwrite the `stat.modify` push at
> `BattleEffects.cs:317-318` from `BaseDerived`. Two ledgers write the same channel through different
> gates. Not reachable today (no aura producer), but it is a SOLID-shaped defect waiting for the first
> producer.

---

## 5. Atom triggers — which of the 13 have a battle fire site

The vocabulary is closed at **13** triggers (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKind.cs:125-143`,
aliased to `FusionRpg.Contracts.EffectTriggers`).

| Trigger | Battle fire site | Lawn fire site | Bucket (battle) |
|---|---|---|---|
| `OnActivate` | `BasicAttack.cs:199` (runner), `:209` (bag); `Battle/Siege/ConstructionActions.cs:274` | `EffectEventAdapterCore.cs:255` | **built** |
| `OnDamageDealt` | `BasicAttack.cs:387` (runner), `:399` (bag) | `EffectEventAdapterCore.cs:173`; `EventDrain.cs:609` | **built** |
| `OnGranted` | via `Host.Bag.Grant` (`BattleRunState.cs:643`, `:675`) → `EffectBag.cs:277-281` | same bag path | **built** |
| `OnRemoved` | via bag withdraw → `EffectBag.cs:300-301` | same | **built** |
| `OnDamageTaken` | **none** | `EffectEventAdapterCore.cs:191`; `EventDrain.cs:640,668` | **wiring gap** |
| `OnDeath` | **none** | `EffectEventAdapterCore.cs:209`; `SimEffectHost.cs:232` | **wiring gap** |
| `OnSpawn` | **none** | `EffectEventAdapterCore.cs:230`; `EventDrain.cs:656` | **wiring gap** |
| `OnTimer` | **none** — battle's status pulse uses `BattlePulseSink` (`BattleEngine.cs:422`), not `EffectBag.TickDots` (`EffectBag.cs:831`) | `EffectBag.cs:831`; `StatusEffectBridge.cs:78,130`; `EffectRuntime.cs:492` | **wiring gap** |
| `OnWave` | **none** | `EffectEventAdapterCore.cs:103` | **wiring gap** |
| `OnMatchStart` | **none** | `EffectEventAdapterCore.cs:118` | **wiring gap** |
| `OnMatchEnd` | **none** | `EffectEventAdapterCore.cs:132` | **wiring gap** |
| `OnSunCollect` | **none** | `EffectEventAdapterCore.cs:143` | **wiring gap** — PvZ-board input by design |
| `OnGridPlace` | **none** | `EffectEventAdapterCore.cs:153` | **wiring gap** — PvZ-board input by design |

**Finding 4 of the main session is CORRECTED: 4 of 13, not 2 of 13.** `OnGranted` and `OnRemoved` do
fire in battle, because battle grants through the same `EffectBag` (`BattleRunState.cs:643,675` →
`EffectBag.cs:273-281`, `:298-301`). The nine listed as gaps are correct. Of those nine, `OnSunCollect`
and `OnGridPlace` are genuinely PvZ-board concepts and arguably should stay lawn-only; the other seven
(`OnDamageTaken`, `OnDeath`, `OnSpawn`, `OnTimer`, `OnWave`, `OnMatchStart`, `OnMatchEnd`) all have an
obvious battle analogue the engine already computes.

`AtomKindRegistry.cs:59-60` names six triggers as the kind-bearing set
(`OnSpawn`, `OnDamageDealt`, `OnDamageTaken`, `OnDeath`, `OnTimer`, `OnActivate`) — **battle fires two
of those six.**

### 5.1 The battle plan-item allowlist (built, and correctly narrow)

`BattleEffectSink.Execute` (`BattleEffects.cs:204`) consumes four actions:
`ApplyStatus` (`:209-210`), `ModifyStat` (`:213-214`), `PlaceStructure` (`:221-222`),
`ApplyResourceDelta` (`:224`, body `:227-241`). The inert line is exactly:

```
gk-core/src/FusionRpg.Core/Battle/BattleEffects.cs:225
    return true; // battle mode consumes ApplyResourceDelta (FA10) / ApplyStatus (FA2) / ModifyStat (FA1) / PlaceStructure (Siege) only; every other action is inert here
```

Quiet-refusal paths inside the four consumed branches: `:246` (status unwired), `:249`, `:254`, `:278`
(ledger/target unwired), `:281`, `:294`, `:311`, `:342` (`ConstructionBoard` null — every non-siege
battle), `:229`, `:232`.

---

## 6. Verdict on the six findings brought into this audit

| # | Main-session finding | Verdict | Correction / citation |
|---|---|---|---|
| 1 | `OverlayCombatCalculator` is the only resolver; battle calls it from `BasicAttack.cs:365` with `Profile = CombatProfile.BattleSim`; lawn reaches it via `OverlayCombatMath` | **CONFIRMED**, line nudged | the call is `BasicAttack.cs:364`; `Profile` is at `:379`. Only two `Compute` call sites exist repo-wide: `BasicAttack.cs:364` and `OverlayCombatMath.cs:62` |
| 2 | Battle applies via `DamageApplyPipeline.Apply` (`BattleRunState.cs:863`), lawn via `CombatDamageDispatcher.DispatchInstant`; both land on the same pipeline + `ShieldGate` | **CONFIRMED** | `BattleRunState.cs:863-867`; `CombatDamageDispatcher.cs:47`. Also `SimEngine.cs:353,390` uses the battle shape |
| 3 | Reflect is lawn-only; the four `combat.reflect.*` families are inert in battle/delve/siege/web-match | **CONFIRMED and strengthened** | `TryReflect` has one caller, `CombatDamageDispatcher.cs:85`, guarded at `:84` on `actorResolve != null`. Battle enters below it (`BattleRunState.cs:863`) **and** battle's bag never sets `ActorResolve` (§2.2) — two independent blocks |
| 4 | Only 2 of 13 atom triggers have a battle-reachable fire site | **CORRECTED → 4 of 13** | `OnGranted`/`OnRemoved` fire via `EffectBag.cs:277-281`/`:300-301`, reached from `BattleRunState.cs:643,675`. The nine named gaps are right |
| 5 | 28 reader methods / 28 families / 196 channels; 20 in the calculator, 4 in `ShieldRuntime`, 4 in the reflect path | **CONFIRMED** | `CombatDerivedReader.cs:9-89`; `DerivedStatChannels.cs:186-216`; 28 × (omni + 6 elements) = 196, measured 2026-09-16. Add: the reflect four are lawn-only, and 72 per-element parry/block/reflect channels have no reader in any mode (`CombatDerivedReader.cs:53-57,67-68`) |
| 6 | `OverlayCombatMath.Finalize` returns the amount unchanged when `ElementPayload` is null/empty; confirm whether production ever dispatches payload-less damage | **CONFIRMED — and yes, constantly** | `OverlayCombatMath.cs:42-43` and `:46-47`. The deliberate case is the reflect bounce (`CombatDamageDispatcher.cs:122-135`, no payload — correct per `combat-damage-ssot.md` §6.7a). The **undeliberate** case is far larger: battle never installs `OverlayCombatMath` at all (§2.2), so the question "does a payload-less packet skip the resolver" is dominated by "battle skips the resolver whatever the payload is" |

---

## 7. Findings sorted into the three buckets

### built

1. Battle's basic-attack damage resolves through the SSOT calculator — 20 combat families reach a real decision. `BasicAttack.cs:364`; `BattleRunState.cs:279`.
2. Shield absorb / pen / toughness / regen apply on every battle HP delta, including DoT pulses. `BattleRunState.cs:342,331-332,863-867`; `ShieldRuntime.cs:122,309,311,404`.
3. Status apply contests (`status.power/resist/immune/immuneReduction/duration/intensity`) run in battle with a real derived resolver. `BattleRunState.cs:303-306`; `ResistanceEvaluator.cs:171,200,279-303,320-338`.
4. Resource pools (`resource.max.*`, `resource.regen.*`) are Hub-sourced in battle. `BattleHubCompose.cs:47`; `BattleRunState.cs:560-561`.
5. Live `atk` modification (status `StatMods` and `stat.modify`) reaches damage on every swing. `BattleRunState.cs:310-321`; `BattleEffects.cs:301-310`; `BattleEngine.cs:101`; `BasicAttack.cs:369`.
6. The per-round `Derived` recompose seam runs unconditionally and is idempotent. `BattleEngine.cs:481`; `BattleDerivedModifierLedger.cs:60-64`.
7. `ai.aggression`, `move.range`, `turn.speed`, `turn.haste`, `skill.cooldown.attack`, `skill.effectiveness.attack` all read in battle. `BattleRunState.cs:847`; `BasicAttack.cs:311,349,438,445`; `BattleTempoSubsystem.cs:38`.
8. Four atom triggers fire in battle: `OnActivate`, `OnDamageDealt`, `OnGranted`, `OnRemoved`.
9. Aptitude / bound atoms / star-loyalty reach battle **in web match**. `WebMatchService.cs:600-609`.
10. One composer, one read: no `BattleStatComposer` remains; `gk-core/scripts/guard-actor-hub.py` holds it. `BattleHubCompose.cs:41`.

### wiring gap — CLOSED LEDGER (2026-09-23, `bdw-1`)

**Every gap below now has a disposition and a landing pointer**, which is what Checkpoint 6's
"§7's wiring-gap table becomes a closed ledger" asked for. Closed inside `solid-remediation`
(2026-09-17) but unpointed until `paperwork-reconcile` P5 (2026-09-20): W1, W2, W5, W9 (siege half),
W10 (7 of 9), W12. Closed by `battle-derived-wire` itself: W3, W4, W6, W7, W11, W13, W14, W15, W17. Not
closed: W8 (blocked on the `item` program), W9's delve half (superseded/moot), W16 (another program's
finding). The detailed per-gap table below is kept as the historical evidence of each gap's inert line.

| W | Disposition | Landing |
|---|---|---|
| W1 `CombatMath` on battle's bag | CLOSED | `solid-remediation` T2.5 |
| W2 `ActorResolve` on battle's bag | CLOSED | `solid-remediation` T2.5/T2.6 |
| W3 reflect step unreachable from battle HP apply | CLOSED | `6c8187e20` (T2/W3) |
| W4 status→`combat.*` owner | CLOSED BY DECISION | `1021589c6` (T5) — battle's derived ledger owns it; `StatusDerivedSubsystem` must NOT be registered |
| W5 `RpgProgressionSubsystem` unregistered | CLOSED | `solid-remediation` T3.1/T3.2 |
| W6 `Host.AddDerivedContribution` zero invokers | CLOSED | `1021589c6` (T5) |
| W7 `ActiveAuras` zero production writers | CLOSED | `474c92d74` (T4) |
| W8 `Draughts` zero production writers | BLOCKED (external) | `tasks/item-todo.md` ~6839, the consumable seed→concrete generator |
| W9 delve/siege `HubInputs` | siege CLOSED / delve SUPERSEDED (moot) | `solid-remediation` T3.3; delve has no production entry |
| W10 atom triggers in battle | CLOSED | `solid-remediation` T3.4 + `474c92d74` + `1021589c6`; 2 correctly excepted |
| W11 status-sourced `defense` unread | CLOSED | `5e33ad647` (T6) |
| W12 72 per-element avoidance channels unread | CLOSED | `solid-remediation` T2.3 |
| W13 `resource.restore.hp` unreachable | CLOSED | `aee1ebe8d` (T3) |
| W14 `loadout.slots` never fed | CLOSED (option b) | `ce6e602be` (T18) |
| W15 `turn.moveSpeed` declared-unregistered | CLOSED | `18139aec6` (T17) |
| W16 `skill.cooldown/effectiveness` content absent | NOT THIS PROGRAM'S | cross-linked to `class-system` P9.0 |
| W17 `progression.bonus.*` unreachable | CLOSED | `ee4d217bc` (T15/W17) |

**Original note, kept for the record:**

**Corrected 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P5, per this plan's own Checkpoint 6
instruction): W1, W2, W5, W9 (siege half), W10 (7 of 9) and W12 closed inside `solid-remediation`
(2026-09-17), absorbed without a pointer until now. See `tasks/battle-derived-wire-todo.md`'s per-task
pointers for landing commits. Genuinely still open at that date: W3, W4, W6, W7, W8, W9 (delve half),
W10 (2 of 9, SR-14), W11, W13 (partial), W14, W15, W16, W17.

| # | Gap | The inert line |
|---|---|---|
| **W1** | ~~**Battle's `EffectBag` never gets `CombatMath`**~~ — **CLOSED, `solid-remediation` T2.5** (2026-09-20, `backlog-clean-up` `paperwork-reconcile` P5) | `CombatDamageDispatcher.cs:28` (`math ??= PassThroughCombatMath.Instance`) + `ICombatMath.cs:15-16`; unset at `BattleEffects.cs:60-63`; only production setter `EffectRuntime.cs:539` |
| **W2** | ~~**Battle's `EffectBag` never gets `ActorResolve`**~~ — **CLOSED, `solid-remediation` T2.5/T2.6** (2026-09-20) | `CombatDamageDispatcher.cs:84` (`if (actorResolve != null && rng != null …)`); only production setter `EffectRuntime.cs:550` |
| **W3** | **Battle's HP apply enters below the reflect step** — all 4 `combat.reflect.*` families inert | `BattleRunState.cs:863` calls `DamageApplyPipeline.Apply`, skipping `CombatDamageDispatcher.cs:83-85` |
| **W4** | **`StatusDerivedSubsystem` is never registered in battle** — a status writing `combat.*` never reaches the composed value | `BattleHubCompose.cs:41-64` (no registration); lawn's is `CheatState.cs:74` |
| **W5** | ~~**`RpgProgressionSubsystem` is never registered in battle**~~ — **CLOSED, `solid-remediation` T3.1/T3.2** (2026-09-20); landed always-on, not default-off as originally specced (owner-adjacent ruling in T3.1). `progression.bonus.*` reach (W17 below) remains separately open | `ActorHub.cs:156` unreachable from `BattleHubCompose.cs:41`; fallback `ActorDerivedSnapshot.cs:44-45`; consumer `ResistanceEvaluator.cs:278,302` |
| **W6** | **`Host.AddDerivedContribution` has zero production invokers** — the live mid-battle derived write is dead | seam declared `BattleEffects.cs:150`, wired `BattleRunState.cs:388`, invoked only in `tests/**` |
| **W7** | **`BattleActorSetup.ActiveAuras` has zero production writers** — the only `DerivedLedger` producer never receives input | consumer `BattleRunState.cs:455-463`; field `BattleModels.cs:478` |
| **W8** | **`BattleHubInputs.Draughts` has zero production writers** — `DraughtSubsystem` never registers in a real battle | read `BattleHubCompose.cs:61-62`; declared `BattleHubInputs.cs:27` |
| **W9** | **Delve and siege setups carry no `HubInputs`** — a player specimen fights without its aptitude, equipment and star/loyalty. **Siege half CLOSED, `solid-remediation` T3.3** (2026-09-20); **delve half SUPERSEDED (moot)** — no production entry exists yet (`DelveBattle.Run` has zero callers), re-open when one ships | `Encounter.cs:206-212`; `DistrictAssaultResolver.cs:360-385` (self-named at `:339-345`) |
| **W10** | ~~**Nine of thirteen atom triggers have no battle fire site**~~ — **7 CLOSED, `solid-remediation` T3.4** (2026-09-20): `OnDamageTaken`, `OnSpawn`, `OnDeath`, `OnTimer`, `OnMatchStart`, `OnMatchEnd`, `OnWave`. 2 correctly excepted (`OnSunCollect`, `OnGridPlace`, no battle analogue). 2 remain open — the aura triggers `W6`/`W7` below (SR-14) | see §5 table |
| **W11** | **Status-sourced `defense` `StatMods` are stored and never read** — only the `stat.modify` executor pushes into `Derived` | stored `BattleRunState.cs:315`; the only push `BattleEffects.cs:316-318` |
| **W12** | ~~**72 per-element parry/block/reflect channels have no reader in any mode**~~ — **CLOSED,
`solid-remediation` T2.3** (2026-09-20); 0 goldens moved (no content authors these yet, as expected) | `CombatDerivedReader.cs:58-65,69-72`, self-documented `:53-57,67-68`; generated `DerivedStatChannels.cs:167-182` |
| **W13** | **`resource.restore.hp` (the heal term) is battle-unreachable** — only `OverlayCombatMath.FinalizeHeal` reads it | `OverlayCombatMath.cs:81`; battle never installs `OverlayCombatMath` (W1) |
| **W14** | **`loadout.slots` reader chain is never fed** — every consumer takes it as a defaulted parameter, no site supplies it | `LoadoutSet.cs:57`, `CapPolicy.cs:44`, `AutoEquip.cs:38` |
| **W15** | **`turn.moveSpeed` declared but never registered** | `Battle/Timeline/DerivedTurnChannels.cs:21`; `DerivedStatRegistry.cs:119-125` registers only Speed/Haste |
| **W16** | **`skill.cooldown/effectiveness` for 4 of 5 categories have no shipped action naming them** — mechanism generic, content absent. **Cross-linked 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P8): the identical missing-reader family set (minus `resource.efficiency`) is `class-system`'s own P9.0 readiness-gate finding — one finding, tracked in both documents; merged write-up at `infra-remainders` BCU8.9 | `DerivedStatRegistry.cs:198,204` state this in-line |
| **W17** | **`progression.bonus.*` never reaches battle** — battle calls `ResolveDerived`, never `Resolve`, so the `AppliedCombat` merge never runs | `BattleHubCompose.cs:71`; merge `ActorHub.cs:89-113` |

### real gap

| # | Gap | Evidence |
|---|---|---|
| **R1** | `status.expose.*` has no consumer anywhere | `DerivedAuditCoverage.cs:198,207` exempts it; `PredicateNode.cs:5` names it the repo's canonical unread channel |
| **R2** | `resource.efficiency.*` (all six resources) has no reader anywhere — the action-cost layer that would read it is unbuilt | `DerivedStatRegistry.cs:244`; `DominanceGuard.cs:116` |
| **R3** | `resource.restore.{stamina,hunger,spirit,qi,poise}` has no reader anywhere | `DerivedStatRegistry.cs:253` |
| **R4** | `progression.xpRate` and `progression.breakthroughSuccess` have no reader anywhere | `DerivedStatChannels.cs:531-532`; registered `DerivedStatRegistry.cs:272,274`; zero `src/**` reads |

> R2–R4 are genuinely "no mechanism": the consumer subsystem does not exist yet. They are **not** in
> scope for a battle-wire program and are listed only so they are not re-discovered as wiring gaps.

### 7a. Delta report — W4: status → `combat.*` (T14 bullet 4; manager-granted write 2026-09-23)

**Before:** a status whose `StatMod` named a `combat.*` channel landed in `BattleStatModifierLedger`
and was read by NOTHING for that channel, so the composed value was exactly the base and the status's
whole contribution was **0**.

**After** (T5/W6, `1021589c6`): `Status.OnApplied` routes a `combat.*` mod into
`BattleDerivedModifierLedger` through `Host.AddDerivedContribution`, `Status.OnEnded` withdraws it, and
the per-round `Recompose` writes `BaseDerived + Σ`. Reading (`BattleStatusDerivedContributionTests`,
`combat.defense.omni`, level 5): base **7** → a flat **+200** status gives **207**; withdrawal returns
**7**. A primary-channel mod (`atk`) still does not reach the derived ledger (7 → 7), and an `increased`
op on a FlatSum `combat.*` channel contributes **0**, matching `DerivedComposer`'s own FlatSum rule.

**Over the existing battle fixtures the delta is 0**, because no shipped status authors a `stat` block
at all — `BattleGoldenTests` 5/5 unmoved. The mechanism delta above is therefore the whole of it today;
the fixture delta becomes non-zero the moment content authors one.

**The W4 decision this settles:** battle's OWN derived ledger owns status→`combat.*`;
`StatusDerivedSubsystem` is NOT registered (`BattleHubCompose` passes `statusDerivedMods: null`), pinned
by `BattleStatusDerivedContributionTests.Battle_registers_progression_but_not_the_status_derived_subsystem`.

### 7b. Delta report — W5/W17: the status-contest level term and `progression.bonus.*` (T15 bullet 3; manager-granted write 2026-09-23)

**The contest term.** `ResistanceEvaluator` reads `ActorDerivedSnapshot.TierPower`, which falls back to
`1.0` when `progression.power` is absent — §8 item 3 below. W5 registered `RpgProgressionSubsystem` on
`BattleHubCompose` with `FixedPowerIndexProvider(theta)`, so battle composes `progression.power` from its
OWN Θ through the one ladder. Reading (`BattleProgressionSubsystemTests`,
`BattleHubCompose.Compose(actor).Get(progression.power)`): **L1=1, L5=5, L10=10, L20=20** — linear in Θ,
never a second curve.

**The bonus term** (W17, `ee4d217bc`). `BattleHubCompose` now exposes `Resolve(setup)` calling
`hub.Resolve(ctx)` — the `AppliedCombat` merge itself — and `ActorState` consumes it by the delta
`AppliedCombat − RuntimePrimary`. Reading (`Fortitude(7)`, shipped `aptitudes.v10.json`, whose maxHp edge
is k=8000 and defense edge k=10000): **maxHp 215 → 1935 (Δ1720)**, **defense 7 → 2351 (Δ2344)**; with no
allocation both stay at the setup bases (215 / 7). `arm1`/`arm2` have no battle analogue and are ignored,
as before.

**Fixture delta: 0.** Every battle golden fixture is bare (no `HubInputs.Aptitude`), so the bonus is 0
there and `BattleGoldenTests` reads 5/5 unmoved — this is a mechanism measurement, not a golden
re-baseline.

---

## 8. What I could not determine, and why

1. **Whether W4/W5 are deliberate.** `BattleHubCompose.cs:15-17` states the omission as intentional
   ("battle composes no progression or status channels … parity with the old composer is
   channel-exact"). That was a **fusion-parity** argument at `battle-hub-fuse` T5 — preserving the
   deleted composer's behaviour byte-for-byte — not a statement that battle should never have status or
   progression channels. I could not find a decision row that ratifies the omission as an end state.
   `docs/architecture/decisions.md` was **not** opened this session. **Owner reading needed** before
   W4/W5 are closed.
2. **Whether battle's effect path ever actually carries an `ElementPayload` today.** I proved the
   resolver is skipped (W1) but did not enumerate shipped atom content to show how many battle-reachable
   grants would produce a typed payload. The size of W1's live impact is therefore unquantified — the
   *defect* is certain, the *blast radius* is not. Task B1 in the plan measures it first.
   **Answered 2026-09-23** (`bdw-1`, manager-granted write): measured by that spike —
   `docs/research/battle-effect-payload-spike-2026-09-17.md` (the plan's Task 0, landed by
   `solid-remediation` T2.1). The reading lives there; this note records that it was produced.
3. **Whether `TierPower = 1.0` in battle is neutral or a real balance shift.** `ActorDerivedSnapshot.cs:44-45`
   defaults both factors to `1.0`, so `totalPower`/`totalResist` at `ResistanceEvaluator.cs:278,302` lose
   a level term symmetrically. Symmetric loss is not necessarily neutral once one side is a wave actor
   with no Θ, but I did not run the evaluator across levels to measure it.
   **Answered 2026-09-23** (`bdw-1`, manager-granted write): the fallback no longer applies in battle —
   W5 registered `RpgProgressionSubsystem` with `FixedPowerIndexProvider(theta)`, so `progression.power`
   composes from battle's own Θ: **L1=1, L5=5, L10=10, L20=20** (§7b). It is linear in Θ, one ladder,
   never a second curve.
4. **Runtime channel census.** All counts above are read from source declarations. The registry's own
   runtime count depends on the injected element roster (`DerivedStatChannels.cs:403`), so the 196 figure
   is "28 families × today's 7 slots", not a value I observed the registry emit.
5. **No test suite was run.** This audit made no source edits and ran no verification command; the plan
   in `tasks/battle-derived-wire-plan.md` names the `verify-change.ps1` invocation for each task.
6. **`tools/**` was excluded** from the "production" reachability judgement except where explicitly
   noted. `SquadHarness`, `ProveAptitude`, `ProveHubCombat` do build `HubInputs`, but they are probes,
   not gameplay.

## 9. DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches: battle engine, ActorHub compose, combat damage SSOT,
    effect/atom layer, status.
[ ] Session boundary recorded. NOT DONE — this session writes documents only and owns no source paths;
    another session owns the source tree. tasks/sessions/ was read, not written. Declared as a gap.
[x] I read every doc in the §1 row(s) for those subsystems, this session (listed in the header).
[ ] decisions.md checked for a lock covering this. NOT DONE — see §8 item 1.
[x] Every factual claim cites file:line.
[x] Verified against CODE, not comments — every doc/comment claim was re-opened in source.
[x] Read the surrounding section of every rule quoted (combat-damage-ssot §4.3 read with §4.1/§4.2
    and §6.7a; actor-hub-ssot §8.3 read with §7/§8).
[x] Constraints tested, not assumed: "reflect is battle-unreachable" was proven by enumerating every
    DispatchInstant caller and reading the :84 guard, not inferred.
[x] Nothing contradicts a §2 invariant. §2.4 (single writer) and §2.5 (Funnel is the only Secondary ->
    Bag path) both hold in battle.
[x] No assertion pins a derived population. The 28/196/269 figures are stated as readings dated
    2026-09-16, and RegistryPin = 269 is named as a legitimate closed-vocabulary pin.
[x] No event-refreshed cache introduced.
[x] No acceptance criterion fixes an ordering that can vary in real play.
[x] Nothing here invents a second composer or a private fold; every remedy proposed in the plan
    contributes to ActorHub or installs an already-shipped component.
[x] Does not extend a SOLID-violating seam. §4.1's latent two-ledger conflict is named, not extended.
```

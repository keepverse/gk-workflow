# Combat AI — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current.** It says *"idea phase ... Not a spec"*. Measured
> today: [combat-ai-map.md](combat-ai-map.md) reads **"APPROVED 2026-09-20 by independent agent
> review"**, with **20** module specs written at `docs/architecture/combat-ai/spec-<module-id>.md`.
> `tasks/combat-ai-todo.md` exists with **0 done / 55 open** — planned but not yet executed.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the capability map, the module specs, the task list, and the code.

**Status:** idea phase, 2026-09-20, **revision 3**. Owner rulings D1–D6 were answered the same day
(§10) and folded into the shape. Revision 2 applied an independent adversarial audit (verdict
PASS-WITH-FIXES, [../research/combat-ai/AUDIT.md](../research/combat-ai/AUDIT.md)). Not a spec; the
build authority is [combat-ai-map.md](combat-ai-map.md) and its module specs.

**Origin.** Owner ruling D2 (`docs/architecture/backlog-clean-up/rulings-2026-09-20.md`) proposed a lawn
caster. The owner's `/idea` the same day widened it:

> enrich lawn combat ai with other combat ai — each combat ai has its own profile but should share the
> same core for reuse — we have delve and siege too

**Folds in:** [lawn-combat-ai-ideal.md](lawn-combat-ai-ideal.md), now the lawn profile of this program.

**Evidence:** [../research/combat-ai/](../research/combat-ai/). Five survey lanes (S1 battle core,
S2 delve, S3 siege, S4 lawn, S5 prior art) and the audit. Revision 2 re-checked the audit's
highest-impact claims in code:
- `CostLedger.RowsFor` allocates per call (`Actions/Cost/CostLedger.cs:67-77`).
- `DecisionTrace` records only `Player`/`Timeout` decisions (`Battle/Timeline/DecisionTrace.cs:5-20`).
- `TimelineDispatch` reselect omits `DefaultAiIntentSource` (`Battle/TimelineDispatch.cs:79-80`).

**Status 2026-09-21 (lane `combat-ai-3`, checked against code).** Two of those three are now closed, so a
reader of this page does not have to reach §4 to learn it: `CostLedger.RowsFor` no longer allocates per call
(**CAI1.14**, whose own test now *measures* zero bytes on that path), and `TimelineDispatch`'s reselect
resolves through the same `IntentRouter` construction as `DeclareBasicAttack` — the omitted term is gone
(**CAI1.10**, M5, and the site's own comment records it). The third bullet was a **scoping** claim rather than
a defect, and it still holds (`DecisionSource` is exactly `Player`/`Timeout`); the conclusion it fed — that a
scored candidate list belongs on `BattleTrace.AiDecision` (`BattleTrace.cs:125`) rather than on
`DecisionTrace` — is what shipped, and §4.1 records why.

---

## 1. Which loop this extends

**Combat depth**, which *"hangs on places, not an eleventh loop"*. This feature decides **what an actor
tries to do** in four places:

| Place (the-loops.md) | Combat surface | Who decides today |
|---|---|---|
| **1. Lawn: first core** | Live PvZ match through the injector | Nobody. Only the basic-attack rider spends a resource. |
| **2. Idle expeditions** (+ interactive battles) | Web/expedition battle; expeditions **auto-resolve at collect** through `WebMatchService` with no `intentSource` | `StubIntentSource` (auto), `InteractiveIntentSource` (player) |
| **3. Farm / hunt / defend** (sieges) | District assault | `SiegeAiIntentSource` |
| **6. The Delve** | Party battles | The steered party is the player. Un-steered parties and wave enemies have **no production policy**. |

It serves three Vision holes: **party formations / combo skills**, **enemy counter-development**, and
**named combat reactions / combo recipes**. The last fits because a "set up wet, then lightning" choice
is a consideration. It adds no loop, currency or clock.

⚠️ **The auto policy is an economy lever.** `battle/auto` is the policy of the **idle economy**:
expeditions stay auto-resolve (`the-loops.md` §2, §6). A smarter default moves expedition reward rates.
Decision **D1** covers this.

## 2. What this is (the player's view)

Every creature fighting for you or against you **uses its kit**, instead of only auto-attacking.
- **On the lawn**, a creature casts between basic attacks, spends its stamina, and can run dry.
- **In a delve or siege**, the side you are not steering fights with intent. It picks targets, uses
  skills, holds or advances, and saves a finisher.

How much of this the player sees or shapes is decision **D4**. Whether a creature fights the same way in
every place is decision **D5**.

## 3. Principles that constrain the shape (restated, not linked)

1. **The RPG layer only.** The AI decides what an RPG actor casts. The cast resolves through the RPG
   stack: intent → action → cost ledger → effects → Funnel → FA10. Nothing changes what PvZ is.
2. **The engine resolves; the AI decides** (`battle-engine-ssot.md` §3c, owner correction 2026-09-16).
   Deciding enters the engine only through `IIntentSource.TryDeclare(actorKey, nowTick)`.
   - The same page retracts D13: **several policies on one seam is correct**.
   - It does **not** protect **two scoring mechanisms**. Two scorers with the same additive semantics are
     a mechanism fork (SOLID S; `battle-engine-ssot.md` §2, §5 Q3/Q4).
   - So this program keeps several *policies* and exactly one *scorer* (§6.1).
3. **A mode owns its loop, never a mechanism.** When a mode asks for a decision (its trigger and
   cadence) is the mode's loop. How a decision is gated, scored and selected is one mechanism.
4. **Determinism, stated precisely.** A battle's automated decisions are a deterministic function of
   `(setup, seed, human trace, profile version, BattleEnvironment.Stamp)`.
   - **Automated decisions are not recorded; they are re-derived on replay.** `DecisionTrace` holds only
     human decisions (`DecisionSource.Player`/`Timeout`), and siege replays from `(setup, seed)`.
   - So the profile version is part of replay identity (§7).
   - Policy memory (the retarget ledger, commitment, repeat-decay) is rebuilt by replay from tick 0.
   - Inputs are doubles (`Derived.Get`, `CombatProbability.Sigmoid` → `Math.Exp`). Cross-platform
     identity therefore rests on the existing `BattleEnvironment.Stamp` (`BattleModels.cs:662-684`,
     arch/OS/runtime), not on "integer purity".
   - Selection itself (argmax with an ordinal tie-break) reads no RNG. A seeded weighted pick is opt-in
     per profile and draws from a battle-owned stream.
5. **Hot loop on the lawn** (`overlay-control-loops.md` §3, §6).
   - Lawn decisions run in the injector, in process, and never await the server, SignalR or SQLite.
   - A dead `ptr` means skip; it never throws.
   - Grants are withdrawn before a `ptr` is reused (§6 rule 4). This covers any per-actor AI state.
   - Re-entry depth is 0 (§6 rule 7).
   - Logic lives in **Core**, because CI never builds the injector.
6. **One ActorHub compose, one cost authority, one estimator.**
   - The AI reads Hub-composed numbers and charges through `CostLedger`.
   - Kill and value considerations read the action's base damage through
     `ActionBaseDerivation.BasePowerMilli` at `EffectiveRungOf` (action-enrich `action-base`, built), and
     the single resolver estimator.
   - No private value math. `SiegeExpectedDamage` was the named anti-example.
7. **One power ladder.** Contests read Θ; magnitudes read P(Θ). No new `f(level)`.
8. **The balance surface is data** (`gk-core/data/tuning/`, published `v{n+1}`).
9. **No hard progression ceilings.** Candidate caps and per-frame budgets are **structural** and say so in
   a comment.
10. **Gameless-first.** Battle, delve and siege AI run with Fusion closed. The lawn profile only enriches.

## 4. What already exists: built, wiring gap, real gap

### 4.1 Built

| Piece | Evidence | Role in the core |
|---|---|---|
| Seam `IIntentSource` / `ActionIntent` (struct; `None` in the value) | `Battle/Timeline/IntentSource.cs:29-37` | The one entry point |
| Selection chain | `Battle/BasicAttack.cs:175-177` — `IntentRouter.Compose(policy: intentSource ?? state.DefaultAiIntentSource ?? NoneIntentSource.Instance, fallback: new StubIntentSource(...))` (CAI1.10 moved the three-term chain into the one router; before it, an inline `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)` sat at `:163-165`) | A mode injects the policy; the reselect site resolves through the same router, so the two can no longer disagree (**closed** by CAI1.10, M5) |
| Legality gates | `Actions/UsabilityEvaluator.cs:15-84` (stance → bound → cooldown → afford → range → condition, short-circuit). Shared verbatim by the stub and siege. | The shared gate. **Its own body** does not allocate, but gate 3 calls `CostLedger.Check`, which does (§4.2). |
| Static preference order | `Actions/ActionTagPreference.cs:16-60` | Deterministic ordering and tie-break |
| Frozen held actions | `Actions/Grants/FrozenActionSet.cs:18-46` | What an actor can choose from |
| Cooldowns | `Battle/Timeline/CooldownLedger.cs:29-106` | Mode-agnostic ledger |
| Default simple policy | `Actions/StubIntentSource.cs:27-97` (nearest enemy, first usable) | The gambit shape at reserve 0 |
| **The one scorer that exists**: `CandidateScorer` (was `AiScoring`) | `Actions/Ai/CandidateScorer.cs` (`Score`, `EffectiveTier`, `ChooseTarget` capped by `maxCandidatesScored`) — moved out of `Battle/Siege/SiegeAi.cs` by **CAI1.1**, which is now 75 lines and no longer holds the class. Additive weights at `gk-core/data/tuning/combat-ai.v1.json` `profiles["siege/default"].scoring` (`weightHitChance 70, weightObjective 50, weightKill 15, weightLowHp 10, weightCannotCounter 10, weightRound 1, weightRisk 120` — the same ten values, moved by **CAI1.8** under H7; `siege.v1.json`'s `ai` block is history). `SiegeAiLiveWiringTests`. | **Is the core scorer** (§6.1). It scores **targets** and then takes the first usable action (`SiegeAiIntentSource.cs`). Core can never add a second rank walk — `CandidateScorer` is the only additive score, pinned by `guard-battle-responsibility` and `CAI1.15`'s DESIGN-GATE row |
| Retarget memory | `Actions/Ai/RetargetLedger.cs` `RetargetLedger` + `retargetLatencyTicks` — moved out of `Battle/Siege/SiegeAiIntentSource.cs` by **CAI1.4** (the row here cited `:316-351`, now a decision-record comment) | The existing anti-oscillation mechanism. The core's commitment bonus **merges into it**, never beside it |
| Decision explanation | `SiegeAi.cs:25-30` `BattleTrace.AiDecision` (top-3, kept out of `Digest`, so it is golden-neutral) | A cheap read-only "why did it do that" (D4) |
| Player input + human trace | `Battle/Timeline/InteractiveIntentSource.cs:30-154`, `DecisionTrace.cs` | Replays human choices; automated ones re-derive |
| Link-strikes (multi-actor coordinated action) | `Battle/Timeline/RendezvousLane.cs:1-44` (atomic multi-slot acquire, shared `LinkedResolve`, rollback) | The combo-skill mechanism (§4.2) |
| Fog | `Actions/FoggedBattleView.cs` | Fog through the view (battle and siege) |
| Delve profile and routing | `Battle/Timeline/BattleModeProfile.cs:295-300`; routing via `Actions/IntentRouter.cs` (`Delve/Battle/RaidIntentSource.cs` deleted 2026-09-20, combat-ai CAI1.10) | Pluggable `automated` policy |
| Web battle fires chosen actions | `Server/WebMatchService.cs:391,403` (+ replay `:136,151,208,223`) `containerResolver:` | Non-basic actions really resolve in web battle |
| Lawn board seam | `Match/Ai/ILawnBoardView.cs:36-66` + `IOwnSideOracle.RelationOf`: *"the one, enforced seam"* for side and relation (owned units, hypno, vanilla units read as Enemy) | The lawn `IBattleView` adapter takes side **only** from this oracle |
| Lawn swing detection | `Events/EventDrain.cs:631` `IsFirstOfSwing` | The hook for a per-actor swing counter (the counter itself is a wiring gap) |
| Lawn clock host | `Injector/Effects/KernelDriveHost.cs:54-56` (whole budget 0.05–0.15 ms) — **scheduling** reads `KernelDriveHost.NowTicks` / `SimulationClock`; `AdvancedEffectClock` (`Injector/Effects/EffectRuntime.cs:42,133`) is the **wall-clock-seeded status-expiry** clock, NOT the decision clock (battle-engine-ssot D15) | **Two clocks, and they are not interchangeable.** Triggers and lawn cooldowns are **scheduled** on the kernel tick base; status expiry is **wall-clock-seeded**. `combat-ai-map.md:81` carries the same correction — a correction in one document and not its sibling has not landed |
| Lawn kill switch and execution tail | `LawnBasicAttackFeature.cs:56`; `EffectRuntime.cs:359` → `EffectBag.OnEvent` → `InjectorEffectActionSink.Execute` → Funnel → `EntityStatWriter` | The pattern and the write path for a lawn cast |
| Strategy → tactics hand-off | `FrontierRulesPolicy` → one `WorldCommand` → `IBattleResolver.Resolve`; doctrine and standing orders arrive as Hub atoms | World AI stays strategic |

### 4.2 Wiring gaps: machinery exists; one line is inert

**Status 2026-09-21 (lane `combat-ai-3`, checked against code).** The table below is the state **at spec
time** and is kept as this program's own brief; four of its gaps have since been closed, and they say so here
rather than being rewritten — the same convention the *Two identical routers* row already uses:

- **Traits wrap only the fallback stub** — **CLOSED (CAI1.11).** `BasicAttack.cs:175-177` composes the router
  with `decorators: new ITraitDecorator[] { new LoyalTargetRedirect(state, now) }`, and
  `TimelineDispatch.cs:79-86` resolves the reselect site through the same construction, so every policy sees
  the decorated view. `TraitDecoratorTests` proves it reaches a policy, not just the stub.
- **Reselect skips the mode's AI** — **CLOSED (CAI1.10, M5).** The site's own comment records it: *"Closed by
  resolving through the SAME `IntentRouter` construction … so there is no second expression left to disagree
  with it."*
- **Aggression is read only by siege** — **CLOSED (CAI1.9).** `CoreIntentPolicy.cs:416` reads
  `_view.AggressionOf(candidateKey)`; CAI1.13 made the map saturating rather than throwing, and pinned the
  clamp at the read.
- **Two identical routers** — already marked *done* below.
- **Stance gate 0 is inert everywhere** — **HALF CLOSED (CAI3.1).** `BattleRunState.Stance` is the one seam and,
  as of 2026-09-21, has a writer (`BattleEngine.Resolve`'s trailing optional `IStanceCheck? stance`); the two
  dead keys (`ai.stanceDefault`, `ai.autoResolveHandicapMilli`) still wait on narrowing `AiTuning`, which is
  outside that lane's fence.

The remaining six are open and tracked row-for-row in `tasks/combat-ai-todo.md`.

| Gap | The inert line | Closing it |
|---|---|---|
| **The delve has no automated policy** | `Server/RpgHub.cs:251-260` `Resume` throws, on the premise that no "siege-ai-class" policy exists. **False premise:** `SiegeAiIntentSource` exists with generic dependencies (`SiegeAiIntentSource.cs:83-85`). `PlayedSide` belongs to the unused `SiegeIntentSource` router. | Pass the core policy as `automated`, with neutral objective terms when a mode has no objective |
| **Delve fights never start** | `Server/DelveBattleSessionManager.cs:191` `StartSession`, zero production callers | Delve content wiring (party-dungeon D2.16/D5.11) |
| **Siege members fight with basic attacks only** | `World/Turn/DistrictAssaultResolver.cs:415-460`: `EquippedActionIds` is never set. Only `AdditionalHeldActions` (construction, `:450`) is set, and only `ConstructionActions.ContainerResolver` is passed (`:217`). | Thread the real loadout and the shared container resolver, as web battle does |
| **Stance gate 0 is inert everywhere** | `Actions/Defence/StanceRuntime.cs:27` has no production constructor. Every production policy gets `NoStanceHeld.Instance` (e.g. `BattleRunState.cs:628-630`). `AiTuning.StanceDefault` is parsed (`SiegeTuning.cs:435`) and read nowhere, and neither is `AutoResolveHandicapMilli`. | Wire `StanceRuntime`, or delete the dead keys |
| **Aggression is read only by siege** | Only `SiegeAiIntentSource.cs:501` reads `AggressionOf`. The stub (battle, expedition, the delve timeout fallback) ignores it. | The core scorer reads it, so taunt, stealth and decoy work everywhere |
| **Traits wrap only the fallback stub** | `BasicAttack.cs:152` builds `BloodthirstyViewFor` and hands it **only** to the stub at `:165`. The `loyal` redirect runs **after** the decision (`:189-191`). Both are locked as engine-side wrappers (`decisions.md:44`). | The router applies trait decorators to **every** policy. The scorer's kill and low-HP terms read the post-`loyal` target. |
| **Reselect skips the mode's AI** | `Battle/TimelineDispatch.cs:79-80` `intentSource ?? new StubIntentSource(...)` omits `state.DefaultAiIntentSource` | The router owns the fallback chain once, including a **"retarget for a fixed action"** entry point that reselect needs |
| **Combo skills** | `RendezvousLane` exists and no decision-side proposer opens a reservation | A core candidate kind that spans two actors (§8) |
| **Lawn swing counter** | Only `IsFirstOfSwing` detection exists. `EventDrain.cs:120-129` `SwingBump` is a per-**swing** dedupe that is consumed and released, not a per-actor count. | A per-actor counter with die and ptr-reuse cleanup |
| **Lawn cost authority** | `LawnBasicAttackCostCharger.cs:98-104` builds a `CostLedger` with **only** basic-attack rows and `rungOf: (_, _) => 1` | Real held-action cost rows plus holder-rung pricing (`action-skill-tiers` `spec-holder-rung-pricing.md`, `EffectiveRungOf`). Otherwise every lawn skill costs rung 1, a second cost behaviour. |
| **The lawn never calls the decision stack** | Zero injector hits for `IIntentSource \| ActionIntent \| FrozenActionSet \| IBattleView` | The lawn adapter below |
| **Exhaustion has no producer** | No `new ExhaustionPolicy` in `src/` | The lawn plan's `exhaustion-event`, fed by AI spend |
| **Two identical routers** | Both deleted 2026-09-20 (combat-ai `intent-router`, CAI1.10): `RaidIntentSource.cs` (whole file, was delve) and `SiegeIntentSource` (was siege, inside `Battle/Siege/SiegeAi.cs`) — zero production callers confirmed for the latter. Replaced by `Actions/IntentRouter.cs`'s own `steered`/`steeredKeys` chain step | One shared router — done |
| **Siege cover blindness and aggression content** | `spec-siege-ai.md` v1 is cover-free; no status writes `ai.aggression` | Named siege follow-ups; the core inherits them |

### 4.3 Real gaps: no mechanism anywhere

**Status 2026-09-21 (lane `combat-ai-3`, checked against code).** Two of these now have a mechanism, and two
more have half of one — recorded here, not rewritten, so the spec-time brief survives:

- **A per-place "resolvable here" filter** — **CLOSED (CAI1.12).** `IDeclaresExecution`
  (`Effects/EffectModels.cs:139`) is the per-place executor allowlist, and the injector's sink declares the
  opcodes it executes; the filter derives from the allowlist rather than being authored per profile.
- **A profile schema** — **CLOSED (CAI1.6 + CAI1.8).** `Actions/Ai/CombatAiProfile.cs` plus
  `gk-core/data/tuning/combat-ai.v1.json` express a policy as data, with the closed vocabularies pinned per enum.
- **A lawn `IBattleView`** — **CORE HALF CLOSED (CAI4.1).** The adapter is `Actions/Ai/Lawn/LawnBattleView.cs`
  (+ `LawnRelationChain`, `LawnDerivedCache`); its injector host is outside every combat-ai lane's fence, so no
  production host reaches it yet.
- **Lawn activation of a non-basic action** — open (`CAI4.6`), and **A trigger layer for real-time modes**,
  **A decision budget** and **A lawn held-action registry** are open (`CAI4.7`, `CAI4.2`).

| Gap | What would be built |
|---|---|
| A lawn `IBattleView` | An adapter over `ILawnBoardView` / `IOwnSideOracle` (§4.1), **built lazily, only on frames with at least one trigger edge**, never a per-frame O(board) census |
| A lawn held-action registry | A per-ptr `FrozenActionSet`, fed through the Cold loop from the same species/loadout → compiled-action path battle uses |
| Lawn activation of a non-basic action | Raise the chosen action's `OnActivate` atoms into the effect bag on the Hot path (the lawn counterpart of the container resolver). Cast records carry a **record-kind discriminator**, so they never increment the swing counter (a feedback loop) and are never charged as a basic-attack swing (a double charge). |
| A profile schema | Nothing expresses a policy as data today. `CombatProfile` (`Combat/CombatProfiles.cs:9-16`) is a damage-floor knob, **not** an AI profile. |
| A trigger layer for real-time modes | "N swings or T ticks" → a decision request |
| A decision budget | `PerfProbe` has 25 sections and no `lawn.ai.decide` (`Diagnostics/PerfProbe.cs:6-41`). There is no token pool. |
| A per-place "resolvable here" filter | Battle's executor consumes only `ApplyResourceDelta` / `ApplyStatus` / `ModifyStat` / `PlaceStructure` (`BattleEffects.cs:243-251`, the dispatch table), and 9 of 13 atom triggers never fire in battle (battle-engine-ssot D3). An AI would otherwise pick actions that are inert in that place and burn the turn and the resources. The filter derives from the executor allowlist and is not authored per profile. |

### 4.4 Allocation and cost today (the perf claims must start from here)

| Site | What happens today |
|---|---|
| `CostLedger.RowsFor` (`Actions/Cost/CostLedger.cs:67-77`) | Allocates `new List<ActionCostRow>` on **every** `Check`. This is gate 3 of every decision in every mode. |
| `BloodthirstyView` (`BasicAttack.cs:494-501`) | Allocates a list per decision |
| Siege | `SiegeAiIntentSource.ChooseTarget` builds a candidate per live enemy and runs an O(live) threat loop per candidate. That is **O(n²) before** `maxCandidatesScored` applies. Lists, a closure and LINQ are allocated per decision (`:176-270`). |
| Lawn gate 3 | `CostLedger.Check` → `DerivedFor` → `InjectorStatusBridge.ResolveDerived` (`LawnBasicAttackCostCharger.cs:62`). This is the "uncached resolve" the perf audit blames. |

These are named **perf tasks** of the program (§10). "Zero allocation per decision" is a **target** that
the program must reach, not a property that exists today.

## 5. Prior art (numbers, formulas, failure modes)

Sources are in `S5-prior-art.md`. [snippet] means a search excerpt; [unverified] means it could not be
confirmed.

- **Casting from a counter that basic attacks fill is the genre default.**
  - TFT gives **10 / 7 / 5 mana per attack** by role, plus 1% pre-mitigation and 7% post-mitigation of
    damage taken.
  - Dota Auto Chess casts at **100 mana** with most units capped at 10 per attack, so about 10 attacks
    per cast.
  - Idle Heroes: +50 per attack, cast at 100.
  - Hero Wars and AFK Arena: 1000 energy.
  - All [snippet]. The owner's "every N basic attacks" is this shape as an integer.
- **After-cast rules.**
  - TFT locks mana gain **about 1 s after a cast**.
  - Since Set 12, TFT carries overflow **up to one cast**. Before that, reset-to-0 made extra mana
    "actively detrimental".
  - Idle Heroes turns overflow into damage.
- **Configurable party AI is an ordered list of (target selector, condition, action), where the first
  match wins.**
  - FF12 gambits: **2 to 12 slots**.
  - Dragon Age: Origins: **2 tactics slots**, plus one at levels 3/6/10/15/20/25/30.
  - Pillars of Eternity 2 uses weighted random by priority, which is non-deterministic.
  - Known criticism: *"the game plays itself"*. Dragon Age: Inquisition cut tactics down to toggles plus
    a mana/stamina **reserve threshold**, and players complained.
- **Dual utility (Dill, GAP2 ch. 3).**
  1. Veto options with weight ≤ 0.
  2. Keep the top **rank**.
  3. Cut options below a **percentage of the best**.
  4. Pick weighted-random among the rest.

  Zoo Tycoon 2's ranks were 0 / ≈5 / 98–102 / 1,000,000. A player order is a high-rank candidate.
- **Shared scorer with data profiles: Guild Wars 2 Heart of Thorns** (Lewis, GAP3 ch. 13).
  - Considerations are curved and multiplied, and scoring **stops at the first 0**, cheap checks first.
    That ordering was *"a large part of what made the HoT AI sufficiently performant"*.
  - Anti-repeat curves: runtime `1 − x^6` and cooldown `x^5`.
  - Lewis: bonuses only **move** oscillation; add a distinguishing consideration instead.
  - It shipped **100+** reusable patterns, and an NPC was assembled in about 7 minutes.
  - The Division: 9 archetypes, each with an 8-attribute profile.
- **Additive beats multiplied** once many considerations stack (0.9⁹ = 0.39; Mark & Dill, GDC 2010).
  Siege's additive-with-vetoes already does this.
- **Scale by budget.**
  - AC Unity: **40** real AIs in a crowd of about 10,000.
  - Doom 2016: **attack tokens**. The documented failure is a token never released.
  - Unreal behaviour trees are event-driven.
  - Planetary Annihilation thinks at 10 ticks/s.
  - Age of Empires: 1,500 units in lockstep on 200 ms turns.
- **Failure modes:**

  | Failure | Example | Fix |
  |---|---|---|
  | Spam and waste | Ultimates fired with no target, on the last enemy, or a buff before victory | Waste guards |
  | Hoarding | Pathfinder: WotR companions never spend | Reserve threshold instead of a ban |
  | Sync spikes | Everyone casts on the same frame [unverified as a shipped incident] | Seeded offset plus a budget |
  | Oscillation | Ping-pong between two close choices | See the Heart of Thorns bullet above |

## 6. The shape

### 6.1 Three layers, one seam, one scorer

```
trigger (mode loop: WHEN)  ──►  router (who decides; fallback chain; traits)  ──►  policy = core + PROFILE (WHAT)  ──►  IIntentSource  ──►  engine resolves
```

**Layer A: the trigger.**
- **Battle, delve, siege:** the engine pulls a decision per turn or round (built).
- **Lawn:** a decision is requested only on a trigger edge: the actor's `N`-th first-of-swing, or `T`
  ticks of the lawn engine clock (D15), OR'd. Never per frame, never per zombie.
- **Lawn trigger rules** (from prior art, all tunable):
  - a blocked cast **holds at N**, with carry-over capped at one cast;
  - there is a lock of `L` ticks after a cast;
  - a seeded per-actor initial offset breaks sync spikes.

**The router** (new, in `Core/Actions/`) replaces `RaidIntentSource` and `SiegeIntentSource`. It owns:
1. **Steering.** Steered keys go to the player source; everyone else goes to the profiled policy. A
   player order is a **top-rank candidate** that ends on commit or timeout.
2. **The one fallback chain.** Injected source, then the mode's policy, then the default. Both
   `BasicAttack` and `TimelineDispatch.Reselect` use it, plus a **retarget-for-fixed-action** entry for
   `EarlyBoundWithFallback`.
3. **Trait decorators on every policy.** `bloodthirsty` is a view decorator. `loyal` stays a
   post-decision engine redirect, and the scorer is told the redirected target.

**Layer B: the decision core.** It is **`AiScoring` generalised and moved to `Core/Actions/`**, with siege
as its **first consumer in this program**, not a later refactor. That is what keeps one scorer. It runs
target-first, which bounds the work:
1. **Target selection.** A closed selector vocabulary (`nearest`, `same-lane-then-adjacent`,
   `lowest-hp`, `highest-threat`, `objective`, `self`, `ally-lowest-hp`, `ally-downed`) produces the
   candidate targets.
   - Candidates are **capped before any per-candidate work** by the structural `maxCandidatesScored`.
   - The threat term runs only over the capped set, which removes siege's O(n²).
2. **Target scoring** uses the additive weights with vetoes: hit-chance, objective, kill, low-HP,
   cannot-counter, risk, round, aggression tier.
   - Kill and value read `ActionBaseDerivation` at `EffectiveRungOf` and the one estimator. This also
     fixes siege's `IsKillingBlow` call, which omits `baseOverlayDamage` (`SiegeAiIntentSource.cs:214`).
3. **Action choice for the chosen target.** One pass over held actions:
   - `UsabilityEvaluator` gates;
   - the **resolvable-here** filter;
   - the **reserve floor**: a pool may not drop below a fraction of its max after paying;
   - **waste guards**: minimum targets for an area action, target not about to die, fight not about to
     end.

   Then the highest rank row wins, and within a rank the profile's action preference decides.
4. **Selection.** Argmax with an ordinal tie-break (the default, RNG-free). A seeded weighted pick is
   available per profile (the dual-utility cut at `keepPct`).
5. **Anti-repeat.** A commitment bonus and repeat-decay, **merged into `RetargetLedger`** as one
   mechanism, with its state rebuilt on replay.

`StubIntentSource` is this core with a trivial profile (a `nearest` selector, no weights, first usable
action, reserve 0). It may stay as the named fallback class, but its gates and ordering are the core's.

**Layer C: the profile (data).** A profile holds:
- **Ranked rows:** rank, selector, conditions, and an action filter by tag, family or rung.
- **Scoring:** the weight vector, reserve floors, waste guards and anti-repeat values.
- **Real-time modes only:** trigger `N`/`T`/`L`, the budget and the token pool.

How profiles are keyed follows **D5**. The recommendation is **per creature role**, with the place
supplying only its trigger and the inputs it can offer. That keeps "the same creature fights the same
way everywhere".

**Reactions stay automatic.** An engine reaction (`TimelineDispatch.cs:231-252`, `ReactionCounter`
counters whenever `poise` pays) is **not** a profile decision. Profiles are told that reaction spend comes
first, so the reserve floor on `poise` accounts for it rather than being silently defeated.

**Aggression bound.** `ai.aggression` is an additive `FlatSum` channel (`DerivedStatRegistry.cs:296-298`).
`AiScoring.EffectiveTier` **throws** outside ±`aggressionRange` (`Actions/Ai/CandidateScorer.cs:79-86`, moved from SiegeAi.cs by CAI1.1). The core maps the
summed channel onto the closed tier vocabulary by **saturating to the tier range**. That is a bounded
ratio of a closed vocabulary, not a progression cap, and the code must say so. The mapping must land
**before** any content writes the channel. 59 passive-tree seed files already name it.

**Silence and CC.** A binary CC lock is pre-decision (`BattleEngine.cs:766-779` `IsCcLocked`). A future
skills-only lock such as `silence` maps to a basic-only candidate row. On the lawn, `hypno` flips relation
through `IOwnSideOracle`.

### 6.2 Per-place defaults

| Place | Trigger | Default profile (seed values; tuned later) | Place inputs |
|---|---|---|---|
| **Lawn** | `N` swings or `T` ticks, `L` lock, per-frame budget and token pool, seeded offset | Spend while resources last. The reserve sits just above the basic attack's own cost, so it never starves. `same-lane-then-adjacent` targeting. Waste guards on. | Lazy lawn view; side from `IOwnSideOracle`; **no fog**, so a lawn stealth status has no effect there (stated). Kill switch like `LawnBasicAttackFeature`. |
| **Battle / expedition auto** | Per turn | **Switches to the profiled policy (D1)**, in one gated commit: `RulesetVersion` 6, one re-bless, a predicted-delta writeup, and the `ActionSchedule` / dominance re-fit (§7). | Fog; `BattleEnvironment.Stamp` |
| **Delve** (un-steered parties, wave enemies) | Per turn; a player order outranks through the router | Role rows (frontliner / support / striker); `ally-downed` targets under `DownedOnDeplete` | 1-D rank formation; dwell only for the steered party |
| **Siege** | Per round (frozen order) | Today's weights, now running on the shared core | 2-D board, A* objective fallback, structures never decide |

### 6.2a AI tiers, personality, orders, visibility (owner rulings D1–D6)

**Tiers (D6): decided by the actor's class, never by difficulty.** There is one core and one set of
profiles. A **tier** only selects how much work a decision may do:

| Tier | Who | What it may do | Cost envelope |
|---|---|---|---|
| **smart** | **Unique creatures** (Bound specimens, commanders, deployed uniques) in every place | The full core: target-first scoring over the capped candidate set, the reserve and waste guards, anti-repeat, and the seeded personality (below) | Bounded by `maxCandidatesScored` × held actions |
| **performance** | **General creatures** (empire species, general plants holding actions) | The same core on a cheap profile: a fixed selector (`nearest` / `same-lane-then-adjacent`), first usable action after the gates, the reserve floor, no scoring pass | O(held actions), with no target scan beyond the cached view |
| *(reserved)* | Vanilla PvZ units | **Not in this program.** Lawn vanilla control is deferred to a later program (D6). | — |

- A tier is a **profile property**, not a second implementation. Both tiers run the one core. Performance
  is the core with the scoring stage switched off, the same way `StubIntentSource` is the trivial
  profile. That keeps one mechanism (SOLID S). A later "dumb / performance" variant is another tier row.
- **The AI is never a difficulty lever (D2).** Both sides get the same core and the same tier rules, by
  actor class. Difficulty is **its own future sub-program**, designed on gameplay mechanisms, not on AI
  quality. Out of scope here (§9).

**Lawn deploy cap (D6): at most 5 unique creatures per side, 10 on the board.**
- Owner reasoning: a vanilla board at high spawn levels already drops fps. AI control moved out of the
  PvZ engine still costs the host.
- This is a **structural concurrency limit** that protects the frame budget, not a progression ceiling.
  It limits how many **smart-tier** actors run at once. It caps no magnitude and no roster size.
- It lives in tuning (`lawn-deploy` limits, `v{n+1}`), and the code comment says why it is structural.
- **Owned by `creature-lawn-deploy`** (admission at deploy), not by the AI. It must reconcile with the
  existing Zomboss own-unit cap (`ZombossDeployPolicy`) and the contract capacity rule
  (`ContractPolicy.Capacity`), so there is one admission rule, not three.
- General creatures are not counted; they run the performance tier.
- Where the decision runs is unchanged: lawn decisions stay in the injector's Hot loop and never reach
  the server. The cap bounds frame cost there.

**Personality (D5): place × role profiles + a seeded personality offset.**
- A profile is keyed by **place × role** (e.g. `lawn/striker`, `delve/support`, `siege/attacker`).
- Each actor also carries a **personality**: a bounded, seeded offset applied to the profile's weights,
  reserve and aggression tier (e.g. more reckless, more careful, focus-the-weak). It is always inside
  per-profile bounds, so a personality shades a role and never breaks it.
- **Determinism:**
  - A unique creature's personality derives from its **instance id**, so it is stable for life and the
    same in every match, with no storage.
  - A general creature's personality derives from `(match seed, actor key)`, so it is reproducible per
    match.
  - Both use `SeededRng.DeriveStream`, never `System.Random`, and both are covered by replay identity
    (§7).
- Bounds and the personality axes are tunables (`combat-ai.v1`).
- The axis **vocabulary** is closed and lives in code. Whether a future generator authors per-species
  personality defaults is left to seedsmith; seed data is never hand-edited.

**Orders (D3): both.** A commander order can be:
- **the commander's own cast** (as `spec-commander-action-bar.md` specifies); or
- **a direct order to a specific creature**, which the router injects as a **top-rank candidate** for
  that actor and which lasts until the cast commits or times out. The creature's AI resumes underneath.

Orders arrive on the Intent loop (FE → Server → injector) and are queued on the Hot side; a decision
never awaits the server. One router and one candidate path serve both kinds, with no second decision
system.

**Visibility (D4): the full mechanism is visible, but hidden by default (a debug/inspection surface).**
It shows, per actor:
- tier and profile;
- the personality offsets;
- the trigger state (swing count, timer, lock, tokens);
- every candidate with its gate verdicts and its score breakdown;
- the chosen intent and the top-3 alternatives.

It rides `BattleTrace.AiDecision` (golden-neutral, out of `Digest`, zero cost when off), widened from
siege-only to the core. On the lawn it is **off unless enabled**: the injector records decisions into a
bounded ring only when the switch is on. It follows the repo's debug-scope rule: it **reads** real
decisions and never fabricates one.

### 6.3 Performance (made measurable)

- **Turn modes.** A target-first pass is capped before any per-candidate work, then one pass over held
  actions. The allocation sites in §4.4 are fixed as part of the program. The target is zero allocation
  once warm, and a test proves it (the same acceptance line `StubIntentSource` claims).
- **Lawn:**
  - Only RPG-backed actors decide (**D6**), and only on trigger edges. At most 10 smart-tier uniques are
    on the board (the deploy cap); every general creature runs the performance tier.
  - The view is built lazily, only on frames with an edge.
  - Gate 3 reads a **per-frame cached** derived snapshot, never `ResolveDerived` per check.
  - A per-frame decision budget carries overflow to the next frame. A per-window cast-token pool releases
    tokens on death, interrupt or timeout.
  - `lawn.ai.decide` is its own `PerfProbe` section with its own share of the lawn budget. It is **not**
    inside `KernelDriveHost`'s 0.05–0.15 ms.
  - Ships default-on only after a 300-zombie A/B, AI on vs off.

### 6.4 Alternatives rejected

| Alternative | Why |
|---|---|
| One class replacing all five `IIntentSource` implementations | Re-litigates the retracted D13. Policies stay; the scorer is shared. |
| Keeping siege's scorer and adding a second one | The SOLID S fork the audit caught |
| Scoring every (action, target) pair | Work multiplies by held-action count. Target-first is bounded and matches siege. |
| A behaviour-tree core | *"poor at modeling analog concepts such as uncertainty over multiple valid options"* (GAP overview); no tree tooling here |
| GOAP | Heavy per agent |
| Multiplicative utility by default | Scores sink as considerations grow |
| Weighted random by default | Non-deterministic. A seeded pick is opt-in only. |
| Lawn decisions on the server | Violates the Hot loop |

## 7. Goldens, replay and balance (the edges this program crosses)

- **RulesetVersion (H1).** `decisions.md:44` names *"a real divergent multi-action loadout reaching a live
  battle"* as the trigger for the next bump, *"with a predicted-delta writeup"*. `RulesetVersion` is 5
  today, and `BattleGoldenTests` pins outcomes.
  - The siege re-expression and any change to the default auto policy each move goldens.
  - Each one is **one cause, one commit, one re-bless**, with the bump and a predicted-delta writeup.
  - The siege re-expression must be **byte-identical** or be its own bump.
  - **D1 ruled: the battle / expedition default switches to the profiled policy.** It is its own single
    cause: `RulesetVersion` 5 → 6, one re-bless, a predicted-delta writeup (the expedition reward-rate
    change stated in it), and the `ActionSchedule` / dominance re-fit in the same change.
- **Profile version in replay identity.** The web match log stamps `EngineVersion`, `RulesetVersion`,
  `RngAlgoVersion`, `BattleEnvironment.Stamp` and `ContentHash` (`WebMatchService.cs:125-128`).
  `ComputeContentHash` covers database tables only (`RpgStore.ContentHash.cs:21-42`), not `gk-core/data/tuning/*`.
  - A `combat-ai` publish would therefore silently change re-derived automated decisions, and with them
    correlation replays and the delve's `ResumeReplayThenLive`.
  - **The profile version joins the match stamp, and a match pins its profile at start.**
- **The balance twin.** `Balance/Analytic/ActionSchedule.cs` (*"priority-ordered affordability,
  pay-on-commit"*), consumed by `Predictor.cs:39-41,255-258`, and `gk-core/tools/CombatSim/ActionEconomy.cs:136-150`
  model today's greedy spend. The dominance baseline and class-system fits are calibrated on it.
  - **`ActionSchedule` is the core's analytic twin.** It models the default profile's reserve and waste
    guards, and it changes in the same change as the core.
  - **Correction (spec phase, 2026-09-20):** the **dominance** guards are *not* on this path.
    `DominanceGuard.cs:64` and `TerminationGuard.cs:100` call the economy-free `Predictor.Predict(a, b)`
    overload, so extending the schedule moves no dominance baseline. Module 14 runs a confirmation and
    stops to report if a baseline moves.
  - Otherwise the predictor models a policy the game no longer plays.

## 8. Tunables

| Number | File | Notes |
|---|---|---|
| Profile rows (rank, selector, conditions, action filter) | `gk-core/data/tuning/combat-ai.v1.json` (new; does not exist yet) | Selector and condition **vocabularies** are closed and live in code (reviewed changes); the rows are data. |
| Additive weights, `keepPct`, commitment / repeat-decay, reserve floors, waste-guard thresholds | same | Integer per-mille. Siege's weights are the seed values. |
| Lawn `N`, `T`, `L`, budget, token pool | same (lawn section) | Lawn ticks from the one engine clock. The budget is structural (commented). |
| `lawn.ai.decide` share | `gk-core/data/tuning/lawn-perf-budget.v1.json` (new; does not exist yet; the lawn plan's first task) | |
| Siege `ai` keys that **move** | `weightHitChance`, `weightObjective`, `weightKill`, `weightLowHp`, `weightCannotCounter`, `weightRound`, `weightRisk`, `aggressionRange`, `maxCandidatesScored`, `retargetLatencyTicks` → `combat-ai` | They are published with the reader switch in one commit (H7) |
| Siege `ai` keys that **stay** | `objectiveReferenceDistanceCells`, `threatRadiusCells` (siege-loop geometry) → `siege.v{n+1}` | |
| Dead keys | `stanceDefault`, `autoResolveHandicapMilli` | **Wired** (stance, §4.2) or **deleted**. Never migrated as dead config. |

`gk-core/data/tuning/ai.v2.json` is the world/strategic AI and does not merge.

## 9. What this deliberately does not decide

- **Combo-skill content.** The mechanism is `RendezvousLane`. The core only reserves a candidate kind
  that spans two actors. The content belongs to the Vision hole.
- **Difficulty.** Ruled out of AI (D2). Difficulty is its own future sub-program built on gameplay
  mechanisms. Enemy counter-development may later pick *profiles* (behaviour), never *quality*.
- **Vanilla PvZ unit control on the lawn.** Deferred to a later program (D6).
- **Strategic AI** (`FrontierRulesPolicy`, Zomboss deploy and repattern). Combat AI starts at
  `IBattleResolver.Resolve` or at the lawn spawn.
- **Balance values.** Every seed is principle-derived and marked for tuning.

## 10. Owner rulings (2026-09-20). No open questions remain.

| # | Question | Ruling |
|---|---|---|
| **D1** | Does the battle / expedition auto side get the profiled policy? | **Switch now, with the bump**: `RulesetVersion` 6, one re-bless, a predicted-delta writeup, and the predictor re-fit (§7) |
| **D2** | Is AI quality ever different by side or difficulty? | **The same for all.** *"In this game we don't make difficulty by AI — only a smart AI, maybe a performance/dumb AI later. Difficulty will have its own sub-program, designed on gameplay mechanisms."* |
| **D3** | What can a lawn commander order do? | **Both**: the commander's own casts, and direct orders to a specific creature (a top-rank candidate) |
| **D4** | Can players see or shape the AI? | **See the full mechanism, hidden by default.** An inspection and debug surface; no player editing (§6.2a). |
| **D5** | Is the profile per creature or per place? | **Place × role, plus a random (seeded) personality** (§6.2a) |
| **D6** | Which lawn actors decide? | **RPG-backed only.** Vanilla control is deferred to a later program. **AI tiers:** unique = smart, general = performance. **Lawn deploy cap: 5 unique per side (10 max)** (§6.2a). |

Not owner decisions (decided by principle): `N`/`T`/`L`, reserve per-mille, `keepPct`, weights, budgets,
personality bounds, and the tuning-file layout.

**Owed at spec time:** `decisions.md` rows lock these five rulings:
- AI is never a difficulty lever;
- tier by actor class;
- the lawn unique deploy cap (structural);
- place × role + seeded personality;
- hidden-by-default AI inspection.

## 11. Next step

`/spec combat-ai`. Expected modules:
1. **core-scorer** (`AiScoring` generalised; siege as the first consumer, byte-identical or its own
   bump);
2. **profile-schema + tuning** (with the siege key migration);
3. **intent-router** (steering, the fallback chain including reselect, trait decorators);
4. **decision-perf** (the §4.4 allocation sites; the siege O(n²) cap);
5. **resolvable-here filter**;
6. **replay-identity** (profile version in the match stamp);
7. **action-schedule twin**;
8. **delve automated wiring** (`RpgHub.Resume`);
9. **siege loadout wiring** (`EquippedActionIds`, container resolver);
10. **stance wiring or delete**;
11. **ai-tiers + personality** (the tier as a profile property; seeded personality offsets and bounds);
12. **decision-inspector** (widened `AiDecision`, hidden by default, injector ring buffer);
13. **commander direct orders** (a router top-rank candidate, on the Intent → Hot queue);
14. **auto-policy switch** (D1: `RulesetVersion` 6, re-bless, predicted-delta writeup; depends on 1, 6 and 7);
15. **lawn adapter** (lazy view on `ILawnBoardView`, held-action registry, activation with the
    record-kind discriminator, swing counter, cost ledger at `EffectiveRungOf`, trigger layer, budget and
    tokens, perf section).

Module 15 and the perf budget are shared with the backlog-clean-up **lawn plan**. The **lawn deploy cap** spec is drafted in the combat-ai `/spec` run and implemented by `creature-lawn-deploy` through that lawn plan. Each is planned once, there.

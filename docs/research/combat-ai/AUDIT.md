# Adversarial audit: `docs/architecture/combat-ai-ideal.md`

Auditor: independent, read-only. Date: 2026-09-20. Branch `features/mega-merge`.
Every claim below was checked against code in this session. Paths are relative to the repo root.

## Verdict: PASS-WITH-FIXES

The three-layer shape is sound: a trigger per mode, then a shared decision core, then the existing
`IIntentSource` seam. It respects §3c (AI is not the engine) and the retracted D13. The evidence base
has problems, though, and so do four load-bearing claims. The doc must fix them before `/spec`:

1. **It contradicts its own principle 3 by keeping two scorers.** `AiScoring.Score` stays beside a new
   core scorer, and that is a mechanism fork (SOLID S; battle-engine-ssot §2 and §5 Q3/Q4).
2. **"Zero allocations per decision in every mode" is false today.** It is false for siege, and false
   for the stub in production.
3. **It misses the golden/`RulesetVersion` edge.** `decisions.md` names this exact change as the next
   bump trigger.
4. **Traits are silently dropped.** `bloodthirsty` and `loyal` are applied only around the stub
   fallback, and the ideal's new policies would lose them.

§9 "None blocking" hides at least one real owner decision: the battle/expedition default policy.

---

## 1. Citation errors

| # | Ideal says | Code says | Severity |
|---|---|---|---|
| C1 | `EventDrain.cs:211` `SwingBump(rec,+1)` is "a per-ptr swing counter, already paid for" | `EventDrain.cs:120-129`: `SwingBump` keys on `SwingKey(SwingPtr, ActorPtr, Frame)`. It is a **per-swing pending-record dedupe counter** that is consumed and released (`ConsumeSwingTriggerAndRelease`, :135). It never accumulates a per-actor count across swings. The real hook is `IsFirstOfSwing` (`:631`). A per-actor N-counter still has to be built, and it needs die/ptr-reuse cleanup (control-loops §6 rule 4). | High: this is the lawn trigger's foundation |
| C2 | `LawnBasicAttackCostCharger.cs:61` "(same `CostLedger`)" | `:61` is `NowTick()`. The `CostLedger` is constructed at `:98-104`, holds **only the basic-attack cost rows**, and has `rungOf: (_, _) => 1` hardcoded (`:103`). | Medium |
| C3 | `SiegeAiIntentSource.cs:53-138`: "stance (Hold/Guard/Engage)" is part of the built scored policy | `Stance` is an enum (`SiegeAi.cs:32`). `AiTuning.StanceDefault` is parsed (`SiegeTuning.cs:435`) and **read nowhere**, and so is `AutoResolveHandicapMilli`. `SiegeAiIntentSource` is always built with `NoStanceHeld.Instance` (`BattleRunState.cs:628-630`). | Medium: overclaims "built" |
| C4 | `UsabilityEvaluator.cs:15-84` "allocation-free" and `StubIntentSource.cs:27-97` "zero allocation" | True only for their own bodies. Gate 3 calls `CostLedger.Check`, which runs `RowsFor`, which allocates `new List<ActionCostRow>` on **every call** (`CostLedger.cs:69-78`). Production passes `state.CostLedger` (`BasicAttack.cs:165`, `TimelineDispatch.cs:80`). `BloodthirstyView` allocates a `List` per decision (`BasicAttack.cs:494-501`). *(`CostLedger.cs:69-78`, `BasicAttack.cs:165`/`:494-501` and `TimelineDispatch.cs:80` are all PRE-FIX line numbers: `CAI1.14` precomputed `RowsFor`, reused the view's retained list and bound the four delegates once — the production ledger pass is now `BasicAttack.cs:177`.)* | High: the perf claim rests on it |
| C5 | §6.3 "Scoring several targets (siege) is capped by the structural `maxCandidatesScored`" | The cap applies only inside `AiScoring.ChooseTarget` (`SiegeAi.cs:135`; pre-CAI1.1 — that scorer no longer exists there, it is `Actions/Ai/CandidateScorer.cs`, and `SiegeAi.cs` is 75 lines today). **Before** that, `SiegeAiIntentSource.ChooseTarget` builds a candidate for every live enemy, and each candidate runs an O(live) threat loop (`:179-262`). That work is O(n²) and uncapped. It also allocates per decision: `new List` at :179, LINQ `.Select().ToList()` at :270, a closure at :176, and LINQ throughout `ChooseTarget`/`TopThree`. | High |
| C6 | §3 principle 4 / §4.1: "Battle, delve and siege replay from a recorded intent stream (`DecisionTrace`)"; "Replay is free for any policy behind the seam" | `DecisionTrace` records **only human decisions** (`DecisionSource.Player`/`Timeout`, `DecisionTrace.cs:5-20`). Automated decisions are **re-derived** on replay (`InteractiveIntentSource.cs:125-151`; `RaidIntentSource` sends un-steered keys straight to `automated`). Siege never uses `DecisionTrace`. It replays from `(setup, seed)`. So replay is free only while the policy is unchanged. See M9. | High |
| C7 | "disagreements … resolved against code, see §3.4"; "Under ruling 3.2" (§6.1) | The doc has no §3.4, and "ruling 3.2" is ambiguous (§3 is a principle list). | Low |
| C8 | `DistrictAssaultResolver.cs:452` `AdditionalHeldActions` | Line 450. | Trivial |
| C9 | "Only `BattleRunState`, `FoggedBattleView`, `BloodthirstyView` and a test fake implement" `IBattleView` | There are three test implementors (`ActionSelectionTests`, `SiegeAiIntentSourceTests`, `SiegeFogTests`). `BloodthirstyView` is a private nested class in `BasicAttack.cs:489` — a PRE-FIX line: `CAI1.11` moved it into the router's `BloodthirstyDecorator`, which now wraps every policy, not only the stub fallback. | Trivial |

Verified correct: `IntentSource.cs:29-37`, `BasicAttack.cs:163-165` (PRE-FIX: `CAI1.10`/`CAI1.11` replaced that three-term chain with one `IntentRouter.Compose` call, `BasicAttack.cs:175-179`), `ActionTagPreference.cs:16-60`,
`FrozenActionSet.cs:18-46`, `CooldownLedger.cs:29-106`, `BattleModeProfile.cs:295-300`,
`RaidIntentSource.cs:42-43` (deleted by combat-ai CAI1.10, `c284f5f6d`; the steered-vs-automated dispatch is `Actions/IntentRouter.cs`), `SiegeAi.cs:220-239` (pre-CAI1.1 — that scorer no longer exists there, it is `Actions/Ai/CandidateScorer.cs`), `WebMatchService.cs:136,151,208,223,391,403`,
`KernelDriveHost.cs:54-56`, `LawnBasicAttackFeature.cs:56`, `EffectRuntime.cs:359`,
`RpgHub.cs:251-260`, `DelveBattleSessionManager.cs:191`, `DistrictAssaultResolver.cs:217,415-460`,
`CombatProfiles.cs:9-16`, `PerfProbe.cs:6-41` (25 sections), and `BattleRunState.cs:405,1202`. The
injector has zero hits for `IIntentSource|ActionIntent|FrozenActionSet|IBattleView`.

## 2. Bucket errors

| # | Item | Ideal bucket | Correct bucket | Why |
|---|---|---|---|---|
| B1 | **Combo skills (delve)** | Real gap ("no `combo` under `Core/Delve`") | **Wiring gap** | `Core/Battle/Timeline/RendezvousLane.cs:1-44` (B7/T2e) already implements *"multi-actor coordinated actions (link-strikes)"*: an atomic multi-slot acquire, one shared `LinkedResolve`, and rollback. What is missing is a decision-side *proposer* that opens a reservation. The grep searched the wrong directory. |
| B2 | **Aggression channel**: "Taunt, stealth and decoy work in every mode through the Hub" | Built | **Wiring gap** for every mode except siege | Only `SiegeAiIntentSource.cs:258` reads `AggressionOf`. `StubIntentSource` (battle, expedition, the delve timeout fallback) never reads it. |
| B3 | Stance gate 0 as part of the built legality core | Built (implied) | **Wiring gap** | `StanceRuntime` (`Actions/Defence/StanceRuntime.cs:27`) has no production constructor. Every production policy gets `NoStanceHeld.Instance`, so gate 0 is inert everywhere. |
| B4 | Swing-count trigger host | Built ("cost no new detection") | **Wiring gap** (small) | The detection (`IsFirstOfSwing`) exists. The per-actor count and its lifecycle do not (C1). |
| B5 | Lawn cost authority | Built | **Wiring gap** | The lawn ledger holds only the basic-attack rows and prices at `rungOf => 1`. Held actions need the real rows and holder-rung pricing (`action-skill-tiers` `spec-holder-rung-pricing.md`, `BattleRunState.EffectiveRungOf`). Otherwise the lawn prices every skill at rung 1, a second cost behaviour. |
| B6 | A lawn `IBattleView` | Real gap | **Partly built** | `Core/Match/Ai/ILawnBoardView.cs:36-66` already has a Unity-free lawn board view and `IOwnSideOracle.RelationOf`, *"the one, enforced seam"* for side and relation. It handles owned units, hypno, and vanilla units read as Enemy. The lawn `IBattleView` adapter must get side from that oracle, never from the raw board side. |

## 3. Misses (what a shared core must account for)

| # | Miss | Evidence | What the ideal should add |
|---|---|---|---|
| M1 | **`bloodthirsty` / `loyal` traits are applied only around the stub fallback** | `BasicAttack.cs:152` wraps the view with `BloodthirstyViewFor` and passes it **only** to `new StubIntentSource(view, …)` (:165). `state.DefaultAiIntentSource` (siege) and every injected source (interactive, raid) get the raw state. The `loyal` redirect runs post-decision (:189-191) — PRE-FIX line numbers, and the defect this row names: `CAI1.11` moved both onto the router, so the decorators reach EVERY policy and the redirect is attached as the router's `LoyalTargetRedirect` decorator (`BasicAttack.cs:179`, its `EffectiveTargetOf` explained at `:204-205`). `decisions.md:44` (Action selection row) locks both as engine-side wrappers. | State that trait decorators apply to **every** policy (at the router or seam), and that scorer considerations (kill, low-HP) must use the post-`loyal` target or they score the wrong actor. Flag the `lowest-hp` selector vs `bloodthirsty` overlap: two mechanisms for "focus the weakest". |
| M2 | **Golden / `RulesetVersion` edge (H1)** | `decisions.md:44`: *"Trigger for the next bump: a real divergent multi-action loadout reaching a live battle … bump `RulesetVersion` then with a predicted-delta writeup."* `BattleModels.cs:284` `RulesetVersion = 5`. `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs` pins outcomes. The ideal's `battle/auto` profile ("stub order plus reserve and waste guards") changes the default policy for every battle and expedition. | Add a section: the default-policy change is a ruleset bump with a single re-bless and a predicted-delta writeup. Otherwise keep `battle/auto` byte-identical to the stub until the owner approves (see D1). |
| M3 | **AI profile version is not in any replay identity** | The web match log stamps `EngineVersion, RulesetVersion, RngAlgoVersion, BattleEnvironment.Stamp, ContentHash` (`WebMatchService.cs:125-127`). `ComputeContentHash` covers DB tables only (`RpgStore.ContentHash.cs:21-42`), not `gk-core/data/tuning/*`. A `combat-ai.v{n+1}` publish would silently change the re-derived automated decisions for correlation replays and for delve `ResumeReplayThenLive`. | Require the profile/tuning version in the match stamp, or pin the profile per match at start. |
| M4 | **Balance analytics model the current spend policy** | `Balance/Analytic/ActionSchedule.cs` (P4.5): *"priority-ordered affordability, pay-on-commit"*, consumed by `Predictor.cs:39-41,255-258`. `gk-core/tools/CombatSim/ActionEconomy.cs:136-150` `ActionPolicy.Choose` means "highest-priority affordable". The DominanceBaseline and class-system fits are calibrated on greedy spend. | Reserve floors, waste guards and anti-repeat make the realised policy differ from the predicted one. Name `ActionSchedule` as the core's analytic twin that must be updated in the same change, or state that the predictor models only the default profile. |
| M5 | **Two fallback sites disagree** | `BasicAttack.cs:163-165` includes `state.DefaultAiIntentSource`. `TimelineDispatch.cs:79-80` (`Reselect`) is `intentSource ?? new StubIntentSource`, which **omits** it. *(Both are PRE-FIX line numbers; `CAI1.10`/`CAI1.11` gave the two sites the one `IntentRouter` chain, which is the fix this row asks for.)* | The shared router or core must own the fallback chain once. A second query also exists: **reselect** (target only, for an already-committed action, `EarlyBoundWithFallback`). The core needs a "retarget for fixed action" entry point. Scoring (action, target) pairs does not answer it. |
| M6 | **Reaction lane is a hidden auto-decision** | `TimelineDispatch.cs:231-252`: a defender that enters the lane **always** counters if poise pays (`ReactionCounter.TryCounter`). No policy is consulted. | A reserve-floor profile on `poise` is defeated by automatic counters. Either the core owns "react or not", or the ideal states that reactions are engine-automatic and outside the profile. |
| M7 | **Mode-inert actions** | DESIGN-GATE §1 Battle row: battle's executor consumes only `ApplyResourceDelta`/`ApplyStatus`/`ModifyStat`/`PlaceStructure` (`BattleEffects.cs:206-225`). battle-engine-ssot D3: 9 of 13 atom triggers never fire in battle. | A shared scorer will value actions whose effects are inert in the current place, so the turn is wasted and resources are spent for nothing. Add a per-place "resolvable here" filter derived from the executor allowlist, not authored per profile. |
| M8 | **Estimator discipline (battle-engine-ssot §5 Q4)** | *"never estimates it with a private formula"*; `SiegeExpectedDamage` is the named anti-example (D7, fixed 2026-09-17). `SiegeAiIntentSource.cs:214` still calls `IsKillingBlow` **without `baseOverlayDamage`** (defaults to 0.0, `SiegeExpectedDamage.cs:113-116`). The file's own doc says omitting it *"changes the mitigated fraction"*. | The ideal adopts siege's vocabulary as "the starting set". It must say the kill and value considerations read the action's base damage through `ActionBaseDerivation.BasePowerMilli` at `EffectiveRungOf` (action-enrich `action-base`, built: `Core/Actions/ActionBaseDerivation.cs`), plus the one resolver estimator. It must never use its own value math. |
| M9 | **Principle 4 "pure function of (actor, tick, view)" contradicts the design** | `RetargetLedger` (`SiegeAiIntentSource.cs:316-351`) is per-battle state. §6.1 step 5's commitment bonus and repeat-decay are memory too. | Restate as: deterministic in `(setup, seed, human trace, profile version)`, with policy state rebuilt by replay from tick 0. Also merge commitment bonus with `RetargetLedger`/`retargetLatencyTicks`. Two anti-oscillation mechanisms would be a fork. |
| M10 | **Commander combat book is not a per-creature manual arm** | `lawn-interactive/spec-commander-action-bar.md` (Objective: *"Enqueue off-board commander combat orders"*; Assumption 2: commander never a tile, one bar). Checkpoint E = `tasks/lawn-interactive-plan.md:329`. Orders arrive on the **Intent** loop (FE→Server→injector), not the Hot loop. | The router's "player order pre-empts AI for that actor" does not map. Commander orders are the commander actor's own casts. Say whether commander orders may also override creature AI (D3), and put the order queue on the Hot side, fed from the Intent loop. |
| M11 | **Lawn cast vs swing counter and cost re-entry** | `LawnBasicAttackCostCharger` charges on `OnDamageDealt` + `IsFirstOfSwing`. Control-loops §6 rule 7 (re-entry depth 0). | A lawn cast's damage records must not increment the swing counter (a feedback loop) and must not be charged as a basic-attack swing (a double charge). State the record-kind discriminator. |
| M12 | **CC and status decisions** | `BattleEngine.cs:766-779` `IsCcLocked` is a binary pre-decision lock. There is no `silence` (skills-only lock) and no taunt/fear redirect status. `charm_pulse`/`hypno` are Cc. On the lawn, `hypno` flips relation (B6). | Name how the core handles a silenced actor (basic-only row) once such a status exists, and read side from `IOwnSideOracle` on the lawn. S5's "cast blocked (silenced) → hold at N" is cited without a producing status. |
| M13 | **Aggression bound vs additive channel** | `ai.aggression` is `FlatSum` (`DerivedStatRegistry.cs:292`). `AiScoring.EffectiveTier` **throws** outside ±`AggressionRange` (2) (`SiegeAi.cs:96-103`; pre-CAI1.1 — that scorer no longer exists there, it is `CandidateScorer.EffectiveTier` in `Actions/Ai/CandidateScorer.cs`). Passive-tree seed quota cells name `ai.aggression` in 59 files under `gk-data/packs/fusion/data/seed/passive-tree/nodes/` (not yet realised in atoms). | Once content writes it, two stacked +1 sources and a +1 status crash the siege AI mid-battle. The shared core must define how a summed channel maps onto a closed tier vocabulary before any content lands. |
| M14 | **Lawn clock (D15)** | battle-engine-ssot D15: the lawn had two time bases. `EffectRuntime.cs:42,133` now wires `AdvancedEffectClock`. `LawnBasicAttackCostCharger.NowTick` = `KernelDriveHost.NowTicks/100`. | `T`, `L` and the lawn `CooldownLedger` must read the same engine clock that status expiry reads. Cite D15 and the ruling that the clock is one engine module. |
| M15 | **Expedition place** | the-loops §2 and §6: *"Expeditions stay auto-resolve"*. Expedition battles resolve at collect through `WebMatchService` with no `intentSource`, so the stub applies. | This makes `battle/auto` the **idle economy's** policy. Any change moves reward rates, which is a product call (D1). |
| M16 | **Named combat reactions (Vision hole)** | `docs/guide/the-loops.md:152,164` lists lawn, delve and interactive. | The ideal lists two Vision holes and omits this one, which an AI "set up wet, then lightning" consideration serves directly. One line is enough. |

## 4. Design challenges

1. **Two scorers is a SOLID S violation the ideal locks in.** Principle 3 says *"How a decision is scored
   and gated is a shared mechanism with one implementation."* §6.1 then keeps `SiegeAiIntentSource` +
   `AiScoring.Score` as they are, adds a new core scorer with the same additive-weighted-consideration
   semantics, and calls re-expressing siege "not a requirement". Ruling D13 protects **several
   policies**, not **two scoring mechanisms**. CLAUDE.md's SOLID rule says extending a
   SOLID-violating seam needs a *named, sequenced* remediation first. **Fix:** make the core scorer
   `AiScoring` generalised: move it to `Core/Actions/`, widen `AiCandidate` from target-only to
   (action, target), and make siege its first consumer in the same program. It must not be a
   deferred refactor.
2. **The dimension mismatch is understated.** Siege scores **targets**, then takes the first usable
   action (`SiegeAiIntentSource.cs:102-123`). The core scores (action, target) pairs. So "siege is this
   core with the siege profile" is not true as written. Scoring pairs also multiplies work by
   held-action count, and §6.3's "one pass over held actions for one chosen target" contradicts it.
   Pick one: select the target first and then score actions (bounded), or score pairs with an explicit
   structural cap.
3. **The perf claims are unsupported.** See C4 and C5. There are also three lawn hot-path costs:
   - `CostLedger.Check` → `DerivedFor` → `InjectorStatusBridge.ResolveDerived` on every gate-3 check
     (`LawnBasicAttackCostCharger.cs:62`), which is exactly the "uncached resolve" the perf audit
     blames.
   - A census "cached per frame" costs O(board) every frame, even with no trigger edge. Build it
     lazily, only on frames that have at least one edge.
   - `KernelDriveHost`'s whole budget is 0.05–0.15 ms. State whether decisions run inside it or in
     their own `lawn.ai.decide` share.
4. **The determinism claim is imprecise.** Argmax plus an ordinal tie-break is RNG-free, but the inputs
   are doubles: `Derived.Get` returns `double`, and `SiegeHitChance` uses `CombatProbability.Sigmoid`
   (`Math.Exp`), rounded once. §5's *"integer … scores avoid the question"* is wrong for siege. The
   repo's answer already exists: `BattleEnvironment.Stamp` (`BattleModels.cs:662-684`, arch/OS/runtime
   major, because `Math.Exp` differs by libm). Cite it, and do not claim integer purity.
5. **The tuning single home is only half right.** The `siege.v1.json` `ai` block mixes weights with
   structural and siege-loop values: `aggressionRange`, `maxCandidatesScored`, `retargetLatencyTicks`,
   `objectiveReferenceDistanceCells`, `threatRadiusCells`, `stanceDefault`, `autoResolveHandicapMilli`.
   The ideal moves "`ai.*` weights" but does not say which keys move and which stay. Two unused keys
   (C3) should be deleted or wired, not migrated as dead config. The H7 same-commit reader switch is
   correct.
6. **Router dedup is fine, but it is not the whole fallback story.** A router with steered→player,
   else→profile does not resolve M5 (the dropped `DefaultAiIntentSource` on reselect) or M1 (the trait
   decorator). Put both in the router's contract.
7. **Hidden and manufactured questions.**
   - §2 promises *"You can see and later shape how each side fights"*. §8 then says player-edited AI
     is out of scope. The promise is either a commitment or it is not; surface it (D4).
   - §9 "None blocking" omits D1, which `decisions.md` already requires as an ask-first bump.
   - §2 *"the same creature … playing the same way in every place"* conflicts with §6.1 Layer C
     `place × role` keys. That is a real identity question (D5).
8. **"Fog for free" does not hold on the lawn.** The lawn adapter declares "no fog". Fine, but siege's
   `FoggedBattleView` fog-gates `AggressionOf`. A lawn stealth status would then do nothing on the
   lawn. Say so.

## 5. Owner decisions the ideal should surface

| # | Decision | Options | Recommended default |
|---|---|---|---|
| D1 | **Does the idle and web battle auto side get smarter?** (changes expedition reward rates and every battle golden) | (a) Keep `battle/auto` byte-identical to `StubIntentSource`; the core serves only lawn, delve and new siege. (b) Switch the default to a profiled policy with a `RulesetVersion` 6 bump, a single re-bless, a predicted-delta writeup, and a re-fit of `ActionSchedule`/Dominance baselines. (c) Switch only for new matches, with the profile version stamped and old matches replayed on the pinned profile. | **(a) now, (b) as its own gated step.** `decisions.md:44` already names this as an ask-first bump. |
| D2 | **Fairness: does the enemy side get the same AI quality as your automated side?** | (a) Strictly symmetric: same core, same profiles by role. (b) Enemy difficulty through profile selection per danger band or tier. (c) Symmetric now; profiles become a counter-development lever later. | **(c).** It matches R23 symmetric empires and the counter-development hole, with no difficulty knob before content. |
| D3 | **Lawn player control: what does a commander order do?** | (a) Commander-only casts (as specced); creature AI is never overridden. (b) An order can command a specific creature to cast, pre-empting its AI. (c) Both. | **(a).** It matches `spec-commander-action-bar.md`. (b) is a new product surface. |
| D4 | **Can players see and shape AI?** (§2 promises it, §8 excludes it) | (a) Read-only: show the chosen profile and the last decision (AiDecision top-3). (b) Pick a preset profile per creature. (c) Full gambit editing with slots as a progression reward. (d) None. | **(a)**, with a profile id on build presets later. It is cheap because `BattleTrace.AiDecision` exists (`SiegeAi.cs:25-30`). |
| D5 | **AI identity: per creature or per place?** | (a) Profile keyed by creature role; a place supplies only the trigger and the inputs it has. (b) `place × role` as in §6.1. (c) Species-authored personality in seed data (generator-owned). | **(a).** It keeps §2's promise that the same creature plays the same way everywhere. |
| D6 | **Which lawn actors decide?** | (a) Only RPG-backed actors (Bound, general plants with actions, deployed creatures) on both sides. (b) Also vanilla zombies, through a zombie-side profile. | **(a).** Vanilla units have no kit; (b) is the 300-agent cost for no content. |

Not owner decisions (decide by principle): N/T/L, reserve per-mille, `keepPct`, weights, budgets and
the tuning-file layout.

## 6. Suggested edits (concise)

1. §4.1: fix C1–C5 and C8/C9. Move stance, aggression-in-every-mode, the swing counter and the lawn
   cost authority into §4.2 as wiring gaps (B2–B5). Add `ILawnBoardView`/`IOwnSideOracle` (B6).
2. §4.3: move combo skills to §4.2 and cite `RendezvousLane` (B1).
3. §3.4: restate determinism as `(setup, seed, human trace, profile version)`. Cite
   `BattleEnvironment.Stamp`. Drop "integer-only" for siege.
4. §6.1: make `AiScoring` the core, with siege as consumer #1 in this program. Resolve the target-first
   vs pair scoring question. Merge anti-repeat with `RetargetLedger`. The router owns the fallback
   chain, including `TimelineDispatch.Reselect`, and the trait decorators on every policy.
5. §6.1 step 2: add a mode-resolvability filter from the battle executor allowlist (M7), and a
   `poise`/reaction note (M6).
6. §6.1 considerations: kill and value read `ActionBaseDerivation` at `EffectiveRungOf` and the single
   resolver estimator. Pass base damage (M8).
7. §6.3: remove "zero alloc in every mode" until `CostLedger.RowsFor`, `BloodthirstyView` and the
   siege LINQ/List are fixed. List these as named perf tasks. Build the census lazily. Cap siege's
   threat loop before scoring.
8. §7: list exactly which `siege.v1.json` `ai` keys move. Wire or delete `stanceDefault` and
   `autoResolveHandicapMilli`. Handle the bound of the additive aggression channel (M13).
9. New §: "Goldens, replay and balance": `RulesetVersion` bump rules (M2), a profile-version stamp
   (M3), and the `ActionSchedule`/Predictor twin (M4).
10. Lawn: the lawn ledger gets real held-action rows and `EffectiveRungOf` (B5). Cast records do not
    feed the swing counter or the basic-attack charge (M11). Use one clock (M14). The commander book
    is the commander's own casts (M10).
11. §9: replace "None blocking" with D1–D6.

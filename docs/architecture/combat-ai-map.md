# Capability map: `combat-ai`

**Status: APPROVED 2026-09-20** by independent agent review (verdict APPROVE-WITH-CHANGES, all three
changes applied), under owner ruling D1 (backlog-clean-up: R28 extends to all programs).

- **Ideal:** [combat-ai-ideal.md](combat-ai-ideal.md), revision 3. Its owner rulings D1–D6 are binding
  and are not reopened here.
- **Evidence:** [../research/combat-ai/](../research/combat-ai/) (S1–S5 + AUDIT).
- **Module specs:** `docs/architecture/combat-ai/spec-<module-id>.md`.
- **Plan / tasks:** [tasks/combat-ai-plan.md](../../tasks/combat-ai-plan.md) /
  [tasks/combat-ai-todo.md](../../tasks/combat-ai-todo.md) — written 2026-09-20 (prefix `CAI`,
  38 tasks over 5 waves). Its "Corrections carried into this plan" section resolves three places where
  two specs disagreed; read it before building a module. A picking-up session starts at
  [tasks/combat-ai-handoff.md](../../tasks/combat-ai-handoff.md).
- **Parent:** `backlog-clean-up` (map module 12). This program is the combat-ai build its ideal calls for.
- **Session record:** `tasks/sessions/backlog-clean-up-20260920.json`.

## Load-bearing rules (restated so every module spec inherits them)

1. **The engine resolves, the AI decides** (`battle-engine-ssot.md` §3c). Everything here is on the
   deciding side of `IIntentSource.TryDeclare`. No module changes what the engine *resolves*, except
   where a spec names an engine-seam wiring gap (reselect fallback, trait wrapper), and that change is
   byte-identical.
2. **One scorer, several policies.** `AiScoring` is generalised into `Core/Actions/` and is the only
   scorer. Existing `IIntentSource` classes may remain as named policies.
3. **Determinism.** A decision is a function of `(setup, seed, human trace, profile version,
   BattleEnvironment.Stamp)`. Randomness comes only from `SeededRng.DeriveStream`, never from a clock.
4. **The lawn is the Hot loop.** Lawn decisions run in the injector, in process, with no server await.
   Logic lives in Core; the injector adapts.
5. **Tiers are actor class, not difficulty** (D2, D6): smart = unique creatures, performance = general
   creatures. There is no difficulty lever in AI.
6. **Tunables** go in `gk-core/data/tuning/combat-ai.v1.json` (new; does not exist yet) through `publish.py`.
   Structural limits carry a comment. **Two tool gaps the writers found:** `publish.py` cannot create a
   new domain, so module 2 authors `combat-ai.v1.json` (including the lawn keys module 19 reads), and it
   has no key-removal, so the siege migration (module 2) and the dead-key deletion (module 11) need a
   narrow `--remove-key`. Both are tasks of this program, not assumptions.
7. **Goldens (H1).** A golden moves for one cause per commit. The siege re-expression is byte-identical.
   The auto-policy switch is its own `RulesetVersion` 6 bump.
8. **Tests** assert contracts and closed vocabularies (selectors, conditions, personality axes, tiers),
   never population counts or generated text.

## 1. Modules

### Wave 1: the shared core (Core only; battle, delve and siege unchanged in behaviour)

| # | Module id | Responsibility | Depends on |
|---|---|---|---|
| 1 | `core-scorer` | Generalise `AiScoring` (`Battle/Siege/SiegeAi.cs`) into `Core/Actions/`. Target-first scoring over a candidate set **capped before any per-candidate work**. Additive weights with vetoes. Argmax with ordinal tie-break, plus an opt-in seeded weighted pick. Kill and value read `ActionBaseDerivation` at `EffectiveRungOf` and the one estimator (fixes the `IsKillingBlow` omission of `baseOverlayDamage`). Anti-repeat merged into `RetargetLedger`. **Siege is consumer #1, byte-identical** (siege goldens unchanged). | — |
| 2 | `profile-schema` | The profile data model: ranked rows (rank, selector, conditions, action filter), weights, reserve floors, waste guards, anti-repeat, trigger block. Closed vocabularies in code: selectors, conditions, tiers, personality axes. `gk-core/data/tuning/combat-ai.v1.json` + parser + host injection. Profile keyed by **place × role** (D5). Siege key migration: the ten keys named in ideal §8 move to `combat-ai`, two siege-geometry keys stay in `siege.v{n+1}`, and the two dead keys are wired or deleted (with `stance-wiring`). The reader switch lands in the same commit (H7). | 1 |
| 3 | `ai-tiers-personality` | Tier as a profile property: **smart** runs the full scorer; **performance** runs a fixed selector, first usable action after the gates, and the reserve floor, with no scoring pass. Tier chosen by actor class. Seeded personality: bounded offsets on weights, reserve and aggression tier. A unique's derives from its **instance id**; a general's from `(match seed, actor key)`. | 1, 2 |
| 4 | `intent-router` | One router in `Core/Actions/` replacing `RaidIntentSource` / `SiegeIntentSource`. It owns steering (steered → player source; a player order is a top-rank candidate), **the one fallback chain** (fixes `TimelineDispatch.Reselect` skipping `DefaultAiIntentSource`), a **retarget-for-fixed-action** entry, **trait decorators on every policy** (`bloodthirsty` view; `loyal` post-redirect communicated to the scorer), and a queue input for direct orders. | 1 |
| 5 | `resolvable-here` | A per-place filter derived from each place's executor allowlist (battle: `BattleEffects.cs:206-225`), so the AI never picks an action whose effects are inert in that place | 1 |
| 6 | `aggression-tier-map` | *(Derived from ideal §6.1 "Aggression bound" / audit M13, not from the §11 list.)* Map the additive `ai.aggression` (`FlatSum`) channel onto the closed tier range by saturation, a **bounded ratio of a closed vocabulary** (commented), replacing the throw in `AiScoring.EffectiveTier`. It must land before any content writes the channel. | 1 |
| 7 | `decision-perf` | *(Depends on `intent-router` because the router moves `BloodthirstyView` into a trait decorator; fixing the allocation before the move would fix it twice.)* Remove the per-decision allocations: `CostLedger.RowsFor` (`CostLedger.cs:67-77`), `BloodthirstyView`, siege lists/LINQ/closures. Cap siege's O(n²) threat loop by running it only over the capped candidates. A zero-allocation-once-warm test for every policy. | 1, 4 |

### Wave 2: identity, balance and visibility

| # | Module id | Responsibility | Depends on |
|---|---|---|---|
| 8 | `replay-identity` | The profile version (the `combat-ai` tuning version + profile ids) joins the web-match stamp (`WebMatchService.cs:125-127`). A match pins its profile at start. Delve `ResumeReplayThenLive` and correlation replays use the pinned profile. | 2 |
| 9 | `action-schedule-twin` | `Balance/Analytic/ActionSchedule.cs` (and `Predictor.cs` consumers) model the default profile's reserve floor, waste guards and tier. `gk-core/tools/CombatSim/ActionEconomy.cs` stays consistent. | 2, 3 |
| 10 | `decision-inspector` | D4: widen `BattleTrace.AiDecision` from siege to the core. Per actor: tier, profile, personality, trigger state, each candidate's gate verdicts and score breakdown, the chosen action and the top-3. **Hidden by default**, golden-neutral (out of `Digest`), zero cost when off. A read surface only: it never fabricates a decision. | 1, 3, 4 |

### Wave 3: place wiring (turn modes)

| # | Module id | Responsibility | Depends on |
|---|---|---|---|
| 11 | `stance-wiring` | Give `StanceRuntime` a production constructor and route stance into gate 0 for every policy, **or** delete `StanceRuntime` / `stanceDefault` / `autoResolveHandicapMilli` with a stated reason. Decision criterion: is any held action a stance action today? | 2, 4 |
| 12 | `siege-loadout-wiring` | `DistrictAssaultResolver.BuildAnimateSetups` sets real `EquippedActionIds` and passes the shared container resolver (as `WebMatchService` does), not only the construction resolver. Its own golden cause. | 1 |
| 13 | `delve-automated-wiring` | `RpgHub.Resume` and the delve session take the router + core policy as `automated` (delve profile rows: frontliner / support / striker, `ally-downed` targets). The spec's "never `StubIntentSource`" boundary is honoured. `StartSession`'s content caller stays party-dungeon's. | 3, 4, 8 |
| 14 | `auto-policy-switch` | D1: the battle and expedition default becomes the profiled policy. **`RulesetVersion` 5 → 6**, one re-bless, a predicted-delta writeup (including the expedition reward-rate change), the `action-schedule-twin` re-fit, and a dominance **confirmation run**. *(Correction, writer lane W3: `DominanceGuard.cs:64` and `TerminationGuard.cs:100` call the economy-free `Predictor.Predict(a, b)` overload, so the action economy is not on the dominance path. A moved baseline is a stop-and-report, not an expected outcome.)* A single cause, one commit. | 3, 5, 7, 8, 9 |

### Wave 4: the lawn (injector adapters over the same core)

| # | Module id | Responsibility | Depends on |
|---|---|---|---|
| 15 | `lawn-actor-view` | An `IBattleView` over `ILawnBoardView` + `IOwnSideOracle` (the side comes only from the oracle; hypno flips it). Built **lazily, only on frames with at least one decision edge**. Derived snapshot cached per frame (never `ResolveDerived` per check). No fog. | 1 |
| 16 | `lawn-held-actions` | A per-ptr `FrozenActionSet` on the lawn, fed through the Cold loop from the same species/loadout → compiled-action path battle uses. Withdrawn on die before ptr reuse (control-loops §6 rule 4). | — *(corrected: it reads no profile)* |
| 17 | `lawn-cost-authority` | The lawn `CostLedger` gets the real held-action cost rows and prices at **`EffectiveRungOf`** (holder-rung pricing), replacing `rungOf => 1`. Basic-attack charging unchanged. | 16 |
| 18 | `lawn-cast-activation` | Fire a chosen action's `OnActivate` atoms into the Hot effect bag → Funnel → `EntityStatWriter`. The **record-kind discriminator** keeps cast records out of the swing counter and out of the basic-attack charge. Re-entry depth 0. | 16, 17 |
| 19 | `lawn-cast-trigger` | *(Depends on `lawn-cast-activation` so a cast path exists and is testable before live per-frame triggering is wired to it.)* Per-actor swing counter (from `IsFirstOfSwing`, with die/ptr-reuse cleanup) and a timer on the **kernel tick base** (`KernelDriveHost.NowTicks / 100`, the 100 ms grid the lawn cost ledger already uses), OR'd. **Correction (writer lane W5):** the map first named `AdvancedEffectClock`; that clock is wall-clock-seeded for status expiry (`EffectRuntime.cs:42,133`) and is not the decision clock. Hold-at-N with carry-over capped at one cast, a post-cast lock `L`, and a seeded initial offset. Per-frame decision budget with overflow carry, a cast-token pool (released on death/interrupt/timeout), `PerfSection` `lawn.ai.decide` with its budget share, and a kill switch (const default + env + debug). | 15, 18 |
| 20 | `commander-direct-orders` | D3: a lawn order to a specific creature enters `intent-router` as a top-rank candidate until commit or timeout. Commander own-casts stay `lawn-interactive`'s. Orders flow Intent loop → Hot queue. | 4, 19 |

### Cross-program specs that combat-ai depends on (not combat-ai modules)

Each has exactly one author and one implementation home:

| Spec path | Spec authored by | Implementation owned by | Responsibility |
|---|---|---|---|
| `docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md` | this `/spec` run, on behalf of `creature-lawn-deploy` | **`creature-lawn-deploy`**, scheduled in the backlog-clean-up **lawn plan** (planned once, there) | D6: at most **5 unique creatures per side** on the lawn (10 total). A structural concurrency limit in tuning, reconciled with the Zomboss own-unit cap (`ZombossDeployPolicy`) and the contract capacity rule (`ContractPolicy.Capacity`) into **one admission rule** |
| `docs/architecture/lawn-tuning-profile/spec-lawn-combat-baseline.md` | **backlog-clean-up BCU2.3** (`orphan-plan-authoring`), executed in this run | `lawn-tuning-profile`, via the lawn plan | Register the shipped `BattleBaselineSubsystem` on the lawn Hub through `mode-profile`, so lawn actors stop sitting at a 0.5 hit coin-flip |
| `docs/architecture/lawn-tuning-profile/spec-zombie-power-source.md` | **backlog-clean-up BCU2.3**, executed in this run | `lawn-tuning-profile`, via the lawn plan | Narrowed to wiring: lawn zombies read Zomboss's empire allocation and Θ via `ZombossCommanderAllocation` instead of the player's (M5) |

combat-ai lists these only as prerequisites. It never plans or builds them itself.

## 2. Dependency direction and build order

```
W1  core-scorer ─┬─► profile-schema ─► ai-tiers-personality
                 ├─► intent-router ─► decision-perf
                 ├─► resolvable-here
                 └─► aggression-tier-map
W2  replay-identity · action-schedule-twin · decision-inspector
W3  stance-wiring · siege-loadout-wiring · delve-automated-wiring ─► auto-policy-switch (last in W3)
W4  lawn-actor-view · lawn-held-actions ─► lawn-cost-authority ─► lawn-cast-activation ─► lawn-cast-trigger ─► commander-direct-orders
```

**Hard edges:**
- `auto-policy-switch` lands only after `replay-identity` and `action-schedule-twin` (H1: one cause).
- `core-scorer`'s siege migration is byte-identical.
- A tuning publish lands with its reader (H7).
- Wave 4 needs the backlog-clean-up **lawn plan's** `lawn-perf-budget.v1` first, and `lawn-signal-ownership`
  (BCU0.1) recorded.
- The unique deploy cap lands before `lawn-cast-trigger` ships default-on.

**Parallel:** waves 1–2 are Core-only. Waves 3 and 4 touch disjoint files and can run in parallel once
wave 1 lands.

## 3. Out of scope

- Difficulty (its own future sub-program, D2).
- Vanilla PvZ unit control (deferred, D6).
- Player-editable AI (D4: inspect only).
- Combo-skill content (`RendezvousLane` proposer later).
- Strategic / world AI.
- Balance values.

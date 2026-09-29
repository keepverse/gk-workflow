# Lane S1 — the battle decision core (the candidate shared core)

## Summary (≤12 lines)
There is **one seam, not one engine**: `IIntentSource.TryDeclare(actorKey, nowTick) -> ActionIntent`
(`Core/Battle/Timeline/IntentSource.cs:29-37`). Five concrete policies plug into it —
`StubIntentSource` (nearest-enemy, preference-ordered, the shared default), `SiegeAiIntentSource`
(real weighted scoring), `InteractiveIntentSource` (player input, wraps a fallback), `RaidIntentSource`
(delve router: steered vs automated), `SiegeIntentSource` (played-side vs AI-side router) — plus a
replay/trace source. `BattleEngine`/`BattleRunState` never construct an AI; the one selection point is
`intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)` (`BasicAttack.cs:163-165`,
`TimelineDispatch.cs:79-80` — **PRE-FIX line numbers, and a superseded expression**: `CAI1.10`/`CAI1.11`
replaced both sites with `IntentRouter.Compose(policy: …, fallback: …)`, `BasicAttack.cs:175-179`). **`battle-engine-ssot.md` §3c carries an owner ruling (2026-09-16) that
explicitly retracts "forked AI is a defect"**: deciding lives outside the deterministic engine by design,
so per-mode policies are correct, not duplication. Lawn has **zero** production callers of
`IIntentSource` — the lawn-combat-ai-ideal.md's premise ("only the basic attack rider spends a resource")
is confirmed in code, not just asserted.

## Inventory
| Piece | Bucket | Evidence (file:line, verbatim quote) | Notes for a shared core |
|---|---|---|---|
| `IIntentSource`/`ActionIntent` | Built | `IntentSource.cs:29` `public interface IIntentSource { ActionIntent TryDeclare(...); }` | This is the seam a lawn AI plugs into — zero-allocation struct return already proven at scale (36 callers) |
| `StubIntentSource` | Built | `StubIntentSource.cs:27-75`, used by battle (fallback), delve (`automated` arg), siege fallback | Bounded-reads (held-action count), preference-ordered, gated stance→bound→cooldown→afford→range→condition via `UsabilityEvaluator`. This is the v1 the lawn ideal names verbatim |
| `SiegeAiIntentSource` | Built | `SiegeAiIntentSource.cs:83-138`; weights loaded from `gk-core/data/tuning/siege.v1.json` `"ai": {...}` | The only mode with a real **utility/score** notion today (see below) — a working precedent, siege-only |
| `InteractiveIntentSource` | Built | `InteractiveIntentSource.cs:30-154`; records `DecisionTrace`, supports replay/resume (`ResumeReplayThenLive`) | Player-input pattern: wraps a fallback `IIntentSource`, records what actually happened so replay never re-asks |
| `RaidIntentSource` | Built, then superseded | `RaidIntentSource.cs:29-51` (deleted by combat-ai CAI1.10, `c284f5f6d`; the same shape is now `Actions/IntentRouter.cs`); `_steeredKeys.Contains(actorKey) ? _steered : _automated` | Delve's per-actor router — the shape a lawn "player arm pre-empts AI" rule (ideal §4.4) would copy |
| `SiegeIntentSource` | Built, then superseded | `SiegeAi.cs:220-239` (pre-CAI1.1 — that dispatch wrapper no longer exists; the scorer is `Actions/Ai/CandidateScorer.cs` and `SiegeAi.cs` is 75 lines today); `PlayedSide is not null && _playedSideKeys.Contains(actorKey) ? PlayedSide : _aiSide` | Same router shape as `RaidIntentSource`, independently written — a real duplication candidate for a shared "manual pre-empts AI" router |
| `UsabilityEvaluator` | Built | `UsabilityEvaluator.cs:15-84`; six gates: stance→bound→cooldown→afford→range→condition, short-circuiting, allocation-free (`FactReader.Reads` stays 0 on early refusal) | Shared by `StubIntentSource` AND `SiegeAiIntentSource` verbatim — this, not `IIntentSource` itself, is the actual shared "can I legally do this" core today |
| `ActionTagPreference` | Built | `ActionTagPreference.cs:16-60`; `Compare`: tag rank → `Rung` DESC → `action_id` ordinal | The one static "preference/utility" ordering that already exists and is shared (comment names `BattleRunState`'s held-action sort AND `SiegeAiIntentSource`'s own use) |
| `CooldownLedger` | Built | `CooldownLedger.cs:29-106`; absolute-tick, never paused, "an absolute tick has nothing to go stale" | Ticks are the sim clock's, mode-agnostic; the lawn's `KernelDriveHost`/100ms tick base would need its own instance, same class |
| `CombatProfile`/`CombatProfiles` | Built (narrower than the name suggests) | `Combat/CombatProfiles.cs:9-16`; `MinChipShareKPm` only — `Overlay=0`, `BattleSim=50` | **Not an AI/decision profile.** It is a damage-floor knob for `OverlayCombatCalculator`. Do not conflate with "per-mode AI profile" — no such registry exists |
| `FrozenActionSet` | Built | `Grants/FrozenActionSet.cs:18-46`; assembled once at run start, frozen until `RefreshAtNextRunStart` | Answers "what can this actor even choose from" — mode-agnostic, already the T24 seam `StubIntentSource`'s docs cite for "sort once, not per decision" |
| `BattleSessionRegistry`/`DecisionTrace` | Built | `DecisionTrace.cs:38`; 39 callers incl. `BattleSessionRegistry.cs`, `InteractiveIntentSource.cs`, `DelveBattleSessionManager.cs` | Records `(tick, actorKey, actionId, targetKey, DecisionSource)` — the byte-identical-replay backbone; a lawn AI producing intents through this seam gets replay for free if ever wired through it |
| Lawn: any `IIntentSource` wiring | **Real gap** | `Grep "IIntentSource\|StubIntentSource\|ActionIntent"` over `gk-fusion/src/FusionRpg.Injector/**` → **0 files**. Only `LawnBasicAttackCostCharger`/`LawnBasicAttackCostGate` exist for the lawn's one spender | No wiring gap to point at — the mechanism itself was never built for the lawn. `lawn-combat-ai-ideal.md` §3 says this correctly |
| Per-mode "AI weight" tunables | Built (siege only) | `gk-core/data/tuning/siege.v1.json:104-117` `weightHitChance:70, weightObjective:50, weightKill:15, weightLowHp:10, weightCannotCounter:10, weightRound:1, weightRisk:120, ...` | Only siege has a tuning file for AI scoring; `ai.v2.json` is the **world/frontier** AI (`FrontierRulesPolicy`/`ThreatMap`/`ValueMap`), a different subsystem entirely — do not conflate the two "ai.*"/"*.ai" tuning families when scoping a lawn one (`lawn-combat-ai.v1.json` per the ideal doc does not exist yet — confirmed, `gk-core/data/tuning/` has no lawn-ai file) |

## How decisions are made today in this mode (trigger, who decides, what inputs, what executes)
- **Trigger:** every time `DeclareBasicAttack`/`Reselect` runs during round resolution (`BasicAttack.cs`,
  `TimelineDispatch.cs`) — i.e. per actor per round/commitment, not per frame. This is a **pull** model:
  the engine asks "what do you want to do" at the moment it needs an intent, it does not run AI on a
  fixed cadence of its own.
- **Who decides:** whichever `IIntentSource` was wired for that battle — resolved once via
  `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)`. `DefaultAiIntentSource` is
  set exactly once, at `BattleRunState` construction, only `if (aiTuning != null)` (siege opt-in);
  every other mode falls through to a fresh `StubIntentSource` built from that call's own `view`.
- **What inputs:** `IBattleView` (board/roster facts, fog-aware via `FoggedBattleView`), `CooldownLedger`,
  `IStanceCheck`, `IAffordabilityCheck`/`CostLedger` — never a raw `BattleEngine` actor list.
- **What executes:** the returned `ActionIntent` (ActionId, TargetKey, Envelope) is handed straight into
  the existing resolution path (`ApplyBasicAttack` → `OverlayCombatCalculator`/atom effects) — deciding
  and resolving are architecturally separated per `battle-engine-ssot.md` §3c.

## Per-mode constraints a shared core must respect (timing, determinism/seeds, perf, fog, goldens)
- **Determinism:** `TryDeclare` implementations shown here are pure functions of `(actorKey, nowTick, view state)`
  — no RNG read inside `StubIntentSource`/`SiegeAiIntentSource`/`RaidIntentSource`. Battle-wide seeded
  streams (`SeededRng.DeriveStream(seed, "crit")`, `"essence"`, `"riders"`, `"capture"`) are declared in
  `BattleRunState.cs:281-292`, none named for AI decisions — decisions are deterministic by construction,
  not by drawing from a dedicated AI stream. A lawn core must keep this: no unseeded randomness in the
  decision itself.
- **Replay/goldens:** `InteractiveIntentSource` + `DecisionTrace` is the actual golden mechanism —
  "replays byte-identical to an uninterrupted run" is asserted by name in tests
  (`ResumeReplayThenLive`, `A_steered_fights_decision_log_replays_and_resumes_byte_identical...`). No
  test pins *what* the AI decides (no "AI always picks X" golden) — only that a recorded decision replays
  identically. This matches the repo's own guardrail rule (never assert generated/derived content, only
  the contract).
- **Fog:** `FoggedBattleView` wraps `IBattleView` and nulls out `PositionOf`/`FactsOf`/etc. for anything
  outside `_viewerSide`'s vision — an AI reading through `IBattleView` gets fog for free; one not
  reading through it (a lawn core reading Unity/injector state directly) would not.
- **Perf:** `StubIntentSource`'s own doc: "reads are bounded by the actor's own held-action count," and
  action ordering is sorted once (`FrozenActionSet`) not per decision — the lawn ideal's "zero
  allocations per decision" bar is the same bar this module already holds itself to.
- **Owner ruling constraint (battle-engine-ssot.md §3c, "Retracted: what was D13"):** a shared core must
  not be read as "the lawn/siege/delve should all call one policy class." The correct target is "one seam,
  several policies" — exactly today's shape. Proposing to collapse `StubIntentSource`/`SiegeAiIntentSource`
  into a single class would be re-litigating an explicitly retracted finding.

## Cross-mode reuse candidates (what this mode already shares / could share)
- **Already shared today:** `IIntentSource` seam, `UsabilityEvaluator`'s six gates, `CooldownLedger`,
  `IStanceCheck`/`IAffordabilityCheck`, `ActionTagPreference.Compare`, `FrozenActionSet`, `IBattleView`/
  `FoggedBattleView`, `DecisionTrace`.
- **Real (not wiring-gap) duplication worth naming:** `RaidIntentSource` (delve) and `SiegeIntentSource`
  (siege) independently implement the identical "steered-keys route to player source, else automated"
  router — same 4-line shape, two classes. A shared `RoutedIntentSource(steered, automated, steeredKeys)`
  in `Core/Actions/` (not `Delve/` or `Siege/`) would be a legitimate small dedup, and is exactly the
  shape a lawn "player arm pre-empts AI" feature (ideal §4.4) needs a third time — a natural third
  consumer, not a new invention.
- **Only siege has a real scoring/utility AI** (`SiegeAiIntentSource` + `AiTuning` weights). If a lawn
  core wants "utility scoring, not just nearest-enemy" later (the ideal's §4.3 extension list explicitly
  defers this past v1), `SiegeAiIntentSource`'s weight-vector shape (`weightHitChance`, `weightKill`,
  `weightLowHp`, `weightRisk`, ... all published via `gk-core/data/tuning/siege.v1.json`) is the one existing
  precedent to extend rather than re-invent — but the ideal doc is explicit that v1 reuses
  `StubIntentSource` unchanged, deferring scoring.
- **Two separate "ai" tuning families exist and must not be conflated:** `gk-core/data/tuning/siege.v1.json`'s
  `ai.*` (combat-decision weights, per-battle) vs `gk-core/data/tuning/ai.v2.json` (`frontierRules`/`threatMap`/
  `valueMap` — world/strategic AI, a different subsystem, `spec-ai-commander.md`). A new
  `lawn-combat-ai.v1.json` is a third, sibling file, not an extension of either. (That file was never created —
  the program took the sibling-rejection branch instead: the lawn keys belong in `data/tuning/combat-ai.v*.json`.)

Files: `gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs`, `gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs`,
`gk-core/src/FusionRpg.Core/Actions/UsabilityEvaluator.cs`, `gk-core/src/FusionRpg.Core/Actions/IBattleView.cs`,
`gk-core/src/FusionRpg.Core/Actions/FoggedBattleView.cs`, `gk-core/src/FusionRpg.Core/Actions/ActionTagPreference.cs`,
`gk-core/src/FusionRpg.Core/Actions/IAffordabilityCheck.cs`, `gk-core/src/FusionRpg.Core/Actions/Grants/FrozenActionSet.cs`,
`gk-core/src/FusionRpg.Core/Battle/Timeline/CooldownLedger.cs`, `gk-core/src/FusionRpg.Core/Battle/Timeline/InteractiveIntentSource.cs`,
`gk-core/src/FusionRpg.Core/Battle/Timeline/DecisionTrace.cs`, `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs`,
`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs`, `src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs` (deleted by combat-ai CAI1.10, `c284f5f6d`),
`gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs`, `gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs`,
`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`, `gk-core/src/FusionRpg.Core/Combat/CombatProfiles.cs`,
`gk-core/data/tuning/siege.v1.json`, `gk-core/data/tuning/ai.v2.json`, `docs/architecture/battle-engine-ssot.md` (§3c),
`docs/architecture/lawn-combat-ai-ideal.md`.

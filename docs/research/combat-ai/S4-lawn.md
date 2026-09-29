# Lane S4 — The lawn runtime a lawn AI would plug into

## Summary (≤12 lines)
The lawn's basic-attack rider (kill-switch, cost-charge, grant-bind) is fully **Built** and is the
only RPG-driven action executing on the lawn today. The generic action-decision stack
(`IIntentSource`/`StubIntentSource`/`ActionCatalog`/`FrozenActionSet`/`IBattleView`/
`BoardSnapshotAdapter`) is **fully built and tested for Battle/Siege/Delve** but has **zero
production callers anywhere under `FusionRpg.Injector`** — confirmed by grep, not inferred. There is
no per-actor held-action registry on the lawn, no lawn implementation of `IBattleView`, and no
injector caller of `ActionRunner`/`FrozenActionSet`/`ActionCatalog` beyond the single hardcoded
basic-attack `CompiledAction`. `ExhaustionPolicy` is never instantiated anywhere in `src/` production
code (Battle or lawn) — only in tests. `KernelDriveHost`/`TimelineDrive` is a real, ticking, tightly
perf-budgeted per-board lawn clock already carrying DoT/shield-upkeep/resource-tick kinds — the
natural timer-trigger host. `EventDrain` already counts swings per ptr internally
(`SwingBump`/`Append`), so a swing-count trigger has a real, already-paid-for hook. The Zomboss lawn
AI (`ZombossDeployPolicy`, `ZombossPatternSelector`) is a **deploy/build-pattern AI**, never a
per-swing combat-casting AI — it decides *what to spawn* and *which aptitude posture to re-pattern
into*, not *what action to cast this swing*. GameHooks' Harmony patches on PvZ's own
`ZombieAttackPlant`/melee methods are the only "FSM" surface — they emit `combat.hit` into the event
pipeline; there is no exposed plant/zombie attack-state object to query.

## Inventory
| Piece | Bucket | Evidence (file:line, verbatim quote ≤1 line) | Notes for a shared core |
|---|---|---|---|
| `LawnBasicAttackFeature` kill switch | Built | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs:56` `public const bool DefaultEnabled = true;` | Exact kill-switch shape (const default + env override + debug override) the ideal doc says a lawn AI should copy |
| `LawnBasicAttackCostCharger` (charges via shared `CostLedger`) | Built | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackCostCharger.cs:61` `static long NowTick() => KernelDriveHost.NowTicks / 100;` | Proves the lawn already reuses the SAME `CostLedger`/rung authority as battle — no second cost engine (guard-actor-hub compliant) |
| `LawnBasicAttackGrantBinder` (per-actor grant bind, Θ-rebind on dirty) | Built | `gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs:203` `static bool Bind(string ptr)` | Record-then-drain pattern (`MarkThetaDirty`/`RebindAllBound`, lines 90-99) is the established "cheap main-thread drain of a socket-thread flag" shape a decision-trigger flag could reuse |
| `LawnBasicAttackRow` (the ONE compiled action the lawn knows) | Built | `gk-fusion/src/FusionRpg.Injector/Actions/LawnBasicAttackRow.cs:31` `public static CompiledAction? TryGet()` | This is the injector's *entire* `CompiledAction` surface — see gap row below |
| `EffectRuntime.OnDrained` / `OnCapture` (trigger → plan → sink) | Built | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:359` `public static void OnDrained(EffectEventDto ev)` | This is the execution tail an AI-chosen action would ride — **no new write path needed** once an intent maps to an effect grant |
| `EventDrain` per-ptr swing counting | Built | `gk-core/src/FusionRpg.Core/Events/EventDrain.cs:211` `SwingBump(rec, +1);` (inside `Append`) | The "swing count" trigger the ideal doc wants is arithmetic on a counter that is already maintained — zero new detection cost, confirmed in code not just claimed |
| `KernelDriveHost`/`TimelineDrive` per-board lawn clock | Built | `gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:54-56` `const double BudgetFrameFraction = 0.01;` / `BudgetMinSeconds = 0.00005` / `BudgetMaxSeconds = 0.00015` | Real, already-ticking, already perf-budgeted per-board clock (drives `KindDotPulse`/`KindShieldUpkeep`/`KindResourceTick`) — natural timer-trigger host, no new clock to build |
| `IIntentSource`/`ActionIntent`/`StubIntentSource` (generic AI decision) | **Wiring gap** | grep `StubIntentSource` under `gk-fusion/src/FusionRpg.Injector/`: **zero matches** (only `gk-core/src/FusionRpg.Core/**` and `FusionRpg.Server/RpgHub.cs`) | Fully built, allocation-free, unit-tested (`StubIntentSource.cs:27-97`) for Battle/Siege/Delve/Interactive. Never instantiated in the injector. This is exactly the "extend `StubIntentSource` unchanged" v1 the ideal doc proposes — the class is ready, the caller is missing |
| `IBattleView` (board/actor read seam `StubIntentSource` needs) | **Wiring gap** | Only implementers found: `BattleRunState.cs:40`, `FoggedBattleView.cs:31`, `BloodthirstyView` (`BasicAttack.cs:489` — PRE-FIX: `CAI1.11` moved it to the router's `BloodthirstyDecorator`), and test `FakeBattleView` — **no injector/lawn implementation exists** | A lawn `IBattleView` adapter over live Unity plants/zombies is unbuilt. This is the single missing piece that unblocks `StubIntentSource` on the lawn |
| `BoardSnapshotAdapter.ToCombatSnapshot` | **Wiring gap** | Only 2 call sites, both in `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:405` and `:1202` — none in the injector | Confirms it is **not fed on the lawn today**, contra a casual reading of the ideal doc's table; it is Battle-only plumbing shaped like a lawn census but never pointed at one |
| `FrozenActionSet` / `ActionCatalog` / held-action registry on the lawn | **Real gap** | grep `FrozenActionSet` and `ActionCatalog` under `gk-fusion/src/FusionRpg.Injector/*.cs`: **zero matches**; grep `HeldAction\|heldActions\|LoadoutRuntime\|EquippedAction` under injector: **zero matches** | No lawn Plant/Zombie ptr is ever associated with a compiled action list at runtime. This is bigger than "wire the existing feed" — the feed itself (species/loadout → per-actor held actions, on the lawn) does not exist. The ideal doc's own §6 names this as a content dependency on the action-corpus run, consistent with this finding |
| `ActionRunner` (turn-based action execution in Core) | **Real gap for lawn** | Callers of `ActionRunner`: only `BasicAttack.cs`, `TimelineDispatch.cs`, `ReactionLane.cs`, `ReadinessDriver.cs`, `RendezvousLane.cs`, `TurnReadiness.cs`, `BattleModeProfile.cs` — no injector caller | Turn/slot-based dispatch does not fit the lawn's continuous-time model anyway; a lawn AI would go intent → effect-grant directly, bypassing `ActionRunner`, matching the ideal doc's §4.1 "the injector only adapts... effect bag → Funnel → EntityStatWriter" |
| `ExhaustionPolicy` | **Real gap (production, both modes)** | `grep -rn "new ExhaustionPolicy" src/` → **no output** (only `gk-core/tests/FusionRpg.Core.Tests/Actions/ExhaustionPolicyTests.cs` instantiates it); `DerivedStatRegistry.cs:239` comment: `"ExhaustionPolicy.cs:59 reads ResourceRegen(resourceId) GENERICALLY... No reader consumes max/regen for hunger/qi/spirit/stamina"` | Confirms the ideal doc's own claim: no production path anywhere (not just the lawn) currently produces a real exhaustion edge. A lawn combat AI would be the first production caller |
| PvZ lawn FSM hooks (`GameHooks`) | Built (as an event source, not a queryable FSM) | `gk-fusion/src/FusionRpg.Injector/GameHooks.cs:1351` `public static class ZombieAttackPlant` ; `:1245`/`:1345`/`:1680`/`:1718` `Emit("combat.hit", payload);` | These are Harmony prefix/postfix patches on PvZ's own attack methods that **emit** into the event pipeline — there is no exposed "attack state" object to poll. A lawn AI monitors via `EventDrain`/`EffectRuntime.OnDrained`, not via a PvZ FSM read |
| Zomboss lawn AI (`ZombossDeployPolicy`, `ZombossPatternSelector`) | Built, but **wrong shape** — deploy/build AI, not combat-cast AI | `gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployPolicy.cs:41-58` scores *whether/which creature to spawn* off `ILawnBoardView`; `gk-core/src/FusionRpg.Core/Battle/Ai/ZombossPatternSelector.cs:1-27` picks an aptitude *posture pattern* on level-up/win-streak, rate-limited by `repatternCooldownEncounters` | Answers the brief's explicit question directly: this is a **deploy AI + a periodic build-pattern AI**, never a per-swing action-casting AI. It shares nothing with "cast a held action this decision tick" and is not reusable machinery for that job beyond the general "deterministic scorer + `SeededRng.DeriveStream`" idiom |
| Perf accounting (`PerfSection`) | Built infrastructure, **no lawn-AI section yet** | `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41`: 25 sections (`LoopTick`…`LawnMoveDrain`), no `lawn.ai.decide` member | Confirms the ideal doc's §5 claim that `lawn.ai.decide` "does not exist yet" — adding it is a small, precedented change (`LawnMoveDrain` at index 24 is the most recent addition, same pattern to follow) |

## How decisions are made today in this mode (trigger, who decides, what inputs, what executes)
Today there is exactly one decision on the lawn: "did this event carry a basic-attack rider." The
trigger is `EffectRuntime.OnCapture`/`OnDrained` firing on every drained combat event (no separate
decision step — `LawnBasicAttackCostCharger.ShouldApplyRider(ev)` gates a fixed, hardcoded behavior).
Nothing chooses *among* actions because nothing but the basic attack exists at runtime. Execution is:
Unity attack method (Harmony-patched in `GameHooks`) → `combat.hit`/damage event → `EventDrain` →
`EffectRuntime.OnDrained` → `EffectBag.OnEvent` plan → `InjectorEffectActionSink.Execute` → Funnel →
`EntityStatWriter`. There is no `IIntentSource.TryDeclare` call anywhere in this path.

## Per-mode constraints a shared core must respect (timing, determinism/seeds, perf, fog, goldens)
- **Timing:** Hot-path only, injector in-process, on the Unity main thread inside the frame budget —
  `overlay-control-loops.md` §3 (per BRIEF); `KernelDriveHost`'s own clamp (`0.05ms`–`0.15ms` per
  board, `BudgetFrameFraction = 0.01`) is the concrete number a decision loop must fit beside.
- **Determinism/seeds:** The lawn has no replay/golden-trace requirement like `InteractiveIntentSource`'s
  `DecisionTrace` — Zomboss AI already threads `SeededRng.DeriveStream(matchSeed, "...")` for its rolls
  (`ZombossDeployPolicy.cs`), the convention a lawn AI's own "which action" tie-break should reuse if
  any randomness is needed; the basic-attack path itself has none.
- **Perf:** Zero-allocation-once-warm is the acceptance line `StubIntentSource` and `TimelineDrive`
  both already carry; a lawn AI must add its own `PerfSection` entry (26th) and prove a measured share
  the way `LawnBasicAttackFeature`'s own doc comment does (28.06%→3.46% of wall, `_baseline-lcw-300z-*`
  files) before shipping default-on.
- **Fog:** Not applicable — the PvZ lawn has no fog-of-war; `FoggedBattleView` is Battle/Siege-only and
  would not be composed in.
- **Goldens:** No lawn combat goldens exist to protect (this mode has no replay contract); the risk is
  entirely on the Core side — reusing `StubIntentSource`/`IIntentSource` read-only from a new lawn
  adapter cannot move a single Battle/Siege/Delve golden as long as no existing implementation or call
  site is touched.

## Cross-mode reuse candidates
- `IIntentSource`/`ActionIntent`/`StubIntentSource` — mode-agnostic already (4+ implementations across
  Battle/Siege/Delve/Interactive); the lawn needs only a new `IBattleView` adapter, not a new interface.
- `CooldownLedger`, `IStanceCheck`, `IAffordabilityCheck` — reusable as-is, no lawn-specific variant needed.
- `CostLedger`/`LawnBasicAttackCostGate` — the lawn already proves the "one authority, not a second
  composer" discipline; a non-basic action would charge through the same ledger.
- `KernelDriveHost`/`TimelineDrive` — reusable directly as the timer-trigger host (no new clock).
- `EventDrain`'s per-ptr swing counters — reusable directly as the swing-count trigger (no new
  detection cost).
- `EffectBag.OnEvent` → `InjectorEffectActionSink.Execute` → Funnel → `EntityStatWriter` — the single
  execution tail every mode's chosen action already rides; an AI-chosen intent needs no new write path.

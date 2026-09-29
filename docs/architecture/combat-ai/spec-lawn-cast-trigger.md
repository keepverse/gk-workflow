# Spec: `lawn-cast-trigger` (combat-ai module 19)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `lawn-actor-view` (module 15), `lawn-cast-activation` (module 18); reads the tuning file
`profile-schema` (module 2) creates and the budget share the lawn plan's `lawn-perf-budget` creates ·
**Unblocks:** `commander-direct-orders` (module 20) · **Status:** **built (Core `CAI4.7`, Injector `CAI4.8`, 2026-09-23).** `gk-core/src/FusionRpg.Core/Match/Ai/{LawnDecisionTrigger,LawnDecisionBudget,LawnCastTokenPool}.cs` are in — the two OR'd triggers, the carry clamp, the lock that does not freeze the counter, the seeded offset, the FIFO budget and the leasing pool — with 33 tests at `tests/FusionRpg.Core.Balance.Tests/CombatAi/`. **The three halves this line used to call owed have landed, and the two files it called absent exist:** `PerfSection.LawnAiDecide` (`CAI-perf-1` — `AiDecide` 25, `LawnAiDecide` 26, `SectionCount` 27, pinned by `PerfProbeTests`); the Injector frame slot and its registry drops (`CAI4.8`, `Injector/Effects/LawnDecisionHost.cs`), **including its `board.start` edge** (`MatchHost` → `LawnDecisionHost.BeginMatch(MatchSeed.For(matchKey))`, with the tuning parsed once at `RpgHost.Initialize`); and the lawn tuning keys, which live in **`gk-core/data/tuning/combat-ai.v2.json`** (`CombatAiTuningFiles.Current`) now that `CAI-F1` closed the H7 blocker. The budget share lives in **`gk-core/data/tuning/lawn-perf-budget.v2.json`** (`LawnPerfBudgetFiles.Current`), where `ceiling.sections.lawn.ai.decide` is **declared and unmeasured** (`null`) — a gate reading it must treat `null` as "cannot pass yet", never as a satisfied gate. **One thing is still owed, and it is not this module's:** the slot's DECISION step is a seam, because module 16's held sets need an `ActionCatalog` the injector has no feed for (`CAI4.3`'s payload decision). See `tasks/reports/CAI4.7.md` and `tasks/reports/CAI4.8-start-edge.md`.

## Objective

**Nothing on the lawn ever asks for a decision.** There is exactly one decision on the lawn today —
*"did this event carry a basic-attack rider"* — and it is not a choice between anything
(`../research/combat-ai/S4-lawn.md:43-49`). This module is the **loop**: it decides *when* to ask, for
whom, how often, and at what cost, and hands the answer to module 18.

The owner's shape is *"trigger actions from the basic attack count and a timer, so a simple AI spends
resources while they are available… keep the performance impact small"*
(`../lawn-combat-ai-ideal.md:13-18`). Prior art makes that shape concrete and gives it its edge cases:
casting from a counter that basic attacks fill is the genre default (TFT 10/7/5 mana per attack, Dota
Auto Chess ≈10 attacks, Idle Heroes +50 at 100), TFT locks mana gain about one second after a cast and
since Set 12 carries overflow **up to one cast** — before that, reset-to-zero made extra mana *"actively
detrimental"* (`../combat-ai-ideal.md:171-180`). The named failure modes are spam, hoarding, sync
spikes and oscillation (`:213-220`); the answers are waste guards, a reserve floor, a seeded offset plus
a budget, and a distinguishing consideration.

Two corrections from the audit are load-bearing here and the design starts from them, not from the
ideal's first draft:

1. **There is no per-actor swing counter to reuse.** `EventDrain`'s `SwingBump` keys on
   `SwingKey(SwingPtr, ActorPtr, Frame)` and is a per-**swing** pending-record dedupe that is consumed
   and released (`gk-core/src/FusionRpg.Core/Events/EventDrain.cs:110-129,135-146`). *"It never accumulates a
   per-actor count across swings. The real hook is `IsFirstOfSwing`"*
   (`../research/combat-ai/AUDIT.md:29`). The counter must be built, **with die and ptr-reuse cleanup**.
2. **`lawn.ai.decide` did not exist.** `PerfSection` had 25 members ending at `LawnMoveDrain = 24`
   (`gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41`), and there was no token pool anywhere
   (`../combat-ai-ideal.md:151`). **Both have since landed:** `AiDecide = 25`, `LawnAiDecide = 26`,
   `SectionCount = 27` (`CAI-perf-1`, pinned by `PerfProbeTests`), and `LawnCastTokenPool` is in
   (`CAI4.7`).

## Tech stack

`FusionRpg.Core` (the whole trigger, budget and token machinery — pure, Unity-free, CI-built, because
CI never builds the injector: `gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:10-14`),
`FusionRpg.Injector` (the frame slot, the swing feed, the kill switch, the cleanup hook). No new
dependency and **no new clock** — `../research/combat-ai/S4-lawn.md:76` is explicit that
`KernelDriveHost`/`TimelineDrive` is *"reusable directly as the timer-trigger host (no new clock)"*.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LawnDecisionTrigger|FullyQualifiedName~LawnDecisionBudget|FullyQualifiedName~LawnCastTokens|FullyQualifiedName~PerfSection"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session backlog-clean-up-20260920
python gk-core/scripts/guard-actor-hub.py ; python gk-fusion/scripts/guard-single-writer.py ; python gk-fusion/scripts/guard-funnel-delta.py
python gk-core/tools/tuning/publish.py combat-ai --label "lawn trigger seed values" lawn.trigger.swingsPerDecision=7
python gk-core/scripts/probe_perf.py --scenario lcw-300z --duration-sec 60      # the A/B, AI on vs off
```

⚠️ `publish.py` *"refuses to invent a key by design"* (`gk-core/tools/tuning/publish.py:22-23`). It writes
`v{n+1}` of an **existing** domain (`:10-11`). `gk-core/data/tuning/combat-ai.v1.json` **was published by CAI1.8** (2026-09-20) — `profile-schema`, module 2, is the module that created it. **Corrected 2026-09-23 (lane `cai3`):** the lawn section is in **`gk-core/data/tuning/combat-ai.v2.json`** (`CombatAiTuningFiles.Current`), published by `CAI4.7` with `CAI-F1` closing the H7 blocker — the revision this sentence called owed has landed. See Open question 1.

## Project structure

| File | New / changed | One line |
|---|---|---|
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnDecisionTrigger.cs` | **landed (CAI4.7)** | Per-actor swing counter, timer, lock, carry, seeded offset — pure |
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnDecisionBudget.cs` | **landed (CAI4.7)** | Per-frame budget with FIFO overflow carry |
| `gk-core/src/FusionRpg.Core/Match/Ai/LawnCastTokenPool.cs` | **landed (CAI4.7)** | Leased tokens with idempotent release and a timeout backstop |
| `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | **landed (CAI-perf-1)** | `AiDecide = 25`, `LawnAiDecide = 26`, `SectionCount = 27`, `"ai.decide"` and `"lawn.ai.decide"` in `SectionNames` |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnCombatAiFeature.cs` | **landed (CAI4.8)** | Kill switch, the `LawnBasicAttackFeature` shape exactly (`:46-72`) |
| `gk-fusion/src/FusionRpg.Injector/Effects/LawnDecisionHost.cs` | **landed (CAI4.8)** | The frame slot: due set → view → policy → module 18 |
| `gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs` | changed | One more tick call beside `LawnBasicAttackGrantBinder.Tick` (`:101`) |
| `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` | **NOT changed — measured 2026-09-23 (lane `cai3`)** | The drained-record swing feed this row called for is **not there**: `grep -rn "RecordSwing" src/` finds only the two definitions (`LawnDecisionTrigger.cs:143`, `LawnDecisionHost.cs:190`) and one internal call (`LawnDecisionHost.cs:199`) — no production caller. Filed as `CAI-find-5`. The feed needs `EffectEventDto.CastOrigin`, which is `CAI4.6`'s Contracts field, because the design forbids INFERRING a cast from a trigger name (the rule `AiDecisionOrigin` already follows) |
| `gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs` | changed | Drop per-actor AI state and release tokens in `Remove` (`:129-146`) / `Clear` (`:148-157`) |
| `gk-core/data/tuning/combat-ai.v2.json` | **landed (CAI4.7 + `CAI-F1`)**; `CombatAiTuningFiles.Current` | The lawn section's four keys: `N`, `T`, `L` and the offset stream name. The four structural values are code `const`s, not rows (§Tunables) |
| `tests/FusionRpg.Core.Balance.Tests/CombatAi/{LawnDecisionTrigger,LawnDecisionBudget,LawnCastTokenPool}Tests.cs` | **landed (CAI4.7)** | Every rule below, each with a planted violation |

## The shape

### 1. The two triggers, OR'd

A decision runs **only on a trigger edge** — never per frame, never per zombie
(`../combat-ai-ideal.md:232-233`).

| Trigger | Mechanic | Cost |
|---|---|---|
| **Swing count** | the actor's `N`-th first-of-swing record | one integer increment on a record already being drained |
| **Timer** | `T` lawn ticks since this actor's last decision | one comparison, only when a frame slot already runs |

Per-actor state is five fields and no allocation once warm:

```csharp
struct LawnActorTriggerState
{
    public int  Swings;         // first-of-swing records since the last DECISION
    public long NextTimerTick;  // lawn ticks
    public long LockUntilTick;  // lawn ticks
    public bool Pending;        // the carry: at most ONE held cast, never a count
    public int  Offset;         // seeded, applied once at registration
}
```

### 2. The swing feed, and what must not feed it

The counter increments from the **already-resolved** `IsFirstOfSwing` flag on the drained DTO
(`gk-core/src/FusionRpg.Contracts/EffectDtos.cs:226`, stamped at `gk-core/src/FusionRpg.Core/Events/EventDrain.cs:631`)
— *"exactly one of the N records sharing one `SwingId` reads true"*. The feed sits in
`EffectRuntime.OnDrained` (`gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:359`), beside the charge
gate that already reads the same flag (`:368`), so the detection costs nothing new — which is the one
claim the audit's C1 correction left standing (`../research/combat-ai/AUDIT.md:29`: the detection
exists; the count does not).

**Three records must not increment it:**

- a record with `IsFirstOfSwing == false` (the other victims of one swing);
- a record with `CastOrigin == true` — module 18's discriminator. A cast that manufactures its own next
  trigger is a feedback loop (`../combat-ai-ideal.md:148`);
- any record for a ptr the registry no longer knows.

### 3. Hold at N, and a carry capped at one cast

When `Swings >= N`, the actor is **due**. If the decision is then refused — nothing usable, no token, or
the frame budget is spent — the actor **holds at N**: `Pending` is set, the counter is not reset, and it
is clamped so surplus cannot accumulate without bound.

On a committed cast:

```csharp
// Carry-over capped at ONE cast (TFT Set 12; before that, reset-to-0 made extra swings
// "actively detrimental" -- combat-ai-ideal.md:175-177). `Pending` is a bool, not a count:
// a bounded ratio of a structural quantity, never a progression ceiling.
//
// CLAMP, not Min, and the floor at 0 is load-bearing: a cast can commit BELOW N swings when an
// ORDER drives it (commander-direct-orders, module 20 -- an order is a top-rank candidate that
// fires as soon as the gates pass, whatever the swing count). `Math.Min(Swings - n, n)` would then
// go NEGATIVE and silently delay the actor's next natural cast by up to 2N swings, which reads in
// play as "my creature stopped casting after I ordered it". Found by module 20's review of this
// expression; fixed here, in the module that owns the line.
state.Swings = Math.Clamp(state.Swings - n, 0, n);
state.Pending = false;
```

Reset-to-zero is the alternative and is rejected by the same prior art. A counter that grows without a
clamp is the hoarding failure (`../combat-ai-ideal.md:218`) inverted — a creature that was blocked for
twenty swings would then fire five casts in five frames.

**The two bounds are different guards and both are needed.** The upper bound `n` is the anti-burst
rule above; the lower bound `0` is the anti-*stall* rule an order-driven cast makes reachable. Test 4a
(§Testing strategy) plants the violation directly: restoring `Math.Min` makes an order-driven cast at
`Swings = 2, N = 7` leave `Swings = -5`, and the actor's next natural cast arrives twelve swings later
instead of five.

### 4. The post-cast lock `L`, and what it does *not* freeze

After a cast, `LockUntilTick = now + L`. While locked, **neither** trigger produces an edge.

**The swing counter keeps accumulating during the lock.** TFT locks mana *gain*
(`../combat-ai-ideal.md:182`) and this deliberately does not, because the owner's shape is *"every N
basic attacks"* (`../lawn-combat-ai-ideal.md:14-15`): freezing the counter would make `L` a second,
hidden multiplier on the cadence, so `N = 7, L = 10` would silently mean something other than seven
swings. Decided by principle, stated here, and listed in Open questions with its alternative — it is a
behaviour switch, not a tunable, so it is not smuggled into the tuning file as one.

### 5. The seeded per-actor offset

Sync spikes — *"everyone casts on the same frame"* — are a named failure
(`../combat-ai-ideal.md:219`). Each actor gets a bounded offset at registration:

```csharp
// SeededRng.DeriveStream (gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26), never System.Random --
// the same convention ZombossDeployPolicy already threads for its lawn rolls
// (gk-core/src/FusionRpg.Core/Match/Ai/ZombossDeployPolicy.cs:75).
var roll = SeededRng.DeriveStream(matchSeed, $"lawn.ai.offset:{actorKey}");
state.Offset      = (int)(roll.NextPerMille() * n / 1000);      // 0..N-1 swings
state.NextTimerTick = nowTick + (roll.NextPerMille() * t / 1000);  // 0..T-1 ticks
```

Same `(matchSeed, actorKey)` gives the same offset every run, which is what makes the trigger testable
at all. It also matches the ideal's determinism rule — randomness comes only from
`SeededRng.DeriveStream`, never from a clock (`../combat-ai-map.md:22-23`).

### 6. The clock — and a genuine disagreement with the map, reported rather than hidden

The map row says the timer runs on `AdvancedEffectClock` (`../combat-ai-map.md:74`, citing D15). Reading
the code, that is the wrong number to use, and this is worth stating plainly:

| Candidate | What it is | Why / why not |
|---|---|---|
| `AdvancedEffectClock` | `DateTimeOffset`, **seeded from the wall clock** at `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs:42` and wired as `Bag.UtcNow` at `:133` | It is the **status-expiry** time source D15 fixed (`battle-engine-ssot.md:242`). It is a wall-clock-shaped value, not a tick counter, and a cadence expressed in it would not be the unit `N`/`T`/`L` are counted in |
| `KernelDriveHost.NowTicks / 100` | Simulated ms since board start / 100 = **one lawn tick**, pause-respecting (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:107,174-176`) | **This one.** It is the exact expression `LawnBasicAttackCostCharger.NowTick` already uses (`:61`) and the `nowTick` the lawn `CostLedger` and `CooldownLedger` are built on (`:106`) |

**The decision: `T` and `L` read `KernelDriveHost.NowTicks / 100`.** A decision consults the cooldown
ledger and the cost ledger in the same breath; a trigger on a different base would recreate D15 — *"one
board, two notions of when"* (`battle-engine-ssot.md:242`) — one field along. Both values are advanced
by the same frame delta on the same 100 ms grid (`EffectRuntime.cs:35-38`;
`KernelDriveHost.cs:60-66`), so this honours D15's ruling that *the engine's module owns when a pulse
happens*; it differs only on which of the engine's two exposed values to read. **Flagged for the plan as
a map-row correction, not silently diverged from** — see Open question 2.

### 7. The per-frame decision budget, with overflow carried

```csharp
/// <summary>Structural per-frame cap. tunables-ssot.md §1 lists per-frame caps as exempt from the
/// "no magic numbers" rule AND requires saying so -- the same wording KernelDriveHost.cs:45-48 uses
/// for its own budget. It caps WORK PER FRAME, never a magnitude and never progression.</summary>
```

Due actors beyond the budget stay due and are served next frame — the overflow carry the lawn ideal asks
for (`../lawn-combat-ai-ideal.md:80-82`). The due set is a **FIFO queue ordered by (due tick, ordinal
ptr)**, not a scan in board order: an ordinal-only order starves high-address ptrs forever, which is the
kind of bug that only shows up at 300 zombies. Nobody waits more than `ceil(due / budget)` frames, and
test 7 asserts exactly that.

### 8. The cast-token pool

A lease, not a mutex — and the spec says so rather than implying long-running casts:

- Module 18's cast is **instantaneous** at the Funnel (build → runner → bag → flush, one call), so the
  pool's real job is to bound **casts per window across all actors**, independently of the per-frame
  *decision* budget. A decision that finds nothing usable costs no token; a decision that casts does.
- A token is released on **completion, actor death, interrupt, and timeout**. The documented failure is
  *a token never released* (`../combat-ai-ideal.md:210`, Doom 2016), so the **timeout is the backstop,
  not the mechanism**: it reclaims a lease whose holder never reported, including one module 18 dropped
  on a refusal path it failed to report.
- Release is **idempotent**. A double release is a no-op, never a negative count.
- The pool survives the shape module 20 (`commander-direct-orders`) and any future channelled cast will
  need, which is why it is a pool rather than a counter.

### 9. Death and ptr reuse

`overlay-control-loops.md:151` (Hot rule 4) and the ideal's extension of it — *"This covers any
per-actor AI state"* (`../combat-ai-ideal.md:81`).

Both the trigger state and any held token are dropped in
`InjectorEntityRegistry.Remove(ptr)`
(`gk-fusion/src/FusionRpg.Injector/Effects/InjectorEntityRegistry.cs:129-159`), beside the shield flush
(`:132-139`) and the resource-pool drop (`:143-145`), whose own comment is the reason: *"a reused ptr
must not inherit a stranger's drained pool"* (`:143-144`). `Clear()` (`:148-157`) drops everything at
the board edge. Every death path funnels through those two methods, which is why a new die hook would be
both redundant and easier to miss.

### 10. `PerfSection lawn.ai.decide`, and where the budget is *not*

`PerfSection` gains member 25, `SectionCount` goes 25 → 26, and `SectionNames` gains
`"lawn.ai.decide"` — the same three-line change `LawnMoveDrain = 24` made
(`gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:40,51,79`). `SectionCount`'s own comment already requires
the match (`:50`), so the count is a **closed vocabulary the code owns** and the pin moves with the
declaration, which is the one case `validation-ssot.md` allows a literal.

The decision tick runs in **its own `InjectorLoop.Tick` slot** beside
`LawnBasicAttackGrantBinder.Tick` (`gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs:101`), each call wrapped
`try { … } catch { }` like every neighbour there (`:93-115`).

⚠️ **It is not inside `KernelDriveHost`'s 0.05–0.15 ms.** That budget is the kernel's own share
(`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:54-56`: `BudgetFrameFraction = 0.01`,
`BudgetMinSeconds = 0.00005`, `BudgetMaxSeconds = 0.00015`) and the ideal requires the decision loop to
have its own (`../combat-ai-ideal.md:389-390`). The share lives in
`gk-core/data/tuning/lawn-perf-budget.v2.json` (`LawnPerfBudgetFiles.Current`) — it is the lawn plan's own
first task (`../combat-ai-ideal.md:437`), which this module depends on and does not author. **Landed
2026-09-23 (`CAI4.8`):** `ceiling.sections.lawn.ai.decide` is present and **declared unmeasured**
(`null`); the number itself is `CAI5.1`'s live A/B.

### 11. The kill switch, and shipping default-off

Exactly `LawnBasicAttackFeature`'s three-part shape
(`gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs:46-72`), for the reason that file documents
at length (`:31-44`): a production flag must not borrow its default from `CheatState`, whose own
contract never promised one.

```csharp
public const string CheatToggleId = "LAWN-COMBAT-AI";
public const string EnvVar = "FUSIONRPG_LAWN_COMBAT_AI";
/// <summary>FALSE until the 300-zombie A/B passes -- combat-ai-ideal.md:391 ("Ships default-on only
/// after a 300-zombie A/B, AI on vs off"). This is the same release condition LawnBasicAttackFeature
/// shipped under and later cleared (its own note, :9-22: 28.06% of wall at 19.8 fps, then 3.46% at
/// 59.7 fps after three fixes).</summary>
public const bool DefaultEnabled = false;
public static bool Enabled => !EnvForcedOff && (EnvForcedOn || (DebugOverride ?? DefaultEnabled));
```

Env is read **once at process start** (`LawnBasicAttackFeature.cs:58-61`), because the gate sits on the
spawn/die path. The switch turning **off** mid-match must take the live state with it — the L-N8 shape:
`FeatureSwitchEdge.TurnedOff` (`gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs:61,141-142`)
→ drop every per-actor state and release every token. Otherwise a half-armed AI keeps holding tokens
nothing will ever release.

**The A/B this ships behind** is `lawn-scale-live-proof`'s (`../lawn-combat-ai-ideal.md:100-102`), run
with `gk-core/scripts/probe_perf.py` against the `_baseline-lcw-300z-*` family the basic-attack feature already
used. This spec states the release condition; it claims no measurement.

## Tunables

`gk-core/data/tuning/combat-ai.v2.json` (**published by `CAI4.7` + `CAI-F1`**; `CombatAiTuningFiles.Current`), lawn section — the file module 2 created (`../combat-ai-ideal.md:436`). Every value is principle- or prior-art-derived and marked for tuning;
none is an owner decision (`../combat-ai-ideal.md:466-467`).

**The classification is decided per key, by the repo's own test**
([tunables-ssot.md](../tunables-ssot.md); `CLAUDE.md` "Magic numbers"): *would a balance pass ever want
to change this number?* → tunable. *Does changing it break whether the system **works**, rather than how
it **feels**?* → structural, and it stays a code `const` **with a comment saying why**. The earlier
draft of this spec put four numbers in the tuning file and labelled three of them "Structural", which
is the one combination the rule forbids — a value on the balance surface is editable by a balance pass
by construction, whatever a table calls it. Four keys are therefore **removed from the tuning file**
below and the reason is given for each.

**Tunable — these three are in `gk-core/data/tuning/combat-ai.v2.json`, lawn section:**

| Key | Unit | Seed | Why this seed, and why it is a balance number |
|---|---|---|---|
| `lawn.trigger.swingsPerDecision` (`N`) | swings | **7** | Prior art clusters at 7–10 attacks per cast: TFT gives 10/7/5 mana per attack at 100 mana, Dota Auto Chess ≈10, Idle Heroes 2 (`../combat-ai-ideal.md:172-177`). 7 is the middle of TFT's role band. **Balance:** cadence is the feel of the whole feature, and it is the first number a tuning pass will move. Nothing breaks at 5 or at 12. |
| `lawn.trigger.ticksPerDecision` (`T`) | lawn ticks (100 ms) | **50** (5 s) | The OR'd floor for an actor that is not swinging (a support, a blocked plant). Slower than the swing path at any normal attack rate, so it never becomes the dominant cadence. **Balance:** same reason as `N`, for the non-swinging half. |
| `lawn.trigger.postCastLockTicks` (`L`) | lawn ticks | **10** (1 s) | TFT locks mana gain *"about 1 s after a cast"* (`../combat-ai-ideal.md:182`), expressed on the lawn's own 100 ms grid. **Balance:** a pacing value; 0 and 30 both work, they just feel different. |
| `lawn.trigger.offsetStream` | — | `"lawn.ai.offset"` | Not a number: the `SeededRng.DeriveStream` stream name, pinned so an offset is reproducible. It sits in tuning for the same reason module 2's `.selection.rngStreamName` does — a stream name is data a file owns, and moving it would re-roll every actor's offset. |

**Structural — these four are code `const`s in `LawnDecisionTrigger.cs` / `LawnDecisionBudget.cs` /
`LawnCastTokenPool.cs`, each carrying the comment the no-hard-ceiling rule requires:**

| Constant | Value | Why it is NOT a balance number |
|---|---|---|
| `CarryCasts` | **1** | It is the **shape of the carry rule**, not a magnitude: `0` is TFT's pre-Set-12 reset-to-zero, `1` is Set 12, `≥2` is the burst this module exists to prevent. §4 and Open question 3 already rule the reset-to-zero alternative *"a behaviour switch, not a tunable"* — carry is the same switch from the other side, and leaving it on the balance surface lets a balance pass flip a behaviour the spec says needs a design decision. It is also the bound **test 4 asserts**, and a number a contract test pins is a declaration, not a reading (`validation-ssot.md`). |
| `DecisionsPerFrame` | **8** | A **per-frame work cap**, the class `tunables-ssot.md` §1 exempts *and* requires to say so — the identical treatment `KernelDriveHost`'s own budget constants get (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:45-48,54-56`), which this spec already cites as its model. Changing it does not change how the game feels; it changes whether the frame holds. **The machine-varying half is already in tuning and stays there:** `lawn.ai.decide`'s *share of the frame* lives in `gk-core/data/tuning/lawn-perf-budget.v2.json` (`ceiling.sections.lawn.ai.decide`, **declared and unmeasured**), authored by the lawn plan, measured by the 300-zombie A/B. A count of decisions and a share of a frame are different quantities; the measured one is in a **perf** domain, not on the balance surface. |
| `CastTokens` | **4** | A **concurrency lease count** bounding casts per window across all actors — the same per-frame/runtime-cap exempt class. AC Unity ran 40 real AIs in a crowd of ~10,000 (`../combat-ai-ideal.md:208`); the lawn's smart-tier population is capped at 10 by D6, so four is generous, not tight. Raising it does not make the game more fun, it makes the worst frame worse. |
| `CastTokenTimeoutTicks` | **20** (2 s) | **Labelled at last** — the review found it the only one of the four carrying no class at all. It is the never-released **backstop** (`../combat-ai-ideal.md:210`, Doom 2016), and it is structural in the strictest sense: set too short it reclaims a legitimate cast's lease and the system is *wrong*, not differently balanced. A balance pass has no reason to touch a leak guard. Long enough that a legitimate cast never trips it; short enough that a leak self-heals in two seconds. |

**Consequence for module 2's schema, carried out rather than left implied.** `AiTriggerBlock`
([spec-profile-schema.md](spec-profile-schema.md) §2) originally reserved `PerFrameBudget` and
`TokenPool` fields for this module. Those two fields are **dropped** from that record in the same
wave — a schema field for a value that lives in code is exactly the dead-config shape the ideal §8
forbids. `AiTriggerBlock` keeps `SwingsN`, `TicksT` and `PostCastLockL`, which are the three rows
above.

## Numeric types

- `Swings`, `Offset`, budgets and token counts are `int`: structural counts with proven small bounds
  (`Swings` is clamped at `2N`, the budget and pool are per-frame/per-window caps). Each says so in a
  comment.
- `NextTimerTick`/`LockUntilTick` are `long` lawn ticks, matching `KernelDriveHost.NowTicks`'s own
  `long` (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:107`).
- The offset multiply widens before dividing and divides last — `roll.NextPerMille() * n / 1000` in
  `int` cannot overflow because `NextPerMille() <= 1000` and `n` is a small structural bound; state the
  bound in the comment rather than relying on it silently (`CLAUDE.md` numeric rules 2 and 5).
- No magnitude is computed here, so `audit-overflow.py` should report no new finding. Run it and say so
  either way.

## Code style

- Record-then-drain: the swing feed is one increment on the drain thread's own record; everything else
  happens in the frame slot (`LawnBasicAttackGrantBinder.cs:10-19` documents why).
- Zero allocation once warm — the acceptance line `StubIntentSource` and `TimelineDrive` both carry
  (`../research/combat-ai/S4-lawn.md:59-60`). Struct state in a pre-sized dictionary; indexed `for`
  over any `IReadOnlyList<T>` (`gk-core/src/FusionRpg.Core/Actions/StubIntentSource.cs:61-63`).
- `try { … } catch { }` per tick call in `InjectorLoop`, exactly like its neighbours (`:93-115`) — a
  throwing decision must never kill the frame.
- Every structural constant carries a comment saying why it is structural.
- Logic in Core; the injector holds the slot, the switch and the feed only.

## Testing strategy

All Core, in memory, over a fake clock and a fake policy. No game, no disk
(`docs/contributing/testing-standard.md`).

| # | Test | Asserts the contract |
|---|---|---|
| 1 | Exactly `N` first-of-swing records produce exactly one edge; `N-1` produce none | The swing trigger |
| 2 | A record with `IsFirstOfSwing == false`, one with `CastOrigin == true`, and one for an unknown ptr each increment nothing. **Planted violation:** removing the `CastOrigin` check makes a cast retrigger itself | §2's three refusals, feedback loop included |
| 3 | A refused decision at `N` leaves the actor due; the next frame serves it with no further swings | Hold at N |
| 4 | `3N` swings accumulated during a lock produce **one** cast when the lock lifts, not three. **Planted violation:** raising `CarryCasts` to 2 fails | Carry capped at one cast (upper bound) |
| 4a | A cast committed at `Swings = 2` with `N = 7` (the order-driven case) leaves `Swings == 0`, and the actor's next natural edge arrives after exactly `N` further swings. **Planted violation:** `Math.Min(Swings - n, n)` leaves `-5` and the next edge arrives after `2N - 2` | Carry **lower** bound — the anti-stall half, and the one an order makes reachable |
| 5 | No edge inside `L`; an edge at `L+1`; the counter **did** advance during the lock | §4, including the accumulate decision |
| 6 | The same `(matchSeed, actorKey)` yields the same offset across runs; two different keys differ | Determinism, and the sync-spike answer. Reproducibility is the assertion — not a source scan for `System.Random` |
| 7 | With `B` due and budget `b < B`, exactly `b` decide this frame, the rest next, in FIFO order, and no actor waits more than `ceil(B/b)` frames | Budget + overflow carry + no starvation |
| 8 | A token taken and never released is reclaimed at the timeout; release is idempotent; a second release does not go negative | The Doom-2016 failure, both halves |
| 9 | Death releases the token and drops the state; a **reused ptr address** starts at zero swings and no lock | Hot rule 4, asserted directly |
| 10 | The switch turning off mid-match drops every state and releases every token | The L-N8 edge |
| 11 | `PerfSection` has 26 members and `SectionCount == 26` | A closed vocabulary the code owns, with the reason stated in the test (`PerfProbe.cs:50`) |
| 12 | A throwing policy is caught at the tick boundary and the next frame still ticks | Fail-closed frame slot |

**Never asserted:** how many actors decided in a real match, fps, wall-clock share, or any
`_baseline-*` number. Those are **readings** and belong to the A/B report
(`validation-ssot.md`; `../combat-ai-map.md:33`).

**Goldens: byte-identical.** No battle, siege or delve path is touched; the lawn has no golden contract
(`../research/combat-ai/S4-lawn.md:67-68`). `PerfProbe` is diagnostics and appears in no report hash.
Verify rather than assume:
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` and state the
result either way.

## Boundaries

- **Always:** decide on an edge only; read `KernelDriveHost.NowTicks / 100` for `T` and `L`; seed the
  offset from `SeededRng.DeriveStream`; carry budget overflow FIFO; release a token on every exit path
  including the timeout; drop state and tokens in `InjectorEntityRegistry.Remove`/`Clear`; ship
  default-off until the A/B.
- **Ask first:** turning `DefaultEnabled` to `true` (that is the A/B's result, and the owner's call —
  `LawnBasicAttackFeature.cs:51-56` is the precedent for how that decision was made and recorded);
  freezing the swing counter during the lock (Open question 3); raising the decision budget above what
  the measured share supports.
- **Never:** decide per frame or per zombie; await anything (`overlay-control-loops.md:150`, Hot rule 3);
  throw out of the tick; count a cast-origin record; introduce a third lawn time base; put the decision
  budget inside `KernelDriveHost`'s 0.05–0.15 ms; use `System.Random`; assert a measured share in a
  unit test; **move `CarryCasts`, `DecisionsPerFrame`, `CastTokens` or `CastTokenTimeoutTicks` onto the
  balance surface** — a value in `gk-core/data/tuning/**` is editable by a balance pass whatever comment sits
  beside it (§Tunables); **use `Math.Min` for the carry** — the floor at 0 is what stops an
  order-driven cast stalling the actor (§3).

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Responsibility 12, *the unified virtual clock — initiative, turn order
   and scheduling* (`battle-engine-ssot.md:149`), on the **deciding** side of it. The register is closed
   and nothing is added: this is a scheduler built *above* the engine's clock, which §2 explicitly
   allows (*"A mode's scheduler is built ABOVE the battle engine, not beside it"*, `:83-84`).
2. **Decide or resolve (§3c)?** Neither, precisely: it decides **when to ask**. Everything it produces
   enters the engine through `IIntentSource.TryDeclare` (`battle-engine-ssot.md:173`) by way of module
   18. It resolves nothing.
3. **Mechanism or loop?** **Loop**, and this is the one module in the lane where that matters:
   *"a turn-based delve and a real-time lawn cannot share a scheduler"* (`battle-engine-ssot.md:64`).
   The ideal states the same split — *"A mode owns its loop, never a mechanism"*
   (`../combat-ai-ideal.md:65-66`).
4. **Which existing implementation does it extend?** `KernelDriveHost`'s tick
   (`gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs:166-181`) and `InjectorLoop.Tick`'s existing
   record-then-drain slot (`gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs:93-101`). **No new clock** is
   built (`../research/combat-ai/S4-lawn.md:76`).
5. **Does every mode get it?** **No, and the reason is the split above.** Battle, delve and siege pull a
   decision per turn or round from the engine (`../combat-ai-ideal.md:231`); a real-time trigger has no
   meaning there. §5 Q5 says to expect a "lawn-only" answer to be refused — this one survives because it
   is a *loop*, the one thing §2 permits to be mode-specific, and because every *mechanism* it invokes
   (view, held set, cost, activation) is shared.
6. **Is it deterministic and seeded?** The offset is `SeededRng.DeriveStream`
   (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`), never `System.Random`; the cadence reads the engine's
   pause-respecting simulated clock, never the wall clock. It is reproducible in test (test 6) and, like
   the rest of the lawn, **not replayable in a live match** — the lawn is the non-deterministic driver
   (`battle-engine-ssot.md:106-111`) and has no replay contract
   (`../research/combat-ai/S4-lawn.md:55-58`). Stated, not overclaimed.

## Success criteria

1. A lawn creature with a kit casts on its `N`-th swing or after `T` ticks, whichever comes first, and
   not otherwise.
2. A blocked creature holds at `N` and casts once when unblocked — never a burst. A cast that commits
   **below** `N` (an order, module 20) leaves the counter at `0`, never negative, and the actor's next
   natural edge is exactly `N` swings later (test 4a).
3. `gk-core/data/tuning/combat-ai.v1.json`'s lawn section holds exactly the four **balance** keys; the four
   structural values are code `const`s carrying the comment `tunables-ssot.md` §1 requires, and
   `AiTriggerBlock` (module 2's record) has three fields, not five.
4. No edge inside `L`; a seeded offset makes two identical creatures cast on different frames.
5. With more due actors than budget, every actor is served within `ceil(due/budget)` frames and none is
   starved.
6. A token is never permanently lost: death, interrupt, refusal and timeout each release.
7. Death and ptr reuse leave no stale counter, lock or token.
8. `lawn.ai.decide` reports its own section, outside `KernelDriveHost`'s budget, with a share read from
   `lawn-perf-budget.v2` (`LawnPerfBudgetFiles.Current`).
9. The feature ships **default-off**; flipping it is a separate, owner-facing change carrying the
   300-zombie A/B numbers.
10. No golden moves; the suite is run and the result stated.

## Open questions

1. **Where do the lawn trigger keys live if module 2 has not landed?** `publish.py` cannot create a new
   domain file (`gk-core/tools/tuning/publish.py:22-23`), and `gk-core/data/tuning/combat-ai.v1.json` does not exist.
   Options: (a) module 2 authors `combat-ai.v1.json` **including** the lawn section's four keys, and
   this module is purely its reader — the H7 same-commit rule then applies to module 2's publish
   (`../combat-ai-map.md:104`); (b) this module authors its own `lawn-combat-ai.v1.json` — **never created**, the
   program took (a) — as the superseded lawn ideal proposed (`../lawn-combat-ai-ideal.md:62`).
   **Recommended default: (a)** — the combat-ai ideal explicitly puts the lawn section in
   `combat-ai.v1.json` (`../combat-ai-ideal.md:436`), and two AI tuning files is the fork the program
   exists to avoid.
   **ANSWERED 2026-09-22 (lane `cai4`):** **option (a) taken, and module 2 has since landed** - `gk-core/data/tuning/combat-ai.v1.json`
   was published by `CAI1.8` and both hosts read it. It carries **no lawn section**, so these four keys
   still await a `v{n+1}` revision, which **H7 blocks until `CAI-F1` lands** (both readers name the v1
   file by hand). The other half of this question's precondition is still unmet too:
   `gk-core/data/tuning/lawn-perf-budget.v1.json` does not exist, and it is the lawn plan's `LW1.1`. So the four
   values arrive as constructor parameters today (`LawnDecisionTrigger`, `CAI4.7`).
   **CORRECTED 2026-09-23 (lane `cai3`): both preconditions are now met, so this answer's last two
   sentences are superseded.** `CAI-F1` closed the H7 blocker by landing `CombatAiTuningFiles.Current`
   and moving BOTH hosts onto it, and the four keys are in **`gk-core/data/tuning/combat-ai.v2.json`** — the
   publish was a pure addition (`profiles`/`router` byte-identical to v1's), and the keys have a reader
   (`CombatAiLawnTuning`, read back through the shipped parser by `CombatAiTuningRevisionTests`).
   `gk-core/data/tuning/lawn-perf-budget.v2.json` also exists and carries `ceiling.sections.lawn.ai.decide` as
   **declared and unmeasured**. So the values no longer arrive *only* as constructor parameters: they
   arrive from the file at `RpgHost.Initialize`, and the constructor parameters are what `CAI4.7`'s own
   tests pass.
2. **The map row names `AdvancedEffectClock`; this spec reads `KernelDriveHost.NowTicks / 100`.**
   §6 gives the reasoning and the lines. Options: (a) correct the map row to name the kernel tick;
   (b) expose a single lawn "now" accessor that both the ledger and the trigger read, and make *that*
   the D15 answer for the action stack. **Recommended default: (a) now, (b) as a named D15 follow-up** —
   (b) is genuinely better and genuinely outside this module, because it would move the cost ledger's
   clock too. **This is a real map/spec disagreement and it is reported, not absorbed.**
   **Owed upstream, not fixed by this spec's lane** (both files are outside it): the one-line edit is to
   **ANSWERED 2026-09-22 (lane `cai4`):** **completely landed upstream.** `docs/architecture/combat-ai-map.md:81` (row 19) now
   names `KernelDriveHost.NowTicks / 100` and carries the correction in its own words, and
   `docs/architecture/combat-ai-ideal.md:138` now reads *"scheduling reads `KernelDriveHost.NowTicks` /
   `SimulationClock`; `AdvancedEffectClock` ..."* for status expiry - both verified by reading the two
   files today. The named D15 follow-up (one lawn "now" accessor shared with the cost ledger) remains a
   follow-up, in this program's Deferred list.

   *(The original text below is kept as the record of the disagreement it reports.)* The owed edit was to
   `combat-ai-map.md` row 19 and to `combat-ai-ideal.md`'s two `AdvancedEffectClock` mentions (§4.1
   "Lawn clock host" and §6.1 "a timer on the lawn engine clock `AdvancedEffectClock`, D15"), replacing
   the name with `KernelDriveHost.NowTicks` / `SimulationClock` and citing §6's finding. DESIGN-GATE's
   propagation rule applies: a correction that lands in this spec and not in its sibling map **has not
   landed**, so whoever next touches those two files carries it. Worth adding at the same time: a
   "clock sources" row in `battle-engine-ssot.md` §4 D15 naming
   `SimulationClock`/`KernelDriveHost.NowTicks` (scheduling) against `AdvancedEffectClock`/wall clock
   (status expiry) explicitly — this is the second time in one program that the two have been confused
   in prose, which is the signal that the distinction is not yet obvious from the docs alone.
3. **Does the swing counter accumulate during the post-cast lock?** §4 decides **yes**, because freezing
   it makes `L` a hidden multiplier on `N`. TFT freezes the equivalent gain
   (`../combat-ai-ideal.md:182`), so the alternative has prior art behind it. It is a one-line behaviour
   switch either way and is deliberately **not** a tunable — a balance pass that wants the other
   behaviour is asking for a design change, not a number.
   **ANSWERED 2026-09-22 (lane `cai4`):** **answered by the landing: it accumulates.** `LawnDecisionTrigger` deliberately does
   not freeze the counter through the lock and says so in its own doc comment for exactly this reason -
   freezing it would make `L` a hidden second multiplier on the cadence. Pinned by
   `No_edge_inside_the_lock_an_edge_at_L_plus_one_and_the_counter_does_advance_through_it` and, at the
   policy level, by `CAI-loop-1`.
4. **Cross-module note (`creature-lawn-deploy`, D6):** the map's hard edge says *"The unique deploy cap
   lands before `lawn-cast-trigger` ships default-on"* (`../combat-ai-map.md:107`). The budget seeds
   above assume that cap (10 smart-tier actors on the board). If this module ever ships default-on
   without it, the decision budget is the only thing bounding smart-tier cost, and it was not sized for
   that. Named here so the plan sequences it.
5. **Cross-module note (module 15):** module 15's derived memo keys on `actor-liveness-refresh`'s
   revision, which is **spec, not built** (`../lawn-playable/spec-actor-liveness-refresh.md:5`). Until
   it lands the memo is frame-scoped only, which is correct for one decision. That is another reason
   default-off is the right shipping state, and it is a second precondition on the same flag.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: lawn AI loop, performance/PerfProbe, match/actor
    lifecycle, tunables.
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json).
[x] I read every doc in the §1 row(s) this session: overlay-control-loops.md (§3 and §6 in full),
    battle-engine-ssot.md (§2, §3c, §4 D15, §5 in full), combat-ai-ideal.md, combat-ai-map.md,
    AUDIT.md, S4-lawn.md, lawn-combat-ai-ideal.md, spec-actor-liveness-refresh.md, DESIGN-GATE §1/§5.
[x] I checked decisions.md for a lock: the "Battle engine is the SSOT" row (:53) covers the loop/
    mechanism split this module relies on; nothing locks a lawn trigger cadence.
[x] Every factual claim cites file:line, and every cited file was opened this session -- including
    PerfProbe's enum and SectionCount, KernelDriveHost's budget constants and pause guard,
    LawnBasicAttackFeature's three-part switch, EventDrain's SwingBump/IsFirstOfSwing,
    InjectorLoop's tick order, SeededRng.DeriveStream and publish.py's refusal to invent a key.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary run
    2026-09-20 over the whole program scope (22 documents, 1019 resolvable citations):
    0 HIGH findings. The remaining rows are D1 (a cited file that does not exist yet) on the
    paths this spec marks "(new; does not exist yet)", which the audit exempts because the *(2026-09-22:
    the three trigger files and their tests have since landed and `combat-ai.v1.json` is published; the
    marker now applies only to the Injector rows and the owed tuning revision)*
    line says so, plus 4 LOW D3 rows the audit reports rather than guesses. **Updated 2026-09-23
    (lane `cai3`): the Injector rows and the tuning revision have landed too, so this spec now marks
    NO path "(new; does not exist yet)" and its D1 rows are no longer covered by that exemption —
    the audit was re-run and reports 0 HIGH either way.**
[x] I verified claims against CODE, not comments. The clock decision in §6 is the clearest case: the
    map row's AdvancedEffectClock was checked in code (EffectRuntime.cs:42,133) and found to be a
    wall-clock-seeded DateTimeOffset, which is why this spec reads the kernel tick instead and reports
    the disagreement rather than following the doc.
[x] I read the surrounding section of every rule I quoted (control-loops §6 rules 1-7; tunables-ssot's
    per-frame-cap exemption as KernelDriveHost.cs:45-48 restates it; battle-engine-ssot §2's
    "scheduler above the engine" paragraph, not just its headline).
[~] I tested (not assumed) any constraint I am reporting. **Gap named honestly:** no suite, no build and
    no perf probe was run in this spec session. Every performance number quoted is a CITATION of an
    already-measured baseline (LawnBasicAttackFeature.cs:9-22), never a new claim, and the 300-zombie
    A/B is written as the release condition with the command to run it.
[x] Nothing contradicts a §2 invariant. Hot rules 1, 3 and 4 are each honoured and cited by line; the
    decision loop never awaits and never sits between combat.hit and FA* apply.
[x] Corrections propagated: Open question 2 records the map-row disagreement explicitly rather than
    silently diverging, and Open questions 1, 4 and 5 hand three sequencing facts to the plan.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. The one pinned literal (PerfSection's 26 members / SectionCount) is a closed vocabulary
    the code owns and PerfProbe.cs:50 already requires the match; the test states that reason.
[x] Event-refreshed cache (§2.16): the per-actor trigger state IS an event-refreshed cache, and every
    invalidator is listed -- a first-of-swing record (value), a committed cast (value + lock), the
    timer tick (value), the kill switch turning off (whole set), and the two KEY SET edges: a ptr
    entering (registration at bind) and a ptr leaving (InjectorEntityRegistry.Remove, and Clear at the
    board edge). Tests 1, 2, 4, 5, 9 and 10 cover them. The trigger set is derived from this cache's
    own key behaviour, not copied from another cache.
[x] No acceptance criterion silently fixes an ordering that can vary. The due-set order IS variable in
    real play, which is exactly why it is specified as FIFO by (due tick, ordinal ptr) and why test 7
    asserts a starvation bound rather than a fixed sequence.
[x] Produces no actor combat/derived magnitude. It consumes module 15's Hub-sourced snapshot through
    module 17's ledger only. No second composer, no private fold; BattleStatComposer is not cited as
    precedent.
[x] Does not invent or extend a SOLID-violating parallel path: it adds a mode LOOP, which §2 permits,
    and invokes only shared mechanisms. It explicitly refuses a new clock, a second tuning file and a
    second kill switch.
[~] A new rule has a registry row. **Gap named honestly:** two rules here want enforcement -- "the lawn
    reads exactly one time base" and "per-actor AI state is dropped before ptr reuse" -- and both are
    currently covered only by this module's tests (9, and §6's decision). Whether either earns a
    gk-core/scripts/enforcement-registry.v1.json row or a guard script is a plan decision, unresolved here.
```

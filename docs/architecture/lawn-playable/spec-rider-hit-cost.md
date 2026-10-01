# Spec: `rider-hit-cost` (lawn-playable module 3)

**Program:** [lawn-playable](../lawn-playable-map.md) · **Depends on:** `hub-snapshot-cache` ·
**Unblocks:** `rider-default-on`
**Status:** spec, 2026-09-16. Not built.

## Objective

Make the per-hit RPG path cheap enough, and the drain fast enough, that a 300-zombie wave is a game
rather than a slideshow.

Measured at 300z with the feature on, one ~4 s window
(`_baseline-lcw-300z-env-on-post-ln37.json`):

```
effect.onCapture     count 129    totalMs 543.6   maxMs 38.6   avgUs 4214.3
loop.tick            count 60     totalMs 3925.7  maxMs 1107.9 avgUs 65427.9
drain    pending 718   carried 5320   processed 48   maxLatencyFrames 47   maxRecordUs 39577
observer totalHits 879  droppedRecords 369
```

Three separate readings, three separate problems:

1. **4.2 ms average per capture** — after module 2 removes the 1.6 ms compose, whatever remains here is
   this module's target.
2. **The drain is 5320 records behind** and 47 frames late; 369 records were dropped by the observer in
   the same window. Work is arriving faster than it is consumed, so the queue is the bottleneck, not
   only the unit cost.
3. **`maxRecordUs 39577`** — a single record took 39 ms. One record can blow a frame on its own.

## Tech stack

`FusionRpg.Injector` (`EffectRuntime`, `EventDrainHost`, `InjectorBoardSnapshot`),
`FusionRpg.Core` (`EventDrain`). Existing `PerfProbe` sections are the instrument — this module adds no
new measurement vocabulary, it moves the numbers the existing one already reports.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~EventDrain|Coalesc"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~Funnel|SingleWriter"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
.\scripts\probe-perf.ps1 -Scenario lcw-300z-env-on-hitcost -DurationSec 60
```

## Project structure

| What | Where |
|---|---|
| Per-hit path | `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs` (`OnDrained`, `OnCapture`) |
| Queue behaviour | `gk-fusion/src/FusionRpg.Injector/Effects/EventDrainHost.cs`, `FusionRpg.Core/Events/EventDrain.cs` |
| Budgets | `data/tuning/lawn-drain.v1.json` (new) — see Tunables |
| Baseline | `docs/research/perf/_baseline-lcw-300z-env-on-hitcost.json` |

## The shape

**Measure first, then cut — in this order, each landing separately with its own window:**

1. **Re-measure after module 2.** The 4214 µs includes the 1624 µs compose. The remainder is the real
   target and it is not yet known. A module that starts cutting before this reading is guessing.
2. **The `maxRecordUs 39577` outlier before the average.** One 39 ms record is a worse player
   experience than a hundred 0.4 ms ones. Find what that record was (the drain already carries
   `expensiveDeferred` — it read 0, so nothing was deferred); give the expensive shape a name and defer
   it, or make it cheap.
3. **Then the queue.** `carried 5320` with `processed 48` per tick is a throughput mismatch, not a unit
   cost. The drain's per-tick budget is currently implicit; make it a **tunable budget** and let the
   drain finish a frame's worth of work in that frame.
4. **Only then the average**, with whatever is left.

## Tunables

`data/tuning/lawn-drain.v1.json`, published through `gk-core/tools/tuning/publish.py`, owner this spec:

| Key | Meaning | v1 |
|---|---|---|
| `perTick.recordBudget` | records a drain tick may process | current implicit value, stated |
| `perTick.microsecondBudget` | wall-clock budget per drain tick | `UNMEASURED` |
| `record.expensiveMicroseconds` | above this, a record is deferred rather than run inline | `UNMEASURED` |
| `queue.depthWarn` | depth at which the drain reports pressure | current implicit value |

These are budgets, not game feel — but they are exactly the numbers a tuning pass moves while watching a
frame graph, so they belong in data (`tunables-ssot.md`), and every one starts marked `UNMEASURED`.

## Testing strategy

- ✅ The drain honours its budget: given N records and a budget of M, exactly M are processed and the
  rest are carried, never dropped (a contract).
- ✅ Nothing is dropped except through the already-ruled per-death overload valve (D9's own counter is
  the proof, and the owner ruled the valve is expected).
- ✅ A deferred expensive record still lands — deferral never silently discards.
- ✅ Order is preserved per victim (attribution depends on it — the melee/ambient bracket work in
  `lawn-combat-wire` L-N39 relies on pairing).
- ❌ Never assert µs or a frame share in a unit test. Those are readings; `probe_perf.py` owns them.

## Boundaries

- **Always:** one change, one window, one committed baseline file — the L-N8 discipline (fresh process
  per arm, env set at start, same scenario) is what made the original measurement trustworthy and it is
  the only way these numbers are comparable.
- **Ask first:** nothing.
- **Never:** reduce cost by dropping records (that is a correctness change wearing a perf hat); move
  combat resolution off the RPG layer into a PvZ patch; re-litigate transport (the 2026-08 audit already
  measured that lag is per-hit main-thread work, not SignalR — do not rewrite it without new probe data).

## Numeric types

Budgets are counts and microseconds — `int`/`long`, no `P(Θ)`-scaled magnitude. The `maxRecordUs` style
readings stay `double` in telemetry.

## ActorHub gate

Consumes Hub output through module 2's cache. Adds no fold, no channel, no composer.

## Success criteria

1. A committed 300z baseline with the feature on shows `effect.onCapture` `avgUs` and `loop.tick`
   `avgUs` both materially below `_baseline-lcw-300z-env-on-post-ln37.json`, on the same scenario.
2. `drain.carried` returns to single digits at the end of a 60 s 300z run, and observer
   `droppedRecords` is 0 outside the ruled death valve.
3. `maxRecordUs` has a named cause and a budget that bounds it.
4. Every number above comes from a committed run file, not a summary.

## Open questions

None. The one unknown — what the per-hit cost is once the compose is cached — is step 1 of the module,
not a question for the owner.

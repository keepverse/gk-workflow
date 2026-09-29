# spec — `unified-clock`

**Module 14 of `solid-remediation`.** Register entry: **D15**. Depends on `battle-mode-parity`,
`battle-responsibility-guard`.

**The riskiest module.** It touches the injector's hot path, where the locked no-round-trip invariant
lives. It wants the guards, the mode parity and a green battle path behind it — which is why it is here
and not earlier.

## Objective

The engine's clock module owns **when a pulse happens** on every board, including the lawn. The wall clock
may only be what *feeds* it.

## The defect (D15)

> **The lawn runs two time bases at once.**

The engine's clock abstraction is shipped and correct, and the kernel drives the lawn's DoT and shield
upkeep as scheduled **100 ms** events — but the injector wires `EffectBag.UtcNow` to `SystemEffectClock`,
the raw wall clock. So **status timing reads wall time while DoT scheduling reads the kernel's event
queue**. One board, two notions of when.

`EffectRuntime.cs:58` · `EffectBag.cs:236-246` · `KernelDriveHost` 100 ms events · `SimulationClock.cs:16-27`

### Report this precisely — the wiring is deliberate

⚠️ The injector's wall-clock wiring is a **documented deliberate choice**, not an accident. `EffectBag`'s
own error text says a live host *"wires it to the real wall clock explicitly, on purpose, at its own
composition root."*

**The defect is not that choice.** It is that the choice was made for the **time source** and then silently
became the **scheduler** for one half of the tick vocabulary. Anyone who reads the wiring as a mistake
will "fix" it by deleting a decision that was correct, and break the thing the comment was protecting.

## The owner's ruling this implements

> *"Because we have many mode, they need engine build above battle engine to resolve time clock. But we
> need ship unify one, so whatever they change, the rule is only one… that mean damage deal by DoT will
> be calculate by battle engine timeclock module, same as status."*

And: the engine is **deterministic**. A deterministic engine whose schedule depends on wall time is a
contradiction — that is the sharpest statement of this defect.

The clock is a unified engine module with `ITimeAdvance` as the only per-mode part
(`NextEventAdvance` / `FixedIncrementAdvance`). The lawn is the mode that **cannot** control its own
clock, so it is the hard case, not the exception: the injector's capture feeds the engine's clock rather
than replacing it.

## Shape

**Share, not rebuild.** `SimulationClock` is shipped and correct.

1. **Status timing reads the engine's clock**, the same source DoT scheduling already reads.
2. **The wall clock keeps its role as the time *source*** for the lawn, feeding `ITimeAdvance` — it stops
   being the *scheduler*.
3. **One tick vocabulary.** A DoT pulse and a status expiry are computed in the same place, on every
   board.

## The hot-path constraint

The locked **no-round-trip** invariant on the injector's hot path is not negotiable in this module. If
unifying the clock would add a round trip per tick, the design is wrong — record it and re-plan rather
than paying for correctness in frame time.

Perf is part of this module's acceptance: `PerfProbe` sections are **inclusive**, and `vfx.tick` must stay
within its locked share of wall time at 300z.

## Numeric

Durations are integer milliseconds. Do not reintroduce fractional seconds — `green-baseline` fixed
exactly that defect in the atom generator, where `duration = ms / 1000.0` produced values the validator
refuses. Divide once, at the end; integer division truncates.

## Tests to rewrite

Any test asserting status expiry against wall time is pinning D15. Restate: expiry is computed from the
engine's clock, and is therefore **deterministic** — the same inputs produce the same expiry, which is a
property a wall-clock test cannot assert at all.

Determinism is the contract to assert. Run the same scenario twice and require identical results; that is
the assertion D15 makes possible and that currently cannot pass.

## Boundaries

- **Always:** keep the wall clock as the lawn's time *source*; preserve the documented composition-root choice
- **Ask first:** any change that adds a round trip to the injector hot path
- **Never:** a second scheduler, or a mode-local notion of "when"

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs gk-core/src/FusionRpg.Core/**/SimulationClock.cs <tests> -Session solid-remediation-<date>
```

- [ ] Status timing and DoT scheduling read one clock
- [ ] A scenario replays identically — determinism asserted, not assumed
- [ ] `vfx.tick` within budget at 300z, measured by `PerfProbe`
- [ ] No new round trip on the hot path
- [ ] The deliberate wall-clock-as-source choice is preserved and its comment updated to say which role it now plays

## Success criteria

One board, one notion of when. A deterministic engine actually is one.

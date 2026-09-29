# Trace: what unit `resource.regen.*` was fitted in, and what the runtime reads it as

**Program:** `lawn-tuning-profile` module 1 · **Task:** `LW2.1` ·
**Spec:** [spec-regen-unit-trace.md](spec-regen-unit-trace.md) · **Status:** answered 2026-09-23.
**Defect traced:** M3 (lane `lawn-tuning-profile-ideal.md`) — *"the numbers were chosen in different
units from the ones the game reads."*

This is a **trace**, not a balance change. Nothing shipped moves here; the republish the finding asks
for is named at the end and is a separate, measured change.

## 1. The runtime's unit: **units per tick** (tick = 100 ms)

| Fact | Site |
|---|---|
| The channel means units per tick, and the reader carries per-mille *of that unit* | `gk-core/src/FusionRpg.Core/Stats/Derived/ResourceChannelReader.cs` (`RegenPerMilleTick`, its own doc: *"resource.regen.{id} still means units per tick, so a composer writing 5 still means five per tick"*) |
| The single `/1000` back to whole units happens once, at the far end, and the sub-unit remainder is carried — never rounded per tick | `gk-core/src/FusionRpg.Core/Actions/Cost/ResourcePoolState.cs` (`Milli`, `Settle`: `accruedMilli = Carry + ratePerMilleTick * elapsed`, `whole = accruedMilli / 1000` last) |
| The baseline authors per second and divides by ten **once**, at the end | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:451-476` (`regenPerSecondUnits / (double)TicksPerSecond`) |
| `TicksPerSecond = 10`, 100 ms per tick — structural, with its own comment saying why it is not a tunable | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:478-482` |

The per-mille resolution was added *because* the unit is per tick (S10.1, `resource-subtick`): rounding
to a whole `long` per tick made `1/tick` the smallest expressible non-zero rate, which over a
~300-tick round accrued ~300 poise against a spend of 100. That work only makes sense if one tick is
the unit — it is the runtime's deliberate contract, and it is asserted by
`gk-core/tests/FusionRpg.Core.Tests/Actions/ResourceSubTickRegenTests.cs` (11 tests, `poise` only).

## 2. The POC's unit: **units per round**

| Fact | Site |
|---|---|
| Accrual multiplies the coefficient by the number of **rounds**, not ticks | `gk-core/tools/CombatSim/ActionEconomy.cs:123-127` — `public void Tick(double rounds = 1.0)` → `_value[id] = Clamp(_value[id] + _regen[id] * rounds, 0, _max[id])` |
| Its callers advance one round per iteration of a round loop | `gk-core/tools/CombatSim/Analytic.cs:567` (`pools.Tick()` inside `for (var r = 0; r < maxRounds; r++)`), `gk-core/tools/CombatSim/Simulator.cs` (`while (round < maxRounds …)`), both with `Tick()`'s default `rounds = 1.0` |
| The POC has no tick and no action duration in this path: a "round" is one exchange in its own loop, never a count of 100 ms ticks | same two loops (they predate `action-timing.v1.json`, added 2026-09-05) |
| The live coefficients still declare that provenance | `gk-core/data/tuning/aptitudes.v10.json` `_meta.status`: *"ported verbatim from gk-core/tools/CombatSim/tuning/aptitudes.v1.json, this program's own POC … That POC file is now frozen as a reference copy"* (72 `resource.regen.*` edges) |

⚠️ **Correction to the spec:** the spec (written 2026-09-16) cites `aptitudes.v8.json`; the live file
today is **v10**, and its status line still carries the verbatim-port declaration. Nothing between v8
and v10 re-expressed the regen edges in a tick unit (checked: 72 `resource.regen.*` edges present, same
`kMilli` shape).

## 3. Do they agree? **No — by the round/tick ratio**

A coefficient fitted so that it accrues `k` units over one POC round is read by the runtime as `k` units
over one tick. At a basic attack's own cadence that ratio is:

```
gk-core/data/tuning/action-timing.v1.json:  basicAttack.windupTicks = 150
                                    basicAttack.recoveryTicks = 50
one basic-attack round            = 200 ticks  ->  the runtime accrues 200x what the POC fit.
```

That is the same order as M2's measured symptom (a clean actor regenerating 0.2/tick; three aptitude
points taking it to 29.2/tick against a pool that grew with it): a per-round coefficient read per tick
is not a small error, it is a 200× one, and it is why an aptitude regen edge dwarfs the pool it refills.

The ratio is **cadence-dependent, not a universal constant**: a long action occupies more ticks per
round than a short one, and the POC's round is not a tick count at all. Any conversion must therefore be
stated against a named cadence — `action-timing.v1.json`'s per-action wind-up/recovery is that cadence
source, and the basic attack's 200 ticks is the one the tests pin.

## 4. Which number is wrong

**The runtime's per-tick unit is the intended one**, and the coefficients are the artifact that was
carried across a unit boundary:

- the runtime states its unit in its own doc comment, next to the number (`ResourceChannelReader`);
- the runtime invested in per-mille-per-tick resolution *because* per-tick is the unit (S10.1), so
  "per tick" is not an accident of an implementation detail;
- `BattleModels.BaseResourceRegen` authors per second and divides by ticks — two independent runtime
  seams agree;
- the POC's per-round accrual is what a discrete round-based simulator needs, and it never claimed to
  be a tick model.

So M3 is **not** closed as "no defect, the POC was the odd one out": the mismatch is real, and the
wrong end is the coefficient table that crossed from a per-round fit into a per-tick consumer.

## 5. What the finding asks for, and who owns it

The repair is a **balance change**: republish `resource.regen.*` as `aptitudes.v{n+1}.json` with the
per-round → per-tick conversion applied (or the coefficients re-fitted directly in the tick unit), then
re-measure. It is deliberately **not** in `LW2.1` (`no shipped behaviour changes yet`) and not in this
lane's fence (`data/tuning/lawn*.json` only; `aptitudes.v*.json` is the class-system program's domain).
`spec-regen-unit-trace.md`'s Boundaries are explicit: land it alone, measured, and say so in its own
commit — it moves **battle as well as lawn**, so a lawn-only scaling would leave battle reading the
wrong unit and hide the defect one layer down.

Routed to `tasks/lawn-todo.md` as `LW5.2` (routed **out**), so this program's dependent
`LW2.6 lawn-resource-scale` — which sizes the stamina pool against this rate — sees it.

## 6. What is asserted, and where

`gk-core/tests/FusionRpg.Core.Tests/Stats/ResourceRegenUnitTests.cs` (new):

- the unit contract over the **whole closed vocabulary** (`DerivedStatChannels.ResourceIds`, all six —
  the existing S10.1 tests cover `poise` alone);
- the per-mille round trip with the remainder carried across ticks, never truncated per tick;
- the reconciliation arithmetic: one basic-attack round is `windupTicks + recoveryTicks` **read from
  `action-timing.v1.json`**, and the runtime accrues exactly that multiple per round more than the POC's
  per-round `Tick()` does for the same coefficient — so the 200× cannot drift silently.

No test asserts a `kMilli`, a pool size, or a recovery window: those are readings a balance pass moves.

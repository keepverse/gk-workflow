# Spec: `essence-loop-read`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.2 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Umbrella invariant 7 (PS-5 scaled capacities): [../../trade-network-map.md](../../trade-network-map.md)
§5; umbrella contradiction X5. Power SSOT: [../../power/ssot-power-scale.md](../../power/ssot-power-scale.md)
§10.2 rows 22–23 and 37, §10.3, §10.4 (PS-5). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md)
§14b (*"the essence loop picks one read for faucet and sink before `sector-yield` sets any yield"*).

## Objective

Decide, before any yield number exists, **which scale each located good reads**, and make every
sector-yield number go through one function for it. Two rules bind:

- **PS-5** (`ssot-power-scale.md` §10.4): within one economy loop, faucet and sink scale on the same
  read, or neither does.
- **Umbrella invariant 7:** warehouse capacity reads the same scaled value as the goods it holds, or a
  flat capacity facing a scaling good is a hidden ceiling.

§10.4 decided that essence **must** scale (it is spent against `P(Θ)`-scaled content). Today both
halves of the essence loop are flat, which satisfies PS-5 but not §10.4 (umbrella X5). This module
carries §10.4 to both halves **in one change**, and records one §10 row for the located-goods read.

Success: `yield-structures` and `warehouse-axis` call one function for their scale; an essence yield
cannot ship while the fusion essence cost is flat; nothing moves at the calibration point.

## Scope and non-goals

**In scope:** the scale read; the per-family loop table; the essence sink's scale (cross-program, with
the creature program); the essence expedition faucet's scale; one §10.2 row.

**Not in scope:** any yield amount (`yield-structures`), any capacity amount (`warehouse-axis`), the
soul economy's own sinks (`SoulSinkPolicy`, creature program), crafting cost legs (materials program,
§10.2 row 37), loam (Θ-invariant by §10.4 — untouched).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| `ContentScale.Milli(Θc) = P(Θc)·1000 / pinValue`, `long`, `checked`; `Apply` rounds once | `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15-20`, `:31-40` |
| The pin: `pinIndex` 20, `pinValue` 680, so `Milli(20)` is exactly 1000 | `gk-core/data/tuning/power-scale.v2.json` (`curve` block) |
| A sector's content level: `MapLevel(dangerBand) = Wm·dangerBand`, `Wm` = 5 | `gk-core/src/FusionRpg.Core/Power/PowerIndexComposer.cs:97-104`; `gk-core/data/tuning/power-scale.v2.json` (`WmMilli` 5000); §10.3 row *mapLevel* |
| Two world readers already use exactly this pair | `gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:81`; `gk-core/src/FusionRpg.Core/World/Turn/SiegeLoot.cs:46` |
| The soul loop's pairing rule and its explicit pin placeholder | `gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:34` (`VanillaPvzTheta = 20`), `:40-41` (`Price`) |
| Essence expedition faucet: flat +1 per creature met | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:132-136` |
| Fusion essence cost: flat `int` from tuning, spent as-is | `gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs:5`, `:7`; `gk-core/src/FusionRpg.Core/Creatures/Fusion/StarPolicy.cs:90-117`; spent at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:522-525` |
| Host-injected power tuning, no default | `gk-core/src/FusionRpg.Core/Power/PowerTuningHub.cs:15-17` |
| Crafting cost legs are rung coefficients, "never a magnitude multiplier" | `ssot-power-scale.md` §10.2 row 37 (`gk-core/data/tuning/materials.v1.json` `operations`) |

### Wiring gap

| What is inert | Evidence | Consequence for this module |
|---|---|---|
| `TurnEngine.Step` accepts `PowerTuning`, but the production commit and replay pass none | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-170`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`, `:773` | **Not the read for this module.** Passing it would also wake `ClaimResolver`'s sector-loot path, another program's inert gate (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:124-127`). The located read uses `PowerTuningHub.Tuning` instead (§Design 2) |

### Real gap

| Gap | What this module builds |
|---|---|
| No scale read for located goods | `LocatedScale` (§Design 1) |
| No decision which located families scale | The loop table (§Design 3) |
| Both halves of the essence loop are flat against §10.4 | §Design 4 |

## Design

### 1. The read — one function

```csharp
// src/FusionRpg.Core/World/Goods/LocatedScale.cs (new)
public static class LocatedScale
{
    public static int ThetaOf(WorldSector sector, PowerTuning t) =>
        PowerIndexComposer.MapLevel(sector.DangerBand, t);            // row 23, never a private f(level)
    public static long Milli(WorldSector sector, PowerTuning t) =>
        ContentScale.Milli(ThetaOf(sector, t), t);                    // row 22
    public static long Apply(long authored, long milli) =>
        ContentScale.Apply(authored, milli);                          // one rounding, checked
}
```

Every located yield (`yield-structures`) and the warehouse capacity (`warehouse-axis`) call
`LocatedScale.Milli` for the **same sector**. It is a read of rows 22 and 23, not a new curve.

**Band 0 is a legal read.** `WorldSectorLootSource` refuses band 0 (`drop.sector-band-safe`,
`gk-core/src/FusionRpg.Core/Items/Drops/WorldSectorLootSource.cs:82-86`) because a drop needs a content level
of at least 1. A yield has no such floor: a building on safe ground yields a small amount, not an
error. `ContentScale.Milli(0)` is `C·1000/pinValue`, a positive reading.

### 2. Where the tuning comes from inside `Step`

`LocatedScale` is called inside `TurnEngine.Step` only on a world whose stamp grants
`trade.sectorYield` — **`sector-yield` wave 1's flag**, registered by `located-stock` with the one
`RulesetVersion` bump that wave takes (round 6 C1; row 1 of [../landing-order.md](../landing-order.md) §2).
This module lands *in* that wave rather than gating on a flag another wave registers, which is what round 6
C1 requires: the flag and everything it gates ship together. It reads `PowerTuningHub.Tuning`, the
host-injected tuning — the same shape `LoamUpkeep` uses for `WorldTuningHub.Tuning`
(`gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:68`). The stamp records the power tuning version, so a
mismatch refuses replay honestly (`world-stamp` acceptance). A missing `Configure` throws
(`PowerTuningHub.cs:15-17`); it is never a default.

### 3. The loop table — which families scale

PS-5 is per loop. A located yield reads the scale its loop's **sink** reads, so a yield never
outgrows what it is spent on:

| Family | Loop read | Why |
|---|---|---|
| `essence.*` | **Content** (`LocatedScale`) — **only after §Design 4 lands** | §10.4: essence must scale; this module moves both halves together |
| `souls` | **Flat — reads the soul loop's pin placeholder** (corrected in the audit of 2026-09-20; was *Content*) | Every soul sink prices through `SoulSinkPolicy.Price` at `SoulSinkPolicy.VanillaPvzTheta` (Θ = 20, exactly 1000‰), and its own pairing rule says *"a sink reads the SAME Θ its faucet reads"* (`gk-core/src/FusionRpg.Core/Creatures/SoulSinkPolicy.cs:23-25`, `:34`). A wallet sink has no sector, so it can never read a sector's depth; a sector soul yield scaled by `LocatedScale` would outgrow every sink by `Milli(band)/1000` — the PS-5 break §10.4 forbids. So a located soul yield reads the same explicit pin the sinks read (byte-identical to Flat) and moves to Content only in the change that gives the soul sinks a real Θ signal |
| `shard.*`, `substrate.*`, `catalyst.*` | **Flat** | Their sinks are rung coefficients that never scale by `P(Θ)` (§10.2 row 37). "Neither" is PS-5-legal |
| legion pieces | **Flat** (count, not magnitude) | A piece is a counted object; its stats are `legion-build`'s |

`LoopScale { Content, Flat }` is a closed two-member enum, pinned with its reason. A family moves
from Flat to Content only in the change that makes its sink scale.

**Residual pairing, measured rather than assumed.** Round 4 Q7 fixes the essence sink's `Θ_sink` as the
fused creature's level, while the essence faucet reads the producing sector's depth. Both are reads of the
one ladder, but of different indices, so PS-5 holds only as far as the two indices move together in play.
The owner decided the sink read; this module does not reopen it. `trade-foundation` `economy-report`
prints the faucet-to-sink scale ratio for every Content loop (its "PS-5 pairing" row), so a drift is a
reported finding with numbers, not a silent inflation.

**Warehouse capacity** reads Content for every sector, whatever it holds: more room at depth never
walls a flat good, and a flat capacity would wall a scaling one.

**Recorded contradiction (not resolved here):** §10.4 says *"souls, essence and materials … must
scale"*; §10.2 row 37 (2026-09-15) makes crafting legs rung coefficients that never scale. Shard,
substrate and catalyst yields therefore stay Flat until the materials program reconciles the two.

### 4. The essence loop — both halves in one change

1. **Faucets.** The sector yield reads `LocatedScale` (above). The expedition faucet, which has no
   depth signal, reads the soul loop's explicit placeholder
   (`SoulSinkPolicy.VanillaPvzTheta`, `contentScale = 1000‰`): byte-identical today, and it moves the
   day an expedition depth exists, exactly as the soul faucet does.
2. **Sink.** `FusionCost.EssenceCount` is scaled once, at spend time, by
   `ContentScale.Apply(count, ContentScale.Milli(Θ_sink))`. `EssenceCount` widens from `int` to `long`
   (a scaled magnitude, CLAUDE.md range table).
   **`Θ_sink` is the fused creature's level, read through the power ladder — decided by the owner
   (round 4 Q7, [../decisions-round-4.md](../decisions-round-4.md)):** *"the fusion essence cost scales by
   the fused creature's level through the power ladder (needs the creature program's agreement in the
   building change)"*. The essence buys that creature's `P(Θ)`-scaled power, so pricing it there keeps the
   ratio fixed as the player climbs. This is the creature program's balance surface (`FusionTuning`,
   `RpgStore.Fusion.cs`); the change is made with that program, not taken over, and its agreement is
   recorded in the change.
3. **Gate.** Until the sink half is merged, the loop table holds `essence.*` at **Content-pending**:
   `yield-structures` refuses, at catalog load, any yield band naming an essence good. No scaling
   essence yield can ship against a flat sink.

### 5. The §10 row

One §10.2 row, at the next free ordinal when it lands (§10's own *"assigned at the moment they land"*
rule): *"Located-goods scale — `LocatedScale.Milli(sector) = ContentScale.Milli(MapLevel(dangerBand))`
for located yields of Content-loop families and for warehouse capacity; a read of rows 22 and 23, not
a curve; Flat families (row 37's sinks) never read it."* Plus a line in §10.4 recording that the essence
loop moved from "neither" to "both" with this module.

## Tunables

None owned. The pin, `Wm` and the curve are `power-scale.v{n}.json`'s; essence counts stay in
`fusion.v{n}.json` (unchanged values — only their scale read changes).

## Numeric types

`long` everywhere a scaled value lives; `ContentScale.Milli` and `Apply` are already `long`, `checked`,
divide once (`gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15-40`). `FusionCost.EssenceCount` and
`FusionCostTuning.EssenceCount` widen `int` → `long`: a count multiplied by `P(Θ)/pin` reaches `int`
range only at very large `Θ`, but it is a content-scaled magnitude and the repo rule is `long` for
those. The expedition `+1` accumulator is already `long`-keyed through the grant list
(`RpgStore.Materials.cs:183`).

## Acceptance (contract)

1. `LocatedScale.Milli` at `dangerBand` 4 (`MapLevel` 20, the pin) is exactly 1000.
2. For every band, `yield-structures`' credit and `warehouse-axis`' capacity are scaled by the value
   `LocatedScale.Milli` returns for that sector — a test that feeds a sector through both paths and
   fails if either used a different factor.
3. `LocatedScale.Milli` at band 0 returns a positive value and never throws.
4. `LoopScale` has exactly two members (closed, pinned with its reason); every `LocatedGoodKind`
   family maps to exactly one loop read. `souls` maps to Flat, and a test fails if it is moved to Content
   while `SoulSinkPolicy.Price` is still called with `VanillaPvzTheta` at any call site (the pairing rule).
5. A yield band that names an `essence.*` good is a load rejection until the sink half is merged; after
   it merges, the same band loads.
6. With the sink half merged: a fusion whose `Θ_sink` is 20 costs exactly today's essence count; one
   whose `Θ_sink` differs costs `ContentScale.Apply(count, Milli(Θ_sink))`, asserted against the
   function, not a literal.
7. The expedition essence faucet produces exactly today's amounts (it reads the pin placeholder).
8. No located read runs on a world whose stamp lacks `trade.sectorYield` (wave 1's flag, §2), and `Step`'s `powerTuning`
   parameter stays unpassed by the commit (sector-loot stays inert).
9. `python gk-core/scripts/audit-overflow.py` reports no new finding on the touched files.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Goods/LocatedScaleTests.cs` (new): items 1–4, 8.
- Creature-program tests for items 6–7 extend the existing fusion and expedition suites; existing
  expected values must not change at `Θ_sink` = 20. If any other expected value moves, that is the
  measured consequence of item 6 and is triaged, never re-blessed to pass.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/LocatedScale.cs',
  'gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs',
  'gk-core/src/FusionRpg.Core/Creatures/Fusion/StarPolicy.cs',
  'gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedScaleTests.cs') -Session <active-session-id>
python gk-core/scripts/audit-overflow.py
python gk-core/scripts/guard-power.py
```

The change crosses Core and Data (fusion spend), so it is one of the three points where the full suite
runs once at module end (AGENTS.md "Verification boundary", point 2).

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedScale.cs               (new) — §Design 1-3
gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs          MODIFIED — EssenceCount long
gk-core/src/FusionRpg.Core/Creatures/Fusion/StarPolicy.cs            MODIFIED — FusionCost.EssenceCount long; scale at Θ_sink
gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs         MODIFIED — explicit pin read (value unchanged)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs                 MODIFIED — spends the scaled count
docs/architecture/power/ssot-power-scale.md                  MODIFIED — one §10.2 row, one §10.4 line
tests/FusionRpg.Core.Tests/World/Goods/LocatedScaleTests.cs  (new)
```

## Boundaries and hard edges

- **Always:** one read function; the sink half and the gate in the same merge as the faucet half.
- **Ask first:** changing which `Θ` the fusion sink reads (round 4 Q7 fixed it); moving a Flat family
  to Content.
- **Never:** pass `powerTuning` into `Step` from the commit to feed this read (wakes sector-loot);
  a private `f(dangerBand)`; a scaled essence yield against a flat sink; scaling loam.
- **Hard edge — cross-program.** `FusionTuning.cs`, `StarPolicy.cs`, `RpgStore.Fusion.cs` and
  `ExpeditionResolver.cs` are the creature and expedition programs' files. The change is coordinated
  with them and carries their sign-off on `Θ_sink`.

## Dependencies and interface

**Depends on:** `trade-foundation` `world-stamp` (the capability flag); nothing else.

| Exposed | Consumer |
|---|---|
| `LocatedScale.Milli/Apply/ThetaOf` | `warehouse-axis`, `yield-structures`; later `logistics-flow` lane throughput (same read, umbrella invariant 7) |
| The loop table (`LoopScale` per family) | `yield-structures` (which goods may scale), `exchange` (valuation reads the same scale) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: power scale (PS-5, §10), economy (essence loop), creature fusion cost, expeditions.
[~] Session boundary: trade-network-idea-20260919 covers this file; session-boundary-check.py exits 1 on
    the crossing already recorded there.
[x] Read this session: ssot-power-scale §10 (whole), economy-principles P1-P14, empire-resource-ssot,
    trade-network-ideal §14b, the umbrella and sector-yield maps.
[x] decisions.md: power scale row; magic numbers row — no literal introduced.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: ContentScale, MapLevel, SoulSinkPolicy, FusionCost, the expedition +1, the
    unpassed powerTuning and ClaimResolver's sector-loot gate.
[x] Surrounding sections read: §10.2 row 37, §10.3 mapLevel, §10.4 PS-5, SoulSinkPolicy's class doc.
[x] Constraints tested, not assumed: no suite run (spec phase). Item 6 names what may move and how it is
    triaged; nothing is claimed as measured.
[x] No §2 invariant contradicted. Named contradiction between ssot-power-scale §10.4 and §10.2 row 37,
    recorded, not resolved.
[x] Corrections propagated to the session report (the §10.4/row 37 tension; the powerTuning hazard).
[x] No population pinned; LoopScale (2) is a closed vocabulary with its reason.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude produced; fusion cost is an economy number, not an actor stat.
[x] No SOLID fork: one read, delegating to rows 22 and 23.
[x] Registry row for a new rule: "located yields read LocatedScale only" is asserted by acceptance 2; the
    power guard (guard-power.py) already covers private curves.
```

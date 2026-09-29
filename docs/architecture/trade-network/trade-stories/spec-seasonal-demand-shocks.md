# Spec: `seasonal-demand-shocks`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 7, wave 3). Every `file:line` below was opened this session. Docs only.

## Objective

Seasons move demand. At a season change a deterministic roll decides which goods classes face a demand
shock, its direction and its duration. The shock is a **term in the one demand function** `counterparties`
owns, so prices move only through `exchange`'s curve, and it is announced as a `trade.demand.shock` fact
that can make storylets eligible (a clan short of fire essence in a cold season).

## Locked anchors

- **One demand function.** `counterparties` `need-vector` is the SSOT for demand; demand is a sum of
  registered terms and *"a new term registers into the one function and never writes a price or a second
  demand table"* ([counterparties-map.md](../counterparties-map.md) module 1, acceptance).
- **One price.** Prices are `exchange`'s curve over demand; a shock never writes a price.
- **Only demand drifts.** A shock never adds stock (trade-network ideal §7.2: stock that refills from nothing
  mints goods).
- **Determinism.** Rolls use `WorldSeed.DeriveRollSeed` with a named stream
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`); never `System.Random`, never the clock.
- **Do not reuse the special week/month rolls** (their effects belong to other modules,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:341`); shocks roll their own stream.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Deterministic season function | `gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:42` (`SeasonOf`) |
| Season change reported in the `Events` phase | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:362-363` |
| Named-stream roll seed | `gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24` |

### Wiring gap

`INeedVector` defaults to a uniform stub (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31`); the real
per-good vector is `counterparties` `need-vector`.

### Real gap

No shock schedule; no demand-term seam (owned by `need-vector`).

## Design

### 1. The schedule (pure)

```csharp
// src/FusionRpg.Core/World/Trade/Demand/DemandShockSchedule.cs (new)
public sealed record DemandShock(string GoodClassId, int Direction /* +1 or -1 */, int StartTurn, int EndTurn,
                                 long DemandMilli);
public static class DemandShockSchedule
{
    // Pure. For a season starting at `seasonStartTurn`: for each (good class, climate) in stable id order,
    // roll WorldSeed.DeriveRollSeed(worldSeed, "trade:demand-shock", $"{seasonOrdinal}:{goodClassId}:{climateId}")
    // where seasonOrdinal = seasonStartTurn / seasonLengthTurns — ABSOLUTE, never TurnCalendar.SeasonOf,
    // which is cyclic (`% SeasonCount`, TurnCalendar.cs:42) and would replay the same shocks every year
    // against shock.chanceMilli; on a hit, direction from the next draw of the same stream.
    public static IReadOnlyList<DemandShock> ForSeason(long worldSeed, int seasonStartTurn, WorldState world,
                                                       TradeTuning tuning);
    // Active shocks at a turn are derived from the schedules of the seasons that could still cover it —
    // never stored, so the hash does not grow.
    public static IReadOnlyList<DemandShock> ActiveAt(long worldSeed, int turn, WorldState world, TradeTuning tuning);
}
```

### 2. The demand term

**Why the ordinal is absolute (audit 2026-09-20).** `TurnCalendar.SeasonOf` returns
`turn / (DaysPerMonth × MonthsPerSeason) % SeasonCount` (`gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:42`) —
the season's **index in the year**. Seeding the roll with it would give every spring of every year the
same shocks, forever, and the fact key built from it (`trade-fact-kinds` §3) would dedupe away every year
after the first. The roll and the key use `seasonOrdinal = seasonStartTurn / seasonLengthTurns`, which
never repeats; the season's *kind* (spring, winter) still comes from `SeasonOf` wherever a shock row
depends on it.

A registered term `SeasonalShockTerm` in `need-vector`'s term registry: for an active shock on
`(good class g, climate c)`, demand **at every sector whose climate is c** (need-vector's per-sector read,
exchange ask E-A10) for every good in g is multiplied by `(1000 ± shock.demandMilli) / 1000` (widened to `long`,
divided last). Truth side and belief side call the same term (seasons are public, never fogged —
`TurnEngine.cs:355-361`).

### 3. The announcement

In the `Events` phase, on the season-change turn, one report entry per shock (a typed kind if
npc-story-events' `world-events-host` typed vocabulary has landed, otherwise a detail prefix
`trade.demand-shock:`), world-visible (seasons are public). `trade-fact-source` projects it to
`trade.demand.shock`.

## Tunables

`data/tuning/trade.v1.json` (new): `shock.chanceMilli` (per-mille per good class per season),
`shock.demandMilli` (per-mille modifier — a **bounded ratio**, `0 ≤ x < 1000`, commented as such, so a
downward shock never makes demand negative), `shock.durationTurns` (world turns, ≤ one season's length,
checked at load).

## Numeric types

`chanceMilli`, `demandMilli`: `long` per-mille; the demand product widens to `long` before multiplying and
divides by 1000 last; turns `int`.

## Contract exposed

`DemandShockSchedule`, `SeasonalShockTerm` (registered in `need-vector`), the announcement entry.
Consumers: `need-vector` (→ `exchange` hub demand, `trade-ai` valuation), `trade-fact-source`,
`trade-predicates` (via story-fact recency).

## Acceptance (contract level)

1. **Deterministic:** same world seed and turn produce the same active shocks, byte for byte.
1a. **No yearly repeat (audit 2026-09-20):** over a fixture spanning three years, the same-named season
    in different years draws from different roll targets (`seasonOrdinal` differs), and each shock's
    announcement is a distinct fact (no dedupe collision across years).
1b. **Climate-scoped:** a shock on `(g, c)` changes demand only at sectors of climate `c`.
2. **One mechanism:** a scan finds no price write outside `exchange`; with the term registered and no
   other change, the only moved values are demand and prices derived from it.
3. **No minting:** a shock never changes any stock (stock before == stock after the phase, per good).
4. **Bounded ratio:** `shock.demandMilli ≥ 1000` rejects the load.
5. **Public:** truth-side and belief-side need vectors agree on the shock term for every faction.
6. **Missing key:** any missing `shock.*` key rejects the load (T5).

## Test plan and verification boundary

Core schedule, term and announcement tests — `core-fallback`; the tuning file's boundary is added by
the first `trade.v1.json` owner (gap stated in `trade-lexicon` §5 for the sibling catalog).

## Hard edges

- Blocked on `counterparties` `need-vector`'s term registry (ask filed: *a demand contribution seam*).
- A behaviour change to demand rides the per-world stamp; old-stamp worlds get no shock.

## Dependencies

`trade-fact-kinds`; `counterparties` `need-vector`; `exchange` (reads demand); `trade-foundation`
`world-stamp`; npc `world-events-host` (typed kinds, optional).

## Boundaries

- **Always:** demand only; named stream; bounded ratio.
- **Ask first:** shocks that target a single clan rather than a good class.
- **Never:** a price write; a stock write; the special-week roll.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world calendar, demand (counterparties), prices (exchange, read), tuning.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: counterparties-map module 1, trade-stories-map §6.7, tunables-ssot T1/T5, CLAUDE.md numeric rules.
[x] decisions.md: Empire resource registry (:108 — no faucet from nothing).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: SeasonOf, season report line, WorldSeed, UniformNeeds, Events comment.
[x] Surrounding sections read (season "never fogged" comment).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted (bounded ratio commented; long math).
[x] Corrections propagated: none needed.
[x] No population pinned.
[x] No cache (active shocks derived, not stored).
[x] No ordering criterion (stable id order is the roll order, stated).
[x] No actor magnitude.
[x] No parallel path: one demand function, one price curve.
[ ] Registry row: "no price write outside exchange" needs a guard row when built (map §11 open box).
```

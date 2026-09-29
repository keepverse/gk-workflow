# Spec: `production-halt`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.5 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §8.2 (*"Production halts
at capacity … not waste. Only incoming deliveries … overflow"*), §10 C7. Umbrella contradiction X1.
Base-defense decision 22 (production stops at capacity, reversible).

## Objective

Wire decision 22 for located goods: when a sector's warehouse is full, its production **stops** —
nothing is made and nothing is wasted — and the turn report says which good stopped where. This module
is the **one credit function** every located yield goes through, and the first production caller of
`StructurePolicy.IsHaltedByCapacity`.

Success: a full warehouse produces a halt fact, not an overflow line; building capacity resumes
production next turn with no clawback; every faction's sectors obey the same rule.

## Scope and non-goals

**In scope:** the credit function, the halt rule, the halt fact.

**Not in scope:** which structures yield what (`yield-structures`); deliveries that arrive at a full
warehouse and overflow (`logistics-flow`, which keeps the "only deliveries waste" half); the throttle
forecast and notification (`trade-surface`, which reads the halt fact). **Loam keeps its shipped
clamp-and-overflow rule** (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-64`); this module does not
touch it. Rubble and ironwork stay uncapped (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:78-81`).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| Decision 22 as a function: `stock >= effectiveCapacity` | `gk-core/src/FusionRpg.Core/World/StructurePolicy.cs:56-58` |
| Its only callers are tests | `gk-core/tests/FusionRpg.Core.Tests/World/StructureStateTests.cs:244-248` (a `*.cs` search of `src/` and `tests/` finds no other) |
| Loam's different rule: clamp to room, report `loam.overflow`, never claw back | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-66` |
| Proportional split with a remainder rule, the repo's precedent | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:345-360` (`DrawProportionally`) |
| Report entries with a subject and an audience | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:64`, `:155-156`; `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs` |

### Wiring gap

| What is inert | Evidence | What closes it |
|---|---|---|
| `IsHaltedByCapacity` has no production caller (umbrella X1: the ideal called it *"shipped"*) | above | This module's credit function calls it |

### Real gap

The credit function and the halt fact.

## Design

### 1. The one credit function

```csharp
// src/FusionRpg.Core/World/Goods/LocatedProduction.cs (new)
public static WorldSector Credit(
    WorldSector sector,
    IReadOnlyList<(string GoodId, long Yield)> yields,   // one turn's yields, Yield > 0
    long capacity,                                       // SectorWarehouse.EffectiveCapacity
    StockDeltaRecorder deltas, TurnReport report, string phase,
    string factKind = "produce",                         // "income" for income-parity
    CreditMode mode = CreditMode.HaltAtCapacity);        // FullCredit for income-parity
```

`CreditMode.FullCredit` is the one exception, and only `income-parity` passes it: an earned reward lands
whole even above capacity (`spec-income-parity.md` §4); steps 1–4 below are skipped and every yield is
credited in full with its factKind. Production always uses `HaltAtCapacity`.

1. `held = SectorWarehouse.Occupancy(sector)` (the owner's stock plus every registered occupancy term,
   such as `exchange` consignments — `spec-warehouse-axis.md` §3). If `StructurePolicy.IsHaltedByCapacity(held, capacity)`: credit
   nothing; emit one halt fact per yielding good; return the sector unchanged.
2. `room = capacity − held`, `want = Σ Yield` (`checked`).
3. If `want <= room`: credit every yield in full.
4. Otherwise split `room` **pro rata by yield**: `share_i = room × Yield_i / want` (`long`, widened,
   `checked`, one integer division); the remainder (fewer units than there are goods) goes one unit
   each to goods in ordinal id order. The same shape as `DrawProportionally`
   (`LoamPhases.cs:345-360`), spread one unit per good rather than all to the first id, so no good is
   systematically starved when room is short. The part not credited is **not produced**: no overflow
   line, no waste delta, and a halt fact for each good whose share fell short.
5. Every credit goes through `LocatedStockOps.Add(..., factKind, ...)` (`located-stock`) with the call's
   own `factKind` — `produce` for production, `income` for `income-parity`'s `FullCredit` — so every unit
   credited is a stock delta of the right kind.

Every located credit — structures today, clan production (`counterparties`), legion-equipment recipes
(`legion-build`) and income with a location (`income-parity`) — calls this function. There is no second
credit path. A sector whose warehouse is full halts its yields; with round 5's base yard (R5-A A2) a
held sector always has some capacity, so the halt comes from a full yard rather than from a missing
building. An unowned sector (capacity 0) halts every yield. The halt fact is what `logistics-flow`
`forecast-facts` answers with *build storage* (a Storehouse, or its next tier).

### 2. The halt fact

A report entry in the calling phase, kind `TurnReportKinds.Event`, subject the sector, audience the
owning faction:

```
goods.halt:<goodId>:<notProduced>
```

`notProduced` is the yield the good would have added (`Yield − credited`). `trade-surface` turns it
into the throttle forecast and a notification; this module only emits it. A halt is not a stock
change, so it writes no stock delta and no ledger row.

### 3. What a halt is not

- **Not a clawback.** If a sector's stock is already above capacity (a warehouse building was
  destroyed), nothing is removed; the sector simply produces nothing until there is room.
- **Not a spiral.** A halt changes no future yield, rating, depletion or capacity. It is fully
  reversible the turn capacity returns (decision 22: *"reversible the moment more storage is built"*,
  `StructurePolicy.cs:56-57`).
- **Not player-only.** The function takes no faction argument and reads none (umbrella invariant 11).

## Tunables

None. The rule is structural (decision 22); capacity and yields are other modules' tunables.

## Numeric types

`long`, `checked`; `room × Yield_i` is widened before the multiply and divided once. `room` and
`Yield_i` are content-scaled magnitudes, so the product is the value to check, not the quotient.

## Acceptance (contract)

1. At capacity (`held >= capacity`), credited is 0 for every good and one halt fact per yielding good
   is emitted.
2. Below capacity with `want <= room`, every good is credited in full and no halt fact is emitted.
3. With `want > room`, credited sums to exactly `room`; each good's credit is its pro-rata floor share
   plus at most one remainder unit; the remainder units go to goods in ordinal id order; the rest is not
   produced — no `*.overflow` line and no negative or waste delta anywhere.
4. **Order-independent resume:** "halt, then build capacity" and "build capacity, then reach the old
   limit" both produce on the next turn; both orders are tested.
5. A halt on turn *t* leaves turn *t+1*'s yields, capacity and depletion exactly as they would be
   without it.
6. Stock above capacity is never reduced by this function.
7. Two sectors with identical state owned by different faction kinds (player, AI empire, clan) credit
   identically.
8. Loam's `LoamPhasesTests` stay green with no expected value changed (loam is untouched).
9. The function is the only caller of `LocatedStockOps.Add` with factKind `produce` or `income` (a source
   scan).
10. `FullCredit` credits every yield in full whatever the occupancy and emits no halt fact; only
    `income-parity` passes it (a source scan).
11. A sector with capacity 0 credits nothing in `HaltAtCapacity` mode and emits one halt fact per yielding
    good.

## Test plan and verification boundary

`tests/FusionRpg.Core.Tests/World/Goods/LocatedProductionTests.cs` (new): items 1–7, 9–11.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/LocatedProduction.cs',
  'gk-core/src/FusionRpg.Core/World/StructurePolicy.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedProductionTests.cs') -Session <active-session-id>
```

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedProduction.cs     (new)
gk-core/src/FusionRpg.Core/World/StructurePolicy.cs             MODIFIED — doc comment names its caller only
tests/FusionRpg.Core.Tests/World/Goods/LocatedProductionTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** one credit function; halt, never waste, for production.
- **Ask first:** changing loam's overflow rule to a halt (a loam behaviour change on every world).
- **Never:** an overflow or waste delta from production; a clawback; a faction branch.

## Dependencies and interface

**Depends on:** `located-stock`, `warehouse-axis` (capacity and occupancy).

| Exposed | Consumer |
|---|---|
| `LocatedProduction.Credit` | `yield-structures`, `legion-equipment-stock`, `income-parity` (full mode); later `counterparties` (clan production), `legion-build` (recipes) |
| `goods.halt:<good>:<n>` report grammar | `trade-surface` (`throttle-forecast`, `trade-notify`) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn (Production), structures policy.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: trade-network-ideal §8.2, §10; umbrella X1; base-defense decision 22 via
    StructurePolicy's own comment; economy-principles P9-P10.
[x] decisions.md checked: no lock on located production.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: IsHaltedByCapacity and its only callers; loam's overflow; DrawProportionally.
[x] Surrounding sections read: LoamPhases.Production's clawback comment; SiegeConstruction's uncapped note.
[x] Constraints tested, not assumed: no golden claim beyond "loam untouched" (acceptance 8).
[x] No §2 invariant contradicted: halt is a reversible soft stop against a scaled capacity.
[x] Corrections propagated: X1 is restated here; no other doc changed.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Ordering: halt-then-build and build-then-halt are both criteria (acceptance 4).
[x] No actor magnitude.
[x] No SOLID fork: one credit function for every located yield.
[ ] Registry row: the one-credit-function rule (acceptance 9) is a test source scan; its
    enforcement-registry row lands with this module.
```

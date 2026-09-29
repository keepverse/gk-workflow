# Spec: `stock-deltas`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `stock-deltas`, §2.6 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; depends on `ledger-keys`).
Principles P1 and P14 ([../../economy-principles.md](../../economy-principles.md)); umbrella
invariants 5 and 6.

## Objective

`Step` changes world stocks in a dozen places and says so only where a phase chose to write a free-text
report line (for example `loam.overflow`, `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:63-64`). Nothing
downstream can tell how much loam was produced, drawn for upkeep, burnt or lost in a turn. This module
makes `Step` **report every change it makes to a world stock as a typed delta** — `(holder, stock,
delta, factKind, owner)` — and proves the record complete: for every holder and every registered stock,
the deltas sum to post-step minus pre-step. It is the pure half of the world-stock ledger and the source
the economy report reads.

Success looks like: a scripted multi-turn run on a synthetic world reconciles every turn; a mutation
site that forgets to record fails the reconciliation; and the state hash is unchanged by the recorder.

## Scope and non-goals

In scope: `StockDelta`, `StockDeltaRecorder`, the closed `WorldStockRegistry`, the reconciliation check,
and one recording call at every current mutation site.

Not in scope: persistence (`world-stock-ledger`); new stocks (each sub-program adds its registry row);
changing any amount a phase computes; the `Logistics` phase's zero-allocation budget (a pooled recorder
is `logistics-flow`'s concern if its bench shows the need).

## What already exists

### Built — every current mutation of a world stock inside `Step`

| Stock | Site | What it does |
|---|---|---|
| loam (sector) | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:57-66` | production, capped; the overflow never enters the stock |
| loam (sector) | `LoamPhases.cs:160-165`, draw rule `:345-360` | pooled upkeep, drawn proportionally across a component |
| loam (sector → legion) | `gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs:98-104` | top-up drawn with the same rule, distributed to legions |
| loam (legion) | `LegionSupply.cs:124-146` | burn out of supply; a legion that cannot pay is destroyed |
| loam (legion → sector) | `gk-core/src/FusionRpg.Core/World/Movement/SustainResolver.cs:58-76` | `sustain` order |
| loam (legion), rubble, ironwork (sector) | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:134-158` | construction cost |
| loam (sector) | `gk-core/src/FusionRpg.Core/World/Growth/DevelopResolver.cs:77` | project cost |
| rubble, ironwork (sector) | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:90-103` | production from cleared slots |
| recruit (sector) | `gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs:66` | weekly pulse |
| recruit (sector) | `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:108` | `raise` spend |
| loam (legion) | any phase that removes an entity (battles in `Movement`, `Sieges`, `Assaults`; starvation in `LegionSupply.cs:134-140`) | the carried stock leaves the world with its holder |

The stock fields: `WorldSector.LoamStock`, `RubbleStock`, `IronworkStock`, `RecruitStock` and
`WorldEntity.CarriedLoam` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:173`, `:181`, `:187`, `:234`, `:327`).
`TurnReport` is already passed to every phase (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:191-207`)
and records the phase order through an internal `BeginPhase` (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:37-45`, `:90`).
The store persists a report by serialising `Entries` and `Phases` only
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:678-679`).

The empire resource registry is a **document**, not code (`docs/architecture/empire-resource-ssot.md` §3);
it lists loam, rubble and ironwork as world stocks and recruits as an accrual meter.

### Real gap

No typed record of any stock change; no completeness check.

## Design

### 1. Types (`src/FusionRpg.Core/World/Ledger/`, beside `ledger-keys`)

```csharp
public enum StockHolderKind { Sector, Entity }        // closed, two members

public readonly record struct StockDelta(
    StockHolderKind HolderKind, string HolderId, string StockId,
    long Delta, string FactKind, string? OwnerId);

public sealed class StockDeltaRecorder
{
    public void Record(WorldSector sector, string stockId, long delta, string factKind);
    public void Record(WorldEntity entity, string stockId, long delta, string factKind);
    public IReadOnlyList<StockDelta> Deltas { get; }  // aggregated, ordered (§3)
}

public sealed record WorldStockDef(string Id, string ResourceClass,
    Func<WorldState, IEnumerable<(StockHolderKind Kind, string HolderId, string StockId, long Qty)>> Holdings);

public static class WorldStockRegistry { public static IReadOnlyList<WorldStockDef> All { get; } }

public static class StockReconciliation
{
    public static IReadOnlyList<string> Check(WorldState before, WorldState after, IReadOnlyList<StockDelta> deltas);
}
```

`Record` ignores a zero delta, validates `factKind` against `FactKinds` (world scope) and `stockId`
against the registry, and takes the owner from the holder it is handed (`sector.OwnerFactionId` /
`entity.OwnerFactionId`) **at the moment of the change** — deriving it later from the post-step world
would misattribute a sector lost in the same turn. Arithmetic is `checked`.

### 2. Where the recorder lives

`TurnReport` owns one `StockDeltaRecorder`, exposed as `report.Stocks`. Every phase already receives the
report, so no phase signature changes. It is a separate type with one responsibility; `TurnReport`
only carries it, the same way it carries phases beside entries. `TurnResult` gains
`public IReadOnlyList<StockDelta> StockDeltas => Report.Stocks.Deltas;`. Stored reports are unchanged
(only `Entries` and `Phases` are serialised); a report rebuilt from storage has an empty recorder, which
is correct — deltas are consumed at commit from the live `Step`, never from a replayed report.

### 3. Aggregation and order

`Deltas` sums records with the same `(HolderKind, HolderId, StockId, FactKind, OwnerId)` across the
turn, drops sums of zero, and orders by those five fields, ordinal. One aggregated delta is exactly one
ledger key (`ledger-keys` §2), so a second `topup` on the same legion in one turn can never be swallowed
by the ledger's dedupe.

### 4. The recording calls

One call beside each mutation in the table above, in the same statement's scope:

- production, upkeep, top-up, burn, sustain, construct, develop, pulse, raise — `factKind` as in
  `ledger-keys` §4;
- `LoamPhases.DrawProportionally` (`:344`) gains an optional `(StockDeltaRecorder, string factKind,
  IReadOnlyDictionary<string, WorldSector>)` so it records each sector's share where it subtracts it —
  one draw rule, one record, for both its callers;
- **removal:** `TurnEngine.Step` records `lost` for every entity present before a phase and absent after
  it, with the amount *(its holding at phase start + this phase's recorded deltas for it)*. Doing it at the
  phase boundary covers every removal site — battles, starvation, anything later — with one rule instead
  of one call per battle path; an entity that appears carrying stock still needs its own site's record,
  and reconciliation fails until it has one.

### 5. The registry

`WorldStockRegistry.All` v1:

| Id | Class (registry doc) | Holdings |
|---|---|---|
| `loam` | world stock | every sector's `LoamStock`, every entity's `CarriedLoam` |
| `rubble` | world stock | every sector's `RubbleStock` |
| `ironwork` | world stock | every sector's `IronworkStock` |
| `recruit` | accrual meter | every sector's `RecruitStock` |

A row is added by the change that ships a world-held quantity — `sector-yield`'s located goods add one
row whose `Holdings` walks the warehouse (`sector-yield/spec-located-stock.md`, which names this
widening); `sector-yield` `banking-fact`'s bank holds are a policy, not a stock, and add no row;
`exchange` consignments and `counterparties` AI treasuries add theirs (the treasury needs the
`Faction` holder kind, `spec-ledger-keys.md` §4a).

**Goods in transit (audit 2026-09-20).** `logistics-flow` `transit-buffer` moves located goods and world
stocks off a sector onto a route. Those goods must stay inside the reconciliation, so the change that
ships `transit-buffer` adds `StockHolderKind.Route` (holder prefix `r:`, `spec-ledger-keys.md` §4a) and
widens the `located goods`, `rubble` and `ironwork` rows' `Holdings` to walk `WorldState.Transit` packets as
well as sectors. Every logistics step then records its move: `depart` (sector −, route +), `deliver` and
`return` (route −, sector +), `loss` and `waste` (route −). A step that moves goods without recording fails
criterion 1 on the first logistics turn — the net this module exists to be.

**What the record does not answer.** Deltas are keyed by holder, and a capture moves no stock (the goods
stay on the sector; only its owner changes). So the ledger reconciles **per holder**, and each delta's
`OwnerId` says who held it at the moment of the change; a per-owner *balance* is not derivable from deltas
alone (it would need a capture transfer fact). Per-owner **flows** — what a faction produced, banked or
lost — are derivable, and those are what `economy-report` reads. A consumer that needs per-owner balances
reads the hashed state, not the ledger.

**Coarse-step rates (world-continuity ask).** `world-continuity` `coarse-step` reads per-sector,
per-stock deltas with production separable from upkeep; the fact kind already separates them
(`produce` vs `upkeep`), so no second record is owed. The registry is a closed vocabulary; its membership is pinned in its test with the reason,
and the pin moves in the change that adds a row. Its ids match the empire resource registry's ids.

### 6. Reconciliation

`Check(before, after, deltas)` builds, for every registry row, the maps *holding → qty* of both worlds
(an absent holder counts 0), and for every key compares `after − before` with the sum of deltas for that
key. It returns one message per mismatch and one per delta whose stock id is not registered. Empty means
complete.

### 7. Determinism and the hash

The recorder is write-only from inside `Step` and read only after it returns. No phase reads it, so the
state and its hash are unchanged. No `RulesetVersion` bump.

### 8. Numeric types

`long` deltas and sums, `checked` (PRINCIPLES §5). No multiplication is added; `DrawProportionally`'s
existing share arithmetic is unchanged.

## Tunables

None.

## Acceptance criteria (contract)

1. Over a scripted multi-turn `SyntheticCampaign` run on a synthetic `medium` world and a `two-hearths`
   run, `StockReconciliation.Check(before, after, result.StockDeltas)` is empty **every turn** for every
   registered stock and holder.
2. A falsifier — a test-only phase wrapper that changes `LoamStock` without recording — makes `Check`
   report that sector and stock.
3. The same world, commands and seed produce the same `StateHash` with the recorder populated as before
   this module (golden suites unchanged, no `RulesetVersion` bump).
4. `Deltas` is ordered by `(HolderKind, HolderId, StockId, FactKind, OwnerId)`, ordinal, and contains no
   zero and no duplicate key — asserted on any run, independent of which phases fired.
5. An unregistered stock id or an unknown fact kind passed to `Record` throws.
6. A legion destroyed in a phase yields exactly one `lost` delta equal to what it held at that moment,
   whether it was topped up earlier in the same turn or not (both orders tested).
7. `WorldStockRegistry.All`'s ids are pinned with the closed-vocabulary reason; `StockHolderKind` has two
   members at this module's landing, pinned the same way (each widening — `Faction`, `Route` — moves the pin
   in its own change, `spec-ledger-keys.md` §4a).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Ledger/StockDeltaTests.cs` and `StockReconciliationTests.cs` (new),
  `[Trait("VerificationId", "core.world-stock-deltas")]`.
- Boundary: the `core-world-ledger` owner row from `ledger-keys` widens to verificationIds
  `core.world-ledger-keys` and `core.world-stock-deltas` (or a sibling row with the second id — one per
  verificationId, as the registry's other rows do). The phase files stay on `core-fallback`, which runs
  the world goldens — the right boundary for criterion 3.
- Verify: `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>`.

## Hard edges

- **No golden move, no ruleset bump** (criterion 3 is the proof, run in the same change).
- `DrawProportionally` is shared by upkeep and top-up; its signature change updates both callers in one
  commit.

## Boundaries

- **Always:** record at the mutation, with the owner as it is then; add a registry row with any new
  world-held quantity.
- **Ask first:** recording from outside `Step` (Data-side passes do not change world stocks today).
- **Never:** let a phase read the recorder; derive owners from the post-step world; skip a zero-sum
  check because a phase "cannot" change a stock.

## Dependencies and interface

**Depends on:** `ledger-keys` (`FactKinds`, the key shape the aggregation mirrors).

| Exposed | Consumer |
|---|---|
| `TurnResult.StockDeltas`, `StockDelta` | `world-stock-ledger`, `economy-report`; `sector-yield` (`located-stock`, `production-halt`, `banking-fact`), `fleet` (`carry`), `rift-trade` (`rift-depart`, `rift-arrive`) |
| `StockDeltaRecorder.Record` | every phase that changes a world-held quantity |
| `WorldStockRegistry` | `sector-yield` (located goods row), later AI treasuries |
| `StockReconciliation.Check` | every sub-program's own reconciliation test |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine phases (loam, supply, construction, growth, siege production), turn
    report, economy instrumentation.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: economy-principles P1/P14/§13, empire-resource-ssot §2-§3, trade-foundation map
    §2.6, sector-yield's located-stock spec (the consumer that widens the registry).
[x] decisions.md: phase order (:7) untouched; registry row (:108) — no quantity added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: every mutation site in the table was opened; the report's serialised fields.
[x] Surrounding sections read (LegionSupply.Resolve whole; DrawProportionally's doc comment).
[~] Constraint tested, not assumed: "state hash unchanged" is criterion 3, proven at build time; not
    run in this docs-only session.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the holder generalisation and the phase-boundary removal rule are recorded in
    the map's corrections section.
[x] No population pinned; registry ids are a closed vocabulary with a stated reason.
[x] No event-refreshed cache.
[x] Order-independent: criterion 6 tests both orders of top-up and removal; criterion 4 holds whatever
    phases fired.
[x] ActorHub: not touched.
[x] No SOLID fork: one recorder, one draw rule recording in one place, one registry.
[x] No new guarded rule; completeness is enforced by the reconciliation test.
```

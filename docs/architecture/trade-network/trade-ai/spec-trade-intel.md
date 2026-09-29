# Spec: `trade-intel`

**Status: written 2026-09-19 against the code on `features/mega-merge`.** Every `file:line` below was
opened in this session. Module id `trade-intel`, row 1 of the approved
[trade-ai map](../trade-ai-map.md) (wave 1). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§8.5 (*"Information — plan on believed prices and lane states; settle on the truth"*), §7.7.
Upstream: `exchange` `price-curve` (the quote), `logistics-flow` `lane-flow` (the flow), `exchange`
`trade-access` (who may read a hub's board). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

An AI may only use what its faction believes (`spec-ai-commander.md` assumption 1), and belief today
holds sectors, slots and forces — no price and no flow (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:89-137`).
This module records the two trade facts a faction can observe — **the quote at a hub** and **the goods
moving along a lane** — in the same Intel phase that records everything else, hashed with it, stamped
with the turn each was seen. Every other trade-ai module reads them; so does the player's own trade
surface, because this is faction belief, not AI memory.

Success looks like: an AI that last saw a hub five turns ago bids on the five-turn-old quote and fills
at today's price (or not at all); a faction that never saw a hub has no quote for it; and a world with
no trade records hashes exactly as before.

## Scope and non-goals

**In:** the remembered quote and flow records, when they are recorded, their banding, their retention,
their hashed canonical rows, and the `IWorldView` reads (believed foreign, exact own).

**Not here:** the price formula (`exchange` `price-curve` — read, never copied); lane flow itself
(`logistics-flow` `lane-flow`); who may trade (`exchange` `trade-access`); any decision made from the
belief (every other module in this map); the player surface that shows it (`trade-surface` `trade-wire`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Belief is per-faction, per-sector snapshots, ordered by sector id; an absent entry means "never heard of it" | `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:143-156` |
| Belief is recorded once per turn in the Intel phase from end-of-turn state | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:380`, `:392`; `gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs:23-62` |
| Owner-only economy state is recorded only on a full survey and reads zero on a glimpse (`RecruitStock`) | `gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs:104`; `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:122-127` |
| A glimpse keeps the survey-only fields of an older survey but takes the glimpse's `LastSeenTurn` | `gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs:78-90` |
| Banding precedent: a remembered force is exact when the observer stood with it, a band otherwise, with a pessimistic and an expected reading | `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:30-49`; `gk-core/src/FusionRpg.Core/World/Intel/StrengthBandCatalog.cs:31` |
| A lane with neither end in sight reads `Open` — lane state is believed, lane shape is public | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:110-113` |
| Own resources are self-knowledge, read live through the view, never through belief (`OwnLoamStock`) | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:45-52` |
| Belief is hashed; intel rows are written last so a world with no intel emits the bytes it always did | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:73-87` |
| An optional hashed field emits a row only when non-default, so older goldens do not move | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:90-97` |

### Wiring gap

None. Nothing in the Intel phase is inert for trade; there is simply nothing to record yet.

### Real gap (this module closes it)

| Gap | What this module builds |
|---|---|
| No price, stock or flow field in belief | §Design 1: `RememberedQuote` on the sector snapshot, `RememberedFlow` on the faction |
| A glimpse would refresh a quote's apparent age (the `Merge` rule) | §Design 2: every quote and flow carries its own seen-turn |
| No view read for trade belief | §Design 4: `BelievedQuotes`, `BelievedFlows`, and own-side exact reads |

## Design

### 1. Two records, both sparse

```csharp
/// One good's quote at one hub, as this faction last read it.
public sealed record RememberedQuote
{
    public string GoodId { get; init; } = "";
    public int SeenTurn { get; init; }              // its own stamp — see §2
    public bool Exact { get; init; }                // read with market access or from own ground
    public long BuyPrice { get; init; }             // meaningful only when Exact
    public long SellPrice { get; init; }            // meaningful only when Exact
    public int PriceBandIndex { get; init; }        // band of price ‰ of base, when not Exact
    public long Pessimistic(bool buying) => …;      // exact, or the band edge that hurts the reader
    public long Expected => …;                      // exact midpoint, or the band midpoint
}

/// Goods one faction was seen moving along one lane.
public sealed record RememberedFlow
{
    public string LaneId { get; init; } = "";
    public string OwnerFactionId { get; init; } = "";   // whose goods
    public int SeenTurn { get; init; }
    public bool Exact { get; init; }
    public long Value { get; init; }                     // value-index units, meaningful only when Exact
    public int ValueBandIndex { get; init; }
    public long Offensive => …;                           // exact, or band midpoint — what a raider expects
}
```

`IntelSnapshot` gains `IReadOnlyList<RememberedQuote> Quotes` (ordered by good id, empty unless the
sector holds a hub); `FactionIntel` gains `IReadOnlyList<RememberedFlow> Flows` (ordered by lane id,
then owner id). A foreign flow row is **aggregate per owner faction**: you see the size of a column of
carts, not its contents. The value is `Σ goods × goods-valuation.ValueOf(good)`, the value index
`exchange` owns — never a second valuation.

### 2. Each record carries its own seen-turn

`IntelRecorder.Merge` keeps a survey's detail while taking a later glimpse's `LastSeenTurn`
(`IntelRecorder.cs:78-90`). A quote stored under that stamp would look fresh after any glimpse — an AI
would bid on a stale price believing it current. So `RememberedQuote.SeenTurn` and
`RememberedFlow.SeenTurn` are their own, set only when that record is actually re-read, and `Merge`
carries `Quotes` across like `Slots`, untouched. Age for a trade decision is
`CurrentTurn − record.SeenTurn`, never the snapshot's.

### 3. When a faction records what

Recorded in `IntelRecorder.Observe` from end-of-turn state, per faction, in the existing ordinal walk,
only when the world's stamp grants the trade capability (`trade-foundation` `world-stamp`):

| Record | Recorded when | Exact when | Otherwise |
|---|---|---|---|
| Quote, per good, at a hub sector | the faction has `SectorSight.Full` on the sector **or** `trade-access` gives it `market` or better there (trading at a hub shows its board) | the faction holds the sector or has `market` access | banded (`PriceBandIndex`) |
| Flow, per lane and owner faction | either end of the lane is in the faction's sight at any level (the lane-state rule, `IWorldView.cs:110-113`) | the faction holds either end sector | banded (`ValueBandIndex`) |

- The quote is read through `exchange` `price-curve`'s pure quote function over end-of-turn stock and
  demand. This module never computes a price.
- Flows are read from `logistics-flow`'s hashed lane-flow state. This module never simulates a flow.
- **Out of sight, the old record stands and ages**, exactly as a sector snapshot does
  (`IntelRecorder.cs:45-51`).
- **A sighting of zero removes the record**: a lane seen with no foreign goods on it for owner `o`
  drops `o`'s row; a hub seen with a good no longer quoted drops that quote. Belief stays sparse.
- **Own hubs and own flows are never stored as belief.** They are self-knowledge, read live (§4), the
  `OwnLoamStock` precedent. Holding ground grants full sight of it (`world-map-program.md` line 46).

### 4. The view

`IWorldView` gains four reads (the `OwnLoamStock` / `LastOrderedDestination` shape, `IWorldView.cs:52`, `:67`):

| Read | Returns |
|---|---|
| `BelievedQuotes(sectorId)` | the faction's remembered quotes at that hub; empty if none |
| `BelievedFlows()` | every remembered foreign flow, ordered by lane id then owner id |
| `OwnHubQuote(sectorId, goodId)` | the live exact quote at a hub the faction holds; null otherwise |
| `OwnFlows()` | the faction's own live lane flows, exact, per lane and good |

`BelievedWorldView` answers the first two from `FactionIntel` and the last two from the world it already
holds (`IWorldView.cs:94-104`), filtered to the faction's own holdings — the same gate `OwnLoamStock` uses.

**Round 4 (2026-09-19) adds two tier reads** so every trade layer can see the building gate before it
files (the `LevelAt` rule in `exchange` `trade-access` §2a; ask T-A9):

| Read | Returns |
|---|---|
| `OwnFeatureTier(SectorFeature)` (was `OwnFeatureTier(structureKind)` — superseded by round 5 X1: keyed by the `sector-features` feature, never a kind; **round 6 C2** confirms it, since no per-building kind exists any more — the one neutral `StructureKind.Feature` is not a gate) | the faction's highest active tier of that ladder (Trade, Diplomacy, Banking, Caravans, Storage, and `standard` after round 6 L6) = `SectorFeatures.FactionTier`, exact — self-knowledge, like `OwnLoamStock`. **S1 lives inside that read:** a building whose sector and slot have different owners counts for nobody, so `FactionTier` answers 0 for it and this projection never re-derives ownership |
| `BelievedAcceptsCaravans(sectorId)` (round 5 B3) | the believed form of `fleet` `depot` `ForeignSite.Of`: whether the remembered slots of that foreign hub sector show a caravans-feature building; `false` if never surveyed |
| `BelievedHubTier(sectorId)` | the tier last seen on that sector's trade hub, from the remembered slot (`RememberedSlot.StructureId`, `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:74`, plus the slot tier `trade-foundation` `sector-features` adds, `WorldSlot.StructureTier`, which the remembered slot must copy — ask T-A11); 0 if never surveyed |

A foreign hub's tier is belief, not truth: an AI may file at a hub it believes is a Market that has
since been razed; the order is then suspended by `order-book`, never thrown (admission does not judge
tiers), so a stale tier costs nothing but a wasted order.

### 5. Canonical form

Two new row kinds, `intel-quote` and `intel-flow`, written after the existing intel rows and **only when
present** (`WorldCanonical.cs:73-97` precedent). A world with no quote and no flow records emits exactly
today's bytes.

### 6. Numeric types

`Value`, `BuyPrice`, `SellPrice` are `long` value-index units (a relative index, never multiplied by
`contentScale` — `exchange` assumption 4). Flow value is `Σ qty × ValueOf` computed `checked`, widened
before multiplying. Band indices are `int` into a tuning table.

## Tunables

`data/tuning/trade.v1.json` (new; read by `Step`, so its version is in the world stamp):

| Key | Unit | Meaning |
|---|---|---|
| `intel.quoteBandEdgesMilli` | ‰ of base, ascending array | price bands a foreign quote is remembered in (e.g. edges inside `price.bandMilli`'s 250–1750 range) |
| `intel.flowBandEdges` | value-index units, ascending array | flow-size bands a foreign flow is remembered in |

Band edges are fog granularity a balance pass would move, so they are tunables (T1). A missing or
non-ascending array is a load rejection (T5).

## Acceptance (contract)

1. **Blindness.** A faction never holds a quote for a hub it neither had `Full` sight of nor `market`
   access to, and never holds a flow row for a lane neither end of which it has seen.
2. **Own is exact, foreign is banded.** For a hub or lane end the faction holds, the view returns the
   live exact value and no belief row is written; for any other, a stored row is banded unless the
   exactness rule in §3 holds.
3. **Own stamp.** After a glimpse of a sector whose quotes were last read on turn *t*, every quote's
   `SeenTurn` is still *t* (the `Merge` trap, TC8).
4. **Different sight, different belief.** Two factions with different sight of one hub hold different
   quote rows for it.
5. **Sparse and non-breaking.** A world with no hubs and no flows produces byte-identical canonical text
   to the pre-module engine; a legacy-stamped world records nothing new.
6. **One price, one valuation.** No file this module adds contains a price or value formula; a
   source-scan test asserts quote reads go through `price-curve` and value through `goods-valuation`.
7. **Exploit guard — no free scouting through trade.** A quote reveals price only; it never carries the
   hub's stock quantity or the owner's treasury (the `LoamStock` rule, `FactionIntel.cs:104-110`).
8. **Deterministic.** Same world and turn ⇒ byte-identical belief; records are ordered by id.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Intel/TradeIntelTests.cs` (new): blindness, exact vs banded, own
  stamp after a glimpse, zero-sighting removal, sparse canonical rows, two-faction divergence — on a
  purpose-built fixture with a hub and a two-lane flow (the `first-light` map has neither; the same
  lesson as `spec-ai-commander.md` §Two graphs).
- `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs` already scans `World/` for clocks and
  `System.Random` and `World/Ai/` for `WorldState` (`:108`); the view reads live under `Intel/`, which the
  engine side may read.
- Run: `.\scripts\verify-change.ps1 -Paths <changed paths> -Session <id>`. Today `World/Intel/**` resolves
  only to the module-level `core-fallback` boundary (`gk-core/scripts/verification-boundaries.v1.json`); this
  module's change adds a focused boundary row for `World/Intel/` plus its test file, per AGENTS.md
  (an unmapped path is a boundary defect to fix, not a reason for the full suite).

## Hard edges

- **New hashed state.** Rows are emitted only when present, so no existing golden should move; that is
  an acceptance test to run, not a claim. Whether this rides a `RulesetVersion` bump is `world-stamp`'s
  rule for capability-gated state, not decided here.
- **`trade.v1.json` is step-read**: its version enters every trade-stamped world's stamp; publishing a
  new band table refuses replay of older trade worlds by design (`trade-foundation` `world-stamp`).

## Dependencies

| Consumes | From |
|---|---|
| pure quote function | `exchange` `price-curve` |
| hashed lane-flow state | `logistics-flow` `lane-flow`, `logistics-canonical` |
| `Access(grantor, requester)` | `exchange` `trade-access` |
| `ValueOf(good)` | `exchange` `goods-valuation` |
| capability flag | `trade-foundation` `world-stamp` |

| Exposes | To |
|---|---|
| `BelievedQuotes`, `OwnHubQuote` | `deal-valuation`, `ai-bidding` |
| `BelievedFlows`, `OwnFlows` | `interdiction`, `ai-logistics`, `deal-valuation` (treaty legs) |
| the same belief | `trade-surface` `trade-wire` (what the player knows) |

## Boundaries

- **Always:** record in the Intel phase only; own stamp per record; sparse rows; read prices and values
  through their owners.
- **Ask first:** recording hub **stock** in belief; any sight rule beyond §3.
- **Never:** a second price or valuation formula; a record written outside `Step`; storing own-faction
  trade state as belief.

## Design-gate checklist

```
[x] Subsystems: world intel (belief, recorder, canonical), world map AI (view), economy (value index,
    read only), tunables.
[~] Session boundary: docs-only work under trade-network-idea-20260919 (paths include
    docs/architecture/trade-network/**). session-boundary-check.py exits 1 on crossings already
    recorded in that record; this file is new.
[~] Read this session: DESIGN-GATE (all), PRINCIPLES, trade-ai-map, trade-network-map,
    trade-network-ideal §1-§17, spec-ai-commander (whole), counterparties-map, exchange-map,
    logistics-flow-map §6-§7 and §10, counterparties/spec-need-vector, economy-principles,
    empire-resource-ssot, world-map-program, spec-budget-debit. NOT read: world-map-runtime ideal and
    its specs (FE rendering; nothing here draws the map), empire-economy-ssot beyond what the maps quote.
[x] decisions.md: no lock covers trade belief; world-map determinism lock respected (hashed, in-step).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file: no HIGH finding.
[x] Verified against code: FactionIntel, IntelRecorder (Merge, RecruitStock gate), IWorldView,
    WorldCanonical intel rows, TurnEngine Intel call.
[x] Surrounding sections read: IntelRecorder Merge comment, IWorldView lane-state comment.
[x] No constraint claimed without a run: "no golden moves" is stated as a test to run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: TC8 recorded in the map.
[x] No population pinned: band tables are tuning, goods and lanes are readings.
[x] No event-refreshed cache: belief is hashed state rebuilt each turn by the recorder.
[x] No ordering-dependent criterion.
[x] No actor magnitude produced or consumed.
[x] No SOLID-violating path: one recorder, one price function, one valuation.
[ ] Registry row for acceptance 6 (one price/valuation source scan) owed with the change.
[x] Round 4 reconciliation (2026-09-19): own feature tiers exact, foreign hub tier believed from the
    remembered slot (RememberedSlot.StructureId verified at FactionIntel.cs:74).
[x] Round 5 (2026-09-20): OwnFeatureTier keyed by SectorFeature (X1); BelievedAcceptsCaravans added
    for B3 from the same remembered slots as BelievedHubTier.
```

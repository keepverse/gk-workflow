# Spec: `yield-structures`

**Status:** written 2026-09-19 against `features/mega-merge` at `b82a4098`. Every `file:line` below
was opened in this session. Module 2.6 of the [sector-yield map](../sector-yield-map.md) (approved
2026-09-19). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §5 real gap *"Sector
yields of banked goods"*, §8.6, §14 D-A. The reward layer `world/spec-sector-development.md` left
unassigned (`docs/architecture/world/spec-sector-development.md:261`). Soul conduit design:
[../../empire-economy-ssot.md](../../empire-economy-ssot.md) §5 (`:195-201`).

## Objective

Held ground pays. A structure's resolved magnitudes carry a **located-yield vector** (good → amount),
and in the `Production` phase every owned sector credits its active structures' yields into its own
warehouse through `production-halt`'s one credit function — for every faction, on every world whose
stamp grants `trade.yieldStructures`. The soul conduit becomes the first row: *"a plain building that yields
souls"* (`empire-economy-ssot.md:195`), where today it yields 20 loam.

A legacy-stamped world keeps today's loam-only yields and its hash, turn for turn.

## Scope and non-goals

**In scope:** the yield field, its resolution from bands, the Production-phase call, the soul
conduit's switch, the P1 economy-report row.

**Not in scope:** banking (`banking-fact`); moving goods (`logistics-flow`); clan production and
seeding (`counterparties` — it calls the same credit function); labour as a production input (P11,
not in the approved map); slot depletion for located yields (P9 is wired for construction stocks only,
`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs` `AdvanceDepletion`; extending it is a later
change); the wonder scope modifier (it multiplies loam output only,
`gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:66-69`).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| `Yield` structures produce loam and recruits only; the reward layer is unassigned | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:16-24` |
| Flat structure yield is added to **loam** for every active structure, any slot kind | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:80-88`; `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:43-56` |
| Unowned sectors have no economy (G-B) | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:25` |
| Under-construction structures yield nothing | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:50-53` |
| The `Production` phase and its three steps | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:301-314` |
| The soul conduit: `Bank` role, `Yield` kind, `EssenceDeposit` slot, `flatYieldPerTurn` 20 | `gk-data/packs/fusion/data/seed/structures/bank/soul-conduit.json` (`anchor.role`, `anchor.requiredSlotKind`, `magnitudes`) |
| No shipped template places a structure on any slot | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs` (no `StructureId =` in either) |

### Wiring gap

| What is inert | Evidence | What closes it |
|---|---|---|
| The `Yield` kind exists and its rows are the mechanism the reward layer attaches to | `StructureCatalog.cs:16-24` | The located-yield field below |

### Real gap

A yield of any located good; the Production-phase step that credits it.

## Design

### 1. The field

`StructureDef.LocatedYields : IReadOnlyList<(string GoodId, long PerTurnAtPin)>` (empty by default),
resolved at load from an anchor field `locatedYields: [{ "good": <id>, "band": <ordinal> }]` through
`empire-seed`'s `band-reader`, against a `yieldBand` table in `data/tuning/structure-seed.v{n}.json`.

- `good` is VALIDATED against `LocatedGoodCatalog` (`located-goods-registry`), and must not be a
  `LegionPiece` (pieces are made by recipes, `legion-build`); an unknown good or band is a load
  rejection naming the row.
- Duplicate goods in one row are a load rejection.
- A yield naming a family whose loop read is **Content-pending** (`essence.*` until the fusion sink
  scales, `spec-essence-loop-read.md` §Design 4) is a load rejection.
- The anchor field and this `StructureDef` field land together (`empire-seed` `trade-structure-rows`:
  an ordinal lands only with its consuming field); the corpus is regenerated, never hand-edited.

### 2. The Production step

```csharp
// src/FusionRpg.Core/World/Goods/LocatedYieldPhase.cs (new)
public static WorldState Production(WorldState world, StockDeltaRecorder deltas,
                                    TurnReport report, string phase, TradeTuning trade, PowerTuning power);
```

Called from `TurnEngine.Production` after `SiegeConstruction.AdvanceDepletion`
(`TurnEngine.cs:313`), **only** when the world's stamp grants `trade.yieldStructures`. In sector id order:

**Round 6 C1 — this module is `sector-yield` wave 3, with its own flag and bump** (row 3 of
[../landing-order.md](../landing-order.md) §2). It used to gate on `trade.sectorYield`, which wave 1's stock
layer registers; a world stamped after wave 1 would then have started yielding goods mid-life when this
module merged. `trade.yieldStructures` is registered here with the one `RulesetVersion` bump this wave
takes.

1. Skip an unowned sector (G-B).
2. Sum `LocatedYields` over active, known structures — `SectorFeatures.ActiveTier(slot) >= 1`
   (`trade-foundation` `sector-features` §3), identical today to the gate at `LoamProduction.cs:50-53` and
   keeping a building mid-upgrade producing — per good.
3. Scale each good by its loop read (`spec-essence-loop-read.md` §Design 3): Content →
   `LocatedScale.Apply(sum, LocatedScale.Milli(sector, power))`; Flat → `sum` unchanged.
4. Drop zero results; call `LocatedProduction.Credit(sector, yields, SectorWarehouse.EffectiveCapacity(...))`.

No faction branch. A player sector, an AI empire's sector and a clan's sector with the same buildings
produce the same stock.

**Storage is a building (round 4 §B), with a base yard (round 5 A2).** A yield building credits into its
own sector's warehouse. A held sector without a storage building has only the small base yard
(`warehouse.baseYard`, `spec-warehouse-axis.md` §3), so its yields halt once the yard is full and the halt
fact names the good; the throttle forecast answers it with *build storage* (`logistics-flow`
`forecast-facts`, "base yard full, no storage building"). *(Corrected in the audit of 2026-09-20: this
paragraph said "no warehouse capacity … halt from the first turn", the round-4 rule round 5 A2
replaced.)*

### 3. The soul conduit — one structure, one reward

The conduit's row gains `locatedYields: [{ good: "souls", band: <ordinal> }]` through the generator
and the band table. Its `flatYieldPerTurn` **stays** in the catalog, because the catalog is
process-global (umbrella X4) and a legacy world must keep reading 20 loam.

On a `trade.yieldStructures` world, a structure whose `LocatedYields` is non-empty does **not** also pay
its `FlatYieldPerTurn` loam: `LoamProduction.For` takes a `locatedYieldsActive` flag from
`LoamPhases.Production` (which holds the world and therefore the stamp) and skips the flat add for
those structures. One structure pays one reward, the one its design names. On a legacy world the flag
is false and the loam sum is today's.

### 4. P1 — the faucet names its sinks

The same change adds the `produce` faucet for located goods to `trade-foundation`'s economy report,
with its sinks named: banking (`banking-fact`), trade (`exchange`), lane loss (`logistics-flow`).
Until those later sinks exist, the report prints located stock as accumulating and names the owning
follow-ups — declared, not hidden. The territorial sink (P2) is `structure-upkeep`, a hard dependency:
a yield building never ships without its loam upkeep term (`empire-economy-ssot.md:197-201`: *"it pays
loam upkeep like everything else"*).

## Tunables

| Key | Home | Meaning |
|---|---|---|
| `bands.yieldBand.*` | `data/tuning/structure-seed.v{n}.json` (`empire-seed`) | Units per turn at the pin, per ordinal |

No yield number lives in `trade.v{n}.json` or in a seed.

## Numeric types

`long` yields, `checked` sums, scaled once through `ContentScale.Apply`. A per-turn yield is a
content-scaled magnitude (`int` exceeds its range by `Θ` 103,557 in whole units, CLAUDE.md table).

## Acceptance (contract)

1. On a `trade.yieldStructures` stamp, a sector with one active yield structure gains exactly its scaled
   yield in the warehouse each turn, or less at capacity (then a halt fact), and the gain appears as a
   stock delta with factKind `produce`.
2. On a legacy stamp, the same world's state hash matches today turn for turn, and `LoamStock` of a
   sector holding a soul conduit gains exactly its `FlatYieldPerTurn`.
3. On a `trade.yieldStructures` stamp, a soul conduit yields souls into the warehouse and adds no loam from
   its flat field; a structure with no located yields keeps its flat loam add.
4. A structure under first construction, or on an unowned sector, yields nothing; a structure mid-upgrade
   yields exactly what it yielded before the upgrade began.
5. Two sectors with identical buildings, band and stock, owned by different faction kinds, end the turn
   with identical located stock (principle 10).
6. Every `good` in every `LocatedYields` resolves in `LocatedGoodCatalog`, is not a `LegionPiece`, and is
   not Content-pending; a violating row is a load rejection (catalog-load test over the real corpus,
   asserting the rule for every row, never the row count).
7. The economy report shows the `produce` faucet with its named sinks.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Goods/LocatedYieldPhaseTests.cs` (new): items 1, 3–6.
- `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs`: a legacy-stamp replay of an existing scripted
  world with a soul conduit, hash-identical (item 2).
- Economy-report assertion in `trade-foundation`'s report test (item 7).

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/StructureCatalog.cs',
  'src/FusionRpg.Core/World/Goods/LocatedYieldPhase.cs',
  'gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs',
  'gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs',
  'gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedYieldPhaseTests.cs') -Session <active-session-id>
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q
```

## Structure

```
gk-core/src/FusionRpg.Core/World/StructureCatalog.cs          MODIFIED — LocatedYields
src/FusionRpg.Core/World/Goods/LocatedYieldPhase.cs   (new)
gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs       MODIFIED — skip flat loam for located-yield rows on the stamp
gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs           MODIFIED — passes the flag
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs           MODIFIED — one call in Production, stamp-gated
gk-data/packs/fusion/data/seed/structures/**                               regenerated by empire-seed (never hand-edited)
data/tuning/structure-seed.v{n+1}.json                yieldBand (empire-seed publishes)
tests/FusionRpg.Core.Tests/World/Goods/LocatedYieldPhaseTests.cs   (new)
```

## Boundaries and hard edges

- **Always:** yields through `LocatedProduction.Credit`; numbers from bands; stamp gate.
- **Ask first:** a structure that pays both a located yield and flat loam; yields of legion pieces
  without a recipe.
- **Never:** edit `gk-data/packs/fusion/data/seed/structures/**` by hand; remove `FlatYieldPerTurn` from the conduit's row
  (it would move every legacy world); a yield before `structure-upkeep` lands.
- **Hard edge — goldens.** Legacy worlds must not move (acceptance 2). A moved golden is a defect in
  this change, never a re-bless.

## Dependencies and interface

**Depends on:** `production-halt`, `essence-loop-read`, `warehouse-axis`, `structure-upkeep` (P2);
`trade-foundation` `world-stamp`, `stock-deltas`, `economy-report`; external `empire-seed` `band-reader`,
`structure-bands`, `trade-structure-rows` (the generator emits `locatedYields`).

| Exposed | Consumer |
|---|---|
| `StructureDef.LocatedYields` | `trade-surface` (sector panels), `trade-ai` (valuing a site), `counterparties` (clan production reads the same field) |
| `LocatedYieldPhase.Production` | `TurnEngine.Production` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn (Production), structures and corpus, economy (P1/P2), power scale.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check exits 1 on the crossing
    already recorded there.
[x] Read this session: trade-network-ideal §5, §8.6, §14; empire-economy-ssot §5; economy-principles
    P1-P2, P11, §12; ssot-power-scale §10.4; empire-seed-map band-reader, structure-bands,
    trade-structure-rows.
[x] decisions.md: phase-order row (no new phase here — a step inside Production); registry row.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file (see the session report).
[x] Verified against code: the loam flat add, G-B, the construction gate, the conduit's row, the
    Production steps, the absence of template structures.
[x] Surrounding sections read: StructureKind.Yield's doc; LoamProduction's W56 comment.
[x] Constraints tested, not assumed: legacy hash identity is acceptance 2, to be proven.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the conduit's loam/souls switch is stamp-gated here; the map's wording
    ("its yield becomes located souls") is kept and the mechanism stated.
[x] No population pinned: the corpus-load test asserts a rule per row.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one credit function; one yield field; flat loam untouched on legacy worlds.
[x] Registry row: the located-goods row lands with located-goods-registry; this module adds the P1
    faucet line to the economy report.
```

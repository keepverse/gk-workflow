# Spec: `need-vector`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `need-vector`, row 1 of the
[counterparties map](../counterparties-map.md) (wave 1). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.2 (a hub's demand is *"the number `INeedVector`
is missing today"*), §7.5, §7.7 (*"real `INeedVector` needs must exist first"*), §14b (*"`counterparties`
owns it"*). **Reconciled 2026-09-19** with `exchange` ask E-A10 and `trade-ai` ask T-A7 (§5, per-sector and
pure reads). Session record: `tasks/sessions/trade-network-idea-20260919.json`. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Replace the uniform stub with **one deterministic demand rule** that says how badly a faction wants one
more unit of each good, per-mille against a neutral 1000. It is the single source of demand: a hub's
local demand (`exchange`), every AI valuation (`trade-ai`), clan consumption (`clan-economy`) and
seasonal shocks (`trade-stories`) all read or feed it. It is never copied.

Success looks like: an enemy empire short of ice essence values an ice vein above a fire vein; a clan
drowning in its own climate's essence sells it cheaply and pays a premium for what its ground lacks; the
same inputs give the same vector on every machine; a faction whose stock equals its demand reads exactly
1000.

## Scope and non-goals

**In scope:** the widened `INeedVector` (a per-good read), the demand function and its registered
terms, the truth-side and belief-side adapters over one rule, wiring the vector into the AI's existing
`ValueMap` call, and the tuning keys.

**Non-goals:** prices (`exchange` `price-curve`); what an AI does with a want (`trade-ai`); located
stock itself (`sector-yield` `located-stock`); the treasury balance (`empire-treasury`); the seasonal
shock schedule (`trade-stories` `seasonal-demand-shocks`, which registers a term here). No stored
vector: it is recomputed from state every read.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The interface and its per-mille contract: `ForSlotKind`, `ForElement`, neutral 1000 | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:15-22` |
| The uniform stub, and it is the default whenever no vector is passed | `gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41`; `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:67` |
| `ValueMap.For` already accepts a vector and multiplies slot yield by both reads, in `long`, dividing by 1000 per factor | `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:59-64`, `:137-153` |
| Own ground is never fogged: the view already answers a live read of the faction's own loam stock | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:45-52` |
| The season index and its tunable count (a per-season array precedent: upkeep reads `Seasons.UpkeepMilli[season]`) | `gk-core/src/FusionRpg.Core/World/Turn/TurnCalendar.cs:32`, `:42`; `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:68` |
| A species carries a primary and an optional secondary element | `gk-core/src/FusionRpg.Core/Creatures/CreatureSpeciesCatalog.cs:17-18` |
| The one content-scale read for a magnitude (`long`, divide once) | `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15-20`, `:31` |

### Wiring gap

| Gap | Evidence |
|---|---|
| The only caller of `ValueMap.For` passes no vector, so the stub is always used | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:60` |

### Real gap

No per-good read; no demand derivation; nothing to derive from until `sector-yield` lands located stock
and `empire-treasury` lands the AI's banked stock.

## Design

### 1. The widened interface (a reviewed change to a Core contract)

```csharp
namespace FusionRpg.Core.World.Ai;

public interface INeedVector
{
    int ForGood(string goodId);                 // new: the one read every other read derives from
    int ForSlotKind(SlotKind kind);             // kept: mean of ForGood over the goods that slot kind yields
    int ForElement(ElementTypeId? element);     // kept: mean of ForGood over the goods of that element
}
```

`ForSlotKind` and `ForElement` stay answerable, so `ValueMap` and every existing test keep compiling and
keep their meaning. Both are **derived** from `ForGood` through `sector-yield`'s located-good catalog
(which goods a slot kind yields, which goods carry an element); a slot kind or element with no goods
reads 1000, the neutral value the stub returns today. One source, three reads.

`UniformNeeds` stays as the vector for a **legacy-stamped** world (below) and for tests.

### 2. The rule

For faction `f`, good `g`, at turn `t`:

```text
stock(f, g)  = Σ located stock of g in sectors f holds        (sector-yield located-stock)
             + treasury balance of g                           (empire-treasury; 0 for player and clans)
demand(f, g) = Σ over registered demand terms  term(f, g, t)   (§3), in value-normalised units
want(f, g)   = 1000 × (demand + k) / (stock + k)
k(f)         = max(1, needs.smoothingUnits × scaleMilli(f) / 1000)   scaleMilli(f) = the content-scale read at
                                                                     f's seat sector with the lowest ordinal id
                                                                     (1000 for a faction holding no seat)
```

- `want` is exactly 1000 when `stock == demand`; it falls as stock rises and rises as demand rises
  (monotone both ways); `k > 0` removes the divide-by-zero at empty stock. The value at zero stock,
  `1000 × (demand + k) / k`, is a **derived bound**, not a cap: it moves with demand.
- **`k` is scaled like demand and stock (PS-5; corrected by the 2026-09-20 audit).** The first draft used a
  flat `k` against scaled `demand` and `stock` (§3). At deep `Θ` a flat `k` shrinks toward nothing relative to
  both, so the curve's shape — how sharply an empty stock reads — would drift with content depth, a flat
  constant facing a scaling quantity (the hidden-ceiling shape PS-8 names). With `k` on the same read, `want`
  is Θ-invariant: scaling every term by one factor leaves every `want` unchanged (acceptance 10).
- `long` throughout, `checked`, multiply before the one division; the result narrows to `int` with a
  checked cast. Because `k` scales with demand, `(demand + k) / k` no longer grows with `Θ`; it grows only with
  a faction's holdings (sectors × climate term + members × species term, over one sector's smoothing). The
  narrowing therefore throws only for a faction whose demand exceeds about two million smoothing units — a
  derived bound that throws, never a clamp. *(The first draft said "the loader rejects a tuning whose
  worst-case demand exceeds that"; no loader can know a world's holdings, so that check could not exist.)*
- The player's banked wallet is **not** stock here: it has no location and the step cannot read it
  (economy-principles P13). A player's want therefore measures what is on the map, which is what hub
  demand and the AI's model of the player need.

### 3. Demand terms (open for extension, closed for modification)

`demand` is a sum of registered `IDemandTerm`s. A new term registers into the one function; it never
writes a price or a second demand table.

| Term | Reads | Tuning | Why this shape |
|---|---|---|---|
| **climate** | per held sector with climate `c`: every element-typed good **except** `c`'s own | `needs.climateDemandUnits` | P12: a sector has its own climate's essence and lacks the rest, so a clan's craving is computed, never authored (`world-graph-ideal.md` §8.2) |
| **species** | per member of the faction's entities: goods of the species' primary and secondary element | `needs.speciesDemandUnits` | fusion and equipment appetite follows what the faction fields; keyed by **element**, a closed vocabulary, never by species id (species are a population) |
| **season** | the turn's season index | `needs.seasonDemandMilli[season]`, one entry per season | multiplies the sum of the terms above; array length must equal `Seasons.Count` (load rejection otherwise), the upkeep precedent |
| **planned sinks** | **registered later by `empire-goods-sinks`**: the goods cost of the cheapest structure the faction can build next, looked ahead `needs.reserveTurns` turns | `needs.reserveTurns` (owned by the registering module) | a faction wants what its next build needs before the build is refused |
| **seasonal shocks** | **registered later by `trade-stories` `seasonal-demand-shocks`** | theirs | their ask on this map |

This module ships the first three terms. The last two are registered by modules that depend on this
one, so the dependency arrow never points back (`empire-goods-sinks` depends on `need-vector`, not the
reverse). `clan-economy` reads the vector; it registers no term, because a clan's consumption **is**
its demand being met, not a second demand.

Every per-sector term is scaled by that sector's content scale, the same read `sector-yield`
`essence-loop-read` applies to faucets and capacities (`ContentScale.Milli(MapLevel(DangerBand))`), so
demand and stock are in the same value-normalised units (PS-5, umbrella invariant 7). A term registered
later ships behind its own capability flag.

### 4. Truth side and belief side — one rule, two adapters

- **Truth side** (inside `Step`, for `exchange`'s hub demand and `clan-economy`): `NeedVector.For(world,
  factionId, turn)` reads `WorldState`.
- **Belief side** (outside `Step`, for AI policies): `NeedVector.For(view)` reads `IWorldView`. It needs
  only the faction's own stock and own members, which are never fogged; the view gains
  `OwnGoodsStock(sectorId, goodId)` and `OwnTreasury(goodId)` beside `OwnLoamStock`
  (`IWorldView.cs:45-52`) for exactly that reason.

Both call one internal `NeedVector.Compute(inputs)` over a plain input record. The two adapters only
gather inputs, the `SupplyReach` precedent (`spec-ai-commander.md` §Believed supply). A test proves they
agree for the faction's own stock.

### 5. Per-sector and pure reads (answers `exchange` E-A10 and `trade-ai` T-A7, 2026-09-19)

`exchange` prices a hub against **its own sector** (E-A10), and `trade-ai` needs a pure want read, a reserve
and an estimate of another faction's want (T-A7). All of them are reads of the one rule in §2 — no second
demand table:

```text
component(f, s)   = the sectors f holds that are reachable from s through f's own traversable ground —
                    SupplyReach.From(seeds = {s}, links, traversable)       (SupplyReach.cs:24, the one traversal)
DemandAt(f, s, g) = Σ registered terms over component(f, s) only            (climate per held sector in it;
                                                                               species per member standing in it;
                                                                               season multiplies)
ReserveAt(f, s, g)= the planned-sinks term's share for component(f, s)      (0 until empire-goods-sinks registers it)
WantAt(demand, stock, k) = 1000 × (demand + k) / (stock + k)                (§2's formula, exposed pure; for a
                                                                              per-sector read k takes that sector's
                                                                              scale — audit 2026-09-20)
EstimateFor(view, other) = Compute over the viewer's BELIEF of `other`      (believed held sectors and seen members;
                                                                               stock not seen reads 0; flagged Estimated)
```

- **Why the supply component.** Goods at a hub serve only what can reach them through the owner's own
  ground; a severed pocket is its own market. The traversal is `SupplyReach`'s, so this adds no rule.
  `Σ over a faction's components of DemandAt ≤ demand(f, g)`, with equality when every member stands on held
  ground (members on lanes or abroad count toward the faction but toward no component) — asserted, not a
  count.
- **Units.** Value-normalised, per-sector scaled (§3), so `exchange`'s curve and `DemandAt` agree (PS-5).
- **`EstimateFor` never reads truth.** It runs the same `Compute` on belief-side inputs (`IWorldView`); it
  lives under `World/Ai/` with the other belief adapter (§4). Own-faction reads stay unfogged.
- **Inside `Step`**, `DemandAt`/`ReserveAt` are truth-side and read hashed state only (P13); the component
  is recomputed per call from the same inputs `SupplyGraph` recomputes each turn (no cache — SupplyGraph's
  own stance, `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:5-11`).

### 6. Wiring and the stamp

- `FrontierRulesPolicy` passes `NeedVector.For(view)` into `ValueMap.For` (`FrontierRulesPolicy.cs:60`)
  when the world's stamp grants `counterparties.needs`; a legacy world keeps `UniformNeeds`. AI changes
  never break a replay (replay never re-runs a policy, `spec-ai-commander.md` §The commander loop), but a
  legacy world keeps its AI too — "old worlds keep their rules" (ideal §14 D-C).
- The capability flag `counterparties.needs` is added to `trade-foundation` `world-stamp`'s closed flag
  registry by this module's change — in **`counterparties` wave 1**, whose **one** `RulesetVersion` bump it
  shares with `counterparties.roster`, `.diplomacy` and `.treasury` (round 6 C1: a flag never spans waves and
  a wave takes exactly one bump; row 15 of [../landing-order.md](../landing-order.md) §2).

## Tunables

`data/tuning/trade.v{n}.json`, added through `gk-core/tools/tuning/publish.py trade --add-key` (the file is
created by whichever trade module lands first, never hand-edited):

| Key | Unit | Starting shape (by principle) |
|---|---|---|
| `needs.smoothingUnits` | base (unscaled) units, scaled at read by the faction's seat-sector content scale (§2) | one turn of a single sector's base yield — small enough that a real shortage reads far above 1000 |
| `needs.climateDemandUnits` | units per held sector per turn | equal to one sector's base yield, so a sector demands roughly what another sector could supply |
| `needs.speciesDemandUnits` | units per member per turn | a fraction of a sector's yield, so a large army shifts demand without swamping climate |
| `needs.seasonDemandMilli` | ‰ per season, array | 1000 for every season at first; seasons diverge only when `trade-stories` shocks are tuned |
| `needs.reserveTurns` | turns | 3 (the AI's `ExploreTurns` horizon, `spec-ai-commander.md` §The decision layer); added by `empire-goods-sinks` with its term |

A missing key is a load rejection (tunables-ssot T5). Values are decided by principle and published as
tunables, never asked of the owner.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| stock, demand, term outputs | `long`, `checked` | value-normalised magnitudes scale with `P(Θ)`; `int` per-mille overflows at Θ 3,213 (PRINCIPLES §5) |
| `want` | `int` at the interface, computed in `long`, narrowed `checked` | the interface is per-mille and already `int`; the loader-derived bound makes the narrowing provably safe |

## Acceptance (contract)

1. **Pure.** Same `(world or view, faction, turn)` gives a byte-identical vector; no wall clock, no
   `System.Random` (inherits `WorldDeterminismGuardTests`, `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-48`).
2. **Monotone.** Raising a faction's stock of `g` never raises `want(g)`; raising any term's demand for
   `g` never lowers it. Property test over generated inputs.
3. **Neutral point.** `stock == demand` reads exactly 1000 for any `demand ≥ 0`.
4. **One source, three reads.** For every slot kind and element, `ForSlotKind`/`ForElement` equal the
   mean of `ForGood` over that kind's or element's goods (joined through the located-good catalog), and
   read 1000 when the set is empty.
5. **Truth equals belief** for the faction's own stock and members.
6. **Terms compose by registration.** Registering a test term that adds demand to one good changes that
   good's want only; no term can write a price (a source scan finds no price type referenced under
   `World/Trade/Needs/`).
7. **Legacy.** A legacy-stamped world's AI receives `UniformNeeds`; its command log and hash are
   byte-identical to today on the shipped scenarios.
8. **Tuning.** A missing key, or a season array whose length differs from `Seasons.Count`, is a load
   rejection naming the key.
9. **Per-sector reads (§5).** For a faction whose members all stand on held ground, the sum of `DemandAt`
   over its supply components equals its faction-wide demand, per good; severing a component moves demand
   between components and never creates any. `WantAt(d, s, k)` equals §2's `want` for every input.
   `EstimateFor(view, other)` reads no `WorldState` (the `World/Ai/` scan).
10. **Θ invariance (added by the 2026-09-20 audit).** Multiplying every sector's scale read by one factor
    (so demand, stock and `k` all scale together) leaves every `want` unchanged, within one per-mille of
    integer rounding — property test over the factor.

No assertion pins how many goods, terms or sectors exist; tests assert the join and the arithmetic.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Needs/NeedVectorTests.cs` (new): neutral point, monotonicity
  (property), derived reads, term registration, overflow bound rejection.
- `gk-core/tests/FusionRpg.Core.Tests/World/Ai/`: `ValueMap` with a real vector ranks a wanted element's vein
  above an unwanted one; the legacy path passes `UniformNeeds`.
- Truth/belief agreement on a `trade-foundation` `synthetic-graph` world.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs','gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','tests/FusionRpg.Core.Tests/World/Trade/Needs/NeedVectorTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.Needs|FullyQualifiedName~World.Ai"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldDeterminism"
```

## Hard edges

- **Interface widening.** `INeedVector` is a Core contract with a guard-scanned consumer folder
  (`World/Ai/` may not mention `WorldState`). The belief adapter lives under `World/Ai/`, the truth
  adapter under `World/Trade/Needs/` (new), so the guard stays green.
- **Stamp gate.** The AI wiring is behind `counterparties.needs`; landing it ungated would change every
  shipped world's AI behaviour mid-campaign.
- **Campaign scenarios.** `TwoHearthsCampaignTests` and `TwoHearthsTenTurnProbeTests` observe AI
  behaviour; a trade-stamped fixture may move them. They are run and reported, never assumed
  (`spec-ai-commander.md` §Momentum point 4).

## Dependencies

| Consumes | From |
|---|---|
| Located stock per (sector, good); the located-good catalog (slot kind → goods, element → goods); the content-scale read | `sector-yield` `located-stock`, `located-goods-registry`, `essence-loop-read` |
| AI treasury balance | `empire-treasury` (a registered stock source; absent → 0) |
| The capability flag registry | `trade-foundation` `world-stamp` |

| Exposes | To |
|---|---|
| `INeedVector.ForGood`, `NeedVector.For(world, faction, turn)` | `exchange` `price-curve`/`order-book` (hub demand), `clan-seeding` (personality) |
| `NeedVector.DemandOf(world, faction, good, turn)` — the `demand` term of §2, in value-normalised units | `clan-economy` (consumption), `exchange` (the curve's demand input) |
| `NeedVector.For(view)` | `trade-ai` `deal-valuation`, `ai-bidding`; `FrontierRulesPolicy` |
| `NeedVector.DemandAt`, `ReserveAt` (truth side, per sector) | `exchange` `price-curve`, `order-book` (E-A10) |
| `NeedVector.WantAt` (pure), `EstimateFor(view, other)` (belief side) | `trade-ai` `deal-valuation`, `ai-bidding` (T-A7) |
| `IDemandTerm` registration | `trade-stories` `seasonal-demand-shocks`; `empire-goods-sinks` (planned sinks) — both depend on this module |

## Contradictions found

1. **Map tunable `needs.demandBySpecies`** (map *Tunables*) would key a tunable by species id — a
   population, not a closed vocabulary (validation-ssot; DESIGN-GATE §3 rule 7). Resolved here: the
   species term keys by element. Propagated to the map's tunables line.

## Open questions

None for the owner. Starting values are decided by principle (ideal §13).

## Design-gate checklist

```
[x] Subsystems: world AI (ValueMap, FrontierRulesPolicy, IWorldView), economy (demand, PS-5), tunables,
    numeric types.
[~] Session boundary: trade-network-idea-20260919 (paths include docs/architecture/trade-network/**).
    session-boundary-check.py not re-run for this docs-only file; the record's notes list the known
    crossings with broad worktree lanes.
[x] Read this session: DESIGN-GATE §1 Economy, World map and tunables rows, §2, §5; PRINCIPLES;
    counterparties-map; trade-network-map; trade-network-ideal §3, §7, §8.6, §10-§14b;
    spec-ai-commander (whole); empire-resource-ssot; economy-principles P1, P2, P13, P14, §12-§13;
    empire-economy-ssot §2, §3, §6; tunables-ssot §1-§3; sector-yield-map §1-§2.4, §2.9.
    Not read: world-map-runtime-ideal and its specs (FE map plane; nothing here renders).
[x] decisions.md: no lock covers needs; Empire resource registry row (:108) respected (no new quantity).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: INeedVector, UniformNeeds, ValueMap.For/YieldOf, FrontierRulesPolicy:60,
    IWorldView.OwnLoamStock, TurnCalendar, ContentScale read directly.
[x] Surrounding sections read for every quoted rule (§7.2, §7.7, §14b rows).
[x] No "moves goldens" claim made; campaign scenarios are named to run and report.
[x] No §2 invariant contradicted.
[x] Correction propagated: species keyed by element, in the map's tunables line.
[x] No population pinned: goods, terms and sectors are readings; the neutral 1000 is the interface's own
    constant.
[x] No event-refreshed cache: the vector is recomputed per read.
[x] No ordering fixed: terms sum; order-independent by construction.
[x] No actor magnitude produced or consumed.
[x] No SOLID-violating path: one rule, two input adapters; ValueMap reused, not forked.
[ ] Registry row: the "no price under World/Trade/Needs" scan is a local test; no enforcement-registry
    row proposed yet.
```

## Audit 2026-09-20

Fixed here: the smoothing term `k` was flat while demand and stock are content-scaled (PS-5), so `want`'s shape
drifted with `Θ`; `k` now takes the same scale read and a Θ-invariance acceptance is added. The "loader rejects a
worst-case demand" claim was impossible (a loader cannot know holdings) and is replaced by the true bound: a
checked narrowing that throws only on holdings-driven demand of about two million smoothing units. Checked and
clean: one rule with two input adapters (truth and belief); demand terms register, never write a price; the
species term is keyed by element, never by species id (a population); no stored vector; legacy worlds keep
`UniformNeeds`. **Verification boundary:** the `core-world-trade-counterparties` owner boundary
(`spec-empire-goods-sinks.md` *Audit 2026-09-20*) covers `World/Trade/Needs/**`; the `World/Ai/` edits stay on
`core-fallback`.

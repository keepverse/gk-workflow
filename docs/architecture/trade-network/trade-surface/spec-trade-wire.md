# Spec: `trade-wire`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 2, wave 1). Every `file:line` below was opened this session. Docs only.

## Objective

One fog-correct read of everything trade shows on the world stage, and one sealed FE view contract for
it, so no trade surface fetches its own numbers or recomputes a provider's fold. The contract follows
world-stage's `world-contract` / `world-wire` split: Server projection → `FusionRpg.Contracts` DTO →
`lib/bus` hook → `contract/adapt.ts` view type → pieces.

Success looks like: the trade panel, status strip, forecast chip, flow lens and treaty layer all read one
`WorldTradeView` (plus one counterparty read), a foreign warehouse is never shown as truth, and an
unowned sector's trade fields are "not yours", never a zero.

## Locked anchors

- **The surface reads, the domain decides** (map §3 principle 9). This module projects provider state
  and folds; it never computes a flow, loss, price, access level or forecast.
- **Fog.** Own warehouses are truth; foreign hubs are believed state with an intel age (trade-network
  ideal §8.5 *"plan on believed prices and lane states; settle on the truth"*). Report lines and
  projections use the existing visibility rule, `VisibleTo` (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576`),
  which notification-ssot's ask moves into Core; it is reused, never re-implemented.
- **Null is "not yours", zero is a real zero.** The lens-2 lesson
  (`gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts:48-55`: the lens renders `—`, never `0`, for
  ground that is not yours).
- **Every magnitude declares its unit** (GG-46; `gk-web/web/fusion-rpg-web/src/contract/types.ts:66-67`: no
  overload of `formatMagnitude` accepts a bare number).
- **Asked for, not always paid for.** Lens 4's lifelines are a query flag because they cost server time
  (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:50-52`); the trade read is a separate endpoint for the same
  reason, so the world-state poll does not grow with goods × sectors.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| World state read with a viewer faction | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:37` (`/{worldId}/state?asFaction=`) |
| Report-line visibility by audience, sector and intel state | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576`; static-fact prefixes `:583-587` |
| Owner-only numeric field precedent | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:177` (`LoamNet`), read as null-when-not-yours by `lensCatalog.ts:48-55` |
| Lane fields on the wire | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:292-301` (`Width`, `HazardMilli`, `WardLevel`) |
| World read hooks and the adapter | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:593` (`useWorldState`), `:621` (`useWorldTurnReport`); `gk-web/web/fusion-rpg-web/src/contract/adapt.ts` |
| Sealed unit union | `gk-web/web/fusion-rpg-web/src/contract/types.ts:67-84` |

### Real gap

No trade DTO, endpoint, hook or view type exists; `WorldDtos.cs` has no trade field. Every provider read
model this contract projects is itself unbuilt (`sector-yield`, `logistics-flow`, `exchange`,
`counterparties`, `fleet`), so the contract lands in slices as each provider does (Design 4).

## Design

### 1. Endpoint

`GET /api/world/{worldId}/trade?asFaction=<id>` in `src/FusionRpg.Server/TradeEndpoints.cs` (new), mapped
in the same route group as `WorldEndpoints`. It loads the committed world once, builds the viewer's
believed view the way `/state` does, and returns `WorldTradeDto`. It calls provider folds only; a guard
test asserts the file references no provider *mutator* type.

### 2. The DTOs (`src/FusionRpg.Contracts/TradeDtos.cs` (new))

```csharp
public sealed record WorldTradeDto(
    int Turn,
    IReadOnlyList<TradeSectorDto> Sectors,          // only sectors with a trade structure the viewer can see
    IReadOnlyList<LaneFlowDto> Lanes,               // only lanes the viewer can see
    TradeStatusDto? Status,                         // the viewer's own fold (trade-status); null before unlock
    ThrottleForecastDto? Forecast,                  // the viewer's own forecast (throttle-forecast); null before unlock
    IReadOnlyList<CounterpartyDto> Counterparties,  // known factions only (treaty-screen)
    BlockedDemandDto? BlockedDemand,                // blocked-demand; null before W4
    TradeCapabilitiesDto Capabilities);             // trade-unlock's flags for the viewer
// TradeSectorDto also gains an own-only `Policy` field in W4 (trade-policy-editor).

public sealed record TradeSectorDto(
    string SectorId, string? StructureRoleId, int? HubTier,        // round 4: SectorFeatures.TierOf(sector, trade), 1..4; the name is the row/variant display name (was HubLevel)
    IReadOnlyList<WarehouseLineDto>? Warehouse,     // null = not yours
    MagnitudeDto? WarehouseCapacity,                // own capacity axis — a real cap, gauges may fill
    MagnitudeDto? ClearingCapacity,
    bool? Halted,                                   // null = not yours
    IReadOnlyList<BelievedQuoteDto>? BelievedQuotes,// foreign hub only
    int? IntelAgeTurns,                             // foreign hub only; 0 = watched this turn
    string? ViewerAccessLevelId,                    // foreign hub only; exchange trade-access LevelAt (round 4: tier-gated)
    string? MissingBuildingId);                     // foreign hub only; the building the viewer lacks for market, null if none

public sealed record LaneFlowDto(
    string LaneId, bool Known,                      // false => every field below is null ("unknown", never 0)
    MagnitudeDto? Flow, int? UtilisationMilli,      // bounded ratio 0..1000
    string? BottleneckReasonId, MagnitudeDto? Lost, string? LossCauseId);
```

`MagnitudeDto` is the existing magnitude wire shape. `CounterpartyDto`, `TradeStatusDto` and
`ThrottleForecastDto` are defined by their owning modules (`treaty-screen`, `trade-status`,
`throttle-forecast`) and live in the same file.

### 3. The goods unit family

Goods quantities are **value-normalised** (umbrella invariant 7; PS-5), so they are not `count` and not
`gameUnits`. This module files one reviewed widening of the sealed `UnitClass` union — `goodsUnits` —
through world-stage `world-numbers` and [spec-magnitude-and-units.md](../../../design/spec-magnitude-and-units.md)
§3, with its renderer rule (a goods quantity prints with the good's display name from `trade-lexicon`).
Until that lands, no goods magnitude ships on the wire. **The same widening carries a value unit**
for `trade-status`'s headline totals, which are `Σ qty × ValueOf` across goods, never a sum of unlike
goods (audit 2026-09-20, `trade-status` §1); one reviewed change, two members. This is the contract-side home of the decision the
map lists under `trade-status`; `trade-status` consumes it.

### 4. Slices, in provider order

| Slice | Fields | Unblocked by |
|---|---|---|
| W1 | `Sectors` (own warehouse, capacity, halt), `Capabilities` (round 4: the milestone flags **and** the viewer's building tiers per ladder, `trade-unlock` §2) | `sector-yield` (`warehouse-axis`, `located-stock`, `production-halt`, `bank-points`); `trade-unlock` |
| W2 | `Lanes`, `Status` | `logistics-flow` (`lane-flow`, `lane-loss`, `logistics-facts`) |
| W3 | `Forecast` | `logistics-flow` `forecast-facts` |
| W4 | foreign `BelievedQuotes`, `IntelAgeTurns`, `ViewerAccessLevelId`, `ClearingCapacity`; own `Policy` (`trade-policy-editor`); `BlockedDemand` (`blocked-demand`) | `exchange` (`exchange-hub`, `price-curve`, `trade-access`); `trade-ai` `trade-intel` for believed quotes |
| W5 | `Counterparties` | `counterparties` (`diplomacy-facts`, `diplomatic-stance`, `relation-facts` band snapshot); `exchange` `treaty-lifecycle` |

Each slice adds fields; no slice renames one. A field whose provider has not landed is absent from the
DTO, not defaulted.

### 5. Web

`useWorldTrade(worldId, asFaction)` in `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts`; `adaptWorldTrade` in
`contract/adapt.ts` producing `WorldTradeView`. Invalidation triggers (DESIGN-GATE §2.16): **turn
advance** (the commit's `Advanced`), **own command filed** (policy/answer commands change the forecast),
**trade unlock edge** (capabilities change the key set of what is returned), **reconnect / save switch**,
and — from slice W4, because `blocked-demand` reads it — **material shelf change** (a fusion, salvage or
expedition collect changes what is blocked without a world turn). Each trigger has a test.

## Contract exposed

| Member | Consumer |
|---|---|
| `GET /{worldId}/trade`, `WorldTradeDto`, `useWorldTrade`, `WorldTradeView` | every trade-surface FE module |
| `goodsUnits` unit class (once accepted) | `trade-status`, `trade-panel`, `flow-lens`, `blocked-demand` |

## Acceptance (contract level)

1. **Fog:** for any fixture world and viewer, a foreign faction's warehouse stock never appears; a foreign
   hub appears only with `BelievedQuotes` and an `IntelAgeTurns`; a lane the viewer cannot see has
   `Known = false` and null fields.
2. **Null is not zero:** an unowned sector's `Warehouse` and `Halted` serialise null; a test distinguishes
   an owned empty warehouse (`[]`) from not-yours (`null`).
3. **Units:** every magnitude field carries a unit class; a test walks the DTO and fails on a bare number
   for a magnitude field.
4. **Read-only:** the endpoint writes nothing and moves no world hash (hash before == after).
5. **Round-trip:** a fixture turn's DTO round-trips through `adaptWorldTrade` byte-stable (golden fixture).
6. **Cache triggers:** each of the five invalidation triggers refetches; the unlock edge test flips
   capabilities with no turn advance and asserts a refetch; the shelf test fuses with no turn advance.

## Test plan and verification boundary

- `FusionRpg.Server.Tests` (endpoint fog, read-only, unit walk) — `server-fallback`; DTOs —
  `contracts-fallback`.
- Web adapter and hook-trigger tests (vitest). **Gap, stated:** no `web/` boundary exists in
  `gk-core/scripts/verification-boundaries.v1.json` (grep count 0; its `projects` map is `.csproj`-only);
  report it, never compensate with the full suite.

## Hard edges

- The fog rule is moved into Core by notification-ssot's ask; this module calls it, never copies it.
- `UnitClass` widening is a reviewed change on `spec-magnitude-and-units.md`; never a local formatter.
- Never add trade fields to `WorldSectorDto` (the poll would pay for them every refresh).

## Dependencies

Providers in Design 4; world-stage `world-numbers` (unit class ask); notification-ssot `world-notify-source`
(fog rule move to Core); `trade-unlock` (capabilities).

## Boundaries

- **Always:** absent until provided; null for not-yours; units on every magnitude.
- **Ask first:** a push channel for trade (today a read after commit suffices).
- **Never:** a provider mutator in the endpoint; FE derivation of access, price or forecast.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world wire/contract, fog, magnitude units, Data read (no SQL added here).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: DESIGN-GATE UI + World map rows (world-stage specs for contract/wire/numbers by heading),
    game-gui-principles GG-15/17/46, spec-magnitude-and-units via UnitClass in code.
[x] decisions.md: Game GUI (:110). No lock on trade wire.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: VisibleTo, LoamNet, lane DTO, state route, UnitClass union.
[x] Surrounding sections read (VisibleTo doc comment, lens-2 comment).
[x] No untested constraint claimed; read-only is an acceptance test.
[x] No §2 invariant contradicted (SQL stays in Data; standalone: pure server read).
[x] Correction propagated: goods unit decision placed here; map §6.3 note updated in the same change.
[x] No population pinned.
[x] Event-refreshed cache: five triggers enumerated including the unlock (key-set) edge and the
    material-shelf edge blocked-demand adds; each tested.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one fog rule, one magnitude renderer, provider folds only.
[ ] Registry row: "trade endpoint references no provider mutator" guard needs a registry row when built.
[x] Round 4 reconciliation (2026-09-19): HubLevel -> HubTier (a structure has no level; the tier is
    trade-foundation sector-features' slot tier); MissingBuildingId; building tiers in Capabilities. Cache: a building completing or being
    lost changes the key set, and it only happens at a turn commit, so the turn-advance trigger covers it.
```

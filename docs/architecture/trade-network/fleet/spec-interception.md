# Spec: `interception`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`). Every `file:line` below was opened
in this session. Module id `interception`, row 6 of the [fleet map](../fleet-map.md) (wave 3; depends on
`trade-route-order`, `carried-goods`, `legion-build` `field-battle-kinds` and `role-aware-placement`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §8.3 (*"A hostile legion meeting a caravan
triggers the kind-agnostic `Sector`/`Lane` battle … No special case"*), §14b (*"Goods on a legion that
loses a battle follow `cargo-fate`"*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

A caravan that meets a hostile force fights an ordinary battle. This module adds **nothing to how the
battle starts or resolves**; it owns the one thing a caravan adds to the outcome — what happens to its
**carried goods** — as a pure classification applied inside the world's one outcome-application point:

| Outcome for the caravan's side | Carried goods |
|---|---|
| Not in the outcome, or the battle was refused | Unchanged |
| Survived (won, withdrew, or routed) with bearer capacity ≥ carried | Unchanged |
| Survived with bearer capacity < carried (bearers died) | The excess **spills** |
| Destroyed | Everything **drops** |

Where spilled or dropped goods go is `goods-cargo-fate`'s. Until `legion-build` routes `Sector`/`Lane`
battles into the engine, every such battle is refused and this module's live behaviour is the first row —
asserted, so the change is visible when it comes.

## Locked anchors

- **One battle engine; a mode owns its loop, never a mechanism** (`battle-engine-ssot.md` §1-§2, §5). A
  caravan's fight is resolved by whatever resolves `Sector`/`Lane`; this module is not a battle mechanism.
  Answering §5: it is not in the responsibility register (§3) because it changes no battle number; it
  **resolves nothing and decides nothing** in battle; it is world loop — what an outcome means for goods
  on the map; it extends `BattleApplication.Apply`, *"the world's half of the combat seam … there is
  exactly one of it"* (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:3-7`); every mode that puts a
  legion carrying goods in a world battle gets it; it is deterministic (pure over the outcome).
  **Register row 20 (*"Victory / defeat and settlement — what the battle meant, what persists, what is
  lost"*, `battle-engine-ssot.md` §3b) — why this is not a second owner of it** (audit 2026-09-20; the first
  draft did not address the row). The engine's settlement output is the outcome the world receives: which
  sides are destroyed, withdrawn or routed, and each side's surviving members (`side.Survivors`). This module
  reads only that output. Carried goods are **world** state that no battle ever sees (they are not a
  combatant, a resource pool or an item in the battle); what an outcome does to them is the world's
  application of the settlement, in the one application point, exactly as `scoped-inventory` `cargo-fate`
  applies an outcome to item cargo Data-side. If the owner ever reads row 20 as covering carried cargo,
  this classification moves behind the engine's settlement seam unchanged — it is already a pure function of
  the outcome.
- **`BattleKinds` is a closed vocabulary; add nothing** (`gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:6-22`).
- **Placement is `legion-build`'s** (`role-aware-placement`: bearers take no cell). A caravan of only
  bearers fields nothing; how an empty side resolves is that module's contract.
- **Rout is the shipped rule**: a routed force falls back and loses exactly one turn of orders
  (`BattleApplication.cs:37-48`; `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:165-178,229-235`). A
  standing order's emitted command is dropped exactly as a hand order is.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Lane meeting → `Lane` request; sector contact → `Sector` request | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:145-156,276-286` |
| The one resolver refuses every non-district kind with a winnerless outcome (T20's feature-absence guarantee) | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:13-25,101-104` |
| An outcome with no sides leaves the world unchanged | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:14` |
| A refused battle still writes one report line, winner `none` | `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:76-80` |
| Destroyed sides leave the map; survivors' members are replaced by `side.Survivors`; routed sides fall back | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:33-48` |
| A destroyed side's removal passes `carried-goods`' seam (added by that module) | `spec-carried-goods.md` §5 |

### Wiring gap

`Sector`/`Lane` battles resolve to no outcome (`DistrictAssaultResolver.cs:101-104`) — closed by
`legion-build` `field-battle-kinds` (its §5.16). This is unfinished wiring with a named owner, not a
wall.

### Real gap (this module closes it)

The carried-goods classification of an outcome, the spill rule, and the caravan battle fact tokens.

## Design

### 1. Classification (pure)

```
CarriedGoodsOutcome.Classify(entityBefore, side) -> Keep | Spill(goods) | Drop(goods)
  side.Destroyed                                   -> Drop(all carried)
  capacityAfter = CarriedGoods.Capacity(entityBefore with Members = side.Survivors)   // flat load units
  Σ Load ≤ capacityAfter                           -> Keep
  else excess = Σ Load − capacityAfter             -> Spill:
    spillLoad_g = floor(excess × Load_g ÷ Σ Load), remainder one unit at a time in good-id order
    spillQty_g  = min(Qty_g, ceil(Qty_g × spillLoad_g ÷ Load_g))
    the survivor keeps (Qty_g − spillQty_g, Load_g − spillLoad_g)
    if the survivor's kept Qty_g is 0, the entry is removed and its whole Load_g is freed
      (the carried-goods invariant: no entry with Qty 0 or Load 0 is ever stored)
```

Capacity is flat in load units and every parcel carries its own load (`spec-carried-goods.md` §1, §3), so
the test needs no scale read: a legion that lost no bearer never spills; a full caravan that loses a
fifth of its bearers spills a fifth of its load; a half-empty one may spill nothing. Quantities round
**up** into the spill, so the survivor never keeps goods its bearers cannot carry.

- **Excess split:** pro rata across goods by load, remainder in good-id order — deterministic and
  independent of the order goods were loaded. Products are `checked` `long`, multiplied before dividing.
- Withdrawn and routed sides keep their members' fate from `side.Survivors`, so they go through the same
  capacity test; routing itself never moves goods.

### 2. Where it runs

Inside `BattleApplication.Apply`, for each side whose entity carries goods, before the entity is
replaced (`BattleApplication.cs:33-48`): `Drop` is exactly the destroyed path, which already passes
`CarriedGoods.OnEntityRemoved`; `Spill` calls `goods-cargo-fate`'s placement function with the excess and
the entity's place, and writes the survivor with the reduced pool. One call site, the existing file, no
fork (the file's own header forbids a second one).

### 3. Facts

Added to `FleetFacts`: `caravan.intercepted` (a battle involved a legion on a trade-route order, whatever
the outcome — `trade-stories`' `trade.caravan.intercepted`), `caravan.lost` (it was destroyed —
`trade.caravan.lost`), `goods.spilled`. Each carries the battle id so a story fact keys on a durable id.

## Tunables

None. Capacity is `carried-goods`'; the battle is the engine's.

## Numeric types

`long`, `checked`; the pro-rata split multiplies before dividing and throws on overflow.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet|FullyQualifiedName~BattleReportingTests|FullyQualifiedName~RoutFallBackTests|FullyQualifiedName~RoutLifecycleTests"
python gk-core/scripts/guard-battle-responsibility.py
```

## Structure

```
src/FusionRpg.Core/World/Logistics/Fleet/Interception.cs   (new) — CarriedGoodsOutcome.Classify, split
gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs          MODIFIED — one call per side carrying goods
src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs      MODIFIED — tokens
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/InterceptionTests.cs (new)
```

## Testing strategy

- **Today's behaviour pinned:** a caravan meeting a hostile legion on a lane and in a sector yields a
  request of kind `lane` / `sector` (never a new kind), a winnerless outcome, unchanged carried goods and
  one report line naming winner `none`. When `field-battle-kinds` lands, this test is the one that changes
  on purpose.
- **Classification table:** synthetic outcomes (no resolver needed): destroyed → `Drop(all)`; survivors
  with all bearers → `Keep`; survivors missing bearers → `Spill(excess)` with the exact pro-rata split;
  routed with all bearers → `Keep` plus the shipped fall-back.
- **Spill proportions:** a legion that lost no bearer keeps everything wherever it fights; a full legion
  losing k of b bearers spills `ΣLoad × k / b` load units within integer rounding, and the kept load
  equals the new capacity exactly.
- **Conservation:** for every class, carried before = carried after + spilled + dropped, per good.
- **No zero entry survives a spill:** a spill that takes the whole quantity of a good removes the entry and
  frees all its load, even when the pro-rata load share was smaller (audit 2026-09-20 edge case: rounding
  `spillQty` up could otherwise leave `(0, positive load)`, which `WorldValidation` rejects).
- **Split independence:** permuting the order goods were loaded changes no spilled quantity.
- **Routed caravan:** its emitted command is dropped `entity.routed` for one turn; its loop phase is
  unchanged; it resumes the turn after (`RoutLifecycleTests` precedent).
- **Kinds closed:** a source scan of `src/FusionRpg.Core/World/Logistics/**` finds no `BattleKinds`
  member added and no new string passed as a request `Kind`.

## Boundaries

- **Always:** classify inside `BattleApplication.Apply`; hand goods on through `goods-cargo-fate`.
- **Ask first:** any caravan effect on the battle itself (placement, strength, a surrender rule).
- **Never:** a caravan battle kind; a battle number computed here; goods moved to the winner directly.

## Success criteria (contract)

1. A caravan's contact produces a `lane` or `sector` request, never a new kind.
2. Routed: goods unchanged; orders dropped for exactly one turn; the route resumes.
3. Destroyed: carried goods leave the entity in the same step and appear in `goods-cargo-fate`'s cache,
   per good.
4. Surviving with fewer bearers: exactly the excess over capacity leaves, split pro rata.
5. While the kinds are still refused, a caravan in contact keeps its goods and the report records the
   refused battle.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CarriedGoodsOutcome.Classify` | `goods-cargo-fate` (places what leaves) |
| `caravan.intercepted`, `caravan.lost` facts | `trade-stories` `trade-fact-source`; `trade-surface` notifications |

## Dependencies

`trade-route-order`, `carried-goods`; `legion-build` `field-battle-kinds`, `role-aware-placement`,
`stack-combatant` (casualties reach `Count`, which is what shrinks bearer capacity); `goods-cargo-fate`
for the spill's destination (the two land together in wave 3; the classification is testable alone).

## Hard edges

Touches `BattleApplication.cs`, a file every world battle crosses — one call, no rule changed; the
battle and turn goldens run once at module end.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: battle seam (world side only), world turn engine, economy (goods conservation).
[~] Session boundary: trade-network-idea-20260919 covers this path; check script not run by me.
[x] Read this session: battle-engine-ssot.md §1, §2 opening, §5; as spec-carried-goods.md.
[x] decisions.md: Battle engine is the SSOT row — answered in Locked anchors (§5's six questions).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding.
[x] Verified against code: refusal, empty-sides no-op, destroyed/routed application, report line.
[x] Surrounding sections read: BattleApplication in full to FallBack; DistrictAssaultResolver header.
[~] Constraints tested: none claimed.
[x] No §2 invariant contradicted; no battle mechanism added.
[x] Corrections propagated: the map's module text matches this spec.
[x] No population pinned; BattleKinds stays a closed vocabulary with nothing added.
[x] No event-refreshed cache.
[x] Orderings: goods load order does not affect the split (tested).
[x] No actor magnitude produced or consumed.
[x] No SOLID fork: the one outcome-application file, one capacity rule.
[ ] Registry rows: "no new BattleKinds from fleet" wants a guard row with its source-scan test. Named
    (audit 2026-09-20): invariant id `fleet-no-battle-kind`.
```

## Audit 2026-09-20

Fixed here: the battle-engine answer now addresses register row 20 (settlement) explicitly — this module
reads the engine's outcome and applies it to world state it owns, and owns no settlement mechanism; the spill
arithmetic no longer can leave a zero-quantity entry with load. Checked and clean: `BattleKinds` untouched;
routed and destroyed paths go through the existing application file; conservation per good.
**Verification boundary:** the `core-world-logistics-fleet` owner boundary (`spec-carried-goods.md` Hard
edges); the `BattleApplication.cs` edit stays on `core-fallback`, so the battle and turn goldens run once at
module end (Hard edges).

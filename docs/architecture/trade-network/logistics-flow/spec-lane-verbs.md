# Spec: `lane-verbs`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `lane-verbs`, row 8 of the
[logistics-flow map](../logistics-flow-map.md) (wave 3; depends on `lane-flow`, `lane-loss`,
`construction-chain`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §8.4 (*a
road-widening verb raises `Width`, so throughput is something you build*; *`WardLevel` keeps its siege
meaning and gains a logistics one … one field serves both*), §8.7 (the `ward` and `widen` kinds).
House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make lanes something you build. Two commands: `widen` raises a lane's `Width` (its throughput) and
`ward` raises its `WardLevel` (its protection — and, as before, its siege approach depth). Both are paid
in construction stocks — rubble and ironwork — from a sector the commander holds at one end of the lane,
on a price that rises with every level and never stops.

Success looks like: a verb with enough stock spends exactly its price and raises its field by one step;
a verb without enough spends nothing; no level is ever refused for being too high; and the one
`WardLevel` field keeps serving both siege and logistics.

## Locked anchors

- **Nothing raises `WardLevel` or changes `Width` today** — confirmed: no writer exists (the ideal's §5
  wiring gap; the only `WardLevel` reader is `gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:342-350`,
  used by `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs:116` and turned into depth at
  `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:170-171`).
- **The name `ward` is reserved for this verb** — `bind-warden` was named to avoid it
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:41-55`).
- **No hard ceilings (PS-8).** The price rises; the level is never capped
  (`docs/architecture/power/ssot-power-scale.md` §11).
- **A cost ladder owes a §10 row** — *"Every further cost ladder of this shape owes its own row here"*
  (`ssot-power-scale.md` §10.2 row 37; the arithmetic-ladder precedent is row 31, `TreeUnlockCost`).
- **Ownership-sensitive orders resolve in `Snapshot`** — the `build` precedent
  (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:421-423`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Width` (default 1000) and `WardLevel` on every lane, both `int`, hashed | `gk-core/src/FusionRpg.Core/World/WorldState.cs:259`, `:262`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:55-56` |
| The siege reader of `WardLevel`, with `checked` depth arithmetic | `gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:342-350`; `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:170-171` |
| The approach zone is chosen per cell from the depth, over a fixed board | `gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs:470-487` |
| Construction stocks on each sector | `gk-core/src/FusionRpg.Core/World/WorldState.cs:181`, `:187` |
| The admission gate and the Snapshot resolver slot | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:24`; `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:415-439` |

### Wiring gap

No writer for either field (above).

### Real gap (this module closes it)

Both verbs, their price ladders, the dual-reader guard, and a §10 row.

## Design

### 1. The commands

| Kind | Fields | Effect when it resolves |
|---|---|---|
| `widen` | `LaneId`, `SectorId` (the paying end) | `Width += lane.widenStep` |
| `ward` | `LaneId`, `SectorId` (the paying end) | `WardLevel += 1` |

`LaneId` is a new optional field on `WorldCommand`, `CommandPayload` and `WorldCommandRequest`, mapped
at both endpoint sites (the same five plumbing sites `auto-banking` extends; the two modules share the
change if they land together).

**Admission:** known kind; `LaneId` names a lane; `SectorId` is one of its two ends and the commander
holds it. **One exception, owned elsewhere:** a `widen` with no `LaneId` and a `SectorId` naming a
crossing anchor raises that anchor's crossing width (`rift-trade` ask A8). That arm's admission, price
(`crossing.widenCostCurve`) and state are `rift-trade` `crossing-leg`'s, resolved beside this resolver —
one verb, one resolver slot, no second kind. **Resolution** (in `Snapshot`, after `WardenResolver`, before `auto-banking`'s route
resolver): the same checks against the settled turn, then the price.

### 2. The price — a rising arithmetic ladder per stock

For a verb at current level `n`:

```
price(n).rubble   = first.rubble   + step.rubble   × n          // long, checked
price(n).ironwork = first.ironwork + step.ironwork × n
```

- `ward`: `n = WardLevel`.
- `widen`: `n = max(0, Width − 1000) ÷ lane.widenStep`, where 1000 is `Width`'s structural default
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:259`) — the level is read from the field, so no extra state is
  stored and an authored wide lane is priced as already widened.

`step > 0` for at least one stock is a load rule, so each level costs strictly more than the last — a
ladder, never a cap. Paid from the paying sector's `RubbleStock` and `IronworkStock`; if either is short
the verb is dropped with `stock.short` and **nothing** is spent (gate before write). An accepted payment
is recorded as `construct` stock deltas on the paying sector (`trade-foundation` `ledger-keys` §4 — the
kind the shipped build cost already uses), so the world-stock ledger explains every unit a lane cost.

### 3. Several verbs on one lane in one turn

Each accepted verb takes the next level. Levels are assigned in **turn-rotated commander order**, then
command id — the same fairness rule `lane-flow` uses — so two empires warding a shared border lane in the
same turn never favour the lower faction id, and the result is the same in either filing order.

### 4. One field, two readers — and the guard that keeps it so

`WardLevel` means *a defended lane*: deeper siege approach for an attacker on it, less loss for goods
on it. The two readings point the same way, so one field serves both (ideal §8.4). A source-scan guard
asserts that `WorldLane` declares exactly one ward-shaped field (`WardLevel`), and that its readers are
`DistrictLayout.WardLevelFor` and `lane-loss` — a third reader or a second ward field fails the guard.
The same guard asserts `Width`'s readers are the canonical writer and `lane-flow`; a later force-width
rule must join that list rather than add a field (map C3).

### 5. High levels in siege

`DistrictAssaultResolver` computes `checked(ApproachDepth + WardLevel × ApproachDepthPerWardLevel)`
(`:170-171`) and picks approach cells from the board's own rows (`:470-487`), so a deep ward saturates at
the board's depth — a geometric bound of the board, not an economic cap. At a level whose product passes
`int`, the `checked` arithmetic throws rather than wraps. Reaching it would take a cumulative ward bill
quadratic in the level; this spec does not assume that is unreachable — it **tests** the siege path at
large `WardLevel` values (well-formed zones up to saturation; the overflow level throws a named error)
and reports what it finds.

**Where the throw happens (audit 2026-09-20).** A throw inside `Step` fails the whole End Turn for every
faction. So the `ward` resolver checks, before it writes, that `WardLevel + 1` still passes the siege
depth arithmetic (`checked(ApproachDepth + (WardLevel + 1) × ApproachDepthPerWardLevel)` in `int`, and
`WardLevel + 1` itself) and refuses the order with `ward.level-unrepresentable` when it would not, spending
nothing. That is an **absolute bound derived from the type's range**, not a tunable ceiling (CLAUDE.md
caps rule: *"absolute bounds are derived … and throw"*): the refusal is the throw moved to where one
order, not the turn, carries it, and the siege path's own `checked` stays as the backstop. `widen` gets
the same check on `Width + widenStep` and on the capacity product in `long`.

### 6. Numbers

`Width` and `WardLevel` stay `int` — they are levels, not magnitudes on the power ladder (capacity's
scaling comes from `lane-flow`'s load units, not from `Width`). Increments are `checked`; an overflow
throws. Prices are `long`, `checked`, widened before multiplying.

## Tunables

| Key | Unit | Home |
|---|---|---|
| `lane.widenStep` | `Width` units per level | `data/tuning/trade.v{n}.json` |
| `lane.widenCostCurve` | `{ rubbleFirst, rubbleStep, ironworkFirst, ironworkStep }`, whole stock units | same |
| `lane.wardCostCurve` | same shape | same |

Missing keys are load rejections (T5); both steps zero for one curve is a load rejection (the ladder
must rise).

## `ssot-power-scale.md` §10 row owed (lands in the same change)

*Lane verb price ladders — `price(n) = first + step × n` per construction stock, `n` the lane's ward or
widen level. A cost ladder, not a power curve — the shape of row 31 (`TreeUnlockCost`); `n` is never `Θ`.
World stocks are Θ-invariant (flat faucets), so the ladder is flat against flat (PS-5 "neither").* Ordinal
assigned when it lands.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LaneVerbs|FullyQualifiedName~World.District"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~LaneFieldReaders"
python scripts\audit-overflow.py --targets A3
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/LaneVerbResolver.cs     (new) — widen, ward, prices
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs              MODIFIED — Widen, Ward kinds; LaneId field
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs     MODIFIED — admission rules
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs                MODIFIED — one resolver call in Snapshot
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs           MODIFIED — CommandPayload.LaneId
gk-core/src/FusionRpg.Contracts/WorldDtos.cs                       MODIFIED — WorldCommandRequest.LaneId
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                     MODIFIED — both mapping sites
data/tuning/trade.v{n+1}.json                               via gk-core/tools/tuning/publish.py
docs/architecture/power/ssot-power-scale.md                 §10 — one row
tests/FusionRpg.Core.Tests/World/Logistics/LaneVerbTests.cs          (new)
tests/FusionRpg.Guard.Tests/LaneFieldReadersGuardTests.cs            (new)
```

## Testing strategy

- **Conservation:** an accepted verb spends exactly `price(n)` from the paying sector; a short verb
  spends nothing and is dropped with `stock.short`.
- **Rising, uncapped:** for `n` across a wide sweep, `price(n+1) > price(n)` in total and no verb is ever
  refused for its level.
- **Effects:** `widen` raises `lane-flow`'s capacity by `widenStep × throughputPerWidth ÷ 1000`; `ward`
  lowers `lane-loss`'s rate by `protectionPerWard` (until the floor) and deepens the siege approach.
- **Order-independent:** two commanders warding one lane in one turn produce the same final state and
  the same payments in either filing order.
- **Guard:** one ward-shaped field on `WorldLane`; the named readers of `WardLevel` and `Width` only.
- **Siege at depth:** assaults resolve with well-formed zones at large `WardLevel`; the level at which the
  depth product passes `int` throws a named overflow, never wraps.
- **Who may act:** only a commander holding the named end may issue either verb; AI and player file the
  same commands through the same admission.

Verification boundary: Core (World/Logistics, World/District), Guard (the reader guard), and the command
plumbing across Data, Contracts and Server — `verify-change.py` with every changed path.

## Acceptance (contract)

1. A short verb is refused with a reason and spends nothing; an accepted one spends exactly the price.
2. Each level costs strictly more than the last; no level is refused for being high — only for being
   unrepresentable in its type (6); integer arithmetic is `checked` and throws, never wraps.
3. `WardLevel` is one field read by siege and by `lane-loss`; a guard fails on a second field or reader.
4. Same-turn verbs on one lane resolve the same in either filing order, with no faction-id tiebreak.
5. Only a commander holding a lane end may act; the AI uses the same path.
6. A `ward` or `widen` whose next level would overflow its field or the arithmetic that reads it is
   refused at resolution with `ward.level-unrepresentable` / `widen.level-unrepresentable` and spends
   nothing; no End Turn throws because of a lane level. Every accepted payment is a `construct` stock
   delta.

## Hard edges

- **Ruleset / goldens:** this module is `logistics-flow` **wave 3** and gates on that wave's flag
  **`trade.logisticsPolicy`**, registered with the wave's one `RulesetVersion` bump and shared with
  `auto-banking` and `construction-chain` (round 6 C1; row 7 of
  [../landing-order.md](../landing-order.md) §2) — never a widening of wave 1's `trade.logistics`. New
  command kinds cannot appear in an existing command log, so no existing golden moves (the `Assaults`
  precedent, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:131-140`). `ward` changes siege geometry for
  warded lanes — only on worlds where someone files it.
- **Command vocabulary and wire:** two kinds and one optional field — reviewed, additive.
- **§10 row** lands in the same change.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `widen`, `ward` | `trade-surface` (throttle answers), `trade-ai` (AI logistics), `forecast-facts` (names `widen` as an answer) |
| Price ladders | `trade-surface` (shows the next level's price) |

## Boundaries

- **Always:** gate before write; rising price; rotation for same-turn ties.
- **Ask first:** a verb that lowers a level; paying from a sector not at the lane's end.
- **Never:** a level cap; a second ward field; a price paid in loam or wallet currency.

## Design-gate checklist

```
[x] Subsystems: world commands, lanes, siege district geometry (read), construction stocks, tunables,
    power-scale inventory (cost ladder row).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md, plus ssot-power-scale §10.2 rows 31 and 37.
    Gap: battle-engine-ssot.md not read this session (siege geometry is only read, never changed).
[x] decisions.md: decision 47 (ward depth) kept; no lock on lane building.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: no writer of Width/WardLevel; the siege depth arithmetic and zone scan;
    the reserved `ward` name.
[x] Surrounding sections read: DistrictAssaultResolver's 17.11 comment; bind-warden's naming note.
[x] Constraints tested, not assumed: siege behaviour at high levels is a test to run, not a claim.
[x] §2 invariants: no ceiling; cost ladder registered; numbers checked.
[x] Corrections propagated: the §10 row (missed by the map) is owed here and in the session report.
[x] No population pinned.
[x] Event-refreshed cache: Width/WardLevel are not path-cache triggers (capacity and loss only).
[x] Orderings: same-turn multi-commander verbs tested in both filing orders.
[x] Actor magnitudes: none.
[x] No SOLID fork: one WardLevel for two readers; the command pipeline extended, not copied.
[ ] Registry row: the lane-field reader guard needs a row in gk-core/scripts/enforcement-registry.v1.json.
```

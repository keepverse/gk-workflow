# Spec: `construction-chain`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `construction-chain`, row 9 of the
[logistics-flow map](../logistics-flow-map.md) (wave 3; depends on `lane-flow`, `auto-banking` for the
policy commands, `empire-seed` for refinery magnitudes). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §3 principles 4 (conversions lossy, rate-capped or
gated) and 7 (world stocks never feed an account path), §3.15 (a per-turn rate is structural), §11 row 3
(*"the construction chain"*); map C3 on fleet's side confirms this module owns refine wiring. House
style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Close the base-defense refine chain the world never ran, and let construction stocks move between an
empire's own sectors. At every **working refinery**, each turn, rubble becomes ironwork through the
already-shipped, already-tested `SiegeConstruction.RefineGated` — lossy by design, at a per-turn rate per
refinery. And rubble and ironwork travel on the same lanes, under the same `route-set` policies, the same
capacity and the same loss as any good — but they never bank.

Success looks like: the two stock deltas reconcile every turn; a sector without a working refinery
refines nothing; refining per turn never exceeds the rate times the working refineries; and no code path
turns rubble, ironwork, loam or recruits into a banking fact, a material or a wallet credit.

## Locked anchors

- **Call the shipped function; never re-derive it.** `Refine` (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:33-38`)
  and `RefineGated` (`:47-48`) exist, are tested (`gk-core/tests/FusionRpg.Core.Tests/World/SiegeConstructionTests.cs:56-79`),
  and have **no production caller**. This module is their first.
- **Decision 28: lossy and gated by a working building** (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:27-32`, `:40-46`).
- **The unset per-turn cap is why the refine was never wired** — *"`refine.perTurnCap` staying unset
  (decision 29) makes an automatic per-turn refine an economically live question (an unbounded refinery
  could drain a sector's whole rubble stock in one pass)"* (`gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:83-89`).
  This module sets it — as a **structural per-turn rate per refinery** — and updates that comment in the
  same change (map C4).
- **World stocks are map-scoped and never auto-bank** (`docs/architecture/empire-resource-ssot.md` §4
  rules 5 and 5b). They cross worlds only as legion cargo (`fleet` / `world-continuity`), never by flow.
- **One domain owns a number** (`docs/architecture/tunables-ssot.md` §2). The refine concept is the siege
  domain's, so the rate lives in `data/tuning/siege.v{n+1}.json`; logistics reads it.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Refine`: `long`, `checked`, divide by 1000 last and once; throws on negative input | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:33-38` |
| `RefineGated`: no working refinery, no output | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:47-48` |
| The raw faucets (shard vein → ironwork, material seam → rubble) are wired into `Production` | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:57-72`, `:90-106`; called at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:310` |
| `StructureKind.Refinery` exists | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:30` |
| A working structure is one on a slot whose construction has finished — the gate production already uses | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:48-55` |
| Refine tunables: `refineYieldMilli` 600, `refineRubblePerIronwork` 4, `refinePerTurnCap` −1 (unset); the loader accepts −1 or ≥ 0 | `gk-core/data/tuning/siege.v1.json` (`construction`); `gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs:286-297` |
| `RubbleStock` and `IronworkStock` are `long` sector fields, hashed as conditional rows | `gk-core/src/FusionRpg.Core/World/WorldState.cs:181`, `:187`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128` |

### Wiring gap

| Gap | Evidence |
|---|---|
| `Refine`/`RefineGated` have zero production callers (tests only) | callers: `gk-core/tests/FusionRpg.Core.Tests/World/SiegeConstructionTests.cs:56-79` only |
| The `refinery` structure row is identity-only (no `magnitudes`), so no refinery can load | `gk-data/packs/fusion/data/seed/structures/refine/refinery.json`; `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65` — magnitudes come from `empire-seed` (map ask A5) |

### Real gap (this module closes it)

The per-turn refine step (L7) and its rate; world stocks as routable goods.

## Design

### 1. Refine (L7)

For each sector in id order, owned by some faction, with `n ≥ 1` **working refineries** (slots holding a
structure of `StructureKind.Refinery` whose construction has finished — the `LoamProduction` gate):

```
spend    = min(RubbleStock, n × construction.refinePerTurnCap)       // long, checked
produced = SiegeConstruction.RefineGated(true, spend, construction.refineYieldMilli)
RubbleStock   −= spend
IronworkStock += produced
```

Both changes are recorded through the turn's `StockDeltaRecorder` as `refine` deltas — `rubble` −spend
and `ironwork` +produced on the sector (`trade-foundation` `ledger-keys` §4a; `stock-deltas`) — so the
world-stock ledger explains every ironwork unit a refinery made. "Working" is
`SectorFeatures.ActiveTier(slot) >= 1` (`trade-foundation` `sector-features` §3), the same gate every
structure reader uses. A sector with no working refinery spends nothing and produces nothing. `Refine` truncates
(`4 rubble → 2 ironwork`, `1 rubble → 0`), which is the lossy conversion P5 asks for — the truncated
remainder vanishes. L7 runs after the flow (L5) and the loss (L6), so rubble delivered this turn is
refined this turn.

### 2. The rate — a structural per-turn limit

`construction.refinePerTurnCap` becomes a **rubble-spend rate per working refinery per turn**, published
as a positive value in `siege.v{n+1}` through `gk-core/tools/tuning/publish.py`. It bounds how much one building
converts per turn — a rate, not a stock ceiling — and the code comment says so (PS-8's structural class;
more refineries convert more, without limit). The loader keeps rejecting values below −1 and, once this
module lands, rejects −1 too: an unset rate on a world that refines is exactly the unbounded drain the
existing comment warns about, so it becomes a load rejection naming the key (T5), not a silent
"unlimited".

### 3. World stocks on the lanes

`rubble` and `ironwork` are goods ids the logistics steps accept, with three differences from located
goods, all enforced in one place (the goods accessor this module adds):

| | Located goods | World stocks |
|---|---|---|
| Read / written at a sector | the warehouse (`sector-yield` `located-stock`) | `RubbleStock` / `IronworkStock` |
| Default destination | nearest bank point | **none** — a world stock moves only under a `route-set` |
| At a bank point | banked by L3 | never touched by L3; stays a world stock |
| Load (lane-flow) | scaled by the faucet's read | `scaleMilli = 1000` (the faucets are flat, `SiegeConstruction.cs:57-72`) |
| Delivery room | warehouse capacity | unbounded (the stocks are uncapped by design, `SiegeConstruction.cs:77-81`) — so they never wait `AtDoor` |

Loss, capacity, transit, stranding and return apply unchanged. Loam and recruits are not goods ids here
and are refused at admission (`auto-banking`).

### 4. The guard — world stocks never become account value

A source-scan guard plus a property test:

- **Scan:** no file under `src/FusionRpg.Core/World/Logistics/` or the banking step's code reads
  `RubbleStock`, `IronworkStock`, `LoamStock` or `RecruitStock` and writes a banking fact, a material
  ledger row or a wallet credit in the same function (the accessor is the one reader of the world-stock
  fields in this namespace; the scan asserts that).
- **Property:** over seeded random worlds with random policies routing every world stock to every
  reachable own sector (bank points included), the sum of all banked credits of every kind is unchanged
  by the presence of world stocks.

### 5. Determinism and numbers

Sectors in id order; no RNG. `spend` and `produced` are `long`; `n × rate` is `checked` (throws, never
wraps). No allocation in the kernel; a changed sector is written back once per turn.

## Tunables

| Key | Unit | Home |
|---|---|---|
| `construction.refinePerTurnCap` | rubble spent per working refinery per turn (structural rate) | `data/tuning/siege.v{n+1}.json` — **owned by the siege domain**, read here |
| `construction.refineYieldMilli` | ‰ (lossy, bounded ratio) | same, unchanged |
| `goods.rubble.transitLossMilli`, `goods.ironwork.transitLossMilli` | ‰ per lane | `data/tuning/trade.v{n}.json` (`lane-loss`'s key family) |

**The key's name says "Cap"; its meaning is a rate.** `refinePerTurnCap` is the siege domain's key and
keeps its name here (renaming a key is that domain's reviewed change). The code comment at its reader
states that it is a per-refinery per-turn **rate** — structural, uncapped in count — so the caps audit and
a reader of `audit-magic-numbers.py` output do not mistake it for a progression ceiling. A rename to
`refineRubblePerRefineryPerTurn` in `siege.v{n+1}` is recommended to the siege domain's owner.

**Verification boundary for the publish.** `data/tuning/siege.v*.json` has no owner row in
`gk-core/scripts/verification-boundaries.v1.json` (`gk-core/data/tuning/**` has no fallback; the audit of 2026-09-20 saw
`verify-change.ps1 -PlanOnly` stop on `gk-core/data/tuning/world.v6.json` with *"VERIFICATION BOUNDARY MISSING"*).
The publish commit adds an owner row `siege-tuning` (paths: each published `data/tuning/siege.v{n}.json`
as an exact path — the matcher takes exact paths and `dir/**` only, `scripts/verify-change.ps1:70-75` —
`gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs`; project `core`) with the siege tuning loader's tests.

`construction.refineRubblePerIronwork` (4) is **not read by `Refine`** — the function reads only
`refineYieldMilli` — and has no reader anywhere in `src/`. Two tunables describe one ratio; this module
reads the one the shipped function takes and reports the other as a contradiction for the siege
domain's owner.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.SiegeConstruction|FullyQualifiedName~World.Logistics.ConstructionFlow"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldStock"
python scripts\audit-magic-numbers.py --summary
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/ConstructionFlow.cs    (new) — L7 refine; the goods accessor
                                                          (world stock vs located good)
gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs      MODIFIED — comment at :77-89 updated (the rate is
                                                          now set and wired); no logic change
gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs           MODIFIED — refinePerTurnCap: −1 rejected
data/tuning/siege.v{n+1}.json                             via gk-core/tools/tuning/publish.py (the rate)
tests/FusionRpg.Core.Tests/World/Logistics/ConstructionFlowTests.cs   (new)
tests/FusionRpg.Guard.Tests/WorldStockNeverBanksGuardTests.cs         (new)
```

## Testing strategy

- **Reconciliation, every turn:** `ΔIronwork = Refine(spent, yieldMilli)` and `ΔRubble = −spent` per
  sector; a sector without a working refinery has both deltas 0 from L7.
- **Rate:** refine per sector per turn ≤ `n × refinePerTurnCap`; doubling the refineries doubles the
  bound (no ceiling on the count).
- **Under construction:** a refinery with construction turns remaining refines nothing.
- **Routed world stock:** rubble routed from a seam sector to a refinery sector arrives after its
  transit, less lane loss, and is refined that turn; nothing banks.
- **Guard:** the source scan and the random-policy property above.
- **Tuning:** a siege file with `refinePerTurnCap: -1` is rejected at load, naming the key.

Verification boundary: `FusionRpg.Core.Tests` (World/Siege, World/Logistics), `FusionRpg.Guard.Tests`
(the new guard). The tuning publish is its own commit (T7: never a refactor and a rebalance together).

## Acceptance (contract)

1. Refining spends rubble and produces exactly `Refine(spent, yieldMilli)` ironwork; both are recorded as
   `refine` stock deltas and `stock-deltas`' reconciliation closes every turn. A refinery mid-upgrade keeps
   refining at its current rate; one under first construction refines nothing.
2. Refine per turn ≤ rate × working refineries; the rate is a commented structural limit.
3. No code path turns rubble, ironwork, loam or recruits into a banking fact, a material or a wallet
   credit (scan + property).
4. Moving a world stock between own sectors conserves it except for lane loss.

## Hard edges

- **Tuning:** `siege.v{n+1}` publishes the rate; the siege loader's rule changes (−1 rejected). Every
  world, legacy or not, loads the same siege file (tuning is process-global — umbrella X4); legacy worlds
  never run L7, so the rate has no effect there. The siege **battle board** does not read
  `refinePerTurnCap` today (no reader in `src/` beyond the loader), so no battle golden moves.
- **Ruleset / goldens:** L7 runs only under **`trade.logisticsPolicy`**, this module's own wave flag
  (round 6 C1: `logistics-flow` wave 3, one bump for the wave, shared with `auto-banking` and `lane-verbs`
  — row 7 of [../landing-order.md](../landing-order.md) §2). It used to gate on `trade.logistics`, which
  wave 1 registers. No existing world golden moves.
- **Content dependency:** until `empire-seed` gives `refinery` magnitudes, no refinery exists in play; the
  step is tested on fixture structures.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| The goods accessor (world stock vs located good) | `lane-flow`, `transit-buffer`, `lane-loss`, `lane-verbs` (spends from the same fields) |
| L7 refine | `forecast-facts` |
| The world-stock guard | `trade-foundation` `economy-report` (reads it as an invariant) |

## Boundaries

- **Always:** call `RefineGated`; one accessor for world stocks; the rate from siege tuning.
- **Ask first:** reading `refineRubblePerIronwork`; any conversion other than rubble → ironwork.
- **Never:** a world stock at a banking fact; a second refine formula; an unbounded refine.

## Design-gate checklist

```
[x] Subsystems: world turn engine (L7), siege construction economy, tunables (siege domain), economy
    registry (world stocks).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md, plus empire-resource-ssot.md §4, tunables-ssot
    §2. Gap: spec-siege-construction.md not read this session.
[x] decisions.md: decisions 28/29 (lossy, gated; the unset cap) respected; Empire resource registry
    (world stocks never bank) guarded.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: Refine/RefineGated have test-only callers; refineRubblePerIronwork has no
    reader; the loader accepts -1; the working-structure gate.
[x] Surrounding sections read: SiegeConstruction's class doc and Production doc in full.
[x] Constraints tested, not assumed: "no battle golden moves" rests on refinePerTurnCap having no
    reader outside the loader (grep this session), to be confirmed by the suite at module end.
[x] §2 invariants: none contradicted; conversion lossy and rate-limited; rate structural and commented.
[x] Corrections propagated: C4 comment update owned here; the unread tunable reported.
[x] No population pinned.
[x] Event-refreshed cache: none.
[x] Orderings: L7 after L5/L6 is fixed by logistics-phase.
[x] Actor magnitudes: none.
[x] No SOLID fork: the shipped Refine is called, not copied.
[ ] Registry row: the "world stocks never bank" guard needs a row in
    gk-core/scripts/enforcement-registry.v1.json when it lands (a guard script `world-stock-never-banks`, tier
    `ci`, and invariant `tn-world-stock-never-banks`, source umbrella §5 invariant 2 and
    empire-resource-ssot §4 rule 5).
[x] Audit 2026-09-20: refine deltas recorded; working gate through sector-features' ActiveTier; the
    siege tuning publish's missing verification boundary named with its row.
```

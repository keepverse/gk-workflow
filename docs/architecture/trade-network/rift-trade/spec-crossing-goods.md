# Spec: `crossing-goods`

**Status: spec written 2026-09-19 against the owner-approved map** ([../rift-trade-map.md](../rift-trade-map.md),
APPROVED 2026-09-19, decision Q2). Module 7 of `rift-trade`, wave 1. Every `file:line` below was opened this
session. Docs only. **House style:** [../../world-action-economy/spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

One closed table that says, for every quantity the game registers, whether a crossing may carry it, what it
becomes on the far side, and whether it can ever bank there — with guards so no later change can quietly move
loam or recruits between worlds, or credit a wallet from the crossing itself.

Success looks like: a route naming fire essence and rubble is admitted; one naming loam is refused
`rift.good-refused:loam`; a property test over random routes finds no path that moves loam or recruits between
worlds and no path that credits a wallet or material ledger from the crossing.

## Scope and non-goals

**In scope:** the table, its admission function, the guards, and the registry wording this program owes.

**Not in scope:** the located-good class and its catalog (`sector-yield` `located-goods-registry`); legion
equipment pieces (`sector-yield` `legion-equipment-stock`, `legion-build`); banking (`sector-yield`
`banking-fact`); moving items or legions between worlds (`world-continuity` `advance-carry`).

## Locked anchors

- **Q2 (owner, 2026-09-19): rubble and ironwork may cross, and they are never auto-banked.**
- **Round 6 S2 — this table is the only trade channel between worlds.** *"Trade goods cross only through
  rift-trade routes. An advance is a weight-limited transit"*
  ([../decisions-round-4.md](../decisions-round-4.md) Round 6 S2). So the table below is not one of two
  answers about what may cross: it is **the** answer for trade, and the priced, bounded crossing leg
  (`crossing-leg`) is the only path a good takes as commerce. The second, lossless channel the family
  worried about — goods riding an advancing legion — is closed by **W1**: an advance carries only what its
  weight limit allows, Σ(unit count × that unit type's carry capacity) read from `world.carry.capacity`,
  with units and goods drawing on the same limit, and the excess refused at `depart` admission
  (`../fleet/spec-carried-goods.md` §5; the arithmetic is `world-continuity` `advance-carry`'s).
- **Round 6 W2 — import/export through the gate is `world-transit`'s**, a named future program (idea round
  later). It will own import and export and the gate's own weight limits. *"Until it exists,
  `world-continuity`'s advance moves only what the weight limit allows, and goods cross by rift-trade
  route."* **No rule in this spec anticipates `world-transit`**: the table stays closed, the admission
  function stays this module's, and nothing here is designed as a partial gate.
- **Loam never crosses worlds** (world-continuity ideal §3.6; `empire-resource-ssot.md` §4 rule 4).
- **Recruits never cross** (an accrual meter buys exactly one action where it accrued, `empire-resource-ssot.md`
  §2).
- **Nothing banks on the crossing.** Goods reach a wallet only through the destination world's own banking step.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The registry classes: wallet, material, world stock, accrual meter, battle budget, item | `docs/architecture/empire-resource-ssot.md` §2 (the class table) |
| Loam, rubble, ironwork and recruits are per-sector `long` fields | `gk-core/src/FusionRpg.Core/World/WorldState.cs:173`, `:181`, `:187`, `:232` |
| A legion's carried loam is its own field | `gk-core/src/FusionRpg.Core/World/WorldState.cs:325` |
| Rubble and ironwork production is uncapped by design (no warehouse ceiling) | `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:75-81` |
| The banked materials catalog the located-goods catalog will derive from | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:68` |

### Wiring gap

None.

### Real gap

The table, the admission function, the guards. The located-good class does not exist yet
(`sector-yield` `located-goods-registry`, a build-order dependency).

## Design

### 1. The table (closed vocabulary)

| Registry class (`empire-resource-ssot.md` §2) | Crosses? | Leaves from | Lands as | Can it bank at the destination? |
|---|---|---|---|---|
| **Located good** (`sector-yield`) — materials and souls in their located form | **Yes** | Anchor warehouse | Located stock in the destination anchor's warehouse | Only by the destination world's own banking step while it resolves a full step; never on the crossing; never in a sleeping world |
| **Located good — legion equipment piece** | **Yes** | Anchor warehouse | Located stock | **Never** — pieces have no banked form (`sector-yield` `legion-equipment-stock`) |
| **World stock — `rubble`, `ironwork`** | **Yes (Q2)** | Anchor sector's stock | The destination anchor sector's stock | **Never** — no world stock banks, and no auto-banking policy may target one |
| **World stock — `loam`** | **Never** | — | — | — |
| **World stock — an AI treasury** (`counterparties` `empire-treasury`, its owner and writer — round 5 X3; filled through `sector-yield` `banking-fact`'s destination seam) | **Never** — routes are the player's; the treasury is an AI faction's | — | — | — |
| **Accrual meter — `recruit`** | **Never** | — | — | — |
| **Wallet, Material** (banked) | **Never** — unlocated; nothing to leave from | — | — | — |
| **Battle budget** | **Never** — dies with its battle | — | — | — |
| **Item** (including relics) | **Never on a crossing** — items ride legion cargo and change worlds only by advancing | — | — | — |

**The other way goods could change worlds (audit 2026-09-20).** `world-continuity` `advance-carry` moves whole
legions between worlds. A legion may also hold `fleet`'s hashed **carried goods** (located goods and world
stocks, `../fleet/spec-carried-goods.md`), which that spec does not mention. If they rode an advance, located
goods would cross worlds with no crossing loss, no throughput bound and no Grand Exchange — a lossless second
channel beside this program's priced one (P5). This table stays the only list of what a **route** carries;
what an **advance** may carry is `fleet`'s owner question FQ3 (`../fleet-map.md`), filed on `world-continuity`
as fleet ask A15. Recommended there: located goods may not ride an advance (unload first); rubble and ironwork
may, in the one carried pool.

The table is keyed by **class**, plus an explicit allow-list inside the world-stock class (`rubble`,
`ironwork`). A new class, or a new world stock, is refused `rift.good-class-unlisted` until this table names it —
so the table can never be widened by accident.

### 2. Admission function

`CrossingGoods.Admit(goodId) → (ok, reason, kind)`, pure, where `kind ∈ {Located, WorldStock}` tells
`crossing-handoff` which stock to move. Reasons (closed): `rift.good-refused:<id>` (named never-crosser),
`rift.good-class-unlisted`, `rift.good-unknown`.

Located-good ids come from `sector-yield`'s `LocatedGoodCatalog`, which is derived from `MaterialCatalog`: its size
is a **reading**, never asserted.

### 3. Guards

- **Source scan** (`FusionRpg.Guard.Tests`): no file under `src/FusionRpg.Core/World/Logistics/Rift/**` names
  `LoamStock`, `CarriedLoam` or `RecruitStock`.
- **Property test:** random route sets over a synthetic two-world fixture never change loam or recruit stock in
  either world through a rift step, and never produce a banking fact, a material-ledger row or a soul-ledger row
  from a rift step (banking facts come only from `banking-fact`).
- **Registry wording (ask A12):** `world-continuity`'s `continuity-doc-amendment` writes `empire-resource-ssot.md`
  rule 5b as *"world stocks cross only as cargo"*. Under Q2 the rule must also name the crossing: *"world stocks
  cross between worlds only as cargo or over a cross-world route, and never bank"*. This program does not edit that
  file; the owning module writes both halves in one change.

## Tunables

None.

## Numeric types

No arithmetic here.

## Contract-level acceptance

1. Membership is a closed vocabulary over registry classes plus the two-member world-stock allow-list, pinned with
   the reason "closed vocabulary the code owns"; no test counts located goods.
2. `Admit` refuses loam, recruits, wallets, materials, battle budgets and items with their named reasons, and
   admits every located good and both allowed world stocks.
3. An id of a class the table does not list is refused `rift.good-class-unlisted`.
4. The property test finds no path that moves loam or recruits between worlds and no path that credits a wallet,
   material or soul ledger from a rift step.
5. The source scan fails on any loam or recruit field named under `World/Logistics/Rift/`.

## Test plan and verification boundary

| Test | Project |
|---|---|
| Table and admission | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| Property test | `gk-core/tests/FusionRpg.Core.Tests` (World/Logistics/Rift) |
| Source scan | `gk-core/tests/FusionRpg.Guard.Tests` |

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
```

## Hard edges

- **Always:** refuse by default; widen only by editing the table.
- **Ask first:** letting any item or legion cross on a route (that is advancing, `world-continuity`'s).
- **Never:** loam or recruits on a crossing; a banking step on the crossing; a banked form for a legion equipment
  piece.

## Dependencies

| Consumes | From |
|---|---|
| Located-good class and catalog | `sector-yield` `located-goods-registry` |
| Legion equipment as a located good | `sector-yield` `legion-equipment-stock` |
| Rule 5b wording | `world-continuity` `continuity-doc-amendment` (ask A12) |

| Exposes | To |
|---|---|
| `CrossingGoods.Admit` | `rift-route` (set-time admission), `crossing-handoff` (which stock moves) |

## Files

```
src/FusionRpg.Core/World/Logistics/Rift/CrossingGoods.cs         NEW — table and Admit (pure)
tests/FusionRpg.Guard.Tests/RiftCrossingGoodsGuardTests.cs         NEW — source scan
```

## DESIGN-GATE §5 checklist

```
[x] Subsystems: economy registry, world stocks, located goods.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run by me.
[x] Read this session: empire-resource-ssot.md in full; sector-yield-map located-goods-registry,
    banking-fact, legion-equipment-stock; world-continuity-ideal §6.2.
[x] decisions.md: Empire resource registry (loam never moved across worlds, via the maps).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: no HIGH finding.
[x] Verified against code: the stock fields and their types; rubble/ironwork uncapped.
[x] Read surrounding sections: empire-resource-ssot §2-§4 in full.
[x] Constraints tested: none claimed.
[x] No §2 invariant contradicted: loam never crosses; every faucet names its sink (no faucet here).
[x] Corrections propagated: rule 5b's wording is filed as an ask (A12); not edited here.
[x] No population count pinned: only the closed class table and the two-member allow-list.
[x] Event-refreshed cache: none.
[x] Orderings: none.
[x] Actor magnitudes: none.
[x] No SOLID-violating parallel path: the registry classes are the one source.
[ ] Registry row: the loam/recruit source scan needs a guards row in
    gk-core/scripts/enforcement-registry.v1.json when it lands (named by the 2026-09-20 audit:
    `rift-loam-never-crosses`).
```

## Audit 2026-09-20

Added here: the note that an advancing legion's carried goods are a second path between worlds that this table
does not govern, with the owner question that decides it (`fleet` FQ3). Checked and clean: the class table is a
closed vocabulary pinned with its reason; no located-good count is asserted; loam and recruits never cross; the
AI treasury never rides a route (round 5 X3); nothing banks on the crossing. **Verification boundary:** the
`core-world-logistics-rift` owner boundary (`spec-crossing-anchor.md` *Audit 2026-09-20*) and the Guard.Tests
source scan.

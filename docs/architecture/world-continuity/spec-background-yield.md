# Spec: `background-yield`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 11 of the
[world-continuity map](../world-continuity-map.md) (wave 4; depends on `coarse-step`, external
trade-network `sector-yield`). Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §3.3,
§3.7, §3.8, §6.6 (the new cure for the 500-hour test). House style:
[../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

Persistent worlds bring back the 500-hour test (*"any permanent solution to a recurring cost is
eventually free"*, `docs/architecture/empire-economy-ssot.md` §7). The cure (ideal §6.6), made concrete:

1. Background production runs at a per-mille multiplier **below 1000** that **decays as more worlds
   hibernate** — a soft curve that never reaches 0 by fiat.
2. Background output lands in **that world's** warehouses and is collected by visiting, by cargo, or by
   `rift-trade` — **never** straight into a wallet or the material ledger.
3. Upkeep and enemy pressure keep running at full rate, so holding an old world is never free.

## Scope and non-goals

**In scope:** the multiplier curve and its two inputs (hibernating count, mode); feeding
`CoarseInputs.YieldMilli`; the no-banking rule for coarse and idle records; the faucet-and-sink statement.

**Not in scope:** warehouses, located goods and banking (trade-network `sector-yield`); the coarse
arithmetic (`coarse-step` §2); the economy report harness (trade-foundation `economy-report`, which this
module adds rows to).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The production phase — loam and siege construction yields | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:302-313` |
| World stocks are map-scoped and never bank (amended registry) | `docs/architecture/empire-resource-ssot.md` §3 (world-stock class) |
| Coarse production is already scaled by one per-mille input and upkeep is not | `coarse-step` §2 (this program) |
| `sector-yield`: pooled, capacity-bounded warehouses per sector; production halts when full; banking only on a bank fact | `docs/architecture/trade-network/sector-yield-map.md` §2.3–§2.5 |

### Wiring gap

No shipped code banks sector yields today (`docs/architecture/trade-network-ideal.md:472-473`), so
"background yield is never auto-banked" is vacuously true until `sector-yield` lands. This module makes it
true by construction for when it does.

### Real gap

No multiplier, no decay with world count, no rule forbidding a background bank.

## Design

### 1. The multiplier — soft, decaying, bounded ratio

```
yieldMilli(h, mode) = base(mode) × 1000 / (1000 + decayPerWorldMilli × (h − 1))      // divide last, long
    h    = number of the save's map worlds in state hibernating or idle, h ≥ 1 for the world being stepped
    base = hibernatingYieldMilli  (mode = Hibernating)
         | idleYieldMilli         (mode = Idle; validated ≤ hibernatingYieldMilli — idle-world §3)
```

- Strictly below 1000 for every `h` (validated: `base < 1000`), strictly decreasing in `h`, never 0 for
  any finite `h` — a **soft** curve (ssot-power-scale §11: no hard floor by fiat). It is a bounded ratio
  (§11.6 class) and says so in a comment.
- `h` is read Data-side when the coarse inputs are built and **logged** with them (`coarse-step` §1), so
  replay never recounts worlds.
- Why a count of worlds and not the sum of their yields: the cure must bite on *breadth* (many old
  worlds), which is exactly what the 500-hour test is about; a single well-developed old world still pays
  below active and still owes full upkeep.

### 2. Where the output goes

- **Until `sector-yield` lands:** coarse production lands in the sector stocks it lands in today (loam,
  rubble, ironwork, recruits) — map-scoped by the registry, so nothing banks.
- **After `sector-yield` lands:** located-good production lands in that sector's `located-stock`, bounded
  by its warehouse (`sector-yield` §2.4–§2.5). The warehouse halt is `sector-yield`'s decision 22, not a
  new cap. The coarse closed form respects it: `stock' = min(stock + n·r·yield/1000, capacity)` with the
  overflow reported.
- **No banking in the background.** A coarse or idle record never emits a banking fact, even where a
  bank point holds goods: banking is a player act on a visit (`sector-yield` bank fact). Enforced by an
  allow-list of fact kinds a coarse record may emit (`produce`, `upkeep`, `loss`, …; never `bank`),
  checked when the record is written.

### 3. Faucet and sink, named in the same change

| Faucet | Sink it names |
|---|---|
| Background production at `yieldMilli` | full-rate upkeep (loam upkeep, garrison upkeep — `coarse-step` §2 does not scale them), enemy pressure (frontier contests), warehouse halt, and the collection trip itself (a visit, cargo capacity, or a priced `rift-trade` crossing) |

P1 check (economy-principles, run by trade-foundation's `economy-report`): no world stock's net flow is
monotone positive across a scripted campaign with 1…k hibernating worlds; the report prints total
background yield per End Turn against `h` and never pins a value.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | production phase; coarse scaling slot | reused |
| Wiring gap | nothing banks yields yet | §2 makes "never auto-bank" structural |
| Real gap | multiplier, decay, banking ban | §1–§2 |

## Acceptance (contract)

1. `yieldMilli(h, mode) < 1000` for every `h ≥ 1`; strictly decreasing in `h`; `> 0` for every tested `h`
   (property test over a wide range — a structural bound, not a population).
2. For the same state, background yield per period is below active yield (asserted with `coarse-step`
   acceptance 5).
3. Adding a hibernating world never raises the per-world multiplier (monotone) — the total is reported
   by the economy report, not pinned.
4. No coarse or idle record writes a wallet row, a material-ledger row or a banking fact (source-scan +
   store test).
5. Idle's base ≤ hibernating's base (load-time validation).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/BackgroundYieldTests.cs` (new): 1, 3, 5.
- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (extend): 2.
- `tests/FusionRpg.Data.Tests/WorldCoarseReplayTests.cs` (extend): 4 (no wallet/ledger rows after a
  catch-up).
- trade-foundation `economy-report` gains the background rows when both exist.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python scripts\audit-magic-numbers.py --summary
```

## Hard edges

- **`rpg_worlds` schema:** none.
- **Replay:** `h` and `yieldMilli` are logged inputs; replay reads them.
- **Corpse-cache tick key:** none.

## Dependencies

`coarse-step` (the input slot), `idle-world` (mode), external `sector-yield` (warehouse landing — the
multiplier works without it). Consumed by `away-digest` (yield lines).

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `hibernatingYieldMilli` | per-mille of active production | 500 | `data/tuning/world-continuity.v1.json` |
| `idleYieldMilli` | per-mille (≤ hibernating) | 400 | same |
| `decayPerWorldMilli` | per-mille added to the divisor per extra old world | 250 | same |

## Boundaries

- **Always:** log the inputs; upkeep at full rate; land output in the world.
- **Ask first:** banking from a hibernating world.
- **Never:** a background wallet or ledger write; a multiplier ≥ 1000; a hard floor of 0.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `BackgroundYield.Milli(h, mode)` | `coarse-step` input builder, `idle-world`, `multiverse-surface` (show the rate) |
| Coarse fact-kind allow-list | `away-digest`, trade-foundation ledgers |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world economy (production, upkeep), coarse step, trade warehouses (external).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md; sector-yield-map.md §2.3-2.5 headings.
    Not read: economy-principles.md, spec-soul-economy.md (Economy row) — P1/P6 taken from
    trade-foundation-map.md §2.9 and PRINCIPLES.md §11. Gap stated.
[x] decisions.md checked: none on background yield.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: production phase lines.
[x] Surrounding sections read (trade-network-ideal §8.6 consequence paragraph).
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted: soft curve, bounded ratio, commented.
[x] Corrections propagated.
[x] No population pinned (economy report prints totals).
[x] No cache.
[x] No ordering-fixed criterion.
[x] No actor magnitude.
[x] No SOLID fork: one multiplier function, one warehouse (sector-yield's).
[ ] Registry row: "no background banking" — source-scan guard added when built.
```

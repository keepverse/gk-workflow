# Spec: `clan-economy`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `clan-economy`, row 9 of the
[counterparties map](../counterparties-map.md) (wave 3; depends on `clan-seeding`, `need-vector` and
`sector-yield`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.2 (*"A clan's stock comes
from its own sector production, under the same rules as everyone's … stock that refills from nothing
would mint banked goods every turn"*), §10 C4, §14b (*"clans consume from their own needs and pay the same
upkeep; clan production enters the P1 net-flow report"*). Session record:
`tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Make a clan's goods **come from somewhere and go somewhere**. A clan produces only from its own sectors
under the rules every faction uses, consumes what it needs every turn, and pays the same loam upkeep. Its
surplus is therefore bounded by its production minus its consumption, and by the warehouse capacity at
which its production halts — never a free faucet.

Success looks like: a clan that nobody trades with fills its warehouse with what it does not need, then
stops producing; a clan starved of what it needs empties that stock and wants it more; the world economy
report shows a clan line whose net flow reconciles to the turn's deltas.

## Scope and non-goals

**In scope:** the clan consumption pass and its place in the Logistics phase; asserting that clan
production and upkeep are the shared rules with no clan branch; the clan rows in the economy report; the
stock-delta kind the pass writes.

**Non-goals:** production, warehouses and production halt (`sector-yield`); banking (clans bank nothing:
no treasury, no destination — `empire-treasury` §3); prices and trading at the clan hub (`exchange`);
what a clan decides (`trade-ai` `clan-behaviour`); loam upkeep arithmetic (`LoamUpkeep`, unchanged).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Loam upkeep is one rule for every owner, with the G-C exemption only for a faction holding no rootbed | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:47-80` |
| Upkeep is drawn per connected territory component, per faction, every turn | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:149-165` |
| Every clan is seeded with a rootbed and a seat (`clan-seeding` §1), so neither exemption applies at seed | `docs/architecture/trade-network/counterparties/spec-clan-seeding.md` §1 |

### Wiring gap

None.

### Real gap

Everything: there are no located goods yet (`sector-yield`), so there is nothing for a clan to produce or
consume. This module rides `sector-yield`'s production and warehouse and adds only the consumption pass.

## Design

### 1. Production — the shared rule, asserted

A clan-owned sector produces located goods through `sector-yield`'s production step exactly as a sector
of the same content owned by anyone else. This module adds **no** clan branch to production; it adds a
test that proves there is none (acceptance 1). Production halts at warehouse capacity for a clan as for
everyone (`sector-yield` `production-halt`).

### 2. Consumption — the one new pass

Inside the `Logistics` phase, after `exchange` settlement (`logistics-flow-map.md` *Phase-internal order*
places `clan-economy`'s pass after the flow steps; this spec fixes it after settlement too, so a clan
consumes what it holds once trading for the turn is settled):

```text
for each clan c (ordinal), for each good g (ordinal) with located stock in c's sectors:
    need      = NeedVector.DemandOf(world, c, g, turn)                       // value-normalised units
    consumed  = min(stock(c, g), need × clan.consumptionPerTurnMilli / 1000)  // long, checked, divide once
    draw `consumed` from c's sectors pro rata by each sector's stock of g;
    the integer remainder goes to sectors in ordinal id order, one unit each
```

- A clan consumes only what it **needs**. Goods it does not need are never consumed: they accumulate to
  warehouse capacity, where production halts. That is the bound on its surplus, and it is the same bound
  the player meets.
- Pro rata across sectors, never "lowest id first", so no sector is drained by an accident of naming
  (ideal §14b replaced "lower faction id wins" with pro rata for the same reason).
- Each draw records a `trade-foundation` `stock-deltas` entry with fact kind `consume` (ask A10 widens the
  closed fact-kind list).
- Runs only when the stamp grants **`counterparties.clanEconomy`** — the flag of `counterparties` **wave 3**,
  which this module shares with `empire-goods-sinks` and `conquest-consequences`, registered with that wave's
  single `RulesetVersion` bump (round 6 C1; row 17 of [../landing-order.md](../landing-order.md) §2). It used
  to gate on `counterparties.clans`, which **wave 2**'s `clan-seeding` registers — a flag spanning two waves,
  so a world stamped at wave 2 (clans on the map, no clan economy yet) would have started consuming and
  producing mid-life when wave 3 merged, moving its hash: the audit's C1 defect.

### 3. Upkeep

Loam upkeep is `LoamUpkeep`, unchanged; a clan pays it because it holds a rootbed from seed (owner
decision). No goods upkeep is charged to clans in v1: the `LoamUpkeep` structure term (`sector-yield`)
charges every owner's structures, a clan's hub included, through the same rule.

### 4. The economy report

`trade-foundation` `economy-report` gains, per clan, per good: production, consumption, sold, bought.
The report's P1 net-flow line includes clans; its assertions stay the report's own (net flow not monotone
positive; sink shares sum to 1000‰; per-stock net flow equals the stock-delta sum). It prints the clan
count; it never asserts it.

## Tunables

| Key | File | Unit | Starting value |
|---|---|---|---|
| `clan.consumptionPerTurnMilli` | `data/tuning/trade.v{n}.json` | ‰ of the turn's demand consumed | 1000 — a clan consumes what it needs each turn; lower values let clans stockpile, higher is impossible by the `min` |

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| stock, need, consumed | `long`, `checked`, widened before the multiply, one division | value-normalised goods scale with `P(Θ)` (PRINCIPLES §5) |
| `consumptionPerTurnMilli` | `int` | a bounded ratio |

## Acceptance (contract)

1. **No clan branch in production:** a clan-owned sector and a player-owned sector with identical content
   produce identical located goods in the same turn (the `sector-yield` symmetry test, run with a clan).
2. **Reconciliation, per clan per good per turn:** `Δstock = produced − consumed − sold + bought − lost`,
   equal to the sum of that turn's stock deltas for the clan.
3. **No free faucet:** a clan with no production and no purchases ends every turn with stock ≤ the turn
   before, for every good.
4. **Needs only:** a good whose demand is zero is never consumed.
5. **Bounded surplus:** a clan's stock of any good never exceeds its warehouse capacity (the halt rule),
   over a scripted multi-turn run on a synthetic world.
6. **Pro rata:** permuting the sector ids of a clan's sectors permutes, but does not change, what each
   sector loses; the total consumed is identical.
7. **Legacy:** without `counterparties.clanEconomy` the pass does nothing and the hash is unchanged; a world
   with `counterparties.clans` but not `counterparties.clanEconomy` has clans that hold ground and run no
   economy, and hashes as it did before this module.
8. The report includes a clan line and asserts reconciliation only; no clan or good count is asserted.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanEconomyTests.cs` (new): consumption, pro rata,
  reconciliation, needs-only, no free faucet.
- `tests/FusionRpg.Core.Tests/World/Economy/` (`trade-foundation`'s report): clan rows, multi-turn bound.

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Clans/ClanConsumption.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanEconomyTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.Clans|FullyQualifiedName~World.Economy"
python gk-core/scripts/audit-overflow.py
```

## Hard edges

- **Phase-internal order is `logistics-flow`'s.** This module owns its pass; the slot after settlement is
  requested of `logistics-flow` `logistics-phase` (ask A12), which fixes the order.
- **A new stock-delta fact kind** (`consume`) is a reviewed widening of `trade-foundation`'s closed list
  (A10).

## Dependencies

| Consumes | From |
|---|---|
| `NeedVector.DemandOf` | `need-vector` |
| Clan validation | `clan-seeding` |
| Located stock, production, halt, warehouse capacity | `sector-yield` |
| The phase slot | `logistics-flow` `logistics-phase` (A12) |
| `stock-deltas`, `economy-report` | `trade-foundation` (A10) |

| Exposes | To |
|---|---|
| Clan consumption per good per turn (stock deltas) | `trade-foundation` `economy-report`; `trade-stories` (shortage facts) |

## Contradictions found

None.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: economy (P1, P2, P5), turn engine (Logistics phase), loam upkeep, tunables, numeric types.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus logistics-flow-map phase-internal order.
[x] decisions.md: phase order row (:7) — no phase added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: LoamUpkeep, LoamPhases upkeep draw.
[x] Surrounding sections read (§7.2, §10 C4, §14b clan row).
[x] No "moves goldens" claim; legacy identity is an acceptance test.
[x] No §2 invariant contradicted; the surplus bound is the shared halt, not a new cap.
[x] Corrections propagated: A10 and A12 in the map.
[x] No population pinned.
[x] No cache; ordering fixed by the phase owner and made id-independent by pro rata.
[x] No actor magnitude.
[x] No SOLID-violating path: production and upkeep reused; one pass added.
[ ] Registry row: none proposed.
```

## Audit 2026-09-20

Checked and clean: no clan branch in production (asserted by a symmetry test); consumption is a sink
proportional to what a clan needs and bounded by what it holds (`min`), drawn pro rata across sectors with an
ordinal remainder; reconciliation per clan per good per turn; `consume` is a requested `FactKinds` widening (A10);
the surplus bound is the shared production halt, not a new cap; no clan count is asserted. P2 holds through the
shared loam upkeep and the seeded buildings' structure terms. **Verification boundary:** the
`core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md` *Audit 2026-09-20*); the
`TurnEngine.cs` edit stays on `core-fallback`.

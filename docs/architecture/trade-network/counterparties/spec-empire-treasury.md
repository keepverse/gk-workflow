# Spec: `empire-treasury`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `empire-treasury`, row 4 of the
[counterparties map](../counterparties-map.md) (wave 1). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.4 (*"it holds a per-world treasury
(world-scoped, hashed)"*), principles 9 and 10, §14b (*"Each AI empire holds a per-world, hashed
treasury (world stock)"*). **Owner decision 2026-09-19: this program owns the AI-empire treasury.**
**Reconciled 2026-09-19** with the round-4 register ([../decisions-round-4.md](../decisions-round-4.md) B:
a bank point is a **Counting House**) and with `exchange` ask E-A12 (settlement never touches a treasury).
**Round 5 (2026-09-20)**, R5-X: **X3** — this module is the AI treasury's **writer**, registered into
`sector-yield` `banking-fact`'s hand-off point (the destination seam, §3); **X2** — settlement fact kinds are
`exchange`'s five, so this module uses no `settle` kind (§2).
Session record: `tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Each AI empire — the dominant enemy empire and every rival — holds a **per-world, hashed, unlocated
treasury**: a sparse per-good balance where goods that reach its bank points land. It is the AI's
equivalent of the player's wallet, applied symmetrically (principle 10): because it has no location,
capturing any sector — the capital included — never hands it to anyone (principle 9). It is a world
stock; it never feeds an account-scoped path.

Success looks like: an enemy empire's banked goods survive the loss of any sector unchanged; its balance
over a turn reconciles exactly to what it banked and sank; the balance is never negative;
a world with no AI treasury hashes as it does today.

## Scope and non-goals

**In scope:** the balance, its canonical rows and persistence, the one credit/debit API every writer
uses, the banking destination the AI's banking facts land in, last turn's banked amount (the income
`trade-ai` reads), the owner-only view read, and the registry row.

**Non-goals:** producing or banking goods (`sector-yield` `banking-fact` emits the fact; this module is
where an AI's fact lands); what the treasury is spent on (`empire-goods-sinks` only — `exchange`
settlement never reads or writes a treasury, E-A12); collapse rules (`conquest-consequences` calls `Destroy`); the player's wallet
(Data-side, `trade-foundation` `material-ledger`); clans (they bank nothing — their goods stay in their
warehouses, `clan-economy`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Faction rows are hashed state, with conditional extra rows when off default | `gk-core/src/FusionRpg.Core/World/WorldState.cs:70-94`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:29-30`, `:94-98` |
| An AI faction has no soul balance; souls are a player-keyed ledger | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:145-149` |
| Own-resource reads through the view are live, owner-only, and never fogged | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:45-52` |
| Overflow discipline for world magnitudes: `long`, `checked`, one division | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:17-25` |

### Wiring gap

None.

### Real gap

The treasury, its banking destination and its registry row.

## Design

### 1. State

```csharp
namespace FusionRpg.Core.World.Trade.Treasury;     // (new)

public sealed record TreasuryEntry
{
    public string FactionId { get; init; } = "";
    public string GoodId { get; init; } = "";      // a located-good id (sector-yield's catalog)
    public long Balance { get; init; }             // >= 0, value-normalised units
    public long BankedLastTurn { get; init; }      // credited by banking facts during the last resolved turn
}
```

`WorldState` gains `IReadOnlyList<TreasuryEntry> Treasury`, sorted by `(FactionId, GoodId)` ordinally. An
entry exists only while `Balance != 0 || BankedLastTurn != 0` (sparse).

- **Who has one:** factions of kind `Zomboss` (the dominant enemy empire) and `Rival`. The player banks to
  the unlocated wallet; a clan and the wild have none. A credit for any other kind throws — a programming
  error, not a report line.
- **What it holds:** located-material-class goods only (the class `sector-yield`
  `located-goods-registry` lands, ideal §14b). Rubble, ironwork, loam and recruits never enter it.
- `BankedLastTurn` is history, not a function of current state (the belief precedent,
  `WorldState.cs:344-351`); it is reset at the start of the banking step each turn and credited by that
  step. `trade-ai` `ai-spend-limit` reads it as *"income"*.

### 2. The one API

```csharp
public static class EmpireTreasury
{
    public static WorldState Credit(WorldState w, string factionId, string goodId, long qty, string factKind,
                                    StockDeltaRecorder deltas);
    public static (WorldState World, bool Ok) TryDebit(WorldState w, string factionId, string goodId, long qty,
                                    string factKind, StockDeltaRecorder deltas);   // refuses beyond balance
    public static WorldState Destroy(WorldState w, string factionId, StockDeltaRecorder deltas); // collapse
    public static long BalanceOf(WorldState w, string factionId, string goodId);
}
```

- Every mutation records a `trade-foundation` `stock-deltas` entry, so the world-stock ledger (P14) has
  one row per change, deduped on the `ledger-keys` key. Fact kinds used: `bank` (from
  `trade-foundation`'s closed list), plus `sink` and `collapse`, added to that list by this module's
  change (filed ask A10). **No settlement kind** (round 5 X2): the ledger's settlement kinds are
  `exchange`'s five (`settle-buy`, `settle-sell`, `fee`, `tariff-grant`, `tariff-sink`,
  `../exchange/spec-settlement-payment.md` §5), and settlement never writes a treasury (E-A12) — trade
  reaches a treasury only as banked goods. The first draft's single `settle` kind is withdrawn.
- The treasury is unlocated, so its ledger key carries **no sector**. The `ledger-keys` grammar widens
  its sector field to a **holder**, and `trade-foundation` answered A10 with a third holder prefix,
  `f:<factionId>`, and a `Faction` member of `stock-deltas`' `StockHolderKind`, added in this module's change
  (`../trade-foundation/spec-ledger-keys.md` §4a *Holder widening*). *(Re-pointed by the 2026-09-20 audit: this
  bullet still asked for an "unlocated sector value", which `trade-foundation` rejected as a sentinel.)*
- `TryDebit` beyond the balance returns `Ok = false` and writes nothing: a spend is refused, never
  clamped, and a balance can never go negative.

### 3. The banking destination (resolves a contradiction between sibling maps)

`sector-yield` `banking-fact` emits the banking fact inside `Step`; **where** it lands depends on the
owner. This module registers the AI destination into a `banking-fact` seam:

```csharp
public interface IBankingDestination { bool Accepts(WorldFaction owner); WorldState Land(...); }
```

- `banking-fact` owns the seam and the player's destination (the wallet, settled Data-side in the
  commit). `empire-treasury` registers `AiTreasuryDestination` for `Zomboss` and `Rival` owners.
- **Until this module lands, an AI empire's goods do not bank.** They stay in its bank-point warehouse,
  where production halts at capacity (`sector-yield` `production-halt`) — the same throttle the player
  meets, and nothing is minted. This replaces `sector-yield-map.md` §2.9's *"an AI empire's fact credits a
  per-world, hashed treasury on its faction … a faucet with no reader"*: there is no interim faucet at
  all. Dependency direction stays one way — `empire-treasury` depends on `banking-fact`'s seam, never the
  reverse.
- **Round 4: an AI empire banks only at a Counting House** (the register's bank point, replacing the earlier
  default capability on the Vault slot). Every empire starts as the player does — the player's first-throttle
  answer is *"build a Counting House"* — so an AI empire's treasury fills only after its policy builds one
  through the ordinary build path (map ask A17 to `trade-ai`). Until then its goods wait in its warehouses
  and production halts at capacity, the same throttle the player meets.

### 4. Canonical form and persistence

- One conditional row per entry after the existing rows:
  `treasury <FactionId> <GoodId> <Balance> <BankedLastTurn>`. An empty treasury writes nothing, so a
  legacy world's hash does not move.
- Table `rpg_world_treasury (world_id, faction_id, good_id, balance, banked_last_turn, PRIMARY KEY
  (world_id, faction_id, good_id))` (new). The diff writer upserts changed entries and deletes an entry
  that became zero — the table is the balance projection; the audit trail is the world-stock ledger.

### 5. The view

`IWorldView` gains `long OwnTreasury(string goodId)`: the viewing faction's own balance, zero for anyone
else's — the `OwnLoamStock` rule (`IWorldView.cs:45-52`). A treasury is private; no faction sees another's.

### 6. The registry row (lands in this module's change)

A row in `empire-resource-ssot.md` §3:

| Id / family | Class | Held by | Faucets | Sinks | Conversions |
|---|---|---|---|---|---|
| **AI empire treasury** `.{good}` | World stock (faction-held, unlocated) | Each AI empire, per world | Banking facts at its bank points (Counting Houses, round 4) | `empire-goods-sinks`; destruction on collapse | None |

P4 is the banked good's own. P6 (two competing sinks on different horizons): the compound cost of **a new
building** (a feature now) against the compound cost of **a tier upgrade** (a wider feature later) — round 4
gives every AI empire the same building ladders the player has. *(Corrected 2026-09-19 for `exchange`
E-A12: the first draft listed trade receipts as a faucet and trade payments as a sink; `exchange`'s
settlement pays and receives only through consignments and located stock, which then bank through the
ordinary banking fact — so trade reaches the treasury only as banked goods, never as a second channel.)*
The row is written when the module ships, not by this spec.

### 7. The capability flag

`counterparties.treasury` joins `world-stamp`'s registry — in **`counterparties` wave 1**, sharing that
wave's single `RulesetVersion` bump with `counterparties.needs`, `.roster` and `.diplomacy` (round 6 C1;
row 15 of [../landing-order.md](../landing-order.md) §2). Without it the destination is not registered and
the list stays empty.

**Round 6 C3 — nothing credits a treasury until the banking step lands.** This module registers into
`sector-yield` `banking-fact`'s destination seam (CM3 / round 5 X3), and that module's **step** half waits on
`material-ledger` → `save-identity` SE4.12 → SE4.38 (`sector-yield/spec-banking-fact.md` §1a; round 6 C3 is
*"wait"*). Consequence, stated rather than left to be discovered: this module may land — the field, the
canonical row, the seam registration, the sink and collapse rules — and the treasury will read **zero** for
every empire until the banking step ships, because banking is its only faucet (E-A12: settlement never
writes a treasury). Its acceptance must therefore prove the arithmetic on injected facts, never on a
scripted campaign's banked total, and the economy report's treasury line prints zero **with that reason**.

**Round 6 CQ2 — the recurring drain.** Legion equipment and doctrine upkeep may draw on banked goods when
local stock runs short, symmetrically for the player and every AI. Those draws debit this treasury through
the `sink` kind with the two reasons `empire-goods-sinks` defines (`spec-empire-goods-sinks.md` §5), which is
what stops the treasury from being a faucet with no finite sink. No new fact kind and no new holder prefix:
`sink` and `f:<factionId>` already cover it.

## Tunables

None of its own. Quantities arrive from `sector-yield` (banking) only (E-A12), with
their own keys.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `Balance`, `BankedLastTurn`, every `qty` | `long`, arithmetic `checked` | value-normalised goods scale with `P(Θ)`; `int` whole units overflow at Θ 103,557 and per-mille at 3,213 (PRINCIPLES §5). No multiply or divide on this path: add and subtract only |

## Acceptance (contract)

1. **Never negative:** every `TryDebit` beyond balance returns `Ok = false` with the world unchanged;
   property test over random credit/debit sequences.
2. **Unlocated:** capture of any sector, including every seat, leaves every treasury entry unchanged
   (asserted by a claim scenario and by a fade scenario).
3. **Who holds one:** a credit to the player, a clan or the wild throws.
4. **Reconciliation, per faction per good per turn:** `Δbalance = banked − sunk − destroyed`
   (no trade term — E-A12), equal to the sum of this turn's `stock-deltas` for the treasury. No population is counted.
5. **Sparse:** a zero entry writes no canonical row and no table row; a world with no treasury hashes
   byte-identically to the same world before the module.
6. **Round-trip:** save, load, re-hash give the same bytes.
7. **Owner-only view:** `OwnTreasury` is the true balance for the viewer and zero for every other faction.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Treasury/EmpireTreasuryTests.cs` (new): API, refusal,
  reconciliation, capture invariance, sparse canonical form, kind guard.
- `gk-core/tests/FusionRpg.Data.Tests/WorldGraphDiffTests.cs` (extend): upsert/delete-at-zero, round-trip. In
  memory.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs','tests/FusionRpg.Core.Tests/World/Trade/Treasury/EmpireTreasuryTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.Treasury"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldGraphDiff|FullyQualifiedName~WorldStore"
python gk-core/scripts/audit-overflow.py
```

Crosses Core and Data: the full suite once at module end.

## Hard edges

- **Registry gate.** The treasury is a new quantity: it is not finished until its §3 row lands in the same
  change (`empire-resource-ssot.md` §5).
- **Cross-map ownership.** `sector-yield`'s `banking-fact` must expose the destination seam rather than
  write a treasury field itself; its spec is written by its own session (ask A11).

## Dependencies

| Consumes | From |
|---|---|
| The banking fact and its destination seam | `sector-yield` `banking-fact` (A11) |
| Located-good ids | `sector-yield` `located-goods-registry` |
| `stock-deltas`, `ledger-keys` (plus `sink`, `collapse`, the `f:` holder / `StockHolderKind.Faction` — A10) | `trade-foundation` |
| Capability flag registry | `trade-foundation` `world-stamp` |

| Exposes | To |
|---|---|
| `EmpireTreasury.Credit` | `sector-yield` `banking-fact` (through `AiTreasuryDestination`) |
| `EmpireTreasury.TryDebit/BalanceOf` | `empire-goods-sinks` (not `exchange` — E-A12) |
| `EmpireTreasury.Destroy` | `conquest-consequences` |
| `BankedLastTurn`, `IWorldView.OwnTreasury` | `trade-ai` `ai-spend-limit`, `need-vector` (stock source) |

## Contradictions found

1. **Two maps define the AI treasury.** `sector-yield-map.md` §2.9 has `banking-fact` touch
   `WorldState.cs` for the AI treasury and add its registry row; this map's module 4 owns the balance.
   `logistics-flow-map.md` C7 asked the two maps to pick one owner. **Decided by the owner 2026-09-19:**
   this program owns it. Resolution: `banking-fact` owns the destination seam and the player's
   destination; this module owns the balance, the AI destination and the registry row. Recorded in the
   counterparties map; the `sector-yield` map is outside this fence and is noted for its spec (A11).

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: world state and hash, economy registry (a new quantity), Data persistence, view.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus logistics-flow-map C7 and
    sector-yield-map §2.9.
[x] decisions.md: Empire resource registry (:108) — the row lands with the module.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: WorldFaction record, canonical conditional rows, soul ledger keying,
    OwnLoamStock, LoamUpkeep overflow comment.
[x] Surrounding sections read (§7.4, principles 9-10, §14b rows).
[x] No "moves goldens" claim; sparse-hash identity is an acceptance test.
[x] No §2 invariant contradicted; no ceiling (a refused spend is not a cap on a magnitude).
[x] Corrections propagated: C7 and ask A11 in the map.
[x] No population pinned.
[x] No event-refreshed cache.
[x] No ordering fixed beyond the phase-internal order logistics-flow owns.
[x] No actor magnitude.
[x] No SOLID-violating path: one balance, one API, one destination seam.
[ ] Registry row: the empire-resource-ssot row is owed at build time (stated in Hard edges).
```

## Audit 2026-09-20

Fixed here: the ledger holder for an unlocated treasury follows `trade-foundation`'s answer (`f:<factionId>`,
`StockHolderKind.Faction`), not the sentinel sector value this spec asked for. Opened (map **CQ2**): §6's P6
answer is two **one-off** sinks (a new building, a tier upgrade); once an empire's ladders are complete the
treasury has a perpetual faucet and no drain — P1 inflation and no P2 upkeep term. The registry row in §6 is not
complete until CQ2 names a recurring sink. Checked and clean: never negative (refused, never clamped); unlocated
(capture invariance); sparse canonical rows; `long` add/subtract only, `checked`; owner-only view.
**Verification boundary:** the `core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md`
*Audit 2026-09-20*); Data tests in memory; the full suite once at module end.

# Spec: `income-parity`

**Status:** written 2026-09-19 (round-4 reconciliation) against `features/mega-merge`. Every `file:line`
below was opened in this session. Module 2.11 of the [sector-yield map](../sector-yield-map.md), added by
owner decision **Q11** in [../decisions-round-4.md](../decisions-round-4.md) (*"Income parity — owned by
**sector-yield**"*). Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §8.6 (*"Income
parity. Income with a location — a delve door, a battle sector — lands in that sector's warehouse and
travels like any yield. Expedition hauls, which have no world location, bank as today."*).

Umbrella note: [../../trade-network-map.md](../../trade-network-map.md) §1 once placed this rule in
`logistics-flow`. Round 4 Q11 moved it here, and round 5 X6 (2026-09-20) corrected the umbrella text,
which now names `sector-yield` `income-parity`.

## Objective

Keep every income that happens **somewhere on the map** on the map, so trade and logistics cannot be
bypassed by earning goods in a fight instead of producing them. A material or soul reward whose source
has a world sector lands in that sector's warehouse as a located good and reaches the wallet only
through the same flow and banking every yield takes. A reward with no world location (an expedition
haul, a Sanctum delve, a web wave) is credited to the wallet exactly as today.

Success looks like: on a trade-stamped world, a won district assault that drops fire essence adds fire
essence to that sector's warehouse, not to the wallet; on a legacy world the same drop credits the wallet
as today; and no located reward is ever credited twice, or both to the wallet and to a warehouse.

## Scope and non-goals

**In scope:** the closed set of located income sources; the rule that diverts a located source's
material and soul grants into a warehouse; the logged per-turn input that carries them into `Step`; the
credit in `Step`; the stamp gate; the P1 report line.

**Not in scope:** rolling any loot (the loot pipeline, unchanged); items and creatures (trade goods in v1
are located goods only, ideal §12); moving the income afterwards (`logistics-flow`); banking
(`banking-fact`); recording a delve's door sector (the delve program's field, see Dependencies).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| A loot manifest's `Material` grants and its `souls` `Currency` grants are credited to the wallet at persist time, inside the caller's transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs:649`, `:667-700` (`CreditManifestGrantsUnlocked`) |
| The closed loot source kinds, including the two world-located ones (`world-sector`, `siege-assault`) and the three delve ones | `gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs:58-59` |
| A delve records the map world it was entered from (null for a Sanctum entry), but not the sector | `gk-core/src/FusionRpg.Core/Delve/Domains/DelveStart.cs:7-13` (`ParentWorldId`) |
| Expedition essence is credited straight to the wallet | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:132-136` |

### Wiring gap

| What is inert | Evidence | Consequence |
|---|---|---|
| Claim loot and siege loot resolve a loot source only when `Step` is given `PowerTuning`, which the commit never passes, so neither rolls today | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:124-133`; `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:82-97`; `sector-yield/spec-essence-loop-read.md` wiring gap | This module is correct whether or not those paths are woken; waking them stays their program's change (`drop-tables`) |
| A delve does not record its door sector | `DelveStart.cs:11-13` | Delve rewards bank as today until the delve program records the door sector (ask below) |

### Real gap

No reward with a location lands in a warehouse; no logged input carries Data-side rewards into `Step`.

## Design

### 1. Located income sources — a closed set

`LocatedIncomeSources` (Core, `src/FusionRpg.Core/World/Goods/LocatedIncome.cs`, new) maps a loot
`SourceKind` to whether it is located and how its sector is found:

| Source kind | Located? | Sector |
|---|---|---|
| `world-sector` | yes | the claimed sector (the source id is the sector id) |
| `siege-assault` | yes | the district's sector (the source id is `"{sectorId}:{turn}"`, `SiegeLoot.cs`) |
| `dungeon-room`, `dungeon-clear`, `dungeon-quest` | yes, **when** the delve records a door sector on a map world; otherwise no | the door sector |
| `expedition-tier`, `web-wave`, the undesigned kind | no | — |

The table is a closed vocabulary joined against `DropTableValidator.KnownSourceKinds` by a test: a new
source kind must be classified here in the change that adds it (a reviewed change), never defaulted.

### 2. The divert (Data, at persist time)

`CreditManifestGrantsUnlocked` gains one branch, before it credits anything: when the manifest's source
is located, its sector's world is a **map** world whose stamp grants `trade.incomeParity` (see §5), the
`Material` and `souls` grants are **not** credited to the wallet. Instead one `located_income` row per
(grant) is written in the same transaction:

```
rpg_located_income(save_id, world_id, source_kind, source_id, sector_id, good_id, qty,
                   earned_turn, applied_turn NULL)   UNIQUE(world_id, source_kind, source_id, good_id)
```

Born Tier A (`save_id`, then the world's own keys), per `spec-save-identity.md`'s rule for a new table.
Two files write it and no other: `RpgStore.Loot.cs` (the divert, insert only) and `RpgStore.WorldTurns.cs`
(the commit, `applied_turn` only). That is registered as a row of `trade-foundation` `material-ledger`'s
`guard-ledger-writers` registry (`scripts/ledger-writers.v1.json`: `rpg_located_income`, those two
writers, `RpgStore.cs` reset-only) in this module's change — the guard already exists for exactly this
("the next ledger adds a row, not a script").
Items in the same manifest are untouched (they mint as today). The drop log's `(player_id,
correlation_id)` early return still runs first, so a retried resolution writes nothing twice
(`RpgStore.Loot.cs:653-660` doc).

### 3. The logged input (Data → `Step`)

At the next turn commit of that world, the commit reads every `located_income` row with
`applied_turn IS NULL`, in `(source_kind, source_id, good_id)` order, and passes them to `Step` as a new
optional input `IReadOnlyList<LocatedIncome>` beside the commands. The same list is written into the
turn-log row with the commands, so replay passes the identical input (the CM1 pattern: a logged
per-turn input, never a live read of a Data-side store). In the same transaction the rows are stamped
`applied_turn = turn`.

### 4. The credit (inside `Step`)

In `Production`, after `yield-structures`' step and only on a stamp granting `trade.incomeParity`, each
`LocatedIncome` is credited to its sector through the one credit function
(`LocatedProduction.Credit`, `spec-production-halt.md`) with `CreditMode.FullCredit` and factKind `income`: an earned reward is never
refused for want of room. The whole quantity lands; a sector pushed over capacity simply halts its own
production until it drains (decision 22 holds for production; the reward is not production). The
stock delta carries factKind `income` (a new `ledger-keys` member, added by this module).

The goods land in the sector whoever holds it at credit time: a located good belongs to the sector
(`located-goods-registry` §2 row: *"capture moves it with the sector"*). No faction argument is read.

### 5. The capability

A new flag `trade.incomeParity` in `world-stamp`'s registry, registered here in this module's own change
with the one `RulesetVersion` bump this wave takes (round 6 C1). This module is **`sector-yield` wave 6**,
row 10 of [../landing-order.md](../landing-order.md) §2.

Its `IntroducedAtRuleset` is **not below** `trade.logistics`'s: without flow, a reward landed away from a
bank point could never reach the wallet. The landing order puts it after `trade.logistics` (row 5) and also
after `trade.banking` (row 8), which is the stronger constraint of the two: until the banking step lands,
nothing credits a wallet from a warehouse at all, so a located reward would sit in the sector indefinitely.
Both are registry values and an order, not code dependencies. On any stamp without the flag, rewards credit
the wallet exactly as today.

### 6. P1

The same change adds the `income` faucet to `trade-foundation`'s economy report with its sinks named
(banking, trade, lane loss, capture), exactly as `yield-structures` did for `produce`.

## Tunables

None. Which sources are located is structural; quantities are the loot tables'.

## Numeric types

`long` quantities, `checked` sums (two incomes of one good in one sector in one turn add).

## Acceptance (contract)

1. **Legacy / unflagged:** on a stamp without `trade.incomeParity`, every loot credit is byte-identical to
   today (wallet materials and soul ledger rows unchanged; no `located_income` row written).
2. **Divert:** on a flagged map world, a located manifest's material and soul grants write
   `located_income` rows and credit no wallet row; its items mint as today.
3. **Non-located:** an expedition, web-wave or Sanctum-delve manifest credits the wallet as today on any
   stamp.
4. **Exactly once:** re-persisting the same manifest writes nothing new; re-committing the same turn
   credits nothing twice (`UNIQUE` + `applied_turn`); replay re-derives the same `Step` output from the
   logged input and writes nothing.
5. **Full credit:** a sector at capacity still gains the whole income quantity; its next production halts
   (`production-halt` acceptance 6 holds: nothing is removed).
6. **Reconciliation:** for every good and turn, Σ `income` stock deltas = Σ applied `located_income` rows.
7. **Closed set:** every `DropTableValidator.KnownSourceKinds` member is classified in
   `LocatedIncomeSources` (a join test, not a count).
8. **No faction branch:** identical incomes to identical sectors owned by different faction kinds produce
   identical stock.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Goods/LocatedIncomeTests.cs` (new): items 5–8.
- `tests/FusionRpg.Data.Tests/World/LocatedIncomePersistenceTests.cs` (new, in-memory store): items 1–4.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'src/FusionRpg.Core/World/Goods/LocatedIncome.cs',
  'gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs',
  'tests/FusionRpg.Core.Tests/World/Goods/LocatedIncomeTests.cs',
  'tests/FusionRpg.Data.Tests/World/LocatedIncomePersistenceTests.cs') -Session <active-session-id>
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
```

Crosses Core and Data: the full suite runs once at module end (AGENTS.md "Verification boundary",
point 2).

## Structure

```
src/FusionRpg.Core/World/Goods/LocatedIncome.cs         (new) — source table, LocatedIncome record, Production step
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs             MODIFIED — optional income input; one call in Production
src/FusionRpg.Core/World/Ledger/FactKinds.cs            MODIFIED — + income
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs              MODIFIED — divert branch
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs        MODIFIED — read, log, stamp applied rows
the world-stamp capability registry                      MODIFIED — + trade.incomeParity
tests/…                                                  (new, above)
```

## Boundaries and hard edges

- **Always:** one credit function; a logged input, never a live read inside `Step`; the stamp gate.
- **Ask first:** diverting items or creatures; refusing a reward for want of room.
- **Never:** credit a located reward to the wallet on a flagged world; read `rpg_located_income` from Core.
- **Hard edge — turn log shape.** The turn log gains the income list beside the commands; an old log row
  reads it as empty, so every stored turn replays unchanged.

## Dependencies and interface

**Depends on:** `located-stock`, `production-halt` (the credit function, `FullCredit` mode), `warehouse-axis` (occupancy), `located-goods-registry`;
`trade-foundation` `world-stamp`, `ledger-keys`, `stock-deltas`, `economy-report`. Capability ordering (not a
code dependency): `trade.incomeParity` is introduced no earlier than `logistics-flow`'s `trade.logistics`.

**Asks of other programs:**

| # | To | Ask |
|---|---|---|
| IP1 | party-dungeon (delve start) | Record the map door's **sector id** beside `ParentWorldId` (`DelveStart.cs:11-13`), so delve rewards from a map door are located. Until then they bank as today — a declared gap, not a hidden one |
| IP2 | `drop-tables` | When claim loot and siege loot are woken (the unpassed `PowerTuning`), their manifests flow through this divert with no further change |

| Exposed | Consumer |
|---|---|
| `LocatedIncomeSources`, `trade.incomeParity` | `trade-surface` (a reward notice says "landed at <sector>"), `trade-stories` |
| factKind `income` | `world-stock-ledger`, `economy-report` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: loot persistence (Data), world turn (Production), economy registry, world stamp.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check was not re-run (docs only).
[x] Read this session: decisions-round-4 (Q11), trade-network-ideal §8.6, the sector-yield specs this
    module calls, the loot persistence path.
[x] decisions.md: registry row (:108) — the located-goods row gains `income` as a faucet in this change.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file.
[x] Verified against code: the manifest credit, the source kinds, the inert world loot, the delve's
    ParentWorldId without a sector.
[x] Surrounding sections read: CreditManifestGrantsUnlocked's doc comment; ClaimResolver's inert-loot note.
[x] Constraints tested, not assumed: none claimed; legacy identity is acceptance 1.
[x] No §2 invariant contradicted: P13 (logged input), P14 (unique rows, dedupe), no faction branch.
[x] Corrections propagated: umbrella §1 ownership sentence reported (not this session's file).
[x] No population pinned; the source table is a closed vocabulary joined against the validator's list.
[x] No event-refreshed cache.
[x] Ordering: re-persist and re-commit are idempotent in any order.
[x] No actor magnitude.
[x] No SOLID fork: the one credit function, the one loot pipeline, the one ledger grammar.
[~] Registry row: the table's two-writer rule is a `ledger-writers` registry row (§2, added in the audit
    of 2026-09-20). "No located reward credits the wallet on a flagged world" still needs a guard or an
    unguardableReason row when the module lands (acceptance 2 is its test).
```

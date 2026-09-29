# Spec: `world-stock-ledger`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `world-stock-ledger`, §2.7 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; depends on `stock-deltas`, and
on `ledger-keys` through it). Principle P14 ([../../economy-principles.md](../../economy-principles.md));
umbrella invariant 6; save-identity's rule for a table created after it
(`docs/architecture/solid-enforcement/spec-save-identity.md:594-603`).

## Objective

World stocks have no ledger: the balance is a hashed field on `WorldSector`/`WorldEntity`, persisted only
by the diff writer, and nothing records why it moved. This module adds an **append-only ledger table**,
written inside the turn commit transaction from `TurnResult.StockDeltas`, one row per aggregated delta,
deduped on the `ledger-keys` key. The balance stays where it is — the hashed field is still the state;
the ledger is the audit and the input to reports. Later sub-programs (banking, delivery, settlement)
write their world facts through the same table and key.

Success looks like: after any number of committed turns, for every holder and stock of a world, the sum
of its ledger rows equals the persisted stock; committing the same rows twice writes nothing the second
time; and a failed commit leaves neither the diff nor the ledger rows behind.

## Scope and non-goals

In scope: the table, its writer inside `CommitWorldTurn`, opening balances, read queries, and their
tests.

Not in scope: account-scoped (banked) facts (`material-ledger`); changing how stocks are stored or
hashed; trimming the ledger.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The commit: `Step`, then the diff writer, relic spend, cargo pass, retrieval missions, re-hash, turn-log insert, turn advance, decay tick, one `tx.Commit()` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:493`, `:601-702` (diff `:607`, commit `:702`) |
| Only the diff writer and creation write `rpg_world_sectors`; post-step passes touch `rpg_world_entities` only for `movement_remaining` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:152`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:286`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs:114` |
| A world's save is `rpg_worlds.player_id` | `RpgStore.World.cs:20-35` |
| Creation writes the whole graph in one transaction after validation | `RpgStore.World.cs:219-254` |
| The soul ledger's shape: append-only rows, `UNIQUE(…, dedupe_key)`, `INSERT OR IGNORE`, "true when newly inserted" | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:684-696`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:138-168` |
| The command log is never trimmed; reports are trimmed to a hot tail | `RpgStore.WorldTurns.cs:237-240` (comment), `:703` (`TrimWorldTurnReportsUnlocked`) |
| New tables are born with their owner columns; `empire_id` shares the world `faction_id` id space | `spec-save-identity.md:594-603`, `:77` |
| Store tests run in memory | `docs/contributing/testing-standard.md` (via PRINCIPLES §7) |

### Real gap

No world-stock ledger.

## Design

### 1. Table (`src/FusionRpg.Data/Sqlite/RpgStore.WorldLedger.cs`, new)

```sql
CREATE TABLE IF NOT EXISTS rpg_world_stock_ledger (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  save_id          INTEGER NOT NULL,   -- rpg_worlds.player_id
  world_id         TEXT    NOT NULL,
  turn             INTEGER NOT NULL,
  owner_faction_id TEXT,               -- the holder's owner at the change; NULL = unowned ground
  holder           TEXT    NOT NULL,   -- 's:<sectorId>' | 'e:<entityId>' (+ 'f:' treasury, 'r:' route — ledger-keys §4a)
  stock_id         TEXT    NOT NULL,   -- WorldStockRegistry id
  fact_kind        TEXT    NOT NULL,   -- FactKinds member, world scope
  delta            INTEGER NOT NULL,   -- signed, never 0
  dedupe_key       TEXT    NOT NULL,   -- LedgerKey.Encode(world fact)
  committed_utc    TEXT    NOT NULL,
  UNIQUE (dedupe_key)
);
CREATE INDEX IF NOT EXISTS ix_rpg_world_stock_ledger_holder
  ON rpg_world_stock_ledger (world_id, holder, stock_id);
CREATE INDEX IF NOT EXISTS ix_rpg_world_stock_ledger_turn
  ON rpg_world_stock_ledger (world_id, turn);
```

**Keying class.** The rows are facts of one world instance, attributed to a faction that may be an
empire, a clan, the wild, or nobody. The table is born with `save_id` (Tier A's first column) and an
owner column in the `empire_id` id space, named `owner_faction_id` because a clan or an unowned sector is
not an empire (`ledger-keys` §3). The dedupe key already carries save, owner, world, turn, kind, holder
and stock, so `UNIQUE (dedupe_key)` is the whole uniqueness contract.

### 2. Writing inside the commit

`AppendWorldStockLedgerUnlocked(db, tx, header, turn, IReadOnlyList<StockDelta>, now)` runs right after
`DiffWorldGraphUnlocked` (`RpgStore.WorldTurns.cs:607`), in the same transaction:

1. **Opening balances, once per world.** If the world has no ledger row yet, write one `open` row per
   non-zero holding of the **pre-step** world (`WorldStockRegistry.All` holdings), keyed at the current
   turn. This covers worlds created before this module and needs no migration. `CreateWorld` writes the
   same `open` rows at creation, so a world created after this module never takes this branch.
2. **The turn's deltas:** one `INSERT OR IGNORE` per `StockDelta`, keyed
   `LedgerKey.Encode(world fact(save, owner, world, turn, factKind, holder, stock))`.

Both steps share one prepared command, reused across rows (the prepared-per-table pattern,
`RpgStore.World.cs:256-283`). Rows are written in the recorder's order (`stock-deltas` §3), so `id` order
within a turn is stable.

### 3. Reads

- `ListWorldStockLedger(worldId, fromTurn, toTurn)` — rows in `(turn, id)` order.
- `SumWorldStockLedger(worldId)` — `(holder, stock_id) → SUM(delta)`.

### 4. Retention

Never trimmed, like the command log: the ledger is what a report or a surface reads for any past turn,
and what the reconciliation contract sums. Its size is a reading (sectors × stocks + entities per turn);
if it ever needs compaction, a watermarked snapshot row on the soul ledger's model is the path, and it is
a later, separate change.

### 5. Numeric types

`delta` is SQLite `INTEGER` (64-bit), read and written as `long`. Sums use `long` and `checked` in C#.

## Tunables

None.

## Acceptance criteria (contract)

1. Committing a turn writes exactly one row per `StockDelta` of that turn's `TurnResult` (plus the
   opening rows on a world's first ledgered commit).
2. Re-running the append with the same deltas for the same `(world, turn)` inserts nothing.
3. **Reconciliation:** after a scripted multi-turn `two-hearths` campaign, for every sector and entity of
   the persisted world and every registered stock, `SumWorldStockLedger` equals the persisted value; a
   holder that no longer exists sums to 0.
4. A world created before this module (rows inserted without ledger rows) reconciles after its first
   ledgered commit — the opening branch covers it.
5. **Atomicity:** an injected failure after the ledger append and before `tx.Commit()` leaves no ledger
   row and no diff write.
6. **Closure:** every non-null `owner_faction_id` exists in `rpg_world_factions` for that world; every
   `stock_id` is a `WorldStockRegistry` id; every `fact_kind` is a world-scope `FactKinds` member; no row
   has `delta = 0`. (The save-empire half of owner closure is `save-identity` SE4.41's contract over
   `rpg_world_factions`, which covers these owners transitively.)
7. Assertions are over the contract only: no test pins how many rows a turn writes.
8. **Per holder, not per owner.** Reconciliation is asserted per `(holder, stock)`; a sector captured
   mid-run still reconciles (its rows carry both owners, in turn order), and no test derives a per-owner
   balance from the ledger (`spec-stock-deltas.md` §5, "What the record does not answer").

## Test plan and verification boundary

- `tests/FusionRpg.Data.Tests/World/WorldStockLedgerTests.cs` (new), in-memory store,
  `[Trait("VerificationId", "data.world-stock-ledger")]`.
- `gk-core/scripts/verification-boundaries.v1.json` owner row `data-world-stock-ledger`: paths
  `src/FusionRpg.Data/Sqlite/RpgStore.WorldLedger.cs` and the test file, project `data`, guards `dal`,
  `test-substrate`. `RpgStore.WorldTurns.cs` and `RpgStore.World.cs` stay on `data-fallback`.
- Verify: `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>`; `python gk-core/scripts/guard-dal.py`.

## Hard edges

- **Save format:** a new table; no existing table changes. The opening branch is the only "migration",
  and it writes only new rows.
- **No golden, no ruleset stamp:** nothing hashed changes.

## Boundaries

- **Always:** write in the commit's transaction; key through `LedgerKey`.
- **Ask first:** trimming or compacting the ledger.
- **Never:** update or delete a ledger row; read the ledger inside `Step`; treat the ledger as the
  balance.

## Dependencies and interface

**Depends on:** `stock-deltas`; `ledger-keys`. External: none required to build. The map listed
`save-identity` SE4.12 for the owner columns; with the owner as a faction id (`ledger-keys` §3) and the
save as `rpg_worlds.player_id`, the table needs no `rpg_save_empires` row to be written, and the empire
half of closure is SE4.41's. Recorded as a map correction; this lets the module land before SE4.12.

| Exposed | Consumer |
|---|---|
| `rpg_world_stock_ledger`, `AppendWorldStockLedgerUnlocked` | `sector-yield` `banking-fact` (bank facts), `logistics-flow` (deliver, loss), `exchange` (settle), `rift-trade` |
| `ListWorldStockLedger`, `SumWorldStockLedger` | `trade-surface` (turn-report entries), `world-continuity` (away digest) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world store (turn commit), economy ledgers, save identity keying.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: economy-principles P14; spec-save-identity's new-table rule and the world
    faction ↔ save empire closure; trade-foundation map §2.7. data-architecture.md not read in full
    (SQL-only-in-Data taken from PRINCIPLES §6 and guard-dal).
[x] decisions.md: Players/save-identity row (:80) — the table follows the new-table rule; no key widens.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: the commit's step order, every SQL writer of rpg_world_sectors and
    rpg_world_entities, the soul ledger's insert-or-ignore shape.
[x] Surrounding sections read (the cargo pass and re-hash block around the diff call).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted; SQL stays in FusionRpg.Data.
[x] Corrections propagated: the SE4.12 dependency and the owner column name are in the map's corrections
    section.
[x] No population pinned (criterion 7).
[x] No event-refreshed cache.
[x] Order-independent: the opening branch is keyed on "no row yet", whichever turn a world first commits.
[x] ActorHub: not touched.
[x] No SOLID fork: the soul ledger's pattern reused; one key grammar.
[x] New guarded rule: the table's single writer is this file, and material-ledger's
    `guard-ledger-writers` registry already lists `rpg_world_stock_ledger` with this file as its only
    writer (spec-material-ledger.md §5), so the rule is guarded from the day both land.
```

# Spec: `material-ledger`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `material-ledger`, §2.8 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; depends on `ledger-keys`;
external `save-identity` SE4.38). Principle P14 ([../../economy-principles.md](../../economy-principles.md)
§P14: *"Any new stock reuses that pattern"*).

## Objective

Banked materials — essence, shards, substrates, catalysts — have no ledger: the balance table is written
by upsert or conditional decrement from several places, and only recipe spends leave a log. When
`sector-yield`'s banking fact starts crediting materials from the map, a retried commit or a replay
could double-credit with nothing to catch it. This module puts materials on the P14 pattern: **one
ledger-first verb** that appends a deduped row and moves the balance, every writer of the balance table
routed through it, and a guard that fails any other SQL write.

Success looks like: for every save and material, the balance equals the sum of its ledger rows; a
repeated fact changes nothing; and the fusion, salvage, expedition, loot and recipe tests stay green with
no expected value changed.

## Scope and non-goals

In scope: `rpg_material_ledger`; the verb; opening balances for existing data; routing every current
writer through the verb; a single-writer guard and its registry row.

Not in scope: the `rpg_creature_materials → rpg_materials` rename (ruled, unscheduled —
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:20-25`); widening the balance table's key (Tier B
stays until save-identity says otherwise); AI empire treasuries (world stocks, `sector-yield`); souls
(the soul ledger already exists).

## What already exists

### Built — every SQL write to `rpg_creature_materials`

| Site | Kind | Durable fact id available there |
|---|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:184-201` `GrantMaterialsUnlocked` (upsert add) | credit | its callers': loot correlation (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs:694`, credited after the `(player_id, correlation_id)` early return, `:652-661`), workbench op (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs:156`), salvage `eventId` (`RpgStore.Workbench.cs:348-352`); the public `GrantMaterials` test/faucet seam (`RpgStore.Materials.cs:164-175`) has none today |
| `RpgStore.Materials.cs:306-318` recipe spend (conditional decrement) | debit | `(player_id, correlation_id)` of `rpg_material_spend_log` (`:57-69`) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:225-244` `AddCreatureMaterialsUnlocked` (upsert add), called at `:220` and `:312` | credit | the expedition id |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:536-552` `TrySpendCreatureMaterialsUnlocked` (conditional decrement) | debit | the fusion correlation (`:530-532`) |
| `gk-core/src/FusionRpg.Data/Sqlite/Migrations/ShardRungs.cs:60-99` (merge into live id, zero the legacy row), run at `Init` | rename | the migration itself |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1032` (`DELETE` in `Reset`) | wipe | — (dev/test reset) |

DDL: `RpgStore.cs:764-770`. Unknown ids throw at the write boundary
(`RpgStore.Materials.cs:186-187`, `:301-302`; `RpgStore.Fusion.cs:541-542`). `Init` runs schema setup and
then `ShardRungs.Migrate` (`RpgStore.cs:138-143`).

### Correction to the map

The map (§1, §2.8) counted **four** writers. There are six SQL writes: the four runtime writers, plus
the `ShardRungs` migration (two statements) and the `Reset` wipe. Both extra sites are handled below.

### Real gap

No ledger, no single writer, no dedupe for credits.

## Design

### 1. Table (`src/FusionRpg.Data/Sqlite/RpgStore.MaterialLedger.cs`, new) — born Tier A

```sql
CREATE TABLE IF NOT EXISTS rpg_material_ledger (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  save_id      INTEGER NOT NULL,
  empire_id    TEXT    NOT NULL,     -- EmpireRef; the human empire today (Tier B store)
  material_id  TEXT    NOT NULL,
  delta        INTEGER NOT NULL,     -- signed, never 0
  fact_kind    TEXT    NOT NULL,     -- FactKinds, account scope: open | grant | spend | rename
  source_kind  TEXT    NOT NULL,     -- loot | workbench | salvage | expedition | fusion | recipe | migration | seam | world-bank
  source_id    TEXT    NOT NULL,
  dedupe_key   TEXT    NOT NULL,     -- LedgerKey.Encode(account fact)
  t            TEXT    NOT NULL,
  UNIQUE (dedupe_key)
);
CREATE INDEX IF NOT EXISTS ix_rpg_material_ledger_owner
  ON rpg_material_ledger (save_id, empire_id, material_id);
```

The save-identity rule for a table created after it: empire-scoped → born `(save_id, empire_id, …)`
even when only the human empire writes it (`docs/architecture/solid-enforcement/spec-save-identity.md:594-603`).

### 2. The verb

```csharp
internal MaterialApplyResult ApplyMaterialFactsUnlocked(
    SqliteConnection db, SqliteTransaction? tx, EmpireRef owner,
    string sourceKind, string sourceId, IReadOnlyList<(string MaterialId, long Delta)> lines,
    string factKind, string nowUtc);

public enum MaterialApplyResult { Applied, Replayed, Insufficient }
```

For each line, in ordinal material order: validate the id (the existing catalog checks, throwing as
today); `INSERT OR IGNORE` the ledger row; **only if it was inserted**, move the balance — upsert-add for
a positive delta, conditional decrement (`qty >= $q`) for a negative one. A conditional decrement that
matches no row returns `Insufficient` and the caller rolls back, exactly as the recipe and fusion paths do
today (`RpgStore.Materials.cs:314-318`). If every line was already present, the result is `Replayed` and
nothing moves. Ledger first, balance second, same transaction: P14's order.

The owner is an `EmpireRef`; the store calls `RequireHumanEmpire` (SE4.37's shared check) because the
balance table is still Tier B, keyed by `player_id` = `owner.Save`.

### 3. Routing the writers

| Writer | Becomes | `factKind` / `sourceKind` / `sourceId` |
|---|---|---|
| `GrantMaterialsUnlocked` | a thin call to the verb; gains `(sourceKind, sourceId)` parameters its callers already hold | `grant` / `loot`, `workbench`, `salvage` / the correlation or event id |
| public `GrantMaterials` | requires an explicit `sourceId` | `grant` / `seam` / caller's id |
| recipe spend | the verb, keyed on the spend-log correlation | `spend` / `recipe` / correlation |
| `AddCreatureMaterialsUnlocked` | the verb | `grant` / `expedition` / expedition id (+ the claim step name, so a two-step reward is two facts) |
| `TrySpendCreatureMaterialsUnlocked` | the verb | `spend` / `fusion` / fusion correlation |
| `ShardRungs.Migrate` | the verb, two lines per stack (−legacy, +live) | `rename` / `migration` / `shard-rungs` |
| `Reset` | also deletes `rpg_material_ledger` | — |
| *(later)* `sector-yield` `banking-fact` commit credit | the verb, one line per banked material | `grant` / `world-bank` / the world `bank` fact's encoded key (`spec-ledger-keys.md` §4a) |

`source_kind` is a closed vocabulary (the column comment above), pinned in the test with the reason; the
`world-bank` member lands with `banking-fact`, the first caller that needs it.

### 4. Opening balances

`OpenMaterialBalancesUnlocked(db)` runs at `Init` **between** schema setup and `ShardRungs.Migrate`
(`RpgStore.cs:141-142`): for every `(player_id, material_id)` with `qty != 0` that has no ledger row, one
`open` row (`source_kind='migration'`, `source_id='material-ledger-v1'`) for `HumanEmpireOf(save)`. It
writes only new rows and never touches a balance, so it is additive and idempotent (a second boot finds
the rows); `decisions.md:90` reserves backups for key-widening, which this is not. Running it before
`ShardRungs` makes a legacy stack's rename move balances the ledger already knows. `HumanEmpireOf` needs
every save seeded — true once save-identity's migration unit has run, which SE4.38 (this module's
dependency) already sits behind (`tasks/solid-enforcement-todo.md:634`, deps chain through SE4.30).

### 5. The single-writer guard

`scripts/guard-ledger-writers.ps1` with registry `scripts/ledger-writers.v1.json`:

```json
{ "schemaVersion": 1, "tables": [
  { "table": "rpg_creature_materials", "writers": ["src/FusionRpg.Data/Sqlite/RpgStore.MaterialLedger.cs"],
    "resetOnly": ["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs"] },
  { "table": "rpg_material_ledger", "writers": ["src/FusionRpg.Data/Sqlite/RpgStore.MaterialLedger.cs"],
    "resetOnly": ["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs"] },
  { "table": "rpg_world_stock_ledger", "writers": ["src/FusionRpg.Data/Sqlite/RpgStore.WorldLedger.cs"],
    "resetOnly": ["gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs"] } ] }
```

It scans `src/` string literals (not comments) for `INSERT … INTO <table>`, `UPDATE <table>`,
`REPLACE INTO <table>` and `DELETE FROM <table>`: a write outside `writers` fails; a `DELETE FROM` in a
`resetOnly` file passes; any other statement there fails. One guard for every ledger-first table, so the
next ledger adds a row, not a script. Registered as guard `ledger-writers` (tier `ci`, gating) and
invariant `tn-ledger-before-balance` (source `docs/architecture/trade-network-map.md §5 invariant 6`).
`guard-dal.py` keeps its own job (SQL only in `FusionRpg.Data`).

### 6. Numeric types

`long` quantities, `checked` sums; SQLite `INTEGER` is 64-bit. Unchanged from today's `long` grants
(`RpgStore.Materials.cs:184`).

## Tunables

None.

## Acceptance criteria (contract)

1. `guard-ledger-writers.ps1` exits 0 on the real tree, and exits 1 on fixtures with a write to a
   registered table outside its writers, with a non-`DELETE` in a reset-only file, and with the statement
   only in a comment (that one exits 0).
2. For every `(save, material)`, `rpg_creature_materials.qty` equals `SUM(delta)` of that save's human
   empire's ledger rows — asserted after a scripted sequence of loot, salvage, expedition, fusion and
   recipe operations, in more than one order.
3. Applying the same `(sourceKind, sourceId, lines)` twice returns `Replayed` and changes neither table.
4. A spend larger than the balance returns `Insufficient` and, after the caller's rollback, leaves both
   tables unchanged.
5. An unknown material id still throws at the write boundary.
6. Opening: a store seeded with balances and no ledger reconciles after `Init`; a second `Init` writes
   nothing; a legacy shard stack is renamed through the ledger and still reconciles.
7. Every existing fusion, salvage, expedition, loot, workbench, shard-rung and recipe test passes **with
   no expected value changed**.
8. No test pins a row count or a material population.

## Test plan and verification boundary

- `tests/FusionRpg.Data.Tests/Materials/MaterialLedgerTests.cs` (new), in memory,
  `[Trait("VerificationId", "data.material-ledger")]`;
  `tests/FusionRpg.Guard.Tests/LedgerWritersGuardTests.cs` (new, fixture trees),
  `[Trait("VerificationId", "guard.ledger-writers")]`.
- `gk-core/scripts/verification-boundaries.v1.json`: owner rows `data-material-ledger` (the new store file and its
  tests; project `data`; guards `dal`, `test-substrate`, `ledger-writers`) and `guard-ledger-writers`
  (script, registry, guard tests; project `guard`). The edited `RpgStore.Materials.cs`,
  `RpgStore.Expeditions.cs`, `RpgStore.Fusion.cs`, `RpgStore.Loot.cs`, `RpgStore.Workbench.cs` and
  `RpgStore.cs` stay on `data-fallback`; `ShardRungs.cs` is already `data.shard-rungs`.
- Verify: `.\scripts\verify-change.py -Paths <changed files> -Session <id>`; `python gk-core/scripts/guard-dal.py`;
  `.\scripts\guard-ledger-writers.ps1`.

## Hard edges

- **Save format:** one new table and new rows only; the balance table's schema is unchanged. No backup
  owed (`decisions.md:90`).
- **Order at `Init`:** opening before `ShardRungs`, or a renamed stack's live-id balance has no opening
  row and reconciliation fails.
- **Sequencing with save-identity:** land after SE4.38 so the four writer sites are edited once, and so
  `HumanEmpireOf` resolves for every save.
- No golden, no ruleset stamp.

## Boundaries

- **Always:** ledger row before balance, same transaction; a durable source id on every fact.
- **Ask first:** widening the balance table's key; a non-human empire write.
- **Never:** SQL to `rpg_creature_materials` outside the verb's file; a credit without a source id.

## Dependencies and interface

**Depends on:** `ledger-keys`. External: `save-identity` SE4.38 (Tier B typing of the materials store,
which lands after the migration unit that seeds every save's empires).

**Round 6 C3 — this module starts after the save-identity re-key finishes.** The owner's ruling is
*"Wait. Save-identity is being built now; `material-ledger` and the banking work that needs it start after
it finishes"* ([../decisions-round-4.md](../decisions-round-4.md) Round 6 C3). So:

- The landing order is `save-identity` SE4.12 → SE4.38, then this module (row 0f of
  [../landing-order.md](../landing-order.md) §2), then `sector-yield` `banking-fact`'s **step** half
  (row 8). SE4.38 is unchecked today (`tasks/solid-enforcement-todo.md:634`) and transitively needs SE4.12
  (`:352`) and every task between; ask X-1 of the global audit reports the schedule need to that lane.
- **The audit's option (b) is not taken.** This module does *not* land on today's Tier B `player_id` key
  and re-point later: that would edit its four writer sites twice, against the rule this module exists to
  enforce. The verb is written once, against the re-keyed store.
- **Interim behaviour, stated so no other spec has to guess it.** Until this module lands, no banked
  material exists: `banking-fact`'s phase slot may land (row 4, it has no ledger dependency) and the lane
  layer may move goods to a bank point, but nothing leaves the map, no wallet or treasury is credited, and
  `economy-report` prints a banked total of zero **with that reason** rather than a silent zero.
  `sector-yield` `bank-points` still answers which sectors are bank points, so the first-throttle answer
  (*build a Counting House*) stays buildable and visible.

| Exposed | Consumer |
|---|---|
| `ApplyMaterialFactsUnlocked` | `sector-yield` `banking-fact` (banked goods credit a human empire's materials through it and nothing else) |
| `rpg_material_ledger` | `economy-report`'s banked rows (later), `trade-surface` |
| `guard-ledger-writers` + `ledger-writers.v1.json` | every later ledger-first table |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: materials store, fusion, expeditions, loot, workbench, a data migration, guards, save
    identity keying.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: economy-principles P14; spec-save-identity's new-table rule; the SE4.12-SE4.40
    task rows; trade-foundation map §2.8. item/ssot-materials-crafting.md not read this session — the
    store code was read instead.
[x] decisions.md: key-widening row (:90) — this change is additive; empire resource registry row (:108)
    — no quantity added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: all six SQL writes to the balance table (grep over src/), each call site's
    available durable id, Init's order.
[x] Surrounding sections read (the recipe spend transaction's doc comment; ShardRungs' idempotency
    argument).
[x] Constraint named, not assumed: "no expected value changes" is criterion 7, proven at build time.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the writer count is corrected in the map's corrections section.
[x] No population pinned (criterion 8).
[x] No event-refreshed cache.
[x] Order-independent: criterion 2 runs the operation script in more than one order.
[x] ActorHub: not touched.
[x] No SOLID fork: one verb for the balance; one guard script for every ledger-first table.
[x] New rule has a registry row: guard ledger-writers + invariant tn-ledger-before-balance.
```

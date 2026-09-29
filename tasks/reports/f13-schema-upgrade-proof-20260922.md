# F13 — the column a real database never gained (2026-09-22)

**Lane** `f13-schema` · **Session** `party-dungeon-f13` · **Branch** `cmdc/f13-schema` · **Base** `246228eb1`
**Worktree** `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-f13-schema`

Row: `tasks/party-dungeon-todo.md` **F13**. Original measurement: `tasks/reports/live-test-proof-20260922.md` §3.

---

## 1. The fix

`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Domains.cs` — one line at the end of `EnsureDomainsSchemaUnlocked`:

```csharp
EnsureColumn(db, "dungeon_domain", "first_clear_ref", "TEXT");
```

`first_clear_ref` is a column of the `CREATE TABLE IF NOT EXISTS dungeon_domain` in the same method, but
`CREATE TABLE IF NOT EXISTS` cannot widen a table that already exists, so an install whose table predates
the column never gains it while `ReadDomains` selects it. `EnsureColumn` (`RpgStore.cs`, `ALTER TABLE … ADD
COLUMN`) is the mechanism this repo already prescribes for schema evolution —
`docs/architecture/data-architecture.md` §2: *"Schema evolution: EnsureColumn (ALTER TABLE ADD COLUMN) only.
No table drops."* Additive only; no row is rewritten; `NULL` means "no first-clear ref authored", which is
what every pre-existing row already reads.

## 2. How the missing-column list was derived (not guessed)

1. **Head's expected schema**: built a fresh store with head code (`new RpgStore(dir).Init()`) and dumped
   `sqlite_master` + `PRAGMA table_info` for every table.
2. **Head's declared-but-lazily-registered schema**: parsed all **110** `EnsureColumn(db, "t", "c", …)`
   call sites in `gk-core/src/FusionRpg.Data/**` and unioned them with (1). This closes the hole left by
   `EnsureColumn` calls that run only on first use.
3. **The real database**: the owner's `dist/FusionRpg.Server/data/rpg-hot.sqlite`, 546,471,936 bytes,
   185 objects of `type='table'` (184 user tables + `sqlite_sequence`), copied by SQLite **online backup**.
4. **Difference**: every (table, column) head expects that the real file lacks.

Head's fresh schema has 175 user tables; the real file has 184. The 9 extra are retired/legacy only
(`demon_species`, `demon_species_magnitude`, `rpg_demon_codex/_contracts/_lineage/_materials/_profiles`,
`rpg_actor_progression__pre_save_identity`, `rpg_xp_ledger__pre_save_identity`); head code references none
of them (`grep`), and head creates **zero** tables the real file lacks.

## 3. The reading — the complete list

| # | (table, column) | head reads it at | in the real file | verdict |
|---|---|---|---|---|
| 1 | `dungeon_domain.first_clear_ref` | `RpgStore.Domains.cs` `ReadDomains` (SELECT list) | absent — `dungeon_domain` has **15** columns | **the defect** (fixed here) |
| 2 | `rpg_corpse_cache.origin_theta` | `RpgStore.CacheRetrieval.cs:318` | absent — `rpg_corpse_cache` has 10 columns | **not a defect**: `EnsureCacheRetrievalSchemaUnlocked` (which adds it, `:149`) runs at every one of its read sites first — `:215`, `:307`, `:374` all precede the read at `:430`. Its own doc comment states the lazy design on purpose. Left untouched. |

Every other (table, column) pair head reads resolves identically on a fresh store and on the real file,
because the two schemas differ in exactly these two pairs. The Data suite runs against a fresh store, so a
head read that resolved on neither would be a different (fresh-store) defect, not this one.

**Nothing else is missing.** In particular there is no missing `player_id` (see §4).

## 4. Correction to F13's diagnosis: the 8 `player_id` errors were a stale binary, not a missing column

The original reading was `'no such column: player_id'` ×8. The authoritative stack traces are in the slot
server's own log, `H:\Games\PVZ-Fusion-Tests\slot-1-server.log`:

```
FusionRpg.Data.RpgStore.ReadActorDtoUnlocked(...) in ...\src\FusionRpg.Data\Sqlite\RpgStore.Progression.cs:line 850
   at FusionRpg.Data.RpgStore.GetRpgActor(...)     ...RpgStore.Progression.cs:line 435
   at FusionRpg.Data.RpgStore.GetRpgProgressionSummary(...)  ...RpgStore.Progression.cs:line 352
   at FusionRpg.Server.DelveEndpoints.HandleGetDomains(...) ... DelveEndpoints.cs:line 67   (the 2 first_clear_ref)
```

Those two line numbers (`:850` = `ReadActorDtoUnlocked`, `:352` = `GetRpgProgressionSummary`) exist in no
checkout present today — they are the source positions of the **stale `dist/FusionRpg.Server` binary**, built
from a main commit between 2026-09-07 (`first_clear_ref` added, `git log -S`) and 2026-09-19 (`save-identity`
SE4.20, `858982da1`, moved `rpg_actor_progression`/`rpg_xp_ledger` from `player_id` to `save_id`/`empire_id`).
That window is exactly a binary with `first_clear_ref` in `ReadDomains` **and** `player_id` in
`ReadActorDtoUnlocked`. The database had since been migrated by a newer server, so the old binary's own SQL
(`WHERE player_id=…` on `rpg_actor_progression`) no longer matched its own database.

Measured directly: the real file has `rpg_actor_progression(save_id, empire_id, …)` and
`pvz_activity_facts(…, player_id, …)`; head-vs-real has **zero** missing `player_id`; and with the fix in
place the same three call sites run green against a copy of the real file (§5).

**Consequence:** `pvz_activity_facts.player_id` is **not** a missing column and there is nothing to fix
there. The activity-facts surface (`docs/architecture/pvz-activity.md`) keeps ownership of that column and of
the query at `RpgStore.Progression.cs:220`; the owning rows are **`creature-progression` D0.2** (activity
propagation and canonical replay identity — the row that owns the fact stream, currently PARTIAL) and
**`species-build` T1.3** (the `MatchEnded` award query over `pvz_activity_facts`). Both are a **no-op repair**:
the column exists in the real file and in head's own DDL, and the zero-missing-`player_id` reading in §3 is
the proof. The routing could not be appended to those todos — they are outside this lane's runner fence
(§7) — so it is recorded here and in the F13 row.

## 5. Proof (a real, pre-existing database is upgraded)

Committed, re-runnable: `tasks/reports/f13-schema-upgrade-proof.ps1`. It online-backups the real file,
boots head code's own `Init()` over the copy, and exits 1 if the column is absent or a read throws.

```
pwsh -NoProfile -File tasks/reports/f13-schema-upgrade-proof.ps1 -SourceDb "D:/Works/source/plant-vs-zombie-rise-of-summoner/dist/FusionRpg.Server/data/rpg-hot.sqlite"
```

```
=== online-backup the real database into …\f13-schema-proof-6197ea17a380463bbb6393daaad44128\data ===
backed up bytes 546471936
backed up bytes 49152
=== boot head code over the copy and read it back ===
before: tables=184 dungeon_domain has 15 columns, first_clear_ref present=False
pre-fix: SqliteException: SQLite Error 1: 'no such column: first_clear_ref'.
init: OK
ReadDomains -> 0 rows
GetRpgActor(1,plant,1) -> level 3
GetRpgProgressionSummary(1) -> player 1
after:  tables=184 dungeon_domain has 16 columns, first_clear_ref present=True
PROOF OK
```

`pre-fix:` is the original failure reproduced with no old build needed (the statement `ReadDomains` runs,
against the column the file lacks); the readings after `init: OK` are the fixed path.

## 6. Evidence

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Data suite stays green | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet` | `Failed: 0, Passed: 1850, Skipped: 0, Total: 1850, Duration: 11 m 4 s` | this report |
| Domain read path focused | `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~Domains"` | `Failed: 0, Passed: 32, Skipped: 0, Total: 32` | this report |
| CI guard tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | `GUARDS OK - 21 guard(s) run, 0 red` | this report |
| Real file upgraded | `pwsh -NoProfile -File tasks/reports/f13-schema-upgrade-proof.ps1 -SourceDb "…/dist/FusionRpg.Server/data/rpg-hot.sqlite"` | `15 → 16` columns, `first_clear_ref present=True`, `ReadDomains -> 0 rows`, `PROOF OK` | `tasks/reports/f13-schema-upgrade-proof.ps1` |
| Complete missing-column list derived | fresh-store dump vs real-file dump + 110 parsed `EnsureColumn` sites | exactly one genuine: `dungeon_domain.first_clear_ref` | §2–§3 |

## 7. NOT proved (explicit)

- **No committed xunit regression test.** The brief's preferred proof is a test in
  `gk-core/tests/FusionRpg.Data.Tests/Delve/Domains/` using `DataTestStore.CreateWithPreInitHot` (the repo's
  established "a save written by an older build" seam), but this lane's runner fence is
  `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`, `tasks/party-dungeon-todo.md`,
  `tasks/party-dungeon-ledger.jsonl`, `tasks/sessions/party-dungeon-f13.json`, `tasks/reports/**` —
  `tests/**` is outside it and a changed file there fails the run. The executable proof above is the
  strongest in-fence form; **finding for the manager: widen the fence by
  `gk-core/tests/FusionRpg.Data.Tests/Delve/Domains/**` and the test lands in one commit.**
- **The owning program's todo was not written.** The fence allows only `tasks/party-dungeon-todo.md`, so
  the `pvz_activity_facts.player_id` routing could not be appended to
  `tasks/creature-progression-todo.md` / `tasks/species-build-todo.md`. It is a no-op repair anyway (§4);
  recorded here and in the F13 row instead.
- **The pooled live re-proof** (`scripts/prove-slot-connection.ps1`, `DATA PATH HEALTHY True`) is the
  manager's acceptance, not this lane's: it needs a slot game launch. Not run here.
- **`GetRpgActor`/`GetRpgProgressionSummary` on real player data**: exercised only through the probe's
  player 1 (`level 3`, `player 1`). Their real-data correctness is unchanged by this fix.

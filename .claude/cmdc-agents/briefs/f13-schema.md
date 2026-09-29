# Lane `f13-schema` — a head build against a REAL database 500s: register the columns `EnsureColumn` never got

**Session:** `party-dungeon-f13` · **Program:** `party-dungeon` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`, `tasks/party-dungeon-todo.md`, `tasks/reports/**`

## The defect — already measured at the integration head, do not re-derive it

Row **F13** in `tasks/party-dungeon-todo.md` carries the full reading. In short: a freshly built server, pointed
at the owner's real `rpg-hot.sqlite` (546 MB / 185 tables, copied by SQLite *online backup* so the copy is
exact), accepted 5 client connections and 10 requests from a real game and failed **all ten**:

```
SQLite Error 1: 'no such column: player_id'          ×8
SQLite Error 1: 'no such column: first_clear_ref'    ×2
```

raised at `RpgStore.GetRpgActor` (`RpgStore.Progression.cs:435`), `ReadActorDtoUnlocked` (`:850`),
`GetRpgProgressionSummary` (`:352`) and `ReadDomains` (`RpgStore.Domains.cs:328`).

`first_clear_ref` sits in head code's own `CREATE TABLE IF NOT EXISTS dungeon_domain`
(`RpgStore.Domains.cs:57–65`) — but `CREATE TABLE IF NOT EXISTS` cannot add a column to a table that already
exists, and neither column is registered with `EnsureColumn` (`RpgStore.cs:4304`, `ALTER TABLE … ADD COLUMN`),
which is the mechanism this repo already uses for exactly this case (`RpgStore.Actions.cs:107–118` registers
eleven `rpg_action` columns that way). Direct check of the real database: `dungeon_domain` has 15 columns and
no `first_clear_ref`, and that column is absent from **every** table in the file.

## Why it matters

The pooled live path can *connect* but cannot be *used*: the server answers `/health` and then 500s on the
game's own data calls. The same failure reaches the owner's own install on its next server restart. It is also
the live half of CC8 — a live probe that cannot read gameplay state back proves nothing.

## Deliverable

1. **The complete list of columns head code reads that an existing database lacks.** Derive it, do not guess:
   compare the schema the code's DDL plus its `EnsureColumn` calls establish against a real database
   (`dist/FusionRpg.Server/data/rpg-hot.sqlite` is a real one). State the method and the reading.
2. **The fix**: register each missing column with `EnsureColumn` at its owning table, following the established
   one-line-per-column pattern. Additive only — no `ALTER` that rewrites or drops, no change to existing rows.
3. **A regression proof that a REAL, pre-existing database is upgraded.** The strongest form is a test that
   opens a database built from the old schema and asserts the columns exist after init. Do not weaken or delete
   an existing test to pass.
4. **`pvz_activity_facts.player_id` is NOT yours to fix** — it belongs to the activity-facts surface
   (`docs/architecture/pvz-activity.md`). Route it: name the owning program and the row, and file it there.

## Verification

- `dotnet test gk-core/tests/FusionRpg.Data.Tests --nologo --verbosity quiet`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

## Evidence contract (what your report must contain)

- exact command text and the numbers printed, for: the Data suite, and the focused filter that reproduces the
  original failure
- the committed artifact (SHA) and the files in it
- an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present** (a reused id has
  silently appended nothing while the commit message claimed it had)

## Boundaries

- The pooled re-proof (a game launched from a slot, the injector naming its URL, `DATA PATH HEALTHY True`) is
  the **manager's**, not yours — your acceptance is the upgrade path proven at test level.
- Your session record's `worktree` path must be **ABSOLUTE**; a relative one makes `verify-change.ps1` exit 1 on
  DRIFT in your own record (measured on lane `isg-gen-fix`).
- `gk-core/data/tuning/**` and generated trees are never hand-edited; if a tuning input is involved, publish `v{n+1}`.

# SE4.30 / CC2 — real-save migration + rollback rehearsal (live-qa probe)

Run against `cmdc/lane-b`'s `SaveIdentity` code (commit `a6fdcca7`, not yet in
`features/mega-merge` as of this probe) via a separate, short-path detached-HEAD `git worktree`
(`D:/wt-cc2-laneb`, removed after the probe) built with `dotnet publish`. This file records evidence
this session (`live-qa-20260920`, worktree `worktree-agent-a133b88741cadeb4f`) owns; it is deliberately
**not** written into `tasks/solid-enforcement-todo.md` — that file is mid-edit on `cmdc/lane-b`'s own
branch (SE4.15-SE4.29 are ticked there but not in this tree), and editing this session's stale copy of
it risks corrupting or conflicting with their own pending merge. Whoever merges the SE4.15-SE4.30 unit
should copy this evidence into SE4.30's own line and Checkpoint 4b.

**Claim:** the migration runs on a real save (never the original), the human commander's numbers are
byte-identical before and after, the backup exists, a second boot is a no-op, and a rollback to the
pre-migration binary reads the same numbers again.

## Real save used

`dist\FusionRpg.Server\data\rpg-hot.sqlite` — this session's own live server (port 5088, started
earlier for the B27/BP4 probes), player 1 = `Crazy Dave`, a real progression state built up through
ordinary play across this session (level 17, a levelled Peashooter and NormalZombie). The original file
was copied, never opened directly by the migration build.

## Steps and evidence

1. **Pre-migration reading**, real server, real REST route:
   - `GET /api/players/current` → `{"id":1,"name":"Crazy Dave","createdUtc":"2026-09-20T06:38:19.77...Z","worldSeed":1585626293663144424}`
   - `GET /api/rpg/progression/1/summary` → `player.level:17 xp:288 xpToNext:820 highestLevel:17 demotionCount:2 revision:682`; `topPlants[0]: level:9 xp:152`; `topZombies[0]: level:19 xp:450`.
2. **Copy, never the original**: `rpg-hot.sqlite`(+`-wal`/`-shm`) and `rpg-media.sqlite`(+`-wal`/`-shm`)
   copied to `dist\FusionRpg.Server-migration-test\data\` (removed after the probe).
3. **Booted the copy on a spare port** (`FUSIONRPG_DATA=...migration-test\data`,
   `FUSIONRPG_URLS=http://127.0.0.1:5099`, `Start-Process` — this session's own server on `:5088` was
   never touched or restarted). `SaveIdentity.Migrate` ran on `Init` (`RpgStore.cs:157`) and printed
   its report to stdout, captured verbatim:
   ```
   [save-identity] migrated save identities; report: {"backupPath":"...\\rpg-hot.sqlite.pre-save-identity.20260920T080510074Z.bak","migratedUtc":"2026-09-20T08:05:10.288...Z","legacyZombossFound":false,"legacyZombossId":null,"legacyZombossIsSave":false,"legacyDecision":"no row named Zomboss","savesSeeded":[1],"tierA":[{"table":"rpg_actor_progression","copied":4,"leftBehind":0},{"table":"rpg_xp_ledger","copied":2225,"leftBehind":0}],"specimensStampedBySave":0,"zombossSpecimensKeptOnSave":0,"rehomedByProvenance":0,"rehomedByOnlySave":0,"unattributedSpecimenIds":[],"legacyArchivedUtc":null}
   ```
4. **Backup confirmed present**: `Test-Path ...\data\rpg-hot.sqlite.pre-save-identity.20260920T080510074Z.bak` → real file on disk (`ls` confirmed, 37,949,440 bytes).
5. **Post-migration reading, same real REST routes, spare port `:5099`**:
   - `GET /api/players/current` → **byte-identical** to step 1 (`id`, `name`, `createdUtc`, `worldSeed` all equal).
   - `GET /api/rpg/progression/1/summary` → **byte-identical** to step 1 (`level:17 xp:288 xpToNext:820 highestLevel:17 demotionCount:2 revision:682`, same `updatedAt`; `topPlants[0]` and `topZombies[0]` byte-identical too).
6. **No-op on a second boot**: stopped the process, `Start-Process`'d the SAME exe against the SAME
   copy again. The `[save-identity] migrated...` line is **absent entirely** from the second run's
   stdout (the marker gate, `SaveIdentity.HasMarker`, short-circuited it). Confirmed exactly **one**
   `.bak` file exists in the data dir after the second boot — no second backup was written.
7. **Rollback rehearsal**: stopped the server, deleted the copy's `rpg-hot.sqlite`(+`-wal`/`-shm`),
   restored the `.bak` as `rpg-hot.sqlite`, booted the **pre-migration binary** (this session's own
   `dist\FusionRpg.Server\FusionRpg.Server.exe`, built before `SaveIdentity` existed) against the
   restored copy on the same spare port. It started cleanly (`health: {"ok":true,...}`) and
   `GET /api/players/current` / `GET /api/rpg/progression/1/summary` read the **same pre-migration
   numbers** as step 1, again byte-identical.
8. **Cleanup**: stopped all migration-test server processes, deleted
   `dist\FusionRpg.Server-migration-test\`, removed the `D:/wt-cc2-laneb` worktree and its publish
   output. This session's own real server (`:5088`) was healthy and untouched throughout
   (`injectorConnected:true` reconfirmed after cleanup).

## Verdict: PASS

A real save migrates; the human player's numbers are byte-identical before and after; the backup
exists and is never reused on a second boot (confirmed absent second write); a rollback to the
pre-migration binary reads the same pre-migration numbers cleanly. Every read in every step went
through the normal REST path (`/api/players/current`, `/api/rpg/progression/{id}/summary`), never the
migration's own return value or a hand-inspected row.

**No defect found** — unlike `BP4`/`B27` (this same session's other two probes), SE4.30's migration
mechanism behaved exactly as specced on the first live attempt.

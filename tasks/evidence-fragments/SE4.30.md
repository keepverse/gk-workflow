# SE4.30 — migration rehearsal on a copy of a real save

**Verdict: CLOSED by owner ruling** (`8aba2900f`), ticked 2026-09-22 by `cmdc/se4-1` (routed as
RECON-F1). The probe itself ran and passed in `live-qa`; the two clauses the ruling accepts as
recorded-but-not-green are named per row below.

| Criterion | Command / artifact | Result |
|---|---|---|
| Copy of the real save, never the original | `live-qa`: `dist/FusionRpg.Server/data/rpg-hot.sqlite` (+`-wal`/`-shm`) copied to a scratch data dir; source sha256 re-checked after | original unchanged — `CC2.md` |
| Migration run by the real server build, spare port | `Start-Process dist/FusionRpg.Server/FusionRpg.Server.exe`, `FUSIONRPG_DATA=<copy>`, `FUSIONRPG_URLS=http://127.0.0.1:5099` | report quoted: `savesSeeded:[1]`, `rpg_actor_progression copied:4`, `rpg_xp_ledger copied:2225`, `leftBehind:0` — `cc2/run1-report.txt` |
| `.bak` present | `ls <copy>/data` | `rpg-hot.sqlite.pre-save-identity.20260920T154427812Z.bak`, 37,961,728 bytes — `cc2/run1-bak-name.txt` |
| Human numbers equal, through normal REST | `GET :5099/api/players/current`, `GET :5099/api/rpg/progression/1/summary` | byte-identical to the pre-boot reads: `Crazy Dave` / `worldSeed:1585626293663144424`; `level:17 xp:288 revision:682`, plant 9/152, zombie 19/450 |
| Second boot is a no-op | stop, boot the same copy again | `grep -c save-identity run2.log` → **0**; `.bak` count → **1** |
| Rollback rehearsal | in-worktree: not runnable (no pre-`SaveIdentity` binary exists there) | rehearsed by the earlier live lane instead — `CC2-SE4.30-live-probe.md` step 7: `.bak` restored over the copy (`-wal`/`-shm` deleted), previous build booted clean, same pre-migration numbers |
| Full suite once | `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault` (`live-qa`) | Data 1698/1698, Server 726/726 pass; Core 14833/14837 (4 fail); E2E 1 fail — **red**, on four pre-existing facts the ruling routes to `test-verification-boundary` as a knownRed registration |
| Row id survives the tick | `grep -c "SE4.30" tasks/solid-enforcement-todo.md` | present (row + closure note) |

Reference: probe detail `tasks/evidence-fragments/CC2-SE4.30-live-probe.md` and `CC2.md`; ruling
`8aba2900f`; parent row `tasks/summoner-convergence-todo.md:74-79`.

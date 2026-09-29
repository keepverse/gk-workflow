# CC2 — Identity foundation — SE4.30 real-save migration probe (live-qa)

Verdict: **migration probe PASS; SE4.30 not closed** — the full-suite acceptance line is red on an
E2E regression this probe did not cause (see below), and the rollback rehearsal was not re-run.

| Criterion | Command | Executed result |
|---|---|---|
| Copy the save, never the original | copied the pre-migration snapshot `agent-a133b88741cadeb4f/.../rpg-hot.sqlite.pre-save-identity.20260920T084148390Z.bak` (sha256 669b0190…) into `dist/FusionRpg.Server-migration-test/data/rpg-hot.sqlite` | source sha256 re-checked after: **unchanged**; original mtime still 15:41:48 |
| Run the migration (real server, spare port) | `Start-Process dist/FusionRpg.Server/FusionRpg.Server.exe` with `FUSIONRPG_DATA=<copy>`, `FUSIONRPG_URLS=http://127.0.0.1:5099` | `[save-identity] migrated save identities; report: {"savesSeeded":[1],"tierA":[{"table":"rpg_actor_progression","copied":4,"leftBehind":0},{"table":"rpg_xp_ledger","copied":2225,"leftBehind":0}],…}` → `tasks/evidence-fragments/cc2/run1-report.txt` |
| Timestamped backup kept | `ls <copy>/data` | `rpg-hot.sqlite.pre-save-identity.20260920T154427812Z.bak` (37,961,728 bytes) — `cc2/run1-bak-name.txt` |
| Read back through the normal path | `GET :5099/api/players/current`, `GET :5099/api/rpg/progression/1/summary` | `{"id":1,"name":"Crazy Dave","createdUtc":"…06:38:19.7799077Z","worldSeed":1585626293663144424}`; player `level:17 xp:288 xpToNext:820 highestLevel:17 demotionCount:2 revision:682`; plant 9/152, zombie 19/450 — **equal to the pre-migration rows** in the source `.bak` |
| Migrated shape, history kept | PRAGMA + sqlite_master on the copy | new cols `save_id,empire_id`; rows `(1,'dave',{plant,player,species,zombie})`; `rpg_actor_progression__pre_save_identity` + `rpg_xp_ledger__pre_save_identity` kept; marker 1 |
| Second boot is a no-op | stop :5099, boot the SAME copy again | `grep -c save-identity run2.log` → **0**; `.bak` count → **1** (`cc2/run2.txt`) |
| The live save itself | consistent `sqlite3` backup of `dist/FusionRpg.Server/data/rpg-hot.sqlite` → boot on :5099 | marker 1, `save-identity` lines **0**, `.bak` count **0**; `GET :5099` player `level:9 xp:42 revision:188` == the copied file row and `GET :5088` (`cc2/live-copy-*.json`, `cc2/live-5088-*.json`) |
| Full suite once (SE4.30 clause) | `pwsh -NoProfile -File scripts/test-fast.ps1 -AllDefault`, then `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "Category!=DiskSemantics&Category!=Heavy"` | Data **1698/1698 pass**, Server **726/726 pass**, Core **14833/14837 pass** (4 fail, below), E2E **1 FAIL** (`ExpeditionE2ETests.Full_loop_dispatch_force_due_collect`) — the suite is **RED** — `cc2/full-suite.txt`, `cc2/core-tests.txt` |
| Rollback rehearsal (SE4.30 clause) | not re-run | needs a pre-SaveIdentity binary; no such build exists in this worktree. Previous live lane rehearsed it: `tasks/evidence-fragments/CC2-SE4.30-live-probe.md` step 7 |
| Cleanup | stop :5099, remove both scratch trees, re-check :5088 | :5099 clear, scratch gone, :5088 health 200, original `.bak` untouched |

**Regression found by the suite (handed over, not fixed here — `tests/**` is outside this lane's
paths):** `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs:90` asserts the battle tick drops
`shard.chaff`, but `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:101` now mints
`CreatureYieldTuningHub.ShardFor(PlannedRungFor(setup.Wave))` — the species-gear-chain T31 commit
`3cf2a9d34` retired the `isBoss` ternary and keys the shard on the wave's species rung, whose value for
this summon is `fused` → the request returned `[{"materialId":"shard.fused","qty":1}]`. Reproduced
deterministically: `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ExpeditionE2ETests.Full_loop_dispatch_force_due_collect"` → `Failed: 1, Passed: 0`. Row filed in
`tasks/species-gear-chain-todo.md`; T31 did not update this E2E test.

**Four more Core failures, all stale-pin/generated-drift handed over the same way (none caused by this
lane — it changed only `gk-fusion/tools/debug-mcp/**` and `tasks/**`):**
`SocketOperationsTests.cs:329` and `UniqueCorpusTests.cs:520` pin corpus values the item-seed pass
changed (`39fbed34`, `12175b3d`) — rows in `tasks/item-todo.md`.
`FamilyExpansionTests.cs:190` is red because `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check`
exits 1 naming `gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-evade.json` stale — row in
`tasks/atom-family-expansion-todo.md`. `SocketOperationsTests.The_legacy_socket_word_corpus_is_ordered…`
is the already-documented SSH2.6-retirement defect (`tasks/backlog-clean-up-todo.md:712`), not re-filed.

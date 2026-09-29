# AE2.4 live probe — the lawn hit follows the action base and `Θ` (2026-09-19)

Taken by the orchestrator on the real game (MelonLoader host, `pvzrh-3.9`) against `features/mega-merge`
at `5df61d81` (code identical to the lane branch HEAD at the time), per
`docs/contributing/live-probe-standard.md`.

## Preconditions

- Full default suite green first (`test-fast.ps1 -AllDefault`, run in a clean checkout of the branch):
  Data 1547/1547, Server 551/551, E2E 226/226, Core 14207/14208. The one Core failure is
  `DungeonLootTableSeedFileTests` (a worktree-only CRLF artifact); the same test passes 4/4 in the main
  checkout.
- Deploy: `deploy-play.ps1 -NoServer -NoRebuildUi` (injector + server publish), server started with
  `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`.

## Scopes

| Reading | Scope | Path |
|---|---|---|
| Commander `Θ` | RPG Server, normal query path | `GET /api/rpg/progression/1/summary` (`player.level`) and `GET /api/aptitudes/1` (`theta`), the same values the injector hydrates from |
| Raising `Θ` | RPG Server, real progression | real lawn kills: `zombie.die` → `POST /api/events` → `ZombieKilled` → `TryApplyXpUnlocked`. No fact-append or seed endpoint was used |
| Hit amount | Game Injector | `debug.combat.overlay.baseOverlayDamage` (the grant's amount before defense), read from the event store |
| Board fixtures | Game Injector Debug | `lawn/quick-start`, `spawn-zombie`/`spawn-plant`. They only skip tedium: the grants are bound by the real `LawnBasicAttackGrantBinder` at spawn, and kills flow through the real ingest |

Expected value: `BasePerHit(140, P(Θ)) = floor(140 × P(Θ) / 1000)` with
`P_milli(Θ) = 80000 + 26200·Θ + 200·Θ·(Θ−1)` (`power-scale.v2.json`; `action-base.v2.json`
`basicAttack.basePowerMilli = 140`).

| Θ | P(Θ) | expected base |
|---|---|---|
| 1 | 106 | 14 |
| 69 | 2826 | 395 |
| 70 | 2880 | 403 |
| 71 | 2934 | 410 |

## Results

1. **Θ = 69** (server: level 69, theta 69). Every overlay hit on the board, in both directions, has
   `baseOverlayDamage = 395`, e.g. events 887092–887339 (zombie `2DFF7736320` ↔ plant `2DFF7849480`).
2. **Real progression to Θ = 70** (real kills), then a game restart (session start rehydrates `Θ`):
   every hit on the fresh board is **403**, e.g. events 894961–895096 (zombie `1FB79984320` → plant
   `1FB7995A240`).
3. **Real progression to Θ = 71** (about 170 real kills; server theta 71). The injector has no push for
   a level-up (no path sends `power.index.reload` after a progression change; this is the open
   `tasks/live-probe-todo.md` Task 25), so it still held 70. Lab zombie `1FB7C2CE640` spawned at
   02:37:10 and was bound at the stale Θ 70. The server was restarted at 02:37:15 and the injector
   reconnected at 02:37:17 (the spec's SignalR-reconnect trigger). The same zombie's first and every
   later bite is **410** (events 925704–926182): the rebind re-baked a live grant, with no respawn.
4. **Same actor, direct before/after.** Still on `1FB7C2CE640`, never respawned: bites at **410** through
   02:38:17.6 (event 926182). The current player was switched to player 2 (level 1, theta 1; the spec's
   player-identity trigger, a real operation) and the server restarted (reconnect 02:38:19). The next
   bites from the same zombie are **14** (events 926382–926415+). Player 1 was restored afterwards
   (current player 1, theta 71).

## Verdict

The lawn hit's base is `BasePerHit(base, P(Θ))` at four `Θ` values measured live (1, 69, 70, 71). A
live grant follows a `Θ` change without a respawn when a listed refresh trigger fires (reconnect,
identity).

## Findings (named, not fixed here)

- **No push of `Θ` after a real level-up.** Until a reconnect, session start or `power.index.reload`,
  the injector keeps the old `Θ` (Task 25 in `tasks/live-probe-todo.md`). Every real level-up mid-match
  is therefore invisible to the lawn until the next trigger.
- **`GET /api/debug/events?afterId=` stops paging.** Past id 895096 it returned nothing although the
  store held rows up to 926k. One row in that range carries `game = pvzrh-3.8.1`, which is a plausible
  cause. Evidence here was read from `rpg-hot.sqlite` directly (read-only).
- **`lawn/quick-start` over a defeated board.** After a defeat it reported `InMatch` and spawned
  fixtures onto the main-menu scene, and `enter-level` refused while the stale `Board` existed. It was
  recovered only by restarting the game.
- **Peashooter bullet hits are vanilla-only.** They are attributed to the bullet, so the overlay path
  (and this probe's telemetry) sees only melee and other direct attacks. That is consistent with the
  lawn-combat-wire design, but it limits which hits can evidence the grant.

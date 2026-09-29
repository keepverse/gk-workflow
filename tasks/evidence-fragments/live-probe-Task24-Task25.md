# live-probe Task 24 + Task 25 — the injector never learns about a player switch or a level-up

**Claim:** `CheatState.CurrentPlayerId`/`CheatState.PowerIndex` (the injector's single global cache of
"who is playing" and "what is their Theta") only ever refreshed at session start, on reconnect, or on
an explicit `power.index.reload` command — and nothing in production ever sent that command on a
player switch (Task 24) or a level-up (Task 25). Fixed by sending it from the two real places those
events actually happen: `PUT /api/players/current` (`Program.cs`) and `EventIngest.
BroadcastProgressionAsync`'s existing player-progression fan-out (`EventIngest.cs`), scoped to
`RpgActorKinds.Player` specifically so a species/zombie/plant level-up (which already has its own,
correctly-scoped "species" `AptitudesUpdated` signal) does not also fire this.

## Root cause confirmed before fixing (file:line)

- `gk-core/src/FusionRpg.Server/UniqueActorService.cs` / `AptitudeEndpoints.cs`: the injector's
  `"AptitudesUpdated"` handler (`RpgClient.cs:108-124`) only ever enqueues
  `aptitudes.allocation.reload`, which refreshes commander/unique/species allocation caches — never
  `CheatState.CurrentPlayerId` or Theta.
- `grep -rn "power.index.reload" gk-core/src/FusionRpg.Server` returned **zero** production senders before
  this fix — the command existed only as a name `CheatCommandRunner.cs:101-105` recognized if it ever
  arrived.

## Fix

- `gk-core/src/FusionRpg.Server/Program.cs`, `PUT /api/players/current`: after the existing "save"-scope
  `AptitudesUpdated` broadcast, sends a real `power.index.reload` command via the same
  `InjectorCommandSender`/`InjectorCommandInbox` path every other production command uses.
- `gk-core/src/FusionRpg.Server/EventIngest.cs`, `BroadcastProgressionAsync`: when a dirty progression row's
  `Kind == RpgActorKinds.Player`, sends the same command. `BroadcastProgressionAsync` made `internal`
  for its own regression test (no test exercised this dispatch method at all before this fix).

## Regression tests (new, both green)

| Test | What it proves |
|---|---|
| `gk-core/tests/FusionRpg.E2E.Tests/PlayerSwitchPowerIndexReloadTests.cs` (real `WebApplicationFactory<Program>`, real SignalR) | `PUT /api/players/current` sends `power.index.reload` to a client joined as `injector` |
| `gk-core/tests/FusionRpg.Server.Tests/ProgressionPowerIndexReloadTests.cs` (2 cases) | A `Player`-kind dirty row sends it; a `Species`-kind dirty row does **not** (regression against over-broadening) — both still fire their pre-existing broadcasts unchanged |

`dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter PlayerSwitchPowerIndexReloadTests` → 1/1.
`dotnet test gk-core/tests/FusionRpg.Server.Tests --filter ProgressionPowerIndexReloadTests` → 2/2.
Full `dotnet test gk-core/tests/FusionRpg.Server.Tests` → 707/708 (1 failure, `ItemPreviewEndpointsTests`,
confirmed a pre-existing Kestrel port-collision flake under parallel execution — passes 11/11 in
isolation, unrelated to this change).

## Live proof (real game, real server, redeployed with this fix)

Both reproduced live via `debug.aptitude-trace` (`side`, `currentPlayerId`, `theta`), the exact
telemetry the original findings used — no hand-made row, no fabricated state.

### Task 24 — player switch

| Step | `currentPlayerId` (real telemetry) | `theta` |
|---|---|---|
| Fresh connect, before any switch | 0 (uninitialized) | 0 |
| `PUT /api/players/current {"id":1}` (no-op switch, exercises the fix) | **1** | **17** (matches player 1's real level 17) |
| Created player 2, `PUT /api/players/current {"id":2}` | **2** | **1** (matches player 2's real level 1) |
| Switched back `{"id":1}` | **1** | **17** |

### Task 25 — level-up, no switch involved

Fresh board bound to player 2 (`board.start` `playerId:2 runId:8`), current player left at 2
throughout — isolates the level-up path from the switch path.

| Step | Real progression (`GET /api/rpg/progression/2/summary`) | `debug.aptitude-trace theta` |
|---|---|---|
| Before combat | level 1, xp 0/100 | **1** |
| `POST /api/debug/stress-fill` (9 plants, 20 zombies, real combat) | level **2**, xp 68/145 (`highestLevel:2`) | still 1 on the LAST trace **during** the kill burst (event ordering: the level-up write landed after that burst) |
| One more real kill after the level-up committed | — | **2** (matches the new level) |

Δtheta = +1, exactly tracking the real level change, with zero manual cache refresh in between.

## Unrelated, found and fixed first

Redeploying to run this live proof required the seed-registry Content-Include fix from the earlier
`live-qa` commit (`fix(injector): deploy commanders + dungeon seed registries with every host
build`) — without it the injector cannot connect to any fresh install at all. Also hit two more
instances of this same MelonLoader host's known transient crash-on-restart (`0xc0000005` in
`coreclr.dll`, matching the failure table's "silent death after host ready" entry) — both resolved by
a clean kill + single relaunch, not a code issue.

## Verdict: PASS, both tasks

Prior art this closes: `docs/architecture/lawn-playable-map.md`'s `actor-liveness-refresh` module
(unbuilt — no `lawn-playable-todo.md` exists yet) plans a more general "one typed invalidation channel,
one per-actor revision" redesign that will likely supersede this fix's narrow `power.index.reload`
send. This fix is intentionally the smallest correct patch for the two reported symptoms now, not a
substitute for that redesign — noted here so whoever builds `actor-liveness-refresh` knows the exact
symptom is already covered and does not need to re-discover it, while the general caching mechanism is
still real, separate work.

# actor-hud — Unity HUD live evidence (AUDIT-4), slot-1 lane, 2026-09-26

**Status: AUDIT-4 is now PARTIALLY closed, and the part that is closed is the half that was owed.**
The Unity→Server HUD ingest is proven on a real lawn with real entities. The HUD's
render-to-screen half is **not** proven, and I did not prove it — not because it failed, but because
the only pixel instrument available in a non-interactive session is *structurally incapable* of
seeing the thing under test (F5). Two findings below are more useful than a green.

This lane produced **evidence only**. It changed no production file (`git diff a49fa229c -- src web
data scripts tools` is empty; the only dirty files in the tree are two `.commandcode/taste/*` files
belonging to another stream, untouched). It did not merge.

---

## 1. Slot, ports, install

| | |
|---|---|
| Pool slot | **1**, claimed with `scripts/live-slot.ps1 -Acquire -Session actor-hud-unity-live-20260926`, **released** at the end (`ready-to-claim now: 3`) |
| Install | `H:\Games\.fusionrpg-pool\slot-1` (slot-owned clone; the owner's default install was never written to) |
| Server port | **`http://127.0.0.1:5190`** — see SPOT-1 in §8; this is a **deviation** from the slot's registry port |
| Server data dir | `H:\Games\.fusionrpg-pool\slot-1-data` (its own; the owner's `dist/.../data` was never written to) |
| Server publish tree | `C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-unity-live-server-20260926` (own tree, see F3) |
| Game process | pid 53536, `PlantsVsZombiesRH.exe` from slot-1, `FUSIONRPG_SERVER_URL=http://127.0.0.1:5190` |
| Server process | pid 55020, stopped by this lane |
| **Never touched** | `:5088` (owner's default, free this whole run), **`:5111`** (owner's server, pid 56816 — still running at end), the owner's install `H:\Games\PVZ-Fusion-3.9_MelonLoader`, slots 2 and 3, and pid 78664 (see SPOT-1) |

---

## 2. Commands and their real output

### 2.1 Slot acquisition, and a blind spot in it

```
$ .\scripts\live-slot.ps1 -Acquire -Session actor-hud-unity-live-20260926
[live-slot] ACQUIRED slot 1 for actor-hud-unity-live-20260926 at H:\Games\.fusionrpg-pool\slot-1
[live-slot] YOUR SERVER PORT: 5101
```

**SPOT-1 — the pool cannot see a server squatting on a slot's port.** `-Status` reported slot 1
`ready`, `session -`, `process none`, and `free 3`, at 11:49:47. At the same moment:

```
port 5088 free
port 5101 LISTEN pid=78664 name=FusionRpg.Server
       cmd="...\.kilo\worktrees\actor-hud-bottom-anchor-20260916\dist\FusionRpg.Server\FusionRpg.Server.exe"
       started 2026-09-25 22:24:25
5101 health: {"ok":true,...,"catalogRevision":1,...}
```

A leftover server from the **merged** browser-proof lane's worktree held slot 1's own registry port.
The registry's `process` field tracks the slot's *game*, not its *server*, so `-Status` cannot see
this. Two consequences I hit for real, not predicted: `lane-server.ps1 -Start -Slot 1` resolves the
port from the registry first (`SlotPort`, `lane-server.ps1:51-57`) so it would have tried to bind
5101 and failed; and `deploy-play.py` refuses to publish when `--server-url` already answers
(`deploy-play.py:470-472`, *"it locks its own DLLs"*).

I did **not** kill pid 78664 (not this lane's process) and did **not** reclaim the slot. I ran my
own server on **5190**, verified free beforehand, outside the pool's 5101–5103 block so no other
slot's port is taken, and outside the launcher's 5089–5188 scan range so the owner's launcher cannot
adopt it. **This is a deviation from `lane-server.ps1` and is stated as such.**

### 2.2 Deploy — two tool-level blockers before the game could be touched

`npm` is not resolvable by `subprocess` on this machine:

```
$ python -c "import subprocess; subprocess.run(['npm','--version'])"
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**F1 — `deploy-play.py`'s FE-build stage cannot run here.** `run()` calls
`subprocess.Popen(["npm","run","build"], shell=False)` (`deploy-play.py:155-159`); `CreateProcess`
with no shell resolves `npm.exe` only, and nvm4w ships `npm.cmd` + `npm.ps1` and **no** `npm.exe`
(`C:\nvm4w\nodejs`). The deploy dies `exit 1` at stage 3 of 12:

```
==> web UI build
  $ npm run build
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

Reproduced standalone, so it is not a deploy-state artifact. **Every pooled deploy on this machine
fails here.** Worked around with the tool's own documented flag: I ran `npm run build` myself
(`✓ built in 12.69s`, output to `src/FusionRpg.Server/wwwroot/`) and deployed with `--no-rebuild-ui`.

Second run, `--no-rebuild-ui`, got through the injector and then died at the server publish:

```
==> injector build (MelonLoader / pvzrh-3.9) -> H:\Games\.fusionrpg-pool\slot-1\Mods
    25 Warning(s)  0 Error(s)   Time Elapsed 00:00:04.92
==> freshness (a 'Build succeeded' is not evidence the DLL was rebuilt)
  Freshness OK — deployed injector artifacts match their source trees
==> server publish
  error MSB3027: Could not copy "...\FusionRpg.Core.dll" to
    "...\dist\FusionRpg.Server\FusionRpg.Core.dll". Exceeded retry count of 10.
    The file is locked by: "FusionRpg Server (56816)"
REFUSED [server_publish] `dotnet` exited 1
```

**F3 — a pooled lane has no supported path to a fresh server while the owner's server is up.**
`dist/FusionRpg.Server/*.dll` are held by the owner's server (pid 56816, on `:5111`). The tool's only
remedies are `--restart-server` (owner-only) and `--reuse-build`; and the seed import would write
into the owner's live `dist/.../data`, which `session-boundary.md` §7 forbids. Worked around by
publishing to my own tree and seeding my own data dir. `--json` verdict: `"ok": false`.

### 2.3 Injector compile verdict — **OK, not SKIPPED**

```
$ $env:FUSIONRPG_ML_GAMEDIR='H:\Games\.fusionrpg-pool\slot-1'
$ pwsh -File scripts\guard-injector-compile.ps1
INJECTOR COMPILE GUARD OK — MelonLoader host (cell pvzrh-3.9) compiled to
  C:\Users\NENESC~1\AppData\Local\Temp\fusionrpg-injector-compile\
exit=0
```

Compiled against **my slot's** install, via the guard's explicit `-p:MlGameDir=$gameDir`. The
brief's SKIPPED failure mode did not occur, so the environment is wired. `deploy-play.py`'s own
injector stage independently agrees (`0 Error(s)`, `Freshness OK`).

### 2.4 The slot's cfg was still pointed at the owner's `:5088`

`deploy-play.py` writes the cfg **always**, before the server starts — and the comment at
`deploy-play.py:496-498` says it was moved out of the `-NoGame` branch precisely so a pooled deploy
cannot leave the slot on the owner's server (the SSH4.9 class). But that write sits **after** the
publish stage, so the F3 refusal skipped it:

```
$ type H:\Games\.fusionrpg-pool\slot-1\Mods\fusionrpg.cfg
# FusionRpg MelonLoader host config (written by deploy-play.ps1)
ServerUrl=http://127.0.0.1:5088      <-- the owner's default
```

**F4 — the cfg stage is unreachable behind an earlier refusal, which is exactly the state it exists
to prevent.** I wrote it to 5190 by hand (same three lines, only `ServerUrl` differing) and also
passed `FUSIONRPG_SERVER_URL` at launch, so the binding is unambiguous.

### 2.5 Server, cold import, health

```
$ dotnet run --project gk-forge/tools/AtomImporter -c Release -- --db H:\Games\.fusionrpg-pool\slot-1-data
33 file(s): 419 atom(s), 23 container(s), 0 curve(s), 10 rarity band(s), 6 element(s),
  2 channel policy row(s), 10 affix(es)
503 row(s) changed; catalog revision now 1
import exit=0
```

Into a **genuinely empty** directory (0 entries beforehand). This is the `LeadNamesHub.Configure(...)`
fix from `47c9d1f60` verified on a real cold path: **exit 0, 503 rows, catalog revision 1** — the
brief's numbers exactly. The bug did not reproduce.

```
$ FUSIONRPG_URLS=http://127.0.0.1:5190  FUSIONRPG_DATA=H:\Games\.fusionrpg-pool\slot-1-data
$ Start-Process ...\FusionRpg.Server.exe
started pid=55020
HEALTH: {"ok":true,"injectorConnected":false,"contentSource":"imported","catalogRevision":1,
         "contentImportError":null}
```

### 2.6 Injector connected to **my** server

```
INJECTOR CONNECTED: {"ok":true,"injectorConnected":true,"source":"injector",
  "lastHeartbeatUtc":"2026-09-26T11:56:14.4913695+07:00","simEnabled":false,
  "catalogRevision":1,"ingestQueued":0,"ingestDroppedEvents":0}
```

`source:"injector"` and `catalogRevision: 1` matching my own cold import — not the owner's
`catalogRevision: 15` on `:5111`. The two servers are demonstrably different servers.

### 2.7 Lawn

```
$ python gk-fusion/tools/debug-mcp/cli.py debug_lawn_setup --param scenario=lab-overlay --param level=1
{"ready":true,"entered":true,"levelType":"Advanture","targetPtr":"28543AE8320",
 "plantPtr":"28543D786C0","liveEntities":{"plantCount":1,"zombieCount":1,"liveState":"InMatch",
 "phaseMismatch":false},"scope":"game-injector-debug"}
```

A real Adventure 第1关 board with a real Peashooter and a real NormalZombie. All `debug.*` calls used
here are **Game Injector Debug** scope (`live-probe-standard.md` §1): they can fabricate engine-side
state and prove only that the engine reflects it.

---

## 3. What the lawn actually showed

Six captures, one valid paired lawn frame. All at
`C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-unity-live-20260926\`:

| file | when | board state verified immediately before | primitive |
|---|---|---|---|
| `lawn-01.png` | 04:57:39 | first capture, HUD **off** | `camera-fallback-no-repaint` |
| `lawn-02-hud-on.png` | 05:01:21 | `plantCount 0, zombieCount 0` — **board empty** | `camera-fallback-no-repaint` |
| **`lawn-03-hud-on-live.png`** | **05:02:00** | **`InMatch, plants=1, zombies=1, phaseMismatch=false`** | `camera-fallback-no-repaint` |
| `lawn-04-repaint-1..4.png` | 05:03 | 4 attempts to force a Repaint | all four **byte-identical** |
| `lawn-05-final-paired.png` | 05:05:29 | injector said `InMatch, plants=1, zombies=1` | frame is the **level-select map** |
| `lawn-06-paired.png` | 05:05:56 | injector said `InMatch, plants=1, zombies=1, mismatch=False` | frame is the **level-select map** |

**`lawn-03-hud-on-live.png` is the one valid frame.** Visible in it: the Adventure 第1关 lawn, sun
10099, the 7-card seed bar, 4 lawnmowers, `场上敌人数量: 1`, a Peashooter at row 2 firing a pea, a
NormalZombie beside it, `难度: 9`. **No FusionRpg actor-HUD marks are visible** — no identity tier
frame, no level-band chip, no shield bar, no element glyph above either actor.

I am **not** reporting that as "the HUD does not draw". See F5: this capture primitive cannot
contain an overlay canvas, so the absence of marks in this frame is **not evidence of absence**.

---

## 4. The control that makes the claims mean something

The 2026-09-13 `bound-loadout-hub` incident is the reason: a probe fed fabricated state into the
Injector and read it back from the same Injector's telemetry, returning `ok:true` for a feature that
was broken until a human looked at the screen. Four controls, each of which **changed a conclusion**:

**(a) The relay response is not the answer.** `POST /api/debug/shield/bar-status` returns
`{"ok":true,"queued":1}` — Game Injector Debug scope, a queue acknowledgement. The real payload
arrives later as an event. Reading only the response would have been reading nothing. All HUD
conclusions below come from `debug.shield.bar-status` **events** in `/api/debug/events`.

**(b) The setting was read back through three independent surfaces.** Flipping the HUD is a real
player operation, so it gets the full treatment:

```
GET  /api/settings      -> {"key":"lawn.worldHud","value":true,"isDefault":false}
PUT  /api/settings      -> {"ok":true,"key":"lawn.worldHud","value":true}
GET  /api/settings      -> lawn.worldHud = true, isDefault = false      (normal query path)
sqlite3 rpg_user_settings -> (1, 'lawn.worldHud', 'true', '2026-09-26T04:59:51.7752984Z')
```

The fourth surface is the *effect*: the injector acted on it (§5). A pass on the server proves
nothing about the engine; these are separate chains (`live-probe-standard.md` §1, §3.4).

**(c) The empty-board false red — which I nearly reported as a defect.** With the HUD on and the
canvas ready, telemetry read `early:"idle", hudSlots:0` twice (ids 378, 410). `early` is
`_worldHud > 0 ? "ok" : "idle"` (`ActorHudPool.cs:187`) and `_worldHud++` is the **last** statement
of the per-actor draw body, so this reads as "nothing drew". It was not a defect: `debug_game_state`
at that moment said `plantCount: 0, zombieCount: 0`. **The board was empty.** With actors present the
same probe reads `early:"ok", hudSlots:2` (ids 558, 892, 1050). This is precisely the failure shape
`live-probe-standard.md` §6 exists to stop, and it happened to me twice.

**(d) The SPA-fallback control, re-measured on my own server** (the browser lane measured it on
theirs, so it is reproduced rather than cited):

```
GET /api/catalogs/actor-surface -> 200 application/json 24968B
   hudPresentation {"identityElementPrimaryPixels":36,"identityElementSecondaryPixels":30,
                    "identityElementGapPixels":4.5}
   7 element rows, 6 with a non-null hudGlyph (omni presentationOnly, no glyph), versionStamp element:2
GET /actor-hud-elements/flame.png   -> 200 image/png 4676B
GET /actor-hud-elements/crystal.png -> 200 image/png 4342B
GET /definitely-not-a-route         -> 200 text/html 403B     <-- the fallback, on the same server
```

---

## 5. What is proven

### 5.1 The Unity→Server HUD ingest — **PROVEN** (this is what AUDIT-4 was owed)

The browser-proof lane fed the FE through `window.__fusionRpgAppendLogEvent`. Here the events came
**out of the running game**. 21 real `debug.actor-hud` events, read through the Server's own
`/api/debug/events`:

```
id=30  ptr=28543ae8640  tier=normal role=vanilla flags=      band=1 elements=null
id=78  ptr=28543d786c0  tier=unique role=vanilla flags=unique band=1 elements=null
id=87  ptr=28543ae8320  tier=normal role=vanilla flags=      band=1 elements={"primary":"earth"}
id=521 ptr=28543d8b240  tier=unique role=vanilla flags=unique band=1 elements={"primary":"earth"}
id=522 ptr=28543ec1320  tier=normal role=vanilla flags=      band=1 elements={"primary":"earth"}
... 21 total
```

Producer side: `ActorHudCache.DeltaEmit` → `DebugRuntime.Emit("debug.actor-hud", {ptr, actorHud})`
(`ActorHudInvalidator.cs:49-60`), serialized by `ActorHudWireSerializer` (`ActorHudObserve.cs:12`
for the census path). The census rows carry the same nested `actorHud` via
`ActorHudObserve.AttachRow` — ids 71, 79, 88, 89, 95, 96 on `entity.stats` / `plant.spawn` /
`zombie.spawn`.

**The subject is a real record, not something the debug call invented** (the anti-cheat check that
matters most). The same ptr appears in:

```
stat.writer  id=27  ptr=28543AE8640  hpBefore=270 maxBefore=270 -> hpAfter=411 maxAfter=411
debug.aptitude-trace id=26  subsystems=rpg.resource.base,rpg.progression,rpg.aptitude,
  rpg.species-layer,atom.derived,l2b.derived
  bonusDefenseContribs=aptitude.Fortitude:Flat:177
zombie.spawn id=88  sourceKind=creature.progression.v1  sourceId=general:normalzombie
```

A real entity, resolved through the real species layer, taking real Hub-derived stats. No
fabrication anywhere in that chain.

### 5.2 Element resolution on the Unity side — **PROVEN as data**

`elements:{"primary":"earth"}` on real snapshots, resolved by
`LawnElementResolverHost.Resolve(ptr)` (`ActorHudBuilder.cs:108-121`) — the same species resolution
elemental combat uses, not a second map. Then, end to end and all measured on my own server/deploy:

```
earth  ->  hudGlyph "stone"     (GET /api/catalogs/actor-surface, v2 catalog, Program.cs:107-108)
stone.png present at H:\Games\.fusionrpg-pool\slot-1\Mods\assets\actor-hud-elements\stone.png (5681 B)
stone.png served 200 image/png from http://127.0.0.1:5190/actor-hud-elements/stone.png
```

The host reads the same v2 catalog the Server does (`RpgHost.cs:133`), so the two halves agree.

### 5.3 The draw switch is a real player setting, and it propagates — **PROVEN**

The default is off, and the registry says why:

```
GET /api/settings -> lawn.worldHud, Bool, value=false, isDefault=true,
  summary "Draw the in-world actor HUD. Off by default: it dominated vfx.tick at 2.513 ms/frame."
```

`ActorHudPool.cs:95-103` documents the same: `vfx.tick` was **2.513 ms/frame at 80 entities**, 91.8%
of `loop.tick`, against a 2 ms/frame budget, so the owner's instruction was "we will disable a
default and add user setting on the web FE". **So an empty HUD screenshot on a default install is
correct product behaviour, not a bug** — worth stating because it is the most likely misreading of
this report.

The switch demonstrably reaches the engine (the effect, not the store):

```
id=345  early=world-hud-off  hudSlots=0  shaderOk=false     <- before
id=378  early=idle           hudSlots=0  shaderOk=true      <- after: canvas + shader now ready
id=558  early=ok             hudSlots=2  shaderOk=true      <- with 2 live actors
```

`world-hud-off` is written only at `ActorHudPool.cs:127`, so its *appearance* proves `TickSync` is
running every frame; its *disappearance* proves the push landed (`Program.cs:2152-2157` maps the
setting to the `hud.world` injector command).

### 5.4 The HUD places slots on a live board — **PROVEN, telemetry scope**

`early="ok", hudSlots=2` with 2 live actors (ids 558, 892, 1050). Because `_worldHud++`
(`ActorHudPool.cs:284`) is the **last** statement of `SyncEntity`, reaching it means each actor got
past `ActorHudCache.GetOrBuild` (line 210), `ActorHudVisibility.ShouldShow` (line 212),
`AnchorResolver.Resolve` (line 217) **and** `ActorScreenAnchorResolver.TryResolve` (line 219) — the
full geometry chain — and then had `slot.Root.SetActive(true)` and
`anchoredPosition = (anchor.CenterX, anchor.TopY)` applied (lines 228-232). Both actors do pass
`ShouldShow`: the zombie via `LevelBand is not null` and the Peashooter via `Tier != Normal` plus
`Flags.Count > 0` (`ActorHudVisibility.cs:11-20`).

`shieldBars=0, drawnOwners=0, dataOwners=0` are **correct, not faults**: every actor on my board had
`resources.shield {hp:0, max:0, stacks:[]}` and `statuses: []`, and
`ActorHudRowResources.Sync` returns false when `shield.Max <= 0` (line 22). The shield row and the
status row were never exercised by this board.

### 5.5 The FE's transport to my server is live

`hub.ts:8` builds `${apiBase() || window.location.origin}/hub/rpg`; in a production build
`apiBase()` returns `""` (`rest.ts:4-5`), so it is same-origin — which is why serving the SPA from
the Server is required. On my server:

```
POST /hub/rpg/negotiate?negotiateVersion=1 -> 200 application/json
  negotiateVersion=1 connectionId=FdYvSChnjl9e5WVfvulaDQ
  availableTransports: WebSockets[Text,Binary]  ServerSentEvents[Text]  LongPolling[Text,Binary]
```

And the production wire from that hub into the lawn projector exists:
`hub-provider.tsx:67-69` (`onEvent` → `appendLogEvent`) → `log-store.ts` → `lawnProjectorFold.ts:1313`
(`case "debug.actor-hud"`) → `foldActorHud` → `SyncFromModelSystem` → `setHudDisplay`. Note the
`window.__fusionRpgAppendLogEvent` hook is documented in-source as *"Playwright e2e — append capture
events **without a live hub**"* (`log-store.ts:336-337`), which is exactly why the browser lane had
to use it and why the real half was untested.

---

## 6. AUDIT-2 — confirmed as a code defect; the five-event re-measurement could NOT be run

**The defect is confirmed by reading the code, and the finding is sharper than the todo's wording.**
`ActorHudDisplay.ts:21-33`:

```ts
if (!scene.textures.exists(key) && !scene.load.isLoading()) {
  scene.load.image(key, url);
  scene.load.start();
}
return scene.textures.exists(key) ? key : undefined;   // <-- read immediately after an async load
```

and the draw site, `ActorHudDisplay.ts:130-136`:

```ts
const texture = ensureElementTexture(scene, id);
if (!texture || size <= 0) return;                      // <-- early return, glyph skipped
```

`scene.load.image` + `start()` is asynchronous, so `textures.exists(key)` is false on that same
call, the draw site skips, and **nothing re-runs `setHudDisplay` until another snapshot arrives** —
so whether a glyph appears depends on how many board-stats events have happened, not on whether the
glyph resolves. `hudSlots`/telemetry cannot detect this at all, which is why it survived the merge.

**I could not re-take the five-event measurement.** It needs the web in a real browser, and **no
desktop browser is attached to this session** (`browser.disconnected: "No desktop browser is
connected to this session"`). So AUDIT-2's *measurement* is unchanged; its *mechanism* is confirmed.

**What changed for the next lane, and it is the actionable part:** the input AUDIT-2 needs now
exists in reality. 21 genuine Unity-produced `debug.actor-hud` events carry
`elements:{"primary":"earth"}`, and `stone.png` is deployed and served. A browser lane can now drive
the real race with real data for the first time — no FE hook, no fixture.

**A caution on interpreting a null result.** The first events on a board are the ones most likely to
be element-less, because `BuildElements` needs the species layer to have resolved. On my board the
Peashooter's first two HUD events (ids 78, 111) had `elements=null` and only later ones (521, 530)
carried `earth`. A five-event window that starts at board entry can therefore contain **no glyph to
draw at all**, and reading that as "still broken" would be a third false red. Sample the window
*after* the first `elements`-bearing event.

---

## 7. Findings — reported, NOT fixed

Every item below is a defect with a `file:line` and a reproduction. **I patched nothing.** Editing
the Injector mid-probe would have destroyed the baseline, and `scripts/`, `src/` and `web/` are
outside this lane's fence.

**F1 — `deploy-play.py` cannot build the FE on this machine. (blocker, every pooled deploy)**
`gk-fusion/scripts/deploy-play.py:155-159` runs `npm` with `shell=False`; `CreateProcess` resolves `npm.exe`
only, and nvm4w ships `npm.cmd`/`npm.ps1`. Repro: `python -c "import subprocess;
subprocess.run(['npm','--version'])"` → `FileNotFoundError [WinError 2]`. Deploy dies `exit 1` at
stage 3/12. Needs `npm.cmd` on Windows, or a resolved absolute path. *Worked around with
`--no-rebuild-ui`.*

**F2 — the pool registry cannot see a server squatting on a slot's port.** See SPOT-1 in §2.1.
`slots.json`'s `process` tracks the game, not the server, so `-Status` reports `free`/`ready` for a
slot whose port is bound. A lane then picks a port it cannot use, and `deploy-play.py` refuses to
publish against it. A `ports` probe in `-Status`, or a per-slot recorded server pid, would close it.

**F3 — a pooled lane has no supported path to a fresh server while the owner's server is up.**
`dist/FusionRpg.Server/*.dll` locked by pid 56816 → `MSB3027`, `REFUSED [server_publish]`. The only
in-tool escapes are owner-only `--restart-server` and `--reuse-build`, and the seed import would
write the owner's live `dist/.../data`, which `session-boundary.md` §7 forbids. A pooled publish
target (or a per-slot publish dir) is the missing capability. *Worked around by publishing to my own
tree.*

**F4 — the cfg stage is unreachable behind an earlier refusal, which is the state it exists to
prevent.** The always-on cfg write (`deploy-play.py:499-513`, moved out of the `-NoGame` branch
specifically to stop the SSH4.9 class) sits *after* the publish stage, so the F3 refusal skipped it
and left slot-1's `Mods/fusionrpg.cfg` reading `ServerUrl=http://127.0.0.1:5088` — the owner's
default. Moving the cfg write above the publish stage makes the guard total.

**F5 — the screenshot path is structurally blind to a UI-overlay HUD. (most important finding)**
The actor-HUD canvas is `RenderMode.ScreenSpaceOverlay` with `overrideSorting` and
`sortingOrder = short.MaxValue` (`ActorHudPool.cs:391-397`). An overlay canvas is composited by the
engine *after* camera render, so it cannot appear in a camera-render capture — and the repo's own
comments say so: `camera-fallback` is *"Misses UI overlays"* (`ScreenshotRunner.cs:136-137`) and the
fallback path *"uGUI overlays may be missing; the emit says which primitive ran"*
(`ScreenshotRunner.cs:72-74`). The only UI-inclusive primitive is `screen-readback`, which needs a
Repaint to consume the capture within `RepaintGraceMs` (2000 ms, `ScreenshotRunner.cs:33`).

Measured: `repaintsSeen=0` on **all seven** captures, including four taken after
`SetForegroundWindow` + `BringWindowToTop` on the game window, and those four are **byte-identical**
(sha256 `5E774967BACA2B53…`). `primitive` was `camera-fallback-no-repaint` every time.

So in a non-interactive session **no automated lane can close a UI-overlay HUD audit**, and the
absence of HUD marks in §3's frame is uninformative. The name-based scene search does not help
either: `debug_evaluate_search` scanned 139 objects and found no `FusionRpgActorHudCanvas`, because
the canvas carries `HideFlags.HideAndDontSave` (`ActorHudPool.cs:392`) and is excluded from scene
scans by construction. Closing this needs either an interactive session, an owner eyeball, or a
third capture primitive that renders overlay canvases to a RenderTexture.

**F6 — the fallback returns a stale frame, and the injector's own state view disagrees with the
presented image.** With `debug_game_state` reporting `InMatch, plants=1, zombies=1,
phaseMismatch=False` immediately before the capture, `lawn-05` and `lawn-06` both show the
Adventure **level-select map**. A live, measured instance of `live-probe-standard.md` §6 — and a
trap for the next lane, which would reasonably read `InMatch` as proof it was looking at a lawn.

**F7 — doc drift, no code defect.** `tasks/actor-hud-todo.md:200` states the Injector host reads
`actor-hud.v1.json` at `RpgHost.cs:203`, and that a v1→v2 publish was missed. At the merged head the
host reads **`actor-hud.v7.json` at `RpgHost.cs:239`**, matching the Server's `Program.cs:91`, and
`element-catalog.v2.json` at `RpgHost.cs:133`. That todo row is closed by the merge and its prose is
stale; the todo should say so.

---

## 8. What remains unproven

1. **Whether the actor HUD is visible on screen, and whether the element glyph renders.** Blocked by
   F5, not by a failure. The draw loop places slots with correct geometry (§5.4); nothing here shows
   a pixel. **A human looking at the running game, or an interactive session, is the only instrument
   that can settle it.**
2. **Whether `ActorHudRowElements.Draw` was actually reached.** `_worldHud` increments regardless of
   whether the element row drew, so telemetry cannot distinguish "row drew" from "row skipped". A
   board whose actors carry a shield and statuses would exercise the shield and status rows too —
   mine never did (`shieldBars=0` throughout).
3. **AUDIT-2's five-event measurement.** Needs a browser; none attached to this session.
4. **The Server→web hop in a real browser.** Transport proven (§5.5); the browser leg not run.
5. **Whether the web's Phaser HUD would draw `stone` on the first real Unity event** — now testable
   with real data for the first time (§6).
6. **Everything non-Chromium, other resolutions/DPI, and a full combat board.** One browser-free
   session, one 960×540 window.
7. **`debug_preflight` is not slot-aware** (incidental): it resolved the game dir from `.env`'s
   `FUSIONRPG_ML_GAMEDIR_DEFAULT` — the **owner's** install, not my slot — and reported
   `dll-freshness FAIL` about `dist/FusionRpg.Server/FusionRpg.Core.dll`, a tree this lane was not
   using and could not republish. `deploy-play.py`'s own freshness stage said `Freshness OK` for the
   artifacts that actually matter. On a pooled slot the preflight's `game-dir`, `interop-refs`,
   `dll-freshness` and `data-dir` checks describe a different install than the one under test.

---

## 9. Open questions (owner's call; none of these are mine)

1. **F1/F3/F4 are one capability or three?** A pooled publish target would likely absorb F3 and let
   the cfg write run; F1 is independent and one line.
2. **Should a UI-overlay HUD be auditable by an agent at all?** Today the answer is no (F5). Either
   fund a capture primitive that sees overlay canvases, or record that overlay-HUD sign-off is
   owner-eyeball-only, so the next lane does not spend an hour rediscovering it.
3. **AUDIT-2's acceptance** — make the loader awaitable, or make the assertion patient? Still a
   contract change at the FE→game seam, so `decisions.md` first (unchanged by this lane).
4. **Should `early:"idle"` be less ambiguous?** It currently means both "0 actors drew" and "0
   actors existed". I misread it once; another agent will. A count of walked actors would separate
   them.
5. **F2's fix shape** — probe the port in `-Status`, or record the slot's server pid in
   `servers.json` and check it in `-Status`?

---

## 10. Housekeeping

- **Slot released**: `[live-slot] RELEASED 1 slot(s) for actor-hud-unity-live-20260926;
  ready-to-claim now: 3`. All three slots `ready`, `process none`.
- **I restored the state I mutated**: `lawn.worldHud` set back to the documented default `false` via
  the real endpoint, confirmed in `GET /api/settings` and in
  `rpg_user_settings (1, 'lawn.worldHud', 'false', ...)`, so the next lane inherits the default
  rather than my mutation.
- **Only this lane's processes were killed**: server pid 55020, game pid 53536. Pid 78664 and
  56816 were verified still running at the end.
- **No code changed.** `git diff a49fa229c -- src web data scripts tools` is empty. The only dirty
  files in the tree are two `.commandcode/taste/*` files from another stream, left untouched.
- **Not run, deliberately**: `verify-change.py` (this lane changed no production path, so there is
  no path-owned boundary to select; the unfiltered suite is CI/nightly/release-owned) and the
  scoped `--verify` deploy bundle (same reason).
- **Known weakness in this evidence, flagged not glossed**: the nine screenshots and the two probe
  scripts are on disk under
  `C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-unity-live-20260926\`, **not in the
  repo**, because this lane's fence admits exactly two files. A decision resting on those images
  depends on a temp path. The owner or manager should decide whether to admit them under
  `tasks/reports/`; `relay_readback.py` and `read_setting.py` regenerate the event and persistence
  readings in seconds. The same weakness was flagged by the browser-proof lane and is still open.
- **Measurement notes for whoever repeats this**: (i) `dotnet test` leaves `testhost.exe` alive and
  the next build fails `MSB3027` — I ran no tests, but the F3 `MSB3027` had a *different* cause
  (a running server holding `dist/`), so do not pattern-match the error to the wrong cause; (ii)
  `$env:` does not survive between shell calls, so every command above sets what it needs inline;
  (iii) `--urls` and `ASPNETCORE_URLS` are ignored by this app — only `FUSIONRPG_URLS` binds.

# SSH4.9 — live probe: **NOT RUN — aborted by a live-deploy incident on the owner's install**

## What happened (incident, reported in full)

Slot 1 was acquired correctly (`scripts/live-slot.ps1 -Acquire -Session strain-splice-host-20260922`
→ `H:\Games\PVZ-Fusion-Tests\slot-1-strain-splice-host-20260922`). I then ran the injector deploy with
what I believed was a slot-scoped game dir:

```
export FUSIONRPG_GAME_DIR='H:\Games\PVZ-Fusion-Tests\slot-1-strain-splice-host-20260922'
pwsh -NoProfile -File scripts/deploy-play.ps1 -NoServer
```

That `export` did **not** reach the script: `FUSIONRPG_GAME_DIR` is unset in the tool's shell, and the
`export A=B && pwsh …` form did not propagate it, so `deploy-play.ps1` fell back to the OWNER's install.
It:

- wrote `H:\Games\PVZ-Fusion-3.9_MelonLoader\Mods\fusionrpg.cfg`;
- refreshed the injector in `H:\Games\PVZ-Fusion-3.9_MelonLoader\Mods\`;
- launched `H:\Games\PVZ-Fusion-3.9_MelonLoader\PlantsVsZombiesRH.exe` with
  `FUSIONRPG_SERVER_URL=http://127.0.0.1:5088` — the owner's port.

**Containment:** the launched process (PID 75728, started 10:20:16) was stopped by PID (verified gone),
my slot was released (`-Release -Session strain-splice-host-20260922`, pool back to free 3/3), and no
further deploy or probe was attempted. **Not restorable:** the previous content of the owner's
`Mods\fusionrpg.cfg` (the deploy overwrote it). The injector DLLs placed there are the same artifacts the
owner's own deploys would place.

**Root cause, and the check that works:** `FUSIONRPG_GAME_DIR` must be set *inline* for the command —
`FUSIONRPG_GAME_DIR='<slot>' pwsh -NoProfile -File scripts/deploy-play.ps1 …` — verified by
`FUSIONRPG_GAME_DIR='<slot>' pwsh -NoProfile -Command '$env:FUSIONRPG_GAME_DIR'` printing the slot. A
bash `export` on its own line does not reach the script. Any future lane must assert the resolved game
dir from the deploy's own output (`Host:`/`Injector:` lines) BEFORE letting it launch anything.

## Probe status

**NOT RUN.** No evidence exists for any acceptance line: no real chassis was socketed, no word was
equipped, and `combo:…#c0` was never read back through the real sheet. The full suite the row names as
its prerequisite was also not run.

## Not proved

- Every acceptance line of SSH4.9: the socket/equip/read-back/withdraw sequence on a real save.
- The pre-probe full suite.
- Whether the deploy's writes to the owner's install changed anything the owner cared about.

## 2026-09-22, second attempt (post-merge) — correct slot, still NOT RUN, new blocker

The pool guard works: with `FUSIONRPG_GAME_POOL`, `FUSIONRPG_GAME_SOURCE` and `FUSIONRPG_ML_GAMEDIR`
set **inline**, `deploy-play.ps1 -NoServer -ServerUrl http://127.0.0.1:5399` deployed into MY slot —
its own output read `Injector: H:\Games\PVZ-Fusion-Tests\slot-1-strain-splice-host-20260922\Mods` and
`Launching …slot-1-strain-splice-host-20260922\PlantsVsZombiesRH.exe (FUSIONRPG_SERVER_URL=http://127.0.0.1:5399)`.
The owner's install was NOT touched this time.

**Blocker (deploy-script defect):** the same run printed
`==> Server already running at http://127.0.0.1:5088/health -- skipping DLL publish (exe locks its own DLLs)`,
because the script's health probe is the hardcoded `$Health = "http://127.0.0.1:5088/health"`
(`scripts/deploy-play.ps1:90`) and ignores `-ServerUrl`. The owner's server occupies :5088, so the
publish was skipped and `dist/FusionRpg.Server/` contains only `data/` and `wwwroot/` — **no
`FusionRpg.Server.exe`** — so my :5399 server could not be started and the game had nothing to talk to.
Starting the server (`dotnet run`/`dotnet publish` by hand) is a workaround the incident rules say not to
improvise, so I stopped: my slot's game (PID 63388) was stopped, the slot released (free 3/3), and the
owner's :5088 server left running (health 200). A `FusionRpg.Server.exe` from another lane's worktree
(`cmdc-live-qa`) is running and was left alone.

**What would unblock it:** a publish path that does not depend on :5088 — e.g. a `-ForcePublish` switch,
a `$Health` derived from `-ServerUrl`, or publishing directly (`dotnet publish gk-core/src/FusionRpg.Server -o
dist/FusionRpg.Server`) before starting my own server on my own port.

## Not proved

- Every SSH4.9 acceptance line: no chassis socketed, no word equipped, no `combo:…#c0` read through the
  real sheet, no withdrawal — on either attempt.
- The pre-probe full suite.

## 2026-09-22, third attempt (post 9e7b5c7f6 / 585a93aa7) — CONNECTION PROVEN, data path red

Prerequisite fixed: `$Health` is now `"$ServerUrl/health"` (`scripts/deploy-play.ps1:102`), so the pooled
deploy health-checks ITS OWN port and publishes instead of skipping:
`FUSIONRPG_GAME_POOL=… FUSIONRPG_GAME_SOURCE=… FUSIONRPG_ML_GAMEDIR=H:\Games\PVZ-Fusion-Tests\slot-1 pwsh
-File scripts/deploy-play.ps1 -NoServer -ServerUrl http://127.0.0.1:5101` → `Injector:
…\slot-1\Mods`, `Launching …\slot-1\PlantsVsZombiesRH.exe (FUSIONRPG_SERVER_URL=http://127.0.0.1:5101)`,
and `dist/FusionRpg.Server/FusionRpg.Server.exe` now exists.

Then the sanctioned reference harness, with the env inline and PATH augmented for its own warning
("never from a pwsh spawned by bash"):

```
FUSIONRPG_GAME_POOL='H:\Games\PVZ-Fusion-Tests' FUSIONRPG_GAME_SOURCE='H:\Games\PVZ-Fusion-3.9_MelonLoader' \
  pwsh -NoProfile -Command "$env:PATH='C:\Program Files\dotnet;C:\Users\NeneScarlet\miniconda3;…'+$env:PATH;
  & ./scripts/prove-slot-connection.ps1 -Session strain-splice-host-20260922"
```

Verdict it printed:

| Reading | Value |
|---|---|
| slot / slotUrl / health | 1 / `http://127.0.0.1:5101` / 200 |
| slotCfg | `ServerUrl=http://127.0.0.1:5101` |
| injectorLine | `FusionRpg MelonMod host ready, server=http://127.0.0.1:5101` |
| injectorSaysSlotUrl | True |
| serverSawClient / connections / failures | the client's request arrived / 2 / 4 |
| **CONNECTION PROVEN** | **True** |
| **DATA PATH HEALTHY** | **False** (4 server-side failure lines) |
| owner untouched | **True** (cfg md5 + :5088 pid identical before/after) |

Cleanup it performed and I verified: my slot's game PIDs 63040/64152 killed, two foreign PIDs (39944,
42260) left alone, slot server (pid 56332, :5101) stopped, slot released (ready-to-claim 1). No stray
`PlantsVsZombiesRH.exe` or `FusionRpg.Server.exe` of mine remains; the owner's :5088 server was never
touched.

## NOT proved (SSH4.9 stays OPEN)

- **The row's actual acceptance: a real word on the real sheet.** No chassis was socketed through
  `/api/items/workbench/*`, no item equipped through `/api/items/equip`, and no `combo:…#c0`
  contribution was read back through the real sheet — because the data path is failing server-side
  (`DATA PATH HEALTHY False`, 4 failure lines; the known F13 row in `tasks/party-dungeon-todo.md`, being
  fixed by another lane). Reporting that as observed rather than as this lane's failure, per the
  orchestrator.
- The pre-probe full suite.
- The withdrawal half (unequip → binding gone) — unreachable without the read-back.
- Attempt 1 and attempt 2's failures (owner-install deploy; skipped publish) are recorded above; this
  attempt supersedes them.

## 2026-09-22, attempt 4 (F13 merged: ba258649d) — CONNECTION PROVEN **False**, row stays OPEN

Command (env inline, PATH augmented for the script's own warning):

```
FUSIONRPG_GAME_POOL='H:\Games\PVZ-Fusion-Tests' FUSIONRPG_GAME_SOURCE='H:\Games\PVZ-Fusion-3.9_MelonLoader' \
pwsh -NoProfile -Command "$env:PATH='C:\Program Files\dotnet;C:\Users\NeneScarlet\miniconda3;…'+$env:PATH;
  & ./scripts/prove-slot-connection.ps1 -Session strain-splice-host-20260922"
```

Verdict block, verbatim:

```
  slot                   1
  slotUrl                http://127.0.0.1:5101
  serverBinary           152064 bytes, built 2026-09-22 16:53:11
  slotCfg                ServerUrl=http://127.0.0.1:5101
  slotHealth             200
  gamePid                75380
  injectorLine           [17:07:36.336] [FusionRpg] FusionRpg MelonMod host ready, server=http://127.0.0.1:5101
  injectorSaysSlotUrl    True
  serverSawClient
  serverLog              H:\Games\PVZ-Fusion-Tests\slot-1-server.log
  CONNECTION PROVEN       False
  owner untouched         True
```

- **`CONNECTION PROVEN` = False.** The injector half is present and correct (`injectorLine` names my slot
  URL); the server half is empty — `serverSawClient` has no value.
- **`DATA PATH HEALTHY` was NOT printed.** The reference script emits that line only when the connection
  is proven (`scripts/prove-slot-connection.ps1:232` is inside the connected branch), so the data path is
  **not evaluated**, not "unhealthy", in this run. F13's fix is present in the tree
  (`EnsureColumn(db, "dungeon_domain", "first_clear_ref", "TEXT")`, `RpgStore.Domains.cs:92`).

**What I observed rather than concluding from the empty field** (your instruction): the run was repeated
with `-KeepRunning` and polled for a further **150 s** after the injector's host-ready line.
`H:\Games\PVZ-Fusion-Tests\slot-1-server.log` contains **zero** `Connection id` / `Request id` / `HTTP`
lines at any point — 1195 bytes, all `Microsoft.Hosting.Lifetime` startup text, ending at the content-root
line. The game itself was alive and rendering throughout (`[perf] fps=60 frameMax=17.23ms …` appears in
the same log tail at 17:08:24), so this is **not** a game that failed to start: it reached gameplay and
the injector never issued an API request in this session. For contrast, attempt 3 (same harness, before
the merge that reordered deploy-before-server) DID record 2 connections — so the path can carry traffic;
this run's ordering/timing did not produce the call. I did not treat the empty field as proof of
anything beyond "no client traffic was observed in ~3.5 minutes".

**Cleanup:** my slot's game (78216) and my server (47732) stopped, `lane-server -Stop -Slot 1` confirmed
gone, slot released (`ready-to-claim now: 1`), no foreign process touched, owner untouched True.

## SSH4.9 remains OPEN — acceptance NOT met

- No chassis was socketed through `/api/items/workbench/*`, nothing was equipped through
  `/api/items/equip`, no `combo:…#c0` was read back through the real sheet, and no withdrawal was
  performed — the acceptance is untouched by attempts 1–4.
- **The pre-probe full suite (AGENTS.md point 3) is still owed and was NOT run.**
- Row left at `- [ ]`; the earlier tick was reverted by the manager's re-open ruling and is not reinstated.

## 2026-09-22, attempt 5 (deploy -NoGame fix ec0b1ce4d merged) — verdicts verbatim, plus a harness/logging finding

Command:

```
FUSIONRPG_GAME_POOL='H:\Games\PVZ-Fusion-Tests' FUSIONRPG_GAME_SOURCE='H:\Games\PVZ-Fusion-3.9_MelonLoader' \
pwsh -NoProfile -Command "$env:PATH='C:\Program Files\dotnet;C:\Users\NeneScarlet\miniconda3;…'+$env:PATH;
  & ./scripts/prove-slot-connection.ps1 -Session strain-splice-host-20260922"
```

The two verdict lines, verbatim:

```
  CONNECTION PROVEN       False
  DATA PATH HEALTHY       (not printed)
```

(`DATA PATH HEALTHY` is emitted only inside the connected branch — `prove-slot-connection.ps1:232` — so it
reads as "not evaluated", never as "unhealthy".)

**But the connection is real, and the harness cannot see it.** With the corrected order (deploy
`-NoGame` → start slot server → gate on `/health` → launch game → evidence), the INJECTOR's own log
`H:\Games\PVZ-Fusion-Tests\slot-1\MelonLoader\Latest.log` reads:

```
[18:11:54.793] [FusionRpg] FusionRpg MelonMod host ready, server=http://127.0.0.1:5101
[18:12:03.881] [FusionRpg] SignalR connected
[18:12:04.023] [FusionRpg] SignalR reconnected + re-joined + Hello (grant rehydrate)
```

A `Hello (grant rehydrate)` is only answerable by a live server, so the game reached MY slot server. The
server-side half is empty for a logging reason, not a connection reason: my slot server's log
(`H:\Games\PVZ-Fusion-Tests\slot-1-server.log`) contains **0** `Connection id` / `Request id` / `POST` /
`GET` lines — only `Microsoft.Hosting.Lifetime` startup text — **including for the harness's own
`/health` probes, which returned 200 five seconds earlier**. A pattern that cannot match the harness's own
successful requests cannot witness the game's either. So `serverSawClient` is unmeasurable against this
server's current logging configuration; evidence-2's absence carries no information here.

(Contrast: attempt 3 recorded 2 connections in the same file with the same harness. Between then and now
the server binary was rebuilt twice by the merged tooling, so the most likely cause is a logging-level
change in the published server, not the game.)

Cleanup verified: my slot's game (73076) killed, a foreign PID (76276) left alone, slot server (59788,
:5101) stopped, slot released (`ready-to-claim now: 1`), owner untouched True.

## SSH4.9 remains OPEN, acceptance NOT met

- Not one acceptance line ran: no chassis socketed through `/api/items/workbench/*`, nothing equipped
  through `/api/items/equip`, no `combo:…#c0` read back through the real sheet, no withdrawal. The run
  above was a connectivity/verdict run, not the acceptance.
- The row is left at `- [ ]`. The earlier unjustified tick was reverted by the manager and is not
  reinstated.
- **The pre-probe full suite (AGENTS.md point 3) is still owed and was NOT run.**

## 2026-09-22, attempt 6 — live slot up, data path SERVES READS, acceptance steps not completed

Live slot brought up with `prove-slot-connection.ps1 -Session strain-splice-host-20260922 -KeepRunning`:
slot 1, server on `http://127.0.0.1:5101` (`/health` 200), game launched and connected (injector's own
`SignalR connected` + `Hello (grant rehydrate)`). The manager has accepted the injector-side reading as
the connection proof.

**Data-path reading (positive, and the first direct one):**

```
GET http://127.0.0.1:5101/api/items/armoury/1        -> 200  {"total":4, ...}
```

Four real rows, served through the normal read path:

```
onboarding-dave-equipment-1            | item.first-clear-almanac-seed | almanac  | assigned=True  locked=True
a1b2c3d4e5f640008000000000000001       | item.humanoid-main-hand-a-001 | heirloom | assigned=False locked=False
34943b9e07674edb8f6a5ffe04f85b4f       | item.equip-proof-helm          |          | assigned=False locked=False
10b4111299c74d5ba01db759979aafeb       | item.equip-proof-blade         |          | assigned=True  locked=False
```

No `no such column` error and no 500, so F13's fix is not blocking the armoury read. API surface
discovered for the remaining steps: `/api/items/equip`, `/api/items/unequip`,
`/api/items/workbench/socket-add`, `/api/items/workbench/socket-insert`,
`/api/items/{instanceId}/combinations` (and `/api/aptitudes` serves the SPA, not JSON).

**The four acceptance steps: NOT completed.** Step (1) socket a real chassis was not run, so (2) equip,
(3) `combo:…#c0` read-back on the real sheet and (4) withdrawal are all unrun. This session's budget ran
out inside the live cycle; the socketable unassigned chassis `a1b2c3d4e5f640008000000000000001`
(`item.humanoid-main-hand-a-001`) is the concrete starting point for whoever resumes, and the harness is
one cheap change from being usable for it (`-KeepRunning` keeps both halves up).

**Harness witness defect, restated as requested:** `serverSawClient` greps
`<pool>\slot-N-server.log` for `Connection id |Request id `, but the server the merged tooling publishes
writes NO request lines at all — not even for the harness's own `/health` probes that returned 200. The
harness should print that reason (e.g. "server log carries no request lines; witness unavailable")
instead of an empty field, so a future probe is not left guessing whether the client was absent or the
witness blind. Both earlier runs' evidence (attempt 5) is in the section above.

**Cleanup verified:** my slot's game (70028) and server (69060) stopped, `lane-server -Stop -Slot 1`
confirmed gone, slot released (`ready-to-claim now: 1`), no foreign process touched.

## SSH4.9 status: OPEN — acceptance NOT met

- The row stays `- [ ]`: none of the four acceptance lines has passed.
- **The pre-probe full suite (AGENTS.md point 3) was NOT run by this lane**; the manager states a gate is
  running it now.

## 2026-09-22, attempt 7 — live slot up, four steps attempted, blocked by the SLOT's inventory

Live slot: `prove-slot-connection.ps1 -Session strain-splice-host-20260922 -KeepRunning` → slot 1,
server `http://127.0.0.1:5101` (STARTED pid 78436, `/health` 200, data dir
`H:\Games\PVZ-Fusion-Tests\slot-1-data`), game launched.

Every call below is verbatim (status + body excerpt).

**(0) real state read — healthy**

```
GET  /api/items/armoury/1                -> 200 {"total":4,...}   4 real rows
GET  /api/unique/actors?playerId=1       -> 200 {"playerId":1,"items":[{"instanceId":"0728d470f2ae4ee68dba150d478183ca", ... "side":"zombie","typeId":246,"phase":"Roster","level":1 ...
GET  /api/items/surfaces/1               -> 200 [{"surface":"armoury","state":"Ready",...},{"surface":"socketBench","state":"L"...
GET  /api/items/a1b2c3d4e5f640008000000000000001/card -> 200 {"blocks":[{"blockKey":"item.card.header",..."name":"Ferocious Honed Hatchet","baseName":"Honed Hatchet","classNounKey":"class.blade","roleNameKey":"role.armament-prim...
```

**(1) socket a real chassis — REFUSED, twice, legitimately**

```
POST /api/items/workbench/socket-add {playerId:1, instanceId:"a1b2c3d4e5f640008000000000000001", recipeId:"recipe.019", correlationId:"ssh49-bore-1"}
     -> 409 {"ok":false,"verb":"socket-add","reason":"ContentRuleViolated: socket.not-socketable: this base type declares no sockets, so there is nothing to widen",...}

POST /api/items/workbench/socket-add {playerId:1, instanceId:"34943b9e07674edb8f6a5ffe04f85b4f", recipeId:"recipe.019", correlationId:"ssh49-bore-helm-1"}
     -> 409 {"ok":false,"verb":"socket-add","reason":"item.container-missing: 'item.equip-proof-helm' is not in the catalog",...}
```

Both are **healthy domain refusals** (no 500, no `no such column`), so the workbench route and the data
path behind it serve correctly. But neither chassis is socketable: the heirloom
`base.honed-hatchet` declares **no sockets**, and the `item.equip-proof-*` rows are stale leftovers whose
containers are not in the catalog. My earlier "concrete unassigned socketable chassis" identification was
wrong — the armoury metadata does not carry `socketMax`, and the server refuses that base type.

**(1b) the slot cannot supply a socketable chassis or a gem**

```
GET  /api/items/workbench/inserts/1      -> 200 []            (the player holds NO insert/gem)
```

The player's whole inventory is those 4 rows: one socketless heirloom blade, one un-renderable
onboarding item, and two stale proof rows. There is **no** socketable chassis and **no** gem, and the
live API has **no sanctioned mint route** (the `/api/debug` group is game-side only — screenshot, act,
lawn, evaluate, derived-audit-actor, effect grant/withdraw — and nothing mints an item instance; the loot
pipeline has no endpoint). Fabricating one is forbidden by the debug rule, so steps (2) equip,
(3) `combo:…#c0` sheet read and (4) withdrawal could not be reached: there is nothing to socket.

**What would unblock it:** a slot whose player actually holds a socketable chassis and one gem — i.e. a
save that has played far enough to earn loot (or a sanctioned provisioning path, which does not exist
today). That is a resource/state question, not a code question; the routes and their shapes are all
recorded above and in attempt 6.

**Harness witness defect (restated):** `serverSawClient` greps `<pool>\slot-N-server.log` for
`Connection id |Request id `, but the published server writes no request lines at all — not even for its
own `/health` 200s. The harness should print that reason instead of an empty field.

**Cleanup verified:** my slot's game (15444) and server (78436) stopped, `lane-server -Stop -Slot 1`
confirmed gone, slot released (`ready-to-claim now: 1`), owner's `:5088` still 200 and never touched.

## SSH4.9 status: OPEN — acceptance NOT met

- All four acceptance lines remain unproven: no socket was opened on a real chassis, nothing was
  equipped, no `combo:…#c0` was read on the sheet, and no withdrawal was performed.
- **The pre-probe full suite was NOT run in MY cycle.** The manager measured the CC8 suite green at the
  merged head (Failed 0, Passed 18273), which satisfies the line at head; I state only that I did not run
  it here.

## 2026-09-22, attempt 8 — the catalog DOES declare sockets; the SAVE does not hold one

Following the manager's lead, in the order asked.

**(1) Which base types genuinely declare sockets — field and value.** The field is `socketMax`, on each
base-type entry. The named files confirm it:

```
gk-data/packs/fusion/data/seed/items/base-types/footing/humanoid/a.json
  item.humanoid-feet-a-001 "Quilted Sock"       socketMax 0
  item.humanoid-feet-a-002 "Spun Slipper"       socketMax 1
  item.humanoid-feet-a-003 "Secondhand Sneaker" socketMax 2   (…0/1/2 pattern, 12 entries)
gk-data/packs/fusion/data/seed/items/base-types/footing/plant/a.json
  item.plant-roots-a-002 "Creeping Rootlet"     socketMax 1
  item.plant-roots-a-003 "Tender Stolon"        socketMax 2   (…0/1/2 pattern, 12 entries)
```

Corpus-wide, computed over `gk-data/packs/fusion/data/seed/items/base-types/**/*.json`: **1178 base types, 984 of them
declare `socketMax ≥ 1`.** So "this base type declares no sockets" was true of my two candidates, not of
the catalog — the manager's lead was right, and my attempt-6/7 framing of it is corrected again.

**(2) What the save actually holds — real endpoint, real rows.**

```
GET /api/items/armoury/1  -> 200 {"total":4, …}
  item.first-clear-almanac-seed    socketMax=(not a corpus base type)  assigned=True
  item.humanoid-main-hand-a-001    socketMax=0                        assigned=False   <- my candidate
  item.equip-proof-helm            socketMax=(not a corpus base type)  assigned=False
  item.equip-proof-blade           socketMax=(not a corpus base type)  assigned=True
GET /api/items/workbench/inserts/1 -> 200 []      (no gem held either)
```

So the save holds **four** items: one socketless base type (`main-hand-a-001`, socketMax 0), one
onboarding container that is not a base type, and two stale `item.equip-proof-*` rows whose containers
are not in the catalog at all — and **not one of the 984 socketable base types**. Both candidate chassis
I had were the wrong pick, and the reads that establish this are all through the real endpoints.

**(3) and (4) — NOT RUN.** With no socketable chassis and no gem, `socket-add` has nothing to widen and
`socket-insert` nothing to insert; equip/sheet-read/withdraw would have no word to bind. Fabricating an
item is forbidden by the debug rule and would weaken the acceptance, so the four steps stay unexecuted.

**What a sanctioned route would have to be.** An operation that grants a player a REAL base-type item
instance through the real instance/loot pipeline — e.g. a server endpoint or CLI that mints an instance
from a shipped base type (and ideally one gem) for a named player on a pooled slot. Nothing like that
exists today: the `/api/debug` group is game-side only (screenshot, act, lawn, evaluate,
derived-audit-actor, effect grant/withdraw) and the loot pipeline has no endpoint, so today the only
sanctioned way for a save to hold a socketable item is to earn one in play. Until then SSH4.9's
acceptance cannot be exercised on a fresh slot.

**Cleanup verified:** my slot server (48468) stopped, `lane-server -Stop -Slot 1` confirmed gone, slot
released (`ready-to-claim now: 1`), owner's `:5088` still 200 and never touched, another lane's server
left alone.

## SSH4.9 status: OPEN — acceptance NOT met

- All four acceptance lines remain unproven (no socket opened, nothing equipped, no `combo:…#c0` sheet
  read, no withdrawal).
- **The pre-probe full suite was NOT run in MY cycle;** the manager measured the CC8 suite green at the
  merged head (Failed 0, Passed 18273), which satisfies that line at head.
- Harness witness defect unchanged: `serverSawClient` greps a server log that carries no request lines
  at all; the harness should print that reason rather than an empty field.

## 2026-09-22, attempt 9 — the grant route built, the probe run: socket + equip PASS, read-back BLOCKED by a real defect

### The route (owner ruling 2026-09-22, SSH4.9-P2)

`gk-core/src/FusionRpg.Server/DebugEndpoints.cs`, three RPG Server Debug routes, each labelled in-code with its
scope, each triggering a REAL write and reading the changed state back through the normal path:

| Route | What it does |
|---|---|
| `POST /api/debug/grant-item {playerId?, baseTypeId, rungId?, itemLevel?}` | resolves the base type from the SHIPPED `gk-data/packs/fusion/data/seed/items/base-types/**` corpus, **upserts its container** (`effect_container` is what the workbench's `TryResolve` reads), instantiates it with the REAL `Instantiator` (pool rolls + `OnInstantiate` params frozen there, not by the route), `SaveInstance` + `AcquireItem` + a real `ItemGenerationRow`; returns the instance read back from the store |
| `POST /api/debug/grant-gem {playerId?, containerId, qty?}` | validates the container against the SHIPPED gem corpus, `AdjustStock`, returns `ListStock` read-back |
| `POST /api/debug/grant-materials {playerId?, souls?, materials:[{materialId,qty}]}` | `AwardSouls` + `GrantMaterials`, returns `GetMaterialQty` read-back |

⛔ They mint nothing gameplay could not: base type, gem and materials all come from shipped corpora, and
the item carries a real generation row so every consumer resolves it exactly as a drop.

### The four steps, verbatim

```
(0) POST /api/debug/grant-item {baseTypeId:"item.humanoid-torso-a-005"}
    -> 200 {"ok":true,"scope":"RpgServerDebug","instanceId":"cb25dcde6b54404caec69ad0ab951787",
            "containerId":"item.humanoid-torso-a-005","socketMax":4,"role":"core-guard","generationRow":true}
    POST /api/debug/grant-gem x4 + grant-materials -> 200 each

(1) POST /api/items/workbench/socket-add   x4  -> 200 (opSeq 1,2,3,4; spent souls 3964 + substrate.humanoid.sound 12 + catalyst.forge 1 each)
    POST /api/items/workbench/socket-insert x4 -> 200 (opSeq 5,6,7,8; minted gem + essence paid)
(2) POST /api/items/equip {specimenId:"0728d470f2ae4ee68dba150d478183ca", role:"core-guard"}
    -> 200 {"ok":true,"verb":"equip","refId":"cb25dcde6b54404caec69ad0ab951787", ...}
(3) GET  /api/items/cb25dcde6b54404caec69ad0ab951787/combinations -> 200 []
    POST /api/internal/actors/0728d470f2ae4ee68dba150d478183ca/live-state -> 204 (no body)
(4) POST /api/items/unequip {specimenId:"0728d470f2ae4ee68dba150d478183ca", role:"core-guard"} -> 200
```

Steps (1) and (2) PASS: the real workbench opened four sockets and filled four gems on a real granted
chassis, and the real equip endpoint bound it. Step (3) does NOT: the word never reads back as
`combo:…#c0`, so step (4)'s "the next sheet read no longer shows it" has nothing to drop.

### Cause (read, not guessed) — a real defect, not a probe mistake

The fill's four families ARE the recipe's (`combo.splice-agility-bulwark` wants `atom.arm-plate`,
`atom.bulwark`, `atom.evasion`, `atom.evd-shift`; the granted gems `gem.g1-023`, `gem.g3-009`,
`gem.g3-018`, `gem.g1-054` carry exactly those families), and the rung-1 floors `[1,1,2,2]` are met by
two g1 + two g3 inserts. What breaks is the READ side's family lookup: after `socket-insert`, the socket
row's `insert_container_id` is the **minted, name-derived** container id, not the corpus key it was
inserted from — the card for the chassis reports `insertKey: "gem.sturdy-layering"`,
`"gem.bulwark-core"`, … for inserts issued as `gem.g1-023`, `gem.g3-009`. `ItemSurfaceEndpoints.InsertOf`
resolves a socket's `InsertDef` through the SHIPPED gem corpus by that id; a minted id the corpus does
not carry falls back to `new InsertDef(id, id, "", UnauthoredInsertTier)` — family = the container id —
which matches no recipe, so the fill is empty of combinable families and `/combinations` is `[]`.

So the mint's container id and the read path's corpus key disagree. Owning program: the gem
mint/read-path pair (species-gear-chain's `gem-tier`/T22 mint against the item-surface reader). Recorded
as a finding row in this program's todo rather than fixed here — it is not SSH4.9's own code.

### NOT proved / open

- **SSH4.9's acceptance lines (3) and (4)**: no `combo:…#c0` was read on the sheet, and no withdrawal
  effect was observed. The row is NOT ticked.
- The sheet route I used returned **204**; whether `POST /api/internal/actors/{id}/live-state` is the
  sheet read at all is now also open (it returns no body).
- No unit test for the three grant routes yet — they were exercised only through the live endpoints here.
- The pre-probe full suite was NOT run in my cycle (the manager measured it green at the merged head:
  Failed 0, Passed 18273).

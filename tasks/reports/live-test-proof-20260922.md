# Live-test path — proof record (2026-09-22)

Owner directive: *"Fix it and make this work completely"* → *"Run it"* → *"Resolve them"* → *"Prune"*.

Scope: make the pooled live-test path (game pool → per-slot server → injector → game) actually work, and
harden the last silent default that let a game talk to the owner's server without anyone asking it to.

Evidence below is copied from command output and job logs, not summarised. Anything not proven says so.

---

## 1. Injector silent fallback — hardened, and proven in the DEPLOYED artifact

**Defect.** `FileRpgConfig` pre-filled `ServerUrl` with `http://127.0.0.1:5088`, so `RpgHost.Initialize`'s
"no configured value" branch could never fire. A game with neither env nor cfg value silently talked to the
owner's server.

**Change** (4 files): `IRpgConfig` gains `bool ServerUrlFromFallback`; `FileRpgConfig` reports true only when
no `ServerUrl=` key was read; `DefaultRpgConfig` reports true; `BepInExRpgConfig` derives it by comparing
against `RpgHost.DefaultServerUrl`; `RpgHost.Initialize` logs a **Warning** naming the fallback URL and the
cfg it looked in when the env override is absent.

**Verification** — the deployment's own artifact, not a source reading:

```
H:\Games\PVZ-Fusion-3.9_MelonLoader\Mods\FusionRpg.Injector.MelonLoader.39.dll   648704 bytes  ServerUrlFromFallback=True
H:\Games\PVZ-Fusion-3.9_MelonLoader\Mods\FusionRpg.Injector.MelonLoader.dll      648192 bytes  ServerUrlFromFallback=True
```

**Two traps this cost, both recorded because both produced convincing wrong answers:**

1. **`src/**/bin` is the wrong place to look.** The `.39` host sets
   `<OutputPath>$(MlGameDir)\Mods\</OutputPath>` when its refs resolve, so a *successful* build writes
   straight into the game's `Mods\`. The dotted copies under `src/**/bin` are 4096-byte **skip-stubs** from a
   build that could not resolve `MelonLoader\Il2CppAssemblies\Assembly-CSharp.dll` — a stub build reports
   `0 Error(s)` and produces no code. Reading those stubs produced a false "the flag is missing".
2. **`Ambiguous project name 'FusionRpg.Injector'` is a property of the repo, not of the worktrees.**
   `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj` is a compatibility shim (its own first line says
   *prefer building …BepInEx.csproj directly*) that `ProjectReference`s the BepInEx project, whose
   `<AssemblyName>` is also `FusionRpg.Injector`. Restoring the shim therefore puts two projects with the same
   name in one graph. Build `gk-fusion/src/FusionRpg.Injector.BepInEx/…`, `…MelonLoader/…` or `…MelonLoader.39/…`
   directly; never the shim. Pruning worktrees did not and could not affect this.

---

## 2. Two pooled servers, simultaneously — with the seed fix exercised

Script: `D:/tmp/two-servers-proof.ps1` (job `b118680b7`, exit 0). Verbatim readings:

```
=== start TWO slot servers (own ports, own data dirs) ===
[lane-server] slot 1 rpg-hot.sqlite has an EMPTY species roster (0 rows) -- moved aside to rpg-hot.sqlite.poisoned-20260922T074201Z; reseeding
[lane-server] slot 1 data is empty -- seeding from D:\Works\source\plant-vs-zombie-rise-of-summoner\dist\FusionRpg.Server\data (SQLite online backup)
[lane-server] slot 1 server STARTED  pid=73800  url=http://127.0.0.1:5101
      seeded rpg-hot.sqlite (444 objects)
[lane-server] slot 2 rpg-hot.sqlite has an EMPTY species roster (0 rows) -- moved aside to rpg-hot.sqlite.poisoned-20260922T074204Z; reseeding
[lane-server] slot 2 server STARTED  pid=74352  url=http://127.0.0.1:5102
      seeded rpg-hot.sqlite (444 objects)
=== wait for both to answer /health (up to 3 minutes) ===
  slot 1 :5101 -> HTTP 200
  slot 2 :5102 -> HTTP 200
=== the owner's server, unchanged while both lane servers ran ===
  owner :5088 -> HTTP 200
  owner listener PID: 30644  (same as before: True)
=== stop both slot servers (only PIDs this tool recorded) ===
[lane-server] slot 2 server STOPPED (pid 74352, port 5102) -- only that recorded PID was touched
[lane-server] slot 1 server STOPPED (pid 73800, port 5101) -- only that recorded PID was touched
```

**Why the seeding fix was required.** `lane-server.ps1` seeded only when `rpg-hot.sqlite` was *absent*. The
previous run's crash left a schema-only database behind, so every later start skipped seeding and died on
`CreatureSpeciesCatalog.Configure received an empty species roster` — a fresh-looking crash with a stale
cause. Measured difference, which is why the fix tests the roster and not the file:

| | good source | poisoned slot DB |
|---|---|---|
| size | 546 MB | 1.4 MB |
| tables | 185 | 167 |
| `creature_species` rows | **904** | **0** |

The fix probes `select count(*) from creature_species`, moves a degenerate DB aside as
`rpg-hot.sqlite.poisoned-<UTC>`, and reseeds from a known-good data dir via SQLite's **online backup**
(correct while another server holds the file open; a plain copy of a live SQLite DB can tear).

Two statements in the *scratch* proof script still failed (`(if …)` used as a bare expression — a PowerShell
runtime error, not a parse error). They suppressed two cosmetic readings only; the health, listener, data-dir
and owner-untouched readings above all printed.

---

## 3. Real connection (slot → its own server)

Script: `scripts/prove-slot-connection.ps1` (new). Requires **both** halves, read from two different
processes: the injector's own line naming the URL (`MelonFusionRpgMod.cs:51`,
`"MelonMod host ready, server="`), and the slot server's own log showing the client arriving. A written cfg
proves a file was written; a running game proves a game started; neither is a connection.

Stale-evidence guard: the slot's `MelonLoader\Latest.log` is deleted before the game starts — a leftover log
contains the exact line being grepped for.

Result — **the connection is proven; the data path is not** (job `b0b83ebcd`, verbatim):

```
=== verdict ===
  slot                   1
  slotUrl                http://127.0.0.1:5101
  slotHealth             200
  slotCfg                ServerUrl=http://127.0.0.1:5101
  gamePid                55764
  injectorLine           [14:55:09.606] [FusionRpg] FusionRpg MelonMod host ready, server=http://127.0.0.1:5101
  injectorSaysSlotUrl    True
  CONNECTION PROVEN       False   <- the script's own evidence-2 pattern was wrong, not the connection
```

Evidence (1/2) is the injector's own line naming the slot server: a game launched from `slot-1` reporting
`server=http://127.0.0.1:5101`, not the owner's `:5088`. Evidence (2/2) is in the slot server's log, in a form the
first pattern did not expect (the server logs `info:` / `fail:` lines, never `api/` or `Request starting`):

```
distinct client connections: 5      request-id lines: 10      unhandled exceptions: 10
        8 SQLite Error 1: 'no such column: player_id'
        2 SQLite Error 1: 'no such column: first_clear_ref'
```

So the client reached **its own** server and the server **failed all ten of its requests**. The script now counts
those failures itself and prints a second, separate verdict (`DATA PATH HEALTHY`) so a 500-serving server can never
be read as a healthy connection again.

**That failure is a real defect, not a pool artefact**, filed as `F13` in `tasks/party-dungeon-todo.md`:
`first_clear_ref` sits in head code's `CREATE TABLE IF NOT EXISTS dungeon_domain` (`RpgStore.Domains.cs:57–65`) but
is absent from **every** table of the owner's real 546 MB database, and no migration adds it — `EnsureColumn`, the
mechanism this repo already uses for exactly this case (`RpgStore.cs:4304`; cf. `RpgStore.Actions.cs:107–118`),
is simply not called for it. A freshly built server against a real database therefore 500s on the game's own data
calls, and the owner's install would hit the same on its next server restart.

Cleanup was honest in both directions: the game was killed **path-scoped** to the slot (two PIDs from this slot
killed, two PIDs from elsewhere left alone), the slot server was stopped by its recorded PID, the slot was released,
and the owner's install was fingerprinted byte-identical before and after (`owner untouched True`).

---

## 4. PowerShell 7-only operators removed from shipped tooling

`scripts/live-slot.ps1` and `.claude/cmdc-agents/scripts/post_merge_check.py` used `??`, which Windows
PowerShell 5.1 cannot parse — `powershell -File scripts/live-slot.ps1 -Status` died with a parse dump. Both
replaced with explicit form. Verified by parsing, not by review:

```
--- 5.1.26100.9444: 0 file(s) with syntax errors
--- 7.6.6: 0 file(s) with syntax errors
```

Files checked: `live-slot.ps1`, `lane-server.ps1`, `deploy-play.ps1`, `post_merge_check.py`,
`accept-lane.ps1`, `prove-slot-connection.ps1`.

---

## 5. Worktree prune

`git worktree list` classified; 52 worktrees removed — 11 clean `agent-*` harness leftovers, 31 clean
`cmdc-review-*` checkouts, 10 clean `.kilo/worktrees/*` (branches preserved). **Left in place on purpose**:
`agent-a4497053…` and `agent-a62e66ae…` and `agent-a7caaafc…` (dirty, other work), `.kilo/worktrees/BepInEx`
(dirty, on `features/mega-merge`), `.kilo/worktrees/actor-hud-bottom-anchor-20260916` (dirty, **27 unmerged
commits**), `sapphire-scilla` (detached).

This did **not** fix the build error, and was never going to: that error is the shim/AssemblyName property in
§1.2 above.

---

## NOT proven (explicit)

- Nothing here exercises the new **Warning** path at runtime: the pooled deploy always writes a cfg value, so the
  fallback branch is proven as code in the deployed artifact, not as a log line in a live run.
- The data path: the connection is proven, the server *serving* the game's data is not (F13). Until F13 is fixed a
  live probe can connect and cannot read gameplay state back.

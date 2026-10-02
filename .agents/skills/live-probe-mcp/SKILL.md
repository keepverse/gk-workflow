---
name: live-probe-mcp
description: Use the local debug MCP to inspect, screenshot, and control a running PVZ Fusion game with scope-aware evidence and safe mutation boundaries.
---

# Live Probe MCP

Use this skill when an agent needs eyes or bounded controls in a locally running PVZ Fusion game. The
MCP is an adapter over the repository's real debug HTTP surface; it is not a second game API and it
does not prove RPG server correctness by itself.

## Start with readiness

1. Run `debug_preflight({})` before any live operation.
2. Continue only when `live.ready` is true for a lawn probe. A connected injector, an idle board, or
   a server `ok:true` response is not enough.
3. Read `debug_game_state({})` when the question is whether a match is actually running. Prefer its
   direct Board/InitBoard observation over event-log history.
4. Treat the reported checkout/deployment caveats literally. If a route is missing, confirm the
   server is running against the checkout that contains it; do not invent a replacement route.

`debug_preflight` is read-only: it does not launch, deploy, restart, or mutate the game. If it names a
fix such as starting the server or game, the operator must run that command in their own terminal.

## Live slots — three games, clone once, claim by lock, no human sequencing

Owner ruling 2026-09-21, refined 2026-09-22 after a lane's probe wrote into the owner's install. Agents **clone**
the game into a pool, **claim** a slot, and **release** it; at most **3** live runs at once; coordination is a JSON
registry guarded by a lock file; no human sequences anything.

**No install path is hardcoded anywhere.** Pool root and source install come from the environment
(`FUSIONRPG_GAME_POOL`, `FUSIONRPG_GAME_SOURCE`). Machine-specific values live in the environment or the gitignored
`.env` — never in a committed file.

```powershell
python gk-core/scripts/live_slot.py --status                                  # per slot: state, holder, install, age, live PID
python gk-core/scripts/live_slot.py --clone   --session <id>                  # populate a free slot + VERIFY it (once per slot)
python gk-core/scripts/live_slot.py --acquire --session <id>                  # claim it (clones on first use if needed)
python gk-core/scripts/live_slot.py --release --session <id>                  # hand it back: state ready, install KEPT for reuse
python gk-core/scripts/live_slot.py --reclaim --slot <n> --session <id>      # force-release a stale claim, after reading --status
```

`--json` prints a machine-readable verdict (including which value the cfg stamp wrote) and every
refusal exits non-zero with a named reason and its remedy. A refusal **never costs a slot**: an
`--acquire` that cannot make the slot safe to launch leaves the pool exactly as it found it.

**Slot states are occupancy, not the absence of an entry:** `free` (nothing cloned) → `ready` (cloned and
verified, nobody probing) → `occupied` (held by a session) → `broken` (clone incomplete or verification failed;
re-clone with `--clone --slot n --force`). `--status` also reports the **game process actually running from that
install** and flags a `STALE CLAIM` (held past the threshold with no process) — so a crashed lane is visible
instead of being trusted. Release keeps the install: the next session reuses it rather than paying the clone again.

**A clone is stamped with the slot's OWN port** (2026-09-26). A slot is cloned from the owner's install,
whose `Mods/fusionrpg.cfg` names the owner's `:5088`; measured before the fix, every cloned slot carried
`ServerUrl=http://127.0.0.1:5088` while the pool reported `5101` and the transcript said "YOUR SERVER PORT:
5101". The tool now writes the slot's own port into the clone's cfg and prints the value it replaced, on
`--clone`, on a `--force` re-clone and on `--acquire`. It **refuses by name** (`CFG-NO-SERVERURL`) rather than
inventing a key if the cfg exists but carries none; an absent cfg is reported, not created, because the
BepInEx host has none by design.

### The probe, in order

```powershell
$env:FUSIONRPG_GAME_POOL   = '<pool root>'        # or --pool-root
$env:FUSIONRPG_GAME_SOURCE = '<game install>'     # or --source-install; what gets cloned
python gk-core/scripts/live_slot.py --acquire --session <your-session-id>
# deploy INTO YOUR SLOT, env INLINE on the same command line (a prior `export` line does NOT reach this process):
$env:FUSIONRPG_GAME_POOL='<pool>'; $env:FUSIONRPG_ML_GAMEDIR='<slot path>'
python gk-fusion/scripts/deploy-play.py --no-server --server-url http://127.0.0.1:<your-port> --paths <changed files>
python gk-core/scripts/live_slot.py --release --session <your-session-id>
```

- **Never the owner's install, never `:5088`.** `deploy-play.py` now **refuses** (exit 3) when
  `FUSIONRPG_GAME_POOL` is set and the target is outside the pool. That guard exists because a lane's probe once
  fell back to the owner's install — it wrote `Mods/fusionrpg.cfg`, refreshed the injector and launched the
  owner's game (incident `SSH4.9-P1`). The fallback is why the env must be set **inline**: a variable exported in
  one command does not reach a child process started by another.
- **All three slots held is a wait**, never a kill: `--status` names the holders and their installs.

### Each slot has its OWN server and port — never the shared :5088

A slot's port is `BasePort + slot` (default `5100 + n`), **stored in the pool registry when you acquire and
derived when you have not** — both halves matter, and reading only the stored field skips every slot that has
not been claimed since the pool was created. `--status` shows the value it resolved. The owner's server stays
on **:5088** and no lane touches it. `scripts/lane-server.ps1` runs a slot's own server with its own data
directory, which is what lets two lanes probe at the same time:

```powershell
pwsh -NoProfile -File scripts/lane-server.ps1 -Start  -Slot <n>   # that slot's server, own <pool>/slot-<n>-data
pwsh -NoProfile -File scripts/lane-server.ps1 -Status             # per slot: port, pid, /health
pwsh -NoProfile -File scripts/lane-server.ps1 -Stop   -Slot <n>   # kills only the PID it recorded
```

Why a separate data directory matters as much as the port: two servers sharing one `rpg-hot.sqlite` corrupt each
other's state, so each slot gets `<pool-root>/slot-<n>-data` and the server's own `FUSIONRPG_DATA`/`FUSIONRPG_URLS`
env (`gk-core/src/FusionRpg.Server/Program.cs:14-17`) carry it. Point the game at **your** port, not 5088:

```powershell
python gk-fusion/scripts/deploy-play.py --no-server --no-rebuild-ui --server-url http://127.0.0.1:<BasePort + slot>
```

⛔ A pooled deploy that omits `-ServerUrl` is **refused** (it would inherit the owner's 5088), and `lane_server.py`
refuses any slot that resolves to 5088. If `/health` on your port is down while another lane's is up, that is your
server, not the owner's — read `<pool-root>/slot-<n>-server.log`.
- **Release is part of the probe.** A slot left `occupied` is a slot nobody else can use. If your game is still
  running, release anyway (the tool warns) and close it.
- Full protocol, including the lock and stale-break rules: `docs/contributing/live-probe-standard.md` §9.

## Killing the game is allowed by default — on the session's own install only

`debug_restart_game` (and `restart-game.ps1`) may be used without asking first, with one hard
boundary: they close **only the game running from the session's own install** (path-scoped kill;
pass `game_dir` + `base_url` + `session` for a clone setup). Killing by bare process/image name
is forbidden — it would take down the owner's game and every other session's clone. A game lock
held by another live session refuses the restart; that refusal is the backstop, not a prompt to
`debug_restart_game` (and `restart_game.py`) may be used without asking first, with one hard
boundary: they close **only the game running from the session's own install** (path-scoped kill;
pass `game_dir` + `base_url` + `session` for a clone setup). Killing by bare process/image name
is forbidden — it would take down the owner's game and every other session's clone. A game lock
held by another live session refuses the restart; that refusal is the backstop, not a prompt to
work around it. `debug_cursor` stays explicit-opt-in per call (`confirmed=true`): it moves the
real machine-wide mouse, so no install scoping can contain it.
- `debug_call` — allowlisted HTTP reads for static/server contracts; it cannot be used as arbitrary
  code execution.
- `debug_events` — budgeted event reads with cursors; never request an unbounded dump.
- `debug_match`, `debug_actor`, `debug_verify` — server-side evidence for a real match or actor.
- `debug_lawn_setup` — enters a controlled level, freezes waves, and prepares a lawn. It mutates the
  live game, so use it only when the agent owns the board and the user has asked for a lawn probe.
- `debug_menu_home` — **default menu recovery**: one call walks the real UI to the true main menu
  (pause menu → its own 主菜单 button → quit-confirm 确定), verified-only success. Proven live
  2026-09-20, operator-guided, screenshot-verified.
- `debug_ui_nav` — single-menu hops only. Its `back-to-menu` is buggy (stale layers, stale Board
  refs reported as InMatch) — do not use it for menu recovery.
- `debug_restart_game` — close/relaunch allowed by default on the session's own install only
  (path-scoped; refused on another session's locked install). Never kill by bare process name.
- `debug_game_state` — direct live Board/InitBoard state and real plant/zombie counts.
- `debug_screenshot` — captures the rendered Unity frame as a PNG; this is visual engine evidence,
  not server evidence. Save it when a later reviewer needs the artifact.
- `debug_inspect` — budgeted menu/lawn control tree with snapshot-scoped refs.
- `debug_click` — invokes one inspected ref after snapshot validation; stale refs must be refreshed,
  never guessed.
- `debug_act` — named lawn verbs such as `shovel`, with a receipt suitable for evidence.
- `debug_cursor` — moves/clicks the real mouse. It is disruptive, foreground-checked, throttled,
  and requires the tool's explicit confirmation field.
- `debug_evaluate_search`, `debug_evaluate_methods`, `debug_evaluate_call`, and
  `debug_evaluate_text` — bounded discovery and method/text inspection for controls. Use the
  returned pointers/tags and never broaden these into an arbitrary evaluator.

## Scope and evidence

Every response carries a scope label. Preserve it in notes and reports:

- `game-injector-debug`: proves what Unity reflected or rendered; it says nothing about server
  persistence or domain correctness.
- `rpg-server-debug`: real domain/persistence evidence for a real record.
- `local-machine`: process/filesystem/preflight facts.
- `null`: unclassifiable static read; do not treat it as live proof.

For an end-to-end claim, collect both halves through their normal paths: a server/domain read and a
live-engine state or screenshot. A response body alone is not proof. A screenshot answers “what did
the engine render?” and must not be parsed to grant loot, settle combat, or infer server state.

## Safe lawn-control recipe

When a user explicitly requests a controlled lawn interaction:

1. `debug_preflight` and `debug_game_state`.
2. `debug_lawn_setup` only if the board is owned and readiness is green.
3. `debug_inspect({scope: "lawn"})` and keep the returned `snapshotId`.
4. Use `debug_click` only with a ref from that snapshot; refresh after any scene/UI change.
5. Use `debug_act` for named lawn verbs when a click is not the behavior under test.
6. Capture `debug_game_state` and `debug_screenshot` after the action. Use the receipt, direct state,
   and image together.
7. Leave the game at a known state with `debug_menu_home` when the probe is finished.

Do not click from a stale snapshot, treat an expired board as live, or use the cursor as a substitute
for an inspectable ref. If setup hangs or the board ends, stop and report the exact readiness/state
failure instead of retrying destructive actions blindly.

## Setup and troubleshooting

From the repository root, install the locked adapter dependencies and run stdio mode:

```powershell
python -m pip install -r gk-fusion/tools/debug-mcp/requirements.lock
python gk-fusion/tools/debug-mcp/server.py
```

HTTP mode is for local dashboards/Inspector only and must remain localhost-bound:

```powershell
python gk-fusion/tools/debug-mcp/server.py --transport http --port 8899
```

## CLI for agents without MCP support (e.g. pi)

The same nineteen adapters are callable without MCP via
[`gk-fusion/tools/debug-mcp/cli.py`](../../../gk-fusion/tools/debug-mcp/cli.py) — one subprocess per call, JSON
envelope on stdout, exit 0 on answer (even `ok:false`), 2 on usage error, 1 on unexpected
failure. Stateless across calls except `snapshotId`/ref pairs, which still die with their
inspect snapshot:

```powershell
python gk-fusion/tools/debug-mcp/cli.py --list
python gk-fusion/tools/debug-mcp/cli.py debug_preflight
python gk-fusion/tools/debug-mcp/cli.py debug_game_state
python gk-fusion/tools/debug-mcp/cli.py debug_call --json '{"method":"GET","route":"/effects/contract"}'
python gk-fusion/tools/debug-mcp/cli.py debug_click --param snapshotId=snap1 --param ref=c0
```

Prefer one `--json` object; use repeatable `--param key=value` where shell quoting fights
back. All readiness, scope, and safe-recipe rules above apply unchanged — only the transport
differs.

For the authoritative walkthrough, route allowlist, and current tool contracts, read
[`gk-fusion/tools/debug-mcp/README.md`](../../../gk-fusion/tools/debug-mcp/README.md) and
[`docs/architecture/debug-mcp/spec-debug-mcp.md`](../../../docs/architecture/debug-mcp/spec-debug-mcp.md).

Common failures:

- `injector-not-connected`: start the game with the injector loaded, then rerun preflight.
- `live.ready:false`: follow the readiness fix; do not assume a heartbeat means a live board.
- stale-ref refusal: rerun `debug_inspect` and use the fresh snapshot/ref pair.
- missing route/allowlist refusal: the server is using a checkout without that endpoint; fix the
  server checkout/deployment rather than bypassing the adapter.
- screenshot appears dark: inspect the image and capture primitive first; do not apply a blanket
  post-process gamma filter. The injector's sRGB write handling is the default color-space path.

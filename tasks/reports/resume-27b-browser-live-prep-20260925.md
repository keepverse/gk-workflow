# Resume 27b — browser/live proof checklist (worktree-local)

**Status: PREPARED — no live proof was run in this session.** This is a read-only handoff for the
next real connected-injector run. No game, server, browser, slot, or long-lived live process was
started by this session.

## Boundary and recovery notes

- The only file edited by this session is this report. No product, test, generated-data, tuning,
  CI, session, or ledger file was changed.
- The inputs were read from this worktree only. The case-variant path `docs/DESIGN-Gate.md` is
  absent; the repository's actual binding file is `docs/DESIGN-GATE.md`, which was read in full.
- The separate `resume-15` source report and its ignored raw Playwright evidence were not opened.
  The partial browser boundary below comes only from the in-worktree handoff
  (`tasks/reports/mega-merge-program-resume-20260925.md:116-130`).
- The handoff remains **partial**: it proves a real no-live-game recovery message, but not
  active-match recovery, HUD/occupant behavior, or foreign-match isolation
  (`tasks/reports/mega-merge-program-resume-20260925.md:42-43,123-130`). Those claims stay open.

## Rules that control the next run

1. **Name the scope for every observation.** `Game Injector Debug` may fabricate or mutate engine
   state and proves only what Unity reflects. `RPG Server Debug` must operate on a real record and
   use the real application/domain/persistence path. The two passes never substitute for one
   another (`docs/contributing/live-probe-standard.md:25-37`; the corrected route classifier is in
   `docs/architecture/live-probe/spec-debug-scope-guard.md:9-48`).
2. **A response body is not persistence proof.** Record the subject before the operation, perform
   the real operation, then read the changed state through the normal frontend query path. Keep
   the server read-back separate from the live-engine read-back
   (`docs/contributing/live-probe-standard.md:41-72,161-178`).
3. **Never manufacture the subject.** Do not use a debug-created active match, a fabricated
   `UniqueActor`, a raw loadout bound directly to a pointer, `window.__fusionRpgAppendLogEvent`,
   or a SIM-only shortcut as the subject of this proof. A debug call may skip tedium, but it must
   still traverse the real flow (`docs/contributing/live-probe-standard.md:41-55,76-87`).
4. **The current lawn state is not a response-body inference.** Prefer the direct
   `debug_game_state` read for “is a real match running now”; use `GET /api/debug/lawn/state` for
   event-derived timing/context. `Unknown` is not idle, and a simulation state cannot prove what
   the screen renders (`docs/contributing/live-probe-standard.md:115-148`;
   `docs/architecture/live-probe/lawn-run-state-machine.md:7-16,87-101`).
5. **The next run must be slot-local.** Each slot owns its install, server port, and data directory.
   Never target the owner install or `:5088`; if all slots are occupied, wait. Do not kill another
   session's game to make room (`docs/contributing/live-probe-standard.md:200-237`).

## Proof claim and acceptance gates

The next report may claim the live/browser proof only when every gate below has evidence. A gate
with only an `ok:true`, one screenshot, or one response body is **not** green.

| Gate | Required evidence | Pass condition |
|---|---|---|
| G0 — head and readiness | Clean authorized integration checkout, current-head gate, tested/deployed heads, `/health`, `debug_preflight` | Current `GREEN` head is the tested head; slot URL is healthy; injector is connected; readiness is rechecked after a real board exists. |
| G1 — slot/server isolation | Before/after slot status, own server status/log, own install/config, owner fingerprint | The game is launched from the acquired slot; the server is on the slot port and data directory; no owner install, owner data, or `:5088` listener is touched. |
| G2 — real match A | Actual UI entry, `board.start`/snapshot/event ids, direct game-state, screenshot | Match A was entered through the game flow, has a real `matchKey`, and direct Unity state agrees with an active board. No debug setup route is the source of the claim. |
| G3 — normal-path read-back | Pre-state, real operation, normal GET, slot DB/log evidence | The record/run changed through the real service and is read back through the same normal query path the frontend uses. The mutation response is not the read-back. |
| G4 — browser recovery | Cold/entry baseline, reload/reconnect snapshots, ready/stale/empty HUD state | Browser A recovers to the same match scope from the authoritative snapshot and shows the real HUD/occupants; stale data is not silently promoted to ready. |
| G5 — cross-match isolation | Real match B event, B identity, A browser snapshot before/after | While A is still in scope, B cannot change A's match key, recovery state, HUD, or occupant set. Sequential B after A's terminal event is a separate next-scope test, not a substitute. |
| G6 — cleanup | Browser close, path-scoped game stop, slot-server stop, slot release, final status/port check | No browser, slot game, slot server, or slot claim leaks; owner fingerprint and `:5088` are unchanged. Cleanup errors fail the run. |
| G7 — durable evidence | Evidence manifest and SHA-256 hashes | Every retained artifact is named, hashed, and tied to the tested/deployed head; ignored raw files are archived or explicitly reported as external. |

## Exact prerequisites

The following are prerequisites for the **authorized integration run**, not commands to execute in
this report-only session.

1. **Use the right checkout.** Run only from a clean checkout on `features/mega-merge` (or the
   owner-authorized equivalent) after the current-head merged-head gate is `GREEN`. The current
   recovery branch is not itself a live-proof environment. Do not reuse the stale merged-head
   report named by the handoff; the terminal gate, exact head, and evidence-only descendants must
   be current (`tasks/reports/mega-merge-program-resume-20260925.md:293-321`).
2. **Pin the tested head.** Before any live command, record `git rev-parse HEAD`, the branch, and a
   clean `git status --porcelain`. Immediately before the live boundary, run the full aggregate
   required by the handoff and retain its log. This is the one intentional broad verification
   boundary immediately before a live probe (`tasks/reports/mega-merge-program-resume-20260925.md:375-392`).
3. **Prepare the web/server inputs.** The worktree needs its locked Node dependencies and a
   production web build. A successful server health check is insufficient: confirm the served root
   is `200`, not a `404` caused by missing `wwwroot`/`node_modules`.
4. **Supply runtime-only environment values.** `FUSIONRPG_GAME_POOL` and
   `FUSIONRPG_GAME_SOURCE` must come from the runner's environment or explicit runtime parameters.
   For the MelonLoader host, set `FUSIONRPG_GAME_PROFILE=pvzrh-3.9`. Never put a drive letter,
   game path, or pool path in this tracked report. Set `FUSIONRPG_ML_GAMEDIR` to the acquired slot
   on the same command line that deploys into that slot; a prior export in another process is not
   sufficient (`scripts/live-slot.ps1:34-50`; `scripts/deploy-play.ps1:157-218`).
5. **Claim, do not collide.** Run `live-slot.ps1 -Status`, acquire one free slot, then run
   `-Status` again. Read the slot number, port, and install from the pool registry, not from a
   copied log line. All slots held is a wait. Never use `-Force` over an occupied slot or a process
   whose ownership has not been checked.
6. **Use the slot server and data.** `lane-server.ps1 -Start -Slot <n>` uses the slot's own port
   and `<pool-root>/slot-<n>-data`; it refuses the owner port. Set the browser and every debug
   adapter's `FUSIONRPG_SERVER_URL` to that slot URL. Leaving it unset makes the CLI default to
   `127.0.0.1:5088` (`scripts/lane-server.ps1:1-18,64-149`; `gk-fusion/tools/debug-mcp/cli.py:7-11`).
7. **Publish before measuring a binary.** Do not start a slot server before the first deploy if
   the proof is meant to measure the current server: `deploy-play.ps1` skips `dotnet publish` when
   its health URL already answers. A safe shape is a first `-NoServer -NoGame` publish into the
   slot, then start the slot server, then a second `-NoServer` deploy to write the slot config and
   launch the game. This ordering prevents a stale `dist` from being mistaken for current code
   (`scripts/deploy-play.ps1:365-410`; the stale-binary failure is documented in
   `scripts/prove-slot-connection.ps1:115-130`).
8. **Keep the game lock scoped.** When the deploy launches the game, pass the active session id so
   `game-lock.ps1` can refuse another live session's install. A process kill is path-scoped and
   only ever targets the acquired slot (`scripts/deploy-play.ps1:224-235`;
   `scripts/restart-game.ps1:84-107`).

## Command sequence shape

The placeholders below are deliberately runtime values. The runner must replace them and record
the resolved values in the evidence bundle, not this tracked checklist.

### 1. Clean head and aggregate

```powershell
$session = '<active-session-id>'
$testedHead = (git rev-parse HEAD).Trim()
$branch = (git branch --show-current).Trim()
$status = @(git status --porcelain=v1 --untracked-files=all)
if ($branch -ne 'features/mega-merge') { throw "live proof must run on features/mega-merge, got $branch" }
if ($status.Count -gt 0) { throw 'live proof started from a dirty checkout' }

$fullLog = Join-Path $env:TEMP ('fusionrpg-full-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
pwsh -NoProfile -File .\scripts\test-fast.ps1 -AllDefault 2>&1 | Tee-Object -FilePath $fullLog
if ($LASTEXITCODE -ne 0) { throw "full aggregate exited $LASTEXITCODE" }
if ((git rev-parse HEAD).Trim() -ne $testedHead) { throw 'full test changed HEAD' }
Get-FileHash -Algorithm SHA256 -LiteralPath $fullLog
```

The full-suite exception is intentional here: this is the handoff's immediate pre-live boundary,
not an ordinary edit. The exact output and hash belong in the future live report.

### 2. Acquire the slot and derive its endpoint

```powershell
$env:FUSIONRPG_GAME_POOL = '<runtime pool root>'
$env:FUSIONRPG_GAME_SOURCE = '<runtime source install>'

.\scripts\live-slot.ps1 -Status
.\scripts\live-slot.ps1 -Acquire -Session $session
.\scripts\live-slot.ps1 -Status

$registryPath = Join-Path $env:FUSIONRPG_GAME_POOL 'slots.json'
$entry = @((Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json).slots |
  Where-Object { $_.session -eq $session -and $_.state -eq 'occupied' })
if ($entry.Count -ne 1) { throw 'slot registry did not name exactly one occupied slot for this session' }
$slot = [int]$entry[0].slot
$slotPort = if ($entry[0].PSObject.Properties['port'] -and $entry[0].port) { [int]$entry[0].port } else { 5100 + $slot }
$slotInstall = (Resolve-Path -LiteralPath $entry[0].installPath).Path
$serverUrl = "http://127.0.0.1:$slotPort"
if ($slotPort -eq 5088) { throw 'slot resolved to the owner port' }
$poolRoot = (Resolve-Path -LiteralPath $env:FUSIONRPG_GAME_POOL).Path.TrimEnd('\','/')
$slotPrefix = $poolRoot + [IO.Path]::DirectorySeparatorChar
if (-not $slotInstall.StartsWith($slotPrefix, [StringComparison]::OrdinalIgnoreCase)) {
  throw 'slot install is outside the configured pool'
}
```

Capture the slot status output before and after the run. Do not copy a machine-local install path
into a tracked report.

### 3. Publish, start the slot server, and launch only the slot game

Use the first deploy while the slot port is still free, then start the server, then use the second
deploy to configure and launch the game. Keep the environment assignments in the same PowerShell
process as the deploy.

```powershell
$env:FUSIONRPG_ML_GAMEDIR = $slotInstall
$env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'

# Fresh server publish for this head; the injector target is the acquired slot.
# No game and no server are launched by this pass.
.\scripts\deploy-play.ps1 -LoaderHost MelonLoader -NoServer -NoGame -NoRebuildUi `
  -ServerUrl $serverUrl -Session $session

# Start only this slot's server; it creates/uses slot-<n>-data and records its own PID.
.\scripts\lane-server.ps1 -Start -Slot $slot
.\scripts\lane-server.ps1 -Status

# Build/refresh the injector, write the slot config, and launch the game from the slot install.
.\scripts\deploy-play.ps1 -LoaderHost MelonLoader -NoServer -NoRebuildUi `
  -ServerUrl $serverUrl -Session $session

$deadline = (Get-Date).AddSeconds(180)
do {
  try { $health = Invoke-RestMethod -Uri "$serverUrl/health" -TimeoutSec 3 } catch { $health = $null }
  if ($health -and $health.ok -and $health.injectorConnected) { break }
  Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)
if (-not ($health -and $health.ok -and $health.injectorConnected)) {
  throw 'slot injector did not become healthy'
}
```

Retain the server's `.log` and `.err` files, the slot `fusionrpg.cfg`, and the injector's
`MelonLoader/Latest.log`. The config hash and the injector's `MelonMod host ready, server=...`
line are connection witnesses, not substitutes for the gates below.

### 4. Preflight and real active-match entry (Match A)

Set the adapter URL for every subsequent command. A missing or unset value silently targets the
owner server and is a hard failure.

```powershell
$env:FUSIONRPG_SERVER_URL = $serverUrl
python gk-fusion/tools/debug-mcp/cli.py debug_preflight --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_game_state --pretty
```

At this point an idle board is allowed. `debug_preflight.live.ready` is not a substitute for a
real match: its own implementation cross-checks the tracked snapshot against `/game-state`, and
an injector heartbeat alone is not readiness (`gk-fusion/tools/debug-mcp/tools/debug_preflight.py:314-417`).

Enter **Match A through the real game UI**: main menu → Adventure/day selection → level 1 →
seed-picker dismissal → actual board start. If recovery is needed, use the real UI recovery path
and a fresh inspect snapshot; `debug_menu_home` is the default recovery adapter, while
`debug_ui_nav`'s `back-to-menu` shortcut is not a valid recovery proof
(`gk-fusion/tools/debug-mcp/tools/debug_menu_home.py:48-130`; `gk-fusion/tools/debug-mcp/README.md:67-89`).

The following debug controls may drive/inspect the real UI, but their scope is **Game Injector
Debug** and their receipts are not server-persistence proof:

```powershell
python gk-fusion/tools/debug-mcp/cli.py debug_inspect --json '{"scope":"menu","limit":50}' --pretty
# Use only a fresh snapshotId/ref returned by the immediately preceding inspect.
python gk-fusion/tools/debug-mcp/cli.py debug_click --json '{"snapshotId":"<fresh-id>","ref":"<fresh-ref>"}' --pretty
```

Do not use `/lawn/quick-start`, `/scenario/*`, `/enter-level`, `/spawn-*`, `debug.lawn_setup`, or a
raw pointer binding to create the match used for G2. Those routes can be Game Injector Debug and
may fabricate or orchestrate engine state. If one is used to recover a board, restart/enter through
the real UI before collecting the acceptance evidence.

After the real board starts, collect all of the following. Record A's `matchKey`, event ids,
snapshot id, direct entity counts, and phase; do not substitute a fixed population count.

```powershell
python gk-fusion/tools/debug-mcp/cli.py debug_preflight --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_game_state --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_events --json '{"kind":"board.start","limit":50}' --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_events --json '{"kind":"debug.snapshot","limit":5}' --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_match --json '{"match_key":"<A-match-key>","entity_limit":50}' --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_call --json '{"method":"GET","route":"/lawn/state"}' --pretty
python gk-fusion/tools/debug-mcp/cli.py debug_screenshot --json '{"tag":"match-A","save_to":"<evidence-root>/match-A.png"}' --pretty
```

Pass conditions:

- `debug_game_state` reports a real active board (`liveState=InMatch`, real plant/zombie counts,
  and no unresolved phase mismatch). `/lawn/state` is retained as timing/context, not as a
  replacement for this direct read.
- A's `board.start` or authoritative snapshot is present with a real key. `debug_match` returns a
  bounded digest for that same key; the response alone is not the claim.
- The screenshot is engine evidence only. It cannot establish a DB write, server correctness, or
  an award (`gk-fusion/tools/debug-mcp/tools/debug_screenshot.py:53-73`).
- `debug_preflight`, `debug_game_state`, `debug_match`, and `/lawn/state` are labelled and filed
  under their actual scopes; no Game Injector Debug result is used as an RPG Server Debug result.

### 5. Normal-path persistence read-back

Before the operation under test, capture the subject through the normal frontend path. For a live
lawn run, the useful baseline is the run/event identity; for a feature mutation, it is the real
actor/deployment row and its current revision. Then perform the real player-facing operation and
read it back through the same normal query path. A representative run-level read-back is:

```powershell
$beforeRuns = Invoke-RestMethod -Uri "$serverUrl/api/runs" -TimeoutSec 10
# Perform the selected real operation through the normal UI/endpoint; save its request and response.
$afterRuns = Invoke-RestMethod -Uri "$serverUrl/api/runs" -TimeoutSec 10
$afterRuns | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath '<evidence-root>/runs-readback.json'
```

For a real `UniqueActor` operation, use the normal `GET /api/unique/actors/<instanceId>` path after
the real mutation, not `debug_actor` as the only read. `GET /api/runs` is a normal server query
(`gk-core/src/FusionRpg.Server/Program.cs:1775-1779`) and its rows carry `matchKey`/`runId`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:3307-3362`). `board.start` is persisted by the normal
event-ingest path (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:2982-3090`), but the runner must still
read the resulting row/event back after ingest. If the selected operation is read-only, label the
result “hydration/read-only” and do not call it a mutation/persistence proof.

Required read-back fields are: subject id/match key, pre-state, operation route and correlation,
post-state, event/snapshot id, normal GET route, and the slot data/log that received it. A response
from the mutation call, a debug-only accessor, or a database query made outside `FusionRpg.Data`
does not satisfy this gate.

### 6. Browser entry, recovery, and HUD/occupant proof

The following commands are for the future runner. They are deliberately not run in this session.
Use the slot URL, not `:5088`.

```powershell
playwright-cli open "$serverUrl/#/lawn"
playwright-cli snapshot --filename="<evidence-root>/browser-00-entry.yaml"
playwright-cli screenshot --filename="<evidence-root>/browser-00-entry.png"
playwright-cli console
playwright-cli requests
```

First retain the no-active-match baseline: the page must show the real no-active-match recovery
message (or a truthful loading/stale state) and must not display a fabricated A. The earlier
no-live-game result is context only; it is not current active-match evidence.

After Match A is real and its identity is recorded, reload the same browser page to exercise the
actual cold/reconnect edge:

```powershell
playwright-cli reload
playwright-cli snapshot --filename="<evidence-root>/browser-01-reconnect-loading.yaml"
playwright-cli --raw eval 'JSON.stringify({
  hud: !!document.querySelector("[data-testid=lawn-match-hud]"),
  phase: document.querySelector("[data-testid=lawn-hud-phase]")?.textContent ?? null,
  empty: document.querySelector("[data-testid=lawn-recovery-empty]")?.textContent ?? null,
  stale: document.querySelector("[data-testid=lawn-recovery-stale]")?.textContent ?? null,
  loading: document.querySelector("[data-testid=lawn-recovery-loading]")?.textContent ?? null
})'
playwright-cli snapshot --filename="<evidence-root>/browser-02-authoritative-ready.yaml"
playwright-cli screenshot --filename="<evidence-root>/browser-02-authoritative-ready.png"
```

Poll or retry the snapshot/evaluation until the server's real snapshot arrives; do not use a fixed
sleep as proof. The pass condition is:

- the page passes through a truthful loading/stale edge (if the reconnect is observed) and then
  shows the real A HUD/board state;
- the recovered `matchKey` is A, the snapshot is fresh, and the page does not show
  `lawn-recovery-empty` while direct game-state says A is active;
- visible occupants/HUD data agree with A's authoritative snapshot. Record the observed set; do
  not pin a literal population count.

This follows the implemented recovery path: `RpgHub.Join("web")` requests the existing
`debug.snapshot`, `EventIngest` broadcasts `LawnRecovery ready` with the snapshot identity, and the
web store rejects a recovery status for a different match key
(`gk-core/src/FusionRpg.Server/RpgHub.cs:32-60`; `gk-core/src/FusionRpg.Server/EventIngest.cs:54-76,155-168,254-263`;
`gk-web/web/fusion-rpg-web/src/lib/bus/log-store.ts:249-318`).

### 7. Real Match B and cross-match isolation (G5)

Do not manufacture B in the browser. Start B through a real player-facing match flow that emits
onto the same authoritative server event stream. A second tab may be used for a real non-lawn
player flow, but if the claim is specifically PvZ match-key isolation, B must be a real PvZ
match/event of the kind under test. Record B's real `matchKey`, event ids, and request path.

```powershell
playwright-cli tab-new "$serverUrl/#/<real-second-match-route>"
playwright-cli snapshot --filename="<evidence-root>/browser-03-match-B-entry.yaml"
# Use only fresh refs from this snapshot to start B through the real player-facing flow.
playwright-cli tab-select 0
playwright-cli snapshot --filename="<evidence-root>/browser-04-A-after-B.yaml"
playwright-cli --raw eval 'JSON.stringify({
  hud: document.querySelector("[data-testid=lawn-match-hud]")?.textContent ?? null,
  phase: document.querySelector("[data-testid=lawn-hud-phase]")?.textContent ?? null,
  empty: document.querySelector("[data-testid=lawn-recovery-empty]")?.textContent ?? null
})'
```

The A tab must retain A's match key, recovery state, HUD, and occupant identities while B's real
events are present. A foreign B snapshot/status must not clear A or retarget the lawn. A second
match started only after A's authoritative terminal snapshot tests the next-scope transition and
does **not** satisfy G5. A web-mode event that is intentionally filtered as non-capture proves
only that narrower filter; it must not be relabeled as PvZ match-key proof.

Forbidden substitutes for B are `window.__fusionRpgAppendLogEvent`, a hand-built event POST used
only to move the browser, the SIM-only `/api/test/web-match` route, a debug-created board, or a
foreign event from a different slot/server that never reaches this browser's stream. If the
product cannot produce B while A remains in scope, record **BLOCKED: no real same-stream second
match** and do not claim G5.

## Scope ledger for the future report

| Observation/operation | Scope to record | What it can prove | What it cannot prove |
|---|---|---|---|
| `debug_preflight`, `debug_game_state`, `debug_screenshot`, `debug_inspect/click`, `debug_menu_home` | `game-injector-debug` (preflight may also report local/server facts) | Connected game, current Unity board, rendered frame, real UI action/recovery | Server persistence, domain correctness, or a web match's state |
| `debug_match`, `debug_events`, `/lawn/state` | `rpg-server-debug` | Bounded event/match context and lifecycle/timing context | What Unity currently renders; it is not the direct active-board read or a substitute for a normal persistence query |
| Normal `GET /api/runs`, `GET /api/unique/actors/<id>`, and the selected frontend query | normal RPG server read path | The persisted state visible to the frontend | Engine application of that state |
| Browser DOM/snapshot/screenshot | browser observation | What the browser rendered and whether its recovery/HUD state changed | Server persistence by itself; it must be paired with the normal read-back |

A future report must include one row per actual call, its scope, the route/tool, the result, and
which claim it supports. Missing halves stay explicitly missing.

## Cleanup contract

Put acquisition inside one `try/finally` boundary. Browser goes first; then only the acquired
slot's game, then that slot's recorded server, then the slot release. A cleanup failure is a
failed probe, not a swallowed exception.

```powershell
$slotAcquired = $false
$slot = $null
$slotPort = $null
$slotInstall = $null
$cleanupErrors = @()

try {
  # Sections 2–7, including -Acquire; set $slotAcquired = $true immediately after acquisition succeeds.
  # slot acquisition, deploy, Match A/B, browser recovery, and evidence capture
}
finally {
  try { playwright-cli close } catch { $cleanupErrors += "browser close: $($_.Exception.Message)" }

  if ($slotInstall) {
    try {
      $prefix = [IO.Path]::GetFullPath($slotInstall).TrimEnd('\','/') + '\'
      Get-Process -Name 'PlantsVsZombiesRH' -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) } |
        Stop-Process -Force
    } catch { $cleanupErrors += "game cleanup: $($_.Exception.Message)" }
  }
  if ($slot) { try { .\scripts\lane-server.ps1 -Stop -Slot $slot } catch { $cleanupErrors += "server stop: $($_.Exception.Message)" } }
  if ($slotAcquired) { try { .\scripts\live-slot.ps1 -Release -Session $session } catch { $cleanupErrors += "slot release: $($_.Exception.Message)" } }
  .\scripts\live-slot.ps1 -Status
  if ($slotPort -and @(Get-NetTCPConnection -LocalPort $slotPort -State Listen -ErrorAction SilentlyContinue).Count -gt 0) {
    $cleanupErrors += "slot port $slotPort still has a listener"
  }
  if ($cleanupErrors.Count -gt 0) { throw ($cleanupErrors -join '; ') }
}
```

Do not use a bare image-name kill. `debug_restart_game` is a recovery operation, not final
cleanup; if used, pass `game_dir`, the slot `base_url`, and `session` so it can only touch the
acquired install (`gk-fusion/tools/debug-mcp/tools/debug_restart_game.py:48-100`). Record final slot state,
port state, game-process state, browser state, and owner fingerprint in the cleanup evidence.

## Evidence files to retain

The future runner should create an external, timestamped evidence root and copy or tee outputs
there. Machine-local absolute values belong in that bundle's runtime metadata, not in tracked
Markdown.

- **Tracked summary:** `tasks/reports/mega-merge-live-browser-current-20260925.md` (only after
  the manager session fence includes that path). Keep its verdict separate from the raw evidence.
- **Head/readiness:** branch/head/status transcript, current-head gate transcript, full-test log,
  `/health` response, `debug_preflight` before and after real entry.
- **Slot/server:** `live-slot -Status` before/acquired/after, `lane-server -Status`, slot registry
  copy, slot config copy, slot server `.log`/`.err`, and owner-install/`:5088` fingerprint before
  and after. Do not commit the mutable registry or a machine-local install path.
- **Match A:** bounded `board.start` and `debug.snapshot` event pages, `debug_match` digest,
  direct `debug_game_state`, `/lawn/state`, normal `/api/runs` (and selected actor/deployment
  normal read-back), plus the engine screenshot.
- **Browser:** entry/no-active baseline, reconnect/loading/stale snapshot, authoritative-ready
  snapshot, HUD/occupant screenshot, Match B evidence, console output, and request list. Preserve
  the raw `.playwright-cli` files or an explicit external archive; a hash alone does not preserve
  ignored raw evidence (`tasks/reports/mega-merge-program-resume-20260925.md:123-130,269-280`).
- **Hashes:** SHA-256 for every retained JSON/YAML/PNG/log/transcript and the final tracked report
  in a separate manifest. Do not put the report's own final hash inside the report.

A portable hash-manifest shape is:

```powershell
$manifest = Get-ChildItem -LiteralPath $evidenceRoot -File -Recurse |
  Sort-Object FullName | ForEach-Object {
    [pscustomobject]@{
      path = [IO.Path]::GetRelativePath($evidenceRoot, $_.FullName).Replace('\','/')
      sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
    }
  }
$manifestPath = Join-Path $evidenceRoot 'sha256-manifest.json'
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Get-FileHash -Algorithm SHA256 -LiteralPath $manifestPath
```

Record the manifest hash in the external transcript. Do not place a self-referential report hash
inside the report being hashed.

## Conditions that remain blocked without a real injector/live game

The following are honest `BLOCKED` outcomes, not reasons to fabricate a pass:

- No authorized clean `features/mega-merge` checkout, current-head `GREEN` gate, or matching
  tested/deployed head: G0–G7 are blocked.
- No runtime pool/source values, no free slot, or no legal MelonLoader 3.9 game install: G1 and
  all live/browser gates are blocked.
- Slot server unavailable, port resolving to `5088`, data directory shared, or a deploy guard
  refuses the target: stop before launch and record the exact refusal.
- `/health` is green but `injectorConnected=false`, `debug_preflight.live.ready=false`, or
  `debug_game_state` shows no real `Board`/entities: no active-match claim is allowed.
- `debug.snapshot`, `/game-state`, or `/lawn/state` is missing from the server checkout: fix the
  deployment; do not invent a replacement route or use a stale response.
- The subject is synthetic, the operation was a debug shortcut, or the changed row cannot be read
  through the normal frontend path: persistence proof is blocked.
- Only a response body, a screenshot, a browser snapshot, or a same-tool telemetry read-back is
  available: the corresponding other half is not proven.
- Match B is synthetic, SIM-only, from another slot/server, or only starts after A's terminal
  snapshot: cross-match isolation remains blocked/partial; do not relabel sequential transition as
  isolation.
- Any cleanup error, owner fingerprint change, `:5088` listener change, or slot claim left occupied:
  the probe fails and cannot be used as evidence.
- The ignored `resume-15` raw browser artifacts remain unavailable: the handoff's partial result
  is context only, not a substitute for a current retained bundle.

## Preparation verification performed in this session

These checks validate only the report edit. They are not live/game/browser evidence.

- `git diff --check` — exit 0; no output.
- `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks` — exit 0; the exact
  terminal summary was `**TOTAL open=671 done=2885 boxes=1884 (not a work count) shaded=843 · unmeasured=2 file(s)**`.

The next runner must append the exact outputs, exit results, and hashes from the real connected
run; this report intentionally contains no fabricated match, response, or live verdict.

<<<REPORT {"status":"partial","summary":"Prepared the worktree-local browser/live proof checklist. No game, server, browser, slot, or long-lived live process was started; active-match recovery, normal-path persistence read-back, and cross-match isolation remain explicitly blocked until a real connected-injector run supplies the evidence.","changed_files":["tasks/reports/resume-27b-browser-live-prep-20260925.md"],"verification":[{"command":"git diff --check","result":"exit 0; no output"},{"command":"python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks","result":"exit 0; **TOTAL open=671 done=2885 boxes=1884 (not a work count) shaded=843 · unmeasured=2 file(s)**"}],"open_issues":["The case-variant docs/DESIGN-Gate.md is absent; docs/DESIGN-GATE.md was read instead.","No real connected injector, active match, browser session, or same-stream second match exists in this worktree.","The resume-15 partial browser result is not current active-match or cross-match evidence."]} REPORT>>>

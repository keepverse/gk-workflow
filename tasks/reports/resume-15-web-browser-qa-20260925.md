# Fresh bounded browser QA — accepted web recovery

- **Worktree:** `.claude/worktrees/opencode-resume-15-web-browser-qa-20260925` (repo-relative reference; the source worktree retains the ignored evidence)
- **Date:** 2026-09-25
- **Scope:** web build, local server boot, HTTP/SPA proof, bounded Playwright review, and cleanup only.
- **Result:** **PARTIAL** — the local server and SPA were proved, and the real no-live-game recovery state was captured. Cross-match isolation and an active-match recovery transition were not browser-proven because no injector/live game was connected; no debug data was used to manufacture one.

## Commands and results

### Web build

Working directory: `gk-web/web/fusion-rpg-web`

```powershell
npm ci
```

Result: exit 0; 433 packages added and 434 audited. npm reported the existing dependency warnings and 6 vulnerabilities (4 moderate, 2 high). No audit fix was run.

```powershell
npm run build
```

Result: exit 0. `tsc --noEmit` and Vite completed in 16.88 s and wrote the production bundle to `src/FusionRpg.Server/wwwroot/`. Non-fatal output included SignalR `/*#__PURE__*/` annotation warnings, the existing `CacheClaimPrompt` dynamic/static-import warning, and large-chunk warnings.

### Port and server lifecycle

The required pre-start check was run before starting the server:

```powershell
Get-NetTCPConnection -LocalPort 5088 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Get-Process -Id $_.OwningProcess | Select-Object Id, ProcessName, StartTime, Path }
```

Observed result: no listener output. The prescribed `src/FusionRpg.Server/data` path did not exist in this worktree, so the first launch attempt emitted a `Resolve-Path` error; it returned PID `36536`, which exited before binding and had no child/listener left behind. No process was killed by name.

The existing built server data directory was used instead, with the local-web-review detached launch shape:

```powershell
$dataDir = (Resolve-Path ".\src\FusionRpg.Server\bin\Debug\net8.0\data").Path; $tag = Get-Date -Format "yyyyMMdd-HHmmss"; $stdout = Join-Path $dataDir "qa-server-$tag.stdout.log"; $stderr = Join-Path $dataDir "qa-server-$tag.stderr.log"; $env:FUSIONRPG_DATA = $dataDir; $server = Start-Process -FilePath "dotnet" -ArgumentList "run" -WorkingDirectory (Resolve-Path ".\src\FusionRpg.Server").Path -WindowStyle Hidden -Environment @{ "FUSIONRPG_DATA" = $env:FUSIONRPG_DATA } -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
```

Result: detached launcher PID `23608`; its child server was `FusionRpg.Server.exe` PID `47304`. The server log records the selected data directory, `Now listening on: http://127.0.0.1:5088`, and the worktree content root. Evidence: `.playwright-cli/qa-server-lifecycle.json` and `.playwright-cli/qa-server-stdout.log`.

The bounded health poll was:

```powershell
$deadline = (Get-Date).AddSeconds(60); $sw = [Diagnostics.Stopwatch]::StartNew(); $last = $null; while ((Get-Date) -lt $deadline) { try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:5088/health" -UseBasicParsing -TimeoutSec 3; $last = [pscustomobject]@{ StatusCode = [int]$r.StatusCode; Content = $r.Content; ContentType = $r.Headers["Content-Type"]; ElapsedSeconds = [math]::Round($sw.Elapsed.TotalSeconds, 2) }; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { $last | Format-List; exit 0 } } catch { $last = $_.Exception.Message }; Start-Sleep -Seconds 1 }; [pscustomobject]@{ Result = "TIMEOUT_OR_UNHEALTHY"; ElapsedSeconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); Last = $last } | Format-List; exit 1
```

Result: HTTP `200` after `15.94 s` (inside the 60-second bound), with `ok:true`, `injectorConnected:false`, `source:"none"`, and no content-import error.

### HTTP and built-index proof

A real HTTP client check was run against both `/health` and `/`; it compared the response bytes with `src/FusionRpg.Server/wwwroot/index.html` and saved the result to `.playwright-cli/qa-http.json`.

- `GET http://127.0.0.1:5088/` → `200`, `text/html`, 403 bytes.
- The response was an exact byte-for-byte match for the built `index.html`.
- Both SHA-256 values: `F480E95902073235BC322EAE63CC40AAF9BB9E549730B9D3EF5E68BE0E4FB0CE`.
- The HTML contains the real React root (`<div id="root"></div>`).

## Browser evidence

All `playwright-cli` calls were bounded with a 30-second shell timeout.

### Sanctum entry

```powershell
playwright-cli open "http://127.0.0.1:5088/#/sanctum"
```

The browser opened as PID `43500`, URL `http://127.0.0.1:5088/#/sanctum`, title `Rise of Summoner`. The initial snapshot and screenshot are:

- `.playwright-cli/qa-sanctum-initial.yaml`
- `.playwright-cli/qa-sanctum-initial.png`

The snapshot showed the real Garden Keeper Sanctum, rank `0`, the locked navigation entries, the first-lawn prompt, and the real four-beat Rift prologue dialog (`Beat 1 of 4`). The first console pass contained one non-fatal request failure: `GET /favicon.ico` returned `404`; that original log is preserved at `.playwright-cli/qa-console-initial.log`.

### Lawn route and observed recovery state

The relevant route was opened with:

```powershell
playwright-cli goto "http://127.0.0.1:5088/#/lawn"
```

A reload after the first-open write was observed to return to `#/sanctum`; that landing behavior is recorded in `.playwright-cli/qa-lawn-reloaded.yaml`. Within the already-mounted app, the normal hash navigation command was then used (not a debug data injection):

```powershell
playwright-cli eval "location.hash = '#/lawn'"
```

Final browser evidence:

- `.playwright-cli/qa-lawn-no-active.yaml`
- `.playwright-cli/qa-lawn-after-hash-navigation.yaml`
- `.playwright-cli/qa-lawn-no-active.png`
- `.playwright-cli/qa-lawn-dom.json`

The real UI observed at `http://127.0.0.1:5088/#/lawn` was:

- phase `Idle` in the snapshot;
- connection text `Disconnected`;
- deployed units: `none yet`;
- authoritative recovery alert: **“No live game is available to provide an authoritative lawn snapshot.”**

This matches the real server health state (`injectorConnected:false`, `source:"none"`). The SignalR browser transport itself logged a successful WebSocket connection, while the recovery UI remained in the no-live-game error state; no active match or match key was displayed. The final captured console file `.playwright-cli/qa-console.txt` reports `Errors: 0, Warnings: 0` and records the WebSocket connection. The final request capture `.playwright-cli/qa-requests.txt` shows HTTP `200` for the displayed API, health, onboarding, and hub-negotiate requests; no API failure was observed. The initial favicon `404` remains the only console/network failure captured during the run.

## What was proven and not proven

**Proven**

1. `npm ci` and the full TypeScript/Vite production build pass.
2. Port `5088` was free before launch.
3. The detached worktree server started with the selected worktree data directory and became healthy within 60 seconds.
4. `GET /` served a real `index.html`, byte-identical to the built file.
5. The real SPA booted in a visible browser at Sanctum and Lawn routes.
6. The browser captured the actual no-live-game recovery state, with no active match shown and no fabricated events/debug data used.

**Not proven**

- A real stale → authoritative-ready recovery transition.
- Foreign-match event isolation or a second match key being rejected while the first remains in scope.
- Active-match HUD/occupant behavior.

Those require a real connected injector/live game or a normal non-debug active match. They were intentionally not simulated because the brief forbids fabricating an active match or using debug-only data as browser proof.

## Cleanup

- `playwright-cli close` → browser `default` closed.
- `playwright-cli list` → `(no browsers)`.
- Explicit cleanup command stopped only the processes started for this run: `Stop-Process -Id 47304 -Force; Stop-Process -Id 23608 -Force`.
- `.playwright-cli/qa-cleanup.json` records both PIDs absent and no listener on `5088`.
- No product, test, CI, generated-data, tuning, or hook files were edited. The only non-ignored file intended for the orchestrator is this report; browser/server evidence is under ignored `.playwright-cli/` and the worktree server build data directory.

## Next steps

1. Repeat the Lawn proof with a real connected injector/live game to observe `stale → ready` and authoritative occupant data.
2. With a real active match, drive a second real match and verify the browser keeps the original match scope; do not use `window.__fusionRpgAppendLogEvent` or debug endpoints as proof.
3. Decide separately whether the missing `favicon.ico` and the observed first-open deep-link landing redirect are intended behavior.

<<<REPORT {"status":"partial","summary":"Web build, worktree server, HTTP index proof, and bounded browser QA completed. Browser showed the real no-live-game recovery state, but active-match and cross-match isolation behavior could not be proven without a connected injector/live game; no debug data was used.","changed_files":["tasks/reports/resume-15-web-browser-qa-20260925.md"],"verification":[{"command":"npm ci","result":"PASS; exit 0, 433 packages added, 434 audited; npm reported 6 vulnerabilities (4 moderate, 2 high)."},{"command":"npm run build","result":"PASS; tsc --noEmit and Vite production build completed in 16.88s."},{"command":"Get-NetTCPConnection -LocalPort 5088 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Get-Process -Id $_.OwningProcess | Select-Object Id, ProcessName, StartTime, Path }","result":"PASS before launch; no listener output."},{"command":"$deadline = (Get-Date).AddSeconds(60); $sw = [Diagnostics.Stopwatch]::StartNew(); $last = $null; while ((Get-Date) -lt $deadline) { try { $r = Invoke-WebRequest -Uri \"http://127.0.0.1:5088/health\" -UseBasicParsing -TimeoutSec 3; $last = [pscustomobject]@{ StatusCode = [int]$r.StatusCode; Content = $r.Content; ContentType = $r.Headers[\"Content-Type\"]; ElapsedSeconds = [math]::Round($sw.Elapsed.TotalSeconds, 2) }; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { $last | Format-List; exit 0 } } catch { $last = $_.Exception.Message }; Start-Sleep -Seconds 1 }; [pscustomobject]@{ Result = \"TIMEOUT_OR_UNHEALTHY\"; ElapsedSeconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); Last = $last } | Format-List; exit 1","result":"PASS; /health returned 200 after 15.94s, inside the 60s bound."},{"command":"$client = [System.Net.Http.HttpClient]::new(); try { $health = $client.GetAsync(\"http://127.0.0.1:5088/health\").GetAwaiter().GetResult(); $healthBody = $health.Content.ReadAsStringAsync().GetAwaiter().GetResult(); $root = $client.GetAsync(\"http://127.0.0.1:5088/\").GetAwaiter().GetResult(); $rootBytes = $root.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult(); $indexPath = (Resolve-Path \".\\src\\FusionRpg.Server\\wwwroot\\index.html\").Path; $indexBytes = [IO.File]::ReadAllBytes($indexPath); $sha = [Security.Cryptography.SHA256]::Create(); $result = [ordered]@{ healthStatus = [int]$health.StatusCode; healthBody = $healthBody; rootStatus = [int]$root.StatusCode; rootContentType = $root.Content.Headers.ContentType.ToString(); rootBytes = $rootBytes.Length; indexBytes = $indexBytes.Length; rootSha256 = [Convert]::ToHexString($sha.ComputeHash($rootBytes)); indexSha256 = [Convert]::ToHexString($sha.ComputeHash($indexBytes)); exactIndexMatch = [Convert]::ToHexString($sha.ComputeHash($rootBytes)) -eq [Convert]::ToHexString($sha.ComputeHash($indexBytes)) }; $result | ConvertTo-Json -Compress | Tee-Object -FilePath \".playwright-cli\\qa-http.json\" } finally { $client.Dispose() }","result":"PASS; / returned 200 text/html, 403 bytes, exact index.html match."},{"command":"playwright-cli open \"http://127.0.0.1:5088/#/sanctum\"","result":"PASS; browser opened, title Rise of Summoner, bounded at 30s."},{"command":"playwright-cli goto \"http://127.0.0.1:5088/#/lawn\"","result":"PASS; real Lawn route rendered, bounded at 30s."},{"command":"playwright-cli eval \"location.hash = '#/lawn'\"","result":"PASS; final route remained #/lawn after the observed first-open landing redirect."},{"command":"playwright-cli close","result":"PASS; default browser closed."},{"command":"playwright-cli list","result":"PASS; no browsers."},{"command":"Stop-Process -Id 47304 -Force -ErrorAction SilentlyContinue; Stop-Process -Id 23608 -Force -ErrorAction SilentlyContinue","result":"PASS; only the two PIDs started by this run were stopped."}],"open_issues":["No connected injector/live game was available, so active-match recovery and foreign-match isolation remain browser-unproven.","The initial browser load logged GET /favicon.ico 404; the final console capture had zero errors/warnings.","A reload of #/lawn was observed to land on #/sanctum after the first-open write; confirm whether that deep-link behavior is intended."]} REPORT>>>

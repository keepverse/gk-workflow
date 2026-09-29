---
name: local-web-review
description: Start the local RPG server so the owner can review the web UI in a browser. Use whenever the owner asks to "open the website", "review the FE", or look at web changes locally — never improvise `npm run dev` or ad-hoc Start-Process calls from scratch.
---

# Local web review

## The one command that matters

```powershell
$env:FUSIONRPG_DATA = (Resolve-Path ".\src\FusionRpg.Server\data").Path
Start-Process -FilePath "dotnet" -ArgumentList "run" -WorkingDirectory (Resolve-Path ".\src\FusionRpg.Server").Path -WindowStyle Hidden -Environment @{ "FUSIONRPG_DATA" = $env:FUSIONRPG_DATA }
```

Then poll `http://127.0.0.1:5088/health` until it returns JSON (10-15s for a `dotnet run` cold start —
it has to compile, not just launch). The server serves **both** the API and the built web UI
(`wwwroot`) at that same port — this is `docs/runbook/local-dev.md` §1.

**`FUSIONRPG_DATA` is not optional when launching via `Start-Process`.** `Program.cs:14-15` calls
`builder.WebHost.UseContentRoot(AppContext.BaseDirectory)` unless `FUSIONRPG_DATA` is set. Launched via
`Start-Process` with an explicit `-WorkingDirectory`, that call throws `NotSupportedException: The
content root changed from "...\FusionRpg.Server\" to "...\bin\Debug\net8.0\"` — confirmed via a real
run, not theorized. Setting `FUSIONRPG_DATA` (to anything non-empty; a `data` subfolder is fine) skips
that branch and the server starts serving straight from the source `wwwroot`. Interactive
`cd src\FusionRpg.Server; dotnet run` in a real terminal doesn't need this — only the
`Start-Process`-from-a-tool-call path does.

## First check: is something already squatting on 5088

**Before starting anything**, check for an already-running (possibly stale) server:

```powershell
Get-NetTCPConnection -LocalPort 5088 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object { Get-Process -Id $_.OwningProcess | Select-Object Id, ProcessName, StartTime, Path }
```

A real incident (2026-08-29): a `dist\FusionRpg.Server\FusionRpg.Server.exe` published **two days
earlier** was still running and silently answering `/health` with a stale build — my own fresh
`dotnet run` attempts were failing to bind and dying, while I kept debugging the wrong thing (browser
cache, service workers) because the health check kept succeeding against the *old* process. If
something is already listening, `Stop-Process -Id <pid> -Force` it first, don't assume a passing
`/health` check means it's *your* build.

If the FE was just edited, rebuild it into `wwwroot` first so the server actually serves the new code:

```powershell
cd web\fusion-rpg-web
npm run build
```

## Why `Start-Process`, not a plain Bash/PowerShell foreground or `&`-backgrounded call

CLAUDE.md's own server-lifetime note (confirmed twice by real incidents): a server started via a
tool call's own process — foreground **or** backgrounded with `&`/`disown` — dies when that tool
call's process tree is cleaned up. It looks like the server crashed mid-session; it didn't, the
assistant's own tool call took it down. `Start-Process` in PowerShell detaches it from this session's
process tree so it survives past the tool call that launched it.

Do not use `deploy-play.py` for this — that script also starts (and full-deploys: guards, injector,
game launch) the server, and the same lifetime problem applies to it from an assistant session. It's
for the integrated game+injector+server flow, not a plain FE review. Reserve it for when the owner
explicitly wants the real game running too.

## After it's up

Open a browser tool (Chrome DevTools MCP or Playwright MCP) and navigate to
`http://127.0.0.1:5088/#/sanctum` (or whatever route is relevant to what's being reviewed). Don't
just report the URL and stop — the owner asked to *see* it, so drive a real, visible browser to it.

## Stopping it afterward

It's a detached process outside this session's tree, so it keeps running after the conversation ends
too. If the owner wants it stopped, find it with `Get-Process dotnet` (or check what's bound to 5088)
and `Stop-Process` it — don't leave that guessing to a future session.

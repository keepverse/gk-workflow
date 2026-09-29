# G2 live-probe runbook — `notification-ssot` NS5.13

**Row:** `NS5.13` (`tasks/notification-ssot-todo.md`) · **Spec:** `docs/architecture/notification-ssot/spec-world-notify-source.md` (§Live probe) ·
**Standard:** `docs/contributing/live-probe-standard.md` (RPG Server Debug scope) · **Written:** 2026-09-21, lane `ns-1`.

The probe itself is blocked (see §Prerequisites). This runbook exists so that the moment its
prerequisites exist, the run is short, exact, and produces the transcript the row asks for — and so the
dead ends this lane already measured are not re-measured.

## Prerequisites (both currently missing)

| # | Needs | Owner | Why the probe cannot run without it |
|---|---|---|---|
| 1 | a **real** world-creation route | `world-continuity` (`spec-world-creation.md` §Wiring gap / §Real gap) | the row's own acceptance: "on a world created through the real path … No `debug.*` fabricator used anywhere in the chain". Today `RpgStore.CreateWorld` has one caller, the SIM route, and on a **stock** server that route is not even mapped (`SimFlags.Enabled` — `POST /api/test/world/create` answers `405` unless `FUSIONRPG_SIM=1`) |
| 2 | an **authored** starvation scenario (play cannot produce one) | this program (a content task), or the manager's ruling | the acceptance's subject is a commit "that starves a component". Measured 2026-09-21 (`tasks/evidence-fragments/NS5.13.md`, measurements 1-3): 25 real turns produce no `loam.shortfall`; the committing save owns **one** sector whose component runs production 50 against upkeep 16 with 500 stock (`loam.overflow:50` each turn); `develop` makes a sector *richer* (development adds production as well as upkeep); `danger` is the upkeep input **no command touches**; and `cede` removes the whole component rather than shrinking it. and measurement 4 played the last lever: marching to a remote zero-stock sector and claiming it — every remote sector in this template is **guarded** (zone-of-control halt, claim resolves without ownership), so even that path needs a battle first. The scenario must therefore be **authored** — a world/template that cannot pay its upkeep, or an authored save |

Until both exist, `NS5.13` stays blocked and its suite line is recorded as measured per project
(`tasks/evidence-fragments/NS5.13.md`).

## The probe, once the prerequisites exist

Every step below is a real endpoint or a real screen action; none is a `debug.*` fabricator. Run against
**your own** server instance: own port (never the default `:5088`, which another session may hold), own
data dir, `FUSIONRPG_NO_BROWSER=1`.

```powershell
# 1. own instance (own data dir), with a species roster the isolated store can load
mkdir <own-data-dir>
$env:FUSIONRPG_DATA='<own-data-dir>'; $env:FUSIONRPG_URLS='http://127.0.0.1:5231'; $env:FUSIONRPG_NO_BROWSER='1'
dotnet run --project gk-forge/tools/CreatureSpeciesImport -c Release      # 904 species written
Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe -PassThru
Invoke-RestMethod http://127.0.0.1:5231/health                     # currentPlayerId

# 2. create the world THROUGH THE REAL ROUTE (not /api/test/...) and record the worldId
#    <world-continuity's route goes here; it must be the product path the web uses>

# 3. drive a REAL commit that starves a component (the scenario from prerequisite 2), then:
Invoke-RestMethod "http://127.0.0.1:5231/api/world/<worldId>/turn/<R>?asFaction=dave"   # the committing save's faction
Invoke-RestMethod "http://127.0.0.1:5231/api/notifications/<playerId>"                  # read-back through the real catch-up path
```

Then, and only then, the screen half: open the web UI against that instance, let it join the save, and
look at the world rail — it must show **exactly the just-resolved turn** (`worldLatestTurn`,
`dto.currentTurn - 1`) and rebuild itself from catch-up after a reload. The rail's items, the toast, and
the notification read-back must agree on the same row (`dedupKey`).

## Evidence the probe must produce

1. Every command with its response body, copied as issued (the `/commit` call, the catch-up GET, the
   rail's own network call if visible).
2. The **read-back through the normal query path** (the catch-up GET above), not a debug accessor.
3. Confirmation that the row's *siblings* were not delivered (a second save's connection receives
   nothing) — the isolation half of `NS5.12`, here on a live instance.
4. A screenshot of the real screen showing the rail's resolved turn (and the toast, if it toasted).
5. The scope statement: **RPG Server Debug** — the subject is a real save's world created through the
   product path; no `debug.*` command appears anywhere in the chain.

Where it goes: the transcript in the commit body or a `tasks/evidence-fragments/NS5.13-live.md` fragment,
with the numbers and the screenshot path; then the row's two acceptance lines can be ticked.

## Cleanup (do this in the same session)

Stop **your** server process by id (`Stop-Process -Id <pid>` — never by image name), delete the own data
dir, and leave no watcher or browser running. Never stop or reconfigure the default instance on `:5088`.

## What this runbook deliberately does not say

It does not propose a fourth debug surface, a parallel MCP toolset, or a fabricated world/notification:
the row's acceptance forbids the fabricator, and the standard's anti-cheat list names exactly that
shortcut. If prerequisite 1 cannot land, the row needs a re-worded acceptance (the in-process equivalent
`NS5.12`/`NS6.5` already prove) — that is a manager ruling, not a workaround to invent here.

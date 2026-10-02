---
name: live-lawn-quick-start
description: Cold-start a LIVE FusionRpg lawn for debug proves — enter level 1, lab-overlay, target ptr. Use before any LIVE status/VFX/combat/shield script.
---

# Live lawn quick start

All-in-one LIVE board setup for MelonLoader (default) or BepInEx. **Do not** ask the operator to manually open Adventure day when a script supports `-Live` or calls `Ensure-LiveLabBoard`.

## When to use

- LIVE status VFX identity audit
- Overlay combat prove (`prove_overlay_combat.py`)
- VFX organic path (`prove_vfx.py` with `-TargetPtr`)
- Python `live_test run status.l2.*`
- Any script needing a living zombie ptr on a lab board

## Cold start (assistant sessions)

```powershell
# 1. Server — survives tool-tree cleanup (do NOT rely on deploy-play starting server from assistant)
Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe

# 2. Injector only
python scripts\deploy-play.py --loader-host MelonLoader --no-server

# 3. Launch game if not running (MelonLoader 3.9 default on this machine)
#    deploy-play without -NoGame does this; or run PlantsVsZombiesRH.exe from the Melon pack

# 4. Wait for injector
Invoke-RestMethod http://127.0.0.1:5088/health
# → injectorConnected=true, simEnabled=false
```

## All-in-one test entry (preferred)

```powershell
.\scripts\audit-status-vfx-identity.ps1 -Live -Stress
```

This calls `Ensure-LiveLabBoard` internally — enter level 1 if needed, `lab-overlay`, assert living zombie, then apply 13 statuses.

Python equivalent:

```powershell
cd tools\live_test
python -m live_test run status.l2.apply
```

## API SSOT

```http
POST /api/debug/lawn/quick-start
Content-Type: application/json

{
  "scenario": "lab-overlay",
  "levelNumber": 1,
  "timeoutSec": 60
}
```

Response fields:

| Field | Meaning |
|---|---|
| `entered` | `true` if `debug.enter-level` opened a new board |
| `levelType` | Must not be Explore/Travel/IZ |
| `targetPtr` | First living zombie hex ptr |
| `plantPtr` | First living plant hex ptr |
| `note` | Set when snapshot did not arrive in server poll window |

PowerShell SSOT helper: [`scripts/lib/LiveLawnSetup.ps1`](../../scripts/lib/LiveLawnSetup.ps1) → `Ensure-LiveLabBoard`.

Python SSOT: [`gk-fusion/tools/live_test/live_test/status_apply.py`](../../tools/live_test/live_test/status_apply.py) → `ensure_lab_board()`.

## Mid-match only (legacy)

When the operator is **already** in Adventure day and only needs fixtures reset:

```powershell
.\scripts\setup-lab-run.ps1
```

This script **does not** enter a level — it throws without `board.start`.

Use `-SkipSetup` on audit when board is already labbed:

```powershell
.\scripts\audit-status-vfx-identity.ps1 -Live -TargetPtr <ptr> -SkipSetup
```

## Failure triage

| Symptom | Fix |
|---|---|
| `injector not connected` | Launch game; wait for MelonLoader FusionRpg mod |
| `lawn/quick-start` HTTP 404/405 | Restart server from fresh `dist\FusionRpg.Server` build |
| `no living zombie ptr` | Read `cheat.error` / `debug.effect.error` in thrown message; return to main menu and re-run |
| `levelType=Explore` | Back to menu → Adventure day, or let quick-start enter level 1 from menu |
| `targetPtr` null but scenario ok | Snapshot poll failed — `Ensure-LiveLabBoard` re-polls `debug.effect.board-snapshot` |

## Related docs

- [debug-pipeline.md](../../docs/runbook/debug-pipeline.md) — status apply two-path table
- [live-test-ssot.md](../../docs/runbook/live-test-ssot.md) — Python harness
- [tasks/vfx-identity-batch6-live-plan.md](../../tasks/vfx-identity-batch6-live-plan.md) — batch 6 LIVE gate

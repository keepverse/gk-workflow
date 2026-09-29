# Status audit captures

Optional screenshot/clips for the [status identity audit](status-identity-audit-2026-08-30.md).

## Capture protocol

For each of the 13 custom statuses, save three files:

| File | Timing | Content |
|---|---|---|
| `{statusId}-apply.png` | T+0.2s after apply | Apply burst + flash peak |
| `{statusId}-sustain.png` | T+2s | Sustained aura/tint/marker |
| `{statusId}-stack.png` | T+2s | Two statuses on one host (stress) |

## How to apply

```powershell
# All-in-one: enter level 1 + lab-overlay + 13 status applies + optional stress
.\scripts\audit-status-vfx-identity.ps1 -Live -Stress
```

Per-status captures after setup (optional `--skip-setup`):

```python
from debug_status_apply import invoke_status_apply_until_started
invoke_status_apply_until_started(status_id="wither", host_ptr=target_ptr, duration_ms=8000)
```

`gk-core/scripts/lib/debug_status_apply.py` is the module; `scripts/lib/DebugStatusApply.ps1` was its PowerShell
form and is retired (ported 2026-09-29).

Or HTTP (RPG path — custom VFX):

```http
POST /api/debug/status/apply
{ "statusId": "wither", "hostPtr": "<TargetPtr>", "amount": 20, "durationMs": 8000 }
```

Do **not** use `/apply-status` for identity captures — that path skips StatusRuntime VFX.

Clear between captures: `POST /api/debug/clear-status` `{ "ptr": "<TargetPtr>" }`.

## LIVE status (2026-08-30)

Automated harness green: **13/13** `sustainedStarted` via `audit-status-vfx-identity.ps1 -Live -Stress` (all-in-one `Ensure-LiveLabBoard`). Screenshots in this folder still pending owner capture.

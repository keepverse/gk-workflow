# CC8 live probe — a real run created by a real game, read back through the normal query path

**Date:** 2026-09-23 · **Slot:** 1 (pool `H:\Games\PVZ-Fusion-Tests`, port 5101) · **Session:** `live-probe-cc8`
**Integration head at probe time:** `196eb398f` · **Standard:** [live-probe-standard.md](../../docs/contributing/live-probe-standard.md)

## What was proven

A real record, created through a real flow, operated on by a real operation, and **read back through the same path
the normal frontend uses** — plus the live-engine half, separately.

| Half | Evidence | Scope (§1) |
|---|---|---|
| the injector talks to the slot's OWN server | `<slot>\MelonLoader\Latest.log`: `[05:26:41.622] [FusionRpg] FusionRpg MelonMod host ready, server=http://127.0.0.1:5101` | `game-injector-debug` |
| the game entered a real lawn run | `debug_lawn_setup` → `ready: true`, `entered: true`, `levelType: "Advanture"`, `liveState: "InMatch"`, plant 1 / zombie 1 | `game-injector-debug` |
| a real operation, with a receipt | `debug_act {"verb":"shovel"}` → `ok: true`, `receipt.tag: act-c4fea300`, `verb: shovel`, `col 0 / row 0`, `expectKind: plant.shovel`, `scenarioId: 7950ad28b1c2` | `game-injector-debug` |
| the live engine reflected it | `debug_game_state` after → `hasBoard: true`, `matchPhase: "InMatch"`, `plantCount: 1`; `debug_screenshot` → `tasks/reports/cc8-live-probe-20260923/lawn.png` (960×540, 1,031,542 B) | `game-injector-debug` |
| **the server ran real domain logic for this client** | slot server log: `[commander] seat refused for run d2b8aba3-e45b-455b-9aeb-5ac19b0bb887: seat.notCommander (commander:dave)` | server domain |
| **READ BACK through the normal query path** | `GET http://127.0.0.1:5101/api/runs` → run `id: 215`, `matchKey: d2b8aba3-e45b-455b-9aeb-5ac19b0bb887`, `playerId: 1`, `startedUtc: 2026-09-22T22:27:30.7329342Z`, `levelType: "Advanture"`, `boardLevel: 1`, `plantsPlanted: 1`, `game: "pvzrh-3.9"` | **normal path** |

The `matchKey` is the exact GUID printed by the server's own domain line, and `startedUtc` is the minute the drive
ran — so the record cannot be an earlier run's, and it cannot have been written by the probe itself.

The read-back used `GET /api/runs`, which is the route the frontend itself calls (`gk-core/src/FusionRpg.Server/Program.cs:1582`),
not a debug-only endpoint.

## The probe tool's verdict differed — and that was the tool, not the product

`prove-slot-connection.ps1` reported `CONNECTION PROVEN False`. Read carefully, that was a **pattern** result: it
greps the server log for `Connection id |Request id `, and this server's console logger emits neither — 21 log
lines, **0** transport lines, 1 domain line. The script already refused to read that as "the server never saw the
client" (`serverLogCanWitness = false`), and the injector's own log carried no SignalR/Hello line to fall back on.

Fixed in the same change: the server's **domain** lines are now accepted as the witness, because a line like
`[commander] seat refused for run <guid>` cannot be written by anything but a request that carried the player's
identity. The read-back above is the independent, normal-path proof.

## Not checked — stated plainly

- Only **slot 1** was exercised. Slots 2 and 3 were never cloned or claimed.
- The probe ran against a **slot** install only. The owner's install and `:5088` server were fingerprinted before
  and after: `owner untouched True`; the owner's server answered HTTP 200 throughout.
- This document is the **live** half of CC8. The unit-test half is a separate reading
  (`test-fast.ps1 -AllDefault`) and is recorded on the run board.
- The drive was performed by the manager through the debug CLI (`gk-fusion/tools/debug-mcp/cli.py`), not by the probe script;
  the script brings the slot up (and, with `-KeepRunning`, leaves it up for exactly this).

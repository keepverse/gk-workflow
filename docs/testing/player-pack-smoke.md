# Player-pack smoke probe

Automation checks for an **unpacked player pack** (`dist/FusionRpg` or a Release unzip). This is **not** the SIM-only HTTP [`/api/test/probe`](probes.md).

| Probe | Role |
|---|---|
| HTTP `test.probe` / snapshot | SIM server events (`FUSIONRPG_SIM=1`) — E2E / fake injector |
| **Player-pack smoke** | Layout, loader/plugin offline, update data preserve, server boot with SIM **off** |

## What it checks

Core logic: [`PlayerPackProbe`](../../gk-fusion/src/FusionRpg.Launcher/Services/PlayerPackProbe.cs)

1. **layout** — launcher/server exes, DropIntoGame injector, `loader-manifest.json`, `PLAYERS.txt`, `LICENSE`, `Server/wwwroot/index.html`
2. **manifest** — pins load; asset regexes non-empty
3. **loader_plugin** — temp BepInEx game tree; `LoaderProbe` OkForV1; `PluginInstaller` copies DropIntoGame
4. **dual_load** — Bep + Melon markers → `LoaderKind.Both`, blocks both installs
5. **update_preserve** — staged zip + `FusionRpgUpdater.PrepareApply` keeps `Server/data`
6. **server_boot** (script) — start `Server\FusionRpg.Server.exe`, `GET /health` with `ok` and `simEnabled` false; `/api/test/snapshot` must not return SIM JSON (SPA fallback is OK when SIM is off)

## How to run

```bash
# After a local publish:
export FUSIONRPG_GAME_DIR="<your game folder>"
python gk-core/scripts/publish_player.py
python gk-core/scripts/smoke_player_pack.py

# Offline probe only (no server process):
python gk-core/scripts/smoke_player_pack.py --skip-server-boot

# Reproducible run against a known-free port (a port is configuration, not a random draw):
python gk-core/scripts/smoke_player_pack.py --port 5391

# Machine-readable verdict:
python gk-core/scripts/smoke_player_pack.py --json

# Console JSON only:
dotnet run --project gk-fusion/tools/FusionRpg.PackSmoke -c Release -- dist/FusionRpg
```

Exit codes: `0` passed, `1` the pack failed a check, `64` the tool refused (the pack, the probe
project, or `dotnet` was missing; the probe's output was unreadable; the requested port was taken).
A refusal names its reason in `--json` — it never reports an empty result as a pass.

Summary JSON: `artifacts/player-pack-smoke.json` (does not exist until a smoke run creates it, never tracked).

Unit tests (always in CI, fake pack fixture): `dotnet test tests\FusionRpg.Launcher.Tests --filter PlayerPackProbe`.
The tool's own contract suite: `python -m pytest gk-core/tests/tools/test_smoke_player_pack.py`.

Release workflow runs `gk-core/scripts/smoke_player_pack.py` after `gk-core/scripts/publish_player.py`, then zips `FusionRpg-win-x64.zip`.

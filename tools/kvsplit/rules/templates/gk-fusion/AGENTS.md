# gk-fusion

The game-host mod: injector and loader hosts, Launcher, game profiles, live-probe and debug tools, the
player release. The only repo allowed to reference the game host. **Public.**

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` and
`../CLAUDE.md` (loaded automatically for any agent working inside this folder). Docs live in `../docs/`.
This file was emitted by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Compile only against gk-core (`GkCoreRoot`); ship the `fusion` content pack from gk-data in the release.
- Never commit game binaries or files extracted from a game install.

## Build and deploy

```powershell
dotnet build FusionRpg.slnx
.\scripts\deploy-play.ps1 -NoServer
```

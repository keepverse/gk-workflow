# gk-core

The engine: Contracts, Core, Data, CheatCore, Server, web, `data/tuning`. **Public.**

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` and
`../CLAUDE.md` (loaded automatically for any agent working inside this folder). Docs live in `../docs/`.
This file was emitted by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Never compile against gk-forge or gk-fusion. Content comes from gk-data at runtime only, through
  `GkDataRoot` and a pack name; no test in this repo may need gk-data (public CI cannot read it).
- No game-host (Unity, Il2Cpp, Harmony, BepInEx, MelonLoader) reference anywhere in this repo.

## Build and test

```powershell
dotnet build FusionRpg.slnx
dotnet test tests/FusionRpg.Core.Tests
cd web/fusion-rpg-web; npm ci; npm test; npm run build
```

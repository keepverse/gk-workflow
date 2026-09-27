# gk-core

The engine: Contracts, Core, Data, CheatCore, Server, `data/tuning`. **Public.**

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` (loaded
automatically for any agent working inside this folder). Docs live in `../docs/`. This file was emitted
by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- Never compile against gk-forge, gk-web or gk-fusion. Content comes from gk-data and gk-content at
  runtime only, through a content root and a pack name; no test in this repo may need them, because
  both are private and public CI cannot read them.
- No game-host (Unity, Il2Cpp, Harmony, BepInEx, MelonLoader) reference anywhere in this repo.
- The browser control room is **gk-web**, not here. This repo serves its static output from `wwwroot`,
  so the two ship as one release and bind to the same `Contracts` DTOs.

## Build and test

```powershell
dotnet build FusionRpg.slnx
dotnet test tests/FusionRpg.Core.Tests
```

Web is `gk-web`. Content is `gk-content` (authored) and `gk-data` (derived corpus).

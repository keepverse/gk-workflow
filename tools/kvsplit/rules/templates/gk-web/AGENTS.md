# gk-web

The browser control room: the lawn view, sheets, progression and the live HUD. **Public.**

The binding rules for every Keepverse repository are in the workspace root: `../AGENTS.md` (loaded
automatically for any agent working inside this folder). Docs live in `../docs/`. This file was emitted
by kvsplit; change its template in `tools/kvsplit/rules/templates/`, not here.

## Rules specific to this repo

- The web **reads** state; it never decides it. Game logic is gk-core.
- Node is **developer-only**. Players get a static build served by `FusionRpg.Server` from the same
  origin; nothing here may become a runtime dependency of the shipped game.
- A type error fails the build (`tsc --noEmit` runs first). Do not weaken it to make a red build pass.
- Phaser stays out of the entry chunk — dynamic `import()` and route splitting. A fat bundle is a
  code-splitting failure, not a reason to ban the library.
- Player names and roster membership load from the content catalog. Do not hardcode a front-end union
  and do not put copy in a numbers file.
- No engine vocabulary on a player surface, and no developer surface in game navigation.

## Build and test

```bash
npm ci
npm test
npm run build
npm run check:bundle
```

The Server serves this build from `wwwroot`, so web and server ship as one release and bind to the
same `Contracts` DTOs.

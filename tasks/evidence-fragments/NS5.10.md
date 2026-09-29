# NS5.10 — `WorldStage` reads the feed; capture-loss debt adapter

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `useState<RailItem[]>` removed; the rail reads the feed through `worldLatestTurn({ worldId, lastResolvedTurn: dto.currentTurn − 1 })`; open / dismiss / undo call `useSetNotificationState` (`read` / `dismissed` / `read`); the world mount registers its sector/legion `TargetActionResolver` | `cd web\fusion-rpg-web; npx vitest run src/stages/world src/shell/notify src/ui/volumeMatrix` | `Tests 871 passed`, `1 failed` — the one failure is `volumeMatrix.test.ts`'s `Map_FE_files_are_untouched`, which shells out to `git status` over the frozen map-FE paths and is red **only while this task is uncommitted** (green at HEAD, see the last row); the world scope itself is green | gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx |
| `legacyCaptureLoss.ts` keeps the capture-loss notice rendering in the world rail under `territory.lost`, never injected into the feed, never durable | `npx vitest run src/stages/world/notify/legacyCaptureLoss.test.ts` | `Tests 6 passed` — one row per captured vault under `territory.lost` (`domainOf(row.category) === "world"`, so the id is a real catalogue row), `seq`/`worldId`/`worldTurn` all `null`, the same sector twice is one notice, and `useNotificationFeed.byKey` stays empty (`maxRev 0`, `playerId null`) | gk-web/web/fusion-rpg-web/src/stages/world/notify/legacyCaptureLoss.ts (+ .test.ts) |
| `volumeMatrix.test.ts` "World notification rail" keeps `render-all` with the new `worldLatestTurn` reason | `npx vitest run src/ui/volumeMatrix.test.ts` | row reads `strategy: "render-all"`, reason `"Structurally one resolved turn's notifications for one player (`worldLatestTurn`), the same one-turn bound as the playback keyframe rail; the visible toast stack is capped at three (Toasts.tsx's own VISIBLE_CAP)"` | gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts |
| `npm run build` (type errors fail it) | `cd web\fusion-rpg-web; npm run build` | `✓ built in 9.59s` | — |
| the map-FE freeze guard, re-run at HEAD | `npx vitest run src/ui/volumeMatrix.test.ts` after the commit | green — the guard reads real `git status`, so it can only be green once committed; this change is the owner's accepted ask **A1** (`notification-ssot-map.md` §G0), now named in the guard's own exception list | gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts |

**The freeze line itself is filed, not patched:** `spec-delve-stage.md` §15 ("UNTOUCHED:
`src/stages/world/**` …") is stale for a third time because the owner's A1 acceptance moved the rail
out of `stages/world/notify/**` and rewired `WorldStage.tsx`. That doc is the party-dungeon program's,
so the row went into **its** todo (`tasks/party-dungeon-todo.md`, F12) rather than being edited here.

**NOT proved:** no live probe (NS5.13); NS5.11 still deletes the world `categories.ts`/`channelSettings.ts`
copies and NS5.6's migration-equivalence test, and updates `world-stage-map.md:241` — nothing in
production imports them any more (checked by grep), which is why the build stays green there.

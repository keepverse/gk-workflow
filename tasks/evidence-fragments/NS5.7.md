# NS5.7 — Move the rail store to `shell/notify/rail/railStore.ts` (ask A1)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `notifyRailStore.ts` -> `shell/notify/rail/railStore.ts`; `RailItem.category` is `NotifyCategoryId` and gains `dedupKey`, `seq`, `worldId`, `worldTurn`, `severity`; `flush`/`onCommit` retired (their intent ported to `worldLatestTurn` tests) | `cd web\fusion-rpg-web; npx vitest run src/shell/notify src/stages/world src/stages/world/cacheClaim` | `Test Files 99 passed (99)`, `Tests 860 passed (860)` — `railStore.test.ts` holds the moved transitions and the retirement proof: `worldLatestTurn` includes only the most recently resolved turn, a non-advancing commit changes nothing, and the store exports no `flush`/`onCommit` | gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts, gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.test.ts |
| the old files are gone and the one type is the new one | `git status --short` | `D web/fusion-rpg-web/src/stages/world/notify/notifyRailStore.ts`, `D …/notifyRailStore.test.ts`; `railItems.ts` no longer declares `RailItem`/`RailItemState` and imports them from `./railStore`, populating the five new fields from the feed row | gk-web/web/fusion-rpg-web/src/shell/notify/rail/railItems.ts |
| `npm run build` (type errors fail it) | `cd web\fusion-rpg-web; npm run build` | `tsc --noEmit` clean; `✓ built in 11.04s` | — |
| the two click-budget rows that used the retired `onCommit` keep their intent | `npx vitest run src/stages/world/notify` (part of the run above) | rows 1 and 3 now assert the mount policy over feed rows (a routine item costs 0 clicks, and a feed of three is retired by the next resolved turn) instead of a store flush; channels unchanged: `growth`/`intel.new`/`supply.change` all default to `rail`, so all three are shown | web/fusion-rpg-web/src/stages/world/notify/clickBudget.test.tsx |

**Two things had to move with the widened type, named here so NS5.9 knows its remainder:**
`ChannelControl` now reads `@/shell/notify/channelSettings` — the ONE channel store (same storage key,
same change-event name), so it accepts the open `NotifyCategoryId`; NS5.9 keeps only its file move and
the moved suites. The named capture-loss debt adapter (`cacheClaim/captureNotice.ts`) supplies
`dedupKey`/`severity` and carries `seq: null`, `worldId/worldTurn: null` — it is local by
construction, never durable, never in the feed (world-notify-source §Debt).

**Environment note:** this worktree had no `web/fusion-rpg-web/node_modules`, so `.kilo/setup-script.ps1`'s
documented step was run by hand (`npm ci`) before any FE check; without it the editor's LSP reports
`Cannot find module 'react'` and every untyped cascade downstream of it.

**NOT proved:** no live probe (NS5.13); NS5.8/5.9/5.10/5.11 still own the component moves, the
`WorldStage` feed wiring, and the deletion of the world `categories.ts`/`channelSettings.ts` copies.

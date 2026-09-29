# NS5.9 — Move `ChannelControl` + the click-budget suites (ask A1)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ChannelControl` under `shell/notify/rail/` reading `shell/notify/channelSettings.ts` | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/rail` | `Test Files 8 passed (8)`, `Tests 35 passed (35)` — the control moved with its test; its store import is `@/shell/notify/channelSettings` (switched in NS5.7 with the widened category type, since the open id cannot be the world's closed union), and `RailItem.tsx`'s temporary world import is now `./ChannelControl` | gk-web/web/fusion-rpg-web/src/shell/notify/rail/ChannelControl.tsx (+ .test.tsx) |
| moved `clickBudget.test.tsx` and `noBandThree.test.tsx` pass **with the same intent** (routine = 0 clicks, act = 1, clear = 0, change channel = 1; no band-3 opener) | same run | the four rows are asserted by name: `row 1: acknowledging one routine event costs 0 clicks…`, `row 2: acting on one important event costs 1 click…`, `row 3: clearing a feed of several items costs 0 per-item clicks…`, `row 4: changing how a category notifies costs 1 click…`; `noBandThree` keeps `clicking every interactive control this module ships never pushes a layer`, `a turn carrying a fade warning (Toast) leaves the layer stack empty once acknowledged`, and its static scan | gk-web/web/fusion-rpg-web/src/shell/notify/rail/clickBudget.test.tsx, …/noBandThree.test.tsx |
| nothing left in the world stage's notify module that the rail owns | `ls src/stages/world/notify/` | only `categories.ts` (+ test), `channelSettings.ts` (+ test), `worldTranslator.ts` (+ test) remain — the world copies NS5.11 retires | — |
| wider scope + `npm run build` | `npx vitest run src/shell/notify src/stages/world`; `npm run build` | `Test Files 99 passed (99)`, `Tests 860 passed (860)`; `✓ built in 8.86s` | — |

**One stale name fixed in the move:** `noBandThree`'s static scan walks `__dirname`, so it now scans
`shell/notify/rail/`; its test name still said `stages/world/notify/`. Renamed to name the module it
actually scans — the scan itself and its intent are unchanged.

**NOT proved:** no live probe (NS5.13); `WorldStage`'s feed wiring is NS5.10, and the world
`categories.ts`/`channelSettings.ts` deletion plus the volume-row reason is NS5.11.

# NS5.8 — Move `NotifyRail` and `RailItem` components (ask A1)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| both components (+ colocated tests) under `shell/notify/rail/`, props unchanged except the category type | `cd web\fusion-rpg-web; npx vitest run src/shell/notify src/stages/world` | `Test Files 99 passed (99)`, `Tests 860 passed (860)` — the four files moved with their tests, and no test body changed (the components' prop types are the same shapes; only `RailItem.category` is the catalogue's open id, from NS5.7) | gk-web/web/fusion-rpg-web/src/shell/notify/rail/NotifyRail.tsx (+ .test.tsx), …/RailItem.tsx (+ .test.tsx) |
| the move | `git status --short gk-web/web/fusion-rpg-web` | `D gk-web/web/fusion-rpg-web/src/stages/world/notify/{NotifyRail,RailItem}{,.test}.tsx` and the four `?? …/src/shell/notify/rail/` files — nothing left behind under `stages/world/notify/` but the control, the two suites and the translator (NS5.9–NS5.11) | — |
| text comes from `renderNotification` | same run | unchanged: `RailItem.tsx` renders `item.title`/`item.body`, which `railItemsFrom` fills from `renderNotification` (NS4.6); this task moved the components, not the text path | gk-web/web/fusion-rpg-web/src/shell/notify/rail/railItems.ts |
| `npm run build` (type errors fail it) | `cd web\fusion-rpg-web; npm run build` | `3141 modules transformed`, `✓ built in 9.13s` | — |

**One temporary import, named for NS5.9:** the moved `RailItem.tsx` imports `ChannelControl` from its
world home (`@/stages/world/notify/ChannelControl`) with a comment saying so — the control moves beside
it in NS5.9, which also moves `clickBudget.test.tsx`/`noBandThree.test.tsx` (both already import the
rail from `shell/notify/rail/`, updated here so nothing points at a deleted path).

**NOT proved:** no live probe (NS5.13); the `WorldStage` feed wiring is NS5.10 and the retirement of the
world `categories.ts`/`channelSettings.ts` copies is NS5.11.

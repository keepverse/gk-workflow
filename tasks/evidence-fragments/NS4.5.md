# NS4.5 — `NotificationWire`: app-level wiring, triggers F1-F7, error state

| Criterion | Command | Result |
|---|---|---|
| mounted beside `<Toasts />` in `App.tsx`, renders nothing; F1/F2/F3/F4/F4b/F5/F6/F7 one test each | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/NotificationWire.test.tsx` | `Test Files 1 passed, Tests 11 passed` |
| a failed catch-up sets `status = "error"`, never an empty feed; `retryNotificationCatchUp` re-attempts from the last known cursor | same run | `a failed catch-up sets status to error...`, `retryNotificationCatchUp re-attempts from the last known cursor and can clear the error` both pass |
| `App.tsx` diff is additive: one import, one `<NotificationWire />` beside `<Toasts />` | `git diff -- src/app/App.tsx` (this lane's own diff) | 2 lines added, 0 removed |
| full web suite has no new failures | `npx vitest run` (whole project) | `3141 passed`, the same 5 pre-existing failures as before this wave (`ui/actor/*`, `ui/gui-lego/*`, `dev/*`, `layers/commanders/*`, `theme/hexGuard` — none touch a wave-4 file, confirmed by reading each failure's file list) |
| build + bundle | `npm run build` / `npm run check:bundle` | `✓ built in 40.05s`, `Phaser is absent from the entry chunk — OK` |

F6 (this session's own read/dismiss/undo) closes through `useSetNotificationState`'s `onSuccess`
(NS4.1), not through `NotificationWire` itself — GG-15's "never paint before the server returns"
holds because the feed is only touched after the mutation resolves.

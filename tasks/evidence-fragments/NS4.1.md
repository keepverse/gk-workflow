# NS4.1 — `lib/bus/notifications.ts`: subscription, catch-up pager, state mutation

| Criterion | Command | Result |
|---|---|---|
| subscribes to `NotificationBatch`/`NotificationStateChanged` via `getHubConnection()`, no new `HubProvider` handler; pages `GET …?since=` until `hasMore=false` | `cd web\fusion-rpg-web; npx vitest run src/lib/bus/notifications.test.ts` | `Test Files 1 passed, Tests 6 passed` |
| `useSetNotificationState()` is a TanStack mutation; on success applies the response through the same reducer path as a pushed `NotificationStateChanged` (F6) | same run | `posts seqs and state...`, `on success, applies the change to the notification feed (F6, same path as F5)` both pass |

`hub-provider.tsx` untouched — confirmed no new `c.on(...)` line added there for these two events.

# NS6.10 — `useNotificationHistory(category)` in the bus

| Criterion | Command | Result |
|---|---|---|
| pages `GET /api/notifications/{playerId}/history?category=&before=` newest first; `load-older` passes the last `seq` as `before`; a failed page surfaces the error state | `cd web\fusion-rpg-web; npx vitest run src/lib/bus/notifications.test.ts` | `Test Files 1 passed, Tests 11 passed` |
| no regression | `npx vitest run src/shell/notify src/lib/bus` | `Test Files 28 passed, Tests 160 passed` |
| `npm run build` | | `✓ built in 13.12s` |

Built on `useInfiniteQuery` (the already-locked `@tanstack/react-query`'s own infinite-pagination
primitive) rather than a hand-rolled accumulate-and-fetch hook — `fetchNextPage()` IS "load older."
The cursor derivation (`hasMore` -> next `seq`, or `undefined` to stop) is a pure exported function,
`nextHistoryPageParam`, tested directly rather than through react-query's own internal timing — the
one `renderHook` integration test only proves the URL shape (`before=8` on the second call), and the
`hasMore: false` "no more pages" edge case is a fast, deterministic unit test on the pure function.

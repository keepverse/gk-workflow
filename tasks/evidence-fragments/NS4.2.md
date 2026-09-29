# NS4.2 — Feed reducer and store (dedup, higher rev wins, per save)

| Criterion | Command | Result |
|---|---|---|
| pure `applyItems`, `applyStateChange`, `resetForPlayer`; `byKey` on `dedupKey`; a merge keeps the higher `rev`; another save's items are ignored (F7) | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/feed/feedReducer.test.ts` | `Test Files 1 passed, Tests 8 passed` |
| push-then-GET and GET-then-push end with one item; a page fetched before a dismiss that lands after its F5 leaves it dismissed | same run | `applyItems dedups on dedupKey and keeps the higher rev regardless of order` (asserts both orders `.toEqual` each other), `a page fetched before a dismiss and applied after its state-change event leaves the item dismissed` both pass |

`applyStateChange` for a `seq` never held drops the change without advancing `maxRev` (documented in
the reducer) — a store row's `rev` is bumped in place, so advancing past an unseen row would make
the next catch-up page skip it forever; the next GET/batch brings it in at its current state instead.

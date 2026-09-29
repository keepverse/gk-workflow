# NS1.8 — Web joins the shown save on start, reconnect and save switch

| Criterion | Command | Result |
|---|---|---|
| `joinCurrentPlayer` invoked after every `Join("web")` (T1, T2 `onreconnected`); on `useSelectPlayer` success (T3, no reconnect); emits `player-joined(id)` only when the server returns `true` | `cd web\fusion-rpg-web; npx vitest run lib/bus/playerRouting` | `Test Files 1 passed (1)`, `Tests 6 passed (6)` |
| T2-then-T3 and T3-then-T2 both end on the shown save; a second session that did not switch keeps its group; T5 (refused) logs once and emits no `player-joined` | same run | `T2-then-T3 and T3-then-T2 both end on the shown save's id...`, `a second session that did not switch keeps its own group...`, `T5 - a refused id logs once...` all green |
| no regression in the existing hub wiring | `npx vitest run lib/bus/hub-provider` | `Test Files 1 passed (1)`, `Tests 5 passed (5)` |
| build | `npm run build` | `✓ built in 1m 29s` (pre-existing >500kB chunk warnings, unrelated) |

A failed `joinShownPlayer` (e.g. a transient `/api/players` read) is caught at both T1 and T2 call
sites and only warns - it never flips the SignalR connection's own `status` to `err`, keeping the
two concerns (connection health vs. player routing) separate.

# Fix — `joinCurrentPlayer` rejected on a disconnected connection (review finding on `aee70cc6`)

**Root cause:** `mutations.ts`'s `useSelectPlayer.onSuccess` calls `void joinCurrentPlayer(getHubConnection(), id)`
unguarded. `HubConnection.invoke` throws synchronously when `state !== Connected` (starting, mid-reconnect,
or a bare test singleton with no live socket), producing an unhandled promise rejection — a real
production robustness bug (a save switch while offline/reconnecting), not just a test artifact.

| Criterion | Command | Before | After |
|---|---|---|---|
| the reported test is clean | `cd web\fusion-rpg-web; npx vitest run src/lib/bus/mutations.test.tsx` | `Errors 1 error` (`Cannot send data if the connection is not in the 'Connected' State`) | `Test Files 1 passed (1)`, `Tests 15 passed (15)`, no Errors line |
| fix generalizes to every caller (T1/T2/T3 all use one function) | `npx vitest run src/lib/bus/mutations.test.tsx src/lib/bus/playerRouting.test.ts src/lib/bus/hub-provider.test.tsx` | — | `Test Files 3 passed (3)`, `Tests 28 passed (28)` |
| whole `lib/bus` suite, broader regression check | `npx vitest run src/lib/bus` | — | `Test Files 16 passed (16)`, `Tests 86 passed (86)` |
| build | `npm run build` | — | `✓ built in 9.98s` |

**Fix:** `joinCurrentPlayer` never rejects now - it checks `c.state === HubConnectionState.Connected`
before invoking (skips with a warning otherwise, the common real case right after boot) and wraps the
`invoke` call itself in try/catch (any other failure, e.g. a mid-send disconnect) as a second line of
defence. Two new tests reproduce the exact regression (`Disconnected` state, and a throwing `invoke`)
and prove `resolves.toBe(false)` rather than a rejection.

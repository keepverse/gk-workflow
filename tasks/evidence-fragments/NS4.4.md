# NS4.4 — Open-id channel settings and toast routing

| Criterion | Command | Result |
|---|---|---|
| `shell/notify/channelSettings.ts` reuses storage key `fusionrpg.world-notify.channels.v1`, defaults from `defaultChannelOf`, change event keeps two controls in step | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/channelSettings.test.ts` | `Test Files 1 passed, Tests 5 passed` |
| `toastRouting.ts` pushes only items first seen in a `live` batch whose channel is `toast`; `off` never toasts, Critical included; a later live copy of a held item does not re-toast | `npx vitest run src/shell/notify/feed/toastRouting.test.ts` | `Test Files 1 passed, Tests 5 passed` |

"First seen" is checked against the feed's OWN pre-merge `byKey` (passed in by the caller), not a
separate memory Set — so it naturally clears on an F3 save switch instead of leaking for the life
of the session. A toast's `action` is resolved through `targetActions.ts`'s registry (§6), built as
part of this task since `toastRouting`'s own acceptance ("plus … an action if the mount resolves
one") depends on it.

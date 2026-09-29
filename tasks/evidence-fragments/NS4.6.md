# NS4.6 — Rail mount policy, rail selector, target-action registry

| Criterion | Command | Result |
|---|---|---|
| `RailMountPolicy` + `worldLatestTurn` (items of `worldId` at `lastResolvedTurn` only; a non-advancing commit leaves the selection; a feed restored by catch-up selects the same items) | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/rail/mountPolicies.test.ts` | `Test Files 1 passed, Tests 3 passed` |
| `railItemsFrom(feed, policy, ctx, channels)` maps unread/read/dismissed/minimized/blocking per §5 and excludes `off`; `TargetActionResolver` registry — an item gets a button only when a resolver is registered for its target kind | `npx vitest run src/shell/notify/rail/railItems.test.ts` | `Test Files 1 passed, Tests 5 passed` |

`blocking` is always `false` in v1 (world-turn's declared list ships empty, spec-world-notify.md §5
— no v1 source sets it, documented in `railItems.ts`). `targetActions.ts`'s registry is exercised
indirectly by `toastRouting.test.ts` (NS4.4) since no resolver is registered by default, so
`resolveTargetAction` returns `null` and no toast carries an action yet — correct for v1, where no
mount has registered one.

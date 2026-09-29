# NS6.9 — Pure fold, closed bus catalog, selection store

| Criterion | Command | Result |
|---|---|---|
| `foldNoticesVm` lists every registered category (zero rows and `off` included) with its channel and unread count; rows newest first; every row's text via `renderNotification`, no id in it | `cd web\fusion-rpg-web; npx vitest run src/features/notices/foldNoticesVm.test.ts` | `Test Files 1 passed, Tests 9 passed` |
| `noticesBus.ts` holds exactly the seven events of spec §2.5, each calling exactly its effect; `selectedCategory` lives in module-level `noticesUiStore.ts`, not component state | `npx vitest run src/features/notices/noticesBus.test.ts` | `Test Files 1 passed, Tests 3 passed` |
| no regression | `npx vitest run src/shell/notify src/features/notices src/features/gui-lego` | `Test Files 26 passed, Tests 194 passed` |
| `npm run build` | | `✓ built in 9.36s` |

`wireNoticesBus(bus, effects)` is framework-free (no React) so "each event calls exactly its own
effect, none of the others" is testable directly, without a `NoticesSurface` component — NS6.11
(blocked on NS6.8's owner review) only has to supply the real mutation hooks as `effects` from a
`useEffect`. `foldNoticesVm` merges the live feed with a paged history for the selected category,
deduped on `dedupKey` with the higher `rev` winning (mirrors `feedReducer.ts`'s own rule), so a
dismiss made in the centre or on the rail is never re-shown as unread by the other.

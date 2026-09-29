# NS4.3 — Toast selection: Critical first at the cap (R-N4, R-N6)

| Criterion | Command | Result |
|---|---|---|
| `ToastEntry.severity?` additive; `Toasts.tsx` uses pure `selectVisibleToasts(toasts, VISIBLE_CAP)` — Critical newest first, then the rest newest first, remainder behind "+N more" | `cd web\fusion-rpg-web; npx vitest run src/shell/toastSelection.test.ts` | `Test Files 1 passed, Tests 5 passed` |
| three routine then one Critical → Critical visible, one routine behind the count; the same set pushed in reverse order gives the same visible set | same run | `three routine then one Critical...`, `the same set pushed in reverse order gives the same visible set (order independence)` both pass |

`Toasts.tsx` now calls `selectVisibleToasts` instead of `toasts.slice(-VISIBLE_CAP).reverse()` — the
selection reads the WHOLE stack (not just its tail), so a Critical buried behind `cap` routine
toasts still surfaces. Mutation-feedback toasts (`mutationFeedback.ts`) carry no `severity` and
count as routine, unchanged.

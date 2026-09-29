# EP1.5 — The FE's `runAutoAssign` calls `/suggest`; delete the TypeScript fill mirror (W1)

Spec: docs/architecture/empire-progression/spec-assign-ladder.md

| Criterion | Command | Result |
|---|---|---|
| `runAutoAssign.ts` calls the route and computes no share | `npm test -- --run aptitude` (gk-web/web/fusion-rpg-web) | pass — `runAutoAssign.test.ts`, 3 new tests, asserts the exact POST body and that every `setValue` write is the response's `draftShares` verbatim |
| `autoAssign.ts` keeps only its types and `APTITUDE_IDS`; the mirror's own unit tests removed with it | same run | `fillEven`/`fillPosture`/`fillFromPermille`/`fillAutoAssign` deleted; `autoAssign.test.ts` now asserts only `APTITUDE_IDS` and `applyAutoAssignShares` (which stays — it writes a draft, computes nothing) |
| A vitest asserts the route is called and no share arithmetic runs in the FE | same run | pass — `calls the route with scope/scopeKey/rule and applies draftShares verbatim` |
| Build green | `npm run build` | tsc --noEmit + vite build succeed; `npm run check:bundle` — Phaser absent from entry chunk |
| Full suite | `npm test -- --run aptitude` | 8 test files, 28 tests, all pass |

## Notes

- `RunAutoAssignArgs` drops `budget` and `speciesId` as **required** reads (the server now resolves its
  own budget via `ResolveBudget` and its own species via `scopeKey`) but keeps them as optional,
  `@deprecated`-marked fields so the two existing callers (`AptitudesTab.tsx`, `SpeciesBuildPanel.tsx`
  — not in this task's file list) do not need editing in this change; their object literals still
  typecheck unchanged.
- Added `suggestAptitudePreset` to `gk-web/web/fusion-rpg-web/src/lib/bus/aptitudePresets.ts` (`POST
  /api/aptitude-presets/suggest`), following the file's existing `sendJson` style.
- `runAutoAssign` always sends a concrete `rule` today (the bus event `aptitude.autoAssign { rule }`
  already always carries one) — the endpoint's "rule omitted" walk path is exercised by the Server
  tests (EP1.4) and will be reached by the FE once `auto-assign-control` (EP1.19/EP1.20) builds a
  "suggest a build" control that omits it.

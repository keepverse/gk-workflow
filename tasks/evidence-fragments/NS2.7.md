# NS2.7 — Coverage guard over the live catalog

| Criterion | Command | Result |
|---|---|---|
| every catalog category + `messageKeys` gets non-empty `samples()`, every sample renders non-fallback; loops the catalog at test time, no pinned number; green over the empty v1 catalog | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/format/coverageGuard.test.ts` | `Test Files 1 passed`, `1 passed` (`is green over the empty v1 catalog` - zero dynamic cases exist today because `categories: []`; the `for` loop itself, not a count, is the guard) |
| whole `shell/notify` suite + build | `npx vitest run src/shell/notify`; `npm run build` | `Test Files 4 passed`, `14 passed`; `✓ built in 8.92s` |

Closes wave 2's web half: `notify-format`'s kit/contract/registry/fallback/coverage-guard exist with
no domain vocabulary anywhere in `shell/notify/format/` except `translators.ts`'s own (currently
empty) import list.

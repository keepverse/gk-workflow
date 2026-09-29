# NS2.6 — Translator registry, `renderNotification` and the designed fallback

| Criterion | Command | Result |
|---|---|---|
| `registerTranslator`/`translatorFor`; `translators.ts` is the one import-list index (empty in v1, no logic); `renderNotification` is the only render entry point | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/format/render.test.ts` | `Test Files 1 passed`, `4 passed` |
| an unknown domain or a `null` translation renders `categoryName` + neutral body (never the id) and logs once in development | same run | `an unknown domain renders categoryName + a neutral body...`, `a translator returning null also falls back...`, `logs once in development for a repeated unknown category` all green |
| a registered translator's real answer is used, not the fallback | same run | `a registered translator's real answer is used, not the fallback` green (catalog's `domainOf` mocked, since v1's catalog is empty and has no real domain to resolve yet) |

`translators.ts` currently exports nothing (`export {}`) - both `world-notify-source` (NS5.4) and
`cache-notify-source` (NS6.3) add their one import line here when their catalog rows land.

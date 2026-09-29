# NS2.5 — Format kit and translator contract (R-N3, primitives first)

| Criterion | Command | Result |
|---|---|---|
| `NotifyTranslator`/`NotifyText`/`NotifyTarget`; kit primitives `magnitude`/`count`/`turn`/`turnsFrom`/`ref`/`categoryName`; no `domainToken` primitive | `cd web\fusion-rpg-web; npx vitest run src/shell/notify/format/kit.test.ts` | `Test Files 1 passed`, `6 passed` |
| kind set read from the vocabulary union - a new kind with no primitive fails | `npm run build` | `✓ built in 8.92s` - `NOTIFY_ARG_KIND_PRIMITIVE`'s `satisfies Record<Exclude<NotifyArgKind,"domainToken">,...>` makes this a compile-time failure, not a runtime one |
| an unresolvable `ref` renders `Pending`, output never contains the id | same vitest run | `an unresolvable ref renders Pending, never the raw id (GG-23/GG-62)` green |

`fmt.magnitude`/`fmt.count` route through the web's one number formatter (`i18n/magnitude.ts`,
zero new formatting code); a kind mismatch (e.g. calling `.magnitude` on a `count` arg) throws
rather than silently misreading the value.

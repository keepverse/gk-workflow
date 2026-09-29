# EP1.11 — FE: quote before Confirm; send a fresh `correlationId` when the change is a respec

Spec: docs/architecture/empire-progression/spec-specimen-respec-price.md

| Criterion | Command | Result |
|---|---|---|
| On confirm the sheet calls `respec-quote`; when `isRespec` is true it shows the soul price before saving and sends a new `correlationId` | `cd web\fusion-rpg-web; npm test -- --run aptitude` | pass (28/28, 8 files) |
| The FE never decides "is this a respec" and never computes a price | code review — `AptitudesTab.tsx`'s `onSave` reads `quote.isRespec`/`quote.soulPrice` only from the server response; no local comparison against `serverValues`/budget decides pricing | n/a (structural) |
| `npm run build` (tsc --noEmit + vite build) | `cd web\fusion-rpg-web; npm run build` | pass, 0 type errors |

## Notes

- `useAptitudeRespecQuote()` (new, `mutations.ts`) is deliberately a `useMutation`, never a
  `useQuery` — same reasoning `usePreviewTree`'s own comment already gives: the call is read-only
  server-side but triggered by an explicit player action (Confirm), not by data the sheet
  subscribes to.
- `AptitudesTab.tsx`'s `onSave` (both the commander and unique branches) now: (1) calls
  `respecQuote.mutateAsync({scope, playerId|instanceId, shares: draft})`; (2) if `isRespec`, pushes a
  `warn`-tone toast naming `soulPrice` and mints `newCorrelationId()`; (3) calls
  `saveCommander`/`saveUnique` with that `correlationId` (`undefined` when not a respec, so the
  server's own free path is untouched).
- `AptitudesState`/`UniqueAptitudesState` gained an additive `AptitudeReallocationFields` (`priced?`,
  `priceAmount?`, `respecCount?`, `soulBalance?`) — present on the POST response, absent on GET,
  matching the server's own additive JSON-merge (`AptitudeEndpoints.WithReallocation`).
- `useSaveAptitudes`/`useSaveUniqueAptitudes` gained an optional `correlationId?: string` body field.
- `AptitudesTab.test.tsx`'s `vi.mock("@/lib/bus", ...)` is a full replacement object (no
  `importOriginal`), so it needed `useAptitudeRespecQuote` and `newCorrelationId` added alongside the
  two save mocks or every test in the file throws "No export is defined on the mock" — caught by
  running the suite, not assumed.
- `queries.ts` needed no change: the new quote surface is a mutation, not a query, and the extended
  state types are structurally additive (optional fields), so no existing `useQuery` caller needed
  updating.

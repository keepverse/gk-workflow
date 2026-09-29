# Spec: hall-surface

Module `hall-surface` (map: `docs/architecture/achievement-title-map.md`,
depends on `empire-titles`, `title-lifecycle`). Parent: UI ideal
`achievement-title-ui-ideal.md` (recipes `hall-console.json`, draft
`surfaces/hall-console.html` — both shipped in T7a).
Reading gate (this session): DESIGN-GATE UI + Player-menus rows,
`game-gui-principles.md`, `gui-lego-ideal.md` (ERM rungs), `gui-lego-map.md`,
`idea-ui-phase.md`, `html-design-implementation.md`, `actor-hud-ideal.md` §4.1
(hudToken), `foldDerivedSurfaceVm.ts` + `derivedSurfaceBus.ts` +
`bindSurface.ts` + `RecipeMount.tsx` + `DerivedTab.tsx` (mount pattern),
`achievement-titles-catalog.v1.json` (copy source).

## Objective

Mount the Empire Achievement Hall: trophy wall + 3-slot doctrine table as a
layer over the empire stage. Users: empire players choosing which doctrine to
wear. Success: what the draft shows is what the build shows (side-by-side),
every tap acknowledged with authority-painted truth, no god TSX, no invented
paint or copy.

## Tech Stack

React 19 + Vite + vitest + lingui (repo web stack), TypeScript strict
(`tsc --noEmit` gates `npm run build`). No new dependencies (buy-before-build;
a fat chunk gets code-split, never a hand-rolled fourth gauge).

## Commands

```
Dev: npm run dev --workspace=gk-web/web/fusion-rpg-web (vite 127.0.0.1:5173)
Test: npm test --workspace=gk-web/web/fusion-rpg-web -- foldHallSurfaceVm hallSurfaceBus hallMount
Build: npm run build --workspace=gk-web/web/fusion-rpg-web (tsc --noEmit + vite build)
Bundle: npm run check:bundle --workspace=gk-web/web/fusion-rpg-web (Phaser/recharts stay off entry chunk)
```

## Project Structure

```
web/fusion-rpg-web/src/features/gui-lego/foldHallSurfaceVm.ts (+ .test.ts) → pure fold (mirror foldDerivedSurfaceVm: XxxUiState + XxxSurfaceVmInput + foldXxxSurfaceVm)
web/fusion-rpg-web/src/features/gui-lego/hallSurfaceBus.ts (+ .test.ts) → closed event union + const array + create + bind (mirror derivedSurfaceBus)
web/fusion-rpg-web/src/ui/gui-lego/pieces/titles.tsx (+ .test.tsx) → title-card (Card rung), title-slot-row (Row), curse-row (Row), hall-slot-list (layout) factories
web/fusion-rpg-web/src/ui/panel/HallConsole.tsx (+ .test.tsx) → fold → bindSurface → RecipeMount host (mirror DerivedTab)
web/fusion-rpg-web/src/ui/panel/HallConsole.css → ported from surfaces/hall-console.html <style>, scoped under .hall-console root
```

## Code Style

```tsx
// Fold → bind → mount. Pieces never fetch; the fold owns copy from the catalog.
import { bindSurface } from "@/features/gui-lego/bindSurface";
import { createHallSurfaceBus } from "@/features/gui-lego/hallSurfaceBus";
import { foldHallSurfaceVm } from "@/features/gui-lego/foldHallSurfaceVm";
import { getRecipe } from "@/features/gui-lego/recipeRegistry";
import { RecipeMount } from "@/ui/gui-lego/RecipeMount";

const vm = foldHallSurfaceVm({ slots, titles, catalog, search });
// Upstream mapping (folds invent no inputs): slots ← Hall bindings read
// (effect_binding slot hall-{1,2,3}); titles ← unlock ledger + grant bindings;
// catalog ← achievement-titles-catalog rows; search ← local query state.
// wornContainerId never appears here (actor-tab surface only).
const plan = bindSurface(getRecipe("hall-console"), vm);
return <RecipeMount plan={plan} bus={asSurfaceBusLike(createHallSurfaceBus())} />;
```

Naming: `foldHallSurfaceVm`, `HallSurfaceEvent` (`hall.*` prefix), `HallConsole`.
New pieces declare ERM rungs (title-card Card, rows Row, hall-slot-list layout);
themeRefs resolve through `themeRegistry` (element/status packs + `paint` hex —
 Themes own paint; no private title colors, no `fill=var()` without hex).

## Testing Strategy

vitest (`npm test`): fold unit tests (slots, teaser `???`, curse disabled-with-
reason, expiry copy with destination, preview-never-mutates); bus contract tests
(closed union exhaustive); mount landmark tests (slots/chips/inspect render from
`hall-console.json` via `bindSurface`, mirroring `RecipeMount.test.tsx`); catalog
copy tests (no dotted ids, no engine words on surface). Coverage: branches of the
fold's state machine (empty/loading/error/teaser/equipped/expired).

Bus exhaustiveness: array↔union test (every `HallSurfaceEvent` in
`HALL_SURFACE_EVENTS` and back — an event without a counterpart fails).
Ownership: `registerTitlePieces()` lives here; a second distinct factory for
any of the 4 ids throws (duplicate-registration test). Mount refusal: mounting
outside PanelShell throws/skips (host test).

## Mutation contracts (GG-15 — one row per mutation, no blanket)

| Mutation | Ack (one frame) | Authority (paints only on) | Reversal |
|---|---|---|---|
| Equip into slot | press/`equipping…` | server confirm | failed confirm repaints prior slot + names cause |
| Unequip-all | press/`clearing…` | server confirm | confirm dialog first (destructive); failed confirm repaints |
| Ritual begin | press/`sending…` | spend-log outcome | insufficient → disabled naming need + source (GG-55); failed ritual paints player-words reversal |

Preview (candidate inspect) never mutates — no contract needed, proven by
preview-then-read-back-equal test.

## Per-case honesty copy (GG-54/GG-55)

Expired title: "back to Hall, re-equippable" (+ Hall-full path naming the
overflow victim slot). Curse CTA disabled reasons from catalog `lockReason`
("needs 500 souls and 50 fire essence" — never generated). Hidden teaser shows
`teaser` + lock reason, never tier placement. Failed apply repaints prior state
with the server reason in player words.

## Tunables & Catalogs

Copy only from `gk-core/data/tuning/achievement-titles-catalog.v1.json`
(displayName/reading/hudToken/flavor/teaser/lockReason); numbers only from
`achievement-titles.v{n}.json` via the intent API (never recomputed in FE).
`hudToken` here is a catalog string consumed by `title-card` (single glyph),
not the actor-hud token registry (status/element catalogs own that system).
Presentation constants (search debounce) are local with a comment, never
balance dials. Lists virtualize, never truncate — no row caps.

## ActorHub Gate

**Consume Hub output only.** The Hall reads empire bindings, the unlock ledger,
catalog rows, and economy intent numbers through `lib/bus` hooks; it never
composes, folds, or writes an actor number (actor snapshots are out of scope —
empire magnitudes never enter ActorHub). Equip intent goes through the existing
server path (same as the tested store APIs), never a client-side fold.

## Numeric Types

Display cooking per GG-46 (spec-magnitude-and-units R1 divide-by-10, one decimal,
trim trailing `.0` — `4‰→0.4%`, `150‰→15%`; R2 round away-from-zero):
per-mille shares → one-decimal %; `validTurns` renders as plain integer turns
("12 turns left" — never ms, never a unit the ledger doesn't carry); ritual
prices in stock units (souls/essence counts). Renderer refuses bare numbers
(no unit inference in components). `long` ids stay strings across the JSON
boundary (no precision loss).

## Boundaries

- Always: recipe + fold + bus, never a god TSX; mount inside PanelShell (never
  fork shells); pieces never fetch; side-by-side draft screenshots before done;
  `verify-change.ps1 -Paths` + vitest + build before commit.
- Ask first: `panel-rail` host mount wiring (gui-lego owns shells); queue row
  placement; title-rarity pack; any new piece beyond the 4 named.
- Never: sibling `/hall` route (GG-1 — layers, not pages); Tailwind mood-board
  over the locked draft; engine vocab or dotted ids on surface; second badge/
  palette kit (ERM/pack extension or nothing); catalog counts asserted in tests.

## Success Criteria

- [ ] Draft-vs-SPA side-by-side screenshots (same viewport) + current wwwroot/vite + owner confirm (html-design-implementation — owner confirm alone never closes it).
- [ ] Equip/compare/expire/ritual flows work on the mount under the mutation table above.
- [ ] `npm test` (new suites) + `npm run build` + `check:bundle` green.

## Open Questions

No new questions beyond UI-ideal OQ1–OQ4 (queue placement, Hall host,
rarity pack, worn-display confirm — owner decisions, Ask-first rows above).
Queue/host/pack ride PR confirmations, not this spec.

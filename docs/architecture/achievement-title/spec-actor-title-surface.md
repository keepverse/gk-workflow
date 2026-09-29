# Spec: actor-title-surface

Module `actor-title-surface` (map: `docs/architecture/achievement-title-map.md`,
depends on `actor-titles`, `title-lifecycle`). Parent: UI ideal
`achievement-title-ui-ideal.md` (recipe `actor-title-tab.json`, draft
`surfaces/actor-title-tab.html` — both shipped in T7a). Shares the 4 piece
factories with `hall-surface` (built there — this module consumes, never forks).
Reading gate (this session): same UI/menus rows as `spec-hall-surface.md`, plus
`actor-sheet-ideal.md` (8-tab grammar, ninth-kind migration, load-reject rule),
`ui/actor/DerivedTab.tsx` (tab mount pattern), `actor-hud-ideal.md` §4.1.

## Objective

Mount the specimen honors sash as the ninth ActorPanel tab: equipped titles,
one worn name (highest-tier wins, stacking underneath), unwearable marks with
their lifting price. Users: roster/commander players. Success: sheet, HUD, and
telemetry agree on what is worn (one selector upstream); the tab never shows a
ninth kind the grammar doesn't know.

## Tech Stack

Same as `hall-surface` (React 19 + Vite + vitest + lingui, strict TS). No new
dependencies.

## Commands

```
Dev: npm run dev --workspace=gk-web/web/fusion-rpg-web (vite 127.0.0.1:5173)
Test: npm test --workspace=gk-web/web/fusion-rpg-web -- foldActorTitlesVm actorTitleBus actorTitleMount
Build: npm run build --workspace=gk-web/web/fusion-rpg-web (tsc --noEmit + vite build)
Bundle: npm run check:bundle --workspace=gk-web/web/fusion-rpg-web
```

## Project Structure

```
web/fusion-rpg-web/src/features/gui-lego/foldActorTitlesVm.ts (+ .test.ts) → pure fold (mirror foldDerivedSurfaceVm)
web/fusion-rpg-web/src/features/gui-lego/actorTitleBus.ts (+ .test.ts) → closed event union + const array + create + bind
web/fusion-rpg-web/src/ui/actor/ActorTitleTab.tsx (+ .test.tsx) → fold → bindSurface → RecipeMount in ActorPanel (mirror DerivedTab)
web/fusion-rpg-web/src/ui/actor/ActorTitleTab.css → ported from surfaces/actor-title-tab.html <style>, scoped under .actor-titles root
```

Piece factories (`title-card`, `title-slot-row`, `curse-row`) ship in
`hall-surface` (`ui/gui-lego/pieces/titles.tsx`); this module imports them.
A second copy is a defect.

## Code Style

```tsx
// Ninth tab: same host, same grammar. Unknown tab kind load-rejects per the
// sheet contract — this tab mounts only after the tab-grammar migration lands
// (Ask-first actor-sheet); until then the recipe + draft stand without a mount.
import { bindSurface } from "@/features/gui-lego/bindSurface";
import { getRecipe } from "@/features/gui-lego/recipeRegistry";

const vm = foldActorTitlesVm({ bindings, wornContainerId, catalog, lifecycle });
// Upstream mapping (folds invent no inputs): bindings ← title-slot bindings read
// (effect_binding slot title-{1,2,3}); wornContainerId ← shared TitleWornSelector
// (never recomputed here); catalog ← achievement-titles-catalog rows;
// lifecycle ← lifecycle ledger rows (windows/expires/curses for destinations).
const plan = bindSurface(getRecipe("actor-title-tab"), vm);
return <RecipeMount plan={plan} bus={asSurfaceBusLike(createActorTitleBus())} />;
```

ActorTitle events use the `title.*` prefix (`title.search.set`,
`title.slot.select`, `title.preview`, `title.ritual.begin`, `title.retry`)
as a closed union + const array (bus exhaustiveness tested both directions).
Worn display renders the single `wornContainerId` from the shared selector —
never a local max-tier recompute (one owner of worn truth). Equip/ritual
intents go through the existing server path; bus events never mutate bindings
client-side.

## Testing Strategy

vitest: fold tests (worn agreement with store selector fixtures, teaser/lock
copy, curse CTA states incl. disabled-with-reason, expiry destinations);
bus contract tests; mount landmark tests via `bindSurface` on
`actor-title-tab.json`; tab-grammar test (ninth kind absent → load reject,
present + renderer → mounts). No sheet/HUD/telemetry triple test here — the
selector agreement is proven upstream (TitleHubReachTests); this module proves
it renders the agreed value.

## Tunables & Catalogs

Same catalog/numbers split as `hall-surface` (catalog copy, intent numbers).
No tab-local numbers beyond presentation constants with comments.

## ActorHub Gate

**Consume Hub output only.** The tab reads the specimen sheet/derived snapshot
(`useActorSheet`-family hooks) and title bindings; worn comes from the shared
selector. No compose, no fold, no second worn computation.

## Numeric Types

Same cooking table as `hall-surface` (GG-46 R1/R2; plain integer turns;
stock-unit prices; bare-number refusal; `long`-as-string over JSON).

## Boundaries

- Always: recipe + fold + bus; mount inside ActorPanel (never a `#/actor/:id`
  route, never a forked shell); pieces never fetch; no identity header
  (ActorPanel owns who/level); draft side-by-side before done.
- Ask first: ninth-kind tab-grammar migration (actor-sheet owns shell/grammar —
  mount waits on it); queue row; any piece beyond the 3 shared factories
  (plus Hall-only `hall-slot-list`).
- Never: mount the tab while the grammar still closes at 8 (load-reject rule);
  second worn computation; engine vocab or dotted ids; god TSX.

## Success Criteria

- [ ] Tab mounts after the grammar migration; rejects before it (both tested).
- [ ] Worn name matches the store selector on shared fixtures; marks show price + disabled reasons.
- [ ] `npm test` + `npm run build` + `check:bundle` green; draft side-by-side
  screenshots (same viewport) + current wwwroot/vite + owner confirm.

## Open Questions

No new questions beyond UI-ideal OQ1–OQ4; host, worn rule, and
presets-deferred stand decided, with Ask-first PR confirmations.

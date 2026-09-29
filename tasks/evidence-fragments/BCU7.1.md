# BCU7.1 — delete orphaned GearTab.tsx, note ProgressionTab collision

Confirmed orphaned before deleting: zero non-test importers, no barrel export, ActorPanel.tsx uses
KitTab (CatalogTabs.tsx) for its "kit" slot, not GearTab. Deleted GearTab.tsx + GearTab.test.tsx.

Added naming-collision comment to ProgressionTab.tsx: not the tab ActorPanel.tsx renders (that's
AptitudesTab) — ProgressionTab is used only by the standalone AptitudesPage.tsx.

Verification-boundary gap found and reported (not self-fixed): no mapping exists for
gk-web/web/fusion-rpg-web/src/ui/actor/** in verification-boundaries.v1.json (owned by
test-verification-boundary).

```
$ npx vitest run src/ui/actor/
Test Files 22 passed (22), Tests 259 passed (259)
$ npm run build
built in 13.31s (tsc --noEmit + vite build)
```

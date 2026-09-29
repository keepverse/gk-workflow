# Actor HUD element icons — V2 tasks

Visual SSOT: `docs/design/11-actor-hud-v2.html`.

- [x] V1: Extend the snapshot and wire contract with 0–2 element ids.
- [x] V1: Publish catalog v2 with six minimal glyph declarations and authored sprite assets.
- [x] V1: Add Unity's original detached packed glyph row and verify injector deployment.

## V2.1 — Geometry and injection

- [x] Publish `actor-hud.v6.json` with named 24px primary, 20px secondary, and identity-gap keys.
  - Acceptance: Core rejects missing/non-positive V2 geometry; Injector and Server load v6.
  - Verify: focused `ActorHudTuningLoader` and `ActorHudHostInjection` tests.
  - Files: Core tuning parser/tests; RpgHost; v6 tuning; host guard.

## V2.2 — Unity identity-line pack

- [x] Make one measured and centred Unity identity line containing tier, role, level, primary, and optional secondary.
  - Acceptance: elements no longer claim their own vertical row; absent slots consume no space; V2 geometry drives icon sizes.
  - Verify: Actor HUD Unity guard plus live dual-element lawn screenshot.
  - Files: `ActorHudPool`, `ActorHudRowIdentity`, `ActorHudRowElements`, Unity guard tests.

## V2.3 — Web presentation contract

- [x] Add injected V2 HUD geometry to the existing actor-surface payload and preserve `elements` through the Web DTO, fold, projection routes, equality comparison, and golden fixture.
  - Acceptance: Web never owns a numeric mirror; valid primary/secondary reach `Occupant.hud`; malformed slots are omitted; element changes repaint.
  - Verify: focused fold and lawn-projector Vitest suites.
  - Files: lawn view model, fold, fold tests, projector fixture/tests.

## V2.4 — Web identity glyph paint

- [x] Expose `hudGlyph` through actor-surface TypeScript and add a verified public mirror of the six authored assets.
  - Acceptance: no hardcoded element switch or unserved Injector-relative URL.
  - Verify: asset-manifest/hash test and Web build.
  - Files: actor-surface types, public asset mirror/manifest, mirror test/guard.

- [x] Render the identity pack in Phaser and Inspector using catalog glyphs and accessible labels.
  - Acceptance: one/two/zero element variants match plate 11 slot order; unknown art hides only its glyph.
  - Verify: ActorHudDisplay and Inspector tests; `npm run build`.
  - Files: ActorHudDisplay, tokens/resolver, Inspector, focused tests.

## V2.5 — End-to-end proof

- [x] Extend golden/E2E coverage and capture Unity + Web evidence against plate 11.
  - Acceptance: both lawn renderers show the same slots in the same order; no overlap with resources/statuses.
  - Verify: scoped verification, Playwright Actor HUD E2E, game screenshot comparison, Injector/Web builds.
  - Files: golden fixture, E2E, relevant visual tests only.

## V2.6 — Live-legibility correction

- [x] Publish `actor-hud.v7.json` with a 36px primary glyph, 30px secondary glyph, and 4.5px identity gap.
  - Acceptance: both hosts load v7; actor-surface sends the same geometry to Web; the live Unity image
    makes the ordered glyphs visibly larger than the level badge without a second row or overlap.
  - Verify: focused tuning/catalog/host tests, scoped verification, build/deploy, live Unity screenshot.
  - Files: v7 tuning, injector/server host wiring, focused tests, plan/todo/specs.
  - Evidence: 2026-09-25 dedicated 4.0 MelonLoader lawn capture `actor-hud-v7-live-proof` rendered an
    elemental Peashooter and Normal Zombie with the v7 identity line; the owner accepted the larger glyph.

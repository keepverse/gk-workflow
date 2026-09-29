# Actor HUD element icons — V2 implementation plan

## Objective

Implement the approved V2 presentation plate: a compact, bottom-centred three-row Actor HUD where
the level and one or two element glyphs form one measured, centred identity line. Unity lawn,
Web/Phaser lawn, and the selected-unit inspector consume the existing `ActorHudSnapshot` /
`Occupant.hud` chain; no new endpoint, element resolver, or HUD compose path is introduced.

Visual SSOT: [11-actor-hud-v2.html](../docs/design/11-actor-hud-v2.html). The older plate 10 is
historical only where it disagrees.

## Current-state evidence

- Core already carries `ActorHudElements` and `ActorHudWireSerializer` emits `elements`.
- Unity `ActorHudPool` renders `ActorHudRowElements` first as a standalone 16px row, then advances
  the vertical cursor before identity.
- Web `ActorHudSnapshot` and `foldActorHud` currently omit `elements`; Phaser consequently draws
  tier/level/role only, and Inspector has no elemental identity glyphs.
- The injected actor-surface catalog already exposes element id, display name, colour, and `hudGlyph`
  from Core, but the TypeScript `ElementCatalogRow` has not retained `hudGlyph`.

## Decisions

1. **One data path:** preserve the existing Core wire → `foldActorHud` → `Occupant.hud` path. Neither
   renderer reads species data or recomputes typing.
2. **One layout contract:** `tier? → role? → level? → primary? → secondary?`, centred as one pack.
   Absent slots reserve neither width nor height. Resources and statuses follow below only when present.
3. **Named geometry:** publish `actor-hud.v7.json` through `gk-core/tools/tuning/publish.py` with 36px primary,
   30px secondary, and an explicit identity-line gap. This supersedes v6 after live evidence showed
   its artwork did not read at the intended size. Injector and Server load the same version; the
   existing actor-surface response carries a small `hudPresentation` DTO to the Web. The parser rejects
   missing values; no code default or 80% multiplier remains.
4. **One art source:** retain the Injector icon directory as the authored source. Add a Web public
   mirror plus checksum guard/manifest so Phaser and Inspector show the same six assets without a
   hand-maintained element switch or an unserved cross-project import.
5. **Performance unchanged:** no new actor walk, resolver, network request, or per-frame data build.
   The existing HUD on/off switch and sync budget remain the performance boundary.

## Dependency order

```text
V2.1 geometry + host injection
  └─ V2.2 Unity identity-line pack
       └─ V2.3 Web DTO/fold/catalog preservation
            └─ V2.4 Web asset mirror + Phaser/Inspector paint
                 └─ V2.5 contract, browser, and live-lawn verification
                      └─ V2.6 live-legibility correction and re-verification
```

## Tasks

### V2.1 — Publish identity-line geometry

Replace detached-row tuning with named primary, secondary, and identity-gap screen-pixel fields;
publish v6, point both composition roots at it, and extend loader/host tests.

**Acceptance:** malformed or missing V2 geometry rejects; the host loads v6; no presentation number is
left as a hidden multiplier.

**Verification:** `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ActorHudTuningLoader`; `dotnet test
gk-core/tests/FusionRpg.Guard.Tests --filter ActorHudHostInjection`.

### V2.2 — Compose the Unity identity line

Move element placement into the measured identity pack. `ActorHudRowElements` retains catalog-to-sprite
resolution only; `ActorHudRowIdentity` owns the single centring calculation and `ActorHudPool` advances
the cursor once after the identity line.

**Acceptance:** a single element, dual element, and no-element actor all centre the complete pack;
identity does not move farther from the sprite when no resource/status row exists; primary/secondary
use V2 tuning.

**Verification:** focused Unity guard tests plus a live lawn screenshot containing a dual-element actor.

### V2.3 — Preserve the Web presentation contract

Extend the existing actor-surface response with injected `hudPresentation` geometry, then extend the
Web HUD DTO, pure fold, equality comparison, golden fixture, and projection tests so valid `elements`
survive every supported observe route. Malformed element shape omits only the element slots (not an
invented species typing).

**Acceptance:** the Web gets V2 geometry from the existing actor-surface payload; `entity.stats`,
`debug.board-stats`, and `debug.actor-hud` all produce matching `Occupant.hud.elements`; a
primary/secondary update is not deduped away.

**Verification:** `npm test -- --run src/features/lawn/foldActorHud.test.ts src/features/lawn/lawnProjectorFold.test.ts`.

### V2.4 — Paint the common Web identity line

Expose catalog `hudGlyph` to TypeScript, serve the six authored PNGs through a checksum-verified Web
mirror, and render the same ordered identity pack in Phaser and Inspector. Missing art/catalog rows
hide that glyph with no fallback id text.

**Acceptance:** Phaser exposes named primary and optional secondary identity children; Inspector shows
the same ordered icons with accessible element names; source and public mirror hashes match.

**Verification:** focused ActorHudDisplay/Inspector tests and `npm run build`.

### V2.5 — End-to-end proof and deploy

Extend the shared golden/E2E assertions for single, dual, and neutral actors. Verify the V2 plate
against a lawn screenshot at the target game resolution, then build both Injector and Web and deploy
only after the owner supplies a valid game-copy path.

**Acceptance:** Unity and Web agree on slot order and one/two/zero visibility; no browser console
errors; HUD is legible under a live sprite and does not overlap the next optional row.

**Verification:** scoped `verify-change.ps1` per changed path, `npm run build`, focused C# tests,
Playwright Actor HUD E2E, then a manual live screenshot comparison to plate 11.

### V2.6 — Live-legibility correction

The live Unity frame showed the 24px/20px v6 icon boxes were not visually prominent beside the level
badge. Publish v7 with a 36px primary, 30px secondary, and 4.5px identity gap; load it in both hosts
and prove the actual engine image still keeps the centred line clear of the next row.

**Acceptance:** primary and secondary glyphs are visibly larger than their neighbouring level badge,
remain ordered primary then secondary, and preserve the existing single-line centring contract.

**Verification:** v7 tuning/actor-surface/host tests, scoped verification, build/deploy, and a fresh
live Unity screenshot containing at least one elemental actor.

**Result (2026-09-25):** focused V7 tests and builds passed; the dedicated 4.0 MelonLoader live lawn
capture `actor-hud-v7-live-proof` rendered elemental plant and zombie identity packs without a detached
element row. The owner accepted the larger glyph presentation.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Web art diverges from Injector | Public mirror manifest records source hash; a focused guard fails drift. |
| Tunable bump changes host without test coverage | Loader and host-injection tests land with V2.1. |
| Identity pack overflows narrow sprites | Pack is centred and bounded by existing HUD width; low-priority slots follow current crowd policy, never shrink glyphs below V2 size. |
| HUD work regresses frame cost | No new actor iteration; verify `vfx.tick` using the existing enabled/budget controls in the live screenshot phase. |

## Boundaries

- Always: use catalog `hudGlyph` and the existing snapshot/fold; preserve screen-silhouette anchor;
  run the path-owned verification command for every code change.
- Ask first: add a new element glyph or deploy to a different game path. The owner approved this V2
  visual-scale correction on 2026-09-25.
- Never: add direct species reads in a renderer, duplicate element maps, create a second HUD endpoint,
  use a UnitFrame/VFX world anchor, or commit game binaries/dist output.

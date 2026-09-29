# Spec: `actor-hud-screen-anchor`

**Program:** `actor-hud` · **Scope:** Unity Band B placement only. It does not change HUD content,
Phaser, Inspector, combat, or VFX world placement.

## Decision

Plant and zombie art has no stable relation between an actor root/Body anchor and visible feet.
Child sprite scale, pivot, flip, and composite visuals make a world-coordinate offset wrong by
construction. Unity HUD placement is therefore screen-space presentation.

For each actor, union qualifying child `SpriteRenderer` projections into `(left, bottom, width,
height)`. The anchor is `centerX = left + width / 2`, `topY = bottom - screenGapPixels`, and
`width = clamp(width * screenWidthFactor, screenMinWidthPixels, screenMaxWidthPixels)`. The HUD root
has top-centre pivot and all rows have non-positive local Y, so content cannot grow into the sprite.

## Contract

- `ActorVisualResolver` caches one sprite-union rectangle per actor per frame from real Unity state.
- `LawnCameraResolver` selects an enabled active camera that renders the actor layer and contains its
  root projection; it does not use a tag lookup.
- `ActorScreenAnchorResolver` delegates the geometry rule to Unity-free
  `ActorHudScreenAnchorMath.TryResolve`.
- Failure to resolve visual/camera omits the actor for that frame; no world-position guess or stale
  anchor is reused.
- `ActorHudPool` uses a pooled `ScreenSpaceOverlay` Canvas and reads cached snapshots only. It never
  reads Shield/Status runtime data directly.

## Tuning

`actor-hud.v4.json` sets `screenGapPixels`, `screenWidthFactor`, min/max screen width,
`screenRowGapPixels`, and `screenResourceHeightPixels`. They are published through
`gk-core/tools/tuning/publish.py actor-hud <key>=<value>`. v4 sets zero gap and a 1.5× width scale; invisible
rows do not reserve vertical space. Legacy world fields remain
backward-parse-only and v3 rendering does not consume them.

## Verification

Core tests cover anchor centre/gap/width. Guard tests protect silhouette, camera, Canvas, and
snapshot boundaries. Target-host build plus live plant/zombie/composite evidence is required.

# Spec: `actor-hud-unity`

**Module id:** `actor-hud-unity` · **Program:** [../actor-hud-map.md](../actor-hud-map.md) ·
**Ideal:** [../actor-hud-ideal.md](../actor-hud-ideal.md) ·
**Pipeline:** [../../research/actor-hud-data-pipeline-audit-2026-08-30.md](../../research/actor-hud-data-pipeline-audit-2026-08-30.md)
**Depends on:** `actor-hud-core`, `actor-hud-dump` · **Blocks:** `shield-slot-migration`
**Status:** implemented 2026-08-31 — placement superseded 2026-09-17 by
[spec-actor-hud-screen-anchor.md](spec-actor-hud-screen-anchor.md).

---

## Assumptions

1. **Screen silhouette SSOT** — placement is the union of projected qualifying actor sprites, with a
   pixel gap below its bottom-centre. `UnitFrameResolver` stays VFX-only; this presenter has no
   world-coordinate offset.
2. **Shield row** reuses segment grammar from the retired ShieldBarPool — element-colored segments +
   **stack pips** mandatory; bar W/H from `actor-hud` tuning (not live `vfx.v3` `render.shieldBar`).
3. **Identity-line elements** use the snapshot's concrete primary element and optional secondary element;
   catalog **`hudGlyph`** + authored **`color`** choose the minimal visual, not a species-specific switch.
   They pack with tier/role/level as one centered row; the V2 live-legibility tuning sets primary at 36px and secondary at 30px.
4. **Status row** uses TextMesh (or equivalent) glyphs from catalog **`hudToken`** + authored
   **`color`** (ideal §4.1) — not sustain VFX duplication, not `StatusInitials(id)`, not hashed RGB.
   Until H2 wires catalog resolve, may show a designed placeholder; must not re-document initials as
   SSOT. Display resolve shared with Phaser via Core.
5. **Identity row** draws **tier letter + level digits** (not blank colored quads).
6. **Coexist with VfxDirector** — sustain auras remain on body/feet/crown; the HUD root is a
   top-centred screen anchor and its rows stack downward from the sprite.
6. **Sync source:** read `ActorHudBuilder` / `ActorHudCache` output only — **no direct `ShieldRuntime`,
   `StatusRuntime`, or derived re-resolve in render path**. Builder owns gather; pool owns draw
   ([pipeline audit §5](../../research/actor-hud-data-pipeline-audit-2026-08-30.md)).
8. **F9** mutes shield resource row only.

---

## Objective

Render four-row Band B HUD at **center-bottom** of each unit in Unity screen space from the same
snapshot the web fold uses.

**Success:** LIVE lab board — shielded zombie shows element-colored segments + stack pips + readable
status letters + level digits under the unit (Body+offset); sustain VFX still visible; F9 mute
documented.

---

## Program acceptance share

1. Guard: screen silhouette resolver + eligible camera + Canvas presenter (not UnitFrame/world offset)
2. Manual LIVE: `/lawn/quick-start` + shield + status cheat — owner eyeball matches plate 10 §A (bottom)

Automated mesh tests optional v1; guard is mandatory.

---

## Commands

```powershell
dotnet test tests\FusionRpg.Guard.Tests --filter ActorHud
python gk-fusion/scripts/guard-single-writer.py
python scripts\deploy-play.py --no-server
```

---

## Project structure

| Path | Change |
|------|--------|
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudPool.cs` | screen-space slot pool, top-centred root, pip slots |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorVisualResolver.cs` | sprite-union rectangle and eligible camera |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorScreenAnchorResolver.cs` | adapter to pure Core screen anchor math |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudRowIdentity.cs` | tier letter, level digits, role pip |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudRowElements.cs` | catalog-driven primary/secondary minimal glyphs |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudElementArt.cs` | cached uGUI sprite loading keyed only by catalog `hudGlyph` |
| `gk-fusion/src/FusionRpg.Injector/Assets/actor-hud-elements/` | six transparent 64px icon sprites plus generated-art provenance manifest |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudRowResources.cs` | shield segments + stack pips |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudRowStatuses.cs` | Catalog `hudToken`/`color` resolve + overflow (H2) |
| `gk-fusion/src/FusionRpg.Injector/Hud/ActorHudDirector.cs` | tick sync entry |
| `gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs` | call `ActorHudDirector` on live match path |
| `gk-core/tests/FusionRpg.Guard.Tests/ActorHudUnityGuardTests.cs` | screen placement and snapshot-boundary guards |

---

## Design

### Layout

```text
Projected sprite-union bottom-centre − screenGapPixels
  local Y ≤ 0     — Identity: tier | role | level | primary glyph | optional secondary glyph
  lower local Y   — Resource row: shield track + element segments + stack pips
  lower local Y   — Status strip: catalog hudToken glyphs | +N overflow
```

Screen gap, width bounds, row gap, resource height, and identity-line element geometry are from `actor-hud.v7.json`; hidden rows
do not reserve vertical space.

### Pool mechanics

- Cap on concurrent HUD slots = **96** — **structural** pool buffer (not a balance dial; omit at capacity, no eviction). Not a tuning key.
- Owner key = normalized combat ptr
- Slot lifecycle: acquire on first shield/status/tier signal; release on entity death / board clear
- **HP sliver:** not rendered when `hpSliverEnabled == false`

### V2 implementation seam

`ActorHudRowIdentity` becomes the sole Unity presenter for the identity-line pack. It receives the
existing `ActorHudIdentity`, optional `ActorHudElements`, catalog resolver, and named V2 geometry;
it measures the whole pack before placing tier/role/level/glyph images. `ActorHudRowElements` keeps
catalog-driven sprite resolution, but no longer chooses a row Y or advances the pool cursor. This
keeps centring logic reusable and ensures elements cannot become a detached row again.

### Shield segments

- `ShieldBarColor.Stop` gradient logic
- Max shield segments = **4** — **structural** (segment array length); stack pip count clamped by tunable `maxStackPips`
- Display ratio: `ShieldBarVisual.DisplayRatio` stepped fill

### Status tokens

- TextMesh (or sprite) with catalog `hudToken` + `color` — Core resolve from injected status-catalog
  (H1/H2). Legacy `ActorHudDisplayTokens.StatusInitials` is **not** the SSOT (delete in H3).
- CC corner accent when `cc: true`
- Overflow pip when `overflow.statusCount > 0`

### Element glyph assets

- The catalog's `hudGlyph` is the file key; the presenter never switches on species or element ids.
- Each icon is a transparent, normalized 64×64 uGUI sprite. The V2 geometry is 36px primary and
  30px secondary in the same centered identity pack; a canvas-scale policy may scale both proportionally.
- The generated-art manifest records palette, prompt, normalization, and the catalog mapping. Light
  is a radiant prism and Dark is a fractured void core; neither uses a star or crescent symbol.

### Perf

- Prefer `ActorHudCache` dirty set from dump module
- Full reconcile fallback ≤ once per frame if dirty set non-empty
- `VfxDirector` must still tick HUD on live match when WorldBars is still 0 (no chicken-egg)

---

## Boundaries

- Presentation-only — no `EntityStatWriter` / funnel writes.
- No `BodyWorld` fallback. Raw renderer bounds are restricted to `ActorVisualResolver`, which owns
  the screen silhouette union.
- **No direct runtime reads** — `ActorHudPool` consumes builder/cache snapshot only; same separation as
  fold/Phaser (no parallel shield data path after migration).
- `ShieldBarPool.cs` is deleted — do not reintroduce.

---

## Test plan

| Test | Assert |
|------|--------|
| Guard screen anchor | pool uses silhouette resolver and Canvas; no UnitFrame/world-offset anchor |
| Guard tokens | Core catalog resolve matches Phaser glyphs (same hudToken/color) |
| LIVE eyeball | Bar under unit; statuses readable; level digits visible |

---

## Related

- [spec-unit-frame.md](../vfx/spec-unit-frame.md)
- [spec-shield-slot-migration.md](spec-shield-slot-migration.md)
- [actor-hud-data-pipeline-audit-2026-08-30.md](../../research/actor-hud-data-pipeline-audit-2026-08-30.md)

# Module: `theme-packs-scene`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defects #2/#3, decision 2
**Touches:** `gk-web/web/fusion-rpg-web/src/features/gui-lego/types.ts` (`ThemeKind`),
`gk-web/web/fusion-rpg-web/src/features/gui-lego/themes/*.json`, `themeRegistry.ts`,
`docs/design/gui-lego/themes/packs/*.json`
**Depends on:** gui-lego `theme-packs` taxonomy
**Ask-first:** widening the closed `ThemeKind` union — **this is the module that requires owner sign-off**

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Make scene mood and actor identity **paint owned by packs**, so a second scene or a second cast is
themed by adding data — not by editing component markup.

Today the evidence that this is broken is one line: the speaker label is hard-coded green —
`features/onboarding/RiftPrologueDialog.tsx:185` — `text-ok`. Speaker identity is paint, and a
hard-coded utility class is the same defect as a hard-coded hex.

---

## The constraint that makes this ask-first

`ThemeKind` is a **closed union** —
`features/gui-lego/types.ts:17-27`:

```ts
export type ThemeKind =
  | "element" | "status-category" | "resource" | "action-category"
  | "rarity" | "side" | "cook-tab" | "bucket" | "posture" | "neutral";
```

Forty packs exist across those kinds (`features/gui-lego/themeRegistry.ts:49-90`). **No kind expresses
a person or a scene.** Widening a closed vocabulary is a reviewed change, not a convenience — the
same rule the atom/action vocabularies carry in `DESIGN-GATE.md` §1.

### Recommendation (S2)

**Widen once, with two kinds, and say why:**

```ts
| "actor"   // a story-scene cast member's identity paint (penny, dave)
| "scene"   // a story-scene's mood paint (rift-portal, quarantine, calm)
```

Rejected alternatives, with reasons:

| Alternative | Rejected because |
|---|---|
| Reuse `side` for actors | Penny and Dave are neither plant nor zombie; `side` is a **faction axis** (`side-plant`, `side-zombie`), and `ActorFrame` already proves the tint is faction-shaped (`ui/actor/shared.tsx:45-46`). Overloading it would make "a person" and "a faction" the same vocabulary |
| Reuse `neutral` | `neutral` is the *absence* of a pack (`themeRegistry.ts:93`); every actor would look identical, which is exactly the bug being fixed |
| Skip packs; put hex in the piece | The ban `spec-theme-packs.md:49-51` — *"piece markup containing `--el-fire` / `#e0703c` for element identity"* — is the identical rule for scene identity |
| One `scene` kind that also carries actors | Actor identity is **per-person** and must be distinguishable in the fallback; scene mood is **per-scene**. Merging them would make an actor's paint depend on which scene he stands in |

**If the owner declines the widen**, the fallback design is: actors and scenes use `neutral` plus a
piece-local CSS variable supplied by the *fold* — but that is strictly worse (paint leaves the pack
system) and must be recorded as a conscious deviation.

---

## Contracts

### Actor pack

```json
{
  "themeId": "actor.penny",
  "kind": "actor",
  "id": "penny",
  "css": { "--piece-accent": "var(--act-penny)", "--piece-nameplate": "…" },
  "paint": { "accent": "#6fb7d4", "accentMuted": "#3f7f99", "onAccent": "#07161c" },
  "vfx": { "select": null, "idle": null },
  "glyphDefault": null
}
```

### Scene pack

```json
{
  "themeId": "scene.quarantine",
  "kind": "scene",
  "id": "quarantine",
  "css": { "--scene-bed": "…", "--scene-window": "…" },
  "paint": { "accent": "…", "accentMuted": "…", "onAccent": "…" },
  "vfx": { "select": "vfx.quarantine-seal", "idle": null }
}
```

Both follow `spec-theme-packs.md:20-41` **exactly**: `css` bound as custom properties on the piece
root, `paint` for resolved hex, `vfx` as binder ids. No new channel, no new schema.

### v1 packs

| Pack | Purpose |
|---|---|
| `actor.penny` | Penny's identity: name tag, fallback accent |
| `actor.dave` | Dave's identity: name tag, fallback accent |
| `scene.rift-portal` | Beats 1–2 mood (the portal opening) |
| `scene.quarantine` | Beats 3–4 mood (the seal, the choice) |

Scene mood is **per-beat**, joined from `scene-script`'s `cueId` — so a scene pack is selected by the
scene's state, not by a component prop.

---

## Sync discipline

Design packs are SSOT; the FE holds copies —
`themeRegistry.ts:44-48`: *"FE copies of docs/design/gui-lego/themes/packs — design pack remains SSOT
on conflict. Sync note: re-copy packs when design JSON changes."*

New packs must be added on **both** sides in the same change, and the new imports registered in
`themeRegistry.ts`'s `PACKS` array (`:49-90`). A pack that exists only in the FE is a drift defect.

---

## Success criteria

- [ ] `ThemeKind` widened with `"actor"` and `"scene"` (or the declined-fallback recorded).
- [ ] `actor.penny`, `actor.dave`, `scene.rift-portal`, `scene.quarantine` exist **both** in
      `docs/design/gui-lego/themes/packs/` and in `features/gui-lego/themes/`.
- [ ] All four are registered in `themeRegistry.ts`'s `PACKS`.
- [ ] `themeIdFor` resolves `actor.penny` / `scene.quarantine` correctly (existing generic path).
- [ ] Unknown actor/scene ref falls back to `neutral` (existing `lookupThemePack` behaviour).
- [ ] Penny and Dave packs produce **visibly different** accent paint in the fallback.
- [ ] No piece contains an `actor`/`scene` hex or a `--act-*` literal.
- [ ] A registry test enumerates packs from the registry, **not** a hard-coded count.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run themeRegistry
npm test -- --run theme-bind
npm run build
```

## Boundaries

- **Always:** packs on both sides; register both; fall back to `neutral`; use the existing schema.
- **Ask first:** widening `ThemeKind`; adding a pack kind; changing `paint`'s shape.
- **Never:** piece-local actor/scene hex; a FE-only pack; a hard-coded pack count in a test; a second
  palette outside `_kit` / `src/theme`.

## Project structure

```text
docs/design/gui-lego/themes/packs/actor-penny.json          # design SSOT
docs/design/gui-lego/themes/packs/actor-dave.json
docs/design/gui-lego/themes/packs/scene-rift-portal.json
docs/design/gui-lego/themes/packs/scene-quarantine.json
gk-web/web/fusion-rpg-web/src/features/gui-lego/themes/actor-penny.json   # FE copy
gk-web/web/fusion-rpg-web/src/features/gui-lego/themes/…
gk-web/web/fusion-rpg-web/src/features/gui-lego/themeRegistry.ts         # imports + PACKS
gk-web/web/fusion-rpg-web/src/features/gui-lego/types.ts                 # ThemeKind widen
```

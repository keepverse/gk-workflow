# Module: `piece-contract`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — principles 3/4
**Touches:** conventions only — **no new file of its own**; it constrains every piece module
**Depends on:** —
**Why this module exists (audit gap G3):** the first pass specified eight pieces that each said
"pack owns paint" but **no spec said how a factory applies it**. That is a guaranteed
hard-coded-paint defect at implementation time, so it is fixed once, here.

---

## Objective

State the **shared contract every story-scene piece factory follows**, so eight specs do not each
invent their own paint, DOM, and test conventions — and so a reviewer has one place to check.

This is not a new mechanism. Every rule below is an **existing** gui-lego/`RecipeMount` behaviour the
piece specs must conform to.

---

## 1. Paint: a factory must apply the theme itself

**This is the load-bearing rule.** `RecipeMount.renderNode` applies the pack's CSS variables and the
`vfx` class **only for pieces with no factory** —
`gk-web/web/fusion-rpg-web/src/ui/gui-lego/RecipeMount.tsx:43-53`:

```ts
if (reg?.factory) {
  return <>{reg.factory({ payload, slots, bus })}</>;   // ← factory path: NO theme applied
}
const style = themeStyle(node.payload);                  // ← fallback path only
const vfx = vfxClass(node.payload);
```

A registered factory therefore renders **unthemed** unless it applies the theme itself. The
established pattern is to import the two helpers from the mount module and apply them on the piece's
own landmark root — exactly as the shipped badges do
(`gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/badges.tsx:6` import, `:12` `themeStyle`, `:32`
`vfxClass`, `:62`/`:74`/`:93` applied to `style`/`className`):

```tsx
import { themeStyle, vfxClass } from "@/ui/gui-lego/RecipeMount";

const style = themeStyle(payload);                       // pack css → inline custom properties
const vfx = vfxClass(payload);                           // pack vfx.select → class id
return (
  <div className={["actor-sprite", vfx].filter(Boolean).join(" ")} style={style}>
    …
  </div>
);
```

**Binding for every story-scene piece spec:**

- [ ] The factory imports `themeStyle` and `vfxClass` from `@/ui/gui-lego/RecipeMount`.
- [ ] Both are applied to the piece's **landmark root** (not to a child, not to a wrapper).
- [ ] No piece declares an actor/scene hex, `--act-*`, or an identity utility class (`text-ok`).
- [ ] A test asserts `style` carries the pack's custom properties when a `themeRef` is present.

Without this rule, `actor-sprite`, `name-tag`, `scene-stage`, and the actor packs' whole purpose
silently fails: the packs exist, resolve, and never reach the DOM.

## 2. Slots and DOM shape

- A piece declares a **closed** slot-name set; slot names are shared kit names, never per-feature.
- A child piece renders as a **direct DOM child** of the parent landmark — an intervening wrapper
  (even `display: contents`) breaks draft CSS child combinators
  (`docs/architecture/html-design-implementation.md:53-58`; `spec-composition.md:36-38`).
- A piece with no slots is a leaf and returns a single root element.

## 3. Payload contract

- Every payload carries `piece`, `instanceId`, and `phase` (`PieceEnvelope`,
  `features/gui-lego/types.ts:70-80`).
- `bindSurface` stamps `piece`/`instanceId` and **validates** that a payload's `piece` matches the
  recipe's, throwing on mismatch (`bindSurface.ts:107-113`) — a piece must not trust a hand-written
  `piece` field in its own payload.
- `themeRef` → `themeResolved` is resolved by `bindSurface` (`:66-90`); the piece **reads** it and
  never resolves a pack itself.
- The piece renders payload text **verbatim**. It assembles no label and hard-codes no player string.

## 4. Draft-first (draft HTML is part of "done")

Every piece module names a draft under `docs/design/gui-lego/pieces/` and authors it **before** the
factory is called done — the same rule the shipped piece specs carry
(`gui-lego/spec-shield-status.md:5` — *"must author before factory done"*).

## 5. Test conventions

| Concern | Level | Assertion style |
|---|---|---|
| Payload → DOM | unit (`vitest` + `@testing-library/react`) | landmark class/`data-piece` present; **absence** asserted for omit rules |
| Paint | unit | `style` carries pack custom properties; no identity hex in the snapshot |
| DOM shape | unit | `:scope > .child` where draft CSS uses `>` |
| Surface | `RecipeMount` integration | `bindSurface` + registry produce the expected tree |

**Never** assert a derived population count or a literal beat/species total
(`docs/architecture/validation-ssot.md`).

## 6. Registration

Pieces register through the existing registry — `registerPiece({ pieceId, slots, factory })`
(`features/gui-lego/pieceRegistry.ts:5-7`) — grouped in a `register*.ts` that is **idempotent** and
re-binds on HMR, mirroring `ui/gui-lego/registerCondition.ts:6-9` and the re-bind note at
`ui/gui-lego/pieces/register.ts:43-50`.

### 6.1 The story-scene group module (coverage-audit fix, G1)

Story-scene pieces live in their **own group module**, not appended to the shared Derived group:

```ts
// gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/storyScene.ts
import type { PieceFactory } from "@/features/gui-lego/types";
// …piece factory imports

export const STORY_SCENE_SLOT_MAP: Record<string, readonly string[]> = {
  "scene-stage": ["actors", "window", "progress", "advance"],
  "actor-portrait": ["body"],
  "dialogue-window": ["nameTag"],
  "actor-sprite": [],
  "name-tag": [],
  "advance-control": [],
  "scene-progress": []
};

export const storySceneFactories: Record<string, PieceFactory> = { /* … */ };
```

`registerStoryScene.ts` then calls `registerStoryScenePieces()` (this group) **and**
`registerRecipe(storySceneRecipe)` — mirroring `registerCondition.ts:6-9`'s two-line shape.

**Why a separate group:** the shared `pieces/register.ts` groups are Derived-surface factories
(`ALL`, `:14-26`) with a Derived re-bind carve-out for aptitudes (`:43-50`). Appending story-scene
pieces there would put a stage-layer surface inside the Derived registration path and would touch
another program's file. The separate group mirrors how a new surface already registers
(`registerCondition`, `registerAptitudes`).

**The failure this prevents, stated plainly:** `RecipeMount.renderNode` looks up `getPiece(node.pieceId)`
— when a factory is missing it silently renders a `<div data-piece=…>` with the payload's theme and
the slot children (`RecipeMount.tsx:43-56`). A scene whose pieces are unregistered therefore **renders
without error** and looks almost right while every piece's own markup and behaviour is missing. That is
a silent failure, which is why registration is an acceptance criterion on **every** piece task, not
just the last one.

## 7. Where a piece's CSS lives (coverage-audit fix, G2)

A piece with draft-scoped styling gets its own CSS module beside its factory, scoped under the piece
root class:

```
gk-web/web/fusion-rpg-web/src/ui/story-scene/<piece>.css     e.g. actorSprite.css, nameTag.css
gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneStage.css
```

Precedent: `ui/gui-lego/conditionConsole.css:1-2` scopes every rule under `.condition-console`.
Binding rules:

- **Never** a global selector; every rule is scoped under the piece's root class.
- **Never** a `z-index`/`z-*` (the band guard scans `.css` — `bandGuard.ts:52-56`, `:10`).
- Paint (colors, type scale) comes from the pack's `css` custom properties via `themeStyle`, not from
  literals in this file. A CSS module owns **layout and draft fidelity**; the pack owns **paint**.
- The draft HTML is the visual SSOT; the CSS module is synced from it
  (`html-design-implementation.md:28-35`).

---

## Success criteria

- [ ] Every story-scene piece spec states the `themeStyle`/`vfxClass` application rule.
- [ ] Every story-scene piece factory imports both helpers and applies them to its landmark root.
- [ ] A test per themed piece asserts pack paint reaches the DOM via `style`/`className`.
- [ ] No piece resolves a theme pack itself; `themeResolved` is read from the payload.
- [ ] Each piece has a draft HTML path in its spec and the file exists before "done".
- [ ] **`ui/gui-lego/pieces/storyScene.ts` exists** with `storySceneFactories` + `STORY_SCENE_SLOT_MAP`,
      and every piece task adds its entry (G1).
- [ ] **A test asserts every pieceId the recipe references resolves to a registered factory** — so a
      missing registration fails loudly instead of rendering a silent fallback div.
- [ ] **Each piece's styling lives in `ui/story-scene/<piece>.css`**, scoped under its root class, with
      no `z-index`/`z-*` (G2).
- [ ] Registration is idempotent; a second call does not throw or duplicate.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run gui-lego
npm test -- --run RecipeMount
npm run build
```

## Boundaries

- **Always:** apply theme in the factory; direct-child slot emission; payload-verbatim text; draft first.
- **Ask first:** adding a shared slot name; adding a cross-piece helper.
- **Never:** a private hex or identity class in a piece; a wrapper between a landmark and its child; a
  piece that fetches or resolves its own pack; a hard-coded player string.

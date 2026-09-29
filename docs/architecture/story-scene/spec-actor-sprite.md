# Module: `actor-sprite`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — **decision 2 (the deliverable's centre)**
**Draft:** `docs/design/gui-lego/pieces/story-actor-sprite.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorSprite.tsx` (+ test + draft HTML)
**Depends on:** `actor-cast`, `theme-packs-scene`, `ui/actor/shared.tsx`

---

## Objective

Render an actor's sprite, and when the sprite (or the requested variant) is missing, render an
**honest labelled shape** that says **whose** art is missing — never a blank, never a broken image,
never an indistinguishable generic body.

This is owner decision 2 and the single most concrete deliverable of the ideal.

---

## The bug this replaces

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Today the fallback is one glyph and one shared string —
`features/onboarding/RiftPrologueDialog.tsx:170-174`:

```tsx
<div className="rift-prologue-placeholder" role="img" aria-label={…}>
  <span aria-hidden="true">◈</span>
```

Every actor shares `RIFT_ASSETS.storySprite.fallbackLabel`. Two missing actors are **identical**, so
the fallback tells the player nothing and the developer nothing.

---

## Do not invent a fourth stand-in — extend what exists

Three honest stand-ins already exist in this repo. The spec must reuse the established pattern:

| Existing piece | What it draws | What it lacks for us |
|---|---|---|
| `ui/actor/shared.tsx:22` — `ActorFrame` | An initialed disc, sized by a `size` prop | No **name**; tinted by a **side** axis (`:45-46`) that a person is not |
| `ui/actor/RungStateFallback.tsx:10` | loading / empty / error / locked stand-ins | States, not identities |
| `ui/actor/CatalogIcon.tsx:104` | A generated token glyph (GG-58) | A token, not a person |

**Rule:** `actor-sprite` composes `ActorFrame`'s visual language (initial + themed accent) and adds
the two things it lacks — **the actor's name** and a **non-faction** theme ref. It does not fork a
new visual grammar and it does not restyle `ActorFrame` (which other surfaces depend on).

---

## The genre precedent (why a labelled shape, not a nicer blank)

This is a solved problem in visual novels, and the solution is exactly decision 2.

- **Ren'Py ships `Placeholder`** (`renpy/common/00placeholder.rpy`): it draws a stand-in body with the
  **image name written on it** (`text = "\n".join(self.name)`), and the same displayable with
  `base="bg"` fills the screen with the name for a missing background. So a missing asset says
  **which** asset is missing.
- **Ren'Py's `config.missing_image_callback`** is the documented hook: *"a function [that] is called
  when an attempt to load an image fails. It may return None, or it may return an image manipulator."*
- **Dialogic's** `get_portrait_info` documents the degradation path: *"Uses the default portrait if
  the given portrait doesn't exist."*
- **Community practice extends it** precisely because the shared stand-in conflates people: the
  Lemma Soft thread "Custom Placeholder Portraits on the Fly" (2022-03-17) exists to draw
  **per-character** placeholders.

Our version is that pattern with the repo's own tokens.

---

## Structure (draft HTML landmarks)

```
.story-actor-sprite                  root; carries the pack's css custom properties
  .story-actor-sprite__art           the <img> when a URL resolved
  .story-actor-sprite__placeholder   shown instead, when art/variant is missing
    .story-actor-sprite__initial     the actor's initial (ActorFrame's language)
    .story-actor-sprite__name        the actor's displayName  ← the "honest" half
    .story-actor-sprite__hint        optional "art not yet authored" affordance
```

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"actor-sprite"` | yes | |
| `instanceId` | `string` | yes | e.g. `scene:actor:penny` |
| `phase` | `Phase` | yes | `empty` when art is missing — **not** `error` |
| `actorId` | `ActorId` | yes | |
| `displayName` | `string` | yes | Fiction name for the label |
| `initial` | `string` | yes | From the cast def, not re-derived inline |
| `variantId` | `string` | no | Defaults to `"default"` |
| `spriteUrl` | `string \| null` | yes | `null` ⇒ placeholder |
| `speaking` | `boolean` | no | Emphasis only; the parent owns the state |
| `themeRef` / `themeResolved` | | yes | `actor.<id>` pack |

## Omit / degrade rules (binding)

1. `spriteUrl === null` ⇒ render the **placeholder** with the actor's name. Never an `<img>` with an
   empty or unresolved `src`.
2. `themeRef` resolves to `neutral` ⇒ render with neutral paint, **still labelled**. A missing pack
   does not silently unlabel a person.
3. `phase === "error"` is reserved for a genuine failure, not for "art not authored" — "not authored"
   is `empty`, because it is an expected state during development, not an error.
4. An image that **fails to load at runtime** (onError) degrades to the same placeholder. The
   placeholder is the terminal state, so a broken URL cannot paint a broken glyph.

## A11y

- Spoken-beat art is decorative when the dialogue line is present: `alt=""` + `aria-hidden="true"` —
  mirroring `docs/ideas/onboarding-gnome-teaser.md:148`.
- The placeholder is **not** decorative: it is `role="img"` with
  `aria-label={`${displayName} — art not yet available`}`. (Today's fallback already uses `role="img"`
  at `:171`; this keeps it and adds the name.)
- The name is **visible** text, not `sr-only` only: the point is that a human sees who is missing.

---

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] `docs/design/gui-lego/pieces/story-actor-sprite.html` exists and shows both states side by side.
- [ ] With `spriteUrl: null`, Penny's and Dave's placeholders are **visually distinguishable**
      (different name text, different initial, different pack accent) — asserted in a test.
- [ ] No `<img>` is rendered when `spriteUrl` is null; no empty `src` ever reaches the DOM.
- [ ] A runtime load failure degrades to the placeholder (tested with a rejecting `onError`).
- [ ] `displayName` appears in the placeholder's visible text **and** its accessible name.
- [ ] Zero hard-coded actor hex; accent comes from `themeResolved.paint`.
- [ ] The piece composes `ActorFrame`'s visual language and does not restyle `ActorFrame` itself.
- [ ] No `side`-axis tint anywhere in this piece.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-actor-sprite.html
npm test -- --run actorSprite
npm run build
```

## Boundaries

- **Always:** labelled placeholder with the actor's name; `null` drives the fallback; pack owns accent.
- **Ask first:** changing the placeholder's shape language; adding a state beyond empty/ready.
- **Never:** a blank box; a broken-image glyph; one shared placeholder for all actors; a `side` tint;
  restyling the shared `ActorFrame`.

## Sample payload

```json
{
  "piece": "actor-sprite",
  "instanceId": "scene:actor:penny",
  "phase": "empty",
  "actorId": "penny",
  "displayName": "Penny",
  "initial": "P",
  "variantId": "default",
  "spriteUrl": null,
  "speaking": true,
  "themeRef": { "kind": "actor", "id": "penny" }
}
```

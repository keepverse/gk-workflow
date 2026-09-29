# Module: `actor-portrait`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — decision 2
**Draft:** `docs/design/gui-lego/pieces/story-actor-portrait.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorPortrait.tsx` (+ test + draft HTML)
**Depends on:** `actor-sprite`, `actor-cast`

---

## Objective

One actor **in a slot array**, carrying `speaking | inactive` state, resolving actor → sprite +
variant. This is the piece that makes "two actors side by side" a real capability (owner decision 2).

Genre precedent for the state half: Dialogic's portrait subsystem updates the portrait on a speaker
change and applies highlight/unhighlight so the active speaker is visually distinguished. That is
exactly the `speaking` state here — a **state the piece reads**, not a CSS accident.

---

## Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"actor-portrait"` | yes | |
| `instanceId` | `string` | yes | e.g. `scene:actor:dave` |
| `phase` | `Phase` | yes | |
| `actorId` | `ActorId` | yes | |
| `speaking` | `boolean` | yes | Highlight state |
| `variantId` | `string` | no | Defaults to `"default"` |
| `spriteUrl` | `string \| null` | yes | Passed through to `actor-sprite` |
| `themeRef` / `themeResolved` | | yes | `actor.<id>` |

### Slots

| Slot | Piece | Required |
|---|---|---|
| `body` | `actor-sprite` | yes |

### Binding rules

1. **Array, never a single slot.** `scene-stage`'s `actors` slot is an ordered array; two is the v1
   floor, more is additive.
2. **The speaker is distinguishable without color alone.** Weight/scale/opacity/position, not only
   accent — an inactive actor must still be readable and identifiable.
3. **Inactive ≠ hidden.** The non-speaking actor stays visible but de-emphasized; a scene with two
   people should not blank one. (If the narrow breakpoint must hide one, that is
   `scene-stage`'s declared collapse rule, not this piece's default.)
4. **The variant is state, not a re-render accident.** The piece receives `variantId` from the fold.
   It must never reset a variant on a speaker change — the genre's own failure mode is that
   re-showing an image with the same tag drops its attributes (Ren'Py's `show` replaces by tag), so
   the fold owns variant continuity and the piece renders what it is given.
5. **Not focusable.** Actors are decoration for focus purposes; the window is the focus target.

---

## Structure (draft HTML landmarks)

```
.story-actor-portrait                    root; carries actor pack css
  .story-actor-portrait__body            -> actor-sprite
  .story-actor-portrait__label           optional name under the art (pack-decided)
data-speaking="true|false"               state hook (no private z-index)
```

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists with two actors side by side, one speaking.
- [ ] `speaking` is visually distinguishable **without** color alone (weight/scale/opacity).
- [ ] The inactive actor remains visible and identifiable.
- [ ] A variant change on speaker change does **not** reset the other actor's variant (tested).
- [ ] The actor is not a focus target (`tabIndex` not set; asserted).
- [ ] `spriteUrl: null` still renders the labelled fallback through `actor-sprite`.
- [ ] No hard-coded accent; paint from the actor pack.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-actor-portrait.html
npm test -- --run actorPortrait
npm run build
```

## Boundaries

- **Always:** array-shaped actor set; state from the fold; non-color speaker distinction; not focusable.
- **Ask first:** adding a third+ actor layout rule to this piece (layout belongs to `scene-stage`).
- **Never:** hide the inactive actor by default; reset a variant on speaker change; a private tier; a
  `side` tint.

## Sample payload

```json
{
  "piece": "actor-portrait",
  "instanceId": "scene:actor:dave",
  "phase": "ready",
  "actorId": "dave",
  "speaking": true,
  "variantId": "default",
  "spriteUrl": null,
  "themeRef": { "kind": "actor", "id": "dave" },
  "slots": { "body": { "piece": "actor-sprite", "instanceId": "scene:actor:dave:sprite" } }
}
```

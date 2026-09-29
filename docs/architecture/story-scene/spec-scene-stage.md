# Module: `scene-stage`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defects #6/#9, decisions 1/2
**Owner decisions:** S1 (full-bleed, stack speaker-forward), S4 (i18n throughout)
**Draft:** `docs/design/gui-lego/pieces/story-scene-stage.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneStage.tsx` (+ test + draft HTML)
**Depends on:** `actor-portrait`, `dialogue-window`, `advance-control`, `scene-progress`,
`shell-scene-size`, `band-compliance`

---

## Objective

The **compose root**: the full-bleed art bed, band-utility stacking, the cue state the whole scene
reads, the two-actor responsive layout, and the reduced-motion rules for transitions.

It owns **composition and geometry**. It does **not** own actor identity, copy, or paint.

---

## Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"scene-stage"` | yes | |
| `instanceId` | `string` | yes | |
| `phase` | `Phase` | yes | |
| `sceneId` | `string` | yes | For tests/diagnostics only — **never rendered** |
| `cueId` | `string \| null` | yes | Drives `data-cue`; FE-local (decision 3) |
| `title` | `string` | yes | Shell title (player-facing) |
| `subtitle` | `string` | no | Shell subtitle |
| `sceneThemeRef` / `sceneThemeResolved` | | yes | `scene.<mood>` pack |

### Slots

| Slot | Piece | Arity | Notes |
|---|---|---|---|
| `actors` | `actor-portrait` | **array** (ordered) | 1..n; two is the v1 floor |
| `window` | `dialogue-window` | single | Hosts `name-tag` |
| `advance` | `advance-control` | single | Both verbs |
| `progress` | `scene-progress` | single | Omitted by the fold when `total <= 1` |

### Binding rules

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


1. **Band utilities only.** Stacking uses the seven `.band-*` utilities / document order. **No
   `z-index`, no `z-*` class.** This is the fix for defect #1; the guard
   (`shell/bandGuard.ts:52-56`) is the proof, and it is run, not assumed.
2. **`data-cue` is the cue state**, set from `cueId` — replacing today's
   `data-cue={beat.cue}` (`RiftPrologueDialog.tsx:169`) with a fold-supplied value. The attribute is
   the FE's own rendering contract (decision 3); it is **not** an engine handle.
3. **Two-actor layout is a real obligation.** Desktop: side by side. Narrow breakpoint: the declared
   **collapse rule** below. This is the structural cost owner decision 2 accepted.
4. **Reduced motion covers transitions**, not only the bed. The current rule
   (`features/onboarding/rift.css:89-94`) animates only `::before`/`::after`; the beat transition and
   any sprite swap must also become instant under `prefers-reduced-motion: reduce`.
5. **The art bed is `aria-hidden`** when a dialogue line is present (mirrors
   `onboarding-gnome-teaser.md:148`) — the window carries the meaning.
6. **The scene renders over the stage, not as a route** (GG-1), and it never unmounts the stage
   (GG-11). It does not own its own shell chrome; the shell is `shell-scene-size`'s contract.

### Narrow-breakpoint collapse rule (owner decision S1: stack, speaker-forward)

| Viewport | Rule |
|---|---|
| `≥ 720px` | Actors side by side, speaking actor slightly forward |
| `< 720px` | Actors **stack**, the speaking actor nearest the window; art scales down; the non-speaking actor shrinks but **stays visible** |

**Rejected (and why):** hiding the inactive actor at narrow widths was considered and **declined by
the owner** — hiding a character is a continuity change, not a layout change, and it would make "two
actors" untrue on the device most likely to be checked. The stack rule is therefore binding, not
optional.

**Full-bleed consequences for the layout (S1):** the scene fills the viewport and **never scrolls**.
That means the actors, window, progress, and advance control must all fit a short viewport
(`100dvh`, including mobile browser chrome) **without** scrolling. If they cannot fit, the art bed
scales down before anything else — the dialogue window and the advance control are never sacrificed,
because an unreachable advance control would trap the player in a scene. This is the one place where
full-bleed creates real layout pressure, and the spec names it instead of discovering it at
implementation.

---

## Structure (draft HTML landmarks)

```
.story-scene-stage                     root; carries scene pack css + data-cue
  .story-scene-stage__backdrop         the flat bed colour/backdrop
  .story-scene-stage__art              the composed illustration layer
  .story-scene-stage__actors           -> actor-portrait[]
  .story-scene-stage__window           -> dialogue-window
  .story-scene-stage__progress         -> scene-progress
  .story-scene-stage__advance          -> advance-control
```

Direct children must remain direct: no convenience wrapper may be inserted between the root and a
slot child, because draft CSS uses child combinators
(`html-design-implementation.md:53-58`).

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists with two actors at desktop and narrow widths, and a narration beat.
- [ ] **Zero** `z-index`/`z-*` in this piece and its CSS; stacking is band utilities/document order.
- [ ] `data-cue` reflects `cueId`; no engine vocabulary is rendered as text.
- [ ] `prefers-reduced-motion: reduce` makes the beat transition and sprite swap instant (tested).
- [ ] Two actors render side by side ≥720px and **stack speaker-forward** <720px (asserted per
      breakpoint); the inactive actor remains visible at both widths.
- [ ] **Full-bleed with no scroll:** at `100dvh` on a short viewport, the advance control and the
      dialogue window are both reachable without scrolling (asserted — this is the S1 risk).
- [ ] The art bed scales down before the window or the control do.
- [ ] `actors` is an ordered array; the fold can emit 1..n.
- [ ] The stage mounts inside the band-3 shell and does not unmount the stage beneath it (GG-11).
- [ ] Art bed is `aria-hidden` when a line is present.
- [ ] No copy, no actor identity, and no paint is hard-coded here.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-scene-stage.html
npm test -- --run sceneStage
npx vitest run src/shell/bandGuard.test.ts
npm test -- --run rift
npm run build
```

## Boundaries

- **Always:** band utilities; `data-cue` from the fold; reduced motion for every transition; direct
  slot children; array actors.
- **Ask first:** changing the collapse rule; adding a fifth slot; adding an auto-advance timer.
- **Never:** a private `z-index`/`z-*`; render `sceneId`/`cueId` as player text; hide an actor;
  unmount the stage; a route; **a scroll container** (full-bleed scenes never scroll).

## Sample payload

```json
{
  "piece": "scene-stage",
  "instanceId": "scene:stage",
  "phase": "ready",
  "sceneId": "rift-prologue",
  "cueId": "rift.portal.open",
  "title": "The Rift is opening",
  "subtitle": "A short warning before your first lawn",
  "themeRef": { "kind": "scene", "id": "rift-portal" },
  "slots": {
    "actors": [
      { "piece": "actor-portrait", "instanceId": "scene:actor:dave" },
      { "piece": "actor-portrait", "instanceId": "scene:actor:penny" }
    ],
    "window": { "piece": "dialogue-window", "instanceId": "scene:window" },
    "progress": { "piece": "scene-progress", "instanceId": "scene:progress" },
    "advance": { "piece": "advance-control", "instanceId": "scene:advance" }
  }
}
```

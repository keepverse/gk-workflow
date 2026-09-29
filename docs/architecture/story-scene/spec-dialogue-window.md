# Module: `dialogue-window`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defects #4/#5, decision 4
**Draft:** `docs/design/gui-lego/pieces/story-dialogue-window.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/dialogueWindow.tsx` (+ test + draft HTML)
**Depends on:** `name-tag`

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Own the **say window**: the speaker's line, the optional teaching sentence, and the narration variant.
It owns **readability**, not color.

Today this is inline markup —
`features/onboarding/RiftPrologueDialog.tsx:184-188` — inside a wrapper that also owns the live
region and the key handler.

---

## The separation that matters (genre-backed)

Ren'Py's say screen is built from a `window` (id `"window"`) containing the `who` text and the line;
its GUI gives the speaker region its own id (`namebox`) and lets a Character carry its own namebox
properties — because the **name tag and the say window are different things with different owners**.
Dialogic likewise separates the character's portrait/label from the dialogue viewport.

So: `dialogue-window` renders the line and hosts the `name-tag` slot; `name-tag` owns the speaker's
identity paint. A narration beat is the **same window** with the `nameTag` slot empty — never a second
component, never a fake speaker.

---

## Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"dialogue-window"` | yes | |
| `instanceId` | `string` | yes | |
| `phase` | `Phase` | yes | |
| `line` | `string` | yes | The beat's line |
| `teaching` | `string` | no | Absent ⇒ no teaching line |
| `narration` | `boolean` | yes | True ⇒ no name tag |
| `lineLabel` | `string` | no | Accessible prefix when needed |

### Slots

| Slot | Piece | When |
|---|---|---|
| `nameTag` | `name-tag` | Only when `narration === false` |

### Reading rules

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


1. **One beat = one line + at most one teaching sentence.** The window does not paginate, scroll, or
   accept a paragraph array — a text wall is a script defect (`scene-script`'s beat cap), not a
   window feature. The documented failure mode is real: reviewers call out *"repeated deeply
   uninteresting cryptic exposition dumps for over twenty minutes"*.
2. **The teaching line is visually subordinate** to the line — smaller/lower-contrast, from the pack's
   type scale, never the same weight.
3. **The line is the live region.** This piece owns the polite announcement of a new line so it is a
   contract, not an accident of the consumer's wrapper (`RiftPrologueDialog.tsx:184` today).
4. **Text is selectable and zoom-safe**; the window grows to a bounded height and the text wraps. No
   truncation of a dialogue line — ever. A truncated line is a defect, not a design choice.

## A11y

- `aria-live="polite"` on the **line region only** — so the teaching line and the name tag do not
  re-announce on every beat. (Today the whole window is the live region, `:184`, which re-reads
  everything each beat; that is the correction.)
- The window is a landmark the stage can focus; the actors are not focus targets.

---

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists showing: spoken beat, narration beat, teaching-present, teaching-absent.
- [ ] A narration beat renders the window with **no** `name-tag` node.
- [ ] `aria-live="polite"` is scoped to the line region, not the whole window.
- [ ] The teaching line renders only when present, and is visually subordinate per pack tokens.
- [ ] A long line **wraps without truncation** (asserted with a long fixture, at the narrow breakpoint).
- [ ] No color/hex in the piece; type scale from pack `css` + kit tokens.
- [ ] The piece accepts no array of paragraphs (a text wall is unrepresentable).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-dialogue-window.html
npm test -- --run dialogueWindow
npm run build
```

## Boundaries

- **Always:** one line + optional teaching; narration = same window, no tag; line owns the live region.
- **Ask first:** adding a pagination or history affordance; adding a second text region.
- **Never:** truncate a line; a fake speaker for narration; a paragraph array; color in the piece.

## Sample payload

```json
{
  "piece": "dialogue-window",
  "instanceId": "scene:window",
  "phase": "ready",
  "line": "Temporal signal unstable.",
  "teaching": "This is a new corruption, seen before it is explained.",
  "narration": false,
  "slots": { "nameTag": { "piece": "name-tag", "instanceId": "scene:name-tag" } }
}
```

## Sample payload — narration (no tag)

```json
{
  "piece": "dialogue-window",
  "instanceId": "scene:window",
  "phase": "ready",
  "line": "UNSTABLE SECTOR. QUARANTINE PENDING.",
  "narration": true,
  "slots": {}
}
```

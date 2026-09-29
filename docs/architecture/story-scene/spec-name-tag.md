# Module: `name-tag`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defect #2 (hard-coded speaker paint)
**Draft:** `docs/design/gui-lego/pieces/story-name-tag.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/nameTag.tsx` (+ test + draft HTML)
**Depends on:** `theme-packs-scene`

---

## Objective

Label the current speaker with **pack-owned paint**, and be **absent** on a narration beat.

---

## The bug this replaces

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


`features/onboarding/RiftPrologueDialog.tsx:185`:

```tsx
<p className="text-xs font-bold uppercase tracking-wide text-ok">{beat.speaker}</p>
```

Two defects in one line: the speaker's color is a hard-coded utility class (paint must come from the
actor's pack), and `beat.speaker` is a free string that cannot distinguish an actor from a synthetic
label like `"Gnome signal"`.

---

## Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"name-tag"` | yes | |
| `instanceId` | `string` | yes | e.g. `scene:name-tag` |
| `phase` | `Phase` | yes | |
| `displayName` | `string` | yes | Actor's fiction name |
| `themeRef` / `themeResolved` | | yes | The **speaker's** `actor.<id>` pack |

**Absence is the contract for narration.** A narration beat renders **no** `name-tag` at all — it does
not render an empty tag, a placeholder name, or a "Narrator" label. This mirrors the genre: Ren'Py's
say screen shows the `who` text only when a character spoke, and a single-argument say is narration
(`config.character_id_prefixes` exists precisely because the namebox is a separate, optional region).

**Omit rule (binding):** the fold does not emit a `name-tag` payload when `speakerId` is absent. The
piece itself also renders nothing when `displayName` is empty, so an upstream mistake cannot ship an
empty tag.

## Paint rules

1. The tag's color/background come from `themeResolved` (`css` custom properties + `paint` hex).
2. No `text-ok`, no `text-*` identity class, no hex.
3. **Contrast is per-pack**: `paint.onAccent` against the window background must be checked for each
   actor pack. A pack whose nameplate fails contrast is a pack defect, fixed in the pack.
4. The tag is **uppercase-styled by the pack's css**, not by a hard-coded utility — so a future scene
   can choose a different name-tag treatment without touching the piece.

> **Implementation note (2026-09-15, after building the piece).** Rule 1's "`+ paint` hex" is **not
> reachable as written**: `RecipeMount`'s `themeStyle` spreads a pack's `css` block **only** and never
> `paint` (`RecipeMount.tsx:5-9`), so `paint.onAccent` cannot arrive in the DOM as a variable. The
> rule therefore means: paint resolves from the **resolved pack theme** (`themeResolved.css`, i.e.
> `--piece-accent`), never from a literal. Rule 3's wording is likewise narrower than reality — the
> `onAccent`-on-`accent` pair is 8.24:1/8.10:1 but is not the rendered pair; the rendered treatment is
> **accent text on a 12% accent wash** (the shipped chip convention), which computes to
> **6.66 / 6.33 / 6.58 / 6.29** for the four actor×mood combinations — all AA. The packs' *muted*
> accents fail AA (4.06 / 3.93 / 3.70 / 3.59), which is why the name is never painted muted. A filled
> `onAccent` plate would require adding a token to all four packs, and is deliberately not taken.

---

## Structure (draft HTML landmarks)

```
.story-name-tag                 root; carries pack css custom properties
  .story-name-tag__label        the display name
```

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists showing Penny's and Dave's tags with **different** pack paint.
- [ ] A narration beat renders **no** name-tag DOM node (asserted by an absence test, not a class).
- [ ] Zero hard-coded identity color (`text-ok` and friends) in the piece.
- [ ] Accent/muted/onAccent resolve from `themeResolved.paint` only.
- [ ] An empty `displayName` renders nothing rather than an empty tag.
- [ ] Contrast per pack is checked and recorded for both v1 actors.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-name-tag.html
npm test -- --run nameTag
npm run build
```

## Boundaries

- **Always:** pack-owned paint; absent on narration; visible and accessible name.
- **Ask first:** adding a subtitle/role line to the tag; changing its placement.
- **Never:** a hard-coded speaker color; an empty tag on narration; a "Narrator" fake speaker.

## Sample payload

```json
{
  "piece": "name-tag",
  "instanceId": "scene:name-tag",
  "phase": "ready",
  "displayName": "Penny",
  "themeRef": { "kind": "actor", "id": "penny" }
}
```

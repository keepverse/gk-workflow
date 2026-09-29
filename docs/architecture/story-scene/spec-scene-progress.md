# Module: `scene-progress`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — decision 4 (shared family)
**Draft:** `docs/design/gui-lego/pieces/story-scene-progress.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneProgress.tsx` (+ test + draft HTML)
**Depends on:** —

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Show the player where they are in the scene — `n of m` — with an accessible label, as a reusable
piece rather than an inline span.

Today it is one line of markup —
`features/onboarding/RiftPrologueDialog.tsx:167` — `aria-label={`Beat ${beatIndex + 1} of ${BEATS.length}`}`.

---

## Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"scene-progress"` | yes | |
| `instanceId` | `string` | yes | |
| `phase` | `Phase` | yes | |
| `index` | `number` | yes | **0-based** beat index |
| `total` | `number` | yes | `sceneScript.beats.length` |
| `label` | `string` | yes | Fold-formatted accessible text, e.g. `"Beat 2 of 4"` |
| `showPips` | `boolean` | no | Default `true` |

### Binding rules

1. **The label is authored by the fold**, not assembled in the piece — so it is one place to
   localize and one place to test. The piece renders `label` verbatim.
2. **`total` is the script's own length.** It is **not** a hard-coded constant anywhere: the script is
   authored data, and its beat count is a **reading of that data**, never a pinned literal in a test
   or a component. (`docs/architecture/validation-ssot.md` — guardrails assert contracts and closed
   enums, never a population count.)
3. **A one-beat scene shows no progress chrome.** If `total <= 1`, render nothing — this is the rule
   that lets a **reveal** reuse this piece (decision 4: a reveal is a one-beat scene) without a
   meaningless "1 of 1".
4. **Progress is session UI state, not durable progression** — mirroring
   `docs/ideas/onboarding-gnome-teaser.md:123-124`: *"Beat position is session UI state, not durable
   progression. If the tab closes before acknowledgement, the next eligible presentation starts at
   beat 1."* The piece must not persist anything.

---

## Structure (draft HTML landmarks)

```
.story-scene-progress
  .story-scene-progress__pips     one pip per beat; current pip emphasized
  .story-scene-progress__label    accessible text (visible or sr-only per pack)
```

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists with 4-beat, 1-beat, and 0-beat cases.
- [ ] `total <= 1` renders **no** DOM node.
- [ ] `label` is rendered verbatim from the payload; the piece assembles no string.
- [ ] Pips are decorative (`aria-hidden`) — the label carries the semantics.
- [ ] No literal beat count appears in the piece or its test; the test derives from a fixture script.
- [ ] Nothing is persisted; a remount at index 0 shows beat 1.
- [ ] Current pip is distinguishable without color alone (shape/weight, not only accent).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-scene-progress.html
npm test -- --run sceneProgress
npm run build
```

## Boundaries

- **Always:** label from the fold; derive totals from data; omit when `total <= 1`; session-only.
- **Ask first:** adding a scene title or chapter label to this piece.
- **Never:** hard-code a beat count; persist beat position; rely on color alone; render "1 of 1".

## Sample payload

```json
{
  "piece": "scene-progress",
  "instanceId": "scene:progress",
  "phase": "ready",
  "index": 1,
  "total": 4,
  "label": "Beat 2 of 4",
  "showPips": true
}
```

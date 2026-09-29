# Module: `advance-control`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — decision 5
**Draft:** `docs/design/gui-lego/pieces/story-advance-control.html` — **author before the factory is "done"**
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/advanceControl.tsx` (+ test + draft HTML)
**Depends on:** — (leaf)

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


One piece owning **both** verbs of a scene — advance and skip — with their pending state, so a scene
never hand-rolls a footer.

Today the footer is a raw fragment inside the consumer's JSX —
`features/onboarding/RiftPrologueDialog.tsx:137-157` — including an error-recovery branch inline.

---

## The contract (owner decision 5: skip is always available)

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"advance-control"` | yes | |
| `instanceId` | `string` | yes | |
| `phase` | `Phase` | yes | |
| `isLastBeat` | `boolean` | yes | Drives the primary label only |
| `nextLabel` | `string` | yes | e.g. `"Next"` |
| `finalLabel` | `string` | yes | e.g. `"Anchor the lawn"` |
| `skipLabel` | `string` | yes | e.g. `"Skip intro"` |
| `pending` | `boolean` | yes | Acknowledgement in flight |
| `pendingLabel` | `string` | yes | In-flight primary label, e.g. `"Saving…"`. **Added 2026-09-15:** the field table omitted it while rule 3 required the in-flight label, which would have forced the piece to hard-code a player string — the opposite of the "labels come from the payload" rule. |
| `error` | `boolean` | no | Acknowledgement failed → recovery affordances |
| `retryLabel` / `bypassLabel` | `string` | no | Required when `error` is true |
| `ackFailedLabel` | `string` | no | The failure sentence shown as `role="status"` in the error variant. **Added 2026-09-15** for the same reason as `pendingLabel`: the inline branch being replaced carried this copy, and a piece must not own player text. |

### Binding rules

1. **Skip is present on every beat, including the last.** No first-scene nudge, no confirmation. This
   is genre-backed and repo-backed: `docs/ideas/onboarding-gnome-teaser.md:33` — *"Skipping never
   loses Souls, grants, content, or future story access"* — and GG-52's dismissibility rule.
2. **One terminal path.** `advance` and `skip` both resolve to a single `finish(outcome)` in the fold,
   so a skip can never leave half-written state. Practitioners name this failure directly: a skip that
   merely stops the sequence *"leaves the game in some incorrect state, possibly softlocking the
   game"*.
3. **`pending` disables both verbs** and the primary shows the in-flight label (today `"Saving…"`,
   `:152`). This is the double-click guard's visible half.
4. **The error branch is a variant, not a fork.** When `error` is true, the piece renders
   retry/bypass and **still** keeps the player able to reach the lawn — today's inline behaviour at
   `:139-145` is the contract to preserve.
5. **No new global key.** Enter/Space advance is handled by the **stage** on the focused body
   (`:159-164`), not by a piece-level global listener, and the keymap **forbids F10** —
   `shell/keymap.ts:18`. The piece must not register a keybinding.

---

## Structure (draft HTML landmarks)

```
.story-advance-control
  .story-advance-control__skip      ghost/secondary
  .story-advance-control__primary   Next | Anchor the lawn
  .story-advance-control__recovery  retry + bypass (error variant)
```

## Paint application

**Per `spec-piece-contract.md` §1:** `RecipeMount` applies `themeStyle`/`vfxClass` **only for
factories-free pieces** (`RecipeMount.tsx:43-53`), so this factory MUST import both from
`@/ui/gui-lego/RecipeMount` and apply them to its landmark root — otherwise the pack resolves and
never reaches the DOM.

## Success criteria

- [ ] Draft HTML exists showing normal, last-beat, pending, and error states.
- [ ] Skip renders on every beat, including `isLastBeat === true`.
- [ ] `pending` disables both verbs and shows the in-flight label.
- [ ] The error variant preserves a path to the lawn without a successful acknowledgement.
- [ ] Both verbs call the same terminal action (asserted by a single-handler test).
- [ ] No keybinding is registered by the piece.
- [ ] Labels come from the payload; no player-visible string is hard-coded in the piece.
- [ ] Touch targets meet the kit minimum at the narrow breakpoint.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
Test-Path docs/design/gui-lego/pieces/story-advance-control.html
npm test -- --run advanceControl
npm run build
```

## Boundaries

- **Always:** both verbs in one piece; one terminal path; pending disables both; labels from payload.
- **Ask first:** adding a third verb; gating skip behind anything.
- **Never:** hide skip; a confirmation dialog before skip; a piece-level global key handler; an F10
  binding.

## Sample payload

```json
{
  "piece": "advance-control",
  "instanceId": "scene:advance",
  "phase": "ready",
  "isLastBeat": false,
  "nextLabel": "Next",
  "finalLabel": "Anchor the lawn",
  "skipLabel": "Skip intro",
  "pending": false
}
```

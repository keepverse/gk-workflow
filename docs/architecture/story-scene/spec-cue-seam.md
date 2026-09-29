# Module: `cue-seam`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — **decision 3 (corrected)**
**Touches:** new `gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.ts` (+ test), scene pack `vfx` ids
**Depends on:** `scene-stage`

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Define the **semantic cue seam** for a story scene — and be explicit about what it is **not**.

Owner decision 3 settled this and corrected the ideal's own over-framing: **the story scene is a
web-FE feature**, so the FE owns the cue. The beats, the speaker, and the cue id live in the FE; the
FE already renders its own cue state today via `data-cue={beat.cue}`
(`RiftPrologueDialog.tsx:169`) with CSS (`features/onboarding/rift.css:32-44`). There is **no
injector-side story state machine and none should be built** — the injector does not know what a
prologue is and should not learn.

---

## What this module owns

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


1. **A closed cue vocabulary for story scenes**, typed, so a typo cannot ship silently:

```ts
export type StoryCueId =
  | "rift.portal.open"
  | "rift.portal.surge"
  | "rift.quarantine.seal"
  | "rift.quarantine.fade";
```

2. **The FE rendering contract**: `cueId → scene pack's `vfx.select` id → CSS class`. The mapping lives
   in the **theme pack** (`spec-theme-packs.md:35-40` — `vfx: { select, idle }`), not in the piece, so
   a scene mood can change its cue without a code edit.
3. **The seam, named and typed but not wired to Unity.** The existing `onCue?: (cueId) => void` prop
   (`RiftPrologueDialog.tsx:59-60`) is the precedent; it stays a **safe, optional** seam. If a host
   later wants to forward a cue over the bridge, it can — but this module does not open a socket,
   bind a key, or invent a transport.

---

## What this module explicitly does NOT own

| Not owned | Owner |
|---|---|
| The four Unity-side VFX recipes (`gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs:65-68`, `:442,466,490,514`) | Not this program. They exist as data and are unwired (a **wiring gap**, reported in the ideal, not a wall) |
| A transport/bridge to the Injector | The **sibling** Rift Gate program, whose ideal owns overlay transport and host selection |
| `prove-vfx.ps1` coverage | Whoever wires the Unity channel |
| Retiring or modifying the `rift.*` recipes | A later increment, deliberately deferred |

**Why deferring is correct, not lazy:** the recipes are cue-id-agnostic data consumed by
`VfxDirector.Play(VfxCueDto)` (`gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs:65-73`), which already
degrades on a missing anchor (`:207-223`). Wiring them without a scene-side need would add a
cross-process channel to satisfy a CSS effect that already works. **Add the channel when a scene
actually needs an in-game effect; not before.**

---

## Naming rule (hard)

Cue ids are **semantic**, and they are **not player-visible**. A cue id may contain a mechanism word
(`rift.`), because it is internal data. But:

- `sceneId` and `cueId` must **never** be rendered as text (`scene-stage`'s contract forbids it).
- `displayName`/`line`/`teaching` values are **fiction only** — no ids, paths, or engine terms.
- The **system** is `story-scene`; "Rift" names this story's content and (later) a mechanism — never
  the presentation system (`story-scene-ideal.md` principle 8).

---

## Success criteria

- [ ] `StoryCueId` is a closed union and the four Rift cue ids are the only members in v1.
- [ ] A cue id typo is a **compile error** (typed in `SceneBeat.cueId`, not a bare `string`).
- [ ] `cueId → vfx class` resolves through the scene pack, not through piece code.
- [ ] Under `prefers-reduced-motion: reduce`, the cue renders as an **instant state change**, not an
      animation (GG-32 analogue).
- [ ] `onCue` remains **optional**; the scene works with no host consumer.
- [ ] No socket, no keybinding, no transport is introduced by this module.
- [ ] No `sceneId`/`cueId` appears in any player-visible string (asserted).
- [ ] The four Unity recipes are **untouched**; the wiring gap is documented, not closed here.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run storyCue
npm test -- --run sceneStage
npm run build
```

## Boundaries

- **Always:** typed cue ids; pack-owned cue rendering; reduced-motion = instant; the seam stays optional.
- **Ask first:** adding a fifth cue id; wiring the Unity channel; changing a cue's visual meaning.
- **Never:** an injector story state machine; a socket/keybinding from a scene; rendering a cue id or
  scene id as player text; editing `VfxCatalog.cs` or `prove-vfx.ps1` here.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.ts        # StoryCueId + resolution
gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.test.ts
web/fusion-rpg-web/src/features/gui-lego/themes/scene-*.json   # vfx.select ids
# NOT touched here: gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs, scripts/prove-vfx.ps1
```

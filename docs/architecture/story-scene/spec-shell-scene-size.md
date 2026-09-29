# Module: `shell-scene-size`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — decision 1
**Owner decision:** S1 — **full-bleed bound** (2026-09-15); carries a scoped **GG-61 exemption**
**Touches:** `gk-web/web/fusion-rpg-web/src/shell/DialogShell.tsx`
**Depends on:** `band-compliance` (green baseline)

---

## Objective

Give `DialogShell` the geometry a scene needs **without** moving the scene off band 3, adding a
second shell, or amending GG-5 — and **without silently violating GG-61**.

The problem in one line: the prologue is a **440px card** —
`DialogShell.tsx:67-71` — `w-[min(440px,92vw)]`, `max-h-[min(720px,82vh)]` — while its own narrative
source says each beat is *"one full-screen illustration"*
(`docs/ideas/onboarding-gnome-teaser.md:23`). The shell's contract comment says band-3 is *"a
decision, not a browsing surface"* (`DialogShell.tsx:17-21`), which is why it is narrow.

**The owner chose full-bleed.** `PanelShell`'s `size?: "default" | "actorSheet"`
(`PanelShell.tsx:17-18`, near-fullscreen `h-[min(960px,92vh)] w-[min(1800px,96vw)]` at `:97-99`) is
the *mechanism* precedent — an optional `size` on an existing shell — but **not** the geometry: the
owner wants a scene to fill the viewport, which is a stronger claim than `actorSheet` makes and the
reason this module carries a GG-61 exemption rather than citing that shell as cover. The exemption is
argued in full in the map (§"GG-61 exemption (S1)") and restated in the prop comment below.

Genre prior art agrees a scene is a **layer, not a tier**: Ren'Py's say screen is a screen shown on a
layer (`master` = background + sprites, `transient` = dialogue widgets), never a new layer class;
Foundry VTT models scenes as ordered canvas layers; Unity dialogue packages overlay a
`CanvasLayer`. Nothing in the genre invents a band for a story scene.

---

## Contract

```ts
export type DialogShellProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  subtitle?: string;
  footer?: ReactNode;
  onEscapeKeyDown?: () => void;
  children: ReactNode;
  testId?: string;
  /**
   * "default" keeps the compact bounded band-3 decision card (confirm / reward / level-up).
   *
   * "scene" is the FULL-BLEED bound for illustrated story scenes — owner decision S1
   * (2026-09-15). It fills the surface the band model gives it and NEVER SCROLLS: a scene's
   * content is a fixed-aspect art bed plus one line, and its overflow is a content defect
   * caught by the beat cap, not something a scrollbar absorbs.
   *
   * GG-61 EXEMPTION (scoped, reasoned — read this before "fixing" it):
   * GG-61 forbids a band-2/3 shell growing to swallow the viewport, because a DENSE ENTITY
   * (an actor's 99-channel sheet, an item's affix list) needs a bounded box so its body can
   * scroll internally. A story scene is not a dense entity and does not scroll, so the failure
   * GG-61 prevents cannot occur here. This exemption applies to `size="scene"` ONLY; every
   * other caller keeps the bounded card and GG-61 still governs them.
   * See docs/architecture/story-scene-map.md §"GG-61 exemption (S1)".
   */
  size?: "default" | "scene";
};
```

| `size` | Geometry | GG-61 status |
|---|---|---|
| `default` (unchanged) | `w-[min(440px,92vw)] max-h-[min(720px,82vh)]` | bounded, as today |
| `scene` | **Full-bleed, viewport-fitting, non-scrolling** | **Scoped exemption** — argued above |

**The `scene` bound (owner S1: full-bleed):**

```
inset-0 m-auto h-[100dvh] w-[100vw] max-h-none max-w-none
```

with the inner stage body sized against the **GG-36 viewport contract** so it cannot overflow:

- The scene fills the viewport, **including** under a notched/short viewport, using `100dvh`
  (dynamic viewport height) rather than `100vh` so mobile browser chrome does not clip it.
- **`overflow: hidden` on the scene body.** A scene never scrolls; content that would overflow is a
  defect the beat cap and the one-line rule exist to prevent.
- The stage beneath stays visible **at its edges only if the shell provides them** — with a full-bleed
  scene it generally does not, which is the accepted cost of S1. GG-11 still holds: the stage is
  **never unmounted** (`stageHost.tsx:12-19` `useStageMountGuard`).

**Why this is not "grows past the space the band model gives it":** it consumes exactly the band's
viewport box — no more. The exemption is about the **absence of an inner scroll region**, not about
exceeding a bound.

---

## Rules this must not break

1. **Existing callers are untouched.** `size` defaults to `"default"`; every current call site renders
   exactly as today. Verify by running the existing suites, not by inspection.
2. **Band 3 ownership is unchanged.** The overlay keeps `band-dialog` (`DialogShell.tsx:54`); the
   layer push keeps `band: "dialog"` (`:38`). Only the content box changes.
3. **Focus/Esc behaviour is unchanged.** Focus-return-to-opener (`:57-60`) and the
   keymap-owns-Esc suppression (`:61-66`) are not touched.
4. **A scene is still a decision surface.** Full-bleed must not become a browsing surface: the scene's
   own `advance-control` remains the only action family.
5. **GG-11 holds absolutely.** Full-bleed does not mean the stage unmounts; `useStageMountGuard`
   (`stageHost.tsx:12-19`) must still pass, and the scene must not register its own layer.
6. **A scene never scrolls.** `overflow: hidden` on the scene body; a scrollbar appearing is a defect,
   not a fallback.

---

## Success criteria

- [ ] `DialogShellProps.size` exists, typed `"default" | "scene"`, with the GG-61 exemption documented
      **in the prop's own comment** (so the next reader sees a reason, not a violation).
- [ ] `size` omitted ⇒ byte-identical className behaviour for all existing callers.
- [ ] `size="scene"` fills the viewport, uses `100dvh` (not `100vh`), and **never scrolls**.
- [ ] The scene body has `overflow: hidden`; a test asserts no scroll container is introduced.
- [ ] Every existing `DialogShell` test still passes; no snapshot churn beyond an added case.
- [ ] A test asserts the scene bound uses the viewport units (pinning the GG-36 fit) and that no
      `min(...)`-style inner scroll region is created.
- [ ] No new shell component, no band token added, **no edit to `game-gui-principles.md`**.
- [ ] The exemption text names GG-61 and states why a scene is not a dense entity.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run DialogShell
npm test -- --run bandDiscipline
npx vitest run src/shell/bandGuard.test.ts
npm test -- --run stageHost
npm run build
```

## Boundaries

- **Always:** keep band 3; full-bleed **fits** the viewport; never scroll; document the exemption.
- **Ask first:** any new `size` value beyond `scene`; any change to the `default` geometry; **removing
  the exemption** (that is an owner/ADR decision).
- **Never:** unbounded overflow that drags the stage; a scrollbar in a scene; an eighth band; a forked
  `SceneShell`; editing GG-61 itself; changing an existing caller's rendering.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/shell/DialogShell.tsx        # size prop + className branch
gk-web/web/fusion-rpg-web/src/shell/DialogShell.test.tsx   # scene bound is bounded (new case)
```

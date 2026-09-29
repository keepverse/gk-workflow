# Module: `story-scene-host`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Owner decision:** N2 (2026-09-15) — extract a reusable host
**Touches:** new `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx` (+ test),
`gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx` (becomes a thin wrapper)
**Depends on:** `recipe-wire`, `scene-trigger`, `story-scene-fold`

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Own the **non-presentational wiring** a scene needs, once, so scene 2 is data + a trigger rather than
a copied dialog.

Today that wiring lives inside the prologue — `RiftPrologueDialog.tsx:62-68` keeps
`beatIndex`/`busyRef`/`finishedRef`/`advanceGuardRef`/`ackError`/`assetMissing`, and `:101-127` keeps
the acknowledgement and advance state machine. Copying that for scene 2 is the "one-off" outcome the
owner's first decision rejects.

---

## Contract

```tsx
export type StorySceneHostProps = {
  /** The scene's data. Scene 2 = a new value here. */
  script: SceneScript;
  /** Whether the scene is showing. The trigger/eligibility decision is the caller's. */
  open: boolean;
  /** Player the acknowledgement is written for. */
  playerId: number;
  /** Close without continuing (dismissed). */
  onClose: () => void;
  /** Existing destination; used by success and degraded completion alike. */
  onContinue?: () => void;
  /** Optional presentation seam — semantic cue. Absent is safe (decision 3). */
  onCue?: (cueId: StoryCueId) => void;
};
```

### What the host owns (and a scene does not re-implement)

| Concern | Detail | Preserved from today |
|---|---|---|
| Beat index | `useState(0)`, reset to 0 on open | `:62`, `:72-82` |
| Advance guard | The ref that makes a double-click **one** transition, released after commit | `:63`, `:84-88` |
| Terminal guard | `finishedRef` — a completed scene cannot be completed twice | `:64`, `:102` |
| Busy/pending | `busyRef` + the mutation's `isPending` | `:63`, `:151` |
| Acknowledgement | `useAcknowledgeOnboardingStory(playerId)` with `{ storyId, version, outcome }` | `:68`, `:106-110` |
| Error recovery | `ackError` → retry + bypass-to-destination | `:66`, `:113-116`, `:139-145` |
| One terminal path | `finish(outcome)` for **advance-on-last** and **skip** alike | `:101-120` |
| Cue emission | Emit once per beat index, not per render | `:70`, `:90-94` |
| Fold + mount | `foldStorySceneVm(...)` → `bindSurface(recipe, vm)` → `<RecipeMount>` | new |
| Shell | `<DialogShell size="scene">` | `:130` + `shell-scene-size` |

### What the host does NOT own

- **Eligibility / triggering** — the caller decides whether `open` is true (`scene-trigger`).
- **Presentation** — every visual is a piece. The host renders **no** scene markup.
- **Story arcs / what plays next** — out of scope (N3).

---

## The prologue after this module

`RiftPrologueDialog` becomes a **thin wrapper**: it reads the story eligibility it already has and
delegates. Nothing else about it changes:

```tsx
export function RiftPrologueDialog(props) {
  return (
    <StorySceneHost
      script={RIFT_PROLOGUE_SCRIPT}
      playerId={props.playerId}
      open={props.open}
      onClose={props.onClose}
      onContinue={props.onContinueToLawn}
      onCue={props.onCue}
    />
  );
}
```

**The `storyId`/`version` the host writes must stay `rift-prologue` / `1`.** `storyContract.ts` does not exist under that name anywhere in `web/` (corrected 2026-09-20) — the values come from the
script's own `sceneId`+`version` fields, so the existing ledger rows keep reconciling. A rename here
would orphan acknowledged rows.

---

## Rules that survive the extraction

1. **Acknowledgement semantics are unchanged in every observable way** — same story id, same version,
   same outcomes, same retry, same bypass. The existing `RiftPrologueDialog.test.tsx` assertions
   (`:39-43`, `:55-62`) must keep passing **against the wrapper**.
2. **One terminal path.** Watched and skipped resolve through the same `finish(outcome)`.
3. **Skip is always available** (decision 5) — the host passes it to `advance-control` on every beat.
4. **Beat position is session-only** — resets on open, never persisted (`onboarding-gnome-teaser.md:123-124`).
5. **The host is not a second shell.** It uses `DialogShell`; it does not register a layer, and it
   must not add a `stage === …` branch (`noStageSpecificBranch.test.ts`).
6. **The host does not localize beat copy itself** — with S4 (i18n throughout) the *script* is
   locale-aware; the host renders what the fold resolves.
7. **One host, many scenes** — adding scene 2 must not require editing this file.

---

## Success criteria

- [ ] `StorySceneHost` exists and renders **no** scene markup of its own.
- [ ] `RiftPrologueDialog` is a thin wrapper; its **existing tests pass unchanged**.
- [ ] The ack call is `{ storyId: "rift-prologue", version: 1, outcome }` — verified by the existing
      assertion at `RiftPrologueDialog.test.tsx:40`.
- [ ] A double-click on the primary button yields exactly **one** transition (advance-guard test).
- [ ] Advance-on-last-beat and skip both call the same terminal path (single-handler test).
- [ ] An acknowledgement failure shows retry + destination, and the destination works without a
      successful ack (mirrors `:46-63`).
- [ ] Beat index resets to 0 when `open` flips true (re-presentation test).
- [ ] A **second** synthetic script renders through the same host without editing the host (this is
      the "reusable" proof, and it is the acceptance test that matters).
- [ ] No `stage === …` branch; `noStageSpecificBranch.test.ts` green.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run StorySceneHost
npm test -- --run RiftPrologueDialog
npx vitest run src/shell/noStageSpecificBranch.test.ts
npm run build
```

## Boundaries

- **Always:** one host for all scenes; preserve ack semantics exactly; thin wrapper for the prologue.
- **Ask first:** changing the ack `storyId`/`version`; adding a host prop that is scene-specific.
- **Never:** a second host per scene; scene markup in the host; a stage branch; persisted beat index.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx        # the reusable host
gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.test.tsx
gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx  # thin wrapper
```

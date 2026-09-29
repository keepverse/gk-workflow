# Module: `recipe-wire`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defects #1/#6/#7, all decisions
**Touches:** `docs/design/gui-lego/recipes/story-scene.json`,
`gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/story-scene.json`,
`gk-web/web/fusion-rpg-web/src/ui/gui-lego/registerStoryScene.ts`,
`gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx`,
`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx`
**Depends on:** every module above

---

## Objective

Mount the scene as a **Lego surface** — recipe + fold + `RecipeMount` — and retire the god TSX. This
is the module that makes "reusable, not a one-off" true, because after it a second scene is new
**data**, not a new component.

---

## The recipe

`docs/design/gui-lego/recipes/story-scene.json` (design SSOT) with a runtime copy in
`src/ui/gui-lego/recipes/` — the same two-sided pattern the other recipes use.

**Audit correction (G1/G2):** the first version of this recipe was **wrong in three ways** that
`bindSurface` would have rejected or silently mis-bound. Corrected below:

1. `"bind": "vm.root"` — there is no `root` field on a VM. The root binds **`vm`** itself, as
   `docs/design/gui-lego/recipes/condition-console.json:9` does.
2. Slot children had **no `bind`** — and `getByPath` returns the **root** for a missing path
   (`bindSurface.ts:25-26`), so every child would have received the whole parent payload.
3. `$bindArray` was `"vm.actors"`, but the array lives **on the root payload**, not on the VM:
   `mountBindArray` resolves a non-`vm.` path against the **parent payload**
   (`bindSurface.ts:188-194`), which is exactly how `docs/design/gui-lego/recipes/condition-console.json:29` binds
   `"elementBadges"` and `docs/design/gui-lego/recipes/derived-console.json:63` binds `"vm.families"`.

**Audit correction (G4) — the scene uses NO lifecycle overlays, and this is a hard rule.**

The first version of this recipe used the shared `phase-loading` / `phase-error` overlays. That would
have **shipped engine vocabulary to the player**, because the shared lifecycle piece renders its own
class name as visible text — `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/lifecycle.tsx:10-11`:

```tsx
<div className={`phase phase-${kind}`} data-phase={kind} role="status">
  <strong>{`phase-${kind}`}</strong>          ← "phase-loading" is player-visible text
```

That is a **pre-existing shared-kit defect** this program does not own (`story-scene-map.md` — Out).
Using those pieces as a scene overlay would make the scene complicit in it and violate principle 7
(no engine vocabulary on the player surface). `condition-console` inherits the same defect; the story
scene must not.

The scene also **has no loading/error surface state to render**:

| State | Who owns it |
|---|---|
| Story not yet known / query in flight | `SanctumStage` gates on `riftStory?.eligible` (`SanctumStage.tsx:85-89`) — the dialog is simply **not open** |
| Story query failed | Same gate — not open. The stage shows its own state |
| Durable acknowledgement failed | `advance-control`'s error variant (that spec's rule 4) — inside the scene, not a surface swap |
| Script malformed (zero beats) | A **data invariant** enforced at module load (`scene-script`), so the fold never sees it |

Therefore: **no `lifecycleOverlays` key in this recipe**, and the VM's `phase` is `"ready"` for every
renderable beat. If a future scene genuinely needs a surface-level loading state, the shared lifecycle
piece must be fixed first (a one-line change, owned separately).

```json
{
  "surfaceId": "story-scene",
  "host": "band-3-dialog",
  "version": 1,
  "notes": "Story scene inside DialogShell size:scene. Root binds vm; children bind relative fields. No lifecycle overlays — see spec §Audit correction G4.",
  "root": {
    "piece": "scene-stage",
    "instanceId": "scene:stage",
    "bind": "vm",
    "slots": {
      "actors": {
        "$bindArray": "actors",
        "piece": "actor-portrait",
        "instanceIdTemplate": "scene:actor:{actorId}"
      },
      "window": {
        "piece": "dialogue-window",
        "instanceId": "scene:window",
        "bind": "window",
        "slots": {
          "nameTag": {
            "piece": "name-tag",
            "instanceId": "scene:name-tag",
            "bind": "nameTag",
            "notes": "PARENT-RELATIVE: resolves on the window payload (bindSurface.ts:123-127). Omit when the fold leaves window.nameTag undefined (narration beat)."
          }
        }
      },
      "progress": {
        "piece": "scene-progress",
        "instanceId": "scene:progress",
        "bind": "progress",
        "notes": "Omit mount when the fold leaves `progress` undefined (one-beat scene)"
      },
      "advance": {
        "piece": "advance-control",
        "instanceId": "scene:advance",
        "bind": "advance"
      }
    }
  }
}
```

Notes on the choices, each backed by an existing recipe:

- **Root binds `vm`** — `docs/design/gui-lego/recipes/condition-console.json:9` (`"bind": "vm"`).
- **`actors` uses the existing `$bindArray`** (`gk-web/web/fusion-rpg-web/src/features/gui-lego/types.ts:127`) with a **parent-relative** path,
  like `docs/design/gui-lego/recipes/condition-console.json:29` — no new grammar.
- **Every slot child declares a `bind`**; an unbound child receives the parent payload
  (`bindSurface.ts:25-26`) — an assertion in this module's tests covers it.
- **Conditional slots omit via `undefined`**, not an empty piece — the mechanism
  `bindSurface.ts:129-132` implements and `docs/design/gui-lego/recipes/condition-console.json:50-55` relies on.
- **`host` is a label, not a router.** `docs/design/gui-lego/recipes/condition-console.json:3` uses `"actor-panel-tab"` and
  `bindSurface` never reads it — so `"band-3-dialog"` records intent without inventing a host
  registry. The **actual** host is the `DialogShell` in `RiftPrologueDialog`.

## Registration

Mirrors `registerCondition.ts:6-9`:

```ts
export function ensureStorySceneRegistered(): void {
  registerStoryScenePieces();          // new piece factories
  registerRecipe(storySceneRecipe as RecipeDocument);
}
```

Idempotent, with the same HMR re-bind caveat the existing register file documents
(`pieces/register.ts:43-50`).

## Closed surface bus

Expanding this list requires map/ideal review — the same rule
`condition-glance/spec-recipe-wire.md:52-54` carries.

| Event | Payload | Sink |
|---|---|---|
| `story-scene.advance` | `{}` | Host fold → terminal action |
| `story-scene.skip` | `{}` | Host fold → terminal action |
| `story-scene.ack.retry` | `{}` | Host `acknowledge.mutate()` |
| `story-scene.ack.bypass` | `{}` | Host → continue to lawn |

Pieces never fetch and never call the ack mutation directly — they emit, the host acts.

---

## The migration (what actually changes)

| Now | After |
|---|---|
| `BEATS` const in the component (`RiftPrologueDialog.tsx:19-44`) | `sceneScript.ts` data |
| `beatIndex`/`busyRef`/`finishedRef`/`advanceGuardRef`/`ackError`/`assetMissing` in the component (`:62-68`) | `foldStorySceneVm` input; host keeps `ack` + `beatIndex` |
| Inline scene markup + `rift.css` scoped classes (`:167-188`) | `scene-stage` + piece CSS scoped under piece roots |
| Raw footer fragment (`:137-157`) | `advance-control` |
| `text-ok` speaker line (`:185`) | `name-tag` + actor pack |
| One generic `◈` placeholder (`:170-174`) | `actor-sprite` labelled shape |
| `data-cue` from `beat.cue` (`:169`) | `data-cue` from `fold.cueId` (same attribute, fold-owned) |
| `DialogShell` default geometry (`:130`) | `DialogShell size="scene"` |
| `onCue` prop, unused by the mount | Fold-owned cue; `onCue` removed if unused (Ask-first) |

**The host keeps exactly three things:** beat index, the acknowledgement mutation, and the
continue-to-lawn callback. Everything else is data or fold.

---

## Owner visual gate (N4 — required before "done")

The prologue is **already built and mounted** (`SanctumStage.tsx:260-265`). Migrating it to pieces is a
**visible change to a working surface**, so tests alone cannot close this module —
`html-design-implementation.md:112` requires an owner visual gate for an SSOT-locked surface, and the
repo has already paid for the gap: *"Behaviour green ≠ visual green"* (`:89`).

**The gate:**

1. **Before** — capture the current prologue at a fixed viewport (e.g. 1280×720) on beat 1 and on the
   narration beat.
2. **After** — capture the migrated `size="scene"` prologue at the **same** viewport and beats.
3. **Owner confirms** the after state is the intended look. This is where the S1 full-bleed change is
   accepted or rejected in the real UI, not in a spec.
4. Record both image paths in the task; without the pair, the module is **not done**.

**What the gate must show specifically:** two actors side by side, the narration beat with **no** name
tag, the speaker's pack-coloured name tag, the skip control present on every beat, and the scene
filling the viewport without a scrollbar (the S1 risk).

**Known limitation, stated rather than papered over:** CSS paint order (the rim animation above/behind
the art — `band-compliance`) and the full-bleed `100dvh` fit are **not** assertable in jsdom. The
screenshot is the only real proof for those two, which is exactly why this gate is binding rather than
a nicety.

---

## Rules this must preserve

1. **The durable acknowledgement is unchanged.** `finish(outcome)` (`:101-120`) still writes the same
   story ledger with the same `storyId`/`version`/`outcome`, still retries, still bypasses to the
   lawn. **One terminal path** for watched and skipped (decision 5).
2. **Eligibility is unchanged.** `SanctumStage.tsx:85-89` still decides whether the scene opens.
3. **Beat position stays session-only** and restarts at beat 1 if the tab closes before
   acknowledgement (`onboarding-gnome-teaser.md:123-124`).
4. **Band compliance is inherited from `band-compliance`** — the mount path must be the allowlisted
   one, and `bandGuard.test.ts` must stay green after the move.
5. **`stages/sanctum/` is not a shell.** The scene must not add a `stage === …` branch, or
   `noStageSpecificBranch.test.ts` fails.

---

## Success criteria

- [ ] `story-scene.json` exists in **both** the design SSOT and the runtime recipe folder.
- [ ] `ensureStorySceneRegistered()` is idempotent and mirrors the existing register pattern.
- [ ] `RiftPrologueDialog.tsx` renders `RecipeMount`; **no** inline scene markup remains.
- [ ] `BEATS` no longer exists as a component const; the script is data.
- [ ] The six local state concerns are gone from the component (three remain: index, ack, continue).
- [ ] Two actors render; a narration beat renders no name tag; a missing sprite renders the labelled
      shape with the actor's name.
- [ ] Ack-on-complete and ack-on-skip still write the ledger and still bypass to the lawn on failure.
- [ ] Skip is present on every beat.
- [ ] `npx vitest run src/shell/bandGuard.test.ts` and `noStageSpecificBranch.test.ts` are **green**
      (the band guard's unrelated failures are fixed by `band-compliance`; the i18n lines by
      `shared-kit-fix`).
- [ ] The owner visual gate (N4) is complete: before/after screenshots at the same viewport, owner
      confirmed, paths recorded in the task.
- [ ] The scene fills the viewport with **no scrollbar** at 1280×720 and at a short viewport.
- [ ] The bus is the four events above; no piece fetches.
- [ ] Adding scene 2 requires **no component change** — only `sceneScript` data + a trigger spec entry.
- [ ] The reveal (`OnboardingReveal`) is **not** edited (decision 4: later adoption).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run story-scene
npm test -- --run RiftPrologueDialog
npm test -- --run RecipeMount
npx vitest run src/shell/bandGuard.test.ts
npx vitest run src/shell/noStageSpecificBranch.test.ts
npm test -- --run rift
npm run build
npm run check:bundle     # Phaser/recharts must stay off the entry chunk
```

## Boundaries

- **Always:** recipe + fold + `RecipeMount`; pieces read payloads; host owns the mutation; explicit
  `paths` in any commit.
- **Ask first:** expanding the closed bus; removing the `onCue` prop; touching the reveal; promoting
  piece specs into `gui-lego/`.
- **Never:** keep the god TSX beside the new surface; a second fold; piece-level fetch; a bare
  `tasks/plan.md`; editing `OnboardingReveal` or the sibling first-session spec.

## Project structure

```text
docs/design/gui-lego/recipes/story-scene.json              # design SSOT
gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/story-scene.json
gk-web/web/fusion-rpg-web/src/ui/gui-lego/registerStoryScene.ts
gk-web/web/fusion-rpg-web/src/ui/story-scene/*.tsx                # the piece factories
gk-web/web/fusion-rpg-web/src/features/story-scene/*.ts           # script, cast, cue, fold
gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx  # thin host
gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx     # eligibility (unchanged)
```

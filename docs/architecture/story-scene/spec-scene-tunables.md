# Module: `scene-tunables`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — Tunables section
**Touches:** new `gk-core/data/tuning/story-scene-ui.v1.json`,
new `gk-web/web/fusion-rpg-web/src/ui/story-scene/storySceneTokens.ts`
**Depends on:** — (Wave 0, so no later module invents a constant)

---

## Objective

Decide **where every story-scene number lives before any piece needs one** — so no module invents a
`const`, and a later balance pass moves data rather than code.

**The rule, restated inline:** a balance number never lives as a `const`, and the balance surface is
data (`docs/architecture/tunables-ssot.md`; rule T1 at `:93`). Writing a balance number in code is a
tax paid at every tuning pass, and it makes a rebalance indistinguishable from a code regression when
a golden moves.

**The correction this module records:** presentation numbers have **three** legitimate homes in this
repo, and picking the wrong one is itself a defect. The first draft of the ideal assigned everything to
`gk-core/data/tuning`, which would have been a new, wrong rule.

---

## The three homes

| # | Home | Use for | Precedent in this repo |
|---|---|---|---|
| 1 | `gk-core/data/tuning/story-scene-ui.v1.json` | **Feel / pacing** — the numbers a designer tunes | FE already imports tuning JSON directly: `lib/bus/actorSurface.ts:3-8`, `features/gui-lego/shieldPriorityLabel.ts:5`; the `-ui` sibling class is `gk-core/data/tuning/delve-ui.v1.json` |
| 2 | `src/ui/story-scene/storySceneTokens.ts` | **Structural** — art box, draw caps, breakpoints, with a **why-not-tunable comment** | `src/ui/lawn/lawnPresentationTokens.ts:1-24`; `src/game/systems/actorHudDisplayTokens.ts:8-9` mirrors a tuning value it cannot load |
| 3 | The **theme pack's `css`** | **Paint / type scale** | `gui-lego/spec-theme-packs.md:20-41`; kit tokens `docs/design/_kit/tokens.css` |

A number belongs to home 1 only if **changing it is a balance/feel decision a designer would make**.
If it is a structural consequence of the layout (a box cannot exceed a ratio, a list cannot exceed the
beat cap), it belongs to home 2 and says so.

---

## Home 1 — `gk-core/data/tuning/story-scene-ui.v1.json`

```json
{
  "version": 1,
  "beatTransitionMs": 220,
  "lineRevealPerCharMs": 0,
  "autoAdvanceMs": null,
  "maxBeatsPerScene": 6
}
```

| Key | Unit | Meaning | Why tunable |
|---|---|---|---|
| `beatTransitionMs` | ms | Cross-fade length between beats | Feel |
| `lineRevealPerCharMs` | ms/char | Per-character reveal; **0 = instant** | Feel; 0 is the honest default (no typewriter unless wanted) |
| `autoAdvanceMs` | ms or `null` | Dwell before auto-advance; **`null` = never auto-advance** | Feel; `null` is the default because auto-advance fights reading |
| `maxBeatsPerScene` | count | A scene needing more should be **two scenes** | Pacing; guards text walls |

**`autoAdvanceMs` is `null` by default and the feature is off.** Auto-advance is the documented
"unskippable cutscene" failure mode's cousin — it steals reading time. A scene with auto-advance must
be a deliberate owner decision.

**`maxBeatsPerScene` is not a population count.** It bounds **authored** content (a script a human
writes), not a derived population. Asserting the *actual* beat count of the shipped script as a
literal would be the forbidden pattern (`validation-ssot.md`); the Rift script's length is a
**reading of its data**.

**Who reads these today (decided 2026-09-23, F8).** `beatTransitionMs` and `maxBeatsPerScene` are
read — the stage's cross-fade and `sceneScript.maxBeatsPerScene()`. `lineRevealPerCharMs` and
`autoAdvanceMs` are **declared and deliberately not read**: v1 ships no typewriter and no
auto-advance, which is what this spec's own "0 is the honest default (no typewriter unless wanted)"
and "the feature is off" mean, and what `story-scene-ideal.md:405-406` calls *if ever* / *if used*.
So an unread key here is **not drift** — it is the declared home for a feature the owner may enable
later, which is exactly why its unit, its meaning and its off-value are written down before anything
consumes it. Wiring one is a **feature plus an owner decision** (see Boundaries: changing
`autoAdvanceMs` from `null` is ask-first), not a bug fix; the alternative — deleting the keys until
someone wants them — was considered and rejected because it would re-add them as code literals at
that point, which is the defect this file exists to prevent. Deleting them later is a `v2` publish
through `gk-core/tools/tuning/publish.py`, never a hand-edit (`tunables-ssot.md`).

## Home 2 — `src/ui/story-scene/storySceneTokens.ts`

```ts
/**
 * Story-scene STRUCTURAL tokens. These are geometry consequences, not balance dials —
 * see docs/architecture/story-scene-map.md (`scene-tunables`). A value here changes
 * because the layout changed, never because a balance pass moved it.
 */
export const STORY_SCENE_STRUCTURAL = {
  /** Art bed aspect ratio (w:h). Structural: it is the authored illustration's shape. */
  artAspect: 16 / 9,
  /** Two-actor layout collapses below this width. Structural: a breakpoint, not a dial. */
  actorCollapsePx: 720,
  /** Labelled-fallback box edge, in px. Structural: it must read at the actor slot's size. */
  placeholderSizePx: 160,
  /** Minimum advance/skip hit target, in px. Structural accessibility floor (WCAG target size). */
  touchTargetMinPx: 44
} as const;
```

Each entry carries **why it is not tunable**. `artAspect` follows the authored illustration;
`actorCollapsePx` is a viewport breakpoint; `placeholderSizePx` follows its slot; `touchTargetMinPx`
is an accessibility floor and must **not** be tuned down.

## Home 3 — theme pack `css`

Type scale (speaker / line / teaching), name-tag treatment, window background, cue class. These are
**paint and readability**, owned per pack, never per piece (`spec-theme-packs-scene.md`).

---

## What is explicitly NOT a tunable here

| Not a tunable | Where it belongs |
|---|---|
| Beat copy, teaching sentences | `scene-script` data (authored content) |
| Actor names, initials | `actor-cast` |
| The `size:"scene"` shell bound | `DialogShell`'s className, beside `PanelShell.tsx:97-99` |
| Cue → effect mapping | Theme pack `vfx` + `VfxCatalog.cs` |
| Beat position | Session UI state — never persisted, never a dial |

---

## Success criteria

- [ ] `gk-core/data/tuning/story-scene-ui.v1.json` exists with exactly the four keys above.
      **Plus:** the two unread keys are a recorded disposition, not an omission — see "Who reads these
      today".
- [ ] `autoAdvanceMs` is `null`; no auto-advance ships enabled.
- [ ] `storySceneTokens.ts` exists, is `as const`, and **every** entry has a why-not-tunable comment.
- [ ] No story-scene piece contains a bare timing/geometry literal (asserted by a source scan for
      `ms`-suffixed numeric literals in the piece files).
- [ ] Type scale is not in either file — it is in a pack.
- [ ] A test reads `maxBeatsPerScene` **from the JSON file** and asserts the guard uses it (so the
      guard cannot drift from its dial).
- [ ] No test asserts the shipped script's beat count as a literal.
- [ ] `npm run extract` / lingui is unaffected (no new player string added by these files).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run storySceneTokens
npm test -- --run sceneScript
npm run build
```

## Boundaries

- **Always:** feel → `story-scene-ui.v1.json`; structural → tokens with a reason; paint → pack.
- **Ask first:** adding a key; changing `autoAdvanceMs` from `null`; changing `touchTargetMinPx`.
- **Never:** a balance number as a `const`; a timing literal in a piece; type scale outside a pack;
  a test asserting the shipped beat count or any derived population.

## Project structure

```text
gk-core/data/tuning/story-scene-ui.v1.json
gk-web/web/fusion-rpg-web/src/ui/story-scene/storySceneTokens.ts
```

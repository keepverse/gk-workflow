# Lane brief — `story-scene-1` (program: story-scene)

## Program

`story-scene` — the reusable story-scene presentation system. It turns the four-beat Rift prologue into the
**first consumer** of a module-first scene system (stage, actors, dialogue window, advance control, progress
indicator), so that "scene 2 is data + a trigger entry".

- **Plan:** `tasks/story-scene-plan.md` — approved 2026-09-15 by the owner; implementation authorised.
- **Map:** `docs/architecture/story-scene-map.md` — 21 modules.
- **Ideal:** `docs/architecture/story-scene-ideal.md`.
- **Specs:** `docs/architecture/story-scene/` — 21 specs.
- **Todo:** `tasks/story-scene-todo.md` — 27 tasks, 7 checkpoints, 0 gates. Its own rule 4 keeps the 261
  acceptance boxes unticked individually; the **task blocks** are the unit of work (a line count is not a metric).

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its story-scene row
names, **in this session**, then verify each claim against code. Code beats docs; docs beat comments.

## Why this lane exists

The goal requires every program's open task-block count driven to **zero with evidence**. This program is the
second-largest untended one in the repo and no lane has worked it. Work the todo top-down; a row that ends the
segment still open must end with a **named dependency** or a **sharpened question**, never "needs investigation".

## The locked decisions (from the plan's table — do not relitigate them)

1. Band 3 stays; `DialogShell` gains an optional `size` — every existing caller must render unchanged.
2. Full-bleed scene with a **scoped GG-61 exemption**; its only real proof is the **visual gate**.
3. Two actors, stacked speaker-forward below 720px; `actor-portrait` is an array from day one.
4. The **FE owns the cue** (`data-cue` drives a CSS effect); `cue-seam` is a named seam — no injector work.
5. Skip is always available, one terminal path.
6. A reveal is a one-beat scene; `OnboardingReveal` is **not** edited here.
7. Typed TS module for the script (`sceneScript.ts`) — compile-time `ActorId`/`StoryCueId` checking.
8. i18n throughout, English default; **pseudo-locale render is the acceptance test** and `extract` output is committed.
9. **Fix the four red guard lines in Wave 0, first** — two of the four are inside this program's path.
10. Extract `StorySceneHost`; the prologue becomes a thin wrapper; the ack contract (`rift-prologue`/`1`) is frozen.
11. Minimal trigger contract: `scene-trigger` reads the server ledger and **narrows** only — no arcs, no ordering.
12. **Owner visual gate required: `recipe-wire` cannot close on tests alone.**
13. Invented defaults accepted: 720px collapse, 160px placeholder, `beatTransitionMs: 220`, `maxBeatsPerScene: 6`,
    `autoAdvanceMs: null`.

## Fence (your session paths)

- `gk-web/web/fusion-rpg-web/**` — the FE (the program's own code, components, i18n locales)
- `docs/architecture/story-scene/**`, `docs/architecture/story-scene-map.md`, `docs/architecture/story-scene-ideal.md`
- `tasks/story-scene-todo.md`, `tasks/story-scene-plan.md`, `tasks/story-scene-ledger.jsonl`
- `scripts/**` — only what a row you close requires

If a row needs the server side (the trigger's ledger read), **name the path in your report as an external
dependency** rather than reaching across the fence.

## FE rules that bind this program

1. **Buy before build.** Prefer a maintained library for icons/charts/motion; the locked set is
   `docs/design/tech-stack.md`. A fat bundle is a **code-splitting failure** (`React.lazy`, dynamic `import()`,
   route chunks) — split the chunk, never ban the library.
2. **The visual gate is real.** `recipe-wire` closes only with an owner-facing visual check; use the
   `playwright-cli` skill to drive the running web UI and capture the side-by-side rather than asserting a class name.
3. **Band compliance** is enforced by guards; the four red guard lines are Wave 0.
4. **i18n**: `npm run extract` regenerates `src/i18n/locales`; commit it when it changes. The pseudo-locale render
   is the acceptance test — not a screenshot of English.
5. **A row you close needs its evidence in the same commit**, and the row id must be asserted present after the edit.

## Verification

- `cd gk-web/web/fusion-rpg-web; npm test` — vitest; read the printed counts.
- `cd gk-web/web/fusion-rpg-web; npm run build` — `tsc --noEmit` + vite build; type errors fail it.
- `cd gk-web/web/fusion-rpg-web; npm run check:bundle` — Phaser stays off the entry chunk.
- `cd gk-web/web/fusion-rpg-web; npm run extract` — lingui; commit `src/i18n/locales` if it changes.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session story-scene-1`

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report (end every segment with this)

```
<<<REPORT
{"status": "partial|done|blocked",
 "summary": "<what landed, with commit shas and row ids>",
 "closed": ["<row id>: <one-line evidence>"],
 "open": ["<row id>: <what it now waits on, named>"],
 "blocked": ["<row id>: <the named dependency, or the visual gate it needs from the owner>"],
 "next": "<the single next row you would take>"}
REPORT
```

Every claim in the report must already be a commit in this worktree.

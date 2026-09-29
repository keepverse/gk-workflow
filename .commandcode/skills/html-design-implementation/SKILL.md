---
name: html-design-implementation
description: >-
  Implement an approved docs/design HTML/CSS draft into production FE with structural and visual
  fidelity. Use when porting a design HTML into React, ActorSheet/Derived/HUD chrome, modern-stat-hud
  consoles, or when the owner rejects a "functionally equivalent" UI that is not the draft. Enforces
  structure breakdown → component contract → layered implement → browser side-by-side gate before done.
---

# HTML design implementation (Rise of Summoner)

Implement an approved HTML/CSS draft into production code with **high visual fidelity and
structural fidelity**.

The approved draft is the visual specification. Production architecture may differ, but the
rendered result must preserve the draft's visual hierarchy, information density, spatial
relationships, interaction model, and intended complexity.

This skill exists because agents frequently make a dangerous substitution:

> "I implemented the same feature."

when the actual requirement is:

> "I implemented this exact UI."

A functionally equivalent UI is not an acceptable substitute for an approved design.

**Durable repo rules (committed):** [docs/architecture/html-design-implementation.md](../../../docs/architecture/html-design-implementation.md).
Restate the hard rules from that doc in the session when this skill runs — a pointer alone does not survive a long turn.

---

## ⛔ Repo hard rules (restated — read before any implement)

1. **DESIGN-GATE first.** Before proposing component cuts or "we should", open
   [docs/DESIGN-GATE.md](../../../docs/DESIGN-GATE.md), find the UI / ActorSheet row, and **read** the
   named docs in this session. Sequence: read → verify against code → propose.
2. **Drafts live under `docs/design/`.** Prefer `docs/design/<screen>.html` (+ `_kit/tokens.css`).
   Plate HTML may be history; if a module spec names a newer SSOT (e.g. Derived →
   `derived-combat-console.html`), that file wins over plate-13.
3. **Plans go to `tasks/<program>-plan.md` / `tasks/<program>-todo.md`.** Never bare
   `tasks/plan.md`. Pick `<program>` from the capability map (e.g. `actor-sheet`).
4. **Buy-before-build for presentation** ([docs/design/tech-stack.md](../../../docs/design/tech-stack.md)):
   `lucide-react`, `recharts`, `@xyflow/react`, `motion`, `react-tiny-sparkline` when they fit.
   **Fidelity still wins:** do not force the draft into plate-13 `InspectSplit` / `StatRow` / Tailwind
   card chrome if the SSOT uses a different grammar (e.g. `.console` / `.cat-bar` / `.inspect-split`).
5. **Stale SPA is invalid.** Claiming done against unrebuilt Server `wwwroot` is forbidden. Rebuild
   FE (`npm run build` → `src/FusionRpg.Server/wwwroot`, sync to `dist/.../wwwroot` if that is what
   serves) **or** prove against vite current source. Side-by-side screenshots required.
6. **Git.** Commit with plain git and explicit paths, one logical change per commit; push only when the
   owner asks. No vendor/assistant watermarks in docs or commit messages
   ([docs/contributing/agent-git.md](../../../docs/contributing/agent-git.md)).

---

## 1. Prime directive

### The draft is the source of truth

When an approved draft HTML exists:

- DO NOT redesign it.
- DO NOT simplify it.
- DO NOT "modernize" it.
- DO NOT convert it into a generic dashboard.
- DO NOT replace custom visual structures with generic cards.
- DO NOT remove decorative elements because they are difficult.
- DO NOT reduce information density.
- DO NOT invent a different information hierarchy.
- DO NOT substitute a different component merely because it is easier to implement.
- DO NOT assume that "functionally equivalent" means "visually equivalent."
- DO NOT restyle with ad-hoc Tailwind that replaces the draft's class vocabulary when the plan
  locked "same CSS, same class names."

You may change:

- framework (React)
- component boundaries
- state management / data loading
- CSS organization (scoped under a root class)
- file structure
- internal implementation
- reusable abstractions

You may NOT change the intended visual result without explicit owner approval.

### Complexity is intentional

A sophisticated game UI may intentionally contain dense information, multiple visual layers,
charts, source breakdowns, filters, grouping, badges, gradients, technical overlays, and
expandable details.

Do not normalize such a UI into a SaaS-style collection of cards. If the draft looks complex,
preserve the complexity.

---

## 2. Required workflow

Never jump directly from `draft.html → production code`.

```text
draft.html
    ↓
Structural Analysis          ← mandatory FE structure breakdown
    ↓
Design Specification
    ↓
Component Contract           ← draft region → production file map
    ↓
Implementation Plan          ← tasks/<program>-plan.md
    ↓
Production Implementation    ← layers 1–5
    ↓
Browser Render (current build)
    ↓
Visual Verification          ← side-by-side screenshots
    ↓
Gap Report
    ↓
Surgical Fixes
    ↓
Final Verification + owner gate
    ↓
DONE
```

Every stage is mandatory unless the owner explicitly disables it.

**Structure breakdown is not optional "docs fluff."** Skipping it is how this repo ships cook tabs
with broken left|right split (DOM wrapper vs CSS `>` selectors) and calls unit tests "done."

---

## 3. Phase 0 — Establish the baseline

1. Locate the approved draft (spec / map / owner).
2. Read the **complete** draft (HTML + `<style>` + script behavior that encodes IA).
3. Determine viewport and responsive assumptions.
4. Open the draft in a browser if possible.
5. Capture baseline screenshot at the target viewport.
6. Record the draft path; treat the draft as **read-only**.

Do not begin implementation from a cropped screenshot alone when the HTML is available.

---

## 4. Phase 1 — Structural decomposition (FE structure breakdown)

Before writing production code, reconstruct the draft as a hierarchy. **Do not skip intermediate
containers** — layout often lives on the containers, not the leaves.

Deliverable artifact (write under the program's analysis path or into the plan):

```text
docs/design/analysis/<screen>-structure.md   # preferred when non-trivial
# or embed in tasks/<program>-plan.md § Structure
```

Include:

- Landmark tree with **class names from the draft**
- Which nodes are flex/grid children vs wrappers
- Which CSS rules use **child combinators (`>`)** and therefore forbid intervening DOM nodes
- Scroll vs fixed regions
- IA rails (primary tabs vs section headers vs variant rails)

Example shape (Derived combat console):

```text
.console
  ├── .console-hd
  ├── .cat-bar                 (cook primary)
  ├── .cat-bar.variant-bar
  ├── .inspect-split           MUST be direct child if CSS uses .console > .inspect-split
  │     ├── .dock > .list-pane > .family-block > .row
  │     └── aside.inspect
  └── .foot
```

---

## 5. Phase 2 — Design specification

Record page geometry, layout model, spacing, visual hierarchy, typography, surface treatment, and
graphics — extracted from the draft where practical. Prefer draft tokens (`var(--sun)`, kit CSS)
over inventing a parallel theme.

---

## 6. Phase 3 — Component contract

Every meaningful visual region maps to a production module.

| Draft region | Production module | Owns |
|---|---|---|
| (example) `.console` shell | `DerivedCombatConsole.tsx` | landmark tree |
| `.row` | `DerivedChannelRow.tsx` | six-state row chrome |
| `.inspect` gauges | `DerivedInspector.tsx` / gauges | donut/stack/sources |
| cook join math | `derivedCook.ts` | pure, no React |

For each: purpose, parent, children, inputs, state, layout responsibility, visual responsibility.

### Traceability rule

- Every major draft region → production code.
- Every major production visual region → explainable from the draft.
- Invented-only regions → flag for review.
- Missing draft regions → defect.

### Structure vs premature refactor

**Allowed and required:** cutting a god file into the modules named by the component contract so
the landmark tree has a single owner.

**Forbidden as "fidelity work":** unrelated refactors, rewriting other ActorSheet tabs, forcing
Derived into shared plate-13 kit because "we already have InspectSplit."

Fidelity-first still means: establish the contract and skeleton **before** painting Tailwind
utilities over a wrong tree.

---

## 7. Phase 4 — Existing codebase analysis

Search for tokens (`gk-web/web/fusion-rpg-web/src/theme/`), kit CSS, CatalogIcon, chart libs, PanelShell,
existing tabs.

Reuse when **visually compatible**. Reuse does not override fidelity.

Prefer: compatible existing primitive → reuse.  
Reject: vaguely similar kit → distort draft to fit.

---

## 8. Phase 5 — Implementation plan

Before editing production files, write `tasks/<program>-plan.md` (+ todo) answering:

1. Files that change / create
2. Component contract table
3. What is reused vs Derived-only (or screen-only)
4. Assets
5. States (six render states, selected, empty, …)
6. Responsive rules from draft
7. How visual verification runs (paths for `ssot-html.png` / `ssot-spa.png`)

---

## 9. Phase 6 — Implement in layers

1. **Skeleton** — dimensions, major regions, columns, scroll, stacking. Verify silhouette.
2. **Information architecture** — headings, labels, values, lists, filters, charts, density.
3. **Visual system** — type, spacing, colors, borders, gradients (from draft/kit).
4. **Graphics** — icons (CatalogIcon / lucide when draft allows), charts (recharts or draft SVG
   grammar — match the SSOT), decorative layers.
5. **Interaction** — hover, selected, expand, filter, keyboard.

Do not remove interactions because the first pass is static.

### CSS sync (when plan locks "same CSS, same class names")

1. Edit look in the HTML draft first.
2. Port `<style>` into a scoped production CSS file (e.g. `.derived-combat-console …`).
3. Keep landmark class names stable.
4. Contract-test **DOM shape** (`:scope > .inspect-split`), not only "class exists somewhere."
5. Never claim done on unit tests of join/expand alone.

---

## 10–12. Assets, charts, density

- Prefer real assets / CatalogIcon / lucide; do not silently swap emoji for distinctive glyphs
  unless the draft uses emoji.
- Charts are structural. Preserve dimensions, legend, emphasis. No "chart goes here."
- Dense RPG HUDs are intentional — do not hide sources/modifiers to "clean up."

---

## 13. Anti-generic-UI rules

Failures when they replace intentional design:

- every section → card
- giant empty spacing / SaaS dashboard IA
- default Tailwind / default component-library look
- replacing custom panels with standard cards
- replacing charts with toy bars
- removing layers / background treatment / technical detail
- flattening hierarchy / fewer controls
- **sheetGroup rails (Offense/Pools/…) as primary tabs when the draft's primary rail is cook tabs**

If the result could be mistaken for an admin dashboard or a Bootstrap demo, stop and re-compare.

---

## 14–18. Browser verification, checklist, gaps, surgical repair

After implementation, render the **actual** production page (current vite or rebuilt wwwroot).

Compare in order: **silhouette → layout → typography → surfaces → graphics → interaction**.

Quantify with side-by-side screenshots (this repo: often
`web/fusion-rpg-web/e2e/artifacts/<area>/ssot-html.png` + `ssot-spa.png`).

Gap report prioritizes: **structure > geometry > density > typography > surfaces > decoration**.

Surgical fixes only — do not rewrite the world for "chart is too low."

---

## 19. Completion gate

Do **not** report complete until:

| Gate | Must pass |
|---|---|
| Structural | Regions mapped; hierarchy documented; no silent missing/invented sections; **CSS `>` parents have matching DOM** |
| Functional | Required interactions + data; applicable filters/grouping |
| Visual | Silhouette, geometry, density, type, surfaces, icons/charts |
| Browser | Real render; target viewport; overflow; interactive states |
| Deploy proof | wwwroot rebuilt or vite-current proven; not a stale Server SPA |
| Traceability | draft → component → rendered result for every major region |
| Owner | Side-by-side visual gate when the surface is player-facing / SSOT-locked |

Unit tests of data join are **necessary, not sufficient.**

---

## 20. Failure protocol

If visually wrong: do not defend, do not "close enough," do not redesign the draft, do not add
unrelated abstractions. Find the largest mismatch → fix structural cause → render → compare →
repeat.

---

## 21. Agent self-review (evidence required)

- Hierarchy preserved? Wrapper breaking `>` selectors?
- Same silhouette / density?
- Generic dashboard slip?
- Wrong primary IA (sheetGroups vs cook)?
- Actually rendered and compared? Three largest remaining diffs?

If you cannot answer with evidence, you are not finished.

---

## 22. Minimal operating procedure

1. Read complete draft HTML.
2. Decompose hierarchy (structure breakdown).
3. Write component map.
4. Plan under `tasks/<program>-*`.
5. Implement major geometry first (correct DOM for CSS).
6. Density → styling → graphics → interaction.
7. Rebuild/prove current SPA.
8. Side-by-side screenshots.
9. Fix largest gaps; repeat.
10. Owner gate; report known deviations only.

**Approved draft → structure → contract → plan → implementation → browser evidence → correction → acceptance.**

Architecture is flexible within the contract. Visual intent is not.

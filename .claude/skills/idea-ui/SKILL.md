---
name: idea-ui
description: >-
  Run the idea-UI phase for player menus, ActorSheet tabs, gauges, badges, HUD chips, and FE
  glance audits — module-first (recipe + fold + theme packs), never a page CSS pass. Use when the
  owner says /idea-ui, audits CSS/graph usage on a game menu, lists UI bugs on a sheet tab, asks why
  element/role badges have no VFX, or before /spec on gui-lego / band-2 surfaces. Delivers
  docs/architecture/<program>-ideal.md; no specs, plans, or code.
---

# Idea-UI phase

**Committed SSOT:** read and follow [`docs/architecture/idea-ui-phase.md`](../../../docs/architecture/idea-ui-phase.md)
**exactly** in this session. That file is binding; this skill is the slash entry + hard gates that
must not be skipped when the doc is long.

This is **not** generic `/idea` (`idea-phase`). Use `idea-phase` for RPG systems (atoms, Hub,
combat). Use **this** skill when the work is **player presentation composition** — menus, sheet
tabs, badges, gauges, graphs, status/shield strips — even when the data is RPG-layer.

## Incident (why this skill exists)

2026-09-10 Condition glance: Hub pools and Standing were live, but the UI still looked broken —
mute element text, stub `definitions.md` titles, no shield/status modules, radar overflow. Agents
treated one tab as a page CSS pass. Theme packs, catalogs, and `StatusGlyph` already existed
(**wiring gaps** / **real gaps** for shared pieces). Corrective ideal:
`docs/architecture/condition-glance-ideal.md`.

## Step 0 — out loud before any subsystem doc

State in your own words:

1. **Every RPG feature lives in the RPG layer** — never blocked by PvZ Unity fields.
2. **Stage + layers, not pages** (GG-1).
3. **Recipe + fold + bus — never a god TSX** (GUI Lego decision).
4. **Theme packs own paint** (`css` + `paint` hex + `vfx`).
5. **Buy before build** for presentation; fat chunk → split, don’t ban libs.
6. **Each bug = one or more modules**; shared piece before surface CSS.
7. **No engine vocabulary** on the player surface.

Then open and read in this session (DESIGN-GATE):

- `docs/guide/the-game.md` + `docs/guide/the-loops.md` — name the loop/place
- `docs/architecture/idea-ui-phase.md` (this procedure)
- `docs/architecture/gui-lego-ideal.md`
- `docs/architecture/gui-lego-authoring.md`
- `docs/architecture/gui-lego-map.md`
- `docs/design/gui-lego/README.md`
- `docs/architecture/gui-lego/menu-refactor-queue.md`
- `docs/architecture/game-gui-principles.md` (at least GG-1 / stage thesis)
- `docs/architecture/fe-game-foundation.md` (DPLP — skim if already loaded)
- Host/domain docs for the surface (e.g. `actor-sheet-ideal.md`, element/status/resource SSOT,
  matching `docs/design/spec-*.md`)

Do **not** form a view before those reads.

## Step 1 — name the surface correctly

Condition ≠ Derived ≠ Shield tab ≠ HUD. Find the recipe id under
`docs/design/gui-lego/recipes/` and the queue row. Audit the **named** surface, not a chat alias.

If `$ARGUMENTS` is empty, ask which surface/program before inventory.

## Step 2 — inventory (four buckets)

| Bucket | Use when |
|---|---|
| **Built** | End-to-end works — `file:line` + proof |
| **Wiring gap** | Exists but inert/bypassed — cite the inert line; **not a wall** |
| **Real gap** | No shareable piece/pack yet |
| **Built, defective** | Present but wrong (overflow, stub copy, bad radar) |

Survey in parallel when useful: design pieces/themes/recipes, FE fold/factories, `gk-core/data/tuning`
catalogs, live API.

## Step 3 — bug → module table (required)

Every owner bug → modules. Add shared reuse map. Reject “fix the page CSS” as a shape.

Run the CSS/layout/graph checklist in `idea-ui-phase.md` §4.

## Step 4 — prior art

Web-search genre UI for badges, gauges, radar, status HUD — numbers, formulas, **failure modes**,
sources.

## Step 5 — write the ideal

**Path:** `docs/architecture/<program>-ideal.md` only.

Restate load-bearing principles **inline**. Include the sections listed in `idea-ui-phase.md` §5.
Mark Condition-style work under a clear program id (`condition-glance`, etc.).

## Step 6 — hand off

State the path. Next = owner answers open questions → `/spec` (per-module specs + prefixed
`tasks/<program>-plan.md` / `-todo.md`). **Stop.** No specs, plans, or code from this phase.

## Red flags — stop and re-read

- Starting at React / one CSS PR
- Conflating Condition with Derived
- Inventing element colors when packs/catalog exist
- “No VFX possible” without checking theme `vfx` + binder
- Omitting empty shield/status because cold sheet is null
- Shipping `.md` paths or author notes as player titles
- Writing `SPEC.md` or bare `tasks/plan.md` / `todo.md`
- Ideal that only links principles

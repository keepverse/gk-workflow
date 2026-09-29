# Idea-UI: `auto-assign-control` placement (EP1.19)

**Program:** [`empire-progression`](../empire-progression-map.md) · **Procedure:**
[`idea-ui-phase.md`](../idea-ui-phase.md), scoped by
[`spec-auto-assign-control.md`](spec-auto-assign-control.md) (C1–C7 already locked — **not
re-decided here**). This pass answers exactly the two questions the spec left open: which piece
hosts the control, and what layout/catalog key it uses. **Not a spec. Not a plan. Not code.**

---

## 0. Principles restated (the ones load-bearing for this decision)

1. **Recipe + fold + bus, never a god TSX** (GUI Lego decision). The control is a new *piece* bound
   into the *existing* `aptitudes-console` recipe, not a new host component.
2. **No engine vocabulary on the player surface.** `AutoAssignRule` ids (`even`,
   `posture-force`, …) are engine tokens; the player sees catalog-sourced display names only —
   this is why the spec requires a `*-catalog.v{n}.json` key rather than the FE `RULE_LABELS`
   union EP1.17 shipped as an interim.
3. **Stage + layers, not pages (GG-1).** *"A game is a screen that has a menu that can open
   anywhere… closing it returns the player to exactly the stage state they left."* This bounds the
   shape choice in §5: a control that adds a **new layer** for a flat 4–6-item choice is heavier
   than GG-1 asks for when the existing `aptitudes-console` layer is already open.
4. **Buy before build / no fat bespoke widget.** The repo already owns a button-row shape used for
   exactly this kind of "pick one, fire one bus event" affordance (`preset-action-strip`,
   `preset-entry`) — reuse it rather than a new control family (native `<select>`, a picker menu).
5. **Each bug is one or more modules.** W2 ("nothing emits `aptitude.autoAssign`") is one module:
   a rule-choice piece. It does not touch the tile grid, the leftover gauge, or the decision strip.

**Loop:** this sits inside the existing aptitude-sheet loop (`docs/guide/the-loops.md` — build/spend
loop, "spend points on a specimen or the commander pool"), not a new loop. The control is reached
exactly where `preset-entry` already is: the aptitudes console hero row, opened from the Actor
sheet's Aptitudes tab, itself opened as a layer over whatever stage the player is on (lawn, world,
etc.) per GG-1 — unchanged by this pass.

---

## 1. Surface named correctly

**Surface:** `aptitudes-console` (`gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/aptitudes-console.json`,
`surfaceId: "aptitudes-console"`, `host: "actor-panel-tab"`). Confirmed via
`docs/architecture/gui-lego/menu-refactor-queue.md:22`: *"Aptitudes: Done"* → owned by
[`aptitude-sheet-map.md`](../aptitude-sheet-map.md), FE A/B/C + presets proven. This is **not** a
new surface and **not** Condition/Derived/Shield — it is the one surface `spec-auto-assign-control.md`
already names as the dependency (`aptitudesSurfaceBus.ts` declares `aptitude.autoAssign`; the two
listening handlers are in `AptitudesTab.tsx:261` and `SpeciesBuildPanel.tsx:116`).

---

## 2. Inventory (four buckets)

| Bucket | Finding | Evidence |
|---|---|---|
| **Built** | `aptitude.autoAssign` event type declared on the closed surface bus; two handlers already listen | `gk-web/web/fusion-rpg-web/src/features/gui-lego/aptitudesSurfaceBus.ts:10,24`; `AptitudesTab.tsx:261`; `SpeciesBuildPanel.tsx:116` |
| **Built** | The `aptitudes-console` recipe's `hero` slot already hosts one "open a related mini-flow" button piece (`preset-entry`) emitting a single bus event with no other side effect — the exact shape this control needs | `aptitudes-console.json` hero slots; `pieces/aptitude.tsx:106` (`presetEntryFactory`) |
| **Built** | A multi-button row piece already exists in this same file for "pick one of several named actions" (`preset-action-strip`) — disabled state + `title` reason per button, matching C4's refusal requirement | `pieces/aptitude.tsx:489` (`presetActionStripFactory`) |
| **Wiring gap** (this is W2 itself) | Nothing emits `aptitude.autoAssign` — the bus event and its two consumers are dead code until a producer exists. **Not a wall**: the machinery is real, only the producer piece is missing | `spec-auto-assign-control.md` Objective |
| **Built, defective** | `RULE_LABELS: Record<AutoAssignRule, string>` (EP1.17) is a hardcoded FE string union standing in for the catalog convention DESIGN-GATE's UI row requires. It correctly uses a closed enum key (TypeScript exhaustiveness), but the display text itself is baked into the bundle, not sourced from `gk-core/data/tuning/*-catalog.v{n}.json` the way `aptitude-catalog.v1.json` sources the twelve aptitude names | `gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.ts` (`RULE_LABELS`); contrast `gk-core/data/tuning/aptitude-catalog.v1.json` |
| **Real gap** | No catalog file yet exists for the six rule labels — `aptitude-catalog.v1.json` is a different, already-full catalog (the twelve aptitudes: Might, Fortitude, …), not reusable for rule ids | `gk-core/data/tuning/*catalog*.json` listing — no rule-label file present. **Closed by EP1.20**, which authored `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` |

No bespoke color/theme gap: the control is plain text buttons like `preset-action-strip`, not an
element/status surface, so no `paint`/`vfx` decision is needed here.

---

## 3. Bug → module table

| # | Player-facing gap | Module | Bucket | Notes |
|---|---|---|---|---|
| W2 | Auto-assign is unreachable — no control emits `aptitude.autoAssign` | **`auto-assign-rule-strip`** (new piece) | Wiring gap → closed by adding the piece | Bound into the existing `aptitudes-console` recipe's `hero` slot; reuses `preset-action-strip`'s button-row + disabled/title pattern |
| — | Rule display text is FE-hardcoded, not catalog-sourced | **`aptitude-auto-assign-catalog.v1.json`** (new at this pass; **published by EP1.20**) | Built, defective → closed by publishing the catalog | `RULE_LABELS`'s *keys* (the closed `AutoAssignRule` union) stay in code — only the *display strings* move to the catalog, same split `aptitude-catalog.v1.json` uses for the twelve aptitudes (id in code/tuning, `displayName`/`reading`/`icon` in the catalog) |

**Shared reuse map:** `auto-assign-rule-strip` reuses `preset-action-strip`'s button markup pattern
(disabled + `title` reason) and sits beside `preset-entry` in the same hero row — no new CSS module,
no new layer, no new recipe.

CSS/layout checklist (`idea-ui-phase.md` §4): not applicable beyond "reuse the existing hero row's
flex layout" — this is a text-button row, not a gauge/graph/radar, so the SVG/paint/overflow checks
do not apply.

---

## 4. Prior art

Scoped deliberately short: C1–C7 already lock the interaction contract (draft-only, named refusal,
`even` fallback, no hidden auto-save), so this pass's only open questions are placement and the
catalog key, not genre interaction design. The pattern itself — a row of labeled "auto-fill" buttons
beside a manual point-allocation grid, each applying a named distribution and never auto-saving — is
the same shape as respec/stat-point screens in the action-RPG genre (a labeled "reset/auto"
strip next to a manual +/- grid, distinct from the manual grid itself). No new failure mode is being
introduced beyond what C1–C7 already name (hardcoded rule list, silent auto-save, hidden refusal) —
this pass does not re-litigate those; it only places the strip.

---

## 5. The shape

**Chosen:** add one new piece, `auto-assign-rule-strip`, to the `hero` slot of the existing
`aptitudes-console` recipe (`aptitudes-console.json`), positioned directly after `preset-entry` and
before `species-build-chrome`. It renders one button per rule the fold's view-model lists (sourced
from the server's rule list per C1, never hardcoded), labeled via
`ruleLabel(ruleId)` reading the new catalog (§6), each `onClick` emitting exactly
`bus.emit("aptitude.autoAssign", { rule: id })` (C2) with no other effect. A refused/unavailable rule
(Mode C hiding `species-favour` per C5, or a named refusal per C4) renders disabled with a `title`
explaining why, mirroring `preset-action-strip`'s existing disabled/title pattern, and the strip
always includes `even` as the guaranteed fallback. A result that resolves to a default build is
labelled "suggested" by the **existing** EP1.17 label (`aptitude-default-label`) already mounted
below this hero row — this pass does not touch that piece.

**Rejected shapes:**

| Rejected | Why |
|---|---|
| A second click-to-open picker (mirroring `preset-entry` → the full preset console layer) | Presets are a growable, named, per-player list that outgrows a flat row; auto-assign is a fixed 4–6-item closed set (`assign-ladder`'s own vocabulary). Adding a layer for a flat closed list is exactly the GG-1-adjacent overreach principle 3 warns against — one more click and one more mounted layer for no added expressiveness. |
| A native HTML `<select>` | Cannot carry a per-option disabled reason as a hover `title` the way a themed button can without extra ARIA plumbing, and it bypasses the piece/theme registry entirely (a raw DOM control standing outside GUI Lego is the god-component failure principle 1 and C7 both rule out). |
| A new dedicated panel/section under the tile grid | Oversized for the amount of state involved (one choice, no persisted sub-state) — the hero row already hosts comparable single-purpose controls (`preset-entry`, the scope chip); a new section would duplicate that role. |

---

## 6. Tunables — the catalog key

**(new at this pass — published by EP1.20)** `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` did not exist
when this pass was written; this pass proposed
it. Same shape family as
`aptitude-catalog.v1.json` (schemaVersion/kind/version/entries), one entry per closed
`AutoAssignRule` id:

```json
{ "id": "even", "displayName": "Even split" }
```

Entries needed (mirroring `RULE_LABELS`'s current six keys, which stay the closed TypeScript union —
only the *string values* move out of code): `even`, `posture-force`, `posture-finesse`,
`posture-bastion`, `active-preset`, `species-favour`.

**Not decided here, left to EP1.20:** whether an icon field is added (the strip is plain text
buttons like `preset-action-strip`, so not required for launch); the exact publish diff. EP1.20's own
acceptance already names this ("published through `publish.py` if the key is new") — H7 (a publish
switches every reader in the same commit) applies at that point, replacing `RULE_LABELS`'s literal
strings with a catalog read in the same commit that publishes `v1`.

---

## 7. What this deliberately does not decide

- The server's rule-list response shape or ordering — owned by `assign-ladder`, unchanged.
- C1–C7 themselves — locked by `spec-auto-assign-control.md`, not reopened.
- Icons, spacing tokens, or exact Tailwind classes for the new buttons — ordinary implementation
  detail for EP1.20, not a placement/shape question.
- Whether a future seventh rule needs an overflow/scroll affordance on the strip — structural, and
  `RULE_LABELS`'s `Record<AutoAssignRule, string>` already makes a missing label a compile error, so
  a seventh rule is caught before it ships regardless of strip layout.

---

## 8. Open questions

None for the owner — placement, reuse, and the catalog key are all decided above; C1–C7 remain
exactly as the spec locked them.

---

## 9. The real question

Not feasibility (the bus event and both consumers already exist) and not interaction design (C1–C7
already closed it) — the real question was **which existing module absorbs the producer**, and the
answer is: no new module family. One new piece (`auto-assign-rule-strip`) in the recipe that already
owns this surface, plus one new catalog file for the labels it was always going to need.

---

## 10. Hand-off

Next: `/spec` is not needed again — `spec-auto-assign-control.md` already exists and is now
unblocked (its only stated dependency was this pass). EP1.20 implements: the `auto-assign-rule-strip`
piece + factory, its registration in `aptitudes-console.json` and `registerAptitudes.ts`, the
`aptitude-auto-assign-catalog.v1.json` (new; authored by EP1.20 as the domain's `v1`) publish (H7: publish + switch `autoAssign.ts`'s `ruleLabel()`
to read it in the same commit), and its vitest. **Stop here** — no code from this pass.

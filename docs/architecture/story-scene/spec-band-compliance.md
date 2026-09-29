# Module: `band-compliance`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defect #1, decision 1
**Owner decision:** N1 (fix the shared-kit red guards in this program, Wave 0)
**Touches:** `web/fusion-rpg-web/src/features/onboarding/rift.css`,
`gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx`,
`gk-web/web/fusion-rpg-web/src/shell/bandGuard.ts`
**Depends on:** `shared-kit-fix` (so a green baseline exists to prove the band fix against)

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Make the repo's band contract **true for the story surface**, so a scene can be built on a green
guard rather than on a red one that every later increment would have to work around.

Today `npx vitest run src/shell/bandGuard.test.ts` reports **3 failed / 8 passed** (run in the main
checkout, identical blobs). Two of the three failures are this consumer's:

| Violation | File:line | Rule broken |
|---|---|---|
| Stray stacking tier | `features/onboarding/rift.css:48`, `:59` — `z-index: 1;` | `bandGuard.ts:52-56` — only `theme/tokens.css` may set `z-index`; surfaces use one of the seven `.band-*` utilities |
| Unvetted band-3 owner | `features/onboarding/RiftPrologueDialog.tsx:130` — `<DialogShell` | `bandGuard.ts:94-134` — only `shell/`, `ui/ConfirmDialog.tsx`, three `world-confirms` dialogs, two item benches + workbench, and two delve confirms may render `DialogShell`; `stages/sanctum/` is not a dev-surface prefix (`:136-150`) |

The third failure (`dev/PhaserSceneSwitchPocPage.tsx:284`, `ui/gui-lego/conditionConsole.css:229`,
`ui/gui-lego/shieldConsole.css:100`, `stages/world/mapChromeMute.ts:5-6`) is **not this program's**
and is reported, not silently absorbed.

---

## The `z-index` fix (verified, not hand-waved)

The two rules exist because the band system is a **token** system, not an ad-hoc tier system
(`src/theme/tokens.css:101-107` define `--band-stage:0 … --band-system:500`; `:122-128` define the
seven `.band-*` utilities). The guard forbids any `z-index:` outside `theme/tokens.css`
(`bandGuard.ts:52-56`).

**What each violated line actually does** (`features/onboarding/rift.css`, read in full):

| Line | Declaration | Why it exists | Verified remedy |
|---|---|---|---|
| `:48` | `.rift-prologue-art { position: relative; z-index: 1; }` | Lifts the `<img>` above the `::before`/`::after` rim animation, which are `position: absolute` siblings on the parent (`:11-30`) | The art is a **later sibling in document order** than the pseudo-elements? No — pseudo-elements paint *after* normal-flow content of the same element by default for `::before`, and `::after` paints after children. So document order alone is **not** sufficient here. The correct fix is **`isolation: isolate` + explicit paint order without a tier**: give the pseudo-elements `z-index`-free stacking by moving them to a **dedicated backdrop element placed before the art** in the DOM, or set the art's parent to a grid and place items with `grid-area` (no `z-index` involved). |
| `:59` | `.rift-prologue-placeholder { position: relative; z-index: 1; }` | Same reason, for the fallback shape | Same remedy as `:48` — the two are one problem, so they must be fixed together, not separately. |

**The honest statement:** this is a **structural CSS fix, not a deletion**. Removing `z-index: 1`
without reordering will make the rim animation paint **over** the art. The module's job is to make
paint order explicit through DOM order/grid placement, then delete both declarations.

**If a genuine sub-tier is needed**, the band vocabulary must be amended (Ask-first) — never worked
around locally.

**Proof the fix is real:** a test that asserts the art is not painted under the rim is not
expressible in jsdom. The verification is therefore (a) the guard goes green, and (b) a **manual
visual check of the cue animation** is recorded in the task, since CSS paint order is the thing under
test. This gap is stated rather than papered over.

## The allowlist entry (requires justification, not a formality)

`stages/sanctum/RiftPrologueDialog` is band-3 **by the narrative source's own lock**:
`docs/ideas/onboarding-gnome-teaser.md:37` — *"The teaser is a band-3 `DialogShell` owned by the
Sanctum stage."*

The allowlist is a **closed registry with per-entry justification** (`bandGuard.ts:96-134`). The entry
must therefore record, like every neighbour does:

1. **Fully controlled** — the caller's own `open` state decides visibility. Verifiable:
   `SanctumStage.tsx:85-89` sets `riftOpen` from an eligibility read; the dialog never self-opens.
2. **Never self-opening from a background event** — no timer, no subscription, no socket opens it.
3. **Why band 3 and not band 2** — it is a **decision** surface (`DialogShell.tsx:17-21`): the beats
   conclude in one explicit choice (`Anchor the lawn`), and skipping writes the same terminal state.

**Placement:** the prologue's **path**, not the component's name, is what `bandGuard` keys on. Because
the scene becomes a `story-scene` surface at `recipe-wire`, the entry must name the path that will
actually render `DialogShell` after migration. **The entry is added in this module for the current
path and re-pointed at `recipe-wire` if the mount path moves** — a stale entry is worse than none.

---

## Structure

| | |
|---|---|
| Root | `gk-web/web/fusion-rpg-web/src/shell/bandGuard.ts` |
| Guard proof | `gk-web/web/fusion-rpg-web/src/shell/bandGuard.test.ts` |
| Guard scan surface | `src/**/*.{ts,tsx,css}` excluding tests and `theme/tokens.css` |

## Success criteria

- [ ] `features/onboarding/rift.css` contains **no** `z-index` declaration and **no** `z-*` class.
- [ ] The scene bed/backdrop and the fallback glyph stack correctly **without** a private tier —
      verified by the **owner visual gate** (the rim animation must not paint over the art), since CSS
      paint order is not jsdom-testable.
- [ ] `bandGuard.ts`'s allowlist has exactly **one** new entry, with a comment carrying the three
      justification points above and citing `onboarding-gnome-teaser.md:37`.
- [ ] `npx vitest run src/shell/bandGuard.test.ts` is **green for this program's paths** — after
      `shared-kit-fix` (N1) the only remaining failures, if any, are the four unrelated surfaces below,
      which are **named** rather than hidden.
- [ ] The prologue still renders inside band 3 (allowlist entry present) and **not** as a dev surface.
- [ ] No second allowlist mechanism, no guard bypass, no `eslint-disable`-style escape.

**Note on the green criterion:** `band-compliance` runs **after** `shared-kit-fix`, so at that point
the guard's own failures are the four out-of-scope surfaces only. If the owner wants a fully green
`bandGuard.test.ts` at the end of this wave, those four must be added to that module's scope — the spec
does **not** assume they are fixed.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npx vitest run src/shell/bandGuard.test.ts
npx vitest run src/shell/noStageSpecificBranch.test.ts
npm test -- --run rift
npm run build
```

## Boundaries

- **Always:** use `.band-*` utilities; justify every allowlist entry in a comment.
- **Ask first:** any change to the band token set (`theme/tokens.css`) or a new band.
- **Never:** a private `z-index`/`z-*`; an allowlist entry without justification; widening the guard to
  make a surface fit; fixing another program's violations here.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/shell/bandGuard.ts          # allowlist entry + justification
web/fusion-rpg-web/src/features/onboarding/rift.css # z-index removal
```

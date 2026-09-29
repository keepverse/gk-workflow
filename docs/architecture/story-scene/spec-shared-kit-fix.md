# Module: `shared-kit-fix`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Owner decision:** N1 (2026-09-15) — fix these here, in Wave 0
**Touches:** `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/lifecycle.tsx`,
`gk-web/web/fusion-rpg-web/src/ui/actor/shared.tsx`,
`gk-web/web/fusion-rpg-web/src/features/gui-lego/foldConditionSurfaceVm.ts`,
`gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts`
**Depends on:** —
**Blocks:** `band-compliance`'s green-baseline criterion, `piece-contract`, `localization`

---

## Objective

Fix the **four specific lines** that make two shipped guard suites red, because this program's own
acceptance criteria depend on a green baseline and two of the four lines sit directly in its path.

This module is deliberately **four lines, not "clean up the shared kit."** Every change below is
justified individually, and anything not listed is out of scope.

---

## The exact violations (run, not inferred)

```
npx vitest run src/shell/bandGuard.test.ts   → 3 failed / 8 passed
npx vitest run src/i18n/                     → 1 failed / 57 passed
```

| # | File:line | Violation | Rule |
|---|---|---|---|
| 1 | `features/gui-lego/foldConditionSurfaceVm.ts:71` | `if (key === "revision") continue;` | `i18n/vocabularyGuard.ts:50` bans `revision` as player-facing copy |
| 2 | `features/gui-lego/foldAptitudesSurfaceVm.ts:66` | same literal | same |
| 3 | `ui/actor/shared.tsx:13` | `return "Retired";` | `vocabularyGuard` — a **genuine player-visible leak**: `formatActorPhase` returns the engine enum word for a person's phase |
| 4 | `ui/gui-lego/pieces/lifecycle.tsx:10-11` | `<strong>{`phase-${kind}`}</strong>` | GG-23 — renders the class name `phase-loading` as **player-visible text** |

**Why #3 and #4 are real defects, not guard false positives:**

- #3: `formatActorPhase` is the function that turns a lifecycle enum into a label a player reads. It
  already translates three of four cases (`"Bound"`, `"Unbound"`, `"Idle"`) and **fails to translate
  the fourth** — the leak is an *inconsistency inside the function*, which is why the guard catches
  it. Fix: return a player word (`"Retired"` → the label the fiction uses; **ask-first** on the exact
  wording, since this is player copy on another program's surface).
- #4: the lifecycle piece renders its own `phase-*` class name as text next to the message. It is a
  scaffolding leftover. Fix: drop the `<strong>` line entirely — the `message` prop already carries
  the player-facing text, and `data-phase={kind}` already carries the state for CSS/tests.

## Why #1/#2 need care (they are not just a rename)

`vocabularyGuard`'s scanner skips `case "…":` labels (`CASE_LABEL_PATTERN`, `vocabularyGuard.ts:119`)
and non-rendering attribute values, but a **bare comparison** in an `if` is matched as a string
literal. The `revision` key must therefore stop being a compared string literal.

Two acceptable fixes; the module picks one and applies it to **both** folds identically:

```ts
// Option A — the guard's own allowed shape (a case label)
switch (key) {
  case "revision": continue;
  default: break;
}

// Option B — no literal at all
const { revision: _revisionStamp, ...rest } = payload;   // then iterate `rest`
```

**Recommended: Option B** — it removes the literal instead of teaching the guard about a new
exception, and it keeps `stampRevision`'s intent (skip the `revision` key while recursing) readable.
Option A is listed because it is the *narrowest* change if the owner prefers not to touch the
iteration shape.

**Behaviour must not change:** both folds must still stamp `revision` on every payload and still skip
it during recursion. The fix is to *how the key is compared*, never *what the fold does*.

---

## Out of scope (explicitly)

| Not fixed here | Owner |
|---|---|
| `dev/PhaserSceneSwitchPocPage.tsx:284` | Developer surface |
| `ui/gui-lego/conditionConsole.css:229`, `ui/gui-lego/shieldConsole.css:100` | Shared kit CSS — a separate band-compliance pass |
| `stages/world/mapChromeMute.ts:5-6` | World-stage program |
| `chrome.tsx:153,157` (dev footer copy as defaults) | A **wiring gap** the ideal names; not a red guard, and it is a copy decision, not a mechanical fix |

---

## Success criteria

- [ ] `npx vitest run src/i18n/` → **0 failed** (all 4 suites, 58 tests).
- [ ] `npx vitest run src/shell/bandGuard.test.ts` → the two **i18n-adjacent** entries are gone; any
      remaining failure is one of the four out-of-scope surfaces above and is **named**, not hidden.
- [ ] `formatActorPhase` returns a player word for every `ActorPhase` case; no enum word escapes.
- [ ] The lifecycle piece renders **no** `phase-*` string as text; `data-phase` still present.
- [ ] Both folds still stamp `revision` and still skip it during recursion — asserted by their
      **existing** tests, which must pass unchanged.
- [ ] No behaviour change beyond the four lines: no snapshot churn in existing condition/aptitudes
      tests beyond a removed text node.
- [ ] Exactly four files touched. A fifth is a scope breach.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npx vitest run src/i18n/
npx vitest run src/shell/bandGuard.test.ts
npm test -- --run foldConditionSurfaceVm
npm test -- --run foldAptitudesSurfaceVm
npm test -- --run lifecycle
npm run build
```

## Boundaries

- **Always:** fix the four lines; keep fold behaviour identical; run both guard suites to prove it.
- **Ask first:** the exact player wording for the retired-actor label (another surface's copy).
- **Never:** widen `BANNED_WORDS` to silence a real leak; delete a guard assertion; fix an
  out-of-scope violation; rename `revision` on the wire (it is a real protocol field).

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/gui-lego/foldConditionSurfaceVm.ts   # "revision" literal
gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts   # same
gk-web/web/fusion-rpg-web/src/ui/actor/shared.tsx                           # formatActorPhase leak
gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/lifecycle.tsx              # class-name-as-text
```

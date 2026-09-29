# Module: `localization`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — principle 7
**Owner decision:** S4 (2026-09-15) — **i18n throughout, English default**
**Touches:** `gk-web/web/fusion-rpg-web/src/features/story-scene/*`, `gk-web/web/fusion-rpg-web/src/ui/story-scene/*`,
`src/i18n/locales/**`
**Depends on:** `piece-contract`, `shared-kit-fix` (the i18n suite must start green)
**Why this module exists (audit gap G7):** no first-pass spec decided whether scene copy is localized,
though lingui is installed and used by the four stage files, and **three guards** govern this tree.

---

## Objective

Decide, once, how player-facing story text is produced and which guard polices it — so eight piece
specs do not each assume something different.

---

## What exists in this tree (verified)

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


| Fact | Evidence |
|---|---|
| lingui v5 is installed | `gk-web/web/fusion-rpg-web/package.json` — `@lingui/core`, `/macro`, `/react`, `/cli`, `/vite-plugin` all `^5.9.5` |
| lingui is actually used | `app/providers.tsx:1` (`I18nProvider`), `test/render.tsx:1`, and four stages: `stages/siege/SiegeStage.tsx:3`, `stages/lawn/LawnStage.tsx:4`, `stages/delve/DelveStage.tsx:4` (`useLingui`) |
| Locales exist | `src/i18n/locales/en`, `src/i18n/locales/pseudo` |
| The Rift prologue is **not** localized today | `grep lingui` over `features/onboarding/*.tsx` → nothing; its copy is hard-coded (`RiftPrologueDialog.tsx:134-135`, `:185-187`) |
| Three guards govern player text | `src/i18n/vocabularyGuard.ts` (banned engine words), `reactivityGuard.ts` (bare `t` macro in components), `magnitudeGuard.ts` (bare number formatters in `src/i18n/`) |

## The three guards, and what each means for this program

### `vocabularyGuard` — the one that constrains the scene most

- Bans engine/protocol words as **player copy** (`BANNED_WORDS`, `:42-68`) and two symbols (`:83-86`).
- Scans string literals and JSX text; **skips** comments, `data-testid`, imports, generics, type
  aliases, `case` labels, and non-rendering attributes (`:146-184`).
- **It is red on HEAD** (see the map's audit section): `foldConditionSurfaceVm.ts:71`,
  `foldAptitudesSurfaceVm.ts:66`, `ui/actor/shared.tsx:13`.
- **Binding for this program:** a story-scene piece or the fold must not introduce a new
  violation. Specifically:
  - no banned word in a JSX text node or a rendered string literal;
  - `sceneId` / `cueId` are **never** rendered;
  - `"revision"` must not appear as a compared literal (G6);
  - the scene must not use `ui/actor/shared.tsx`'s `formatActorPhase`, whose `"Retired"` return is a
    live violation — actor names come from `actor-cast`, not from a phase formatter.

### `reactivityGuard` — locale switches must re-render

- Bans the bare `t` macro import in `.tsx` (`reactivityGuard.ts:37`): a component using only `t` has
  no React subscription, so a locale switch never re-renders it.
- **Binding:** any piece that renders translated text uses `msg` + `useLingui()`'s `_`, never a bare
  `t`. This matches every shipped stage.

### `magnitudeGuard` — not applicable here

- It governs bare-number formatters inside `src/i18n/` only (`magnitudeGuard.ts:37`). A scene renders
  **no magnitude**: no actor numbers, no costs, no per-mille values.
- **Binding:** the story scene contributes no `Magnitude`, so GG-46 and the ActorHub gate are **N/A**
  (already recorded in the map's DESIGN-GATE checklist).

---

## Decision (owner S4, 2026-09-15 — settled)

**i18n throughout, English as the default locale — the same posture as the rest of the UI.** This
**supersedes** the earlier chrome-only recommendation: **all** player-facing story text goes through
lingui, and nothing is "deferred narrative."

| Text | Treatment |
|---|---|
| `shellTitle`, `shellSubtitle` | lingui `msg` |
| `nextLabel`, `finalLabel`, `skipLabel`, `retryLabel`, `bypassLabel`, `progress.label` | lingui `msg`, assembled in the fold |
| Actor `displayName` | **lingui `msg`** — a person's name is player text |
| Beat `line`, `teaching` | **lingui `msg`** — the narrative is localized like any other copy |
| `sceneId`, `cueId`, `ActorId` | **Never rendered.** Identity, not copy |

### What this changes about the script and cast

This is the real consequence of S4, and it is why the decision belongs in the spec rather than in
implementation:

1. **`sceneScript` beats carry message descriptors, not plain strings**, for `line`/`teaching` — or the
   script stays plain English and the fold resolves each string through a **stable message id**
   (`scene.<sceneId>.beat<n>.line`). Either shape works; the second avoids re-authoring the script and
   keeps the four Rift lines byte-identical, so this is the **chosen shape** (message-id resolution in
the fold).
2. **`actorCast.displayName` is localized the same way** (`actor.<id>.name`).
3. **`npm run extract` must be run** and `src/i18n/locales/**` committed whenever story copy changes.
   A story string added without extraction is an untranslated string — the exact half-state the
   earlier recommendation was trying to avoid, now avoided by doing it properly.
4. **The pseudo locale must render the scene.** `src/i18n/locales/pseudo` exists precisely to expose
   hard-coded strings; a scene that renders English under the pseudo locale has a missed `msg`.
   **This is the acceptance test for S4**, and it is stronger than any string-by-string assertion:
   no English sentence appears from the dialogue window, name tag, progress label, or advance control
   when the pseudo locale is active.
5. **The scene's copy lives in the locale files, not in the piece.** A piece that renders a literal is
   a defect regardless of the locale.

### Implementation constraint discovered while building (2026-09-15)

**`@lingui/macro` requires literal message text.** `msg({ message: someRuntimeVariable })` is a hard
error (`@lingui/macro: Unsupported macro usage`) — verified with a probe against the repo's own
lingui/babel config, not assumed. The macro compiles at build time and a runtime string extracts
nothing, so there is **no runtime-string path into the catalog**.

Consequence: the spec's first listed shape (**each beat carries a literal message descriptor with an
explicit stable id**) is the one that works, and it is what shipped. The script stays the single
source of the *English wording*; the catalog holds literal copies bound by explicit id. That
duplication is inherent to compile-time extraction, and `messages.test.ts` binds the two **by
assertion in both directions**, so an edit to either alone fails the suite. That is the guarantee the
"a missing message id fails a test" clause was reaching for, enforced from the other side.

**Related defect this surfaced and fixed:** `src/i18n/index.ts`'s pseudo-locale builder passed any
message richer than a single string segment through **untouched**, so an ICU-interpolated message
rendered plain English under the pseudo locale — the precise hardcoded-English symptom the pseudo
locale exists to catch. Every message in the catalog happened to be simple until the scene's
beat-position label (`"Beat {position} of {total}"`) became the first interpolated one.
`compilePseudoMessage` now marks each literal run and leaves placeholder tuples resolvable. A nested
plural/select shape is still passed through unmarked rather than guessed at — a residual limitation
to close before a plural ships.

### Why message-id resolution is the recommended shape

Keeping the authored script as plain English and resolving through a message id means:

- the four Rift lines stay **byte-identical** to `docs/ideas/onboarding-gnome-teaser.md` (a copy-parity
  test we already want);
- the script stays readable as a script;
- a translator never edits a beat structure.

The cost is a mapping from (sceneId, beat index, field) → message id, which is mechanical and testable
(a test asserts every beat and actor has a resolvable message id — so a *missing* translation is a
failing test, not a silent English fallback in one locale).

---

### Where content resolves — corrected 2026-09-23 (lane `story-scene-1`)

Point 1 above says the chosen shape is "**message-id resolution in the fold**". That is not buildable,
and it is not what shipped — the fold is a pure function with no locale, and the macro constraint
below forbids a runtime-string path anyway. What shipped first was also not right: the descriptors in
`messages.ts` were extracted for translators but **read by no production code**, so the render used
the script's and the cast's own English literals. Under the pseudo locale the chrome changed and
every beat line, teaching, actor name and sprite label stayed English — and nothing caught it,
because the pseudo-locale **render** test this spec makes the S4 acceptance test had never been
written (the catalog-level `src/i18n/index.test.ts` was green throughout).

**The shipped shape (2026-09-23):** the **host** resolves content, because it is the one place that
has a locale, exactly as it already resolves chrome — `sceneContentResolver(script, id => i18n._(id))`
(`messages.ts:211-242`) → `StorySceneHost.tsx:117` → the fold's `content` input
(`foldStorySceneVm.ts:76-91`, applied at `:168-170` for `line`/`teaching` and at the two `displayName`
sites). The fold still places text and never translates, so point 7 ("labels are fold-authored") and
`spec-piece-contract.md:82` ("the piece renders payload text verbatim") both stand unchanged.

A scene with no descriptor table resolves to `{}` rather than throwing, which is what keeps the
host's synthetic second scene rendering — the fold falls back to the script's authored string.

**The acceptance test now exists:** `src/ui/story-scene/StorySceneHost.pseudo.test.tsx` renders the
assembled scene under `setLocale("pseudo")` and asserts, per beat, that the line, teaching and name
tag equal the catalog's own pseudo text, that the progress label keeps its interpolation, and that
both verbs are catalog-resolved. It red on first run for three of the four named families — that red
is the evidence this correction is real, not a tidy-up.

**The resolvers follow the active locale (defect found and fixed 2026-09-23).** Both resolutions were
keyed on the `i18n` singleton (`[i18n]`, `[script, i18n]`). A singleton's identity never changes, so a
locale switch made *while the scene is mounted* left every label and every line in the mount-time
language — and the app can make exactly that switch: System → Preferences offers `en | pseudo`
(`layers/system/SystemLayer.tsx:117-118` calls `setLocale`). Both memos now depend on `i18n.locale`
(`ui/story-scene/StorySceneHost.tsx:114,128`). Proved load-bearing by revert: removing the dependency
reds `follows a locale switch made while the scene is open`, and nothing else notices.

**The layout half has a mechanism too (F11, closed 2026-09-23).** The locale's second job — "a layout
that can't survive a longer translation is visible immediately" — could not be exercised in a browser
at all: `setLocale("pseudo")` is a no-op outside `import.meta.env.DEV` and the end-to-end gate runs a
production preview, so `window.__i18nDebug` is stripped there. Rather than ship the pseudo catalog to
make a test possible, the gate gained an opt-in **dev** project:
`e2e/story-scene-pseudo.spec.ts` + `e2e/helpers/pseudo-gate.ts` (`npx playwright test
e2e/story-scene-pseudo.spec.ts --project=pseudo-chromium`) drives `vite dev`, switches the locale on
the **live** instance the way the preference screen does, and then applies the T23 obligations in
pseudo: every player string pseudo-marked, dialog body never overflowing, advance control inside the
viewport — at 1280×720, 1280×600 and 390×844, with PNGs under `e2e/artifacts/story-scene/`.
First run: **3/3 green, `overflow=False` and `pseudoMarked=True` on all 12 captures**, including the
short viewport that clipped the pre-cutover dialog by 90px.

**Residual (closed 2026-09-23, same lane):** success criterion 2 below ("no piece renders a
hard-coded player string") was **not** met when this correction was written. Three literals were left,
all English under every locale and all found by the new pseudo render:

| Where | Literal | Now |
|---|---|---|
| `actorSprite.tsx:47` | `` `${displayName} — art not yet available` `` (the placeholder's accessible label) | `payload.spriteLabel`, an ICU message interpolated with the already-resolved name — `story-scene.sprite.placeholder` |
| `actorSprite.tsx:91` | `art not yet authored` (the visible hint line) | `payload.hintLabel` — `story-scene.sprite.hint`; absent ⇒ no hint span, never English |
| `advanceControl.tsx:134,142` | `"Working…"` title fallbacks | removed; the piece's own doc comment already said "absent by default — the scene host never needed one, and an untitled button stays untitled", so the code now matches it |

They live in `STORY_SCENE_PIECE_LABELS` (`messages.ts`), resolved by the host and carried on the
payload, which is what keeps the pieces translation-free and still verbatim (`spec-piece-contract.md:82`).
`actorSprite.test.tsx` pins the shape with a source scan (the same technique its hex-literal test
already used), and `StorySceneHost.pseudo.test.tsx` now asserts the hint and every placeholder's
accessible label on every beat.

**`initial` is deliberately not localized (F12, ruled 2026-09-23):** the fallback's `initial` is authored
in the cast (`actorCast.ts:37-38`, `:73,:80`) and derived from the name, so a non-Latin translation
keeps a Latin initial. That is by design, not a missed `msg`: it is an *identity glyph* (decorative,
`aria-hidden`), and a translatable initial would re-author the name's first letter in a second place —
the drift `actor-cast`'s "derived, not authored twice" rule exists to prevent. Recorded in
`spec-actor-cast.md` § "`initial` is not localized" and pinned by `StorySceneHost.pseudo.test.tsx`.

**Checked and deliberately left:** every host in this shell has the same `*.rd` "recipe not registered"
fallback (`ConditionTab.tsx:75`, `DerivedTab.tsx:235`, `ShieldTab.tsx:73`, `StorySceneHost.tsx:254`).
It is an unreachable programming-error surface (registration is synchronous and asserted) and an
established four-host idiom — changing only the story-scene one would deviate for no player benefit.

---

## Success criteria

- [ ] **Every** story string is a lingui message: `shellTitle`, `shellSubtitle`, all control labels,
      `progress.label`, actor `displayName`, and beat `line`/`teaching`.
- [ ] No piece renders a hard-coded player string (asserted by a pseudo-locale render, below).
      **Met as of 2026-09-23:** the three literals that remained (`actor-sprite`'s hint and accessible
      label, `advance-control`'s title fallback) are catalog messages now, carried on the payload;
      asserted by `src/ui/story-scene/StorySceneHost.pseudo.test.tsx` (window, name tag, sprite hint,
      sprite label, progress, controls) and by the piece's own source scan.
- [ ] Under the **pseudo locale**, no English sentence appears from the dialogue window, name tag,
      progress label, or advance control — **this is the S4 acceptance test**.
      **Met as of 2026-09-23** by `src/ui/story-scene/StorySceneHost.pseudo.test.tsx` (2 tests).
- [ ] Every beat and every actor has a resolvable message id; a missing one **fails a test** rather
      than silently falling back to English.
- [ ] The four Rift lines remain byte-identical to `docs/ideas/onboarding-gnome-teaser.md` (copy
      parity survives localization).
- [ ] `npm run extract` is run and `src/i18n/locales/**` is committed when story copy changes.
- [ ] Every localized component uses `msg` + `useLingui()` — **never** a bare `t`
      (`reactivityGuard`).
- [ ] `npx vitest run src/i18n/vocabularyGuard.test.ts` does **not** gain a violation from any
      story-scene file (the three pre-existing ones are fixed by `shared-kit-fix`, not adopted).
- [ ] No story-scene file imports `formatActorPhase` from `ui/actor/shared.tsx`.
- [ ] No `sceneId`/`cueId`/engine word is rendered (asserted).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npx vitest run src/i18n/
npm run extract
npm run build
```

## Boundaries

- **Always:** lingui for **all** story text; `msg` not bare `t`; extract + commit locales; pseudo-locale
  render as the acceptance test.
- **Ask first:** changing the message-id scheme; adding a locale.
- **Never:** a hard-coded player string in a piece; a bare `t` import in a piece; a rendered engine
  word; a new `vocabularyGuard` violation; a translated string without extraction.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/i18n/locales/en/**          # if chrome strings are extracted
gk-web/web/fusion-rpg-web/src/i18n/locales/pseudo/**
gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts  # descriptors + sceneContentResolver (host-side)
gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx # resolves chrome AND content, once, for the active locale
```

# Capability map: story-scene

**Status:** **approved 2026-09-15** (owner). Phase 0, Phase 1 (21 module specs) and Phase 2/3
(plan + task list) are complete; implementation is authorized via `/build full`.
**Program id:** `story-scene`
**Ideal:** [story-scene-ideal.md](story-scene-ideal.md) (idea-UI phase, 2026-09-15; all five owner
questions answered — decisions 1–5)
**Procedure:** [idea-ui-phase.md](idea-ui-phase.md) (`/idea-ui`) for the ideal ·
[spec-driven-development] for this map and the module specs
**Parent kit:** [gui-lego-map.md](gui-lego-map.md) · [gui-lego-authoring.md](gui-lego-authoring.md) ·
[design/gui-lego/README.md](../design/gui-lego/README.md)
**Shared shell this program extends:** `gk-web/web/fusion-rpg-web/src/shell/DialogShell.tsx`
**Consumer under migration:** `gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx`
**First consumer:** the four-beat Rift prologue (`docs/ideas/onboarding-gnome-teaser.md`)

**Sibling programs (do not absorb):**

- [rift-gate-ideal.md](rift-gate-ideal.md) — the Rift Gate mechanism (overlay transport, host
  selection, first-open capture). May later own the Unity-side cue bridge; this program does not.
- [standalone/spec-first-session-progression.md](standalone/spec-first-session-progression.md) — owns
  the first-session reveal sequence and `stages/sanctum/OnboardingReveal.tsx`. Decision 4 makes the
  reveal a **later consumer** of shared pieces; adoption is out of this program.
- [gui-lego-map.md](gui-lego-map.md) — owns the piece/recipe/theme registries and the shared kit.

**DESIGN-GATE:** **UI** + **Player menus** rows read in this session.

---

## What this program is

Make the Rift prologue the **first consumer** of a reusable, module-first story-scene presentation
system: a scene stage that plays illustrated, beat-by-beat narrative with actors, a dialogue window,
an advance control, and a progress indicator — composed from Lego pieces, themed by packs, fed by a
pure fold, over the existing band-3 shell.

**Not** a one-off dialog refactor. **Not** a page CSS pass. **Not** a new stage, a new band, or a new
route. **Not** an injector story engine (owner decision 3).

---

## Modules

Dependency direction is one-way; no cycles. Every module id is stable and kebab-case.

| Module id | Responsibility | Depends on | Spec |
|---|---|---|---|
| `shared-kit-fix` | **Wave 0.** Fix the four shared-kit red-guard lines this program depends on (N1) so the tree goes green: `lifecycle.tsx:10-11`, `ui/actor/shared.tsx:13`, and the two `"revision"` literals | — | [story-scene/spec-shared-kit-fix.md](story-scene/spec-shared-kit-fix.md) |
| `band-compliance` | Fix this program's own band violations **plus (absorbed 2026-09-15) the three remaining stray-tier violations on other surfaces and the `layerStack` import outside `shell/`**, so `bandGuard.test.ts` is fully green. Carries the **GG-61 scene exemption** (S1) | `shared-kit-fix` (for a green baseline) | [story-scene/spec-band-compliance.md](story-scene/spec-band-compliance.md) |
| `shell-scene-size` | `DialogShell` gains `size: "default" \| "scene"` — a **viewport-fitting, non-scrolling** bound (owner S1), with the GG-61 exemption recorded rather than assumed | `band-compliance` | [story-scene/spec-shell-scene-size.md](story-scene/spec-shell-scene-size.md) |
| `scene-script` | Beat/script data contract `{ speakerId, variant?, line, teaching?, cueId? }`; the four Rift beats move out of the component into data; `maxBeatsPerScene` guard | — | [story-scene/spec-scene-script.md](story-scene/spec-scene-script.md) |
| `scene-tunables` | The two number homes: `gk-core/data/tuning/story-scene-ui.v1.json` (feel/pacing, loadable by the FE) and `storySceneTokens.ts` (structural caps, with a why-not-tunable comment). No balance number in a `const` | — | [story-scene/spec-scene-tunables.md](story-scene/spec-scene-tunables.md) |
| `piece-contract` | Shared conventions every piece factory follows — **paint application, slot/DOM shape, payload trust, draft-first, test style, registration**, the **group-registration module** (`ui/gui-lego/pieces/storyScene.ts`) and the **piece CSS location convention**. Exists because a factory gets **no** theme from `RecipeMount` (`RecipeMount.tsx:43-53`) and must apply it itself, and because without a group module a piece is never registered and renders as an unstyled fallback div | gui-lego `composition`, `RecipeMount` | [story-scene/spec-piece-contract.md](story-scene/spec-piece-contract.md) |
| `localization` | Whether scene copy is localized (lingui is installed and used by the four stage files), and which guard governs the surface (`vocabularyGuard`, `reactivityGuard`, `magnitudeGuard`) | gui-lego, `i18n/` | [story-scene/spec-localization.md](story-scene/spec-localization.md) |
| `actor-cast` | Actor identity registry (`penny`, `dave`) + per-actor asset roles for **N** sprites; no plant/zombie side axis | `scene-script` (ids) | [story-scene/spec-actor-cast.md](story-scene/spec-actor-cast.md) |
| `theme-packs-scene` | `actor.*` and `scene.*` theme packs; **widens the closed `ThemeKind` union** (ask-first gui-lego amendment) | gui-lego `theme-packs` taxonomy | [story-scene/spec-theme-packs-scene.md](story-scene/spec-theme-packs-scene.md) |
| `actor-sprite` | The sprite element **plus the honest labelled shape** (name + initial + pack accent) when art or variant is missing; extends `ActorFrame`, invents nothing | `actor-cast`, `theme-packs-scene`, `ui/actor/shared.tsx` | [story-scene/spec-actor-sprite.md](story-scene/spec-actor-sprite.md) |
| `name-tag` | Speaker label + pack-owned paint; absent on a narration beat | `theme-packs-scene` | [story-scene/spec-name-tag.md](story-scene/spec-name-tag.md) |
| `advance-control` | Next / final-label / **always-present skip**, with pending-disabled state; one piece, both verbs | — | [story-scene/spec-advance-control.md](story-scene/spec-advance-control.md) |
| `scene-progress` | Beat `n of m` with its accessible label and pips | — | [story-scene/spec-scene-progress.md](story-scene/spec-scene-progress.md) |
| `dialogue-window` | The say window: line, teaching line, narration variant (no speaker); owns readability, not color | `name-tag` | [story-scene/spec-dialogue-window.md](story-scene/spec-dialogue-window.md) |
| `actor-portrait` | One actor in a **slot array** plus `speaking \| inactive` state; resolves actor → sprite + variant; owns the fallback decision | `actor-sprite`, `actor-cast` | [story-scene/spec-actor-portrait.md](story-scene/spec-actor-portrait.md) |
| `scene-stage` | Compose root: full-bleed bed, band utilities, `data-cue` state, two-actor responsive layout, reduction-motion transition rules | `actor-portrait`, `dialogue-window`, `advance-control`, `scene-progress`, `shell-scene-size`, `band-compliance` | [story-scene/spec-scene-stage.md](story-scene/spec-scene-stage.md) |
| `cue-seam` | Typed cue ids and the FE-local rendering contract; **plus (absorbed 2026-09-15) the Unity-side channel** — director wiring (T27a) and delivery over the **shared** host bridge (T27b), never a second one | `scene-stage` | [story-scene/spec-cue-seam.md](story-scene/spec-cue-seam.md) |
| `story-scene-fold` | Pure VM: beat index, finish/ack state, script join, omit rules; `scene-script` → payloads | `scene-script`, `actor-cast`, `cue-seam` | [story-scene/spec-story-scene-fold.md](story-scene/spec-story-scene-fold.md) |
| `scene-trigger` | **Minimal trigger/eligibility contract** (owner N3): "should this scene play for this player now?" — the seam a later story-progression program builds on. Does **not** author story arcs or schedule beats | `scene-script`, story ledger read | [story-scene/spec-scene-trigger.md](story-scene/spec-scene-trigger.md) |
| `story-scene-host` | **Reusable host** (owner N2): `StorySceneHost` owns beat index, ack mutation, continue-to-lawn, and mounts `RecipeMount` inside `DialogShell`. Scene 2 = data + a trigger, not a copied dialog | `recipe-wire`, `scene-trigger` | [story-scene/spec-story-scene-host.md](story-scene/spec-story-scene-host.md) |
| `recipe-wire` | The `story-scene` recipe + piece registration + closed surface bus; migrates the prologue off the god TSX onto `StorySceneHost` | all of the above | [story-scene/spec-recipe-wire.md](story-scene/spec-recipe-wire.md) |

**Piece specs are authored here, not in `gui-lego/`** (locked assumption 2): promoting them into the
gui-lego fence would cross another program's ownership mid-flight. Promotion is a follow-up when
decision 4's reveal adoption happens.

---

## Build order

```text
Wave 0 — unblock + shell seam + shared conventions   (independent; land immediately)
  shared-kit-fix           (turns the two red guard suites green — N1)
  band-compliance          (this program's own band violations; needs the green baseline)
  shell-scene-size         (full-bleed scene bound + GG-61 exemption — S1)
  scene-tunables           (number homes, so no later module invents a const)
  piece-contract           (paint/slot/DOM conventions, before any piece exists)
  localization             (i18n throughout, English default — S4)

Wave 1 — contracts
  scene-script      →      actor-cast
  scene-trigger            (minimal eligibility seam — N3)

Wave 2 — theme
  theme-packs-scene        (ask-first: ThemeKind widen — S2)

Wave 3 — leaf pieces
  actor-sprite · name-tag · advance-control · scene-progress
  dialogue-window          (needs name-tag)

Wave 4 — composite pieces
  actor-portrait           (needs actor-sprite)
  scene-stage              (needs the four composites + shell + band)
  cue-seam

Wave 5 — fold + host + surface
  story-scene-fold    →    recipe-wire   (recipe + registration + bus)
                          →    story-scene-host   (reusable host — N2)
                          →    prologue migration + owner visual gate (N4)
```

**Critical path:** `scene-script → actor-cast → theme-packs-scene → actor-sprite → actor-portrait →
scene-stage → story-scene-fold → recipe-wire → story-scene-host → prologue cutover`.

**Wave 0 is genuinely independent** except `band-compliance`, which wants `shared-kit-fix` first so a
green guard baseline exists to prove the band fix against.

---

## Ownership splits (binding)

| Concern | Owner | Must not |
|---|---|---|
| Scene stage, actor, window, controls pieces | `story-scene` | Fork a menu panel recipe, or a second band-3 shell |
| **The four shared-kit red lines** | `story-scene` (`shared-kit-fix`, owner N1) | Widen `BANNED_WORDS`, delete a guard assertion, or absorb the four unrelated band violations |
| **The stray-tier violations on other surfaces** | `story-scene` (**absorbed 2026-09-15** → T24) | Fix a tier by adding a band token; claim jsdom proves paint order |
| **`layerStack` access outside `shell/`** | `story-scene` (**absorbed** → T25) | Widen the import guard; move `mapChromeMute` away from its three callers |
| **`OnboardingReveal` presentation** | `story-scene` (**absorbed** → T26), **presentation only** | Edit `standalone/spec-first-session-progression.md` or change the reveal's data/lifecycle |
| `DialogShell` `size` contract | `story-scene`, **shared shell** (`shell/`) | Move the scene off band 3; change an existing caller's geometry; edit GG-61 |
| **The GG-61 exemption text** | `story-scene` (`shell-scene-size`) | Let it drift into a general "scenes may overflow" claim — it is scoped to `size="scene"` |
| Band allowlist entry + `z-index` fix | `story-scene` (`band-compliance`) | Widen the allowlist without justification, or bypass `bandGuard` |
| `ThemeKind` widen + `actor.*`/`scene.*` packs | `story-scene` with gui-lego review | Add a pack kind without widening the closed union; private hex in a piece |
| Beat copy / cue ids / beat order | `scene-script` data | Put scene copy in a component `const`, or author it by hand in a generated tree |
| **Message ids + locales** | `story-scene` (`localization`) | Hard-code a player string; use a bare `t`; ship a message without `extract` |
| **Scene eligibility** | `scene-trigger` (server ledger is authority) | Invent eligibility, order scenes, schedule arcs, or write from the trigger |
| **Host wiring (beat index, ack, continue)** | `story-scene-host` | Copy the wiring per scene; put scene markup in the host; change the ack story id/version |
| Cue effect rendering (FE) | `story-scene` (`cue-seam`) | Bind a key, open a socket, or invent engine vocabulary |
| **Unity-side `rift.*` VFX wiring** | `story-scene` (**absorbed** → T27a/b) | Build a **second** FE→host channel — the bridge is `rift-gate-ideal.md` decision 9's; or leave `onboarding-rift-todo.md` T12–T14 open beside this |
| **The FE↔host bridge mechanism itself** | **Sibling** `rift-gate-ideal` (decision 9) | Redefine it here; this program **consumes** it. ⚠️ **2026-09-23 — the bridge now EXISTS**, so "no bridge" is no longer a reason to stop: `OverlayCommandNames.Hide` = `overlay.hide` (`gk-core/src/FusionRpg.Core/Overlay/OverlayCommandNames.cs:19`), route `POST /api/overlay/leave` (`gk-core/src/FusionRpg.Server/OverlayEndpoints.cs:21`), injector arm (`gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:112-114`), FE sender (`gk-web/web/fusion-rpg-web/src/lib/bus/overlay.ts:13-14`). Its vocabulary holds exactly one verb, so T27b needs a **new verb** (an owner ruling) plus `src/` edits, and locked decision 4 still says the FE owns the cue. T27b is blocked on those, not on a missing channel |
| First-session reveal **contract** + `spec-first-session-progression` | **Sibling** `spec-first-session-progression` | Change its checkpoint semantics (only presentation is absorbed) |
| Rift Gate mechanism (overlay transport, host selection, first-open capture) | **Sibling** `rift-gate-ideal` | Decide its transport here |
| **`gk-core/scripts/verification-boundaries.v1.json` / `verify-change.py` / `test_fast.py`** | **Sibling** `verification-boundaries-20260913-6f31` (**active**) | Edit them — the FE verification mapping stays follow-up **F1**, un-absorbable |

---

## Locked assumptions

1. **Band 3 stays.** The scene is a band-3 `DialogShell` surface (decision 1) with a **full-bleed
   `size`** (S1) and a **scoped GG-61 exemption** argued in this map — not a new band, shell, or GG-5
   amendment, and not a silent violation.
2. **Piece specs live under `story-scene/`** for this program; gui-lego promotion is a later,
   separately-owned increment.
3. **Two actors minimum** (decision 2): `actor-portrait` is an array and the narrow stack rule is
   real work, not deferred.
4. **The FE owns the cue** (decision 3): `data-cue` today, the host bridge is a named seam.
5. **Skip is always available** (decision 5) and writes the same terminal state as watching a scene.
6. **A reveal is a one-beat scene** (decision 4): the shared pieces are designed to be adopted by
   `OnboardingReveal` later, without being edited here.
7. **Generated trees are never hand-edited.** Beat copy is authored content (`scene-script`), not a
   seedsmith/`*Gen` output — but if a scene script ever moves under a generated tree, the generator is
   the only edit path.
8. **No engine vocabulary on the player surface.** No `cueId`, `storyId`, `.md` paths, or author notes
   in player-visible text — including the two shared-kit leaks `shared-kit-fix` now closes.
9. **Eligibility is server-owned** (N3): `scene-trigger` reads and narrows; it never invents, orders,
   or schedules scenes.
10. **All player text is localized** (S4) through lingui with English as the default locale.
11. **The prologue's durable contract is frozen**: story id `rift-prologue`, version `1`.
    `storyContract.ts` does not exist under that name anywhere in `web/` (corrected 2026-09-20); the
    closest live candidates are `contract/types.ts` (StoryId typing) and
    `features/story-scene/sceneTrigger.ts`, neither verified against this row's specific claim in
    this pass. Extraction into a host must not change either the id or the version, or acknowledged
    ledger rows stop reconciling.

---

## Explicitly out of this program

| Out | Why / owner |
|---|---|
| **Story arcs, beat scheduling, chapter sequencing** | Owner N3: `scene-trigger` adds an **eligibility seam only**. Authoring what story happens when is a future program |
| **The FE↔host bridge mechanism** | Sibling `rift-gate-ideal` decision 9 owns it. T27 **consumes** it; it does not create a second channel. **2026-09-23:** that channel shipped as `overlay.hide` (one verb); a story cue needs a new verb in it, which is an owner ruling plus `src/` work — see the row above |
| **The first-session reveal's contract, data, and lifecycle** | Sibling `spec-first-session-progression`. T26 absorbs **presentation only** and does not edit that spec |
| **`gk-core/scripts/verification-boundaries.v1.json`, `verify-change.py`, `test_fast.py`** | Fenced by the **active** session `verification-boundaries-20260913-6f31`. Stays follow-up **F1** |
| Dr. Zomboss as a v1 actor | Deliberate story deferral (owner) |
| Branching narrative / ink / Yarn Spinner | No branch exists; revisit then |
| Amending GG-61 in `game-gui-principles.md` | S1 records a **scoped exemption** citing GG-61; changing a GG is an owner/ADR action |
| Editing `AGENTS.md`, `CLAUDE.md`, `.kilo/`, `docs/ideas/*` | Local-only / other sessions' fences |
| `SPEC.md`, bare `tasks/plan.md`, bare `tasks/todo.md` | Parallel programs — never written |
| Any plan or todo file | `/plan` is a separate phase |

**Absorbed into this program (owner, 2026-09-15):** the stray-tier violations on other surfaces (T24),
the `layerStack` import behind a shell accessor (T25), `OnboardingReveal`'s **presentation** (T26), and
the Unity `rift.*` cue channel (T27a/b). Absorbing T27 also **retires the duplicate ownership** in
`tasks/onboarding-rift-todo.md` T12–T14, which describe the same injector work.

---

## Success criteria (program-level)

- The prologue renders from `recipe-wire` **through `StorySceneHost`** (recipe + fold + `RecipeMount`);
  no god TSX remains, and `RiftPrologueDialog` is a thin wrapper.
- Every piece has a draft HTML and a registered factory; no piece hard-codes pack paint
  (`piece-contract`).
- Two actors render side by side at desktop width and **stack speaker-forward** at the narrow
  breakpoint; no actor is hidden.
- The scene is **full-bleed and never scrolls**; the advance control stays reachable on a short
  viewport.
- A missing sprite renders the **name-labelled** honest shape, distinguishable per actor.
- **Both guard suites are green**: `src/shell/bandGuard.test.ts` (this program's paths, plus
  `shared-kit-fix`'s lines) and `src/i18n/` (`shared-kit-fix` fixes all four).
- The FE owns the cue; `data-cue` drives the FE effect; no injector story engine exists.
- Skip is present on every beat and writes the same terminal state as completion.
- **All** story text is localized (lingui, English default) and the pseudo locale renders no English.
- No player-visible engine vocabulary in any scene surface.
- Scene eligibility comes from the server ledger through `isSceneEligible`; the FE never invents it.
- Every tunable is in `gk-core/data/tuning/story-scene-ui.v1.json`; every structural cap is in
  `storySceneTokens.ts` with a why-not-tunable comment; no balance number is a `const`.
- The **owner visual gate** (N4) is recorded with before/after screenshots.

---

## DESIGN-GATE §5 checklist

```
[x] I identified the subsystem(s) this touches.
[x] I established and recorded this session's boundary before any edit.
[x] I read every doc in the §1 row(s) for those subsystems, this session.
[x] I checked decisions.md for a lock covering this.
[x] Every factual claim cites file:line.
[x] I verified claims against CODE, not comments.
[x] I read the surrounding section of every rule I quoted.
[x] I tested (not assumed) any constraint I am reporting — the band guard was RUN
    (`npx vitest run src/shell/bandGuard.test.ts`: 3 failed / 8 passed) and so was the i18n
    suite (`npx vitest run src/i18n/`: 1 failed / 57 passed), not inferred.
[x] Nothing contradicts a §2 invariant, or I named the contradiction explicitly.
[x] Corrections are propagated to prose, Structure, Testing, Boundaries, map, and tasks.
    The map, all 18 specs, and the ideal carry the audit's seven corrections (see the audit
    section below). Plan and tasks do not exist yet — this phase writes no plan; they inherit
    from this map at `/plan`.
[x] No assertion pins a derived-population count, an item total, generated text, or a per-cycle
    outcome. `maxBeatsPerScene` is a **structural bound on authored content**, not a population
    reading; the Rift script's length is asserted as a **reading of its own data**, and the script
    has a named owner.
[x] If this introduces or touches an event-refreshed cache (§2.16): N/A — no cache is introduced.
    The story ledger is read-through; the scene does not cache it.
[x] No acceptance criterion silently fixes an ordering that can vary in real play.
    The dual-write case is the acknowledgement (see `recipe-wire`); it is explicitly
    order-independent by using `finish(outcome)` as the single terminal path.
[x] If this feature produces or consumes an actor combat/derived magnitude: **N/A** — a story scene
    produces no combat, derived, or AppliedCombat magnitude. It reads no Hub output and folds no
    actor number. `ActorHub` gate does not apply. `magnitudeGuard` is likewise N/A (`localization`).
[x] Does not invent or extend a SOLID-violating parallel path (§2.15): the program **removes** a
    parallel path (the god TSX) rather than adding one; `cue-seam` is a named seam, not a second
    pipeline; `piece-contract` states an existing convention rather than adding a mechanism.
```

---

## Spec audit (2026-09-15, second pass) — what the first pass got wrong

The 16 first-pass specs were audited against the real `bindSurface` / `RecipeMount` / guard code.
**Seven real gaps** were found; three would have broken implementation on contact.

| Id | Severity | Gap | Where fixed |
|---|---|---|---|
| **G1** | **Blocking** | The fold spec invented a VM shape (`root`, a `payloads` map) that does not exist. `bindSurface` resolves binds against the VM object itself; `grep payloads` over `src/` finds no such mechanism | `spec-story-scene-fold.md` rewritten to the shipped convention |
| **G2** | **Blocking** | The recipe used `bind: "vm.root"`, gave slot children **no** `bind`, and used `$bindArray: "vm.actors"` for an array that lives on the **root payload**. With no `bind`, `getByPath` returns the **root** → every child receives the whole payload | `spec-recipe-wire.md` recipe corrected; a "every slot child declares a bind" assertion added |
| **G5** | **Blocking** | `nameTag` was specified at **VM top level**, but nested slots bind **parent-relative** (`bindSurface.ts:123-127`; verified against `condition-console.json`'s `cond-hero` → `shield`). A top-level bind resolves to `undefined` on the window payload → **every spoken beat silently loses its name tag** and only narration looks right | `spec-story-scene-fold.md`: `nameTag` moves onto `DialogueWindowPayload`; regression criterion added |
| **G3** | High | Eight piece specs said "pack owns paint" but **no spec said how a factory applies it**. `RecipeMount` applies `themeStyle`/`vfxClass` **only for pieces with no factory** (`RecipeMount.tsx:43-53`) — a registered factory renders unthemed unless it applies the theme itself | New `piece-contract` module + spec |
| **G4** | High | The recipe used the shared `phase-loading`/`phase-error` overlays, which render their own class name as **player-visible text** (`lifecycle.tsx:10-11`) → the scene would ship engine vocabulary | `spec-recipe-wire.md`: **no lifecycle overlays**, with the four real state owners recorded |
| **G6** | High | The fold spec instructed `if (key === "revision") continue;` — **the exact literal that trips `i18n/vocabularyGuard`** (`vocabularyGuard.ts:50` bans `revision`; both shipped folds are already red on it at `foldConditionSurfaceVm.ts:71` / `foldAptitudesSurfaceVm.ts:66`). A new spec would have **copied a live violation** | `spec-story-scene-fold.md` rule 10 + criterion: inherit the shared-kit fix, add no new violation |
| **G7** | Medium | No spec decided whether scene copy is **localized**, though lingui is installed (`@lingui/* ^5.9.5`) and used by all four stage files, and three guards (`vocabularyGuard`, `reactivityGuard`, `magnitudeGuard`) govern this tree | New `localization` module + spec |

### A second red suite was found (reported, not absorbed)

Beyond the band guard, `src/i18n/vocabularyGuard.test.ts` is **red on HEAD** (1 failed / 14 passed;
`src/i18n/` overall: 1 failed / 57 passed) and it constrains this program's surface directly:

| Violation | Note |
|---|---|
| `features/gui-lego/foldConditionSurfaceVm.ts:71` — `if (key === "revision") continue;` | The exact line G6 would have copied |
| `features/gui-lego/foldAptitudesSurfaceVm.ts:66` — same | Same |
| `ui/actor/shared.tsx:13` — `return "Retired";` | **A genuine player-visible leak**: `formatActorPhase` renders the engine enum word for a person's phase. This is the file `actor-sprite` extends, so it is named here as a **pre-existing defect the scene would inherit** — `actor-sprite` must not depend on that helper |

Both are **shared-kit** defects, not this program's, and neither is fixed here.

### Also verified during the audit

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


- **`data-sealed` is a dead attribute.** `RiftPrologueDialog.tsx:169` sets it from `beat.seal`, and
  **no CSS or test reads it** (`grep sealed` over `src/**/*.css` and `**.test.tsx` → nothing). So
  `seal?: boolean` is dead data, not merely coupled data — drop it, do not migrate it
  (`spec-scene-script.md`).
- **`RiftPrologueCueId` is consumed nowhere** outside its own file, so replacing it with `StoryCueId`
  breaks no external import.
- **`gk-core/tools/tuning/publish.py` edits existing tunables only** (`:131` — *"publish edits existing
  tunables, it does not add undocumented ones"*), so `gk-core/data/tuning/story-scene-ui.v1.json` must be
  **authored by hand once**, then becomes publishable. A sequencing note for `/plan`, not a blocker.
- **`tsconfig` has `resolveJsonModule: true`** and the FE already deep-imports `gk-core/data/tuning/*.json`
  (`shieldPriorityLabel.ts:5`), so the home-1 tuning file is genuinely loadable — the tunables split
  is real, not aspirational.

---

## Owner decisions (locked 2026-09-15) — all questions resolved

**Nothing is open. This map is approved and `/plan` + `/build full` are unblocked.**

| Id | Question | Owner decision | Consequence |
|---|---|---|---|
| **S1** | Scene geometry + narrow layout | **Full-bleed bound, actors stack speaker-forward** (not the recommended bounded box) | A scene is a viewport-fitting, **non-scrolling** band-3 surface. This **conflicts with GG-61** ("the shell never grows to swallow the viewport", `game-gui-principles.md` GG-61), so `shell-scene-size` must record a **scoped exemption with reasons**, not a silent breach — see "GG-61 exemption" below. Below 720px the two actors stack, speaker nearest the window; no actor is hidden |
| **S2** | `ThemeKind` widen | **Widen with `actor` + `scene`** (recommended) | One reviewed change; 4 packs on both design and FE sides; no faction or neutral overload |
| **S3** | Script home | **Typed TS module** (recommended) | `ActorId`/`StoryCueId` typos are compile errors |
| **S4** | Localization | **i18n throughout, default English like other UI** — not chrome-only | **All** player text goes through lingui (`msg` + `useLingui`), English as the default locale, matching the four stage files. This **supersedes** the recommended chrome-only split: beat `line`/`teaching` and actor `displayName` are **localized too**, which means `sceneScript`/`actorCast` become locale-aware sources and the `extract` step must be run and its output committed |
| **N1** | The four red guard lines | **Fix here in Wave 0** (recommended) | New `shared-kit-fix` module; `band-compliance`'s "guards green" criterion becomes achievable. The four unrelated band failures stay out of scope |
| **N2** | Reusable host | **Extract `StorySceneHost`** (recommended) | New module; the prologue becomes a thin wrapper; scene 2 needs no copied wiring |
| **N3** | Who triggers a scene | **Add a minimal trigger contract** (not the recommended "out of scope") | New `scene-trigger` module: an eligibility/trigger **seam** only. It must not grow into arc authoring or beat scheduling — that stays a future program, and the spec says so explicitly |
| **N4** | Visual gate | **Side-by-side owner gate** (recommended) | `recipe-wire` cannot be "done" on tests alone; before/after screenshots at the same viewport, owner confirms (`html-design-implementation.md:112`) |
| **N5** | Invented defaults | **Accepted as starting values** (recommended) | 720px collapse, 160px placeholder, `beatTransitionMs: 220`, `maxBeatsPerScene: 6`, `autoAdvanceMs: null` — all in data or structural tokens, none asserted as truth |

### GG-61 exemption (S1) — required, and it must be argued, not assumed

**The conflict, stated plainly.** GG-61 says *"Every band-2/3 shell (`PanelShell`, `DialogShell`)
declares a bounded height against the GG-36 viewport contract… The shell itself never grows past the
space the band model gives it."* The owner's S1 choice is a **full-bleed** scene — which is exactly
"grows to swallow the viewport" as written.

**Why an exemption is defensible (and why it is not a loophole).** GG-61's own rule text scopes itself
to **one entity's own content scroll** — its examples are *"one actor's 99-channel derived-stat
sheet, one item's affix list… one comparison table"*, and its rationale is that a dense entity needs a
bounded box so its body can scroll internally. **A story scene is not a dense entity and does not
scroll.** Its content is a fixed-aspect art bed plus one line of text, and it is **taller-content-free
by construction**: the beat cap (`maxBeatsPerScene`) and the one-line rule exist precisely so nothing
overflows. So the failure GG-61 prevents — a shell whose body outgrows the viewport and drags the
stage — cannot occur here.

**What the exemption must therefore carry, in `shell-scene-size`:**

1. The scene bound **fits the viewport** (no overflow, no stage scroll) — full-bleed in *area*, still
   bounded by the viewport contract.
2. The scene body **never scrolls**; overflow is a **content defect** caught by the beat cap, not
   absorbed by a scrollbar.
3. `size="default"` callers keep the existing bounded card unchanged; GG-61 continues to govern them.
4. The exemption is **scoped to `size="scene"` only** and names GG-61 explicitly, so a later reader
   sees a deliberate, reasoned exception rather than a violation someone forgot about.

**If the owner prefers to avoid the exemption entirely**, the recommended bounded box from the
alternatives remains available and GG-61 needs no change — but that is S1's call, already made.

**What this program does not do:** it does **not** edit `game-gui-principles.md`. Amending a GG is an
owner/ADR action; the spec records the exemption and cites it instead.

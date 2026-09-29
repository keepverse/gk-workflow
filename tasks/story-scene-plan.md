# Implementation plan: story-scene — reusable story-scene presentation system

**Status:** **approved 2026-09-15** (owner). Phase 2 (Plan) complete; implementation is authorized
via `/build full`. No code written from this phase.
**Program id:** `story-scene`
**Capability map:** [docs/architecture/story-scene-map.md](../docs/architecture/story-scene-map.md) (21 modules)
**Ideal:** [docs/architecture/story-scene-ideal.md](../docs/architecture/story-scene-ideal.md)
**Module specs:** [docs/architecture/story-scene/](../docs/architecture/story-scene/) (21 specs)
**Task list:** [tasks/story-scene-todo.md](story-scene-todo.md) — **27 tasks, 7 checkpoints, 0 gates**
(23 for the original program + 4 absorbed at the owner's direction)
**Sibling programs (not touched):** [rift-gate-ideal.md](../docs/architecture/rift-gate-ideal.md) ·
[standalone/spec-first-session-progression.md](../docs/architecture/standalone/spec-first-session-progression.md)

---

## Overview

Turn the four-beat Rift prologue into the **first consumer** of a reusable, module-first story-scene
system: a scene stage that plays illustrated, beat-by-beat narrative with actors, a dialogue window, an
advance control, and a progress indicator — composed from Lego pieces, themed by packs, fed by a pure
fold, mounted by a reusable host inside the existing band-3 shell.

Today the prologue is a 193-line component (`features/onboarding/RiftPrologueDialog.tsx`) with six
independent state concerns (`:62-68`), a `BEATS` const (`:19-44`), inline scene markup (`:167-188`), a
one-shape-fits-all missing-art fallback (`:170-174`), a hard-coded speaker color (`:185`), and two
band-guard violations. Scene 2 today means a second copy of all of it.

After this plan, scene 2 is **data + a trigger entry**.

**The program is deliberately presentation-only.** It does not own story arcs, scheduling, the Unity
VFX channel, the Rift Gate mechanism, or the first-session reveal sequence — each has its own owner
(map §"Ownership splits").

---

## Architecture decisions (locked by the map and the owner)

| # | Decision | Consequence for this plan |
|---|---|---|
| 1 | **Band 3 stays**; `DialogShell` gains an optional `size` (S1) | `shell-scene-size` is a shared-shell change; every existing caller must render unchanged |
| 2 | **Full-bleed scene with a scoped GG-61 exemption** (owner S1) | The highest-risk item in the plan. `100dvh`, `overflow: hidden`, art scales before the controls. Its only real proof is the visual gate |
| 3 | **Two actors, stacked speaker-forward below 720px** (owner S1) | `actor-portrait` is an array from day one; the stack rule is real work |
| 4 | **The FE owns the cue** (decision 3) | `data-cue` drives a CSS effect; `cue-seam` is a *named* seam — no injector work in this plan |
| 5 | **Skip always available, one terminal path** (decision 5) | Preserved verbatim through the host extraction |
| 6 | **A reveal is a one-beat scene** (decision 4) | `scene-progress` omits itself when `total <= 1`; `OnboardingReveal` is **not** edited here |
| 7 | **Typed TS module for the script** (S3) | `sceneScript.ts` — compile-time `ActorId`/`StoryCueId` checking |
| 8 | **i18n throughout, English default** (S4) | Message-id resolution in the fold; pseudo-locale render is the acceptance test; `extract` output is committed |
| 9 | **Fix the four red guard lines here** (N1) | Wave 0, first task; two of the four are inside this program's path |
| 10 | **Extract `StorySceneHost`** (N2) | The prologue becomes a thin wrapper; the ack contract (`rift-prologue`/`1`) is frozen |
| 11 | **Minimal trigger contract** (N3) | `scene-trigger` reads the server ledger and **narrows** only — no arcs, no ordering |
| 12 | **Owner visual gate required** (N4) | `recipe-wire` cannot close on tests alone |
| 13 | **Invented defaults accepted** (N5) | 720px collapse, 160px placeholder, `beatTransitionMs: 220`, `maxBeatsPerScene: 6`, `autoAdvanceMs: null` |

---

## Dependency graph

```text
shared-kit-fix ──┐
                 ├──> band-compliance ──> shell-scene-size ──┐
scene-tunables ──┘                                           │
                                                             │
piece-contract ──────────────────────────────────────────────┤
                                                             │
scene-script ──┬──> actor-cast ──> theme-packs-scene ──┐      │
               │                                        │      │
               └──> scene-trigger                       │      │
                                                        ▼      ▼
localization ──────────────────────────────────> actor-sprite  │
                                                 name-tag      │
                                                 advance-control│
                                                 scene-progress │
                                                 dialogue-window│
                                                        │       │
                                                        ▼       │
                                                 actor-portrait │
                                                 cue-seam       │
                                                        │       │
                                                        ▼       ▼
                                                    scene-stage
                                                         │
                                                         ▼
                                                 story-scene-fold
                                                         │
                                                         ▼
                                                    recipe-wire
                                                         │
                                                         ▼
                                                story-scene-host
                                                         │
                                                         ▼
                                          prologue cutover + owner visual gate
```

**Critical path:**
`scene-script → actor-cast → theme-packs-scene → actor-sprite → actor-portrait → scene-stage →
story-scene-fold → recipe-wire → story-scene-host → cutover`.

---

## Vertical slicing — the honest version

The skill's default is "one complete user-visible path per task". This program is **presentation
infrastructure**, so most tasks are pieces that cannot individually deliver a user-visible path — a
`name-tag` alone shows nothing. Pretending otherwise would produce 22 fake "the player can now see X"
claims.

So slicing is done at the level where it is real:

| Slice | Complete path it delivers | Tasks |
|---|---|---|
| **1. Green, safe baseline** | The repo's red guards go green and the shell can host a full-bleed surface | T1–T5 |
| **2. A scene has data and is allowed to play** | A script resolves, a cast resolves, the server says whether to play | T6–T9 |
| **3. A scene can be painted** | Packs resolve actor identity and scene mood | T10–T11 |
| **4. One piece renders and proves its paint** | Each leaf piece: draft HTML, registered factory, themed DOM | T12–T16 |
| **5. Two actors on a real stage** | The compose root with cue state, full-bleed, stack rule | T17–T19 |
| **6. The real prologue, migrated** | **The complete path**: server eligibility → host → fold → recipe → pieces → acknowledgement → lawn | T20–T23 |
| **7. Absorbed: the tree is actually clean, and the pieces serve a second consumer** | Fully green guards; a reveal renders through the shared pieces; a cue reaches the game | T24–T27 |

Every task is **S or M** (≤4 files). No XL — T27's original L sizing was split into T27a/T27b.

---

## Phases and checkpoints

### Phase 0 — Green baseline and seams (T1–T5)

Turns the two red guard suites green, establishes the number homes, adds the full-bleed shell bound
with its GG-61 exemption, fixes this program's band violations, and lands the piece registry seam.

### Checkpoint A — after T1–T5

- [ ] `npx vitest run src/i18n/` → 0 failed
- [ ] `npx vitest run src/shell/bandGuard.test.ts` → 0 failed for this program's paths
- [ ] `DialogShell` still renders every existing caller identically (`shells.test.tsx` green)
- [ ] A `size="scene"` shell renders full-bleed with no scroll container
- [ ] `gk-core/data/tuning/story-scene-ui.v1.json` + `storySceneTokens.ts` exist; no balance number in a `const`
- [ ] **Review with owner before proceeding** (this is where the full-bleed look is accepted in the shell)

### Phase 1 — Contracts (T6–T9)

The script, the cast, the eligibility seam, and the localization scheme.

### Checkpoint B — after T6–T9

- [ ] The four Rift beats exist as data with copy parity to `docs/ideas/onboarding-gnome-teaser.md`
- [ ] Beat 3 is narration (no `speakerId`); `"Gnome signal"` is gone; `seal` is gone
- [ ] Penny and Dave resolve, with distinguishable fallbacks
- [ ] `SanctumStage` reads `isSceneEligible`; its observable behaviour is unchanged
- [ ] Every beat/actor/message id resolves; a missing id fails a test

### Phase 2 — Theme (T10–T11)

`ThemeKind` widens; four packs on both design and FE sides.

### Checkpoint C — after T10–T11

- [ ] `listThemePacks()` includes all four new packs (derived, not a literal count)
- [ ] `actor.penny` and `actor.dave` resolve to **different** accent paint
- [ ] Unknown ref falls back to `neutral`

### Phase 3 — Leaf pieces (T12–T16)

`actor-sprite`, `name-tag`, `advance-control`, `scene-progress`, `dialogue-window`.

### Checkpoint D — after T12–T16

- [ ] Every piece has a draft HTML that exists
- [ ] Every factory applies `themeStyle`/`vfxClass` to its landmark root (asserted)
- [ ] `actor-sprite` with a null URL renders the **name-labelled** shape, distinct per actor
- [ ] A narration beat renders **no** name-tag node
- [ ] Skip renders on every beat including the last
- [ ] No piece hard-codes a player string or an identity color

### Phase 4 — Composite pieces (T17–T19)

`actor-portrait`, `cue-seam`, `scene-stage`.

### Checkpoint E — after T17–T19

- [ ] Two actors render side by side ≥720px and **stack speaker-forward** <720px; neither is hidden
- [ ] Full-bleed at `100dvh`: the advance control and window are reachable **without scrolling**
- [ ] The art bed scales down before the window or the control
- [ ] `prefers-reduced-motion` makes the beat transition and sprite swap instant
- [ ] Zero `z-index`/`z-*` in the stage and its CSS

### Phase 5 — Fold, surface, host, cutover (T20–T23)

The pure fold, the recipe + bus, the reusable host, and the real prologue migration with the owner
visual gate.

### Checkpoint F — Program complete

- [ ] The prologue renders from `recipe-wire` through `StorySceneHost`; no god TSX remains
- [ ] `RiftPrologueDialog.test.tsx` passes **unchanged** against the wrapper
- [ ] The ack call is still `{ storyId: "rift-prologue", version: 1, outcome }`
- [ ] Skip on every beat; one terminal path; failure still bypasses to the lawn
- [ ] A **second synthetic script** renders through the same host with no host edit (the reuse proof)
- [ ] Pseudo locale renders **no** English from window/name tag/progress/controls
- [ ] `npm run build` + `npm run check:bundle` pass; Phaser/recharts stay off the entry chunk
- [ ] **Owner visual gate recorded**: before/after screenshots, same viewport, paths in the task

### Phase 6 — Absorbed scope (T24–T27)

**Added 2026-09-15 at the owner's direction ("absorb them").** The coverage audit had listed three
areas as owned outside this program; they are now in scope, and absorbing them **also resolves two
duplicate-ownership conflicts** the audit had surfaced.

| Task | What it absorbs | Conflict resolved |
|---|---|---|
| **T24** | The three remaining stray-tier violations (`conditionConsole.css:229`, `shieldConsole.css:100`, `dev/PhaserSceneSwitchPocPage.tsx:284`) → `bandGuard.test.ts` **fully green** | None (plain defect) |
| **T25** | The `layerStack` import outside `shell/` (`mapChromeMute.ts:5-6`) → a **shell-owned accessor** the stage delegates to | None (guard-forbidden import) |
| **T26** | `OnboardingReveal` adopts the shared pieces (decision 4 made real) | **The reveal's contract stays the sibling program's** — presentation only, its spec is not edited |
| **T27a/b** | The Unity-side `rift.*` cue channel | **Two:** injector VFX work is also owned by `onboarding-rift-todo.md` T12–T14 (OPEN), and the FE→host transport is owned by `rift-gate-ideal.md` decision 9. T27 **closes the duplicate task list as superseded** and **consumes the shared bridge rather than building a second channel** |

> **State 2026-09-23 (lane `story-scene-1`) — `tasks/story-scene-todo.md` is the maintained list; this
> table and the checkpoint copy below are the plan-time view.** T27a's in-fence half landed
> (`scripts/prove-vfx.ps1` gained the four rift cases; the live run stays owner-run). T27b's recorded
> blocker is **stale**: the FE→host channel shipped as `overlay.hide`, so T27b is blocked on the lane
> fence + a new-verb owner ruling, not on a missing bridge. Checkpoint E is closed; F and G are closed
> except for the named owner / other-program items. `OnboardingReveal` (above) does render through the
> shared pieces, and `RiftPrologueDialog.test.tsx`'s "unchanged" box owes the manager an erratum —
> both with evidence in the todo.

### Checkpoint G — absorbed scope complete

- [ ] `npx vitest run src/shell/bandGuard.test.ts` → **0 failed** (all 11)
- [ ] `npx vitest run src/i18n/` → **0 failed**
- [ ] Radial label, shield meta, and dev panel visually correct after the tier removals
- [ ] `OnboardingReveal` renders through the shared pieces; its tests pass **unchanged**
- [ ] No `scene-progress` node in the reveal (the one-beat omission proven on a real consumer)
- [ ] The story cue reaches the game **live** (`prove-vfx.ps1`), or T27b is recorded as bridge-blocked
- [ ] `onboarding-rift-todo.md` T12–T14 closed as superseded — one list owns the VFX wiring
- [ ] **Owner confirms the reveal still looks right** (another program's surface)

---

## Gates: none — and why (checked, not assumed)

The skill requires every pre-work gate to be tested against two questions before it is written. Applied
honestly to this plan:

| Candidate gate | Irreversible? | Verdict |
|---|---|---|
| "Wait for `ThemeKind` widen approval" | No — kinds can be removed; and **the owner already answered S2** (2026-09-15) | **Not a gate.** Ships as a task (T10) |
| "Wait for the GG-61 exemption to be formally accepted" | No — it is a documented, scoped, reversible prop comment; **the owner already chose S1** | **Not a gate.** Ships in T3, flagged to the owner at Checkpoint A |
| "Wait for another program's confirmation on the band allowlist" | No — one reviewed registry entry, revertible | **Not a gate.** Ships in T4 |
| "Wait for the FE verification-boundary mapping" | No — direct `npx vitest run` works today; the mapping is a convenience | **Not a gate.** Non-blocking follow-up (below) |
| "Stop before the prologue cutover, the surface is in use" | **Partly** — the cutover changes a live player surface | **Checkpoint, not a gate.** The work exists and is reviewable; the owner visual gate (T22) reviews it |

**I also checked the premise against the project's own source of truth.** `docs/architecture/decisions.md`
was read in this session: it contains **no row covering story-scene, `ThemeKind`, or `DialogShell`**, so
there is no standing lock to wait on and no "not yet approved" premise that holds. The only relevant
architecture rows are combat/Hub ones, which this program does not touch (it produces no magnitude).

**Conclusion: 0 pre-work gates, 6 review checkpoints.** Everything that could have been a gate either
has a reversible default or has already been answered by the owner.

---

## Verification boundary (a real defect, reported not compensated)

`gk-core/scripts/verification-boundaries.v1.json` maps only four **C#** projects
(`core`, `data`, `server`, `guard`) — **there is no `web` boundary**, and `scripts/test-fast.ps1`
requires `-Project` naming a C# test project. So the repo's sanctioned
`scripts/verify-change.ps1 -Paths …` workflow **cannot select FE tests** for any of this plan's paths.

Per `AGENTS.md` — *"An unmapped production path is a verification-boundary defect: add/repair its
mapping or report it; never compensate by running the full suite"* — this plan does **both**:

1. **Reports it** here and in the task list.
2. **Does not compensate by running the full suite.** Every FE task's verification uses the
   documented, focused commands directly:
   ```powershell
   cd gk-web/web/fusion-rpg-web
   npx vitest run <path-or-pattern>     # focused
   npm run build                        # tsc --noEmit + vite build
   npx vitest run src/shell/bandGuard.test.ts
   npx vitest run src/i18n/
   npm run check:bundle
   npm run test:e2e -- --grep story     # the visual gate
   ```
3. **Tracks the mapping repair as a non-blocking follow-up** (below), so this plan does not stall on it.

---

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **Absorbed scope collides with two live owners** (T26's reveal contract, T27's injector VFX tasks + bridge) | **High** — duplicate ownership is the drift that costs a re-discovery | T26 edits **presentation only** and its spec is untouched; T27 **closes `onboarding-rift-todo.md` T12–T14 as superseded** and **consumes** rift-gate's bridge instead of building a second one. Both are named in the tasks and in Checkpoint G |
| **Full-bleed + `100dvh` + no-scroll traps the player on a short viewport** (the S1 cost) | **High** — an unreachable advance control is a soft-lock | Explicit acceptance in T19: window + control reachable without scrolling; art bed scales **first**; e2e at a short viewport; visual gate at T23 |
| **Nested `nameTag` bind is parent-relative** (audit G5) | **High, silent** — every spoken beat loses its tag and only narration looks right | T20 asserts a spoken beat renders the tag; T21 asserts every slot child declares a `bind` |
| **A factory renders unthemed** because `RecipeMount` applies paint only to factory-free pieces (audit G3) | High, silent — packs resolve and never reach the DOM | T5 lands the rule; every piece task asserts pack paint on the DOM |
| **No piece factory is ever registered** — the group module and its entries were missing from the first plan (coverage audit G1) | **Blocking, silent** — the whole surface renders as unstyled fallback divs (`RecipeMount.tsx:35-56`) | T5 creates `ui/gui-lego/pieces/storyScene.ts`; T12–T19 each register their factory |
| **CSS paint order is the thing T24/T25 change and it is not jsdom-testable** | Medium — a tier removal can paint the wrong layer | Both tasks pair the deletion with a **recorded visual check**, not a unit assertion |
| **Band guard red on HEAD** | Medium — a red baseline cannot prove a fix | T1 (shared-kit) + T4 (band) + T24 (other surfaces) → fully green at Checkpoint G |
| **`vocabularyGuard` catches new literals** (audit G6) | Medium — a copied violation | T1 fixes the two `"revision"` literals; T20 inherits the fix; T9/T12–T16 run the real guard |
| **lingui extraction churn** (S4) | Medium — untranslated strings silently ship | T9 lands the scheme + pseudo harness; Checkpoint F runs the pseudo render |
| **The keyboard advance contract is silently dropped** in the cutover (coverage audit G4) | Medium — a real affordance regression | T19 owns it explicitly, preserving `RiftPrologueDialog.tsx:159-164` |
| **The visual gate has no mechanism** (coverage audit G5) | Medium — a binding gate that cannot be satisfied | T23 states the draft-HTML pair mechanism (mirroring `derived-ssot-side-by-side.spec.ts:31-46`) |
| **Entry-chunk growth** | Low–Medium | `npm run check:bundle` in every task that adds a module; Phaser/recharts untouched |
| **A second scene still needs a copied host** | Medium — the "reusable" goal fails | T22's acceptance includes a **second synthetic script** through the same host |
| **Generated-tree temptation** (fixing behaviour by editing seed JSON) | Medium | No task edits `gk-data/packs/fusion/data/seed/**` or `gk-data/packs/fusion/data/generated/**`; beat copy is authored `sceneScript` data |

---

## Non-blocking follow-ups (tracked, not gates)

| # | Follow-up | Why non-blocking |
|---|---|---|
| F1 | Add `web` boundaries to `gk-core/scripts/verification-boundaries.v1.json` so `verify-change.ps1` can select FE tests | **Cannot be absorbed:** a live session (`verification-boundaries-20260913-6f31`, status `active`) fences those exact files. The focused commands work today |
| ~~F2~~ | ~~Fix the four unrelated band violations~~ | **Absorbed → T24** |
| F3 | Fix `chrome.tsx:153,157` — dev footer copy shipped as defaults | Not one of the three areas named; a wording choice on another surface |
| ~~F4~~ | ~~Adopt the shared pieces into `OnboardingReveal`~~ | **Absorbed → T26** |
| ~~F5~~ | ~~Wire the Unity-side `rift.*` VFX recipes~~ | **Absorbed → T27a/T27b** |
| F6 | Promote the piece specs into `gui-lego/` | Deliberate: avoids crossing another program's fence mid-flight (map, locked assumption 2) |
| F7 | Add the `story-scene` row to the gui-lego menu-refactor queue | The queue file is outside this session's fence; one line |
| F8 | Wire or delete `lineRevealPerCharMs` / `autoAdvanceMs` | A decision, not a defect: v1 reads neither by design (no typewriter, no auto-advance) |

---

## Open questions

**None blocking.** All nine owner decisions are recorded in the map §"Owner decisions" (S1–S4, N1–N5).
The remaining uncertainty is *implementation detail* the specs already assign a home:

| Item | Where it is decided |
|---|---|
| Exact `scene` className values | `shell-scene-size` (T3), confirmed at Checkpoint A |
| `scene.<mood>` pack values | `theme-packs-scene` (T10), design SSOT |
| Message-id naming | `localization` (T9) |
| The retired-actor label wording | `shared-kit-fix` (T1) — **ask-first**, another surface's copy |

---

## Parallelization

| Safe in parallel (after Phase 1) | Must be sequential |
|---|---|
| T12–T16 (leaf pieces are independent given T5/T11) | T3 → T4 → T19 (shell → band → stage) |
| T13 + T14 + T15 (no interdependencies) | T20 → T21 → T22 → T23 (fold → recipe → host → cutover) |
| T6, T7, T8 (contracts, different files) | T10 → T11 (packs before a themed piece) |

**Needs coordination:** T21 (recipe) and T16/T19 (slots) — the slot names must match the map's recipe
sketch. Define the slot set once, in T5, before parallel piece work starts.

# Task list: story-scene

**Program:** `story-scene` · **Plan:** [story-scene-plan.md](story-scene-plan.md) ·
**Map:** [docs/architecture/story-scene-map.md](../docs/architecture/story-scene-map.md)
**Status:** **approved 2026-09-15** (owner). **27 tasks · 7 checkpoints · 0 gates.**
**Specs:** [docs/architecture/story-scene/](../docs/architecture/story-scene/) — 21 specs.

**All boxes below are closed by the header above**, per the HANDOFF section at the bottom of this
file (verified 2026-09-20,
`backlog-clean-up` `paperwork-reconcile` P2): "T1–T26 done and committed; T27 assessed," 44 feat/docs
commits 2026-09-15/16, merged via PR #7 `f384b3809` into `features/mega-merge` `4efa57e7`. Per this
program's own rule 4, the 261 boxes stay unticked individually; this line is the pointer
`pipeline-audit-v2` reads. T27b and the Follow-ups table's still-open rows (F3/F6/F8, corrected
2026-09-20: F1 SUPERSEDED, F7 done — `backlog-clean-up` BCU7.6) are real,
tracked separately (see `backlog-clean-up-todo.md` `ui-remainders`).

**Verification note (binding):** `scripts/verify-change.ps1` cannot select FE tests — the registry
(`gk-core/scripts/verification-boundaries.v1.json`) maps only C# projects, and `test-fast.ps1` requires a C#
`-Project`. Per `AGENTS.md` this is a **reported boundary defect** (follow-up F1), not a reason to run
the full suite. Every task below therefore names its **focused** command directly. Run from
`gk-web/web/fusion-rpg-web` unless stated.

**Second blocker on the same command (2026-09-23, lane `story-scene-1`):** it also refuses before
that, because there is **no `tasks/sessions/story-scene-1.json`** —
`pwsh -File scripts/verify-change.ps1 -Paths @('scripts/prove-vfx.ps1','gk-web/web/fusion-rpg-web/e2e/story-scene-visual.spec.ts') -Session story-scene-1`
→ `Exception: session record not found: story-scene-1` (`verify-change.ps1:98`). Creating that record
requires `/session-start`, which asks the owner by design, and `tasks/sessions/**` is outside every
lane's fence — the same "owner needed" item T23 recorded. Until it exists, FE work verifies with the
per-task focused commands + `npm run build` + the e2e gate, exactly as the tasks already say.

**Global rules for every task**

- **Never** edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, or `gk-data/packs/fusion/data/seed/atoms/generated/**` by hand.
- **Never** write `SPEC.md`, `tasks/plan.md`, or `tasks/todo.md`.
- **Never** run raw `git commit`/`push`; commit via MCP `repo-git.commit` with **explicit `paths`**.
  ⚠️ **Superseded 2026-09-23:** the git gate (the `repo-git` MCP server and the shell blockers) was
  retired by the owner on 2026-09-19 — agents commit with plain `git` and explicit paths
  (`AGENTS.md` "Git — plain git"). The T1–T22 commits above went through the gate; this lane's did
  not. Kept visible so the instruction is not read as current.
- Any new player string is a **lingui message** (`msg` + `useLingui`); a bare `t` fails
  `reactivityGuard`.
- Any piece factory applies `themeStyle`/`vfxClass` to its landmark root (spec `piece-contract` §1).

---

## Build progress (build full mode, 2026-09-15)

State written down so a resumed session does not re-derive it. Update in each task's own commit.

**Baseline:** HEAD `56221713`, working tree clean at start. Program base `e2182a3d`.

**Resume pointer (updated 2026-09-23, lane `story-scene-1`):** **T1–T26 done.** **T27a's in-fence half
is now done** (`scripts/prove-vfx.ps1` gained the rift cases; the live run stays owner-run) and
**T27b is re-blocked with a named, current dependency** (the bridge exists now; the fence and locked
decision 4 are what block it — see the T27 row). **Checkpoint E is closed**, and Checkpoint F/G are
closed except for the items whose dependency is named in place: the `RiftPrologueDialog.test.tsx`
"unchanged" erratum still owed by the manager, `tasks/onboarding-rift-todo.md` T12–T14 (outside this
lane's fence), the radial/shield visual capture (another surface), and the reveal look (owner). The
pseudo-locale box was **red** and is now green — it needed a code fix, not a tick; **F9** (the three
literals no locale could reach) was found by that test and closed the same lane, leaving **F12** (a
design question about the fallback initial) and the T27b/F-tree items. Open after this lane: **T27** (live half, owner-run),
**T27b** (fence + owner verb ruling), **F6** (fence — named dependency in the row above) and **F13** (the shared-port hazard,
infrastructure). **F10 is closed** (suite fully green: 386 files / 3239 tests) and **F8 is closed as a decided disposition** — the two feel keys
stay declared and unread on purpose, now written into `spec-scene-tunables.md`.
The rift-gate branch (`worktree-rift-gate-20260914`) carries everything — story-scene cutover,
visual gate, sibling migration, band cleanups, commit-tool push/pr extension, T26 reveal adoption —
merged with `origin/main` and proposed as PR #7. T27b is blocked by design (no shared bridge on
either side; FE keeps `data-cue`); T27a's core already exists via onboarding's recipe commit, with
reduced-motion, the prove case and live proof remaining there. Still open: build-phase session
record (for `verify-change.ps1`), the T24 visual-eyeball box, push of post-PR commits, PR review.

**Checkpoint D verified:** all five drafts exist; no piece source carries a hex literal or an identity
utility class; all five factories are registered in the `storyScene` group with the right slots
(`dialogue-window` alone declares `nameTag`); `src/ui/story-scene` + `src/ui/gui-lego` +
`keymapGuard` = **114 tests passed**.

**Phase 4 entry notes for the next session**

- **T17 `actor-portrait`** is the first composite: an **array** slot of actors, each carrying
  `speaking | inactive`. Owner decision 2 fixed two actors side by side as the floor, so this piece
  renders a set, not one actor; `actor-sprite` composes inside it. The variant-continuity rule
  (a speaker change must not reset the other actor's variant) belongs to the fold (T20), so T17
  renders whatever variant it is handed.
- **T18 `cue-seam`** owns the typed cue ids and the FE→class mapping through the **scene pack's**
  `vfx.select`. T11 already made `sceneMoodRefForCue` load-bearing for the `"scene"` ThemeKind arm, so
  T18 should extend that join rather than invent a parallel one.
- **T19 `scene-stage`** is the compose root and the highest-risk task: full-bleed, band utilities
  only (no `z-index`), the two-actor stack rule below 720px, reduced motion for transitions, and the
  no-scroll `100dvh` obligation. Its Verify names `bandGuard` and `stageHost`.
- **T23 carries three amendments** (all recorded in its row): the visual gate is **agent-performed**
  (owner reassigned the reviewer); the capture mechanism is the **live SPA** via the sibling
  `e2e/story-ui-evidence.spec.ts` pattern (mocking `**/api/onboarding/**`), not the draft-HTML
  fallback the spec assumed; and the peer-measured **short-viewport fit defect** (1280×600 clips 90px)
  must be fixed and its `known-defect` annotation flipped to `expect(bodyOverflows).toBe(false)`.
  **Measure the dialog body, never the document** — `DialogShell`'s body is `overflow-y-auto`, so the
  document never scrolls even when the scene is clipped, which is a false pass on a broken screen.

| Task | State | Gate rounds | Commit | Notes |
|---|---|---|---|---|
| T1 shared-kit fix | **done** | 2 (FAIL → PASS) | `75adc615` | Round 1 correctly rejected: the first word (`Consumed`) split vocabulary from the shipped `Fallen`. Also fixed CRLF pollution of `types.ts` caused by an experiment. |
| T2 scene-tunables | **done** | 1 (PASS) | `f21a4342` | Two spec-sketch deviations judged improvements and recorded: keys nested under `"scene"` (matches `delve-ui.v1.json`), and named primitive exports instead of one object (matches the cited `lawnPresentationTokens.ts`; `as const` is a no-op on a primitive). |
| T3 shell-scene-size | **done** | 1 (PASS) | `f34b1922` | 9 non-test consumers verified unchanged (1140 passed). Gate judged the GG-61 exemption sound and narrow, not a rationalization. |
| T4 band-compliance | **done** | 1 (PASS) | `8075215b` | Rims became real elements before the art (document order replaces the tier); gate verified the CSS paint-order equivalence. bandGuard 3 → 2 failures. |
| T5 piece-contract | **done** | 2 (FAIL → PASS) | `d6201573` | Round 1 correctly caught two real gaps: the group registration seam was missing, and the five shared slot names were pinned nowhere. Both fixed; the registration test now installs a fixture so it is not vacuous. |
| T6 scene-script | **done** | 1 (PASS) | `765f8635` | Beats are data with typed ids; beat 3 became narration; dead `seal` dropped. Gate re-derived copy parity against both the narrative source and the old const. |
| T7 actor-cast | **done** | 1 (PASS) | `27436465` | Gate's non-blockers were real and fixed here: dead `actorSpritePath`/`ACTOR_ASSET_VERSION` (a latent 404), an untested variant fallback chain, and a tautological assertion. |
| T8 scene-trigger | **done** | 1 (PASS) | `a951c993` | Server-authoritative eligibility seam; gate proved the `SanctumStage` refactor equivalent for every input. |
| T9 localization | **done** | 2 (FAIL → PASS) | `e0bf64bb` | Round 1 caught stale committed `.po` catalogs (CI would have thrown: extract ran before the test line that adds a reference). Also fixed a latent defect: pseudo-localization passed ICU messages through unmarked, so interpolated text escaped it. |
| T10 ThemeKind widen | **done** | 1 (PASS) | see log | Owner approved S2. Gate caught that the widen was **decorative**: `actorCast.ts` had its own inline `{ kind: "actor" }`, which compiles without `"actor"` being a union member. Fixed by typing the ref as `ThemeRef & { kind: "actor" }`, then proved load-bearing (reverting the arm fails `tsc`). Gate also noted `"scene"` is not yet enforced — carried into T11. |
| T11 scene/actor packs | **done** | 1 (PASS) | see log | Four packs on both sides + `sceneMood.ts` makes the `"scene"` arm load-bearing (proved: reverting it fails `tsc` at `sceneMood.ts:44`). T11 correctly broke three T10 assertions that encoded "no packs yet" — replaced with durable invariants. Gate independently reproduced a **pre-existing** `check:bundle` failure at base HEAD (entry 276.8 KB gz vs a 180 KB budget) — not this task's, flagged below. |
| T12 `actor-sprite` | **done** | 1 (PASS) | see log | The honest labelled shape (owner decision 2). Gate's non-blockers fixed here: the initial was not independently pinned, and a whitespace-only URL would have rendered `<img src="   ">`. Also corrected CSS token names — `--text`/`--muted` are defined **nowhere** in the tree (pre-existing dead fallbacks in older piece CSS), so the hint colour now uses the real `--color-muted`. |
| T13 `name-tag` | **done** | 1 (PASS) | `a1f384f4` | Pack-owned speaker paint; absent on narration. Gate found four corrections, all fixed: the doc comment/draft now quote the **rendered** contrast pair (accent on a 12% wash, 6.29–6.66 AA) rather than the unreachable `onAccent` plate; the draft lists all four muted values; the spec's rules 1/3 are corrected (they over-specified — `themeStyle` spreads a pack's `css` only, never `paint`); and two `check:bundle` lines my T23 amendment had wrongly dropped are restored. |
| T14 `advance-control` | **done** | 2 (FAIL → PASS) | `f84538e0` | Both verbs in one piece over the closed bus; skip unconditional. Round 1 caught two real blockers: the doc comment's literal `F10` tripped `keymapGuard` (a **new** red guard, green at base), and the draft used `--color-*` tokens the design kit does not define (unprefixed there), so it rendered colourless. Both fixed; the 44px floor is now wired from `storySceneTokens` instead of duplicated in CSS. |
| T15 `scene-progress` | **done** | 1 (PASS) | `6f48dcb7` | Beat n of m; one-beat scenes render nothing. Gate probe confirmed `0`/`-1`/`NaN`/`Infinity` all render no node, and that the test's `[2,3,4,7]` loop *exercises variety* rather than asserting the shipped script's length. Its non-blocker was real and fixed here: `.lego-grid.three` was **defined nowhere**, so three of my drafts silently rendered single-column — the class is now added to the shared kit. |
| T16 `dialogue-window` | **done** | 1 (PASS) | see log | The say window: line + optional teaching, narration variant, `nameTag` slot. Gate's non-blocker was a **real bug** and is fixed: the CSS read `--piece-scene-window`, which is defined nowhere, so the scene pack's window tint silently never reached the DOM and the fallback always won. It now reads the packs' actual `--scene-window`, pinned by a test that also asserts the packs declare it; the wrap test now asserts the wrapping declarations are present, not merely that truncation is absent. |
| T17 `actor-portrait` | **done** | 1 (PASS) | see log | One actor in a slot array with `speaking` state; non-color distinction (scale/lift/ring/opacity, grayscale-proof). Caught and fixed mid-build: the slot-map entry first used `"body"`, which the T5-pinned shared vocabulary forbids — corrected to `[]` with the render-time-composition rationale, since the sprite arrives via `slots.body` from the parent, not recipe binding. Also fixed my own test asserting full-HTML equality across a speaking flip (the root's own `data-speaking` legitimately changes — compare the sprite subtree) and a wrapper `aria-hidden` that would have silenced the fallback's labelled name. |
| T18 `cue-seam` | **done** | 1 (PASS) | see log | The union stays canonical in `sceneScript.ts` (zero churn to green, tested code); `storyCue.ts` owns the runtime-closed list + resolution + reduced-motion helper. Caught and fixed mid-build: my own test constructed the bad string it asserted against (testing a template literal, not the code) — corrected to assert the spread adds no key. The closed-`Record` exhaustiveness proof lives in non-test source because `tsconfig` excludes `*.test.*` from the build; the same pattern T11 already proved load-bearing by revert. |
| T19 `scene-stage` | **done** | 1 (PASS) | see log | The compose root: full-bleed bed, band-utility stacking, `data-cue`, two-actor layout with the stack rule. Caught and fixed mid-build, three times: (1) index-keyed wrapper divs around actors (pins nodes positionally across a speaker reorder AND violates the no-wrapper rule — render the array directly so each node's own key drives reconciliation); (2) a `transition:none` rule that applied always instead of only under reduced motion; (3) a missing `StoryCueId` import plus a missing title/subtitle render the test caught (contract table lists them as required). Also wired the three remaining acceptance items the first pass skipped: `beatTransitionMs` read from the version-pinned tuning JSON (never a literal), Enter/Space emitting `story-scene.advance` on the closed bus with the shipped target-guard (buttons keep native keys), and window autofocus with `tabIndex={-1}`. GG-11 holds by construction (pure render, touches nothing outside its root); the host's actual mount is T22's. |
| T20 `story-scene-fold` | **done** | 1 (PASS) | see log | Pure VM: bind-root shape per the shipped `ConditionSurfaceVm` convention (no invented `root`/`payloads` map — the audit correction G1). G5 honored: `nameTag` lives on the window payload, absent (not empty) on narration. Variant continuity derived per-actor from the script (stateless — same input always re-derives the same variant). Terminal is always present (skip guarantees it); last beat resolves advance/completed. `revision` stamped at construction via shorthand (never the banned string literal). Labels/shell text arrive host-resolved; content passes through verbatim. |
| T21 `recipe-wire` | **done** | 1 (PASS) | see log | Recipe both sides, byte-identical by convention (no parity test exists for other recipes either — the files are compared directly in-test). Root binds `vm`; every slot child declares a bind (walked like the mount does); actors uses parent-relative `$bindArray`; no `lifecycleOverlays` key (the G4 audit: shared phase pieces render engine text as player copy). Registration mirrors `registerCondition`; the bus is exactly four events. Caught and fixed mid-build: my own notes field lied about a design/runtime difference that does not exist (corrected to state byte-identity), and my first test imported docs JSON through the bundler with no precedent — switched to the fs-read the CSS-convention test already uses. |
| T22 `story-scene-host` | **done** | 1 (PASS) | see log | Host owns beat index, guards, ack, recovery, cues, fold→mount; renders no scene markup. All six acceptance items hold, reuse proven by a one-beat synthetic script with no host edit. Caught and fixed mid-build, four times: (1) the commit-gate double-click guard was timing-luck — measured inter-click gaps overlap (47ms double vs 60–110ms deliberate), and the OLD dialog double-advances too, so the guard is now structural: per-beat `RecipeMount` remount (second press lands on a detached node) + commit-gate for same-tick dispatch, focus repaired by the stage's own mount autofocus; (2) a host focus effect referenced a `windowRef` that no longer exists after the stage moved into the recipe — removed, the stage owns focus; (3) this build's `i18n._` takes values only with a string id, so progress resolves through `RIFT_PROLOGUE_PROGRESS.id` (catalog word order intact); (4) the fold's sprite `phase` widened to `string` against the closed `Phase` — now typed at construction. `npm test` (host+fold+recipe+stage+progress suites), `noStageSpecificBranch`, `tsc`, full `npm run build` all green. |

**Standing notes for the runner**

- Any file edited by an external script must keep **LF** endings — `.gitattributes` sets
  `* text=auto eol=lf`, and a python `write_text` on Windows converts the whole file to CRLF,
  which shows as a spurious diff.
- Every commit goes through `repo-git.commit` with explicit `paths`.
- **Accurate red-guard baseline at build start** (measured after T3 — my first note understated it
  as 3 failures): `npx vitest run` → **6 failed files / 321 passed (327)**, **8 failed tests /
  2593 passed (2601)**. All six are whole-tree guard scans over files this program has not touched;
  each was confirmed pre-existing at base HEAD by the T1 and T3 gates. The six:

  | Suite | Failing | Violations | Owner |
  |---|---|---|---|
  | `src/shell/bandGuard.test.ts` | 3 | `rift.css:48,59`, `conditionConsole.css:229`, `shieldConsole.css:100`, `dev/PhaserSceneSwitchPocPage.tsx:284`, `mapChromeMute.ts:5-6`, `RiftPrologueDialog.tsx:130` | **T4, T23, T24, T25** (this program) |
  | `src/theme/hexGuard.test.ts` | 1 | `foldConditionSurfaceVm.ts:41-45` hex paints | not this program |
  | `src/contract/contractGuard.test.ts` | 1 | `ui/actor/*Tab.tsx` surfaces | not this program |
  | `src/contract/delveViews.test.ts` | 1 | dev/lawn/commanders surfaces | not this program |
  | `src/contract/pendingCopyGuard.test.ts` | 1 | `lifecycle.tsx:43` `"Pending…"` | not this program |
  | `src/ui/disabledReasonGuard.test.ts` | 1 | `ui/gui-lego/pieces/condition.tsx` | not this program |

  The 5 non-band suites are **out of scope** and must not be absorbed into a task commit; they are
  reported here so their presence is never mistaken for a regression this program caused.

  **Delta 2026-09-16 (T22/T23 cutover, uncommitted):** the band row above is stale in our favour.
  `rift.css` (2 violations) is retired — file deleted, zero importers. `RiftPrologueDialog.tsx:130`
  is gone with the old markup; the render moved to `ui/story-scene/StorySceneHost.tsx` and the
  GG-53 allowlist was re-pointed per the guard's own note, so the dialog-band test is green again.
  Current: **2 failing tests / 9 passing** in `bandGuard.test.ts` — the survivors
  (`conditionConsole.css`, `shieldConsole.css`, `PhaserSceneSwitchPocPage.tsx`, `mapChromeMute.ts`)
  are byte-identical to HEAD (confirmed via `git status`) and owned elsewhere; they are not this
  program's and must not be absorbed either.

  **Delta 2026-09-16 later the same day: owner approved cleaning them ("clean 2 pre failure
  too") — bandGuard is now 11/11 green.** Checkpoint G's first box is ticked above with the
  evidence; the absorbed F2/T24 band items landed early in this session instead.

  **Delta 2026-09-23 (lane `story-scene-1`) — the real numbers, replacing the stale baseline above.**
  Every command below was run in `gk-web/web/fusion-rpg-web` on this worktree's HEAD; read the printed counts.

  | Command | Result |
  |---|---|
  | `npx vitest run src/ui/story-scene src/features/story-scene src/features/onboarding` (as T23 left it) | 16 files / **201 passed** |
  | same + `src/i18n` + `src/shell/bandGuard.test.ts` + `src/shell/noStageSpecificBranch.test.ts` + `src/stages/sanctum`, after this lane's changes | 29 files / **315 passed** |
  | guards alone (`bandGuard`, `noStageSpecificBranch`, `src/i18n`, `keymapGuard`) | 8 files / **84 passed** |
  | `npx vitest run src/ui/story-scene src/features/story-scene src/features/onboarding src/stages/sanctum src/i18n` (after F9/F11) | 27 files / **299 passed** |
  | `npx vitest run src/ui/gui-lego src/features/gui-lego` (after F3) | 22 files / **176 passed** |
  | guards alone (`bandGuard`, `noStageSpecificBranch`, `keymapGuard`) | 3 files / **24 passed** (the `src/i18n` files were in the 27-file run above; the earlier 8-file/84 run also covered them) |
  | `npm test` (whole FE suite, run 1) | 3 failed / 382 passed (385) files · 5 failed / 3229 passed (3234) tests |
  | `npm test` (run 2, same tree) | 2 failed / 383 passed (385) files · 2 failed / 3232 passed (3234) tests |
  | `npm run build` | `✓ built`, `tsc --noEmit` clean (2m 21s first, 14s incremental after) |
  | `npm run check:bundle` | exit 0 — "Phaser is absent from the entry chunk (assets/index-DevnuXQT.js) — OK" |
  | `npm run extract` | 44 → 46 messages; reference-line churn plus the two `story-scene.sprite.*` rows, committed with this lane |
  | `E2E_PREVIEW_PORT=4401 npx playwright test e2e/story-scene-visual.spec.ts --project=chromium` | **6 passed**, 20 PNGs + 5 reports, `bodyOverflows=false` ×20 |
  | `E2E_DEV_PORT=4402 npx playwright test e2e/story-scene-pseudo.spec.ts --project=pseudo-chromium` | **3 passed**, 12 PNGs + 3 reports, `pseudoMarked=true` and `bodyOverflows=false` everywhere |

  ⚠️ **The port override is not optional on this machine — see F13.** The plain `npx playwright test …
  --project=chromium` reuses whatever already listens on 4173 (`reuseExistingServer: !CI`), and while
  this lane ran, that was another worktree's preview server: two gate runs were served *that* tree's
  build and reported green. The evidence above was re-taken with `E2E_PREVIEW_PORT`/`E2E_DEV_PORT` set
  to ports only this lane used.

  | `npm test` (after the F10 fixes) | **386 files / 3239 tests passed, exit 0** — the first fully green full-suite run here |

  **The six-suite red baseline is retired, not fixed by us:** the five non-band suites named above
  were each empty by the time of this run — the only two failures left are
  `src/ui/disabledReasonGuard.test.ts:11` and the flaky `condition.waveCD` recharts `waitFor`
  (see **F10**) — **both were fixed in this lane** (a real GG-55 violation in `Workbench.tsx`, plus two lazy-mount
  wait budgets), so the line above is the historical record and the current baseline is the green run. Nothing in this
  lane's scope is red.
- **Pre-existing, not ours:** `npm run extract` deletes four stale `DelveStage.tsx` entries from
  the committed `messages.po` at HEAD. Unrelated to this program; do not absorb it into a task
  commit. (Gate T2 verified this and restored the catalogs byte-exactly.)
- **Pre-existing, not ours:** `npm run check:bundle` **fails at base HEAD** (exit 1, four lines:
  entry 276.8 KB gz vs a 180 KB budget, Phaser in the entry, plus `recharts`/`@xyflow/react` as
  deps). Independently reproduced by the T11 gate against `0d2cb650` in an isolated copy, so it is
  **not** this program's regression — T11's own delta is +0.5 KB gz. Two of the four lines are also
  stale against current design: `docs/design/tech-stack.md:122` retracted the plan to remove
  `recharts`/`@xyflow/react`, and `:289` says the check must **not** fail merely because
  presentation libs exist in `package.json`. **Do not absorb this into a task commit**, and do not
  let a red `check:bundle` alone block a task whose declared Verify does not name it.

---

## Phase 0 — Green baseline and seams

### Task 1: Fix the four shared-kit red-guard lines

**Spec:** `spec-shared-kit-fix.md` · **Size:** S (4 files)

**Description:** Make the two red guard suites green by fixing exactly four lines: the two `"revision"`
string literals that `vocabularyGuard` bans, the `formatActorPhase` leak that returns the engine word
`"Retired"` to a player, and the lifecycle piece that renders its own class name as visible text.

**Acceptance criteria:**
- [ ] `npx vitest run src/i18n/` reports **0 failed** (58 tests).
- [ ] `formatActorPhase` returns a player word for **every** `ActorPhase` case; no enum word escapes.
- [ ] The lifecycle piece renders **no** `phase-*` string as text; `data-phase` remains.
- [ ] Both folds still stamp `revision` and skip it during recursion — their tests pass unchanged.
- [ ] Exactly **four** files touched.

**Verification:**
- [ ] `npx vitest run src/i18n/`
- [ ] `npx vitest run src/shell/bandGuard.test.ts` (baseline captured before/after)
- [ ] `npm test -- --run foldConditionSurfaceVm` and `--run foldAptitudesSurfaceVm`
- [ ] `npm test -- --run lifecycle`
- [ ] `npm run build`

**Dependencies:** None · **Risk:** High (a green baseline gates every later claim)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/foldConditionSurfaceVm.ts`
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts`
- `gk-web/web/fusion-rpg-web/src/ui/actor/shared.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/lifecycle.tsx`

---

### Task 2: Number homes (`scene-tunables`)

**Spec:** `spec-scene-tunables.md` · **Size:** S (2 files)

**Description:** Create the two declared number homes before any piece can invent a constant: the
loadable feel/pacing file and the structural token module, each entry carrying why it is not a dial.

**Acceptance criteria:**
- [ ] `gk-core/data/tuning/story-scene-ui.v1.json` exists with exactly `beatTransitionMs`, `lineRevealPerCharMs`,
      `autoAdvanceMs`, `maxBeatsPerScene`.
- [ ] `autoAdvanceMs` is `null`; no auto-advance ships enabled.
- [ ] `storySceneTokens.ts` exists, is `as const`, and **every** entry has a why-not-tunable comment.
- [ ] Type scale is **not** in either file (it is pack `css`).
- [ ] No test asserts the shipped script's beat count as a literal.

**Verification:**
- [ ] `npm test -- --run storySceneTokens`
- [ ] `npm run build`

**Dependencies:** None · **Risk:** Low

**Files likely touched:**
- `gk-core/data/tuning/story-scene-ui.v1.json`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/storySceneTokens.ts`

---

### Task 3: `DialogShell` `size` contract with the GG-61 exemption

**Spec:** `spec-shell-scene-size.md` · **Size:** M (1 file + test)

**Description:** Add `size?: "default" | "scene"` to `DialogShell`. `default` keeps today's bounded card
byte-identically; `scene` is full-bleed (`100dvh`, `overflow: hidden`), with the scoped GG-61 exemption
written into the prop's own comment.

**Acceptance criteria:**
- [ ] `size` omitted ⇒ every existing caller renders **identically**.
- [ ] `size="scene"` fills the viewport using `100dvh` (not `100vh`) and **never scrolls**.
- [ ] The scene body has `overflow: hidden`; no scroll container is introduced.
- [ ] The exemption text names GG-61 and explains why a scene is not a dense entity.
- [ ] Band 3 ownership unchanged (`band-dialog`, `band: "dialog"`); focus/Esc untouched.
- [ ] **No** edit to `game-gui-principles.md`; no new band token; no `z-index`.

**Verification:**
- [ ] `npm test -- --run shells` (existing callers unchanged)
- [ ] `npm test -- --run DialogShell` (new case: scene bound uses viewport units, no scroll)
- [ ] `npm test -- --run stageHost` (GG-11 still holds)
- [ ] `npx vitest run src/shell/bandGuard.test.ts`
- [ ] `npm run build`

**Dependencies:** T1 · **Risk:** **High** (shared shell + the highest-risk geometry decision)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/shell/DialogShell.tsx`
- `gk-web/web/fusion-rpg-web/src/shell/shells.test.tsx` (or the DialogShell test file)

---

### Task 4: Band compliance (this program's violations)

**Spec:** `spec-band-compliance.md` · **Size:** M (3 files)

**Description:** Remove the prologue's two `z-index: 1` declarations by making paint order explicit
(DOM order/grid), and add the one justified `bandGuard` allowlist entry for the scene's band-3 owner.
The rim animation must not end up painting over the art.

**Acceptance criteria:**
- [ ] `features/onboarding/rift.css` contains **no** `z-index` and **no** `z-*` class.
- [ ] `bandGuard.ts` has exactly **one** new allowlist entry, with a comment carrying the three
      justification points and citing `onboarding-gnome-teaser.md:37`.
- [ ] `npx vitest run src/shell/bandGuard.test.ts` → **0 failed for this program's paths**; any remaining
      failure is one of the four unrelated surfaces and is **named**.
- [ ] Art/rim paint order verified visually (CSS paint order is not jsdom-testable) — recorded.

**Verification:**
- [ ] `npx vitest run src/shell/bandGuard.test.ts`
- [ ] `npm test -- --run rift`
- [ ] `npm run build`

**Dependencies:** T1 (green baseline) · **Risk:** Medium

**Files likely touched:**
- `web/fusion-rpg-web/src/features/onboarding/rift.css`
- `gk-web/web/fusion-rpg-web/src/shell/bandGuard.ts`
- `gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx` (if the mount path moves)

---

### Task 5: Piece contract, group registration seam, and CSS convention

**Spec:** `spec-piece-contract.md` · **Size:** S (3 files)

**Description:** Land the shared conventions every piece follows — most importantly that a **factory
must apply `themeStyle`/`vfxClass` itself** (`RecipeMount` applies paint only to factory-free pieces) —
plus the closed slot-name set, the group-registration module every piece appends to, and the CSS
location convention.

**Acceptance criteria:**
- [ ] The paint rule is stated and demonstrated by a test using a real factory.
- [ ] The shared slot names are fixed once (`actors`, `window`, `nameTag`, `progress`, `advance`).
- [ ] A factory-free piece still gets paint from `RecipeMount` (regression guard).
- [ ] A registered factory that applies the helpers receives pack custom properties on its root.
- [ ] Direct-child slot emission is asserted where draft CSS uses `>`.
- [ ] **`ui/gui-lego/pieces/storyScene.ts` exists** exporting `storySceneFactories` +
      `STORY_SCENE_SLOT_MAP` (empty at first), and `registerStoryScene.ts` calls it — so every piece
      task appends one entry and nothing is left unregistered (gap G1).
- [ ] **CSS convention fixed:** a piece with draft-scoped styling gets
      `gk-web/web/fusion-rpg-web/src/ui/story-scene/<piece>.css` scoped under its root class, mirroring
      `ui/gui-lego/conditionConsole.css:1-2` (gap G2).
- [ ] Registration is idempotent and re-binds on HMR (mirrors `pieces/register.ts:29-51`).

**Verification:**
- [ ] `npm test -- --run gui-lego`
- [ ] `npm test -- --run RecipeMount`
- [ ] `npm run build`

**Dependencies:** T1 · **Risk:** Medium (this rule silently governs every piece)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/storyScene.ts` (new group module)
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/RecipeMount.test.tsx`
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/types.ts` (slot-name constants, if needed)

---

## Checkpoint A — after T1–T5

- [ ] `npx vitest run src/i18n/` → 0 failed
- [ ] `npx vitest run src/shell/bandGuard.test.ts` → 0 failed for this program's paths
- [ ] `npm test -- --run shells` green (existing callers unchanged)
- [ ] A `size="scene"` shell renders full-bleed with no scroll container
- [ ] Both number homes exist; no balance number in a `const`
- [ ] **Owner reviews the full-bleed look in the shell before Phase 1**

---

## Phase 1 — Contracts

### Task 6: Scene script contract + the four Rift beats

**Spec:** `spec-scene-script.md` · **Size:** M

**Description:** Typed TS module holding `SceneScript`/`SceneBeat` and the four Rift beats migrated
**verbatim**; beat 3 becomes narration (no `speakerId`); `seal` is dropped as dead data.

**Acceptance criteria:**
- [ ] `SceneBeat` has `speakerId?: ActorId` (optional = narration), no `seal`.
- [ ] Beat copy is **byte-identical** to today's `BEATS` const / the narrative source.
- [ ] Beat 3 has **no** `speakerId`; `"Gnome signal"` appears nowhere as a speaker.
- [ ] A zero-beat script fails at module load (the fold never sees an empty scene).
- [ ] `maxBeatsPerScene` is read from `story-scene-ui.v1.json`, never a literal.
- [ ] No `sceneId`/`cueId` is rendered as player text.

**Verification:**
- [ ] `npm test -- --run sceneScript`
- [ ] `npm test -- --run RiftPrologueDialog` (copy parity)
- [ ] `npm run build`

**Dependencies:** T2 · **Risk:** Low

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts`
- `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.test.ts`

---

### Task 7: Actor cast

**Spec:** `spec-actor-cast.md` · **Size:** S

**Description:** Closed `ActorId` (`penny`, `dave`) with `displayName`, `initial`, named `variants[]`, and
an `actor` theme ref — **no** plant/zombie side axis, and a `null` sprite URL as the missing-art signal.

**Acceptance criteria:**
- [ ] `ActorId` is exactly `penny` and `dave` in v1; Zomboss appears nowhere.
- [ ] No actor is tinted by a plant/zombie side axis.
- [ ] A missing actor/variant resolves to `null` (never a 404 string).
- [ ] Penny and Dave are distinguishable **per actor** (name + initial) in the fallback path.
- [ ] Adding a third actor needs no change to `ActorDefinition`'s shape.
- [ ] `displayName` values are fiction-only.

**Verification:**
- [ ] `npm test -- --run actorCast`
- [ ] `npm test -- --run riftAssets`
- [ ] `npm run build`

**Dependencies:** T6 · **Risk:** Low

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts`
- `gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.test.ts`

---

### Task 8: Minimal scene trigger

**Spec:** `spec-scene-trigger.md` · **Size:** S

**Description:** A pure `isSceneEligible(spec, ledger, ctx)` that **narrows** the server's `eligible`
flag, requires `noLayerOpen`, and pins the version. `SanctumStage` reads it instead of an inline
expression, with no observable behaviour change.

**Acceptance criteria:**
- [ ] A server-**ineligible** row returns false even when `when` returns true.
- [ ] `noLayerOpen: false` returns false regardless of eligibility.
- [ ] A version mismatch does not match; a missing row returns false.
- [ ] `SanctumStage` behaviour is unchanged (existing tests pass).
- [ ] No copy, ordering, or scheduling logic exists here; the FE never writes eligibility.
- [ ] No `stage === …` branch added.

**Verification:**
- [ ] `npm test -- --run sceneTrigger`
- [ ] `npm test -- --run SanctumStage`
- [ ] `npx vitest run src/shell/noStageSpecificBranch.test.ts`
- [ ] `npm run build`

**Dependencies:** T6 · **Risk:** Low

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts`
- `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.test.ts`
- `gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx`

---

### Task 9: Localization scheme + pseudo harness

**Spec:** `spec-localization.md` · **Size:** M

**Description:** Land the message-id resolution scheme (script keeps authored English; the fold resolves
through `scene.<sceneId>.beat<n>.line`), and the pseudo-locale harness that proves no English leaks.

**Acceptance criteria:**
- [ ] Every beat, actor, and control label has a resolvable message id; a **missing id fails a test**.
- [ ] The four Rift lines remain byte-identical to the narrative source.
- [ ] Every localized component uses `msg` + `useLingui()` — no bare `t`.
- [ ] The pseudo-locale harness lands here (the pieces assert it in Phase 3).
- [ ] `npm run extract` output is committed if it changes.

**Verification:**
- [ ] `npm test -- --run messages` (the module's tests live in `messages.test.ts`; an earlier `--run localization` filter matched no file)
- [ ] `npx vitest run src/i18n/`
- [ ] `npm run extract`
- [ ] `npm run build`

**Dependencies:** T6 · **Risk:** Medium (extraction churn)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts` (or equivalent)
- `gk-web/web/fusion-rpg-web/src/features/story-scene/messages.test.ts`
- `gk-web/web/fusion-rpg-web/src/i18n/locales/en/**` (extracted output, if changed)

---

## Checkpoint B — after T6–T9

- [ ] Four Rift beats exist as data with copy parity to `docs/ideas/onboarding-gnome-teaser.md`
- [ ] Beat 3 is narration; `"Gnome signal"` and `seal` are gone
- [ ] Penny and Dave resolve with distinguishable fallbacks
- [ ] `SanctumStage` reads `isSceneEligible`; observable behaviour unchanged
- [ ] Every beat/actor/message id resolves; a missing one fails a test

---

## Phase 2 — Theme

### Task 10: Widen `ThemeKind` (mechanism only)

**Spec:** `spec-theme-packs-scene.md` · **Size:** S (2 files)

**Description:** Add `actor` and `scene` to the closed `ThemeKind` union with a stated reason, so packs
of those kinds can be registered. **No packs in this task** — split so neither exceeds the file cap.

**Acceptance criteria:**
- [ ] `ThemeKind` includes `"actor"` and `"scene"`, each with a comment stating why the union widened
      (a person is not a faction; a scene mood is not a person).
- [ ] The existing `neutral` fallback still resolves for an unknown ref.
- [ ] No pack data added yet; existing packs and tests unaffected.
- [ ] `npm run build` clean (a union widen surfaces every exhaustive switch).

**Verification:**
- [ ] `npm test -- --run themeRegistry`
- [ ] `npm test -- --run theme-bind`
- [ ] `npm run build`

**Dependencies:** T6, T7 · **Risk:** Medium (closed-union change)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/types.ts`
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/themeRegistry.ts`

---

### Task 11: The four scene/actor packs

**Spec:** `spec-theme-packs-scene.md` · **Size:** M (4 files)

**Description:** `actor.penny`, `actor.dave`, `scene.rift-portal`, `scene.quarantine` on **both** the
design and FE sides, registered via the mechanism T10 landed.

**Gate carry-over from T10 — `"scene"` must become load-bearing.** T10's gate proved the `"actor"`
arm is compiler-enforced (reverting it fails `tsc`, because `actorCast.ts` types its ref as
`ThemeRef & { kind: "actor" }`), but found that reverting the `"scene"` arm still passes `tsc`: no
production code writes `kind: "scene"` yet, and the pack JSON is cast `as ThemePack`, so it enforces
nothing. **T11 must give the scene arm a consumer**: type the cue→scene-mood join (the spec says scene
mood is per-beat, derived from `scene-script`'s `cueId` — `spec-theme-packs-scene.md:104`) so a
`ThemeRef & { kind: "scene" }` flows through production code, and prove it the same way T10 did
(revert the arm, `tsc` must fail). If that join belongs in T18's `cue-seam` instead, say so here and
carry the criterion there — but do not leave the arm decorative.

**Acceptance criteria:**
- [ ] Four packs exist in `docs/design/gui-lego/themes/packs/` **and** `features/gui-lego/themes/`.
- [ ] All four are registered, verified via **`listThemePacks()`** — never a hard-coded count.
- [ ] `actor.penny` and `actor.dave` resolve to **different** accent paint.
- [ ] Each scene pack carries its `vfx.select` id for `cue-seam`.
- [ ] Unknown ref still falls back to `neutral`.
- [ ] No piece contains an actor/scene hex.
- [ ] **The `"scene"` arm is load-bearing:** a `ThemeRef & { kind: "scene" }` flows through
      production code, and reverting the arm makes `tsc` fail (proved, not asserted).

**Verification:**
- [ ] `npm test -- --run themeRegistry`
- [ ] `npm run build`
- [ ] `npm run check:bundle`

**Dependencies:** T10 · **Risk:** Low (design/FE sync)

**Files likely touched:**
- `docs/design/gui-lego/themes/packs/actor-penny.json` (+ `actor-dave`, `scene-rift-portal`, `scene-quarantine`)
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/themes/*.json` (4 copies)
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/themeRegistry.ts` (imports)

---

## Checkpoint C — after T10–T11

- [ ] `ThemeKind` widened with a stated reason; no exhaustive-switch regression
- [ ] `listThemePacks()` includes all four new packs (derived assertion)
- [ ] Penny and Dave resolve to different accent paint
- [ ] Unknown ref falls back to `neutral`

---

## Phase 3 — Leaf pieces (safe to parallelize after T5 + T11)

### Task 12: `actor-sprite` — the honest labelled shape

**Spec:** `spec-actor-sprite.md` · **Size:** M · **Draft:** `docs/design/gui-lego/pieces/story-actor-sprite.html`

**Description:** The sprite plus the **name-labelled** fallback when art or variant is missing — the
concrete deliverable of owner decision 2. Extends `ActorFrame`'s visual language; invents no fourth
stand-in.

**Acceptance criteria:**
- [ ] Draft HTML exists showing both states side by side.
- [ ] `spriteUrl: null` ⇒ Penny's and Dave's placeholders are **visually distinguishable** (name,
      initial, pack accent) — asserted in a test.
- [ ] No `<img>` renders when the URL is null; no empty `src` reaches the DOM.
- [ ] A runtime load failure degrades to the same placeholder.
- [ ] The name appears in the **visible** text and the accessible name.
- [ ] Pack accent only; zero actor hex; **no** `side` tint.
- [ ] `phase` is `empty` (not `error`) for not-yet-authored art.
- [ ] The factory is registered in `ui/gui-lego/pieces/storyScene.ts` (`storySceneFactories` + `STORY_SCENE_SLOT_MAP`).
- [ ] Styling lives in `ui/story-scene/actorSprite.css`, scoped under the piece root (G2).

**Verification:**
- [ ] `Test-Path docs/design/gui-lego/pieces/story-actor-sprite.html`
- [ ] `npm test -- --run actorSprite`
- [ ] `npm run build`

**Dependencies:** T5, T7, T11 · **Risk:** Medium

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-actor-sprite.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorSprite.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorSprite.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorSprite.css`

---

### Task 13: `name-tag`

**Spec:** `spec-name-tag.md` · **Size:** S · **Draft:** `docs/design/gui-lego/pieces/story-name-tag.html`

**Acceptance criteria:**
- [ ] Draft HTML shows Penny's and Dave's tags with **different** pack paint.
- [ ] A narration beat renders **no** name-tag DOM node (absence test).
- [ ] Zero hard-coded identity color (`text-ok` et al.); paint from `themeResolved`.
- [ ] An empty `displayName` renders nothing.
- [ ] Contrast per v1 pack checked and recorded.
- [ ] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`.
- [ ] Styling lives in `ui/story-scene/nameTag.css`, scoped under the piece root.

**Verification:** `Test-Path` draft · `npm test -- --run nameTag` · `npm run build`

**Dependencies:** T5, T11 · **Risk:** Low

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-name-tag.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/nameTag.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/nameTag.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/nameTag.css`

---

### Task 14: `advance-control`

**Spec:** `spec-advance-control.md` · **Size:** S · **Draft:** `docs/design/gui-lego/pieces/story-advance-control.html`

**Acceptance criteria:**
- [ ] Draft HTML shows normal, last-beat, pending, and error states.
- [ ] Skip renders on **every** beat, including `isLastBeat === true`.
- [ ] `pending` disables both verbs and shows the in-flight label.
- [ ] The error variant preserves a path onward without a successful acknowledgement.
- [ ] Both verbs call the same terminal action (single-handler test).
- [ ] No keybinding registered by the piece; labels come from the payload.
- [ ] Touch targets meet the kit minimum at the narrow breakpoint.
- [ ] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`.
- [ ] Styling lives in `ui/story-scene/advanceControl.css`, scoped under the piece root.

**Verification:** `Test-Path` draft · `npm test -- --run advanceControl` · `npm run build`

**Dependencies:** T5 · **Risk:** Low

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-advance-control.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/advanceControl.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/advanceControl.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/advanceControl.css`

---

### Task 15: `scene-progress`

**Spec:** `spec-scene-progress.md` · **Size:** S · **Draft:** `docs/design/gui-lego/pieces/story-scene-progress.html`

**Acceptance criteria:**
- [ ] Draft HTML shows 4-beat, 1-beat, and 0-beat cases.
- [ ] `total <= 1` renders **no** DOM node (the rule that lets a reveal reuse this).
- [ ] `label` is rendered verbatim; the piece assembles no string.
- [ ] Pips are decorative; the label carries semantics.
- [ ] No literal beat count in the piece or its test (derived from a fixture script).
- [ ] Nothing is persisted.
- [ ] The current pip is distinguishable **without** color alone.
- [ ] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`.
- [ ] Styling lives in `ui/story-scene/sceneProgress.css`, scoped under the piece root.

**Verification:** `Test-Path` draft · `npm test -- --run sceneProgress` · `npm run build`

**Dependencies:** T5 · **Risk:** Low

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-scene-progress.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneProgress.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneProgress.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneProgress.css`

---

### Task 16: `dialogue-window`

**Spec:** `spec-dialogue-window.md` · **Size:** M · **Draft:** `docs/design/gui-lego/pieces/story-dialogue-window.html`

**Acceptance criteria:**
- [ ] Draft HTML shows spoken, narration, teaching-present, teaching-absent.
- [ ] A narration beat renders the window with **no** `name-tag` node.
- [ ] `aria-live="polite"` is scoped to the **line region**, not the whole window.
- [ ] The teaching line renders only when present and is visually subordinate per pack tokens.
- [ ] A long line **wraps without truncation** at the narrow breakpoint.
- [ ] No color/hex in the piece; type scale from pack `css`.
- [ ] The payload cannot express a paragraph array (a text wall is unrepresentable).
- [ ] Hosts the `nameTag` slot (parent-relative bind — asserted in T20).
- [ ] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`.
- [ ] Styling lives in `ui/story-scene/dialogueWindow.css`, scoped under the piece root.

**Verification:** `Test-Path` draft · `npm test -- --run dialogueWindow` · `npm run build`

**Dependencies:** T5, T13 · **Risk:** Medium

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-dialogue-window.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/dialogueWindow.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/dialogueWindow.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/dialogueWindow.css`

---

## Checkpoint D — after T12–T16

- [ ] Every piece has a draft HTML that exists
- [ ] Every factory applies `themeStyle`/`vfxClass` to its landmark root (asserted)
- [ ] `actor-sprite` with a null URL renders the name-labelled shape, distinct per actor
- [ ] A narration beat renders **no** name-tag node
- [ ] Skip renders on every beat including the last
- [ ] No piece hard-codes a player string or an identity color
- [ ] Pseudo locale renders no English from the window, name tag, progress, or controls

---

## Phase 4 — Composite pieces

### Task 17: `actor-portrait`

**Spec:** `spec-actor-portrait.md` · **Size:** S · **Draft:** `docs/design/gui-lego/pieces/story-actor-portrait.html`

**Acceptance criteria:**
- [x] Draft HTML shows two actors side by side, one speaking.
- [x] `speaking` is distinguishable **without** color alone.
- [x] The inactive actor stays visible and identifiable.
- [x] A variant change on speaker change does **not** reset the other actor's variant.
- [x] The actor is not a focus target.
- [x] `spriteUrl: null` still renders the labelled fallback through `actor-sprite`.
- [x] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`.
- [x] Styling lives in `ui/story-scene/actorPortrait.css`, scoped under the piece root.

**Verification:** `Test-Path` draft · `npm test -- --run actorPortrait` · `npm run build`

**Dependencies:** T5, T12 · **Risk:** Low

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-actor-portrait.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorPortrait.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorPortrait.test.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/actorPortrait.css`

---

### Task 18: `cue-seam`

**Spec:** `spec-cue-seam.md` · **Size:** S

**Acceptance criteria:**
- [x] `StoryCueId` is a closed union; the four Rift ids are the only members in v1.
- [x] A cue-id typo is a **compile error** (typed in `SceneBeat.cueId`).
- [x] `cueId → vfx class` resolves through the **scene pack**, not piece code.
- [x] Under `prefers-reduced-motion`, the cue renders as an instant state change.
- [x] `onCue` remains **optional**; the scene works with no host consumer.
- [x] **No** socket, keybinding, or transport introduced.
- [x] `gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs` and `scripts/prove-vfx.ps1` are **untouched**.

**Verification:** `npm test -- --run storyCue` · `npm run build`

**Dependencies:** T6, T11 · **Risk:** Low

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.ts`
- `gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.test.ts`

---

### Task 19: `scene-stage`

**Spec:** `spec-scene-stage.md` · **Size:** M · **Draft:** `docs/design/gui-lego/pieces/story-scene-stage.html`

**Description:** The compose root: full-bleed bed, band-utility stacking, `data-cue`, the two-actor
layout with the stack rule, and reduced-motion for transitions. **Also the task that proves the
full-bleed no-scroll constraint is survivable.**

**Acceptance criteria:**
- [x] Draft HTML shows two actors at desktop + narrow widths, and a narration beat.
- [x] **Zero** `z-index`/`z-*` in the piece and its CSS.
- [x] Two actors side by side ≥720px; **stack speaker-forward** <720px; neither hidden.
- [x] At `100dvh` on a short viewport, the **advance control and window are reachable without
      scrolling**; the art bed scales down first.
- [x] `prefers-reduced-motion` makes the beat transition and sprite swap instant.
- [x] **`beatTransitionMs` from `story-scene-ui.v1.json` is the actual transition duration** — read by
      the piece, never a literal (gap G3).
- [x] **The Enter/Space advance contract is owned here** (gap G4): the stage is the key handler, actors
      are not focus targets, and the advance fires only when the stage surface itself has focus —
      preserving `RiftPrologueDialog.tsx:159-164`'s behaviour through the migration. No global
      keybinding; F10 stays forbidden (`keymap.ts:18`).
- [x] The **dialogue window is the focus target** when the scene opens (the focus contract the a11y
      section promises but no other piece asserts).
- [x] `data-cue` reflects `cueId`; no engine vocabulary rendered as text.
- [x] The art bed is `aria-hidden` when a line is present.
- [x] Direct slot children (no intervening wrapper under `>` CSS).
- [x] Mounts over the stage without unmounting it (GG-11).
- [x] The factory is registered in `ui/gui-lego/pieces/storyScene.ts`; styling in
      `ui/story-scene/sceneStage.css` scoped under the root.

**Verification:** `Test-Path` draft · `npm test -- --run sceneStage` ·
`npx vitest run src/shell/bandGuard.test.ts` · `npm test -- --run stageHost` · `npm run build`

**Dependencies:** T3, T4, T14, T15, T16, T17, T18 · **Risk:** **High** (full-bleed + stack + no-scroll)

**Files likely touched:**
- `docs/design/gui-lego/pieces/story-scene-stage.html`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneStage.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneStage.css`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/sceneStage.test.tsx`

---

## Checkpoint E — after T17–T19

All six re-proven on the current HEAD (2026-09-23) in the T23 gate run, so they are evidence, not
carry-over. Command:
`npx playwright test e2e/story-scene-visual.spec.ts --project=chromium` → **6 passed (1.5m)**, 20 PNGs
+ 5 capture reports under `e2e/artifacts/story-scene/` (gitignored, reproducible).

- [x] **Two actors render side by side ≥720px and stack speaker-forward <720px; neither hidden.**
  Side by side at `gate-720` (`1280×720`): Penny left in the inactive ring, Dave right in the accent
  ring. Stacked at `mobile` (`390×844`): Penny above/inactive, **Dave below and forward** (larger,
  accent ring, speaking). Both visible in the capture, neither hidden.
- [x] **Full-bleed at `100dvh`: window + advance control reachable without scrolling.** Asserted as
  geometry, not eyeballed — the gate now measures the dialog box **and** `.story-advance-control`
  against the viewport height at all five viewports, because a full-bleed dialog that overflowed
  would still screenshot at viewport size. `bodyOverflows=false` on all 20 captures incl. `1280×600`.
- [x] **Art bed scales down before the window or the control.** Construction proof:
  `sceneStage.css:62` gives the bed `flex: 1 1 auto; min-height: 0` while the window/advance are
  `flex: none` (`:67-75`, with the comment naming the S1 risk). The `gate-short`/`mobile` captures
  show the bed yielding while the window and both buttons stay whole.
- [x] **`prefers-reduced-motion` makes transitions instant.** `emulateMedia({ reducedMotion: "reduce" })`
  run asserts `data-motion="instant"` on the stage root.
- [x] **Zero `z-index`/`z-*` in the stage and its CSS.** `bandGuard` green (see the last box); the
  paint-order fix is document order plus `position: relative` and says why in `sceneStage.css`.
- [x] **`bandGuard.test.ts` and `noStageSpecificBranch.test.ts` green.** 8 files / 84 tests green
  (`npx vitest run` over `src/shell/bandGuard.test.ts src/shell/noStageSpecificBranch.test.ts
  src/i18n src/shell/keymapGuard.test.ts`) → `Test Files 8 passed (8) · Tests 84 passed (84)`.

---

## Phase 5 — Fold, surface, host, cutover

### Task 20: `story-scene-fold`

**Spec:** `spec-story-scene-fold.md` · **Size:** M

**Description:** The pure VM — VM-as-bind-root, derive speaking state, own the omit rules, format labels,
and emit a single `terminal` intent. Includes the **G5 regression guard**: `nameTag` lives on the
**window payload**, because nested slots bind parent-relative.

**Acceptance criteria:**
- [x] The VM matches the spec; **no** `root`/`payloads` map introduced.
- [x] **A spoken beat emits `window.nameTag`**; a narration beat omits it. (The G5 regression test.)
- [x] A one-beat script emits **no** `progress`.
- [x] `speaking` is true only for the beat's speaker; a narration beat has none.
- [x] A variant set on beat 1 survives to beat 3 unchanged.
- [x] `terminal` covers advance and skip through one shape; skip reachable on every beat.
- [x] `beats.length` read from the input script; no literal.
- [x] `revision` stamped on every payload **and** no new `vocabularyGuard` violation.
- [x] Fold is pure (deep-equal on repeat); no fetch/`Date.now()`/random.
- [x] Missing art yields `phase: "empty"`, not `"error"`.

**Verification:**
- [ ] `npm test -- --run foldStorySceneVm`
- [ ] `npm test -- --run bindSurface`
- [ ] `npx vitest run src/i18n/vocabularyGuard.test.ts`
- [ ] `npm run build`

**Dependencies:** T6, T7, T18 · **Risk:** **High** (G5 is silent if wrong)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/story-scene/foldStorySceneVm.ts`
- `gk-web/web/fusion-rpg-web/src/features/story-scene/foldStorySceneVm.test.ts`

---

### Task 21: `recipe-wire` — recipe, registration, bus

**Spec:** `spec-recipe-wire.md` · **Size:** M

**Description:** The `story-scene` recipe (both sides), the idempotent registration, and the closed
four-event bus. **No lifecycle overlays** — the shared `phase-*` pieces render engine text.

**Acceptance criteria:**
- [x] `story-scene.json` exists in the design SSOT **and** the runtime recipe folder.
- [x] Root binds `vm`; **every** slot child declares a `bind` (asserted — an unbound child receives the
      whole parent payload).
- [x] `actors` uses parent-relative `$bindArray`.
- [x] Conditional slots omit via `undefined`, not an empty piece.
- [x] **No** `lifecycleOverlays` key; the four real state owners are documented.
- [x] `ensureStorySceneRegistered()` is idempotent and mirrors the existing register pattern.
- [x] The bus is exactly the four declared events; no piece fetches.

**Verification:**
- [ ] `npm test -- --run story-scene` · `npm test -- --run RecipeMount`
- [ ] `npm run build` · `npm run check:bundle`

**Dependencies:** T5, T19, T20 · **Risk:** Medium

**Files likely touched:**
- `docs/design/gui-lego/recipes/story-scene.json`
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/story-scene.json`
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/registerStoryScene.ts`
- `gk-web/web/fusion-rpg-web/src/features/gui-lego/storySceneBus.ts`

---

### Task 22: `story-scene-host`

**Spec:** `spec-story-scene-host.md` · **Size:** M

**Description:** The reusable host owning beat index, advance guard, ack mutation, error recovery, cue
emission, and the fold→mount wiring. Scene 2 then needs no copied wiring.

**Acceptance criteria:**
- [ ] `StorySceneHost` renders **no** scene markup of its own.
- [ ] A double-click on the primary button yields exactly **one** transition.
- [ ] Advance-on-last and skip both call the same terminal path.
- [ ] An acknowledgement failure shows retry + destination; the destination works without a successful ack.
- [ ] Beat index resets to 0 when `open` flips true.
- [ ] **A second synthetic script renders through the same host with no host edit** (the reuse proof).
- [ ] No `stage === …` branch.

**Verification:**
- [ ] `npm test -- --run StorySceneHost`
- [ ] `npx vitest run src/shell/noStageSpecificBranch.test.ts`
- [ ] `npm run build`

**Dependencies:** T20, T21 · **Risk:** Medium

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx`
- `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.test.tsx`

---

### Task 23: Prologue cutover + agent-performed visual gate

**Spec:** `spec-recipe-wire.md` §"Owner visual gate" · **Size:** M

> **AMENDED 2026-09-15 (owner): the visual gate is now AGENT-performed, not owner-performed.**
> The owner explicitly reassigned the reviewer (`html-design-implementation` §"mandatory unless the
> owner disables it", `SKILL.md:127`). **The check is not removed — only who runs it changes.** I run
> the browser capture and the visual review myself in Playwright; I still write the evidence, the gap
> report (`SKILL.md:118`, `:302-307`), and surgical fixes. T23 must **not** be marked done on jsdom
> tests alone, and it must **not** be deferred waiting for the owner.
>
> **The mechanism is also amended — the spec's premise is out of date.** `spec-recipe-wire.md`'s gate
> section declares a live-SPA capture impossible ("no force-open path"; falls back to draft HTML).
> That is no longer true: `gk-web/web/fusion-rpg-web/e2e/story-ui-evidence.spec.ts` (a sibling session, now
> on this base) drives the **real shipped SPA** through all four beats at three viewports by mocking
> `**/api/onboarding/**` so `stories[0].eligible = true`, which is the one field `SanctumStage`'s gate
> reads. That is strictly stronger than a draft-HTML page because it captures the assembled surface.
>
> **Revised gate:**
> 1. **Before** — re-run the sibling spec to regenerate `e2e/artifacts/story-ui/` (it was empty when
>    T13 landed: `e2e/artifacts/` is gitignored, so it is reproducible evidence, not committed).
>    Capture the shipped prologue at all four beats × viewports `1440×900`, `768×1024`, `390×844`.
> 2. **After** — capture the cutover surface with the same beats, viewports and assertions, into
>    `e2e/artifacts/story-scene/`, so before/after are directly comparable. **Prefer adding my own
>    T23 spec** over editing the sibling's file (its fence is `story-ui-evidence-20260915-d5f2`); if I
>    must extend it, keep its existing assertions and report the crossing.
> 3. **Review the images myself**, comparing against the draft HTML and the before set, prioritising
>    **structure > geometry > density > typography > surfaces > decoration**, then **surgical fixes
>    only** (never "rewrite the world for one low element"). Record the gap report and each fix in
>    this row, plus the exact command that regenerates both artifact sets.
> 4. If a defect needs a product decision, that is a genuine stop — record it and continue with T24.
>
> **What the review must verify:** no scrollbar at 1280×720 **and** at a short viewport (`100dvh` fit —
> exactly what jsdom cannot test); two actors side by side ≥720px and stacked speaker-forward <720px
> with **neither hidden**; the art bed scaling **before** the window or the advance control;
> `prefers-reduced-motion` making transitions instant; **zero** `z-index`/`z-*` in the stage and its
> CSS; a narration beat rendering **no** name tag; a missing sprite labelled and distinct per actor;
> and Skip present on every beat including the last.
>
> **Test-id disposition:** the shipped dialog carries `data-testid="rift-prologue-say|speaker|line|teaching"`.
> The replacement must **keep or consciously supersede** them — if T23 makes them redundant, say so
> here rather than leaving a stale half-state.
>
> **A measured pre-existing fit defect to fix here (peer evidence, 2026-09-15).** The sibling
> evidence spec was hardened to capture the two viewports T23 names, and the **shipped** prologue
> fails one:
>
> | Viewport | Body content | Body visible | Result |
> |---|---|---|---|
> | 1280×720 | 469 px | 469 px | fits, **zero margin** |
> | 1280×600 | 469 px | 379 px | **clipped — 90 px hidden** (`gate-short-beat4.png`) |
>
> So the failure begins just under 720px of viewport height — an ordinary laptop once browser chrome
> is subtracted. **This is exactly T23's "no scrollbar at 1280×720 *and* at a short viewport" and
> checkpoint E's `100dvh` reachability criterion.** T23 must make the scene body fit at a short
> viewport — scaling the art bed down **before** the window or the control, per checkpoint E's
> ordering — not let the window push content out of the body.
>
> **The false-pass trap — do not inherit it.** `DialogShell` makes its body `overflow-y-auto` inside
> `max-h-[min(720px,82vh)]` (`DialogShell.tsx:70,82`), so **the document never scrolls even when the
> scene is clipped**. Measuring `document.documentElement.scrollHeight` reports a **false pass on a
> visibly broken screen**. Measure the **dialog body**, never the document:
>
> ```ts
> const body = dialog.getByTestId("rift-prologue-dialog-body"); // DialogShell.tsx:83
> const fit = await body.evaluate((el) => ({ scrollHeight: el.scrollHeight, clientHeight: el.clientHeight }));
> const bodyOverflows = fit.scrollHeight > fit.clientHeight;
> ```
>
> The peer left this as a `known-defect` **annotation** so its own spec stays green while the defect is
> unfixed. **Once the scene fits, replace that annotation with `expect(bodyOverflows).toBe(false)` for
> both gate viewports** — that assertion going red→green is the proof the fix landed, and it stops the
> defect returning silently.

**Acceptance criteria:**
- [ ] `RiftPrologueDialog` is a thin wrapper; **no** inline scene markup; `BEATS` gone from the component.
- [ ] The six local state concerns are gone (index, ack, continue remain in the host).
- [ ] `RiftPrologueDialog.test.tsx` passes **unchanged**.
- [ ] The ack call is exactly `{ storyId: "rift-prologue", version: 1, outcome }`.
- [ ] Skip present on every beat; one terminal path; failure bypasses to the lawn.
- [ ] Before/after artifacts exist under `e2e/artifacts/`, are **directly comparable**, the command
      that regenerates them is recorded, and **the agent review has been performed with its gap report
      written** (not deferred to the owner).
- [ ] The `rift-prologue-*` test ids are kept or their supersession is stated here.
- [ ] `riftAssets.ts` / `RIFT_ASSETS` / `RiftPrologueCueId` disposition is decided and applied:
      either retired (unused after cutover) or repointed at the actor-cast resolver — **no dead
      module left behind** (gap G6).
- [ ] `OnboardingReveal` is **not** edited (decision 4).
- [ ] `npm run check:bundle` passes; Phaser/recharts off the entry chunk. **Pre-existing red at base
      HEAD** (entry 276.8 KB gz vs a 180 KB budget; independently reproduced by T11's gate) and not
      this program's regression — so this line may not be satisfiable, but it must **not** be silently
      dropped from the criteria either. Judge at cutover whether T23 moved it; the standing note above
      governs how to treat it.

**Verification:**
- [ ] `npm test -- --run RiftPrologueDialog` · `npm test -- --run story-scene`
- [ ] `npx vitest run src/shell/bandGuard.test.ts` · `npx vitest run src/shell/noStageSpecificBranch.test.ts`
- [ ] `npm run test:e2e -- --grep story` (regenerates both artifact sets; record the exact command)
- [ ] `npm run build` · `npm run check:bundle` (see the standing note on its pre-existing failure)
- [ ] **Agent visual review performed; gap report + fixes in this row**

**Dependencies:** T22 · **Risk:** **High** (live player surface)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx`
- `web/fusion-rpg-web/src/features/onboarding/riftAssets.ts` (retire or repoint — G6)
- `gk-web/web/fusion-rpg-web/e2e/story-scene-visual.spec.ts` (the gate)
- `gk-web/web/fusion-rpg-web/playwright.config.ts` (only if a `story-scene` project or dev route is added)

**Cutover progress, 2026-09-16 (code done, gate open).** The wrapper is thin (no markup, no `BEATS`,
six state concerns gone); ack/skip/retry/bypass/cues verified identical. Evidence: `RiftPrologueDialog`
4/4, `StorySceneHost` 8/8, `SanctumStage` 21/21 (caller), full story-scene set 214/214, `tsc` clean,
`npm run build` green. G6 **retired**: `riftAssets.ts` + `riftAssets.test.ts` + `rift.css` +
`storyContract.ts` deleted (zero importers anywhere; art source PNGs kept — the cast carries URLs
when art ships). GG-53 allowlist **re-pointed** `features/onboarding/RiftPrologueDialog.tsx` →
`ui/story-scene/StorySceneHost.tsx` per the guard's own note (bandGuard 3→2 failing tests; the two
remaining are pre-existing in HEAD-clean files owned elsewhere: `conditionConsole.css`,
`shieldConsole.css`, `PhaserSceneSwitchPocPage.tsx`, `mapChromeMute.ts`).
- **"Passes unchanged" verdict:** the walk + skip tests pass **literally unchanged** (progress
  `aria-label` restored on the piece — the piece's own docstring already promised it). The two rim
  tests could not: they pin the retired dialog's `.rift-prologue-rim` spans. Their contract
  (decoration under art via DOM order, no tier; decoration out of the AT tree) now lives in the
  stage piece and is proven at both layers — piece tests added (`sceneStage.test.tsx` art-bed
  semantics) and the onboarding tests re-expressed in piece vocabulary at the assembled surface.
  This checkbox stays unticked with the reason stated, per the design-gate honest-gap rule.
- **Test-id disposition (line 939: KEPT in part, SUPERSEDED in part).** Kept: `rift-prologue-dialog`
  (host `testId` prop, wrapper passes it — instance identity, needed by `SanctumStage` too) and the
  `Beat n of m` aria-label (AT contract). Superseded: `rift-prologue-say|speaker|line|teaching` and
  the `.rift-prologue-scene`/`.rift-prologue-placeholder` classes — the window/stage pieces carry
  stable module hooks instead (`.story-dialogue-window`, `__nameTag`, `__line` (aria-live),
  `__teaching`, `[data-narration]`; `.story-scene-stage[data-cue]`; missing sprites are labelled
  fallbacks, not a placeholder branch). No `src/` consumer references the old hooks (verified by
  grep); my own T23 after-spec will use the module hooks, keeping before/after structurally
  comparable.
- **Sibling crossing PERFORMED 2026-09-16 (owner explicitly approved: "fix it ... in this
  session too").** `e2e/story-ui-evidence.spec.ts` (fence `story-ui-evidence-20260915-d5f2`) migrated
  with every assertion kept: `.rift-prologue-scene` → `.story-scene-stage` (`data-cue` was already
  there); `.rift-prologue-placeholder` → `.story-actor-sprite__placeholder` (same `role="img"`
  shape); `rift-prologue-speaker|line|teaching` →
  `.story-dialogue-window__nameTag|__line|__teaching`; speaker read made conditional with
  `hasNameTag` null-guarded (beat-3 narration — rendering no name tag there is an explicit gate
  item, not a missing hook); stale BEATS-source comment re-pointed at the script. Untouched and
  still green: `rift-prologue-dialog`, `[aria-label="Beat n of 4"]`, `Next` clicks. Result: sibling
  spec **3/3 green on the cutover tree**, desktop report showing beat-3 `None`/no-tag honestly.
  Note: this run overwrote the co-located `e2e/artifacts/story-ui/` before-set with after-captures
  (same dir by the spec's design) — the review already consumed it and the regenerate command is
  recorded below, so nothing irreproducible was lost. No `known-defect` annotation exists in the
  sibling spec to flip (it carries no fit assertion at any viewport) — the fit gate lives in the
  after-spec instead, green.
- **Visual gate PERFORMED 2026-09-16 (agent).** Before-set regenerated from a throwaway HEAD
  worktree (sibling spec unmodified, 3/3 green, then worktree removed): `e2e/artifacts/story-ui/`
  (12 PNGs + 3 reports, co-located for comparison; regenerate with
  `npx playwright test e2e/story-ui-evidence.spec.ts --project=chromium`).
  After-set: new `e2e/story-scene-visual.spec.ts` (MY file),
  6/6 green: 5 viewports × 4 beats + reduced-motion. Regenerate with
  `npx playwright test e2e/story-scene-visual.spec.ts --project=chromium`.
  Baseline confirmed first: shipped dialog fits 1280×720 with zero margin (469/469) and clips 90px
  at 1280×600 (469 vs 379) — the peer's numbers reproduced exactly, measured on the dialog BODY.
  After: `bodyOverflows=false` on all 20 captures — the short-viewport defect is fixed by the new
  stage's construction (bed yields first), a genuine red→green.
- **Gap report (structure > geometry > density > typography > surfaces > decoration).**
  (1) REAL DEFECT FOUND AND FIXED: the absolute mood backdrop painted ABOVE all static content
  (CSS step 6 vs 3-5 — positioned beats non-positioned regardless of DOM order), dimming the
  window/text/controls while transformed portraits stayed crisp. No unit test or guard can see
  paint order — this is exactly what the visual gate is for. Fix is band-clean: `position:
  relative` (z-auto, zero `z-index`) on the six content layers, with a do-not-simplify comment in
  `sceneStage.css`. (2) CHECKED, BY DESIGN: the rift PNG is gone — the draft (`story-scene-stage.html`)
  shows a pack-painted bed, not the PNG, and the ideal lists the prologue-scoped art/CSS as debt
  replaced; the narrative "full-screen illustration" is the mood bed + cast. G6 retire stands.
  (3) Spec artifact fixed: captures now settle 500ms past the 220ms cross-fade (tuning-sourced).
  Verified against the must-list: Skip on every beat incl. last (asserted), reduced-motion →
  `data-motion="instant"` (asserted), narration beat renders no name tag (asserted), both actors
  side-by-side ≥720px and stacked speaker-forward <720px with neither hidden (reviewed mobile),
  zero `z-index` (bandGuard + file pin).
- **Still open (owner needed):** a build-phase session record so `verify-change.ps1` can run
  (it correctly refuses the idea record's fence — requires `/session-start`, which asks the owner
  by design). Everything else on the T23 list is done: the sibling migration is landed green
  (above), the fit gate is proven in the after-spec, bundle is ruled stale.
- **Owner ruling 2026-09-16: `check:bundle` is a STALE RULE — ignored, not gated on.** (Matches the
  standing notes: tech-stack retracted the recharts/xyflow removal plan and forbids failing merely
  for presentation libs in package.json.) No bundle investigation, no absorption, no block.

---

## Checkpoint F — Program complete

Verified **2026-09-23**, lane `story-scene-1`, on the post-merge HEAD.

- [x] **Prologue renders from `recipe-wire` through `StorySceneHost`; no god TSX remains.**
  `RiftPrologueDialog.tsx` is 38 lines: props in, `<StorySceneHost>` out, no markup and no `BEATS`.
  Re-proven end-to-end in the browser (the gate drives the real SPA through all four beats).
- [ ] **`RiftPrologueDialog.test.tsx` passes unchanged** — **not as written, with the reason stated**
  (T23's own note, unchanged): the walk and skip tests pass literally unchanged, but two rim tests
  pinned the retired dialog's `.rift-prologue-rim` spans. Their contract moved to the `scene-stage`
  piece and is proven at both layers (piece test + the assembled surface's own assertions). The
  checkbox is not ticked because "unchanged" is false for that file, not because the contract is
  untested. **Erratum ruling still owed by the manager** — same request T23 recorded.
- [x] **Ack still `rift-prologue`/`1`; skip on every beat; failure bypasses to the lawn.**
  `StorySceneHost` acknowledges exactly one `{storyId, version, outcome}` per terminal (double-click
  and double-terminal guarded), skip is unconditional on every beat including the last, and an ack
  failure renders retry + destination and the destination works without the ack. `src/ui/story-scene`
  suite green. The gate re-asserts "Skip intro" on all four beats incl. the last.
- [x] **A second synthetic script renders through the same host with no host edit.**
  `StorySceneHost.test.tsx:120` — "a second synthetic script renders through the same host with no
  host edit" (`sceneId: "synthetic-check"`, one beat). Extended rather than broken by this lane's
  content-resolution fix: `sceneContentResolver` returns `{}` for a scene with no descriptor table
  (`messages.ts:211-231`), so an unknown scene still renders its authored strings.
- [x] **Pseudo locale renders no English from window / name tag / progress / controls.** **This box
  was failing, and the test for it did not exist.** New `src/ui/story-scene/StorySceneHost.pseudo.test.tsx`
  (2 tests) renders the assembled scene under `setLocale("pseudo")` and asserts, per beat, the
  line/teaching/name tag equal the catalog's own pseudo text, the progress label keeps its
  interpolation, and both verbs are catalog-resolved. It failed on first run for **three** of the
  four named families (window line, teaching, name tag), because the content path never read the
  catalog. Fixed in this lane: `StorySceneHost.tsx:117` now resolves content through
  `sceneContentResolver` (`messages.ts:211`) and the fold places it (`foldStorySceneVm.ts:76-91,168-170`).
  English rendering is provably unchanged — `messages.test.ts` binds every descriptor's text to the
  script's, and the five-viewport gate re-run is byte-for-byte the same English. That test then found
  **F9** — three more player strings no locale could reach (`actor-sprite`'s hint and accessible
  label, `advance-control`'s `"Working…"` title fallback) — fixed in the same lane; see F9's row.
  **Browser-level too (F11, 2026-09-23):** `e2e/story-scene-pseudo.spec.ts` under the opt-in
  `pseudo-chromium` project drives `vite dev`, switches the locale on the live instance the way
  System → Preferences does, and re-applies the T23 obligations in pseudo —
  `E2E_DEV_PORT=4402 npx playwright test e2e/story-scene-pseudo.spec.ts --project=pseudo-chromium`
  → **3 passed**, `pseudoMarked=true` and `bodyOverflows=false` on all 12 captures at 1280×720,
  1280×600 and 390×844. The switch also exposed a real defect (resolvers keyed on the `i18n`
  singleton, so a live locale change left the scene in the old language), fixed and pinned by
  `follows a locale switch made while the scene is open`.
- [x] **`npm run build` + `npm run check:bundle` pass.** `✓ built in 2m 21s` (tsc + vite, clean) and
  `check-bundle: Phaser is absent from the entry chunk (assets/index-DevnuXQT.js) — OK`, exit 0. The
  standing note's "pre-existing red at base HEAD" is **no longer true** — the entry-chunk split landed
  since, so the owner's 2026-09-16 stale ruling no longer has to be invoked.
- [x] **Owner visual gate recorded with both screenshot paths.** T23's after-set plus the before-set
  under `e2e/artifacts/story-scene/` and `e2e/artifacts/story-ui/` (both gitignored and regenerated by
  the two recorded commands); agent-performed per T23's amendment. Re-run 2026-09-23, 6/6 green,
  reviewed against the draft: gate-720 side by side, mobile stacked speaker-forward.
- [x] **`npx vitest run src/i18n/` and `src/shell/bandGuard.test.ts` green for this program's paths.**
  Included in the 8-file / 84-test guard run above; `src/i18n` 5 files green.

---

## Phase 6 — Absorbed scope (owner, 2026-09-15: "absorb them")

The coverage audit listed three areas as "owned outside this program". The owner directed them to be
**absorbed into this plan**, so they are now in scope. Two of the three also resolve a real
**duplicate-ownership conflict**, recorded per task.

### Task 24: The remaining band violations on other surfaces

**Spec:** `spec-band-compliance.md` (extended scope) · **Size:** S (3 files)

**Description:** Fix the three remaining stray-tier violations so `bandGuard.test.ts` is **fully green**,
not just green for this program's paths. Each is a stacking tier picked locally instead of via the
band system.

**The three, with their real fix (each verified by reading the rule and the code):**

| File:line | Violation | Fix |
|---|---|---|
| `ui/gui-lego/conditionConsole.css:229` | `.radial-wrap .n { z-index: 1 }` — lifts the radial's centre label above the SVG arc | The label is a later sibling inside a positioned wrapper → **normal flow paints it above**; delete the declaration and assert the label is still visible |
| `ui/gui-lego/shieldConsole.css:100` | `.shield-segment .meta { z-index: 1 }` — lifts the segment meta above the fill | Same shape (`.meta` follows the fill in document order) → delete and assert |
| `dev/PhaserSceneSwitchPocPage.tsx:284` | `className="fixed inset-0 z-[80] …"` on the GG-11 panel | Use a **band utility** (`.band-dialog`-class scrim/overlay) — `dev/` is exempt from the *DialogShell* scan (`bandGuard.ts:136-150`) but **not** from the stray-tier scan (`scanForStrayZIndex` skips only `theme/tokens.css`, `:58-64`) |

**Acceptance criteria:**
- [ ] `npx vitest run src/shell/bandGuard.test.ts` → **0 failed** (all 11 tests).
- [ ] No `z-index`/`z-*` remains in `conditionConsole.css`, `shieldConsole.css`, or the dev page.
- [ ] The radial centre label and the shield meta are still visible above their fills — **verified
      visually** (CSS paint order is not jsdom-testable), recorded.
- [ ] The dev GG-11 panel still overlays and still closes; its Track-A identity assertion still passes.
- [ ] `conditionConsole`/`shieldConsole` visual output is unchanged apart from the removal.

**Verification:**
- [ ] `npx vitest run src/shell/bandGuard.test.ts`
- [ ] `npm test -- --run conditionConsole` · `npm test -- --run shield`
- [ ] `npm test -- --run PhaserSceneSwitchPocPage`
- [ ] `npm run build`

**Dependencies:** T1, T4 · **Risk:** Medium (paint order is the thing under test and is not unit-testable)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/conditionConsole.css`
- `gk-web/web/fusion-rpg-web/src/ui/gui-lego/shieldConsole.css`
- `gk-web/web/fusion-rpg-web/src/dev/PhaserSceneSwitchPocPage.tsx`

---

### Task 25: Relocate the `layerStack` import behind a shell accessor

**Spec:** `spec-band-compliance.md` (extended scope) · **Size:** S (3 files)

**Description:** `stages/world/mapChromeMute.ts:5-6` imports `layerStack` directly, which the guard
forbids outside `shell/` (`bandGuard.ts:72-80` — `LayerStack` is a shell-only mechanism, GG-1's one owner
of visibility, `layerStack.ts:29-34`). Rather than widen the guard, put the **shell-owned accessor**
where it belongs and have the stage delegate to it.

**The fix:** add `shell/stageChromePolicy.ts` exporting the same predicate (it may read
`useLayerStack` because it lives in `shell/`), and make `stages/world/mapChromeMute.ts` **delegate** to
it so the three existing callers (`WorldStage.tsx:146`, `turn/UnresolvedCount.tsx:53`,
`lenses/useLensHotkeys.ts:24`) and the existing test keep their import paths and pass unchanged.

**Acceptance criteria:**
- [ ] No file under `src/` outside `shell/` imports `layerStack` (`npx vitest run src/shell/bandGuard.test.ts`
      → the layerStack-import test passes).
- [ ] `shell/stageChromePolicy.ts` owns the band-mute predicate; `stages/world/mapChromeMute.ts`
      delegates and keeps its public name.
- [ ] `mapChromeMute.test.ts` passes **unchanged** (behaviour identical: panel/dialog mute, system wins,
      empty stack unmuted).
- [ ] `WorldStage`, `UnresolvedCount`, `useLensHotkeys` are **not** modified.
- [ ] No new `z-index`; no keybinding change.

**Verification:**
- [ ] `npx vitest run src/shell/bandGuard.test.ts`
- [ ] `npm test -- --run mapChromeMute`
- [ ] `npm test -- --run WorldStage`
- [ ] `npm run build`

**Dependencies:** T1, T4 · **Risk:** Low

**Files likely touched:**
- `web/fusion-rpg-web/src/shell/stageChromePolicy.ts` (new — the shell-owned accessor)
- `gk-web/web/fusion-rpg-web/src/stages/world/mapChromeMute.ts` (delegate)

**Landed 2026-09-16 with one judged deviation (T2 precedent): the accessor is
`shell/topLayer.ts` exporting `isTopGestureCaptured()`, not `stageChromePolicy.ts` — a generic
shell query rather than a stage-named one, since the policy it encodes (panel/dialog capture
gestures, system owns Esc) belongs to the shell, not the world stage. Every acceptance item holds
literally otherwise: no non-shell `layerStack` import, delegate keeps its public name,
`mapChromeMute.test.ts` and all three callers untouched, no z-index or keybinding change.

---

### Task 26: Adopt the shared pieces into `OnboardingReveal`

**Spec:** `spec-dialogue-window.md` / `spec-advance-control.md` (decision 4 made real) · **Size:** M

**Description:** Decision 4 said a reveal is a **one-beat scene** and that `OnboardingReveal` would
adopt the shared pieces "in a later increment". Absorbing makes this that increment: the reveal stops
hand-rolling its heading/body/button trio (`OnboardingReveal.tsx:24-33`) and composes
`dialogue-window` + `advance-control`, with `scene-progress` omitted because `total <= 1`.

**Ownership note — this task resolves a duplicate-ownership conflict.** `OnboardingReveal.tsx` sits in
the sibling program's spec (`standalone/spec-first-session-progression.md`). Its checkpoint semantics
(query, claim mutation, `onOpenCommanders`) are **that program's**, and this task **must not** change
them. Absorbing the *presentation* is the point; the reveal's **data and lifecycle stay where they are.**

**Acceptance criteria:**
- [ ] `OnboardingReveal` renders through `dialogue-window` + `advance-control`; its hand-rolled
      heading/body/button markup is gone.
- [ ] **No** `scene-progress` node renders (one-beat rule — the omission rule proves itself here).
- [ ] The reveal's **behaviour is unchanged**: the same checkpoint content, the same claim action, the
      same `onOpenCommanders` call, the same loading/error/`null` paths (`:19-21`).
- [ ] `OnboardingReveal.test.tsx` passes **unchanged**.
- [ ] **The owning spec is not edited** (`standalone/spec-first-session-progression.md`) — this is a
      presentation adoption, not a contract change. If the contract must change, that is a separate ask.
- [ ] All reveal copy is a lingui message (`msg` + `useLingui`), no bare `t`.
- [ ] No new `z-index`; the reveal still sits where it sat (it is an inline block, **not** a band
      surface — do not promote it to one).

**Verification:**
- [ ] `npm test -- --run OnboardingReveal`
- [ ] `npm test -- --run first-session` (the owning program's tests, unmodified)
- [ ] `npm test -- --run dialogueWindow` · `npm test -- --run advanceControl`
- [ ] `npm run build`

**Dependencies:** T16, T14 · **Risk:** Medium (another program's user-visible surface)

**Files likely touched:**
- `gk-web/web/fusion-rpg-web/src/stages/sanctum/OnboardingReveal.tsx`
- `gk-web/web/fusion-rpg-web/src/stages/sanctum/OnboardingReveal.test.tsx` (expected **unchanged**)

**Landed 2026-09-16 (committed).** Reveal renders through `dialogue-window` + `advance-control`
(envelope payloads built inline, no recipe needed — factories are functions), `scene-progress`
never mounted, container/testids/loading/error/Dave-sheet paths unchanged. Skip dismisses locally
without claiming (presentation-only; server state untouched; the piece forbids hiding skip).
Copy is `msg` + `useLingui` behind a self-provided `I18nProvider` (same singleton — bare-test
safe, nested provider changes nothing). Piece extended backward-compatibly with optional
`primaryTitle`/`pendingTitle` (the owning suite pins the Saving title on the button). Evidence:
owning suite 3/3 unchanged, dismiss/piece-layout suites new, advanceControl titles new, first-session
suite N/A in this tree (owning fence), extract clean with locales committed, build green.

---

### Task 27: The Unity-side `rift.*` cue channel

**Spec:** `spec-cue-seam.md` (extended scope) · **Size:** L → **split into T27a + T27b**

**Description:** Wire the four declared recipes so a story cue can reach `VfxDirector` in-game. Decision
3 kept this a named, unwired seam; absorbing makes it real.

**Ownership resolution — two conflicts, both stated rather than duplicated:**

1. **The injector VFX wiring already has an owner list.** `tasks/onboarding-rift-todo.md` T12 (recipes),
   **T13** (director integration + live proof) and **T14** (VFX↔dialog seam) are **OPEN** and describe
   exactly this work; `docs/architecture/rift-gate-ideal.md:117` says it *"Belongs to the **onboarding**
   program's open T13/T14"*. Absorbing means this plan owns it, so **T12–T14 must be closed as
   superseded** — two live task lists owning identical work is the drift this audit exists to catch.
   That closure is a **coordination action for `/build`**, performed by naming it, not a gate.
2. **The FE→host transport is another program's decision.** `rift-gate-ideal.md:113` records an
   exhaustive negative — *no `FE → host message channel of any kind`* — and its decision 9 owns a
   `rift.hide` bridge verb. **Building a second channel here would violate one-owner-per-mechanism.**
   So this task **consumes** the shared bridge; it does not create a competing one.

**T27a — injector-side director wiring (this program, no transport needed)**
- [ ] The four `rift.*` recipes resolve through `VfxDirector` (already cue-id-agnostic,
      `VfxDirector.cs:65-73`) with anchor degradation (`:207-223`).
- [ ] `scripts/prove-vfx.ps1` gains a rift case and **exits non-zero on failure** (`:378`).
- [ ] A missing anchor or shader failure emits a skip reason and leaves the story usable.
- [ ] Reduced motion still yields an instant state change, not an animation.
- [ ] **No** new `VfxCatalog` cue id, **no** gameplay write, **no** binary patch.

**Files (T27a only — 2):**
- `gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs` (or a story-cue consumer beside it)
- `scripts/prove-vfx.ps1`

**T27b — story→host cue delivery (consumes the shared bridge)**
- [ ] The scene's `onCue` seam is wired to the **shared** host bridge — the same channel rift-gate
      already owns, not a new one.
- [ ] **If the shared bridge does not yet exist**, this task stops at the seam and records the blocker;
      it does **not** invent a second channel. (Reversible default: the FE-local `data-cue` effect from
      decision 3 remains the shipped behaviour until the bridge lands.)
- [ ] No new keybinding (F10 stays forbidden, `keymap.ts:18`); no socket; no engine vocabulary on the
      player surface.

**Files (T27b only — 2):**
- `gk-fusion/src/FusionRpg.Injector/Hud/OverlayViewHost.cs` (wire into the **existing** host message path)
- `gk-web/web/fusion-rpg-web/src/features/story-scene/storyCue.ts` (emit over the shared channel)

**Coordination (not a file edit here):** `tasks/onboarding-rift-todo.md` T12–T14 are closed as
superseded, so one list owns the VFX wiring. That list belongs to the onboarding program and is done in
that program's session or by the owner — this plan **names** the duplication rather than editing
another program's todo.

**Assessed 2026-09-16 — T27b BLOCKED by design, T27a substantially already built:**
- **T27b stops at the seam (reversible default, as instructed).** Verified both sides: no
  `WebMessageReceived`/host-object channel in `OverlayViewHost.cs`, zero `postMessage` calls in
  the web FE, no `rift.hide` anywhere in `src/`. The shared bridge does not exist, so no channel
  was invented; the FE keeps the shipped `data-cue` behaviour. No code written — correctly.
- **T27a core already landed by onboarding** (`71a28b28c feat(onboarding): add Rift teaser and
  menu VFX`): the four ids are catalog constants AND backed by recipes (portal purple / surge
  green / seal blue / fade muted — Fixed colors, table-owned durations, pure render specs, no
  gameplay writes). Director mechanics already satisfy the rest: cue-agnostic `Play`, anchor
  degradation via `Missing` skip (story stays usable), no-throw loop. Remaining with onboarding:
  reduced-motion has NO concept anywhere in `src/` (needs design + live proof, not a drive-by),
  the `prove-vfx.ps1` rift case (script exists but needs the running game), and the owner-run
  live proof of all four cues.
- **T12–T14 coordination named, not closed:** that list is the onboarding program's to close (or
  the owner's); editing it from here would be the drift this audit catches.

**Verification:**
- [ ] `npm test -- --run storyCue` · `npm run build`
- [ ] Injector build + `scripts/prove-vfx.ps1` (live proof, owner-run) — **`prove-vfx.ps1` still has
      no rift case** (`grep -n rift scripts/prove-vfx.ps1` → no hits, confirmed 2026-09-20); not
      added in this pass, see below.
- [ ] `python gk-core/scripts/audit-magic-numbers.py` (no new magic number)
- [ ] **Owner-run live proof** — the four cues visibly reach the game — **`live-qa` 2026-09-20
      attempted** (evidence [story-scene-rift-vfx-live.md](evidence-fragments/story-scene-rift-vfx-live.md)):
      fired all four (`rift.portal.open/surge`, `rift.quarantine.seal/fade`) via the same real
      `POST /api/debug/fx/play` route `prove-vfx.ps1` itself uses. All four produced a real
      `debug.fx.shown` — zero skips, zero errors, the pipeline claim holds. **Real finding:** every
      one rendered as the SAME generic white/neutral burst (`rgb:"#FFFFFF"`), not its own distinct
      authored color (purple/green/blue/muted) — consistent with firing them against a lawn cell
      rather than their real onboarding-flow anchor (`ptr:""` on every payload), but worth the owning
      program checking whether a missing anchor should skip (as documented) rather than silently
      substitute the fallback color. Visual "looks right" half not confirmed; pipeline-reaches-the-game
      half is.

**T27a's in-fence half landed; the 2026-09-20 live-qa finding is withdrawn; T27b's blocker is stale (2026-09-23, lane `story-scene-1`).**

- **`scripts/prove-vfx.ps1` gained the rift cases, and now covers every T27a acceptance line the script can reach** (re-checked 2026-09-23): four cell-anchored plays assert `primitives=burst`, one `-TargetPtr` play asserts the recipe's second primitive (`flash`, which only spawns when a transform is followed — `VfxDirector.cs:299-301`), and a fifth — `rift-missing-anchor`, `ptr: "0x1"`, `amount = -915` — asserts **`skipped` with reason `missing`**, i.e. T27a's "a missing anchor … emits a skip reason and leaves the story usable". That case is safe by construction rather than by luck: `AnchorResolver.Resolve` parses the string and looks it up in `InjectorEntityRegistry`'s dictionary (`FindZombie`/`FindPlant` → `TryParsePtr` + `TryGetValue`, `AnchorResolver.cs:19-31`, `InjectorEntityRegistry.cs:315-327`), nothing dereferences it as a native pointer, and every failure path returns null (a caught exception included). All five ride the existing `expectPrim`/`expectSkip` paths, so a wrong id, a dropped recipe or a lost skip reason exits non-zero at `prove-vfx.ps1:412`.
  Evidence: parse OK (`Parser::ParseFile` → no errors); the four ids diff-equal to the four `VfxCueIds.Rift*` constants (`IDS-MATCH-EXACTLY-THE-FOUR-CATALOG-CONSTANTS`); `python gk-core/scripts/audit-magic-numbers.py` → `total 0 finding(s)`; the script had **zero** rift references on 2026-09-20 (`grep -n rift` → 0 hits; 8 now). The live run is still owner-run (see below), so this is the complete in-fence instrument, not the proof.
  `total 0 finding(s)`. **The live run is not made here**: the script's organic block ends in
  `/kill` (`:283`), so a full run needs a claimed live slot and a lab board — owner-run, as this row
  already said (`scripts/prove-vfx.ps1 -TargetPtr <ZombiePtr>`).
- **The "all four render the same generic white burst" finding is WITHDRAWN — it misread the
  payload.** `debug.fx.shown.rgb` is the **color plan** (`VfxDirector.cs:621` → `plan.Rgb`, which is
  `(255,255,255)` for a tag-less, element-less cue — `VfxColorPlan.Rgb`'s default), while a
  `Fixed`-colour primitive renders `spec.FixedRgb` (`BurstPool.cs:72-73`, `VfxDirector.cs:346`) and
  **the payload has no field for it at all**. The four recipes are distinctly authored
  (`VfxCatalog.cs:449-537`: portal 210,100,255 · surge 190,255,70 · seal 120,220,255 · fade
  150,120,220). So the open question the probe raised ("should a missing anchor skip instead of
  degrading to white?") **does not exist**, nothing is owed to the onboarding program, and the"white"
  observation was the plan's neutral colour, not a rendered burst. The authored colours stay
  **eyeball-only**, which the script now says in its own checklist; the new script comment records
  the reasoning so the next edit does not re-add `expectRgb` and get a false failure.
- **T27b's recorded blocker is STALE.** "No shared FE→host bridge exists" was true on 2026-09-16;
  rift-gate has since shipped one — `OverlayCommandNames.Hide`
  (`gk-core/src/FusionRpg.Core/Overlay/OverlayCommandNames.cs:19`), `POST /api/overlay/leave`
  (`gk-core/src/FusionRpg.Server/OverlayEndpoints.cs:21`), drained at
  `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:112-114`, emitted by the FE at
  `gk-web/web/fusion-rpg-web/src/lib/bus/overlay.ts:13-14`. T27b is therefore **not** bridge-blocked. It
  stays blocked on two things, both named: (a) **this lane's fence** — a story cue needs a *new verb*
  in a vocabulary that today holds exactly one (`overlay.hide`), plus a server route and an injector
  arm, all under `src/`, outside `gk-web/web/fusion-rpg-web/**`; and (b) **locked decision 4** ("the FE owns
  the cue … no injector work"), which is why `SanctumStage.tsx:269` still passes no `onCue` and the
  FE-local `data-cue` effect remains the shipped behaviour. Whoever takes T27b needs an owner ruling
  on the verb name before any code, not a bridge.

**Dependencies:** T18 (cue seam), T25 · **Risk:** **High** (cross-process, live, and two owner conflicts)

**Files likely touched:** per half — T27a's two files are listed above, T27b's two below it. **No file
in this task is edited twice**, so each half stays within the cap.

---

## Checkpoint G — absorbed scope complete

- [x] `npx vitest run src/shell/bandGuard.test.ts` → **0 failed** (all 11) — done 2026-09-16,
  owner-approved crossing ("clean 2 pre failure too"), landed in this session: condition `.n` and
  shield `.meta` tiers removed as provably redundant (paint-order analysis in the CSS comments —
  absolute-over-static and DOM-last-among-positioned respectively; `relative` on `.meta` KEPT as
  load-bearing), PoC `z-[80]` → `band-panel`, and the `mapChromeMute` store import replaced by a
  shell-owned `isTopGestureCaptured()` facade (`shell/topLayer.ts`, exact walk preserved, callers
  and test untouched). Evidence: bandGuard 11/11, 709/709 across `stages/world` + `ui/gui-lego` +
  shell suites, `tsc` clean, build green, PoC e2e green.
- [x] `npx vitest run src/i18n/` → **0 failed** (5 files, 60 tests — measured 2026-09-16; it was never in the failing set, only unmeasured)
- [ ] The radial label, shield meta, and dev panel are visually correct after the tier removals —
  NOT visually re-photographed: the removals are construction-proofs (no paint-order change
  possible — the mechanism is pinned in comments), and all owning suites pass. **Still open with a
  named dependency (2026-09-23):** closing it needs a capture of `conditionConsole` (the radial
  centre label) and `shieldConsole` (the segment meta) on their real owning surfaces, or the owner's
  10-second eyeball on the lawn HUD. No e2e fixture reaches either console today, so this lane would
  have to build one — an owning-program capture, not story-scene's fence. Do not hold T23 on it.
- [x] `OnboardingReveal` renders through the shared pieces; its tests pass **unchanged** — 2026-09-23:
  `OnboardingReveal.tsx` imports and mounts `dialogueWindowFactory` + `advanceControlFactory`
  (`:7,:9,:114,:137`) and no hand-rolled heading/body/button trio remains; the adoption commit
  (`cc9e0f9ef`) touches `OnboardingReveal.tsx`, the two catalogs, `advanceControl.*` and a **new**
  `OnboardingReveal.dismiss.test.tsx` — `OnboardingReveal.test.tsx` is not in that commit's file list,
  so "unchanged" holds literally. Owning suite green in the 29-file run.
- [x] No `scene-progress` node in the reveal (one-beat omission proven on a real consumer) — 2026-09-23:
  the reveal mounts only the two factories above; `scene-progress` appears in the file solely as the
  doc comment's "deliberately never mounted" note, and the owning suite asserts its absence.
- [ ] The story cue reaches the game **live** (`prove-vfx.ps1`), or T27b is recorded as bridge-blocked —
  **left unticked, and the reason changed.** The second branch is now **false as written**: T27b is
  not bridge-blocked, because the bridge shipped (see the T27 row) — recording it as bridge-blocked
  would be recording something that is not true, and the rule is that an acceptance line which cannot
  pass as written is never closed `done`. The first branch is unrun: the four rift cases now exist in
  the script, but running them needs a claimed live slot and a lab board, and the script's organic
  block ends by killing the lab target — owner-run. So the box stays open on **one** unrun owner step
  plus one erratum (the disjunction needs `bridge-blocked` replaced, since that state no longer
  exists).
- [ ] `tasks/onboarding-rift-todo.md` T12–T14 closed as superseded, so one list owns the VFX wiring —
  **external to this lane's fence**: `tasks/onboarding-rift-todo.md` is not in the allowed paths
  (`gk-web/web/fusion-rpg-web/**`, `docs/architecture/story-scene*`, `tasks/story-scene-*`, `scripts/**`).
  The row is named here and in the T27 row; closing it is the onboarding program's or the owner's edit.
- [ ] **Owner confirms the reveal still looks right** (another program's surface) — owner gate, unchanged.

---

## What absorption did NOT include, and why

| Item | Why not absorbed |
|---|---|
| **F1 — `web` boundaries in `verification-boundaries.v1.json`** | ~~A LIVE session owns those exact files (`verification-boundaries-20260913-6f31`, status `active`...)~~ — **STALE 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P2): `tasks/sessions/verification-boundaries-20260913-6f31.json` reads `"status": "merged"` since 2026-09-17. **SUPERSEDED by `test-verification-boundary`** (`summoner-convergence` lane D — a convergence file, read-only here): its own map names `verification-boundaries-map.md` as "Predecessor program, whose decisions this one keeps" and still lists web boundaries as open (`docs/architecture/test-verification-boundary-map.md:231`). Not this program's fence to build against anymore — the FE-test-selection gap is that program's to close |
| F3 — `chrome.tsx:153,157` dev footer copy | **Closed 2026-09-23** (see the follow-up row): not in the three areas you named, but the ideal's own "fix the default" instruction held — the defaults were another surface's copy in a shared piece. The producer's wording is untouched |
| F6 — promote specs into `gui-lego/` | Would cross the gui-lego fence mid-flight; a mechanical move better done once this program has landed |
| F7 — queue row | Outside this session's fence by design; the row is one line and can be added by whoever owns the queue next |
| F8 — `lineRevealPerCharMs` / `autoAdvanceMs` | A real decision (wire or delete), not a defect. Kept visible as a follow-up |

**Say the word on any of the above and I will absorb it too** — except F1, which cannot be absorbed
without breaking another live session's fence.

---

## Follow-ups (non-blocking, tracked — not gates)

**Absorbed 2026-09-15** — F2 (band violations), F4 (reveal adoption) and F5 (Unity `rift.*` wiring) are
**no longer follow-ups**: they are T24, T26 and T27. They stay listed here struck through so the
original numbering is not silently reused.

| # | Follow-up | State |
|---|---|---|
| F1 | Add `web` boundaries to `gk-core/scripts/verification-boundaries.v1.json` so `verify-change.ps1` can select FE tests | ~~Open — cannot be absorbed. A live session (`verification-boundaries-20260913-6f31`) fences those files~~ — **SUPERSEDED 2026-09-20** by `test-verification-boundary` (see "What absorption did NOT include" above; the fence citation was stale, the work itself belongs to that program) |
| ~~F2~~ | ~~Fix the four unrelated band violations~~ | **Absorbed → T24, then landed early 2026-09-16 by owner approval** (Checkpoint G box 1: bandGuard 11/11; see the delta note under the red-guard baseline) |
| F3 | Fix `chrome.tsx:153,157` (dev footer copy as defaults) | **Closed 2026-09-23, same lane.** The ideal's own instruction ("the defect is the **default**. Fix the default; do not rewrite the piece", `story-scene-ideal.md:241`) was right, and my first reading of this row was wrong: the defaults were unreachable **today** (one live consumer, which passes both fields) but they are another surface's copy inside a **shared** piece — any second recipe binding `surface-foot` would render the derived console's engine wording as its own. Fixed in `chrome.tsx`: `note`/`deferred` no longer default to anything, so absent means absent and the caller states its own line. The live producer (`foldDerivedSurfaceVm.ts:463-464`) is untouched, so the derived console's output is byte-identical. New guard `src/ui/gui-lego/pieces/chrome.foot.test.tsx` (3 tests): payload rendered verbatim, nothing invented when omitted (no empty sibling span either), and a source scan for the wording. **Residual, named not dropped:** the piece's own `"Hidden unchanged:"` label is still a literal — it is the approved draft's copy on a developer console (`docs/design/derived-combat-console.html:572`), so localizing it is that surface's contract change, not a default fix |
| F6 | Promote the piece specs into `gui-lego/` | **Blocked at this lane's allowed paths — re-verified 2026-09-23, and the original reason needed correcting.** The old text said "would cross the gui-lego fence mid-flight"; that flight has landed — every session record naming a `docs/architecture/gui-lego/**` path is `merged` (`backlog-clean-up-build-20260920`, `build-preset-20260920`, `notification-ssot-20260920`, `web-guard-repair-20260920`), and no *active* record lists one, so **no competing session owns the destination**. What blocks it is mechanical: this lane's allowed paths do not include `docs/architecture/gui-lego/**`, and the runner fails a run for any file outside them. The destination exists and is the right home (`docs/architecture/gui-lego/` holds `README.md`, `spec-*.md` per piece, `menu-refactor-queue.md`), the 21 sources are all under `docs/architecture/story-scene/`, and **no gui-lego doc references a story-scene spec today** (`grep -rn "story-scene/" docs/architecture/gui-lego/*.md` → 0 hits, so the move leaves no dangling link behind). What blocks it is the fence: `docs/architecture/gui-lego/**` is **not** in this lane's allowed paths (`gk-web/web/fusion-rpg-web/**`, `docs/architecture/story-scene/**`, `docs/architecture/story-scene-map.md`, `docs/architecture/story-scene-ideal.md`, `tasks/story-scene-*`, `scripts/**`), and the promotion is not one-sided — it needs gui-lego's own `README.md` + `menu-refactor-queue.md` rows (its owner's files) *and* the reference updates on this side (`story-scene-map.md`, `story-scene-ideal.md`, this todo) in the same commit, or the program's index points at a folder it no longer owns. **Dependency, precisely:** a lane (or the manager) whose brief includes `docs/architecture/gui-lego/**` — not a live probe, not another lane's unmerged work. Recorded; not attempted across the fence |
| F8 | Wire or delete `lineRevealPerCharMs` / `autoAdvanceMs` | **Closed 2026-09-23 as a decided disposition, not code — and the decision is “keep them, unread, on purpose”.** The specs already answer this and my earlier framing was too vague: `spec-scene-tunables.md:56-57` gives both keys a unit, a meaning and an off-value (“0 is the honest default (no typewriter unless wanted)”, “‘null’ = never auto-advance”), `story-scene-ideal.md:405-406` calls them *if ever* / *if used*, and `story-scene-plan.md:319` already said “v1 reads neither **by design**”. So an unread key here is not drift — it is the declared home for a feature the owner may enable later, which is why its unit/meaning/off-value were written down first. **Wiring** one is a feature plus an owner decision (Boundaries: changing `autoAdvanceMs` from `null` is ask-first; a typewriter needs reduced-motion and layout-stability design no task owns), and a null-guarded timer today would be a mechanism no host reaches — the thing this repo refuses to call done. **Deleting** them was the other half of the row and is a `gk-core/data/tuning/story-scene-ui.v1.json` edit, i.e. outside this lane’s allowed paths and, per `tunables-ssot.md`, a `v2` publish through `gk-core/tools/tuning/publish.py` rather than a hand-edit; rejected on merits too, since the keys would return as code literals the moment someone wants them. Recorded in `spec-scene-tunables.md` § “Who reads these today” |
| F9 | **New 2026-09-23 — the sprite placeholder and the advance tooltip were English literals, not catalog messages. CLOSED the same day, same lane.** `actorSprite.tsx:47` built the accessible label as `` `${displayName} — art not yet available` `` and `:91` rendered `art not yet authored`; `advanceControl.tsx:134,142` fell back to `"Working…"` — which contradicted that piece's own doc comment ("absent by default … an untitled button stays untitled"). All three were English under any locale and no locale could change them; none was a beat line, so the catalog-level pseudo tests never saw them. **Fixed:** two new messages in `STORY_SCENE_PIECE_LABELS` (`story-scene.sprite.hint`, `story-scene.sprite.placeholder` — ICU-interpolated with the resolved name), resolved by the host (`StorySceneHost.tsx:117-121`) and carried on the sprite payload (`foldStorySceneVm.ts`), plus the two title fallbacks deleted. Evidence: `actorSprite` + `actorSprite.test.tsx` source scan for the literals; `StorySceneHost.pseudo.test.tsx` asserts the hint and every placeholder label on every beat; 27 files / 299 tests green; e2e 6/6 with identical English captures; `extract` 44 → 46 messages. Residual → **F12**. The `*.rd` "recipe not registered" fallback was checked and deliberately left (unreachable programming-error surface, shared idiom across four hosts) |
| F12 | **New 2026-09-23 — the fallback `initial` is derived from the English name. RULED AND CLOSED the same day, in-lane — overturn freely.** `actorCast.ts:37-38` derives it from `displayName` and authors `"D"`/`"P"` (`:73,:80`), so under a non-Latin translation the name localizes and the initial stays Latin. Ruling: **keep it derived and unlocalized.** `initial` is an *identity glyph* — the monogram in the labelled fallback, `aria-hidden`, decorative — not prose; making it a message would re-author the name's own first letter in a second place, which is exactly the drift the field's “derived, not authored twice” rule prevents, and it would let the two disagree inside a 44px circle. Recorded in `spec-actor-cast.md` § “initial is not localized” and pinned by `StorySceneHost.pseudo.test.tsx`: under pseudo the name is marked while the initial is the authored glyph (asserted per actor, on every beat). A locale whose monogram must differ is a **new ruling**, not a defect in this one |
| F11 | **New 2026-09-23 — the pseudo locale's *layout* half had no mechanism. CLOSED the same day, same lane.** `setLocale("pseudo")` returns early outside `import.meta.env.DEV` (`i18n/index.ts:79-82`) and the end-to-end gate runs a production preview where `window.__i18nDebug` is stripped, so no browser run could render pseudo — the S4 acceptance test proved the *string* half (vitest) and nothing proved “a layout that can't survive a longer translation”. **Fixed without shipping pseudo:** an opt-in **dev** project, `e2e/story-scene-pseudo.spec.ts` + `e2e/helpers/pseudo-gate.ts`, drives `vite dev`, switches the locale on the live instance the way System → Preferences does, then applies the T23 obligations in pseudo. Evidence: `E2E_DEV_PORT=4402 npx playwright test e2e/story-scene-pseudo.spec.ts --project=pseudo-chromium` → **3 passed**, 12 captures, `bodyOverflows=false` and `pseudoMarked=true` at 1280×720, 1280×600 and 390×844. It also proved a **real defect** in the process: the host's resolvers were keyed on the `i18n` singleton, so a locale switched while the scene was mounted left it in the old language — fixed (`StorySceneHost.tsx:114,128`, dep on `i18n.locale`) and pinned by `follows a locale switch made while the scene is open`, which reds on revert. The shared `e2e/helpers/sanctum-story-mock.ts` keeps both story gates photographing the same surface | 
| F10 | **New 2026-09-23 — `npm test` was flaky at the file boundary. CLOSED the same day, same lane — and one of the three was a real defect, not flakiness.** Three consecutive runs of one unchanged tree gave `3 failed / 382 passed (385)`, `2 failed / 383 passed`, `1 failed / 385 passed` — each a different file, which is why it read as noise. Diagnosed to three distinct causes and fixed: **(1) a real GG-55 violation** — `layers/relics/Workbench.tsx:469` (`craft-upgrade-preview-btn`) was disabled with **no** reason on the control, so `disabledReasonGuard` failed on the real tree; it now carries the repo's own busy idiom (`title={busy ? "Working…" : undefined}`, the string ~10 sibling sites already use) and its neighbour `craft-upgrade-btn` gained the *busy* cause it never named (it explained only "Preview the upgrade first", so busy-but-previewed was disabled with nothing to say). **(2) two lazy-mount waits with a 1s budget** — `condition.waveCD.test.tsx` waiting on `lazy(() => import("./StandingRadarChart"))` (`condition.tsx:11`) and `SanctumStage.test.tsx:304` waiting on the lazily-mounted Pacts layer; the first got an explicit 5s budget with the cause in a comment, the second is covered by **(3) a global async budget** — `src/test/setup.ts` now sets `configure({ asyncUtilTimeout: 5000 })`, because "the chunk has not loaded yet" is not an assertion and 1s is short for a dynamic import under a fully parallel run. Timeouts only bound how long an *unmet* condition is waited for; every assertion still has to pass, so a regression still fails (1s later). **Evidence:** `npm test` → **386 files / 3239 tests passed, exit 0** (the first fully green full-suite run in this lane's three attempts), `disabledReasonGuard` 6/6, `condition.waveCD` 7/7, `src/stages/sanctum` 21/21, `src/layers/relics` 85/85 incl. `workbench.test.tsx` 25/25, `npm run build` clean. **Named for their owners:** (1) belongs to `species-gear-chain` (the file's own comment cites its T37) and (2) to the gui-lego condition surface; (3) is FE test infra — every lane is affected, and the revert is one line. One green run does not *prove* a flake is gone; what is proven is that each failure had a cause that is now fixed |
| F13 | **New 2026-09-23 — a shared worktree port silently invalidates e2e evidence (infrastructure, repo-wide).** `playwright.config.ts` hardcoded `4173` (preview) / `5173` (dev) with `reuseExistingServer: !CI`, and several cmdc lanes run on one machine. While this lane ran the story gates, `127.0.0.1:4173` was already held by **another worktree's** preview server (`cmdc-ep-autoassign`, pid 74584) — so two of my gate runs were served *that* tree's build and reported 6/6 green. Nothing in the output says whose build it is; the only reason it surfaced is that the run took 4s instead of 90s and I checked the listener's command line. **Mitigated here, not fixed repo-wide:** the ports are now env-overridable (`E2E_PREVIEW_PORT` / `E2E_DEV_PORT`, documented at `playwright.config.ts:11-17`) and this lane's evidence was re-taken on private ports (`E2E_PREVIEW_PORT=4401` → 6/6; `E2E_DEV_PORT=4402` → 3/3). The repo-wide answer (per-lane port convention, or failing when a foreign server owns the port) is an infrastructure ruling — ownership: whoever owns the cmdc lane tooling |
| ~~F4~~ | ~~Adopt the shared pieces into `OnboardingReveal`~~ | **Absorbed → T26** |
| ~~F5~~ | ~~Wire the Unity-side `rift.*` VFX recipes~~ | **Absorbed → T27a/T27b** |
| F6 | Promote the piece specs into `gui-lego/` | Open — **blocked at this lane's fence** (see the row above); the move needs gui-lego's own README/queue rows plus this side's index updates in one commit |
| F7 | Add the `story-scene` row to `docs/architecture/gui-lego/menu-refactor-queue.md` | **Done, closed 2026-09-20** (`backlog-clean-up` BCU7.6) — the fence claim was stale, no session held that file; added the row (`Status` section, matching the `W2 Wonder composer` precedent for a non-rail consumer) |
| F8 | Wire or delete `lineRevealPerCharMs` / `autoAdvanceMs` | Open (a decision, not a defect) |

---

## Audit record (coverage + semantic gaps, 2026-09-15)

The plan was audited for **coverage** (every spec has a task; every task names a real spec) and for
**semantic coverage** (every binding requirement has an owning task). Coverage was already clean;
semantic coverage was not.

**Mechanical coverage — clean**

| Check | Result |
|---|---|
| Specs referenced by a task | **21 / 21** |
| Task spec refs that do not exist | 0 |
| Files named in spec `Touches:` lines that appear in no task | **0 / 30** |
| Map modules with no task | 0 |
| Tasks with acceptance + verification + dependencies | 23 / 23 |
| Tasks over the ~5-file cap | 0 (max 4) |

**Semantic gaps found and fixed**

| Id | Gap | Why it mattered | Fixed in |
|---|---|---|---|
| **G1** | No task registered the new piece factories. The plan named `registerStoryScene.ts` but nothing created the factory group or added the pieces to it — every piece would render as an **unthemed fallback div** (`RecipeMount.tsx:35-56`) with no factory | **Blocking** — the whole surface would silently render as unstyled divs | T5 (group module + per-piece criterion) |
| **G2** | Only `sceneStage.css` had a home; the other six pieces had **no CSS owner**, though every one needs draft-scoped styling | High — six pieces would ship with no styling location | T5 (convention) + T12–T17 (per-piece criterion) |
| **G3** | `beatTransitionMs` was written by T2 but **read by no task** — a tunable nothing consumes | Medium — a dial that does nothing is drift | T19 (reads it as the real duration) |
| **G4** | The Enter/Space advance contract had **no owning task**. It exists today (`RiftPrologueDialog.tsx:159-164`) and would have been silently dropped by the cutover | **High** — a keyboard affordance regression on a live surface | T19 (owns the contract + focus target) |
| **G5** | T23 named an e2e visual gate, but **the mechanism does not exist**: no force-open path for the prologue and no `story-scene` playwright project (`playwright.config.ts:44-68`) | **High** — a binding gate with no way to satisfy it | T23 (stated mechanism: draft-HTML pair, mirroring `derived-ssot-side-by-side.spec.ts:31-46`) |
| **G6** | `riftAssets.ts` / `RIFT_ASSETS` / `RiftPrologueCueId` had **no disposition task**, and `RIFT_ASSETS` is imported only by the component being replaced | Medium — dead module left behind, or a silent deletion | T23 (retire or repoint, explicitly) |
| **G7** | The **focus contract** ("the window is the focus target, actors are not") appeared in the a11y section and in T17 negatively, but **no task asserted the positive** | Medium — an unasserted a11y promise | T19 |
| **G8** | The `menu-refactor-queue` row the ideal promised was **tracked nowhere** — not a task, not a follow-up | Low — a promise with no owner | **F7** |

**Also recorded:** `lineRevealPerCharMs` and `autoAdvanceMs` ship in the tuning file but v1 reads
neither. That is a deliberate default (no typewriter; no auto-advance), now written down as **F8** so it
is a decision rather than an oversight.

**Deliberately not added:** the four unrelated band violations, the reveal adoption, and the Unity VFX
channel were originally left out because each had an owner outside this program. **All three were
absorbed at the owner's direction the same day** — now T24, T26 and T27a/b — with their ownership
conflicts resolved in the task text. F1 remains un-absorbable (a live session fences those files).

---

## Absorption record (owner, 2026-09-15: "absorb them")

Three areas the audit had deferred became tasks. Each was checked against the repo's actual state
before being written, and **two turned out to hide a duplicate-ownership conflict** — which is the
same class of defect the audit exists to catch.

| Absorbed | Now | Conflict found | Resolution |
|---|---|---|---|
| The three stray-tier violations | **T24** | None — plain defects | Fix each by document order/band utility; pair with a recorded visual check |
| The `layerStack` import outside `shell/` | **T25** | None — a guard-forbidden import | Add `shell/stageChromePolicy.ts`; the three callers and the existing test keep their imports |
| `OnboardingReveal` adopts the pieces | **T26** | Its **contract** belongs to `standalone/spec-first-session-progression.md` | Presentation only; that spec is **not** edited; behaviour and tests unchanged |
| The Unity `rift.*` channel | **T27a/b** | **Two:** `onboarding-rift-todo.md` T12–T14 (OPEN) already own the injector VFX work; and `rift-gate-ideal.md:113` records that **no FE→host channel exists**, with decision 9 owning the bridge | T27 **closes T12–T14 as superseded** and **consumes** the shared bridge — it does not build a second channel. T27b stops at the seam if the bridge is not there yet |

**Pre-flight checks run before absorbing** (so the tasks are not written against a stale tree):

- `main`, `.kilo/worktrees/rift-gate-20260914` and `.kilo/worktrees/solid-run-20260912-eb53` are all
  **clean** on every absorbed path — nothing uncommitted would be clobbered.
- No story-scene task references another program's task numbers, so there is no numbering collision.
- The injected `z-index` lines were **read in context** (`.radial-wrap .n`, `.shield-segment .meta`,
  the dev panel overlay) — each really is a local tier that document order can replace.
- `mapChromeMute` has **three live callers** plus a test, which is why T25 delegates rather than moving
  the file.

**Not absorbed, and the reason is a hard fence, not preference:** F1
(`verification-boundaries.v1.json` + `verify-change.ps1` + `test-fast.ps1`) is fenced by the **active**
session `verification-boundaries-20260913-6f31`. Editing it would be exactly the cross-session
collision `AGENTS.md` forbids.

---

## Task summary

| Phase | Tasks | Sizes | Max files/task |
|---|---|---|---|
| 0 — Baseline & seams | T1–T5 | S, S, M, M, S | 4 |
| 1 — Contracts | T6–T9 | M, S, S, M | 3 |
| 2 — Theme | T10–T11 | S, M | 4 |
| 3 — Leaf pieces | T12–T16 | M, S, S, S, M | 4 |
| 4 — Composite pieces | T17–T19 | S, S, M | 4 |
| 5 — Fold, surface, host, cutover | T20–T23 | M, M, M, M | 4 |
| 6 — Absorbed scope | T24–T27 | S, S, M, L→split | 3 |

**27 tasks · 7 checkpoints · 0 gates · every task ≤4 files · 21/21 specs covered · 3 open follow-ups
(F3, F6, F8) — corrected 2026-09-20 (`backlog-clean-up` BCU7.6): F1 is SUPERSEDED (see the
Follow-ups table above), F7 is done (the queue row is added).**

**Absorbed at the owner's direction (2026-09-15):** T24 (band violations on other surfaces),
T25 (`layerStack` import behind a shell accessor), T26 (`OnboardingReveal` adopts the shared pieces),
T27a/b (the Unity `rift.*` cue channel). Former F2/F4/F5 are now tasks, not follow-ups.

---

## HANDOFF — 2026-09-16, PR #7 open, push is owner's

**Where everything sits.** Branch `worktree-rift-gate-20260914` (worktree
`.kilo/worktrees/rift-gate-20260914`) is fully pushed and clean; PR #7
(`rift gate plus story-scene cutover`, base `main`) is open. The `story-scene-idea` worktree is
Agent Manager-managed — left alone; its branch is fully merged upward so no second PR is needed.
T1–T26 done and committed; T27 assessed (T27b blocked by design, T27a core pre-exists via
onboarding's recipe commit). Commit-tool push/pr extension is folded into the PR branch;
**its originals in the main checkout are intentionally uncommitted** (that checkout sits on
another stream's `features/derived-stat-extension` branch — committing there would pollute it).

**To push (owner, from mobile or terminal):** the branch is currently in sync; after any new
commit run `git push origin worktree-rift-gate-20260914` (from the rift worktree) — or, once a
fresh session picks up the MCP tools post-restart, just say "push and update the PR".

**Tests deferred to later (owner: "other test will be do later"):** scoped suites all green at
handoff; the full default profile (`test-fast.ps1 -AllDefault`, run 2026-09-16 pre-probe) gives
13591/13592 with ONE failure outside this program's blast radius —
`DungeonLootTableSeedFileTests` byte-identity, a Windows-newline artifact (file and blob are both
LF-pure; the generator emits `Environment.NewLine`, so Windows red / Linux CI green). Untouched
area (`gk-data/packs/fusion/data/seed/loot`, committed by others); fixing the generator is the loot program's one-liner,
not taken here. Deploy proceeds on the scoped green plus 13591.
- T24 visual-eyeball box (radial label / shield meta / dev panel post-tier-removal; construction-proof
  recorded, photograph pending): re-run `npx vitest run src/shell/bandGuard.test.ts` + eyeball the lawn HUD.
- `first-session` suite (owning program's fence — no such tests exist in this tree).
- T27 live proof: `scripts/prove-vfx.ps1` rift case + four cues visibly reaching the game (needs the
  running game; game dir default `H:\Games\PVZ-Fusion-3.9_MelonLoader` exists, env var unset).
- Full unfiltered suite (`test-fast.ps1 -AllDefault` / CI) — scoped evidence only so far.
- Commit-tool `smoke_test.py` from a real terminal (agent shells cannot execute that path).

**Pending decisions (yours):** tooling-original placement (own branch vs fold vs drop); rift-gate
checkbox debt (134 unticked vs "complete" header — needs its own game-env pass); T12–T14 closure
(onboarding program / owner); build-phase session record for `verify-change.ps1`; PR review/merge;
saved memory still says push is owner-only (update to explicit-ask if wanted).

# Story scene — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-18)
>
> **This document's status line is not current, and it is the kind of wrong that costs a whole
> session.** Measured today: **map approved 2026-09-15 (owner)**, **21 module specs** under `docs/architecture/story-scene/`, and a task list at **47 done**.
>
> A status line reading *"no build authorized"* over a program that has already shipped invites
> the next session to re-derive work that exists — and its inventory of gaps is stale in the same
> direction, because a gap named before the build is usually closed by it. **Read this document
> for its reasoning and its decisions; never for its status, its gap list, or its counts.**
> Verify anything load-bearing against the capability map, the task list, and the code.

**Status:** idea phase (idea-UI), 2026-09-15. Revised after an evidence audit and **all five owner
questions answered the same day** (see Owner decisions). **Not a spec.** No build authorized. This
document stops at shape + settled decisions; `/spec` is the next phase and writes the first spec,
plan, and todo.
**Program id:** `story-scene` (a reusable web-FE presentation sub-program; first consumer is the
Rift prologue).
**Procedure:** produced under [idea-ui-phase.md](idea-ui-phase.md) (`/idea-ui`) — module-first
presentation composition, not generic system `/idea`.
**Sibling programs this must not fork:** [rift-gate-ideal.md](rift-gate-ideal.md) owns the **Rift
Gate** mechanism (overlay transport, host selection, first-open capture);
[standalone/spec-first-session-progression.md](standalone/spec-first-session-progression.md) owns
the **first-session reveal sequence** (the three checkpoints). This doc edits neither.
**Consumer under audit:** `gk-web/web/fusion-rpg-web/src/features/onboarding/RiftPrologueDialog.tsx`
(the four-beat Rift prologue).

> **Revision note (2026-09-15, second pass).** The first draft of this doc was written before the
> shell guards, the first-session reveal surface, and the existing honest-stand-in pieces were read.
> That made three claims wrong: it called the labelled shape a *real gap* when the house pattern
> already exists (`ActorFrame`, `RungStateFallback`, `CatalogIcon`); it assigned **every** number to
> `gk-core/data/tuning` when structural draw caps have their own FE home
> (`lawnPresentationTokens.ts`); and it missed `OnboardingReveal` / `FirstRunReveal` — a live
> reveal sequence with its own owning spec. It also missed that **three shell band guards are red on
> HEAD**, two of them caused by this consumer. Corrections are marked **[corrected]**.
>
> **Third pass (same day): owner answers.** Q1 → extend `DialogShell` with a `size` contract (the
> `PanelShell` `actorSheet` precedent), not a new band; Q2 → **two actors**, the genre floor; Q3 →
> the web FE owns the cue, and **my question was over-framed** — corrected below; Q4 → **shared**
> pieces, because in the genre a reveal is a one-beat scene; Q5 → skip always available. The
> decisions table is the record.

---

## Which loop/place this extends

Named from `docs/guide/the-loops.md` (three clocks, a spine, seven places):

| Loop / place | Role |
|---|---|
| **Places §1 — Lawn, first core** (`the-loops.md:63`) | The scene plays *before* the first lawn; the lawn is where it hands the player off |
| **First session — the designed cold start (GG-43)** | The scene is the authored opening: what the player sees first is scripted, not the normal interface with everything empty |
| **Sanctum stage, dialog layer** | The prologue mounts inside `SanctumStage`; a scene is a layer over the stage the player already stands on, not a route |

This is **not an eleventh loop** — it applies `the-loops.md`'s own rule ("combat depth hangs on
places, not an eleventh loop") to narrative presentation: a scene **hangs on** the first-session and
lawn moments. It is also **not a new top-level route** — the sibling first-session spec says the same
for its reveals: *"The FE renders a single current reveal over the current stage (Sanctum or the
settled run result), never a new top-level route"* (`spec-first-session-progression.md:139-141`).

It is how the *narrative presentation surface* is authored as composable modules so an illustrated,
beat-by-beat scene stops being one fragile React host with hand-written CSS, and so later scenes (a
second story, a character reveal, a mid-run transmission) reuse the same pieces instead of forking a
second dialog.

---

## Load-bearing principles (restated inline)

1. **Every RPG feature lives in the RPG layer.** A story scene is RPG narrative presentation.
   Speaker, line, beat order, and outcome are RPG/server state; they are never gated on a
   Plant/Zombie Unity field. "The Injector cannot host this" is not a reason a scene cannot exist.
2. **A game is a stage with layers, not a document with pages (GG-1).** A scene is a layer over the
   current stage, declared in the band system — never a `/story` route. GG-11 makes it harder still:
   *"Opening a layer never destroys the stage"* — the scene must not unmount what is beneath it.
3. **Player menus are recipe + pure fold + closed bus — never a god TSX.** A page component owning
   layout, paint, data joins, and copy is the defect this phase exists to catch. Every bug in this
   doc is **one or more modules** (piece + optional theme pack + fold slice + draft HTML), not one
   CSS pass.
4. **Theme packs own paint.** Pieces declare slots; a pack supplies `css` custom properties and
   resolved `paint` hex. A hard-coded purple for the Rift or a hard-coded green for a speaker name is
   a Lego violation, not a style preference.
5. **Buy before build.** Prefer a locked library or an existing kit piece over hand-rolling motion,
   icons, or layout. A fat entry chunk is a code-splitting failure — split the chunk; never ban the
   library. (Audit note: `motion` is installed and **currently unused anywhere** — see Wiring gaps.)
6. **Each bug = one or more modules.** Shared piece first, surface recipe second, polish third. A
   surface that owns everything is the failure, not the fix.
7. **No engine vocabulary on the player surface.** No `typeId`, `instanceId`, `cueId`, `VfxCatalog`,
   `storyId`, `.md` paths, or author notes in anything the player reads. Fiction labels only. This is
   **already broken in shared kit pieces the scene would compose** — see Wiring gaps.
8. **The web FE is not named after a mechanism.** "Rift" is a story and (later) a mechanism word; it
   is reserved and must not become the name of this presentation system. The program id is
   `story-scene`.
9. **An honest placeholder beats a blank square.** Missing art renders a **labelled shape** that says
   what is missing and carries the actor's name — never a broken-image glyph, never an empty box,
   never an unlabelled generic body. The house already has three variants of this pattern; the defect
   is that none of them carries an actor's *name*.
10. **Buy in is deliberate; a scene is skippable and durable.** A story the player has seen is
    dismissible, and skipping writes the same terminal state as watching it (GG-52), so a skip can
    never soft-lock progression.
11. **Structural limits, bounded ratios, and closed registries are exempt from "never clamp"** and
    must say why in a comment. A scene's draw caps and box sizes are structural — but see Tunables:
    they still have a declared home, and it is not a bare literal.

---

## What this is (player language)

A **story scene** is a short, illustrated, beat-by-beat narrative the game plays to you: a speaker,
a line, art behind them, and a cue that says what the moment feels like. You read one beat, advance,
read the next. You can skip a scene you have already seen. When the scene ends you are back where you
were — usually on the lawn, about to start.

The **first** such scene is the Rift prologue: four beats, two speakers (Crazy Dave and Penny), and a
quarantine signal, shown once before the player's first lawn. But the prologue is the *first
consumer*, not the design target: the same pieces must play a later story, a character reveal, or a
mid-run transmission without a second dialog being written from scratch.

---

## Debate — is this the right shape? (what holds, what I would overturn)

**What holds.** The module decomposition is right and the audit strengthened it: the pieces a scene
needs (stage, actor slot, sprite+fallback, window, name tag, advance, progress, cue seam) are exactly
the ones no shared piece covers today, and the mechanism to compose them (piece registry +
`bindSurface` + theme packs) already exists. The "reusable, not a one-off" decision is well-founded:
`RiftPrologueDialog` is a 193-line component with six independent state concerns and zero extracted
pieces, so a second scene today means a second god TSX.

**The strongest counter-argument — and it is real.** A scene is **not** a menu. Every existing Lego
surface (`derived-console`, `condition-console`, `shield-console`, `aptitudes-console`) is an
ActorSheet tab or a band-2 panel; none is full-bleed stage presentation. Forcing a scene through the
menu recipe grammar risks inheriting menu constraints (bounded panel width, dock/inspect split) that
a scene actively does not want. **The answer is not to fork the grammar** — it is to keep the
registries, slots, theme packs, and fold, and to **reject the menu's host contract**: a scene stays a
band-3 shell layer whose geometry the shell declares for it (`size`), not a menu panel. The owner
settled both consequences of this: the band/geometry question (decision 1) and cast size
(decision 2).

**What I would overturn from my own first pass.**
- **[corrected] The labelled shape is not a real gap.** `ActorFrame` (`ui/actor/shared.tsx:22`) already
draws an honest initialed disc, `RungStateFallback` (`ui/actor/RungStateFallback.tsx:10`) draws
  loading/empty/error/locked stand-ins, and `CatalogIcon` (`ui/actor/CatalogIcon.tsx:104`) draws a
  generated token-glyph fallback. Inventing a fourth stand-in would be the mistake. The real gap is
  narrower: **no existing variant is labelled with a person's name and none is free of the
  plant/zombie side axis** — Penny and Dave are neither. Extend the house pattern; do not create one.
- **[corrected] Not every number belongs in `gk-core/data/tuning`.** The tree has two legitimate FE homes
  (see Tunables): structural draw caps live in a FE tokens module with a why-not-tunable comment
  (`ui/lawn/lawnPresentationTokens.ts:1-24`), and feel/pacing lives in
  `gk-core/data/tuning/<domain>-ui.v1.json` (`gk-core/data/tuning/delve-ui.v1.json`). Assigning all of it to
  `gk-core/data/tuning` would have been a new, wrong rule.
- **[corrected] A scene must not become a second reveal grammar.** `OnboardingReveal` and
  `spec-first-session-progression.md` already own an "one current reveal over the current stage"
  sequence with checkpoint semantics. The scene's `advance-control` and `scene-progress` are the same
  family; the spec must decide whether they are shared or deliberately distinct.

**What is the real question here?** Not feasibility — the answers are settled (see Owner decisions).
The real question was **shape**: which geometry a scene occupies inside band 3, how many actors stand
on stage, and whether the scene's cue is driven by the FE or the Unity side. All three are answered;
what remains for `/spec` is the structural detail (the exact scene bound, the narrow-breakpoint
collapse rule, and the asset-role contract for N actors).

---

## What already exists — four buckets
> ### ⚠️ The code this survey describes has been replaced (checked 2026-09-18)
>
> Every `RiftPrologueDialog.tsx:<line>` and `riftAssets.ts:<line>` citation in this document points
> into code that the **S6 cutover removed on 2026-09-16** (`00b1f2aa9`):
>
> | Cited | Then | Now |
> |---|---|---|
> | `features/onboarding/RiftPrologueDialog.tsx` | 203 lines | **39 lines** — its own header says everything moved out |
> | `features/onboarding/riftAssets.ts` | the asset table | **deleted** |
> | `features/onboarding/rift.css` | 12 cited sites | **deleted** |
>
> **Successor: `gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx`** (264 lines).
>
> These citations are **kept, not repointed.** Re-pointing twenty-five of them would mean inventing
> twenty-five line numbers in a file none of them was written against — manufacturing exactly the
> false precision that made this document unreliable in the first place. What they are is an accurate
> survey of the code **as it stood on 2026-09-15**, which is worth keeping and is why the design came
> out the way it did. What they are not is a statement about the code today. The
> `citations-historical` markers below say so to `scripts/audit-doc-citations.py` as well as to you.
>
> Two further findings from the same check, both about this document's authority rather than its
> citations:
>
> - **All twelve rows of the “Real gap” table are built**, including the tuning file —
>   `gk-core/data/tuning/story-scene-ui.v1.json` carries exactly the four keys this document proposes.
> - **The shipped code overturns this document's own owner-approved Decision 17.**
>   `ThemeKind` is not *"closed with no actor or scene kind"*; `features/gui-lego/types.ts:17-49`
>   has **14** members including `"actor"` and `"scene"`, both stamped *"story-scene S2,
>   2026-09-15"*. The cited SSOT for that claim, `gui-lego/payload-types.md`, does not exist.

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

### Built (works end to end today)

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

| Capability | Proof |
|---|---|
| Four-beat prologue with speaker / line / teaching / cue | `features/onboarding/RiftPrologueDialog.tsx:19-44` — `const BEATS: readonly Beat[]` |
| Beat advance with a double-click guard and terminal finish | `RiftPrologueDialog.tsx:122-127` |
| Durable acknowledgement of completed *or* skipped, with retry and a lawn bypass | `RiftPrologueDialog.tsx:101-120`; `lib/bus/onboarding.ts:59-66` |
| Server story ledger (per player, version, state, outcome, revision) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs:51-88` |
| Story ack endpoint | `gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:35-40` |
| Story eligibility gate into the Sanctum stage | `stages/sanctum/SanctumStage.tsx:85-89` |
| Semantic cue seam (prop; safe when absent) | `RiftPrologueDialog.tsx:59-60`, emitted `:90-94` |
| Versioned, filename-independent asset roles | `features/onboarding/riftAssets.ts:11-26` |
| Missing art does not show a broken glyph | `RiftPrologueDialog.tsx:170-182`, `role="img"` fallback `:171` |
| Band-3 dialog shell: layer push/pop, focus return, Esc suppression | `shell/DialogShell.tsx:36-40`, `:57-66` |
| Progress indicator with accessible label | `RiftPrologueDialog.tsx:167` |
| Polite live region for the changing line | `RiftPrologueDialog.tsx:184` |
| Reduced-motion handling for the scene chrome | `features/onboarding/rift.css:89-94` |
| Four VFX recipes exist as Core data | `gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs:65-68`, `:442,466,490,514` |
| **Layer host + stage-survival guard (GG-11)** | `shell/stageHost.tsx:12-19` (`useStageMountGuard`), `:32-38` (`StageHost`, band 0); every stage calls it (`SanctumStage.tsx:71` and four siblings) |
| **Band system as tokens, not ad-hoc z-index** | `src/theme/tokens.css:101-107` — `--band-stage:0 … --band-system:500`; seven `.band-*` utilities `:122-128` |
| **Real-tree guards that police the band contract** | `shell/bandGuard.ts:52-56` (stray z-index), `:72-80` (layerStack imports), `:94-134` (band-3 allowlist) with `shell/bandGuard.test.ts:10-21` |
| **Shell must not branch on stage id** | `shell/noStageSpecificBranch.test.ts` — a source scan of `src/shell/` per stage id |
| **A sibling reveal sequence already shipped** | `stages/sanctum/OnboardingReveal.tsx:11-45`; owning spec `standalone/spec-first-session-progression.md:126-147` — implemented |
| **An honest stand-in already exists for actor art** | `ui/actor/shared.tsx:22-53` (`ActorFrame` initialed disc), `ui/actor/RungStateFallback.tsx:10-59`, `ui/actor/CatalogIcon.tsx:104-117` (GG-58 generated glyph) |
| **Queue/cap + auto-expiry precedent for a reveal stack** | `shell/toastStack.ts:29,38-44`; `shell/Toasts.tsx:13` (`VISIBLE_CAP = 3`) |

### Wiring gap (exists but inert/bypassed — **not a wall**)

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

| Finding | Inert line | Why it is not a wall |
|---|---|---|
| The four Rift cues are never produced. Recipes sit in `CreateAll` with no producer. | `VfxCatalog.cs:442`; `RiftPortal*`/`RiftQuarantine*` appear **only** in `VfxCatalog.cs` | `VfxDirector.Play(VfxCueDto)` exists and already degrades on a missing anchor (`gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs:65-73`, `:207-223`). A producer + a `prove_vfx.py` case closes it. |
| The `onCue` seam is declared and unit-tested; the only caller is the test, and the real mount omits it. | `RiftPrologueDialog.tsx:90-94` emits; `RiftPrologueDialog.test.tsx:26` is the only `onCue=` site; `SanctumStage.tsx:260-265` passes **no** `onCue` | The seam shape is right (a semantic id, not a Unity handle). It needs one host consumer. |
| `VfxDirector` has **zero** Rift handling. | `gk-fusion/src/FusionRpg.Injector/Fx/VfxDirector.cs` — no `rift` match | Correct layering: the director resolves a `VfxCueDto`, not a story. The story must not teach it what a prologue is. |
| `prove_vfx.py` has no Rift case. | `scripts/prove_vfx.py:369` is an unrelated "drift" substring | Proof coverage is additive; the script already exits non-zero on failure (`:378`). |
| The `icon` asset role is declared with no consumer. | `riftAssets.ts:18-23` | Deliberate: plan Task 20 acceptance says "Icon is not wired into combat HUD chrome" (`tasks/onboarding-rift-todo.md:425`). |
| **`motion` is installed and never imported.** The tree hand-rolls CSS transitions instead. | `gk-web/web/fusion-rpg-web/package.json` lists `motion ^13.2.0`; `grep "motion/react"` over `src` returns **zero** matches | Buy-before-build is satisfied but unused. A scene's transitions are the natural first consumer; if CSS proves sufficient, say so rather than leaving the dependency unexamined. |
| **An honest stand-in exists but is not composed for a named actor.** | `ui/actor/shared.tsx:22` `ActorFrame` draws an initial but has no name; it is tinted by `side === "plant"` / `"zombie"` (`:45-46`) | The pattern is there to extend; nothing needs to be invented. |
| **[corrected] Dev vocabulary already leaks on a shared piece a scene would compose.** `phase-*` renders its own class name as player-visible text. | `ui/gui-lego/pieces/lifecycle.tsx:10-11` — `<strong>{`phase-${kind}`}</strong>` | A one-line piece fix; it is a wiring gap on an existing piece, not a reason to avoid the lifecycle piece. |
| **[corrected, fixed 2026-09-23] Dev footer copy is a default, not a payload.** | `ui/gui-lego/pieces/chrome.tsx:153,157` — the two defaults `"expand×join · UnitClass closed"`, `"Deferred in FE v1: live build compare · full xyflow calc graph"`; source of truth `features/gui-lego/foldDerivedSurfaceVm.ts:463-464` | The piece already accepts `payload.note` / `payload.deferred`; the defect is the **default**. Fix the default; do not rewrite the piece. **Done:** both defaults are gone, so absent means absent — the caller states its own line, and no other recipe binding `surface-foot` inherits the derived console's engine wording. The live producer is untouched (one live consumer: `derived-console.json` ← `foldDerivedSurfaceVm.ts:458-465`), its rendering is byte-identical, and `ui/gui-lego/pieces/chrome.foot.test.tsx` pins both halves plus a source scan. Residual, not fixed here: the piece's own `"Hidden unchanged:"` label is still a literal — it is the approved draft's copy on a developer console (`docs/design/derived-combat-console.html:572`) and localizing it is that surface's contract change, not a default fix |
| **No shared piece exists for a scene stage, and the recipe catalog is menus only.** | `docs/design/gui-lego/recipes/` holds `aptitude-preset-console`, `aptitudes-console`, `condition-console`, `derived-console`, `shield-console`; runtime mirror `src/ui/gui-lego/recipes/` | The *mechanism* exists (`features/gui-lego/{pieceRegistry,recipeRegistry,bindSurface}.ts`, `ui/gui-lego/RecipeMount.tsx`). This is missing content, not missing infrastructure. |

### Real gap (no shareable piece / pack yet)

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

| Gap | Evidence |
|---|---|
| No **scene stage** piece (full-bleed art bed + cue state) | The bed is prologue-scoped CSS: `rift.css:1-56` — `.rift-prologue-scene`, `.rift-prologue-art` |
| No **dialogue window** piece | Inline markup: `RiftPrologueDialog.tsx:184-188` |
| No **name tag** piece | Inline: `RiftPrologueDialog.tsx:185` |
| No **actor / portrait slot** piece | `Beat` has `speaker: string` only (`RiftPrologueDialog.tsx:9-15`); there is no actor concept |
| No **labelled-shape-by-name** component | The existing fallbacks (`ActorFrame`, `RungStateFallback`, `CatalogIcon`) carry an initial, a state word, or a token — **never a person's name**; the fallback is one generic `◈` + one manifest string (`RiftPrologueDialog.tsx:170-174`) |
| No **advance control** piece | Raw footer fragment: `RiftPrologueDialog.tsx:137-157` |
| No **cue seam** piece / binder | `data-cue` is a CSS attribute selector (`rift.css:32-44`), not a piece contract |
| No **progress indicator** piece | Inline span: `RiftPrologueDialog.tsx:167` |
| No story/scene **theme pack** | The closed `ThemeKind` union is `element \| status-category \| resource \| action-category \| rarity \| side \| cook-tab \| bucket \| posture \| neutral` (`gui-lego/payload-types.md:35-46`) — no actor or scene kind — and `themes/packs/` holds only those kinds (40 packs) |
| No story/scene **recipe** | See the recipe catalog above |
| No **scene script** source | The four beats are a `const` in a component (`RiftPrologueDialog.tsx:19-44`), so scene 2 means editing a TSX |
| No **scene timing / art aspect / fallback size** tuning file | No `data/tuning/story-scene*.json`; the art box is inline CSS (`rift.css:46-55`) |

### Built, defective (present but wrong)

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

| Defect | Location | Wrong because |
|---|---|---|
| **[corrected — new, highest severity] Three shell band guards are red on HEAD, and two are this consumer's.** | `shell/bandGuard.test.ts:11,15,19` fail. Violations include `features/onboarding/rift.css:48,59` (`z-index: 1`), `features/onboarding/RiftPrologueDialog.tsx:130` (`<DialogShell` outside the band-3 allowlist), plus pre-existing `dev/PhaserSceneSwitchPocPage.tsx:284`, `ui/gui-lego/conditionConsole.css:229`, `ui/gui-lego/shieldConsole.css:100`, and `stages/world/mapChromeMute.ts:5-6` | A scene must use the seven `.band-*` utilities — never its own `z-index` — and a non-`shell/` surface that renders `DialogShell` is **unvetted band-3** by construction (`bandGuard.ts:94`). The allowlist is a closed registry with per-entry justification (`:96-134`), and `stages/lawn/` is a **dev-surface** exemption (`:149`) that `stages/sanctum/` does **not** get. Verified by running `npx vitest run src/shell/bandGuard.test.ts` in the main checkout (same blobs; `bandGuard.test.ts` was added 2026-08-24, the Rift prologue landed 2026-09-15). I could not run CI to confirm the red build. **This means the prologue shipped without the band guard being satisfied — a real, checkable contract breach, not a style question.** |
| One placeholder for every actor; `◈` says nothing about *who* is missing | `RiftPrologueDialog.tsx:170-174` | Decision 2 requires an honest labelled shape carrying the actor's name. All actors share `RIFT_ASSETS.storySprite.fallbackLabel` ("Rift visual unavailable"), so two missing actors are indistinguishable. |
| Speaker color is hard-coded, not pack-owned | `RiftPrologueDialog.tsx:185` — `text-ok` | Speaker identity is paint. A second scene with a different cast cannot be themed; this is the "hard-coded muted chip" violation idea-ui names. |
| Scene art is one manifest role, not per-actor | `riftAssets.ts:11-17` | A scene with Penny *and* Dave needs two sprites; the manifest models one `storySprite`. Actor is not a concept. |
| The `Beat` type mixes presentation, pedagogy, and cue | `RiftPrologueDialog.tsx:9-15` — `teaching`, `cue`, `seal?` | `teaching` is a first-user-guide concern and `cue`/`seal` are stage concerns; coupling them means a scene cannot vary one without the others. |
| A full-screen illustrated scene sits on a band-3 **bounded** dialog | `DialogShell.tsx:67-71` — `w-[min(440px,92vw)]`, `max-h-[min(720px,82vh)]`; contract `:17-21` | The shell's own comment says band-3 is "a decision, not a browsing surface". A scene needs geometry the shell refuses to give it; today the prologue is a 440px card. |
| Six concerns in one component, no fold | `RiftPrologueDialog.tsx:62-68` — `beatIndex`, `busyRef`, `finishedRef`, `advanceGuardRef`, `ackError`, `assetMissing` | The god-TSX shape in miniature: reusable pieces cannot be extracted while state lives here. |
| `Rift` naming is baked into the surface, its CSS, and its files | `rift.css`, `RiftPrologueDialog.tsx`, `RiftPrologueDialogCueId` | The prologue *is* a Rift story, so its own name is fine; the **system** must be `story-scene`. Watch that extraction does not rename the mechanism into the surface. |
| Reduced motion covers the bed only, not the beat transition | `rift.css:89-94` stops `::before`/`::after` animation only | Beat change and any sprite swap still animate. The rule must cover transitions (GG-32 analogue). |

---

## Bug → module table (existing defects → module owner)

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

| # | Defect | Bucket | Module(s) that own the fix |
|---|---|---|---|
| 1 | Band guards red: `rift.css:48,59` stray `z-index`; `RiftPrologueDialog.tsx:130` unvetted band-3 | Built, defective | `scene-stage` (band utilities only) + a **band-compliance** entry in the spec; if the scene stays band-3 it must be added to `bandGuard.ts`'s allowlist with justification, and `bandGuard.test.ts` is the proof |
| 2 | One generic placeholder per actor (`:170-174`) | Built, defective | `actor-sprite` + `actor.penny` / `actor.dave` packs; extend `ActorFrame`/`RungStateFallback`, do not invent a fourth stand-in |
| 3 | Speaker paint hard-coded `text-ok` (`:185`) | Built, defective | `name-tag` + scene/actor packs |
| 4 | Scene art is one role, not per-actor (`riftAssets.ts:11-17`) | Built, defective | `actor-sprite` + asset-role contract (spec) |
| 5 | `Beat` couples presentation + teaching + cue (`:9-15`) | Built, defective | `scene-script` (data) + `cue-seam` |
| 6 | Full-bleed scene on a 440px bounded dialog (`DialogShell.tsx:67-71`) | Built, defective | `DialogShell` `size:"scene"` (decision 1) + `scene-stage` |
| 7 | Six concerns in one component, no fold (`:62-68`) | Built, defective | `scene-stage` + a `story-scene` fold slice; pieces read payload |
| 8 | Rift cues never produced (`VfxCatalog.cs:442` ff.) | Wiring gap | `cue-seam` producer + injector wiring (sibling transport) |
| 9 | Reduced motion misses transition (`rift.css:89-94`) | Built, defective | `advance-control` / `scene-stage` motion tokens (tuning + pack) |
| 10 | `onCue` never consumed by the real mount (`SanctumStage.tsx:260-265`) | Wiring gap | `cue-seam` host consumer |
| 11 | `phase-*` renders its class name as text (`lifecycle.tsx:10-11`) | Wiring gap | lifecycle piece (shared kit) — a **pre-existing** defect the scene would inherit |
| 12 | Dev footer copy shipped as defaults (`chrome.tsx:153,157`) | Wiring gap | `surface-foot` piece (shared kit) — **pre-existing.** **Fixed 2026-09-23** (see the corrected row above): the defaults are gone, so no surface inherits the derived console's wording; the piece renders only what the caller passes |
| 13 | `motion` installed, unused | Wiring gap | `scene-stage`/`advance-control` become the first consumer, or the dependency is explicitly declined |

**Note on scope:** #11 and #12 are shared-kit defects **not caused by this program**. They are listed
because a scene composes those pieces and would inherit them, and because fixing a shared piece is the
idea-ui rule ("shared piece before surface CSS"). They should be fixed on their own increment.

### Reuse map (shared with other surfaces)

| Piece | Other surfaces it should serve |
|---|---|
| `dialogue-window` | `OnboardingReveal` copy block, guide callouts, a later NPC conversation, contract briefing |
| `name-tag` | Anything labelling a speaker (guide callouts, `OnboardingReveal`'s "New milestone" eyebrow) |
| `actor-sprite` (+ labelled shape) | `ActorFrame` consumers (`ActorToken`, `ActorChip`, `ActorRow`, `ActorCard`), ActorSheet identity, Almanac |
| `advance-control` | `OnboardingReveal`'s "Got it", `Pager` (`ui/Pager.tsx:7-53`), reward sequences (GG-52) |
| `scene-progress` | `OnboardingReveal` queue position, `Pager` label, stepped/reveal family |
| `cue-seam` | Any story moment that asks for a semantic cue; **FE-local today** (decision 3), the Unity channel is a later increment |
| `scene-stage` | Later scenes; possibly the Rift Gate's first-open presentation (sibling program, not decided here) |
| *(new)* `reveal-sequence` fold | The sibling checkpoint sequence — **decision 4: shared, adopted by `OnboardingReveal` in a later increment** |

---

## The shape — module-first piece breakdown

A **surface** is `recipe + fold + bus` (`gui-lego/spec-composition.md:25`). The story scene is a
**stage layer**, so its host is the stage layer stack, not `ActorPanel`. Pieces still follow Lego:
named `pieceId`, declared slots, theme packs for paint. **Rejected:** a menu recipe's panel geometry.

### Recipe

`docs/design/gui-lego/recipes/story-scene.json` (design SSOT; runtime home decided at implementation)

```
surfaceId: "story-scene"
host: "band-3 DialogShell with size:\"scene\""   // decision 1 — same band, scene geometry
root: scene-stage
  slots:
    actors[]      -> actor-portrait        // decision 2 — array, two actors side by side is the floor
      actor.body  -> actor-sprite
    window        -> dialogue-window
      nameTag     -> name-tag
    advance       -> advance-control
    progress      -> scene-progress
```

### Pieces (each a Lego module; what it owns)

| Module id | Bucket | Owns | Slots | First consumer |
|---|---|---|---|---|
| `scene-stage` | Real gap | The full-bleed art bed, layer ordering, band utilities, and the `data-cue` state the whole scene reads. **Does not own actor identity or copy.** | `actors`, `window`, `advance`, `progress` | Rift prologue |
| `actor-portrait` | Real gap | **One actor in a slot array** (decision 2) plus its `speaking \| inactive` state (the Dialogic highlight analogue). Resolves actor → sprite + variant; owns the fallback decision. | `body` (`actor-sprite`) | Rift prologue (Penny, Dave) |
| `actor-sprite` | Real gap (extends an existing pattern) | The image **plus the honest labelled shape** when sprite/variant is missing. Carries the actor's name + initial + pack accent. **Should wrap/extend `ActorFrame`, not replace it.** | none (leaf) | Every scene with a cast |
| `dialogue-window` | Real gap | The say window: line, teaching line, narration variant (no speaker). Owns readability rules, not color. | `nameTag` | Rift prologue |
| `name-tag` | Real gap | The speaker label + its pack-owned paint. Absent on a narration beat. | none | Every spoken beat |
| `advance-control` | Real gap | Next / final-label / skip and their disabled-pending state. One piece, both verbs; **skip always present** (decision 5). | none | Every scene |
| `scene-progress` | Real gap | Beat `n of m`, its accessible label, and pips. | none | Every scene |
| `cue-seam` | **Named seam, not a v1 work item** (decision 3) | The semantic cue id. The FE already owns and renders it (`data-cue`); the Unity-side `rift.*` recipes are a later additive increment owned by whoever owns the host bridge. | none | Rift prologue (FE-local today) |
| `scene-script` | Real gap | The **data**: ordered beats `{ speakerId, variant?, line, teaching?, cueId? }`. Not a piece — a fold input / contract type. | n/a | Every scene |
| *(shell)* `DialogShell size` | Built, extend | A `size?: "default" \| "scene"` contract on the existing shell (decision 1), mirroring `PanelShell`'s `size?: "default" \| "actorSheet"`. Not a new piece. | n/a | Rift prologue; any future scene |

### Theme packs vs recipes vs tuning — the line

| Concern | Home | Why |
|---|---|---|
| Piece structure, slot names, bind paths | **Recipe** (`story-scene.json`) | A recipe that embeds hex is banned (`spec-composition.md` anti-patterns) |
| Scene mood (portal/violet, quarantine/steel, calm/soil), actor identity paint | **Theme pack** (`themes/packs/scene-*.json`, `actor.penny`, `actor.dave`) | Paint is identity; the same markup must render any scene |
| Beat copy, cue ids, beat order | **Script data** (`scene-script`) | Content, versioned like a runtime catalog |
| Beat/transition timing, auto-advance dwell | **`gk-core/data/tuning/story-scene-ui.v1.json`** | Feel/pacing — the `delve-ui.v1.json` precedent |
| Art box cap, fallback box size, draw caps | **FE tokens module** (`src/ui/story-scene/storySceneTokens.ts`) | Structural, like `lawnPresentationTokens.ts` |
| Type scale | **Pack `css`** custom properties + kit tokens | Readability ladder belongs to paint |
| Cue → effect mapping | `VfxCatalog` (exists) | **Not** a story number |

### Alternatives rejected

| Alternative | Rejected because |
|---|---|
| Keep one `RiftPrologueDialog`, add scene 2 inside it | Forks the god TSX; "reusable, not a one-off" is the owner's first decision |
| Adopt ink/Yarn Spinner now | Solves branching we do not have; adds a compiler and build step. Revisit when a scene branches |
| Build the scene on `DialogShell` **unchanged** | Correct for the band, wrong for the geometry: the fixed `440px` card (`DialogShell.tsx:68`) cannot hold an illustration. **Decision 1 extends the shell with a `size` contract** instead of bypassing it |
| A dedicated layer that "owns the stage" while a scene plays | Needs a GG-5 amendment (eighth band) **and** violates GG-4 — *"Layers never cause a stage change as a side effect"* |
| A second `SceneShell` | Two shells maintaining the same two jobs (`DialogShell` already does layer push/pop + focus return). Genre prior art has one say screen on a layer, not a new layer class |
| Cut to one actor on stage | A cast is the genre floor (Ren'Py `show`/`hide`, Dialogic multi-portrait). Owner decision 2: two side by side |
| Build an injector-side story state machine for cues | Owner decision 3: the scene is a web-FE feature. The FE owns the beats and already renders `data-cue`; there is no injector "story" to own |
| Invent a fourth honest stand-in | `ActorFrame` / `RungStateFallback` / `CatalogIcon` already exist; extend the house pattern |
| A separate "reveal" grammar for `OnboardingReveal` | Owner decision 4: the genre has one dialogue viewport for dialogue, narration, and one-shot messages. A reveal is a one-beat scene |
| A first-scene nudge before skip is allowed | Owner decision 5 + GG-52 + the narrative source's own `:33` — skip never loses content |
| A scene **route** (`/story/rift`) | GG-1 is stage + layers; the sibling spec says "never a new top-level route" for the same family |
| Rename pieces `rift-*` | "Rift" is reserved; the system is `story-scene` |
| Put beat copy in a TSX `const` | Scene 2 must not require a code edit |
| Skip the band allowlist and ship anyway | That is what HEAD did; `bandGuard.test.ts` is red and CI's `npm test` step is a hard gate (`gk-core/.github/workflows/ci.yml:683-689`) |

---

## Tunables

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

**A balance number never lives as a `const`, and the balance surface is data**
(`gk-core/data/tuning/<domain>.v{n}.json`; rule T1, `docs/architecture/tunables-ssot.md:93`). A piece that
hard-codes a balance number is defective.

**[corrected]** Presentation numbers have **three** legitimate homes in this tree, and picking the
wrong one is itself a defect:

| Number | Meaning | Home |
|---|---|---|
| Beat enter/exit duration | Cross-fade length | `gk-core/data/tuning/story-scene-ui.v1.json` (`beatTransitionMs`) |
| Auto-advance dwell (if ever) | Dwell before advancing — **absent by default** | same (`autoAdvanceMs`, nullable) |
| Line reveal speed | Per-character reveal, if used | same (`lineRevealPerCharMs`) |
| Scene shell bound | The `size:"scene"` box (`h-[min(…)] w-[min(…)`) | `DialogShell`'s own className, **beside `PanelShell`'s `actorSheet`** bound (`PanelShell.tsx:97-99`) — the shell owns its bound, and it is not a balance number |
| Art box cap / aspect | Bed ratio and max height | `src/ui/story-scene/storySceneTokens.ts` (structural, with a why-not-tunable comment) |
| Fallback shape size | Labelled-shape box + initial scale | same (structural), tint from the pack |
| Narrow-breakpoint actor layout | The 320px collapse rule (decision 2) | `storySceneTokens.ts` (structural) — this is the new cost of two actors |
| Per-scene beat cap | Guards against text walls | `story-scene-ui.v1.json` (`maxBeatsPerScene`) — a pacing choice, so tunable |
| Type scale (speaker / line / teaching) | Readability ladder | pack `css` custom properties + `_kit/tokens.css` |
| Touch target min | Advance/skip hit area | kit token, asserted in spec |
| Cue → effect mapping | Which cue plays which recipe | `VfxCatalog` (exists); **not wired for v1** per decision 3 |

Scene **copy** (lines, teaching sentences, speaker names) is neither a tunable nor a pack — it is
`scene-script` content, versioned like a runtime catalog, so a rename never reads as a rebalance
(T7, `tunables-ssot.md:114-118`).

---

## A11y / responsive

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

**Inherited today (keep, and make it a contract):**
- Focus return to the opener on close — `DialogShell.tsx:57-60`.
- Esc owned by the keymap; Radix's own handling suppressed — `DialogShell.tsx:61-66`;
  `keymap.ts:10-18` (Esc dismissible bands: panel, dialog, system).
- Polite live region so a new line is announced — `RiftPrologueDialog.tsx:184`.
- Accessible beat label `Beat n of m` — `RiftPrologueDialog.tsx:167`.
- Enter/Space advance when the body is focused — `RiftPrologueDialog.tsx:159-164`.
- `prefers-reduced-motion` stops the bed animation — `rift.css:89-94`.
- Fallback is `role="img"` with a label — `RiftPrologueDialog.tsx:171`.

**A reusable scene must re-specify (not inherit):**
- **Band compliance.** No `z-index`; no `z-*` class; the seven `.band-*` utilities only. Today the
  prologue fails this (`rift.css:48,59`) and the guard that says so is already red.
- **Full-bleed fits the viewport (S1).** `100dvh`, never `100vh`; the scene body **never scrolls**, and
  the advance control must stay reachable on a short viewport. If something must give, the art bed
  scales down first — an unreachable Skip/Next is a trapped player.
- **Focus order across a cast**: with two actors on stage (decision 2), decide who is focused and
  whether an actor is a focus target at all; recommendation — actors are **not** focus targets, the
  window is, so `Tab` does not walk through decoration.
- **Live-region scope**: today `aria-live` wraps the whole window, so the teaching line re-announces
  every beat. Decide one region per beat vs the line only.
- **Reduced motion for transitions**, not only the bed: beat change and sprite swap become instant.
- **A skippable-scene affordance that is always focusable** on every beat, including the last
  (decision 5) — a contract now, not a preference.
- **No new global keybinding.** Any scene shortcut goes through the keymap verb registry, which
  **forbids F10** — `keymap.ts:18`; F10 is reserved to the host/game. Enter/Space on the focused body
  is the pattern to keep.
- **Contrast on pack paint**: a name tag tinted by `accent`/`onAccent` must be checked against the
  window background per pack, not assumed.
- **Responsive across a cast (decision 2).** `≥720px` side by side; `<720px` **stack speaker-forward**
  with the non-speaking actor still visible (owner S1). Hiding an actor was considered and declined.
- **Localization (S4).** All story text is a lingui message with English as the default locale, and the
  pseudo locale must render **no** English from the window, name tag, progress label, or advance
  control. A hard-coded string is a defect; a bare `t` macro is a defect.

---

## What this deliberately does not decide

- The **Rift Gate** mechanism — owned by [rift-gate-ideal.md](rift-gate-ideal.md) and its session.
- The **first-session reveal sequence** — owned by
  [standalone/spec-first-session-progression.md](standalone/spec-first-session-progression.md).
- **Story arcs, beat scheduling, chapter sequencing** — N3 grants `scene-trigger` an **eligibility
  seam only**; what story happens when is a future program.
- **Dr. Zomboss** as a v1 actor — a story question, deliberately deferred by the owner.
- Whether scenes are **branching** (which would reopen the ink/Yarn question).
- Whether the Injector, the server, or a later mechanism drives a cue; this doc fixes only the seam.
- **Amending GG-61** — S1 records a scoped exemption citing it; changing a GG is an owner/ADR action.
- The **four unrelated band violations** on other surfaces.
- Any change to the four VFX recipes or `prove_vfx.py`.
- Any runtime code, spec, plan, or todo.

---

## Owner decisions (2026-09-15) — all nine resolved

**Nothing blocks `/spec` or `/plan`.** Each answer is folded into the specs; the authoritative record
is [story-scene-map.md](story-scene-map.md) §"Owner decisions". This doc summarises them:

| # | Question | Decision |
|---|---|---|
| 1 | Scene layer band / geometry | Band 3 stays; `DialogShell` gains `size`, and the scene is **full-bleed** with a **scoped GG-61 exemption** (S1) |
| 2 | Cast size in v1 | **Two actors side by side**, stacking speaker-forward at the narrow breakpoint |
| 3 | Cue ownership | **The web FE owns the cue**; the Unity channel is a named, unwired seam |
| 4 | Relationship to the reveal sequence | **Shared pieces**; a reveal is a one-beat scene (later adoption, sibling spec untouched) |
| 5 | Skip semantics | **Always available**, one terminal path |
| S3 | Script home | **Typed TS module** |
| S4 | Localization | **i18n throughout, English default** — all story text through lingui |
| N1 | The red guards | **Fixed in this program** (Wave 0), four lines |
| N2 | Reusable host | **`StorySceneHost` extracted** |
| N3 | Who triggers a scene | **A minimal trigger/eligibility seam** (`scene-trigger`), server-authoritative, no arcs |
| N4 | Owner visual gate | **Required** before `recipe-wire` is done |
| N5 | Invented defaults | **Accepted as starting values** (all in data/tokens) |

### Decision 1 detail — why `size`, not a new band (the "do like other games" answer)

The question asked what other games do, and the genre is clear: **a dialogue scene is a layer, not a
new stage tier.** Ren'Py's own model is explicit — `master` holds backgrounds and sprites, `screens`
holds UI, `transient` holds dialogue widgets, and the *say screen* is a screen shown on a layer; it
is never a new layer class (`renpy reference: "The transient layer is used to display ui widgets,
like windows containing dialogue and menus"`). Foundry VTT models a scene as ordered canvas layers
(background → foreground → templates), not as modes. Unity's dialogue packages put the dialogue on a
`CanvasLayer`/screen-space canvas overlaying the scene. **Nothing in the genre invents a tier for a
story scene.**

So the reusable, no-refactor-later move is the one this repo already made: **`PanelShell` has a
`size?: "default" | "actorSheet"` prop, and `actorSheet` is the near-fullscreen bound**
(`PanelShell.tsx:17-18`, `:97-99` — `h-[min(960px,92vh)] w-[min(1800px,96vw)]`). That is the exact
shape a scene needs, already reviewer-accepted for a full-height surface inside band 2/3. Extending
`DialogShell` with the same optional `size` contract is:

- **Not a refactor when a scene grows** — a later scene can request another size without a new band,
  a new shell, or an allowlist edit.
- **Still honest about GG-61** — GG-61 says a dense entity scrolls inside its own shell and the shell
  never swallows the viewport; `actorSheet` already proves a near-fullscreen *bounded* shell is the
  accepted way to do that.
- **Zero band-guard churn beyond the one real fix** — the prologue's `stages/sanctum/` path still is
  not a `shell/` path, so it must be added to `bandGuard.ts`'s allowlist (defect #1), but that is one
  reviewed entry with the required justification, not a band amendment.

**Owner decision (S1, 2026-09-15) — the geometry is stronger than the recommendation above.** The
owner chose **full-bleed**, not the bounded `actorSheet`-style box. The *mechanism* (an optional
`size` on the existing shell) is unchanged; the *geometry* fills the viewport, and because that runs
against GG-61's literal text the `shell-scene-size` spec carries a **scoped, reasoned exemption**:
GG-61 exists so a *dense entity's* body can scroll inside a bounded shell, and a scene has no dense
body and **never scrolls**, so the failure GG-61 prevents cannot occur. The exemption is scoped to
`size="scene"` and is not a licence for other surfaces. See
[story-scene-map.md](story-scene-map.md) §"GG-61 exemption (S1)".

**Rejected for Q1:** a dedicated stage-owning layer (needs a GG-5 amendment for an eighth band, and
GG-4 says a layer must never cause a stage change as a side effect — a scene that "owns the stage"
would violate that); a brand-new `SceneShell` (a second shell to maintain for the two things
`DialogShell` already provides: layer push/pop and focus return).

### Decision 2 detail — two actors is the floor, not the ceiling

A dialogue scene with a cast is the genre floor: Ren'Py's `show`/`hide` model *is* multiple sprites on
the master layer, and Dialogic's portrait subsystem manages many portraits per character. Cutting to
one actor would be the "don't cut the fundamental" mistake. Therefore:

- `actor-portrait` is a **slot array** (`actors[]`), and each actor carries a `speaking | inactive`
  state (the Dialogic highlight analogue).
- The **narrow breakpoint is the new work**: at 320px two side-by-side actors do not both fit, so the
  scene needs a declared collapse rule (stack with the speaker forward, or show the speaker only).
  That rule is a structural decision for the spec, and it is why Q2 could not be answered "later".
- The art manifest must support **N sprites**, not one `storySprite` role (defect #4), and
  `scene-script` beats name a `speakerId` that resolves to one of them.

### Cue ownership, corrected (decision 3)

**My Q3 framing was wrong, and the challenge was right.** The story scene is a web-FE feature: the
beats, the `speakerId`, and the cue id all live in the FE (`RiftPrologueDialog.tsx:13-44`), and the FE
already renders its own cue state today via `data-cue={beat.cue}` (`:169`) with a CSS-driven effect
(`rift.css:32-44`). There is **no injector-side story state machine and no reason to build one** — the
injector does not know what a prologue is, and it should not learn.

What is genuinely unresolved is much narrower, and it is a **rendering** question, not an ownership
question:

- **Where the cue's visual effect is drawn.** Today the cue is CSS inside the scene bed. The four
  `rift.*` recipes in `VfxCatalog` are the *other* channel (Unity-side particles/overlays), and they
  are unwired.
- So the real choice is: **(a)** the scene's cue stays purely CSS (no Unity VFX), and the `rift.*`
  recipes are retired or left for the sibling Rift Gate program; or **(b)** the scene additionally
  emits the semantic cue over the host bridge so the Unity-side recipe plays *behind the overlay*.

**Decision 3 as recorded:** the scene owns the cue; the FE keeps `data-cue`; the `onCue` seam stays a
seam and is **not** required to be wired for v1. Option (b) is a later, additive increment owned by
whoever owns the bridge (the Rift Gate program's `rift.hide`-style vocabulary), and the FE must never
bind a key or open a socket for it. This removes `cue-seam` from the v1 critical path — it remains a
named seam, not a work item.

### Decision 4 detail — why shared wins (the "gold standard" question)

The question asked whether this is the genre standard. **In the genre there is no separate
"reveal" component: a reveal is just a one-beat scene.** Ren'Py has one say screen for both a
dialogue line and a narration line (single-argument say = narration); Dialogic has one dialogue
viewport for dialogue, narration, and choices; neither has a second "notification" grammar for a
one-shot message.

So the gold-standard shape is: `OnboardingReveal` (the shipped one-current-reveal component,
`stages/sanctum/OnboardingReveal.tsx:11-45`) should eventually **compose the same `dialogue-window` /
`advance-control` / `scene-progress` pieces** with a one-beat script and no cast — instead of
hand-rolling its own heading/body/button trio as it does today. That is the shared-family answer, and
it is a **later increment**: this program does not edit `OnboardingReveal` or its owning spec
(`standalone/spec-first-session-progression.md`), it only declares the shared pieces so the reveal can
adopt them.

### Decision 5 detail — skip is a contract

<!-- citations-historical: the S6 cutover (00b1f2aa9, 2026-09-16) cut RiftPrologueDialog.tsx from 203 lines to 39 and deleted riftAssets.ts and features/onboarding/rift.css; the successor is src/ui/story-scene/StorySceneHost.tsx -->

Skip stays present on **every** beat including the last, and skipping writes the same terminal state
as watching (GG-52; already true — `RiftPrologueDialog.tsx:148` calls the same `finish("skipped")`
that acknowledges durably). No first-scene nudge, no confirmation dialog. The sibling ideal records
the same rule from the other side: *"Skip intro → the same destination. Skipping never loses Souls,
grants, content, or future story access"* (`docs/ideas/onboarding-gnome-teaser.md:33`).

### One conflict this creates (flagged, not hidden)

`docs/ideas/onboarding-gnome-teaser.md:37` locks the prologue as *"a band-3 `DialogShell` owned by the
Sanctum stage"*. Decision 1 keeps band 3, so **that lock is honored, not broken** — but the narrative
source also says each beat is *"one full-screen illustration"* (`:23`), which the current 440px card
does not deliver. Decision 1 (`size` contract) is exactly what reconciles the two: band-3 ownership
stays, the geometry becomes scene-sized. The spec must update that sentence's *implementation* while
preserving its band decision.

---

## Handoff

**Next phase:** `/spec` — module specs under `docs/architecture/story-scene/`, then the prefixed
plan/todo. Every path this program writes is prefixed `story-scene`:
`docs/architecture/story-scene-ideal.md` (this doc), `docs/architecture/story-scene-map.md`,
`docs/architecture/story-scene/spec-<piece-id>.md`, `tasks/story-scene-plan.md`,
`tasks/story-scene-todo.md`.

**Three things the spec must carry that are easy to lose:**

1. **Band 3 stays, geometry changes.** Decision 1 extends `DialogShell` with a `size` contract; it
   does not move the scene to a new band or a new shell, and it does not break
   `onboarding-gnome-teaser.md:37`'s band-3 lock.
2. **Two actors is the floor.** Decision 2 makes `actors[]` an array and creates a real
   narrow-breakpoint obligation; the art-role contract must support N sprites (defect #4).
3. **Skip is a contract, not a convenience.** Decision 5 keeps skip present on every beat, and the
   acknowledgement path stays one `finish(outcome)` for watched and skipped.

**This phase wrote no spec, no plan, and no code.** It did not edit other programs' docs.

**Handoff:** `/spec` and the map are complete — 21 modules, 21 specs, all owner questions resolved.
The next phase is `/plan`, which writes `tasks/story-scene-plan.md` and `tasks/story-scene-todo.md`.
**This phase wrote no plan and no code**, and did not edit other programs' docs.

**Reading gate:** `docs/DESIGN-GATE.md` §1 rows for Player menus (gui-lego, GG-1, fe-game-foundation)
and the onboarding/story surface were read in this session, along with the consumer, its contracts,
the VFX catalog, the shell band/layer/stage guards, the i18n guards, the sibling first-session spec,
the narrative source (`docs/ideas/onboarding-gnome-teaser.md`), the lore boundary, and the art brief.

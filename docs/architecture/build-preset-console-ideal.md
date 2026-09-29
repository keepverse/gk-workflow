# Build preset console — the idea-ui pass

**Status:** idea-ui phase (`/idea-ui`, procedure [idea-ui-phase.md](idea-ui-phase.md)). Not a spec.
Not a plan. No React authorized. This is **BP3.1** of [`build-preset`](build-preset-map.md) Wave C —
`spec-preset-surface.md` deliberately left host/layout/pieces to this pass.

**Contract this fills in:** [build-preset/spec-preset-surface.md](build-preset/spec-preset-surface.md)
— the VM shape (`foldBuildPresetConsoleVm`), the closed bus (`buildPresetConsoleBus`), and the API
routes are fixed there. This document answers the three things that spec deliberately left open:
**where** the surface lives, **what tree** composes it, and **which pieces** it needs.

**DESIGN-GATE read in this session:** [idea-ui-phase.md](idea-ui-phase.md),
[game-gui-principles.md](game-gui-principles.md) (full), [gui-lego-ideal.md](gui-lego-ideal.md),
[gui-lego-authoring.md](gui-lego-authoring.md), [gui-lego-map.md](gui-lego-map.md),
[design/gui-lego/README.md](../design/gui-lego/README.md),
[gui-lego/menu-refactor-queue.md](gui-lego/menu-refactor-queue.md), `decisions.md` **GUI Lego — menu
composition**, [actor-sheet-ideal.md](actor-sheet-ideal.md). Supporting reads: the shipped
`aptitude-preset-console` recipe + FE (`AptitudePresetConsoleHost.tsx`, `foldPresetConsoleVm.ts`,
`foldAptitudesSurfaceVm.ts`), `docs/guide/the-loops.md` / `relics-and-builds.md` /
`mechanisms/build-presets.md`, `gk-web/web/fusion-rpg-web/src/shell/railState.ts`,
[tech-stack.md](../design/tech-stack.md) §3.3 buy-before-build libs.

---

## 0. Out loud

1. **Every RPG feature lives in the RPG layer.** This console presents patron/field/skills/gear/
   aptitude state the server already computes (`preset-store`, `piece-appliers`,
   `apply-orchestrator`, `capture-current`); it invents no rule and no price.
2. **A game is a stage with layers, not a document with pages** (GG-1). This is one more layer,
   opened over whichever stage the player is on.
3. **Player menus are recipe + pure fold + closed bus — never a god TSX** (`decisions.md` GUI Lego).
4. **Theme packs own paint.** No hard-coded chip colours for patron/field/skills/gear/aptitudes rows.
5. **Buy before build.** `lucide-react` for icons, `recharts` only if a chart earns its place (this
   surface is lists and price lines — no distribution chart is needed; see §5's rejected shapes),
   `motion` for panel transitions. A fat chunk is a code-splitting job, never a reason to hand-roll.
6. **This is new construction, not a bug list.** There is no live surface to audit; §4 inventories
   what the *server side* already ships (proven end to end in BP1.1–BP2.12) versus what the FE has
   zero of today.
7. **No engine vocabulary on the player surface.** No `refId`, `refKind`, `correlationId`,
   `presetRevision` on a player-visible label — those stay in the fold's internals and the wire.

---

## 1. Which loop this extends

From [the-loops.md](../guide/the-loops.md) spine C (item collection and progression) /
spine A (level up and power), pillar [relics-and-builds.md](../guide/relics-and-builds.md):

> **Build presets (Vision):** save a synergy loadout — patron, relics, aptitudes, who you field — so
> a fire lean is something you keep, not five independent clicks.

The guide page this ships against is [mechanisms/build-presets.md](../guide/mechanisms/build-presets.md)
(rewritten from "Vision" at CP4, per `spec-preset-surface.md`'s own Player-copy section — not this
pass's job).

This is not a new loop. It is the one surface where the player *keeps* a combination the other five
surfaces (Patron, Pacts/Contracts, the aptitude console, the item loadout library, the skill loadout)
already let them set by hand, one at a time.

---

## 2. What this is (player language)

**"Save what you have as a build. Swap builds without five separate clicks."**

You look at a list of saved builds. Each one names what it changed last time: a patron, a squad, a
skill loadout, gear, an aptitude lean — and whether every piece it remembers still exists (a salvaged
item, a released creature — named, never silently dropped). You capture your current setup into a new
build with one click. You preview a build before you commit to it: every soul it will cost, every free
respec it will spend, anything it cannot do and why, and — if a choice is yours to make (spend a free
respec now or pay souls) — you make that choice before you apply, never after. Applying restores the
five pieces you saved, and the surfaces that already show patron, contracts, aptitudes and gear each
show the result through their own normal read, not through this panel's own memory of what it just did.

---

## 3. What already exists

### Built (server side — BP1.1 through BP2.12, proven by their own test suites)

| Finding | Evidence |
|---|---|
| Every gate a build preset applies through already has a named service: `PatronService.SetAsync`, `ContractService.BindAsync`/`ReleaseAsync`, `ActionLoadoutService.Set`/`Preview`, `ItemLoadoutApplyService.Preview`/`ApplyAsync` | `gk-core/src/FusionRpg.Server/Gates/*.cs` |
| Preview/quote functions exist for patron and contracts, sharing the exact precondition the write uses | `RpgStore.QuotePatron`, `QuoteBind`, `QuoteRelease` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs`, `RpgStore.Contracts.cs`) |
| The item loadout library has a full CRUD + preview + apply surface over HTTP, proving the "preview names conflicts, force reports what it stripped" contract this console must render | `gk-core/src/FusionRpg.Server/ItemLoadoutEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemLoadoutEndpointsTests.cs` |
| The points-to-shares half of "capture the current aptitude allocation as a preset" is pure and tested | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudePresetCapture.cs` |
| A working, shipped sibling console for exactly one of the five libraries (aptitude presets) already exists end to end: gallery + editor + a recharts donut, opened as a nested `PanelShell`, with its own closed bus and pure fold | `gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx`; `foldPresetConsoleVm.ts`; `presetConsoleBus.ts`; `docs/design/gui-lego/recipes/aptitude-preset-console.json` |

### Wiring gap (server-side machinery not yet reachable from the FE)

| Finding | The inert line |
|---|---|
| `preset-store`, `apply-orchestrator`, `capture-current` (BP1.9–BP1.12, BP2.3–BP2.15) are specced but currently **blocked on empire-progression** (`EP1.10`/`EP4.10`/`EP3.3`, tracked in `tasks/build-preset-ledger.jsonl`) — the routes this console's Model layer needs (`GET/POST/PUT/DELETE /api/build-presets…`) do not exist on the server yet | `docs/architecture/build-preset/spec-preset-store.md`, `spec-apply-orchestrator.md` |
| `preset-entry` (the aptitude console's own "open the wider build console" affordance) already exists and already reads **"Build presets…"** — pointed at a program that, at the time it was written, meant the aptitude console itself | `gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts:205,262`; `AptitudePresetConsoleHost.tsx:384` — this is the exact name collision `spec-preset-surface.md` §"The name collision (map X1)" already names, and BP3.4 (next task, same session) fixes it |

### Real gap (nothing to reuse; new module)

| Finding | What has to be built |
|---|---|
| No FE code anywhere reads or writes patron+field+skills+gear+aptitudes as **one composite** | `foldBuildPresetConsoleVm.ts` (new), `buildPresetConsoleBus.ts` (new), `lib/bus/buildPresets.ts` (new) — BP3.2/3.3, after BP1.9–2.15 unblock |
| No recipe/piece exists for "one row per closed piece kind, present or missing with its reason" | `build-preset-detail` (this pass, §6) |
| No recipe/piece exists for "a price line, a refusal, or a two-option payment choice, rendered generically" | `build-preset-price-line`, `build-preset-payment-choice` (this pass, §6) |
| No top-level rail entry exists for "your whole build" as a concept — Patron/Pacts/Aptitudes/Gear are each reachable, but never as one saved thing | `railState.ts` gains a `builds` entry (this pass, §5/§8; wiring is a later wave's job) |

**Not a real gap:** "the server can't preview a build preset yet." It can, per piece
(`ItemLoadoutApplyService.Preview`, `QuoteBind`/`QuoteRelease`/`QuotePatron`) — the missing piece is
the orchestrator that sums them (`apply-orchestrator`, BP2.9/2.10), which is a scheduling question
(blocked on `empire-progression`), not a design question this pass owns.

---

## 4. Prior art

| Steal | From | Failure mode if copied wrong |
|---|---|---|
| Named, swappable gear/skill loadouts as a first-class saved object, separate from "the thing itself" | Path of Exile's Item/Skill sets, Diablo IV's Loadouts | PoE lets a set reference a missing/changed item silently on load — this program's own contract already refuses that (`LoadoutEntryState.Missing`, named, never dropped); do not regress to "it just applies what it can" |
| A build-list gallery with a one-line "what changed" summary per entry, not a full re-render of the whole build per row | Diablo IV's Loadout picker (name + class icon + gear-slot glyphs, not eleven stat blocks) | A gallery item that tries to preview the WHOLE build inline becomes the "channel-id table as first paint" defect GG-25/GG-64 already name — summary only, detail on select |
| Price-before-commit as a first-class step, not a toast after the fact | PoE2's respec-cost preview before confirming a passive refund | Computing the price client-side to "feel fast" is exactly what `spec-preset-surface.md`'s own self-audit rejects — the preview route is the only price source |
| A single saved-loadout list feeding a diff/preview pane on select (list left, detail right) | The shipped `aptitude-preset-console` itself (`preset-console-layout`: gallery / editor / chart) | Copying its literal three-slot shape (gallery / editor / chart) would be wrong here — a build preset has no "editor" (you capture it, you don't hand-tune five subsystems in one place) and no distribution to chart. The steal is the **gallery-left, detail-right InspectSplit shape** (GG-63), not the slot names. |

---

## 5. The shape — chosen vs rejected

### Host

**Chosen: a new top-level rail entry, "Builds" (key `B`), its own `PanelShell` (band 2), depth 1 from
whichever stage the player is on.**

Reasoning:
- **GG-9 (one canonical home).** A build preset is not owned by Patron, Pacts, Aptitudes, or Gear —
  it is a composite *over* all four plus Skills. Nesting it under any one of them (e.g. "open Builds
  from inside the aptitude console") would make that one subsystem the accidental owner of a concept
  that spans five.
- **GG-10 (depth cap, three pushes).** `AptitudePresetConsoleHost` already sits at depth 3 (stage →
  ActorSheet → nested `PanelShell`, its own doc comment: *"Depth: stage → sheet/layer → this
  PanelShell ≤ 3"*). Opening the build-preset console **from inside** that nested console, or from
  inside ActorSheet at all, would be a fourth push — GG-10 names exactly this as the smell that the
  information architecture is wrong, not that another sub-panel is needed.
- **Precedent already in the nav.** `railState.ts` derives eight layers (`creatures`, `commanders`,
  `relics`, `fusion`, `pacts`, `expeditions`, `almanac`, `chronicle`) from one state-driven ladder
  (GG-44 — never a compile-time constant list, always keyed to an unlock condition). Patron and Pacts
  (Contracts) already live inside `creatures`/`pacts`; a ninth entry for "the whole build, saved" is
  the same shape, not a new mechanism. Key `B` is free (used keys: `M C K R F P E A H`).
- **Product-vision naming already agrees.** `relics-and-builds.md` lists Build presets as a sibling
  section to Commanders, Relics, and Free-build aptitudes under one pillar page — not as a sub-feature
  of any one of them.

**Rejected:**

| Rejected | Why |
|---|---|
| Nest under ActorSheet's Aptitudes tab (a fourth-level `PanelShell` inside `AptitudePresetConsoleHost`) | Violates GG-10; the aptitude console is already at the depth ceiling |
| Nest under the Creatures page (where Patron/Pacts views already live) | Patron and Field are only two of five pieces; making Creatures the owner privileges those two over Skills/Gear/Aptitudes for no structural reason (GG-9) |
| A modal/dialog rather than a Panel (band 3 instead of band 2) | This is a browsing + preview + apply flow with real state (selection, an unanswered choice) that the player may want to leave open while checking Pacts/Aptitudes in another layer — band 2 (Panel) is the correct band per GG-5's own table; band 3 (Dialog) is for a single decision, not a console |

### Recipe tree

```text
build-preset-layout (root, new — a minimal 2-slot frame, mirrors preset-console-layout's own
                      precedent rather than cloning surface-shell's six slots; mounts INSIDE the
                      existing rail PanelShell, never a forked one)
├── slots.gallery   → build-preset-gallery (piece: preset-gallery, reused + widened — see §6)
└── slots.inspect   → split-inspect                (reused: list left / detail right, GG-63)
                        ├── build-preset-detail     (new — one row per piece kind, §6)
                        └── build-preset-preview    (thin layout container, no new spec — see below)
                              ├── build-preset-price-line*      (new, one per price/refusal line)
                              └── build-preset-payment-choice*  (new, one per unanswered species choice)

Host-owned, outside the recipe (same treatment preset-console-layout gives allocate-decision-strip):
  PanelShell's own sticky footer → Capture · Preview · Apply · Delete
  lifecycle overlays: phase-loading | phase-empty | phase-error | phase-pending (reused, unchanged)
```

`build-preset-preview` is a thin layout container, not a piece with its own payload beyond the two
lists — folded here rather than given a sixth spec, the same way `inspect-pane` hosts
`value-hero`/`meta-sentences`/`gauge-*` in the Derived recipe without being a "new" concept on its own.

**Rejected:** a three-slot `gallery / editor / chart` clone of the aptitude console (no editor concept
exists here — a build preset is captured, not hand-tuned in this surface; no distribution chart —
nothing here is a share-of-1000 breakdown to chart, unlike aptitude presets).

### Actions (footer)

**Chosen:** Capture · Preview · Apply · Delete, in a sticky panel footer (same place
`allocate-decision-strip` puts Confirm/Cancel for the aptitude console) — never a nested
`ConfirmDialog` (GG-63), matching `buildPresetConsoleBus.ts` (new)'s own closed event list
(`build.capture`, `build.preview`, `build.apply`, `build.delete`) fixed by
[spec-preset-surface.md](build-preset/spec-preset-surface.md).

---

## 6. New pieces (this pass)

Every piece below gets its own `docs/architecture/gui-lego/spec-<piece-id>.md` (this commit) and is
added to `docs/design/gui-lego/recipes/build-preset-console.json` (this commit). HTML drafts and React
factories are **not** this pass's job (authoring.md steps 6–8, a later wave).

| piece-id | Kind (ERM) | Job |
|---|---|---|
| [`build-preset-layout`](gui-lego/spec-build-preset-layout.md) | layout | Root 2-slot frame (gallery / inspect) — mirrors `preset-console-layout`'s own minimal-root precedent rather than cloning `surface-shell`'s six slots; actions are host-owned footer chrome, not a slot |
| [`preset-gallery`](gui-lego/spec-preset-gallery.md) | Row list | **Widened, not forked** — the shipped aptitude console's own gallery piece, given a canonical spec for the first time (it shipped with none) and two new optional payload fields so build-preset can reuse it unchanged for its own consumer |
| [`build-preset-detail`](gui-lego/spec-build-preset-detail.md) | Row list | One row per one of the five closed piece kinds: target label, reference label, present/missing + reason |
| [`build-preset-price-line`](gui-lego/spec-build-preset-price-line.md) | Row list | Every price and refusal line, generic over resource/reason |
| [`build-preset-payment-choice`](gui-lego/spec-build-preset-payment-choice.md) | Row (chrome) | The species dual-option chooser (pay souls vs spend a free respec), one mounted instance per unanswered target, no default |

Reused unchanged (already specced, already shipped): `split-inspect`, `scroll-region`,
`phase-loading`, `phase-empty`, `phase-error`, `phase-pending`, `chip`.

---

## 7. Tunables

**None.** This surface presents prices and refusals the server already computed
(`spec-preset-surface.md`'s own "Tunables: none"). No catalog file is added; no theme pack is added —
existing `chip`/status theme packs (element/status-category/neutral) already cover "present" /
"missing" / "refused" chip states. No structural CSS constant beyond the existing band-2 `PanelShell`
bound (`min(1440px,92vw)`-class sizing, same viewport contract as every other rail panel — GG-36).

---

## 8. What this deliberately does not decide

- **The exact unlock condition for the "Builds" rail entry.** `hasAnyBoundCreature` (matching
  Expeditions' own condition) is this pass's working assumption — capturing a build needs at least one
  bound creature to be meaningful — but it is a one-line change in `railState.ts` a later wave makes,
  not a structural choice this pass locks.
- **Whether `preset-entry`'s wording changes beyond the label.** BP3.4 (immediately following this
  task) relabels `AptitudePresetConsoleHost` to "Aptitude presets"; whether the aptitude console also
  grows a *link* into the new Builds panel (so a player editing an aptitude lean can jump straight to
  saving it as part of a build) is a cross-sell decision for a later wave, not this one.
- **HTML drafts, theme swatches, or React factories** for the four new pieces — authoring.md steps
  6–8, after an owner accepts this recipe.
- **Whether `build-preset-price-line` is later promoted to a shared gui-lego piece** (workbench and
  the armoury both render price lines today in their own shapes) — a real reuse opportunity, flagged
  here, not resolved here.

---

## 9. Open questions — owner only

1. **Rail entry approval.** Add "Builds" (key `B`) as a ninth top-level rail layer — confirm the label
   and the unlock condition (`hasAnyBoundCreature`, this pass's recommendation) before BP3.2 wires it.
2. **Cross-sell link.** Should `preset-entry` (inside the now-renamed "Aptitude presets" console) gain
   a "save this as part of a build" affordance pointing at the new console, or stay a closed, unrelated
   sibling? Either answer ships the same BP3.x scope; this only affects a follow-up task, not this one.

---

## 10. The real question

Not feasibility — every gate this console calls already exists and is tested (BP1.1–BP2.12). The real
question is **shape**: does a five-subsystem composite deserve its own top-level home (this pass's
recommendation), or should it live inside one of the five it touches? This pass answers with GG-9,
GG-10, and the existing nav rail's own precedent; §9 asks the owner to confirm the one piece of that
answer that is a product decision (the rail entry itself) rather than an architectural one.

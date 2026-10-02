# Spec: `wonder-composer`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`; main checkout untouched. Module id
`wonder-composer`, row 3 of the [empire-wonder-surfaces map](../empire-wonder-surfaces-map.md)
(wave 2 — depends on `wonder-rest` + `wonder-content`; external: inventory shelf). Ideal:
[empire-wonder-surfaces-ideal.md](../empire-wonder-surfaces-ideal.md) (§5 composer/cost-plate/refusal
rows, §7 chosen, §8 catalog/packs, §9.7 backend-reads note, §10 Q1–Q4 + Owner resolutions). Backend
contracts: [loam-relics-and-wonders/spec-wonder-build-flow.md](../loam-relics-and-wonders/spec-wonder-build-flow.md)
(§Design 1/3/4/6–7) and `spec-wonder-rest.md` / `spec-wonder-content.md` in this folder (wave-1
pass-through + rows — consumed, never re-decided). Authoring order:
[idea-ui-phase.md](../idea-ui-phase.md) §1 (queue → recipe → fold+bus → themeRefs → drafts → owner
accept → mount). House style precedent:
[scoped-inventory-hierarchy/spec-legion-cargo.md](../scoped-inventory-hierarchy/spec-legion-cargo.md),
adapted for a UI spec (recipes, folds, buses instead of tables/verbs where apt; Locked anchors +
checklist kept).

## Objective

Specify — but do not build — the great-work composer: a band-2 panel over the world stage where the
player picks a Wonder row, lays the exact relic instances its foundation asks for, picks the open
plot, sees the stone-and-ironwork price beside the relic price, and confirms. Then specify its two
inseparable companions: the cost-plate (materials + relic price, always comparable) and the refusal
fold (all four wire reasons translated to player copy with next actions, nothing consumed on
refusal).

Success looks like: a wave-2 UI build can mount this recipe with no further design decisions — every
slot, every bus event, every fold reading, every themeRef, and every draft state is named here; the
picked list it files is exactly `PendingOrder.relicInstanceIds` → `WorldCommandRequest.relicInstanceIds`
(`spec-wonder-rest.md` §Design 3, consumed by name); and the owner has accepted HTML drafts before a
single TSX file is written.

**This spec stops at owner-accept drafts.** No React code, no factory, no mount — per idea-ui §1 and
ideal §9.8. Drafts are HTML/description pairs; the React mount + landmark tests are the wave-2 build
task this spec locks anchors for.

## Locked anchors

- **The wire shape is consumed, never re-shaped.** `PendingOrder.relicInstanceIds?: string[]` +
  `toRequests` mapping (`worldSelection.ts:28-46`, `:106-118`) and TS/C# `WorldCommandRequest`
  `relicInstanceIds` are `wonder-rest`'s contract (`spec-wonder-rest.md` §Design 1–3). This module
  files through them; it may not rename, re-shape, or fork the field. Picking order is preserved
  (list order is what the `claimed` set and the spend iterate).
- **The rows are consumed, never re-authored.** `standing-stones` (Sector/Common, `relicCost: 1`)
  and `sunspire-throne` (Empire/Unique, `relicCost: 3`) are `wonder-content`'s rows
  (`spec-wonder-content.md` §Design 1–2). This module reads their names, scope/rarity readings, and
  `RelicCost` counts; it authors no row, edits no seed file, touches no tuning file.
- **Owner resolutions bind every presentation choice below** (ideal Owner resolutions, 2026-09-15):
  composer is a **panel** (band-2, never a route); relic picking is **reachable-first** (legion sheet
  cargo tab + sector store, full shelf one disclosure away); **live cap counts are shown** (the fold
  MUST render them); reserved tiers render as **locked teasers**. A design that hides counts,
  replaces the stage, or omits the teasers contradicts a locked decision.
- **Refusal strings are owned by the backend, translated here, never reinvented.** The four wire
  tokens — `wonder.cap-reached`, `relic.count-mismatch`, `relic.not-reachable`,
  `build.cannot-afford-materials` (`WorldCommandAdmission.cs:114-116`,
  `BuildResolver.cs:104-130`) — are translated by the refusal fold into authored player copy. The
  raw token never renders (GG-23); a second spelling of any token is a defect.
- **Shared pieces are consumed from the inventory program, never re-specified here** (map
  Assumption 1; ideal §10 Q7 recommendation). `tool-search`, `chip`, `split-inspect`,
  `scroll-region`, `phase-*`, `stock-row`, `capacity-meter`, relic shelf, `RelicRow`/`ItemCard`/
  `CompareView` are owned by `empire-inventory-surfaces` — this spec names them by piece id and
  states the bind, and designs nothing inside them. (Ownership is RECOMMENDED, owner confirms at
  the `/spec` gate per the map — if the owner assigns the shelf elsewhere, this anchor follows.)
- **Paint belongs to packs, copy belongs to the catalog.** No hard-coded scope/rarity colour map in
  any recipe or fold (Lego violation); no refusal sentence or Wonder name invented in a draft
  (GG-62). Undecided pack/catalog rows are listed as owed (§Design 6), not improvised.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| FE order queue + wire mirror shape (pre-relic): `PendingOrder` eight kinds, `toRequests` round-trips `stance`/`amount`/`structureId`; `WorldCommandRequest` TS mirror | `gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.ts:28-46` (`PendingOrder`), `:106-118` (`toRequests`); `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:277-295` (mirror) — both read in full this session |
| Submit/commit verbs the composer files through: `useSubmitWorldCommands` (`POST /api/world/{id}/commands`), `useCommitWorldTurn` | `bus/world.ts:549-554` (submit), `:560-571` (commit) |
| Sector inspector host the panel layers over: `SectorInspector` (nine blocks + action cluster), `SlotRow` seven states with built vs under-construction sentences | `stages/world/inspector/SectorInspector.tsx:1-60` (host, blocks); `SlotRow.tsx:4-37` (seven states), `:49-78` (sentences) |
| gui-lego kit: registries (piece/theme/recipe), `RecipeMount`, folds/buses per surface, theme packs (element/side/resource/action-category/neutral), ERM rungs, queue discipline | `docs/design/gui-lego/README.md` (piece inventory + reuse matrix, incl. `tool-search`, `split-inspect`, `scroll-region`, `phase-loading`/`empty`/`error`/`pending`); `features/gui-lego/` (`pieceRegistry.ts`, `recipeRegistry.ts`, `themeRegistry.ts`, `createSurfaceBus.ts`, `*SurfaceBus.ts`); `ui/gui-lego/` (`RecipeMount.tsx`, pieces) |
| Relic collection layer (the authoritative card home, GG-9): row/card/compare with four tabs | `layers/relics/RelicsLayer.tsx:1-120` (tabs at `:39`, no-route discipline at `:89-115`) — via ideal §4, re-confirmed by location this session |
| Sector loam ledger pattern the cost-plate joins: attributable upkeep rows | `stages/world/inspector/SectorLoamBlock.tsx:1-38`; upkeep adapter `contract/adapt.ts:447-454` — via ideal §4 |

### Wiring gap

| Gap | The inert/underused line |
|---|---|
| Queue + wire carry no relic list (closed by `wonder-rest`, consumed here) | `worldSelection.ts` + `bus/world.ts` carry no `relicInstanceIds` today — `spec-wonder-rest.md` §What already exists |
| `SlotRow` built/under-construction sentences print the raw `structureId` — no Wonder identity, no scope/rarity badge, no link to what the Wonder does | `SlotRow.tsx:54,58` (`"${slot.slotTypeId} — ${slot.structureId}"`); `SlotView` (`contract/types.ts:871-872`) carries no Wonder facet — via `spec-wonder-content.md` §What already exists |
| Zero FE handlers for the four Wonder refusal tokens — nothing could explain a refusal even if the engine refused correctly | Web-wide grep (`wonder\|RelicCost\|RelicInstanceIds\|cap-reached\|count-mismatch\|not-reachable`) returns only a "wondering" comment false positive — ideal §4, consumed |
| No `wonder-scope` / `wonder-rarity` theme packs; no `wonder-composer.*` bus | Packs dir survey (no `wonder-*`); `features/gui-lego/*SurfaceBus.ts` (nothing wonder-scoped) — ideal §4 |
| Relics layer is equip-framed (equip flow, paperdoll, sockets); nothing presents a relic as build-founding treasure with where-it-sits | `RelicsLayer.tsx:96-120` (Held=equip, Storage="not split yet") — ideal §4 |

### Real gap

| Gap | What this module specifies (build is wave-2) |
|---|---|
| No `wonder-composer` recipe (Wonder row + N relic instances + slot + material price + confirm) | §Design 1: recipe slot tree |
| No composer fold (reachable-first join, live cap counts, affordability) + closed bus | §Design 2–3: fold slices + `wonder-composer.*` bus |
| No cost-plate piece contract (materials + relic price side by side) | §Design 4: cost-plate |
| No refusal-message catalog mapping (four reasons → copy + next actions) | §Design 5: refusal fold + catalog rows owed |
| No Wonder display-copy rows (names, effect readings, scope/rarity readings, refusal copy) | §Design 6: catalog rows owed (GG-62) |
| No scope/rarity paint contracts | §Design 6: `wonder-scope-*` / `wonder-rarity-*` pack refs owed (paint lives there, never here) |

## Design

Authoring order throughout is idea-ui §1: queue row → piece index → recipe → fold + bus →
themeRefs → HTML drafts → owner accept → (wave-2) React mount + landmark tests. This spec walks the
order up to owner accept; the mount step is locked anchors for the build (§Locked anchors for
build), not work done here.

### 1. Recipe — `wonder-composer` (band-2 panel over the world stage)

Host: a band-2 panel layered over the world stage (`SectorInspector` stays mounted beneath;
`surface-shell` / `PanelShell` grammar — never a forked shell, never a new route, GG-1/GG-5/GG-11).
The URL encodes stage + open layers (GG-8). Closing returns the player to the exact sector,
selection, and scroll they left (GG-12). The destructive-by-consumption confirm (spends relics) is a
band-3 dialog (GG-22); refusal and result notices are band-4 toasts (GG-16). Stage → sector →
composer → confirm is the full depth — no fourth push for "what does this do" (GG-63: readings open
in-pane).

Slot tree (recipe JSON `docs/design/gui-lego/recipes/wonder-composer.json`, wave-2 build; shaped
here, written there):

```
surface-shell (band-2 panel)
├── tool-search                    — Wonder-row + relic filtering (shared piece, consumed)
├── split-inspect                  — list left / reading right (GG-63)
│   ├── scroll-region ── wonder-catalog      — one row per buildable Wonder (identity piece,
│   │                           live cap-count line, locked teasers as peers — §Design 2, §Design 6)
│   └── scroll-region ── relic-shelf-link    — reachable-first candidates (§Design 2);
│                               full shelf one disclosure away (shared shelf, linked GG-9)
├── slot-pick                      — open plots of the held sector (SlotRow + Wonder facet,
│                               consumed; wonder-display extends the facet, this recipe only binds it)
├── wonder-cost-plate              — §Design 4 (materials + relic price + nights)
├── confirm (band-3 dialog)        — spends relics; names exactly what leaves (GG-22)
└── lifecycle overlays             — phase-loading / phase-empty (empty shelf, locked tier) /
                                    phase-error + retry (failed sector read) / phase-pending
                                    (order filed, awaiting End Turn commit — GG-15)
```

Recipe rules: Wonder rows lead with price and requirement (relic count + stone/ironwork + nights),
details behind the select (ideal §6 Civ6-list precedent, GG-26 inverted correctly). Picking between
rows — and between candidate relic instances — defaults to side-by-side against current state (this
slot now vs with the Wonder; relics needed vs relics reachable here — GG-47). An unbuildable row
names its blocker on the control (GG-55); empty shelf, locked tier, and failed sector reads are
authored states, not blank panels (GG-17). Structural CSS (grid/flex areas, 720px-floor bounds per
GG-36/GG-61, internal scroll) is called out per recipe, not per piece.

Queue: the composer enters `menu-refactor-queue.md` as its own row (one surface per stream —
composer first, sector display second; never both in one stream — ideal §7).

### 2. Fold — reachable-first join, live counts, affordability (pure data, no paint, no copy)

One pure fold slice (sibling of `foldDerivedSurfaceVm` / `foldConditionSurfaceVm` in
`features/gui-lego/`, e.g. `foldWonderComposerVm` — name locked at build, shaped here). Inputs are
world/Game state and catalogs only — never lawn, Unity, or injector fields (ideal §0.1). Outputs are
payloads with `themeRef`s; pieces declare slots only.

| Fold reading | Source (read, never re-owned) | Renders as |
|---|---|---|
| Wonder catalog rows (both shipped rows: identity + `RelicCost` + scope/rarity + effect reading) | Structure catalog rows `standing-stones` / `sunspire-throne` (`wonder-content`); display catalog names/readings (§Design 6) | Catalog list rows: authored name (never raw id, GG-62), price-first line, effect sentence |
| Reachable-first candidates: relics reachable *here* (issuing legion's cargo via the sheet tab + target sector's store) first; full owned shelf one disclosure away | Reachability overlay API owned by `scoped-inventory-hierarchy` + sibling shelf (ideal §9.3, §9.7); where-it-sits truth is theirs, this fold only joins it | Candidate rows (`stock-row` density, shared): picked vs needed (`k of N`), reachable group above the fold, full shelf behind one disclosure |
| Live cap counts: raised-vs-cap per Unique row; Common rows read as buildable-on-cap-grounds | `WonderPolicy.ExistenceCapFor` numbers via the catalog/slot wire (Phase 4A.3/4B backend-reads task — §Design 7); tuning file owns the numbers | "N of cap raised" line on every capped row (owner-locked — the fold MUST render them, ideal §8); `Common` never renders a painted-full gauge (GG-64) |
| Slot compatibility: open plots of the held sector, legal role/slot pairs only | `SlotView` (+ Wonder facet when `wonder-display`'s wire lands); `_plan.json` legal pairs consumed | Slot pick list (`SlotRow` states, consumed); incompatible slots name why (GG-55) |
| Affordability: sector-store stone/ironwork vs row cost; relic count vs `RelicCost` | Material costs on the structure rows; sector stores via the normal sector read | Cost-plate payload (§Design 4); confirm disabled with reason until affordable AND `k == N` relics picked |
| Locked teasers: reserved scopes (`World`/`Multiverse`) + reserved kinds (`DefensePower`/`AuraGrant`/`EmpireBuff`) as peers with reason | Closed vocabularies (`WonderCatalog.cs:8-60`, consumed); packs carry the "not yet" slot (ideal §8) | Locked rows with reason (GG-17/GG-44); never buildable, never a promise of a date |

Fold prohibitions: no per-mille rendered bare (GG-46 — *"this ground earns +X loam a night"* /
*"every holding earns …"*, formatted by unit family, never invented); no id-words (GG-23/GG-62 —
no `RelicCost`, `WonderScope`, `ExistenceCapFor`, dotted ids, raw reason strings anywhere in
payloads bound to player text); no second palette / second shell / second density ladder (GG-29).

### 3. Bus — closed `wonder-composer.*` vocabulary

One closed bus (sibling of `derivedSurfaceBus` / `conditionSurfaceBus` via `createSurfaceBus`,
e.g. `wonderComposerBus` — name locked at build, vocabulary locked here). No other module emits
these events; no handler outside the composer recipe consumes them.

| Event | Payload | Effect |
|---|---|---|
| `wonder-composer.search.set` | `{ text }` | Filters catalog + candidate rows (via shared `tool-search`) |
| `wonder-composer.wonder.select` | `{ structureId }` | Selects the Wonder row; re-computes needed-relic count, cap line, cost-plate, slot filter; locked-teaser ids refuse with reason (no select) |
| `wonder-composer.relic.toggle` | `{ instanceId }` | Toggles one reachable candidate into/out of the foundation set; refuses over-`N` picks with the count line (never silently drops) |
| `wonder-composer.slot.select` | `{ slotIndex }` | Picks the open plot; incompatible slots are unpickable-with-reason, never silently hidden |
| `wonder-composer.confirm` | — | Opens the band-3 spend confirm (names exactly what leaves: N relic instances + materials); on accept files via `PendingOrder.relicInstanceIds` → `useSubmitWorldCommands` (`wonder-rest` shape) and paints GG-15 pending ("order filed — resolves at End Turn") |
| `wonder-composer.retry` | — | Retries a failed sector/reachability read from `phase-error` |

Filing acknowledgement is instant (within a frame); slot, stocks, and relics change only when the
turn commit confirms (GG-15/GG-54). A reversal (filed, then refused at commit) is shown and
explained in player words via the refusal fold (§Design 5), never silently snapped back.

### 4. Cost-plate — `wonder-cost-plate` (one piece contract, comparable by default)

The cost-plate is the composer's decision surface (ideal §5 module `wonder-cost-plate`, Real-gap
bucket): one row that keeps the whole price comparable (GG-47) — relic foundation + materials +
time — before the confirm.

| Cost-plate line | Fold source | Player words (catalog-owned, §Design 6) |
|---|---|---|
| Relic foundation | `k of N` picked vs `RelicCost` (row magnitudes) | "Laid into the foundation: k of N pieces of treasure" — each picked instance linked to its authoritative card (GG-9), never re-implemented |
| Stone + ironwork | `constructRubbleCost` / `constructIronworkCost` vs this sector's stores | "From this ground's own stores: X stone, Y ironwork (have H)" — shortfall names the blocker + next action (fetch/store), never a bare number |
| Nights | `buildTurns` | "Rises over N nights" (construction takes nights on the virtual-turn clock — ideal §1) |
| Blessing reading | Effect magnitude via the display catalog | *"this ground earns +X loam a night"* (Sector) / *"every holding earns …"* (Empire) — attributable ledger rows join later via `wonder-display`; the plate shows the reading, never the per-mille |
| Upkeep note | `wonder-effect-empire` upkeep term | Opportunity-cost line (nights + upkeep), never just the prize (ideal §6 Civ5 production-sink trap) |

Density reuse: `stock-row` for candidate/cost rows, `capacity-meter`/`value-hero`/`gauge-*` for the
effect hero — all consumed from the shared kit by name (ideal §5 reuse map). Icons, progress, and
motion come from the locked stack (`lucide-react`, motion) via kit pieces — never four bespoke SVGs
(buy-before-build; GG-38: split the chunk, never ban the library).

### 5. Refusal fold — all four reasons, each with copy + next action, nothing consumed

One fold mapping (sibling of the composer fold, e.g. `wonderRefusalVm` — name locked at build)
translating every wire token to authored player copy from the display catalog (§Design 6). Toasts
are band-4 (GG-16); the spend confirm's own refusal path reuses the same mapping. The Civ6
"production salvaged" precedent (ideal §6) is the bar: every refusal names what was *not* taken and
the next action.

| Wire token (owner: backend) | Player copy shape (catalog-owned) | Next action |
|---|---|---|
| `wonder.cap-reached` | "This land already holds all it can — N of cap raised." (live counts, owner-locked) | Points at the capped scope-unit (this sector / the empire roster); offers the other Wonder row if buildable |
| `relic.count-mismatch` | "The foundation asks for exactly N pieces of treasure — k are laid." (covers wrong count incl. null-vs-needed; blank/whitespace ids are mismatch, never cleaned — `spec-wonder-rest.md` §Design 2) | Returns to the shelf with the shortfall highlighted; over-picks refuse with the same line |
| `relic.not-reachable` | "That treasure isn't here — it sits with [band / sector store], not where the work would rise." | Names where each missing piece sits (where-it-sits join) + the move that would bring it in reach (fetch/deposit verb owned by the inventory program) |
| `build.cannot-afford-materials` | "The stores are short — need X stone / Y ironwork, hold H." | Points at the sector store + the earn/fetch path; confirm stays disabled-with-reason (GG-55) |

Refusal rules: raw tokens never render (GG-23); nothing owned is taken on any refusal (the player
sentence, ideal §3); a per-command refusal never throws away the rest of the turn's batch
(`WorldEndpoints.cs:123-126` partial-acceptance comment, consumed via `spec-wonder-rest.md`).
Refusal-path probes (wrong count, unreachable id, over cap) are this fold's acceptance alongside the
composer — named in `spec-wonder-rest.md` §Design 4 as `wonder-composer`/`wonder-refusal` acceptance,
not `wonder-rest`'s.

### 6. themeRefs + display-catalog rows owed (designed here, authored at build)

Pieces declare slots only; these contracts are what the build fills. **No pack or catalog file is
written by this spec** — the rows below are the owed authoring list the wave-2 build completes
before React mounts (ideal §8; `wonder-display` co-consumes the same catalog).

themeRefs (payload fields, paint lives in packs, never in feature code):

- `wonder-scope`: `Sector` vs `Empire` + reserved (`World`/`Multiverse` "not yet" slot) — `css` +
  `paint` hex + optional `vfx` (GG-32 reduced-motion).
- `wonder-rarity`: `Common` vs `Unique` — same contract shape.
- Construction-state `vfx` for the under-construction reading (the gradual-state seed,
  `SlotRow.tsx:55-59`, grows Wonder identity at build via `wonder-display`).

Display catalog rows owed (new runtime display catalog, GG-62 authored lexicon — T7/T8 sibling of
number files, never mixed into balance numbers; spec-time decision at build: new file vs extending
an existing display catalog):

- Wonder display names + one-line effect readings for `standing-stones` + `sunspire-throne`
  (rows supply provisional identity; catalog owns the player words the composer renders).
- Scope readings (Sector/Empire) + rarity readings (Common/Unique) + locked-teaser reasons for all
  four reserved members (`World`/`Multiverse`, `DefensePower`/`AuraGrant`/`EmpireBuff`).
- All four refusal copies + next actions (§Design 5) + cap-count sentence shape ("N of cap raised").
- Unknown ids fall to a designed placeholder, never id-words. Effect readings for reserved kinds:
  later, when their wave ships (ideal §10 Q5 recommendation, consumed).

### 7. Backend-reads dependency note (owed to Phase 4A.3/4B, not this module)

The composer renders live data it cannot yet read — correctly deferred, named here so the build is
not mistaken for unblocked (ideal §9.7; `spec-wonder-rest.md` §Boundaries;
`spec-wonder-content.md` §Design 5):

- Reachable-first picking needs a REST reachability read (only `ListClaimableCachesUnlocked`
  in-process exists today).
- Live cap counts need `WonderScope`/`WonderRarity`/`RelicCost`/cap fields on the catalog/slot wire
  (`WorldStructureDto`/`SlotView` carry none today — `gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895`).
- Locked teasers need the scope metadata the catalog exposes.

Until that task lands, the fold's reachability/cap joins have no wire to bind — the recipe, bus,
fold shape, catalog rows, and drafts in this spec are still the build's locked input; the build
binds them to the new reads when they land. This module builds no wire, no adapter, and no fold for
those reads.

### 8. Drafts — owner-accept gate (HTML/description, NO React)

Per idea-ui §1, drafts precede React and the owner accepts them before any mount. The wave-2 build
produces, at minimum, these draft states (each: one HTML draft under
`docs/design/gui-lego/pieces/` or `recipes/` convention + one-paragraph description of what varies):

1. Catalog with price-first rows + live cap lines + one locked teaser peer.
2. Reachable-first shelf: reachable group picked (`k of N`), full shelf behind one disclosure.
3. Cost-plate: materials + relic price + nights + blessing reading, affordable vs shortfall.
4. Confirm dialog (band-3): names exactly what leaves.
5. Refusal toasts (band-4): one per reason, each with next action.
6. Lifecycle: empty shelf, locked tier, failed sector read (+ retry), GG-15 pending.

Draft copy is provisional catalog text (amended into the design SSOT before ship — never stub copy
shipped as product, idea-ui §1). Owner accept of these drafts is the gate to the React mount.

## Tunables

None in this module. This spec introduces zero tunable numbers — no cost, no cap, no rate, no
threshold. Every number the composer shows is owned elsewhere:

| Number the composer shows | Actual home (not this module) |
|---|---|
| `RelicCost` per Wonder row | Seed corpus (`gk-data/packs/fusion/data/seed/structures/wonder/**`), via `wonder-content` |
| `UniqueExistenceCap.Sector` / `.Empire` | `gk-core/data/tuning/loam-relics-wonders.v1.json`, read via `WonderPolicy.ExistenceCapFor` |
| Material costs, `buildTurns`, effect `valueMilli` | Structure rows (provisional seed content, balance-owned) |
| Refusal-threshold copy, names, readings, scope/rarity paint | Display catalog + theme packs (§Design 6 — authored content, never balance numbers) |

A balance-shaped literal appearing in the wave-2 diff is a review failure
(`spec-wonder-rest.md` Locked anchors, consumed).

## Numeric types

No new magnitudes. Counts shown (`k of N`, "N of cap raised") are `long`-backed integers formatted
by the fold (GG-46 unit families); the fold invents none. No `f(level)`, no per-mille math in the
composer (effect per-mille is formatted to player words, never computed here). No progression
ceiling: caps render as data (`ExistenceCapFor` readings), never as painted-full gauges on uncapped
magnitudes (GG-64); `Common` is uncapped in code (`long.MaxValue`) and renders as
buildable-on-cap-grounds.

## Commands

```powershell
# web (gk-web/web/fusion-rpg-web) — wave-2 build verification (this spec itself runs no suite):
npm test -- wonderComposer   # fold: reachable-first join, cap lines, affordability, refusal mapping
npm run build                # tsc --noEmit + vite build — type errors fail the build
python gk-core/scripts/guard-dal.py      # no new SQL in this module — must stay green
```

Idea phase runs no suite — no test movement claimed by this spec (ideal Hand-off checklist,
consumed). The wave-2 build verifies with the scoped `verify-change.py -Paths <files>` boundary
for the recipe/fold/bus/draft files it touches.

## Structure

```
docs/design/gui-lego/recipes/wonder-composer.json   NEW (wave-2 build) — §Design 1 slot tree
docs/design/gui-lego/pieces/wonder-*.html           NEW (wave-2 build) — §Design 8 drafts (HTML)
<display catalog>                                   EXTENDED-or-NEW (wave-2 build) — §Design 6 rows
                                                     (spec-time decision: new file vs extending)
<wonder-scope-* / wonder-rarity-* packs>            NEW (wave-2 build, with wonder-display) — §Design 6
web/.../features/gui-lego/foldWonderComposerVm.*    NEW (wave-2 build) — §Design 2 (+ refusal fold §Design 5)
web/.../features/gui-lego/wonderComposerBus.*       NEW (wave-2 build) — §Design 3
web/.../stages/world/worldSelection.ts              CONSUMED (wonder-rest shape) — file path, never re-spec'd
tasks/sessions/<session>.json                       boundary record (this spec's own session)
UNTOUCHED: WorldCommand.cs, WorldCommandAdmission.cs, BuildResolver.cs, RpgStore.WonderBuild.cs,
           RpgStore.WorldTurns.cs, WorldDtos.cs, WorldEndpoints.cs, bus/world.ts, StructureCatalog.cs,
           StructureCorpus.cs, WonderCatalog.cs, gk-data/packs/fusion/data/seed/structures/**, gk-core/data/tuning/**,
           SlotRow.tsx, SectorInspector.tsx, RelicsLayer.tsx, every shared piece/fold/bus/pack,
           menu-refactor-queue.md (build adds the row)
```

## Code style

Recipe JSON follows the `derived-console.json` / `shield-console.json` composition grammar
(`docs/design/gui-lego/recipes/`): slots bind pieces by id, lifecycle overlays bind `vm.phasePayload`,
structural CSS per recipe. Bus follows the `createSurfaceBus` closed-vocabulary shape
(`features/gui-lego/*SurfaceBus.ts`): one event per player action, payloads named above. Fold
follows the `foldDerivedSurfaceVm` / `foldConditionSurfaceVm` pure-function shape: world/Game state
in, payloads + `themeRef`s out — no fetch in pieces, no paint in the fold, no copy invented outside
the catalog. No React code in this spec or its drafts — drafts stop at HTML/description per idea-ui.

## Testing strategy (wave-2 build acceptance)

- **Reachable-first join:** candidates from the legion cargo tab + sector store sort above the full
  shelf; picking is order-preserving; over-`N` picks refuse with the count line (never silently
  dropped).
- **Live counts:** capped rows render "N of cap raised" from `WonderPolicy` numbers (tuning change
  moves the line with no code change); `Common` renders buildable-on-cap-grounds, never a gauge.
- **Affordability gate:** confirm disabled-with-reason until affordable AND `k == N`; shortfalls name
  blocker + next action (GG-55).
- **Refusal mapping:** each of the four wire tokens renders its catalog copy + next action; raw
  tokens never render; nothing consumed on any refusal (read back through the normal path).
- **File path:** the accepted pick files as `relicInstanceIds` through `PendingOrder` →
  `toRequests` → `useSubmitWorldCommands` unchanged (round-trip test, `wonder-rest` harness reused).
- **No closed-vocabulary drift:** scope/rarity/effect readings assert enum membership (closed
  vocabularies, owned — state the reason), never corpus sizes, item totals, or authored
  name/description strings (validation-ssot). Locked-teaser ids are unpickable-with-reason.
- **Not covered here:** reachability/cap wire fields themselves (Phase 4A.3/4B task); sector-card
  construction-progress + ledger rows (`wonder-display`); reserved-kind effect promises (later wave).

## Boundaries

- **Always:** panel over the stage (never a route); reachable-first with the full shelf one
  disclosure away; live counts rendered; locked teasers as peers; price-first rows; confirm names
  what leaves; every refusal names blocker + next action with nothing consumed; GG-15 pending on
  file; GG-9 link to the authoritative relic card.
- **Ask first:** a third Wonder row reaching the composer (proves demand — `wonder-content`
  boundary, consumed); giving the structures generator Wonder support (generator-program decision);
  registering any reserved scope/kind as live (needs its named prerequisite work first); a second
  composer bus or a parallel relic-list wire shape (SOLID forks — extend, never duplicate).
- **Never:** backend changes (engine/admission/spend/store/DTO/endpoint/catalog are built or
  other modules'); seed or tuning edits (rows + numbers are `wonder-content`'s + balance's);
  re-specifying shared pieces (`tool-search`, `chip`, `split-inspect`, `scroll-region`, `phase-*`,
  `stock-row`, `capacity-meter`, shelf, relic card — consumed by name); hard-coded scope/rarity
  paint; raw tokens or ids on the surface; a god `BuildWonderPanel.tsx`; a new top-level route; a
  second debug surface re-implementing these endpoints; React code before owner-accepted drafts.

## Success criteria

1. Recipe, fold slices, closed bus, cost-plate contract, refusal mapping, themeRefs, catalog rows
   owed, and draft list are all named here with no open presentation decision left for the build —
   verifiable by a reviewer checking each named artifact exists in §§Design 1–8 (a missing artifact
   fails this criterion, no judgment call).
2. The picked list the composer files consumes `wonder-rest`'s locked shape by name with no further
   wire work.
3. Both `wonder-content` rows are readable by the recipe (names, counts, scope/rarity) with no seed
   edit.
4. Owner accepts the §Design 8 HTML drafts — the gate to the wave-2 React mount.
5. `guard-dal.py` green (no new SQL). 6. Zero changes to backend, seed, tuning, shared pieces, or
   hosts beyond binding them.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `wonder-composer` recipe + `wonder-composer.*` bus + fold slices (§Design 1–3) | Wave-2 UI build — mounts recipe, implements fold/bus, binds Phase 4A.3/4B reads; no further design |
| `wonder-cost-plate` contract (§Design 4) | Wave-2 UI build — the price piece; `wonder-display` reuses its affordability readings |
| Refusal fold + four-reason mapping (§Design 5) | Wave-2 UI build; `wonder-display` + turn-report surfaces reuse the mapping for commit-time reversals |
| Display-catalog rows + pack refs owed (§Design 6) | `wonder-display` (module 4) — co-consumes the same catalog/packs for sector-card identity |
| Backend-reads gap (§Design 7) | Phase 4A.3/4B backend-reads task — must land before the build can bind live counts/reachability |

## Design-gate checklist

```
[x] Subsystems: world-stage composer presentation (FE Lego recipe/fold/bus) + Wonder build contract
    (read-only refs). No Status/ActorHub/Combat, no engine behavior change.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
[x] Read this session: empire-wonder-surfaces/spec-wonder-rest.md (full: four-file pass-through,
    request shape, wave-2 composer contract); spec-wonder-content.md (full: Sector/Common +
    Empire/Unique rows, authored path); empire-wonder-surfaces-map.md (module 3 row);
    empire-wonder-surfaces-ideal.md (full: §5 composer/cost-plate/refusal rows, §7 chosen,
    §8 catalog/packs, §9.7 backend-reads note, Owner resolutions: panel, reachable-first,
    show-counts, locked-teasers; shared pieces consumed); idea-ui-phase.md (full: authoring order
    queue→recipe→fold+bus→themeRefs→drafts→owner accept→mount); DESIGN-GATE.md (§1 UI + menu rows,
    §2 invariants, §5 checklist).
[x] Checked decisions.md: Loam relics and wonders SSOT + Scoped inventory hierarchy SSOT + GUI Lego
    rows — composer direction (panel, reachable-first, counts, teasers, shared-piece ownership)
    confirmed, no re-decision.
[x] Every factual claim cites file:line, verified against CODE this session:
    worldSelection.ts (:28-46 PendingOrder, :106-118 toRequests), bus/world.ts (:277-295 mirror,
    :549-554 submit, :560-571 commit), SlotRow.tsx (:4-37 states, :49-78 sentences),
    SectorInspector.tsx (:1-60 host), features/gui-lego/ (pieceRegistry, createSurfaceBus,
    *SurfaceBus, folds), ui/gui-lego/ (RecipeMount, pieces incl. domain/chrome/layout/lifecycle),
    design/gui-lego/README.md (tool-search, chip, split-inspect, scroll-region, phase-* inventory +
    reuse matrix), WonderCatalog.cs vocabularies + BuildResolver.cs refusal strings (via wave-1 specs'
    this-session-verified readings, re-confirmed by location here).
[x] Read the surrounding section of every rule quoted (GG-1 stage/layers, GG-9 one home, GG-15
    acknowledge/authority, GG-22 destructive confirm, GG-23 player vocabulary, GG-46 numbers with
    meaning, GG-47 comparable, GG-55 disabled-with-reason, GG-62 authored names, GG-63 in-pane
    readings; endpoint partial-acceptance; live-probe RPG-server-debug scope for the build's later
    proof).
[x] Tested constraints: none claimed — no "moves goldens" / "needs sign-off" asserted. Suite
    selection stated in Commands; drafts-accept gate stated as not yet run (said so).
[x] No §2 invariant contradicted: SQL only in FusionRpg.Data (no new SQL); no cap on a magnitude
    (caps render as data, Common uncapped — GG-64); no f(Θ); no second ActorHub composer; no second
    ownership root (reachability joined, never re-owned); no generated-data hand-edit (no seed
    touched); no second shell/kit/palette; no parallel relic path (extends the one wire shape).
[x] Corrections propagated: prose + Structure + Testing + Boundaries + Interface agree on the
    recipe/fold/bus/catalog/pack set and the non-touch list (no backend change, no shared-piece
    re-spec).
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. Refusal strings, scope/rarity/effect kinds, and cap-count shapes are closed
    vocabularies owned by the backend/catalog, with reasons stated (validation-ssot).
[x] No event-refreshed cache introduced or touched.
[x] No acceptance criterion fixes a silently-ordered execution: filing/pending/commit/refusal are
    state transitions (filed → pending → confirmed-or-refused), asserted order-independent where
    both orders are reachable.
[x] No actor combat/derived magnitude produced or consumed.
[x] No SOLID-violating parallel path: consumes the one wire shape, the one relic shelf, the one kit
    (recipe + pieces + packs) — links (GG-9), never duplicates.
[ ] Owner accept of §Design 8 drafts — correctly deferred to the wave-2 build gate, named here, not
    assumed done.
[ ] Phase 4A.3/4B backend reads (reachability + catalog/slot Wonder facets) — correctly deferred,
    named in §Design 7, not assumed solved.
[ ] Full display-copy catalog + scope/rarity packs authored — wave-2 build deliverable, owed rows
    listed in §Design 6, seeded here only with shapes.
```

(End of file)

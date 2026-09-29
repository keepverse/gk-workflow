# Spec: `wonder-display`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`; main checkout untouched. Module id
`wonder-display`, row 4 of the [empire-wonder-surfaces map](../empire-wonder-surfaces-map.md)
(wave 2 — depends on `wonder-content` for rows; consumes shared meter/row from the inventory
program by name). Ideal: [empire-wonder-surfaces-ideal.md](../empire-wonder-surfaces-ideal.md)
(§5 sector-card/packs rows, §7 chosen shape, §8 display catalog + packs, §9.7 backend-reads note,
§10 Q1–Q4 answered + Owner resolutions). Sibling specs consumed exactly:
[spec-wonder-content.md](spec-wonder-content.md) (both rows),
[spec-wonder-rest.md](spec-wonder-rest.md) (wire shape, refusal vocabulary). House style precedent:
[scoped-inventory-hierarchy/spec-legion-cargo.md](../scoped-inventory-hierarchy/spec-legion-cargo.md),
adapted for UI (Locked anchors + checklist mandatory).

## Objective

Give a held sector's Wonder a readable face: a sector-card recipe (identity + effect +
construction-progress) that turns the mounted `SlotRow` id-sentence into an authored Wonder reading;
two theme-pack contracts (`wonder-scope`, `wonder-rarity`) that own all scope/rarity paint including
the reserved-tier "not yet" slot; and a display catalog owning every Wonder name, scope/rarity
reading, effect sentence, and refusal copy + next action — with an unknown-id placeholder rule so no
raw id ever reaches the player. This module presents readings only: it authors no backend behavior,
no numbers, no wire fields — the wire fields it needs are named in §Design 5 as Phase 4A.3/4B
blockers, not assumed solved.

Success looks like: a sector holding `standing-stones` renders its authored name, its scope/rarity
badges in pack paint, its effect sentence, and (while rising) nights-left progress — never
`"Rootbed — standing-stones."`; a `sunspire-throne` card renders the Empire reading plus the live
cap line; a `World`-scope row renders as a locked teaser with a reason, never as buildable; and an
unknown `structureId` renders the designed placeholder, never the id.

## Locked anchors

- **Shared pieces are consumed by name, never re-specified here** (map assumption 1;
  ideal §5 reuse map). `capacity-meter` and `stock-row` are owned by the sibling inventory program
  (owner confirms ownership at `/spec` gate); the treasure shelf is owned by the sibling inventory
  ideal (`wonder-relic-shelf` row). This spec names the consumption points (§Design 4) and designs
  nothing they own. A second meter/row/shelf beside the shared ones is a SOLID fork — fail review.
- **Owner resolutions (ideal doc, 2026-09-15) bind this module:** composer is a band-2 panel (not
  this module's surface, but the card links into it); relic picking is reachable-first (legion sheet
  cargo tab + sector store); **live cap counts are shown — the fold MUST render them, not
  either-way** (so §Design 5 names the exact wire fields as blockers); reserved tiers render as
  locked teasers with the packs carrying the "not yet" slot (ideal §8, §9.4).
- **Paint belongs to theme packs, not to Wonder code** (ideal §0.4). No hard-coded scope/rarity
  colour map inside any piece — the `element-badge` precedent (paint SSOT, mute twin forbidden)
  applies verbatim: pieces declare slots only; `wonder-scope-*` / `wonder-rarity-*` packs own `css`
  + `paint` hex + optional `vfx`.
- **Names are authored, never ids** (GG-23, GG-62). `SlotRow.tsx:54`'s
  `` `${slot.slotTypeId} — ${slot.structureId}.` `` is the standing defect this module fixes: a
  Wonder row rendering as its seed id. The display catalog (§Design 3) is the only source of Wonder
  names; the card reads the catalog, never `structureId`.
- **Reads `wonder-content` rows by name, never re-authors them.** `standing-stones`
  (`Sector`/`Common`, `LoamGenerationRate`/`Sector`) and `sunspire-throne` (`Empire`/`Unique`,
  `LoamGenerationRate`/`Empire`) are this card's content dependency (content spec §Interface). This
  module adds no seed row, edits no shipped row, touches no tuning number.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Seven-state slot row machine (built vs under-construction with nights-to-build) exists and is mounted | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SlotRow.tsx:4-37` (states at `:4-11`, construction read at `:28-34`), sentence render at `:49-78` |
| Built-state sentence prints the raw structure id — the GG-23/GG-62 defect this module fixes | `SlotRow.tsx:54` (`"${slot.slotTypeId} — ${slot.structureId}."`); under-construction variant at `:55-59` appends turns-to-build to the same raw id |
| Construction progress wire is known straight off the wire, never permanently Pending | `gk-web/web/fusion-rpg-web/src/contract/adapt.ts:499-518` (W62 note at `:499-505`, `adaptWorldSlot` at `:506-518`); `contract/types.ts:863-873` (`SlotView`, `constructionTurnsRemaining: Pending<number \| null>` at `:872`) |
| `SlotView` carries exactly nine fields and no Wonder facet: `slotIndex/slotTypeId/element/state/ownerFactionId/guardWaveId/guardState/structureId/constructionTurnsRemaining` | `contract/types.ts:863-873` (all nine read in full this session) |
| Sector loam block with attributable upkeep ledger — the pattern Wonder rows must join | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorLoamBlock.tsx:1-38` (Earns/Costs/Net/In store at `:17-34`); upkeep breakdown adapter at `contract/adapt.ts:447-454` (four rows: base/garrison/development/danger) |
| `ModifierLedger` reads four rows straight off the wire, never re-derived; row keys are a closed 4-member union | `gk-web/web/fusion-rpg-web/src/ui/world/ModifierLedger.tsx:21-26` (`ROW_LABELS`), `:80-90` (pending/known); `modifierLedgerMath.ts:19-31` (`ModifierLedgerRowKey = "base" \| "garrison" \| "development" \| "danger"`) |
| Catalog wire (`WorldStructureDto`) carries `StructureId/Name/Kind/RequiredSlotKind/Cost/YieldMultiplierMilli/BuildTurns/CapacityBonus/ObstacleKind/MaterialTier` — and no Wonder field | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:363-393`, read in full this session |
| Slot wire (`WorldSlotDto`) carries `SlotIndex/SlotTypeId/Element/State/OwnerFactionId/GuardWaveId/GuardState/StructureId/ConstructionTurnsRemaining` — and no Wonder field | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:47-78`, read in full this session |
| Refusal vocabulary exists server-side with stable reason strings; zero FE handlers exist | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:102-132` (`relic.not-reachable`, `wonder.cap-reached`, `build.cannot-afford-materials`); `WorldCommandAdmission.cs:112-119` (`relic.count-mismatch`, `relic.duplicate` — rest spec §What already exists); ideal §4 confirms the web-wide grep returns only a "wondering" comment false positive |
| Theme-pack kit exists with a fixed shape (`themeId/kind/id/css/paint/vfx/glyphDefault`) — no `wonder-*` pack exists | `docs/design/gui-lego/themes/packs/element-fire.json:1-20` (shape precedent); packs-dir listing this session: element-*, status-category-*, resource-*, side-*, action-category-*, bucket-*, cook-tab-*, neutral, posture-* — no wonder-* |
| Release-ground confirm shows construction cost in player words ("N nights of building lost") — the tone precedent for progress copy | `gk-web/web/fusion-rpg-web/src/stages/world/confirms/ReleaseGroundDialog.tsx:89-91` (per ideal §4) |
| Content rows this card reads: `standing-stones` (Sector/Common) + `sunspire-throne` (Empire/Unique) | `spec-wonder-content.md` §Design 1–2; legal pairs `Extract`→`Rootbed`, `Bank`→`Shrine` |

### Wiring gap (machinery exists but the Wonder path doesn't use it)

| Gap | The inert/underused line |
|---|---|
| Slot rows print the raw `structureId` with no Wonder identity: no scope/rarity/effect reading, no themed badge | `SlotRow.tsx:49-78` renders sentences from `SlotView` only; `SlotView` carries no Wonder facet (`gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895`) |
| Sector loam upkeep ledger has exactly four rows; the Empire-scope Wonder upkeep term has no row and no wire field reaching the adapter | `SectorLoamBlock.tsx:22-26` + `adapt.ts:447-454`; backend term is `wonder-effect-empire` §Design 6 (per ideal §4) |
| Sector production figure carries no attributable Wonder contribution | `SectorLoamBlock.tsx:17-20` reads `sector.loam.production` alone |
| Theme packs cover element/status/resource/side/action-category/neutral/bucket/cook-tab/posture — no `wonder-scope` / `wonder-rarity` pack exists | packs-dir listing (this session) |

### Real gap (no shareable piece/pack/recipe path exists yet)

| Gap | What this module builds |
|---|---|
| No Wonder identity piece (scope/rarity/effect presentation) and no scope/rarity theme packs | §Design 1 (card recipe) + §Design 2 (two pack contracts) |
| No refusal-message catalog mapping the four wire reasons to authored player copy with next actions | §Design 3 (display catalog, refusal rows) |
| No Wonder display-name/reading catalog rows (GG-62: names and one-line effect readings authored, never generated from ids) | §Design 3 (display catalog, identity rows) |
| Reserved tiers (`World`/`Multiverse`, `DefensePower`/`AuraGrant`/`EmpireBuff`) have no presentation contract — not even a "not yet" state | §Design 2 ("not yet" slot) + §Design 3 (locked-teaser rows); locked by owner: locked-with-reason teasers |

## Design

### 1. Sector-card recipe — identity + effect + construction-progress

A `wonder-sector-card` recipe composed of small pieces plus a pure data fold plus a closed bus —
never one big component owning layout, paint, data-joining, and copy (ideal §0.3; the
`BuildWonderPanel.tsx` god-component is the named defect, §7 rejected).

**Slot tree** (recipe JSON owns the layout; changing IA = editing the recipe, not the TSX):

```
wonder-sector-card
├── identity        — authored name (catalog) + scope badge + rarity badge (packs, §Design 2)
├── effect-reading  — one-line effect sentence (catalog) + attributable ledger row join (§Design 4)
├── progress        — construction-progress sentence + meter (shared capacity-meter by name)
│                     built → no progress slot; under-construction → "rising, N nights left" + meter
└── locked-slot     — reserved-tier teaser (pack "not yet" paint + catalog reason copy), §Design 2–3
```

**Fold contract (pure data, no paint, no copy):** the fold takes the slot's `SlotView` +
catalog-wire Wonder facet (§Design 5 — blocked until the wire lands) + display catalog (§Design 3)
and returns one closed reading per card: `{ name, scope, rarity, effectSentence, progress, capLine?,
lockedReason? }`. Wire reason strings (`wonder.cap-reached`, `relic.count-mismatch`,
`relic.not-reachable`, `build.cannot-afford-materials`) are translated by the fold into catalog keys
— they never render raw (GG-23). Cap lines render `WonderPolicy` numbers through the fold
(`ExistenceCapFor` readings, ideal §8 — LOCKED: show live counts), never literals in prose or rows.

**Construction-progress rule:** the progress slot reuses the existing `constructionTurnsRemaining`
known-reading (`SlotRow.tsx:28-34`, `adapt.ts:506-518`) and the release-ground player-words tone
(`ReleaseGroundDialog.tsx:89-91`): under-construction renders the authored name + "rising — N
nights left" + the shared meter; built renders name + effect with no progress slot. The raw-id
sentence at `SlotRow.tsx:54,58` is replaced by the catalog name read — the id never renders.

**Closed bus** (e.g. `wonder-display.*`: `card.expand`, `reading.open`, `teaser.explain`, `retry`):
all card actions travel the bus; pieces never fetch. The card mounts inside the existing inspector
host (`SectorInspector` over the world stage — no new route, GG-1/GG-7; the "Wonders route" is the
named rejected shape, ideal §7).

### 2. Theme-pack contracts — `wonder-scope` / `wonder-rarity` + the "not yet" slot

Two new theme-pack kinds following the exact `element-fire.json` shape (`themeId/kind/id/css/paint/
vfx/glyphDefault`):

| Pack kind | Live members | Reserved ("not yet") members | Notes |
|---|---|---|---|
| `wonder-scope` | `Sector`, `Empire` | `World`, `Multiverse` | Whether a far-reaching Wonder reads as gold and a local one as stone lives here (ideal §0.4), never in piece code |
| `wonder-rarity` | `Common`, `Unique` | — (rarity has no reserved tier; the pack carries no invented member) | `Common` = uncapped by construction (`ExistenceCapFor` returns `long.MaxValue`); the pack never paints a cap gauge on it (GG-64) |

**Pack contract rules:**

- Pieces declare paint slots only. A hard-coded scope/rarity colour map inside a piece is a Lego
  violation, not taste (ideal §0.4 — the same rule that already forbids hard-coded element chips).
- Every pack member carries `css` + `paint` hex + optional `vfx` (GG-32 reduced-motion honored).
  Reserved members (`World`, `Multiverse`) carry a deliberately muted "not yet" treatment defined
  once in the pack contract — never an invented look per surface (ideal §8).
- Reserved tiers render as locked teasers with a reason (Owner resolution, ideal §8 + §9.4):
  the card shows the reserved scope badge in "not yet" paint + the catalog's locked-reason line
  (§Design 3) — never hidden, never buildable, never a per-surface improvisation.
- Design SSOT; re-copy to `features/gui-lego/themes/` per the gui-lego README §FE sync (ideal §8).
- No second palette / second shell / second density ladder (ideal §7 rejected): packs extend the
  existing kit; ERM rungs are reused, amended before any invented density.

### 3. Display catalog — names, readings, refusal copy + next actions, unknown-id rule

A new runtime display catalog (GG-62 authored lexicon; T7/T8 sibling of number files — never mixed
into balance numbers, ideal §8). Spec-time decision recorded here: **new file**
(`gk-data/packs/fusion/data/seed/display/wonder-display.v1.json` proposed; implementation confirms the path) rather than
extending an existing display catalog — Wonder copy (identity + refusal + teaser) is one closed
vocabulary owned by this program, and folding it into a sibling catalog would split ownership of
the same sentences across two programs.

**Identity rows** (seeded by `wonder-content`'s authored names; full copy authored at build time):

| Row key | Name source | Scope reading | Rarity reading | Effect sentence (player words) |
|---|---|---|---|---|
| `standing-stones` | content row `name: "Standing Stones"` | pack `wonder-scope.Sector` | pack `wonder-rarity.Common` | "this ground earns faster each night" (+ formatted magnitude via GG-46 unit families — the fold formats `wonder-effect-empire`/yield numbers, never invents them) |
| `sunspire-throne` | content row `name: "Sunspire Throne"` | pack `wonder-scope.Empire` | pack `wonder-rarity.Unique` | "every holding earns faster each night" + live cap line "N of cap raised" (fold-read `WonderPolicy` numbers — LOCKED shown) |

**Refusal rows** (one per wire reason; each names the blocker and the next action, and states that
nothing was taken — the Civ6 salvaged-amount precedent, ideal §6):

| Wire reason | Player copy (authored) | Next action |
|---|---|---|
| `wonder.cap-reached` | "this land already holds all it can" + live count ("N of cap raised") | pick another ground, or raise no further Wonders of this kind |
| `relic.count-mismatch` | "the foundation asks for N pieces of treasure; M were laid" | re-lay the exact count (composer re-opens with the recipe intact) |
| `relic.not-reachable` | "that treasure isn't here — it travels with [band/sector]" | move the treasure within reach (legion cargo tab / sector store) first |
| `build.cannot-afford-materials` | "the stores are short of stone and ironwork" | gather stores, or choose a lesser work |

All four reasons exist server-side (`BuildResolver.cs:102-132`,
`WorldCommandAdmission.cs:112-119`) with **zero** FE handlers today — this catalog plus the fold is
the first handler. Refusals surface as band-4 toasts (+ band-3 confirm for the spend, ideal §2);
filing acknowledges within a frame ("order filed — resolves at End Turn"), and a commit-time
reversal is shown and explained in player words, never silently snapped back (GG-15/GG-54).

**Locked-teaser rows** (reserved tiers): `World`/`Multiverse` scope and
`DefensePower`/`AuraGrant`/`EmpireBuff` kinds each get a catalog row carrying only a locked reason
("not yet sung into the world" or equivalent authored line) — never an effect promise (ideal §10
Q5 recommendation consumed: now for scope/rarity, later for effect kinds — effects imply promises).

**Unknown-id placeholder rule:** any `structureId` with no catalog row renders the designed
placeholder ("a work not yet named in the chronicle") + the `card.expand` reading action — never
the raw id, never id-words, never "see definitions" (GG-23). The placeholder is a closed-vocabulary
row in the same catalog, not a fallback string in piece code.

### 4. Shelf-consume by name

The treasure shelf (`wonder-relic-shelf`) is owned by the sibling inventory program (map assumption
1; ideal §5 row 4 + §10 Q7 recommendation consumed: the sibling inventory ideal owns `stock-row` +
`capacity-meter` + the relic shelf; this program consumes by name, GG-9). This module's consumption
points, named so the sibling spec can bind them:

- The sector card links to the authoritative relic card (GG-9: link, don't re-implement) — the
  `RelicRow`/`ItemCard`/`CompareView` home in `layers/relics/` stays the one home per concept.
- The card's relic-candidate density reuses shared `stock-row`; its progress/effect hero density
  reuses shared `capacity-meter` / `value-hero` / `gauge-*` — by name, as the ideal §5 reuse map
  already tabulates (`capacity-meter`: progress meter; `stock-row`: relic candidate rows).
- Reachable-first picking spans the legion sheet cargo tab + sector store (locked sibling
  direction, Owner resolutions); the where-it-sits truth depends on `scoped-inventory-hierarchy`
  (spec'd, unbuilt) — this module designs the card's reading contract, not the backend join
  (ideal §9.3).

### 5. Wire-field dependency table — EXACT missing fields owed by Phase 4A.3/4B (blockers)

The fold **REQUIRES** live counts (owner-locked: shown — ideal §8, Owner resolutions), so every
missing field below is a **blocker**, not an enhancement. None exists on the wire today (verified
fresh this session against `WorldDtos.cs:47-78` + `:363-393`, `gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895`,
`adapt.ts:447-454` + `:506-518`). Owned by plan Tasks 4A.3/4B (ideal §9.7), not by this module.

| # | Missing wire field | Lives on | Sourced from (server truth) | Card needs it for |
|---|---|---|---|---|
| 1 | `WonderScope` | catalog wire (`WorldStructureDto`) | `StructureDef.WonderScope` (`StructureCatalog.cs:206-227`) | scope badge + pack selection + Sector-vs-Empire reading |
| 2 | `WonderRarity` | catalog wire (`WorldStructureDto`) | `StructureDef.WonderRarity` (`StructureCatalog.cs:206-227`) | rarity badge + pack selection + Unique cap-line gating |
| 3 | `RelicCost` | catalog wire (`WorldStructureDto`) | `StructureDef.RelicCost` (`StructureCatalog.cs:220-226`) | recipe count line ("asks for N pieces of treasure") + mismatch copy |
| 4 | `ExistenceCap` (per scope+rarity, resolved via `WonderPolicy.ExistenceCapFor`) | catalog wire or dedicated cap read | `WonderPolicy` + `gk-core/data/tuning/loam-relics-wonders.v1.json` (`uniqueExistenceCap.sector`/`.empire`) | live cap line "N of cap raised" (LOCKED shown — without this the fold cannot render) |
| 5 | `LiveWonderCount` (built + under-construction per scope-unit, the N in "N of cap") | slot/sector wire or dedicated cap read | `WonderExistenceScan` (counts built **and** under-construction, per scope-unit) | live cap line numerator (LOCKED shown — without this the fold cannot render) |
| 6 | `WonderScope`/`WonderRarity` facet on the slot | slot wire (`WorldSlotDto` → `SlotView`) | catalog join at projection time (`WorldEndpoints.cs` slot projection) | card identity without a second fetch per slot |
| 7 | `WonderUpkeep` row operand | upkeep breakdown wire (`LoamUpkeepBreakdownDto` → `UpkeepBreakdownView`) | `wonder-effect-empire` §Design 6 term | fifth ledger row (adapter + type + ledger change together — the W62/W63 drift class, ideal §4) |
| 8 | `WonderProductionContribution` | sector loam wire (`SectorView.loam.production` expansion) | Empire-scope effect sum per faction (SUM rule) | attributable "Earns" expansion (GG-49 — no mystery delta) |
| 9 | Reachability read (REST) for reachable-first picking | new REST read (only `ListClaimableCachesUnlocked` in-process exists today) | `scoped-inventory-hierarchy` overlay API the sibling ideal specifies | treasure shelf + `relic.not-reachable` next-action accuracy |

Until 1–6 land, the card renders catalog identity from its local display catalog keyed by
`structureId` (names survive — they are authored here, not on the wire) but **cap lines render as
the designed pending state** (`phase-*` pending piece, GG-17), never a guessed number and never a
hidden row. Field 9 additionally gates composer picking accuracy; fields 7–8 gate ledger
attribution. This module builds no wire, no adapter, and no fold-number — it names the debt so the
plan can sequence it.

## Tunables

| Number | Home | Notes |
|---|---|---|
| Wonder display names, one-line effect readings, scope/rarity readings, refusal copy + next actions, locked reasons, unknown-id placeholder | New runtime display catalog (§Design 3 — GG-62 authored lexicon; T7/T8 sibling of number files) | Every Wonder row, both live scopes, all four refusal reasons, all reserved tiers need authored rows before React mounts |
| Scope paint + rarity paint + construction-state `vfx` (+ reserved "not yet" treatments) | New theme packs `wonder-scope-*` / `wonder-rarity-*` (§Design 2) | Pieces declare slots only; Design SSOT, re-copied to `features/gui-lego/themes/` |
| Refusal-threshold text ("N of cap raised") | Display catalog + fold reading `WonderPolicy` numbers | LOCKED shown — the fold MUST render live counts (Owner resolution) |
| Recipe slot trees (sector card slots, toast placement) | Recipe JSON (`docs/design/gui-lego/recipes/wonder-*.json` proposed) | Changing IA = editing the recipe, not the TSX; structural CSS (grid/flex, 720px-floor bounds GG-36/GG-61, internal scroll) per recipe |
| Backend numbers (`RelicCost`, existence caps, upkeep rate, `ValueMilli`) | Owned by the four backend specs + `wonder-content` rows | **Not this module's to tune.** The fold formats them (GG-46); it never invents them |

No progression ceiling is introduced: caps render as data (`ExistenceCapFor` readings), never as
painted-full gauges on uncapped magnitudes (GG-64); `Common` is explicitly uncapped.

## Numeric types

No new magnitude is introduced. The fold formats `long` per-mille (`ValueMilli`, upkeep operands)
through the GG-46 unit families with widen-before-multiply / divide-by-1000-last discipline;
`relicCost` counts are `long`; caps are `long` via `ExistenceCapFor`. No `f(level)` — nothing here
touches the power ladder. Floating-point needs none.

## Commands

```powershell
# web (gk-web/web/fusion-rpg-web):
npm test -- SlotRow            # seven-state machine incl. Wonder identity rows stays green
npm test -- ModifierLedger     # four rows unchanged until the fifth (Wonder upkeep) wire lands
npm run build                  # tsc --noEmit + vite build — type errors fail the build
```

```powershell
python gk-core/scripts/guard-dal.py        # no SQL in this module — green with zero new hits is the proof
```

No suite ran in this spec session (spec writes run no suite — idea/spec phase claims no test
movement; Commands above are implementation's verification, not this session's evidence).

## Structure

```
docs/architecture/empire-wonder-surfaces/spec-wonder-display.md   NEW — this file
docs/design/gui-lego/recipes/wonder-sector-card.json             NEW — §Design 1 slot tree (implementation)
docs/design/gui-lego/themes/packs/wonder-scope-*.json            NEW — §Design 2 scope pack (implementation)
docs/design/gui-lego/themes/packs/wonder-rarity-*.json           NEW — §Design 2 rarity pack (implementation)
gk-data/packs/fusion/data/seed/display/wonder-display.v1.json                         NEW — §Design 3 catalog (implementation; path to confirm)
UNTOUCHED: SlotRow.tsx; SectorLoamBlock.tsx; ModifierLedger.tsx; modifierLedgerMath.ts;
           contract/types.ts; contract/adapt.ts; WorldDtos.cs; WorldSlotDto; WorldStructureDto;
           gk-core/data/tuning/loam-relics-wonders.v1.json; gk-data/packs/fusion/data/seed/structures/**; packs/* (existing);
           RelicsLayer.tsx; stock-row / capacity-meter (sibling-owned).
```

## Code style

Recipe + fold + bus, mounted in existing hosts (ideal §7 chosen shape). Authoring order per idea-ui
§1: queue row → piece index → recipe → fold + bus → themeRefs → HTML drafts → owner accept → React
mount + landmark tests. New surfaces enter `menu-refactor-queue.md` as their own rows (sector
display second, composer first; never both in one stream — ideal §7).

```json
// pack member shape — identical keys to element-fire.json, new kinds only.
{ "themeId": "wonder-scope.sector", "kind": "wonder-scope", "id": "sector",
  "css": { "--piece-accent": "var(--wonder-sector)" },
  "paint": { "accent": "#…", "accentMuted": "#…", "onAccent": "#…" },
  "vfx": { "select": null, "idle": null }, "glyphDefault": "landmark" }
```

## Testing strategy

- **Identity over ids:** `standing-stones` and `sunspire-throne` slots render authored names +
  scope/rarity badges, never `"Rootbed — standing-stones."` (the `SlotRow.tsx:54` defect as
  regression test).
- **Progress:** under-construction Wonder slot renders name + "rising — N nights left" + shared
  meter off the `constructionTurnsRemaining` known-reading; built slot renders no progress slot.
- **Live counts (post-wire):** `Unique` card renders "N of cap raised" from `WonderPolicy` numbers;
  `Common` card renders no cap line (uncapped by construction). Pre-wire: pending state, never a
  guessed number.
- **Locked teasers:** `World`/`Multiverse` rows render "not yet" pack paint + catalog reason, never
  a build action.
- **Refusals:** each of the four wire reasons maps to its catalog copy + next action; nothing
  consumed on refusal (assert stocks/relics untouched).
- **Unknown id:** uncatalogued `structureId` renders the placeholder row, never the id.
- **No population-count or generated-text pins** (validation-ssot): assert closed-vocabulary
  membership (scope/rarity/effect-kind enums, refusal strings — state the reason), envelope/closure
  (every rendered Wonder has a catalog row or the placeholder; every wire reason has a refusal row),
  determinism, and structural bounds — never corpus sizes, item totals, or authored name literals.
- **Not covered here:** composer picking, shelf where-it-sits, spend atomicity, live probe —
  `wonder-composer` / `wonder-rest` acceptance, named so this card is not mistaken for covering them.

## Boundaries

- **Always:** recipe + fold + closed bus; paint in packs; copy in the catalog; shared meter/row/
  shelf consumed by name; wire reasons translated by the fold, never rendered raw; caps rendered
  from `WonderPolicy` numbers.
- **Ask first:** a third theme-pack kind (proves a paint dimension the two packs cannot carry);
  extending an existing display catalog instead of the new file (§Design 3 decision);
  authoring effect-kind display rows for reserved kinds (needs the §10 Q5 wave decision first).
- **Never:** a god `BuildWonderPanel.tsx`; hard-coded scope/rarity paint in piece code; a new
  top-level "Wonders" route; raw reason strings or structure ids on the player surface; a second
  palette/shell/density ladder; banning lucide/recharts/motion for chunk anxiety (split the chunk —
  GG-38); backend behavior or numbers; seed/tuning edits; wire/adapter/SQL work (Phase 4A.3/4B's
  problem, §Design 5); a second debug surface re-implementing these endpoints.

## Success criteria

1. Wonder slots render authored names + themed scope/rarity badges + effect sentences — zero raw
   ids on the surface. 2. Under-construction Wonders show rising progress; built Wonders show none.
   3. `Unique` cards show live cap counts (post-wire); `Common` cards show no cap line; pre-wire the
   fold shows the designed pending state. 4. Reserved tiers render as locked teasers with reasons.
   5. All four refusal reasons map to copy + next action with nothing consumed. 6. Unknown ids render
   the placeholder, never the id. 7. `guard-dal.py` green (no SQL). 8. Zero changes to engine,
   catalog/slot wire, seed corpus, tuning, or sibling-owned pieces.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `wonder-sector-card` recipe + fold reading contract (§Design 1) | `wonder-composer` (module 3) — the composer links the card's reading in-pane (GG-63), never re-implements identity |
| Display catalog copy keys (identity + refusal + teaser + placeholder rows) | `wonder-composer` / refusal toasts — same catalog, same sentences everywhere (one home per concept, GG-9) |
| Pack slot names (`wonder-scope.*`, `wonder-rarity.*` incl. "not yet") | Any future Wonder surface — paint by slot reference, never re-declared |
| Wire-field dependency table (§Design 5, blockers 1–9) | Phase 4A.3/4B backend-reads tasks — the exact fields owed before live counts / identity / attribution render |

## Design-gate checklist

```
[x] Subsystems: world-stage sector/legion presentation (FE Lego), Wonder backend contract
    (read-only refs). No Status/ActorHub/Combat touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
[x] Checked decisions.md direction via the ideal doc's own GUI Lego + Loam-relics SSOT rows
    (cited through empire-wonder-surfaces-ideal.md §0 + §7, read this session) — greenfield
    display confirmed; no "wonder display" lock contradicted.
[x] Read this session: empire-wonder-surfaces-map.md (full, module 4 row); ideal (full: §5
    sector-card/packs rows, §7 chosen, §8 packs + display catalog, §9.7 backend-reads note,
    §10 + Owner resolutions — live counts shown, locked teasers; shared meter/row consumed
    from inventory program); spec-wonder-content.md (full — both rows consumed as the card's
    content dependency); spec-wonder-rest.md (full — wire shape + refusal vocabulary);
    spec-legion-cargo.md (house style, full Objective/Locked-anchors/Boundaries/Interface +
    checklist shape); DESIGN-GATE.md (§1 UI + proving-live rows, §2 invariants, §5 checklist).
[x] Every factual claim cites file:line, verified against CODE opened fresh this session:
    SlotRow.tsx (:4-11 states, :28-34 construction read, :54 built id-sentence, :55-59
    under-construction sentence); SectorLoamBlock.tsx (:1-38, :17-34 figures, :22-26 ledger);
    ModifierLedger.tsx (:21-26 labels, :80-90 pending/known); modifierLedgerMath.ts (:19-31
    four-row closed union); contract/types.ts (:863-873 SlotView — nine fields, no Wonder
    facet); contract/adapt.ts (:447-454 four-row upkeep, :499-518 slot adapter);
    Contracts/WorldDtos.cs (:47-78 WorldSlotDto, :363-393 WorldStructureDto — no Wonder field
    on either); element-fire.json (:1-20 pack shape); packs dir listing (no wonder-*);
    ReleaseGroundDialog.tsx:89-91 (player-words progress tone, via ideal §4 — not re-opened,
    said so).
[x] Read the surrounding section of every rule quoted (slot-state derivation comment, W62
    adapter note, ModifierLedger GG-49 comment, WorldSlotDto/WorldStructureDto doc comments,
    pack shape file in full).
[x] Tested constraints: none claimed — no "moves goldens" / "needs sign-off" asserted. Suite
    selection stated in Commands; the wire gaps are named as blockers (said so in §Design 5).
[x] No §2 invariant contradicted: SQL only in FusionRpg.Data (no new SQL); no cap on a
    magnitude (Unique caps tunable via WonderPolicy, Common explicitly uncapped — GG-64);
    no f(Θ); no second ActorHub composer; no parallel relic/display path (consumes shared
    pieces by name); no second debug surface.
[x] Corrections propagated: prose + Structure + Testing + Boundaries + Interface agree on the
    recipe/packs/catalog change set, the sibling-owned non-touch list, and the nine wire
    blockers.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. Refusal strings + scope/rarity/effect kinds are closed vocabularies
    owned by admission/catalog code, with reasons stated (validation-ssot).
[x] No event-refreshed cache introduced or touched.
[x] No acceptance criterion fixes a silently-ordered execution: criteria assert readings/state
    (named, badged, counted, locked, placeholder), not an order.
[x] No actor combat/derived magnitude produced or consumed.
[x] Does not invent or extend a SOLID-violating parallel path: extends the mounted SlotRow /
    ModifierLedger seams, consumes the sibling shelf/meter/row by name, reuses the one build
    kind + one admission vocabulary from wonder-rest.
```

(End of file)

# Spec: `trade-lexicon`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 1, wave 1). Every `file:line` below was opened this session. Docs only; no
code is authorised by this file. House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Every trade surface shows goods, causes, reasons, answers, treaty kinds and access levels **in authored
player words**, never in ids. This module owns the one runtime catalog that holds those words, the guard
that keeps trade copy inside the generic strategy-genre vocabulary, and the playback rows that let the
world's one translation table read trade report lines.

Success looks like: a lost-goods line reads *"12 fire essence lost to raiders on the Ashfold road"*, not
`logistics.loss:hostile:12`; every token a provider publishes has exactly one catalog row; a new token
with no row fails a test, not a player.

## Locked anchors

- **Runtime catalog, never the number file** (tunables-ssot T8, [tunables-ssot.md](../../tunables-ssot.md)
  §1 "Runtime catalog" row: *"Never mixed into the number file for the same domain"*). Home
  `data/tuning/trade-catalog.v1.json` (new); numbers stay in `data/tuning/trade.v1.json` (new).
- **Player words are authored** (GG-62, [game-gui-principles.md](../../game-gui-principles.md) §14). A
  title-cased id is a developer fallback and is forbidden on a player band.
- **Reads, never defines, the token sets.** Loss causes (`stranded`, `hazard`, `hostile-presence`,
  `perishability`) and short reasons (`lane-capacity`, `no-path`, `contested`, `too-far`, `buffer-full`) are
  `logistics-flow` `logistics-facts`' closed sets ([spec-logistics-facts.md](../logistics-flow/spec-logistics-facts.md),
  *Closed token sets*; that spec drops the map's "destination full", which is waste, not a short reason); treaty kinds are
  `exchange` `treaty-vocabulary`'s; access levels are `exchange` `trade-access`'s; goods ids are the
  `exchange` `tradeable-goods` table joined to `sector-yield` `located-goods-registry`; the throttle
  answer vocabulary is `throttle-forecast`'s. This catalog has a row per member and adds none.
- **Vocabulary** (owner, trade-network-ideal §14b): *trade hub, warehouse, depot, trade route, caravan,
  supply line, treaty, tariff, embargo*; keep *legion, sector, clan*; "district" is never a building-slot
  term; no franchise-specific words. `ip-censor` is the release gate for names — no second name filter.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Authored labels beside a closed id set, the pattern to copy | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts:9-16` |
| One world translation table, not per-prefix handling | `gk-web/web/fusion-rpg-web/src/stages/world/playbackTable.ts:5-19` (header), rows below it |
| Magnitude rendering refuses a bare number | `gk-web/web/fusion-rpg-web/src/contract/types.ts:66-67`; exhaustive switch `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:59` |
| World catalog read hook (the delivery precedent for a host-injected catalog) | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:573` (`useWorldCatalog`) |

### Real gap

| Gap | This module builds |
|---|---|
| No trade token exists anywhere | The catalog and its loader, joined to each provider's set as that provider lands |
| No trade vocabulary guard | Design 3 |
| No playback rows for trade report lines | Design 4 (rows filed on world-stage `world-playback`) |
| `data/tuning/trade-catalog.v*.json` has no verification boundary | Design 5 |

## Design

### 1. The catalog file

```jsonc
// data/tuning/trade-catalog.v1.json (new) — runtime catalog, host-injected (T8); Core never reads it
{
  "schemaVersion": 1, "version": 1,
  "_meta": { "owner": "docs/architecture/trade-network/trade-surface/spec-trade-lexicon.md",
             "rebalance": "Never hand-edit. python gk-core/tools/tuning/publish.py trade-catalog <key>=<value>" },
  "goods":             { "<goodId>":   { "displayName": "...", "reading": "..." } },
  "structureRoles":    { "<roleId>":   { "displayName": "...", "reading": "..." } },  // trade hub, depot, warehouse
  "lossCauses":        { "<causeId>":  { "displayName": "...", "reading": "..." } },
  "shortReasons":      { "<reasonId>": { "displayName": "...", "reading": "..." } },
  "throttleKinds":     { "<kindId>":   { "displayName": "...", "reading": "..." } },  // halt, waste, strand, loss-alert
  "throttleAnswers":   { "<answerId>": { "displayName": "...", "reading": "..." } },
  "treatyKinds":       { "<kindId>":   { "displayName": "...", "reading": "..." } },
  "featureTiers":      { "<feature>.<tier>": { "reading": "..." } },  // round 4: what a tier unlocks ("Unlocks empire market orders"); the building NAME is the structure row's or variant's display name (trade-foundation sector-features §2), never repeated here
  "accessLevels":      { "<levelId>":  { "displayName": "...", "reading": "..." } }
}
```

Every family is a map keyed by the provider's wire id. `displayName` is a noun phrase; `reading` is one
line (GG-64: the reading lives in the inspector, the name leads). The host loads the file at boot next to
the other `*-catalog` files and serves it through the world catalog read; the web never hardcodes a
union of these ids (tunables-ssot T8).

### 2. Join closure, both directions

For each family whose provider has landed, a test joins the catalog to the provider's declared set:
every provider token has exactly one row, and no row names a token the provider does not declare. A
family whose provider has not landed ships **absent** from the file, not empty-with-placeholders, so the
join cannot pass vacuously on a stub. Goods join against the tradeable-goods table at test time; the
number of goods is a reading and is never asserted (validation-ssot).

### 3. The trade vocabulary guard

One guard test over the catalog's `displayName`/`reading` strings and every trade translator string
(`trade-notify`) and trade piece copy:

- **Fails on "district"** used as a structure, slot or building label (whole-word, case-insensitive; the
  only allowed use is none — the ideal bans it as a slot term and trade has no other use for it).
- **Fails on a raw id shape** (a dotted or kebab token such as `essence.fire`) in player copy (GG-62).
- **Franchise words are not re-listed here.** The ask on `ip-censor` is that its `scan` covers
  `data/tuning/trade-catalog.v*.json` and the trade translator files; a second avoid-list would drift
  from its registry.

### 4. Playback rows

Every trade report kind the providers write (`lane.cut`, `logistics.loss`, `logistics.strand`,
`logistics.overflow`, `logistics.short` from `logistics-facts`; the halt and banking lines from `sector-yield`; the exchange
and fleet lines as they land) gets one row in the world's one translation table, whose words come from
this catalog's families. **Sentence frames are chrome, not catalog** (audit 2026-09-20): the frame of a
report sentence (*"{qty} {good} lost to {cause} on {route}"*) is a Lingui ICU message in the playback row
and the trade translator, extracted by `npm run extract` (`docs/design/tech-stack.md` §4.1: chrome is
Lingui, content is served data); this catalog supplies only the nouns. The `reportPrefixes` family (a map
to message ids) is withdrawn — a data file naming Lingui ids couples the two text systems §4.1 keeps apart. The table belongs to world-stage `world-playback`
([spec-world-playback.md](../../world-stage/spec-world-playback.md) §1, §4); the rows are filed as an ask,
never added around it. If npc-story-events' typed-kind row lands first, trade lines adopt typed kinds and
the rows key on the kind instead.

### 4a. Slot display names — round 5 C4 (owner, 2026-09-20)

*"Rename the slots' display names; building names stay; ids unchanged"* ([decisions-round-4.md](../decisions-round-4.md)
R5-A C4, which closed exchange-map OQ-2 with its option (a)). Three words collided: the Trade tier-2
building "Market" with the `Market` slot, the Banking tier-3 building "Vault" with the `Vault` slot, and the
Trade tier-3 building "Exchange" with the ladder's code name ~~`StructureKind.Exchange`~~ — **round 6 C2
withdrew that member**, so the collision is gone at the source: no code name shares the building's word.

| Slot type id (unchanged) | Display name today | Round 5 display name | Evidence |
|---|---|---|---|
| `market` (`SlotKind.Market`) | "Market" | **"Market Square"** | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74` |
| `vault` (`SlotKind.Vault`) | "Vault" | **"Vault Site"** | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:72` |

- The words are the examples the owner's chosen option carried (exchange-map OQ-2 (a)); they describe
  **ground**, which is what a slot is, and neither is a building name. They are authored copy (GG-62) and
  go through `ip-censor` like every name.
- **Where the change lands — one ask, both slots (global audit m15).** The display name is the slot catalog's
  `Name` field (world-map program's file), not this catalog: a slot name is one field and the world stage
  already reads it. `exchange` `exchange-hub` §3 used to edit that field for the `market` slot while this
  module filed an ask for `vault` — two routes into one world-map file. **Resolved:** one ask (global audit
  X-14) covering both display names, filed here and referenced by `exchange-hub`, which no longer edits
  `SlotTypeCatalog.cs`. This module still does **not** duplicate slot names into `trade-catalog.v*.json`.
- **"Exchange" needs no rename.** No slot is called "Exchange"; ~~`StructureKind.Exchange`~~ (withdrawn by
  round 6 C2 — the one neutral kind is `Feature`) was a code name
  that never reaches a player band (GG-62). Player copy calls the whole ladder a **trade hub** (ideal
  §14b vocabulary) and each tier by its building name.
- **Guard rule, now active** (was "once OQ-2 is answered"): the vocabulary guard (§3) fails when any
  slot type's display name equals, after the decision-43 normalisation, any structure row's or variant's
  display name. It reads both catalogs; it pins no name and no count.

### 5. Verification boundary

`gk-core/data/tuning/**` has no owner boundary; only single files such as `materials-tuning` are mapped
(`gk-core/scripts/verification-boundaries.v1.json`). This module adds a boundary row `trade-catalog-tuning`
(`data/tuning/trade-catalog.v*.json` → the catalog join and guard tests). The web half has no mapping
(see Test plan).

## Contract exposed

| Member | Consumer |
|---|---|
| `TradeCatalog` (host-loaded, served on the world catalog read) with the nine families above (round 4 adds `featureTiers`, reading lines only; the 2026-09-20 audit withdrew `reportPrefixes`) | every trade-surface FE module; `trade-notify`'s translator |
| `tradeLabel(family, id)` web helper that returns the catalog row or a **designed unknown placeholder**, never an id | pieces and folds |
| The vocabulary guard | CI; `trade-click-budget` reuses nothing from it |

## Acceptance (contract level)

1. Join closure holds both ways for every landed provider family; an unlanded family is absent.
2. No player-facing trade string is derived from an id: `tradeLabel` on an unknown id returns the
   placeholder, and a test asserts no rendered trade surface contains a raw token.
3. The guard fails on a fixture row labelled "Trade District" and on a row whose `displayName` is
   `essence.fire`; it passes on the shipped file.
3a. **Slot vs building names (round 5 C4).** The guard fails on a fixture slot catalog whose `market`
   slot is named "Market" while a trade variant is named "Market", and passes once the slot is
   "Market Square"; no slot and no building share a normalised display name in the shipped catalogs.
4. Every trade report prefix has a playback row; a prefix with no row fails the world-playback coverage
   test.
5. Missing file or a missing family key the host expects is a load rejection naming it (T5).

## Test plan and verification boundary

- **Core/host:** catalog loader rejection tests; join-closure tests per family (`FusionRpg.Server.Tests`
  or `FusionRpg.Core.Tests`, wherever the other `*-catalog` loaders' tests live) — boundary
  `server-fallback`/`core-fallback` plus the new `trade-catalog-tuning` row.
- **Guard:** the vocabulary guard in `FusionRpg.Guard.Tests` — `guard-tests-fallback`.
- **Web:** `tradeLabel` placeholder test and the no-raw-token render test (vitest).
  **Gap, stated:** `gk-core/scripts/verification-boundaries.v1.json` has no `web/` path (grep count 0) and its
  `projects` map lists `.csproj` files only, so `verify-change.py` cannot select vitest. Per AGENTS.md
  this is a boundary defect to report, never a reason to run the full suite; the fix is owned by the
  `guard-verification-boundary-tests` owners.

```powershell
.\scripts\verify-change.ps1 -Paths @('data/tuning/trade-catalog.v1.json', '<loader path>', '<test paths>') -Session <id>
```

## Hard edges

- **Never** a number in the catalog; never display copy in `trade.v1.json`.
- **Never** define a token here; a missing provider token is that provider's change.
- **Never** a second franchise or name filter.
- Editing `playbackTable.ts` is world-stage's; this module files rows.

## Dependencies

Providers' closed sets (`logistics-flow` `logistics-facts`; `exchange` `tradeable-goods`,
`treaty-vocabulary`, `trade-access`; `sector-yield` `located-goods-registry`); `throttle-forecast` for the
answer vocabulary (the catalog rows land when that module does); world-stage `world-playback` (ask);
`ip-censor` `scan` (ask).

## Boundaries

- **Always:** authored rows; join closure both ways; publish `v{n+1}` through `gk-core/tools/tuning/publish.py`.
- **Ask first:** a family beyond the nine above (`reportPrefixes` withdrawn, `featureTiers` added in round 4); any copy outside trade.
- **Never:** hand-edit a published version; a banned term; an id on a player band.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: tunables (runtime catalog class), UI vocabulary (GG-23/GG-62), world playback.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/trade-network/**;
    session-boundary-check.py not re-run in this docs-only task.
[x] Read this session: DESIGN-GATE, PRINCIPLES §7/§9, game-gui-principles (GG-1..GG-64 rules cited),
    tunables-ssot §1/§3, trade-surface-map, logistics-flow-map §10, exchange-map module table.
[x] decisions.md: Game GUI (:110), GUI Lego (:132). No lock on trade copy.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH finding.
[x] Claims verified against code (LENSES labels, playback header, UnitClass guard, catalog hook).
[x] Surrounding sections read (tunables T5/T8, GG-62 Home paragraph).
[x] No constraint claimed without a test.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none needed outside this file.
[x] No population pinned: goods count is a reading; family names are this module's declaration.
[x] No event-refreshed cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No parallel path: one catalog, one translation table, one name filter (ip-censor).
[ ] Registry row: the trade vocabulary guard needs a row in gk-core/scripts/enforcement-registry.v1.json when built.
[x] Round 4 reconciliation (2026-09-19): `featureTiers` family — reading lines keyed (feature, tier), joined
    to trade-foundation `SectorFeature` and each feature's maximum tier; building names come from the
    structure catalog, never duplicated; `throttleAnswers` gains `build-feature`. ~~Name collisions (tier "Market" vs the Market slot, tier
    "Exchange" vs the ladder, banking "Vault" vs the Vault slot) are exchange-map owner question OQ-2;
    the vocabulary guard gets a rule once it is answered~~ (superseded: answered by round 5 C4, §4a):
    no building and slot share a display name.
[x] Round 5 (2026-09-20): C4 applied — §4a slot display names ("Market Square", "Vault Site"), ids
    unchanged, change filed on the slot catalog's Name field (SlotTypeCatalog.cs:72, :74 verified);
    guard rule active (acceptance 3a).
```

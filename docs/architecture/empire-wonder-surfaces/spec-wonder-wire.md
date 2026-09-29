# Spec: `wonder-wire`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`; main checkout untouched. Module id
`wonder-wire`, wave 1 (no dependency — builds in parallel with `wonder-rest` + `wonder-content`;
`wonder-composer` + `wonder-display` consume it). Map:
[empire-wonder-surfaces-map.md](../empire-wonder-surfaces-map.md) (orphan-closer: the map names no
wire module — this spec closes the orphan its rows 3–4 defer). Ideal:
[empire-wonder-surfaces-ideal.md](../empire-wonder-surfaces-ideal.md) (§9.7 backend-reads note,
Owner resolutions: show-counts, teasers, reachable-first, panel). Sibling specs consumed exactly:
[spec-wonder-display.md](spec-wonder-display.md) §Design 5 (blockers 1–9 — consumed verbatim,
owned here); [spec-wonder-composer.md](spec-wonder-composer.md) §Design 7 (backend-reads note —
owned here); [spec-wonder-rest.md](spec-wonder-rest.md) Boundaries (catalog/slot wire explicitly
refused there — owned here, never duplicated). House style precedent:
[scoped-inventory-hierarchy/spec-legion-cargo.md](../scoped-inventory-hierarchy/spec-legion-cargo.md).

## Objective

Give the two landed wave-2 specs the live REST/catalog wire reads they name as blockers and no
spec owns: owner-locked live cap counts (`ExistenceCap` + `LiveWonderCount` per scope-unit) and
scope/rarity identity (`WonderScope`/`WonderRarity`/`RelicCost`) on the catalog wire; the Wonder
facet on the slot wire (identity without a second fetch per slot); upkeep/production attribution
reads (`WonderUpkeep` + `WonderProductionContribution`) on the sector wire; and one REST
reachability read for reachable-first picking. Each field names its producer (which
store/catalog function computes it), its route, and its DTO name — so `wonder-composer` and
`wonder-display` can rely on exact field names with no further design.

Success looks like: `GET /api/world/catalog` names every Wonder row's scope, rarity, relic count,
and cap; `GET /api/world/{worldId}/state` names every slot's Wonder facet, every owned sector's
Wonder upkeep operand and Wonder-attributable production, and every owned sector's live
raised-vs-cap numerators; one `GET` reachability read answers "which relic instances are reachable
here for (entity, sector)"; and both wave-2 folds bind those fields by name with zero new pricing,
zero new command verbs, and zero pack/copy design.

## Locked anchors

- **The nine display blockers are consumed exactly, owned here.** `spec-wonder-display.md` §Design 5
  tables blockers 1–9 as "owned by plan Tasks 4A.3/4B, not by this module". This module IS that
  backend-reads task's spec: blockers 1–6 (catalog identity + caps + counts + slot facet), 7–8
  (upkeep/production attribution), and 9 (reachability read) land here. The composer note
  (`spec-wonder-composer.md` §Design 7) names the same three gaps; it binds them here too.
- **`wonder-rest`'s refusal is consumed, never re-litigated.** `spec-wonder-rest.md` Boundaries
  "Never: … catalog/slot wire additions for cap counts, scope/rarity, or `RelicCost` display (ideal
  §9.7 … `wonder-display`'s problem, not this module's)". This module is that named owner. It
  extends the DTOs `wonder-rest` refused; it does not touch `wonder-rest`'s four files
  (`WorldCommandRequest.RelicInstanceIds`, endpoint mapping + early check, FE queue mirror).
- **Owner resolutions bind the shape of every read** (ideal Owner resolutions, 2026-09-15): live cap
  counts are SHOWN (so `ExistenceCap` + `LiveWonderCount` are blockers, not enhancements — a fold
  that cannot read them cannot render); reserved tiers render as LOCKED TEASERS (so the catalog
  MUST expose the scope metadata teasers read — `WonderScope` on the wire, including for rows the
  player can never build); relic picking is REACHABLE-FIRST (so the reachability read MUST answer
  per (entity, sector) pair, not per empire); composer is a PANEL (no route work here — reads only).
- **Values are owned upstream; this module moves them, never prices them.** Every number below is
  read from its existing producer (catalog row, `WonderPolicy`, `WonderExistenceScan`,
  `LoamUpkeep`/`LoamProduction`, cargo/storage tables). A literal cap, cost, rate, or threshold
  appearing in this diff is a review failure — same discipline as `wonder-rest`'s Locked anchors.
- **Field names below are the contract.** `wonder-composer` / `wonder-display` rely on the exact
  names in §Design 6 / Interface by name (GG-9: link, don't re-implement). Renaming a field after
  this spec lands is a breaking change to two specs, not a cleanup.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Wonder facet fields exist on `StructureDef`: `WonderScope?` / `WonderRarity?` / `WonderEffects` / `RelicCost` | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:206-227`, read in full this session (facet docs at `:206-226`) |
| Facet parse exists: `ToStructureDef` parses `WonderScope`/`WonderRarity`/`WonderEffects`/`RelicCost` with exact-spelling `Enum.Parse` | `StructureCatalog.cs:316-327` |
| `Validate` pairing + reservation refusals exist (scope/rarity pairing, reserved-scope refusal, reserved-kind refusal, scope-mismatch, `RelicCost` pairing) | `StructureCatalog.cs:393-426` (pairing `:393-395`, reserved scope `:396-399`, kinds `:406-411`, mismatch `:412-415`, `RelicCost` `:423-426`) |
| Closed vocabularies exist: `WonderScope` (Sector/Empire live, World/Multiverse reserved), `WonderRarity` (Common/Unique), `WonderEffectKind` (`LoamGenerationRate` live) | `gk-core/src/FusionRpg.Core/World/WonderCatalog.cs:8-64`, read in full this session |
| Cap lookup exists: `WonderPolicy.ExistenceCapFor` (`Common` = `long.MaxValue`; `Unique` = tuning per scope; reserved throws) | `WonderCatalog.cs:98-126` (lookup at `:115-125`) |
| Existence scan exists: `WonderExistenceScan.CountExisting` counts built AND under-construction per scope-unit (Sector = target sector; Empire = owner's holdings) | `gk-core/src/FusionRpg.Core/World/WonderExistenceScan.cs:12-53`, read in full this session (no-skip rule `:38-50`, `checked` `:51`) |
| Cap + materials re-checks exist at resolution (`relic.not-reachable` on count after the Data gate empties; `wonder.cap-reached` via scan-vs-policy; `build.cannot-afford-materials`) | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:102-132` (re-check `:106-110`, cap `:114-123`, materials `:128-132`) |
| Admission structural check exists (right count, no duplicates — never ownership) | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:112-119` |
| Data-side reachability gate exists: owned/live/unassigned/Relic-container + reachable-right-now (aboard issuing legion's cargo OR target sector's storage) + per-batch `claimed` set | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:53-117` (gate), `:128-182` (`IsRelicSpendableUnlocked`: ownership `:144-162`, reachability UNION `:168-181`) |
| Catalog route exists: `GET /api/world/catalog` projects `StructureCatalog.All` to `WorldStructureDto` (rules, not state — no world id, no viewer, no fog) | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:259-273` (route `:259`, projection `:261-273`) |
| Catalog DTO exists WITHOUT any Wonder field: `StructureId/Name/Kind/RequiredSlotKind/Cost/YieldMultiplierMilli/BuildTurns/CapacityBonus/ObstacleKind/MaterialTier` | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:363-393`, read in full this session |
| Slot DTO exists WITHOUT any Wonder field: `SlotIndex/SlotTypeId/Element/State/OwnerFactionId/GuardWaveId/GuardState/StructureId/ConstructionTurnsRemaining` | `WorldDtos.cs:47-78` (construction doc `:72-77`) |
| Slot projection exists (`believed.Slots` → `WorldSlotDto`, `StructureId` + `ConstructionTurnsRemaining` assigned) | `WorldEndpoints.cs:492-509` (slot projection `:492-509`, construction at `:508`) |
| Sector loam projection exists: `LoamProduction.For(sector, scopeModifierMilli)` + `LoamUpkeep.BreakdownFor` + `LoamForecast.WillRelease` per component, owner-gated structurally (unowned sectors simply have no entry) | `WorldEndpoints.cs:613-661` (`ComputeLoamReading`: production `:635`, breakdown `:636`, forecast `:655`); `ProjectSector` `:407-544` (production `:514`, breakdown `:516-524`, net `:525`) |
| Upkeep truth ALREADY carries the Wonder term: `LoamUpkeepBreakdown` has `WonderUpkeep` (5 additive terms), computed as `Σ Empire ValueMilli × rate / 1000` | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:11-26` (record at `:11-13`, `Sum` at `:15`), `:70-79` (wonder term `:75-77` via `WonderEmpireEffects.EmpireLoamGenerationValueMilliFor`) |
| Production truth ALREADY carries the Empire modifier: `LoamProduction.For(sector, scopeModifierMilli)` applies the faction's stored modifier once at the end | `gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs:23-70` (modifier param `:23`, application `:69`) |
| Stored modifier + its computer exist: `WorldFaction.ScopeModifierMilli` (default 1000); `WonderEmpireEffects.ComputeScopeModifierMilli` = `1000 + Σ ValueMilli` over owner's built Empire Wonders; per-sector half `EmpireLoamGenerationValueMilliFor` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:93` (field); `gk-core/src/FusionRpg.Core/World/Loam/WonderEmpireEffects.cs:19-57` (sector half `:19-37`, faction sum `:47-57`) |
| Balance/forecast read the STORED modifier, never rescan (the pattern this wire follows) | `gk-core/src/FusionRpg.Core/World/Loam/LoamBalance.cs:13-18`; `LoamForecast.cs:55-59` (stored read `:57-58`), `:76-86` (`WillRelease`) |
| Upkeep-breakdown DTO exists with FOUR additive terms (stale vs Core's five): `Base/Garrison/Development/Danger + IntensityMilli/HandicapMilli` | `WorldDtos.cs:107-115` |
| FE mirrors exist without Wonder fields: TS `WorldStructureDto` (no Wonder keys), `WorldSlotDto` (+ drift comments proving the mirror lags the DTO), `WorldLoamUpkeepBreakdownDto` (four terms), `SlotView` (eight fields), `UpkeepBreakdownView` (four terms), `adaptWorldSlot` / `adapt.ts` upkeep block (four rows) | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:309-320` (structure), `:24-48` (slot + W4/W62 drift comments), `:66-73` (breakdown); `contract/types.ts:863-873` (`SlotView`), `:745-752` (`UpkeepBreakdownView`); `contract/adapt.ts:447-454` (upkeep), `:506-518` (`adaptWorldSlot`, W62 note `:499-505`) |
| Ledger reads four rows straight off the wire; row keys are a closed 4-member union | `gk-web/web/fusion-rpg-web/src/ui/world/ModifierLedger.tsx:21-26` (`ROW_LABELS`), `:80-90`; `modifierLedgerMath.ts:19-31` (`ModifierLedgerRowKey`), `:38-41` (`reproducedTotal` — four-term sum, two-factor divisor) |
| Only in-process reachability read today: `ListClaimableCachesUnlocked` (corpse-cache reachability at the legion's position — NOT relic reachability) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:48-93` (position-gated `:51-72`, cache query `:76-82`) |

### Wiring gap (machinery exists but the Wonder path doesn't use it)

| Gap | The inert/underused line |
|---|---|
| Catalog wire drops every Wonder facet: `/catalog` projection maps eight structure fields and none of `WonderScope/WonderRarity/RelicCost`/cap | `WorldEndpoints.cs:261-273` vs `StructureDef` `:211-226`; DTO `WorldDtos.cs:363-393` has no Wonder field |
| Upkeep DTO + projection drop the Wonder term the truth already computes: `LoamUpkeepBreakdown.WonderUpkeep` never reaches `LoamUpkeepBreakdownDto` or the adapter | `LoamUpkeep.cs:11-13` (truth has it) vs `WorldDtos.cs:107-115` + `WorldEndpoints.cs:516-524` + `adapt.ts:447-454` (wire drops it); `modifierLedgerMath.ts:38-41` reproduces a four-term total that will disagree with `LoamUpkeep.For` the moment the term is nonzero |
| Production attribution missing: the sector wire sends `LoamProduction` total only — an Empire-blessed sector's "Earns" cannot be expanded into its Wonder source | `WorldSectorDto.LoamProduction` (`WorldDtos.cs:143`) + `SectorLoamBlock` reads `sector.loam.production` alone (display spec §What already exists) |
| Live counts have a producer but no wire: `WonderExistenceScan.CountExisting` is called only by `BuildResolver` (refusal path) — nothing projects it for display | `WonderExistenceScan.cs:14-52` (producer) vs zero projection sites (grep: only `BuildResolver.cs:116` calls it) |
| Slot wire carries `StructureId` but no Wonder facet — every slot card needs a second catalog fetch per slot to learn scope/rarity | `WorldEndpoints.cs:492-509` (no catalog join); `SlotView` `gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895` (no facet) |
| Relic reachability has a commit-time gate but no planning-time read — the composer cannot sort reachable-first before filing | `RpgStore.WonderBuild.cs:128-182` (gate, tx-bound, commit-only) vs no `GET` route; `ListClaimableCachesUnlocked` answers a different question (corpse caches at position, not relic instances for (entity, sector)) |

### Real gap (no shareable wire path exists yet)

| Gap | What this module builds |
|---|---|
| No Wonder identity/cap/count fields on the catalog wire | §Design 1: four DTO extensions + projection lines |
| No Wonder facet or live-count fields on the state wire (slot + sector) | §Design 2–3: slot facet + sector counts + upkeep/production attribution |
| No planning-time relic-reachability REST read | §Design 4: one `GET` read + DTO |
| No FE mirror/adapter lines for any of the above (TS DTOs + `SlotView`/`UpkeepBreakdownView` + adapters) | §Design 5: mirror + adapter extensions (wire + mirror + adapter land together — the W62/W63 drift class) |

## Design

### 1. Catalog DTO extensions — identity + cap on the rules wire (no fog, no viewer)

`WorldStructureDto` (`WorldDtos.cs:363-393`) gains four fields. All four are RULES (per catalog
row, identical for every viewer and every world) — they ride the existing `GET /api/world/catalog`
route (`WorldEndpoints.cs:259-273`), need no fog gate, and change no golden that pins state:

| Field (exact name) | DTO type | Producer (computes it) | Route |
|---|---|---|---|
| `WonderScope` | `string?` — `WonderScope.ToString()` or `null` for non-Wonder rows | `StructureCatalog.Get(id).WonderScope` (`StructureCatalog.cs:211`; parsed `:316`; paired `:393-395`; reserved refused `:396-399`) | `GET /api/world/catalog` — one projection line beside `MaterialTier` (`WorldEndpoints.cs:261-273`) |
| `WonderRarity` | `string?` — `null` for non-Wonder rows | `StructureCatalog.Get(id).WonderRarity` (`:214`; parsed `:317`) | same row |
| `RelicCost` | `long` — `0` for every non-Wonder row (the existing pairing invariant) | `StructureCatalog.Get(id).RelicCost` (`:226`; parsed `:326`; pairing `:423-426`) | same row |
| `ExistenceCap` | `long` — `WonderPolicy.ExistenceCapFor` result; `long.MaxValue` for `Common` (uncapped by construction, never a finite number) | `WonderPolicy.ExistenceCapFor(scope, rarity)` (`WonderCatalog.cs:115-125`) reading `gk-core/data/tuning/loam-relics-wonders.v1.json` `uniqueExistenceCap.sector`/`.empire` (UNTOUCHED file) | same row |

Rules: `WonderScope`/`WonderRarity` are `null`-together (the pairing invariant `:393-395` — never
one null and the other set); `RelicCost` is `>= 1` iff scope is set (`:423-426`); `ExistenceCap`
for a non-Wonder row is `long.MaxValue` (no cap — same idiom as `Common`); reserved scopes/kinds
never appear here because `Validate` refuses them at startup (`:396-411`) — a `World`/`Multiverse`
row cannot reach this projection. Enum spelling is the exact C# member name (`"Sector"`,
`"Empire"`, `"Common"`, `"Unique"`) — the FE compares closed-vocabulary membership, never
free text (validation-ssot). `long` end to end (`RelicCost` is `long` at `:226`, caps are `long`
via `ExistenceCapFor`); the TS mirror types them `number` with the overflow discipline in
§Numeric types.

Display blockers closed: 1 (`WonderScope`), 2 (`WonderRarity`), 3 (`RelicCost`), 4
(`ExistenceCap`). Composer §Design 7 "catalog/slot wire" — same four.

### 2. Slot facet — Wonder identity without a second fetch per slot

`WorldSlotDto` (`WorldDtos.cs:47-78`) gains two nullable fields, projected by catalog join at slot
projection time (`WorldEndpoints.cs:492-509`):

| Field (exact name) | DTO type | Producer | Route |
|---|---|---|---|
| `WonderScope` | `string?` — scope of `StructureId`'s catalog row, else `null` (empty slot, unknown id, non-Wonder row) | `StructureCatalog.IsKnown(id) ? Get(id).WonderScope?.ToString() : null` (same `IsKnown`/`Get` the scan itself uses at `WonderExistenceScan.cs:36-48`) | `GET /api/world/{worldId}/state` — inside the existing `Slots = believed.Slots.Select(...)` (`:492-509`) |
| `WonderRarity` | `string?` — same null rule | same join | same projection |

Fog: IDENTICAL to `StructureId` — "as visible as the slot itself, no owner-gating"
(`WorldDtos.cs:66-70` comment). A viewer who can see the slot's structure id can see its scope;
nothing here leaks beyond what the slot already shows. `ConstructionTurnsRemaining` is CONSUMED,
not added — it already exists on the DTO (`:77`), the projection (`:508`), the TS mirror
(`bus/world.ts:47`), `SlotView` (`gk-web/web/fusion-rpg-web/src/lib/bus/types.ts`), and `adaptWorldSlot` (`adapt.ts:516`, W62 note
`:499-505`). This module adds no construction field.

Display blocker closed: 6 (slot facet). Until this lands, cards key identity off the local display
catalog by `structureId` (names survive — authored in `wonder-display`); cap lines stay in the
designed pending state (display spec §Design 5 rule, unchanged).

### 3. Sector attribution reads — live counts + upkeep + production (owner-only, stored reads)

`WorldSectorDto` (`WorldDtos.cs:117-247`) gains three fields, all computed in the existing
`ComputeLoamReading` / `ProjectSector` path (`WorldEndpoints.cs:407-544`, `:613-661`) over the
viewer's own holdings only (structural gating — an unowned sector simply has no entry, the same
discipline `LoamProduction`/`LoamUpkeep` already use):

| Field (exact name) | DTO type | Producer (computes it) | Route |
|---|---|---|---|
| `WonderLiveCountSector` | `long` — raised Unique Wonders of `Sector` scope in THIS sector (built + under-construction); `0` for unowned/unseen | `WonderExistenceScan.CountExisting(world, sector, WonderScope.Sector, WonderRarity.Unique)` (`WonderExistenceScan.cs:14-52`; Sector arm `:23`; under-construction counted `:38-50`) | `GET /api/world/{worldId}/state` — `ProjectSector` (`:407-544`), alongside `LoamProduction` (`:514`) |
| `WonderLiveCountEmpire` | `long` — raised Unique Wonders of `Empire` scope across the viewer's holdings (built + under-construction); `0` for unowned/unseen | `WonderExistenceScan.CountExisting(world, sector, WonderScope.Empire, WonderRarity.Unique)` (Empire arm `:24-25` — owner's sectors) | same projection |
| `WonderUpkeep` | `long` — this sector's Wonder upkeep operand (additive, pre-intensity/handicap/season) | `LoamUpkeep.BreakdownFor(world, sector).WonderUpkeep` (`LoamUpkeep.cs:47-80`; term `:75-77` = `WonderEmpireEffects.EmpireLoamGenerationValueMilliFor(sector) × LoamPolicy.EmpireWonderUpkeepRateMilli / 1000`) — projected from the ALREADY-COMPUTED `upkeepBreakdownBySector` map (`:636`, `:642`), never a second formula | same projection — extends the existing `UpkeepBreakdown = new LoamUpkeepBreakdownDto {...}` (`:516-524`) with one line |
| `WonderProductionContribution` | `long` — this sector's Wonder-attributable production: `For(sector, storedModifier) − For(sector, 1000)`; `0` when no Empire Wonder blesses this faction | `LoamProduction.For(sector, scopeModifierMilli)` (`LoamProduction.cs:23-70`) minus the identity call; `scopeModifierMilli` is the faction's STORED `WorldFaction.ScopeModifierMilli` (`WorldState.cs:93`) — never rescanned, exactly the `LoamBalance.PerSector` (`LoamBalance.cs:13-18`) / `LoamForecast.ProjectedStock` (`LoamForecast.cs:55-59`) pattern | same projection, from the ALREADY-COMPUTED `production` (`:635`) minus one identity call |

Gating: all four are owner-only — same gate as `LoamProduction` (`WorldDtos.cs:142-143`),
`LoamUpkeep` (`:145-146`), and the breakdown (`:148-154`): structurally zero for a sector the
viewer does not own (the `ComputeLoamReading` maps only ever contain the viewer's holdings —
`:623-647`). `Common` counts are deliberately ABSENT: `CountExisting` returns `0` for `Common`
(`:18-19`) and `ExistenceCapFor` returns `long.MaxValue` — the fold renders `Common` as
buildable-on-cap-grounds with no count line (GG-64; both sibling specs agree). `checked` on the
subtraction (overflow throws, never wraps — §Numeric types).

Display blockers closed: 5 (`WonderLiveCountSector`/`WonderLiveCountEmpire` — the N in "N of
cap"), 7 (`WonderUpkeep` — the fifth ledger operand), 8 (`WonderProductionContribution` — the
attributable "Earns" expansion, GG-49). The `reproducedTotal` drift is closed HERE at the wire
level by documenting the new divisor: Core `Total` is now a four-factor product
(`Sum × Intensity × Handicap × Season / 1_000_000_000`, `LoamUpkeep.cs:25`) while the DTO still
carries two multis and the FE reproduces two factors (`modifierLedgerMath.ts:38-41`) — the fifth
ledger ROW is `wonder-display`'s module, but the fifth OPERAND + its test update land here so the
wire never ships a total its own ledger cannot reproduce (the W62/W63 drift class, ideal §4).

### 4. Reachability read — reachable-first picking's planning-time source

One new read-only `GET` under the existing `/api/world` group (no command verb, no write, no turn
effect). It answers the composer's one question — "which relic instances are reachable HERE for
(entity, sector)" — with the same predicate the commit-time gate enforces, minus the batch-only
`claimed` set:

| Element (exact name) | Shape | Producer | Route |
|---|---|---|---|
| `WorldRelicReachabilityDto` | `{ worldId: string; entityId: string; sectorId: string; reachableInstanceIds: string[] }` — sorted ordinal, de-duplicated; `[]` for unknown legion / unpositioned legion / nothing reachable (inert, not broken — same posture as `ListClaimableCaches` for an unknown legion) | New `RpgStore.ListReachableRelicsUnlocked(db, tx, worldId, entityId, sectorId, playerStr)` — the `IsRelicSpendableUnlocked` predicate (`RpgStore.WonderBuild.cs:128-182`) factored to a list: ownership/live/unassigned/Relic-container filter (`:144-162`, incl. `disposition IN ('owned','cargo')` + `origin_kind='drop'` + Relic-container `EXISTS` + dual unassigned `NOT EXISTS`) JOINED to the reachability UNION (`:168-181`: `rpg_world_entity_cargo WHERE entity_id` UNION `rpg_world_sector_storage WHERE sector_id`); NO `claimed` set (batch-scoped, commit-only — planning-time has no batch) | `GET /api/world/{worldId}/relic-reachability?entityId={e}&sectorId={s}&asFaction={f}` — read-only; viewer gating identical to `/state` (`:42-46`: unknown faction → `faction.unknown`, never silent omniscience); SQL lives in `FusionRpg.Data` only (guard-dal) |

Rules: presence-only (the faction/presence gates stay deposit/withdraw's job at move time;
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:128-131` comment consumed); sector ownership re-validated at
resolution by `BuildResolver` (`build.not-yours`), never by this read; a `NULL`/blank entity or
sector matches nothing (same comment). Where-each-piece-sits for the FULL shelf (band vs sector
per instance) stays the sibling inventory program's `scoped-inventory-hierarchy` overlay API
(ideal §9.3) — this read answers only "reachable here", which is all reachable-first sorting
needs. `ListClaimableCachesUnlocked` (`RpgStore.CacheFieldAccess.cs:48-93`) is explicitly NOT the
producer (different question: corpse caches at position, not relic instances for a pair) — named
so no implementation binds the wrong table.

Display blocker closed: 9 (reachability REST read). Composer §Design 7 "REST reachability read
(only `ListClaimableCachesUnlocked` in-process exists)" — closed by this route.

### 5. Routes — no new verbs, only extensions + one GET

| Route | Change in this module |
|---|---|
| `GET /api/world/catalog` (`WorldEndpoints.cs:259-302`) | Four projection lines on `WorldStructureDto` (§Design 1). No new route. |
| `GET /api/world/{worldId}/state` (`:37-90` → `Project` `:663-738` → `ProjectSector` `:407-544`) | Slot facet join (§Design 2) + sector attribution fields (§Design 3). No new route. |
| `GET /api/world/{worldId}/relic-reachability` (NEW) | The one new read (§Design 4). No POST, no command kind, no turn effect. |
| `POST /{worldId}/commands`, `POST /{worldId}/commit`, `/turn/{turn}` | UNTOUCHED — `wonder-rest`'s shape flows through them unchanged. |

### 6. FE mirrors — wire + mirror + adapter land together (no drift)

Every DTO extension above lands with its TS mirror and adapter line in the SAME diff (the
W4/W62/W63 drift class — `bus/world.ts`'s own drift comments at `:33-47`, `:109-115`, `:136-142`
are the precedent for what happens when they separate):

| Wire field | TS mirror | Adapter |
|---|---|---|
| `WorldStructureDto.WonderScope/WonderRarity/RelicCost/ExistenceCap` | `bus/world.ts:309-320` `WorldStructureDto` gains `wonderScope: string \| null; wonderRarity: string \| null; relicCost: number; existenceCap: number` | Catalog adapter (whatever the build names) reads them straight through; `Common`/`long.MaxValue` renders as uncapped (never a gauge — GG-64) |
| `WorldSlotDto.WonderScope/WonderRarity` | `bus/world.ts:24-48` `WorldSlotDto` gains `wonderScope: string \| null; wonderRarity: string \| null` | `adaptWorldSlot` (`adapt.ts:506-518`) passes them straight through (same `known(...)` discipline as `constructionTurnsRemaining` at `:516`) into `SlotView` (`gk-web/web/fusion-rpg-web/src/lib/bus/types.ts` gains the two fields) |
| `UpkeepBreakdownDto.WonderUpkeep` | `bus/world.ts:66-73` `WorldLoamUpkeepBreakdownDto` gains `wonderUpkeep: number` | `adapt.ts:447-454` upkeep block gains `wonderUpkeep: { unit: "loamUnits", value: dto.upkeepBreakdown.wonderUpkeep }` into `UpkeepBreakdownView` (`gk-web/web/fusion-rpg-web/src/lib/bus/types.ts` gains `wonderUpkeep: Magnitude`); `reproducedTotal` + `Sum` documentation updated to five terms (the ROW itself — `ModifierLedger.tsx:21-26` fifth label + `ledgerRows` — stays `wonder-display`'s module) |
| `WorldSectorDto.WonderLiveCountSector/WonderLiveCountEmpire/WonderUpkeep-outside-breakdown?/WonderProductionContribution` | `bus/world.ts:99-177` `WorldSectorDto` gains `wonderLiveCountSector: number; wonderLiveCountEmpire: number; wonderProductionContribution: number` (`WonderUpkeep` travels INSIDE `upkeepBreakdown`, not beside it — one home, GG-9) | `adaptWorldSector` (`adapt.ts:~439-455`) maps all three straight through (`loamUnits` for contribution, `count` for live counts); live counts render via the fold's "N of cap raised" line (LOCKED shown) |
| `WorldRelicReachabilityDto` | New TS type beside `WorldCatalogDto` (`bus/world.ts:349-357` neighbourhood) + one `useReachableRelics(worldId, entityId, sectorId)` query hook (sibling of `useSubmitWorldCommands` at `:549-554` — read, never a file path) | Fold joins reachable ids above the full shelf (reachable-first, Owner resolution); full-shelf where-it-sits stays the sibling overlay |

## Tunables

None in this module. This spec introduces zero tunable numbers — no cost, no cap, no rate, no
threshold. Every number on the wire is owned elsewhere:

| Number on the wire | Actual home (not this module) |
|---|---|
| `WonderScope` / `WonderRarity` / effect `Kind`+`Scope` identity | Seed corpus rows (`gk-data/packs/fusion/data/seed/structures/wonder/**`), via `wonder-content` |
| `RelicCost` per row | Seed corpus magnitudes (provisional seed content, balance-owned) |
| `ExistenceCap` per scope+rarity | `gk-core/data/tuning/loam-relics-wonders.v1.json` `uniqueExistenceCap.sector`/`.empire`, read via `WonderPolicy.ExistenceCapFor` |
| `WonderLiveCount*` numerators | Live world state via `WonderExistenceScan.CountExisting` (no tunable — a reading) |
| `WonderUpkeep` operand + `EmpireWonderUpkeepRateMilli` | Upkeep term via `LoamUpkeep.BreakdownFor`; the RATE lives in `LoamPolicy` tuning (UNTOUCHED) |
| `WonderProductionContribution` + `ScopeModifierMilli` | `LoamProduction.For` + `WonderEmpireEffects.ComputeScopeModifierMilli` (SUM rule is a structural constant, decisions SSOT — not a tunable) |
| Reachability membership | Live cargo/storage tables via the spendability predicate (no tunable — a reading) |

A balance-shaped literal appearing in this diff is a review failure (`wonder-rest` Locked anchors,
consumed). `Common = long.MaxValue` is code, not a tunable — the "dynamic headroom" idiom
(`WonderCatalog.cs:29-31`), never a number to tune.

## Numeric types

Counts on the wire (`RelicCost`, `ExistenceCap`, `WonderLiveCount*`) are `long` end to end
(`StructureCatalog.cs:226`, `WonderCatalog.cs:115-125`, `WonderExistenceScan.cs:51`
`checked(count)`). The TS mirror types them `number` (JSON has no `long`; values are structurally
bounded — live Wonder counts cannot approach 2^53, and caps are tuning counts, never magnitudes
on the power ladder). The C#→TS narrowing is a documented transport narrowing, reported in the
DTO doc comment, never a silent cast in logic. `WonderUpkeep` / `WonderProductionContribution`
are `long` loam magnitudes: widen-before-multiply already satisfied (both operands `long` at
`LoamUpkeep.cs:75-77`, `LoamProduction.cs:69` `checked(total * scopeModifierMilli) / 1000`,
divide-by-1000-last); the FE reproduces integer division with `Math.trunc` (the
`modifierLedgerMath.ts:38-41` discipline, extended to five terms). `ScopeModifierMilli` narrowing
(`long` sum → `int` field) is `checked` (`WonderEmpireEffects.cs:56`) — throws, never wraps. No
`f(level)`, no per-mille math invented here, no progression ceiling: caps render as data
(`ExistenceCapFor` readings), `Common` explicitly uncapped (GG-64).

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Wonder"       # facet + cap + scan incl. new rows
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldCatalog" # /catalog projection incl. four new fields
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldState"   # /state slot facet + sector attribution
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ReachableRelic" # reachability read vs gate predicate
python gk-core/scripts/guard-dal.py        # every new SQL string lives in FusionRpg.Data
```

```powershell
# web (gk-web/web/fusion-rpg-web):
npm test -- adaptWorldSlot     # slot facet passes through; construction stays known
npm test -- adaptWorldSector   # upkeep fifth operand + contribution + live counts map straight through
npm run build                  # tsc --noEmit + vite build — type errors fail the build
```

No suite ran in this spec session (spec writes run no suite — idea/spec phase claims no test
movement; Commands above are implementation's verification, not this session's evidence).

## Structure

```
gk-core/src/FusionRpg.Contracts/WorldDtos.cs            MODIFIED — WorldStructureDto +4 (§Design 1);
                                                WorldSlotDto +2 (§Design 2);
                                                LoamUpkeepBreakdownDto +1 (WonderUpkeep) (§Design 3);
                                                WorldSectorDto +3 (live counts + contribution) (§Design 3);
                                                NEW WorldRelicReachabilityDto (§Design 4)
gk-core/src/FusionRpg.Server/WorldEndpoints.cs          MODIFIED — /catalog projection +4 (§Design 1);
                                                slot projection join +2 (§Design 2);
                                                ProjectSector/ComputeLoamReading attribution (§Design 3);
                                                NEW GET relic-reachability (§Design 4)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderReach.cs  NEW — ListReachableRelicsUnlocked (§Design 4;
                                                same predicate as IsRelicSpendableUnlocked, no claimed set)
gk-web/web/fusion-rpg-web/src/lib/bus/world.ts         MODIFIED — TS mirrors for every field (§Design 6)
gk-web/web/fusion-rpg-web/src/contract/types.ts        MODIFIED — SlotView +2, UpkeepBreakdownView +1,
                                                SectorView loam/count extensions (§Design 6)
gk-web/web/fusion-rpg-web/src/contract/adapt.ts        MODIFIED — adaptWorldSlot + adapt upkeep/sector lines (§Design 6)
UNTOUCHED: WorldCommand.cs; WorldCommandAdmission.cs; BuildResolver.cs; RpgStore.WonderBuild.cs
            (gate + spend — read, never re-implemented); RpgStore.WorldTurns.cs; StructureCatalog.cs;
            WonderCatalog.cs; WonderExistenceScan.cs; LoamUpkeep.cs; LoamProduction.cs; LoamBalance.cs;
            LoamForecast.cs; WonderEmpireEffects.cs; gk-core/data/tuning/loam-relics-wonders.v1.json;
            gk-data/packs/fusion/data/seed/structures/**; bus/world.ts submit/commit verbs; worldSelection.ts;
            ModifierLedger.tsx + modifierLedgerMath.ts ROWS (display's module — operand + test-doc
            update here, row there); every theme pack; every display-copy row.
```

## Code style

```csharp
// /catalog projection — one line per facet, same flat style as every sibling field.
WonderScope = s.WonderScope?.ToString(),
WonderRarity = s.WonderRarity?.ToString(),
RelicCost = s.RelicCost,
ExistenceCap = s.WonderScope is { } ws && s.WonderRarity is { } wr
    ? WonderPolicy.ExistenceCapFor(ws, wr) : long.MaxValue,
```

```csharp
// Slot projection — catalog join, null unless a known Wonder row.
WonderScope = sl.StructureId is { } sid && StructureCatalog.IsKnown(sid)
    ? StructureCatalog.Get(sid).WonderScope?.ToString() : null,
```

```ts
// adaptWorldSlot — same straight-through discipline as constructionTurnsRemaining.
wonderScope: dto.wonderScope,
wonderRarity: dto.wonderRarity,
constructionTurnsRemaining: known(dto.constructionTurnsRemaining)
```

## Testing strategy

- **Catalog identity round-trips:** `standing-stones` projects `WonderScope="Sector"`,
  `WonderRarity="Common"`, `RelicCost=1`, `ExistenceCap=long.MaxValue`; `sunspire-throne`
  projects `Empire`/`Unique`/`3`/tuning number (changing the tuning file changes the cap with no
  code change); every non-Wonder row projects `null`/`null`/`0`/`long.MaxValue`.
- **Reserved tiers never reach the wire:** a probe `wonderScope: "World"` row still fails
  `Validate` at startup (`StructureCatalog.cs:396-399`) — loud, never a wire value.
- **Slot facet without a second fetch:** a slot carrying `standing-stones` projects its scope/rarity
  inline; an empty slot / unknown id / non-Wonder structure projects `null`/`null`; fog parity —
  facet visible exactly when `StructureId` is visible (no owner-gating drift).
- **Live counts count acceptance, not completion:** two `Unique` Wonders of the same scope with one
  still under construction count `2` (`WonderExistenceScan` no-skip rule `:38-50` as wire test);
  `Common` scope counts read `0` (never scanned); Empire count identical across all sectors of one
  faction, `0` for unowned/unseen.
- **Upkeep operand reconciles:** `Base+Garrison+Development+Danger+WonderUpkeep` through the
  four-factor `Total` reproduces `LoamUpkeep.For` exactly (the ledger-reproduction test extended to
  five terms — wire and ledger agree or the test fails).
- **Production attribution reconciles:** `WonderProductionContribution == For(stored) − For(1000)`;
  a Wonder-free faction reads `0` (stored `1000`, byte-identical worlds).
- **Reachability matches the gate:** every id the `GET` returns passes `IsRelicSpendableUnlocked`
  (owned/live/unassigned/Relic-container + reachable); an id in neither overlay is absent; unknown
  legion / unpositioned legion reads `[]`; the read performs no write of any kind.
- **No population-count or generated-text pins** (validation-ssot): assert closed-vocabulary
  membership (scope/rarity/effect kinds, refusal strings — state the reason),
  envelope/reconciliation (every catalog row has a wire row; every wire total reproduces),
  determinism, and structural bounds — never corpus sizes, item totals, or authored names.
- **Not covered here:** composer picking, shelf where-it-sits, spend atomicity, refusal copy,
  pack paint, cap-line rendering, live probe — `wonder-composer` / `wonder-display` acceptance,
  named so this wire is not mistaken for covering them.

## Boundaries

- **Always:** project stored/computed truth (never rescan where a stored read exists —
  `ScopeModifierMilli`, `upkeepBreakdownBySector`); extend existing DTOs/routes before inventing
  any; land wire + TS mirror + adapter in one diff (no drift); fog-parity with the field's
  neighbours (catalog = public rules; slot facet = slot visibility; sector attribution = owner-only).
- **Ask first:** a second reachability shape (per-instance where-it-sits for the full shelf is the
  sibling inventory overlay's — extending this read to answer it needs that program's decision);
  a dedicated `/wonder-caps` route instead of per-sector fields (per-sector is the default —
  counts are scope-unit readings, and a route per question is how drift starts); exposing
  `SeasonMilli` on the DTO (Core computes with it, the DTO never carried it — adjacent staleness,
  not this module's mandate, but flag it).
- **Never:** pricing (no cost/cap/rate/threshold literal — values owned upstream); new command
  verbs (no new `WorldCommand` kind, no POST, no turn effect — one GET read only); pack/copy
  design (no theme pack, no display-catalog row, no refusal sentence, no authored name — those are
  `wonder-display`'s modules); engine changes (scan/policy/upkeep/production/gate/spend are read,
  never edited); seed or tuning edits (rows + numbers are `wonder-content`'s + balance's);
  re-specifying shared FE pieces (ledger ROWS, shelf, meter — consumed by name downstream); a
  second debug surface re-implementing these reads (adapter-wrap, scope-label — debug-mcp-ideal
  assessed shape).

## Success criteria

1. `GET /api/world/catalog` names `WonderScope/WonderRarity/RelicCost/ExistenceCap` on every
   structure row — `wonder-composer` catalog rows and `wonder-display` teaser gating bind them by
   name. 2. `GET /api/world/{worldId}/state` names slot `WonderScope/WonderRarity`, sector
   `WonderLiveCountSector/WonderLiveCountEmpire`, breakdown `WonderUpkeep`, and sector
   `WonderProductionContribution` — live cap lines ("N of cap raised", LOCKED shown) and ledger
   attribution render from these alone. 3. `GET relic-reachability` answers reachable-here per
   (entity, sector) matching the commit gate minus the batch set — reachable-first sorting binds
   it. 4. Every field has a TS mirror + adapter line in the same diff (zero drift). 5.
   `guard-dal.py` green (new SQL only in `FusionRpg.Data`). 6. Zero changes to pricing, verbs,
   packs, copy, engine, seed, or tuning.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldStructureDto.WonderScope/WonderRarity/RelicCost/ExistenceCap` (§Design 1) | `wonder-composer` — price-first catalog rows, cap lines, teaser gating; `wonder-display` — scope/rarity badges + pack selection + `Unique` cap-line gating |
| `WorldSlotDto.WonderScope/WonderRarity` → `SlotView` (§Design 2) | `wonder-display` — card identity without a second fetch per slot; `wonder-composer` — slot-pick Wonder facet |
| `WorldSectorDto.WonderLiveCountSector/WonderLiveCountEmpire` (§Design 3) | `wonder-composer` + `wonder-display` — the N in "N of cap raised" (LOCKED shown); `Common` reads `0`/uncapped by contract |
| `LoamUpkeepBreakdownDto.WonderUpkeep` → `UpkeepBreakdownView` (§Design 3) | `wonder-display` — fifth ledger row (row itself is display's module; operand + test update here) |
| `WorldSectorDto.WonderProductionContribution` (§Design 3) | `wonder-display` — attributable "Earns" expansion (GG-49, no mystery delta) |
| `WorldRelicReachabilityDto` + `GET relic-reachability` (§Design 4) | `wonder-composer` — reachable-first candidate join (reachable group above the fold, full shelf one disclosure away) |
| Nine-blocker table (§Design 1–4) | Phase 4A.3/4B plan — the exact fields owed before live counts / identity / attribution render; nothing left orphaned |

## Design-gate checklist

```
[x] Subsystems: world catalog/state wire (Contracts/Server/FE mirrors) + Wonder build contract
    (read-only refs) + loam attribution reads (read-only refs). No Status/ActorHub/Combat, no
    engine behavior change.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
[x] Read this session: empire-wonder-surfaces-map.md (full, rows 1-4 + assumptions);
    empire-wonder-surfaces-ideal.md (full: §4 built/wiring tables, §5 module rows, §7 chosen,
    §8 tunables + packs, §9.7 backend-reads note, §10 Q1-Q4 + Owner resolutions: panel,
    reachable-first, show-counts, locked-teasers); spec-wonder-display.md (full — §Design 5
    blockers 1-9 consumed exactly); spec-wonder-composer.md (full — §Design 7 backend-reads
    note); spec-wonder-rest.md (full — Boundaries catalog/slot refusal, owned here);
    spec-wonder-content.md (full — both rows as content dependency);
    scoped-inventory-hierarchy/spec-legion-cargo.md (full, house style);
    DESIGN-GATE.md (§1 UI + proving-live rows, §2 invariants, §5 checklist).
[x] Checked decisions.md direction via the ideal doc's own GUI Lego + Loam-relics SSOT rows
    (consumed through empire-wonder-surfaces-ideal.md §0 + §7, read this session) — wire
    greenfield confirmed (rest spec: "no wonder REST lock"); SUM rule + scope-modifier storage
    consumed from WonderEmpireEffects doc comments.
[x] Every factual claim cites file:line, verified against CODE opened fresh this session:
    WorldDtos.cs (:47-78 WorldSlotDto, :107-115 LoamUpkeepBreakdownDto, :363-393
    WorldStructureDto, :449-472 WorldCommandRequest — no Wonder/RelicCost field on any);
    WorldEndpoints.cs (:37-90 /state, :108-121 commands projection — no RelicInstanceIds line,
    :259-302 /catalog projection :261-273, :407-544 ProjectSector/:492-509 slots/:516-524
    upkeep, :613-661 ComputeLoamReading/:635 production/:636 breakdown/:655 forecast);
    StructureCatalog.cs (:206-227 facets, :316-327 parse, :393-426 Validate);
    WonderCatalog.cs (:8-64 vocabularies, :98-126 WonderPolicy/:115-125 ExistenceCapFor);
    WonderExistenceScan.cs (:12-53 CountExisting, Sector arm :23, Empire arm :24-25,
    no-skip :38-50, checked :51); BuildResolver.cs (:102-132 refusals, cap :114-123);
    WorldCommandAdmission.cs (:112-119 count/dup); RpgStore.WonderBuild.cs (:53-117 gate,
    :128-182 IsRelicSpendableUnlocked — ownership :144-162, UNION :168-181);
    RpgStore.CacheFieldAccess.cs (:48-93 ListClaimableCachesUnlocked — different question);
    WorldState.cs (:93 ScopeModifierMilli); WonderEmpireEffects.cs (:19-37 sector half,
    :47-57 faction sum); LoamUpkeep.cs (:11-26 record+Total, :47-80 BreakdownFor, :75-77
    wonder term); LoamProduction.cs (:23-70 truth side, :69 modifier application);
    LoamBalance.cs (:13-18 stored read); LoamForecast.cs (:55-59 stored read, :76-86
    WillRelease); bus/world.ts (:24-48 slot mirror + drift comments, :66-73 breakdown mirror,
    :99-177 sector mirror, :309-320 structure mirror, :349-357 catalog);
    contract/types.ts (:745-752 UpkeepBreakdownView, :754-813 SectorView, :863-873 SlotView);
    contract/adapt.ts (:447-454 upkeep, :506-518 adaptWorldSlot + W62 note :499-505);
    ModifierLedger.tsx (:21-26 labels, :80-90 pending/known);
    modifierLedgerMath.ts (:19-31 row union, :38-41 reproducedTotal).
[x] Read the surrounding section of every rule quoted (facet doc comments, Validate reservation
    comments, ExistenceCapFor Common/reserved docs, scan no-skip rationale, gate pipeline note,
    /state fog comment, /catalog rules-not-state doc, upkeep Total divisor comment, production
    modifier doc, reachability presence-only comment, TS drift comments, W62 adapter note).
[x] Tested constraints: none claimed — no "moves goldens" / "needs sign-off" asserted. Suite
    selection stated in Commands; the SeasonMilli DTO staleness is flagged as Ask-first, not
    assumed.
[x] No §2 invariant contradicted: SQL only in FusionRpg.Data (new read lives in
    RpgStore.WonderReach.cs); no cap on a magnitude (Unique caps tunable via WonderPolicy,
    Common explicitly uncapped — GG-64; live counts are readings, not ceilings); no f(Θ); no
    second ActorHub composer (reserved combat kinds refused, never wired); no parallel
    relic/reachability path (extends the one gate predicate, lists it — never a second gate);
    no second debug surface; no generated-data hand-edit (no seed touched).
[x] Corrections propagated: prose + Structure + Testing + Boundaries + Interface agree on the
    DTO/route/producer set, the nine-blocker closure, and the non-touch list (no pricing, no
    new verbs, no pack/copy design).
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. Scope/rarity/effect kinds, refusal strings, and cap-count shapes are
    closed vocabularies owned by the backend/catalog, with reasons stated (validation-ssot).
[x] No event-refreshed cache introduced or touched.
[x] No acceptance criterion fixes a silently-ordered execution: criteria assert readings/state
    (named, badged, counted, attributed, reachable), not an order.
[x] No actor combat/derived magnitude produced or consumed.
[x] Does not invent or extend a SOLID-violating parallel path: extends the one catalog DTO, the
    one slot/sector projection, the one upkeep/production read path, and the one relic-gate
    predicate — links (GG-9), never duplicates.
```

(End of file)

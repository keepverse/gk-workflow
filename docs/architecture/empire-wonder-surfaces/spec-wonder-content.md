# Spec: `wonder-content`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `wonder-content`, row 2 of the
[empire-wonder-surfaces map](../empire-wonder-surfaces-map.md) (wave 1, no dependency — builds in
parallel with `wonder-rest`). Ideal: [empire-wonder-surfaces-ideal.md](../empire-wonder-surfaces-ideal.md)
§4 (display rows), §8 (catalog/packs), Owner resolutions (panel composer, live cap counts shown,
locked teasers). Backend contract: [loam-relics-and-wonders/spec-wonder-structure.md](../loam-relics-and-wonders/spec-wonder-structure.md)
§Design 1–6. House style precedent:
[scoped-inventory-hierarchy/spec-legion-cargo.md](../scoped-inventory-hierarchy/spec-legion-cargo.md).

## Objective

Ship the first two Wonder catalog rows — one `Sector`-scope, one `Empire`-scope — through the
structures authoring path, proving the `wonder-structure` facet contract (`StructureDef.WonderScope?` /
`.WonderRarity?` / `.WonderEffects`, `StructureCorpus` optional parse, `StructureCatalog.Validate`
refusals, `WonderPolicy.ExistenceCapFor`) loads real content and still refuses reserved tiers. This
module authors content only: no engine change, no new field, no tuning-file edit.

Success looks like: two new seed files load through the existing `StructureCatalog.All` pipeline
alongside every shipped row; both rows render an authored name (never a raw id) for `wonder-composer`
/ `wonder-display` to consume; a probe row authoring `wonderScope: "World"` (or a `DefensePower`
effect) still fails `Validate` at startup, loud, naming the reserved member.

## Locked anchors

- **Identity is authored, magnitudes are table-owned (Seedsmith Law 2).** Names, flavor, and
  role/slot-kind picks are LLM-authored identity; every magnitude (`yieldMultiplierMilli`,
  `constructRubbleCost`, `relicCost`, effect `valueMilli`) is provisional seed content a balance pass
  owns. Caps are never in the row — `Unique` caps are read from
  `gk-core/data/tuning/loam-relics-wonders.v1.json` (`uniqueExistenceCap.sector` / `.empire`) via
  `WonderPolicy.ExistenceCapFor`, never restated as literals in content or prose.
- **Owner resolutions (ideal doc, 2026-09-15) bind the consumers of these rows:** composer is a
  band-2 panel; relic picking is reachable-first; live cap counts are shown (the fold MUST render
  them); reserved tiers render as locked teasers. These rows supply the identity and magnitude
  readings those surfaces present; they do not design the surfaces.
- **Reserved tiers stay refused, never presented as buildable.** `World`/`Multiverse` scope and
  `DefensePower`/`AuraGrant`/`EmpireBuff` kinds are named-but-unregistered
  (`WonderCatalog.cs:8-22`, `:44-60`); this module authors no row using them and adds no
  presentation contract for them — locked teasers are `wonder-display`'s module, not this one's.
- **A Wonder stays `Kind = LoamSource`/`Yield` on a legal role/slot pair** (backend spec §Design 1,
  the `Obstacle`-facet precedent): no new `StructureKind`, no new seedsmith role/slot pairing.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Wonder facet fields exist on `StructureDef`: `WonderScope?`, `WonderRarity?`, `WonderEffects` (default empty), `RelicCost` (default 0) | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:206-227`, read in full this session |
| Facet parse sites exist: `ToStructureDef` parses `WonderScope`/`WonderRarity`/`WonderEffects`/`RelicCost` with exact-spelling `Enum.Parse` (no `ignoreCase`) | `StructureCatalog.cs:316-327` |
| Corpus parse is genuinely optional for Wonder keys (`TryGetProperty`, default null) — shipped rows without Wonder keys load unmodified, matching `ContainerId`'s precedent | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:42-48` (record defaults), `:154-167` (parse) |
| Closed vocabularies exist: `WonderScope` (Sector/Empire live, World/Multiverse reserved), `WonderRarity` (Common/Unique), `WonderEffectKind` (`LoamGenerationRate` live, three reserved) | `gk-core/src/FusionRpg.Core/World/WonderCatalog.cs:8-60`, read this session |
| `Validate` refusals exist: scope/rarity pairing, reserved-scope refusal, empty/non-Wonder effect lists, reserved-kind refusal, scope-mismatch refusal, negative `ValueMilli`, duplicate pairs, and the `RelicCost` pairing (Wonder ⇒ `RelicCost >= 1`; non-Wonder ⇒ `0`) | `StructureCatalog.cs:393-426` |
| `Unique` existence caps exist as tuning (per-scope), read via `WonderPolicy.ExistenceCapFor` (`Common` = `long.MaxValue`, never a finite number) | `gk-core/data/tuning/loam-relics-wonders.v1.json:10-13` (`uniqueExistenceCap.sector`/`.empire`); `WonderCatalog.cs` policy section |
| `SlotView` wire carries `structureId` + `constructionTurnsRemaining` and nothing Wonder-shaped | `gk-web/web/fusion-rpg-web/src/contract/types.ts:863-872` (type at `:863`, fields at `:871-872`), confirmed this session |
| Structures corpus is AUTHORED content: shipped rows carry `_provenance.source: "AUTHORED"`, no `_meta.model` / `promptVersion` / `batch` generator provenance anywhere under `gk-data/packs/fusion/data/seed/structures/` | `gk-data/packs/fusion/data/seed/structures/extract/well.json:2-10` (`_meta.partition`, `_provenance.source: "AUTHORED"`); `gk-data/packs/fusion/data/seed/structures/bank/reliquary.json:2-10` (same); corpus-wide grep for `wonderScope\|WonderScope\|_meta.*model\|promptVersion` returns no files |
| No Wonder row exists yet: no shipped row authors any Wonder key | Same corpus-wide grep returns no files |
| The structures seedsmith adapter cannot express Wonder facets — its only "wonder" hit is a prose false positive ("left for a reader to wonder whether omission was an oversight") | grep over `gk-forge/tools/seedsmith/seedsmith/adapters/structures/` for `wonderScope\|wonder\|Wonder\|relicCost`: one hit, `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:19` (prose) |
| Legal role/slot pairs for the two rows: `Extract`→`Rootbed`, `Bank`→`Shrine` | `gk-data/packs/fusion/data/seed/structures/_plan.json:132-143` (`Extract`/`Rootbed`), `:108-115` (`Bank`/`Shrine`) |
| `well.json` shape precedent: `Extract` role on `Rootbed`, `Kind = LoamSource` | `gk-data/packs/fusion/data/seed/structures/extract/well.json:26-28` (anchor role/requiredSlotKind), `:52` (`structureKind: LoamSource`) |

### Real gap

| Gap | What this module builds |
|---|---|
| Zero Wonder seed rows — the facet contract has no content proving it loads | §Design 1–2: two authored rows (Sector + Empire) |
| No Wonder identity copy for `wonder-composer`/`wonder-display` to read (names, one-line effect readings) | Row `name` fields + §Design 3 reading contract (full display catalog is `wonder-display`'s module per ideal §8; these rows supply the names it reads) |
| No proof that reserved tiers are still refused once real Wonder rows exist | §Design 4: Validate acceptance (rows load, reserved probe rows still refused) |
| No Wonder facet on the catalog/slot wire for live-cap display | NOT this module — §Interface exposed to dependents (owed to Phase 4A.3/4B) |

## Design

### 1. Row A — Sector Wonder: `standing-stones`

A `Sector`-scope, `Common`-rarity Wonder: the prize a sector holds with its own ground. `Common`
means uncapped (`ExistenceCapFor` returns `long.MaxValue`) — the composer's live-count line for this
row always reads as buildable-on-cap-grounds, and the row exercises the "no cap" path end to end.

```json
{
  "_meta": { "partition": "Extract" },
  "entries": [
    {
      "_provenance": {
        "citation": "empire-wonder-surfaces `wonder-content` §Design 1 — Sector-scope Wonder anchor; Extract role on Rootbed per gk-data/packs/fusion/data/seed/structures/_plan.json legal pairs.",
        "source": "AUTHORED"
      },
      "anchor": {
        "acquisitionPaths": ["built"],
        "controlPoint": true,
        "costProfile": "steep",
        "coverTier": "none",
        "elementPrimary": "none",
        "elementSecondary": "none",
        "family": "loam-structures",
        "footprint": "one-cell",
        "obstacleVerbs": [],
        "rarity": "mythic",
        "reach": "melee",
        "reason": "",
        "requiredSlotKind": "Rootbed",
        "role": "Extract",
        "roleSecondary": "none",
        "strengthBand": "stone",
        "structureId": "standing-stones",
        "targetPreference": "none",
        "tempo": "none",
        "traits": [],
        "variants": []
      },
      "id": "standing-stones",
      "magnitudes": {
        "blocksLineOfFire": false,
        "blocksMovement": false,
        "buildTurns": 4,
        "capacityBonus": 0,
        "constructIronworkCost": 0,
        "constructRubbleCost": 0,
        "containerId": null,
        "cost": 0,
        "coverPowerMilli": 0,
        "coverRadius": 0,
        "entryStaminaMultiplierMilli": 1000,
        "flatYieldPerTurn": 0,
        "materialTier": 0,
        "obstacleKind": "None",
        "structureKind": "LoamSource",
        "visionRangeTiles": null,
        "yieldMultiplierMilli": 1000,
        "wonderScope": "Sector",
        "wonderRarity": "Common",
        "wonderEffects": [{ "kind": "LoamGenerationRate", "scope": "Sector", "valueMilli": 0 }],
        "relicCost": 1
      },
      "name": "Standing Stones"
    }
  ],
  "kind": "structure-anchor"
}
```

Notes: `Kind = LoamSource` on `Rootbed` mirrors `well.json` exactly (`:26-28`, `:52`), so the row
reuses `YieldMultiplierMilli`/`FlatYieldPerTurn` through the existing `LoamProduction.For` read with
zero new plumbing (backend spec §Design 3: for Sector scope the consumed magnitude is the row's own
yield fields; effect `ValueMilli` is descriptive tooltip consistency). `relicCost: 1` satisfies the
`RelicCost >= 1` pairing (`StructureCatalog.cs:423-424`) at the minimum meaningful recipe — one
relic laid in the foundation. All magnitude values above are provisional seed content for a balance
pass to set (they reuse the exact `well.json:37-55` key set plus the four Wonder keys the corpus
parse already supports at `StructureCorpus.cs:154-167`); the row carries no cap number — `Common`
is uncapped in code by construction.

### 2. Row B — Empire Wonder: `sunspire-throne`

An `Empire`-scope, `Unique`-rarity Wonder: the rarest work, prospering every holding. `Unique` means
the cap is read from tuning (`uniqueExistenceCap.empire` via `WonderPolicy.ExistenceCapFor`) — the
composer's live-count line for this row ("N of cap raised") renders tuning data, never a literal,
and the row exercises the capped path end to end.

```json
{
  "_meta": { "partition": "Bank" },
  "entries": [
    {
      "_provenance": {
        "citation": "empire-wonder-surfaces `wonder-content` §Design 2 — Empire-scope Wonder anchor; Bank role on Shrine per gk-data/packs/fusion/data/seed/structures/_plan.json legal pairs (reliquary precedent).",
        "source": "AUTHORED"
      },
      "anchor": {
        "acquisitionPaths": ["built"],
        "controlPoint": true,
        "costProfile": "steep",
        "coverTier": "none",
        "elementPrimary": "none",
        "elementSecondary": "none",
        "family": "loam-structures",
        "footprint": "one-cell",
        "obstacleVerbs": [],
        "rarity": "mythic",
        "reach": "melee",
        "reason": "",
        "requiredSlotKind": "Shrine",
        "role": "Bank",
        "roleSecondary": "none",
        "strengthBand": "stone",
        "structureId": "sunspire-throne",
        "targetPreference": "none",
        "tempo": "none",
        "traits": [],
        "variants": []
      },
      "id": "sunspire-throne",
      "magnitudes": {
        "blocksLineOfFire": false,
        "blocksMovement": false,
        "buildTurns": 6,
        "capacityBonus": 0,
        "constructIronworkCost": 0,
        "constructRubbleCost": 0,
        "containerId": null,
        "cost": 0,
        "coverPowerMilli": 0,
        "coverRadius": 0,
        "entryStaminaMultiplierMilli": 1000,
        "flatYieldPerTurn": 0,
        "materialTier": 0,
        "obstacleKind": "None",
        "structureKind": "Yield",
        "visionRangeTiles": null,
        "yieldMultiplierMilli": 1000,
        "wonderScope": "Empire",
        "wonderRarity": "Unique",
        "wonderEffects": [{ "kind": "LoamGenerationRate", "scope": "Empire", "valueMilli": 0 }],
        "relicCost": 3
      },
      "name": "Sunspire Throne"
    }
  ],
  "kind": "structure-anchor"
}
```

Notes: `Bank` role on `Shrine` follows the `reliquary.json` precedent (`:26-28`) — a legal pair
(`_plan.json:108-115`) already proven catalog-loadable (identity-registered; magnitudes make it
loadable per `StructureCorpus.cs:65`). For `Empire` scope the effect `ValueMilli` IS the consumed
magnitude (backend spec §Design 3: `wonder-effect-empire` sums it per faction under the locked SUM
rule) — the `0` above is a placeholder the balance pass sets, never a literal the code reads as
final. `relicCost: 3` (three distinct relic instances) marks the Empire work as the dearer
foundation without touching any tuning number. The cap this row enforces against lives only in
`loam-relics-wonders.v1.json` (`uniqueExistenceCap.empire`) — the row restates no count.

### 3. The AUTHORING PATH decision — hand-authored files, no generator work

**Decision: author two new files by hand under `gk-data/packs/fusion/data/seed/structures/wonder/`
(`standing-stones.json`, `sunspire-throne.json`). No generator fix is this module's deliverable.**

The evidence trail, all opened this session:

1. The corpus is authored, not generated: `well.json:7-10` and `reliquary.json:7-10` both carry
   `_provenance.source: "AUTHORED"` with a human citation; no file under `gk-data/packs/fusion/data/seed/structures/`
   carries `_meta.model` / `promptVersion` / `batch` generator provenance (corpus-wide grep: no
   hits). Per the generated-data hard rule, hand-editing is forbidden only for generator OUTPUT —
   this tree is authored source, so new hand-authored files are the sanctioned path, not a fork.
2. The parse layer already expresses Wonder facets: `StructureCorpus.cs:42-48` (optional record
   defaults) + `:154-167` (`TryGetProperty` for `wonderScope`/`wonderRarity`/`wonderEffects`/
   `relicCost`). There is no expressiveness gap for a generator fix to close.
3. The seedsmith `structures` adapter cannot author Wonders today (grep: only the `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:19`
   prose false positive), but nothing requires it to: Wonders are two bespoke mythic rows, not a
   generated population. Routing two authored rows through a generator that cannot express them
   would invert the sanctioned path — the generator gains Wonder support only when a future brief
   asks for Wonder populations, as its own program's decision, not as a side effect of this module.
4. The loader walks every `*.json` recursively (`StructureCorpus.cs:93`), skipping non-
   `structure-anchor` files — a new `wonder/` partition directory needs no loader change, and the
   `_plan.json` budget/balances are generation planning, not load-time validation, so no plan edit
   is required for two authored rows.

### 4. Validate acceptance

- Both rows load through `StructureCatalog.All` (`StructureCatalog.cs:262`) with all shipped rows
  byte-identical: every Wonder key is optional-at-parse (`StructureCorpus.cs:154-167`), so existing
  rows are untouched.
- Pairing holds: both rows set `WonderScope` + `WonderRarity` together (`:393-395`); both carry
  exactly one `WonderEffectDef` with `Kind = LoamGenerationRate` (`:406-411`) and
  `Scope == WonderScope` (`:412-415`); `RelicCost >= 1` on both (`:423-424`).
- Reserved tiers still refused: a probe row with `wonderScope: "World"` fails at `:396-399` naming
  the reserved scope; a probe effect with `kind: "DefensePower"` (or `AuraGrant`/`EmpireBuff`)
  fails at `:408-411` naming the reserved kind — loud startup errors, never silent acceptance.
- Enum spelling is exact-case (`"Sector"`, `"Empire"`, `"Common"`, `"Unique"`,
  `"LoamGenerationRate"`) — `Enum.Parse` without `ignoreCase` (`:316-323`) rejects any other
  casing at load, matching the `structureKind`/`obstacleKind` convention.

### 5. Live-cap display dependency note (owed to Phase 4A.3/4B, not this module)

The composer must show live cap counts (owner-locked, ideal §8) and the sector card must show
Wonder identity — neither wire field exists today: `SlotView` carries only `structureId` +
`constructionTurnsRemaining` (`gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895`) with no Wonder facet, and the catalog/slot wire
carries no `WonderScope`/`WonderRarity`/`RelicCost`/cap fields (ideal §9.7). `wonder-composer` and
`wonder-display` are therefore blocked on a Phase 4A.3/4B backend-reads task that extends the
catalog/slot wire (plus the reachability read and scope metadata the ideal names); this module's
rows are the content those fields will describe, and this module builds no wire, no adapter, and
no fold. Locked anchors for those modules: composer = band-2 panel over the world stage;
reachable-first relic picking (legion sheet cargo tab + sector store); live counts rendered from
`WonderPolicy` numbers; reserved tiers as locked teasers with the packs carrying the "not yet" slot
(ideal §8, Owner resolutions).

## Tunables

| Number | Home | Notes |
|---|---|---|
| `uniqueExistenceCap.sector`, `uniqueExistenceCap.empire` | `gk-core/data/tuning/loam-relics-wonders.v1.json` (existing file, UNTOUCHED by this module) | Policy constants, read via `WonderPolicy.ExistenceCapFor`; `Common` is uncapped in code (`long.MaxValue`). This spec restates no count — prose or rows carrying a literal cap number is a defect |
| Per-row `WonderScope`/`WonderRarity`/effect `Kind`+`Scope` | New seed rows (§Design 1–2) | Closed-vocabulary identity (constant, pinned with a reason: the Validate contract), not magnitudes |
| Per-row `yieldMultiplierMilli`/`flatYieldPerTurn`/`constructRubbleCost`/`constructIronworkCost`/`relicCost`/effect `valueMilli`/`buildTurns`/`cost` | New seed rows (§Design 1–2) | Provisional seed content; every value balance-owned, set by a balance pass — never tuned in code. Units: `*Milli` = per-mille (int), `buildTurns` = turns (int), `*Cost`/`relicCost` = whole units (long/int per Numeric types), counts = plain ints |
| Refusal-threshold copy ("N of cap raised") | Display catalog owned by `wonder-display` (ideal §8) + fold reading `WonderPolicy` numbers | This module supplies the N; the copy and the fold are not this module |

## Numeric types

`relicCost` is `long` (a count of consumed instances — matches `RelicCost`'s `long` at
`StructureCatalog.cs:226`); effect `valueMilli` is `long` per-mille (backend spec §Numeric types);
caps are `long` via `ExistenceCapFor`. No `f(level)` introduced — `MaterialTier = 0`
(indestructible default, `StructureCatalog.cs:112-113`) keeps both rows off the power ladder
entirely. No progression ceiling: `Unique` caps are tunable counts, `Common` is explicitly
uncapped.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StructureCatalogImportTests"  # shipped rows byte-identical
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WonderCatalog"                 # facet + cap contract incl. new rows
python gk-core/scripts/guard-dal.py        # no SQL in this module — green with zero new hits is the proof
```

## Structure

```
gk-data/packs/fusion/data/seed/structures/wonder/standing-stones.json   NEW — §Design 1 (Sector/Common)
gk-data/packs/fusion/data/seed/structures/wonder/sunspire-throne.json   NEW — §Design 2 (Empire/Unique)
UNTOUCHED: every shipped gk-data/packs/fusion/data/seed/structures/**/*.json row; gk-core/data/tuning/loam-relics-wonders.v1.json;
           StructureCatalog.cs; StructureCorpus.cs; WonderCatalog.cs; web/ contract, adapter, inspector.
```

## Code style

```json
"_provenance": {
  "citation": "empire-wonder-surfaces `wonder-content` §Design 1 — Sector-scope Wonder anchor; Extract role on Rootbed per gk-data/packs/fusion/data/seed/structures/_plan.json legal pairs.",
  "source": "AUTHORED"
}
```

Every new row carries the `well.json:7-10` / `reliquary.json:7-10` provenance shape verbatim —
`source: "AUTHORED"` plus a citation naming this spec section — so a later reader can tell authored
Wonder rows from any future generated population at a glance.

## Testing strategy

- **Shipped rows byte-identical:** `StructureCatalogImportTests` passes unmodified — every Wonder
  key is optional-at-parse, so no existing file needs a byte edited.
- **Both rows load:** `StructureCatalog.All` contains `standing-stones` (`WonderScope.Sector`,
  `WonderRarity.Common`, one `LoamGenerationRate`/`Sector` effect, `RelicCost >= 1`) and
  `sunspire-throne` (`WonderScope.Empire`, `WonderRarity.Unique`, one `LoamGenerationRate`/
  `Empire` effect, `RelicCost >= 1`).
- **Reserved scope still refused:** a probe `wonderScope: "World"` row fails `Validate` naming the
  reserved scope (`StructureCatalog.cs:396-399`).
- **Reserved kinds still refused:** probe `DefensePower`/`AuraGrant`/`EmpireBuff` effects each fail
  `Validate` naming the reserved kind (`:408-411`).
- **Pairing enforced:** a probe row with `WonderScope` set and `WonderRarity` absent (or vice
  versa) fails (`:393-395`); a probe Wonder with `RelicCost = 0` fails (`:423-424`).
- **Cap reads stay tunable:** `ExistenceCapFor(Empire, Unique)` returns the tuning file's number
  (changing the file changes the cap with no code change); `ExistenceCapFor(any, Common)` returns
  `long.MaxValue`.
- **Names are authored, never ids:** both rows carry a human `name` (`Standing Stones`,
  `Sunspire Throne`) — the composer/card reads the name, never `structureId`, per GG-62.

## Boundaries

- **Always:** hand-authored rows under `gk-data/packs/fusion/data/seed/structures/wonder/` with `AUTHORED` provenance;
  closed-vocabulary spellings exact-case; caps referenced by tunable key, never literals; one effect
  per row with `Scope == WonderScope`; `RelicCost >= 1` on every Wonder row.
- **Ask first:** a third Wonder row (proves demand before growing the population); giving the
  structures generator Wonder support (a generator-program decision, not this module's side effect);
  registering any reserved scope/kind as live (needs its named prerequisite work first).
- **Never:** hand-editing any shipped row to turn a test green (a failing seed test is a stale test
  or a generator defect — never a prompt to edit emitted data); a second Wonder-content generator
  beside the structures adapter; wire/adapter/fold/FE work (owed to `wonder-composer`/
  `wonder-display` + Phase 4A.3/4B); touching `gk-core/data/tuning/loam-relics-wonders.v1.json` from this
  module; `World`/`Multiverse` or reserved-kind rows presented as buildable content.

## Success criteria

1. Two seed files exist at `gk-data/packs/fusion/data/seed/structures/wonder/standing-stones.json` and
   `sunspire-throne.json`, AUTHORED, on legal role/slot pairs. 2. Both load through the unmodified
   `StructureCatalog.All` pipeline; all shipped rows byte-identical. 3. Reserved-scope and
   reserved-kind probe rows still fail `Validate` loud. 4. No cap literal appears in rows or prose —
   caps resolve only through `WonderPolicy` + tuning. 5. `guard-dal.py` green (no SQL).
   6. `wonder-composer`/`wonder-display` can cite these rows as their content dependency.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `standing-stones` row (`Sector`/`Common`, `LoamGenerationRate`/`Sector`, `RelicCost >= 1`) | `wonder-composer` — reachable-first pickable row with minimum recipe; `wonder-display` — sector card identity + effect reading |
| `sunspire-throne` row (`Empire`/`Unique`, `LoamGenerationRate`/`Empire`, `RelicCost >= 1`) | `wonder-composer` — capped row exercising the live-count line; `wonder-display` — Empire reading + upkeep attribution |
| Wire-field gap (`SlotView` has no Wonder facet; catalog/slot wire has no scope/rarity/cost/cap fields) | Phase 4A.3/4B backend-reads task — must land before `wonder-composer`/`wonder-display` can render live counts or identity |
| Authored-row precedent (`wonder/` partition, `AUTHORED` provenance) | Any future Wonder row — copy the shape, cite the section |

## Design-gate checklist

```
[x] Subsystems: world-map structure catalog + seed corpus (Core/Data-adjacent content) — no
    Status/ActorHub/Combat touched; the two effect kinds that WOULD touch ActorHub
    (DefensePower/AuraGrant) stay refused by Validate, never authored.
[x] Read this session: empire-wonder-surfaces-map.md (full, module 2 row); empire-wonder-surfaces-ideal.md
    (full: §4 tables, §5 module breakdown, §7 chosen shape, §8 tunables, §9.4/§9.7 non-decisions,
    §10 + Owner resolutions); loam-relics-and-wonders/spec-wonder-structure.md (full, §Design 1-6 +
    Tunables); scoped-inventory-hierarchy/spec-legion-cargo.md (full, house style).
[x] Code cited by file:line, opened fresh this session: StructureCatalog.cs (:206-227 facets,
    :316-327 facet parse, :393-426 Validate incl. RelicCost pairing at :423-426);
    StructureSeed/StructureCorpus.cs (:42-48 optional defaults, :65 loadable rule, :93-107
    recursive load, :154-167 Wonder parse); WonderCatalog.cs (:8-60 vocabularies);
    gk-data/packs/fusion/data/seed/structures/extract/well.json (:2-10 provenance, :26-28 role/slot, :37-55 magnitudes,
    :52 Kind); gk-data/packs/fusion/data/seed/structures/bank/reliquary.json (:2-10 provenance, :26-28 Bank/Shrine);
    gk-data/packs/fusion/data/seed/structures/_plan.json (:108-115 Bank/Shrine, :132-143 Extract/Rootbed pairs);
    gk-core/data/tuning/loam-relics-wonders.v1.json (:10-13 caps); contract/types.ts (:863-872 SlotView);
    gk-forge/tools/seedsmith/seedsmith/adapters/structures/ (grep: no Wonder support, planner.py:19 prose
    false positive); corpus-wide grep (no Wonder row ships; no generator provenance under
    gk-data/packs/fusion/data/seed/structures/).
[x] Drift reported: spec-wonder-structure.md's "StructureKind is closed at exactly 5" is stale —
    the real enum has 6 members today (ItemStorage shipped since, StructureCatalog.cs:40-44);
    the staleness does not touch this module (no new Kind proposed either way). No other drift:
    every other cited contract (facets, parse, Validate, caps, SlotView) matched its spec on a
    fresh open.
[x] No §2 invariant contradicted: no SQL (guard-dal trivially green); no cap on a magnitude
    (Unique caps tunable via WonderPolicy, Common explicitly uncapped); no f(Θ) (MaterialTier 0,
    off the ladder); no second ActorHub composer (reserved combat kinds refused, not designed);
    no second ownership root (no item/relic state); no generated-data hand-edit (corpus is
    AUTHORED source; shipped rows untouched); no population-count or generated-text pins.
[ ] Wire fields for live-cap display (SlotView/catalog facets, reachability read) — correctly
    deferred to Phase 4A.3/4B, named in §Design 5, not assumed solved.
[ ] Full display-copy catalog + scope/rarity packs (ideal §8) — wonder-display's module, seeded
    here only with authored row names.
```

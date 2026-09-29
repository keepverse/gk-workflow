# Spec: `storage-content`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `storage-content`, row 3 of the
[empire-inventory-surfaces map](../empire-inventory-surfaces-map.md) (wave 1, no dependency).
Ideal: [empire-inventory-surfaces-ideal.md](../empire-inventory-surfaces-ideal.md) §4 (vault rows),
§8 (vault-room row). Backend SSOT: [scoped-inventory-hierarchy/spec-sector-storage.md](../scoped-inventory-hierarchy/spec-sector-storage.md)
§Design 1–3. House style: `spec-legion-cargo.md`.

## Objective

Ship **one** catalog-loadable `ItemStorage`-kind structure row — the vault a held sector builds —
so the sector-storage backend (`SectorItemCapacity.EffectiveCapacity` + `BuildResolver`) has real
content to read and offer, and the wave-2 `storage-cache-ui` surface has a real room number to
paint. No verb, no UI, no tuning file: one row, through the structures authoring path, never
hand-edited if that path is generated.

Success looks like: `StructureCatalog.IsKnown("relic-vault")` is true from the committed corpus;
a sector with a built `relic-vault` on a `Vault` slot reports `SectorItemCapacity.EffectiveCapacity == 20`;
a `build` order for it on a compatible empty `Vault` slot resolves `build.started:relic-vault`.

## Locked anchors

- **A 6th `StructureKind`, not a second field on `Storage`** (spec-sector-storage §Locked anchors,
  owner Q2 verbatim: *"A new, distinct structure concept for items."*). Already shipped in code:
  `StructureKind.ItemStorage` (`StructureCatalog.cs:40-43`), `StructureDef.ItemStorageCapacityBonus`
  (`StructureCatalog.cs:74-78`), `Validate` non-negative check (`StructureCatalog.cs:370-371`).
- **Slot-bound, additive, fresh-computed capacity** (spec-sector-storage §Design 2): exactly the
  `SectorItemCapacity.EffectiveCapacity` shape already shipped
  (`SectorItemCapacity.cs:14-27` — active-slot gate, additive sum, `checked`, no loam base term).
- **Row-count is the capacity unit** (spec-sector-storage §Design 3): one storage row is one slot,
  never summed `qty`. This module authors the capacity number; the row-count rule itself is untouched.
- **Capacity bonus is content, not a tuning entry** (spec-sector-storage §Tunables correction):
  like `CapacityBonus`, `ItemStorageCapacityBonus` lives per structure row in the seed corpus, never
  in `gk-core/data/tuning/*.json`.
- **LLMs author identity only** (seedsmith Law 2; `StructureDef.MaterialTier` doc comment
  `StructureCatalog.cs:103-115`): the model picks name/flavor/role/slot-kind; deterministic code
  assigns magnitudes. The capacity number below is a **content** value assigned by the planner
  path, not a model guess typed into JSON.
- **Vault-room is a content number with an open value** (ideal §8 row: *"Vault room per structure
  row … exact numbers open"*). This spec fixes the first value (20) so validation is provable;
  rebalancing stays a content edit through the same path.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `StructureKind` closed at 6 with `ItemStorage` ("The fifth thing a structure can do") | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-43`, read in full this session |
| `StructureDef.ItemStorageCapacityBonus` (`long`), documented as never read by loam math | `StructureCatalog.cs:74-78` |
| Corpus parse path already carries the field, optional-default 0 so shipped rows load byte-identical | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:26,137,194-197` (`OptionalLong`, missing/null → 0) |
| `ToStructureDef` maps it; `IsCatalogLoadable` = magnitudes non-null; catalog skips anchor-only rows | `StructureCatalog.cs:272-280` (`BuildRows`), `:289-328` (`ToStructureDef`, `:302` the mapping) |
| `Validate` refuses negative bonus + duplicate id + empty acquisition | `StructureCatalog.cs:350-430` (`:370-371` bonus, `:379-381` acquisition) |
| `SectorItemCapacity.EffectiveCapacity` sums `ItemStorageCapacityBonus` over active `ItemStorage` slots | `gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14-27`, read in full this session |
| `BuildResolver` is kind-agnostic: `IsKnown` + `RequiredSlotKind` match + Seat-range + relic/wonder/cost gates, no `Kind` switch | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:75-138`, read in full this session |
| `SlotKind.Vault` exists (thematically closest ground for item storage) | `spec-sector-storage.md` §What already exists (via `SlotTypeCatalog.cs:7-22,:72`); `garrison-charter` already sits on `Vault` (`generate_corpus.py:460-465`) |
| The 25 shipped rows are **hand-authored** (`_provenance.source == "AUTHORED"` on every row checked), zero model calls | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:1-22` (top note); `gk-data/packs/fusion/data/seed/structures/store/granary.json:7-10`, `store/coffer.json:7-10` |
| `granary` (loadable) carries `magnitudes.structureKind == "Storage"`, `capacityBonus: 300`, and **no** `itemStorageCapacityBonus` key (defaults 0 through `OptionalLong`) | `gk-data/packs/fusion/data/seed/structures/store/granary.json:37-55` |
| `coffer`/`stockyard` (Store-role) are anchor-only: no `magnitudes` block, hence registered but not catalog-loadable | `gk-data/packs/fusion/data/seed/structures/store/coffer.json:1-41` (no `magnitudes` key) |
| `_plan.json` pairs `Store` only with `Wildland`; `Enable` already pairs with `Vault` | `gk-data/packs/fusion/data/seed/structures/_plan.json:107-176` (`legalRoleSlotPairs`) |

### Real gap

| Gap | What would have to be built |
|---|---|
| **No `ItemStorage` row exists anywhere in the corpus** | Confirmed this session: zero `itemStorageCapacityBonus` keys and zero `"structureKind": "ItemStorage"` hits under `gk-data/packs/fusion/data/seed/structures/` (grep); zero `ItemStorage` hits under `gk-forge/tools/seedsmith/seedsmith/adapters/structures/` except none |
| **The generator cannot express one.** `_magnitudes()` has no `item_storage_capacity_bonus` parameter and emits no `itemStorageCapacityBonus` key | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:133-193` (full signature + emitted dict — `capacity_bonus` present, item-storage twin absent) |
| `ROLE_TO_STRUCTURE_KIND` maps `Store → Storage` with no `ItemStorage` member — and is **provably not the import path** (Correction 2: kind is authored per-row in `magnitudes.structureKind`, never derived from role) | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:65-87`; `generate_corpus.py:165-173` (why the dict is already wrong against shipped rows, left as-is) |
| No `Store ↔ Vault` legal pair exists for the planner | `_plan.json:173-175` (`Store`↔`Wildland` only) vs `Enable`↔`Vault` precedent (`_plan.json:128-131`) |

## Design

### 1. The row — `relic-vault` ("Relic Vault")

One row, `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json` (role directory `store/`, matching the
one-row-per-file `file_tree()` convention, `generate_corpus.py:471-480`):

| Field | Value | Owner / notes |
|---|---|---|
| `id` / `structureId` | `relic-vault` | AUTHORED identity (kebab, `WorldIds.RequireKebab`) |
| `name` | `Relic Vault` | AUTHORED identity (display string, sibling of anchor per `_row`, `generate_corpus.py:204-224`) |
| `anchor.role` | `Store` | Reuses the existing 10-role vocabulary — no new role (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:12`) |
| `anchor.requiredSlotKind` | `Vault` | New pairing `Store ↔ Vault` (generator fix §2); thematically the vault ground, following `garrison-charter`'s `Enable ↔ Vault` precedent |
| `anchor.strengthBand` | `timber` | AUTHORED ordinal (follows `coffer`'s timber/steep precedent) |
| `anchor.rarity` | `grafted` | AUTHORED ordinal (same precedent) |
| `anchor.costProfile` | `steep` | AUTHORED band, never an amount (schema SS1) |
| `anchor.acquisitionPaths` | `["built"]` | Non-empty (Validate refuses empty, `StructureCatalog.cs:379-381`) |
| `anchor.controlPoint` | `true` | Every economic row holds its ground (all dumped rows `true`) |
| `anchor.family` | `loam-structures` | Same family as every Store row (`generate_corpus.py:110`) |
| `magnitudes.structureKind` | `ItemStorage` | AUTHORED fact per Correction 2, never derived from role |
| `magnitudes.itemStorageCapacityBonus` | **`20`** | **The content number.** First vault-room value (ideal §8: numbers open → fixed here). `long`. Mirrors spec-sector-storage's own worked example (capacities 20 and 30). Granary precedent: `capacityBonus: 300` for loam; the item axis starts smaller because one row is one slot (§Design 3 of the parent spec) |
| `magnitudes.cost` | `200` | Planner-assigned magnitude (granary 150 / soul-conduit 250 band; steep profile) |
| `magnitudes.buildTurns` | `2` | Planner-assigned (granary precedent) |
| `magnitudes.capacityBonus` | `0` | Explicit zero — the two axes never bleed (`StructureCatalog.cs:74-78`) |
| everything else | C# defaults | `yieldMultiplierMilli: 1000`, `materialTier: 0` (indestructible, pre-siege content), `blocksMovement/LineOfFire: false`, `obstacleKind: "None"`, `coverPowerMilli/Radius: 0`, `entryStaminaMultiplierMilli: 1000`, `visionRangeTiles: null` (tuning fallback), `containerId: null` (nothing to roll) |
| `_provenance` | `{"source": "AUTHORED", "citation": "empire-inventory-surfaces storage-content §Design 1; ideal §8 vault-room row"}` | Same shape as every shipped row |

`Validate` outcome by construction: kebab id ✓, unique ✓, named ✓, non-negative ✓,
acquisition non-empty ✓, no Wonder pairing ✓, `RelicCost` 0 ✓.

### 2. Authoring path — hand-authored row, no generator fix owed (RULING 2026-09-15 strengthen pass)

**Decision: author `relic-vault.json` by hand, same as every shipped row.** Correction of this
section's own first draft (which demanded a generator fix): verified fresh — rows are
hand-authored (`_dumped` stamps `AUTHORED`, `generate_corpus.py:227-228`; file header `:1-22`
states zero model calls; no `_meta.model` provenance anywhere in the tree), and `write_corpus`
only writes `file_tree()` entries without deleting (`:483-491`), so a hand-added file survives
regen. There is no fork risk because there is no generated stamp to fork from. (A future
`_magnitudes()` `item_storage_capacity_bonus` key for generated `Store` rows is a structures-program
enhancement, explicitly NOT this module's deliverable.) This converges with
`spec-wonder-content.md` §Design 3 — both content specs author rows; neither touches the generator:

1. Write `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json` with the §Design 1 shape and the
   `_provenance` citation above.
2. Prove survival: run `write_corpus` (or its `--check` mode) and show `relic-vault.json`
   byte-identical afterwards plus the tree still byte-identical otherwise.
3. Same hardening as before: extend `tests/test_structure_corpus.py`'s authored-kind asserts
   with `by_id["relic-vault"]["structureKind"] == "ItemStorage"`.

### 3. Validation (three reads, no new verb)

1. **Catalog loads:** `StructureCorpus.Load("gk-data/packs/fusion/data/seed/structures")` → `StructureCatalog.Configure`
   → `All` contains `relic-vault`, `IsKnown("relic-vault")` true, `Get("relic-vault").Kind ==
   ItemStorage`, `ItemStorageCapacityBonus == 20`. Fails today (no such row); passes after §2.
2. **`EffectiveCapacity` reads it:** sector with one built `relic-vault` (active slot, `Vault`
   kind) reports `20`; with a second future ItemStorage row reports the sum; under-construction
   (`ConstructionTurnsRemaining > 0`) and unknown-id slots contribute 0
   (`SectorItemCapacity.cs:14-27` gates). Mirrors spec-sector-storage's own testing strategy
   (20 + 30 = 50 case generalizes to 20 + N).
3. **`BuildResolver` offers it:** `build` order with `StructureId: relic-vault` on an empty
   `Vault`-kind slot, own faction, affordable, resolves `build.started:relic-vault`
   (`BuildResolver.cs:75-89` — `IsKnown` + `RequiredSlotKind` match, no Kind switch to extend).
   Wrong slot kind refuses `build.wrong-slot-kind` by the existing line, proving the `Vault`
   pairing is real.

## Tunables / content homes

| Number | Home | Notes |
|---|---|---|
| `itemStorageCapacityBonus` = 20 for `relic-vault` | `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json` `magnitudes` (content, hand-authored via §2) | Per spec-sector-storage §Tunables correction: content-authored per row like `CapacityBonus`, never `gk-core/data/tuning/*.json` |
| `cost` = 200, `buildTurns` = 2 (planner-assigned) | Same row, same path | Magnitudes, deterministic assignment — not model guesses (Law 2) |
| `Store ↔ Vault` legal pair | `_plan.json` + `adapters/structures/planner.py` | Generated planning artifact, regenerated not edited |
| No entry in `data/tuning/scoped-inventory.v{n}.json` or any tuning file | — | Deliberate: this module authors zero tuning keys |
| Future rebalances (20 → N, second ItemStorage row) | Same corpus path (§2 rerun) | Content edits, never tuning-file or code edits |

## Numeric types

`ItemStorageCapacityBonus` and `EffectiveCapacity` return: `long` (magnitude — matches
`CapacityBonus`'s own type; spec-sector-storage §Numeric types). `cost`: `long`. `buildTurns`:
`int` (turn count, structural). Accumulation in `SectorItemCapacity.cs:14-27` is plain
`long` addition (`:26` is `return checked(bonus)`, an identity check, not the sum — corrected
2026-09-15); overflow is unreachable in practice (a few structure bonuses, `long` range), and the
file's own exemption comment (`:9`) states the structural-limit rationale.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SectorItemCapacity"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StructureCatalog"
python gk-core/scripts/guard-dal.py        # no SQL in this module — must stay green trivially
```

Corpus-side (after §2): seedsmith structure-corpus tests per `gk-forge/tools/seedsmith/tests/test_structure_corpus.py`.

## Structure

```
gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py  UNTOUCHED (no generator fix owed — ruling 2026-09-15 §Design 2)
gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py (+ _plan.json)  UNTOUCHED (same ruling)
gk-forge/tools/seedsmith/tests/test_structure_corpus.py                    EXTENDED — by_id["relic-vault"]["structureKind"] == "ItemStorage" corpus assert (survival proof: write_corpus regen leaves relic-vault.json byte-identical, §Design 2)
gk-data/packs/fusion/data/seed/structures/store/relic-vault.json                       NEW, hand-authored (AUTHORED provenance, §Design 1 + §Design 2 citation) — NO generate_corpus.py / planner.py modification (ruling 2026-09-15 §Design 2)
tests/.../SectorItemCapacityTests.cs (+ catalog import tests)     EXTENDED — §Design 3 asserts
UNTOUCHED: StructureCatalog.cs (ItemStorage kind/field/Validate already shipped); SectorItemCapacity.cs;
           BuildResolver.cs (kind-agnostic, zero change); LoamPhases.cs; all 25 existing seed rows;
           anchor/schema.py ROLE_TO_STRUCTURE_KIND (dead mapping, чужой cleanup);
           rpg_item/rpg_item_stock schema; gk-core/data/tuning/**.
```

## Code style

No production C# in this module (content-only + generator Python). Generator diff mirrors the
existing `capacity_bonus` line exactly:

```python
# mirrors capacity_bonus one line above — a second axis, never a reuse of it.
"itemStorageCapacityBonus": item_storage_capacity_bonus,
```

## Testing strategy

- **Catalog contains the row:** `IsKnown("relic-vault")`, `Get.Kind == ItemStorage`,
  `ItemStorageCapacityBonus == 20` — contract (closed enum + authored value), never a population count.
- **Capacity reads it:** one built `relic-vault` → `EffectiveCapacity == 20`; under-construction →
  0; loam-`Storage` granary on the same sector contributes 0 to the item axis (two axes never bleed).
- **Row-count unit untouched:** asserted by the parent spec; this module adds no `qty` semantic.
- **Resolver offers it:** `build.started:relic-vault` on empty `Vault` slot; `build.wrong-slot-kind`
  on a `Wildland` slot — proves the new pairing without touching resolver code.
- **Regeneration is byte-stable:** rerun `write_corpus` → zero diff (idempotency contract,
  `generate_corpus.py:471-480`); the 8 dumped rows byte-identical (the `OptionalLong` default-0
  guarantee, `StructureCorpus.cs:194-197`).
- **Guardrail discipline:** no assert on corpus size (25 → 26 is a reading, not a constant —
  validation-ssot); assert envelope, closed-enum membership (`structureKind ∈ {6 C# members}`),
  uniqueness, and the `Store ↔ Vault` join closure instead.

## Boundaries

- **Always:** regenerate through `write_corpus`, never hand-edit `gk-data/packs/fusion/data/seed/structures/**`;
  `magnitudes.structureKind` authored per row, never derived from `role` (Correction 2);
  capacity additive + fresh + `checked`; row-count unit.
- **Ask first:** a second ItemStorage row or a different bonus value (content call, owner confirms
  at `/spec` gate); a weight gate on sector storage (parent spec §2's explicit non-ask — still needs
  a named decision).
- **Never:** `ROLE_TO_STRUCTURE_KIND`-derived kind; a `gk-core/data/tuning/*.json` entry for the bonus;
  reusing `CapacityBonus` for item capacity (owner-rejected, §Locked anchors); an owner/faction
  column on any storage table; touching the 25 shipped rows' bytes (beyond the additive file);
  a `BuildResolver` Kind switch (kind-agnosticism is the feature).

## Non-touch list

`StructureCatalog.cs`, `StructureCorpus.cs`, `SectorItemCapacity.cs`, `BuildResolver.cs`,
`LoamPhases.cs`, `WorldState.cs` / `SlotTypeCatalog.cs`, `anchor/schema.py`
(`ROLE_TO_STRUCTURE_KIND` + 10-role vocab), all 25 existing `gk-data/packs/fusion/data/seed/structures/**/*.json`
bytes, `rpg_item` / `rpg_item_stock` schema, `gk-core/data/tuning/**`, `WorldEndpoints.cs` (no REST in
this module), any FE surface (`SectorInspector`, `StoragePage`, `RelicsLayer` — wave-2 consumers,
not this module's host).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `relic-vault` catalog row (`Kind == ItemStorage`, bonus 20, `RequiredSlotKind == Vault`) | `claim-endpoints` / `storage-cache-ui` (wave 2): the vault-room number the panel paints and the `build` target the panel names |
| `Store ↔ Vault` legal pair | Any future ItemStorage row (second vault, factional variant) — the pairing precedent, not a one-off |
| `_magnitudes(item_storage_capacity_bonus=…)` generator capability | `structure-planner` (27): anchor-only Store rows (`stockyard`, `coffer`) gain loadable magnitudes through this same key when planned |

## Design-gate checklist

```
[x] Subsystems: world-map sector/structure content (Core catalog + seedsmith structures adapter).
    No Status/ActorHub/Combat/Data-verb/FE subsystem touched.
[x] Read this session: empire-inventory-surfaces-map.md row 3; empire-inventory-surfaces-ideal.md
    §4 (vault rows) + §8 (vault-room row); spec-sector-storage.md §Design 1-3 + §Tunables correction;
    spec-legion-cargo.md (house style); StructureCatalog.cs (full); StructureCorpus.cs (full);
    SectorItemCapacity.cs (full); BuildResolver.cs (full); generate_corpus.py (full);
    anchor/schema.py (ROLE_TO_STRUCTURE_KIND); _plan.json (legalRoleSlotPairs);
    gk-data/packs/fusion/data/seed/structures/store/granary.json + coffer.json (provenance + magnitudes shape).
[x] Checked decisions.md for a lock covering this: scoped-inventory SSOT (ItemStorage kind,
    additive capacity, content-not-tuning) — followed, not re-litigated. No
    "empire inventory surfaces" lock contradicts this row.
[x] Every factual claim cites file:line (see Built/Real-gap tables).
[x] Verified claims against CODE, not comments: ItemStorage kind/field/Validate read in
    StructureCatalog.cs; OptionalLong default read in StructureCorpus.cs; kind-agnosticism read
    in BuildResolver.cs (no Kind switch); generator incapacity read in _magnitudes signature;
    AUTHORED provenance read in two seed files; Store↔Wildland-only read in _plan.json.
[x] Read the surrounding section of every rule quoted (ideal §8 tunables-home table, parent spec
    §Tunables correction, Law 2 identity/magnitude split, Correction 2 authored-kind rule).
[x] Tested (not assumed) constraints: zero ItemStorage/magnitudes-key hits under gk-data/packs/fusion/data/seed/structures
    and the structures adapter (grep); no golden/test movement claimed — spec phase runs no suite.
[x] Nothing contradicts a §2 invariant: SQL untouched (content-only); no progression ceiling
    (per-sector structural limit, exempt, commented in parent spec); no f(Θ); no second Hub/composer;
    no second ownership root; SOLID: extends the corpus path, no parallel content pipeline.
[x] Corrections propagated: generator incapacity named in Real gap + §Design 2 + Structure +
    Testing (not prose-only); content-not-tuning in Tunables + Non-touch + Boundaries.
[x] No assertion pins a derived-population count, item total, generated name/description text, or
    per-cycle outcome. (26-row total is a reading; guardrails assert enum membership, uniqueness,
    join closure. The fixed bonus 20 is closed-vocabulary content for this row with a stated reason
    — the first vault-room value the ideal left open — not a population literal.)
[x] No event-refreshed cache introduced. (N/A — content row.)
[x] No acceptance criterion fixes an ordering. (N/A — three order-independent reads in §Design 3.)
[x] No actor combat/derived magnitude produced or consumed.
[x] No SOLID-violating parallel path: one corpus, one _magnitudes key, one Store↔Vault pair —
    no second generator, no hand-edited fork, no tuning-file twin.
[ ] Exact planner-source edit for the Store↔Vault pair (§2.2) not traced to a line this session —
    named as implementation's first task (planner.py vs _plan.json ownership), not assumed solved.
```

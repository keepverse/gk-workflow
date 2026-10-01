# Spec: `structure-bands`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `structure-bands` · **Map row:** 4 ·
**Wave:** 1 · **Ideal id:** I3
**Depends on:** `band-reader`, `structures-adapter` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19, including the decision that
folds the three hand-authored rows into the generator (map §12). No build authorized until this spec is
approved.

---

## 1. Objective

Every structure number leaves the seed. The anchor keeps identity, the ordinals, and the **mechanism
enums**, which are not magnitudes. Every number the catalog uses resolves from a `structure-seed` tuning
band through `band-reader` at load. The corpus has **one writer**, `generate_corpus.py`, and is
regenerated through it, never by hand. `LoamPolicy`'s second, unread copy of the structure numbers is
deleted.

**Done means:**
- The resolved `StructureCatalog.All` is **byte-identical** before and after.
- No seed file under `gk-data/packs/fusion/data/seed/structures/` contains a JSON number.
- Every structure number has exactly one source: a band row in `structure-seed.v{n}.json`.

This is a refactor (T7). No resolved number changes here. A rebalance is a later `v{n+1}` publish.

## 2. Scope and non-goals

**In scope.**
- The anchor widening: mechanism enums and magnitude ordinals.
- The band tables.
- Folding `relic-vault`, `standing-stones` and `sunspire-throne` into the generator's source.
- Deleting `magnitudes` from the seed and the C# reader.
- Deleting `ROLE_TO_STRUCTURE_KIND`.
- Deleting the `LoamPolicy` structure magnitudes.
- Retargeting the test oracles.
- Correcting the two stale notes.

**Not in scope.**
- New roles (`exchange-role`), new rows (`trade-structure-rows`), and any rebalance.
- Giving the 17 identity-only rows numbers. They stay registered but not loadable (§5.4), because
  turning them on would change the catalog and would be content design, not a refactor.
- Changing any `StructureDef` field or type.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The catalog and its validation | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:289-328`, `:350-430` |
| Built | The tier ladder in tuning | `gk-core/data/tuning/structure-seed.v1.json:17` |
| Built | The generator is pure and sorted-key, and a rerun is byte-identical | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:471-493`; `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:198-216` |
| Wiring gap | Numbers are written as literals by the generator (`cost=200`, `build_turns=2`, …), transcribed from `loam.v4.json` by hand | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:241-318` |
| Wiring gap | The C# `magnitudes` block and its parse | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:20-48`, `:126-168` |
| Wiring gap | The generator's `_magnitudes()` cannot express `itemStorageCapacityBonus`, `wonderScope`, `wonderRarity`, `wonderEffects` or `relicCost`, which is why the three rows that carry them sit outside it | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:133-193`; `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json`; `gk-data/packs/fusion/data/seed/structures/wonder/*.json` |
| Wiring gap | The two wonder files are not sorted-key JSON (`wonderScope` after `yieldMultiplierMilli`), so they were written by no writer the generator knows | `gk-data/packs/fusion/data/seed/structures/wonder/standing-stones.json` |
| Wiring gap | `wonder/` holds rows whose `partition` is `Extract` and `Bank`. The generator groups by role directory and asserts it (`test_file_tree_groups_by_role_directory`) | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:296-302` |
| Wiring gap | `ROLE_TO_STRUCTURE_KIND` is wrong against shipped rows (`hatchery`, `soul-conduit`, `extractor` are `Yield`). The C# catalog ignores it, and a test suite still asserts it | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:64-86`; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:282-288`; `gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py:120-153` |
| Wiring gap | `LoamPolicy` exposes 17 structure magnitudes. Production reads only `WaystationRangeHops` (grep this session: `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:192`, `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:522`). The rest are read by tests as oracles | `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs:122-191`; `gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamStructuresTests.cs`, `LoamTextureTests.cs`, `gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs` |
| Wiring gap | The seedsmith oracle test reads `loam.v4.json`, while the server loads `loam.v5.json`. Their `structures` blocks are equal today (compared this session) | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:70-75`; `gk-core/src/FusionRpg.Server/Program.cs:36` |
| Wiring gap | Two notes say per-row magnitudes are seed content, which contradicts `structure-seed-ideal.md` §7 | `gk-core/data/tuning/loam-relics-wonders.v1.json` `_meta.note`; `gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs:10-11` |
| Real gap | The band tables for every numeric field | — |

**The shipped values the bands must reproduce** (every playable row, read this session, a reading):

| `StructureDef` field | Distinct shipped values |
|---|---|
| `Cost` | 0, 150, 200, 250, 300 |
| `BuildTurns` | 0, 2, 3, 4, 6 |
| `YieldMultiplierMilli` | 1000, 1500, 2000 |
| `FlatYieldPerTurn` | 0, 15, 20 |
| `CapacityBonus` | 0, 300 |
| `ItemStorageCapacityBonus` | 0 (default), 20 |
| `ConstructRubbleCost` / `ConstructIronworkCost` | 0, 4 / 0, 1 |
| `MaterialTier` | 0, 1 |
| `CoverPowerMilli`, `CoverRadius` | 0 |
| `EntryStaminaMultiplierMilli` | 1000 |
| `VisionRangeTiles` | the fog default (every row `null`) |
| `RelicCost` | 0 (default), 1, 3 |
| `WonderEffectDef.ValueMilli` | 0 |

`costProfile` cannot reproduce `Cost` today. `moderate` covers 0 (`moat`), 150, 200 and 300, and
`steep` covers 0, 200 and 250 (map §11 item 5).

## 4. Principles as they bind this module

- **The model writes identity, deterministic code writes magnitude** (seedsmith P1). After this module,
  no seed row carries a number. A model could still choose among ordinals, but here the **planner** (and
  for the 28 existing rows, the hand-written generator source) fixes every ordinal. No model is involved.
- **Four ownership levels** (`item/seed-contract.md` §2). Numbers are DERIVED, computed at load, "a
  column, never the seed". Ordinals and mechanism enums are VALIDATED or AUTHORED, and each carries its
  level in `OWNERSHIP`.
- **Bands, never numbers** (`item/seed-contract.md` §3). An ordinal names a rung, and the tuning file
  owns the value.
- **One mechanism.** Map §5.4 obligation 2 decided this by principle: widen the ordinal vocabularies
  until every shipped number is some rung's value. A per-structure override table would be a per-row
  magnitude under another name.
- **Generated data is never hand-edited.** The tree is rewritten only by `write_corpus()`.
- **Refactor and rebalance never land together** (T7).
- **Range.** Resolved integers are `long`. Narrowing into the shipped `int` fields (`BuildTurns`,
  `MaterialTier`, the `*Milli` ratios, `CoverRadius`) is `checked`, and it throws, never wraps. The
  `*Milli` fields are bounded ratios, exempt from the no-ceiling rule as ratios (`PRINCIPLES.md` §5).

## 5. Design

### 5.1 One writer for the tree (owner decision, 2026-09-19)

`relic-vault`, `standing-stones` and `sunspire-throne` move into `generate_corpus.py`'s source as
**hand-authored rows with no model involved**, next to the other 25, each keeping its
`_provenance.citation`. The 2026-09-15 ruling quoted at `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:320-325`
("rows are hand-authored, no generator fix owed") keeps its intent: these rows remain hand-authored, and
the generator is hand-written Python. The change is only that they now have one writer.

The wonder rows are written to their **role** directory, as every other row is:
`extract/standing-stones.json` and `bank/sunspire-throne.json`. `wonder/` is removed. The decision row
at `docs/architecture/decisions.md` — '`exchange` structure role (2026-09-19)' already records *"`wonder/` is a seed folder, not a role."* The
`_provenance.citation` strings of the two wonder rows mention the folder; they are left as authored.

### 5.2 The anchor widening

Every added field is a string enum or boolean, required, with a description carrying a negative clause.
`none` is a member wherever absence is meaningful. No field name hits the audit's deny list
(`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py:18-21`).

| Field | Level | Vocabulary | Resolves to |
|---|---|---|---|
| `structureKind` | VALIDATED | `StructureKind` names (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:10-49`) + `none` | `StructureDef.Kind`. **`none` = identity-registered, not catalog-loadable** (§5.4). **Round 6 C2:** every feature building carries the one neutral member `Feature`, never `none` — see §5.4a |
| `obstacleKind` | VALIDATED | `ObstacleKind` names (`gk-core/src/FusionRpg.Core/World/Siege/Obstacles.cs:10`) | `StructureDef.Obstacle` |
| `blocksMovement`, `blocksLineOfFire` | VALIDATED (boolean) | — | the same-named `StructureDef` fields |
| `wonderScope` | VALIDATED | `Sector · Empire · none` (the registered members; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:395-398` rejects the others) | `WonderScope` |
| `wonderRarity` | VALIDATED | `Common · Unique · none` | `WonderRarity` |
| `wonderEffects[]` | VALIDATED items `{kind, scope, valueBand}` | `kind` ∈ registered `WonderEffectKind`; `scope` as `wonderScope` | `WonderEffectDef` |
| `containerId` | VALIDATED | a container id or `none` (planner `CONTAINER_POLICY`, `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:67-71`) | `StructureDef.ContainerId` |
| `costProfile` | AUTHORED ordinal, **widened** | `free · low · standard · high · premium` | `Cost` |
| `buildTimeBand` | AUTHORED ordinal | `instant · short · medium · long · epic` | `BuildTurns` |
| `yieldMultiplierBand` | AUTHORED ordinal | `unchanged · raised · doubled` | `YieldMultiplierMilli` |
| `flatYieldBand` | AUTHORED ordinal | `none · trickle · steady` | `FlatYieldPerTurn` |
| `capacityBand` | AUTHORED ordinal | `none · large` | `CapacityBonus` |
| `itemCapacityBand` | AUTHORED ordinal | `none · small` | `ItemStorageCapacityBonus` |
| `constructRubbleBand`, `constructIronworkBand` | AUTHORED ordinals | `none · light` each | the two construct costs |
| `strengthBand` | AUTHORED ordinal, **widened** | `indestructible · rubble · timber · stone` | `MaterialTier` (0, 1, 2, 3) |
| `coverTier` | AUTHORED ordinal (unchanged) | `none · light · heavy · trench` | `CoverPowerMilli`, `CoverRadius` |
| `entryBand` | AUTHORED ordinal | `normal` | `EntryStaminaMultiplierMilli` |
| `visionBand` | AUTHORED ordinal | `default` | `VisionRangeTiles`. `default` is the one ordinal with no table row: it means "read `SiegeTuningPolicy.Fog.DefaultVisionRangeTiles`", the resolution already at `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:313`. A copied number would drift from that tunable |
| `relicCostBand` | AUTHORED ordinal | `none · minor · major` | `RelicCost` |

`reach`, `tempo`, `footprint` and `targetPreference` are unchanged. They are still ordinals with no
consuming `StructureDef` field, and they get no band until a field reads them. A band with no reader is
a converter with no consumer, the rule stated at `gk-core/src/FusionRpg.Core/World/Bands.cs:7-8`.

Rung names describe meaning, never value. Each vocabulary is exactly wide enough to reproduce §3's table:
every shipped value is one rung, and no rung exists without a shipped value. `tier`-named fields stay out
because `tier` and `materialtier` are audit deny names.

### 5.3 The band tables

The next `structure-seed` version adds `bands.<axis>.<ordinal> = <long>` for every axis in §5.2. The
values are copied from the shipped rows, and a test proves the copy (§8 criterion 1). The existing
`bands.tierLadder` becomes `["indestructible","rubble","timber","stone"]`, and `bands.materialTier` (from
`band-reader`) gains `indestructible: 0`. That is one reviewed widening of a closed vocabulary. The
planner's `tier_ladder_completeness` metric now needs a row at every rung
(`gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:103-107`). Rows exist at every rung today.

It is published through `gk-core/tools/tuning/publish.py --add-key`, extending the tool only if a nested object
cannot be added. It is never hand-edited.

### 5.4 The C# side

- `StructureMagnitudes` and `WonderEffectMagnitude` are deleted. `StructureCorpusRow` carries the
  ordinals and enums as strings (VALIDATED at parse through `band-reader`'s `RequireMember`).
- `IsCatalogLoadable` becomes `StructureKind != "none"`. The 17 identity-only rows stay registered and
  not loaded, exactly as today (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:275`).
- `StructureCatalog.ToStructureDef` resolves every number through `SeedBandResolver.Resolve`, narrowing
  with `checked` where the field is `int`. `Enum.Parse` calls stay for the enums, now fed from anchor
  fields.

### 5.4a `none` is for identity-only rows, never for a feature building (round 6 C2)

The `none` rule above was read as *"a feature building stays `none` until its consumer adds a kind"*, which
made every round-4 feature building permanently unloadable (global audit C2). **Owner decision C2
(2026-09-20):** all feature buildings load under **one neutral `StructureKind.Feature`**, and
`StructureKind.Exchange` is withdrawn. Ruling X1's wording is amended to allow this one neutral kind — a
kind is still never a feature gate; the gate is `trade-foundation` `sector-features` reading `FeatureUnlock`.

- The `structureKind` vocabulary gains `Feature` when the C# member lands. The member is a reviewed
  closed-vocabulary widening owned by the field's first reader, `trade-foundation` `sector-features`
  (which also lands `StructureDef.FeatureUnlock`); this program only emits the value. `Feature` does
  nothing in the loam or siege economy — the `Obstacle` precedent of a kind that deliberately does nothing
  economic (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:32-38`) — and its whole behaviour is its
  `FeatureUnlock`.
- `none` keeps exactly one meaning after C2: **identity-registered content no mechanism consumes** —
  exemplars (`world-exemplars` §5), wonders and the other identity-only rows. A row with a non-`none`
  `featureUnlock` and `structureKind: none` is a defect the anchor audit refuses (`trade-structure-rows`
  §7 criterion 7).
- Loadability is unchanged in shape: `magnitudes`/ordinals present **and** `structureKind != none`.

### 5.5 Generator and schema changes

- `_magnitudes()` is deleted. `_anchor()` gains the §5.2 fields with keyword defaults equal to today's
  defaults, mapped to rungs, so each row names only what differs. The row values are transcribed from the
  current `magnitudes` blocks to rungs, with the mapping in one table in the generator's docstring.
- `ROLE_TO_STRUCTURE_KIND`, `structure_kind_for` and `NoStructureKindMapping` are deleted, and so are
  their tests (`gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py:120-153`).
- `test_strength_band_is_the_only_magnitude_ordinal` (`:76`) is a stale test and becomes "every
  magnitude ordinal has a band axis in tuning".
- The `role` description's claim that *"StructureKind, DERIVED from this field"* is rewritten
  (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/descriptions.py:21-24`). `costProfile`'s
  description changes from a material ratio to a cost band, with a negative clause (*"not which
  materials, not an amount"*).
- `test_dumped_magnitudes_match_the_real_tuning_files_not_a_hand_copied_number`
  (`gk-forge/tools/seedsmith/tests/test_structure_corpus.py:70`) is replaced by "every loadable row's ordinals are
  keys in the published band tables". Its `loam.v4.json` read disappears with it.

### 5.6 `LoamPolicy` deletion

Delete the 17 structure accessors at `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs:124-191`, keeping
`WaystationRangeHops` (`:147`). It is a build rule of the movement domain, not a structure magnitude. It
stays in loam tuning, which is the smaller change, and both production readers keep working unchanged.
Publish `loam.v{n+1}` with the `structures` block reduced to `waystationRangeHops`. Update `LoamTuning`'s
parser in the same change, and point `gk-core/src/FusionRpg.Server/Program.cs:36` at the new version.

Retarget the oracles to `StructureCatalog.Get(id)`:
- `gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamStructuresTests.cs` (27 references)
- `gk-core/tests/FusionRpg.Core.Tests/World/Loam/LoamTextureTests.cs` (3)
- `gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs` (1)

These are counts from this session.

### 5.7 Stale notes

- Republish `loam-relics-wonders` with `_meta.note` corrected: per-row numbers live in `structure-seed`
  band tables, keyed by the seed's ordinals.
- Correct the doc comment at `gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs:10-11` the same way.

### 5.8 Temporary-corpus tests

There are 63 `StructureCorpus.Load` call sites across `tests/` today (a reading). They write
`magnitudes` JSON. A shared builder from `band-reader`'s test helper emits ordinal rows plus a
band-table fixture, and each call site moves to it mechanically. Where a test needs a number no shipped
rung has, for example a cost that exercises an overflow path, the fixture tuning adds a fixture-only rung.
The test does not bend a shipped row.

## 6. Tunables

| File | Keys | Unit |
|---|---|---|
| `data/tuning/structure-seed.v{n+1}.json` | `bands.cost.*` (loam), `bands.buildTurns.*` (turns), `bands.yieldMultiplierMilli.*` (per-mille), `bands.flatYieldPerTurn.*` (loam/turn), `bands.capacityBonus.*` (loam), `bands.itemStorageCapacityBonus.*` (items), `bands.constructRubbleCost.*`, `bands.constructIronworkCost.*` (stock units), `bands.materialTier.*` (tier index), `bands.coverPowerMilli.*` (per-mille), `bands.coverRadius.*` (cells), `bands.entryStaminaMultiplierMilli.*` (per-mille), `bands.relicCost.*` (relics), `bands.wonderEffectValueMilli.*` (per-mille); `bands.tierLadder` widened | as listed (T6) |
| `data/tuning/loam.v{n+1}.json` | `structures` reduced to `waystationRangeHops` | hops |
| `data/tuning/loam-relics-wonders.v{n+1}.json` | `_meta.note` only | — |

## 7. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith.adapters.structures.generate_corpus      # the only writer of gk-data/packs/fusion/data/seed/structures/**
python -m seedsmith.adapters.structures.planner
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q
.\scripts\verify-change.ps1 -Paths <every changed C#/test path> -Session <build-session-id>
.\scripts\test-fast.ps1 -AllDefault       # once, at module close (crosses Core, Data, Server)
python gk-core/scripts/audit-magic-numbers.py --summary
python gk-core/scripts/audit-overflow.py
```

## 8. Acceptance (contract level)

1. **Byte-identical catalog.** The serialization of `StructureCatalog.All` from `band-reader`'s snapshot
   harness is identical before and after. The snapshot is then deleted (it guarded the refactor only).
2. **No number in any seed file.** A walk over every JSON document under `gk-data/packs/fusion/data/seed/structures/`
   (excluding `_plan.json`, which is planner output, and `_registry/`) finds no JSON number anywhere in the
   row, not only in `anchor`. The existing walker
   (`gk-forge/tools/seedsmith/tests/test_structure_corpus.py:218-243`) is widened to the whole row.
3. **Schema audit.** `numeric_audit` over the widened schema reports no defect across all four smuggling
   shapes.
4. **Every loadable row resolves.** For every row with `structureKind != none`, every ordinal is a key
   of its band table (Python), and `StructureCatalog.All` builds without `SeedBandException` (C#).
5. **One writer.** Every `.json` file under `gk-data/packs/fusion/data/seed/structures/` except `_plan.json`, `_registry/**`
   and `_exemplars/**` is a key of `file_tree()`, and the two sets are equal. `write_corpus` into a
   temporary directory followed by a tree hash equals the committed tree's hash.
6. **`LoamPolicy`** exposes no structure cost, yield, capacity or build-turn member. A reflection test
   asserts that the only `Structures`-sourced member is `WaystationRangeHops`.
7. **No `ROLE_TO_STRUCTURE_KIND`.** The symbol is absent (grep test).
8. `python gk-core/scripts/audit-magic-numbers.py` shows no new literal on the balance surface.
9. No test asserts a row count, a generated string, or a per-row number except through a band key.
10. (Round 6 C2) **`none` and `featureUnlock` are exclusive.** No row carries a non-`none` `featureUnlock`
   together with `structureKind: none`; every row that carries one is loadable. The assertion is over the
   two closed vocabularies, not over how many feature rows exist.

## 9. Test plan and verification boundary

| Test | Project | Criterion |
|---|---|---|
| `StructureCatalogSnapshotTests` | Core.Tests | 1 |
| `test_no_seed_file_holds_a_number` (widened walker) | seedsmith pytest | 2 |
| `test_schema_audit_passes_all_four_shapes` | pytest | 3 |
| `test_every_loadable_row_resolves_to_a_band`; `StructureCatalogBandResolutionTests` | pytest; Core.Tests | 4 |
| `test_generator_is_the_only_writer` | pytest | 5 |
| `LoamPolicyShapeTests` | Core.Tests | 6 |
| existing suites that reach `StructureCatalog` | Core, Data, Server tests | regression |

**Verification boundary.**
- C#: `.\scripts\verify-change.ps1 -Paths … -Session …` selects `core-fallback`, `core-tests-fallback`,
  `gk-core/tests/FusionRpg.Data.Tests/**` and `gk-core/src/FusionRpg.Server/**` boundaries
  (`gk-core/scripts/verification-boundaries.v1.json:802-811`, `:850-859`, `:1900-1909`, `:3270-3281`).
- This module crosses Core, Data and Server, which is point 2 of AGENTS.md "Verification boundary", so
  the full suite runs once at close.
- **Gap:** `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**`, `data/tuning/structure-seed.*` and
  `data/tuning/loam.*` are unmapped, and `gk-core/scripts/verify-change.py:771` throws. The owner of the fix is
  `test-verification-boundary` `python-test-lane`. The pytest command in §7 is the boundary for the
  Python side until it lands.

## 10. Hard edges

- **Order inside the module:**
  1. `band-reader`'s snapshot is captured first.
  2. Tuning bands are published.
  3. Generator, schema and C# reader change in one commit with the regenerated tree.
  4. The `LoamPolicy` deletion and the `loam.v{n+1}` publish land with their readers switched in the same
     commit.
  5. The snapshot is deleted last.
- **Goldens.** A world golden that hashes structure definitions would move only if a resolved number
  moved. Criterion 1 is the proof that none did. If a golden moves anyway, the refactor is wrong. Do not
  re-bless it.
- **Keepverse split.** `gk-data/packs/fusion/data/seed/**` moves to `gk-data` and the Core and tuning to `gk-core` (map §9
  item 4). If this lands after the split, the one commit becomes one commit per repository, in the order
  above.

## 11. Dependencies

- Upstream: `band-reader` (reader, resolver, snapshot harness), `structures-adapter` (disk-read
  planner).
- Downstream: `exchange-role` (needs `ROLE_TO_STRUCTURE_KIND` gone and the C# registry),
  `corpus-metrics` (band-resolves metric), `trade-structure-rows` (new rows get bands, not numbers).
- Cross-map: `trade-network` `sector-yield` adds any capacity field a new band would feed. This module
  adds none.

## 12. Open questions

None. The rung vocabularies are decided in §5.2 by the principle "exactly wide enough to reproduce the
shipped values". Where `WaystationRangeHops` lives is decided in §5.6 (it stays in loam).

## 13. DESIGN-GATE §5 checklist

```
[x] Subsystems: structure seed schema and generator, structure catalog, loam tuning and LoamPolicy, tests
    across Core/Data/Server.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session records src/, tests/,
    data/, gk-forge/tools/seedsmith/ paths.
[x] Read this session: DESIGN-GATE rows (tunables, numeric magnitudes, seedsmith, validation);
    tunables-ssot §2-§3; item/seed-contract §1-§3; structure-seed-ideal (all); PRINCIPLES §5-§7.
[x] decisions.md: rows for structure-corpus ownership and the exchange role present (working tree,
    2026-09-19; the exchange row states wonder/ is a folder, not a role).
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: every playable row's magnitudes read by script; LoamPolicy callers by grep;
    loam v4/v5 structures blocks compared (equal).
[x] Read the surrounding sections of seed-contract §3 and T7.
[~] Tested: the value inventory and the costProfile collision were computed. The byte-identical proof is
    the module's own first task.
[x] No §2 invariant contradicted. Closes invariant 12 for structures.
[x] Corrections propagated: the stale notes (§5.7), the stale tests (§5.5), and the wonder/ folder (§5.1).
[x] No population pin. The widened vocabularies are closed and pinned by their schema tuples, with the reason.
[x] No event-refreshed cache.
[x] No ordering assumption beyond band-reader's order-independence.
[x] No actor magnitude.
[x] SOLID: one source per number; the LoamPolicy duplicate and the ROLE_TO_STRUCTURE_KIND contradiction deleted.
[ ] New rule registry row: none beyond band-reader's.
```

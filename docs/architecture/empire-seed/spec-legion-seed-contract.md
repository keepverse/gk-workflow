# Spec: `legion-seed-contract`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `legion-seed-contract` · **Map row:** 13 ·
**Wave:** 4
**Depends on:** `band-reader`, `world-exemplars` (the tone registry and renderer) · **Cross-map (hard):**
the vocabularies approved in `legion-build`'s specs for `legion-equipment`, `legion-traditions`,
`legion-standards` and `legion-doctrine` · **Model calls:** none
**Status:** spec phase, 2026-09-19; reconciled 2026-09-19 with the round-4 owner decisions
([decisions-round-4.md](../trade-network/decisions-round-4.md) Q12: *"one shared legion vocabulary registry
both read"*; §B: the Workshop chain is the one legion-equipment building). **This contract lands only
after `legion-build` approves the vocabularies the registry holds** (§3). No build authorized until then and
until this spec is approved.

---

## 1. Objective

A `legion` adapter with four seed kinds: `legion-standard`, `legion-tradition`, `legion-doctrine` and
`legion-equipment`. Every field carries an ownership level and a description with a negative clause, no
field holds a number, and every kind has hand-authored exemplars that validate against it. These
exemplars are what `legion-build`'s modules test against until `legion-seed-rows` generates real seeds
(`docs/architecture/legion-build-map.md`, Assumption 4).

**Done means:**
- `resolve_adapter("legion")` works.
- The schema audit passes all four smuggling shapes for every kind.
- Every VALIDATED field joins to one registry that Python and C# both read.
- The equipment kind structurally cannot carry a set, socket, affix pool, roll or rarity count.
- Each kind has at least one exemplar passing `ExemplarConformance`.

## 2. Scope and non-goals

**In scope.**
- The adapter.
- The four schemas.
- The shared legion vocabulary registry file.
- The exemplars.
- The C# parse of the four kinds through `band-reader` (identity and VALIDATED fields only).

**Not in scope.**
- Numbers (`legion-bands`).
- Generation (`legion-seed-rows`).
- Every legion mechanic: layer 5c, `OwnerKind.Legion`, stack `Count`, the stack-scoped equipment
  layer, forging, fitting and traditions' counters. All of it is `legion-build`'s (map §8).
- **Inventing any vocabulary `legion-build` owns**: the legion slot list, the tradition trigger facts,
  the carrier roles, and the doctrine trade-off kinds.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The atom-family namespace validator | `gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py:585` (`validate_atom_family_namespace`, over the authored affix families) |
| Built | The v1 goods vocabulary: the closed material list | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs:68` |
| Built | The element vocabulary | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:46` |
| Built | The structure role registry, which after `band-reader` is one file read by both languages | `spec-band-reader.md` §5.3 |
| Built | The numeric audit pattern: four shapes, a deny list and a `*Milli` suffix | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py:18-25`, `:40-70` |
| Real gap | Every legion kind; no `data/seed/legion/` tree | — |
| Owned elsewhere, not yet approved | The legion slot list (`legion-equipment`), trigger facts (`legion-traditions`), carrier roles (`legion-standards`), `worldTradeoffKind` (`legion-doctrine`, *"a closed four-member vocabulary with a membership test"*) | `docs/architecture/legion-build-map.md` §5.11-§5.14 |

**Two findings that shape the schema.**
1. **`tier` is an audit deny name.** The numeric audit rejects a field named `tier` or `materialtier`
   regardless of type (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py:18-21`). The
   equipment ordinal is therefore named **`tierBand`**. The map's table says `tier`. This is the
   correction.
2. **"Standard" is taken.** `ItemRole.Standard` is the commander's item slot
   (`gk-core/src/FusionRpg.Core/Items/ItemRole.cs:29-31`). The kind is `legion-standard`, and no legion
   vocabulary contains the bare word `standard` (map §11 item 7; `docs/architecture/legion-build-map.md`
   X8).

## 4. The generation rules, as they bind this module

- **The model writes identity; deterministic code writes magnitude.** No field is numeric. The four
  smuggling shapes are tested per kind.
- **Four ownership levels.** A field with no level is a contract defect, and a test asserts every field
  has one.
- **`none` is a value; a missing key is a defect.** `additionalProperties: false`, and every field is
  required. Where `none` is illegal, the description says why.
- **Every description has a negative clause.** This is a mechanical test, as for structures
  (`gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py:59`).
- **The planner fixes every enum; the model names.** The schemas mark AUTHORED text fields
  (`name`, `flavor`, `rankNames`) as the only model-written fields. `legion-seed-rows` hands the rest to
  the planner. No vote set is needed. The permutation and voting rules apply only if a later spec gives a
  model an enum to choose.
- **Fixed, not rolled** (owner amendment 2026-09-19; `legion-build-ideal.md` §6.7). Legion equipment has
  no set, socket, affix pool, roll or rarity-count field, and the unique-item generator never touches this
  family. Standards and traditions carry no inheritance field (ruling L2: both reset on disband or rout).

## 5. Design

### 5.1 The four kinds

| Kind | Field | Level | Vocabulary / rule | `none`? |
|---|---|---|---|---|
| **`legion-standard`** | `name`, `flavor` | AUTHORED | text, no digit | — |
| | `elementAffinity` | VALIDATED | the six elements | legal (an unattuned standard) |
| | `atomFamilies[]` | VALIDATED | the atom-family namespace (§5.3), min 1, unique | illegal: a standard with no effect is not a standard |
| | `carrierRequirement` | VALIDATED | `legion-build` carrier roles; the map proposes `any · fighter · commander` | `any` is the absence value, so no separate `none` |
| | `forgeGoods[]` | VALIDATED | goods registry = `MaterialCatalog.All`; *which* goods, never how many | illegal (min 1): forging must create trade demand (`legion-build-map.md` §5.11) |
| **`legion-tradition`** | `name`, `flavor` | AUTHORED | text | — |
| | `triggerKind` | VALIDATED | `legion-build` trigger facts | illegal: a tradition with no trigger can never be earned |
| | `atomFamily` | VALIDATED | the atom-family namespace | illegal |
| | `rankNames[]` | AUTHORED | text, **one or more** names (min 1). Rank *r* displays name `min(r, len) − 1` with the rank number; ranks past the list reuse its last name — presentation, never a rank cap (the curve has no top rank, `legion-build/spec-legion-traditions.md` §4). **Corrected by the 2026-09-20 audit:** the first draft required the length to equal the number of authored points in `legion.v1.json` `traditions.rankThresholds`, which made a generated seed invalid the moment a tuning publish added a threshold — a balance change forcing a content regeneration, the coupling tunables-ssot T7 exists to prevent. The list length is now independent of tuning | illegal: a tradition needs at least one rank name |
| **`legion-doctrine`** | `name`, `flavor` | AUTHORED | text | — |
| | `combatFamilies[]` | VALIDATED | the atom-family namespace, min 1 | illegal |
| | `worldTradeoffKind` | VALIDATED | `march · burn · sight · cargo` (`legion-build-map.md` §5.13) | illegal: every doctrine pays a world-side cost (`legion-build-ideal.md` §6.1) |
| **`legion-equipment`** | `name`, `flavor` | AUTHORED | text | — |
| | `pieceId` | DERIVED (audit 2026-09-20) | kebab id minted **once** per `planKey` by the legion writer (hand-authored for exemplars) and frozen: saved worlds persist it (a fitted stack's `Gear`, `legion-build` `legion-equipment` §3), so a regeneration never changes it — the `world-namer` §5.4 id rule | illegal |
| | `slot` | VALIDATED | the `legion-build` legion-slot list, disjoint from `ItemRole` | illegal: a piece fits a slot |
| | `tierBand` | VALIDATED ordinal | the tier ladder `legion-bands` publishes | illegal |
| | `atomFamilies[]` | VALIDATED | the atom-family namespace, min 1 | illegal |
| | `recipeGoods[]` | VALIDATED | goods registry; which inputs, never how many | illegal |
| | ~~`producedBy`~~ | — | **Removed (round 4 §B).** Every piece is produced by the one legion-equipment building, the Workshop chain (`featureUnlock: legion-equipment`, `spec-trade-structure-rows.md` §5.1); the `tierBand` alone decides the minimum Workshop tier (`spec-legion-bands.md` §3 item 3). A field with one legal value is noise, and a per-piece producer would be a second place the rule lives | — |
| | `elementAffinity` | VALIDATED | six elements | legal: element is a second axis only where a piece is attuned |

Every row also carries `id` (the kind's id field: `pieceId` for equipment, a kebab `id` for the others)
and `_provenance`.

### 5.2 One vocabulary registry, read by both languages

`data/seed/legion/_registry/vocab.v1.json` is hand-authored and holds:
- `legionSlots`
- `triggerKinds`
- `carrierRequirements`
- `worldTradeoffKinds`

**This file is the one shared legion vocabulary registry the owner decided on (Q12, 2026-09-19).** It is the
single source: Python schemas build their enums from it, and `legion-build`'s C# reads the same file through
`band-reader` (the host injects it; Core never opens a file). Where `legion-build` code needs a C# enum to
branch on (for example `worldTradeoffKind` choosing a pricer), the enum is **validated against the registry
at load** — a member missing from either side is a load rejection naming it — so there is one list and one
check, never two lists and a sync test. The file lives in the seed tree because it is seed vocabulary; its
members are `legion-build`'s decisions, changed only by a reviewed `legion-build` widening in the same commit
as the code that reads the new member. The former `producedByRoles` list is gone with `producedBy`.

### 5.3 The atom-family namespace

`atomFamilies`, `atomFamily` and `combatFamilies` are VALIDATED against the same namespace the actions
adapter validates against, through `validate_atom_family_namespace`
(`gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py:585`), imported and not
copied. If `legion-build`'s layer-5c binder accepts only a subset, that subset is a list in
`vocab.v1.json` (`legionAtomFamilies`), and the validator checks membership in both.

### 5.4 The equipment kind's negative space

On `legion-equipment` the schema has `additionalProperties: false`, and a dedicated test asserts that
none of these appear as a property at any depth:

```
set, setId, sets, socket, sockets, socketMax, affix, affixes, affixPool,
roll, rolls, rollSeed, rarity, rarityBand, prefixRolls, suffixRolls
```

The list is the unique-item vocabulary this scope must never inherit (`legion-build-ideal.md` §6.7
table).

### 5.5 The adapter

`tools/seedsmith/seedsmith/adapters/legion/`:
- four `KindSpec`s with `reference_fields` empty (legion seeds reference registries, not other kinds)
- `dimensions()`: `elementAffinity`, `worldTradeoffKind`, `slot`, `tierBand`
- `legal_combinations()`: `slot × tierBand` legal as published by `legion-bands`, else `True`, with a
  real `False` once the ladder exists
- `registries()` from `vocab.v1.json`
- `channels()` empty, with the same stated reason as structures
- `corpus_root = "data/seed/legion"`, so `world-name-index` picks it up

### 5.6 Exemplars

`data/seed/legion/_exemplars/<kind>.exemplar.json`, at least one per kind and hand-authored. The tone is
the shared `data/seed/_registry/world-tone.v1.json` (generic strategy-genre vocabulary, no named
characters, no IP words). Names must not collide with any corpus name (`world-name-index`) or a normalised
almanac type name. `legion-build`'s tests read these exemplars, so a change to an exemplar is reviewed as
a test-fixture change for that program.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest tools/seedsmith/tests/test_legion_contract.py tools/seedsmith/tests/test_legion_adapter.py -q
python -m seedsmith check data/seed/legion --adapter legion
.\scripts\verify-change.ps1 -Paths <C# parse + tests> -Session <build-session-id>
```

## 7. Acceptance (contract level)

1. `numeric_audit` reports nothing for each of the four schemas, and a fixture schema with each of the
   four smuggling shapes is rejected.
2. Every field of every kind has exactly one ownership level and a description with a negative clause.
3. Every closed enum either admits `none` or its description states why not (§5.1). A missing key fails
   validation.
4. Every VALIDATED value in every exemplar joins its registry: elements, the atom namespace,
   `MaterialCatalog.All` and `vocab.v1.json`. No `legion-equipment` exemplar carries `producedBy`.
5. No property in §5.4's list exists on `legion-equipment` at any depth, and no inheritance-shaped field
   (`inherit*`, `legacy*`, `carryOver*`) exists on `legion-standard` or `legion-tradition`.
6. `vocab.v1.json` is the only list: every `legion-build` C# enum that names one of its vocabularies is
   checked against it at load, and a membership test pins each list as a **closed vocabulary**, naming the
   `legion-build` spec that decided it.
7. The adapter passes the protocol cases (`isinstance`, a real `False` legality case once `tierBand`
   exists, `channels()` empty) and `ExemplarConformance` for every exemplar.
8. The C# parse of each kind rejects an unknown VALIDATED value, naming the field (`band-reader`'s
   `RequireMember`).
9. No test counts legion seeds or asserts exemplar text.

## 8. Test plan and verification boundary

`test_legion_contract.py` covers criteria 1-6 and 9. `test_legion_adapter.py` covers 7. Core.Tests
`LegionSeedParseTests` covers 8. All offline.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `data/seed/legion/**` are unmapped
(`scripts/verify-change.ps1:118`). The owner of the fix is `test-verification-boundary` `python-test-lane`.
The pytest command is the boundary. The C# tests go through `verify-change.ps1`.

## 9. Hard edges

- **Cross-program order** (map §4): `legion-build` approves its vocabularies at spec time → this module
  lands schemas, registry and exemplars → `legion-build` builds on the exemplars → `legion-seed-rows`
  generates. The edge into this module is an approved spec, never built code.
- **A new seed tree** (`data/seed/legion/`). The Keepverse split maps it with `gk-data/packs/fusion/data/seed/**`.

## 10. Dependencies

- Upstream: `band-reader` (C# parse, registry injection), `world-exemplars` (tone registry and renderer),
  `world-name-index` (exemplar dedup; soft).
- Cross-map (hard): `legion-build` specs for `legion-standards`, `legion-traditions`, `legion-doctrine`
  and `legion-equipment` (vocabularies). The tradition rank count is from `legion-build`'s tuning.
- Downstream: `legion-bands`, `legion-seed-rows`, and `legion-build`'s four modules (exemplars as test
  input).

## 11. Open questions

None. The mirror's shape was decided by the owner on 2026-09-19 (Q12: one shared registry both programs
read, §5.2).

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: a new seedsmith adapter, a new seed tree and registry, C# parse via band-reader.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: legion-build-ideal §6.1, §6.7, §7-§9; legion-build-map §5.11-§5.14 and §6;
    item/seed-contract §1-§3; ai-native README; the structure audit's deny list.
[x] decisions.md: rows "Actor layer 5c — legion" and "Legion equipment scope" (working tree, 2026-09-19)
    are legion-build's. This contract respects both (no sets, stack scope is theirs).
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: the audit deny list (tier), ItemRole.Standard, MaterialCatalog.All, the namespace validator.
[x] Read surrounding sections of L2/L5 and §6.7.
[x] Tested: none claimed.
[x] No §2 invariant contradicted.
[x] Correction propagated: tier → tierBand, recorded in the map and in spec-legion-bands.
[x] Pins only for closed vocabularies mirrored from approved specs, with the reason.
[x] No cache, no ordering.
[x] Actor magnitude: none produced here; every legion number reaches ActorHub through legion-build's
    layer-5c reader or the stack-scoped equipment layer (GG-49 SourceIds are theirs). No private fold.
[x] SOLID: one registry per vocabulary, one namespace validator, one reader.
[ ] New rule registry row: none.
```

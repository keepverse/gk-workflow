# Spec: `world-exemplars`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `world-exemplars` · **Map row:** 7 ·
**Wave:** 2 · **Ideal id:** I4
**Depends on:** `exchange-role` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

Give the naming model a small, hand-authored distribution to extend, and give every family's naming prompt
one shared tone brief. Invention fails by mode collapse and generic flavour (`structure-seed-ideal.md` §3,
where nine variations of "Sturdy Wall" is the named failure). A vote does not catch that. What
counters it is a real distribution written first by a person, plus a tone rule every call carries.

**Done means:**
- Every structure role, `Exchange` included, has at least one exemplar that validates as real content of
  its kind.
- The tone brief exists as authored data.
- A generic renderer puts the tone brief and the IP avoid-list into every naming prompt.
- The planner never counts an exemplar, and the C# catalog never loads one.

## 2. Scope and non-goals

**In scope.**
- Structure exemplars.
- The `flavor` field on the structure anchor, which exemplars need to be real content (§5.1).
- The shared tone brief.
- The feature-agnostic brief helper that renders it.
- Consuming `ip-censor`'s avoid-list when it exists.

**Not in scope.**
- Legion exemplars. They belong to `legion-seed-contract`, because an exemplar must validate against a
  schema that does not exist yet (map §4 "Why these boundaries").
- Any model call.
- Filling `flavor` for the 28 existing rows. That is hand-authored generator source, and it is reported
  as open work (§5.1).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | Item exemplars, flat `<kind>.exemplar.json` files | `gk-data/packs/fusion/data/seed/items/_exemplars/` |
| Built | `Corpus.load` marks `_exemplars/` entries as exemplars | `gk-forge/tools/seedsmith/seedsmith/corpus/model.py:188` |
| Built | `ExemplarConformance`, a closed-loop metric: every exemplar validates as real content of its kind | `gk-forge/tools/seedsmith/seedsmith/metrics/exemplar.py:20-23` |
| Built | The decision-43 guard: no corpus id equals a real PvZ almanac type name, normalised | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:249-281` |
| Built | `briefkit` inlines every vocabulary and refuses citation-shaped text | `gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-13`; `gk-forge/tools/seedsmith/seedsmith/briefkit/render.py:72` |
| Wiring gap | The C# reader walks `_exemplars/` (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:93`). `band-reader` closes it by skipping that segment | `spec-band-reader.md` §5.1 |
| Real gap | Structure exemplars, the anchor `flavor` field, the tone brief | — |
| Cross-map, not built | `ip-censor` `avoid-list`: `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py` (new) renders the registry into briefs as advisory text. Ruling IC-3: advisory in briefs, the release scan is the gate | `docs/architecture/ip-censor/spec-avoid-list.md:27`, `:58`; `docs/architecture/ip-censor-ideal.md:440` |

**Correction to the map (§5.11).** The map put the `flavor` schema widening in `world-namer`. It moves
here, because an exemplar must validate against its kind's schema: that is `ExemplarConformance`'s
contract, and the same reason the map gives for placing legion exemplars in `legion-seed-contract`.

## 4. Principles as they bind this module

- **Exemplars are hand-authored** (`PRINCIPLES.md` §6: hand-author only `**/_registry/**`,
  `**/_exemplars/**` and hand-authored kinds).
- **A tone rule is data, a renderer is code** (P5). The brief text lives in a registry file, and the
  helper that inlines it is feature-agnostic.
- **No IP words, no named characters** (owner, round 3; the legion-build vocabulary rule). The block list
  is **not** a private word list. It is `ip-censor`'s shared helper.
- **A closed contract is described, not frozen** (ai-native README §3). Every new field carries a
  description with a negative clause.
- **No model.** Zero calls.

## 5. Design

### 5.1 `flavor` on the structure anchor

| Field | Level | Contract |
|---|---|---|
| `flavor` | AUTHORED, keyed text (`item/seed-contract.md` §2.1 lists `flavor` as AUTHORED) | A string of one or two sentences, with no digit, no brace and no markup. Description: *"What a player feels standing next to this structure — its look and use in the world. NOT its numbers, NOT its role name restated, NOT a character's name, NOT another game's term."* `""` is legal and means *not yet written* |

The generator writes `flavor: ""` for the 28 existing rows, which regenerates the tree through the one
writer. A closed-loop completeness finding lists every row with empty flavour. It is a **work queue**,
not a gate (§5.4). Filling those 28 is a hand edit to generator source, reviewed like any content.

### 5.2 Exemplar files

`data/seed/structures/_exemplars/<role-lowercase>.exemplar.json`, one file per role, eleven in total:
the ten roles plus `Exchange`. Each file is the shipped shape
(`{"kind": "structure-anchor", "_meta": {...}, "entries": [row]}`) with a complete anchor, a real
`name`, a written `flavor` and a `reason`. `_meta` carries `exemplarVersion` and a `maintenanceNote`,
following the item exemplars' own shape (`gk-data/packs/fusion/data/seed/items/_exemplars/unique.exemplar.json`).

- **Ids and names** must not equal any corpus id or name, any real PvZ almanac type name (normalised as
  the decision-43 guard does), or any avoid-list term. An exemplar is an example of a new row, not a copy
  of an existing one.
- **`structureKind: none`** is the value, so no reader ever mistakes an exemplar for loadable content.
  The skip rule in both loaders is the primary guard. This is a second one.
- An exemplar row's ordinals are legal members, and they need not have band rows.

### 5.3 The tone brief

`data/seed/_registry/world-tone.v1.json`, authored. It is shared by every world family, structures and
legion alike, so it lives in a family-neutral place:

```jsonc
{ "schemaVersion": 1, "registryVersion": 1,
  "voice": "Generic strategy-genre register: buildings, depots, warehouses, standards, doctrines, legions, rival empires.",
  "rules": [
    "Name what the thing is and does in this world; never a person's name, never a title held by a character.",
    "No term from another game, film or franchise; no real brand.",
    "No number, no unit, no quantity in any name or flavour.",
    "A stronger version is not a different thing: never name a row 'Greater X' or 'X II'.",
    "A building never takes a slot's display name: slots name ground ('Market Square', 'Vault Site'), buildings name what stands on it."
  ],
  "avoid": ["<rendered from ip-censor avoid-list; empty until that registry exists>"] }
```

The last rule is **round 5 C4** (owner, 2026-09-20: *"rename the slots' display names; building names
stay; ids unchanged"*): the slot words are `trade-surface` `trade-lexicon` §4a's, and its vocabulary guard
enforces the rule over the shipped catalogs; the brief only keeps a model from re-creating the collision.

The rules are text a model reads. None of them is enforced by a model: enforcement is `world-namer`'s
validators (digits, dedup) and `ip-censor`'s release scan.

### 5.4 The renderer

`tools/seedsmith/seedsmith/briefkit/tone.py`, `render_tone_section(family) -> str`. It inlines the tone
registry and appends `avoid_list.load_avoid_terms()` when that module exists. If the module is absent, it
appends nothing and emits one `Finding` (`AvoidListUnavailable`, severity info). The section passes
`briefkit`'s citation check, so it is text, never a filename.

### 5.5 Metrics this module registers

| Metric | Loop | Target |
|---|---|---|
| `ExemplarConformance` over the structures adapter | closed (existing) | every exemplar valid |
| `exemplar_role_coverage` | closed | every member of the role registry has at least one exemplar |
| `flavor_missing` | **open** (review queue) | none; it lists rows with `""` |

`flavor_missing` is open-loop on purpose. Whether a row *deserves* hand-written flavour now is a
judgement, and an empty field on an AUTHORED row is not a defect of the contract.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith.adapters.structures.generate_corpus
python -m pytest tools/seedsmith/tests/test_structure_exemplars.py tools/seedsmith/tests/test_briefkit_tone.py gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q
python -m seedsmith check gk-data/packs/fusion/data/seed/structures --adapter structures --metric ExemplarConformance/InvalidShape
```

## 7. Acceptance (contract level)

1. Every role in the registry has at least one exemplar, and every exemplar passes `ExemplarConformance`.
2. No exemplar id or name equals a corpus id or name, a normalised almanac type name, or an avoid-list
   term.
3. `load_rows` (the planner's input) contains no exemplar, and the C# `StructureCorpus` contains no
   exemplar (the `band-reader` skip test, extended to a real exemplar file).
4. The tone section renders into a brief, passes the citation check, and is byte-identical across two
   renders (content-addressed).
5. The tone registry contains no digit, and its avoid list is either empty or equal to `ip-censor`'s
   rendered terms. It is never a hand-typed list.
6. `flavor` exists on the schema with a negative clause, and `numeric_audit` still reports nothing.
7. No test asserts exemplar text. Tests assert membership, uniqueness, non-emptiness and length bounds.

## 8. Test plan and verification boundary

`test_structure_exemplars.py` (criteria 1-3, 6-7), `test_briefkit_tone.py` (4-5), and `band-reader`'s
`SeedFileReaderTests.Exemplars_are_skipped` fed a real exemplar file (3, C#). All offline.

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/**` are unmapped
(`gk-core/scripts/verify-change.py:771`). The owner of the fix is `test-verification-boundary` `python-test-lane`.
The pytest command in §6 is the boundary. The C# test runs through `verify-change.py`
(`core-tests-fallback`).

## 9. Hard edges

- **The `flavor` widening regenerates all 28 rows** (one field added). It lands in one commit with the
  generator change.
- **`data/seed/_registry/`** is a new top-level registry location. The Keepverse split tool must map it
  with the rest of `gk-data/packs/fusion/data/seed/**` to `gk-data` (map §9 item 4). No special rule is expected.

## 10. Dependencies

- Upstream: `exchange-role` (the eleventh exemplar), `band-reader` (the C# skip), `structures-adapter`
  (`load_rows`).
- Downstream: `call-budget-dry-run` (renders the tone section), `world-namer` (uses exemplars as
  few-shot input and the tone section), `legion-seed-contract` (reuses the tone registry and renderer).
- Cross-map (soft): `ip-censor` `avoid-list`. Its absence never blocks this module.

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: structure anchor schema, seedsmith briefkit, exemplar metric, seed registries.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: ai-native README (all), seed-contract §2 (flavor AUTHORED), structure-seed-ideal §3/§6,
    ip-censor spec-avoid-list (header and design), exemplar metric code.
[x] decisions.md: no lock on exemplars or tone.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: Corpus.load exemplar marking, C# recursion, ExemplarConformance.
[x] Read IC-3 in its section before relying on it.
[x] Tested: none claimed.
[x] No §2 invariant contradicted.
[x] Correction propagated: flavor widening moved from world-namer (recorded in the map and in spec-world-namer).
[x] No population pin; exemplar count is "at least one per role", a coverage contract.
[x] No cache, no ordering, no actor magnitude.
[x] SOLID: one tone registry and one renderer for every family; no private block list.
[ ] New rule registry row: none.
[x] Round 5 (2026-09-20): C4 — tone brief rule "a building never takes a slot's display name";
    enforcement is trade-lexicon's guard, not the model.
```

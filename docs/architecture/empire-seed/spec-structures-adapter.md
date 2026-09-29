# Spec: `structures-adapter`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `structures-adapter` · **Map row:** 1 ·
**Wave:** 0 · **Ideal id:** I1
**Depends on:** — · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

Make the committed structure corpus visible to seedsmith's generic machinery. Today it is visible only to
its own hand-wired `structures contract` subcommand. After this module, `resolve_adapter("structures")`
returns a real `SeedAdapter`, the generic `check` and `metrics` commands run on `gk-data/packs/fusion/data/seed/structures`,
and the structure planner and metrics count **the rows on disk**, meaning every row the game loads.

**Done means:** every row the C# reader loads is a row the planner counts. The committed `_plan.json` is
regenerated from the corpus on disk, not from the generator's in-memory tuple. The adapter passes the
protocol tests the `_stub` fixture passes. Nothing structure-shaped enters the seedsmith core.

## 2. Scope and non-goals

**In scope.** The `StructuresAdapter` class and its registration. A committed-corpus loader that reads
the nested `anchor` object. The planner and metrics entry points switch to that loader. The regenerated
`_plan.json`. A one-hook generalisation of the CLI's per-adapter loader branch (§5.4).

**Not in scope.**
- Numbers. The `magnitudes` block and the band tables belong to `structure-bands`.
- The literal-to-tuning moves and population pins. Those belong to `world-budgets`.
- New metrics. Those belong to `corpus-metrics`.
- Folding the three hand-authored rows into `generate_corpus.py`. That is `structure-bands` obligation 1
  (owner decision, 2026-09-19). This module only makes them *counted*.

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The protocol: `kinds`, `dimensions`, `legal_combinations`, `registries`, `channels` | `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:94-100` |
| Built | `KindSpec`, `Dimension`, `RegistrySet` | `gk-forge/tools/seedsmith/seedsmith/adapters/base.py:23-91` |
| Built | The closed vocabularies | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41-55` |
| Built | `build_plan(rows, tuning, seed)` and `run_all(rows, tuning)` already take `rows` as a parameter | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:78`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:254` |
| Wiring gap | `structures/__init__.py` is empty (0 bytes), and `ADAPTERS` has no `structures` key | `gk-forge/tools/seedsmith/seedsmith/adapters/registry.py:12-18` |
| Wiring gap | Both `__main__` blocks import the generator's `ALL_ROWS` instead of reading disk | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:174-181`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:259-266` |
| Wiring gap | `ALL_ROWS` has 25 rows. Disk has 28 entries: `relic-vault`, `standing-stones` and `sunspire-throne` are outside the generator (counted this session; the counts are readings) | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py:468`; `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json`; `gk-data/packs/fusion/data/seed/structures/wonder/` |
| Wiring gap | `Entry.get` reads **top-level** keys only. A structure row nests `role`, `requiredSlotKind` and the other fields inside `anchor`, so a `Dimension(field="role")` over raw `Corpus.load` output reads `None` for every row | `gk-forge/tools/seedsmith/seedsmith/corpus/model.py:48-49`; the pairwise reader at `gk-forge/tools/seedsmith/seedsmith/metrics/pairwise.py:46` |
| Wiring gap | The generic `check` special-cases adapters with `if args.adapter == "actions"` / `elif args.adapter == "dungeon"` loader branches | `gk-forge/tools/seedsmith/seedsmith/report/cli.py:380-400` |
| Real gap | None | — |

**Two corrections to the map (§5.1).**
- The map mentions *"the adapter conformance suite the `_stub` adapter already runs."* No such suite
  exists. `gk-forge/tools/seedsmith/tests/test_stub_adapter.py` is a per-adapter test file with its own cases
  (`:22-56`), and each real adapter writes its own copy (`tests/test_adapter_creatures.py`). This module
  writes the equivalent cases for structures (§8).
- The map says the budget is checked *"through the adapter's distribution metric."* The core
  `Distribution/CellDeviation` counts only `kind:` and `role:…:base-type` dimensions. Any other
  dimension raises (`gk-forge/tools/seedsmith/seedsmith/metrics/distribution.py:18-25`). So the per-role budget
  stays checked by the structure metric `per_role_coverage`
  (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:83-93`). Teaching the core budget a third
  dimension shape is seedsmith-core work. It is recorded here and not done here.

## 4. Principles as they bind this module

- **P5: feature knowledge lives in adapters.** Everything structure-shaped is in `adapters/structures/`.
  The one core touch (§5.4) removes adapter names from the core rather than adding one.
- **A guardrail validates the contract** (`validation-ssot.md` §2). Tests assert reconciliation (plan
  rows == entries on disk), membership and determinism, never 25, 28 or any row count.
- **Generated data is never hand-edited.** `_plan.json` is written only by the planner's entry point.
- **No model.** This module makes zero calls. The generation rules (permutation, voting, constrained
  decoding) do not bind it, because nothing here samples.

## 5. Design

### 5.1 The adapter

`gk-forge/tools/seedsmith/seedsmith/adapters/structures/__init__.py` exports `StructuresAdapter`:

| Method | Answer |
|---|---|
| `kinds()` | One `KindSpec`. `kind="structure-anchor"`, `directory="."`, `namespace="structure"`. `required` = the anchor schema's `required` set plus `id` and `name`. `id_pattern` = the kebab pattern `WorldIds.RequireKebab` enforces. No `reference_fields` (a structure references no other kind) |
| `dimensions()` | `role` (field `role`) and `requiredSlotKind` (field `requiredSlotKind`), both `applies_to={"structure-anchor"}`. Values come from `ROLE` and `REQUIRED_SLOT_KIND` |
| `legal_combinations()` | `True` for `(role, r, requiredSlotKind, s)` only when `[r, s]` is in the committed plan's `legalRoleSlotPairs` (round 5 B1: a row with `requiredSlotKinds` is legal only when **every** entry pairs legally with its role). Any other dimension pair → `True`. A real `False` exists today: for example `("Deny", "Rootbed")` is not a committed pair |
| `registries()` | `RegistrySet(vocabularies={role, requiredSlotKind, element, tempo, reach, strengthBand, rarity, costProfile, targetPreference, acquisitionPath, footprint, coverTier})`, each built from the schema tuples, never re-typed |
| `channels()` | `[]`, with a comment: *structures own no stat channel, so `numerics` has nothing to resolve here. Structure numbers resolve in C# through `band-reader`, not in seedsmith.* The same deliberate emptiness as `spec-adapter-creatures.md` §2.6 |

The legality function reads `_plan.json`. It never re-derives legality from the rows, because a pair the
plan declares ahead of content has to be legal before a row exists. `exchange-role` depends on that
(§10).

### 5.2 The committed-corpus loader

`load_structure_corpus(root) -> LoadResult` in the same package:

1. Call `Corpus.load(root)`. `_plan.json` carries no `kind`, so it is already skipped
   (`gk-forge/tools/seedsmith/seedsmith/corpus/model.py:183-186`), and `_exemplars/` entries are already marked
   `is_exemplar` (`:188`).
2. For each entry, build a **read-only projection**: the entry's `anchor` fields lifted to top level,
   plus `id` and `name`. The on-disk shape stays untouched, and the C# reader still reads nested
   `anchor` (`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:115-124`).
3. Return the projected `Corpus` and a `Finding` for any entry without an `anchor` object.

The planner and metrics functions receive the same rows `ALL_ROWS` gives them today, which is the list of
row dicts with a nested `anchor`. They read it from disk through `load_rows(root) -> list[dict]`: every
non-exemplar entry, in `(path, id)` order. Their signatures do not change.

### 5.3 Entry points

`planner.py` and `metrics.py` `__main__` blocks call `load_rows(repo_root / "gk-data/packs/fusion/data/seed/structures")` in
place of `ALL_ROWS`. `generate_corpus.py` keeps `ALL_ROWS` as the generator's own source. It stops being
the planner's source.

### 5.4 The CLI hook — one additive core change, stated as the finding

`cmd_check` chooses a loader by adapter name (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:380-400`). A third
`elif` would extend an open/closed defect along its own seam. The fix is one duck-typed hook:

```python
load = getattr(adapter, "load_corpus", None)
if load is not None:
    result = load(Path(args.corpus_root))     # -> LoadResult(corpus, findings)
else:
    corpus = Corpus.load(Path(args.corpus_root))
```

`ActionsAdapter.load_corpus` delegates to its existing `load_committed`, and `DungeonAdapter.load_corpus`
to its existing `load_dungeon_corpus`, so both branches collapse into the hook in the same change.
`StructuresAdapter.load_corpus` is §5.2. This mirrors the recorded precedent of an additive core change
with a default (`gk-forge/tools/seedsmith/seedsmith/adapters/base.py:39-61`, `KindSpec.motif_expression`). The
`_stub`, `items` and `creatures` adapters are untouched.

### 5.5 The regenerated plan

Running `python -m seedsmith.adapters.structures.planner` rewrites `gk-data/packs/fusion/data/seed/structures/_plan.json`
from disk. Expected diff, computed against the committed plan this session: `actualCounts` gains the three rows
(`Store`, `Extract`, `Bank` each +1), `legalRoleSlotPairs` gains `["Store", "Vault"]` (absent today),
and `gridDensityMilli` moves from 2500 to 2800. Those are readings. That value stays inside the band at
`gk-core/data/tuning/structure-seed.v1.json:23`, and every per-role count only rises, so `check_plan` passes.
That was run this session over the 28 disk rows: `check_plan` raised nothing, and the density read 2800.
It is re-run at build time anyway, and the plan is committed only after it passes. If it ever fails,
that is the planner reporting the truth, and the fix is a published tuning value (`world-budgets`),
never a literal here.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest tools/seedsmith/tests/test_structures_adapter.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py gk-forge/tools/seedsmith/tests/test_actions_adapter.py gk-forge/tools/seedsmith/tests/test_stub_adapter.py -q
python -m seedsmith check gk-data/packs/fusion/data/seed/structures --adapter structures
python -m seedsmith.adapters.structures.planner      # rewrites _plan.json from disk
```

## 7. Structure

```
gk-forge/tools/seedsmith/seedsmith/adapters/structures/__init__.py   StructuresAdapter, load_structure_corpus, load_rows
gk-forge/tools/seedsmith/seedsmith/adapters/registry.py              + "structures"
gk-forge/tools/seedsmith/seedsmith/adapters/actions/__init__.py      + load_corpus (delegates to load_committed)
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/__init__.py      + load_corpus (delegates to load_dungeon_corpus)
gk-forge/tools/seedsmith/seedsmith/report/cli.py                     the hook (§5.4); two elif branches removed
gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py    __main__ reads disk
gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py    __main__ reads disk
gk-data/packs/fusion/data/seed/structures/_plan.json                             regenerated, never hand-edited
tools/seedsmith/tests/test_structures_adapter.py            new
```

## 8. Acceptance (contract level)

1. `isinstance(resolve_adapter("structures"), SeedAdapter)` is true.
2. `legal_combinations()` returns `False` for at least one real `(role, requiredSlotKind)` pair and
   `True` for every committed pair.
3. `channels()` is empty. It is asserted, so nobody "fixes" it.
4. Every registry vocabulary equals its schema tuple. It is a **closed vocabulary**, so membership is
   asserted exactly, because a change is a reviewed schema edit.
5. **Reconciliation.** `sum(plan["actualCounts"].values()) == len(load_rows(root))`, and that equals the
   number of non-exemplar `structure-anchor` entries on disk, counted by the test. No literal.
6. Every id the C# reader would load, meaning every `structure-anchor` entry under the root, is in
   `load_rows`. The test walks the directory independently and compares the id sets.
7. The regenerated plan is byte-identical across two runs (hash of the written file).
8. `python -m seedsmith check gk-data/packs/fusion/data/seed/structures --adapter structures` exits without `CANNOT_RUN`.
   The `Coverage/PairwiseHole` findings it prints are readings.
9. `check --adapter actions` and `check --adapter dungeon` return the same findings before and after the
   hook (the existing suites stay green).
10. No test in this module names a row count.

## 9. Test plan and verification boundary

| Test | Asserts |
|---|---|
| `test_satisfies_seed_adapter_protocol` | criterion 1 |
| `test_legality_has_a_real_false_case` | criterion 2 |
| `test_channels_is_deliberately_empty` | criterion 3 |
| `test_registries_mirror_the_schema_tuples` | criterion 4 |
| `test_plan_counts_exactly_the_rows_on_disk` | criteria 5 and 6 (walks the tree independently of the loader) |
| `test_projection_lifts_anchor_fields` | `entry.get("role")` is non-`None` for every loaded entry |
| `test_exemplars_are_not_counted` | a temporary `_exemplars/x.json` fixture is marked exemplar and absent from `load_rows` (in-memory `tmp_path`; the disk *is* the subject here) |
| `test_plan_rerun_is_byte_identical` | criterion 7 |
| existing `test_actions_adapter.py`, dungeon tests | criterion 9 |

Every test runs offline. No test imports the transport.

**Verification boundary: a gap, stated.** `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/structures/**` have no
mapping in `gk-core/scripts/verification-boundaries.v1.json`, so `scripts/verify-change.ps1:118` throws
`VERIFICATION BOUNDARY MISSING`. The owner of the fix is `test-verification-boundary` `python-test-lane`
(`docs/architecture/test-verification-boundary/spec-python-test-lane.md:16`, `:110-112`). Until it
lands, the focused pytest command in §6 is the boundary. It is not replaced by a broad suite.

## 10. Hard edges

- **Never commit a plan that fails `check_plan`** (§5.5). A new legal pair (`Store`/`Vault`) changes
  the legality function's answer, which is the intended correction: the pair has shipped since
  `relic-vault` landed.
- **`legalRoleSlotPairs` is still derived only from rows** (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:74-75`,
  `:154-160`), so a new role has no legal pair until a row exists. `exchange-role` must add pairs
  declared ahead of content. This adapter reads the plan, so it inherits that fix without change.
- **The core hook touches two other adapters' wiring.** It is behaviour-preserving, and their own suites
  prove it (criterion 9).

## 11. Dependencies

- Upstream: none.
- Downstream: `world-budgets`, `structure-bands`, `world-name-index` and `corpus-metrics` read the
  corpus through this loader.
- Cross-map: `test-verification-boundary` `python-test-lane` (soft: the local verification lane).

## 12. Open questions

None. The one core touch is decided in §5.4, by the principle that an open/closed seam is not extended.

## 13. DESIGN-GATE §5 checklist

```
[x] Subsystems: seedsmith adapter layer, report CLI, structure planner and metrics entry points.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/empire-seed/**
    for this spec. The build session records its own paths (gk-forge/tools/seedsmith/**, gk-data/packs/fusion/data/seed/structures/_plan.json).
[x] Read this session: DESIGN-GATE §1 seedsmith, tunables and validation rows; seedsmith-map P1-P5;
    item/seed-contract §1-§3; ai-native-generation README; validation-ssot; spec-adapter-creatures.md (house style).
[x] decisions.md: no lock on adapter wiring. The D-E2 ownership row is present (working tree, 2026-09-19).
[x] Every claim cites file:line.
[x] audit-doc-citations run on this file: no HIGH finding.
[x] Verified against code: Entry.get, Corpus.load, cli.py branches, planner/metrics __main__ blocks.
[x] Read the surrounding section of each quoted rule.
[x] Tested constraints: ran build_plan + check_plan over the 28 disk rows (passes, density 2800 -- a
    reading); counted disk rows vs ALL_ROWS.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the map's two mis-statements are recorded in §3 and in the map's spec-phase notes.
[x] No population pin. Acceptance is reconciliation plus closed vocabularies with the reason stated.
[x] No event-refreshed cache.
[x] Ordering: the loader sorts by (path, id); file enumeration order cannot change the result.
[x] No actor magnitude.
[x] SOLID: removes an OCP seam (per-adapter elif) rather than extending it.
[ ] New rule registry row: none introduced.
[x] Round 5 (2026-09-20): B1 — legality covers every requiredSlotKinds entry.
```

# Spec: `corpus-metrics`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `corpus-metrics` · **Map row:** 9 ·
**Wave:** 2
**Depends on:** `structures-adapter`, `structure-bands`, `world-budgets` (and `world-name-index` for one
metric, §5.2) · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

Close the structure metric set over the **committed corpus**. Every metric declares closed or open loop,
every closed metric has a target read from tuning or from a contract, and no open-loop metric can make a
report fail. Three missing metrics are added: bands resolve, names are unique across corpora, and the
review queues that invention needs.

**Done means:** `run_all(load_rows(root), tuning)` is the report the planner and `world-namer` consult.
Its closed-loop verdict is the gate before any model call. It prints corpus scale as readings and asserts
none.

## 2. Scope and non-goals

**In scope.**
- Switching the measured input to disk.
- Three new closed metrics.
- Fixing the n-gram metric's input.
- Declaring the two-producer metric's deferral.

**Not in scope.**
- Metrics over legion seeds. `legion-seed-rows` reuses this module's registry shape for its own family.
- Any gate on generated text quality. That is open-loop by nature (P3).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | A registration that refuses a metric with no loop, a closed metric with no target, and an open metric with a target | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:54-65` |
| Built | `Report.passed` reads only closed-loop results | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:232-237` |
| Built | Eight closed and two open metrics: schema conformance, per-role coverage, grid density, tier-ladder completeness, non-empty acquisition paths, idempotency, unresolved rate, rarity-strength correlation; flavour distinctness and n-gram overlap | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:215-224` |
| Wiring gap | The `__main__` report measures the generator's `ALL_ROWS`, not disk | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:259-266` |
| Wiring gap | `_idempotency` proves the generator reruns identically, but not that the committed tree equals the generator's output | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:116-135` |
| Wiring gap | `_mode_collapse_ngram_overlap` says it reads `reason` and actually reads `_provenance.citation`, which is the author's source note, not player-facing prose | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:173-183` |
| Wiring gap | `_schema_conformance` compares anchor key sets but does not validate enum membership row by row | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:74-80` |
| Real gap | Bands-resolve, cross-corpus name uniqueness, and the two-producer metric | — |

## 4. Principles as they bind this module

- **P2** (a target is declared) and **P3** (closed or open, and open never gates), restated in the
  module's own docstring (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:1-5`).
- **A guardrail validates the contract** (`validation-ssot.md`). The report prints scale and asserts
  relationships.
- **Distinctness reads abilities, not stats** (seedsmith-design ②). `rarity` and `strengthBand` stay out
  of the distinctness signature, and the existing source-scan test keeps that true.
- **No model.**

## 5. Design

### 5.1 The metric set after this module

| Metric | Loop | Target (source) | Change |
|---|---|---|---|
| `schema_conformance` | closed | every row validates with `jsonschema` against the anchor schema, enum membership included | strengthened (§3) |
| `bands_resolve` | closed | every ordinal of every row with `structureKind != none` is a key of its band table in the published `structure-seed` tuning | **new** |
| `per_role_coverage` | closed | tuning `budget` ± `metrics.roleCountTolerance` | input → disk |
| `grid_density` | closed | tuning `metrics.densityBand` (target by key path, `world-budgets` §5.1) | input → disk |
| `tier_ladder_completeness` | closed | every rung of `bands.tierLadder` has a row | reads the ladder from tuning, not the schema tuple |
| `acquisition_paths_non_empty` | closed | 100% | unchanged |
| `name_unique_across_corpora` | closed | zero collisions: no row's normalised name is owned by another entry in `world-name-index` | **new** |
| `idempotency` | closed | the generator's output hash equals the committed tree's hash (excluding `_plan.json`, `_registry/`, `_exemplars/`) | strengthened |
| `unresolved_rate` | closed | ≤ tuning `metrics.unresolvedCeilingMilli` | unchanged (reads 0 until GENERATED rows exist) |
| `rarity_strength_correlation` | closed | no lockstep power axis (existing target) | unchanged |
| `flavour_distinctness` | **open** | review queue | unchanged |
| `mode_collapse_ngram_overlap` | **open** | review queue | input → `flavor` + `reason` text (§3) |
| `flavor_missing` | **open** | review queue | registered by `world-exemplars` |

### 5.2 `name_unique_across_corpora`

The metric reads `world-name-index`'s `NameIndex`. It depends on that module, which is a dependency the
map's §4 row for this module omits. `world-name-index` is also in Wave 2 and has no dependency on this
module, so the edge adds no cycle. It is recorded as a correction.

### 5.3 The two-producer metric: declared here, not registered

*"Every good has two or more producers"* (Against the Storm, `empire-seed-ideal.md` §5.5 lesson 2) needs a
goods-chain definition, and `trade-network` `sector-yield` owns that. A metric registered before it can
measure would either always pass, which is a lie with a checkmark on it, or always fail, which is a red
suite by design. Neither is allowed. So the metric is **not registered** in this module. This spec
carries its definition, closed loop with the target *"every good in the goods registry has ≥ 2 producing
structure rows"*, and the module that registers it is `trade-structure-rows`, once `sector-yield` ships
the chain.

### 5.4 The report

`python -m seedsmith.adapters.structures.metrics` prints the header, one line per metric, and a
**readings block**: rows per role, rows per `(role, requiredSlotKind)`, density, and the unresolved count.
The block is printed and never asserted. The exit code is `Report.passed` over closed metrics only.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith.adapters.structures.metrics
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q
```

## 7. Acceptance (contract level)

1. Every registered metric declares a loop, and every closed metric a target. The registration error
   stays and is tested.
2. For every open metric, a fixture that makes it report its worst value leaves `Report.passed` true.
3. `bands_resolve` fails on a fixture row with an ordinal that has no band row, and passes on the
   committed corpus.
4. `name_unique_across_corpora` fails when a fixture row takes a name owned by another corpus entry
   (after normalisation), and passes on the committed corpus.
5. `idempotency` fails when a committed file is altered in a `tmp_path` copy.
6. `mode_collapse_ngram_overlap` reads no `_provenance` field (a source-scan test).
7. The report's readings block exists, and no test asserts any value in it.
8. The whole suite runs with the transport stubbed to raise.

## 8. Test plan and verification boundary

`test_structure_metrics.py` is extended for criteria 1-8. Fixtures are in-memory row lists or a
`tmp_path` copy of the tree, the latter only where the disk is the subject (criterion 5).

**Verification boundary: a gap.** `gk-forge/tools/seedsmith/**` is unmapped (`gk-core/scripts/verify-change.py:771`). The
owner of the fix is `test-verification-boundary` `python-test-lane`. The pytest command in §6 is the
boundary.

## 9. Hard edges

- **Strengthening `schema_conformance` may surface rows that pass the key-set check but fail enum
  membership.** If it does, the fix is in the generator's source and a regeneration, never an edit to
  the JSON.

## 10. Dependencies

- Upstream: `structures-adapter` (`load_rows`), `structure-bands` (band tables, `structureKind`),
  `world-budgets` (targets by key path), `world-name-index` (one metric; correction to the map's row).
- Downstream: `call-budget-dry-run` (runs the report before rendering), `world-namer` (the gate before
  spending tokens), `trade-structure-rows` (registers the two-producer metric).

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: structure metrics module and its tests.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: seedsmith-map P2/P3, ai-native README §7, validation-ssot, metrics.py in full.
[x] decisions.md: no lock.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: the citation-vs-reason mismatch and the idempotency scope, by reading the functions.
[x] Read surrounding sections.
[x] Tested: none claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the world-name-index dependency and the two-producer deferral, recorded in the map.
[x] No population pin.
[x] No cache, no ordering, no actor magnitude.
[x] SOLID: one metric registry per family; reuses SemanticDedup and the name index.
[ ] New rule registry row: none.
```

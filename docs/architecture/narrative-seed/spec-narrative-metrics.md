# Spec: `narrative-metrics`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `narrative-metrics` · **Map row:** 13 · **Wave:** 3
**Depends on:** `narrative-contract` · **Model calls:** none
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §5.2d (diversity), §6.5, §6.7, §11 items 2 and 8
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Measure the narrative corpus against **declared** targets, and say for every measurement whether it can
verify its own fix. A metric without a declared target is an opinion (seedsmith P2); an open-loop metric
that contributes to a pass is *"a lie with a checkmark on it"* (`docs/research/ai-native-generation/README.md`
§7). This module adds narrative metrics to seedsmith's one metric registry; it builds no second report.

Closed-loop metrics (may, once calibrated, gate): per-cell coverage, choice-kind distribution, required
line-pair coverage, arc and chain integrity, per-cell diversity. Open-loop metrics (readings and review
queues, never a pass): acceptance per voice register, voice distinctness.

## Design

### 1. One registry, one base class

Every metric subclasses `Metric` (`gk-forge/tools/seedsmith/seedsmith/metrics/model.py:86`) with a stable `id`, a
`family`, a `loop` (`Loop`, `gk-forge/tools/seedsmith/seedsmith/metrics/model.py:26`), `gates=False` at birth, and
declared `needs`; findings are `Finding` rows with mandatory `evidence` (`gk-forge/tools/seedsmith/seedsmith/metrics/model.py:44`).
They are registered in `build_registry` (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:73`), one line each, and
reached through `seedsmith report --adapter narrative`. Metrics are pure functions of the context; none
reads another metric's output (`seedsmith/spec-metrics.md` §6).

**Budget wiring gap.** `cmd_report` builds budget rows for the `items` adapter only
(`gk-forge/tools/seedsmith/seedsmith/report/cli.py:514`). A narrative metric that needs `budget` would therefore
report `NOT_MEASURED` forever. This module adds the `narrative` branch that loads the narrative budget
file into `Ctx.budget` as `BudgetRow`s (`gk-forge/tools/seedsmith/seedsmith/budget/model.py:37`). The budget
**file** and its coverage rows are authored with `narrative-planner`; this module consumes rows of the
existing shape and never invents a target.

### 2. The catalogue

| Metric id | Family | Loop | Needs | What it measures | Target from |
|---|---|---|---|---|---|
| `Narrative/CellCoverage` | Coverage | CLOSED | corpus, budget | per planner cell (host × kind × climate for storylets; side × role × element for characters), seeds present vs declared `target` with asymmetric tolerance | budget coverage rows (`narrative-planner`) |
| `Narrative/ChoiceKindDistribution` | Distribution | CLOSED | corpus, budget | share of storylets offering each choice kind, against a declared floor per kind | budget `distribution.choiceKind` |
| `Narrative/ChoiceTypeDistribution` | Distribution | CLOSED | corpus | share of each passing choice type (`relaxed`, `dilemma-upside`) per cell, computed by `narrative-validators`' classifier; reported, not gated, until calibrated | none yet: `NOTE` severity only until a row is declared |
| `Narrative/LinePairCoverage` | Coverage | CLOSED | corpus, adapter | every character carries a line for every required (context, band) pair its registry declares | `character-vocab`'s required-pairs registry (a declaration, not a budget number) |
| `Narrative/ArcIntegrity` | Linkage | CLOSED | corpus, adapter | every arc has the link count its shape declares, every link resolves to a storylet in the same arc, flags read by a link are set by an earlier link, and the persistent roles are declared by every link that uses them | `arc-shapes` registry |
| `Narrative/ChainIntegrity` | Linkage | CLOSED | corpus | every chain or link reference resolves; no reference points outside its own arc; no cycle | contract rule |
| `Narrative/TombstoneIntegrity` | Linkage | CLOSED | corpus | no tombstoned id is referenced by a live seed; no id is reused after its tombstone | contract rule (`narrative-emit`) |
| `Narrative/CellDiversity` | Quality | CLOSED | corpus, budget | per cell: compression ratio of the concatenated text, and long-n-gram self-repetition (share of word 5-grams that repeat across seeds in the cell) | budget `diversity.*` |
| `Narrative/VoteDisagreement` | Distribution | CLOSED | corpus, run ledger | per voted field (`ordinal`, `consequence`, `role`, `voice`): share of items whose vote was `split` (from `_provenance`) or `unresolved` (from the ledger's terminal rows) | none yet: `NOTE` severity only until a row is declared (Audit 2026-09-19: a metric with no declared target is a reading, seedsmith P2); a near-zero field is a candidate to leave the vote set, a high one a description to rewrite (ai-native README §2) |
| `Narrative/RegisterAcceptance` | Quality | **OPEN** | corpus, adapter | acceptance rate per voice register and per prompt version, from `review-render`'s recorded verdicts | reading only |
| `Narrative/VoiceDistinctness` | Quality | **OPEN** | corpus | leave-one-out accuracy of a classifier that tells cast members apart by their lines | reading only; low accuracy pushes the affected characters into the review queue |

**Why coverage is per cell, not per kind.** The committed Delve corpus shows the failure a per-kind count
cannot see: 39 of 54 events chose `climateAffinity: none` and none chose ice, earth or light (map §3.4).
Per-kind counts were all healthy.

**Why `CellDiversity` is closed-loop.** Its fix (regenerate the flagged cell) is re-measured by the same
metric, which is the definition of closed-loop (`seedsmith/spec-metrics.md` §1). Its thresholds are
calibrated on this corpus before it gates; embedding near-duplicate thresholds are never borrowed from
another corpus (ideal §5.2d). Distinct-n is not used (length-biased, ideal §5.2d).

**Why `VoiceDistinctness` is open-loop.** A classifier that cannot tell two characters apart shows voices
converged, but no machine check can confirm a rewrite restored a *good* voice. It produces a review queue
and never gates (ideal §11 item 8). It never judges a single line.

### 3. Algorithms (stdlib only)

- **Compression ratio.** `len(zlib.compress(text_bytes, level)) / len(text_bytes)` over the cell's
  concatenated AUTHORED text with tokens replaced by their token id (so name length never moves the
  ratio). The zlib level is a structural constant with a comment (it changes the unit of measure, not the
  game).
- **Self-repetition.** Lowercased word 5-grams per seed; the share of the cell's 5-gram occurrences whose
  5-gram occurs in at least two different seeds of the cell. The n-gram length lives in the budget as
  `diversity.ngram` so it can be retuned without a code change.
- **Voice distinctness.** A multinomial naive Bayes over character 3-grams and word unigrams of each
  character's lines, evaluated leave-one-line-out within a comparison group (same role, same side), macro
  accuracy reported per group. Deterministic: no random split, no seed. Groups with fewer than
  `voice.minCharacters` characters report `NOT_MEASURED`.
- **Vote disagreement.** Reads `_provenance.votes.<field path>.confidence` per voted field as
  `narrative-emit` records it (`high`, `split`), plus the run ledger's `unresolved` terminal rows for the
  third outcome — an `unresolved` item never reaches the corpus, so it cannot be read from `_provenance`
  (Audit 2026-09-19: the path and the source of `unresolved` were wrong; `resolve_vote` result shape at
  `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`).

### 4. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `metrics`. Every value is a starting
shape; the metric reports against it with `gates=False` until a person looks at the readings on a
corpus believed healthy and flips it (`seedsmith/spec-metrics.md` §4).

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `distribution.choiceKind.<kind>.floorPermille` | ‰ of storylets | 100 for each of the seven kinds other than `leave` | every kind appears in at least one storylet in ten; the planner allocates patterns to meet it. `leave` has no row: every storylet carries exactly one, so a floor on it measures nothing (Audit 2026-09-19) |
| `diversity.compressionRatio.min` | ratio | set from the first calibrated reading | a threshold guessed before measuring either never fires or fires constantly (`spec-metrics.md` §4) |
| `diversity.selfRepetition.maxPermille` | ‰ | set from the first calibrated reading | same |
| `diversity.ngram` | words | 5 | long enough to skip shared function-word runs |
| `voice.minCharacters` | characters per comparison group | 3 | a two-way classifier is a coin flip |
| `review.registerMinVerdicts` | verdicts | 8 | below it the acceptance rate prints as `NOT_MEASURED` rather than a noisy percentage |

"Set from the first calibrated reading" is a declared state, not a missing value: the row exists with
`derivation: pending-calibration` and the metric reports `NOTE` with its evidence until the value is
published.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_metrics.py -q
cd tools\seedsmith; python -m seedsmith report --adapter narrative --corpus ..\..\data\seed\narrative
cd tools\seedsmith; python -m seedsmith report --adapter narrative --corpus ..\..\data\seed\narrative --metric Narrative/CellCoverage --json out.json
cd tools\seedsmith; python -m seedsmith metrics --coverage    # the catalogue's own coverage of Appendix-A rows
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/metrics/__init__.py       (new) ALL_NARRATIVE_METRICS
tools/seedsmith/seedsmith/adapters/narrative/metrics/coverage.py       (new) CellCoverage, LinePairCoverage
tools/seedsmith/seedsmith/adapters/narrative/metrics/distribution.py   (new) ChoiceKind, ChoiceType, VoteDisagreement
tools/seedsmith/seedsmith/adapters/narrative/metrics/linkage.py        (new) ArcIntegrity, ChainIntegrity, TombstoneIntegrity
tools/seedsmith/seedsmith/adapters/narrative/metrics/diversity.py      (new) CellDiversity
tools/seedsmith/seedsmith/adapters/narrative/metrics/voice.py          (new) VoiceDistinctness, RegisterAcceptance
gk-forge/tools/seedsmith/seedsmith/report/cli.py                                build_registry lines; the narrative budget branch in cmd_report
tools/seedsmith/tests/test_narrative_metrics.py                        (new)
```

Metrics live in the adapter because they read narrative registries; the base classes and the runner stay
in `seedsmith.metrics` (P5).

## Code style

```python
class CellCoverage(Metric):
    id = "Narrative/CellCoverage"
    family = "Coverage"
    loop = Loop.CLOSED
    gates = False            # promoted only after calibration (spec-metrics.md §4)
    needs = frozenset({"corpus", "budget"})

    def run(self, ctx: Ctx) -> "list[Finding]":
        """One finding per cell outside tolerance; evidence carries observed, target, tolerance.
        A missing budget row is NOT_MEASURED for that cell, never a pass."""
```

## Testing strategy

Synthetic fixture corpora only (`seedsmith/spec-metrics.md` §6): each metric gets one fixture that must
trip it, one that must not, and — for closed-loop metrics — one proving the `assertion` flips true when
the defect is fixed. The model transport is stubbed to raise in every test module.

| Test | Asserts |
|---|---|
| `every_metric_declares_loop_and_starts_ungated` | every narrative metric has a `loop`, and `gates is False` |
| `open_loop_metrics_cannot_gate` | registering `RegisterAcceptance` or `VoiceDistinctness` with `gates=True` raises at registration |
| `cell_coverage_trips_and_clears` | an under-filled fixture cell is a `GAP` with `observed`/`target`/`tolerance` evidence; filling it clears the assertion |
| `missing_budget_row_is_not_measured` | a cell with no row reports `NOT_MEASURED`, never a pass |
| `climate_skew_is_visible_per_cell` | a fixture shaped like the committed skew (most seeds at `none`) trips per-cell coverage while a per-kind count would pass |
| `line_pair_coverage_names_the_missing_pair` | a character missing `(refused, hostile)` is one finding naming character, context and band |
| `arc_integrity` | a link pointing outside its arc, a read flag never set, a missing link, each one finding |
| `tombstone_reference_is_a_gap` | a live seed referencing a tombstoned id fails; a reused id fails |
| `diversity_is_name_length_invariant` | swapping the names registry does not change the compression ratio (tokens are replaced by ids) |
| `self_repetition_trips_on_template_reuse` | three seeds sharing a 5-gram run trip; three distinct seeds do not |
| `voice_distinctness_is_deterministic` | two runs give identical accuracy; a fixture of two characters with identical lines scores at chance and enters the queue |
| `vote_disagreement_reads_provenance` | `split` shares match the fixture provenance and `unresolved` shares match the fixture ledger |
| `no_metric_reads_another_metrics_output` | metrics run in reversed and shuffled order give identical findings |

No test asserts a corpus size, a per-cell count of the committed corpus, or an acceptance percentage.

## Success criteria

1. Eleven metrics registered, each with its loop declared and `gates=False`.
2. `seedsmith report --adapter narrative` measures budget-backed metrics instead of reporting
   `NOT_MEASURED` for all of them (the §1 wiring gap closed).
3. Every closed-loop metric has a trip fixture, a clean fixture and an assertion-flip fixture.
4. The two open-loop metrics produce review-queue findings and cannot gate.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** declare the loop; start ungated; put evidence in every finding; read targets from the budget
  file or a declared registry; report `NOT_MEASURED` when a need is absent.
- **Ask first:** flipping any metric to `gates=True` (after its calibration reading is published);
  adding a model-based judge (a model judge may rank prompt versions over a batch, never pass or fail one
  item, and never judge its own model's output — ideal §5.2b).
- **Never:** gate on an open-loop metric; assert a population count in a test; borrow a threshold from
  another corpus; let a metric depend on another metric's output.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | `VoteDisagreement` read `unresolved` from `_provenance`, where it can never exist, at a path emit does not write | fixed (ledger + `_provenance.votes`) |
| 2 | low | `VoteDisagreement` had no declared target (P2) | fixed (`NOTE` only until a row exists) |
| 3 | low | A choice-kind floor on `leave` measures nothing | fixed |
| 4 | low | Loops declared, open-loop metrics cannot gate, no population asserted | verified |

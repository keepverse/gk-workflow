# RB-H1 — the roster's coverage axes, and its two metric blind spots

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` RB-H1 (received from `roster-balance` via `backlog-clean-up` BCU4.5).
Edited: `gk-forge/tools/seedsmith/seedsmith/metrics/creature_roster.py`,
`gk-forge/tools/seedsmith/tests/test_roster_metrics.py`. Both metrics are `roster-balance`'s own; the *fix* is this
row's, and the file is inside this lane's fence.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `posture: "unresolved"` visible to BOTH metrics | `python -m pytest tests/test_roster_metrics.py -q` (in `gk-forge/tools/seedsmith`) | **18 passed in 0.28 s** — `test_a_planted_unresolved_posture_is_visible_to_both_metrics` plants one unresolved posture in 20 and asserts a finding from EACH metric; `test_an_all_unresolved_roster_is_named_not_merely_not_measured` proves the old shape returned only `NOT_MEASURED` ("no species with a resolved posture") — the silent drop, not a zero | `creature_roster.py` |
| The old behaviour really was a drop | same run | `UnresolvedCountMetric.VOTED_FIELDS` now carries `posture` (the ONE derived field that can carry the sentinel, via `derive_posture`), and `PostureBalanceMetric` counts every row whose posture is none of its three keys instead of skipping it — emitting its own finding with `evidence={"unresolved", "total", "resolved"}`, and still a `NOT_MEASURED` suite row when nothing is resolved | same |
| No gate semantics silently tightened | same run + `-k "metric or roster"` | sub-threshold unresolved counts are reported at `Severity.NOTE`, not `GAP`, so adding a field to a `gates=True` metric cannot fail a run it used to pass; `UnresolvedCountMetric.gates` is unchanged and `test_open_loop_metric_never_contributes_to_pass` still pins it | same |
| No population size pinned in a test | same run | every new assertion uses `len(anchors)` (or the fixture's own list) — no literal count anywhere | `test_roster_metrics.py` |
| The row's own Verify line | `python -m pytest tests/ -q -k roster` (in `gk-forge/tools/seedsmith`) | **67 passed, 4407 deselected, 9.16 s** | — |
| Wider metric surface | `python -m pytest tests/ -q -k "metric or roster"` | **240 passed, 4234 deselected, 4 subtests passed, 11.08 s** | — |

## Current readings, per axis — each dispositioned

Measured this session over the real committed corpus: **904 anchors**, by loading
`gk-data/packs/fusion/data/seed/creatures/species/**` into `Ctx(creature_anchors=…)` and running `ALL_CREATURE_ROSTER_METRICS`
directly (the same classes the registry runs).

| Axis | Reading | Disposition |
|---|---|---|
| Grid occupancy | **129/252 cells (511‰)** vs the 900‰ target — 123 empty cells, all over the element-pair × aptitude cross-product | **A ladder/curve (tuning) problem, not content.** 900‰ of a 252-cell cross-product needs ≈227 occupied cells; the source game's 904-species almanac cannot supply that density, so the *target* is mis-scaled for a cross-product grid. Retune `gridFill.minOccupiedSharePermille` in `gk-core/data/tuning/creature-roster-targets.v1.json` — an owner-facing balance change, filed as **RB-H1-F**. |
| Single-element share | **497‰** — no finding (inside the band) | **Accepted with a stated reason:** roughly half the corpus carries no secondary element, which is the intended shape — the fusion-lineage pass deliberately leaves a secondary absent when neither parent supplies a clean single signal. |
| Aptitude distribution | 5 families below the 500‰-of-mean target: **Agility 28, Composure 5, Ferocity 6, Might 10, Vigor 7** (mean 75.3) | **A content gap in the classification pipeline**, not the roster: the metric's own remedy names it (an `aptitude-primary` description that does not separate these families). Closing it is a MODEL pass — **a manager job** per this run's standing note, not this lane's. |
| Posture balance | **Bastion 373 · Force 348 · Finesse 183**, 0 unresolved — no finding | **Accepted** (inside band; the posture axis is the aptitude axis seen from the other side). |
| Threat-band occupancy | **10/10 rungs occupied** — no finding | **Accepted.** |
| Rarity monotonicity | 4 non-monotone adjacent pairs: `sprout 45 > chaff 34`, `cultivated 159 > grafted 33`, `fused 486 > cultivated 159`, `almanac 23 > sunwoven 4` | **A ladder/curve (tuning) problem.** The 486-strong `fused` mass is the *deterministic fallback's* own rung (`creature-rarity-power-fallback.v1.json` maps threat rung 5 → `fused`), so the skew is the fallback concentrating the corpus, not a classification outcome. Retuning the fallback (or accepting the concentration in the target band) is owner-facing — filed as **RB-H1-F**. |
| Family size spread | no finding | **Accepted.** |
| Unresolved counts | **0 unresolved on every reported field** — and `posture` is now among them | **Accepted**, and now *falsifiable*: the next run that leaves a posture unresolved produces a named finding instead of being invisible. |

## NOT proved / declared gaps

- The two tuning dispositions above are named, not performed: a balance change needs the owner's ruling and
  a published revision (`gk-core/tools/tuning/publish.py`), so they are filed as **RB-H1-F** rather than folded in here.
- The aptitude skew is recorded as a content/pipeline gap for a model pass — deliberately NOT acted on in this
  lane (the standing rule: corpus/model rows are manager jobs).
- "A test with a planted unresolved row proves the old behaviour was a silent drop" is proven for
  `PostureBalanceMetric` (the all-unresolved roster returned only `NOT_MEASURED` before, and now names the
  count). For `UnresolvedCountMetric` the proof is structural — the field was not in `VOTED_FIELDS`, so no
  code path could report it — plus the positive test that it now does.

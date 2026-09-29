# ST3.1 — `action-rungs.v3` `scopeWindows`, and the planner reads it through one loader (H7)

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| v3 published **by the tool** | `python gk-core/tools/tuning/publish.py action-rungs --label "ST3 scope windows" --add-key ':scopeWindows={...}' --add-key '_meta:scopeWindowsNote=...'` | **`scopeWindows  ADDED` · `_meta.scopeWindowsNote  ADDED` · `published action-rungs (v2 -> v3, 2 change(s)); v2 stays on disk for revert`.** Never hand-edited; `version: 3`, `cap: 10` and all 10 rows inherited intact. | gk-core/data/tuning/action-rungs.v3.json |
| `load_scope_windows` refuses every case, naming the key | `python -m pytest gk-forge/tools/seedsmith/tests/test_distribution_planner.py -q` | **145 passed, 3 subtests passed.** a floor of 5 (`scopeWindows.species.floor` + `spec-rung-semantics.md`), a string `"6"` ceiling (`scopeWindows.family.ceiling`), a missing scope (`scopeWindows.family`), a ceiling above `cap` (`scopeWindows.species.ceiling`), non-monotone ceilings (`monotone`), and a gap in the rows (`contiguous`). | tests/test_distribution_planner.py |
| A 12-row contiguous fixture loads — the `cap == 10` literal is gone | same command | **Passes.** `cap: 12` with 12 contiguous rows and a matching `species` ceiling loads through both loaders. | src/…/distribution_planner/derive.py (load_rung_table) |
| The planner's windows **equal the file's block** | same command | **Passes.** The old literal pin (`test_distribution_planner.py:510`) is replaced: the block is read with plain `json` and compared against the loaded windows, so nothing in the test can pass by both sides calling the same loader. | tests/test_distribution_planner.py |
| A retuned window **reaches the briefs** | same command | **Passes.** A `family.ceiling = 6` fixture yields `rungBand [1, 6]` and structure axes taken from rung 6, not from the shipped ceiling. | tests/test_distribution_planner.py |
| The publish path itself is covered | `python -m pytest gk-core/tools/tuning -q` | **21 passed, 1 failed** (the failure is pre-existing and not this task's — see below). New `ActionRungsScopeWindowsTests`: `--add-key` writes the objects and refuses a second add, `set scopeWindows.family.ceiling=6` writes an **int**, and `main()` on a v2 fixture really writes v3 with the block. | gk-core/tools/tuning/test_publish_add_key.py |
| Everything else that shares the changed signatures | `python -m pytest gk-forge/tools/seedsmith/tests/test_validate_heal.py test_characteristic_pool.py test_coverage_report.py test_innate_picker.py test_distribution_planner.py -q` | **384 passed, 1 skipped, 3 subtests passed.** | — |

## The one red, diagnosed (not this task's)

`gk-core/tools/tuning/test_resource_ownership.py::test_1_generation_reproduces_shipped_resource_edges_byte_for_byte`
asserts `version == 5` for `aptitudes`, while the shipped file is `aptitudes.v8.json`. Dated by git:
that test last changed **2026-09-04** (`dcabac329`), `aptitudes.v8.json` shipped **2026-09-12**
(`740920d2e`) — a stale pin that predates this branch, in a file outside this session's fence, reading
a different tuning domain. Nothing in ST3.1 touches it.

## Two deliberate deviations, both forced

1. **`RUN_WINDOW` is still defined, with a loud deprecation block — it is not deleted here.**
   Contract 2 wants it gone, but its only two remaining readers (`coverage_report/derive.py:45`,
   `innate_picker/derive.py:65`) import it at module level: deleting it here was tried and produced
   `ImportError: cannot import name 'RUN_WINDOW'` in **both** of their suites — a red tree between two
   commits of the same wave, which this repo forbids. ST3.2 migrates those two readers and owns the
   acceptance "grep RUN_WINDOW gk-forge/tools/seedsmith returns nothing"; its own Files note already says the
   deletion needs both stages in one change. The planner no longer reads it, and nothing new may.
2. **`generate_validate_heal.py` was moved to v3 too** (not in this task's Files line). It calls the
   shared `structure_axes_for`, which gained the `windows` argument, so leaving it would have broken
   `test_validate_heal.py` on my change. It now loads the windows from the same rung table it already
   reads for structures — H7's own "one file" — and the switch is behaviour-neutral: v3's rows are
   identical to v1's apart from the `powerBudgetMilli` column this stage never reads. ST5 will point
   it at v4 with the rest.

## Found for ST3.5, not fixed here

Pointing the planner at v3 **moves the plan's provenance hash**, by design: `_corpus_hash` folds
`rungs_doc["version"]`, so `2e8910cf…` (v1) becomes `99161625…` (v3) and the committed
`gk-data/packs/fusion/data/seed/actions/_briefs/round-1.json` is stale relative to a fresh plan. ST3.5's acceptance is
"`git diff --stat gk-data/packs/fusion/data/seed/actions/` is empty" and its own rule is that a non-empty diff is a defect in
ST3 — that rule does not hold for this one, and the diff is the version fold working, not new content.
A real regeneration cannot be run here at all: `refuse_full_run_if_ungated` refuses without `--full`,
and ST3.5's own command omits it (the smoke report itself is `verdict: pass`).

# ST3.3 — the general and family propose prompts label by scope

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Each `_RUNG_BAND_LABELS` keys by SCOPE with a direct index, so an unknown scope raises | `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_general_propose.py gk-forge/tools/seedsmith/tests/test_family_propose.py -q` | **158 passed, 1160 subtests passed.** Both tables are `{scope: label}` now and `_rung_band_label(scope)` indexes directly, raising and naming `EligibilityScope` instead of returning the old fallback string. | general_propose/prompts.py, family_propose/prompts.py |
| The rendered prompt is byte-identical at the shipped windows | same command | **Passes.** The scope→label pairs are the same strings the pair-keyed table held for the matching window (`general`→ early, `family`→ mid, `species`→ late), so each stage's real briefs render the identical text. | both prompts.py |
| Spec test 6b: a retuned window renders the label, never the fallback | same command (new `ScopeLabelTests` in both files) | **Passes.** A family brief at the RETUNED band `[1, 6]` renders exactly the same label as the shipped `[1, 7]` brief — asserted in both files — and never "a tier outside the three known scope windows". This is precisely the degradation the pair-keyed table produced. | tests/test_general_propose.py, tests/test_family_propose.py |
| An unknown scope raises | same command | **Passes.** `scope="not-a-real-scope"` raises and the message names both the scope and `EligibilityScope`. | both test files |
| No model is called | — | **None was.** `build_context` composes the prompt text only; no transport is imported or invoked anywhere in the new tests. | — |

## The five reds in this suite are pre-existing, and named

`RealWorkedExampleTests` (5 tests) fails because `render_worked_example()` returns `""`: it reads
`data/seed/actions/_candidates/general/round-1.json`, and **that whole directory is gitignored**
(`.gitignore:125` — a locally-generated pipeline output). `git check-ignore -v` confirms the path is
ignored, `git ls-files` shows it was never tracked, and nothing in this change creates or removes
anything under `data/` (`git status` lists only the two prompts files and their two test files). The
tests' own assertion message says what is happening — "the real pinned brief/answer pair must be found
in this checkout" — which is a property of a checkout that has not run that pipeline stage, not of the
label change.

## Why the label moved off the window

The old read was `_RUNG_BAND_LABELS.get((floor, ceiling), "a tier outside the three known scope
windows")`. Scope and window are a bijection only while the shipped values hold: retuning
`family.ceiling` to 6 makes a family brief's band `[1, 6]`, which misses the `(1, 7)` key, and the
fallback sentence is rendered into a model-calling prompt in place of the family label — a silent
degradation rather than a failure. Keying on the scope (a closed vocabulary) makes the label
retune-proof and turns a missing entry into the code defect it is.

# Spec: scope-window-tunables (ST3)

**Status: proposed 2026-09-18.** Module **ST3** of [action-skill-tiers-map.md](../action-skill-tiers-map.md).
No dependencies. Not approved; no build authorized.

## Objective

**Make the scope windows the tunables ruling 4 says they are.**

Ruling 4: *"Scope windows stay moderate tunable defaults … the windows may be tuned freely from day
one."* Today they cannot be tuned without a code edit:

| Where the window is written | Evidence |
|---|---|
| A Python constant in the planner | `distribution_planner/derive.py:381` — `RUN_WINDOW = {"general": (1, 4), "family": (1, 7), "species": (1, 10)}` |
| Re-imported as a constant by the coverage report | `coverage_report/derive.py:45`, used at `:180` and `:671` |
| Re-imported as a constant by the innate picker (species ceiling) | `innate_picker/derive.py:65`, `:103` (`CAP = RUN_WINDOW["species"][1]`) |
| Keyed by literal tuple in three prompt label tables | `general_propose/prompts.py:172-175`, `family_propose/prompts.py:198-201`, `signature_propose/prompts.py:215-218` |
| Pinned by a test | `tests/test_distribution_planner.py:510` asserts the literal dict |

Tunables rule T1: *"A number a balance pass would change lives in config, never in code."* A window is
exactly such a number. And the prompt tables mean a retuned window would **silently degrade** every
model-calling prompt: each table is read with `.get(key, "a tier outside the three known scope windows")`
(`general_propose/prompts.py:222`, `family_propose/prompts.py:253`, `signature_propose/prompts.py:291`), so
a `[1,6]` family band renders that fallback text into the prompt instead of failing. (Corrected
2026-09-18, strengthen pass: an earlier draft said it would raise.)

A related literal: the planner refuses any rung table whose `cap` is not 10
(`distribution_planner/derive.py:390`), while `ssot-power-scale.md:888` records `rungCap` as a soft,
tunable window. Ruling 2 keeps the ladder at 10 rows — this module does **not** change that value; it
stops the planner hard-coding it.

## Contract

1. **Publish** `gk-core/data/tuning/action-rungs.v3.json` from v2 with one new root block, through the
   existing tool (no hand edit, tunables T4):

   ```powershell
   python gk-core/tools/tuning/publish.py action-rungs --label "ST3 scope windows" `
     --add-key ':scopeWindows={"general":{"floor":1,"ceiling":4},"family":{"floor":1,"ceiling":7},"species":{"floor":1,"ceiling":10}}'
   ```

   This is **v3** — the first `action-rungs` publish after A-G1's v2, and it must land before ST4's R8
   retune (v4), which sits on top of it (map §5.1). Values are the shipped ones; R7 (2026-09-18) fixed the
   signature window at 1–10. **Objects, not pairs:** `publish.py`'s `set` path parses a value as int,
   float or bool and otherwise stores the raw string (`parse_value`, `publish.py:49-57`; `set_path` does
   no type check, `:152-165`), so a `[floor, ceiling]` array could only be retuned by writing the string
   `"[1,6]"`. With objects a retune is `scopeWindows.family.ceiling=6`, an int.
   `_meta` gains one line saying these are the planner's per-scope rung windows, that the floor is 1 by
   A-U1 §3.2, and that the ceiling is what bounds structure (authored `Rung`) and the holder's rung (ST2).
   `RungTableLoader` ignores unknown root keys (`RungTableLoader.cs:30-51` reads `cap` and `rows` only),
   so the C# side is unaffected.
2. **One loader.** `distribution_planner/derive.py` gains `load_scope_windows(path)` returning
   `{scope: (floor, ceiling)}` from the `{floor, ceiling}` objects, and `RUN_WINDOW` is deleted. It
   refuses, naming the key (a non-`int` bound, e.g. a string written by a mistyped `set`, included):
   - a missing scope among `general`, `family`, `species` (the closed `EligibilityScope` set,
     `ActionEnums.cs:84`);
   - a floor other than 1 (A-U1 §3.2 — the floor is dropped; this is that spec's planted-violation
     test 4, now enforced at load);
   - a ceiling outside `1..cap` or a row set that is not contiguous `1..cap` (replaces the literal
     `cap == 10` check at `:390`);
   - ceilings that are not `general ≤ family ≤ species` (A-U1 §3.2 point 2: `restriction` stays the
     signature tier's one exclusive axis only while signature's ceiling is the highest).
3. **Every reader takes the loaded windows.** `structure_axes_for`, `validate_rung_band` and the brief
   builder (`derive.py:396-412,770`), the coverage report (`:180,:671`) and the innate picker (`:103`)
   receive the loaded windows instead of importing a constant. Entrypoints load once and pass them down.
4. **Prompt labels key by scope, not by pair.** The three `_RUNG_BAND_LABELS` tables become
   `{scope: label}` and the `.get(…, fallback)` read becomes a direct index: an unknown **scope** raises
   (a closed `EligibilityScope` member missing from a label table is a code defect), and a retuned
   **window** no longer changes which label renders. The rendered prompt text is **byte-identical** at the
   shipped windows. This touches A-P1/A-P2/A-P3 source but calls no model and changes no rendered prompt.
5. **The planner reads v3.** `generate_distribution_planner.py:60` points at `action-rungs.v3.json`, so
   windows and structure budgets come from one file. The other seedsmith readers of the rung table
   (`characteristic_pool/pool.py:31`, `generate_validate_heal.py:54`) move in ST5, which also adds the
   one-version guard. Between ST3 and ST5 they read v1, whose rows are identical to v3's except the
   budget column they do not read.
6. **Register row.** `ssot-power-scale.md` §11 gains a row for `scopeWindows` (A-U1 §3.4 named this row;
   it was never written). That file belongs to the power program; the row is written as part of this
   module's change with that program's review.

   > **ERRATUM (manager ruling 2026-09-19, from the ST3.5 run).** The regenerate chain is the REAL
   > pipeline order, taken from `generate_action_pipeline.run_pipeline`, not the three commands in
   > §Seedsmith: characteristic_pool → type_weights → distribution planner (`--full`) →
   > **`coverage_assignment` (A-S7)** → … → innate_picker → coverage_report. A-S7 splices
   > `requiredFamilies` into the plan, so a planner-only "real" run drops that splice and reads as a
   > content regression when it is a missing stage. The planner's own `--dry-run` also refuses without
   > `--full` (`refuse_full_run_if_ungated`, `gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py:747`), so the dry-run form covers two of three.

## Tunables

| Key | File | Unit | Shipped value |
|---|---|---|---|
| `scopeWindows.{general,family,species}.floor` / `.ceiling` | `gk-core/data/tuning/action-rungs.v3.json` | rung index | floors `1` (fixed by A-U1 §3.2 / R7); ceilings `4`, `7`, `10` |

Retune (ruling 4: free from day one, no sign-off): `python gk-core/tools/tuning/publish.py action-rungs
scopeWindows.family.ceiling=6` → v{n+1} (the next free version — v5 once ST4's v4 exists), then re-run
the planner. Already-committed seed rows keep the band they were generated with; a changed window reaches
content only through regeneration, never a hand edit.

## Numeric types

Window bounds are rung indices, structural, `1..cap`. Python `int`; on the C# side they arrive as the
existing `RungBand(int, int)`.

## Seedsmith / generator

| Stage | File:line | Change |
|---|---|---|
| A-S1 distribution planner | `distribution_planner/derive.py:379-412,770`; `generate_distribution_planner.py:60` | Load windows from v3; delete `RUN_WINDOW`; replace the `cap == 10` literal |
| A-S5 coverage report | `coverage_report/derive.py:45,180,671` | Take loaded windows |
| A-S6 innate picker | `innate_picker/derive.py:65,103` | Species ceiling from loaded windows |
| A-P1/A-P2/A-P3 prompts | `general_propose/prompts.py:171-175`, `family_propose/prompts.py:200-201`, `signature_propose/prompts.py:217-218` | Label by scope; render byte-identical. **No model run** |
| Seed fields | — | **None new.** `rungBand` stays an index pair (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/kinds.py:24`); `audit_schema` unchanged |

Regenerate, all model-free, all expected byte-identical at the shipped values:

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith.adapters.actions.generate_distribution_planner --dry-run
python -m seedsmith.adapters.actions.generate_coverage_report --round 1 --dry-run
python -m seedsmith.adapters.actions.generate_innate_picker --round 1 --dry-run
```

Then the same three without `--dry-run`; `git diff --stat gk-data/packs/fusion/data/seed/actions/` must be empty. A non-empty
diff is a defect in this change, not new content.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest gk-forge/tools/seedsmith/tests/test_distribution_planner.py gk-forge/tools/seedsmith/tests/test_coverage_report.py gk-forge/tools/seedsmith/tests/test_innate_picker.py gk-forge/tools/seedsmith/tests/test_general_propose.py gk-forge/tools/seedsmith/tests/test_family_propose.py gk-forge/tools/seedsmith/tests/test_signature_propose.py -q
python -m pytest gk-core/tools/tuning -q
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~RungTable"
python scripts\audit-magic-numbers.py --summary
```

## Project structure

```
gk-core/data/tuning/action-rungs.v3.json                                   (published, never hand-edited)
gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py
gk-forge/tools/seedsmith/seedsmith/adapters/actions/generate_distribution_planner.py
gk-forge/tools/seedsmith/seedsmith/adapters/actions/coverage_report/derive.py
gk-forge/tools/seedsmith/seedsmith/adapters/actions/innate_picker/derive.py
gk-forge/tools/seedsmith/seedsmith/adapters/actions/{general,family,signature}_propose/prompts.py
gk-forge/tools/seedsmith/tests/test_distribution_planner.py  (+ the five suites above)
docs/architecture/power/ssot-power-scale.md                        (§11 row, power program's file)
```

## Code style

```python
def load_scope_windows(path: Path) -> "dict[str, tuple[int, int]]":
    """ST3: the per-scope rung windows, read from the published rung table -- never a literal.
    Refuses, naming the key: a missing scope, a non-int bound, a floor other than 1
    (spec-rung-semantics.md SS3.2, R7), a ceiling outside 1..cap, or ceilings that are not
    general <= family <= species."""
```

## Testing strategy

Contract, not values. The test that pins the literal windows (`test_distribution_planner.py:510`) is
replaced: it asserts the planner's windows **equal the published file's block**, never a literal.

| # | Test | Proves |
|---|---|---|
| 1 | Planner windows equal `action-rungs.v3.json`'s `scopeWindows` | Contract 2, 3 |
| 2 | A fixture file with a floor of 5 is refused naming A-U1 §3.2 / R7 | Contract 2 |
| 2b | A fixture whose `family.ceiling` is the string `"6"` is refused naming the key | Contract 2 |
| 3 | A fixture with a missing scope / a ceiling above `cap` / non-monotone ceilings is refused, each by name | Contract 2 |
| 4 | A fixture table with 12 contiguous rows and matching windows loads (the `cap == 10` literal is gone) | Contract 2 |
| 5 | A fixture with `family: [1,6]` produces family briefs with `rungBand [1,6]` and structure axes from rung 6 | Contract 3 — tuning actually reaches output |
| 6 | Each propose prompt renders byte-identical to its pre-change output for a fixture brief of each scope | Contract 4 |
| 6b | With `family.ceiling = 6`, a family brief's prompt renders the family label, never the "outside the three known scope windows" fallback | Contract 4 |
| 7 | `publish.py --add-key` on the v2 fixture writes v3 and refuses a second add; `set scopeWindows.family.ceiling=6` on it writes an `int` | Contract 1 (tool already tested in `gk-core/tools/tuning/test_publish_add_key.py`; add the action-rungs case) |

## Boundaries

- **Always:** publish through `gk-core/tools/tuning/publish.py`; keep the shipped values; regenerate model-free
  and diff.
- **Ask first:** changing the rung count (ruling 2). Window **ceilings** are free to retune through
  `publish.py` (ruling 4); this module ships the current values only because it is a no-behaviour-change
  extraction (tunables T7: extract, prove byte-identical, tune separately).
- **Never:** hand-edit a tuning file or `gk-data/packs/fusion/data/seed/actions/**`; run A-P1/A-P2/A-P3; reintroduce a floor
  above 1 without A-U1 §3.2 being overturned; pin a tunable value in a test.

## Success criteria

1. No rung window value is written in seedsmith code or tests.
2. Changing a window is one publish call and a planner re-run.
3. At the shipped values every regenerated seed file is byte-identical.

   > **ERRATUM (manager ruling 2026-09-19, from the ST3.5 run).** "Byte-identical" means identical
   > CONTENT **modulo the provenance hash**, not an empty `git diff`. The rung table's version is folded
   > into `_corpus_hash`, so pointing the planner at v3 moves `_meta.corpusHash` and every brief's
   > `_provenance.corpusHash` by design — the artifact's provenance now names its real input, which is
   > H7 taken seriously rather than a regression. Proof run at ST3.5: the model-free chain in pipeline
   > order rewrote seven files, and with every `corpusHash` removed from both sides the difference count
   > was **0** (6,656 hash moves in `_briefs/round-1.json` — one `_meta` plus one per entry — and one in
   > the coverage report; the other five files were untouched in content). A difference in any OTHER
   > field is still a defect in this change, never new content.
4. Every propose prompt renders byte-identical.

## Self-audit (debate pass)

- *"A separate `action-scope-windows` domain file instead of the rung table?"* The windows are rung-table
  semantics (which rungs a scope spans), the same file the planner already reads for structure budgets,
  and ST5 needs one rung-table version across readers anyway. A second domain file would make two files
  to keep in step for one question. Kept in the rung table.
- *"Should C# validate the windows too?"* The C# runtime never reads them — it reads the band carried on
  each action row. One reader, one validator (SOLID S).
- *"Monotone ceilings — a business rule sneaking into a loader?"* It is A-U1's stated structural
  consequence (signature's exclusive `restriction` axis), not a balance preference; a window set that
  breaks it silently changes which axes a scope may use.

## Open questions

None. The signature window is 1–10 (R7).

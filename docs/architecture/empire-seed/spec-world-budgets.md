# Spec: `world-budgets`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `world-budgets` · **Map row:** 3 ·
**Wave:** 0 · **Ideal id:** I5
**Depends on:** `structures-adapter` · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

Every corpus target is a published tuning value, and every test reads it. Seedsmith P2: *"a metric without
a declared target is an opinion."* The per-role budget and the density band already exist in tuning. What
this module removes is the **copies**: the tests and one metric declaration that restate the band as
literals, and the two tests that pin population counts. It also declares the budget **shape** for the
legion family, which `legion-bands` publishes.

**Done means:**
- No seedsmith structure test contains a density or a corpus-size literal.
- Publishing a new band moves the verdict with no code edit.
- The budget validates against the closed role list: every role has a target, and there is no target
  for a role outside the list.

## 2. Scope and non-goals

**In scope.**
- Replacing the density literals and the target string.
- Converting the population pins to reconciliations.
- Adding a budget-shape validator.
- The legion budget shape, as a documented contract.

**Not in scope.**
- The `Exchange` budget row. It lands with the role itself in `exchange-role`. The budget validator this
  module adds would reject a target for a role outside the closed list, and that is the point (§11).
- New metrics (`corpus-metrics`).
- Changing any budget value. The values are a tuning pass (`empire-seed-ideal.md` §10).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | Per-role `budget` floors, `metrics.densityBand`, `metrics.roleCountTolerance` | `gk-core/data/tuning/structure-seed.v1.json:3-14`, `:22-23` |
| Built | `check_plan` reads the band and the tolerance from tuning | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:139-148` |
| Built | `per_role_coverage` and `grid_density` measure against tuning | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:83-100` |
| Wiring gap | Density restated as literals | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:192-195`; `gk-forge/tools/seedsmith/tests/test_structure_planner.py:58-60` |
| Wiring gap | The declared target is a literal string `"2400-4000 per-mille"` | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:217` |
| Wiring gap | Population pins: `len(DUMPED_ROWS) == 8`, `len(AUTHORED_ROWS) == 17`, `len(ALL_ROWS) == 25` | `gk-forge/tools/seedsmith/tests/test_structure_corpus.py:149`, `:312-317` |
| Wiring gap | Nothing checks that `budget`'s keys equal the closed role list | `gk-core/data/tuning/structure-seed.v1.json:3-14` against `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41` |
| Real gap | The legion budget block | — |

**Correction to the map (§5.3).** The map has this module add the `exchange` budget row and publish
`structure-seed.v2`. That conflicts with this module's own acceptance, which says *"no role outside"* the
closed list, because `Exchange` joins the list only in `exchange-role`, which depends on this module. The
row therefore moves to `exchange-role`, and the role, its budget row and its legal pairs land together.

## 4. Principles as they bind this module

- **P2.** A metric's target is published data.
- **`validation-ssot.md` §3.** A corpus size is a reading. `len(DUMPED_ROWS) == 8` guards nothing: it
  fails when content changes, and its "fix" is editing the number.
- **Tuning is never hand-edited** (T4). Any new key publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`.
- **No model.** Zero calls.

## 5. Design

### 5.1 Tests read the band

- `test_grid_density_is_between_2_4_and_4_0` is renamed `test_grid_density_is_inside_the_published_band`.
  It reads `TUNING["metrics"]["densityBand"]` and asserts `minMilli <= round(1000 * rows / roles) <= maxMilli`.
  `rows` is `len(load_rows(root))` (the committed corpus, `structures-adapter`), and `roles` is
  `len(ROLE)`.
- `test_grid_density_lands_in_the_2_4_to_4_0_band` and the `plan` assertion at
  `gk-forge/tools/seedsmith/tests/test_structure_planner.py:58-60` read the same key.
- `metrics.py:217` declares its target as the **key path** `"tuning:metrics.densityBand"`. The
  `MetricResult` carries the resolved band. The `_declare` contract (a closed metric has a non-`None`
  target, `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:57-59`) still holds.

### 5.2 Pins become reconciliations

| Was | Becomes |
|---|---|
| `len(DUMPED_ROWS) == 8` | every `DUMPED_ROWS` id resolves to a row whose `name` equals the shipped C# name (the existing check at `:123`), and `len(DUMPED_ROWS) == len({r["id"] for r in DUMPED_ROWS})` |
| `len(AUTHORED_ROWS) == 17`, `len(ALL_ROWS) == 25` | `len(file_tree()) == len(ALL_ROWS)`; every `file_tree()` path exists on disk with identical bytes (the generator and the committed tree agree); the scale is printed, never asserted |

### 5.3 The budget validates against the closed list

`validate_budget(tuning, roles)` in `planner.py`. Every member of `ROLE` has an integer target ≥ 0. No key
names a role outside `ROLE`. `roleCountTolerance ≥ 0`. `densityBand.minMilli ≤ maxMilli`. `check_plan`
calls it first, and a failing budget raises `PlanCheckFailure` naming the key.

### 5.4 The legion budget shape (declared, not published)

For `legion-bands` to publish in `data/tuning/legion-seed.v1.json` (proposed; does not exist yet — map
§11 item 6):

```jsonc
"budget": {
  "legion-standard":  { "axes": ["elementAffinity", "worldTradeoffKind"], "perCellMin": <int>, "perCellMax": <int> },
  "legion-doctrine":  { "axes": ["elementAffinity", "worldTradeoffKind"], "perCellMin": <int>, "perCellMax": <int> },
  "legion-tradition": { "axes": ["triggerKind"],                          "perCellMin": <int>, "perCellMax": <int> },
  "legion-equipment": { "axes": ["slot", "tierBand"],                     "perCellMin": <int>, "perCellMax": <int> }
},
"metrics": { "densityBandMilli": { "min": <int>, "max": <int> } }
```

The values are chosen at publish time by the principle this repo already uses. Rosters hold at about 1–3
entries per cell (`docs/research/game-design/03-roster-scale.md`, "The three ways games hold ~1–3 per
cell"). Fire Emblem Heroes, at about 15 per cell with a maximum of 129, is the documented failure (same
file, its genre table). The seedsmith-design skill's figures (3.6 safe, 12.6 failure) are the same band
at a coarser grain. The axis
names must equal the closed vocabularies `legion-seed-contract` declares, and a validator of the same
shape as §5.3 enforces it.

## 6. Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q
```

No tuning publish is needed. The keys already exist.

## 7. Structure

```
gk-forge/tools/seedsmith/tests/test_structure_corpus.py     literals and pins removed (§5.1-5.2)
gk-forge/tools/seedsmith/tests/test_structure_planner.py    literal removed; validate_budget tests
gk-forge/tools/seedsmith/tests/test_structure_metrics.py    target-key test
gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py   target by key path
gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py   validate_budget
```

## 8. Acceptance (contract level)

1. A source scan of the three structure test files finds no `2.4`, `4.0`, `2400`, `4000`, and no
   `len(...) == <integer literal>` on a row collection. The scan is itself a test.
2. With a fixture tuning whose `densityBand` excludes the current density, the density test and
   `check_plan` both fail. With the published band, both pass. The verdict moves with data only.
3. A fixture budget with a role outside `ROLE`, or missing a role in `ROLE`, raises `PlanCheckFailure`
   naming it.
4. The generator and the committed tree agree byte for byte (§5.2).
5. No assertion names a population count or a generated string.

## 9. Test plan and verification boundary

Tests as in §5 and §8. All offline, with no transport import. **Verification boundary: a gap.**
`gk-forge/tools/seedsmith/**` is unmapped (`scripts/verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING`).
The owner of the fix is `test-verification-boundary` `python-test-lane`. The focused pytest command in
§6 is the boundary until then.

## 10. Hard edges

- **Criterion 4 fails today if the committed tree and the generator disagree.** They do for the three
  hand-authored rows, which `file_tree()` does not emit. The check is scoped to `file_tree()`'s own paths
  until `structure-bands` moves those rows into the generator (owner decision, 2026-09-19). After that it
  becomes a full-tree equality.

## 11. Dependencies

- Upstream: `structures-adapter` (`load_rows`).
- Downstream: `exchange-role` (publishes the `Exchange` budget row, which `validate_budget` then
  requires), `corpus-metrics`, `legion-bands` (publishes the §5.4 shape).

## 12. Open questions

None.

## 13. DESIGN-GATE §5 checklist

```
[x] Subsystems: seedsmith structure planner, metrics and tests; structure-seed tuning.
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares gk-forge/tools/seedsmith/** paths.
[x] Read this session: validation-ssot (all), tunables-ssot §2-§3, seedsmith-map P2/P3, DESIGN-GATE §3 rule 7.
[x] decisions.md: no lock on corpus budgets.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: the literal lines, the pin lines and the tuning keys were opened.
[x] Read the surrounding sections of P2 and validation-ssot §3.
[x] Tested: counted the corpus and ran check_plan over the disk rows (structures-adapter §5.5).
[x] No §2 invariant contradicted.
[x] Correction propagated: the Exchange budget row moved to exchange-role (§3), also noted in the map.
[x] No population pin. This module removes three.
[x] No event-refreshed cache.
[x] No ordering assumption.
[x] No actor magnitude.
[x] No SOLID-violating path; one tuning source for every target.
[ ] New rule registry row: none (the literal scan is a test inside the suite, not a repo-wide rule).
```

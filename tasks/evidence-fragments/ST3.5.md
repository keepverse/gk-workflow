# ST3.5 — the §11 row, and the model-free regenerate proven content-identical

**Acceptance erratum applied** (manager ruling 2026-09-19): "byte-identical" means identical CONTENT
modulo the provenance hash, and the regenerate chain is the real pipeline order including A-S7. Both
are recorded in the ST3.5 todo entry and in `spec-scope-window-tunables.md` (contract 6 and success
criterion 3).

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| §11 gains the `scopeWindows` row (A-U1 §3.4) | doc read + edit | **Written**, in §11.2 beside its two sibling action rows (`heldCap`/`rungCap`, `powerBudgetMilli`), same Cap/Value/Where/Question shape and the same "**No conflict — a soft, freely tunable content window, not a player-progression stop**" verdict. It names ruling 4, the `publish.py action-rungs scopeWindows.family.ceiling=6` retune path, what the ceiling bounds (structure via `Rung = rungBand[1]`; the holder's rung via ST2), and every refusal `load_scope_windows` enforces. | docs/architecture/power/ssot-power-scale.md |
| No new window literal in code | `python gk-core/scripts/audit-magic-numbers.py --summary` | **0 findings across every domain** (`M1 0 · M2 0 · M3 0 · M4 0`). | gk-forge/tools/seedsmith/**, gk-core/scripts/audit-magic-numbers.py |
| The model-free chain runs for real, in pipeline order | `characteristic_pool.regenerate(write=True)` → `type_weights.regenerate(write=True)` → `distribution_planner.regenerate(write=True, full_flag=True)` → `coverage_assignment.regenerate(plan_path=…, write=True)` → `innate_picker.regenerate(round_no=1, write=True)` → `coverage_report.regenerate(round_no=1, write=True)` | **All six ran.** planner: 6655 briefs written; A-S7: `assignedCount: 6655`, written; innate and coverage written. Order taken from `generate_action_pipeline.run_pipeline` (`generate_action_pipeline.py:87-153`) — where the acceptance's three-command form falls short; see the erratum. | — |
| **Every regenerated file is content-identical modulo the provenance hash** | scratch comparison (not committed): for each rewritten file, `json.load` of `git show HEAD:<path>` vs the working file, deep-walked | **Seven files rewritten, ZERO content differences.** With every `corpusHash` removed from both sides the difference count is **0 for all seven**. Kept, the moves are exactly: `_briefs/round-1.json` **6,656** (one `_meta.corpusHash` + one `_provenance.corpusHash` per brief, over 6,655 entries), `_reports/coverage-round-1.json` **1** (`_meta.corpusHash`). `_generated/characteristic-pool.json`, `_generated/family-map.json`, `_generated/role-lean.json`, `species-innate.json` and `type-weights.json` moved **no field at all** — rewritten bytes only. | scratch script |
| The dry-run form | `python -m …generate_distribution_planner --dry-run`; `…generate_coverage_report --round 1 --dry-run`; `…generate_innate_picker --round 1 --dry-run`; then `git diff --stat gk-data/packs/fusion/data/seed/actions/` | Coverage and innate picker ran clean, both reporting `"written": false`; the diff was empty. **The planner refuses**: `ValueError: mode: 'full' refused — missing a passing quality-gate report from A-S5` — `refuse_full_run_if_ungated` (`derive.py:747`) raises on `not full_flag` before the gate is even consulted, and the acceptance's command omits `--full`. | — |

## Why the hashes move, and why that is correct

`_corpus_hash` folds `rungs_doc["version"]` (`generate_distribution_planner.py:217-239`) — deliberately,
so a version bump cannot silently resume candidates planned against a different table. Pointing the
planner at v3 therefore moves `2e8910cf…` (v1, the committed value) to `99161625…` (v3), and the coverage
report's `d40f7728…` to `9c8ff5b7…`. That is H7's "point at v3 in the same commit" being taken
seriously: the corpus's provenance now names the file it was actually planned from. Everything else —
all 6,655 briefs, every candidate, the coverage entries, the innate picks — is unchanged.

## Why the first attempt looked like a content regression

The first real run was planner-only, and it differed in a real field:
`brief.family.academic.001`'s `requiredFamilies` (`['atom.chill-punisher']` committed, absent after it).
That field is not A-S1's: **A-S7 `coverage-assignment`** splices it, and A-S7's own test says so —
*"A-S7 is ADDITIVE: re-running it changes `requiredFamilies` (and nothing else) on every brief"*
(`test_generate_coverage_assignment.py:56`). Running A-S7 in its pipeline position puts it back, which is
what the chain above does, and the difference disappears. That run's artifacts were restored
byte-for-byte from HEAD and nothing from it was committed.

# Mega-merge QC 14 — seedsmith corpora on the merged head

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
pytest + CLI gates. No live game.

## Verdict: GREEN with two pre-existing reds (both routed, neither new)

| Check | Command | Result |
|---|---|---|
| Items adapter | `pytest gk-forge/tools/seedsmith/tests/test_items_adapter.py` | 18/18 |
| Bulk suite | `pytest gk-forge/tools/seedsmith/tests/` (minus completeness file) | 1142 passed, 2 skipped, **1 failed** → routed, see F1 |
| Completeness file | `pytest test_actions_description_completeness.py` | 5 failed / 7 passed — matches the documented pre-existing failure on clean HEAD |

**Cycle 5 close (2026-09-24):** both routed reds are now fixed — F1 (AC-F1 loader amendment) and F2
(description backfill). Completeness file 12 passed; actions suites 71 passed.

## Routed findings (pre-existing, owned elsewhere)

- **F1 — `test_actions_check_uses_domain_loader_and_excludes_round_scratch`:** `act.attack`'s
  `atomFamilies` names unknown `atom.fx-overlay-damage`. Already routed as **AC-F1**
  (measured in SGC T55); unchanged by any merge under QC.
  **FIXED in QC fix cycle 4 (2026-09-24), checked to QC 1 F2 + QC 14 F1:** root cause was loader
  drift, not seed drift — `atom.fx-overlay-damage` is a live atom-registry family
  (`gk-data/packs/fusion/data/seed/atoms/fx-core.json`) that the 2026-09-03 namespace rule predated. **Refined in fix
  cycle 11:** the first form widened `load_family_ids()` itself, which is ALSO the generator pool
  (`distribution_planner`/`dedup_select`), and broke their "fx id must be refused" invariants. The
  fix now SPLITS the two vocabularies: `load_family_ids()` stays the 98 affix families (generator
  pool), and a new `load_accepted_family_ids()` (affix ∪ 16 fx) is what the corpus loader and the
  adapter registry use. Both red rows green + `guard-vocabulary-mirror.py` OK. No seed JSON
  hand-edited.
- **F2 — completeness file reds:** documented pre-existing on clean HEAD per the seedsmith
  runbook; unchanged by any merge under QC. **Cycle 4 update:** the AC-F1 fix removed one of the
  five (shared cause — the completeness suite's `test_load_committed_reports_zero_loader_findings`
  and `test_resumed_plan_is_empty…` name the same unknown-family). Live baseline now **4 failed /
  8 passed**, all four tracing to `action.family.academic.004` (a generated row) lacking an inline
  `description` — the SGC5-F4 cause, to be repaired via the sanctioned backfill in the next cycle.
  **FIXED in QC fix cycle 5 (2026-09-24), checked to QC 14 F2:** ran the sanctioned resumable
  backfill (`python -m seedsmith.adapters.actions.generate_action_descriptions --only
  action.family.academic.004`) against the local LM Studio model (`google/gemma-4-26b-a4b-qat`);
  it stamped `description` + `_provenance` into `committed-round-1.json` and a `RunLedger` entry,
  **no hand-edit of generated content**. One stale assertion in the suite itself
  (`test_the_backfill_plan_never_targets_authored_content` pinned the SGC5-F4 gap open by id — it
  demanded the bug return once fixed) was replaced with the structural form its own docstring
  required. Proof: completeness file **12 passed** (was 4 failed / 8 passed) + `test_actions_adapter`
  / `test_cli` / `test_corpus_loader` 71 passed.
- **QC 14 close:** seedsmith corpora now have **zero open reds** under this QC (F1 + F2 both fixed).
